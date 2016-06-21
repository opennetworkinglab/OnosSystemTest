import os
import imp
import time

from core import utilities


class Testcaselib:
    @staticmethod
    def initTest( main ):
        """
        - Construct tests variables
        - GIT ( optional )
            - Checkout ONOS master branch
            - Pull latest ONOS code
        - Building ONOS ( optional )
            - Install ONOS package
            - Build ONOS package
        """
        main.step( "Constructing test variables" )
        # Test variables
        main.cellName = main.params[ 'ENV' ][ 'cellName' ]
        main.apps = main.params[ 'ENV' ][ 'cellApps' ]
        main.diff = main.params[ 'ENV' ][ 'diffApps' ]
        gitBranch = main.params[ 'GIT' ][ 'branch' ]
        main.path = os.path.dirname( main.testFile )
        main.dependencyPath = main.path +"/../dependencies/"
        main.topology = main.params[ 'DEPENDENCY' ][ 'topology' ]
        wrapperFile1 = main.params[ 'DEPENDENCY' ][ 'wrapper1' ]
        main.scale = ( main.params[ 'SCALE' ][ 'size' ] ).split( "," )
        main.maxNodes = int( main.params[ 'SCALE' ][ 'max' ] )
        #main.ONOSport = main.params[ 'CTRL' ][ 'port' ]
        main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
        main.cellData = {} # for creating cell file
        main.CLIs = []
        main.ONOSip = []

        # Assigning ONOS cli handles to a list
        for i in range( 1,  main.maxNodes + 1 ):
            main.CLIs.append( getattr( main, 'ONOScli' + str( i ) ) )
            main.ONOSip.append( main.CLIs[i-1].ip_address )
        # -- INIT SECTION, ONLY RUNS ONCE -- #
        main.startUp = imp.load_source( wrapperFile1,
                                        main.dependencyPath +
                                        wrapperFile1 +
                                        ".py" )

        copyResult1 = main.ONOSbench.scp( main.Mininet1,
                                          main.dependencyPath +
                                          main.topology,
                                          main.Mininet1.home,
                                          direction="to" )
        if main.CLIs:
            stepResult = main.TRUE
        else:
            main.log.error( "Did not properly created list of ONOS CLI handle" )
            stepResult = main.FALSE

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully construct " +
                                        "test variables ",
                                 onfail="Failed to construct test variables" )

    @staticmethod
    def installOnos( main ):
        """
        - Set up cell
            - Create cell file
            - Set cell file
            - Verify cell file
        - Kill ONOS process
        - Uninstall ONOS cluster
        - Verify ONOS start up
        - Install ONOS cluster
        - Connect to cli
        """
        # main.scale[ 0 ] determines the current number of ONOS controller
        apps=main.apps
        if main.diff:
            apps = main.apps + "," + main.diff
        else: main.log.error( "App list is empty" )
        main.case( "Package and start ONOS using apps:" + apps)
        print "NODE COUNT = ", main.numCtrls
        print main.ONOSip
        tempOnosIp = []
        for i in range( main.numCtrls ):
            tempOnosIp.append( main.ONOSip[i] )
        onosUser = main.params[ 'ENV' ][ 'cellUser' ]
        main.step("Create and Apply cell file")
        main.ONOSbench.createCellFile( main.ONOSbench.ip_address,
                                       "temp",
                                       main.Mininet1.ip_address,
                                       apps,
                                       tempOnosIp,
                                       onosUser )
        cellResult = main.ONOSbench.setCell( "temp" )
        verifyResult = main.ONOSbench.verifyCell()
        stepResult = cellResult and verifyResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully applied cell to " + \
                                        "environment",
                                 onfail="Failed to apply cell to environment " )
        #kill off all onos processes
        main.log.info( "Safety check, killing all ONOS processes" +
                       " before initiating environment setup" )
        for i in range( main.maxNodes ):
            main.ONOSbench.onosDie( main.ONOSip[ i ] )
        main.step( "Create and Install ONOS package" )
        main.ONOSbench.handle.sendline( "cp "+main.dependencyPath+"/"+main.cfgName+".json ~/onos/tools/package/config/network-cfg.json")
        packageResult = main.ONOSbench.onosPackage()

        onosInstallResult = main.TRUE
        for i in range( main.numCtrls ):
            onosInstallResult = onosInstallResult and \
                                main.ONOSbench.onosInstall( node=main.ONOSip[ i ] )
        stepResult = onosInstallResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully installed ONOS package",
                                 onfail="Failed to install ONOS package" )
        main.step( "Starting ONOS service" )
        stopResult,startResult, onosIsUp= main.TRUE, main.TRUE, main.TRUE,
        for i in range( main.numCtrls ):
            onosIsUp = onosIsUp and main.ONOSbench.isup( main.ONOSip[ i ] )
        if onosIsUp == main.TRUE:
            main.log.report( "ONOS instance is up and ready" )
        else:
            main.log.report( "ONOS instance may not be up, stop and " +
                             "start ONOS again " )
            for i in range( main.numCtrls ):
                stopResult = stopResult and \
                             main.ONOSbench.onosStop( main.ONOSip[ i ] )
            for i in range( main.numCtrls ):
                startResult = startResult and \
                              main.ONOSbench.onosStart( main.ONOSip[ i ] )
        stepResult = onosIsUp and stopResult and startResult

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ONOS service is ready",
                                 onfail="ONOS service did not start properly" )
        main.step( "Checking if ONOS CLI is ready" )
        for i in range( main.numCtrls ):
            main.CLIs[i].startCellCli()
            cliResult = main.CLIs[i].startOnosCli( main.ONOSip[ i ],
                                               commandlineTimeout=60, onosStartTimeout=100 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=cliResult,
                                 onpass="ONOS CLI is ready",
                                 onfail="ONOS CLI is not ready" )
        main.active=0
        for i in range( 10 ):
            ready = True
            output = main.CLIs[main.active].summary()
            if not output:
                ready = False
            if ready:
                break
            time.sleep( 10 )
        utilities.assert_equals( expect=True, actual=ready,
                                 onpass="ONOS summary command succeded",
                                 onfail="ONOS summary command failed" )

        if not ready:
            main.log.error( "ONOS startup failed!" )
            main.cleanup()
            main.exit()

        for i in range( main.numCtrls ):
            main.CLIs[i].logSet( "DEBUG", "org.onosproject.segmentrouting" )
            main.CLIs[i].logSet( "DEBUG", "org.onosproject.driver.pipeline" )
            main.CLIs[i].logSet( "DEBUG", "org.onosproject.store.group.impl" )
            main.CLIs[i].logSet( "DEBUG", "org.onosproject.net.flowobjective.impl" )

    @staticmethod
    def startMininet( main, topology, args="" ):
        main.step( "Starting Mininet Topology" )
        arg = "--onos %d %s" % (main.numCtrls, args)
        main.topology=topology
        topoResult = main.Mininet1.startNet( topoFile= main.dependencyPath + main.topology, args=arg )
        stepResult = topoResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanup()
            main.exit()

    @staticmethod
    def checkFlows(main, minFlowCount):
        main.step(" Check whether the flow count is bigger than %s" % minFlowCount)
        count =  utilities.retry(main.CLIs[main.active].checkFlowCount,
                                 main.FALSE,
                                 kwargs={'min':minFlowCount},
                                 attempts=10,
                                 sleep=10)
        utilities.assertEquals( \
                expect=True,
                actual=(count>0),
                onpass="Flow count looks correct: "+str(count),
                onfail="Flow count looks wrong: "+str(count) )

        main.step( "Check whether all flow status are ADDED" )
        flowCheck = utilities.retry( main.CLIs[main.active].checkFlowsState,
                                     main.FALSE,
                                     kwargs={'isPENDING':False},
                                     attempts=10,
                                     sleep=10)
        utilities.assertEquals( \
                expect=main.TRUE,
                actual=flowCheck,
                onpass="Flow status is correct!",
                onfail="Flow status is wrong!" )
        main.ONOSbench.dumpFlows( main.ONOSip[main.active],
                                  main.logdir, "flowsBefore" + main.cfgName)
        main.ONOSbench.dumpGroups( main.ONOSip[0],
                                   main.logdir, "groupsBefore" + main.cfgName)

    @staticmethod
    def pingAll( main, tag=""):
        main.log.report( "Check full connectivity" )
        main.step("Check full connectivity %s" %tag)
        pa = main.Mininet1.pingall()
        utilities.assert_equals( expect=main.TRUE, actual=pa,
                                 onpass="Full connectivity successfully tested",
                                 onfail="Full connectivity failed" )
        main.ONOSbench.dumpFlows( main.ONOSip[main.active],
                                  main.logdir, "flowsOn" + tag)
        main.ONOSbench.dumpGroups( main.ONOSip[main.active],
                                   main.logdir, "groupsOn" + tag)

    @staticmethod
    def killLink( main, end1, end2, switches, links ):
        """
        end1,end2: identify the switches, ex.: 'leaf1', 'spine1'
        switches, links: number of expected switches and links after linkDown, ex.: '4', '6'
        Kill a link and verify ONOS can see the proper link change
        """
        main.linkSleep = float( main.params[ 'timers' ][ 'LinkDiscovery' ] )
        main.step( "Kill link between %s and %s" %(end1, end2))
        LinkDown = main.Mininet1.link( END1=end1, END2=end2, OPTION="down" )
        main.log.info( "Waiting %s seconds for link down to be discovered" % main.linkSleep )
        time.sleep( main.linkSleep )
        topology =  utilities.retry( main.CLIs[main.active].checkStatus,
                                     main.FALSE,
                                     kwargs={'numoswitch':switches, 'numolink':links},
                                     attempts=10,
                                     sleep=main.linkSleep)
        result = topology & LinkDown
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                 onpass="Link down successful",
                                 onfail="Failed to turn off link?" )

    @staticmethod
    def restoreLink( main, end1, end2, dpid1, dpid2, port1, port2, switches, links ):
        """
        Params:
            end1,end2: identify the end switches, ex.: 'leaf1', 'spine1'
            dpid1, dpid2: dpid of the end switches respectively, ex.: 'of:0000000000000002'
            port1, port2: respective port of the end switches that connects to the link, ex.:'1'
            switches, links: number of expected switches and links after linkDown, ex.: '4', '6'
        Kill a link and verify ONOS can see the proper link change
        """
        main.step( "Restore link between %s and %s" %( end1, end2 ) )
        result = False
        count=0
        while True:
            count+=0
            main.Mininet1.link( END1=end1, END2=end2, OPTION="up" )
            main.Mininet1.link( END2=end1, END1=end2, OPTION="up" )
            main.log.info( "Waiting %s seconds for link up to be discovered" % main.linkSleep )
            time.sleep( main.linkSleep )
            main.CLIs[main.active].portstate( dpid=dpid1, port=port1 )
            main.CLIs[main.active].portstate( dpid=dpid2, port=port2 )
            time.sleep( main.linkSleep )

            result = main.CLIs[main.active].checkStatus( numoswitch=switches, numolink=links )
            if count>5 or result:
                break
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                 onpass="Link up successful",
                                 onfail="Failed to bring link up" )

    @staticmethod
    def killSwitch( main, switch, switches, links ):
        """
        Params: switches, links: number of expected switches and links after SwitchDown, ex.: '4', '6'
        Completely kill a switch and verify ONOS can see the proper change
        """
        main.switchSleep = float( main.params[ 'timers' ][ 'SwitchDiscovery' ] )
        main.step( "Kill " + switch )
        main.log.info( "Stopping" + switch )
        main.Mininet1.switch( SW=switch, OPTION="stop" )
        main.log.info( "Waiting %s seconds for switch down to be discovered" % ( main.switchSleep ) )
        time.sleep( main.switchSleep )
        topology =  utilities.retry( main.CLIs[main.active].checkStatus,
                                     main.FALSE,
                                     kwargs={'numoswitch':switches, 'numolink':links},
                                     attempts=10,
                                     sleep=main.switchSleep)
        utilities.assert_equals( expect=main.TRUE, actual=topology,
                                 onpass="Kill switch successful",
                                 onfail="Failed to kill switch?" )

    @staticmethod
    def recoverSwitch( main, switch, switches, links ):
        """
        Params: switches, links: number of expected switches and links after SwitchUp, ex.: '4', '6'
        Recover a switch and verify ONOS can see the proper change
        """
        main.step( "Recovering " + switch )
        main.log.info( "Starting" + switch )
        main.Mininet1.switch( SW=switch, OPTION="start")
        main.log.info( "Waiting %s seconds for switch up to be discovered" %(main.switchSleep))
        time.sleep( main.switchSleep )
        topology =  utilities.retry( main.CLIs[main.active].checkStatus,
                                     main.FALSE,
                                     kwargs={'numoswitch':switches, 'numolink':links},
                                     attempts=10,
                                     sleep=main.switchSleep)
        utilities.assert_equals( expect=main.TRUE, actual=topology,
                                 onpass="Switch recovery successful",
                                 onfail="Failed to recover switch?" )

    @staticmethod
    def cleanup( main ):
        """
        Stop Onos-cluster.
        Stops Mininet
        Copies ONOS log
        """
        main.Mininet1.stopNet()
        main.ONOSbench.scp( main.ONOScli1 ,"/opt/onos/log/karaf.log",
                           "/tmp/karaf.log", direction="from" )
        main.ONOSbench.cpLogsToDir("/tmp/karaf.log",main.logdir,
                                   copyFileName="karaf.log."+main.cfgName)
        for i in range(main.numCtrls):
            main.ONOSbench.onosStop( main.ONOSip[i] )
