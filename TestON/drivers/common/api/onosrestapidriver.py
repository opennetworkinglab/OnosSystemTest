#!/usr/bin/env python
'''
Created on 4-Jun-2013

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


onosrestapidriver is the basic driver which will handle the onorestapi functions
'''

import struct
import fcntl
import os
import signal
import re
import sys
import time 

sys.path.append("../")
from drivers.common.apidriver import API
import urllib
import __builtin__


class OnosRestApiDriver(API):

    def __init__(self):
        super(API, self).__init__()
                                                

    def connect(self,**connectargs):
        for key in connectargs:
            vars(self)[key] = connectargs[key]
        
        self.name = self.options['name']
        self.handle = super(OnosRestApiDriver,self).connect()
        main.log.info(self.options['topology_url'])
        try :
            self.handle = urllib.urlopen(self.options['topology_url'])
        except Exception,e:
            main.log.error(e)
            
        self.logFileName = main.logdir+"/"+self.name+".session"
        
        if self.handle:
            return self.handle
        else :
            return main.FALSE

    def execute(self):
        main.log.info(self.options['topology_url'])
        response = main.FALSE
        for i in [1,2] :
            time.sleep(2)
            response = self.http_request()
        return response
        
    def http_request(self):
        try :
            self.handle = urllib.urlopen(self.options['topology_url'])

            resonse_lines = self.handle.readlines()
            print resonse_lines
            return resonse_lines
        except Exception,e:
            main.log.error(e)
            return "url error"
   
    def disconnect(self,handle):
        response = ''
        '''
        if self.handle:
            self.handle = handle
            response = self.execute(cmd="exit",prompt="(.*)",timeout=120)
        else :
            main.log.error("Connection failed to the host")
            response = main.FALSE
        '''
        return response  
    
    
   
    
