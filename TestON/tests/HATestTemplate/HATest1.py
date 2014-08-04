
class HATest1:

    global topology
    global masterSwitchList
    global highIntentList
    global lowIntentList
    global flows
    flows = []

    def __init__(self) :
        self.default = ''

    '''
    CASE1 is to close any existing instances of ONOS, clean out the 
    RAMCloud database, and start up ONOS instances. 
    '''
    def CASE1(self,main) :
        main.case("Initial Startup")
        main.step("Stop ONOS")
        if not main.ONOS1.status():
            main.ONOS1.stop_all()
        if not main.ONOS1.status():
            main.ONOS2.stop_all()
        if not main.ONOS1.status():
            main.ONOS3.stop_all()
        if not main.ONOS1.status():
            main.ONOS4.stop_all()
        main.ONOS1.stop_rest()
        main.ONOS2.stop_rest()
        main.ONOS3.stop_rest()
        main.ONOS4.stop_rest()
        result = main.ONOS1.status() or main.ONOS2.status() \
                or main.ONOS3.status() or main.ONOS4.status()
        utilities.assert_equals(expect=main.FALSE,actual=result,onpass="ONOS stopped successfully",onfail="ONOS WAS NOT KILLED PROPERLY")
        main.step("Startup Zookeeper")
        main.ZK1.start()
        main.ZK2.start()
        main.ZK3.start()
        main.ZK4.start()
        result = main.ZK1.isup() and main.ZK2.isup()\
                and main.ZK3.isup() and main.ZK4.isup
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Zookeeper started successfully",onfail="ZOOKEEPER FAILED TO START")
        main.step("Cleaning RC Database and Starting All")
        main.RC1.deldb()
        main.RC2.deldb()
        main.RC3.deldb()
        main.RC4.deldb()
        main.ONOS1.start_all()
        main.ONOS2.start_all()
        main.ONOS3.start_all()
        main.ONOS4.start_all()
        main.ONOS1.start_rest()
        main.step("Testing Startup")
        result1 = main.ONOS1.rest_status()
        vm1 = main.RC1.status_coor and main.RC1.status_serv and \
                main.ONOS1.isup()
        vm2 = main.RC2.status_coor and main.ONOS2.isup()
        vm3 = main.RC3.status_coor and main.ONOS3.isup()
        vm4 = main.RC4.status_coor and main.ONOS4.isup()
        result = result1 and vm1 and vm2 and vm3 and vm4
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Everything started successfully",onfail="EVERYTHING FAILED TO START")

    '''
    CASE2
    '''
    def CASE2(self,main) :
        import time
        import json
        import re
        main.log.report("Assigning Controllers")
        main.case("Assigning Controllers")
        main.step("Assign Master Controllers")
        for i in range(1,28):
            if i ==1:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
            elif i>=2 and i<5:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=main.params['CTRL']['ip2'],port1=main.params['CTRL']['port2'])
            elif i>=5 and i<8:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=main.params['CTRL']['ip3'],port1=main.params['CTRL']['port3'])
            elif i>=8 and i<18:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=main.params['CTRL']['ip4'],port1=main.params['CTRL']['port4'])
            elif i>=18 and i<28:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=main.params['CTRL']['ip5'],port1=main.params['CTRL']['port5'])
            else:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=main.params['CTRL']['ip1'],port1=main.params['CTRL']['port1'])
        
        result = main.TRUE
        for i in range (1,28):
            if i==1:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is " + str(response))
                if re.search("tcp:"+main.params['CTRL']['ip1'],response):
                    result = result and main.TRUE
                else:
                    result = main.FALSE
            elif i>=2 and i<5:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is " + str(response))
                if re.search("tcp:"+main.params['CTRL']['ip2'],response):
                    result = result and main.TRUE
                else:
                    result = main.FALSE
            elif i>=5 and i<8:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is " + str(response))
                if re.search("tcp:"+main.params['CTRL']['ip3'],response):
                    result = result and main.TRUE
                else:
                    result = main.FALSE
            elif i>=8 and i<18:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is " + str(response))
                if re.search("tcp:"+main.params['CTRL']['ip4'],response):
                    result = result and main.TRUE
                else:
                    result = main.FALSE
            elif i>=18 and i<28:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is " + str(response))
                if re.search("tcp:"+main.params['CTRL']['ip5'],response):
                    result = result and main.TRUE
                else:
                    result = main.FALSE
            else:
                response = main.Mininet1.get_sw_controller("s"+str(i))
                print("Response is" + str(response))
                if re.search("tcp:" +main.params['CTRL']['ip1'],response):
                    result = result and main.TRUE
                else:
                    result = main.FALSE
        utilities.assert_equals(expect = main.TRUE,actual=result,onpass="MasterControllers assigned correctly")

    def CASE3(self,main) :
        import time
        import json
        import re
        main.case("Adding Intents")
        intentIP = main.params['CTRL']['ip1']
        intentPort=main.params['INTENTS']['intentPort']
        intentURL=main.params['INTENTS']['intentURL']
        count = 1
        for i in range(8,18):
            srcMac = '00:00:00:00:00:' + str(hex(i)[2:]).zfill(2)
            dstMac = '00:00:00:00:00:'+str(hex(i+10)[2:])
            srcDPID = '00:00:00:00:00:00:30:'+str(i).zfill(2)
            dstDPID= '00:00:00:00:00:00:60:' +str(i+10)
            main.ONOS1.add_intent(intent_id=str(count),src_dpid=srcDPID,dst_dpid=dstDPID,src_mac=srcMac,dst_mac=dstMac,intentIP=intentIP,intentPort=intentPort,intentURL=intentURL)
            count+=1
            dstDPID = '00:00:00:00:00:00:30:'+str(i).zfill(2)
            srcDPID= '00:00:00:00:00:00:60:' +str(i+10)
            dstMac = '00:00:00:00:00:' + str(hex(i)[2:]).zfill(2)
            srcMac = '00:00:00:00:00:'+str(hex(i+10)[2:])
            main.ONOS1.add_intent(intent_id=str(count),src_dpid=srcDPID,dst_dpid=dstDPID,src_mac=srcMac,dst_mac=dstMac,intentIP=intentIP,intentPort=intentPort,intentURL=intentURL)
            count+=1
        count = 1
        i = 8
        result = main.TRUE
        while i <18 :
            main.log.info("\n\nh"+str(i)+" is Pinging h" + str(i+10))
            ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+10))
            if ping ==main.FALSE and count <9:
                count+=1
                i = 8
                result = main.FALSE
                main.log.info("Ping FAILED! Making attempt number "+str(count) + "in 2 seconds")
                time.sleep(2)
            elif ping==main.FALSE:
                main.log.info("PINGS FAILED! MAX RETRIES REACHED!")
                i=19
                result = main.FALSE
            elif ping==main.TRUE:
                main.log.info("Ping passed!")
                i+=1
                result = main.TRUE
            else:
                main.log.info("ERROR!!")
                result = main.ERROR
        if result==main.FALSE:
            main.log.info("INTENTS HAVE NOT BEEN INSTALLED CORRECTLY!! EXITING!!!")
            main.cleanup()
            main.exit()
        

    def CASE4(self,main) :
        import time
        from subprocess import Popen, PIPE
        main.case("Setting up and Gathering data for current state")
        main.step("Get the current In-Memory Topology on each ONOS Instance")

        '''
        ctrls = []
        count = 1
        while True:
            temp = ()
            if ('ip'+str(count)) in main.params['CTRL']:
                temp = temp+(getattr(main,('ONOS'+str(count))),)
                temp = temp + ("ONOS"+str(count),)
                temp = temp + (main.params['CTRL']['ip'+str(count)],)
                temp = temp + (eval(main.params['CTRL']['port'+str(count)]),)
                ctrls.append(temp)
                count+=1
            else:
                break
        topo_result = main.TRUE

        for n in range(1,count):
            temp_result = main.Mininet1.compare_topo(ctrls,main.ONOS1.get_json(main.params['CTRL']['ip'+str(n)]+":"+main.params['CTRL']['restPort'+str(n)]+main.params['TopoRest']))
        '''

        main.step("Get the Mastership of each switch")
        (stdout,stderr)=Popen(["curl",main.params['CTRL']['ip1']+":"+main.params['CTRL']['restPort1']+main.params['CTRL']['switchURL']],stdout=PIPE).communicate()
        global masterSwitchList1
        masterSwitchList1 = stdout

        main.step("Get the High Level Intents")
        (stdout,stderr)=Popen(["curl",main.params['CTRL']['ip1']+":"+main.params['CTRL']['restPort1']+main.params['CTRL']['intentHighURL']],stdout=PIPE).communicate()
        global highIntentList1
        highIntentList1 = stdout
        
        main.step("Get the Low level Intents")
        (stdout,stderr)=Popen(["curl",main.params['CTRL']['ip1']+":"+main.params['CTRL']['restPort1']+main.params['CTRL']['intentLowURL']],stdout=PIPE).communicate()
        global lowIntentList1
        lowIntentList1= stdout
        
        main.step("Get the OF Table entries")
        global flows
        flows=[]
        for i in range(1,28):
            print main.Mininet2.get_flowTable("s"+str(i))
            flows.append(main.Mininet2.get_flowTable("s"+str(i)))

        
        main.step("Start continuous pings")
        main.Mininet2.pingLong(src=main.params['PING']['source1'],target=main.params['PING']['target1'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source2'],target=main.params['PING']['target2'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source3'],target=main.params['PING']['target3'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source4'],target=main.params['PING']['target4'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source5'],target=main.params['PING']['target5'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source6'],target=main.params['PING']['target6'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source7'],target=main.params['PING']['target7'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source8'],target=main.params['PING']['target8'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source9'],target=main.params['PING']['target9'],pingTime=500)
        main.Mininet2.pingLong(src=main.params['PING']['source10'],target=main.params['PING']['target10'],pingTime=500)


    def CASE5(self,main) :
        import re
        main.case("MAIN COMPONENT FAILURE AND SCENARIO SPECIFIC TESTS")
        main.step("Zookeeper Server Failure!")
        result = main.TRUE
        master1 = main.ZK1.status()
        print master1
        if re.search("leader",master1):
            main.ZK1.stop()
            main.log.info("ZK1 was Master and Killed! Also Killing ZK2")
            main.ZK2.stop()
            time.sleep(10)
            if re.search("leader",main.ZK3.status()) or re.search("leader",main.ZK4.status()) or re.search("leader",main.ZK5.status()):
                result = main.TRUE
                main.log.info("New Leader Elected")
            else:
                result = main.FALSE
                main.log.info("NO NEW ZK LEADER ELECTED!!!")
        else:
            master2 = main.ZK2.status()
            if re.search("leader",master2):
                main.ZK2.stop()
                main.log.info("ZK2 was Master and Killed! Also Killing ZK3")
                main.ZK3.stop()
                time.sleep(10)
                if re.search("leader",main.ZK1.status()) or re.search("leader",main.ZK4.status()) or re.search("leader",main.ZK5.status()):
                    result = main.TRUE
                    main.log.info("New Leader Elected")
                else:
                    result = main.FALSE
                    main.log.info("NO NEW ZK LEADER ELECTED!!!")
            else:
                master3 = main.ZK3.status()
                if re.search("leader",master3):
                    main.ZK3.stop()
                    main.log.info("ZK3 was Master and Killed! Also Killing ZK4")
                    main.ZK4.stop()
                    time.sleep(10)
                    if re.search("leader",main.ZK1.status()) or re.search("leader",main.ZK2.status()) or re.search("leader",main.ZK5.status()):
                        result = main.TRUE
                        main.log.info("New Leader Elected")
                    else:
                        result = main.FALSE
                        main.log.info("NO NEW ZK LEADER ELECTED!!!")
                else:
                    master4 = main.ZK4.status()
                    if re.search("leader",master4):
                        main.ZK4.stop()
                        main.log.info("ZK4 was Master and Killed! Also Killing ZK5")
                        main.ZK5.stop()
                        time.sleep(10)
                        if re.search("leader",main.ZK1.status()) or re.search("leader",main.ZK2.status()) or re.search("leader",main.ZK3.status()):
                            result = main.TRUE
                            main.log.info("New Leader Elected")
                        else:
                            result = main.FALSE
                            main.log.info("NO NEW ZK LEADER ELECTED!!!")
                    else:
                        main.ZK5.stop()
                        main.log.info("ZK5 was Master and Killed! Also Killing ZK1")
                        main.ZK1.stop()
                        time.sleep(10)
                        if re.search("leader",main.ZK3.status()) or re.search("leader",main.ZK4.status()) or re.search("leader",main.ZK2.status()):
                            result = main.TRUE
                            main.log.info("New Leader Elected")
                        else:
                            result = main.FALSE
                            main.log.info("NO NEW ZK LEADER ELECTED!!!")


    def CASE6(self,main) :
        import os
        main.case("Running ONOS Constant State Tests")
        main.step("Get the current In-Memory Topology on each ONOS Instance and Compare it to the Topology before component failure")

        main.step("Get the Mastership of each switch and compare to the Mastership before component failure")
        (stdout,stderr)=Popen(["curl",main.params['CTRL']['ip1']+":"+main.params['CTRL']['restPort1']+main.params['CTRL']['switchURL']],stdout=PIPE).communicate()
        result = main.TRUE
        for i in range(1,28):
            if main.ZK1.findMaster(switchDPID="s"+str(i),switchList=masterSwitchList1)==main.ZK1.findMaster(switchDPID="s"+str(i),switchList=stdout):
                result = result and main.TRUE
            else:
                result = main.FALSE
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Mastership of Switches was not changed",onfail="MASTERSHIP OF SWITCHES HAS CHANGED!!!")

        main.step("Get the High Level Intents and compare to before component failure")
        (stdout,stderr)=Popen(["curl",main.params['CTRL']['ip1']+":"+main.params['CTRL']['restPort1']+main.params['CTRL']['intentHighURL']],stdout=PIPE).communicate()
        changesInIntents=main.ONOS1.comp_intents(preIntents=highIntentList1,postIntents=stdout)
        if not changesInIntents:
            result = main.TRUE
        else:
            main.log.info("THERE WERE CHANGES TO THE HIGH LEVEL INTENTS! CHANGES WERE: "+str(changesInIntents))
            result = main.FALSE
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="No changes to High level Intents",onfail="CHANGES WERE MADE TO HIGH LEVEL INTENTS")

        main.step("Get the Low level Intents and compare to before component failure")
        (stdout,stderr)=Popen(["curl",main.params['CTRL']['ip1']+":"+main.params['CTRL']['restPort1']+main.params['CTRL']['intentLowURL']],stdout=PIPE).communicate()
        changesInIntents=main.ONOS1.comp_low(preIntents=lowIntentList1,postIntents=stdout)
        if not changesInIntents:
            result = main.TRUE
        else:
            main.log.info("THERE WERE CHANGES TO THE LOW LEVEL INTENTS! CHANGES WERE: "+str(changesInIntents))
            result = main.FALSE
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="No changes to Low level Intents",onfail="CHANGES WERE MADE TO LOW LEVEL INTENTS")


        main.step("Get the OF Table entries and compare to before component failure")
        result = main.TRUE
        flows2=[]
        for i in range(27):
            flows2.append(main.Mininet2.get_flowTable(sw="s"+str(i+1)))
            result = result and main.Mininet2.flow_comp(flow1=flows[i], flow2=main.Mininet2.get_flowTable(sw="s"+str(i+1)))   
            print flows[i]
            print flows2[i]
            if result == main.FALSE:
                main.log.info("DIFFERENCES IN FLOW TABLES FOR SWITCH "+str(i))
                break
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="No changes in the flow tables",onfail="CHANGES IN THE FLOW TABLES!!")
        
        main.step("Check the continuous pings to ensure that no packets were dropped during component failure")
        main.Mininet2.pingKill()
        result = main.FALSE
        for i in range(8,18):
            result = result or main.Mininet2.checkForLoss("/tmp/ping.h"+str(i))
        if result==main.TRUE:
            main.log.info("LOSS IN THE PINGS!")
        elif result == main.ERROR:
            main.log.info("There are multiple mininet process running!!")
        else:
            main.log.info("No Loss in the pings!")
        utilities.assert_equals(expect=main.FALSE,actual=result,onpass="No Loss of connectivity!",onfail="LOSS OF CONNECTIVITY")





