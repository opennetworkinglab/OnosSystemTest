# 2015.03.12 10:22:05 PDT
#Embedded file name: ../tests/TopoPerfNextBM/TopoPerfNextBM.py
import time
import sys
import os
import re

class TopoPerfNextBM:

    def __init__(self):
        self.default = ''

    def CASE1(self, main):
        """
        ONOS startup sequence
        """
        global clusterCount
        global timeToPost
        global runNum

        import time
        clusterCount = 1
        timeToPost = time.strftime('%Y-%m-%d %H:%M:%S')
        runNum = time.strftime('%d%H%M%S')
        cellName = main.params['ENV']['cellName']
        gitPull = main.params['GIT']['autoPull']
        checkoutBranch = main.params['GIT']['checkout']
       
        global CLIs
        CLIs = []
        global nodes
        nodes = []
        global nodeIpList
        nodeIpList = []
        for i in range( 1, 8 ):
            CLIs.append( getattr( main, 'ONOS' + str( i ) + 'cli' ) )
            nodes.append( getattr( main, 'ONOS' + str( i ) ) )
            nodeIpList.append( main.params[ 'CTRL' ][ 'ip'+str(i) ] )

        MN1Ip = main.params['MN']['ip1']
        BENCHIp = main.params['BENCH']['ip']
        cellFeatures = main.params['ENV']['cellFeatures']
        topoCfgFile = main.params['TEST']['topoConfigFile']
        topoCfgName = main.params['TEST']['topoConfigName']
        portEventResultPath = main.params['DB']['portEventResultPath']
        switchEventResultPath = main.params['DB']['switchEventResultPath']
        mvnCleanInstall = main.params['TEST']['mci']
        
        main.case('Setting up test environment')

        # NOTE: Below is deprecated after new way to install features
        #main.log.info('Copying topology event accumulator config' +
        #        ' to ONOS /package/etc')
        #main.ONOSbench.handle.sendline('cp ~/' +
        #        topoCfgFile + ' ~/ONOS/tools/package/etc/' +
        #        topoCfgName)
        #main.ONOSbench.handle.expect('\\$')
        
        main.log.report('Setting up test environment')
        
        main.step('Starting mininet topology ')
        main.Mininet1.startNet()
        
        main.step('Cleaning previously installed ONOS if any')
        # Nodes 2 ~ 7
        for i in range( 1, 7 ):
            main.ONOSbench.onosUninstall(nodeIp=nodeIpList[i])
        
        main.step('Clearing previous DB log file')
        
        fPortLog = open(portEventResultPath, 'w')
        fPortLog.write('')
        fPortLog.close()
        fSwitchLog = open(switchEventResultPath, 'w')
        fSwitchLog.write('')
        fSwitchLog.close()
        
        main.step('Creating cell file')
        cellFileResult = main.ONOSbench.createCellFile(
                BENCHIp, cellName, MN1Ip, cellFeatures, nodeIpList[0])
        
        main.step('Applying cell file to environment')
        cellApplyResult = main.ONOSbench.setCell(cellName)
        verifyCellResult = main.ONOSbench.verifyCell()
        
        main.step('Git checkout and pull ' + checkoutBranch)
        if gitPull == 'on':
            checkoutResult = main.TRUE
            pullResult = main.ONOSbench.gitPull()
        else:
            checkoutResult = main.TRUE
            pullResult = main.TRUE
            main.log.info('Skipped git checkout and pull')
        
        main.log.report('Commit information - ')
        main.ONOSbench.getVersion(report=True)
        main.step('Using mvn clean & install')
        if mvnCleanInstall == 'on':
            mvnResult = main.ONOSbench.cleanInstall()
        elif mvnCleanInstall == 'off':
            main.log.info('mci turned off by settings')
            mvnResult = main.TRUE
        main.step('Set cell for ONOS cli env')
        CLIs[0].setCell(cellName)
        
        main.step('Creating ONOS package')
        packageResult = main.ONOSbench.onosPackage()
        
        main.step('Installing ONOS package')
        install1Result = main.ONOSbench.onosInstall(node=nodeIpList[0])
        
        time.sleep(10)
        
        main.step('Start onos cli')
        cli1 = CLIs[0].startOnosCli(nodeIpList[0])
        
        main.step( 'activating essential applications' )
        CLIs[0].activateApp( 'org.onosproject.metrics' )
        CLIs[0].activateApp( 'org.onosproject.openflow' )

        main.step( 'Configuring application parameters' )
        
        configName = 'org.onosproject.net.topology.impl.DefaultTopologyProvider'
        configParam = 'maxEvents 1'
        main.ONOSbench.onosCfgSet( nodeIpList[0], configName, configParam )
        configParam = 'maxBatchMs 0'
        main.ONOSbench.onosCfgSet( nodeIpList[0], configName, configParam )
        configParam = 'maxIdleMs 0'
        main.ONOSbench.onosCfgSet( nodeIpList[0], configName, configParam )
        
        utilities.assert_equals(expect=main.TRUE,
                actual=cellFileResult and cellApplyResult and\
                        verifyCellResult and checkoutResult and\
                        pullResult and mvnResult and\
                        install1Result,
                        onpass='Test Environment setup successful',
                        onfail='Failed to setup test environment')

    def CASE2(self, main):
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
        
        ONOSUser = main.params['CTRL']['user']
        defaultSwPort = main.params['CTRL']['port1']
        numIter = main.params['TEST']['numIter']
        iterIgnore = int(main.params['TEST']['iterIgnore'])
        
        deviceTimestampKey = main.params['JSON']['deviceTimestamp']
        graphTimestampKey = main.params['JSON']['graphTimestamp']

        debugMode = main.params['TEST']['debugMode']
        onosLog = main.params['TEST']['onosLogFile']
        resultPath = main.params['DB']['switchEventResultPath']
        thresholdStr = main.params['TEST']['singleSwThreshold']
        thresholdObj = thresholdStr.split(',')
        thresholdMin = float(thresholdObj[0])
        thresholdMax = float(thresholdObj[1])
       
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
        ofpToGraphLatNodeIter = numpy.zeros((clusterCount, int(numIter)))
        ofpToDeviceLatNodeIter = numpy.zeros((clusterCount, int(numIter)))
        
        tcpToOfpLatIter = []
        tcpToFeatureLatIter = []
        tcpToRoleLatIter = []
        assertion = main.TRUE
        localTime = time.strftime('%x %X')
        localTime = localTime.replace('/', '')
        localTime = localTime.replace(' ', '_')
        localTime = localTime.replace(':', '')

        if debugMode == 'on':
            main.ONOS1.tsharkPcap('eth0',
                    '/tmp/single_sw_lat_pcap_' + localTime)
            main.log.info('Debug mode is on')
        main.log.report('Latency of adding one switch to controller')
        main.log.report('First ' + str(iterIgnore) +
                ' iterations ignored' + ' for jvm warmup time')
        main.log.report('Total iterations of test: ' + str(numIter))
        
        for i in range(0, int(numIter)):
            main.log.info('Starting tshark capture')
            main.ONOS1.tsharkGrep(tsharkTcpString, tsharkTcpOutput)
            main.ONOS1.tsharkGrep(tsharkOfString, tsharkOfOutput)
            main.ONOS1.tsharkGrep(tsharkRoleRequest, tsharkRoleOutput)
            main.ONOS1.tsharkGrep(tsharkFeatureReply, tsharkFeatureOutput)

            time.sleep(10)
           
            main.log.info('Assigning s3 to controller')
            main.Mininet1.assignSwController(sw='3',
                    ip1=nodeIpList[0], port1=defaultSwPort)
            
            time.sleep(10)
            
            main.log.info('Stopping all Tshark processes')
            main.ONOS1.tsharkStop()
            
            main.log.info('Copying over tshark files')
            os.system('scp ' + ONOSUser + '@' + nodeIpList[0] +
                    ':' + tsharkTcpOutput + ' /tmp/')
            os.system('scp ' + ONOSUser + '@' + nodeIpList[0] +
                    ':' + tsharkRoleOutput + ' /tmp/')
            os.system('scp ' + ONOSUser + '@' + nodeIpList[0] +
                    ':' + tsharkFeatureOutput + ' /tmp/')
            os.system('scp ' + ONOSUser + '@' +
                      nodeIpList[0] + ':' + tsharkOfOutput + ' /tmp/')
           
            # Get tcp syn / ack output
            time.sleep(5)
            tcpFile = open(tsharkTcpOutput, 'r')
            tempText = tcpFile.readline()
            tempText = tempText.split(' ')
            main.log.info('Object read in from TCP capture: ' +
                    str(tempText))
            
            if len(tempText) > 1:
                t0Tcp = float(tempText[1]) * 1000.0
            else:
                main.log.error('Tshark output file for TCP' +
                        ' returned unexpected results')
                t0Tcp = 0
                assertion = main.FALSE
            tcpFile.close()
           
            # Get Role reply output
            time.sleep(5)
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
                featureTimestamp = float(tempText[1]) * 1000.0
            else:
                main.log.error('Tshark output file for feature reply' +
                        ' returned unexpected results')
                timeFeatureReply = 0
                assertion = main.FALSE
            featureFile.close()

            # TODO: calculate feature reply, role request times
            # stack measurements correctly and report

            #TODO: Refactor in progress

            for node in range(0, clusterCount):
                nodeNum = node+1
                metricsSwUp = CLIs[node].topologyEventsMetrics
                jsonStr = metricsSwUp()
                jsonObj = json.loads(jsonStr)
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
                roleToOfp = int(t0Ofp) - int(roleTimestamp)
                ofpToDevice = int(deviceTimestamp) - int(t0Ofp)
                deviceToGraph = float(graphTimestamp) - float(deviceTimestamp)
                
                if endToEnd > thresholdMin and\
                   endToEnd < thresholdMax and i >= iterIgnore:
                    endToEndLatNodeIter[node][i] = endToEnd 
                    main.log.info("ONOS "+str(nodeNum)+ " end-to-end: "+
                            str(endToEnd) + " ms")
                else:
                    main.log.info("ONOS "+str(nodeNum)+ " end-to-end "+
                            "measurement ignored due to excess in "+
                            "threshold or premature iteration")

                if tcpToFeature > thresholdMin and\
                   tcpToFeature < thresholdMax and i >= iterIgnore:
                    tcpToFeatureLatNodeIter[node][i] = tcpToFeature 
                    main.log.info("ONOS "+str(nodeNum)+ " tcp-to-feature: "+
                            str(tcpToFeature) + " ms")
                else:
                    main.log.info("ONOS "+str(nodeNum)+ " tcp-to-feature "+
                            "measurement ignored due to excess in "+
                            "threshold or premature iteration")

                if featureToRole > thresholdMin and\
                   featureToRole < thresholdMax and i >= iterIgnore:
                    featureToRoleRequestLatNodeIter[node][i] = featureToRole 
                    main.log.info("ONOS "+str(nodeNum)+ " feature-to-role: "+
                            str(featureToRole) + " ms")
                else:
                    main.log.info("ONOS "+str(nodeNum)+ " feature-to-role "+
                            "measurement ignored due to excess in "+
                            "threshold or premature iteration")

                if roleToOfp > thresholdMin and\
                   roleToOfp < thresholdMax and i >= iterIgnore:
                    roleRequestToRoleReplyLatNodeIter[node][i] = roleToOfp
                    main.log.info("ONOS "+str(nodeNum)+ " role-to-reply: "+
                            str(roleToOfp) + " ms")
                else:
                    main.log.info("ONOS "+str(nodeNum)+ " role-to-reply "+
                            "measurement ignored due to excess in "+
                            "threshold or premature iteration")
                
                if ofpToDevice > thresholdMin and\
                   ofpToDevice < thresholdMax and i >= iterIgnore:
                    roleReplyToDeviceLatNodeIter[node][i] = ofpToDevice 
                    main.log.info("ONOS "+str(nodeNum)+ " reply-to-device: "+
                            str(ofpToDevice) + " ms")
                else:
                    main.log.info("ONOS "+str(nodeNum)+ " role-to-reply "+
                            "measurement ignored due to excess in "+
                            "threshold or premature iteration")

                if deviceToGraph > thresholdMin and\
                   deviceToGraph < thresholdMax and i >= iterIgnore:
                    deviceToGraphLatNodeIter[node][i] = deviceToGraph
                    main.log.info("ONOS "+str(nodeNum)+ " device-to-graph: "+
                            str(deviceToGraph) + " ms")
                else:
                    main.log.info("ONOS "+str(nodeNum)+ " device-to-graph "+
                            "measurement ignored due to excess in "+
                            "threshold or premature iteration")
                                
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

            main.ONOS1.tsharkGrep( tsharkFinAckSequence, tsharkFinAckOutput, 
                    grepOptions = '-A 1' )
           
            time.sleep( 5 )

            removeJsonList = []

            main.step('Remove switch from controller')
            main.Mininet1.deleteSwController('s3')
            firstDevice = deviceList[0] 
            main.log.info( "Removing device " +str(firstDevice)+
                    " from ONOS" )
            
            time.sleep( 5 )
           
            # We need to get metrics before removing
            # device from the store below.
            for node in range(0, clusterCount):
                metricsSwDown = CLIs[node].topologyEventsMetrics
                jsonStr = metricsSwDown()
                removeJsonList.append( json.loads(jsonStr) ) 
            
            #if deviceId:
            main.ONOS1cli.deviceRemove(firstDevice)
           
            main.ONOS1.tsharkStop()

            main.log.info('Copying over tshark files')
            os.system('scp ' + ONOSUser + '@' + nodeIpList[0] +
                    ':' + tsharkFinAckOutput + ' /tmp/')
           
            time.sleep( 10 )
            finAckOutputList = []
            with open(tsharkFinAckOutput, 'r') as f:
                tempLine = f.readlines()
                main.log.info('Object read in from FinAck capture: ' +
                    str(tempLine))
                
                index = 1
                for line in tempLine:
                    obj = line.split(' ')
            
                    if len(obj) > 1:
                        if index == 1:
                            tFinAck = float(obj[1]) * 1000.0
                        elif index == 3:
                            tAck = float(obj[1]) * 1000.0
                    else:
                        main.log.error('Tshark output file for OFP' +
                            ' returned unexpected results')
                        tFinAck = 0
                        tAck = 0
                        assertion = main.FALSE
                    
                    index = index+1

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
               
                finAckTransaction = int(tAck) - int(tFinAck)
                ackToDevice = int(deviceTimestamp) - int(tAck)
                deviceToGraph = int(graphTimestamp) - int(deviceTimestamp)
                
                if finAckTransaction > thresholdMin and\
                   finAckTransaction < thresholdMax and i >= iterIgnore:
                    finAckTransactionLatNodeIter[node][i] = finAckTransaction 
                    main.log.info("ONOS "+str(nodeNum)+
                            " fin/ack transaction: "+
                            str(finAckTransaction) + " ms")
                else:
                    main.log.info("ONOS "+str(nodeNum)+
                            " fin/ack transaction "+
                            "measurement ignored due to excess in "+
                            "threshold or premature iteration")
                
                if ackToDevice > thresholdMin and\
                   ackToDevice < thresholdMax and i >= iterIgnore:
                    ackToDeviceLatNodeIter[node][i] = ackToDevice
                    main.log.info("ONOS "+str(nodeNum)+
                            " ack-to-device: "+
                            str(ackToDevice) + " ms")
                else:
                    main.log.info("ONOS "+str(nodeNum)+
                            " ack-to-device "+
                            "measurement ignored due to excess in "+
                            "threshold or premature iteration")
                
                if deviceToGraph > thresholdMin and\
                   deviceToGraph < thresholdMax and i >= iterIgnore:
                    deviceToGraphDiscLatNodeIter[node][i] = deviceToGraph
                    main.log.info("ONOS "+str(nodeNum)+
                            " device-to-graph disconnect: "+
                            str(deviceToGraph) + " ms")
                else:
                    main.log.info("ONOS "+str(nodeNum)+
                            " device-to-graph disconnect "+
                            "measurement ignored due to excess in "+
                            "threshold or premature iteration")

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
                if item > 0.0:
                    tcpToFeatureList.append(item)

            for item in featureToRoleRequestLatNodeIter[node]:
                if item > 0.0:
                    featureToRoleList.append(item)

            for item in deviceToGraphLatNodeIter[node]:
                if item > 0.0:
                    deviceToGraphList.append(item)

            # Switch disconnect measurements
            for item in finAckTransactionLatNodeIter[node]:
                if item > 0.0:
                    finAckTransactionList.append(item)

            for item in ackToDeviceLatNodeIter[node]:
                if item > 0.0:
                    ackToDeviceList.append(item)

            for item in deviceToGraphDiscLatNodeIter[node]:
                if item > 0.0:
                    deviceToGraphDiscList.append(item)
            
            endToEndAvg = round(numpy.mean(endToEndList), 2)
            endToEndStdDev = round(numpy.std(endToEndList), 2)

            tcpToFeatureAvg = round(numpy.mean(tcpToFeatureList), 2)
            tcpToFeatureStdDev = round(numpy.std(tcpToFeatureList), 2)

            featureToRoleAvg = round(numpy.mean(featureToRoleList), 2)
            featureToRoleStdDev = round(numpy.std(featureToRoleList), 2)
            
            roleToOfpAvg = round(numpy.mean(roleToOfpList), 2)
            roleToOfpStdDev = round(numpy.std(roleToOfpList), 2)

            ofpToDeviceAvg = round(numpy.mean(ofpToDeviceList), 2)
            ofpToDeviceStdDev = round(numpy.std(ofpToDeviceList), 2)
            
            deviceToGraphAvg = round(numpy.mean(deviceToGraphList), 2)
            deviceToGraphStdDev = round(numpy.std(deviceToGraphList), 2)

            finAckAvg = round(numpy.mean(finAckTransactionList), 2)
            finAckStdDev = round(numpy.std(finAckTransactionList), 2)
            
            ackToDeviceAvg = round(numpy.mean(ackToDeviceList), 2)
            ackToDeviceStdDev = round(numpy.std(ackToDeviceList), 2)
            
            deviceToGraphDiscAvg = round(numpy.mean(deviceToGraphDiscList), 2)
            deviceToGraphDiscStdDev = round(numpy.std(deviceToGraphDiscList), 2)

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

            dbCmdList.append(
                    "INSERT INTO switch_latency_tests VALUES('" +
                    timeToPost + "','switch_latency_results'," +
                    runNum + ',' + str(clusterCount) + ",'baremetal" + 
                    str(node + 1) + "'," + str(endToEndAvg) + ',' +
                    str(endToEndStdDev) + ',0,0);')

        if debugMode == 'on':
            main.ONOS1.cpLogsToDir('/opt/onos/log/karaf.log',
                    '/tmp/', copyFileName='sw_lat_karaf')
        fResult = open(resultPath, 'a')
        for line in dbCmdList:
            if line:
                fResult.write(line + '\n')

        fResult.close()
        assertion = main.TRUE
        utilities.assert_equals(expect=main.TRUE, actual=assertion,
                onpass='Switch latency test successful', 
                onfail='Switch latency test failed')

    def CASE3(self, main):
        """
        Bring port up / down and measure latency.
        Port enable / disable is simulated by ifconfig up / down
        
        In ONOS-next, we must ensure that the port we are
        manipulating is connected to another switch with a valid
        connection. Otherwise, graph view will not be updated.
        """
        global timeToPost
        import time
        import subprocess
        import os
        import requests
        import json
        import numpy
        ONOS1Ip = main.params['CTRL']['ip1']
        ONOS2Ip = main.params['CTRL']['ip2']
        ONOS3Ip = main.params['CTRL']['ip3']
        ONOSUser = main.params['CTRL']['user']
        defaultSwPort = main.params['CTRL']['port1']
        assertion = main.TRUE
        numIter = main.params['TEST']['numIter']
        iterIgnore = int(main.params['TEST']['iterIgnore'])
        
        deviceTimestampKey = main.params['JSON']['deviceTimestamp']
        graphTimestampKey = main.params['JSON']['graphTimestamp']
        linkTimestampKey = main.params['JSON']['linkTimestamp']
        
        tsharkPortUp = '/tmp/tshark_port_up.txt'
        tsharkPortDown = '/tmp/tshark_port_down.txt'
        tsharkPortStatus = main.params[ 'TSHARK' ][ 'ofpPortStatus' ]
        
        debugMode = main.params['TEST']['debugMode']
        postToDB = main.params['DB']['postToDB']
        resultPath = main.params['DB']['portEventResultPath']
        timeToPost = time.strftime('%Y-%m-%d %H:%M:%S')
        localTime = time.strftime('%x %X')
        localTime = localTime.replace('/', '')
        localTime = localTime.replace(' ', '_')
        localTime = localTime.replace(':', '')
        
        if debugMode == 'on':
            main.ONOS1.tsharkPcap('eth0', '/tmp/port_lat_pcap_' + localTime)
        
        upThresholdStr = main.params['TEST']['portUpThreshold']
        downThresholdStr = main.params['TEST']['portDownThreshold']
        upThresholdObj = upThresholdStr.split(',')
        downThresholdObj = downThresholdStr.split(',')
        upThresholdMin = int(upThresholdObj[0])
        upThresholdMax = int(upThresholdObj[1])
        downThresholdMin = int(downThresholdObj[0])
        downThresholdMax = int(downThresholdObj[1])
        
        interfaceConfig = 's1-eth1'
        main.log.report('Port enable / disable latency')
        main.log.report('Simulated by ifconfig up / down')
        main.log.report('Total iterations of test: ' + str(numIter))
        main.step('Assign switches s1 and s2 to controller 1')
        
        main.Mininet1.assignSwController(sw='1',
                ip1=ONOS1Ip, port1=defaultSwPort)
        main.Mininet1.assignSwController(sw='2',
                ip1=ONOS1Ip, port1=defaultSwPort)
        
        time.sleep(15)
        
        portUpDeviceToOfpList = []
        portUpGraphToOfpList = []
        portDownDeviceToOfpList = []
        portDownGraphToOfpList = []
        
        portUpDevNodeIter = numpy.zeros((clusterCount, int(numIter)))
        portUpGraphNodeIter = numpy.zeros((clusterCount, int(numIter)))
        portUpLinkLatNodeIter = numpy.zeros((clusterCount, int(numIter)))
        portDownDevNodeIter = numpy.zeros((clusterCount, int(numIter)))
        portDownGraphNodeIter = numpy.zeros((clusterCount, int(numIter)))
        portDownLinkNodeIter = numpy.zeros((clusterCount, int(numIter)))
        portUpLinkNodeIter = numpy.zeros((clusterCount, int(numIter)))
        
        for i in range(0, int(numIter)):
            main.step('Starting wireshark capture for port status down')
            main.ONOS1.tsharkGrep(tsharkPortStatus, tsharkPortDown)
            
            time.sleep(5)
            
            main.step('Disable port: ' + interfaceConfig)
            main.Mininet1.handle.sendline('sh ifconfig ' +
                    interfaceConfig + ' down')
            main.Mininet1.handle.expect('mininet>')
            
            time.sleep(3)
            
            main.ONOS1.tsharkStop()
            
            os.system('scp ' + ONOSUser + '@' + ONOS1Ip + ':' +
                    tsharkPortDown + ' /tmp/')
            
            fPortDown = open(tsharkPortDown, 'r')
            fLine = fPortDown.readline()
            objDown = fLine.split(' ')
            if len(fLine) > 0:
                timestampBeginPtDown = int(float(objDown[1]) * 1000)
                # At times, tshark reports timestamp at the 3rd 
                # index of the array. If initial readings were 
                # unlike the epoch timestamp, then check the 3rd
                # index and set that as a timestamp
                if timestampBeginPtDown < 1400000000000:
                    timestampBeginPtDown = int(float(objDown[2]) * 1000)
                # If there are any suspicion of invalid results
                # check this reported value
                main.log.info('Port down begin timestamp: ' +
                        str(timestampBeginPtDown))
            else:
                main.log.info('Tshark output file returned unexpected' +
                        ' results: ' + str(objDown))
                timestampBeginPtDown = 0
            fPortDown.close()
          
            for node in range(0, clusterCount):
                nodeNum = node+1
                metricsDown = CLIs[node].topologyEventsMetrics
                jsonStrDown = metricsDown()
                jsonObj = json.loads(jsonStrDown)
                
                if jsonObj:
                    graphTimestamp = jsonObj[graphTimestampKey]['value']
                    deviceTimestamp = jsonObj[deviceTimestampKey]['value']
                    linkTimestamp = jsonObj[linkTimestampKey]['value']
                else:
                    main.log.error( "Unexpected json object" )
                    graphTimestamp = 0
                    deviceTimestamp = 0
                    linkTimestamp = 0

                ptDownGraphToOfp = int(graphTimestamp) - int(timestampBeginPtDown)
                ptDownDeviceToOfp = int(deviceTimestamp) - int(timestampBeginPtDown)
                ptDownLinkToOfp = int(linkTimestamp) - int(timestampBeginPtDown)

                if ptDownGraphToOfp > downThresholdMin and\
                   ptDownGraphToOfp < downThresholdMax and i >= iterIgnore:
                    portDownGraphNodeIter[node][i] = ptDownGraphToOfp
                    main.log.info("ONOS "+str(nodeNum)+ 
                            " port down graph-to-ofp: "+
                            str(ptDownGraphToOfp) + " ms") 
                else:
                    main.log.info("ONOS "+str(nodeNum)+
                            " port down graph-to-ofp ignored"+
                            " due to excess in threshold or premature iteration")

                if ptDownDeviceToOfp > downThresholdMin and\
                   ptDownDeviceToOfp < downThresholdMax and i >= iterIgnore:
                    portDownDevNodeIter[node][i] = ptDownDeviceToOfp
                    main.log.info("ONOS "+str(nodeNum)+ 
                            " port down device-to-ofp: "+
                            str(ptDownDeviceToOfp) + " ms") 
                else:
                    main.log.info("ONOS "+str(nodeNum)+
                            " port down device-to-ofp ignored"+
                            " due to excess in threshold or premature iteration")

                if ptDownLinkToOfp > downThresholdMin and\
                   ptDownLinkToOfp < downThresholdMax and i >= iterIgnore:
                    portDownLinkNodeIter[node][i] = ptDownLinkToOfp
                    main.log.info("ONOS "+str(nodeNum)+
                            " port down link-to-ofp: "+
                            str(ptDownLinkToOfp) + " ms")
                else:
                    main.log.info("ONOS "+str(nodeNum)+
                            " port down link-to-ofp ignored"+
                            " due to excess in threshold or premature iteration")

            time.sleep(3)
            
            main.step('Starting wireshark capture for port status up')
            main.ONOS1.tsharkGrep(tsharkPortStatus, tsharkPortUp)
            
            time.sleep(5)
            main.step('Enable port and obtain timestamp')
            main.Mininet1.handle.sendline('sh ifconfig ' + interfaceConfig + ' up')
            main.Mininet1.handle.expect('mininet>')
            
            time.sleep(5)
            main.ONOS1.tsharkStop()
            
            time.sleep(3)
            os.system('scp ' + ONOSUser + '@' +
                    ONOS1Ip + ':' + tsharkPortUp + ' /tmp/')
            
            fPortUp = open(tsharkPortUp, 'r')
            fLine = fPortUp.readline()
            objUp = fLine.split(' ')
            if len(fLine) > 0:
                timestampBeginPtUp = int(float(objUp[1]) * 1000)
                if timestampBeginPtUp < 1400000000000:
                    timestampBeginPtUp = int(float(objUp[2]) * 1000)
                main.log.info('Port up begin timestamp: ' + str(timestampBeginPtUp))
            else:
                main.log.info('Tshark output file returned unexpected' + ' results.')
                timestampBeginPtUp = 0
            fPortUp.close()
            
            for node in range(0, clusterCount):
                nodeNum = node+1
                metricsUp = CLIs[node].topologyEventsMetrics
                jsonStrUp = metricsUp()
                jsonObj = json.loads(jsonStrUp)
               
                if jsonObj:
                    graphTimestamp = jsonObj[graphTimestampKey]['value']
                    deviceTimestamp = jsonObj[deviceTimestampKey]['value']
                    linkTimestamp = jsonObj[linkTimestampKey]['value']
                else:
                    main.log.error( "Unexpected json object" )
                    graphTimestamp = 0
                    deviceTimestamp = 0
                    linkTimestamp = 0

                ptUpGraphToOfp = int(graphTimestamp) - int(timestampBeginPtUp)
                ptUpDeviceToOfp = int(deviceTimestamp) - int(timestampBeginPtUp)
                ptUpLinkToOfp = int(linkTimestamp) - int(timestampBeginPtUp)

                if ptUpGraphToOfp > upThresholdMin and\
                   ptUpGraphToOfp < upThresholdMax and i > iterIgnore:
                    portUpGraphNodeIter[node][i] = ptUpGraphToOfp
                    main.log.info("ONOS "+str(nodeNum)+ 
                            " port up graph-to-ofp: "+
                            str(ptUpGraphToOfp) + " ms") 
                else:
                    main.log.info("ONOS "+str(nodeNum)+
                            " port up graph-to-ofp ignored"+
                            " due to excess in threshold or premature iteration")

                if ptUpDeviceToOfp > upThresholdMin and\
                   ptUpDeviceToOfp < upThresholdMax and i > iterIgnore:
                    portUpDevNodeIter[node][i] = ptUpDeviceToOfp
                    main.log.info("ONOS "+str(nodeNum)+ 
                            " port up device-to-ofp: "+
                            str(ptUpDeviceToOfp) + " ms") 
                else:
                    main.log.info("ONOS "+str(nodeNum)+
                            " port up device-to-ofp ignored"+
                            " due to excess in threshold or premature iteration")

                if ptUpLinkToOfp > upThresholdMin and\
                   ptUpLinkToOfp < upThresholdMax and i > iterIgnore:
                    portUpLinkNodeIter[node][i] = ptUpLinkToOfp
                    main.log.info("ONOS "+str(nodeNum)+
                            " port up link-to-ofp: "+
                            str(ptUpLinkToOfp) + " ms")
                else:
                    main.log.info("ONOS "+str(nodeNum)+
                            " port up link-to-ofp ignored"+
                            " due to excess in threshold or premature iteration")

        dbCmdList = []
        for node in range(0, clusterCount):
            portUpDevList = []
            portUpGraphList = []
            portUpLinkList = []
            portDownDevList = []
            portDownGraphList = []
            portDownLinkList = []

            portUpDevAvg = 0
            portUpGraphAvg = 0
            portUpLinkAvg = 0
            portDownDevAvg = 0
            portDownGraphAvg = 0
            portDownLinkAvg = 0

            for item in portUpDevNodeIter[node]:
                if item > 0.0:
                    portUpDevList.append(item)

            for item in portUpGraphNodeIter[node]:
                if item > 0.0:
                    portUpGraphList.append(item)

            for item in portUpLinkNodeIter[node]:
                if item > 0.0:
                    portUpLinkList.append(item)

            for item in portDownDevNodeIter[node]:
                if item > 0.0:
                    portDownDevList.append(item)

            for item in portDownGraphNodeIter[node]:
                if item > 0.0:
                    portDownGraphList.append(item)

            for item in portDownLinkNodeIter[node]:
                if item > 0.0:
                    portDownLinkList.append(item)

            portUpDevAvg = round(numpy.mean(portUpDevList), 2)
            portUpGraphAvg = round(numpy.mean(portUpGraphList), 2)
            portUpLinkAvg = round(numpy.mean(portUpLinkList), 2)

            portDownDevAvg = round(numpy.mean(portDownDevList), 2)
            portDownGraphAvg = round(numpy.mean(portDownGraphList), 2)
            portDownLinkAvg = round(numpy.mean(portDownLinkList), 2)
            
            portUpStdDev = round(numpy.std(portUpGraphList), 2)
            portDownStdDev = round(numpy.std(portDownGraphList), 2)
           
            main.log.report(' - Node ' + str(node + 1) + ' Summary - ')
            main.log.report(' Port up ofp-to-device ' +
                    str(portUpDevAvg) + ' ms')
            main.log.report(' Port up ofp-to-graph ' +
                    str(portUpGraphAvg) + ' ms')
            main.log.report(' Port up ofp-to-link ' +
                    str(portUpLinkAvg) + ' ms')
            
            main.log.report(' Port down ofp-to-device ' +
                    str(round(portDownDevAvg, 2)) + ' ms')
            main.log.report(' Port down ofp-to-graph ' +
                    str(portDownGraphAvg) + ' ms')
            main.log.report(' Port down ofp-to-link ' +
                    str(portDownLinkAvg) + ' ms')

            dbCmdList.append("INSERT INTO port_latency_tests VALUES('" + 
                    timeToPost + "','port_latency_results'," + runNum +
                    ',' + str(clusterCount) + ",'baremetal" + str(node + 1) +
                    "'," + str(portUpGraphAvg) + ',' + str(portUpStdDev) +
                    '' + str(portDownGraphAvg) + ',' + str(portDownStdDev) + ');')

        fResult = open(resultPath, 'a')
        for line in dbCmdList:
            if line:
                fResult.write(line + '\n')

        fResult.close()

        # Delete switches from controller to prepare for next
        # set of tests
        main.Mininet1.deleteSwController('s1')
        main.Mininet1.deleteSwController('s2')
        utilities.assert_equals(expect=main.TRUE,
                actual=assertion,
                onpass='Port discovery latency calculation successful',
                onfail='Port discovery test failed')

    def CASE4(self, main):
        """
        Increase number of nodes and initiate CLI
        
        With the most recent implementation, we need a method to
        ensure all ONOS nodes are killed, as well as redefine
        the cell files to ensure all nodes that will be used
        is in the cell file. Otherwise, exceptions will
        prohibit test from running successfully.
        
        3/12/15

        """
        global clusterCount
        import time
        import os

        clusterCount += 2

        benchIp = main.params[ 'BENCH' ][ 'ip' ]
        features = main.params[ 'ENV' ][ 'cellFeatures' ]
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        mininetIp = main.params[ 'MN' ][ 'ip1' ]
        
        main.log.report('Increasing cluster size to ' + str(clusterCount))
     
        main.log.step( "Killing all ONOS processes before scale-out" )
        
        for i in range( 1, 8 ):
            main.ONOSbench.onosDie(
                    main.params[ 'CTRL' ][ 'ip'+str(i) ] )
            main.ONOSbench.onosUninstall(
                    main.params[ 'CTRL' ][ 'ip'+str(i) ] )

        main.step( "Creating scale-out cell file" )
        cellIp = []
        for node in range( 1, clusterCount + 1 ):
            cellIp.append( main.params[ 'CTRL' ][ 'ip'+str(node) ] )

        main.log.info( "Cell Ip list: " + str(cellIp) )
        main.ONOSbench.createCellFile( benchIp, cellName, mininetIp,
                                       str(features), *cellIp )
        
        main.step( "Setting cell definition" )
        main.ONOSbench.setCell(cellName)

        main.step( "Packaging cell definition" )
        main.ONOSbench.onosPackage()

        for node in range( 1, clusterCount + 1 ):
            main.ONOSbench.onosInstall(
                    node = main.params[ 'CTRL' ][ 'ip'+str(node) ])
        
        time.sleep( 20 )
        
        for node in range( 1, clusterCount + 1):
            for i in range( 2 ):
                isup = main.ONOSbench.isup( 
                        main.params[ 'CTRL' ][ 'ip'+str(node) ] )
                if isup:
                    main.log.info( "ONOS "+str(node) + " is up\n")
                    break
            if not isup:
                main.log.error( "ONOS "+str(node) + " did not start" )

        for node in range( 0, clusterCount ):
            CLIs[node].startOnosCli( cellIp[node] )
       
        main.step( 'Setting configurations for metrics' )
        configParam = 'maxEvents 1'
        main.ONOSbench.onosCfgSet( nodeIpList[0], configName, configParam )
        configParam = 'maxBatchMs 0'
        main.ONOSbench.onosCfgSet( nodeIpList[0], configName, configParam )
        configParam = 'maxIdleMs 0'
        main.ONOSbench.onosCfgSet( nodeIpList[0], configName, configParam )
       
        main.step( 'Activating essential applications' )
        CLIs[0].activateApp( 'org.onosproject.metrics' )
        CLIs[0].activateApp( 'org.onosproject.openflow' )

