
#Testing the basic functionality of SDN-IP

class SdnIpTest:
    def __init__(self):
        self.default = ''

    def CASE1(self, main):

        '''
        Test the SDN-IP functionality
        '''
        import time
        import json
        from operator import eq
        
        # all generated routes for all BGP peers
        allRoutes = []

        main.step("Start to generate routes for BGP peer on host1")
        routes = main.Quaggacli.generate_routes(1, 3)
        main.log.info(routes)
        
        for route in routes:
            allRoutes.append(route + "/" + "1.1.1.1")

        # start to insert routes into the bgp peer
        main.step("Start Quagga-cli on host1")
        main.Quaggacli.loginQuagga("1.1.1.1")

        main.step("Start to configure Quagga on host1")
        main.Quaggacli.enter_config(64513)
    
        main.step("Start to generate and add routes for BGP peer on host1")    
        routes = main.Quaggacli.generate_routes(8, 3)
        main.Quaggacli.add_routes(routes, 1)
             
        # add generates routes to allRoutes
        for route in routes:
            allRoutes.append(route + "/" + "1.1.1.1")

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
        routes_list = []
        routes_json_obj = json.loads(get_routes_result)   
        for route in routes_json_obj:
            if route['prefix'] == '172.16.10.0/24':
                continue
            routes_list.append(route['prefix'] + "/" + route['nextHop'])
      
        main.log.info("Start to checking routes")
        main.log.info("Routes inserted into the system:")
        main.log.info(sorted(allRoutes))
        main.log.info("Routes get from ONOS CLI:")
        main.log.info(sorted(routes_list))

        if eq(sorted(allRoutes), sorted(routes_list)): 
            main.log.report("***Routes in SDN-IP are correct!***")
        else:
            main.log.report("***Routes in SDN-IP are wrong!***")
        
        time.sleep(2)
        main.step("Get intents installed on ONOS")
        get_intents_result = main.ONOScli.intents(json_format=True)
        main.log.info(get_intents_result)


        #main.step("Test whether Mininet is started")
        #main.Mininet2.handle.sendline("xterm host1")
        #main.Mininet2.handle.expect("mininet>")

