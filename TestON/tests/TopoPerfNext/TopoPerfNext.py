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
        #TODO: fix run number implementation
        global runNum 
        # Set initial cluster count
        clusterCount = 1
        ##

        runNum = time.strftime("%d%H%M%S")

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

        main.step( "Starting mininet topology " )
        main.Mininet1.startNet()

        main.step( "Cleaning previously installed ONOS if any" )
        main.ONOSbench.onosUninstall( nodeIp=ONOS2Ip )
        main.ONOSbench.onosUninstall( nodeIp=ONOS3Ip )
        main.ONOSbench.onosUninstall( nodeIp=ONOS4Ip )
        main.ONOSbench.onosUninstall( nodeIp=ONOS5Ip )
        main.ONOSbench.onosUninstall( nodeIp=ONOS6Ip )
        main.ONOSbench.onosUninstall( nodeIp=ONOS7Ip )

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

        # Initialize 2d array for [node][iteration] storage
        endToEndLatNodeIter = numpy.zeros(( clusterCount, int(numIter) ))
        ofpToGraphLatNodeIter = numpy.zeros(( clusterCount, int(numIter) ))
        # tcp-to-ofp measurements are same throughout each iteration 
        tcpToOfpLatIter = [] 

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

            if len( obj ) > 1:
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
            # tcp to ofp processing latency ( switch connection )
            deltaTcpOfp1 = int(t0Ofp) - int(t0Tcp)

            if deltaTcpOfp1 > thresholdMin and deltaTcpOfp1 < thresholdMax\
               and i >= iterIgnore:
                tcpToOfpLatIter.append(deltaTcpOfp1)
                main.log.info("iter"+str(i)+" tcp-to-ofp: "+
                          str(deltaTcpOfp1)+" ms")
            else:
                tcpToOfpLatIter.append(0)
                main.log.info("iter"+str(i)+" tcp-to-ofp: "+
                          str(deltaTcpOfp1)+" ms - ignored this iteration")

            # Store initial measurements in data array
            #This measurement is for node 1
           
            if deltaGraph1 > thresholdMin and deltaGraph1 < thresholdMax\
               and i >= iterIgnore:
                endToEndLatNodeIter[0][i] = deltaGraph1
                main.log.info("ONOS1 iter"+str(i)+" end-to-end: "+
                          str(deltaGraph1)+" ms")
            else:
                main.log.info("ONOS1 iter"+str(i)+" end-to-end: "+
                          str(deltaGraph1)+" ms - ignored this iteration")


            if deltaOfpGraph1 > thresholdMin and deltaOfpGraph1 < thresholdMax\
               and i >= iterIgnore:
                ofpToGraphLatNodeIter[0][i] = deltaOfpGraph1
             
            main.log.info("ONOS1 iter"+str(i)+" ofp-to-graph: "+
                          str(deltaOfpGraph1)+" ms")

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

                if deltaGraph2 > thresholdMin and\
                   deltaGraph2 < thresholdMax and i >= iterIgnore:
                    endToEndLatNodeIter[1][i] = deltaGraph2
                    main.log.info("ONOS2 iter"+str(i)+" end-to-end: "+
                            str(deltaGraph2)+" ms")
                
                if deltaOfpGraph2 > thresholdMin and\
                   deltaOfpGraph2 < thresholdMax and i >= iterIgnore:
                    ofpToGraphLatNodeIter[1][i] = deltaOfpGraph2
                    main.log.info("ONOS2 iter"+str(i)+" ofp-to-graph: "+
                            str(deltaOfpGraph2)+" ms")

                if deltaGraph3 > thresholdMin and\
                   deltaGraph3 < thresholdMax and i >= iterIgnore:
                    endToEndLatNodeIter[2][i] = deltaGraph3
                    main.log.info("ONOS3 iter"+str(i)+" end-to-end: "+
                            str(deltaGraph3)+" ms")
                
                if deltaOfpGraph3 > thresholdMin and\
                   deltaOfpGraph3 < thresholdMax and i >= iterIgnore:
                    ofpToGraphLatNodeIter[2][i] = deltaOfpGraph3
                    main.log.info("ONOS3 iter"+str(i)+" ofp-to-graph: "+
                            str(deltaOfpGraph3)+" ms")
                
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
                
                if deltaGraph4 > thresholdMin and\
                   deltaGraph4 < thresholdMax and i >= iterIgnore:
                    endToEndLatNodeIter[3][i] = deltaGraph4
                    main.log.info("ONOS4 iter"+str(i)+" end-to-end: "+
                            str(deltaGraph4)+" ms")
                
                    #TODO:
                if deltaOfpGraph4 > thresholdMin and\
                   deltaOfpGraph4 < thresholdMax and i >= iterIgnore:
                    ofpToGraphLatNodeIter[3][i] = deltaOfpGraph4
                    main.log.info("ONOS4 iter"+str(i)+" ofp-to-graph: "+
                            str(deltaOfpGraph4)+" ms")

                if deltaGraph5 > thresholdMin and\
                   deltaGraph5 < thresholdMax and i >= iterIgnore:
                    endToEndLatNodeIter[4][i] = deltaGraph5
                    main.log.info("ONOS5 iter"+str(i)+" end-to-end: "+
                            str(deltaGraph5)+" ms")
                
                if deltaOfpGraph5 > thresholdMin and\
                   deltaOfpGraph5 < thresholdMax and i >= iterIgnore:
                    ofpToGraphLatNodeIter[4][i] = deltaOfpGraph5
                    main.log.info("ONOS5 iter"+str(i)+" ofp-to-graph: "+
                            str(deltaOfpGraph5)+" ms")
                
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
                
                if deltaGraph6 > thresholdMin and\
                   deltaGraph6 < thresholdMax and i >= iterIgnore:
                    endToEndLatNodeIter[5][i] = deltaGraph6
                    main.log.info("ONOS6 iter"+str(i)+" end-to-end: "+
                            str(deltaGraph6)+" ms")
                
                    #TODO:
                if deltaOfpGraph6 > thresholdMin and\
                   deltaOfpGraph6 < thresholdMax and i >= iterIgnore:
                    ofpToGraphLatNodeIter[5][i] = deltaOfpGraph6
                    main.log.info("ONOS6 iter"+str(i)+" ofp-to-graph: "+
                            str(deltaOfpGraph6)+" ms")

                if deltaGraph7 > thresholdMin and\
                   deltaGraph7 < thresholdMax and i >= iterIgnore:
                    endToEndLatNodeIter[6][i] = deltaGraph7
                    main.log.info("ONOS7 iter"+str(i)+" end-to-end: "+
                            str(deltaGraph7)+" ms")
                
                if deltaOfpGraph7 > thresholdMin and\
                   deltaOfpGraph7 < thresholdMax and i >= iterIgnore:
                    ofpToGraphLatNodeIter[6][i] = deltaOfpGraph7
                    main.log.info("ONOS7 iter"+str(i)+" ofp-to-graph: "+
                            str(deltaOfpGraph7)+" ms")

            main.step( "Remove switch from controller" )
            main.Mininet1.deleteSwController( "s1" )

            time.sleep( 5 )

        # END of for loop iteration

        #str( round( numpy.std( latencyT0ToDeviceList ), 1 ) )

        endToEndAvg = 0
        ofpToGraphAvg = 0
        endToEndList = []
        ofpToGraphList = []

        for node in range( 0, clusterCount ):
            # The latency 2d array was initialized to 0. 
            # If an iteration was ignored, then we have some 0's in
            # our calculation. To avoid having this interfere with our 
            # results, we must delete any index where 0 is found...
            # WARN: Potentially, we could have latency that hovers at
            # 0 ms once we have optimized code. FIXME for when this is
            # the case. Being able to obtain sub-millisecond accuracy
            # can prevent this from happening
            for item in endToEndLatNodeIter[node]:
                if item > 0.0:
                    endToEndList.append(item)
            for item in ofpToGraphLatNodeIter[node]:
                if item > 0.0:
                    ofpToGraphList.append(item)

            endToEndAvg = numpy.mean(endToEndList)
            ofpToGraphAvg = numpy.mean(ofpToGraphList)

            main.log.report( " - Node "+str(node+1)+" Summary - " )
            main.log.report( " End-to-end Avg: "+
                             str(round(endToEndAvg,2))+" ms"+
                             " End-to-end Std dev: "+
                             str(round(numpy.std(endToEndList),2))+" ms")
            #main.log.report( " Ofp-to-graph Avg: "+
            #                 str(round(ofpToGraphAvg,2))+" ms"+
            #                 " Ofp-to-graph Std dev: "+
            #                 str(round(numpy.std(ofpToGraphList),2))+
            #                 " ms")

        if debugMode == 'on':
            main.ONOS1.cpLogsToDir( "/opt/onos/log/karaf.log",
                                      "/tmp/", copyFileName="sw_lat_karaf" )

        #TODO: correct assert
        assertion = main.TRUE

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
        global runNum

        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS2Ip = main.params[ 'CTRL' ][ 'ip2' ]
        ONOS3Ip = main.params[ 'CTRL' ][ 'ip3' ]
        ONOSUser = main.params[ 'CTRL' ][ 'user' ]

        defaultSwPort = main.params[ 'CTRL' ][ 'port1' ]

        assertion = main.TRUE
        # Number of iterations of case
        numIter = main.params[ 'TEST' ][ 'numIter' ]
        iterIgnore = int( main.params[ 'TEST' ][ 'iterIgnore' ] )

        # Timestamp 'keys' for json metrics output.
        # These are subject to change, hence moved into params
        deviceTimestamp = main.params[ 'JSON' ][ 'deviceTimestamp' ]
        graphTimestamp = main.params[ 'JSON' ][ 'graphTimestamp' ]

        debugMode = main.params[ 'TEST' ][ 'debugMode' ]
        postToDB = main.params[ 'DB' ][ 'postToDB' ]
        resultPath = main.params[ 'DB' ][ 'portEventResultPath' ]
        timeToPost = time.strftime("%Y-%m-%d %H:%M:%S")

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
       
        # Initialize 2d array filled with 0's
        # arraySizeFormat[clusterCount][numIter]
        portUpDevNodeIter = numpy.zeros(( clusterCount, int(numIter) ))
        portUpGraphNodeIter = numpy.zeros(( clusterCount, int(numIter) ))
        portDownDevNodeIter = numpy.zeros(( clusterCount, int(numIter) ))
        portDownGraphNodeIter = numpy.zeros(( clusterCount, int(numIter) ))

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

            if ptDownGraphToOfp1 > downThresholdMin and\
               ptDownGraphToOfp1 < downThresholdMax and i > iterIgnore:
                portDownGraphNodeIter[0][i] = ptDownGraphToOfp1
                main.log.info("iter"+str(i)+" port down graph-to-ofp: "+
                              str(ptDownGraphToOfp1)+" ms")
            else:
                main.log.info("iter"+str(i)+" skipped. Result: "+
                              str(ptDownGraphToOfp1)+" ms")
            if ptDownDeviceToOfp1 > downThresholdMin and\
               ptDownDeviceToOfp1 < downThresholdMax and i > iterIgnore:
                portDownDevNodeIter[0][i] = ptDownDeviceToOfp1
                main.log.info("iter"+str(i)+" port down device-to-ofp: "+
                              str(ptDownDeviceToOfp1)+" ms")
            else:
                main.log.info("iter"+str(i)+" skipped. Result: "+
                              str(ptDownDeviceToOfp1)+" ms")

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

                if ptDownGraphToOfp2 > downThresholdMin and\
                   ptDownGraphToOfp2 < downThresholdMax and i > iterIgnore:
                    portDownGraphNodeIter[1][i] = ptDownGraphToOfp2
                    main.log.info("ONOS2 iter"+str(i)+" graph-to-ofp: "+
                                  str(ptDownGraphToOfp2)+" ms")

                if ptDownDeviceToOfp2 > downThresholdMin and\
                   ptDownDeviceToOfp2 < downThresholdMax and i > iterIgnore:
                    portDownDevNodeIter[1][i] = ptDownDeviceToOfp2
                    main.log.info("ONOS2 iter"+str(i)+" device-to-ofp: "+
                                  str(ptDownDeviceToOfp2)+" ms")

                if ptDownGraphToOfp3 > downThresholdMin and\
                   ptDownGraphToOfp3 < downThresholdMax and i > iterIgnore:
                    portDownGraphNodeIter[2][i] = ptDownGraphToOfp3
                    main.log.info("ONOS3 iter"+str(i)+" graph-to-ofp: "+
                                  str(ptDownGraphToOfp3)+" ms")

                if ptDownDeviceToOfp3 > downThresholdMin and\
                   ptDownDeviceToOfp3 < downThresholdMax and i > iterIgnore:
                    portDownDevNodeIter[2][i] = ptDownDeviceToOfp3
                    main.log.info("ONOS3 iter"+str(i)+" device-to-ofp: "+
                                  str(ptDownDeviceToOfp3)+" ms")

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
                
                if ptDownGraphToOfp4 > downThresholdMin and\
                   ptDownGraphToOfp4 < downThresholdMax and i > iterIgnore:
                    portDownGraphNodeIter[3][i] = ptDownGraphToOfp4
                    main.log.info("ONOS4 iter"+str(i)+" graph-to-ofp: "+
                                  str(ptDownGraphToOfp4)+" ms")

                if ptDownDeviceToOfp4 > downThresholdMin and\
                   ptDownDeviceToOfp4 < downThresholdMax and i > iterIgnore:
                    portDownDevNodeIter[3][i] = ptDownDeviceToOfp4
                    main.log.info("ONOS4 iter"+str(i)+" device-to-ofp: "+
                                  str(ptDownDeviceToOfp4)+" ms")

                if ptDownGraphToOfp5 > downThresholdMin and\
                   ptDownGraphToOfp5 < downThresholdMax and i > iterIgnore:
                    portDownGraphNodeIter[4][i] = ptDownGraphToOfp5
                    main.log.info("ONOS5 iter"+str(i)+" graph-to-ofp: "+
                                  str(ptDownGraphToOfp5)+" ms")
                
                if ptDownDeviceToOfp5 > downThresholdMin and\
                   ptDownDeviceToOfp5 < downThresholdMax and i > iterIgnore:
                    portDownDevNodeIter[4][i] = ptDownDeviceToOfp5
                    main.log.info("ONOS5 iter"+str(i)+" device-to-ofp: "+
                                  str(ptDownDeviceToOfp5)+" ms")

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
                
                if ptDownGraphToOfp6 > downThresholdMin and\
                   ptDownGraphToOfp6 < downThresholdMax and i > iterIgnore:
                    portDownGraphNodeIter[5][i] = ptDownGraphToOfp6
                    main.log.info("ONOS6 iter"+str(i)+" graph-to-ofp: "+
                                  str(ptDownGraphToOfp6)+" ms")

                if ptDownDeviceToOfp6 > downThresholdMin and\
                   ptDownDeviceToOfp6 < downThresholdMax and i > iterIgnore:
                    portDownDevNodeIter[5][i] = ptDownDeviceToOfp6
                    main.log.info("ONOS6 iter"+str(i)+" device-to-ofp: "+
                                  str(ptDownDeviceToOfp6)+" ms")

                if ptDownGraphToOfp7 > downThresholdMin and\
                   ptDownGraphToOfp7 < downThresholdMax and i > iterIgnore:
                    portDownGraphNodeIter[6][i] = ptDownGraphToOfp7
                    main.log.info("ONOS7 iter"+str(i)+" graph-to-ofp: "+
                                  str(ptDownGraphToOfp7)+" ms")
                
                if ptDownDeviceToOfp7 > downThresholdMin and\
                   ptDownDeviceToOfp7 < downThresholdMax and i > iterIgnore:
                    portDownDevNodeIter[6][i] = ptDownDeviceToOfp7
                    main.log.info("ONOS7 iter"+str(i)+" device-to-ofp: "+
                                  str(ptDownDeviceToOfp7)+" ms")

            time.sleep( 3 )

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
            
            if ptUpGraphToOfp1 > upThresholdMin and\
               ptUpGraphToOfp1 < upThresholdMax and i > iterIgnore:
                portUpGraphNodeIter[0][i] = ptUpGraphToOfp1
                main.log.info("iter"+str(i)+" port up graph-to-ofp: "+
                              str(ptUpGraphToOfp1)+" ms")
            else:
                main.log.info("iter"+str(i)+" skipped. Result: "+
                              str(ptUpGraphToOfp1)+" ms")
            
            if ptUpDeviceToOfp1 > upThresholdMin and\
               ptUpDeviceToOfp1 < upThresholdMax and i > iterIgnore:
                portUpDevNodeIter[0][i] = ptUpDeviceToOfp1
                main.log.info("iter"+str(i)+" port up device-to-ofp: "+
                              str(ptUpDeviceToOfp1)+" ms")
            else:
                main.log.info("iter"+str(i)+" skipped. Result: "+
                              str(ptUpDeviceToOfp1)+" ms")

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
            
                if ptUpGraphToOfp2 > upThresholdMin and\
                   ptUpGraphToOfp2 < upThresholdMax and i > iterIgnore:
                    portUpGraphNodeIter[1][i] = ptUpGraphToOfp2
                    main.log.info("iter"+str(i)+" port up graph-to-ofp: "+
                              str(ptUpGraphToOfp2)+" ms")
            
                if ptUpDeviceToOfp2 > upThresholdMin and\
                   ptUpDeviceToOfp2 < upThresholdMax and i > iterIgnore:
                    portUpDevNodeIter[1][i] = ptUpDeviceToOfp2
                    main.log.info("iter"+str(i)+" port up device-to-ofp: "+
                              str(ptUpDeviceToOfp2)+" ms")
                
                if ptUpGraphToOfp3 > upThresholdMin and\
                   ptUpGraphToOfp3 < upThresholdMax and i > iterIgnore:
                    portUpGraphNodeIter[2][i] = ptUpGraphToOfp3
                    main.log.info("iter"+str(i)+" port up graph-to-ofp: "+
                              str(ptUpGraphToOfp3)+" ms")
            
                if ptUpDeviceToOfp3 > upThresholdMin and\
                   ptUpDeviceToOfp3 < upThresholdMax and i > iterIgnore:
                    portUpDevNodeIter[2][i] = ptUpDeviceToOfp3
                    main.log.info("iter"+str(i)+" port up device-to-ofp: "+
                              str(ptUpDeviceToOfp3)+" ms")

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
                
                if ptUpGraphToOfp4 > upThresholdMin and\
                   ptUpGraphToOfp4 < upThresholdMax and i > iterIgnore:
                    portUpGraphNodeIter[3][i] = ptUpGraphToOfp4
                    main.log.info("iter"+str(i)+" port up graph-to-ofp: "+
                              str(ptUpGraphToOfp4)+" ms")
            
                if ptUpDeviceToOfp4 > upThresholdMin and\
                   ptUpDeviceToOfp4 < upThresholdMax and i > iterIgnore:
                    portUpDevNodeIter[3][i] = ptUpDeviceToOfp4
                    main.log.info("iter"+str(i)+" port up device-to-ofp: "+
                              str(ptUpDeviceToOfp4)+" ms")
                
                if ptUpGraphToOfp5 > upThresholdMin and\
                   ptUpGraphToOfp5 < upThresholdMax and i > iterIgnore:
                    portUpGraphNodeIter[4][i] = ptUpGraphToOfp5
                    main.log.info("iter"+str(i)+" port up graph-to-ofp: "+
                              str(ptUpGraphToOfp5)+" ms")
            
                if ptUpDeviceToOfp5 > upThresholdMin and\
                   ptUpDeviceToOfp5 < upThresholdMax and i > iterIgnore:
                    portUpDevNodeIter[4][i] = ptUpDeviceToOfp5
                    main.log.info("iter"+str(i)+" port up device-to-ofp: "+
                              str(ptUpDeviceToOfp5)+" ms")

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
                
                if ptUpGraphToOfp6 > upThresholdMin and\
                   ptUpGraphToOfp6 < upThresholdMax and i > iterIgnore:
                    portUpGraphNodeIter[5][i] = ptUpGraphToOfp6
                    main.log.info("iter"+str(i)+" port up graph-to-ofp: "+
                              str(ptUpGraphToOfp6)+" ms")
            
                if ptUpDeviceToOfp6 > upThresholdMin and\
                   ptUpDeviceToOfp6 < upThresholdMax and i > iterIgnore:
                    portUpDevNodeIter[5][i] = ptUpDeviceToOfp6
                    main.log.info("iter"+str(i)+" port up device-to-ofp: "+
                              str(ptUpDeviceToOfp6)+" ms")
                
                if ptUpGraphToOfp7 > upThresholdMin and\
                   ptUpGraphToOfp7 < upThresholdMax and i > iterIgnore:
                    portUpGraphNodeIter[6][i] = ptUpGraphToOfp7
                    main.log.info("iter"+str(i)+" port up graph-to-ofp: "+
                              str(ptUpGraphToOfp7)+" ms")
            
                if ptUpDeviceToOfp7 > upThresholdMin and\
                   ptUpDeviceToOfp7 < upThresholdMax and i > iterIgnore:
                    portUpDevNodeIter[6][i] = ptUpDeviceToOfp7
                    main.log.info("iter"+str(i)+" port up device-to-ofp: "+
                              str(ptUpDeviceToOfp7)+" ms")

            # END ITERATION FOR LOOP
        
        portUpDevList = []
        portUpGraphList = []
        portDownDevList = []
        portDownGraphList = []

        portUpDevAvg = 0
        portUpGraphAvg = 0
        portDownDevAvg = 0
        portDownGraphAvg = 0

        dbCmdList = []

        for node in range( 0, clusterCount ):

            # NOTE: 
            # Currently the 2d array is initialized with 0's. 
            # We want to avoid skewing our results if the array
            # was not modified with the correct latency.
            for item in portUpDevNodeIter[node]:
                if item > 0.0:
                    portUpDevList.append(item)
            for item in portUpGraphNodeIter[node]:
                if item > 0.0:
                    portUpGraphList.append(item)
            for item in portDownDevNodeIter[node]:
                if item > 0.0:
                    portDownDevList.append(item)
            for item in portDownGraphNodeIter[node]:
                if item > 0.0:
                    portDownGraphList.append(item)
       
            portUpDevAvg = round(numpy.mean(portUpDevList), 2)
            portUpGraphAvg = round(numpy.mean(portUpGraphList), 2)
            portDownDevAvg = round(numpy.mean(portDownDevList), 2)
            portDownGraphAvg = round(numpy.mean(portDownGraphList), 2)

            main.log.report( " - Node "+str(node+1)+" Summary - " )
            #main.log.report( " Port up ofp-to-device "+
            #                 str(round(portUpDevAvg, 2))+" ms")
            main.log.report( " Port up ofp-to-graph "+
                             str(portUpGraphAvg)+" ms")
            #main.log.report( " Port down ofp-to-device "+
            #                 str(round(portDownDevAvg, 2))+" ms")
            main.log.report( " Port down ofp-to-graph "+
                             str(portDownGraphAvg)+" ms")
       
            dbCmdList.append(
                "INSERT INTO port_latency_tests VALUES("
                   "'"+timeToPost+"','port_latency_results',"
                   ""+runNum+","+str(clusterCount)+",'baremetal"+str(node+1)+"',"
                   ""+str(portUpGraphAvg)+",0,"+str(portDownGraphAvg)+",0);"
            )
        
        #Write to file for posting to DB
        fResult = open(resultPath, 'a')
        for line in dbCmdList:
            if line:
                fResult.write(line+"\n")
        fResult.close()

        # Remove switches from controller for next test
        main.Mininet1.deleteSwController( "s1" )
        main.Mininet1.deleteSwController( "s2" )

        #TODO: correct assertion

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
            main.log.info( "Installing nodes 6 and 7" )
            node6Result = \
                main.ONOSbench.onosInstall( node=ONOS6Ip )
            node7Result = \
                main.ONOSbench.onosInstall( node=ONOS7Ip )
            installResult = node6Result and node7Result

            time.sleep( 5 )

            main.ONOS6cli.startOnosCli( ONOS6Ip )
            main.ONOS7cli.startOnosCli( ONOS7Ip )
