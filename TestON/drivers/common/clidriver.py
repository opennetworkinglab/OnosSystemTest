#!/usr/bin/env python
'''
Created on 24-Oct-2012
    
@authors: Anil Kumar (anilkumar.s@paxterrasolutions.com),
          Raghav Kashyap(raghavkashyap@paxterrasolutions.com)


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


          
'''
import pexpect
import struct, fcntl, os, sys, signal
import sys, re
sys.path.append("../")

from drivers.component import Component
class CLI(Component):
    '''
        This will define common functions for CLI included.
    '''
    def __init__(self):
        super(Component, self).__init__()
        
    def connect(self,**connectargs):
        '''
           Connection will establish to the remote host using ssh.
           It will take user_name ,ip_address and password as arguments<br>
           and will return the handle. 
        '''
        for key in connectargs:
            vars(self)[key] = connectargs[key]

        connect_result = super(CLI, self).connect()
        ssh_newkey = 'Are you sure you want to continue connecting'
        refused = "ssh: connect to host "+self.ip_address+" port 22: Connection refused"
        if self.port:
            self.handle =pexpect.spawn('ssh -p '+self.port+' '+self.user_name+'@'+self.ip_address,maxread=50000)
        else :
            self.handle =pexpect.spawn('ssh -X '+self.user_name+'@'+self.ip_address,maxread=50000)

        self.handle.logfile = self.logfile_handler
	i = 5
	while i == 5:
	    i=self.handle.expect([ssh_newkey,'password:',pexpect.EOF,pexpect.TIMEOUT,refused,'teston>','>|#|\$'],120)
	    if i==0:
	        main.log.info("ssh key confirmation received, send yes")
	        self.handle.sendline('yes')
	        i=self.handle.expect([ssh_newkey,'password:',pexpect.EOF])
	    if i==1:
	        main.log.info("ssh connection asked for password, gave password")
	        self.handle.sendline(self.pwd)
	        self.handle.expect('>|#|\$')
	    elif i==2:
	        main.log.error("Connection timeout")
	        return main.FALSE
	    elif i==3: #timeout
	        main.log.error("No route to the Host "+self.user_name+"@"+self.ip_address)
	        return main.FALSE
	    elif i==4:
	        main.log.error("ssh: connect to host "+self.ip_address+" port 22: Connection refused")
	        return main.FALSE
	    elif i==6:
	        main.log.info("Password not required logged in")

        self.handle.sendline("\n")
        self.handle.expect('>|#|\$')
        return self.handle

    
    def disconnect(self):
        result = super(CLI, self).disconnect(self)
        result = main.TRUE
        #self.execute(cmd="exit",timeout=120,prompt="(.*)")
    
    
    def execute(self, **execparams):
        '''
        It facilitates the command line execution of a given command. It has arguments as :
        cmd => represents command to be executed,
        prompt => represents expect command prompt or output,
        timeout => timeout for command execution,
        more => to provide a key press if it is on.

        It will return output of command exection.
        '''

        result = super(CLI, self).execute(self)
        defaultPrompt = '.*[$>\#]'
        args = utilities.parse_args(["CMD", "TIMEOUT", "PROMPT", "MORE"], **execparams)
        expectPrompt = args["PROMPT"] if args["PROMPT"] else defaultPrompt
        self.LASTRSP = ""
        timeoutVar = args["TIMEOUT"] if args["TIMEOUT"] else 10
        cmd = ''
        if args["CMD"]:
            cmd = args["CMD"]
        else :
            return 0
        if args["MORE"] == None:
            args["MORE"] = " "
        self.handle.sendline(cmd)
        self.lastCommand = cmd
        index = self.handle.expect([expectPrompt, "--More--", 'Command not found.', pexpect.TIMEOUT,"^:$"], timeout = timeoutVar)
        if index == 0:
            self.LASTRSP = self.LASTRSP + self.handle.before + self.handle.after
            main.log.info("Executed :"+str(cmd)+" \t\t Expected Prompt '"+ str(expectPrompt)+"' Found")
        elif index == 1:
            self.LASTRSP = self.LASTRSP + self.handle.before
            self.handle.send(args["MORE"])
            main.log.info("Found More screen to go , Sending a key to proceed")
            indexMore = self.handle.expect(["--More--", expectPrompt], timeout = timeoutVar)
            while indexMore == 0:
                main.log.info("Found anoother More screen to go , Sending a key to proceed")
                self.handle.send(args["MORE"])
                indexMore = self.handle.expect(["--More--", expectPrompt], timeout = timeoutVar)
                self.LASTRSP = self.LASTRSP + self.handle.before
        elif index ==2:
            main.log.error("Command not found")
            self.LASTRSP = self.LASTRSP + self.handle.before
        elif index ==3:
            main.log.error("Expected Prompt not found , Time Out!!") 
            main.log.error( expectPrompt ) 
            return "Expected Prompt not found , Time Out!!"
        
        elif index == 4:
            self.LASTRSP = self.LASTRSP + self.handle.before
            #self.handle.send(args["MORE"])
            self.handle.sendcontrol("D")
            main.log.info("Found More screen to go , Sending a key to proceed")
            indexMore = self.handle.expect(["^:$", expectPrompt], timeout = timeoutVar)
            while indexMore == 0:
                main.log.info("Found anoother More screen to go , Sending a key to proceed")
                self.handle.sendcontrol("D")
                indexMore = self.handle.expect(["^:$", expectPrompt], timeout = timeoutVar)
                self.LASTRSP = self.LASTRSP + self.handle.before
        
        main.last_response = self.remove_contol_chars(self.LASTRSP)
        return self.LASTRSP
    
    def remove_contol_chars(self,response):
        #RE_XML_ILLEGAL = '([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])|([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])'%(unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff))  
        #response = re.sub(RE_XML_ILLEGAL, "\n", response) 
        response = re.sub(r"[\x01-\x1F\x7F]", "", response)
        #response = re.sub(r"\[\d+\;1H", "\n", response)
        response = re.sub(r"\[\d+\;\d+H", "", response)
        return response
        
    def runAsSudoUser(self,handle,pwd,default):
        
        i = handle.expect([".ssword:*",default, pexpect.EOF])
        if i==0:
            handle.sendline(pwd)
            handle.sendline("\r")

        if i==1:
            handle.expect(default)
        
        if i==2:
            main.log.error("Unable to run as Sudo user")
            
        return handle
        
    def onfail(self):
        if main.componentDictionary[self.name].has_key('onfail'):
            commandList = main.componentDictionary[self.name]['onfail'].split(",")
            for command in commandList :
                response = self.execute(cmd=command,prompt="(.*)",timeout=120)

    def secureCopy(self,user_name, ip_address,filepath, pwd,dst_path):
        
        #scp openflow@192.168.56.101:/home/openflow/sample /home/paxterra/Desktop/

        '''
           Connection will establish to the remote host using ssh.
           It will take user_name ,ip_address and password as arguments<br>
           and will return the handle. 
        '''
        ssh_newkey = 'Are you sure you want to continue connecting'
        refused = "ssh: connect to host "+ip_address+" port 22: Connection refused"
        self.handle =pexpect.spawn('scp '+user_name+'@'+ip_address+':'+filepath+' '+dst_path)
        i=self.handle.expect([ssh_newkey,'password:',pexpect.EOF,pexpect.TIMEOUT,refused],120)
        
        if i==0:    
            main.log.info("ssh key confirmation received, send yes")
            self.handle.sendline('yes')
            i=self.handle.expect([ssh_newkey,'password:',pexpect.EOF])
        if i==1:
            main.log.info("ssh connection asked for password, gave password")
            self.handle.sendline(pwd)
            #self.handle.expect(user_name)
            
        elif i==2:
            main.log.error("Connection timeout")
            pass
        elif i==3: #timeout
            main.log.error("No route to the Host "+user_name+"@"+ip_address)
            return main.FALSE
        elif i==4:
            main.log.error("ssh: connect to host "+ip_address+" port 22: Connection refused")
            return main.FALSE

        self.handle.sendline("\r")
        
        return self.handle
    
