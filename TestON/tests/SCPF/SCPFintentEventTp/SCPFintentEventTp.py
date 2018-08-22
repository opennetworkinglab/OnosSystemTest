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
SCPFintentEventTp
    - Use intentperf app to generate a lot of intent install and withdraw events
    - Test will run with 1,3,5,7 nodes, and with all neighbors
    - Test will run 400 seconds and grep the overall rate from intent-perf summary

    yunpeng@onlab.us
"""
import time


class SCPFintentEventTp:

    def __init__( self ):
        self.default = ''

    def CASE0( self, main ):
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
            main.cellName = main.params[ 'ENV' ][ 'cellName' ]
            main.apps = main.params[ 'ENV' ][ 'cellApps' ]
            main.BENCHIp = main.params[ 'BENCH' ][ 'ip1' ]
            main.BENCHUser = main.params[ 'BENCH' ][ 'user' ]
            main.MN1Ip = main.params[ 'MN' ][ 'ip1' ]
            main.numSwitches = ( main.params[ 'TEST' ][ 'numSwitches' ] ).split( "," )
            main.skipRelRsrc = main.params[ 'TEST' ][ 'skipReleaseResourcesOnWithdrawal' ]
            main.flowObj = main.params[ 'TEST' ][ 'flowObj' ]
            main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
            main.installSleep = int( main.params[ 'SLEEP' ][ 'install' ] )
            main.verifySleep = int( main.params[ 'SLEEP' ][ 'verify' ] )
            main.scale = ( main.params[ 'SCALE' ] ).split( "," )
            main.testDuration = main.params[ 'TEST' ][ 'duration' ]
            main.logInterval = main.params[ 'TEST' ][ 'log_interval' ]
            main.debug = main.params[ 'debugMode' ]
            main.intentManagerCfg = main.params[ 'CFG' ][ 'intentManager' ]
            main.intentConfigRegiCfg = main.params[ 'CFG' ][ 'intentConfigRegi' ]
            main.nullProviderCfg = main.params[ 'CFG' ][ 'nullProvider' ]
            main.intentPerfInstallerCfg = main.params[ 'CFG' ][ 'intentPerfInstaller' ]
            main.neighbor = ( main.params[ 'TEST' ][ 'neighbors' ] ).split( "," )
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
        main.testSetUp.ONOSSetUp( main.Cluster, True,
                                  cellName=main.cellName, killRemoveMax=False )
        # config apps
        main.Cluster.active( 0 ).CLI.setCfg( main.intentManagerCfg,
                                             "skipReleaseResourcesOnWithdrawal " + main.skipRelRsrc )
        main.Cluster.active( 0 ).CLI.setCfg( main.nullProviderCfg,
                                             "deviceCount " + str( int( main.Cluster.numCtrls * 10 ) ) )
        main.Cluster.active( 0 ).CLI.setCfg( main.nullProviderCfg, "topoShape linear" )
        main.Cluster.active( 0 ).CLI.setCfg( main.nullProviderCfg, "enabled true" )
        if main.flowObj:
            main.Cluster.active( 0 ).CLI.setCfg( main.intentConfigRegiCfg,
                                                 "useFlowObjectives", value="true" )
        time.sleep( main.startUpSleep )

        # balanceMasters
        main.Cluster.active( 0 ).CLI.balanceMasters()
        time.sleep( main.startUpSleep )

    def CASE2( self, main ):
        import numpy
        # If we activate intentperf from the cell, there's chance that it doesn't get all cluster
        # nodes when some of the nodes have a large startup delay
        main.log.info( "Activate intentperf app" )
        main.Cluster.active( 0 ).CLI.app( "intentperf", "activate" )
        time.sleep( 5 )
        main.log.info( "Cluster Count = " + str( main.Cluster.numCtrls ) )
        neighbors = '0' if main.neighbor.pop( 0 ) == '0' else str( main.Cluster.numCtrls - 1 )
        main.log.info( "Neighbors: " + neighbors )
        main.log.info( "Config intent-perf app" )
        main.Cluster.active( 0 ).CLI.setCfg( main.intentPerfInstallerCfg,
                                             "numKeys " + main.numKeys )
        main.Cluster.active( 0 ).CLI.setCfg( main.intentPerfInstallerCfg,
                                             "numNeighbors " + neighbors )
        main.Cluster.active( 0 ).CLI.setCfg( main.intentPerfInstallerCfg,
                                             "cyclePeriod " + main.cyclePeriod )

        main.log.info( "Starting intent-perf test for " + str( main.testDuration ) + " seconds..." )
        main.Cluster.active( 0 ).CLI.sendline( "intent-perf-start" )
        stop = time.time() + float( main.testDuration )

        while time.time() < stop:
            time.sleep( 15 )
            result = main.Cluster.active( 0 ).CLI.getIntentPerfSummary()
            if result:
                for ctrl in main.Cluster.active():
                    main.log.info( "Node {} Overall Rate: {}".format( ctrl.ipAddress,
                                                                      result[ ctrl.ipAddress ] ) )
        main.log.info( "Stop intent-perf" )
        for ctrl in main.Cluster.active():
            ctrl.CLI.sendline( "intent-perf-stop" )
        if result:
            for ctrl in main.Cluster.active():
                main.log.info( "Node {} final Overall Rate: {}".format( ctrl.ipAddress,
                                                                        result[ ctrl.ipAddress ] ) )

        with open( main.dbFileName, "a" ) as resultDB:
            for nodes in range( main.Cluster.numCtrls ):
                resultString = "'" + main.commit + "',"
                resultString += "'1gig',"
                resultString += str( main.Cluster.numCtrls ) + ","
                resultString += "'baremetal" + str(nodes + 1) + "',"
                resultString += neighbors + ","
                resultString += result[ main.Cluster.active( nodes ).ipAddress ] + ","
                resultString += str( 0 ) + "\n"  # no stddev
                resultDB.write( resultString )
        resultDB.close()
