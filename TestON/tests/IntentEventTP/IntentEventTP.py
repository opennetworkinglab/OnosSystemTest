# ScaleOutTemplate
#
# CASE1 starts number of nodes specified in param file
#
# cameron@onlab.us

import sys
import os.path


class IntentEventTP:

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
        numSwitches = (main.params[ 'TEST' ][ 'numSwitches' ]).split(",")


        # ?? homeDir = os.path.expanduser('~')
        # ?? main.ONOSbench.handle.sendline("export TERM=vt100")
        # ?^ dump = main.ONOSbench.handle.expect(":~")        


        # -- INIT SECTION, ONLY RUNS ONCE -- # 
        if init == False: 
            init = True
            global clusterCount             #number of nodes running
            global ONOSIp                   #list of ONOS IP addresses
            global scale 
            
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
        
        # -- END OF INIT SECTION --#
         
        clusterCount = int(scale[0])
        scale.remove(scale[0])       
        
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

        myDistribution = []
        for node in range (1, clusterCount + 1):
            myDistribution.append(numSwitches[node-1])

        main.ONOSbench.createLinkGraphFile( BENCHIp,cellIp,myDistribution)
       
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
        main.log.info("Startup sequence complete")

        lastOutput = "--"
        origin = time.time()
        clockStarted = False
        while True:
            main.ONOSbench.handle.sendline("onos $OC1 summary")
            main.ONOSbench.handle.expect(":~")
            clusterCheck = ((main.ONOSbench.handle.before).splitlines())[3]
            print("\nBefore: " + str(clusterCheck))
            if ("SCC(s)=1,") in clusterCheck:
                break
            if clusterCheck != lastOutput:
                sameOutput = False
            elif clusterCheck == lastOutput:
                if clockStarted == False:
                    start = time.time()
                    clockStarted = True
                if time.time() > (start + 10):
                    main.log.error("TIMEOUT EXCEEDED: Clusters have not converged, continuing anyway...")
                    break
            lastOutput = clusterCheck
            time.sleep(5)

        main.ONOSbench.configNullDev(cellIp, myDistribution)

    def CASE2( self, main ): 
        import time
        import json
        import string
        import csv
        import numpy

        main.log.info("Cluster Count = " + str(clusterCount))

        intentsRate = main.params['METRICS']['intents_rate']
        intentsWithdrawn = main.params[ 'METRICS' ][ 'intents_withdrawn' ]
        intentsFailed  = main.params[ 'METRICS' ][ 'intents_failed' ]
        testDuration = main.params[ 'TEST' ][ 'duration' ]
        logInterval = main.params[ 'TEST' ][ 'log_interval' ]
        debug = main.params[ 'debugMode' ]
        numKeys = main.params[ 'TEST' ][ 'numKeys' ]
        cyclePeriod = main.params[ 'TEST' ][ 'cyclePeriod' ]
        neighbors = (main.params[ 'TEST' ][ 'neighbors' ]).split(",") 
        metricList = [intentsRate, intentsWithdrawn, intentsFailed]

        for n in range(0, len(neighbors)): 
            if neighbors[n] == 'a': 
                neighbors[n] = str(clusterCount -1)
        print str(neighbors)

        for n in neighbors:
            main.log.info("Run with " + n + " neighbors") 
            time.sleep(5)
            main.ONOSbench.handle.sendline("onos $OC1 cfg set org.onosproject.intentperf.IntentPerfInstaller numKeys " + numKeys )
            main.ONOSbench.handle.expect(":~")
            main.ONOSbench.handle.sendline("onos $OC1 cfg set org.onosproject.intentperf.IntentPerfInstaller numNeighbors " + n ) 
            main.ONOSbench.handle.expect(":~")
            main.ONOSbench.handle.sendline("onos $OC1 cfg set org.onosproject.intentperf.IntentPerfInstaller cyclePeriod " + cyclePeriod )
            main.ONOSbench.handle.expect(":~")

            cmd = "onos $OC1 intent-perf-start"
            main.ONOSbench.handle.sendline(cmd)
            main.ONOSbench.handle.expect(":~")
            main.log.info("Starting ONOS (all nodes)  intent-perf from $OC1" )

            main.log.info( "Starting test loop for " + str(testDuration) + " seconds...\n" )
            stop = time.time() + float( testDuration )

            while time.time() < stop:
                time.sleep( float( logInterval ) )
                groupResult = []
                for node in range (1, clusterCount + 1):
                    groupResult.append(0)

                    cmd = " onos-ssh $OC" + str(node) +  """ cat /opt/onos/log/karaf.log | grep "SNAPSHOT | Throughput" | tail -1  """
                    main.log.info("COMMAND: " + str(cmd))

                    x = 0
                    while True:
                        main.ONOSbench.handle.sendline(cmd)
                        main.ONOSbench.handle.expect(":~")
                        raw = main.ONOSbench.handle.before
                        if "OVERALL=" in raw:
                            break
                        x += 1
                        if x > 10:
                            main.log.error("Expected output not being recieved... continuing")
                            break
                        time.sleep(2)

                    raw = raw.splitlines()
                    splitResults = []
                    for line in raw:
                        splitResults.extend(line.split(" "))

                    myResult = "--"
                    for field in splitResults:
                        if "OVERALL" in field:
                            myResult = field

                    if myResult == "--":
                        main.log.error("Parsing/Pexpect error\n" + str(splitResults))

                    myResult = myResult.replace(";", "")
                    myResult = myResult.replace("OVERALL=","")
                    myResult = float(myResult)
                    groupResult[len(groupResult) -1] = myResult

                    main.log.info("Node " + str(node) + " overall rate: " + str(myResult))

                main.log.report("Results from this round of polling: " + str(groupResult))
                main.log.report("Cluster Total: " + str(numpy.sum(groupResult)) + "\n")
            
            cmd = "onos $OC1 intent-perf-stop"
            main.ONOSbench.handle.sendline(cmd)
            main.ONOSbench.handle.expect(":~")
            main.log.info("Stopping intentperf" )
     
