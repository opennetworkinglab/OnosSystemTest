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
        MN1_ip = main.params['MN']['ip1']
        BENCH_ip = main.params['BENCH']['ip']

        main.case("Setting up test environment")

        main.step("Creating cell file")
        cell_file_result = main.ONOSbench.create_cell_file(
                BENCH_ip, cell_name, MN1_ip, ONOS1_ip)

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
        if git_pull == 'on':
            mvn_result = main.ONOSbench.clean_install()
        else:
            mvn_result = main.TRUE
            main.log.info("Skipped mvn clean compile")

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


