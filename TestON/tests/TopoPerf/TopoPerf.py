
class TopoPerf:
    def __init__(self) :
        self.default = ''
#Test startup
    def CASE1(self,main) :  #Check to be sure ZK, Cass, and ONOS are up, then get ONOS version
        main.case("Initial setup")
        main.step("Stop ONOS")
        import time
        main.ONOS1.stop()
        main.ONOS2.stop()
        main.ONOS3.stop()
        main.ONOS2.rest_stop()
        main.step("Start ONOS")
        time.sleep(5)
        main.Zookeeper1.start()
        main.Zookeeper2.start()
        main.Zookeeper3.start()
        time.sleep(5)
        main.RamCloud1.del_db()
        main.RamCloud2.del_db()
        main.RamCloud3.del_db()
        main.ONOS1.start()
        main.ONOS2.start()
        main.ONOS3.start()
        main.ONOS2.start_rest()
        time.sleep(3)
       
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

        url_topo = main.params['INTENTS']['url_topo']
        ctrl_1 = main.params['CTRL']['ip1']
        port_1 = main.params['CTRL']['port1']
        tshark_output = "/tmp/tshark_of_topo.txt"
        assertion = main.TRUE

        main.case("Measure latency of adding one switch")
        main.step("Starting tshark open flow capture") 
        #TODO: research tshark capture options to filter OFP packets.
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
        if obj[0]:
            timestamp = int(float(obj[0])*1000)
        else:
            timestamp = 0
            main.log.error("Tshark output file returned unexpected value")

        topo_ms_begin = timestamp

        main.step("Verify that switch s1 has been assigned properly") 
        response = main.Mininet1.get_sw_controller(sw="s1")
        if response == main.FALSE:
            main.log.error("Switch s1 was NOT assigned properly")
            assertion = main.FALSE
        elif topo_ms_begin > 0: 
            json_obj = main.ONOS1.get_json(url_topo) 
            main.log.info("Switch s1 was assigned properly!")
        topo_ms_end = json_obj['gauges'][0]['gauge']['value']
        delta = int(topo_ms_end) - int(topo_ms_begin)
        main.log.report("Add begin timestamp (epoch ms): " + str(topo_ms_begin))
        main.log.report("Add end timestamp (epoch ms): " + str(topo_ms_end))
        main.log.report("1 switch add latency: " + str(delta) + " ms") 
        time.sleep(5)

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
        assertion = "" 
        ctrl_1 = main.params['CTRL']['ip1']
        port_1 = main.params['CTRL']['port1']
        url_topo = main.params['INTENTS']['url_topo'] 

        main.case("Port enable / disable latency") 

        main.step("Assign switch to controller")
        main.Mininet1.assign_sw_controller(sw="1",ip1=ctrl_1,port1=port_1) 
   
        main.step("Verify switch is assigned correctly")
        result = main.Mininet1.get_sw_controller(sw="s1")
        if result == main.FALSE:
            main.log.info("Switch s1 was NOT assigned correctly")
            assertion = main.FALSE
        else:
            main.log.report("Switch s1 was assigned correctly!")

        main.step("Starting wireshark capture for port status down")
        main.ONOS1.tshark_grep("OFP 130 Port Status", tshark_output_down)
        time.sleep(10)

        main.step("Disable port and obtain timestamp via REST")
        main.Mininet2.handle.sendline("sudo ifconfig s1-eth2 down")
        main.Mininet2.handle.expect("\$")
        time.sleep(10)
        
        main.ONOS1.stop_tshark() 
        time.sleep(5)       
 
        ssh = subprocess.Popen(['ssh', 'admin@'+ctrl_1, 'cat', tshark_output_down],stdout=subprocess.PIPE)
        text = ssh.stdout.readline()
        obj = text.split(" ")
        if obj[0]:
            timestamp = int(float(obj[0])*1000)

        json_obj = main.ONOS1.get_json(url_topo)
        topo_ms_end = json_obj['gauges'][0]['gauge']['value']

        delta = int(topo_ms_end) - int(timestamp)
        main.log.report("Port down latency: " + str(delta) + " ms")
        
        main.step("Enable port and obtain timestamp via REST") 
        main.step("Starting wireshark capture for port status up")
        main.ONOS1.tshark_grep("OFP 130 Port Status", tshark_output_up)
        time.sleep(10)
        
        main.Mininet2.handle.sendline("")
        main.Mininet2.handle.expect("\$")
        main.Mininet2.handle.sendline("sudo ifconfig s1-eth2 up")
        main.Mininet2.handle.expect("\$")
        time.sleep(10)
 
        main.ONOS1.stop_tshark()
        time.sleep(5)
 
        ssh = subprocess.Popen(['ssh', 'admin@'+ctrl_1, 'cat', tshark_output_up], stdout=subprocess.PIPE)
        text = ssh.stdout.readline()
        text2 = ssh.stdout.readline()
        obj2 = text2.split(" ")
        if obj2[0]:
            timestamp = int(float(obj2[0])*1000)

        json_obj = main.ONOS1.get_json(url_topo)
        topo_ms_end = json_obj['gauges'][0]['gauge']['value']
          
        delta = int(topo_ms_end) - int(timestamp)
        main.log.report("Port up latency: " + str(delta) + " ms")



#***************************************
#CASE4
#Time to add or remove a link between two switches 
#***************************************
    def CASE4(self,main):
        import requests
        import json
        import time 
        import subprocess
        import os

        assertion = ""
        ctrl_1 = main.params['CTRL']['ip1']
        port_1 = main.params['CTRL']['port1']
        url_topo = main.params['INTENTS']['url_topo']

        main.case("Add / remove link latency between two switches")
        main.step("Assign two switches")
        main.Mininet1.assign_sw_controller(sw="1",ip1=ctrl_1,port1=port_1)
        main.Mininet1.assign_sw_controller(sw="2",ip1=ctrl_1,port1=port_1)

        main.step("Verify assignment of switches")
        result_s1 = main.Mininet1.get_sw_controller(sw="s1")
        result_s2 = main.Mininet1.get_sw_controller(sw="s2")
        if result_s1 == main.TRUE and result_s2 == main.TRUE:
            main.log.report("Switches s1 and s2 assigned successfully")
        else:
            main.log.error("Error assigning switches s1 and s2 to controller "+str(ctrl_1))
            assertion = main.FALSE

        main.step("Start tshark capture for link disabled")

        main.step("Disable link via loss-rate: 100%")
        main.step("Obtain link disabled timestamp via REST for each ONOS")

#**********
#END SCRIPT
#andrew@onlab.us
#**********
