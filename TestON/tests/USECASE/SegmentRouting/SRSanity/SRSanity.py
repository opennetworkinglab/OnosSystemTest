# This test should always succeed. it runs cases 1,2,3,4
#CASE1: Get and Build ONOS
#CASE2: Package and Install ONOS
#CASE3: Start Mininet and check flows
#CASE4: Ping all
#CASE5: Link Failure
#CASE6: Switch Failure
#CASE7: ONOS Failure
#CASE8: CLUSTER Failure
#CASE10: Logging

class SRSanity:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        import time
        import os
        import imp
        import re

        """
        - Construct tests variables
        - GIT ( optional )
            - Checkout ONOS master branch
            - Pull latest ONOS code
        - Building ONOS ( optional )
            - Install ONOS package
            - Build ONOS package
        """

        main.case( "Constructing test variables and building ONOS" )
        main.step( "Constructing test variables" )
        stepResult = main.FALSE

        # Test variables
        main.cellName = main.params[ 'ENV' ][ 'cellName' ]
        main.apps = main.params[ 'ENV' ][ 'cellApps' ]
        main.diff = []
        main.diff.extend(( main.params[ 'ENV' ][ 'diffApps' ] ).split(";"))
        main.diff=main.diff*2
        gitBranch = main.params[ 'GIT' ][ 'branch' ]
        main.path = os.path.dirname( main.testFile )
        main.dependencyPath = main.path +"/../dependencies/"
        main.topology = main.params[ 'DEPENDENCY' ][ 'topology' ]
        main.json = ["2x2"]*4
        main.args = [" "]*4
        main.scale = ( main.params[ 'SCALE' ][ 'size' ] ).split( "," )
        main.maxNodes = int( main.params[ 'SCALE' ][ 'max' ] )
        main.ONOSport = main.params[ 'CTRL' ][ 'port' ]
        wrapperFile1 = main.params[ 'DEPENDENCY' ][ 'wrapper1' ]
        main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
        gitPull = main.params[ 'GIT' ][ 'pull' ]
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

        if gitPull == 'True':
            main.step( "Building ONOS in " + gitBranch + " branch" )
            onosBuildResult = main.startUp.onosBuild( main, gitBranch )
            stepResult = onosBuildResult
            utilities.assert_equals( expect=main.TRUE,
                                     actual=stepResult,
                                     onpass="Successfully compiled " +
                                            "latest ONOS",
                                     onfail="Failed to compile " +
                                            "latest ONOS" )
        else:
            main.log.warn( "Did not pull new code so skipping mvn " +
                           "clean install" )
        main.numCtrls = int( main.scale[ 0 ] )
         
    def CASE2( self, main ):
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
        main.numCtrls = int( main.scale[ 0 ] )
        main.scale.remove( main.scale[ 0 ] )
        apps=main.apps
        if main.diff:
            apps = main.apps+","+main.diff.pop(0)
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
        main.jsonFile=main.json.pop(0)
        main.ONOSbench.handle.sendline( "cp "+main.dependencyPath+"/"+main.jsonFile+".json ~/onos/tools/package/config/network-cfg.json")
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
        stopResult = main.TRUE
        startResult = main.TRUE
        onosIsUp = main.TRUE

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
        main.CLIs[0].startCellCli()
        cliResult = main.CLIs[0].startOnosCli( main.ONOSip[ 0 ],
                                           commandlineTimeout=60, onosStartTimeout=100 )
        utilities.assert_equals( expect=main.TRUE,
                             actual=cliResult,
                             onpass="ONOS CLI is ready",
                             onfail="ONOS CLI is not ready" )
        for i in range( 10 ):
            ready = True
            output = main.CLIs[0].summary()
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

    def CASE3( self, main ):
        """
            Start mininet
        """
        main.case( "Start Leaf-Spine "+main.jsonFile+" Mininet Topology" )
        main.log.report( "Start Mininet topology" )

        main.step( "Starting Mininet Topology" )
        args,topo=" "," "
        if main.args:
            args = "--onos %d %s" % (main.numCtrls, main.args.pop(0))
        else: main.log.error( "Argument list is empty" )
 
        topoResult = main.Mininet1.startNet( topoFile= main.dependencyPath + main.topology, args=args )
        stepResult = topoResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanup()
            main.exit()
        main.step(" Check whether the flow count is bigger than 116" )
        count =  utilities.retry( main.CLIs[0].checkFlowCount,
                                 main.FALSE,
                                 kwargs={'min':116},
                                 attempts=10,
                                 sleep=10 )
        utilities.assertEquals( \
            expect=True,
            actual=(count>0),
            onpass="Flow count looks correct: "+str(count),
            onfail="Flow count looks wrong: "+str(count) )

        main.step( "Check whether all flow status are ADDED" )
        flowCheck = utilities.retry( main.CLIs[0].checkFlowsState,
                                 main.FALSE,
                                 kwargs={'isPENDING':False},
                                 attempts=10,
                                 sleep=10)
        utilities.assertEquals( \
            expect=main.TRUE,
            actual=flowCheck,
            onpass="Flow status is correct!",
            onfail="Flow status is wrong!" )
        main.ONOSbench.dumpFlows( main.ONOSip[0],
                 main.logdir, "flowsBefore" + main.jsonFile)
        main.ONOSbench.dumpGroups( main.ONOSip[0],
                                   main.logdir, "groupsBefore" + main.jsonFile)
        main.count=1

    def CASE4( self, main ):
        main.case( "Check full connectivity" )
        main.log.report( "Check full connectivity" )

        main.step("Check full connectivity"+str(main.count))
        pa = main.Mininet1.pingall()
        utilities.assert_equals( expect=main.TRUE, actual=pa,
                                 onpass="Full connectivity successfully tested",
                                 onfail="Full connectivity failed" )
        main.ONOSbench.dumpFlows( main.ONOSip[0],
                 main.logdir, "flowsAfter" + str(main.count) + main.jsonFile)
        main.ONOSbench.dumpGroups( main.ONOSip[0],
                           main.logdir, "groupsAfter" + str(main.count) + main.jsonFile)

    def CASE5( self, main ):
        """
        Link spine101-leaf2 down
        Pingall
        Link spine101-leaf2 up
        Pingall
        """
        import time
        assert main.numCtrls, "main.numCtrls not defined"
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"
        assert main.CLIs, "main.CLIs not defined"

        linkSleep = float( main.params[ 'timers' ][ 'LinkDiscovery' ] )

        description = "Turn off a link to ensure that Segment Routing reroutes traffic " + \
                      "properly"
        main.case( description )

        main.step( "Kill Link between spine101 and leaf2" )
        LinkDown = main.Mininet1.link( END1="spine101", END2="leaf2", OPTION="down" )
        main.log.info( "Waiting %s seconds for link up to be discovered" % (linkSleep) )
        # TODO Maybe parameterize number of expected links
        time.sleep( linkSleep )
        topology =  utilities.retry( main.CLIs[0].checkStatus,
                                      main.FALSE,
                                      kwargs={'numoswitch':'4', 'numolink':'6'},
                                      attempts=10,
                                      sleep=linkSleep)
        result = topology & LinkDown
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                 onpass="Link down successful",
                                 onfail="Failed to turn off link?" )

        main.step( "Check connectivity after link failure" )
        pa = main.Mininet1.pingall()
        utilities.assert_equals( expect=main.TRUE, actual=pa,
                                 onpass="Survived link failure successfully",
                                 onfail="Did not survive link failure" )
        main.ONOSbench.dumpFlows( main.ONOSip[0],
                                  main.logdir,
                                  "flowsAfterLinkFailure" + main.jsonFile)
        main.ONOSbench.dumpGroups( main.ONOSip[0],
                                   main.logdir,
                                   "groupsAfterLinkFailure" + main.jsonFile)

        main.step( "Restore link between spine101 and leaf2" )

        result = False
        count=0
        while True:
            count+=0
            main.Mininet1.link( END1="spine101", END2="leaf2", OPTION="up" )
            main.Mininet1.link( END2="spine101", END1="leaf2", OPTION="up" )
            main.log.info( "Waiting %s seconds for link up to be discovered" % (linkSleep) )
            time.sleep( linkSleep )

            main.CLIs[0].portstate(dpid='of:0000000000000002', port='1')
            main.CLIs[0].portstate(dpid='of:0000000000000101', port='2')
            time.sleep( linkSleep )

            result = main.CLIs[0].checkStatus(numoswitch='4', numolink='8')
            if count>10 or result:
                break
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                 onpass="Link up successful",
                                 onfail="Failed to bring link up" )

        main.step( "Check connectivity after link recovery" )
        pa = main.Mininet1.pingall()
        utilities.assert_equals( expect=main.TRUE, actual=pa,
                                 onpass="Survived link recovery successfully",
                                 onfail="Did not survive link recovery" )
        main.ONOSbench.dumpFlows( main.ONOSip[0],
                                  main.logdir,
                                  "flowsAfterLinkRecovery" + main.jsonFile)
        main.ONOSbench.dumpGroups( main.ONOSip[0],
                                   main.logdir,
                                   "groupsAfterLinkRecovery" + main.jsonFile)

    def CASE6( self, main ):
        """
        Switch Down
        Pingall
        Switch up
        Pingall
        """
        import time
        assert main.numCtrls, "main.numCtrls not defined"
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"
        assert main.CLIs, "main.CLIs not defined"
    
        switchSleep = float( main.params[ 'timers' ][ 'SwitchDiscovery' ] )
    
        description = "Killing a switch to ensure it is discovered correctly"
        onosCli = main.CLIs[0]
        main.case( description )
        switch = main.params[ 'kill' ][ 'switch' ]
        switchDPID = main.params[ 'kill' ][ 'dpid' ]

        main.step( "Kill " + switch )
        main.log.info( "Stopping" + switch )
        main.Mininet1.switch( SW=switch, OPTION="stop")
        main.log.info( "Waiting %s seconds for switch down to be discovered" %(switchSleep))
        time.sleep( switchSleep )
        topology =  utilities.retry( main.CLIs[0].checkStatus,
                                      main.FALSE,
                                     kwargs={'numoswitch':'3', 'numolink':'4'},
                                      attempts=10,
                                     sleep=switchSleep)
        utilities.assert_equals( expect=main.TRUE, actual=topology,
                                 onpass="Kill switch successful",
                                 onfail="Failed to kill switch?" )

        main.step( "Check connectivity after switch failure" )
        pa = main.Mininet1.pingall()
        utilities.assert_equals( expect=main.TRUE, actual=pa,
                                 onpass="Survived switch failure successfully",
                                 onfail="Did not survive switch failure" )
        main.ONOSbench.dumpFlows( main.ONOSip[0],
                                  main.logdir,
                                  "flowsAfterSwitchFailure" + main.jsonFile)
        main.ONOSbench.dumpGroups( main.ONOSip[0],
                                   main.logdir,
                                   "groupsAfterSwitchFailure" + main.jsonFile)

        main.step( "Recovering " + switch )
        main.log.info( "Starting" + switch )
        main.Mininet1.switch( SW=switch, OPTION="start")
        main.log.info( "Waiting %s seconds for switch up to be discovered" %(switchSleep))
        time.sleep( switchSleep )
        topology =  utilities.retry( main.CLIs[0].checkStatus,
                                     main.FALSE,
                                     kwargs={'numoswitch':'4', 'numolink':'8'},
                                     attempts=10,
                                     sleep=switchSleep)
        utilities.assert_equals( expect=main.TRUE, actual=topology,
                                 onpass="Switch recovery successful",
                                 onfail="Failed to recover switch?" )

        main.step( "Check connectivity after switch recovery" )
        pa = main.Mininet1.pingall()
        utilities.assert_equals( expect=main.TRUE, actual=pa,
                                 onpass="Survived switch recovery successfully",
                                 onfail="Did not survive switch recovery" )
        main.ONOSbench.dumpFlows( main.ONOSip[0],
                                  main.logdir,
                                  "flowsAfterSwitchRecovery" + main.jsonFile)
        main.ONOSbench.dumpGroups( main.ONOSip[0],
                                   main.logdir,
                                   "groupsAfterSwitchRecovery" + main.jsonFile)

    def CASE7( self, main ):
        """
        OnosInstance1 Down
        Pingall
        OnosInstance1 up
        Pingall
        """

        description = "Killing single instance to test controlplane resilience of Segment Routing"
        main.case( description )
        main.step( "Killing ONOS instance" )
        killResult = main.ONOSbench.onosDie( main.CLIs[0].ip_address )
        utilities.assert_equals( expect=main.TRUE, actual=killResult,
                                 onpass="ONOS instance Killed",
                                 onfail="Error killing ONOS instance" )
        time.sleep( 12 )
        topology =  utilities.retry( main.CLIs[1].checkStatus,
                                     main.FALSE,
                                     kwargs={'numoswitch':'4', 'numolink':'8', 'numoctrl':'2'},
                                     attempts=10,
                                     sleep=12)
        utilities.assert_equals( expect=main.TRUE, actual=topology,
                                 onpass="ONOS Instance down successful",
                                 onfail="Failed to turn off ONOS Instance" )
        main.step( "Check connectivity after ONOS instance failure" )
        pa = main.Mininet1.pingall()
        utilities.assert_equals( expect=main.TRUE, actual=pa,
                                 onpass="Survived instance failure successfully",
                                 onfail="Did not survive instance failure" )
        main.ONOSbench.dumpFlows( main.ONOSip[1], main.logdir,
                                  "flowsAfterSwitchFailure" + main.jsonFile)
        main.ONOSbench.dumpGroups( main.ONOSip[1], main.logdir,
                                   "groupsAfterSwitchFailure" + main.jsonFile)
        main.step( "Recovering ONOS instance" )
        startResult = main.ONOSbench.onosStart( main.CLIs[0].ip_address )
        isUp = main.ONOSbench.isup( main.ONOSip[ 0 ] )
        utilities.assert_equals( expect=main.TRUE, actual=isUp,
                                 onpass="ONOS service is ready",
                                 onfail="ONOS service did not start properly" )
        main.step( "Checking if ONOS CLI is ready" )
        main.CLIs[0].startCellCli()
        cliResult = main.CLIs[0].startOnosCli( main.ONOSip[ 0 ],
                                               commandlineTimeout=60, onosStartTimeout=100 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=cliResult,
                                 onpass="ONOS CLI is ready",
                                 onfail="ONOS CLI is not ready" )
        for i in range( 10 ):
            ready = True
            output = main.CLIs[0].summary()
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
        main.step(" Check whether the flow count is bigger than 116" )
        count =  utilities.retry( main.CLIs[0].checkFlowCount,
                                  main.FALSE,
                                  kwargs={'min':116},
                                  attempts=10,
                                  sleep=10 )
        utilities.assertEquals( expect=True,
                                actual=(count>0),
                                onpass="Flow count looks correct: "+str(count),
                                onfail="Flow count looks wrong: "+str(count) )

        main.step( "Check connectivity after ONOS instance recovery" )
        pa = main.Mininet1.pingall()
        utilities.assert_equals( expect=main.TRUE, actual=pa,
                                 onpass="Survived instance recovery successfully",
                                 onfail="Did not survive recovery failure" )
        main.ONOSbench.dumpFlows( main.ONOSip[0], main.logdir,
                                  "flowsAfterCtrlFailure" + main.jsonFile)
        main.ONOSbench.dumpGroups( main.ONOSip[0], main.logdir,
                                   "groupsAfterCtrlFailure" + main.jsonFile)

    def CASE8( self, main ):
        """
        Cluster Down
        Pingall
        Cluster up
        Pingall
        """
        description = "Killing all instances to test controlplane resilience of Segment Routing"
        main.case( description )
        main.step( "Shutting down ONOS Cluster" )
        for i in range( main.numCtrls ):
            killResult = main.ONOSbench.onosDie( main.CLIs[i].ip_address )
            utilities.assert_equals( expect=main.TRUE, actual=killResult,
                                 onpass="ONOS instance Killed",
                                 onfail="Error killing ONOS instance" )
        time.sleep(12)
        main.step( "Check connectivity after ONOS instance failure" )
        pa = main.Mininet1.pingall()
        utilities.assert_equals( expect=main.TRUE, actual=pa,
                                 onpass="Survived instance failure successfully",
                                 onfail="Did not survive instance failure" )
        main.step( "Recovering ONOS Cluster" )
        for i in range( main.numCtrls ):
            startResult = main.ONOSbench.onosStart( main.CLIs[i].ip_address )
            isUp = main.ONOSbench.isup( main.ONOSip[ i ] )
            utilities.assert_equals( expect=main.TRUE, actual=isUp,
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
        for i in range( 10 ):
            ready = True
            output = main.CLIs[0].summary()
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

        main.step(" Check whether the flow count is bigger than 116" )
        count =  utilities.retry( main.CLIs[0].checkFlowCount,
                                  main.FALSE,
                                  kwargs={'min':116},
                                  attempts=10,
                                  sleep=10 )
        utilities.assertEquals( expect=True,
                                actual=(count>0),
                                onpass="Flow count looks correct: "+str(count),
                                onfail="Flow count looks wrong: "+str(count) )

        main.step( "Check connectivity after CLUSTER recovery" )
        pa = main.Mininet1.pingall()
        utilities.assert_equals( expect=main.TRUE, actual=pa,
                                 onpass="Survived instance recovery successfully",
                                 onfail="Did not survive recovery failure" )
        main.ONOSbench.dumpFlows( main.ONOSip[0], main.logdir,
                                  "flowsAfterCtrlFailure" + main.jsonFile)
        main.ONOSbench.dumpGroups( main.ONOSip[0], main.logdir,
                                   "groupsAfterCtrlFailure" + main.jsonFile)

    def CASE10( self, main ):
        '''
            Report errors/warnings/exceptions
        '''
        main.case( "Logging test for " + main.jsonFile )
        for i in range(main.numCtrls):
            main.ONOSbench.onosStop( main.ONOSip[i] )
        main.Mininet1.stopNet()
        
        main.ONOSbench.scp( main.ONOScli1 ,
                                          "/opt/onos/log/karaf.log",
                                          "/tmp/karaf.log",
                                          direction="from" )
        main.ONOSbench.cpLogsToDir("/tmp/karaf.log",main.logdir,
                                   copyFileName="karaf.log."+main.jsonFile+str(len(main.json)))
        #main.ONOSbench.logReport( main.ONOSip[ 0 ],
        #                          [ "INFO" ],
        #                          "a" )
        #main.log.info("Error report: \n" )
        main.ONOSbench.logReport( main.ONOSip[ 0 ],
                                  [ "INFO",
                                    "FOLLOWER",
                                    "WARN",
                                    "flow",
                                    "ERROR",
                                    "Except" ],
                                  "s" )
