

class JamesTest :

    def __init__(self) :
        self.default = ''




#***************************************************************************************************************


    def CASE1(self,main) : 
        main.case("\nStart-Up of Zookeeper, RAMCloud, ONOS, and Mininet")
        import time 
        main.step("\n**********************Git pulls and Rebuilds******************")
        for i in range(2):
            main.log.report("ONOS1 Git Pull")
            uptodate = main.ONOS1.git_pull()
            ver1 = main.ONOS1.get_version()
            main.log.report("ONOS2 Git Pull")
            main.ONOS2.git_pull()
            main.log.report("ONOS3 Git Pull")
            main.ONOS3.git_pull()
            main.log.report("ONOS4 Git Pull")
            main.ONOS4.git_pull()
            ver2 = main.ONOS4.get_version()
            if ver1==ver2:
                break
            elif i==1:
                main.log.report("Versions differ. Doing Git pulls from ONOS1")
                main.ONOS2.git_pull("ONOS1 master")
                main.ONOS3.git_pull("ONOS1 master")
                main.ONOS4.git_pull("ONOS1 master")
        if uptodate==0:
            main.log.report("Building ONOS1")
            main.ONOS1.git_compile()
            main.log.report("Building ONOS2")
            main.ONOS2.git_compile()
            main.log.report("Building ONOS3")
            main.ONOS3.git_compile()
            main.log.report("Building ONOS4")
            main.ONOS4.git_compile()
        

        main.step("\n********************Testing Zookeeper Startup**************")
        data1 = main.Zookeeper1.isup()
        utilities.assert_equals(expect=main.TRUE,actual=data1,onpass="Zookeeper is up!",onfail="Zookeeper is down...")
        if data1==main.FALSE:
            main.log.report("Zookeeper is Down, Exiting the Test!")
            main.cleanup()
            main.exit()

        main.step("\n********************Starting Up RAMCloud*********************")
        main.RamCloud1.start_coor()
        time.sleep(2)
        main.RamCloud1.start_serv()
        main.RamCloud2.start_serv()
        main.RamCloud3.start_serv()
        main.RamCloud4.start_serv()
        time.sleep(5)
        
        main.step("\n********************Testing RAMCloud Startup**************")
        data2 = main.RamCloud1.status_serv()
        print(data2)
        for i in range(3):
            if data2 == main.FALSE:
                main.RamCloud1.stop_serv()
                main.RamCloud2.stop_serv()
                main.RamCloud3.stop_serv()
                main.RamCloud4.stop_serv()
                main.RamCloud1.stop_coor()
                main.RamCloud1.start_coor()
                time.sleep(2)
                main.RamCloud1.start_serv()
                main.RamCloud2.start_serv()
                main.RamCloud3.start_serv()
                main.RamCloud4.start_serv()
                time.sleep(5)
                data2 = main.RamCloud1.status_serv()
            else:
                break
        utilities.assert_equals(expect=main.TRUE,actual=data2,onpass="RAMCloud is up!",onfail="RAMCloud is down...")
        if data2==main.FALSE:
            main.log.report("RAMCloud is Down, Exiting the Test!")
            main.cleanup()
            main.exit()

        main.step("\n************************Starting Up ONOS and Rest*****************")
        main.ONOS1.start()
        time.sleep(10)
        main.ONOS2.start()
        main.ONOS3.start()
        main.ONOS4.start()
        main.ONOS1.start_rest()
        time.sleep(5)
        test = main.ONOS1.rest_status()
        for i in range(3):
            if test == main.FALSE:
                main.ONOS1.start_rest()
                time.sleep(5)
                test = main.ONOS1.rest_status()
            else:
                break
        
        main.step("\n************************Testing ONOS Startup***************")
        data3 = main.ONOS1.isup()
        for i in range(3):
            if data3 == main.FALSE:
                main.log.report("ONOS did not start, restarting ONOS")
                main.ONOS1.stop()
                main.ONOS2.stop()
                main.ONOS3.stop()
                main.ONOS4.stop()
                time.sleep(2)
                main.ONOS1.start()
                time.sleep(10)
                main.ONOS2.start()
                main.ONOS3.start()
                main.ONOS4.start()
                data3 = main.ONOS1.isup()
            else:
                break
        utilities.assert_equals(expect=main.TRUE,actual=data3,onpass="ONOS is up!",onfail="ONOS is down...")
        if data3==main.FALSE:
            main.log.report("ONOS did not START!! Exiting the Test")
            main.cleanup()
            main.exit() 

        main.step("\n****************************Testing Mininet Startup***************")
        data4 = main.Mininet1.checkIP(main.params['CASE1']['destination'])
        utilities.assert_equals(expect=main.TRUE,actual=data4,onpass="Host IP address configured",onfail="Host IP address not configured")

        finalAssert = data1 and data2 and data3
        utilities.assert_equals(expect=main.TRUE,actual=finalAssert,onpass="Good to Go!",onfail="NO GO FOR LAUNCH")

#*****************************************************************************************

    def CASE2(self,main) :
        import time
        main.case("\nAssign ONOS Controllers to Switches and run Initial Ping Test")
        main.step("\n**********************Assign initial master controller to switches**********************")
        for i in range(25):
            if i < 3:
                main.Mininet1.assign_sw_controller(sw=str(i+1),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
                time.sleep(1)
            elif i>=3 and i <5:
                main.Mininet1.assign_sw_controller(sw=str(i+1),ip1=main.params['CTRL']['ip2'],port1=main.params['CTRL']['port2'])
                time.sleep(1)
            elif i>=5 and i<15:
                main.Mininet1.assign_sw_controller(sw=str(i+1),ip1=main.params['CTRL']['ip3'],port1=main.params['CTRL']['port3'])
                time.sleep(1)
            else: 
                main.Mininet1.assign_sw_controller(sw=str(i+16),ip1=main.params['CTRL']['ip4'],port1=main.params['CTRL']['port4'])
                time.sleep(1)
        
        main.step("\n**********************Assign all ONOS instances to all Switches*************************")
        for i in range(25):
            if i < 15:
                main.Mininet1.assign_sw_controller(sw=str(i+1),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'])                
                time.sleep(1)
            else:
                main.Mininet1.assign_sw_controller(sw=str(i+16),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'],ip2=main.params['CTRL']['ip2'],port2=main.params['CTRL']['port2'],ip3=main.params['CTRL']['ip3'],port3=main.params['CTRL']['port3'],ip4=main.params['CTRL']['ip4'],port4=main.params['CTRL']['port4'])                
       

    def CASE3(self,main):
        main.case("\nPerforming Initial Ping Test")
        main.step("\n**********************Initial Ping Test***************")
        count = 1
        i = 6
        while i < 16:
            main.log.info("\n\t\t\th" + str(i) + " IS PINGING h" + str(i+25) )
            strtTime = time.time()
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+25))
            if ping == main.FALSE and count<6:
                count+=1
                i = 6
                main.log.info("Ping failed, making attempt number " + str(count)+" in 2 seconds")
                time.sleep(2)
            elif ping == main.FALSE and count==6:
                main.log.error("Ping test failed")
                i = 17
                result = main.FALSE
            elif ping == main.TRUE:
                i += 1
                result = main.TRUE
        endTime = time.time()
        if result == main.TRUE:
            main.log.report("\tTime to complete ping test: " + str(round(endTime-strtTime,2))+ " seconds")
        else:
            main.log.report("\tPING TEST FAILED!")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="NO PACKET LOSS, HOST IS REACHABLE",onfail="PACKET LOSS!!!! HOST IS NOT REACHABLE!!!!!!")



    def CASE4(self,main):
        main.case("\nWhat happens when 3 of the ONOS instances die?")
        main.step("\n********************Removing 3 ONOS instances****************************")
        main.ONOS2.stop()
        main.ONOS3.stop()
        main.ONOS4.stop()
        main.step("\n*******************Checking for the correct topology*********************")
        data1 = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        print("%s" % data1)
        for i in range(10):
            if data1 == main.FALSE:
                time.sleep(5)
                data1 = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
            else:
                break
        main.step("\n********************Running PING Test****************************")
        count = 1
        i = 6
        while i < 16:
            main.log.info("\n\t\t\tH" + str(i) + " is PINGING H" + str(i+25))
            strtTime = time.time()
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+25))
            if ping == main.FALSE and count<6:
                count+=1
                i = 6
                main.log.info("Ping failed, making attempt number " + str(count)+" in 2 seconds")
                time.sleep(2)
            elif ping == main.FALSE and count==6:
                main.log.error("Ping test failed")
                i = 17
                result2 = main.FALSE
            elif ping == main.TRUE:
                i += 1
                result2 = main.TRUE
        endTime = time.time()
        if result2 == main.TRUE:
            main.log.report("\tTime to complete ping test: " + str(round(endTime-strtTime,2))+ " seconds")
        else:
            main.log.report("\tPING TEST FAILED!")
        finalResult = data1 and result2
        utilities.assert_equals(expect=main.TRUE,actual=finalResult,onpass="NO PACKET LOSS, HOST IS REACHABLE",onfail="PACKET LOSS!!!! HOST IS NOT REACHABLE!!!!!!")
        time.sleep(5)


    def CASE5(self,main):
        main.case("\nRestart the 3 ONOS instances and run a PING test")
        main.step("\n************************Bringing Back up ONOS Instances*****************************")
        main.ONOS2.start()
        main.ONOS3.start()
        main.ONOS4.start()
        time.sleep(4)
        main.step("\n********************Running PING Test****************************")
        count = 1
        i = 6
        while i < 16:
            main.log.info("\n\t\t\tH" + str(i) + " is PINGING H" + str(i+25))
            strtTime = time.time()
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+25))
            if ping == main.FALSE and count<6:
                count+=1
                i = 6
                main.log.info("Ping failed, making attempt number " + str(count)+" in 2 seconds")
                time.sleep(2)
            elif ping == main.FALSE and count==6:
                main.log.error("Ping test failed")
                i = 17
                result2 = main.FALSE
            elif ping == main.TRUE:
                i += 1
                result2 = main.TRUE
        endTime = time.time()
        if result2 == main.TRUE:
            main.log.report("\tTime to complete ping test: " + str(round(endTime-strtTime,2))+ " seconds")
        else:
            main.log.report("\tPING TEST FAILED!")
        finalResult = result2
        utilities.assert_equals(expect=main.TRUE,actual=finalResult,onpass="NO PACKET LOSS, HOST IS REACHABLE",onfail="PACKET LOSS!!!! HOST IS NOT REACHABLE!!!!!!")
        time.sleep(5)
       

    def CASE6(self,main):
        main.case("Bring links between S1 and S2 down, then ping untill all hosts are reachable or fail after 10 attempts")
        import time
        main.step("\n*****************Bringing Link DOWN!!!************************")
        data1 = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        utilities.assert_equals(expect=main.TRUE,actual=data1,onpass="Link Brought DOWN!",onfail="Link still up...")
        main.step("\n******************Waiting for Topology Convergence****************")
        strtTime = time.time()
        data2 = main.FALSE
        data2 = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],str(int(main.params['NR_Links'])-2))
        print("hello world")
        for i in range(2):
            if data2 == main.FALSE:
                time.sleep(5)
                data2 = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],str(int(main.params['NR_Links'])-2))
            else:
                break
        utilities.assert_equals(expect=main.TRUE,actual=data2,onpass="Topology Converged",onfail="Topology FAILED to Converge")
        main.case("\n*******************Ping Test***********************")
        count = 1
        i = 6
        while i < 16:
            main.log.info("\n\t\t\tH" + str(i) + " is PINGING H" + str(i+25))
            strtTime = time.time()
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+25))
            if ping == main.FALSE and count<6:
                count+=1
                i = 6
                main.log.info("Ping failed, making attempt number " + str(count)+" in 2 seconds")
                time.sleep(2)
            elif ping == main.FALSE and count==6:
                main.log.error("Ping test failed")
                i = 17
                data3 = main.FALSE
            elif ping == main.TRUE:
                i += 1
                data3 = main.TRUE
        endTime = time.time()
        if data3 == main.TRUE:
            main.log.report("\tTime to complete ping test: " + str(round(endTime-strtTime,2))+ " seconds")
        else:
            main.log.report("\tPING TEST FAILED!")
        utilities.assert_equals(expect=main.TRUE,actual=data3,onpass="Ping test PASSED!",onfail="Ping Test FAILED!!!!")
        finalResult = data1 and data2 and data3
        utilities.assert_equals(expect=main.TRUE,actual=finalResult,onpass="NO PACKET LOSS, HOST IS REACHABLE",onfail="PACKET LOSS!!!! HOST IS NOT REACHABLE!!!!!!")
        time.sleep(5)
       
    def CASE31(self,main) : 
        import time
        main.case("\nClear out flows, then add flows from FLOWDEF file")
        main.step("\n\n***************Cleaning out OLD flows!*************")
        main.ONOS1.delete_flow("all")
        main.step("\n\n***************Adding Flows from FLOWDEF File**********")
        strtTime = time.time()
        main.ONOS1.add_flow(main.params['FLOWDEF'])
        main.step("\n\n**************Checking Flows***********************")
        count = 1
        i = 6
        while i <16:
            main.log.info("\n\t\t\t\th" + str(i) + " IS PINGING h" + str(i+25))
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+25))
            if ping == main.FALSE and count < 9:
                count +=1
                i = 6
                main.log.info("Ping failed, making attempt number " + str(count) + " in 2 seconds")
                time.sleep(2)
            elif ping == main.FALSE and count == 9:
                main.log.error("Ping test failed")
                i = 17
                result = main.FALSE
            elif ping == main.TRUE:
                i = i+1
                result = main.TRUE
        endTime = time.time()
        if result == main.TRUE:
            main.log.report("\tTime to add flows: " + str(round(endTime-strtTime,2))+" seconds")
        else:
            main.log.report("\tFlows failed check")
        result2 = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        finalResult = result and result2
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Flows added and Checked!",onfail="Flows did not add properly")



    def CASE21(self,main) : 
        import json
        main.case("Test device discovery function by attaching, metaching, moving host1 from s1 -> s6 -> s1. Per mininet naming, when switching ports, the host attaches will still remain as 's1-eth1' throughout the entire test")
        main.step("\n\n******Checking that the initial host MAC/IP exists on the mininet******")
        host = main.params['YANK']['hostname']
        mac = main.params['YANK']['hostmac']
        hostip = main.params['YANK']['hostip']
        RestIP1 = main.params['RESTCALL']['restIP1']
        RestPort = main.params['RESTCALL']['restPort']
        url = main.params['RESTCALL']['restURL']
        t_topowait = 0
        t_restwait = 10
        main.log.report("Wait time from topo change to ping set to " + str(t_topowait))
        main.log.report("Wait time from ping to rest call set to " + str(t_restwait))
        time.sleep(t_topowait)
        main.log.info("\n\t\t\t\t Ping: Issue 1 ping from " + str(host) + " to generate arp to switch. Ping result is not important")
        ping = main.Mininet1.pingHost(src = str(host),target = "10.0.0.254")
        time.sleep(t_restwait)
        Reststatus, Swtich, Port, MAC = main.ONOS1.find_host(RestIP1,RestPort,url,hostip)
        main.log.report("Number of hosts with IP=10.0.0.1 found by ONOS is: " + str(Reststatus))
        if Reststatus ==1:
            main.log.report("\t PASSED - Found host IP = " + hostip + "; MAC = " + "".join(MAC)+"; attached to switchDPPID = " + "".join(Switch)+ "; at port = " + "".join(Port))
            result1 = main.TRUE
        elif Reststatus >1:
            main.log.report("\t FAILED - Host " + host + " with MAC:" + mac + " has " + str(Reststatus) + " duplicated IP addresses. FAILED")
            main.log.report("switches are: " + "; ".join(Switch))
            main.log.report("Ports are: " + "; ".join(Port))
            main.log.report("MACS are: " + "; ".join(MAC))
            result1 = main.FALSE
        else:
            main.log.report("\]t FAILED - Host " + host + " with MAC:" + mac + " does not exist. FAILED")
            result1 = main.FALSE

#*****************Step to yank out s1-eth1 from s1

        main.step("Yank out s1-eth1")
        main.log.report("Yankout s6-eth1 (link to h1) from s1")
        result = main.Mininet1.yank(SW=main.params['YANK']['sw1'],INTF=main.params['YANK']['intf'])
        time.sleep(t_topowait)
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Yank command suceeded",onfail="Yank command failed...")
       
        main.step("\n\n Ping: Issue 1 ping from " + str(host) + " to generate arp to switch. Ping result is not important")
        ping = main.Mininet1.pingHost(src = str(host),target = "10.0.0.254")
        time.sleep(t_restwait)
        Reststatus, Switch, Port, MAC = main.ONOS1.find_host(RestIP1,RestPort,url,hostip)
        main.log.report("Number of hosts with IP=10.0.0.1 found by ONOS is: " + str(Reststatus))
        if Reststatus ==1:
            main.log.report("\tFAILED - Found host IP = " + hostip + "; MAC = " + "".join(MAC) + "".join(Port))
            result2 = main.FALSE
        elif Reststatus >1:
            main.log.report("\t FAILED - Host " + host + " with MAC:" + str(mac) + " has " + str(Reststatus) + " duplicated IP addresses. FAILED")
            main.log.report("Switches are: " + "; ".join(Switch))
            main.log.report("Ports are: " + "; ".join(Port))
            main.log.report("MACs are: " + "; ".join(MAC))
            result2 = main.FALSE
        else:
            main.log.report("\t PASSED - Host" + host + " with MAC:" + str(mac) + " does not exist. PASSED - host is not supposed to be attached to the switch.")
            result2 = main.TRUE
        utilities.assert_equals(expect=main.TRUE,actual=result2,onpass="s1-eth1 yanked!",onfail="s1-eth1 failed to be yanked!")

# Step to plug "s1-eth1" to s6
        main.step("Plug s1-eth1 into s6")
        result3 = main.Mininet1.plug(SW=main.params['PLUG']['sw6'],INTF=main.params['PLUG']['intf'])
        time.sleep(t_topowait)
        utilities.assert_equals(expect=main.TRUE,actual=result3,onpass="Plug command suceeded",onfail="Plug command failed ... ")
        main.step("\n\nPing issue one ping from " + str(host) + "to generate arp to switch. Ping result is not important")
        ping = main.Mininet1.pingHost(src = str(host),target = "10.0.0.254")
        time.sleep(t_restwait)
        Reststatus, Switch, Port, MAC = main.ONOS1.find_host(RestIP1,RestPort,url,hostip)

        main.log.report("Number of hosts with IP=10.0.0.1 found by ONOS is: " + str(Reststatus))
        if Reststatus ==1:
            main.log.report("\t PASSED - Found host IP = " + hostip + "; MAC = " + "".join(MAC) + "; attached to switchDPID = " + "".join(Switch) + "; at port = " + "".join(Port))
            result4 = main.TRUE
        elif Reststatus >1:
            main.log.report("\t FAILED - Host " + host + " with MAC: " + str(mac) + " has " + str(Reststatus) + "duplicated IP addresses. FAILED")
            main.log.report("switches are: " + "; ".join(Switch))
            main.log.report("Ports are: " + "; ".join(Port))
            main.log.report("MACs are: " + "; ".join(MAC))
            result4 = main.FALSE
        else:
            main.log.report("\t FAILED - Host " + host + " with MAC: " + str(mac) + " does not exist. FAILED")
            result4 = main.FALSE

# Step to put "s1-eth1" back to s1
        main.step("Move s1-eth1 back to s1")
        result5 = main.Mininet1.yank(SW=main.params['YANK']['sw6'],INTF=main.params['YANK']['intf'])
        time.sleep(t_topowait)
        result6 = main.Mininet1.plug(SW=main.params['PLUG']['sw1'],INTF=main.params['PLUG']['intf'])
        utilities.assert_equals(expect=main.TRUE,actual=(result5 and result6),onpass="Yank/Plug command suceeded",onfail="Yank/Plug command failed...")   
        main.log.info("\n\t\t\t\t ping issue one ping from" + str(host) + "to generate arp to switch. Ping result is not important" )   
        ping = main.Mininet1.pingHost(src = str(host),target = "10.0.0.254")
        time.sleep(t_restwait)
        Reststatus, Switch, Port, MAC = main.ONOS1.find_host(RestIP1,RestPort,url, hostip)

        main.log.report("Number of host with IP=10.0.0.1 found by ONOS is: " + str(Reststatus))
        if Reststatus == 1:
            main.log.report("\tPASSED - Found host IP = " + hostip + "; MAC = " + "".join(MAC) + "; attached to switchDPID = " + "".join(Switch) + "; at port = " + "".join(Port))
            result7 = main.TRUE
        elif Reststatus > 1:
            main.log.report("\t FAILED - Host " + host + " with MAC:" + str(mac) + " has " + str(Reststatuas) + " duplicated IP addresses. FAILED")
            main.log.report("switches are: " + "; ".join(Switch))
            main.log.report("Ports are: " + "; ".join(Port))
            main.log.report("MACs are: " + "; ".join(MAC))      
            result7 = main.FALSE
        else:   
            main.log.report("\t FAILED -Host " + host + " with MAC:" + str(mac) + " does not exist. FAILED")
            result7 = main.FALSE

        result = result1 and result2 and result3 and result4 and result5 and result6 and result7
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="DEVICE DISCOVERY TEST PASSED PLUG/UNPLUG/MOVE TEST",onfail="DEVICE DISCOVERY TEST FAILED")

    def CASE7(self, main) : 
        import time
        main.case("Bring Link between s1 and s2 up, then ping untill all hosts are reachable or fail after 10 attemtps!")
        main.step("Bringing Link up... " )
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="up")
        utilities.assert_equlas(expect=main.TRUE,actual=result,onpass="Link UP!",onfail="Link not brought up...")
        main.step("\n\n\t\tPing Test!")
        strtTime = time.time()
        result2 = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
        for i in range(2):
            if result2 == main.FALSE:
                time.sleep(5)
                result2 = main.ONOS1.check_status_report(main.params['RestIP'],main.params['NR_Switches'],main.params['NR_Links'])
            else:
                break
        strtTime = time.time()
        count = 1
        i = 6
        while i <16 :
            main.log.info("\n\t\t\t\th" + str(i) + " IS PINGING h" + str(i+25))
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+25))
            if ping ==main.FALSE and count<10:
                count +=1
                main.log.info("Ping failed, making attempt number " + str(count) + " in 2 seconds")
                i = 6
                time.sleep(2)
            elif ping ==main.FALSE and count==10:
                main.log.error("Ping test failed")
                i = 17
                result3 = main.FALSE
            elif ping ==main.TRUE:
                i += 1
                result3 = main.TRUE
        endTime = time.time()
        if result3 ==main.TRUE:
            main.log.report("\t Time to complete ping test: " + str(round(endTime-strtTime,2)) + " seconds")
        else:
            main.log.report("\tPing Tests FAILED!!")
        finalResult = result and result2 and result3 and result4
        utilities.assert_equals(expect=main.TRUE,actual=finalResult,onpass="NO PACKET LOSS, HOST IS REACHABLE",onfail="PACKET LOST, HOST IS NOT REACHABLE")
                


