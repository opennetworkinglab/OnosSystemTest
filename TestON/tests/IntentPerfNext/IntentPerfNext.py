#Intent Performance Test for ONOS-next
#
#andrew@onlab.us
#
#November 5, 2014

class IntentPerfNext:
    def __init__(self):
        self.default = ""

    def CASE1(self, main):
        '''
        ONOS startup sequence
        '''

        import time
        global cluster_count
        cluster_count = 1 

        cell_name = main.params['ENV']['cellName']

        git_pull = main.params['GIT']['autoPull']
        checkout_branch = main.params['GIT']['checkout']

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS4_ip = main.params['CTRL']['ip4']
        ONOS5_ip = main.params['CTRL']['ip5']
        ONOS6_ip = main.params['CTRL']['ip6']
        ONOS7_ip = main.params['CTRL']['ip7']

        main.ONOSbench.onos_uninstall(node_ip=ONOS1_ip)
        main.ONOSbench.onos_uninstall(node_ip=ONOS2_ip)
        main.ONOSbench.onos_uninstall(node_ip=ONOS3_ip)
        main.ONOSbench.onos_uninstall(node_ip=ONOS4_ip)
        main.ONOSbench.onos_uninstall(node_ip=ONOS5_ip)
        main.ONOSbench.onos_uninstall(node_ip=ONOS6_ip)
        main.ONOSbench.onos_uninstall(node_ip=ONOS7_ip)

        MN1_ip = main.params['MN']['ip1']
        BENCH_ip = main.params['BENCH']['ip']
    
        main.case("Setting up test environment")

        main.step("Creating cell file")
        cell_file_result = main.ONOSbench.create_cell_file(
                BENCH_ip, cell_name, MN1_ip,
                "onos-core,onos-app-metrics,onos-gui",
                #ONOS1_ip, ONOS2_ip, ONOS3_ip)
                ONOS1_ip)

        main.step("Applying cell file to environment")
        cell_apply_result = main.ONOSbench.set_cell(cell_name)
        verify_cell_result = main.ONOSbench.verify_cell()

        main.step("Removing raft logs")
        main.ONOSbench.onos_remove_raft_logs()

        main.step("Git checkout and pull "+checkout_branch)
        if git_pull == 'on':
            checkout_result = \
                main.ONOSbench.git_checkout(checkout_branch)
            pull_result = main.ONOSbench.git_pull()
           
            #If you used git pull, auto compile
            main.step("Using onos-build to compile ONOS")
            build_result = main.ONOSbench.onos_build()
        else:
            checkout_result = main.TRUE
            pull_result = main.TRUE
            build_result = main.TRUE
            main.log.info("Git pull skipped by configuration")

        main.log.report("Commit information - ")
        main.ONOSbench.get_version(report=True)

        main.step("Creating ONOS package")
        package_result = main.ONOSbench.onos_package()

        main.step("Installing ONOS package")
        install1_result = main.ONOSbench.onos_install(node=ONOS1_ip)
        #install2_result = main.ONOSbench.onos_install(node=ONOS2_ip)
        #install3_result = main.ONOSbench.onos_install(node=ONOS3_ip)

        main.step("Set cell for ONOScli env")
        main.ONOS1cli.set_cell(cell_name)
        #main.ONOS2cli.set_cell(cell_name)
        #main.ONOS3cli.set_cell(cell_name)

        time.sleep(5)

        main.step("Start onos cli")
        cli1 = main.ONOS1cli.start_onos_cli(ONOS1_ip)
        #cli2 = main.ONOS2cli.start_onos_cli(ONOS2_ip)
        #cli3 = main.ONOS3cli.start_onos_cli(ONOS3_ip)

        utilities.assert_equals(expect=main.TRUE,
                actual = cell_file_result and cell_apply_result and\
                         verify_cell_result and checkout_result and\
                         pull_result and build_result and\
                         install1_result, #and install2_result and\
                         #install3_result,
                onpass="ONOS started successfully",
                onfail="Failed to start ONOS")

    def CASE2(self, main):
        '''
        Single intent add latency

        '''
        import time
        import json
        import requests
        import os

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS_user = main.params['CTRL']['user']

        default_sw_port = main.params['CTRL']['port1']

        #number of iterations of case
        num_iter = main.params['TEST']['numIter']

        #Timestamp keys for json metrics output
        submit_time = main.params['JSON']['submittedTime']
        install_time = main.params['JSON']['installedTime']
        wdRequest_time = main.params['JSON']['wdRequestTime']
        withdrawn_time = main.params['JSON']['withdrawnTime']
        
        intent_add_lat_list = []

        #Assign 'linear' switch format for basic intent testing
        main.Mininet1.assign_sw_controller(
                sw="1", ip1=ONOS1_ip,port1=default_sw_port)
        main.Mininet1.assign_sw_controller(
                sw="2", ip1=ONOS2_ip,port1=default_sw_port)
        main.Mininet1.assign_sw_controller(
                sw="3", ip1=ONOS2_ip,port1=default_sw_port)
        main.Mininet1.assign_sw_controller(
                sw="4", ip1=ONOS2_ip,port1=default_sw_port)
        main.Mininet1.assign_sw_controller(
                sw="5", ip1=ONOS3_ip,port1=default_sw_port)

        time.sleep(10)

        devices_json_str = main.ONOS1cli.devices()
        devices_json_obj = json.loads(devices_json_str)
        device_id_list = []

        #Obtain device id list in ONOS format.
        #They should already be in order (1,2,3,10,11,12,13, etc)
        for device in devices_json_obj:
            device_id_list.append(device['id'])

        for i in range(0, int(num_iter)):
            #add_point_intent(ingr_device,  egr_device,
            #                 ingr_port,    egr_port)
            main.ONOS1cli.add_point_intent(
                device_id_list[0]+"/1", device_id_list[4]+"/1")
        
            #Allow some time for intents to propagate
            time.sleep(5)

            #Obtain metrics from ONOS 1, 2, 3
            intents_json_str_1 = main.ONOS1cli.intents_events_metrics()
            intents_json_str_2 = main.ONOS2cli.intents_events_metrics()
            intents_json_str_3 = main.ONOS3cli.intents_events_metrics()

            intents_json_obj_1 = json.loads(intents_json_str_1)
            intents_json_obj_2 = json.loads(intents_json_str_2)
            intents_json_obj_3 = json.loads(intents_json_str_3)

            #Parse values from the json object
            intent_submit_1 = \
                    intents_json_obj_1[submit_time]['value']
            intent_submit_2 = \
                    intents_json_obj_2[submit_time]['value']
            intent_submit_3 = \
                    intents_json_obj_3[submit_time]['value']

            intent_install_1 = \
                    intents_json_obj_1[install_time]['value']
            intent_install_2 = \
                    intents_json_obj_2[install_time]['value']
            intent_install_3 = \
                    intents_json_obj_3[install_time]['value']

            intent_install_lat_1 = \
                    int(intent_install_1) - int(intent_submit_1)
            intent_install_lat_2 = \
                    int(intent_install_2) - int(intent_submit_2)
            intent_install_lat_3 = \
                    int(intent_install_3) - int(intent_submit_3)
            
            intent_install_lat_avg = \
                    (intent_install_lat_1 + 
                     intent_install_lat_2 +
                     intent_install_lat_3 ) / 3

            main.log.info("Intent add latency avg for iteration "+str(i)+
                    ": "+str(intent_install_lat_avg))

            if intent_install_lat_avg > 0.0 and \
               intent_install_lat_avg < 1000:
                intent_add_lat_list.append(intent_install_lat_avg)
            else:
                main.log.info("Intent add latency exceeded "+
                        "threshold. Skipping iteration "+str(i))

            time.sleep(3)
            
            #TODO: Possibly put this in the driver function
            main.log.info("Removing intents for next iteration")
            json_temp = \
                    main.ONOS1cli.intents(json_format=True)
            json_obj_intents = json.loads(json_temp)
            if json_obj_intents:
                for intents in json_obj_intents:
                    temp_id = intents['id']
                    main.ONOS1cli.remove_intent(temp_id)
                    main.log.info("Removing intent id: "+
                        str(temp_id))
                    main.ONOS1cli.remove_intent(temp_id)
            else:
                main.log.info("Intents were not installed correctly")

            time.sleep(5)

        intent_add_lat_min = min(intent_add_lat_list)
        intent_add_lat_max = max(intent_add_lat_list)
        intent_add_lat_avg = sum(intent_add_lat_list) /\
                             len(intent_add_lat_list)
        #END ITERATION FOR LOOP
        main.log.report("Single intent add latency - \n"+
                "Min: "+str(intent_add_lat_min)+" ms\n"+
                "Max: "+str(intent_add_lat_max)+" ms\n"+
                "Avg: "+str(intent_add_lat_avg)+" ms\n")


    def CASE3(self, main):
        '''
        Intent Reroute latency
        '''
        import time
        import json
        import requests
        import os

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS_user = main.params['CTRL']['user']

        default_sw_port = main.params['CTRL']['port1']

        #number of iterations of case
        num_iter = main.params['TEST']['numIter']

        #Timestamp keys for json metrics output
        submit_time = main.params['JSON']['submittedTime']
        install_time = main.params['JSON']['installedTime']
        wdRequest_time = main.params['JSON']['wdRequestTime']
        withdrawn_time = main.params['JSON']['withdrawnTime']

        devices_json_str = main.ONOS1cli.devices()
        devices_json_obj = json.loads(devices_json_str)

        device_id_list = []

        #Obtain device id list in ONOS format.
        #They should already be in order (1,2,3,10,11,12,13, etc)
        for device in devices_json_obj:
            device_id_list.append(device['id'])

        intent_reroute_lat_list = []

        print device_id_list

        for i in range(0, int(num_iter)):
            #add_point_intent(ingr_device, ingr_port, 
            #                 egr_device, egr_port)
            main.ONOS1cli.add_point_intent(
                device_id_list[0]+"/2", device_id_list[4]+"/1")
       
            time.sleep(5)

            intents_str = main.ONOS1cli.intents(json_format=True)
            intents_obj = json.loads(intents_str)
            for intent in intents_obj:
                if intent['state'] == "INSTALLED":
                    main.log.info("Intent installed successfully")
                    intent_id = intent['id']
                else:
                    #TODO: Add error handling
                    main.log.info("Intent installation failed")
                    intent_id = ""

            #NOTE: this interface is specific to
            #      topo-intentFlower.py topology
            #      reroute case.
            main.log.info("Disabling interface s2-eth3 <--> s4")
            main.Mininet1.handle.sendline(
                    "sh ifconfig s2-eth3 down")
            t0_system = time.time()*1000
                    
            #TODO: Check for correct intent reroute
            time.sleep(5)

            #Obtain metrics from ONOS 1, 2, 3
            intents_json_str_1 = main.ONOS1cli.intents_events_metrics()
            intents_json_str_2 = main.ONOS2cli.intents_events_metrics()
            intents_json_str_3 = main.ONOS3cli.intents_events_metrics()

            intents_json_obj_1 = json.loads(intents_json_str_1)
            intents_json_obj_2 = json.loads(intents_json_str_2)
            intents_json_obj_3 = json.loads(intents_json_str_3)

            #Parse values from the json object
            intent_install_1 = \
                    intents_json_obj_1[install_time]['value']
            intent_install_2 = \
                    intents_json_obj_2[install_time]['value']
            intent_install_3 = \
                    intents_json_obj_3[install_time]['value']

            intent_reroute_lat_1 = \
                    int(intent_install_1) - int(t0_system)
            intent_reroute_lat_2 = \
                    int(intent_install_2) - int(t0_system)
            intent_reroute_lat_3 = \
                    int(intent_install_3) - int(t0_system)
            
            intent_reroute_lat_avg = \
                    (intent_reroute_lat_1 + 
                     intent_reroute_lat_2 +
                     intent_reroute_lat_3 ) / 3
    
            main.log.info("Intent reroute latency avg for iteration "+
                    str(i)+": "+str(intent_reroute_lat_avg))

            if intent_reroute_lat_avg > 0.0 and \
               intent_reroute_lat_avg < 1000:
                intent_reroute_lat_list.append(intent_reroute_lat_avg)
            else:
                main.log.info("Intent reroute latency exceeded "+
                        "threshold. Skipping iteration "+str(i))

            #TODO: Possibly put this in the driver function
            main.log.info("Removing intents for next iteration")
            
            #NOTE: TODO: Currently, the remove intent will
            #            not trigger the intent request 
            #            timestamp. Thus we cannot use the same
            #            intent to get the latency over iterations.
            #            we can 1) install different intents every
            #            time, or 2) look into state machine and 
            #            determine what timestsamp to get
            main.ONOS1cli.remove_intent(intent_id)
            
        #TODO: Report framework
        print intent_reroute_lat_list


    def CASE4(self, main):
        import time
        import json
        import requests
        import os

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS4_ip = main.params['CTRL']['ip4']
        ONOS5_ip = main.params['CTRL']['ip5']
        ONOS6_ip = main.params['CTRL']['ip6']
        ONOS7_ip = main.params['CTRL']['ip7']
       
        ONOS_ip_list = []
        for i in range(1, 8):
            ONOS_ip_list.append(main.params['CTRL']['ip'+str(i)])

        ONOS_user = main.params['CTRL']['user']

        default_sw_port = main.params['CTRL']['port1']
    
        batch_intent_size = main.params['TEST']['batchIntentSize']
        batch_thresh_min = int(main.params['TEST']['batchThresholdMin'])
        batch_thresh_max = int(main.params['TEST']['batchThresholdMax'])

        #number of iterations of case
        num_iter = main.params['TEST']['numIter']
        num_switch = int(main.params['TEST']['numSwitch'])
        n_thread = main.params['TEST']['numMult']

        #*****
        global cluster_count
        #*****
       
        #Switch assignment NOTE: hardcoded 
        if cluster_count == 1:
            for i in range(1, num_switch+1):
                main.Mininet1.assign_sw_controller(
                    sw=str(i), 
                    ip1=ONOS1_ip,
                    port1=default_sw_port)
        if cluster_count == 3:
            for i in range(1, 3):
                main.Mininet1.assign_sw_controller(
                    sw=str(i),
                    ip1=ONOS1_ip,
                    port1=default_sw_port)
            for i in range(3, 6):
                main.Mininet1.assign_sw_controller(
                    sw=str(i),
                    ip1=ONOS2_ip,
                    port1=default_sw_port)
            for i in range(6, 9):
                main.Mininet1.assign_sw_controller(
                    sw=str(i),
                    ip1=ONOS3_ip,
                    port1=default_sw_port)
        if cluster_count == 5:
            main.Mininet1.assign_sw_controller(
                    sw="1",
                    ip1=ONOS1_ip,
                    port1=default_sw_port)
            main.Mininet1.assign_sw_controller(
                    sw="2",
                    ip1=ONOS2_ip,
                    port1=default_sw_port)
            for i in range(3, 6):
                main.Mininet1.assign_sw_controller(
                    sw=str(i),
                    ip1=ONOS3_ip,
                    port1=default_sw_port)
            main.Mininet1.assign_sw_controller(
                    sw="6",
                    ip1=ONOS4_ip,
                    port1=default_sw_port)
            main.Mininet1.assign_sw_controller(
                    sw="7",
                    ip1=ONOS5_ip,
                    port1=default_sw_port)
            main.Mininet1.assign_sw_controller(
                    sw="8",
                    ip1=ONOS5_ip,
                    port1=default_sw_port)
        
        if cluster_count == 7:
            for i in range(1,9):
                if i < 7:
                    main.Mininet1.assign_sw_controller(
                        sw=str(i),
                        ip1=ONOS_ip_list[i-1],
                        port1=default_sw_port)
                elif i >= 8: 
                    main.Mininet1.assign_sw_controller(
                        sw=str(i),
                        ip1=ONOS_ip_list[6],
                        port1=default_sw_port)

        main.log.report("Batch intent installation test of "+
               batch_intent_size +" intents")

        batch_result_list = []

        main.log.info("Getting list of available devices")
        device_id_list = []
        json_str = main.ONOS1cli.devices()
        json_obj = json.loads(json_str)
        for device in json_obj:
            device_id_list.append(device['id'])

        batch_install_lat = []
        batch_withdraw_lat = []
        
        base_dir = "/tmp/"

        for i in range(0, int(num_iter)):
            main.log.info("Pushing "+
                    str(int(batch_intent_size)*int(n_thread))+
                    " intents. Iteration "+str(i))
                
            for node in range(1, cluster_count+1):
                save_dir = base_dir + "batch_intent_"+str(node)+".txt" 
                main.ONOSbench.push_test_intents_shell(
                "of:0000000000000001/"+str(node),
                "of:0000000000000008/"+str(node),
                batch_intent_size, save_dir, ONOS_ip_list[node-1],
                num_mult=n_thread, app_id=node)
            
            time.sleep(120 / int(cluster_count))
            for node in range(1, cluster_count+1):
                with open(save_dir) as f_onos:
                    for line in f_onos:
                        line = line[1:]
                        line = line.split(": ")
                        result = line[1].split(" ")[0]
                        #TODO: add parameters before appending latency
                        if line_count == 0:
                            batch_install_lat.append(result)
                        elif line_count == 1:
                            batch_withdraw_lat.append(result)
                        line_count += 1
                main.log.info("Batch install latency for ONOS"+
                    str(node)+" with "+\
                    str(batch_intent_size) + "intents: "+\
                    str(batch_install_lat))
            time.sleep(5)

        main.log.report("Max of batch installation latency "+
            "for ONOS" + str(node)+ ": "+
            str(max(batch_install_lat)))
            
    def CASE5(self,main):
        '''
        Increase number of nodes and initiate CLI
        '''
        import time
        import json

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS4_ip = main.params['CTRL']['ip4']
        ONOS5_ip = main.params['CTRL']['ip5']
        ONOS6_ip = main.params['CTRL']['ip6']
        ONOS7_ip = main.params['CTRL']['ip7']

        global cluster_count
        cluster_count += 2
        main.log.info("Increasing cluster size to "+
                str(cluster_count))

        install_result = main.FALSE

        if cluster_count == 3:
            install_result1 = \
                main.ONOSbench.onos_install(node=ONOS2_ip)
            install_result2 = \
                main.ONOSbench.onos_install(node=ONOS3_ip)
            time.sleep(5)

            main.log.info("Starting ONOS CLI")
            main.ONOS2cli.start_onos_cli(ONOS2_ip)
            main.ONOS3cli.start_onos_cli(ONOS3_ip)

            install_result = install_result1 and install_result2

        if cluster_count == 5:
            main.log.info("Installing ONOS on node 4 and 5")
            install_result1 = \
                main.ONOSbench.onos_install(node=ONOS4_ip)
            install_result2 = \
                main.ONOSbench.onos_install(node=ONOS5_ip)

            main.log.info("Starting ONOS CLI")
            main.ONOS4cli.start_onos_cli(ONOS4_ip)
            main.ONOS5cli.start_onos_cli(ONOS5_ip)

            install_result = install_result1 and install_result2

        if cluster_count == 7:
            main.log.info("Installing ONOS on node 6 and 7")
            install_result1 = \
                main.ONOSbench.onos_install(node=ONOS6_ip)
            install_result2 = \
                main.ONOSbench.onos_install(node=ONOS7_ip)

            main.log.info("Starting ONOS CLI")
            main.ONOS6cli.start_onos_cli(ONOS6_ip)
            main.ONOS7cli.start_onos_cli(ONOS7_ip)

            install_result = install_result1 and install_result2

        time.sleep(5)

        if install_result == main.TRUE:
            assertion = main.TRUE
        else:
            assertion = main.FALSE

        utilities.assert_equals(expect=main.TRUE, actual=assertion,
            onpass="Scale out to "+str(cluster_count)+\
                   " nodes successful",
            onfail="Scale out to "+str(cluster_count)+\
                   " nodes failed")



