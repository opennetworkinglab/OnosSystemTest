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


ZookeeperCliDriver is the basic driver which will handle the Zookeeper functions
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

sys.path.append("../")
from drivers.common.clidriver import CLI

class ZookeeperCliDriver(CLI):
    '''
    ZookeeperCliDriver is the basic driver which will handle the Zookeeper's functions
    '''
    def __init__(self):
        super(CLI, self).__init__()
        self.handle = self
        self.wrapped = sys.modules[__name__]

    def kill(self):
        import re
        try: 
            self.handle.sendline("ps -ef |grep 'zookeeper.log.dir' |awk 'NR==1 {print $2}' |xargs sudo kill -9")
            self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
            self.handle.sendline("ps -ef |grep 'zookeeper.log.dir' |wc -l")
            self.handle.expect(["wc -l",pexpect.EOF,pexpect.TIMEOUT])
            response = self.handle.after
            if re.search("1",response):
                return "Zookeeper Killed!"
            else:
                return "ERROR!!! ZOOKEEPER MAY NOT HAVE BEEN KILLED PROPERLY!!!"
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.hane + ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()



    def connect(self, **connectargs):
        # Here the main is the TestON instance after creating all the log handles.
        self.port = None
        for key in connectargs:
            vars(self)[key] = connectargs[key]       
        self.home = "~/ONOS"
        self.zkhome = "~/zookeeper-3.4.6"
        self.clustername = "sanity-rc-onos"
        #self.home = "~/zookeeper-3.4.5"
        for key in self.options:
            if key == "home":
                self.home = self.options['home']
                break
        
        self.name = self.options['name']
        self.handle = super(ZookeeperCliDriver, self).connect(user_name = self.user_name, ip_address = self.ip_address,port = self.port, pwd = self.pwd, home = self.home)
        
        self.ssh_handle = self.handle
        if self.handle :
            return main.TRUE
        else :
            main.log.error("Connection failed to the host "+self.user_name+"@"+self.ip_address) 
            main.log.error(self.name + ": Failed to connect to Zookeeper")
            return main.FALSE
   
 
    def start(self):
        '''
        This Function will start the Zookeeper
        '''
        main.log.info(self.name + ": Starting Zookeeper" )
        self.handle.sendline("")
        self.handle.expect("\$")
        self.handle.sendline("cd "+self.home)
        self.handle.sendline("./onos.sh zk start")
        self.handle.expect("zk start") 
        self.handle.expect("\$")
        response = self.handle.before + self.handle.after 
        if re.search("STARTED", response):
            main.log.info(self.name + ": Zookeeper Started ")
            return main.TRUE
        elif re.search("running", response):
            main.log.warn(self.name +": zookeeper ... already running")
            return main.TRUE
        else:
            main.log.error(self.name + ": Failed to start Zookeeper"+ response)
            return main.FALSE
        
    def status(self):
        '''
        This Function will return the Status of the Zookeeper 
        '''
        self.execute(cmd="\n",prompt="\$",timeout=10)
        self.handle.sendline("cd "+self.home)
        response = self.execute(cmd="./onos.sh zk status ",prompt="JMX",timeout=10)
        response=self.handle.after
        self.execute(cmd="\n",prompt="\$",timeout=10)
        return self.handle.before + self.handle.after
        
    def stop(self):
        '''
        This Function will stop the Zookeeper if it is Running
        ''' 
        self.execute(cmd="\n",prompt="\$",timeout=10)
        time.sleep(1)
        self.handle.sendline("cd "+self.home)
        response = self.execute(cmd="./onos.sh zk stop ",prompt="$",timeout=10)
        if re.search("stopping",response):
            main.log.info(self.name + ": Zookeeper Stopped")
            return main.TRUE
        else:
            main.log.warn(self.name + ": No zookeeper to stop")
            return main.FALSE
            
    def disconnect(self):
        ''' 
        Called at the end of the test to disconnect the ZK handle 
        ''' 
        response = ''
        if self.handle:
            self.handle.sendline("exit")
            self.handle.expect("closed")
        else :
            main.log.error(self.name + ": Connection failed to the host")
            response = main.FALSE
        return response 
   
#**********************************************************************************************
#**********************************************************************************************
# findMaster is used to determine the master controller of a switch. 
# it uses the switchList which is a json dict, and finds the first controller of 
# each switch
#**********************************************************************************************
#**********************************************************************************************


    def findMaster(self, switchDPID, switchList):
        import json
        decoded = json.loads(switchList)
        if switchList=="":
            return "NO CONTROLLERS FOUND"
        for k in decoded.iteritems():
            k2 = json.dumps(k)
            if re.search(switchDPID,k2):
                k3 = k2.split(',')
                k4 = k3[1].split()
                k5 = k4[1].split('"')
                return k5[1]
        return "NO CONTROLLERS FOUND"

    def isup(self):
        '''
        Calls the zookeeper status and returns TRUE if it has an assigned Mode to it. 
        '''
        self.execute(cmd="\n",prompt="\$",timeout=10)
        response = self.execute(cmd=self.home + "/onos.sh zk status ",prompt="Mode",timeout=10)
        pattern = '(.*)Mode(.*)'
        if re.search(pattern, response): 
	    main.log.info(self.name + ": Zookeeper is up.") 
            return main.TRUE
        else:
	    main.log.info(self.name + ": Zookeeper is down.") 
            return main.FALSE


