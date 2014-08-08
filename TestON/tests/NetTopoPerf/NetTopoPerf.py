
class NetTopoPerf:
    def __init__(self) :
        self.default = ''

#        def print_hello_world(self,main):
#            print("hello world")
#*****************************************************************************************************************************************************************************************
#Test startup
#Tests the startup of Zookeeper1, RamCloud1, and ONOS1 to be certain that all started up successfully
    def CASE1(self,main) :  #Check to be sure ZK, Cass, and ONOS are up, then get ONOS version
        main.case("Initial setup")
        main.step("Stop ONOS")
        import time
        main.ONOS1.stop()
        main.ONOS2.stop()
        main.ONOS3.stop()
        main.ONOS2.rest_stop()
        #main.ONOS1.handle.sendline("cp ~/onos.properties.proactive ~/ONOS/conf/onos.properties")
        #main.ONOS2.handle.sendline("cp ~/onos.properties.proactive ~/ONOS/conf/onos.properties")
        #main.ONOS3.handle.sendline("cp ~/onos.properties.proactive ~/ONOS/conf/onos.properties")
        #main.step("Start tcpdump on mn")
        #main.Mininet2.start_tcpdump(main.params['tcpdump']['filename'], intf = main.params['tcpdump']['intf'], port = main.params['tcpdump']['port'])
        main.step("Start ONOS")
        time.sleep(5)
        main.Zookeeper1.start()
        main.Zookeeper2.start()
        main.Zookeeper3.start()
        time.sleep(5)
        main.RamCloud1.del_db()
        main.RamCloud2.del_db()
        main.RamCloud3.del_db()
        #time.sleep(5)
        #main.ONOS1.stop_all()
        #main.ONOS2.stop_all()
        #main.ONOS3.stop_all()
        #main.ONOS2.stop_rest()
#        main.log.report("Pulling latest code from github to all nodes")
#        for i in range(2):
#            uptodate = main.ONOS1.git_pull()
#            main.ONOS2.git_pull()
#            main.ONOS3.git_pull()
#            main.ONOS4.git_pull()
#            ver1 = main.ONOS1.get_version()
#            ver2 = main.ONOS4.get_version()
#            if ver1==ver2:
#                break
#            elif i==1:
#                main.ONOS2.git_pull("ONOS1 master")
#                main.ONOS3.git_pull("ONOS1 master")
#                main.ONOS4.git_pull("ONOS1 master")
#        if uptodate==0:
       # if 1:
#            main.ONOS1.git_compile()
#            main.ONOS2.git_compile()
#            main.ONOS3.git_compile()
#            main.ONOS4.git_compile()
#        main.ONOS1.print_version()    
       # main.RamCloud1.git_pull()
       # main.RamCloud2.git_pull()
       # main.RamCloud3.git_pull()
       # main.RamCloud4.git_pull()
       # main.ONOS1.get_version()
       # main.ONOS2.get_version()
       # main.ONOS3.get_version()
       # main.ONOS4.get_version()
        #main.RamCloud1.start_coor()
       
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
        main.step("Testing startup ONOS")   
        data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup()
        for i in range(3):
            if data == main.FALSE: 
                #main.log.report("Something is funny... restarting ONOS")
                #main.ONOS1.stop()
                #main.ONOS2.stop()
                #main.ONOS3.stop()
                #time.sleep(3)
                main.ONOS1.handle.sendline("cd ~/ONOS")
                main.ONOS2.handle.sendline("cd ~/ONOS")
                main.ONOS3.handle.sendline("cd ~/ONOS")

                main.ONOS1.handle.sendline("./onos.sh start")
                main.ONOS2.handle.sendline("./onos.sh start")
                main.ONOS3.handle.sendline("./onos.sh start")
                time.sleep(5) 
                data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup()
            else:
                break
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="ONOS is up and running!",onfail="ONOS didn't start...")
        time.sleep(20)
           
#**********************************************************************************************************************************************************************************************
#Assign a single switch to a controller and verify assignment. Measure time to add switch

    def CASE2(self,main) :    #Make sure mininet exists, then assign controllers to switches
        import re
        import time
        main.log.report("Check if mininet started properly, then assign controllers ONOS 1,2,3 and 4")
        #main.case("Checking if one MN host exists")
        #main.step("Host IP Checking using checkIP")
        #result = main.Mininet1.checkIP(main.params['CASE1']['destination'])
        #main.step("Verifying the result")
        #utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Host IP address configured",onfail="Host IP address not configured")
        main.case("Starting tshark open flow capture")
        main.ONOS1.stop_tshark() 
        main.ONOS1.tshark_of("add")
        main.case("Assigning a switch to the ONOS controller")
        #main.Mininet1.assign_sw_contorller(sw=str(1),ip0=main.params['CTRL']['ip0'],port0=main.params['CTRL']['port0'])
        main.Mininet1.handle.sendline("sh ovs-vsctl set-controller s1 tcp:10.128.5.51:6633")
        time.sleep(1)
        main.step("Verifying that switch is assigned properly")
        response=main.Mininet1.get_sw_controller("s1")
        if re.search("tcp:"+main.params['CTRL']['ip1'],response):
            main.log.report("Switch assigned correctly")
        else:
            main.log.error("Switch was NOT assigned correctly")
            print response
        main.case("Stopping tshark open flow capture")
        main.ONOS1.stop_tshark()
        #TODO: Obtain timestamp via rest here 
        time.sleep(5)
 
        main.ONOS1.tshark_of("remove")
        main.case("Removing the switch from the controller")
        main.Mininet1.handle.sendline("sh ovs-vsctl del-controller s1")
        time.sleep(1)
        main.step("Verifying that switch was removed")
        response = main.Mininet1.get_sw_controller("s1")
        print "response: " + response
        main.ONOS1.stop_tshark()
        #TODO: Obtain timestamp via rest here
        time.sleep(5)

# **********************************************************************************************************************************************************************************************
#Disable a port on a switch and add to controller. enable and obtain timestamps
    def CASE3(self,main):
        import re
        import time

        main.log.report("Measuring time to enable / disable port")
   
        #Disable the port connected to host on switch 1
        main.Mininet1.handle.sendline("sudo ifconfig s1-eth1 down")
        main.Mininet1.handle.expect("\$")
        #Assign switch to controller 
        main.Mininet1.handle.sendline("sh ovs-vsctl set-controller s1 tcp:10.128.5.51:6633")
        time.sleep(1)
        main.step("Verifying that switch is assigned properly")
        response=main.Mininet1.get_sw_controller("s1")
        if re.search("tcp:"+main.params['CTRL']['ip1'],response):
            main.log.report("Switch assigned correctly")
        else:
            main.log.error("Switch was NOT assigned correctly")
            print response
        
        #Start tshark and re-enable the port
        main.ONOS1.tshark_of("port_enable")
        main.Mininet1.handle.sendline("sudo ifconfig s1-eth1 up")
        #TODO: get timestamps from ONOS instances of ports coming up
        main.ONOS1.stop_tshark()

    def CASE11(self, main):
        import requests
        import json
        import time
        #Assign all switches to controllers
        for i in range(1,8):
            if i < 3:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
                time.sleep(5) 
                #main.Mininet1.assign_sw_controller(sw=str(i),count=3,\
                #                                   ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],\
                #                                   ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],\
                #                                   ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'])
            elif i < 6 and i > 2:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=main.params['CTRL']['ip2'],port1=main.params['CTRL']['port2'])
                time.sleep(5)
                #main.Mininet1.assign_sw_controller(sw=str(i),count=3,\
                #                                   ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],\
                #                                   ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],\
                #                                   ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'])
            elif i < 8 and i > 5:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=main.params['CTRL']['ip3'],port1=main.params['CTRL']['port3'])
                time.sleep(5)
                #main.Mininet1.assign_sw_controller(sw=str(i),count=3,\
                #                                   ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],\
                #                                   ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],\
                #                                   ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'])
        time.sleep(10)        
        
 
    def CASE99(self, main):
    #TEST CASE 99 - remove when done
        import time
        main.ONOS2.handle.sendline("cd ~/ONOS/scripts")
        main.ONOS2.handle.sendline("./pyintents.py")
        time.sleep(10) 
        main.ONOS2.handle.sendline("cd ..")
        url = main.params['INTENTS']['url_new']
        string = main.ONOS2.handle.sendline("curl -s "+url) 
        print string
        main.ONOS2.comp_intents(string, string)

#**********************************************
#Single intent add / delete performance    
    def CASE4(self, main):
        import requests
        import json
        import time
        #Assign all switches to controllers
        for i in range(1,8):
            if i < 3:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
                time.sleep(5) 
                #main.Mininet1.assign_sw_controller(sw=str(i),count=3,\
                #                                   ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],\
                #                                   ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],\
                #                                   ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'])
            elif i < 6 and i > 2:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=main.params['CTRL']['ip2'],port1=main.params['CTRL']['port2'])
                time.sleep(5)
                #main.Mininet1.assign_sw_controller(sw=str(i),count=3,\
                #                                   ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],\
                #                                   ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],\
                #                                   ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'])
            elif i < 8 and i > 5:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=main.params['CTRL']['ip3'],port1=main.params['CTRL']['port3'])
                time.sleep(5)
                #main.Mininet1.assign_sw_controller(sw=str(i),count=3,\
                #                                   ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],\
                #                                   ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],\
                #                                   ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'])
        time.sleep(10)        
       
        #Assign variables from params file 
        intent_ip = main.params['INTENTREST']['intentIP']
        url = main.params['INTENTS']['url_new']
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        intent_id = main.params['INTENTS']['intent_id']
        intent_id2 = main.params['INTENTS']['intent_id2'] 
        intent_type = main.params['INTENTS']['intent_type']
        srcSwitch = main.params['INTENTS']['srcSwitch']
        srcPort = int(main.params['INTENTS']['srcPort'])
        srcMac = main.params['INTENTS']['srcMac']
        dstSwitch = main.params['INTENTS']['dstSwitch']
        dstPort = int(main.params['INTENTS']['dstPort'])
        dstMac = main.params['INTENTS']['dstMac']
        numIter = main.params['INTENTS']['numIter']
        url_add = main.params['INTENTS']['urlAddIntent'] 
        url_rem = main.params['INTENTS']['urlRemIntent']
 
        intent_add_lat_list = []
        intent_rem_lat_list = []

        #NOTE: REST call may change in the future
        #For number of iterations, repeat add / remove and obtain latency min/max/avg calculations
        for i in range(0, int(numIter)):
            print "Iteration " + str(i)

            result = main.ONOS1.add_intent(intent_id = intent_id, src_dpid = srcSwitch, dst_dpid = dstSwitch, src_mac = srcMac, dst_mac = dstMac, intentIP = intent_ip)
            utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Intent Add Successful",onfail="Intent Add NOT successful...") 
            time.sleep(5)
            json_obj = main.ONOS1.get_json(url_add) 
            intent_lat_add = main.ONOS1.get_single_intent_latency(json_obj)
            main.log.report("Intent Add Latency of Intent ID "+intent_id+": " + str(intent_lat_add) + " ms")
            intent_add_lat_list.append(intent_lat_add)
            print intent_add_lat_list

            intent_del = requests.delete(url+"/"+intent_id)
            time.sleep(5)
            json_obj = main.ONOS1.get_json(url_rem)
            intent_lat_rem = main.ONOS1.get_single_intent_latency(json_obj)
            main.log.report("Intent Rem Latency of Intent ID "+intent_id+": " + str(intent_lat_rem) + "ms")
            intent_rem_lat_list.append(intent_lat_rem)
            print intent_rem_lat_list

            time.sleep(2)

        min_lat = min(intent_add_lat_list)
        max_lat = max(intent_add_lat_list)
        avg_lat = sum(intent_add_lat_list) / len(intent_add_lat_list)
        
        main.log.report("Intent add latency min: "+ str(min_lat))
        main.log.report("Intent add latency max: "+ str(max_lat))
        main.log.report("Intent add latency avg: "+ str(avg_lat))

        min_lat = min(intent_rem_lat_list)
        max_lat = max(intent_rem_lat_list)
        avg_lat = sum(intent_rem_lat_list) / len(intent_rem_lat_list)

        main.log.report("Intent rem latency min: "+ str(min_lat))
        main.log.report("Intent rem latency max: "+ str(max_lat))
        main.log.report("Intent rem latency avg: "+ str(avg_lat)) 
# **********************************************************************************************************************************************************************************************
#This case tests performance of Intent Reroute Installation

    def CASE5(self,main):
        import requests
        import json
        import time 
        import subprocess

        #To bring link down: link s1 s2 down
        #Assign variables from params file 
        url = main.params['INTENTS']['url_new']
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        intent_id = main.params['INTENTS']['intent_id']
        intent_type = main.params['INTENTS']['intent_type']
        srcSwitch = main.params['INTENTS']['srcSwitch2']
        srcPort = int(main.params['INTENTS']['srcPort'])
        srcMac = main.params['INTENTS']['srcMac2']
        dstSwitch = main.params['INTENTS']['dstSwitch2']
        dstPort = int(main.params['INTENTS']['dstPort'])
        dstMac = main.params['INTENTS']['dstMac2']
        intent_id2 = "1"+intent_id

        #Add intents in both directions
        main.ONOS1.add_intent(intent_id = intent_id, src_dpid = srcSwitch, dst_dpid = dstSwitch, src_mac = srcMac, dst_mac = dstMac, intentIP = main.params['INTENTREST']['intentIP'])
        main.ONOS1.add_intent(intent_id = intent_id2, src_dpid = dstSwitch, dst_dpid = srcSwitch, src_mac = dstMac, dst_mac = srcMac, intentIP = main.params['INTENTREST']['intentIP'])

        result = main.Mininet1.pingHost(src="h1",target="h7") 
        print result

        main.ONOS1.stop_tshark() 
        
        time.sleep(5)
        main.case("Starting tshark open flow capture") 
        #TODO: research tshark capture options to filter OFP packets. 
        #main.ONOS1.handle.sendline("tshark -i eth0 -t e | grep 'OFP 130 Port Status' > /tmp/tshark_of_port.txt")
        #main.ONOS2.handle.sendline("tshark -i eth0 -t e | grep 'OFP 130 Port Status' > /tmp/tshark_of_port.txt")
        #main.ONOS3.handle.sendline("tshark -i eth0 -t e | grep 'OFP 130 Port Status' > /tmp/tshark_of_port.txt")
         
        main.ONOS2.handle.sendline("tshark - i eth0 -t e | grep 'OFP' > /tmp/tshark_of_port.txt")

        #main.ONOS1.handle.sendline("tshark -i eth0 -t e -P -w | grep 'OFP 130 Port Status' > /tmp/tshark_of_port_raw.txt")
        time.sleep(10) 
        #Bring down interface (port)
        main.Mininet1.link(END1="s3",END2="s5",OPTION="down") 
        main.Mininet1.handle.sendline("")
        #main.Mininet1.handle.sendline("sudo ifconfig s3-eth2 down")
        #main.Mininet1.handle.sendline("ifconfig")

        time.sleep(5)
        main.ONOS1.stop_tshark()
        #Check flow
        result = main.Mininet1.pingHost(src="h1",target="h7") 
       
        #TESTING IF link down actually even works. If it does, ping should not go through
        main.Mininet1.link(END1="s3",END2="s4",OPTION="down")
        result = main.Mininet1.pingHost(src="h1",target="h7")
 
        #Read ONOS tshark_of_port file and get first line
        #TODO: improve accuracy of timestamp by parsing packet data using "tshark -V" option
        ssh = subprocess.Popen(['ssh', 'admin@'+main.params['CTRL']['ip1'], 'cat', '/tmp/tshark_of_port.txt'],stdout=subprocess.PIPE)
        port_down_time = ssh.stdout.readline()
        ssh2 = subprocess.Popen(['ssh', 'admin@'+main.params['CTRL']['ip2'], 'cat', '/tmp/tshark_of_port.txt'],stdout=subprocess.PIPE)
        port_down_time2 = ssh.stdout.readline()
        ssh3 = subprocess.Popen(['ssh', 'admin@'+main.params['CTRL']['ip3'], 'cat', '/tmp/tshark_of_port.txt'],stdout=subprocess.PIPE)
        port_down_time3 = ssh.stdout.readline()        

        print port_down_time 
        print port_down_time2 
        print port_down_time3

        obj = port_down_time.split(" ")
        timestamp = obj[0] 
        print obj
        print timestamp
 
        time.sleep(10)
        main.Mininet1.pingHost(src="h1",target="h7") 
 
# **********************************************************************************************************************************************************************************************
# Intent Batch Installation Latency

    def CASE6(self,main):
        main.log.report("Adding batch of intents to calculate latency")
        numflows = main.params['INTENTS']['numFlows']
        ip = main.params['INTENTREST']['intentIP']
        intaddr = main.params['INTENTS']['url_new']
        url_add = main.params['INTENTS']['urlAddIntent']

        result = main.ONOS1.dynamicIntent(NUMFLOWS = numflows, INTADDR = intaddr, OPTION = "ADD")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Batch installation successful",onfail="Batch installation NOT successful...")
        
        #TODO: get timestamp of batch installation here
        json_obj = main.ONOS1.get_json(url_add) 
        intent_lat_add = main.ONOS1.get_single_intent_latency(json_obj)
        main.log.report("Intent Add Batch latency: " + str(intent_lat_add) + " ms")
 

# **********************************************************************************************************************************************************************************************
#Brings the link that Case 6 took down  back up, then runs a ping test to view reroute time

    def CASE7(self,main) :
        main.log.report("Bring Link between s1 and s2 up, then ping until all hosts are reachable or fail after 10 attempts")
        import time
        main.case("Bringing Link up... ")
        result = main.Mininet1.link(END1='s1',END2='s3',OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Link UP!",onfail="Link not brought up...")
        time.sleep(10) 
        strtTime = time.time() 
        result = main.ONOS1.check_status_report(main.params['RestIP0'],main.params['NR_Switches'],str(int(main.params['NR_Links'])-2))
        for i in range(10):
            if result == main.FALSE:
                time.sleep(15)
                result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],str(int(main.params['NR_Links'])-2))
            else:
                break

        strtTime = time.time()
        count = 1
        i = 6
        while i < 16 :
            main.log.info("\n\t\t\t\th"+str(i)+" IS PINGING h"+str(i+25) )
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+25))
            if ping == main.FALSE and count < 10:
                count = count + 1
                main.log.info("Ping failed, making attempt number "+str(count)+" in 2 seconds")
                i = 6
                time.sleep(2)
            elif ping == main.FALSE and count ==10:
                main.log.error("Ping test failed")
                i = 17
                result = main.FALSE
            elif ping == main.TRUE:
                i = i + 1
                result = main.TRUE
        endTime = time.time()
        if result == main.TRUE:
            main.log.report("\tTime to complete ping test: "+str(round(endTime-strtTime,2))+" seconds")
        else:
            main.log.report("\tPING TESTS FAILED")
        data = main.Mininet1.link(END1='s1',END2='s3',OPTION="up")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="NO PACKET LOSS, HOST IS REACHABLE",onfail="PACKET LOST, HOST IS NOT REACHABLE")


# ******************************************************************************************************************************************************************
# Test Device Discovery function by yanking s6:s6-eth0 interface and re-plug it into a switch

    def CASE21(self,main) :
        import json
        main.log.report("Test device discovery function, by attach, detach, move host h1 from s1->s6->s1. Per mininet naming, switch port the host attaches will remain as 's1-eth1' throughout the test.")
        main.log.report("Check initially hostMAC/IP exist on the mininet...")
        host = main.params['YANK']['hostname']
        mac = main.params['YANK']['hostmac']
        RestIP1 = main.params['RESTCALL']['restIP1']
        RestPort = main.params['RESTCALL']['restPort']
        url = main.params['RESTCALL']['restURL']
       
        t_topowait = 5
        t_restwait = 5
        main.log.report( "Wait time from topo change to ping set to " + str(t_topowait))
        main.log.report( "Wait time from ping to rest call set to " + str(t_restwait))
        #print "host=" + host + ";  RestIP=" + RestIP1 + ";  RestPort=" + str(RestPort)
        time.sleep(t_topowait) 
        main.log.info("\n\t\t\t\t ping issue one ping from " + str(host) + " to generate arp to switch. Ping result is not important" )
        ping = main.Mininet1.pingHost(src = str(host),target = "10.0.0.254")
        time.sleep(t_restwait)
        Reststatus, Switch, Port = main.ONOS1.find_host(RestIP1,RestPort,url, mac)
        main.log.report("Number of host with MAC address = " + mac + " found by ONOS is: " + str(Reststatus))
        if Reststatus == 1:
            main.log.report("\t PASSED - Found host mac = " + mac + ";  attached to switchDPID = " +"".join(Switch) + "; at port = " + str(Port[0]))
            result1 = main.TRUE
        elif Reststatus > 1:
            main.log.report("\t FAILED - Host " + host + " with MAC:" + mac + " has " + str(Reststatus) + " duplicated mac  addresses. FAILED")
            main.log.report("switches are: " + "; ".join(Switch))
            main.log.report("Ports are: " + "; ".join(Port))
            result1 = main.FALSE
        elif Reststatus == 0 and Switch == []:
            main.log.report("\t FAILED - Host " + host + " with MAC:" + mac + " does not exist. FAILED")
            result1 = main.FALSE
        else:# check if rest server is working
            main.log.error("Issue with find host")
            result1 = main.FALSE


        ##### Step to yank out "s1-eth1" from s1, which is on autoONOS1 #####

        main.log.report("Yank out s1-eth1")
        main.case("Yankout s6-eth1 (link to h1) from s1")
        result = main.Mininet1.yank(SW=main.params['YANK']['sw1'],INTF=main.params['YANK']['intf'])
        time.sleep(t_topowait)
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Yank command suceeded",onfail="Yank command failed...")

        main.log.info("\n\t\t\t\t ping issue one ping from " + str(host) + " to generate arp to switch. Ping result is not important" )
        ping = main.Mininet1.pingHost(src = str(host),target = "10.0.0.254")
        time.sleep(t_restwait)
        Reststatus, Switch, Port = main.ONOS1.find_host(RestIP1,RestPort,url, mac)

        main.log.report("Number of host with MAC = " + mac + " found by ONOS is: " + str(Reststatus))
        if Reststatus == 1:
            main.log.report("\tFAILED - Found host MAC = " + mac + "; attached to switchDPID = " + "".join(Switch) + "; at port = " + str(Port))
            result2 = main.FALSE
        elif Reststatus > 1:
            main.log.report("\t FAILED - Host " + host + " with MAC:" + str(mac) + " has " + str(Reststatus) + " duplicated IP addresses. FAILED")
            main.log.report("switches are: " + "; ".join(Switch))
            main.log.report("Ports are: " + "; ".join(Port))
            main.log.report("MACs are: " + "; ".join(MAC))
            result2 = main.FALSE
        elif Reststatus == 0 and Switch == []:
            main.log.report("\t PASSED - Host " + host + " with MAC:" + str(mac) + " does not exist. PASSED - host is not supposed to be attached to the switch.")
            result2 = main.TRUE
        else:# check if rest server is working
            main.log.error("Issue with find host")
            result2 = main.FALSE
         
        ##### Step to plug "s1-eth1" to s6, which is on autoONOS3  ######
        main.log.report("Plug s1-eth1 into s6")
        main.case("Plug s1-eth1 to s6")
        result = main.Mininet1.plug(SW=main.params['PLUG']['sw6'],INTF=main.params['PLUG']['intf'])
        time.sleep(t_topowait)
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Plug command suceeded",onfail="Plug command failed...")
        main.log.info("\n\t\t\t\t ping issue one ping from " + str(host) + " to generate arp to switch. Ping result is not important" )

        ping = main.Mininet1.pingHost(src = str(host),target = "10.0.0.254")
        time.sleep(t_restwait)
        Reststatus, Switch, Port = main.ONOS1.find_host(RestIP1,RestPort,url, mac)

        main.log.report("Number of host with MAC " + mac + " found by ONOS is: " + str(Reststatus))
        if Reststatus == 1:
            main.log.report("\tPASSED - Found host MAC = " + mac + "; attached to switchDPID = " + "".join(Switch) + "; at port = " + str(Port[0]))
            result3 = main.TRUE
        elif Reststatus > 1:
            main.log.report("\t FAILED - Host " + host + " with MAC:" + str(mac) + " has " + str(Reststatus) + " duplicated IP addresses. FAILED")
            main.log.report("switches are: " + "; ".join(Switch))
            main.log.report("Ports are: " + "; ".join(Port))
            main.log.report("MACs are: " + "; ".join(MAC))            
            result3 = main.FALSE
        elif Reststatus == 0 and Switch == []:
            main.log.report("\t FAILED - Host " + host + " with MAC:" + str(mac) + " does not exist. FAILED")
            result3 = main.FALSE
        else:# check if rest server is working
            main.log.error("Issue with find host")
            result3 = main.FALSE

        ###### Step to put interface "s1-eth1" back to s1"#####
        main.log.report("Move s1-eth1 back on to s1")
        main.case("Move s1-eth1 back to s1")
        result = main.Mininet1.yank(SW=main.params['YANK']['sw6'],INTF=main.params['YANK']['intf'])
        time.sleep(t_topowait)
        result = main.Mininet1.plug(SW=main.params['PLUG']['sw1'],INTF=main.params['PLUG']['intf'])
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Yank/Plug command suceeded",onfail="Yank/Plug command failed...")
        main.log.info("\n\t\t\t\t ping issue one ping from " + str(host) + " to generate arp to switch. Ping result is not important" )

        ping = main.Mininet1.pingHost(src = str(host),target = "10.0.0.254")
        time.sleep(t_restwait)
        Reststatus, Switch, Port = main.ONOS1.find_host(RestIP1,RestPort,url, mac)

        main.log.report("Number of host with IP=10.0.0.1 found by ONOS is: " + str(Reststatus))
        if Reststatus == 1:
            main.log.report("\tPASSED - Found host MAC = " + mac + "; attached to switchDPID = " + "".join(Switch) + "; at port = " + str(Port[0]))
            result4 = main.TRUE
        elif Reststatus > 1:
            main.log.report("\t FAILED - Host " + host + " with MAC:" + str(mac) + " has " + str(Reststatuas) + " duplicated IP addresses. FAILED")
            main.log.report("switches are: " + "; ".join(Switch))
            main.log.report("Ports are: " + "; ".join(Port))
            main.log.report("MACs are: " + "; ".join(MAC))            
            result4 = main.FALSE
        elif Reststatus == 0 and Switch == []:
            main.log.report("\t FAILED -Host " + host + " with MAC:" + str(mac) + " does not exist. FAILED")
            result4 = main.FALSE
        else:# check if rest server is working
            main.log.error("Issue with find host")
            result4 = main.FALSE
        time.sleep(20)
        Reststatus, Switch, Port = main.ONOS1.find_host(RestIP1,RestPort,url,mac)
        main.log.report("Number of host with IP=10.0.0.1 found by ONOS is: " + str(Reststatus))
        if Reststatus ==1:
            main.log.report("\t FAILED - Host " + host + "with MAC:" + str(mac) + "was still found after expected timeout")
        elif Reststatus>1:
            main.log.report("\t FAILED - Host " + host + "with MAC:" + str(mac) + "was still found after expected timeout(multiple found)")
        elif Reststatus==0:
            main.log.report("\t PASSED - Device cleared after timeout")

        result = result1 and result2 and result3 and result4
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="DEVICE DISCOVERY TEST PASSED PLUG/UNPLUG/MOVE TEST",onfail="DEVICE DISCOVERY TEST FAILED")

# Run a pure ping test. 

    def CASE31(self, main):
        main.log.report("Performing Ping Test")        
        count = 1
        i = 6
        while i < 16 :
            main.log.info("\n\t\t\t\th"+str(i)+" IS PINGING h"+str(i+25) )
            strtTime = time.time()
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+25))
            if ping == main.FALSE and count < 6:
                count = count + 1
                i = 6
                main.log.info("Ping failed, making attempt number "+str(count)+" in 2 seconds")
                time.sleep(2)
            elif ping == main.FALSE and count ==6:
                main.log.error("Ping test failed")
                i = 17
                result = main.FALSE
            elif ping == main.TRUE:
                i = i + 1
                result = main.TRUE
        endTime = time.time()
        if result == main.TRUE:
            main.log.report("\tTime to complete ping test: "+str(round(endTime-strtTime,2))+" seconds")
        else:
            main.log.report("\tPING TEST FAIL")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="NO PACKET LOSS, HOST IS REACHABLE",onfail="PACKET LOST, HOST IS NOT REACHABLE")


    def CASE66(self, main):
        main.log.report("Checking ONOS logs for exceptions")
        count = 0
        check1 = main.ONOS1.check_exceptions()
        main.log.report("Exceptions in ONOS1 logs: \n" + check1)
        check2 = main.ONOS2.check_exceptions()
        main.log.report("Exceptions in ONOS2 logs: \n" + check2)
        check3 = main.ONOS3.check_exceptions()
        main.log.report("Exceptions in ONOS3 logs: \n" + check3)
        check4 = main.ONOS4.check_exceptions()
        main.log.report("Exceptions in ONOS4 logs: \n" + check4)
        result = main.TRUE
        if (check1 or check2 or check3 or check4):
            result = main.FALSE
            count = len(check1.splitlines()) + len(check2.splitlines()) + len(check3.splitlines()) + len(check4.splitlines())
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="No Exceptions found in the logs",onfail=str(count) + " Exceptions were found in the logs")
        main.Mininet1.stop_tcpdump()


    def CASE8(self,main) :
        main.log.report("Testing Removal of Zookeeper")
        main.Zookeeper2.stop()
        main.Zookeeper3.stop()
        main.Zookeeper4.stop()
        strtTime = time.time() 
        result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        for i in range(10):
            if result == main.FALSE:
                time.sleep(5)
                result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
            else:
                break

        count = 1
        i = 6
        while i < 16 :
            main.log.info("\n\t\t\t\th"+str(i)+" IS PINGING h"+str(i+25) )
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+25))
            if ping == main.FALSE and count < 6:
                count = count + 1
                i = 6
                main.log.info("Ping failed, making attempt number "+str(count)+" in 2 seconds")
                time.sleep(2)
            elif ping == main.FALSE and count ==6:
                main.log.error("Ping test failed")
                i = 17
                result = main.FALSE
            elif ping == main.TRUE:
                i = i + 1
                result = main.TRUE
        endTime = time.time() 
        if result == main.TRUE:
            main.log.report("\tTime to complete ping test: "+str(round(endTime-strtTime,2))+" seconds")
        else:
            main.log.report("\tPING TEST FAIL")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="NO PACKET LOSS, HOST IS REACHABLE",onfail="PACKET LOST, HOST IS NOT REACHABLE")
        time.sleep(10)
        main.Zookeeper2.start() 
        main.Zookeeper3.start()
        main.Zookeeper4.start() 
        time.sleep(10)


    def CASE67(self, main) :
        main.case("Flapping link s1-s2")
        main.log.report("Toggling of link s1-s2 multiple times")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")

        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],str(int(main.params['NR_Links'])-2))
        for i in range(10):
            if result == main.FALSE:
                time.sleep(15)
                result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],str(int(main.params['NR_Links'])-2))
            else:
                break

        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],str(int(main.params['NR_Links'])))
        for i in range(10):
            if result == main.FALSE:
                time.sleep(15)
                result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],str(int(main.params['NR_Links'])))
            else:
                break
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],str(int(main.params['NR_Links'])-2))
        for i in range(10):
            if result == main.FALSE:
                time.sleep(15)
                result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],str(int(main.params['NR_Links'])-2))
            else:
                break
           


    def CASE101(self,main) :
        import time
        import json
        import re
        main.case("Testing the Intent Framework of ONOS")
        
        main.step("Assigning Master Controllers to the Switches and check")
        for i in range(25):
            if i<3:
                j=i+1
                main.Mininet1.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
            elif i>=3 and i<5:
                j=i+1
                main.Mininet1.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip2'],port1=main.params['CTRL']['port1'])
            elif i>=5 and i<15:
                j=j+1
                main.Mininet1.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip3'],port1=main.params['CTRL']['port1'])
            else:
                j=i+16
                main.Mininet1.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip4'],port1=main.params['CTRL']['port1'])
        result = main.TRUE
        for i in range(25):
            if i<3:
                j=i+1
                response=main.Mininet1.get_sw_controller("s"+str(j))
                print(response)
                if re.search("tcp:"+main.params['CTRL']['ip1'],response) :
                    result = result and main.TRUE
                else:
                    result = main.FALSE
            elif i>=3 and i<5:
                j=i+1
                response=main.Mininet1.get_sw_controller("s"+str(j))
                if re.search("tcp:"+main.params['CTRL']['ip2'],response) :
                    result = result and main.TRUE
                else:
                    result = main.FALSE
            elif i>=5 and i<15:
                j=j+1
                response=main.Mininet1.get_sw_controller("s"+str(j))
                if re.search("tcp:"+main.params['CTRL']['ip3'],response) :
                    result = result and main.TRUE
                else:
                    result = main.FALSE
            else:
                j=i+16
                response=main.Mininet1.get_sw_controller("s"+str(j))
                if re.search("tcp:"+main.params['CTRL']['ip4'],response) :
                    result = result and main.TRUE
                else:
                    result = main.FALSE
            print(result)
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Master Controllers assigned Properly",onfail="FAILED TO ASSIGN MASTER CONTROLLERS!")

        main.step("Assigning all Controllers as Backups to Switches and Check")
        for i in range(25):
            if i<15:
                j=i+1
                main.Mininet1.assign_sw_controller(sw=str(j),count=4,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'])
            else:
                j=i+16
                main.Mininet1.assign_sw_controller(sw=str(j),count=4,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'])
        result = main.TRUE
        for i in range(25):
            if i<15:
                j=i+1
                response=main.Mininet1.get_sw_controller("s"+str(j))
                if re.search("tcp:"+main.params['CTRL']['ip1'],response) and re.search("tcp:"+main.params['CTRL']['ip2'],response) and re.search("tcp:"+main.params['CTRL']['ip3'],response) and re.search("tcp:"+main.params['CTRL']['ip4'],response):
                    result = result and main.TRUE
                else:
                    result = main.FALSE
            else:
                j=i+16
                response=main.Mininet1.get_sw_controller("s"+str(j))
                if re.search("tcp:"+main.params['CTRL']['ip1'],response) and re.search("tcp:"+main.params['CTRL']['ip2'],response) and re.search("tcp:"+main.params['CTRL']['ip3'],response) and re.search("tcp:"+main.params['CTRL']['ip4'],response):
                    result = result and main.TRUE
                else:
                    result = main.FALSE
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Controllers assigned properly to all switches",onfail="FAILED TO ASSIGN CONTROLLERS PROPERLY!")
        
        main.step("Install intents and Check for Installation of Flows")
        intentIP = main.params['INTENTREST']['intentIP']
        intentPort=main.params['INTENTREST']['intentPort']
        intentURL=main.params['INTENTREST']['intentURL']
        for i in range(6,16):
            srcMac = '00:00:00:00:00:' + str(hex(i)[2:]).zfill(2)
            dstMac = '00:00:00:00:00:'+str(hex(i+25)[2:])
        #    srcDPID=str(i)
        #    dstDPID=str(i+10)
            srcDPID = '00:00:00:00:00:00:10:'+str(i).zfill(2)
            dstDPID= '00:00:00:00:00:00:20:' +str(i+25)
            main.ONOS1.add_intent(intent_id=str(i),src_dpid=srcDPID,dst_dpid=dstDPID,src_mac=srcMac,dst_mac=dstMac,intentIP=intentIP,intentPort=intentPort,intentURL=intentURL)
        result = main.TRUE
        response = main.Mininet1.check_flows(sw="s1")
        for i in range(6,16):
            if re.search("dl_src=00:00:00:00:00:"+''.join('%02x'%i),response) and re.search("dl_src=00:00:00:00:00:"+''.join('%02x'%(i+10)),response) and re.search("dl_dst=00:00:00:00:00:"+''.join('%02x'%i),response) and re.search("dl_dst=00:00:00:00:00:"+''.join('%02x'%(i+10)),response):   
                result = result and main.TRUE
            else:
                result = main.FALSE
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Flows added Properly",onfail="Flows were not added properly")
 


    def CASE10(self, main) :
        import time
        time.sleep(600)
