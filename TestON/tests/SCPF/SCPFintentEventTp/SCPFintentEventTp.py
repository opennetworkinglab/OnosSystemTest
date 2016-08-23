'''
SCPFintentEventTp
    - Use intentperf app to generate a lot of intent install and withdraw events
    - Test will run with 1,3,5,7 nodes, and with all neighbors
    - Test will run 400 seconds and grep the overall rate from intent-perf summary

    yunpeng@onlab.us
'''

import time


class SCPFintentEventTp:
    def __init__( self ):
        self.default = ''

    def CASE0( self, main ):
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

        main.case( "Pull onos branch and build onos on Teststation." )

        if gitPull == 'True':
            main.step( "Git Checkout ONOS branch: " + gitBranch )
            stepResult = main.ONOSbench.gitCheckout( branch=gitBranch )
            utilities.assert_equals(expect=main.TRUE,
                                    actual=stepResult,
                                    onpass="Successfully checkout onos branch.",
                                    onfail="Failed to checkout onos branch. Exiting test...")
            if not stepResult: main.exit()

            main.step( "Git Pull on ONOS branch:" + gitBranch )
            stepResult = main.ONOSbench.gitPull()
            utilities.assert_equals(expect=main.TRUE,
                                    actual=stepResult,
                                    onpass="Successfully pull onos. ",
                                    onfail="Failed to pull onos. Exiting test ...")
            if not stepResult: main.exit()

            main.step( "Building ONOS branch: " + gitBranch )
            stepResult = main.ONOSbench.cleanInstall( skipTest=True )
            utilities.assert_equals(expect=main.TRUE,
                                    actual=stepResult,
                                    onpass="Successfully build onos.",
                                    onfail="Failed to build onos. Exiting test...")
            if not stepResult: main.exit()

        else:
            main.log.warn( "Skipped pulling onos and Skipped building ONOS" )

        main.cellName = main.params['ENV']['cellName']
        main.Apps = main.params['ENV']['cellApps']
        main.BENCHIp = main.params['BENCH']['ip1']
        main.BENCHUser = main.params['BENCH']['user']
        main.MN1Ip = main.params['MN']['ip1']
        main.maxNodes = int(main.params['max'])
        main.numSwitches = (main.params['TEST']['numSwitches']).split(",")
        main.flowRuleBU = main.params['TEST']['flowRuleBUEnabled']
        main.skipRelRsrc = main.params['TEST']['skipReleaseResourcesOnWithdrawal']
        main.flowObj = main.params['TEST']['flowObj']
        main.startUpSleep = int(main.params['SLEEP']['startup'])
        main.installSleep = int(main.params['SLEEP']['install'])
        main.verifySleep = int(main.params['SLEEP']['verify'])
        main.scale = (main.params['SCALE']).split(",")
        main.testDuration = main.params[ 'TEST' ][ 'duration' ]
        main.logInterval = main.params[ 'TEST' ][ 'log_interval' ]
        main.debug = main.params[ 'debugMode' ]
        main.numKeys = main.params[ 'TEST' ][ 'numKeys' ]
        main.timeout = int(main.params['SLEEP']['timeout'])
        main.cyclePeriod = main.params[ 'TEST' ][ 'cyclePeriod' ]
        if main.flowObj == "True":
            main.flowObj = True
            main.dbFileName = main.params['DATABASE']['dbFlowObj']
        else:
            main.flowObj = False
            main.dbFileName = main.params['DATABASE']['dbName']
        # Create DataBase file
        main.log.info( "Create Database file " + main.dbFileName )
        resultsDB = open( main.dbFileName, "w+" )
        resultsDB.close()

        # set neighbors
        main.neighbors = "1"

    def CASE1( self, main ):
        # Clean up test environment and set up
        import time
        main.log.info( "Get ONOS cluster IP" )
        print( main.scale )
        main.numCtrls = int( main.scale.pop(0) )
        main.ONOSip = []
        main.maxNumBatch = 0
        main.AllONOSip = main.ONOSbench.getOnosIps()
        for i in range( main.numCtrls ):
            main.ONOSip.append( main.AllONOSip[i] )
        main.log.info( main.ONOSip )
        main.CLIs = []
        main.log.info( "Creating list of ONOS cli handles" )
        for i in range( main.numCtrls ):
            main.CLIs.append( getattr( main, 'ONOS%scli' % (i + 1) ) )

        if not main.CLIs:
            main.log.error( "Failed to create the list of ONOS cli handles" )
            main.cleanup()
            main.exit()

        main.commit = main.ONOSbench.getVersion( report=True )
        main.commit = main.commit.split(" ")[1]
        main.log.info( "Starting up %s node(s) ONOS cluster" % main.numCtrls )
        main.log.info("Safety check, killing all ONOS processes" +
                      " before initiating environment setup")

        for i in range( main.numCtrls ):
            main.ONOSbench.onosDie( main.ONOSip[i] )

        main.log.info( "NODE COUNT = %s" % main.numCtrls )
        main.ONOSbench.createCellFile(main.ONOSbench.ip_address,
                                      main.cellName,
                                      main.MN1Ip,
                                      main.Apps,
                                      main.ONOSip)
        main.step( "Apply cell to environment" )
        cellResult = main.ONOSbench.setCell( main.cellName )
        verifyResult = main.ONOSbench.verifyCell()
        stepResult = cellResult and verifyResult
        utilities.assert_equals(expect=main.TRUE,
                                actual=stepResult,
                                onpass="Successfully applied cell to " + \
                                       "environment",
                                onfail="Failed to apply cell to environment ")

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.buckBuild()
        stepResult = packageResult
        utilities.assert_equals(expect=main.TRUE,
                                actual=stepResult,
                                onpass="Successfully created ONOS package",
                                onfail="Failed to create ONOS package")

        main.step( "Uninstall ONOS package on all Nodes" )
        uninstallResult = main.TRUE
        for i in range( int( main.numCtrls ) ):
            main.log.info( "Uninstalling package on ONOS Node IP: " + main.ONOSip[i] )
            u_result = main.ONOSbench.onosUninstall( main.ONOSip[i] )
            utilities.assert_equals(expect=main.TRUE, actual=u_result,
                                    onpass="Test step PASS",
                                    onfail="Test step FAIL")
            uninstallResult = ( uninstallResult and u_result )

        main.step( "Install ONOS package on all Nodes" )
        installResult = main.TRUE
        for i in range( int( main.numCtrls ) ):
            main.log.info( "Installing package on ONOS Node IP: " + main.ONOSip[i] )
            i_result = main.ONOSbench.onosInstall(node=main.ONOSip[i])
            utilities.assert_equals(expect=main.TRUE, actual=i_result,
                                    onpass="Test step PASS",
                                    onfail="Test step FAIL")
            installResult = installResult and i_result

        main.step( "Verify ONOS nodes UP status" )
        statusResult = main.TRUE
        for i in range( int( main.numCtrls ) ):
            main.log.info( "ONOS Node " + main.ONOSip[i] + " status:" )
            onos_status = main.ONOSbench.onosStatus(node=main.ONOSip[i])
            utilities.assert_equals(expect=main.TRUE, actual=onos_status,
                                    onpass="Test step PASS",
                                    onfail="Test step FAIL")
            statusResult = (statusResult and onos_status)
        time.sleep(2)
        main.step( "Start ONOS cli using thread" )
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
        time.sleep( main.startUpSleep )

        # config apps
        main.CLIs[0].setCfg( "org.onosproject.store.flow.impl.DistributedFlowRuleStore",
                            "backupEnabled " + main.flowRuleBU )
        main.CLIs[0].setCfg( "org.onosproject.net.intent.impl.IntentManager",
                                  "skipReleaseResourcesOnWithdrawal " + main.skipRelRsrc )
        main.CLIs[0].setCfg( "org.onosproject.provider.nil.NullProviders", "deviceCount " + str(int(main.numCtrls*10)) )
        main.CLIs[0].setCfg( "org.onosproject.provider.nil.NullProviders", "topoShape linear" )
        main.CLIs[0].setCfg( "org.onosproject.provider.nil.NullProviders", "enabled true" )
        if main.flowObj:
            main.CLIs[0].setCfg("org.onosproject.net.intent.impl.compiler.IntentConfigurableRegistrator",
                                "useFlowObjectives", value="true")
        time.sleep( main.startUpSleep )

        # balanceMasters
        main.CLIs[0].balanceMasters()
        time.sleep( main.startUpSleep )

    def CASE2(self, main):
        import numpy

        main.log.info( "Cluster Count = " + str( main.numCtrls ) )
        # adjust neighbors
        if main.numCtrls == 1:
            main.neighbors = "0"
            main.log.info( "Neighbors: 0" )
        elif main.neighbors != "0":
            main.neighbors = "0"
            main.log.info( "Neighbors: 0" )
        elif main.neighbors == "0":
            main.neighbors = str( main.numCtrls - 1 )
            main.log.info( "Neighbors: " + main.neighbors )

        main.log.info( "Config intent-perf app" )
        main.CLIs[0].setCfg( "org.onosproject.intentperf.IntentPerfInstaller", "numKeys " + main.numKeys )
        main.CLIs[0].setCfg( "org.onosproject.intentperf.IntentPerfInstaller", "numNeighbors " + str( main.neighbors ) )
        main.CLIs[0].setCfg( "org.onosproject.intentperf.IntentPerfInstaller", "cyclePeriod " + main.cyclePeriod )

        main.log.info( "Starting intent-perf test for " + str(main.testDuration) + " seconds..." )
        main.CLIs[0].sendline( "intent-perf-start" )
        stop = time.time() + float( main.testDuration )

        while time.time() < stop:
            time.sleep(15)
            result = main.CLIs[0].getIntentPerfSummary()
            if result:
                for ip in main.ONOSip:
                    main.log.info( "Node {} Overall Rate: {}".format( ip, result[ip] ) )
        main.log.info( "Stop intent-perf" )
        for node in main.CLIs:
            node.sendline( "intent-perf-stop" )
        if result:
            for ip in main.ONOSip:
                main.log.info( "Node {} final Overall Rate: {}".format( ip, result[ip] ) )

        with open( main.dbFileName, "a" ) as resultDB:
            for nodes in range( 0, len( main.ONOSip ) ):
                resultString = "'" + main.commit + "',"
                resultString += "'1gig',"
                resultString += str(main.numCtrls) + ","
                resultString += "'baremetal" + str( nodes+1 ) + "',"
                resultString += main.neighbors + ","
                resultString += result[ main.ONOSip[ nodes ] ]+","
                resultString += str(0) + "\n"  # no stddev
                resultDB.write( resultString )
        resultDB.close()
