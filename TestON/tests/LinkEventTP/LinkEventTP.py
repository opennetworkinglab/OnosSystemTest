# ScaleOutTemplate --> LinkEventTP
#
# CASE1 starts number of nodes specified in param file
#
# cameron@onlab.us

import sys
import os


class LinkEventTP:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):            #This is the initialization case
        import os.path                  #this case will clean up all nodes 
                                        #but only node 1 isnodestarted in this case
        
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
        Features = main.params[ 'ENV' ][ 'cellFeatures' ]
        skipMvn = main.params[ 'TEST' ][ 'skipCleanInstall' ]
        flickerRate = main.params[ 'TEST' ][ 'flickerRate']
        MNip = main.params[ 'TEST' ][ 'MN' ]
       
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
        main.log.step("Creating cell file")
        exec "a = main.ONOSbench.createCellFile"
        cellIp = []
        for node in range (1, maxNodes + 1):
            	cellIp.append(ONOSIp[node])
        a(BENCHIp,cellName,MNip,str(Features), *cellIp)    #'0' as third arg because we are not using mininet

        main.step( "Set Cell" )
        main.ONOSbench.setCell(cellName)

        #Uninstall everywhere
        main.log.step( "Cleaning Enviornment..." )
        for i in range(1, maxNodes + 1):
            main.log.info(" Uninstalling ONOS " + str(i) )
            main.ONOSbench.onosUninstall( ONOSIp[i] )

        #git step - skipable 
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

        #configuring file to enable flicker
        main.log.step(" Configuring null provider to enable flicker. Flicker Rate = " + flickerRate )
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
        main.log.info("File opened")
        configFile.write("# Sample configurations for the NullLinkProvider.\n")
        configFile.write("# \n")
        configFile.write("# If enabled, sets time between linkEvent generation\n")
        configFile.write("# in milliseconds.\n")
        configFile.write("#\n") 
        configFile.write("eventRate = " + flickerRate)
        configFile.write("\n")
        configFile.write("#Set order of islands to chain together, in a line.\n")
        configFile.write("neighbors = " + neighborsString)
        configFile.close()
        main.log.info("Configuration completed")

        ### configure event rate file ###
        main.log.step("Writing Default Topology Provider config file")
        localPath = main.params[ 'TEST' ][ 'configFile' ]
        filePath = homeDir + localPath
        main.log.info(filePath)
        configFile = open(filePath, 'w+')
        main.log.info("File Opened")
        configFile.write("maxEvents = 1\n")
        configFile.write("maxIdleMs = 0\n")
        configFile.write("maxBatchMs = 0\n")
        main.log.info("File written and closed")
       
 
        devices_by_ip = ""
        for node in range(1, maxNodes + 1):
            devices_by_ip += (ONOSIp[node] + ":" + str(5))
            if node < maxNodes:
                devices_by_ip +=(",")
        
        main.log.step("Configuring device provider")
        localPath = "/onos/tools/package/etc/org.onosproject.provider.nil.device.impl.NullDeviceProvider.cfg"
        filePath = homeDir + localPath
        main.log.info(filePath)
        configFile = open(filePath, 'w+')
        main.log.info("Device config file opened")
        configFile.write("devConfigs = " + devices_by_ip)
        configFile.close()
        main.log.info("File closed")

        logFileName = main.params[ 'TEST' ][ 'logFile' ]
        logFile = open(logFileName, 'w+')
        main.log.info("Created log File")
        logFile.close()

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()  

        main.step( "Installing ONOS package" )
        install1Result = main.ONOSbench.onosInstall( node=ONOSIp[1] )

        main.step( "Verify cells" )
        verifyCellResult = main.ONOSbench.verifyCell()

        main.step( "Enviornment setup and verification complete." )
        main.ONOS1cli.startOnosCli( ONOSIp[1] )
        main.step( "ONOS 1 is up and running." )
	

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
            main.ONOSbench.onosInstall( ONOSIp[node] )
            exec "a = main.ONOS%scli.startOnosCli" %str(node)
            a(ONOSIp[node])
    
    def CASE3( self, main ):   
        import time
        import json
        import string 
        import csv
        import os.path


        linkResult = main.FALSE
        scale = int( main.params[ 'SCALE' ] )

        testDelay = main.params[ 'TEST' ][ 'wait']
        time.sleep( float( testDelay ) )

        metric1 = main.params[ 'TEST' ][ 'metric1' ]
        metric2 = main.params[ 'TEST' ][ 'metric2' ]
        testDuration = main.params[ 'TEST' ][ 'duration' ]
        stop = time.time() + float( testDuration )

        msg = ( "Starting test loop for " + str(testDuration) + " seconds on a " + str(clusterCount) + " node cluster" )
        main.log.info( msg )
        logInterval = main.params[ 'TEST' ][ 'log_interval' ]

        linkResults = [0,0,0,0,0,0,0,0]
        graphResults = [0,0,0,0,0,0,0,0]
        JsonStr = [ 0,0,0,0,0,0,0,0 ]
        JsonObj = [ 0,0,0,0,0,0,0,0 ]
        
        while time.time() < stop:
            time.sleep( float( logInterval ) )
            for node in range(1, clusterCount+1):
                exec "a = main.ONOS%scli.topologyEventsMetrics" %str(node)    
                JsonStr[node] = a()
                JsonObj[node] = json.loads( JsonStr[node] )
                msg = ( "Node " + str(node)  +  " Link Event TP: " + str( JsonObj[node][ metric1 ][ 'm1_rate' ] ) )
                main.log.info( msg )
                msg = ( "Node " + str(node) + " Graph Event TP: " + str( JsonObj[node][ metric2 ][ 'm1_rate' ] ) )
                main.log.info( msg )
               
                linkResults[node] = round(JsonObj[node][ metric2 ][ 'm1_rate' ],2)
                graphResults[node] = round(JsonObj[node][ metric1  ][ 'm1_rate' ],2)

        print("")
        print("")

        main.log.info("Final Link Event TP Results on " + str(clusterCount) + " node cluster")
        main.log.info("_______________________________________________")
        for node in range(1, clusterCount+1):
            main.log.info("Node " + str(node) + ": " + str(linkResults[node])) 

        print("")
        print("")

        main.log.info("Final Graph Event TP Results on " + str(clusterCount) + " node cluster")
        main.log.info("_______________________________________________")
        for node in range(1, clusterCount+1):
            main.log.info("Node " + str(node) + ": " + str(graphResults[node]))           
          
        ################################################################################# 
				# 	Data Logging

        logFileName = main.params[ 'TEST' ][ 'logFile' ]
        logFile = open(logFileName, 'a')
        main.log.info("Log file opened")
        flickerRate = main.params[ 'TEST' ][ 'flickerRate']

        for node in range (1, clusterCount + 1):
            logFile.write( str(clusterCount) + "," )
            logFile.write("'" + "baremetal" + str(node)  + "'," )
            logFile.write( testDuration + "," )
            logFile.write( flickerRate + "," )
            logFile.write( str(linkResults[node]) + "," )
            logFile.write( str(graphResults[node]) + "\n" )

        logFile.close()
        main.log.info("Log file closed")        
        
















