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
        import numpy
        global cluster_count

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS_ip_list = []
        for i in range(1, 8):
            ONOS_ip_list.append(main.params['CTRL']['ip'+str(i)])
        
        ONOS_user = main.params['CTRL']['user']

        default_sw_port = main.params['CTRL']['port1']

        #number of iterations of case
        num_iter = main.params['TEST']['numIter']
        num_ignore = int(main.params['TEST']['numIgnore'])

        #Timestamp keys for json metrics output
        submit_time = main.params['JSON']['submittedTime']
        install_time = main.params['JSON']['installedTime']
        wdRequest_time = main.params['JSON']['wdRequestTime']
        withdrawn_time = main.params['JSON']['withdrawnTime']
        
        assertion = main.TRUE

        intent_add_lat_list = []
        
        #Distribute switches according to cluster count
        for i in range(1, 9):
            if cluster_count == 1:
                main.Mininet1.assign_sw_controller(
                    sw=str(i), ip1=ONOS_ip_list[0],
                    port1=default_sw_port
                    )
            elif cluster_count == 3:
                if i < 3:
                    index = 0
                elif i < 6 and i >= 3:
                    index = 1
                else:
                    index = 2
                main.Mininet1.assign_sw_controller(
                    sw=str(i), ip1=ONOS_ip_list[index],
                    port1=default_sw_port
                    )
            elif cluster_count == 5:
                if i < 3:
                    index = 0
                elif i < 5 and i >= 3:
                    index = 1
                elif i < 7 and i >= 5:
                    index = 2
                elif i == 7:
                    index = 3
                else:
                    index = 4
                main.Mininet1.assign_sw_controller(
                    sw=str(i), ip1=ONOS_ip_list[index],
                    port1=default_sw_port
                    )
            elif cluster_count == 7:
                if i < 6:
                    index = i
                else:
                    index = 6
                main.Mininet1.assign_sw_controller(
                    sw=str(i), ip1=ONOS_ip_list[index],
                    port1=default_sw_port
                    )

        time.sleep(10)

        main.log.report("Single intent add latency test")

        devices_json_str = main.ONOS1cli.devices()
        devices_json_obj = json.loads(devices_json_str)
        
        if not devices_json_obj:
            main.log.report("Devices not discovered")
            main.log.report("Aborting test")
            main.exit()
        else:
            main.log.info("Devices discovered successfully")

        device_id_list = []

        #Obtain device id list in ONOS format.
        #They should already be in order (1,2,3,10,11,12,13, etc)
        for device in devices_json_obj:
            device_id_list.append(device['id'])

        for i in range(0, int(num_iter)):
            #add_point_intent(ingr_device,  egr_device,
            #                 ingr_port,    egr_port)
            main.ONOS1cli.add_point_intent(
                device_id_list[0]+"/2", device_id_list[7]+"/2")
        
            #Allow some time for intents to propagate
            time.sleep(5)
            
            intents_str = main.ONOS1cli.intents(json_format=True)
            intents_obj = json.loads(intents_str)
            for intent in intents_obj:
                if intent['state'] == "INSTALLED":
                    main.log.info("Intent installed successfully")
                    intent_id = intent['id']
                    main.log.info("Intent id: "+str(intent_id))
                else:
                    #TODO: Add error handling
                    main.log.info("Intent installation failed")
                    intent_id = ""

            #Obtain metrics from ONOS 1, 2, 3
            intents_json_str_1 = main.ONOS1cli.intents_events_metrics()
            intents_json_obj_1 = json.loads(intents_json_str_1)
            #Parse values from the json object
            intent_submit_1 = \
                    intents_json_obj_1[submit_time]['value']
            intent_install_1 = \
                    intents_json_obj_1[install_time]['value']
            intent_install_lat_1 = \
                    int(intent_install_1) - int(intent_submit_1)
            
            if cluster_count == 3: 
                intents_json_str_2 = main.ONOS2cli.intents_events_metrics()
                intents_json_str_3 = main.ONOS3cli.intents_events_metrics()
                intents_json_obj_2 = json.loads(intents_json_str_2)
                intents_json_obj_3 = json.loads(intents_json_str_3)
                intent_submit_2 = \
                    intents_json_obj_2[submit_time]['value']
                intent_submit_3 = \
                    intents_json_obj_3[submit_time]['value']
                intent_install_2 = \
                    intents_json_obj_2[install_time]['value']
                intent_install_3 = \
                    intents_json_obj_3[install_time]['value']
                intent_install_lat_2 = \
                    int(intent_install_2) - int(intent_submit_2)
                intent_install_lat_3 = \
                    int(intent_install_3) - int(intent_submit_3)
            else:
                intent_install_lat_2 = 0
                intent_install_lat_3 = 0

            if cluster_count == 5:
                intents_json_str_4 = main.ONOS4cli.intents_events_metrics()
                intents_json_str_5 = main.ONOS5cli.intents_events_metrics()
                intents_json_obj_4 = json.loads(intents_json_str_4)
                intents_json_obj_5 = json.loads(intents_json_str_5)
                intent_submit_4 = \
                    intents_json_obj_4[submit_time]['value']
                intent_submit_5 = \
                    intents_json_obj_5[submit_time]['value']
                intent_install_4 = \
                    intents_json_obj_5[install_time]['value']
                intent_install_5 = \
                    intents_json_obj_5[install_time]['value']
                intent_install_lat_4 = \
                    int(intent_install_4) - int(intent_submit_4)
                intent_install_lat_5 = \
                    int(intent_install_5) - int(intent_submit_5)
            else:
                intent_install_lat_4 = 0
                intent_install_lat_5 = 0

            if cluster_count == 7:
                intents_json_str_6 = main.ONOS6cli.intents_events_metrics()
                intents_json_str_7 = main.ONOS7cli.intents_events_metrics()
                intents_json_obj_6 = json.loads(intents_json_str_6)
                intents_json_obj_7 = json.loads(intents_json_str_7)
                intent_submit_6 = \
                    intents_json_obj_6[submit_time]['value']
                intent_submit_7 = \
                    intents_json_obj_6[submit_time]['value']
                intent_install_6 = \
                    intents_json_obj_6[install_time]['value']
                intent_install_7 = \
                    intents_json_obj_7[install_time]['value']
                intent_install_lat_6 = \
                    int(intent_install_6) - int(intent_submit_6)
                intent_install_lat_7 = \
                    int(intent_install_7) - int(intent_submit_7)
            else:
                intent_install_lat_6 = 0
                intent_install_lat_7 = 0

            intent_install_lat_avg = \
                    (intent_install_lat_1 + 
                     intent_install_lat_2 +
                     intent_install_lat_3 +
                     intent_install_lat_4 +
                     intent_install_lat_5 +
                     intent_install_lat_6 +
                     intent_install_lat_7) / cluster_count

            main.log.info("Intent add latency avg for iteration "+str(i)+
                    ": "+str(intent_install_lat_avg)+" ms")

            if intent_install_lat_avg > 0.0 and \
               intent_install_lat_avg < 1000 and i > num_ignore:
                intent_add_lat_list.append(intent_install_lat_avg)
            else:
                main.log.info("Intent add latency exceeded "+
                        "threshold. Skipping iteration "+str(i))

            time.sleep(3)
            
            #TODO: Only remove intents that were installed 
            #      in this case... Otherwise many other intents
            #      may show up distorting the results
            main.log.info("Removing intents for next iteration")
            json_temp = \
                    main.ONOS1cli.intents(json_format=True)
            json_obj_intents = json.loads(json_temp)
            if json_obj_intents:
                for intents in json_obj_intents:
                    temp_id = intents['id']
                    #main.ONOS1cli.remove_intent(temp_id)
                    main.log.info("Removing intent id: "+
                        str(temp_id))
                    main.ONOS1cli.remove_intent(temp_id)
            else:
                main.log.info("Intents were not installed correctly")

            time.sleep(5)

        if intent_add_lat_list:
            intent_add_lat_avg = sum(intent_add_lat_list) /\
                             len(intent_add_lat_list)
        else:
            main.log.report("Intent installation latency test failed")
            intent_add_lat_avg = "NA"
            assertion = main.FALSE

        intent_add_lat_std = \
            round(numpy.std(intent_add_lat_list),1)
        #END ITERATION FOR LOOP
        main.log.report("Single intent add latency - ")
        main.log.report("Avg: "+str(intent_add_lat_avg)+" ms")
        main.log.report("Std Deviation: "+str(intent_add_lat_std)+" ms")
        
        utilities.assert_equals(expect=main.TRUE, actual=assertion,
            onpass="Single intent install latency test successful",
            onfail="Single intent install latency test failed")

    def CASE3(self, main):
        '''
        Intent Reroute latency
        '''
        import time
        import json
        import requests
        import os
        import numpy
        global cluster_count

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS_user = main.params['CTRL']['user']

        default_sw_port = main.params['CTRL']['port1']

        #number of iterations of case
        num_iter = main.params['TEST']['numIter']
        num_ignore = int(main.params['TEST']['numIgnore'])
        assertion = main.TRUE

        #Timestamp keys for json metrics output
        submit_time = main.params['JSON']['submittedTime']
        install_time = main.params['JSON']['installedTime']
        wdRequest_time = main.params['JSON']['wdRequestTime']
        withdrawn_time = main.params['JSON']['withdrawnTime']

        #NOTE: May need to configure interface depending on topology
        intfs = main.params['TEST']['intfs']

        devices_json_str = main.ONOS1cli.devices()
        devices_json_obj = json.loads(devices_json_str)

        device_id_list = []

        #Obtain device id list in ONOS format.
        #They should already be in order (1,2,3,10,11,12,13, etc)
        for device in devices_json_obj:
            device_id_list.append(device['id'])

        intent_reroute_lat_list = []

        for i in range(0, int(num_iter)):
            #add_point_intent(ingr_device, ingr_port, 
            #                 egr_device, egr_port)
            if len(device_id_list) > 0:
                main.ONOS1cli.add_point_intent(
                    device_id_list[0]+"/2", device_id_list[7]+"/2")
            else:
                main.log.info("Failed to fetch devices from ONOS")

            time.sleep(5)

            intents_str = main.ONOS1cli.intents(json_format=True)
            intents_obj = json.loads(intents_str)
            for intent in intents_obj:
                if intent['state'] == "INSTALLED":
                    main.log.info("Intent installed successfully")
                    intent_id = intent['id']
                    main.log.info("Intent id: "+str(intent_id))
                else:
                    #TODO: Add error handling
                    main.log.info("Intent installation failed")
                    intent_id = ""
            
            main.log.info("Disabling interface "+intfs)
            t0_system = time.time()*1000
            main.Mininet1.handle.sendline(
                    "sh ifconfig "+intfs+" down")
            main.Mininet1.handle.expect("mininet>")    

            #TODO: Check for correct intent reroute
            time.sleep(1)

            #Obtain metrics from ONOS 1, 2, 3
            intents_json_str_1 = main.ONOS1cli.intents_events_metrics()
            intents_json_obj_1 = json.loads(intents_json_str_1)
            #Parse values from the json object
            intent_install_1 = \
                    intents_json_obj_1[install_time]['value']
            intent_reroute_lat_1 = \
                    int(intent_install_1) - int(t0_system)
            
            if cluster_count == 3:
                intents_json_str_2 = main.ONOS2cli.intents_events_metrics()
                intents_json_str_3 = main.ONOS3cli.intents_events_metrics()

                intents_json_obj_2 = json.loads(intents_json_str_2)
                intents_json_obj_3 = json.loads(intents_json_str_3)
                intent_install_2 = \
                    intents_json_obj_2[install_time]['value']
                intent_install_3 = \
                    intents_json_obj_3[install_time]['value']
                intent_reroute_lat_2 = \
                    int(intent_install_2) - int(t0_system)
                intent_reroute_lat_3 = \
                    int(intent_install_3) - int(t0_system)
            else:
                intent_reroute_lat_2 = 0
                intent_reroute_lat_3 = 0

            if cluster_count == 5:
                intents_json_str_4 = main.ONOS4cli.intents_events_metrics()
                intents_json_str_5 = main.ONOS5cli.intents_events_metrics()

                intents_json_obj_4 = json.loads(intents_json_str_4)
                intents_json_obj_5 = json.loads(intents_json_str_5)
                intent_install_4 = \
                    intents_json_obj_4[install_time]['value']
                intent_install_5 = \
                    intents_json_obj_5[install_time]['value']
                intent_reroute_lat_4 = \
                    int(intent_install_4) - int(t0_system)
                intent_reroute_lat_5 = \
                    int(intent_install_5) - int(t0_system)
            else:
                intent_reroute_lat_4 = 0
                intent_reroute_lat_5 = 0

            if cluster_count == 7:
                intents_json_str_6 = main.ONOS6cli.intents_events_metrics()
                intents_json_str_7 = main.ONOS7cli.intents_events_metrics()

                intents_json_obj_6 = json.loads(intents_json_str_6)
                intents_json_obj_7 = json.loads(intents_json_str_7)
                intent_install_6 = \
                    intents_json_obj_6[install_time]['value']
                intent_install_7 = \
                    intents_json_obj_7[install_time]['value']
                intent_reroute_lat_6 = \
                    int(intent_install_6) - int(t0_system)
                intent_reroute_lat_7 = \
                    int(intent_install_7) - int(t0_system)
            else:
                intent_reroute_lat_6 = 0
                intent_reroute_lat_7 = 0

            intent_reroute_lat_avg = \
                    (intent_reroute_lat_1 + 
                     intent_reroute_lat_2 +
                     intent_reroute_lat_3 +
                     intent_reroute_lat_4 +
                     intent_reroute_lat_5 +
                     intent_reroute_lat_6 +
                     intent_reroute_lat_7) / cluster_count 
    
            main.log.info("Intent reroute latency avg for iteration "+
                    str(i)+": "+str(intent_reroute_lat_avg))

            if intent_reroute_lat_avg > 0.0 and \
               intent_reroute_lat_avg < 1000 and i > num_ignore:
                intent_reroute_lat_list.append(intent_reroute_lat_avg)
            else:
                main.log.info("Intent reroute latency exceeded "+
                        "threshold. Skipping iteration "+str(i))

            main.log.info("Removing intents for next iteration")
            main.ONOS1cli.remove_intent(intent_id)

            main.log.info("Bringing Mininet interface up for next "+
                "iteration")
            main.Mininet1.handle.sendline(
                    "sh ifconfig "+intfs+" up")
            main.Mininet1.handle.expect("mininet>")

        if intent_reroute_lat_list:
            intent_reroute_lat_avg = sum(intent_reroute_lat_list) /\
                             len(intent_reroute_lat_list)
        else:
            main.log.report("Intent reroute test failed. Results NA")
            intent_reroute_lat_avg = "NA" 
            #NOTE: fails test when list is empty
            assertion = main.FALSE
        
        intent_reroute_lat_std = \
            round(numpy.std(intent_reroute_lat_list),1)
        #END ITERATION FOR LOOP
        main.log.report("Single intent reroute latency - ")
        main.log.report("Avg: "+str(intent_reroute_lat_avg)+" ms")
        main.log.report("Std Deviation: "+str(intent_reroute_lat_std)+" ms")
       
        utilities.assert_equals(expect=main.TRUE, actual=assertion,
            onpass="Single intent reroute latency test successful",
            onfail="Single intent reroute latency test failed")
        
    def CASE4(self, main):
        '''
        Batch intent install
        '''
        
        import time
        import json
        import requests
        import os
        import numpy
        global cluster_count

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS4_ip = main.params['CTRL']['ip4']
        ONOS5_ip = main.params['CTRL']['ip5']
        ONOS6_ip = main.params['CTRL']['ip6']
        ONOS7_ip = main.params['CTRL']['ip7']

        assertion = main.TRUE

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
        num_ignore = int(main.params['TEST']['numIgnore'])
        num_switch = int(main.params['TEST']['numSwitch'])
        n_thread = main.params['TEST']['numMult']
        #n_thread = 105

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
                if i < 8:
                    main.Mininet1.assign_sw_controller(
                        sw=str(i),
                        ip1=ONOS_ip_list[i-1],
                        port1=default_sw_port)
                elif i >= 8: 
                    main.Mininet1.assign_sw_controller(
                        sw=str(i),
                        ip1=ONOS_ip_list[6],
                        port1=default_sw_port)

        time.sleep(20)

        main.log.report("Batch intent installation test of "+
               batch_intent_size +" intent(s)")

        batch_result_list = []

        main.log.info("Getting list of available devices")
        device_id_list = []
        json_str = main.ONOS1cli.devices()
        json_obj = json.loads(json_str)
        for device in json_obj:
            device_id_list.append(device['id'])

        batch_install_lat = []
        batch_withdraw_lat = []
        
        #Max intent install measurement of all nodes
        max_install_lat = []
        max_withdraw_lat = []
        sleep_time = 10
        
        base_dir = "/tmp/"

        for batch in range(0, 5):
            for i in range(0, int(num_iter)):
                main.log.info("Pushing "+
                    str(int(batch_intent_size)*int(n_thread))+
                    " intents. Iteration "+str(i))
               
                for node in range(1, cluster_count+1):
                    save_dir = base_dir + "batch_intent_"+str(node)+".txt" 
                    main.ONOSbench.push_test_intents_shell(
                    device_id_list[0]+"/2",
                    device_id_list[7]+"/2",
                    int(batch_intent_size),
                    save_dir, ONOS_ip_list[node-1],
                    num_mult=n_thread, app_id=node)
         
                #Wait sufficient time for intents to start
                #installing
                time.sleep(sleep_time)

                intent = ""
                counter = 300
                while len(intent) > 0 and counter > 0:
                    main.ONOS1cli.handle.sendline(
                        "intents | wc -l")
                    main.ONOS1cli.handle.expect(
                        "intents | wc -l")
                    main.ONOS1cli.handle.expect(
                        "onos>")
                    intent_temp = main.ONOS1cli.handle.before()
                    intent = main.ONOS1cli.intents()
                    intent = json.loads(intent)
                    counter = counter-1
                    time.sleep(1)

                time.sleep(5)

                for node in range(1, cluster_count+1):
                    save_dir = base_dir + "batch_intent_"+str(node)+".txt"
                    with open(save_dir) as f_onos:
                        line_count = 0
                        for line in f_onos:
                            line = line[1:]
                            line = line.split(": ")
                            main.log.info("Line read: "+str(line))
                            result = line[1].split(" ")[0]
                            #TODO: add parameters before appending latency
                            if line_count == 0:
                                batch_install_lat.append(int(result))
                                install_result = result
                            elif line_count == 1:
                                batch_withdraw_lat.append(int(result))
                                withdraw_result = result
                            line_count += 1
                    main.log.info("Batch install latency for ONOS"+
                        str(node)+" with "+\
                        str(batch_intent_size) + "intents: "+\
                        str(install_result)+" ms")
                    main.log.info("Batch withdraw latency for ONOS"+
                        str(node)+" with "+
                        str(batch_intent_size) + "intents: "+
                        str(withdraw_result)+" ms")

                if len(batch_install_lat) > 0 and int(i) > num_ignore:
                    max_install_lat.append(max(batch_install_lat))
                elif len(batch_install_lat) == 0:
                    #If I failed to read anything from the file,
                    #increase the wait time before checking intents
                    sleep_time += 30
                if len(batch_withdraw_lat) > 0 and int(i) > num_ignore:
                    max_withdraw_lat.append(max(batch_withdraw_lat))
                batch_install_lat = []
                batch_withdraw_lat = []
    
                #Sleep in between iterations
                time.sleep(5)
            
            if max_install_lat:
                avg_install_lat = str(sum(max_install_lat) /\
                                  len(max_install_lat))
            else:
                avg_install_lat = "NA"
                main.log.report("Batch installation failed")
                assertion = main.FALSE

            if max_withdraw_lat:
                avg_withdraw_lat = str(sum(max_withdraw_lat) /\
                                   len(max_withdraw_lat))
            else:
                avg_withdraw_lat = "NA"
                main.log.report("Batch withdraw failed")
                assertion = main.FALSE

            main.log.report("Avg of batch installation latency "+
                "of size "+batch_intent_size+": "+
                str(avg_install_lat)+" ms")
            main.log.report("Std Deviation of batch installation latency "+
                ": "+str(numpy.std(max_install_lat))+" ms")

            main.log.report("Avg of batch withdraw latency "+
                "of size "+batch_intent_size+": "+
                str(avg_withdraw_lat)+" ms")
            main.log.report("Std Deviation of batch withdraw latency "+
                ": "+str(numpy.std(max_withdraw_lat))+" ms")
           
            batch_intent_size += 1000
            main.log.report("Increasing batch intent size to "+
                             batch_intent_size)
           
        #main.log.info("Removing all intents for next test case")
        #json_temp = main.ONOS1cli.intents(json_format=True)
        #json_obj_intents = json.loads(json_temp)
        #if json_obj_intents:
        #    for intents in json_obj_intents:
        #        temp_id = intents['id']
                #main.ONOS1cli.remove_intent(temp_id)
        #        main.ONOS1cli.remove_intent(temp_id)
        
        utilities.assert_equals(expect=main.TRUE, actual=assertion,
            onpass="Batch intent install/withdraw test successful",
            onfail="Batch intent install/withdraw test failed")

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
        main.log.report("Increasing cluster size to "+
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
    
    def CASE7(self, main):
        #TODO: Fix for scale-out scenario

        '''
        Batch intent reroute latency
        '''
        import time
        import json
        import requests
        import os
        import numpy
        global cluster_count

        ONOS_ip_list = []
        for i in range(1, 8):
            ONOS_ip_list.append(main.params['CTRL']['ip'+str(i)])

        ONOS_user = main.params['CTRL']['user']
        default_sw_port = main.params['CTRL']['port1']
    
        batch_intent_size = main.params['TEST']['batchIntentSize']
        batch_thresh_min = int(main.params['TEST']['batchThresholdMin'])
        batch_thresh_max = int(main.params['TEST']['batchThresholdMax'])
        intfs = main.params['TEST']['intfs']
        install_time = main.params['JSON']['installedTime']

        #number of iterations of case
        num_iter = main.params['TEST']['numIter']
        num_ignore = int(main.params['TEST']['numIgnore'])
        num_switch = int(main.params['TEST']['numSwitch'])
        n_thread = main.params['TEST']['numMult']

        main.log.report("Batch intent installation test of "+
               batch_intent_size +" intents")

        batch_result_list = []

        time.sleep(10)

        main.log.info("Getting list of available devices")
        device_id_list = []
        json_str = main.ONOS1cli.devices()
        json_obj = json.loads(json_str)
        for device in json_obj:
            device_id_list.append(device['id'])

        batch_install_lat = []
        batch_withdraw_lat = []
        sleep_time = 10
        
        base_dir = "/tmp/"
        max_install_lat = []

        for i in range(0, int(num_iter)):
            main.log.info("Pushing "+
                    str(int(batch_intent_size)*int(n_thread))+
                    " intents. Iteration "+str(i))

            main.ONOSbench.push_test_intents_shell(
                device_id_list[0]+"/2",
                device_id_list[7]+"/2",
                batch_intent_size, "/tmp/batch_install.txt",
                ONOS_ip_list[0], num_mult="1", app_id="1",
                report=False, options="--install")
            #main.ONOSbench.push_test_intents_shell(
            #    "of:0000000000001002/1",
            #    "of:0000000000002002/1",
            #    133, "/tmp/temp2.txt", "10.128.174.2",
            #    num_mult="6", app_id="2",report=False)
               
            #TODO: Check for installation success then proceed
            time.sleep(30)
            
            #NOTE: this interface is specific to
            #      topo-intentFlower.py topology
            #      reroute case.
            main.log.info("Disabling interface "+intfs)
            main.Mininet1.handle.sendline(
                    "sh ifconfig "+intfs+" down")
            t0_system = time.time()*1000

            #TODO: Wait sufficient time for intents to install
            time.sleep(10)

            #TODO: get intent installation time
            
            #Obtain metrics from ONOS 1, 2, 3
            intents_json_str_1 = main.ONOS1cli.intents_events_metrics()
            intents_json_obj_1 = json.loads(intents_json_str_1)
            #Parse values from the json object
            intent_install_1 = \
                    intents_json_obj_1[install_time]['value']
            intent_reroute_lat_1 = \
                    int(intent_install_1) - int(t0_system)
            
            
            if cluster_count == 3: 
                intents_json_str_2 =\
                    main.ONOS2cli.intents_events_metrics()
                intents_json_str_3 =\
                    main.ONOS3cli.intents_events_metrics()
                intents_json_obj_2 = json.loads(intents_json_str_2)
                intents_json_obj_3 = json.loads(intents_json_str_3)
                intent_install_2 = \
                    intents_json_obj_2[install_time]['value']
                intent_install_3 = \
                    intents_json_obj_3[install_time]['value']
                intent_reroute_lat_2 = \
                    int(intent_install_2) - int(t0_system)
                intent_reroute_lat_3 = \
                    int(intent_install_3) - int(t0_system)
            else:
                intent_reroute_lat_2 = 0
                intent_reroute_lat_3 = 0

            if cluster_count == 5:
                intents_json_str_4 =\
                    main.ONOS4cli.intents_events_metrics()
                intents_json_str_5 =\
                    main.ONOS5cli.intents_events_metrics()
                intents_json_obj_4 = json.loads(intents_json_str_4)
                intents_json_obj_5 = json.loads(intents_json_str_5)
                intent_install_4 = \
                    intents_json_obj_4[install_time]['value']
                intent_install_5 = \
                    intents_json_obj_5[install_time]['value']
                intent_reroute_lat_4 = \
                    int(intent_install_4) - int(t0_system)
                intent_reroute_lat_5 = \
                    int(intent_install_5) - int(t0_system)
            else:
                intent_reroute_lat_4 = 0
                intent_reroute_lat_5 = 0

            if cluster_count == 7:
                intents_json_str_6 =\
                    main.ONOS6cli.intents_events_metrics()
                intents_json_str_7 =\
                    main.ONOS7cli.intents_events_metrics()
                intents_json_obj_6 = json.loads(intents_json_str_6)
                intents_json_obj_7 = json.loads(intents_json_str_7)
                intent_install_6 = \
                    intents_json_obj_6[install_time]['value']
                intent_install_7 = \
                    intents_json_obj_7[install_time]['value']
                intent_reroute_lat_6 = \
                    int(intent_install_6) - int(t0_system)
                intent_reroute_lat_7 = \
                    int(intent_install_7) - int(t0_system)
            else:
                intent_reroute_lat_6 = 0
                intent_reroute_lat_7 = 0

            intent_reroute_lat_avg = \
                    (intent_reroute_lat_1 + 
                     intent_reroute_lat_2 +
                     intent_reroute_lat_3 +
                     intent_reroute_lat_4 + 
                     intent_reroute_lat_5 +
                     intent_reroute_lat_6 +
                     intent_reroute_lat_7) / cluster_count 
    
            main.log.info("Intent reroute latency avg for iteration "+
                    str(i)+": "+str(intent_reroute_lat_avg))
            #TODO: Remove intents for next iteration
            
            time.sleep(5)

            intents_str = main.ONOS1cli.intents()
            intents_json = json.loads(intents_str)
            for intents in intents_json:
                intent_id = intents['id']
                #TODO: make sure this removes all intents
                #print intent_id
                if intent_id:
                    main.ONOS1cli.remove_intent(intent_id)

            main.Mininet1.handle.sendline(
                    "sh ifconfig "+intfs+" up")
            
            main.log.info("Intents removed and port back up")

    def CASE9(self, main):
        count = 0
        sw_num1 = 1 
        sw_num2 = 1
        appid = 0
        port_num1 = 1
        port_num2 = 1
       
        time.sleep(30)

        while True:
            #main.ONOS1cli.push_test_intents(
                    #"of:0000000000001001/1",
                #"of:0000000000002001/1",
                #    100, num_mult="10", app_id="1")
            #main.ONOS2cli.push_test_intents(
            #    "of:0000000000001002/1",
            #    "of:0000000000002002/1",
            #    100, num_mult="10", app_id="2")
            #main.ONOS2cli.push_test_intents(
            #    "of:0000000000001003/1",
            #    "of:0000000000002003/1",
            #    100, num_mult="10", app_id="3")
            count += 1
           
            if count >= 100:
                main.ONOSbench.handle.sendline(
                    "onos 10.128.174.1 intents-events-metrics >>"+\
                    " /tmp/metrics_intents_temp.txt &")
                count = 0

            arg1 = "of:000000000000100"+str(sw_num1)+"/"+str(port_num1)
            arg2 = "of:000000000000200"+str(sw_num2)+"/"+str(port_num2)
            
            sw_num1 += 1

            if sw_num1 > 7:
                sw_num1 = 1
                sw_num2 += 1
                if sw_num2 > 7:
                    appid += 1

            if sw_num2 > 7:
                sw_num2 = 1
            
            main.ONOSbench.push_test_intents_shell(
                arg1,
                arg2, 
                100, "/tmp/temp.txt", "10.128.174.1",
                num_mult="10", app_id=appid,report=False)
            #main.ONOSbench.push_test_intents_shell(
            #    "of:0000000000001002/1",
            #    "of:0000000000002002/1",
            #    133, "/tmp/temp2.txt", "10.128.174.2",
            #    num_mult="6", app_id="2",report=False)
            #main.ONOSbench.push_test_intents_shell(
            #    "of:0000000000001003/1",
            #    "of:0000000000002003/1",
            #    133, "/tmp/temp3.txt", "10.128.174.3",
            #    num_mult="6", app_id="3",report=False)
   
            time.sleep(0.2)

