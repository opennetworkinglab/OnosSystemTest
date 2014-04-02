
class OnosSanity8nodes :

    def __init__(self) :
        self.default = ''

#**********************************************************************************************************************************************************************************************
#Test startup
#Tests the startup of Zookeeper1, Cassandra1, and ONOS1 to be certain that all started up successfully
    def CASE1(self,main) :  #Check to be sure ZK, Cass, and ONOS are up, then get ONOS version
        main.log.report("Startup check Zookeeper1, Cassandra1, and ONOS1 connections")
        import time
        main.Zookeeper1.start()
        main.Zookeeper2.start()
        main.Zookeeper3.start()
        main.Zookeeper4.start()
        main.Zookeeper5.start()
        main.Zookeeper6.start()
        main.Zookeeper7.start()
        main.Zookeeper8.start()
        main.case("Checking if the startup was clean...") 
        main.step("Testing startup Zookeeper")   
        data =  main.Zookeeper1.isup()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Zookeeper is up!",onfail="Zookeeper is down...")
        main.step("Testing startup Cassandra")   
        data =  main.Cassandra1.isup()
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
        main.log.report("\n\n\t\t\t\t ONOS VERSION")
        main.ONOS1.get_version()
        main.log.info("\n\n")
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
                main.Mininet1.assign_sw_controller(sw="s"+str(j),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
                time.sleep(1)
                main.Mininet1.assign_sw_controller(sw="s"+str(j),count=8,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'],ip5=main.params['CTRL']['ip5'],port5=main.params['CTRL']['port5'],ip6=main.params['CTRL']['ip6'],port6=main.params['CTRL']['port6'],ip7=main.params['CTRL']['ip7'],port7=main.params['CTRL']['port7'],ip8=main.params['CTRL']['ip8'],port8=main.params['CTRL']['port8'])
                time.sleep(1)
            elif i >= 3 and i < 5:
                j=i+1
                main.Mininet1.assign_sw_controller(sw="s"+str(j),ip1=main.params['CTRL']['ip2'],port1=main.params['CTRL']['port2'])
                time.sleep(1)
                main.Mininet1.assign_sw_controller(sw="s"+str(j),count=8,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'],ip5=main.params['CTRL']['ip5'],port5=main.params['CTRL']['port5'],ip6=main.params['CTRL']['ip6'],port6=main.params['CTRL']['port6'],ip7=main.params['CTRL']['ip7'],port7=main.params['CTRL']['port7'],ip8=main.params['CTRL']['ip8'],port8=main.params['CTRL']['port8'])
                time.sleep(1)
            elif i >= 5 and i < 15:
                j=i+1
                main.Mininet1.assign_sw_controller(sw="s"+str(j),ip1=main.params['CTRL']['ip3'],port1=main.params['CTRL']['port3'])
                time.sleep(1)
                main.Mininet1.assign_sw_controller(sw="s"+str(j),count=8,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'],ip5=main.params['CTRL']['ip5'],port5=main.params['CTRL']['port5'],ip6=main.params['CTRL']['ip6'],port6=main.params['CTRL']['port6'],ip7=main.params['CTRL']['ip7'],port7=main.params['CTRL']['port7'],ip8=main.params['CTRL']['ip8'],port8=main.params['CTRL']['port8'])
                time.sleep(1)
            else:
                j=i+16
                main.Mininet1.assign_sw_controller(sw="s"+str(j),ip1=main.params['CTRL']['ip4'],port1=main.params['CTRL']['port4'])
                time.sleep(1)
                main.Mininet1.assign_sw_controller(sw="s"+str(j),count=8,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'],ip5=main.params['CTRL']['ip5'],port5=main.params['CTRL']['port5'],ip6=main.params['CTRL']['ip6'],port6=main.params['CTRL']['port6'],ip7=main.params['CTRL']['ip7'],port7=main.params['CTRL']['port7'],ip8=main.params['CTRL']['ip8'],port8=main.params['CTRL']['port8'])
                time.sleep(1)
        main.Mininet1.get_sw_controller("s1")       
 
# **********************************************************************************************************************************************************************************************
#Add Flows
#Deletes any remnant flows from any previous test, add flows from the file labeled <FLOWDEF>, then runs the check flow test
#NOTE: THE FLOWDEF FILE MUST BE PRESENT ON TESTON VM!!! TestON will copy the file from its home machine into /tmp/flowtmp on the machine the ONOS instance is present on

    def CASE3(self,main) :    #Delete any remnant flows, then add flows, and time how long it takes flow tables to update
        main.log.report("Delete any flows from previous tests, then add flows from FLOWDEF file, then wait for switch flow tables to update")
        import time
        main.case("Taking care of these flows!") 
        main.step("Cleaning out any leftover flows...")
        main.ONOS1.delete_flow("all")
        time.sleep(5)
        strtTime = time.time()
        main.ONOS1.add_flow(main.params['FLOWDEF'])
        main.case("Checking flows")
        tmp = main.FALSE
        count = 1
        main.log.info("Wait for flows to settle, then check")
        while tmp == main.FALSE:
            main.step("Waiting")
            time.sleep(10)
            main.step("Checking")
            tmp = main.ONOS1.check_flow()
            if tmp == main.FALSE and count < 6:
                count = count + 1
                main.log.report("Flow failed, waiting 10 seconds then making attempt number "+str(count))
            elif tmp == main.FALSE and count == 6:
                result = main.FALSE
                break
            else:
                result = main.TRUE
                break
        endTime = time.time()
        if result == main.TRUE:
            main.log.report("\n\t\t\t\tTime to add flows: "+str(round(endTime-strtTime,2))+" seconds")
        else:
            main.log.report("\tFlows failed check")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Flow check PASS",onfail="Flow check FAIL")

#**********************************************************************************************************************************************************************************************
#This test case removes Controllers 2,3, and 4 then performs a ping test.
#The assign controller is used because the ovs-vsctl module deletes all current controllers when a new controller is assigned.
#The ping test performs single pings on hosts from opposite sides of the topology. If one ping fails, the test waits 10 seconds before trying again.
#If the ping test fails 6 times, then the test case will return false

    def CASE4(self,main) :
        main.log.report("Remove ONOS 2,3,4 then ping until all hosts are reachable or fail after 6 attempts")
        import time
        for i in range(25):
            if i < 15:
                j=i+1
                main.Mininet1.assign_sw_controller(sw="s"+str(j),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])  #Assigning a single controller removes all other controllers
                time.sleep(1)
            else:
                j=i+16
                main.Mininet1.assign_sw_controller(sw="s"+str(j),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
                time.sleep(1)
        strtTime = time.time()
        count = 1
        i = 6
        while i < 16 :
            main.log.info("\n\t\t\t\th"+str(i)+" IS PINGING h"+str(i+25) )
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+25))
            if ping == main.FALSE and count < 6:
                count = count + 1
                i = 6
                main.log.info("Ping failed, making attempt number "+str(count)+" in 15 seconds")
                time.sleep(15)
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
                main.Mininet1.assign_sw_controller(sw="s"+str(j),count=8,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'],ip5=main.params['CTRL']['ip5'],port5=main.params['CTRL']['port5'],ip6=main.params['CTRL']['ip6'],port6=main.params['CTRL']['port6'],ip7=main.params['CTRL']['ip7'],port7=main.params['CTRL']['port7'],ip8=main.params['CTRL']['ip8'],port8=main.params['CTRL']['port8'])
                time.sleep(1)
            else:
                j=i+16
                main.Mininet1.assign_sw_controller(sw="s"+str(j),count=8,ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'],ip5=main.params['CTRL']['ip5'],port5=main.params['CTRL']['port5'],ip6=main.params['CTRL']['ip6'],port6=main.params['CTRL']['port6'],ip7=main.params['CTRL']['ip7'],port7=main.params['CTRL']['port7'],ip8=main.params['CTRL']['ip8'],port8=main.params['CTRL']['port8'])
                time.sleep(1)
        strtTime = time.time()
        count = 1
        i = 6
        while i < 16 :
            main.log.info("\n\t\t\t\th"+str(i)+" IS PINGING h"+str(i+25) )
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+25))
            if ping == main.FALSE and count < 6:
                count = count + 1
                i = 6
                main.log.info("Ping failed, making attempt number "+str(count)+" in 15 seconds")
                time.sleep(15)
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
        main.log.report("Bring Link between s1 and s2 down, then ping until all hosts are reachable or fail after 6 attempts")
        import time
        main.case("Bringing Link down... ")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        time.sleep(3)
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Link DOWN!",onfail="Link not brought down...")
        strtTime = time.time()
        count = 1
        i = 6
        while i < 16 :
            main.log.info("\n\t\t\t\th"+str(i)+" IS PINGING h"+str(i+25) )
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+25))
            if ping == main.FALSE and count < 6:
                count = count + 1
                main.log.info("Ping failed, making attempt number "+str(count)+" in 15 seconds")
                i = 6
                time.sleep(15)
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
#Brings the link that Case 6 took down  back up, then runs a ping test to view reroute time

    def CASE7(self,main) :
        main.log.report("Bring Link between S1 and S2 up, then ping until all hosts are reachable or fail after 6 attempts")
        import time
        main.case("Bringing Link back up... ")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        time.sleep(3)
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Link DOWN!",onfail="Link not brought down...")
        strtTime = time.time()
        count = 1
        i = 6
        while i < 16 :
            main.log.info("\n\t\t\t\th"+str(i)+" IS PINGING h"+str(i+25) )
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+25))
            if ping == main.FALSE and count < 6:
                count = count + 1
                main.log.info("Ping failed, making attempt number "+str(count)+" in 15 seconds")
                i = 6
                time.sleep(15)
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
            main.log.report("\tPING TESTS FAILED")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="NO PACKET LOSS, HOST IS REACHABLE",onfail="PACKET LOST, HOST IS NOT REACHABLE")

