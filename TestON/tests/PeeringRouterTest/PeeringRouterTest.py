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

	# Copy the json files to config dir
        main.ONOSbench.handle.sendline("cp " + TESTCASE_ROOT_PATH + "/addresses.json ~/onos/tools/package/config/")
        main.ONOSbench.handle.sendline("cp " + TESTCASE_ROOT_PATH + "/sdnip.json ~/onos/tools/package/config/")

        # Launch mininet topology for this case
        MININET_TOPO_FILE = TESTCASE_MININET_ROOT_PATH + "/PeeringRouterMininet.py"
        main.step( "Launch mininet" )
        main.Mininet.handle.sendline("sudo python " + MININET_TOPO_FILE + " " + TESTCASE_MININET_ROOT_PATH)
        main.step("waiting 20 secs for all switches and quagga instances to comeup")
        time.sleep(20)
        main.step( "Test whether Mininet is started" )
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
        main.log.info( "Installing bgprouter feature" )
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

        time.sleep( 30 )

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
        allRoutesActual = \
            main.QuaggaCliHost3.extractActualRoutes( getRoutesResult )

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

        main.ONOScli.logout()
        main.ONOSbench.onosStop(ONOS1Ip);
        main.Mininet.stopNet()
        time.sleep(10)

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
        TESTCASE_ROOT_PATH = main.params[ 'ENV' ][ 'home' ]
        TESTCASE_MININET_ROOT_PATH = TESTCASE_ROOT_PATH + "/mininet"
        SDNIPJSONFILEPATH = TESTCASE_ROOT_PATH + "/sdnip.json"
        main.log.info("sdnip.json file path: "+ SDNIPJSONFILEPATH)
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
        pingTestScript = TESTCASE_ROOT_PATH + "CASE4-ping-as2host.sh"
        pingTestResultsFile = \
        TESTCASE_ROOT_PATH + "CASE4-ping-results-before-delete-routes-" \
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
        pingTestScript = TESTCASE_ROOT_PATH + "CASE4-ping-as2host.sh"
        pingTestResultsFile = \
        TESTCASE_ROOT_PATH + "CASE4-ping-results-after-delete-routes-" \
            + strftime( "%Y-%m-%d_%H:%M:%S", localtime() ) + ".txt"
        pingTestResults = main.QuaggaCliHost.pingTest(
            "1.168.30.100", pingTestScript, pingTestResultsFile )
        main.log.info("Ping test results")
        main.log.info( pingTestResults )
        time.sleep( 10 )

        # main.step( "Test whether Mininet is started" )
        # main.Mininet2.handle.sendline( "xterm host1" )
        # main.Mininet2.handle.expect( "mininet>" )
        main.ONOScli.disconnect()
        main.ONOSbench.onosStop(ONOS1Ip);

    # Route convergence and connectivity test
    def CASE21( self, main):
        import time
        import json
        from operator import eq
        # from datetime import datetime
        from time import localtime, strftime

        main.case("The test case is to help to setup the TestON environment \
            and test new drivers" )
        TESTCASE_ROOT_PATH = main.params[ 'ENV' ][ 'home' ]
        TESTCASE_MININET_ROOT_PATH = TESTCASE_ROOT_PATH + "/routeconvergence/mininet"
        SDNIPJSONFILEPATH = TESTCASE_ROOT_PATH + "/sdnip.json"
        main.log.info("sdnip.json file path: "+ SDNIPJSONFILEPATH)
        
        # Copy the json files to config dir
        main.ONOSbench.handle.sendline("cp " + TESTCASE_ROOT_PATH + "/addresses.json ~/onos/tools/package/config/")
        main.ONOSbench.handle.sendline("cp " + TESTCASE_ROOT_PATH + "/sdnip.json ~/onos/tools/package/config/")

        # Launch mininet topology for this case        
        MININET_TOPO_FILE = TESTCASE_MININET_ROOT_PATH + "/PeeringRouterConvergenceMininet.py"
        main.step( "Launch mininet" )
        main.Mininet.handle.sendline("sudo python " + MININET_TOPO_FILE + " " + TESTCASE_MININET_ROOT_PATH)
        main.step("waiting 20 secs for all switches and quagga instances to comeup")
        time.sleep(20)
        main.step( "Test whether Mininet is started" )
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

        time.sleep( 30 )

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

        #============= Disconnect the BGP session between QuaggaCliHost4 and ONOS ==================
        main.log.info( "Disabling bgp session between QuaggaCliHost4 and 192.168.30.101:" )
        main.QuaggaCliHost4.disable_bgp_peer( "192.168.30.101", "64513" )
        main.log.info( "Sleeping for 150 seconds for network to converge" )
        time.sleep(150)
        # get routes inside SDN-IP
        main.log.info( "Getting Routes from ONOS CLI" )
        getRoutesResult = main.ONOScli.routes( jsonFormat=True )

        # parse routes from ONOS CLI
        newAllRoutesActual = \
            main.QuaggaCliHost3.extractActualRoutes( getRoutesResult )
        newAllRoutesStrActual = str( newAllRoutesActual ).replace( 'u', "" )

        # Expected routes with changed next hop
        newAllRoutesExpected = []
        for prefix in prefixesHost3:
            newAllRoutesExpected.append( prefix + "/" + "192.168.20.1" )
        for prefix in prefixesHost4:
            newAllRoutesExpected.append( prefix + "/" + "192.168.60.2" )
        for prefix in prefixesHost5:
            newAllRoutesExpected.append( prefix + "/" + "192.168.60.2" )
        newAllRoutesStrExpected = str( sorted( newAllRoutesExpected ) )
        main.step( "Check routes installed after convergence-1" )
        main.log.info( "Routes expected:" )
        main.log.info( newAllRoutesStrExpected )
        main.log.info( "Routes got from ONOS CLI after convergence-1:" )
        main.log.info( newAllRoutesStrActual )
        utilities.assertEquals(
            expect=newAllRoutesStrExpected, actual=newAllRoutesStrActual,
            onpass="***Routes in SDN-IP are correct after convergence!***",
            onfail="***Routes in SDN-IP are wrong after convergence!***" )
        if( eq( newAllRoutesStrExpected, newAllRoutesStrActual ) ):
            main.log.report(
                "***Routes in SDN-IP after convergence are correct!***" )
        else:
            main.log.report(
                "***Routes in SDN-IP after convergence are wrong!***" )

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
        allRoutesActual = \
            main.QuaggaCliHost3.extractActualRoutes( getRoutesResult )

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

        main.ONOScli.logout()
        main.ONOSbench.onosStop(ONOS1Ip);
        main.Mininet.stopNet()
        time.sleep(10)

