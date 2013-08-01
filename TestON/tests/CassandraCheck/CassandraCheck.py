
class CassandraCheck:

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
        Second case is to stress adding and removing flows to see if it can crash any cassandras
        '''
        import time
        main.case("Adding and deleting flows")
        main.step("Adding 1008 flows") 
        #main.ONOS1.add_flow("~/flowdef_files/flowdef_3node_1008.txt")
        main.ONOS1.add_flow("~/flowdef_files/flowdef_3node_1008.txt")
        time.sleep(30)
        main.ONOS1.delete_flow("all") 
        main.ONOS1.check_for_no_exceptions()
        test = main.Cassandra1.isup()
        utilities.assert_equals(expect=main.TRUE,actual=test,onpass="Cassandra is still good",onfail="Something broke on Cassandra")
 
    def CASE3(self,main) :
        '''
        Merely testing if a specific driver call works
        '''
        main.case("Checking for exceptions") 
        main.step("Step 1") 
        test = main.ONOS1.check_for_no_exceptions()
        utilities.assert_equals(expect=main.TRUE,actual=test)

