class SDNIPRouteTest :

    def __init__(self) :
        self.default = ''

    def CASE1(self):
        
        result = main.Quagga1.enter_config(1)
        result = result and main.Quagga2.enter_config(2)
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Entered config mode successfully",onfail="Failed to enter config mode")
    
        result = main.Dataplane1.create_interfaces(main.params['Q1']['net'],main.params['numRoutes'],main.params['Q1']['startNet'])
        result = result and main.Dataplane2.create_interfaces(main.params['Q2']['net'],main.params['numRoutes'],main.params['Q2']['startNet'])
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Interfaces created successfully",onfail="Failed to create interfaces")
    def CASE2(self):
        import time

        main.log.info('Adding routes into Quagga1 and Quagga2')
        result = main.Quagga1.add_route(str(main.params['Q1']['net']),int(main.params['numRoutes']),int(main.params['Q1']['routeRate']))
        result = result and main.Quagga2.add_route(str(main.params['Q2']['net']),int(main.params['numRoutes']),int(main.params['Q2']['routeRate']))
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Added routes successfully",onfail="Failed to add routes")

        main.log.info('Routes added, now waiting 30 seconds')
        time.sleep(30)

        main.log.info('Dataplane1 pinging all interfaces on Dataplane1')
        result = main.Dataplane1.pingall_interfaces(main.params['DP1']['pingIntf'],main.params['Q2']['net'],main.params['Q2']['startNet'],main.params['numRoutes'])
        main.log.info('Dataplane2 pinging all interfaces on Dataplane2')
        result = result and main.Dataplane2.pingall_interfaces(main.params['DP2']['pingIntf'],main.params['Q1']['net'],main.params['Q1']['startNet'],main.params['numRoutes'])
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Switches properly direct traffic",onfail="Network unable to ping")
        
    def CASE3(self):
        import time

        main.log.info('Removing routes on Quagga1 and Quagga2')
        result = main.Quagga1.del_route(str(main.params['Q1']['net']),int(main.params['numRoutes']),int(main.params['Q1']['routeRate']))
        result = result and main.Quagga2.del_route(str(main.params['Q2']['net']),int(main.params['numRoutes']),int(main.params['Q2']['routeRate']))
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Removed routes successfully",onfail="Failed to remove routes")

        main.log.info('Routes removed, now waiting 30 seconds')
        time.sleep(30)

        main.log.info('Dataplane1 pinging all interfaces on Dataplane1')
        result = main.Dataplane1.pingall_interfaces(main.params['DP1']['pingIntf'],main.params['Q2']['net'],main.params['Q2']['startNet'],main.params['numRoutes'])
        main.log.info('Dataplane2 pinging all interfaces on Dataplane2')
        result = result and main.Dataplane2.pingall_interfaces(main.params['DP2']['pingIntf'],main.params['Q1']['net'],main.params['Q1']['startNet'],main.params['numRoutes'])
        utilities.assert_equals(expect=main.FALSE,actual=result,onpass="Flows removed properly",onfail="Flows still present")

        '''
        num_routes = int(main.params['Q1']['numRoutes'])
        a = str(Q2check)
        main.log.info("The number of routes checked are" + a)
        #print Q2check
        #if Q1check == num_routes:
        #    main.log.info("all routes added from Quagga1 successfully")
        #else:
        #    main.log.info("failed to add routes from Quagga1 fully")
        if Q2check == num_routes:
            print "all routes added from Quagga2 successfully"
        else:
            print "failed to add routes from Quagga2 fully"
        #delresult = main.Quagga1.del_route(str(main.params['Q1']['net']),int(main.params['Q1']['numRoutes']),int(main.params['Q1']['routeRate']))
        delresult = main.Quagga2.del_route(str(main.params['Q2']['net']),int(main.params['Q2']['numRoutes']),int(main.params['Q2']['routeRate'])) 
        utilities.assert_equals(expect=main.TRUE,actual=delresult,onpass="Deleted routes successfully",onfaile="Failed to delete routes")
        '''
