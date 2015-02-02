# ScaleOutTemplate -> NullProviderTest
#
# CASE1 starts number of nodes specified in param file
#
# cameron@onlab.us


class IntentEventTP:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        import os.path
        global clusterCount
        global ONOSIp
        clusterCount = 1
        ONOSIp = []
        checkoutBranch = main.params[ 'GIT' ][ 'checkout' ]
        gitPull = main.params[ 'GIT' ][ 'autopull' ]
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        BENCHIp = main.params[ 'BENCH' ][ 'ip1' ]
        BENCHUser = main.params[ 'BENCH' ][ 'user' ]
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOSIp.append(ONOS1Ip)
        ONOS2Ip = main.params[ 'CTRL' ][ 'ip2' ]
        ONOSIp.append(ONOS2Ip)
        ONOS3Ip = main.params[ 'CTRL' ][ 'ip3' ]
        ONOSIp.append(ONOS3Ip)
        MN1Ip = main.params[ 'MN' ][ 'ip1' ]
        Features= main.params[ 'ENV' ][ 'cellFeatures' ]
        

        main.ONOSbench.createCellFile(BENCHIp, cellName, MN1Ip,str(Features), ONOS1Ip, ONOS2Ip, ONOS3Ip)

        main.log.step( "Cleaning Enviornment..." )
        main.ONOSbench.onosUninstall( ONOS1Ip )
        main.ONOSbench.onosUninstall( ONOS2Ip )
        main.ONOSbench.onosUninstall( ONOS3Ip )

        main.step( "Git checkout and pull " + checkoutBranch )
        if gitPull == 'on':
            checkoutResult = main.ONOSbench.gitCheckout( checkoutBranch )
            pullResult = main.ONOSbench.gitPull()

        else:
            checkoutResult = main.TRUE
            pullResult = main.TRUE
            main.log.info( "Skipped git checkout and pull" )

        #mvnResult = main.ONOSbench.cleanInstall()

        main.step( "Set cell for ONOS cli env" )
        main.ONOS1cli.setCell( cellName )
        main.ONOS2cli.setCell( cellName )
        main.ONOS3cli.setCell( cellName )

        main.log.info("Modifying org.onosproject.provider.nil.link.impl.NullLinkProvider.cfg: Turning off flicker ")
        homeDir = os.path.expanduser('~')
        main.log.info(homeDir)
        localPath = "/ONOS/tools/package/etc/org.onosproject.provider.nil.link.impl.NullLinkProvider.cfg"
        filePath = homeDir + localPath
        main.log.info(filePath)

        configFile = open(filePath, 'w+')
        main.log.info("file opened")
        configFile.write("# Sample configurations for the NullLinkProvider.\n")
        configFile.write("# \n")
        configFile.write("# If enabled, generates LinkDetected and LinkVanished events\n")
        configFile.write("# to make the link appear to be flapping.\n")
        configFile.write("#\n")
        configFile.write("# flicker = true\n")
        configFile.write("#\n")
        configFile.write("# If enabled, sets the time between LinkEvent generation,\n")
        configFile.write("# in milliseconds.\n")
        configFile.write("#\n")
        configFile.write("# eventRate = 2000\n")

        configFile.close()
        main.log.info("Closing config file")

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()  

        main.step( "Installing ONOS package" )
        install1Result = main.ONOSbench.onosInstall( node=ONOS1Ip )

        cellName = main.params[ 'ENV' ][ 'cellName' ]
        main.step( "Applying cell file to environment" )
        cellApplyResult = main.ONOSbench.setCell( cellName )
        main.step( "verify cells" )
        verifyCellResult = main.ONOSbench.verifyCell()

        main.step( "Set cell for ONOS cli env" )
        cli1 = main.ONOS1cli.startOnosCli( ONOS1Ip )

        ###### UPGRADE FOR SCALABLILTY ######
        jenkinsReport = open('IntentEventTP.csv', 'w')
        jenkinsReport.write("T1 - Node 1, T2 - Node 1, T2 - Node 2, T3 - Node 1, T3 - Node 2, T3 - Node 3\n")
        jenkinsReport.close 
        #####################################

    def CASE2( self, main ):
        ''
        'Increase number of nodes and initiate CLI'
        ''
        import time

        global clusterCount

        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS2Ip = main.params[ 'CTRL' ][ 'ip2' ]
        ONOS3Ip = main.params[ 'CTRL' ][ 'ip3' ]
        #ONOS4Ip = main.params[ 'CTRL' ][ 'ip4' ]
        #ONOS5Ip = main.params[ 'CTRL' ][ 'ip5' ]
        #ONOS6Ip = main.params[ 'CTRL' ][ 'ip6' ]
        #ONOS7Ip = main.params[ 'CTRL' ][ 'ip7' ]
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        scale = int( main.params[ 'SCALE' ] )

        # Cluster size increased everytime the case is defined
        clusterCount += scale

        main.log.report( "Increasing cluster size to " +
                         str( clusterCount ) )
        installResult = main.FALSE

        if scale == 2:
            if clusterCount == 3:
                main.log.info( "Installing nodes 2 and 3" )
                install2Result = main.ONOSbench.onosInstall( node=ONOS2Ip )
                install3Result = main.ONOSbench.onosInstall( node=ONOS3Ip )
                cli2 = main.ONOS2cli.startOnosCli(ONOS2Ip)
                cli3 = main.ONOS3cli.startOnosCli(ONOS3Ip)

            
            #elif clusterCount == 5:

            #    main.log.info( "Installing nodes 4 and 5" )
            #    node4Result = main.ONOSbench.onosInstall( node=ONOS4Ip )
            #    node5Result = main.ONOSbench.onosInstall( node=ONOS5Ip )
            #    installResult = node4Result and node5Result
            #    time.sleep( 5 )

            #    main.ONOS4cli.startOnosCli( ONOS4Ip )
            #    main.ONOS5cli.startOnosCli( ONOS5Ip )

            #elif clusterCount == 7:

            #    main.log.info( "Installing nodes 4 and 5" )
            #    node6Result = main.ONOSbench.onosInstall( node=ONOS6Ip )
            #    node7Result = main.ONOSbench.onosInstall( node=ONOS7Ip )
            #    installResult = node6Result and node7Result
            #    time.sleep( 5 )
    
            #    main.ONOS6cli.startOnosCli( ONOS6Ip )
            #    main.ONOS7cli.startOnosCli( ONOS7Ip )
            #

        if scale == 1:
            if clusterCount == 2:
                main.log.info( "Installing node 2" )
                install2Result = main.ONOSbench.onosInstall( node=ONOS2Ip )
                cli2 = main.ONOS2cli.startOnosCli(ONOS2Ip)

            if clusterCount == 3: main.log.info( "Installing node 3" )
            install3Result = main.ONOSbench.onosInstall( node=ONOS3Ip ) 
            cli3 = main.ONOS3cli.startOnosCli(ONOS3Ip)


    def CASE3( self, main ): 
        
        import os.path 
        import sys
        import json
        import time          
        
        main.log.info("Cluster Count = " + str(clusterCount))

        defaultSwPort = main.params[ 'CTRL' ][ 'port1' ]
        intentsRate = main.params['JSON']['intents_rate']        
        
        for i in range( 0,clusterCount ):       #iterates over nodes 
            switchNum = i
            while switchNum < 7:                #iterates over applicable  switches
                main.Mininet1.assignSwController(sw = switchNum + 1, ip1 = ONOSIp[i], port1 = defaultSwPort)
                main.log.info("ONOS " + str(i + 1) + " assigned switch : " + str(switchNum+1))   
                switchNum += clusterCount

        main.log.info("running arping")
        mnArp = main.params['TEST']['arping'] 
        main.Mininet1.handle.sendline( mnArp )

        generateLoad = main.params[ 'TEST' ][ 'loadstart' ]

        for node in range(1, clusterCount+1):
            exec "a = main.ONOS%s.handle.sendline" %str(node)
            a(generateLoad)
            main.log.info("Load initiated on node " + str(node)) 

        #
        #       TODO: Confirm Load somehow 
        #
        
        getMetric = main.params[ 'TEST' ][ 'metric1' ]
        testDuration = main.params[ 'TEST' ][ 'duration' ]
        stop = time.time() + float( testDuration )

        main.log.info( "Starting test loop for " + str(testDuration) + " seconds..." )
        logInterval = main.params[ 'TEST' ][ 'log_interval' ]


        rateResult = [0,0,0,0,0,0,0,0]
        while time.time() < stop:
            time.sleep( float( logInterval ) )
            for node in range (1, clusterCount + 1):
                exec "a = main.ONOS%scli.intentsEventsMetrics" %str(node)
                intentsJsonObj = json.loads(a())
   
                main.log.info( "Node " + str(node) + " rate: " + str( intentsJsonObj[ intentsRate ][ 'm1_rate' ] ) )
                rateResult[node] = round(intentsJsonObj[ intentsRate ][ 'm1_rate' ], 2)
                
        stopLoad = main.params[ 'TEST' ][ 'loadstop' ]
       
        jenkinsReport = open('IntentEventTP.csv', 'a')
        for node in range(1, clusterCount + 1):
            main.log.report("Cluster Size = " + str(clusterCount) + "        Final on node " + str(node) + ": " + str(rateResult[node]))
            exec "a = main.ONOS%s.handle.sendline" %str(node)
            a(stopLoad)
            jenkinsReport.write(str(rateResult[node]))
            jenkinsReport.write(", ")
        jenkinsReport.close()
        









