# ScaleOutTemplate --> IntentsLoad
#
# CASE1 starts number of nodes specified in param file
#
# cameron@onlab.us

import sys 
import os 


class IntentsLoad:
    def __init__(self):
        self.default = ''
   
    def CASE1(self, main):
        
        global cluster_count 
        cluster_count = 1        

        checkout_branch = main.params['GIT']['checkout']
        git_pull = main.params['GIT']['autopull']
        cell_name = main.params['ENV']['cellName']
        BENCH_ip = main.params['BENCH']['ip1']
        BENCH_user = main.params['BENCH']['user']
        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        MN1_ip = main.params['MN']['ip1']

        main.log.step("Cleaning Enviornment...")
        main.ONOSbench.onos_uninstall(ONOS1_ip)
        main.ONOSbench.onos_uninstall(ONOS2_ip)
        main.ONOSbench.onos_uninstall(ONOS3_ip)                                     
        
        main.step("Git checkout and pull "+checkout_branch)
        if git_pull == 'on':
            checkout_result = main.ONOSbench.git_checkout(checkout_branch)       
            pull_result = main.ONOSbench.git_pull()
            
        else:
            checkout_result = main.TRUE
            pull_result = main.TRUE
            main.log.info("Skipped git checkout and pull")

        #mvn_result = main.ONOSbench.clean_install()
                                                                   
        main.step("Set cell for ONOS cli env")
        main.ONOS1cli.set_cell(cell_name)
        main.ONOS2cli.set_cell(cell_name)
        main.ONOS3cli.set_cell(cell_name)

        main.step("Creating ONOS package")
        package_result = main.ONOSbench.onos_package()                             #no file or directory 

        main.step("Installing ONOS package")
        install1_result = main.ONOSbench.onos_install(node=ONOS1_ip)

        cell_name = main.params['ENV']['cellName']
        main.step("Applying cell file to environment")
        cell_apply_result = main.ONOSbench.set_cell(cell_name)
        main.step("verify cells")
        verify_cell_result = main.ONOSbench.verify_cell()

        main.step("Set cell for ONOS cli env")
        main.ONOS1cli.set_cell(cell_name) 
 
        cli1 = main.ONOS1cli.start_onos_cli(ONOS1_ip) 

    def CASE2(self, main):

        '''  
        Increase number of nodes and initiate CLI
        '''
        import time 
        
        global cluster_count
        
        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        #ONOS4_ip = main.params['CTRL']['ip4']
        #ONOS5_ip = main.params['CTRL']['ip5']
        #ONOS6_ip = main.params['CTRL']['ip6']
        #ONOS7_ip = main.params['CTRL']['ip7']
        cell_name = main.params['ENV']['cellName']
        scale = int(main.params['SCALE'])


        #Cluster size increased everytime the case is defined
        cluster_count += scale
 
        main.log.report("Increasing cluster size to "+
                str(cluster_count))
        install_result = main.FALSE
        
        if scale == 2:
            if cluster_count == 3:
                main.log.info("Installing nodes 2 and 3")
                install2_result = main.ONOSbench.onos_install(node=ONOS2_ip)
                install3_result = main.ONOSbench.onos_install(node=ONOS3_ip)
                cli2 = main.ONOS2cli.start_onos_cli(ONOS2_ip)
                cli3 = main.ONOS3cli.start_onos_cli(ONOS3_ip) 
            '''
            elif cluster_count == 5:

                main.log.info("Installing nodes 4 and 5")
                node4_result = main.ONOSbench.onos_install(node=ONOS4_ip)
                node5_result = main.ONOSbench.onos_install(node=ONOS5_ip)
                install_result = node4_result and node5_result
                time.sleep(5)

                main.ONOS4cli.start_onos_cli(ONOS4_ip)
                main.ONOS5cli.start_onos_cli(ONOS5_ip)

            elif cluster_count == 7:

                main.log.info("Installing nodes 4 and 5")
                node6_result = main.ONOSbench.onos_install(node=ONOS6_ip)
                node7_result = main.ONOSbench.onos_install(node=ONOS7_ip)
                install_result = node6_result and node7_result
                time.sleep(5)

                main.ONOS6cli.start_onos_cli(ONOS6_ip)
                main.ONOS7cli.start_onos_cli(ONOS7_ip)
            '''
        if scale == 1: 
            if cluster_count == 2:
                main.log.info("Installing node 2")
                install2_result = main.ONOSbench.onos_install(node=ONOS2_ip)
                cli2 = main.ONOS2cli.start_onos_cli(ONOS2_ip)

            if cluster_count == 3:
                main.log.info("Installing node 3")
                install3_result = main.ONOSbench.onos_install(node=ONOS3_ip)
                cli3 = main.ONOS3cli.start_onos_cli(ONOS3_ip)
    
    
    
    def CASE3(self,main):
        import time 
        import json
        import string
        
        intents_rate = main.params['JSON']['intents_rate']

        default_sw_port = main.params[ 'CTRL' ][ 'port1' ]

        main.Mininet1.assign_sw_controller(sw="1", ip1=ONOS1_ip, port1=default_sw_port )
        main.Mininet1.assign_sw_controller(sw="2", ip1=ONOS1_ip, port1=default_sw_port )
        main.Mininet1.assign_sw_controller(sw="3", ip1=ONOS1_ip, port1=default_sw_port )
        main.Mininet1.assign_sw_controller(sw="4", ip1=ONOS1_ip, port1=default_sw_port )
        main.Mininet1.assign_sw_controller(sw="5", ip1=ONOS1_ip, port1=default_sw_port )
        main.Mininet1.assign_sw_controller(sw="6", ip1=ONOS1_ip, port1=default_sw_port )
        main.Mininet1.assign_sw_controller(sw="7", ip1=ONOS1_ip, port1=default_sw_port )
        
        mn_arp = main.params['TEST']['arping']
        main.Mininet1.handle.sendline(mn_arp)

        generate_load = main.params['TEST']['loadstart']
   
        main.ONOS1.handle.sendline(generate_load)
        main.ONOS1.handle.expect("sdn")
        print("before: ", main.ONOS1.handle.before)
        print("after: ",main.ONOS1.handle.after)
        
        load_confirm = main.ONOS1.handle.after
        if load_confirm == "{}":
            main.log.info("Load started")

        else: 
            main.log.error("Load start failure")
            main.log.error("expected '{}', got: " + str(load_confirm))
     
        devices_json_str = main.ONOS1cli.devices()
        devices_json_obj = json.loads(devices_json_str)

        get_metric = main.params['TEST']['metric1']
        test_duration = main.params['TEST']['duration']
        stop = time.time() + float(test_duration)


        main.log.info("Starting test loop...")
        log_interval = main.params['TEST']['log_interval']

        while time.time() < stop: 
            time.sleep(float(log_interval))
         
            intents_json_str_1 = main.ONOS1cli.intents_events_metrics()
            intents_json_obj_1 = json.loads(intents_json_str_1)
            main.log.info("Node 1 rate: " + str(intents_json_obj_1[intents_rate]['m1_rate']))
            last_rate_1 = intents_json_obj_1[intents_rate]['m1_rate']
        
        stop_load = main.params['TEST']['loadstop']
        main.ONOS1.handle.sendline(stop_load)
        
        
        msg = ("Final rate on node 1: " + str(last_rate_1))
        main.log.report(msg)

    def CASE4(self, main):      #2 node scale 
        import time
        import json
        import string

        intents_rate = main.params['JSON']['intents_rate']
        
        default_sw_port = main.params[ 'CTRL' ][ 'port1' ]

        main.Mininet1.assign_sw_controller(sw="1", ip1=ONOS1_ip, port1=default_sw_port )
        main.Mininet1.assign_sw_controller(sw="2", ip1=ONOS2_ip, port1=default_sw_port )
        main.Mininet1.assign_sw_controller(sw="3", ip1=ONOS1_ip, port1=default_sw_port )
        main.Mininet1.assign_sw_controller(sw="4", ip1=ONOS2_ip, port1=default_sw_port )
        main.Mininet1.assign_sw_controller(sw="5", ip1=ONOS1_ip, port1=default_sw_port )
        main.Mininet1.assign_sw_controller(sw="6", ip1=ONOS2_ip, port1=default_sw_port )
        main.Mininet1.assign_sw_controller(sw="7", ip1=ONOS1_ip, port1=default_sw_port )

        mn_arp = main.params['TEST']['arping']
        main.Mininet1.handle.sendline(mn_arp)

        generate_load = main.params['TEST']['loadstart']

        main.ONOS1.handle.sendline(generate_load)
        main.ONOS2.handle.sendline(generate_load)

        devices_json_str_1 = main.ONOS1cli.devices()
        devices_json_obj_1 = json.loads(devices_json_str_1)
        devices_json_str_2 = main.ONOS2cli.devices()
        devices_json_obj_2 = json.loads(devices_json_str_2)

        get_metric = main.params['TEST']['metric1']
        test_duration = main.params['TEST']['duration']
        stop = time.time() + float(test_duration)


        main.log.info("Starting test loop...")
        log_interval = main.params['TEST']['log_interval']

        while time.time() < stop:
            time.sleep(float(log_interval))

            intents_json_str_1 = main.ONOS1cli.intents_events_metrics()
            intents_json_obj_1 = json.loads(intents_json_str_1)
            main.log.info("Node 1 rate: " + str(intents_json_obj_1[intents_rate]['m1_rate']))
            last_rate_1 = intents_json_obj_1[intents_rate]['m1_rate']
            
            intents_json_str_2 = main.ONOS2cli.intents_events_metrics()
            intents_json_obj_2 = json.loads(intents_json_str_2)
            main.log.info("Node 2 rate: " + str(intents_json_obj_2[intents_rate]['m1_rate']))
            last_rate_2 = intents_json_obj_2[intents_rate]['m1_rate']

        stop_load = main.params['TEST']['loadstop']
        main.ONOS1.handle.sendline(stop_load)
        main.ONOS2.handle.sendline(stop_load)


        msg = ("Final rate on node 1: " + str(last_rate_1))
        main.log.report(msg)
    
        msg = ("Final rate on node 2: " + str(last_rate_2))
        main.log.report(msg)



