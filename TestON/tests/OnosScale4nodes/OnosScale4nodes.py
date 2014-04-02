
class OnosScale4nodes:

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
        main.Zookeeper1.start()
        main.Zookeeper2.start()
        main.Zookeeper3.start()
        main.Zookeeper4.start()
        main.ONOS1.stop()
        main.ONOS2.stop()
        main.ONOS3.stop()
        main.ONOS4.stop()
        main.Cassandra1.start()
        main.Cassandra2.start()
        main.Cassandra3.start()
        main.Cassandra4.start()
        time.sleep(20)
        main.ONOS1.drop_keyspace()
        main.ONOS1.start()
        time.sleep(10)
        main.ONOS2.start()
        main.ONOS3.start()
        main.ONOS4.start()
        main.ONOS1.start_rest()
        time.sleep(5)
        test= main.ONOS1.rest_status()
        if test == main.FALSE:
            main.ONOS1.start_rest()
        main.ONOS1.get_version()
        main.log.report("Startup check Zookeeper1, Cassandra1, and ONOS1 connections")
        main.case("Checking if the startup was clean...")
        main.step("Testing startup Zookeeper")
        data =  main.Zookeeper1.isup()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Zookeeper is up!",onfail="Zookeeper is down...")
        main.step("Testing startup Cassandra")
        data =  main.Cassandra1.isup()
        if data == main.FALSE:
            main.Cassandra1.stop()
            main.Cassandra2.stop()
            main.Cassandra3.stop()
            main.Cassandra4.stop()

            time.sleep(5)

            main.Cassandra1.start()
            main.Cassandra2.start()
            main.Cassandra3.start()
            main.Cassandra4.start()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Cassandra is up!",onfail="Cassandra is down...")
        main.step("Testing startup ONOS")
        data = main.ONOS1.isup()
        data = data and main.ONOS2.isup()
        data = data and main.ONOS3.isup()
        data = data and main.ONOS4.isup()
        if data == main.FALSE:
            main.log.report("Something is funny... restarting ONOS")
            main.ONOS1.stop()
            main.ONOS2.stop()
            main.ONOS3.stop()
            main.ONOS4.stop()
            time.sleep(5)
            main.ONOS1.start()
            time.sleep(10)
            main.ONOS2.start()
            main.ONOS3.start()
            main.ONOS4.start()
            data = main.ONOS1.isup()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="ONOS is up and running!",onfail="ONOS didn't start...")

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
        main.ONOS1.isup()
        main.ONOS2.isup()
        main.ONOS3.isup()
        main.ONOS4.isup()
        main.ONOS1.check_status(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        main.log.info("Pointing the Switches at ONE controller... then BEGIN time") 
        main.Mininet1.ctrl_local()
        t1 = time.time()
        for i in range(15) : 
            result = main.ONOS1.check_status(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
            if result == 1 : 
                break
            else : 
                time.sleep(1)
        t2 = time.time()
        conv_time = t2 - t1
        main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        if result == 1 : 
            main.log.report( "Convergence time of : %f seconds" % conv_time ) 
            if float(conv_time) < float(main.params['TargetTime']) :
                test=main.TRUE
                main.log.info("Time is less then supplied target time")
            else:
                test=main.FALSE
                main.log.info("Time is greater then supplied target time")
        else : 
            main.log.report( "ONOS did NOT converge over : %f seconds" % conv_time ) 
            test=main.FALSE
 
        utilities.assert_equals(expect=main.TRUE,actual=test)

    def CASE3(self,main) :
        '''
        Second case is to time the convergence time of a topology for ONOS. 
        It shuts down the ONOS, drops keyspace, starts ONOS...
        Then it points all the mininet switches at all ONOS nodes and times how long it take for the ONOS rest call to reflect the correct count of switches and links.
        '''
        import time
        main.log.report("Time convergence for switches -> all ONOS nodes in cluster")
        main.case("Timing Onos Convergence for switch -> all ONOS nodes in cluster")
        main.step("Bringing ONOS down...") 
        main.log.info("all switch no controllers") 
        main.Mininet1.ctrl_none()
        main.log.info("bringing ONOS down") 
        main.ONOS1.stop()
        main.ONOS2.stop()
        main.ONOS3.stop()
        main.ONOS4.stop()
        #main.log.info("Dropping keyspace...")
        #main.ONOS1.drop_keyspace()
        time.sleep(5)
        main.log.info("Bringing ONOS up")
        main.ONOS1.start()
        time.sleep(5) 
        main.ONOS2.start()
        main.ONOS2.start_rest()
        main.ONOS3.start()
        main.ONOS4.start()
        main.ONOS1.isup()
        main.ONOS2.isup()
        main.ONOS3.isup()
        main.ONOS4.isup()
        main.ONOS1.check_status(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        main.log.info("Pointing the Switches at ALL controllers... then BEGIN time") 
        main.Mininet1.ctrl_all()
        t1 = time.time()
        for i in range(15) : 
            result = main.ONOS1.check_status(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
            if result == 1 : 
                break
            else : 
                time.sleep(1)
        t2 = time.time()
        conv_time = t2 - t1
        main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        if result == 1 : 
            main.log.report( "Convergence time of : %f seconds" % conv_time ) 
            if float(conv_time) < float(main.params['TargetTime']) :
                test=main.TRUE
                main.log.info("Time is less then supplied target time")
            else:
                test=main.FALSE
                main.log.info("Time is greater then supplied target time")
        else : 
            main.log.report( "ONOS did NOT converge over : %f seconds" % conv_time ) 
            test=main.FALSE
 
        utilities.assert_equals(expect=main.TRUE,actual=test)

    def CASE4(self,main) :
        '''
        Second case is to time the convergence time of a topology for ONOS. 
        It shuts down the ONOS, drops keyspace, starts ONOS...
        Then it evenly points all mininet switches to all ONOS nodes, but only one node, and times how long it take for the ONOS rest call to reflect the correct count of switches and links.
        '''
        import time
        main.log.report("Time convergence for switches -> Divide switches equall among all  nodes in cluster")
        main.case("Timing Onos Convergence for even single controller distribution")
        main.step("Bringing ONOS down...") 
        main.log.info("all switch no controllers") 
        main.Mininet1.ctrl_none()
        main.log.info("bringing ONOS down") 
        main.ONOS1.stop()
        main.ONOS2.stop()
        main.ONOS3.stop()
        main.ONOS4.stop()
        #main.log.info("Dropping keyspace...")
        #main.ONOS1.drop_keyspace()
        time.sleep(5)
        main.log.info("Bringing ONOS up")
        main.ONOS1.start()
        time.sleep(5) 
        main.ONOS2.start()
        main.ONOS2.start_rest()
        main.ONOS3.start()
        main.ONOS4.start()
        main.ONOS1.isup()
        main.ONOS2.isup()
        main.ONOS3.isup()
        main.ONOS4.isup()
        main.ONOS1.check_status(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        main.log.info("Pointing the Switches to alternating controllers... then BEGIN time") 
        main.Mininet1.ctrl_divide()
        t1 = time.time()
        for i in range(15) : 
            result = main.ONOS1.check_status(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
            if result == 1 : 
                break
            else : 
                time.sleep(1)
        t2 = time.time()
        conv_time = t2 - t1
        main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        if result == 1 : 
            main.log.report( "Convergence time of : %f seconds" % conv_time ) 
            if float(conv_time) < float(main.params['TargetTime']) :
                test=main.TRUE
                main.log.info("Time is less then supplied target time")
            else:
                test=main.FALSE
                main.log.info("Time is greater then supplied target time")
        else : 
            main.log.report( "ONOS did NOT converge over : %f seconds" % conv_time ) 
            test=main.FALSE
 
        utilities.assert_equals(expect=main.TRUE,actual=test)

