# Testing the functionality of SDN-IP with single ONOS instance
class SDNIPfunction:

    def __init__( self ):
        self.default = ''
        global branchName


    # This case is to setup ONOS
    def CASE100( self, main ):
        """
           CASE100 is to compile ONOS and install it
           Startup sequence:
           cell <name>
           onos-verify-cell
           git pull
           mvn clean install
           onos-package
           onos-install -f
           onos-wait-for-start
        """
        main.case( "Setting up test environment" )

        cellName = main.params[ 'ENV' ][ 'cellName' ]
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]

        main.step( "Applying cell variable to environment" )
        cellResult = main.ONOSbench.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()

        branchName = main.ONOSbench.getBranchName()
        main.log.info( "ONOS is on branch: " + branchName )

        main.log.report( "Uninstalling ONOS" )
        main.ONOSbench.onosUninstall( ONOS1Ip )

        # cleanInstallResult = main.TRUE
        # gitPullResult = main.TRUE

        main.step( "Git pull" )
        gitPullResult = main.ONOSbench.gitPull()

        main.step( "Using mvn clean install" )
        if gitPullResult == main.TRUE:
            cleanInstallResult = main.ONOSbench.cleanInstall( mciTimeout = 1000 )
        else:
             main.log.warn( "Did not pull new code so skipping mvn " +
                            "clean install" )
             cleanInstallResult = main.TRUE

        main.ONOSbench.getVersion( report = True )

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage( opTimeout = 500 )

        main.step( "Installing ONOS package" )
        onos1InstallResult = main.ONOSbench.onosInstall( options = "-f",
                                                           node = ONOS1Ip )

        main.step( "Checking if ONOS is up yet" )
        for i in range( 2 ):
            onos1Isup = main.ONOSbench.isup( ONOS1Ip, timeout = 420 )
            if onos1Isup:
                break
        if not onos1Isup:
            main.log.report( "ONOS1 didn't start!" )

        cliResult = main.ONOScli.startOnosCli( ONOS1Ip,
                commandlineTimeout = 100, onosStartTimeout = 600 )

        case1Result = ( cleanInstallResult and packageResult and
                        cellResult and verifyResult and
                        onos1InstallResult and
                        onos1Isup and cliResult )

        utilities.assert_equals( expect = main.TRUE, actual = case1Result,
                                 onpass = "ONOS startup successful",
                                 onfail = "ONOS startup NOT successful" )

        if case1Result == main.FALSE:
            main.cleanup()
            main.exit()

    def CASE4( self, main ):
        """
        Test the SDN-IP functionality
        allRoutesExpected: all expected routes for all BGP peers
        routeIntentsExpected: all expected MultiPointToSinglePointIntent \
        intents
        bgpIntentsExpected: expected PointToPointIntent intents
        allRoutesActual: all routes from ONOS LCI
        routeIntentsActual: actual MultiPointToSinglePointIntent intents from \
        ONOS CLI
        bgpIntentsActual: actual PointToPointIntent intents from ONOS CLI
        """
        import json
        import time
        from operator import eq
        from time import localtime, strftime

        main.case( "This case is to testing the functionality of SDN-IP with \
        single ONOS instance" )
        SDNIPJSONFILEPATH = \
            "/home/admin/ONOS/tools/package/config/sdnip.json"
        # all expected routes for all BGP peers
        allRoutesExpected = []
        main.step( "Start to generate routes for all BGP peers" )
        main.log.info( "Generate prefixes for host3" )
        prefixesHost3 = main.QuaggaCliHost3.generatePrefixes( 3, 10 )
        main.log.info( prefixesHost3 )
        # generate route with next hop
        for prefix in prefixesHost3:
            allRoutesExpected.append( prefix + "/" + "192.168.20.1" )
        routeIntentsExpectedHost3 = \
            main.QuaggaCliHost3.generateExpectedOnePeerRouteIntents( 
            prefixesHost3, "192.168.20.1", "00:00:00:00:02:02",
            SDNIPJSONFILEPATH )

        main.log.info( "Generate prefixes for host4" )
        prefixesHost4 = main.QuaggaCliHost4.generatePrefixes( 4, 10 )
        main.log.info( prefixesHost4 )
        # generate route with next hop
        for prefix in prefixesHost4:
            allRoutesExpected.append( prefix + "/" + "192.168.30.1" )
        routeIntentsExpectedHost4 = \
            main.QuaggaCliHost4.generateExpectedOnePeerRouteIntents( 
            prefixesHost4, "192.168.30.1", "00:00:00:00:03:01",
            SDNIPJSONFILEPATH )

        main.log.info( "Generate prefixes for host5" )
        prefixesHost5 = main.QuaggaCliHost5.generatePrefixes( 5, 10 )
        main.log.info( prefixesHost5 )
        for prefix in prefixesHost5:
            allRoutesExpected.append( prefix + "/" + "192.168.60.2" )
        routeIntentsExpectedHost5 = \
            main.QuaggaCliHost5.generateExpectedOnePeerRouteIntents( 
            prefixesHost5, "192.168.60.1", "00:00:00:00:06:02",
            SDNIPJSONFILEPATH )

        routeIntentsExpected = routeIntentsExpectedHost3 + \
            routeIntentsExpectedHost4 + routeIntentsExpectedHost5

        main.step( "Get links in the network" )
        listResult = main.ONOScli.links( jsonFormat = False )
        main.log.info( listResult )
        main.log.info( "Activate sdn-ip application" )
        main.ONOScli.activateApp( "org.onosproject.sdnip" )
        # wait sdn-ip to finish installing connectivity intents, and the BGP
        # paths in data plane are ready.
        time.sleep( int( main.params[ 'timers' ][ 'SdnIpSetup' ] ) )

        main.step( "Login all BGP peers and add routes into peers" )

        main.log.info( "Login Quagga CLI on host3" )
        main.QuaggaCliHost3.loginQuagga( "1.168.30.2" )
        main.log.info( "Enter configuration model of Quagga CLI on host3" )
        main.QuaggaCliHost3.enterConfig( 64514 )
        main.log.info( "Add routes to Quagga on host3" )
        main.QuaggaCliHost3.addRoutes( prefixesHost3, 1 )

        main.log.info( "Login Quagga CLI on host4" )
        main.QuaggaCliHost4.loginQuagga( "1.168.30.3" )
        main.log.info( "Enter configuration model of Quagga CLI on host4" )
        main.QuaggaCliHost4.enterConfig( 64516 )
        main.log.info( "Add routes to Quagga on host4" )
        main.QuaggaCliHost4.addRoutes( prefixesHost4, 1 )

        main.log.info( "Login Quagga CLI on host5" )
        main.QuaggaCliHost5.loginQuagga( "1.168.30.5" )
        main.log.info( "Enter configuration model of Quagga CLI on host5" )
        main.QuaggaCliHost5.enterConfig( 64521 )
        main.log.info( "Add routes to Quagga on host5" )
        main.QuaggaCliHost5.addRoutes( prefixesHost5, 1 )

        for i in range( 101, 201 ):
            prefixesHostX = main.QuaggaCliHost.generatePrefixes( str( i ), 10 )
            main.log.info( prefixesHostX )
            for prefix in prefixesHostX:
                allRoutesExpected.append( prefix + "/" + "192.168.40."
                                           + str( i - 100 ) )

            routeIntentsExpectedHostX = \
            main.QuaggaCliHost.generateExpectedOnePeerRouteIntents( 
                prefixesHostX, "192.168.40." + str( i - 100 ),
                "00:00:%02d:00:00:90" % ( i - 101 ), SDNIPJSONFILEPATH )
            routeIntentsExpected = routeIntentsExpected + \
                routeIntentsExpectedHostX

            main.log.info( "Login Quagga CLI on host" + str( i ) )
            QuaggaCliHostX = getattr( main, ( 'QuaggaCliHost' + str( i ) ) )
            QuaggaCliHostX.loginQuagga( "1.168.30." + str( i ) )
            main.log.info( \
                "Enter configuration model of Quagga CLI on host" + str( i ) )
            QuaggaCliHostX.enterConfig( 65000 + i - 100 )
            main.log.info( "Add routes to Quagga on host" + str( i ) )
            QuaggaCliHostX.addRoutes( prefixesHostX, 1 )
        # wait Quagga to finish delivery all routes to each other and to sdn-ip,
        # plus finish installing all intents.
        time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
        time.sleep( int( main.params[ 'timers' ][ 'PathAvailable' ] ) )
        # get routes inside SDN-IP
        getRoutesResult = main.ONOScli.routes( jsonFormat = True )

        allRoutesActual = \
            main.QuaggaCliHost3.extractActualRoutesMaster( getRoutesResult )

        allRoutesStrExpected = str( sorted( allRoutesExpected ) )
        allRoutesStrActual = str( allRoutesActual ).replace( 'u', "" )
        main.step( "Check routes installed" )
        main.log.info( "Routes expected:" )
        main.log.info( allRoutesStrExpected )
        main.log.info( "Routes get from ONOS CLI:" )
        main.log.info( allRoutesStrActual )
        utilities.assertEquals( \
            expect = allRoutesStrExpected, actual = allRoutesStrActual,
            onpass = "***Routes in SDN-IP are correct!***",
            onfail = "***Routes in SDN-IP are wrong!***" )

        getIntentsResult = main.ONOScli.intents( jsonFormat = True )

        main.step( "Check MultiPointToSinglePointIntent intents installed" )
        # routeIntentsExpected are generated when generating routes
        # get route intents from ONOS CLI
        routeIntentsActualNum = \
            main.QuaggaCliHost3.extractActualRouteIntentNum( getIntentsResult )
        routeIntentsExpectedNum = 1030
        main.log.info( "MultiPointToSinglePoint Intent Num expected is:" )
        main.log.info( routeIntentsExpectedNum )
        main.log.info( "MultiPointToSinglePoint Intent NUM Actual is:" )
        main.log.info( routeIntentsActualNum )
        utilities.assertEquals( \
            expect = True,
            actual = eq( routeIntentsExpectedNum, routeIntentsActualNum ),
            onpass = "***MultiPointToSinglePoint Intent Num in SDN-IP is \
            correct!***",
            onfail = "***MultiPointToSinglePoint Intent Num in SDN-IP is \
            wrong!***" )

        main.step( "Check BGP PointToPointIntent intents installed" )

        bgpIntentsActualNum = \
            main.QuaggaCliHost3.extractActualBgpIntentNum( getIntentsResult )
        bgpIntentsExpectedNum = 624
        main.log.info( "bgpIntentsExpected num is:" )
        main.log.info( bgpIntentsExpectedNum )
        main.log.info( "bgpIntentsActual num is:" )
        main.log.info( bgpIntentsActualNum )
        utilities.assertEquals( \
            expect = True,
            actual = eq( bgpIntentsExpectedNum, bgpIntentsActualNum ),
            onpass = "***PointToPointIntent Intent Num in SDN-IP are correct!***",
            onfail = "***PointToPointIntent Intent Num in SDN-IP are wrong!***" )

        #============================= Ping Test ========================
        pingTestScript = "~/OnosSystemTest/TestON/tests/SDNIPfunction/Dependency/CASE4-ping-as2host.sh"
        pingTestResultsFile = \
        "~/OnosSystemTest/TestON/tests/SDNIPfunction/Dependency/log/CASE4-ping-results-before-delete-routes-"\
            + strftime( "%Y-%m-%d_%H:%M:%S", localtime() ) + ".txt"
        pingTestResults = main.QuaggaCliHost.pingTest( \
            "1.168.30.100", pingTestScript, pingTestResultsFile )
        main.log.info( pingTestResults )
        # wait to finish the ping test
        time.sleep( int( main.params[ 'timers' ][ 'PingTestWithRoutes' ] ) )

        #============================= Deleting Routes ==================
        main.step( "Check deleting routes installed" )
        main.QuaggaCliHost3.deleteRoutes( prefixesHost3, 1 )
        main.QuaggaCliHost4.deleteRoutes( prefixesHost4, 1 )
        main.QuaggaCliHost5.deleteRoutes( prefixesHost5, 1 )

        for i in range( 101, 201 ):
            prefixesHostX = main.QuaggaCliHost.generatePrefixes( str( i ), 10 )
            main.log.info( prefixesHostX )
            QuaggaCliHostX = getattr( main, ( 'QuaggaCliHost' + str( i ) ) )
            QuaggaCliHostX.deleteRoutes( prefixesHostX, 1 )
        # wait Quagga to finish delivery all routes to each other and to sdn-ip,
        # plus finish un-installing all intents.
        time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
        time.sleep( int( main.params[ 'timers' ][ 'PathAvailable' ] ) )

        getRoutesResult = main.ONOScli.routes( jsonFormat = True )
        allRoutesActual = \
            main.QuaggaCliHost3.extractActualRoutesMaster( getRoutesResult )
        main.log.info( "allRoutes_actual = " )
        main.log.info( allRoutesActual )

        utilities.assertEquals( \
            expect = "[]", actual = str( allRoutesActual ),
            onpass = "***Route number in SDN-IP is 0, correct!***",
            onfail = "***Routes number in SDN-IP is not 0, wrong!***" )

        main.step( "Check intents after deleting routes" )
        getIntentsResult = main.ONOScli.intents( jsonFormat = True )
        routeIntentsActualNum = \
            main.QuaggaCliHost3.extractActualRouteIntentNum( 
                getIntentsResult )
        main.log.info( "route Intents Actual Num is: " )
        main.log.info( routeIntentsActualNum )
        utilities.assertEquals( \
            expect = 0, actual = routeIntentsActualNum,
            onpass = "***MultiPointToSinglePoint Intent Num in SDN-IP is 0, \
            correct!***",
            onfail = "***MultiPointToSinglePoint Intent Num in SDN-IP is not 0, \
            wrong!***" )

        pingTestScript = "~/OnosSystemTest/TestON/tests/SDNIPfunction/Dependency/CASE4-ping-as2host.sh"
        pingTestResultsFile = \
        "~/OnosSystemTest/TestON/tests/SDNIPfunction/Dependency/log/CASE4-ping-results-after-delete-routes-"\
            + strftime( "%Y-%m-%d_%H:%M:%S", localtime() ) + ".txt"
        pingTestResults = main.QuaggaCliHost.pingTest( \
            "1.168.30.100", pingTestScript, pingTestResultsFile )
        main.log.info( pingTestResults )
        # wait to finish the ping test
        time.sleep( int( main.params[ 'timers' ][ 'PingTestWithoutRoutes' ] ) )
