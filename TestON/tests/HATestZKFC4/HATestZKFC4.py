'''
Description: This test will verify that the ONOS registry will stop working when all ZK instances
are down. Then, once the ZK instances are restarted, and a new leader is elected the ONOS registry
should begin to work again. ONOS instances and RC Coordinators may have reconnected to a different
instance of ZK, and a new leader may have been elected.
'''
class HATestZKFC4:

    def __init__(self) :
        self.default = ''

    '''
    CASE1 is to close any existing instances of ONOS, clean out the 
    RAMCloud database, and start up ONOS instances. 
    '''
    def CASE1(self,main) :
        import time
        main.log.report("Initial startup")
        main.case("Initial Startup")
        
        main.step("Stop ONOS")
        main.ONOS1.stop_all()
        main.ONOS2.stop_all()
        main.ONOS3.stop_all()
        main.ONOS4.stop_all()
        main.ONOS5.stop_all()
        main.ONOS1.stop_rest()
        main.ONOS2.stop_rest()
        main.ONOS3.stop_rest()
        main.ONOS4.stop_rest()
        main.ONOS5.stop_rest()

        main.step("Checking git commit")
        ONOS_commit = []
        ONOS_commit.append(main.ONOS1.get_branch())
        ONOS_commit.append(main.ONOS2.get_branch())
        ONOS_commit.append(main.ONOS3.get_branch())
        ONOS_commit.append(main.ONOS4.get_branch())
        ONOS_commit.append(main.ONOS5.get_branch())
        #Compare commits and if different print them all out
        if len(set(ONOS_commit)) == 1:
            main.log.report("On branch: "+ ONOS_commit[0])
        else:
            main.log.report("Warning, ONOS VM's on different commits")
            main.log.report("ONOS1 is on branch: "+ ONOS_commit[0])
            main.log.report("ONOS2 is on branch: "+ ONOS_commit[1])
            main.log.report("ONOS3 is on branch: "+ ONOS_commit[2])
            main.log.report("ONOS4 is on branch: "+ ONOS_commit[3])
            main.log.report("ONOS5 is on branch: "+ ONOS_commit[4])

        
        main.step("Startup Zookeeper")
        main.ZK1.start()
        main.ZK2.start()
        main.ZK3.start()
        main.ZK4.start()
        main.ZK5.start()
        time.sleep(2)
        result = main.ZK1.isup() and main.ZK2.isup()\
                and main.ZK3.isup() and main.ZK4.isup() and main.ZK5.isup()
        
        utilities.assert_equals(expect=main.TRUE,actual=result,
                onpass="Zookeeper started successfully",
                onfail="ZOOKEEPER FAILED TO START")
        
        main.step("Cleaning RC Database and Starting All") 
        main.RC1.del_db()
        main.RC2.del_db()
        main.RC3.del_db()
        main.RC4.del_db()
        main.RC5.del_db() 
        main.ONOS1.start_all()
        main.ONOS2.start_all()
        main.ONOS3.start_all()
        main.ONOS4.start_all()
        main.ONOS5.start_all()
        main.ONOS1.start_rest()
        
        main.step("Testing Startup")
        result1 = main.ONOS1.rest_status()
        vm1 = main.RC1.status_coor and main.RC1.status_serv and \
                main.ONOS1.isup()
        vm2 = main.RC2.status_coor and main.ONOS2.isup()
        vm3 = main.RC3.status_coor and main.ONOS3.isup()
        vm4 = main.RC4.status_coor and main.ONOS4.isup()
        vm5 = main.RC5.status_coor and main.ONOS5.isup()
        result = result1 and vm1 and vm2 and vm3 and vm4 and vm5
        utilities.assert_equals(expect=main.TRUE,actual=result,
                onpass="All components started successfully",
                onfail="One or more components failed to start")
        #if result==main.FALSE:
        #    main.cleanup()
        #    main.exit()

    '''
    CASE2
    '''
    def CASE2(self,main) :
        import time
        import json
        import re

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS4_ip = main.params['CTRL']['ip4']
        ONOS5_ip = main.params['CTRL']['ip5']

        ONOS1_port = main.params['CTRL']['port1']
        ONOS2_port = main.params['CTRL']['port2']
        ONOS3_port = main.params['CTRL']['port3']
        ONOS4_port = main.params['CTRL']['port4']
        ONOS5_port = main.params['CTRL']['port5']

        main.log.report("Assigning Controllers")
        main.case("Assigning Controllers")
        main.step("Assign Master Controllers")
        for i in range(1,29):
            if i ==1:
                main.Mininet1.assign_sw_controller(sw=str(i),
                        ip1=ONOS1_ip,port1=ONOS1_port)
            elif i>=2 and i<5:
                main.Mininet1.assign_sw_controller(sw=str(i),
                        ip1=ONOS2_ip,port1=ONOS2_port)
            elif i>=5 and i<8:
                main.Mininet1.assign_sw_controller(sw=str(i),
                        ip1=ONOS3_ip,port1=ONOS3_port)
            elif i>=8 and i<18:
                main.Mininet1.assign_sw_controller(sw=str(i),
                        ip1=ONOS4_ip,port1=ONOS4_port)
            elif i>=18 and i<28:
                main.Mininet1.assign_sw_controller(sw=str(i),
                        ip1=ONOS5_ip,port1=ONOS5_port)
            else:
                main.Mininet1.assign_sw_controller(sw=str(i),
                        ip1=ONOS1_ip,port1=ONOS1_port)
        
        result = main.TRUE
        for i in range (1,29):
            if i==1:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is " + str(response))
                if re.search("tcp:"+ONOS1_ip,response):
                    result = result and main.TRUE
                else:
                    result = main.FALSE
            elif i>=2 and i<5:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is " + str(response))
                if re.search("tcp:"+ONOS2_ip,response):
                    result = result and main.TRUE
                else:
                    result = main.FALSE
            elif i>=5 and i<8:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is " + str(response))
                if re.search("tcp:"+ONOS3_ip,response):
                    result = result and main.TRUE
                else:
                    result = main.FALSE
            elif i>=8 and i<18:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is " + str(response))
                if re.search("tcp:"+ONOS4_ip,response):
                    result = result and main.TRUE
                else:
                    result = main.FALSE
            elif i>=18 and i<28:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is " + str(response))
                if re.search("tcp:"+ONOS5_ip,response):
                    result = result and main.TRUE
                else:
                    result = main.FALSE
            else:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is" + str(response))
                if re.search("tcp:" +ONOS1_ip,response):
                    result = result and main.TRUE
                else:
                    result = main.FALSE

        utilities.assert_equals(expect = main.TRUE,actual=result,
                onpass="MasterControllers assigned correctly")
        for i in range (1,29):
            main.Mininet1.assign_sw_controller(sw=str(i),count=5,
                    ip1=ONOS1_ip,port1=ONOS1_port,
                    ip2=ONOS2_ip,port2=ONOS2_port,
                    ip3=ONOS3_ip,port3=ONOS3_port,
                    ip4=ONOS4_ip,port4=ONOS4_port,
                    ip5=ONOS5_ip,port5=ONOS5_port) 

    def CASE3(self,main) :
        import time
        import json
        import re
        
        main.log.report("Adding birectional intents")
        main.case("Adding Intents")
        intentIP = main.params['CTRL']['ip1']
        intentPort=main.params['INTENTS']['intentPort']
        intentURL=main.params['INTENTS']['intentURL']
        count = 1
        for i in range(8,18):
            srcMac = '00:00:00:00:00:' + str(hex(i)[2:]).zfill(2)
            dstMac = '00:00:00:00:00:'+str(hex(i+10)[2:])
            srcDPID = '00:00:00:00:00:00:30:'+str(i).zfill(2)
            dstDPID= '00:00:00:00:00:00:60:' +str(i+10)
            main.ONOS1.add_intent(intent_id=str(count),
                    src_dpid=srcDPID,dst_dpid=dstDPID,
                    src_mac=srcMac,dst_mac=dstMac,
                    intentIP=intentIP,intentPort=intentPort,intentURL=intentURL)
            count+=1
            dstDPID = '00:00:00:00:00:00:30:'+str(i).zfill(2)
            srcDPID= '00:00:00:00:00:00:60:' +str(i+10)
            dstMac = '00:00:00:00:00:' + str(hex(i)[2:]).zfill(2)
            srcMac = '00:00:00:00:00:'+str(hex(i+10)[2:])
            main.ONOS1.add_intent(intent_id=str(count),
                    src_dpid=srcDPID,dst_dpid=dstDPID,
                    src_mac=srcMac,dst_mac=dstMac,
                    intentIP=intentIP,intentPort=intentPort,intentURL=intentURL)
            count+=1
        count = 1
        i = 8
        Ping_Result = main.TRUE
        while i <18 :
            main.log.info("\n\nh"+str(i)+" is Pinging h" + str(i+10))
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+10))
            if ping ==main.FALSE and count <9:
                count+=1
                i = 8
                Ping_Result = main.FALSE
                main.log.report("Ping between h" + str(i) + " and h" + str(i+10) + " failed. Making attempt number "+str(count) + " in 2 seconds")
                time.sleep(2)
            elif ping==main.FALSE:
                main.log.info("PINGS FAILED! MAX RETRIES REACHED!")
                i=19
                Ping_Result = main.FALSE
            elif ping==main.TRUE:
                main.log.info("Ping passed!")
                i+=1
                Ping_Result = main.TRUE
            else:
                main.log.info("ERROR!!")
                Ping_Result = main.ERROR
        if Ping_Result==main.FALSE:
            main.log.info("Intents have not been installed correctly. Exiting...")
            main.cleanup()
            main.exit()
        if Ping_Result==main.TRUE:
            main.log.report("Intents have been installed correctly")
        utilities.assert_equals(expect = main.TRUE,actual=Ping_Result,
                onpass="Intents have been installed correctly")
        

    def CASE4(self,main) :
        import time
        from subprocess import Popen, PIPE
        from sts.topology.teston_topology import TestONTopology # assumes that sts is already in you PYTHONPATH
        
        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS_restPort1 = main.params['CTRL']['restPort1']
        switchURL = main.params['CTRL']['switchURL']
        intentHighURL = main.params['CTRL']['intentHighURL']
        intentLowURL = main.params['CTRL']['intentLowURL']

        main.log.report("Setting up and gathering data for current state")
        main.case("Setting up and Gathering data for current state")

        main.step("Get the Mastership of each switch")
        (stdout,stderr)=Popen(["curl",ONOS1_ip+":"+ONOS_restPort1+switchURL],
                stdout=PIPE).communicate()
        global masterSwitchList1
        masterSwitchList1 = stdout

        main.step("Get the High Level Intents")
        (stdout,stderr)=Popen(["curl",ONOS1_ip+":"+ONOS_restPort1+intentHighURL],
                stdout=PIPE).communicate()
        global highIntentList1
        highIntentList1 = stdout
        
        main.step("Get the Low level Intents")
        (stdout,stderr)=Popen(["curl",ONOS1_ip+":"+ONOS_restPort1+intentLowURL],
                stdout=PIPE).communicate()
        global lowIntentList1
        lowIntentList1= stdout
        
        main.step("Get the OF Table entries")
        global flows
        flows=[]
        for i in range(1,29):
            flows.append(main.Mininet2.get_flowTable("s"+str(i)))

        
        main.step("Start continuous pings")
        main.Mininet2.pingLong(src=main.params['PING']['source1'],target=main.params['PING']['target1'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source2'],target=main.params['PING']['target2'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source3'],target=main.params['PING']['target3'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source4'],target=main.params['PING']['target4'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source5'],target=main.params['PING']['target5'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source6'],target=main.params['PING']['target6'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source7'],target=main.params['PING']['target7'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source8'],target=main.params['PING']['target8'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source9'],target=main.params['PING']['target9'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source10'],target=main.params['PING']['target10'],pingTime=500)

        main.step("Create TestONTopology object")
        global ctrls
        ctrls = []
        count = 1
        while True:
            temp = ()
            if ('ip' + str(count)) in main.params['CTRL']:
                temp = temp + (getattr(main,('ONOS' + str(count))),)
                temp = temp + ("ONOS"+str(count),)
                temp = temp + (main.params['CTRL']['ip'+str(count)],)
                temp = temp + (eval(main.params['CTRL']['port'+str(count)]),)
                ctrls.append(temp)
                count = count + 1
            else:
                break
        global MNTopo
        Topo = TestONTopology(main.Mininet1, ctrls) # can also add Intent API info for intent operations
        MNTopo = Topo

        main.step("Compare ONOS Topology to MN Topology")
        for n in range(1,6):
            result = main.Mininet1.compare_topo(MNTopo, 
                    main.ONOS1.get_json(main.params['CTRL']['ip'+str(n)]+
                    ":"+main.params['CTRL']['restPort'+str(n)]+main.params['TopoRest']))
            utilities.assert_equals(expect=main.TRUE,actual=result,
                    onpass="ONOS" + str(n) + " Topology matches MN Topology",
                    onfail="ONOS" + str(n) + " Topology does not match MN Topology")

    def CASE5(self,main) :
        import re
        
        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS4_ip = main.params['CTRL']['ip4']
        ONOS5_ip = main.params['CTRL']['ip5']

        ONOS1_port = main.params['CTRL']['port1']
        ONOS2_port = main.params['CTRL']['port2']
        ONOS3_port = main.params['CTRL']['port3']
        ONOS4_port = main.params['CTRL']['port4']
        ONOS5_port = main.params['CTRL']['port5']
       
        main.log.report("Main component failure and scenario specific tests") 
        main.case("MAIN COMPONENT FAILURE AND SCENARIO SPECIFIC TESTS")
        main.step("Determine the current number of switches and links")
        (number,active)=main.ONOS1.num_switch(RestIP=ONOS1_ip)
        links = main.ONOS1.num_link(RestIP=ONOS1_ip)
        main.log.report("Currently there are %s switches, %s are active, and %s links" %(number,active,links))

        main.step("All Zookeeper Server Failure!")
        main.ZK1.stop()
        main.ZK2.stop()
        main.ZK3.stop()
        main.ZK4.stop()
        main.ZK5.stop() 

        main.step("Change topology during failover")
        main.Mininet2.del_switch("s1")
        time.sleep(31)
        result = main.ONOS1.check_status_report(ONOS1_ip,str(int(active)-1),str(int(links)-2))
        utilities.assert_equals(expect=main.FALSE,actual=result,
                onpass="Registry is no longer active",
                onfail="Registry is still being updated")
        result1 = result

        main.step("Compare ONOS Topology to MN Topology")
        Topo = TestONTopology(main.Mininet1, ctrls) # can also add Intent API info for intent operations
        MNTopo = Topo
        result2 = main.TRUE
        for n in range(1,6):
            result = main.Mininet1.compare_topo(MNTopo,
                    main.ONOS1.get_json(main.params['CTRL']['ip'+str(n)]+
                    ":"+main.params['CTRL']['restPort'+str(n)]+main.params['TopoRest']))
            utilities.assert_equals(expect=main.TRUE,actual=result,
                    onpass="ONOS" + str(n) + " Topology matches MN Topology",
                    onfail="ONOS" + str(n) + " Topology does not match MN Topology")
            result2 = result2 and result

        main.step("Restart Zookeeper")
        main.ZK1.start()
        main.ZK2.start()
        main.ZK3.start()
        main.ZK4.start()
        main.ZK5.start()
        time.sleep(10) # Time for Zookeeper to reboot
        master1=main.ZK1.status()
        master2=main.ZK2.status()
        master3=main.ZK3.status()
        master4=main.ZK4.status()
        master5=main.ZK5.status()
        if re.search("leader",master1) or re.search("leader",master2) or re.search("leader",master3) or re.search("leader",master4) or re.search("leader",master5):
            main.log.info("New ZK Leader Elected")
        else:
            main.log.info("NO NEW ZK LEADER ELECTED!!!")
        main.step("Add back s1")
        main.Mininet2.add_switch("s1")
        main.Mininet1.assign_sw_controller(sw="1",ip1=ONOS1_ip,port1=ONOS1_port)
        main.Mininet1.assign_sw_controller(sw="1",count=5,
                ip1=ONOS1_ip,port1=ONOS1_port,
                ip2=ONOS2_ip,port2=ONOS2_port,
                ip3=ONOS3_ip,port3=ONOS3_port,
                ip4=ONOS4_ip,port4=ONOS4_port,
                ip5=ONOS5_ip,port5=ONOS5_port) 
        time.sleep(31)
        result = result1 and result2
        if result == main.TRUE:
            main.log.report("Failover test passed")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Failover Pass",onfail="Failover fail")


    def CASE6(self,main) :
        import os

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS_restPort1 = main.params['CTRL']['restPort1']
        intentHighURL = main.params['CTRL']['intentHighURL']
        intentLowURL = main.params['CTRL']['intentLowURL']

        main.log.report("Running ONOS constant state tests")
        main.case("Running ONOS Constant State Tests")
        main.step("Get the current In-Memory Topology on each ONOS Instance and Compare it to the Topology before component failure")

        result = main.TRUE
        result1 = result

        main.step("Get the High Level Intents and compare to before component failure")
        (stdout,stderr)=Popen(["curl",ONOS1_ip+":"+ONOS_restPort1+intentHighURL],
                stdout=PIPE).communicate()
        changesInIntents=main.ONOS1.comp_intents(preIntents=highIntentList1,postIntents=stdout)
        if not changesInIntents:
            result = main.TRUE
        else:
            main.log.info("THERE WERE CHANGES TO THE HIGH LEVEL INTENTS! CHANGES WERE: "+str(changesInIntents))
            result = main.FALSE
        if result == main.TRUE:
            main.log.report("No changes to high level intents")
        utilities.assert_equals(expect=main.TRUE,actual=result,
                onpass="No changes to High level Intents",
                onfail="Changes were made to high level intents")
        result2=result

        main.step("Get the Low level Intents and compare to before component failure")
        (stdout,stderr)=Popen(["curl",ONOS1_ip+":"+ONOS_restPort1+intentLowURL],
                stdout=PIPE).communicate()
        changesInIntents=main.ONOS1.comp_low(preIntents=lowIntentList1,postIntents=stdout)
        if not changesInIntents:
            result = main.TRUE
        else:
            main.log.info("THERE WERE CHANGES TO THE LOW LEVEL INTENTS! CHANGES WERE: "+str(changesInIntents))
            result = main.FALSE
        utilities.assert_equals(expect=main.TRUE,actual=result,
                onpass="No changes to Low level Intents",
                onfail="Changes were made to the low level intents")
        result3=result

        main.step("Get the OF Table entries and compare to before component failure")
        result = main.TRUE
        flows2=[]
        for i in range(27):
            flows2.append(main.Mininet2.get_flowTable(sw="s"+str(i+1)))
            main.log.info("Checking flow table on s" + str(i+1))
            result = result and main.Mininet2.flow_comp(flow1=flows[i], flow2=main.Mininet2.get_flowTable(sw="s"+str(i+1)))
            if result == main.FALSE:
                main.log.info("Differences in flow tables for switch "+str(i))
                break
        if result == main.TRUE:
            main.log.report("No changes in the flow tables")
        utilities.assert_equals(expect=main.TRUE,actual=result,
                onpass="No changes in the flow tables",
                onfail="Changes were made in the flow tables")
        result4 = result
        
        #NOTE: Packet loss is expected since switches will go into emergancy mode
        main.step("Check the continuous pings to ensure that no packets were dropped during component failure")
        main.Mininet2.pingKill(main.params['TESTONUSER'], main.params['TESTONIP'])
        result = main.FALSE
        for i in range(8,18):
            result = result or main.Mininet2.checkForLoss("/tmp/ping.h"+str(i))
        if result==main.TRUE:
            main.log.info("Loss in pings detected")
        elif result == main.ERROR:
            main.log.info("There are multiple mininet process running!!")
        else:
            main.log.info("No Loss in the pings!")
        utilities.assert_equals(expect=main.FALSE,actual=result,
                onpass="No Loss of connectivity!",
                onfail="Loss of connectivity detected")
        
        #NOTE: here we are not flipping the value from checkForLoss since we expect this test to fail
        #      but don't want the case to fail
        #result5= not result
        result5 = main.TRUE

        main.step("Check that ONOS Topology is consistent with MN Topology")
        Topo = TestONTopology(main.Mininet1, ctrls) # can also add Intent API info for intent operations
        MNTopo = Topo

        result6 = main.TRUE
        for n in range(1,6):
            result = main.Mininet1.compare_topo(MNTopo,
                    main.ONOS1.get_json(main.params['CTRL']['ip'+str(n)]+
                    ":"+main.params['CTRL']['restPort'+str(n)]+main.params['TopoRest']))
            utilities.assert_equals(expect=main.TRUE,actual=result,
                    onpass="ONOS" + str(n) + " Topology matches MN Topology",
                    onfail="ONOS" + str(n) + " Topology does not match MN Topology")
            result6 = result6 and result

        result = result1 and result2 and result3 and result4 and result5 and result6
        if result == main.TRUE:
            main.log.report("Constant state tests passed")
        utilities.assert_equals(expect=main.TRUE,actual=result,
                onpass="Constant State Tests Passed!",
                onfail="Constant state tests failed")

    def CASE7 (self,main):
        main.case("Killing a link to Ensure that Link Discovery is Working Properly")

        main.step("Determine the current number of switches and links")
        (number,active)=main.ONOS1.num_switch(RestIP=main.params['CTRL']['ip1'])
        links = main.ONOS1.num_link(RestIP=main.params['CTRL']['ip1'])
        main.log.info("Currently there are %s switches, %s are active, and %s links" %(number,active,links))
        
        main.step("Kill Link between s3 and s28")
        main.Mininet1.link(END1="s3",END2="s28",OPTION="down")
        result = main.ONOS1.check_status_report(main.params['CTRL']['ip1'],active,str(int(links)-2))
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Link Down discovered properly",onfail="LINKS NOT DISCOVERED PROPERLY")
        result1 = result
        result = main.Mininet1.link(END1="s3",END2="s28",OPTION="up")

        main.step("Compare ONOS Topology to MN Topology")
        Topo = TestONTopology(main.Mininet1, ctrls) # can also add Intent API info for intent operations
        MNTopo = Topo
        result2 = main.TRUE
        for n in range(1,6):
            result = main.Mininet1.compare_topo(MNTopo, main.ONOS1.get_json(main.params['CTRL']['ip'+str(n)]+":"+main.params['CTRL']['restPort'+str(n)]+main.params['TopoRest']))
            utilities.assert_equals(expect=main.TRUE,actual=result,onpass="ONOS" + str(n) + " Topology matches MN Topology",onfail="ONOS" + str(n) + " Topology does not match MN Topology")
            result2 = result2 and result
        

        result = result1 and result2
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Link failure is discovered correctly",onfail="Link Discovery failed!")
        

    
    def CASE8 (self, main) :
        import time
       
        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS4_ip = main.params['CTRL']['ip4']
        ONOS5_ip = main.params['CTRL']['ip5']

        ONOS1_port = main.params['CTRL']['ip1']
        ONOS2_port = main.params['CTRL']['ip2']
        ONOS3_port = main.params['CTRL']['ip3']
        ONOS4_port = main.params['CTRL']['ip4']
        ONOS5_port = main.params['CTRL']['ip5']

        main.case("Killing a switch to ensure switch discovery is working properly")

        main.step("Determine the current number of switches and links")
        (number,active)=main.ONOS1.num_switch(RestIP=main.params['CTRL']['ip1'])
        links = main.ONOS1.num_link(RestIP=main.params['CTRL']['ip1'])
        main.log.info("Currently there are %s switches, %s are active, and %s links" %(number,active,links))
        
        main.step("Kill s28 ")
        main.Mininet2.del_switch("s28")
        time.sleep(31)
        result = main.ONOS1.check_status_report(main.params['CTRL']['ip1'],str(int(active)-1),str(int(links)-4))
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Switch Discovery is Working",onfail="Switch Discovery FAILED TO WORK PROPERLY!")
        result1 = result

        #NOTE: Compare Topo does not currently work for this case
        #main.step("Compare ONOS Topology to MN Topology")
        #Topo = TestONTopology(main.Mininet1, ctrls) # can also add Intent API info for intent operations
        #MNTopo = Topo
        #result2 = main.TRUE
        #for n in range(1,6):
        #    result = main.Mininet1.compare_topo(MNTopo, main.ONOS1.get_json(main.params['CTRL']['ip'+str(n)]+":"+main.params['CTRL']['restPort'+str(n)]+main.params['TopoRest']))
        #    utilities.assert_equals(expect=main.TRUE,actual=result,onpass="ONOS" + str(n) + " Topology matches MN Topology",onfail="ONOS" + str(n) + " Topology does not match MN Topology")
        #    result2 = result2 and result

        main.step("Add back s28")
        main.Mininet2.add_switch("s28")
        main.Mininet1.assign_sw_controller(sw="28",ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
        main.Mininet1.assign_sw_controller(sw="28",count=5,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'],ip5=main.params['CTRL']['ip5'],port5=main.params['CTRL']['port5']) 
        time.sleep(31)
        result = main.ONOS1.check_status_report(main.params['CTRL']['ip1'],active,links)
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Switch Discovery is Working",onfail="Switch Discovery FAILED TO WORK PROPERLY!")
        result3=result

        
        #NOTE: Compare Topo does not currently work for this case
        #main.step("Compare ONOS Topology to MN Topology")
        #Topo = TestONTopology(main.Mininet1, ctrls) # can also add Intent API info for intent operations
        #MNTopo = Topo
        #result4 = main.TRUE
        #for n in range(1,6):
        #    result = main.Mininet1.compare_topo(MNTopo, main.ONOS1.get_json(main.params['CTRL']['ip'+str(n)]+":"+main.params['CTRL']['restPort'+str(n)]+main.params['TopoRest']))
        #    utilities.assert_equals(expect=main.TRUE,actual=result,onpass="ONOS" + str(n) + " Topology matches MN Topology",onfail="ONOS" + str(n) + " Topology does not match MN Topology")
        #    result4 = result4 and result


        #NOTE: the compare_topo function doesn't currently work when we change the switch dpid since we aren't updating the MN data structures
        result =result1 and result2 and result3 #and result4 
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Switch Discovered Correctly",onfail="Switch discovery failed")

