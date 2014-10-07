class scaleONOS7nodesSB :

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
       

#**** TODO: ****
#  Add correct assertions for cases 4~7
    def CASE4(self,main):
        import time 
        
        main.log.report("Scale-up ONOS to 4-nodes ")
      
        main.ONOS5.handle.sendline("./onos.sh core stop")
        main.ONOS6.handle.sendline("./onos.sh core stop")
        main.ONOS7.handle.sendline("./onos.sh core stop")
        
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
        import time
        
        main.log.report("Scale-up ONOS to 5-nodes")
        
        main.ONOS6.handle.sendline("./onos.sh core stop")
        main.ONOS7.handle.sendline("./onos.sh core stop")
        
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
        import time
        
        main.log.report("Scale-up ONOS to 6-nodes")
        
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
        import time
       
        main.log.report("Scale-up ONOS to 7-nodes")
        
        main.Zookeeper7.start()
        time.sleep(5)
        
        main.ONOS7.start()

        main.ONOS7.start_rest()
        time.sleep(5)
        
        utilities.assert_equals(expect=main.TRUE,actual=data,
                onpass="Scale up successful 7-node ONOS cluster is up and running",
                onfail="ONOS didn't start...")
        time.sleep(10)


    def CASE31(self,main):
        
        import time
        import json
        import math
        import sys

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        
        url1 = main.params['url1']
        url2 = main.params['url2']
        url3 = main.params['url3']
       
        #Variables for SB loadgen script
        num_switch = main.params['LOADVARS']['numSw']
        num_port = main.params['LOADVARS']['numPort']
        sw_add_rate = main.params['LOADVARS']['swAddRate']
        gen_duration = main.params['LOADVARS']['genDur']
        time_sleep = main.params['LOADVARS']['timesleep']
        #NOTE: The loadgen timeout must be significant enough
        #      to ensure that the loadgen script finishes.
        loadgen_timeout = main.params['LOADVARS']['genTimeout'] 
        init_sleep = main.params['LOADVARS']['initSleep'] 

        #Initialize global throughput average value
        global tpavg3n 
        tpavg3n = 0.0

        main.log.report("SB Throughput test - 3 ONOS instances")
      
        #NOTE: 
        # Here are the parameters for loadgen_SB.py at the time of 
        # writing this code:
        # -u : space separated URL string of to add load
        # -s : number of switches to add to each instance
        # -p : number of ports to add to each switch
        # -a : rate to add each switch / second
        # -l : length of time that load is generated
        # Refer to loadgen_SB.py --help for additional information
        # This script may take a while to run depending on 
        #      how many port / switch events you have added
        main.log.info("Loadgen script is being initialized..."+
                "This may take a while")
         
        main.Mininet2.handle.sendline(
                    "./loadgen_SB.py"+
                    " -u '"+ONOS1_ip+" "+ONOS2_ip+" "+ONOS3_ip+"'"+
                    " -s "+num_switch+
                    " -a "+sw_add_rate+
                    " -p "+num_port+
                    " -l "+gen_duration+
                    " -t "+time_sleep)
        #Expect string that indicates loading has started 
        main.Mininet2.handle.expect(
                    "Starting SB load", 
                    timeout = int(loadgen_timeout))
        main.log.info("SB loading has started")

        #Initial sleep before calling REST for metrics
        time.sleep(int(init_sleep))

        #Continue obtaining metrics from REST
        #and save the highest throughput
        temp_timestamp = 0
        temp_list = []
        loop_counter = 0
        rest_loop_count = main.params['LOADVARS']['loopCount']
        while True:
            json_obj_ONOS1 = main.ONOS2.get_json(url1)
            m1_rate_ONOS1 = json_obj_ONOS1['meters'][4]['meter']['m1_rate']
           
            temp_list.append(int(m1_rate_ONOS1))
            #If current measurement is greater than the previous one,
            #save the current measurement into global variable
            main.log.info("Current throughput average is: "+
                    str(m1_rate_ONOS1)+" events/second")
            
            loop_counter = loop_counter + 1

            time.sleep(3)
            if loop_counter == int(rest_loop_count):
                break

        tpavg3n = max(temp_list)

        main.log.report("Max SB Throughput for 3 ONOS instances: "+
                str(tpavg3n) + " Events / second")

        main.log.info("Please wait for cleanup")
        
        for i in range(1, 101):
            time.sleep(0.5)
            sys.stdout.write("\rProgress: "+str(i)+"%")
            sys.stdout.flush()
         
        #Ensure test is killed and MN is cleaned
        main.Mininet2.handle.sendline("sudo pkill -9 loadgen_SB")
        main.Mininet2.handle.sendline("sudo mn -c")
        main.Mininet2.handle.expect("\$", timeout=100)

    def CASE41(self,main):
        import time
        import json
        import math
        import sys

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS4_ip = main.params['CTRL']['ip4']

        url1 = main.params['url1']
        url2 = main.params['url2']
        url3 = main.params['url3']
        url4 = main.params['url4']

        #Variables for SB loadgen script
        num_switch = main.params['LOADVARS']['numSw']
        num_port = main.params['LOADVARS']['numPort']
        sw_add_rate = main.params['LOADVARS']['swAddRate']
        gen_duration = main.params['LOADVARS']['genDur']
        time_sleep = main.params['LOADVARS']['timesleep']
        #NOTE: The loadgen timeout must be significant enough
        #      to ensure that the loadgen script finishes.
        loadgen_timeout = main.params['LOADVARS']['genTimeout'] 
        init_sleep = main.params['LOADVARS']['initSleep'] 
       
        global tpavg4n 
        tpavg4n = 0.0

        main.log.report("SB Throughput test - 4 ONOS instances")
      
        #NOTE: 
        # Here are the parameters for loadgen_SB.py at the time of 
        # writing this code:
        # -u : space separated URL string of to add load
        # -s : number of switches to add to each instance
        # -p : number of ports to add to each switch
        # -a : rate to add each switch / second
        # -l : length of time that load is generated
        # Refer to loadgen_SB.py --help for additional information
        # This script may take a while to run depending on 
        #      how many port / switch events you have added
        main.log.info("Please wait while loadgen script is running")
        main.Mininet2.handle.sendline(
                    "./loadgen_SB.py"+
                    " -u '"+ONOS1_ip+" "+ONOS2_ip+" "+ONOS3_ip+" "+
                            ONOS4_ip+"'"+
                    " -s "+num_switch+
                    " -a "+sw_add_rate+
                    " -p "+num_port+
                    " -l "+gen_duration+
                    " -t "+time_sleep)
        #Expect string that indicates loading has started 
        main.Mininet2.handle.expect(
                    "Starting SB load", 
                    timeout = int(loadgen_timeout))

        #Initial sleep before calling REST for metrics
        time.sleep(int(init_sleep))
        
        #Continue obtaining metrics from REST
        #and save the highest throughput
        temp_timestamp = 0
        loop_counter = 0
        temp_list = []
        rest_loop_count = main.params['LOADVARS']['loopCount']
        while True:
            json_obj_ONOS1 = main.ONOS2.get_json(url1)
            m1_rate_ONOS1 = json_obj_ONOS1['meters'][4]['meter']['m1_rate']
           
            temp_list.append(int(m1_rate_ONOS1))
            #If current measurement is greater than the previous one,
            #save the current measurement into global variable
            main.log.info("Current throughput average is: "+
                    str(m1_rate_ONOS1)+" events/second")
            
            loop_counter = loop_counter + 1

            time.sleep(3)
            if loop_counter == int(rest_loop_count):
                break

        tpavg4n = max(temp_list)
        main.log.report("Max SB Throughput for 4 ONOS instances: "+
                str(tpavg4n) + " Events / second")
        
        main.log.info("Please wait for cleanup")
        
        for i in range(1, 101):
            time.sleep(0.5)
            sys.stdout.write("\rProgress: "+str(i)+"%")
            sys.stdout.flush()
   
        #Ensure test is killed and MN is cleaned
        main.Mininet2.handle.sendline("sudo pkill -9 loadgen_SB")
        main.Mininet2.handle.sendline("sudo mn -c")
        main.Mininet2.handle.expect("\$", timeout=100)

    
    def CASE51(self,main):
        import time
        import json
        import math
        import sys

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS4_ip = main.params['CTRL']['ip4']
        ONOS5_ip = main.params['CTRL']['ip5']

        url1 = main.params['url1']
        url2 = main.params['url2']
        url3 = main.params['url3']
        url4 = main.params['url4']
        url5 = main.params['url5']

        #Variables for SB loadgen script
        num_switch = main.params['LOADVARS']['numSw']
        num_port = main.params['LOADVARS']['numPort']
        sw_add_rate = main.params['LOADVARS']['swAddRate']
        gen_duration = main.params['LOADVARS']['genDur']
        time_sleep = main.params['LOADVARS']['timesleep']
        #NOTE: The loadgen timeout must be significant enough
        #      to ensure that the loadgen script finishes.
        loadgen_timeout = main.params['LOADVARS']['genTimeout'] 
        init_sleep = main.params['LOADVARS']['initSleep'] 
       
        global tpavg5n 
        tpavg5n = 0.0

        main.log.report("SB Throughput test - 5 ONOS instances")
      
        #NOTE: 
        # Here are the parameters for loadgen_SB.py at the time of 
        # writing this code:
        # -u : space separated URL string of to add load
        # -s : number of switches to add to each instance
        # -p : number of ports to add to each switch
        # -a : rate to add each switch / second
        # -l : length of time that load is generated
        # Refer to loadgen_SB.py --help for additional information
        # This script may take a while to run depending on 
        #      how many port / switch events you have added
        main.log.info("Please wait while loadgen script is running")
        main.Mininet2.handle.sendline(
                    "./loadgen_SB.py"+
                    " -u '"+ONOS1_ip+" "+ONOS2_ip+" "+ONOS3_ip+" "+
                            ONOS4_ip+" "+ONOS5_ip+"'"
                    " -s "+num_switch+
                    " -a "+sw_add_rate+
                    " -p "+num_port+
                    " -l "+gen_duration+
                    " -t "+time_sleep)
        #Expect string that indicates loading has started 
        main.Mininet2.handle.expect(
                    "Starting SB load", 
                    timeout = int(loadgen_timeout))

        #Initial sleep before calling REST for metrics
        time.sleep(int(init_sleep))
        
        #Continue obtaining metrics from REST
        #and save the highest throughput
        temp_timestamp = 0
        loop_counter = 0
        temp_list = []
        rest_loop_count = main.params['LOADVARS']['loopCount']
        while True:
            json_obj_ONOS1 = main.ONOS2.get_json(url1)
            m1_rate_ONOS1 = json_obj_ONOS1['meters'][4]['meter']['m1_rate']
           
            temp_list.append(int(m1_rate_ONOS1))
            #If current measurement is greater than the previous one,
            #save the current measurement into global variable
            main.log.info("Current throughput average is: "+
                    str(m1_rate_ONOS1)+" events/second")

            loop_counter = loop_counter + 1

            time.sleep(3)
            if loop_counter == int(rest_loop_count):
                break

        
        tpavg5n = max(temp_list)
        main.log.report("SB Throughput for 5 ONOS instances: "+
                str(tpavg5n) + " Events / second")
        
        main.log.info("Please wait for cleanup")
        
        for i in range(1, 101):
            time.sleep(0.5)
            sys.stdout.write("\rProgress: "+str(i)+"%")
            sys.stdout.flush()

        #Ensure test is killed and MN is cleaned
        main.Mininet2.handle.sendline("sudo pkill -9 loadgen_SB")
        main.Mininet2.handle.sendline("sudo mn -c")
        main.Mininet2.handle.expect("\$", timeout=100)
        
    
    def CASE61(self,main):
        import time
        import json
        import math
        import sys

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS4_ip = main.params['CTRL']['ip4']
        ONOS5_ip = main.params['CTRL']['ip5']
        ONOS6_ip = main.params['CTRL']['ip6']

        url1 = main.params['url1']
        url2 = main.params['url2']
        url3 = main.params['url3']
        url4 = main.params['url4']
        url5 = main.params['url5']
        url6 = main.params['url6']

        #Variables for SB loadgen script
        num_switch = main.params['LOADVARS']['numSw']
        num_port = main.params['LOADVARS']['numPort']
        sw_add_rate = main.params['LOADVARS']['swAddRate']
        gen_duration = main.params['LOADVARS']['genDur']
        time_sleep = main.params['LOADVARS']['timesleep']
        #NOTE: The loadgen timeout must be significant enough
        #      to ensure that the loadgen script finishes.
        loadgen_timeout = main.params['LOADVARS']['genTimeout'] 
        init_sleep = main.params['LOADVARS']['initSleep'] 
       
        global tpavg6n 
        tpavg6n = 0.0

        main.log.report("SB Throughput test - 6 ONOS instances")
      
        #NOTE: 
        # Here are the parameters for loadgen_SB.py at the time of 
        # writing this code:
        # -u : space separated URL string of to add load
        # -s : number of switches to add to each instance
        # -p : number of ports to add to each switch
        # -a : rate to add each switch / second
        # -l : length of time that load is generated
        # Refer to loadgen_SB.py --help for additional information
        # This script may take a while to run depending on 
        #      how many port / switch events you have added
        main.log.info("Please wait while loadgen script is running")
        main.Mininet2.handle.sendline(
                    "./loadgen_SB.py"+
                    " -u '"+ONOS1_ip+" "+ONOS2_ip+" "+ONOS3_ip+" "+
                            ONOS4_ip+" "+ONOS5_ip+" "+ONOS6_ip+"'"+
                    " -s "+num_switch+
                    " -a "+sw_add_rate+
                    " -p "+num_port+
                    " -l "+gen_duration+
                    " -t "+time_sleep)
        #Expect string that indicates loading has started 
        main.Mininet2.handle.expect(
                    "Starting SB load", 
                    timeout = int(loadgen_timeout))

        #Initial sleep before calling REST for metrics
        time.sleep(int(init_sleep))
        
        #Continue obtaining metrics from REST
        #and save the highest throughput
        temp_timestamp = 0
        loop_counter = 0
        temp_list = []
        rest_loop_count = main.params['LOADVARS']['loopCount']
        while True:
            json_obj_ONOS1 = main.ONOS2.get_json(url1)
            m1_rate_ONOS1 = json_obj_ONOS1['meters'][4]['meter']['m1_rate']
            
            temp_list.append(int(m1_rate_ONOS1))

            #If current measurement is greater than the previous one,
            #save the current measurement into global variable
            main.log.info("Current throughput average is: "+
                    str(m1_rate_ONOS1)+" events/second")

            loop_counter = loop_counter + 1

            time.sleep(3)
            if loop_counter == int(rest_loop_count):
                break
        

        tpavg6n = max(temp_list)
        main.log.report("SB Throughput for 6 ONOS instances: "+
                str(tpavg6n) + " Events / second")
        
        main.log.info("Please wait for cleanup")

        for i in range(1, 101):
            time.sleep(0.5)
            sys.stdout.write("\rProgress: "+str(i)+"%")
            sys.stdout.flush()
        
        #Ensure test is killed and MN is cleaned
        main.Mininet2.handle.sendline("sudo pkill -9 loadgen_SB")
        main.Mininet2.handle.sendline("sudo mn -c")
        main.Mininet2.handle.expect("\$", timeout=100)
    
    def CASE71(self,main):
        import time
        import json
        import math
        import sys

        ONOS1_ip = main.params['CTRL']['ip1']
        ONOS2_ip = main.params['CTRL']['ip2']
        ONOS3_ip = main.params['CTRL']['ip3']
        ONOS4_ip = main.params['CTRL']['ip4']
        ONOS5_ip = main.params['CTRL']['ip5']
        ONOS6_ip = main.params['CTRL']['ip6']
        ONOS7_ip = main.params['CTRL']['ip7']

        url1 = main.params['url1']
        url2 = main.params['url2']
        url3 = main.params['url3']
        url4 = main.params['url4']
        url5 = main.params['url5']
        url6 = main.params['url6']
        url7 = main.params['url7']

        #Variables for SB loadgen script
        num_switch = main.params['LOADVARS']['numSw']
        num_port = main.params['LOADVARS']['numPort']
        sw_add_rate = main.params['LOADVARS']['swAddRate']
        gen_duration = main.params['LOADVARS']['genDur']
        time_sleep = main.params['LOADVARS']['timesleep']
        #NOTE: The loadgen timeout must be significant enough
        #      to ensure that the loadgen script finishes.
        loadgen_timeout = main.params['LOADVARS']['genTimeout'] 
        init_sleep = main.params['LOADVARS']['initSleep'] 
       
        global tpavg7n 
        tpavg7n = 0.0

        main.log.report("SB Throughput test - 7 ONOS instances")
      
        #NOTE: 
        # Here are the parameters for loadgen_SB.py at the time of 
        # writing this code:
        # -u : space separated URL string of to add load
        # -s : number of switches to add to each instance
        # -p : number of ports to add to each switch
        # -a : rate to add each switch / second
        # -l : length of time that load is generated
        # Refer to loadgen_SB.py --help for additional information
        # This script may take a while to run depending on 
        #      how many port / switch events you have added
        main.log.info("Please wait while loadgen script is running")
        main.Mininet2.handle.sendline(
                    "./loadgen_SB.py"+
                    " -u '"+ONOS1_ip+" "+ONOS2_ip+" "+ONOS3_ip+" "+
                            ONOS4_ip+" "+ONOS5_ip+" "+ONOS6_ip+" "+
                            ONOS7_ip+"'"+
                    " -s "+num_switch+
                    " -a "+sw_add_rate+
                    " -p "+num_port+
                    " -l "+gen_duration+
                    " -t "+time_sleep)
        #Expect string that indicates loading has started 
        main.Mininet2.handle.expect(
                    "Starting SB load", 
                    timeout = int(loadgen_timeout))

        #Initial sleep before calling REST for metrics
        time.sleep(int(init_sleep))
        
        #Continue obtaining metrics from REST
        #and save the highest throughput
        temp_timestamp = 0
        loop_counter = 0
        temp_list = []
        rest_loop_count = main.params['LOADVARS']['loopCount']
        while True:
            json_obj_ONOS1 = main.ONOS2.get_json(url1)
            m1_rate_ONOS1 = json_obj_ONOS1['meters'][4]['meter']['m1_rate']
           
            temp_list.append(int(m1_rate_ONOS1))

            #If current measurement is greater than the previous one,
            #save the current measurement into global variable
            main.log.info("Current throughput average is: "+
                    str(m1_rate_ONOS1)+" events/second")

            loop_counter = loop_counter + 1

            time.sleep(3)
            if loop_counter == int(rest_loop_count):
                break
        
        tpavg7n = max(temp_list)

        main.log.report("SB Throughput for 7 ONOS instances: "+
                str(tpavg7n) + " Events / second")
        
        main.log.info("Please wait for cleanup")

        for i in range(1, 101):
            time.sleep(0.5)
            sys.stdout.write("\rProgress: "+str(i)+"%")
            sys.stdout.flush()
        
        #Ensure test is killed and MN is cleaned
        main.Mininet2.handle.sendline("sudo pkill -9 loadgen_SB")
        main.Mininet2.handle.sendline("sudo mn -c")
        main.Mininet2.handle.expect("\$", timeout=100)

        
    def CASE8(self,main):
        import time
        main.log.report("Scaling ONOS down to 6 ONOS instances")
        main.ONOS7.handle.sendline("./onos.sh core stop")
        time.sleep(8)
        pdata = main.ONOS7.isup()
        utilities.assert_equals(expect=main.FALSE,actual=pdata,
                onpass="ONOS7 stopped... ",
                onfail="ONOS scale down failed...")
        time.sleep(3)
        data = main.ONOS1.isup() and main.ONOS2.isup() \
                and main.ONOS3.isup() and main.ONOS4.isup()\
                and main.ONOS5.isup() and main.ONOS6.isup()
        for i in range(3):
            if data == main.FALSE: 
                time.sleep(3)
                data = main.ONOS1.isup() and main.ONOS2.isup()\
                        and main.ONOS3.isup() and main.ONOS4.isup()\
                        and main.ONOS5.isup() and main.ONOS6.isup()
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
                onpass="ONOS7 stopped... ",
                onfail="ONOS scale down failed...")
        data = main.ONOS1.isup() and main.ONOS2.isup()\
                and main.ONOS3.isup() and main.ONOS4.isup()\
                and main.ONOS5.isup()
        for i in range(3):
            if data == main.FALSE: 
                time.sleep(3)
                data = main.ONOS1.isup() and main.ONOS2.isup()\
                        and main.ONOS3.isup() and main.ONOS4.isup()\
                        and main.ONOS5.isup()
            else:
                break
        utilities.assert_equals(expect=main.TRUE,actual=data,
                onpass="Scale down successfull - 5 node ONOS clsuter is up and running!",
                onfail="ONOS didn't start...")

    def CASE10(self,main):

        main.log.report("Scaling ONOS down to 4 ONOS instances")
        
        main.ONOS5.handle.sendline("./onos.sh core stop ")
        time.sleep(5)
        pdata = main.ONOS5.isup() and main.ONOS6.isup() \
                and main.ONOS7.isup()
        utilities.assert_equals(expect=main.FALSE,actual=pdata,
                onpass="ONOS7 stopped... ",
                onfail="ONOS scale down failed...")
        data = main.ONOS1.isup() and main.ONOS2.isup()\
                and main.ONOS3.isup() and main.ONOS4.isup()
        for i in range(3):
            if data == main.FALSE: 
                time.sleep(3)
                data = main.ONOS1.isup() and main.ONOS2.isup()\
                        and main.ONOS3.isup() and main.ONOS4.isup()
            else:
                break
        utilities.assert_equals(expect=main.TRUE,actual=data,
                onpass="Scale down successful - 4 node ONOS cluster is up and running!",
                onfail="ONOS didn't start...")

    def CASE11(self,main):

        main.log.report("Scaling ONOS down to 3 ONOS instances")
        main.ONOS4.handle.sendline("./onos.sh core stop ")
        time.sleep(5)
        pdata = main.ONOS4.isup() and main.ONOS5.isup()\
                and  main.ONOS6.isup() and main.ONOS7.isup()
        utilities.assert_equals(expect=main.FALSE,actual=pdata,
                onpass="ONOS7 stopped... ",
                onfail="ONOS scale down failed...")
        data = main.ONOS1.isup() and main.ONOS2.isup()\
                and main.ONOS3.isup()
        for i in range(3):
            if data == main.FALSE: 
                time.sleep(3)
                data = main.ONOS1.isup() and main.ONOS2.isup()\
                        and main.ONOS3.isup()
            else:
                break
        utilities.assert_equals(expect=main.TRUE,actual=data,
                onpass="Scale down successful - 3 node ONOS cluster is up and running!",
                onfail="ONOS didn't start...")

    def CASE103(self,main):
        import os
        import time
        main.log.report("Posting the results to http://10.128.5.54/scale.html")
        db_script = main.params['db_script']
        os.system(db_script + " -n='100SwitchScaleUp" + 
                "' -rate3='" + str(tpavg3n) +
                "' -rate4='" + str(tpavg4n) +
                "' -rate5='" + str(tpavg5n) +
                "' -rate6='" + str(tpavg6n) +
                "' -rate7='" + str(tpavg7n) +
                "' -table='onos_scale'")
        main.log.report("The graphical view of the tests can be viewed at http://10.128.5.54/scale.html")

        #FIXME: Do meaningful assertion
        data = main.TRUE
        utilities.assert_equals(expect=main.TRUE,actual=data,
                onpass="Post to database succeeded",
                onfail="Post to databse failed")

    def CASE104(self,main):
        import os
        import time
        main.log.report("Posting the results to http://10.128.5.54/scale.html ....")
        db_script = main.params['db_script']
        os.system(db_script + " -n='100SwitchScaleDown" +
                "' -rate3='" + str(tpavg3n) +
                "' -rate4='" + str(tpavg4n) +
                "' -rate5='" + str(tpavg5n) +
                "' -rate6='" + str(tpavg6n) +
                "' -rate7='" + str(tpavg7n) +
                "' -table='onos_scale'")

        main.log.report("The graphical view of the tests can be viewed at http://10.128.5.54/scale.html")

        #FIXME: Do meaningful assertion
        data = main.TRUE
        utilities.assert_equals(expect=main.TRUE,actual=data,
                onpass="Post to database succeeded",
                onfail="Post to databse failed")

