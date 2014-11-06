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
                BENCH_ip, cell_name, MN1_ip, "onos-core",
                ONOS1_ip, ONOS2_ip, ONOS3_ip)

        main.step("Applying cell file to environment")
        cell_apply_result = main.ONOSbench.set_cell(cell_name)
        verify_cell_result = main.ONOSbench.verify_cell()

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

        main.step("Creating ONOS package")
        package_result = main.ONOSbench.onos_package()

        main.step("Installing ONOS package")
        install1_result = main.ONOSbench.onos_install(node=ONOS1_ip)
        install2_result = main.ONOSbench.onos_install(node=ONOS2_ip)
        install3_result = main.ONOSbench.onos_install(node=ONOS3_ip)

        main.step("Set cell for ONOScli env")
        main.ONOS1cli.set_cell(cell_name)
        main.ONOS2cli.set_cell(cell_name)
        main.ONOS3cli.set_cell(cell_name)

        time.sleep(5)

        main.step("Start onos cli")
        cli1 = main.ONOS1cli.start_onos_cli(ONOS1_ip)
        cli2 = main.ONOS2cli.start_onos_cli(ONOS2_ip)
        cli3 = main.ONOS3cli.start_onos_cli(ONOS3_ip)

        main.step("Enable metrics feature")
        main.ONOS1cli.feature_install("onos-app-metrics")
        main.ONOS2cli.feature_install("onos-app-metrics")
        main.ONOS3cli.feature_install("onos-app-metrics")

        utilities.assert_equals(expect=main.TRUE,
                actual = cell_file_result and cell_apply_result and\
                         verify_cell_result and checkout_result and\
                         pull_result and build_result and\
                         install1_result and install2_result and\
                         install3_result,
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

        devices_json_str = main.ONOS1cli.devices()
        devices_json_obj = json.loads(devices_json_str)

        device_id_list = []

        #Obtain device id list in ONOS format.
        #They should already be in order (1,2,3,10,11,12,13, etc)
        for device in devices_json_obj:
            device_id_list.append(device['id'])

        intent_add_lat_list = []

        for i in range(0, int(num_iter)):
            #add_point_intent(ingr_device, ingr_port, 
            #                 egr_device, egr_port)
            main.ONOS1cli.add_point_intent(
                device_id_list[0], 2,
                device_id_list[2], 1)
        
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
        CASE3 coming soon
        '''

