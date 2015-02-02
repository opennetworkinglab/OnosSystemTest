# ScaleOutTemplate
#
# CASE1 starts number of nodes specified in param file
#
# cameron@onlab.us

import sys
import os


class pushTestIntents:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):

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

        # Cluster size increased everytime the case is run
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
                cli2 = main.ONOS2cli.startOnosCli(ONOS2_ip)

            if clusterCount == 3:
                main.log.info( "Installing node 3" )
                install3Result = main.ONOSbench.onosInstall( node=ONOS3Ip )
                cli3 = main.ONOS3cli.startOnosCli(ONOS3_ip)


    def CASE3( self, main ):

        import subprocess 
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        defaultSwPort = main.params[ 'CTRL' ][ 'port1' ]

        main.Mininet1.assignSwController(
            sw="1",
            ip1=ONOS1Ip,
            port1=defaultSwPort )
        main.Mininet1.assignSwController(
            sw="2",
            ip1=ONOS1Ip,
            port1=defaultSwPort )
        main.Mininet1.assignSwController(
            sw="3",
            ip1=ONOS1Ip,
            port1=defaultSwPort )
        main.Mininet1.assignSwController(
            sw="4",
            ip1=ONOS1Ip,
            port1=defaultSwPort )
        main.Mininet1.assignSwController(
            sw="5",
            ip1=ONOS1Ip,
            port1=defaultSwPort )
        main.Mininet1.assignSwController(
            sw="6",
            ip1=ONOS1Ip,
            port1=defaultSwPort )
        main.Mininet1.assignSwController(
            sw="7",
            ip1=ONOS1Ip,
            port1=defaultSwPort )

        mnArp = main.params[ 'TEST' ][ 'arping' ]
        main.Mininet1.handle.sendline( mnArp ) 

        getMetric = main.params[ 'TEST' ][ 'metric1' ]
        
        batch = main.params[ 'TEST' ][ 'batch' ]
        batchSize = batch.split(",")
        iterations = main.params[ 'TEST' ][ 'cycles' ]

        for size in batchSize:
            commandString = """ "onos """ + ONOS1Ip + " '" + getMetric + " "  + size + "'" + """" """ 
            output = subprocess.check_output(commandString,shell=True)
            outjson=json.loads(output) 
            print outjson 



















       
