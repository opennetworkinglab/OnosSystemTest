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
                BENCH_ip, cell_name, MN1_ip,
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
        mvn_result = main.ONOSbench.clean_install()

        main.step("Creating ONOS package")
        package_result = main.ONOSbench.onos_package()

        main.step("Installing ONOS package")
        install_result = main.ONOSbench.onos_install()

        main.step("Starting ONOS service")
        start_result = main.ONOSbench.onos_start(ONOS1_ip)

        utilities.assert_equals(expect=main.TRUE,
                actual= cell_file_result and cell_apply_result and\
                        verify_cell_result and checkout_result and\
                        pull_result and mvn_result and\
                        install_result and start_result,
                onpass="Cell file created successfully",
                onfail="Failed to create cell file")

    def CASE2(self, main):
        '''
        Assign s1 to ONOS1 and measure latency
        '''
        import time

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        default_sw_port = main.params['CTRL']['port1']
       
        #Number of iterations of case
        num_iter = main.params['TEST']['numIter']
       
        #Directory/file to store tshark results
        tshark_of_output = "/tmp/tshark_of_topo.txt"
        tshark_tcp_output = "/tmp/tshark_tcp_topo.txt"

        #String to grep in tshark output
        tshark_tcp_string = "TCP 74 "+default_sw_port
        tshark_of_string = "OFP 86 Vendor"
       
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
            time.sleep(10)
    
            main.ONOS1.stop_tshark()













