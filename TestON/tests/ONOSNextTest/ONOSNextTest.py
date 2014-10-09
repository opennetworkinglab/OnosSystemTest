
#Testing the basic functionality of ONOS Next
#For sanity and driver functionality excercises only.

import time
import sys
import os

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

        main.case("Setting up test environment")

        main.step("Using mvn clean & compile")
        install_result = main.ONOSbench.clean_install()
        
        main.step("Creating ONOS package")
        package_result = main.ONOSbench.onos_package()

        main.step("Applying cell variable to environment")
        cell_result = main.ONOSbench.set_cell(cell_name)
        verify_result = main.ONOSbench.verify_cell()
   
        main.step("Starting ONOS service")
        start_result = main.ONOSbench.onos_start(ONOS1_ip)



        case1_result = (install_result and package_result and\
                cell_result and verify_result and start_result)
        utilities.assert_equals(expect=main.TRUE, actual=case1_result,
                onpass="Test startup successful",
                onfail="Test startup NOT successful")


