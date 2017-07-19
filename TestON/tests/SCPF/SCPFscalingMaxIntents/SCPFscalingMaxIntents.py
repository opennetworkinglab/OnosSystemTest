import sys
import json
import time
import os
'''
SCPFscalingMaxIntents
Push test Intents to onos
CASE10: set up Null Provider
CASE11: set up Open Flows
Check flows number, if flows number is not as except, finished this test iteration
Scale up when reach the Limited
Start from 1 nodes, 8 devices. Then Scale up to 3,5,7 nodes
'''
class SCPFscalingMaxIntents:
    def __init__( self ):
        self.default = ''

    def CASE0( self, main):
        import sys
        import json
        import time
        import os
        import imp
        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
            main.testSetUp = ONOSSetup()
        except ImportError:
            main.log.error( "ONOSSetup not found. exiting the test" )
            main.exit()
        main.testSetUp.envSetupDescription()
        stepResult = main.FALSE
        try:
            # Test variables
            main.dependencyPath = main.testOnDirectory + \
                    main.params[ 'DEPENDENCY' ][ 'path' ]
            main.cellName = main.params[ 'ENV' ][ 'cellName' ]
            main.apps = main.params[ 'ENV' ][ 'cellApps' ]
            main.topology = main.params[ 'DEPENDENCY' ][ 'topology' ]
            main.scale = ( main.params[ 'SCALE' ] ).split( "," )
            main.ONOSport = main.params[ 'CTRL' ][ 'port' ]
            main.timeout = int( main.params[ 'SLEEP' ][ 'timeout' ] )
            main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
            main.installSleep = int( main.params[ 'SLEEP' ][ 'install' ] )
            main.verifySleep = int( main.params[ 'SLEEP' ][ 'verify' ] )
            main.rerouteSleep = int ( main.params[ 'SLEEP' ][ 'reroute' ] )
            main.verifyAttempts = int( main.params[ 'ATTEMPTS' ][ 'verify' ] )
            main.ingress = main.params[ 'LINK' ][ 'ingress' ]
            main.egress = main.params[ 'LINK' ][ 'egress' ]
            main.reroute = main.params[ 'reroute' ]
            main.flowObj = main.params[ 'TEST' ][ 'flowObj' ]
            if main.flowObj == "True":
                main.flowObj = True
                main.dbFileName = main.params[ 'DATABASE' ][ 'dbFlowObj' ]
            else:
                main.flowObj = False
                main.dbFileName = main.params[ 'DATABASE' ][ 'dbName' ]
            main.threadID = 0

            if main.reroute == "True":
                main.reroute = True
            else:
                main.reroute = False
            main.setupSkipped = False

            wrapperFile1 = main.params[ 'DEPENDENCY' ][ 'wrapper1' ]
            nic = main.params[ 'DATABASE' ][ 'nic' ]
            node = main.params[ 'DATABASE' ][ 'node' ]
            stepResult = main.testSetUp.gitPulling()
            main.log.info( "Cresting DB file" )
            with open( main.dbFileName, "w+" ) as dbFile:
                dbFile.write("")
        except Exception as e:
            main.testSetUp.envSetupException( e )
        main.testSetUp.evnSetupConclusion( stepResult )
        main.commit = main.commit.split( " " )[ 1 ]
        with open( main.dbFileName, "a" ) as dbFile:
            temp = "'" + main.commit + "',"
            temp += "'" + nic + "',"
            dbFile.write( temp )
    def CASE1( self ):
        main.testSetUp.getNumCtrls( True )
        main.testSetUp.envSetup( includeGitPull=False, makeMaxNodes=False )
        copyResult = main.ONOSbench.copyMininetFile( main.topology,
                                                     main.dependencyPath,
                                                     main.Mininet1.user_name,
                                                     main.Mininet1.ip_address )

    def CASE2( self, main ):
        """
        - Uninstall ONOS cluster
        - Verify ONOS start up
        - Install ONOS cluster
        - Connect to cli
        """
        main.testSetUp.ONOSSetUp( main.Mininet1, True,
                                  killRemoveMax=False, CtrlsSet=False )

    def CASE10( self, main ):
        """
            Setting up null-provider
        """
        import json
        # Activate apps
        main.step("Activating null-provider")
        appStatus = utilities.retry( main.CLIs[0].activateApp,
                                     main.FALSE,
                                     [ 'org.onosproject.null' ],
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
                                      'org.onosproject.provider.nil.NullProviders', 'deviceCount 8' ],
                                    sleep=main.verifySleep,
                                    attempts = main.verifyAttempts )
        cfgStatus = cfgStatus and utilities.retry( main.ONOSbench.onosCfgSet,
                                                   main.FALSE,
                                                   [ main.ONOSip[0],
                                                     'org.onosproject.provider.nil.NullProviders', 'topoShape reroute' ],
                                                   sleep=main.verifySleep,
                                                   attempts = main.verifyAttempts )

        cfgStatus = cfgStatus and utilities.retry( main.ONOSbench.onosCfgSet,
                                                   main.FALSE,
                                                   [ main.ONOSip[0],
                                                     'org.onosproject.provider.nil.NullProviders', 'enabled true' ],
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

        time.sleep(main.startUpSleep)
        main.step( "Balancing Masters" )

        stepResult = main.FALSE
        stepResult = utilities.retry( main.CLIs[0].balanceMasters,
                                      main.FALSE,
                                      [],
                                      sleep=3,
                                      attempts=3 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Balance masters was successfull",
                                 onfail="Failed to balance masters")

        time.sleep( 5 )
        if not caseResult:
            main.setupSkipped = True

    def CASE11( self, main):
        '''
            Setting up mininet
        '''
        import json
        import time
 
        devices = []
        devices = main.CLIs[0].getAllDevicesId()
        for d in devices:
            main.CLIs[0].deviceRemove( d )

        time.sleep(main.startUpSleep)
        if main.flowObj:
            main.CLIs[0].setCfg("org.onosproject.net.intent.impl.compiler.IntentConfigurableRegistrator",
                                "useFlowObjectives", value="true")
            main.CLIs[0].setCfg("org.onosproject.net.intent.impl.compiler.IntentConfigurableRegistrator",
                                "defaultFlowObjectiveCompiler",
                                value='org.onosproject.net.intent.impl.compiler.LinkCollectionIntentObjectiveCompiler')
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
        # Balancing Masters
        main.step( "Balancing Masters" )
        stepResult = main.FALSE
        stepResult = utilities.retry( main.CLIs[0].balanceMasters,
                                      main.FALSE,
                                      [],
                                      sleep=3,
                                      attempts=3 )

        utilities.assert_equals( expect=main.TRUE,
                                       actual=stepResult,
                                       onpass="Balance masters was successfull",
                                       onfail="Failed to balance masters" )

        main.log.info("Getting default flows")
        jsonSum = json.loads(main.CLIs[0].summary())
        main.defaultFlows = jsonSum["flows"]

        main.step("Check status of Mininet setup")
        caseResult = mnStatus and swStatus
        utilities.assert_equals( expect=main.TRUE,
                                 actual=caseResult,
                                 onpass="Successfully setup Mininet",
                                 onfail="Failed setup Mininet" )

        # This tells the following cases if we are using the null-provider or ovs
        main.switchType = "of:"

        time.sleep(main.startUpSleep)
        main.step( "Balancing Masters" )

        stepResult = main.FALSE
        stepResult = utilities.retry( main.CLIs[0].balanceMasters,
                                      main.FALSE,
                                      [],
                                      sleep=3,
                                      attempts=3 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Balance masters was successfull",
                                 onfail="Failed to balance masters")

        time.sleep(5)
        if not caseResult:
            main.setupSkipped = True



    def CASE20( self, main ):
        try:
            from tests.dependencies.utils import Utils
        except ImportError:
            main.log.error( "Utils not found exiting the test" )
            main.exit()
        try:
            main.Utils
        except ( NameError, AttributeError ):
            main.Utils = Utils()
        if main.reroute:
            main.minIntents = int(main.params[ 'NULL' ][ 'REROUTE' ][ 'min_intents' ] )
            main.maxIntents = int(main.params[ 'NULL' ][ 'REROUTE' ][ 'max_intents' ] )
            main.checkInterval = int(main.params[ 'NULL' ][ 'REROUTE' ][ 'check_interval' ] )
            main.batchSize = int(main.params[ 'NULL' ][ 'REROUTE' ][ 'batch_size' ] )
        else:
            main.minIntents = int(main.params[ 'NULL' ][ 'PUSH' ][ 'min_intents' ] )
            main.maxIntents = int(main.params[ 'NULL' ][ 'PUSH' ][ 'max_intents' ] )
            main.checkInterval = int(main.params[ 'NULL' ][ 'PUSH' ][ 'check_interval' ] )
            main.batchSize = int(main.params[ 'NULL' ][ 'PUSH' ][ 'batch_size' ] )

        # check if the case needs to be skipped
        if main.setupSkipped:
            main.setupSkipped = False
            main.skipCase()

        # the index where the next intents will be installed
        offfset = 0
        # keeps track of how many intents have been installed
        currIntents = 0
        # keeps track of how many flows have been installed, set to 0 at start
        currFlows = 0
        # limit for the number of intents that can be installed
        main.batchSize = int( int(main.batchSize)/int(main.numCtrls))
        limit = main.maxIntents / main.batchSize
        # total intents installed
        totalIntents = 0

        intentsState = None

        offtmp = 0
        main.step( "Pushing intents" )
        stepResult = main.TRUE
        # temp variable to contain the number of flows
        flowsNum = 0
        if main.numCtrls > 1:
            # if more than one onos nodes, we should check more frequently
            main.checkInterval = main.checkInterval/4

        # make sure the checkInterval divisible batchSize
        main.checkInterval = int( int( main.checkInterval / main.batchSize ) * main.batchSize )
        flowTemp=0
        intentVerifyTemp = 0
        totalFlows=0
        for i in range(limit):

            # Threads pool
            pool = []

            for j in range( int( main.numCtrls) ):
                if main.numCtrls > 1:
                    time.sleep( 1 )
                offtmp = offfset + main.maxIntents * j
                # Push intents by using threads
                t = main.Thread( target=main.CLIs[j].pushTestIntents,
                                 threadID=main.threadID,
                                 name="Push-Test-Intents",
                                 args=[ main.switchType + main.ingress,
                                        main.switchType + main.egress,
                                        main.batchSize ],
                                 kwargs={ "offset": offtmp,
                                          "options": "-i",
                                          "timeout": main.timeout,
                                          "background":False,
                                          "noExit":True} )
                pool.append(t)
                t.start()
                main.threadID = main.threadID + 1
            for t in pool:
                t.join()
                stepResult = stepResult and t.result
            offfset = offfset + main.batchSize

            totalIntents = main.batchSize * main.numCtrls + totalIntents
            if totalIntents >= main.minIntents and totalIntents % main.checkInterval == 0:
                # if reach to minimum number and check interval, verify Intetns and flows
                time.sleep( main.verifySleep * main.numCtrls )

                main.log.info("Verify Intents states")
                # k is a control variable for verify retry attempts
                k = 1
                while k <= main.verifyAttempts:
                    # while loop for check intents by using CLI driver
                    time.sleep(5)
                    intentsState = main.CLIs[0].checkIntentSummary(timeout=600, noExit=True)
                    if intentsState:
                        verifyTotalIntents = main.CLIs[0].getTotalIntentsNum(timeout=600, noExit=True)
                        if intentVerifyTemp < verifyTotalIntents:
                            intentVerifyTemp = verifyTotalIntents
                        else:
                            verifyTotalIntents = intentVerifyTemp
                            intentsState = False
                        main.log.info("Total Installed Intents: {}".format( verifyTotalIntents ) )
                        break
                    k = k+1

                k = 1
                flowVerify = True
                while k <= main.verifyAttempts:
                    time.sleep(5)
                    totalFlows = main.CLIs[0].getTotalFlowsNum( timeout=600, noExit=True )
                    expectFlows = totalIntents * 7 + main.defaultFlows
                    if totalFlows == expectFlows:
                        main.log.info("Total Flows Added: {}".format(totalFlows))
                        break
                    else:
                        main.log.info("Some Flows are not added, retry...")
                        main.log.info("Total Flows Added: {} Expect Flows: {}".format(totalFlows, expectFlows))
                        flowVerify = False

                    k += 1
                    if flowTemp < totalFlows:
                        flowTemp = totalFlows
                    else:
                        totalFlows = flowTemp

                if not intentsState or not flowVerify:
                    # If some intents are not installed, grep the previous flows list, and finished this test case
                    main.log.warn( "Intents or flows are not installed" )
                    verifyTotalIntents = main.CLIs[0].getTotalIntentsNum(timeout=600, noExit=True)
                    if intentVerifyTemp < verifyTotalIntents:
                        intentVerifyTemp = verifyTotalIntents
                    else:
                        verifyTotalIntents = intentVerifyTemp
                    if flowTemp < totalFlows:
                        flowTemp = totalFlows
                    else:
                        totalFlows = flowTemp
                    main.log.info("Total Intents: {}".format( verifyTotalIntents) )
                    break

        utilities.assert_equals( expect = main.TRUE,
                                 actual = intentsState,
                                 onpass = "Successfully pushed and verified intents",
                                 onfail = "Failed to push and verify intents" )

        main.log.info( "Total Intents Installed before crash: {}".format( totalIntents ) )
        main.log.info( "Total Flows ADDED before crash: {}".format( totalFlows ) )

        main.Utils.mininetCleanup( main.Mininet1 )

        main.log.info("Writing results to DS file")
        with open(main.dbFileName, "a") as dbFile:
            # Scale number
            temp = str(main.numCtrls)
            temp += ",'" + "baremetal1" + "'"
            # how many intents we installed before crash
            temp += "," + str(verifyTotalIntents)
            # how many flows we installed before crash
            temp += "," + str(totalFlows)
            # other columns in database, but we didn't use in this test
            temp += "," + "0,0,0,0,0,0"
            temp += "\n"
            dbFile.write( temp )
