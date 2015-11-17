# CASE1 starts number of nodes specified in param file
#
# cameron@onlab.us

class SCPFswitchLat:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        import sys
        import re
        import os
        import time

        global init
        try:
            if type(init) is not bool:
                init = Fals
        except NameError:
            init = False

        #Load values from params file
        checkoutBranch = main.params[ 'GIT' ][ 'checkout' ]
        gitPull = main.params[ 'GIT' ][ 'autopull' ]
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        Apps = main.params[ 'ENV' ][ 'cellApps' ]
        BENCHIp = main.params[ 'BENCH' ][ 'ip' ]
        MN1Ip = main.params[ 'MN' ][ 'ip1' ]
        main.maxNodes = int(main.params[ 'max' ])
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        homeDir = os.path.expanduser('~')
        topoCfgFile = main.params['TEST']['topoConfigFile']
        topoCfgName = main.params['TEST']['topoConfigName']
        switchEventResultPath = main.params['DB']['switchEventResultPath']
        skipMvn = main.params ['TEST']['mci']
        testONpath = re.sub( "(tests)$", "bin", main.testDir )  # TestON/bin
        user = main.params[ 'CTRL' ][ 'user' ]

        # -- INIT SECTION, ONLY RUNS ONCE -- #
        if init == False:
            init = True
            global clusterCount             #number of nodes running
            global scale
            global commit
            global timeToPost
            global runNum
            global jenkinsBuildNumber
            global CLIs
            CLIs = []
            main.ONOSIp = []

            for i in range( 1, 8 ):
                CLIs.append( getattr( main, 'ONOS' + str( i ) + 'cli' ) )

            timeToPost = time.strftime('%Y-%m-%d %H:%M:%S')
            runNum = time.strftime('%d%H%M%S')

            try:
                jenkinsBuildNumber = str(os.environ['BUILD_NUMBER'])
                main.log.report( 'Jenkins build number: ' + jenkinsBuildNumber )
            except KeyError:
                jenkinsBuildNumber = str(0)
                main.log.info( 'Job is not run by jenkins. ' + 'Build number set to: ' + jenkinsBuildNumber)

            clusterCount = 0
            main.ONOSIp = main.ONOSbench.getOnosIps()

            scale = (main.params[ 'SCALE' ]).split(",")
            clusterCount = int(scale[0])

            #mvn clean install, for debugging set param 'skipCleanInstall' to yes to speed up test
            if skipMvn != "off":
                mvnResult = main.ONOSbench.cleanInstall()

            #git
            main.step( "Git checkout and pull " + checkoutBranch )
            if gitPull == 'on':
                checkoutResult = main.ONOSbench.gitCheckout( checkoutBranch )
                pullResult = main.ONOSbench.gitPull()

            else:
                checkoutResult = main.TRUE
                pullResult = main.TRUE
                main.log.info( "Skipped git checkout and pull" )

            main.log.step("Grabbing commit number")
            commit = main.ONOSbench.getVersion()       ####
            commit = (commit.split(" "))[1]

            temp = testONpath.replace("bin","") + "tests/SCPFswitchLat/Dependency/"
            main.ONOSbench.scp( main.Mininet1,
                                temp + "topo-perf-1sw.py",
                                main.Mininet1.home,
                                direction="to" )
            #main.ONOSbench.handle.expect(":~")

            main.step('Clearing previous DB log file')
            print switchEventResultPath
            fSwitchLog = open(switchEventResultPath, "w+")
            fSwitchLog.write("")
            fSwitchLog.close()

        # -- END OF INIT SECTION --#

        main.log.step("Adjusting scale")
        clusterCount = int(scale[0])
        scale.remove(scale[0])

        #kill off all onos processes
        main.log.step("Safety check, killing all ONOS processes before initiating environment setup")
        for node in range(main.maxNodes):
            main.ONOSbench.onosDie(main.ONOSIp[node])

        #Uninstall everywhere
        main.log.step( "Cleaning Enviornment..." )
        for i in range(main.maxNodes):
            main.log.info(" Uninstalling ONOS " + str(i) )
            main.ONOSbench.onosUninstall( main.ONOSIp[i] )
        main.log.info("Sleep 10 second for uninstall to settle...")
        time.sleep(10)
        main.ONOSbench.handle.sendline(" ")
        main.ONOSbench.handle.expect(":~")

        #construct the cell file
        main.log.info("Creating cell file")
        cellIp = []
        for node in range (clusterCount):
            cellIp.append(main.ONOSIp[node])

        main.ONOSbench.createCellFile(main.ONOSbench.ip_address, cellName, MN1Ip, str(Apps), cellIp)

        main.step( "Set Cell" )
        main.ONOSbench.setCell(cellName)

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()

        main.step( "verify cells" )
        verifyCellResult = main.ONOSbench.verifyCell()

        main.step('Starting mininet topology ')
        main.Mininet1.startNet()

        main.log.report( "Initializeing " + str( clusterCount ) + " node cluster." )
        for node in range(clusterCount):
            main.log.info("Starting ONOS " + str(node) + " at IP: " + main.ONOSIp[node])
            main.ONOSbench.onosInstall( node=main.ONOSIp[node])

        for i in range(50):
            time.sleep(15)
            print "attempt " + str(i)
            main.ONOSbench.handle.sendline("onos $OC1 summary")
            main.ONOSbench.handle.expect(":~")
            print main.ONOSbench.handle.before
            if "nodes=" in main.ONOSbench.handle.before:
                break

        for node in range(clusterCount):
            for i in range( 2 ):
                isup = main.ONOSbench.isup( main.ONOSIp[node] )
                if isup:
                    main.log.info("ONOS " + str(node) + " is up\n")
                    break
            if not isup:
                main.log.report( "ONOS " + str(node) + " didn't start!" )
        main.log.info("Startup sequence complete")

        #time.sleep(20)

        main.step('Start onos cli')
        for i in range(0,clusterCount):
            cli1 = CLIs[i].startOnosCli(main.ONOSIp[i])

        main.step( 'Configuring application parameters' )

        configName = 'org.onosproject.net.topology.impl.DefaultTopologyProvider'
        configParam = 'maxEvents 1'
        main.ONOSbench.onosCfgSet( main.ONOSIp[0], configName, configParam )
        configParam = 'maxBatchMs 0'
        main.ONOSbench.onosCfgSet( main.ONOSIp[0], configName, configParam )
        configParam = 'maxIdleMs 0'
        main.ONOSbench.onosCfgSet( main.ONOSIp[0], configName, configParam )

    def CASE2(self, main):
        print "Cluster size: " + str(clusterCount)
        """
        Assign s3 to ONOSbench and measure latency

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

        ONOSUser = main.params['CTRL']['user']
        numIter = main.params['TEST']['numIter']
        iterIgnore = int(main.params['TEST']['iterIgnore'])

        deviceTimestampKey = main.params['JSON']['deviceTimestamp']
        graphTimestampKey = main.params['JSON']['graphTimestamp']

        debugMode = main.params['TEST']['debugMode']
        onosLog = main.params['TEST']['onosLogFile']
        resultPath = main.params['DB']['switchEventResultPath']
        thresholdStr = main.params['TEST']['singleSwThreshold']
        thresholdObj = thresholdStr.split(',')
        thresholdMin = int(thresholdObj[0])
        thresholdMax = int(thresholdObj[1])

        # Look for 'role-request' messages,
        # which replaces the 'vendor' messages previously seen
        # on OVS 2.0.1
        tsharkTcpString = main.params[ 'TSHARK' ][ 'tcpSynAck' ]
        tsharkFeatureReply = main.params[ 'TSHARK' ][ 'featureReply' ]
        tsharkRoleRequest = main.params[ 'TSHARK' ][ 'roleRequest' ]
        tsharkOfString = main.params[ 'TSHARK' ][ 'ofpRoleReply' ]
        tsharkFinAckSequence = main.params[ 'TSHARK' ][ 'finAckSequence' ]

        tsharkOfOutput = '/tmp/tshark_of_topo.txt'
        tsharkTcpOutput = '/tmp/tshark_tcp_topo.txt'
        tsharkRoleOutput = '/tmp/tshark_role_request.txt'
        tsharkFeatureOutput = '/tmp/tshark_feature_reply.txt'
        tsharkFinAckOutput = '/tmp/tshark_fin_ack.txt'

        # Switch connect measurement list
        # TCP Syn/Ack -> Feature Reply latency collection for each node
        tcpToFeatureLatNodeIter = numpy.zeros((clusterCount, int(numIter)))
        # Feature Reply -> Role Request latency collection for each node
        featureToRoleRequestLatNodeIter = numpy.zeros((clusterCount,
            int(numIter)))
        # Role Request -> Role Reply latency collection for each node
        roleRequestToRoleReplyLatNodeIter = numpy.zeros((clusterCount,
            int(numIter)))
        # Role Reply -> Device Update latency collection for each node
        roleReplyToDeviceLatNodeIter = numpy.zeros((clusterCount,
            int(numIter)))
        # Device Update -> Graph Update latency collection for each node
        deviceToGraphLatNodeIter = numpy.zeros((clusterCount,
            int(numIter)))
        endToEndLatNodeIter = numpy.zeros((clusterCount, int(numIter)))

        # Switch disconnect measurement lists
        # Mininet Fin / Ack -> Mininet Ack
        finAckTransactionLatNodeIter = numpy.zeros((clusterCount,
            int(numIter)))
        # Mininet Ack -> Device Event
        ackToDeviceLatNodeIter = numpy.zeros((clusterCount,
            int(numIter)))
        # Device event -> Graph event
        deviceToGraphDiscLatNodeIter = numpy.zeros((clusterCount,
            int(numIter)))
        endToEndDiscLatNodeIter = numpy.zeros((clusterCount, int(numIter)))

        assertion = main.TRUE
        localTime = time.strftime('%x %X')
        localTime = localTime.replace('/', '')
        localTime = localTime.replace(' ', '_')
        localTime = localTime.replace(':', '')

        if debugMode == 'on':
            main.ONOSbench.tsharkPcap('eth0', '/tmp/single_sw_lat_pcap_' + localTime)
            main.log.info('Debug mode is on')

        main.log.report('Latency of adding one switch to controller')
        main.log.report('First ' + str(iterIgnore) + ' iterations ignored' + ' for jvm warmup time')
        main.log.report('Total iterations of test: ' + str(numIter))

        for i in range(0, int(numIter)):
            main.log.info('Starting tshark capture')
            main.ONOSbench.tsharkGrep(tsharkTcpString, tsharkTcpOutput)
            main.ONOSbench.tsharkGrep(tsharkOfString, tsharkOfOutput)
            main.ONOSbench.tsharkGrep(tsharkRoleRequest, tsharkRoleOutput)
            main.ONOSbench.tsharkGrep(tsharkFeatureReply, tsharkFeatureOutput)

            time.sleep(10)

            main.log.info('Assigning s3 to controller')
            main.Mininet1.assignSwController(sw='s3',
                    ip=main.ONOSIp[0])

            jsonStr = []
            for node in range (0, clusterCount):
                metricsSwUp = CLIs[node].topologyEventsMetrics()
                jsonStr.append(metricsSwUp)

            time.sleep(10)

            main.log.info('Stopping all Tshark processes')
            main.ONOSbench.tsharkStop()

            time.sleep(5)

            '''
            main.log.info('Copying over tshark files')
            os.system('scp ' + ONOSUser + '@' + main.ONOSIp[0] +
                    ':' + tsharkTcpOutput + ' /tmp/')
            os.system('scp ' + ONOSUser + '@' + main.ONOSIp[0] +
                    ':' + tsharkRoleOutput + ' /tmp/')
            os.system('scp ' + ONOSUser + '@' + main.ONOSIp[0] +
                    ':' + tsharkFeatureOutput + ' /tmp/')
            os.system('scp ' + ONOSUser + '@' +
                      main.ONOSIp[0] + ':' + tsharkOfOutput + ' /tmp/')
            '''

            # Get tcp syn / ack output
            time.sleep(1)

            tcpFile = open(tsharkTcpOutput, 'r')
            tempText = tcpFile.readline()
            tempText = tempText.split(' ')
            main.log.info('Object read in from TCP capture: ' + str(tempText))

            if len(tempText) > 1:
                t0Tcp = float(tempText[1]) * 1000.0
            else:
                main.log.error('Tshark output file for TCP' + ' returned unexpected results')
                t0Tcp = 0
                assertion = main.FALSE
            tcpFile.close()

            # Get Role reply output
            ofFile = open(tsharkOfOutput, 'r')
            lineOfp = ''
            while True:
                tempText = ofFile.readline()
                if tempText != '':
                    lineOfp = tempText
                else:
                    break
            obj = lineOfp.split(' ')
            main.log.info('Object read in from OFP capture: ' +
                    str(lineOfp))
            if len(obj) > 1:
                t0Ofp = float(obj[1]) * 1000.0
            else:
                main.log.error('Tshark output file for OFP' +
                        ' returned unexpected results')
                t0Ofp = 0
                assertion = main.FALSE
            ofFile.close()

            # Get role request output
            roleFile = open(tsharkRoleOutput, 'r')
            tempText = roleFile.readline()
            tempText = tempText.split(' ')
            if len(tempText) > 1:
                main.log.info('Object read in from role request capture:' +
                        str(tempText))
                roleTimestamp = float(tempText[1]) * 1000.0
            else:
                main.log.error('Tshark output file for role request' +
                        ' returned unexpected results')
                timeRoleRequest = 0
                assertion = main.FALSE
            roleFile.close()

            # Get feature reply output
            featureFile = open(tsharkFeatureOutput, 'r')
            tempText = featureFile.readline()
            tempText = tempText.split(' ')
            if len(tempText) > 1:
                main.log.info('Object read in from feature reply capture: '+
                        str(tempText))
                if tempText[1] != ' ' and float(tempText[1]) > 1400000000.0:
                    temp = tempText[1]
                elif tempText[2] != ' ' and float(tempText[2]) > 1400000000.0:
                    temp = tempText[2]
                else:
                    temp = 0
                featureTimestamp = float(temp) * 1000.0
            else:
                main.log.error('Tshark output file for feature reply' +
                        ' returned unexpected results')
                timeFeatureReply = 0
                assertion = main.FALSE
            featureFile.close()

            for node in range(0, clusterCount):
                nodeNum = node+1
                #metricsSwUp = CLIs[node].topologyEventsMetrics
                #jsonStr = metricsSwUp()
                jsonObj = json.loads(jsonStr[node])
                if jsonObj:
                    graphTimestamp = jsonObj[graphTimestampKey]['value']
                    deviceTimestamp = jsonObj[deviceTimestampKey]['value']
                else:
                    main.log.error( "Unexpected JSON object" )
                    # If we could not obtain the JSON object,
                    # set the timestamps to 0, which will be
                    # excluded from the measurement later on
                    # (realized as invalid)
                    graphTimestamp = 0
                    deviceTimestamp = 0

                endToEnd = int(graphTimestamp) - int(t0Tcp)

                # Below are measurement breakdowns of the end-to-end
                # measurement.
                tcpToFeature = int(featureTimestamp) - int(t0Tcp)
                featureToRole = int(roleTimestamp) - int(featureTimestamp)
                roleToOfp = float(t0Ofp) - float(roleTimestamp)
                ofpToDevice = float(deviceTimestamp) - float(t0Ofp)
                # Timestamps gathered from ONOS are millisecond
                # precision. They are returned as integers, thus no
                # need to be more precise than 'int'. However,
                # the processing seems to be mostly under 1 ms,
                # thus this may be a problem point to handle any
                # submillisecond output that we are unsure of.
                # For now, this will be treated as 0 ms if less than 1 ms
                deviceToGraph = int(graphTimestamp) - int(deviceTimestamp)

                if endToEnd >= thresholdMin and\
                   endToEnd < thresholdMax and i >= iterIgnore:
                    endToEndLatNodeIter[node][i] = endToEnd
                    main.log.info("ONOS "+str(nodeNum)+ " end-to-end: "+
                            str(endToEnd) + " ms")
                else:
                    main.log.info("ONOS "+str(nodeNum)+ " end-to-end "+
                            "measurement ignored due to excess in "+
                            "threshold or premature iteration: ")
                    main.log.info(str(endToEnd))

                if tcpToFeature >= thresholdMin and\
                   tcpToFeature < thresholdMax and i >= iterIgnore:
                    tcpToFeatureLatNodeIter[node][i] = tcpToFeature
                    main.log.info("ONOS "+str(nodeNum)+ " tcp-to-feature: "+
                            str(tcpToFeature) + " ms")
                else:
                    main.log.info("ONOS "+str(nodeNum)+ " tcp-to-feature "+
                            "measurement ignored due to excess in "+
                            "threshold or premature iteration: ")
                    main.log.info(str(tcpToFeature))

                if featureToRole >= thresholdMin and\
                   featureToRole < thresholdMax and i >= iterIgnore:
                    featureToRoleRequestLatNodeIter[node][i] = featureToRole
                    main.log.info("ONOS "+str(nodeNum)+ " feature-to-role: "+
                            str(featureToRole) + " ms")
                else:
                    main.log.info("ONOS "+str(nodeNum)+ " feature-to-role "+
                            "measurement ignored due to excess in "+
                            "threshold or premature iteration: ")
                    main.log.info(str(featureToRole))

                if roleToOfp >= thresholdMin and\
                   roleToOfp < thresholdMax and i >= iterIgnore:
                    roleRequestToRoleReplyLatNodeIter[node][i] = roleToOfp
                    main.log.info("ONOS "+str(nodeNum)+ " role-to-reply: "+
                            str(roleToOfp) + " ms")
                else:
                    main.log.info("ONOS "+str(nodeNum)+ " role-to-reply "+
                            "measurement ignored due to excess in "+
                            "threshold or premature iteration: ")
                    main.log.info(str(roleToOfp))

                if ofpToDevice >= thresholdMin and\
                   ofpToDevice < thresholdMax and i >= iterIgnore:
                    roleReplyToDeviceLatNodeIter[node][i] = ofpToDevice
                    main.log.info("ONOS "+str(nodeNum)+ " reply-to-device: "+
                            str(ofpToDevice) + " ms")
                else:
                    main.log.info("ONOS "+str(nodeNum)+ " reply-to-device "+
                            "measurement ignored due to excess in "+
                            "threshold or premature iteration: ")
                    main.log.info(str(ofpToDevice))

                if deviceToGraph >= thresholdMin and\
                   deviceToGraph < thresholdMax and i >= iterIgnore:
                    deviceToGraphLatNodeIter[node][i] = deviceToGraph
                    main.log.info("ONOS "+str(nodeNum)+ " device-to-graph: "+
                            str(deviceToGraph) + " ms")
                else:
                    if deviceToGraph == 0:
                        deviceToGraphLatNodeIter[node][i] = 0
                        main.log.info("ONOS "+str(nodeNum) +
                            " device-to-graph measurement "+
                            "was set to 0 ms because of precision "+
                            "uncertainty. ")
                    else:
                        main.log.info("ONOS "+str(nodeNum)+
                            " device-to-graph "+
                            "measurement ignored due to excess in "+
                            "threshold or premature iteration: ")
                        main.log.info(str(deviceToGraph))

            # ********************
            time.sleep(5)

            # Get device id to remove
            deviceIdJsonStr = main.ONOS1cli.devices()

            main.log.info( "Device obj obtained: " + str(deviceIdJsonStr) )
            deviceId = json.loads(deviceIdJsonStr)

            deviceList = []
            for device in deviceId:
                deviceList.append(device['id'])

            # Measure switch down metrics
            # TCP FIN/ACK -> TCP FIN
            # TCP FIN -> Device Event
            # Device Event -> Graph Event
            # Capture switch down FIN / ACK packets

            # The -A 1 grep option allows us to grab 1 extra line after the
            # last tshark output grepped originally
            main.ONOSbench.tsharkGrep( tsharkFinAckSequence, tsharkFinAckOutput,
                    grepOptions = '-A 1' )

            time.sleep( 5 )

            removeJsonList = []
            main.step('Remove switch from controller')
            main.Mininet1.deleteSwController('s3')
            firstDevice = deviceList[0]

            time.sleep( 5 )

            # We need to get metrics before removing
            # device from the store below.
            for node in range(0, clusterCount):
                metricsSwDown = CLIs[node].topologyEventsMetrics
                jsonStr = metricsSwDown()
                removeJsonList.append( json.loads(jsonStr) )

            main.ONOSbench.tsharkStop()

            main.log.info( "Removing device " +str(firstDevice)+
                    " from ONOS" )

            #if deviceId:
            main.ONOS1cli.deviceRemove(firstDevice)

            #main.log.info('Copying over tshark files')
            #os.system('scp ' + ONOSUser + '@' + main.ONOSIp[0] + ':' + tsharkFinAckOutput + ' /tmp/')

            time.sleep( 10 )
            finAckOutputList = []
            with open(tsharkFinAckOutput, 'r') as f:
                tempLine = f.readlines()
                main.log.info('Object read in from FinAck capture: ' +
                    "\n".join(tempLine))

                index = 1
                for line in tempLine:
                    obj = line.split(' ')

                    # There are at least 3 objects in field (valid
                    # tshark output is lengthy)
                    if len(obj) > 2:
                        # If first index of object is like an epoch time
                        if obj[1] != ' ' and float(obj[1]) > 1400000000.0:
                            temp = obj[1]
                        elif obj[2] != ' 'and float(obj[2]) > 1400000000.0:
                            temp = obj[2]
                        elif obj[3] != ' 'and float(obj[3]) > 1400000000.0:
                            temp = obj[3]
                        else:
                            temp = 0
                        if index == 1:
                            tFinAck = float(temp) * 1000.0
                            main.log.info("DEBUG-- tFinAck: " + str(tFinAck))
                        elif index == 3:
                            tAck = float(temp) * 1000.0
                            main.log.info("DEBUG-- tAck: " + str(tAck))
                        else:
                            tAck = 0
                    else:
                        main.log.error('Tshark output file for OFP' +
                            ' returned unexpected results')
                        tFinAck = 0
                        tAck = 0
                        assertion = main.FALSE

                    index += 1
                main.log.info("DEBUG-- tFinAck: " + str(tFinAck))
                main.log.info("DEBUG-- tAck: " + str(tAck))

            # with open() as f takes care of closing file

            time.sleep(5)

            for node in range(0, clusterCount):
                nodeNum = node+1
                jsonObj = removeJsonList[node]
                if jsonObj:
                    graphTimestamp = jsonObj[graphTimestampKey]['value']
                    deviceTimestamp = jsonObj[deviceTimestampKey]['value']
                    main.log.info("Graph timestamp: "+str(graphTimestamp))
                    main.log.info("Device timestamp: "+str(deviceTimestamp))
                else:
                    main.log.error( "Unexpected JSON object" )
                    # If we could not obtain the JSON object,
                    # set the timestamps to 0, which will be
                    # excluded from the measurement later on
                    # (realized as invalid)
                    graphTimestamp = 0
                    deviceTimestamp = 0

                finAckTransaction = float(tAck) - float(tFinAck)
                ackToDevice = float(deviceTimestamp) - float(tAck)
                deviceToGraph = float(graphTimestamp) - float(deviceTimestamp)
                endToEndDisc = int(graphTimestamp) - int(tFinAck)
                main.log.info("DEBUG-- endToEndDisc = graphTimestamp - tFinAck  == (" + str(graphTimestamp) + "-" + str(tFinAck) + ")") 

                if endToEndDisc >= thresholdMin and\
                   endToEndDisc < thresholdMax and i >= iterIgnore:
                    endToEndDiscLatNodeIter[node][i] = endToEndDisc
                    main.log.info("ONOS "+str(nodeNum) +
                            "end-to-end disconnection: "+
                            str(endToEndDisc) + " ms" )
                else:
                    main.log.info("ONOS " + str(nodeNum) +
                            " end-to-end disconnection "+
                            "measurement ignored due to excess in "+
                            "threshold or premature iteration: ")
                    main.log.info(str(endToEndDisc))

                if finAckTransaction >= thresholdMin and\
                   finAckTransaction < thresholdMax and i >= iterIgnore:
                    finAckTransactionLatNodeIter[node][i] = finAckTransaction
                    main.log.info("ONOS "+str(nodeNum)+
                            " fin/ack transaction: "+
                            str(finAckTransaction) + " ms")
                else:
                    main.log.info("ONOS "+str(nodeNum)+
                            " fin/ack transaction "+
                            "measurement ignored due to excess in "+
                            "threshold or premature iteration: ")
                    main.log.info(str(finAckTransaction))

                if ackToDevice >= thresholdMin and\
                   ackToDevice < thresholdMax and i >= iterIgnore:
                    ackToDeviceLatNodeIter[node][i] = ackToDevice
                    main.log.info("ONOS "+str(nodeNum)+
                            " ack-to-device: "+
                            str(ackToDevice) + " ms")
                else:
                    main.log.info("ONOS "+str(nodeNum)+
                            " ack-to-device "+
                            "measurement ignored due to excess in "+
                            "threshold or premature iteration: ")
                    main.log.info(str(ackToDevice))

                if deviceToGraph >= thresholdMin and\
                   deviceToGraph < thresholdMax and i >= iterIgnore:
                    deviceToGraphDiscLatNodeIter[node][i] = deviceToGraph
                    main.log.info("ONOS "+str(nodeNum)+
                            " device-to-graph disconnect: "+
                            str(deviceToGraph) + " ms")
                else:
                    main.log.info("ONOS "+str(nodeNum)+
                            " device-to-graph disconnect "+
                            "measurement ignored due to excess in "+
                            "threshold or premature iteration: ")
                    main.log.info(str(deviceToGraph))

        endToEndAvg = 0
        ofpToGraphAvg = 0
        dbCmdList = []
        for node in range(0, clusterCount):
            # List of latency for each node
            endToEndList = []
            tcpToFeatureList = []
            featureToRoleList = []
            roleToOfpList = []
            ofpToDeviceList = []
            deviceToGraphList = []

            finAckTransactionList = []
            ackToDeviceList = []
            deviceToGraphDiscList = []
            endToEndDiscList = []

            # LatNodeIter 2d arrays contain all iteration latency
            # for each node of the current scale cluster size
            # Switch connection measurements
            # Set further acceptance criteria for measurements
            # here if you would like to filter reporting results
            for item in endToEndLatNodeIter[node]:
                if item > 0.0:
                    endToEndList.append(item)

            for item in tcpToFeatureLatNodeIter[node]:
                if item > 0.0:
                    tcpToFeatureList.append(item)

            for item in featureToRoleRequestLatNodeIter[node]:
                if item > 0.0:
                    featureToRoleList.append(item)

            for item in roleRequestToRoleReplyLatNodeIter[node]:
                if item > 0.0:
                    roleToOfpList.append(item)

            for item in roleReplyToDeviceLatNodeIter[node]:
                if item >= 0.0:
                    ofpToDeviceList.append(item)

            for item in featureToRoleRequestLatNodeIter[node]:
                if item > 0.0:
                    featureToRoleList.append(item)

            for item in deviceToGraphLatNodeIter[node]:
                if item >= 0.0:
                    deviceToGraphList.append(item)

            # Switch disconnect measurements
            for item in endToEndDiscLatNodeIter[node]:
                if item > 0.0:
                    endToEndDiscList.append(item)

            for item in finAckTransactionLatNodeIter[node]:
                if item > 0.0:
                    finAckTransactionList.append(item)

            for item in ackToDeviceLatNodeIter[node]:
                if item > 0.0:
                    ackToDeviceList.append(item)

            for item in deviceToGraphDiscLatNodeIter[node]:
                if item >= 0.0:
                    deviceToGraphDiscList.append(item)

            endToEndAvg = round(numpy.mean(endToEndList), 2)
            endToEndStdDev = round(numpy.std(endToEndList), 2)
            main.log.info("endToEndList: " + str(endToEndList))

            tcpToFeatureAvg = round(numpy.mean(tcpToFeatureList), 2)
            tcpToFeatureStdDev = round(numpy.std(tcpToFeatureList), 2)
            main.log.info("tcpToFeatureList: " + str(tcpToFeatureList))

            featureToRoleAvg = round(numpy.mean(featureToRoleList), 2)
            featureToRoleStdDev = round(numpy.std(featureToRoleList), 2)
            main.log.info("featureToRoleList: " + str(featureToRoleList)) 

            roleToOfpAvg = round(numpy.mean(roleToOfpList), 2)
            roleToOfpStdDev = round(numpy.std(roleToOfpList), 2)
            main.log.info("roleToOfList: " + str(roleToOfpList))

            ofpToDeviceAvg = round(numpy.mean(ofpToDeviceList), 2)
            ofpToDeviceStdDev = round(numpy.std(ofpToDeviceList), 2)
            main.log.info("ofpToDeviceList: " + str(ofpToDeviceList))

            deviceToGraphAvg = round(numpy.mean(deviceToGraphList), 2)
            deviceToGraphStdDev = round(numpy.std(deviceToGraphList), 2)
            main.log.info("deviceToGraphList: " + str(deviceToGraphList))

            endToEndDiscAvg = round(numpy.mean(endToEndDiscList), 2)
            endToEndDiscStdDev = round(numpy.std(endToEndDiscList), 2)
            main.log.info("endToEndDiscList: " + str(endToEndDiscList))

            finAckAvg = round(numpy.mean(finAckTransactionList), 2)
            finAckStdDev = round(numpy.std(finAckTransactionList), 2)
            main.log.info("finAckTransactionList: " + str(finAckTransactionList))

            ackToDeviceAvg = round(numpy.mean(ackToDeviceList), 2)
            ackToDeviceStdDev = round(numpy.std(ackToDeviceList), 2)
            main.log.info("ackToDeviceList: " + str(ackToDeviceList))

            deviceToGraphDiscAvg = round(numpy.mean(deviceToGraphDiscList), 2)
            deviceToGraphDiscStdDev = round(numpy.std(deviceToGraphDiscList), 2)
            main.log.info("deviceToGraphDiscList: " + str(deviceToGraphDiscList))

            main.log.report(' - Node ' + str(node + 1) + ' Summary - ')
            main.log.report(' - Switch Connection Statistics - ')

            main.log.report(' End-to-end Avg: ' + str(endToEndAvg) +
                    ' ms' + ' End-to-end Std dev: ' +
                    str(endToEndStdDev) + ' ms')

            main.log.report(' Tcp-to-feature-reply Avg: ' +
                    str(tcpToFeatureAvg) + ' ms')
            main.log.report(' Tcp-to-feature-reply Std dev: '+
                    str(tcpToFeatureStdDev) + ' ms')

            main.log.report(' Feature-reply-to-role-request Avg: ' +
                    str(featureToRoleAvg) + ' ms')
            main.log.report(' Feature-reply-to-role-request Std Dev: ' +
                    str(featureToRoleStdDev) + ' ms')

            main.log.report(' Role-request-to-role-reply Avg: ' +
                    str(roleToOfpAvg) +' ms')
            main.log.report(' Role-request-to-role-reply Std dev: ' +
                    str(roleToOfpStdDev) + ' ms')

            main.log.report(' Role-reply-to-device Avg: ' +
                    str(ofpToDeviceAvg) +' ms')
            main.log.report(' Role-reply-to-device Std dev: ' +
                    str(ofpToDeviceStdDev) + ' ms')

            main.log.report(' Device-to-graph Avg: ' +
                    str(deviceToGraphAvg) + ' ms')
            main.log.report( 'Device-to-graph Std dev: ' +
                    str(deviceToGraphStdDev) + ' ms')

            main.log.report(' - Switch Disconnection Statistics - ')
            main.log.report(' End-to-end switch disconnect Avg: ' +
                    str(endToEndDiscAvg) + ' ms')
            main.log.report(' End-to-end switch disconnect Std dev: ' +
                    str(endToEndDiscStdDev) + ' ms')
            main.log.report(' Fin/Ack-to-Ack Avg: ' + str(finAckAvg) + ' ms')
            main.log.report(' Fin/Ack-to-Ack Std dev: ' +
                    str(finAckStdDev) + ' ms')

            main.log.report(' Ack-to-device Avg: ' + str(ackToDeviceAvg) +
                    ' ms')
            main.log.report(' Ack-to-device Std dev: ' + str(ackToDeviceStdDev) +
                    ' ms')

            main.log.report(' Device-to-graph (disconnect) Avg: ' +
                    str(deviceToGraphDiscAvg) + ' ms')
            main.log.report(' Device-to-graph (disconnect) Std dev: ' +
                    str(deviceToGraphDiscStdDev) + ' ms')

            # For database schema, refer to Amazon web services
            dbCmdList.append(
                    "'" + timeToPost + "','switch_latency_results'," +
                    jenkinsBuildNumber + ',' + str(clusterCount) + ",'baremetal" +
                    str(node + 1) + "'," +
                    str(endToEndAvg) + ',' +
                    str(tcpToFeatureAvg) + ',' +
                    str(featureToRoleAvg) + ',' +
                    str(roleToOfpAvg) + ',' +
                    str(ofpToDeviceAvg) + ',' +
                    str(deviceToGraphAvg) + ',' +
                    str(endToEndDiscAvg) + ',' +
                    str(finAckAvg) + ',' +
                    str(ackToDeviceAvg) + ',' +
                    str(deviceToGraphDiscAvg))

        if debugMode == 'on':
            main.ONOSbench.cpLogsToDir('/opt/onos/log/karaf.log',
                    '/tmp/', copyFileName='sw_lat_karaf')
        fResult = open(resultPath, 'a')
        for line in dbCmdList:
            if line:
                fResult.write(line + '\n')
                main.log.report(line)
        fResult.close()

        assertion = main.TRUE

        utilities.assert_equals(expect=main.TRUE, actual=assertion,
                onpass='Switch latency test successful',
                onfail='Switch latency test failed')

        main.Mininet1.stopNet()
