'''
This class tests inter-ONOS network down event (network partition)
ONOS network will be partitioned in the following fashion

(ONOS1, ONOS2) -x- (ONOS3, ONOS4, ONOS5)
The communication that is cut is only between the ONOS controllers.
Other components such as Ramcloud and zookeeper should remain linked.
For this reason, we will target and disable Hazelcast channel between
the two ONOS subclusters outlined above.
'''



class HANetFailONOS:

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
        result = main.ONOS1.status() or main.ONOS2.status() \
                or main.ONOS3.status() or main.ONOS4.status() or main.ONOS5.status()
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
        result1 = main.ONOS1.rest_status() and result_zk
        vm1 = main.RC1.status_coor and main.RC1.status_serv and \
                main.ONOS1.isup()
        vm2 = main.RC2.status_coor and main.ONOS2.isup()
        vm3 = main.RC3.status_coor and main.ONOS3.isup()
        vm4 = main.RC4.status_coor and main.ONOS4.isup()
        vm5 = main.RC5.status_coor and main.ONOS5.isup()
        result = result1 and vm1 and vm2 and vm3 and vm4 and vm5
        if result == main.TRUE: 
            main.log.report("All components started successfully")
        utilities.assert_equals(expect=main.TRUE,actual=result,
                onpass="All components started successfully",
                onfail="One or more components failed to start")
        #if result==main.FALSE:
        #    main.cleanup()
        #    main.exit()

    '''
    CASE2: Assign designated switches to controllers
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

        main.log.report("Assigning controllers")
        main.case("Assigning Controllers")
        main.step("Assign Master Controllers")
        for i in range(1,29):
            if i ==1:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=ONOS1_ip,port1=ONOS1_port)
            elif i>=2 and i<5:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=ONOS2_ip,port1=ONOS2_port)
            elif i>=5 and i<8:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=ONOS3_ip,port1=ONOS3_port)
            elif i>=8 and i<18:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=ONOS4_ip,port1=ONOS4_port)
            elif i>=18 and i<28:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=ONOS5_ip,port1=ONOS5_port)
            else:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=ONOS1_ip,port1=ONOS1_port)
        
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
        if result == main.TRUE:
            main.log.report("Master controllers assigned successfully")
        utilities.assert_equals(expect = main.TRUE,actual=result,
                onpass="MasterControllers assigned correctly",
                onfail="MasterControllers not assigned correctly")
        for i in range (1,29):
            main.Mininet1.assign_sw_controller(sw=str(i),count=5,
                    ip1=ONOS1_ip,port1=ONOS1_port,
                    ip2=ONOS2_ip,port2=ONOS2_port,
                    ip3=ONOS3_ip,port3=ONOS3_port,
                    ip4=ONOS4_ip,port4=ONOS4_port,
                    ip5=ONOS5_ip,port5=ONOS5_port) 
        time.sleep(100)

    def CASE4(self,main) :
        import time
        from subprocess import Popen, PIPE
        from sts.topology.teston_topology import TestONTopology # assumes that sts is already in you PYTHONPATH
        
        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS_restPort1 = main.params['CTRL']['restPort1']
        switchURL = main.params['CTRL']['switchURL']
        intentHighURL = main.params['CTRL']['intentHighURL']
        intentLowURL = main.params['CTRL']['intentLowURL']
        
        main.log.report("Setting up and Gathering data for current state")
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
        main.Mininet2.pingLong(src=main.params['PING']['source1'],
                target=main.params['PING']['target1'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source2'],
                target=main.params['PING']['target2'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source3'],
                target=main.params['PING']['target3'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source4'],
                target=main.params['PING']['target4'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source5'],
                target=main.params['PING']['target5'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source6'],
                target=main.params['PING']['target6'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source7'],
                target=main.params['PING']['target7'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source8'],
                target=main.params['PING']['target8'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source9'],
                target=main.params['PING']['target9'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source10'],
                target=main.params['PING']['target10'],pingTime=500)

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
        for n in range(1,5):
            result = main.Mininet1.compare_topo(MNTopo, main.ONOS1.get_json(main.params['CTRL']['ip'+str(n)]+":"+main.params['CTRL']['restPort'+str(n)]+main.params['TopoRest']))
            utilities.assert_equals(expect=main.TRUE,actual=result,onpass="ONOS" + str(n) + " Topology matches MN Topology",onfail="ONOS" + str(n) + " Topology does not match MN Topology")


#******************
#Network Failure Scenario 
# andrew@onlab.us
#******************


    def CASE9(self,main):
        '''
        CASE9: This case cuts Hazelcast link between subcluster 1 and
        subcluster 2 by adding iptables rule to block its port from 
        designated instances. 
        The case also compares the zookeeper topology before and after
        cutting the hazelcast link.
        
        
        Inter-ONOS core network down (network partition)
        (ONOS1, ONOS2) --x-- (ONOS3, ONOS4, ONOS5)
        subcluster 1         subcluster 2
        '''
        import json 
        import time

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS4_ip = main.params['CTRL']['ip4']
        ONOS5_ip = main.params['CTRL']['ip5']

        ONOS_port_default = main.params['CTRL']['port1']
        REST_port_default = main.params['CTRL']['restPort1']
        registry_suffix = main.params['TOPO']['registry']
      
        intentIP = ONOS1_ip
        intentPort=main.params['INTENTS']['intentPort']
        intentURL=main.params['INTENTS']['intentURL']
       
        topo_sw_suffix = main.params['TOPO']['switches']
        topo_sw_url = "http://"+ONOS1_ip+":"+REST_port_default + topo_sw_suffix
        #******************************************
        #NOTE: Hardcoded values for specific test purposes
        HZ_port = "5701"
        
        #For additional intent purposes
        #Sub-cluster 1:
        srcDPID = "00:00:00:00:00:00:10:00"
        dstDPID = "00:00:00:00:00:00:30:04"
        srcMac = "00:00:00:00:00:01"
        dstMac = "00:00:00:00:00:04" 
       
       #Sub-cluster 2:
        srcDPID2 = "00:00:00:00:00:00:50:00"
        dstDPID2 = "00:00:00:00:00:00:60:07"
        srcMac2 = "00:00:00:00:00:05"
        dstMac2 = "00:00:00:00:00:07"
        
        #******************************************

        assertion = main.TRUE

        main.log.report("ONOS Communication Failure test")
        main.log.report("(ONOS1 - ONOS2) ---x--- (ONOS3 - ONOS4 - ONOS5)")

        #We obtain registry for ONOS1 and ONOS3 because the communication 
        #is divided into 2 subclusters and we want to observe the registry
        #in each cluster. ONOS1 and ONOS3 are representatives of each 
        #subcluster
        reg_url_ONOS1 = ONOS1_ip + ":" + REST_port_default + registry_suffix
        reg_url_ONOS3 = ONOS3_ip + ":" + REST_port_default + registry_suffix

        main.log.info("Getting zookeeper registry before hazelcast cut")
        json_ONOS1_before = main.ONOS1.get_json(reg_url_ONOS1)
        json_ONOS3_before = main.ONOS1.get_json(reg_url_ONOS3)

        #Install Intents within subcluster before actually dividing the 
        #cluster. We will later test connectivity within subcluster 
        #by pinging 

        #Sub-cluster 1 intent add bi-directional
        main.ONOS1.add_intent(intent_id = '1', src_dpid = srcDPID,
                dst_dpid = dstDPID, src_mac = srcMac, dst_mac = dstMac,
                intentIP = intentIP, intentPort = intentPort,
                intentURL = intentURL)
        main.ONOS1.add_intent(intent_id = '11', src_dpid = dstDPID,
                dst_dpid = srcDPID, src_mac = dstMac, dst_mac = srcMac,
                intentIP = intentIP, intentPort = intentPort,
                intentURL = intentURL)

        #Sub-cluster 2 intent add bi-directional
        main.ONOS1.add_intent(intent_id = '2', src_dpid = srcDPID2,
                dst_dpid = dstDPID2, src_mac = srcMac2, dst_mac = dstMac2,
                intentIP = intentIP, intentPort = intentPort,
                intentURL = intentURL)
        main.ONOS1.add_intent(intent_id = '22', src_dpid = dstDPID2,
                dst_dpid = srcDPID2, src_mac = dstMac2, dst_mac = srcMac2,
                intentIP = intentIP, intentPort = intentPort,
                intentURL = intentURL)
       
        main.log.info("Blocking hazelcast communication and \
                        creating 2 subclusters (ONOS1,ONOS2) --x-- \
                        (ONOS3,ONOS4,ONOS5)")
       
        #NOTE: the test ping is just to test for intent installation
        main.step("Ping across hosts within each sub-cluster")
        #Ping within ONOS1 and ONOS2
        main.Mininet1.pingHost(SRC='h1',TARGET='h4')
        
        #Ping within ONOS3, ONOS4, and ONOS5
        #Not all switches are connected, so we need to ping two 
        #different sets to verify flow
        main.Mininet1.pingHost(SRC='h5',TARGET='h7')  

        #NOTE: Hazelcast communication is blocked by configuring iptables
        #Any incoming messages through default port(5701) from a specified
        #IP address (ONOS instance ip) will be blocked per iptables config
        
        main.log.report("Isolating topology into 2 sub-clusters using iptables")
        #Sub-cluster 1 setup:
        # block all communication through hazelcast coming from ONOS 3,4,5
        main.ONOS1.setIpTables(ONOS3_ip, HZ_port, action='add')
        main.ONOS1.setIpTables(ONOS4_ip, HZ_port, action='add')
        main.ONOS1.setIpTables(ONOS5_ip, HZ_port, action='add')

        main.ONOS2.setIpTables(ONOS3_ip, HZ_port, action='add')
        main.ONOS2.setIpTables(ONOS4_ip, HZ_port, action='add')
        main.ONOS2.setIpTables(ONOS5_ip, HZ_port, action='add')

        #Sub-cluster 2 setup:
        # block all communication through hazelcast coming from ONOS 1,2
        main.ONOS3.setIpTables(ONOS1_ip, HZ_port, action='add')
        main.ONOS3.setIpTables(ONOS2_ip, HZ_port, action='add')

        main.ONOS4.setIpTables(ONOS1_ip, HZ_port, action='add')
        main.ONOS4.setIpTables(ONOS2_ip, HZ_port, action='add')

        main.ONOS5.setIpTables(ONOS1_ip, HZ_port, action='add')
        main.ONOS5.setIpTables(ONOS2_ip, HZ_port, action='add')

        #**************
        #NOTE: There is a large timeout specification in hazelcast internals.
        #      We need to wait by default 450 seconds for the blocked
        #      channels to be registered with hazelcast. 
        #      With the modification of onos.sh, we set the no.master.confirmation
        #      to value of 150 seconds to reduce test time 
        time.sleep(180)
        #**************
        
        main.log.report("Hazelcast communication has been blocked successfully")
        #NOTE: In order to "update" the zookeeper registry cache, we must
        #      trigger a topology event. This way, when making a REST call,
        #      we will see the true value of the zk registry.
        #Furthermore, we want to see topology discovery across ONOS instances
        #      that have been cut from communication. We will delete s28
        #      and observe topology of all clusters
        #Then, we will delete s20 and observe the topology of all clusters, 
        
        main.log.report("Removing switch 28 from controller")
        main.Mininet1.delete_sw_controller(sw="s28")        

        time.sleep(10)

        #***************************
        #IMPORTANT check
        #NOTE: At this point, the expected behavior is that 
        #      subcluster 2 (ONOS3,4,5) does not see the topology
        #      events of subcluster 1 (ONOS1, 2) and vice versa 
        #Since we rid of 1 switch from each sub-cluster, we 
        #      expect to see 27 switch count in each sub-cluster
        #      although the overall topology has 26/28 switches

        main.log.report("Expecting 27 switches visible out of 28")
        num_switch_ONOS1 = main.ONOS1.check_switch(ONOS1_ip, 27)
        num_switch_ONOS2 = main.ONOS2.check_switch(ONOS2_ip, 27)
        num_switch_ONOS3 = main.ONOS3.check_switch(ONOS3_ip, 27)
        num_switch_ONOS4 = main.ONOS4.check_switch(ONOS4_ip, 27)
        num_switch_ONOS5 = main.ONOS5.check_switch(ONOS5_ip, 27)
      
        main.log.report("ONOS1: "+str(num_switch_ONOS1[0]) + str(num_switch_ONOS1[1]))
        main.log.report("ONOS2: "+str(num_switch_ONOS2[0]) + str(num_switch_ONOS2[1]))
        main.log.report("ONOS3: "+str(num_switch_ONOS3[0]) + str(num_switch_ONOS3[1]))
        main.log.report("ONOS4: "+str(num_switch_ONOS4[0]) + str(num_switch_ONOS4[1]))
        main.log.report("ONOS5: "+str(num_switch_ONOS5[0]) + str(num_switch_ONOS5[1]))

        time.sleep(5)
        
        main.log.report("Removing switch 20 from controller")
        main.Mininet1.delete_sw_controller(sw="s20")

        main.log.report("Expecting 26 switches visible out of 28")
        num_switch_ONOS1 = main.ONOS1.check_switch(ONOS1_ip, 26)
        num_switch_ONOS2 = main.ONOS2.check_switch(ONOS2_ip, 26)
        num_switch_ONOS3 = main.ONOS3.check_switch(ONOS3_ip, 26)
        num_switch_ONOS4 = main.ONOS4.check_switch(ONOS4_ip, 26)
        num_switch_ONOS5 = main.ONOS5.check_switch(ONOS5_ip, 26)
      
        main.log.report(str(num_switch_ONOS1[0]) + str(num_switch_ONOS1[1]))
        main.log.report(str(num_switch_ONOS2[0]) + str(num_switch_ONOS2[1]))
        main.log.report(str(num_switch_ONOS3[0]) + str(num_switch_ONOS3[1]))
        main.log.report(str(num_switch_ONOS4[0]) + str(num_switch_ONOS4[1]))
        main.log.report(str(num_switch_ONOS5[0]) + str(num_switch_ONOS5[1]))

        #***************************

        json_ONOS1_after = main.ONOS1.get_json(reg_url_ONOS1)
        json_ONOS3_after = main.ONOS1.get_json(reg_url_ONOS3)

        dpid_list_before_ONOS1 = []
        dpid_list_after_ONOS1 = []
        dpid_list_before_ONOS3 = []
        dpid_list_after_ONOS3 = []

        if len(json_ONOS1_before) > 0 and len(json_ONOS1_after) > 0:
            if len(json_ONOS3_before) > 0 and len(json_ONOS3_after) > 0:
                #Iterate through json object and obtain all keys
                for key in json_ONOS1_before.keys():
                    dpid_list_before_ONOS1.append(key)
                for key in json_ONOS1_after.keys():
                    dpid_list_after_ONOS1.append(key)
                for key in json_ONOS3_before.keys():
                    dpid_list_before_ONOS3.append(key)
                for key in json_ONOS3_after.keys():
                    dpid_list_after_ONOS3.append(key)
            else:
                main.log.error("Json object for ONOS3 does not exist")
        else:
            main.log.error("Json object for ONOS1 does not exist")

        #Find differences in the json object
        #Alternatives: use 'items' function provided by dictionaries object
        #Refer to pg. 16 of python cookbook

        json_set1 = set(dpid_list_after_ONOS1)
        json_diff_ONOS1 = [x for x in dpid_list_before_ONOS1\
                if x not in json_set1]
        json_set3 = set(dpid_list_after_ONOS3)
        json_diff_ONOS3 = [y for y in dpid_list_before_ONOS3\
                if y not in json_set3]

        #***********************************************
        #IMPORTANT check
        #NOTE: If ONOS is working properly, there should not be any 
        #      differences in the zookeeper registry across ONOS instances.
        if len(json_diff_ONOS1) == 0 and len(json_diff_ONOS3) == 0:
            main.log.report("Zookeeper registry is consistent")
        else:
            main.log.report("Zookeeper registry is NOT consistent")
            assertion = main.FALSE
        #***********************************************
       

        #NOTE: this step is checked manually. Does not need to be 
        #      included in the final release of the test
        #main.step("Check flow table on switches in each sub-cluster")
        #flow_s1 = main.Mininet1.check_flows("s1")
        #flow_s4 = main.Mininet1.check_flows("s4")
        #flow_s5 = main.Mininet1.check_flows("s5")
        #flow_s7 = main.Mininet1.check_flows("s7")

        main.step("Ping across hosts within each sub-cluster")
        #Ping within ONOS1 and ONOS2
        main.Mininet1.pingHost(SRC='h1',TARGET='h4')
        
        #Ping within ONOS3, ONOS4, and ONOS5
        #Not all switches are connected, so we need to ping two 
        #different sets to verify flow
        main.Mininet1.pingHost(SRC='h5',TARGET='h7') 

        main.log.report("Deleting iptables rule")
        main.step("Delete iptables and observe ONOS behavior")
        #Remove all previously set rules for sub-cluster 1
        main.ONOS1.setIpTables(ONOS3_ip, HZ_port, action='remove')
        main.ONOS1.setIpTables(ONOS4_ip, HZ_port, action='remove')
        main.ONOS1.setIpTables(ONOS5_ip, HZ_port, action='remove')

        main.ONOS2.setIpTables(ONOS3_ip, HZ_port, action='remove')
        main.ONOS2.setIpTables(ONOS4_ip, HZ_port, action='remove')
        main.ONOS2.setIpTables(ONOS5_ip, HZ_port, action='remove')

        #Remove all previously set rules for sub-cluster 2
        main.ONOS3.setIpTables(ONOS1_ip, HZ_port, action='remove')
        main.ONOS3.setIpTables(ONOS2_ip, HZ_port, action='remove')

        main.ONOS4.setIpTables(ONOS1_ip, HZ_port, action='remove')
        main.ONOS4.setIpTables(ONOS2_ip, HZ_port, action='remove')

        main.ONOS5.setIpTables(ONOS1_ip, HZ_port, action='remove')
        main.ONOS5.setIpTables(ONOS2_ip, HZ_port, action='remove')

        time.sleep(180)

        #**********************************************
        #IMPORTANT check
        #NOTE: at this point, the ideal behavior is that all
        #      ONOS instances should see a consistent topology
        #      therefore we will expect 26 from all instances
        main.log.report("Expecting 26 switches visible out of 28")
        num_switch_ONOS1 = main.ONOS1.check_switch(ONOS1_ip, 26)
        num_switch_ONOS2 = main.ONOS2.check_switch(ONOS2_ip, 26)
        num_switch_ONOS3 = main.ONOS3.check_switch(ONOS3_ip, 26)
        num_switch_ONOS4 = main.ONOS4.check_switch(ONOS4_ip, 26)
        num_switch_ONOS5 = main.ONOS5.check_switch(ONOS5_ip, 26)

        main.log.report(str(num_switch_ONOS1[0]) + str(num_switch_ONOS1[1]))
        main.log.report(str(num_switch_ONOS2[0]) + str(num_switch_ONOS2[1]))
        main.log.report(str(num_switch_ONOS3[0]) + str(num_switch_ONOS3[1]))
        main.log.report(str(num_switch_ONOS4[0]) + str(num_switch_ONOS4[1]))
        main.log.report(str(num_switch_ONOS5[0]) + str(num_switch_ONOS5[1]))
        #**********************************************

        time.sleep(10) 
        
        #main.step("Check switches that have been deleted previously")
        #sw7_status = main.ONOS1.get_json(topo_sw_url)
        #print sw7_status


        #main.step("Restart ONOS instances and observe behavior")

#***************
#andrew@onlab.us
#***************
