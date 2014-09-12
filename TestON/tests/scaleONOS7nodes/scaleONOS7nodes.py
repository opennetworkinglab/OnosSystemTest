#Author: Santhosh Jayashankar
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
        main.log.report("Starting 3-node ONOS cluster.")
        main.step("Stop ONOS")
        import time
        main.log.info("Stopping all ONOS nodes...")
        main.ONOS1.stop_all()
        main.ONOS2.stop_all()
        main.ONOS3.stop_all()
#        main.print_hello_world()
        main.ONOS4.stop_all()
        main.ONOS5.stop_all()
        main.ONOS6.stop_all()
        main.ONOS7.stop_all()
        #main.ONOS2.stop_rest()
        time.sleep(5)
        #main.ONOS1.handle.sendline("cp ~/onos.properties.proactive ~/ONOS/conf/onos.properties")
        #main.ONOS2.handle.sendline("cp ~/onos.properties.proactive ~/ONOS/conf/onos.properties")
        #main.ONOS3.handle.sendline("cp ~/onos.properties.proactive ~/ONOS/conf/onos.properties")
        #main.ONOS4.handle.sendline("cp ~/onos.properties.proactive ~/ONOS/conf/onos.properties")        
        #main.step("Start tcpdump on mn")
        #main.Mininet2.start_tcpdump(main.params['tcpdump']['filename'], intf = main.params['tcpdump']['intf'], port = main.params['tcpdump']['port'])
        main.step("Starting 3 ONOS nodes...")
        main.Zookeeper1.start()
        main.Zookeeper2.start()
        main.Zookeeper3.start()
        main.Zookeeper4.start()
        main.Zookeeper5.start()
        main.Zookeeper6.start()
        main.Zookeeper7.start()
        
        time.sleep(5)
        
        """        
        main.RamCloud1.del_db()
        main.RamCloud2.del_db()
        main.RamCloud3.del_db()
       # main.RamCloud4.del_db()

        time.sleep(5)
        #main.log.report("Pulling latest code from github to all nodes")
          
        
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

        
        main.RamCloud1.start_coor()
        main.RamCloud1.start_serv()
        main.RamCloud2.start_serv()
        main.RamCloud3.start_serv()
        time.sleep(5)
        main.ONOS1.start()
        main.ONOS2.start()
        main.ONOS3.start()
        #main.ONOS4.start()
        time.sleep(5)
        """
        main.ONOS1.handle.sendline("./onos.sh core start")
        main.ONOS2.handle.sendline("./onos.sh core start")
        main.ONOS3.handle.sendline("./onos.sh core start")

        main.ONOS1.start_rest()
        main.ONOS2.start_rest()
        main.ONOS3.start_rest()
        test= main.ONOS2.rest_status()
        if test == main.FALSE:
            main.ONOS1.start_rest()
        main.ONOS1.get_version()
        main.log.report("Startup check Zookeeper, and ONOS connections")
        main.step("Testing startup Zookeeper")   
        data =  main.Zookeeper1.isup() and main.Zookeeper2.isup() and main.Zookeeper3.isup()
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Zookeeper is up!",onfail="Zookeeper is down...")
        """
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
        """
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


    def CASE31(self,main):
        main.log.report("SB Throughput test: loading ONOS cluster with 740 Topo Events/s")
        main.case("Staring SB load with 3 ONOS nodes")
        ip1 = main.params['CTRL']['ip1']
        ip2 = main.params['CTRL']['ip2']
        ip3 = main.params['CTRL']['ip3']
        rate1 = main.params['RATE1']
        run_dur = main.params['RUN_DUR']
        loop = int( main.params['loop'])
        port = main.params['port']
        switches_num = main.params['switches_num']
        print loop
        sleep_init = int(main.params['sleep_init'])
        sleep_t =int( main.params['sleep_t'])
        main.case("Starting SB load on 3 nodes from mininet with " + rate1 +"  added/removed/s for " + run_dur)
        main.Mininet2.handle.sendline("sudo ./loadgen_SB.py -u \"" + ip1 + " " + ip2 + " " + ip3 + "\"" + " -s " + switches_num + " -p " + port + " -a " + rate1 + " -d " + rate1 + " -l " + run_dur)
        main.log.info("Adding switches and ports.....")
        main.Mininet2.handle.expect("Starting SB load....", timeout=400)
        main.log.info("Starting SB load....")
        import time
        import json
        import math
        time.sleep(sleep_init)
        open("/home/admin/TestON/tests/scaleONOS7nodes/logs/scale3nodesrate1", 'w').close()
        url1 = main.params['url1']
        url2 = main.params['url2']
        url3 = main.params['url3']
        f = open("/home/admin/TestON/tests/scaleONOS7nodes/logs/scale3nodesrate1", "a")
        #time.sleep(10)
        tpval = 0.0
        global tpavg3n
        tpavg3n = 0.0
        for i in range(int (loop)):
            j1 = main.ONOS2.get_json(url1)
            j2 = main.ONOS2.get_json(url2)
            j3 = main.ONOS2.get_json(url3)
            json_str = []
            json_str.append(0)
            json_str.append(j1)
            json_str.append(j2)
            json_str.append(j3)
            #float jval = 0
            if json_str[1] != "" and json_str[2] != "" and json_str[3] != "":
                # write_str = str(json_str["meters"][4]["meter"][2])
                #print str(json_str["meters"][4])
                #f.write(str(json_str["meters"][4]))
                #f.write('\n')
                #time.sleep(3)
                for j in range(1,4):
                    f.write("ONOS" + str(j) + "\n")
                    f.write(str(json_str[j]["meters"][4]['meter']['count']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][4]['meter']['m1_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][4]['meter']['m5_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][4]['meter']['m15_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][4]['meter']['mean_rate']))
                    f.write('\n')
                    if j == 3:
                        tpval += float(json_str[j]["meters"][4]['meter']['m1_rate']) 
                        #print tpval
                        #print ("\n")
                            
                
                f.write('\n')
                f.write('\n')
                
                f.write("--------------------------------------------------------------------------------- \n") 
                time.sleep(sleep_t)
        f.close() 
       # print tpval
        print("\n")
        tpavg3n = round(tpval)/loop
        print tpavg3n
        main.log.report("Topology Event Throughput for 3-node ONOS cluster = " +str(tpavg3n) + " Events/sec")
        main.Mininet2.handle.expect("\$", timeout=900)
        time.sleep(180)
        
    def CASE33(self,main):
        
        ip1 = main.params['CTRL']['ip1']
        ip2 = main.params['CTRL']['ip2']
        ip3 = main.params['CTRL']['ip3']
        import time
        import json
        int_num = int(main.params['int_num'])
        addrate = main.params['addrate']
        NBdur = main.params['NBdur']
        NBsleep = int(main.params['NBsleep'])
        NBsleep_init = int(main.params['NBsleep_init'])
        NBloop = int(main.params['NBloop'])
        int_r = 3 * int_num
        main.log.report("Starting NB Throughput test: loading 3-node ONOS cluster with " + str(int_num) + " Intents/s on each node" )
        main.Mininet4.handle.expect("\$")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s1 tcp:" + ip1 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s2 tcp:" + ip1 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s3 tcp:" + ip2 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s4 tcp:" + ip2 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s5 tcp:" + ip3 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s6 tcp:" + ip3 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s7 tcp:" + ip3 + ":6633")
        
        main.ONOS3.handle.sendline("cd ~admin/suibin-dev")
        main.ONOS3.handle.expect("\$")

        main.ONOS3.handle.sendline("./loadgen_NB.py -n 3 -u \"" + ip1 + ":8080 " + ip2 + ":8080 " + ip3 + ":8080 \" -i " + str(int_r) + " -a " + addrate + " -l " + NBdur + " -p 20")
        main.ONOS3.handle.expect("Pause between add and delete:", timeout=900)
        time.sleep(NBsleep_init)
        import json
        nbtpval = 0.0
        global nbtpavg3n
        nbtpavg3n = 0.0
        
        open("/home/admin/TestON/tests/scaleONOS7nodes/logs/NBscale3nodesrate1", 'w').close()
        url1 = main.params['url1']
        url2 = main.params['url2']
        url3 = main.params['url3']
        f = open("/home/admin/TestON/tests/scaleONOS7nodes/logs/NBscale3nodesrate1", "a")
        for i in range(NBloop):
            j1 = main.ONOS1.get_json(url1)
            j2 = main.ONOS1.get_json(url2)
            j3 = main.ONOS1.get_json(url3)
            json_str = []
            json_str.append(0)
            json_str.append(j1)
            json_str.append(j2)
            json_str.append(j3)
            if json_str[1] != "" and json_str[2] != "" and json_str[3] != "":
                for j in range(1,4):
                    f.write("*****************ONOS" + str(j) + " INCOMING RATE****************************" "\n")
                    f.write(str(json_str[j]["meters"][0]['meter']['count']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][0]['meter']['m1_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][0]['meter']['m5_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][0]['meter']['m15_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][0]['meter']['mean_rate']))
                    f.write('\n')
                
                    f.write('\n')

                    f.write("--------------------------------------------------------------------------------- \n") 
                
                    f.write("***************** ONOS" + str(j) + " PROCESSING RATE************************" + " \n ")
                    f.write(str(json_str[j]["meters"][1]['meter']['count']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][1]['meter']['m1_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][1]['meter']['m5_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][1]['meter']['m15_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][1]['meter']['mean_rate']))
                    f.write('\n')
                    f.write('\n')
                    f.write('\n')
                    nbtpval += float(json_str[j]["meters"][1]['meter']['m1_rate']) 

                    f.write("--------------------------------------------------------------------------------- \n") 
                    f.write("--------------------------------------------------------------------------------- \n \n") 
                    time.sleep(NBsleep)
        f.close()
        print("\n")
        nbtpavg3n = round(round(nbtpval)/NBloop,2)
        print nbtpavg3n
        
        main.ONOS3.handle.expect("\$", timeout=900)
        #time.sleep(180) 
        main.log.report("Intent Throughput for 3-node ONOS cluster = " + str(nbtpavg3n) + " Intents/sec")
        
    def CASE4(self,main):
        
        main.log.report("Scale-up ONOS to 4-nodes ")
        main.case("Starting ONOS scale-up to 4 nodes ")
        import time
       # main.RamCloud4.start_serv()
        main.ONOS5.handle.sendline("./onos.sh core stop")
        main.ONOS6.handle.sendline("./onos.sh core stop")
        main.ONOS7.handle.sendline("./onos.sh core stop")
    
            
        main.Zookeeper4.start()
        time.sleep(5)
        """ 
        main.RamCloud4.del_db()
        time.sleep(3)
        main.RamCloud4.start_serv()
        time.sleep(3)
        """
        main.ONOS4.start()
        main.ONOS4.start_rest()
        time.sleep(5)
        data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup() and main.ONOS4.isup()
        for i in range(3):
            if data == main.FALSE: 
                time.sleep(3)
                data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup() and main.ONOS4.isup()
            else:
                break
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Scale up successful - 4-node ONOS cluster is up and running!",onfail="ONOS didn't start...")
        
        time.sleep(10)
    
    def CASE5(self,main):
        main.log.report("Scale-up ONOS to 5-nodes")
        main.case("Starting ONOS scale-up/down to 5 nodes ")
        import time
        main.ONOS6.handle.sendline("./onos.sh core stop")
        main.ONOS7.handle.sendline("./onos.sh core stop")
    
        main.Zookeeper5.start()
        time.sleep(5)
        """
        main.RamCloud5.del_db()
        time.sleep(3)
        main.RamCloud5.start_serv()
        time.sleep(3)
        """
        main.ONOS5.start()
        main.ONOS5.start_rest()
        time.sleep(5)
        data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup() and main.ONOS4.isup() and main.ONOS5.isup()
        for i in range(3):
            if data == main.FALSE: 
                time.sleep(3)
                data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup() and main.ONOS4.isup() and main.ONOS5.isup() 
            else:
                break
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Scale up successful - 5-node ONOS cluster is up and running!",onfail="ONOS didn't start...")
        time.sleep(10)

    def CASE6(self,main):
        main.log.report("Scale-up ONOS to 6-nodes")
        main.case("Starting ONOS scale-up/down to 6 nodes ")
        import time
        main.ONOS7.handle.sendline("./onos.sh core stop")

        main.Zookeeper6.start()
        time.sleep(5)
        """
        main.RamCloud6.del_db()
        time.sleep(3)
        main.RamCloud6.start_serv()
        time.sleep(3)
        """
        main.ONOS6.start()
        main.ONOS6.start_rest()
        time.sleep(5)
        data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup() and main.ONOS4.isup() and main.ONOS5.isup() and main.ONOS6.isup()
        for i in range(3):
            if data == main.FALSE: 
                time.sleep(3)
                data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup() and main.ONOS4.isup() and main.ONOS5.isup() and main.ONOS6.isup()
            else:
                break
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Scale up successful - 6-node ONOS cluster is up and running!",onfail="ONOS didn't start...")
        time.sleep(10)

    def CASE7(self,main):
        main.log.report("Scale-up ONOS to 7-nodes")
        main.case("Starting ONOS scale-up/down to 7 nodes ")
        import time
    
        main.Zookeeper7.start()
        time.sleep(5)
        """
        main.RamCloud7.del_db()            
        time.sleep(3)
        main.RamCloud7.start_serv()
        time.sleep(3)
        """
        main.ONOS7.start()
        main.ONOS7.start_rest()
        time.sleep(5)
        data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup() and main.ONOS4.isup() and main.ONOS5.isup() and main.ONOS6.isup() and main.ONOS7.isup()
        for i in range(3):
            if data == main.FALSE: 
                time.sleep(3)
                data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup() and main.ONOS4.isup() and main.ONOS5.isup() and main.ONOS6.isup() and main.ONOS7.isup()
            else:
                break
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Scale up successful - 7-node ONOS cluster is up and running!",onfail="ONOS didn't start...")
        time.sleep(10)



    def CASE41(self,main):
        main.case("Starting SB test for 4 nodes")
        main.log.report("SB Throughput test: loading 4-node ONOS cluster with 740 Topo Events/s")
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
        sleep_init = int(main.params['sleep_init'])
        sleep_t =int( main.params['sleep_t'])
        main.case("Starting SB load on 4 nodes from mininet with " + rate1 +"  added/removed/s for " + run_dur)
        main.Mininet2.handle.sendline("sudo ./loadgen_SB.py -u \"" + ip1 + " " + ip2 + " " + ip3 + " " + ip4 +  "\"" + " -s " + switches_num + " -p " + port + " -a " + rate1 + " -d " + rate1 + " -l " + run_dur)
        main.Mininet2.handle.expect("Starting SB load....", timeout=900)
        import time
        import json
        import math
        time.sleep(sleep_init)
        open("/home/admin/TestON/tests/scaleONOS7nodes/logs/scale4nodesrate1", 'w').close()
        url1 = main.params['url1']
        url2 = main.params['url2']
        url3 = main.params['url3']
        url4 = main.params['url4']
        tpval = 0.0
        global tpavg4n 
        tpavg4n = 0.0

        f = open("/home/admin/TestON/tests/scaleONOS7nodes/logs/scale4nodesrate1", "a")
        for i in range(int (loop)):
            j1 = main.ONOS2.get_json(url1)
            j2 = main.ONOS2.get_json(url2)
            j3 = main.ONOS2.get_json(url3)
            j4 = main.ONOS2.get_json(url4)
            json_str = []
            json_str.append(0)
            json_str.append(j1)
            json_str.append(j2)
            json_str.append(j3)
            json_str.append(j4)
            if json_str[1] != "" and json_str[2] != "" and json_str[3] != "" and json_str[4] != "":
                for j in range(1,5):
                    f.write("ONOS" + str(j) + "\n")
                    f.write(str(json_str[j]["meters"][4]['meter']['count']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][4]['meter']['m1_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][4]['meter']['m5_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][4]['meter']['m15_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][4]['meter']['mean_rate']))
                    f.write('\n')
                    if j == 4:
                        tpval += float(json_str[j]["meters"][4]['meter']['m1_rate']) 
                
                f.write('\n')
                f.write('\n')
                
                f.write("--------------------------------------------------------------------------------- \n") 
                time.sleep(sleep_t)
        f.close() 
        print("\n")
        tpavg4n = round(tpval)/loop
        print tpavg4n
        main.log.report("Topology Event Throughput for 4-node ONOS cluster = " + str(tpavg4n) + " Events/sec")
        
        time.sleep(5)
        main.Mininet2.handle.expect("\$", timeout=900)
        time.sleep(180)
        

    def CASE43(self,main):
        
        main.case("Starting NB Throughput test after scaling up to 4 onos nodes")
        ip1 = main.params['CTRL']['ip1']
        ip2 = main.params['CTRL']['ip2']
        ip3 = main.params['CTRL']['ip3']
        ip4 = main.params['CTRL']['ip4']

        import time
        import json
        int_num = int(main.params['int_num'])
        addrate = main.params['addrate']
        NBdur = main.params['NBdur']
        NBsleep = int(main.params['NBsleep'])
        NBsleep_init = int(main.params['NBsleep_init'])
        NBloop = int(main.params['NBloop'])
        nbtpval = 0.0
        main.log.report("Starting NB Throughput test: loading 4-node ONOS cluster with " +str(int_num) + " Intents/s on each node" )
        global nbtpavg4n
        nbtpavg4n = 0.0
        int_r = 4 * int_num
        main.Mininet4.handle.expect("\$")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s1 tcp:" + ip1 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s2 tcp:" + ip2 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s3 tcp:" + ip3 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s4 tcp:" + ip4 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s5 tcp:" + ip1 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s6 tcp:" + ip2 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s7 tcp:" + ip4 + ":6633")
        
        main.ONOS3.handle.sendline("cd ~admin/suibin-dev")
        main.ONOS3.handle.expect("\$")

        main.ONOS3.handle.sendline("./loadgen_NB.py -n 4 -u \"" + ip1 + ":8080 " + ip2 + ":8080 " + ip3 + ":8080 " + ip4 + ":8080  \" -i " + str(int_r) + " -a " + addrate + " -l " + NBdur + " -p 20")
        main.ONOS3.handle.expect("Pause between add and delete:", timeout=900)

        
        time.sleep(NBsleep_init)
        import json
        
        open("/home/admin/TestON/tests/scaleONOS7nodes/logs/NBscale4nodesrate1", 'w').close()
        url1 = main.params['url1']
        url2 = main.params['url2']
        url3 = main.params['url3']
        url4 = main.params['url4']
        f = open("/home/admin/TestON/tests/scaleONOS7nodes/logs/NBscale4nodesrate1", "a")
        for i in range(NBloop):
            j1 = main.ONOS2.get_json(url1)
            j2 = main.ONOS2.get_json(url2)
            j3 = main.ONOS2.get_json(url3)
            j4 = main.ONOS2.get_json(url4)
            json_str = []
            json_str.append(0)
            json_str.append(j1)
            json_str.append(j2)
            json_str.append(j3)
            json_str.append(j4)
            if json_str[1] != "" and json_str[2] != "" and json_str[3] != "" and json_str[4] != "":
                for j in range(1,5):
                    f.write("*****************ONOS" + str(j) + " INCOMING RATE****************************" "\n")
                    f.write(str(json_str[j]["meters"][0]['meter']['count']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][0]['meter']['m1_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][0]['meter']['m5_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][0]['meter']['m15_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][0]['meter']['mean_rate']))
                    f.write('\n')
                
                    f.write('\n')

                    f.write("--------------------------------------------------------------------------------- \n") 
                
                    f.write("***************** ONOS" + str(j) + " PROCESSING RATE************************" + " \n ")
                    f.write(str(json_str[j]["meters"][1]['meter']['count']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][1]['meter']['m1_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][1]['meter']['m5_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][1]['meter']['m15_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][1]['meter']['mean_rate']))
                    f.write('\n')
                    f.write('\n')
                    f.write('\n')
                    
                    nbtpval += float(json_str[j]["meters"][1]['meter']['m1_rate']) 

                    f.write("--------------------------------------------------------------------------------- \n") 
                    f.write("--------------------------------------------------------------------------------- \n \n") 
                    time.sleep(NBsleep)
        f.close()
        print("\n")
        nbtpavg4n = round(round(nbtpval)/NBloop,2)
        print nbtpavg4n
        

        main.ONOS3.handle.expect("\$", timeout=900)
        time.sleep(180)
        main.log.report("Intent Throughput for 4-node ONOS cluster = " + str(nbtpavg4n) + " Intents/sec")
    
    def CASE51(self,main):
        main.case("Starting SB test for 5 nodes")
        main.log.report("SB Throughput test: loading 5-node ONOS cluster with 740 Topo Events/s")
        ip1 = main.params['CTRL']['ip1']
        ip2 = main.params['CTRL']['ip2']
        ip3 = main.params['CTRL']['ip3']
        ip4 = main.params['CTRL']['ip4']
        ip5 = main.params['CTRL']['ip5']
        rate1 = main.params['RATE1']
        run_dur = main.params['RUN_DUR']
        loop = int( main.params['loop'])
        switches_num = main.params['switches_num']
        port = main.params['port']
        print loop
        sleep_init = int(main.params['sleep_init'])
        sleep_t =int( main.params['sleep_t'])
        main.case("Starting SB load on 5 nodes from mininet with " + rate1 +"  added/removed/s for " + run_dur)
        main.Mininet2.handle.sendline("sudo ./loadgen_SB.py -u \"" + ip1 + " " + ip2 + " " + ip3 + " " + ip4 + " " + ip5 + "\"" + " -s " + switches_num + " -p " + port + " -a " + rate1 + " -d " + rate1 + " -l " + run_dur)
        main.Mininet2.handle.expect("Starting SB load....", timeout=900)
        import time
        import json
        tpval = 0.0
        global tpavg5n 
        tpavg5n = 0.0
        time.sleep(sleep_init)

        open("/home/admin/TestON/tests/scaleONOS7nodes/logs/scale5nodesrate1", 'w').close()
        url1 = main.params['url1']
        url2 = main.params['url2']
        url3 = main.params['url3']
        url4 = main.params['url4']
        url5 = main.params['url5']
        f = open("/home/admin/TestON/tests/scaleONOS7nodes/logs/scale5nodesrate1", "a")
        for i in range(int (loop)):
            j1 = main.ONOS2.get_json(url1)
            j2 = main.ONOS2.get_json(url2)
            j3 = main.ONOS2.get_json(url3)
            j4 = main.ONOS2.get_json(url4)
            j5 = main.ONOS2.get_json(url5)
            json_str = []
            json_str.append(0)
            json_str.append(j1)
            json_str.append(j2)
            json_str.append(j3)
            json_str.append(j4)
            json_str.append(j5)
            if json_str[1] != "" and json_str[2] != "" and json_str[3] != "" and json_str[4] != "" and json_str[5] != "":
                for j in range(1,6):
                    f.write("ONOS" + str(j) + "\n")
                    f.write(str(json_str[j]["meters"][4]['meter']['count']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][4]['meter']['m1_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][4]['meter']['m5_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][4]['meter']['m15_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][4]['meter']['mean_rate']))
                    f.write('\n')
                    if j == 4:
                        tpval += float(json_str[j]["meters"][4]['meter']['m1_rate']) 
                
                f.write('\n')
                f.write('\n')
                
                f.write("--------------------------------------------------------------------------------- \n") 
                time.sleep(sleep_t)
        f.close() 
        print("\n")
        tpavg5n = round(tpval)/loop
        print tpavg5n
        
        time.sleep(5)
        main.Mininet2.handle.expect("\$", timeout=900)
        time.sleep(180)
        main.log.report("Topology Event Throughput for 5-node ONOS cluster = " + str(tpavg5n) + " Events/sec")
        

    def CASE53(self,main):
        
        main.case("Starting NB Throughput test after scaling up to 5 onos nodes")
        ip1 = main.params['CTRL']['ip1']
        ip2 = main.params['CTRL']['ip2']
        ip3 = main.params['CTRL']['ip3']
        ip4 = main.params['CTRL']['ip4']
        ip5 = main.params['CTRL']['ip5']

        import time
        import json
        int_num = int(main.params['int_num'])
        addrate = main.params['addrate']
        NBdur = main.params['NBdur']
        NBsleep = int(main.params['NBsleep'])
        NBsleep_init = int(main.params['NBsleep_init'])
        NBloop = int(main.params['NBloop'])
        nbtpval = 0.0
        main.log.report("Starting NB Throughput test: loading 5-node ONOS cluster with " + str(int_num) + " Intents/s on each node" )
        global nbtpavg5n
        nbtpavg5n = 0.0
        int_r = 5 * int_num
        main.Mininet4.handle.expect("\$")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s1 tcp:" + ip1 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s2 tcp:" + ip2 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s3 tcp:" + ip3 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s4 tcp:" + ip4 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s5 tcp:" + ip5 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s6 tcp:" + ip3 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s7 tcp:" + ip5 + ":6633")
        
        main.ONOS3.handle.sendline("cd ~admin/suibin-dev")
        main.ONOS3.handle.expect("\$")

        main.ONOS3.handle.sendline("./loadgen_NB.py -n 5 -u \"" + ip1 + ":8080 " + ip2 + ":8080 " + ip3 + ":8080 " + ip4 + ":8080 " + ip5 + ":8080  \" -i " + str(int_r) + " -a " + addrate + " -l " + NBdur + " -p 20")
        main.ONOS3.handle.expect("Pause between add and delete:", timeout=900)

        
        time.sleep(NBsleep_init)
        import json
        
        open("/home/admin/TestON/tests/scaleONOS7nodes/logs/NBscale5nodesrate1", 'w').close()
        url1 = main.params['url1']
        url2 = main.params['url2']
        url3 = main.params['url3']
        url4 = main.params['url4']
        url5 = main.params['url5']
        f = open("/home/admin/TestON/tests/scaleONOS7nodes/logs/NBscale5nodesrate1", "a")
        for i in range(NBloop):
            j1 = main.ONOS2.get_json(url1)
            j2 = main.ONOS2.get_json(url2)
            j3 = main.ONOS2.get_json(url3)
            j4 = main.ONOS2.get_json(url4)
            j5 = main.ONOS2.get_json(url5)
            json_str = []
            json_str.append(0)
            json_str.append(j1)
            json_str.append(j2)
            json_str.append(j3)
            json_str.append(j4)
            json_str.append(j5)
            if json_str[1] != "" and json_str[2] != "" and json_str[3] != "" and json_str[4] != "" and json_str[5] != "":
                for j in range(1,6):
                    f.write("*****************ONOS" + str(j) + " INCOMING RATE****************************" "\n")
                    f.write(str(json_str[j]["meters"][0]['meter']['count']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][0]['meter']['m1_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][0]['meter']['m5_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][0]['meter']['m15_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][0]['meter']['mean_rate']))
                    f.write('\n')
                
                    f.write('\n')

                    f.write("--------------------------------------------------------------------------------- \n") 
                
                    f.write("***************** ONOS" + str(j) + " PROCESSING RATE************************" + " \n ")
                    f.write(str(json_str[j]["meters"][1]['meter']['count']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][1]['meter']['m1_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][1]['meter']['m5_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][1]['meter']['m15_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][1]['meter']['mean_rate']))
                    f.write('\n')
                    f.write('\n')
                    f.write('\n')
                    
                    nbtpval += float(json_str[j]["meters"][1]['meter']['m1_rate']) 


                    f.write("--------------------------------------------------------------------------------- \n") 
                    f.write("--------------------------------------------------------------------------------- \n \n") 
                    time.sleep(NBsleep)
        f.close()
        print("\n")
        nbtpavg5n = round(round(nbtpval)/NBloop,2)
        print nbtpavg5n
        

        main.ONOS3.handle.expect("\$", timeout=900)
        time.sleep(180)
        main.log.report("Intent Throughput for 5-node ONOS cluster = " + str(nbtpavg5n) + " Intents/sec")
    
    def CASE61(self,main):
        main.case("Starting SB test for 5 nodes")
        ip1 = main.params['CTRL']['ip1']
        main.log.report("SB Throughput test: loading 6-node ONOS cluster with 740 Topo Events/s")
        ip2 = main.params['CTRL']['ip2']
        ip3 = main.params['CTRL']['ip3']
        ip4 = main.params['CTRL']['ip4']
        ip5 = main.params['CTRL']['ip5']
        ip6 = main.params['CTRL']['ip6']
        rate1 = main.params['RATE1']
        run_dur = main.params['RUN_DUR']
        loop = int( main.params['loop'])
        switches_num = main.params['switches_num']
        port = main.params['port']
        print loop
        sleep_t =int( main.params['sleep_t'])
        sleep_init = int(main.params['sleep_init'])
        main.case("Starting SB load on 6 nodes from mininet with " + rate1 +"  added/removed/s for " + run_dur)
        main.Mininet2.handle.sendline("sudo ./loadgen_SB.py -u \"" + ip1 + " " + ip2 + " " + ip3 + " " + ip4 + " " + ip5 + " " + ip6 +  "\"" + " -s " + switches_num + " -p " + port + " -a " + rate1 + " -d " + rate1 + " -l " + run_dur)
        main.Mininet2.handle.expect("Starting SB load....", timeout=900)
        
        import time
        import json
        tpval = 0.0
        global tpavg6n
        tpavg6n = 0.0
        time.sleep(sleep_init)
        open("/home/admin/TestON/tests/scaleONOS7nodes/logs/scale6nodesrate1", 'w').close()
        url1 = main.params['url1']
        url2 = main.params['url2']
        url3 = main.params['url3']
        url4 = main.params['url4']
        url5 = main.params['url5']
        url6 = main.params['url6']
        f = open("/home/admin/TestON/tests/scaleONOS7nodes/logs/scale6nodesrate1", "a")
        for i in range(int (loop)):
            j1 = main.ONOS2.get_json(url1)
            j2 = main.ONOS2.get_json(url2)
            j3 = main.ONOS2.get_json(url3)
            j4 = main.ONOS2.get_json(url4)
            j5 = main.ONOS2.get_json(url5)
            j6 = main.ONOS2.get_json(url6)
            json_str = []
            json_str.append(0)
            json_str.append(j1)
            json_str.append(j2)
            json_str.append(j3)
            json_str.append(j4)
            json_str.append(j5)
            json_str.append(j6)
            if json_str[1] != "" and json_str[2] != "" and json_str[3] != "" and json_str[4] != "" and json_str[5] != "" and json_str[6] != "":
                for j in range(1,7):
                    f.write("ONOS" + str(j) + "\n")
                    f.write(str(json_str[j]["meters"][4]['meter']['count']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][4]['meter']['m1_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][4]['meter']['m5_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][4]['meter']['m15_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][4]['meter']['mean_rate']))
                    f.write('\n')
                    if j == 4:
                        tpval += float(json_str[j]["meters"][4]['meter']['m1_rate']) 
                
                f.write('\n')
                f.write('\n')
                
                f.write("--------------------------------------------------------------------------------- \n") 
                time.sleep(sleep_t)
        f.close() 
        print("\n")
        tpavg6n = round(tpval)/loop
        print tpavg6n
        
        time.sleep(5)
        main.Mininet2.handle.expect("\$", timeout=900)
        time.sleep(180)
        main.log.report("Topology Event Throughput for 6-node ONOS cluster = " + str(tpavg6n) + " Events/sec")
        

    def CASE63(self,main):
        
        main.case("Starting NB Throughput test after scaling up to 4 onos nodes")
        ip1 = main.params['CTRL']['ip1']
        ip2 = main.params['CTRL']['ip2']
        ip3 = main.params['CTRL']['ip3']
        ip4 = main.params['CTRL']['ip4']
        ip5 = main.params['CTRL']['ip5']
        ip6 = main.params['CTRL']['ip6']

        import time
        import json
        int_num = int(main.params['int_num'])
        addrate = main.params['addrate']
        NBdur = main.params['NBdur']
        NBsleep = int(main.params['NBsleep'])
        NBsleep_init = int(main.params['NBsleep_init'])
        NBloop = int(main.params['NBloop'])
        nbtpval = 0.0
        main.log.report("Starting NB Throughput test: loading 6-node ONOS cluster with " + str(int_num) + " Intents/s" )
        global nbtpavg6n
        nbtpavg6n = 0.0
        int_r = 6 * int_num
        main.Mininet4.handle.expect("\$")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s1 tcp:" + ip1 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s2 tcp:" + ip2 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s3 tcp:" + ip3 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s4 tcp:" + ip4 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s5 tcp:" + ip5 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s6 tcp:" + ip6 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s7 tcp:" + ip6 + ":6633")
        
        main.ONOS3.handle.sendline("cd ~admin/suibin-dev")
        main.ONOS3.handle.expect("\$")

        main.ONOS3.handle.sendline("./loadgen_NB.py -n 6 -u \"" + ip1 + ":8080 " + ip2 + ":8080 " + ip3 + ":8080 " + ip4 + ":8080 " + ip5 + ":8080 " + ip6 + ":8080 \" -i " + str(int_r) + " -a " + addrate + " -l " + NBdur + " -p 20")
        main.ONOS3.handle.expect("Pause between add and delete:", timeout=900)

        
        time.sleep(NBsleep_init)
        import json
        
        open("/home/admin/TestON/tests/scaleONOS7nodes/logs/NBscale6nodesrate1", 'w').close()
        url1 = main.params['url1']
        url2 = main.params['url2']
        url3 = main.params['url3']
        url4 = main.params['url4']
        url5 = main.params['url5']
        url6 = main.params['url6']
        f = open("/home/admin/TestON/tests/scaleONOS7nodes/logs/NBscale6nodesrate1", "a")
        for i in range(NBloop):
            j1 = main.ONOS2.get_json(url1)
            j2 = main.ONOS2.get_json(url2)
            j3 = main.ONOS2.get_json(url3)
            j4 = main.ONOS2.get_json(url4)
            j5 = main.ONOS2.get_json(url5)
            j6 = main.ONOS2.get_json(url6)
            json_str = []
            json_str.append(0)
            json_str.append(j1)
            json_str.append(j2)
            json_str.append(j3)
            json_str.append(j4)
            json_str.append(j5)
            json_str.append(j6)
            if json_str[1] != "" and json_str[2] != "" and json_str[3] != "" and json_str[4] != "" and json_str[5] != "" and json_str[6] != "":
                for j in range(1,7):
                    f.write("*****************ONOS" + str(j) + " INCOMING RATE****************************" "\n")
                    f.write(str(json_str[j]["meters"][0]['meter']['count']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][0]['meter']['m1_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][0]['meter']['m5_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][0]['meter']['m15_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][0]['meter']['mean_rate']))
                    f.write('\n')
                
                    f.write('\n')

                    f.write("--------------------------------------------------------------------------------- \n") 
                
                    f.write("***************** ONOS" + str(j) + " PROCESSING RATE************************" + " \n ")
                    f.write(str(json_str[j]["meters"][1]['meter']['count']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][1]['meter']['m1_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][1]['meter']['m5_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][1]['meter']['m15_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][1]['meter']['mean_rate']))
                    f.write('\n')
                    f.write('\n')
                    f.write('\n')
                    
                    nbtpval += float(json_str[j]["meters"][1]['meter']['m1_rate']) 


                    f.write("--------------------------------------------------------------------------------- \n") 
                    f.write("--------------------------------------------------------------------------------- \n \n") 
                    time.sleep(NBsleep)
        f.close()
        print("\n")
        nbtpavg6n = round(round(nbtpval)/NBloop,2)
        print nbtpavg6n
        
        

        main.ONOS3.handle.expect("\$", timeout=900)
        time.sleep(180)
        main.log.report("Intent Throughput for 6-node ONOS cluster = " + str(nbtpavg6n) + " Intents/sec")
    
    def CASE71(self,main):
        main.case("Starting SB test for 7 nodes")
        main.log.report("SB Throughput test: loading 7-node ONOS cluster with 740 Topo Events/s")
        ip1 = main.params['CTRL']['ip1']
        ip2 = main.params['CTRL']['ip2']
        ip3 = main.params['CTRL']['ip3']
        ip4 = main.params['CTRL']['ip4']
        ip5 = main.params['CTRL']['ip5']
        ip6 = main.params['CTRL']['ip6']
        ip7 = main.params['CTRL']['ip7']
        rate1 = main.params['RATE1']
        run_dur = main.params['RUN_DUR']
        loop = int( main.params['loop'])
        switches_num = main.params['switches_num']
        port = main.params['port']
        print loop
        sleep_t =int( main.params['sleep_t'])
        sleep_init = int(main.params['sleep_init'])
        main.case("Starting SB load on 6 nodes from mininet with " + rate1 +"  added/removed/s for " + run_dur)
        main.Mininet2.handle.sendline("sudo ./loadgen_SB.py -u \"" + ip1 + " " + ip2 + " " + ip3 + " " + ip4 + " " + ip5 +  " " + ip6 + " " + ip7 + "\"" + " -s " + switches_num + " -p " + port + " -a " + rate1 + " -d " + rate1 + " -l " + run_dur)
        main.Mininet2.handle.expect("Starting SB load....", timeout=900)
        import time
        import json
        tpval = 0.0
        global tpavg7n
        tpavg7n = 0.0
        time.sleep(sleep_init)
        
        open("/home/admin/TestON/tests/scaleONOS7nodes/logs/scale7nodesrate1", 'w').close()
        url1 = main.params['url1']
        url2 = main.params['url2']
        url3 = main.params['url3']
        url4 = main.params['url4']
        url5 = main.params['url5']
        url6 = main.params['url6']
        url7 = main.params['url7']

        f = open("/home/admin/TestON/tests/scaleONOS7nodes/logs/scale7nodesrate1", "a")
        for i in range(int (loop)):
            j1 = main.ONOS2.get_json(url1)
            j2 = main.ONOS2.get_json(url2)
            j3 = main.ONOS2.get_json(url3)
            j4 = main.ONOS2.get_json(url4)
            j5 = main.ONOS2.get_json(url5)
            j6 = main.ONOS2.get_json(url6)
            j7 = main.ONOS2.get_json(url7)
            json_str = []
            json_str.append(0)
            json_str.append(j1)
            json_str.append(j2)
            json_str.append(j3)
            json_str.append(j4)
            json_str.append(j5)
            json_str.append(j6)
            json_str.append(j7)
            if json_str[1] != "" and json_str[2] != "" and json_str[3] != "" and json_str[4] != "" and json_str[5] != "" and json_str[6] != "" and json_str[7] != "":
                for j in range(1,8):
                    f.write("ONOS" + str(j) + "\n")
                    f.write(str(json_str[j]["meters"][4]['meter']['count']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][4]['meter']['m1_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][4]['meter']['m5_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][4]['meter']['m15_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][4]['meter']['mean_rate']))
                    f.write('\n')
                    if j == 4:
                        tpval += float(json_str[j]["meters"][4]['meter']['m1_rate']) 
                
                f.write('\n')
                f.write('\n')
                
                f.write("--------------------------------------------------------------------------------- \n") 
                time.sleep(sleep_t)
        f.close() 
        print("\n")
        tpavg7n = round(tpval)/loop
        print tpavg7n
        
        time.sleep(5)
        main.Mininet2.handle.expect("\$", timeout=900)
        time.sleep(180)
        main.log.report("Topology Event Throughput for 7-node ONOS cluster = " + str(tpavg7n) + " Events/sec")
        

    def CASE73(self,main):
        
        main.case("Starting NB Throughput test after scaling up to 7 onos nodes")
        ip1 = main.params['CTRL']['ip1']
        ip2 = main.params['CTRL']['ip2']
        ip3 = main.params['CTRL']['ip3']
        ip4 = main.params['CTRL']['ip4']
        ip5 = main.params['CTRL']['ip5']
        ip6 = main.params['CTRL']['ip6']
        ip7 = main.params['CTRL']['ip7']

        import time
        import json
        int_num = int(main.params['int_num'])
        addrate = main.params['addrate']
        NBdur = main.params['NBdur']
        NBsleep = int(main.params['NBsleep'])
        NBsleep_init = int(main.params['NBsleep_init'])
        NBloop = int(main.params['NBloop'])
        main.log.report("Starting NB Throughput test: loading 7-node ONOS cluster with " + str(int_num) + " Intents/s" )
        nbtpval = 0.0
        global nbtpavg7n
        nbtpavg7n = 0.0
        int_r = 7 * int_num
        main.Mininet4.handle.expect("\$")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s1 tcp:" + ip1 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s2 tcp:" + ip2 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s3 tcp:" + ip3 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s4 tcp:" + ip4 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s5 tcp:" + ip5 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s6 tcp:" + ip6 + ":6633")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s7 tcp:" + ip7 + ":6633")
        
        main.ONOS3.handle.sendline("cd ~admin/suibin-dev")
        main.ONOS3.handle.expect("\$")

        main.ONOS3.handle.sendline("./loadgen_NB.py -n 7 -u \"" + ip1 + ":8080 " + ip2 + ":8080 " + ip3 + ":8080 " + ip4 + ":8080 " + ip6 + ":8080 " + ip5 + ":8080 " + ip7 + ":8080  \" -i " + str(int_r) + " -a " + addrate + " -l " + NBdur + " -p 20")
        main.ONOS3.handle.expect("Pause between add and delete:", timeout=900)

        
        time.sleep(NBsleep_init)
        import json
        
        open("/home/admin/TestON/tests/scaleONOS7nodes/logs/NBscale7nodesrate1", 'w').close()
        url1 = main.params['url1']
        url2 = main.params['url2']
        url3 = main.params['url3']
        url4 = main.params['url4']
        url5 = main.params['url5']
        url6 = main.params['url6']
        url7 = main.params['url7']
        f = open("/home/admin/TestON/tests/scaleONOS7nodes/logs/NBscale7nodesrate1", "a")
        for i in range(NBloop):
            j1 = main.ONOS2.get_json(url1)
            j2 = main.ONOS2.get_json(url2)
            j3 = main.ONOS2.get_json(url3)
            j4 = main.ONOS2.get_json(url4)
            j5 = main.ONOS2.get_json(url5)
            j6 = main.ONOS2.get_json(url6)
            j7 = main.ONOS2.get_json(url7)
            json_str = []
            json_str.append(0)
            json_str.append(j1)
            json_str.append(j2)
            json_str.append(j3)
            json_str.append(j4)
            json_str.append(j5)
            json_str.append(j6)
            json_str.append(j7)
            if json_str[1] != "" and json_str[2] != "" and json_str[3] != "" and json_str[4] != "" and json_str[5] != "" and json_str[6] != "" and json_str[6] != "":
                for j in range(1,8):
                    f.write("*****************ONOS" + str(j) + " INCOMING RATE****************************" "\n")
                    f.write(str(json_str[j]["meters"][0]['meter']['count']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][0]['meter']['m1_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][0]['meter']['m5_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][0]['meter']['m15_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][0]['meter']['mean_rate']))
                    f.write('\n')
                
                    f.write('\n')

                    f.write("--------------------------------------------------------------------------------- \n") 
                
                    f.write("***************** ONOS" + str(j) + " PROCESSING RATE************************" + " \n ")
                    f.write(str(json_str[j]["meters"][1]['meter']['count']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][1]['meter']['m1_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][1]['meter']['m5_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][1]['meter']['m15_rate']))
                    f.write('\t')
                    f.write(str(json_str[j]["meters"][1]['meter']['mean_rate']))
                    f.write('\n')
                    f.write('\n')
                    f.write('\n')
                    
                    nbtpval += float(json_str[j]["meters"][1]['meter']['m1_rate']) 


                    f.write("--------------------------------------------------------------------------------- \n") 
                    f.write("--------------------------------------------------------------------------------- \n \n") 
                    time.sleep(NBsleep)
        f.close()
        print("\n")
        nbtpavg7n = round(round(nbtpval)/NBloop,2)
        print nbtpavg7n
        

        main.ONOS3.handle.expect("\$", timeout=900)
        time.sleep(180)
        main.log.report("Intent Throughput for 7-node ONOS cluster = " + str(nbtpavg7n) + " Intents/sec")
    
    def CASE8(self,main):
        import time
        main.log.report("Scaling ONOS down to 6 ONOS instances")
        main.ONOS7.handle.sendline("./onos.sh core stop")
        time.sleep(8)
        pdata = main.ONOS7.isup()
        utilities.assert_equals(expect=main.FALSE,actual=pdata,onpass="ONOS7 stopped... ",onfail="ONOS scale down failed...")
        time.sleep(3)
        data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup() and main.ONOS4.isup() and main.ONOS5.isup() and main.ONOS6.isup()
        for i in range(3):
            if data == main.FALSE: 
                time.sleep(3)
                data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup() and main.ONOS4.isup() and main.ONOS5.isup() and main.ONOS6.isup()
            else:
                break
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Scale down successfull -6-node ONOS cluster is up and running!",onfail="ONOS didn't start...")
    
    def CASE9(self,main):

        main.log.report("Scaling ONOS down to 5 ONOS instances")
        main.ONOS6.handle.sendline("./onos.sh core stop")
        time.sleep(8)
        pdata = main.ONOS6.isup() and main.ONOS7.isup()
        utilities.assert_equals(expect=main.FALSE,actual=pdata,onpass="ONOS7 stopped... ",onfail="ONOS scale down failed...")
        data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup() and main.ONOS4.isup() and main.ONOS5.isup()
        for i in range(3):
            if data == main.FALSE: 
                time.sleep(3)
                data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup() and main.ONOS4.isup() and main.ONOS5.isup()
            else:
                break
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Scale down successfull - 5 node ONOS clsuter is up and running!",onfail="ONOS didn't start...")

    def CASE10(self,main):

        main.log.report("Scaling ONOS down to 4 ONOS instances")
        
        main.ONOS5.handle.sendline("./onos.sh core stop ")
        time.sleep(5)
        pdata = main.ONOS5.isup() and main.ONOS6.isup() and main.ONOS7.isup()
        utilities.assert_equals(expect=main.FALSE,actual=pdata,onpass="ONOS7 stopped... ",onfail="ONOS scale down failed...")
        data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup() and main.ONOS4.isup()
        for i in range(3):
            if data == main.FALSE: 
                time.sleep(3)
                data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup() and main.ONOS4.isup()
            else:
                break
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Scale down successful - 4 node ONOS cluster is up and running!",onfail="ONOS didn't start...")

    def CASE11(self,main):

        main.log.report("Scaling ONOS down to 3 ONOS instances")
        main.ONOS4.handle.sendline("./onos.sh core stop ")
        time.sleep(5)
        pdata = main.ONOS4.isup() and main.ONOS5.isup() and  main.ONOS6.isup() and main.ONOS7.isup()
        utilities.assert_equals(expect=main.FALSE,actual=pdata,onpass="ONOS7 stopped... ",onfail="ONOS scale down failed...")
        data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup()
        for i in range(3):
            if data == main.FALSE: 
                time.sleep(3)
                data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup()
            else:
                break
        utilities.assert_equals(expect=main.TRUE,actual=data,onpass="Scale down successful - 3 node ONOS cluster is up and running!",onfail="ONOS didn't start...")

    def CASE100(self,main):
        import os
        import time
        global timestr
        timestr = time.strftime("%Y%m%d-%H%M%S")
        main.case("Scale-up tests complete...now making final changes")
        main.log.info("moving logs....")
        os.system("sudo mkdir ~admin/TestON/tests/scaleONOS7nodes/logs/ONOSscale_up" + timestr + "")
        os.system("sudo mkdir ~admin/TestON/tests/scaleONOS7nodes/logs/NBONOSscale_up" + timestr + "")
        time.sleep(2)
        os.system("sudo  cp ~admin/TestON/tests/scaleONOS7nodes/logs/scale* ~admin/TestON/tests/scaleONOS7nodes/logs/ONOSscale_up" + timestr + "")
        os.system("sudo  cp ~admin/TestON/tests/scaleONOS7nodes/logs/NBscale* ~admin/TestON/tests/scaleONOS7nodes/logs/NBONOSscale_up" + timestr + "")
        time.sleep(2)
        os.system("sudo rm ~admin/TestON/tests/scaleONOS7nodes/logs/*")
        time.sleep(180)
                        
    def CASE101(self,main):
        
        import os
        import time
        main.case("Scale-down tests complete...now making final changes")
        global timestr
        main.case("Scale-down tests complete...now making final changes")
        main.log.info("moving logs....")
        os.system("sudo mkdir ~admin/TestON/tests/scaleONOS7nodes/logs/ONOSscale_dwn" + timestr + "")
        os.system("sudo mkdir ~admin/TestON/tests/scaleONOS7nodes/logs/NBONOSscale_dwn" + timestr + "")
        time.sleep(2)
        os.system("sudo  cp ~admin/TestON/tests/scaleONOS7nodes/logs/scale* ~admin/TestON/tests/scaleONOS7nodes/logs/ONOSscale_dwn" + timestr + "")
        os.system("sudo  cp ~admin/TestON/tests/scaleONOS7nodes/logs/NBscale* ~admin/TestON/tests/scaleONOS7nodes/logs/NBONOSscale_dwn" + timestr + "")
        time.sleep(2)
        os.system("sudo rm ~admin/TestON/tests/scaleONOS7nodes/logs/*")
        time.sleep(2)

    def CASE103(self,main):
        import os
        import time
        main.log.report("Posting the results to http://10.128.5.54/scale.html")
        db_script = main.params['db_script']
        os.system(db_script + " -n='100SwitchScaleUp" + "' -rate3='" + str(tpavg3n) + "' -rate4='" + str(tpavg4n) + "' -rate5='" + str(tpavg5n) + "' -rate6='" + str(tpavg6n) + "' -rate7='" + str(tpavg7n) + "' -table='onos_scale'")
        main.log.report("The graphical view of the tests can be viewed at http://10.128.5.54/scale.html")
    
    def CASE104(self,main):
        import os
        import time
        main.log.report("Posting the results to http://10.128.5.54/scale.html ....")
        db_script = main.params['db_script']
        os.system(db_script + " -n='100SwitchScaleDown" + "' -rate3='" + str(tpavg3n) + "' -rate4='" + str(tpavg4n) + "' -rate5='" + str(tpavg5n) + "' -rate6='" + str(tpavg6n) + "' -rate7='" + str(tpavg7n) + "' -table='onos_scale'")

        main.log.report("The graphical view of the tests can be viewed at http://10.128.5.54/scale.html")

    def CASE105(self,main):
        import os
        import time
        main.log.report("Posting the results to http://10.128.5.54/scale.html ....")
        db_script = main.params['db_script']
        os.system(db_script + " -n='1000IntentsScaleUp" + "' -rate3='" + str(nbtpavg3n) + "' -rate4='" + str(nbtpavg4n) + "' -rate5='" + str(nbtpavg5n) + "' -rate6='" + str(nbtpavg6n) + "' -rate7='" + str(nbtpavg7n) + "' -table='onos_scale'")

        main.log.report("The graphical view of the tests can be viewed at http://10.128.5.54/scale.html")

    def CASE106(self,main):
        import os
        import time
        main.log.report("Posting the results to http://10.128.5.54/scale.html ....")
        db_script = main.params['db_script']
        os.system(db_script + " -n='1000IntentsScaleDown" + "' -rate3='" + str(nbtpavg3n) + "' -rate4='" + str(nbtpavg4n) + "' -rate5='" + str(nbtpavg5n) + "' -rate6='" + str(nbtpavg6n) + "' -rate7='" + str(nbtpavg7n) + "' -table='onos_scale'")

        main.log.report("The graphical view of the tests can be viewed at http://10.128.5.54/scale.html")


