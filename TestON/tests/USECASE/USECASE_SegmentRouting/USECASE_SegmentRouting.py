
# This test is to determine if the Segment Routing application is working properly

class USECASE_SegmentRouting:

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
        main.diff.extend(( main.params[ 'ENV' ][ 'diffApps' ] ).split(";"))
        gitBranch = main.params[ 'GIT' ][ 'branch' ]
        main.path = os.path.dirname( main.testFile )
        main.dependencyPath = main.path + "/dependencies/"
        main.topology = main.params[ 'DEPENDENCY' ][ 'topology' ]
        #main.json = ["0x1","0x1"]
        main.json = ["2x2", "2x2","4x4","4x4"]
        main.args = [" ", " ", " --spine 4 --leaf 4 ", " --spine 4 --leaf 4 "]
        #main.args = [" --spine 0 --leaf 1 "," --spine 0 --leaf 1 "]
        main.scale = ( main.params[ 'SCALE' ][ 'size' ] ).split( "," )
        main.maxNodes = int( main.params[ 'SCALE' ][ 'max' ] )
        main.ONOSport = main.params[ 'CTRL' ][ 'port' ]
        wrapperFile1 = main.params[ 'DEPENDENCY' ][ 'wrapper1' ]
        main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
        gitPull = main.params[ 'GIT' ][ 'pull' ]
        main.cellData = {} # for creating cell file
        main.CLIs = []
        main.ONOSip = []

        main.ONOSip = main.ONOSbench.getOnosIps()

        # Assigning ONOS cli handles to a list
        for i in range( 1,  main.maxNodes + 1 ):
            main.CLIs.append( getattr( main, 'ONOScli' + str( i ) ) )

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
        apps=main.apps
        if main.diff:
            apps = main.apps+","+main.diff.pop(0)
        else: main.log.error( "App list is empty" )
        main.case( "Package and start ONOS using apps:" + apps)

        print "NODE COUNT = ", main.numCtrls

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
        main.ONOSbench.handle.sendline( "cp "+main.path+"/"+main.jsonFile+".json ~/onos/tools/package/config/network-cfg.json")
        packageResult = main.ONOSbench.onosPackage()
        #stepResult = packageResult
        #utilities.assert_equals( expect=main.TRUE,
        #                         actual=stepResult,
        #                         onpass="Successfully created ONOS package",
        #                         onfail="Failed to create ONOS package" )

        #time.sleep( main.startUpSleep )

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
        #time.sleep( 2*main.startUpSleep )
        #main.ONOSbench.handle.sendline( "onos-secure-ssh")
        main.step( "Checking if ONOS CLI is ready" )
        cellResult = main.CLIs[0].setCell( "temp" )

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
        #if main.topology:
        #    topo = main.topology.pop(0)
        #else: main.log.error( "Topo list is empty" )
        if main.args:
            args = "--onos 1 " + main.args.pop(0)
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
        #main.step("Waiting for switch initialization and configuration")
        main.step(" Check whether the flow count is bigger than 116" )
        count =  utilities.retry( main.CLIs[0].checkFlowCount,
                                 main.FALSE,
                                 kwargs={'min':116},
                                 attempts=10 )
        utilities.assertEquals( \
            expect=True,
            actual=(count>0),
            onpass="Flow count looks correct: "+str(count),
            onfail="Flow count looks wrong: "+str(count) )

        main.step( "Check whether all flow status are ADDED" )
        flowCheck = utilities.retry( main.CLIs[0].checkFlowsState,
                                 main.FALSE,
                                 kwargs={'isPENDING':False},
                                 attempts=10 )
        utilities.assertEquals( \
            expect=main.TRUE,
            actual=flowCheck,
            onpass="Flow status is correct!",
            onfail="Flow status is wrong!" )
        main.ONOSbench.dumpFlows( main.ONOSip[0],
                 main.logdir, "flowsBefore" + main.jsonFile)
        main.ONOSbench.dumpGroups( main.ONOSip[0],
                                   main.logdir, "groupsBefore" + main.jsonFile)
        #time.sleep( 3*main.startUpSleep)
        main.count=1

    def CASE4( self, main ):
        main.case( "Check full connectivity" )
        main.log.report( "Check full connectivity" )

        main.step("Check full connectivity"+str(main.count))
        pa = main.Mininet1.pingall()
        utilities.assert_equals( expect=main.TRUE, actual=pa,
                                 onpass="Full connectivity successfully tested",
                                 onfail="Full connectivity failed" )
        # cleanup mininet
        main.ONOSbench.dumpFlows( main.ONOSip[0],
                 main.logdir, "flowsAfter" + str(main.count) + main.jsonFile)
        main.ONOSbench.dumpGroups( main.ONOSip[0],
                           main.logdir, "groupsAfter" + str(main.count) + main.jsonFile)

    def CASE10( self, main ):
        '''
            Report errors/warnings/exceptions
        '''
        main.case( "Logging test for " + main.jsonFile )
        #if len(main.json) > 0 :
        main.ONOSbench.onosStop( main.ONOSip[0] )
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



