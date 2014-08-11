class scaleONOS7nodes :



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
        main.ONOS1.stop_all()
        main.ONOS2.stop_all()
        main.ONOS3.stop_all()
#        main.print_hello_world()
        main.ONOS4.stop_all()
       # main.ONOS5.stop_all()
       # main.ONOS6.stop_all()
       # main.ONOS7.stop_all()
        main.ONOS2.stop_rest()
        time.sleep(5)
        #main.ONOS1.handle.sendline("cp ~/onos.properties.proactive ~/ONOS/conf/onos.properties")
        #main.ONOS2.handle.sendline("cp ~/onos.properties.proactive ~/ONOS/conf/onos.properties")
        #main.ONOS3.handle.sendline("cp ~/onos.properties.proactive ~/ONOS/conf/onos.properties")
        #main.ONOS4.handle.sendline("cp ~/onos.properties.proactive ~/ONOS/conf/onos.properties")        
        #main.step("Start tcpdump on mn")
        #main.Mininet2.start_tcpdump(main.params['tcpdump']['filename'], intf = main.params['tcpdump']['intf'], port = main.params['tcpdump']['port'])
        main.step("Start ONOS")
        main.Zookeeper1.start()
        main.Zookeeper2.start()
        main.Zookeeper3.start()
        main.Zookeeper4.start()
        time.sleep(5)
        
        
        main.RamCloud1.del_db()
        main.RamCloud2.del_db()
        main.RamCloud3.del_db()
        main.RamCloud4.del_db()

        time.sleep(5)
        #main.log.report("Pulling latest code from github to all nodes")
          
        """
        for i in range(2):
            uptodate = main.ONOS1.git_pull()
            main.ONOS2.git_pull()
            main.ONOS3.git_pull()
        #    main.ONOS4.git_pull()
            ver1 = main.ONOS1.get_version()
            ver2 = main.ONOS3.get_version()
            if ver1==ver2:
                break
            elif i==1:
                main.ONOS2.git_pull("ONOS1 master")
                main.ONOS3.git_pull("ONOS1 master")
               # main.ONOS4.git_pull("ONOS1 master")
        if uptodate==0:
       # if 1:
            main.ONOS1.git_compile()
            main.ONOS2.git_compile()
            main.ONOS3.git_compile()
           # main.ONOS4.git_compile()
        main.ONOS1.print_version()    
       # main.RamCloud1.git_pull()
       # main.RamCloud2.git_pull()
       # main.RamCloud3.git_pull()
       # main.RamCloud4.git_pull()
       # main.ONOS1.get_version()
       # main.ONOS2.get_version()
       # main.ONOS3.get_version()
       # main.ONOS4.get_version()
       # main.ONOS1.start_all()
       # main.ONOS2.start_all()
       # main.ONOS3.start_all()
       # main.ONOS4.start_all()

        """
        main.RamCloud1.start_coor()
        main.RamCloud1.start_serv()
        main.RamCloud2.start_serv()
        main.RamCloud3.start_serv()
        #main.RamCloud4.start_serv()

        main.ONOS1.start()
        main.ONOS2.start()
        main.ONOS3.start()
        #main.ONOS4.start()



        main.ONOS1.start_rest()
        main.ONOS2.start_rest()
        main.ONOS3.start_rest()
        test= main.ONOS2.rest_status()
        if test == main.FALSE:
            main.ONOS1.start_rest()
        main.ONOS1.get_version()
        main.log.report("Startup check Zookeeper1, RamCloud1, and ONOS1 connections")
        main.step("Testing startup Zookeeper")   
        data =  main.Zookeeper1.isup() and main.Zookeeper2.isup() and main.Zookeeper3.isup()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Zookeeper is up!",onfail="Zookeeper is down...")
        
        main.step("Testing startup RamCloud")   
        data =  main.RamCloud1.status_serv() and main.RamCloud2.status_serv() and main.RamCloud3.status_serv() #and main.RamCloud4.status_serv()
        if data == main.FALSE:
            main.RamCloud1.stop_coor()
            main.RamCloud1.stop_serv()
            main.RamCloud2.stop_serv()
            main.RamCloud3.stop_serv()
        #    main.RamCloud4.stop_serv()

            time.sleep(5)
            main.RamCloud1.start_coor()
            main.RamCloud1.start_serv()
            main.RamCloud2.start_serv()
            main.RamCloud3.start_serv()
         #   main.RamCloud4.start_serv()
            time.sleep(5)
            data =  main.RamCloud1.status_serv() and main.RamCloud2.status_serv() and main.RamCloud3.status_serv() #and main.RamCloud4.status_serv()
            

        
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="RamCloud is up!",onfail="RamCloud is down...")
        
        main.step("Testing startup ONOS")   
        data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup() #and main.ONOS4.isup()
        for i in range(3):
            if data == main.FALSE: 
                #main.log.report("Something is funny... restarting ONOS")
                #main.ONOS1.stop()
                time.sleep(3)
                #main.ONOS1.start()
                #time.sleep(5) 
                data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup() #and main.ONOS4.isup()
            else:
                break
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="ONOS is up and running!",onfail="ONOS didn't start...")
        time.sleep(10)


    def CASE2(self,main) :
        ip1 = main.params['CTRL']['ip1']
        ip2 = main.params['CTRL']['ip2']
        ip3 = main.params['CTRL']['ip3']
        rate1 = main.params['RATE1']
        run_dur = main.params['RUN_DUR']
        loop = int( main.params['loop'])
        port = main.params['port']
        switches_num = main.params['switches_num']
        print loop
        sleep_t =int( main.params['sleep_t'])
        main.case("Starting SB load on 3 nodes from mininet with " + rate1 +"  added/removed/s for " + run_dur)
        main.Mininet2.handle.sendline("sudo ./loadgen_SB.py -u \"" + ip1 + " " + ip2 + " " + ip3 + "\"" + " -s " + switches_num + " -p " + port + " -a " + rate1 + " -d " + rate1 + " -l " + run_dur)
        main.log.info("Adding switches and ports.....")
        main.Mininet2.handle.expect("Starting SB load....", timeout=400)
        main.log.info("Starting SB load....")
        import time
        import json
        open("/home/admin/TestON/tests/scaleONOS7nodes/logs/scale3nodesrate1", 'w').close()
        url1 = "http://10.128.10.1:8080/wm/onos/metrics"
        url2 = "http://10.128.10.2:8080/wm/onos/metrics"
        url3 = "http://10.128.10.3:8080/wm/onos/metrics"
        f = open("/home/admin/TestON/tests/scaleONOS7nodes/logs/scale3nodesrate1", "a")
        #time.sleep(10)
        for i in range(int (loop)):
            json_str1 = main.ONOS1.get_json(url1)
            json_str2 = main.ONOS2.get_json(url2)
            json_str3 = main.ONOS3.get_json(url3)
            if json_str1 != "" and json_str2 != "" and json_str3 != "":
                # write_str = str(json_str["meters"][4]["meter"][2])
                #print str(json_str["meters"][4])
                #f.write(str(json_str["meters"][4]))
                #f.write('\n')
                #time.sleep(3)
                f.write("ONOS1 \n")
                f.write(str(json_str1["meters"][4]['meter']['count']))
                f.write('\t')
                f.write(str(json_str1["meters"][4]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str1["meters"][4]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str1["meters"][4]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str1["meters"][4]['meter']['mean_rate']))
                f.write('\n')
                f.write("ONOS2 \n")
                f.write(str(json_str2["meters"][4]['meter']['count']))
                f.write('\t')
                f.write(str(json_str2["meters"][4]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str2["meters"][4]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str2["meters"][4]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str2["meters"][4]['meter']['mean_rate']))
                f.write('\n')
                f.write("ONOS3 \n")
                f.write(str(json_str3["meters"][4]['meter']['count']))
                f.write('\t')
                f.write(str(json_str3["meters"][4]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str3["meters"][4]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str3["meters"][4]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str3["meters"][4]['meter']['mean_rate']))
                f.write('\n')
                f.write('\n')
                
                f.write("--------------------------------------------------------------------------------- \n") 
                time.sleep(sleep_t)
        f.close() 
        main.Mininet2.handle.expect("\$", timeout=900)
       # main.Mininet2.handle.sendline("sudo mn -c")
        #main.Mininet2.handle.expect("\$")
        time.sleep(5)
       # main.Mininet2.handle.expect("\$", timeout=900)
        

    def CASE3(self,main):
        ip1 = main.params['CTRL']['ip1']
        ip2 = main.params['CTRL']['ip2']
        ip3 = main.params['CTRL']['ip3']
        import time
        rate2 = main.params['RATE2']
        run_dur = main.params['RUN_DUR']
        loop = int(main.params['loop'])
        sleep_t = int(main.params['sleep_t'])
        port = main.params['port']
        switches_num = main.params['switches_num']
        main.case("Starting SB load on 3 nodes from mininet with " + rate2 +"  added/removed/s for " + run_dur)
        #main.Mininet2.handle.sendline("./loadgen_SB.sh startload \"" + ip1 + " " + ip2 + " " + ip3 + "\"" + " " + switches_num + " " + port + " " + rate2 + " " + run_dur +  "  \"11\"")
        main.Mininet2.handle.sendline("sudo ./loadgen_SB.py -u \"" + ip1 + " " + ip2 + " " + ip3 + "\"" + " -s " + switches_num + " -p " + port + " -a " + rate2 + " -d " + rate2 + " -l " + run_dur)
       #main.Mininet2.handle.sendline("./loadgen_SB.sh startload \"10.128.10.1\" 100 50 1200 \"11\"")
        main.Mininet2.handle.expect("Starting SB load....", timeout=900 )
        
        import json
        
        open("/home/admin/TestON/tests/scaleONOS7nodes/logs/scale3nodesrate2", 'w').close()
        url1 = "http://10.128.10.1:8080/wm/onos/metrics"
        url2 = "http://10.128.10.2:8080/wm/onos/metrics"
        url3 = "http://10.128.10.3:8080/wm/onos/metrics"
        f = open("/home/admin/TestON/tests/scaleONOS7nodes/logs/scale3nodesrate2", "a")
        #time.sleep(10)
        for i in range(int (loop)):
            json_str1 = main.ONOS1.get_json(url1)
            json_str2 = main.ONOS2.get_json(url2)
            json_str3 = main.ONOS3.get_json(url3)
            if json_str1 != "" and json_str2 != "" and json_str3 != "":
                # write_str = str(json_str["meters"][4]["meter"][2])
                #print str(json_str["meters"][4])
                #f.write(str(json_str["meters"][4]))
                #f.write('\n')
                #time.sleep(3)
                f.write("ONOS1 \n")
                f.write(str(json_str1["meters"][4]['meter']['count']))
                f.write('\t')
                f.write(str(json_str1["meters"][4]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str1["meters"][4]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str1["meters"][4]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str1["meters"][4]['meter']['mean_rate']))
                f.write('\n')
                f.write("ONOS2 \n")
                f.write(str(json_str2["meters"][4]['meter']['count']))
                f.write('\t')
                f.write(str(json_str2["meters"][4]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str2["meters"][4]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str2["meters"][4]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str2["meters"][4]['meter']['mean_rate']))
                f.write('\n')
                f.write("ONOS3 \n")
                f.write(str(json_str3["meters"][4]['meter']['count']))
                f.write('\t')
                f.write(str(json_str3["meters"][4]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str3["meters"][4]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str3["meters"][4]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str3["meters"][4]['meter']['mean_rate']))
                f.write('\n')
                f.write('\n')
                f.write("--------------------------------------------------------------------------------- \n") 
                time.sleep(sleep_t)
        f.close()
        main.Mininet2.handle.expect("\$", timeout=900)
       # main.Mininet2.handle.sendline("sudo mn -c")
        #time.sleep(5)
       # main.Mininet2.handle.expect("\$", timeout=900)


    def CASE4(self,main):
        
        main.case("Starting NB Throughput test")
        ip1 = main.params['CTRL']['ip1']
        ip2 = main.params['CTRL']['ip2']
        ip3 = main.params['CTRL']['ip3']
        import time
        import json

        main.Mininet4.handle.expect("\$")
        #main.Mininet2.handle.sendline("sudo mn --custom topo-intentTPtest.py --topo mytopo --mac --arp")
        #main.Mininet2.handle.expect("mininet>" , timeout=400)
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s1 tcp:10.128.10.1:6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s2 tcp:10.128.10.1:6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s3 tcp:10.128.10.2:6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s4 tcp:10.128.10.2:6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s5 tcp:10.128.10.3:6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s6 tcp:10.128.10.3:6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s7 tcp:10.128.10.3:6633")

        main.ONOS3.handle.sendline("cd ~admin/suibin-dev")
        main.ONOS3.handle.expect("\$")

        main.ONOS3.handle.sendline("./multiLoadgen_NB.py -u \"10.128.10.1:8080 10.128.10.2:8080 10.128.10.3:8080 \" -i 4 -g 100 -a 1 -d 1 -p 0")
        main.ONOS3.handle.expect("intent group is : 0", timeout=900)

        
        import json
        
        open("/home/admin/TestON/tests/scaleONOS7nodes/logs/NBscale3nodesrate1", 'w').close()
        url1 = "http://10.128.10.1:8080/wm/onos/metrics"
        url2 = "http://10.128.10.2:8080/wm/onos/metrics"
        url3 = "http://10.128.10.3:8080/wm/onos/metrics"
        f = open("/home/admin/TestON/tests/scaleONOS7nodes/logs/NBscale3nodesrate1", "a")
        #time.sleep(10)
        for i in range(8):
            json_str1 = main.ONOS1.get_json(url1)
            json_str2 = main.ONOS2.get_json(url2)
            json_str3 = main.ONOS3.get_json(url3)
            if json_str1 != "" and json_str2 != "" and json_str3 != "":
                f.write("ONOS1......IncomingRate \n ")
                f.write(str(json_str1["meters"][0]['meter']['count']))
                f.write('\t')
                f.write(str(json_str1["meters"][0]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str1["meters"][0]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str1["meters"][0]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str1["meters"][0]['meter']['mean_rate']))
                f.write('\n')
                f.write("ONOS2......IncomingRate \n")
                f.write(str(json_str2["meters"][0]['meter']['count']))
                f.write('\t')
                f.write(str(json_str2["meters"][0]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str2["meters"][0]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str2["meters"][0]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str2["meters"][0]['meter']['mean_rate']))
                f.write('\n')
                f.write("ONOS3......IncomingRate \n")
                f.write(str(json_str3["meters"][0]['meter']['count']))
                f.write('\t')
                f.write(str(json_str3["meters"][0]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str3["meters"][0]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str3["meters"][0]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str3["meters"][0]['meter']['mean_rate']))
                f.write('\n')
                f.write('\n')

                f.write("--------------------------------------------------------------------------------- \n") 
                
                f.write("ONOS1......ProcessingRate \n ")
                f.write(str(json_str1["meters"][1]['meter']['count']))
                f.write('\t')
                f.write(str(json_str1["meters"][1]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str1["meters"][1]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str1["meters"][1]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str1["meters"][1]['meter']['mean_rate']))
                f.write('\n')
                f.write("ONOS2......ProcessingRate \n")
                f.write(str(json_str2["meters"][1]['meter']['count']))
                f.write('\t')
                f.write(str(json_str2["meters"][1]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str2["meters"][1]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str2["meters"][1]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str2["meters"][1]['meter']['mean_rate']))
                f.write('\n')
                f.write("ONOS3......ProcessingRate \n")
                f.write(str(json_str3["meters"][1]['meter']['count']))
                f.write('\t')
                f.write(str(json_str3["meters"][1]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str3["meters"][1]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str3["meters"][1]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str3["meters"][1]['meter']['mean_rate']))
                f.write('\n')
                f.write('\n')

                f.write("--------------------------------------------------------------------------------- \n") 
                time.sleep(10)
        f.close()

        main.ONOS3.handle.expect("\$", timeout=900)
        
    def CASE5(self,main):
        
        main.case("Starting ONOS scale-up to 4 nodes ")
        import time
       # main.RamCloud4.start_serv()
        main.Zookeeper1.start()
        time.sleep(5)
        
        main.RamCloud4.del_db()
        time.sleep(3)
        main.RamCloud4.start_serv()
        time.sleep(3)
        main.ONOS4.start()
        main.ONOS4.start_rest()
        time.sleep(5)
        data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup() and main.ONOS4.isup()
        for i in range(3):
            if data == main.FALSE: 
                #main.log.report("Something is funny... restarting ONOS")
                #main.ONOS1.stop()
                time.sleep(3)
                #main.ONOS1.start()
                #time.sleep(5) 
                data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup() and main.ONOS4.isup()
            else:
                break
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="ONOS is up and running!",onfail="ONOS didn't start...")
        time.sleep(10)

    def CASE6(self,main):
        
        ip1 = main.params['CTRL']['ip1']
        ip2 = main.params['CTRL']['ip2']
        ip3 = main.params['CTRL']['ip3']
        ip4 = main.params['CTRL']['ip4']
        rate1 = main.params['RATE1']
        run_dur = main.params['RUN_DUR']
        loop = int( main.params['loop'])
        switches_num = main.params['switches_num']
        port = main.params['port']
        print loop
        sleep_t =int( main.params['sleep_t'])
        main.case("Starting SB load on 4 nodes from mininet with " + rate1 +"  added/removed/s for " + run_dur)
        #main.Mininet2.handle.sendline("./loadgen_SB.sh startload \"" + ip1 + " " + ip2 + " " + ip3 + " " + ip4 + "\"" + " " + switches_num + " " + port + " " + rate1 + " " + run_dur +  "  \"11\"")
        main.Mininet2.handle.sendline("sudo ./loadgen_SB.py -u \"" + ip1 + " " + ip2 + " " + ip3 + " " + ip4 +  "\"" + " -s " + switches_num + " -p " + port + " -a " + rate1 + " -d " + rate1 + " -l " + run_dur)
        main.Mininet2.handle.expect("Starting SB load....", timeout=900)
        import time
        import json
        open("/home/admin/TestON/tests/scaleONOS7nodes/logs/scale4nodesrate1", 'w').close()
        url1 = "http://10.128.10.1:8080/wm/onos/metrics"
        url2 = "http://10.128.10.2:8080/wm/onos/metrics"
        url3 = "http://10.128.10.3:8080/wm/onos/metrics"
        url4 = "http://10.128.10.4:8080/wm/onos/metrics"

        f = open("/home/admin/TestON/tests/scaleONOS7nodes/logs/scale4nodesrate1", "a")
        #time.sleep(10)
        for i in range(int (loop)):
            json_str1 = main.ONOS1.get_json(url1)
            json_str2 = main.ONOS2.get_json(url2)
            json_str3 = main.ONOS3.get_json(url3)
            json_str4 = main.ONOS4.get_json(url4)
            if json_str1 != "" and json_str2 != "" and json_str3 != "" and json_str4 != "":
                # write_str = str(json_str["meters"][4]["meter"][2])
                #print str(json_str["meters"][4])
                #f.write(str(json_str["meters"][4]))
                #f.write('\n')
                #time.sleep(3)

                f.write("ONOS1 \n")
                f.write(str(json_str1["meters"][4]['meter']['count']))
                f.write('\t')
                f.write(str(json_str1["meters"][4]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str1["meters"][4]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str1["meters"][4]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str1["meters"][4]['meter']['mean_rate']))
                f.write('\n')

                f.write("ONOS2 \n")
                f.write(str(json_str2["meters"][4]['meter']['count']))
                f.write('\t')
                f.write(str(json_str2["meters"][4]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str2["meters"][4]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str2["meters"][4]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str2["meters"][4]['meter']['mean_rate']))
                f.write('\n')

                f.write("ONOS3 \n")
                f.write(str(json_str3["meters"][4]['meter']['count']))
                f.write('\t')
                f.write(str(json_str3["meters"][4]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str3["meters"][4]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str3["meters"][4]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str3["meters"][4]['meter']['mean_rate']))
                f.write('\n')

                f.write("ONOS4 \n")
                f.write(str(json_str4["meters"][4]['meter']['count']))
                f.write('\t')
                f.write(str(json_str4["meters"][4]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str4["meters"][4]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str4["meters"][4]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str4["meters"][4]['meter']['mean_rate']))
                f.write('\n')

                f.write('\n')
                
                time.sleep(sleep_t)
        f.close() 
        #main.Mininet2.handle.expect("\$", timeout=900)
        #main.Mininet2.handle.sendline("sudo mn -c")
        #main.Mininet2.handle.expect("\$")
        time.sleep(5)
        main.Mininet2.handle.expect("\$", timeout=900)
        

    def CASE7(self,main):
        
        ip1 = main.params['CTRL']['ip1']
        ip2 = main.params['CTRL']['ip2']
        ip3 = main.params['CTRL']['ip3']
        ip4 = main.params['CTRL']['ip4']
        
        import time
        import json
        rate2 = main.params['RATE2']
        run_dur = main.params['RUN_DUR']
        loop = int(main.params['loop'])
        sleep_t = int(main.params['sleep_t'])
        switches_num = main.params['switches_num']
        port = main.params['port']
        main.case("Starting SB load on 4 nodes from mininet with " + rate2 +"  added/removed/s for " + run_dur)
        #main.Mininet2.handle.sendline("./loadgen_SB.sh startload \"" + ip1 + " " + ip2 + " " + ip3 + " " + ip4 +  "\"" + " " + switches_num + " " + port +  " " + rate2 + " " + run_dur +  "  \"11\"")
        main.Mininet2.handle.sendline("sudo ./loadgen_SB.py -u \"" + ip1 + " " + ip2 + " " + ip3 + " " + ip4 +  "\"" + " -s " + switches_num + " -p " + port + " -a " + rate2 + " -d " + rate2 + " -l " + run_dur)
        main.Mininet2.handle.expect("Starting SB load....", timeout=900 )
        
        open("/home/admin/TestON/tests/scaleONOS7nodes/logs/scale4nodesrate2", 'w').close()
        url1 = "http://10.128.10.1:8080/wm/onos/metrics"
        url2 = "http://10.128.10.2:8080/wm/onos/metrics"
        url3 = "http://10.128.10.3:8080/wm/onos/metrics"
        url4 = "http://10.128.10.4:8080/wm/onos/metrics"
        f = open("/home/admin/TestON/tests/scaleONOS7nodes/logs/scale4nodesrate2", "a")
        #time.sleep(10)
        for i in range(int (loop)):
            json_str1 = main.ONOS1.get_json(url1)
            json_str2 = main.ONOS2.get_json(url2)
            json_str3 = main.ONOS3.get_json(url3)
            json_str4 = main.ONOS4.get_json(url4)
            if json_str1 != "" and json_str2 != "" and json_str3 != "" and json_str4 != "":

                f.write("ONOS1 \n")
                f.write(str(json_str1["meters"][4]['meter']['count']))
                f.write('\t')
                f.write(str(json_str1["meters"][4]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str1["meters"][4]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str1["meters"][4]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str1["meters"][4]['meter']['mean_rate']))
                f.write('\n')
                
                f.write("ONOS2 \n")
                f.write(str(json_str2["meters"][4]['meter']['count']))
                f.write('\t')
                f.write(str(json_str2["meters"][4]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str2["meters"][4]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str2["meters"][4]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str2["meters"][4]['meter']['mean_rate']))
                f.write('\n')
                
                f.write("ONOS3 \n")
                f.write(str(json_str3["meters"][4]['meter']['count']))
                f.write('\t')
                f.write(str(json_str3["meters"][4]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str3["meters"][4]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str3["meters"][4]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str3["meters"][4]['meter']['mean_rate']))
                f.write('\n')
                
                f.write("ONOS4 \n")
                f.write(str(json_str4["meters"][4]['meter']['count']))
                f.write('\t')
                f.write(str(json_str4["meters"][4]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str4["meters"][4]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str4["meters"][4]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str4["meters"][4]['meter']['mean_rate']))
                f.write('\n')

                f.write('\n')
                
                time.sleep(sleep_t)
        f.close()

    def CASE8(self,main):
        
        main.case("Starting NB Throughput test after scaling up to 4 onos nodes")
        ip1 = main.params['CTRL']['ip1']
        ip2 = main.params['CTRL']['ip2']
        ip3 = main.params['CTRL']['ip3']
        ip4 = main.params['CTRL']['ip4']

        import time
        import json

        main.Mininet4.handle.expect("\$")
        #main.Mininet2.handle.sendline("sudo mn --custom topo-intentTPtest.py --topo mytopo --mac --arp")
        #main.Mininet2.handle.expect("mininet>" , timeout=400)
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s1 tcp:10.128.10.1:6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s2 tcp:10.128.10.2:6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s3 tcp:10.128.10.3:6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s4 tcp:10.128.10.4:6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s5 tcp:10.128.10.1:6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s6 tcp:10.128.10.2:6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s7 tcp:10.128.10.4:6633")

        main.ONOS3.handle.sendline("cd ~admin/suibin-dev")
        main.ONOS3.handle.expect("\$")

        main.ONOS3.handle.sendline("./multiLoadgen_NB.py -u \"10.128.10.1:8080 10.128.10.2:8080 10.128.10.3:8080 10.128.10.4:8080  \" -i 4 -g 100 -a 1 -d 1 -p 0")
        main.ONOS3.handle.expect("intent group is : 0", timeout=900)

        
        import json
        
        open("/home/admin/TestON/tests/scaleONOS7nodes/logs/NBscale4nodesrate1", 'w').close()
        url1 = "http://10.128.10.1:8080/wm/onos/metrics"
        url2 = "http://10.128.10.2:8080/wm/onos/metrics"
        url3 = "http://10.128.10.3:8080/wm/onos/metrics"
        url4 = "http://10.128.10.4:8080/wm/onos/metrics"
        f = open("/home/admin/TestON/tests/scaleONOS7nodes/logs/NBscale4nodesrate1", "a")
        #time.sleep(10)
        for i in range(8):
            json_str1 = main.ONOS1.get_json(url1)
            json_str2 = main.ONOS2.get_json(url2)
            json_str3 = main.ONOS3.get_json(url3)
            json_str4 = main.ONOS4.get_json(url4)

            if json_str1 != "" and json_str2 != "" and json_str3 != "":
                f.write("ONOS1......IncomingRate \n ")
                f.write(str(json_str1["meters"][0]['meter']['count']))
                f.write('\t')
                f.write(str(json_str1["meters"][0]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str1["meters"][0]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str1["meters"][0]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str1["meters"][0]['meter']['mean_rate']))
                f.write('\n')
                f.write("ONOS2......IncomingRate \n")
                f.write(str(json_str2["meters"][0]['meter']['count']))
                f.write('\t')
                f.write(str(json_str2["meters"][0]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str2["meters"][0]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str2["meters"][0]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str2["meters"][0]['meter']['mean_rate']))
                f.write('\n')
                f.write("ONOS3......IncomingRate \n")
                f.write(str(json_str3["meters"][0]['meter']['count']))
                f.write('\t')
                f.write(str(json_str3["meters"][0]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str3["meters"][0]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str3["meters"][0]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str3["meters"][0]['meter']['mean_rate']))
                f.write('\n')
                f.write("ONOS4......IncomingRate \n")
                f.write(str(json_str4["meters"][0]['meter']['count']))
                f.write('\t')
                f.write(str(json_str4["meters"][0]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str4["meters"][0]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str4["meters"][0]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str4["meters"][0]['meter']['mean_rate']))
                f.write('\n')
                f.write('\n')

                f.write("--------------------------------------------------------------------------------- \n") 
                
                f.write("ONOS1......ProcessingRate \n ")
                f.write(str(json_str1["meters"][1]['meter']['count']))
                f.write('\t')
                f.write(str(json_str1["meters"][1]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str1["meters"][1]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str1["meters"][1]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str1["meters"][1]['meter']['mean_rate']))
                f.write('\n')
                f.write("ONOS2......ProcessingRate \n")
                f.write(str(json_str2["meters"][1]['meter']['count']))
                f.write('\t')
                f.write(str(json_str2["meters"][1]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str2["meters"][1]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str2["meters"][1]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str2["meters"][1]['meter']['mean_rate']))
                f.write('\n')
                f.write("ONOS3......ProcessingRate \n")
                f.write(str(json_str3["meters"][1]['meter']['count']))
                f.write('\t')
                f.write(str(json_str3["meters"][1]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str3["meters"][1]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str3["meters"][1]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str3["meters"][1]['meter']['mean_rate']))
                f.write('\n')

                f.write("ONOS4......ProcessingRate \n")
                f.write(str(json_str4["meters"][1]['meter']['count']))
                f.write('\t')
                f.write(str(json_str4["meters"][1]['meter']['m1_rate']))
                f.write('\t')
                f.write(str(json_str4["meters"][1]['meter']['m5_rate']))
                f.write('\t')
                f.write(str(json_str4["meters"][1]['meter']['m15_rate']))
                f.write('\t')
                f.write(str(json_str4["meters"][1]['meter']['mean_rate']))
                f.write('\n')

                f.write('\n')

                f.write("--------------------------------------------------------------------------------- \n") 
       
                time.sleep(10)
        f.close()

        main.ONOS3.handle.expect("\$", timeout=900)

