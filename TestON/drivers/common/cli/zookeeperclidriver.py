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

    def connect(self, **connectargs):
        # Here the main is the TestON instance after creating all the log handles.
        self.port = None
        for key in connectargs:
            vars(self)[key] = connectargs[key]       
        
        self.name = self.options['name']
        self.handle = super(ZookeeperCliDriver, self).connect(user_name = self.user_name, ip_address = self.ip_address,port = self.port, pwd = self.pwd)
        
        self.ssh_handle = self.handle
        if self.handle :
            self.start()
            return main.TRUE
        else :
            main.log.error("Connection failed to the host "+self.user_name+"@"+self.ip_address) 
            main.log.error("Failed to connect to the Onos system")
            return main.FALSE
   
 
    def start(self):
        ''' This Function will start the Zookeeper'''
        main.log.info( "Starting Zookeeper" )
        self.handle.sendline("")
        self.handle.expect("\$")
        self.handle.sendline("~/zookeeper-3.4.5/bin/zkServer.sh start")
        self.handle.expect("zkServer.sh start") 
        self.handle.expect("\$")
        response = self.handle.before + self.handle.after 
        if re.search("STARTED", response):
            main.log.info("Zookeeper Started ")
            return main.TRUE
        elif re.search("running", response):
            main.log.warn("zookeeper ... already running")
        else:
            main.log.error("Failed to start Zookeeper"+ response)
            return main.FALSE
        
    def status(self):
        '''This Function will return the Status of the Zookeeper '''
        time.sleep(5)
        self.execute(cmd="\r",prompt="\$",timeout=10)
        response = self.execute(cmd="~/zookeeper-3.4.5/bin/zkServer.sh status ",prompt="JMX",timeout=10)
        
        self.execute(cmd="\r",prompt="\$",timeout=10)
        return response
        
    def stop(self):
        '''This Function will stop the Zookeeper if it is Running''' 
        self.execute(cmd="\r",prompt="\$",timeout=10)
        time.sleep(5)
        response = self.execute(cmd="~/zookeeper-3.4.5/bin/zkServer.sh stop ",prompt="STOPPED",timeout=10)
        self.execute(cmd="\r",prompt="\$",timeout=10)
        if re.search("STOPPED",response):
            main.log.info("Zookeeper Stopped")
            return main.TRUE
        else:
            main.log.warn("No zookeeper to stop")
            return main.FALSE
            
    def disconnect(self):
        
        response = ''
        if self.handle:
            self.handle.sendline("exit")
            self.handle.expect("closed")
        else :
            main.log.error("Connection failed to the host")
            response = main.FALSE
        return response 

    def isup(self):
        self.execute(cmd="\n",prompt="\$",timeout=10)
        response = self.execute(cmd="~/zookeeper-3.4.5/bin/zkServer.sh status ",prompt="Mode",timeout=10)
        pattern = '(.*)Mode(.*)'
        if re.search(pattern, response):  
            return main.TRUE
        else:
            return main.FALSE


