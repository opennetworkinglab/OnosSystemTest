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


FloodLightCliDriver is the basic driver which will handle the Mininet functions
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

class FloodLightCliDriver(CLI):
    '''
        FloodLightCliDriver is the basic driver which will handle the Mininet functions
    '''
    def __init__(self):
        super(CLI, self).__init__()
        
    def connect(self,**connectargs):
        for key in connectargs:
            vars(self)[key] = connectargs[key]
        
        self.name = self.options['name']

        self.handle = super(FloodLightCliDriver,self).connect(user_name = self.user_name, ip_address = self.ip_address,port = self.port, pwd = self.pwd)
        if self.handle :
            main.log.info("Connected "+self.name)
            self.execute(cmd="\r",prompt="\$",timeout=10)
            self.execute(cmd='cd /home/user_one/floodlight/', prompt="floodlight\$", timeout=3)
            self.execute(cmd='killall java', prompt="floodlight\$", timeout=5)
	    self.execute(cmd='java -jar target/floodlight.jar > display.log 2>&1 &', prompt='floodlight\$', timeout=45 )
            return self.handle
        else :
            return main.FALSE
     
    def isup(self):
        main.log.info("Checking if floodlight controller is started")  
        #response = self.execute(cmd="cat display.log", prompt='\$', timeout = 30)
        #response = self.execute(cmd='Listening for switch connections on 0.0.0.0/0.0.0.0:6633', prompt='floodlight\$', timeout=15)
	#if re.search("\sListening\sfor\sswitch\sconnections\son\s\w\.\w\.\w\.\w/\w\.\w\.\w\.\w:6633", response): 
	#self.handle.sendline("grep -c \"Listening for switch connections on\" display.log")
	#self.handle.expect('\$')
	response = self.execute(cmd='cat display.log', prompt='floodlight\$', timeout=15)
	#print 'response=', response
	if "Listening for switch connections on" in response:
    	    return main.TRUE
        else:
            return main.FALSE
        
