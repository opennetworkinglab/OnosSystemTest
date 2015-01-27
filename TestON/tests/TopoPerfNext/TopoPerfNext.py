# TopoPerfNext
#
# Topology Performance test for ONOS-next
#
# andrew@onlab.us
#
# If your machine does not come with numpy
# run the following command:
# sudo apt-get install python-numpy python-scipy

import time
import sys
import os
import re


class TopoPerfNext:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        ONOS startup sequence
        """
        import time

        # Global cluster count for scale-out purposes
        global clusterCount
        # Set initial cluster count
        clusterCount = 1
        ##

        cellName = main.params[ 'ENV' ][ 'cellName' ]

        gitPull = main.params[ 'GIT' ][ 'autoPull' ]
        checkoutBranch = main.params[ 'GIT' ][ 'checkout' ]

        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS2Ip = main.params[ 'CTRL' ][ 'ip2' ]
        ONOS3Ip = main.params[ 'CTRL' ][ 'ip3' ]
        ONOS4Ip = main.params[ 'CTRL' ][ 'ip4' ] 
        ONOS5Ip = main.params[ 'CTRL' ][ 'ip5' ]
        ONOS6Ip = main.params[ 'CTRL' ][ 'ip6' ]
        ONOS7Ip = main.params[ 'CTRL' ][ 'ip7' ] 

        MN1Ip = main.params[ 'MN' ][ 'ip1' ]
        BENCHIp = main.params[ 'BENCH' ][ 'ip' ]

        topoCfgFile = main.params[ 'TEST' ][ 'topoConfigFile' ]
        topoCfgName = main.params[ 'TEST' ][ 'topoConfigName' ]

        mvnCleanInstall = main.params[ 'TEST' ][ 'mci' ]
        
        main.case( "Setting up test environment" )
        main.log.info( "Copying topology event accumulator config" +
                       " to ONOS /package/etc" )
        main.ONOSbench.handle.sendline( "cp ~/" +
                                        topoCfgFile +
                                        " ~/ONOS/tools/package/etc/" +
                                        topoCfgName )
        main.ONOSbench.handle.expect( "\$" )

        main.log.report( "Setting up test environment" )

        main.step( "Cleaning previously installed ONOS if any" )
        main.ONOSbench.onosUninstall( nodeIp=ONOS2Ip )
        main.ONOSbench.onosUninstall( nodeIp=ONOS3Ip )
        main.ONOSbench.onosUninstall( nodeIp=ONOS4Ip )
        main.ONOSbench.onosUninstall( nodeIp=ONOS5Ip )
        main.ONOSbench.onosUninstall( nodeIp=ONOS6Ip )
        #main.ONOSbench.onosUninstall( nodeIp=ONOS7Ip )

        main.step( "Creating cell file" )
        cellFileResult = main.ONOSbench.createCellFile(
            BENCHIp, cellName, MN1Ip,
            "onos-core,onos-app-metrics,onos-app-gui",
            ONOS1Ip )

        main.step( "Applying cell file to environment" )
        cellApplyResult = main.ONOSbench.setCell( cellName )
        verifyCellResult = main.ONOSbench.verifyCell()

        # NOTE: This step may be removed after proper
        #      copy cat log functionality
        main.step( "Removing raft/copy-cat logs from ONOS nodes" )
        main.ONOSbench.onosRemoveRaftLogs()
        time.sleep( 30 )

        main.step( "Git checkout and pull " + checkoutBranch )
        if gitPull == 'on':
            # checkoutResult = \
                    #        main.ONOSbench.gitCheckout( checkoutBranch )
            checkoutResult = main.TRUE
            pullResult = main.ONOSbench.gitPull()
        else:
            checkoutResult = main.TRUE
            pullResult = main.TRUE
            main.log.info( "Skipped git checkout and pull" )

        main.log.report( "Commit information - " )
        main.ONOSbench.getVersion( report=True )

        main.step( "Using mvn clean & install" )
        if mvnCleanInstall == 'on':
            mvnResult = main.ONOSbench.cleanInstall()
        elif mvnCleanInstall == 'off':
            main.log.info("mci turned off by settings")
            mvnResult = main.TRUE

        main.step( "Set cell for ONOS cli env" )
        main.ONOS1cli.setCell( cellName )
        # main.ONOS2cli.setCell( cellName )
        # main.ONOS3cli.setCell( cellName )

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()

        main.step( "Installing ONOS package" )
        install1Result = main.ONOSbench.onosInstall( node=ONOS1Ip )
        #install2Result = main.ONOSbench.onosInstall( node=ONOS2Ip )
        #install3Result = main.ONOSbench.onosInstall( node=ONOS3Ip )

        time.sleep( 10 )

        main.step( "Start onos cli" )
        cli1 = main.ONOS1cli.startOnosCli( ONOS1Ip )
        #cli2 = main.ONOS2cli.startOnosCli( ONOS2Ip )
        #cli3 = main.ONOS3cli.startOnosCli( ONOS3Ip )

        utilities.assert_equals( expect=main.TRUE,
                                actual=cellFileResult and cellApplyResult and
                                verifyCellResult and checkoutResult and
                                pullResult and mvnResult and
                                install1Result,  # and install2Result and
                                # install3Result,
                                onpass="Test Environment setup successful",
                                onfail="Failed to setup test environment" )

    def CASE2( self, main ):
        """
        Assign s1 to ONOS1 and measure latency

        There are 4 levels of latency measurements to this test:
        1 ) End-to-end measurement: Complete end-to-end measurement
           from TCP ( SYN/ACK ) handshake to Graph change
        2 ) OFP-to-graph measurement: 'ONOS processing' snippet of
           measurement from OFP Vendor message to Graph change
        3 ) OFP-to-device measurement: 'ONOS processing without
           graph change' snippet of measurement from OFP vendor
           message to Device change timestamp
        4 ) T0-to-device measurement: Measurement that includes
           the switch handshake to devices timestamp without
           the graph view change. ( TCP handshake -> Device
           change )
        """
        import time
        import subprocess
        import json
        import requests
        import os
        import numpy
        global clusterCount

        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS2Ip = main.params[ 'CTRL' ][ 'ip2' ]
        ONOS3Ip = main.params[ 'CTRL' ][ 'ip3' ]
        ONOS4Ip = main.params[ 'CTRL' ][ 'ip4' ]
        ONOS5Ip = main.params[ 'CTRL' ][ 'ip5' ]
        ONOS6Ip = main.params[ 'CTRL' ][ 'ip6' ]
        ONOS7Ip = main.params[ 'CTRL' ][ 'ip7' ]

        ONOSUser = main.params[ 'CTRL' ][ 'user' ]

        defaultSwPort = main.params[ 'CTRL' ][ 'port1' ]

        # Number of iterations of case
        numIter = main.params[ 'TEST' ][ 'numIter' ]
        # Number of first 'x' iterations to ignore:
        iterIgnore = int( main.params[ 'TEST' ][ 'iterIgnore' ] )

        # Timestamp 'keys' for json metrics output.
        # These are subject to change, hence moved into params
        deviceTimestamp = main.params[ 'JSON' ][ 'deviceTimestamp' ]
        graphTimestamp = main.params[ 'JSON' ][ 'graphTimestamp' ]

        debugMode = main.params[ 'TEST' ][ 'debugMode' ]
        onosLog = main.params[ 'TEST' ][ 'onosLogFile' ]

        # Threshold for the test
        thresholdStr = main.params[ 'TEST' ][ 'singleSwThreshold' ]
        thresholdObj = thresholdStr.split( "," )
        thresholdMin = int( thresholdObj[ 0 ] )
        thresholdMax = int( thresholdObj[ 1 ] )

        # List of switch add latency collected from
        # all iterations
        latencyEndToEndList = []
        latencyOfpToGraphList = []
        latencyOfpToDeviceList = []
        latencyT0ToDeviceList = []
        latencyTcpToOfpList = []

        # Directory/file to store tshark results
        tsharkOfOutput = "/tmp/tshark_of_topo.txt"
        tsharkTcpOutput = "/tmp/tshark_tcp_topo.txt"

        # String to grep in tshark output
        tsharkTcpString = "TCP 74 " + defaultSwPort
        tsharkOfString = "OFP 86 Vendor"

        # Initialize assertion to TRUE
        assertion = main.TRUE

        localTime = time.strftime( '%x %X' )
        localTime = localTime.replace( "/", "" )
        localTime = localTime.replace( " ", "_" )
        localTime = localTime.replace( ":", "" )
        if debugMode == 'on':
            main.ONOS1.tsharkPcap( "eth0",
                                   "/tmp/single_sw_lat_pcap_" + localTime )

            main.log.info( "Debug mode is on" )

        main.log.report( "Latency of adding one switch to controller" )
        main.log.report( "First " + str( iterIgnore ) + " iterations ignored" +
                         " for jvm warmup time" )
        main.log.report( "Total iterations of test: " + str( numIter ) )

        for i in range( 0, int( numIter ) ):
            main.log.info( "Starting tshark capture" )

            #* TCP [ ACK, SYN ] is used as t0A, the
            #  very first "exchange" between ONOS and
            #  the switch for end-to-end measurement
            #* OFP [ Stats Reply ] is used for t0B
            #  the very last OFP message between ONOS
            #  and the switch for ONOS measurement
            main.ONOS1.tsharkGrep( tsharkTcpString,
                                   tsharkTcpOutput )
            main.ONOS1.tsharkGrep( tsharkOfString,
                                   tsharkOfOutput )

            # Wait and ensure tshark is started and
            # capturing
            time.sleep( 10 )

            main.log.info( "Assigning s1 to controller" )

            main.Mininet1.assignSwController(
                sw="1",
                ip1=ONOS1Ip,
                port1=defaultSwPort )

            # Wait and ensure switch is assigned
            # before stopping tshark
            time.sleep( 30 )

            main.log.info( "Stopping all Tshark processes" )
            main.ONOS1.stopTshark()

            # tshark output is saved in ONOS. Use subprocess
            # to copy over files to TestON for parsing
            main.log.info( "Copying over tshark files" )

            # TCP CAPTURE ****
            # Copy the tshark output from ONOS machine to
            # TestON machine in tsharkTcpOutput directory>file
            os.system( "scp " + ONOSUser + "@" + ONOS1Ip + ":" +
                       tsharkTcpOutput + " /tmp/" )
            tcpFile = open( tsharkTcpOutput, 'r' )
            tempText = tcpFile.readline()
            tempText = tempText.split( " " )

            main.log.info( "Object read in from TCP capture: " +
                           str( tempText ) )
            if len( tempText ) > 1:
                t0Tcp = float( tempText[ 1 ] ) * 1000.0
            else:
                main.log.error( "Tshark output file for TCP" +
                                " returned unexpected results" )
                t0Tcp = 0
                assertion = main.FALSE

            tcpFile.close()
            #****************

            # OF CAPTURE ****
            os.system( "scp " + ONOSUser + "@" + ONOS1Ip + ":" +
                       tsharkOfOutput + " /tmp/" )
            ofFile = open( tsharkOfOutput, 'r' )

            lineOfp = ""
            # Read until last line of file
            while True:
                tempText = ofFile.readline()
                if tempText != '':
                    lineOfp = tempText
                else:
                    break
            obj = lineOfp.split( " " )

            main.log.info( "Object read in from OFP capture: " +
                           str( lineOfp ) )

            if len( lineOfp ) > 1:
                t0Ofp = float( obj[ 1 ] ) * 1000.0
            else:
                main.log.error( "Tshark output file for OFP" +
                                " returned unexpected results" )
                t0Ofp = 0
                assertion = main.FALSE

            ofFile.close()
            #****************

            jsonStr1 = main.ONOS1cli.topologyEventsMetrics()
            # Initialize scale-out variables
            jsonStr2 = ""
            jsonStr3 = ""
            jsonStr4 = ""
            jsonStr5 = ""
            jsonStr6 = ""
            jsonStr7 = ""

            jsonObj1 = json.loads( jsonStr1 )
            # Initialize scale-out variables
            jsonObj2 = ""
            jsonObj3 = ""
            jsonObj4 = ""
            jsonObj5 = ""
            jsonObj6 = ""
            jsonObj7 = ""

            # Obtain graph timestamp. This timestsamp captures
            # the epoch time at which the topology graph was updated.
            graphTimestamp1 = \
                jsonObj1[ graphTimestamp ][ 'value' ]
            # Obtain device timestamp. This timestamp captures
            # the epoch time at which the device event happened
            deviceTimestamp1 = \
                jsonObj1[ deviceTimestamp ][ 'value' ]

            # t0 to device processing latency
            deltaDevice1 = int( deviceTimestamp1 ) - int( t0Tcp )

            # t0 to graph processing latency ( end-to-end )
            deltaGraph1 = int( graphTimestamp1 ) - int( t0Tcp )

            # ofp to graph processing latency ( ONOS processing )
            deltaOfpGraph1 = int( graphTimestamp1 ) - int( t0Ofp )

            # ofp to device processing latency ( ONOS processing )
            deltaOfpDevice1 = float( deviceTimestamp1 ) - float( t0Ofp )

            # TODO: Create even cluster number events

            # Include scale-out measurements when applicable
            if clusterCount >= 3:
                jsonStr2 = main.ONOS2cli.topologyEventsMetrics()
                jsonStr3 = main.ONOS3cli.topologyEventsMetrics()
                jsonObj2 = json.loads( jsonStr2 )
                jsonObj3 = json.loads( jsonStr3 )
                graphTimestamp2 = \
                    jsonObj2[ graphTimestamp ][ 'value' ]
                graphTimestamp3 = \
                    jsonObj3[ graphTimestamp ][ 'value' ]
                deviceTimestamp2 = \
                    jsonObj2[ deviceTimestamp ][ 'value' ]
                deviceTimestamp3 = \
                    jsonObj3[ deviceTimestamp ][ 'value' ]
                deltaDevice2 = int( deviceTimestamp2 ) - int( t0Tcp )
                deltaDevice3 = int( deviceTimestamp3 ) - int( t0Tcp )
                deltaGraph2 = int( graphTimestamp2 ) - int( t0Tcp )
                deltaGraph3 = int( graphTimestamp3 ) - int( t0Tcp )
                deltaOfpGraph2 = int( graphTimestamp2 ) - int( t0Ofp )
                deltaOfpGraph3 = int( graphTimestamp3 ) - int( t0Ofp )
                deltaOfpDevice2 = float( deviceTimestamp2 ) -\
                    float( t0Ofp )
                deltaOfpDevice3 = float( deviceTimestamp3 ) -\
                    float( t0Ofp )
            else:
                deltaDevice2 = 0
                deltaDevice3 = 0
                deltaGraph2 = 0
                deltaGraph3 = 0
                deltaOfpGraph2 = 0
                deltaOfpGraph3 = 0
                deltaOfpDevice2 = 0
                deltaOfpDevice3 = 0

            if clusterCount >= 5:
                jsonStr4 = main.ONOS4cli.topologyEventsMetrics()
                jsonStr5 = main.ONOS5cli.topologyEventsMetrics()
                jsonObj4 = json.loads( jsonStr4 )
                jsonObj5 = json.loads( jsonStr5 )
                graphTimestamp4 = \
                    jsonObj4[ graphTimestamp ][ 'value' ]
                graphTimestamp5 = \
                    jsonObj5[ graphTimestamp ][ 'value' ]
                deviceTimestamp4 = \
                    jsonObj4[ deviceTimestamp ][ 'value' ]
                deviceTimestamp5 = \
                    jsonObj5[ deviceTimestamp ][ 'value' ]
                deltaDevice4 = int( deviceTimestamp4 ) - int( t0Tcp )
                deltaDevice5 = int( deviceTimestamp5 ) - int( t0Tcp )
                deltaGraph4 = int( graphTimestamp4 ) - int( t0Tcp )
                deltaGraph5 = int( graphTimestamp5 ) - int( t0Tcp )
                deltaOfpGraph4 = int( graphTimestamp4 ) - int( t0Ofp )
                deltaOfpGraph5 = int( graphTimestamp5 ) - int( t0Ofp )
                deltaOfpDevice4 = float( deviceTimestamp4 ) -\
                    float( t0Ofp )
                deltaOfpDevice5 = float( deviceTimestamp5 ) -\
                    float( t0Ofp )
            else:
                deltaDevice4 = 0
                deltaDevice5 = 0
                deltaGraph4 = 0
                deltaGraph5 = 0
                deltaOfpGraph4 = 0
                deltaOfpGraph5 = 0
                deltaOfpDevice4 = 0
                deltaOfpDevice5 = 0

            if clusterCount >= 7:
                jsonStr6 = main.ONOS6cli.topologyEventsMetrics()
                jsonStr7 = main.ONOS7cli.topologyEventsMetrics()
                jsonObj6 = json.loads( jsonStr6 )
                jsonObj7 = json.loads( jsonStr7 )
                graphTimestamp6 = \
                    jsonObj6[ graphTimestamp ][ 'value' ]
                graphTimestamp7 = \
                    jsonObj7[ graphTimestamp ][ 'value' ]
                deviceTimestamp6 = \
                    jsonObj6[ deviceTimestamp ][ 'value' ]
                deviceTimestamp7 = \
                    jsonObj7[ deviceTimestamp ][ 'value' ]
                deltaDevice6 = int( deviceTimestamp6 ) - int( t0Tcp )
                deltaDevice7 = int( deviceTimestamp7 ) - int( t0Tcp )
                deltaGraph6 = int( graphTimestamp6 ) - int( t0Tcp )
                deltaGraph7 = int( graphTimestamp7 ) - int( t0Tcp )
                deltaOfpGraph6 = int( graphTimestamp6 ) - int( t0Ofp )
                deltaOfpGraph7 = int( graphTimestamp7 ) - int( t0Ofp )
                deltaOfpDevice6 = float( deviceTimestamp6 ) -\
                    float( t0Ofp )
                deltaOfpDevice7 = float( deviceTimestamp7 ) -\
                    float( t0Ofp )
            else:
                deltaDevice6 = 0
                deltaDevice7 = 0
                deltaGraph6 = 0
                deltaGraph7 = 0
                deltaOfpGraph6 = 0
                deltaOfpGraph7 = 0
                deltaOfpDevice6 = 0
                deltaOfpDevice7 = 0

            # Get average of delta from all instances
            avgDeltaDevice = \
                ( int( deltaDevice1 ) +
                  int( deltaDevice2 ) +
                  int( deltaDevice3 ) +
                  int( deltaDevice4 ) +
                  int( deltaDevice5 ) +
                  int( deltaDevice6 ) +
                  int( deltaDevice7 ) ) / clusterCount

            # Ensure avg delta meets the threshold before appending
            if avgDeltaDevice > 0.0 and avgDeltaDevice < 10000\
                    and int( i ) > iterIgnore:
                latencyT0ToDeviceList.append( avgDeltaDevice )
            else:
                main.log.info(
                    "Results for t0-to-device ignored" +
                    "due to excess in threshold / warmup iteration." )

            # Get average of delta from all instances
            # TODO: use max delta graph
            #maxDeltaGraph = max( three )
            avgDeltaGraph = \
                ( int( deltaGraph1 ) +
                  int( deltaGraph2 ) +
                  int( deltaGraph3 ) +
                  int( deltaGraph4 ) +
                  int( deltaGraph5 ) +
                  int( deltaGraph6 ) +
                  int( deltaGraph7 ) ) / clusterCount

            # Ensure avg delta meets the threshold before appending
            if avgDeltaGraph > 0.0 and avgDeltaGraph < 10000\
                    and int( i ) > iterIgnore:
                latencyEndToEndList.append( avgDeltaGraph )
            else:
                main.log.info( "Results for end-to-end ignored" +
                               "due to excess in threshold" )

            avgDeltaOfpGraph = \
                ( int( deltaOfpGraph1 ) +
                  int( deltaOfpGraph2 ) +
                  int( deltaOfpGraph3 ) +
                  int( deltaOfpGraph4 ) +
                  int( deltaOfpGraph5 ) +
                  int( deltaOfpGraph6 ) +
                  int( deltaOfpGraph7 ) ) / clusterCount

            if avgDeltaOfpGraph > thresholdMin \
                    and avgDeltaOfpGraph < thresholdMax\
                    and int( i ) > iterIgnore:
                latencyOfpToGraphList.append( avgDeltaOfpGraph )
            elif avgDeltaOfpGraph > ( -10 ) and \
                    avgDeltaOfpGraph < 0.0 and\
                    int( i ) > iterIgnore:
                main.log.info( "Sub-millisecond result likely; " +
                               "negative result was rounded to 0" )
                # NOTE: Current metrics framework does not
                # support sub-millisecond accuracy. Therefore,
                # if the result is negative, we can reasonably
                # conclude sub-millisecond results and just
                # append the best rounded effort - 0 ms.
                latencyOfpToGraphList.append( 0 )
            else:
                main.log.info( "Results for ofp-to-graph " +
                               "ignored due to excess in threshold" )

            avgDeltaOfpDevice = \
                ( float( deltaOfpDevice1 ) +
                  float( deltaOfpDevice2 ) +
                  float( deltaOfpDevice3 ) +
                  float( deltaOfpDevice4 ) +
                  float( deltaOfpDevice5 ) +
                  float( deltaOfpDevice6 ) +
                  float( deltaOfpDevice7 ) ) / clusterCount

            # NOTE: ofp - delta measurements are occasionally negative
            #      due to system time misalignment.
            latencyOfpToDeviceList.append( avgDeltaOfpDevice )

            deltaOfpTcp = int( t0Ofp ) - int( t0Tcp )
            if deltaOfpTcp > thresholdMin \
                    and deltaOfpTcp < thresholdMax and\
                    int( i ) > iterIgnore:
                latencyTcpToOfpList.append( deltaOfpTcp )
            else:
                main.log.info( "Results fo tcp-to-ofp " +
                               "ignored due to excess in threshold" )

            # TODO:
            # Fetch logs upon threshold excess

            main.log.info( "ONOS1 delta end-to-end: " +
                           str( deltaGraph1 ) + " ms" )

            main.log.info( "ONOS1 delta OFP - graph: " +
                           str( deltaOfpGraph1 ) + " ms" )

            main.log.info( "ONOS1 delta device - t0: " +
                           str( deltaDevice1 ) + " ms" )

            main.log.info( "TCP to OFP delta: " +
                           str( deltaOfpTcp ) + " ms" )

            main.step( "Remove switch from controller" )
            main.Mininet1.deleteSwController( "s1" )

            time.sleep( 5 )

        # END of for loop iteration

        # If there is at least 1 element in each list,
        # pass the test case
        if len( latencyEndToEndList ) > 0 and\
           len( latencyOfpToGraphList ) > 0 and\
           len( latencyOfpToDeviceList ) > 0 and\
           len( latencyT0ToDeviceList ) > 0 and\
           len( latencyTcpToOfpList ) > 0:
            assertion = main.TRUE
        elif len( latencyEndToEndList ) == 0:
            # The appending of 0 here is to prevent
            # the min,max,sum functions from failing
            # below
            latencyEndToEndList.append( 0 )
            assertion = main.FALSE
        elif len( latencyOfpToGraphList ) == 0:
            latencyOfpToGraphList.append( 0 )
            assertion = main.FALSE
        elif len( latencyOfpToDeviceList ) == 0:
            latencyOfpToDeviceList.append( 0 )
            assertion = main.FALSE
        elif len( latencyT0ToDeviceList ) == 0:
            latencyT0ToDeviceList.append( 0 )
            assertion = main.FALSE
        elif len( latencyTcpToOfpList ) == 0:
            latencyTcpToOfpList.append( 0 )
            assertion = main.FALSE

        # Calculate min, max, avg of latency lists
        latencyEndToEndMax = \
            int( max( latencyEndToEndList ) )
        latencyEndToEndMin = \
            int( min( latencyEndToEndList ) )
        latencyEndToEndAvg = \
            ( int( sum( latencyEndToEndList ) ) /
              len( latencyEndToEndList ) )
        latencyEndToEndStdDev = \
            str( round( numpy.std( latencyEndToEndList ), 1 ) )

        latencyOfpToGraphMax = \
            int( max( latencyOfpToGraphList ) )
        latencyOfpToGraphMin = \
            int( min( latencyOfpToGraphList ) )
        latencyOfpToGraphAvg = \
            ( int( sum( latencyOfpToGraphList ) ) /
              len( latencyOfpToGraphList ) )
        latencyOfpToGraphStdDev = \
            str( round( numpy.std( latencyOfpToGraphList ), 1 ) )

        latencyOfpToDeviceMax = \
            int( max( latencyOfpToDeviceList ) )
        latencyOfpToDeviceMin = \
            int( min( latencyOfpToDeviceList ) )
        latencyOfpToDeviceAvg = \
            ( int( sum( latencyOfpToDeviceList ) ) /
              len( latencyOfpToDeviceList ) )
        latencyOfpToDeviceStdDev = \
            str( round( numpy.std( latencyOfpToDeviceList ), 1 ) )

        latencyT0ToDeviceMax = \
            int( max( latencyT0ToDeviceList ) )
        latencyT0ToDeviceMin = \
            int( min( latencyT0ToDeviceList ) )
        latencyT0ToDeviceAvg = \
            ( int( sum( latencyT0ToDeviceList ) ) /
              len( latencyT0ToDeviceList ) )
        latencyOfpToDeviceStdDev = \
            str( round( numpy.std( latencyT0ToDeviceList ), 1 ) )

        latencyTcpToOfpMax = \
            int( max( latencyTcpToOfpList ) )
        latencyTcpToOfpMin = \
            int( min( latencyTcpToOfpList ) )
        latencyTcpToOfpAvg = \
            ( int( sum( latencyTcpToOfpList ) ) /
              len( latencyTcpToOfpList ) )
        latencyTcpToOfpStdDev = \
            str( round( numpy.std( latencyTcpToOfpList ), 1 ) )

        main.log.report( "Cluster size: " + str( clusterCount ) +
                         " node(s)" )
        main.log.report( "Switch add - End-to-end latency: " +
                         "Avg: " + str( latencyEndToEndAvg ) + " ms " +
                         "Std Deviation: " + latencyEndToEndStdDev + " ms" )
        main.log.report(
            "Switch add - OFP-to-Graph latency: " +
            "Note: results are not accurate to sub-millisecond. " +
            "Any sub-millisecond results are rounded to 0 ms. " )
        main.log.report( "Avg: " + str( latencyOfpToGraphAvg ) + " ms " +
                         "Std Deviation: " + latencyOfpToGraphStdDev + " ms" )
        main.log.report( "Switch add - TCP-to-OFP latency: " +
                         "Avg: " + str( latencyTcpToOfpAvg ) + " ms " +
                         "Std Deviation: " + latencyTcpToOfpStdDev + " ms" )

        if debugMode == 'on':
            main.ONOS1.cpLogsToDir( "/opt/onos/log/karaf.log",
                                      "/tmp/", copyFileName="sw_lat_karaf" )

        utilities.assert_equals( expect=main.TRUE, actual=assertion,
                                onpass="Switch latency test successful",
                                onfail="Switch latency test failed" )

    def CASE3( self, main ):
        """
        Bring port up / down and measure latency.
        Port enable / disable is simulated by ifconfig up / down

        In ONOS-next, we must ensure that the port we are
        manipulating is connected to another switch with a valid
        connection. Otherwise, graph view will not be updated.
        """
        import time
        import subprocess
        import os
        import requests
        import json
        import numpy
        global clusterCount

        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS2Ip = main.params[ 'CTRL' ][ 'ip2' ]
        ONOS3Ip = main.params[ 'CTRL' ][ 'ip3' ]
        ONOSUser = main.params[ 'CTRL' ][ 'user' ]

        defaultSwPort = main.params[ 'CTRL' ][ 'port1' ]

        assertion = main.TRUE
        # Number of iterations of case
        numIter = main.params[ 'TEST' ][ 'numIter' ]

        # Timestamp 'keys' for json metrics output.
        # These are subject to change, hence moved into params
        deviceTimestamp = main.params[ 'JSON' ][ 'deviceTimestamp' ]
        graphTimestamp = main.params[ 'JSON' ][ 'graphTimestamp' ]

        debugMode = main.params[ 'TEST' ][ 'debugMode' ]

        localTime = time.strftime( '%x %X' )
        localTime = localTime.replace( "/", "" )
        localTime = localTime.replace( " ", "_" )
        localTime = localTime.replace( ":", "" )
        if debugMode == 'on':
            main.ONOS1.tsharkPcap( "eth0",
                                   "/tmp/port_lat_pcap_" + localTime )

        # Threshold for this test case
        upThresholdStr = main.params[ 'TEST' ][ 'portUpThreshold' ]
        downThresholdStr = main.params[ 'TEST' ][ 'portDownThreshold' ]

        upThresholdObj = upThresholdStr.split( "," )
        downThresholdObj = downThresholdStr.split( "," )

        upThresholdMin = int( upThresholdObj[ 0 ] )
        upThresholdMax = int( upThresholdObj[ 1 ] )

        downThresholdMin = int( downThresholdObj[ 0 ] )
        downThresholdMax = int( downThresholdObj[ 1 ] )

        # NOTE: Some hardcoded variables you may need to configure
        #      besides the params

        tsharkPortStatus = "OFP 130 Port Status"

        tsharkPortUp = "/tmp/tshark_port_up.txt"
        tsharkPortDown = "/tmp/tshark_port_down.txt"
        interfaceConfig = "s1-eth1"

        main.log.report( "Port enable / disable latency" )
        main.log.report( "Simulated by ifconfig up / down" )
        main.log.report( "Total iterations of test: " + str( numIter ) )

        main.step( "Assign switches s1 and s2 to controller 1" )
        main.Mininet1.assignSwController( sw="1", ip1=ONOS1Ip,
                                           port1=defaultSwPort )
        main.Mininet1.assignSwController( sw="2", ip1=ONOS1Ip,
                                           port1=defaultSwPort )

        # Give enough time for metrics to propagate the
        # assign controller event. Otherwise, these events may
        # carry over to our measurements
        time.sleep( 15 )

        portUpDeviceToOfpList = []
        portUpGraphToOfpList = []
        portDownDeviceToOfpList = []
        portDownGraphToOfpList = []

        for i in range( 0, int( numIter ) ):
            main.step( "Starting wireshark capture for port status down" )
            main.ONOS1.tsharkGrep( tsharkPortStatus,
                                   tsharkPortDown )

            time.sleep( 5 )

            # Disable interface that is connected to switch 2
            main.step( "Disable port: " + interfaceConfig )
            main.Mininet1.handle.sendline( "sh ifconfig " +
                                           interfaceConfig + " down" )
            main.Mininet1.handle.expect( "mininet>" )

            time.sleep( 3 )
            main.ONOS1.tsharkStop()

            # Copy tshark output file from ONOS to TestON instance
            #/tmp directory
            os.system( "scp " + ONOSUser + "@" + ONOS1Ip + ":" +
                       tsharkPortDown + " /tmp/" )

            fPortDown = open( tsharkPortDown, 'r' )
            # Get first line of port down event from tshark
            fLine = fPortDown.readline()
            objDown = fLine.split( " " )
            if len( fLine ) > 0:
                # NOTE: objDown[ 1 ] is a very unreliable
                #      way to determine the timestamp. If
                #      results seem way off, check the object
                #      itself by printing it out
                timestampBeginPtDown = int( float( objDown[ 1 ] ) * 1000 )
                # For some reason, wireshark decides to record the
                # timestamp at the 3rd object position instead of
                # 2nd at unpredictable times. This statement is
                # used to capture that odd behavior and use the
                # correct epoch time
                if timestampBeginPtDown < 1400000000000:
                    timestampBeginPtDown = \
                        int( float( objDown[ 2 ] ) * 1000 )

                main.log.info( "Port down begin timestamp: " +
                               str( timestampBeginPtDown ) )
            else:
                main.log.info( "Tshark output file returned unexpected" +
                               " results: " + str( objDown ) )
                timestampBeginPtDown = 0
            fPortDown.close()

            main.step( "Obtain t1 by metrics call" )
            jsonStrUp1 = main.ONOS1cli.topologyEventsMetrics()
            jsonObj1 = json.loads( jsonStrUp1 )
            # Obtain graph timestamp. This timestsamp captures
            # the epoch time at which the topology graph was updated.
            graphTimestamp1 = \
                jsonObj1[ graphTimestamp ][ 'value' ]
            # Obtain device timestamp. This timestamp captures
            # the epoch time at which the device event happened
            deviceTimestamp1 = \
                jsonObj1[ deviceTimestamp ][ 'value' ]
            # Get delta between graph event and OFP
            ptDownGraphToOfp1 = int( graphTimestamp1 ) -\
                int( timestampBeginPtDown )
            # Get delta between device event and OFP
            ptDownDeviceToOfp1 = int( deviceTimestamp1 ) -\
                int( timestampBeginPtDown )

            if clusterCount >= 3:
                jsonStrUp2 = main.ONOS2cli.topologyEventsMetrics()
                jsonStrUp3 = main.ONOS3cli.topologyEventsMetrics()
                jsonObj2 = json.loads( jsonStrUp2 )
                jsonObj3 = json.loads( jsonStrUp3 )
                graphTimestamp2 = \
                    jsonObj2[ graphTimestamp ][ 'value' ]
                graphTimestamp3 = \
                    jsonObj3[ graphTimestamp ][ 'value' ]
                deviceTimestamp2 = \
                    jsonObj2[ deviceTimestamp ][ 'value' ]
                deviceTimestamp3 = \
                    jsonObj3[ deviceTimestamp ][ 'value' ]
                ptDownGraphToOfp2 = int( graphTimestamp2 ) -\
                    int( timestampBeginPtDown )
                ptDownGraphToOfp3 = int( graphTimestamp3 ) -\
                    int( timestampBeginPtDown )
                ptDownDeviceToOfp2 = int( deviceTimestamp2 ) -\
                    int( timestampBeginPtDown )
                ptDownDeviceToOfp3 = int( deviceTimestamp3 ) -\
                    int( timestampBeginPtDown )
            else:
                ptDownGraphToOfp2 = 0
                ptDownGraphToOfp3 = 0
                ptDownDeviceToOfp2 = 0
                ptDownDeviceToOfp3 = 0

            if clusterCount >= 5:
                jsonStrUp4 = main.ONOS4cli.topologyEventsMetrics()
                jsonStrUp5 = main.ONOS5cli.topologyEventsMetrics()
                jsonObj4 = json.loads( jsonStrUp4 )
                jsonObj5 = json.loads( jsonStrUp5 )
                graphTimestamp4 = \
                    jsonObj4[ graphTimestamp ][ 'value' ]
                graphTimestamp5 = \
                    jsonObj5[ graphTimestamp ][ 'value' ]
                deviceTimestamp4 = \
                    jsonObj4[ deviceTimestamp ][ 'value' ]
                deviceTimestamp5 = \
                    jsonObj5[ deviceTimestamp ][ 'value' ]
                ptDownGraphToOfp4 = int( graphTimestamp4 ) -\
                    int( timestampBeginPtDown )
                ptDownGraphToOfp5 = int( graphTimestamp5 ) -\
                    int( timestampBeginPtDown )
                ptDownDeviceToOfp4 = int( deviceTimestamp4 ) -\
                    int( timestampBeginPtDown )
                ptDownDeviceToOfp5 = int( deviceTimestamp5 ) -\
                    int( timestampBeginPtDown )
            else:
                ptDownGraphToOfp4 = 0
                ptDownGraphToOfp5 = 0
                ptDownDeviceToOfp4 = 0
                ptDownDeviceToOfp5 = 0

            if clusterCount >= 7:
                jsonStrUp6 = main.ONOS6cli.topologyEventsMetrics()
                jsonStrUp7 = main.ONOS7cli.topologyEventsMetrics()
                jsonObj6 = json.loads( jsonStrUp6 )
                jsonObj7 = json.loads( jsonStrUp7 )
                graphTimestamp6 = \
                    jsonObj6[ graphTimestamp ][ 'value' ]
                graphTimestamp7 = \
                    jsonObj7[ graphTimestamp ][ 'value' ]
                deviceTimestamp6 = \
                    jsonObj6[ deviceTimestamp ][ 'value' ]
                deviceTimestamp7 = \
                    jsonObj7[ deviceTimestamp ][ 'value' ]
                ptDownGraphToOfp6 = int( graphTimestamp6 ) -\
                    int( timestampBeginPtDown )
                ptDownGraphToOfp7 = int( graphTimestamp7 ) -\
                    int( timestampBeginPtDown )
                ptDownDeviceToOfp6 = int( deviceTimestamp6 ) -\
                    int( timestampBeginPtDown )
                ptDownDeviceToOfp7 = int( deviceTimestamp7 ) -\
                    int( timestampBeginPtDown )
            else:
                ptDownGraphToOfp6 = 0
                ptDownGraphToOfp7 = 0
                ptDownDeviceToOfp6 = 0
                ptDownDeviceToOfp7 = 0

            time.sleep( 3 )

            # Caluclate average across clusters
            ptDownGraphToOfpAvg =\
                ( int( ptDownGraphToOfp1 ) +
                  int( ptDownGraphToOfp2 ) +
                  int( ptDownGraphToOfp3 ) +
                  int( ptDownGraphToOfp4 ) +
                  int( ptDownGraphToOfp5 ) +
                  int( ptDownGraphToOfp6 ) +
                  int( ptDownGraphToOfp7 ) ) / clusterCount
            ptDownDeviceToOfpAvg = \
                ( int( ptDownDeviceToOfp1 ) +
                  int( ptDownDeviceToOfp2 ) +
                  int( ptDownDeviceToOfp3 ) +
                  int( ptDownDeviceToOfp4 ) +
                  int( ptDownDeviceToOfp5 ) +
                  int( ptDownDeviceToOfp6 ) +
                  int( ptDownDeviceToOfp7 ) ) / clusterCount

            if ptDownGraphToOfpAvg > downThresholdMin and \
                    ptDownGraphToOfpAvg < downThresholdMax:
                portDownGraphToOfpList.append(
                    ptDownGraphToOfpAvg )
                main.log.info( "Port down: graph to ofp avg: " +
                               str( ptDownGraphToOfpAvg ) + " ms" )
            else:
                main.log.info( "Average port down graph-to-ofp result" +
                               " exceeded the threshold: " +
                               str( ptDownGraphToOfpAvg ) )

            if ptDownDeviceToOfpAvg > 0 and \
                    ptDownDeviceToOfpAvg < 1000:
                portDownDeviceToOfpList.append(
                    ptDownDeviceToOfpAvg )
                main.log.info( "Port down: device to ofp avg: " +
                               str( ptDownDeviceToOfpAvg ) + " ms" )
            else:
                main.log.info( "Average port down device-to-ofp result" +
                               " exceeded the threshold: " +
                               str( ptDownDeviceToOfpAvg ) )

            # Port up events
            main.step( "Enable port and obtain timestamp" )
            main.step( "Starting wireshark capture for port status up" )
            main.ONOS1.tsharkGrep( tsharkPortStatus, tsharkPortUp )
            time.sleep( 5 )

            main.Mininet1.handle.sendline( "sh ifconfig " +
                                           interfaceConfig + " up" )
            main.Mininet1.handle.expect( "mininet>" )

            # Allow time for tshark to capture event
            time.sleep( 5 )
            main.ONOS1.tsharkStop()

            time.sleep( 3 )
            os.system( "scp " + ONOSUser + "@" + ONOS1Ip + ":" +
                       tsharkPortUp + " /tmp/" )
            fPortUp = open( tsharkPortUp, 'r' )
            fLine = fPortUp.readline()
            objUp = fLine.split( " " )
            if len( fLine ) > 0:
                timestampBeginPtUp = int( float( objUp[ 1 ] ) * 1000 )
                if timestampBeginPtUp < 1400000000000:
                    timestampBeginPtUp = \
                        int( float( objUp[ 2 ] ) * 1000 )
                main.log.info( "Port up begin timestamp: " +
                               str( timestampBeginPtUp ) )
            else:
                main.log.info( "Tshark output file returned unexpected" +
                               " results." )
                timestampBeginPtUp = 0
            fPortUp.close()

            # Obtain metrics shortly afterwards
            # This timestsamp captures
            # the epoch time at which the topology graph was updated.
            main.step( "Obtain t1 by REST call" )
            jsonStrUp1 = main.ONOS1cli.topologyEventsMetrics()
            jsonObj1 = json.loads( jsonStrUp1 )
            graphTimestamp1 = \
                jsonObj1[ graphTimestamp ][ 'value' ]
            # Obtain device timestamp. This timestamp captures
            # the epoch time at which the device event happened
            deviceTimestamp1 = \
                jsonObj1[ deviceTimestamp ][ 'value' ]
            # Get delta between graph event and OFP
            ptUpGraphToOfp1 = int( graphTimestamp1 ) -\
                int( timestampBeginPtUp )
            # Get delta between device event and OFP
            ptUpDeviceToOfp1 = int( deviceTimestamp1 ) -\
                int( timestampBeginPtUp )

            if clusterCount >= 3:
                jsonStrUp2 = main.ONOS2cli.topologyEventsMetrics()
                jsonStrUp3 = main.ONOS3cli.topologyEventsMetrics()
                jsonObj2 = json.loads( jsonStrUp2 )
                jsonObj3 = json.loads( jsonStrUp3 )
                graphTimestamp2 = \
                    jsonObj2[ graphTimestamp ][ 'value' ]
                graphTimestamp3 = \
                    jsonObj3[ graphTimestamp ][ 'value' ]
                deviceTimestamp2 = \
                    jsonObj2[ deviceTimestamp ][ 'value' ]
                deviceTimestamp3 = \
                    jsonObj3[ deviceTimestamp ][ 'value' ]
                ptUpGraphToOfp2 = int( graphTimestamp2 ) -\
                    int( timestampBeginPtUp )
                ptUpGraphToOfp3 = int( graphTimestamp3 ) -\
                    int( timestampBeginPtUp )
                ptUpDeviceToOfp2 = int( deviceTimestamp2 ) -\
                    int( timestampBeginPtUp )
                ptUpDeviceToOfp3 = int( deviceTimestamp3 ) -\
                    int( timestampBeginPtUp )
            else:
                ptUpGraphToOfp2 = 0
                ptUpGraphToOfp3 = 0
                ptUpDeviceToOfp2 = 0
                ptUpDeviceToOfp3 = 0

            if clusterCount >= 5:
                jsonStrUp4 = main.ONOS4cli.topologyEventsMetrics()
                jsonStrUp5 = main.ONOS5cli.topologyEventsMetrics()
                jsonObj4 = json.loads( jsonStrUp4 )
                jsonObj5 = json.loads( jsonStrUp5 )
                graphTimestamp4 = \
                    jsonObj4[ graphTimestamp ][ 'value' ]
                graphTimestamp5 = \
                    jsonObj5[ graphTimestamp ][ 'value' ]
                deviceTimestamp4 = \
                    jsonObj4[ deviceTimestamp ][ 'value' ]
                deviceTimestamp5 = \
                    jsonObj5[ deviceTimestamp ][ 'value' ]
                ptUpGraphToOfp4 = int( graphTimestamp4 ) -\
                    int( timestampBeginPtUp )
                ptUpGraphToOfp5 = int( graphTimestamp5 ) -\
                    int( timestampBeginPtUp )
                ptUpDeviceToOfp4 = int( deviceTimestamp4 ) -\
                    int( timestampBeginPtUp )
                ptUpDeviceToOfp5 = int( deviceTimestamp5 ) -\
                    int( timestampBeginPtUp )
            else:
                ptUpGraphToOfp4 = 0
                ptUpGraphToOfp5 = 0
                ptUpDeviceToOfp4 = 0
                ptUpDeviceToOfp5 = 0

            if clusterCount >= 7:
                jsonStrUp6 = main.ONOS6cli.topologyEventsMetrics()
                jsonStrUp7 = main.ONOS7cli.topologyEventsMetrics()
                jsonObj6 = json.loads( jsonStrUp6 )
                jsonObj7 = json.loads( jsonStrUp7 )
                graphTimestamp6 = \
                    jsonObj6[ graphTimestamp ][ 'value' ]
                graphTimestamp7 = \
                    jsonObj7[ graphTimestamp ][ 'value' ]
                deviceTimestamp6 = \
                    jsonObj6[ deviceTimestamp ][ 'value' ]
                deviceTimestamp7 = \
                    jsonObj7[ deviceTimestamp ][ 'value' ]
                ptUpGraphToOfp6 = int( graphTimestamp6 ) -\
                    int( timestampBeginPtUp )
                ptUpGraphToOfp7 = int( graphTimestamp7 ) -\
                    int( timestampBeginPtUp )
                ptUpDeviceToOfp6 = int( deviceTimestamp6 ) -\
                    int( timestampBeginPtUp )
                ptUpDeviceToOfp7 = int( deviceTimestamp7 ) -\
                    int( timestampBeginPtUp )
            else:
                ptUpGraphToOfp6 = 0
                ptUpGraphToOfp7 = 0
                ptUpDeviceToOfp6 = 0
                ptUpDeviceToOfp7 = 0

            ptUpGraphToOfpAvg = \
                ( int( ptUpGraphToOfp1 ) +
                  int( ptUpGraphToOfp2 ) +
                  int( ptUpGraphToOfp3 ) +
                  int( ptUpGraphToOfp4 ) +
                  int( ptUpGraphToOfp5 ) +
                  int( ptUpGraphToOfp6 ) +
                  int( ptUpGraphToOfp7 ) ) / clusterCount

            ptUpDeviceToOfpAvg = \
                ( int( ptUpDeviceToOfp1 ) +
                  int( ptUpDeviceToOfp2 ) +
                  int( ptUpDeviceToOfp3 ) +
                  int( ptUpDeviceToOfp4 ) +
                  int( ptUpDeviceToOfp5 ) +
                  int( ptUpDeviceToOfp6 ) +
                  int( ptUpDeviceToOfp7 ) ) / clusterCount

            if ptUpGraphToOfpAvg > upThresholdMin and \
                    ptUpGraphToOfpAvg < upThresholdMax:
                portUpGraphToOfpList.append(
                    ptUpGraphToOfpAvg )
                main.log.info( "Port down: graph to ofp avg: " +
                               str( ptUpGraphToOfpAvg ) + " ms" )
            else:
                main.log.info( "Average port up graph-to-ofp result" +
                               " exceeded the threshold: " +
                               str( ptUpGraphToOfpAvg ) )

            if ptUpDeviceToOfpAvg > upThresholdMin and \
                    ptUpDeviceToOfpAvg < upThresholdMax:
                portUpDeviceToOfpList.append(
                    ptUpDeviceToOfpAvg )
                main.log.info( "Port up: device to ofp avg: " +
                               str( ptUpDeviceToOfpAvg ) + " ms" )
            else:
                main.log.info( "Average port up device-to-ofp result" +
                               " exceeded the threshold: " +
                               str( ptUpDeviceToOfpAvg ) )

            # END ITERATION FOR LOOP

        # Check all list for latency existence and set assertion
        if ( portDownGraphToOfpList and portDownDeviceToOfpList
                and portUpGraphToOfpList and portUpDeviceToOfpList ):
            assertion = main.TRUE

        main.log.report( "Cluster size: " + str( clusterCount ) +
                         " node(s)" )
        # Calculate and report latency measurements
        portDownGraphToOfpMin = min( portDownGraphToOfpList )
        portDownGraphToOfpMax = max( portDownGraphToOfpList )
        portDownGraphToOfpAvg = \
            ( sum( portDownGraphToOfpList ) /
              len( portDownGraphToOfpList ) )
        portDownGraphToOfpStdDev = \
            str( round( numpy.std( portDownGraphToOfpList ), 1 ) )

        main.log.report( "Port down graph-to-ofp " +
                         "Avg: " + str( portDownGraphToOfpAvg ) + " ms " +
                         "Std Deviation: " + portDownGraphToOfpStdDev + " ms" )

        portDownDeviceToOfpMin = min( portDownDeviceToOfpList )
        portDownDeviceToOfpMax = max( portDownDeviceToOfpList )
        portDownDeviceToOfpAvg = \
            ( sum( portDownDeviceToOfpList ) /
              len( portDownDeviceToOfpList ) )
        portDownDeviceToOfpStdDev = \
            str( round( numpy.std( portDownDeviceToOfpList ), 1 ) )

        main.log.report(
            "Port down device-to-ofp " +
            "Avg: " +
            str( portDownDeviceToOfpAvg ) +
            " ms " +
            "Std Deviation: " +
            portDownDeviceToOfpStdDev +
            " ms" )

        portUpGraphToOfpMin = min( portUpGraphToOfpList )
        portUpGraphToOfpMax = max( portUpGraphToOfpList )
        portUpGraphToOfpAvg = \
            ( sum( portUpGraphToOfpList ) /
              len( portUpGraphToOfpList ) )
        portUpGraphToOfpStdDev = \
            str( round( numpy.std( portUpGraphToOfpList ), 1 ) )

        main.log.report( "Port up graph-to-ofp " +
                         "Avg: " + str( portUpGraphToOfpAvg ) + " ms " +
                         "Std Deviation: " + portUpGraphToOfpStdDev + " ms" )

        portUpDeviceToOfpMin = min( portUpDeviceToOfpList )
        portUpDeviceToOfpMax = max( portUpDeviceToOfpList )
        portUpDeviceToOfpAvg = \
            ( sum( portUpDeviceToOfpList ) /
              len( portUpDeviceToOfpList ) )
        portUpDeviceToOfpStdDev = \
            str( round( numpy.std( portUpDeviceToOfpList ), 1 ) )

        main.log.report( "Port up device-to-ofp " +
                         "Avg: " + str( portUpDeviceToOfpAvg ) + " ms " +
                         "Std Deviation: " + portUpDeviceToOfpStdDev + " ms" )

        # Remove switches from controller for next test
        main.Mininet1.deleteSwController( "s1" )
        main.Mininet1.deleteSwController( "s2" )

        utilities.assert_equals(
            expect=main.TRUE,
            actual=assertion,
            onpass="Port discovery latency calculation successful",
            onfail="Port discovery test failed" )

    def CASE4( self, main ):
        """
        Link down event using loss rate 100%

        Important:
            Use a simple 2 switch topology with 1 link between
            the two switches. Ensure that mac addresses of the
            switches are 1 / 2 respectively
        """
        import time
        import subprocess
        import os
        import requests
        import json
        import numpy

        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS2Ip = main.params[ 'CTRL' ][ 'ip2' ]
        ONOS3Ip = main.params[ 'CTRL' ][ 'ip3' ]
        ONOSUser = main.params[ 'CTRL' ][ 'user' ]

        defaultSwPort = main.params[ 'CTRL' ][ 'port1' ]

        # Number of iterations of case
        numIter = main.params[ 'TEST' ][ 'numIter' ]

        # Timestamp 'keys' for json metrics output.
        # These are subject to change, hence moved into params
        deviceTimestamp = main.params[ 'JSON' ][ 'deviceTimestamp' ]
        linkTimestamp = main.params[ 'JSON' ][ 'linkTimestamp' ]
        graphTimestamp = main.params[ 'JSON' ][ 'graphTimestamp' ]

        debugMode = main.params[ 'TEST' ][ 'debugMode' ]

        localTime = time.strftime( '%x %X' )
        localTime = localTime.replace( "/", "" )
        localTime = localTime.replace( " ", "_" )
        localTime = localTime.replace( ":", "" )
        if debugMode == 'on':
            main.ONOS1.tsharkPcap( "eth0",
                                   "/tmp/link_lat_pcap_" + localTime )

        # Threshold for this test case
        upThresholdStr = main.params[ 'TEST' ][ 'linkUpThreshold' ]
        downThresholdStr = main.params[ 'TEST' ][ 'linkDownThreshold' ]

        upThresholdObj = upThresholdStr.split( "," )
        downThresholdObj = downThresholdStr.split( "," )

        upThresholdMin = int( upThresholdObj[ 0 ] )
        upThresholdMax = int( upThresholdObj[ 1 ] )

        downThresholdMin = int( downThresholdObj[ 0 ] )
        downThresholdMax = int( downThresholdObj[ 1 ] )

        assertion = main.TRUE
        # Link event timestamp to system time list
        linkDownLinkToSystemList = []
        linkUpLinkToSystemList = []
        # Graph event timestamp to system time list
        linkDownGraphToSystemList = []
        linkUpGraphToSystemList = []

        main.log.report( "Link up / down discovery latency between " +
                         "two switches" )
        main.log.report( "Simulated by setting loss-rate 100%" )
        main.log.report( "'tc qdisc add dev <intfs> root netem loss 100%'" )
        main.log.report( "Total iterations of test: " + str( numIter ) )

        main.step( "Assign all switches" )
        main.Mininet1.assignSwController( sw="1",
                                           ip1=ONOS1Ip, port1=defaultSwPort )
        main.Mininet1.assignSwController( sw="2",
                                           ip1=ONOS1Ip, port1=defaultSwPort )

        main.step( "Verifying switch assignment" )
        resultS1 = main.Mininet1.getSwController( sw="s1" )
        resultS2 = main.Mininet1.getSwController( sw="s2" )

        # Allow time for events to finish before taking measurements
        time.sleep( 10 )

        linkDown1 = False
        linkDown2 = False
        linkDown3 = False
        # Start iteration of link event test
        for i in range( 0, int( numIter ) ):
            main.step( "Getting initial system time as t0" )

            # System time in epoch ms
            timestampLinkDownT0 = time.time() * 1000
            # Link down is simulated by 100% loss rate using traffic
            # control command
            main.Mininet1.handle.sendline(
                "sh tc qdisc add dev s1-eth1 root netem loss 100%" )

            # TODO: Iterate through 'links' command to verify that
            #      link s1 -> s2 went down ( loop timeout 30 seconds )
            #      on all 3 ONOS instances
            main.log.info( "Checking ONOS for link update" )
            loopCount = 0
            while( not ( linkDown1 and linkDown2 and linkDown3 )
                    and loopCount < 30 ):
                jsonStr1 = main.ONOS1cli.links()
                jsonStr2 = main.ONOS2cli.links()
                jsonStr3 = main.ONOS3cli.links()

                if not ( jsonStr1 and jsonStr2 and jsonStr3 ):
                    main.log.error( "CLI command returned error " )
                    break
                else:
                    jsonObj1 = json.loads( jsonStr1 )
                    jsonObj2 = json.loads( jsonStr2 )
                    jsonObj3 = json.loads( jsonStr3 )
                for obj1 in jsonObj1:
                    if '01' not in obj1[ 'src' ][ 'device' ]:
                        linkDown1 = True
                        main.log.info( "Link down from " +
                                       "s1 -> s2 on ONOS1 detected" )
                for obj2 in jsonObj2:
                    if '01' not in obj2[ 'src' ][ 'device' ]:
                        linkDown2 = True
                        main.log.info( "Link down from " +
                                       "s1 -> s2 on ONOS2 detected" )
                for obj3 in jsonObj3:
                    if '01' not in obj3[ 'src' ][ 'device' ]:
                        linkDown3 = True
                        main.log.info( "Link down from " +
                                       "s1 -> s2 on ONOS3 detected" )

                loopCount += 1
                # If CLI doesn't like the continuous requests
                # and exits in this loop, increase the sleep here.
                # Consequently, while loop timeout will increase
                time.sleep( 1 )

            # Give time for metrics measurement to catch up
            # NOTE: May need to be configured more accurately
            time.sleep( 10 )
            # If we exited the while loop and link down 1,2,3 are still
            # false, then ONOS has failed to discover link down event
            if not ( linkDown1 and linkDown2 and linkDown3 ):
                main.log.info( "Link down discovery failed" )

                linkDownLatGraph1 = 0
                linkDownLatGraph2 = 0
                linkDownLatGraph3 = 0
                linkDownLatDevice1 = 0
                linkDownLatDevice2 = 0
                linkDownLatDevice3 = 0

                assertion = main.FALSE
            else:
                jsonTopoMetrics1 =\
                    main.ONOS1cli.topologyEventsMetrics()
                jsonTopoMetrics2 =\
                    main.ONOS2cli.topologyEventsMetrics()
                jsonTopoMetrics3 =\
                    main.ONOS3cli.topologyEventsMetrics()
                jsonTopoMetrics1 = json.loads( jsonTopoMetrics1 )
                jsonTopoMetrics2 = json.loads( jsonTopoMetrics2 )
                jsonTopoMetrics3 = json.loads( jsonTopoMetrics3 )

                main.log.info( "Obtaining graph and device timestamp" )
                graphTimestamp1 = \
                    jsonTopoMetrics1[ graphTimestamp ][ 'value' ]
                graphTimestamp2 = \
                    jsonTopoMetrics2[ graphTimestamp ][ 'value' ]
                graphTimestamp3 = \
                    jsonTopoMetrics3[ graphTimestamp ][ 'value' ]

                linkTimestamp1 = \
                    jsonTopoMetrics1[ linkTimestamp ][ 'value' ]
                linkTimestamp2 = \
                    jsonTopoMetrics2[ linkTimestamp ][ 'value' ]
                linkTimestamp3 = \
                    jsonTopoMetrics3[ linkTimestamp ][ 'value' ]

                if graphTimestamp1 and graphTimestamp2 and\
                        graphTimestamp3 and linkTimestamp1 and\
                        linkTimestamp2 and linkTimestamp3:
                    linkDownLatGraph1 = int( graphTimestamp1 ) -\
                        int( timestampLinkDownT0 )
                    linkDownLatGraph2 = int( graphTimestamp2 ) -\
                        int( timestampLinkDownT0 )
                    linkDownLatGraph3 = int( graphTimestamp3 ) -\
                        int( timestampLinkDownT0 )

                    linkDownLatLink1 = int( linkTimestamp1 ) -\
                        int( timestampLinkDownT0 )
                    linkDownLatLink2 = int( linkTimestamp2 ) -\
                        int( timestampLinkDownT0 )
                    linkDownLatLink3 = int( linkTimestamp3 ) -\
                        int( timestampLinkDownT0 )
                else:
                    main.log.error( "There was an error calculating" +
                                    " the delta for link down event" )
                    linkDownLatGraph1 = 0
                    linkDownLatGraph2 = 0
                    linkDownLatGraph3 = 0

                    linkDownLatDevice1 = 0
                    linkDownLatDevice2 = 0
                    linkDownLatDevice3 = 0

            main.log.info( "Link down latency ONOS1 iteration " +
                           str( i ) + " (end-to-end): " +
                           str( linkDownLatGraph1 ) + " ms" )
            main.log.info( "Link down latency ONOS2 iteration " +
                           str( i ) + " (end-to-end): " +
                           str( linkDownLatGraph2 ) + " ms" )
            main.log.info( "Link down latency ONOS3 iteration " +
                           str( i ) + " (end-to-end): " +
                           str( linkDownLatGraph3 ) + " ms" )

            main.log.info( "Link down latency ONOS1 iteration " +
                           str( i ) + " (link-event-to-system-timestamp): " +
                           str( linkDownLatLink1 ) + " ms" )
            main.log.info( "Link down latency ONOS2 iteration " +
                           str( i ) + " (link-event-to-system-timestamp): " +
                           str( linkDownLatLink2 ) + " ms" )
            main.log.info( "Link down latency ONOS3 iteration " +
                           str( i ) + " (link-event-to-system-timestamp): " +
                           str( linkDownLatLink3 ) )

            # Calculate avg of node calculations
            linkDownLatGraphAvg =\
                ( linkDownLatGraph1 +
                  linkDownLatGraph2 +
                  linkDownLatGraph3 ) / 3
            linkDownLatLinkAvg =\
                ( linkDownLatLink1 +
                  linkDownLatLink2 +
                  linkDownLatLink3 ) / 3

            # Set threshold and append latency to list
            if linkDownLatGraphAvg > downThresholdMin and\
               linkDownLatGraphAvg < downThresholdMax:
                linkDownGraphToSystemList.append(
                    linkDownLatGraphAvg )
            else:
                main.log.info( "Link down latency exceeded threshold" )
                main.log.info( "Results for iteration " + str( i ) +
                               "have been omitted" )
            if linkDownLatLinkAvg > downThresholdMin and\
               linkDownLatLinkAvg < downThresholdMax:
                linkDownLinkToSystemList.append(
                    linkDownLatLinkAvg )
            else:
                main.log.info( "Link down latency exceeded threshold" )
                main.log.info( "Results for iteration " + str( i ) +
                               "have been omitted" )

            # NOTE: To remove loss rate and measure latency:
            #       'sh tc qdisc del dev s1-eth1 root'
            timestampLinkUpT0 = time.time() * 1000
            main.Mininet1.handle.sendline( "sh tc qdisc del dev " +
                                           "s1-eth1 root" )
            main.Mininet1.handle.expect( "mininet>" )

            main.log.info( "Checking ONOS for link update" )

            linkDown1 = True
            linkDown2 = True
            linkDown3 = True
            loopCount = 0
            while( ( linkDown1 and linkDown2 and linkDown3 )
                    and loopCount < 30 ):
                jsonStr1 = main.ONOS1cli.links()
                jsonStr2 = main.ONOS2cli.links()
                jsonStr3 = main.ONOS3cli.links()
                if not ( jsonStr1 and jsonStr2 and jsonStr3 ):
                    main.log.error( "CLI command returned error " )
                    break
                else:
                    jsonObj1 = json.loads( jsonStr1 )
                    jsonObj2 = json.loads( jsonStr2 )
                    jsonObj3 = json.loads( jsonStr3 )

                for obj1 in jsonObj1:
                    if '01' in obj1[ 'src' ][ 'device' ]:
                        linkDown1 = False
                        main.log.info( "Link up from " +
                                       "s1 -> s2 on ONOS1 detected" )
                for obj2 in jsonObj2:
                    if '01' in obj2[ 'src' ][ 'device' ]:
                        linkDown2 = False
                        main.log.info( "Link up from " +
                                       "s1 -> s2 on ONOS2 detected" )
                for obj3 in jsonObj3:
                    if '01' in obj3[ 'src' ][ 'device' ]:
                        linkDown3 = False
                        main.log.info( "Link up from " +
                                       "s1 -> s2 on ONOS3 detected" )

                loopCount += 1
                time.sleep( 1 )

            if ( linkDown1 and linkDown2 and linkDown3 ):
                main.log.info( "Link up discovery failed" )

                linkUpLatGraph1 = 0
                linkUpLatGraph2 = 0
                linkUpLatGraph3 = 0
                linkUpLatDevice1 = 0
                linkUpLatDevice2 = 0
                linkUpLatDevice3 = 0

                assertion = main.FALSE
            else:
                jsonTopoMetrics1 =\
                    main.ONOS1cli.topologyEventsMetrics()
                jsonTopoMetrics2 =\
                    main.ONOS2cli.topologyEventsMetrics()
                jsonTopoMetrics3 =\
                    main.ONOS3cli.topologyEventsMetrics()
                jsonTopoMetrics1 = json.loads( jsonTopoMetrics1 )
                jsonTopoMetrics2 = json.loads( jsonTopoMetrics2 )
                jsonTopoMetrics3 = json.loads( jsonTopoMetrics3 )

                main.log.info( "Obtaining graph and device timestamp" )
                graphTimestamp1 = \
                    jsonTopoMetrics1[ graphTimestamp ][ 'value' ]
                graphTimestamp2 = \
                    jsonTopoMetrics2[ graphTimestamp ][ 'value' ]
                graphTimestamp3 = \
                    jsonTopoMetrics3[ graphTimestamp ][ 'value' ]

                linkTimestamp1 = \
                    jsonTopoMetrics1[ linkTimestamp ][ 'value' ]
                linkTimestamp2 = \
                    jsonTopoMetrics2[ linkTimestamp ][ 'value' ]
                linkTimestamp3 = \
                    jsonTopoMetrics3[ linkTimestamp ][ 'value' ]

                if graphTimestamp1 and graphTimestamp2 and\
                        graphTimestamp3 and linkTimestamp1 and\
                        linkTimestamp2 and linkTimestamp3:
                    linkUpLatGraph1 = int( graphTimestamp1 ) -\
                        int( timestampLinkUpT0 )
                    linkUpLatGraph2 = int( graphTimestamp2 ) -\
                        int( timestampLinkUpT0 )
                    linkUpLatGraph3 = int( graphTimestamp3 ) -\
                        int( timestampLinkUpT0 )

                    linkUpLatLink1 = int( linkTimestamp1 ) -\
                        int( timestampLinkUpT0 )
                    linkUpLatLink2 = int( linkTimestamp2 ) -\
                        int( timestampLinkUpT0 )
                    linkUpLatLink3 = int( linkTimestamp3 ) -\
                        int( timestampLinkUpT0 )
                else:
                    main.log.error( "There was an error calculating" +
                                    " the delta for link down event" )
                    linkUpLatGraph1 = 0
                    linkUpLatGraph2 = 0
                    linkUpLatGraph3 = 0

                    linkUpLatDevice1 = 0
                    linkUpLatDevice2 = 0
                    linkUpLatDevice3 = 0

            if debugMode == 'on':
                main.log.info( "Link up latency ONOS1 iteration " +
                               str( i ) + " (end-to-end): " +
                               str( linkUpLatGraph1 ) + " ms" )
                main.log.info( "Link up latency ONOS2 iteration " +
                               str( i ) + " (end-to-end): " +
                               str( linkUpLatGraph2 ) + " ms" )
                main.log.info( "Link up latency ONOS3 iteration " +
                               str( i ) + " (end-to-end): " +
                               str( linkUpLatGraph3 ) + " ms" )

                main.log.info(
                    "Link up latency ONOS1 iteration " +
                    str( i ) +
                    " (link-event-to-system-timestamp): " +
                    str( linkUpLatLink1 ) +
                    " ms" )
                main.log.info(
                    "Link up latency ONOS2 iteration " +
                    str( i ) +
                    " (link-event-to-system-timestamp): " +
                    str( linkUpLatLink2 ) +
                    " ms" )
                main.log.info(
                    "Link up latency ONOS3 iteration " +
                    str( i ) +
                    " (link-event-to-system-timestamp): " +
                    str( linkUpLatLink3 ) )

            # Calculate avg of node calculations
            linkUpLatGraphAvg =\
                ( linkUpLatGraph1 +
                  linkUpLatGraph2 +
                  linkUpLatGraph3 ) / 3
            linkUpLatLinkAvg =\
                ( linkUpLatLink1 +
                  linkUpLatLink2 +
                  linkUpLatLink3 ) / 3

            # Set threshold and append latency to list
            if linkUpLatGraphAvg > upThresholdMin and\
               linkUpLatGraphAvg < upThresholdMax:
                linkUpGraphToSystemList.append(
                    linkUpLatGraphAvg )
            else:
                main.log.info( "Link up latency exceeded threshold" )
                main.log.info( "Results for iteration " + str( i ) +
                               "have been omitted" )
            if linkUpLatLinkAvg > upThresholdMin and\
               linkUpLatLinkAvg < upThresholdMax:
                linkUpLinkToSystemList.append(
                    linkUpLatLinkAvg )
            else:
                main.log.info( "Link up latency exceeded threshold" )
                main.log.info( "Results for iteration " + str( i ) +
                               "have been omitted" )

        # Calculate min, max, avg of list and report
        linkDownMin = min( linkDownGraphToSystemList )
        linkDownMax = max( linkDownGraphToSystemList )
        linkDownAvg = sum( linkDownGraphToSystemList ) / \
            len( linkDownGraphToSystemList )
        linkUpMin = min( linkUpGraphToSystemList )
        linkUpMax = max( linkUpGraphToSystemList )
        linkUpAvg = sum( linkUpGraphToSystemList ) / \
            len( linkUpGraphToSystemList )
        linkDownStdDev = \
            str( round( numpy.std( linkDownGraphToSystemList ), 1 ) )
        linkUpStdDev = \
            str( round( numpy.std( linkUpGraphToSystemList ), 1 ) )

        main.log.report( "Link down latency " +
                         "Avg: " + str( linkDownAvg ) + " ms " +
                         "Std Deviation: " + linkDownStdDev + " ms" )
        main.log.report( "Link up latency " +
                         "Avg: " + str( linkUpAvg ) + " ms " +
                         "Std Deviation: " + linkUpStdDev + " ms" )

        utilities.assert_equals(
            expect=main.TRUE,
            actual=assertion,
            onpass="Link discovery latency calculation successful",
            onfail="Link discovery latency case failed" )

    def CASE5( self, main ):
        """
        100 Switch discovery latency

        Important:
            This test case can be potentially dangerous if
            your machine has previously set iptables rules.
            One of the steps of the test case will flush
            all existing iptables rules.
        Note:
            You can specify the number of switches in the
            params file to adjust the switch discovery size
            ( and specify the corresponding topology in Mininet1
            .topo file )
        """
        import time
        import subprocess
        import os
        import requests
        import json

        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS2Ip = main.params[ 'CTRL' ][ 'ip2' ]
        ONOS3Ip = main.params[ 'CTRL' ][ 'ip3' ]
        MN1Ip = main.params[ 'MN' ][ 'ip1' ]
        ONOSUser = main.params[ 'CTRL' ][ 'user' ]

        defaultSwPort = main.params[ 'CTRL' ][ 'port1' ]

        # Number of iterations of case
        numIter = main.params[ 'TEST' ][ 'numIter' ]
        numSw = main.params[ 'TEST' ][ 'numSwitch' ]

        # Timestamp 'keys' for json metrics output.
        # These are subject to change, hence moved into params
        deviceTimestamp = main.params[ 'JSON' ][ 'deviceTimestamp' ]
        graphTimestamp = main.params[ 'JSON' ][ 'graphTimestamp' ]

        debugMode = main.params[ 'TEST' ][ 'debugMode' ]

        localTime = time.strftime( '%X' )
        localTime = localTime.replace( "/", "" )
        localTime = localTime.replace( " ", "_" )
        localTime = localTime.replace( ":", "" )
        if debugMode == 'on':
            main.ONOS1.tsharkPcap( "eth0",
                                   "/tmp/100_sw_lat_pcap_" + localTime )

        # Threshold for this test case
        swDiscThresholdStr = main.params[ 'TEST' ][ 'swDisc100Threshold' ]
        swDiscThresholdObj = swDiscThresholdStr.split( "," )
        swDiscThresholdMin = int( swDiscThresholdObj[ 0 ] )
        swDiscThresholdMax = int( swDiscThresholdObj[ 1 ] )

        tsharkOfpOutput = "/tmp/tshark_ofp_" + numSw + "sw.txt"
        tsharkTcpOutput = "/tmp/tshark_tcp_" + numSw + "sw.txt"

        tsharkOfpResultList = []
        tsharkTcpResultList = []

        swDiscoveryLatList = []

        main.case( numSw + " Switch discovery latency" )
        main.step( "Assigning all switches to ONOS1" )
        for i in range( 1, int( numSw ) + 1 ):
            main.Mininet1.assignSwController(
                sw=str( i ),
                ip1=ONOS1Ip,
                port1=defaultSwPort )

        # Ensure that nodes are configured with ptpd
        # Just a warning message
        main.log.info( "Please check ptpd configuration to ensure" +
                       " All nodes' system times are in sync" )
        time.sleep( 5 )

        for i in range( 0, int( numIter ) ):

            main.step( "Set iptables rule to block incoming sw connections" )
            # Set iptables rule to block incoming switch connections
            # The rule description is as follows:
            #   Append to INPUT rule,
            #   behavior DROP that matches following:
            #       * packet type: tcp
            #       * source IP: MN1Ip
            #       * destination PORT: 6633
            main.ONOS1.handle.sendline(
                "sudo iptables -A INPUT -p tcp -s " + MN1Ip +
                " --dport " + defaultSwPort + " -j DROP" )
            main.ONOS1.handle.expect( "\$" )
            #   Append to OUTPUT rule,
            #   behavior DROP that matches following:
            #       * packet type: tcp
            #       * source IP: MN1Ip
            #       * destination PORT: 6633
            main.ONOS1.handle.sendline(
                "sudo iptables -A OUTPUT -p tcp -s " + MN1Ip +
                " --dport " + defaultSwPort + " -j DROP" )
            main.ONOS1.handle.expect( "\$" )
            # Give time to allow rule to take effect
            # NOTE: Sleep period may need to be configured
            #      based on the number of switches in the topology
            main.log.info( "Please wait for switch connection to " +
                           "time out" )
            time.sleep( 60 )

            # Gather vendor OFP with tshark
            main.ONOS1.tsharkGrep( "OFP 86 Vendor",
                                   tsharkOfpOutput )
            main.ONOS1.tsharkGrep( "TCP 74 ",
                                   tsharkTcpOutput )

            # NOTE: Remove all iptables rule quickly ( flush )
            #      Before removal, obtain TestON timestamp at which
            #      removal took place
            #      ( ensuring nodes are configured via ptp )
            #      sudo iptables -F

            t0System = time.time() * 1000
            main.ONOS1.handle.sendline(
                "sudo iptables -F" )

            # Counter to track loop count
            counterLoop = 0
            counterAvail1 = 0
            counterAvail2 = 0
            counterAvail3 = 0
            onos1Dev = False
            onos2Dev = False
            onos3Dev = False
            while counterLoop < 60:
                # Continue to check devices for all device
                # availability. When all devices in all 3
                # ONOS instances indicate that devices are available
                # obtain graph event timestamp for t1.
                deviceStrObj1 = main.ONOS1cli.devices()
                deviceStrObj2 = main.ONOS2cli.devices()
                deviceStrObj3 = main.ONOS3cli.devices()

                deviceJson1 = json.loads( deviceStrObj1 )
                deviceJson2 = json.loads( deviceStrObj2 )
                deviceJson3 = json.loads( deviceStrObj3 )

                for device1 in deviceJson1:
                    if device1[ 'available' ]:
                        counterAvail1 += 1
                        if counterAvail1 == int( numSw ):
                            onos1Dev = True
                            main.log.info( "All devices have been " +
                                           "discovered on ONOS1" )
                    else:
                        counterAvail1 = 0
                for device2 in deviceJson2:
                    if device2[ 'available' ]:
                        counterAvail2 += 1
                        if counterAvail2 == int( numSw ):
                            onos2Dev = True
                            main.log.info( "All devices have been " +
                                           "discovered on ONOS2" )
                    else:
                        counterAvail2 = 0
                for device3 in deviceJson3:
                    if device3[ 'available' ]:
                        counterAvail3 += 1
                        if counterAvail3 == int( numSw ):
                            onos3Dev = True
                            main.log.info( "All devices have been " +
                                           "discovered on ONOS3" )
                    else:
                        counterAvail3 = 0

                if onos1Dev and onos2Dev and onos3Dev:
                    main.log.info( "All devices have been discovered " +
                                   "on all ONOS instances" )
                    jsonStrTopologyMetrics1 =\
                        main.ONOS1cli.topologyEventsMetrics()
                    jsonStrTopologyMetrics2 =\
                        main.ONOS2cli.topologyEventsMetrics()
                    jsonStrTopologyMetrics3 =\
                        main.ONOS3cli.topologyEventsMetrics()

                    # Exit while loop if all devices discovered
                    break

                counterLoop += 1
                # Give some time in between CLI calls
                #( will not affect measurement )
                time.sleep( 3 )

            main.ONOS1.tsharkStop()

            os.system( "scp " + ONOSUser + "@" + ONOS1Ip + ":" +
                       tsharkOfpOutput + " /tmp/" )
            os.system( "scp " + ONOSUser + "@" + ONOS1Ip + ":" +
                       tsharkTcpOutput + " /tmp/" )

            # TODO: Automate OFP output analysis
            # Debug mode - print out packets captured at runtime
            if debugMode == 'on':
                ofpFile = open( tsharkOfpOutput, 'r' )
                main.log.info( "Tshark OFP Vendor output: " )
                for line in ofpFile:
                    tsharkOfpResultList.append( line )
                    main.log.info( line )
                ofpFile.close()

                tcpFile = open( tsharkTcpOutput, 'r' )
                main.log.info( "Tshark TCP 74 output: " )
                for line in tcpFile:
                    tsharkTcpResultList.append( line )
                    main.log.info( line )
                tcpFile.close()

            jsonObj1 = json.loads( jsonStrTopologyMetrics1 )
            jsonObj2 = json.loads( jsonStrTopologyMetrics2 )
            jsonObj3 = json.loads( jsonStrTopologyMetrics3 )

            graphTimestamp1 = \
                jsonObj1[ graphTimestamp ][ 'value' ]
            graphTimestamp2 = \
                jsonObj2[ graphTimestamp ][ 'value' ]
            graphTimestamp3 = \
                jsonObj3[ graphTimestamp ][ 'value' ]

            graphLat1 = int( graphTimestamp1 ) - int( t0System )
            graphLat2 = int( graphTimestamp2 ) - int( t0System )
            graphLat3 = int( graphTimestamp3 ) - int( t0System )

            avgGraphLat = \
                ( int( graphLat1 ) +
                  int( graphLat2 ) +
                  int( graphLat3 ) ) / 3

            if avgGraphLat > swDiscThresholdMin \
                    and avgGraphLat < swDiscThresholdMax:
                swDiscoveryLatList.append(
                    avgGraphLat )
            else:
                main.log.info( "100 Switch discovery latency " +
                               "exceeded the threshold." )

            # END ITERATION FOR LOOP

        swLatMin = min( swDiscoveryLatList )
        swLatMax = max( swDiscoveryLatList )
        swLatAvg = sum( swDiscoveryLatList ) /\
            len( swDiscoveryLatList )

        main.log.report( "100 Switch discovery lat " +
                         "Min: " + str( swLatMin ) + " ms" +
                         "Max: " + str( swLatMax ) + " ms" +
                         "Avg: " + str( swLatAvg ) + " ms" )

    def CASE6( self, main ):
        """
        Increase number of nodes and initiate CLI
        """
        import time

        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS2Ip = main.params[ 'CTRL' ][ 'ip2' ]
        ONOS3Ip = main.params[ 'CTRL' ][ 'ip3' ]
        ONOS4Ip = main.params[ 'CTRL' ][ 'ip4' ]
        ONOS5Ip = main.params[ 'CTRL' ][ 'ip5' ]
        ONOS6Ip = main.params[ 'CTRL' ][ 'ip6' ]
        ONOS7Ip = main.params[ 'CTRL' ][ 'ip7' ]

        cellName = main.params[ 'ENV' ][ 'cellName' ]

        global clusterCount

        # Cluster size increased everytime the case is defined
        clusterCount += 2

        main.log.report( "Increasing cluster size to " +
                         str( clusterCount ) )

        installResult = main.FALSE
        if clusterCount == 3:
            main.log.info( "Installing nodes 2 and 3" )
            node2Result = \
                main.ONOSbench.onosInstall( node=ONOS2Ip )
            node3Result = \
                main.ONOSbench.onosInstall( node=ONOS3Ip )
            installResult = node2Result and node3Result

            time.sleep( 5 )

            main.ONOS2cli.startOnosCli( ONOS2Ip )
            main.ONOS3cli.startOnosCli( ONOS3Ip )

        elif clusterCount == 5:
            main.log.info( "Installing nodes 4 and 5" )
            node4Result = \
                main.ONOSbench.onosInstall( node=ONOS4Ip )
            node5Result = \
                main.ONOSbench.onosInstall( node=ONOS5Ip )
            installResult = node4Result and node5Result

            time.sleep( 5 )

            main.ONOS4cli.startOnosCli( ONOS4Ip )
            main.ONOS5cli.startOnosCli( ONOS5Ip )

        elif clusterCount == 7:
            main.log.info( "Installing nodes 4 and 5" )
            node6Result = \
                main.ONOSbench.onosInstall( node=ONOS6Ip )
            node7Result = \
                main.ONOSbench.onosInstall( node=ONOS7Ip )
            installResult = node6Result and node7Result

            time.sleep( 5 )

            main.ONOS6cli.startOnosCli( ONOS6Ip )
            main.ONOS7cli.startOnosCli( ONOS7Ip )
