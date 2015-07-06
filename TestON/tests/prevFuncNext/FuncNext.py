
#Testing the basic functionality of ONOS Next
#For sanity and driver functionality excercises only.

import time
import sys
import os
import re
import time

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
        version_result = main.ONOSbench.get_version()

        main.step("Using mvn clean & install")
        #clean_install_result = main.ONOSbench.clean_install()
        #clean_install_result = main.TRUE

        main.step("Applying cell variable to environment")
        cell_result = main.ONOSbench.set_cell(cell_name)
        verify_result = main.ONOSbench.verify_cell()
        cell_result = main.ONOS2.set_cell(cell_name)
        #verify_result = main.ONOS2.verify_cell()
        main.ONOS2.start_onos_cli(ONOS_ip=main.params['CTRL']['ip1'])
        
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
        '''
        main.step("Add point-to-point intents")
        ptp_intent_result = main.ONOS2.add_point_intent(
            devices_id_list[0], 1, devices_id_list[1], 2)
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            main.log.info(get_intent_result)
        '''

        case4_result = Switch_Mastership and ping_result
        utilities.assert_equals(expect=main.TRUE, actual=case4_result,
                onpass="Pingall Test successful",
                onfail="Pingall Test NOT successful")

    def CASE5(self,main) :
        import time
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
        '''for n in range(1,6):
            result = main.Mininet1.compare_topo(MNTopo,
                    main.ONOS1.get_json(main.params['CTRL']['ip'+str(n)]+":"+ \
                        main.params['CTRL']['restPort'+str(n)]+main.params['TopoRest']))
            if result == main.TRUE:
                main.log.report("ONOS"+str(n) + " Topology matches MN Topology")
            utilities.assert_equals(expect=main.TRUE,actual=result,
                    onpass="ONOS" + str(n) + " Topology matches MN Topology",
                    onfail="ONOS" + str(n) + " Topology does not match MN Topology")
            Topology_Check = Topology_Check and result
        utilities.assert_equals(expect=main.TRUE,actual=Topology_Check,
                onpass="Topology checks passed", onfail="Topology checks failed")
        '''


