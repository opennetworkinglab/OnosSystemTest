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
"""
SCPFintentInstallWithdrawLat:
    - Test the latency of intent installed and withdrawn
    - Use Push-test-intents command to push intents
    - Use Null provider with 7 devices and linear topology
    - Always push intents between 1/6 and 7/5
    - The batch size is defined in parm file. ( default 1,100,1000 )

    yunpeng@onlab.us
"""
class SCPFintentInstallWithdrawLat:

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
            main.maxNodes = int( main.params[ 'max' ] )
            main.cellName = main.params[ 'ENV' ][ 'cellName' ]
            main.scale = ( main.params[ 'SCALE' ] ).split( "," )
            main.timeout = int( main.params[ 'SLEEP' ][ 'timeout' ] )
            main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
            main.installSleep = int( main.params[ 'SLEEP' ][ 'install' ] )
            main.verifySleep = int( main.params[ 'SLEEP' ][ 'verify' ] )
            main.intentManagerCfg = main.params[ 'CFG' ][ 'intentManager' ]
            main.intentConfigRegiCfg = main.params[ 'CFG' ][ 'intentConfigRegi' ]
            main.nullProviderCfg = main.params[ 'CFG' ][ 'nullProvider' ]
            main.linkCollectionIntentCfg = main.params[ 'CFG' ][ 'linkCollectionIntent' ]
            main.verifyAttempts = int( main.params[ 'ATTEMPTS' ][ 'verify' ] )
            main.cfgRetry = int( main.params[ 'ATTEMPTS' ][ 'cfg' ] )
            main.maxInvalidRun = int( main.params[ 'ATTEMPTS' ][ 'maxInvalidRun' ] )
            main.sampleSize = int( main.params[ 'TEST' ][ 'sampleSize' ] )
            main.warmUp = int( main.params[ 'TEST' ][ 'warmUp' ] )
            main.intentsList = ( main.params[ 'TEST' ][ 'intents' ] ).split( "," )
            main.deviceCount = int( main.params[ 'TEST' ][ 'deviceCount' ] )
            main.ingress = main.params[ 'TEST' ][ 'ingress' ]
            main.egress = main.params[ 'TEST' ][ 'egress' ]
            main.debug = main.params[ 'TEST' ][ 'debug' ]
            main.flowObj = main.params[ 'TEST' ][ 'flowObj' ]

            if main.flowObj == "True":
                main.flowObj = True
                main.dbFileName = main.params[ 'DATABASE' ][ 'dbFlowObj' ]
            else:
                main.flowObj = False
                main.dbFileName = main.params[ 'DATABASE' ][ 'dbName' ]

            for i in range( 0, len( main.intentsList ) ):
                main.intentsList[ i ] = int( main.intentsList[ i ] )

            stepResult = main.testSetUp.envSetup()
            # Create DataBase file
            main.log.info( "Create Database file " + main.dbFileName )
            resultsDB = open( main.dbFileName, "w+" )
            resultsDB.close()
            file1 = main.params[ "DEPENDENCY" ][ "FILE1" ]
            main.dependencyPath = os.path.dirname( os.getcwd() ) + main.params[ "DEPENDENCY" ][ "PATH" ]
            main.intentFuncs = imp.load_source( file1, main.dependencyPath + file1 + ".py" )
        except Exception as e:
            main.testSetUp.envSetupException( e )
        main.testSetUp.evnSetupConclusion( stepResult )
        main.commit = main.commit.split( " " )[ 1 ]

    def CASE1( self, main ):
        # Clean up test environment and set up
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
                                                              "deviceCount", value=main.deviceCount )
            stepResult = stepResult and \
                         main.Cluster.active( 0 ).CLI.setCfg( main.nullProviderCfg,
                                                              "topoShape", value="linear" )
            stepResult = stepResult and \
                         main.Cluster.active( 0 ).CLI.setCfg( main.nullProviderCfg,
                                                              "enabled", value="true" )
            stepResult = stepResult and \
                         main.Cluster.active( 0 ).CLI.setCfg( main.intentManagerCfg,
                                                              "skipReleaseResourcesOnWithdrawal",
                                                              value="true" )
            if main.flowObj:
                stepResult = stepResult and \
                             main.Cluster.active( 0 ).CLI.setCfg( main.intentConfigRegiCfg,
                                                                  "useFlowObjectives", value="true" )
                stepResult = stepResult and \
                             main.Cluster.active( 0 ).CLI.setCfg( main.intentConfigRegiCfg,
                                                                  "defaultFlowObjectiveCompiler",
                                                                  value=main.linkCollectionIntentCfg )
            time.sleep( main.startUpSleep )

            # balanceMasters
            stepResult = stepResult and \
                         main.Cluster.active( 0 ).CLI.balanceMasters()
            if stepResult:
                main.cfgCheck = True
                break
            configRetry += 1
            time.sleep( main.verifySleep )

        time.sleep( main.startUpSleep )
        if not main.cfgCheck:
            main.log.error( "Setting configuration to the ONOS failed. Skip the rest of the steps" )

    def CASE2( self, main ):
        import time
        import numpy
        import json
        testResult = main.TRUE
        main.case( "Installing/Withdrawing intents start" )
        main.step( "Checking starts" )
        if main.cfgCheck:
            print( main.intentsList )
            for batchSize in main.intentsList:
                main.log.report( "Intent Batch size: {}".format( batchSize ) )
                main.batchSize = batchSize
                main.installLatList = []
                main.withdrawLatList = []
                main.validrun = 0
                main.invalidrun = 0
                # we use two variables to control the iteration
                while main.validrun <= main.warmUp + main.sampleSize and main.invalidrun <= main.maxInvalidRun:
                    if main.validrun >= main.warmUp:
                        main.log.info( "================================================" )
                        main.log.info( "Starting test iteration " + str( main.validrun - main.warmUp ) )
                        main.log.info( "Total test iteration: " + str( main.invalidrun + main.validrun ) )
                        main.log.info( "================================================" )
                    else:
                        main.log.info( "====================Warm Up=====================" )

                    # push intents
                    installResult = main.Cluster.active( 0 ).CLI.pushTestIntents( main.ingress,
                                                                                  main.egress,
                                                                                  batchSize,
                                                                                  offset=1,
                                                                                  options="-i",
                                                                                  timeout=main.timeout,
                                                                                  getResponse=True )

                    time.sleep( 2 )
                    main.intentFuncs.sanityCheck( main,
                                                  ( main.deviceCount - 1 ) * 2,
                                                  batchSize * main.deviceCount,
                                                  main.batchSize )
                    if not main.verify:
                        main.log.warn( "Sanity check failed, skipping this iteration..." )
                        continue
                    if isinstance( installResult, str ):
                        if "Failure" in installResult:
                            main.log.error( "Install Intents failure, ignore this iteration." )
                            if main.validrun < main.warmUp:
                                main.validrun += 1
                                continue
                            else:
                                main.invalidrun += 1
                                continue

                        try:
                            latency = int( installResult.split()[ 5 ] )
                            main.log.info( installResult )
                        except:
                            main.log.error( "Failed to get latency, ignore this iteration." )
                            main.log.error( "Response from ONOS:" )
                            print( installResult )
                            if main.validrun < main.warmUp:
                                main.validrun += 1
                                continue
                            else:
                                main.invalidrun += 1
                                continue

                        if main.validrun >= main.warmUp:
                            main.installLatList.append( latency )
                    else:
                        main.invalidrun += 1
                        continue
                    # Withdraw Intents
                    withdrawResult = main.Cluster.active( 0 ).CLI.pushTestIntents( main.ingress,
                                                                                   main.egress,
                                                                                   batchSize,
                                                                                   offset=1,
                                                                                   options="-w",
                                                                                   timeout=main.timeout,
                                                                                   getResponse=True )
                    time.sleep( 5 )
                    main.Cluster.active( 0 ).CLI.purgeWithdrawnIntents()
                    main.intentFuncs.sanityCheck( main, ( main.deviceCount - 1 ) * 2, 0, 0 )
                    if not main.verify:
                        main.log.warn( "Sanity check failed, skipping this iteration..." )
                        continue
                    if isinstance( withdrawResult, str ):
                        if "Failure" in withdrawResult:
                            main.log.error( "withdraw Intents failure, ignore this iteration." )
                            if main.validrun < main.warmUp:
                                main.validrun += 1
                                continue
                            else:
                                main.invalidrun += 1
                                continue

                        try:
                            latency = int( withdrawResult.split()[ 5 ] )
                            main.log.info( withdrawResult )
                        except:
                            main.log.error( "Failed to get latency, ignore this iteration." )
                            main.log.error( "Response from ONOS:" )
                            print( withdrawResult )
                            if main.validrun < main.warmUp:
                                main.validrun += 1
                                continue
                            else:
                                main.invalidrun += 1
                                continue

                        if main.validrun >= main.warmUp:
                            main.withdrawLatList.append( latency )
                    else:
                        main.invalidrun += 1
                        continue
                    main.validrun += 1
                result = ( main.TRUE if main.invalidrun <= main.maxInvalidRun else main.FALSE )
                installave = numpy.average( main.installLatList ) if main.installLatList and result else 0
                installstd = numpy.std( main.installLatList ) if main.installLatList and result else 0
                withdrawave = numpy.average( main.withdrawLatList ) if main.withdrawLatList and result else 0
                withdrawstd = numpy.std( main.withdrawLatList ) if main.withdrawLatList and result else 0
                testResult = testResult and result
                # log report
                main.log.report( "----------------------------------------------------" )
                main.log.report( "Scale: " + str( main.Cluster.numCtrls ) )
                main.log.report( "Intent batch: " + str( batchSize ) )
                main.log.report( "Install average: {}    std: {}".format( installave, installstd ) )
                main.log.report( "Withdraw average: {}   std: {}".format( withdrawave, withdrawstd ) )
                # write result to database file
                if not ( numpy.isnan( installave ) or numpy.isnan( installstd ) or
                         numpy.isnan( withdrawstd ) or numpy.isnan( withdrawave ) ):
                    databaseString = "'" + main.commit + "',"
                    databaseString += str( main.Cluster.numCtrls ) + ","
                    databaseString += str( batchSize ) + ","
                    databaseString += str( installave ) + ","
                    databaseString += str( installstd ) + ","
                    databaseString += str( withdrawave ) + ","
                    databaseString += str( withdrawstd ) + "\n"
                    resultsDB = open( main.dbFileName, "a" )
                    resultsDB.write( databaseString )
                    resultsDB.close()
        else:
            testResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass="Installing and withdrawing intents properly",
                                 onfail="There was something wrong installing and withdrawing intents" )
