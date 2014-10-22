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


