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
        #,user_name, ip_address, pwd,options):
        # Here the main is the TestON instance after creating all the log handles.
        for key in connectargs:
            vars(self)[key] = connectargs[key]       
        
        self.name = self.options['name']
        self.handle = super(MininetCliDriver, self).connect(user_name = self.user_name, ip_address = self.ip_address,port = None, pwd = self.pwd)
        
        self.ssh_handle = self.handle
        
        # Copying the readme file to process the 
        if self.handle :
            #self.handle.logfile = sys.stdout
            main.log.info("Clearing any residual state or processes")
            self.handle.sendline("sudo mn -c")

            i=self.handle.expect(['password\sfor\sadmin','Cleanup\scomplete',pexpect.EOF,pexpect.TIMEOUT],60)
            if i==0:
                main.log.info("sending sudo password")
                self.handle.sendline('onos_test')
                i=self.handle.expect(['admin:','\$',pexpect.EOF,pexpect.TIMEOUT],60)
            if i==1:
                main.log.info("Clean")

            elif i==2:
                main.log.error("Connection timeout")
            elif i==3: #timeout
                main.log.error("Something while cleaning MN took too long... " )
 
            #cmdString = "sudo mn --topo "+self.options['topo']+","+self.options['topocount']+" --mac --switch "+self.options['switch']+" --controller "+self.options['controller']
            #cmdString = "sudo mn --custom ~/mininet/custom/topo-2sw-2host.py --controller remote --ip 192.168.56.102 --port 6633 --topo mytopo"
            main.log.info("building fresh mininet") 

            #### for reactive/PARP enabled tests
            cmdString = "sudo mn " + self.options['arg1'] + " " + self.options['arg2'] +  " --mac --controller " + self.options['controller']
            #### for proactive flow with static ARP entries
            #cmdString = "sudo mn " + self.options['arg1'] + " " + self.options['arg2'] +  " --mac --arp --controller " + self.options['controller']
            #resultCommand = self.execute(cmd=cmdString,prompt='mininet>',timeout=120)
            self.handle.sendline(cmdString)
            self.handle.expect("sudo mn")
            while 1: 
                i=self.handle.expect(['mininet>','\*\*\*','Exception',pexpect.EOF,pexpect.TIMEOUT],300)
                if i==0:
                    main.log.info("mininet built") 
                    return main.TRUE
                if i==1:
                    self.handle.expect("\n")
                    main.log.info(self.handle.before)
                elif i==2:
                    main.log.error("Launching mininet failed...")
                    return main.FALSE
                elif i==3:
                    main.log.error("Connection timeout")
                    return main.FALSE
                elif i==4: #timeout
                    main.log.error("Something took too long... " )
                    return main.FALSE

            #if utilities.assert_matches(expect=patterns,actual=resultCommand,onpass="Network is being launched",onfail="Network launching is being failed "):
            return main.TRUE
            #else:
            #    return main.FALSE

        else :
            main.log.error("Connection failed to the host "+self.user_name+"@"+self.ip_address) 
            main.log.error("Failed to connect to the Mininet")
            return main.FALSE
                       
    def pingall(self):
        '''
           Verifies the reachability of the hosts using pingall command.
        '''
        if self.handle :
            main.log.info("Checking reachabilty to the hosts using pingall")
            response = self.execute(cmd="pingall",prompt="mininet>",timeout=10)
            pattern = 'Results\:\s0\%\sdropped\s\(0\/\d+\slost\)\s*$'
            if utilities.assert_matches(expect=pattern,actual=response,onpass="All hosts are reaching",onfail="Unable to reach all the hosts"):
                return main.TRUE
            else:
                return main.FALSE
        else :
            main.log.error("Connection failed to the host") 
            return main.FALSE

    def fpingHost(self,**pingParams):
        ''' 
        Uses the fping package for faster pinging...
        *requires fping to be installed on machine running mininet 
        ''' 
        args = utilities.parse_args(["SRC","TARGET"],**pingParams)
        command = args["SRC"] + " fping -i 100 -t 20 -C 1 -q "+args["TARGET"]
        self.handle.sendline(command) 
        self.handle.expect(args["TARGET"]) 
        self.handle.expect("mininet")
        response = self.handle.before 
        if re.search(":\s-" ,response):
            main.log.info("Ping fail") 
            return main.FALSE
        elif re.search(":\s\d{1,2}\.\d\d", response):
            main.log.info("Ping good!")
            return main.TRUE
        main.log.info("Install fping on mininet machine... ") 
        main.log.info("\n---\n"+response)
        return main.FALSE
        
    def pingHost(self,**pingParams):
        
        args = utilities.parse_args(["SRC","TARGET"],**pingParams)
        #command = args["SRC"] + " ping -" + args["CONTROLLER"] + " " +args ["TARGET"]
        command = args["SRC"] + " ping "+args ["TARGET"]+" -c 1 -i .2"
        response = self.execute(cmd=command,prompt="mininet",timeout=10 )
        if utilities.assert_matches(expect=',\s0\%\spacket\sloss',actual=response,onpass="No Packet loss",onfail="Host is not reachable"):
            main.log.info("NO PACKET LOSS, HOST IS REACHABLE")
            main.last_result = main.TRUE 
            return main.TRUE
        else :
            main.log.error("PACKET LOST, HOST IS NOT REACHABLE")
            main.last_result = main.FALSE
            return main.FALSE
        
    
    def checkIP(self,host):
        '''
            Verifies the host's ip configured or not.
        '''
        if self.handle :
            response = self.execute(cmd=host+" ifconfig",prompt="mininet>",timeout=10)

            pattern = "inet\s(addr|Mask):([0-1]{1}[0-9]{1,2}|2[0-4][0-9]|25[0-5]|[0-9]{1,2}).([0-1]{1}[0-9]{1,2}|2[0-4][0-9]|25[0-5]|[0-9]{1,2}).([0-1]{1}[0-9]{1,2}|2[0-4][0-9]|25[0-5]|[0-9]{1,2}).([0-1]{1}[0-9]{1,2}|2[0-4][0-9]|25[0-5]|[0-9]{1,2})"
            #pattern = "inet\saddr:10.0.0.6"  
            if utilities.assert_matches(expect=pattern,actual=response,onpass="Host Ip configured properly",onfail="Host IP not found") :
                return main.TRUE
            else:
                return main.FALSE
        else :
            main.log.error("Connection failed to the host") 
            
    def verifySSH(self,**connectargs):
        response = self.execute(cmd="h1 /usr/sbin/sshd -D&",prompt="mininet>",timeout=10)
        response = self.execute(cmd="h4 /usr/sbin/sshd -D&",prompt="mininet>",timeout=10)
        for key in connectargs:
            vars(self)[key] = connectargs[key]
        response = self.execute(cmd="xterm h1 h4 ",prompt="mininet>",timeout=10)
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
            response = self.execute(cmd=host+" ifconfig",prompt="mininet>",timeout=10)

            pattern = "HWaddr\s(((\d|\w)+:)+(\d|\w))"
            mac_address_search = re.search(pattern, response)
            main.log.info("Mac-Address of Host "+host +" is "+mac_address_search.group(1))
            return mac_address_search.group(1)
        else :
            main.log.error("Connection failed to the host") 
    def getIPAddress(self,host):
        '''
            Verifies the host's ip configured or not.
        '''
        if self.handle :
            response = self.execute(cmd=host+" ifconfig",prompt="mininet>",timeout=10)

            pattern = "inet\saddr:(\d+\.\d+\.\d+\.\d+)"
            ip_address_search = re.search(pattern, response)
            main.log.info("IP-Address of Host "+host +" is "+ip_address_search.group(1))
            return ip_address_search.group(1)
        else :
            main.log.error("Connection failed to the host") 
        
    def dump(self):
        main.log.info("Dump node info")
        self.execute(cmd = 'dump',prompt = 'mininet>',timeout = 10)
        return main.TRUE
            
    def intfs(self):
        main.log.info("List interfaces")
        self.execute(cmd = 'intfs',prompt = 'mininet>',timeout = 10)
        return main.TRUE
    
    def net(self):
        main.log.info("List network connections")
        self.execute(cmd = 'net',prompt = 'mininet>',timeout = 10)
        return main.TRUE
    
    def iperf(self):
        main.log.info("Simple iperf TCP test between two (optionally specified) hosts")
        self.execute(cmd = 'iperf',prompt = 'mininet>',timeout = 10)
        return main.TRUE
    
    def iperfudp(self):
        main.log.info("Simple iperf TCP test between two (optionally specified) hosts")
        self.execute(cmd = 'iperfudp',prompt = 'mininet>',timeout = 10)
        return main.TRUE
    
    def nodes(self):
        main.log.info("List all nodes.")
        self.execute(cmd = 'nodes',prompt = 'mininet>',timeout = 10)    
        return main.TRUE
    
    def pingpair(self):
        main.log.infoe("Ping between first two hosts")
        self.execute(cmd = 'pingpair',prompt = 'mininet>',timeout = 20)
        
        if utilities.assert_matches(expect='0% packet loss',actual=response,onpass="No Packet loss",onfail="Hosts not reachable"):
            main.log.info("Ping between two hosts SUCCESS")
            main.last_result = main.TRUE 
            return main.TRUE
        else :
            main.log.error("PACKET LOST, HOSTS NOT REACHABLE")
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
        response = self.execute(cmd=command,prompt="mininet>",timeout=10)
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
	response = self.execute(cmd=command,prompt="mininet>",timeout=10)
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
        response = self.execute(cmd=command,prompt="mininet>",timeout=10)
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
        response = self.execute(cmd=command,prompt="mininet>",timeout=10)
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
        main.log.info(self.execute(cmd=command,prompt="mininet>",timeout=10))

    def assign_sw_controller(self,**kwargs):
        args = utilities.parse_args(["SW","IP1","PORT1","IP2","PORT2","IP3","PORT3","IP4","PORT4","IP5","PORT5","IP6","PORT6","IP7","PORT7","IP8","PORT8"],**kwargs)
        sw = args["SW"] if args["SW"] != None else ""
        ip1 = args["IP1"] if args["IP1"] != None else ""
        ip2 = args["IP2"] if args["IP2"] != None else ""
        ip3 = args["IP3"] if args["IP3"] != None else ""
        ip4 = args["IP4"] if args["IP4"] != None else ""
        ip5 = args["IP5"] if args["IP5"] != None else ""
        ip6 = args["IP6"] if args["IP6"] != None else ""
        ip7 = args["IP7"] if args["IP7"] != None else ""
        ip8 = args["IP8"] if args["IP8"] != None else ""
       # master = args["MASTER"] if args["MASTER"] != None else ""
        port1 = args["PORT1"] if args["PORT1"] != None else ""
        port2 = args["PORT2"] if args["PORT2"] != None else ""
        port3 = args["PORT3"] if args["PORT3"] != None else ""
        port4 = args["PORT4"] if args["PORT4"] != None else ""
        port5 = args["PORT5"] if args["PORT5"] != None else ""
        port6 = args["PORT6"] if args["PORT6"] != None else ""
        port7 = args["PORT7"] if args["PORT7"] != None else ""
        port8 = args["PORT8"] if args["PORT8"] != None else ""
        ptcpA = int(args["PORT1"])+int(sw) if args["PORT1"] != None else ""
        ptcpB = "ptcp:"+str(ptcpA) if ip1 != "" else ""
        tcp1 = "tcp:"+str(ip1)+":"+str(port1) if ip1 != "" else ""
        tcp2 = "tcp:"+str(ip2)+":"+str(port2) if ip2 != "" else ""
        tcp3 = "tcp:"+str(ip3)+":"+str(port3) if ip3 != "" else ""
        tcp4 = "tcp:"+str(ip4)+":"+str(port4) if ip4 != "" else ""
        tcp5 = "tcp:"+str(ip5)+":"+str(port5) if ip5 != "" else ""
        tcp6 = "tcp:"+str(ip6)+":"+str(port6) if ip6 != "" else ""
        tcp7 = "tcp:"+str(ip7)+":"+str(port7) if ip7 != "" else ""
        tcp8 = "tcp:"+str(ip8)+":"+str(port8) if ip8 != "" else ""
       # master1 = tcp1+" role master " if args["MASTER"] == 1 else ""
       # master2 = tcp2+" role master " if args["MASTER"] == 2 else ""
       # master3 = tcp3+" role master " if args["MASTER"] == 3 else ""
       # master4 = tcp4+" role master " if args["MASTER"] == 4 else ""
        command = "sh ovs-vsctl set-controller s"+str(sw)+" "+ptcpB+" "+tcp1+" "+tcp2+" "+tcp3+" "+tcp4+" "+tcp5+" "+tcp6+" "+tcp7+" "+tcp8
        self.execute(cmd=command,prompt="mininet>",timeout=5)

    def disconnect(self):
        main.log.info("Disconnecting mininet...")
        response = ''
        if self.handle:
            response = self.execute(cmd="exit",prompt="(.*)",timeout=120)
            response = self.execute(cmd="exit",prompt="(.*)",timeout=120)

        else :
            main.log.error("Connection failed to the host")
            response = main.FALSE
        return response  

    def ctrl_none(self):
        #self.execute(cmd="sh ~/ONOS/scripts/test-ctrl-none.sh", prompt="mininet",timeout=20)
        self.handle.sendline()
        self.handle.expect("mininet>")
        self.handle.sendline("sh ~/ONOS/scripts/test-ctrl-none.sh")
        self.handle.expect("test-ctrl-none")
        self.handle.expect("mininet>", 20)

    def ctrl_all(self):
        self.execute(cmd="sh ~/ONOS/scripts/test-ctrl-add-ext.sh", prompt="mininet",timeout=20)
  
    def ctrl_divide(self):
        self.execute(cmd="sh ~/ONOS/scripts/ctrl-divide.sh ", prompt="mininet",timeout=20)

    def ctrl_local(self):
        self.execute(cmd="sh ~/ONOS/scripts/test-ctrl-local.sh ", prompt="mininet",timeout=20)

    def ctrl_one(self, ip):
        self.execute(cmd="sh ~/ONOS/scripts/ctrl-one.sh "+ip, prompt="mininet",timeout=20)
  
    def arping(self, src, dest, destmac):
        self.handle.sendline('')
        self.handle.expect("mininet")

        self.handle.sendline(src + ' arping ' + dest)
        try:
            self.handle.expect(destmac)
            main.log.info("ARP successful")
            self.handle.expect("mininet")
            return main.TRUE
        except:
            main.log.warn("ARP FAILURE")
            self.handle.expect("mininet")
            return main.FALSE

    def decToHex(num):
        return hex(num).split('x')[1]

if __name__ != "__main__":
    import sys
    sys.modules[__name__] = MininetCliDriver()
