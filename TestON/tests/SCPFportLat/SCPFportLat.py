# CASE1 starts number of nodes specified in param file
#
# cameron@onlab.us

class SCPFportLat:

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
        resultPath = main.params['DB']['portEventResultPath']
        skipMvn = main.params ['TEST']['mci']
        testONpath = re.sub( "(tests)$", "bin", main.testDir )  # TestON/bin

        # -- INIT SECTION, ONLY RUNS ONCE -- #
        if init == False:
            init = True
            global clusterCount             #number of nodes running
            global ONOSIp                   #list of ONOS IP addresses
            global scale
            global commit
            global timeToPost
            global runNum
            global jenkinsBuildNumber
            global CLIs
            CLIs = []

            timeToPost = time.strftime('%Y-%m-%d %H:%M:%S')
            runNum = time.strftime('%d%H%M%S')
            ONOSIp = main.ONOSbench.getOnosIps()

            #Assigning ONOS cli handles to a list
            for i in range(main.maxNodes):
                CLIs.append( getattr( main, 'ONOS' + str(i+1) + 'cli'))

            try:
                jenkinsBuildNumber = str(os.environ['BUILD_NUMBER'])
                main.log.report( 'Jenkins build number: ' + jenkinsBuildNumber )
            except KeyError:
                jenkinsBuildNumber = str(0)
                main.log.info( 'Job is not run by jenkins. ' + 'Build number set to: ' + jenkinsBuildNumber)

            clusterCount = 0
            ONOSIp = main.ONOSbench.getOnosIps()

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

            main.step("Grabbing commit number")
            commit = main.ONOSbench.getVersion()
            commit = (commit.split(" "))[1]

            main.step("Creating results file")
            resultsDB = open(resultPath, "w+")
            resultsDB.close()

            main.log.report('Commit information - ')
            main.ONOSbench.getVersion(report=True)

        # -- END OF INIT SECTION --#

        main.step("Adjusting scale")
        clusterCount = int(scale[0])
        scale.remove(scale[0])

        #kill off all onos processes
        main.step("Killing all ONOS processes before environmnet setup")
        for node in range(main.maxNodes):
            main.ONOSbench.onosDie(ONOSIp[node])

        #Uninstall everywhere
        main.step( "Cleaning Enviornment..." )
        for i in range(main.maxNodes):
            main.log.info(" Uninstalling ONOS " + str(i) )
            main.ONOSbench.onosUninstall( ONOSIp[i] )
        main.log.info("Sleep 10 second for uninstall to settle...")
        time.sleep(10)
        main.ONOSbench.handle.sendline(" ")
        main.ONOSbench.handle.expect(":~")

        #construct the cell file
        main.log.info("Creating cell file")
        cellIp = []
        for node in range (clusterCount):
            cellIp.append(ONOSIp[node])

        main.ONOSbench.createCellFile("localhost",cellName,MN1Ip,str(Apps), cellIp)

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
            main.log.info("Starting ONOS " + str(node) + " at IP: " + ONOSIp[node])
            main.ONOSbench.onosInstall( ONOSIp[node])

        for node in range(clusterCount):
            for i in range( 2 ):
                isup = main.ONOSbench.isup( ONOSIp[node] )
                if isup:
                    main.log.info("ONOS " + str(node + 1) + " is up\n")
                    break
            if not isup:
                main.log.report( "ONOS " + str(node) + " didn't start!" )
        main.log.info("Startup sequence complete")

        main.step('Starting onos CLIs')
        for i in range(clusterCount):
            CLIs[i].startOnosCli(ONOSIp[i])

        time.sleep(20)

        main.step( 'activating essential applications' )
        CLIs[0].activateApp( 'org.onosproject.metrics' )
        CLIs[0].activateApp( 'org.onosproject.openflow' )

        main.step( 'Configuring application parameters' )

        configName = 'org.onosproject.net.topology.impl.DefaultTopologyProvider'
        configParam = 'maxEvents 1'
        main.ONOSbench.onosCfgSet( ONOSIp[0], configName, configParam )
        configParam = 'maxBatchMs 0'
        main.ONOSbench.onosCfgSet( ONOSIp[0], configName, configParam )
        configParam = 'maxIdleMs 0'
        main.ONOSbench.onosCfgSet( ONOSIp[0], configName, configParam )

    def CASE2( self, main ):
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

        ONOSUser = main.params['CTRL']['user']
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
        localTime = time.strftime('%x %X')
        localTime = localTime.replace('/', '')
        localTime = localTime.replace(' ', '_')
        localTime = localTime.replace(':', '')

        if debugMode == 'on':
            main.ONOSbench.tsharkPcap('eth0', '/tmp/port_lat_pcap_' + localTime)

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

        main.Mininet1.assignSwController(sw='s1', ip=ONOSIp[0])
        main.Mininet1.assignSwController(sw='s2', ip=ONOSIp[0])

        time.sleep(15)

        portUpEndToEndNodeIter = numpy.zeros((clusterCount, int(numIter)))
        portUpOfpToDevNodeIter = numpy.zeros((clusterCount, int(numIter)))
        portUpDevToLinkNodeIter = numpy.zeros((clusterCount, int(numIter)))
        portUpLinkToGraphNodeIter = numpy.zeros((clusterCount, int(numIter)))

        portDownEndToEndNodeIter = numpy.zeros((clusterCount, int(numIter)))
        portDownOfpToDevNodeIter = numpy.zeros((clusterCount, int(numIter)))
        portDownDevToLinkNodeIter = numpy.zeros((clusterCount, int(numIter)))
        portDownLinkToGraphNodeIter = numpy.zeros((clusterCount, int(numIter)))

        for i in range(0, int(numIter)):
            main.log.report('Iteration: ' + str(i+1) + ' ClusterCount: ' + str(clusterCount))
            main.step('Starting wireshark capture for port status down')
            main.ONOSbench.tsharkGrep(tsharkPortStatus, tsharkPortDown)

            time.sleep(2)

            main.step('Disable port: ' + interfaceConfig)
            main.Mininet1.handle.sendline('sh ifconfig ' +
                    interfaceConfig + ' down')
            main.Mininet1.handle.expect('mininet>')

            time.sleep(2)

            jsonStrPtDown = []
            for node in range (0, clusterCount):
                metricsPortDown = CLIs[node].topologyEventsMetrics()
                jsonStrPtDown.append(metricsPortDown)

            time.sleep(10)

            main.ONOSbench.tsharkStop()

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
            else:
                main.log.info('Tshark output file returned unexpected' +
                        ' results: ' + str(objDown))
                timestampBeginPtDown = 0
            fPortDown.close()

            for node in range(0, clusterCount):
                nodeNum = node+1
                metricsDown = CLIs[node].topologyEventsMetrics
                jsonStrPtDown[node] = metricsDown()
                jsonObj = json.loads(jsonStrPtDown[node])

                if jsonObj:
                    graphTimestamp = jsonObj[graphTimestampKey]['value']
                    deviceTimestamp = jsonObj[deviceTimestampKey]['value']
                    linkTimestamp = jsonObj[linkTimestampKey]['value']
                else:
                    main.log.error( "Unexpected json object" )
                    graphTimestamp = 0
                    deviceTimestamp = 0
                    linkTimestamp = 0

                main.log.info('ptDownTimestamp: ' + str(timestampBeginPtDown))
                main.log.info("graphTimestamp: " + str(graphTimestamp))
                main.log.info("deviceTimestamp: " + str(deviceTimestamp))
                main.log.info("linkTimestamp: " + str(linkTimestamp))

                ptDownEndToEnd = int(graphTimestamp) - int(timestampBeginPtDown)
                ptDownOfpToDevice = float(deviceTimestamp) - float(timestampBeginPtDown)
                ptDownDeviceToLink = float(linkTimestamp) - float(deviceTimestamp)
                ptDownLinkToGraph = float(graphTimestamp) - float(linkTimestamp)

                if ptDownEndToEnd < downThresholdMin or ptDownEndToEnd >= downThresholdMax:
                    main.log.info("ONOS " +str(nodeNum) + " surpassed threshold - port down End-to-end: "+ str(ptDownEndToEnd) + " ms")
                elif i < iterIgnore:
                    main.log.info("ONOS "+str(nodeNum) + " warming up - port down End-to-end: "+ str(ptDownEndToEnd) + " ms")
                else:
                    portDownEndToEndNodeIter[node][i] = ptDownEndToEnd
                    main.log.info("ONOS "+str(nodeNum) + " port down End-to-end: "+ str(ptDownEndToEnd) + " ms")

                if ptDownOfpToDevice < downThresholdMin or ptDownOfpToDevice >= downThresholdMax:
                    main.log.info("ONOS " +str(nodeNum) + " surpassed threshold - port down Ofp-to-device: "+ str(ptDownOfpToDevice) + " ms")
                elif i < iterIgnore:
                    main.log.info("ONOS "+str(nodeNum) + " warming up - port down Ofp-to-device: "+ str(ptDownOfpToDevice) + " ms")
                else:
                    portDownOfpToDevNodeIter[node][i] = ptDownOfpToDevice
                    main.log.info("ONOS "+str(nodeNum) + " port down Ofp-to-device: "+ str(ptDownOfpToDevice) + " ms")

                if ptDownDeviceToLink < downThresholdMin or ptDownDeviceToLink >= downThresholdMax:
                    main.log.info("ONOS " +str(nodeNum) + " surpassed threshold - port down Device-to-link: "+ str(ptDownDeviceToLink) + " ms")
                elif i < iterIgnore:
                    main.log.info("ONOS "+str(nodeNum) + " warming up - port down Device-to-link: "+ str(ptDownDeviceToLink) + " ms")
                else:
                    portDownDevToLinkNodeIter[node][i] = ptDownDeviceToLink
                    main.log.info("ONOS "+str(nodeNum) + " port down Device-to-link: "+ str(ptDownDeviceToLink) + " ms")

                if ptDownLinkToGraph < downThresholdMin or ptDownLinkToGraph >= downThresholdMax:
                    main.log.info("ONOS " +str(nodeNum) + " surpassed threshold - port down Link-to-graph: "+ str(ptDownLinkToGraph) + " ms")
                elif i < iterIgnore:
                    main.log.info("ONOS "+str(nodeNum) + " warming up - port down Link-to-graph: "+ str(ptDownLinkToGraph) + " ms")
                else:
                    portDownLinkToGraphNodeIter[node][i] = ptDownLinkToGraph
                    main.log.info("ONOS "+str(nodeNum) + " port down Link-to-graph: "+ str(ptDownLinkToGraph) + " ms")

            time.sleep(3)

            main.step('Starting wireshark capture for port status up')
            main.ONOSbench.tsharkGrep(tsharkPortStatus, tsharkPortUp)

            time.sleep(5)
            main.step('Enable port and obtain timestamp')
            main.Mininet1.handle.sendline('sh ifconfig ' + interfaceConfig + ' up')
            main.Mininet1.handle.expect('mininet>')

            time.sleep(5)

            jsonStrPtUp = []
            for node in range (0, clusterCount):
                metricsPortUp = CLIs[node].topologyEventsMetrics()
                jsonStrPtUp.append(metricsPortUp)

            time.sleep(5)
            main.ONOSbench.tsharkStop()

            time.sleep(3)

            fPortUp = open(tsharkPortUp, 'r')
            fLine = fPortUp.readline()
            objUp = fLine.split(' ')
            if len(fLine) > 0:
                timestampBeginPtUp = int(float(objUp[1]) * 1000)
                if timestampBeginPtUp < 1400000000000:
                    timestampBeginPtUp = int(float(objUp[2]) * 1000)
            else:
                main.log.info('Tshark output file returned unexpected' + ' results.')
                timestampBeginPtUp = 0
            fPortUp.close()

            for node in range(0, clusterCount):
                nodeNum = node+1
                metricsUp = CLIs[node].topologyEventsMetrics
                jsonStrUp = metricsUp()
                jsonObj = json.loads(jsonStrPtUp[node])

                if jsonObj:
                    graphTimestamp = jsonObj[graphTimestampKey]['value']
                    deviceTimestamp = jsonObj[deviceTimestampKey]['value']
                    linkTimestamp = jsonObj[linkTimestampKey]['value']
                else:
                    main.log.error( "Unexpected json object" )
                    graphTimestamp = 0
                    deviceTimestamp = 0
                    linkTimestamp = 0


                main.log.info('ptUpTimestamp: ' + str(timestampBeginPtUp))
                main.log.info("graphTimestamp: " + str(graphTimestamp))
                main.log.info("deviceTimestamp: " + str(deviceTimestamp))
                main.log.info("linkTimestamp: " + str(linkTimestamp))

                ptUpEndToEnd = int(graphTimestamp) - int(timestampBeginPtUp)
                ptUpOfpToDevice = float(deviceTimestamp) - float(timestampBeginPtUp)
                ptUpDeviceToLink = float(linkTimestamp) - float(deviceTimestamp)
                ptUpLinkToGraph = float(graphTimestamp) - float(linkTimestamp)

                if ptUpEndToEnd < upThresholdMin or ptUpEndToEnd >= upThresholdMax:
                    main.log.info("ONOS " +str(nodeNum) + " surpassed threshold - port up End-to-end: "+ str(ptUpEndToEnd) + " ms")
                elif i < iterIgnore:
                    main.log.info("ONOS "+str(nodeNum) + " warming up - port up End-to-end: "+ str(ptUpEndToEnd) + " ms")
                else:
                    portUpEndToEndNodeIter[node][i] = ptUpEndToEnd
                    main.log.info("ONOS "+str(nodeNum) + " port up End-to-end: "+ str(ptUpEndToEnd) + " ms")

                if ptUpOfpToDevice < upThresholdMin or ptUpOfpToDevice >= upThresholdMax:
                    main.log.info("ONOS " + str(nodeNum) + " surpassed threshold - port up Ofp-to-device: "+ str(ptUpOfpToDevice) + " ms")
                elif i < iterIgnore:
                    main.log.info("ONOS "+ str(nodeNum) + " warming up - port up Ofp-to-device: "+ str(ptUpOfpToDevice) + " ms")
                else:
                    portUpOfpToDevNodeIter[node][i] = ptUpOfpToDevice
                    main.log.info("ONOS "+ str(nodeNum) + " port up Ofp-to-device: "+ str(ptUpOfpToDevice) + " ms")

                if ptUpDeviceToLink < upThresholdMin or ptUpDeviceToLink >= upThresholdMax:
                    main.log.info("ONOS " +str(nodeNum) + " surpassed threshold - port up Device-to-link: "+ str(ptUpDeviceToLink) + " ms")
                elif i < iterIgnore:
                    main.log.info("ONOS "+str(nodeNum) + " warming up - port up Device-to-link: "+ str(ptUpDeviceToLink) + " ms")
                else:
                    portUpDevToLinkNodeIter[node][i] = ptUpDeviceToLink
                    main.log.info("ONOS "+str(nodeNum) + " port up Device-to-link: "+ str(ptUpDeviceToLink) + " ms")

                if ptUpLinkToGraph < upThresholdMin or ptUpLinkToGraph >= upThresholdMax:
                    main.log.info("ONOS " + str(nodeNum) + " surpassed threshold - port up Link-to-graph: " + str(ptUpLinkToGraph) + " ms")
                elif i < iterIgnore:
                    main.log.info("ONOS " + str(nodeNum) + " warming up - port up Link-to-graph: " + str(ptUpLinkToGraph) + " ms")
                else:
                    portUpLinkToGraphNodeIter[node][i] = ptUpLinkToGraph
                    main.log.info("ONOS " + str(nodeNum) + " port up Link-to-graph: " + str(ptUpLinkToGraph) + " ms")

        dbCmdList = []
        for node in range(0, clusterCount):
            portUpEndToEndList = []
            portUpOfpToDevList = []
            portUpDevToLinkList = []
            portUpLinkToGraphList = []

            portDownEndToEndList = []
            portDownOfpToDevList = []
            portDownDevToLinkList = []
            portDownLinkToGraphList = []

            portUpEndToEndAvg = 0
            portUpOfpToDevAvg = 0
            portUpDevToLinkAvg = 0
            portUpLinkToGraphAvg = 0

            portDownEndToEndAvg = 0
            portDownOfpToDevAvg = 0
            portDownDevToLinkAvg = 0
            portDownLinkToGraphAvg = 0

            # TODO: Update for more pythonic way to get list
            # portUpDevList = [item for item in portUpDevNodeIter[node]
            #        if item > 0.0]
            for item in portUpEndToEndNodeIter[node]:
                if item > 0.0:
                    portUpEndToEndList.append(item)

            for item in portUpOfpToDevNodeIter[node]:
                if item > 0.0:
                    portUpOfpToDevList.append(item)

            for item in portUpDevToLinkNodeIter[node]:
                if item > 0.0:
                    portUpDevToLinkList.append(item)

            for item in portUpLinkToGraphNodeIter[node]:
                if item >= 0.0:
                    portUpLinkToGraphList.append(item)

            for item in portDownEndToEndNodeIter[node]:
                if item > 0.0:
                    portDownEndToEndList.append(item)

            for item in portDownOfpToDevNodeIter[node]:
                if item > 0.0:
                    portDownOfpToDevList.append(item)

            for item in portDownDevToLinkNodeIter[node]:
                if item >= 0.0:
                    portDownDevToLinkList.append(item)

            for item in portDownLinkToGraphNodeIter[node]:
                if item >= 0.0:
                    portDownLinkToGraphList.append(item)

            portUpEndToEndAvg = round(numpy.mean(portUpEndToEndList), 2)
            portUpOfpToDevAvg = round(numpy.mean(portUpOfpToDevList), 2)
            portUpDevToLinkAvg = round(numpy.mean(portUpDevToLinkList), 2)
            portUpLinkToGraphAvg = round(numpy.mean(portUpLinkToGraphList), 2)

            portDownEndToEndAvg = round(numpy.mean(portDownEndToEndList), 2)
            portDownOfpToDevAvg = round(numpy.mean(portDownOfpToDevList), 2)
            portDownDevToLinkAvg = round(numpy.mean(portDownDevToLinkList), 2)
            portDownLinkToGraphAvg = round(numpy.mean(portDownLinkToGraphList), 2)

            portUpStdDev = round(numpy.std(portUpEndToEndList), 2)
            portDownStdDev = round(numpy.std(portDownEndToEndList), 2)

            main.log.report(' - Node ' + str(node + 1) + ' Summary ---------------- ')
            main.log.report(' Port up End-to-end ' +
                    str(portUpEndToEndAvg) + ' ms')
            main.log.report(' Port up Ofp-to-device ' +
                    str(portUpOfpToDevAvg) + ' ms')
            main.log.report(' Port up Device-to-link ' +
                    str(portUpDevToLinkAvg) + ' ms')
            main.log.report(' Port up Link-to-graph ' +
                    str(portUpLinkToGraphAvg) + ' ms')

            main.log.report(' Port down End-to-end ' +
                    str(round(portDownEndToEndAvg, 2)) + ' ms')
            main.log.report(' Port down Ofp-to-device ' +
                    str(portDownOfpToDevAvg) + ' ms')
            main.log.report(' Port down Device-to-link ' +
                    str(portDownDevToLinkAvg) + ' ms')
            main.log.report(' Port down Link-to-graph' +
                    str(portDownLinkToGraphAvg) + ' ms')

            dbCmdList.append(
                    "'" + timeToPost + "','port_latency_results'," + jenkinsBuildNumber +
                    ',' + str(clusterCount) + ",'baremetal" + str(node + 1) +
                    "'," +
                    str(portUpEndToEndAvg) +',' +
                    str(portUpOfpToDevAvg) + ',' +
                    str(portUpDevToLinkAvg) + ',' +
                    str(portUpLinkToGraphAvg) + ',' +
                    str(portDownEndToEndAvg) + ',' +
                    str(portDownOfpToDevAvg) + ',' +
                    str(portDownDevToLinkAvg) + ',' +
                    str(portDownLinkToGraphAvg))

        fResult = open(resultPath, 'a')
        for line in dbCmdList:
            if line:
                fResult.write(line + '\n')

        fResult.close()

        # Delete switches from controller to prepare for next
        # set of tests
        main.Mininet1.deleteSwController('s1')
        main.Mininet1.deleteSwController('s2')

        main.log.info("Stopping mininet")
        main.Mininet1.stopNet()
