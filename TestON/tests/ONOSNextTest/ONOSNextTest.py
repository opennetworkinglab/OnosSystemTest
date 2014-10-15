
#Testing the basic functionality of ONOS Next
#For sanity and driver functionality excercises only.

import time
import sys
import os
import re
import time

class ONOSNextTest:
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
        
        main.step("Creating cell file")
        #params: (bench ip, cell name, mininet ip, *onos ips)
        cell_file_result = main.ONOSbench.create_cell_file(
                "10.128.20.10", "temp_cell_2", "10.128.10.90",
                "10.128.10.11", "10.128.10.12", "10.128.10.13")

        main.step("Applying cell variable to environment")
        cell_result = main.ONOSbench.set_cell(cell_name)
        verify_result = main.ONOSbench.verify_cell()
        
        main.step("Git checkout and pull master")
        main.ONOSbench.git_checkout("master")
        git_pull_result = main.ONOSbench.git_pull()


        main.step("Using mvn clean & install")
        clean_install_result = main.ONOSbench.clean_install()
        #clean_install_result = main.TRUE

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
        
        cell_name = main.params['ENV']['cellName']
        ONOS1_ip = main.params['CTRL']['ip1']
        
        main.case("Testing the ONOS-cli")
        
        main.step("Set cell for ONOS-cli environment")
        main.ONOScli.set_cell(cell_name)

        main.step("Start ONOS-cli")
        main.ONOScli.start_onos_cli(ONOS1_ip)

        main.step("issue command: onos:topology")
        topology_obj = main.ONOScli.onos_topology()

        main.step("issue various feature:install <str> commands")
        main.ONOScli.feature_install("onos-app-fwd")
        main.ONOScli.feature_install("onos-rest")

        main.step("Add a bad node")
        node_result = main.ONOScli.add_node("111", "10.128.20.")
        if node_result == main.TRUE:
            main.log.info("Node successfully added")

        main.step("Add a correct node")
        node_result = main.ONOScli.add_node("111", "10.128.20.12")

        main.step("Assign switches and list devices")
        for i in range(1,8):
            main.Mininet2.handle.sendline("sh ovs-vsctl set-controller s"+str(i)+
                    " tcp:10.128.20.11")
            main.Mininet2.handle.expect("mininet>")
        #Need to sleep to allow switch add processing
        time.sleep(5)
        list_result = main.ONOScli.devices()
        main.log.info(list_result)

        main.step("Get all devices id")
        devices_id_list = main.ONOScli.get_all_devices_id()
        main.log.info(devices_id_list)

        main.step("Get path and cost between device 1 and 7")
        (path, cost) = main.ONOScli.paths(devices_id_list[0], devices_id_list[6])
        main.log.info("Path: "+str(path))
        main.log.info("Cost: "+str(cost))
    
######
#jhall@onlab.us
#andrew@onlab.us
######
