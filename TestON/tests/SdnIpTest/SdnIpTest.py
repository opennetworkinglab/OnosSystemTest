
#Testing the basic functionality of SDN-IP

class SdnIpTest:
    def __init__(self):
        self.default = ''

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
        
        SDNIP_JSON_FILE_PATH = "../tests/SdnIpTest/sdnip.json"
        # all expected routes for all BGP peers
        allRoutes_expected = []
        main.step("Start to generate routes for BGP peer on host1")
        prefixes = main.Quaggacli.generate_prefixes(1, 3)
        main.log.info(prefixes)

        # TODO: delete the static prefix below after integration with Demo Mininet script
        prefixes = []
        prefixes.append("172.16.30.0/24")
        prefixes.append("1.0.0.0/24")
        prefixes.append("2.0.0.0/24")
        prefixes.append("3.0.0.0/24")


        for prefix in prefixes:
            # generate route with next hop
            allRoutes_expected.append(prefix + "/" + "1.1.1.1")

        routeIntents_expected = main.Quaggacli.generate_expected_onePeerRouteIntents(prefixes, "192.168.30.1", "00:00:00:00:03:01", SDNIP_JSON_FILE_PATH)

        # start to insert routes into the bgp peer
        main.step("Start Quagga-cli on host1")
        main.Quaggacli.loginQuagga("1.1.1.1")

        main.step("Start to configure Quagga on host1")
        main.Quaggacli.enter_config(64513)
    
        main.step("Start to generate and add routes for BGP peer on host1")
        routes = main.Quaggacli.generate_prefixes(8, 3)
        main.Quaggacli.add_routes(routes, 1)
             
        # add generates routes to allRoutes
        for route in routes:
            allRoutes_expected.append(route + "/" + "1.1.1.1")

        cell_name = main.params['ENV']['cellName']
        ONOS1_ip = main.params['CTRL']['ip1']

        main.step("Starting ONOS service")
        # TODO: start ONOS from Mininet Script
        # start_result = main.ONOSbench.onos_start("127.0.0.1")

        main.step("Set cell for ONOS-cli environment")
        main.ONOScli.set_cell(cell_name)
   
        main.step("Start ONOS-cli")
        # TODO: change the hardcode in start_onos_cli method in ONOS CLI driver
        time.sleep(5)
        main.ONOScli.start_onos_cli(ONOS1_ip)    

        main.step("Get devices in the network")
        list_result = main.ONOScli.devices(json_format=False)
        main.log.info(list_result)

        #get all routes inside SDN-IP
        get_routes_result = main.ONOScli.routes(json_format=True)  
                     
        # parse routes from ONOS CLI
        allRoutes_actual = main.Quaggacli.extract_actual_routes(get_routes_result)
      
        main.step("Check routes installed")
        main.log.info("Routes expected:")
        main.log.info(sorted(allRoutes_expected))
        main.log.info("Routes get from ONOS CLI:")
        main.log.info(allRoutes_actual)
        utilities.assert_equals(expect=sorted(allRoutes_expected), actual=allRoutes_actual,
                                onpass="***Routes in SDN-IP are correct!***",
                                onfail="***Routes in SDN-IP are wrong!***")

        time.sleep(2)
        get_intents_result = main.ONOScli.intents(json_format=True)


        main.step("Check MultiPointToSinglePointIntent intents installed")
        # route_intents_expected are generated when generating routes
        # get rpoute intents from ONOS CLI
        routeIntents_actual  = main.Quaggacli.extract_actual_routeIntents(get_intents_result)
        main.log.info("MultiPointToSinglePoint intents expected:")
        main.log.info(routeIntents_expected)
        main.log.info("MultiPointToSinglePoint intents get from ONOS CLI:")
        main.log.info(routeIntents_actual)
        utilities.assert_equals(expect=True, actual=eq(routeIntents_expected, routeIntents_actual),
                                onpass="***MultiPointToSinglePoint Intents in SDN-IP are correct!***",
                                onfail="***MultiPointToSinglePoint Intents in SDN-IP are wrong!***")


        main.step("Check BGP PointToPointIntent intents installed")
        # bgp intents expected
        bgpIntents_expected = main.Quaggacli.generate_expected_bgpIntents(SDNIP_JSON_FILE_PATH)
        # get BGP intents from ONOS CLI
        bgpIntents_actual = main.Quaggacli.extract_actual_bgpIntents(get_intents_result)
        main.log.info("PointToPointIntent intents expected:")
        main.log.info(str(bgpIntents_expected).replace('u',""))
        main.log.info("PointToPointIntent intents get from ONOS CLI:")
        main.log.info(bgpIntents_actual)
        utilities.assert_equals(expect=True, actual=eq(str(bgpIntents_expected).replace('u',""), str(bgpIntents_actual)),
                                onpass="***PointToPointIntent Intents in SDN-IP are correct!***",
                                onfail="***PointToPointIntent Intents in SDN-IP are wrong!***")

        #main.step("Test whether Mininet is started")
        #main.Mininet2.handle.sendline("xterm host1")
        #main.Mininet2.handle.expect("mininet>")

