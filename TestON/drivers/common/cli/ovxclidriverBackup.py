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


OVXCliDriver is the basic driver which will handle the OVX functions
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

from drivers.common.clidriver import CLI

class OVXCliDriver(CLI):
    '''
        OVXCliDriver is the basic driver which will handle all the OVX functions
    '''
    def __init__(self):
        super(CLI, self).__init__()
        
    def connect(self,**connectargs):
        for key in connectargs:
            vars(self)[key] = connectargs[key]
        
        self.name = self.options['name']

        self.handle = super(OVXCliDriver,self).connect(user_name = self.user_name, ip_address = self.ip_address,port = self.port, pwd = self.pwd)
        if self.handle :
            main.log.info("Connected "+self.name)
            self.execute(cmd='cd /home/ovx/OpenVirteX', prompt="OpenVirteX\$", timeout=3)
            self.execute(cmd='cd pgm', prompt="pgm\$", timeout=5)
            self.execute(cmd='killall java', prompt="pgm\$", timeout=15)
	    self.execute(cmd='bash ovx.sh> ovxDisplay.log 2>&1 &', prompt='pgm\$', timeout=30 )
            return self.handle
        else :
            return main.FALSE
     
    def isup(self):
        main.log.info("Checking if ovx is started")  
	self.handle.sendline("sleep 10")
	self.expect("pgm\$", 12)
	response = self.execute(cmd='cat ovxDisplay.log', prompt='pgm\$', timeout=30)
	#print "response=", response
	print "***********************"
	if "ServerConnector - Started ServerConnector" in response:
    	    return main.TRUE
        else:
            return main.FALSE

    def NetworkCreate(self, **kwargs):
        main.log.info ("Checking createNetwork API")
        #self.execute(cmd='cd /home/ovx/OpenVirteX/utils/', prompt="utils\$", timeout=5)
	self.handle.sendline("cd /home/ovx/OpenVirteX/utils/")
	self.handle.expect("utils\$")
	self.handle.sendline("pwd")
	self.handle.expect("\$")
	print "pwd=", self.handle.before
        args = utilities.parse_args(["PROTOCOL","IP","PORT","IPRANGE","MASK"],**kwargs)    
	protocol = str(args["PROTOCOL"]) if args["PROTOCOL"] != None else ""
	ip = str(args["IP"]) if args["IP"] != None else ""
	port = str(args["PORT"]) if args["PORT"] != None else ""
	iprange = str(args["IPRANGE"]) if args["IPRANGE"] != None else ""
	mask = str(args["MASK"]) if args["MASK"] != None else ""
	command = "./ovxctl.py -n createNetwork" + " " + protocol + ":" + ip + ":" + port + " " + iprange + " " + mask   
	print "command = ", command
	response = self.execute(cmd=command, prompt="utils\$", timeout=30)
	print "response = ", response
	print "***********************"
	if "Virtual network has been created (network_id" in response:
		#command = './ovxctl.py -n listVirtualNetworks'
		#networkIDList = self.execute(cmd=command, prompt="ovx@ovx:~/OpenVirteX/utils\$", timeout=30)
		#print "networkIDList = ", networkIDList
		#networkID = networkIDList[0] #listVirtualNetworks API call returns a list
		#print "networkID = ", networkID
		return main.TRUE
	else:
		return main.FALSE
	
    def SwitchCreate(self, **swargs):
	main.log.info ("Checking createSwitch API")	
        args = utilities.parse_args(["DPID", "NWID"], **swargs)
	print "DPID =",args["DPID"]
	print "NWID =", args["NWID"]
	nw_id = str(args["NWID"]) if args["NWID"] != None else ""
	dpid = str(args["DPID"]) if args["DPID"] != None else ""
	command = './ovxctl.py -n createSwitch' + " " + nw_id + " " + dpid
        print "command = ", command
        response = self.execute(cmd=command, prompt="utils\$", timeout=30)
        print "response = ", response
        print "***********************"
	if "Virtual switch has been created" in response:
		return main.TRUE
	else:
		return main.FALSE

    def PortCreate(self, **pargs):
        main.log.info ("Checking createPort API")
        args = utilities.parse_args(["NWID", "DPID", "PORTNO"], **pargs)
        print "DPID =",args["DPID"]
        print "NWID =", args["NWID"]
	print "PORT_NUM =", args["PORTNO"]
        nw_id = str(args["NWID"]) if args["NWID"] != None else ""
        dpid = str(args["DPID"]) if args["DPID"] != None else ""
	port_num = str(args["PORTNO"]) if args["PORTNO"] != None else ""
        command = './ovxctl.py -n createPort' + " " + nw_id + " " + dpid + " " + port_num
        print "command = ", command
        response = self.execute(cmd=command, prompt="utils\$", timeout=30)
        print "response = ", response
        print "***********************"
        if "Virtual port has been created" in response:
                return main.TRUE
        else:
                return main.FALSE
