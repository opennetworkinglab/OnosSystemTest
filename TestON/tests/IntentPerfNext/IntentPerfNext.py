# Intent Performance Test for ONOS-next
#
# andrew@onlab.us
#
# November 5, 2014


class IntentPerfNext:

    def __init__( self ):
        self.default = ""

    def CASE1( self, main ):
        """
        ONOS startup sequence
        """
        import time
        global clusterCount
        global timeToPost
        global runNum

        clusterCount = 1
        timeToPost = time.strftime("%Y-%m-%d %H:%M:%S")
        runNum = time.strftime("%d%H%M%S")

        cellName = main.params[ 'ENV' ][ 'cellName' ]

        gitPull = main.params[ 'GIT' ][ 'autoPull' ]
        checkoutBranch = main.params[ 'GIT' ][ 'checkout' ]
        intentFilePath = main.params[ 'DB' ][ 'intentFilePath' ]

        ONOSIp = []
        for i in range(1, 8):
            ONOSIp.append(main.params[ 'CTRL' ][ 'ip'+str(i) ]) 
            main.ONOSbench.onosUninstall( nodeIp = ONOSIp[i-1] )

        MN1Ip = main.params[ 'MN' ][ 'ip1' ]
        BENCHIp = main.params[ 'BENCH' ][ 'ip' ]

        main.case( "Setting up test environment" )

        main.step( "Clearing previous DB log file" )
        fIntentLog = open(intentFilePath, 'w')
        # Overwrite with empty line and close 
        fIntentLog.write('')
        fIntentLog.close()

        main.step( "Starting mininet topology" )
        main.Mininet1.startNet()

        main.step( "Creating cell file" )
        cellFileResult = main.ONOSbench.createCellFile(
            BENCHIp, cellName, MN1Ip,
            ("onos-core,webconsole,onos-api,onos-app-metrics,onos-gui,"
            "onos-cli,onos-openflow"),
            ONOSIp[0] )

        main.step( "Applying cell file to environment" )
        cellApplyResult = main.ONOSbench.setCell( cellName )
        verifyCellResult = main.ONOSbench.verifyCell()

        main.step( "Removing raft logs" )
        main.ONOSbench.onosRemoveRaftLogs()

        main.step( "Git checkout and pull " + checkoutBranch )
        if gitPull == 'on':
            checkoutResult = \
                main.ONOSbench.gitCheckout( checkoutBranch )
            pullResult = main.ONOSbench.gitPull()

            # If you used git pull, auto compile
            main.step( "Using onos-build to compile ONOS" )
            buildResult = main.ONOSbench.onosBuild()
        else:
            checkoutResult = main.TRUE
            pullResult = main.TRUE
            buildResult = main.TRUE
            main.log.info( "Git pull skipped by configuration" )

        main.log.report( "Commit information - " )
        main.ONOSbench.getVersion( report=True )

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()

        main.step( "Installing ONOS package" )
        install1Result = main.ONOSbench.onosInstall( node=ONOSIp[0] )

        main.step( "Set cell for ONOScli env" )
        main.ONOS1cli.setCell( cellName )

        time.sleep( 5 )

        main.step( "Start onos cli" )
        cli1 = main.ONOS1cli.startOnosCli( ONOSIp[0] )

        utilities.assert_equals( expect=main.TRUE,
                                actual=cellFileResult and cellApplyResult and
                                verifyCellResult and checkoutResult and
                                pullResult and buildResult and
                                install1Result,  # and install2Result and
                                # install3Result,
                                onpass="ONOS started successfully",
                                onfail="Failed to start ONOS" )

    def CASE2( self, main ):
        """
        Single intent add latency

        """
        import time
        import json
        import requests
        import os
        import numpy
        global clusterCount

        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS2Ip = main.params[ 'CTRL' ][ 'ip2' ]
        ONOS3Ip = main.params[ 'CTRL' ][ 'ip3' ]
        ONOSIpList = []
        for i in range( 1, 8 ):
            ONOSIpList.append( main.params[ 'CTRL' ][ 'ip' + str( i ) ] )

        ONOSUser = main.params[ 'CTRL' ][ 'user' ]

        defaultSwPort = main.params[ 'CTRL' ][ 'port1' ]

        # number of iterations of case
        numIter = main.params[ 'TEST' ][ 'numIter' ]
        numIgnore = int( main.params[ 'TEST' ][ 'numIgnore' ] )

        # Timestamp keys for json metrics output
        submitTime = main.params[ 'JSON' ][ 'submittedTime' ]
        installTime = main.params[ 'JSON' ][ 'installedTime' ]
        wdRequestTime = main.params[ 'JSON' ][ 'wdRequestTime' ]
        withdrawnTime = main.params[ 'JSON' ][ 'withdrawnTime' ]

        assertion = main.TRUE

        intentAddLatList = []

        # Distribute switches according to cluster count
        for i in range( 1, 9 ):
            if clusterCount == 1:
                main.Mininet1.assignSwController(
                    sw=str( i ), ip1=ONOSIpList[ 0 ],
                    port1=defaultSwPort
                )
            elif clusterCount == 3:
                if i < 3:
                    index = 0
                elif i < 6 and i >= 3:
                    index = 1
                else:
                    index = 2
                main.Mininet1.assignSwController(
                    sw=str( i ), ip1=ONOSIpList[ index ],
                    port1=defaultSwPort
                )
            elif clusterCount == 5:
                if i < 3:
                    index = 0
                elif i < 5 and i >= 3:
                    index = 1
                elif i < 7 and i >= 5:
                    index = 2
                elif i == 7:
                    index = 3
                else:
                    index = 4
                main.Mininet1.assignSwController(
                    sw=str( i ), ip1=ONOSIpList[ index ],
                    port1=defaultSwPort
                )
            elif clusterCount == 7:
                if i < 6:
                    index = i
                else:
                    index = 6
                main.Mininet1.assignSwController(
                    sw=str( i ), ip1=ONOSIpList[ index ],
                    port1=defaultSwPort
                )

        time.sleep( 10 )

        main.log.report( "Single intent add latency test" )

        devicesJsonStr = main.ONOS1cli.devices()
        devicesJsonObj = json.loads( devicesJsonStr )

        if not devicesJsonObj:
            main.log.report( "Devices not discovered" )
            main.log.report( "Aborting test" )
            main.exit()
        else:
            main.log.info( "Devices discovered successfully" )

        deviceIdList = []

        # Obtain device id list in ONOS format.
        # They should already be in order ( 1,2,3,10,11,12,13, etc )
        for device in devicesJsonObj:
            deviceIdList.append( device[ 'id' ] )

        for i in range( 0, int( numIter ) ):
            # addPointIntent( ingrDevice,  egrDevice,
            #                 ingrPort,    egrPort )
            main.ONOS1cli.addPointIntent(
                deviceIdList[ 0 ] + "/2", deviceIdList[ 7 ] + "/2" )

            # Allow some time for intents to propagate
            time.sleep( 5 )

            intentsStr = main.ONOS1cli.intents( jsonFormat=True )
            intentsObj = json.loads( intentsStr )
            for intent in intentsObj:
                if intent[ 'state' ] == "INSTALLED":
                    main.log.info( "Intent installed successfully" )
                    intentId = intent[ 'id' ]
                    main.log.info( "Intent id: " + str( intentId ) )
                else:
                    # TODO: Add error handling
                    main.log.info( "Intent installation failed" )
                    intentId = ""

            # Obtain metrics from ONOS 1, 2, 3
            intentsJsonStr1 = main.ONOS1cli.intentsEventsMetrics()
            intentsJsonObj1 = json.loads( intentsJsonStr1 )
            # Parse values from the json object
            intentSubmit1 = \
                intentsJsonObj1[ submitTime ][ 'value' ]
            intentInstall1 = \
                intentsJsonObj1[ installTime ][ 'value' ]
            intentInstallLat1 = \
                int( intentInstall1 ) - int( intentSubmit1 )

            if clusterCount == 3:
                intentsJsonStr2 = main.ONOS2cli.intentsEventsMetrics()
                intentsJsonStr3 = main.ONOS3cli.intentsEventsMetrics()
                intentsJsonObj2 = json.loads( intentsJsonStr2 )
                intentsJsonObj3 = json.loads( intentsJsonStr3 )
                intentSubmit2 = \
                    intentsJsonObj2[ submitTime ][ 'value' ]
                intentSubmit3 = \
                    intentsJsonObj3[ submitTime ][ 'value' ]
                intentInstall2 = \
                    intentsJsonObj2[ installTime ][ 'value' ]
                intentInstall3 = \
                    intentsJsonObj3[ installTime ][ 'value' ]
                intentInstallLat2 = \
                    int( intentInstall2 ) - int( intentSubmit2 )
                intentInstallLat3 = \
                    int( intentInstall3 ) - int( intentSubmit3 )
            else:
                intentInstallLat2 = 0
                intentInstallLat3 = 0

            if clusterCount == 5:
                intentsJsonStr4 = main.ONOS4cli.intentsEventsMetrics()
                intentsJsonStr5 = main.ONOS5cli.intentsEventsMetrics()
                intentsJsonObj4 = json.loads( intentsJsonStr4 )
                intentsJsonObj5 = json.loads( intentsJsonStr5 )
                intentSubmit4 = \
                    intentsJsonObj4[ submitTime ][ 'value' ]
                intentSubmit5 = \
                    intentsJsonObj5[ submitTime ][ 'value' ]
                intentInstall4 = \
                    intentsJsonObj5[ installTime ][ 'value' ]
                intentInstall5 = \
                    intentsJsonObj5[ installTime ][ 'value' ]
                intentInstallLat4 = \
                    int( intentInstall4 ) - int( intentSubmit4 )
                intentInstallLat5 = \
                    int( intentInstall5 ) - int( intentSubmit5 )
            else:
                intentInstallLat4 = 0
                intentInstallLat5 = 0

            if clusterCount == 7:
                intentsJsonStr6 = main.ONOS6cli.intentsEventsMetrics()
                intentsJsonStr7 = main.ONOS7cli.intentsEventsMetrics()
                intentsJsonObj6 = json.loads( intentsJsonStr6 )
                intentsJsonObj7 = json.loads( intentsJsonStr7 )
                intentSubmit6 = \
                    intentsJsonObj6[ submitTime ][ 'value' ]
                intentSubmit7 = \
                    intentsJsonObj6[ submitTime ][ 'value' ]
                intentInstall6 = \
                    intentsJsonObj6[ installTime ][ 'value' ]
                intentInstall7 = \
                    intentsJsonObj7[ installTime ][ 'value' ]
                intentInstallLat6 = \
                    int( intentInstall6 ) - int( intentSubmit6 )
                intentInstallLat7 = \
                    int( intentInstall7 ) - int( intentSubmit7 )
            else:
                intentInstallLat6 = 0
                intentInstallLat7 = 0

            intentInstallLatAvg = \
                ( intentInstallLat1 +
                  intentInstallLat2 +
                  intentInstallLat3 +
                  intentInstallLat4 +
                  intentInstallLat5 +
                  intentInstallLat6 +
                  intentInstallLat7 ) / clusterCount

            main.log.info( "Intent add latency avg for iteration " + str( i ) +
                           ": " + str( intentInstallLatAvg ) + " ms" )

            if intentInstallLatAvg > 0.0 and \
               intentInstallLatAvg < 1000 and i > numIgnore:
                intentAddLatList.append( intentInstallLatAvg )
            else:
                main.log.info( "Intent add latency exceeded " +
                               "threshold. Skipping iteration " + str( i ) )

            time.sleep( 3 )

            # TODO: Only remove intents that were installed
            #      in this case... Otherwise many other intents
            #      may show up distorting the results
            main.log.info( "Removing intents for next iteration" )
            jsonTemp = \
                main.ONOS1cli.intents( jsonFormat=True )
            jsonObjIntents = json.loads( jsonTemp )
            if jsonObjIntents:
                for intents in jsonObjIntents:
                    tempId = intents[ 'id' ]
                    # main.ONOS1cli.removeIntent( tempId )
                    main.log.info( "Removing intent id: " +
                                   str( tempId ) )
                    main.ONOS1cli.removeIntent( tempId )
            else:
                main.log.info( "Intents were not installed correctly" )

            time.sleep( 5 )

        if intentAddLatList:
            intentAddLatAvg = sum( intentAddLatList ) /\
                len( intentAddLatList )
        else:
            main.log.report( "Intent installation latency test failed" )
            intentAddLatAvg = "NA"
            assertion = main.FALSE

        intentAddLatStd = \
            round( numpy.std( intentAddLatList ), 1 )
        # END ITERATION FOR LOOP
        main.log.report( "Single intent add latency - " )
        main.log.report( "Avg: " + str( intentAddLatAvg ) + " ms" )
        main.log.report( "Std Deviation: " + str( intentAddLatStd ) + " ms" )

        utilities.assert_equals(
            expect=main.TRUE,
            actual=assertion,
            onpass="Single intent install latency test successful",
            onfail="Single intent install latency test failed" )

    def CASE3( self, main ):
        """
        Intent Reroute latency
        """
        import time
        import json
        import requests
        import os
        import numpy
        global clusterCount

        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS2Ip = main.params[ 'CTRL' ][ 'ip2' ]
        ONOS3Ip = main.params[ 'CTRL' ][ 'ip3' ]
        ONOSUser = main.params[ 'CTRL' ][ 'user' ]

        defaultSwPort = main.params[ 'CTRL' ][ 'port1' ]

        # number of iterations of case
        numIter = main.params[ 'TEST' ][ 'numIter' ]
        numIgnore = int( main.params[ 'TEST' ][ 'numIgnore' ] )
        assertion = main.TRUE

        # Timestamp keys for json metrics output
        submitTime = main.params[ 'JSON' ][ 'submittedTime' ]
        installTime = main.params[ 'JSON' ][ 'installedTime' ]
        wdRequestTime = main.params[ 'JSON' ][ 'wdRequestTime' ]
        withdrawnTime = main.params[ 'JSON' ][ 'withdrawnTime' ]

        # NOTE: May need to configure interface depending on topology
        intfs = main.params[ 'TEST' ][ 'intfs' ]

        devicesJsonStr = main.ONOS1cli.devices()
        devicesJsonObj = json.loads( devicesJsonStr )

        deviceIdList = []

        # Obtain device id list in ONOS format.
        # They should already be in order ( 1,2,3,10,11,12,13, etc )
        for device in devicesJsonObj:
            deviceIdList.append( device[ 'id' ] )

        intentRerouteLatList = []

        for i in range( 0, int( numIter ) ):
            # addPointIntent( ingrDevice, ingrPort,
            #                 egrDevice, egrPort )
            if len( deviceIdList ) > 0:
                main.ONOS1cli.addPointIntent(
                    deviceIdList[ 0 ] + "/2", deviceIdList[ 7 ] + "/2" )
            else:
                main.log.info( "Failed to fetch devices from ONOS" )

            time.sleep( 5 )

            intentsStr = main.ONOS1cli.intents( jsonFormat=True )
            intentsObj = json.loads( intentsStr )
            for intent in intentsObj:
                if intent[ 'state' ] == "INSTALLED":
                    main.log.info( "Intent installed successfully" )
                    intentId = intent[ 'id' ]
                    main.log.info( "Intent id: " + str( intentId ) )
                else:
                    # TODO: Add error handling
                    main.log.info( "Intent installation failed" )
                    intentId = ""

            main.log.info( "Disabling interface " + intfs )
            t0System = time.time() * 1000
            main.Mininet1.handle.sendline(
                "sh ifconfig " + intfs + " down" )
            main.Mininet1.handle.expect( "mininet>" )

            # TODO: Check for correct intent reroute
            time.sleep( 1 )

            # Obtain metrics from ONOS 1, 2, 3
            intentsJsonStr1 = main.ONOS1cli.intentsEventsMetrics()
            intentsJsonObj1 = json.loads( intentsJsonStr1 )
            # Parse values from the json object
            intentInstall1 = \
                intentsJsonObj1[ installTime ][ 'value' ]
            intentRerouteLat1 = \
                int( intentInstall1 ) - int( t0System )

            if clusterCount == 3:
                intentsJsonStr2 = main.ONOS2cli.intentsEventsMetrics()
                intentsJsonStr3 = main.ONOS3cli.intentsEventsMetrics()

                intentsJsonObj2 = json.loads( intentsJsonStr2 )
                intentsJsonObj3 = json.loads( intentsJsonStr3 )
                intentInstall2 = \
                    intentsJsonObj2[ installTime ][ 'value' ]
                intentInstall3 = \
                    intentsJsonObj3[ installTime ][ 'value' ]
                intentRerouteLat2 = \
                    int( intentInstall2 ) - int( t0System )
                intentRerouteLat3 = \
                    int( intentInstall3 ) - int( t0System )
            else:
                intentRerouteLat2 = 0
                intentRerouteLat3 = 0

            if clusterCount == 5:
                intentsJsonStr4 = main.ONOS4cli.intentsEventsMetrics()
                intentsJsonStr5 = main.ONOS5cli.intentsEventsMetrics()

                intentsJsonObj4 = json.loads( intentsJsonStr4 )
                intentsJsonObj5 = json.loads( intentsJsonStr5 )
                intentInstall4 = \
                    intentsJsonObj4[ installTime ][ 'value' ]
                intentInstall5 = \
                    intentsJsonObj5[ installTime ][ 'value' ]
                intentRerouteLat4 = \
                    int( intentInstall4 ) - int( t0System )
                intentRerouteLat5 = \
                    int( intentInstall5 ) - int( t0System )
            else:
                intentRerouteLat4 = 0
                intentRerouteLat5 = 0

            if clusterCount == 7:
                intentsJsonStr6 = main.ONOS6cli.intentsEventsMetrics()
                intentsJsonStr7 = main.ONOS7cli.intentsEventsMetrics()

                intentsJsonObj6 = json.loads( intentsJsonStr6 )
                intentsJsonObj7 = json.loads( intentsJsonStr7 )
                intentInstall6 = \
                    intentsJsonObj6[ installTime ][ 'value' ]
                intentInstall7 = \
                    intentsJsonObj7[ installTime ][ 'value' ]
                intentRerouteLat6 = \
                    int( intentInstall6 ) - int( t0System )
                intentRerouteLat7 = \
                    int( intentInstall7 ) - int( t0System )
            else:
                intentRerouteLat6 = 0
                intentRerouteLat7 = 0

            intentRerouteLatAvg = \
                ( intentRerouteLat1 +
                  intentRerouteLat2 +
                  intentRerouteLat3 +
                  intentRerouteLat4 +
                  intentRerouteLat5 +
                  intentRerouteLat6 +
                  intentRerouteLat7 ) / clusterCount

            main.log.info( "Intent reroute latency avg for iteration " +
                           str( i ) + ": " + str( intentRerouteLatAvg ) )

            if intentRerouteLatAvg > 0.0 and \
               intentRerouteLatAvg < 1000 and i > numIgnore:
                intentRerouteLatList.append( intentRerouteLatAvg )
            else:
                main.log.info( "Intent reroute latency exceeded " +
                               "threshold. Skipping iteration " + str( i ) )

            main.log.info( "Removing intents for next iteration" )
            main.ONOS1cli.removeIntent( intentId )

            main.log.info( "Bringing Mininet interface up for next " +
                           "iteration" )
            main.Mininet1.handle.sendline(
                "sh ifconfig " + intfs + " up" )
            main.Mininet1.handle.expect( "mininet>" )

        if intentRerouteLatList:
            intentRerouteLatAvg = sum( intentRerouteLatList ) /\
                len( intentRerouteLatList )
        else:
            main.log.report( "Intent reroute test failed. Results NA" )
            intentRerouteLatAvg = "NA"
            # NOTE: fails test when list is empty
            assertion = main.FALSE

        intentRerouteLatStd = \
            round( numpy.std( intentRerouteLatList ), 1 )
        # END ITERATION FOR LOOP
        main.log.report( "Single intent reroute latency - " )
        main.log.report( "Avg: " + str( intentRerouteLatAvg ) + " ms" )
        main.log.report(
            "Std Deviation: " +
            str( intentRerouteLatStd ) +
            " ms" )

        utilities.assert_equals(
            expect=main.TRUE,
            actual=assertion,
            onpass="Single intent reroute latency test successful",
            onfail="Single intent reroute latency test failed" )

    def CASE4( self, main ):
        """
        Batch intent install
        
        Supports scale-out scenarios and increasing
        number of intents within each iteration
        """
        import time
        import json
        import requests
        import os
        import numpy
        global clusterCount
        global timeToPost

        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS2Ip = main.params[ 'CTRL' ][ 'ip2' ]
        ONOS3Ip = main.params[ 'CTRL' ][ 'ip3' ]
        ONOS4Ip = main.params[ 'CTRL' ][ 'ip4' ]
        ONOS5Ip = main.params[ 'CTRL' ][ 'ip5' ]
        ONOS6Ip = main.params[ 'CTRL' ][ 'ip6' ]
        ONOS7Ip = main.params[ 'CTRL' ][ 'ip7' ]

        assertion = main.TRUE

        ONOSIpList = []
        for i in range( 1, 8 ):
            ONOSIpList.append( main.params[ 'CTRL' ][ 'ip' + str( i ) ] )

        ONOSUser = main.params[ 'CTRL' ][ 'user' ]

        defaultSwPort = main.params[ 'CTRL' ][ 'port1' ]

        batchIntentSize = int( main.params[ 'TEST' ][ 'batchIntentSize' ] )
        batchThreshMin = int( main.params[ 'TEST' ][ 'batchThresholdMin' ] )
        batchThreshMax = int( main.params[ 'TEST' ][ 'batchThresholdMax' ] )

        # number of iterations of case
        numIter = main.params[ 'TEST' ][ 'numIter' ]
        numIgnore = int( main.params[ 'TEST' ][ 'numIgnore' ] )
        numSwitch = int( main.params[ 'TEST' ][ 'numSwitch' ] )
        nThread = main.params[ 'TEST' ][ 'numMult' ]
        #nThread = 105

        # DB operation variables
        intentFilePath = main.params[ 'DB' ][ 'intentFilePath' ]

        # Switch assignment NOTE: hardcoded
        if clusterCount == 1:
            for i in range( 1, numSwitch + 1 ):
                main.Mininet1.assignSwController(
                    sw=str( i ),
                    ip1=ONOS1Ip,
                    port1=defaultSwPort )
        if clusterCount == 3:
            for i in range( 1, 3 ):
                main.Mininet1.assignSwController(
                    sw=str( i ),
                    ip1=ONOS1Ip,
                    port1=defaultSwPort )
            for i in range( 3, 6 ):
                main.Mininet1.assignSwController(
                    sw=str( i ),
                    ip1=ONOS2Ip,
                    port1=defaultSwPort )
            for i in range( 6, 9 ):
                main.Mininet1.assignSwController(
                    sw=str( i ),
                    ip1=ONOS3Ip,
                    port1=defaultSwPort )
        if clusterCount == 5:
            main.Mininet1.assignSwController(
                sw="1",
                ip1=ONOS1Ip,
                port1=defaultSwPort )
            main.Mininet1.assignSwController(
                sw="2",
                ip1=ONOS2Ip,
                port1=defaultSwPort )
            for i in range( 3, 6 ):
                main.Mininet1.assignSwController(
                    sw=str( i ),
                    ip1=ONOS3Ip,
                    port1=defaultSwPort )
            main.Mininet1.assignSwController(
                sw="6",
                ip1=ONOS4Ip,
                port1=defaultSwPort )
            main.Mininet1.assignSwController(
                sw="7",
                ip1=ONOS5Ip,
                port1=defaultSwPort )
            main.Mininet1.assignSwController(
                sw="8",
                ip1=ONOS5Ip,
                port1=defaultSwPort )

        if clusterCount == 7:
            for i in range( 1, 9 ):
                if i < 8:
                    main.Mininet1.assignSwController(
                        sw=str( i ),
                        ip1=ONOSIpList[ i - 1 ],
                        port1=defaultSwPort )
                elif i >= 8:
                    main.Mininet1.assignSwController(
                        sw=str( i ),
                        ip1=ONOSIpList[ 6 ],
                        port1=defaultSwPort )

        time.sleep( 20 )

        main.log.report( "Batch intent installation test of " +
                         str( batchIntentSize ) + " intent(s)" )

        batchResultList = []

        main.log.info( "Getting list of available devices" )
        deviceIdList = []
        jsonStr = main.ONOS1cli.devices()
        jsonObj = json.loads( jsonStr )
        for device in jsonObj:
            deviceIdList.append( device[ 'id' ] )

        # List of install / witdhraw latencies for each batch
        batchInstallLat = []
        batchWithdrawLat = []

        sleepTime = 10

        baseDir = "/tmp/"

        # Batch size increase loop
        for batch in range( 0, 5 ):
            # Max intent install measurement of all nodes
            # Resets after each batch calculation
            maxInstallLat = []
            maxWithdrawLat = []
            # Statistical gathering loop over number of iterations
            for i in range( 0, int( numIter ) ):
                main.log.info( "Pushing " +
                               str( int( batchIntentSize ) * int( nThread ) ) +
                               " intents. Iteration " + str( i ) )

                for node in range( 1, clusterCount + 1 ):
                    saveDir = baseDir + "batch_intent_" + str( node ) + ".txt"
                    main.ONOSbench.pushTestIntentsShell(
                        deviceIdList[ 0 ] + "/2",
                        deviceIdList[ 7 ] + "/2",
                        batchIntentSize,
                        saveDir, ONOSIpList[ node - 1 ],
                        numMult=nThread, appId=node )

                # Wait sufficient time for intents to start
                # installing
                time.sleep( sleepTime )

                intent = ""
                counter = 300
                while len( intent ) > 0 and counter > 0:
                    main.ONOS1cli.handle.sendline(
                        "intents | wc -l" )
                    main.ONOS1cli.handle.expect(
                        "intents | wc -l" )
                    main.ONOS1cli.handle.expect(
                        "onos>" )
                    intentTemp = main.ONOS1cli.handle.before()
                    intent = main.ONOS1cli.intents()
                    intent = json.loads( intent )
                    counter = counter - 1
                    time.sleep( 1 )

                time.sleep( 5 )

                for node in range( 1, clusterCount + 1 ):
                    saveDir = baseDir + "batch_intent_" + str( node ) + ".txt"
                    with open( saveDir ) as fOnos:
                        lineCount = 0
                        for line in fOnos:
                            line = line[ 1: ]
                            line = line.split( ": " )
                            main.log.info( "Line read: " + str( line ) )
                            #Prevent split method if line doesn't have
                            #space
                            if " " in str(line):
                                result = line[ 1 ].split( " " )[ 0 ]
                            else:
                                main.log.warn( "Empty line read" )
                                result = 0
                            # TODO: add parameters before appending latency
                            if lineCount == 0:
                                batchInstallLat.append( int( result ) )
                                installResult = result
                            elif lineCount == 1:
                                batchWithdrawLat.append( int( result ) )
                                withdrawResult = result
                            else:
                                main.log.warn("Invalid results")
                                installResult = 'NA'
                                withdrawResult = 'NA'
                            lineCount += 1
                    main.log.info( "Batch install latency for ONOS" +
                                   str( node ) + " with " +
                                   str( batchIntentSize ) + "intents: " +
                                   str( installResult ) + " ms" )
                    main.log.info( "Batch withdraw latency for ONOS" +
                                   str( node ) + " with " +
                                   str( batchIntentSize ) + "intents: " +
                                   str( withdrawResult ) + " ms" )

                #NOTE: END node loop

                if len( batchInstallLat ) > 0 and int( i ) > numIgnore:
                    maxInstallLat.append( max( batchInstallLat ) )
                elif len( batchInstallLat ) == 0:
                    # If I failed to read anything from the file,
                    # increase the wait time before checking intents
                    sleepTime += 30
                if len( batchWithdrawLat ) > 0 and int( i ) > numIgnore:
                    maxWithdrawLat.append( max( batchWithdrawLat ) )
                batchInstallLat = []
                batchWithdrawLat = []

                # Sleep in between iterations
                time.sleep( 5 )

            #NOTE: END iteration loop

            if maxInstallLat:
                avgInstallLat = str( round(
                                            sum( maxInstallLat ) /
                                            len( maxInstallLat )
                                          , 2 ))
                stdInstallLat = str( round(
                                    numpy.std(maxInstallLat), 2))
            else:
                avgInstallLat = "NA"
                stdInstallLat = "NA"
                main.log.report( "Batch installation failed" )
                assertion = main.FALSE

            if maxWithdrawLat:
                avgWithdrawLat = str( round(
                                            sum( maxWithdrawLat ) /
                                            len( maxWithdrawLat )
                                            , 2 ))
                stdWithdrawLat = str( round(
                                    numpy.std(maxWithdrawLat), 2))
            else:
                avgWithdrawLat = "NA"
                stdWithdrawLat = "NA"
                main.log.report( "Batch withdraw failed" )
                assertion = main.FALSE

            main.log.report( "Avg of batch installation latency " +
                             "of size " + str( batchIntentSize ) + ": " +
                             str( avgInstallLat ) + " ms" )
            main.log.report( "Std Deviation of batch installation latency " +
                             ": " +
                             str( stdInstallLat ) + " ms" )

            main.log.report( "Avg of batch withdraw latency " +
                             "of size " + str( batchIntentSize ) + ": " +
                             str( avgWithdrawLat ) + " ms" )
            main.log.report( "Std Deviation of batch withdraw latency " +
                             ": " +
                             str( stdWithdrawLat ) + " ms" )

            dbCmd = (
                "INSERT INTO intent_latency_tests VALUES("
                "'"+timeToPost+"','intent_latency_results',"
                ""+runNum+","+str(clusterCount)+","+str(batchIntentSize)+","
                ""+str(avgInstallLat)+","+str(stdInstallLat)+","
                ""+str(avgWithdrawLat)+","+str(stdWithdrawLat)+");"
            )

            # Write result to file (which is posted to DB by jenkins)
            fResult = open(intentFilePath, 'a')
            if dbCmd:        
                fResult.write(dbCmd+"\n")
            fResult.close()

            if batch == 0:
                batchIntentSize = 10
            elif batch == 1:
                batchIntentSize = 100
            elif batch == 2:
                batchIntentSize = 1000
            elif batch == 3:
                batchIntentSize = 2000
            if batch < 4:
                main.log.report( "Increasing batch intent size to " +
                             str(batchIntentSize) )

        #NOTE: END batch loop

        #main.log.info( "Removing all intents for next test case" )
        #jsonTemp = main.ONOS1cli.intents( jsonFormat=True )
        #jsonObjIntents = json.loads( jsonTemp )
        # if jsonObjIntents:
        #    for intents in jsonObjIntents:
        #        tempId = intents[ 'id' ]
            # main.ONOS1cli.removeIntent( tempId )
        #        main.ONOS1cli.removeIntent( tempId )

        utilities.assert_equals(
            expect=main.TRUE,
            actual=assertion,
            onpass="Batch intent install/withdraw test successful",
            onfail="Batch intent install/withdraw test failed" )

    def CASE5( self, main ):
        """
        Increase number of nodes and initiate CLI
        """
        import time
        import json

        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS2Ip = main.params[ 'CTRL' ][ 'ip2' ]
        ONOS3Ip = main.params[ 'CTRL' ][ 'ip3' ]
        ONOS4Ip = main.params[ 'CTRL' ][ 'ip4' ]
        ONOS5Ip = main.params[ 'CTRL' ][ 'ip5' ]
        ONOS6Ip = main.params[ 'CTRL' ][ 'ip6' ]
        ONOS7Ip = main.params[ 'CTRL' ][ 'ip7' ]

        global clusterCount
        clusterCount += 2
        main.log.report( "Increasing cluster size to " +
                         str( clusterCount ) )

        installResult = main.FALSE

        if clusterCount == 3:
            installResult1 = \
                main.ONOSbench.onosInstall( node=ONOS2Ip )
            installResult2 = \
                main.ONOSbench.onosInstall( node=ONOS3Ip )
            time.sleep( 5 )

            main.log.info( "Starting ONOS CLI" )
            main.ONOS2cli.startOnosCli( ONOS2Ip )
            main.ONOS3cli.startOnosCli( ONOS3Ip )

            installResult = installResult1 and installResult2

        if clusterCount == 5:
            main.log.info( "Installing ONOS on node 4 and 5" )
            installResult1 = \
                main.ONOSbench.onosInstall( node=ONOS4Ip )
            installResult2 = \
                main.ONOSbench.onosInstall( node=ONOS5Ip )

            main.log.info( "Starting ONOS CLI" )
            main.ONOS4cli.startOnosCli( ONOS4Ip )
            main.ONOS5cli.startOnosCli( ONOS5Ip )

            installResult = installResult1 and installResult2

        if clusterCount == 7:
            main.log.info( "Installing ONOS on node 6 and 7" )
            installResult1 = \
                main.ONOSbench.onosInstall( node=ONOS6Ip )
            installResult2 = \
                main.ONOSbench.onosInstall( node=ONOS7Ip )

            main.log.info( "Starting ONOS CLI" )
            main.ONOS6cli.startOnosCli( ONOS6Ip )
            main.ONOS7cli.startOnosCli( ONOS7Ip )

            installResult = installResult1 and installResult2

        time.sleep( 5 )

        if installResult == main.TRUE:
            assertion = main.TRUE
        else:
            assertion = main.FALSE

        utilities.assert_equals( expect=main.TRUE, actual=assertion,
                                onpass="Scale out to " + str( clusterCount ) +
                                " nodes successful",
                                onfail="Scale out to " + str( clusterCount ) +
                                " nodes failed" )

    def CASE7( self, main ):
        # TODO: Fix for scale-out scenario
        """
        Batch intent reroute latency
        """
        import time
        import json
        import requests
        import os
        import numpy
        global clusterCount

        ONOSIpList = []
        for i in range( 1, 8 ):
            ONOSIpList.append( main.params[ 'CTRL' ][ 'ip' + str( i ) ] )

        ONOSUser = main.params[ 'CTRL' ][ 'user' ]
        defaultSwPort = main.params[ 'CTRL' ][ 'port1' ]

        batchIntentSize = main.params[ 'TEST' ][ 'batchIntentSize' ]
        batchThreshMin = int( main.params[ 'TEST' ][ 'batchThresholdMin' ] )
        batchThreshMax = int( main.params[ 'TEST' ][ 'batchThresholdMax' ] )
        intfs = main.params[ 'TEST' ][ 'intfs' ]
        installTime = main.params[ 'JSON' ][ 'installedTime' ]

        # number of iterations of case
        numIter = main.params[ 'TEST' ][ 'numIter' ]
        numIgnore = int( main.params[ 'TEST' ][ 'numIgnore' ] )
        numSwitch = int( main.params[ 'TEST' ][ 'numSwitch' ] )
        nThread = main.params[ 'TEST' ][ 'numMult' ]

        main.log.report( "Batch intent installation test of " +
                         batchIntentSize + " intents" )

        batchResultList = []

        time.sleep( 10 )

        main.log.info( "Getting list of available devices" )
        deviceIdList = []
        jsonStr = main.ONOS1cli.devices()
        jsonObj = json.loads( jsonStr )
        for device in jsonObj:
            deviceIdList.append( device[ 'id' ] )

        batchInstallLat = []
        batchWithdrawLat = []
        sleepTime = 10

        baseDir = "/tmp/"
        maxInstallLat = []

        for i in range( 0, int( numIter ) ):
            main.log.info( "Pushing " +
                           str( int( batchIntentSize ) * int( nThread ) ) +
                           " intents. Iteration " + str( i ) )

            main.ONOSbench.pushTestIntentsShell(
                deviceIdList[ 0 ] + "/2",
                deviceIdList[ 7 ] + "/2",
                batchIntentSize, "/tmp/batch_install.txt",
                ONOSIpList[ 0 ], numMult="1", appId="1",
                report=False, options="--install" )
            # main.ONOSbench.pushTestIntentsShell(
            #    "of:0000000000001002/1",
            #    "of:0000000000002002/1",
            #    133, "/tmp/temp2.txt", "10.128.174.2",
            #    numMult="6", appId="2",report=False )

            # TODO: Check for installation success then proceed
            time.sleep( 30 )

            # NOTE: this interface is specific to
            #      topo-intentFlower.py topology
            #      reroute case.
            main.log.info( "Disabling interface " + intfs )
            main.Mininet1.handle.sendline(
                "sh ifconfig " + intfs + " down" )
            t0System = time.time() * 1000

            # TODO: Wait sufficient time for intents to install
            time.sleep( 10 )

            # TODO: get intent installation time

            # Obtain metrics from ONOS 1, 2, 3
            intentsJsonStr1 = main.ONOS1cli.intentsEventsMetrics()
            intentsJsonObj1 = json.loads( intentsJsonStr1 )
            # Parse values from the json object
            intentInstall1 = \
                intentsJsonObj1[ installTime ][ 'value' ]
            intentRerouteLat1 = \
                int( intentInstall1 ) - int( t0System )

            if clusterCount == 3:
                intentsJsonStr2 =\
                    main.ONOS2cli.intentsEventsMetrics()
                intentsJsonStr3 =\
                    main.ONOS3cli.intentsEventsMetrics()
                intentsJsonObj2 = json.loads( intentsJsonStr2 )
                intentsJsonObj3 = json.loads( intentsJsonStr3 )
                intentInstall2 = \
                    intentsJsonObj2[ installTime ][ 'value' ]
                intentInstall3 = \
                    intentsJsonObj3[ installTime ][ 'value' ]
                intentRerouteLat2 = \
                    int( intentInstall2 ) - int( t0System )
                intentRerouteLat3 = \
                    int( intentInstall3 ) - int( t0System )
            else:
                intentRerouteLat2 = 0
                intentRerouteLat3 = 0

            if clusterCount == 5:
                intentsJsonStr4 =\
                    main.ONOS4cli.intentsEventsMetrics()
                intentsJsonStr5 =\
                    main.ONOS5cli.intentsEventsMetrics()
                intentsJsonObj4 = json.loads( intentsJsonStr4 )
                intentsJsonObj5 = json.loads( intentsJsonStr5 )
                intentInstall4 = \
                    intentsJsonObj4[ installTime ][ 'value' ]
                intentInstall5 = \
                    intentsJsonObj5[ installTime ][ 'value' ]
                intentRerouteLat4 = \
                    int( intentInstall4 ) - int( t0System )
                intentRerouteLat5 = \
                    int( intentInstall5 ) - int( t0System )
            else:
                intentRerouteLat4 = 0
                intentRerouteLat5 = 0

            if clusterCount == 7:
                intentsJsonStr6 =\
                    main.ONOS6cli.intentsEventsMetrics()
                intentsJsonStr7 =\
                    main.ONOS7cli.intentsEventsMetrics()
                intentsJsonObj6 = json.loads( intentsJsonStr6 )
                intentsJsonObj7 = json.loads( intentsJsonStr7 )
                intentInstall6 = \
                    intentsJsonObj6[ installTime ][ 'value' ]
                intentInstall7 = \
                    intentsJsonObj7[ installTime ][ 'value' ]
                intentRerouteLat6 = \
                    int( intentInstall6 ) - int( t0System )
                intentRerouteLat7 = \
                    int( intentInstall7 ) - int( t0System )
            else:
                intentRerouteLat6 = 0
                intentRerouteLat7 = 0

            intentRerouteLatAvg = \
                ( intentRerouteLat1 +
                  intentRerouteLat2 +
                  intentRerouteLat3 +
                  intentRerouteLat4 +
                  intentRerouteLat5 +
                  intentRerouteLat6 +
                  intentRerouteLat7 ) / clusterCount

            main.log.info( "Intent reroute latency avg for iteration " +
                           str( i ) + ": " + str( intentRerouteLatAvg ) )
            # TODO: Remove intents for next iteration

            time.sleep( 5 )

            intentsStr = main.ONOS1cli.intents()
            intentsJson = json.loads( intentsStr )
            for intents in intentsJson:
                intentId = intents[ 'id' ]
                # TODO: make sure this removes all intents
                # print intentId
                if intentId:
                    main.ONOS1cli.removeIntent( intentId )

            main.Mininet1.handle.sendline(
                "sh ifconfig " + intfs + " up" )

            main.log.info( "Intents removed and port back up" )

    def CASE9( self, main ):
        count = 0
        swNum1 = 1
        swNum2 = 1
        appid = 0
        portNum1 = 1
        portNum2 = 1

        time.sleep( 30 )

        while True:
            # main.ONOS1cli.pushTestIntents(
                    #"of:0000000000001001/1",
                #"of:0000000000002001/1",
                #    100, numMult="10", appId="1" )
            # main.ONOS2cli.pushTestIntents(
            #    "of:0000000000001002/1",
            #    "of:0000000000002002/1",
            #    100, numMult="10", appId="2" )
            # main.ONOS2cli.pushTestIntents(
            #    "of:0000000000001003/1",
            #    "of:0000000000002003/1",
            #    100, numMult="10", appId="3" )
            count += 1

            if count >= 100:
                main.ONOSbench.handle.sendline(
                    "onos 10.128.174.1 intents-events-metrics >>" +
                    " /tmp/metrics_intents_temp.txt &" )
                count = 0

            arg1 = "of:000000000000100" + str( swNum1 ) + "/" + str( portNum1 )
            arg2 = "of:000000000000200" + str( swNum2 ) + "/" + str( portNum2 )

            swNum1 += 1

            if swNum1 > 7:
                swNum1 = 1
                swNum2 += 1
                if swNum2 > 7:
                    appid += 1

            if swNum2 > 7:
                swNum2 = 1

            main.ONOSbench.pushTestIntentsShell(
                arg1,
                arg2,
                100, "/tmp/temp.txt", "10.128.174.1",
                numMult="10", appId=appid, report=False )
            # main.ONOSbench.pushTestIntentsShell(
            #    "of:0000000000001002/1",
            #    "of:0000000000002002/1",
            #    133, "/tmp/temp2.txt", "10.128.174.2",
            #    numMult="6", appId="2",report=False )
            # main.ONOSbench.pushTestIntentsShell(
            #    "of:0000000000001003/1",
            #    "of:0000000000002003/1",
            #    133, "/tmp/temp3.txt", "10.128.174.3",
            #    numMult="6", appId="3",report=False )

            time.sleep( 0.2 )
