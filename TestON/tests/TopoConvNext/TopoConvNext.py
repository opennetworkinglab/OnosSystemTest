#TopoPerfNext
#
#Topology Performance test for ONOS-next
#
#andrew@onlab.us

import time
import sys
import os
import re

class TopoConvNext:
    def __init__(self):
        self.default = ''

    #******
    #Global cluster count for scale-out purposes
    cluster_count = 1
    #******

    def CASE1(self, main):
        '''
        ONOS startup sequence
        '''
        import time
    
        cell_name = main.params['ENV']['cellName']

        git_pull = main.params['GIT']['autoPull']
        checkout_branch = main.params['GIT']['checkout']

        ONOS1_ip = main.params['CTRL']['ip1']
        MN1_ip = main.params['MN']['ip1']
        BENCH_ip = main.params['BENCH']['ip']

        main.case("Setting up test environment")
        main.log.report("Setting up test environment")

        main.step("Creating cell file")
        cell_file_result = main.ONOSbench.create_cell_file(
                BENCH_ip, cell_name, MN1_ip, "onos-core",
                ONOS1_ip)

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

        main.step("Set cell for ONOS cli env")
        main.ONOS1cli.set_cell(cell_name)

        main.step("Creating ONOS package")
        package_result = main.ONOSbench.onos_package()

        main.step("Installing ONOS package")
        install1_result = main.ONOSbench.onos_install(node=ONOS1_ip)

        time.sleep(10)

        main.step("Start onos cli")
        cli1 = main.ONOS1cli.start_onos_cli(ONOS1_ip)

        main.step("Enable metrics feature")
        main.ONOS1cli.feature_install("onos-app-metrics")

        utilities.assert_equals(expect=main.TRUE,
                actual= cell_file_result and cell_apply_result and\
                        verify_cell_result and checkout_result and\
                        pull_result and mvn_result and\
                        install1_result and install2_result and\
                        install3_result,
                onpass="Test Environment setup successful",
                onfail="Failed to setup test environment")
    
    def CASE2(self, main):
        '''
        100 Switch discovery latency

        Important:
            This test case can be potentially dangerous if 
            your machine has previously set iptables rules.
            One of the steps of the test case will flush
            all existing iptables rules.
        Note:
            You can specify the number of switches in the 
            params file to adjust the switch discovery size
            (and specify the corresponding topology in Mininet1 
            .topo file)
        '''
        import time
        import subprocess
        import os
        import requests
        import json

        ONOS_ip_list = []
        ONOS_ip_list[0] = main.params['CTRL']['ip1']
        MN1_ip = main.params['MN']['ip1']
        ONOS_user = main.params['CTRL']['user']

        default_sw_port = main.params['CTRL']['port1']
       
        #Number of iterations of case
        num_iter = main.params['TEST']['numIter']
        num_sw = main.params['TEST']['numSwitch']

        #Timestamp 'keys' for json metrics output.
        #These are subject to change, hence moved into params
        deviceTimestamp = main.params['JSON']['deviceTimestamp']
        graphTimestamp = main.params['JSON']['graphTimestamp']
        
        debug_mode = main.params['TEST']['debugMode']

        local_time = time.strftime('%X')
        local_time = local_time.replace("/","")
        local_time = local_time.replace(" ","_")
        local_time = local_time.replace(":","")
        if debug_mode == 'on':
            main.ONOS1.tshark_pcap("eth0",
                    "/tmp/100_sw_lat_pcap_"+local_time) 
 
        #Threshold for this test case
        sw_disc_threshold_str = main.params['TEST']['swDisc100Threshold']
        sw_disc_threshold_obj = sw_disc_threshold_str.split(",")
        sw_disc_threshold_min = int(sw_disc_threshold_obj[0])
        sw_disc_threshold_max = int(sw_disc_threshold_obj[1])

        tshark_ofp_output = "/tmp/tshark_ofp_"+num_sw+"sw.txt"
        tshark_tcp_output = "/tmp/tshark_tcp_"+num_sw+"sw.txt"

        tshark_ofp_result_list = []
        tshark_tcp_result_list = []

        sw_discovery_lat_list = []

        main.case(num_sw+" Switch discovery latency")
        
        #TODO: Implement modular switch discovery measurements
        #for scale-out scenario


    def CASE3(self, main):
        '''
        Increase number of nodes and start those nodes
        '''
        import time
        import subprocess
        import os
        import requests
        import json
       
        ONOS_ip_list = []
        ONOS_ip_list.append(main.params['ONOS']['ip1'])
        ONOS_ip_list.append(main.params['ONOS']['ip2'])
        ONOS_ip_list.append(main.params['ONOS']['ip3'])
        ONOS_ip_list.append(main.params['ONOS']['ip4'])
        ONOS_ip_list.append(main.params['ONOS']['ip5'])
        ONOS_ip_list.append(main.params['ONOS']['ip6'])
        ONOS_ip_list.append(main.params['ONOS']['ip7'])
        
        MN1_ip = main.params['MN']['ip1']
        BENCH_ip = main.params['BENCH']['ip']
 
        #NOTE:We start with cluster_count at 1. The first 
        #case already initialized ONOS1. Increase the
        #cluster count and start from 2.
        #You can optionally change the increment to
        #test steps of node sizes, such as 1,3,5,7
        
        global cluster_count
        cluster_count += 1
       
        #Supports up to 7 node configuration
        for node in cluster_count:
            main.log.info("Installing ONOS instance: "+
                    ONOS_ip_list[node])
            main.ONOSbench.onos_install(ONOS_ip_list[node]) 
            time.sleep(5) 
            if node == 0:
                main.log.info("Starting CLI for instance "+
                        ONOS_ip_list[node])
                main.ONOS1cli.start_onos_cli(ONOS_ip_list[node])
            elif node == 1:
                main.log.info("Starting CLI for instance "+
                        ONOS_ip_list[node])
                main.ONOS2cli.start_onos_cli(ONOS_ip_list[node])
            elif node == 2:
                main.log.info("Starting CLI for instance "+
                        ONOS_ip_list[node])
                main.ONOS3cli.start_onos_cli(ONOS_ip_list[node])
            elif node == 3:
                main.log.info("Starting CLI for instance "+
                        ONOS_ip_list[node])
                main.ONOS3cli.start_onos_cli(ONOS_ip_list[node])
            elif node == 4:
                main.log.info("Starting CLI for instance "+
                        ONOS_ip_list[node])
                main.ONOS4cli.start_onos_cli(ONOS_ip_list[node])
            elif node == 5:
                main.log.info("Starting CLI for instance "+
                        ONOS_ip_list[node])
                main.ONOS5cli.start_onos_cli(ONOS_ip_list[node])
            elif node == 6:
                main.log.info("Starting CLI for instance "+
                        ONOS_ip_list[node])
                main.ONOS6cli.start_onos_cli(ONOS_ip_list[node])
            elif node == 7:
                main.log.info("Starting CLI for instance "+
                        ONOS_ip_list[node])
                main.ONOS7cli.start_onos_cli(ONOS_ip_list[node]) 
            time.sleep(5)





