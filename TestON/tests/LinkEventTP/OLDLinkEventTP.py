# ScaleOutTemplate --> LinkEventTp
#
# CASE1 starts number of nodes specified in param file
#
# cameron@onlab.us

import sys
import os


class LinkEventTP:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        import os.path
        global clusterCount
        clusterCount = 1

        checkoutBranch = main.params[ 'GIT' ][ 'checkout' ]
        gitPull = main.params[ 'GIT' ][ 'autopull' ]
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        BENCHIp = main.params[ 'BENCH' ][ 'ip1' ]
        BENCHUser = main.params[ 'BENCH' ][ 'user' ]
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS2Ip = main.params[ 'CTRL' ][ 'ip2' ]
        ONOS3Ip = main.params[ 'CTRL' ][ 'ip3' ]
        flickerRate = main.params[ 'TEST' ][ 'flickerRate']
        

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
        
        ### configuring file to enable flicker ###
        main.log.info(" Configuring null provider to enable flicker. Flicker Rate = " + flickerRate ) 
        homeDir = os.path.expanduser('~')
        main.log.info(homeDir)
        localPath = "/ONOS/tools/package/etc/org.onosproject.provider.nil.link.impl.NullLinkProvider.cfg"
        filePath = homeDir + localPath
        main.log.info(filePath)

        configFile = open(filePath, 'w+')
        main.log.info("File opened")
        configFile.write("# Sample configurations for the NullLinkProvider.\n")
        configFile.write("# \n")
        configFile.write("# If enabled, generates LinkDetected and LinkVanished events\n")
        configFile.write("# to make the link appear to be flapping.\n")
        configFile.write("#\n")
        configFile.write("flicker = true\n")
        configFile.write("#\n")
        configFile.write("# If enabled, sets the time between LinkEvent generation,\n")
        configFile.write("# in milliseconds.\n")
        configFile.write("#\n")
        configFile.write("eventRate = " + flickerRate)
        configFile.close()
        main.log.info("Configuration completed")
        
        #############################
        #config file default topo provider 
        ###########################

        ### configure deafult topo provider event rate ###??????????????????
        localPath = main.params[ 'TEST' ][ 'configFile' ]
        filePath = homeDir + localPath
        main.log.info(filePath)
        configFile = open(filePath, 'w+')
        main.log.info("File Opened")
        configFile.write("maxEvents = 1\n") 
        configFile.write("maxIdleMs = 0\n")
        configFile.write("maxBatchMs = 0\n")
        main.log.info("File written and closed") 

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()  # no file or directory

        main.step( "Installing ONOS package" )
        install1Result = main.ONOSbench.onosInstall( node=ONOS1Ip )

        cellName = main.params[ 'ENV' ][ 'cellName' ]
        main.step( "Applying cell file to environment" )
        cellApplyResult = main.ONOSbench.setCell( cellName )
        main.step( "verify cells" )
        verifyCellResult = main.ONOSbench.verifyCell()

        main.step( "Set cell for ONOS cli env" )
        main.ONOS1cli.setCell( cellName )

        cli1 = main.ONOS1cli.startOnosCli( ONOS1Ip )

    def CASE2( self, main ):
        """
        Increase number of nodes and initiate CLI
        """
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
                cli2 = main.ONOS2cli.startOnosCli( ONOS2Ip )
                cli3 = main.ONOS3cli.startOnosCli( ONOS3Ip )
                installResult = main.TRUE 
              
        if scale == 1:
            if clusterCount == 2:
                main.log.info( "Installing node 2" )
                install2Result = main.ONOSbench.onosInstall( node=ONOS2Ip )
                cli2 = main.ONOS2cli.startOnosCli( ONOS2Ip )
                installResult = main.TRUE 

            if clusterCount == 3:
                main.log.info( "Installing node 3" )
                install3Result = main.ONOSbench.onosInstall( node=ONOS3Ip )
                cli3 = main.ONOS3cli.startOnosCli( ONOS3Ip )
                installResult = main.TRUE 


    def CASE3( self, main ):
        import time
        import json
        import string
        import csv
        
        linkResult = main.FALSE 
        
        testDelay = main.params[ 'TEST' ][ 'wait']
        time.sleep( float( testDelay ) )

        metric1 = main.params[ 'TEST' ][ 'metric1' ]
        metric2 = main.params[ 'TEST' ][ 'metric2' ]
        testDuration = main.params[ 'TEST' ][ 'duration' ]
        stop = time.time() + float( testDuration )
    
        main.ONOS1cli.featureInstall("onos-null")

        msg = ( "Starting test loop for " + str(testDuration) + " seconds" )
        main.log.info( msg )
        logInterval = main.params[ 'TEST' ][ 'log_interval' ]

        while time.time() < stop:
            time.sleep( float( logInterval ) )

            JsonStr1 = main.ONOS1cli.topologyEventsMetrics() 
            JsonObj1 = json.loads( JsonStr1 ) 
            msg = ( "Node 1 Link Event TP: " + str( JsonObj1[ metric1  ][ 'm1_rate' ] ) )
            main.log.info( msg )
            msg = ( "Node 1 Graph Event TP: " + str( JsonObj1[ metric2  ][ 'm1_rate' ] ) )
            main.log.info( msg ) 
            
            lastGraphRate = round(JsonObj1[ metric2 ][ 'm1_rate' ],2)
            lastLinkRate = round(JsonObj1[ metric1  ][ 'm1_rate' ],2)

        msg = ( "Final Link Event TP: " + str( lastLinkRate ) ) 
        main.log.report( msg )
        msg = ( "Final Graph Event TP: " + str( lastGraphRate ) )
        main.log.report( msg )
       
        linkResult = main.TRUE 
        '''
        jenkinsReport = open('LinkEventTP.csv', 'w')
        jenkinsReport.write("T1 - Node 1, T2 - Node 1, T2 - Node 2, T3 - Node 1, T3 - Node 2, T3 - Node 3\n")
        jenkinsReport.write(str(lastRate1))
        jenkinsReport.write("\n")
        jenkinsReport.close()
        
        dbReportS1 = open('LinkEventTP-S1.csv','w')         #must be the name of the test "-S" followed by the scale 
        dbReportS1.write(str(linkResult))
        dbReportS1.write("\n")
        dbReportS1.write(str(lastRate1))
        dbReportS1.write("\n")                              #additional newline needed for bash script reading
        dbReportS1.close()
        '''


    def CASE4( self, main ):
        import time
        import json
        import string

        linkResult = main.FALSE

        testDelay = main.params[ 'TEST' ][ 'wait']
        time.sleep( float( testDelay ) )

        getMetric = main.params[ 'TEST' ][ 'metric1' ]
        testDuration = main.params[ 'TEST' ][ 'duration' ]
        stop = time.time() + float( testDuration )

        main.ONOS2cli.featureInstall("onos-null")

        msg = ( "Starting test loop for " + str(testDuration) + " seconds" )
        main.log.info( msg )
        logInterval = main.params[ 'TEST' ][ 'log_interval' ]

        while time.time() < stop:
            time.sleep( float( logInterval ) )

            JsonStr1 = main.ONOS1cli.topologyEventsMetrics() 
            JsonObj1 = json.loads( JsonStr1 )
            msg = ( "Node 1 TP: " + str( JsonObj1[ getMetric  ][ 'm1_rate' ] ) )
            main.log.info( msg )
            lastRate1 = round(JsonObj1[ getMetric  ][ 'm1_rate' ],2)


            JsonStr2 = main.ONOS2cli.topologyEventsMetrics() 
            JsonObj2 = json.loads( JsonStr2 )
            msg = ( "Node 2 TP: " + str( JsonObj2[ getMetric  ][ 'm1_rate' ] ) )
            main.log.info( msg )
            lastRate2 = round(JsonObj2[ getMetric  ][ 'm1_rate' ],2)


        msg = ( "Final TP on node 1: " + str( lastRate1 ) )
        main.log.report( msg )

        msg = ( "Final TP on node 2: " + str( lastRate2 ) )
        main.log.report( msg )

        linkResult = main.TRUE

        jenkinsReport = open('LinkEventTP.csv', 'a')
        jenkinsReport.write(str(lastRate1))
        jenkinsReport.write(", ")
        jenkinsReport.write(str(lastRate2))
        jenkinsReport.write(", ")
        jenkinsReport.close()

        dbReportS2 = open('LinkEventTP-S2.csv','w')         #must be the name of the test "-S" followed by the scale
        dbReportS2.write(str(linkResult))
        dbReportS2.write("\n")
        dbReportS2.write(str(lastRate1))
        dbReportS2.write("\n")
        dbReportS2.write(str(lastRate2))
        dbReportS2.write("\n")
        dbReportS2.close()



    def CASE5( self, main ):
        import time
        import json
        import string

        linkResult = main.FALSE

        testDelay = main.params[ 'TEST' ][ 'wait']
        time.sleep( float( testDelay ) )

        getMetric = main.params[ 'TEST' ][ 'metric1' ]
        testDuration = main.params[ 'TEST' ][ 'duration' ]
        stop = time.time() + float( testDuration )

        main.ONOS3cli.featureInstall("onos-null")

        msg = ( "Starting test loop for " + str(testDuration) + " seconds" )
        main.log.info( msg )
        logInterval = main.params[ 'TEST' ][ 'log_interval' ]

        while time.time() < stop:
            time.sleep( float( logInterval ) )

            JsonStr1 = main.ONOS1cli.topologyEventsMetrics()
            JsonObj1 = json.loads( JsonStr1 )
            msg = ( "Node 1 TP: " + str( JsonObj1[ getMetric  ][ 'm1_rate' ] ) )
            main.log.info( msg )
            lastRate1 = round(JsonObj1[ getMetric  ][ 'm1_rate' ],2)

            JsonStr2 = main.ONOS2cli.topologyEventsMetrics()
            JsonObj2 = json.loads( JsonStr2 )
            msg = ( "Node 2 TP: " + str( JsonObj2[ getMetric  ][ 'm1_rate' ] ) )
            main.log.info( msg )
            lastRate2 = round(JsonObj2[ getMetric  ][ 'm1_rate' ],2)
    
            JsonStr3 = main.ONOS3cli.topologyEventsMetrics()
            JsonObj3 = json.loads( JsonStr3 )
            msg = ( "Node 3 TP: " + str( JsonObj3[ getMetric  ][ 'm1_rate' ] ) )
            main.log.info( msg )
            lastRate3 = round(JsonObj3[ getMetric  ][ 'm1_rate' ],2)

        msg = ( "Final TP on node 1: " + str( lastRate1 ) )
        main.log.report( msg )

        msg = ( "Final TP on node 2: " + str( lastRate2 ) )
        main.log.report( msg )

        msg = ( "Final TP on node 3: " + str( lastRate3 ) )
        main.log.report( msg )

        linkResult = main.TRUE

        jenkinsReport = open('LinkEventTP.csv', 'a')
        jenkinsReport.write(str(lastRate1))
        jenkinsReport.write(", ")
        jenkinsReport.write(str(lastRate2))
        jenkinsReport.write(", ")
        jenkinsReport.write(str(lastRate3))
        jenkinsReport.close()
       
        dbReportS3 = open('LinkEventTP-S3.csv','w')         #must be the name of the test "-S" followed by the scale
        dbReportS3.write(str(linkResult))
        dbReportS3.write("\n")
        dbReportS3.write(str(lastRate1))
        dbReportS3.write("\n")
        dbReportS3.write(str(lastRate2))
        dbReportS3.write("\n")
        dbReportS3.write(str(lastRate3))
        dbReportS3.write("\n")
        dbReportS3.close() 


