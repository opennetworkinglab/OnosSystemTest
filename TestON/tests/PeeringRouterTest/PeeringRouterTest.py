# from cupshelpers.config import prefix

# Testing the basic functionality of SDN-IP


class PeeringRouterTest:

    def __init__( self ):
        self.default = ''

# from cupshelpers.config import prefix

# Testing the basic functionality of SDN-IP


class PeeringRouterTest:

    def __init__( self ):
        self.default = ''

    def CASE6 (self, main):
        import time
        import json
        from operator import eq
        # from datetime import datetime
        from time import localtime, strftime

        #============================= Ping Test ========================
        main.log.info("Start ping test")
        pingTestResults = main.QuaggaCliHost.pingTestAndCheck(
            "1.168.30.100" )
        main.log.info("Ping test result")
        if pingTestResults:
            main.log.info("Test succeeded")
        else:
            main.log.info("Test failed")
        
        utilities.assert_equals(expect=main.TRUE,actual=pingTestResults, 
                                  onpass="Default connectivity check PASS", 
                                  onfail="Default connectivity check FAIL") 


    def CASE4( self, main):
        import time
        import json
        from operator import eq
        # from datetime import datetime
        from time import localtime, strftime

        main.case("The test case is to help to setup the TestON environment \
            and test new drivers" )
        TESTCASE_ROOT_PATH = main.params[ 'ENV' ][ 'home' ]
        TESTCASE_MININET_ROOT_PATH = TESTCASE_ROOT_PATH + "/mininet"
        SDNIPJSONFILEPATH = TESTCASE_ROOT_PATH + "/sdnip.json"
        main.log.info("sdnip.json file path: "+ SDNIPJSONFILEPATH)
        # Launch mininet topology for this case
        MININET_TOPO_FILE = TESTCASE_MININET_ROOT_PATH + "/PeeringRouterMininet.py"
        main.step( "Launch mininet" )
        main.Mininet.handle.sendline("sudo python " + MININET_TOPO_FILE + " " + TESTCASE_MININET_ROOT_PATH)
        main.step("waiting 20 secs for all switches and quagga instances to comeup")
        time.sleep(20)
        main.step("verifying mininet launch")
        main.log.info( "Login Quagga CLI on host3" )
        main.QuaggaCliHost3.loginQuagga( "1.168.30.2" )
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

        cellName = main.params[ 'ENV' ][ 'cellName' ]
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        main.step( "Set cell for ONOS-cli environment" )
        main.ONOScli.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()

        main.log.report( "Removing raft logs" )
        main.ONOSbench.onosRemoveRaftLogs()
        main.log.report( "Uninstalling ONOS" )
        main.ONOSbench.onosUninstall( ONOS1Ip )

        main.step( "Installing ONOS package" )
        onos1InstallResult = main.ONOSbench.onosInstall(
            options="-f", node=ONOS1Ip )

        onos1Isup = main.ONOSbench.isup( ONOS1Ip )
        if not onos1Isup:
            main.log.report( "ONOS1 didn't start!" )

        main.step( "Start ONOS-cli" )

        main.ONOScli.startOnosCli( ONOS1Ip )

        main.step( "Get devices in the network" )
        listResult = main.ONOScli.devices( jsonFormat=False )
        main.log.info( listResult )
        time.sleep( 10 )
        main.log.info( "Installing gbprouter feature" )
        main.ONOScli.featureInstall( "onos-app-bgprouter" )
        time.sleep( 10 )
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

        #time.sleep( 30 )
        time.sleep(10)

        # get routes inside SDN-IP
        getRoutesResult = main.ONOScli.routes( jsonFormat=True )

        # parse routes from ONOS CLI
        # allRoutesActual = \
        #    main.QuaggaCliHost3.extractActualRoutes( getRoutesResult )
        allRoutesActual = []
        main.log.info("allRoutesExpected")

        allRoutesStrExpected = str( sorted( allRoutesExpected ) )
        allRoutesStrActual = str( allRoutesActual ).replace( 'u', "" )
        main.step( "Check routes installed" )
        main.log.info( "Routes expected:" )
        main.log.info( allRoutesStrExpected )
        main.log.info( "Routes get from ONOS CLI:" )
        main.log.info( allRoutesStrActual )
        utilities.assertEquals(
            expect=allRoutesStrExpected, actual=allRoutesStrActual,
            onpass="***Routes in SDN-IP are correct!***",
            onfail="***Routes in SDN-IP are wrong!***" )
        if( eq( allRoutesStrExpected, allRoutesStrActual ) ):
            main.log.report(
                "***Routes in SDN-IP after adding routes are correct!***" )
        else:
            main.log.report(
                "***Routes in SDN-IP after adding routes are wrong!***" )

        #============================= Ping Test ========================
        pingTestResults = main.QuaggaCliHost.pingTestAndCheckAllPass( "1.168.30.100" )
        main.log.info("Ping test result")
        if pingTestResults:
            main.log.info("Test succeeded")
        else:
            main.log.info("Test failed")
       
        utilities.assert_equals(expect=main.TRUE,actual=pingTestResults,
                                  onpass="Default connectivity check PASS",
                                  onfail="Default connectivity check FAIL")

        #============================= Deleting Routes ==================
        main.step( "Check deleting routes installed" )
        main.QuaggaCliHost3.deleteRoutes( prefixesHost3, 1 )
        main.QuaggaCliHost4.deleteRoutes( prefixesHost4, 1 )
        main.QuaggaCliHost5.deleteRoutes( prefixesHost5, 1 )

        getRoutesResult = main.ONOScli.routes( jsonFormat=True )
        # FIX ME
        #allRoutesActual = \
        #    main.QuaggaCliHost3.extractActualRoutes( getRoutesResult )
        allRoutesActual = []

        main.log.info( "allRoutes_actual = " )
        main.log.info( allRoutesActual )

        utilities.assertEquals(
            expect="[]", actual=str( allRoutesActual ),
            onpass="***Route number in SDN-IP is 0, correct!***",
            onfail="***Routes number in SDN-IP is not 0, wrong!***" )

        if( eq( allRoutesStrExpected, allRoutesStrActual ) ):
            main.log.report( "***Routes in SDN-IP after deleting correct!***" )
        else:
            main.log.report( "***Routes in SDN-IP after deleting wrong!***" )

        #============================= Ping Test ========================
        pingTestResults = main.QuaggaCliHost.pingTestAndCheckAllFail( "1.168.30.100" )
        main.log.info("Ping test result")
        if pingTestResults:
            main.log.info("Test succeeded")
        else:
            main.log.info("Test failed")

        utilities.assert_equals(expect=main.TRUE,actual=pingTestResults,
                                  onpass="disconnect check PASS",
                                  onfail="disconnect check FAIL")

        main.ONOScli.disconnect()
        main.ONOSbench.onosStop(ONOS1Ip);
        main.Mininet.disconnect()

    def CASE5( self, main ):
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
        import time
        import json
        from operator import eq
        # from datetime import datetime
        from time import localtime, strftime

        main.case("The test case is to help to setup the TestON environment \
            and test new drivers" )
        CURRENT_PATH = "/home/sdnip/TestON/tests/PeeringRouterTest/"
        SDNIPJSONFILEPATH = \
            "/home/sdnip/TestON/tests/PeeringRouterTest/sdnip.json"
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

        cellName = main.params[ 'ENV' ][ 'cellName' ]
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        main.step( "Set cell for ONOS-cli environment" )
        main.ONOScli.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()

        main.log.report( "Removing raft logs" )
        main.ONOSbench.onosRemoveRaftLogs()
        main.log.report( "Uninstalling ONOS" )
        main.ONOSbench.onosUninstall( ONOS1Ip )

        main.step( "Installing ONOS package" )
        onos1InstallResult = main.ONOSbench.onosInstall(
            options="-f", node=ONOS1Ip )

        main.step( "Checking if ONOS is up yet" )
        time.sleep( 20 )
        onos1Isup = main.ONOSbench.isup( ONOS1Ip )
        if not onos1Isup:
            main.log.report( "ONOS1 didn't start!" )

        main.step( "Start ONOS-cli" )

        main.ONOScli.startOnosCli( ONOS1Ip )

        main.step( "Get devices in the network" )
        listResult = main.ONOScli.devices( jsonFormat=False )
        main.log.info( listResult )
        time.sleep( 10 )
        main.log.info( "Installing gbprouter feature" )
        main.ONOScli.featureInstall( "onos-app-bgprouter" )
        time.sleep( 10 )
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

        #time.sleep( 30 )
        time.sleep(10)

        # get routes inside SDN-IP
        getRoutesResult = main.ONOScli.routes( jsonFormat=True )

        # parse routes from ONOS CLI
        # allRoutesActual = \
        #    main.QuaggaCliHost3.extractActualRoutes( getRoutesResult )
        allRoutesActual = []
        main.log.info("allRoutesExpected")

        allRoutesStrExpected = str( sorted( allRoutesExpected ) )
        allRoutesStrActual = str( allRoutesActual ).replace( 'u', "" )
        main.step( "Check routes installed" )
        main.log.info( "Routes expected:" )
        main.log.info( allRoutesStrExpected )
        main.log.info( "Routes get from ONOS CLI:" )
        main.log.info( allRoutesStrActual )
        utilities.assertEquals(
            expect=allRoutesStrExpected, actual=allRoutesStrActual,
            onpass="***Routes in SDN-IP are correct!***",
            onfail="***Routes in SDN-IP are wrong!***" )
        if( eq( allRoutesStrExpected, allRoutesStrActual ) ):
            main.log.report(
                "***Routes in SDN-IP after adding routes are correct!***" )
        else:
            main.log.report(
                "***Routes in SDN-IP after adding routes are wrong!***" )

        #time.sleep( 20 )
        #getIntentsResult = main.ONOScli.intents( jsonFormat=True )

        #main.step( "Check MultiPointToSinglePointIntent intents installed" )
        # routeIntentsExpected are generated when generating routes
        # get rpoute intents from ONOS CLI
        #routeIntentsActual = \
        #    main.QuaggaCliHost3.extractActualRouteIntents(
        #        getIntentsResult )
        #routeIntentsStrExpected = str( sorted( routeIntentsExpected ) )
        #routeIntentsStrActual = str( routeIntentsActual ).replace( 'u', "" )
        #main.log.info( "MultiPointToSinglePoint intents expected:" )
        #main.log.info( routeIntentsStrExpected )
        #main.log.info( "MultiPointToSinglePoint intents get from ONOS CLI:" )
        #main.log.info( routeIntentsStrActual )
        #utilities.assertEquals(
        #    expect=True,
        #    actual=eq( routeIntentsStrExpected, routeIntentsStrActual ),
        #    onpass="***MultiPointToSinglePoint Intents in SDN-IP are \
        #    correct!***",
        #    onfail="***MultiPointToSinglePoint Intents in SDN-IP are \
        #    wrong!***" )

        #if( eq( routeIntentsStrExpected, routeIntentsStrActual ) ):
        #    main.log.report( "***MultiPointToSinglePoint Intents before \
        #    deleting routes correct!***" )
        #else:
        #    main.log.report( "***MultiPointToSinglePoint Intents before \
        #    deleting routes wrong!***" )

        #main.step( "Check BGP PointToPointIntent intents installed" )
        ## bgp intents expected
        #bgpIntentsExpected = \
        #    main.QuaggaCliHost3.generateExpectedBgpIntents( SDNIPJSONFILEPATH )
        ## get BGP intents from ONOS CLI
        #bgpIntentsActual = \
        #    main.QuaggaCliHost3.extractActualBgpIntents( getIntentsResult )

        #bgpIntentsStrExpected = str( bgpIntentsExpected ).replace( 'u', "" )
        #bgpIntentsStrActual = str( bgpIntentsActual )
        #main.log.info( "PointToPointIntent intents expected:" )
        #main.log.info( bgpIntentsStrExpected )
        #main.log.info( "PointToPointIntent intents get from ONOS CLI:" )
        #main.log.info( bgpIntentsStrActual )

        #utilities.assertEquals(
        #    expect=True,
        #    actual=eq( bgpIntentsStrExpected, bgpIntentsStrActual ),
        #    onpass="***PointToPointIntent Intents in SDN-IP are correct!***",
        #    onfail="***PointToPointIntent Intents in SDN-IP are wrong!***" )

        #if ( eq( bgpIntentsStrExpected, bgpIntentsStrActual ) ):
        #    main.log.report(
        #        "***PointToPointIntent Intents in SDN-IP are correct!***" )
        #else:
        #    main.log.report(
        #        "***PointToPointIntent Intents in SDN-IP are wrong!***" )

        #============================= Ping Test ========================
        # wait until all MultiPointToSinglePoint
        time.sleep( 10 )
        main.log.info("Start ping test")
        pingTestScript = CURRENT_PATH + "CASE4-ping-as2host.sh"
        pingTestResultsFile = \
        CURRENT_PATH + "CASE4-ping-results-before-delete-routes-" \
            + strftime( "%Y-%m-%d_%H:%M:%S", localtime() ) + ".txt"
        pingTestResults = main.QuaggaCliHost.pingTest(
            "1.168.30.100", pingTestScript, pingTestResultsFile )
        main.log.info("Ping test result")
        main.log.info( pingTestResults )
        time.sleep( 10 )

        #============================= Deleting Routes ==================
        main.step( "Check deleting routes installed" )
        main.QuaggaCliHost3.deleteRoutes( prefixesHost3, 1 )
        main.QuaggaCliHost4.deleteRoutes( prefixesHost4, 1 )
        main.QuaggaCliHost5.deleteRoutes( prefixesHost5, 1 )

        getRoutesResult = main.ONOScli.routes( jsonFormat=True )
        # FIX ME
        #allRoutesActual = \
        #    main.QuaggaCliHost3.extractActualRoutes( getRoutesResult )
        allRoutesActual = []

        main.log.info( "allRoutes_actual = " )
        main.log.info( allRoutesActual )

        utilities.assertEquals(
            expect="[]", actual=str( allRoutesActual ),
            onpass="***Route number in SDN-IP is 0, correct!***",
            onfail="***Routes number in SDN-IP is not 0, wrong!***" )

        if( eq( allRoutesStrExpected, allRoutesStrActual ) ):
            main.log.report( "***Routes in SDN-IP after deleting correct!***" )
        else:
            main.log.report( "***Routes in SDN-IP after deleting wrong!***" )

        #main.step( "Check intents after deleting routes" )
        #getIntentsResult = main.ONOScli.intents( jsonFormat=True )
        #routeIntentsActual = \
        #    main.QuaggaCliHost3.extractActualRouteIntents(
        #        getIntentsResult )
        #main.log.info( "main.ONOScli.intents()= " )
        #main.log.info( routeIntentsActual )
        #utilities.assertEquals(
        #    expect="[]", actual=str( routeIntentsActual ),
        #    onpass="***MultiPointToSinglePoint Intents number in SDN-IP is 0, \
        #    correct!***",
        #    onfail="***MultiPointToSinglePoint Intents number in SDN-IP is 0, \
        #    wrong!***" )

        #if( eq( routeIntentsStrExpected, routeIntentsStrActual ) ):
        #    main.log.report( "***MultiPointToSinglePoint Intents after \
        #    deleting routes correct!***" )
        #else:
        #    main.log.report( "***MultiPointToSinglePoint Intents after \
        #    deleting routes wrong!***" )

        time.sleep( 10 )
        main.log.info("Ping test after removing routs")
        pingTestScript = CURRENT_PATH + "CASE4-ping-as2host.sh"
        pingTestResultsFile = \
        CURRENT_PATH + "CASE4-ping-results-after-delete-routes-" \
            + strftime( "%Y-%m-%d_%H:%M:%S", localtime() ) + ".txt"
        pingTestResults = main.QuaggaCliHost.pingTest(
            "1.168.30.100", pingTestScript, pingTestResultsFile )
        main.log.info("Ping test results")
        main.log.info( pingTestResults )
        time.sleep( 10 )

        # main.step( "Test whether Mininet is started" )
        # main.Mininet2.handle.sendline( "xterm host1" )
        # main.Mininet2.handle.expect( "mininet>" )

    def CASE3( self, main ):
        """
        Test the SDN-IP functionality
        allRoutesExpected: all expected routes for all BGP peers
        routeIntentsExpected: all expected MultiPointToSinglePointIntent intents
        bgpIntentsExpected: expected PointToPointIntent intents
        allRoutesActual: all routes from ONOS LCI
        routeIntentsActual: actual MultiPointToSinglePointIntent intents from \
        ONOS CLI
        bgpIntentsActual: actual PointToPointIntent intents from ONOS CLI
        """
        import time
        import json
        from operator import eq
        # from datetime import datetime
        from time import localtime, strftime

        main.case( "The test case is to help to setup the TestON \
            environment and test new drivers" )
        # SDNIPJSONFILEPATH = "../tests/SdnIpTest/sdnip.json"
        TESTPATH = "/home/adnip/TestOn/tests/PeeringRouterTest/"
        SDNIPJSONFILEPATH = \
            "/home/sdnip/onos/tools/package/config/sdnip.json"
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

        routeIntentsExpected = routeIntentsExpectedHost3 + \
            routeIntentsExpectedHost4

        cellName = main.params[ 'ENV' ][ 'cellName' ]
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        main.step( "Set cell for ONOS-cli environment" )
        main.ONOScli.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()

        main.log.report( "Removing raft logs" )
        main.ONOSbench.onosRemoveRaftLogs()
        main.log.report( "Uninstalling ONOS" )
        main.ONOSbench.onosUninstall( ONOS1Ip )

        main.step( "Installing ONOS package" )
        onos1InstallResult = main.ONOSbench.onosInstall(
            options="-f", node=ONOS1Ip )

        main.step( "Checking if ONOS is up yet" )
        time.sleep( 60 )
        onos1Isup = main.ONOSbench.isup( ONOS1Ip )
        if not onos1Isup:
            main.log.report( "ONOS1 didn't start!" )

        main.step( "Start ONOS-cli" )

        main.ONOScli.startOnosCli( ONOS1Ip )

        main.step( "Get devices in the network" )
        listResult = main.ONOScli.devices( jsonFormat=False )
        main.log.info( listResult )
        time.sleep( 10 )
        main.log.info( "Installing sdn-ip feature" )
        main.ONOScli.featureInstall( "onos-app-sdnip" )
        time.sleep( 10 )
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

        for i in range( 101, 201 ):
            prefixesHostX = \
                main.QuaggaCliHost.generatePrefixes( str( i ), 10 )
            main.log.info( prefixesHostX )
            for prefix in prefixesHostX:
                allRoutesExpected.append(
                    prefix + "/" + "192.168.40." + str( i - 100 ) )

            routeIntentsExpectedHostX = \
                main.QuaggaCliHost.generateExpectedOnePeerRouteIntents(
                prefixesHostX, "192.168.40." + str( i - 100 ),
                "00:00:%02d:00:00:90" % ( i - 101 ), SDNIPJSONFILEPATH )
            routeIntentsExpected = routeIntentsExpected + \
                routeIntentsExpectedHostX

            main.log.info( "Login Quagga CLI on host" + str( i ) )
            QuaggaCliHostX = getattr( main, ( 'QuaggaCliHost' + str( i ) ) )
            QuaggaCliHostX.loginQuagga( "1.168.30." + str( i ) )
            main.log.info(
                "Enter configuration model of Quagga CLI on host" + str( i ) )
            QuaggaCliHostX.enterConfig( 65000 + i - 100 )
            main.log.info( "Add routes to Quagga on host" + str( i ) )
            QuaggaCliHostX.addRoutes( prefixesHostX, 1 )

        time.sleep( 60 )

        # get routes inside SDN-IP
        getRoutesResult = main.ONOScli.routes( jsonFormat=True )

        # parse routes from ONOS CLI
        allRoutesActual = \
            main.QuaggaCliHost3.extractActualRoutes( getRoutesResult )

        allRoutesStrExpected = str( sorted( allRoutesExpected ) )
        allRoutesStrActual = str( allRoutesActual ).replace( 'u', "" )
        main.step( "Check routes installed" )
        main.log.info( "Routes expected:" )
        main.log.info( allRoutesStrExpected )
        main.log.info( "Routes get from ONOS CLI:" )
        main.log.info( allRoutesStrActual )
        utilities.assertEquals(
            expect=allRoutesStrExpected, actual=allRoutesStrActual,
            onpass="***Routes in SDN-IP are correct!***",
            onfail="***Routes in SDN-IP are wrong!***" )
        if( eq( allRoutesStrExpected, allRoutesStrActual ) ):
            main.log.report(
                "***Routes in SDN-IP after adding routes are correct!***" )
        else:
            main.log.report(
                "***Routes in SDN-IP after adding routes are wrong!***" )

        time.sleep( 20 )
        getIntentsResult = main.ONOScli.intents( jsonFormat=True )

        main.step( "Check MultiPointToSinglePointIntent intents installed" )
        # routeIntentsExpected are generated when generating routes
        # get rpoute intents from ONOS CLI
        routeIntentsActual = \
            main.QuaggaCliHost3.extractActualRouteIntents(
                getIntentsResult )
        routeIntentsStrExpected = str( sorted( routeIntentsExpected ) )
        routeIntentsStrActual = str( routeIntentsActual ).replace( 'u', "" )
        main.log.info( "MultiPointToSinglePoint intents expected:" )
        main.log.info( routeIntentsStrExpected )
        main.log.info( "MultiPointToSinglePoint intents get from ONOS CLI:" )
        main.log.info( routeIntentsStrActual )
        utilities.assertEquals(
            expect=True,
            actual=eq( routeIntentsStrExpected, routeIntentsStrActual ),
            onpass="***MultiPointToSinglePoint Intents in SDN-IP are \
            correct!***",
            onfail="***MultiPointToSinglePoint Intents in SDN-IP are \
            wrong!***" )

        if( eq( routeIntentsStrExpected, routeIntentsStrActual ) ):
            main.log.report(
                "***MultiPointToSinglePoint Intents before deleting routes \
                correct!***" )
        else:
            main.log.report(
                "***MultiPointToSinglePoint Intents before deleting routes \
                wrong!***" )

        main.step( "Check BGP PointToPointIntent intents installed" )
        # bgp intents expected
        bgpIntentsExpected = main.QuaggaCliHost3.generateExpectedBgpIntents(
            SDNIPJSONFILEPATH )
        # get BGP intents from ONOS CLI
        bgpIntentsActual = main.QuaggaCliHost3.extractActualBgpIntents(
            getIntentsResult )

        bgpIntentsStrExpected = str( bgpIntentsExpected ).replace( 'u', "" )
        bgpIntentsStrActual = str( bgpIntentsActual )
        main.log.info( "PointToPointIntent intents expected:" )
        main.log.info( bgpIntentsStrExpected )
        main.log.info( "PointToPointIntent intents get from ONOS CLI:" )
        main.log.info( bgpIntentsStrActual )

        utilities.assertEquals(
            expect=True,
            actual=eq( bgpIntentsStrExpected, bgpIntentsStrActual ),
            onpass="***PointToPointIntent Intents in SDN-IP are correct!***",
            onfail="***PointToPointIntent Intents in SDN-IP are wrong!***" )

        if ( eq( bgpIntentsStrExpected, bgpIntentsStrActual ) ):
            main.log.report(
                "***PointToPointIntent Intents in SDN-IP are correct!***" )
        else:
            main.log.report(
                "***PointToPointIntent Intents in SDN-IP are wrong!***" )

        #============================= Ping Test ========================
        # wait until all MultiPointToSinglePoint
        time.sleep( 20 )
        pingTestScript = "~/SDNIP/test-tools/CASE3-ping-as2host.sh"
        pingTestResultsFile = \
        "~/SDNIP/SdnIpIntentDemo/log/CASE3-ping-results-before-delete-routes-" \
            + strftime( "%Y-%m-%d_%H:%M:%S", localtime() ) + ".txt"
        pingTestResults = main.QuaggaCliHost.pingTest(
            "1.168.30.100", pingTestScript, pingTestResultsFile )
        main.log.info( pingTestResults )
        time.sleep( 20 )

        #============================= Deleting Routes ==================
        main.step( "Check deleting routes installed" )
        main.QuaggaCliHost3.deleteRoutes( prefixesHost3, 1 )
        main.QuaggaCliHost4.deleteRoutes( prefixesHost4, 1 )
        for i in range( 101, 201 ):
            prefixesHostX = \
                main.QuaggaCliHost.generatePrefixes( str( i ), 10 )
            main.log.info( prefixesHostX )
            QuaggaCliHostX = getattr( main, ( 'QuaggaCliHost' + str( i ) ) )
            QuaggaCliHostX.deleteRoutes( prefixesHostX, 1 )

        getRoutesResult = main.ONOScli.routes( jsonFormat=True )
        allRoutesActual = main.QuaggaCliHost3.extractActualRoutes(
            getRoutesResult )
        main.log.info( "allRoutes_actual = " )
        main.log.info( allRoutesActual )

        utilities.assertEquals(
            expect="[]", actual=str( allRoutesActual ),
            onpass="***Route number in SDN-IP is 0, correct!***",
            onfail="***Routes number in SDN-IP is not 0, wrong!***" )

        if( eq( allRoutesStrExpected, allRoutesStrActual ) ):
            main.log.report(
                "***Routes in SDN-IP after deleting correct!***" )
        else:
            main.log.report(
                "***Routes in SDN-IP after deleting wrong!***" )

        main.step( "Check intents after deleting routes" )
        getIntentsResult = main.ONOScli.intents( jsonFormat=True )
        routeIntentsActual = \
            main.QuaggaCliHost3.extractActualRouteIntents(
                getIntentsResult )
        main.log.info( "main.ONOScli.intents()= " )
        main.log.info( routeIntentsActual )
        utilities.assertEquals(
            expect="[]", actual=str( routeIntentsActual ),
            onpass="***MultiPointToSinglePoint Intents number in SDN-IP is \
            0, correct!***",
            onfail="***MultiPointToSinglePoint Intents number in SDN-IP is \
            0, wrong!***" )

        if( eq( routeIntentsStrExpected, routeIntentsStrActual ) ):
            main.log.report(
                "***MultiPointToSinglePoint Intents after deleting routes \
                correct!***" )
        else:
            main.log.report(
                "***MultiPointToSinglePoint Intents after deleting routes \
                wrong!***" )

        time.sleep( 20 )
        pingTestScript = "~/SDNIP/test-tools/CASE3-ping-as2host.sh"
        pingTestResultsFile = \
        "~/SDNIP/SdnIpIntentDemo/log/CASE3-ping-results-after-delete-routes-" \
            + strftime( "%Y-%m-%d_%H:%M:%S", localtime() ) + ".txt"
        pingTestResults = main.QuaggaCliHost.pingTest(
            "1.168.30.100", pingTestScript, pingTestResultsFile )
        main.log.info( pingTestResults )
        time.sleep( 100 )

        # main.step( "Test whether Mininet is started" )
        # main.Mininet2.handle.sendline( "xterm host1" )
        # main.Mininet2.handle.expect( "mininet>" )

    def CASE1( self, main ):
        """
        Test the SDN-IP functionality
        allRoutesExpected: all expected routes for all BGP peers
        routeIntentsExpected: all expected MultiPointToSinglePointIntent \
        intents
        bgpIntentsExpected: expected PointToPointIntent intents
        allRoutesActual: all routes from ONOS LCI
        routeIntentsActual: actual MultiPointToSinglePointIntent intents \
        from ONOS CLI
        bgpIntentsActual: actual PointToPointIntent intents from ONOS CLI
        """
        import time
        import json
        from operator import eq
        # from datetime import datetime
        from time import localtime, strftime

        main.case("The test case is to help to setup the TestON environment \
            and test new drivers" )
        SDNIPJSONFILEPATH = "../tests/SdnIpTest/sdnip.json"
        # all expected routes for all BGP peers
        allRoutesExpected = []
        main.step( "Start to generate routes for all BGP peers" )
        # bgpPeerHosts = []
        # for i in range( 3, 5 ):
        #    bgpPeerHosts.append( "host" + str( i ) )
        # main.log.info( "BGP Peer Hosts are:" + bgpPeerHosts )

        # for i in range( 3, 5 ):
         #   QuaggaCliHost = "QuaggaCliHost" + str( i )
          #  prefixes = main.QuaggaCliHost.generatePrefixes( 3, 10 )

           # main.log.info( prefixes )
            # allRoutesExpected.append( prefixes )
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

        routeIntentsExpected = routeIntentsExpectedHost3 + \
            routeIntentsExpectedHost4

        cellName = main.params[ 'ENV' ][ 'cellName' ]
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        main.step( "Set cell for ONOS-cli environment" )
        main.ONOScli.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()
        main.log.report( "Removing raft logs" )
        main.ONOSbench.onosRemoveRaftLogs()
        main.log.report( "Uninstalling ONOS" )
        main.ONOSbench.onosUninstall( ONOS1Ip )
        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()

        main.step( "Starting ONOS service" )
        # TODO: start ONOS from Mininet Script
        # startResult = main.ONOSbench.onosStart( "127.0.0.1" )
        main.step( "Installing ONOS package" )
        onos1InstallResult = main.ONOSbench.onosInstall(
            options="-f", node=ONOS1Ip )

        main.step( "Checking if ONOS is up yet" )
        time.sleep( 60 )
        onos1Isup = main.ONOSbench.isup( ONOS1Ip )
        if not onos1Isup:
            main.log.report( "ONOS1 didn't start!" )

        main.step( "Start ONOS-cli" )
        # TODO: change the hardcode in startOnosCli method in ONOS CLI driver

        main.ONOScli.startOnosCli( ONOS1Ip )

        main.step( "Get devices in the network" )
        listResult = main.ONOScli.devices( jsonFormat=False )
        main.log.info( listResult )
        time.sleep( 10 )
        main.log.info( "Installing sdn-ip feature" )
        main.ONOScli.featureInstall( "onos-app-sdnip" )
        time.sleep( 10 )
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
        time.sleep( 60 )

        # get all routes inside SDN-IP
        getRoutesResult = main.ONOScli.routes( jsonFormat=True )

        # parse routes from ONOS CLI
        allRoutesActual = \
            main.QuaggaCliHost3.extractActualRoutes( getRoutesResult )

        allRoutesStrExpected = str( sorted( allRoutesExpected ) )
        allRoutesStrActual = str( allRoutesActual ).replace( 'u', "" )
        main.step( "Check routes installed" )
        main.log.info( "Routes expected:" )
        main.log.info( allRoutesStrExpected )
        main.log.info( "Routes get from ONOS CLI:" )
        main.log.info( allRoutesStrActual )
        utilities.assertEquals(
            expect=allRoutesStrExpected, actual=allRoutesStrActual,
            onpass="***Routes in SDN-IP are correct!***",
            onfail="***Routes in SDN-IP are wrong!***" )
        if( eq( allRoutesStrExpected, allRoutesStrActual ) ):
            main.log.report(
                "***Routes in SDN-IP after adding routes are correct!***" )
        else:
            main.log.report(
                "***Routes in SDN-IP after adding routes are wrong!***" )

        time.sleep( 20 )
        getIntentsResult = main.ONOScli.intents( jsonFormat=True )

        main.step( "Check MultiPointToSinglePointIntent intents installed" )
        # routeIntentsExpected are generated when generating routes
        # get rpoute intents from ONOS CLI
        routeIntentsActual = \
            main.QuaggaCliHost3.extractActualRouteIntents(
                getIntentsResult )
        routeIntentsStrExpected = str( sorted( routeIntentsExpected ) )
        routeIntentsStrActual = str( routeIntentsActual ).replace( 'u', "" )
        main.log.info( "MultiPointToSinglePoint intents expected:" )
        main.log.info( routeIntentsStrExpected )
        main.log.info( "MultiPointToSinglePoint intents get from ONOS CLI:" )
        main.log.info( routeIntentsStrActual )
        utilities.assertEquals(
            expect=True,
            actual=eq( routeIntentsStrExpected, routeIntentsStrActual ),
            onpass="***MultiPointToSinglePoint Intents in SDN-IP are \
            correct!***",
            onfail="***MultiPointToSinglePoint Intents in SDN-IP are \
            wrong!***" )

        if( eq( routeIntentsStrExpected, routeIntentsStrActual ) ):
            main.log.report(
                "***MultiPointToSinglePoint Intents before deleting routes \
                correct!***" )
        else:
            main.log.report(
                "***MultiPointToSinglePoint Intents before deleting routes \
                wrong!***" )

        main.step( "Check BGP PointToPointIntent intents installed" )
        # bgp intents expected
        bgpIntentsExpected = \
            main.QuaggaCliHost3.generateExpectedBgpIntents( SDNIPJSONFILEPATH )
        # get BGP intents from ONOS CLI
        bgpIntentsActual = main.QuaggaCliHost3.extractActualBgpIntents(
            getIntentsResult )

        bgpIntentsStrExpected = str( bgpIntentsExpected ).replace( 'u', "" )
        bgpIntentsStrActual = str( bgpIntentsActual )
        main.log.info( "PointToPointIntent intents expected:" )
        main.log.info( bgpIntentsStrExpected )
        main.log.info( "PointToPointIntent intents get from ONOS CLI:" )
        main.log.info( bgpIntentsStrActual )

        utilities.assertEquals(
            expect=True,
            actual=eq( bgpIntentsStrExpected, bgpIntentsStrActual ),
            onpass="***PointToPointIntent Intents in SDN-IP are correct!***",
            onfail="***PointToPointIntent Intents in SDN-IP are wrong!***" )

        if ( eq( bgpIntentsStrExpected, bgpIntentsStrActual ) ):
            main.log.report(
                "***PointToPointIntent Intents in SDN-IP are correct!***" )
        else:
            main.log.report(
                "***PointToPointIntent Intents in SDN-IP are wrong!***" )

        #============================= Ping Test ========================
        # wait until all MultiPointToSinglePoint
        time.sleep( 20 )
        pingTestScript = "~/SDNIP/SdnIpIntentDemo/CASE1-ping-as2host.sh"
        pingTestResultsFile = \
        "~/SDNIP/SdnIpIntentDemo/log/CASE1-ping-results-before-delete-routes-" \
             + strftime( "%Y-%m-%d_%H:%M:%S", localtime() ) + ".txt"
        pingTestResults = main.QuaggaCliHost.pingTest(
            "1.168.30.100", pingTestScript, pingTestResultsFile )
        main.log.info( pingTestResults )

        # ping test

        #============================= Deleting Routes ==================
        main.step( "Check deleting routes installed" )
        main.QuaggaCliHost3.deleteRoutes( prefixesHost3, 1 )
        main.QuaggaCliHost4.deleteRoutes( prefixesHost4, 1 )

        # main.log.info( "main.ONOScli.get_routes_num() = " )
        # main.log.info( main.ONOScli.getRoutesNum() )
        # utilities.assertEquals( expect="Total SDN-IP routes = 1", actual=
        # main.ONOScli.getRoutesNum(),
        getRoutesResult = main.ONOScli.routes( jsonFormat=True )
        allRoutesActual = \
            main.QuaggaCliHost3.extractActualRoutes( getRoutesResult )
        main.log.info( "allRoutes_actual = " )
        main.log.info( allRoutesActual )

        utilities.assertEquals(
            expect="[]", actual=str( allRoutesActual ),
            onpass="***Route number in SDN-IP is 0, correct!***",
            onfail="***Routes number in SDN-IP is not 0, wrong!***" )

        if( eq( allRoutesStrExpected, allRoutesStrActual ) ):
            main.log.report(
                "***Routes in SDN-IP after deleting correct!***" )
        else:
            main.log.report(
                "***Routes in SDN-IP after deleting wrong!***" )

        main.step( "Check intents after deleting routes" )
        getIntentsResult = main.ONOScli.intents( jsonFormat=True )
        routeIntentsActual = \
            main.QuaggaCliHost3.extractActualRouteIntents(
                getIntentsResult )
        main.log.info( "main.ONOScli.intents()= " )
        main.log.info( routeIntentsActual )
        utilities.assertEquals(
            expect="[]", actual=str( routeIntentsActual ),
            onpass="***MultiPointToSinglePoint Intents number in SDN-IP is \
            0, correct!***",
            onfail="***MultiPointToSinglePoint Intents number in SDN-IP is \
            0, wrong!***" )

        if( eq( routeIntentsStrExpected, routeIntentsStrActual ) ):
            main.log.report(
                "***MultiPointToSinglePoint Intents after deleting routes \
                correct!***" )
        else:
            main.log.report(
                "***MultiPointToSinglePoint Intents after deleting routes \
                wrong!***" )

        time.sleep( 20 )
        pingTestScript = "~/SDNIP/SdnIpIntentDemo/CASE1-ping-as2host.sh"
        pingTestResultsFile = \
        "~/SDNIP/SdnIpIntentDemo/log/CASE1-ping-results-after-delete-routes-" \
             + strftime( "%Y-%m-%d_%H:%M:%S", localtime() ) + ".txt"
        pingTestResults = main.QuaggaCliHost.pingTest(
            "1.168.30.100", pingTestScript, pingTestResultsFile )
        main.log.info( pingTestResults )
        time.sleep( 30 )

        # main.step( "Test whether Mininet is started" )
        # main.Mininet2.handle.sendline( "xterm host1" )
        # main.Mininet2.handle.expect( "mininet>" )

    def CASE2( self, main ):
        """
        Test the SDN-IP functionality
        allRoutesExpected: all expected routes for all BGP peers
        routeIntentsExpected: all expected MultiPointToSinglePointIntent \
        intents
        bgpIntentsExpected: expected PointToPointIntent intents
        allRoutesActual: all routes from ONOS LCI
        routeIntentsActual: actual MultiPointToSinglePointIntent intents \
        from ONOS CLI
        bgpIntentsActual: actual PointToPointIntent intents from ONOS CLI
        """
        import time
        import json
        from operator import eq
        from time import localtime, strftime

        main.case(
            "The test case is to help to setup the TestON environment and \
            test new drivers" )
        SDNIPJSONFILEPATH = "../tests/SdnIpTest/sdnip.json"
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

        routeIntentsExpected = routeIntentsExpectedHost3 + \
            routeIntentsExpectedHost4

        main.log.report( "Removing raft logs" )
        main.ONOSbench.onosRemoveRaftLogs()
        main.log.report( "Uninstalling ONOS" )
        main.ONOSbench.onosUninstall( ONOS1Ip )

        cellName = main.params[ 'ENV' ][ 'cellName' ]
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        main.step( "Set cell for ONOS-cli environment" )
        main.ONOScli.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()
        # main.log.report( "Removing raft logs" )
        # main.ONOSbench.onosRemoveRaftLogs()
        # main.log.report( "Uninstalling ONOS" )
        # main.ONOSbench.onosUninstall( ONOS1Ip )
        main.step( "Creating ONOS package" )
        # packageResult = main.ONOSbench.onosPackage()

        main.step( "Installing ONOS package" )
        # onos1InstallResult = main.ONOSbench.onosInstall( options="-f",
        # node=ONOS1Ip )

        main.step( "Checking if ONOS is up yet" )
        # time.sleep( 60 )
        onos1Isup = main.ONOSbench.isup( ONOS1Ip )
        if not onos1Isup:
            main.log.report( "ONOS1 didn't start!" )

        main.step( "Start ONOS-cli" )
        main.ONOScli.startOnosCli( ONOS1Ip )

        main.step( "Get devices in the network" )
        listResult = main.ONOScli.devices( jsonFormat=False )
        main.log.info( listResult )
        time.sleep( 10 )
        main.log.info( "Installing sdn-ip feature" )
        main.ONOScli.featureInstall( "onos-app-sdnip" )
        time.sleep( 10 )

        main.step( "Check BGP PointToPointIntent intents installed" )
        # bgp intents expected
        bgpIntentsExpected = main.QuaggaCliHost3.generateExpectedBgpIntents(
            SDNIPJSONFILEPATH )
        # get BGP intents from ONOS CLI
        getIntentsResult = main.ONOScli.intents( jsonFormat=True )
        bgpIntentsActual = main.QuaggaCliHost3.extractActualBgpIntents(
            getIntentsResult )

        bgpIntentsStrExpected = str( bgpIntentsExpected ).replace( 'u', "" )
        bgpIntentsStrActual = str( bgpIntentsActual )
        main.log.info( "PointToPointIntent intents expected:" )
        main.log.info( bgpIntentsStrExpected )
        main.log.info( "PointToPointIntent intents get from ONOS CLI:" )
        main.log.info( bgpIntentsStrActual )

        utilities.assertEquals(
            expect=True,
            actual=eq( bgpIntentsStrExpected, bgpIntentsStrActual ),
            onpass="***PointToPointIntent Intents in SDN-IP are correct!***",
            onfail="***PointToPointIntent Intents in SDN-IP are wrong!***" )

        if ( eq( bgpIntentsStrExpected, bgpIntentsStrActual ) ):
            main.log.report(
                "***PointToPointIntent Intents in SDN-IP are correct!***" )
        else:
            main.log.report(
                "***PointToPointIntent Intents in SDN-IP are wrong!***" )

        allRoutesStrExpected = str( sorted( allRoutesExpected ) )
        routeIntentsStrExpected = str( sorted( routeIntentsExpected ) )
        pingTestScript = "~/SDNIP/SdnIpIntentDemo/CASE1-ping-as2host.sh"
        # roundNum = 0;
        # while( True ):
        for roundNum in range( 1, 6 ):
            # round = round + 1;
            main.log.report( "The Round " + str( roundNum ) +
                             " test starts................................" )

            main.step( "Login all BGP peers and add routes into peers" )
            main.log.info( "Login Quagga CLI on host3" )
            main.QuaggaCliHost3.loginQuagga( "1.168.30.2" )
            main.log.info(
                "Enter configuration model of Quagga CLI on host3" )
            main.QuaggaCliHost3.enterConfig( 64514 )
            main.log.info( "Add routes to Quagga on host3" )
            main.QuaggaCliHost3.addRoutes( prefixesHost3, 1 )

            main.log.info( "Login Quagga CLI on host4" )
            main.QuaggaCliHost4.loginQuagga( "1.168.30.3" )
            main.log.info(
                "Enter configuration model of Quagga CLI on host4" )
            main.QuaggaCliHost4.enterConfig( 64516 )
            main.log.info( "Add routes to Quagga on host4" )
            main.QuaggaCliHost4.addRoutes( prefixesHost4, 1 )
            time.sleep( 60 )

            # get all routes inside SDN-IP
            getRoutesResult = main.ONOScli.routes( jsonFormat=True )

            # parse routes from ONOS CLI
            allRoutesActual = \
                main.QuaggaCliHost3.extractActualRoutes( getRoutesResult )

            # allRoutesStrExpected = str( sorted( allRoutesExpected ) )
            allRoutesStrActual = str( allRoutesActual ).replace( 'u', "" )
            main.step( "Check routes installed" )
            main.log.info( "Routes expected:" )
            main.log.info( allRoutesStrExpected )
            main.log.info( "Routes get from ONOS CLI:" )
            main.log.info( allRoutesStrActual )
            utilities.assertEquals(
                expect=allRoutesStrExpected, actual=allRoutesStrActual,
                onpass="***Routes in SDN-IP are correct!***",
                onfail="***Routes in SDN-IP are wrong!***" )
            if( eq( allRoutesStrExpected, allRoutesStrActual ) ):
                main.log.report(
                    "***Routes in SDN-IP after adding correct!***" )
            else:
                main.log.report(
                    "***Routes in SDN-IP after adding wrong!***" )

            time.sleep( 20 )
            getIntentsResult = main.ONOScli.intents( jsonFormat=True )

            main.step(
                "Check MultiPointToSinglePointIntent intents installed" )
            # routeIntentsExpected are generated when generating routes
            # get route intents from ONOS CLI
            routeIntentsActual = \
                main.QuaggaCliHost3.extractActualRouteIntents(
                    getIntentsResult )
            # routeIntentsStrExpected = str( sorted( routeIntentsExpected ) )
            routeIntentsStrActual = str(
                routeIntentsActual ).replace( 'u', "" )
            main.log.info( "MultiPointToSinglePoint intents expected:" )
            main.log.info( routeIntentsStrExpected )
            main.log.info(
                "MultiPointToSinglePoint intents get from ONOS CLI:" )
            main.log.info( routeIntentsStrActual )
            utilities.assertEquals(
                expect=True,
                actual=eq( routeIntentsStrExpected, routeIntentsStrActual ),
                onpass="***MultiPointToSinglePoint Intents in SDN-IP are \
                correct!***",
                onfail="***MultiPointToSinglePoint Intents in SDN-IP are \
                wrong!***" )

            if( eq( routeIntentsStrExpected, routeIntentsStrActual ) ):
                main.log.report(
                    "***MultiPointToSinglePoint Intents after adding routes \
                    correct!***" )
            else:
                main.log.report(
                    "***MultiPointToSinglePoint Intents after adding routes \
                    wrong!***" )

            #============================= Ping Test ========================
            # wait until all MultiPointToSinglePoint
            time.sleep( 20 )
            # pingTestScript = "~/SDNIP/SdnIpIntentDemo/CASE1-ping-as2host.sh"
            pingTestResultsFile = \
                "~/SDNIP/SdnIpIntentDemo/log/CASE2-Round" \
                + str( roundNum ) + "-ping-results-before-delete-routes-" \
                + strftime( "%Y-%m-%d_%H:%M:%S", localtime() ) + ".txt"
            pingTestResults = main.QuaggaCliHost.pingTest(
                "1.168.30.100", pingTestScript, pingTestResultsFile )
            main.log.info( pingTestResults )
            # ping test

            #============================= Deleting Routes ==================
            main.step( "Check deleting routes installed" )
            main.log.info( "Delete routes to Quagga on host3" )
            main.QuaggaCliHost3.deleteRoutes( prefixesHost3, 1 )
            main.log.info( "Delete routes to Quagga on host4" )
            main.QuaggaCliHost4.deleteRoutes( prefixesHost4, 1 )

            getRoutesResult = main.ONOScli.routes( jsonFormat=True )
            allRoutesActual = \
                main.QuaggaCliHost3.extractActualRoutes( getRoutesResult )
            main.log.info( "allRoutes_actual = " )
            main.log.info( allRoutesActual )

            utilities.assertEquals(
                expect="[]", actual=str( allRoutesActual ),
                onpass="***Route number in SDN-IP is 0, correct!***",
                onfail="***Routes number in SDN-IP is not 0, wrong!***" )

            if( eq( allRoutesStrExpected, allRoutesStrActual ) ):
                main.log.report(
                    "***Routes in SDN-IP after deleting correct!***" )
            else:
                main.log.report(
                    "***Routes in SDN-IP after deleting wrong!***" )

            main.step( "Check intents after deleting routes" )
            getIntentsResult = main.ONOScli.intents( jsonFormat=True )
            routeIntentsActual = \
                main.QuaggaCliHost3.extractActualRouteIntents(
                    getIntentsResult )
            main.log.info( "main.ONOScli.intents()= " )
            main.log.info( routeIntentsActual )
            utilities.assertEquals(
                expect="[]", actual=str( routeIntentsActual ),
                onpass=
                "***MultiPointToSinglePoint Intents number in SDN-IP \
                is 0, correct!***",
                onfail="***MultiPointToSinglePoint Intents number in SDN-IP \
                is 0, wrong!***" )

            if( eq( routeIntentsStrExpected, routeIntentsStrActual ) ):
                main.log.report(
                    "***MultiPointToSinglePoint Intents after deleting \
                    routes correct!***" )
            else:
                main.log.report(
                    "***MultiPointToSinglePoint Intents after deleting \
                    routes wrong!***" )

            time.sleep( 20 )
            # pingTestScript = "~/SDNIP/SdnIpIntentDemo/CASE1-ping-as2host.sh"
            pingTestResultsFile = \
                "~/SDNIP/SdnIpIntentDemo/log/CASE2-Round" \
                + str( roundNum ) + "-ping-results-after-delete-routes-" \
                + strftime( "%Y-%m-%d_%H:%M:%S", localtime() ) + ".txt"
            pingTestResults = main.QuaggaCliHost.pingTest(
                "1.168.30.100", pingTestScript, pingTestResultsFile )
            main.log.info( pingTestResults )
            time.sleep( 30 )

