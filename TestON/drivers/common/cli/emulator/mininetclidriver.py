#!/usr/bin/env python
'''
Created on 26-Oct-2012

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


MininetCliDriver is the basic driver which will handle the Mininet functions
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
from drivers.common.cli.emulatordriver import Emulator
from drivers.common.clidriver import CLI

class MininetCliDriver(Emulator):
    '''
    MininetCliDriver is the basic driver which will handle the Mininet functions
    '''
    def __init__(self):
        super(Emulator, self).__init__()
        self.handle = self
        self.wrapped = sys.modules[__name__]
        self.flag = 0

    def connect(self, **connectargs):
        '''
        Here the main is the TestON instance after creating all the log handles.
        '''
        for key in connectargs:
            vars(self)[key] = connectargs[key]       
        
        self.name = self.options['name']
        self.handle = super(MininetCliDriver, self).connect(user_name = self.user_name, ip_address = self.ip_address,port = None, pwd = self.pwd)
        
        self.ssh_handle = self.handle
        
        if self.handle :
            main.log.info(self.name+": Clearing any residual state or processes")
            self.handle.sendline("sudo mn -c")
            i=self.handle.expect(['password\sfor\s','Cleanup\scomplete',pexpect.EOF,pexpect.TIMEOUT],120)
            if i==0:
                main.log.info(self.name+": Sending sudo password")
                self.handle.sendline(self.pwd)
                i=self.handle.expect(['%s:'%(self.user),'\$',pexpect.EOF,pexpect.TIMEOUT],120) 
            if i==1:
                main.log.info(self.name+": Clean")
            elif i==2:
                main.log.error(self.name+": Connection terminated")
            elif i==3: #timeout
                main.log.error(self.name+": Something while cleaning MN took too long... " )
 
            main.log.info(self.name+": building fresh mininet") 
            #### for reactive/PARP enabled tests
            cmdString = "sudo mn " + self.options['arg1'] + " " + self.options['arg2'] +  " --mac --controller " + self.options['controller']
            #### for proactive flow with static ARP entries
            #cmdString = "sudo mn " + self.options['arg1'] + " " + self.options['arg2'] +  " --mac --arp --controller " + self.options['controller']
            self.handle.sendline(cmdString)
            self.handle.expect(["sudo mn",pexpect.EOF,pexpect.TIMEOUT])
            while 1: 
                i=self.handle.expect(['mininet>','\*\*\*','Exception',pexpect.EOF,pexpect.TIMEOUT],300)
                if i==0:
                    main.log.info(self.name+": mininet built") 
                    return main.TRUE
                if i==1:
                    self.handle.expect(["\n",pexpect.EOF,pexpect.TIMEOUT])
                    main.log.info(self.handle.before)
                elif i==2:
                    main.log.error(self.name+": Launching mininet failed...")
                    return main.FALSE
                elif i==3:
                    main.log.error(self.name+": Connection timeout")
                    return main.FALSE
                elif i==4: #timeout
                    main.log.error(self.name+": Something took too long... " )
                    return main.FALSE
            #if utilities.assert_matches(expect=patterns,actual=resultCommand,onpass="Network is being launched",onfail="Network launching is being failed "):
            return main.TRUE
        else:#if no handle
            main.log.error(self.name+": Connection failed to the host "+self.user_name+"@"+self.ip_address) 
            main.log.error(self.name+": Failed to connect to the Mininet")
            return main.FALSE
                       
    def pingall(self):
        '''
        Verifies the reachability of the hosts using pingall command.
        '''
        if self.handle :
            main.log.info(self.name+": Checking reachabilty to the hosts using pingall")
            try:
                response = self.execute(cmd="pingall",prompt="mininet>",timeout=120)
            except pexpect.EOF:  
                main.log.error(self.name + ": EOF exception found")
                main.log.error(self.name + ":     " + self.handle.before)
                main.cleanup()
                main.exit()
            pattern = 'Results\:\s0\%\sdropped\s\(0\/\d+\slost\)\s*$'
            #if utilities.assert_matches(expect=pattern,actual=response,onpass="All hosts are reaching",onfail="Unable to reach all the hosts"):
            if re.search(pattern,response):
                main.log.info(self.name+": All hosts are reachable")
                return main.TRUE
            else:
                main.log.error(self.name+": Unable to reach all the hosts")
                return main.FALSE
        else :
            main.log.error(self.name+": Connection failed to the host") 
            return main.FALSE

    def fpingHost(self,**pingParams):
        ''' 
        Uses the fping package for faster pinging...
        *requires fping to be installed on machine running mininet 
        ''' 
        args = utilities.parse_args(["SRC","TARGET"],**pingParams)
        command = args["SRC"] + " fping -i 100 -t 20 -C 1 -q "+args["TARGET"]
        self.handle.sendline(command) 
        self.handle.expect([args["TARGET"],pexpect.EOF,pexpect.TIMEOUT]) 
        self.handle.expect(["mininet",pexpect.EOF,pexpect.TIMEOUT])
        response = self.handle.before 
        if re.search(":\s-" ,response):
            main.log.info(self.name+": Ping fail") 
            return main.FALSE
        elif re.search(":\s\d{1,2}\.\d\d", response):
            main.log.info(self.name+": Ping good!")
            return main.TRUE
        main.log.info(self.name+": Install fping on mininet machine... ") 
        main.log.info(self.name+": \n---\n"+response)
        return main.FALSE
        
    def pingHost(self,**pingParams):
        '''
        Ping from one mininet host to another
        Currently the only supported Params: SRC and TARGET
        '''
        args = utilities.parse_args(["SRC","TARGET"],**pingParams)
        #command = args["SRC"] + " ping -" + args["CONTROLLER"] + " " +args ["TARGET"]
        command = args["SRC"] + " ping "+args ["TARGET"]+" -c 1 -i 1 -W 8"
        try:
            main.log.warn("Sending: " + command)
            #response = self.execute(cmd=command,prompt="mininet",timeout=10 )
            self.handle.sendline(command)
            i = self.handle.expect([command,pexpect.TIMEOUT])
            if i == 1:
                main.log.error(self.name + ": timeout when waiting for response from mininet")
                main.log.error("response: " + str(self.handle.before))
            i = self.handle.expect(["mininet>",pexpect.TIMEOUT])
            if i == 1:
                main.log.error(self.name + ": timeout when waiting for response from mininet")
                main.log.error("response: " + str(self.handle.before))
            response = self.handle.before
        except pexpect.EOF:  
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        main.log.info(self.name+": Ping Response: "+ response )
        #if utilities.assert_matches(expect=',\s0\%\spacket\sloss',actual=response,onpass="No Packet loss",onfail="Host is not reachable"):
        if re.search(',\s0\%\spacket\sloss',response):
            main.log.info(self.name+": no packets lost, host is reachable")
            main.last_result = main.TRUE 
            return main.TRUE
        else :
            main.log.error(self.name+": PACKET LOST, HOST IS NOT REACHABLE")
            main.last_result = main.FALSE
            return main.FALSE
    
    def checkIP(self,host):
        '''
        Verifies the host's ip configured or not.
        '''
        if self.handle :
            try:
                response = self.execute(cmd=host+" ifconfig",prompt="mininet>",timeout=10)
            except pexpect.EOF:  
                main.log.error(self.name + ": EOF exception found")
                main.log.error(self.name + ":     " + self.handle.before)
                main.cleanup()
                main.exit()

            pattern = "inet\s(addr|Mask):([0-1]{1}[0-9]{1,2}|2[0-4][0-9]|25[0-5]|[0-9]{1,2}).([0-1]{1}[0-9]{1,2}|2[0-4][0-9]|25[0-5]|[0-9]{1,2}).([0-1]{1}[0-9]{1,2}|2[0-4][0-9]|25[0-5]|[0-9]{1,2}).([0-1]{1}[0-9]{1,2}|2[0-4][0-9]|25[0-5]|[0-9]{1,2})"
            #pattern = "inet addr:10.0.0.6"  
            #if utilities.assert_matches(expect=pattern,actual=response,onpass="Host Ip configured properly",onfail="Host IP not found") :
            if re.search(pattern,response):
                main.log.info(self.name+": Host Ip configured properly")
                return main.TRUE
            else:
                main.log.error(self.name+": Host IP not found")
                return main.FALSE
        else :
            main.log.error(self.name+": Connection failed to the host") 
            
    def verifySSH(self,**connectargs):
        try:
            response = self.execute(cmd="h1 /usr/sbin/sshd -D&",prompt="mininet>",timeout=10)
            response = self.execute(cmd="h4 /usr/sbin/sshd -D&",prompt="mininet>",timeout=10)
            for key in connectargs:
                vars(self)[key] = connectargs[key]
            response = self.execute(cmd="xterm h1 h4 ",prompt="mininet>",timeout=10)
        except pexpect.EOF:  
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        import time
        time.sleep(20)
        if self.flag == 0:
            self.flag = 1
            return main.FALSE
        else :
            return main.TRUE
    
    def getMacAddress(self,host):
        '''
        Verifies the host's ip configured or not.
        '''
        if self.handle :
            try:
                response = self.execute(cmd=host+" ifconfig",prompt="mininet>",timeout=10)
            except pexpect.EOF:  
                main.log.error(self.name + ": EOF exception found")
                main.log.error(self.name + ":     " + self.handle.before)
                main.cleanup()
                main.exit()

            pattern = r'HWaddr\s([0-9A-F]{2}[:-]){5}([0-9A-F]{2})'
            mac_address_search = re.search(pattern, response, re.I)
            mac_address = mac_address_search.group().split(" ")[1]
            main.log.info(self.name+": Mac-Address of Host "+ host + " is " + mac_address)
            return mac_address
        else :
            main.log.error(self.name+": Connection failed to the host") 

    def getInterfaceMACAddress(self,host, interface):
        '''
            Return the IP address of the interface on the given host
        '''
        if self.handle :
            try:
                response = self.execute(cmd=host+" ifconfig " + interface,
                                    prompt="mininet>",timeout=10)
            except pexpect.EOF:  
                main.log.error(self.name + ": EOF exception found")
                main.log.error(self.name + ":     " + self.handle.before)
                main.cleanup()
                main.exit()

            pattern = r'HWaddr\s([0-9A-F]{2}[:-]){5}([0-9A-F]{2})'
            mac_address_search = re.search(pattern, response, re.I)
            if mac_address_search is None:
                main.log.info("No mac address found in %s" % response)
                return main.FALSE
            mac_address = mac_address_search.group().split(" ")[1]
            main.log.info("Mac-Address of "+ host + ":"+ interface + " is " + mac_address)
            return mac_address
        else:
            main.log.error("Connection failed to the host")

    def getIPAddress(self,host):
        '''
        Verifies the host's ip configured or not.
        '''
        if self.handle :
            try:
                response = self.execute(cmd=host+" ifconfig",prompt="mininet>",timeout=10)
            except pexpect.EOF:  
                main.log.error(self.name + ": EOF exception found")
                main.log.error(self.name + ":     " + self.handle.before)
                main.cleanup()
                main.exit()

            pattern = "inet\saddr:(\d+\.\d+\.\d+\.\d+)"
            ip_address_search = re.search(pattern, response)
            main.log.info(self.name+": IP-Address of Host "+host +" is "+ip_address_search.group(1))
            return ip_address_search.group(1)
        else :
            main.log.error(self.name+": Connection failed to the host") 
        
    def getSwitchDPID(self,switch):
        '''
            return the datapath ID of the switch
        '''
        if self.handle :
            cmd = "py %s.dpid" % switch
            try:
                response = self.execute(cmd=cmd,prompt="mininet>",timeout=10)
            except pexpect.EOF:  
                main.log.error(self.name + ": EOF exception found")
                main.log.error(self.name + ":     " + self.handle.before)
                main.cleanup()
                main.exit()
            pattern = r'^(?P<dpid>\d)+'
            result = re.search(pattern, response, re.MULTILINE)
            if result is None:
                main.log.info("Couldn't find DPID for switch '', found: %s" % (switch, response))
                return main.FALSE
            return str(result.group(0))
        else:
            main.log.error("Connection failed to the host")

    def getDPID(self, switch):
        if self.handle:
            self.handle.sendline("")
            self.expect("mininet>")
            cmd = "py %s.dpid" %switch
            try:
                response = self.execute(cmd=cmd,prompt="mininet>",timeout=10)
                self.handle.expect("mininet>")
                response = self.handle.before
                return response
            except pexpect.EOF:
                main.log.error(self.name + ": EOF exception found")
                main.log.error(self.name + ":     " + self.handle.before)
                main.cleanup()
                main.exit()


    def getInterfaces(self, node):
        '''
            return information dict about interfaces connected to the node
        '''
        if self.handle :
            cmd = 'py "\\n".join(["name=%s,mac=%s,ip=%s,isUp=%s" % (i.name, i.MAC(), i.IP(), i.isUp())'
            cmd += ' for i in %s.intfs.values()])' % node
            try:
                response = self.execute(cmd=cmd,prompt="mininet>",timeout=10)
            except pexpect.EOF:  
                main.log.error(self.name + ": EOF exception found")
                main.log.error(self.name + ":     " + self.handle.before)
                main.cleanup()
                main.exit()
            return response
        else:
            main.log.error("Connection failed to the node")

    def dump(self):
        main.log.info(self.name+": Dump node info")
        try:
            response = self.execute(cmd = 'dump',prompt = 'mininet>',timeout = 10)
        except pexpect.EOF:  
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        return response
            
    def intfs(self):
        main.log.info(self.name+": List interfaces")
        try:
            response = self.execute(cmd = 'intfs',prompt = 'mininet>',timeout = 10)
        except pexpect.EOF:  
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        return response
    
    def net(self):
        main.log.info(self.name+": List network connections")
        try:
            response = self.execute(cmd = 'net',prompt = 'mininet>',timeout = 10)
        except pexpect.EOF:  
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        return response
    
    def iperf(self):
        main.log.info(self.name+": Simple iperf TCP test between two (optionally specified) hosts")
        try:
            response = self.execute(cmd = 'iperf',prompt = 'mininet>',timeout = 10)
        except pexpect.EOF:  
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        return response
    
    def iperfudp(self):
        main.log.info(self.name+": Simple iperf TCP test between two (optionally specified) hosts")
        try:
            response = self.execute(cmd = 'iperfudp',prompt = 'mininet>',timeout = 10)
        except pexpect.EOF:  
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        return response
    
    def nodes(self):
        main.log.info(self.name+": List all nodes.")
        try:
            response = self.execute(cmd = 'nodes',prompt = 'mininet>',timeout = 10)    
        except pexpect.EOF:  
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        return response
    
    def pingpair(self):
        main.log.info(self.name+": Ping between first two hosts")
        try:
            response = self.execute(cmd = 'pingpair',prompt = 'mininet>',timeout = 20)
        except pexpect.EOF:  
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        
        #if utilities.assert_matches(expect='0% packet loss',actual=response,onpass="No Packet loss",onfail="Hosts not reachable"):
        if re.search(',\s0\%\spacket\sloss',response):
            main.log.info(self.name+": Ping between two hosts SUCCESSFUL")
            main.last_result = main.TRUE 
            return main.TRUE
        else :
            main.log.error(self.name+": PACKET LOST, HOSTS NOT REACHABLE")
            main.last_result = main.FALSE
            return main.FALSE
    
    def link(self,**linkargs):
        '''
        Bring link(s) between two nodes up or down
        '''
        main.log.info('Bring link(s) between two nodes up or down')
        args = utilities.parse_args(["END1","END2","OPTION"],**linkargs)
        end1 = args["END1"] if args["END1"] != None else ""
        end2 = args["END2"] if args["END2"] != None else ""
        option = args["OPTION"] if args["OPTION"] != None else ""
        command = "link "+str(end1) + " " + str(end2)+ " " + str(option)
        try:
            #response = self.execute(cmd=command,prompt="mininet>",timeout=10)
            self.handle.sendline(command)
            self.handle.expect("mininet>")    
        except pexpect.EOF:  
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        return main.TRUE
        

    def yank(self,**yankargs):
	'''
	yank a mininet switch interface to a host
	'''
	main.log.info('Yank the switch interface attached to a host')
	args = utilities.parse_args(["SW","INTF"],**yankargs)
	sw = args["SW"] if args["SW"] !=None else ""
	intf = args["INTF"] if args["INTF"] != None else ""
	command = "py "+ str(sw) + '.detach("' + str(intf) + '")'
        try:
            response = self.execute(cmd=command,prompt="mininet>",timeout=10)
        except pexpect.EOF:  
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
	return main.TRUE

    def plug(self, **plugargs):
        '''
        plug the yanked mininet switch interface to a switch
        '''
        main.log.info('Plug the switch interface attached to a switch')
        args = utilities.parse_args(["SW","INTF"],**plugargs)
        sw = args["SW"] if args["SW"] !=None else ""
        intf = args["INTF"] if args["INTF"] != None else ""
        command = "py "+ str(sw) + '.attach("' + str(intf) + '")'
        try:
            response = self.execute(cmd=command,prompt="mininet>",timeout=10)
        except pexpect.EOF:  
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        return main.TRUE



    def dpctl(self,**dpctlargs):
        '''
        Run dpctl command on all switches.
        '''
        main.log.info('Run dpctl command on all switches')
        args = utilities.parse_args(["CMD","ARGS"],**dpctlargs)
        cmd = args["CMD"] if args["CMD"] != None else ""
        cmdargs = args["ARGS"] if args["ARGS"] != None else ""
        command = "dpctl "+cmd + " " + str(cmdargs)
        try:
            response = self.execute(cmd=command,prompt="mininet>",timeout=10)
        except pexpect.EOF:  
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        return main.TRUE
   
        
    def get_version(self):
        file_input = path+'/lib/Mininet/INSTALL'
        version = super(Mininet, self).get_version()
        pattern = 'Mininet\s\w\.\w\.\w\w*'
        for line in open(file_input,'r').readlines():
            result = re.match(pattern, line)
            if result:
                version = result.group(0)
        return version 

    def get_sw_controller_sanity(self, sw):
        command = "sh ovs-vsctl get-controller "+str(sw)
        try:
            response = self.execute(cmd=command,prompt="mininet>",timeout=10)
            if response:
                return main.TRUE
            else:
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        else:
            main.log.info(response)

    def get_sw_controller(self,sw):
        command = "sh ovs-vsctl get-controller "+str(sw)
        try:
            response = self.execute(cmd=command,prompt="mininet>",timeout=10)
            print(response)
            if response:
                print("**********************")
                return response
            else:
                return main.FALSE
        except pexpect.EOF:  
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        else:
            main.log.info(response)

    def assign_sw_controller(self,**kwargs):
        '''
        count is only needed if there is more than 1 controller
        '''
        args = utilities.parse_args(["COUNT"],**kwargs)
        count = args["COUNT"] if args!={} else 1

        argstring = "SW"
        for j in range(count):
            argstring = argstring + ",IP" + str(j+1) + ",PORT" + str(j+1)
        args = utilities.parse_args(argstring.split(","),**kwargs)

        sw = args["SW"] if args["SW"] != None else ""
        ptcpA = int(args["PORT1"])+int(sw) if args["PORT1"] != None else ""
        ptcpB = "ptcp:"+str(ptcpA) if ptcpA != "" else ""
        
        command = "sh ovs-vsctl set-controller s" + str(sw) + " " + ptcpB + " "
        for j in range(count):
            i=j+1
            args = utilities.parse_args(["IP"+str(i),"PORT"+str(i)],**kwargs)
            ip = args["IP"+str(i)] if args["IP"+str(i)] != None else ""
            port = args["PORT" + str(i)] if args["PORT" + str(i)] != None else ""
            tcp = "tcp:" + str(ip) + ":" + str(port) + " " if ip != "" else ""
            command = command + tcp
        try:
            self.execute(cmd=command,prompt="mininet>",timeout=5)
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def delete_sw_controller(self,sw):
        '''
        Removes the controller target from sw
        '''

        command = "sh ovs-vsctl del-controller "+str(sw)
        try:
            response = self.execute(cmd=command,prompt="mininet>",timeout=10)
        except pexpect.EOF:  
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        else:
            main.log.info(response)


    def disconnect(self):
        main.log.info(self.name+": Disconnecting mininet...")
        response = ''
        if self.handle:
            try:
                response = self.execute(cmd="exit",prompt="(.*)",timeout=120)
                response = self.execute(cmd="exit",prompt="(.*)",timeout=120)
                self.handle.sendline("sudo mn -c")
            except pexpect.EOF:  
                main.log.error(self.name + ": EOF exception found")
                main.log.error(self.name + ":     " + self.handle.before)
                main.cleanup()
                main.exit()
        else :
            main.log.error(self.name+": Connection failed to the host")
            response = main.FALSE
        return response  
  
    def arping(self, src, dest, destmac):
        self.handle.sendline('')
        self.handle.expect(["mininet",pexpect.EOF,pexpect.TIMEOUT])

        self.handle.sendline(src + ' arping ' + dest)
        try:
            self.handle.expect([destmac,pexpect.EOF,pexpect.TIMEOUT])
            main.log.info(self.name+": ARP successful")
            self.handle.expect(["mininet",pexpect.EOF,pexpect.TIMEOUT])
            return main.TRUE
        except:
            main.log.warn(self.name+": ARP FAILURE")
            self.handle.expect(["mininet",pexpect.EOF,pexpect.TIMEOUT])
            return main.FALSE

    def decToHex(num):
        return hex(num).split('x')[1]
    
    def getSwitchFlowCount(self, switch):
        '''
        return the Flow Count of the switch
        '''
        if self.handle:
            cmd = "sh ovs-ofctl dump-aggregate %s" % switch
            try:
                response = self.execute(cmd=cmd, prompt="mininet>", timeout=10)
            except pexpect.EOF:
                main.log.error(self.name + ": EOF exception found")
                main.log.error(self.name + "     " + self.handle.before)
                main.cleanup()
                main.exit()
            pattern = "flow_count=(\d+)"
            result = re.search(pattern, response, re.MULTILINE)
            if result is None:
                print "no flow on switch print test"
                main.log.info("Couldn't find flows on switch '', found: %s" % (switch, response))
                return main.FALSE
            return result.group(1)
        else:
            main.log.error("Connection failed to the Mininet host")
    
    def check_flows(self, sw, dump_format=None):
        if dump_format:
          command = "sh ovs-ofctl -F " + dump_format + " dump-flows " + str(sw)
        else:
          command = "sh ovs-ofctl dump-flows "+str(sw)
        try:
            response=self.execute(cmd=command,prompt="mininet>",timeout=10)
            return response
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        else:
            main.log.info(response)

    def start_tcpdump(self, filename, intf = "eth0", port = "port 6633"):
        '''
        Runs tpdump on an intferface and saves the file
        intf can be specified, or the default eth0 is used
        '''
        try:
            self.handle.sendline("")
            self.handle.expect("mininet>")
            self.handle.sendline("sh sudo tcpdump -n -i "+ intf + " " + port + " -w " + filename.strip() + "  &")
            self.handle.sendline("")
            self.handle.sendline("")
            i=self.handle.expect(['No\ssuch\device','listening\son',pexpect.TIMEOUT,"mininet>"],timeout=10)
            main.log.warn(self.handle.before + self.handle.after)
            if i == 0:
                main.log.error(self.name + ": tcpdump - No such device exists. tcpdump attempted on: " + intf)
                return main.FALSE
            elif i == 1:
                main.log.info(self.name + ": tcpdump started on " + intf)
                return main.TRUE
            elif i == 2:
                main.log.error(self.name + ": tcpdump command timed out! Check interface name, given interface was: " + intf)
                return main.FALSE
            elif i ==3: 
                main.log.info(self.name +": " +  self.handle.before)
                return main.TRUE
            else:
                main.log.error(self.name + ": tcpdump - unexpected response")
            return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def stop_tcpdump(self):
        "pkills tcpdump"
        try:
            self.handle.sendline("sh sudo pkill tcpdump")
            self.handle.sendline("")
            self.handle.sendline("")
            self.handle.expect("mininet>")
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        except:
            main.log.info(self.name + ":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.log.error( traceback.print_exc() )
            main.log.info(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
            main.cleanup()
            main.exit()

    def compare_topo(self, topo, onos_json):
        '''
        compares mn topology with ONOS topology
        onos_list is a list of ONOS controllers, each element of the list should be (handle, name, ip, port)
        onos_json is the output of the onos get_json function calling the /wm/onos/topology REST API
        Returns: True if MN and ONOS topology match and False if the differ. 
        Differences between ONOS and MN topology will be printed to the log.

        Dependency: Requires STS to be installed on the TestON machine. STS can be pulled 
        from https://github.com/ucb-sts/sts.git . Currently the required functions from STS are located in the 
        topology_refactoring2 branch, but may be merged into the master branch soon. You may need to install some
        python modules such as networkx to use the STS functions.

        To install sts:
            $ git clone git://github.com/ucb-sts/sts.git
            $ cd sts
            $ git clone -b debugger git://github.com/ucb-sts/pox.git
            $ sudo apt-get install python-dev
            $ ./tools/install_hassel_python.sh
            $ sudo pip install networkx

        Include sts in your PYTHONPATH. it should looks comething like: 
            PYTHONPATH=/home/admin/TestON:/home/admin/sts

        '''
        import sys
        sys.path.append("~/sts")
        #NOTE: Create this once per Test and pass the TestONTopology object around. It takes too long to create this object.
        #      This will make it easier to use the sts methods for severing links and solve that issue
        import json

        link_results = main.TRUE
        switch_results = main.TRUE
        port_results = main.TRUE

        ########Switches#######
        output = {"switches":[]}
        for switch in topo.graph.switches: #iterate through the MN topology and pull out switches and and port info
            ports = []
            for port in switch.ports.values():
                #print port.hw_addr.toStr(separator = '')
                ports.append({'of_port': port.port_no, 'mac': str(port.hw_addr).replace('\'',''), 'name': port.name})
            output['switches'].append({"name": switch.name, "dpid": str(switch.dpid).zfill(16), "ports": ports })
        #print output

        #print json.dumps(output, sort_keys=True,indent=4,separators=(',', ': '))


        # created sorted list of dpid's in MN and ONOS for comparison
        mnDPIDs=[]
        for switch in output['switches']:
            mnDPIDs.append(switch['dpid'])
        mnDPIDs.sort()
        #print mnDPIDs
        if onos_json == "":#if rest call fails
            main.log.error(self.name + ".compare_topo(): Empty JSON object given from ONOS rest call")
            return main.FALSE
        onos=onos_json
        onosDPIDs=[]
        for switch in onos['switches']:
            onosDPIDs.append(switch['dpid'].replace(":",''))
        onosDPIDs.sort()
        #print onosDPIDs

        if mnDPIDs!=onosDPIDs:
            switch_results = main.FALSE
            main.log.report( "Switches in MN but not in ONOS:")
            main.log.report( str([switch for switch in mnDPIDs if switch not in onosDPIDs]))
            main.log.report( "Switches in ONOS but not in MN:")
            main.log.report(  str([switch for switch in onosDPIDs if switch not in mnDPIDs]))
        else:#list of dpid's match in onos and mn
            switch_results = main.TRUE

        ################ports#############
            for switch in output['switches']:
                mn_ports = []
                onos_ports = []
                for port in switch['ports']:
                    mn_ports.append(port['of_port'])
                for onos_switch in onos['switches']:
                    if onos_switch['dpid'].replace(':','') == switch['dpid']:
                        for port in onos_switch['ports']:
                            onos_ports.append(port['portNumber']) 
                mn_ports.sort()
                onos_ports.sort()
                if mn_ports == onos_ports:
                    pass #don't set results to true here as this is just one of many checks and it might override a failure
                else: #the ports of this switch don't match
                    port_results = main.FALSE
                    main.log.report("ports in MN switch %s(%s) but not in ONOS:" % (switch['name'],switch['dpid'])) 
                    main.log.report( str([port for port in mn_ports if port not in onos_ports]))
                    main.log.report("ports in ONOS switch %s(%s) but not in MN:" % (switch['name'],switch['dpid']))
                    main.log.report( str([port for port in onos_ports if port not in mn_ports]))


        #######Links########
        # iterate through MN links and check if and ONOS link exists in both directions
        # NOTE: Will currently only show mn links as down if they are cut through STS. 
        #       We can either do everything through STS or wait for up_network_links 
        #       and down_network_links to be fully implemented.
        for link in topo.patch_panel.network_links: 
            #print "Link: %s" % link
            #TODO: Find a more efficient search method
            node1 = None
            port1 = None
            node2 = None
            port2 = None
            first_dir = main.FALSE
            second_dir = main.FALSE
            for switch in output['switches']:
                if switch['name'] == link.node1.name:
                    node1 = switch['dpid']
                    for port in switch['ports']:
                        if str(port['name']) == str(link.port1):
                            port1 = port['of_port'] 
                    if node1 is not None and node2 is not None:
                        break
                if switch['name'] == link.node2.name:
                    node2 = switch['dpid']
                    for port in switch['ports']: 
                        if str(port['name']) == str(link.port2):
                            port2 = port['of_port'] 
                    if node1 is not None and node2 is not None:
                        break
            # check onos link from node1 to node2
            for onos_link in onos['links']:
                if onos_link['src']['dpid'].replace(":",'') == node1 and onos_link['dst']['dpid'].replace(":",'') == node2:
                    if onos_link['src']['portNumber'] == port1 and onos_link['dst']['portNumber'] == port2:
                        first_dir = main.TRUE
                    else:
                        main.log.report('the port numbers do not match for ' +str(link) + ' between ONOS and MN')
                    #print node1, ' to ', node2
                elif onos_link['src']['dpid'].replace(":",'') == node2 and onos_link['dst']['dpid'].replace(":",'') == node1:
                    if onos_link['src']['portNumber'] == port2 and onos_link['dst']['portNumber'] == port1:
                        second_dir = main.TRUE
                    else:
                        main.log.report('the port numbers do not match for ' +str(link) + ' between ONOS and MN')
                    #print node2, ' to ', node1
                else:#this is not the link you're looking for
                    pass
            if not first_dir:
                main.log.report('ONOS has issues with the link from '+str(link.node1.name) +"(dpid: "+ str(node1)+"):"+str(link.port1)+"(portNumber: "+str(port1)+")"+ ' to ' + str(link.node2.name) +"(dpid: "+ str(node2)+"):"+str(link.port2)+"(portNumber: "+str(port2)+")")
            if not second_dir:
                main.log.report('ONOS has issues with the link from '+str(link.node2.name) +"(dpid: "+ str(node2)+"):"+str(link.port2)+"(portNumber: "+str(port2)+")"+ ' to ' + str(link.node1.name) +"(dpid: "+ str(node1)+"):"+str(link.port1)+"(portNumber: "+str(port1)+")")
            link_results = link_results and first_dir and second_dir

        
        results =  switch_results and port_results and link_results
#        if not results: #To print out both topologies
#            main.log.error("Topology comparison failed, printing json objects, MN then ONOS")
#            main.log.error(str(json.dumps(output, sort_keys=True,indent=4,separators=(',', ': '))))
#            main.log.error('MN Links:')
#            for link in topo.patch_panel.network_links: main.log.error(str("\tLink: %s" % link))
#            main.log.error(str(json.dumps(onos, sort_keys=True,indent=4,separators=(',', ': '))))
        return results


    def links_status(self):
        """
        Returns list of links and their status
        """
        if self.handle :
            cmd = "py 'Links: %s' % [item for sublist in [[(y[0].name, y[1].name, y[0].isUp() and y[1].isUp()) for y in x[0].connectionsTo(x[1])] for x in __import__('itertools').permutations(net.nameToNode.values(), 2) if x[0] != x[1] and x[0].connectionsTo(x[1])] for item in sublist]"
            try:
                response = self.execute(cmd=cmd,prompt="mininet>",timeout=10)
                if not response:
                  return None
                for line in response.split('\n'):
                  if line.startswith('Links:'):
                    return eval(line[len("Links :"):])
            except pexpect.EOF:
                main.log.error(self.name + ": EOF exception found")
                main.log.error(self.name + ":     " + self.handle.before)
                main.cleanup()
                main.exit()
            return response
        else:
            main.log.error("Connection failed to the node")



if __name__ != "__main__":
    import sys
    sys.modules[__name__] = MininetCliDriver()

