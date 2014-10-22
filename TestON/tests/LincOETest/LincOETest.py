#LincOETest
#
#Packet-Optical Intent Testing
#
#andrew@onlab.us


import time
import sys
import os
import re

class LincOETest:
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
        import time

        cell_name = main.params['ENV']['cellName']

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS1_port = main.params['CTRL']['port1']
        
        git_pull_trigger = main.params['GIT']['autoPull']
        git_checkout_branch = main.params['GIT']['checkout']

        main.case("Setting up test environment")
        
        main.step("Creating cell file")
        #params: (bench ip, cell name, mininet ip, *onos ips)
        cell_file_result = main.ONOSbench.create_cell_file(
                "10.128.20.10", cell_name, "10.128.10.90",
                "onos-core-trivial,onos-app-fwd",
                "10.128.174.1")

        main.step("Applying cell variable to environment")
        #cell_result = main.ONOSbench.set_cell(cell_name)
        cell_result = main.ONOSbench.set_cell("temp_cell_2")
        verify_result = main.ONOSbench.verify_cell()
       
        if git_pull_trigger == 'on':
            main.step("Git checkout and pull master")
            main.ONOSbench.git_checkout(git_checkout_branch)
            git_pull_result = main.ONOSbench.git_pull()
        else:
            main.log.info("Git checkout and pull skipped by config")
            git_pull_result = main.TRUE

        main.step("Using mvn clean & install")
        #clean_install_result = main.ONOSbench.clean_install()
        clean_install_result = main.TRUE

        main.step("Creating ONOS package")
        package_result = main.ONOSbench.onos_package()

        main.step("Installing ONOS package")
        onos_install_result = main.ONOSbench.onos_install()
        onos1_isup = main.ONOSbench.isup()
   
        main.step("Starting ONOS service")
        start_result = main.ONOSbench.onos_start(ONOS1_ip)

        case1_result = (clean_install_result and package_result and\
                cell_result and verify_result and onos_install_result and\
                onos1_isup and start_result )
        utilities.assert_equals(expect=main.TRUE, actual=case1_result,
                onpass="Test startup successful",
                onfail="Test startup NOT successful")

        time.sleep(10)


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
        
        main.step("Testing check_status")
        check_status_results =  main.ONOSbench.check_status(ONOS1_ip, 4, 6)
        main.log.info("Results of check_status " + str(check_status_results))

        main.step("Sending command 'onos -w <onos-ip> bundle:list'")
        cmdstr3 = "bundle:list"
        cmd_result3 = main.ONOSbench.onos_cli(ONOS1_ip, cmdstr3)
        main.log.info("onos command returned: "+cmd_result3)
        case3_result = (cmd_result1 and cmd_result2 and\
                check_status_results and cmd_result3 )
        utilities.assert_equals(expect=main.TRUE, actual=case3_result,
                onpass="Test case 3 successful",
                onfail="Test case 3 NOT successful")

    def CASE4(self, main):
        import re
        import time
        main.case("Pingall Test(No intents are added)")
        main.step("Assigning switches to controllers")
        for i in range(1,5): #1 to (num of switches +1)
            main.Mininet1.assign_sw_controller(sw=str(i), 
                    ip1=ONOS1_ip, port1=ONOS1_port)
        switch_mastership = main.TRUE
        for i in range (1,5):
            response = main.Mininet1.get_sw_controller("s"+str(i))
            print("Response is " + str(response))
            if re.search("tcp:"+ONOS1_ip,response):
                switch_mastership = switch_mastership and main.TRUE
            else:
                switch_mastership = main.FALSE

        #REACTIVE FWD test
        main.step("Pingall")
        ping_result = main.FALSE
        while ping_result == main.FALSE:
            time1 = time.time()
            ping_result = main.Mininet1.pingall()
            time2 = time.time()
            print "Time for pingall: %2f seconds" % (time2 - time1)
      
        case4_result = switch_mastership and ping_result
        utilities.assert_equals(expect=main.TRUE, actual=case4_result,
                onpass="Pingall Test successful",
                onfail="Pingall Test NOT successful")

    def CASE5(self, main):
        '''
        Test the ONOS-cli functionality
        
        Below are demonstrations of what the 
        ONOS cli driver functions can be used for.
        '''
        import time
        import json

        cell_name = main.params['ENV']['cellName']
        ONOS1_ip = main.params['CTRL']['ip1']
        
        main.case("Testing the ONOS-cli")
        
        main.step("Set cell for ONOS-cli environment")
        #main.ONOScli.set_cell(cell_name)
        main.ONOScli.set_cell("temp_cell_2")

        main.step("Start ONOS-cli")
        main.ONOScli.start_onos_cli(ONOS1_ip)

        main.step("issue command: onos:topology")
        topology_obj = main.ONOScli.topology()

        main.step("issue various feature:install <str> commands")
        #main.ONOScli.feature_install("onos-app-fwd")
        #main.ONOScli.feature_install("onos-rest")

        main.step("Add a bad node")
        node_result = main.ONOScli.add_node("111", "10.128.20.")
        if node_result == main.TRUE:
            main.log.info("Node successfully added")

        main.step("Add a correct node")
        node_result = main.ONOScli.add_node("111", "10.128.174.2")

        main.step("Assign switches and list devices")
        for i in range(1,8):
            main.Mininet2.handle.sendline("sh ovs-vsctl set-controller s"+str(i)+
                    " tcp:10.128.174.1")
            main.Mininet2.handle.expect("mininet>")
        #Need to sleep to allow switch add processing
        time.sleep(5)
        list_result = main.ONOScli.devices(json_format=False)
        main.log.info(list_result)

        main.step("Get all devices id")
        devices_id_list = main.ONOScli.get_all_devices_id()
        main.log.info(devices_id_list)

        main.step("Get path and cost between device 1 and 7")
        (path, cost) = main.ONOScli.paths(devices_id_list[0], devices_id_list[6])
        main.log.info("Path: "+str(path))
        main.log.info("Cost: "+str(cost))

        main.step("Get nodes currently visible")
        nodes_str = main.ONOScli.nodes()
        main.log.info(nodes_str)

        main.step("Get all nodes id's")
        node_id_list = main.ONOScli.get_all_nodes_id()
        main.log.info(node_id_list)

        main.step("Set device "+str(devices_id_list[0])+" to role: standby")
        device_role_result = main.ONOScli.device_role(
                devices_id_list[0], node_id_list[0], "standby")
        if device_role_result == main.TRUE:
            main.log.report("Device role successfully set")

        main.step("Revert device role to master")
        device_role = main.ONOScli.device_role(
                devices_id_list[0], node_id_list[0], "master")

        main.step("Check devices / role again")
        dev_result = main.ONOScli.devices(json_format=False)
        main.log.info(dev_result)
       
        #Sample steps to push intents ***********
        # * Obtain host id in ONOS format 
        # * Push intents
        main.step("Get list of hosts from Mininet")
        host_list = main.Mininet2.get_hosts()
        main.log.info(host_list)

        main.step("Get host list in ONOS format")
        host_onos_list = main.ONOScli.get_hosts_id(host_list)
        main.log.info(host_onos_list)

        time.sleep(5)

        #We must use ping from hosts we want to add intents from 
        #to make the hosts talk
        #main.Mininet2.handle.sendline("\r")
        #main.Mininet2.handle.sendline("h4 ping 10.1.1.1 -c 1 -W 1")
        #time.sleep(3)
        #main.Mininet2.handle.sendline("h5 ping 10.1.1.1 -c 1 -W 1")
        #time.sleep(5)

        main.ONOScli.feature_install("onos-app-fwd")
        
        main.Mininet2.pingall()

        time.sleep(5)

        main.step("Get hosts")
        main.ONOScli.handle.sendline("hosts")
        main.ONOScli.handle.expect("onos>")
        hosts = main.ONOScli.handle.before
        main.log.info(hosts)

        main.step("Install host-to-host-intents")
        intent_install1 = main.ONOScli.add_host_intent(
                host_onos_list[0], host_onos_list[1])
        intent_install2 = main.ONOScli.add_host_intent(
                host_onos_list[2], host_onos_list[3])
        intent_install3 = main.ONOScli.add_host_intent(
                host_onos_list[4], host_onos_list[5])

        main.log.info(intent_install1)
        main.log.info(intent_install2)
        main.log.info(intent_install3)

        main.step("Get intents installed on ONOS")
        get_intent_result = main.ONOScli.intents()
        main.log.info(get_intent_result)
        #****************************************

        #Sample steps to delete intents ********
        main.step("Get all intent id's")
        intent_id = main.ONOScli.get_all_intents_id()
        main.log.info(intent_id)

        main.step("Remove specified intent id: "+str(intent_id[0]))
        intent_result = main.ONOScli.remove_intent(intent_id[0])
        main.log.info(intent_result)

        main.step("Check installed intents again")
        get_intent_result = main.ONOScli.intents()
        main.log.info(get_intent_result)
        #***************************************

        #Sample steps to add point-to-point intents*
        main.step("Add point-to-point intents")
        ptp_intent_result = main.ONOScli.add_point_intent(
                devices_id_list[0], 1, devices_id_list[1], 2)
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOScli.intents()
            main.log.info("Point to point intent install successful")
            main.log.info(get_intent_result)
        #*******************************************

        main.step("Print intents in json format")
        intents = main.ONOScli.intents(json_format = True)
        main.log.info(intents)

        main.step("Add eth options in point-to-point intent")
        ptp_eth = main.ONOScli.add_point_intent(
                devices_id_list[2], 1, devices_id_list[3], 2,
                ethSrc = "00:02", ethDst = "00:03")
        main.log.info(ptp_eth)

        main.step("Print intents with eth options")
        intents = main.ONOScli.intents()
        main.log.info(intents)
######
#jhall@onlab.us
#andrew@onlab.us
######
