class scaleONOS7nodes :

    def __init__(self) :
        self.default = ''

#Test startup
#Tests the startup of Zookeeper1, RamCloud1, and ONOS1 to be certain that all started up successfully
    def CASE1(self,main) :  #Check to be sure ZK, Cass, and ONOS are up, then get ONOS version 
        import time

        main.case("Initial setup")
        main.log.report("Starting 3-node ONOS cluster.")
        
        main.step("Stop ONOS")
        
        main.log.info("Stopping all ONOS nodes...")
        main.ONOS1.stop_all()
        main.ONOS2.stop_all()
        main.ONOS3.stop_all()
        main.ONOS4.stop_all()
        main.ONOS5.stop_all()
        main.ONOS6.stop_all()
        main.ONOS7.stop_all()
        #main.ONOS2.stop_rest()
        time.sleep(5)
        
        main.step("Starting 3 ONOS nodes...")
        main.Zookeeper1.start()
        main.Zookeeper2.start()
        main.Zookeeper3.start()
        main.Zookeeper4.start()
        main.Zookeeper5.start()
        main.Zookeeper6.start()
        main.Zookeeper7.start()
        
        time.sleep(5)
        
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
        utilities.assert_equals(expect=main.TRUE,actual=data,
                onpass="Zookeeper is up!",
                onfail="Zookeeper is down...")
        
        main.step("Testing startup ONOS")   
        data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup()
        for i in range(3):
            if data == main.FALSE: 
                time.sleep(3)
                data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup() 
            else:
                break
        utilities.assert_equals(expect=main.TRUE,actual=data,
                onpass="ONOS is up and running!",
                onfail="ONOS didn't start...")
        time.sleep(10)
        
    def CASE4(self,main):
        import time 
        main.log.report("Scale-up ONOS to 4-nodes ")
        main.case("Starting ONOS scale-up to 4 nodes ")
      
        #Restart all ONOS core
        main.ONOS5.handle.sendline("./onos.sh core stop")
        main.ONOS6.handle.sendline("./onos.sh core stop")
        main.ONOS7.handle.sendline("./onos.sh core stop")
        
        #Start zookeeper 4 to prepare for ONOS4
        main.Zookeeper4.start()
        time.sleep(5)
       
        main.ONOS4.start()

        main.ONOS4.start_rest()
        time.sleep(5)
        
        utilities.assert_equals(expect=main.TRUE,actual=data,
                onpass="Scale up successful - 4-node ONOS cluster is up and running!",
                onfail="ONOS didn't start...")
        
        time.sleep(10)
    
    def CASE5(self,main):
        main.log.report("Scale-up ONOS to 5-nodes")
        main.case("Starting ONOS scale-up/down to 5 nodes ")
        import time
        
        main.ONOS6.handle.sendline("./onos.sh core stop")
        main.ONOS7.handle.sendline("./onos.sh core stop")
        
        #Start zookeeper 5 to prepare for ONOS5
        main.Zookeeper5.start()
        time.sleep(5)
        main.ONOS5.start()

        main.ONOS5.start_rest()
        time.sleep(5)
        
        utilities.assert_equals(expect=main.TRUE,actual=data,
                onpass="Scale up successful - 5-node ONOS cluster is up and running!",
                onfail="ONOS didn't start...")
        time.sleep(10)

    def CASE6(self,main):
        main.log.report("Scale-up ONOS to 6-nodes")
        main.case("Starting ONOS scale-up/down to 6 nodes ")
        import time
        
        main.ONOS7.handle.sendline("./onos.sh core stop")

        main.Zookeeper6.start()
        time.sleep(5)
        
        main.ONOS6.start()

        main.ONOS6.start_rest()
        time.sleep(5)
        
        utilities.assert_equals(expect=main.TRUE,actual=data,
                onpass="Scale up successful. 6-node ONOS cluster is up and running",
                onfail="ONOS didn't start...")
        time.sleep(10)

    def CASE7(self,main):
        main.log.report("Scale-up ONOS to 7-nodes")
        main.case("Starting ONOS scale-up/down to 7 nodes ")
        import time
        
        main.Zookeeper7.start()
        time.sleep(5)
        
        main.ONOS7.start()

        main.ONOS7.start_rest()
        time.sleep(5)
        
        utilities.assert_equals(expect=main.TRUE,actual=data,
                onpass="Scale up successful 7-node ONOS cluster is up and running",
                onfail="ONOS didn't start...")
        time.sleep(10)




    def CASE33(self,main):
        '''
        CASE33 NB Throughput for 3 nodes
        '''
        import time
        import json
        import sys

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        
        ONOS1_url_metrics = main.params['url1']
        ONOS2_url_metrics = main.params['url2']
        ONOS3_url_metrics = main.params['url3']

        intentPort = main.params['INTENTREST']['intentPort']
        intentCount = main.params['INTENTS']['intentCount']

        #Global north bound throughput average value for 3 nodes
        global nbtpavg3n
        nbtpavg3n = 0.0
        
        main.log.report("NB Throughput Test with 3-node ONOS cluster")

        #Assign switches evenly across ONOS instances
        #ONOS1 = s1, s2
        #ONOS2 = s3, s4
        #ONOS3 = s5, s6, s7
        main.log.info("Assigning switches evenly across ONOS instances")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s1"+
                " tcp:"+ONOS1_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s2"+
                " tcp:"+ONOS1_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s3"+
                " tcp:"+ONOS2_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s4"+
                " tcp:"+ONOS2_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s5"+
                " tcp:"+ONOS3_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s6"+
                " tcp:"+ONOS3_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s7"+
                " tcp:"+ONOS3_ip+":6633") 

        time.sleep(15)
        
        #Load each ONOS instance with the NB loadgen script
        # -n 1 indicates a unique node id
        # -u indicates ip to load intents on
        # -i indicates number of bidrectional intents to add
        # -d indicates duration of script in seconds
        # -p indicates pause before deleting
        main.log.info("Loading each ONOS instances with intents")
        main.log.report("Each ONOS instance loaded with "+intentCount+
                " intents / second")
        main.ONOS1.handle.sendline("~/./loadgen_NB1.py -n 10 -u "+
                ONOS1_ip+":"+intentPort+" -i "+intentCount+" -a 1 -l 135 -p 3")
        main.ONOS2.handle.sendline("~/./loadgen_NB2.py -n 11 -u "+
                ONOS2_ip+":"+intentPort+" -i "+intentCount+" -a 1 -l 135 -p 3")
        main.ONOS3.handle.sendline("~/./loadgen_NB3.py -n 12 -u "+
                ONOS3_ip+":"+intentPort+" -i "+intentCount+" -a 1 -l 135 -p 3")
        
        #Sleep a pre-determined number to allow ONOS throughput 
        #metrics to process events and obtain proper value
        main.log.info("Please wait while intents are being generated")
       
        #NOTE: You can change the wait time here to saturate ONOS more
        for i in range(1,101):
            time.sleep(1.8)
            #Progress counter for a long sleep
            sys.stdout.write("\rProgress: "+ str(i)+"%") 
            sys.stdout.flush()

        #Loop multiple times and measure metrics 
        json_obj1 = main.ONOS1.get_json(ONOS1_url_metrics)
        json_obj2 = main.ONOS2.get_json(ONOS2_url_metrics)
        json_obj3 = main.ONOS3.get_json(ONOS3_url_metrics)
        rate1 = json_obj1['meters'][1]['meter']['m1_rate'] 
        rate2 = json_obj2['meters'][1]['meter']['m1_rate']
        rate3 = json_obj3['meters'][1]['meter']['m1_rate']
        aggr_rate = [int(rate1), int(rate2), int(rate3)]

        nbtpavg3n = sum(aggr_rate)
        main.log.report("Intent Throughput for 3-node ONOS cluster = " +
                str(nbtpavg3n) + " Intents/sec")
   
        #NOTE: This sleep to allow for intents to finish removing
        # Allow plenty of time here before moving on to next case
        main.log.info("Please wait while intents are being removed")
        for i in range(1, 101):
            time.sleep(2)
            sys.stdout.write("\rProgress: "+str(i)+"%")
            sys.stdout.flush()
        
        main.log.info("Intents successfully removed")

        #Kill loadgen script
        main.ONOS1.handle.sendline("sudo pkill -9 loadgen_NB")
        main.ONOS2.handle.sendline("sudo pkill -9 loadgen_NB")
        main.ONOS3.handle.sendline("sudo pkill -9 loadgen_NB")


    def CASE43(self, main):
        '''
        CASE43 - NB Throughput for 4 nodes 
        '''
        
        import time
        import json
        import sys

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS4_ip = main.params['CTRL']['ip4']
    
        ONOS1_url_metrics = main.params['url1']
        ONOS2_url_metrics = main.params['url2']
        ONOS3_url_metrics = main.params['url3']
        ONOS4_url_metrics = main.params['url4']

        intentPort = main.params['INTENTREST']['intentPort']
        intentCount = main.params['INTENTS']['intentCount']
        #Divide up the intents amongst nodes we add
        intentCountNode = str(int(intentCount) * 3 / 4) 

        #Global north bound throughput average value for 4 nodes
        global nbtpavg4n
        nbtpavg4n = 0.0

        main.log.report("NB Throughput Test with 4-node ONOS cluster")
       
        #Delete previously assigned controllers
        for i in range(1, 8): 
            main.Mininet4.handle.sendline("sudo ovs-vsctl del-controller s"+
                    str(i))
        
        time.sleep(10)

        #Assign switches evenly across ONOS instances
        #ONOS1 = s1, s2
        #ONOS2 = s3, s4
        #ONOS3 = s5, s6
        #ONOS4 = s7
        main.log.info("Assigning switches evenly across ONOS instances")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s1"+
                " tcp:"+ONOS1_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s2"+
                " tcp:"+ONOS1_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s3"+
                " tcp:"+ONOS2_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s4"+
                " tcp:"+ONOS2_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s5"+
                " tcp:"+ONOS3_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s6"+
                " tcp:"+ONOS3_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s7"+
                " tcp:"+ONOS4_ip+":6633") 

        time.sleep(15)
       
        #Load each ONOS instance with the NB loadgen script
        # -n 1 indicates a unique node id
        # -u indicates ip to load intents on
        # -i indicates number of bidrectional intents to add
        # -d indicates duration of script in seconds
        # -p indicates pause before deleting
        main.log.info("Loading each ONOS instances with intents")
        main.log.report("Each ONOS instance loaded with "+intentCountNode+
                " intents / second")
        main.ONOS1.handle.sendline("~/./loadgen_NB1.py -n 13 -u "+
                ONOS1_ip+":"+intentPort+" -i "+intentCountNode+" -a 1 -l 105 -p 3")
        main.ONOS2.handle.sendline("~/./loadgen_NB2.py -n 14 -u "+
                ONOS2_ip+":"+intentPort+" -i "+intentCountNode+" -a 1 -l 105 -p 3")
        main.ONOS3.handle.sendline("~/./loadgen_NB3.py -n 15 -u "+
                ONOS3_ip+":"+intentPort+" -i "+intentCountNode+" -a 1 -l 105 -p 3")
        main.ONOS4.handle.sendline("~/./loadgen_NB4.py -n 16 -u "+
                ONOS4_ip+":"+intentPort+" -i "+intentCountNode+" -a 1 -l 105 -p 3")

        #Sleep a pre-determined number to allow ONOS throughput 
        #metrics to process events and obtain proper value
        main.log.info("Please wait while intents are generated")
        #NOTE: You can change the wait time here to saturate ONOS more
        for i in range(1,101):
            time.sleep(1.8)
            #Progress counter for a long sleep
            sys.stdout.write("\rProgress: "+ str(i)+"%") 
            sys.stdout.flush()
    
        #Loop multiple times and measure metrics 
        json_obj1 = main.ONOS1.get_json(ONOS1_url_metrics)
        json_obj2 = main.ONOS2.get_json(ONOS2_url_metrics)
        json_obj3 = main.ONOS3.get_json(ONOS3_url_metrics)
        json_obj4 = main.ONOS4.get_json(ONOS4_url_metrics)
        rate1 = json_obj1['meters'][1]['meter']['m1_rate'] 
        rate2 = json_obj2['meters'][1]['meter']['m1_rate']
        rate3 = json_obj3['meters'][1]['meter']['m1_rate']
        rate4 = json_obj4['meters'][1]['meter']['m1_rate']
        aggr_rate = [int(rate1), int(rate2), int(rate3), int(rate4)]

        nbtpavg4n = sum(aggr_rate)
        main.log.report("Intent Throughput for 4-node ONOS cluster = " +
                str(nbtpavg4n) + " Intents/sec")
   
        #NOTE: This sleep to allow for intents to finish removing
        # Allow plenty of time here before moving on to next case
        main.log.info("Please wait while intents are being removed")
        for i in range(1, 101):
            time.sleep(2)
            sys.stdout.write("\rProgress: "+str(i)+"%")
            sys.stdout.flush()
        
        main.log.info("Intents successfully removed")
        
        #Kill loadgen script
        main.ONOS1.handle.sendline("sudo pkill -9 loadgen_NB")
        main.ONOS2.handle.sendline("sudo pkill -9 loadgen_NB")
        main.ONOS3.handle.sendline("sudo pkill -9 loadgen_NB")
        main.ONOS4.handle.sendline("sudo pkill -9 loadgen_NB")

    def CASE53(self, main):
        '''
        CASE53 - NB Throughput for 5 nodes 
        '''
        
        import time
        import json
        import sys

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS4_ip = main.params['CTRL']['ip4']
        ONOS5_ip = main.params['CTRL']['ip5']

        ONOS1_url_metrics = main.params['url1']
        ONOS2_url_metrics = main.params['url2']
        ONOS3_url_metrics = main.params['url3']
        ONOS4_url_metrics = main.params['url4']
        ONOS5_url_metrics = main.params['url5']

        intentPort = main.params['INTENTREST']['intentPort']
        intentCount = main.params['INTENTS']['intentCount']
        #Divide up the intents amongst nodes we add
        intentCountNode = str(int(intentCount) * 3 / 5 )

        #Global north bound throughput average value for 4 nodes
        global nbtpavg5n
        nbtpavg5n = 0.0

        main.log.report("NB Throughput Test with 5-node ONOS cluster")
        
        #Delete previously assigned controllers
        for i in range(1, 8): 
            main.Mininet4.handle.sendline("sudo ovs-vsctl del-controller s"+
                    str(i))
        
        time.sleep(10)
        
        #Assign switches evenly across ONOS instances
        #ONOS1 = s1 
        #ONOS2 = s2
        #ONOS3 = s3
        #ONOS4 = s4, s5
        #ONOS5 = s6, s7
        main.log.info("Assigning switches evenly across ONOS instances")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s1"+
                " tcp:"+ONOS1_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s2"+
                " tcp:"+ONOS2_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s3"+
                " tcp:"+ONOS3_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s4"+
                " tcp:"+ONOS4_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s5"+
                " tcp:"+ONOS4_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s6"+
                " tcp:"+ONOS5_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s7"+
                " tcp:"+ONOS5_ip+":6633") 

        time.sleep(15)
       
        #Load each ONOS instance with the NB loadgen script
        # -n 1 indicates a unique node id
        # -u indicates ip to load intents on
        # -i indicates number of bidrectional intents to add
        # -d indicates duration of script in seconds
        # -p indicates pause before deleting
        main.log.info("Loading each ONOS instances with intents")
        main.log.report("Each ONOS instance loaded with "+intentCountNode+
                " intents / second")
        main.ONOS1.handle.sendline("~/./loadgen_NB1.py -n 17 -u "+
                ONOS1_ip+":"+intentPort+" -i "+intentCountNode+" -a 1 -l 105 -p 3")
        main.ONOS2.handle.sendline("~/./loadgen_NB2.py -n 18 -u "+
                ONOS2_ip+":"+intentPort+" -i "+intentCountNode+" -a 1 -l 105 -p 3")
        main.ONOS3.handle.sendline("~/./loadgen_NB3.py -n 19 -u "+
                ONOS3_ip+":"+intentPort+" -i "+intentCountNode+" -a 1 -l 105 -p 3")
        main.ONOS4.handle.sendline("~/./loadgen_NB4.py -n 20 -u "+
                ONOS4_ip+":"+intentPort+" -i "+intentCountNode+" -a 1 -l 105 -p 3")
        main.ONOS5.handle.sendline("~/./loadgen_NB5.py -n 21 -u "+
                ONOS5_ip+":"+intentPort+" -i "+intentCountNode+" -a 1 -l 105 -p 3")

        #Sleep a pre-determined number to allow ONOS throughput 
        #metrics to process events and obtain proper value
        main.log.info("Please wait while intents are generated")
        #NOTE: You can change the wait time here to saturate ONOS more
        for i in range(1,101):
            time.sleep(1.8)
            #Progress counter for a long sleep
            sys.stdout.write("\rProgress: "+ str(i)+"%") 
            sys.stdout.flush()

        #Loop multiple times and measure metrics 
        json_obj1 = main.ONOS1.get_json(ONOS1_url_metrics)
        json_obj2 = main.ONOS2.get_json(ONOS2_url_metrics)
        json_obj3 = main.ONOS3.get_json(ONOS3_url_metrics)
        json_obj4 = main.ONOS4.get_json(ONOS4_url_metrics)
        json_obj5 = main.ONOS5.get_json(ONOS5_url_metrics)
        rate1 = json_obj1['meters'][1]['meter']['m1_rate'] 
        rate2 = json_obj2['meters'][1]['meter']['m1_rate']
        rate3 = json_obj3['meters'][1]['meter']['m1_rate']
        rate4 = json_obj4['meters'][1]['meter']['m1_rate']
        rate5 = json_obj5['meters'][1]['meter']['m1_rate']
        aggr_rate = [int(rate1), int(rate2), int(rate3), int(rate4),
                int(rate5)]

        nbtpavg5n = sum(aggr_rate)
        main.log.report("Intent Throughput for 5-node ONOS cluster = " +
                str(nbtpavg5n) + " Intents/sec")
   
        #NOTE: This sleep to allow for intents to finish removing
        # Allow plenty of time here before moving on to next case
        main.log.info("Please wait while intents are being removed")
        for i in range(1, 101):
            time.sleep(2)
            sys.stdout.write("\rProgress: "+str(i)+"%")
            sys.stdout.flush()
        
        main.log.info("Intents successfully removed")

        #Kill loadgen script
        main.ONOS1.handle.sendline("sudo pkill -9 loadgen_NB")
        main.ONOS2.handle.sendline("sudo pkill -9 loadgen_NB")
        main.ONOS3.handle.sendline("sudo pkill -9 loadgen_NB")
        main.ONOS4.handle.sendline("sudo pkill -9 loadgen_NB")
        main.ONOS5.handle.sendline("sudo pkill -9 loadgen_NB")

    def CASE63(self, main):
        '''
        CASE63 - NB Throughput for 6 nodes 
        '''
        
        import time
        import json
        import sys

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS4_ip = main.params['CTRL']['ip4']
        ONOS5_ip = main.params['CTRL']['ip5']
        ONOS6_ip = main.params['CTRL']['ip6']

        ONOS1_url_metrics = main.params['url1']
        ONOS2_url_metrics = main.params['url2']
        ONOS3_url_metrics = main.params['url3']
        ONOS4_url_metrics = main.params['url4']
        ONOS5_url_metrics = main.params['url5']
        ONOS6_url_metrics = main.params['url6']

        intentPort = main.params['INTENTREST']['intentPort']
        intentCount = main.params['INTENTS']['intentCount']
        #Divide up the intents amongst nodes we add
        intentCountNode = str(int(intentCount) * 3 / 6) 

        #Global north bound throughput average value for 4 nodes
        global nbtpavg6n
        nbtpavg6n = 0.0

        main.log.report("NB Throughput Test with 6-node ONOS cluster")
        
        #Delete previously assigned controllers
        for i in range(1, 8): 
            main.Mininet4.handle.sendline("sudo ovs-vsctl del-controller s"+
                    str(i))
        
        time.sleep(10)

        #Assign switches evenly across ONOS instances
        #ONOS1 = s1 
        #ONOS2 = s2
        #ONOS3 = s3
        #ONOS4 = s4 
        #ONOS5 = s5
        #ONOS6 = s6, s7

        main.log.info("Assigning switches evenly across ONOS instances")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s1"+
                " tcp:"+ONOS1_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s2"+
                " tcp:"+ONOS2_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s3"+
                " tcp:"+ONOS3_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s4"+
                " tcp:"+ONOS4_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s5"+
                " tcp:"+ONOS5_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s6"+
                " tcp:"+ONOS6_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s7"+
                " tcp:"+ONOS6_ip+":6633") 

        time.sleep(15)
       
        #Load each ONOS instance with the NB loadgen script
        # -n 1 indicates a unique node id
        # -u indicates ip to load intents on
        # -i indicates number of bidrectional intents to add
        # -d indicates duration of script in seconds
        # -p indicates pause before deleting
        main.log.info("Loading each ONOS instances with intents")
        main.log.report("Each ONOS instance loaded with "+intentCountNode+
                " intents / second")
        main.ONOS1.handle.sendline("~/./loadgen_NB1.py -n 22 -u "+
                ONOS1_ip+":"+intentPort+" -i "+intentCountNode+" -a 1 -l 105 -p 3")
        main.ONOS2.handle.sendline("~/./loadgen_NB2.py -n 23 -u "+
                ONOS2_ip+":"+intentPort+" -i "+intentCountNode+" -a 1 -l 105 -p 3")
        main.ONOS3.handle.sendline("~/./loadgen_NB3.py -n 24 -u "+
                ONOS3_ip+":"+intentPort+" -i "+intentCountNode+" -a 1 -l 105 -p 3")
        main.ONOS4.handle.sendline("~/./loadgen_NB4.py -n 25 -u "+
                ONOS4_ip+":"+intentPort+" -i "+intentCountNode+" -a 1 -l 105 -p 3")
        main.ONOS5.handle.sendline("~/./loadgen_NB5.py -n 26 -u "+
                ONOS5_ip+":"+intentPort+" -i "+intentCountNode+" -a 1 -l 105 -p 3")
        main.ONOS6.handle.sendline("~/./loadgen_NB6.py -n 27 -u "+
                ONOS6_ip+":"+intentPort+" -i "+intentCountNode+" -a 1 -l 105 -p 3")

        #Sleep a pre-determined number to allow ONOS throughput 
        #metrics to process events and obtain proper value
        main.log.info("Please wait while intents are generated")
        #NOTE: You can change the wait time here to saturate ONOS more
        for i in range(1,101):
            time.sleep(1.8)
            #Progress counter for a long sleep
            sys.stdout.write("\rProgress: "+ str(i)+"%") 
            sys.stdout.flush()
        
        #Loop multiple times and measure metrics 
        json_obj1 = main.ONOS1.get_json(ONOS1_url_metrics)
        json_obj2 = main.ONOS2.get_json(ONOS2_url_metrics)
        json_obj3 = main.ONOS3.get_json(ONOS3_url_metrics)
        json_obj4 = main.ONOS4.get_json(ONOS4_url_metrics)
        json_obj5 = main.ONOS5.get_json(ONOS5_url_metrics)
        json_obj6 = main.ONOS6.get_json(ONOS6_url_metrics)
        rate1 = json_obj1['meters'][1]['meter']['m1_rate'] 
        rate2 = json_obj2['meters'][1]['meter']['m1_rate']
        rate3 = json_obj3['meters'][1]['meter']['m1_rate']
        rate4 = json_obj4['meters'][1]['meter']['m1_rate']
        rate5 = json_obj5['meters'][1]['meter']['m1_rate']
        rate6 = json_obj6['meters'][1]['meter']['m1_rate']
        aggr_rate = [int(rate1), int(rate2), int(rate3), int(rate4),
                int(rate5), int(rate6)]

        nbtpavg6n = sum(aggr_rate)
        main.log.report("Intent Throughput for 6-node ONOS cluster = " +
                str(nbtpavg6n) + " Intents/sec")
   
        #NOTE: This sleep to allow for intents to finish removing
        # Allow plenty of time here before moving on to next case
        main.log.info("Please wait while intents are being removed")
        for i in range(1, 101):
            time.sleep(2)
            sys.stdout.write("\rProgress: "+str(i)+"%")
            sys.stdout.flush()
        
        main.log.info("Intents successfully removed")
        
        #Kill loadgen script
        main.ONOS1.handle.sendline("sudo pkill -9 loadgen_NB")
        main.ONOS2.handle.sendline("sudo pkill -9 loadgen_NB")
        main.ONOS3.handle.sendline("sudo pkill -9 loadgen_NB")
        main.ONOS4.handle.sendline("sudo pkill -9 loadgen_NB")
        main.ONOS5.handle.sendline("sudo pkill -9 loadgen_NB")
        main.ONOS6.handle.sendline("sudo pkill -9 loadgen_NB") 

    def CASE73(self, main):
        '''
        CASE73 - NB Throughput for 7 nodes 
        '''
        
        import time
        import json
        import sys

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS4_ip = main.params['CTRL']['ip4']
        ONOS5_ip = main.params['CTRL']['ip5']
        ONOS6_ip = main.params['CTRL']['ip6']
        ONOS7_ip = main.params['CTRL']['ip7']

        ONOS1_url_metrics = main.params['url1']
        ONOS2_url_metrics = main.params['url2']
        ONOS3_url_metrics = main.params['url3']
        ONOS4_url_metrics = main.params['url4']
        ONOS5_url_metrics = main.params['url5']
        ONOS6_url_metrics = main.params['url6']
        ONOS7_url_metrics = main.params['url7']

        intentPort = main.params['INTENTREST']['intentPort']
        intentCount = main.params['INTENTS']['intentCount']
        #Divide up the intents amongst nodes we add
        intentCountNode = str(int(intentCount) * 3 / 7) 
    
        #Global north bound throughput average value for 4 nodes
        global nbtpavg7n
        nbtpavg7n = 0.0

        main.log.report("NB Throughput Test with 7-node ONOS cluster")
        
        #Delete previously assigned controllers
        for i in range(1, 8): 
            main.Mininet4.handle.sendline("sudo ovs-vsctl del-controller s"+
                    str(i))
        
        time.sleep(10)

        #Assign switches evenly across ONOS instances
        #ONOS1 = s1 
        #ONOS2 = s2
        #ONOS3 = s3
        #ONOS4 = s4 
        #ONOS5 = s5
        #ONOS6 = s6
        #ONOS7 = s7

        main.log.info("Assigning switches evenly across ONOS instances")
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s1"+
                " tcp:"+ONOS1_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s2"+
                " tcp:"+ONOS2_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s3"+
                " tcp:"+ONOS3_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s4"+
                " tcp:"+ONOS4_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s5"+
                " tcp:"+ONOS5_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s6"+
                " tcp:"+ONOS6_ip+":6633") 
        main.Mininet4.handle.sendline("sudo ovs-vsctl set-controller s7"+
                " tcp:"+ONOS7_ip+":6633") 

        time.sleep(15)
       
        #Load each ONOS instance with the NB loadgen script
        # -n 1 indicates a unique node id
        # -u indicates ip to load intents on
        # -i indicates number of bidrectional intents to add
        # -d indicates duration of script in seconds
        # -p indicates pause before deleting
        main.log.info("Loading each ONOS instances with intents")
        main.log.report("Each ONOS instance loaded with "+intentCountNode+
                " intents / second")
        main.ONOS1.handle.sendline("~/./loadgen_NB1.py -n 29 -u "+
                ONOS1_ip+":"+intentPort+" -i "+intentCountNode+" -a 1 -l 105 -p 3")
        main.ONOS2.handle.sendline("~/./loadgen_NB2.py -n 30 -u "+
                ONOS2_ip+":"+intentPort+" -i "+intentCountNode+" -a 1 -l 105 -p 3")
        main.ONOS3.handle.sendline("~/./loadgen_NB3.py -n 31 -u "+
                ONOS3_ip+":"+intentPort+" -i "+intentCountNode+" -a 1 -l 105 -p 3")
        main.ONOS4.handle.sendline("~/./loadgen_NB4.py -n 32 -u "+
                ONOS4_ip+":"+intentPort+" -i "+intentCountNode+" -a 1 -l 105 -p 3")
        main.ONOS5.handle.sendline("~/./loadgen_NB5.py -n 33 -u "+
                ONOS5_ip+":"+intentPort+" -i "+intentCountNode+" -a 1 -l 105 -p 3")
        main.ONOS6.handle.sendline("~/./loadgen_NB6.py -n 34 -u "+
                ONOS6_ip+":"+intentPort+" -i "+intentCountNode+" -a 1 -l 105 -p 3")
        main.ONOS7.handle.sendline("~/./loadgen_NB7.py -n 35 -u "+
                ONOS7_ip+":"+intentPort+" -i "+intentCountNode+" -a 1 -l 105 -p 3")

        #Sleep a pre-determined number to allow ONOS throughput 
        #metrics to process events and obtain proper value
        main.log.info("Please wait while intents are generated")
        #NOTE: You can change the wait time here to saturate ONOS more
        for i in range(1,101):
            time.sleep(1.8)
            #Progress counter for a long sleep
            sys.stdout.write("\rProgress: "+ str(i)+"%") 
            sys.stdout.flush()
        
        #Loop multiple times and measure metrics 
        json_obj1 = main.ONOS1.get_json(ONOS1_url_metrics)
        json_obj2 = main.ONOS2.get_json(ONOS2_url_metrics)
        json_obj3 = main.ONOS3.get_json(ONOS3_url_metrics)
        json_obj4 = main.ONOS4.get_json(ONOS4_url_metrics)
        json_obj5 = main.ONOS5.get_json(ONOS5_url_metrics)
        json_obj6 = main.ONOS6.get_json(ONOS6_url_metrics)
        json_obj7 = main.ONOS7.get_json(ONOS7_url_metrics)
        rate1 = json_obj1['meters'][1]['meter']['m1_rate'] 
        rate2 = json_obj2['meters'][1]['meter']['m1_rate']
        rate3 = json_obj3['meters'][1]['meter']['m1_rate']
        rate4 = json_obj4['meters'][1]['meter']['m1_rate']
        rate5 = json_obj5['meters'][1]['meter']['m1_rate']
        rate6 = json_obj6['meters'][1]['meter']['m1_rate']
        rate7 = json_obj7['meters'][1]['meter']['m1_rate']
        aggr_rate = [int(rate1), int(rate2), int(rate3), int(rate4),
                int(rate5), int(rate6), int(rate7)]

        nbtpavg7n = sum(aggr_rate)
        main.log.report("Intent Throughput for 7-node ONOS cluster = " +
                str(nbtpavg7n) + " Intents/sec")
   
        #NOTE: This sleep to allow for intents to finish removing
        # Allow plenty of time here before moving on to next case
        main.log.info("Please wait while intents are being removed")
        for i in range(1, 101):
            time.sleep(2)
            sys.stdout.write("\rProgress: "+str(i)+"%")
            sys.stdout.flush()
        
        main.log.info("Intents successfully removed")

        #Kill loadgen script
        main.ONOS1.handle.sendline("sudo pkill -9 loadgen_NB")
        main.ONOS2.handle.sendline("sudo pkill -9 loadgen_NB")
        main.ONOS3.handle.sendline("sudo pkill -9 loadgen_NB")
        main.ONOS4.handle.sendline("sudo pkill -9 loadgen_NB")
        main.ONOS5.handle.sendline("sudo pkill -9 loadgen_NB")
        main.ONOS6.handle.sendline("sudo pkill -9 loadgen_NB") 
        main.ONOS7.handle.sendline("sudo pkill -9 loadgen_NB")


    
    def CASE8(self,main):
        import time
        main.log.report("Scaling ONOS down to 6 ONOS instances")
        main.ONOS7.handle.sendline("./onos.sh core stop")
        time.sleep(8)
        pdata = main.ONOS7.isup()
        
        utilities.assert_equals(expect=main.FALSE,actual=pdata,
                onpass="ONOS7 stopped",
                onfail="ONOS scale down failed")
        time.sleep(3)
        data = main.ONOS1.isup() and main.ONOS2.isup() and\
                main.ONOS3.isup() and main.ONOS4.isup() and\
                main.ONOS5.isup() and main.ONOS6.isup()
        for i in range(3):
            if data == main.FALSE: 
                time.sleep(3)
                data = main.ONOS1.isup() and main.ONOS2.isup() and\
                        main.ONOS3.isup() and main.ONOS4.isup() and\
                        main.ONOS5.isup() and main.ONOS6.isup()
            else:
                break
        utilities.assert_equals(expect=main.TRUE,actual=data,
                onpass="Scale down successfull -6-node ONOS cluster is up and running!",
                onfail="ONOS didn't start...")
    
    def CASE9(self,main):

        main.log.report("Scaling ONOS down to 5 ONOS instances")
        main.ONOS6.handle.sendline("./onos.sh core stop")
        time.sleep(8)
        pdata = main.ONOS6.isup() and main.ONOS7.isup()
        
        utilities.assert_equals(expect=main.FALSE,actual=pdata,
                onpass="ONOS 6,7 stopped",
                onfail="ONOS scale down failed")
        data = main.ONOS1.isup() and main.ONOS2.isup() and\
                main.ONOS3.isup() and main.ONOS4.isup() and\
                main.ONOS5.isup()
        for i in range(3):
            if data == main.FALSE: 
                time.sleep(3)
                data = main.ONOS1.isup() and main.ONOS2.isup() and\
                        main.ONOS3.isup() and main.ONOS4.isup() and\
                        main.ONOS5.isup()
            else:
                break
        utilities.assert_equals(expect=main.TRUE,actual=data,
                onpass="Scale down successfull - 5 node ONOS clsuter is up and running!",
                onfail="ONOS didn't start...")

    def CASE10(self,main):

        main.log.report("Scaling ONOS down to 4 ONOS instances")
        
        main.ONOS5.handle.sendline("./onos.sh core stop ")
        time.sleep(5)
        pdata = main.ONOS5.isup() and main.ONOS6.isup() and main.ONOS7.isup()
        utilities.assert_equals(expect=main.FALSE,actual=pdata,
                onpass="ONOS 5, 6, 7 stopped",
                onfail="ONOS scale down failed")
        data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup() and\
                main.ONOS4.isup()
        for i in range(3):
            if data == main.FALSE: 
                time.sleep(3)
                data = main.ONOS1.isup() and main.ONOS2.isup() and main.ONOS3.isup() and\
                        main.ONOS4.isup()
            else:
                break
        utilities.assert_equals(expect=main.TRUE,actual=data,
                onpass="Scale down successful - 4 node ONOS cluster is up and running!",
                onfail="ONOS didn't start...")

    def CASE11(self,main):

        main.log.report("Scaling ONOS down to 3 ONOS instances")
        main.ONOS4.handle.sendline("./onos.sh core stop ")
        time.sleep(5)
        pdata = main.ONOS4.isup() and main.ONOS5.isup() and\
                main.ONOS6.isup() and main.ONOS7.isup()
        utilities.assert_equals(expect=main.FALSE,actual=pdata,
                onpass="ONOS 4, 5, 6, 7 stopped",
                onfail="ONOS scale down failed")
        data = main.ONOS1.isup() and main.ONOS2.isup() and\
                main.ONOS3.isup()
        for i in range(3):
            if data == main.FALSE: 
                time.sleep(3)
                data = main.ONOS1.isup() and main.ONOS2.isup() and\
                        main.ONOS3.isup()
            else:
                break
        utilities.assert_equals(expect=main.TRUE,actual=data,
                onpass="Scale down successful - 3 node ONOS cluster is up and running!",
                onfail="ONOS didn't start...")


    def CASE105(self,main):
        import os
        import time

        main.log.info("Posting the results to http://10.128.5.54/scale.html")
        db_script = main.params['db_script']
        os.system(db_script + " -n='1000IntentsScaleUp" + "' -rate3='" + str(nbtpavg3n) +
                "' -rate4='" + str(nbtpavg4n) + "' -rate5='" + str(nbtpavg5n) +
                "' -rate6='" + str(nbtpavg6n) + "' -rate7='" + str(nbtpavg7n) +
                "' -table='onos_scale'")

        main.log.report("The graphical view of the tests can be viewed at "+
                "http://10.128.5.54/scale.html")

    def CASE106(self,main):
        import os
        import time
        
        main.log.info("Posting the results to http://10.128.5.54/scale.html")
        db_script = main.params['db_script']
        os.system(db_script + " -n='1000IntentsScaleDown" + "' -rate3='" + str(nbtpavg3n) +
                "' -rate4='" + str(nbtpavg4n) + "' -rate5='" + str(nbtpavg5n) +
                "' -rate6='" + str(nbtpavg6n) + "' -rate7='" + str(nbtpavg7n) +
                "' -table='onos_scale'")

        main.log.report("The graphical view of the tests can be viewed at "+
                +"http://10.128.5.54/scale.html")


