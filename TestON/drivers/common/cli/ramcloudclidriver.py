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


RamCloudCliDriver is the basic driver which will handle the RamCloud server functions
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

class RamCloudCliDriver(CLI):
    '''
RamCloudCliDriver is the basic driver which will handle the RamCloud server functions
    '''
    def __init__(self):
        super(CLI, self).__init__()
        self.handle = self
        self.wrapped = sys.modules[__name__]

    def connect(self, **connectargs):
        # Here the main is the TestON instance after creating all the log handles.
        self.port = None
        for key in connectargs:
            vars(self)[key] = connectargs[key]       
        
        self.name = self.options['name']
        self.handle = super(RamCloudCliDriver, self).connect(user_name = self.user_name, ip_address = self.ip_address,port = self.port, pwd = self.pwd)
        
        self.ssh_handle = self.handle
        if self.handle :
            #self.start()
            return main.TRUE
        else :
            main.log.error("Connection failed to the host "+self.user_name+"@"+self.ip_address) 
            main.log.error("Failed to connect to the Onos system")
            return main.FALSE
   
 
    def start_serv(self):
        '''
        This Function will start RamCloud Servers
        '''
        main.log.info( "Starting RAMCloud Server" )
        self.handle.sendline("")
        self.handle.expect("\$")
        self.handle.sendline("~/ONOS/start-ramcloud-server.sh start")
        self.handle.expect("start-ramcloud-server.sh start")
        self.handle.expect("\$")
        response = self.handle.before + self.handle.after
        time.sleep(5)
        if re.search("Starting\sramcloud(.*)", response):
            main.log.info("RAMCloud Server Started ")
            return main.TRUE
        else:
            main.log.error("Failed to start RAMCloud Server"+ response)
            return main.FALSE
    def git_pull(self):
        '''
	This function will perform a git pull for RAMCloud
	'''       
        main.log.info("Stopping RAMCloud")
        self.stop_coor()
        self.handle.sendline("cd ~/ramcloud")
        self.handle.expect("ramcloud\$")
        self.handle.sendline("git pull")
        uptodate = 0
        i=self.handle.expect(['fatal','Username\sfor\s(.*):\s','Unpacking\sobjects',pexpect.TIMEOUT,'Already up-to-date','Aborting'],timeout=180)
        if i==0:
            main.log.error("Git pull had some issue...")
            return main.FALSE
        elif i==1:
            main.log.error("Asking for username!!! BAD!!")
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





 
    def start_coor(self):
        '''
        This Function will start RamCloud
        '''
        main.log.info( "Starting RAMCloud Coordinator" )
        self.handle.sendline("")
        self.handle.expect("\$")
        self.handle.sendline("~/ONOS/start-ramcloud-coordinator.sh start")
        self.handle.expect("start-ramcloud-coordinator.sh start")
        self.handle.expect("\$")
        response = self.handle.before + self.handle.after
        time.sleep(5)
        if re.search("Starting\sramcloud\scoordinator(.*)", response):
            main.log.info("RAMCloud Coordinator Started ")
            return main.TRUE
        else:
            main.log.error("Failed to start RAMCloud Coordinator"+ response)
            return main.FALSE

    def status_serv(self):
        '''
        This Function will return the Status of the RAMCloud
        '''
        time.sleep(5)
        self.execute(cmd="\r",prompt="\$",timeout=10)
        response = self.execute(cmd="~/ONOS/start-ramcloud-server.sh status ",prompt="\d+\sramcloud\sserver\srunning(.*)",timeout=10)
        

        self.execute(cmd="\r",prompt="\$",timeout=10)
        return response
        
        if re.search("0\sramcloud\sserver\srunning(.*)") :
            main.log.info("RAMCloud not running")
            return main.TRUE
        elif re.search("1\sramcloud\sserver\srunning(.*)"):
            main.log.warn("RAMCloud Running")
            return main.TRUE
            
    def status_coor(self):
        '''
        This Function will return the Status of the RAMCloud
        '''
        time.sleep(5)
        self.execute(cmd="\r",prompt="\$",timeout=10)
        response = self.execute(cmd="~/ONOS/start-ramcloud-coordinator.sh status ",prompt="\d+\sramcloud\scoordinator\sis\srunning(.*)",timeout=10)
        

        self.execute(cmd="\r",prompt="\$",timeout=10)
        return response
        
        if re.search("0\sramcloud\scoordinator\sis\srunning(.*)") :
            main.log.info("RAMCloud Coordinator not running")
            return main.TRUE
        elif re.search("1\sramcloud\scoordinator\sis\srunning(.*)"):
            main.log.warn("RAMCloud Coordinator Running")
            return main.TRUE

    def stop_serv(self):
        '''
        This Function will stop the RAMCloud if it is Running
        ''' 
        self.execute(cmd="\r",prompt="\$",timeout=10)
        time.sleep(5)
        response = self.execute(cmd="~/ONOS/start-ramcloud-server.sh stop ",prompt="Killed\sexisting\sprosess(.*)",timeout=10)
        self.execute(cmd="\r",prompt="\$",timeout=10)
        if re.search("Killed\sexisting\sprosess(.*)",response):
            main.log.info("RAMCloud Server Stopped")
            return main.TRUE
        else:
            main.log.warn("RAMCloud is not Running")
            return main.FALSE
           

    def stop_coor(self):
        '''
        This Function will stop the RAMCloud if it is Running
        ''' 
        self.execute(cmd="\r",prompt="\$",timeout=10)
        time.sleep(5)
        response = self.execute(cmd="~/ONOS/start-ramcloud-coordinator.sh stop ",prompt="Killed\sexisting\sprosess(.*)",timeout=10)
        self.execute(cmd="\r",prompt="\$",timeout=10)
        if re.search("Killed\sexisting\sprosess(.*)",response):
            main.log.info("RAMCloud Coordinator Stopped")
            return main.TRUE
        else:
            main.log.warn("RAMCloud is not Running")
 
    def disconnect(self):
        ''' 
        Called at the end of the test to disconnect the ssh handle. 
        ''' 
        response = ''
        if self.handle:
            self.handle.sendline("exit")
            self.handle.expect("closed")
        else :
            main.log.error("Connection failed to the host")
            response = main.FALSE
        return response 

    def isup(self):
        '''
        A more complete status check of ramcloud.
        Tries 5 times to call start-ramcloud-server.sh status
        returns TRUE if it sees four occurances of both Up, and Normal 
        '''
        tries = 5
        main.log.info("trying %i times" % tries )
        for i in range(tries):
            self.execute(cmd="\r",prompt="\$",timeout=10)
            self.handle.sendline("")
            self.handle.expect("\$") 
            self.handle.sendline("~/ONOS/start-ramcloud-server.sh status")
            self.handle.expect("sh status") 
            self.handle.expect("\$") 
            result = self.handle.before + self.handle.after 
            pattern = '(.*)Up(.*)Normal(.*)\n(.*)Up(.*)Normal(.*)\n(.*)Up(.*)Normal(.*)\n(.*)Up(.*)Normal(.*)'
            if re.search(pattern, result): 
                return main.TRUE
        return main.FALSE
