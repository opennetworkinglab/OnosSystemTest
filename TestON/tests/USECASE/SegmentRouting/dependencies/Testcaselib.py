import os
import imp
import time
import json
import urllib
from core import utilities


class Testcaselib:

    useSSH=False

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
        main.dependencyPath = main.path + "/../dependencies/"
        main.topology = main.params[ 'DEPENDENCY' ][ 'topology' ]
        wrapperFile1 = main.params[ 'DEPENDENCY' ][ 'wrapper1' ]
        main.scale = (main.params[ 'SCALE' ][ 'size' ]).split( "," )
        main.maxNodes = int( main.params[ 'SCALE' ][ 'max' ] )
        # main.ONOSport = main.params[ 'CTRL' ][ 'port' ]
        main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
        main.cellData = { }  # for creating cell file
        main.CLIs = [ ]
        main.ONOSip = [ ]
        main.RESTs = [ ]

        # Assigning ONOS cli handles to a list
        for i in range( 1, main.maxNodes + 1 ):
            main.CLIs.append( getattr( main, 'ONOScli' + str( i ) ) )
            main.RESTs.append( getattr( main, 'ONOSrest' + str( i ) ) )
            main.ONOSip.append( main.CLIs[ i - 1 ].ip_address )
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
    def installOnos( main, vlanCfg=True ):
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
        apps = main.apps
        if main.diff:
            apps = main.apps + "," + main.diff
        else:
            main.log.error( "App list is empty" )
        print "NODE COUNT = ", main.numCtrls
        print main.ONOSip
        tempOnosIp = [ ]
        main.dynamicHosts = [ 'in1', 'out1' ]
        for i in range( main.numCtrls ):
            tempOnosIp.append( main.ONOSip[ i ] )
        onosUser = main.params[ 'ENV' ][ 'cellUser' ]
        main.step( "Create and Apply cell file" )
        main.ONOSbench.createCellFile( main.ONOSbench.ip_address,
                                       "temp",
                                       main.Mininet1.ip_address,
                                       apps,
                                       tempOnosIp,
                                       onosUser,
                                       useSSH=Testcaselib.useSSH )
        cellResult = main.ONOSbench.setCell( "temp" )
        verifyResult = main.ONOSbench.verifyCell( )
        stepResult = cellResult and verifyResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully applied cell to " + \
                                        "environment",
                                 onfail="Failed to apply cell to environment " )
        # kill off all onos processes
        main.log.info( "Safety check, killing all ONOS processes" +
                       " before initiating environment setup" )
        for i in range( main.maxNodes ):
            main.ONOSbench.onosDie( main.ONOSip[ i ] )
        main.step( "Create and Install ONOS package" )
        packageResult = main.ONOSbench.buckBuild()

        onosInstallResult = main.TRUE
        for i in range( main.numCtrls ):
            onosInstallResult = onosInstallResult and \
                                main.ONOSbench.onosInstall(
                                        node=main.ONOSip[ i ] )
        stepResult = onosInstallResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully installed ONOS package",
                                 onfail="Failed to install ONOS package" )
        if Testcaselib.useSSH:
            for i in range( main.numCtrls ):
                onosInstallResult = onosInstallResult and \
                                    main.ONOSbench.onosSecureSSH(
                                            node=main.ONOSip[ i ] )
            stepResult = onosInstallResult
            utilities.assert_equals( expect=main.TRUE,
                                     actual=stepResult,
                                     onpass="Successfully secure SSH",
                                     onfail="Failed to secure SSH" )
        main.step( "Starting ONOS service" )
        stopResult, startResult, onosIsUp = main.TRUE, main.TRUE, main.TRUE,
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
            main.CLIs[ i ].startCellCli( )
            cliResult = main.CLIs[ i ].startOnosCli( main.ONOSip[ i ],
                                                     commandlineTimeout=60,
                                                     onosStartTimeout=100 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=cliResult,
                                 onpass="ONOS CLI is ready",
                                 onfail="ONOS CLI is not ready" )
        main.active = 0
        for i in range( 10 ):
            ready = True
            output = main.CLIs[ main.active ].summary( )
            if not output:
                ready = False
            if ready:
                break
            time.sleep( 10 )
        utilities.assert_equals( expect=True, actual=ready,
                                 onpass="ONOS summary command succeded",
                                 onfail="ONOS summary command failed" )

        with open( "%s/json/%s.json" % (
                main.dependencyPath, main.cfgName) ) as cfg:
            main.RESTs[ main.active ].setNetCfg( json.load( cfg ) )
        with open( "%s/json/%s.chart" % (
                main.dependencyPath, main.cfgName) ) as chart:
            main.pingChart = json.load( chart )
        if not ready:
            main.log.error( "ONOS startup failed!" )
            main.cleanup( )
            main.exit( )

        for i in range( main.numCtrls ):
            main.CLIs[ i ].logSet( "DEBUG", "org.onosproject.segmentrouting" )
            main.CLIs[ i ].logSet( "DEBUG", "org.onosproject.driver.pipeline" )
            main.CLIs[ i ].logSet( "DEBUG", "org.onosproject.store.group.impl" )
            main.CLIs[ i ].logSet( "DEBUG",
                                   "org.onosproject.net.flowobjective.impl" )

    @staticmethod
    def startMininet( main, topology, args="" ):
        main.step( "Starting Mininet Topology" )
        arg = "--onos %d %s" % (main.numCtrls, args)
        main.topology = topology
        topoResult = main.Mininet1.startNet(
                topoFile=main.Mininet1.home + main.topology, args=arg )
        stepResult = topoResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanup( )
            main.exit( )

    @staticmethod
    def checkFlows( main, minFlowCount, dumpflows=True ):
        main.step(
                " Check whether the flow count is bigger than %s" % minFlowCount )
        count = utilities.retry( main.CLIs[ main.active ].checkFlowCount,
                                 main.FALSE,
                                 kwargs={ 'min': minFlowCount },
                                 attempts=10,
                                 sleep=10 )
        utilities.assertEquals( \
                expect=True,
                actual=(count > 0),
                onpass="Flow count looks correct: " + str( count ),
                onfail="Flow count looks wrong: " + str( count ) )

        main.step( "Check whether all flow status are ADDED" )
        flowCheck = utilities.retry( main.CLIs[ main.active ].checkFlowsState,
                                     main.FALSE,
                                     kwargs={ 'isPENDING': False },
                                     attempts=2,
                                     sleep=10 )
        utilities.assertEquals( \
                expect=main.TRUE,
                actual=flowCheck,
                onpass="Flow status is correct!",
                onfail="Flow status is wrong!" )
        if dumpflows:
            main.ONOSbench.dumpONOSCmd( main.ONOSip[ main.active ],
                                        "flows",
                                        main.logdir,
                                        "flowsBefore" + main.cfgName )
            main.ONOSbench.dumpONOSCmd( main.ONOSip[ main.active ],
                                        "groups",
                                        main.logdir,
                                        "groupsBefore" + main.cfgName )

    @staticmethod
    def pingAll( main, tag="", dumpflows=True ):
        main.log.report( "Check full connectivity" )
        print main.pingChart
        for entry in main.pingChart.itervalues( ):
            print entry
            hosts, expect = entry[ 'hosts' ], entry[ 'expect' ]
            expect = main.TRUE if expect else main.FALSE
            main.step( "Connectivity for %s %s" % (str( hosts ), tag) )
            pa = main.Mininet1.pingallHosts( hosts )
            utilities.assert_equals( expect=expect, actual=pa,
                                     onpass="IP connectivity successfully tested",
                                     onfail="IP connectivity failed" )
        if dumpflows:
            main.ONOSbench.dumpONOSCmd( main.ONOSip[ main.active ],
                                        "flows",
                                        main.logdir,
                                        "flowsOn" + tag )
            main.ONOSbench.dumpONOSCmd( main.ONOSip[ main.active ],
                                        "groups",
                                        main.logdir,
                                        "groupsOn" + tag )

    @staticmethod
    def killLink( main, end1, end2, switches, links ):
        """
        end1,end2: identify the switches, ex.: 'leaf1', 'spine1'
        switches, links: number of expected switches and links after linkDown, ex.: '4', '6'
        Kill a link and verify ONOS can see the proper link change
        """
        main.linkSleep = float( main.params[ 'timers' ][ 'LinkDiscovery' ] )
        main.step( "Kill link between %s and %s" % (end1, end2) )
        LinkDown = main.Mininet1.link( END1=end1, END2=end2, OPTION="down" )
        LinkDown = main.Mininet1.link( END2=end1, END1=end2, OPTION="down" )
        main.log.info(
                "Waiting %s seconds for link down to be discovered" % main.linkSleep )
        time.sleep( main.linkSleep )
        topology = utilities.retry( main.CLIs[ main.active ].checkStatus,
                                    main.FALSE,
                                    kwargs={ 'numoswitch': switches,
                                             'numolink': links },
                                    attempts=10,
                                    sleep=main.linkSleep )
        result = topology & LinkDown
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                 onpass="Link down successful",
                                 onfail="Failed to turn off link?" )

    @staticmethod
    def restoreLink( main, end1, end2, dpid1, dpid2, port1, port2, switches,
                     links ):
        """
        Params:
            end1,end2: identify the end switches, ex.: 'leaf1', 'spine1'
            dpid1, dpid2: dpid of the end switches respectively, ex.: 'of:0000000000000002'
            port1, port2: respective port of the end switches that connects to the link, ex.:'1'
            switches, links: number of expected switches and links after linkDown, ex.: '4', '6'
        Kill a link and verify ONOS can see the proper link change
        """
        main.step( "Restore link between %s and %s" % (end1, end2) )
        result = False
        count = 0
        while True:
            count += 1
            main.Mininet1.link( END1=end1, END2=end2, OPTION="up" )
            main.Mininet1.link( END2=end1, END1=end2, OPTION="up" )
            main.log.info(
                    "Waiting %s seconds for link up to be discovered" % main.linkSleep )
            time.sleep( main.linkSleep )

            for i in range(0, main.numCtrls):
                onosIsUp = main.ONOSbench.isup( main.ONOSip[ i ] )
                if onosIsUp == main.TRUE:
                    main.CLIs[ i ].portstate( dpid=dpid1, port=port1 )
                    main.CLIs[ i ].portstate( dpid=dpid2, port=port2 )
            time.sleep( main.linkSleep )

            result = main.CLIs[ main.active ].checkStatus( numoswitch=switches,
                                                           numolink=links )
            if count > 5 or result:
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
        # todo make this repeatable
        main.log.info( "Waiting %s seconds for switch down to be discovered" % (
            main.switchSleep) )
        time.sleep( main.switchSleep )
        topology = utilities.retry( main.CLIs[ main.active ].checkStatus,
                                    main.FALSE,
                                    kwargs={ 'numoswitch': switches,
                                             'numolink': links },
                                    attempts=10,
                                    sleep=main.switchSleep )
        utilities.assert_equals( expect=main.TRUE, actual=topology,
                                 onpass="Kill switch successful",
                                 onfail="Failed to kill switch?" )

    @staticmethod
    def recoverSwitch( main, switch, switches, links ):
        """
        Params: switches, links: number of expected switches and links after SwitchUp, ex.: '4', '6'
        Recover a switch and verify ONOS can see the proper change
        """
        # todo make this repeatable
        main.step( "Recovering " + switch )
        main.log.info( "Starting" + switch )
        main.Mininet1.switch( SW=switch, OPTION="start" )
        main.log.info( "Waiting %s seconds for switch up to be discovered" % (
            main.switchSleep) )
        time.sleep( main.switchSleep )
        topology = utilities.retry( main.CLIs[ main.active ].checkStatus,
                                    main.FALSE,
                                    kwargs={ 'numoswitch': switches,
                                             'numolink': links },
                                    attempts=10,
                                    sleep=main.switchSleep )
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
        main.Mininet1.stopNet( )
        main.ONOSbench.scp( main.ONOScli1, "/opt/onos/log/karaf.log",
                            "/tmp/karaf.log", direction="from" )
        main.ONOSbench.cpLogsToDir( "/tmp/karaf.log", main.logdir,
                                    copyFileName="karaf.log." + main.cfgName )
        for i in range( main.numCtrls ):
            main.ONOSbench.onosStop( main.ONOSip[ i ] )

    @staticmethod
    def killOnos( main, nodes, switches, links, expNodes ):
        """
        Params: nodes, integer array with position of the ONOS nodes in the CLIs array
        switches, links, nodes: number of expected switches, links and nodes after KillOnos, ex.: '4', '6'
        Completely Kill an ONOS instance and verify the ONOS cluster can see the proper change
        """
        main.step( "Killing ONOS instance" )
        for i in nodes:
            killResult = main.ONOSbench.onosDie( main.CLIs[ i ].ip_address )
            utilities.assert_equals( expect=main.TRUE, actual=killResult,
                                     onpass="ONOS instance Killed",
                                     onfail="Error killing ONOS instance" )
            if i == main.active:
                main.active = (i + 1) % main.numCtrls
        time.sleep( 12 )
        if len( nodes ) < main.numCtrls:
            topology = utilities.retry( main.CLIs[ main.active ].checkStatus,
                                        main.FALSE,
                                        kwargs={ 'numoswitch': switches,
                                                 'numolink': links,
                                                 'numoctrl': expNodes },
                                        attempts=10,
                                        sleep=12 )
            utilities.assert_equals( expect=main.TRUE, actual=topology,
                                     onpass="ONOS Instance down successful",
                                     onfail="Failed to turn off ONOS Instance" )
        else:
            main.active = -1

    @staticmethod
    def recoverOnos( main, nodes, switches, links, expNodes ):
        """
        Params: nodes, integer array with position of the ONOS nodes in the CLIs array
        switches, links, nodes: number of expected switches, links and nodes after recoverOnos, ex.: '4', '6'
        Recover an ONOS instance and verify the ONOS cluster can see the proper change
        """
        main.step( "Recovering ONOS instance" )
        [ main.ONOSbench.onosStart( main.CLIs[ i ].ip_address ) for i in nodes ]
        for i in nodes:
            isUp = main.ONOSbench.isup( main.ONOSip[ i ] )
            utilities.assert_equals( expect=main.TRUE, actual=isUp,
                                     onpass="ONOS service is ready",
                                     onfail="ONOS service did not start properly" )
        for i in nodes:
            main.step( "Checking if ONOS CLI is ready" )
            main.CLIs[ i ].startCellCli( )
            cliResult = main.CLIs[ i ].startOnosCli( main.ONOSip[ i ],
                                                     commandlineTimeout=60,
                                                     onosStartTimeout=100 )
            utilities.assert_equals( expect=main.TRUE,
                                     actual=cliResult,
                                     onpass="ONOS CLI is ready",
                                     onfail="ONOS CLI is not ready" )
            main.active = i if main.active == -1 else main.active

        topology = utilities.retry( main.CLIs[ main.active ].checkStatus,
                                    main.FALSE,
                                    kwargs={ 'numoswitch': switches,
                                             'numolink': links,
                                             'numoctrl': expNodes },
                                    attempts=10,
                                    sleep=12 )
        utilities.assert_equals( expect=main.TRUE, actual=topology,
                                 onpass="ONOS Instance down successful",
                                 onfail="Failed to turn off ONOS Instance" )
        for i in range( 10 ):
            ready = True
            output = main.CLIs[ main.active ].summary( )
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
            main.cleanup( )
            main.exit( )

    @staticmethod
    def addHostCfg( main ):
        """
        Adds Host Configuration to ONOS
        Updates expected state of the network (pingChart)
        """
        import json
        hostCfg = { }
        with open( main.dependencyPath + "/json/extra.json" ) as template:
            hostCfg = json.load( template )
        main.pingChart[ 'ip' ][ 'hosts' ] += [ 'in1' ]
        main.step( "Pushing new configuration" )
        mac, cfg = hostCfg[ 'hosts' ].popitem( )
        main.RESTs[ main.active ].setNetCfg( cfg[ 'basic' ],
                                             subjectClass="hosts",
                                             subjectKey=urllib.quote( mac,
                                                                      safe='' ),
                                             configKey="basic" )
        main.pingChart[ 'ip' ][ 'hosts' ] += [ 'out1' ]
        main.step( "Pushing new configuration" )
        mac, cfg = hostCfg[ 'hosts' ].popitem( )
        main.RESTs[ main.active ].setNetCfg( cfg[ 'basic' ],
                                             subjectClass="hosts",
                                             subjectKey=urllib.quote( mac,
                                                                      safe='' ),
                                             configKey="basic" )
        main.pingChart.update( { 'vlan1': { "expect": "True",
                                            "hosts": [ "olt1", "vsg1" ] } } )
        main.pingChart[ 'vlan5' ][ 'expect' ] = 0
        main.pingChart[ 'vlan10' ][ 'expect' ] = 0
        ports = "[%s,%s]" % (5, 6)
        cfg = '{"of:0000000000000001":[{"vlan":1,"ports":%s,"name":"OLT 1"}]}' % ports
        main.RESTs[ main.active ].setNetCfg( json.loads( cfg ),
                                             subjectClass="apps",
                                             subjectKey="org.onosproject.segmentrouting",
                                             configKey="xconnect" )

    @staticmethod
    def delHostCfg( main ):
        """
        Removest Host Configuration from ONOS
        Updates expected state of the network (pingChart)
        """
        import json
        hostCfg = { }
        with open( main.dependencyPath + "/json/extra.json" ) as template:
            hostCfg = json.load( template )
        main.step( "Removing host configuration" )
        main.pingChart[ 'ip' ][ 'expect' ] = 0
        mac, cfg = hostCfg[ 'hosts' ].popitem( )
        main.RESTs[ main.active ].removeNetCfg( subjectClass="hosts",
                                                subjectKey=urllib.quote(
                                                        mac,
                                                        safe='' ),
                                                configKey="basic" )
        main.step( "Removing configuration" )
        main.pingChart[ 'ip' ][ 'expect' ] = 0
        mac, cfg = hostCfg[ 'hosts' ].popitem( )
        main.RESTs[ main.active ].removeNetCfg( subjectClass="hosts",
                                                subjectKey=urllib.quote(
                                                        mac,
                                                        safe='' ),
                                                configKey="basic" )
        main.step( "Removing vlan configuration" )
        main.pingChart[ 'vlan1' ][ 'expect' ] = 0
        main.RESTs[ main.active ].removeNetCfg( subjectClass="apps",
                                                subjectKey="org.onosproject.segmentrouting",
                                                configKey="xconnect" )
