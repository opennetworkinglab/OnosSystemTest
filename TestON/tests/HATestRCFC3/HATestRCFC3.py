'''
Description: This case is to ensure that in the event of Zookeeper failures (including the leader node)
the cluster should continue to function properly by the passing of Zookeeper functionality to the 
remaining nodes. In this test, a quorum of the Zookeeper instances must be kept alive.

'''
class HATestRCFC3:


    def __init__(self) :
        self.default = ''

    '''
    CASE1 is to close any existing instances of ONOS, clean out the 
    RAMCloud database, and start up ONOS instances. 
    '''
    def CASE1(self,main) :
        main.log.report("ONOS instance network failure scenario test initialization")
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

        main.step("Start Packet Captures")
        main.Mininet2.start_tcpdump(str(main.params['MNtcpdump']['folder'])+str(main.TEST)+"-MN.pcap", 
                intf = main.params['MNtcpdump']['intf'],
                port = main.params['MNtcpdump']['port']) 
        main.ONOS1.tcpdump()
        main.ONOS2.tcpdump()
        main.ONOS3.tcpdump()
        main.ONOS4.tcpdump()
        main.ONOS5.tcpdump()

        result = main.ONOS1.status() or main.ONOS2.status() \
                or main.ONOS3.status() or main.ONOS4.status() or main.ONOS5.status()
        '''
        main.step("Startup Zookeeper")
        main.ZK1.start()
        main.ZK2.start()
        main.ZK3.start()
        main.ZK4.start()
        main.ZK5.start()
        result_zk = main.ZK1.isup() and main.ZK2.isup()\
                and main.ZK3.isup() and main.ZK4.isup() and main.ZK5.isup()
        utilities.assert_equals(expect=main.TRUE,actual=result_zk,
                onpass="Zookeeper started successfully",
                onfail="Zookeeper failed to start")
        main.step("Cleaning RC Database")
        main.RC1.del_db()
        main.RC2.del_db()
        main.RC3.del_db()
        main.RC4.del_db()
        main.RC5.del_db()
        '''
        main.step("Starting All")
        main.ONOS1.start_all()
        main.ONOS2.start_all()
        main.ONOS3.start_all()
        main.ONOS4.start_all()
        main.ONOS5.start_all()
        main.ONOS1.start_rest()
        main.step("Testing Startup")
        '''
        result1 = main.ONOS1.rest_status() and result_zk
        vm1 = main.RC1.status_coor and main.RC1.status_serv and \
                main.ONOS1.isup()
        vm2 = main.RC2.status_coor and main.ONOS2.isup()
        vm3 = main.RC3.status_coor and main.ONOS3.isup()
        vm4 = main.RC4.status_coor and main.ONOS4.isup()
        vm5 = main.RC5.status_coor and main.ONOS5.isup()
        result = result1 and vm1 and vm2 and vm3 and vm4 and vm5
        '''
        result = main.ONOS1.isup() and main.ONOS2.isup() and \
                main.ONOS3.isup() and main.ONOS4.isup() and \
                main.ONOS5.isup() 
        if result == main.TRUE: 
            main.log.report("All components started successfully")
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
        main.log.report("Assigning Controllers")
        main.case("Assigning Controllers")
        main.step("Assign Master Controllers")
        for i in range(1,29):
            if i ==1:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
            elif i>=2 and i<5:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=main.params['CTRL']['ip2'],port1=main.params['CTRL']['port2'])
            elif i>=5 and i<8:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=main.params['CTRL']['ip3'],port1=main.params['CTRL']['port3'])
            elif i>=8 and i<18:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=main.params['CTRL']['ip4'],port1=main.params['CTRL']['port4'])
            elif i>=18 and i<28:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=main.params['CTRL']['ip5'],port1=main.params['CTRL']['port5'])
            else:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
        
        result = main.TRUE
        for i in range (1,29):
            if i==1:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is " + str(response))
                if re.search("tcp:"+main.params['CTRL']['ip1'],response):
                    result = result and main.TRUE
                else:
                    result = main.FALSE
            elif i>=2 and i<5:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is " + str(response))
                if re.search("tcp:"+main.params['CTRL']['ip2'],response):
                    result = result and main.TRUE
                else:
                    result = main.FALSE
            elif i>=5 and i<8:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is " + str(response))
                if re.search("tcp:"+main.params['CTRL']['ip3'],response):
                    result = result and main.TRUE
                else:
                    result = main.FALSE
            elif i>=8 and i<18:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is " + str(response))
                if re.search("tcp:"+main.params['CTRL']['ip4'],response):
                    result = result and main.TRUE
                else:
                    result = main.FALSE
            elif i>=18 and i<28:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is " + str(response))
                if re.search("tcp:"+main.params['CTRL']['ip5'],response):
                    result = result and main.TRUE
                else:
                    result = main.FALSE
            else:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is" + str(response))
                if re.search("tcp:" +main.params['CTRL']['ip1'],response):
                    result = result and main.TRUE
                else:
                    result = main.FALSE

        utilities.assert_equals(expect = main.TRUE,actual=result,onpass="MasterControllers assigned correctly")
        for i in range (1,29):
            main.Mininet1.assign_sw_controller(sw=str(i),count=5,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'],ip5=main.params['CTRL']['ip5'],port5=main.params['CTRL']['port5']) 

    def CASE3(self,main) :
        import time
        import json
        import re
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
            main.ONOS1.add_intent(intent_id=str(count),src_dpid=srcDPID,dst_dpid=dstDPID,src_mac=srcMac,dst_mac=dstMac,intentIP=intentIP,intentPort=intentPort,intentURL=intentURL)
            count+=1
            dstDPID = '00:00:00:00:00:00:30:'+str(i).zfill(2)
            srcDPID= '00:00:00:00:00:00:60:' +str(i+10)
            dstMac = '00:00:00:00:00:' + str(hex(i)[2:]).zfill(2)
            srcMac = '00:00:00:00:00:'+str(hex(i+10)[2:])
            main.ONOS1.add_intent(intent_id=str(count),src_dpid=srcDPID,dst_dpid=dstDPID,src_mac=srcMac,dst_mac=dstMac,intentIP=intentIP,intentPort=intentPort,intentURL=intentURL)
            count+=1
        count = 1
        i = 8
        result = main.TRUE
        while i <18 :
            main.log.info("\n\nh"+str(i)+" is Pinging h" + str(i+10))
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+10))
            if ping ==main.FALSE and count <9:
                count+=1
                i = 8
                result = main.FALSE
                main.log.report("Ping between h" + str(i) + " and h" + str(i+10) + " failed. Making attempt number "+str(count) + " in 2 seconds")
                time.sleep(2)
            elif ping==main.FALSE:
                main.log.info("PINGS FAILED! MAX RETRIES REACHED!")
                i=19
                result = main.FALSE
            elif ping==main.TRUE:
                main.log.info("Ping passed!")
                i+=1
                result = main.TRUE
            else:
                main.log.info("ERROR!!")
                result = main.ERROR
        if result==main.FALSE:
            main.log.info("INTENTS HAVE NOT BEEN INSTALLED CORRECTLY!! EXITING!!!")
            main.cleanup()
            main.exit()
        if Ping_Result==main.TRUE:
            main.log.report("Intents have been instaled correctly")
        utilities.assert_equals(expect = main.TRUE,actual=Switch_Mastership,
                onpass="Intents have been instaled correctly")
        

    def CASE4(self,main) :
        import time
        from subprocess import Popen, PIPE
        from sts.topology.teston_topology import TestONTopology # assumes that sts is already in you PYTHONPATH
        main.case("Setting up and Gathering data for current state")

        main.step("Get the Mastership of each switch")
        (stdout,stderr)=Popen(["curl",main.params['CTRL']['ip1']+":"+main.params['CTRL']['restPort1']+main.params['CTRL']['switchURL']],stdout=PIPE).communicate()
        global masterSwitchList1
        masterSwitchList1 = stdout

        main.step("Get the High Level Intents")
        (stdout,stderr)=Popen(["curl",main.params['CTRL']['ip1']+":"+main.params['CTRL']['restPort1']+main.params['CTRL']['intentHighURL']],stdout=PIPE).communicate()
        global highIntentList1
        highIntentList1 = stdout
        
        main.step("Get the Low level Intents")
        (stdout,stderr)=Popen(["curl",main.params['CTRL']['ip1']+":"+main.params['CTRL']['restPort1']+main.params['CTRL']['intentLowURL']],stdout=PIPE).communicate()
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
        MNTopo = TestONTopology(main.Mininet1, ctrls) # can also add Intent API info for intent operations

        main.step("Compare ONOS Topology to MN Topology")
        for n in range(1,6):
            result = main.Mininet1.compare_topo(MNTopo, main.ONOS1.get_json(main.params['CTRL']['ip'+str(n)]+":"+main.params['CTRL']['restPort'+str(n)]+main.params['TopoRest']))
            utilities.assert_equals(expect=main.TRUE,actual=result,onpass="ONOS" + str(n) + " Topology matches MN Topology",onfail="ONOS" + str(n) + " Topology does not match MN Topology")


    def CASE5(self,main) :
        import re
        import random
        main.case("MAIN COMPONENT FAILURE AND SCENARIO SPECIFIC TESTS")
        main.step("RAMCloud-ONOS Communication Failure!")
        main.log.info("Blocking incoming traffic on udp port 12242 on 2 instances...")
        global rand1
        global rand2
        rand1 = random.randint(1,5)
        rand2 = random.randint(1,5)
        
        
        while rand1 == rand2:
            rand2 = random.randint(1,5)
        
        ip2=main.params['CTRL']['ip2']
        ip3=main.params['CTRL']['ip3']
        ip4=main.params['CTRL']['ip4']
        ip5=main.params['CTRL']['ip5']
        ip1=main.params['CTRL']['ip1']

        if rand1 == 1 or rand2 == 1:
            main.ONOS1.setIpTables(ip1,12242, action='add', packet_type='udp', direction='INPUT', rule='DROP')
        if rand1 == 2 or rand2 == 2:
            main.ONOS2.setIpTables(ip2, 12242, action='add', packet_type='udp', direction='INPUT', rule='DROP')
        if rand1 == 3 or rand2 == 3:
            main.ONOS3.setIpTables(ip3, 12242, action='add', packet_type='udp', direction='INPUT', rule='DROP')
        if rand1 == 4 or rand2 == 4:
            main.ONOS4.setIpTables(ip4, 12242, action='add', packet_type='udp', direction='INPUT', rule='DROP')
        if rand1 == 5 or rand2 == 5:
            main.ONOS5.setIpTables(ip5, 12242, action='add', packet_type='udp', direction='INPUT', rule='DROP')
        



    def CASE6(self,main) :
        import os
        main.case("Running ONOS Constant State Tests")
        main.step("Get the current In-Memory Topology on each ONOS Instance and Compare it to the Topology before component failure")

        #NOTE: Possible behavior for this case is for switches to change mastership to another 
        #      controller if the current controller's zk client loses connection with the ZK controller
        #      OR, Mastership shouldn't change. Investigation is needed

        main.step("Get the Mastership of each switch and compare to the Mastership before component failure")
        (stdout,stderr)=Popen(["curl",main.params['CTRL']['ip1']+":"+main.params['CTRL']['restPort1']+main.params['CTRL']['switchURL']],stdout=PIPE).communicate()
        result = main.TRUE
        for i in range(1,29):
            switchDPID = str(main.Mininet1.getSwitchDPID(switch="s"+str(i)))
            switchDPID = switchDPID[:2]+":"+switchDPID[2:4]+":"+switchDPID[4:6]+":"+switchDPID[6:8]+":"+switchDPID[8:10]+":"+switchDPID[10:12]+":"+switchDPID[12:14]+":"+switchDPID[14:]
            master1 = main.ZK1.findMaster(switchDPID=switchDPID,switchList=masterSwitchList1)
            master2 = main.ZK1.findMaster(switchDPID=switchDPID,switchList=stdout)
            if master1 == master2:
            #if main.ZK1.findMaster(switchDPID=switchDPID,switchList=masterSwitchList1)==main.ZK1.findMaster(switchDPID=switchDPID,switchList=stdout):
                result = result and main.TRUE
            else:
                result = main.FALSE
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Mastership of Switches was not changed",onfail="MASTERSHIP OF SWITCHES HAS CHANGED!!!")
        result1 = result

        main.step("Get the High Level Intents and compare to before component failure")
        (stdout,stderr)=Popen(["curl",main.params['CTRL']['ip1']+":"+main.params['CTRL']['restPort1']+main.params['CTRL']['intentHighURL']],stdout=PIPE).communicate()
        changesInIntents=main.ONOS1.comp_intents(preIntents=highIntentList1,postIntents=stdout)
        if not changesInIntents:
            result = main.TRUE
        else:
            main.log.info("THERE WERE CHANGES TO THE HIGH LEVEL INTENTS! CHANGES WERE: "+str(changesInIntents))
            result = main.FALSE
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="No changes to High level Intents",onfail="CHANGES WERE MADE TO HIGH LEVEL INTENTS")
        result2=result

        main.step("Get the Low level Intents and compare to before component failure")
        (stdout,stderr)=Popen(["curl",main.params['CTRL']['ip1']+":"+main.params['CTRL']['restPort1']+main.params['CTRL']['intentLowURL']],stdout=PIPE).communicate()
        changesInIntents=main.ONOS1.comp_low(preIntents=lowIntentList1,postIntents=stdout)
        if not changesInIntents:
            result = main.TRUE
        else:
            main.log.info("THERE WERE CHANGES TO THE LOW LEVEL INTENTS! CHANGES WERE: "+str(changesInIntents))
            result = main.FALSE
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="No changes to Low level Intents",onfail="CHANGES WERE MADE TO LOW LEVEL INTENTS")
        result3=result


        main.step("Get the OF Table entries and compare to before component failure")
        result = main.TRUE
        flows2=[]
        for i in range(27):
            flows2.append(main.Mininet2.get_flowTable(sw="s"+str(i+1)))
            main.log.info("Checking flow table on s" + str(i+1))
            result = result and main.Mininet2.flow_comp(flow1=flows[i], flow2=main.Mininet2.get_flowTable(sw="s"+str(i+1)))
            if result == main.FALSE:
                main.log.info("DIFFERENCES IN FLOW TABLES FOR SWITCH "+str(i))
                break
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="No changes in the flow tables",onfail="CHANGES IN THE FLOW TABLES!!")
        result4 = result
        
        main.step("Check the continuous pings to ensure that no packets were dropped during component failure")
        main.Mininet2.pingKill(main.params['TESTONUSER'], main.params['TESTONIP'])
        result = main.FALSE
        for i in range(8,18):
            result = result or main.Mininet2.checkForLoss("/tmp/ping.h"+str(i))
        if result==main.TRUE:
            main.log.info("LOSS IN THE PINGS!")
        elif result == main.ERROR:
            main.log.info("There are multiple mininet process running!!")
        else:
            main.log.info("No Loss in the pings!")
        utilities.assert_equals(expect=main.FALSE,actual=result,onpass="No Loss of connectivity!",onfail="LOSS OF CONNECTIVITY")
        result5=not result

        main.step("Check that ONOS Topology is consistent with MN Topology")
        MNTopo = TestONTopology(main.Mininet1, ctrls) # can also add Intent API info for intent operations
        result6 = main.TRUE
        for n in range(1,6):
            result = main.Mininet1.compare_topo(MNTopo, main.ONOS1.get_json(main.params['CTRL']['ip'+str(n)]+":"+main.params['CTRL']['restPort'+str(n)]+main.params['TopoRest']))
            utilities.assert_equals(expect=main.TRUE,actual=result,onpass="ONOS" + str(n) + " Topology matches MN Topology",onfail="ONOS" + str(n) + " Topology does not match MN Topology")
            result6 = result6 and result


        result = result1 and result2 and result3 and result4 and result5 and result6
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Constant State Tests Passed!",onfail="CONSTANT STATE TESTS FAILED!!")

    def CASE7 (self,main):
        main.case("Killing a link to Ensure that Link Discovery is Working Properly")

        main.step("Determine the current number of switches and links")
        (number,active)=main.ONOS1.num_switch(RestIP=main.params['CTRL']['ip1'])
        links = main.ONOS1.num_link(RestIP=main.params['CTRL']['ip1'])
        main.log.info("Currently there are %s switches %s of which are active, and %s links" %(number,active,links))
        
        main.step("Kill Link between s3 and s28")
        main.Mininet1.link(END1="s3",END2="s28",OPTION="down")
        result = main.ONOS1.check_status(main.params['CTRL']['ip1'],active,str(int(links)-2))
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
        main.case("Killing a switch to ensure switch discovery is working properly")

        main.step("Determine the current number of switches and links")
        (number,active)=main.ONOS1.num_switch(RestIP=main.params['CTRL']['ip1'])
        links = main.ONOS1.num_link(RestIP=main.params['CTRL']['ip1'])
        main.log.info("Currently there are %s switches %s of which are active, and %s links" %(number,active,links))
        
        main.step("Kill s28 ")
        main.Mininet2.del_switch("s28")
        time.sleep(45)
        result = main.ONOS1.check_status(main.params['CTRL']['ip1'],str(int(active)-1),str(int(links)-4))
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
        time.sleep(45)
        result = main.ONOS1.check_status(main.params['CTRL']['ip1'],active,links)
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Switch Discovery is Working",onfail="Switch Discovery FAILED TO WORK PROPERLY!")
        result3=result


        #NOTE: Compare Topo does not currently work for this case
        #main.step("Compare ONOS Topology to MN Topology")
        #Topo = TestONTopology(main.Mininet1, ctrls) # can also add Intent API info for intent operations
        #MNTopo = Topo
        #result5 = main.TRUE
        #for n in range(1,6):
        #    if n == kill or n == kill2: 
        #        pass
        #    else: 
        #        Topology_Current = main.Mininet1.compare_topo(MNTopo, 
        #                main.ONOS1.get_json(main.params['CTRL']['ip'+str(n)]+":"+\
        #                main.params['CTRL']['restPort'+str(n)]+main.params['TopoRest']))
        #        if Topology_Current == main.TRUE:
        #            main.log.report("ONOS"+str(n)+" Topolgoy matches MN Topology")
        #        utilities.assert_equals(expect=main.TRUE,actual=Topology_Current,
        #                onpass="ONOS" + str(n) + " Topology matches MN Topology",
        #                onfail="ONOS" + str(n) + " Topology does not match MN Topology")
        #        Topology_Check2 = Topology_Check2 and Topology_Current

        #NOTE: Commenting out this result since currently compare_topo doesn't work when we remove a
        #      switch since we don't update the MN data structures
        result = Del_Switch_Discovered and Add_Switch_Discovered #and Topology_Check and Topology_Check2
        if result == main.TRUE:
            main.log.report("Switch event discovered correctly")
        utilities.assert_equals(expect=main.TRUE,actual=result,
                onpass="Switch Discovered Correctly",
                onfail="Switch discovery failed")
        main.log.info("Removing existing Iptable rules...") 
        ip2=main.params['CTRL']['ip2']
        ip3=main.params['CTRL']['ip3']
        ip4=main.params['CTRL']['ip4']
        ip5=main.params['CTRL']['ip5']
        ip1=main.params['CTRL']['ip1']

        if rand1 == 1 or rand2 == 1:
            main.ONOS1.setIpTables(ip1,12242, action='remove', packet_type='udp', direction='INPUT', rule='DROP')
        if rand1 == 2 or rand2 == 2:
            main.ONOS2.setIpTables(ip2, 12242, action='remove', packet_type='udp', direction='INPUT', rule='DROP')
        if rand1 == 3 or rand2 == 3:
            main.ONOS3.setIpTables(ip3, 12242, action='remove', packet_type='udp', direction='INPUT', rule='DROP')
        if rand1 == 4 or rand2 == 4:
            main.ONOS4.setIpTables(ip4, 12242, action='remove', packet_type='udp', direction='INPUT', rule='DROP')
        if rand1 == 5 or rand2 == 5:
            main.ONOS5.setIpTables(ip5, 12242, action='remove', packet_type='udp', direction='INPUT', rule='DROP')
        
        
# Authored by James Lee
# Just wanted to see how many people were paying attention here.
# Elayne Boosler once said "I have six locks on my door all in a row
# When I go out, I lock every other one. I figure no matter how long 
# somebody stands there picking the locks, they are always locking three"



        main.log.step("Killing tcpdumps")
        main.Mininet2.stop_tcpdump()
        main.ONOS1.kill_tcpdump()
        main.ONOS2.kill_tcpdump()
        main.ONOS3.kill_tcpdump()
        main.ONOS4.kill_tcpdump()
        main.ONOS5.kill_tcpdump()

        main.log.step("Copying pcap files to test station")
        dumpDir = main.params['ONOStcpdump']['dumpDir']
        scpDir = main.params['ONOStcpdump']['scpDir']
        testname = main.TEST 
        teststation_user = main.params['TESTONUSER']
        teststation_IP = main.params['TESTONIP']

        main.ONOS1.handle.sendline("scp "+dumpDir+"/tcpdump " +teststation_user+ "@" +teststation_IP+ ":" +scpDir + "/" + testname + "-" +main.ONOS1.name + ".pcap")
        main.ONOS2.handle.sendline("scp "+dumpDir+"/tcpdump " +teststation_user+ "@" +teststation_IP+ ":" +scpDir + "/" + testname + "-" +main.ONOS2.name + ".pcap")
        main.ONOS3.handle.sendline("scp "+dumpDir+"/tcpdump " +teststation_user+ "@" +teststation_IP+ ":" +scpDir + "/" + testname + "-" +main.ONOS3.name + ".pcap")
        main.ONOS4.handle.sendline("scp "+dumpDir+"/tcpdump " +teststation_user+ "@" +teststation_IP+ ":" +scpDir + "/" + testname + "-" +main.ONOS4.name + ".pcap")
        main.ONOS5.handle.sendline("scp "+dumpDir+"/tcpdump " +teststation_user+ "@" +teststation_IP+ ":" +scpDir + "/" + testname + "-" +main.ONOS5.name + ".pcap")
        #sleep so scp can finish
        time.sleep(10)
        
        main.log.step("Packing and rotating pcap archives")
        import os
        print os.system("~/TestON/dependencies/rotate.sh "+ str(testname))
