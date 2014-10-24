#TopoPerfNext
#
#Topology Performance test for ONOS-next
#
#andrew@onlab.us

import time
import sys
import os
import re

class TopoPerfNext:
    def __init__(self):
        self.default = ''

    def CASE1(self, main):
        '''
        ONOS startup sequence
        '''
        import time
    
        cell_name = main.params['ENV']['cellName']

        git_pull = main.params['GIT']['autoPull']
        checkout_branch = main.params['GIT']['checkout']

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        MN1_ip = main.params['MN']['ip1']
        BENCH_ip = main.params['BENCH']['ip']

        main.case("Setting up test environment")

        main.step("Creating cell file")
        cell_file_result = main.ONOSbench.create_cell_file(
                BENCH_ip, cell_name, MN1_ip, "onos-core",
                ONOS1_ip, ONOS2_ip, ONOS3_ip)

        main.step("Applying cell file to environment")
        cell_apply_result = main.ONOSbench.set_cell(cell_name)
        verify_cell_result = main.ONOSbench.verify_cell()
        
        main.step("Git checkout and pull "+checkout_branch)
        if git_pull == 'on':
            checkout_result = \
                    main.ONOSbench.git_checkout(checkout_branch)
            pull_result = main.ONOSbench.git_pull()
        else:
            checkout_result = main.TRUE
            pull_result = main.TRUE
            main.log.info("Skipped git checkout and pull")

        main.step("Using mvn clean & install")
        #mvn_result = main.ONOSbench.clean_install()
        mvn_result = main.TRUE

        main.step("Creating ONOS package")
        package_result = main.ONOSbench.onos_package()

        main.step("Installing ONOS package")
        install1_result = main.ONOSbench.onos_install(node=ONOS1_ip)
        install2_result = main.ONOSbench.onos_install(node=ONOS2_ip)
        install3_result = main.ONOSbench.onos_install(node=ONOS3_ip)

        #NOTE: This step may be unnecessary
        #main.step("Starting ONOS service")
        #start_result = main.ONOSbench.onos_start(ONOS1_ip)

        main.step("Set cell for ONOS cli env")
        main.ONOS1cli.set_cell(cell_name)
        main.ONOS2cli.set_cell(cell_name)
        main.ONOS3cli.set_cell(cell_name)

        time.sleep(10)

        main.step("Start onos cli")
        cli1 = main.ONOS1cli.start_onos_cli(ONOS1_ip)
        cli2 = main.ONOS2cli.start_onos_cli(ONOS2_ip)
        cli3 = main.ONOS3cli.start_onos_cli(ONOS3_ip)

        main.step("Enable metrics feature")
        main.ONOS1cli.feature_install("onos-app-metrics-topology")
        main.ONOS2cli.feature_install("onos-app-metrics-topology")
        main.ONOS3cli.feature_install("onos-app-metrics-topology")

        utilities.assert_equals(expect=main.TRUE,
                actual= cell_file_result and cell_apply_result and\
                        verify_cell_result and checkout_result and\
                        pull_result and mvn_result and\
                        install1_result and install2_result and\
                        install3_result,
                onpass="ONOS started successfully",
                onfail="Failed to start ONOS")

    def CASE2(self, main):
        '''
        Assign s1 to ONOS1 and measure latency
        
        There are 4 levels of latency measurements to this test:
        1) End-to-end measurement: Complete end-to-end measurement
           from TCP (SYN/ACK) handshake to Graph change
        2) OFP-to-graph measurement: 'ONOS processing' snippet of
           measurement from OFP Vendor message to Graph change
        3) OFP-to-device measurement: 'ONOS processing without 
           graph change' snippet of measurement from OFP vendor
           message to Device change timestamp
        4) T0-to-device measurement: Measurement that includes
           the switch handshake to devices timestamp without 
           the graph view change. (TCP handshake -> Device 
           change)
        '''
        import time
        import subprocess
        import json
        import requests
        import os

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS_user = main.params['CTRL']['user']

        default_sw_port = main.params['CTRL']['port1']
       
        #Number of iterations of case
        num_iter = main.params['TEST']['numIter']
       
        #Timestamp 'keys' for json metrics output.
        #These are subject to change, hence moved into params
        deviceTimestamp = main.params['JSON']['deviceTimestamp']
        graphTimestamp = main.params['JSON']['graphTimestamp']

        #List of switch add latency collected from
        #all iterations
        latency_end_to_end_list = []
        latency_ofp_to_graph_list = []
        latency_ofp_to_device_list = []
        latency_t0_to_device_list = []

        #Directory/file to store tshark results
        tshark_of_output = "/tmp/tshark_of_topo.txt"
        tshark_tcp_output = "/tmp/tshark_tcp_topo.txt"

        #String to grep in tshark output
        tshark_tcp_string = "TCP 74 "+default_sw_port
        tshark_of_string = "OFP 86 Vendor"
     
        #Initialize assertion to TRUE
        assertion = main.TRUE
        
        main.log.report("Latency of adding one switch")

        for i in range(0, int(num_iter)):
            main.log.info("Starting tshark capture")

            #* TCP [ACK, SYN] is used as t0_a, the
            #  very first "exchange" between ONOS and 
            #  the switch for end-to-end measurement
            #* OFP [Stats Reply] is used for t0_b
            #  the very last OFP message between ONOS
            #  and the switch for ONOS measurement
            main.ONOS1.tshark_grep(tshark_tcp_string,
                    tshark_tcp_output)
            main.ONOS1.tshark_grep(tshark_of_string,
                    tshark_of_output)

            #Wait and ensure tshark is started and 
            #capturing
            time.sleep(10)

            main.log.info("Assigning s1 to controller")

            main.Mininet1.assign_sw_controller(sw="1",
                    ip1=ONOS1_ip, port1=default_sw_port)

            #Wait and ensure switch is assigned
            #before stopping tshark
            time.sleep(30)
   
            main.log.info("Stopping all Tshark processes")
            main.ONOS1.stop_tshark()

            #tshark output is saved in ONOS. Use subprocess
            #to copy over files to TestON for parsing
            main.log.info("Copying over tshark files")
            
            #TCP CAPTURE ****
            #Copy the tshark output from ONOS machine to
            #TestON machine in tshark_tcp_output directory>file
            os.system("scp "+ONOS_user+"@"+ONOS1_ip+":"+
                    tshark_tcp_output+" /tmp/") 
            tcp_file = open(tshark_tcp_output, 'r')
            temp_text = tcp_file.readline()
            temp_text = temp_text.split(" ")

            main.log.info("Object read in from TCP capture: "+
                    str(temp_text))
            if len(temp_text) > 1:
                t0_tcp = float(temp_text[1])*1000.0
            else:
                main.log.error("Tshark output file for TCP"+
                        " returned unexpected results")
                t0_tcp = 0
                assertion = main.FALSE
            
            tcp_file.close()
            #****************

            #OF CAPTURE ****
            os.system("scp "+ONOS_user+"@"+ONOS1_ip+":"+
                    tshark_of_output+" /tmp/")
            of_file = open(tshark_of_output, 'r')
           
            line_ofp = ""
            #Read until last line of file
            while True:
                temp_text = of_file.readline()
                if temp_text !='':
                    line_ofp = temp_text
                else:
                    break 
            obj = line_ofp.split(" ")
            
            main.log.info("Object read in from OFP capture: "+
                    str(line_ofp))
    
            if len(line_ofp) > 1:
                t0_ofp = float(obj[1])*1000.0
            else:
                main.log.error("Tshark output file for OFP"+
                        " returned unexpected results")
                t0_ofp = 0
                assertion = main.FALSE
            
            of_file.close()
            #****************
           
            #TODO: 
            #Get json object from all 3 ONOS instances
            json_str_1 = main.ONOS1cli.topology_events_metrics()
            json_str_2 = main.ONOS2cli.topology_events_metrics()
            json_str_3 = main.ONOS3cli.topology_events_metrics()

            json_obj_1 = json.loads(json_str_1)
            json_obj_2 = json.loads(json_str_2)
            json_obj_3 = json.loads(json_str_3)

            #Obtain graph timestamp. This timestsamp captures
            #the epoch time at which the topology graph was updated.
            graph_timestamp_1 = \
                    json_obj_1[graphTimestamp]['value']
            graph_timestamp_2 = \
                    json_obj_2[graphTimestamp]['value']
            graph_timestamp_3 = \
                    json_obj_3[graphTimestamp]['value']

            #Obtain device timestamp. This timestamp captures
            #the epoch time at which the device event happened
            device_timestamp_1 = \
                    json_obj_1[deviceTimestamp]['value'] 
            device_timestamp_2 = \
                    json_obj_2[deviceTimestamp]['value'] 
            device_timestamp_3 = \
                    json_obj_3[deviceTimestamp]['value'] 

            #t0 to device processing latency 
            delta_device_1 = int(device_timestamp_1) - int(t0_tcp)
            delta_device_2 = int(device_timestamp_2) - int(t0_tcp)
            delta_device_3 = int(device_timestamp_3) - int(t0_tcp)
        
            #Get average of delta from all instances
            avg_delta_device = \
                    (int(delta_device_1)+\
                     int(delta_device_2)+\
                     int(delta_device_3)) / 3

            #Ensure avg delta meets the threshold before appending
            if avg_delta_device > 0.0 and avg_delta_device < 10000:
                latency_t0_to_device_list.append(avg_delta_device)
            else:
                main.log.info("Results ignored due to excess in "+\
                        "threshold")

            #t0 to graph processing latency (end-to-end)
            delta_graph_1 = int(graph_timestamp_1) - int(t0_tcp)
            delta_graph_2 = int(graph_timestamp_2) - int(t0_tcp)
            delta_graph_3 = int(graph_timestamp_3) - int(t0_tcp)
        
            #Get average of delta from all instances
            avg_delta_graph = \
                    (int(delta_graph_1)+\
                     int(delta_graph_2)+\
                     int(delta_graph_3)) / 3

            latency_end_to_end_list.append(avg_delta_graph)
            
            #Ensure avg delta meets the threshold before appending
            if avg_delta_graph > 0.0 and avg_delta_graph < 10000:
                latency_t0_to_device_list.append(avg_delta_graph)
            else:
                main.log.info("Results ignored due to excess in "+\
                        "threshold")

            #ofp to graph processing latency (ONOS processing)
            delta_ofp_graph_1 = int(graph_timestamp_1) - int(t0_ofp)
            delta_ofp_graph_2 = int(graph_timestamp_2) - int(t0_ofp)
            delta_ofp_graph_3 = int(graph_timestamp_3) - int(t0_ofp)
            
            avg_delta_ofp_graph = \
                    (int(delta_ofp_graph_1)+\
                     int(delta_ofp_graph_2)+\
                     int(delta_ofp_graph_3)) / 3
            
            if avg_delta_ofp_graph > 0.0 and avg_delta_ofp_graph < 10000:
                latency_ofp_to_graph_list.append(avg_delta_ofp_graph)
            else:
                main.log.info("Results ignored due to excess in "+\
                        "threshold")

            #ofp to device processing latency (ONOS processing)
            delta_ofp_device_1 = float(device_timestamp_1) - float(t0_ofp)
            delta_ofp_device_2 = float(device_timestamp_2) - float(t0_ofp)
            delta_ofp_device_3 = float(device_timestamp_3) - float(t0_ofp)
            
            avg_delta_ofp_device = \
                    (float(delta_ofp_device_1)+\
                     float(delta_ofp_device_2)+\
                     float(delta_ofp_device_3)) / 3.0
            
            #NOTE: ofp - delta measurements are occasionally negative
            #      due to system time misalignment.
            #TODO: Implement ptp across all clusters
            #Just add the calculation to list for now
            latency_ofp_to_device_list.append(avg_delta_ofp_device)

            #TODO:
            #Fetch logs upon threshold excess

            
            main.log.info("ONOS1 delta end-to-end: "+
                    str(delta_graph_1))
            main.log.info("ONOS2 delta end-to-end: "+
                    str(delta_graph_2))
            main.log.info("ONSO3 delta end-to-end: "+
                    str(delta_graph_3))

            main.log.info("ONOS1 delta OFP - graph: "+
                    str(delta_ofp_graph_1))
            main.log.info("ONOS2 delta OFP - graph: "+
                    str(delta_ofp_graph_2))
            main.log.info("ONOS3 delta OFP - graph: "+
                    str(delta_ofp_graph_3))
            
            main.log.info("ONOS1 delta device - t0: "+
                    str(delta_device_1))
            main.log.info("ONOS2 delta device - t0: "+
                    str(delta_device_2))
            main.log.info("ONOS3 delta device - t0: "+
                    str(delta_device_3))
          
            main.log.info("ONOS1 delta OFP - device: "+
                    str(delta_ofp_device_1))
            main.log.info("ONOS2 delta OFP - device: "+
                    str(delta_ofp_device_2))
            main.log.info("ONOS3 delta OFP - device: "+
                    str(delta_ofp_device_3))

            main.step("Remove switch from controller")
            main.Mininet1.delete_sw_controller("s1")

            time.sleep(5)

        #END for loop for iteration

        #If there is at least 1 element in each list,
        #pass the test case
        if len(latency_end_to_end_list) > 0 and\
           len(latency_ofp_to_graph_list) > 0 and\
           len(latency_ofp_to_device_list) > 0 and\
           len(latency_t0_to_device_list) > 0:
            assertion = main.TRUE
        elif len(latency_end_to_end_list) == 0:
            #The appending of 0 here is to prevent 
            #the min,max,sum functions from failing 
            #below
            latency_end_to_end_list.append(0)
            assertion = main.FALSE
        elif len(latency_ofp_to_graph_list) == 0:
            latency_ofp_to_graph_list.append(0)
            assertion = main.FALSE
        elif len(latency_ofp_to_device_list) == 0:
            latency_ofp_to_device_list.append(0)
            assertion = main.FALSE
        elif len(latency_t0_to_device_list) == 0:
            latency_t0_to_device_list.append(0)
            assertion = main.FALSE

        #Calculate min, max, avg of latency lists
        latency_end_to_end_max = \
                int(max(latency_end_to_end_list))
        latency_end_to_end_min = \
                int(min(latency_end_to_end_list))
        latency_end_to_end_avg = \
                (int(sum(latency_end_to_end_list)) / \
                 len(latency_end_to_end_list))
   
        latency_ofp_to_graph_max = \
                int(max(latency_ofp_to_graph_list))
        latency_ofp_to_graph_min = \
                int(min(latency_ofp_to_graph_list))
        latency_ofp_to_graph_avg = \
                (int(sum(latency_ofp_to_graph_list)) / \
                 len(latency_ofp_to_graph_list))

        latency_ofp_to_device_max = \
                int(max(latency_ofp_to_device_list))
        latency_ofp_to_device_min = \
                int(min(latency_ofp_to_device_list))
        latency_ofp_to_device_avg = \
                (int(sum(latency_ofp_to_device_list)) / \
                 len(latency_ofp_to_device_list))

        latency_t0_to_device_max = \
                float(max(latency_t0_to_device_list))
        latency_t0_to_device_min = \
                float(min(latency_t0_to_device_list))
        latency_t0_to_device_avg = \
                (float(sum(latency_t0_to_device_list)) / \
                 len(latency_ofp_to_device_list))

        main.log.report("Switch add - End-to-end latency: \n"+\
                "Min: "+str(latency_end_to_end_min)+"\n"+\
                "Max: "+str(latency_end_to_end_max)+"\n"+\
                "Avg: "+str(latency_end_to_end_avg))
        main.log.report("Switch add - OFP-to-Graph latency: \n"+\
                "Min: "+str(latency_ofp_to_graph_min)+"\n"+\
                "Max: "+str(latency_ofp_to_graph_max)+"\n"+\
                "Avg: "+str(latency_ofp_to_graph_avg))
        main.log.report("Switch add - OFP-to-Device latency: \n"+\
                "Min: "+str(latency_ofp_to_device_min)+"\n"+\
                "Max: "+str(latency_ofp_to_device_max)+"\n"+\
                "Avg: "+str(latency_ofp_to_device_avg))
        main.log.report("Switch add - t0-to-Device latency: \n"+\
                "Min: "+str(latency_t0_to_device_min)+"\n"+\
                "Max: "+str(latency_t0_to_device_max)+"\n"+\
                "Avg: "+str(latency_t0_to_device_avg))

        utilities.assert_equals(expect=main.TRUE, actual=assertion,
                onpass="Switch latency test successful",
                onfail="Switch latency test failed")

    def CASE3(self, main):
        '''
        Bring port up / down and measure latency.
        Port enable / disable is simulated by ifconfig up / down
        '''
        import time
        import subprocess
        import os
        import requests
        import json

        ONOS1_ip = main.params['CTRL']['ip1']
        default_sw_port = main.params['CTRL']['port1']
        ONOS_user = main.params['CTRL']['user']
        num_iter = main.params['TEST']['numIter']

        tshark_port_status = "OFP 130 Port Status"

        tshark_port_up = "/tmp/tshark_port_up.txt"
        tshark_port_down = "/tmp/tshark_port_down.txt"

        main.log.report("Port enable / disable latency")

        main.step("Assign switch to controller")
        main.Mininet1.assign_sw_controller(sw="1",ip1=ONOS1_ip,
                port1=default_sw_port)

        main.step("Verify switch is assigned correctly")
        result_s1 = main.Mininet1.get_sw_controller(sw="s1")
        if result_s1 == main.FALSE:
            main.log.info("Switch s1 was not assigned correctly")
            assertion = main.FALSE
        else:
            main.log.info("Switch s1 was assigned correctly")

        for i in range(0, int(num_iter)):
            main.step("Starting wireshark capture for port status down")
            main.ONOS1.tshark_grep(tshark_port_status,
                    tshark_port_down)
            
            time.sleep(10)

            main.step("Disable port (interface s1-eth2)")
            main.Mininet2.handle.sendline("sudo ifconfig s1-eth2 down")
            main.Mininet2.handle.expect("\$")
            time.sleep(20)

            main.ONOS1.tshark_stop()
            time.sleep(5)
            
            #Copy tshark output file from ONOS to TestON instance
            #/tmp directory
            os.system("scp "+ONOS_user+"@"+ONOS1_ip+":"+
                    tshark_port_down+" /tmp/")

            f_port_down = open(tshark_port_down, 'r')
            f_line = f_port_down.readline()
            obj_down = f_line.split(" ")
            if len(f_line) > 0:
                timestamp_begin_pt_down = int(float(obj_down[1])*1000)
            else:
                main.log.info("Tshark output file returned unexpected"+
                        " results")
                timestamp_begin_pt_down = 0

            main.step("Obtain t1 by REST call")
            #TODO: Implement json object parsing here

            timestamp_end_pt_down_1 = 0
            timestamp_end_pt_down_2 = 0
            timestamp_end_pt_down_3 = 0

            delta_pt_down_1 = int(timestamp_end_pt_down_1) - \
                    int(timestamp_begin_pt_down)
            delta_pt_down_2 = int(timestamp_end_pt_down_2) - \
                    int(timestamp_begin_pt_down)
            delta_pt_down_3 = int(timestamp_end_pt_down_3) - \
                    int(timestamp_begin_pt_down)
           
            #TODO: Remove these logs. For test purposes only
            main.log.info("Delta1: "+str(delta_pt_down_1))
            main.log.info("Delta2: "+str(delta_pt_down_2)) 
            main.log.info("Delta3: "+str(delta_pt_down_3)) 
        
            #Port up events 
            main.step("Enable port and obtain timestamp")
            main.step("Starting wireshark capture for port status up")
            main.ONOS1.tshark_grep("OFP 130 Port Status", tshark_port_up)
            time.sleep(10)

            main.Mininet2.handle.sendline("sudo ifconfig s1-eth2 up")
            main.Mininet2.handle.expect("\$")
            time.sleep(20)

            os.system("scp "+ONOS_user+"@"+ONOS1_ip+":"+
                    tshark_port_up+" /tmp/")

            f_port_up = open(tshark_port_up, 'r')
            f_line = f_port_down.readline()
            obj_up = f_line.split(" ")
            if len(f_line) > 0:
                timestamp_begin_pt_up = int(float(obj_up[1])*1000)
            else:
                main.log.info("Tshark output file returned unexpected"+
                        " results.")
                timestamp_begin_pt_up = 0
            
            main.step("Obtain t1 by REST call")
            #TODO: Implement json object parsing here

            timestamp_end_pt_up_1 = 0
            timestamp_end_pt_up_2 = 0
            timestamp_end_pt_up_3 = 0

            delta_pt_up_1 = int(timestamp_end_pt_up_1) - \
                    int(timestamp_begin_pt_up)
            delta_pt_up_2 = int(timestamp_end_pt_up_2) - \
                    int(timestamp_begin_pt_up)
            delta_pt_up_3 = int(timestamp_end_pt_up_3) - \
                    int(timestamp_begin_pt_up)
           
            #TODO: Remove these logs. For test purposes only
            main.log.info("Delta1: "+str(delta_pt_up_1))
            main.log.info("Delta2: "+str(delta_pt_up_2)) 
            main.log.info("Delta3: "+str(delta_pt_up_3)) 
             
            
            
            
            
            
            
            
            
            
            
            
            
            
            
