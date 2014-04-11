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
                response = self.execute(cmd="pingall",prompt="mininet>",timeout=10)
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
        command = args["SRC"] + " ping "+args ["TARGET"]+" -c 1 -i 1"
        try:
            response = self.execute(cmd=command,prompt="mininet",timeout=10 )
        except pexpect.EOF:  
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        main.log.info(self.name+": Ping Response: "+ response )
        #if utilities.assert_matches(expect=',\s0\%\spacket\sloss',actual=response,onpass="No Packet loss",onfail="Host is not reachable"):
        if re.search(',\s0\%\spacket\sloss',response):
            main.log.info(self.name+": NO PACKET LOSS, HOST IS REACHABLE")
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
            #pattern = "inet\saddr:10.0.0.6"  
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
            return int(result.group('dpid'))
        else:
            main.log.error("Connection failed to the host")

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
            response = self.execute(cmd=command,prompt="mininet>",timeout=10)
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

    def get_sw_controller(self,sw):
        command = "sh ovs-vsctl get-controller "+str(sw)
        try:
            response = self.execute(cmd=command,prompt="mininet>",timeout=10)
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

    def disconnect(self):
        main.log.info(self.name+": Disconnecting mininet...")
        response = ''
        if self.handle:
            try:
                response = self.execute(cmd="exit",prompt="(.*)",timeout=120)
                response = self.execute(cmd="exit",prompt="(.*)",timeout=120)
            except pexpect.EOF:  
                main.log.error(self.name + ": EOF exception found")
                main.log.error(self.name + ":     " + self.handle.before)
                main.cleanup()
                main.exit()
        else :
            main.log.error(self.name+": Connection failed to the host")
            response = main.FALSE
        return response  

    def ctrl_none(self):
        #self.execute(cmd="sh ~/ONOS/scripts/test-ctrl-none.sh", prompt="mininet",timeout=20)
        self.handle.sendline()
        self.handle.expect(["mininet>",pexpect.EOF,pexpect.TIMEOUT])
        self.handle.sendline("sh ~/ONOS/scripts/test-ctrl-none.sh")
        self.handle.expect(["test-ctrl-none",pexpect.EOF,pexpect.TIMEOUT])
        self.handle.expect(["mininet>",pexpect.EOF,pexpect.TIMEOUT], 20)

    def ctrl_all(self):
        try:
            self.execute(cmd="sh ~/ONOS/scripts/test-ctrl-add-ext.sh", prompt="mininet",timeout=20)
        except pexpect.EOF:  
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()

    def ctrl_divide(self):
        try:
            self.execute(cmd="sh ~/ONOS/scripts/ctrl-divide.sh ", prompt="mininet",timeout=20)
        except pexpect.EOF:  
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()

    def ctrl_local(self):
        try:
            self.execute(cmd="sh ~/ONOS/scripts/test-ctrl-local.sh ", prompt="mininet",timeout=20)
        except pexpect.EOF:  
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()

    def ctrl_one(self, ip):
        try:
            self.execute(cmd="sh ~/ONOS/scripts/ctrl-one.sh "+ip, prompt="mininet",timeout=20)
        except pexpect.EOF:  
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
  
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

if __name__ != "__main__":
    import sys
    sys.modules[__name__] = MininetCliDriver()
