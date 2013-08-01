
class OnosPerf:

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
        #main.step("Pulling and Compiling ONOS Repo")
        #main.ONOS1.git_pull()
        main.ONOS1.drop_keyspace()
        time.sleep(5) 
        main.ONOS1.start()
        time.sleep(5)
        main.ONOS2.start()
        main.ONOS3.start()
        main.ONOS4.start()
        main.ONOS5.start()
        main.ONOS6.start()
        main.ONOS7.start()
        main.ONOS8.start()
        main.step("Testing startup ONOS")
        data = main.ONOS1.isup()
        if data == main.FALSE:
            main.log.info("Something is funny... restarting ONOS")
            main.ONOS1.stop()
            time.sleep(3)
            main.ONOS1.start()
            time.sleep(5)
            data = main.ONOS1.isup()
        #topoview = main.ONOS1.check_status(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])

        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="ONOS is up and running ",onfail="ONOS didn't start ...")

    def CASE2(self,main) :
        '''
        Makes sure that the HW links are all up
        Verifies that at least one mininet host exists.
        Proves that there is actually a mininet that we are working with
        '''
        import time
        main.case("Bringing Link up... ")
        main.ONOS1.link_up(SDPID=main.params['LINK1']['dpid1'],SPORT=main.params['LINK1']['port1'],DDPID=main.params['LINK1']['dpid2'],DPORT=main.params['LINK1']['port2'])
        main.log.info( "Waiting 10 seconds.... " )
        time.sleep(10)
        main.step("Checking if MN switches exist")
        result = main.TRUE
        result = result & main.Mininet2.checknum(main.params['MN_size'])
        result = result & main.Mininet3.checknum(main.params['MN_size'])
        result = result & main.Mininet4.checknum(main.params['MN_size'])
        result = result & main.Mininet5.checknum(main.params['MN_size'])
        result = result & main.Mininet6.checknum(main.params['MN_size'])
        result = result & main.Mininet7.checknum(main.params['MN_size'])
        result = result & main.Mininet8.checknum(main.params['MN_size'])
        main.step("Verifying the result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="MN switches exist",onfail="MN is missing switches")


    def CASE3(self,main) :
        '''
        This Test case: 
            - Clears out any leftover flows
            - Adds new flows into ONOS
            - Checks flows up to 10 times waiting for each flow to be caluculated and no "NOT" statements inte get_flow
        '''
        import time
        main.case("Taking care of these flows!") 
        main.step("Cleaning out any leftover flows...")
        main.log.info("deleting...")
        main.ONOS1.delete_flow("all")
        main.log.info("adding...")
        t1 = time.time()
        main.ONOS1.add_flow(main.params['FLOWDEF'])   
        main.log.info("Checking...")
        for i in range(15):
            result = main.ONOS1.check_flow()
            if result == main.TRUE: 
                t2 = time.time()
                main.log.info( 'Adding flows took %0.3f ms' % ((t2-t1)*1000.0))
                break
            time.sleep(2)
            main.log.info("Checking Flows again...")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="flows are good",onfail="FLOWS not correct") 


    def CASE4(self,main) :
        '''
        Tests a single ping 
        '''
        main.case("Testing ping...")
        ping_result = main.Mininet4.pingHost(src=main.params['PING']['source1'],target=main.params['PING']['target1'])
        utilities.assert_equals(expect=main.TRUE,actual=ping_result,onpass="NO PACKET LOSS, HOST IS REACHABLE",onfail="PACKET LOST, HOST IS NOT REACHABLE") 


    def CASE5(self,main) :
        '''
        Starts continuous pings on the Mininet nodes
        '''
        import time
        main.case("Starting long ping... ") 
        main.Mininet4.pingLong(src=main.params['PING']['source1'],target=main.params['PING']['target1'])
        main.Mininet4.pingLong(src=main.params['PING']['source2'],target=main.params['PING']['target2'])
        main.Mininet4.pingLong(src=main.params['PING']['source3'],target=main.params['PING']['target3'])
        main.Mininet4.pingLong(src=main.params['PING']['source4'],target=main.params['PING']['target4'])
        main.Mininet4.pingLong(src=main.params['PING']['source5'],target=main.params['PING']['target5'])
        main.Mininet4.pingLong(src=main.params['PING']['source6'],target=main.params['PING']['target6'])
        main.Mininet4.pingLong(src=main.params['PING']['source7'],target=main.params['PING']['target7'])
        main.Mininet4.pingLong(src=main.params['PING']['source8'],target=main.params['PING']['target8'])
        main.Mininet4.pingLong(src=main.params['PING']['source9'],target=main.params['PING']['target9'])
        main.Mininet4.pingLong(src=main.params['PING']['source10'],target=main.params['PING']['target10'])
        time.sleep(5) 
        result = main.Mininet4.pingstatus()
        utilities.assert_equals(expect=main.TRUE,actual=result) 


    def CASE6(self,main) : 
        '''
        Brings the defined link down and up a certain number of iterations
        Stops the continuous pings that are running on the mininet machines from CASE 5
        '''
        import time
        import os
        main.log.case( "Link down number of iterations: " +  main.params['Iterations'] )
        os.popen("echo "" > ~/tools/downtimes.log")
        for i in range(int(main.params['Iterations'])):
            main.log.info("Bringing Link down... ")
            main.ONOS1.link_down(SDPID=main.params['LINK1']['dpid1'],SPORT=main.params['LINK1']['port1'],DDPID=main.params['LINK1']['dpid2'],DPORT=main.params['LINK1']['port2'])
            os.popen("echo `date +%s` >> ~/tools/downtimes.log")
            main.log.info( "Waiting " + main.params['WaitTime'] + " seconds.... " )
            time.sleep( int(main.params['WaitTime']) )
            #main.log.info("Checking...")
            #t1 = time.time()
            #for i in range(15):
            #    result = main.ONOS1.check_flow()
            #    if result == main.TRUE:
            #        t2 = time.time()
            #        main.log.info( 'Adding flows took %0.3f ms' % ((t2-t1)*1000.0))
            #        break
            #time.sleep(2)
            #main.log.info("Checking Flows again...")
            main.log.info("Bringing Link up... ")
            main.ONOS1.link_up(SDPID=main.params['LINK1']['dpid1'],SPORT=main.params['LINK1']['port1'],DDPID=main.params['LINK1']['dpid2'],DPORT=main.params['LINK1']['port2'])
            main.log.info( "Waiting " + main.params['WaitTime'] + " seconds.... " )
            time.sleep( int(main.params['WaitTime']) )
        main.case("Killing remote ping processes ") 
        result = main.Mininet4.pingKill() 
        utilities.assert_equals(expect=main.TRUE,actual=result) 
       

    def CASE7(self,main) :
        '''
        Processes all of the ping data and outputs raw data and an overall average
        '''
        import os
        import time
        main.case("Processing Ping data") 
        time.sleep(3) 
        result=os.popen("~/tools/shell.sh " + main.params['Iterations']).read()
        average=result.split(":")[1] 
        main.log.info( "Reroute times are... " ) 
        main.log.report( result ) 
        try:
            if float(average) < float(main.params['TargetTime']) :
                test=main.TRUE
            else:
                test=main.FALSE
        except ValueError: 
            main.log.error("Data is corrupted")
            test=main.FALSE
        utilities.assert_equals(expect=main.TRUE,actual=test,onpass="Average is less then the target time!",onfail="Average is worse then target time... ")
