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
        deviceDistribution = (main.params[ 'TEST' ][ 'devicesPerNode']).split(",")    
        MNip = main.params[ 'TEST' ][ 'MN' ]
        logFileName = main.params[ 'TEST' ][ 'logFile' ]
        onBaremetal = main.params[ 'ENV' ][ 'onBaremetal' ]

        main.ONOSbench.handle.sendline("export TERM=vt100")
        main.ONOSbench.handle.expect(":~") 	    
        homeDir = os.path.expanduser('~')

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
        cellIp = []
        for node in range (1, clusterCount + 1):
            	cellIp.append(ONOSIp[node]) 
        main.ONOSbench.createCellFile(BENCHIp,cellName,MNip,str(Features), *cellIp)

        main.step( "Set Cell" )
        main.ONOSbench.setCell(cellName)

        #Uninstall everywhere
        main.log.step( "Cleaning Enviornment..." )
        for i in range(1, maxNodes + 1):
            main.log.info(" Uninstalling ONOS " + str(i) )
            main.ONOSbench.onosUninstall( ONOSIp[i] )

        myDistribution = []
        for node in range (1, clusterCount + 1): 
            myDistribution.append(deviceDistribution[node-1]) 

        main.ONOSbench.createLinkGraphFile( BENCHIp,cellIp,myDistribution) 
        main.ONOSbench.createNullDevProviderFile( BENCHIp, cellIp, myDistribution) 
        main.ONOSbench.createNullLinkProviderFile(BENCHIp)
        
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
        configFile.close()

        logFile = open(logFileName, 'w+')
        main.log.info("Created log File")
        logFile.close()

        if onBaremetal == "true":
            filename = "/onos/tools/package/bin/onos-service"
            serviceConfig = open(homeDir + filename, 'w+')
            serviceConfig.write("#!/bin/bash\n ")
            serviceConfig.write("#------------------------------------- \n ")
            serviceConfig.write("# Starts ONOS Apache Karaf container\n ")
            serviceConfig.write("#------------------------------------- \n ")
            serviceConfig.write("#export JAVA_HOME=${JAVA_HOME:-/usr/lib/jvm/java-7-openjdk-amd64/}\n ")
            serviceConfig.write("""export JAVA_OPTS="${JAVA_OPTS:--Xms256m -Xmx8G}" \n """)
            serviceConfig.write("")
            serviceConfig.write("ONOS_HOME=/opt/onos \n ")
            serviceConfig.write("")
            serviceConfig.write("[ -d $ONOS_HOME ] && cd $ONOS_HOME || ONOS_HOME=$(dirname $0)/..\n")
            serviceConfig.write("""${ONOS_HOME}/apache-karaf-$KARAF_VERSION/bin/karaf "$@" \n """)
            serviceConfig.close() 

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()  

        main.step( "Installing ONOS package" )
        install1Result = main.ONOSbench.onosInstall( node=ONOSIp[1] )

        main.step( "Verify cells" )
        verifyCellResult = main.ONOSbench.verifyCell()

        main.step( "Enviornment setup and verification complete." )
        main.ONOS1cli.startOnosCli( ONOSIp[1] )
        main.step( "ONOS 1 is up and running." )
        main.ONOSbench.handle.expect(":~") #there is a dangling sendline somewhere...	
    
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
    
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        Features= main.params[ 'ENV' ][ 'cellFeatures' ]
        BENCHIp = main.params[ 'BENCH' ][ 'ip1' ]
        MNip = main.params[ 'TEST' ][ 'MN' ]        
        deviceDistribution = (main.params[ 'TEST' ][ 'devicesPerNode']).split(",")

        scale = int( main.params[ 'SCALE' ] )
        clusterCount += scale

        main.log.step( "Cleaning Enviornment..." )
        for i in range(1, maxNodes + 1):
            main.ONOSbench.onosDie(ONOSIp[i])
            main.log.info(" Uninstalling ONOS " + str(i) )
            main.ONOSbench.onosUninstall( ONOSIp[i] )

        myDistribution = []
        for node in range (1, clusterCount + 1):
            myDistribution.append(deviceDistribution[node-1])

        main.log.step("Creating cell file")
        cellIp = []
        for node in range (1, clusterCount + 1):
                cellIp.append(ONOSIp[node])
        main.ONOSbench.createCellFile(BENCHIp,cellName,MNip,str(Features), *cellIp)

        main.ONOSbench.createLinkGraphFile( BENCHIp,cellIp,myDistribution)
        main.ONOSbench.createNullDevProviderFile( BENCHIp, cellIp, myDistribution)
        main.ONOSbench.createNullLinkProviderFile(BENCHIp)

        main.step( "Set Cell" )
        main.ONOSbench.setCell(cellName)

        main.step( "Packaging" ) 
        main.ONOSbench.onosPackage()

        main.log.report( "Increasing cluster size to " + str( clusterCount ) )
        for node in range(1, clusterCount + 1):
            time.sleep(10)
            main.log.info("Starting ONOS " + str(node) + " at IP: " + ONOSIp[node])
            main.ONOSbench.onosInstall( node=ONOSIp[node] )
            exec "a = main.ONOS%scli.startOnosCli" %str(node)
            a(ONOSIp[node])
        
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
        import json
        import string 
        import csv
        import os.path
        import requests
        import numpy

        sustainability = float(main.params[ 'TEST' ][ 'linkgraphdif' ])
        flickerRates = (main.params[ 'TEST' ][ 'flickerRates']).split(",")        
        homeDir = os.path.expanduser('~')     

        linkResult = main.FALSE
        scale = int( main.params[ 'SCALE' ] )

        testDelay = main.params[ 'TEST' ][ 'wait' ]
                
        for node in range(1, clusterCount + 1): 
            main.log.info("Writing flicker file to node " + str(node))
            main.ONOSbench.createNullLinkProviderFile( ONOSIp[node], eventRate=flickerRates[node-1], onNode=True  )     

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
                main.ONOSbench.handle.sendline("""onos $OC1 topology-events-metrics|grep "Topology Link Events"|cut -d ' ' -f7 """)
                main.ONOSbench.handle.expect(":~") 
                raw = (main.ONOSbench.handle.before).splitlines() 
                myresult = "--"
                for word in raw: 
                    if "m1" in word: 
                        myresult = word 
                        myresult = myresult.replace("m1=","")
                        break 
                if myresult == "--": 
                    main.log.error("Parse error or no data error") 
                msg = ( "Node " + str(node)  +  " Link Event TP: " + str(myresult) )
                main.log.info( msg )
                linkResults[node] = round(float(myresult),2)
                myLinkRate = round(float(myresult),2)

                main.ONOSbench.handle.sendline("""onos $OC1 topology-events-metrics|grep "Topology Graph Events"|cut -d ' ' -f7 """)
                main.ONOSbench.handle.expect(":~")
                raw = (main.ONOSbench.handle.before).splitlines()
                myresult = "--"
                for word in raw:
                    if "m1" in word:
                        myresult = word
                        myresult = myresult.replace("m1=","")
                        break
                if myresult == "--":
                    main.log.error("Parse error or no data error")
                msg = ( "Node " + str(node) + " Graph Event TP: " + str(myresult) )
                main.log.info( msg )
                graphResults[node] = round(float(myresult),2)
                myGraphRate = round(float(myresult),2)
                
                difLinkGraph = float(myLinkRate - myGraphRate)
                difLinkGraph = numpy.absolute(difLinkGraph)
                main.log.info("Node " + str(node) + " abs(Link event - Graph event) = " + str(difLinkGraph)) 
                tempx = numpy.divide(difLinkGraph,float(myLinkRate)) 
                if tempx > sustainability:
                    main.log.error("Difference in link event rate and graph event rate above " + str(sustainability) + " tolerance") 
                print("")

        print("")
        print("")

        main.log.report("Final Link Event TP Results on " + str(clusterCount) + " node cluster")
        main.log.report("_______________________________________________")
        for node in range(1, clusterCount+1):
            main.log.report("Node " + str(node) + ": " + str(linkResults[node])) 

        print("")
        print("")

        main.log.report("Final Graph Event TP Results on " + str(clusterCount) + " node cluster")
        main.log.report("_______________________________________________")
        for node in range(1, clusterCount+1):
            main.log.report("Node " + str(node) + ": " + str(graphResults[node]))           
          
        ################################################################################# 
				# 	Data Logging

        logFileName = main.params[ 'TEST' ][ 'logFile' ]
        logFile = open(logFileName, 'a')
        main.log.info("Log file opened")
        flickerRate = main.params[ 'TEST' ][ 'flickerRate']

        for node in range (1, clusterCount + 1):
            # replare ->  logFile.write( str(clusterCount) + "," + flickerNodes + "," )
            logFile.write("'" + "baremetal" + str(node)  + "'," )
            logFile.write( testDuration + "," )
            logFile.write( flickerRate + "," )
            logFile.write( str(linkResults[node]) + "," )
            logFile.write( str(graphResults[node]) + "\n" )

        logFile.close()
        main.log.info("Log file closed")        
        
















