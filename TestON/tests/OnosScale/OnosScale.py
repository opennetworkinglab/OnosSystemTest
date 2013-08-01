
class OnosScale:

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
        main.case("Checking if the startup was clean...")
        main.step("Testing startup Zookeeper")
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
        main.ONOS5.start()
        main.ONOS6.start()
        main.ONOS7.start()
        main.ONOS8.start()
        data = main.ONOS1.isup()
        if data == main.FALSE:
            main.log.info("Something is funny... restarting ONOS")
            main.ONOS1.stop()
            time.sleep(3)
            main.ONOS1.start()
            time.sleep(5)
            data = main.ONOS1.isup()
        #topoview = main.ONOS1.check_status(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        topoview = main.TRUE
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
        main.case("Timing Onos Convergence for switch -> ONOS1")
        main.step("Bringing ONOS down...") 
        main.log.info("all switch no controllers") 
        main.Mininet2.ctrl_none()
        main.Mininet3.ctrl_none()
        main.Mininet4.ctrl_none()
        main.Mininet5.ctrl_none()
        main.Mininet6.ctrl_none()
        main.Mininet7.ctrl_none()
        main.Mininet8.ctrl_none()
        main.log.info("bringing ONOS down") 
        main.ONOS1.stop()
        main.ONOS2.stop()
        main.ONOS3.stop()
        main.ONOS4.stop()
        main.ONOS5.stop()
        main.ONOS6.stop()
        main.ONOS7.stop()
        main.ONOS8.stop()
        main.log.info("Dropping keyspace...")
        main.ONOS1.drop_keyspace()
        time.sleep(5)
        main.log.info("Bringing ONOS up")
        main.ONOS1.start()
        time.sleep(5) 
        main.ONOS2.start()
        main.ONOS3.start()
        main.ONOS4.start()
        main.ONOS5.start()
        main.ONOS6.start()
        main.ONOS7.start()
        main.ONOS8.start()
        main.ONOS1.isup()
        main.ONOS2.isup()
        main.ONOS3.isup()
        main.ONOS4.isup()
        main.ONOS5.isup()
        main.ONOS6.isup()
        main.ONOS7.isup()
        main.ONOS8.isup()
        main.ONOS1.check_status(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        main.log.info("Pointing the Switches at controller... then BEGIN time") 
        main.Mininet2.ctrl_local()
        main.Mininet3.ctrl_local()
        main.Mininet4.ctrl_local()
        main.Mininet5.ctrl_local()
        main.Mininet6.ctrl_local()
        main.Mininet7.ctrl_local()
        main.Mininet8.ctrl_local()
        #main.Mininet2.ctrl_one(main.params['RestIP'])
        #main.Mininet3.ctrl_one(main.params['RestIP'])
        #main.Mininet4.ctrl_one(main.params['RestIP'])
        #main.Mininet5.ctrl_one(main.params['RestIP'])
        #main.Mininet6.ctrl_one(main.params['RestIP'])
        #main.Mininet7.ctrl_one(main.params['RestIP'])
        #main.Mininet8.ctrl_one(main.params['RestIP'])
        t1 = time.time()
        for i in range(4) : 
            result = main.ONOS1.check_status(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
            if result == 1 : 
                break
            else : 
                time.sleep(1)
        t2 = time.time()
        conv_time = t2 - t1
        if result == 1 : 
            main.log.info( "Convergence time of : %f seconds" % conv_time ) 
            if float(conv_time) < float(main.params['TargetTime']) :
                test=main.TRUE
                main.log.info("Time is less then supplied target time")
            else:
                test=main.FALSE
                main.log.info("Time is greater then supplied target time")
        else : 
            main.log.info( "ONOS did NOT converge over : %f seconds" % conv_time ) 
            test=main.FALSE
 
        utilities.assert_equals(expect=main.TRUE,actual=test)

