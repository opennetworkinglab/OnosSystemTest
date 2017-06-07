# SCPFintentRerouteLat
"""
SCPFintentRerouteLat
    - Test Intent Reroute Latency
    - Test Algorithm:
        1. Start Null Provider reroute Topology
        2. Using Push-test-intents to push batch size intents from switch 1 to switch 7
        3. Cut the link between switch 3 and switch 4 (the path will reroute to switch 8)
        4. Get the topology time stamp
        5. Get Intent reroute(Installed) time stamp from each nodes
        6. Use the latest intent time stamp subtract topology time stamp
    - This test will run 5 warm up by default, warm up iteration can be setup in Param file
    - The intent batch size will default set to 1, 100, and 1000, also can be set in Param file
    - The unit of the latency result is milliseconds
"""


class SCPFintentRerouteLat:
    def __init__(self):
        self.default = ''

    def CASE0( self, main ):
        import imp
        import os
        '''
        - GIT
        - BUILDING ONOS
            Pull specific ONOS branch, then Build ONOS ono ONOS Bench.
            This step is usually skipped. Because in a Jenkins driven automated
            test env. We want Jenkins jobs to pull&build for flexibility to handle
            different versions of ONOS.
        - Construct tests variables
        '''
        gitPull = main.params['GIT']['gitPull']
        gitBranch = main.params['GIT']['gitBranch']

        main.case("Pull onos branch and build onos on Teststation.")

        if gitPull == 'True':
            main.step("Git Checkout ONOS branch: " + gitBranch)
            stepResult = main.ONOSbench.gitCheckout(branch=gitBranch)
            utilities.assert_equals(expect=main.TRUE,
                                    actual=stepResult,
                                    onpass="Successfully checkout onos branch.",
                                    onfail="Failed to checkout onos branch. Exiting test...")
            if not stepResult:
                main.exit()

            main.step("Git Pull on ONOS branch:" + gitBranch)
            stepResult = main.ONOSbench.gitPull()
            utilities.assert_equals(expect=main.TRUE,
                                    actual=stepResult,
                                    onpass="Successfully pull onos. ",
                                    onfail="Failed to pull onos. Exiting test ...")
            if not stepResult: main.exit()

            main.step("Building ONOS branch: " + gitBranch)
            stepResult = main.ONOSbench.cleanInstall(skipTest=True)
            utilities.assert_equals(expect=main.TRUE,
                                    actual=stepResult,
                                    onpass="Successfully build onos.",
                                    onfail="Failed to build onos. Exiting test...")
            if not stepResult:
                main.exit()

        else:
            main.log.warn("Skipped pulling onos and Skipped building ONOS")
        main.onosIp = main.ONOSbench.getOnosIps()
        main.apps = main.params['ENV']['cellApps']
        main.BENCHUser = main.params['BENCH']['user']
        main.BENCHIp = main.params['BENCH']['ip1']
        main.MN1Ip = main.params['MN']['ip1']
        main.maxNodes = int(main.params['max'])
        main.skipMvn = main.params['TEST']['skipCleanInstall']
        main.cellName = main.params['ENV']['cellName']
        main.scale = (main.params['SCALE']).split(",")
        main.timeout = int(main.params['SLEEP']['timeout'])
        main.startUpSleep = int(main.params['SLEEP']['startup'])
        main.installSleep = int(main.params['SLEEP']['install'])
        main.verifySleep = int(main.params['SLEEP']['verify'])
        main.setMasterSleep = int(main.params['SLEEP']['setmaster'])
        main.verifyAttempts = int(main.params['ATTEMPTS']['verify'])
        main.maxInvalidRun = int(main.params['ATTEMPTS']['maxInvalidRun'])
        main.sampleSize = int(main.params['TEST']['sampleSize'])
        main.warmUp = int(main.params['TEST']['warmUp'])
        main.ingress = main.params['TEST']['ingress']
        main.egress = main.params['TEST']['egress']
        main.debug = main.params['TEST']['debug']
        main.flowObj = main.params['TEST']['flowObj']
        main.deviceCount = int(main.params['TEST']['deviceCount'])
        main.end1 = main.params['TEST']['end1']
        main.end2 = main.params['TEST']['end2']
        main.searchTerm = main.params['SEARCHTERM']
        if main.flowObj == "True":
            main.flowObj = True
            main.dbFileName = main.params['DATABASE']['dbFlowObj']
            main.intentsList = (main.params['TEST']['FObjintents']).split(",")
        else:
            main.flowObj = False
            main.dbFileName = main.params['DATABASE']['dbName']
            main.intentsList = (main.params['TEST']['intents']).split(",")

        for i in range(0, len(main.intentsList)):
            main.intentsList[i] = int(main.intentsList[i])
            # Create DataBase file
        main.log.info("Create Database file " + main.dbFileName)
        resultsDB = open(main.dbFileName, "w+")
        resultsDB.close()
        file1 = main.params[ "DEPENDENCY" ][ "FILE1" ]
        main.dependencyPath = os.path.dirname( os.getcwd() ) + main.params[ "DEPENDENCY" ][ "PATH" ]
        main.intentRerouteLatFuncs = imp.load_source(file1, main.dependencyPath + file1 + ".py")

        main.record = 0

    def CASE1( self, main ):
        '''
            clean up test environment and set up
        '''
        import time

        main.log.info("Get ONOS cluster IP")
        print(main.scale)
        main.numCtrls = int(main.scale[0])
        main.ONOSip = []
        main.maxNumBatch = 0
        main.AllONOSip = main.ONOSbench.getOnosIps()
        for i in range(main.numCtrls):
            main.ONOSip.append(main.AllONOSip[i])
        main.log.info(main.ONOSip)
        main.CLIs = []
        main.log.info("Creating list of ONOS cli handles")
        for i in range(main.numCtrls):
            main.CLIs.append(getattr(main, 'ONOS%scli' % (i + 1)))

        if not main.CLIs:
            main.log.error("Failed to create the list of ONOS cli handles")
            main.cleanup()
            main.exit()

        main.commit = main.ONOSbench.getVersion(report=True)
        main.commit = main.commit.split(" ")[1]
        main.log.info("Starting up %s node(s) ONOS cluster" % main.numCtrls)
        main.log.info("Safety check, killing all ONOS processes" +
                      " before initiating environment setup")

        for i in range(main.numCtrls):
            main.ONOSbench.onosStop(main.ONOSip[i])
            main.ONOSbench.onosKill(main.ONOSip[i])

        main.log.info("NODE COUNT = %s" % main.numCtrls)
        main.ONOSbench.createCellFile(main.ONOSbench.ip_address,
                                      main.cellName,
                                      main.MN1Ip,
                                      main.apps,
                                      main.ONOSip,
                                      main.ONOScli1.user_name)
        main.step("Apply cell to environment")
        cellResult = main.ONOSbench.setCell(main.cellName)
        verifyResult = main.ONOSbench.verifyCell()
        stepResult = cellResult and verifyResult
        utilities.assert_equals(expect=main.TRUE,
                                actual=stepResult,
                                onpass="Successfully applied cell to " + \
                                       "environment",
                                onfail="Failed to apply cell to environment ")

        main.step("Creating ONOS package")
        packageResult = main.ONOSbench.buckBuild()
        stepResult = packageResult
        utilities.assert_equals(expect=main.TRUE,
                                actual=stepResult,
                                onpass="Successfully created ONOS package",
                                onfail="Failed to create ONOS package")

        main.step("Uninstall ONOS package on all Nodes")
        uninstallResult = main.TRUE
        for i in range(int(main.numCtrls)):
            main.log.info("Uninstalling package on ONOS Node IP: " + main.ONOSip[i])
            u_result = main.ONOSbench.onosUninstall(main.ONOSip[i])
            utilities.assert_equals(expect=main.TRUE, actual=u_result,
                                    onpass="Test step PASS",
                                    onfail="Test step FAIL")
            uninstallResult = (uninstallResult and u_result)

        main.step("Install ONOS package on all Nodes")
        installResult = main.TRUE
        for i in range(int(main.numCtrls)):
            main.log.info("Installing package on ONOS Node IP: " + main.ONOSip[i])
            i_result = main.ONOSbench.onosInstall(node=main.ONOSip[i])
            utilities.assert_equals(expect=main.TRUE, actual=i_result,
                                    onpass="Test step PASS",
                                    onfail="Test step FAIL")
            installResult = installResult and i_result

        main.step( "Set up ONOS secure SSH" )
        secureSshResult = main.TRUE
        for i in range( int( main.numCtrls ) ):
            secureSshResult = secureSshResult and main.ONOSbench.onosSecureSSH( node=main.ONOSip[i] )
            utilities.assert_equals( expect=main.TRUE, actual=secureSshResult,
                                    onpass="Test step PASS",
                                    onfail="Test step FAIL" )

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
        utilities.assert_equals( expect=main.TRUE, actual=stepResult,
                                 onpass="Test step PASS",
                                 onfail="Test step FAIL" )

        time.sleep(main.startUpSleep)
        main.step("Start ONOS CLI on all nodes")
        cliResult = main.TRUE
        main.step(" Start ONOS cli using thread ")
        startCliResult = main.TRUE
        pool = []
        main.threadID = 0
        for i in range(int(main.numCtrls)):
            t = main.Thread(target=main.CLIs[i].startOnosCli,
                            threadID=main.threadID,
                            name="startOnosCli",
                            args=[main.ONOSip[i]],
                            kwargs={"onosStartTimeout": main.timeout})
            pool.append(t)
            t.start()
            main.threadID = main.threadID + 1
        for t in pool:
            t.join()
            startCliResult = startCliResult and t.result
        time.sleep(main.startUpSleep)

        # configure apps
        main.CLIs[0].setCfg("org.onosproject.provider.nil.NullProviders", "deviceCount", value=main.deviceCount)
        main.CLIs[0].setCfg("org.onosproject.provider.nil.NullProviders", "topoShape", value="reroute")
        main.CLIs[0].setCfg("org.onosproject.provider.nil.NullProviders", "enabled", value="true")
        if main.flowObj:
            main.CLIs[0].setCfg("org.onosproject.net.intent.impl.compiler.IntentConfigurableRegistrator",
                                "useFlowObjectives", value="true")
            main.CLIs[0].setCfg("org.onosproject.net.intent.impl.compiler.IntentConfigurableRegistrator",
                                "defaultFlowObjectiveCompiler",
                                value='org.onosproject.net.intent.impl.compiler.LinkCollectionIntentObjectiveCompiler')
        time.sleep( main.startUpSleep )
        for i in range( int( main.numCtrls ) ):
            main.CLIs[i].logSet( "DEBUG", "org.onosproject.metrics.topology" )
            main.CLIs[i].logSet( "DEBUG", "org.onosproject.metrics.intent" )
        # Balance Master
        main.CLIs[0].balanceMasters()
        time.sleep( main.setMasterSleep )
        if len(main.ONOSip) > 1:
            main.CLIs[0].deviceRole(main.end1[ 'name' ], main.ONOSip[0])
            main.CLIs[0].deviceRole(main.end2[ 'name' ], main.ONOSip[0])
        time.sleep( main.setMasterSleep )

    def CASE2( self, main ):
        import time
        import numpy
        import datetime
        import json
        # from scipy import stats

        print(main.intentsList)
        for batchSize in main.intentsList:
            main.batchSize = batchSize
            main.log.report("Intent Batch size: " + str(batchSize) + "\n      ")
            firstLocalLatencies = []
            lastLocalLatencies = []
            firstGlobalLatencies = []
            lastGlobalLatencies = []
            main.startLine = {}
            main.validRun = 0
            main.invalidRun = 0
            while main.validRun <= main.warmUp + main.sampleSize and main.invalidRun <= main.maxInvalidRun:
                if main.validRun >= main.warmUp:
                    main.log.info("================================================")
                    main.log.info("Valid iteration: {} ".format( main.validRun - main.warmUp))
                    main.log.info("Total iteration: {}".format( main.validRun + main.invalidRun))
                    main.log.info("================================================")
                else:
                    main.log.info("====================Warm Up=====================")

                # push intents
                main.CLIs[0].pushTestIntents(main.ingress, main.egress, main.batchSize,
                                             offset=1, options="-i", timeout=main.timeout)

                # check links, flows and intents
                main.intentRerouteLatFuncs.sanityCheck( main, main.deviceCount * 2, batchSize * (main.deviceCount - 1 ), main.batchSize )
                if not main.verify:
                    main.log.warn( "Sanity check failed, skipping this iteration..." )
                    continue

                # Insert one line in karaf.log before link down
                for i in range( main.numCtrls ):
                    main.CLIs[ i ].log( "\'Scale: {}, Batch:{}, Iteration: {}\'".format( main.numCtrls, batchSize, main.validRun + main.invalidRun ) )

                # bring link down
                main.CLIs[0].link( main.end1[ 'port' ], main.end2[ 'port' ], "down",
                                  timeout=main.timeout, showResponse=False)

                # check links, flows and intents
                main.intentRerouteLatFuncs.sanityCheck( main, (main.deviceCount - 1) * 2, batchSize * main.deviceCount, main.batchSize )
                if not main.verify:
                    main.log.warn( "Sanity check failed, skipping this iteration..." )
                    continue

                # Get timestamp of last LINK_REMOVED event as separator between iterations
                skip = False
                for i in range( main.numCtrls ):
                    logNum = main.intentRerouteLatFuncs.getLogNum( main, i )
                    timestamp = str( main.CLIs[ i ].getTimeStampFromLog( "last", "LINK_REMOVED", "time = ", " ", logNum=logNum ) )
                    if timestamp == main.ERROR:
                        # Try again in case that the log number just increased
                        logNum = main.intentRerouteLatFuncs.getLogNum( main, i )
                        timestamp = str( main.CLIs[ i ].getTimeStampFromLog( "last", "LINK_REMOVED", "time = ", " ", logNum=logNum ) )
                    if timestamp == main.ERROR:
                        main.log.warn( "Cannot find the event we want in the log, skipping this iteration..." )
                        main.intentRerouteLatFuncs.bringBackTopology( main )
                        if main.validRun >= main.warmUp:
                            main.invalidRun += 1
                        else:
                            main.validRun += 1
                        skip = True
                        break
                    else:
                        main.startLine[ i ] = timestamp
                        main.log.info( "Timestamp of last LINK_REMOVED event on node {} is {}".format( i+1, main.startLine[ i ] ) )
                if skip: continue

                # calculate values
                topologyTimestamps = main.intentRerouteLatFuncs.getTopologyTimestamps( main )
                intentTimestamps = main.intentRerouteLatFuncs.getIntentTimestamps( main )
                if intentTimestamps == main.ERROR or topologyTimestamps == main.ERROR:
                    main.log.info( "Got invalid timestamp, skipping this iteration..." )
                    main.intentRerouteLatFuncs.bringBackTopology( main )
                    if main.validRun >= main.warmUp:
                        main.invalidRun += 1
                    else:
                        main.validRun += 1
                    continue
                else:
                    main.log.info( "Got valid timestamps" )

                firstLocalLatnecy, lastLocalLatnecy, firstGlobalLatency, lastGlobalLatnecy = main.intentRerouteLatFuncs.calculateLatency( main, topologyTimestamps, intentTimestamps )
                if firstLocalLatnecy < 0:
                    main.log.info( "Got negative latency, skipping this iteration..." )
                    main.intentRerouteLatFuncs.bringBackTopology( main )
                    if main.validRun >= main.warmUp:
                        main.invalidRun += 1
                    else:
                        main.validRun += 1
                    continue
                else:
                    main.log.info( "Got valid latencies" )
                    main.validRun += 1

                firstLocalLatencies.append( firstLocalLatnecy )
                lastLocalLatencies.append( lastLocalLatnecy )
                firstGlobalLatencies.append( firstGlobalLatency )
                lastGlobalLatencies.append( lastGlobalLatnecy )

                # bring up link and withdraw intents
                main.CLIs[0].link( main.end1[ 'port' ], main.end2[ 'port' ], "up",
                                  timeout=main.timeout)
                main.CLIs[0].pushTestIntents(main.ingress, main.egress, batchSize,
                                             offset=1, options="-w", timeout=main.timeout)
                main.CLIs[0].purgeWithdrawnIntents()

                # check links, flows and intents
                main.intentRerouteLatFuncs.sanityCheck( main, main.deviceCount * 2, 0, 0 )
                if not main.verify:
                    continue

            aveLocalLatency = numpy.average( lastLocalLatencies )
            aveGlobalLatency = numpy.average( lastGlobalLatencies )
            stdLocalLatency = numpy.std( lastLocalLatencies )
            stdGlobalLatency = numpy.std( lastGlobalLatencies )

            main.log.report( "Scale: " + str( main.numCtrls ) + "  \tIntent batch: " + str( batchSize ) )
            main.log.report( "Local latency average:................" + str( aveLocalLatency ) )
            main.log.report( "Global latency average:................" + str( aveGlobalLatency ) )
            main.log.report( "Local latency std:................" + str( stdLocalLatency ) )
            main.log.report( "Global latency std:................" + str( stdGlobalLatency ) )
            main.log.report( "________________________________________________________" )

            if not ( numpy.isnan( aveLocalLatency ) or numpy.isnan( aveGlobalLatency ) ):
                # check if got NaN for result
                resultsDB = open( main.dbFileName, "a" )
                resultsDB.write( "'" + main.commit + "'," )
                resultsDB.write( str( main.numCtrls ) + "," )
                resultsDB.write( str( batchSize ) + "," )
                resultsDB.write( str( aveLocalLatency ) + "," )
                resultsDB.write( str( stdLocalLatency ) + "\n" )
                resultsDB.close()
        del main.scale[ 0 ]
