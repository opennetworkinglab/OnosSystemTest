# ScaleOutTemplate -> flowTP
#
# CASE1 starts number of nodes specified in param file
#
# cameron@onlab.us

import sys
import os.path


class flowTP1g:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):            #This is the initialization case
                                        #this case will clean up all nodes 
                                        #but only node 1 is started in this case
        
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
        
        main.ONOSbench.handle.sendline("export TERM=vt100")

        #Populate ONOSIp with ips from params 
        for i in range(1, maxNodes + 1): 
            ipString = 'ip' + str(i) 
            ONOSIp.append(main.params[ 'CTRL' ][ ipString ])   

        #kill off all onos processes 
        main.log.step("Safety check, killing all ONOS processes")
        main.log.step("before initiating enviornment setup")
        for node in range(1, maxNodes + 1):
            main.ONOSbench.onosDie(ONOSIp[node])


        #construct the cell file
        main.log.info("Creating initial cell file")
        exec "a = main.ONOSbench.createCellFile"
        cellIp = []
        for node in range(1, 2):
        #for node in range (1, maxNodes + 1):
            cellIp.append(ONOSIp[node])
        a(BENCHIp,cellName,MN1Ip,str(Features), *cellIp)

        main.log.info(cellIp)

        #Uninstall everywhere
        #main.log.step( "Cleaning Enviornment..." )
        #for i in range(1, maxNodes + 1):
        #    main.log.info(" Uninstalling ONOS " + str(i) )
        #    main.ONOSbench.onosUninstall( ONOSIp[i] )
        
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


        #main.step( "Set cell for ONOS cli env" )
        #main.ONOS1cli.setCell( cellName )
        
        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()  

        #main.step( "Installing ONOS package" )
        #install1Result = main.ONOSbench.onosInstall( node=ONOSIp[1] )

        cellName = main.params[ 'ENV' ][ 'cellName' ]
        main.step( "Applying cell file to environment" )
        cellApplyResult = main.ONOSbench.setCell( cellName )
        main.step( "verify cells" )
        verifyCellResult = main.ONOSbench.verifyCell()

        #main.step( "Set cell for ONOS cli env" )
        #cli1 = main.ONOS1cli.startOnosCli( node=ONOSIp[1] )

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

        scale = int( main.params[ 'SCALE' ] )
        clusterCount += scale

        main.log.report( "Increasing cluster size to " + str( clusterCount ) )
        for node in range((clusterCount - scale) + 1, clusterCount + 1):
            main.ONOSbench.onosDie(ONOSIp[node])
            time.sleep(10)
            main.log.info("Starting ONOS " + str(node) + " at IP: " + ONOSIp[node])    
            main.ONOSbench.onosInstall( node=ONOSIp[node])
            exec "a = main.ONOS%scli.startOnosCli" %str(node)
            a(ONOSIp[node])
    
    
    def CASE3( self, main ):
        #
        # This is the flow TP test 
        #
        import os.path  
        import numpy       
        import math
        import time 
        import datetime
        import traceback

        testCMD = [ 0,0,0,0 ]
        warmUp = int(main.params[ 'TEST' ][ 'warmUp' ])
        sampleSize = int(main.params[ 'TEST' ][ 'sampleSize' ])
        switches = int(main.params[ 'TEST' ][ 'switches' ])
        neighborList = main.params[ 'TEST' ][ 'neighbors' ]
        serverList = main.params[ 'TEST' ][ 'servers' ]
        #flows = int(main.params[ 'TEST' ][ 'flows' ]) 
        testCMD[0] = main.params[ 'TEST' ][ 'testCMD0' ]
        testCMD[1] = main.params[ 'TEST' ][ 'testCMD1' ]
        maxNodes = main.params[ 'availableNodes' ]
        onBaremetal = main.params['isOnBaremetal']


        cellName = main.params[ 'ENV' ][ 'cellName' ]
        Features= main.params[ 'ENV' ][ 'cellFeatures' ]
        BENCHIp = main.params[ 'BENCH' ][ 'ip1' ]
        BENCHUser = main.params[ 'BENCH' ][ 'user' ]
        MN1Ip = main.params[ 'MN' ][ 'ip1' ]
        maxNodes = int(main.params[ 'availableNodes' ])
        Features = main.params[ 'ENV' ][ 'cellFeatures' ]
        homeDir = os.path.expanduser('~')
    
        serverList = serverList.split(",")
        main.log.info("serverlist: " + str(serverList))
        neighborList = neighborList.split(",") 
        main.log.info("neightborlist: " + str(neighborList))

        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        logFileName = "../logs/flowTPResultsLog" + str(st)

        #initialize log file, remove any previous data
        resultsLog = open("flowTPResultsLog","w+")
        resultsLog.close()

        #write file to change mem limit to 32 gigs (BAREMETAL ONLY!)
        if onBaremetal == "true":
            filename = "/onos/tools/package/bin/onos-service"
            serviceConfig = open(homeDir + filename, 'w+')
            serviceConfig.write("#!/bin/bash\n ")
            serviceConfig.write("#------------------------------------- \n ")
            serviceConfig.write("# Starts ONOS Apache Karaf container\n ")
            serviceConfig.write("#------------------------------------- \n ")
            serviceConfig.write("#export JAVA_HOME=${JAVA_HOME:-/usr/lib/jvm/java-7-openjdk-amd64/}\n ")
            serviceConfig.write("""export JAVA_OPTS="${JAVA_OPTS:--Xms8G -Xmx8G}" \n """)
            serviceConfig.write("")
            serviceConfig.write("ONOS_HOME=/opt/onos \n ")
            serviceConfig.write("")
            serviceConfig.write("[ -d $ONOS_HOME ] && cd $ONOS_HOME || ONOS_HOME=$(dirname $0)/..\n")
            serviceConfig.write("""${ONOS_HOME}/apache-karaf-$KARAF_VERSION/bin/karaf "$@" \n """)
            serviceConfig.close()

        for n in neighborList:
            for servers in serverList:
                main.log.step("\tSTARTING TEST")
                main.log.step("\tSERVERS:  \t" + servers ) 
                main.log.step("\tNEIGHBORS:\t" + n )  
                main.log.info("=============================================================")
                main.log.info("=============================================================")
                #write file to configure nil link
                ipCSV = ""
                for i in range (1, int(maxNodes) + 1):
                    tempstr = "ip" + str(i)
                    ipCSV += main.params[ 'CTRL' ][ tempstr ] 
                    if i < int(maxNodes):
                        ipCSV +=","
                
                filename = "/onos/tools/package/etc/org.onosproject.provider.nil.link.impl.NullLinkProvider.cfg"
                linkConfig = open(homeDir + filename,'w+')
                linkConfig.write("# eventRate = 2000\n")
                linkConfig.write("neighbors = "  + ipCSV)
                main.log.info(" NullLinkProvider.cfg: " + ipCSV)
                linkConfig.close()

  
                #write file for null device 
                filename = "/onos/tools/package/etc/org.onosproject.provider.nil.device.impl.NullDeviceProvider.cfg"
                deviceConfig = open(homeDir + filename,'w+')    
            
                serversToRun = max(int(servers), (int(n) + 1))

                switchDistribution = [(switches/int(serversToRun))]*int(serversToRun) 
                main.log.info("Switch distribution init: " + str(switchDistribution))
                remainder = switches % int(serversToRun) 
                for r in range(0, remainder): 
                    switchDistribution[r] += 1 
                main.log.info("Switch distribution: " + str(switchDistribution))
                    
                deviceSettings = ""
                for i in range(0, serversToRun):
                    deviceSettings += (ONOSIp[i+1] + ":" + str(switchDistribution[i]))
                    if i < int(serversToRun)-1: 
                        deviceSettings +=","         

                deviceConfig.write("devConfigs = "  + deviceSettings)
                main.log.info(" NullDeviceProvider.cfg: " + deviceSettings)
                deviceConfig.close() 

                main.log.info("Creating cell file for this step")
                exec "a = main.ONOSbench.createCellFile"
                cellIp = []
                for node in range (1, serversToRun + 1):
                    cellIp.append(ONOSIp[node]) 
                main.log.info("Cells are: " + str(cellIp) )
                a(BENCHIp,cellName,MN1Ip,str(Features), *cellIp)
                main.step( "Applying cell file to environment for this step" )
                cellApplyResult = main.ONOSbench.setCell( cellName )
                main.step( "verify cells for this step" )
                verifyCellResult = main.ONOSbench.verifyCell()
                
                #devide flows
                flows = int(main.params[ 'TEST' ][ 'flows' ])
                main.log.info("Flow Target  = " + str(flows))

                flows = (flows *max(int(n)+1,int(servers)))/((int(n) + 1)*int(servers)*(switches))

                main.log.info("Flows per switch = " + str(flows))
                #main.log.info("Total flows = " + str(switches * flows))

                
                #kill off all onos processes
                main.log.step("Safety check, killing all ONOS processes")
                for node in range(1, int(maxNodes) + 1):
                    main.ONOSbench.onosDie(ONOSIp[node]) 
                  
                #Uninstall everywhere
                main.log.step( "Cleaning Enviornment..." )
                for i in range(1, int(maxNodes) + 1):
                    main.log.info(" Uninstalling ONOS " + str(i) )
                    main.ONOSbench.onosUninstall( ONOSIp[i] )

                #package
                main.log.step( "Repackaging onos to reflect config file changes" )
                main.ONOSbench.onosPackage()
                
                # install on relevant nodes
                startNodes = max(int(n), serversToRun)
                main.log.step( "Reinstalling ONOS on relevant nodes (1-" + str(startNodes) + ")" )          
                for s in range(1, startNodes + 1): 
                    main.ONOSbench.onosInstall( node=ONOSIp[s])    
                    exec "a = main.ONOS%scli.startOnosCli" %str(s)
                    a(ONOSIp[s])

                main.log.info("sleeping 30 second waiting for null provider bundle...")
                time.sleep(30)

                #build list of servers in "$OC1, $OC2...." format
                serverEnvVars = ""
                for i in range (1,int(servers)+1):
                    serverEnvVars += ("-s " + ONOSIp[i] + " ")
                
                data = [[""]*int(servers)]*int(sampleSize)
                maxes = [""]*int(sampleSize)

                for test in range(0, (warmUp + sampleSize)): 
                    flowCMD = "python3 " + homeDir + "/onos/tools/test/bin/"
                    flowCMD += testCMD[0] + " " + str(flows) + " " + testCMD[1] 
                    flowCMD += " " + str(n) + " " + str(serverEnvVars)
                    print("\n")                    
                    main.log.info("COMMAND: " + flowCMD)
                    main.log.info("Executing command") 
                    main.ONOSbench.handle.sendline(flowCMD)
                    result = []
                    for s in range(0, int(servers)):
                        result.append("q")
                    
                    for s in range(0, int(servers)):
                        main.ONOSbench.handle.expect("ms")
                        rawResult = ((main.ONOSbench.handle.before).splitlines())

                        rawResult = ((rawResult.pop()).split(" "))
                        main.log.info("Debug: rawResult: " + str(rawResult))

                        myresult = int(rawResult[2])
                        main.log.info("Result: " + str(myresult))                    
                            
                        myIp = rawResult[0]
                        main.log.info("myIp: " + myIp)

                        serverIndex = int(ONOSIp.index(myIp))
                        main.log.info("server index = " + str(serverIndex))
                            
                        result[serverIndex - 1] = myresult
                    
                    if test >= warmUp:
                        maxes[test-warmUp] = max(result)
                        main.log.info("Data collection iteration: " + str(test-warmUp) + " of " + str(sampleSize))
                        main.log.info("Throughput time: " + str(maxes[test-warmUp]) + "(ms)")                

                    if test >= warmUp:
                        data[test-warmUp] = result

                    # wait for flows = 0 
                    removedFlows = False
                    repeat = 0
                    time.sleep(3)
                    while removedFlows == False & repeat <= 10:
                        main.ONOSbench.handle.sendline("onos $OC1 summary| cut -d ' ' -f6")
                        main.ONOSbench.handle.expect("~")
                        before = main.ONOSbench.handle.before
                        parseTest = before.splitlines()
                        flowsummary = ""
                        for line in parseTest:
                            if "flow" in str(line):
                                flowsummary = line 
                                break
                        currentflow = ""
                        for word in flowsummary.split(" "): 
                            if "flow" in str(word):
                                currentflow = str(word)
                        currentflow = currentflow.replace(",","")
                        currentflow = currentflow.replace("\n","")
                        main.log.info(currentflow)

                        zeroFlow = "flows=0"                
                        if zeroFlow in before:
                            removedFlows = True 
                            main.log.info("\t Wait 5 sec of cool down...")
                            time.sleep(5)

                        time.sleep(5)
                        repeat +=1
         
                main.log.info("raw data: " + str(data))
                main.log.info("maxes:" + str(maxes))

                
                # report data
                print("")
                main.log.info("\t Results (measurments are in milliseconds)")
                print("")

                nodeString = ""
                for i in range(1, int(servers) + 1):
                    nodeString += ("\tNode " + str(i)) 
                 
                for test in range(0, sampleSize ):
                    main.log.info("\t Test iteration " + str(test + 1) )
                    main.log.info("\t------------------")
                    main.log.info(nodeString)       
                    resultString = ""

                    for i in range(0, int(servers) ):
                        resultString += ("\t" + str(data[test][i]) ) 
                    main.log.info(resultString)

                    print("\n")

                avgOfMaxes = numpy.mean(maxes)
                main.log.info("Average of max value from each test iteration: " + str(avgOfMaxes))

                stdOfMaxes = numpy.std(maxes)
                main.log.info("Standard Deviation of max values: " + str(stdOfMaxes))       
                print("\n\n")

                avgTP = int(main.params[ 'TEST' ][ 'flows' ])  / avgOfMaxes #result in kflows/second
                
                tp = []
                for i in maxes: 
                    tp.append((int(main.params[ 'TEST' ][ 'flows' ]) / i ))

                stdTP = numpy.std(tp)

                main.log.info("Average thoughput:  " + str(avgTP) + " Kflows/second" )
                main.log.info("Standard deviation of throughput: " + str(stdTP) + " Kflows/second") 

                resultsLog = open(logFileName,"a")
                resultsLog.write(str(main.params[ 'TEST' ][ 'flows' ]) + "," + n + "," + str(servers) + str(switches) + "," + str(warmUp))
                resultsLog.write("," +str(sampleSize) + "," + str(avgTP) + "," + str(stdTP) + "\n")
                resultsLog.close()
 
                    
