
class OnosSanity :

    def __init__(self) :
        self.default = ''

    def CASE1(self,main) :
        import time
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
            main.log.info("Something is funny... restarting ONOS")
            main.ONOS1.stop()
            time.sleep(3)
            main.ONOS1.start()
            time.sleep(5) 
            data = main.ONOS1.isup()
        main.log.info("\n\n\t\t\t\t ONOS VERSION")
        main.ONOS1.get_version()
        main.log.info("\n\n")
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="ONOS is up and running!",onfail="ONOS didn't start...")
            
    def CASE2(self,main) :
        main.case("Checking if one MN host exists")
        main.step("Host IP Checking using checkIP")
        result = main.Mininet1.checkIP(main.params['CASE1']['destination'])
        main.step("Verifying the result")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Host IP address configured",onfail="Host IP address not configured")
        
    def CASE3(self,main) :
        import time
        main.case("Taking care of these flows!") 
        main.step("Cleaning out any leftover flows...")
        main.ONOS1.delete_flow("all")
        time.sleep(5)
        strtTime = time.time()
        main.ONOS1.add_flow(main.params['FLOWDEF'])
        main.case("Checking flows")
        result = main.FALSE
        count = 1
        main.log.info("Wait for flows to settle, then check")
        while result == main.FALSE:
            main.step("Waiting")
            time.sleep(10)
            main.step("Checking")
            result = main.ONOS1.check_flow()
            if result== main.FALSE and count < 6:
                count = count + 1
                main.log.info("Flow failed, waiting 10 seconds then making attempt number "+str(count))
            elif result == main.FALSE and count == 6:
                success = main.FALSE
                break
            else:
                success = main.TRUE
                break
        endTime = time.time()
        main.log.info("\n\t\t\t\tTime to add flows: "+str(endTime-strtTime)+" seconds")
        utilities.assert_equals(expect=main.TRUE,actual=success,onpass="Flow check PASS",onfail="Flow check FAIL")
        #time.sleep(10)
        #data = main.ONOS1.get_flow("all")   

    def CASE4(self,main) :
        main.case("Testing ping...")
        ping_result = main.Mininet1.pingHost(src=main.params['PING']['source1'],target=main.params['PING']['target1'])
        utilities.assert_equals(expect=main.TRUE,actual=ping_result,onpass="NO PACKET LOSS, HOST IS REACHABLE",onfail="PACKET LOST, HOST IS NOT REACHABLE") 

    def CASE5(self,main) :
        import time
        main.case("Bringing Link down... ")
        result = main.Mininet1.link(END1=main.params['LINK']['begin'],END2=main.params['LINK']['end'],OPTION="down")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="Link DOWN!",onfail="Link not brought down...")
        time.sleep(10)

    def CASE6(self,main) :
        import time
        main.case("Checking flows")
        result = main.FALSE
        count = 1
        main.log.info("Wait for flows to settle, then check")
        while result == main.FALSE:
            main.step("Waiting")
            time.sleep(10)
            main.step("Checking")
            result = main.ONOS1.check_flow()
            if result== main.FALSE and count < 6:
                count = count + 1
                main.log.info("Flow failed, waiting 10 seconds then making attempt number "+str(count))
            elif result == main.FALSE and count == 6:
                success = main.FALSE
                break
            else:
                success = main.TRUE
                break
        utilities.assert_equals(expect=main.TRUE,actual=success,onpass="Flow check PASS",onfail="Flow check FAIL")
   
    def CASE7(self,main) :
        main.case("Pinging EVERYTHINGGG!!!")
        import time
        strtTime = time.time()
        result = main.TRUE
        exit = main.FALSE
        count = 1
        while 1:
            for i in range(6, 16) :
                main.log.info("\n\t\t\t\th"+str(i)+" IS PINGING h"+str(i+25) )
                ping = main.Mininet1.pingHost(src="h"+str(i),target="h"+str(i+25))
                if ping == main.FALSE and count < 6:
                    count = count + 1
                    main.log.info("Ping failed, making attempt number "+str(count)+" in 10 seconds")
                    time.sleep(10)
                    break
                elif ping == main.FALSE and count ==6:
                    main.log.error("Ping test failed")
                    exit = main.TRUE
                    break
                elif ping == main.TRUE:
                    exit = main.TRUE
            if exit == main.TRUE:
               endTime = time.time() 
               break
        main.log.info("\n\t\t\t\tTime to complete ping test: "+str(endTime-strtTime)+" seconds")
        utilities.assert_equals(expect=main.TRUE,actual=result,onpass="NO PACKET LOSS, HOST IS REACHABLE",onfail="PACKET LOST, HOST IS NOT REACHABLE")

