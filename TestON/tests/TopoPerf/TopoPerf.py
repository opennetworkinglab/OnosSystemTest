
class TopoPerf:
    def __init__(self) :
        self.default = ''
#**********************
#CASE1
#Test startup
#**********************
    def CASE1(self,main) :  #Check to be sure ZK, Cass, and ONOS are up, then get ONOS version
        import time
        main.case("Initial setup")
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
        main.step("Delete RC db")
        time.sleep(5)
        main.RamCloud1.del_db()
        main.RamCloud2.del_db()
        main.RamCloud3.del_db()
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
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Zookeeper is up!",onfail="Zookeeper is down...")
        main.step("Testing startup RamCloud")   
        data = main.RamCloud1.status_serv() and main.RamCloud2.status_serv() and main.RamCloud3.status_serv() 
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
            data = main.RamCloud1.status_serv() and main.RamCloud2.status_serv() and main.RamCloud3.status_serv()
            
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="RamCloud is up!",onfail="RamCloud is down...")

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
 
        url_topo = main.params['TOPO']['url_topo']
        ctrl_1 = main.params['CTRL']['ip1']
        port_1 = main.params['CTRL']['port1']
        numIter = main.params['TOPO']['numIter']
        db_script = main.params['TOPO']['databaseScript']
        table_name = main.params['TOPO']['tableName']
        tshark_output = "/tmp/tshark_of_topo.txt"
        assertion = main.TRUE
        topo_lat = []

        main.case("Measure latency of adding one switch")

        for i in range(0, int(numIter)):
            main.step("Starting tshark open flow capture") 

            #***********************************************************************************
            #TODO: Capture packets in pcap format and read in / parse more specific data for
            #improved accuracy. Grep may not work in the future when we dissect at a lower level
            #***********************************************************************************

            #NOTE: Get Config Reply is the last message of the OF handshake message.
            #Hence why we use it as T0 
            main.ONOS1.tshark_grep("OFP 78 Get Config Reply", tshark_output) 
            time.sleep(10) 

            #NOTE: We need to assign the switch in a specific way for perf measurements
            main.step("Assign controller s1 and get timestamp")
            main.Mininet1.assign_sw_controller(sw="1",ip1=ctrl_1,port1=port_1)        
            time.sleep(10)
            main.ONOS1.stop_tshark()

            ssh = subprocess.Popen(['ssh', 'admin@'+ctrl_1, 'cat', tshark_output],stdout=subprocess.PIPE)
            text = ssh.stdout.readline()
            obj = text.split(" ")
            print text
            if len(text) > 0:
                timestamp = int(float(obj[0])*1000)
                topo_ms_begin = timestamp
            else:
                main.log.error("Tshark output file returned unexpected value")
                topo_ms_begin = 0
                assertion = main.FALSE    
 
            main.step("Verify that switch s1 has been assigned properly") 
            response = main.Mininet1.get_sw_controller(sw="s1")
            if response == main.FALSE:
                main.log.error("Switch s1 was NOT assigned properly")
                assertion = main.FALSE
            else:
                main.log.info("Switch s1 was assigned properly!")
            
            json_obj = main.ONOS1.get_json(url_topo) 
        
            if json_obj: 
                topo_ms_end = json_obj['gauges'][0]['gauge']['value']
            else:
                topo_ms_end = 0
                assertion = main.FALSE

            delta = int(topo_ms_end) - int(topo_ms_begin)

            time.sleep(5)

            main.step("Remove switch from controller s1")
            main.Mininet1.delete_sw_controller("s1")
            time.sleep(5)

            #NOTE: edit threshold as needed to fail test case
            if delta < 0 or delta > 100000:
                main.log.report("Delta of switch add timestamp returned unexpected results")
                main.log.report("Value returned: " + str(delta))
            else:
                topo_lat.append(delta)
                main.log.info("One switch add latency iteration "+str(i)+": " + str(delta) + " ms")  
 
        topo_lat_min = str(min(topo_lat))
        topo_lat_max = str(max(topo_lat))
        topo_lat_avg = str(sum(topo_lat) / len(topo_lat))
       
        #NOTE: configure threshold as needed here: 
        if int(topo_lat_max) > 0 and int(topo_lat_max) < 100000:
            assertion = main.TRUE
            os.system(db_script + " --name='1 switch add' --minimum='"+topo_lat_min+
                      "' --maximum='"+topo_lat_max+"' --average='"+topo_lat_avg+"' " + 
                      "--table='"+table_name+"'")
  
        main.log.report("One switch add latency: Min: "+topo_lat_min+" ms    Max: "+topo_lat_max+" ms    Avg: "+topo_lat_avg+" ms")
 
        utilities.assert_equals(expect=main.TRUE,actual=assertion,onpass="Switch latency test successful!",onfail="Switch latency test NOT successful")
#***************************************** 
#CASE3
#latency to enable or disable a port on switch 
# 
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
        port_1 = main.params['CTRL']['port1']
        url_topo = main.params['TOPO']['url_topo'] 
        numIter = main.params['TOPO']['numIter']
        db_script = main.params['TOPO']['databaseScript']
        table_name = main.params['TOPO']['tableName']

        port_up_lat = []
        port_down_lat = []

        main.case("Port enable / disable latency") 

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

            main.step("Disable port (interface s1-eth2)")
            main.Mininet2.handle.sendline("sudo ifconfig s1-eth2 down")
            main.Mininet2.handle.expect("\$")
            time.sleep(10)
        
            main.ONOS1.stop_tshark() 
            time.sleep(5)       
 
            ssh_down = subprocess.Popen(['ssh', 'admin@'+ctrl_1, 'cat', tshark_output_down],stdout=subprocess.PIPE)
            text_down = ssh_down.stdout.readline()
            obj_down = text_down.split(" ")
            if len(text_down) > 0:
                timestamp_begin_pt_down = int(float(obj_down[0])*1000)
            else:
                timestamp_begin_pt_down = 0   

            main.step("Obtain t1 timestamp by REST call")
            json_obj = main.ONOS1.get_json(url_topo)
            timestamp_end_pt_down = json_obj['gauges'][0]['gauge']['value']

            delta_pt_down = int(timestamp_end_pt_down) - int(timestamp_begin_pt_down)
   
            #NOTE: modify threshold as necessary
            if (delta_pt_down < 0) or (delta_pt_down > 100000):
                main.log.report("Delta port down timestamp returned unexpected results")
                main.log.report("Value returned: " + str(delta_pt_down))
                assertion = main.FALSE
            else:
                port_down_lat.append(delta_pt_down)     
                main.log.info("Port down latency iteration "+str(i)+": "+str(delta_pt_down)+" ms")
 
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
 
            ssh_up = subprocess.Popen(['ssh', 'admin@'+ctrl_1, 'cat', tshark_output_up], stdout=subprocess.PIPE)
            text1 = ssh_up.stdout.readline()
            #read second line 
            text_up = ssh_up.stdout.readline()
            obj_up = text_up.split(" ")
            obj_up1 = text1.split(" ")
            if len(text_up) > 0:
                timestamp_begin_pt_up = int(float(obj_up[0])*1000)
            elif len(text1) > 0: 
                timestamp_begin_pt_up = int(float(obj_up1[0])*1000)
            else:
                timestamp_begin_pt_up = 0

            json_obj_up = main.ONOS1.get_json(url_topo)
            timestamp_end_pt_up = json_obj_up['gauges'][0]['gauge']['value']
        
            delta_pt_up = int(timestamp_end_pt_up) - int(timestamp_begin_pt_up)

            #NOTE: modify threshold as necessary
            if (delta_pt_up < 0) or (delta_pt_up > 100000):
                main.log.report("Delta of timestamp returned unexpected results")
                main.log.report("Value returned: " + str(delta_pt_up))
                assertion = main.FALSE
            else:
                port_up_lat.append(delta_pt_up)           
                main.log.info("Port up latency iteration "+str(i)+": "+str(delta_pt_up)+" ms")
  
            time.sleep(5)

        port_up_lat_min = str(min(port_up_lat))
        port_up_lat_max = str(max(port_up_lat))
        port_up_lat_avg = str(sum(port_up_lat) / len(port_up_lat))
 
        port_down_lat_min = str(min(port_down_lat))
        port_down_lat_max = str(max(port_down_lat))
        port_down_lat_avg = str(sum(port_down_lat) / len(port_down_lat))

        #NOTE: configure threshold as needed
        if int(port_up_lat_avg) > 0 and int(port_down_lat_avg) > 0:
            assertion = main.TRUE
            os.system(db_script + " --name='Switch Port Down' --minimum='"+port_down_lat_min+
                      "' --maximum='"+port_down_lat_max+"' --average='"+port_down_lat_avg+
                      "' --table='"+table_name+"'")
            os.system(db_script + " --name='Switch Port Up' --minimum='"+port_up_lat_min+
                      "' --maximum='"+port_up_lat_max+"' --average='"+port_up_lat_avg+
                      "' --table='"+table_name+"'")

        main.log.report("Port up latency: Min: "+port_up_lat_min+" ms    Max: "+port_up_lat_max+" ms    Avg: "+port_up_lat_avg+" ms")
        main.log.report("Port down latency: Min: "+port_down_lat_min+" ms    Max: "+port_down_lat_max+" ms Avg: "+port_down_lat_avg+" ms")
 
        utilities.assert_equals(expect=main.TRUE,actual=assertion,onpass="Port latency test successful!",onfail="Port latency test NOT successful")

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
        port_1 = main.params['CTRL']['port1']
        url_topo = main.params['TOPO']['url_topo']
        url_links = main.params['TOPO']['url_links']
        numIter = main.params['TOPO']['numIter']
        db_script = main.params['TOPO']['databaseScript']
        table_name = main.params['TOPO']['tableName']
        switch1_mac = main.params['TOPO']['switch1']
        switch3_mac = main.params['TOPO']['switch3']
 
        link_down_lat = []
        link_up_lat = []

        main.case("Add / remove link latency between two switches")

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
            main.Mininet2.handle.sendline("sudo tc qdisc add dev s1-eth2 root netem loss 100")
            #The above line sends a shell command tc qdisc which is part of the linux kernel's method of
            #traffic control. network emulator (netem) can then be added on to simulate link loss rate
         
            #this step call came after the actual event to reduce latency gap between the 
            #Timestamp and link cut
            main.step("Disabling link on s1") 

            #NOTE: This sleep is critical to ensure that get_json has enough time to detect and fetch 
            #the necessary object. If you find that get_json has trouble returning an object,
            #check the url, since the rest call is subject to change
            time.sleep(5)

            #This segment of code calls REST to check for 2 things:
            #1) changes to timestamp of url_topo which indicates that there has been a topology change
            #2) changes to url_links, specifically the existence of link between s1 -> s3, which is the 
            #   link we cut. Note that method used  is a UNIDIRECTIONAL cut. Which means link between
            #   s3 -> s1 still persists
            counter = 0
            temp_timestamp = "" 
            timestamp_diff = False
            link_cut_detected = False
         
            main.step("Calling REST to detect link change event... please wait")
            while counter < 60:
                json_obj_up = main.ONOS1.get_json(url_topo)
                json_topo = main.ONOS1.get_json(url_links) 
         
                timestamp_diff = True
                timestamp_link_end = json_obj_up['gauges'][0]['gauge']['value']
                if temp_timestamp == timestamp_link_end:
                    timestamp_diff = False
                temp_timestamp = timestamp_link_end  

                link_cut_detected = True
                #get length of json list to loop a correct amount. Otherwise we will get index out of range
                list_len = len(json_topo)
                #NOTE: Loop through all available switches and check for switch link 1->3
                # If the link does not exist, trigger break 
                for j in range(0, list_len):
                    s1 = json_topo[j]['src']['dpid']
                    s3 = json_topo[j]['dst']['dpid']
                    if s1 == switch1_mac and s3 == switch3_mac:
                        link_cut_detected = False
                if timestamp_diff:
                    main.log.info("Timestamp difference in REST call detected")
                    if link_cut_detected:
                        main.log.info("Link cut detected between s1 -> s3")
                        break
                if link_cut_detected:
                    main.log.info("Link cut detected between s1 -> s3 but no timestamp diff")
                    main.log.info("This is most likely due to link cut detected before the second REST call")       
                    break               
                counter = counter+1
                time.sleep(3)            

            delta_timestamp = int(timestamp_link_end) - int(timestamp_link_begin)
    
            if delta_timestamp < 0 or delta_timestamp > 100000:
                main.log.report("Delta of timestamp returned unexpected results")
                main.log.report("Value returned: " + str(delta_timestamp))
                assertion = main.FALSE
            else:
                link_down_lat.append(delta_timestamp)
                main.log.info("Link down discovery latency iteration "+str(i)+": "+str(delta_timestamp)+" ms")

            time.sleep(5)

            #Enable link and get timestamp
            main.step("Initial timestamp (system time via time.time()) for link enabled")
            timestamp_link_enable_t0 = time.time() * 1000
            #Remove previous 100% packet loss on an interface
            main.Mininet1.handle.sendline("sh tc qdisc del dev s1-eth2 root")
            main.Mininet2.handle.sendline("sudo tc qdisc del dev s1-eth2 root")
            main.step("Enabling link on s1")

            time.sleep(5)
 
            counter = 0
            temp_timestamp = ""
            link_enable_detected = False
            timestamp_diff = False

            main.step("Calling REST to detect link change event... please wait")
            while counter < 60:
                json_obj_up = main.ONOS1.get_json(url_topo)
                json_topo = main.ONOS1.get_json(url_links)
                timestamp_diff = True
                timestamp_link_enable_t1 = json_obj_up['gauges'][0]['gauge']['value']
                if temp_timestamp == timestamp_link_enable_t1:
                    timestamp_diff = False
                temp_timestamp = timestamp_diff

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

            delta_timestamp_enable = int(timestamp_link_enable_t1) - int(timestamp_link_enable_t0)
 
            if delta_timestamp_enable < 0 and delta_timestamp_enable > 100000:
                main.log.report("Delta of timestamp enable switch returned unexpected results")
                main.log.report("Value returned: " + str(delta_timestamp_enable))
                assertion = main.FALSE
            else:
                link_up_lat.append(delta_timestamp_enable)
                main.log.info("Link up discovery latency iteration "+str(i)+": "+str(delta_timestamp_enable)+" ms")                
   
        link_down_lat_min = str(min(link_down_lat))
        link_down_lat_max = str(max(link_down_lat))
        link_down_lat_avg = str(sum(link_down_lat) / len(link_down_lat))

        link_up_lat_min = str(min(link_up_lat))
        link_up_lat_max = str(max(link_up_lat))
        link_up_lat_avg = str(sum(link_up_lat) / len(link_up_lat))

        #NOTE: configure threshold as needed
        if int(link_down_lat_avg) > 0:
            os.system(db_script + " --name='Link remove' --minimum='"+link_down_lat_min+
                      "' --maximum='"+link_down_lat_max+"' --average='"+link_down_lat_avg+"' "+
                      "--table='"+table_name+"'")
        if int(link_up_lat_avg) > 0:
            os.system(db_script + " --name='Link add' --minimum='"+link_up_lat_min+
                      "' --maximum='"+link_up_lat_max+"' --average='"+link_up_lat_avg+"' "+
                      "--table='"+table_name+"'")
        if int(link_up_lat_avg) > 0 and int(link_down_lat_avg) > 0:
            assertion = main.TRUE

        main.log.report("Link down discovery latency: Min: "+link_down_lat_min+" ms    Max: "+link_down_lat_max+" ms    Avg: "+link_down_lat_avg+" ms")
        main.log.report("Link up discovery latency: Min: "+link_up_lat_min+" ms    Max: "+link_up_lat_max+" ms    Avg: "+link_up_lat_avg+" ms")

        utilities.assert_equals(expect=main.TRUE,actual=assertion,onpass="Link Latency test successful",onfail="Link Latency test NOT successful")


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

        url_topo = main.params['TOPO']['url_topo']
        ctrl_1 = main.params['CTRL']['ip1']
        port_1 = main.params['CTRL']['port1']
        tshark_output = "/tmp/tshark_of_topo_25.txt"
        numIter = main.params['TOPO']['numIter']
        db_script = main.params['TOPO']['databaseScript']
        table_name = main.params['TOPO']['tableName']
        assertion = main.TRUE
        add_lat = []
   
        main.case("Measure latency of adding 25 switches")

        main.step("Deleting previously added switches")
        main.Mininet1.handle.sendline("sh ovs-vsctl del-controller s1")
        main.Mininet1.handle.sendline("sh ovs-vsctl del-controller s2")
        main.Mininet1.handle.sendline("sh ovs-vsctl del-controller s3")

        time.sleep(5) 

        for i in range(0,int(numIter)):
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
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
            for i in range(31, 41):       
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])

            time.sleep(10)
            main.ONOS1.stop_tshark()

            ssh = subprocess.Popen(['ssh', 'admin@'+ctrl_1, 'cat', tshark_output],stdout=subprocess.PIPE)
            time.sleep(5)
            text = ssh.stdout.readline()
            print text
            obj = text.split(" ")
            if len(text) > 0:
                timestamp = int(float(obj[0])*1000)
                topo_ms_begin = timestamp
            else:
                main.log.error("Tshark output file returned unexpected value")
                topo_ms_begin = 0
                assertion = main.FALSE    
            
            json_obj = main.ONOS1.get_json(url_topo) 
         
            if json_obj: 
                topo_ms_end = json_obj['gauges'][0]['gauge']['value']
            else:
                topo_ms_end = 0

            delta = int(topo_ms_end) - int(topo_ms_begin)

            time.sleep(5)

            #NOTE: edit threshold as needed to fail test case
            if delta < 0 or delta > 100000:
                main.log.report("Delta of switch add timestamp returned unexpected results")
                main.log.report("Value returned: " + str(delta))
                assertion = main.FALSE 
            else:
                add_lat.append(delta) 
                main.log.info("Add 25 switches latency iteration "+str(i)+": "+str(delta)) 

            main.step("Remove switches from the controller")
            for i in range(1,16):
                main.Mininet1.delete_sw_controller("s"+str(i)) 
            for i in range(31, 41):
                main.Mininet1.delete_sw_controller("s"+str(i))
        
            time.sleep(5)

        add_lat_min = str(min(add_lat))
        add_lat_max = str(max(add_lat))
        add_lat_avg = str(sum(add_lat) / len(add_lat))

        if int(add_lat_avg) > 0:
            assertion = main.TRUE
            os.system(db_script + " --name='25 Switch add' --minimum='"+add_lat_min+
                      "' --maximum='"+add_lat_max+"' --average='"+add_lat_avg+"' " + 
                      "--table='"+table_name+"'")
  
        main.log.report("Add 25 switches discovery latency: Min: "+add_lat_min+" ms    Max: "+add_lat_max+" ms    Avg: "+add_lat_avg+" ms")

        utilities.assert_equals(expect=main.TRUE,actual=assertion,onpass="25 Switch latency test successful!",onfail="25 Switch latency test NOT successful")


#**********
#END SCRIPT
#andrew@onlab.us
#email me for any questions regarding this test
#**********
