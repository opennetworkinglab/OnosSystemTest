
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
        main.minIntents = int(main.params['TEST']['min_intents'])
        main.maxIntents = int(main.params['TEST']['max_intents'])
        main.checkInterval = int(main.params['TEST']['check_interval'])
        main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
        main.installSleep = int( main.params[ 'SLEEP' ][ 'install' ] )
        main.verifySleep = int( main.params[ 'SLEEP' ][ 'verify' ] )
        main.rerouteSleep = int ( main.params['SLEEP']['reroute'] )
        main.batchSize = int(main.params['TEST']['batch_size'])
        main.dbFileName = main.params['DATABASE']['file']
        main.cellData = {} # for creating cell file
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
                       " before initiating enviornment setup" )

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

        main.log.info( "Applying cell to environment" )
        cell = main.ONOSbench.setCell( "temp" )
        verify = main.ONOSbench.verifyCell()
        if not cell or not verify:
            main.log.error("Failed to apply cell to environment")
            main.cleanup()
            main.exit()

        main.log.info( "Creating ONOS package" )
        if not main.ONOSbench.onosPackage():
            main.log.error("Failed to create ONOS package")
            main.cleanup()
            main.exit()

        main.log.info("Creating DB file")
        with open(main.dbFileName, "w+") as dbFile:
            temp = "'" + commit + "',"
            temp += "'" + nic + "',"
            temp += str(main.numCtrls) + ","
            temp += "'" + node + "1" + "'"
            dbFile.write(temp)

    def CASE1( self, main ):
        """
        - Uninstall ONOS cluster
        - Verify ONOS start up
        - Install ONOS cluster
        - Connect to cli
        """

        main.log.info( "Uninstalling ONOS package" )
        main.ONOSbench.onosUninstall( nodeIp=main.ONOSip[i] )
        for i in range( main.maxNodes ):
            if not main.ONOSbench.onosUninstall( nodeIp=main.ONOSip[i] ):
                main.log.error("Failed to uninstall onos on node %s" % (i+1))
                main.cleanup()
                main.exit()

        main.log.info( "Installing ONOS package" )
        for i in range( main.numCtrls ):
            if not main.ONOSbench.onosInstall( node=main.ONOSip[i] ):
                main.log.error("Failed to install onos on node %s" % (i+1))
                main.cleanup()
                main.exit()

        main.log.info( "Starting ONOS service" )
        for i in range( main.numCtrls ):
            start = main.ONOSbench.onosStart( main.ONOSip[i] )
            isup = main.ONOSbench.isup( main.ONOSip[i] )
            if not start or not isup:
                main.log.error("Failed to start onos service on node %s" % (i+1))
                main.cleanup()
                main.exit()

        main.log.info( "Starting ONOS cli" )
        for i in range( main.numCtrls ):
            if not main.CLIs[i].startOnosCli( main.ONOSip[i] ):
                main.log.error("Failed to start onos cli on node %s" % (i+1))
                main.cleanup()
                main.exit()

    def CASE10( self, main ):
        """
            Setting up null-provider
        """
        import json
        import pexpect

        # Activate apps
        main.log.info("Activating null-provider")
        appStatus = main.CLIs[0].activateApp('org.onosproject.null')
        if not appStatus:
            main.log.error("Failed to activate null-provider")

        # Setup the null-provider
        main.log.info("Configuring null-provider")
        cfgStatus = main.ONOSbench.onosCfgSet( main.ONOSip[0],
                'org.onosproject.provider.nil.NullProviders', 'deviceCount 3' )
        cfgStatus = cfgStatus and main.ONOSbench.onosCfgSet( main.ONOSip[0],
                'org.onosproject.provider.nil.NullProviders', 'topoShape reroute' )
        cfgStatus = cfgStatus and main.ONOSbench.onosCfgSet( main.ONOSip[0],
                'org.onosproject.provider.nil.NullProviders', 'enabled true' )

        if not cfgStatus:
            main.log.error("Failed to configure null-provider")

        # give onos some time to settle
        time.sleep(main.startUpSleep)

        main.defaultFlows = 0
        main.ingress =  ":0000000000000001/3"
        main.egress = ":0000000000000003/2"
        main.switch = "null"
        main.linkUpCmd = "null-link null:0000000000000001/3 null:0000000000000003/1 up"
        main.linkDownCmd = "null-link null:0000000000000001/3 null:0000000000000003/1 down"

        if not appStatus or not cfgStatus:
            main.setupSkipped = True

    def CASE11( self, main ):
        '''
            Setting up mininet
        '''
        import json
        import time

        main.log.step("Activating openflow")
        appStatus = main.CLIs[0].activateApp('org.onosproject.openflow')
        if appStatus:
            main.log.error("Failed to activate openflow")

        time.sleep(main.startUpSleep)

        main.log.info('Starting mininet topology')
        mnStatus = main.Mininet1.startNet(topoFile='~/mininet/custom/rerouteTopo.py')
        if mnStatus:
            main.log.error("Failed to start mininet")

        main.log.info("Assinging masters to switches")
        swStatus =  main.Mininet1.assignSwController(sw='s1', ip=main.ONOSip[0])
        swStatus = swStatus and  main.Mininet1.assignSwController(sw='s2', ip=main.ONOSip[0])
        swStatus = swStatus and main.Mininet1.assignSwController(sw='s3', ip=main.ONOSip[0])
        if not swStatus:
            main.log.info("Failed to assign masters to switches")

        time.sleep(main.startUpSleep)

        jsonSum = json.loads(main.CLIs[0].summary())
        sumStatus = (jsonSum['devices'] == 3 and jsonSum['SCC(s)'] == 1)

        main.log.step("Getting default flows")
        jsonSum = json.loads(main.CLIs[0].summary())

        main.defaultFlows = jsonSum["flows"]
        main.ingress =  ":0000000000000001/3"
        main.egress = ":0000000000000003/2"
        main.switch = "of"
        main.linkDownCmd = 'link s1 s3 down'
        main.linkUpCmd = 'link s1 s3 up'

        if not appStatus or not mnStatus or not swStatus or not sumStatus:
            main.setupSkipped = True

    def CASE20( self, main ):
        import pexpect
        '''
            Pushing intents
        '''

        # check if the setup case has been skipped
        if main.setupSkipped:
            main.setupSkipped = False
            main.skipCase()

        # the index where the next intents will be installed
        offset = 0
        # the number of intents we expect to be in the installed state
        expectedIntents = 0
        # keeps track of how many intents have been installed
        maxIntents = 0
        # the number of flows we expect to be in the added state
        expectedFlows = main.defaultFlows
        # keeps track of how many flows have been installed
        maxFlows = main.defaultFlows
        # limit for the number of intents that can be installed
        limit = main.maxIntents / main.batchSize

        for i in range(limit):
            # Push intents
            main.log.info("Pushing intents")
            main.intentFunctions.pushIntents( main,
                                              main.switch,
                                              main.ingress,
                                              main.egress,
                                              main.batchSize,
                                              offset,
                                              sleep=main.installSleep,
                                              timeout=main.timeout,
                                              options="-i" )

            offset += main.batchSize
            expectedIntents = offset
            expectedFlows += main.batchSize*2

            main.log.info("Grabbing number of installed intents and flows")
            maxIntents = main.intentFunctions.getIntents( main )
            maxFlows = main.intentFunctions.getFlows( main )

            if offset >= main.minIntents and offset % main.checkInterval == 0 or expectedIntents == main.maxIntents:
                # Verifying intents
                main.log.info("Verifying intents\nExpected intents: " + str(expectedIntents))
                intentStatus = main.intentFunctions.verifyIntents( main,
                                                                   expectedIntents,
                                                                   sleep=main.verifySleep,
                                                                   timeout=main.timeout)
                # Verfying flows
                main.log.info("Verifying flows\nExpected Flows: " + str(expectedFlows))
                flowStatus = main.intentFunctions.verifyFlows( main,
                                                               expectedFlows,
                                                               sleep=main.verifySleep,
                                                               timeout=main.timeout)

                if not flowStatus or not intentsStataus:
                    main.log.error("Failed to verify")
                    break

        main.log.info("Summary: Intents=" + str(expectedIntents) + " Flows=" + str(expectedFlows))
        main.log.info("Installed intents: " + str(maxIntents) +
                      " Added flows: " + str(maxFlows))

        main.log.info("Writing results to DB file")
        with open(dbFileName, "a") as dbFile:
            temp = "," + str(maxIntents)
            temp += "," + str(maxFlows)
            dbFile.write(temp)

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

        # check if the setup case has been skipped
        if main.setupSkipped:
            main.setupSkipped = False
            main.skipCase()

        # the index where the next intents will be installed
        offset = 0
        # the number of intents we expect to be in the installed state
        expectedIntents = 0
        # keeps track of how many intents have been installed
        maxIntents = 0
        # the number of flows we expect to be in the added state
        expectedFlows = main.defaultFlows
        # keeps track of how many flows have been installed
        maxFlows = main.defaultFlows
        # limit for the number of intents that can be installed
        limit = main.maxIntents / main.batchSize

        for i in range(limit):
            # Push intents
            main.log.info("Pushing intents")
            main.intentFunctions.pushIntents( main,
                                              main.switch,
                                              main.ingress,
                                              main.egress,
                                              main.batchSize,
                                              offset,
                                              sleep=main.installSleep,
                                              timeout=main.timeout,
                                              options="-i" )

            offset += main.batchSize
            expectedIntents = offset
            expectedFlows += main.batchSize*2

            main.log.info("Grabbing number of installed intents and flows")
            maxIntents = main.intentFunctions.getIntents( main )
            maxFlows = main.intentFunctions.getFlows( main )

            # Verifying intents
            main.log.info("Verifying intents\n\tExpected intents: " + str(expectedIntents))
            intentStatus = main.intentFunctions.verifyIntents( main,
                                                               expectedIntents,
                                                               sleep=main.verifySleep,
                                                               timeout=main.timeout)
            # Verfying flows
            main.log.info("Verifying flows\n\tExpected Flows: " + str(expectedFlows))
            flowStatus = main.intentFunctions.verifyFlows( main,
                                                           expectedFlows,
                                                           sleep=main.verifySleep,
                                                           timeout=main.timeout)

            if not flowStatus or not intentsStataus:
                main.log.error("Failed to verify\n\tSkipping case")
                main.log.skipCase()

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

            main.log.info("Grabbing number of added flows")
            maxFlows = main.intentFunctions.getFlows( main )

            # Verfying flows
            main.log.info("Verifying flows\n\tExpected Flows: " + str(expectedFlows))
            flowStatus = main.intentFunctions.verifyFlows( main,
                                                           expectedFlows,
                                                           sleep=main.verifySleep,
                                                           timeout=main.timeout)
            if not flowStatus:
                main.log.error("Failed to verify flows\n\tSkipping case")
                main.skipCase()

            # Bring link back up
            main.log.step("Bringing link back up")
            if main.switch == "of":
                main.log.info("Sending: " + main.linkUpCmd)
                main.Mininet1.handle.sendline(main.linkUpCmd)
                main.Mininet1.handle.expect('mininet>')
            else:
                main.log.info("Sending: " + main.linkUpCmd)
                main.CLIs[0].handle.sendline(main.linkUpCmd)
                main.CLIs[0].handle.expect('onos>')

            time.sleep(main.rerouteSleep)

        main.log.info("Summary: Intents=" + str(expectedIntents) + " Flows=" + str(expectedFlows))
        main.log.info("Installed intents: " + str(maxIntents) +
                      " Added flows: " + str(maxFlows))

        with open(main.dbFileName, "a") as dbFile:
            temp = "," + str(maxIntents)
            temp += "," + str(maxFlows)
            dbFile.write(temp)

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
