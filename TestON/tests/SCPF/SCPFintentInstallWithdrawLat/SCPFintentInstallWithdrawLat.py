"""
Copyright 2015 Open Networking Foundation (ONF)

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

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
    - The batch size is defined in parm file. ( default 1,100,1000)

    yunpeng@onlab.us
"""
class SCPFintentInstallWithdrawLat:
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
            main.sampleSize = int( main.params[ 'TEST' ][ 'sampleSize' ] )
            main.warmUp = int( main.params[ 'TEST' ][ 'warmUp' ] )
            main.intentsList = ( main.params[ 'TEST' ][ 'intents' ] ).split( "," )
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
        except Exception as e:
            main.testSetUp.envSetupException( e )
        main.testSetUp.evnSetupConclusion( stepResult )
        main.commit = main.commit.split( " " )[ 1 ]
    def CASE1( self, main ):
        # Clean up test environment and set up
        import time

        main.maxNumBatch = 0
        main.testSetUp.ONOSSetUp( main.MN1Ip, main.Cluster, True,
                                  cellName=main.cellName, killRemoveMax=False )

        # configure apps
        main.Cluster.active( 0 ).CLI.setCfg( main.nullProviderCfg,
                                             "deviceCount", value=7 )
        main.Cluster.active( 0 ).CLI.setCfg( main.nullProviderCfg,
                                             "topoShape", value="linear" )
        main.Cluster.active( 0 ).CLI.setCfg( main.nullProviderCfg,
                                             "enabled", value="true" )
        main.Cluster.active( 0 ).CLI.setCfg( main.intentManagerCfg,
                                             "skipReleaseResourcesOnWithdrawal",
                                             value="true" )
        if main.flowObj:
            main.Cluster.active( 0 ).CLI.setCfg( main.intentConfigRegiCfg,
                                                 "useFlowObjectives", value="true" )
            main.Cluster.active( 0 ).CLI.setCfg( main.intentConfigRegiCfg,
                                                 "defaultFlowObjectiveCompiler",
                                                 value=main.linkCollectionIntentCfg )
        time.sleep( main.startUpSleep )

        # balanceMasters
        main.Cluster.active( 0 ).CLI.balanceMasters()
        time.sleep( main.startUpSleep )

    def CASE2( self, main ):
        import time
        import numpy
        import json
        print( main.intentsList )
        for batchSize in main.intentsList:
            main.log.report( "Intent Batch size: {}".format( batchSize ) )
            main.installLatList = []
            main.withdrawLatList = []
            validrun = 0
            invalidrun = 0
            # we use two variables to control the iteration
            while validrun <= main.warmUp + main.sampleSize and invalidrun < 20:
                if validrun >= main.warmUp:
                    main.log.info( "================================================" )
                    main.log.info( "Starting test iteration " + str( validrun - main.warmUp ) )
                    main.log.info( "Total test iteration: " + str( invalidrun + validrun ) )
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
                if type( installResult ) is str:
                    if "Failure" in installResult:
                        main.log.error( "Install Intents failure, ignore this iteration." )
                        if validrun < main.warmUp:
                            validrun += 1
                            continue
                        else:
                            invalidrun += 1
                            continue

                    try:
                        latency = int( installResult.split()[ 5 ] )
                        main.log.info( installResult )
                    except:
                        main.log.error( "Failed to get latency, ignore this iteration." )
                        main.log.error( "Response from ONOS:" )
                        print( installResult )
                        if validrun < main.warmUp:
                            validrun += 1
                            continue
                        else:
                            invalidrun += 1
                            continue

                    if validrun >= main.warmUp:
                        main.installLatList.append( latency )
                else:
                    invalidrun += 1
                    continue
                time.sleep( 2 )
                # Withdraw Intents
                withdrawResult = main.Cluster.active( 0 ).CLI.pushTestIntents( main.ingress,
                                                                               main.egress,
                                                                               batchSize,
                                                                               offset=1,
                                                                               options="-w",
                                                                               timeout=main.timeout,
                                                                               getResponse=True )

                if type( withdrawResult ) is str:
                    if "Failure" in withdrawResult:
                        main.log.error( "withdraw Intents failure, ignore this iteration." )
                        if validrun < main.warmUp:
                            validrun += 1
                            continue
                        else:
                            invalidrun += 1
                            continue

                    try:
                        latency = int( withdrawResult.split()[ 5 ] )
                        main.log.info( withdrawResult )
                    except:
                        main.log.error( "Failed to get latency, ignore this iteration." )
                        main.log.error( "Response from ONOS:" )
                        print( withdrawResult )
                        if validrun < main.warmUp:
                            validrun += 1
                            continue
                        else:
                            invalidrun += 1
                            continue

                    if validrun >= main.warmUp:
                        main.withdrawLatList.append( latency )
                else:
                    invalidrun += 1
                    continue
                time.sleep( 2 )
                main.Cluster.active( 0 ).CLI.purgeWithdrawnIntents()
                validrun += 1
            installave = numpy.average( main.installLatList )
            installstd = numpy.std( main.installLatList )
            withdrawave = numpy.average( main.withdrawLatList )
            withdrawstd = numpy.std( main.withdrawLatList )
            # log report
            main.log.report( "----------------------------------------------------" )
            main.log.report( "Scale: " + str( main.Cluster.numCtrls ) )
            main.log.report( "Intent batch: " + str( batchSize ) )
            main.log.report( "Install average: {}    std: {}".format( installave, installstd ) )
            main.log.report( "Withdraw average: {}   std: {}".format( withdrawave, withdrawstd ) )
            # write result to database file
            if not ( numpy.isnan( installave ) or numpy.isnan( installstd ) or\
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
