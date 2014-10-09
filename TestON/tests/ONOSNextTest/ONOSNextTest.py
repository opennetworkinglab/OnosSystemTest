
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

        install_result = main.ONOSbench.clean_install()
        package_result = main.ONOSbench.onos_package()
        cell_result = main.ONOSbench.set_cell(cell_name)
        verify_result = main.ONOSbench.verify_cell()

        case1_result = (install_result and package_result and\
                cell_result and verify_result)
        utilities.assert_equals(expect=main.TRUE, actual=case1_result,
                onpass="Test startup successful",
                onfail="Test startup NOT successful")


