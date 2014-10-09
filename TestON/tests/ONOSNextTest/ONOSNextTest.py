
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
        
        
        install_result = main.ONOSbench.clean_install()
        package_result = main.ONOSbench.onos_package()

        print install_result
        print package_result
        print (install_result and package_result)
        


