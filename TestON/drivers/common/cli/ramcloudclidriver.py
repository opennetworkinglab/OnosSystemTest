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
        self.home = "~/ONOS"
        for key in self.options:
           if key == "ONOShome":
               self.home = self.options['ONOShome']
               break

        
        self.name = self.options['name']
        self.handle = super(RamCloudCliDriver, self).connect(user_name = self.user_name, ip_address = self.ip_address,port = self.port, pwd = self.pwd, home = self.home)
        
        self.ssh_handle = self.handle
        if self.handle :
            return main.TRUE
        else :
            main.log.error(self.name+": Connection failed to the host "+self.user_name+"@"+self.ip_address) 
            main.log.error(self.name+": Failed to connect to the Onos system")
            return main.FALSE

    def kill_serv(self):
        import re
        try: 
            self.handle.sendline("ps -ef |grep 'master/server' |awk 'NR==1 {print $2}' |xargs sudo kill -9")
            self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
            self.handle.sendline("ps -ef |grep 'master/server' |wc -l")
            self.handle.expect(["wc -l",pexpect.EOF,pexpect.TIMEOUT])
            response = self.handle.after
            if re.search("1",response):
                return "RAMCloud Server Killed!"
            else:
                return "ERROR!!! RAMCLOUd SERVER MAY NOT HAVE BEEN KILLED PROPERLY!!!"
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
   
    def kill_coord(self):
        import re
        try: 
            self.handle.sendline("ps -ef |grep 'master/coordinator' |awk 'NR==1 {print $2}' |xargs sudo kill -9")
            self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
            self.handle.sendline("ps -ef |grep 'master/coordinator' |wc -l")
            self.handle.expect(["wc -l",pexpect.EOF,pexpect.TIMEOUT])
            response = self.handle.after
            if re.search("1",response):
                return "RAMCloud Coordinator Killed!"
            else:
                return "ERROR!!! RAMCLOUD COORDINATOR MAY NOT HAVE BEEN KILLED PROPERLY!!!"
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

   
 
    def start_serv(self):
        '''
        This Function will start RamCloud Servers
        '''
        main.log.info(self.name+": Starting RAMCloud Server" )
        self.handle.sendline("")
        self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
        self.handle.sendline("cd "+self.home)
        self.handle.sendline("./onos.sh rc-server start")
        self.handle.expect(["onos.sh rc-server start",pexpect.EOF,pexpect.TIMEOUT])
        self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
        response = self.handle.before + self.handle.after
        #print ("RESPONSE IS: "+response)
        time.sleep(5)
        if re.search("Killed\sexisting\sprocess", response):
            main.log.info(self.name + ": Previous RAMCloud killed. ")
            if re.search("Starting\sRAMCloud\sserver",response):
                main.log.info(self.name + ": RAMCloud Server Started")
                return main.TRUE
            else:
                main.log.info(self.name + ": Failed to start RAMCloud Server"+response)
                return main.FALSE
        elif re.search("Starting\sRAMCloud\sserver",response):
            main.log.info(self.name + ": RAMCloud Server Started")
            return main.TRUE
        else:
            main.log.info(self.name + ": Failed to start RAMCloud Server"+response)
            return main.FALSE

 
    def start_coor(self):
        '''
        This Function will start RamCloud
        '''
        main.log.info(self.name+": Starting RAMCloud Coordinator" )
        self.handle.sendline("")
        self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
        self.handle.sendline("cd "+self.home)
        self.handle.sendline("./onos.sh rc-coord start")
        self.handle.expect(["onos.sh rc-coord start",pexpect.EOF,pexpect.TIMEOUT])
        self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
        response = self.handle.before + self.handle.after
        if re.search("Starting\sRAMCloud\scoordinator\s", response):
            if re.search("Killed\sexisting\sprocess", response):
                main.log.warn(self.name+": Process was already running, killing existing process")
            main.log.info(self.name+": RAMCloud Coordinator Started ")
            return main.TRUE
        else:
            main.log.error(self.name+": Failed to start RAMCloud Coordinator"+ response)
            return main.FALSE

    def status_serv(self):
        '''
        This Function will return the Status of the RAMCloud
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
            return main.FALSE
        elif re.search("1\sRAMCloud\sserver\srunning",response):
            main.log.warn(self.name+": RAMCloud Running")
            return main.TRUE
        else:
            main.log.info( self.name+":  WARNING: status recieved unknown response")
            return main.FALSE
            
    def status_coor(self):
        '''
        This Function will return the Status of the RAMCloud
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
            return main.FALSE
        elif re.search("1\sRAMCloud\scoordinator\srunning", response):
            main.log.info(self.name+": RAMCloud Coordinator Running")
            return main.TRUE
        else:
            main.log.warn( self.name+": coordinator status recieved unknown response")
            return main.FALSE

    def stop_serv(self):
        '''
        This Function will stop the RAMCloud if it is Running
        '''
        main.log.info(self.name + ": Stopping RC-Server")
        self.handle.sendline("")
        self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
        self.handle.sendline("cd "+self.home)
        self.handle.sendline("./onos.sh rc-server stop")
        self.handle.expect(["onos.sh rc-server stop",pexpect.EOF,pexpect.TIMEOUT])
        self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
        response = self.handle.before + self.handle.after
        if re.search("Killed\sexisting\sprocess",response):
            main.log.info("RAMCloud Server Stopped")
            return main.TRUE
        else:
            main.log.warn(self.name+": RAMCloud is not Running")
            return main.FALSE

    def del_db(self):
        '''
        This function will clean out the database
        '''
        main.log.info(self.name + ": Deleting RC Database")
        self.handle.sendline("")
        self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
        self.handle.sendline("cd "+self.home)
        self.handle.sendline("./onos.sh rc deldb")
        self.handle.expect(["\[y/N\]",pexpect.EOF,pexpect.TIMEOUT])
        self.handle.sendline("y")
        self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
        response = self.handle.before + self.handle.after
        if re.search("DONE",response) or re.search("Terminated",response):
            main.log.info("RAMCloud Database Cleaned")
            return main.TRUE
        else:
            main.log.warn("Something wrong in Cleaning Database")
            main.log.warn(self.handle.before)
            return main.FALSE
           

    def stop_coor(self):
        '''
        This Function will stop the RAMCloud if it is Running
        ''' 
        main.log.info(self.name + ": Stopping RC-Coord")
        self.handle.sendline("")
        self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
        self.handle.sendline("cd "+self.home)
        self.handle.sendline( "./onos.sh rc-coord stop")
        self.handle.expect(["onos.sh rc-coord stop",pexpect.EOF,pexpect.TIMEOUT])
        self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
        response = self.handle.before + self.handle.after
        if re.search("Killed\sexisting\sprocess",response):
            main.log.info(self.name+": RAMCloud Coordinator Stopped")
            return main.TRUE
        else:
            main.log.warn(self.name+": RAMCloud was not Running")
            return main.FALSE
 
    def disconnect(self):
        ''' 
        Called at the end of the test to disconnect the ssh handle. 
        ''' 
        response = ''
        if self.handle:
            self.handle.sendline("exit")
            self.handle.expect(["closed",pexpect.EOF,pexpect.TIMEOUT])
        else :
            main.log.error("Connection failed to the host when trying to disconnect from RAMCloud component")
            response = main.FALSE
        return response 
