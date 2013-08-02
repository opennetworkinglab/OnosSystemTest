
class TimsDeathTest:

    def __init__(self) :
        self.default = ''

    def CASE1(self,main) :
        '''
        First case is to simply check if ONOS, ZK, and Cassandra are all running properly.
        If ONOS if not running properly, it will restart ONOS once before continuing. 
        It will then check if the ONOS has a view of all the switches and links as defined in the params file.
        The test will only pass if ONOS is running properly, and has a full view of all topology elements.
        '''
        import time
        main.log.report("Checking is startup was clean")
        main.case("Checking if the startup was clean...")
        main.step("Testing startup Zookeeper")
        main.ONOS1.get_version()
        data =  main.Zookeeper1.isup()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Zookeeper is up!",onfail="Zookeeper is down...")
        main.step("Testing startup Cassandra")
        data =  main.Cassandra1.isup()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Cassandra is up!",onfail="Cassandra is down...")
        main.step("Testing startup ONOS")
        main.ONOS1.start()
        main.ONOS2.start()
        main.ONOS3.start()
        main.ONOS4.start()
        main.ONOS1.start_rest()
        main.ONOS2.start_rest()
        main.ONOS3.start_rest()
        main.ONOS4.start_rest()
        data = main.ONOS1.isup()
        if data == main.FALSE:
            main.log.info("Something is funny... restarting ONOS")
            main.ONOS1.stop()
            time.sleep(3)
            main.ONOS1.start()
            time.sleep(5)
            data = main.ONOS1.isup()
        topoview = main.ONOS1.check_status(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        if topoview == main.TRUE & data == main.TRUE :
            data = main.TRUE
        else:
            data = main.FALSE

        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="ONOS is up and running and has full view of topology",onfail="ONOS didn't start or has fragmented view of topology...")

    def CASE2(self,main) :
        '''
        Second case is to time the convergence time of a topology for ONOS. 
        It shuts down the ONOS, drops keyspace, starts ONOS...
        Then it points all the mininet switches at the ONOS node and times how long it take for the ONOS rest call to reflect the correct count of switches and links.
        '''
        import time
        main.log.report("Time convergence for switches -> single ONOS node in cluster")
        main.case("Timing Onos Convergence for switch -> a single ONOS node in the cluster")
        main.step("Bringing ONOS down...") 
        main.log.info("all switch no controllers") 
        main.Mininet1.ctrl_none()
        main.log.info("bringing ONOS down") 
        main.ONOS1.stop()
        main.ONOS2.stop()
        main.ONOS3.stop()
        main.ONOS4.stop()
        main.log.info("Dropping keyspace...")
        main.ONOS1.drop_keyspace()
        time.sleep(5)
        main.log.info("Bringing ONOS up")
        main.ONOS1.start()
        time.sleep(5) 
        main.ONOS2.start()
        main.ONOS3.start()
        main.ONOS4.start()
        onosup = main.ONOS1.isup()
        onosup = onosup & main.ONOS2.isup()
        onosup = onosup & main.ONOS3.isup()
        onosup = onosup & main.ONOS4.isup()
        onosup = onosup & main.ONOS1.check_status(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        utilities.assert_equals(expect=main.TRUE,actual=onosup,onpass="ONOS is up and running and has full view of topology",onfail="ONOS could not even start properly...")

    def CASE3(self, main) :
        import time
        main.log.report("Pointing the Switches at ONE controller...") 
        main.case("Point the switches to ONOS, ONOS must discover ") 
        main.Mininet1.ctrl_divide()
        time.sleep( 10 )
        result = main.ONOS1.check_status(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        if result == 1 : 
            test = main.TRUE
        else : 
            test = main.FALSE
        utilities.assert_equals(expect=main.TRUE,actual=test,onpass="ONOS converged",onfail="ONOS did not converge")

    def CASE4(self,main) :
        import time
        main.log.report("Test Convergence again") 
        main.case("Test Convergence again") 
        time.sleep( 5 ) 
        result = main.ONOS1.check_status(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        if result == 1 : 
            test = main.TRUE
        else : 
            test = main.FALSE
        utilities.assert_equals(expect=main.TRUE,actual=test,onpass="ONOS converged",onfail="ONOS did not converge")

    def CASE5(self,main) :
        import time
        main.log.report("Test Convergence again") 
        main.case("Test Convergence again") 
        time.sleep( 5 ) 
        result = main.ONOS1.check_status(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        if result == 1 : 
            test = main.TRUE
        else : 
            test = main.FALSE
        utilities.assert_equals(expect=main.TRUE,actual=test,onpass="ONOS converged",onfail="ONOS did not converge, moving on with the test")

    def CASE6(self,main) :
        '''
        This Test case:
            - Clears out any leftover flows
            - Adds new flows into ONOS
            - Checks flows up to 10 times waiting for each flow to be caluculated and no "NOT" statements inte get_flow
        '''
        import time
        main.log.report("Deleting and adding flows")
        main.case("Taking care of these flows!")
        main.step("Cleaning out any leftover flows...")
        main.log.info("deleting...")
        main.ONOS1.delete_flow("all")
        main.log.info("adding...")
        t1 = time.time()
        main.ONOS1.add_flow(main.params['FLOWDEF'])
        main.log.info("Checking...")
        for i in range(8):
            result = main.ONOS1.check_flow()
            if result == main.TRUE:
                t2 = time.time()
                main.log.info( 'Adding flows took %0.3f ms' % ((t2-t1)*1000.0))
                break
            time.sleep(2)
            main.log.info("Checking Flows again...")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="flows are good",onfail="FLOWS not correct")

    def CASE7(self,main) : 
        '''
        First major stir of the network... 
        '''
        main.log.report("bring down links and test pings") 
        main.case("bring down links and test pings")
        main.step("Links down") 
        for link in main.params['SET1']['begin']:
            main.log.info(str(main.params['SET1']['begin'][link]))
            main.Mininet1.link(END1=main.params['SET1']['begin'][link],END2=main.params['SET1']['end'][link],OPTION="down")
 
        main.step("Testing ping")
        success = 0
        main.log.info("starting loops") 
        result = main.Mininet1.fpingHost(src="h9",target="h33")
        for j in range(23) :
            result = result & main.Mininet1.fpingHost(src="h"+str((10+j)),target="h"+str((34+j)))
            main.log.info("result updated") 
            if result == main.TRUE:
                success = success + 1
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h"+str((33+j)),target="h"+str((57+j)))
            if result == main.TRUE:
                success = success + 1
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h"+str((57+j)),target="h"+str((81+j)))
            if result == main.TRUE:
                success = success + 1
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h"+str((81+j)),target="h"+str((9+j)))
            if result == main.TRUE:
                success = success + 1
        main.log.info("%d/98 Pings Good" % success) 
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Pings are good, flow re-route: SUCCESS",onfail="Pings are bad. flow re-route: FAILED")

    def CASE8(self,main) :
        '''
        Continued ping checking
        '''
        main.log.report("Testing flow re-route with ping")
        main.case("Testing ping")
        result = main.TRUE
        success = 0
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h%d"%(9+j),target="h%d"%(33+j))
            if result == main.TRUE:
                success = success + 1
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h%d"%(33+j),target="h%d"%(57+j))
            if result == main.TRUE:
                success = success + 1
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h%d"%(57+j),target="h%d"%(81+j))
            if result == main.TRUE:
                success = success + 1
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h%d"%(81+j),target="h%d"%(9+j))
            if result == main.TRUE:
                success = success + 1
        main.log.info("%d/98 Pings Good" % success)
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Pings are good, flow re-route: SUCCESS",onfail="Pings are bad. flow re-route: FAILED")

    def CASE9(self,main) :
        '''
        Continued ping checking
        '''
        main.log.report("Testing flow re-route with ping")
        main.case("Testing ping")
        result = main.TRUE
        success = 0
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h%d"%(9+j),target="h%d"%(33+j))
            if result == main.TRUE:
                success = success + 1
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h%d"%(33+j),target="h%d"%(57+j))
            if result == main.TRUE:
                success = success + 1
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h%d"%(57+j),target="h%d"%(81+j))
            if result == main.TRUE:
                success = success + 1
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h%d"%(81+j),target="h%d"%(9+j))
            if result == main.TRUE:
                success = success + 1
        main.log.info("%d/98 Pings Good" % success)
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Pings are good, flow re-route: SUCCESS",onfail="Pings are bad. flow re-route: FAILED, moving on... ")

    def CASE10(self,main) :
        '''
        Links back, up check pings. 
        '''
        main.log.report("bring up links and test pings")
        main.case("bring up links and test pings")
        main.step("Links up")
        for link in main.params['SET1']['begin']:
            main.log.info(str(main.params['SET1']['begin'][link]))
            main.Mininet1.link(END1=main.params['SET1']['begin'][link],END2=main.params['SET1']['end'][link],OPTION="up")

        main.step("Testing ping")
        result = main.TRUE
        success = 0 
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h%d"%(9+j),target="h%d"%(33+j))
            if result == main.TRUE:
                success = success + 1
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h%d"%(33+j),target="h%d"%(57+j))
            if result == main.TRUE:
                success = success + 1
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h%d"%(57+j),target="h%d"%(81+j))
            if result == main.TRUE:
                success = success + 1
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h%d"%(81+j),target="h%d"%(9+j))
            if result == main.TRUE:
                success = success + 1
        main.log.info("%d/98 Pings Good" % success) 
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Pings are good ",onfail="Pings are bad")

    def CASE11(self,main) : 
        '''
        Assign all switches to all Controllers, then kill 3 / 4 of the controllers
        '''
        import time
        main.log.report("Assign all switches to all Controllers, then kill 3 / 4 of the controllers") 
        main.case("Assign all switches to all Controllers, then kill 3 / 4 of the controllers") 
        main.step("Assign all switches to all Controllers...") 
        main.Mininet1.ctrl_all()
        time.sleep( 5 ) 		# Sleep for 5 sec because of my immense generosity
        main.step("Kill ONOS 1, 3, 4") 
        main.ONOS1.stop() 
        main.ONOS3.stop() 
        main.ONOS4.stop() 
        
        time.sleep( 10 ) 		# Sleep again... failover failover failover failover... 
        topoview = main.ONOS1.check_status(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        utilities.assert_equals(expect=main.TRUE,actual=topoview,onpass="ONOS has full view of topology",onfail="ONOS has fragmented view of topology...")

    def CASE12(self,main) : 
        '''
        Check Convergance
        '''
        import time
        main.log.report("Still checking convergance") 
        main.case("Call the rest call, check all switches") 
        time.sleep( 10 ) 		# Sleep again... failover failover failover failover... 
        topoview = main.ONOS1.check_status(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        utilities.assert_equals(expect=main.TRUE,actual=topoview,onpass="ONOS has full view of topology",onfail="ONOS has fragmented view of topology...")
 
    def CASE13(self,main) : 
        '''
        Check Convergance
        '''
        import time
        main.log.report("Still checking convergance") 
        main.case("Call the rest call, check all switches") 
        time.sleep( 10 ) 		# Sleep again... failover failover failover failover... 
        topoview = main.ONOS1.check_status(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        utilities.assert_equals(expect=main.TRUE,actual=topoview,onpass="ONOS has full view of topology",onfail="ONOS has fragmented view of topology...")
 
    def CASE14(self,main) : 
        '''
        Bring ONOS nodes back to a good state and check health 
        '''
        main.log.report("Bringing ONOS nodes back up and checking if they're healthy") 
        main.case("Bring up ONOS nodes") 
        import time
        main.ONOS1.start()
        main.ONOS3.start()
        main.ONOS4.start()
        onosup = main.ONOS1.isup()
        onosup = onosup & main.ONOS2.isup()
        onosup = onosup & main.ONOS3.isup()
        onosup = onosup & main.ONOS4.isup()
        onosup = onosup & main.ONOS1.check_status(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        utilities.assert_equals(expect=main.TRUE,actual=onosup,onpass="ONOS is up and running and has full view of topology",onfail="ONOS could not even start properly...")

    def CASE15(self,main):
        '''
        Make a major churn in the network again... 
        '''
        import time
        main.log.report("Maked a major churn in the network") 
        main.case("Churning the network") 
        main.step("Links down")
        for link in main.params['SET2']['begin']:
            main.log.info(str(main.params['SET2']['begin'][link]))
            main.Mininet1.link(END1=main.params['SET2']['begin'][link],END2=main.params['SET2']['end'][link],OPTION="down")
        main.step("ONOS nodes down") 
        main.ONOS2.stop()
        main.ONOS3.stop()
        main.ONOS4.stop()
        time.sleep( 10 ) 
        main.step("First ping check") 
        result = main.TRUE
        success = 0
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h%d"%(9+j),target="h%d"%(33+j))
            if result == main.TRUE:
                success = success + 1
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h%d"%(33+j),target="h%d"%(57+j))
            if result == main.TRUE:
                success = success + 1
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h%d"%(57+j),target="h%d"%(81+j))
            if result == main.TRUE:
                success = success + 1
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h%d"%(81+j),target="h%d"%(9+j))
            if result == main.TRUE:
                success = success + 1
        main.log.info("%d/98 Pings Good" % success)
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Pings are good, flow re-route: SUCCESS",onfail="Pings are bad. flow re-route: FAILED ")

    def CASE16(self,main) :
        '''
        Continued ping checking
        '''
        main.log.report("Testing flow re-route with ping")
        main.case("Testing ping")
        main.step("Second ping check") 
        result = main.TRUE
        success = 0
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h%d"%(9+j),target="h%d"%(33+j))
            if result == main.TRUE:
                success = success + 1
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h%d"%(33+j),target="h%d"%(57+j))
            if result == main.TRUE:
                success = success + 1
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h%d"%(57+j),target="h%d"%(81+j))
            if result == main.TRUE:
                success = success + 1
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h%d"%(81+j),target="h%d"%(9+j))
            if result == main.TRUE:
                success = success + 1
        main.log.info("%d/98 Pings Good" % success)
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Pings are good, flow re-route: SUCCESS",onfail="Pings are bad. flow re-route: FAILED")

    def CASE17(self,main) :
        '''
        Continued ping checking
        '''
        main.log.report("Testing flow re-route with ping")
        main.case("Testing ping")
        main.step("Third ping check")
        result = main.TRUE
        success = 0
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h%d"%(9+j),target="h%d"%(33+j))
            if result == main.TRUE:
                success = success + 1
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h%d"%(33+j),target="h%d"%(57+j))
            if result == main.TRUE:
                success = success + 1
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h%d"%(57+j),target="h%d"%(81+j))
            if result == main.TRUE:
                success = success + 1
        for j in range(24) :
            result = result & main.Mininet1.fpingHost(src="h%d"%(81+j),target="h%d"%(9+j))
            if result == main.TRUE:
                success = success + 1
        main.log.info("%d/98 Pings Good" % success)
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Pings are good, flow re-route: SUCCESS",onfail="Pings are bad. flow re-route: FAILED")
