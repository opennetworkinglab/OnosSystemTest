#!/usr/bin/env python
'''
'''

import pexpect
import struct
import fcntl
import os
import signal
import re
import sys
import core.teston
import time
import json
import traceback
import requests
import urllib2
sys.path.append("../")
from drivers.common.clidriver import CLI

class onossanityclidriver(CLI):
    '''
    '''
    def __init__(self):
        super(CLI, self).__init__()

    def connect(self,**connectargs):
        '''
        Creates ssh handle for ONOS.
        '''
        try:
            for key in connectargs:
                vars(self)[key] = connectargs[key]
            self.home = "~/ONOS"
            for key in self.options:
                if key == "home":
                    self.home = self.options['home']
                    break

            
            self.name = self.options['name']
            self.handle = super(onossanityclidriver,self).connect(user_name = self.user_name, ip_address = self.ip_address,port = self.port, pwd = self.pwd, home = self.home)

            if self.handle:
                return self.handle
            else :
                main.log.info("NO ONOS HANDLE")
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()   
 
    def start(self):
        '''
        Starts ONOS on remote machine.
        Returns false if any errors were encountered.
        '''
        try:
            self.handle.sendline("")
            self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
            self.handle.sendline("cd "+self.home)
            self.handle.sendline("./onos.sh zk start") 
	    self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
            self.handle.sendline("./onos.sh rc deldb")
            self.handle.sendline("y")
            self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
	    #Send a confirmation to delete ramcloud
	    #self.handle.sendline("y")
	    main.log.info("Ramcloud db deleted")
            #self.handle.sendline("./onos.sh zk start")
            #Check if zookeeper is running
            #delete database ./onos.sh rc deldb
            #main.log.info(self.name + ": ZooKeeper Started Separately")
	    self.handle.sendline("./onos.sh start")
            i=self.handle.expect(["STARTED","FAILED","running",pexpect.EOF,pexpect.TIMEOUT])
            if i==0:
                    main.log.info(self.name + ": ZooKeeper, Ramcloud and ONOS Started ")
                    return main.TRUE
            elif i==1:
                main.log.error(self.name + ": Failed to start")
                return main.FALSE
	    elif i==2:
		main.log.info(self.name + ": Already running, so Restarting ONOS")
		self.handle.sendline("./onos.sh restart")
		j=self.handle.expect(["STARTED","FAILED",pexpect.EOF,pexpect.TIMEOUT])
		if j==0:
		    main.log.info(self.name + ": ZooKeeper, Ramcloud and ONOS Started ")
		    return main.TRUE
		else:
		    main.log.error(self.name + ": ONOS Failed to Start")
            elif i==3:
                main.log.error(self.name + ": EOF exception found")
                main.log.error(self.name + ":     " + self.handle.before)
                main.cleanup()
	    elif i==2:
		main.log.info(self.name + ": Already running, so Restarting ONOS")
		self.handle.sendline("./onos.sh restart")
		j=self.handle.expect(["STARTED","FAILED",pexpect.EOF,pexpect.TIMEOUT])
		if j==0:
		    main.log.info(self.name + ": ZooKeeper, Ramcloud and ONOS Started ")
		    return main.TRUE
		elif j==1:
		    main.log.error(self.name + ": ONOS Failed to Start")
		    main.log.info(self.name + ": cleaning up and exiting...")
		    main.cleanup()
		    main.exit()
		elif j==2: 
		    main.log.error(self.name + ": EOF exception found")
		    main.log.error(self.name + ":    " + self.handle.before)
		    main.log.info(self.name + ": cleaning up and exiting...")
		    main.cleanup()
		    main.exit() 
            elif i==3:
                main.log.error(self.name + ": EOF exception found")
                main.log.error(self.name + ":     " + self.handle.before)
                main.cleanup()
                main.exit()
            elif i==4:
                main.log.error(self.name + ": ONOS timedout while starting")
                return main.FALSE
            else:
                main.log.error(self.name + ": ONOS start  expect script missed something... ")
            return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()
    
    def status(self):
        '''
        Calls onos.sh core status and returns TRUE/FALSE accordingly
        '''
        try:
            self.execute(cmd="\n",prompt="\$",timeout=10)
            self.handle.sendline("cd "+self.home)
            response = self.execute(cmd="./onos.sh core status ",prompt="\d+\sinstance\sof\sonos\srunning",timeout=10)
            self.execute(cmd="\n",prompt="\$",timeout=10)
            if re.search("1\sinstance\sof\sonos\srunning",response):
                return main.TRUE
            elif re.search("0\sinstance\sof\sonos\srunning",response):
                return main.FALSE
            else :
                main.log.info( self.name + " WARNING: status recieved unknown response")
		main.log.info( self.name + " For details: check onos core status manually")
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def zk_status(self):
        '''
        Calls the zookeeper status and returns TRUE if it has an assigned Mode to it. 
        '''
        try:
	    self.execute(cmd="\n",prompt="\$",timeout=10)
            self.handle.sendline("cd "+self.home)
	    self.handle.sendline("./onos.sh zk status")
	    i=self.handle.expect(["standalone","Error",pexpect.EOF,pexpect.TIMEOUT])
            if i==0: 
	        main.log.info(self.name + ": Zookeeper is running.") 
                return main.TRUE
            elif i==1:
	        main.log.error(self.name + ": Error with zookeeper") 
                main.log.info(self.name + ": Directory used: "+self.home)
		return main.FALSE
	    elif i==3:
		main.log.error(self.name + ": Zookeeper timed out")
		main.log.info(self.name + ": Directory used: "+self.home)
		return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()	

    def rcs_status(self):
        '''
        This Function will return the Status of the RAMCloud Server
        '''
        main.log.info(self.name + ": Getting RC-Server Status")
        self.handle.sendline("")
        self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
        self.handle.sendline("cd "+self.home)
        self.handle.sendline("./onos.sh rc-server status")
        self.handle.expect(["onos.sh rc-server status",pexpect.EOF,pexpect.TIMEOUT])
        self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
        response = self.handle.before + self.handle.after

        if re.search("0\sRAMCloud\sserver\srunning", response) :
            main.log.info(self.name+": RAMCloud not running")
            return main.TRUE
        elif re.search("1\sRAMCloud\sserver\srunning",response):
            main.log.warn(self.name+": RAMCloud Running")
            return main.TRUE
        else:
            main.log.info( self.name+":  WARNING: status recieved unknown response")
            return main.FALSE
            
    def rcc_status(self):
        '''
        This Function will return the Status of the RAMCloud Coord
        '''
        main.log.info(self.name + ": Getting RC-Coord Status")
        self.handle.sendline("")
        self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
        self.handle.sendline("cd "+self.home)
        self.handle.sendline("./onos.sh rc-coord status")
        i=self.handle.expect(["onos.sh rc-coord status",pexpect.EOF,pexpect.TIMEOUT])
        self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
        response = self.handle.before + self.handle.after
        #return response
        
        if re.search("0\sRAMCloud\scoordinator\srunning", response) :
            main.log.warn(self.name+": RAMCloud Coordinator not running")
            return main.TRUE
        elif re.search("1\sRAMCloud\scoordinator\srunning", response):
            main.log.info(self.name+": RAMCloud Coordinator Running")
            return main.TRUE
        else:
            main.log.warn( self.name+": coordinator status recieved unknown response")
            return main.FALSE

    def stop(self):
        '''
        Runs ./onos.sh stop to stop ONOS
        '''
        try:
            self.handle.sendline("")
            self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
            self.handle.sendline("cd "+self.home)
            self.handle.sendline("./onos.sh stop")
            i=self.handle.expect(["Stop",pexpect.EOF,pexpect.TIMEOUT])
            self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT], 60)
            result = self.handle.before
            if re.search("Killed", result):
                main.log.info(self.name + ": ONOS Killed Successfully")
                return main.TRUE
            else :
                main.log.warn(self.name + ": ONOS wasn't running")
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def start_rest(self):
        '''
        Starts the rest server on ONOS.
        '''
        try:
            self.handle.sendline("cd "+self.home)
            response = self.execute(cmd= "./start-rest.sh start",prompt="\$",timeout=10)
            if re.search(self.user_name,response):
                main.log.info(self.name + ": Rest Server Started Successfully")
                time.sleep(5)
                return main.TRUE
            else :
                main.log.warn(self.name + ": Failed to start Rest Server")
		main.log.info(self.name + ": Directory used: "+self.home )
		main.log.info(self.name + ": Rest server response: "+response)
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def rest_stop(self):
        '''
        Runs ./start-rest.sh stop to stop ONOS rest server
        '''
        try:
            response = self.execute(cmd= self.home + "./start-rest.sh stop ",prompt="killing",timeout=10)
            self.execute(cmd="\n",prompt="\$",timeout=10)
            if re.search("killing", response):
                main.log.info(self.name + ": Rest Server Stopped")
                return main.TRUE
            else :
                main.log.error(self.name + ": Failed to Stop, Rest Server is not Running")
		main.log.info(self.name + ": Directory used: "+self.home)
		main.log.info(self.name + ": Rest server response: " + response)
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def rest_status(self):
        '''
        Checks if the rest server is running.
        '''
        #this function does not capture the status response correctly...
        #when cmd is executed, the prompt expected should be a string containing
        #status message, but instead returns the user@user$ Therefore prompt="running"
        #was changed to prompt="\$"
        try:
            response = self.execute(cmd= self.home + "./start-rest.sh status ",prompt="\$",timeout=10)
            if re.search(self.user_name,response):
                main.log.info(self.name + ": Rest Server is running")
                return main.TRUE
            elif re.search("rest\sserver\sis\snot\srunning",response):
                main.log.warn(self.name + ": Rest Server is not Running")
                return main.FALSE
            else :
                main.log.error(self.name + ": No response" +response)
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def disconnect(self):
        '''
        Called when Test is complete to disconnect the ONOS handle.
        '''
        response = ''
        try:
            self.handle.sendline("exit")
            self.handle.expect("closed")
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
        except:
            main.log.error(self.name + ": Connection failed to the host")
            response = main.FALSE
        return response
 
    def print_version(self):
        '''
        Writes the COMMIT number to the report to be parsed by Jenkins data collecter.
        '''
        try:
            self.handle.sendline("export TERM=xterm-256color")
            self.handle.expect("xterm-256color")
            self.handle.expect("\$")
            self.handle.sendline("cd " + self.home + "; git log -1 --pretty=fuller | grep -A 5 \"commit\"; cd \.\.")
            self.handle.expect("cd ..")
            self.handle.expect("\$")
            response=(self.name +": \n"+ str(self.handle.before + self.handle.after))
            main.log.report(response)
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
    def get_version(self):
        '''
        Writes the COMMIT number to the report to be parsed by Jenkins data collecter.
        '''
        try:
            self.handle.sendline("export TERM=xterm-256color")
            self.handle.expect("xterm-256color")
            self.handle.expect("\$")
            self.handle.sendline("cd " + self.home + "; git log -1 --pretty=fuller | grep -A 5 \"commit\"; cd \.\.")
            self.handle.expect("cd ..")
            self.handle.expect("\$")
            response=(self.name +": \n"+ str(self.handle.before + self.handle.after))
            lines=response.splitlines()
            for line in lines:
                print line
            return lines[2]
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def add_flow(self, intentFile, path):
	try:
            main.log.info("add_flow running...")
	    main.log.info("using directory: "+path) 
            time.sleep(10)
            self.handle.sendline("cd " + path)
            #self.handle.expect("tests")
            self.handle.sendline("./"+intentFile)
            time.sleep(10)
            self.handle.sendline("cd "+self.home)
            return main.TRUE
	except pexpect.EOF:
	    main.log.error(self.name + ": EOF exception found")
	    main.log.error(self.name + ":    " + self.handle.before)
	    main.cleanup()
	    main.exit()
	except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
	    main.log.error( traceback.print_exc() )	       
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
	    main.cleanup()
	    main.exit()

    def delete_flow(self, intentFile, path):
	try:
            main.log.info("delete_flow running...")
	    main.log.info("using directory: " + path)
	    main.log.info("using file: " + intentFile)
            self.handle.sendline("cd " + path)
            self.handle.expect("tests")
            self.handle.sendline("./" + intentFile)
            time.sleep(10)
            self.handle.sendline("cd "+self.home)
            return main.TRUE
	except pexepct.EOF:
	    main.log.error(self.name + ": EOF exception found")
	    main.log.error(self.name + ":    " + self.handle.before)
	    main.cleanup()
	    main.exit()
	except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
	    main.log.error( traceback.print_exc() )	       
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
	    main.cleanup()
	    main.exit()	

    def check_flow(self):
        '''
        Calls the ./get_flow.py all and checks:
        - If each FlowPath has at least one FlowEntry
        - That there are no "NOT"s found
        returns TRUE/FALSE
        '''
        try:
            flowEntryDetect = 1
            count = 0
            self.handle.sendline("clear")
            time.sleep(1)
            self.handle.sendline(self.home + "/web/get_flow.py all")
            self.handle.expect("get_flow")
            while 1:
                i=self.handle.expect(['FlowPath','FlowEntry','NOT','\$',pexpect.TIMEOUT],timeout=180)
                if i==0:
                    count = count + 1
                    if flowEntryDetect == 0:
                        main.log.info(self.name + ": FlowPath without FlowEntry")
                        return main.FALSE
                    else:
                        flowEntryDetect = 0
                elif i==1:
                    flowEntryDetect = 1
                elif i==2:
                    main.log.error(self.name + ": Found a NOT")
                    return main.FALSE
                elif i==3:
                    if count == 0:
                        main.log.info(self.name + ": There don't seem to be any flows here...")
                        return main.FALSE
                    else:
                        main.log.info(self.name + ": All flows pass")
                        main.log.info(self.name + ": Number of FlowPaths: "+str(count))
                        return main.TRUE
                elif i==4:
                    main.log.error(self.name + ":Check_flow() - Command Timeout!")
            return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def get_flow(self, *flowParams):
        '''
        Returns verbose output of ./get_flow.py
        '''
        try:
            if len(flowParams)==1:
                if str(flowParams[0])=="all":
                    self.execute(cmd="\n",prompt="\$",timeout=60)
                    main.log.info(self.name + ": Getting all flow data...")
                    data = self.execute(cmd=self.home + "/scripts/TestON_get_flow.sh all",prompt="done",timeout=150)
                    self.execute(cmd="\n",prompt="\$",timeout=60)
                    return data
                else:
                    main.log.info(self.name + ": Retrieving flow "+str(flowParams[0])+" data...")
                    data = self.execute(cmd=self.home +"/scripts/TestON_get_flow.sh "+str(flowParams[0]),prompt="done",timeout=150)
                    self.execute(cmd="\n",prompt="\$",timeout=60)
                    return data
            elif len(flowParams)==5:
                main.log.info(self.name + ": Retrieving flow installer data...")
                data = self.execute(cmd=self.home + "/scripts/TestON_get_flow.sh "+str(flowParams[0])+" "+str(flowParams[1])+" "+str(flowParams[2])+" "+str(flowParams[3])+" "+str(flowParams[4]),prompt="done",timeout=150)
                self.execute(cmd="\n",prompt="\$",timeout=60)
                return data
            elif len(flowParams)==4:
                main.log.info(self.name + ": Retrieving flow endpoints...")
                data = self.execute(cmd=self.home + "/scripts/TestON_get_flow.sh "+str(flowParams[0])+" "+str(flowParams[1])+" "+str(flowParams[2])+" "+str(flowParams[3]),prompt="done",timeout=150)
                self.execute(cmd="\n",prompt="\$",timeout=60)
                return data
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()


# http://localhost:8080/wm/onos/ng/switches/json
# http://localhost:8080/wm/onos/ng/links/json
# http://localhost:8080/wm/onos/registry/controllers/json
# http://localhost:8080/wm/onos/registry/switches/json"

    def get_json(self, url):
        '''
        Helper functions used to parse the json output of a rest call
        '''
        try:
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
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def check_switch(self,RestIP,correct_nr_switch, RestPort ="8080" ):
        '''
        Used by check_status
        '''
        try:
            buf = ""
            retcode = 0
            url="http://%s:%s/wm/onos/topology/switches" % (RestIP, RestPort)
            parsedResult = self.get_json(url)
            if parsedResult == "":
                retcode = 1
                return (retcode, "Rest API has an issue")
            url = "http://%s:%s/wm/onos/registry/switches" % (RestIP, RestPort)
            registry = self.get_json(url)
        
            if registry == "":
                retcode = 1
                return (retcode, "Rest API has an issue")
        
            cnt = 0
            active = 0

            for s in parsedResult:
                cnt += 1
                if s['state'] == "ACTIVE":
                   active += 1

            buf += "switch: network %d : %d switches %d active\n" % (0+1, cnt, active)
            if correct_nr_switch != cnt:
                buf += "switch fail: network %d should have %d switches but has %d\n" % (1, correct_nr_switch, cnt)
                retcode = 1

            if correct_nr_switch != active:
                buf += "switch fail: network %d should have %d active switches but has %d\n" % (1, correct_nr_switch, active)
                retcode = 1
        
            return (retcode, buf)
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def check_link(self,RestIP, nr_links, RestPort = "8080"):
        '''
        Used by check_status
        '''
        try:
            buf = ""
            retcode = 0
        
            url = "http://%s:%s/wm/onos/topology/links" % (RestIP, RestPort)
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
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def check_status_report(self, ip, numoswitch, numolink, port="8080"):
        '''
        Checks the number of swithes & links that ONOS sees against the supplied values.
        Writes to the report log.
        '''
        try:
            main.log.info(self.name + ": Making some rest calls...")
            switch = self.check_switch(ip, int(numoswitch), port)
            link = self.check_link(ip, int(numolink), port)
            value = switch[0]
            value += link[0]
            main.log.report( self.name + ": \n-----\n%s%s-----\n" % ( switch[1], link[1]) )
            if value != 0:
                return main.FALSE
            else:
                # "PASS"
                return main.TRUE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def check_status(self, ip, numoswitch, numolink, port = "8080"):
        '''
        Checks the number of swithes & links that ONOS sees against the supplied values.
        Writes to the main log.
        '''
        try:
            main.log.info(self.name + ": Making some rest calls...")
            switch = self.check_switch(ip, int(numoswitch), port)
            link = self.check_link(ip, int(numolink), port)
            value = switch[0]
            value += link[0]
            main.log.info(self.name + ": \n-----\n%s%s-----\n" % ( switch[1], link[1]) )
            if value != 0:
                return main.FALSE
            else:
                # "PASS"
                return main.TRUE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()
 
    def check_for_no_exceptions(self):
        '''
        TODO: Rewrite
        Used by CassndraCheck.py to scan ONOS logs for Exceptions
        '''
        try:
            self.handle.sendline("dsh 'grep Exception ~/ONOS/onos-logs/onos.*.log'")
            self.handle.expect("\$ dsh")
            self.handle.expect("\$")
            output = self.handle.before
            main.log.info(self.name + ": " + output )
            if re.search("Exception",output):
                return main.FALSE
            else :
                return main.TRUE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()


    def git_pull(self, comp1=""):
        '''
        Assumes that "git pull" works without login
        
        This function will perform a git pull on the ONOS instance.
        If used as git_pull("NODE") it will do git pull + NODE. This is
        for the purpose of pulling from other nodes if necessary.

        Otherwise, this function will perform a git pull in the 
        ONOS repository. If it has any problems, it will return main.ERROR
        If it successfully does a git_pull, it will return a 1.
        If it has no updates, it will return a 0.

        '''
        try:
            main.log.info(self.name + ": Stopping ONOS")
            self.stop()
            self.handle.sendline("cd " + self.home)
            self.handle.expect("ONOS\$")
            if comp1=="":
                self.handle.sendline("git pull")
            else:
                self.handle.sendline("git pull " + comp1)
           
            uptodate = 0
            i=self.handle.expect(['fatal','Username\sfor\s(.*):\s','Unpacking\sobjects',pexpect.TIMEOUT,'Already up-to-date','Aborting'],timeout=1800)
            #debug
           #main.log.report(self.name +": \n"+"git pull response: " + str(self.handle.before) + str(self.handle.after))
            if i==0:
                main.log.error(self.name + ": Git pull had some issue...")
                return main.ERROR
            elif i==1:
                main.log.error(self.name + ": Git Pull Asking for username!!! BADD!")
                return main.ERROR
            elif i==2:
                main.log.info(self.name + ": Git Pull - pulling repository now")
                self.handle.expect("ONOS\$", 120)
                return 0
            elif i==3:
                main.log.error(self.name + ": Git Pull - TIMEOUT")
                return main.ERROR
            elif i==4:
                main.log.info(self.name + ": Git Pull - Already up to date")
                return 1
            elif i==5:
                main.log.info(self.name + ": Git Pull - Aborting... Are there conflicting git files?")
                return main.ERROR
            else:
                main.log.error(self.name + ": Git Pull - Unexpected response, check for pull errors")
                return main.ERROR
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()
#********************************************************           


    def git_compile(self):
        '''
        Compiles ONOS
        First runs mvn clean then mvn compile
        '''
        try:
            main.log.info(self.name + ": mvn clean")
            self.handle.sendline("cd " + self.home)
            self.handle.sendline("mvn clean")
            while 1:
                i=self.handle.expect(['There\sis\sinsufficient\smemory\sfor\sthe\sJava\sRuntime\sEnvironment\sto\scontinue','BUILD\sFAILURE','BUILD\sSUCCESS','ONOS\$',pexpect.TIMEOUT],timeout=30)
                if i == 0:
                    main.log.error(self.name + ":There is insufficient memory for the Java Runtime Environment to continue.")
                    return main.FALSE
                elif i == 1:
                    main.log.error(self.name + ": Clean failure!")
                    return main.FALSE
                elif i == 2:
                    main.log.info(self.name + ": Clean success!")
                elif i == 3:
                    main.log.info(self.name + ": Clean complete")
                    break;
                elif i == 4:
                    main.log.error(self.name + ": mvn clean TIMEOUT!")
                    return main.FALSE
                else:
                    main.log.error(self.name + ": unexpected response from mvn clean")
                    return main.FALSE
        
            main.log.info(self.name + ": mvn compile")
            self.handle.sendline("mvn compile")
            while 1:
                i=self.handle.expect(['There\sis\sinsufficient\smemory\sfor\sthe\sJava\sRuntime\sEnvironment\sto\scontinue','BUILD\sFAILURE','BUILD\sSUCCESS','ONOS\$',pexpect.TIMEOUT],timeout=60)
                if i == 0:
                    main.log.error(self.name + ":There is insufficient memory for the Java Runtime Environment to continue.")
                    return main.FALSE
                if i == 1:
                    main.log.error(self.name + ": Build failure!")
                    return main.FALSE
                elif i == 2:
                    main.log.info(self.name + ": Build success!")
                    return main.TRUE
                elif i == 3:
                    main.log.info(self.name + ": Build complete")
                    return main.TRUE
                elif i == 4:
                    main.log.error(self.name + ": mvn compile TIMEOUT!")
                    return main.FALSE
                else:
                    main.log.error(self.name + ": unexpected response from mvn compile")
                    return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def tcpdump(self, intf = "eth0"):
        '''
        Runs tpdump on an intferface and saves in onos-logs under the ONOS home directory
        intf can be specified, or the default eth0 is used
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("\$")
            self.handle.sendline("sudo tcpdump -n -i "+ intf + " -s0 -w " + self.home +"/onos-logs/tcpdump &")
            i=self.handle.expect(['No\ssuch\device','listening\son',pexpect.TIMEOUT],timeout=10)
            if i == 0:
                main.log.error(self.name + ": tcpdump - No such device exists. tcpdump attempted on: " + intf)
                return main.FALSE
            elif i == 1:
                main.log.info(self.name + ": tcpdump started on " + intf)
                return main.TRUE
            elif i == 2:
                main.log.error(self.name + ": tcpdump command timed out! Check interface name, given interface was: " + intf)
                return main.FALSE
            else:
                main.log.error(self.name + ": tcpdump - unexpected response")
            return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def kill_tcpdump(self):
        '''
        Kills any tcpdump processes running
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("\$")
            self.handle.sendline("sudo kill -9 `ps -ef | grep \"tcpdump -n\" | grep -v grep | awk '{print $2}'`")
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def find_host(self,RestIP,RestPort,RestAPI,hostIP):
        retcode = 0
        retswitch = []
        retport = []
        retmac = []
        foundIP = []
        try:
            ##### device rest API is: 'host:8080/wm/onos/ng/switches/json' ###
            url ="http://%s:%s%s" %(RestIP,RestPort,RestAPI)
            print url

            try:
                command = "curl -s %s" % (url)
                result = os.popen(command).read()
                parsedResult = json.loads(result)
                print parsedResult
            except:
                print "REST IF %s has issue" % command
                parsedResult = ""

            if parsedResult == "":
                return (retcode, "Rest API has an error", retport, retmac)
            else:
                for switch in enumerate(parsedResult):
                    #print switch
                    for port in enumerate(switch[1]['ports']):
                        if ( port[1]['devices'] != [] ):
                            try:
                                foundIP = port[1]['devices'][0]['ipv4addresses'][0]['ipv4']
                            except:
                                print "Error in detecting IP address."
                            if foundIP == hostIP:
                                retswitch.append(switch[1]['dpid'])
                                retport.append(port[1]['desc'])
                                retmac.append(port[1]['devices'][0]['mac'])
                                retcode = retcode +1
                                foundIP =''
            return(retcode, retswitch, retport, retmac)
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

#Perf test related functions

    def addPerfFlows(self, onosdir, numflows):
        main.log.info("ADD_FLOW RUNNING!!!! ")
        startTime=time.time()
        self.execute(cmd=onosdir+"/scripts"+"/add_"+str(numflows)+".py",prompt="\$",timeout=10)
        elapsedTime=time.time()-startTime
        main.log.info("AddFlows script run time: " + str(elapsedTime) + " seconds")
        time.sleep(15)
        return main.TRUE

    def removePerfFlows(self, onosdir, numflows):
        main.log.info("REMOVE_FLOW RUNNING!!!! ")
        startTime=time.time()
        self.execute(cmd=onosdir+"/scripts"+"/remove_"+str(numflows)+".py",prompt="\$",timeout=10)
        elapsedTime=time.time()-startTime
        main.log.info("RemoveFlows script run time: " + str(elapsedTime) + " seconds")
        time.sleep(15)
        return main.TRUE

    def tshark_of(self, capture_type):
        self.handle.sendline("")
        self.handle.expect("\$")
        self.handle.sendline("rm /tmp/wireshark*")
        self.handle.expect("\$")
        #self.execute(cmd='''tshark -i eth0 -t e | grep --color=auto CSM | grep --color=auto -E 'Flow|Barrier' > /tmp/tshark_of_'''+capture_type+''' .txt''',prompt="Capturing",timeout=10)
        self.execute(cmd="tshark -i eth0 -t e | grep OFP > /tmp/tshark_of_"+capture_type+".txt", prompt="Capturing", timeout=10) 
        self.handle.sendline("")
        main.log.info("tshark_of started")
        return main.TRUE

    def start_tshark(self,flowtype, numflows):
        self.handle.sendline("")
        self.handle.expect("\$")
        self.execute(cmd='''rm /tmp/wireshark*''')
        self.handle.sendline("y")
        self.handle.expect("\$")
        self.execute(cmd='''tshark -i eth0 -t e | grep --color=auto CSM | grep --color=auto -E 'Flow|Barrier' > /tmp/tdump_'''+flowtype+"_"+str(numflows)+".txt &",prompt="Capturing",timeout=10)
        self.handle.sendline("")
        self.handle.expect("\$")
        main.log.info("TSHARK STARTED!!!")
        return main.TRUE

    def stop_tshark(self):
        self.handle.sendline("")
        #self.handle.expect("\$")
        self.handle.sendline("sudo kill -9 `ps -ef | grep \"tshark -i\" | grep -v grep | awk '{print $2}'`")
        self.handle.sendline("")
        #self.handle.expect("\$")
        main.log.info("TSHARK STOPPED!!!")
        return main.TRUE

    def dynamicIntent(self, **kwargs):
        import json
        import requests
        args = utilities.parse_args(["NUMFLOWS","INTADDR","OPTION"],**kwargs)
        print args
        url = args['INTADDR']
        option = args['OPTION']
        intents = []
        idx=0
        
        if args['NUMFLOWS'] != None: 
            numflows = int(args['NUMFLOWS'])
        else: 
            numflows = 0       
        
        if(option == "ADD"): 
            for i in range(6,numflows+6):
                oper = {}
                mac3 = idx / 255
                mac4 = idx % 255
                str_mac3 = "%0.2x" % mac3
                str_mac4 = "%0.2x" % mac4
                src_mac = "00:01:"+str_mac3+":"+str_mac4+":00:00"
                dst_mac = "00:02:"+str_mac3+":"+str_mac4+":00:00"
                src_dpid = "00:00:00:00:00:00:30:00"
                dst_dpid = "00:00:00:00:00:00:30:00"
                oper['intentId'] = str(idx) 
                oper['intentType'] = 'SHORTEST_PATH'   # XXX: Hardcoded
                oper['staticPath'] = False            # XXX: Hardcoded
                oper['srcSwitchDpid'] = src_dpid
                oper['srcSwitchPort'] = 1
                oper['dstSwitchDpid'] = dst_dpid
                oper['dstSwitchPort'] = 1
                oper['matchSrcMac'] = str(src_mac)
                oper['matchDstMac'] = str(dst_mac)
                intents.append(oper)
                idx = idx + 1

            parsed_result = []
            data_json = json.dumps(intents)
            request = urllib2.Request(url,data_json)
            request.add_header("Content-Type", "application/json")
            response=urllib2.urlopen(request)
            result = response.read()
            response.close()
            if len(result) != 0:
                parsed_result = json.loads(result)
                return main.TRUE
                
        elif(option == "REM"):
            #passing in just the url should delete all existing high level intents
            intent_del = requests.delete(url)
            return main.TRUE
   
        else:
            return main.FALSE

    def generateFlows(self, flowdef, flowtype, numflows, ip):
        main.log.info("GENERATE FLOWS RUNNING!!!")
        #main.log.info("Test" + flowdef+"/"+flowtype+"_"+str(numflows)+".py")
        f = open(flowdef+"/"+flowtype+"_"+str(numflows)+".py", 'w')
        f.write('''#! /usr/bin/python\n''')
        f.write('import json\n')
        f.write('import requests\n')
        f.write('''url = 'http://127.0.0.1:8080/wm/onos/datagrid/add/intents/json'\n''') 
        f.write('''headers = {'Content-type': 'application/json', 'Accept': 'application/json'}\n''') 
        
        intents = []
        idx = 0
        for i in range(6,(numflows+6)):
	    mac3 = idx / 255
	    mac4 = idx % 255
	    str_mac3 = "%0.2x" % mac3
	    str_mac4 = "%0.2x" % mac4
	    srcMac = '00:01:'+str_mac3+':'+str_mac4+':00:00'
	    dstMac = '00:02:'+str_mac3+':'+str_mac4+':00:00'
	    srcSwitch = '00:00:00:00:00:00:10:00'
	    dstSwitch = '00:00:00:00:00:00:10:00'
	    srcPort = 1
	    dstPort = 2
	
	    intent = {'intent_id': '%d' %(i),'intent_type':'shortest_intent_type','intent_op':flowtype,'srcSwitch':srcSwitch,'srcPort':srcPort,'srcMac':srcMac,'dstSwitch':dstSwitch,'dstPort':dstPort,'dstMac':dstMac}
	    intents.append(intent)
	    idx = idx + 1
        f.write('''s=''')
        f.write(json.dumps(intents, sort_keys = True))
        f.write('''\nr = requests.post(url, data=json.dumps(s), headers = headers)''')
        f.flush()
        #subprocess.Popen(flowdef, stdout=f, stderr=f, shell=True)
        f.close()
        os.system("chmod a+x "+flowdef+"/"+flowtype+"_"+str(numflows)+".py")
        
        return main.TRUE
    
    def getFile(self, numflows, onosIp, testIp, testdirectory, onosdirectory, flowparams):
        import datetime
        time.sleep(15)
        main.log.info("SCP'ing FILES FROM TEST STATION: "+str(testIp)+ " TO ONOS: "+str(onosIp))
        for i in range(0,numflows):
            self.handle.sendline("scp admin@"+testIp+":"+testdirectory+"/add_"+str(flowparams[i])+".py admin@"+onosIp+":"+onosdirectory+"/scripts/" )
            self.handle.sendline("scp admin@"+testIp+":"+testdirectory+"/remove_"+str(flowparams[i])+".py admin@"+onosIp+":"+onosdirectory+"/scripts/" ) 
        time.sleep(15)
        return main.TRUE

    def sendFile(self, **kwargs):
        import datetime
        time.sleep(15)
        args = utilities.parse_args(["TESTIP","ONOSIP","TESTDIR","ONOSDIR","TESTUSER","ONOSUSER","FILENAME"],**kwargs)
        if(args["TESTDIR"][:-1] != "/"):
            args["TESTDIR"] = args["TESTDIR"] + "/"
        if(args["ONOSDIR"][:-1] != "/"):
            args["ONOSDIR"] = args["ONOSDIR"] + "/"
        main.log.info("Using SCP to copy files")
        sendstr = "scp "+args["TESTUSER"]+"@"+args["TESTIP"]+":"+args["TESTDIR"]+args["FILENAME"]+".py "+args["ONOSUSR"]+"@"+args["ONOSIP"]\
                  +":"+args["ONOSDIR"]
        print sendstr
        self.handle.sendline(sendstr) 
        

    def printPerfResults(self, flowtype, numflows, stime, onosip):
        import datetime  
        import os
        import subprocess
        self.handle.sendline("")
        self.handle.expect("\$")
        for (i,j) in zip(numflows,stime):
            startTime=datetime.datetime.fromtimestamp(j)
            #tshark_file=os.popen("/tmp/tdump_"+flowtype+"_"+str(i)+".txt",'r')
            #allFlowmods=tshark_file.read()
            #time.sleep(5)
            #firstFlowmod=allFlowmods[0]
            #lastBarrierReply=allFlowmods[-1]
            self.handle.sendline("")
            self.handle.expect("\$")
            ssh = subprocess.Popen(['ssh', 'admin@'+onosip, 'cat', "/tmp/tdump_"+flowtype+"_"+str(i)+".txt"], stdout=subprocess.PIPE)
            firstline = ""
            lastline = ""
            count = 0
            while True:
                line = ssh.stdout.readline() 
                if count == 0:
                    firstline = line
                    count = 1
                elif line != '':
                    lastline = line
                if not line:
                    break
            print firstline
            print lastline
            firstFlowmod = firstline
            lastBarrierReply = lastline
            #self.handle.sendline("head -1 /tmp/tdump_"+flowtype+"_"+str(i)+".txt")
            #self.handle.expect("\(CSM\)")
            #firstFlowmod=self.handle.before
            #firstFlowmod=self.execute(cmd="head -1 /tmp/tdump_"+flowtype+"_"+str(i)+".txt",prompt="\$",timeout=10)
            #lastBarrierReply=self.execute(cmd="tail -n 1 /tmp/tdump_"+flowtype+"_"+str(i)+".txt",prompt="\$",timeout=10)
            print "first flow: " + firstFlowmod
            print "last barrier: " + lastBarrierReply
            firstFlowmodSplit=firstFlowmod.split()
            firstFlowmodTS=datetime.datetime.fromtimestamp(float(firstFlowmodSplit[0]))
            lastBarrierSplit=lastBarrierReply.split()
            lastBarrierTS=datetime.datetime.fromtimestamp(float(lastBarrierSplit[0]))
            print firstFlowmodTS
            print startTime
            main.log.report("Number of Flows: " + str(i))
            #main.log.info("Add Flow Start Time: " + str(startTime))
            main.log.report("First Flow mod seen after: " + str(float(datetime.timedelta.total_seconds(firstFlowmodTS-startTime)*1000))+"ms")
            main.log.report("Last Barrier Reply seen after: " + str(float(datetime.timedelta.total_seconds(lastBarrierTS-startTime)*1000))+"ms\n")
            main.log.report("Total Flow Setup Delay(from first flowmod): " + str(float(datetime.timedelta.total_seconds(lastBarrierTS-firstFlowmodTS)*1000))+"ms")
            main.log.report("Total Flow Setup Delay(from start): " + str(float(datetime.timedelta.total_seconds(lastBarrierTS-startTime)*1000))+"ms\n")
            main.log.report("Flow Setup Rate (using first flowmod TS): " + str(int(1000/datetime.timedelta.total_seconds(lastBarrierTS-firstFlowmodTS)))+" flows/sec")
            main.log.report("Flow Setup Rate (using start time): " + str(int(1000/datetime.timedelta.total_seconds(lastBarrierTS-startTime)))+" flows/sec")
            print "*****************************************************************"
            #main.log.info("first: " + str(firstFlowmod))
            #main.log.info(firstFlowmodSplit)
            #main.log.info("last: " + str(lastBarrierReply))
            #tshark_file.close()
        return main.TRUE

    def isup(self):
        '''
        A more complete check to see if ONOS is up and running properly.
        First, it checks if the process is up.
        Second, it reads the logs for "Exception: Connection refused"
        Third, it makes sure the logs are actually moving.
        returns TRUE/FALSE accordingly.
        '''
        try:
            self.execute(cmd="\n",prompt="\$",timeout=10)
            self.handle.sendline("cd "+self.home)
            response = self.execute(cmd= "./onos.sh core status ",prompt="running",timeout=10)
            self.execute(cmd="\n",prompt="\$",timeout=10)
            tail1 = self.execute(cmd="tail " + self.home + "/onos-logs/onos.*.log",prompt="\$",timeout=10)
            time.sleep(10)
            self.execute(cmd="\n",prompt="\$",timeout=10)
            tail2 = self.execute(cmd="tail " + self.home + "/onos-logs/onos.*.log",prompt="\$",timeout=10)
            pattern = '(.*)1 instance(.*)'
            patternUp = 'Sending LLDP out'
            pattern2 = '(.*)Exception: Connection refused(.*)'
           # if utilities.assert_matches(expect=pattern,actual=response,onpass="ONOS process is running...",onfail="ONOS process not running..."):
            
            if re.search(pattern, response):
                if re.search(patternUp,tail2):
                    main.log.info(self.name + ": ONOS process is running...")
                    if tail1 == tail2:
                        main.log.error(self.name + ": ONOS is frozen...")#logs aren't moving
                        return main.FALSE
                    elif re.search( pattern2,tail1 ):
                        main.log.info(self.name + ": Connection Refused found in onos log")
                        return main.FALSE
                    elif re.search( pattern2,tail2 ):
                        main.log.info(self.name + ": Connection Refused found in onos log")
                        return main.FALSE
                    else:
                        main.log.info(self.name + ": Onos log is moving! It's looking good!")
                        return main.TRUE
                else:
                    main.log.info(self.name + ": ONOS not yet sending out LLDP messages")
                    return main.FALSE
            else:
                main.log.error(self.name + ": ONOS process not running...")
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()
        

    def add_intent(self, intent_id,src_dpid,dst_dpid,src_mac,dst_mac,intentIP,intentPort=8080,intentURL="wm/onos/intent/high" , intent_type = 'SHORTEST_PATH', static_path=False, src_port=1,dst_port=1):
        from urllib2 import URLError, HTTPError 
        import json
        import requests
        intents = []
        oper = {}
        oper['intentId'] = intent_id
        oper['intentType'] = intent_type    # XXX: Hardcoded
        oper['staticPath'] = static_path              # XXX: Hardcoded
        oper['srcSwitchDpid'] = src_dpid
        oper['srcSwitchPort'] = src_port
        oper['dstSwitchDpid'] = dst_dpid
        oper['dstSwitchPort'] = dst_port
        oper['matchSrcMac'] = src_mac
        oper['matchDstMac'] = dst_mac
        intents.append(oper)
        url = "http://%s:%s/%s"%(intentIP,intentPort,intentURL)
        parsed_result = []
        data_json = json.dumps(intents)
        headers = {'content-type': 'application/json'} 
        
        #r = requests.post(url, data=json.dumps(intents), headers=headers)
        #parsed_result = r
        request = urllib2.Request(url,data_json)
        request.add_header("Content-Type", "application/json")
        response=urllib2.urlopen(request)
        result = response.read()
        response.close()
        if len(result) != 0:
            parsed_result = json.loads(result)
            return main.TRUE
        #except HTTPError as exc:
        #    print "ERROR:"
        #    print "  REST GET URL: %s" % url
        #    error_payload = json.loads(exc.fp.read())
        #    print "  REST Error Code: %s" % (error_payload['code'])
        #    print "  REST Error Summary: %s" % (error_payload['summary'])
        #    print "  REST Error Description: %s" % (error_payload['formattedDescription'])
        #    print "  HTTP Error Code: %s" % exc.code
        #    print "  HTTP Error Reason: %s" % exc.reason
        #except URLError as exc:
        #    print "ERROR:"
        #    print "  REST GET URL: %s" % url
        #    print "  URL Error Reason: %s" % exc.reason
        return main.FALSE
        
    def get_single_intent_latency(self, json_obj):
        begin_time = json_obj['gauges'][0]['gauge']['value']
        end_time = json_obj['gauges'][1]['gauge']['value']
        intent_lat_ms = int(end_time) - int(begin_time)
        return intent_lat_ms                                      
 
# purpose of comp_intents is to find if the high level intents have changed. preIntents
# and postIntents should be the output of curl of the intents. preIntents being the original
# and postIntents being the later. We are looking at the intents with the same id from both
# and comparing the dst and src DPIDs and macs, and the state. If any of these are changed
# we print that there are changes, then return a list of the intents that have changes`
#**********************************************************************************************
#**********************************************************************************************
    def comp_intents(self,preIntents,postIntents):
        import json
        preDecoded = json.loads(preIntents)
        postDecoded = json.loads(postIntents)
        print preDecoded
        print postDecoded
        changes = []
        if not preDecoded:
            if postDecoded:
                print "THERE ARE CHANGES TO THE HIGH LEVEL INTENTS!!!!"
                return postDecoded
        for k in preDecoded:
            for l in postDecoded:
                if l['id']==k['id']:
                    if k['dstSwitchDpid']==l['dstSwitchDpid'] and k['srcMac']==l['srcMac'] and k['dstMac']==l['dstMac'] and k['srcSwitchDpid']==l['srcSwitchDpid'] and k['state']==l['state']:
                        postDecoded.remove(l)
                    else:
                        changes.append(k)
                        print ("THERE ARE CHANGES TO THE HIGH LEVEL INTENTS!!!")
        return changes
    
#**********************************************************************************************
#**********************************************************************************************
# the purpose of comp_low is to find if the low level intents have changed. The main idea
# is to determine if the path has changed. Again, like with the comp_intents function, the
# pre and post Intents variables are the json dumps of wm/onos/intent/low. The variables
# that will be compared are the state, and the path.
#**********************************************************************************************
#**********************************************************************************************
    def comp_low(self, preIntents,postIntents):
        import json
        preDecoded = json.loads(preIntents)
        postDecoded = json.loads(postIntents)
        changes = []
        if not preDecoded:
            if postDecoded:
                print "THERE ARE CHANGES TO THE LOW LEVEL INTENTS!!!"
                return postDecoded
        for k in preDecoded:
            for l in postDecoded:
                if l['id']==k['id']:
                    if l['path']!=k['path']:
                        changes.append(l)
                        print "\n\n\n\nTHERE ARE CHANGES TO THE LOW LEVEL INTENTS!!!"
                    else:
                        if k['state']!=l['state']:
                            changes.append(l)
                            print "\n\n\n\nTHERE ARE CHANGES TO THE LOW LEVEL INTENTS!!!"
                        else:
                            print "NO CHANGES SO FAR\n\n\n"
        return changes
