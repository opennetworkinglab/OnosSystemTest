import sys
import json
import time
import os
'''
SCPFscalingMaxIntents
Push test Intents to onos
CASE10: set up Null Provider
CASE11: set up Open Flows
Scale up when reach the Limited
Start from 1 nodes, 8 devices. Then Scale up to 3,5,7 nodes
Recommand batch size: 100, check interval: 100
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
        main.scale = ( main.params[ 'SCALE' ] ).split( "," )
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
        main.threadID = 0

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
        gitBranch = main.params[ 'GIT' ][ 'branch' ]
        gitPull = main.params[ 'GIT' ][ 'pull' ]
        nic = main.params['DATABASE']['nic']
        node = main.params['DATABASE']['node']
        nic = main.params['DATABASE']['nic']
        node = main.params['DATABASE']['node']
        stepResult = main.TRUE

        main.log.info("Cresting DB file")
        with open(main.dbFileName, "w+") as dbFile:
            dbFile.write("")

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="environment set up successfull",
                                 onfail="environment set up Failed" )

    def CASE1( self ):
        # main.scale[ 0 ] determines the current number of ONOS controller
        main.CLIs = []
        main.numCtrls = int( main.scale[ 0 ] )
        main.log.info( "Creating list of ONOS cli handles" )
        for i in range(main.numCtrls):
            main.CLIs.append( getattr( main, 'ONOScli%s' % (i+1) ) )

        main.log.info(main.CLIs)
        if not main.CLIs:
            main.log.error( "Failed to create the list of ONOS cli handles" )
            main.cleanup()
            main.exit()

        main.log.info( "Loading wrapper files" )
        main.startUp = imp.load_source( wrapperFile1,
                                        main.dependencyPath +
                                        wrapperFile1 +
                                        ".py" )

        copyResult = main.ONOSbench.copyMininetFile( main.topology,
                                                     main.dependencyPath,
                                                     main.Mininet1.user_name,
                                                     main.Mininet1.ip_address )

        commit = main.ONOSbench.getVersion(report=True)
        commit = commit.split(" ")[1]

        if gitPull == 'True':
            if not main.startUp.onosBuild( main, gitBranch ):
                main.log.error( "Failed to build ONOS" )
                main.cleanup()
                main.exit()
        else:
            main.log.warn( "Did not pull new code so skipping mvn " +
                           "clean install" )
        with open(main.dbFileName, "a") as dbFile:
            temp = "'" + commit + "',"
            temp += "'" + nic + "',"
            dbFile.write(temp)

    def CASE2( self, main ):
        """
        - Uninstall ONOS cluster
        - Verify ONOS start up
        - Install ONOS cluster
        - Connect to cli
        """
        main.log.info( "Starting up %s node(s) ONOS cluster" % main.numCtrls)
        main.log.info( "Safety check, killing all ONOS processes" +
                       " before initiating environment setup" )

        for i in range( main.numCtrls ):
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

        main.step( "Uninstall ONOS package on all Nodes" )
        uninstallResult = main.TRUE
        for i in range( int( main.numCtrls ) ):
            main.log.info( "Uninstalling package on ONOS Node IP: " + main.ONOSip[i] )
            u_result = main.ONOSbench.onosUninstall( main.ONOSip[i] )
            utilities.assert_equals( expect=main.TRUE, actual=u_result,
                                     onpass="Test step PASS",
                                     onfail="Test step FAIL" )
            uninstallResult = ( uninstallResult and u_result )

        main.step( "Install ONOS package on all Nodes" )
        installResult = main.TRUE
        for i in range( int( main.numCtrls ) ):
            main.log.info( "Installing package on ONOS Node IP: " + main.ONOSip[i] )
            i_result = main.ONOSbench.onosInstall( node=main.ONOSip[i] )
            utilities.assert_equals( expect=main.TRUE, actual=i_result,
                                     onpass="Test step PASS",
                                     onfail="Test step FAIL" )
            installResult = installResult and i_result

        main.step( "Verify ONOS nodes UP status" )
        statusResult = main.TRUE
        for i in range( int( main.numCtrls ) ):
            main.log.info( "ONOS Node " + main.ONOSip[i] + " status:" )
            onos_status = main.ONOSbench.onosStatus( node=main.ONOSip[i] )
            utilities.assert_equals( expect=main.TRUE, actual=onos_status,
                                     onpass="Test step PASS",
                                     onfail="Test step FAIL" )
            statusResult = ( statusResult and onos_status )

        main.step( "Start ONOS CLI on all nodes" )
        cliResult = main.TRUE
        main.log.step(" Start ONOS cli using thread ")
        startCliResult  = main.TRUE
        pool = []

        for i in range( int( main.numCtrls) ):
            t = main.Thread( target=main.CLIs[i].startOnosCli,
                             threadID=main.threadID,
                             name="startOnosCli",
                             args=[ main.ONOSip[i] ],
                             kwargs = {"onosStartTimeout":main.timeout} )
            pool.append(t)
            t.start()
            main.threadID = main.threadID + 1
        for t in pool:
            t.join()
            startCliResult = startCliResult and t.result
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
                                      'org.onosproject.provider.nil.NullProviders', 'deviceCount 8'],
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

        time.sleep(main.startUpSleep)

        main.step("Activating openflow")
        appStatus = utilities.retry( main.ONOSrest1.activateApp,
                                     main.FALSE,
                                     ['org.onosproject.openflow'],
                                     sleep=3,
                                     attempts=3 )
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
        if main.reroute:
            main.minIntents = int(main.params['NULL']['REROUTE']['min_intents'])
            main.maxIntents = int(main.params['NULL']['REROUTE']['max_intents'])
            main.checkInterval = int(main.params['NULL']['REROUTE']['check_interval'])
            main.batchSize = int(main.params['NULL']['REROUTE']['batch_size'])
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
        offfset = 0
        # keeps track of how many intents have been installed
        currIntents = 0
        # keeps track of how many flows have been installed, set to 0 at start
        currFlows = 0
        # limit for the number of intents that can be installed
        limit = main.maxIntents / main.batchSize
        # total intents installed
        totalIntents = 0

        intentsState = None

        offtmp = 0
        main.step( "Pushing intents" )
        stepResult = main.TRUE

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
                                          "background":False } )
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
                intentVerify = main.FALSE

                while k <= main.verifyAttempts:
                    # while loop for check intents by using REST api
                    time.sleep(5)
                    temp = 0
                    intentsState = json.loads( main.ONOSrest1.intents() )
                    for f in intentsState:
                        # get INSTALLED intents number
                        if f.get("state") == "INSTALLED":
                            temp = temp + 1

                    main.log.info("Total Intents: {} INSTALLED: {}".format(totalIntents, temp))
                    if totalIntents == temp:
                        intentVerify = main.TRUE
                        break
                    intentVerify = main.FALSE
                    k = k+1

                if not intentVerify:
                    # If some intents are not installed, finished this test case
                    main.log.warn( "Some intens did not install" )
                    # We don't want to check flows if intents not installed, because onos will drop flows
                    if currFlows == 0:
                    # If currFlows equal 0, which means we failed to install intents at first, or we didn't get
                    # the correct number, so we need get flows here.
                        flowsState = json.loads( main.ONOSrest1.flows() )
                    break

                main.log.info("Verify Flows states")
                k = 1
                flowsVerify = main.TRUE

                while k <= main.verifyAttempts:
                    # while loop for check flows by using REST api
                    time.sleep(3)
                    temp = 0
                    flowsStateCount = []
                    flowsState = json.loads( main.ONOSrest1.flows() )
                    for f in flowsState:
                        # get PENDING_ADD flows
                        if f.get("state") == "PENDING_ADD":
                            temp = temp + 1

                    flowsStateCount.append(temp)
                    temp = 0

                    for f in flowsState:
                        # get PENDING_REMOVE flows
                        if f.get("state") == "PENDING_REMOVE":
                            temp = temp + 1

                    flowsStateCount.append(temp)
                    temp = 0

                    for f in flowsState:
                        # get REMOVED flows
                        if f.get("state") == "REMOVED":
                            temp = temp + 1

                    flowsStateCount.append(temp)
                    temp = 0

                    for f in flowsState:
                        # get FAILED flwos
                        if f.get("state") == "FAILED":
                            temp = temp + 1

                    flowsStateCount.append(temp)
                    temp = 0
                    k = k + 1
                    for c in flowsStateCount:
                        if int(c) > 0:
                            flowsVerify = main.FALSE

                    main.log.info( "Check flows States:" )
                    main.log.info( "PENDING_ADD: {}".format( flowsStateCount[0]) )
                    main.log.info( "PENDING_REMOVE: {}".format( flowsStateCount[1]) )
                    main.log.info( "REMOVED: {}".format( flowsStateCount[2]) )
                    main.log.info( "FAILED: {}".format( flowsStateCount[3]) )

                    if flowsVerify == main.TRUE:
                        break

        del main.scale[0]
        utilities.assert_equals( expect = main.TRUE,
                                 actual = intentVerify,
                                 onpass = "Successfully pushed and verified intents",
                                 onfail = "Failed to push and verify intents" )

        # we need the total intents before crash
        totalIntents = len(intentsState)
        totalFlows = len(flowsState)

        main.log.info( "Total Intents Installed before crash: {}".format( totalIntents ) )
        main.log.info( "Total Flows ADDED before crash: {}".format( totalFlows ) )

        main.step('clean up Mininet')
        main.Mininet1.stopNet()

        main.log.info("Writing results to DS file")
        with open(main.dbFileName, "a") as dbFile:
            # Scale number
            temp = str(main.numCtrls)
            temp += ",'" + "baremetal1" + "'"
            # how many intents we installed before crash
            temp += "," + str(totalIntents)
            # how many flows we installed before crash
            temp += "," + str(totalFlows)
            # other columns in database, but we didn't use in this test
            temp += "," + "0,0,0,0,0,0"
            temp += "\n"
            dbFile.write( temp )
