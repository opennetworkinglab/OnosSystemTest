
class RCOnosScale4nodes:

    def __init__(self) :
        self.default = ''

    def CASE1(self,main) :
        '''
        First case is to simply check if ONOS, ZK, and RamCloud are all running properly.
        If ONOS if not running properly, it will restart ONOS once before continuing. 
        It will then check if the ONOS has a view of all the switches and links as defined in the params file.
        The test will only pass if ONOS is running properly, and has a full view of all topology elements.
        '''
        import time
        main.case("Initial setup")
        main.step("stopping ONOS")
        main.ONOS1.stop()
        main.ONOS2.stop()
        main.ONOS3.stop()
        main.ONOS4.stop()
        main.RamCloud1.stop_coor()
        main.RamCloud1.stop_serv()
        main.RamCloud2.stop_serv()
        main.RamCloud3.stop_serv()
        main.RamCloud4.stop_serv()
        main.step("Start tcpdump on mn")
        main.Mininet1.start_tcpdump(main.params['tcpdump']['filename'], intf = main.params['tcpdump']['intf'], port = main.params['tcpdump']['port'])
#        main.step("Start tcpdump on mn")
#        main.Mininet1.start_tcpdump(main.params['tcpdump']['filename'], intf = main.params['tcpdump']['intf'], port = main.params['tcpdump']['port'])
        main.step("Starting ONOS")
        main.Zookeeper1.start()
        main.Zookeeper2.start()
        main.Zookeeper3.start()
        main.Zookeeper4.start()
        time.sleep(10)
        main.RamCloud1.del_db()
        main.RamCloud2.del_db()
        main.RamCloud3.del_db()
        main.RamCloud4.del_db()
        
        main.RamCloud1.start_coor()
        time.sleep(10)
        main.RamCloud1.start_serv()
        main.RamCloud2.start_serv()
        main.RamCloud3.start_serv()
        main.RamCloud4.start_serv()
        time.sleep(20)
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
        main.log.report("Startup check Zookeeper1, RamCloud1, and ONOS1 connections")
        main.step("Testing startup Zookeeper")
        data =  main.Zookeeper1.isup()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Zookeeper is up!",onfail="Zookeeper is down...")
        main.step("Testing startup RamCloud")
        data =  main.RamCloud1.status_serv()
        if data == main.FALSE:
            main.RamCloud1.stop_coor()
            main.RamCloud1.stop_serv()
            main.RamCloud2.stop_serv()
            main.RamCloud3.stop_serv()
            main.RamCloud4.stop_serv()
            main.RamCloud1.del_db()
            main.RamCloud2.del_db()
            main.RamCloud3.del_db()
            main.RamCloud4.del_db()

            time.sleep(5)

            main.RamCloud1.start_coor()
            main.RamCloud1.start_serv()
            main.RamCloud2.start_serv()
            main.RamCloud3.start_serv()
            main.RamCloud4.start_serv()
        data =  main.RamCloud1.isup()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="RamCloud is up!",onfail="RamCloud is down...")
        main.step("Testing startup ONOS")
        time.sleep(10)
        data = main.ONOS1.isup()
        data = data and main.ONOS2.isup()
        data = data and main.ONOS3.isup()
        data = data and main.ONOS4.isup()
        if data == main.FALSE:
            main.log.report("Something is funny... restarting ONOS")
            time.sleep(10)
            data = main.ONOS1.isup()
            data = data and main.ONOS2.isup()
            data = data and main.ONOS3.isup()
            data = data and main.ONOS4.isup()

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
        for i in range(1,int(main.params['NR_Switches'])+1):
            main.Mininet1.delete_sw_controller("s"+str(i))
        main.log.info("bringing ONOS down") 
        main.ONOS1.stop()
        main.ONOS2.stop()
        main.ONOS3.stop()
        main.ONOS4.stop()
        main.RamCloud1.stop_coor()
        main.RamCloud1.stop_serv()
        main.RamCloud2.stop_serv()
        main.RamCloud3.stop_serv()
        main.RamCloud4.stop_serv()
        main.Zookeeper1.start()
        main.Zookeeper2.start()
        main.Zookeeper3.start()
        main.Zookeeper4.start()
        time.sleep(4)
        main.RamCloud1.del_db()
        main.RamCloud2.del_db()
        main.RamCloud3.del_db()
        main.RamCloud4.del_db()

        time.sleep(5)

        main.RamCloud1.start_coor()
        main.RamCloud1.start_serv()
        main.RamCloud2.start_serv()
        main.RamCloud3.start_serv()
        main.RamCloud4.start_serv()
        
        main.log.info("Bringing ONOS up")
        main.ONOS1.start()
        time.sleep(5) 
        main.ONOS2.start()
        main.ONOS3.start()
        main.ONOS4.start()
        time.sleep(10)
        data = main.ONOS1.isup()
        data = data and main.ONOS2.isup()
        data = data and main.ONOS3.isup()
        data = data and main.ONOS4.isup()
        if data == main.FALSE:
            main.log.report("Something is funny... restarting ONOS")
            time.sleep(10)
            data = main.ONOS1.isup()
            data = data and main.ONOS2.isup()
            data = data and main.ONOS3.isup()
            data = data and main.ONOS4.isup()
        if data == main.FALSE:
            main.log.report("Something is funny... restarting ONOS")
        main.ONOS1.check_status(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])

        main.log.info("Pointing the Switches at ONE controller... then BEGIN time") 
        for i in range(1,int(main.params['NR_Switches'])+1):
            main.Mininet1.assign_sw_controller(sw=str(i),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])



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
        for i in range(1,int(main.params['NR_Switches'])+1):
            main.Mininet1.delete_sw_controller("s"+str(i))
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
        for i in range(1,int(main.params['NR_Switches'])+1):
            main.Mininet1.assign_sw_controller(sw=str(i),count=4,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'])
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
        for i in range(1,int(main.params['NR_Switches'])+1):
            main.Mininet1.delete_sw_controller("s"+str(i))
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
        count = 0
        for i in range(1,int(main.params['NR_Switches'])+1):
            num = (count % 4)+1
            #num = count % len(controllers) #TODO: check number of controllers in cluster
            main.Mininet1.assign_sw_controller(sw=str(i),ip1=main.params['CTRL']['ip'+str(num)],port1=main.params['CTRL']['port'+str(num)])
            count = count + 1


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

    def CASE66(self, main):
        main.log.report("Checking ONOS logs for exceptions")
        count = 0
        check1 = main.ONOS1.check_exceptions()
        main.log.report("Exceptions in ONOS1 logs: \n" + check1)
        check2 = main.ONOS2.check_exceptions()
        main.log.report("Exceptions in ONOS2 logs: \n" + check2)
        check3 = main.ONOS3.check_exceptions()
        main.log.report("Exceptions in ONOS3 logs: \n" + check3)
        check4 = main.ONOS4.check_exceptions()
        main.log.report("Exceptions in ONOS4 logs: \n" + check4)
        result = main.TRUE
        if (check1 or check2 or check3 or check4):
            result = main.FALSE
            count = len(check1.splitlines()) + len(check2.splitlines()) + len(check3.splitlines()) + len(check4.splitlines())
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="No Exceptions found in the logs",onfail=str(count) + " Exceptions were found in the logs")
        main.Mininet1.stop_tcpdump()


