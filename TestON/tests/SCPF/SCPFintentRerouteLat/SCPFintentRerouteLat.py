# ScaleOutTemplate
#
# CASE1 starts number of nodes specified in param file
#
# cameron@onlab.us

import sys
import os.path


class SCPFintentRerouteLat:

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
        BENCHUser = main.params[ 'BENCH' ][ 'user' ]
        BENCHIp = main.params[ 'BENCH' ][ 'ip1' ]
        MN1Ip = main.params[ 'MN' ][ 'ip1' ]
        main.maxNodes = int(main.params[ 'max' ])
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
            ONOSIp = [0]
            ONOSIp.extend(main.ONOSbench.getOnosIps())

            print("-----------------" + str(ONOSIp))
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

            resultsDB = open("/tmp/IntentRerouteLatDB", "w+")
            resultsDB.close()

        # -- END OF INIT SECTION --#

        clusterCount = int(scale[0])
        scale.remove(scale[0])

        #kill off all onos processes
        main.log.step("Safety check, killing all ONOS processes")
        main.log.step("before initiating environment setup")
        for node in range(1, main.maxNodes + 1):
            main.ONOSbench.onosDie(ONOSIp[node])

        #Uninstall everywhere
        main.log.step( "Cleaning Enviornment..." )
        for i in range(1, main.maxNodes + 1):
            main.log.info(" Uninstalling ONOS " + str(i) )
            main.ONOSbench.onosUninstall( ONOSIp[i] )

        #construct the cell file
        main.log.info("Creating cell file")
        cellIp = []
        for node in range (1, clusterCount + 1):
            cellIp.append(ONOSIp[node])

        main.ONOSbench.createCellFile(BENCHIp,cellName,MN1Ip,str(Apps), cellIp)

        main.step( "Set Cell" )
        main.ONOSbench.setCell(cellName)

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

        deviceMastership = (main.params[ 'TEST' ][ "s" + str(clusterCount) ]).split(",")
        print("Device mastership list: " + str(deviceMastership))

        main.ONOSbench.onosCfgSet( ONOSIp[1], "org.onosproject.store.flow.impl.NewDistributedFlowRuleStore", "backupEnabled false")

        main.log.step("Setting up null provider")
        for i in range(3):
            main.ONOSbench.onosCfgSet( ONOSIp[1], "org.onosproject.provider.nil.NullProviders", "deviceCount 8")
            main.ONOSbench.onosCfgSet( ONOSIp[1], "org.onosproject.provider.nil.NullProviders", "topoShape reroute")
            main.ONOSbench.onosCfgSet( ONOSIp[1], "org.onosproject.provider.nil.NullProviders", "enabled true")
            time.sleep(5)
            main.ONOSbench.handle.sendline("onos $OC1 summary")
            main.ONOSbench.handle.expect(":~")
            x = main.ONOSbench.handle.before
            if "devices=8" in x and "links=16," in x:
                break

        index = 1
        for node in deviceMastership:
            for attempt in range(0,10):
                cmd = ( "onos $OC" + node + """ "device-role null:000000000000000""" + str(index) + " " + ONOSIp[int(node)]  + """ master" """)
                main.log.info("assigning mastership of device " + str(index) + " to node " + node + ": \n " + cmd + "\n")
                main.ONOSbench.handle.sendline(cmd)
                main.ONOSbench.handle.expect(":~")
                time.sleep(4)

                cmd = ( "onos $OC" + node + " roles|grep 00000" + str(index))
                main.log.info(cmd)
                main.ONOSbench.handle.sendline(cmd)
                main.ONOSbench.handle.expect(":~")
                check = main.ONOSbench.handle.before
                main.log.info("CHECK:\n" + check)
                if ("master=" + ONOSIp[int(node)]) in check:
                    break
            index += 1

        main.ONOSbench.logReport(ONOSIp[1], ["ERROR", "WARNING", "EXCEPT"])

    def CASE2( self, main ):

        import time
        import numpy
        import datetime
        #from scipy import stats

        ts = time.time()

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
        egress = "null:0000000000000007"

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
                    if ("links=16,") in linkCheck and ("flows=" + str(intents*7) + ","):
                        break
                    if i == 39:
                        main.log.error("Flow/link count incorrect, data invalid."+ linkCheck)
                        main.ONOSbench.logReport(ONOSIp[1], ["ERROR", "WARNING", "EXCEPT"], "d")
                        #main.ONOSbench.logReport(ONOSIp[(clusterCount-1)], ["ERROR", "WARNING", "EXCEPT"], "d")
                        main.ONOSbench.sendline("onos $OC1 summary")
                        main.ONOSbench.sendline("onos $OC1 devices")
                        main.ONOSbench.sendline("onos $OC1 links")
                        main.ONOSbench.expect(":~")
                        main.log.info(main.ONOSbench.before)

                #collect timestamp from link cut
                cmd = """onos $OC1 null-link "null:0000000000000004/1 null:0000000000000003/2 down" """
                if debug: main.log.info("COMMAND: " + str(cmd))
                main.ONOSbench.handle.sendline(cmd)
                main.ONOSbench.handle.expect(":~")

                cmd = "onos-ssh $OC1 cat /opt/onos/log/karaf.log | grep TopologyManager| tail -1"
                for i in range(0,10):
                    main.ONOSbench.handle.sendline(cmd)
                    time.sleep(2)
                    main.ONOSbench.handle.expect(":~")
                    raw = main.ONOSbench.handle.before
                    #if "NullLinkProvider" in raw and "links=14" in raw:
                    if "links=14" in raw:
                        break
                    if i >= 9:
                        main.log.error("Expected output not being recieved... continuing")
                        main.log.info(raw)
                        break
                    time.sleep(2)

                if debug: main.log.debug("raw: " + raw)

                temp = raw.splitlines()

                if debug: main.log.debug("temp (after splitlines): " + str(temp))

                # Since the string is deterministic the date is always the 3rd element.
                # However, if the data were grepping for in the onos log changes then this will
                # not work. This is why we print out the raw and temp string so we can visually
                # check if everything is in the correct order. temp should like this:
                # temp = ['/onos$ onos-ssh $OC1 cat /opt/onos/log/karaf.log | grep Top ', 
                #         'ologyManager| tail -1', '2015-10-15 12:03:33,736 ... ]
                temp = temp[2]

                if debug: main.log.debug("temp (checking for date): " + str(temp))

                cutTimestamp = (temp.split(" "))[0] + " " + (temp.split(" "))[1]

                if debug: main.log.info("Cut timestamp: " + cutTimestamp)

                #validate link count and flow count
                for i in range(0, 40):
                    main.ONOSbench.handle.sendline("onos $OC1 summary")
                    main.ONOSbench.handle.expect(":~")
                    linkCheck = main.ONOSbench.handle.before
                    #if "links=" + str(7*intents)+ "," in linkCheck and ("flows=" + str(7*intents) + ",") in linkCheck:
                    if "links=14," in linkCheck and ("flows=" + str(8*intents) + ",") in linkCheck:
                        break
                    if i == 39:
                        main.log.error("Link or flow count incorrect, data invalid." + linkCheck)
                        main.ONOSbench.logReport(ONOSIp[1], ["ERROR", "WARNING", "EXCEPT"], "d")

                time.sleep(5) #trying to avoid negative values

                #intents events metrics installed timestamp
                IEMtimestamps = [0]*(clusterCount + 1)
                installedTemp = [0]*(clusterCount + 1)
                for node in range(1, clusterCount +1):
                    cmd = "onos $OC" + str(node) + """ "intents-events-metrics"|grep Timestamp """
                    raw = ""
                    while "epoch)" not in raw:
                        main.ONOSbench.handle.sendline(cmd)
                        main.ONOSbench.handle.expect(":~")
                        raw = main.ONOSbench.handle.before

                    print(raw)

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
                if debug: main.log.info(cmd)
                main.ONOSbench.handle.sendline(cmd)
                main.ONOSbench.handle.expect(":~")

                #wait for intent withdraw
                main.ONOSbench.handle.sendline(withdrawCmd)
                main.log.info(withdrawCmd)
                main.ONOSbench.handle.expect(":~")
                if debug: main.log.info(main.ONOSbench.handle.before)
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

            average = numpy.multiply(average, 1000)
            stdDev = numpy.multiply(stdDev, 1000)

            main.log.report("Scale: " + str(clusterCount) + "  \tIntent batch: " + str(intents))
            main.log.report("Latency average:................" + str(average))
            main.log.report("Latency standard deviation:....." + str(stdDev))
            main.log.report("Mode of last node to respond:..." + str(nodeMode))
            main.log.report("________________________________________________________")

            resultsDB = open("/tmp/IntentRerouteLatDB", "a")
            resultsDB.write("'" + commit + "',")
            resultsDB.write(str(clusterCount) + ",")
            resultsDB.write(str(intents) + ",")
            resultsDB.write(str(average) + ",")
            resultsDB.write(str(stdDev) + "\n")
            resultsDB.close()

            main.ONOSbench.logReport(ONOSIp[1], ["ERROR", "WARNING", "EXCEPT"])

