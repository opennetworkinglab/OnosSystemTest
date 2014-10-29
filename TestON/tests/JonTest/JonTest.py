
#Testing the basic functionality of ONOS Next
#For sanity and driver functionality excercises only.

import time
import sys
import os
import re

class JonTest:
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
        
        PULL_CODE = False
        if main.params['Git'] == 'True':
            PULL_CODE = True
        cell_name = main.params['ENV']['cellName']
        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS1_port = main.params['CTRL']['port1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS2_port = main.params['CTRL']['port2']
        
        main.case("Setting up test environment")
        
        main.step("Applying cell variable to environment")
        cell_result = main.ONOSbench.set_cell(cell_name)
        #cell_result = main.ONOSbench.set_cell("temp_cell_2")
        verify_result = main.ONOSbench.verify_cell()

        if PULL_CODE:
            main.step("Git checkout and pull master")
            #main.log.report("Skipping git pull")
            main.ONOSbench.git_checkout("master")
            git_pull_result = main.ONOSbench.git_pull()
            main.log.report(main.ONOSbench.get_version())

            main.step("Using mvn clean & install")
            clean_install_result = main.FALSE
            if git_pull_result == main.TRUE:
                clean_install_result = main.ONOSbench.clean_install()
            else:
                main.log.report("did not pull new code so skipping mvn clean install")

        main.step("Creating ONOS package")
        package_result = main.ONOSbench.onos_package()

        main.step("Installing ONOS package")
        onos1_install_result = main.ONOSbench.onos_install(options="-f", node=ONOS1_ip)
        onos2_install_result = main.ONOSbench.onos_install(options="-f", node=ONOS2_ip)
        onos1_isup = main.ONOSbench.isup(ONOS1_ip)
        onos2_isup = main.ONOSbench.isup(ONOS2_ip)
   
        main.step("Starting ONOS service")
        start_result = main.TRUE
        #start_result = main.ONOSbench.onos_start(ONOS1_ip)

        main.ONOScli1.start_onos_cli(ONOS1_ip)
        main.ONOScli2.start_onos_cli(ONOS2_ip)

        case1_result = (clean_install_result and package_result and\
                cell_result and verify_result and onos1_install_result and\
                onos2_install_result and onos1_isup and onos2_isup )
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
        check_status_results = main.FALSE
        topology_result = main.ONOScli1.topology()
        check_status_results =  main.ONOSbench.check_status(topology_result, 4, 6)
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
            main.Mininet1.assign_sw_controller(sw=str(i),count=2, 
                    ip1=ONOS1_ip, port1=ONOS1_port,
                    ip2=ONOS2_ip, port2=ONOS2_port)

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
        main.ONOScli.set_cell(cell_name)

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
        node_result = main.ONOScli.add_node("111", "10.128.20.12")

        main.step("Assign switches and list devices")
        for i in range(1,8):
            main.Mininet1.handle.sendline("sh ovs-vsctl set-controller s"+str(i)+
                    " tcp:10.128.20.11")
            main.Mininet1.handle.expect("mininet>")
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
        dev_result = main.ONOScli.devices()
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

        main.step("Ensure that reactive forwarding is installed")
        feature_result = main.ONOScli.feature_install("onos-app-fwd")

        time.sleep(5)

        main.Mininet2.handle.sendline("\r")
        main.Mininet2.handle.sendline("h4 ping h5 -c 1")

        time.sleep(5)

        main.step("Get hosts")
        main.ONOScli.handle.sendline("hosts")
        main.ONOScli.handle.expect("onos>")
        hosts = main.ONOScli.handle.before
        main.log.info(hosts)

        main.step("Install host-to-host-intents between h4 and h5")
        intent_install = main.ONOScli.add_host_intent(
                host_onos_list[3], host_onos_list[4])
        main.log.info(intent_install)

        main.step("Uninstall reactive forwarding to test host-to-host intent")
        main.ONOScli.feature_uninstall("onos-app-fwd")

        main.step("Get intents installed on ONOS")
        get_intent_result = main.ONOScli.intents()
        main.log.info(get_intent_result)
        #****************************************


    def CASE7(self, main):
        '''
        Test compare topo functions
        '''
        import sys
        sys.path.append("/home/admin/sts") # Trying to remove some dependancies, #FIXME add this path to params
        from sts.topology.teston_topology import TestONTopology # assumes that sts is already in you PYTHONPATH
        import json

        main.step("Create TestONTopology object")
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
        MNTopo = TestONTopology(main.Mininet1, ctrls) # can also add Intent API info for intent operations

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']

    
        main.step("Collecting topology information from ONOS")
        devices1 = main.ONOScli1.devices()
        devices2 = main.ONOScli2.devices()
        switch1 = main.ONOScli1.get_device("0000000000000001")
        hosts1 = main.ONOScli1.hosts()
        hosts2 = main.ONOScli2.hosts()
        host1 = main.ONOScli1.get_host("00:00:00:00:00:01")
        #print json.dumps(json.loads(hosts1), sort_keys=True,indent=4,separators=(',', ': '))
        #print json.dumps(json.loads(hosts2), sort_keys=True,indent=4,separators=(',', ': '))
        #print json.dumps(host1, sort_keys=True,indent=4,separators=(',', ': '))
        ports1 = main.ONOScli1.ports()
        ports2 = main.ONOScli2.ports()
        links1 = main.ONOScli1.links()
        links2 = main.ONOScli2.links()


        main.step("Comparing ONOS topology to MN")
        #results =  main.Mininet1.compare_topo(MNTopo, json.loads(devices))
        switches_results1 =  main.Mininet1.compare_switches(MNTopo, json.loads(devices1))
        utilities.assert_equals(expect=main.TRUE, actual=switches_results1,
                onpass="ONOS1 Switches view is correct",
                onfail="ONOS1 Switches view is incorrect")

        switches_results2 =  main.Mininet1.compare_switches(MNTopo, json.loads(devices2))
        utilities.assert_equals(expect=main.TRUE, actual=switches_results2,
                onpass="ONOS2 Switches view is correct",
                onfail="ONOS2 Switches view is incorrect")


        ports_results1 =  main.Mininet1.compare_ports(MNTopo, json.loads(ports1))
        utilities.assert_equals(expect=main.TRUE, actual=ports_results1,
                onpass="ONOS1 Ports view is correct",
                onfail="ONOS1 Ports view is incorrect")

        ports_results2 =  main.Mininet1.compare_ports(MNTopo, json.loads(ports2))
        utilities.assert_equals(expect=main.TRUE, actual=ports_results2,
                onpass="ONOS2 Ports view is correct",
                onfail="ONOS2 Ports view is incorrect")

        links_results1 =  main.Mininet1.compare_links(MNTopo, json.loads(links1))
        utilities.assert_equals(expect=main.TRUE, actual=links_results1,
                onpass="ONOS1 Links view is correct",
                onfail="ONOS1 Links view is incorrect")

        links_results2 =  main.Mininet1.compare_links(MNTopo, json.loads(links2))
        utilities.assert_equals(expect=main.TRUE, actual=links_results2,
                onpass="ONOS2 Links view is correct",
                onfail="ONOS2 Links view is incorrect")

        topo_result = switches_results1 and switches_results2 \
                and ports_results1 and ports_results2\
                and links_results1 and links_results2
        utilities.assert_equals(expect=main.TRUE, actual=topo_result,
                onpass="Topology Check Test successful",
                onfail="Topology Check Test NOT successful")

    def CASE8(self, main):
        '''
        try doing some role assignments
        '''
        import time
        print main.ONOScli1.devices()
        print main.ONOScli1.device_role("of:0000000000000001", "    ", "none")
        time.sleep(1)
        roles = main.ONOScli1.roles()
        roles2 = main.ONOScli2.roles()
        print roles
        print roles2
        print main.ONOScli1.get_role("00001")

        print main.ONOScli1.devices()
        print main.ONOScli1.device_role("of:0000000000000001", "10.128.30.11", "master")
        time.sleep(1)
        roles = main.ONOScli1.roles()
        roles2 = main.ONOScli2.roles()
        print roles
        print roles2
        print main.ONOScli1.get_role("00001")

        print main.ONOScli1.devices()
        print main.ONOScli1.device_role("of:0000000000000001", "10.128.30.11", "standby")
        time.sleep(1)
        roles = main.ONOScli1.roles()
        roles2 = main.ONOScli2.roles()
        print roles
        print roles2
        print main.ONOScli1.get_role("00001")

        print main.ONOScli1.devices()
        print main.ONOScli1.device_role("of:0000000000000001", "10.128.30.11", "MASTER")
        time.sleep(1)
        roles = main.ONOScli1.roles()
        roles2 = main.ONOScli2.roles()
        print roles
        print roles2
        print main.ONOScli1.get_role("00001")
        print main.ONOScli1.devices()

    def CASE9(self, main):
        '''
        Bring Links down
        '''
        main.Mininet1.link(END1="s1", END2="s2", OPTION="down")
        main.Mininet1.link(END1="s1", END2="s3", OPTION="down")
        main.Mininet1.link(END1="s1", END2="s4", OPTION="down")




######
#jhall@onlab.us
#andrew@onlab.us
######
