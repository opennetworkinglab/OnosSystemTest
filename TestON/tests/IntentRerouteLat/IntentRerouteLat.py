# ScaleOutTemplate
#
# CASE1 starts number of nodes specified in param file
#
# cameron@onlab.us

import sys
import os.path


class IntentRerouteLat:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):           
                                        
        import time                     
        global init       
        try: 
            if type(init) is not bool: 
                init = False  
        except NameError: 
            init = False 
       
        #Load values from params file
        checkoutBranch = main.params[ 'GIT' ][ 'checkout' ]
        gitPull = main.params[ 'GIT' ][ 'autopull' ]
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        Apps = main.params[ 'ENV' ][ 'cellApps' ]
        BENCHIp = main.params[ 'BENCH' ][ 'ip1' ]
        BENCHUser = main.params[ 'BENCH' ][ 'user' ]
        MN1Ip = main.params[ 'MN' ][ 'ip1' ]
        maxNodes = int(main.params[ 'availableNodes' ])
        skipMvn = main.params[ 'TEST' ][ 'skipCleanInstall' ]
        cellName = main.params[ 'ENV' ][ 'cellName' ]        

        # -- INIT SECTION, ONLY RUNS ONCE -- # 
        if init == False: 
            init = True
            global clusterCount             #number of nodes running
            global ONOSIp                   #list of ONOS IP addresses
            global scale 
            global commit

            clusterCount = 0
            ONOSIp = [ 0 ]
            scale = (main.params[ 'SCALE' ]).split(",")            
            clusterCount = int(scale[0])

            #Populate ONOSIp with ips from params 
            for i in range(1, maxNodes + 1): 
                ipString = 'ip' + str(i) 
                ONOSIp.append(main.params[ 'CTRL' ][ ipString ])   
            
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
            
            commit = main.ONOSbench.getVersion()
            commit = (commit.split(" "))[1]

            resultsDB = open("IntentRerouteLatDB", "w+")
            resultsDB.close()

        # -- END OF INIT SECTION --#
         
        clusterCount = int(scale[0])
        scale.remove(scale[0])       
       
        switchParams = ("scale" + str(clusterCount) + "switches")
        switchCount = (main.params[ 'ENV' ][ switchParams ]).split(",")

        #kill off all onos processes 
        main.log.step("Safety check, killing all ONOS processes")
        main.log.step("before initiating enviornment setup")
        for node in range(1, maxNodes + 1):
            main.ONOSbench.onosDie(ONOSIp[node])
        
        #Uninstall everywhere
        main.log.step( "Cleaning Enviornment..." )
        for i in range(1, maxNodes + 1):
            main.log.info(" Uninstalling ONOS " + str(i) )
            main.ONOSbench.onosUninstall( ONOSIp[i] )
       
        #construct the cell file
        main.log.info("Creating cell file")
        cellIp = []
        for node in range (1, clusterCount + 1):
            cellIp.append(ONOSIp[node])

        main.ONOSbench.createCellFile(BENCHIp,cellName,MN1Ip,str(Apps), *cellIp)

        main.step( "Set Cell" )
        main.ONOSbench.setCell(cellName)
        
        if clusterCount == 1:
            temp = "one"
        if clusterCount == 3:
            temp = "three"
        if clusterCount == 5:
            temp = "five"
        if clusterCount == 7:
            temp = "seven"

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()  

        main.step( "verify cells" )
        verifyCellResult = main.ONOSbench.verifyCell()
      
        main.log.report( "Initializing " + str( clusterCount ) + " node cluster." )
        for node in range(1, clusterCount + 1):
            main.log.info("Starting ONOS " + str(node) + " at IP: " + ONOSIp[node])
            main.ONOSbench.onosInstall( ONOSIp[node])

        for node in range(1, clusterCount + 1):
            for i in range( 2 ):
                isup = main.ONOSbench.isup( ONOSIp[node] )
                if isup:
                    main.log.info("ONOS " + str(node) + " is up\n")
                    break
            if not isup:
                main.log.report( "ONOS " + str(node) + " didn't start!" )
        main.log.info("Startup sequence complete")
     
        main.ONOSbench.handle.sendline("""onos $OC1 "cfg set org.onosproject.provider.nil.NullProviders deviceCount 8 " """)
        main.ONOSbench.handle.expect(":~")
        print repr(main.ONOSbench.handle.before)
        time.sleep(3)
        main.ONOSbench.handle.sendline("""onos $OC1 "cfg set org.onosproject.provider.nil.NullProviders topoShape reroute" """)
        main.ONOSbench.handle.expect(":~")
        print repr(main.ONOSbench.handle.before)
        time.sleep(3)
        main.ONOSbench.handle.sendline("""onos $OC1 "cfg set org.onosproject.provider.nil.NullProviders enabled true" """)
        main.ONOSbench.handle.expect(":~")
        print repr(main.ONOSbench.handle.before) 

        while True: 
            main.ONOSbench.handle.sendline("onos $OC1 summary")
            main.ONOSbench.handle.expect(":~")
            x = main.ONOSbench.handle.before
            if "devices=8" in x:
                break
            else:   
                main.ONOSbench.handle.sendline("""onos $OC1 "cfg set org.onosproject.provider.nil.NullProviders enabled false" """)
                main.ONOSbench.handle.expect(":~")
                time.sleep(3)
                main.ONOSbench.handle.sendline("""onos $OC1 "cfg set org.onosproject.provider.nil.NullProviders enabled true" """)
                main.ONOSbench.handle.expect(":~")
                main.log.error("Null provider start failed, retrying..") 
                time.sleep(8)

        main.ONOSbench.handle.sendline("""onos $OC1 "null-simulation start" """)
        main.ONOSbench.handle.expect(":~")
        print main.ONOSbench.handle.before
        time.sleep(10)
        main.ONOSbench.handle.sendline("""onos $OC1 "balance-masters" """)
        main.ONOSbench.handle.expect(":~")
        
        temp = 1 
        for node in range(1, clusterCount + 1): 
            for switch in range (0, int(switchCount[node-1])): 
                cmd = ("""onos $OC1 "device-role null:000000000000000""" + str(temp) + " " + ONOSIp[node] + """ master" """)
                main.ONOSbench.handle.sendline(cmd)
                main.log.info( cmd ) 
                main.ONOSbench.handle.expect(":~")
                temp += 1


        #    cmd = ( """onos $OC1 "device-role null:0000000000000008 10.128.5.52 master" """)
        #if clusterCount == 7: 
        #    cmd = ( """onos $OC1 "device-role null:0000000000000008 10.128.5.53 master" """)
            
        #main.ONOSbench.handle.sendline(cmd)
        #main.log.info( cmd )
        #main.ONOSbench.handle.expect(":~")

        #print "sleeping"
        #time.sleep(120)

    def CASE2( self, main ):
         
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

        ingress = "null:0000000000000001"
        egress = "null:0000000000000008"

        for intents in intentsList:
            main.log.report("Intent Batch size: " + str(intents) + "\n      ")
            myResult = [["latency", "lastNode"] for x in range(sampleSize)]

            for run in range(0, (warmUp + sampleSize)):
                if run > warmUp:
                    main.log.info("Starting test iteration " + str(run-warmUp))

                cmd = """onos $OC1 push-test-intents -i" """
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
                    if ("flows=16,") in linkCheck:
                        break
                    if i == 39:
                        main.log.error("Flow count incorrect, data invalid."+ linkCheck)


                #collect timestamp from link cut
                cmd = """onos $OC1 null-link "null:0000000000000004/1 null:0000000000000003/2 down" """
                if debug: main.log.info("COMMAND: " + str(cmd))
                main.ONOSbench.handle.sendline(cmd)

                cmd = "onos-ssh $OC1 cat /opt/onos/log/karaf.log | grep TopologyManager| tail -1"
                for i in range(0,10):
                    main.ONOSbench.handle.sendline(cmd)
                    time.sleep(2)
                    main.ONOSbench.handle.expect(":~")
                    raw = main.ONOSbench.handle.before
                    if "NullLinkProvider" in raw and "links=14" in raw:
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
                if debug: main.log.info("Cut timestamp: " + cutTimestamp) 

                #validate link count and flow count
                for i in range(0, 40):
                    main.ONOSbench.handle.sendline("onos $OC1 summary")
                    main.ONOSbench.handle.expect(":~")
                    linkCheck = main.ONOSbench.handle.before
                    if "links=" + str(7*intents)+ "," in linkCheck and ("flows=" + str(7*intents) + ",") in linkCheck:
                        break
                    if i == 39:
                        main.log.error("Link or flow count incorrect, data invalid." + linkCheck)

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

                cmd = """ onos $OC1 null-link "null:0000000000000004/1 null:0000000000000003/2 up" """

                #wait for intent withdraw
                if debug: main.log.info(cmd)
                main.ONOSbench.handle.sendline(cmd)
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
                        main.log.info("Links Failed to reconnect, next iteration of data invalid." + linkCheck)

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

            resultsDB = open("IntentRerouteLatDB", "w+")
            resultsDB.write("'" + commit + "',") 
            resultsDB.write(str(clusterCount) + ",")
            resultsDB.write(str(intents) + ",")
            resultsDB.write(str(average) + ",")
            resultsDB.write(str(stdDev) + "\n")
            resultsDB.close()

