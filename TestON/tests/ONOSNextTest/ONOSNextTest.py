
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
        
        clean_install_result = main.ONOSbench.clean_install()
        package_result = main.ONOSbench.onos_package()
        cell_result = main.ONOSbench.set_cell(cell_name)
        verify_result = main.ONOSbench.verify_cell()
        onos_install_result = main.ONOSbench.onos_install()
        onos1_isup = main.ONOSbench.isup()

        case1_result = (clean_install_result and package_result and\
                cell_result and verify_result and onos_install_result\
                and onos1_isup)
        utilities.assert_equals(expect=main.TRUE, actual=case1_result,
                onpass="Test startup successful",
                onfail="Test startup NOT successful")


