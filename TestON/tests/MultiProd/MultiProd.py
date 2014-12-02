
#Testing the basic functionality of ONOS Next
#For sanity and driver functionality excercises only.

import time
import sys
import os
import re
import time
import json

time.sleep(1)
class MultiProd:
    def __init__(self):
        self.default = ''

    def CASE1(self, main):
        '''
        Startup sequence:
        cell <name>
        onos-verify-cell
        onos-remove-raft-logs        
        git pull
        mvn clean install
        onos-package
        onos-install -f
        onos-wait-for-start
        '''
        
        cell_name = main.params['ENV']['cellName']
        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS1_port = main.params['CTRL']['port1']
        ONOS2_port = main.params['CTRL']['port2']
        ONOS3_port = main.params['CTRL']['port3']   
       
        main.case("Setting up test environment")
        main.log.report("This testcase is testing setting up test environment") 
        main.log.report("__________________________________")
 
        main.step("Applying cell variable to environment")
        cell_result1 = main.ONOSbench.set_cell(cell_name)
        #cell_result2 = main.ONOScli1.set_cell(cell_name)
        #cell_result3 = main.ONOScli2.set_cell(cell_name)
        #cell_result4 = main.ONOScli3.set_cell(cell_name)
        verify_result = main.ONOSbench.verify_cell() 
        cell_result = cell_result1

        main.step("Removing raft logs before a clen installation of ONOS")
        remove_log_Result = main.ONOSbench.onos_remove_raft_logs()        

        main.step("Git checkout and pull master and get version")
        main.ONOSbench.git_checkout("master")
        git_pull_result = main.ONOSbench.git_pull()
        print "git_pull_result = ", git_pull_result
        version_result = main.ONOSbench.get_version(report=True)

        if git_pull_result == 1:
            main.step("Using mvn clean & install")
            clean_install_result = main.ONOSbench.clean_install()
            #clean_install_result = main.TRUE 

        main.step("Creating ONOS package")
        package_result = main.ONOSbench.onos_package()

        #main.step("Creating a cell")
        #cell_create_result = main.ONOSbench.create_cell_file(**************)

        main.step("Installing ONOS package")
        onos1_install_result = main.ONOSbench.onos_install(options="-f", node=ONOS1_ip)
        onos2_install_result = main.ONOSbench.onos_install(options="-f", node=ONOS2_ip)
        onos3_install_result = main.ONOSbench.onos_install(options="-f", node=ONOS3_ip)
        onos_install_result = onos1_install_result and onos2_install_result and onos3_install_result        
        if onos_install_result == main.TRUE:
            main.log.report("Installing ONOS package successful")
        else:
            main.log.report("Installing ONOS package failed")
        	
        onos1_isup = main.ONOSbench.isup(ONOS1_ip)
        onos2_isup = main.ONOSbench.isup(ONOS2_ip)
        onos3_isup = main.ONOSbench.isup(ONOS3_ip)
        onos_isup = onos1_isup and onos2_isup and onos3_isup
        if onos_isup == main.TRUE:
            main.log.report("ONOS instances are up and ready")
        else:
            main.log.report("ONOS instances may not be up")          

        main.step("Starting ONOS service")
        start_result = main.TRUE
        #start_result = main.ONOSbench.onos_start(ONOS1_ip)
        startcli1 = main.ONOScli1.start_onos_cli(ONOS_ip = ONOS1_ip)
        startcli2 = main.ONOScli2.start_onos_cli(ONOS_ip = ONOS2_ip)
        startcli3 = main.ONOScli3.start_onos_cli(ONOS_ip = ONOS3_ip)
        print startcli1
        print startcli2
        print startcli3
            
        case1_result = (package_result and\
                cell_result and verify_result and onos_install_result and\
                onos_isup and start_result )
        utilities.assert_equals(expect=main.TRUE, actual=case1_result,
                onpass="Test startup successful",
                onfail="Test startup NOT successful")

    def CASE11(self, main):
        '''
        Cleanup sequence:
        onos-service <node_ip> stop
        onos-uninstall

        TODO: Define rest of cleanup
        
        '''

      	ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
	
        main.case("Cleaning up test environment")

        main.step("Testing ONOS kill function")
        kill_result1 = main.ONOSbench.onos_kill(ONOS1_ip)
        kill_result2 = main.ONOSbench.onos_kill(ONOS2_ip)
        kill_result3 = main.ONOSbench.onos_kill(ONOS3_ip)
	
        main.step("Stopping ONOS service")
        stop_result1 = main.ONOSbench.onos_stop(ONOS1_ip)
        stop_result2 = main.ONOSbench.onos_stop(ONOS2_ip)
        stop_result3 = main.ONOSbench.onos_stop(ONOS3_ip)

        main.step("Uninstalling ONOS service") 
        uninstall_result = main.ONOSbench.onos_uninstall()

    def CASE3(self, main):
        '''
        Test 'onos' command and its functionality in driver
        '''
       
        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']	

        main.case("Testing 'onos' command")

        main.step("Sending command 'onos -w <onos-ip> system:name'")
        cmdstr1 = "system:name"
        cmd_result1 = main.ONOSbench.onos_cli(ONOS1_ip, cmdstr1) 
        main.log.info("onos command returned: "+cmd_result1)
        cmd_result2 = main.ONOSbench.onos_cli(ONOS2_ip, cmdstr1)
        main.log.info("onos command returned: "+cmd_result2)
        cmd_result3 = main.ONOSbench.onos_cli(ONOS3_ip, cmdstr1)
        main.log.info("onos command returned: "+cmd_result3)

        main.step("Sending command 'onos -w <onos-ip> onos:topology'")
        cmdstr2 = "onos:topology"
        cmd_result4 = main.ONOSbench.onos_cli(ONOS1_ip, cmdstr2)
        main.log.info("onos command returned: "+cmd_result4)
        cmd_result5 = main.ONOSbench.onos_cli(ONOS2_ip, cmdstr2)
        main.log.info("onos command returned: "+cmd_result5)
        cmd_result6 = main.ONOSbench.onos_cli(ONOS6_ip, cmdstr2)
        main.log.info("onos command returned: "+cmd_result6)


    def CASE4(self, main):
        import re
        import time
        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS1_port = main.params['CTRL']['port1']
        ONOS2_port = main.params['CTRL']['port2']
        ONOS3_port = main.params['CTRL']['port3']
        
        main.log.report("This testcase is testing the assignment of all the switches to all controllers and discovering the hosts in reactive mode")
        main.log.report("__________________________________")        
        main.case("Pingall Test(No intents are added)")
        main.step("Assigning switches to controllers")
        for i in range(1,29): #1 to (num of switches +1)
            main.Mininet1.assign_sw_controller(sw=str(i),count=3, 
                    ip1=ONOS1_ip, port1=ONOS1_port,
                    ip2=ONOS2_ip, port2=ONOS2_port,
		            ip3=ONOS3_ip, port3=ONOS3_port)

        switch_mastership = main.TRUE
        for i in range (1,29):
            response = main.Mininet1.get_sw_controller("s"+str(i))
            print("Response is " + str(response))
            if re.search("tcp:"+ONOS1_ip,response):
                switch_mastership = switch_mastership and main.TRUE
            else:
                switch_mastership = main.FALSE

        if switch_mastership == main.TRUE:
            main.log.report("Controller assignment successfull")
        else:
             main.log.report("Controller assignment failed")
        #REACTIVE FWD test
        main.step("Pingall")
        ping_result = main.FALSE
        time1 = time.time()
        ping_result = main.Mininet1.pingall()
        time2 = time.time()
        print "Time for pingall: %2f seconds" % (time2 - time1)
      
        case4_result = switch_mastership and ping_result
        if ping_result == main.TRUE:
            main.log.report("Pingall Test in reactive mode to discover the hosts successful")
        else:
            main.log.report("Pingall Test in reactive mode to discover the hosts failed")

        utilities.assert_equals(expect=main.TRUE, actual=case4_result,onpass="Controller assignment and Pingall Test successful",onfail="Controller assignment and Pingall Test NOT successful")

    

    def CASE5(self,main) :
        import json
        from subprocess import Popen, PIPE
        from sts.topology.teston_topology import TestONTopology # assumes that sts is already in you PYTHONPATH
        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        
        main.log.report("This testcase is testing if all ONOS nodes are in topology sync with mininet and its peer ONOS nodes")
        main.log.report("__________________________________")        
        main.case ("Testing Mininet topology with the topology of multi instances ONOS") 
        main.step("Collecting topology information from ONOS")
        devices1 = main.ONOScli1.devices()
        devices2 = main.ONOScli2.devices()
        devices3 = main.ONOScli3.devices()
        #print "devices1 = ", devices1
        #print "devices2 = ", devices2
        #print "devices3 = ", devices3
        hosts1 = main.ONOScli1.hosts()
        hosts2 = main.ONOScli2.hosts()
        hosts3 = main.ONOScli3.hosts()
        #print "hosts1 = ", hosts1
        #print "hosts2 = ", hosts2
        #print "hosts3 = ", hosts3
        ports1 = main.ONOScli1.ports()
        ports2 = main.ONOScli2.ports()
        ports3 = main.ONOScli3.ports()
        #print "ports1 = ", ports1
        #print "ports2 = ", ports2    
        #print "ports3 = ", ports3
        links1 = main.ONOScli1.links()
        links2 = main.ONOScli2.links()
        links3 = main.ONOScli3.links()
        #print "links1 = ", links1
        #print "links2 = ", links2
        #print "links3 = ", links3
        
        print "**************"
        
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

        Topology_Check = main.TRUE
        main.step("Compare ONOS Topology to MN Topology")
        
        switches_results1 =  main.Mininet1.compare_switches(MNTopo, json.loads(devices1))
        print "switches_Result1 = ", switches_results1
        utilities.assert_equals(expect=main.TRUE, actual=switches_results1,
                onpass="ONOS1 Switches view is correct",
                onfail="ONOS1 Switches view is incorrect")

        switches_results2 =  main.Mininet1.compare_switches(MNTopo, json.loads(devices2))
        utilities.assert_equals(expect=main.TRUE, actual=switches_results2,
                onpass="ONOS2 Switches view is correct",
                onfail="ONOS2 Switches view is incorrect")
    
        switches_results3 =  main.Mininet1.compare_switches(MNTopo, json.loads(devices3))
        utilities.assert_equals(expect=main.TRUE, actual=switches_results3,
                onpass="ONOS3 Switches view is correct",
                onfail="ONOS3 Switches view is incorrect")

        '''
        ports_results1 =  main.Mininet1.compare_ports(MNTopo, json.loads(ports1))
        utilities.assert_equals(expect=main.TRUE, actual=ports_results1,
                onpass="ONOS1 Ports view is correct",
                onfail="ONOS1 Ports view is incorrect")

        ports_results2 =  main.Mininet1.compare_ports(MNTopo, json.loads(ports2))
        utilities.assert_equals(expect=main.TRUE, actual=ports_results2,
                onpass="ONOS2 Ports view is correct",
                onfail="ONOS2 Ports view is incorrect")

        ports_results3 =  main.Mininet1.compare_ports(MNTopo, json.loads(ports3))
        utilities.assert_equals(expect=main.TRUE, actual=ports_results3,
                onpass="ONOS3 Ports view is correct",
                onfail="ONOS3 Ports view is incorrect")
        '''        

        links_results1 =  main.Mininet1.compare_links(MNTopo, json.loads(links1))
        utilities.assert_equals(expect=main.TRUE, actual=links_results1,
                onpass="ONOS1 Links view is correct",
                onfail="ONOS1 Links view is incorrect")

        links_results2 =  main.Mininet1.compare_links(MNTopo, json.loads(links2))
        utilities.assert_equals(expect=main.TRUE, actual=links_results2,
                onpass="ONOS2 Links view is correct",
                onfail="ONOS2 Links view is incorrect")

        links_results3 =  main.Mininet1.compare_links(MNTopo, json.loads(links3))
        utilities.assert_equals(expect=main.TRUE, actual=links_results3,
                onpass="ONOS2 Links view is correct",
                onfail="ONOS2 Links view is incorrect")

        #topo_result = switches_results1 and switches_results2 and switches_results3\
                #and ports_results1 and ports_results2 and ports_results3\
                #and links_results1 and links_results2 and links_results3
        
        topo_result = switches_results1 and switches_results2 and switches_results3\
                and links_results1 and links_results2 and links_results3

        if topo_result == main.TRUE:
            main.log.report("Topology Check Test with mininet and ONOS instances successful")
        else:
            main.log.report("Topology Check Test with mininet and ONOS instances failed")

        utilities.assert_equals(expect=main.TRUE, actual=topo_result,
                onpass="Topology Check Test successful",
                onfail="Topology Check Test NOT successful")




    def CASE10(self):
        main.log.report("This testcase uninstalls the reactive forwarding app")
        main.log.report("__________________________________")
        main.case("Uninstalling reactive forwarding app")
        #Unistall onos-app-fwd app to disable reactive forwarding
        appUninstall_result1 = main.ONOScli1.feature_uninstall("onos-app-fwd")
        appUninstall_result2 = main.ONOScli2.feature_uninstall("onos-app-fwd")
        appUninstall_result3 = main.ONOScli3.feature_uninstall("onos-app-fwd")
        main.log.info("onos-app-fwd uninstalled")

        #After reactive forwarding is disabled, the reactive flows on switches timeout in 10-15s
        #So sleep for 15s
        time.sleep(15)
        
        hosts = main.ONOScli1.hosts()
        main.log.info(hosts)
        
        case10_result = appUninstall_result1 and appUninstall_result2 and appUninstall_result3
        utilities.assert_equals(expect=main.TRUE, actual=case10_result,onpass="Reactive forwarding app uninstallation successful",onfail="Reactive forwarding app uninstallation failed")


    def CASE6(self):
        main.log.report("This testcase is testing the addition of host intents and then doing pingall")
        main.log.report("__________________________________")        
        main.case("Obtaining hostsfor adding host intents")
        main.step("Get hosts")
        hosts = main.ONOScli1.hosts()
        main.log.info(hosts)

        main.step("Get all devices id")
        devices_id_list = main.ONOScli1.get_all_devices_id()
        main.log.info(devices_id_list) 

        #ONOS displays the hosts in hex format unlike mininet which does in decimal format
        #So take care while adding intents
        
        '''
        main.step("Add host intents for mn hosts(h8-h18,h9-h19,h10-h20,h11-h21,h12-h22,h13-h23,h14-h24,h15-h25,h16-h26,h17-h27)")
        hth_intent_result = main.ONOScli1.add_host_intent("00:00:00:00:00:08/-1", "00:00:00:00:00:12/-1")
        hth_intent_result = main.ONOScli1.add_host_intent("00:00:00:00:00:09/-1", "00:00:00:00:00:13/-1")
        hth_intent_result = main.ONOScli1.add_host_intent("00:00:00:00:00:0A/-1", "00:00:00:00:00:14/-1")
        hth_intent_result = main.ONOScli1.add_host_intent("00:00:00:00:00:0B/-1", "00:00:00:00:00:15/-1")
        hth_intent_result = main.ONOScli1.add_host_intent("00:00:00:00:00:0C/-1", "00:00:00:00:00:16/-1")
        hth_intent_result = main.ONOScli1.add_host_intent("00:00:00:00:00:0D/-1", "00:00:00:00:00:17/-1")
        hth_intent_result = main.ONOScli1.add_host_intent("00:00:00:00:00:0E/-1", "00:00:00:00:00:18/-1")
        hth_intent_result = main.ONOScli1.add_host_intent("00:00:00:00:00:0F/-1", "00:00:00:00:00:19/-1")
        hth_intent_result = main.ONOScli1.add_host_intent("00:00:00:00:00:10/-1", "00:00:00:00:00:1A/-1")
        hth_intent_result = main.ONOScli1.add_host_intent("00:00:00:00:00:11/-1", "00:00:00:00:00:1B/-1") 
        '''

        for i in range(8,18):
            main.log.info("Adding host intent between h"+str(i)+" and h"+str(i+10))
            host1 =  "00:00:00:00:00:" + str(hex(i)[2:]).zfill(2).upper()
            host2 =  "00:00:00:00:00:" + str(hex(i+10)[2:]).zfill(2).upper()
            #NOTE: get host can return None
            #TODO: handle this
            host1_id = main.ONOScli1.get_host(host1)['id']
            host2_id = main.ONOScli1.get_host(host2)['id']
            tmp_result = main.ONOScli1.add_host_intent(host1_id, host2_id )

        flowHandle = main.ONOScli1.flows()
        #print "flowHandle = ", flowHandle
        main.log.info("flows:" +flowHandle)

        count = 1
        i = 8
        Ping_Result = main.TRUE
        while i <18 :
            main.log.info("\n\nh"+str(i)+" is Pinging h" + str(i+10))
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+10))
            if ping == main.FALSE and count <5:
                count+=1
                #i = 8
                Ping_Result = main.FALSE
                main.log.report("Ping between h" + str(i) + " and h" + str(i+10) + " failed. Making attempt number "+str(count) + " in 2 seconds")
                time.sleep(2)
            elif ping==main.FALSE:
                main.log.report("All ping attempts between h" + str(i) + " and h" + str(i+10) +"have failed")
                i=19
                Ping_Result = main.FALSE
            elif ping==main.TRUE:
                main.log.info("Ping test between h" + str(i) + " and h" + str(i+10) + "passed!")
                i+=1
                Ping_Result = main.TRUE
            else:
                main.log.info("Unknown error")
                Ping_Result = main.ERROR
        if Ping_Result==main.FALSE:
            main.log.report("Host intents have not ben installed correctly. Cleaning up")
            #main.cleanup()
            #main.exit()
        if Ping_Result==main.TRUE:
            main.log.report("Host intents have been installed correctly")

        case6_result = Ping_Result
        utilities.assert_equals(expect=main.TRUE, actual=case6_result,
                onpass="Host intent addition and Pingall Test successful",
                onfail="Host intent addition and Pingall Test NOT successful")


    def CASE7 (self,main):
       
        ONOS1_ip = main.params['CTRL']['ip1']

        link_sleep = int(main.params['timers']['LinkDiscovery'])

        main.log.report("This testscase is killing a link to ensure that link discovery is consistent")
        main.log.report("__________________________________")        
        main.case("Killing a link to Ensure that Link Discovery is Working Properly")
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


        main.step("Determine the current number of switches and links")
        topology_output = main.ONOScli1.topology()
        topology_result = main.ONOSbench.get_topology(topology_output)
        activeSwitches = topology_result['devices']
        links = topology_result['links']
        print "activeSwitches = ", type(activeSwitches)
        print "links = ", type(links)
        main.log.info("Currently there are %s switches and %s links"  %(str(activeSwitches), str(links)))

        main.step("Kill Link between s3 and s28")
        main.Mininet1.link(END1="s3",END2="s28",OPTION="down")
        time.sleep(link_sleep)
        topology_output = main.ONOScli2.topology()
        Link_Down = main.ONOSbench.check_status(topology_output,activeSwitches,str(int(links)-2))
        if Link_Down == main.TRUE:
            main.log.report("Link Down discovered properly")
        utilities.assert_equals(expect=main.TRUE,actual=Link_Down,
                onpass="Link Down discovered properly",
                onfail="Link down was not discovered in "+ str(link_sleep) + " seconds")
        
        main.step("Bring link between s3 and s28 back up")
        Link_Up = main.Mininet1.link(END1="s3",END2="s28",OPTION="up")
        time.sleep(link_sleep)
        topology_output = main.ONOScli2.topology()
        Link_Up = main.ONOSbench.check_status(topology_output,activeSwitches,str(links))
        if Link_Up == main.TRUE:
            main.log.report("Link up discovered properly")
        utilities.assert_equals(expect=main.TRUE,actual=Link_Up,
                onpass="Link up discovered properly",
                onfail="Link up was not discovered in "+ str(link_sleep) + " seconds")

        main.step("Compare ONOS Topology to MN Topology")
        main.case ("Testing Mininet topology with the topology of multi instances ONOS") 
        main.step("Collecting topology information from ONOS")
        devices1 = main.ONOScli1.devices()
        devices2 = main.ONOScli2.devices()
        devices3 = main.ONOScli3.devices()
        print "devices1 = ", devices1
        print "devices2 = ", devices2
        print "devices3 = ", devices3
        hosts1 = main.ONOScli1.hosts()
        hosts2 = main.ONOScli2.hosts()
        hosts3 = main.ONOScli3.hosts()
        #print "hosts1 = ", hosts1
        #print "hosts2 = ", hosts2
        #print "hosts3 = ", hosts3
        ports1 = main.ONOScli1.ports()
        ports2 = main.ONOScli2.ports()
        ports3 = main.ONOScli3.ports()
        #print "ports1 = ", ports1
        #print "ports2 = ", ports2    
        #print "ports3 = ", ports3
        links1 = main.ONOScli1.links()
        links2 = main.ONOScli2.links()
        links3 = main.ONOScli3.links()
        #print "links1 = ", links1
        #print "links2 = ", links2
        #print "links3 = ", links3
        
        print "**************"
        
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

        Topology_Check = main.TRUE
        main.step("Compare ONOS Topology to MN Topology")
        
        switches_results1 =  main.Mininet1.compare_switches(MNTopo, json.loads(devices1))
        print "switches_Result1 = ", switches_results1
        utilities.assert_equals(expect=main.TRUE, actual=switches_results1,
                onpass="ONOS1 Switches view is correct",
                onfail="ONOS1 Switches view is incorrect")

        switches_results2 =  main.Mininet1.compare_switches(MNTopo, json.loads(devices2))
        utilities.assert_equals(expect=main.TRUE, actual=switches_results2,
                onpass="ONOS2 Switches view is correct",
                onfail="ONOS2 Switches view is incorrect")
    
        switches_results3 =  main.Mininet1.compare_switches(MNTopo, json.loads(devices3))
        utilities.assert_equals(expect=main.TRUE, actual=switches_results3,
                onpass="ONOS3 Switches view is correct",
                onfail="ONOS3 Switches view is incorrect")

        '''
        ports_results1 =  main.Mininet1.compare_ports(MNTopo, json.loads(ports1))
        utilities.assert_equals(expect=main.TRUE, actual=ports_results1,
                onpass="ONOS1 Ports view is correct",
                onfail="ONOS1 Ports view is incorrect")

        ports_results2 =  main.Mininet1.compare_ports(MNTopo, json.loads(ports2))
        utilities.assert_equals(expect=main.TRUE, actual=ports_results2,
                onpass="ONOS2 Ports view is correct",
                onfail="ONOS2 Ports view is incorrect")

        ports_results3 =  main.Mininet1.compare_ports(MNTopo, json.loads(ports3))
        utilities.assert_equals(expect=main.TRUE, actual=ports_results3,
                onpass="ONOS3 Ports view is correct",
                onfail="ONOS3 Ports view is incorrect")
        '''        

        links_results1 =  main.Mininet1.compare_links(MNTopo, json.loads(links1))
        utilities.assert_equals(expect=main.TRUE, actual=links_results1,
                onpass="ONOS1 Links view is correct",
                onfail="ONOS1 Links view is incorrect")

        links_results2 =  main.Mininet1.compare_links(MNTopo, json.loads(links2))
        utilities.assert_equals(expect=main.TRUE, actual=links_results2,
                onpass="ONOS2 Links view is correct",
                onfail="ONOS2 Links view is incorrect")

        links_results3 =  main.Mininet1.compare_links(MNTopo, json.loads(links3))
        utilities.assert_equals(expect=main.TRUE, actual=links_results3,
                onpass="ONOS2 Links view is correct",
                onfail="ONOS2 Links view is incorrect")
               
        #topo_result = switches_results1 and switches_results2 and switches_results3\
                #and ports_results1 and ports_results2 and ports_results3\
                #and links_results1 and links_results2 and links_results3
        
        topo_result = switches_results1 and switches_results2 and switches_results3\
                and links_results1 and links_results2 and links_results3

        utilities.assert_equals(expect=main.TRUE, actual=topo_result and Link_Up and Link_Down,
                onpass="Topology Check Test successful",
                onfail="Topology Check Test NOT successful")


    def CASE8(self):
        '''
        Intent removal
        ''' 
        main.log.report("This testcase removes host intents before adding the point intents")
        main.log.report("__________________________________")        
        main.log.info("Host intents removal")
        main.case("Removing host intents")
        main.step("Obtain the intent id's")
        intent_result = main.ONOScli1.intents()
        #print "intent_result = ",intent_result
        
        intent_linewise = intent_result.split("\n")
        intentList = []
        for line in intent_linewise:
            if line.startswith("id="):
                intentList.append(line)

        intentids = []
        for line in intentList:
            intentids.append(line.split(",")[0].split("=")[1])
        for id in intentids:
            print "id = ", id

        main.step("Iterate through the intentids list and remove each intent")
        for id in intentids:
            main.ONOScli1.remove_intent(intent_id = id)

        intent_result = main.ONOScli1.intents()
        intent_linewise = intent_result.split("\n")
        list_afterRemoval = []
        for line in intent_linewise:
            if line.startswith("id="):
                list_afterRemoval.append(line)

        intentState = {}
        for id, line in zip(intentids, list_afterRemoval):
            #print "line after removing intent = ", line
            x = line.split(",")
            state = x[1].split("=")[1]
            intentState[id] = state

        case8_result = main.TRUE
        for key,value in intentState.iteritems():
            print "key,value = ", key, value
            if value == "WITHDRAWN": 
                case8_result = case8_result and main.TRUE
            else:    
                case8_result = case8_result and main.FALSE

        i = 8
        Ping_Result = main.TRUE
        while i <18 :
            main.log.info("\n\nh"+str(i)+" is Pinging h" + str(i+10))
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+10))
            if ping==main.TRUE:
                i = 19
                Ping_Result = main.TRUE
            elif ping==main.FALSE:
                i+=1
                Ping_Result = main.FALSE
            else:
                main.log.info("Unknown error")
                Ping_Result = main.ERROR
        
        #Note: If the ping result failed, that means the intents have been withdrawn correctly.
        if Ping_Result==main.TRUE:
            main.log.report("Host intents have not been withdrawn correctly")
            #main.cleanup()
            #main.exit()
        if Ping_Result==main.FALSE:
            main.log.report("Host intents have been withdrawn correctly")

        case8_result = case8_result and Ping_Result

        if case8_result == main.FALSE:
            main.log.report("Intent removal successful")
        else:
            main.log.report("Intent removal failed")
                        
        utilities.assert_equals(expect=main.FALSE, actual=case8_result,
                onpass="Intent removal test failed",
                onfail="Intent removal test successful")
             

    def CASE9(self):
        '''
        This test case adds point intents. Make sure you run test case 8 which is host intent removal before executing this test case.
        Else the host intent's flows will persist on switches and the pings would work even if there is some issue with the point intent's flows
        '''
        main.log.report("This testcase adds point intents and then does pingall")
        main.log.report("__________________________________")        
        main.log.info("Adding point intents")
        main.case("Adding bidirectional point for mn hosts(h8-h18,h9-h19,h10-h20,h11-h21,h12-h22,h13-h23,h14-h24,h15-h25,h16-h26,h17-h27)") 
        main.step("Add point-to-point intents for mininet hosts h8 and h18 or ONOS hosts h8 and h12")
        ptp_intent_result = main.ONOScli1.add_point_intent("of:0000000000003008/1", "of:0000000000006018/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOScli1.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOScli1.add_point_intent("of:0000000000006018/1", "of:0000000000003008/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOScli1.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
       
        main.step("Add point-to-point intents for mininet hosts h9 and h19 or ONOS hosts h9 and h13")
        ptp_intent_result = main.ONOScli1.add_point_intent("of:0000000000003009/1", "of:0000000000006019/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOScli1.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOScli1.add_point_intent("of:0000000000006019/1", "of:0000000000003009/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOScli1.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
        
        main.step("Add point-to-point intents for mininet hosts h10 and h20 or ONOS hosts hA and h14")
        ptp_intent_result = main.ONOScli1.add_point_intent("of:0000000000003010/1", "of:0000000000006020/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOScli1.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOScli1.add_point_intent("of:0000000000006020/1", "of:0000000000003010/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOScli1.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)

        main.step("Add point-to-point intents for mininet hosts h11 and h21 or ONOS hosts hB and h15")
        ptp_intent_result = main.ONOScli1.add_point_intent("of:0000000000003011/1", "of:0000000000006021/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOScli1.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOScli1.add_point_intent("of:0000000000006021/1", "of:0000000000003011/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOScli1.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
            
        main.step("Add point-to-point intents for mininet hosts h12 and h22 or ONOS hosts hC and h16")
        ptp_intent_result = main.ONOScli1.add_point_intent("of:0000000000003012/1", "of:0000000000006022/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOScli1.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOScli1.add_point_intent("of:0000000000006022/1", "of:0000000000003012/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOScli1.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
            
        main.step("Add point-to-point intents for mininet hosts h13 and h23 or ONOS hosts hD and h17")
        ptp_intent_result = main.ONOScli1.add_point_intent("of:0000000000003013/1", "of:0000000000006023/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOScli1.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOScli1.add_point_intent("of:0000000000006023/1", "of:0000000000003013/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOScli1.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)

        main.step("Add point-to-point intents for mininet hosts h14 and h24 or ONOS hosts hE and h18")
        ptp_intent_result = main.ONOScli1.add_point_intent("of:0000000000003014/1", "of:0000000000006024/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOScli1.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOScli1.add_point_intent("of:0000000000006024/1", "of:0000000000003014/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOScli1.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
            
        main.step("Add point-to-point intents for mininet hosts h15 and h25 or ONOS hosts hF and h19")
        ptp_intent_result = main.ONOScli1.add_point_intent("of:0000000000003015/1", "of:0000000000006025/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOScli1.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOScli1.add_point_intent("of:0000000000006025/1", "of:0000000000003015/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOScli1.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
            
        main.step("Add point-to-point intents for mininet hosts h16 and h26 or ONOS hosts h10 and h1A")
        ptp_intent_result = main.ONOScli1.add_point_intent("of:0000000000003016/1", "of:0000000000006026/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOScli1.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOScli1.add_point_intent("of:0000000000006026/1", "of:0000000000003016/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOScli1.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)


        main.step("Add point-to-point intents for mininet hosts h17 and h27 or ONOS hosts h11 and h1B")
        ptp_intent_result = main.ONOScli1.add_point_intent("of:0000000000003017/1", "of:0000000000006027/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOScli1.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOScli1.add_point_intent("of:0000000000006027/1", "of:0000000000003017/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOScli1.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)

        print("_______________________________________________________________________________________")

        flowHandle = main.ONOScli1.flows()
        #print "flowHandle = ", flowHandle
        main.log.info("flows :" + flowHandle)        

        count = 1
        i = 8
        Ping_Result = main.TRUE
        while i <18 :
            main.log.info("\n\nh"+str(i)+" is Pinging h" + str(i+10))
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+10))
            if ping == main.FALSE and count <5:
                count+=1
                #i = 8
                Ping_Result = main.FALSE
                main.log.report("Ping between h" + str(i) + " and h" + str(i+10) + " failed. Making attempt number "+str(count) + " in 2 seconds")
                time.sleep(2)
            elif ping==main.FALSE:
                main.log.report("All ping attempts between h" + str(i) + " and h" + str(i+10) +"have failed")
                i=19
                Ping_Result = main.FALSE
            elif ping==main.TRUE:
                main.log.info("Ping test between h" + str(i) + " and h" + str(i+10) + "passed!")
                i+=1
                Ping_Result = main.TRUE
            else:
                main.log.info("Unknown error")
                Ping_Result = main.ERROR
        if Ping_Result==main.FALSE:
            main.log.report("Ping all test after Point intents addition failed. Cleaning up")
            #main.cleanup()
            #main.exit()
        if Ping_Result==main.TRUE:
            main.log.report("Ping all test after Point intents addition successful")

        case8_result = Ping_Result
        utilities.assert_equals(expect=main.TRUE, actual=case8_result,
                onpass="Ping all test after Point intents addition successful",
                onfail="Ping all test after Point intents addition failed")

    def CASE31(self):
        ''' 
            This test case adds point intent related to SDN-IP matching on ICMP (ethertype=IPV4, ipProto=1)
        '''
        import json

        main.log.report("This test case adds point intent related to SDN-IP matching on ICMP")
        main.case("Adding bidirectional point intent related to SDN-IP matching on ICMP")
        main.step("Adding bidirectional point intent")
        #add-point-intent --ipSrc=10.0.0.8/32 --ipDst=10.0.0.18/32 --ethType=IPV4 --ipProto=1  of:0000000000003008/1 of:0000000000006018/1
        
        hosts_json = json.loads(main.ONOScli1.hosts())
        for  i in range(8,11):
            main.log.info("Adding point intent between h"+str(i)+" and h"+str(i+10))
            host1 =  "00:00:00:00:00:" + str(hex(i)[2:]).zfill(2).upper()
            host2 =  "00:00:00:00:00:" + str(hex(i+10)[2:]).zfill(2).upper()
            host1_id = main.ONOScli1.get_host(host1)['id']
            host2_id = main.ONOScli1.get_host(host2)['id']
            for host in hosts_json:
                if host['id'] == host1_id:
                    ip1 = host['ips'][0]
                    ip1 = str(ip1+"/32")
                    print "ip1 = ", ip1
                    device1 = host['location']['device']
                    device1 = str(device1+"/1")
                    print "device1 = ", device1
                elif host['id'] == host2_id:
                    ip2 = str(host['ips'][0])+"/32"
                    print "ip2 = ", ip2
                    device2 = host['location']["device"]
                    device2 = str(device2+"/1")
                    print "device2 = ", device2
                
            p_intent_result1 = main.ONOScli1.add_point_intent(ingress_device=device1, egress_device=device2, ipSrc=ip1, ipDst=ip2,
                                  ethType=main.params['SDNIP']['ethType'], ipProto=main.params['SDNIP']['icmpProto'])
            
            get_intent_result = main.ONOScli1.intents()
            main.log.info(get_intent_result)
 
            p_intent_result2 = main.ONOScli1.add_point_intent(ingress_device=device2, egress_device=device1, ipSrc=ip2, ipDst=ip1, 
                                  ethType=main.params['SDNIP']['ethType'], ipProto=main.params['SDNIP']['icmpProto']) 
            
            get_intent_result = main.ONOScli1.intents()
            main.log.info(get_intent_result)
            if (p_intent_result1 and p_intent_result2) == main.TRUE:
                #get_intent_result = main.ONOScli1.intents()
                #main.log.info(get_intent_result)
                main.log.info("Point intent related to SDN-IP matching on ICMP install successful")
       
        time.sleep(15) 
        get_intent_result = main.ONOScli1.intents()
        main.log.info("intents = "+ get_intent_result)
        get_flows_result = main.ONOScli1.flows()
        main.log.info("flows = " + get_flows_result)
        
        count = 1
        i = 8
        Ping_Result = main.TRUE
        while i <11 :
            main.log.info("\n\nh"+str(i)+" is Pinging h" + str(i+10))
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+10))
            if ping == main.FALSE and count <3:
                count+=1
                #i = 8
                Ping_Result = main.FALSE
                main.log.report("Ping between h" + str(i) + " and h" + str(i+10) + " failed. Making attempt number "+str(count) + " in 2 seconds")
                time.sleep(2)
            elif ping==main.FALSE:
                main.log.report("All ping attempts between h" + str(i) + " and h" + str(i+10) +"have failed")
                i=19
                Ping_Result = main.FALSE
            elif ping==main.TRUE:
                main.log.info("Ping test between h" + str(i) + " and h" + str(i+10) + "passed!")
                i+=1
                Ping_Result = main.TRUE
            else:
                main.log.info("Unknown error")
                Ping_Result = main.ERROR
        if Ping_Result==main.FALSE:
            main.log.report("Ping test after Point intents related to SDN-IP matching on ICMP failed.")
            #main.cleanup()
            #main.exit()
        if Ping_Result==main.TRUE:
            main.log.report("Ping all test after Point intents related to SDN-IP matching on ICMP successful")
                   
        case31_result = Ping_Result and p_intent_result1 and p_intent_result2
        utilities.assert_equals(expect=main.TRUE, actual=case31_result,
                onpass="Point intent related to SDN-IP matching on ICMP and ping test successful",
                onfail="Point intent related to SDN-IP matching on ICMP and ping test failed")
   
    def CASE32(self):
        ''' 
            This test case adds point intent related to SDN-IP matching on TCP (ethertype=IPV4, ipProto=6, DefaultPort for iperf=5001)
            Note: Although BGP port is 179, we are using 5001 because iperf is used for verifying and iperf's default port is 5001
        '''
        import json

        main.log.report("This test case adds point intent related to SDN-IP matching on TCP")
        main.case("Adding bidirectional point intent related to SDN-IP matching on TCP")
        main.step("Adding bidirectional point intent")
        """
        add-point-intent --ipSrc=10.0.0.8/32 --ipDst=10.0.0.18/32 --ethType=IPV4 --ipProto=6 --tcpDst=5001  of:0000000000003008/1 of:0000000000006018/1

        add-point-intent --ipSrc=10.0.0.18/32 --ipDst=10.0.0.8/32 --ethType=IPV4 --ipProto=6 --tcpDst=5001  of:0000000000006018/1 of:0000000000003008/1
    
        add-point-intent --ipSrc=10.0.0.8/32 --ipDst=10.0.0.18/32 --ethType=IPV4 --ipProto=6 --tcpSrc=5001  of:0000000000003008/1 of:0000000000006018/1

        add-point-intent --ipSrc=10.0.0.18/32 --ipDst=10.0.0.8/32 --ethType=IPV4 --ipProto=6 --tcpSrc=5001  of:0000000000006018/1 of:0000000000003008/1

        """           
    
        hosts_json = json.loads(main.ONOScli1.hosts())
        for  i in range(8,9):
            main.log.info("Adding point intent between h"+str(i)+" and h"+str(i+10))
            host1 =  "00:00:00:00:00:" + str(hex(i)[2:]).zfill(2).upper()
            host2 =  "00:00:00:00:00:" + str(hex(i+10)[2:]).zfill(2).upper()
            host1_id = main.ONOScli1.get_host(host1)['id']
            host2_id = main.ONOScli1.get_host(host2)['id']
            for host in hosts_json:
                if host['id'] == host1_id:
                    ip1 = host['ips'][0]
                    ip1 = str(ip1+"/32")
                    print "ip1 = ", ip1
                    device1 = host['location']['device']
                    device1 = str(device1+"/1")
                    print "device1 = ", device1
                elif host['id'] == host2_id:
                    ip2 = str(host['ips'][0])+"/32"
                    print "ip2 = ", ip2
                    device2 = host['location']["device"]
                    device2 = str(device2+"/1")
                    print "device2 = ", device2
                
            p_intent_result1 = main.ONOScli1.add_point_intent(ingress_device=device1, egress_device=device2, ipSrc=ip1, ipDst=ip2,
                                  ethType=main.params['SDNIP']['ethType'], ipProto=main.params['SDNIP']['tcpProto'], tcpDst=main.params['SDNIP']['dstPort']) 
            p_intent_result2 = main.ONOScli1.add_point_intent(ingress_device=device2, egress_device=device1, ipSrc=ip2, ipDst=ip1, 
                                  ethType=main.params['SDNIP']['ethType'], ipProto=main.params['SDNIP']['tcpProto'], tcpDst=main.params['SDNIP']['dstPort'])

            p_intent_result3 = main.ONOScli1.add_point_intent(ingress_device=device1, egress_device=device2, ipSrc=ip1, ipDst=ip2,
                                  ethType=main.params['SDNIP']['ethType'], ipProto=main.params['SDNIP']['tcpProto'], tcpSrc=main.params['SDNIP']['srcPort'])
            p_intent_result4 = main.ONOScli1.add_point_intent(ingress_device=device2, egress_device=device1, ipSrc=ip2, ipDst=ip1,
                                  ethType=main.params['SDNIP']['ethType'], ipProto=main.params['SDNIP']['tcpProto'], tcpSrc=main.params['SDNIP']['srcPort']) 

            p_intent_result = p_intent_result1 and p_intent_result2 and p_intent_result3 and p_intent_result4
            if p_intent_result ==main.TRUE:
                get_intent_result = main.ONOScli1.intents()
                main.log.info(get_intent_result)
                main.log.info("Point intent related to SDN-IP matching on TCP install successful")
        
        iperf_result = main.Mininet1.iperf('h8', 'h18') 
        if iperf_result == main.TRUE:
            main.log.report("iperf test successful")
        else:
            main.log.report("iperf test failed")


        case32_result = p_intent_result and iperf_result
        utilities.assert_equals(expect=main.TRUE, actual=case32_result,
                onpass="Ping all test after Point intents addition related to SDN-IP on TCP match successful",
                onfail="Ping all test after Point intents addition related to SDN-IP on TCP match failed") 
