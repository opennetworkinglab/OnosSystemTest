# ScaleOutTemplate --> IntentsLoad
#
# CASE1 starts number of nodes specified in param file
#
# cameron@onlab.us

import sys
import os


class IntentsLoad:

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
              
        if scale == 1:
            if clusterCount == 2:
                main.log.info( "Installing node 2" )
                install2Result = main.ONOSbench.onosInstall( node=ONOS2Ip )
                cli2 = main.ONOS2cli.startOnosCli( ONOS2Ip )

            if clusterCount == 3:
                main.log.info( "Installing node 3" )
                install3Result = main.ONOSbench.onosInstall( node=ONOS3Ip )
                cli3 = main.ONOS3cli.startOnosCli( ONOS3Ip )

    def CASE3( self, main ):
        import time
        import json
        import string

        intentsRate = main.params[ 'JSON' ][ 'intents_rate' ]

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

        generateLoad = main.params[ 'TEST' ][ 'loadstart' ]

        main.ONOS1.handle.sendline( generateLoad )
        main.ONOS1.handle.expect( "sdn" )
        print( "before: ", main.ONOS1.handle.before )
        print( "after: ", main.ONOS1.handle.after )

        loadConfirm = main.ONOS1.handle.after
        if loadConfirm == "{}":
            main.log.info( "Load started" )

        else:
            main.log.error( "Load start failure" )
            main.log.error( "expected '{}', got: " + str( loadConfirm ) )

        devicesJsonStr = main.ONOS1cli.devices()
        devicesJsonObj = json.loads( devicesJsonStr )

        getMetric = main.params[ 'TEST' ][ 'metric1' ]
        testDuration = main.params[ 'TEST' ][ 'duration' ]
        stop = time.time() + float( testDuration )

        main.log.info( "Starting test loop..." )
        logInterval = main.params[ 'TEST' ][ 'log_interval' ]

        while time.time() < stop:
            time.sleep( float( logInterval ) )

            intentsJsonStr1 = main.ONOS1cli.intentsEventsMetrics()
            intentsJsonObj1 = json.loads( intentsJsonStr1 )
            main.log.info( "Node 1 rate: " +
                           str( intentsJsonObj1[ intentsRate ][ 'm1_rate' ] ) )
            lastRate1 = intentsJsonObj1[ intentsRate ][ 'm1_rate' ]

        stopLoad = main.params[ 'TEST' ][ 'loadstop' ]
        main.ONOS1.handle.sendline( stopLoad )

        msg = ( "Final rate on node 1: " + str( lastRate1 ) )
        main.log.report( msg )

    def CASE4( self, main ):  # 2 node scale
        import time
        import json
        import string

        intentsRate = main.params[ 'JSON' ][ 'intents_rate' ]

        defaultSwPort = main.params[ 'CTRL' ][ 'port1' ]

        main.Mininet1.assignSwController(
            sw="1",
            ip1=ONOS1Ip,
            port1=defaultSwPort )
        main.Mininet1.assignSwController(
            sw="2",
            ip1=ONOS2Ip,
            port1=defaultSwPort )
        main.Mininet1.assignSwController(
            sw="3",
            ip1=ONOS1Ip,
            port1=defaultSwPort )
        main.Mininet1.assignSwController(
            sw="4",
            ip1=ONOS2Ip,
            port1=defaultSwPort )
        main.Mininet1.assignSwController(
            sw="5",
            ip1=ONOS1Ip,
            port1=defaultSwPort )
        main.Mininet1.assignSwController(
            sw="6",
            ip1=ONOS2Ip,
            port1=defaultSwPort )
        main.Mininet1.assignSwController(
            sw="7",
            ip1=ONOS1Ip,
            port1=defaultSwPort )

        mnArp = main.params[ 'TEST' ][ 'arping' ]
        main.Mininet1.handle.sendline( mnArp )

        generateLoad = main.params[ 'TEST' ][ 'loadstart' ]

        main.ONOS1.handle.sendline( generateLoad )
        main.ONOS2.handle.sendline( generateLoad )

        devicesJsonStr1 = main.ONOS1cli.devices()
        devicesJsonObj1 = json.loads( devicesJsonStr1 )
        devicesJsonStr2 = main.ONOS2cli.devices()
        devicesJsonObj2 = json.loads( devicesJsonStr2 )

        getMetric = main.params[ 'TEST' ][ 'metric1' ]
        testDuration = main.params[ 'TEST' ][ 'duration' ]
        stop = time.time() + float( testDuration )

        main.log.info( "Starting test loop..." )
        logInterval = main.params[ 'TEST' ][ 'log_interval' ]

        while time.time() < stop:
            time.sleep( float( logInterval ) )

            intentsJsonStr1 = main.ONOS1cli.intentsEventsMetrics()
            intentsJsonObj1 = json.loads( intentsJsonStr1 )
            main.log.info( "Node 1 rate: " +
                           str( intentsJsonObj1[ intentsRate ][ 'm1_rate' ] ) )
            lastRate1 = intentsJsonObj1[ intentsRate ][ 'm1_rate' ]

            intentsJsonStr2 = main.ONOS2cli.intentsEventsMetrics()
            intentsJsonObj2 = json.loads( intentsJsonStr2 )
            main.log.info( "Node 2 rate: " +
                           str( intentsJsonObj2[ intentsRate ][ 'm1_rate' ] ) )
            lastRate2 = intentsJsonObj2[ intentsRate ][ 'm1_rate' ]

        stopLoad = main.params[ 'TEST' ][ 'loadstop' ]
        main.ONOS1.handle.sendline( stopLoad )
        main.ONOS2.handle.sendline( stopLoad )

        msg = ( "Final rate on node 1: " + str( lastRate1 ) )
        main.log.report( msg )

        msg = ( "Final rate on node 2: " + str( lastRate2 ) )
        main.log.report( msg )


    
    def CASE5( self, main ):  # 2 node scale
        import time
        import json
        import string

        intentsRate = main.params[ 'JSON' ][ 'intents_rate' ]

        defaultSwPort = main.params[ 'CTRL' ][ 'port1' ]

        main.Mininet1.assignSwController(
            sw="1",
            ip1=ONOS1Ip,
            port1=defaultSwPort )
        main.Mininet1.assignSwController(
            sw="2",
            ip1=ONOS2Ip,
            port1=defaultSwPort )
        main.Mininet1.assignSwController(
            sw="3",
            ip1=ONOS3Ip,
            port1=defaultSwPort )
        main.Mininet1.assignSwController(
            sw="4",
            ip1=ONOS1Ip,
            port1=defaultSwPort )
        main.Mininet1.assignSwController(
            sw="5",
            ip1=ONOS2Ip,
            port1=defaultSwPort )
        main.Mininet1.assignSwController(
            sw="6",
            ip1=ONOS3Ip,
            port1=defaultSwPort )
        main.Mininet1.assignSwController(
            sw="7",
            ip1=ONOS1Ip,
            port1=defaultSwPort )

        mnArp = main.params[ 'TEST' ][ 'arping' ]
        main.Mininet1.handle.sendline( mnArp )

        generateLoad = main.params[ 'TEST' ][ 'loadstart' ]

        main.ONOS1.handle.sendline( generateLoad )
        main.ONOS2.handle.sendline( generateLoad )
        main.ONOS3.handle.sendline( generateLoad )        

        devicesJsonStr1 = main.ONOS1cli.devices()
        devicesJsonObj1 = json.loads( devicesJsonStr1 )
        devicesJsonStr2 = main.ONOS2cli.devices()
        devicesJsonObj2 = json.loads( devicesJsonStr2 )
        devicesJsonStr3 = main.ONOS3cli.devices()
        devicesJsonObj3 = json.loads( devicesJsonStr3 )

        getMetric = main.params[ 'TEST' ][ 'metric1' ]
        testDuration = main.params[ 'TEST' ][ 'duration' ]
        stop = time.time() + float( testDuration )

        main.log.info( "Starting test loop..." )
        logInterval = main.params[ 'TEST' ][ 'log_interval' ]

        while time.time() < stop:
            time.sleep( float( logInterval ) )

            intentsJsonStr1 = main.ONOS1cli.intentsEventsMetrics()
            intentsJsonObj1 = json.loads( intentsJsonStr1 )
            main.log.info( "Node 1 rate: " +
                           str( intentsJsonObj1[ intentsRate ][ 'm1_rate' ] ) )
            lastRate1 = intentsJsonObj1[ intentsRate ][ 'm1_rate' ]

            intentsJsonStr2 = main.ONOS2cli.intentsEventsMetrics()
            intentsJsonObj2 = json.loads( intentsJsonStr2 )
            main.log.info( "Node 2 rate: " +
                           str( intentsJsonObj2[ intentsRate ][ 'm1_rate' ] ) )
            lastRate2 = intentsJsonObj2[ intentsRate ][ 'm1_rate' ]

            intentsJsonStr3 = main.ONOS3cli.intentsEventsMetrics()
            intentsJsonObj3 = json.loads( intentsJsonStr3 )
            main.log.info( "Node 3 rate: " +
                           str( intentsJsonObj3[ intentsRate ][ 'm1_rate' ] ) )
            lastRate3 = intentsJsonObj3[ intentsRate ][ 'm1_rate' ]

        stopLoad = main.params[ 'TEST' ][ 'loadstop' ]
        main.ONOS1.handle.sendline( stopLoad )
        main.ONOS2.handle.sendline( stopLoad )
        main.ONOS3.handle.sendline( stopLoad )

        msg = ( "Final rate on node 1: " + str( lastRate1 ) )
        main.log.report( msg )

        msg = ( "Final rate on node 2: " + str( lastRate2 ) )
        main.log.report( msg )

        msg = ( "Final rate on node 3: " + str( lastRate3 ) )
        main.log.report( msg )


    
