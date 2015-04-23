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
 
        #----do i need this line?
        #main.ONOSbench.handle.sendline("export TERM=vt100")

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

            resultsDB = open("flowTP1gDB", "w+")
            resultsDB.close()

        # -- END OF INIT SECTION --#

        clusterCount = int(scale[0])
        scale.remove(scale[0])
        main.log.info("CLUSTER COUNT: " + str(clusterCount))

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
        main.log.info("Cell Ip list: " + str(cellIp))
        
        main.step( "Set Cell" )
        main.ONOSbench.setCell(cellName)       
 
        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()  

        main.step( "verify cells" )
        verifyCellResult = main.ONOSbench.verifyCell()

        main.log.report( "Initializeing " + str( clusterCount ) + " node cluster." )
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
        
        for node in range(1, clusterCount + 1):
            exec "a = main.ONOS%scli.startOnosCli" %str(node)
            a(ONOSIp[node])
         
        main.log.info("Startup sequence complete")

        
    def CASE2( self, main ):
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
        neighborList = (main.params[ 'TEST' ][ 'neighbors' ]).split(",")
        testCMD[0] = main.params[ 'TEST' ][ 'testCMD0' ]
        testCMD[1] = main.params[ 'TEST' ][ 'testCMD1' ]
        maxNodes = main.params[ 'availableNodes' ]
        onBaremetal = main.params['isOnBaremetal']

        cellName = main.params[ 'ENV' ][ 'cellName' ]
        BENCHIp = main.params[ 'BENCH' ][ 'ip1' ]
        BENCHUser = main.params[ 'BENCH' ][ 'user' ]
        MN1Ip = main.params[ 'MN' ][ 'ip1' ]
        maxNodes = int(main.params[ 'availableNodes' ])
        homeDir = os.path.expanduser('~')
  
        servers = str(clusterCount) 
        for i in range(0, len(neighborList)):
            if neighborList[i] == 'a':
                neighborList[i] = str(clusterCount - 1)  
        
        if clusterCount == 1: 
            neighborList = ['0']
        main.log.info("neightborlist: " + str(neighborList))

        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        #initialize log file, remove any previous data
        resultsLog = open("flowTP1gDB","w+")
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
            main.log.step("\tSTARTING TEST")
            main.log.step("\tLOADING FROM SERVERS:  \t" + str(clusterCount) ) 
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
            
            main.ONOSbench.handle.sendline("""onos $OC1 "cfg setorg.onosproject.provider.nil.NullProviders enabled true" """)
            main.ONOSbench.handle.expect(":~")
            main.ONOSbench.handle.sendline("""onos $OC1 "cfg set org.onosproject.provider.nil.NullProviders deviceCount 35" """)
            main.ONOSbench.handle.expect(":~")
            main.ONOSbench.handle.sendline("""onos $OC1 "cfg set org.onosproject.provider.nil.NullProviders topoShape linear" """)
            main.ONOSbench.handle.expect(":~")
            main.ONOSbench.handle.sendline("""onos $OC1 "null-simulation start" """)
            main.ONOSbench.handle.expect(":~")
            main.ONOSbench.handle.sendline("""onos $OC1 "balance-masters" """)
            main.ONOSbench.handle.expect(":~")
        
            #devide flows
            flows = int(main.params[ 'TEST' ][ 'flows' ])
            main.log.info("Flow Target  = " + str(flows))

            flows = (flows *max(int(n)+1,int(servers)))/((int(n) + 1)*int(servers)*(switches))

            main.log.info("Flows per switch = " + str(flows))

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
                
                for i in range(0,15):
                    main.ONOSbench.handle.sendline(flowCMD)
                    time.sleep(1)
                    main.ONOSbench.handle.expect(":~")
                    rawResult = main.ONOSbench.handle.before
                    if " -> " in rawResult:
                        break

                result = [""]*(clusterCount)
                rawResult = rawResult.splitlines()
                print(rawResult)
                for node in range(1, clusterCount + 1):        
                    for line in rawResult:
                        if ONOSIp[node] in line and " -> " in line:
                            myLine = line.split(" ")
                            for word in myLine:
                                if "ms" in word:
                                    result[node-1] = int(word.replace("ms",""))
                                    main.log.info("Parsed result: " + str(result[node-1]))
                                    break
                            break

                if test >= warmUp:
                    for i in result: 
                        if i == "": 
                            main.log.error("Missing data point, critical failure incoming")

                    print result
                    maxes[test-warmUp] = max(result)
                    main.log.info("Data collection iteration: " + str(test-warmUp) + " of " + str(sampleSize))
                    main.log.info("Throughput time: " + str(maxes[test-warmUp]) + "(ms)")                

                if test >= warmUp:
                    data[test-warmUp] = result

                # wait for flows = 0 
                removedFlows = False
                repeat = 0
                time.sleep(3)
                while ( removedFlows == False and repeat <= 10 ):
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
                    #main.log.info(currentflow)

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

            resultsLog = open("flowTP1gDB","a")
            resultsLog.write("'" + commit + "',")
            resultsLog.write("'1gig',")
            resultsLog.write((main.params[ 'TEST' ][ 'flows' ]) + ",")
            resultsLog.write(str(clusterCount)+ ",")
            resultsLog.write(str(n) + ",")
            resultsLog.write(str(avgTP) + "," + str(stdTP) + "\n")
            resultsLog.close()

             