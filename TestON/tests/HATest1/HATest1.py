
class HATest1:

    
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
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=main.params['CTRL']['ip2'],port1=main.params['CTRL']['port1'])
            elif i>=5 and i<8:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=main.params['CTRL']['ip3'],port1=main.params['CTRL']['port1'])
            elif i>=8 and i<18:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=main.params['CTRL']['ip4'],port1=main.params['CTRL']['port1'])
            elif i>=18 and i<28:
                main.Mininet1.assign_sw_controller(sw=str(i),ip1=main.params['CTRL']['ip5'],port1=main.params['CTRL']['port1'])
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
        time.sleep(30)

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
        time.sleep(400)
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
        main.case("Setting up and Gathering data for current state")
        



