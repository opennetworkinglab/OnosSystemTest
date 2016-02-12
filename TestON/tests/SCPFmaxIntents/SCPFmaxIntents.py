
# This is a performance scale intent that test onos to see how many intents can
# be installed and rerouted using the null provider and mininet.
'''
This test will not test on reroute and OVS!!!
If you need test on reroute or OVS, change the params file

Test information:
    - BatchSize: 1000
    - Minimum intents: 10,000
    - Maximum Intents: 1,000,000
    - Check Interval: 10,000
    - Link:
        - ingress: 0000000000000001/9
        - egress: 0000000000000002/9
    - Timeout: 120 Seconds
'''

class SCPFmaxIntents:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
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
        - Set up cell
            - Create cell file
            - Set cell file
            - Verify cell file
        - Kill ONOS process
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
        main.topology = main.params[ 'DEPENDENCY' ][ 'topology' ]
        main.scale = ( main.params[ 'SCALE' ][ 'size' ] ).split( "," )
        main.maxNodes = int( main.params[ 'SCALE' ][ 'max' ] )
        main.ONOSport = main.params[ 'CTRL' ][ 'port' ]
        main.timeout = int(main.params['SLEEP']['timeout'])
        main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
        main.installSleep = int( main.params[ 'SLEEP' ][ 'install' ] )
        main.verifySleep = int( main.params[ 'SLEEP' ][ 'verify' ] )
        main.rerouteSleep = int ( main.params['SLEEP']['reroute'] )
        main.verifyAttempts = int( main.params['ATTEMPTS']['verify'] )
        main.ingress = main.params['LINK']['ingress']
        main.egress = main.params['LINK']['egress']
        main.dbFileName = main.params['DATABASE']['file']
        main.cellData = {} # for creating cell file
        main.reroute = main.params['reroute']
        if main.reroute == "True":
            main.reroute = True
        else:
            main.reroute = False
        main.CLIs = []
        main.ONOSip = []
        main.maxNumBatch = 0
        main.ONOSip = main.ONOSbench.getOnosIps()
        main.log.info(main.ONOSip)
        main.setupSkipped = False

        wrapperFile1 = main.params[ 'DEPENDENCY' ][ 'wrapper1' ]
        wrapperFile2 = main.params[ 'DEPENDENCY' ][ 'wrapper2' ]
        gitBranch = main.params[ 'GIT' ][ 'branch' ]
        gitPull = main.params[ 'GIT' ][ 'pull' ]
        nic = main.params['DATABASE']['nic']
        node = main.params['DATABASE']['node']
        nic = main.params['DATABASE']['nic']
        node = main.params['DATABASE']['node']

        # main.scale[ 0 ] determines the current number of ONOS controller
        main.numCtrls = int( main.scale[ 0 ] )

        main.log.info("Creating list of ONOS cli handles")
        for i in range(main.maxNodes):
            main.CLIs.append( getattr( main, 'ONOScli' + str( i+1 )))

        if not main.CLIs:
            main.log.error("Failed to create the list of ONOS cli handles")
            main.cleanup()
            main.exit()

        main.log.info("Loading wrapper files")
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

        commit = main.ONOSbench.getVersion(report=True)
        commit = commit.split(" ")[1]

        if gitPull == 'True':
            if not main.startUp.onosBuild( main, gitBranch ):
                main.log.error("Failed to build ONOS")
                main.cleanup()
                main.exit()
        else:
            main.log.warn( "Did not pull new code so skipping mvn " +
                           "clean install" )

        main.log.info( "Starting up %s node(s) ONOS cluster" % main.numCtrls)
        main.log.info( "Safety check, killing all ONOS processes" +
                       " before initiating environment setup" )

        for i in range( main.maxNodes ):
            main.ONOSbench.onosDie( main.ONOSip[ i ] )

        main.log.info( "NODE COUNT = %s" % main.numCtrls)

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

        main.log.info("Creating DB file")
        with open(main.dbFileName, "w+") as dbFile:
            temp = "'" + commit + "',"
            temp += "'" + nic + "',"
            temp += str(main.numCtrls) + ","
            temp += "'" + node + "1" + "'"
            temp += ",0"
            temp += ",0"
            temp += ",0"
            temp += ",0"
            dbFile.write(temp)

    def CASE2( self, main ):
        """
        - Uninstall ONOS cluster
        - Verify ONOS start up
        - Install ONOS cluster
        - Connect to cli
        """

        main.step( "Installing ONOS with -f" )
        onosInstallResult = main.TRUE
        for i in range( main.numCtrls ):
            onosInstallResult = onosInstallResult and \
                    main.ONOSbench.onosInstall( node=main.ONOSip[ i ] )
        stepResult = onosInstallResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully installed ONOS package",
                                 onfail="Failed to install ONOS package" )

        time.sleep( main.startUpSleep )

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

        time.sleep( main.startUpSleep )

    def CASE10( self, main ):
        """
            Setting up null-provider
        """
        import json
        # Activate apps
        main.step("Activating null-provider")
        appStatus = utilities.retry( main.CLIs[0].activateApp,
                                     main.FALSE,
                                     ['org.onosproject.null'],
                                     sleep=main.verifySleep,
                                     attempts=main.verifyAttempts )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=appStatus,
                                 onpass="Successfully activated null-provider",
                                 onfail="Failed activate null-provider" )

        # Setup the null-provider
        main.step("Configuring null-provider")
        cfgStatus = utilities.retry( main.ONOSbench.onosCfgSet,
                                     main.FALSE,
                                     [ main.ONOSip[0],
                                      'org.onosproject.provider.nil.NullProviders', 'deviceCount 3'],
                                     sleep=main.verifySleep,
                                     attempts = main.verifyAttempts )
        cfgStatus = cfgStatus and utilities.retry( main.ONOSbench.onosCfgSet,
                                                   main.FALSE,
                                                   [ main.ONOSip[0],
                                                     'org.onosproject.provider.nil.NullProviders', 'topoShape reroute'],
                                                   sleep=main.verifySleep,
                                                   attempts = main.verifyAttempts )

        cfgStatus = cfgStatus and utilities.retry( main.ONOSbench.onosCfgSet,
                                                   main.FALSE,
                                                   [ main.ONOSip[0],
                                                     'org.onosproject.provider.nil.NullProviders', 'enabled true'],
                                                   sleep=main.verifySleep,
                                                   attempts = main.verifyAttempts )


        utilities.assert_equals( expect=main.TRUE,
                                 actual=cfgStatus,
                                 onpass="Successfully configured null-provider",
                                 onfail="Failed to configure null-provider" )

        # give onos some time to settle
        time.sleep(main.startUpSleep)

        main.log.info("Setting default flows to zero")
        main.defaultFlows = 0

        main.step("Check status of null-provider setup")
        caseResult = appStatus and cfgStatus
        utilities.assert_equals( expect=main.TRUE,
                                 actual=caseResult,
                                 onpass="Setting up null-provider was successfull",
                                 onfail="Failed to setup null-provider" )

        # This tells the following cases if we are using the null-provider or ovs
        main.switchType = "null:"

        # If the null-provider setup was unsuccessfull, then there is no point to
        # run the subsequent cases
        if not caseResult:
            main.setupSkipped = True

    def CASE11( self, main ):
        '''
            Setting up mininet
        '''
        import json
        import time

        time.sleep(main.startUpSleep)

        main.step("Activating openflow")
        appStatus = main.CLIs[0].activateApp('org.onosproject.openflow')
        utilities.assert_equals( expect=main.TRUE,
                                 actual=appStatus,
                                 onpass="Successfully activated openflow",
                                 onfail="Failed activate openflow" )

        time.sleep(main.startUpSleep)

        main.step('Starting mininet topology')
        mnStatus = main.Mininet1.startNet(topoFile='~/mininet/custom/rerouteTopo.py')
        utilities.assert_equals( expect=main.TRUE,
                                 actual=mnStatus,
                                 onpass="Successfully started Mininet",
                                 onfail="Failed to activate Mininet" )

        main.step("Assinging masters to switches")
        switches = main.Mininet1.getSwitches()
        swStatus = main.Mininet1.assignSwController( sw=switches.keys(), ip=main.ONOSip )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=swStatus,
                                 onpass="Successfully assigned switches to masters",
                                 onfail="Failed assign switches to masters" )

        time.sleep(main.startUpSleep)

        main.log.info("Getting default flows")
        jsonSum = json.loads(main.CLIs[0].summary())
        main.defaultFlows = jsonSum["flows"]

        main.step("Check status of Mininet setup")
        caseResult = appStatus and mnStatus and swStatus
        utilities.assert_equals( expect=main.TRUE,
                                 actual=caseResult,
                                 onpass="Successfully setup Mininet",
                                 onfail="Failed setup Mininet" )

        # This tells the following cases if we are using the null-provider or ovs
        main.switchType = "of:"

        if not caseResult:
            main.setupSkipped = True

    def CASE20( self, main ):
        '''
            Pushing intents
        '''

        if main.reroute:
            if main.switchType == "of:":
                main.minIntents = int(main.params['OVS']['REROUTE']['min_intents'])
                main.maxIntents = int(main.params['OVS']['REROUTE']['max_intents'])
                main.checkInterval = int(main.params['OVS']['REROUTE']['check_interval'])
                main.batchSize = int(main.params['OVS']['REROUTE']['batch_size'])
            else:
                main.minIntents = int(main.params['NULL']['REROUTE']['min_intents'])
                main.maxIntents = int(main.params['NULL']['REROUTE']['max_intents'])
                main.checkInterval = int(main.params['NULL']['REROUTE']['check_interval'])
                main.batchSize = int(main.params['NULL']['REROUTE']['batch_size'])
        else:
            if main.switchType == "of:":
                main.minIntents = int(main.params['OVS']['PUSH']['min_intents'])
                main.maxIntents = int(main.params['OVS']['PUSH']['max_intents'])
                main.checkInterval = int(main.params['OVS']['PUSH']['check_interval'])
                main.batchSize = int(main.params['OVS']['PUSH']['batch_size'])
            else:
                main.minIntents = int(main.params['NULL']['PUSH']['min_intents'])
                main.maxIntents = int(main.params['NULL']['PUSH']['max_intents'])
                main.checkInterval = int(main.params['NULL']['PUSH']['check_interval'])
                main.batchSize = int(main.params['NULL']['PUSH']['batch_size'])

        # check if the case needs to be skipped
        if main.setupSkipped:
            main.setupSkipped = False
            main.skipCase()

        # the index where the next intents will be installed
        offset = 0
        # keeps track of how many intents have been installed
        currIntents = 0
        # keeps track of how many flows have been installed
        currFlows = main.defaultFlows
        # limit for the number of intents that can be installed
        limit = main.maxIntents / main.batchSize

        main.step( "Pushing intents" )
        for i in range(limit):
            pushResult = main.ONOScli1.pushTestIntents( main.switchType +  main.ingress,
                                                        main.switchType +  main.egress,
                                                        main.batchSize,
                                                        offset = offset,
                                                        options = "-i",
                                                        timeout = main.timeout )
            if pushResult == None:
                main.log.info( "Timeout!" )
                main.skipCase()
            time.sleep(1)

            # Update offset
            offset += main.batchSize

            if offset >= main.minIntents and offset % main.checkInterval == 0:
                intentVerify = utilities.retry( main.ONOScli1.checkIntentSummary,
                                                main.FALSE,
                                                [main.timeout],
                                                sleep=main.verifySleep,
                                                attempts=main.verifyAttempts )

                flowVerify = utilities.retry( main.ONOScli1.checkFlowsState,
                                              main.FALSE,
                                              [False,main.timeout],
                                              sleep=main.verifySleep,
                                              attempts=main.verifyAttempts )

                if not intentVerify:
                    main.log.error( "Failed to install intents" )
                    break

                if main.reroute:
                    main.step( "Reroute" )
                    # tear down a link
                    main.log.info("Tearing down link")
                    if main.switchType == "of:":
                        downlink = main.Mininet1.link( END1 = "s1", END2 = "s3", OPTION = "down" )
                    else:
                        downlink = main.ONOScli1.link( main.ingress, main.egress, "down")

                    if downlink:
                        main.log.info( "Successfully tear down link" )
                    else:
                        main.log.warn( "Failed to tear down link" )

                    time.sleep(main.rerouteSleep)

                    # Verifying intents
                    main.step( "Checking intents and flows" )
                    intentVerify = utilities.retry( main.ONOScli1.checkIntentSummary,
                                                    main.FALSE,
                                                    [main.timeout],
                                                    sleep=main.verifySleep,
                                                    attempts=main.verifyAttempts )
                    # Verfying flows
                    flowVerify = utilities.retry( main.ONOScli1.checkFlowsState,
                                                  main.FALSE,
                                                  [False, main.timeout],
                                                  sleep = main.verifySleep,
                                                  attempts = main.verifyAttempts )

                    if not intentVerify:
                        main.log.error( "Failed to install intents" )
                    # Bring link back up
                    main.log.info("Bringing link back up")
                    if main.switchType == "of:":
                        uplink = main.Mininet1.link( END1 = "s1", END2 = "s3", OPTION = "up" )
                    else:
                        uplink = main.ONOScli1.link( main.ingress, main.egress, "up" )

                    if uplink:
                        main.log.info( "Successfully bring link back up" )
                    else:
                        main.log.warn( "Failed to bring link back up" )

                    time.sleep(main.rerouteSleep)

                    # Verifying intents
                    main.step( "Checking intents and flows" )
                    intentVerify = utilities.retry( main.ONOScli1.checkIntentSummary,
                                                    main.FALSE,
                                                    [main.timeout],
                                                    sleep=main.verifySleep,
                                                    attempts=main.verifyAttempts )
                    # Verfying flows
                    flowVerify = utilities.retry( main.ONOScli1.checkFlowsState,
                                                  main.FALSE,
                                                  [False, main.timeout],
                                                  sleep = main.verifySleep,
                                                  attempts = main.verifyAttempts )

                    if not intentVerify:
                        main.log.error( "Failed to install intents" )

                    rerouteResult = downlink and uplink
                    utilities.assert_equals( expect = main.TRUE,
                                             actual = rerouteResult,
                                             onpass = "Successfully reroute",
                                             onfail = "Failed to reroute" )

        utilities.assert_equals( expect = main.TRUE,
                                 actual = intentVerify,
                                 onpass = "Successfully pushed and verified intents",
                                 onfail = "Failed to push and verify intents" )
        currIntents = main.ONOScli1.getTotalIntentsNum()
        currFlows = 0
        # Get current flows from REST API
        temp = json.loads( main.ONOSrest1.flows() )
        for t in temp:
            if t.get("state") == "ADDED":
                currFlows = currFlows + 1
        main.log.info( "Total Intents Installed: {}".format( currIntents ) )
        main.log.info( "Total Flows ADDED: {}".format( currFlows ) )

        main.log.info("Writing results to DB file")
        with open(main.dbFileName, "a") as dbFile:
            temp = "," + str(currIntents)
            temp += "," + str(currFlows)
            temp += ",0"
            temp += ",0\n"
            dbFile.write(temp)

        if main.switchType == "of:":
            main.step( "Stopping mininet" )
            stepResult = main.Mininet1.stopNet()
            utilities.assert_equals( expect = main.TRUE,
                                     actual = stepResult,
                                     oppass = "Successfully stop Mininet",
                                     opfail = "Failed stop Mininet" )


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
