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
from math import pow
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
            cmdString = "sudo mn " + self.options['arg1'] + " " + self.options['arg2'] +  " --mac --controller " + self.options['controller'] + " " + self.options['arg3']
            
            argList = self.options['arg1'].split(",")
            global topoArgList
            topoArgList = argList[0].split(" ")
            argList = map(int, argList[1:])
            topoArgList = topoArgList[1:] + argList
            
          #### for proactive flow with static ARP entries
            #cmdString = "sudo mn " + self.options['arg1'] + " " + self.options['arg2'] +  " --mac --arp --controller " + self.options['controller'] + " " + self.options['arg3']
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
                    
    def num_switches_n_links(self,topoType,depth,fanout):
        if topoType == 'tree':
            if fanout is None:     #In tree topology, if fanout arg is not given, by default it is 2
                fanout = 2
            k = 0
            count = 0
            while(k <= depth-1): 
                count = count + pow(fanout,k)
                k = k+1
                num_switches = count
            while(k <= depth-2): 
                '''depth-2 gives you only core links and not considering edge links as seen by ONOS
                    If all the links including edge links are required, do depth-1
                '''
                count = count + pow(fanout,k)
                k = k+1
            num_links = count * fanout
            #print "num_switches for %s(%d,%d) = %d and links=%d" %(topoType,depth,fanout,num_switches,num_links)
        
        elif topoType =='linear':
            if fanout is None:     #In linear topology, if fanout or num_hosts_per_sw is not given, by default it is 1
                fanout = 1
            num_switches = depth
            num_hosts_per_sw = fanout
            total_num_hosts = num_switches * num_hosts_per_sw
            num_links = total_num_hosts + (num_switches - 1)
            print "num_switches for %s(%d,%d) = %d and links=%d" %(topoType,depth,fanout,num_switches,num_links) 
        topoDict = {}
        topoDict = {"num_switches":int(num_switches), "num_corelinks":int(num_links)}
        return topoDict


    def calculate_sw_and_links(self):
        topoDict = self.num_switches_n_links(*topoArgList)
        return topoDict

    def pingall(self, timeout=300):
        '''
        Verifies the reachability of the hosts using pingall command.
        Optional parameter timeout allows you to specify how long to wait for pingall to complete
        Returns:
                main.TRUE if pingall completes with no pings dropped
                otherwise main.FALSE
        '''
        if self.handle :
            main.log.info(self.name+": Checking reachabilty to the hosts using pingall")
            try:
                response = self.execute(cmd="pingall",prompt="mininet>",timeout=int(timeout))
            except pexpect.EOF:
                main.log.error(self.name + ": EOF exception found")
                main.log.error(self.name + ":     " + self.handle.before)
                main.cleanup()
                main.exit()
            except pexpect.TIMEOUT:
                #We may not want to kill the test if pexpect times out
                main.log.error(self.name + ": TIMEOUT exception found")
                main.log.error(self.name + ":     " + str(self.handle.before) )
            #NOTE: mininet's pingall rounds, so we will check the number of passed and number of failed
            pattern = "Results\:\s0\%\sdropped\s\((?P<passed>[\d]+)/(?P=passed)"
            if re.search(pattern,response):
                main.log.info(self.name+": All hosts are reachable")
                return main.TRUE
            else:
                main.log.error(self.name+": Unable to reach all the hosts")
                main.log.info("Pingall ouput: " + str(response))
                #NOTE: Send ctrl-c to make sure pingall is done
                self.handle.send("\x03")
                self.handle.expect("Interrupt")
                self.handle.expect("mininet>")
                return main.FALSE
        else :
            main.log.error(self.name+": Connection failed to the host") 
            main.cleanup()
            main.exit()

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

    


    def changeIP(self,host,intf,newIP,newNetmask):
        '''
        Changes the ip address of a host on the fly
        Ex: h2 ifconfig h2-eth0 10.0.1.2 netmask 255.255.255.0
        '''
        if self.handle:
            try:
                cmd = host+" ifconfig "+intf+" "+newIP+" "+'netmask'+" "+newNetmask
                self.handle.sendline(cmd)
                self.handle.expect("mininet>")
                response = self.handle.before
                main.log.info("response = "+response)
                main.log.info("Ip of host "+host+" changed to new IP "+newIP)
                return main.TRUE
            except pexpect.EOF:
                main.log.error(self.name + ": EOF exception found")
                main.log.error(self.name + ":     " + self.handle.before)
                return main.FALSE

    def changeDefaultGateway(self,host,newGW):
        '''
        Changes the default gateway of a host
        Ex: h1 route add default gw 10.0.1.2
        '''
        if self.handle:
            try:
                cmd = host+" route add default gw "+newGW 
                self.handle.sendline(cmd)
                self.handle.expect("mininet>")
                response = self.handle.before
                main.log.info("response = "+response)
                main.log.info("Default gateway of host "+host+" changed to "+newGW)
                return main.TRUE
            except pexpect.EOF:
                main.log.error(self.name + ": EOF exception found")
                main.log.error(self.name + ":     " + self.handle.before)
                return main.FALSE
  
    def addStaticMACAddress(self,host,GW,macaddr):
        '''
        Changes the mac address of a geateway host
        '''
        if self.handle:
            try:
                #h1  arp -s 10.0.1.254 00:00:00:00:11:11 
                cmd = host+" arp -s "+GW+" "+macaddr
                self.handle.sendline(cmd)
                self.handle.expect("mininet>")
                response = self.handle.before
                main.log.info("response = "+response)
                main.log.info("Mac adrress of gateway "+GW+" changed to "+macaddr)
                return main.TRUE
            except pexpect.EOF:
                main.log.error(self.name + ": EOF exception found")
                main.log.error(self.name + ":     " + self.handle.before)
                return main.FALSE

    def verifyStaticGWandMAC(self,host):
        '''
        Verify if the static gateway and mac address assignment 
        '''
        if self.handle:
            try:
                #h1  arp -an
                cmd = host+" arp -an "
                self.handle.sendline(cmd)
                self.handle.expect("mininet>")
                response = self.handle.before
                main.log.info(host+" arp -an = "+response)
                return main.TRUE
            except pexpect.EOF:
                main.log.error(self.name + ": EOF exception found")
                main.log.error(self.name + ":     " + self.handle.before)
                return main.FALSE



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
            pattern = r'^(?P<dpid>\w)+'
            result = re.search(pattern, response, re.MULTILINE)
            if result is None:
                main.log.info("Couldn't find DPID for switch '', found: %s" % (switch, response))
                return main.FALSE
            return str(result.group(0)).lower()
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
            cmd = 'py "\\n".join(["name=%s,mac=%s,ip=%s,enabled=%s" % (i.name, i.MAC(), i.IP(), i.isUp())'
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
    '''
    def iperf(self,host1,host2):
        main.log.info(self.name+": Simple iperf TCP test between two (optionally specified) hosts")
        try:
            if not host1 and not host2:
                response = self.execute(cmd = 'iperf',prompt = 'mininet>',timeout = 10)
            else:
                cmd1 = 'iperf '+ host1 + " " + host2
                response = self.execute(cmd = cmd1, prompt = '>',timeout = 20)
        except pexpect.EOF:  
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
        return response
     '''
    def iperf(self,host1,host2):
        main.log.info(self.name+": Simple iperf TCP test between two hosts")
        try:
            cmd1 = 'iperf '+ host1 + " " + host2
            self.handle.sendline(cmd1)
            self.handle.expect("mininet>") 
            response = self.handle.before
            if re.search('Results:',response):
                main.log.info(self.name+": iperf test succssful")
                return main.TRUE
            else:
                main.log.error(self.name+": iperf test failed")
                return main.FALSE 
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()
    
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
        args = utilities.parse_args(["END1","END2","OPTION"],**linkargs)
        end1 = args["END1"] if args["END1"] != None else ""
        end2 = args["END2"] if args["END2"] != None else ""
        option = args["OPTION"] if args["OPTION"] != None else ""
        main.log.info("Bring link between '"+ end1 +"' and '" + end2 + "' '" + option + "'")
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

    def get_sw_controller(self, sw):
        '''
        Parameters:
            sw: The name of an OVS switch. Example "s1"
        Return:
            The output of the command from the mininet cli or main.FALSE on timeout
        '''
        command = "sh ovs-vsctl get-controller "+str(sw)
        try:
            response = self.execute(cmd=command, prompt="mininet>", timeout=10)
            if response:
                return response
            else:
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()

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

    def add_switch( self, sw, **kwargs ):
        '''
        adds a switch to the mininet topology
        NOTE: this uses a custom mn function
        NOTE: cannot currently specify what type of switch
        required params:
            switchname = name of the new switch as a string
        optional keyvalues:
            dpid = "dpid"
        returns: main.FASLE on an error, else main.TRUE
        '''
        dpid = kwargs.get('dpid', '')
        command = "addswitch " + str( sw ) + " " + str( dpid )
        try:
            response = self.execute(cmd=command,prompt="mininet>",timeout=10)
            if re.search("already exists!", response):
                main.log.warn(response)
                return main.FALSE
            elif re.search("Error", response):
                main.log.warn(response)
                return main.FALSE
            elif re.search("usage:", response):
                main.log.warn(response)
                return main.FALSE
            else:
                return main.TRUE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()

    def del_switch( self, sw ):
        '''
        delete a switch from the mininet topology
        NOTE: this uses a custom mn function
        required params:
            switchname = name of the switch as a string
        returns: main.FASLE on an error, else main.TRUE
        '''
        command = "delswitch " + str( sw )
        try:
            response = self.execute(cmd=command,prompt="mininet>",timeout=10)
            if re.search("no switch named", response):
                main.log.warn(response)
                return main.FALSE
            elif re.search("Error", response):
                main.log.warn(response)
                return main.FALSE
            elif re.search("usage:", response):
                main.log.warn(response)
                return main.FALSE
            else:
                return main.TRUE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()

    def add_link( self, node1, node2 ):
        '''
        add a link to the mininet topology
        NOTE: this uses a custom mn function
        NOTE: cannot currently specify what type of link
        required params:
            node1 = the string node name of the first endpoint of the link
            node2 = the string node name of the second endpoint of the link
        returns: main.FASLE on an error, else main.TRUE
        '''
        command = "addlink " + str( node1 ) + " " + str( node2 )
        try:
            response = self.execute(cmd=command,prompt="mininet>",timeout=10)
            if re.search("doesnt exist!", response):
                main.log.warn(response)
                return main.FALSE
            elif re.search("Error", response):
                main.log.warn(response)
                return main.FALSE
            elif re.search("usage:", response):
                main.log.warn(response)
                return main.FALSE
            else:
                return main.TRUE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()

    def del_link( self, node1, node2 ):
        '''
        delete a link from the mininet topology
        NOTE: this uses a custom mn function
        required params:
            node1 = the string node name of the first endpoint of the link
            node2 = the string node name of the second endpoint of the link
        returns: main.FASLE on an error, else main.TRUE
        '''
        command = "dellink " + str( node1 ) + " " + str( node2 )
        try:
            response = self.execute(cmd=command,prompt="mininet>",timeout=10)
            if re.search("no node named", response):
                main.log.warn(response)
                return main.FALSE
            elif re.search("Error", response):
                main.log.warn(response)
                return main.FALSE
            elif re.search("usage:", response):
                main.log.warn(response)
                return main.FALSE
            else:
                return main.TRUE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()

    def add_host( self, hostname, **kwargs ):
        '''
        Add a host to the mininet topology
        NOTE: this uses a custom mn function
        NOTE: cannot currently specify what type of host
        required params:
            hostname = the string hostname
        optional key-value params
            switch = "switch name"
            returns: main.FASLE on an error, else main.TRUE
        '''
        switch = kwargs.get('switch', '')
        command = "addhost " + str( hostname ) + " " + str( switch )
        try:
            response = self.execute(cmd=command,prompt="mininet>",timeout=10)
            if re.search("already exists!", response):
                main.log.warn(response)
                return main.FALSE
            elif re.search("doesnt exists!", response):
                main.log.warn(response)
                return main.FALSE
            elif re.search("Error", response):
                main.log.warn(response)
                return main.FALSE
            elif re.search("usage:", response):
                main.log.warn(response)
                return main.FALSE
            else:
                return main.TRUE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()

    def del_host( self, hostname ):
        '''
        delete a host from the mininet topology
        NOTE: this uses a custom mn function
        required params:
            hostname = the string hostname
            returns: main.FASLE on an error, else main.TRUE
        '''
        command = "delhost " + str( hostname )
        try:
            response = self.execute(cmd=command,prompt="mininet>",timeout=10)
            if re.search("no host named", response):
                main.log.warn(response)
                return main.FALSE
            elif re.search("Error", response):
                main.log.warn(response)
                return main.FALSE
            elif re.search("usage:", response):
                main.log.warn(response)
                return main.FALSE
            else:
                return main.TRUE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()

    def disconnect(self):
        main.log.info(self.name+": Disconnecting mininet...")
        response = ''
        if self.handle:
            try:
                response = self.execute(cmd="exit",prompt="(.*)",timeout=120)
                response = self.execute(cmd="exit",prompt="(.*)",timeout=120)
                self.handle.sendline("sudo mn -c")
                response = main.TRUE
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
            i=self.handle.expect(['No\ssuch\device','listening\son',pexpect.TIMEOUT,"mininet>"],timeout=10)
            main.log.warn(self.handle.before + self.handle.after)
            self.handle.sendline("")
            self.handle.expect("mininet>")
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
            self.handle.expect("mininet>")
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

    def compare_switches(self, topo, switches_json):
        '''
        Compare mn and onos switches
        topo: sts TestONTopology object
        switches_json: parsed json object from the onos devices api

        This uses the sts TestONTopology object

        '''
        import json
        #main.log.debug("Switches_json string: ", switches_json)
        output = {"switches":[]}
        for switch in topo.graph.switches: #iterate through the MN topology and pull out switches and and port info
            ports = []
            for port in switch.ports.values():
                ports.append({'of_port': port.port_no, 'mac': str(port.hw_addr).replace('\'',''), 'name': port.name})
            output['switches'].append({"name": switch.name, "dpid": str(switch.dpid).zfill(16), "ports": ports })

        #print "mn"
        #print json.dumps(output, sort_keys=True,indent=4,separators=(',', ': '))
        #print "onos"
        #print json.dumps(switches_json, sort_keys=True,indent=4,separators=(',', ': '))


        # created sorted list of dpid's in MN and ONOS for comparison
        mnDPIDs=[]
        for switch in output['switches']:
            mnDPIDs.append(switch['dpid'].lower())
        mnDPIDs.sort()
        #print "List of Mininet switch DPID's"
        #print mnDPIDs
        if switches_json == "":#if rest call fails
            main.log.error(self.name + ".compare_switches(): Empty JSON object given from ONOS")
            return main.FALSE
        onos=switches_json
        onosDPIDs=[]
        for switch in onos:
            if switch['available'] == True:
                onosDPIDs.append(switch['id'].replace(":",'').replace("of",'').lower())
            #else:
                #print "Switch is unavailable:"
                #print switch
        onosDPIDs.sort()
        #print "List of ONOS switch DPID's"
        #print onosDPIDs

        if mnDPIDs!=onosDPIDs:
            switch_results = main.FALSE
            main.log.report( "Switches in MN but not in ONOS:")
            main.log.report( str([switch for switch in mnDPIDs if switch not in onosDPIDs]))
            main.log.report( "Switches in ONOS but not in MN:")
            main.log.report(  str([switch for switch in onosDPIDs if switch not in mnDPIDs]))
        else:#list of dpid's match in onos and mn
            #main.log.report("DEBUG: The dpid's of the switches in Mininet and ONOS match")
            switch_results = main.TRUE
        return switch_results



    def compare_ports(self, topo, ports_json):
        '''
        Compare mn and onos ports
        topo: sts TestONTopology object
        ports_json: parsed json object from the onos ports api

        Dependencies: 
            1. This uses the sts TestONTopology object
            2. numpy - "sudo pip install numpy"

        '''
        #FIXME: this does not look for extra ports in ONOS, only checks that ONOS has what is in MN
        import json
        from numpy import uint64
        ports_results = main.TRUE
        output = {"switches":[]}
        for switch in topo.graph.switches: #iterate through the MN topology and pull out switches and and port info
            ports = []
            for port in switch.ports.values():
                #print port.hw_addr.toStr(separator = '')
                tmp_port = {}
                tmp_port['of_port'] = port.port_no
                tmp_port['mac'] = str(port.hw_addr).replace('\'','')
                tmp_port['name'] = port.name
                tmp_port['enabled'] = port.enabled

                ports.append(tmp_port)
            tmp_switch = {}
            tmp_switch['name'] = switch.name
            tmp_switch['dpid'] = str(switch.dpid).zfill(16)
            tmp_switch['ports'] = ports

            output['switches'].append(tmp_switch)


        ################ports#############
        for mn_switch in output['switches']:
            mn_ports = []
            onos_ports = []
            switch_result = main.TRUE
            for port in mn_switch['ports']:
                if port['enabled'] == True:
                    mn_ports.append(port['of_port'])
                #else: #DEBUG only 
                #    main.log.warn("Port %s on switch %s is down" % ( str(port['of_port']) , str(mn_switch['name'])) )
            for onos_switch in ports_json:
                #print "Iterating through a new switch as seen by ONOS"
                #print onos_switch
                if onos_switch['device']['available'] == True:
                    if onos_switch['device']['id'].replace(':','').replace("of", '') == mn_switch['dpid']:
                        for port in onos_switch['ports']:
                            if port['isEnabled']:
                                #print "Iterating through available ports on the switch"
                                #print port
                                if port['port'] == 'local':
                                    #onos_ports.append('local')
                                    onos_ports.append(long(uint64(-2)))
                                else:
                                    onos_ports.append(int(port['port']))
                                    '''
                                else: #This is likely a new reserved port implemented
                                    main.log.error("unkown port '" + str(port['port']) )
                                    '''
                           #else: #DEBUG
                           #    main.log.warn("Port %s on switch %s is down" % ( str(port['port']) , str(onos_switch['device']['id'])) )
                        break
            mn_ports.sort(key=float)
            onos_ports.sort(key=float)
            #print "\nPorts for Switch %s:" % (mn_switch['name'])
            #print "\tmn_ports[] = ", mn_ports
            #print "\tonos_ports[] = ", onos_ports
            mn_ports_log = mn_ports
            onos_ports_log = onos_ports
            mn_ports = [x for x in mn_ports]
            onos_ports = [x for x in onos_ports]

            #TODO: handle other reserved port numbers besides LOCAL
            #NOTE: Reserved ports
            #   Local port: -2 in Openflow, ONOS shows 'local', we store as long(uint64(-2))
            for mn_port in mn_ports_log:
                if mn_port in onos_ports:
                    #don't set results to true here as this is just one of many checks and it might override a failure
                    mn_ports.remove(mn_port)
                    onos_ports.remove(mn_port)
                #NOTE: OVS reports this as down since there is no link
                #      So ignoring these for now
                #TODO: Come up with a better way of handling these
                if 65534 in mn_ports:
                    mn_ports.remove(65534)
                if long(uint64(-2)) in onos_ports:
                    onos_ports.remove( long(uint64(-2))  )
            if len(mn_ports):  #the ports of this switch don't match
                switch_result = main.FALSE
                main.log.warn("Ports in MN but not ONOS: " + str(mn_ports) )
            if len(onos_ports):  #the ports of this switch don't match
                switch_result = main.FALSE
                main.log.warn("Ports in ONOS but not MN: " + str(onos_ports) )
            if switch_result == main.FALSE:
                main.log.report("The list of ports for switch %s(%s) does not match:" % (mn_switch['name'], mn_switch['dpid']) )
                main.log.warn("mn_ports[]  =  " + str(mn_ports_log))
                main.log.warn("onos_ports[] = " + str(onos_ports_log))
            ports_results = ports_results and switch_result
        return ports_results




    def compare_links(self, topo, links_json):
        '''
        Compare mn and onos links
        topo: sts TestONTopology object
        links_json: parsed json object from the onos links api

        This uses the sts TestONTopology object

        '''
        #FIXME: this does not look for extra links in ONOS, only checks that ONOS has what is in MN
        import json
        link_results = main.TRUE
        output = {"switches":[]}
        onos = links_json
        for switch in topo.graph.switches: #iterate through the MN topology and pull out switches and and port info
            # print "Iterating though switches as seen by Mininet"
            # print switch
            ports = []
            for port in switch.ports.values():
                #print port.hw_addr.toStr(separator = '')
                ports.append({'of_port': port.port_no, 'mac': str(port.hw_addr).replace('\'',''), 'name': port.name})
            output['switches'].append({"name": switch.name, "dpid": str(switch.dpid).zfill(16), "ports": ports })
        #######Links########

        mn_links = [link for link in topo.patch_panel.network_links if (link.port1.enabled and link.port2.enabled)]
        #print "mn_links:"
        #print mn_links
        if 2*len(mn_links) == len(onos):
            link_results = main.TRUE
        else:
            link_results = main.FALSE
            main.log.report("Mininet has %i bidirectional links and ONOS has %i unidirectional links" % (len(mn_links), len(onos) ))


        # iterate through MN links and check if an ONOS link exists in both directions
        # NOTE: Will currently only show mn links as down if they are cut through STS. 
        #       We can either do everything through STS or wait for up_network_links 
        #       and down_network_links to be fully implemented.
        for link in mn_links: 
            #print "Link: %s" % link
            #TODO: Find a more efficient search method
            node1 = None
            port1 = None
            node2 = None
            port2 = None
            first_dir = main.FALSE
            second_dir = main.FALSE
            for switch in output['switches']:
                #print "Switch: %s" % switch['name']
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


            for onos_link in onos:
                onos_node1 = onos_link['src']['device'].replace(":",'').replace("of", '')
                onos_node2 = onos_link['dst']['device'].replace(":",'').replace("of", '')
                onos_port1 = onos_link['src']['port']
                onos_port2 = onos_link['dst']['port']

                #print "Checking ONOS for link %s/%s -> %s/%s and" % (node1, port1, node2, port2)
                #print "Checking ONOS for link %s/%s -> %s/%s" % (node2, port2, node1, port1)
                # check onos link from node1 to node2
                if str(onos_node1) == str(node1) and str(onos_node2) == str(node2):
                    if int(onos_port1) == int(port1) and int(onos_port2) == int(port2):
                        first_dir = main.TRUE
                    else:
                        main.log.warn('The port numbers do not match for ' +str(link) +\
                                ' between ONOS and MN. When cheking ONOS for link '+\
                                '%s/%s -> %s/%s' % (node1, port1, node2, port2)+\
                                ' ONOS has the values %s/%s -> %s/%s' %\
                                (onos_node1, onos_port1, onos_node2, onos_port2))

                # check onos link from node2 to node1
                elif ( str(onos_node1) == str(node2) and str(onos_node2) == str(node1) ):
                    if ( int(onos_port1) == int(port2) and int(onos_port2) == int(port1) ):
                        second_dir = main.TRUE
                    else:
                        main.log.warn('The port numbers do not match for ' +str(link) +\
                                ' between ONOS and MN. When cheking ONOS for link '+\
                                '%s/%s -> %s/%s' % (node2, port2, node1, port1)+\
                                ' ONOS has the values %s/%s -> %s/%s' %\
                                (onos_node2, onos_port2, onos_node1, onos_port1))
                else:#this is not the link you're looking for
                    pass
            if not first_dir:
                main.log.report('ONOS does not have the link %s/%s -> %s/%s' % (node1, port1, node2, port2))
            if not second_dir:
                main.log.report('ONOS does not have the link %s/%s -> %s/%s' % (node2, port2, node1, port1))
            link_results = link_results and first_dir and second_dir
        return link_results


    def get_hosts(self):
        '''
        Returns a list of all hosts
        Don't ask questions just use it
        '''
        self.handle.sendline("")
        self.handle.expect("mininet>")
        
        self.handle.sendline("py [ host.name for host in net.hosts ]")
        self.handle.expect("mininet>")

        handle_py = self.handle.before
        handle_py = handle_py.split("]\r\n",1)[1]
        handle_py = handle_py.rstrip()

        self.handle.sendline("")
        self.handle.expect("mininet>")

        host_str = handle_py.replace("]", "")
        host_str = host_str.replace("'", "")
        host_str = host_str.replace("[", "")
        host_list = host_str.split(",")

        return host_list 


    def update(self):
        '''
        updates the port address and status information for each port in mn
        '''
        #TODO: Add error checking. currently the mininet command has no output
        main.log.info("Updateing MN port information")
        try:
            self.handle.sendline("")
            self.handle.expect("mininet>")

            self.handle.sendline("update")
            self.handle.expect("update")
            self.handle.expect("mininet>")

            self.handle.sendline("")
            self.handle.expect("mininet>")

            return main.TRUE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()

if __name__ != "__main__":
    import sys
    sys.modules[__name__] = MininetCliDriver()

