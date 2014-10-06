#Class TopoPerf
#Measures latency regarding topology events
#CASE2: add 1 switch latency
#CASE3: port up / down latency
#CASE4: link up / down latency
#CASE5: add 25 switch latency
#NOTE:
# * each case is iterated numIter times. Then min/max/avg is calculated based on results.
#   If an iteration is omitted, it means unexpected results were found (such as negative
#   delta of timestamps or delta that is too large) 
#   Each valid iteration is saved to a list 
#

#***********
#Google doc power point for overview:
#https://docs.google.com/a/onlab.us/presentation/d/1rnSDpAOm0IHv__U3PlwJiJuio3oYFWY7A17ZlWi5oTM/edit?usp=sharing
#***********

class TopoPerf:
    def __init__(self) :
        self.default = ''

#**********************
#CASE1
#Test startup
#**********************
    def CASE1(self,main) :  #Check to be sure ZK, Cass, and ONOS are up, then get ONOS version
        import time
        main.log.report("Initial setup")
        main.step("Stop ONOS") 
        main.ONOS1.stop()
        main.ONOS2.stop()
        main.ONOS3.stop()
        main.ONOS2.rest_stop()
        main.step("Start Zookeeper")
        time.sleep(5)
        main.Zookeeper1.start()
        main.Zookeeper2.start()
        main.Zookeeper3.start()
        #NOTE: I am currently using hazelcast. No need for deldb
        #main.step("Delete RC db")
        #time.sleep(5)
        #main.RamCloud1.del_db()
        #main.RamCloud2.del_db()
        #main.RamCloud3.del_db()
        main.step("Start ONOS")
        main.ONOS1.start()
        main.ONOS2.start()
        main.ONOS3.start()
        main.ONOS2.start_rest()
        time.sleep(3)
        main.step("Make sure core is started") 
        main.ONOS1.handle.sendline("./onos.sh core start")
        main.ONOS2.handle.sendline("./onos.sh core start")
        main.ONOS3.handle.sendline("./onos.sh core start")
        test= main.ONOS2.rest_status()
        if test == main.FALSE:
            main.ONOS2.start_rest()
        main.ONOS1.get_version()
        main.log.report("Startup check Zookeeper1, RamCloud1, and ONOS1 connections")
        main.step("Testing startup Zookeeper")   
        data =  main.Zookeeper1.isup()
        utilities.assert_equals(expect=main.TRUE,actual=data,
                onpass="Zookeeper is up!",onfail="Zookeeper is down...")
        main.step("Testing startup RamCloud")   
        data = main.RamCloud1.status_serv() and main.RamCloud2.status_serv() \
                and main.RamCloud3.status_serv() 
        if data == main.FALSE:
            main.RamCloud1.stop_coor()
            main.RamCloud1.stop_serv()
            main.RamCloud2.stop_serv()
            main.RamCloud3.stop_serv()

            time.sleep(10)
            main.RamCloud1.start_coor()
            main.RamCloud1.start_serv()
            main.RamCloud2.start_serv()
            main.RamCloud3.start_serv()
            time.sleep(10)
            data = main.RamCloud1.status_serv() and main.RamCloud2.status_serv()\
                    and main.RamCloud3.status_serv()
            
        utilities.assert_equals(expect=main.TRUE,actual=data,
                onpass="RamCloud is up!",onfail="RamCloud is down...")

        time.sleep(20)

#******************************************
#CASE2
#Assign s1 to  controller 1
#measure latency 
#******************************************
    def CASE2(self, main):
        import time
        import subprocess
        import json
        import requests
        import os
 
        ctrl_1 = main.params['CTRL']['ip1']
        ctrl_2 = main.params['CTRL']['ip2']
        ctrl_3 = main.params['CTRL']['ip3']
        port_1 = main.params['CTRL']['port1']
        port_2 = main.params['CTRL']['port2']
        port_3 = main.params['CTRL']['port3']
        rest_port = main.params['INTENTREST']['intentPort']

        url_suffix = main.params['TOPO']['url_topo']
        url_topo_1 = "http://"+ctrl_1+":"+rest_port+url_suffix
        url_topo_2 = "http://"+ctrl_2+":"+rest_port+url_suffix
        url_topo_3 = "http://"+ctrl_3+":"+rest_port+url_suffix 

        add_sw_threshold = main.params['LOG']['threshold']['switch_add1']
        logNameONOS1 = main.params['LOG']['logNameONOS1']
        logNameONOS2 = main.params['LOG']['logNameONOS2']
        logNameONOS3 = main.params['LOG']['logNameONOS3']
        logDir = main.params['LOG']['logDir']

        numIter = main.params['TOPO']['numIter']
        #Location of script that posts results to database
        db_script = main.params['TOPO']['databaseScript']
        table_name = main.params['TOPO']['tableName']
        postToDB = main.params['TOPO']['postToDB']

        #Directory/file to output the tshark results
        tshark_output = "/tmp/tshark_of_topo.txt"
        tshark_tcp = "/tmp/tshark_tcp_topo.txt"
        tshark_string_tcp = "TCP 74 "+port_1

        assertion = main.TRUE
        topo_lat = []
        tcp_lat = []

        main.log.report("Latency of adding one switch")

        for i in range(0, int(numIter)):
            main.step("Starting tshark open flow capture") 

            #NOTE: 
            #     * TCP [ACK, SYN] will be used as t0_a, the very first "exchange"
            #       between ONOS and the switch for end to end measurement
            #     * OFP [Stats Reply] will be used for t0_b, the very last OFP
            #       message between ONOS and the switch for ONOS measurement
            main.ONOS1.tshark_grep(tshark_string_tcp, tshark_tcp)
            main.ONOS1.tshark_grep("OFP 86 Vendor", tshark_output) 
            
            time.sleep(10) 

            #NOTE: We need to assign the switch in a specific way for perf measurements
            main.step("Assign s1 to controller and get timestamp")
            main.Mininet1.assign_sw_controller(sw="1",ip1=ctrl_1,port1=port_1)        
           
            time.sleep(10)
            main.ONOS1.stop_tshark()
            
            #NOTE: tshark output is saved in ONOS. Use subprocess to read file into TestON for parsing
            #TCP packet capture timestamp calculation
            ssh_tcp = subprocess.Popen(['ssh', 'admin@'+ctrl_1, 'cat', tshark_tcp],
                    stdout=subprocess.PIPE)
            text_tcp = ssh_tcp.stdout.readline()
            obj_tcp = text_tcp.split(" ")
            main.log.info("Object read in for TCP capture: "+str(text_tcp))
            if len(text_tcp) > 0:
                t0_tcp = int(float(obj_tcp[1])*1000)
            else:
                main.log.error("Tshark output file for TCP returned unexpected value")
                t0_tcp = 0
                assertion = main.FALSE

            #OFP capture timestamp calculation
            ssh_ofp = subprocess.Popen(['ssh', 'admin@'+ctrl_1, 'cat', tshark_output],
                    stdout=subprocess.PIPE) 
            #Read last line of Vendor Message (mastership role reply)
            while True:
                line = ssh_ofp.stdout.readline()
                if line != '':
                    text_ofp = line
                else:
                    break

            obj = text_ofp.split(" ")
            main.log.info("Object read in for OFP capture: "+str(text_ofp)) 
            if len(text_ofp) > 0:
                #NOTE: Important!
                #      Note that we are reading tshark object of index 1.
                #      This may differ with the tshark version. For older version of 
                #      tshark, you may need to get the tshark object of index 0
                #      to get the timestamp. 
                timestamp = int(float(obj[1])*1000)
                t0_ofp = timestamp
            else:
                main.log.error("Tshark output file returned unexpected value")
                t0_ofp = 0
                assertion = main.FALSE   

            main.step("Verify that switch s1 has been assigned properly") 
            s1_response = main.Mininet1.get_sw_controller(sw="s1")
            
            if s1_response == main.FALSE:
                main.log.error("Switch s1 was NOT assigned properly")
                assertion = main.FALSE
            else:
                main.log.info("Switch s1 was assigned properly!")
           
            #Obtain json object from all 3 ONOS instances.
            #The url distinguishes between different ONOS instance results.
            #The call to get_json indicated by ONOS1.get_json does not 
            #actually matter which ONOS instance calls it.
            json_obj_1 = main.ONOS1.get_json(url_topo_1) 
            json_obj_2 = main.ONOS2.get_json(url_topo_2)
            json_obj_3 = main.ONOS3.get_json(url_topo_3)

            print "JOSN OBJECT: "+ str(json_obj_1)

            #If all 3 json objects exist, parse dictionary to get end time
            if json_obj_1 != "" and json_obj_2 != "" and json_obj_3 != "": 
                topo_ms_end_1 = json_obj_1['gauges'][0]['gauge']['value']
                topo_ms_end_2 = json_obj_2['gauges'][0]['gauge']['value']
                topo_ms_end_3 = json_obj_3['gauges'][0]['gauge']['value']
            else:
                topo_ms_end_1 = 0
                topo_ms_end_2 = 0
                topo_ms_end_3 = 0

                assertion = main.FALSE

            #delta without switch negotiation
            delta_1 = int(topo_ms_end_1) - int(t0_ofp)
            delta_2 = int(topo_ms_end_2) - int(t0_ofp)
            delta_3 = int(topo_ms_end_3) - int(t0_ofp)

            #delta with switch negotiation (end-to-end) 
            delta_tcp1 = int(topo_ms_end_1) - int(t0_tcp)
            delta_tcp2 = int(topo_ms_end_2) - int(t0_tcp)
            delta_tcp3 = int(topo_ms_end_3) - int(t0_tcp)

            #If one of the delta exceeds the threshold, investigate onos-log
            if delta_1 > int(add_sw_threshold) or \
               delta_2 > int(add_sw_threshold) or \
               delta_3 > int(add_sw_threshold):
                log_result = main.ONOS1.tailLog(log_directory = logDir,
                        log_name = logNameONOS1, tail_length = 50)
                
                main.log.info("Latency calculation exceeded threshold of "+add_sw_threshold)
                main.log.info("Fetching onos-log for investigation: ")
                main.log.info(log_result)

            main.log.info("ONOS1 delta TCP: "+str(delta_tcp1))
            main.log.info("ONOS2 delta TCP: "+str(delta_tcp2))
            main.log.info("ONOS3 delta TCP: "+str(delta_tcp3))

            main.log.info("ONOS1 delta OFP: "+str(delta_1))
            main.log.info("ONOS2 delta OFP: "+str(delta_2))
            main.log.info("ONOS3 delta OFP: "+str(delta_3))

            #NOTE: Obtain average delta of the three clusters
            #IMPORTANT: we want to account for all ONOS instance processing time
            #           therefore we obtain the average of the three deltas across
            #           the instances. However, you may change it to either max 
            #           or min of the three deltas depending on future discussions
            if delta_1 > 0 and delta_1 < 100000:
                if delta_2 > 0 and delta_2 < 100000:
                    if delta_3 > 0 and delta_3 < 100000:
                        delta_avg = (delta_1 + delta_2 + delta_3) / 3
                    else:
                        delta_avg = (delta_1 + delta_2) / 2
                else:
                    delta_avg = delta_1
            else:
                main.log.info("Delta average OFP was not caluclated for iteration "+str(i))
                delta_avg = 0
            
            if delta_tcp1 > 0 and delta_tcp1 < 100000:
                if delta_tcp2 > 0 and delta_tcp2 < 100000:
                    if delta_tcp3 > 0 and delta_tcp3 < 100000:
                        delta_tcp = (delta_tcp1 + delta_tcp2 + delta_tcp3) / 3
                    else:
                        delta_tcp = (delta_tcp1 + delta_tcp2) / 2
                else:
                    delta_tcp = delta_tcp1
            else:
                main.log.info("Delta average TCP was not caluclated for iteration "+str(i))
                delta_tcp = 0

            time.sleep(5)

            main.step("Remove switch from controller s1")
            main.Mininet1.delete_sw_controller("s1")

            time.sleep(5)

            #NOTE: edit threshold as needed to fail test case
            #If outside threshold, delta is not saved to list.
            if delta_avg < 0.00001 or delta_avg > 100000:
                main.log.info("Delta OFP of switch add timestamp returned unexpected results")
                main.log.info("Value returned: " + str(delta_avg))
                main.log.info("Omitting iteration "+ str(i))
            else:
                topo_lat.append(delta_avg)
                main.log.info("One switch add latency OFP iteration "+
                        str(i)+": " + str(delta_avg) + " ms")  

            if delta_tcp < 0.00001 or delta_tcp > 100000:
                main.log.info("Delta TCP of switch add timestamp returned unexpected results")
                main.log.info("Value returned: " + str(delta_tcp))
                main.log.info("Omitting iteration "+ str(i))
            else:
                tcp_lat.append(delta_tcp)
                main.log.info("One switch add latency TCP iteration "+
                        str(i)+": "+str(delta_tcp) + " ms")

        #Omit the first 2 iterations to account for "warm-up" time of ONOS
        #Except when the list contains less than 2 values
        if len(topo_lat) > 2:
            topo_lat = topo_lat[2:]
            topo_lat_min = str(min(topo_lat))
            topo_lat_max = str(max(topo_lat))
            topo_lat_avg = str(sum(topo_lat) / len(topo_lat))
        else:
            topo_lat_max = 0
            main.log.report("Could not calculate min, max, avg"+
                " of OFP due to error in results")
        
        if len(tcp_lat) > 2:
            tcp_lat = tcp_lat[2:]
            tcp_lat_min = str(min(tcp_lat))
            tcp_lat_max = str(max(tcp_lat))
            tcp_lat_avg = str(sum(tcp_lat) / len(tcp_lat))
        else:
            tcp_lat_max = 0
            main.log.report("Could not calculate min, max, avg"+ 
                " of TCP due to error in results")

        #NOTE: configure threshold as needed here: 
        if int(topo_lat_max) > 0 and int(topo_lat_max) < 100000:
            assertion = main.TRUE
            if postToDB == 'on':
                os.system(db_script + " --name='1 switch add' --minimum='"+topo_lat_min+
                      "' --maximum='"+topo_lat_max+"' --average='"+topo_lat_avg+"' " + 
                      "--table='"+table_name+"'")
            else:
                main.log.report("Results were not posted to the database")
            #Calculate number of iterations that were omitted
            omit_num = int(numIter) - int(len(topo_lat)) 
            main.log.report("Iterations omitted/total: "+ str(omit_num) +"/"+ str(numIter))
            main.log.report("One switch add latency (ONOS processing only): Min: "+topo_lat_min+
                    " ms    Max: "+topo_lat_max+" ms    Avg: "+topo_lat_avg+" ms")
            main.log.report("One switch add latency (End to end): Min: "+tcp_lat_min+
                    " ms    Max: "+tcp_lat_max+" ms    Avg: "+tcp_lat_avg+" ms")

        else:
            assertion = main.FALSE
            main.log.report("Switch latency test NOT successful")
        
        utilities.assert_equals(expect=main.TRUE,actual=assertion,
                onpass="Switch latency test successful!",
                onfail="Switch latency test NOT successful")

#***************************************** 
#CASE3
#latency to enable or disable a port on switch 
#NOTE: Port enable / disable is simulated by 
#      ifconfig eth0 up / down
#      As of the date of development of this case,
#      port enable / disable is treated the same as
#      port add / remove
#***************************************** 
    def CASE3(self, main):
        import requests
        import json
        import time
        import os
        import subprocess

        tshark_output_up = "/tmp/tshark_of_port_up.txt"
        tshark_output_down = "/tmp/tshark_of_port_down.txt"
        assertion = main.TRUE
        
        ctrl_1 = main.params['CTRL']['ip1']
        ctrl_2 = main.params['CTRL']['ip2']
        ctrl_3 = main.params['CTRL']['ip3']

        port_1 = main.params['CTRL']['port1']
        port_2 = main.params['CTRL']['port2']
        port_3 = main.params['CTRL']['port3']

        numIter = main.params['TOPO']['numIter']
        db_script = main.params['TOPO']['databaseScript']
        table_name = main.params['TOPO']['tableName']
        postToDB = main.params['TOPO']['postToDB']

        port_up_threshold = main.params['LOG']['threshold']['port_up']
        port_down_threshold = main.params['LOG']['threshold']['port_down']
        logNameONOS1 = main.params['LOG']['logNameONOS1']
        logNameONOS2 = main.params['LOG']['logNameONOS2']
        logNameONOS3 = main.params['LOG']['logNameONOS3']
        logDir = main.params['LOG']['logDir']
        
        rest_port = main.params['INTENTREST']['intentPort']
        url_suffix = main.params['TOPO']['url_topo']
        url_topo_1= "http://"+ctrl_1+":"+rest_port+url_suffix
        url_topo_2 = "http://"+ctrl_2+":"+rest_port+url_suffix
        url_topo_3 = "http://"+ctrl_3+":"+rest_port+url_suffix 

        port_up_lat = []
        port_down_lat = []

        main.log.report("Port enable / disable latency") 

        main.step("Assign switch to controller")
        main.Mininet1.assign_sw_controller(sw="1",ip1=ctrl_1,port1=port_1) 
 
        main.step("Verify switch is assigned correctly")
        result_s1 = main.Mininet1.get_sw_controller(sw="s1")
        if result_s1 == main.FALSE:
            main.log.info("Switch s1 was NOT assigned correctly")
            assertion = main.FALSE
        else:
            main.log.info("Switch s1 was assigned correctly!")

        for i in range(0, int(numIter)):
            main.step("Starting wireshark capture for port status down")
            main.ONOS1.tshark_grep("OFP 130 Port Status", tshark_output_down)
            time.sleep(5)

            #Disabling port is emulated by disabling interface on that switch
            main.step("Disable port (interface s1-eth2)")
            main.Mininet2.handle.sendline("sudo ifconfig s1-eth2 down")
            main.Mininet2.handle.expect("\$")
            time.sleep(10)
        
            main.ONOS1.stop_tshark() 
            time.sleep(5)       
 
            ssh_down = subprocess.Popen(['ssh', 'admin@'+ctrl_1, 'cat', tshark_output_down],
                    stdout=subprocess.PIPE)
            text_down = ssh_down.stdout.readline()
            obj_down = text_down.split(" ")
            if len(text_down) > 0:
                timestamp_begin_pt_down = int(float(obj_down[1])*1000)
            else:
                timestamp_begin_pt_down = 0   

            main.step("Obtain t1 timestamp by REST call")

            #Obtain json objects from each ONOS instance
            json_obj_1 = main.ONOS1.get_json(url_topo_1)
            json_obj_2 = main.ONOS2.get_json(url_topo_2)
            json_obj_3 = main.ONOS3.get_json(url_topo_3)

            timestamp_end_pt_down_1 = json_obj_1['gauges'][0]['gauge']['value']
            timestamp_end_pt_down_2 = json_obj_2['gauges'][0]['gauge']['value']
            timestamp_end_pt_down_3 = json_obj_3['gauges'][0]['gauge']['value']

            delta_pt_down_1 = int(timestamp_end_pt_down_1) - int(timestamp_begin_pt_down)
            delta_pt_down_2 = int(timestamp_end_pt_down_2) - int(timestamp_begin_pt_down)
            delta_pt_down_3 = int(timestamp_end_pt_down_3) - int(timestamp_begin_pt_down)
            
            #If one of the delta exceeds the threshold, investigate onos-log
            if delta_pt_down_1 > int(port_down_threshold) or \
               delta_pt_down_2 > int(port_down_threshold) or \
               delta_pt_down_3 > int(port_down_threshold):
                log_result = main.ONOS1.tailLog(log_directory = logDir,
                        log_name = logNameONOS1, tail_length = 50)
                
                main.log.info("Latency calculation exceeded threshold of "+port_down_threshold)
                main.log.info("Fetching onos-log for investigation: ")
                main.log.info(log_result)

            #Check values of delta_pt_down and calculate average
            if delta_pt_down_1 > 0 and delta_pt_down_1 < 100000:
                if delta_pt_down_2 > 0 and delta_pt_down_2 < 100000:
                    if delta_pt_down_3 > 0 and delta_pt_down_3 < 100000:
                        delta_pt_down_avg = \
                            (delta_pt_down_1 + delta_pt_down_2 + delta_pt_down_3) / 3
                    else:
                        delta_pt_down_avg = \
                            (delta_pt_down_1 + delta_pt_down_2) / 2
                else:
                    delta_pt_down_avg = delta_pt_down_1
            #NOTE: If first delta calculation is not valid, just set average to 0
            #      this is more or less a lazy method, so FIXME if needed
            else:
                delta_pt_down_avg = 0

            #NOTE: modify threshold as necessary
            if (delta_pt_down_avg < 0.00001) or (delta_pt_down_avg > 100000):
                main.log.info("Delta port down timestamp returned unexpected results")
                main.log.info("ONOS1 Value returned: " + str(delta_pt_down_avg))
                main.log.info("Omitting iteration "+ str(i))
                assertion = main.FALSE
            else:
                port_down_lat.append(delta_pt_down_avg)     
                main.log.info("Port down latency iteration "+str(i)+": "+str(delta_pt_down_avg)+" ms")
 
            #Port status up case 
            main.step("Enable port and obtain timestamp via REST") 
            main.step("Starting wireshark capture for port status up")
            main.ONOS1.tshark_grep("OFP 130 Port Status", tshark_output_up)
            time.sleep(10)
        
            main.Mininet2.handle.sendline("sudo ifconfig s1-eth2 up")
            main.Mininet2.handle.expect("\$")
            time.sleep(10)
 
            main.ONOS1.stop_tshark()
            time.sleep(5)
 
            ssh_up = subprocess.Popen(['ssh', 'admin@'+ctrl_1, 'cat', tshark_output_up],
                    stdout=subprocess.PIPE)
            text1 = ssh_up.stdout.readline()
            #read second line. Port up status will produce two port status packets.
            #the last port status packet indicates that the port is usable. 
            #Hence why we take the second line as a timestamp.
            text_up = ssh_up.stdout.readline()
            obj_up = text_up.split(" ")
            obj_up1 = text1.split(" ")
            if len(text_up) > 0:
                timestamp_begin_pt_up = int(float(obj_up[1])*1000)
            elif len(text1) > 0: 
                timestamp_begin_pt_up = int(float(obj_up1[1])*1000)
            else:
                timestamp_begin_pt_up = 0

            json_obj_up_1 = main.ONOS1.get_json(url_topo_1)
            json_obj_up_2 = main.ONOS2.get_json(url_topo_2)
            json_obj_up_3 = main.ONOS3.get_json(url_topo_3)

            timestamp_end_pt_up_1 = json_obj_up_1['gauges'][0]['gauge']['value']
            timestamp_end_pt_up_2 = json_obj_up_2['gauges'][0]['gauge']['value']
            timestamp_end_pt_up_3 = json_obj_up_3['gauges'][0]['gauge']['value']
        
            delta_pt_up_1 = int(timestamp_end_pt_up_1) - int(timestamp_begin_pt_up)
            delta_pt_up_2 = int(timestamp_end_pt_up_2) - int(timestamp_begin_pt_up)
            delta_pt_up_3 = int(timestamp_end_pt_up_3) - int(timestamp_begin_pt_up)
            
            #If one of the delta exceeds the threshold, investigate onos-log
            if delta_pt_up_1 > int(port_up_threshold) or \
               delta_pt_up_2 > int(port_up_threshold) or \
               delta_pt_up_3 > int(port_up_threshold):
                log_result = main.ONOS1.tailLog(log_directory = logDir,
                        log_name = logNameONOS1, tail_length = 50)
                
                main.log.info("Latency calculation exceeded threshold of "+port_up_threshold)
                main.log.info("Fetching onos-log for investigation: ")
                main.log.info(log_result)

            if delta_pt_up_1 > 0 and delta_pt_up_1 < 100000:
                if delta_pt_up_2 > 0 and delta_pt_up_2 < 100000:
                    if delta_pt_up_3 > 0 and delta_pt_up_3 < 100000:
                        delta_pt_up_avg = \
                            (delta_pt_up_1 + delta_pt_up_2 + delta_pt_up_3) / 3
                    else:
                        delta_pt_up_avg = \
                            (delta_pt_up_1 + delta_pt_up_2) / 2
                else:
                    delta_pt_up_avg = delta_pt_up_1
            else:
                delta_pt_up_avg = 0

            #NOTE: modify threshold as necessary
            if (delta_pt_up_avg < 0.00001) or (delta_pt_up_avg > 100000):
                main.log.info("Delta of timestamp returned unexpected results")
                main.log.info("Value returned: " + str(delta_pt_up_avg))
                main.log.info("Omitting iteration "+ str(i))
                assertion = main.FALSE
            else:
                port_up_lat.append(delta_pt_up_avg)           
                main.log.info("Port up latency iteration "+str(i)+": "+str(delta_pt_up_avg)+" ms")
  
            time.sleep(5)

        if len(port_up_lat) > 2 and len(port_down_lat) > 2:
            port_up_lat = port_up_lat[2:]
            port_up_lat_min = str(min(port_up_lat))
            port_up_lat_max = str(max(port_up_lat))
            port_up_lat_avg = str(sum(port_up_lat) / len(port_up_lat))
 
            port_down_lat = port_down_lat[2:]
            port_down_lat_min = str(min(port_down_lat))
            port_down_lat_max = str(max(port_down_lat))
            port_down_lat_avg = str(sum(port_down_lat) / len(port_down_lat))
        else:
            main.log.report("Port event latency could not be calculated due to errors in results")

        #NOTE: configure threshold as needed
        if int(port_up_lat_avg) > 0 and int(port_down_lat_avg) > 0:
            assertion = main.TRUE
            if postToDB == 'on':
                os.system(db_script + " --name='Switch Port Down' --minimum='"+port_down_lat_min+
                      "' --maximum='"+port_down_lat_max+"' --average='"+port_down_lat_avg+
                      "' --table='"+table_name+"'")
                os.system(db_script + " --name='Switch Port Up' --minimum='"+port_up_lat_min+
                      "' --maximum='"+port_up_lat_max+"' --average='"+port_up_lat_avg+
                      "' --table='"+table_name+"'")
            else:
                main.log.report("Results were not posted to the database")

        omit_num_up = int(numIter) - int(len(port_up_lat))
        omit_num_down = int(numIter) - int(len(port_down_lat))
        main.log.report("Iterations omitted/total for Port Up Latency: "+
                str(omit_num_up) +"/"+ str(numIter))
        main.log.report("Iterations omitted/total for Port Down Latency: "+
                str(omit_num_down) + "/" + str(numIter))
        main.log.report("Port up latency: Min: "+port_up_lat_min+" ms    Max: "+
                port_up_lat_max+" ms    Avg: "+port_up_lat_avg+" ms")
        main.log.report("Port down latency: Min: "+port_down_lat_min+" ms    Max: "+
                port_down_lat_max+" ms Avg: "+port_down_lat_avg+" ms")
 
        utilities.assert_equals(expect=main.TRUE,actual=assertion,
                onpass="Port latency test successful!",
                onfail="Port latency test NOT successful")

#***************************************
#CASE4
#Time to add or remove a link between two switches 
#We expect link state discovery return a large fluctuation of latency numbers.
#This, we suspect, is primarily due to LLDP timing that is needed for link state discovery 
#NOTE: This may change in the future to include a finer granularity of measurement
#***************************************
    def CASE4(self,main):
        import requests
        import json
        import time 
        import subprocess
        import os

        assertion = main.TRUE
        ctrl_1 = main.params['CTRL']['ip1']
        ctrl_2 = main.params['CTRL']['ip2']
        ctrl_3 = main.params['CTRL']['ip3']

        port_1 = main.params['CTRL']['port1']
        
        url_links = main.params['TOPO']['url_links']
        numIter = main.params['TOPO']['numIter']
        db_script = main.params['TOPO']['databaseScript']
        table_name = main.params['TOPO']['tableName']
        postToDB = main.params['TOPO']['postToDB']

        switch1_mac = main.params['TOPO']['switch1']
        switch3_mac = main.params['TOPO']['switch3']
        
        link_up_threshold = main.params['LOG']['threshold']['link_up']
        link_down_threshold = main.params['LOG']['threshold']['link_down']
        logNameONOS1 = main.params['LOG']['logNameONOS1']
        logNameONOS2 = main.params['LOG']['logNameONOS2']
        logNameONOS3 = main.params['LOG']['logNameONOS3']
        logDir = main.params['LOG']['logDir']
        
        rest_port = main.params['INTENTREST']['intentPort']
        url_suffix = main.params['TOPO']['url_topo']
        url_topo_1 = "http://"+ctrl_1+":"+rest_port+url_suffix
        url_topo_2 = "http://"+ctrl_2+":"+rest_port+url_suffix
        url_topo_3 = "http://"+ctrl_3+":"+rest_port+url_suffix 

        link_down_lat = []
        link_up_lat = []

        main.log.report("Add / remove link latency between two switches")

        main.step("Assign all switches")
        main.Mininet1.assign_sw_controller(sw="1",ip1=ctrl_1,port1=port_1)
        time.sleep(5)
        main.Mininet1.assign_sw_controller(sw="2",ip1=ctrl_1,port1=port_1)
        time.sleep(5)
        main.Mininet1.assign_sw_controller(sw="3",ip1=ctrl_1,port1=port_1)
        time.sleep(5)

        main.step("Verify assignment of switches")
        result_s1 = main.Mininet1.get_sw_controller(sw="s1")
        result_s2 = main.Mininet1.get_sw_controller(sw="s2")
        result_s3 = main.Mininet1.get_sw_controller(sw="s3")

        if result_s1 != main.FALSE and result_s2 != main.FALSE and result_s3 != main.FALSE:
            main.log.report("Switches s1, s2, and s3 assigned successfully")
        else:
            main.log.error("Error assigning switches s1, s2, and s3 to controller "+str(ctrl_1))
            main.log.error("Result s1 returned: " + str(result_s1))
            main.log.error("Result s2 returned: " + str(result_s2))
            main.log.error("Result s3 returned: " + str(result_s3))
            assertion = main.FALSE

        time.sleep(5)

        for i in range(0, int(numIter)):
            #NOTE: There is no method to obtain link down event via tshark because no Open flow message
            #is provided for a link down event. Instead, we must wait for ONOS to discover that there
            #is a problem with the link
            main.step("Initial timestamp (system time via time.time()) for link disabled")
            timestamp_link_begin = time.time() * 1000 
            main.Mininet1.handle.sendline("sh tc qdisc add dev s1-eth2 root netem loss 100%")
            #The above line sends a shell command tc qdisc which is part of the linux kernel's method of
            #traffic control. network emulator (netem) can then be added on to simulate link loss rate
            
            #The below line has the same functionality as the one above so it may be obsolete. 
            #However, you may want to try it in case the line above does not work as expected. 
            #main.Mininet2.handle.sendline("sudo tc qdisc add dev s1-eth2 root netem loss 100")
         
            #this step call came after the actual event to reduce latency gap between the 
            #Timestamp and link cut
            main.step("Disabling link on s1") 

            #NOTE: This sleep is critical to ensure that get_json has enough time to detect and fetch 
            #the necessary object. If you find that get_json has trouble returning an object,
            #check the url, since the rest call is subject to change
            #Furthermore, this sleep should not affect the latency measurement because 
            #current implementation of link down discovery takes much longer than 5 seconds. 
            #At the time of writing this code, link down is discovered via
            #LLDP timeout
            time.sleep(5)

            #This segment of code calls REST to check for 2 things:
            #1) changes to timestamp of url_topo which indicates that there has been a topology change
            #2) changes to url_links, specifically the existence of link between s1 -> s3, which is the 
            #   link we cut. Note that method used  is a UNIDIRECTIONAL cut. Which means link between
            #   s3 -> s1 still persists
            counter = 0
            temp_timestamp_1 = "" 
            temp_timestamp_2 = "" 
            temp_timestamp_3 = "" 
            timestamp_diff = False
            link_cut_detected = False
         
            main.step("Calling REST to detect link change event... please wait")
            while counter < 60:
                json_obj_up_1 = main.ONOS1.get_json(url_topo_1)
                json_obj_up_2 = main.ONOS2.get_json(url_topo_2)
                json_obj_up_3 = main.ONOS3.get_json(url_topo_3)

                json_topo = main.ONOS1.get_json(url_links)
         
                timestamp_diff = True
                timestamp_link_end_1 = json_obj_up_1['gauges'][0]['gauge']['value']
                timestamp_link_end_2 = json_obj_up_2['gauges'][0]['gauge']['value']
                timestamp_link_end_3 = json_obj_up_3['gauges'][0]['gauge']['value']
               
                #If all temporary timestamps match the json object timestamp
                #     (which means timestamp has stopped changing)  
                if temp_timestamp_1 == timestamp_link_end_1:
                    if temp_timestamp_2 == timestamp_link_end_2:
                        if temp_timestamp_3 == timestamp_link_end_3:
                            timestamp_diff = False

                temp_timestamp_1 = timestamp_link_end_1 
                temp_timestamp_2 = timestamp_link_end_2
                temp_timestamp_3 = timestamp_link_end_3

                link_cut_detected = True
                #get length of json list to loop a correct amount. Otherwise we will get index out of range
                list_len = len(json_topo)
                #NOTE: Loop through all available switches and check for switch link 1->3
                # If the link does not exist, trigger break 
                for j in range(0, list_len):
                    s1 = json_topo[j]['src']['dpid']
                    s3 = json_topo[j]['dst']['dpid']
                    #As long as there is a dpid match in s1->s3, we have a link
                    if s1 == switch1_mac and s3 == switch3_mac:
                        link_cut_detected = False
                if timestamp_diff:
                    #timestamp_diff is not the most significant change to detect, but it is the 
                    #first category to check that indicates topology has changed (link is cut) 
                    main.log.info("Timestamp difference in REST call detected")
                    if link_cut_detected:
                        main.log.info("Link cut detected between s1 -> s3")
                        break
                if link_cut_detected:
                    #Only link cut is detected. Again, not an error, but may indicate some lack of 
                    #Code sanity in the loop. 
                    main.log.info("Link cut detected between s1 -> s3 but no timestamp diff")
                    main.log.info("This is most likely due to link cut detected before the second REST call")       
                    break               
                counter = counter+1
                
                #NOTE: This sleep does not deter from the performance measurement. When the correct 
                #      timestamp is obtained via REST, it has already internally captured the
                #      ending timestamp t1. Therefore, even if we spend a long time waiting here,
                #      the t1 will not change. 
                time.sleep(3)            

            delta_timestamp_1 = int(timestamp_link_end_1) - int(timestamp_link_begin)
            delta_timestamp_2 = int(timestamp_link_end_2) - int(timestamp_link_begin)
            delta_timestamp_3 = int(timestamp_link_end_3) - int(timestamp_link_begin)
            
            #If one of the delta exceeds the threshold, investigate onos-log
            if delta_timestamp_1 > int(link_down_threshold) or \
               delta_timestamp_2 > int(link_down_threshold) or \
               delta_timestamp_3 > int(link_down_threshold):
                log_result = main.ONOS1.tailLog(log_directory = logDir,
                        log_name = logNameONOS1, tail_length = 50)
                
                main.log.info("Latency calculation exceeded threshold of "+link_down_threshold)
                main.log.info("Fetching onos-log for investigation: ")
                main.log.info(log_result)
            
            if delta_timestamp_1 > 0 and delta_timestamp_1 < 100000:
                if delta_timestamp_2 > 0 and delta_timestamp_2 < 100000:
                    if delta_timestamp_3 > 0 and delta_timestamp_3 < 100000:
                        delta_timestamp_avg = \
                            (delta_timestamp_1 + delta_timestamp_2 + delta_timestamp_3) / 3
                    else:
                        delta_timestamp_avg = \
                            (delta_timestamp_1 + delta_timestamp_2) / 2
                else:
                    delta_timestamp_avg = delta_timestamp_1
            else:
                delta_timestamp_avg = 0

            if delta_timestamp_avg < 0 or delta_timestamp_avg > 100000:
                main.log.info("Delta of timestamp returned unexpected results")
                main.log.info("Value returned: " + str(delta_timestamp_avg))
                main.log.info("Omitting iteration "+ str(i))
                assertion = main.FALSE
            else:
                link_down_lat.append(delta_timestamp_avg)
                main.log.info("Link down discovery latency iteration "+str(i)+": "+
                        str(delta_timestamp_avg)+" ms")

            time.sleep(5)

            #Enable link and get timestamp
            main.step("Initial timestamp (system time via time.time()) for link enabled")
            timestamp_link_enable_t0 = time.time() * 1000
            #NOTE: Remove previous 100% packet loss on an interface
            #Note the different method used for tc qdisc. We do not set the loss rate back down to 0.
            #This will not work as expected. Instead we must remove all rules set by qdisc previously
            main.Mininet1.handle.sendline("sh tc qdisc del dev s1-eth2 root")
            #main.Mininet2.handle.sendline("sudo tc qdisc del dev s1-eth2 root")
            main.step("Enabling link on s1")

            time.sleep(1)
 
            counter = 0
            temp_timestamp_1 = ""
            temp_timestamp_2 = ""
            temp_timestamp_3 = ""
            link_enable_detected = False
            timestamp_diff = False

            main.step("Calling REST to detect link change event... please wait")
            while counter < 60:
                json_obj_up_1 = main.ONOS1.get_json(url_topo_1)
                json_obj_up_2 = main.ONOS2.get_json(url_topo_2)
                json_obj_up_3 = main.ONOS3.get_json(url_topo_3)
                
                json_topo = main.ONOS1.get_json(url_links)
                
                timestamp_diff = True
                timestamp_link_enable_t1 = json_obj_up_1['gauges'][0]['gauge']['value']
                timestamp_link_enable_t2 = json_obj_up_2['gauges'][0]['gauge']['value']
                timestamp_link_enable_t3 = json_obj_up_3['gauges'][0]['gauge']['value']
                
                if temp_timestamp_1 == timestamp_link_enable_t1:
                    if temp_timestamp_2 == timestamp_link_enable_t2:
                        if temp_timestamp_3 == timestamp_link_enable_t3:
                            timestamp_diff = False

                temp_timestamp_1 = timestamp_link_enable_t1
                temp_timestamp_2 = timestamp_link_enable_t2
                temp_timestamp_3 = timestamp_link_enable_t3

                link_enable_detected = False
                list_len = len(json_topo)
                for k in range(0, list_len):
                    s1 = json_topo[k]['src']['dpid']
                    s3 = json_topo[k]['dst']['dpid']
                    if s1 == switch1_mac and s3 == switch3_mac:
                        link_enable_detected = True
                if timestamp_diff:
                    main.log.info("Timestamp difference in REST call detected")
                    if link_enable_detected:
                        main.log.info("Link enable detected between s1 -> s3")
                        break
                if link_enable_detected:
                    main.log.info("Link enable detected between s1 -> s3 but no timestamp diff")
                    break
                counter = counter+1
                time.sleep(3)

            delta_timestamp_enable_1 = int(timestamp_link_enable_t1) - int(timestamp_link_enable_t0)
            delta_timestamp_enable_2 = int(timestamp_link_enable_t2) - int(timestamp_link_enable_t0)
            delta_timestamp_enable_3 = int(timestamp_link_enable_t3) - int(timestamp_link_enable_t0)
            
            #If one of the delta exceeds the threshold, investigate onos-log
            if delta_timestamp_enable_1 > int(link_up_threshold) or \
               delta_timestamp_enable_2 > int(link_up_threshold) or \
               delta_timestamp_enable_3 > int(link_up_threshold):
                log_result = main.ONOS1.tailLog(log_directory = logDir,
                        log_name = logNameONOS1, tail_length = 50)
                
                main.log.info("Latency calculation exceeded threshold of "+link_up_threshold)
                main.log.info("Fetching onos-log for investigation: ")
                main.log.info(log_result)
        
            if delta_timestamp_enable_1 > 0 and delta_timestamp_enable_1 < 100000:
                if delta_timestamp_enable_2 > 0 and delta_timestamp_enable_2 < 100000:
                    if delta_timestamp_enable_3 > 0 and delta_timestamp_enable_3 < 100000:
                        delta_timestamp_enable_avg = \
                            (delta_timestamp_enable_1 + delta_timestamp_enable_2 + delta_timestamp_enable_3) / 3
                    else:
                        delta_timestamp_enable_avg = \
                            (delta_timestamp_enable_1 + delta_timestamp_enable_2) / 2
                else:
                    delta_timestamp_enable_avg = delta_timestamp_enable_t1
            else:
                delta_timestamp_enable_avg = 0

            if delta_timestamp_enable_avg < 0.00001 and delta_timestamp_enable_avg > 100000:
                main.log.info("Delta of timestamp enable switch returned unexpected results")
                main.log.info("Value returned: " + str(delta_timestamp_enable_avg))
                main.log.info("Omitting iteration " + str(i))
                assertion = main.FALSE
            else:
                link_up_lat.append(delta_timestamp_enable_avg)
                main.log.info("Link up discovery latency iteration "+str(i)+": "+str(delta_timestamp_enable_avg)+" ms")                
   
        if len(link_down_lat) > 2 and len(link_up_lat) > 2:
            link_down_lat = link_down_lat[2:]
            link_down_lat_min = str(min(link_down_lat))
            link_down_lat_max = str(max(link_down_lat))
            link_down_lat_avg = str(sum(link_down_lat) / len(link_down_lat))

            link_down_lat = link_down_lat[2:] 
            link_up_lat_min = str(min(link_up_lat))
            link_up_lat_max = str(max(link_up_lat))
            link_up_lat_avg = str(sum(link_up_lat) / len(link_up_lat))
        else:
            main.log.report("Link event latency could not be calculatd due to errors in results")

        #NOTE: configure threshold as needed
        if int(link_down_lat_avg) > 0:
            if postToDB == 'on': 
                os.system(db_script + " --name='Link remove' --minimum='"+link_down_lat_min+
                      "' --maximum='"+link_down_lat_max+"' --average='"+link_down_lat_avg+"' "+
                      "--table='"+table_name+"'")
            else:
                main.log.report("Results were not posted to the database")
        
        if int(link_up_lat_avg) > 0:
            if postToDB == 'on': 
                os.system(db_script + " --name='Link add' --minimum='"+link_up_lat_min+
                      "' --maximum='"+link_up_lat_max+"' --average='"+link_up_lat_avg+"' "+
                      "--table='"+table_name+"'")
            else:
                main.log.report("Results were not posted to the database")
            
        if int(link_up_lat_avg) > 0 and int(link_down_lat_avg) > 0:
            assertion = main.TRUE

        omit_num_down = int(numIter) - int(len(link_down_lat))
        omit_num_up = int(numIter) - int(len(link_up_lat))
        main.log.report("Iterations omitted/total of link down event: "+
                str(omit_num_down) +"/"+ str(numIter))
        main.log.report("Iterations omitted/total of link up event: "+
                str(omit_num_up) + "/"+ str(numIter))
        main.log.report("Link down discovery latency: Min: "+
                link_down_lat_min+" ms    Max: "+link_down_lat_max+
                " ms    Avg: "+link_down_lat_avg+" ms")
        main.log.report("Link up discovery latency: Min: "+
                link_up_lat_min+" ms    Max: "+link_up_lat_max+
                " ms    Avg: "+link_up_lat_avg+" ms")

        utilities.assert_equals(expect=main.TRUE,actual=assertion,
                onpass="Link Latency test successful",
                onfail="Link Latency test NOT successful")


#******************************************
#CASE5
#Assign 25 switches to  controller 1
#measure latency 
#******************************************
    def CASE5(self, main):
        import time
        import subprocess
        import json
        import requests
        import os

        ctrl_1 = main.params['CTRL']['ip1']
        ctrl_2 = main.params['CTRL']['ip2']
        ctrl_3 = main.params['CTRL']['ip3']
        
        port_1 = main.params['CTRL']['port1']
        tshark_output = "/tmp/tshark_of_topo_25.txt"
        numIter = main.params['TOPO']['numIter']
        db_script = main.params['TOPO']['databaseScript']
        table_name = main.params['TOPO']['tableName']
        postToDB = main.params['TOPO']['postToDB']
        assertion = main.TRUE
        
        add_sw25_threshold = main.params['LOG']['threshold']['switch_add25']
        logNameONOS1 = main.params['LOG']['logNameONOS1']
        logNameONOS2 = main.params['LOG']['logNameONOS2']
        logNameONOS3 = main.params['LOG']['logNameONOS3']
        logDir = main.params['LOG']['logDir']
        
        rest_port = main.params['INTENTREST']['intentPort']
        url_suffix = main.params['TOPO']['url_topo']
        url_topo_1 = "http://"+ctrl_1+":"+rest_port+url_suffix 
        url_topo_2 = "http://"+ctrl_2+":"+rest_port+url_suffix 
        url_topo_3 = "http://"+ctrl_3+":"+rest_port+url_suffix 
        
        add_lat = []
   
        main.log.report("Measure latency of adding 25 switches")

        #We need to delete the switches assigned in the previous test case 
        #To get an accurate time measurement
        main.step("Deleting previously added switches")
        main.Mininet1.handle.sendline("sh ovs-vsctl del-controller s1")
        main.Mininet1.handle.sendline("sh ovs-vsctl del-controller s2")
        main.Mininet1.handle.sendline("sh ovs-vsctl del-controller s3")

        time.sleep(5) 

        for x in range(0,int(numIter)):
            main.step("Starting tshark open flow capture") 

            #***********************************************************************************
            #TODO: Capture packets in pcap format and read in / parse more specific data for
            #improved accuracy. Grep may not work in the future when we dissect at a lower level
            #***********************************************************************************

            #NOTE: Get Config Reply is the last message of the OF handshake message.
            #Hence why we use it as T0 
            main.ONOS1.tshark_grep("OFP 78 Get Config Reply", tshark_output) 
            time.sleep(10) 
        
            main.step("Assign controllers and get timestamp")
            
            for i in range(1, 16):
                main.Mininet2.handle.sendline("sudo ovs-vsctl set-controller s"+\
                        str(i)+" tcp:"+ctrl_1+" ptcp:6633 --no-wait --no-syslog &")
                #main.Mininet1.assign_sw_controller(sw=str(i),ip1=ctrl_1,port1=port_1)
            for i in range(31, 41):       
                main.Mininet2.handle.sendline("sudo ovs-vsctl set-controller s"+\
                        str(i)+" tcp:"+ctrl_1+" ptcp:6633 --no-wait --no-syslog &")
                #main.Mininet1.assign_sw_controller(sw=str(i),ip1=ctrl_1,port1=port_1)

            time.sleep(10)
            main.ONOS1.stop_tshark()

            ssh = subprocess.Popen(['ssh', 'admin@'+ctrl_1, 'cat', tshark_output],
                    stdout=subprocess.PIPE)
            time.sleep(5)
            text = ssh.stdout.readline()
            obj = text.split(" ")
            
            if len(text) > 0:
                timestamp = int(float(obj[1])*1000)
                topo_ms_begin = timestamp
            else:
                main.log.error("Tshark output file returned unexpected value")
                topo_ms_begin = 0
                assertion = main.FALSE    
            
            json_obj_1 = main.ONOS1.get_json(url_topo_1) 
            json_obj_2 = main.ONOS2.get_json(url_topo_2)
            json_obj_3 = main.ONOS3.get_json(url_topo_3)

            #If json object exists, parse timestamp from the object
            if json_obj_1: 
                topo_ms_end_1 = json_obj_1['gauges'][0]['gauge']['value']
            else:
                topo_ms_end_1 = 0
            if json_obj_2:
                topo_ms_end_2 = json_obj_2['gauges'][0]['gauge']['value']
            else:
                topo_ms_end_2 = 0
            if json_obj_3:
                topo_ms_end_3 = json_obj_3['gauges'][0]['gauge']['value']
            else:
                topo_ms_end_3 = 0

            delta_1 = int(topo_ms_end_1) - int(topo_ms_begin)
            delta_2 = int(topo_ms_end_2) - int(topo_ms_begin)
            delta_3 = int(topo_ms_end_3) - int(topo_ms_begin)
            
            #If one of the delta exceeds the threshold, investigate onos-log
            if delta_1 > int(add_sw25_threshold) or \
               delta_2 > int(add_sw25_threshold) or \
               delta_3 > int(add_sw25_threshold):
                log_result = main.ONOS1.tailLog(log_directory = logDir,
                        log_name = logNameONOS1, tail_length = 50)
                
                main.log.info("Latency calculation exceeded threshold of "+add_sw25_threshold)
                main.log.info("Fetching onos-log for investigation: ")
                main.log.info(log_result)

            if delta_1 > 0 and delta_1 < 100000:
                if delta_2 > 0 and delta_2 < 100000:
                    if delta_3 > 0 and delta_3 < 100000:
                        delta_avg = (delta_1 + delta_2 + delta_3) / 3
                    else:
                        delta_avg = (delta_1 + delta_2) / 2
                else:
                    delta_avg = delta_1
            else:
                delta_avg = 0

            time.sleep(5)

            #NOTE: edit threshold as needed to fail test case
            if delta_avg < 0.00001 or delta_avg > 100000:
                main.log.info("Delta of switch add timestamp returned unexpected results")
                main.log.info("Value returned: " + str(delta_avg))
                main.log.info("Omitting iteration "+ str(x))
                assertion = main.FALSE 
            else:
                add_lat.append(delta_avg) 
                main.log.info("Add 25 switches latency iteration "+str(x)+": "+str(delta_avg)) 

            main.step("Remove switches from the controller")
            for j in range(1,16):
                main.Mininet1.delete_sw_controller("s"+str(j)) 
            for k in range(31, 41):
                main.Mininet1.delete_sw_controller("s"+str(k))
        
            time.sleep(5)

        if len(add_lat) > 2:
            add_lat = add_lat[2:]
            add_lat_min = str(min(add_lat))
            add_lat_max = str(max(add_lat))
            add_lat_avg = str(sum(add_lat) / len(add_lat))
        else:
            main.log.report("Add 25 switch latency could not be calculated due to errors in results")

        if int(add_lat_avg) > 0 and int(add_lat_avg) < 100000:
            if postToDB == 'on':
                os.system(db_script + " --name='25 Switch add' --minimum='"+add_lat_min+
                      "' --maximum='"+add_lat_max+"' --average='"+add_lat_avg+"' " + 
                      "--table='"+table_name+"'")
            else:
                main.log.report("Results were not posted to the database")

        if int(add_lat_avg) > 0 and int(add_lat_avg) < 100000:
            assertion = main.TRUE
            omit_iter = int(numIter) - int(len(add_lat))
            main.log.report("Iterations omitted/total: "+str(omit_iter)+"/"+str(numIter))
            main.log.report("Add 25 switches discovery latency: Min: "+
                    add_lat_min+" ms    Max: "+add_lat_max+
                    " ms    Avg: "+add_lat_avg+" ms")
        else:
            assertion = main.FALSE
            main.log.report("add_lat_avg for 25 switches returned unexpected results")

        utilities.assert_equals(expect=main.TRUE,actual=assertion,
                onpass="25 Switch latency test successful!",
                onfail="25 Switch latency test NOT successful")



    #CASE6: assign 88 switches

    def CASE6(self, main):
        import time
        import subprocess
        import json
        import requests
        import os

        ctrl_1 = main.params['CTRL']['ip1']
        ctrl_2 = main.params['CTRL']['ip2']
        ctrl_3 = main.params['CTRL']['ip3']
        
        port_1 = main.params['CTRL']['port1']
        tshark_output = "/tmp/tshark_of_topo_88.txt"
        numIter = main.params['TOPO']['numIter']
        db_script = main.params['TOPO']['databaseScript']
        table_name = main.params['TOPO']['tableName']
        postToDB = main.params['TOPO']['postToDB']
        assertion = main.TRUE
       
        add_sw88_threshold = main.params['LOG']['threshold']['switch_add88']
        logNameONOS1 = main.params['LOG']['logNameONOS1']
        logNameONOS2 = main.params['LOG']['logNameONOS2']
        logNameONOS3 = main.params['LOG']['logNameONOS3']
        logDir = main.params['LOG']['logDir']
        
        rest_port = main.params['INTENTREST']['intentPort']
        url_suffix = main.params['TOPO']['url_topo']
        url_topo_1 = "http://"+ctrl_1+":"+rest_port+url_suffix 
        url_topo_2 = "http://"+ctrl_2+":"+rest_port+url_suffix 
        url_topo_3 = "http://"+ctrl_3+":"+rest_port+url_suffix 
        
        add_lat = []
   
        main.log.report("Measure latency of adding 88 switches")

        time.sleep(5) 

        for x in range(0,int(numIter)):
            main.step("Starting tshark open flow capture") 

            #***********************************************************************************
            #TODO: Capture packets in pcap format and read in / parse more specific data for
            #improved accuracy. Grep may not work in the future when we dissect at a lower level
            #***********************************************************************************

            #NOTE: Get Config Reply is the last message of the OF handshake message.
            #Hence why we use it as T0 
            main.ONOS1.tshark_grep("OFP 78 Get Config Reply", tshark_output) 
            time.sleep(10) 

            main.step("Assign controllers and get timestamp")
            for i in range(1, 89): 
                main.Mininet2.handle.sendline("sudo ovs-vsctl set-controller s"+str(i)+" tcp:"+ctrl_1+" ptcp:6633")
            #    main.Mininet1.assign_sw_controller(sw=str(i),ip1=ctrl_1,port1=port_1) #30% slower 
            #    cmd = "sudo ovs-vsctl set-controller s"+str(i)+" tcp:"+ctrl_1+" ptcp:6633"
            #    s = subprocess.Popen(['ssh', 'admin@10.128.5.59', cmd], shell=True)

            time.sleep(10)
            main.ONOS1.stop_tshark()

            ssh = subprocess.Popen(['ssh', 'admin@'+ctrl_1, 'cat', tshark_output],
                    stdout=subprocess.PIPE)
            time.sleep(5)
            text = ssh.stdout.readline()
            obj = text.split(" ")
            
            if len(text) > 0:
                timestamp = int(float(obj[1])*1000)
                topo_ms_begin = timestamp
            else:
                main.log.error("Tshark output file returned unexpected value")
                topo_ms_begin = 0
                assertion = main.FALSE    
            
            json_obj_1 = main.ONOS1.get_json(url_topo_1) 
            json_obj_2 = main.ONOS2.get_json(url_topo_2)
            json_obj_3 = main.ONOS3.get_json(url_topo_3)

            #If json object exists, parse timestamp from the object
            if json_obj_1: 
                topo_ms_end_1 = json_obj_1['gauges'][0]['gauge']['value']
            else:
                topo_ms_end_1 = 0
            if json_obj_2:
                topo_ms_end_2 = json_obj_2['gauges'][0]['gauge']['value']
            else:
                topo_ms_end_2 = 0
            if json_obj_3:
                topo_ms_end_3 = json_obj_3['gauges'][0]['gauge']['value']
            else:
                topo_ms_end_3 = 0

            delta_1 = int(topo_ms_end_1) - int(topo_ms_begin)
            delta_2 = int(topo_ms_end_2) - int(topo_ms_begin)
            delta_3 = int(topo_ms_end_3) - int(topo_ms_begin)
            
            #If one of the delta exceeds the threshold, investigate onos-log
            if delta_1 > int(add_sw88_threshold) or \
               delta_2 > int(add_sw88_threshold) or \
               delta_3 > int(add_sw88_threshold):
                log_result = main.ONOS1.tailLog(log_directory = logDir,
                        log_name = logNameONOS1, tail_length = 50)
                
                main.log.info("Latency calculation exceeded threshold of "+add_sw88_threshold)
                main.log.info("Fetching onos-log for investigation: ")
                main.log.info(log_result)

            if delta_1 > 0 and delta_1 < 100000:
                if delta_2 > 0 and delta_2 < 100000:
                    if delta_3 > 0 and delta_3 < 100000:
                        delta_avg = (delta_1 + delta_2 + delta_3) / 3
                    else:
                        delta_avg = (delta_1 + delta_2) / 2
                else:
                    delta_avg = delta_1
            else:
                delta_avg = 0

            time.sleep(5)

            #NOTE: edit threshold as needed to fail test case
            if delta_avg < 0.00001 or delta_avg > 100000:
                main.log.info("Delta of switch add timestamp returned unexpected results")
                main.log.info("Value returned: " + str(delta_avg))
                main.log.info("Omitting iteration "+ str(x))
                assertion = main.FALSE 
            else:
                add_lat.append(delta_avg) 
                main.log.info("Add 88 switches latency iteration "+str(x)+": "+str(delta_avg)) 

            main.step("Remove switches from the controller")
            for j in range(1,89):
                main.Mininet1.delete_sw_controller("s"+str(j)) 
        
            time.sleep(5)

        if len(add_lat) > 2:
            add_lat = add_lat[2:]
            add_lat_min = str(min(add_lat))
            add_lat_max = str(max(add_lat))
            add_lat_avg = str(sum(add_lat) / len(add_lat))
        else:
            main.log.report("Add 88 switches latency could not be calculated due to errors in results")

        if int(add_lat_avg) > 0 and int(add_lat_avg) < 100000:
            assertion = main.TRUE
            omit_iter = int(numIter) - int(len(add_lat))
            main.log.report("Iterations omitted/total: "+str(omit_iter)+"/"+str(numIter))
            main.log.report("Add 88 switches discovery latency: Min: "+
                    add_lat_min+" ms    Max: "+add_lat_max+
                    " ms    Avg: "+add_lat_avg+" ms")
        else:
            assertion = main.FALSE
            main.log.report("add_lat_avg for 88 switches returned unexpected results")

        utilities.assert_equals(expect=main.TRUE,actual=assertion,
                onpass="88 Switch latency test successful!",
                onfail="88 Switch latency test NOT successful")


    def CASE7(self, main):
        '''
        CASE7 25 Switch assignment via threading
        '''
        import time
        import subprocess
        import json
        import requests
        import os

        import threading

        ctrl_1 = main.params['CTRL']['ip1']
        ctrl_2 = main.params['CTRL']['ip2']
        ctrl_3 = main.params['CTRL']['ip3']
        
        port_1 = main.params['CTRL']['port1']
        tshark_output = "/tmp/tshark_of_topo_25_thread.txt"
        numIter = main.params['TOPO']['numIter']
        db_script = main.params['TOPO']['databaseScript']
        table_name = main.params['TOPO']['tableName']
        assertion = main.TRUE
        
        add_sw_threshold = main.params['LOG']['threshold']['switch_add1']
        logNameONOS1 = main.params['LOG']['logNameONOS1']
        logNameONOS2 = main.params['LOG']['logNameONOS2']
        logNameONOS3 = main.params['LOG']['logNameONOS3']
        logDir = main.params['LOG']['logDir']
        
        rest_port = main.params['INTENTREST']['intentPort']
        url_suffix = main.params['TOPO']['url_topo']
        url_topo_1 = "http://"+ctrl_1+":"+rest_port+url_suffix 
        url_topo_2 = "http://"+ctrl_2+":"+rest_port+url_suffix 
        url_topo_3 = "http://"+ctrl_3+":"+rest_port+url_suffix 
        
        add_lat = []
        threads = []
   
        main.log.report("Measure latency of adding 25 switches using threading")

        time.sleep(5) 

        #This segment uses threads to set controllers concurrently
        def set_controller(i, ctrl_1, cond):
            main.log.info("Starting set_controller thread "+str(i))
            main.Mininet2.handle.sendline("sudo ovs-vsctl set-controller s"+\
                str(i)+" tcp:"+ctrl_1+" ptcp:"+str(6633+int(i))+" --no-wait --no-syslog & \n")
            with cond:
                #Wait for all threads to start before executing set controller on all threads
                cond.wait()
        
        for x in range(0,int(numIter)):
            main.step("Starting tshark open flow capture") 

            #***********************************************************************************
            #TODO: Capture packets in pcap format and read in / parse more specific data for
            #improved accuracy. Grep may not work in the future when we dissect at a lower level
            #***********************************************************************************

            #NOTE: Get Config Reply is the last message of the OF handshake message.
            #Hence why we use it as T0 
            main.ONOS1.tshark_grep("OFP 78 Get Config Reply", tshark_output, interface='eth0') 
            time.sleep(10) 
       
            main.step("Assign controllers and get timestamp")
            
            thread_list = []
            #Threading condition
            condition = threading.Condition()
            
            for i in range(1, 26): 
                #prepare controller threads
                t = threading.Thread(target=set_controller, args=(i, ctrl_1, condition))
                thread_list.append(t)
                thread_list[i-1].start()
            
            time.sleep(25)

            #Join all threads
            #main_thread = threading.currentThread()
            #for t in threading.enumerate():
                #if t is main_thread:
                    #    continue
                #else:
                    #        t.join()

            main.ONOS1.stop_tshark()

            time.sleep(5)
            ssh = subprocess.Popen(['ssh', 'admin@'+ctrl_1, 'cat', tshark_output],
                    stdout=subprocess.PIPE)
            text = ssh.stdout.readline()
            obj = text.split(" ")
            
            time.sleep(5)
            
            if len(text) > 0:
                timestamp = int(float(obj[1])*1000)
                topo_ms_begin = timestamp
            else:
                main.log.error("Tshark output file returned unexpected value")
                topo_ms_begin = 0
                assertion = main.FALSE    
            
            json_obj_1 = main.ONOS1.get_json(url_topo_1) 
            json_obj_2 = main.ONOS2.get_json(url_topo_2)
            json_obj_3 = main.ONOS3.get_json(url_topo_3)

            #If json object exists, parse timestamp from the object
            if json_obj_1: 
                topo_ms_end_1 = json_obj_1['gauges'][0]['gauge']['value']
            else:
                topo_ms_end_1 = 0
            if json_obj_2:
                topo_ms_end_2 = json_obj_2['gauges'][0]['gauge']['value']
            else:
                topo_ms_end_2 = 0
            if json_obj_3:
                topo_ms_end_3 = json_obj_3['gauges'][0]['gauge']['value']
            else:
                topo_ms_end_3 = 0

            delta_1 = int(topo_ms_end_1) - int(topo_ms_begin)
            delta_2 = int(topo_ms_end_2) - int(topo_ms_begin)
            delta_3 = int(topo_ms_end_3) - int(topo_ms_begin)

            if delta_1 > 0 and delta_1 < 100000:
                if delta_2 > 0 and delta_2 < 100000:
                    if delta_3 > 0 and delta_3 < 100000:
                        delta_avg = (delta_1 + delta_2 + delta_3) / 3
                    else:
                        delta_avg = (delta_1 + delta_2) / 2
                else:
                    delta_avg = delta_1
            else:
                delta_avg = 0

            time.sleep(5)

            #NOTE: edit threshold as needed to fail test case
            if delta_avg < 0.00001 or delta_avg > 100000:
                main.log.info("Delta of switch add timestamp returned unexpected results")
                main.log.info("Value returned: " + str(delta_avg))
                main.log.info("Omitting iteration "+ str(x))
                assertion = main.FALSE 
            else:
                add_lat.append(delta_avg) 
                main.log.info("Add 25 switches latency iteration "+str(x)+": "+str(delta_avg)) 

            main.step("Remove switches from the controller")
            for j in range(1,26):
                main.Mininet1.delete_sw_controller("s"+str(j)) 
        
            time.sleep(5)

        if len(add_lat) > 2:
            add_lat = add_lat[2:]
            add_lat_min = str(min(add_lat))
            add_lat_max = str(max(add_lat))
            add_lat_avg = str(sum(add_lat) / len(add_lat))
        else:
            main.log.report("Add 25 switch latency calculation failed due to errors in results")

        if int(add_lat_avg) > 0 and int(add_lat_avg) < 100000:
            assertion = main.TRUE
            omit_iter = int(numIter) - int(len(add_lat))
            main.log.report("Iterations omitted/total: "+str(omit_iter)+"/"+str(numIter))
            main.log.report("Add 25 switches discovery latency: Min: "+
                    add_lat_min+" ms    Max: "+add_lat_max+
                    " ms    Avg: "+add_lat_avg+" ms")
        else:
            assertion = main.FALSE
            main.log.report("add_lat_avg for 25 switches returned unexpected results")

        utilities.assert_equals(expect=main.TRUE,actual=assertion,
                onpass="25 Switch latency test successful!",
                onfail="25 Switch latency test NOT successful")

#**********
#END SCRIPT
#andrew@onlab.us
#**********
