#!/usr/bin/env python
'''
Created on 12-Feb-2013

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


FlowVisorCliDriver is the basic driver which will handle the Mininet functions
'''

import pexpect
import struct
import fcntl
import os
import signal
import re
import sys
import time

sys.path.append("../")

from drivers.common.cli.remotetestbeddriver import RemoteTestBedDriver

class FlowVisorCliDriver(RemoteTestBedDriver):
    '''
        FlowVisorCliDriver is the basic driver which will handle the Mininet functions
    '''
    def __init__(self):
        super(RemoteTestBedDriver, self).__init__()
        
    def connect(self,**connectargs):
        for key in connectargs:
            vars(self)[key] = connectargs[key]
        
        self.name = self.options['name']

        self.handle = super(FlowVisorCliDriver,self).connect(user_name = self.user_name, ip_address = self.ip_address,port = self.port, pwd = self.pwd)
        if self.handle :
            main.log.info(self.name+" connected successfully")
            return self.handle
        else :
            main.log.error("Failed to connect "+self.name)
            return main.FALSE
    
    def removeFlowSpace(self,id):
        if id == "all":
            flow_space = self.listFlowSpace()
            flow_ids = re.findall("\,id=\[(\d+)\]", flow_space)
            for id in flow_ids :
                self.removeFlowSpace(id)
        else :
            self.execute(cmd="clear",prompt="\$",timeout=10)
            self.execute(cmd="fvctl removeFlowSpace "+id,prompt="passwd:",timeout=10)
            self.execute(cmd="\r",prompt="\$",timeout=10)
            main.log.info("Removed flowSpace which is having id :"+id)
            
        return main.TRUE
        
    def addFlowSpace(self,flow_space):
        self.execute(cmd="clear",prompt="\$",timeout=10)
        self.execute(cmd="fvctl addFlowSpace "+flow_space,prompt="passwd:",timeout=10)
        self.execute(cmd="\r",prompt="\$",timeout=10)
        sucess_match = re.search("success\:\s+(\d+)", main.last_response)
        if sucess_match :
            main.log.info("Added flow Space and id is "+sucess_match.group(1))
            return main.TRUE
        else :
            return main.FALSE
    
    def listFlowSpace(self):
        self.execute(cmd="clear",prompt="\$",timeout=10)
        self.execute(cmd="fvctl listFlowSpace ",prompt="passwd:",timeout=10)
        self.execute(cmd="\r",prompt="\$",timeout=10)
        flow_space = main.last_response
        flow_space = self.remove_contol_chars( flow_space)
        flow_space = re.sub("rule\s(\d+)\:", "\nrule "+r'\1'+":",flow_space)
        #main.log.info(flow_space)
        
        return main.TRUE
        
    def listDevices(self):
        self.execute(cmd="clear",prompt="\$",timeout=10)
        self.execute(cmd="fvctl listDevices ",prompt="passwd:",timeout=10)
        self.execute(cmd="\r",prompt="\$",timeout=10)
        devices_list = ''
        last_response = re.findall("(Device\s\d+\:\s((\d|[a-z])(\d|[a-z])\:)+(\d|[a-z])(\d|[a-z]))", main.last_response)
        
        for resp in last_response :
            devices_match = re.search("(Device\s\d+\:\s((\d|[a-z])(\d|[a-z])\:)+(\d|[a-z])(\d|[a-z]))", str(resp))
            if devices_match:
                devices_list = devices_list+devices_match.group(0)+"\n"
        main.log.info("List of Devices \n"+devices_list)  
        return main.TRUE
    
    
    
