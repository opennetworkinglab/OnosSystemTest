# from cupshelpers.config import prefix

# Testing the basic functionality of SDN-IP

class SdnIpTest:
    def __init__(self):
        self.default = ''

# from cupshelpers.config import prefix

# Testing the basic functionality of SDN-IP

class SdnIpTest:
    def __init__(self):
        self.default = ''

    def CASE4(self, main):

        '''
        Test the SDN-IP functionality
        allRoutes_expected: all expected routes for all BGP peers
        routeIntents_expected: all expected MultiPointToSinglePointIntent intents
        bgpIntents_expected: expected PointToPointIntent intents
        allRoutes_actual: all routes from ONOS LCI
        routeIntents_actual: actual MultiPointToSinglePointIntent intents from ONOS CLI
        bgpIntents_actual: actual PointToPointIntent intents from ONOS CLI
        '''
        import time
        import json
        from operator import eq
        # from datetime import datetime
        from time import localtime, strftime

        main.case("The test case is to help to setup the TestON environment and test new drivers")
        #SDNIP_JSON_FILE_PATH = "../tests/SdnIpTest/sdnip.json"
        SDNIP_JSON_FILE_PATH = "/home/admin/workspace/onos/tools/package/config/sdnip.json"
        # all expected routes for all BGP peers
        allRoutes_expected = []
        main.step("Start to generate routes for all BGP peers")
        main.log.info("Generate prefixes for host3")
        prefixes_host3 = main.QuaggaCliHost3.generate_prefixes(3, 10)
        main.log.info(prefixes_host3)
        # generate route with next hop
        for prefix in prefixes_host3:
            allRoutes_expected.append(prefix + "/" + "192.168.20.1")
        routeIntents_expected_host3 = main.QuaggaCliHost3.generate_expected_onePeerRouteIntents(prefixes_host3, "192.168.20.1", "00:00:00:00:02:02", SDNIP_JSON_FILE_PATH)

        main.log.info("Generate prefixes for host4")
        prefixes_host4 = main.QuaggaCliHost4.generate_prefixes(4, 10)
        main.log.info(prefixes_host4)
        # generate route with next hop
        for prefix in prefixes_host4:
            allRoutes_expected.append(prefix + "/" + "192.168.30.1")
        routeIntents_expected_host4 = main.QuaggaCliHost4.generate_expected_onePeerRouteIntents(prefixes_host4, "192.168.30.1", "00:00:00:00:03:01", SDNIP_JSON_FILE_PATH)

        main.log.info("Generate prefixes for host5")
        prefixes_host5 = main.QuaggaCliHost5.generate_prefixes(5, 10)
        main.log.info(prefixes_host5)
        for prefix in prefixes_host5:
            allRoutes_expected.append(prefix + "/" + "192.168.60.2")
        routeIntents_expected_host5 = main.QuaggaCliHost5.generate_expected_onePeerRouteIntents(prefixes_host5, "192.168.60.1", "00:00:00:00:06:02", SDNIP_JSON_FILE_PATH)

        routeIntents_expected = routeIntents_expected_host3 + routeIntents_expected_host4 + routeIntents_expected_host5

        cell_name = main.params['ENV']['cellName']
        ONOS1_ip = main.params['CTRL']['ip1']
        main.step("Set cell for ONOS-cli environment")
        main.ONOScli.set_cell(cell_name)
        verify_result = main.ONOSbench.verify_cell()
        
        main.log.report("Removing raft logs")
        main.ONOSbench.onos_remove_raft_logs()
        main.log.report("Uninstalling ONOS")
        main.ONOSbench.onos_uninstall(ONOS1_ip)

        main.step("Installing ONOS package")
        onos1_install_result = main.ONOSbench.onos_install(options="-f", node=ONOS1_ip)

        main.step("Checking if ONOS is up yet")
        time.sleep(150)
        onos1_isup = main.ONOSbench.isup(ONOS1_ip)
        if not onos1_isup:
            main.log.report("ONOS1 didn't start!")

        main.step("Start ONOS-cli")

        main.ONOScli.start_onos_cli(ONOS1_ip)

        main.step("Get devices in the network")
        list_result = main.ONOScli.devices(json_format=False)
        main.log.info(list_result)
        time.sleep(10)
        main.log.info("Installing sdn-ip feature")
        main.ONOScli.feature_install("onos-app-sdnip")
        time.sleep(10)
        main.step("Login all BGP peers and add routes into peers")

        main.log.info("Login Quagga CLI on host3")
        main.QuaggaCliHost3.loginQuagga("1.168.30.2")
        main.log.info("Enter configuration model of Quagga CLI on host3")
        main.QuaggaCliHost3.enter_config(64514)
        main.log.info("Add routes to Quagga on host3")
        main.QuaggaCliHost3.add_routes(prefixes_host3, 1)

        main.log.info("Login Quagga CLI on host4")
        main.QuaggaCliHost4.loginQuagga("1.168.30.3")
        main.log.info("Enter configuration model of Quagga CLI on host4")
        main.QuaggaCliHost4.enter_config(64516)
        main.log.info("Add routes to Quagga on host4")
        main.QuaggaCliHost4.add_routes(prefixes_host4, 1)

        main.log.info("Login Quagga CLI on host5")
        main.QuaggaCliHost5.loginQuagga("1.168.30.5")
        main.log.info("Enter configuration model of Quagga CLI on host5")
        main.QuaggaCliHost5.enter_config(64521)
        main.log.info("Add routes to Quagga on host5")
        main.QuaggaCliHost5.add_routes(prefixes_host5, 1)      

        for i in range(101, 201):
            prefixes_hostX=main.QuaggaCliHost.generate_prefixes(str(i),10)
            main.log.info(prefixes_hostX)
            for prefix in prefixes_hostX:
                allRoutes_expected.append(prefix + "/" + "192.168.40."+ str(i-100))
            
            routeIntents_expected_hostX = main.QuaggaCliHost.generate_expected_onePeerRouteIntents(prefixes_hostX, "192.168.40."+str(i-100), "00:00:%02d:00:00:90" %(i-101), SDNIP_JSON_FILE_PATH)
            routeIntents_expected = routeIntents_expected + routeIntents_expected_hostX

            main.log.info("Login Quagga CLI on host" + str(i))
            QuaggaCliHostX = getattr(main, ('QuaggaCliHost' + str(i)))
            QuaggaCliHostX.loginQuagga("1.168.30." + str(i))
            main.log.info("Enter configuration model of Quagga CLI on host" + str(i))
            QuaggaCliHostX.enter_config(65000+i-100)
            main.log.info("Add routes to Quagga on host" + str(i))
            QuaggaCliHostX.add_routes(prefixes_hostX, 1)
 
        time.sleep(60)

        # get routes inside SDN-IP
        get_routes_result = main.ONOScli.routes(json_format=True)

        # parse routes from ONOS CLI
        allRoutes_actual = main.QuaggaCliHost3.extract_actual_routes(get_routes_result)

        allRoutes_str_expected = str(sorted(allRoutes_expected))
        allRoutes_str_actual = str(allRoutes_actual).replace('u', "")
        main.step("Check routes installed")
        main.log.info("Routes expected:")
        main.log.info(allRoutes_str_expected)
        main.log.info("Routes get from ONOS CLI:")
        main.log.info(allRoutes_str_actual)
        utilities.assert_equals(expect=allRoutes_str_expected, actual=allRoutes_str_actual,
                                onpass="***Routes in SDN-IP are correct!***",
                                onfail="***Routes in SDN-IP are wrong!***")
        if(eq(allRoutes_str_expected, allRoutes_str_actual)):
            main.log.report("***Routes in SDN-IP after adding routes are correct!***")
        else:
            main.log.report("***Routes in SDN-IP after adding routes are wrong!***")

        time.sleep(20)
        get_intents_result = main.ONOScli.intents(json_format=True)


        main.step("Check MultiPointToSinglePointIntent intents installed")
        # route_intents_expected are generated when generating routes
        # get rpoute intents from ONOS CLI
        routeIntents_actual = main.QuaggaCliHost3.extract_actual_routeIntents(get_intents_result)
        routeIntents_str_expected = str(sorted(routeIntents_expected))
        routeIntents_str_actual = str(routeIntents_actual).replace('u', "")
        main.log.info("MultiPointToSinglePoint intents expected:")
        main.log.info(routeIntents_str_expected)
        main.log.info("MultiPointToSinglePoint intents get from ONOS CLI:")
        main.log.info(routeIntents_str_actual)
        utilities.assert_equals(expect=True, actual=eq(routeIntents_str_expected, routeIntents_str_actual),
                                onpass="***MultiPointToSinglePoint Intents in SDN-IP are correct!***",
                                onfail="***MultiPointToSinglePoint Intents in SDN-IP are wrong!***")

        if(eq(routeIntents_str_expected, routeIntents_str_actual)):
            main.log.report("***MultiPointToSinglePoint Intents before deleting routes correct!***")
        else:
            main.log.report("***MultiPointToSinglePoint Intents before deleting routes wrong!***")

        main.step("Check BGP PointToPointIntent intents installed")
        # bgp intents expected
        bgpIntents_expected = main.QuaggaCliHost3.generate_expected_bgpIntents(SDNIP_JSON_FILE_PATH)
        # get BGP intents from ONOS CLI
        bgpIntents_actual = main.QuaggaCliHost3.extract_actual_bgpIntents(get_intents_result)

        bgpIntents_str_expected = str(bgpIntents_expected).replace('u', "")
        bgpIntents_str_actual = str(bgpIntents_actual)
        main.log.info("PointToPointIntent intents expected:")
        main.log.info(bgpIntents_str_expected)
        main.log.info("PointToPointIntent intents get from ONOS CLI:")
        main.log.info(bgpIntents_str_actual)

        utilities.assert_equals(expect=True, actual=eq(bgpIntents_str_expected, bgpIntents_str_actual),
                                onpass="***PointToPointIntent Intents in SDN-IP are correct!***",
                                onfail="***PointToPointIntent Intents in SDN-IP are wrong!***")


        if (eq(bgpIntents_str_expected, bgpIntents_str_actual)):
            main.log.report("***PointToPointIntent Intents in SDN-IP are correct!***")
        else:
            main.log.report("***PointToPointIntent Intents in SDN-IP are wrong!***")



        #============================= Ping Test ========================
        # wait until all MultiPointToSinglePoint
        time.sleep(20)
        ping_test_script = "~/SDNIP/test-tools/CASE4-ping-as2host.sh"
        ping_test_results_file = "~/SDNIP/SdnIpIntentDemo/log/CASE4-ping-results-before-delete-routes-" + strftime("%Y-%m-%d_%H:%M:%S", localtime()) + ".txt"
        ping_test_results = main.QuaggaCliHost.ping_test("1.168.30.100", ping_test_script, ping_test_results_file)
        main.log.info(ping_test_results)
        time.sleep(20)


        #============================= Deleting Routes ==================
        main.step("Check deleting routes installed")
        main.QuaggaCliHost3.delete_routes(prefixes_host3, 1)
        main.QuaggaCliHost4.delete_routes(prefixes_host4, 1)
        main.QuaggaCliHost5.delete_routes(prefixes_host5, 1)

        for i in range(101, 201):
            prefixes_hostX=main.QuaggaCliHost.generate_prefixes(str(i),10)
            main.log.info(prefixes_hostX)
            QuaggaCliHostX = getattr(main, ('QuaggaCliHost' + str(i)))       
            QuaggaCliHostX.delete_routes(prefixes_hostX, 1)

        

        get_routes_result = main.ONOScli.routes(json_format=True)
        allRoutes_actual = main.QuaggaCliHost3.extract_actual_routes(get_routes_result)
        main.log.info("allRoutes_actual = ")
        main.log.info(allRoutes_actual)

        utilities.assert_equals(expect="[]", actual=str(allRoutes_actual),
                                onpass="***Route number in SDN-IP is 0, correct!***",
                                onfail="***Routes number in SDN-IP is not 0, wrong!***")

        if(eq(allRoutes_str_expected, allRoutes_str_actual)):
            main.log.report("***Routes in SDN-IP after deleting correct!***")
        else:
            main.log.report("***Routes in SDN-IP after deleting wrong!***")

        main.step("Check intents after deleting routes")
        get_intents_result = main.ONOScli.intents(json_format=True)
        routeIntents_actual = main.QuaggaCliHost3.extract_actual_routeIntents(get_intents_result)
        main.log.info("main.ONOScli.intents()= ")
        main.log.info(routeIntents_actual)
        utilities.assert_equals(expect="[]", actual=str(routeIntents_actual),
                                onpass="***MultiPointToSinglePoint Intents number in SDN-IP is 0, correct!***",
                                onfail="***MultiPointToSinglePoint Intents number in SDN-IP is 0, wrong!***")

        if(eq(routeIntents_str_expected, routeIntents_str_actual)):
            main.log.report("***MultiPointToSinglePoint Intents after deleting routes correct!***")
        else:
            main.log.report("***MultiPointToSinglePoint Intents after deleting routes wrong!***")

        time.sleep(20)
        ping_test_script = "~/SDNIP/test-tools/CASE4-ping-as2host.sh"
        ping_test_results_file = "~/SDNIP/SdnIpIntentDemo/log/CASE4-ping-results-after-delete-routes-" + strftime("%Y-%m-%d_%H:%M:%S", localtime()) + ".txt"
        ping_test_results = main.QuaggaCliHost.ping_test("1.168.30.100", ping_test_script, ping_test_results_file)
        main.log.info(ping_test_results)
        time.sleep(100)

        # main.step("Test whether Mininet is started")
        # main.Mininet2.handle.sendline("xterm host1")
        # main.Mininet2.handle.expect("mininet>")





    def CASE3(self, main):

        '''
        Test the SDN-IP functionality
        allRoutes_expected: all expected routes for all BGP peers
        routeIntents_expected: all expected MultiPointToSinglePointIntent intents
        bgpIntents_expected: expected PointToPointIntent intents
        allRoutes_actual: all routes from ONOS LCI
        routeIntents_actual: actual MultiPointToSinglePointIntent intents from ONOS CLI
        bgpIntents_actual: actual PointToPointIntent intents from ONOS CLI
        '''
        import time
        import json
        from operator import eq
        # from datetime import datetime
        from time import localtime, strftime

        main.case("The test case is to help to setup the TestON environment and test new drivers")
        #SDNIP_JSON_FILE_PATH = "../tests/SdnIpTest/sdnip.json"
        SDNIP_JSON_FILE_PATH = "/home/admin/workspace/onos/tools/package/config/sdnip.json"
        # all expected routes for all BGP peers
        allRoutes_expected = []
        main.step("Start to generate routes for all BGP peers")
        main.log.info("Generate prefixes for host3")
        prefixes_host3 = main.QuaggaCliHost3.generate_prefixes(3, 10)
        main.log.info(prefixes_host3)
        # generate route with next hop
        for prefix in prefixes_host3:
            allRoutes_expected.append(prefix + "/" + "192.168.20.1")
        routeIntents_expected_host3 = main.QuaggaCliHost3.generate_expected_onePeerRouteIntents(prefixes_host3, "192.168.20.1", "00:00:00:00:02:02", SDNIP_JSON_FILE_PATH)

        main.log.info("Generate prefixes for host4")
        prefixes_host4 = main.QuaggaCliHost4.generate_prefixes(4, 10)
        main.log.info(prefixes_host4)
        # generate route with next hop
        for prefix in prefixes_host4:
            allRoutes_expected.append(prefix + "/" + "192.168.30.1")
        routeIntents_expected_host4 = main.QuaggaCliHost4.generate_expected_onePeerRouteIntents(prefixes_host4, "192.168.30.1", "00:00:00:00:03:01", SDNIP_JSON_FILE_PATH)

        routeIntents_expected = routeIntents_expected_host3 + routeIntents_expected_host4
        
        #
        #main.log.info("Generate prefixes for 100 guaggas")
        #for i in range(101, 105):
         #    prefixes_hostX=main.QuaggaCliHost.generate_prefixes(str(i),10)
         #    main.log.info(prefixes_hostX)
        #for prefix in prefixes_hostX:
        #    allRoutes_expected.append(prefix + "/" + "192.168.40."+ str(i-100))
        #    routeIntents_expected_hostX = main.QuaggaCliHost.generate_expected_onePeerRouteIntents(prefixes_hostX, "192.168.40."+str(i), "00:00:"+str(i-101)+":00:00:90", SDNIP_JSON_FILE_PATH)
        #routeIntents_expected = routeIntents_expected + routeIntents_expected_hostX
        #

        cell_name = main.params['ENV']['cellName']
        ONOS1_ip = main.params['CTRL']['ip1']
        main.step("Set cell for ONOS-cli environment")
        main.ONOScli.set_cell(cell_name)
        verify_result = main.ONOSbench.verify_cell()
        
        main.log.report("Removing raft logs")
        main.ONOSbench.onos_remove_raft_logs()
        main.log.report("Uninstalling ONOS")
        main.ONOSbench.onos_uninstall(ONOS1_ip)

        main.step("Installing ONOS package")
        onos1_install_result = main.ONOSbench.onos_install(options="-f", node=ONOS1_ip)

        main.step("Checking if ONOS is up yet")
        time.sleep(60)
        onos1_isup = main.ONOSbench.isup(ONOS1_ip)
        if not onos1_isup:
            main.log.report("ONOS1 didn't start!")

        main.step("Start ONOS-cli")

        main.ONOScli.start_onos_cli(ONOS1_ip)

        main.step("Get devices in the network")
        list_result = main.ONOScli.devices(json_format=False)
        main.log.info(list_result)
        time.sleep(10)
        main.log.info("Installing sdn-ip feature")
        main.ONOScli.feature_install("onos-app-sdnip")
        time.sleep(10)
        main.step("Login all BGP peers and add routes into peers")

        main.log.info("Login Quagga CLI on host3")
        main.QuaggaCliHost3.loginQuagga("1.168.30.2")
        main.log.info("Enter configuration model of Quagga CLI on host3")
        main.QuaggaCliHost3.enter_config(64514)
        main.log.info("Add routes to Quagga on host3")
        main.QuaggaCliHost3.add_routes(prefixes_host3, 1)

        main.log.info("Login Quagga CLI on host4")
        main.QuaggaCliHost4.loginQuagga("1.168.30.3")
        main.log.info("Enter configuration model of Quagga CLI on host4")
        main.QuaggaCliHost4.enter_config(64516)
        main.log.info("Add routes to Quagga on host4")
        main.QuaggaCliHost4.add_routes(prefixes_host4, 1)

        for i in range(101, 201):
            prefixes_hostX=main.QuaggaCliHost.generate_prefixes(str(i),10)
            main.log.info(prefixes_hostX)
            for prefix in prefixes_hostX:
                allRoutes_expected.append(prefix + "/" + "192.168.40."+ str(i-100))
            
            routeIntents_expected_hostX = main.QuaggaCliHost.generate_expected_onePeerRouteIntents(prefixes_hostX, "192.168.40."+str(i-100), "00:00:%02d:00:00:90" %(i-101), SDNIP_JSON_FILE_PATH)
            routeIntents_expected = routeIntents_expected + routeIntents_expected_hostX

            main.log.info("Login Quagga CLI on host" + str(i))
            QuaggaCliHostX = getattr(main, ('QuaggaCliHost' + str(i)))
            QuaggaCliHostX.loginQuagga("1.168.30." + str(i))
            main.log.info("Enter configuration model of Quagga CLI on host" + str(i))
            QuaggaCliHostX.enter_config(65000+i-100)
            main.log.info("Add routes to Quagga on host" + str(i))
            QuaggaCliHostX.add_routes(prefixes_hostX, 1)
 
        time.sleep(60)

        # get routes inside SDN-IP
        get_routes_result = main.ONOScli.routes(json_format=True)

        # parse routes from ONOS CLI
        allRoutes_actual = main.QuaggaCliHost3.extract_actual_routes(get_routes_result)

        allRoutes_str_expected = str(sorted(allRoutes_expected))
        allRoutes_str_actual = str(allRoutes_actual).replace('u', "")
        main.step("Check routes installed")
        main.log.info("Routes expected:")
        main.log.info(allRoutes_str_expected)
        main.log.info("Routes get from ONOS CLI:")
        main.log.info(allRoutes_str_actual)
        utilities.assert_equals(expect=allRoutes_str_expected, actual=allRoutes_str_actual,
                                onpass="***Routes in SDN-IP are correct!***",
                                onfail="***Routes in SDN-IP are wrong!***")
        if(eq(allRoutes_str_expected, allRoutes_str_actual)):
            main.log.report("***Routes in SDN-IP after adding routes are correct!***")
        else:
            main.log.report("***Routes in SDN-IP after adding routes are wrong!***")

        time.sleep(20)
        get_intents_result = main.ONOScli.intents(json_format=True)


        main.step("Check MultiPointToSinglePointIntent intents installed")
        # route_intents_expected are generated when generating routes
        # get rpoute intents from ONOS CLI
        routeIntents_actual = main.QuaggaCliHost3.extract_actual_routeIntents(get_intents_result)
        routeIntents_str_expected = str(sorted(routeIntents_expected))
        routeIntents_str_actual = str(routeIntents_actual).replace('u', "")
        main.log.info("MultiPointToSinglePoint intents expected:")
        main.log.info(routeIntents_str_expected)
        main.log.info("MultiPointToSinglePoint intents get from ONOS CLI:")
        main.log.info(routeIntents_str_actual)
        utilities.assert_equals(expect=True, actual=eq(routeIntents_str_expected, routeIntents_str_actual),
                                onpass="***MultiPointToSinglePoint Intents in SDN-IP are correct!***",
                                onfail="***MultiPointToSinglePoint Intents in SDN-IP are wrong!***")

        if(eq(routeIntents_str_expected, routeIntents_str_actual)):
            main.log.report("***MultiPointToSinglePoint Intents before deleting routes correct!***")
        else:
            main.log.report("***MultiPointToSinglePoint Intents before deleting routes wrong!***")

        main.step("Check BGP PointToPointIntent intents installed")
        # bgp intents expected
        bgpIntents_expected = main.QuaggaCliHost3.generate_expected_bgpIntents(SDNIP_JSON_FILE_PATH)
        # get BGP intents from ONOS CLI
        bgpIntents_actual = main.QuaggaCliHost3.extract_actual_bgpIntents(get_intents_result)

        bgpIntents_str_expected = str(bgpIntents_expected).replace('u', "")
        bgpIntents_str_actual = str(bgpIntents_actual)
        main.log.info("PointToPointIntent intents expected:")
        main.log.info(bgpIntents_str_expected)
        main.log.info("PointToPointIntent intents get from ONOS CLI:")
        main.log.info(bgpIntents_str_actual)

        utilities.assert_equals(expect=True, actual=eq(bgpIntents_str_expected, bgpIntents_str_actual),
                                onpass="***PointToPointIntent Intents in SDN-IP are correct!***",
                                onfail="***PointToPointIntent Intents in SDN-IP are wrong!***")


        if (eq(bgpIntents_str_expected, bgpIntents_str_actual)):
            main.log.report("***PointToPointIntent Intents in SDN-IP are correct!***")
        else:
            main.log.report("***PointToPointIntent Intents in SDN-IP are wrong!***")



        #============================= Ping Test ========================
        # wait until all MultiPointToSinglePoint
        time.sleep(20)
        ping_test_script = "~/SDNIP/test-tools/CASE3-ping-as2host.sh"
        ping_test_results_file = "~/SDNIP/SdnIpIntentDemo/log/CASE3-ping-results-before-delete-routes-" + strftime("%Y-%m-%d_%H:%M:%S", localtime()) + ".txt"
        ping_test_results = main.QuaggaCliHost.ping_test("1.168.30.100", ping_test_script, ping_test_results_file)
        main.log.info(ping_test_results)
        time.sleep(20)


        #============================= Deleting Routes ==================
        main.step("Check deleting routes installed")
        main.QuaggaCliHost3.delete_routes(prefixes_host3, 1)
        main.QuaggaCliHost4.delete_routes(prefixes_host4, 1)
        for i in range(101, 201):
            prefixes_hostX=main.QuaggaCliHost.generate_prefixes(str(i),10)
            main.log.info(prefixes_hostX)
            QuaggaCliHostX = getattr(main, ('QuaggaCliHost' + str(i)))       
            QuaggaCliHostX.delete_routes(prefixes_hostX, 1)

        

        get_routes_result = main.ONOScli.routes(json_format=True)
        allRoutes_actual = main.QuaggaCliHost3.extract_actual_routes(get_routes_result)
        main.log.info("allRoutes_actual = ")
        main.log.info(allRoutes_actual)

        utilities.assert_equals(expect="[]", actual=str(allRoutes_actual),
                                onpass="***Route number in SDN-IP is 0, correct!***",
                                onfail="***Routes number in SDN-IP is not 0, wrong!***")

        if(eq(allRoutes_str_expected, allRoutes_str_actual)):
            main.log.report("***Routes in SDN-IP after deleting correct!***")
        else:
            main.log.report("***Routes in SDN-IP after deleting wrong!***")

        main.step("Check intents after deleting routes")
        get_intents_result = main.ONOScli.intents(json_format=True)
        routeIntents_actual = main.QuaggaCliHost3.extract_actual_routeIntents(get_intents_result)
        main.log.info("main.ONOScli.intents()= ")
        main.log.info(routeIntents_actual)
        utilities.assert_equals(expect="[]", actual=str(routeIntents_actual),
                                onpass="***MultiPointToSinglePoint Intents number in SDN-IP is 0, correct!***",
                                onfail="***MultiPointToSinglePoint Intents number in SDN-IP is 0, wrong!***")

        if(eq(routeIntents_str_expected, routeIntents_str_actual)):
            main.log.report("***MultiPointToSinglePoint Intents after deleting routes correct!***")
        else:
            main.log.report("***MultiPointToSinglePoint Intents after deleting routes wrong!***")

        time.sleep(20)
        ping_test_script = "~/SDNIP/test-tools/CASE3-ping-as2host.sh"
        ping_test_results_file = "~/SDNIP/SdnIpIntentDemo/log/CASE3-ping-results-after-delete-routes-" + strftime("%Y-%m-%d_%H:%M:%S", localtime()) + ".txt"
        ping_test_results = main.QuaggaCliHost.ping_test("1.168.30.100", ping_test_script, ping_test_results_file)
        main.log.info(ping_test_results)
        time.sleep(100)

        # main.step("Test whether Mininet is started")
        # main.Mininet2.handle.sendline("xterm host1")
        # main.Mininet2.handle.expect("mininet>")

    def CASE1(self, main):

        '''
        Test the SDN-IP functionality
        allRoutes_expected: all expected routes for all BGP peers
        routeIntents_expected: all expected MultiPointToSinglePointIntent intents
        bgpIntents_expected: expected PointToPointIntent intents
        allRoutes_actual: all routes from ONOS LCI
        routeIntents_actual: actual MultiPointToSinglePointIntent intents from ONOS CLI
        bgpIntents_actual: actual PointToPointIntent intents from ONOS CLI
        '''
        import time
        import json
        from operator import eq
        # from datetime import datetime
        from time import localtime, strftime

        main.case("The test case is to help to setup the TestON environment and test new drivers")
        SDNIP_JSON_FILE_PATH = "../tests/SdnIpTest/sdnip.json"
        # all expected routes for all BGP peers
        allRoutes_expected = []
        main.step("Start to generate routes for all BGP peers")
        # bgpPeerHosts = []
        # for i in range(3, 5):
        #    bgpPeerHosts.append("host" + str(i))
        # main.log.info("BGP Peer Hosts are:" + bgpPeerHosts)

        # for i in range(3, 5):
         #   QuaggaCliHost = "QuaggaCliHost" + str(i)
          #  prefixes = main.QuaggaCliHost.generate_prefixes(3, 10)

           # main.log.info(prefixes)
            # allRoutes_expected.append(prefixes)
        main.log.info("Generate prefixes for host3")
        prefixes_host3 = main.QuaggaCliHost3.generate_prefixes(3, 10)
        main.log.info(prefixes_host3)
        # generate route with next hop
        for prefix in prefixes_host3:
            allRoutes_expected.append(prefix + "/" + "192.168.20.1")
        routeIntents_expected_host3 = main.QuaggaCliHost3.generate_expected_onePeerRouteIntents(prefixes_host3, "192.168.20.1", "00:00:00:00:02:02", SDNIP_JSON_FILE_PATH)

        main.log.info("Generate prefixes for host4")
        prefixes_host4 = main.QuaggaCliHost4.generate_prefixes(4, 10)
        main.log.info(prefixes_host4)
        # generate route with next hop
        for prefix in prefixes_host4:
            allRoutes_expected.append(prefix + "/" + "192.168.30.1")
        routeIntents_expected_host4 = main.QuaggaCliHost4.generate_expected_onePeerRouteIntents(prefixes_host4, "192.168.30.1", "00:00:00:00:03:01", SDNIP_JSON_FILE_PATH)

        routeIntents_expected = routeIntents_expected_host3 + routeIntents_expected_host4


        cell_name = main.params['ENV']['cellName']
        ONOS1_ip = main.params['CTRL']['ip1']
        main.step("Set cell for ONOS-cli environment")
        main.ONOScli.set_cell(cell_name)
        verify_result = main.ONOSbench.verify_cell()
        main.log.report("Removing raft logs")
        main.ONOSbench.onos_remove_raft_logs()
        main.log.report("Uninstalling ONOS")
        main.ONOSbench.onos_uninstall(ONOS1_ip)
        main.step("Creating ONOS package")
        package_result = main.ONOSbench.onos_package()

        main.step("Starting ONOS service")
        # TODO: start ONOS from Mininet Script
        # start_result = main.ONOSbench.onos_start("127.0.0.1")
        main.step("Installing ONOS package")
        onos1_install_result = main.ONOSbench.onos_install(options="-f", node=ONOS1_ip)

        main.step("Checking if ONOS is up yet")
        time.sleep(60)
        onos1_isup = main.ONOSbench.isup(ONOS1_ip)
        if not onos1_isup:
            main.log.report("ONOS1 didn't start!")

        main.step("Start ONOS-cli")
        # TODO: change the hardcode in start_onos_cli method in ONOS CLI driver

        main.ONOScli.start_onos_cli(ONOS1_ip)

        main.step("Get devices in the network")
        list_result = main.ONOScli.devices(json_format=False)
        main.log.info(list_result)
        time.sleep(10)
        main.log.info("Installing sdn-ip feature")
        main.ONOScli.feature_install("onos-app-sdnip")
        time.sleep(10)
        main.step("Login all BGP peers and add routes into peers")
        main.log.info("Login Quagga CLI on host3")
        main.QuaggaCliHost3.loginQuagga("1.168.30.2")
        main.log.info("Enter configuration model of Quagga CLI on host3")
        main.QuaggaCliHost3.enter_config(64514)
        main.log.info("Add routes to Quagga on host3")
        main.QuaggaCliHost3.add_routes(prefixes_host3, 1)

        main.log.info("Login Quagga CLI on host4")
        main.QuaggaCliHost4.loginQuagga("1.168.30.3")
        main.log.info("Enter configuration model of Quagga CLI on host4")
        main.QuaggaCliHost4.enter_config(64516)
        main.log.info("Add routes to Quagga on host4")
        main.QuaggaCliHost4.add_routes(prefixes_host4, 1)
        time.sleep(60)

        # get all routes inside SDN-IP
        get_routes_result = main.ONOScli.routes(json_format=True)

        # parse routes from ONOS CLI
        allRoutes_actual = main.QuaggaCliHost3.extract_actual_routes(get_routes_result)

        allRoutes_str_expected = str(sorted(allRoutes_expected))
        allRoutes_str_actual = str(allRoutes_actual).replace('u', "")
        main.step("Check routes installed")
        main.log.info("Routes expected:")
        main.log.info(allRoutes_str_expected)
        main.log.info("Routes get from ONOS CLI:")
        main.log.info(allRoutes_str_actual)
        utilities.assert_equals(expect=allRoutes_str_expected, actual=allRoutes_str_actual,
                                onpass="***Routes in SDN-IP are correct!***",
                                onfail="***Routes in SDN-IP are wrong!***")
        if(eq(allRoutes_str_expected, allRoutes_str_actual)):
            main.log.report("***Routes in SDN-IP after adding routes are correct!***")
        else:
            main.log.report("***Routes in SDN-IP after adding routes are wrong!***")

        time.sleep(20)
        get_intents_result = main.ONOScli.intents(json_format=True)


        main.step("Check MultiPointToSinglePointIntent intents installed")
        # route_intents_expected are generated when generating routes
        # get rpoute intents from ONOS CLI
        routeIntents_actual = main.QuaggaCliHost3.extract_actual_routeIntents(get_intents_result)
        routeIntents_str_expected = str(sorted(routeIntents_expected))
        routeIntents_str_actual = str(routeIntents_actual).replace('u', "")
        main.log.info("MultiPointToSinglePoint intents expected:")
        main.log.info(routeIntents_str_expected)
        main.log.info("MultiPointToSinglePoint intents get from ONOS CLI:")
        main.log.info(routeIntents_str_actual)
        utilities.assert_equals(expect=True, actual=eq(routeIntents_str_expected, routeIntents_str_actual),
                                onpass="***MultiPointToSinglePoint Intents in SDN-IP are correct!***",
                                onfail="***MultiPointToSinglePoint Intents in SDN-IP are wrong!***")

        if(eq(routeIntents_str_expected, routeIntents_str_actual)):
            main.log.report("***MultiPointToSinglePoint Intents before deleting routes correct!***")
        else:
            main.log.report("***MultiPointToSinglePoint Intents before deleting routes wrong!***")

        main.step("Check BGP PointToPointIntent intents installed")
        # bgp intents expected
        bgpIntents_expected = main.QuaggaCliHost3.generate_expected_bgpIntents(SDNIP_JSON_FILE_PATH)
        # get BGP intents from ONOS CLI
        bgpIntents_actual = main.QuaggaCliHost3.extract_actual_bgpIntents(get_intents_result)

        bgpIntents_str_expected = str(bgpIntents_expected).replace('u', "")
        bgpIntents_str_actual = str(bgpIntents_actual)
        main.log.info("PointToPointIntent intents expected:")
        main.log.info(bgpIntents_str_expected)
        main.log.info("PointToPointIntent intents get from ONOS CLI:")
        main.log.info(bgpIntents_str_actual)

        utilities.assert_equals(expect=True, actual=eq(bgpIntents_str_expected, bgpIntents_str_actual),
                                onpass="***PointToPointIntent Intents in SDN-IP are correct!***",
                                onfail="***PointToPointIntent Intents in SDN-IP are wrong!***")


        if (eq(bgpIntents_str_expected, bgpIntents_str_actual)):
            main.log.report("***PointToPointIntent Intents in SDN-IP are correct!***")
        else:
            main.log.report("***PointToPointIntent Intents in SDN-IP are wrong!***")



        #============================= Ping Test ========================
        # wait until all MultiPointToSinglePoint
        time.sleep(20)
        ping_test_script = "~/SDNIP/SdnIpIntentDemo/CASE1-ping-as2host.sh"
        ping_test_results_file = "~/SDNIP/SdnIpIntentDemo/log/CASE1-ping-results-before-delete-routes-" + strftime("%Y-%m-%d_%H:%M:%S", localtime()) + ".txt"
        ping_test_results = main.QuaggaCliHost.ping_test("1.168.30.100", ping_test_script, ping_test_results_file)
        main.log.info(ping_test_results)

        # ping test

        #============================= Deleting Routes ==================
        main.step("Check deleting routes installed")
        main.QuaggaCliHost3.delete_routes(prefixes_host3, 1)
        main.QuaggaCliHost4.delete_routes(prefixes_host4, 1)

        # main.log.info("main.ONOScli.get_routes_num() = " )
        # main.log.info(main.ONOScli.get_routes_num())
        # utilities.assert_equals(expect = "Total SDN-IP routes = 1", actual= main.ONOScli.get_routes_num(),
        get_routes_result = main.ONOScli.routes(json_format=True)
        allRoutes_actual = main.QuaggaCliHost3.extract_actual_routes(get_routes_result)
        main.log.info("allRoutes_actual = ")
        main.log.info(allRoutes_actual)

        utilities.assert_equals(expect="[]", actual=str(allRoutes_actual),
                                onpass="***Route number in SDN-IP is 0, correct!***",
                                onfail="***Routes number in SDN-IP is not 0, wrong!***")

        if(eq(allRoutes_str_expected, allRoutes_str_actual)):
            main.log.report("***Routes in SDN-IP after deleting correct!***")
        else:
            main.log.report("***Routes in SDN-IP after deleting wrong!***")

        main.step("Check intents after deleting routes")
        get_intents_result = main.ONOScli.intents(json_format=True)
        routeIntents_actual = main.QuaggaCliHost3.extract_actual_routeIntents(get_intents_result)
        main.log.info("main.ONOScli.intents()= ")
        main.log.info(routeIntents_actual)
        utilities.assert_equals(expect="[]", actual=str(routeIntents_actual),
                                onpass="***MultiPointToSinglePoint Intents number in SDN-IP is 0, correct!***",
                                onfail="***MultiPointToSinglePoint Intents number in SDN-IP is 0, wrong!***")

        if(eq(routeIntents_str_expected, routeIntents_str_actual)):
            main.log.report("***MultiPointToSinglePoint Intents after deleting routes correct!***")
        else:
            main.log.report("***MultiPointToSinglePoint Intents after deleting routes wrong!***")

        time.sleep(20)
        ping_test_script = "~/SDNIP/SdnIpIntentDemo/CASE1-ping-as2host.sh"
        ping_test_results_file = "~/SDNIP/SdnIpIntentDemo/log/CASE1-ping-results-after-delete-routes-" + strftime("%Y-%m-%d_%H:%M:%S", localtime()) + ".txt"
        ping_test_results = main.QuaggaCliHost.ping_test("1.168.30.100", ping_test_script, ping_test_results_file)
        main.log.info(ping_test_results)
        time.sleep(30)

        # main.step("Test whether Mininet is started")
        # main.Mininet2.handle.sendline("xterm host1")
        # main.Mininet2.handle.expect("mininet>")


    def CASE2(self, main):

        '''
        Test the SDN-IP functionality
        allRoutes_expected: all expected routes for all BGP peers
        routeIntents_expected: all expected MultiPointToSinglePointIntent intents
        bgpIntents_expected: expected PointToPointIntent intents
        allRoutes_actual: all routes from ONOS LCI
        routeIntents_actual: actual MultiPointToSinglePointIntent intents from ONOS CLI
        bgpIntents_actual: actual PointToPointIntent intents from ONOS CLI
        '''
        import time
        import json
        from operator import eq
        from time import localtime, strftime

        main.case("The test case is to help to setup the TestON environment and test new drivers")
        SDNIP_JSON_FILE_PATH = "../tests/SdnIpTest/sdnip.json"
        # all expected routes for all BGP peers
        allRoutes_expected = []
        main.step("Start to generate routes for all BGP peers")

        main.log.info("Generate prefixes for host3")
        prefixes_host3 = main.QuaggaCliHost3.generate_prefixes(3, 10)
        main.log.info(prefixes_host3)
        # generate route with next hop
        for prefix in prefixes_host3:
            allRoutes_expected.append(prefix + "/" + "192.168.20.1")
        routeIntents_expected_host3 = main.QuaggaCliHost3.generate_expected_onePeerRouteIntents(prefixes_host3, "192.168.20.1", "00:00:00:00:02:02", SDNIP_JSON_FILE_PATH)

        main.log.info("Generate prefixes for host4")
        prefixes_host4 = main.QuaggaCliHost4.generate_prefixes(4, 10)
        main.log.info(prefixes_host4)
        # generate route with next hop
        for prefix in prefixes_host4:
            allRoutes_expected.append(prefix + "/" + "192.168.30.1")
        routeIntents_expected_host4 = main.QuaggaCliHost4.generate_expected_onePeerRouteIntents(prefixes_host4, "192.168.30.1", "00:00:00:00:03:01", SDNIP_JSON_FILE_PATH)

        routeIntents_expected = routeIntents_expected_host3 + routeIntents_expected_host4

        main.log.report("Removing raft logs")
        main.ONOSbench.onos_remove_raft_logs()
        main.log.report("Uninstalling ONOS")
        main.ONOSbench.onos_uninstall(ONOS1_ip)

        cell_name = main.params['ENV']['cellName']
        ONOS1_ip = main.params['CTRL']['ip1']
        main.step("Set cell for ONOS-cli environment")
        main.ONOScli.set_cell(cell_name)
        verify_result = main.ONOSbench.verify_cell()
        #main.log.report("Removing raft logs")
        #main.ONOSbench.onos_remove_raft_logs()
        #main.log.report("Uninstalling ONOS")
        #main.ONOSbench.onos_uninstall(ONOS1_ip)
        main.step("Creating ONOS package")
        #package_result = main.ONOSbench.onos_package()

        main.step("Installing ONOS package")
        #onos1_install_result = main.ONOSbench.onos_install(options="-f", node=ONOS1_ip)

        main.step("Checking if ONOS is up yet")
        #time.sleep(60)
        onos1_isup = main.ONOSbench.isup(ONOS1_ip)
        if not onos1_isup:
            main.log.report("ONOS1 didn't start!")

        main.step("Start ONOS-cli")
        main.ONOScli.start_onos_cli(ONOS1_ip)

        main.step("Get devices in the network")
        list_result = main.ONOScli.devices(json_format=False)
        main.log.info(list_result)
        time.sleep(10)
        main.log.info("Installing sdn-ip feature")
        main.ONOScli.feature_install("onos-app-sdnip")
        time.sleep(10)


        main.step("Check BGP PointToPointIntent intents installed")
        # bgp intents expected
        bgpIntents_expected = main.QuaggaCliHost3.generate_expected_bgpIntents(SDNIP_JSON_FILE_PATH)
        # get BGP intents from ONOS CLI
        get_intents_result = main.ONOScli.intents(json_format=True)
        bgpIntents_actual = main.QuaggaCliHost3.extract_actual_bgpIntents(get_intents_result)

        bgpIntents_str_expected = str(bgpIntents_expected).replace('u', "")
        bgpIntents_str_actual = str(bgpIntents_actual)
        main.log.info("PointToPointIntent intents expected:")
        main.log.info(bgpIntents_str_expected)
        main.log.info("PointToPointIntent intents get from ONOS CLI:")
        main.log.info(bgpIntents_str_actual)

        utilities.assert_equals(expect=True, actual=eq(bgpIntents_str_expected, bgpIntents_str_actual),
                                onpass="***PointToPointIntent Intents in SDN-IP are correct!***",
                                onfail="***PointToPointIntent Intents in SDN-IP are wrong!***")

        if (eq(bgpIntents_str_expected, bgpIntents_str_actual)):
            main.log.report("***PointToPointIntent Intents in SDN-IP are correct!***")
        else:
            main.log.report("***PointToPointIntent Intents in SDN-IP are wrong!***")


        allRoutes_str_expected = str(sorted(allRoutes_expected))
        routeIntents_str_expected = str(sorted(routeIntents_expected))
        ping_test_script = "~/SDNIP/SdnIpIntentDemo/CASE1-ping-as2host.sh"
        # round_num = 0;
        # while(True):
        for round_num in range(1, 6):
            # round = round + 1;
            main.log.report("The Round " + str(round_num) + " test starts........................................")

            main.step("Login all BGP peers and add routes into peers")
            main.log.info("Login Quagga CLI on host3")
            main.QuaggaCliHost3.loginQuagga("1.168.30.2")
            main.log.info("Enter configuration model of Quagga CLI on host3")
            main.QuaggaCliHost3.enter_config(64514)
            main.log.info("Add routes to Quagga on host3")
            main.QuaggaCliHost3.add_routes(prefixes_host3, 1)

            main.log.info("Login Quagga CLI on host4")
            main.QuaggaCliHost4.loginQuagga("1.168.30.3")
            main.log.info("Enter configuration model of Quagga CLI on host4")
            main.QuaggaCliHost4.enter_config(64516)
            main.log.info("Add routes to Quagga on host4")
            main.QuaggaCliHost4.add_routes(prefixes_host4, 1)
            time.sleep(60)

            # get all routes inside SDN-IP
            get_routes_result = main.ONOScli.routes(json_format=True)

            # parse routes from ONOS CLI
            allRoutes_actual = main.QuaggaCliHost3.extract_actual_routes(get_routes_result)

            # allRoutes_str_expected = str(sorted(allRoutes_expected))
            allRoutes_str_actual = str(allRoutes_actual).replace('u', "")
            main.step("Check routes installed")
            main.log.info("Routes expected:")
            main.log.info(allRoutes_str_expected)
            main.log.info("Routes get from ONOS CLI:")
            main.log.info(allRoutes_str_actual)
            utilities.assert_equals(expect=allRoutes_str_expected, actual=allRoutes_str_actual,
                                    onpass="***Routes in SDN-IP are correct!***",
                                    onfail="***Routes in SDN-IP are wrong!***")
            if(eq(allRoutes_str_expected, allRoutes_str_actual)):
                main.log.report("***Routes in SDN-IP after adding correct!***")
            else:
                main.log.report("***Routes in SDN-IP after adding wrong!***")

            time.sleep(20)
            get_intents_result = main.ONOScli.intents(json_format=True)


            main.step("Check MultiPointToSinglePointIntent intents installed")
            # route_intents_expected are generated when generating routes
            # get route intents from ONOS CLI
            routeIntents_actual = main.QuaggaCliHost3.extract_actual_routeIntents(get_intents_result)
            # routeIntents_str_expected = str(sorted(routeIntents_expected))
            routeIntents_str_actual = str(routeIntents_actual).replace('u', "")
            main.log.info("MultiPointToSinglePoint intents expected:")
            main.log.info(routeIntents_str_expected)
            main.log.info("MultiPointToSinglePoint intents get from ONOS CLI:")
            main.log.info(routeIntents_str_actual)
            utilities.assert_equals(expect=True, actual=eq(routeIntents_str_expected, routeIntents_str_actual),
                                    onpass="***MultiPointToSinglePoint Intents in SDN-IP are correct!***",
                                    onfail="***MultiPointToSinglePoint Intents in SDN-IP are wrong!***")

            if(eq(routeIntents_str_expected, routeIntents_str_actual)):
                main.log.report("***MultiPointToSinglePoint Intents after adding routes correct!***")
            else:
                main.log.report("***MultiPointToSinglePoint Intents after adding routes wrong!***")

            #============================= Ping Test ========================
            # wait until all MultiPointToSinglePoint
            time.sleep(20)
            # ping_test_script = "~/SDNIP/SdnIpIntentDemo/CASE1-ping-as2host.sh"
            ping_test_results_file = "~/SDNIP/SdnIpIntentDemo/log/CASE2-Round" + str(round_num) + "-ping-results-before-delete-routes-" + strftime("%Y-%m-%d_%H:%M:%S", localtime()) + ".txt"
            ping_test_results = main.QuaggaCliHost.ping_test("1.168.30.100", ping_test_script, ping_test_results_file)
            main.log.info(ping_test_results)
            # ping test

            #============================= Deleting Routes ==================
            main.step("Check deleting routes installed")
            main.log.info("Delete routes to Quagga on host3")
            main.QuaggaCliHost3.delete_routes(prefixes_host3, 1)
            main.log.info("Delete routes to Quagga on host4")
            main.QuaggaCliHost4.delete_routes(prefixes_host4, 1)

            get_routes_result = main.ONOScli.routes(json_format=True)
            allRoutes_actual = main.QuaggaCliHost3.extract_actual_routes(get_routes_result)
            main.log.info("allRoutes_actual = ")
            main.log.info(allRoutes_actual)

            utilities.assert_equals(expect="[]", actual=str(allRoutes_actual),
                                    onpass="***Route number in SDN-IP is 0, correct!***",
                                    onfail="***Routes number in SDN-IP is not 0, wrong!***")

            if(eq(allRoutes_str_expected, allRoutes_str_actual)):
                main.log.report("***Routes in SDN-IP after deleting correct!***")
            else:
                main.log.report("***Routes in SDN-IP after deleting wrong!***")

            main.step("Check intents after deleting routes")
            get_intents_result = main.ONOScli.intents(json_format=True)
            routeIntents_actual = main.QuaggaCliHost3.extract_actual_routeIntents(get_intents_result)
            main.log.info("main.ONOScli.intents()= ")
            main.log.info(routeIntents_actual)
            utilities.assert_equals(expect="[]", actual=str(routeIntents_actual),
                                    onpass="***MultiPointToSinglePoint Intents number in SDN-IP is 0, correct!***",
                                    onfail="***MultiPointToSinglePoint Intents number in SDN-IP is 0, wrong!***")

            if(eq(routeIntents_str_expected, routeIntents_str_actual)):
                main.log.report("***MultiPointToSinglePoint Intents after deleting routes correct!***")
            else:
                main.log.report("***MultiPointToSinglePoint Intents after deleting routes wrong!***")

            time.sleep(20)
            # ping_test_script = "~/SDNIP/SdnIpIntentDemo/CASE1-ping-as2host.sh"
            ping_test_results_file = "~/SDNIP/SdnIpIntentDemo/log/CASE2-Round" + str(round_num) + "-ping-results-after-delete-routes-" + strftime("%Y-%m-%d_%H:%M:%S", localtime()) + ".txt"
            ping_test_results = main.QuaggaCliHost.ping_test("1.168.30.100", ping_test_script, ping_test_results_file)
            main.log.info(ping_test_results)
            time.sleep(30)



