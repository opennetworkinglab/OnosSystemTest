#!/usr/bin/env python
'''
Created on 31-May-2013 

@author: Anil Kumar (anilkumar.s@paxterrasolutions.com)      

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.        


''' 
import time
import pexpect
import struct, fcntl, os, sys, signal
import sys
import re
import json
sys.path.append("../")
from drivers.common.clidriver import CLI

class OnosCliDriver(CLI):
    
    def __init__(self):
        super(CLI, self).__init__()
        
    def connect(self,**connectargs):
	'''
        Creates ssh handle for ONOS. 
        '''
        for key in connectargs:
           vars(self)[key] = connectargs[key]

        
        self.name = self.options['name']
        self.handle = super(OnosCliDriver,self).connect(user_name = self.user_name, ip_address = self.ip_address,port = self.port, pwd = self.pwd)

        if self.handle:
            #self.start()
            #self.start_rest()
            return self.handle
        else :
            main.log.info("NO HANDLE")
            return main.FALSE
        
    def start(self):
        '''
        Starts ONOS on remote machine.
        Returns false if any errors were encountered. 
        '''
        self.handle.sendline("")
        self.handle.expect("\$")
        self.handle.sendline("~/ONOS/start-onos.sh start")
        self.handle.expect("onos.sh start")
        i=self.handle.expect(["Starting\sONOS\scontroller","Cassandra\sis\snot\srunning"])
        if i==0:
            try: 
                self.handle.expect("\$", timeout=60)
                main.log.info("ONOS Started ") 
            except:  
                main.log.info("ONOS NOT Started, stuck while waiting for it to start ") 
                return main.FALSE
            return main.TRUE
        elif i==1:
            main.log.error("ONOS didn't start because cassandra wasn't running.") 
            return main.FALSE
        
        main.log.error("ONOS expect script missed something... ") 
        return main.FALSE
 
    def start_embedded(self):
        self.handle.sendline("")
        self.handle.expect("\$")
        self.handle.sendline("~/ONOS/start-onos-embedded.sh start")
        try:
            self.handle.expect("start...")
            main.log.info("Embedded ONOS started")
        except:
            main.log.info("Embedded ONOS failed to start")

    def link_down(self, **linkParams):
        '''
        Specifically used for the ONOS demo on the HW.
        Should be replaced by actual switch drivers in the future.
        '''
        args = utilities.parse_args(["SDPID","SPORT","DDPID","DPORT"], **linkParams)
        sdpid = args["SDPID"] if args["SDPID"] != None else "00:00:00:00:ba:5e:ba:13"
        sport = args["SPORT"] if args["SPORT"] != None else "22"
        ddpid = args["DDPID"] if args["DDPID"] != None else "00:00:20:4e:7f:51:8a:35"
        dport = args["DPORT"] if args["DPORT"] != None else "22"
       
        cmd = "curl -s  10.128.4.11:9000/gui/link/down/" + sdpid + "/" + sport + "/" + ddpid + "/" + dport + " > /tmp/log &"
        os.popen( cmd ) 

    def link_up(self, **linkParams):
        '''
        Specifically used for the ONOS demo on the HW.
        Should be replaced by actual switch drivers in the future.
        '''
        args = utilities.parse_args(["SDPID","SPORT","DDPID","DPORT"], **linkParams)
        sdpid = args["SDPID"] if args["SDPID"] != None else "00:00:00:00:ba:5e:ba:13"
        sport = args["SPORT"] if args["SPORT"] != None else "22"
        ddpid = args["DDPID"] if args["DDPID"] != None else "00:00:20:4e:7f:51:8a:35"
        dport = args["DPORT"] if args["DPORT"] != None else "22"
       
        cmd = "curl -s  10.128.4.11:9000/gui/link/up/" + sdpid + "/" + sport + "/" + ddpid + "/" + dport + " > /tmp/log &"
        os.popen( cmd ) 

    def start_rest(self):
        '''
        Starts the rest server on ONOS.
        '''
        response = self.execute(cmd="~/ONOS/start-rest.sh start",prompt="\$",timeout=10)
        if re.search("admin",response):
            main.log.info("Rest Server Started Successfully")
            time.sleep(5)
            return main.TRUE
        else :
            main.log.warn("Failed to start Rest Server")   
            return main.FALSE     
        
    def status(self):
        '''
        Called start-onos.sh status and returns TRUE/FALSE accordingly 
        '''
        self.execute(cmd="\r",prompt="\$",timeout=10)
        response = self.execute(cmd="~/ONOS/start-onos.sh status ",prompt="\d+\sinstance\sof\sonos\srunning",timeout=10)
        self.execute(cmd="\r",prompt="\$",timeout=10)
        if re.search("1\sinstance\sof\sonos\srunning",response):
            return main.TRUE
        elif re.search("0\sinstance\sof\sonos\srunning",response):
            return main.FALSE
        else :
            return main.FALSE

    def isup(self):
        '''
        A more complete check to see if ONOS is up and running properly. 
        First, it checks if the process is up. 
        Second, it reads the logs for "Exception: Connection refused" 
        Third, it makes sure the logs are actually moving. 
        returns TRUE/FALSE accordingly.
        '''
        self.execute(cmd="\r",prompt="\$",timeout=10)
        response = self.execute(cmd="~/ONOS/start-onos.sh status ",prompt="running",timeout=10)
        self.execute(cmd="\r",prompt="\$",timeout=10)
        tail1 = self.execute(cmd="tail ~/ONOS/onos-logs/onos.*.log",prompt="\$",timeout=10)
        time.sleep(30)
        self.execute(cmd="\r",prompt="\$",timeout=10)
        tail2 = self.execute(cmd="tail ~/ONOS/onos-logs/onos.*.log",prompt="\$",timeout=10)
        pattern = '(.*)1 instance(.*)'
        pattern2 = '(.*)Exception: Connection refused(.*)'
        if utilities.assert_matches(expect=pattern,actual=response,onpass="ONOS process is running...",onfail="ONOS process not running..."):
            if tail1 == tail2:
                main.log.error("ONOS is frozen...")
                return main.FALSE
            elif re.search( pattern2,tail1 ):
                main.log.info("Connection Refused found in onos log") 
                return main.FALSE
            elif re.search( pattern2,tail2 ):
                main.log.info("Connection Refused found in onos log") 
                return main.FALSE
            else:
                main.log.info("Onos log is moving! It's looking good!")
                return main.TRUE
        else:
            return main.FALSE

    
    def rest_status(self): 
        '''
        Checks if the rest server is running. 
        '''
        response = self.execute(cmd="~/ONOS/start-rest.sh status ",prompt="running",timeout=10)
        if re.search("rest\sserver\sis\srunning",response):
            main.log.info("Rest Server is running")
        elif re.search("rest\sserver\sis\snot\srunning",response):
            main.log.warn("Rest Server is not Running")
        else :
            main.log.error("No response" +response)
        self.execute(cmd="\r",prompt="\$",timeout=10)
        
        return response
    
    def stop(self):
        '''
        Runs ./start-onos.sh stop to stop ONOS
        '''
        self.handle.sendline("")
        self.handle.expect("\$")
        self.handle.sendline("~/ONOS/start-onos.sh stop")
        self.handle.expect("stop", 2)
        result = self.handle.before 
        self.handle.expect("\$", 60)
        if re.search("Killed", result):
            main.log.info("ONOS Killed Successfully")
            return main.TRUE
        else :
            main.log.warn("ONOS wasn't running")
            return main.FALSE
    
    def rest_stop(self):
        '''
        Runs ./start-rest.sh stop to stop ONOS rest server
        '''
        response = self.execute(cmd="~/ONOS/start-rest.sh stop ",prompt="killing",timeout=10)
        self.execute(cmd="\r",prompt="\$",timeout=10)
        if re.search("killing", response):
            main.log.info("Rest Server Stopped")
            return main.TRUE
        else :
            main.log.error("Failed to Stop, Rest Server is not Running")
            return main.FALSE
        
    def disconnect(self):
        '''
        Called when Test is complete to disconnect the ONOS handle.  
        '''
        response = ''
        try:
            self.handle.sendline("exit")
            self.handle.expect("closed")
        except: 
            main.log.error("Connection failed to the host")
            response = main.FALSE
        return response
 
    def get_version(self):
        ''' 
        Writes the COMMIT number to the report to be parsed by Jenkins data collecter.  
        '''
        self.handle.sendline("export TERM=xterm-256color")
        self.handle.expect("xterm-256color")
        self.handle.expect("\$") 
        self.handle.sendline("cd ONOS; git log -1 | grep -A 3 \"commit\"; cd \.\.")
        self.handle.expect("cd ..")
        self.handle.expect("\$")
        main.log.report( str(self.handle.before + self.handle.after))

    def add_flow(self, path):
        ''' 
        Copies the flowdef file from TestStation -> ONOS machine
        Then runs ./add_flow.py to add the flows to ONOS
        ''' 
        main.log.info("Adding Flows...")
        self.handle.sendline("scp admin@10.128.7.7:%s /tmp/flowtmp" % path) 
        self.handle.expect("100%")
        self.handle.expect("\$", 30)
        self.handle.sendline("~/ONOS/web/add_flow.py -m onos -f /tmp/flowtmp") 
        self.handle.expect("add_flow")
        self.handle.expect("\$", 1000)
        main.log.info("Flows added")

    def delete_flow(self, *delParams):
        '''
        Deletes a specific flow, a range of flows, or all flows.
        '''
        if len(delParams)==1:
             if str(delParams[0])=="all":
                  main.log.info("Deleting ALL flows...")
                  #self.execute(cmd="~/ONOS/scripts/TestON_delete_flow.sh all",prompt="done",timeout=150)
                  self.handle.sendline("~/ONOS/web/delete_flow.py all")
                  self.handle.expect("delete_flow")
                  self.handle.expect("\$",1000)
                  main.log.info("Flows deleted")
             else:
                  main.log.info("Deleting flow "+str(delParams[0])+"...")
                  #self.execute(cmd="~/ONOS/scripts/TestON_delete_flow.sh "+str(delParams[0]),prompt="done",timeout=150)
                  #self.execute(cmd="\n",prompt="\$",timeout=60)
                  self.handle.sendline("~/ONOS/web/delete_flow.py %d" % int(delParams[0]))
                  self.handle.expect("delete_flow")
                  self.handle.expect("\$",60)
                  main.log.info("Flow deleted")
        elif len(delParams)==2:
             main.log.info("Deleting flows "+str(delParams[0])+" through "+str(delParams[1])+"...")
             #self.execute(cmd="~/ONOS/scripts/TestON_delete_flow.sh "+str(delParams[0])+" "+str(delParams[1]),prompt="done",timeout=150)
             #self.execute(cmd="\n",prompt="\$",timeout=60)
             self.handle.sendline("~/ONOS/web/delete_flow.py %d %d" % (int(delParams[0]), int(delParams[1])))
             self.handle.expect("delete_flow")
             self.handle.expect("\$",600)
             main.log.info("Flows deleted")

    def check_flow(self):
        '''
        Calls the ./get_flow.py all and checks:
          - If each FlowPath has at least one FlowEntry  
          - That there are no "NOT"s found
        returns TRUE/FALSE 
        '''
        flowEntryDetect = 1
        count = 0
        self.handle.sendline("clear")
        time.sleep(1)
        self.handle.sendline("~/ONOS/web/get_flow.py all")
        self.handle.expect("get_flow")
        while 1:
            i=self.handle.expect(['FlowPath','FlowEntry','NOT','\$',pexpect.TIMEOUT],timeout=180)
            if i==0:
                count = count + 1
                if flowEntryDetect == 0:
                    main.log.info("FlowPath without FlowEntry")
                    return main.FALSE
                else:
                    flowEntryDetect = 0
            elif i==1:
                flowEntryDetect = 1
            elif i==2:
                main.log.error("Found a NOT")
                return main.FALSE
            elif i==3:
                if count == 0:
                    main.log.info("There don't seem to be any flows here...")
                    return main.FALSE
                else:
                    main.log.info("All flows pass")
                    main.log.info("Number of FlowPaths: "+str(count))
                    return main.TRUE
            elif i==4:
                main.log.error("Command Timeout!")
                return main.FALSE

    def get_flow(self, *flowParams):
         '''
         Returns verbose output of ./get_flow.py
         '''
         if len(flowParams)==1:
              if str(flowParams[0])=="all":
                   self.execute(cmd="\n",prompt="\$",timeout=60)
                   main.log.info("Getting all flow data...")
                   data = self.execute(cmd="~/ONOS/scripts/TestON_get_flow.sh all",prompt="done",timeout=150)
                   self.execute(cmd="\n",prompt="\$",timeout=60)
                   return data
              else:
                   main.log.info("Retrieving flow "+str(flowParams[0])+" data...")
                   data = self.execute(cmd="~/ONOS/scripts/TestON_get_flow.sh "+str(flowParams[0]),prompt="done",timeout=150)
                   self.execute(cmd="\n",prompt="\$",timeout=60)
                   return data
         elif len(flowParams)==5:
              main.log.info("Retrieving flow installer data...")
              data = self.execute(cmd="~/ONOS/scripts/TestON_get_flow.sh "+str(flowParams[0])+" "+str(flowParams[1])+" "+str(flowParams[2])+" "+str(flowParams[3])+" "+str(flowParams[4]),prompt="done",timeout=150)
              self.execute(cmd="\n",prompt="\$",timeout=60)
              return data
         elif len(flowParams)==4:
              main.log.info("Retrieving flow endpoints...")
              data = self.execute(cmd="~/ONOS/scripts/TestON_get_flow.sh "+str(flowParams[0])+" "+str(flowParams[1])+" "+str(flowParams[2])+" "+str(flowParams[3]),prompt="done",timeout=150)
              self.execute(cmd="\n",prompt="\$",timeout=60)
              return data


# http://localhost:8080/wm/core/topology/switches/all/json
# http://localhost:8080/wm/core/topology/links/json
# http://localhost:8080/wm/registry/controllers/json
# http://localhost:8080/wm/registry/switches/json"

    def get_json(self, url):
        '''
        Helper functions used to parse the json output of a rest call 
        '''
        try:
            command = "curl -s %s" % (url)
            result = os.popen(command).read()
            parsedResult = json.loads(result)
        except:
            print "REST IF %s has issue" % command
            parsedResult = ""
    
        if type(parsedResult) == 'dict' and parsedResult.has_key('code'):
            print "REST %s returned code %s" % (command, parsedResult['code'])
            parsedResult = ""
        return parsedResult 

    def check_switch(self,RestIP,correct_nr_switch ):
        ''' 
        Used by check_status 
        ''' 
        buf = ""
        retcode = 0
        RestPort="8080"
        url="http://%s:%s/wm/onos/topology/switches/all/json" % (RestIP, RestPort)
        parsedResult = self.get_json(url)
        if parsedResult == "":
            retcode = 1
            return (retcode, "Rest API has an issue")
        url = "http://%s:%s/wm/onos/registry/switches/json" % (RestIP, RestPort)
        registry = self.get_json(url)
    
        if registry == "":
            retcode = 1
            return (retcode, "Rest API has an issue")
    
        cnt = 0
        active = 0

        for s in parsedResult:
            cnt += 1
            if s['state']  == "ACTIVE":
               active += 1

        buf += "switch: network %d : %d switches %d active\n" % (0+1, cnt, active)
        if correct_nr_switch != cnt:
            buf += "switch fail: network %d should have %d switches but has %d\n" % (1, correct_nr_switch, cnt)
            retcode = 1

        if correct_nr_switch != active:
            buf += "switch fail: network %d should have %d active switches but has %d\n" % (1, correct_nr_switch, active)
            retcode = 1
    
        return (retcode, buf)

    def check_link(self,RestIP, nr_links):
        ''' 
        Used by check_status 
        ''' 
        RestPort = "8080"
        buf = ""
        retcode = 0
    
        url = "http://%s:%s/wm/onos/topology/links/json" % (RestIP, RestPort)
        parsedResult = self.get_json(url)
    
        if parsedResult == "":
            retcode = 1
            return (retcode, "Rest API has an issue")
    
        buf += "link: total %d links (correct : %d)\n" % (len(parsedResult), nr_links)
        intra = 0
        interlink=0
    
        for s in parsedResult:
            intra = intra + 1 
    
        if intra != nr_links:
            buf += "link fail\n"
            retcode = 1
    
        return (retcode, buf)

    def check_status_report(self, ip, numoswitch, numolink):
        ''' 
        Checks the number of swithes & links that ONOS sees against the supplied values.
        Writes to the report log.  
        ''' 
        main.log.info("Making some rest calls...") 
        switch = self.check_switch(ip, int(numoswitch))
        link = self.check_link(ip, int(numolink))
        value = switch[0]
        value += link[0]
        main.log.report( "\n-----\n%s%s-----\n" % ( switch[1], link[1]) )
        if value != 0:
            return 0
        else: 
            # "PASS"
            return 1

    def check_status(self, ip, numoswitch, numolink):
        ''' 
        Checks the number of swithes & links that ONOS sees against the supplied values.
        Writes to the main log.  
        ''' 
        main.log.info("Making some rest calls...") 
        switch = self.check_switch(ip, int(numoswitch))
        link = self.check_link(ip, int(numolink))
        value = switch[0]
        value += link[0]
        main.log.info( "\n-----\n%s%s-----\n" % ( switch[1], link[1]) )
        if value != 0:
            return 0
        else: 
            # "PASS"
            return 1
 
    def drop_keyspace(self):
        '''
        Drops the ONOS keyspace
        '''
        self.handle.sendline("~/ONOS/scripts/test-drop-keyspace.sh")
        self.handle.expect("keyspace")
        self.handle.sendline("")
        self.handle.expect("\$")
        self.handle.expect("\$")
        main.log.info("Keyspace dropped")

    def ctrl_none(self):
        '''
        Points all the mininet swithces to no controllers 
        *NOTE will only work if CLUSTER is set up on ONOS nodes
        '''
        self.execute(cmd="switch none", prompt="\$",timeout=10)

    def ctrl_one(self, ip):
        '''
        Points all the mininet swithces to all controllers 
        *NOTE will only work if CLUSTER is set up on ONOS nodes
        '''
        self.execute(cmd="switch one", prompt="\$",timeout=10)

    def check_for_no_exceptions(self):
        '''
        Used by CassndraCheck.py to scan ONOS logs for Exceptions
        '''
        self.handle.sendline("dsh 'grep Exception ~/ONOS/onos-logs/onos.*.log'")
        self.handle.expect("\$ dsh") 
        self.handle.expect("\$")
        output = self.handle.before
        main.log.info( output ) 
        if re.search("Exception",output):
            return main.FALSE
        else :
            return main.TRUE
 
    def git_pull(self):
        '''
        Stops the ONOS, pulls the latest code, and builds with mvn. 
        Assumes that "git pull" works without login 
        '''
        main.log.info("Stopping onos") 
        self.stop()
        self.handle.sendline("cd ~/ONOS") 
        self.handle.expect("ONOS\$")
        self.handle.sendline("git pull")
       
        uptodate = 0 
        i=self.handle.expect(['fatal','Username\sfor\s(.*):\s','Unpacking\sobjects',pexpect.TIMEOUT,'Already up-to-date','Aborting'],timeout=180)
        if i==0:
            main.log.error("Git pull had some issue...") 
            return main.FALSE
        elif i==1:
            main.log.error("Asking for username!!! BADD!") 
            return false 
            
            self.handle.expect('Password\sfor\s(.*):\s')
            j = self.handle.expect(['Unpacking\sobjects','Already up-to-date'])
            if j == 0:
                main.log.info("pulling repository now")
            elif j == 1:
                main.log.info("Up to date!")
            else:
                main.log.error("something went wrong")
                return main.FALSE
            self.handle.expect("ONOS\$", 120)
        elif i==2:
            main.log.info("pulling repository now")
            self.handle.expect("ONOS\$", 120)
        elif i==3:
            main.log.error("TIMEOUT")
            return main.FALSE
        elif i==4:
            main.log.info("Already up to date")
            uptodate = 1 
        elif i==5:
            main.log.info("Aborting... Are there conflicting git files?")
            return main.FALSE
        
        '''        
        main.log.info("./setup-local-maven.sh")
        self.handle.sendline("./setup-local-maven.sh")
        self.handle.expect("local-maven.sh")
        while 1: 
            i=self.handle.expect(['BUILD\sFAILURE','BUILD\sSUCCESS','ONOS\$',pexpect.TIMEOUT],timeout=90)
            if i == 0:
                main.log.error("Build failure!")
                return main.FALSE
            elif i == 1:
                main.log.info("Build success!")
            elif i == 2:
                main.log.info("Build complete") 
                break;
            elif i == 3:
                main.log.error("TIMEOUT!")
                return main.FALSE
        '''      
        if uptodate == 0:
            main.log.info("mvn clean") 
            self.handle.sendline("mvn clean")
            while 1: 
                i=self.handle.expect(['BUILD\sFAILURE','BUILD\sSUCCESS','ONOS\$',pexpect.TIMEOUT],timeout=30)
                if i == 0:
                    main.log.error("Build failure!")
                    return main.FALSE
                elif i == 1:
                    main.log.info("Build success!")
                elif i == 2:
                    main.log.info("Build complete") 
                    break;
                elif i == 3:
                    main.log.error("TIMEOUT!")
                    return main.FALSE
        
            main.log.info("mvn compile") 
            self.handle.sendline("mvn compile")
            while 1: 
                i=self.handle.expect(['BUILD\sFAILURE','BUILD\sSUCCESS','ONOS\$',pexpect.TIMEOUT],timeout=30)
                if i == 0:
                    main.log.error("Build failure!")
                    return main.FALSE
                elif i == 1:
                    main.log.info("Build success!")
                elif i == 2:
                    main.log.info("Build complete") 
                    break;
                elif i == 3:
                    main.log.error("TIMEOUT!")
                    return main.FALSE

    def tcpdump(self):
        self.handle.sendline("")
        self.handle.expect("\$")
        self.handle.sendline("sudo tcpdump -n -i eth0 -s0 -w onos-logs/tcpdump &")
  
    def kill_tcpdump(self):
        self.handle.sendline("")
        self.handle.expect("\$")
        self.handle.sendline("sudo kill -9 `ps -ef | grep \"tcpdump -n\" | grep -v grep | awk '{print $2}'`")
