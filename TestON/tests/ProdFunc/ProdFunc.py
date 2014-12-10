
#Testing the basic functionality of ONOS Next
#For sanity and driver functionality excercises only.

import time
import sys
import os
import re
import json

time.sleep(1)
class ProdFunc:
    def __init__(self):
        self.default = ''

    def CASE1(self, main):
        '''
        Startup sequence:
        cell <name>
        onos-verify-cell
        onos-remove-raft-log
        git pull
        mvn clean install
        onos-package
        onos-install -f
        onos-wait-for-start
        '''
        
        cell_name = main.params['ENV']['cellName']
        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS1_port = main.params['CTRL']['port1']
        
        main.case("Setting up test environment")
        main.log.report("This testcase is testing setting up test environment")
        main.log.report("__________________________________") 

        main.step("Applying cell variable to environment")
        cell_result = main.ONOSbench.set_cell(cell_name)
        verify_result = main.ONOSbench.verify_cell()
        
        main.step("Removing raft logs before a clen installation of ONOS")
        main.ONOSbench.onos_remove_raft_logs()

        main.step("Git checkout and pull master and get version")
        main.ONOSbench.git_checkout("master")
        git_pull_result = main.ONOSbench.git_pull()
        main.log.info("git_pull_result = " +git_pull_result)
        version_result = main.ONOSbench.get_version(report=True)
    
        if git_pull_result == 1:
            main.step("Using mvn clean & install")
            clean_install_result = main.ONOSbench.clean_install()
            #clean_install_result = main.TRUE
        elif git_pull_result == 0:
            main.log.report("Git Pull Failed, look into logs for detailed reason")
            main.cleanup()
            main.exit() 
         
        main.step("Creating ONOS package")
        package_result = main.ONOSbench.onos_package()


        main.step("Installing ONOS package")
        onos_install_result = main.ONOSbench.onos_install()
        if onos_install_result == main.TRUE:
            main.log.report("Installing ONOS package successful")
        else:
            main.log.report("Installing ONOS package failed")

        onos1_isup = main.ONOSbench.isup()
        if onos1_isup == main.TRUE:
            main.log.report("ONOS instance is up and ready")  
        else:
            main.log.report("ONOS instance may not be up")  
       
        main.step("Starting ONOS service")
        start_result = main.ONOSbench.onos_start(ONOS1_ip)
        
        main.ONOS2.start_onos_cli(ONOS_ip=main.params['CTRL']['ip1'])        

        case1_result = (package_result and\
                cell_result and verify_result and onos_install_result and\
                onos1_isup and start_result )
        utilities.assert_equals(expect=main.TRUE, actual=case1_result,
                onpass="Test startup successful",
                onfail="Test startup NOT successful")

    def CASE2(self, main) :
        '''  
        Switch Down
        '''
        #NOTE: You should probably run a topology check after this
        import time 
        import json
 
        main.case("Switch down discovery")
        main.log.report("This testcase is testing a switch down discovery")
        main.log.report("__________________________________")

        switch_sleep = int(main.params['timers']['SwitchDiscovery'])

        description = "Killing a switch to ensure it is discovered correctly"
        main.log.report(description)
        main.case(description)

        #TODO: Make this switch parameterizable
        main.step("Kill s28 ")
        main.log.report("Deleting s28")
        #FIXME: use new dynamic topo functions
        main.Mininet1.del_switch("s28")
        main.log.info("Waiting " + str(switch_sleep) + " seconds for switch down to be discovered")
        time.sleep(switch_sleep)
        #Peek at the deleted switch
        device = main.ONOS2.get_device(dpid="0028")
        print "device = ", device
        if device[u'available'] == 'False':
            case2_result = main.FALSE
        else:
            case2_result = main.TRUE
        utilities.assert_equals(expect=main.TRUE, actual=case2_result,
                onpass="Switch down discovery successful",
                onfail="Switch down discovery failed")

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


    def CASE20(self):
        '''
            Exit from mininet cli
            reinstall ONOS
        '''
        cell_name = main.params['ENV']['cellName']
        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS1_port = main.params['CTRL']['port1']
        
        main.log.report("This testcase exits the mininet cli and reinstalls ONOS to switch over to Packet Optical topology")
        main.log.report("_____________________________________________")
        main.case("Disconnecting mininet and restarting ONOS")
        main.step("Disconnecting mininet and restarting ONOS")
        mininet_disconnect = main.Mininet1.disconnect()

        main.step("Removing raft logs before a clen installation of ONOS")
        main.ONOSbench.onos_remove_raft_logs()

        main.step("Applying cell variable to environment")
        cell_result = main.ONOSbench.set_cell(cell_name)
        verify_result = main.ONOSbench.verify_cell()

        onos_install_result = main.ONOSbench.onos_install()
        if onos_install_result == main.TRUE:
            main.log.report("Installing ONOS package successful")
        else:
            main.log.report("Installing ONOS package failed")

        onos1_isup = main.ONOSbench.isup()
        if onos1_isup == main.TRUE:
            main.log.report("ONOS instance is up and ready")
        else:
            main.log.report("ONOS instance may not be up")

        main.step("Starting ONOS service")
        start_result = main.ONOSbench.onos_start(ONOS1_ip)
      
        main.ONOS2.start_onos_cli(ONOS_ip=main.params['CTRL']['ip1']) 
        print "mininet_disconnect =", mininet_disconnect
        print "onos_install_result =", onos_install_result
        print "onos1_isup =", onos1_isup
        print "start_result =", start_result
 
        case20_result = mininet_disconnect and cell_result and onos_install_result and onos1_isup and start_result
        utilities.assert_equals(expect=main.TRUE, actual=case20_result,
                onpass="Exiting functionality mininet topology and reinstalling ONOS successful",
                onfail="Exiting functionality mininet topology and reinstalling ONOS failed") 

    def CASE21(self, main):
        import time
        '''
            On ONOS bench, run this command: ./~/ONOS/tools/test/bin/onos-topo-cfg
            which starts the rest and copies the links json file to the onos instance
            Note that in case of Packet Optical, the links are not learnt from the topology, instead the links are learnt 
            from the json config file
        ''' 
        main.log.report("This testcase starts the packet layer topology and REST")
        main.log.report("_____________________________________________")
        main.case("Starting LINC-OE and other components")
        main.step("Starting LINC-OE and other components")
        start_console_result = main.LincOE1.start_console()
        optical_mn_script = main.LincOE2.run_optical_mn_script()
        onos_topo_cfg_result = main.ONOSbench.run_onos_topo_cfg(instance_name = main.params['CTRL']['ip1'], json_file = main.params['OPTICAL']['jsonfile'])
            
        print "start_console_result =",start_console_result 
        print "optical_mn_script = ",optical_mn_script 
        print "onos_topo_cfg_result =",onos_topo_cfg_result 

        case21_result = start_console_result and optical_mn_script and onos_topo_cfg_result
        utilities.assert_equals(expect=main.TRUE, actual=case21_result,
                onpass="Packet optical topology spawned successsfully",
                onfail="Packet optical topology spawning failed") 


    def CASE22(self, main):
        '''
            Curretly we use, 4 linear switch optical topology and 2 packet layer mininet switches each with one host.
             Therefore, the roadmCount variable = 4, packetLayerSWCount variable = 2, hostCount =2
            and this is hardcoded in the testcase. If the topology changes, these hardcoded values need to be changed
        '''

        main.log.report("This testcase compares the optical+packet topology against what is expected")
        main.case("Topology comparision")
        main.step("Topology comparision")
        main.ONOS3.start_onos_cli(ONOS_ip=main.params['CTRL']['ip1'])
        devices_result = main.ONOS3.devices(json_format = False)

        print "devices_result = ", devices_result
        devices_linewise = devices_result.split("\n")
        devices_linewise = devices_linewise[1:-1]
        roadmCount = 0
        packetLayerSWCount = 0
        for line in devices_linewise:
            components = line.split(",")
            availability = components[1].split("=")[1]
            type = components[3].split("=")[1]
            if availability == 'true' and type == 'ROADM':
                roadmCount += 1
            elif availability == 'true' and type =='SWITCH':
                packetLayerSWCount += 1
        if roadmCount == 4:
            print "Number of Optical Switches = %d and is correctly detected" %roadmCount
            main.log.info ("Number of Optical Switches = " +str(roadmCount) +" and is correctly detected")
            opticalSW_result = main.TRUE
        else:
            print "Number of Optical Switches = %d and is wrong" %roadCount
            main.log.info ("Number of Optical Switches = " +str(roadmCount) +" and is wrong")
            opticalSW_result = main.FALSE

        if packetLayerSWCount == 2:
            print "Number of Packet layer or mininet Switches = %d and is correctly detected" %packetLayerSWCount
            main.log.info("Number of Packet layer or mininet Switches = " +str(packetLayerSWCount) + " and is correctly detected")
            packetSW_result = main.TRUE
        else:
            print "Number of Packet layer or mininet Switches = %d and is wrong" %packetLayerSWCount
            main.log.info("Number of Packet layer or mininet Switches = " +str(packetLayerSWCount) + " and is wrong")
            packetSW_result = main.FALSE
        print "_________________________________"
        
        links_result = main.ONOS3.links(json_format = False)
        print "links_result = ", links_result
        print "_________________________________"
        
        #NOTE:Since only point intents are added, there is no requirement to discover the hosts
                #Therfore, the below portion of the code is commented.
        '''
        #Discover hosts using pingall
        pingall_result = main.LincOE2.pingall()    
    
        hosts_result = main.ONOS3.hosts(json_format = False)
        main.log.info("hosts_result = "+hosts_result)   
        main.log.info("_________________________________")
        hosts_linewise = hosts_result.split("\n")
        hosts_linewise = hosts_linewise[1:-1]
        hostCount = 0
        for line in hosts_linewise:
            hostid = line.split(",")[0].split("=")[1]
            hostCount +=1
        if hostCount ==2:
            print "Number of hosts = %d and is correctly detected" %hostCount
            main.log.info("Number of hosts = " + str(hostCount) +" and is correctly detected")
            hostDiscovery = main.TRUE
        else:
            print "Number of hosts = %d and is wrong" %hostCount
            main.log.info("Number of hosts = " + str(hostCount) +" and is wrong")
            hostDiscovery = main.FALSE
        '''

        case22_result = opticalSW_result and packetSW_result
        utilities.assert_equals(expect=main.TRUE, actual=case22_result,
                onpass="Packet optical topology discovery successful",
                onfail="Packet optical topology discovery failed")

    def CASE23(self, main):
        import time
        '''
            Add bidirectional point intents between 2 packet layer(mininet) devices and 
            ping mininet hosts
        '''
        main.log.report("This testcase adds bidirectional point intents between 2 packet layer(mininet) devices and ping mininet hosts")
        main.case("Topology comparision")
        main.step("Adding point intents")
        ptp_intent_result = main.ONOS3.add_point_intent("of:0000ffffffff0001/1", "of:0000ffffffff0002/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS3.intents(json_format = False)
            main.log.info("Point to point intent install successful")

        ptp_intent_result = main.ONOS3.add_point_intent("of:0000ffffffff0002/1", "of:0000ffffffff0001/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS3.intents(json_format = False)
            main.log.info("Point to point intent install successful")

        time.sleep(10)
        flowHandle = main.ONOS3.flows()
        main.log.info("flows :" + flowHandle)

        # Sleep for 30 seconds to provide time for the intent state to change
        time.sleep(30)
        intentHandle = main.ONOS3.intents(json_format = False)        
        main.log.info("intents :" + intentHandle)        
 
        Ping_Result = main.TRUE
        count = 1
        main.log.info("\n\nh1 is Pinging h2")
        ping = main.LincOE2.pingHostOptical(src="h1", target="h2")
        #ping = main.LincOE2.pinghost()
        if ping == main.FALSE and count<5:
            count+=1
            Ping_Result = main.FALSE
            main.log.info("Ping between h1 and h2  failed. Making attempt number "+str(count) + " in 2 seconds")
            time.sleep(2)
        elif ping==main.FALSE:
            main.log.info("All ping attempts between h1 and h2 have failed")
            Ping_Result = main.FALSE
        elif ping==main.TRUE:
            main.log.info("Ping test between h1 and h2 passed!")
            Ping_Result = main.TRUE
        else:
            main.log.info("Unknown error")
            Ping_Result = main.ERROR
        
        if Ping_Result==main.FALSE:
            main.log.report("Point intents for packet optical have not ben installed correctly. Cleaning up")
        if Ping_Result==main.TRUE:
            main.log.report("Point Intents for packet optical have been installed correctly")

        case23_result = Ping_Result
        utilities.assert_equals(expect=main.TRUE, actual=case23_result,
                onpass="Point intents addition for packet optical and Pingall Test successful",
                onfail="Point intents addition for packet optical and Pingall Test NOT successful")



    def CASE24(self, main):
        import time
        import json
        '''
            Test Rerouting of Packet Optical by bringing a port down (port 22) of a switch(switchID=1), so that link (between switch1 port22 - switch4-port30) is inactive
            and do a ping test. If rerouting is successful, ping should pass. also check the flows
        '''
        main.log.report("This testcase tests rerouting and pings mininet hosts")
        main.case("Test rerouting and pings mininet hosts")
        main.step("Bring a port down and verify the link state")
        main.LincOE1.port_down(sw_id="1", pt_id="22") 
        links_nonjson = main.ONOS3.links(json_format = False)
        main.log.info("links = " +links_nonjson)

        links = main.ONOS3.links()
        main.log.info("links = " +links)
        
        links_result = json.loads(links)
        links_state_result = main.FALSE
        for item in links_result:
            if item['src']['device'] == "of:0000ffffffffff01" and item['src']['port'] == "22":
                if item['dst']['device'] == "of:0000ffffffffff04" and item['dst']['port'] == "30":
                    links_state = item['state']
                    if links_state == "INACTIVE":
                        main.log.info("Links state is inactive as expected due to one of the ports being down")
                        main.log.report("Links state is inactive as expected due to one of the ports being down")
                        links_state_result = main.TRUE
                        break
                    else:
                        main.log.info("Links state is not inactive as expected")
                        main.log.report("Links state is not inactive as expected")
                        links_state_result = main.FALSE

        print "links_state_result = ", links_state_result
        time.sleep(10)
        flowHandle = main.ONOS3.flows()
        main.log.info("flows :" + flowHandle)

        main.step("Verify Rerouting by a ping test")
        Ping_Result = main.TRUE
        count = 1        
        main.log.info("\n\nh1 is Pinging h2")
        ping = main.LincOE2.pingHostOptical(src="h1", target="h2")
        #ping = main.LincOE2.pinghost()
        if ping == main.FALSE and count<5:
            count+=1
            Ping_Result = main.FALSE
            main.log.info("Ping between h1 and h2  failed. Making attempt number "+str(count) + " in 2 seconds")
            time.sleep(2)
        elif ping==main.FALSE:
            main.log.info("All ping attempts between h1 and h2 have failed")
            Ping_Result = main.FALSE
        elif ping==main.TRUE:
            main.log.info("Ping test between h1 and h2 passed!")
            Ping_Result = main.TRUE
        else:
            main.log.info("Unknown error")
            Ping_Result = main.ERROR

        if Ping_Result==main.TRUE:
            main.log.report("Ping test successful ")
        if Ping_Result==main.FALSE:
            main.log.report("Ping test failed")

        case24_result = Ping_Result and links_state_result
        utilities.assert_equals(expect=main.TRUE, actual=case24_result,
                onpass="Packet optical rerouting successful",
                onfail="Packet optical rerouting failed")

    def CASE4(self, main):
        import re
        import time
        main.log.report("This testcase is testing the assignment of all the switches to all the controllers and discovering the hosts in reactive mode")
        main.log.report("__________________________________")
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
            main.log.report("Controller assignmnet successful")
        else:
            main.log.report("Controller assignmnet failed")
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

        case4_result = Switch_Mastership and ping_result
        if ping_result == main.TRUE:
            main.log.report("Pingall Test in reactive mode to discover the hosts successful") 
        else:
            main.log.report("Pingall Test in reactive mode to discover the hosts failed")

        utilities.assert_equals(expect=main.TRUE, actual=case4_result,onpass="Controller assignment and Pingall Test successful",onfail="Controller assignment and Pingall Test NOT successful")   

    def CASE10(self):
        main.log.report("This testcase uninstalls the reactive forwarding app")
        main.log.report("__________________________________")
        main.case("Uninstalling reactive forwarding app")
        #Unistall onos-app-fwd app to disable reactive forwarding
        appUninstall_result = main.ONOS2.feature_uninstall("onos-app-fwd")
        main.log.info("onos-app-fwd uninstalled")

        #After reactive forwarding is disabled, the reactive flows on switches timeout in 10-15s
        #So sleep for 15s
        time.sleep(15)

        flows = main.ONOS2.flows()
        main.log.info(flows)

        case10_result = appUninstall_result
        utilities.assert_equals(expect=main.TRUE, actual=case10_result,onpass="Reactive forwarding app uninstallation successful",onfail="Reactive forwarding app uninstallation failed") 

    
    def CASE6(self):
        main.log.report("This testcase is testing the addition of host intents and then does pingall")
        main.log.report("__________________________________")
        main.case("Obtaining host id's")
        main.step("Get hosts")
        hosts = main.ONOS2.hosts()
        #main.log.info(hosts)

        main.step("Get all devices id")
        devices_id_list = main.ONOS2.get_all_devices_id()
        #main.log.info(devices_id_list)
        
        #ONOS displays the hosts in hex format unlike mininet which does in decimal format
        #So take care while adding intents
        '''
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
        
        for i in range(8,18):
            main.log.info("Adding host intent between h"+str(i)+" and h"+str(i+10))
            host1 =  "00:00:00:00:00:" + str(hex(i)[2:]).zfill(2).upper()
            host2 =  "00:00:00:00:00:" + str(hex(i+10)[2:]).zfill(2).upper()
            #NOTE: get host can return None
            #TODO: handle this
            host1_id = main.ONOS2.get_host(host1)['id']
            host2_id = main.ONOS2.get_host(host2)['id']
            tmp_result = main.ONOS2.add_host_intent(host1_id, host2_id )        

        time.sleep(10)
        h_intents = main.ONOS2.intents(json_format = False)
        main.log.info("intents:" +h_intents)
        flowHandle = main.ONOS2.flows()
        #main.log.info("flow:" +flowHandle)

        count = 1
        i = 8
        Ping_Result = main.TRUE
        #while i<10:
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
            main.log.report("Ping all test after Host intent addition failed. Cleaning up")
            #main.cleanup()
            #main.exit()
        if Ping_Result==main.TRUE:
            main.log.report("Ping all test after Host intent addition successful")
            
        case6_result = Ping_Result
        utilities.assert_equals(expect=main.TRUE, actual=case6_result,
                onpass="Pingall Test after Host intents addition successful",
                onfail="Pingall Test after Host intents addition failed")


    def CASE5(self,main) :
        import json
        from subprocess import Popen, PIPE
        from sts.topology.teston_topology import TestONTopology # assumes that sts is already in you PYTHONPATH
        #main.ONOS2.start_onos_cli(ONOS_ip=main.params['CTRL']['ip1'])
        deviceResult = main.ONOS2.devices()
        linksResult = main.ONOS2.links()
        #portsResult = main.ONOS2.ports()
        print "**************"

        main.log.report("This testcase is testing if all ONOS nodes are in topology sync with mininet")
        main.log.report("__________________________________")
        main.case("Comparing Mininet topology with the topology of ONOS")
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
        #ports_json = main.ONOS2.ports()
        print "devices_json= ", devices_json
        
        result1 = main.Mininet1.compare_switches(MNTopo, json.loads(devices_json))
        result2 = main.Mininet1.compare_links(MNTopo, json.loads(links_json))
        #result3 = main.Mininet1.compare_ports(MNTopo, json.loads(ports_json))
            
        #result = result1 and result2 and result3
        result = result1 and result2
        
        print "***********************"
        if result == main.TRUE:
            main.log.report("ONOS"+ " Topology matches MN Topology")
        else:
            main.log.report("ONOS"+ " Topology does not match MN Topology") 

        utilities.assert_equals(expect=main.TRUE,actual=result,
            onpass="ONOS" + " Topology matches MN Topology",
            onfail="ONOS" + " Topology does not match MN Topology")
        
        Topology_Check = Topology_Check and result
        utilities.assert_equals(expect=main.TRUE,actual=Topology_Check,
            onpass="Topology checks passed", onfail="Topology checks failed")
    

    def CASE7 (self,main):
       
        ONOS1_ip = main.params['CTRL']['ip1']

        link_sleep = int(main.params['timers']['LinkDiscovery'])

        main.log.report("This testscase is killing a link to ensure that link discovery is consistent")
        main.log.report("__________________________________")
        main.log.report("Killing a link to ensure that link discovery is consistent")
        main.case("Killing a link to Ensure that Link Discovery is Working Properly")
        '''
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
        '''

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
       
        #Check ping result here..add code for it
         
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
            
        #NOTE Check ping result here..add code for it
        
        
        main.step("Compare ONOS Topology to MN Topology")
        Topo = TestONTopology(main.Mininet1, ctrls) # can also add Intent API info for intent operations
        MNTopo = Topo
        Topology_Check = main.TRUE
        
        devices_json = main.ONOS2.devices()
        links_json = main.ONOS2.links()
        ports_json = main.ONOS2.ports()
        print "devices_json= ", devices_json
        
        result1 = main.Mininet1.compare_switches(MNTopo, json.loads(devices_json))
        result2 = main.Mininet1.compare_links(MNTopo, json.loads(links_json))
        #result3 = main.Mininet1.compare_ports(MNTopo, json.loads(ports_json))
            
        #result = result1 and result2 and result3
        result = result1 and result2
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


    def CASE8(self):
        '''
        Host intents removal
        ''' 
        main.log.report("This testcase removes host intents before adding the same intents or point intents")
        main.log.report("__________________________________")        
        main.log.info("Host intents removal")
        main.case("Removing host intents")
        main.step("Obtain the intent id's")
        intent_result = main.ONOS2.intents(json_format = False)
        main.log.info("intent_result = " +intent_result)        
 
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
            main.ONOS2.remove_intent(intent_id = id)
        
        intent_result = main.ONOS2.intents(json_format = False)
        main.log.info("intent_result = " +intent_result)        

        case8_result = main.TRUE
        if case8_result == main.TRUE:
            main.log.report("Intent removal successful")
        else:
            main.log.report("Intent removal failed")
       
        Ping_Result = main.TRUE
        if case8_result == main.TRUE:
            i = 8
            while i <18 :
                main.log.info("\n\nh"+str(i)+" is Pinging h" + str(i+10))
                ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+10))
                if ping==main.TRUE:
                    i = 19
                    Ping_Result = Ping_Result and main.TRUE
                elif ping==main.FALSE:
                    i+=1
                    Ping_Result = Ping_Result and main.FALSE
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
                onfail="Intent removal test passed")


    def CASE9(self):
        main.log.report("This testcase adds point intents and then does pingall")
        main.log.report("__________________________________") 
        main.log.info("Adding point intents")
        main.case("Adding bidirectional point for mn hosts(h8-h18,h9-h19,h10-h20,h11-h21,h12-h22,h13-h23,h14-h24,h15-h25,h16-h26,h17-h27)") 
        main.step("Add point-to-point intents for mininet hosts h8 and h18 or ONOS hosts h8 and h12")
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000003008/1", "of:0000000000006018/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000006018/1", "of:0000000000003008/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
       
        main.step("Add point-to-point intents for mininet hosts h9 and h19 or ONOS hosts h9 and h13")
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000003009/1", "of:0000000000006019/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000006019/1", "of:0000000000003009/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
        
        main.step("Add point-to-point intents for mininet hosts h10 and h20 or ONOS hosts hA and h14")
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000003010/1", "of:0000000000006020/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000006020/1", "of:0000000000003010/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)

        main.step("Add point-to-point intents for mininet hosts h11 and h21 or ONOS hosts hB and h15")
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000003011/1", "of:0000000000006021/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000006021/1", "of:0000000000003011/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
            
        main.step("Add point-to-point intents for mininet hosts h12 and h22 or ONOS hosts hC and h16")
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000003012/1", "of:0000000000006022/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000006022/1", "of:0000000000003012/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
            
        main.step("Add point-to-point intents for mininet hosts h13 and h23 or ONOS hosts hD and h17")
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000003013/1", "of:0000000000006023/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000006023/1", "of:0000000000003013/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)

        main.step("Add point-to-point intents for mininet hosts h14 and h24 or ONOS hosts hE and h18")
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000003014/1", "of:0000000000006024/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000006024/1", "of:0000000000003014/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
            
        main.step("Add point-to-point intents for mininet hosts h15 and h25 or ONOS hosts hF and h19")
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000003015/1", "of:0000000000006025/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000006025/1", "of:0000000000003015/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
            
        main.step("Add point-to-point intents for mininet hosts h16 and h26 or ONOS hosts h10 and h1A")
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000003016/1", "of:0000000000006026/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000006026/1", "of:0000000000003016/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)


        main.step("Add point-to-point intents for mininet hosts h17 and h27 or ONOS hosts h11 and h1B")
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000003017/1", "of:0000000000006027/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)
       
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000000000006027/1", "of:0000000000003017/1")
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            #main.log.info(get_intent_result)

        print("_______________________________________________________________________________________")

        flowHandle = main.ONOS2.flows()
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
            main.log.report("Point intents have not ben installed correctly. Cleaning up")
            #main.cleanup()
            #main.exit()
        if Ping_Result==main.TRUE:
            main.log.report("Point Intents have been installed correctly")

        case9_result = Ping_Result
        utilities.assert_equals(expect=main.TRUE, actual=case9_result,
                onpass="Point intents addition and Pingall Test successful",
                onfail="Point intents addition and Pingall Test NOT successful")


