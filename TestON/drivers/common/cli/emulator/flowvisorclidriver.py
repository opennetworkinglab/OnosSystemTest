#!/usr/bin/env python
'''
Created on 26-Mar-2013

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
import core.teston
sys.path.append("../")
from drivers.common.cli.emulatordriver import Emulator
from drivers.common.clidriver import CLI

class FlowVisorCliDriver(Emulator):
    '''
        FlowVisorCliDriver is the basic driver which will handle the Mininet functions
    '''
    def __init__(self):
        super(Emulator, self).__init__()
        self.handle = self
        self.wrapped = sys.modules[__name__]

    def connect(self, **connectargs):
        #,user_name, ip_address, pwd,options):
        # Here the main is the TestON instance after creating all the log handles.
        for key in connectargs:
            vars(self)[key] = connectargs[key]
        self.home = "~/flowvisor"
        for key in self.options:
            if key == "home":
	        self.home = self.options['home']
	        break

        self.name = self.options['name']
        self.handle = super(FlowVisorCliDriver, self).connect(user_name = self.user_name, ip_address = self.ip_address,port = None, pwd = self.pwd)
        self.ssh_handle = self.handle
        
        # Copying the readme file to process the 
        if self.handle :
            self.execute(cmd='\n',prompt='\$',timeout=10)
            self.options['path'] = self.home + '/scripts/'
            #self.handle.logfile = sys.stdout
            self.execute(cmd='cd '+self.options['path'],prompt='\$',timeout=10)
            main.log.info("Starting FlowVisor ")
	    self.handle.sendline("")
            self.handle.expect("\$")
            
            response = self.execute(cmd='sudo -u flowvisor flowvisor &',prompt='Starting FlowVisor',timeout=100)
	    self.handle.sendline("")
            self.handle.expect("\$")
           
            pattern = '\d+'
            
            process_id_search = re.search("\[\d+\]\s+(\d+)", response)
            self.fvprocess_id = "None"
            if process_id_search:
                self.fvprocess_id = process_id_search.group(1)
            
            utilities.assert_matches(expect=pattern,actual=response,onpass="FlowVisor Started Successfully : Proceess Id :"+self.fvprocess_id,onfail="Failed to start FlowVisor")
            return main.TRUE
        else :
            main.log.error("Connection failed to the host "+self.user_name+"@"+self.ip_address) 
            main.log.error("Failed to connect to the FlowVisor")
            return main.FALSE

    def removeFlowSpace(self,id):
        if id == "all":
            flow_space = self.listFlowSpace()
            flow_ids = re.findall("\,id=\[(\d+)\]", flow_space)
            for id in flow_ids :
                self.removeFlowSpace(id)
        else :
	    self.handle.sendline("")
            self.handle.expect("\$")
            self.execute(cmd="fvctl -n remove-flowspace "+id,prompt="fvctl",timeout=10)
	    self.handle.sendline("")
            self.handle.expect("\$")
            main.log.info("Removed flowSpace which is having id :"+id)
        return main.TRUE
            
    def removeSlice(self,name):
        if name == "all":
	    pass
        else:
	    self.handle.sendline("")
            self.handle.expect("\$")
            self.execute(cmd="fvctl -n remove-slice "+name,prompt="fvctl",timeout=10)
	    self.handle.sendline("")
            response = self.handle.expect("\$")
	    if re.search("has been deleted",response):
        	main.log.info("Removed slice named :"+name)
        	return main.TRUE
	    else:
		main.log.error("Failed to remove slice " + name)
		return main.FALSE
        
    def addFlowSpace(self,flowspace_args):
	print flowspace_args
	self.handle.sendline("")
        self.handle.expect("\$")
        self.execute(cmd="fvctl -n add-flowspace "+flowspace_args,prompt="fvctl",timeout=10)
        self.execute(cmd="\n",prompt="\$",timeout=10)
        sucess_match = re.search("\swas\sadded\swith\srequest\sid\s(\d+)", main.last_response)
	self.handle.sendline("")
        self.handle.expect("\$")
        if sucess_match :
            main.log.info("Added flow Space and id is "+sucess_match.group(1))
            return main.TRUE
        else :
            return main.FALSE
        
    
    
    def listFlowSpace(self):
	self.handle.sendline("")
        self.handle.expect("\$")
        self.execute(cmd="fvctl -n list-flowspace ",prompt="fvctl",timeout=10)
        self.execute(cmd="\n",prompt="\$",timeout=10)
        flow_space = main.last_response
        flow_space = self.remove_contol_chars( flow_space)
        flow_space = re.sub("rule\s(\d+)\:", "\nrule "+r'\1'+":",flow_space)
        main.log.info(flow_space)
        
        return flow_space
        
    def listDevices(self):
	self.handle.sendline("")
        self.handle.expect("\$")
        self.execute(cmd="fvctl -n list-datapath-info ",prompt="fvctl",timeout=10)
        #self.execute(cmd="\n",prompt="\$",timeout=10)
        devices_list = ''
        last_response = re.findall("(Device\s\d+\:\s((\d|[a-z])(\d|[a-z])\:)+(\d|[a-z])(\d|[a-z]))", main.last_response)
        
        for resp in last_response :
            devices_match = re.search("(Device\s\d+\:\s((\d|[a-z])(\d|[a-z])\:)+(\d|[a-z])(\d|[a-z]))", str(resp))
            if devices_match:
                devices_list = devices_list+devices_match.group(0)+"\n"
       # devices_list = "Device 0: 00:00:00:00:00:00:00:02 \n Device 1: 00:00:00:00:00:00:00:03"
        main.log.info("List of Devices \n"+devices_list)
        
        return main.TRUE
 
    def listSlices(self, name = ''):
	self.handle.sendline("")
        self.handle.expect("\$")
        self.execute(cmd="fvctl -n list-slices ",prompt="Configured slices:",timeout=10)
        slices = self.execute(cmd="\n",prompt="\$",timeddout=10)
	if name == '':
	    main.log.info("Slices: " + str(slices))
	self.handle.sendline("")
        self.handle.expect("\$")
        if name != '':
	    if re.search(name, slices):
		main.log.info("Slice " + name + " found.")
		return main.TRUE
	    else:
		main.log.warn("Slice " + name + " not found.")
		return main.FALSE
	else:
            return main.FALSE
        

    def addSlice(self, **slice_args):
        args = {}
        args['slice_name'] = ""
        args['controller_url'] = ""
        args['admin_email'] = ""
        args['password'] = ""
        for key in slice_args:
		args[key] = slice_args[key]

        if args['slice_name'] == "" or args['controller_url'] == "" or args['admin_email'] == "":
	    main.log.error("incorrect function arguments")
	    return main.FALSE
	else:
	    self.handle.sendline("")
            self.handle.expect("\$")
	    self.execute(cmd="fvctl -n add-slice "+args['slice_name']+" "+args['controller_url']+" "+args['admin_email']+" --password="+args['password'], prompt="was\ssuccessfully\screated",timeout=10)
	    self.execute(cmd="\n",prompt="\$",timeout=10)
	    main.log.info("Added slice "+args['slice_name'])
	    return main.TRUE
	    if pexpect.ExceptionPexpect:
		main.log.error(str(get_trace))
		return main.FALSE
    
 
    def disconnect(self):
        
        response = ''
        main.log.info("Stopping the FlowVisor")
        if self.handle:
            self.handle.sendline("kill -9 "+str(self.fvprocess_id))
        else :
            main.log.error("Connection failed to the host")
            response = main.FALSE
        return response 
