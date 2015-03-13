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
        
        ONOS1Ip = main.params['CTRL']['ip1']
        ONOS2Ip = main.params['CTRL']['ip2']
        ONOS3Ip = main.params['CTRL']['ip3']
        ONOS4Ip = main.params['CTRL']['ip4']
        ONOS5Ip = main.params['CTRL']['ip5']
        ONOS6Ip = main.params['CTRL']['ip6']
        ONOS7Ip = main.params['CTRL']['ip7']
        MN1Ip = main.params['MN']['ip1']
        BENCHIp = main.params['BENCH']['ip']
        
        topoCfgFile = main.params['TEST']['topoConfigFile']
        topoCfgName = main.params['TEST']['topoConfigName']
        portEventResultPath = main.params['DB']['portEventResultPath']
        switchEventResultPath = main.params['DB']['switchEventResultPath']
        mvnCleanInstall = main.params['TEST']['mci']
        
        main.case('Setting up test environment')
        main.log.info('Copying topology event accumulator config' +
                ' to ONOS /package/etc')
        main.ONOSbench.handle.sendline('cp ~/' +
                topoCfgFile + ' ~/ONOS/tools/package/etc/' +
                topoCfgName)
        main.ONOSbench.handle.expect('\\$')
        
        main.log.report('Setting up test environment')
        
        main.step('Starting mininet topology ')
        main.Mininet1.startNet()
        
        main.step('Cleaning previously installed ONOS if any')
        main.ONOSbench.onosUninstall(nodeIp=ONOS2Ip)
        main.ONOSbench.onosUninstall(nodeIp=ONOS3Ip)
        main.ONOSbench.onosUninstall(nodeIp=ONOS4Ip)
        main.ONOSbench.onosUninstall(nodeIp=ONOS5Ip)
        main.ONOSbench.onosUninstall(nodeIp=ONOS6Ip)
        main.ONOSbench.onosUninstall(nodeIp=ONOS7Ip)
        
        main.step('Clearing previous DB log file')
        
        fPortLog = open(portEventResultPath, 'w')
        fPortLog.write('')
        fPortLog.close()
        fSwitchLog = open(switchEventResultPath, 'w')
        fSwitchLog.write('')
        fSwitchLog.close()
        
        cellStr = 'webconsole,onos-core,onos-api,onos-app-metrics,' +\
                'onos-app-gui,onos-cli,onos-openflow'
        
        main.step('Creating cell file')
        cellFileResult = main.ONOSbench.createCellFile(
                BENCHIp, cellName, MN1Ip, cellStr, ONOS1Ip)
        
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
        main.ONOS1cli.setCell(cellName)
        
        main.step('Creating ONOS package')
        packageResult = main.ONOSbench.onosPackage()
        
        main.step('Installing ONOS package')
        install1Result = main.ONOSbench.onosInstall(node=ONOS1Ip)
        
        time.sleep(10)
        
        main.step('Start onos cli')
        cli1 = main.ONOS1cli.startOnosCli(ONOS1Ip)
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
        
        ONOS1Ip = main.params['CTRL']['ip1']
        ONOS2Ip = main.params['CTRL']['ip2']
        ONOS3Ip = main.params['CTRL']['ip3']
        ONOS4Ip = main.params['CTRL']['ip4']
        ONOS5Ip = main.params['CTRL']['ip5']
        ONOS6Ip = main.params['CTRL']['ip6']
        ONOS7Ip = main.params['CTRL']['ip7']
        
        ONOSUser = main.params['CTRL']['user']
        defaultSwPort = main.params['CTRL']['port1']
        numIter = main.params['TEST']['numIter']
        iterIgnore = int(main.params['TEST']['iterIgnore'])
        deviceTimestamp = main.params['JSON']['deviceTimestamp']
        graphTimestamp = main.params['JSON']['graphTimestamp']
        debugMode = main.params['TEST']['debugMode']
        onosLog = main.params['TEST']['onosLogFile']
        resultPath = main.params['DB']['switchEventResultPath']
        thresholdStr = main.params['TEST']['singleSwThreshold']
        thresholdObj = thresholdStr.split(',')
        thresholdMin = int(thresholdObj[0])
        thresholdMax = int(thresholdObj[1])
       
        #TODO: Look for 'role-request' messages,
        #      which replaces the 'vendor' messages previously seen
        #      on OVS 2.0.1
        tsharkOfString = main.params[ 'TSHARK' ][ 'ofpRoleReply' ]
        tsharkTcpString = main.params[ 'TSHARK' ][ 'tcpSynAck' ]
        tsharkOfOutput = '/tmp/tshark_of_topo.txt'
        tsharkTcpOutput = '/tmp/tshark_tcp_topo.txt'

        latencyEndToEndList = []
        latencyOfpToGraphList = []
        latencyOfpToDeviceList = []
        latencyT0ToDeviceList = []
        latencyTcpToOfpList = []
        
        endToEndLatNodeIter = numpy.zeros((clusterCount, int(numIter)))
        ofpToGraphLatNodeIter = numpy.zeros((clusterCount, int(numIter)))
        ofpToDeviceLatNodeIter = numpy.zeros((clusterCount, int(numIter)))
        
        tcpToOfpLatIter = []
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
            
            time.sleep(10)
           
            main.log.info('Assigning s3 to controller')
            main.Mininet1.assignSwController(sw='3',
                    ip1=ONOS1Ip, port1=defaultSwPort)
            
            time.sleep(10)
            
            main.log.info('Stopping all Tshark processes')
            main.ONOS1.tsharkStop()
            
            main.log.info('Copying over tshark files')
            os.system('scp ' + ONOSUser + '@' + ONOS1Ip +
                    ':' + tsharkTcpOutput + ' /tmp/')
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
            
            os.system('scp ' + ONOSUser + '@' +
                      ONOS1Ip + ':' + tsharkOfOutput + ' /tmp/')
            
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
            
            jsonStr1 = main.ONOS1cli.topologyEventsMetrics()
            jsonStr2 = ''
            jsonStr3 = ''
            jsonStr4 = ''
            jsonStr5 = ''
            jsonStr6 = ''
            jsonStr7 = ''
            
            jsonObj1 = json.loads(jsonStr1)
            jsonObj2 = ''
            jsonObj3 = ''
            jsonObj4 = ''
            jsonObj5 = ''
            jsonObj6 = ''
            jsonObj7 = ''
            
            graphTimestamp1 = jsonObj1[graphTimestamp]['value']
            deviceTimestamp1 = jsonObj1[deviceTimestamp]['value']
            
            main.log.info(' GraphTimestamp: ' + str(graphTimestamp1))
            main.log.info(' DeviceTimestamp: ' + str(deviceTimestamp1))
            
            deltaDevice1 = int(deviceTimestamp1) - int(t0Tcp)
            deltaGraph1 = int(graphTimestamp1) - int(t0Tcp)
            deltaOfpGraph1 = int(graphTimestamp1) - int(t0Ofp)
            deltaOfpDevice1 = int(deviceTimestamp1) - int(t0Ofp)
            deltaTcpOfp1 = int(t0Ofp) - int(t0Tcp)
            
            if deltaTcpOfp1 > thresholdMin and\
               deltaTcpOfp1 < thresholdMax and i >= iterIgnore:
                tcpToOfpLatIter.append(deltaTcpOfp1)
                main.log.info('ONOS1 iter' + str(i) +
                              ' tcp-to-ofp: ' +
                              str(deltaTcpOfp1) + ' ms')
            else:
                tcpToOfpLatIter.append(0)
                main.log.info('ONOS1 iter' + str(i) +
                        ' tcp-to-ofp: ' + str(deltaTcpOfp1) +
                        ' ms - ignored this iteration')
            if deltaGraph1 > thresholdMin and\
               deltaGraph1 < thresholdMax and i >= iterIgnore:
                endToEndLatNodeIter[0][i] = deltaGraph1
                main.log.info('ONOS1 iter' + str(i) +
                              ' end-to-end: ' +
                              str(deltaGraph1) + ' ms')
            else:
                main.log.info('ONOS1 iter' + str(i) +
                        ' end-to-end: ' + str(deltaGraph1) +
                        ' ms - ignored this iteration')
            if deltaOfpGraph1 > thresholdMin and \
               deltaOfpGraph1 < thresholdMax and i >= iterIgnore:
                ofpToGraphLatNodeIter[0][i] = deltaOfpGraph1
                main.log.info('ONOS1 iter' + str(i) +
                        ' ofp-to-graph: ' +
                        str(deltaOfpGraph1) + ' ms')
            if deltaOfpDevice1 > thresholdMin and\
               deltaOfpDevice1 < thresholdMax and i >= iterIgnore:
                ofpToDeviceLatNodeIter[0][i] = deltaOfpDevice1
                main.log.info('ONOS1 iter' + str(i) +
                        ' ofp-to-device: ' +
                        str(deltaOfpDevice1))
            
            if clusterCount >= 3:
                jsonStr2 = main.ONOS2cli.topologyEventsMetrics()
                jsonStr3 = main.ONOS3cli.topologyEventsMetrics()
                jsonObj2 = json.loads(jsonStr2)
                jsonObj3 = json.loads(jsonStr3)
                graphTimestamp2 = jsonObj2[graphTimestamp]['value']
                graphTimestamp3 = jsonObj3[graphTimestamp]['value']
                deviceTimestamp2 = jsonObj2[deviceTimestamp]['value']
                deviceTimestamp3 = jsonObj3[deviceTimestamp]['value']
                deltaDevice2 = int(deviceTimestamp2) - int(t0Tcp)
                deltaDevice3 = int(deviceTimestamp3) - int(t0Tcp)
                deltaGraph2 = int(graphTimestamp2) - int(t0Tcp)
                deltaGraph3 = int(graphTimestamp3) - int(t0Tcp)
                deltaOfpGraph2 = int(graphTimestamp2) - int(t0Ofp)
                deltaOfpGraph3 = int(graphTimestamp3) - int(t0Ofp)
                deltaOfpDevice2 = int(deviceTimestamp2) - int(t0Ofp)
                deltaOfpDevice3 = int(deviceTimestamp3) - int(t0Ofp)
                if deltaGraph2 > thresholdMin and\
                   deltaGraph2 < thresholdMax and i >= iterIgnore:
                    endToEndLatNodeIter[1][i] = deltaGraph2
                    main.log.info('ONOS2 iter' + str(i) +
                            ' end-to-end: ' +
                            str(deltaGraph2) + ' ms')
                if deltaOfpGraph2 > thresholdMin and\
                   deltaOfpGraph2 < thresholdMax and i >= iterIgnore:
                    ofpToGraphLatNodeIter[1][i] = deltaOfpGraph2
                    main.log.info('ONOS2 iter' + str(i) +
                            ' ofp-to-graph: ' +
                            str(deltaOfpGraph2) + ' ms')
                if deltaOfpDevice2 > thresholdMin and\
                   deltaOfpDevice2 < thresholdMax and i >= iterIgnore:
                    ofpToDeviceLatNodeIter[1][i] = deltaOfpDevice2
                    main.log.info('ONOS2 iter' + str(i) +
                            ' ofp-to-device: ' +
                            str(deltaOfpDevice2))
                if deltaGraph3 > thresholdMin and\
                   deltaGraph3 < thresholdMax and i >= iterIgnore:
                    endToEndLatNodeIter[2][i] = deltaGraph3
                    main.log.info('ONOS3 iter' + str(i) +
                            ' end-to-end: ' + str(deltaGraph3) + ' ms')
                if deltaOfpGraph3 > thresholdMin and\
                   deltaOfpGraph3 < thresholdMax and i >= iterIgnore:
                    ofpToGraphLatNodeIter[2][i] = deltaOfpGraph3
                    main.log.info('ONOS3 iter' + str(i) +
                            ' ofp-to-graph: ' +
                            str(deltaOfpGraph3) + ' ms')
                if deltaOfpDevice3 > thresholdMin and\
                        deltaOfpDevice3 < thresholdMax and i >= iterIgnore:
                    ofpToDeviceLatNodeIter[2][i] = deltaOfpDevice3
                    main.log.info('ONOS3 iter' + str(i) +
                            ' ofp-to-device: ' + str(deltaOfpDevice3))
            if clusterCount >= 5:
                jsonStr4 = main.ONOS4cli.topologyEventsMetrics()
                jsonStr5 = main.ONOS5cli.topologyEventsMetrics()
                jsonObj4 = json.loads(jsonStr4)
                jsonObj5 = json.loads(jsonStr5)
                graphTimestamp4 = jsonObj4[graphTimestamp]['value']
                graphTimestamp5 = jsonObj5[graphTimestamp]['value']
                deviceTimestamp4 = jsonObj4[deviceTimestamp]['value']
                deviceTimestamp5 = jsonObj5[deviceTimestamp]['value']
                deltaDevice4 = int(deviceTimestamp4) - int(t0Tcp)
                deltaDevice5 = int(deviceTimestamp5) - int(t0Tcp)
                deltaGraph4 = int(graphTimestamp4) - int(t0Tcp)
                deltaGraph5 = int(graphTimestamp5) - int(t0Tcp)
                deltaOfpGraph4 = int(graphTimestamp4) - int(t0Ofp)
                deltaOfpGraph5 = int(graphTimestamp5) - int(t0Ofp)
                deltaOfpDevice4 = int(deviceTimestamp4) - int(t0Ofp)
                deltaOfpDevice5 = int(deviceTimestamp5) - int(t0Ofp)
                if deltaGraph4 > thresholdMin and \
                   deltaGraph4 < thresholdMax and i >= iterIgnore:
                    endToEndLatNodeIter[3][i] = deltaGraph4
                    main.log.info('ONOS4 iter' + str(i) +
                            ' end-to-end: ' + str(deltaGraph4) + ' ms')
                if deltaOfpDevice4 > thresholdMin and \
                   deltaOfpDevice4 < thresholdMax and i >= iterIgnore:
                    ofpToDeviceLatNodeIter[3][i] = deltaOfpDevice4
                    main.log.info('ONOS4 iter' + str(i) +
                            ' ofp-to-device: ' + str(deltaOfpDevice4))
                if deltaOfpGraph4 > thresholdMin and \
                        deltaOfpGraph4 < thresholdMax and i >= iterIgnore:
                    ofpToGraphLatNodeIter[3][i] = deltaOfpGraph4
                    main.log.info('ONOS4 iter' + str(i) +
                            ' ofp-to-graph: ' + str(deltaOfpGraph4) + ' ms')
                if deltaGraph5 > thresholdMin and\
                        deltaGraph5 < thresholdMax and i >= iterIgnore:
                    endToEndLatNodeIter[4][i] = deltaGraph5
                    main.log.info('ONOS5 iter' + str(i) +
                            ' end-to-end: ' + str(deltaGraph5) + ' ms')
                if deltaOfpDevice5 > thresholdMin and\
                        deltaOfpDevice5 < thresholdMax and i >= iterIgnore:
                    ofpToDeviceLatNodeIter[4][i] = deltaOfpDevice5
                    main.log.info('ONOS5 iter' + str(i) +
                            ' ofp-to-device: ' + str(deltaOfpDevice5))
                if deltaOfpGraph5 > thresholdMin and\
                        deltaOfpGraph5 < thresholdMax and i >= iterIgnore:
                    ofpToGraphLatNodeIter[4][i] = deltaOfpGraph5
                    main.log.info('ONOS5 iter' + str(i) +
                            ' ofp-to-graph: ' +
                            str(deltaOfpGraph5) + ' ms')
            if clusterCount >= 7:
                jsonStr6 = main.ONOS6cli.topologyEventsMetrics()
                jsonStr7 = main.ONOS7cli.topologyEventsMetrics()
                jsonObj6 = json.loads(jsonStr6)
                jsonObj7 = json.loads(jsonStr7)
                graphTimestamp6 = jsonObj6[graphTimestamp]['value']
                graphTimestamp7 = jsonObj7[graphTimestamp]['value']
                deviceTimestamp6 = jsonObj6[deviceTimestamp]['value']
                deviceTimestamp7 = jsonObj7[deviceTimestamp]['value']
                deltaDevice6 = int(deviceTimestamp6) - int(t0Tcp)
                deltaDevice7 = int(deviceTimestamp7) - int(t0Tcp)
                deltaGraph6 = int(graphTimestamp6) - int(t0Tcp)
                deltaGraph7 = int(graphTimestamp7) - int(t0Tcp)
                deltaOfpGraph6 = int(graphTimestamp6) - int(t0Ofp)
                deltaOfpGraph7 = int(graphTimestamp7) - int(t0Ofp)
                deltaOfpDevice6 = int(deviceTimestamp6) - int(t0Ofp)
                deltaOfpDevice7 = int(deviceTimestamp7) - int(t0Ofp)
                if deltaGraph6 > thresholdMin and \
                   deltaGraph6 < thresholdMax and i >= iterIgnore:
                    endToEndLatNodeIter[5][i] = deltaGraph6
                    main.log.info('ONOS6 iter' + str(i) +
                            ' end-to-end: ' + str(deltaGraph6) + ' ms')
                if deltaOfpDevice6 > thresholdMin and\
                   deltaOfpDevice6 < thresholdMax and i >= iterIgnore:
                    ofpToDeviceLatNodeIter[5][i] = deltaOfpDevice6
                    main.log.info('ONOS6 iter' + str(i) +
                            ' ofp-to-device: ' + str(deltaOfpDevice6))
                if deltaOfpGraph6 > thresholdMin and\
                   deltaOfpGraph6 < thresholdMax and i >= iterIgnore:
                    ofpToGraphLatNodeIter[5][i] = deltaOfpGraph6
                    main.log.info('ONOS6 iter' + str(i) +
                            ' ofp-to-graph: ' +
                            str(deltaOfpGraph6) + ' ms')
                if deltaGraph7 > thresholdMin and \
                   deltaGraph7 < thresholdMax and i >= iterIgnore:
                    endToEndLatNodeIter[6][i] = deltaGraph7
                    main.log.info('ONOS7 iter' + str(i) +
                            ' end-to-end: ' + 
                            str(deltaGraph7) + ' ms')
                if deltaOfpDevice7 > thresholdMin and\
                        deltaOfpDevice7 < thresholdMax and i >= iterIgnore:
                    ofpToDeviceLatNodeIter[6][i] = deltaOfpDevice7
                    main.log.info('ONOS7 iter' + str(i) +
                            ' ofp-to-device: ' +
                            str(deltaOfpDevice7))
                if deltaOfpGraph7 > thresholdMin and \
                        deltaOfpGraph7 < thresholdMax and i >= iterIgnore:
                    ofpToGraphLatNodeIter[6][i] = deltaOfpGraph7
                    main.log.info('ONOS7 iter' + str(i) +
                            ' ofp-to-graph: ' +
                            str(deltaOfpGraph7) + ' ms')
            
            time.sleep(5)
        
            # Get device id to remove
            deviceIdJsonStr = main.ONOS1cli.devices()
            
            main.log.info( "Device obj obtained: " + str(deviceIdJsonStr) )
            deviceId = json.loads(deviceIdJsonStr)

            deviceList = []
            for device in deviceId:
                deviceList.append(device['id'])
            
            main.step('Remove switch from controller')
            main.Mininet1.deleteSwController('s3')
            
            #firstDevice = deviceList[0] 
            firstDevice = "of:0000000000000003"
            main.log.info( "Removing device " +str(firstDevice)+
                    " from ONOS" )
            #if deviceId:
            main.ONOS1cli.deviceRemove(firstDevice)
            
            time.sleep(5)

        endToEndAvg = 0
        ofpToGraphAvg = 0
        endToEndList = []
        ofpToGraphList = []
        ofpToDeviceList = []
        dbCmdList = []
        for node in range(0, clusterCount):
            for item in endToEndLatNodeIter[node]:
                if item > 0.0:
                    endToEndList.append(item)

            for item in ofpToGraphLatNodeIter[node]:
                if item > 0.0:
                    ofpToGraphList.append(item)

            for item in ofpToDeviceLatNodeIter[node]:
                if item > 0.0:
                    ofpToDeviceList.append(item)

            endToEndAvg = round(numpy.mean(endToEndList), 2)
            ofpToGraphAvg = round(numpy.mean(ofpToGraphList), 2)
            endToEndStd = round(numpy.std(endToEndList), 2)
            ofpToGraphStd = round(numpy.std(ofpToGraphList), 2)
            ofpToDeviceAvg = round(numpy.mean(ofpToDeviceList), 2)
            ofpToDeviceStd = round(numpy.std(ofpToDeviceList), 2)
            main.log.report(' - Node ' + str(node + 1) + ' Summary - ')
            main.log.report(' End-to-end Avg: ' + str(endToEndAvg) +
                    ' ms' + ' End-to-end Std dev: ' +
                    str(endToEndStd) + ' ms')
            main.log.report(' Ofp-to-graph Avg: ' + str(ofpToGraphAvg) +
                    ' ms' + ' Ofp-to-graph Std dev: ' +
                    str(ofpToGraphStd) + ' ms')
            main.log.report(' Ofp-to-device Avg: ' + str(ofpToDeviceAvg) +
                    ' ms' + ' Ofp-to-device Std dev: ' +
                    str(ofpToDeviceStd) + ' ms')
            dbCmdList.append(
                    "INSERT INTO switch_latency_tests VALUES('" +
                    timeToPost + "','switch_latency_results'," +
                    runNum + ',' + str(clusterCount) + ",'baremetal" + 
                    str(node + 1) + "'," + str(endToEndAvg) + ',' +
                    str(endToEndStd) + ',0,0);')

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
        deviceTimestamp = main.params['JSON']['deviceTimestamp']
        graphTimestamp = main.params['JSON']['graphTimestamp']
        linkTimestamp = main.params['JSON']['linkTimestamp']
        
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
                if timestampBeginPtDown < 1400000000000:
                    timestampBeginPtDown = int(float(objDown[2]) * 1000)
                main.log.info('Port down begin timestamp: ' +
                        str(timestampBeginPtDown))
            else:
                main.log.info('Tshark output file returned unexpected' +
                        ' results: ' + str(objDown))
                timestampBeginPtDown = 0
            fPortDown.close()
            
            main.step('Obtain t1 by metrics call')
            
            jsonStrUp1 = main.ONOS1cli.topologyEventsMetrics()
            jsonObj1 = json.loads(jsonStrUp1)
            graphTimestamp1 = jsonObj1[graphTimestamp]['value']
            deviceTimestamp1 = jsonObj1[deviceTimestamp]['value']
            linkTimestamp1 = jsonObj1[linkTimestamp]['value']
            ptDownGraphToOfp1 = int(graphTimestamp1) - int(timestampBeginPtDown)
            ptDownDeviceToOfp1 = int(deviceTimestamp1) - int(timestampBeginPtDown)
            ptDownLinkToOfp1 = int(linkTimestamp1) - int(timestampBeginPtDown)
            
            if ptDownGraphToOfp1 > downThresholdMin and\
               ptDownGraphToOfp1 < downThresholdMax and i > iterIgnore:
                portDownGraphNodeIter[0][i] = ptDownGraphToOfp1
                main.log.info('ONOS1 iter' + str(i) +
                        ' port down graph-to-ofp: ' +
                        str(ptDownGraphToOfp1) + ' ms')
            else:
                main.log.info('ONOS1 iter' + str(i) + 
                        ' skipped. Result: ' +
                        str(ptDownGraphToOfp1) + ' ms')
            if ptDownDeviceToOfp1 > downThresholdMin and \
               ptDownDeviceToOfp1 < downThresholdMax and i > iterIgnore:
                portDownDevNodeIter[0][i] = ptDownDeviceToOfp1
                main.log.info('ONOS1 iter' + str(i) + 
                        ' port down device-to-ofp: ' +
                        str(ptDownDeviceToOfp1) + ' ms')
            else:
                main.log.info('ONOS1 iter' + str(i) +
                        ' skipped. Result: ' +
                        str(ptDownDeviceToOfp1) + ' ms')
            if ptDownLinkToOfp1 > downThresholdMin and\
               ptDownLinkToOfp1 < downThresholdMax and i > iterIgnore:
                portDownLinkNodeIter[0][i] = ptDownLinkToOfp1
                main.log.info('ONOS1 iter' + str(i) +
                        ' port down link-to-ofp: ' +
                        str(ptDownLinkToOfp1) + ' ms')
            else:
                main.log.info('ONOS1 Link-to-ofp skipped. Result: ' +
                        str(ptDownLinkToOfp1) + ' ms')
            if clusterCount >= 3:
                jsonStrUp2 = main.ONOS2cli.topologyEventsMetrics()
                jsonStrUp3 = main.ONOS3cli.topologyEventsMetrics()
                jsonObj2 = json.loads(jsonStrUp2)
                jsonObj3 = json.loads(jsonStrUp3)
                graphTimestamp2 = jsonObj2[graphTimestamp]['value']
                graphTimestamp3 = jsonObj3[graphTimestamp]['value']
                deviceTimestamp2 = jsonObj2[deviceTimestamp]['value']
                deviceTimestamp3 = jsonObj3[deviceTimestamp]['value']
                linkTimestamp2 = jsonObj2[linkTimestamp]['value']
                linkTimestamp3 = jsonObj3[linkTimestamp]['value']
                ptDownGraphToOfp2 = int(graphTimestamp2) - int(timestampBeginPtDown)
                ptDownGraphToOfp3 = int(graphTimestamp3) - int(timestampBeginPtDown)
                ptDownDeviceToOfp2 = int(deviceTimestamp2) - int(timestampBeginPtDown)
                ptDownDeviceToOfp3 = int(deviceTimestamp3) - int(timestampBeginPtDown)
                ptDownLinkToOfp2 = int(linkTimestamp2) - int(timestampBeginPtDown)
                ptDownLinkToOfp3 = int(linkTimestamp3) - int(timestampBeginPtDown)
                if ptDownGraphToOfp2 > downThresholdMin and\
                   ptDownGraphToOfp2 < downThresholdMax and i > iterIgnore:
                    portDownGraphNodeIter[1][i] = ptDownGraphToOfp2
                    main.log.info('ONOS2 iter' + str(i) +
                            ' graph-to-ofp: ' +
                            str(ptDownGraphToOfp2) + ' ms')
                if ptDownDeviceToOfp2 > downThresholdMin and \
                   ptDownDeviceToOfp2 < downThresholdMax and i > iterIgnore:
                    portDownDevNodeIter[1][i] = ptDownDeviceToOfp2
                    main.log.info('ONOS2 iter' + str(i) +
                            ' device-to-ofp: ' +
                            str(ptDownDeviceToOfp2) + ' ms')
                if ptDownLinkToOfp2 > downThresholdMin and\
                   ptDownLinkToOfp2 < downThresholdMax and i > iterIgnore:
                    portDownLinkNodeIter[1][i] = ptDownLinkToOfp2
                    main.log.info('ONOS2 iter' + str(i) +
                            ' link-to-ofp: ' +
                            str(ptDownLinkToOfp2) + ' ms')
                if ptDownGraphToOfp3 > downThresholdMin and\
                   ptDownGraphToOfp3 < downThresholdMax and i > iterIgnore:
                    portDownGraphNodeIter[2][i] = ptDownGraphToOfp3
                    main.log.info('ONOS3 iter' + str(i) +
                            ' graph-to-ofp: ' +
                            str(ptDownGraphToOfp3) + ' ms')
                if ptDownDeviceToOfp3 > downThresholdMin and\
                   ptDownDeviceToOfp3 < downThresholdMax and i > iterIgnore:
                    portDownDevNodeIter[2][i] = ptDownDeviceToOfp3
                    main.log.info('ONOS3 iter' + str(i) +
                            ' device-to-ofp: ' +
                            str(ptDownDeviceToOfp3) + ' ms')
                if ptDownLinkToOfp3 > downThresholdMin and\
                   ptDownLinkToOfp3 < downThresholdMax and i > iterIgnore:
                    portDownLinkNodeIter[2][i] = ptDownLinkToOfp3
                    main.log.info('ONOS3 iter' + str(i) +
                            ' link-to-ofp: ' +
                            str(ptDownLinkToOfp3) + ' ms')
            if clusterCount >= 5:
                jsonStrUp4 = main.ONOS4cli.topologyEventsMetrics()
                jsonStrUp5 = main.ONOS5cli.topologyEventsMetrics()
                jsonObj4 = json.loads(jsonStrUp4)
                jsonObj5 = json.loads(jsonStrUp5)
                graphTimestamp4 = jsonObj4[graphTimestamp]['value']
                graphTimestamp5 = jsonObj5[graphTimestamp]['value']
                deviceTimestamp4 = jsonObj4[deviceTimestamp]['value']
                deviceTimestamp5 = jsonObj5[deviceTimestamp]['value']
                linkTimestamp4 = jsonObj4[linkTimestamp]['value']
                linkTimestamp5 = jsonObj5[linkTimestamp]['value']
                ptDownGraphToOfp4 = int(graphTimestamp4) - int(timestampBeginPtDown)
                ptDownGraphToOfp5 = int(graphTimestamp5) - int(timestampBeginPtDown)
                ptDownDeviceToOfp4 = int(deviceTimestamp4) - int(timestampBeginPtDown)
                ptDownDeviceToOfp5 = int(deviceTimestamp5) - int(timestampBeginPtDown)
                ptDownLinkToOfp4 = int(linkTimestamp4) - int(timestampBeginPtDown)
                ptDownLinkToOfp5 = int(linkTimestamp5) - int(timestampBeginPtDown)
                if ptDownGraphToOfp4 > downThresholdMin and \
                   ptDownGraphToOfp4 < downThresholdMax and i > iterIgnore:
                    portDownGraphNodeIter[3][i] = ptDownGraphToOfp4
                    main.log.info('ONOS4 iter' + str(i) +
                            ' graph-to-ofp: ' +
                            str(ptDownGraphToOfp4) + ' ms')
                if ptDownDeviceToOfp4 > downThresholdMin and\
                   ptDownDeviceToOfp4 < downThresholdMax and i > iterIgnore:
                    portDownDevNodeIter[3][i] = ptDownDeviceToOfp4
                    main.log.info('ONOS4 iter' + str(i) +
                            ' device-to-ofp: ' +
                            str(ptDownDeviceToOfp4) + ' ms')
                if ptDownLinkToOfp4 > downThresholdMin and\
                   ptDownLinkToOfp4 < downThresholdMax and i > iterIgnore:
                    portDownLinkNodeIter[3][i] = ptDownLinkToOfp4
                    main.log.info('ONOS4 iter' + str(i) +
                            ' link-to-ofp: ' +
                            str(ptDownLinkToOfp4) + ' ms')
                if ptDownGraphToOfp5 > downThresholdMin and\
                   ptDownGraphToOfp5 < downThresholdMax and i > iterIgnore:
                    portDownGraphNodeIter[4][i] = ptDownGraphToOfp5
                    main.log.info('ONOS5 iter' + str(i) +
                            ' graph-to-ofp: ' +
                            str(ptDownGraphToOfp5) + ' ms')
                if ptDownDeviceToOfp5 > downThresholdMin and\
                   ptDownDeviceToOfp5 < downThresholdMax and i > iterIgnore:
                    portDownDevNodeIter[4][i] = ptDownDeviceToOfp5
                    main.log.info('ONOS5 iter' + str(i) +
                            ' device-to-ofp: ' +
                            str(ptDownDeviceToOfp5) + ' ms')
                if ptDownLinkToOfp5 > downThresholdMin and\
                   ptDownLinkToOfp5 < downThresholdMax and i > iterIgnore:
                    portDownLinkNodeIter[4][i] = ptDownLinkToOfp5
                    main.log.info('ONOS5 iter' + str(i) +
                            ' link-to-ofp: ' +
                            str(ptDownLinkToOfp5) + ' ms')
            if clusterCount >= 7:
                jsonStrUp6 = main.ONOS6cli.topologyEventsMetrics()
                jsonStrUp7 = main.ONOS7cli.topologyEventsMetrics()
                jsonObj6 = json.loads(jsonStrUp6)
                jsonObj7 = json.loads(jsonStrUp7)
                graphTimestamp6 = jsonObj6[graphTimestamp]['value']
                graphTimestamp7 = jsonObj7[graphTimestamp]['value']
                deviceTimestamp6 = jsonObj6[deviceTimestamp]['value']
                deviceTimestamp7 = jsonObj7[deviceTimestamp]['value']
                linkTimestamp6 = jsonObj6[linkTimestamp]['value']
                linkTimestamp7 = jsonObj7[linkTimestamp]['value']
                ptDownGraphToOfp6 = int(graphTimestamp6) - int(timestampBeginPtDown)
                ptDownGraphToOfp7 = int(graphTimestamp7) - int(timestampBeginPtDown)
                ptDownDeviceToOfp6 = int(deviceTimestamp6) - int(timestampBeginPtDown)
                ptDownDeviceToOfp7 = int(deviceTimestamp7) - int(timestampBeginPtDown)
                ptDownLinkToOfp6 = int(linkTimestamp6) - int(timestampBeginPtDown)
                ptDownLinkToOfp7 = int(linkTimestamp7) - int(timestampBeginPtDown)
                if ptDownGraphToOfp6 > downThresholdMin and\
                   ptDownGraphToOfp6 < downThresholdMax and i > iterIgnore:
                    portDownGraphNodeIter[5][i] = ptDownGraphToOfp6
                    main.log.info('ONOS6 iter' + str(i) +
                            ' graph-to-ofp: ' +
                            str(ptDownGraphToOfp6) + ' ms')
                if ptDownDeviceToOfp6 > downThresholdMin and\
                   ptDownDeviceToOfp6 < downThresholdMax and i > iterIgnore:
                    portDownDevNodeIter[5][i] = ptDownDeviceToOfp6
                    main.log.info('ONOS6 iter' + str(i) +
                            ' device-to-ofp: ' +
                            str(ptDownDeviceToOfp6) + ' ms')
                if ptDownLinkToOfp6 > downThresholdMin and\
                   ptDownLinkToOfp6 < downThresholdMax and i > iterIgnore:
                    portDownLinkNodeIter[5][i] = ptDownLinkToOfp6
                    main.log.info('ONOS6 iter' + str(i) +
                            ' link-to-ofp: ' +
                            str(ptDownLinkToOfp6) + ' ms')
                if ptDownGraphToOfp7 > downThresholdMin and\
                   ptDownGraphToOfp7 < downThresholdMax and i > iterIgnore:
                    portDownGraphNodeIter[6][i] = ptDownGraphToOfp7
                    main.log.info('ONOS7 iter' + str(i) +
                            ' graph-to-ofp: ' +
                            str(ptDownGraphToOfp7) + ' ms')
                if ptDownDeviceToOfp7 > downThresholdMin and\
                   ptDownDeviceToOfp7 < downThresholdMax and i > iterIgnore:
                    portDownDevNodeIter[6][i] = ptDownDeviceToOfp7
                    main.log.info('ONOS7 iter' + str(i) +
                            ' device-to-ofp: ' + 
                            str(ptDownDeviceToOfp7) + ' ms')
                if ptDownLinkToOfp7 > downThresholdMin and\
                   ptDownLinkToOfp7 < downThresholdMax and i > iterIgnore:
                    portDownLinkNodeIter[6][i] = ptDownLinkToOfp7
                    main.log.info('ONOS7 iter' + str(i) +
                            ' link-to-ofp: ' +
                            str(ptDownLinkToOfp7) + ' ms')
            
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
            main.step('Obtain t1 by REST call')
            jsonStrUp1 = main.ONOS1cli.topologyEventsMetrics()
            jsonObj1 = json.loads(jsonStrUp1)
            graphTimestamp1 = jsonObj1[graphTimestamp]['value']
            deviceTimestamp1 = jsonObj1[deviceTimestamp]['value']
            linkTimestamp1 = jsonObj1[linkTimestamp]['value']
            ptUpGraphToOfp1 = int(graphTimestamp1) - int(timestampBeginPtUp)
            ptUpDeviceToOfp1 = int(deviceTimestamp1) - int(timestampBeginPtUp)
            ptUpLinkToOfp1 = int(linkTimestamp1) - int(timestampBeginPtUp)
            if ptUpGraphToOfp1 > upThresholdMin and\
               ptUpGraphToOfp1 < upThresholdMax and i > iterIgnore:
                portUpGraphNodeIter[0][i] = ptUpGraphToOfp1
                main.log.info('ONOS1 iter' + str(i) +
                        ' port up graph-to-ofp: ' +
                        str(ptUpGraphToOfp1) + ' ms')
            else:
                main.log.info('ONOS1 iter' + str(i) +
                        ' skipped. Result: ' +
                        str(ptUpGraphToOfp1) + ' ms')
            if ptUpDeviceToOfp1 > upThresholdMin and \
               ptUpDeviceToOfp1 < upThresholdMax and i > iterIgnore:
                portUpDevNodeIter[0][i] = ptUpDeviceToOfp1
                main.log.info('ONOS1 iter' + str(i) +
                        ' port up device-to-ofp: ' +
                        str(ptUpDeviceToOfp1) + ' ms')
            else:
                main.log.info('ONOS1 iter' + str(i) +
                        ' skipped. Result: ' +
                        str(ptUpDeviceToOfp1) + ' ms')
            if ptUpLinkToOfp1 > downThresholdMin and\
               ptUpLinkToOfp1 < downThresholdMax and i > iterIgnore:
                portUpLinkNodeIter[0][i] = ptUpLinkToOfp1
                main.log.info('ONOS1 iter' + str(i) +
                        ' link-to-ofp: ' +
                        str(ptUpLinkToOfp1) + ' ms')
            if clusterCount >= 3:
                jsonStrUp2 = main.ONOS2cli.topologyEventsMetrics()
                jsonStrUp3 = main.ONOS3cli.topologyEventsMetrics()
                jsonObj2 = json.loads(jsonStrUp2)
                jsonObj3 = json.loads(jsonStrUp3)
                graphTimestamp2 = jsonObj2[graphTimestamp]['value']
                graphTimestamp3 = jsonObj3[graphTimestamp]['value']
                deviceTimestamp2 = jsonObj2[deviceTimestamp]['value']
                deviceTimestamp3 = jsonObj3[deviceTimestamp]['value']
                linkTimestamp2 = jsonObj2[linkTimestamp]['value']
                linkTimestamp3 = jsonObj3[linkTimestamp]['value']
                ptUpGraphToOfp2 = int(graphTimestamp2) - int(timestampBeginPtUp)
                ptUpGraphToOfp3 = int(graphTimestamp3) - int(timestampBeginPtUp)
                ptUpDeviceToOfp2 = int(deviceTimestamp2) - int(timestampBeginPtUp)
                ptUpDeviceToOfp3 = int(deviceTimestamp3) - int(timestampBeginPtUp)
                ptUpLinkToOfp2 = int(linkTimestamp2) - int(timestampBeginPtUp)
                ptUpLinkToOfp3 = int(linkTimestamp3) - int(timestampBeginPtUp)
                if ptUpGraphToOfp2 > upThresholdMin and\
                   ptUpGraphToOfp2 < upThresholdMax and i > iterIgnore:
                    portUpGraphNodeIter[1][i] = ptUpGraphToOfp2
                    main.log.info('ONOS2 iter' + str(i) +
                            ' port up graph-to-ofp: ' +
                            str(ptUpGraphToOfp2) + ' ms')
                if ptUpDeviceToOfp2 > upThresholdMin and\
                   ptUpDeviceToOfp2 < upThresholdMax and i > iterIgnore:
                    portUpDevNodeIter[1][i] = ptUpDeviceToOfp2
                    main.log.info('ONOS2 iter' + str(i) +
                            ' port up device-to-ofp: ' +
                            str(ptUpDeviceToOfp2) + ' ms')
                if ptUpLinkToOfp2 > downThresholdMin and\
                   ptUpLinkToOfp2 < downThresholdMax and i > iterIgnore:
                    portUpLinkNodeIter[1][i] = ptUpLinkToOfp2
                    main.log.info('ONOS2 iter' + str(i) +
                            ' port up link-to-ofp: ' +
                            str(ptUpLinkToOfp2) + ' ms')
                if ptUpGraphToOfp3 > upThresholdMin and\
                   ptUpGraphToOfp3 < upThresholdMax and i > iterIgnore:
                    portUpGraphNodeIter[2][i] = ptUpGraphToOfp3
                    main.log.info('ONOS3 iter' + str(i) +
                            ' port up graph-to-ofp: ' +
                            str(ptUpGraphToOfp3) + ' ms')
                if ptUpDeviceToOfp3 > upThresholdMin and\
                   ptUpDeviceToOfp3 < upThresholdMax and i > iterIgnore:
                    portUpDevNodeIter[2][i] = ptUpDeviceToOfp3
                    main.log.info('ONOS3 iter' + str(i) +
                            ' port up device-to-ofp: ' +
                            str(ptUpDeviceToOfp3) + ' ms')
                if ptUpLinkToOfp3 > downThresholdMin and\
                   ptUpLinkToOfp3 < downThresholdMax and i > iterIgnore:
                    portUpLinkNodeIter[2][i] = ptUpLinkToOfp3
                    main.log.info('ONOS3 iter' + str(i) +
                            ' port up link-to-ofp: ' +
                            str(ptUpLinkToOfp3) + ' ms')
            if clusterCount >= 5:
                jsonStrUp4 = main.ONOS4cli.topologyEventsMetrics()
                jsonStrUp5 = main.ONOS5cli.topologyEventsMetrics()
                jsonObj4 = json.loads(jsonStrUp4)
                jsonObj5 = json.loads(jsonStrUp5)
                graphTimestamp4 = jsonObj4[graphTimestamp]['value']
                graphTimestamp5 = jsonObj5[graphTimestamp]['value']
                deviceTimestamp4 = jsonObj4[deviceTimestamp]['value']
                deviceTimestamp5 = jsonObj5[deviceTimestamp]['value']
                linkTimestamp4 = jsonObj4[linkTimestamp]['value']
                linkTimestamp5 = jsonObj5[linkTimestamp]['value']
                ptUpGraphToOfp4 = int(graphTimestamp4) - int(timestampBeginPtUp)
                ptUpGraphToOfp5 = int(graphTimestamp5) - int(timestampBeginPtUp)
                ptUpDeviceToOfp4 = int(deviceTimestamp4) - int(timestampBeginPtUp)
                ptUpDeviceToOfp5 = int(deviceTimestamp5) - int(timestampBeginPtUp)
                ptUpLinkToOfp4 = int(linkTimestamp4) - int(timestampBeginPtUp)
                ptUpLinkToOfp5 = int(linkTimestamp5) - int(timestampBeginPtUp)
                if ptUpGraphToOfp4 > upThresholdMin and\
                   ptUpGraphToOfp4 < upThresholdMax and i > iterIgnore:
                    portUpGraphNodeIter[3][i] = ptUpGraphToOfp4
                    main.log.info('ONOS4 iter' + str(i) +
                            ' port up graph-to-ofp: ' +
                            str(ptUpGraphToOfp4) + ' ms')
                if ptUpDeviceToOfp4 > upThresholdMin and\
                   ptUpDeviceToOfp4 < upThresholdMax and i > iterIgnore:
                    portUpDevNodeIter[3][i] = ptUpDeviceToOfp4
                    main.log.info('ONOS4 iter' + str(i) +
                            ' port up device-to-ofp: ' +
                            str(ptUpDeviceToOfp4) + ' ms')
                if ptUpGraphToOfp5 > upThresholdMin and\
                    ptUpGraphToOfp5 < upThresholdMax and i > iterIgnore:
                    portUpGraphNodeIter[4][i] = ptUpGraphToOfp5
                    main.log.info('ONSO5 iter' + str(i) +
                            ' port up graph-to-ofp: ' +
                            str(ptUpGraphToOfp5) + ' ms')
                if ptUpDeviceToOfp5 > upThresholdMin and \
                   ptUpDeviceToOfp5 < upThresholdMax and i > iterIgnore:
                    portUpDevNodeIter[4][i] = ptUpDeviceToOfp5
                    main.log.info('ONOS5 iter' + str(i) +
                            ' port up device-to-ofp: ' +
                            str(ptUpDeviceToOfp5) + ' ms')
            if clusterCount >= 7:
                jsonStrUp6 = main.ONOS6cli.topologyEventsMetrics()
                jsonStrUp7 = main.ONOS7cli.topologyEventsMetrics()
                jsonObj6 = json.loads(jsonStrUp6)
                jsonObj7 = json.loads(jsonStrUp7)
                graphTimestamp6 = jsonObj6[graphTimestamp]['value']
                graphTimestamp7 = jsonObj7[graphTimestamp]['value']
                deviceTimestamp6 = jsonObj6[deviceTimestamp]['value']
                deviceTimestamp7 = jsonObj7[deviceTimestamp]['value']
                ptUpGraphToOfp6 = int(graphTimestamp6) - int(timestampBeginPtUp)
                ptUpGraphToOfp7 = int(graphTimestamp7) - int(timestampBeginPtUp)
                ptUpDeviceToOfp6 = int(deviceTimestamp6) - int(timestampBeginPtUp)
                ptUpDeviceToOfp7 = int(deviceTimestamp7) - int(timestampBeginPtUp)
                if ptUpGraphToOfp6 > upThresholdMin and\
                   ptUpGraphToOfp6 < upThresholdMax and i > iterIgnore:
                    portUpGraphNodeIter[5][i] = ptUpGraphToOfp6
                    main.log.info('iter' + str(i) +
                            ' port up graph-to-ofp: ' +
                            str(ptUpGraphToOfp6) + ' ms')
                if ptUpDeviceToOfp6 > upThresholdMin and\
                   ptUpDeviceToOfp6 < upThresholdMax and i > iterIgnore:
                    portUpDevNodeIter[5][i] = ptUpDeviceToOfp6
                    main.log.info('iter' + str(i) +
                            ' port up device-to-ofp: ' + 
                            str(ptUpDeviceToOfp6) + ' ms')
                if ptUpGraphToOfp7 > upThresholdMin and \
                   ptUpGraphToOfp7 < upThresholdMax and i > iterIgnore:
                    portUpGraphNodeIter[6][i] = ptUpGraphToOfp7
                    main.log.info('iter' + str(i) +
                            ' port up graph-to-ofp: ' + 
                            str(ptUpGraphToOfp7) + ' ms')
                if ptUpDeviceToOfp7 > upThresholdMin and\
                   ptUpDeviceToOfp7 < upThresholdMax and i > iterIgnore:
                    portUpDevNodeIter[6][i] = ptUpDeviceToOfp7
                    main.log.info('iter' + str(i) +
                            ' port up device-to-ofp: ' +
                            str(ptUpDeviceToOfp7) + ' ms')

        dbCmdList = []
        for node in range(0, clusterCount):
            portUpDevList = []
            portUpGraphList = []
            portDownDevList = []
            portDownGraphList = []
            portUpDevAvg = 0
            portUpGraphAvg = 0
            portDownDevAvg = 0
            portDownGraphAvg = 0
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
            portUpStdDev = round(numpy.std(portUpGraphList), 2)
            portDownStdDev = round(numpy.std(portDownGraphList), 2)
            main.log.report(' - Node ' + str(node + 1) + ' Summary - ')
            main.log.report(' Port up ofp-to-device ' +
                    str(round(portUpDevAvg, 2)) + ' ms')
            main.log.report(' Port up ofp-to-graph ' +
                    str(portUpGraphAvg) + ' ms')
            main.log.report(' Port down ofp-to-device ' +
                    str(round(portDownDevAvg, 2)) + ' ms')
            main.log.report(' Port down ofp-to-graph ' +
                    str(portDownGraphAvg) + ' ms')
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

        for node in range( 1, clusterCount + 1):
            exec "a = main.ONOS%scli.startOnosCli" %str(node)
            a(main.params[ 'CTRL' ][ 'ip'+str(node) ])

