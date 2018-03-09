"""
Copyright 2015 Open Networking Foundation ( ONF )

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    ( at your option ) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.
"""
# SCPFintentRerouteLat
"""
SCPFintentRerouteLat
    - Test Intent Reroute Latency
    - Test Algorithm:
        1. Start Null Provider reroute Topology
        2. Using Push-test-intents to push batch size intents from switch 1 to switch 7
        3. Cut the link between switch 3 and switch 4 ( the path will reroute to switch 8 )
        4. Get the topology time stamp
        5. Get Intent reroute( Installed ) time stamp from each nodes
        6. Use the latest intent time stamp subtract topology time stamp
    - This test will run 5 warm up by default, warm up iteration can be setup in Param file
    - The intent batch size will default set to 1, 100, and 1000, also can be set in Param file
    - The unit of the latency result is milliseconds
"""
class SCPFintentRerouteLat:

    def __init__( self ):
        self.default = ''

    def CASE0( self, main ):
        import imp
        import os
        """
        - GIT
        - BUILDING ONOS
            Pull specific ONOS branch, then Build ONOS ono ONOS Bench.
            This step is usually skipped. Because in a Jenkins driven automated
            test env. We want Jenkins jobs to pull&build for flexibility to handle
            different versions of ONOS.
        - Construct tests variables
        """
        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
            main.testSetUp = ONOSSetup()
        except ImportError:
            main.log.error( "ONOSSetup not found. exiting the test" )
            main.cleanAndExit()
        main.testSetUp.envSetupDescription()
        stepResult = main.FALSE
        try:
            main.apps = main.params[ 'ENV' ][ 'cellApps' ]
            main.BENCHUser = main.params[ 'BENCH' ][ 'user' ]
            main.BENCHIp = main.params[ 'BENCH' ][ 'ip1' ]
            main.MN1Ip = main.params[ 'MN' ][ 'ip1' ]
            main.cellName = main.params[ 'ENV' ][ 'cellName' ]
            main.scale = ( main.params[ 'SCALE' ] ).split( "," )
            main.timeout = int( main.params[ 'SLEEP' ][ 'timeout' ] )
            main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
            main.installSleep = int( main.params[ 'SLEEP' ][ 'install' ] )
            main.verifySleep = int( main.params[ 'SLEEP' ][ 'verify' ] )
            main.setMasterSleep = int( main.params[ 'SLEEP' ][ 'setmaster' ] )
            main.verifyAttempts = int( main.params[ 'ATTEMPTS' ][ 'verify' ] )
            main.maxInvalidRun = int( main.params[ 'ATTEMPTS' ][ 'maxInvalidRun' ] )
            main.cfgRetry = int( main.params[ 'ATTEMPTS' ][ 'cfg' ] )
            main.sampleSize = int( main.params[ 'TEST' ][ 'sampleSize' ] )
            main.intentManagerCfg = main.params[ 'CFG' ][ 'intentManager' ]
            main.intentConfigRegiCfg = main.params[ 'CFG' ][ 'intentConfigRegi' ]
            main.nullProviderCfg = main.params[ 'CFG' ][ 'nullProvider' ]
            main.warmUp = int( main.params[ 'TEST' ][ 'warmUp' ] )
            main.ingress = main.params[ 'TEST' ][ 'ingress' ]
            main.egress = main.params[ 'TEST' ][ 'egress' ]
            main.debug = main.params[ 'TEST' ][ 'debug' ]
            main.flowObj = main.params[ 'TEST' ][ 'flowObj' ]
            main.deviceCount = int( main.params[ 'TEST' ][ 'deviceCount' ] )
            main.end1 = main.params[ 'TEST' ][ 'end1' ]
            main.end2 = main.params[ 'TEST' ][ 'end2' ]
            main.searchTerm = main.params[ 'SEARCHTERM' ]
            if main.flowObj == "True":
                main.flowObj = True
                main.dbFileName = main.params[ 'DATABASE' ][ 'dbFlowObj' ]
                main.intentsList = ( main.params[ 'TEST' ][ 'FObjintents' ] ).split( "," )
            else:
                main.flowObj = False
                main.dbFileName = main.params[ 'DATABASE' ][ 'dbName' ]
                main.intentsList = ( main.params[ 'TEST' ][ 'intents' ] ).split( "," )

            stepResult = main.testSetUp.envSetup()

            for i in range( 0, len( main.intentsList ) ):
                main.intentsList[ i ] = int( main.intentsList[ i ] )
                # Create DataBase file
            main.log.info( "Create Database file " + main.dbFileName )
            resultsDB = open( main.dbFileName, "w+" )
            resultsDB.close()
            file1 = main.params[ "DEPENDENCY" ][ "FILE1" ]
            main.dependencyPath = os.path.dirname( os.getcwd() ) + main.params[ "DEPENDENCY" ][ "PATH" ]
            main.intentRerouteLatFuncs = imp.load_source( file1, main.dependencyPath + file1 + ".py" )

            main.record = 0
        except Exception as e:
            main.testSetUp.envSetupException( e )
        main.testSetUp.evnSetupConclusion( stepResult )
        main.commit = main.commit.split( " " )[ 1 ]

    def CASE1( self, main ):
        """
            clean up test environment and set up
        """
        import time

        main.maxNumBatch = 0
        main.testSetUp.ONOSSetUp( main.Cluster, True,
                                  cellName=main.cellName, killRemoveMax=False )
        configRetry = 0
        main.cfgCheck = False
        while configRetry < main.cfgRetry:
            # configure apps
            stepResult = main.TRUE
            stepResult = stepResult and \
                         main.Cluster.active( 0 ).CLI.setCfg( main.nullProviderCfg,
                                                              "deviceCount",
                                                              value=main.deviceCount )

            stepResult = stepResult and \
                         main.Cluster.active( 0 ).CLI.setCfg( main.nullProviderCfg,
                                                              "topoShape",
                                                              value="reroute" )
            stepResult = stepResult and \
                         main.Cluster.active( 0 ).CLI.setCfg( main.nullProviderCfg,
                                                              "enabled",
                                                              value="true" )

            stepResult = stepResult and \
                         main.Cluster.active( 0 ).CLI.setCfg( main.intentManagerCfg,
                                                              "skipReleaseResourcesOnWithdrawal",
                                                              value="true" )
            if main.flowObj:
                stepResult = stepResult and \
                             main.Cluster.active( 0 ).CLI.setCfg( main.intentConfigRegiCfg,
                                                                  "useFlowObjectives",
                                                                  value="true" )
            if stepResult:
                main.cfgCheck = True
                break
            configRetry += 1
            time.sleep( main.verifySleep )

        time.sleep( main.startUpSleep )
        for ctrl in main.Cluster.active():
            ctrl.CLI.logSet( "DEBUG", "org.onosproject.metrics.topology" )
            ctrl.CLI.logSet( "DEBUG", "org.onosproject.metrics.intent" )
        # Balance Master
        main.Cluster.active( 0 ).CLI.balanceMasters()
        time.sleep( main.setMasterSleep )
        if main.Cluster.numCtrls:
            main.Cluster.active( 0 ).CLI.deviceRole( main.end1[ 'name' ], main.Cluster.active( 0 ).ipAddress )
            main.Cluster.active( 0 ).CLI.deviceRole( main.end2[ 'name' ], main.Cluster.active( 0 ).ipAddress )
        time.sleep( main.setMasterSleep )
        if not main.cfgCheck:
            main.log.error( "Setting configuration to the ONOS failed. Skip the rest of the steps" )

    def CASE2( self, main ):
        import time
        import numpy
        import datetime
        import json
        # from scipy import stats
        testResult = main.TRUE
        main.case( "Intent Reroute starts" )
        main.step( "Checking intent reroute" )
        if main.cfgCheck:
            print( main.intentsList )
            for batchSize in main.intentsList:
                main.batchSize = batchSize
                main.log.report( "Intent Batch size: " + str( batchSize ) + "\n      " )
                firstLocalLatencies = []
                lastLocalLatencies = []
                firstGlobalLatencies = []
                lastGlobalLatencies = []
                main.startLine = {}
                main.validRun = 0
                main.invalidRun = 0
                while main.validRun <= main.warmUp + main.sampleSize and main.invalidRun <= main.maxInvalidRun:
                    if main.validRun >= main.warmUp:
                        main.log.info( "================================================" )
                        main.log.info( "Valid iteration: {} ".format( main.validRun - main.warmUp ) )
                        main.log.info( "Total iteration: {}".format( main.validRun + main.invalidRun ) )
                        main.log.info( "================================================" )
                    else:
                        main.log.info( "====================Warm Up=====================" )

                    # push intents
                    main.Cluster.active( 0 ).CLI.pushTestIntents( main.ingress,
                                                                  main.egress,
                                                                  main.batchSize,
                                                                  offset=1,
                                                                  options="-i",
                                                                  timeout=main.timeout )

                    # check links, flows and intents
                    main.intentRerouteLatFuncs.sanityCheck( main,
                                                            main.deviceCount * 2,
                                                            batchSize * ( main.deviceCount - 1 ),
                                                            main.batchSize )
                    if not main.verify:
                        main.log.warn( "Sanity check failed, skipping this iteration..." )
                        continue

                    # Insert one line in karaf.log before link down
                    main.Cluster.command( "log",
                                          args=[ "\'Scale: {}, Batch:{}, Iteration: {}\'".format(
                                              main.Cluster.numCtrls, batchSize, main.validRun + main.invalidRun ) ],
                                          returnBool=True, specificDriver=2 )
                    # bring link down
                    main.Cluster.active( 0 ).CLI.link( main.end1[ 'port' ], main.end2[ 'port' ], "down",
                                                       timeout=main.timeout, showResponse=False )

                    # check links, flows and intents
                    main.intentRerouteLatFuncs.sanityCheck( main,
                                                            ( main.deviceCount - 1 ) * 2,
                                                            batchSize * main.deviceCount,
                                                            main.batchSize )
                    if not main.verify:
                        main.log.warn( "Sanity check failed, skipping this iteration..." )
                        continue

                    # Get timestamp of last LINK_REMOVED event as separator between iterations
                    skip = False
                    for i in range( main.Cluster.numCtrls ):
                        logNum = main.intentRerouteLatFuncs.getLogNum( main, i )
                        timestamp = str( main.Cluster.active( i ).CLI.getTimeStampFromLog( "last",
                                                                                           "LINK_REMOVED",
                                                                                           "time = ", " ",
                                                                                           logNum=logNum ) )
                        if timestamp == main.ERROR:
                            # Try again in case that the log number just increased
                            logNum = main.intentRerouteLatFuncs.getLogNum( main, i )
                            timestamp = str( main.Cluster.active( i ).CLI.getTimeStampFromLog( "last",
                                                                                               "LINK_REMOVED",
                                                                                               "time = ", " ",
                                                                                               logNum=logNum ) )
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
                            main.log.info( "Timestamp of last LINK_REMOVED event on node {} is {}".format( i + 1,
                                                                                                           main.startLine[ i ] ) )
                    if skip:
                        continue

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

                    firstLocalLatnecy, lastLocalLatnecy, firstGlobalLatency, lastGlobalLatnecy \
                        = main.intentRerouteLatFuncs.calculateLatency( main, topologyTimestamps, intentTimestamps )
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

                    if main.validRun >= main.warmUp:
                        firstLocalLatencies.append( firstLocalLatnecy )
                        lastLocalLatencies.append( lastLocalLatnecy )
                        firstGlobalLatencies.append( firstGlobalLatency )
                        lastGlobalLatencies.append( lastGlobalLatnecy )

                    # bring up link and withdraw intents
                    main.Cluster.active( 0 ).CLI.link( main.end1[ 'port' ],
                                                       main.end2[ 'port' ],
                                                       "up",
                                                       timeout=main.timeout )
                    main.Cluster.active( 0 ).CLI.pushTestIntents( main.ingress,
                                                                  main.egress,
                                                                  batchSize,
                                                                  offset=1,
                                                                  options="-w",
                                                                  timeout=main.timeout )
                    main.Cluster.active( 0 ).CLI.purgeWithdrawnIntents()

                    # check links, flows and intents
                    main.intentRerouteLatFuncs.sanityCheck( main, main.deviceCount * 2, 0, 0 )
                    if not main.verify:
                        main.log.warn( "Sanity check failed, skipping this iteration..." )
                        continue
                result = ( main.TRUE if main.invalidRun <= main.maxInvalidRun else main.FALSE )
                aveLocalLatency = numpy.average( lastLocalLatencies ) if lastLocalLatencies and result else 0
                aveGlobalLatency = numpy.average( lastGlobalLatencies ) if lastGlobalLatencies and result else 0
                stdLocalLatency = numpy.std( lastLocalLatencies ) if lastLocalLatencies and result else 0
                stdGlobalLatency = numpy.std( lastGlobalLatencies ) if lastGlobalLatencies and result else 0
                testResult = testResult and result

                main.log.report( "Scale: " + str( main.Cluster.numCtrls ) + "  \tIntent batch: " + str( batchSize ) )
                main.log.report( "Local latency average:................" + str( aveLocalLatency ) )
                main.log.report( "Global latency average:................" + str( aveGlobalLatency ) )
                main.log.report( "Local latency std:................" + str( stdLocalLatency ) )
                main.log.report( "Global latency std:................" + str( stdGlobalLatency ) )
                main.log.report( "________________________________________________________" )

                if not ( numpy.isnan( aveLocalLatency ) or numpy.isnan( aveGlobalLatency ) ):
                    # check if got NaN for result
                    resultsDB = open( main.dbFileName, "a" )
                    resultsDB.write( "'" + main.commit + "'," )
                    resultsDB.write( str( main.Cluster.numCtrls ) + "," )
                    resultsDB.write( str( batchSize ) + "," )
                    resultsDB.write( str( aveLocalLatency ) + "," )
                    resultsDB.write( str( stdLocalLatency ) + "\n" )
                    resultsDB.close()
        else:
            testResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass="Installing and withdrawing intents reroute properly",
                                 onfail="There was something wrong installing and withdrawing intents reroute" )
