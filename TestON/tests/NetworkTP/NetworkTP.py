# ScaleOutTemplate --> NetworkTP
#
# CASE1 starts number of nodes specified in param file
#
# cameron@onlab.us

import sys
import os


class NetworkTP:

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

        testDelay = main.params[ 'TEST' ][ 'wait']
        time.sleep( float( testDelay ) )

        getMetric = main.params[ 'TEST' ][ 'metric1' ]
        testDuration = main.params[ 'TEST' ][ 'duration' ]
        stop = time.time() + float( testDuration )
    
        main.ONOS1cli.featureInstall("onos-null")

        msg = ( "Starting test loop for " + str(testDuration) + " seconds" )
        main.log.info( msg )
        logInterval = main.params[ 'TEST' ][ 'log_interval' ]

        while time.time() < stop:
            time.sleep( float( logInterval ) )

            intentsJsonStr1 = main.ONOS1cli.topologyEventsMetrics() 
            intentsJsonObj1 = json.loads( intentsJsonStr1 ) 
            msg = ( "Node 1 TP: " + str( intentsJsonObj1[ getMetric  ][ 'm1_rate' ] ) )
            main.log.info( msg ) 
            lastRate1 = intentsJsonObj1[ getMetric  ][ 'm1_rate' ]

        msg = ( "Final TP on node 1: " + str( lastRate1 ) )
        main.log.report( msg )


    def CASE4( self, main ):
        import time
        import json
        import string

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

            intentsJsonStr1 = main.ONOS1cli.topologyEventsMetrics() 
            intentsJsonObj1 = json.loads( intentsJsonStr1 )
            msg = ( "Node 1 TP: " + str( intentsJsonObj1[ getMetric  ][ 'm1_rate' ] ) )
            main.log.info( msg )
            lastRate1 = intentsJsonObj1[ getMetric  ][ 'm1_rate' ]


            intentsJsonStr2 = main.ONOS2cli.topologyEventsMetrics() 
            intentsJsonObj2 = json.loads( intentsJsonStr2 )
            msg = ( "Node 2 TP: " + str( intentsJsonObj2[ getMetric  ][ 'm1_rate' ] ) )
            main.log.info( msg )
            lastRate2 = intentsJsonObj2[ getMetric  ][ 'm1_rate' ]


        msg = ( "Final TP on node 1: " + str( lastRate1 ) )
        main.log.report( msg )

        msg = ( "Final TP on node 2: " + str( lastRate2 ) )
        main.log.report( msg )

    def CASE5( self, main ):
        import time
        import json
        import string

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

            intentsJsonStr1 = main.ONOS1cli.topologyEventsMetrics()
            intentsJsonObj1 = json.loads( intentsJsonStr1 )
            msg = ( "Node 1 TP: " + str( intentsJsonObj1[ getMetric  ][ 'm1_rate' ] ) )
            main.log.info( msg )
            lastRate1 = intentsJsonObj1[ getMetric  ][ 'm1_rate' ]


            intentsJsonStr2 = main.ONOS2cli.topologyEventsMetrics()
            intentsJsonObj2 = json.loads( intentsJsonStr2 )
            msg = ( "Node 2 TP: " + str( intentsJsonObj2[ getMetric  ][ 'm1_rate' ] ) )
            main.log.info( msg )
            lastRate2 = intentsJsonObj2[ getMetric  ][ 'm1_rate' ]
    
            intentsJsonStr3 = main.ONOS3cli.topologyEventsMetrics()
            intentsJsonObj3 = json.loads( intentsJsonStr3 )
            msg = ( "Node 3 TP: " + str( intentsJsonObj3[ getMetric  ][ 'm1_rate' ] ) )
            main.log.info( msg )
            lastRate3 = intentsJsonObj3[ getMetric  ][ 'm1_rate' ]

        msg = ( "Final TP on node 1: " + str( lastRate1 ) )
        main.log.report( msg )

        msg = ( "Final TP on node 2: " + str( lastRate2 ) )
        main.log.report( msg )

        msg = ( "Final TP on node 3: " + str( lastRate3 ) )
        main.log.report( msg )



