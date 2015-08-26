
# This is a performance scale intent that test onos to see how many intents can
# be installed and rerouted using the null provider and mininet.

class SCPFmaxIntents:

    def __init__( self ):
        self.default = ''

    def CASE0( self, main ):
        import time
        import os
        import imp

        """
        - Construct tests variables
        - GIT ( optional )
            - Checkout ONOS master branch
            - Pull latest ONOS code
        - Building ONOS ( optional )
            - Install ONOS package
            - Build ONOS package
        """

        main.case( "Constructing test variables and building ONOS package" )
        main.step( "Constructing test variables" )
        stepResult = main.FALSE

        # Test variables
        main.testOnDirectory = os.path.dirname( os.getcwd ( ) )
        main.dependencyPath = main.testOnDirectory + \
                main.params['DEPENDENCY']['path']
        main.cellName = main.params[ 'ENV' ][ 'cellName' ]
        main.apps = main.params[ 'ENV' ][ 'cellApps' ]
        gitBranch = main.params[ 'GIT' ][ 'branch' ]
        main.topology = main.params[ 'DEPENDENCY' ][ 'topology' ]
        main.scale = ( main.params[ 'SCALE' ][ 'size' ] ).split( "," )
        main.maxNodes = int( main.params[ 'SCALE' ][ 'max' ] )
        main.ONOSport = main.params[ 'CTRL' ][ 'port' ]
        main.timeout = int(main.params['SLEEP']['timeout'])
        main.minIntents = int(main.params['TEST']['min_intents'])
        main.checkInterval = int(main.params['TEST']['check_interval'])
        wrapperFile1 = main.params[ 'DEPENDENCY' ][ 'wrapper1' ]
        wrapperFile2 = main.params[ 'DEPENDENCY' ][ 'wrapper2' ]
        main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
        main.installSleep = int( main.params[ 'SLEEP' ][ 'install' ] )
        main.verifySleep = int( main.params[ 'SLEEP' ][ 'verify' ] )
        main.rerouteSleep = int ( main.params['SLEEP']['reroute'] )
        gitPull = main.params[ 'GIT' ][ 'pull' ]
        main.batchSize = int(main.params['TEST']['batch_size'])
        main.cellData = {} # for creating cell file
        main.CLIs = []
        main.ONOSip = []
        main.maxNumBatch = 0

        main.ONOSip = main.ONOSbench.getOnosIps()
        main.log.info(main.ONOSip)

        # Assigning ONOS cli handles to a list
        for i in range( 1,  main.maxNodes + 1 ):
            main.CLIs.append( getattr( main, 'ONOScli' + str( i ) ) )

        # -- INIT SECTION, ONLY RUNS ONCE -- #
        main.startUp = imp.load_source( wrapperFile1,
                                        main.dependencyPath +
                                        wrapperFile1 +
                                        ".py" )

        main.intentFunctions = imp.load_source( wrapperFile2,
                                               main.dependencyPath +
                                               wrapperFile2 +
                                               ".py" )

        copyResult = main.ONOSbench.copyMininetFile( main.topology,
                                                    main.dependencyPath,
                                                    main.Mininet1.user_name,
                                                    main.Mininet1.ip_address )

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

    def CASE1( self, main ):
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

        main.case( "Starting up " + str( main.numCtrls ) +
                   " node(s) ONOS cluster" )

        # kill off all onos processes
        main.log.info( "Safety check, killing all ONOS processes" +
                       " before initiating enviornment setup" )

        for i in range( main.maxNodes ):
            main.ONOSbench.onosDie( main.ONOSip[ i ] )

        main.log.info( "NODE COUNT = " + str( main.numCtrls))

        tempOnosIp = []
        for i in range( main.numCtrls ):
            tempOnosIp.append( main.ONOSip[i] )

        main.ONOSbench.createCellFile( main.ONOSbench.ip_address,
                                       "temp",
                                       main.Mininet1.ip_address,
                                       main.apps,
                                       tempOnosIp )

        main.step( "Apply cell to environment" )
        cellResult = main.ONOSbench.setCell( "temp" )
        verifyResult = main.ONOSbench.verifyCell()
        stepResult = cellResult and verifyResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully applied cell to " + \
                                        "environment",
                                 onfail="Failed to apply cell to environment " )

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()
        stepResult = packageResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully created ONOS package",
                                 onfail="Failed to create ONOS package" )

        main.step( "Uninstalling ONOS package" )
        onosUninstallResult = main.TRUE
        for i in range( main.maxNodes ):
            onosUninstallResult = onosUninstallResult and \
                    main.ONOSbench.onosUninstall( nodeIp=main.ONOSip[ i ] )
        stepResult = onosUninstallResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully uninstalled ONOS package",
                                 onfail="Failed to uninstall ONOS package" )

        time.sleep( main.startUpSleep )
        main.step( "Installing ONOS package" )
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

        main.step( "Start ONOS cli" )
        cliResult = main.TRUE
        for i in range( main.numCtrls ):
            cliResult = cliResult and \
                        main.CLIs[ i ].startOnosCli( main.ONOSip[ i ] )
        stepResult = cliResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully start ONOS cli",
                                 onfail="Failed to start ONOS cli" )

    def CASE10( self, main ):
        """
            Setting up null-provider
        """
        import json
        import pexpect

        # Activate apps
        main.log.step("Activating apps")
        stepResult = main.CLIs[0].activateApp('org.onosproject.null')
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully activated null-provider",
                                 onfail="Failed to activate null-provider")

        # Setup the null-provider
        main.log.step("Configuring null-provider")
        stepResult = main.FALSE
        for i in range(3):
            main.ONOSbench.onosCfgSet( main.ONOSip[0],
                                                    'org.onosproject.provider.nil.NullProviders',
                                                    'deviceCount 3' )
            main.ONOSbench.onosCfgSet( main.ONOSip[0],
                                                    'org.onosproject.provider.nil.NullProviders',
                                                    'topoShape reroute' )
            main.ONOSbench.onosCfgSet( main.ONOSip[0],
                                                    'org.onosproject.provider.nil.NullProviders',
                                                    'enabled true' )
            # give onos some time to settle
            time.sleep(main.startUpSleep)
            jsonSum = json.loads(main.CLIs[0].summary())
            if jsonSum['devices'] == 3 and jsonSum['SCC(s)'] == 1:
                stepResult = main.TRUE
                break
        utilities.assert_equals( expect=stepResult,
                                     actual=stepResult,
                                     onpass="Successfully configured the null-provider",
                                     onfail="Failed to configure the null-provider")


        main.log.step("Get default flows")
        jsonSum = json.loads(main.CLIs[0].summary())

        # flows installed by the null-provider
        main.defaultFlows = jsonSum["flows"]
        main.ingress =  ":0000000000000001/3"
        main.egress = ":0000000000000003/2"
        main.switch = "null"
        main.linkUpCmd = "null-link null:0000000000000001/3 null:0000000000000003/1 up"
        main.linkDownCmd = "null-link null:0000000000000001/3 null:0000000000000003/1 down"

    def CASE11( self, main ):
        '''
            Setting up mininet
        '''
        import json
        import time

        # Activate apps
        main.log.step("Activating apps")
        stepResult = main.CLIs[0].activateApp('org.onosproject.openflow')

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully activated openflow",
                                 onfail="Failed to activate openflow")
        # give onos some time settle
        time.sleep(main.startUpSleep)

        main.log.step('Starting mininet topology')
        main.Mininet1.startNet(topoFile='~/mininet/custom/rerouteTopo.py')
        main.Mininet1.assignSwController(sw='s1', ip=main.ONOSip[0])
        main.Mininet1.assignSwController(sw='s2', ip=main.ONOSip[0])
        main.Mininet1.assignSwController(sw='s3', ip=main.ONOSip[0])
        time.sleep(main.startUpSleep)

        jsonSum = json.loads(main.CLIs[0].summary())
        if jsonSum['devices'] == 3 and jsonSum['SCC(s)'] == 1:
            stepResult = main.TRUE

        utilities.assert_equals( expect=stepResult,
                                     actual=stepResult,
                                     onpass="Successfully assigned switches to their master",
                                     onfail="Failed to assign switches")

        main.log.step("Get default flows")
        jsonSum = json.loads(main.CLIs[0].summary())

        # flows installed by the null-provider
        main.defaultFlows = jsonSum["flows"]
        main.ingress =  ":0000000000000001/3"
        main.egress = ":0000000000000003/2"
        main.switch = "of"
        main.linkDownCmd = 'link s1 s3 down'
        main.linkUpCmd = 'link s1 s3 up'


    def CASE20( self, main ):
        import pexpect
        '''
            Pushing intents
        '''
        # the index where the next intents will be installed
        offset = 0
        # the number of intents we expect to be in the installed state
        expectedIntents = 0
        # the number of flows we expect to be in the added state
        expectedFlows = main.defaultFlows

        try:
            while True:
                # Push intents
                main.log.step("Pushing intents")
                stepResult = main.intentFunctions.pushIntents( main,
                                                               main.switch,
                                                               main.ingress,
                                                               main.egress,
                                                               main.batchSize,
                                                               offset,
                                                               sleep=main.installSleep,
                                                               timeout=main.timeout,
                                                               options="-i" )
                utilities.assert_equals( expect=main.TRUE,
                                     actual=stepResult,
                                     onpass="Successfully pushed intents",
                                     onfail="Failed to push intents")
                if stepResult == main.FALSE:
                    break

                offset += main.batchSize
                expectedIntents = offset
                expectedFlows += main.batchSize*2

                if offset >= main.minIntents and offset % main.checkInterval == 0:
                    # Verifying intents
                    main.log.step("Verifying intents")
                    main.log.info("Expected intents: " + str(expectedIntents))
                    stepResult = main.intentFunctions.verifyIntents( main,
                                                                     expectedIntents,
                                                                     sleep=main.verifySleep,
                                                                     timeout=main.timeout)
                    utilities.assert_equals( expect=main.TRUE,
                                             actual=stepResult,
                                             onpass="Successfully verified intents",
                                             onfail="Failed to verify intents")

                    if stepResult == main.FALSE:
                        break

                    # Verfying flows
                    main.log.step("Verifying flows")
                    main.log.info("Expected Flows: " + str(expectedFlows))
                    stepResult = main.intentFunctions.verifyFlows( main,
                                                                   expectedFlows,
                                                                   sleep=main.verifySleep,
                                                                   timeout=main.timeout)

                    utilities.assert_equals( expect=main.TRUE,
                                             actual=stepResult,
                                             onpass="Successfully verified flows",
                                             onfail="Failed to verify flows")

                    if stepResult == main.FALSE:
                        break

        except pexpect.TIMEOUT:
            main.log.exception("Timeout exception caught")

        main.log.report("Done pushing intents")
        main.log.info("Summary: Intents=" + str(expectedIntents) + " Flows=" + str(expectedFlows))
        main.log.info("Installed intents: " + str(main.intentFunctions.getIntents(main)) +
                      "\nAdded flows: " + str(main.intentFunctions.getFlows(main)))

        # Stopping mininet
        if main.switch == "of":
            main.log.info("Stopping mininet")
            main.Mininet1.stopNet()

    def CASE21( self, main ):
        import pexpect
        import time
        '''
            Reroute
        '''
        # the index where the next intents will be installed
        offset = 0
        # the number of intents we expect to be in the installed state
        expectedIntents = 0
        # the number of flows we expect to be in the added state
        expectedFlows = main.defaultFlows

        try:
            while True:
                # Push intents
                main.log.step("Pushing intents")
                stepResult = main.intentFunctions.pushIntents( main,
                                                               main.switch,
                                                               main.ingress,
                                                               main.egress,
                                                               main.batchSize,
                                                               offset,
                                                               sleep=main.installSleep,
                                                               options="-i",
                                                               timeout=main.timeout )
                utilities.assert_equals( expect=main.TRUE,
                                     actual=stepResult,
                                     onpass="Successfully pushed intents",
                                     onfail="Failed to push intents")
                if stepResult == main.FALSE:
                    break

                offset += main.batchSize
                expectedIntents = offset
                expectedFlows += main.batchSize*2

                # Verifying intents
                main.log.step("Verifying intents")
                main.log.info("Expected intents: " + str(expectedIntents))
                stepResult = main.intentFunctions.verifyIntents( main,
                                                                 expectedIntents,
                                                                 sleep=main.verifySleep,
                                                                 timeout=main.timeout )
                utilities.assert_equals( expect=main.TRUE,
                                         actual=stepResult,
                                         onpass="Successfully verified intents",
                                         onfail="Failed to verify intents")

                if stepResult == main.FALSE:
                    break

                # Verfying flows
                main.log.step("Verifying flows")
                main.log.info("Expected Flows: " + str(expectedFlows))
                stepResult = main.intentFunctions.verifyFlows( main,
                                                               expectedFlows,
                                                               sleep=main.verifySleep,
                                                               timeout=main.timeout )
                utilities.assert_equals( expect=main.TRUE,
                                         actual=stepResult,
                                         onpass="Successfully verified flows",
                                         onfail="Failed to verify flows")

                if stepResult == main.FALSE:
                    break

                # tear down a link
                main.log.step("Tearing down link")
                if main.switch == "of":
                    main.log.info("Sending: " + main.linkDownCmd)
                    main.Mininet1.handle.sendline(main.linkDownCmd)
                    main.Mininet1.handle.expect('mininet>')
                else:
                    main.log.info("Sending: " + main.linkDownCmd)
                    main.CLIs[0].handle.sendline(main.linkDownCmd)
                    main.CLIs[0].handle.expect('onos>')
                time.sleep(main.rerouteSleep)

                # rerouting adds a 1000 flows
                expectedFlows += 1000

                # Verfying flows
                main.log.step("Verifying flows")
                main.log.info("Expected Flows: " + str(expectedFlows))
                stepResult = main.intentFunctions.verifyFlows( main,
                                                               expectedFlows,
                                                               sleep=main.verifySleep,
                                                               timeout=main.timeout)
                utilities.assert_equals( expect=main.TRUE,
                                         actual=stepResult,
                                         onpass="Successfully verified flows",
                                         onfail="Failed to verify flows")

                if stepResult == main.FALSE:
                    break

                # Bring link back up
                main.log.step("Tearing down link")
                if main.switch == "of":
                    main.log.info("Sending: " + main.linkUpCmd)
                    main.Mininet1.handle.sendline(main.linkUpCmd)
                    main.Mininet1.handle.expect('mininet>')
                else:
                    main.log.info("Sending: " + main.linkUpCmd)
                    main.CLIs[0].handle.sendline(main.linkUpCmd)
                    main.CLIs[0].handle.expect('onos>')
                time.sleep(main.rerouteSleep)

        except pexpect.TIMEOUT:
            main.log.exception("Timeout exception caught")

        main.log.report("Done pushing intents")
        main.log.info("Summary: Intents=" + str(expectedIntents) + " Flows=" + str(expectedFlows))
        main.log.info("Installed intents: " + str(main.intentFunctions.getIntents(main)) +
                      "\nAdded flows: " + str(main.intentFunctions.getFlows(main)))

        # Stopping mininet
        if main.switch == "of":
            main.log.info("Stopping mininet")
            main.Mininet1.stopNet()

    def CASE100( self, main ):
        '''
            Report errors/warnings/exceptions
        '''
        main.log.info("Error report: \n")
        main.ONOSbench.logReport( main.ONOSip[ 0 ],
                                  [ "INFO",
                                    "FOLLOWER",
                                    "WARN",
                                    "flow",
                                    "ERROR",
                                    "Except" ],
                                  "s" )
