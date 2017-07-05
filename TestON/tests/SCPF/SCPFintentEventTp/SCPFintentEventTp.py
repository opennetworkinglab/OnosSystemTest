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
        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
            main.testSetUp = ONOSSetup()
        except ImportError:
            main.log.error( "ONOSSetup not found. exiting the test" )
            main.exit()
        main.testSetUp.envSetupDescription()
        stepResult = main.FALSE
        try:
            main.cellName = main.params[ 'ENV'][ 'cellName']
            main.apps = main.params[ 'ENV' ][ 'cellApps' ]
            main.BENCHIp = main.params[ 'BENCH' ][ 'ip1' ]
            main.BENCHUser = main.params[ 'BENCH' ][ 'user' ]
            main.MN1Ip = main.params[ 'MN' ][ 'ip1' ]
            main.maxNodes = int( main.params[ 'max' ] )
            main.numSwitches = ( main.params[ 'TEST' ][ 'numSwitches' ] ).split(",")
            main.skipRelRsrc = main.params[ 'TEST' ][ 'skipReleaseResourcesOnWithdrawal' ]
            main.flowObj = main.params[ 'TEST' ][ 'flowObj' ]
            main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
            main.installSleep = int( main.params[ 'SLEEP' ][ 'install' ] )
            main.verifySleep = int( main.params[ 'SLEEP' ][ 'verify' ] )
            main.scale = ( main.params[ 'SCALE' ] ).split(",")
            main.testDuration = main.params[ 'TEST' ][ 'duration' ]
            main.logInterval = main.params[ 'TEST' ][ 'log_interval' ]
            main.debug = main.params[ 'debugMode' ]
            main.timeout = int( main.params[ 'SLEEP' ][ 'timeout' ] )
            main.cyclePeriod = main.params[ 'TEST' ][ 'cyclePeriod' ]
            if main.flowObj == "True":
                main.flowObj = True
                main.dbFileName = main.params[ 'DATABASE' ][ 'dbFlowObj' ]
                main.numKeys = main.params[ 'TEST' ][ 'numKeysFlowObj' ]
            else:
                main.flowObj = False
                main.dbFileName = main.params[ 'DATABASE' ][ 'dbName' ]
                main.numKeys = main.params[ 'TEST' ][ 'numKeys' ]

            stepResult = main.testSetUp.gitPulling()
            # Create DataBase file
            main.log.info( "Create Database file " + main.dbFileName )
            resultsDB = open( main.dbFileName, "w+" )
            resultsDB.close()

            # set neighbors
            main.neighbors = "1"
        except Exception as e:
            main.testSetUp.envSetupException( e )
        main.testSetUp.evnSetupConclusion( stepResult )
        main.commit = main.commit.split( " " )[ 1 ]

    def CASE1( self, main ):
        # Clean up test environment and set up
        import time
        main.maxNumBatch = 0
        main.testSetUp.getNumCtrls( True )
        main.testSetUp.envSetup( includeGitPull=False, makeMaxNodes=False )
        main.testSetUp.ONOSSetUp( main.MN1Ip, True,
                                  cellName=main.cellName, killRemoveMax=False,
                                  CtrlsSet=False )

        # config apps
        main.CLIs[0].setCfg( "org.onosproject.net.intent.impl.IntentManager",
                                  "skipReleaseResourcesOnWithdrawal " + main.skipRelRsrc )
        main.CLIs[0].setCfg( "org.onosproject.provider.nil.NullProviders", "deviceCount " + str(int( main.numCtrls*10)) )
        main.CLIs[0].setCfg( "org.onosproject.provider.nil.NullProviders", "topoShape linear" )
        main.CLIs[0].setCfg( "org.onosproject.provider.nil.NullProviders", "enabled true" )
        if main.flowObj:
            main.CLIs[0].setCfg("org.onosproject.net.intent.impl.compiler.IntentConfigurableRegistrator",
                                "useFlowObjectives", value="true")
            main.CLIs[0].setCfg("org.onosproject.net.intent.impl.compiler.IntentConfigurableRegistrator",
                                "defaultFlowObjectiveCompiler",
                                value='org.onosproject.net.intent.impl.compiler.LinkCollectionIntentObjectiveCompiler')
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

        main.log.info( "Starting intent-perf test for " + str( main.testDuration) + " seconds..." )
        main.CLIs[0].sendline( "intent-perf-start" )
        stop = time.time() + float( main.testDuration )

        while time.time() < stop:
            time.sleep(15)
            result = main.CLIs[0].getIntentPerfSummary()
            if result:
                for i in range( main.numCtrls ):
                    main.log.info( "Node {} Overall Rate: {}".format( main.ONOSip[ i ], result[ main.ONOSip[ i ] ] ) )
        main.log.info( "Stop intent-perf" )
        for i in range( main.numCtrls ):
            main.CLIs[i].sendline( "intent-perf-stop" )
        if result:
            for i in range( main.numCtrls ):
                main.log.info( "Node {} final Overall Rate: {}".format( main.ONOSip[ i ], result[ main.ONOSip[ i ] ] ) )

        with open( main.dbFileName, "a" ) as resultDB:
            for nodes in range( main.numCtrls ):
                resultString = "'" + main.commit + "',"
                resultString += "'1gig',"
                resultString += str( main.numCtrls) + ","
                resultString += "'baremetal" + str( nodes+1 ) + "',"
                resultString += main.neighbors + ","
                resultString += result[ main.ONOSip[ nodes ] ]+","
                resultString += str(0) + "\n"  # no stddev
                resultDB.write( resultString )
        resultDB.close()
