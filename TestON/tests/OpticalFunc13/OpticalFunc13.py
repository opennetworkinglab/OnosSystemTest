
#Testing the basic functionality of ONOS Next
#For sanity and driver functionality excercises only.

import time
import sys
import os
import re
import time
import json

time.sleep(1)
class OpticalFunc13:
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
        main.log.report(main.ONOSbench.get_version())
        if git_pull_result == 1:
            main.step("Using mvn clean & install")
            clean_install_result = main.ONOSbench.clean_install()
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
        sart_console_result = main.LincOE1.start_console()
        optical_mn_script = main.LincOE2.run_optical_mn_script()
        onos_topo_cfg_result = main.ONOSbench.run_onos_topo_cfg(instance_name = main.params['CTRL']['ip1'], json_file = main.params['OPTICAL']['jsonfile'])
         


    def CASE22(self, main):
        '''
            Curretly we use, 4 linear switch optical topology and 2 packet layer mininet switches each with one host.
             Therefore, the roadmCount variable = 4, packetLayerSWCount variable = 2, hostCount =2
            and this is hardcoded in the testcase. If the topology changes, these hardcoded values need to be changed
        '''

        main.log.report("This testcase compares the optical+packet topology against what is expected")
        main.ONOS2.start_onos_cli(ONOS_ip=main.params['CTRL']['ip1'])
        devices_result = main.ONOS2.devices(json_format = False)

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
        
        links_result = main.ONOS2.links(json_format = False)
        print "links_result = ", links_result
        print "_________________________________"
        


        #Discover hosts using pingall
        pingall_result = main.LincOE2.pingall()    
    
        hosts_result = main.ONOS2.hosts(json_format = False)
        print "hosts_result = ", hosts_result   
        print "_________________________________"
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
        
        case22_result = opticalSW_result and packetSW_result and hostDiscovery
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
        ptp_intent_result = main.ONOS2.add_point_intent("of:0000ffffffff0001", 1, "of:0000ffffffff0002", 1)
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            main.log.info(get_intent_result)

        ptp_intent_result = main.ONOS2.add_point_intent("of:0000ffffffff0002", 1, "of:0000ffffffff0001", 1)
        if ptp_intent_result == main.TRUE:
            get_intent_result = main.ONOS2.intents()
            main.log.info("Point to point intent install successful")
            main.log.info(get_intent_result)

        time.sleep(10)
        flowHandle = main.ONOS2.flows()
        #print "flowHandle = ", flowHandle
        main.log.info("flows :" + flowHandle)
        intentHandle = main.ONOS2.intents()        
        main.log.info("intents :" + intentHandle)        
 
        Ping_Result = main.TRUE
        count = 1
        main.log.info("\n\nh1 is Pinging h2")
        ping = main.LincOE2.pingHostOptical(src="h1", target="h2")
        #ping = main.LincOE2.pinghost()
        if ping == main.FALSE and count<5:
            count+=1
            Ping_Result = main.FALSE
            main.log.report("Ping between h1 and h2  failed. Making attempt number "+str(count) + " in 2 seconds")
            time.sleep(2)
            ping = main.LincOE2.pingHostOptical(src="h1", target="h2")
            #ping = main.LincOE2.pinghost()
        elif ping==main.FALSE:
            main.log.report("All ping attempts between h1 and h2 have failed")
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


