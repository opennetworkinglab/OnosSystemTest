"""
Copyright 2016 Open Networking Foundation ( ONF )

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
    SCPFhostLat
    This test will test the host found latency.
    Host will arping a ip address, tshark will caputure the package time, then compare with the topology event timestamp.
    Test will run with 1 node from start, and scale up to 7 nodes.
    The event timestamp will only greb the latest one, then calculate average and standar dev.

    yunpeng@onlab.us
"""
class SCPFhostLat:

    def __init__( self ):
        self.default = ''

    def CASE0( self, main ):
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
            main.cleanAndExit()
        main.testSetUp.envSetupDescription()
        stepResult = main.FALSE
        try:

            # Test variables
            main.cellName = main.params[ 'ENV' ][ 'cellName' ]
            main.apps = main.params[ 'ENV' ][ 'cellApps' ]
            main.scale = ( main.params[ 'SCALE' ] ).split( "," )
            main.ONOSport = main.params[ 'CTRL' ][ 'port' ]
            main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
            main.installSleep = int( main.params[ 'SLEEP' ][ 'install' ] )
            main.measurementSleep = int( main.params[ 'SLEEP' ][ 'measurement' ] )
            main.timeout = int( main.params[ 'SLEEP' ][ 'timeout' ] )
            main.dbFileName = main.params[ 'DATABASE' ][ 'file' ]

            # Tshark params
            main.tsharkResultPath = main.params[ 'TSHARK' ][ 'tsharkPath' ]
            main.tsharkPacketIn = main.params[ 'TSHARK' ][ 'tsharkPacketIn' ]

            main.numlter = main.params[ 'TEST' ][ 'numIter' ]
            main.iterIgnore = int( main.params[ 'TEST' ][ 'iterIgnore' ] )
            main.hostTimestampKey = main.params[ 'TEST' ][ 'hostTimestamp' ]
            main.thresholdStr = main.params[ 'TEST' ][ 'singleSwThreshold' ]
            main.thresholdObj = main.thresholdStr.split( ',' )
            main.thresholdMin = int( main.thresholdObj[ 0 ] )
            main.thresholdMax = int( main.thresholdObj[ 1 ] )
            main.threadID = 0

            main.maxNumBatch = 0
            main.setupSkipped = False

            main.nic = main.params[ 'DATABASE' ][ 'nic' ]
            node = main.params[ 'DATABASE' ][ 'node' ]
            stepResult = main.TRUE

            main.log.info( "Cresting DB file" )
            with open( main.dbFileName, "w+" ) as dbFile:
                dbFile.write( "" )
            stepResult = main.testSetUp.envSetup()
        except Exception as e:
            main.testSetUp.envSetupException( e )
        main.testSetUp.evnSetupConclusion( stepResult )

        main.commit = main.commit.split( " " )[ 1 ]

    def CASE2( self, main ):
        """
        - Uninstall ONOS cluster
        - Verify ONOS start up
        - Install ONOS cluster
        - Connect to cli
        """
        main.testSetUp.ONOSSetUp( main.Cluster, True,
                                  cellName=main.cellName, killRemoveMax=False )

    def CASE11( self, main ):
        main.log.info( "set and configure Application" )
        import json
        import time
        time.sleep( main.startUpSleep )
        main.step( "Activating org.onosproject.proxyarp" )
        appStatus = utilities.retry( main.Cluster.active( 0 ).REST.activateApp,
                                     main.FALSE,
                                     [ 'org.onosproject.proxyarp' ],
                                     sleep=3,
                                     attempts=3 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=appStatus,
                                 onpass="Successfully activated proxyarp",
                                 onfail="Failed to activated proxyarp" )

        main.step( "Set up Default Topology Provider" )
        appStatus = main.TRUE
        configName = 'org.onosproject.net.topology.impl.DefaultTopologyProvider'
        configParam = 'maxEvents'
        appStatus = appStatus and main.Cluster.active( 0 ).CLI.setCfg( configName, configParam, '1' )
        configParam = 'maxBatchMs'
        appStatus = appStatus and main.Cluster.active( 0 ).CLI.setCfg( configName, configParam, '0' )
        configParam = 'maxIdleMs'
        appStatus = appStatus and main.Cluster.active( 0 ).CLI.setCfg( configName, configParam, '0' )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=appStatus,
                                 onpass="Successfully set DefaultTopologyProvider",
                                 onfail="Failed to set DefaultTopologyProvider" )

        time.sleep( main.startUpSleep )
        main.step( 'Starting mininet topology' )
        mnCmd = '--topo=linear,1 '
        for ctrl in main.Cluster.active():
            mnCmd += " --controller remote,ip=" + ctrl.ipAddress
        mnStatus = main.Mininet1.startNet( args=mnCmd )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=mnStatus,
                                 onpass="Successfully started Mininet",
                                 onfail="Failed to activate Mininet" )
        main.step( "Assinging masters to switches" )
        switches = main.Mininet1.getSwitches()
        swStatus = main.Mininet1.assignSwController( sw=switches.keys(),
                                                     ip=main.Cluster.active( 0 ).ipAddress )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=swStatus,
                                 onpass="Successfully assigned switches to masters",
                                 onfail="Failed assign switches to masters" )

        time.sleep( main.startUpSleep )

    def CASE20( self, main ):
        """
        host1 send arping package and measure latency

        There are only 1 levels of latency measurements to this test:
        1 ) ARPING-to-device measurement: Measurement the time from host1
        send apring package to onos processing the host event

        """
        import time
        import subprocess
        import json
        import requests
        import os
        import numpy
        try:
            from tests.dependencies.utils import Utils
        except ImportError:
            main.log.error( "Utils not found exiting the test" )
            main.cleanAndExit()
        try:
            main.Utils
        except ( NameError, AttributeError ):
            main.Utils = Utils()
        # Host adding measurement
        assertion = main.TRUE

        main.log.report( 'Latency of adding one host to ONOS' )
        main.log.report( 'First ' + str( main.iterIgnore ) + ' iterations ignored' + ' for jvm warmup time' )
        main.log.report( 'Total iterations of test: ' + str( main.numlter ) )

        addingHostTime = []
        metricsResultList = []
        for i in range( 0, int( main.numlter ) ):
            main.log.info( 'Clean up data file' )
            with open( main.tsharkResultPath, "w" ) as dbFile:
                dbFile.write( "" )

            main.log.info( 'Starting tshark capture' )
            main.ONOSbench.tsharkGrep( main.tsharkPacketIn, main.tsharkResultPath )
            time.sleep( main.measurementSleep )

            main.log.info( 'host 1 arping...' )
            main.Mininet1.arping( srcHost='h1', dstHost='10.0.0.2' )

            time.sleep( main.measurementSleep )

            main.log.info( 'Stopping all Tshark processes' )
            main.ONOSbench.tsharkStop()

            time.sleep( main.measurementSleep )

            # Get tshark output
            with open( main.tsharkResultPath, "r" ) as resultFile:
                resultText = resultFile.readline()
                main.log.info( 'Capture result:' + resultText )
                resultText = resultText.strip().split( ' ' )
                if len( resultText ) > 1:
                    tsharkResultTime = float( resultText[ 1 ] ) * 1000.0
                else:
                    main.log.error( 'Tshark output file for packet_in' + ' returned unexpected results' )
                    hostTime = 0
                    caseResult = main.FALSE
                resultFile.close()
            # Compare the timestemps, and get the lowest one.
            temp = 0
            # Get host event timestamps from each nodes
            for ctrl in main.Cluster.active():
                metricsResult = json.loads( ctrl.CLI.topologyEventsMetrics() )
                metricsResult = metricsResult.get( main.hostTimestampKey ).get( "value" )
                main.log.info( "ONOS topology event matrics timestemp: {}".format( str( metricsResult ) ) )

                if temp < metricsResult:
                    temp = metricsResult
                metricsResult = temp

            if i >= main.iterIgnore:
                addingHostTime.append( float( metricsResult ) - tsharkResultTime )
            main.log.info( "Result of this iteration: {}".format( str( float( metricsResult ) - tsharkResultTime ) ) )
            # gethost to remove
            gethost = main.Cluster.active( 0 ).REST.hosts()
            HosttoRemove = []
            HosttoRemove.append( json.loads( gethost[ 1:len( gethost ) - 1 ] ).get( 'id' ) )
            main.Cluster.active( 0 ).CLI.removeHost( HosttoRemove )

        main.log.info( "Result List: {}".format( addingHostTime ) )

        # calculate average latency from each nodes
        averageResult = numpy.average( addingHostTime )
        main.log.info( "Average Latency: {}".format( averageResult ) )

        # calculate std
        stdResult = numpy.std( addingHostTime )
        main.log.info( "std: {}".format( stdResult ) )

        # Check test results
        threshold = float( main.params[ 'ALARM' ][ 'maxLat' ].split( ',' )[ main.cycle - 1 ] )
        if averageResult > threshold:
            main.log.alarm( "{}-node: {} ms > {} ms".format( main.Cluster.numCtrls,
                                                             averageResult, threshold ) )

        # write to DB file
        main.log.info( "Writing results to DS file" )
        with open( main.dbFileName, "a" ) as dbFile:
            temp = "'" + main.commit + "',"
            temp += "'" + main.nic + "',"
            # Scale number
            temp += str( main.Cluster.numCtrls )
            temp += ",'" + "baremetal1" + "'"
            # average latency
            temp += "," + str( averageResult )
            # std of latency
            temp += "," + str( stdResult )
            temp += "\n"
            dbFile.write( temp )

        assertion = main.TRUE

        utilities.assert_equals( expect=main.TRUE, actual=assertion,
                                 onpass='Host latency test successful',
                                 onfail='Host latency test failed' )

        main.Utils.mininetCleanup( main.Mininet1 )
