
class RCOnosSanity :

    def __init__(self) :
        self.default = ''

#*****************************************************************************************************************************************************************************************
#Test startup
#Tests the startup of Zookeeper1, RamCloud1, and ONOS1 to be certain that all started up successfully
    def CASE1(self,main) :  #Check to be sure ZK, Cass, and ONOS are up, then get ONOS version
        import time
        main.ONOS.start()
        time.sleep(20)
        main.ONOS.rest_stop()
        main.ONOS.start_rest()
        test= main.ONOS.rest_status()
        if test == main.FALSE:
            main.ONOS.start_rest()
        main.ONOS.get_version()
        main.log.report("Started Zookeeper, RamCloud, and ONOS")
        main.case("Checking if the startup was clean...")
        main.step("Testing Zookeeper Status")   
        data =  main.ONOS.zk_status()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Zookeeper is up!",onfail="Zookeeper is down...")
        main.step("Testing Ramcloud Coord Status")   
        data =  main.ONOS.rcc_status()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Ramcloud Coord is up!",onfail="Ramcloud Coord is down...")
        main.step("Testing Ramcloud Server Status")   
        data =  main.ONOS.rcs_status()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Ramcloud Server is up!",onfail="Ramcloud Server is down...")
        main.step("Testing ONOS Status")   
        data =  main.ONOS.status()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="ONOS is up!",onfail="ONOS is down...")
        main.step("Testing Rest Status")
        data =  main.ONOS.rest_status()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="REST is up!",onfail="REST is down...")
	
#**********************************************************************************************************************************************************************************************
#Assign Controllers
#This test first checks the ip of a mininet host, to be certain that the mininet exists(Host is defined #inParams as <CASE1><destination>).
#Then the program assignes each ONOS instance a single controller to a switch(To be the initial master), then #assigns all controllers.    

    def CASE2(self,main) :    #Make sure mininet exists, then assign controllers to switches
        import time
        main.log.report("Check if mininet started properly, then assign the switches to ONOS")
        main.case("Checking if one MN host exists")
        main.step("Host IP Checking using checkIP")
        result = main.Mininet.checkIP(main.params['CASE1']['destination'])
        main.step("Verifying the result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Host IP address configured",onfail="Host IP address not configured")
        main.step("assigning ONOS controller to switches")
        for i in range(25):
            if i < 15:
                j=i+1
                main.Mininet.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
            else:
                j=i+16
                main.Mininet.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
        #time.sleep(1)
        main.Mininet.get_sw_controller("s1")

# **********************************************************************************************************************************************************************************************
#Add Flows
#Deletes any remnant flows from any previous test, add flows from the file labeled <FLOWDEF>, then runs the #check flow test

    def CASE3(self,main) :    #Delete any remnant flows, then add flows, and time how long it takes flow tables to update
        main.log.report("Delete any flows from previous tests, then add flows from FLOWDEF file, then wait for switch flow tables to update")
        import time
        main.case("Taking care of these flows!") 
        main.step("Cleaning out any leftover flows...")
        main.ONOS.delete_flow(main.params['INTENTS']['rem'], main.params['FLOWDEF'])
        strtTime = time.time()
        main.ONOS.add_flow(main.params['INTENTS']['add'], main.params['FLOWDEF'])
        main.case("Checking flows")
        
        count = 1
        i = 6
        while i < 16 :
            main.log.info("\n\t\t\t\th"+str(i)+" IS PINGING h"+str(i+25) )
            ping = main.Mininet.pingHost(SRC="h"+str(i),TARGET="h"+str(i+25))
            if ping == main.FALSE and count < 9:
                count = count + 1
                i = 6
                main.log.info("Ping failed, making attempt number "+str(count)+" in 2 seconds")
                time.sleep(2)
            elif ping == main.FALSE and count ==9:
                main.log.error("Ping test failed")
                i = 17
                result = main.FALSE
            elif ping == main.TRUE:
                i = i + 1
                result = main.TRUE
        endTime = time.time()
        if result == main.TRUE:
            main.log.report("\tTime to add flows: "+str(round(endTime-strtTime,2))+" seconds")
        else:
            main.log.report("\tFlows failed check")

        result2 = main.ONOS.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        main.step("Verifying the result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Flow check PASS",onfail="Flow check FAIL")

##########*****************************************************
    def CASE4(self,main) :
        main.log.report("Remove ONOS 2,3,4 then ping until all hosts are reachable or fail after 6 attempts")
        import time
        for i in range(25):
            if i < 15:
                j=i+1
                main.Mininet.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
            else:
                j=i+16
                main.Mininet.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
        strtTime = time.time()
        result = main.ONOS.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        for i in range(10):
            if result == main.FALSE:
                time.sleep(5)
                result = main.ONOS.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
            else:
                break
        count = 1
        i = 6
        while i < 16 :
            main.log.info("\n\t\t\t\th"+str(i)+" IS PINGING h"+str(i+25) )
            ping = main.Mininet.pingHost(src="h"+str(i),target="h"+str(i+25))
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

# **********************************************************************************************************************************************************************************************
#This test case restores the controllers removed by Case 4 then performs a ping test.

    def CASE5(self,main) :
        main.log.report("Restore ONOS 2,3,4 then ping until all hosts are reachable or fail after 6 attempts")
        import time
        for i in range(25):
            if i < 15:
                j=i+1
                main.Mininet.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
            else:
                j=i+16
                main.Mininet.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
        strtTime = time.time()
        result = main.ONOS.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        for i in range(2):
            if result == main.FALSE:
                time.sleep(5)
                result = main.ONOS.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
            else:
                break
        count = 1
        i = 6
        while i < 16 :
            main.log.info("\n\t\t\t\th"+str(i)+" IS PINGING h"+str(i+25) )
            ping = main.Mininet.pingHost(src="h"+str(i),target="h"+str(i+25))
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
            main.log.report("\tPING TEST FAILED")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="NO PACKET LOSS, HOST IS REACHABLE",onfail="PACKET LOST, HOST IS NOT REACHABLE") 
# #**********************************************************************************************************************************************************************************************
#Brings a link that all flows pass through in the mininet down, then runs a ping test to view reroute time

    def CASE6(self,main) :
        main.log.report("Bring Link between s1 and s2 down, then ping until all hosts are reachable or fail after 10 attempts")
        import time
        main.case("Bringing Link down... ")
        result = main.Mininet.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Link DOWN!",onfail="Link not brought down...")
       
        strtTime = time.time() 
        result = main.ONOS.check_status_report(main.params['RestIP'],main.params['NR_Switches'],str(int(main.params['NR_Links'])-2))
        for i in range(2):
            if result == main.FALSE:
                time.sleep(5)
                result = main.ONOS.check_status_report(main.params['RestIP'],main.params['NR_Switches'],str(int(main.params['NR_Links'])-2))
            else:
                break
        count = 1
        i = 6
        while i < 16 :
            main.log.info("\n\t\t\t\th"+str(i)+" IS PINGING h"+str(i+25) )
            ping = main.Mininet.pingHost(src="h"+str(i),target="h"+str(i+25))
            if ping == main.FALSE and count < 10:
                count = count + 1
                main.log.info("Ping failed, making attempt number "+str(count)+" in 2 seconds")
                i = 6
                time.sleep(2)
            elif ping == main.FALSE and count == 10:
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
            main.log.report("\tPING TEST FAILED")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="NO PACKET LOSS, HOST IS REACHABLE",onfail="PACKET LOST, HOST IS NOT REACHABLE")
# #**********************************************************************************************************************************************************************************************
#Brings the link that Case 6 took down  back up, then runs a ping test to view reroute time

    def CASE7(self,main) :
        main.log.report("Bring Link between s1 and s2 up, then ping until all hosts are reachable or fail after 10 attempts")
        import time
        main.case("Bringing Link up... ")
        result = main.Mininet.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Link UP!",onfail="Link not brought up...")      
        strtTime = time.time()
        result = main.ONOS.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        for i in range(2):
            if result == main.FALSE:
                time.sleep(5)
                result = main.ONOS.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
            else:
                break
        strtTime = time.time()
        count = 1
        i = 6
        while i < 16 :
            main.log.info("\n\t\t\t\th"+str(i)+" IS PINGING h"+str(i+25) )
            ping = main.Mininet.pingHost(src="h"+str(i),target="h"+str(i+25))
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
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="NO PACKET LOSS, HOST IS REACHABLE",onfail="PACKET LOST, HOST IS NOT REACHABLE")
# #******************************************************************************************************************************************************************
# Test Device Discovery function by yanking s6:s6-eth0 interface and re-plug it into a switch

    def CASE21(self,main) :
        import json
        main.log.report("Test device discovery function, by attach, detach, move host h1 from s1->s6->s1. Per mininet naming, switch port the host attaches will remain as 's1-eth1' throughout the test.")
        main.log.report("Check initially hostMAC/IP exist on the mininet...")
        host = main.params['YANK']['hostname']
        mac = main.params['YANK']['hostmac']
        hostip = main.params['YANK']['hostip']
        RestIP1 = main.params['RESTCALL']['restIP1']
        RestPort = main.params['RESTCALL']['restPort']
        url = main.params['RESTCALL']['restURL']
       
        t_topowait = 0
        t_restwait = 10
        main.log.report( "Wait time from topo change to ping set to " + str(t_topowait))
        main.log.report( "Wait time from ping to rest call set to " + str(t_restwait))
        #print "host=" + host + ";  RestIP=" + RestIP1 + ";  RestPort=" + str(RestPort)
        time.sleep(t_topowait) 
        main.log.info("\n\t\t\t\t ping issue one ping from " + str(host) + " to generate arp to switch. Ping result is not important" )
        ping = main.Mininet.pingHost(SRC = str(host),TARGET = "10.0.0.254")
        time.sleep(t_restwait)
        Reststatus, Switch, Port, MAC = main.ONOS.find_host(RestIP1,RestPort,url, hostip)
        main.log.report("Number of host with IP=10.0.0.1 found by ONOS is: " + str(Reststatus))
        if Reststatus == 1:
            main.log.report("\t PASSED - Found host IP = " + hostip + "; MAC = " + "".join(MAC) + "; attached to switchDPID = " + "".join(Switch) + "; at port = " + "".join(Port))
            result1 = main.TRUE
        elif Reststatus > 1:
            main.log.report("\t FAILED - Host " + host + " with MAC:" + mac + " has " + str(Reststatus) + " duplicated IP addresses. FAILED")
            main.log.report("switches are: " + "; ".join(Switch))
            main.log.report("Ports are: " + "; ".join(Port))
            main.log.report("MACs are: " + "; ".join(MAC))
            result1 = main.FALSE
        else:
            main.log.report("\t FAILED - Host " + host + " with MAC:" + mac + " does not exist. FAILED")
            result1 = main.FALSE
        ##### Step to yank out "s1-eth1" from s1, which is on autoONOS1 #####
        main.log.report("Yank out s1-eth1")
        main.step("Yankout s6-eth1 (link to h1) from s1")
        result = main.Mininet.yank(SW=main.params['YANK']['sw1'],INTF=main.params['YANK']['intf'])
        time.sleep(t_topowait)
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Yank command suceeded",onfail="Yank command failed...")

        main.log.info("\n\t\t\t\t ping issue one ping from" + str(host) + "to generate arp to switch. Ping result is not important" )
        ping = main.Mininet.pingHost(SRC = str(host),TARGET = "10.0.0.254")
        time.sleep(t_restwait)
        Reststatus, Switch, Port, MAC = main.ONOS.find_host(RestIP1,RestPort,url, hostip)

        main.log.report("Number of host with IP=10.0.0.1 found by ONOS is: " + str(Reststatus))
        if Reststatus == 1:
            main.log.report("\tFAILED - Found host IP = " + hostip + "; MAC = " + "".join(MAC) + "; attached to switchDPID = " + "".join(Switch) + "; at port = " + "".join(Port))
            result2 = main.FALSE
        elif Reststatus > 1:
            main.log.report("\t FAILED - Host " + host + " with MAC:" + str(mac) + " has " + str(Reststatus) + " duplicated IP addresses. FAILED")
            main.log.report("switches are: " + "; ".join(Switch))
            main.log.report("Ports are: " + "; ".join(Port))
            main.log.report("MACs are: " + "; ".join(MAC))
            result2 = main.FALSE
        else:
            main.log.report("\t PASSED - Host " + host + " with MAC:" + str(mac) + " does not exist. PASSED - host is not supposed to be attached to the switch.")
            result2 = main.TRUE
         
        ##### Step to plug "s1-eth1" to s6, which is on autoONOS3  ######
        main.log.report("Plug s1-eth1 into s6")
        main.step("Plug s1-eth1 to s6")
        result = main.Mininet.plug(SW=main.params['PLUG']['sw6'],INTF=main.params['PLUG']['intf'])
        time.sleep(t_topowait)
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Plug command suceeded",onfail="Plug command failed...")
        main.log.info("\n\t\t\t\t ping issue one ping from" + str(host) + "to generate arp to switch. Ping result is not important" )

        ping = main.Mininet.pingHost(src = str(host),target = "10.0.0.254")
        time.sleep(t_restwait)
        Reststatus, Switch, Port, MAC = main.ONOS.find_host(RestIP1,RestPort,url, hostip)

        main.log.report("Number of host with IP=10.0.0.1 found by ONOS is: " + str(Reststatus))
        if Reststatus == 1:
            main.log.report("\tPASSED - Found host IP = " + hostip + "; MAC = " + "".join(MAC) + "; attached to switchDPID = " + "".join(Switch) + "; at port = " + "".join(Port))
            result3 = main.TRUE
        elif Reststatus > 1:
            main.log.report("\t FAILED - Host " + host + " with MAC:" + str(mac) + " has " + str(Reststatus) + " duplicated IP addresses. FAILED")
            main.log.report("switches are: " + "; ".join(Switch))
            main.log.report("Ports are: " + "; ".join(Port))
            main.log.report("MACs are: " + "; ".join(MAC))            
            result3 = main.FALSE
        else:
            main.log.report("\t FAILED - Host " + host + " with MAC:" + str(mac) + " does not exist. FAILED")
            result3 = main.FALSE

        ###### Step to put interface "s1-eth1" back to s1"#####
        main.log.report("Move s1-eth1 back on to s1")
        main.step("Move s1-eth1 back to s1")
        result = main.Mininet.yank(SW=main.params['YANK']['sw6'],INTF=main.params['YANK']['intf'])
        time.sleep(t_topowait)
        result = main.Mininet.plug(SW=main.params['PLUG']['sw1'],INTF=main.params['PLUG']['intf'])
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Yank/Plug command suceeded",onfail="Yank/Plug command failed...")
        main.log.info("\n\t\t\t\t ping issue one ping from" + str(host) + "to generate arp to switch. Ping result is not important" )

        ping = main.Mininet.pingHost(src = str(host),target = "10.0.0.254")
        time.sleep(t_restwait)
        Reststatus, Switch, Port, MAC = main.ONOS.find_host(RestIP1,RestPort,url, hostip)

        main.log.report("Number of host with IP=10.0.0.1 found by ONOS is: " + str(Reststatus))
        if Reststatus == 1:
            main.log.report("\tPASSED - Found host IP = " + hostip + "; MAC = " + "".join(MAC) + "; attached to switchDPID = " + "".join(Switch) + "; at port = " + "".join(Port))
            result4 = main.TRUE
        elif Reststatus > 1:
            main.log.report("\t FAILED - Host " + host + " with MAC:" + str(mac) + " has " + str(Reststatus) + " duplicated IP addresses. FAILED")
            main.log.report("switches are: " + "; ".join(Switch))
            main.log.report("Ports are: " + "; ".join(Port))
            main.log.report("MACs are: " + "; ".join(MAC))            
            result4 = main.FALSE
        else:
            main.log.report("\t FAILED -Host " + host + " with MAC:" + str(mac) + " does not exist. FAILED")
            result4 = main.FALSE

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
            ping = main.Mininet.pingHost(src="h"+str(i),target="h"+str(i+25))
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


    def CASE200(self, main): 
        '''
        POSTS 2 pre-set intents to the REST server and compares the REST server output to expected flows. 
        '''
        import time
        import requests
        import json
        import re
        main.case("Testing Rest Status") 

        #----------------------

        main.log.report("Starting Rest API Only Test")
        main.log.report("Rest IP used: " + main.params['RestIP'])
        restcall1 = "http://"+ main.params['RESTCALL']['restIP1'] + ":" + main.params['RESTCALL']['restPort'] + main.params['RESTCALL']['restURL'] 
        restcall2 = "http://"+ main.params['RESTCALL']['restIP1'] + ":" + main.params['RESTCALL']['restPort'] + main.params['RESTCALL']['restURL2']
        restcall3 = "http://"+ main.params['RESTCALL']['restIP1'] + ":" + main.params['RESTCALL']['restPort'] + main.params['RESTCALL']['restURL3']
        restcall4 = "http://"+ main.params['RESTCALL']['restIP1'] + ":" + main.params['RESTCALL']['restPort'] + main.params['RESTCALL']['restURL4']

        main.log.report("Rest Calls used: " + restcall1)
        main.log.report("Rest Calls used: " + restcall2)
        main.log.report("Rest Calls used: " + restcall3)
        main.log.report("Rest Calls used: " + restcall4)

        url = main.params['RESTTEST']['url']
        #headers = main.params['RESTTEST']['head']
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        expSrcMac = main.params['RESTTEST']['srcMac']
        expDstMac = main.params['RESTTEST']['dstMac']
        expSrcSwitch = main.params['RESTTEST']['srcSwitch']
        expDstSwitch = main.params['RESTTEST']['dstSwitch']
        srcPort = main.params['RESTTEST']['srcPort']
        dstPort = main.params['RESTTEST']['dstPort']
        intID = int(main.params['RESTTEST']['intID'])

        intent = [{'intent_id': '%d' %(intID),'intent_type':'shortest_intent_type','intent_op':'add','srcSwitch':expSrcSwitch,'srcPort':int(srcPort),'srcMac':expSrcMac,'dstSwitch':expDstSwitch,'dstPort':int(dstPort),'dstMac':expDstMac}]
        r = requests.post(url, data=json.dumps(intent, sort_keys=True), headers = headers)

        intent = [{'intent_id': '%d' %(intID+10),'intent_type':'shortest_intent_type','intent_op':'add','srcSwitch':expDstSwitch,'srcPort':int(dstPort),'srcMac':expDstMac,'dstSwitch':expSrcSwitch,'dstPort':int(srcPort),'dstMac':expSrcMac}]
        r = requests.post(url, data=json.dumps(intent, sort_keys=True), headers = headers)

        count = 0
        main.step("Getting JSON...")
        #r1 = main.ONOS.get_json_string(restcall1, expSrcSwitch, expDstSwitch, expSrcMac, expDstMac, srcPort, dstPort, intID)
        r1 = main.ONOS.get_json(restcall1)
        if re.search(expSrcSwitch, str(r1)) and re.search(expDstSwitch, str(r1)):
            main.log.report("Restcall: "+restcall1)
            main.log.report("Expected SrcSwitch "+expSrcSwitch+" found")
            main.log.report("Expected DstSwitch "+expDstSwitch+" found")
            count = count+1
        #r2 = main.ONOS.get_json_string(restcall2, expSrcSwitch, expDstSwitch, expSrcMac, expDstMac, srcPort, dstPort, intID) 
        r2 = main.ONOS.get_json(restcall2)
        if re.search("u\'srcMac\': u\'"+expSrcMac+"\'", str(r2)) and re.search("u\'dstMac\': u\'"+expDstMac+"\'", str(r2)):
            main.log.report("Restcall: "+restcall2)
            main.log.report("Expected SrcMac "+expSrcMac+" found")
            main.log.report("Expected DstMac "+expDstMac+" found")
            if re.search("u\'srcSwitchDpid\': u\'"+expSrcSwitch+"\'", str(r2)) and re.search("u\'dstSwitchDpid\': u\'"+expDstSwitch+"\'", str(r2)):
                main.log.report("Expected SrcSwitch "+expSrcSwitch+" found")
                main.log.report("Expected DstSwitch "+expDstSwitch+" found")
                if re.search("u\'srcPortNumber\': u\'"+srcPort+"\'", str(r2)) and re.search("u\'dstPortNumber\': u\'"+dstPort+"\'", str(r2)):
                    main.log.report("Expected SrcPort "+srcPort+" found")
                    main.log.report("Expected DstPort "+dstPort+" found")
                    count = count+1
                else:
                    main.log.report("Expected SrcPort "+srcPort+" NOT found")
                    main.log.report("Expected DstPort "+dstPort+" NOT found")
            else:
                main.log.report("Expected SrcSwitch "+expSrcSwitch+" NOT found")
                main.log.report("Expected DstSwitch "+expDstSwitch+" NOT found")
        else:
            main.log.report("Expected SrcMac "+expSrcMac+" NOT found")
            main.log.report("Expected DstMac "+expDstMac+" NOT found")
        if count != 2:
            main.log.report("Actual data: "+str(r2)) 
 
        #r3 = main.ONOS.get_json_string(restcall3, expSrcSwitch, expDstSwitch, expSrcMac, expDstMac, srcPort, dstPort, intID)
        r3 = main.ONOS.get_json(restcall3)
        if re.search("", str(r3)):
            main.log.report("Restcall: "+restcall3)
            count = count+1
  
        #r4 = main.ONOS.get_json_string(restcall4, expSrcSwitch, expDstSwitch, expSrcMac, expDstMac, srcPort, dstPort, intID)
        r4 = main.ONOS.get_json(restcall4)
        if re.search(expSrcSwitch, str(r4)) and re.search(expDstSwitch, str(r4)):
            main.log.report("Restcall: "+restcall4)
            main.log.report("Expected SrcSwitch: "+expSrcSwitch+" found")
            main.log.report("Expected DstSwitch: "+expDstSwitch+" found")
            count = count+1
        else:
            main.log.report("Expected SrcSwitch: "+expSrcSwitch+" NOT found")
            main.log.report("Expected DstSwitch: "+expDstSwitch+" NOT found")

        utilities.assert_equals(expect=4,actual=count,onpass="REST API test passed!",onfail="REST API test failed...")
 
