
class RCOnosSanity4nodes_cass :

    def __init__(self) :
        self.default = ''

#**********************************************************************************************************************************************************************************************
#Test startup
#Tests the startup of Zookeeper1, Cassandra1, and ONOS1 to be certain that all started up successfully
    def CASE1(self,main) :  #Check to be sure ZK, Cass, and ONOS are up, then get ONOS version
        import time
        main.log.report("Pulling latest code from github to all nodes")
        main.ONOS1.git_pull()
        main.ONOS2.git_pull()
        main.ONOS3.git_pull()
        main.ONOS4.git_pull()
        main.Cassandra1.start()
        main.Cassandra2.start()
        main.Cassandra3.start()
        main.Cassandra4.start()
        time.sleep(20)
        main.ONOS1.drop_keyspace()
        main.ONOS1.start()
        time.sleep(10)
        main.ONOS2.start()
        main.ONOS3.start()
        main.ONOS4.start()
        main.ONOS1.start_rest()
        time.sleep(5)
        main.ONOS1.get_version()
        main.log.report("Startup check Zookeeper1, Cassandra1, and ONOS1 connections")
        main.case("Checking if the startup was clean...")
        main.step("Testing startup Zookeeper")   
        data =  main.Zookeeper1.isup()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Zookeeper is up!",onfail="Zookeeper is down...")
        main.step("Testing startup Cassandra")   
        data =  main.Cassandra1.isup() 
        if data == main.FALSE:
            main.Cassandra1.stop()
            main.Cassandra2.stop()
            main.Cassandra3.stop()
            main.Cassandra4.stop()

            time.sleep(5)
 
            main.Cassandra1.start()
            main.Cassandra2.start()
            main.Cassandra3.start()
            main.Cassandra4.start()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Cassandra is up!",onfail="Cassandra is down...")
        main.step("Testing startup ONOS")   
        data = main.ONOS1.isup()
        if data == main.FALSE: 
            main.log.report("Something is funny... restarting ONOS")
            main.ONOS1.stop()
            time.sleep(3)
            main.ONOS1.start()
            time.sleep(5) 
            data = main.ONOS1.isup()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="ONOS is up and running!",onfail="ONOS didn't start...")
           
#**********************************************************************************************************************************************************************************************
#Assign Controllers
#This test first checks the ip of a mininet host, to be certain that the mininet exists(Host is defined in Params as <CASE1><destination>).
#Then the program assignes each ONOS instance a single controller to a switch(To be the initial master), then assigns all controllers.
#NOTE: The reason why all four controllers are assigned although one was already assigned as the master is due to the 'ovs-vsctl set-controller' command erases all present controllers if
#      the controllers already assigned to the switch are not specified.

    def CASE2(self,main) :    #Make sure mininet exists, then assign controllers to switches
        import time
        main.log.report("Check if mininet started properly, then assign controllers ONOS 1,2,3 and 4")
        main.case("Checking if one MN host exists")
        main.step("Host IP Checking using checkIP")
        result = main.Mininet1.checkIP(main.params['CASE1']['destination'])
        main.step("Verifying the result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Host IP address configured",onfail="Host IP address not configured")
        main.step("assigning ONOS controllers to switches")
        for i in range(25): 
            if i < 3:
                j=i+1
                main.Mininet1.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
                time.sleep(1)
                main.Mininet1.assign_sw_controller(sw=str(j),count=4,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'])
            elif i >= 3 and i < 5:
                j=i+1
                main.Mininet1.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip2'],port1=main.params['CTRL']['port2'])
                time.sleep(1)
                main.Mininet1.assign_sw_controller(sw=str(j),count=4,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'])
            elif i >= 5 and i < 15:
                j=i+1
                main.Mininet1.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip3'],port1=main.params['CTRL']['port3'])
                time.sleep(1)
                main.Mininet1.assign_sw_controller(sw=str(j),count=4,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'])
            else:
                j=i+16
                main.Mininet1.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip4'],port1=main.params['CTRL']['port4'])
                time.sleep(1)
                main.Mininet1.assign_sw_controller(sw=str(j),count=4,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'])
        main.Mininet1.get_sw_controller("s1")       

        for i in range(9):
            if result == main.FALSE:
                time.sleep(3)
                result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
            else:
                break 
 
# **********************************************************************************************************************************************************************************************
#Add Flows
#Deletes any remnant flows from any previous test, add flows from the file labeled <FLOWDEF>, then runs the check flow test
#NOTE: THE FLOWDEF FILE MUST BE PRESENT ON TESTON VM!!! TestON will copy the file from its home machine into /tmp/flowtmp on the machine the ONOS instance is present on

    def CASE3(self,main) :    #Delete any remnant flows, then add flows, and time how long it takes flow tables to update
        main.log.report("Delete any flows from previous tests, then add flows from FLOWDEF file, then wait for switch flow tables to update")
        import time

        result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        for i in range(9):
            if result == main.FALSE:
                time.sleep(3)
                result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
            else:
                break

        main.case("Taking care of these flows!") 
        main.step("Cleaning out any leftover flows...")
        main.ONOS1.delete_flow("all")
        time.sleep(5)
        strtTime = time.time()
        main.ONOS1.add_flow(main.params['FLOWDEF'])
        main.case("Checking flows")
        tmp = main.FALSE
        count = 1
        main.log.info("Wait for flows to be pushed to the switches, then check")
        while tmp == main.FALSE:
            main.step("Waiting")
            time.sleep(5)
            main.step("Checking")
            tmp = main.ONOS1.check_flow()
            if tmp == main.FALSE and count < 6:
                count = count + 1
                main.log.report("Flow failed, waiting 10 seconds then making attempt number "+str(count))
            elif tmp == main.FALSE and count == 6:
                result1 = main.FALSE
                break
            else:
                result1 = main.TRUE
                break
        endTime = time.time()
        if result1 == main.TRUE:
            main.log.report("\n\t\t\t\tTime to add flows: "+str(round(endTime-strtTime,2))+" seconds")
        else:
            main.log.report("\tFlows failed check")
        
        count = 1
        i = 6
        while i < 16 :
            main.log.info("\n\t\t\t\th"+str(i)+" IS PINGING h"+str(i+25) )
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+25))
            if ping == main.FALSE and count < 3:
                count = count + 1
                i = 6
                main.log.info("Ping failed, making attempt number "+str(count)+" in 10 seconds")
                time.sleep(10)
            elif ping == main.FALSE and count ==3:
                main.log.error("Ping test failed")
                i = 17
                result2 = main.FALSE
            elif ping == main.TRUE:
                i = i + 1
                result2 = main.TRUE
        if result2 == main.TRUE:
            main.log.info("Flows successfully added")
        else:
            main.log.report("\tPING TEST FAIL")

        main.step("Verifying the result")
        utilities.assert_equals(expect=main.TRUE,actual=result1 and result2,onpass="Flow check PASS",onfail="Flow check FAIL")

#**********************************************************************************************************************************************************************************************
#This test case removes Controllers 2,3, and 4 then performs a ping test.
#The assign controller is used because the ovs-vsctl module deletes all current controllers when a new controller is assigned.
#The ping test performs single pings on hosts from opposite sides of the topology. If one ping fails, the test waits 5 seconds before trying again.
#If the ping test fails 6 times, then the test case will return false

    def CASE4(self,main) :
        main.log.report("Remove ONOS 2,3,4 then ping until all hosts are reachable or fail after 6 attempts")
        import time
        for i in range(25):
            if i < 15:
                j=i+1
                main.Mininet1.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])  #Assigning a single controller removes all other controllers
            else:
                j=i+16
                main.Mininet1.assign_sw_controller(sw=str(j),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
      
        strtTime = time.time() 
        result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        for i in range(9):
            if result == main.FALSE:
                time.sleep(3)
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
                main.log.info("Ping failed, making attempt number "+str(count)+" in 5 seconds")
                time.sleep(5)
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

# **********************************************************************************************************************************************************************************************
#This test case restores the controllers removed by Case 4 then performs a ping test.

    def CASE5(self,main) :
        main.log.report("Restore ONOS 2,3,4 then ping until all hosts are reachable or fail after 6 attempts")
        import time
        for i in range(25):
            if i < 15:
                j=i+1
                main.Mininet1.assign_sw_controller(sw=str(j),count=4,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'])
            else:
                j=i+16
                main.Mininet1.assign_sw_controller(sw=str(j),count=4,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'])
      
        strtTime = time.time() 
        result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        for i in range(9):
            if result == main.FALSE:
                time.sleep(3)
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
                main.log.info("Ping failed, making attempt number "+str(count)+" in 5 seconds")
                time.sleep(5)
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

# **********************************************************************************************************************************************************************************************
#Brings a link that all flows pass through in the mininet down, then runs a ping test to view reroute time

    def CASE6(self,main) :
        main.log.report("Bring Link between s1 and s2 down, then ping until all hosts are reachable or fail after 10 attempts")
        import time
        main.case("Bringing Link down... ")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Link DOWN!",onfail="Link not brought down...")
       
        strtTime = time.time() 
        result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],str(int(main.params['NR_Links'])-2))
        for i in range(9):
            if result == main.FALSE:
                time.sleep(3)
                result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],str(int(main.params['NR_Links'])-2))
            else:
                break

        count = 1
        i = 6
        while i < 16 :
            main.log.info("\n\t\t\t\th"+str(i)+" IS PINGING h"+str(i+25) )
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+25))
            if ping == main.FALSE and count < 10:
                count = count + 1
                main.log.info("Ping failed, making attempt number "+str(count)+" in 5 seconds")
                i = 6
                time.sleep(5)
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

# **********************************************************************************************************************************************************************************************
#Brings the link that Case 6 took down  back up, then runs a ping test to view reroute time

    def CASE7(self,main) :
        main.log.report("Bring Link between s1 and s2 up, then ping until all hosts are reachable or fail after 10 attempts")
        import time
        main.case("Bringing Link up... ")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Link UP!",onfail="Link not brought up...")
      
        strtTime = time.time() 
        result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        for i in range(9):
            if result == main.FALSE:
                time.sleep(3)
                result = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
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
                main.log.info("Ping failed, making attempt number "+str(count)+" in 5 seconds")
                i = 6
                time.sleep(5)
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


# ******************************************************************************************************************************************************************
# Test Device Discovery function by yanking s6:s6-eth0 interface and re-plug it into a switch

    def CASE21(self,main) :
        import json
        from drivers.common.api.onosrestapidriver import *
        main.log.report("Test device discovery function, by attach/detach/move host h1 from s1->s6->s1.")
        main.log.report("Check initially hostMAC exist on the mininet...")
        host = main.params['YANK']['hostname']
        mac = main.params['YANK']['hostmac']
        RestIP1 = main.params['RESTCALL']['restIP1']
        RestIP2 = main.params['RESTCALL']['restIP2']
        RestPort = main.params['RESTCALL']['restPort']
        url = main.params['RESTCALL']['restURL']
        #print "host=" + host + ";  RestIP=" + RestIP1 + ";  RestPort=" + str(RestPort)
        
        main.log.info("\n\t\t\t\t ping issue one ping from" + str(host) + "to generate arp to switch. Ping result is not important" )
        ping = main.Mininet1.pingHost(src = str(host),target = "10.0.0.254")
        restcall = OnosRestApiDriver()
        Reststatus, Hoststatus = restcall.find_host(RestIP1,RestPort,url,mac)
        try:
            attachedSW = Hoststatus[0]['attachmentPoint'][0]['switchDPID']
            ip_found = Hoststatus[0]['ipv4'][0]
        except:
            Reststatus = 0

        if Reststatus == 1:
            main.log.report("\tFound host " + host + " attached to switchDPID = " + attachedSW)
            if ip_found != None:
                main.log.report("\t IP discovered is ip_found ( " + ip_found + " ).")
                result = main.TRUE
            else:
                main.log.report("\t Found host attached to switch, but no IP address discovered.")
                result = main.FALSE
        else:
            main.log.report("\t Host " + host + " with MAC:" + str(mac) + " does not exist. FAILED")
            result = main.FALSE

        ##### Step to yank out "s1-eth1" from s1, which is on autoONOS1 #####

        main.log.report("Yank out s1-eth1")
        main.case("Yankout s6-eth1 (link to h1) from s1")
        result = main.Mininet1.yank(SW=main.params['YANK']['sw1'],INTF=main.params['YANK']['intf'])
        time.sleep(3)
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Yank command suceeded",onfail="Yank command failed...")
        ping = main.Mininet1.pingHost(src = str(host),target = "10.0.0.254")
        Reststatus, Hoststatus = restcall.find_host(RestIP1,RestPort,url,mac)
        try:
            attachedSW = Hoststatus[0]['attachmentPoint'][0]['switchDPID']
        except:
            Reststatus = 0
        if Reststatus == 0:
            main.log.report("Attempt to yank out s1-eth1 from s1 sucessfully")
            result = main.TRUE
        else:
            main.log.report("Attempt to yank out s1-eht1 from s1 failed.")
            result = main.FALSE
        
        ##### Step to plug "s1-eth1" to s6, which is on autoONOS3  ######
        main.log.report("Plug s1-eth1 into s6")
        main.case("Plug s1-eth1 to s6")
        result = main.Mininet1.plug(SW=main.params['PLUG']['sw6'],INTF=main.params['PLUG']['intf'])
        time.sleep(3)
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Plug command suceeded",onfail="Plug command failed...")
        ping = main.Mininet1.pingHost(src = str(host),target = "10.0.0.254")
        Reststatus, Hoststatus = restcall.find_host(RestIP2,RestPort,url,mac)
        try:
            attachedSW = Hoststatus[0]['attachmentPoint'][0]['switchDPID']
            ip_found = Hoststatus[0]['ipv4'][0]
        except:
            Reststatus = 0
        if Reststatus == 0:
            main.log.report("Attempt to plug s1-eth1 to s6 FAILED")
            result = main.FALSE
        elif attachedSW == "00:00:00:00:00:00:00:06":
            main.log.report("Attempt to plug s1-eht1 to s6 succeded.")
            if ip_found != None:
                main.log.report("\t IP discovered is ip_found ( " + ip_found + " ).")
                result = main.TRUE
            else:
                main.log.report("\t Found host attached to switch, but no IP address discovered.")
                result = main.FALSE
        else:
            main.log.report( "FAILED to attach s1-eth1 to s6 correctly!")
            result = main.FALSE

        ###### Step to put interface "s1-eth1" back to s1"#####
        main.log.report("Move s1-eth1 back on to s1")
        main.case("Move s1-eth1 back to s1")
        result = main.Mininet1.yank(SW=main.params['YANK']['sw6'],INTF=main.params['YANK']['intf'])
        time.sleep(3)
        retult = main.Mininet1.plug(SW=main.params['PLUG']['sw1'],INTF=main.params['PLUG']['intf'])
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Yank/Plug command suceeded",onfail="Yank/Plug command failed...")
        ping = main.Mininet1.pingHost(src = str(host),target = "10.0.0.254")
        Reststatus, Hoststatus = restcall.find_host(RestIP1,RestPort,url,mac)
        try:
            attachedSW = Hoststatus[0]['attachmentPoint'][0]['switchDPID']
            ip_found = Hoststatus[0]['ipv4'][0]
        except:
            Reststatus = 0
        if Reststatus == 0:
            main.log.report("Attempt to plug s1-eth1 back to s1 FAILED")
            result = main.FALSE
        elif attachedSW == "00:00:00:00:00:00:00:01":
            main.log.report("Attempt to plug s1-eht1 back to s1 succeded.")
            if ip_found != None:
                main.log.report("\t IP discovered is ip_found ( " + ip_found + " ).")
                result = main.TRUE
            else:
                main.log.report("\t Found host attached to switch, but no IP address discovered.")
                result = main.FALSE
        else:
            main.log.report( "FAIL to attach s1-eth1 to s1 correctly!")
            result = main.FALSE

        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="DEVICE DISCOVERY TEST PASSED PLUG/UNPLUG/MOVE TEST",onfail="DEVICE DISCOVERY TEST FAILED")




