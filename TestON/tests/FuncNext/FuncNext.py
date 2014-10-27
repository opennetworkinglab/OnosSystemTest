
#Testing the basic functionality of ONOS Next
#For sanity and driver functionality excercises only.

import time
import sys
import os
import re
import time
import json

time.sleep(1)
class FuncNext:
    def __init__(self):
        self.default = ''

    def CASE1(self, main):
        '''
        Startup sequence:
        git pull
        mvn clean install
        onos-package
        cell <name>
        onos-verify-cell
        onos-install -f
        onos-wait-for-start
        '''
        
        cell_name = main.params['ENV']['cellName']
        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS1_port = main.params['CTRL']['port1']
        
        main.case("Setting up test environment")
        
        main.step("Git checkout and pull master and get version")
        main.ONOSbench.git_checkout("master")
        git_pull_result = main.ONOSbench.git_pull()
        print "git_pull_result = ", git_pull_result
        version_result = main.ONOSbench.get_version()

        main.step("Using mvn clean & install")
        #clean_install_result = main.ONOSbench.clean_install()
        #clean_install_result = main.TRUE

        main.step("Applying cell variable to environment")
        cell_result1 = main.ONOSbench.set_cell(cell_name)
        verify_result = main.ONOSbench.verify_cell()
        cell_result2 = main.ONOS2.set_cell(cell_name)
        #verify_result = main.ONOS2.verify_cell()
        main.ONOS2.start_onos_cli(ONOS_ip=main.params['CTRL']['ip1'])
        
        cell_result = cell_result1 and cell_result2

        main.step("Creating ONOS package")
        package_result = main.ONOSbench.onos_package()

        #main.step("Creating a cell")
        #cell_create_result = main.ONOSbench.create_cell_file(**************)

        main.step("Installing ONOS package")
        onos_install_result = main.ONOSbench.onos_install()
        onos1_isup = main.ONOSbench.isup()
   
        main.step("Starting ONOS service")
        start_result = main.ONOSbench.onos_start(ONOS1_ip)

        case1_result = (package_result and\
                cell_result and verify_result and onos_install_result and\
                onos1_isup and start_result )
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

        main.case("Cleaning up test environment")

        main.step("Testing ONOS kill function")
        kill_result = main.ONOSbench.onos_kill(ONOS1_ip)

        main.step("Stopping ONOS service")
        stop_result = main.ONOSbench.onos_stop(ONOS1_ip)

        main.step("Uninstalling ONOS service") 
        uninstall_result = main.ONOSbench.onos_uninstall()

    def CASE3(self, main):
        '''
        Test 'onos' command and its functionality in driver
        '''
        
        ONOS1_ip = main.params['CTRL']['ip1']

        main.case("Testing 'onos' command")

        main.step("Sending command 'onos -w <onos-ip> system:name'")
        cmdstr1 = "system:name"
        cmd_result1 = main.ONOSbench.onos_cli(ONOS1_ip, cmdstr1) 
        main.log.info("onos command returned: "+cmd_result1)

        main.step("Sending command 'onos -w <onos-ip> onos:topology'")
        cmdstr2 = "onos:topology"
        cmd_result2 = main.ONOSbench.onos_cli(ONOS1_ip, cmdstr2)
        main.log.info("onos command returned: "+cmd_result2)



    def CASE4(self, main):
        import re
        import time
        main.case("Pingall Test")
        main.step("Assigning switches to controllers")
        for i in range(1,29):
            if i ==1:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=ONOS1_ip,port1=ONOS1_port)
            elif i>=2 and i<5:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=ONOS1_ip,port1=ONOS1_port)
            elif i>=5 and i<8:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=ONOS1_ip,port1=ONOS1_port)
            elif i>=8 and i<18:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=ONOS1_ip,port1=ONOS1_port)
            elif i>=18 and i<28:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=ONOS1_ip,port1=ONOS1_port)
            else:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=ONOS1_ip,port1=ONOS1_port)
        Switch_Mastership = main.TRUE
        for i in range (1,29):
            if i==1:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is " + str(response))
                if re.search("tcp:"+ONOS1_ip,response):
                    Switch_Mastership = Switch_Mastership and main.TRUE
                else:
                    Switch_Mastership = main.FALSE
            elif i>=2 and i<5:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is " + str(response))
                if re.search("tcp:"+ONOS1_ip,response):
                    Switch_Mastership = Switch_Mastership and main.TRUE
                else:
                    Switch_Mastership = main.FALSE
            elif i>=5 and i<8:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is " + str(response))
                if re.search("tcp:"+ONOS1_ip,response):
                    Switch_Mastership = Switch_Mastership and main.TRUE
                else:
                    Switch_Mastership = main.FALSE
            elif i>=8 and i<18:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is " + str(response))
                if re.search("tcp:"+ONOS1_ip,response):
                    Switch_Mastership = Switch_Mastership and main.TRUE
                else:
                    Switch_Mastership = main.FALSE
            elif i>=18 and i<28:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is " + str(response))
                if re.search("tcp:"+ONOS1_ip,response):
                    Switch_Mastership = Switch_Mastership and main.TRUE
                else:
                    Switch_Mastership = main.FALSE
            else:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is" + str(response))
                if re.search("tcp:" +ONOS1_ip,response):
                    Switch_Mastership = Switch_Mastership and main.TRUE
                else:
                    Switch_Mastership = main.FALSE

        if Switch_Mastership == main.TRUE:
            main.log.report("MasterControllers assigned correctly")
        utilities.assert_equals(expect = main.TRUE,actual=Switch_Mastership,
                onpass="MasterControllers assigned correctly")
        '''
        for i in range (1,29):
            main.Mininet1.assign_sw_controller(sw=str(i),count=5,
                    ip1=ONOS1_ip,port1=ONOS1_port,
                    ip2=ONOS2_ip,port2=ONOS2_port,
                    ip3=ONOS3_ip,port3=ONOS3_port,
                    ip4=ONOS4_ip,port4=ONOS4_port,
                    ip5=ONOS5_ip,port5=ONOS5_port)
        '''
        #REACTIVE FWD test

        main.step("Get list of hosts from Mininet")
        host_list = main.Mininet1.get_hosts()
        main.log.info(host_list)

        main.step("Get host list in ONOS format")
        host_onos_list = main.ONOS2.get_hosts_id(host_list)
        main.log.info(host_onos_list)
        #time.sleep(5)

        #We must use ping from hosts we want to add intents from 
        #to make the hosts talk
        #main.Mininet2.handle.sendline("\r")
        #main.Mininet2.handle.sendline("h4 ping 10.1.1.1 -c 1 -W 1")
        #time.sleep(3)
        #main.Mininet2.handle.sendline("h5 ping 10.1.1.1 -c 1 -W 1")
        #time.sleep(5)
        
        main.step("Pingall")
        ping_result = main.FALSE
        while ping_result == main.FALSE:
            time1 = time.time()
            ping_result = main.Mininet1.pingall()
            time2 = time.time()
            print "Time for pingall: %2f seconds" % (time2 - time1)
      
        #Start onos cli again because u might have dropped out of onos prompt to the shell prompt
        #if there was no activity
        main.ONOS2.start_onos_cli(ONOS_ip=main.params['CTRL']['ip1'])

        main.step("Get hosts")
        main.ONOS2.handle.sendline("hosts")
        main.ONOS2.handle.expect("onos>")
        hosts = main.ONOS2.handle.before
        main.log.info(hosts)

        main.step("Get all devices id")
        devices_id_list = main.ONOS2.get_all_devices_id()
        main.log.info(devices_id_list)
        
        #ONOS displays the hosts in hex format unlike mininet which does in decimal format
        #So take care while adding intents
        
        main.step("Add host-to-host intents for mininet hosts h8 and h18 or ONOS hosts h8 and h12")
        hth_intent_result = main.ONOS2.add_host_intent("00:00:00:00:00:08/-1", "00:00:00:00:00:12/-1")
        hth_intent_result = main.ONOS2.add_host_intent("00:00:00:00:00:09/-1", "00:00:00:00:00:13/-1")
        hth_intent_result = main.ONOS2.add_host_intent("00:00:00:00:00:0A/-1", "00:00:00:00:00:14/-1")
        hth_intent_result = main.ONOS2.add_host_intent("00:00:00:00:00:0B/-1", "00:00:00:00:00:15/-1")
        hth_intent_result = main.ONOS2.add_host_intent("00:00:00:00:00:0C/-1", "00:00:00:00:00:16/-1")
        hth_intent_result = main.ONOS2.add_host_intent("00:00:00:00:00:0D/-1", "00:00:00:00:00:17/-1")
        hth_intent_result = main.ONOS2.add_host_intent("00:00:00:00:00:0E/-1", "00:00:00:00:00:18/-1")
        hth_intent_result = main.ONOS2.add_host_intent("00:00:00:00:00:0F/-1", "00:00:00:00:00:19/-1")
        hth_intent_result = main.ONOS2.add_host_intent("00:00:00:00:00:10/-1", "00:00:00:00:00:1A/-1") 
        hth_intent_result = main.ONOS2.add_host_intent("00:00:00:00:00:11/-1", "00:00:00:00:00:1B/-1")

 
        
        print "_____________________________________________________________________________________"
        '''
        main.step("Add point-to-point intents for mininet hosts h8 and h18 or ONOS hosts h8 and h12")
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000003008", 1, "of:0000000000006018", 1)
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000006018", 1, "of:0000000000003008", 1)
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            main.log.info(get_intent_result)
       
        main.step("Add point-to-point intents for mininet hosts h9 and h19 or ONOS hosts h9 and h13")
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000003009", 1, "of:0000000000006019", 1)
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000006019", 1, "of:0000000000003009", 1)
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            main.log.info(get_intent_result)
        
        main.step("Add point-to-point intents for mininet hosts h10 and h20 or ONOS hosts hA and h14")
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000003010", 1, "of:0000000000006020", 1)
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000006020", 1, "of:0000000000003010", 1)
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            main.log.info(get_intent_result)
            
        main.step("Add point-to-point intents for mininet hosts h11 and h21 or ONOS hosts hB and h15")
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000003011", 1, "of:0000000000006021", 1)
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000006021", 1, "of:0000000000003011", 1)
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            main.log.info(get_intent_result)
            
        main.step("Add point-to-point intents for mininet hosts h12 and h22 or ONOS hosts hC and h16")
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000003012", 1, "of:0000000000006022", 1)
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000006022", 1, "of:0000000000003012", 1)
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            main.log.info(get_intent_result)
            
        main.step("Add point-to-point intents for mininet hosts h13 and h23 or ONOS hosts hD and h17")
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000003013", 1, "of:0000000000006023", 1)
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000006023", 1, "of:0000000000003013", 1)
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            main.log.info(get_intent_result)
            
        main.step("Add point-to-point intents for mininet hosts h14 and h24 or ONOS hosts hE and h18")
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000003014", 1, "of:0000000000006024", 1)
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000006024", 1, "of:0000000000003014", 1)
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            main.log.info(get_intent_result)
            
        main.step("Add point-to-point intents for mininet hosts h15 and h25 or ONOS hosts hF and h19")
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000003015", 1, "of:0000000000006025", 1)
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000006025", 1, "of:0000000000003015", 1)
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            main.log.info(get_intent_result)
            
        main.step("Add point-to-point intents for mininet hosts h16 and h26 or ONOS hosts h10 and h1A")
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000003016", 1, "of:0000000000006026", 1)
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000006026", 1, "of:0000000000003016", 1)
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            main.log.info(get_intent_result)
        
        main.step("Add point-to-point intents for mininet hosts h17 and h27 or ONOS hosts h11 and h1B")
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000003017", 1, "of:0000000000006027", 1)
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000006027", 1, "of:0000000000003017", 1)
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            main.log.info(get_intent_result)

        print("_______________________________________________________________________________________")
       ''' 
        #Unistall onos-app-fwd app to disable reactive forwarding
        appUninstall_result = main.ONOS2.feature_uninstall("onos-app-fwd")
        main.log.info("onos-app-fwd uninstalled")

        #After reactive forwarding is disabled, the reactive flows on switches timeout in 10-15s
        #So sleep for 15s
        time.sleep(15)
        
        flowHandle = main.ONOS2.flows()
        print "flowHandle = ", flowHandle

        count = 1
        i = 8
        Ping_Result = main.TRUE
        #while i<10:
        while i <18 :
            main.log.info("\n\nh"+str(i)+" is Pinging h" + str(i+10))
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+10))
            if ping == main.FALSE and count <5:
                count+=1
                i = 8
                Ping_Result = main.FALSE
                main.log.report("Ping between h" + str(i) + " and h" + str(i+10) + " failed. Making attempt number "+str(count) + " in 2 seconds")
                time.sleep(2)
            elif ping==main.FALSE:
                main.log.report("All ping attempts have failed")
                i=19
                Ping_Result = main.FALSE
            elif ping==main.TRUE:
                main.log.info("Ping test passed!")
                i+=1
                Ping_Result = main.TRUE
            else:
                main.log.info("Unknown error")
                Ping_Result = main.ERROR
        if Ping_Result==main.FALSE:
            main.log.report("Intents have not ben installed correctly. Cleaning up")
            main.cleanup()
            main.exit()
        if Ping_Result==main.TRUE:
            main.log.report("Intents have been installed correctly")
            
        case4_result = Switch_Mastership and Ping_Result
        utilities.assert_equals(expect=main.TRUE, actual=case4_result,
                onpass="Pingall Test successful",
                onfail="Pingall Test NOT successful")

    def CASE5(self,main) :
        import json
        from subprocess import Popen, PIPE
        from sts.topology.teston_topology import TestONTopology # assumes that sts is already in you PYTHONPATH
        #main.ONOS2.start_onos_cli(ONOS_ip=main.params['CTRL']['ip1'])
        deviceResult = main.ONOS2.devices()
        linksResult = main.ONOS2.links()
        portsResult = main.ONOS2.ports()
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
        devices_json = main.ONOS2.devices()
        links_json = main.ONOS2.links()
        ports_json = main.ONOS2.ports()
        print "devices_json= ", devices_json
        
        result1 = main.Mininet1.compare_switches(MNTopo, json.loads(devices_json))
        print "***********************"
        result2 = main.Mininet1.compare_links(MNTopo, json.loads(links_json))
        print "***********************"
        result3 = main.Mininet1.compare_ports(MNTopo, json.loads(ports_json))
            
        result = result1 and result2 and result3
        print "***********************"
        if result == main.TRUE:
            main.log.report("ONOS"+ " Topology matches MN Topology")
        utilities.assert_equals(expect=main.TRUE,actual=result,
            onpass="ONOS" + " Topology matches MN Topology",
            onfail="ONOS" + " Topology does not match MN Topology")
        Topology_Check = Topology_Check and result
        utilities.assert_equals(expect=main.TRUE,actual=Topology_Check,
            onpass="Topology checks passed", onfail="Topology checks failed")
    

    def CASE7 (self,main):
       
        ONOS1_ip = main.params['CTRL']['ip1']

        link_sleep = int(main.params['timers']['LinkDiscovery'])

        main.log.report("Killing a link to ensure that link discovery is consistent")
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
        topology_output = main.ONOS2.topology()
        topology_result = main.ONOS1.get_topology(topology_output)
        activeSwitches = topology_result['devices']
        links = topology_result['links']
        print "activeSwitches = ", type(activeSwitches)
        print "links = ", type(links)
        main.log.info("Currently there are %s switches and %s links"  %(str(activeSwitches), str(links)))

        main.step("Kill Link between s3 and s28")
        main.Mininet1.link(END1="s3",END2="s28",OPTION="down")
        time.sleep(link_sleep)
        topology_output = main.ONOS2.topology()
        Link_Down = main.ONOS1.check_status(topology_output,activeSwitches,str(int(links)-2))
        if Link_Down == main.TRUE:
            main.log.report("Link Down discovered properly")
        utilities.assert_equals(expect=main.TRUE,actual=Link_Down,
                onpass="Link Down discovered properly",
                onfail="Link down was not discovered in "+ str(link_sleep) + " seconds")
        
        main.step("Bring link between s3 and s28 back up")
        Link_Up = main.Mininet1.link(END1="s3",END2="s28",OPTION="up")
        time.sleep(link_sleep)
        topology_output = main.ONOS2.topology()
        Link_Up = main.ONOS1.check_status(topology_output,activeSwitches,str(links))
        if Link_Up == main.TRUE:
            main.log.report("Link up discovered properly")
        utilities.assert_equals(expect=main.TRUE,actual=Link_Up,
                onpass="Link up discovered properly",
                onfail="Link up was not discovered in "+ str(link_sleep) + " seconds")




        main.step("Compare ONOS Topology to MN Topology")
        Topo = TestONTopology(main.Mininet1, ctrls) # can also add Intent API info for intent operations
        MNTopo = Topo
        Topology_Check = main.TRUE
        devices_json = main.ONOS2.devices()
        links_json = main.ONOS2.links()
        ports_json = main.ONOS2.ports()
        print "devices_json= ", devices_json
        
        result1 = main.Mininet1.compare_switches(MNTopo, json.loads(devices_json))
        print "***********************"
        result2 = main.Mininet1.compare_links(MNTopo, json.loads(links_json))
        print "***********************"
        result3 = main.Mininet1.compare_ports(MNTopo, json.loads(ports_json))
            
        result = result1 and result2 and result3
        print "***********************"
        if result == main.TRUE:
            main.log.report("ONOS"+ " Topology matches MN Topology")
        utilities.assert_equals(expect=main.TRUE,actual=result,
            onpass="ONOS" + " Topology matches MN Topology",
            onfail="ONOS" + " Topology does not match MN Topology")
        Topology_Check = Topology_Check and result
        utilities.assert_equals(expect=main.TRUE,actual=Topology_Check,
            onpass="Topology checks passed", onfail="Topology checks failed")
    
        result = Link_Down and Link_Up and Topology_Check
        utilities.assert_equals(expect=main.TRUE,actual=result,
                onpass="Link failure is discovered correctly",
                onfail="Link Discovery failed")



