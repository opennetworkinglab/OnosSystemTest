#!/usr/bin/env python

'''
This driver handles the optical switch emulator linc-oe.

Please follow the coding style demonstrated by existing
functions and document properly.

If you are a contributor to the driver, please
list your email here for future contact:

    andrew@onlab.us

OCT 20 2014
'''

import traceback
import pexpect
import struct
import fcntl
import os
import signal
import re
import sys
import core.teston
sys.path.append("../")
from math import pow
from drivers.common.cli.emulatordriver import Emulator
from drivers.common.clidriver import CLI

class LincOEDriver(Emulator):
    '''
    LincOEDriver class will handle all emulator functions    
    '''
    def __init__(self):
        super(Emulator, self).__init__()
        self.handle = self
        self.wrapped = sys.modules[__name__]
        self.flag = 0

    def connect(self, **connectargs):
        '''
        Create ssh handle for Linc-OE cli
        '''
        for key in connectargs:
            vars(self)[key] = connectargs[key]       
        
        self.name = self.options['name']
        self.handle = \
                super(LincOEDriver, self).connect(\
                user_name = self.user_name,
                ip_address = self.ip_address,
                port = None, 
                pwd = self.pwd)
        
        self.ssh_handle = self.handle
        
        if self.handle :
            main.log.info(self.name+": Starting Linc-OE CLI")
            cmdStr = "sudo ./rel/linc/bin/linc console"
            
            self.handle.sendline(cmdStr)
            #Sending blank lines "shows" the CLI
            self.handle.sendline("")
            self.handle.sendline("")
            self.handle.expect(["linc@",pexpect.EOF,pexpect.TIMEOUT])

        else:
            main.log.error(self.name+
                    ": Connection failed to the host "+
                    self.user_name+"@"+self.ip_address) 
            main.log.error(self.name+
                    ": Failed to connect to Linc-OE")
            return main.FALSE

    def set_interface_up(self, intfs):
        '''
        Specify interface to bring up.
        When Linc-OE is started, tap interfaces should
        be created. They must be brought up manually
        '''
        try:
            self.handle.sendline("ifconfig "+str(intf)+" up")
            self.handle.expect("linc@")
   
            handle = self.handle.before

            return handle

        except pexpect.EOF:
            main.log.error(self.name+ ": EOF exception")
            main.log.error(self.name+ ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" :::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" :::::::")
            main.cleanup()
            main.exit()


    def disconnect(self):
        '''
        Send disconnect prompt to Linc-OE CLI
        (CTRL+C)
        '''
        try:
            #Send CTRL+C twice to exit CLI
            self.handle.sendline("\x03")
            self.handle.sendline("\x03")
            self.handle.expect("\$")

        except pexpect.EOF:
            main.log.error(self.name+ ": EOF exception")
            main.log.error(self.name+ ":    " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name+" :::::::")
            main.log.error( traceback.print_exc())
            main.log.info(self.name+" :::::::")
            main.cleanup()
            main.exit()

if __name__ != "__main__":
    import sys
    sys.modules[__name__] = LincOEDriver()

