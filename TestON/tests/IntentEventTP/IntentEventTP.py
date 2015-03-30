# ScaleOutTemplate --> IntentEventTP
#
# CASE1 starts number of nodes specified in param file
#
# cameron@onlab.us

import sys
import os
import time


class IntentEventTP:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):            #This is the initialization case
        import os.path                  #this case will clean up all nodes 
        import time                     #but only node 1 is started in this case
        
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
        maxNodes = int(main.params[ 'availableNodes' ])
        MNip = main.params[ 'MN' ][ 'ip1' ]
        skipMvn = main.params[ 'TEST' ][ 'skipCleanInstall' ]
        numSwitches = (main.params[ 'TEST' ][ 'numSwitches' ]).split(",")

        homeDir = os.path.expanduser('~')
        
        main.ONOSbench.handle.sendline("export TERM=vt100")
        dump = main.ONOSbench.handle.expect(":~")

        #Populate ONOSIp with ips from params 
        for i in range(1, maxNodes + 1): 
            ipString = 'ip' + str(i) 
            ONOSIp.append(main.params[ 'CTRL' ][ ipString ])   
        
        #kill off all onos processes
        main.log.step("Safety check, killing all ONOS processes")
        main.log.step("before initiating enviornment setup")
        for node in range(1, maxNodes + 1):
            main.log.info("killing node " + str(node))
            main.ONOSbench.onosDie(ONOSIp[node])

        #construct the cell file
        main.log.info("Creating cell file")
        exec "a = main.ONOSbench.createCellFile"
        cellIp = []
        for node in range (1, clusterCount + 1):
            cellIp.append(ONOSIp[node])
        a(BENCHIp,cellName,MNip,str(Features), *cellIp)   

        main.step( "Set Cell" )
        main.ONOSbench.setCell(cellName)

        #Uninstall everywhere
        main.log.step( "Cleaning Enviornment..." )
        for i in range(1, maxNodes + 1):
            main.log.info(" Uninstalling ONOS " + str(i) )
            main.ONOSbench.onosUninstall( ONOSIp[i] )

        #git 
        main.step( "Git checkout and pull " + checkoutBranch )
        if gitPull == 'on':
            checkoutResult = main.ONOSbench.gitCheckout( checkoutBranch )
            pullResult = main.ONOSbench.gitPull()
        else:
            checkoutResult = main.TRUE
            pullResult = main.TRUE
            main.log.info( "Skipped git checkout and pull" )
        
        #mvn clean install, for debugging set param 'skipCleanInstall' to yes to speed up test
        if skipMvn != "yes":
            mvnResult = main.ONOSbench.cleanInstall()
 
        #null link
        #null provider 
        #linkgraph 
        #intentPerf

        myDistribution = []
        for node in range (1, clusterCount + 1):
            myDistribution.append(numSwitches[node-1])

        main.ONOSbench.createLinkGraphFile( BENCHIp,cellIp,myDistribution)
        main.ONOSbench.createNullDevProviderFile( BENCHIp, cellIp, myDistribution)
        main.ONOSbench.createNullLinkProviderFile(BENCHIp)

        main.log.step("Writing IntentPerf config file") 
        intentPerfConfig = open( homeDir + "/onos/tools/package/etc/org.onosproject.intentperf.IntentPerfInstaller.cfg", "w+")
        intentPerfConfig.write("numKeys = 40000\n")        
        intentPerfConfig.write("cyclePeriod = 1000\n")
        intentPerfConfig.write("numNeighors = 0\n")
        intentPerfConfig.close()
        
        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()  

        main.step( "Installing ONOS package" )
        install1Result = main.ONOSbench.onosInstall( node=ONOSIp[1] )

        main.step( "verify cells" )
        verifyCellResult = main.ONOSbench.verifyCell()

        main.step( "Checking if ONOS is up yet" )
        for i in range( 2 ):
            isup = main.ONOSbench.isup( ONOSIp[1] )
            if isup:
                break
        if not isup:
            main.log.report( "ONOS1 didn't start!" )

        lastOutput = "--" 
        origin = time.time()
        clockStarted = False 
        while True:
            main.ONOSbench.handle.sendline("onos $OC1 summary")
            main.ONOSbench.handle.expect(":~")
            clusterCheck = ((main.ONOSbench.handle.before).splitlines())[3]
            print("\nBefore: " + str(clusterCheck))
            if "SCC(s)=1," in clusterCheck:     
                break 
            if clusterCheck != lastOutput:
                sameOutput = False 
            elif clusterCheck == lastOutput:
                if clockStarted == False: 
                    start = time.time()
                    clockStarted = True
                if time.time() > (start + 30):
                    main.log.error("TIMEOUT EXCEEDED: Clusters have not converged, continuing anyway...") 
                    break 
            lastOutput = clusterCheck
            time.sleep(5)



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
        import os.path
        global clusterCount
        
        Features= main.params[ 'ENV' ][ 'cellFeatures' ] 
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        MNip = main.params[ 'MN' ][ 'ip1' ]
        BENCHIp = main.params[ 'BENCH' ][ 'ip1' ]
        numSwitches = (main.params[ 'TEST' ][ 'numSwitches' ]).split(",")
        scale = int( main.params[ 'SCALE' ] )
        maxNodes = int(main.params[ 'availableNodes' ])
        clusterCount += scale
        homeDir = os.path.expanduser('~')        

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
        exec "a = main.ONOSbench.createCellFile"
        cellIp = []
        for node in range (1, clusterCount + 1):
            cellIp.append(ONOSIp[node])
        a(BENCHIp,cellName,MNip,str(Features), *cellIp)

        main.step( "Set Cell" )
        main.ONOSbench.setCell(cellName)

        myDistribution = []
        for node in range (1, clusterCount + 1):
            myDistribution.append(numSwitches[node-1])

        main.ONOSbench.createLinkGraphFile( BENCHIp, cellIp, myDistribution)
        main.ONOSbench.createNullDevProviderFile( BENCHIp, cellIp, myDistribution)
        main.ONOSbench.createNullLinkProviderFile( BENCHIp )

        #neighbors = max(1, clusterCount-1) 
        neighbors = 0

        main.log.step("Writing IntentPerf config file")
        intentPerfConfig = open( homeDir + "/onos/tools/package/etc/org.onosproject.intentperf.IntentPerfInstaller.cfg", "w+")
        intentPerfConfig.write("numKeys = 40000\n")
        intentPerfConfig.write("cyclePeriod = 1000\n")
        intentPerfConfig.write("numNeighors = " + str(neighbors) + "\n")
        intentPerfConfig.close()

        main.step( "Creating ONOS package, preparing to reinstall" )
        packageResult = main.ONOSbench.onosPackage()   
       
        main.log.report( "Reinstalling on all nodes and increasing cluster size to " + str( clusterCount ) )
        for node in range(1, clusterCount + 1):
            main.log.info("Starting ONOS " + str(node) + " at IP: " + ONOSIp[node])    
            main.ONOSbench.onosInstall( ONOSIp[node])
    
            for i in range( 2 ):
                isup = main.ONOSbench.isup( ONOSIp[node] )
                if isup:
                    main.log.info("ONOS " + str(node) + " is up\n")
                    break
            if not isup:
                main.log.report( "ONOS " + str(node) + " didn't start!" )
        
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
                if time.time() > (start + 60):
                    main.log.error("TIMEOUT EXCEEDED: Clusters have not converged, continuing anyway...")
                    break
            lastOutput = clusterCheck
            time.sleep(5)
        
            
    def CASE3( self, main ):   
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

        metricList = [intentsRate, intentsWithdrawn, intentsFailed]
        
        tempsleep =20
        main.log.info("sleeping " + str(tempsleep)) 
        time.sleep(tempsleep)
        
        loadFrom = ['0']
        loadFrom.extend((main.params[ 'TEST' ][ 'loadFrom' ]).split(","))

        for node in range(1, clusterCount+1):
            if loadFrom[node] == "1": 
                cmd = "onos $OC" + str(node) + " feature:install onos-app-intent-perf"
                main.ONOSbench.handle.sendline(cmd)
                main.ONOSbench.handle.expect(":~")
                main.log.info("Load initiated on node " + str(node))
        
            time.sleep(5)
            actcmd = "onos $OC" + str(node) + " intent-perf-start"
            main.ONOSbench.handle.sendline(actcmd)
            main.ONOSbench.handle.expect(":~")
            main.log.info("Starting ONOS " + str(node) + "  intent-perf...")

        main.log.info( "Starting test loop for " + str(testDuration) + " seconds...\n" )
        stop = time.time() + float( testDuration )
        
        while time.time() < stop:
            time.sleep( float( logInterval ) )
            groupResult = []
            for node in range (1, clusterCount + 1):
                if loadFrom[node] == "0": continue
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
                
