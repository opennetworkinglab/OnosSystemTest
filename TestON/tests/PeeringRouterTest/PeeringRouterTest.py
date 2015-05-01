# from cupshelpers.config import prefix

# Testing the basic functionality of BgpRouter

class PeeringRouterTest:

    def __init__( self ):
        self.default = ''

    def CASE1 (self, main):
        main.ONOSbench.handle.sendline("cd ~/onos")
        main.step( "Git checkout and pull master" )
        main.ONOSbench.gitCheckout( "master" )
        gitPullResult = main.ONOSbench.gitPull()

        main.step( "Using mvn clean & installi & No Test" )
        cleanInstallResult = main.TRUE
        if gitPullResult == main.TRUE or gitPullResult == 3:
            cleanInstallResult = main.ONOSbench.cleanInstallSkipTest()
        else:
            main.log.warn( "Did not pull new code so skipping mvn " +
                           "clean install" )
        main.ONOSbench.getVersion( report=True )
        main.ONOSbench.handle.sendline("cell sdnip_single_instance")

        main.case("The test case is to help to setup the TestON environment \
            and test new drivers" )
        TESTCASE_ROOT_PATH = main.params[ 'ENV' ][ 'home' ]
        TESTCASE_MININET_ROOT_PATH = TESTCASE_ROOT_PATH + "/vlan/mininet"
        SDNIPJSONFILEPATH = TESTCASE_ROOT_PATH + "/vlan/sdnip.json"
        main.log.info("sdnip.json file path: "+ SDNIPJSONFILEPATH)

        main.ONOSbench.handle.sendline("cell sdnip_single_instance")
        # Copy the json files to config dir
        main.ONOSbench.handle.sendline("cp " + TESTCASE_ROOT_PATH + "/vlan/addresses.json ~/onos/tools/package/config/")
        main.ONOSbench.handle.sendline("cp " + TESTCASE_ROOT_PATH + "/vlan/sdnip.json ~/onos/tools/package/config/")

        cellName = main.params[ 'ENV' ][ 'cellName' ]
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        main.step( "Set cell for ONOS-cli environment" )
        main.ONOScli.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()

        # Copy the cfg files to config dir
        main.log.info("Copying two cfg files to onos etc folder")
        main.ONOSbench.handle.sendline("cp " + TESTCASE_ROOT_PATH + "/org.onosproject.openflow.controller.impl.OpenFlowControllerImpl.cfg ~/onos/tools/package/etc/")
        main.ONOSbench.handle.sendline("cp " + TESTCASE_ROOT_PATH + "/org.onosproject.provider.lldp.impl.LLDPLinkProvider.cfg  ~/onos/tools/package/etc/")
        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()

    def CASE6 ( self, main):
        
        import time
        import json
        from operator import eq
        # from datetime import datetime
        from time import localtime, strftime

        cellName = main.params[ 'ENV' ][ 'cellName' ]
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        main.step( "Set cell for ONOS-cli environment" )
        main.ONOScli.setCell( cellName )
      
        main.ONOScli.startOnosCli( ONOS1Ip )

        getRoutesResult = main.ONOScli.routes( jsonFormat=True )
        allRoutesActual = \
            main.QuaggaCliHost3.extractActualRoutes( getRoutesResult )

        main.log.info( "allRoutes_actual = " )
        main.log.info( allRoutesActual )

        allRoutesStrExpected = []
        allRoutesStrActual = str( allRoutesActual )

        if( eq( "[]", allRoutesStrActual ) ):
            main.log.report( "***Routes in BgpRouter after deleting correct!***" )
            routeCheckResult2 = main.TRUE
        else:
            main.log.report( "***Routes in BgpRouter after deleting wrong!***" )
            routeCheckResult2 = main.FALSE

        time.sleep(10)


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

        #Inject the config file
        main.ONOSbench.handle.sendline("onos-topo-cfg $OC1 bgprouter.json")
        listResult = main.ONOScli.devices( jsonFormat=False )
        main.log.info( listResult )

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




        main.ONOScli.logout()
        main.ONOSbench.onosStop(ONOS1Ip);
        main.Mininet.stopNet()
        time.sleep(10)

    def CASE5( self, main ):
        import time
        import json
        from operator import eq
        # from datetime import datetime
        from time import localtime, strftime

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
        main.log.info("Waiting until all modules are up")
        time.sleep(10)

        #Inject the config file
        main.log.info("Injecting config file: bgprouter.json")
        main.ONOSbench.handle.sendline("onos-topo-cfg $OC1 ~/TestON/tests/PeeringRouterTest/bgprouter.json")
        listResult = main.ONOScli.devices( jsonFormat=False )
        main.log.info( listResult )
        time.sleep(10)

        # Activate bgprouter app
        main.log.info( "Installing bgprouter app" )
        main.ONOScli.handle.sendline("app activate org.onosproject.bgprouter")
        time.sleep( 10 )

        # Launch mininet topology for this case
        MININET_TOPO_FILE = TESTCASE_MININET_ROOT_PATH + "/PeeringRouterMininetVlan.py"
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

        main.log.info("Restart ONOS cli")
        main.ONOScli.logout()
        main.ONOScli.startOnosCli( ONOS1Ip )

        main.step( "Get devices in the network" )
        listResult = main.ONOScli.devices( jsonFormat=False )
        main.log.info( listResult )
        time.sleep( 30 )

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

        time.sleep( 60 )

        # get routes inside SDN-IP
        getRoutesResult = main.ONOScli.routes( jsonFormat=True )

        main.log.info(getRoutesResult)

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

        if( eq( allRoutesStrExpected, allRoutesStrActual ) ):
            main.log.report(
                "***Routes in BgpRouter after adding routes are correct!***" )
            routeCheckResult1 = main.TRUE
        else:
            main.log.report(
                "***Routes in BgpRouter after adding routes are wrong!***" )
            routeCheckResult1 = main.FALSE

        time.sleep(20)

        #============================= Ping Test ========================
        pingTestResults = main.TRUE
        sources = ["as2host", "as3host", "as6host"]
        targets = ["192.168.10.101", "192.168.20.101", "192.168.30.101", "192.168.60.101"]
        for source in sources:
            for target in targets:
                r = main.Mininet.pingHost(SRC=source, TARGET=target)
                if r == main.FALSE:
                    pingTestResults = main.FALSE      

        pingTestResult1 = pingTestResults

        pingTestResults = main.TRUE
        for m in range( 3, 6 ):
            for n in range( 1, 10 ):
                hostIp = str( m ) + ".0." + str( n ) + ".1"
                r = main.Mininet.pingHost(SRC="as2host", TARGET=hostIp)
                if r == main.FALSE:
                    pingTestResults = main.FALSE
        pingTestResult2 = pingTestResults
        
        if pingTestResult1 and pingTestResult2:
            main.log.report("*** Ping test pass ***")
        else:
            main.log.report("*** Ping test fail ***")

        time.sleep(20)
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

        allRoutesStrExpected = []
        allRoutesStrActual = str( allRoutesActual )

        if( eq( "[]", allRoutesStrActual ) ):
            main.log.report( "***Routes in BgpRouter after deleting correct!***" )
            routeCheckResult2 = main.TRUE
        else:
            main.log.report( "***Routes in BgpRouter after deleting wrong!***" )
            routeCheckResult2 = main.FALSE

        time.sleep(10)
        #============================= Ping Test ========================
        pingTestResults = main.TRUE
        for m in range( 4, 6 ):
            for n in range( 1, 10 ):
                hostIp = str( m ) + ".0." + str( n ) + ".1"
                r = main.Mininet.pingHost(SRC="as2host", TARGET=hostIp)
                if r == main.TRUE:
                    pingTestResults = main.FALSE

        pingTestResult3 = pingTestResults
   
        if pingTestResult3:
            main.log.report("*** Ping test pass ***")
        else:
            main.log.report("*** Ping test fail ***")

        time.sleep(20);

        finalTestResult = pingTestResult1 and pingTestResult2 and pingTestResult3 and routeCheckResult1 and routeCheckResult2
        utilities.assertEquals(
            expect=main.TRUE, actual=finalTestResult,
            onpass="*** TEST CASE 5 passed ***",
            onfail="*** TEST CASE 5 failed ***" )

        main.ONOScli.logout()
        main.log.info("ONOS cli logout")
        time.sleep(20);
        main.ONOSbench.onosStop(ONOS1Ip);
        main.log.info("onos stop")
        time.sleep(20);
        main.Mininet.stopNet()
        main.log.info("mininet stop")
        time.sleep(20)


    def CASE7( self, main ):
        import time
        import json
        from operator import eq
        # from datetime import datetime
        from time import localtime, strftime

        TESTCASE_ROOT_PATH = main.params[ 'ENV' ][ 'home' ]
        TESTCASE_MININET_ROOT_PATH = TESTCASE_ROOT_PATH + "/vlan/mininet"
        SDNIPJSONFILEPATH = TESTCASE_ROOT_PATH + "/vlan/sdnip.json"
        main.log.info("sdnip.json file path: "+ SDNIPJSONFILEPATH)

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

        #Inject the config file
        main.log.info("Injecting config file: bgprouter.json")
        main.ONOSbench.handle.sendline("onos-topo-cfg $OC1 ~/TestON/tests/PeeringRouterTest/bgprouter.json")
        listResult = main.ONOScli.devices( jsonFormat=False )
        main.log.info( listResult )

        # Activate bgprouter app
        main.log.info( "Installing bgprouter app" )
        main.ONOScli.handle.sendline("app activate org.onosproject.bgprouter")
        time.sleep( 10 )

        # Launch mininet topology for this case
        MININET_TOPO_FILE = TESTCASE_MININET_ROOT_PATH + "/PeeringRouterMininetVlan.py"
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
        prefixesHost3 = main.QuaggaCliHost3.generatePrefixes( 3, 2000 )
        main.log.info( prefixesHost3 )
        # generate route with next hop
        for prefix in prefixesHost3:
            allRoutesExpected.append( prefix + "/" + "192.168.20.1" )
        routeIntentsExpectedHost3 = \
            main.QuaggaCliHost3.generateExpectedOnePeerRouteIntents(
            prefixesHost3, "192.168.20.1", "00:00:00:00:02:02",
            SDNIPJSONFILEPATH )
        main.log.info( "Generate prefixes for host4" )
        prefixesHost4 = main.QuaggaCliHost4.generatePrefixes( 4, 2000 )
        main.log.info( prefixesHost4 )
        # generate route with next hop
        for prefix in prefixesHost4:
            allRoutesExpected.append( prefix + "/" + "192.168.30.1" )
        routeIntentsExpectedHost4 = \
            main.QuaggaCliHost4.generateExpectedOnePeerRouteIntents(
            prefixesHost4, "192.168.30.1", "00:00:00:00:03:01",
            SDNIPJSONFILEPATH )

        main.log.info( "Generate prefixes for host5" )
        prefixesHost5 = main.QuaggaCliHost5.generatePrefixes( 5, 2000 )
        main.log.info( prefixesHost5 )
        for prefix in prefixesHost5:
            allRoutesExpected.append( prefix + "/" + "192.168.60.2" )
        routeIntentsExpectedHost5 = \
            main.QuaggaCliHost5.generateExpectedOnePeerRouteIntents(
            prefixesHost5, "192.168.60.1", "00:00:00:00:06:02",
            SDNIPJSONFILEPATH )

        routeIntentsExpected = routeIntentsExpectedHost3 + \
            routeIntentsExpectedHost4 + routeIntentsExpectedHost5

        main.ONOScli.logout()
        main.ONOScli.startOnosCli( ONOS1Ip )

        main.step( "Get devices in the network" )
        listResult = main.ONOScli.devices( jsonFormat=False )
        main.log.info( listResult )
        time.sleep( 10 )
        main.step( "Login all BGP peers and add routes into peers" )

        main.log.info( "Login Quagga CLI on host3" )
        main.QuaggaCliHost3.loginQuagga( "1.168.30.2" )
        main.log.info( "Enter configuration model of Quagga CLI on host3" )
        main.QuaggaCliHost3.enterConfig( 64514 )
        main.log.info( "Add routes to Quagga on host3" )
        main.QuaggaCliHost3.addRoutes( prefixesHost3, 1 )

        time.sleep(20)

        main.log.info( "Login Quagga CLI on host4" )
        main.QuaggaCliHost4.loginQuagga( "1.168.30.3" )
        main.log.info( "Enter configuration model of Quagga CLI on host4" )
        main.QuaggaCliHost4.enterConfig( 64516 )
        main.log.info( "Add routes to Quagga on host4" )
        main.QuaggaCliHost4.addRoutes( prefixesHost4, 1 )

        time.sleep(20)

        main.log.info( "Login Quagga CLI on host5" )
        main.QuaggaCliHost5.loginQuagga( "1.168.30.5" )
        main.log.info( "Enter configuration model of Quagga CLI on host5" )
        main.QuaggaCliHost5.enterConfig( 64521 )
        main.log.info( "Add routes to Quagga on host5" )
        main.QuaggaCliHost5.addRoutes( prefixesHost5, 1 )

        time.sleep(80)

        main.ONOScli.logout()
        main.ONOScli.startOnosCli( ONOS1Ip )

        # get routes inside SDN-IP
        getRoutesResult = main.ONOScli.routes( jsonFormat=True )

        # parse routes from ONOS CLI
        allRoutesActual = \
           main.QuaggaCliHost3.extractActualRoutes( getRoutesResult )

        allRoutesStrExpected = str( sorted( allRoutesExpected ) )
        allRoutesStrActual = str( allRoutesActual ).replace( 'u', "" )

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
        if( eq( allRoutesStrExpected, allRoutesStrActual ) ):
            main.log.report(
                "***Routes in BgpRouter after adding routes are correct!***" )
            routeCheckResult1 = main.TRUE
        else:
            main.log.report(
                "***Routes in BgpRouter after adding routes are wrong!***" )
            routeCheckResult1 = main.FALSE

        time.sleep(20)

        #============================= Ping Test ========================
        pingTestResults = main.TRUE
        for m in range( 3, 6 ):
            for n in range( 1, 10 ):
                hostIp = str( m ) + ".0." + str( n ) + ".1"
                r = main.Mininet.pingHost(SRC="as2host", TARGET=hostIp)
                if r == main.FALSE:
                    pingTestResults = main.FALSE

        pingTestResult1 = pingTestResults

        if pingTestResult1 == main.TRUE:
            main.log.report("*** Ping test pass ***")
        else:
            main.log.report("*** Ping test fail ***")

        finalTestResult = pingTestResult1 and routeCheckResult1
        utilities.assertEquals(
            expect=main.TRUE, actual=finalTestResult,
            onpass="*** TEST CASE 7 passed ***",
            onfail="*** TEST CASE 7 failed ***" )

        time.sleep(10)

        main.ONOScli.logout()
        main.log.info("ONOS cli logout")
        time.sleep(20);
        main.ONOSbench.onosStop(ONOS1Ip);
        main.log.info("onos stop")
        time.sleep(20);
        main.Mininet.stopNet()
        main.log.info("mininet stop")
        time.sleep(20)

    # Route flap test (Add a route and detele it very fast 20 times) in VLAN configuration
    def CASE8( self, main ):
        import time
        import json
        from operator import eq
        # from datetime import datetime
        from time import localtime, strftime

        main.case("The test case is to help to setup the TestON environment \
            and test new drivers" )
        TESTCASE_ROOT_PATH = main.params[ 'ENV' ][ 'home' ]
        TESTCASE_MININET_ROOT_PATH = TESTCASE_ROOT_PATH + "/vlan/mininet"
        SDNIPJSONFILEPATH = TESTCASE_ROOT_PATH + "/vlan/sdnip.json"
        main.log.info("sdnip.json file path: "+ SDNIPJSONFILEPATH)

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

        #Inject the config file
        main.log.info("Injecting config file: bgprouter.json")
        main.ONOSbench.handle.sendline("onos-topo-cfg $OC1 ~/TestON/tests/PeeringRouterTest/bgprouter.json")
        listResult = main.ONOScli.devices( jsonFormat=False )
        main.log.info( listResult )

        # Activate bgprouter app
        main.log.info( "Installing bgprouter app" )
        main.ONOScli.handle.sendline("app activate org.onosproject.bgprouter")
        time.sleep( 10 )

        # Launch mininet topology for this case
        MININET_TOPO_FILE = TESTCASE_MININET_ROOT_PATH + "/PeeringRouterMininetVlan.py"
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
        prefixesHost3 = main.QuaggaCliHost3.generatePrefixes( 3, 1 )
        main.log.info( prefixesHost3 )
        # generate route with next hop
        for prefix in prefixesHost3:
            allRoutesExpected.append( prefix + "/" + "192.168.20.1" )
        routeIntentsExpectedHost3 = \
            main.QuaggaCliHost3.generateExpectedOnePeerRouteIntents(
            prefixesHost3, "192.168.20.1", "00:00:00:00:02:02",
            SDNIPJSONFILEPATH )

        main.log.info( "Generate prefixes for host5" )
        prefixesHost5 = main.QuaggaCliHost5.generatePrefixes( 5, 1 )
        main.log.info( prefixesHost5 )
        for prefix in prefixesHost5:
            allRoutesExpected.append( prefix + "/" + "192.168.60.2" )
        routeIntentsExpectedHost5 = \
            main.QuaggaCliHost5.generateExpectedOnePeerRouteIntents(
            prefixesHost5, "192.168.60.1", "00:00:00:00:06:02",
            SDNIPJSONFILEPATH )
  
        routeIntentsExpected = routeIntentsExpectedHost3 + \
            routeIntentsExpectedHost5

        main.ONOScli.logout()
        main.ONOScli.startOnosCli( ONOS1Ip )

        main.step( "Get devices in the network" )
        listResult = main.ONOScli.devices( jsonFormat=False )
        main.log.info( listResult )
        time.sleep( 10 )
        main.step( "Login all BGP peers and add routes into peers" )

        main.log.info( "Login Quagga CLI on host5" )
        main.QuaggaCliHost5.loginQuagga( "1.168.30.5" )
        main.log.info( "Enter configuration model of Quagga CLI on host5" )
        main.QuaggaCliHost5.enterConfig( 64521 )
        main.log.info( "Add routes to Quagga on host5" )
        main.QuaggaCliHost5.addRoutes( prefixesHost5, 1 )

        main.log.info( "Login Quagga CLI on host3" )
        main.QuaggaCliHost3.loginQuagga( "1.168.30.2" )
        main.log.info( "Enter configuration model of Quagga CLI on host3" )
        main.QuaggaCliHost3.enterConfig( 64514 )
        main.log.info( "Add and delete a route to Quagga on host3 20 times" )
        for i in range(0, 20):
            main.QuaggaCliHost3.addRoutes( prefixesHost3, 1 )
            main.log.info("Add a route %s times", i)
            main.QuaggaCliHost3.deleteRoutes( prefixesHost3, 1 )
            main.log.info("Delete the route")
            time.sleep(0.1)   
        
        main.QuaggaCliHost3.addRoutes( prefixesHost3, 1 )
        main.log.info("Add the route finally and wait for 10 sec")

        #============================= Ping Test ========================
        for j in range(0, 30):
            r = main.Mininet.pingHost(SRC="as6host", TARGET="3.0.0.1")

        pingTestResult1 = r
   
        if pingTestResult1:
            main.log.report("*** Ping test pass ***")
        else:
            main.log.report("*** Ping test fail ***")

        #time.sleep(20)

        main.ONOScli.logout()
        main.ONOScli.startOnosCli( ONOS1Ip )

        # get routes inside SDN-IP
        getRoutesResult = main.ONOScli.routes( jsonFormat=True )

        # parse routes from ONOS CLI
        allRoutesActual = \
           main.QuaggaCliHost3.extractActualRoutes( getRoutesResult )

        allRoutesStrExpected = str( sorted( allRoutesExpected ) )
        allRoutesStrActual = str( allRoutesActual ).replace( 'u', "" )

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
        if( eq( allRoutesStrExpected, allRoutesStrActual ) ):
            main.log.report(
                "***Routes in BgpRouter after adding routes are correct!***" )
            routeCheckResult1 = main.TRUE
        else:
            main.log.report(
                "***Routes in BgpRouter after adding routes are wrong!***" )
            routeCheckResult1 = main.FALSE
 
        main.log.info( "Login Quagga CLI on host3" )
        main.QuaggaCliHost3.loginQuagga( "1.168.30.2" )
        main.log.info( "Enter configuration model of Quagga CLI on host3" )
        main.QuaggaCliHost3.enterConfig( 64514 )
        main.log.info( "Add and delete a route to Quagga on host3 20 times" )
        for i in range(0, 20):
            main.QuaggaCliHost3.addRoutes( prefixesHost3, 1 )
            main.log.info("Add a route %s times", i)
            main.QuaggaCliHost3.deleteRoutes( prefixesHost3, 1 )
            main.log.info("Delete the route")
            time.sleep(0.1)
        
        main.QuaggaCliHost5.deleteRoutes( prefixesHost5, 1 )

        # get routes inside SDN-IP
        getRoutesResult = main.ONOScli.routes( jsonFormat=True )

        # parse routes from ONOS CLI
        allRoutesActual = \
           main.QuaggaCliHost3.extractActualRoutes( getRoutesResult )

        allRoutesStrActual = str( allRoutesActual ).replace( 'u', "" )

        # get routes inside SDN-IP
        getRoutesResult = main.ONOScli.routes( jsonFormat=True )

        # parse routes from ONOS CLI
        allRoutesActual = \
           main.QuaggaCliHost3.extractActualRoutes( getRoutesResult )

        allRoutesStrActual = str( allRoutesActual )
        main.step( "Check routes installed" )
        main.log.info( "Routes expected: []" )
        main.log.info( "Routes get from ONOS CLI:" )
        main.log.info( allRoutesStrActual )
        if( eq( "[]", allRoutesStrActual ) ):
            main.log.report(
                "***Routes in BgpRouter after deleting routes are correct!***" )
            routeCheckResult2 = main.TRUE
        else:
            main.log.report(
                "***Routes in BgpRouter after deleting routes are wrong!***" )
            routeCheckResult2 = main.FALSE

        for j in range(0, 5):
            r = main.Mininet.pingHost(SRC="as6host", TARGET="3.0.0.1")
        
        if r == main.FALSE:
            main.log.report("*** Ping test pass ***")
            pingTestResult2 = main.TRUE
        else:
            main.log.report("*** Ping test fail ***")
            pingTestResult2 = main.FALSE

        finalTestResult = pingTestResult1 and pingTestResult2 and routeCheckResult1 and routeCheckResult2
        utilities.assertEquals(
            expect=main.TRUE, actual=finalTestResult,
            onpass="*** TEST CASE 8 passed ***",
            onfail="*** TEST CASE 8 failed ***" )

        main.ONOScli.logout()
        main.log.info("ONOS cli logout")
        time.sleep(20);
        main.ONOSbench.onosStop(ONOS1Ip);
        main.log.info("onos stop")
        time.sleep(20);
        main.Mininet.stopNet()
        main.log.info("mininet stop")
        time.sleep(20)

    # Route flap test (change the next-hop very fast 20 times) in VLAN configuration
    def CASE9( self, main):
        import time
        import json
        from operator import eq
        # from datetime import datetime
        from time import localtime, strftime

        main.case("The test case is to help to setup the TestON environment \
            and test new drivers" )
        TESTCASE_ROOT_PATH = main.params[ 'ENV' ][ 'home' ]
        TESTCASE_MININET_ROOT_PATH = TESTCASE_ROOT_PATH + "/vlan/routeconvergence/mininet"
        SDNIPJSONFILEPATH = TESTCASE_ROOT_PATH + "/vlan/sdnip.json"
        main.log.info("sdnip.json file path: "+ SDNIPJSONFILEPATH)

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

        #Inject the config file
        main.log.info("Injecting config file: bgprouter.json")
        main.ONOSbench.handle.sendline("onos-topo-cfg $OC1 ~/TestON/tests/PeeringRouterTest/bgprouter.json")
        listResult = main.ONOScli.devices( jsonFormat=False )
        main.log.info( listResult )

        # Activate bgprouter app
        main.log.info( "Installing bgprouter app" )
        main.ONOScli.handle.sendline("app activate org.onosproject.bgprouter")
        time.sleep( 10 )

        # Launch mininet topology for this case        
        MININET_TOPO_FILE = TESTCASE_MININET_ROOT_PATH + "/PeeringRouterConvergenceVlanMininet.py"
        main.step( "Launch mininet" )
        main.Mininet.handle.sendline("sudo python " + MININET_TOPO_FILE + " " + TESTCASE_MININET_ROOT_PATH)
        main.step("waiting 20 secs for all switches and quagga instances to comeup")
        time.sleep(20)
        main.step( "Test whether Mininet is started" )
        main.log.info( "Login Quagga CLI on host3" )
        result = main.QuaggaCliHost3.loginQuagga( "1.168.30.2" )
        #if result is not main.TRUE:
        #     main.log.report("Mininet is not started...Aborting")
        #     main.Mininet.stopNet()
        #     main.cleanup()
        #     main.exit()
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

        main.ONOScli.logout()
        main.ONOScli.startOnosCli( ONOS1Ip )

        main.step( "Get devices in the network" )
        listResult = main.ONOScli.devices( jsonFormat=False )
        main.log.info( listResult )
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
        if( eq( allRoutesStrExpected, allRoutesStrActual ) ):
            main.log.report(
                "***Routes in BgpRouter after adding routes are correct!***" )
            routeCheckResult1 = main.TRUE
        else:
            main.log.report(
                "***Routes in BgpRouter after adding routes are wrong!***" )
            routeCheckResult2 = main.FALSE

        #============= Flap the BGP session between QuaggaCliHost4 and ONOS ==================
        main.log.info( "Disabling bgp session and enable it 20 times very fast between QuaggaCliHost4 and 192.168.30.101:" )
        for i in range(0, 20):
            main.log.info("Disable it %s times", i)
            main.QuaggaCliHost4.disable_bgp_peer( "192.168.30.101", "64513")
            main.log.info("Enable it again")
            main.QuaggaCliHost4.enable_bgp_peer( "192.168.30.101", "64513" )
            time.sleep(0.1)
        main.log.info("Disable it finally")
        main.QuaggaCliHost4.disable_bgp_peer( "192.168.30.101", "64513")            

        main.log.info( "Sleeping for 30 seconds for network to converge" )
        time.sleep(60)
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
        if( eq( newAllRoutesStrExpected, newAllRoutesStrActual ) ):
            main.log.report(
                "***Routes in BgpRouter after convergence are correct!***" )
            routeCheckResult2 = main.TRUE
        else:
            main.log.report(
                "***Routes in BgpRouter after convergence are wrong!***" )
            routeCheckResult2 = main.FALSE

        main.log.info( "Sleeping for 60 seconds for network to converge" )
        time.sleep(60)

        #============================= Ping Test ========================
        pingTestResults = main.TRUE
        for m in range( 3, 6 ):
            for n in range( 1, 10 ):
                hostIp = str( m ) + ".0." + str( n ) + ".1"
                r = main.Mininet.pingHost(SRC="as2host", TARGET=hostIp)
                if r == main.FALSE:
                    pingTestResults = main.FALSE
        pingTestResult1 = pingTestResults

        if pingTestResult1:
            main.log.report("*** Ping test pass ***")
        else:
            main.log.report("*** Ping test fail ***")     

        #============= Flap the BGP session between QuaggaCliHost4 and ONOS ==================
        main.log.info( "Disabling bgp session and enable it 20 times very fast between QuaggaCliHost4 and 192.168.30.101:" )
        for i in range(0, 20):
            main.log.info("Disable it %s times", i)
            main.QuaggaCliHost4.disable_bgp_peer( "192.168.30.101", "64513")
            main.log.info("Enable it again")
            main.QuaggaCliHost4.enable_bgp_peer( "192.168.30.101", "64513" )
            time.sleep(0.1)

        main.log.info( "Sleeping for 60 seconds for network to converge" )
        time.sleep(60)

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
            newAllRoutesExpected.append( prefix + "/" + "192.168.30.1" )
        for prefix in prefixesHost5:
            newAllRoutesExpected.append( prefix + "/" + "192.168.60.2" )
        newAllRoutesStrExpected = str( sorted( newAllRoutesExpected ) )
        main.step( "Check routes installed after convergence-2" )
        main.log.info( "Routes expected:" )
        main.log.info( newAllRoutesStrExpected )
        main.log.info( "Routes got from ONOS CLI after convergence-2:" )
        main.log.info( newAllRoutesStrActual )
        if( eq( newAllRoutesStrExpected, newAllRoutesStrActual ) ):
            main.log.report(
                "***Routes in BgpRouter after convergence are correct!***" )
            routeCheckResult3 = main.TRUE
        else:
            main.log.report(
                "***Routes in BgpRouter after convergence are wrong!***" )
            routeCheckResult3 = main.FALSE

        #============================= Ping Test ========================
        pingTestResults = main.TRUE
        for m in range( 3, 6 ):
            for n in range( 1, 10 ):
                hostIp = str( m ) + ".0." + str( n ) + ".1"
                r = main.Mininet.pingHost(SRC="as2host", TARGET=hostIp)
                if r == main.FALSE:
                    pingTestResults = main.FALSE
        pingTestResult2 = pingTestResults
        
        if pingTestResult2:
            main.log.report("*** Ping test pass ***")
        else:
            main.log.report("*** Ping test fail ***")

        finalTestResult = pingTestResult1 and pingTestResult2 and routeCheckResult1 and routeCheckResult2 and routeCheckResult3
        utilities.assertEquals(
            expect=main.TRUE, actual=finalTestResult,
            onpass="*** TEST CASE 9 passed ***",
            onfail="*** TEST CASE 9 failed ***" )

        main.ONOScli.logout()
        main.log.info("ONOS cli logout")
        time.sleep(20);
        main.ONOSbench.onosStop(ONOS1Ip);
        main.log.info("onos stop")
        time.sleep(20);
        main.Mininet.stopNet()
        main.log.info("mininet stop")
        time.sleep(20)

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

        cellName = main.params[ 'ENV' ][ 'cellName' ]
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        main.step( "Set cell for ONOS-cli environment" )
        main.ONOScli.setCell( cellName )
        main.ONOSbench.handle.sendline("cell sdnip_single_instance")
        verifyResult = main.ONOSbench.verifyCell()

        # Copy the cfg files to config dir
        main.log.info("Copying two cfg files to onos etc folder")
        main.ONOSbench.handle.sendline("cp " + TESTCASE_ROOT_PATH + "/org.onosproject.openflow.controller.impl.OpenFlowControllerImpl.cfg ~/onos/tools/package/etc/")
        main.ONOSbench.handle.sendline("cp " + TESTCASE_ROOT_PATH + "/org.onosproject.provider.lldp.impl.LLDPLinkProvider.cfg  ~/onos/tools/package/etc/")
        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()

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

        #Inject the config file
        main.log.info("Injecting config file: bgprouter.json")
        main.ONOSbench.handle.sendline("onos-topo-cfg $OC1 ~/TestON/tests/PeeringRouterTest/bgprouter.json")
        listResult = main.ONOScli.devices( jsonFormat=False )
        main.log.info( listResult )

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




        #============= Enabling the BGP session between QuaggaCliHost4 and ONOS ==================
        main.log.info( "Enabling bgp session between QuaggaCliHost4 and 192.168.30.101:" )
        main.QuaggaCliHost4.enable_bgp_peer( "192.168.30.101", "64513" )
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
            newAllRoutesExpected.append( prefix + "/" + "192.168.30.1" )
        for prefix in prefixesHost5:
            newAllRoutesExpected.append( prefix + "/" + "192.168.60.2" )
        newAllRoutesStrExpected = str( sorted( newAllRoutesExpected ) )
        main.step( "Check routes installed after convergence-2" )
        main.log.info( "Routes expected:" )
        main.log.info( newAllRoutesStrExpected )
        main.log.info( "Routes got from ONOS CLI after convergence-2:" )
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




        main.ONOScli.logout()
        main.ONOSbench.onosStop(ONOS1Ip);
        main.Mininet.stopNet()
        time.sleep(10)

    # Route convergence and connectivity test with Route Server
    def CASE22( self, main):
        import time
        import json
        from operator import eq
        # from datetime import datetime
        from time import localtime, strftime

        main.case("The test case is to help to setup the TestON environment \
            and test new drivers" )
        TESTCASE_ROOT_PATH = main.params[ 'ENV' ][ 'home' ]
        TESTCASE_MININET_ROOT_PATH = TESTCASE_ROOT_PATH + "/routeserver/mininet"
        SDNIPJSONFILEPATH = TESTCASE_ROOT_PATH + "/routeserver/sdnip.json"
        main.log.info("sdnip.json file path: "+ SDNIPJSONFILEPATH)        

        # Copy the json files to config dir
        main.ONOSbench.handle.sendline("cp " + TESTCASE_ROOT_PATH + "/routeserver/addresses.json ~/onos/tools/package/config/")
        main.ONOSbench.handle.sendline("cp " + TESTCASE_ROOT_PATH + "/routeserver/sdnip.json ~/onos/tools/package/config/")

        cellName = main.params[ 'ENV' ][ 'cellName' ]
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        main.step( "Set cell for ONOS-cli environment" )
        main.ONOScli.setCell( cellName )
        main.ONOSbench.handle.sendline("cell sdnip_single_instance")
        verifyResult = main.ONOSbench.verifyCell()

        # Copy the cfg files to config dir
        main.log.info("Copying two cfg files to onos etc folder")
        main.ONOSbench.handle.sendline("cp " + TESTCASE_ROOT_PATH + "/org.onosproject.openflow.controller.impl.OpenFlowControllerImpl.cfg ~/onos/tools/package/etc/")
        main.ONOSbench.handle.sendline("cp " + TESTCASE_ROOT_PATH + "/org.onosproject.provider.lldp.impl.LLDPLinkProvider.cfg  ~/onos/tools/package/etc/")
        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()

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

        #Inject the config file
        main.log.info("Injecting config file: bgprouter.json")
        main.ONOSbench.handle.sendline("onos-topo-cfg $OC1 ~/TestON/tests/PeeringRouterTest/bgprouter.json")
        listResult = main.ONOScli.devices( jsonFormat=False )
        main.log.info( listResult )

        # Launch mininet topology for this case        
        MININET_TOPO_FILE = TESTCASE_MININET_ROOT_PATH + "/PeeringRouteServerMininet.py"
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

        #============================= Ping Test ========================



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



        #============= Enabling the BGP session between QuaggaCliHost4 and ONOS ==================
        main.log.info( "Enabling bgp session between QuaggaCliHost4 and 192.168.30.101:" )
        main.QuaggaCliHost4.enable_bgp_peer( "192.168.30.101", "64513" )
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
            newAllRoutesExpected.append( prefix + "/" + "192.168.30.1" )
        for prefix in prefixesHost5:
            newAllRoutesExpected.append( prefix + "/" + "192.168.60.2" )
        newAllRoutesStrExpected = str( sorted( newAllRoutesExpected ) )
        main.step( "Check routes installed after convergence-2" )
        main.log.info( "Routes expected:" )
        main.log.info( newAllRoutesStrExpected )
        main.log.info( "Routes got from ONOS CLI after convergence-2:" )
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




        main.ONOScli.logout()
        main.ONOSbench.onosStop(ONOS1Ip);
        main.Mininet.stopNet()
        time.sleep(10)

    # Route convergence and connectivity test in VLAN configuration
    def CASE31( self, main):
        import time
        import json
        from operator import eq
        # from datetime import datetime
        from time import localtime, strftime

        main.case("The test case is to help to setup the TestON environment \
            and test new drivers" )
        TESTCASE_ROOT_PATH = main.params[ 'ENV' ][ 'home' ]
        TESTCASE_MININET_ROOT_PATH = TESTCASE_ROOT_PATH + "/vlan/routeconvergence/mininet"
        SDNIPJSONFILEPATH = TESTCASE_ROOT_PATH + "/vlan/sdnip.json"
        main.log.info("sdnip.json file path: "+ SDNIPJSONFILEPATH)

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

        #Inject the config file
        main.log.info("Injecting config file: bgprouter.json")
        main.ONOSbench.handle.sendline("onos-topo-cfg $OC1 ~/TestON/tests/PeeringRouterTest/bgprouter.json")
        listResult = main.ONOScli.devices( jsonFormat=False )
        main.log.info( listResult )

        # Activate bgprouter app
        main.log.info( "Installing bgprouter app" )
        main.ONOScli.handle.sendline("app activate org.onosproject.bgprouter")
        time.sleep( 10 )

        # Launch mininet topology for this case        
        MININET_TOPO_FILE = TESTCASE_MININET_ROOT_PATH + "/PeeringRouterConvergenceVlanMininet.py"
        main.step( "Launch mininet" )
        main.Mininet.handle.sendline("sudo python " + MININET_TOPO_FILE + " " + TESTCASE_MININET_ROOT_PATH)
        main.step("waiting 20 secs for all switches and quagga instances to comeup")
        time.sleep(20)
        main.step( "Test whether Mininet is started" )
        main.log.info( "Login Quagga CLI on host3" )
        result = main.QuaggaCliHost3.loginQuagga( "1.168.30.2" )
        #if result is not main.TRUE:
        #     main.log.report("Mininet is not started...Aborting")
        #     main.Mininet.stopNet()
        #     main.cleanup()
        #     main.exit()
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

        main.ONOScli.logout()
        main.ONOScli.startOnosCli( ONOS1Ip )

        main.step( "Get devices in the network" )
        listResult = main.ONOScli.devices( jsonFormat=False )
        main.log.info( listResult )
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
        if( eq( allRoutesStrExpected, allRoutesStrActual ) ):
            main.log.report(
                "***Routes in BgpRouter after adding routes are correct!***" )
            routeCheckResult1 = main.TRUE
        else:
            main.log.report(
                "***Routes in BgpRouter after adding routes are wrong!***" )
            routeCheckResult1 = main.FALSE

        time.sleep( 90)

        #============================= Ping Test ========================
        pingTestResults = main.TRUE
        sources = ["as2host", "as3host", "as6host"]
        targets = ["192.168.10.101", "192.168.20.101", "192.168.30.101", "192.168.60.101"]
        for source in sources:
            for target in targets:
                r = main.Mininet.pingHost(SRC=source, TARGET=target)
                if r == main.FALSE:
                    pingTestResults = main.FALSE
        pingTestResult1 = pingTestResults

        pingTestResults = main.TRUE
        for m in range( 3, 6 ):
            for n in range( 1, 10 ):
                hostIp = str( m ) + ".0." + str( n ) + ".1"
                r = main.Mininet.pingHost(SRC="as2host", TARGET=hostIp)
                if r == main.FALSE:
                    pingTestResults = main.FALSE
        pingTestResult2 = pingTestResults

        if pingTestResult1 and pingTestResult2:
            main.log.report("*** Ping test pass ***")
        else:
            main.log.report("*** Ping test fail ***")

        time.sleep(20)

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
        if( eq( newAllRoutesStrExpected, newAllRoutesStrActual ) ):
            main.log.report(
                "***Routes in BgpRouter after convergence are correct!***" )
            routeCheckResult2 = main.TRUE
        else:
            main.log.report(
                "***Routes in BgpRouter after convergence are wrong!***" )
            routeCheckResult2 = main.FALSE

        time.sleep(120)       
 
        #============================= Ping Test ========================
        pingTestResults = main.TRUE
        sources = ["as2host", "as3host", "as6host"]
        targets = ["192.168.10.101", "192.168.20.101", "192.168.30.101", "192.168.60.101"]
        for source in sources:
            for target in targets:
                r = main.Mininet.pingHost(SRC=source, TARGET=target)
                if r == main.FALSE:
                    pingTestResults = main.FALSE
        pingTestResult3 = pingTestResults

        pingTestResults = main.TRUE
        for m in range( 3, 6 ):
            for n in range( 1, 10 ):
                hostIp = str( m ) + ".0." + str( n ) + ".1"
                r = main.Mininet.pingHost(SRC="as2host", TARGET=hostIp)
                if r == main.FALSE:
                    pingTestResults = main.FALSE
        pingTestResult4 = pingTestResults

        if pingTestResult4 and pingTestResult4:
            main.log.report("*** Ping test pass ***")
        else:
            main.log.report("*** Ping test fail ***")

        time.sleep(20)

        #============= Enabling the BGP session between QuaggaCliHost4 and ONOS ==================
        main.log.info( "Enabling bgp session between QuaggaCliHost4 and 192.168.30.101:" )
        main.QuaggaCliHost4.enable_bgp_peer( "192.168.30.101", "64513" )
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
            newAllRoutesExpected.append( prefix + "/" + "192.168.30.1" )
        for prefix in prefixesHost5:
            newAllRoutesExpected.append( prefix + "/" + "192.168.60.2" )
        newAllRoutesStrExpected = str( sorted( newAllRoutesExpected ) )
        main.step( "Check routes installed after convergence-2" )
        main.log.info( "Routes expected:" )
        main.log.info( newAllRoutesStrExpected )
        main.log.info( "Routes got from ONOS CLI after convergence-2:" )
        main.log.info( newAllRoutesStrActual )
        if( eq( newAllRoutesStrExpected, newAllRoutesStrActual ) ):
            main.log.report(
                "***Routes in BgpRouter after convergence are correct!***" )
            routeCheckResult3 = main.TRUE
        else:
            main.log.report(
                "***Routes in BgpRouter after convergence are wrong!***" )
            routeCheckResult3 = main.TRUE

        time.sleep(120)

        #============================= Ping Test ========================
        pingTestResults = main.TRUE
        sources = ["as2host", "as3host", "as6host"]
        targets = ["192.168.10.101", "192.168.20.101", "192.168.30.101", "192.168.60.101"]
        for source in sources:
            for target in targets:
                r = main.Mininet.pingHost(SRC=source, TARGET=target)
                if r == main.FALSE:
                    pingTestResults = main.FALSE
        pingTestResult5 = pingTestResults

        pingTestResults = main.TRUE
        for m in range( 3, 6 ):
            for n in range( 1, 10 ):
                hostIp = str( m ) + ".0." + str( n ) + ".1"
                r = main.Mininet.pingHost(SRC="as2host", TARGET=hostIp)
                if r == main.FALSE:
                    pingTestResults = main.FALSE
        pingTestResult6 = pingTestResults

        if pingTestResult5 and pingTestResult6:
            main.log.report("*** Ping test pass ***")
        else:
            main.log.report("*** Ping test fail ***")

        time.sleep(20)

        #============================= Deleting Routes ==================
        main.log.info( "Login Quagga CLI on host3" )
        main.QuaggaCliHost3.loginQuagga( "1.168.30.2" )
        main.log.info( "Enter configuration model of Quagga CLI on host3" )
        main.QuaggaCliHost3.enterConfig( 64514 )

        main.log.info( "Login Quagga CLI on host4" )
        main.QuaggaCliHost4.loginQuagga( "1.168.30.3" )
        main.log.info( "Enter configuration model of Quagga CLI on host4" )
        main.QuaggaCliHost4.enterConfig( 64516 )

        main.log.info( "Login Quagga CLI on host5" )
        main.QuaggaCliHost5.loginQuagga( "1.168.30.5" )
        main.log.info( "Enter configuration model of Quagga CLI on host5" )
        main.QuaggaCliHost5.enterConfig( 64521 )

        main.step( "Check deleting routes installed" )
        main.QuaggaCliHost3.deleteRoutes( prefixesHost3, 1 )
        main.QuaggaCliHost4.deleteRoutes( prefixesHost4, 1 )
        main.QuaggaCliHost5.deleteRoutes( prefixesHost5, 1 )

        time.sleep(60)

        getRoutesResult = main.ONOScli.routes( jsonFormat=True )
        allRoutesActual = \
            main.QuaggaCliHost3.extractActualRoutes( getRoutesResult )

        main.log.info( "allRoutes_actual = " )
        main.log.info( allRoutesActual )
        allRoutesStrActual = str ( allRoutesActual )

        if( eq( "[]", allRoutesStrActual ) ):
            main.log.report( "***Routes in BgpRouter after deleting correct!***" )
            routeCheckResult4 = main.TRUE
        else:
            main.log.report( "***Routes in BgpRouter after deleting wrong!***" )
            routeCheckResult4 = main.TRUE

        time.sleep(60)

        #============================= Ping Test ========================
        pingTestResults = main.TRUE
        for m in range( 4, 6 ):
            for n in range( 1, 10 ):
                hostIp = str( m ) + ".0." + str( n ) + ".1"
                r = main.Mininet.pingHost(SRC="as2host", TARGET=hostIp)
                if r == main.TRUE:
                    pingTestResults = main.FALSE
        pingTestResult7 = pingTestResults

        if pingTestResult7:
            main.log.report("*** Ping test pass ***")
        else:
            main.log.report("*** Ping test fail ***")

        finalTestResult = pingTestResult1 and pingTestResult2 and pingTestResult3 and pingTestResult4 and pingTestResult5 and pingTestResult6 and pingTestResult7 and routeCheckResult1 and routeCheckResult2 and routeCheckResult3 and routeCheckResult4

        utilities.assertEquals(
            expect=main.TRUE, actual=finalTestResult,
            onpass="*** TEST CASE 31 passed ***",
            onfail="*** TEST CASE 31 failed ***" )

        time.sleep(20);

        main.ONOScli.logout()
        main.ONOSbench.onosStop(ONOS1Ip);
        main.Mininet.stopNet()
        time.sleep(10)

    # Route convergence and connectivity test with Route Server in VLAN tagged network
    def CASE32( self, main):
        import time
        import json
        from operator import eq
        # from datetime import datetime
        from time import localtime, strftime

        main.ONOSbench.handle.sendline("cell sdnip_single_instance")

        cleanInstallResult = main.ONOSbench.cleanInstallSkipTest()

        main.case("The test case is to help to setup the TestON environment \
            and test new drivers" )
        TESTCASE_ROOT_PATH = main.params[ 'ENV' ][ 'home' ]
        TESTCASE_MININET_ROOT_PATH = TESTCASE_ROOT_PATH + "/vlan/routeserver/mininet"
        SDNIPJSONFILEPATH = TESTCASE_ROOT_PATH + "/vlan/routeserver/sdnip.json"
        main.log.info("sdnip.json file path: "+ SDNIPJSONFILEPATH)

        # Copy the json files to config dir
        main.ONOSbench.handle.sendline("cp " + TESTCASE_ROOT_PATH + "/vlan/routeserver/addresses.json ~/onos/tools/package/config/")
        main.ONOSbench.handle.sendline("cp " + TESTCASE_ROOT_PATH + "/vlan/routeserver/sdnip.json ~/onos/tools/package/config/")

        cellName = main.params[ 'ENV' ][ 'cellName' ]
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        main.step( "Set cell for ONOS-cli environment" )
        main.ONOScli.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()


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

        #Inject the config file
        main.log.info("Injecting config file: bgprouter.json")
        main.ONOSbench.handle.sendline("onos-topo-cfg $OC1 ~/TestON/tests/PeeringRouterTest/bgprouter.json")
        listResult = main.ONOScli.devices( jsonFormat=False )
        main.log.info( listResult )

        # Activate bgprouter app
        main.log.info( "Installing bgprouter app" )
        main.ONOScli.handle.sendline("app activate org.onosproject.bgprouter")
        time.sleep( 10 )

        # Launch mininet topology for this case        
        MININET_TOPO_FILE = TESTCASE_MININET_ROOT_PATH + "/PeeringRouteServerVlanMininet.py"
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

        main.ONOScli.logout()
        main.ONOScli.startOnosCli( ONOS1Ip )

        main.step( "Get devices in the network" )
        listResult = main.ONOScli.devices( jsonFormat=False )
        main.log.info( listResult )
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
        if( eq( allRoutesStrExpected, allRoutesStrActual ) ):
            main.log.report(
                "***Routes in BgpRouter after adding routes are correct!***" )
            routeCheckResult1 = main.TRUE
        else:
            main.log.report(
                "***Routes in BgpRouter after adding routes are wrong!***" )
            routeCheckResult1 = main.FALSE

        time.sleep(60)

        #============================= Ping Test ========================
        pingTestResults = main.TRUE
        sources = ["as2host", "as3host", "as6host"]
        targets = ["192.168.10.101", "192.168.20.101", "192.168.30.101", "192.168.60.101"]
        for source in sources:
            for target in targets:
                r = main.Mininet.pingHost(SRC=source, TARGET=target)
                if r == main.FALSE:
                    pingTestResults = main.FALSE
        pingTestResult1 = pingTestResults

        pingTestResults = main.TRUE
        for m in range( 3, 6 ):
            for n in range( 1, 10 ):
                hostIp = str( m ) + ".0." + str( n ) + ".1"
                r = main.Mininet.pingHost(SRC="as2host", TARGET=hostIp)
                if r == main.FALSE:
                    pingTestResults = main.FALSE
        pingTestResult2 = pingTestResults

        if pingTestResult1 and pingTestResult2:
            main.log.report("*** Ping test pass ***")
        else:
            main.log.report("*** Ping test fail ***")

        time.sleep(20)

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
        if( eq( newAllRoutesStrExpected, newAllRoutesStrActual ) ):
            main.log.report(
                "***Routes in BgpRouter after convergence are correct!***" )
            routeCheckResult2 = main.TRUE
        else:
            main.log.report(
                "***Routes in BgpRouter after convergence are wrong!***" )
            routeCheckResult2 = main.FALSE

        time.sleep(120)

        #============================= Ping Test ========================
        pingTestResults = main.TRUE
        sources = ["as2host", "as3host", "as6host"]
        targets = ["192.168.10.101", "192.168.20.101", "192.168.30.101", "192.168.60.101"]
        for source in sources:
            for target in targets:
                r = main.Mininet.pingHost(SRC=source, TARGET=target)
                if r == main.FALSE:
                    pingTestResults = main.FALSE
        pingTestResult3 = pingTestResults

        pingTestResults = main.TRUE
        for m in range( 3, 6 ):
            for n in range( 1, 10 ):
                hostIp = str( m ) + ".0." + str( n ) + ".1"
                r = main.Mininet.pingHost(SRC="as2host", TARGET=hostIp)
                if r == main.FALSE:
                    pingTestResults = main.FALSE

        utilities.assert_equals(expect=main.TRUE,actual=pingTestResults,
                                  onpass="Default connectivity check PASS",
                                  onfail="Default connectivity check FAIL")
        pingTestResult4 = pingTestResults

        if pingTestResult3 and pingTestResult4:
            main.log.report("*** Ping test pass ***")
        else:
            main.log.report("*** Ping test fail ***")

        time.sleep(20)

        #============= Enabling the BGP session between QuaggaCliHost4 and ONOS ==================
        main.log.info( "Enabling bgp session between QuaggaCliHost4 and 192.168.30.101:" )
        main.QuaggaCliHost4.enable_bgp_peer( "192.168.30.101", "64513" )
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
            newAllRoutesExpected.append( prefix + "/" + "192.168.30.1" )
        for prefix in prefixesHost5:
            newAllRoutesExpected.append( prefix + "/" + "192.168.60.2" )
        newAllRoutesStrExpected = str( sorted( newAllRoutesExpected ) )
        main.step( "Check routes installed after convergence-2" )
        main.log.info( "Routes expected:" )
        main.log.info( newAllRoutesStrExpected )
        main.log.info( "Routes got from ONOS CLI after convergence-2:" )
        main.log.info( newAllRoutesStrActual )
        if( eq( newAllRoutesStrExpected, newAllRoutesStrActual ) ):
            main.log.report(
                "***Routes in BgpRouter after convergence are correct!***" )
            routeCheckResult3 = main.TRUE
        else:
            main.log.report(
                "***Routes in BgpRouter after convergence are wrong!***" )
            routeCheckResult3 = main.FALSE

        time.sleep(60)

        #============================= Ping Test ========================
        pingTestResults = main.TRUE
        sources = ["as2host", "as3host", "as6host"]
        targets = ["192.168.10.101", "192.168.20.101", "192.168.30.101", "192.168.60.101"]
        for source in sources:
            for target in targets:
                r = main.Mininet.pingHost(SRC=source, TARGET=target)
                if r == main.FALSE:
                    pingTestResults = main.FALSE
        pingTestResult5 = pingTestResults

        pingTestResults = main.TRUE
        for m in range( 3, 6 ):
            for n in range( 1, 10 ):
                hostIp = str( m ) + ".0." + str( n ) + ".1"
                r = main.Mininet.pingHost(SRC="as2host", TARGET=hostIp)
                if r == main.FALSE:
                    pingTestResults = main.FALSE

        utilities.assert_equals(expect=main.TRUE,actual=pingTestResults,
                                  onpass="Default connectivity check PASS",
                                  onfail="Default connectivity check FAIL")
        pingTestResult6 = pingTestResults
 
        if pingTestResult5 and pingTestResult6:
            main.log.report("*** Ping test pass ***")
        else:
            main.log.report("*** Ping test fail ***")

        time.sleep(20)

        #============================= Deleting Routes ==================
        main.step( "Check deleting routes installed" )
   
        main.log.info( "Login Quagga CLI on host3" )
        main.QuaggaCliHost3.loginQuagga( "1.168.30.2" )
        main.log.info( "Enter configuration model of Quagga CLI on host3" )
        main.QuaggaCliHost3.enterConfig( 64514 )

        main.log.info( "Login Quagga CLI on host4" )
        main.QuaggaCliHost4.loginQuagga( "1.168.30.3" )
        main.log.info( "Enter configuration model of Quagga CLI on host4" )
        main.QuaggaCliHost4.enterConfig( 64516 )

        main.log.info( "Login Quagga CLI on host5" )
        main.QuaggaCliHost5.loginQuagga( "1.168.30.5" )
        main.log.info( "Enter configuration model of Quagga CLI on host5" )
        main.QuaggaCliHost5.enterConfig( 64521 )
   
        main.QuaggaCliHost3.deleteRoutes( prefixesHost3, 1 )
        main.QuaggaCliHost4.deleteRoutes( prefixesHost4, 1 )
        main.QuaggaCliHost5.deleteRoutes( prefixesHost5, 1 )

        getRoutesResult = main.ONOScli.routes( jsonFormat=True )
        allRoutesActual = \
            main.QuaggaCliHost3.extractActualRoutes( getRoutesResult )

        main.log.info( "allRoutes_actual = " )
        main.log.info( allRoutesActual )
        allRoutesStrActual = str ( allRoutesActual )

        if( eq( "[]", allRoutesStrActual ) ):
            main.log.report( "***Routes in BgpRouter after deleting correct!***" )
            routeCheckResult4 = main.TRUE
        else:
            main.log.report( "***Routes in BgpRouter after deleting wrong!***" )
            routeCheckResult4 = main.FALSE

        time.sleep(20)

        #============================= Ping Test ========================
        pingTestResults = main.TRUE
        for m in range( 4, 6 ):
            for n in range( 1, 10 ):
                hostIp = str( m ) + ".0." + str( n ) + ".1"
                r = main.Mininet.pingHost(SRC="as2host", TARGET=hostIp)
                if r == main.TRUE:
                    pingTestResults = main.FALSE
        pingTestResult7 = pingTestResults
     
        if pingTestResult7:
            main.log.report("*** Ping test pass ***")
        else:
            main.log.report("*** Ping test fail ***")


        finalTestResult = pingTestResult1 and pingTestResult2 and pingTestResult3 and pingTestResult4 and pingTestResult5 and pingTestResult6 and pingTestResult7 and routeCheckResult1 and routeCheckResult2 and routeCheckResult3 and routeCheckResult4

        utilities.assertEquals(
            expect=main.TRUE, actual=finalTestResult,
            onpass="*** TEST CASE 32 passed ***",
            onfail="*** TEST CASE 32 failed ***" )

        time.sleep(20)

        main.ONOScli.logout()
        main.ONOSbench.onosStop(ONOS1Ip);
        main.Mininet.stopNet()
        time.sleep(10)

