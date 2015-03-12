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
        numSwitches = main.params[ 'TEST' ][ 'numSwitches' ]

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
 
        #configure null device provider         
        switchList = [0,int(numSwitches),0,0,0,0,0,0]
        devicesString  = ""
        for node in range(1, maxNodes + 1):
            devicesString += (ONOSIp[node] + ":" + str(switchList[node] ))
            if node < maxNodes:
                devicesString += (",")

        main.log.info("Configuring device provider: ONOS 1 with " + (numSwitches) + " switches")
        localPath = "/onos/tools/package/etc/org.onosproject.provider.nil.device.impl.NullDeviceProvider.cfg"
        filePath = homeDir + localPath
        main.log.info(filePath)

        configFile = open(filePath, 'w+')
        configFile.write("devConfigs = " + devicesString + "\n")
        configFile.write("#numPorts = 8") 
        configFile.close()
        main.log.info("DevConfig = " + devicesString) 
        main.log.info("Device provider file written and closed")

        ## configuring null link provider
        main.log.info(" Configuring null provider to disable flicker" )
        homeDir = os.path.expanduser('~')
        main.log.info(homeDir)
        localPath = "/onos/tools/package/etc/org.onosproject.provider.nil.link.impl.NullLinkProvider.cfg"
        filePath = homeDir + localPath
        main.log.info(filePath)

        neighborsString = ""
        for node in range(1, maxNodes + 1):
            neighborsString += ONOSIp[node]
            if node < maxNodes:
                neighborsString += ","

        configFile = open(filePath, 'w+')
        configFile.write("#eventRate =\n")
        configFile.write("#cfgFile = /tmp/foo.cfg        #If enabled, points to the full path to the topology file.\n")
        configFile.write("#neighbors = ")
        configFile.close()
        main.log.info("Configuration completed")
        
        main.log.info("Writing link graph configuration file..." )
        homeDir = os.path.expanduser('~')
        localPath = "/onos/tools/package/etc/linkGraph.cfg"
        filePath = homeDir + localPath
        linkGraph = open(filePath, 'w+')
        linkGraph.write("# NullLinkProvider topology description (config file).\n")
        linkGraph.write("# The NodeId is only added if the destination is another node's device.\n")
        linkGraph.write("# Bugs: Comments cannot be appended to a line to be read.\n")

        myPort = 6
        for node in range(1, clusterCount+1):
            linkGraph.write("graph " + ONOSIp[node] + " {\n")
            for switch in range (0, switchList[node]-1):
                line = ""
                line = ("\t" + str(switch) + ":" + str(myPort))
                line += " -- "
                line += (str(switch+1) + ":" + str(myPort-1) + "\n")
                linkGraph.write(line) 
            linkGraph.write("}")
        linkGraph.close()        

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
            if "SCC(s)=1," in clusterCheck and ("devices=" + str(numSwitches)) in clusterCheck:                  #check for links and devices too 
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
        numSwitches = int(main.params[ 'TEST' ][ 'numSwitches' ])
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

        baselineSwitchCount = numSwitches/clusterCount
        switchList = [0,0,0,0,0,0,0,0]
        
        for node in range(1, clusterCount + 1):
            switchList[node] = baselineSwitchCount  
            
        for node in range(1, (numSwitches%clusterCount)+1):
            switchList[node] += 1
                      
        devicesString  = ""
        for node in range(1, maxNodes + 1):
            devicesString += (ONOSIp[node] + ":" + str(switchList[node] ))
            if node < maxNodes:
                devicesString += (",")

        main.log.info("Configuring device provider")
        localPath = "/onos/tools/package/etc/org.onosproject.provider.nil.device.impl.NullDeviceProvider.cfg"
        filePath = homeDir + localPath
        main.log.info(filePath)

        configFile = open(filePath, 'w+')
        configFile.write("devConfigs = " + devicesString +"\n")
        configFile.write("# numPorts = 8")
        configFile.close()
        main.log.info("DevConfig = " + devicesString)
        main.log.info("Device provider file written and closed")

        main.log.info("Writing link graph configuration file..." )
        homeDir = os.path.expanduser('~')
        localPath = "/onos/tools/package/etc/linkGraph.cfg"
        filePath = homeDir + localPath
        linkGraph = open(filePath, 'w+')
        linkGraph.write("# NullLinkProvider topology description (config file).\n")
        linkGraph.write("# The NodeId is only added if the destination is another node's device.\n")
        linkGraph.write("# Bugs: Comments cannot be appended to a line to be read.\n")

        myPort = 6
        for node in range(1, clusterCount+1):
            linkGraph.write("graph " + ONOSIp[node] + " {\n")
            for switch in range (0, switchList[node]-1):
                line = ""
                line = ("\t" + str(switch) + ":" + str(myPort))
                line += " -- "
                line += (str(switch+1) + ":" + str(myPort-1) + "\n")
                linkGraph.write(line)
            linkGraph.write("}\n")
        linkGraph.close()

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
            if "SCC(s)=1," in clusterCheck and ("nodes=" + str(clusterCount)) in clusterCheck and ("devices=" + str(numSwitches)) in clusterCheck:  
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

        main.log.info("Cluster Count = " + str(clusterCount))

        intentsRate = main.params['METRICS']['intents_rate']
        intentsWithdrawn = main.params[ 'METRICS' ][ 'intents_withdrawn' ]
        intentsFailed  = main.params[ 'METRICS' ][ 'intents_failed' ]
        testDuration = main.params[ 'TEST' ][ 'duration' ]
        logInterval = main.params[ 'TEST' ][ 'log_interval' ]
        debug = main.params[ 'debugMode' ]

        metricList = [intentsRate, intentsWithdrawn, intentsFailed]
        
        tempsleep =40
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
       
        main.log.info( "Starting test loop for " + str(testDuration) + " seconds...\n" )
        stop = time.time() + float( testDuration )
        
        while time.time() < stop:
            time.sleep( float( logInterval ) )
            for node in range (1, clusterCount + 1):
                myResults = ['0','0','0']
                for metric in metricList: 

                    onosEnv = "onos $OC" + str(node)  
                    cmd = onosEnv + " " + metric
                    main.log.info("COMMAND: " + cmd)
                    main.ONOSbench.handle.sendline( cmd )
                    time.sleep(10)
                    main.ONOSbench.handle.expect(":~")                   
                    rawResult = main.ONOSbench.handle.before
                    rawResult = (rawResult.splitlines())

                    tempResult = "--"
                    for word in rawResult:
                        if debug: print("word: " + word)
                        if "m1" in str(word): 
                            tempResult = word
                            break

                    if tempResult == "--": 
                        main.log.error("WRONG pexepct.before data\n" + str(rawResult))
                        main.log.info("retrying command... ")
                        main.ONOSbench.handle.sendline(cmd)
                        main.ONOSbench.handle.expect(":~")
                        test = main.ONOSbench.handle.before
                        print ("\n\n" + str(test))

                    tempResult = round(float(tempResult.replace("m1=","")),1)
                    tempResult = str(tempResult)                        # easy way to clean up number/prep to log
                    resultIndex = metricList.index(metric)
                    myResults[resultIndex] = tempResult
                
                main.log.info("\tNode " + str(node))
                main.log.info("Installed\tWithdrawn\tFailed")
                main.log.info(myResults[0] + "\t\t " + myResults[1] + "\t\t" + myResults[2] + "\n")
                

