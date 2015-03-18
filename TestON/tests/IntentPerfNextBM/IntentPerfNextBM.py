# 2015.03.12 10:28:21 PDT
#Embedded file name: ../tests/IntentPerfNextBM/IntentPerfNextBM.py


class IntentPerfNextBM:

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
        intentFilePath = main.params['DB']['intentFilePath']
        ONOSIp = []
        
        for i in range(1, 8):
            ONOSIp.append(main.params['CTRL']['ip' + str(i)])
            main.ONOSbench.onosUninstall(nodeIp=ONOSIp[i - 1])

        MN1Ip = main.params['MN']['ip1']
        BENCHIp = main.params['BENCH']['ip']
        main.case('Setting up test environment')
        main.step('Clearing previous DB log file')
        fIntentLog = open(intentFilePath, 'w')
        fIntentLog.write('')
        fIntentLog.close()
        main.step('Starting mininet topology')
        main.Mininet1.startNet()
        main.step('Creating cell file')
        cellFileResult = main.TRUE
        main.step('Applying cell file to environment')
        cellApplyResult = main.ONOSbench.setCell(cellName)
        verifyCellResult = main.ONOSbench.verifyCell()
        main.step('Removing raft logs')
        main.ONOSbench.onosRemoveRaftLogs()
        main.step('Git checkout and pull ' + checkoutBranch)
        
        if gitPull == 'on':
            checkoutResult = main.ONOSbench.gitCheckout(checkoutBranch)
            pullResult = main.ONOSbench.gitPull()
            main.step('Using onos-build to compile ONOS')
            buildResult = main.ONOSbench.onosBuild()
        else:
            checkoutResult = main.TRUE
            pullResult = main.TRUE
            buildResult = main.TRUE
            main.log.info('Git pull skipped by configuration')
        
        main.log.report('Commit information - ')
        main.ONOSbench.getVersion(report=True)
        main.step('Creating ONOS package')
        packageResult = main.ONOSbench.onosPackage()
        main.step('Installing ONOS package')
        install1Result = main.ONOSbench.onosInstall(node=ONOSIp[0])
        main.step('Set cell for ONOScli env')
        main.ONOS1cli.setCell(cellName)
        time.sleep(5)
        main.step('Start onos cli')
        cli1 = main.ONOS1cli.startOnosCli(ONOSIp[0])
        utilities.assert_equals(expect=main.TRUE, 
                actual=cellFileResult and cellApplyResult and\
                        verifyCellResult and checkoutResult and\
                        pullResult and buildResult and install1Result, 
                        onpass='ONOS started successfully',
                        onfail='Failed to start ONOS')

    def CASE2(self, main):
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
        ONOS1Ip = main.params['CTRL']['ip1']
        ONOS2Ip = main.params['CTRL']['ip2']
        ONOS3Ip = main.params['CTRL']['ip3']
        ONOS4Ip = main.params['CTRL']['ip4']
        ONOS5Ip = main.params['CTRL']['ip5']
        ONOS6Ip = main.params['CTRL']['ip6']
        ONOS7Ip = main.params['CTRL']['ip7']
        assertion = main.TRUE
        ONOSIpList = []
        
        for i in range(1, 8):
            ONOSIpList.append(main.params['CTRL']['ip' + str(i)])

        ONOSUser = main.params['CTRL']['user']
        defaultSwPort = main.params['CTRL']['port1']
        batchIntentSize = int(main.params['TEST']['batchIntentSize'])
        batchThreshMin = int(main.params['TEST']['batchThresholdMin'])
        batchThreshMax = int(main.params['TEST']['batchThresholdMax'])
        numIter = main.params['TEST']['numIter']
        numIgnore = int(main.params['TEST']['numIgnore'])
        numSwitch = int(main.params['TEST']['numSwitch'])
        nThread = main.params['TEST']['numMult']
        intentFilePath = main.params['DB']['intentFilePath']
        
        if clusterCount == 1:
            for i in range(1, numSwitch + 1):
                main.Mininet1.assignSwController(sw=str(i),
                        ip1=ONOS1Ip, port1=defaultSwPort)
        if clusterCount == 3:
            for i in range(1, 3):
                main.Mininet1.assignSwController(sw=str(i),
                        ip1=ONOS1Ip, port1=defaultSwPort)
            for i in range(3, 6):
                main.Mininet1.assignSwController(sw=str(i),
                        ip1=ONOS2Ip, port1=defaultSwPort)
            for i in range(6, 9):
                main.Mininet1.assignSwController(sw=str(i),
                        ip1=ONOS3Ip, port1=defaultSwPort)
        if clusterCount == 5:
            main.Mininet1.assignSwController(sw='1',
                    ip1=ONOS1Ip, port1=defaultSwPort)
            main.Mininet1.assignSwController(sw='2',
                    ip1=ONOS2Ip, port1=defaultSwPort)
            for i in range(3, 6):
                main.Mininet1.assignSwController(sw=str(i),
                        ip1=ONOS3Ip, port1=defaultSwPort)
            main.Mininet1.assignSwController(sw='6',
                    ip1=ONOS4Ip, port1=defaultSwPort)
            main.Mininet1.assignSwController(sw='7', 
                    ip1=ONOS5Ip, port1=defaultSwPort)
            main.Mininet1.assignSwController(sw='8',
                    ip1=ONOS5Ip, port1=defaultSwPort)
        if clusterCount == 7:
            for i in range(1, 9):
                if i < 8:
                    main.Mininet1.assignSwController(sw=str(i),
                            ip1=ONOSIpList[i - 1], port1=defaultSwPort)
                elif i >= 8:
                    main.Mininet1.assignSwController(sw=str(i),
                            ip1=ONOSIpList[6], port1=defaultSwPort)

        time.sleep(20)
        
        batchResultList = []
        deviceIdList = []
        batchInstallLat = []
        batchWithdrawLat = []

        main.log.report('Batch intent installation test of ' +
                str(batchIntentSize) + ' intent(s)')
        main.log.info('Getting list of available devices')
        
        jsonStr = main.ONOS1cli.devices()
        jsonObj = json.loads(jsonStr)
        for device in jsonObj:
            deviceIdList.append(device['id'])

        sleepTime = 10
        baseDir = '/tmp/'
        for batch in range(0, 5):
            maxInstallLat = []
            maxWithdrawLat = []
            maxSingleInstallLat = []
            maxSingleWithdrawLat = []
            for i in range(0, int(numIter)):
                main.log.info('Pushing ' + str(
                    int(batchIntentSize) * int(nThread)) +
                    ' intents. Iteration ' + str(i))
                saveDir = baseDir + 'batch_intent_1.txt'
                main.ONOSbench.pushTestIntentsShell(deviceIdList[0] +
                        '/2', deviceIdList[7] + '/2', batchIntentSize,
                        saveDir, ONOSIpList[0], numMult=nThread)
                time.sleep(sleepTime)
                intent = ''
                counter = 300
                while len(intent) > 0 and counter > 0:
                    main.ONOS1cli.handle.sendline('intents | wc -l')
                    main.ONOS1cli.handle.expect('intents | wc -l')
                    main.ONOS1cli.handle.expect('onos>')
                    intentTemp = main.ONOS1cli.handle.before()
                    intent = main.ONOS1cli.intents()
                    intent = json.loads(intent)
                    counter = counter - 1
                    time.sleep(1)

                time.sleep(5)
                saveDir = baseDir + 'batch_intent_1.txt'
                with open(saveDir) as fOnos:
                    lineCount = 0
                    for line in fOnos:
                        line_temp = ''
                        main.log.info('Line read: ' + str(line))
                        line_temp = line[1:]
                        line_temp = line_temp.split(': ')
                        if ' ' in str(line_temp):
                            result = line_temp[1].split(' ')[0]
                        else:
                            main.log.warn('Empty line read')
                            result = 0
                        if lineCount == 0:
                            if 'Failure' in str(line):
                                main.log.warn('Intent installation failed')
                                result = 'NA'
                            else:
                                main.log.info('Install result: ' + result)
                                batchInstallLat.append(int(result))
                            installResult = result
                        elif lineCount == 1:
                            if 'Failure' in str(line):
                                main.log.warn('Intent withdraw failed')
                                result = 'NA'
                            else:
                                main.log.info('Withdraw result: ' + result)
                                batchWithdrawLat.append(int(result))
                            withdrawResult = result
                        else:
                            main.log.warn('Invalid results')
                            installResult = 'NA'
                            withdrawResult = 'NA'
                        lineCount += 1

                main.log.info('Batch install latency with' +
                        str(batchIntentSize) + 'intents: ' +
                        str(installResult) + ' ms')
                main.log.info('Batch withdraw latency with' +
                        str(batchIntentSize) + 'intents: ' +
                        str(withdrawResult) + ' ms')
                main.log.info('Single intent install latency with' +
                        str(batchIntentSize) + 'intents: ' +
                        str(float(installResult) / int(batchIntentSize))+' ms')
                main.log.info('Single intent withdraw latency with' +
                        str(batchIntentSize) + 'intents: ' +
                        str(float(withdrawResult)/ int(batchIntentSize))+' ms')
                if len(batchInstallLat) > 0 and int(i) > numIgnore:
                    maxInstallLat.append(max(batchInstallLat))
                    maxSingleInstallLat.append(
                            max(batchInstallLat) / int(batchIntentSize))
                elif len(batchInstallLat) == 0:
                    sleepTime += 30
                if len(batchWithdrawLat) > 0 and int(i) > numIgnore:
                    maxWithdrawLat.append(max(batchWithdrawLat))
                    maxSingleWithdrawLat.append(
                            max(batchWithdrawLat) / int(batchIntentSize))
                batchInstallLat = []
                batchWithdrawLat = []
                time.sleep(5)

            if maxInstallLat:
                avgInstallLat = str(round(
                    numpy.average(maxInstallLat), 2))
                stdInstallLat = str(round(
                    numpy.std(maxInstallLat), 2))
                avgSingleInstallLat = str(round(
                    numpy.average(maxSingleInstallLat), 3))
                stdSingleInstallLat = str(round(
                    numpy.std(maxSingleInstallLat), 3))
            else:
                avgInstallLat = 'NA'
                stdInstallLat = 'NA'
                main.log.report('Batch installation failed')
                assertion = main.FALSE
            if maxWithdrawLat:
                avgWithdrawLat = str(round(
                    numpy.average(maxWithdrawLat), 2))
                stdWithdrawLat = str(round(
                    numpy.std(maxWithdrawLat), 2))
                avgSingleWithdrawLat = str(round(
                    numpy.average(maxSingleWithdrawLat), 3))
                stdSingleWithdrawLat = str(round(
                    numpy.std(maxSingleWithdrawLat), 3))
            else:
                avgWithdrawLat = 'NA'
                stdWithdrawLat = 'NA'
                main.log.report('Batch withdraw failed')
                assertion = main.FALSE
            main.log.report('Avg of batch installation latency ' +
                    'of size ' + str(batchIntentSize) + ': ' +
                    str(avgInstallLat) + ' ms')
            main.log.report('Std Deviation of batch installation latency ' +
                    ': ' + str(round(numpy.std(maxInstallLat), 2)) + ' ms')
            main.log.report('Avg of batch withdraw latency ' +
                    'of size ' + str(batchIntentSize) + ': ' +
                    str(avgWithdrawLat) + ' ms')
            main.log.report('Std Deviation of batch withdraw latency ' +
                    ': ' + str(round(numpy.std(maxWithdrawLat), 2)) + ' ms')
            main.log.report('Avg of batch withdraw latency ' + 'of size ' +
                    str(batchIntentSize) + ': ' + str(avgWithdrawLat) + ' ms')
            main.log.report('Std Deviation of batch withdraw latency ' +
                    ': ' + str(stdWithdrawLat) + ' ms')
            main.log.report('Avg of single withdraw latency ' + 'of size ' +
                    str(batchIntentSize) + ': ' +
                    str(avgSingleWithdrawLat) + ' ms')
            main.log.report('Std Deviation of single withdraw latency ' +
                    ': ' + str(stdSingleWithdrawLat) + ' ms')
            dbCmd = "INSERT INTO intents_latency_tests VALUES('" +\
                    timeToPost + "','intents_latency_results'," +\
                    runNum + ',' + str(clusterCount) + ',' +\
                    str(batchIntentSize) + ',' + str(avgInstallLat) +\
                    ',' + str(stdInstallLat) + ',' + str(avgWithdrawLat) +\
                    ',' + str(stdWithdrawLat) + ');'
            
            fResult = open(intentFilePath, 'a')
            if dbCmd:
                fResult.write(dbCmd + '\n')
            fResult.close()
            if batch == 0:
                batchIntentSize = 10
            elif batch == 1:
                batchIntentSize = 100
            elif batch == 2:
                batchIntentSize = 1000
            elif batch == 3:
                batchIntentSize = 1500
            if batch < 4:
                main.log.report('Increasing batch intent size to ' +
                        str(batchIntentSize))

        utilities.assert_equals(expect=main.TRUE, actual=assertion,
                onpass='Batch intent install/withdraw test successful',
                onfail='Batch intent install/withdraw test failed')

    def CASE3(self, main):
        """
        Batch intent reroute latency
        """
        import time
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
        
        ONOSIpList = []
        for i in range(1, 8):
            ONOSIpList.append(main.params['CTRL']['ip' + str(i)])

        ONOSUser = main.params['CTRL']['user']
        defaultSwPort = main.params['CTRL']['port1']
        batchIntentSize = main.params['TEST']['batchIntentSize']
        thresholdMin = int(main.params['TEST']['batchThresholdMin'])
        thresholdMax = int(main.params['TEST']['batchThresholdMax'])
        
        intfs = main.params['TEST']['intfs']
        installTime = main.params['JSON']['installedTime']
        numIter = main.params['TEST']['numIter']
        numIgnore = int(main.params['TEST']['numIgnore'])
        numSwitch = int(main.params['TEST']['numSwitch'])
        nThread = main.params['TEST']['numMult']
        
        tsharkPortStatus = main.params[ 'TSHARK' ][ 'ofpPortStatus' ]
        tsharkPortDown = '/tmp/tshark_port_down_reroute.txt'
        
        if clusterCount == 1:
            for i in range(1, numSwitch + 1):
                main.Mininet1.assignSwController(sw=str(i),
                        ip1=ONOS1Ip, port1=defaultSwPort)
        if clusterCount == 3:
            for i in range(1, 3):
                main.Mininet1.assignSwController(sw=str(i),
                        ip1=ONOS1Ip, port1=defaultSwPort)
            for i in range(3, 6):
                main.Mininet1.assignSwController(sw=str(i),
                        ip1=ONOS2Ip, port1=defaultSwPort)
            for i in range(6, 9):
                main.Mininet1.assignSwController(sw=str(i),
                        ip1=ONOS3Ip, port1=defaultSwPort)
        if clusterCount == 5:
            main.Mininet1.assignSwController(sw='1',
                    ip1=ONOS1Ip, port1=defaultSwPort)
            main.Mininet1.assignSwController(sw='2',
                    ip1=ONOS2Ip, port1=defaultSwPort)
            for i in range(3, 6):
                main.Mininet1.assignSwController(sw=str(i),
                        ip1=ONOS3Ip, port1=defaultSwPort)
            main.Mininet1.assignSwController(sw='6', 
                    ip1=ONOS4Ip, port1=defaultSwPort)
            main.Mininet1.assignSwController(sw='7',
                    ip1=ONOS5Ip, port1=defaultSwPort)
            main.Mininet1.assignSwController(sw='8',
                    ip1=ONOS5Ip, port1=defaultSwPort)
        if clusterCount == 7:
            for i in range(1, 9):
                if i < 8:
                    main.Mininet1.assignSwController(sw=str(i),
                            ip1=ONOSIpList[i - 1], port1=defaultSwPort)
                elif i >= 8:
                    main.Mininet1.assignSwController(sw=str(i),
                            ip1=ONOSIpList[6], port1=defaultSwPort)

        main.log.report('Batch intent reroute test ')

        batchIntentRerouteAvgSystem = numpy.zeros((
            clusterCount, int(numIter)))
        batchIntentRerouteStdSystem = numpy.zeros((
            clusterCount, int(numIter)))
        batchIntentRerouteAvgPort = numpy.zeros((
            clusterCount, int(numIter)))
        batchIntentRerouteStdSystem = numpy.zeros((
            clusterCount, int(numIter)))
        
        time.sleep(10)
        
        main.log.info('Getting list of available devices')
        
        deviceIdList = []
        jsonStr = main.ONOS1cli.devices()
        jsonObj = json.loads(jsonStr)
        for device in jsonObj:
            deviceIdList.append(device['id'])
        if not jsonObj:
            main.log.warn('No devices have been discovered')
            assertion = main.FALSE
        
        sleepTime = 10
        
        baseDir = '/tmp/'
        for batch in range(0, 5):
            maxRerouteLatSystem = []
            maxRerouteLatPort = []
            for i in range(0, int(numIter)):
                rerouteLatSystem = []
                rerouteLatPort = []
                main.log.info('Pushing ' + str(
                    int(batchIntentSize) * int(nThread)) +
                    ' intents. Iteration ' + str(i))
                main.ONOSbench.pushTestIntentsShell(
                        deviceIdList[0] + '/2', deviceIdList[7] +
                        '/2', batchIntentSize, '/tmp/batch_install.txt',
                        ONOSIpList[0], numMult='1', report=False,
                        options='-i')
                
                time.sleep(10)
                
                main.ONOS1.tsharkGrep(tsharkPortStatus, tsharkPortDown)
                main.log.info('Disabling interface ' + intfs)
                main.Mininet1.handle.sendline(
                        'sh ifconfig ' + intfs + ' down')
                t0System = time.time() * 1000
                
                time.sleep(3)
                
                main.ONOS1.tsharkStop()
                
                time.sleep(2)
                
                os.system('scp ' + ONOSUser + '@' + ONOSIpList[0] +
                        ':' + tsharkPortDown + ' /tmp/')
                time.sleep(5)
                
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
                            ' results: ' + str(fLine))
                fPortDown.close()
                
                intentsJsonStr1 = main.ONOS1cli.intentsEventsMetrics()
                intentsJsonObj1 = json.loads(intentsJsonStr1)
                intentInstall1 = intentsJsonObj1[installTime]['value']
                intentRerouteLat1 = int(intentInstall1) - int(t0System)
                intentRerouteLatPort1 =\
                        int(intentInstall1) - int(timestampBeginPtDown)
                
                if intentRerouteLat1 > thresholdMin and \
                        intentRerouteLat1 < thresholdMax and\
                        i > numIgnore:
                    rerouteLatSystem.append(intentRerouteLat1)
                main.log.info('ONOS1 Intent Reroute Lat ' +
                        ' size: ' + str(batchIntentSize) +
                        ' system-to-install: ' +
                        str(intentRerouteLat1) + ' ms')
                if intentRerouteLatPort1 > thresholdMin and\
                        intentRerouteLatPort1 < thresholdMax and\
                        i > numIgnore:
                    rerouteLatPort.append(intentRerouteLatPort1)
                
                main.log.info('ONOS1 Intent Reroute Lat ' +
                        ' size: ' + str(batchIntentSize) +
                        ' system-to-install: ' +
                        str(intentRerouteLatPort1) + ' ms')
                
                if clusterCount == 3:
                    intentsJsonStr2 = main.ONOS2cli.intentsEventsMetrics()
                    intentsJsonStr3 = main.ONOS3cli.intentsEventsMetrics()
                    intentsJsonObj2 = json.loads(intentsJsonStr2)
                    intentsJsonObj3 = json.loads(intentsJsonStr3)
                    intentInstall2 = intentsJsonObj2[installTime]['value']
                    intentInstall3 = intentsJsonObj3[installTime]['value']
                    intentRerouteLat2 = int(intentInstall2) - int(t0System)
                    intentRerouteLat3 = int(intentInstall3) - int(t0System)
                    intentRerouteLatPort2 = int(intentInstall2) - int(timestampBeginPtDown)
                    intentRerouteLatPort3 = int(intentInstall3) - int(timestampBeginPtDown)
                    
                    if intentRerouteLat2 > thresholdMin and\
                            intentRerouteLat2 < thresholdMax and\
                            i > numIgnore:
                        rerouteLatSystem.append(intentRerouteLat2)
                        main.log.info('ONOS2 Intent Reroute Lat' +
                                ' size: ' + str(batchIntentSize) +
                                ' system-to-install: ' + str(intentRerouteLat2) + ' ms')
                    if intentRerouteLat3 > thresholdMin and\
                            intentRerouteLat3 < thresholdMax and\
                            i > numIgnore:
                        rerouteLatSystem.append(intentRerouteLat3)
                        main.log.info('ONOS3 Intent Reroute Lat' +
                                ' size: ' + str(batchIntentSize) +
                                ' system-to-install: ' + str(intentRerouteLat3) +
                                ' ms')
                    if intentRerouteLatPort2 > thresholdMin and\
                            intentRerouteLatPort2 < thresholdMax and\
                            i > numIgnore:
                        rerouteLatPort.append(intentRerouteLatPort2)
                        main.log.info('ONOS2 Intent Reroute Lat' +
                                ' size: ' + str(batchIntentSize) +
                                ' port-to-install: ' +
                                str(intentRerouteLatPort2) + ' ms')
                    if intentRerouteLatPort3 > thresholdMin and\
                            intentRerouteLatPort3 < thresholdMax and\
                            i > numIgnore:
                        rerouteLatPort.append(intentRerouteLatPort3)
                        main.log.info('ONOS3 Intent Reroute Lat' +
                                ' size: ' + str(batchIntentSize) +
                                ' port-to-install: ' +
                                str(intentRerouteLatPort2) + ' ms')
                
                if clusterCount == 5:
                    intentsJsonStr4 = main.ONOS4cli.intentsEventsMetrics()
                    intentsJsonStr5 = main.ONOS5cli.intentsEventsMetrics()
                    intentsJsonObj4 = json.loads(intentsJsonStr4)
                    intentsJsonObj5 = json.loads(intentsJsonStr5)
                    intentInstall4 = intentsJsonObj4[installTime]['value']
                    intentInstall5 = intentsJsonObj5[installTime]['value']
                    intentRerouteLat4 = int(intentInstall4) - int(t0System)
                    intentRerouteLat5 = int(intentInstall5) - int(t0System)
                    intentRerouteLatPort4 =\
                            int(intentInstall4) - int(timestampBeginPtDown)
                    intentRerouteLatPort5 =\
                            int(intentInstall5) - int(timestampBeginPtDown)
                    if intentRerouteLat4 > thresholdMin and\
                            intentRerouteLat4 < thresholdMax and \
                            i > numIgnore:
                        rerouteLatSystem.append(intentRerouteLat4)
                        main.log.info('ONOS4 Intent Reroute Lat' +
                                ' size: ' + str(batchIntentSize) +
                                ' system-to-install: ' + str(intentRerouteLat4) +
                                ' ms')
                    if intentRerouteLat5 > thresholdMin and\
                            intentRerouteLat5 < thresholdMax and\
                            i > numIgnore:
                        rerouteLatSystem.append(intentRerouteLat5)
                        main.log.info('ONOS5 Intent Reroute Lat' +
                                ' size: ' + str(batchIntentSize) +
                                ' system-to-install: ' +
                                str(intentRerouteLat5) + ' ms')
                    if intentRerouteLatPort4 > thresholdMin and\
                            intentRerouteLatPort4 < thresholdMax and\
                            i > numIgnore:
                        rerouteLatPort.append(intentRerouteLatPort4)
                        main.log.info('ONOS4 Intent Reroute Lat' +
                                ' size: ' + str(batchIntentSize) +
                                ' port-to-install: ' +
                                str(intentRerouteLatPort4) + ' ms')
                    if intentRerouteLatPort5 > thresholdMin and\
                            intentRerouteLatPort5 < thresholdMax and\
                            i > numIgnore:
                        rerouteLatPort.append(intentRerouteLatPort5)
                        main.log.info('ONOS5 Intent Reroute Lat' +
                                ' size: ' + str(batchIntentSize) +
                                ' port-to-install: ' +
                                str(intentRerouteLatPort5) + ' ms')
                
                if clusterCount == 7:
                    intentsJsonStr6 = main.ONOS6cli.intentsEventsMetrics()
                    intentsJsonStr7 = main.ONOS7cli.intentsEventsMetrics()
                    intentsJsonObj6 = json.loads(intentsJsonStr6)
                    intentsJsonObj7 = json.loads(intentsJsonStr7)
                    intentInstall6 = intentsJsonObj6[installTime]['value']
                    intentInstall7 = intentsJsonObj7[installTime]['value']
                    intentRerouteLat6 = int(intentInstall6) - int(t0System)
                    intentRerouteLat7 = int(intentInstall7) - int(t0System)
                    intentRerouteLatPort4 =\
                            int(intentInstall4) - int(timestampBeginPtDown)
                    intentRerouteLatPort5 =\
                            int(intentInstall5) - int(timestampBeginPtDown)
                    if intentRerouteLat6 > thresholdMin and\
                            intentRerouteLat6 < thresholdMax and\
                            i > numIgnore:
                        rerouteLatSystem.append(intentRerouteLat6)
                        main.log.info('ONOS6 Intent Reroute Lat' +
                                ' size: ' + str(batchIntentSize) +
                                ' system-to-install: ' +
                                str(intentRerouteLat6) + ' ms')
                    if intentRerouteLat7 > thresholdMin and\
                            intentRerouteLat7 < thresholdMax and\
                            i > numIgnore:
                        rerouteLatSystem.append(intentRerouteLat7)
                        main.log.info('ONOS7 Intent Reroute Lat' +
                                ' size: ' + str(batchIntentSize) +
                                ' system-to-install: ' + 
                                str(intentRerouteLat7) + ' ms')
                    if intentRerouteLatPort6 > thresholdMin and\
                            intentRerouteLatPort6 < thresholdMax and\
                            i > numIgnore:
                        rerouteLatPort.append(intentRerouteLatPort6)
                        main.log.info('ONOS6 Intent Reroute Lat' +
                                ' size: ' + str(batchIntentSize) +
                                ' port-to-install: ' +
                                str(intentRerouteLatPort6) + ' ms')
                    if intentRerouteLatPort7 > thresholdMin and\
                            intentRerouteLatPort7 < thresholdMax and\
                            i > numIgnore:
                        rerouteLatPort.append(intentRerouteLatPort7)
                        main.log.info('ONOS7 Intent Reroute Lat' +
                                ' size: ' + str(batchIntentSize) +
                                ' port-to-install: ' +
                                str(intentRerouteLatPort7) + ' ms')

                time.sleep(5)
                
                main.log.info('System: ' + str(rerouteLatSystem))
                main.log.info('Port: ' + str(rerouteLatPort))
                if rerouteLatSystem:
                    maxRerouteLatSystem = max(rerouteLatSystem)
                    main.log.info('Max system: ' + str(maxRerouteLatSystem))
                if rerouteLatPort:
                    maxRerouteLatPort = max(rerouteLatPort)
                    main.log.info('Max port: ' + str(maxRerouteLatPort))
               
                # Bring port back up for next iteration
                main.Mininet1.handle.sendline('sh ifconfig ' + intfs + ' up')
                time.sleep(5)

                # Use 'withdraw' option to withdraw batch intents
                main.ONOSbench.pushTestIntentsShell(
                        deviceIdList[0] + '/2', deviceIdList[7] + '/2',
                        batchIntentSize, '/tmp/batch_install.txt',
                        ONOSIpList[0], numMult='1', report=False, options='-w')
                main.log.info('Intents removed and port back up')
             
            # NOTE: End iteration loop
            if batch == 1:
                batchIntentSize = 10
            elif batch == 2:
                batchIntentSize = 100
            elif batch == 3:
                batchIntentSize = 500
            elif batch == 4:
                batchIntentSize = 1000
            main.log.info('Batch intent size increased to ' + str(batchIntentSize))

    def CASE4(self, main):
        """
        Increase number of nodes and initiate CLI
        """
        global clusterCount
        import time
        import json
        
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        features = main.params[ 'ENV' ][ 'cellFeatures' ]
        benchIp = main.params[ 'BENCH' ][ 'ip' ]
        mininetIp = main.params[ 'TEST' ][ 'MN' ]
        
        clusterCount += 2
        main.log.report('Increasing cluster size to ' + str(clusterCount))
        
        ONOSIp = []
        for i in range( 1, 8 ):
            ONOSIp.append( main.params[ 'CTRL' ][ 'ip'+str(i) ]

        main.step( "Cleaning environment" )
        for i in range( 1, 8 ):
            main.ONOSbench.onosDie( ONOSIp[i] )
            main.log.info( "Uninstalling ONOS "+str(i) )
            main.ONOSbench.onosUninstall( ONOSIp[i] )

        main.step( "Creating new cell file" )
        cellIp = []
        for node in range( 1, clusterCount + 1 )
            cellIp.append( ONOSIp[node] )
        main.ONOSbench.createCellFile( benchIp, cellName,
                                       mininetIp, str(features), *cellIp )

        main.step( "Setting cell definition" )
        main.ONOSbench.setCell( cellName )

        main.step( "Packaging cell definition" )
        main.ONOSbench.onosPackage()

        for node in range( 1, clusterCount + 1 ):
            time.sleep(10)
            main.log.info( "Starting ONOS "+str(node) +
                            " at IP: "+ONOSIp[node] )
            main.ONOSbench.onosInstall( ONOSIp[node] )
            exec "a = main.ONOS%scli.startOnosCli" %str(node)
            a( ONOSIp[node] )

        for node in range( 1, clusterCount + 1 ):
            for i in range( 2 ):
                isup = main.ONOSbench.isup( ONOSIp[node] )
                if isup:
                    main.log.info( "ONOS "+str(node) + " is up\n")
                    assertion = main.TRUE
                    break
                if not isup:
                    main.log.info( "ONOS" + str(node) + " did not start")
        
        utilities.assert_equals(expect=main.TRUE, actual=assertion,
            onpass='Scale out to ' + str(clusterCount) + ' nodes successful',
            onfail='Scale out to ' + str(clusterCount) + ' nodes failed')

