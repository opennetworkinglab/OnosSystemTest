# ScaleOutTemplate - IntentReroute 
#
# CASE1 starts number of nodes specified in param file
#
# cameron@onlab.us

import sys
import os.path


class IntentReroute:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):            #This is the initialization case
                                        #this case will clean up all nodes 
        import time                     #but only node 1 is started in this case
        import os.path

        global clusterCount             #number of nodes running
        global ONOSIp                   #list of ONOS IP addresses 
        clusterCount = 1
        ONOSIp = [ 0 ]


        #Load values from params file
        checkoutBranch = main.params[ 'GIT' ][ 'checkout' ]
        gitPull = main.params[ 'GIT' ][ 'autopull' ]
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        Features= main.params[ 'ENV' ][ 'cellFeatures' ]
        BENCHIp = main.params[ 'BENCH' ][ 'ip1' ]
        BENCHUser = main.params[ 'BENCH' ][ 'user' ]
        MN1Ip = main.params[ 'MN' ][ 'ip1' ]
        maxNodes = int(main.params[ 'availableNodes' ])
        Features = main.params[ 'ENV' ][ 'cellFeatures' ]
        skipMvn = main.params[ 'TEST' ][ 'skipCleanInstall' ]
        switchCount = (main.params[ 'ENV' ][ 'scale1switches' ]).split(",")
        homeDir = os.path.expanduser('~')

        #Populate ONOSIp with ips from params 
        for i in range(1, maxNodes + 1): 
            ipString = 'ip' + str(i) 
            ONOSIp.append(main.params[ 'CTRL' ][ ipString ])   
    
        tempIp = []
        for node in range( 1, clusterCount + 1):
            tempIp.append(ONOSIp[node])

        #kill off all onos processes 
        main.log.step("Safety check, killing all ONOS processes")
        main.log.step("before initiating enviornment setup")
        for node in range(1, maxNodes + 1):
            main.ONOSbench.onosDie(ONOSIp[node])

        #construct the cell file
        main.log.info("Creating cell file")
        exec "a = main.ONOSbench.createCellFile"
        cellIp = []
        for node in range (1, clusterCount + 1):
            cellIp.append(ONOSIp[node])
        a(BENCHIp,cellName,MN1Ip,str(Features), *cellIp)

        main.step( "Applying cell file to environment" )
        cellApplyResult = main.ONOSbench.setCell( cellName )

        #Uninstall everywhere
        main.log.step( "Cleaning Enviornment..." )
        for i in range(1, maxNodes + 1):
            main.log.info(" Uninstalling ONOS " + str(i) )
            main.ONOSbench.onosUninstall( ONOSIp[i] )
        
        #mvn clean install, for debugging set param 'skipCleanInstall' to yes to speed up test
        if skipMvn != "yes":
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
        
        main.ONOSbench.handle.sendline("cp ~/ONLabTest/TestON/dependencies/IntentRerouteTest/oneNode7linear.cfg ~/onos/tools/package/etc/")
        main.ONOSbench.handle.expect(":~")
        main.ONOSbench.handle.sendline("cp ~/ONLabTest/TestON/dependencies/IntentRerouteTest/oneNode7linearCut.cfg ~/onos/tools/package/etc/")
        main.ONOSbench.handle.expect(":~")

        main.ONOSbench.createNullDevProviderFile(BENCHIp, tempIp, switchCount)
        main.ONOSbench.createNullLinkProviderFile(BENCHIp, fileName=("/opt/onos/apache-karaf-3.0.2/etc/oneNode7linear.cfg"))
 
        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()  

        main.step( "Installing ONOS package" )
        install1Result = main.ONOSbench.onosInstall( node=ONOSIp[1] )

        main.step( "verify cells" )
        verifyCellResult = main.ONOSbench.verifyCell()

        main.step( "Set cell for ONOS cli env" )
        cli1 = main.ONOS1cli.startOnosCli( ONOSIp[1] )

        
    def CASE2( self, main ):
        # This case increases the cluster size by whatever scale is
        # Note: 'scale' is the size of the step
        # if scaling is not a part of your test, simply run this case
        # once after CASE1 to set up your enviornment for your desired 
        # cluster size. If scaling is a part of you test call this case each time 
        # you want to increase cluster size

        ''                                                         
        'Increase number of nodes and initiate CLI'
        ''
        import time
        global clusterCount
        
        BENCHIp = main.params[ 'BENCH' ][ 'ip1' ]
        scale = int( main.params[ 'SCALE' ] )
        clusterCount += scale
        homeDir = os.path.expanduser('~')
        switchParams = ("scale" + str(clusterCount) + "switches")
        switchCount = (main.params[ 'ENV' ][ switchParams ]).split(",") 

        if clusterCount == 1: 
            temp = "one"
        if clusterCount == 3: 
            temp = "three"
        if clusterCount == 5: 
            temp = "five"
        if clusterCount == 7: 
            temp = "seven"

        lgfile = temp + "Node7linear.cfg"
        main.ONOSbench.handle.sendline("cp ~/ONLabTest/TestON/dependencies/IntentRerouteTest/" + lgfile + " ~/onos/tools/package/etc/")
        main.ONOSbench.handle.expect(":~")
        main.ONOSbench.handle.sendline("cp ~/ONLabTest/TestON/dependencies/IntentRerouteTest/" + temp + "Node7linearCut.cfg" + " ~/onos/tools/package/etc/")
        main.ONOSbench.handle.expect(":~")
        
        main.log.info("Creating cell file")
        exec "a = main.ONOSbench.createCellFile"
        cellIp = []
        for node in range (1, clusterCount + 1):
            cellIp.append(ONOSIp[node])
        a(BENCHIp,cellName,MN1Ip,str(Features), *cellIp) 
    
        main.step( "Applying cell file to environment" )
        cellApplyResult = main.ONOSbench.setCell( cellName )

        #Uninstall everywhere
        main.log.step( "Cleaning Enviornment..." )
        for node in range(1, maxNodes + 1):
            main.ONOSbench.onosDie(ONOSIp[node])
            main.log.info(" Uninstalling ONOS " + str(node) )
            main.ONOSbench.onosUninstall( ONOSIp[node] )

        tempIp = []
        for node in range( 1, clusterCount + 1): 
            tempIp.append(ONOSIp[node]) 

        main.ONOSbench.createNullDevProviderFile(BENCHIp, tempIp, switchCount)
        main.ONOSbench.createNullLinkProviderFile(BENCHIp, fileName=("/opt/onos/apache-karaf-3.0.2/etc/" + lgfile))

        main.ONOSbench.onosPackage()
        
        
        main.log.report( "Increasing cluster size to " + str( clusterCount ) )
        for node in range(1, clusterCount + 1):
            main.log.info("Starting ONOS " + str(node) + " at IP: " + ONOSIp[node])    
            main.ONOSbench.onosInstall( node=ONOSIp[node])
            if node == 1: 
                main.ONOS1cli.startOnosCli( ONOSIp[1] )
        
        for node in range(1, clusterCount + 1): 
            for i in range( 2 ):
                isup = main.ONOSbench.isup( ONOSIp[node] )
                if isup:
                    main.log.info("ONOS " + str(node) + " is up\n")
                    break
            if not isup:
                main.log.report( "ONOS " + str(node) + " didn't start!" ) 
    
    def CASE3( self, main ): 

        import time 
        import numpy 
        import datetime
        #from scipy import stats

        ts = time.time()
        date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')

        sampleSize = int(main.params[ 'TEST' ][ 'sampleSize' ]) 
        warmUp = int(main.params[ 'TEST' ][ 'warmUp' ])
        intentsList = (main.params[ 'TEST' ][ 'intents' ]).split(",")
        debug = main.params[ 'TEST' ][ 'debug' ]
        for i in range(0,len(intentsList)):
            intentsList[i] = int(intentsList[i]) 
        
        timestampMetrics = []
        if main.params['METRICS']['Submitted'] == "1":
            timestampMetrics.append("Submitted")
        if main.params['METRICS']['Installed'] == "1": 
            timestampMetrics.append("Installed")
        if main.params['METRICS']['Failed'] == "1":
            timestampMetrics.append("Failed")    
        if main.params['METRICS']['Withdraw'] == "1":
            timestampMetrics.append("Withdraw")
        if main.params['METRICS']['Withdrawn'] == "1":
            timestampMetrics.append("Withdrawn")
        if debug: main.log.info(timestampMetrics) 
    
        if debug == "True": 
            debug = True
        else: 
            debug = False

        if clusterCount == 1:
            temp = "one"
        if clusterCount == 3:
            temp = "three"
        if clusterCount == 5:
            temp = "five"
        if clusterCount == 7:
            temp = "seven"

        lgfile = temp + "Node7linear.cfg"
        lgfileCut = temp + "Node7linearCut.cfg"
        linkCount = 0

        for i in range(0,15):
            main.ONOSbench.handle.sendline("onos $OC1 links|wc -l")
            main.ONOSbench.handle.expect(":~")
            linkCount = main.ONOSbench.handle.before
            if debug: main.log.info("Link Count check: " + linkCount)
            if str(16) in linkCount:
                break
            time.sleep(3)
            main.log.info("waiting for links")

        links = "--"
        while "=null:" not in links:
            if debug: main.log.info("top of loop")
            main.ONOSbench.handle.sendline("onos $OC1 links")
            main.ONOSbench.handle.expect(":~")
            links = main.ONOSbench.handle.before
            if debug: main.log.info(str(links))
            time.sleep(1)
        links = links.splitlines()
        templinks = links

        tempDevices = []
        for line in links:
            temp = line.split(" ")
            temp[0].replace("src=","")
            temp[0] = (temp[0].split("/"))[0]
            tempDevices.append(temp[0])

        tempDevices.sort()
        devices = []
        for i in tempDevices:
            if "src=null" in i:
                devices.append(i.replace("src=", ""))
        if debug: main.log.info(str(devices))

        ingress = devices[0]
        egress = devices.pop()
        if debug: main.log.info("ingress: " + ingress)
        if debug: main.log.info("egress: " + egress)


        for intents in intentsList:
            main.log.report("Intent Batch size: " + str(intents) + "\n      ") 
            myResult = [["latency", "lastNode"] for x in range(sampleSize)]
            
            for run in range(0, (warmUp + sampleSize)):
                if run > warmUp: 
                    main.log.info("Starting test iteration " + str(run-warmUp)) 

                cmd = """onos $OC1 "push-test-intents -i """
                cmd += ingress + "/0 "
                cmd += egress + "/0 "
                cmd += str(intents) +""" 1" """
                if debug: main.log.info(cmd)

                withdrawCmd = cmd.replace("intents -i", "intents -w ")
                 
                #push-test-intents 
                main.ONOSbench.handle.sendline(cmd)
                main.ONOSbench.handle.expect(":~")
                myRawResult = main.ONOSbench.handle.before
              
                for i in range(0, 40):
                    main.ONOSbench.handle.sendline("onos $OC1 summary")
                    main.ONOSbench.handle.expect(":~")
                    linkCheck = main.ONOSbench.handle.before
                    if ("flows=" + str(8*intents) + ",") in linkCheck:
                        break
                    if i == 39:
                        main.log.error("Flow count incorrect, data invalid.")

                #cut link
                nodesLinksCut = []
                if clusterCount == 1: 
                    nodesLinksCut.append(1)
                if clusterCount == 3 or clusterCount == 5:
                    nodesLinksCut.append(2)
                if clusterCount == 7:
                    nodesLinksCut.append(3)
                    nodesLinksCut.append(4)

                for node in nodesLinksCut:
                    exec "a = main.ONOS%s.createNullLinkProviderFile" %str(node)
                    a(ONOSIp[node], fileName=("/opt/onos/apache-karaf-3.0.2/etc/" + lgfileCut), onNode=True)

                #collect timestamp from link cut 
                cmd = "onos-ssh $OC" + str(nodesLinksCut[len(nodesLinksCut)-1]) + " cat /opt/onos/log/karaf.log | grep " + lgfileCut + "| tail -1" 
                if debug: main.log.info("COMMAND: " + str(cmd))
                
                for i in range(0,10):
                    main.ONOSbench.handle.sendline(cmd)
                    main.ONOSbench.handle.expect(":~")
                    raw = main.ONOSbench.handle.before
                    if "NullLinkProvider" in raw:
                        break
                    if i >= 9:
                        main.log.error("Expected output not being recieved... continuing")
                        main.log.info(raw)
                        break
                    time.sleep(2) 

                temp = raw.splitlines()
                for line in temp: 
                    if str(date) in line: 
                        temp = line 
                        break

                cutTimestamp = (temp.split(" "))[0] + " " + (temp.split(" "))[1]

                #validate link count and flow count
                for i in range(0, 40):
                    main.ONOSbench.handle.sendline("onos $OC1 summary")
                    main.ONOSbench.handle.expect(":~")
                    linkCheck = main.ONOSbench.handle.before
                    if "links=14," in linkCheck and ("flows=" + str(7*intents) + ",") in linkCheck:
                        break
                    if i == 39:
                        main.log.error("Link or flow count incorrect, data invalid.")

                #intents events metrics installed timestamp 
                IEMtimestamps = [0]*(clusterCount + 1)
                installedTemp = [0]*(clusterCount + 1)
                for node in range(1, clusterCount +1):      
                    cmd = "onos $OC" + str(node) + " intents-events-metrics|grep Timestamp"
                    raw = ""
                    while "Timestamp" not in raw:
                        main.ONOSbench.handle.sendline(cmd)
                        main.ONOSbench.handle.expect(":~")
                        raw = main.ONOSbench.handle.before 

                    intentsTimestamps = {}
                    rawTimestamps = raw.splitlines()
                    for line in rawTimestamps: 
                        if "Timestamp" in line and "grep" not in line: 
                            metricKey = (line.split(" "))[1]
                            metricTimestamp = (line.split(" ")[len(line.split(" ")) -1]).replace("epoch)=","")
                            metricTimestamp = float(metricTimestamp)
                            metricTimestamp = numpy.divide(metricTimestamp, 1000)
                            if debug: main.log.info(repr(metricTimestamp))
                            intentsTimestamps[metricKey] = metricTimestamp
                            if metricKey == "Installed":
                                installedTemp[node] = metricTimestamp 

                    main.log.info("Node: " + str(node) + " Timestamps: " + str(intentsTimestamps))
                    IEMtimestamps[node] = intentsTimestamps
              
                myMax = max(installedTemp)
                indexOfMax = installedTemp.index(myMax)

                #number crunch
                for metric in timestampMetrics:     #this is where we sould add support for computing other timestamp metrics
                    if metric == "Installed":
                        if run >= warmUp: 
                            main.log.report("link cut timestamp: " + cutTimestamp)
                            #readableInstalledTimestamp = str(intentsTimestamps["Installed"])
                            readableInstalledTimestamp = str(myMax)

                            #main.log.report("Intent Installed timestamp: " + str(intentsTimestamps["Installed"]))          
                            main.log.report("Intent Installed timestamp: " + str(myMax))

                            cutEpoch = time.mktime(time.strptime(cutTimestamp, "%Y-%m-%d %H:%M:%S,%f"))
                            if debug: main.log.info("cutEpoch=" + str(cutEpoch))
                            #rerouteLatency = float(intentsTimestamps["Installed"] - cutEpoch)
                            rerouteLatency = float(myMax - cutEpoch)

                            rerouteLatency = numpy.divide(rerouteLatency, 1000)
                            main.log.report("Reroute latency:" + str(rerouteLatency) + " (seconds)\n    ") 
                            myResult[run-warmUp][0] = rerouteLatency
                            myResult[run-warmUp][1] = indexOfMax
                            if debug: main.log.info("Latency: " + str(myResult[run-warmUp][0])) 
                            if debug: main.log.info("last node: " + str(myResult[run-warmUp][1]))  

                #time.sleep(12)

                #reset
                for node in nodesLinksCut:
                    exec "a = main.ONOS%s.createNullLinkProviderFile" %str(node)
                    a(ONOSIp[node], fileName=("/opt/onos/apache-karaf-3.0.2/etc/" + lgfile), onNode=True)

                #wait for intent withdraw
                if debug: main.log.info(withdrawCmd)
                main.ONOSbench.handle.sendline(withdrawCmd)
                main.ONOSbench.handle.expect(":~")
                main.ONOSbench.handle.sendline("onos $OC1 intents|grep WITHDRAWN|wc -l")
                main.ONOSbench.handle.expect(":~")
                intentWithdrawCheck = main.ONOSbench.handle.before
                if (str(intents)) in intentWithdrawCheck: 
                    main.log.info("intents withdrawn")
                if debug: main.log.info(intentWithdrawCheck)
                
                # wait for links to be reestablished  
                for i in range(0, 10): 
                    main.ONOSbench.handle.sendline("onos $OC1 summary")
                    main.ONOSbench.handle.expect(":~") 
                    linkCheck = main.ONOSbench.handle.before
                    if "links=16," in linkCheck:
                        break
                    time.sleep(1)
                    if i == 9: 
                        main.log.info("Links Failed to reconnect, next iteration of data invalid.") 

                if run < warmUp: 
                    main.log.info("Warm up run " + str(run+1) + " completed") 
            
            if debug: main.log.info(myResult)
            latTemp = []
            nodeTemp = []
            for i in myResult: 
                latTemp.append(i[0])
                nodeTemp.append(i[1])

            mode = {}
            for i in nodeTemp: 
                if i in mode: 
                    mode[i] += 1
                else: 
                    mode[i] = 1

            for i in mode.keys():
                if mode[i] == max(mode.values()):
                    nodeMode = i 
            
            average = numpy.average(latTemp)
            stdDev = numpy.std(latTemp) 

            main.log.report("Scale: " + str(clusterCount) + "  \tIntent batch: " + str(intents))
            main.log.report("Latency average:................" + str(average)) 
            main.log.report("Latency standard deviation:....." + str(stdDev))
            main.log.report("Mode of last node to respond:..." + str(nodeMode))
            main.log.report("________________________________________________________")


             
