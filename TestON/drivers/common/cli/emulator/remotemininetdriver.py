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
from time import time

class RemoteMininetDriver(Emulator):
    '''
    RemoteMininetCliDriver is the basic driver which will handle the Mininet functions
    The main different between this and the MininetCliDriver is that this one does not build the mininet. 
    It assumes that there is already a mininet running on the target. 
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
        self.handle = super(RemoteMininetDriver, self).connect(user_name = self.user_name, ip_address = self.ip_address,port = None, pwd = self.pwd)
        
        self.ssh_handle = self.handle
        
        # Copying the readme file to process the 
        if self.handle :
            return main.TRUE

        else :
            main.log.error("Connection failed to the host "+self.user_name+"@"+self.ip_address) 
            main.log.error("Failed to connect to the Mininet")
            return main.FALSE

#*********************************************************************************************
#*********************************************************************************************
# checkForLoss will determine if any of the pings had any packets lost during the course of 
# the pingLong.
#*********************************************************************************************
#*********************************************************************************************

    def checkForLoss(self, pingList):
        '''
        Returns main.FALSE for 0% packet loss and
        Returns main.ERROR if "found multiple mininet" is found and
        Returns main.TRUE else
        '''
        import os
        self.handle.sendline("")
        self.handle.expect("\$")
        self.handle.sendline("cat " + pingList)
        self.handle.expect(pingList)
        self.handle.expect("\$")
        outputs = self.handle.before + self.handle.after
        if re.search(" 0% packet loss",outputs):
            return main.FALSE
        elif re.search("found multiple mininet",outputs):
            return main.ERROR
        return main.TRUE


    def pingLong(self,**pingParams):
        '''
        Starts a continuous ping on the mininet host outputing to a file in the /tmp dir. 
        '''
        self.handle.sendline("")
        self.handle.expect("\$")
        args = utilities.parse_args(["SRC","TARGET","PINGTIME"],**pingParams)
        precmd = "sudo rm /tmp/ping." + args["SRC"]
        self.execute(cmd=precmd,prompt="(.*)",timeout=10)
        command = "sudo mininet/util/m " + args["SRC"] + " ping "+args ["TARGET"]+" -i .2 -w " + str(args['PINGTIME']) + " > /tmp/ping." + args["SRC"] + " &"
        main.log.info( command ) 
        self.execute(cmd=command,prompt="(.*)",timeout=10)
        self.handle.sendline("")
        self.handle.expect("\$")
        return main.TRUE

    def pingstatus(self,**pingParams):
        '''
        Tails the respective ping output file and check that there is a moving "64 bytes"
        '''
        self.handle.sendline("")
        self.handle.expect("\$")
        args = utilities.parse_args(["SRC"],**pingParams)
        self.handle.sendline("tail /tmp/ping." + args["SRC"])
        self.handle.expect("tail")
        self.handle.expect("\$")
        result = self.handle.before + self.handle.after
        self.handle.sendline("")
        self.handle.expect("\$")
        if re.search('Unreachable', result ):
            main.log.info("Unreachable found in ping logs...") 
            return main.FALSE
        elif re.search('64\sbytes', result): 
            main.log.info("Pings look good") 
            return main.TRUE
        else: 
            main.log.info("No, or faulty ping data...") 
            return main.FALSE
         
    def pingKill(self, testONUser, testONIP):
        '''
        Kills all continuous ping processes.
        Then copies all the ping files to the TestStation.
        '''
        import time
        self.handle.sendline("")
        self.handle.expect("\$")
        command = "sudo kill -SIGINT `pgrep ping`" 
        main.log.info( command ) 
        self.execute(cmd=command,prompt="(.*)",timeout=10)
        #Commenting out in case TestON and MN are on the same machine. scp overrights the file anyways
        #main.log.info( "Removing old ping data" )
        #command = "rm /tmp/ping.*"
        #os.popen(command) 
        #time.sleep(2)      
        main.log.info( "Transferring ping files to TestStation" )
        command = "scp /tmp/ping.* "+ str(testONUser) + "@" + str(testONIP) + ":/tmp/" 
        self.execute(cmd=command,prompt="100%",timeout=20)
        self.handle.sendline("")
        self.handle.expect("\$")
        return main.TRUE
    
    def pingLongKill(self):
        import time
        self.handle.sendline("")
        self.handle.expect("\$")
        command = "sudo kill -SIGING `pgrep ping`"
        main.log.info(command)
        self.execute(cmd=command,prompt="(.*)",timeout=10)
        self.handle.sendline("")
        self.handle.expect("\$")
        return main.TRUE
        
    def pingHost(self,**pingParams):
        ''' 
        Pings between two hosts on remote mininet  
        ''' 
        self.handle.sendline("")
        self.handle.expect("\$")
        args = utilities.parse_args(["SRC","TARGET"],**pingParams)
        command = "mininet/util/m " + args["SRC"] + " ping "+args ["TARGET"]+" -c 4 -W 1 -i .2"
        main.log.info ( command ) 
        response = self.execute(cmd=command,prompt="rtt",timeout=10 )
        self.handle.sendline("")
        self.handle.expect("\$")
        if utilities.assert_matches(expect=',\s0\%\spacket\sloss',actual=response,onpass="No Packet loss",onfail="Host is not reachable"):
            main.log.info("NO PACKET LOSS, HOST IS REACHABLE")
            main.last_result = main.TRUE 
            return main.TRUE
        else :
            main.log.error("PACKET LOST, HOST IS NOT REACHABLE")
            main.last_result = main.FALSE
            return main.FALSE
        
    
    def checknum(self,num):
        '''
        Verifies the correct number of switches are running 
        '''
        if self.handle :
            self.handle.sendline("")
            self.handle.expect("\$")
            self.handle.sendline('ifconfig -a | grep "sw.. " | wc -l')
            self.handle.expect("wc")
            self.handle.expect("\$")
            response = self.handle.before
            self.handle.sendline('ps -ef | grep "bash -ms mininet:sw" | grep -v color | wc -l') 
            self.handle.expect("color")
            self.handle.expect("\$")
            response2 = self.handle.before

            if re.search(num, response):
                if re.search(num, response2):
                    return main.TRUE
                else:
                    return main.FALSE
            else:
                return main.FALSE
        else :
            main.log.error("Connection failed to the host") 

    def ctrl_none(self):
        '''
        Sets all the switches to no controllers. 
        '''
        self.execute(cmd="~/ONOS/scripts/test-ctrl-none.sh", prompt="\$",timeout=10)

    def ctrl_one(self, ip):
        '''
        Sets all the switches to point to the supplied IP
        '''
        self.execute(cmd="~/ONOS/scripts/test-ctrl-one.sh "+ip, prompt="\$",timeout=10)
 
    def ctrl_local(self):
        '''
        Sets all the switches to point to the Controller on the same machine that they are running on. 
        '''
        self.execute(cmd="~/ONOS/scripts/test-ctrl-local.sh ", prompt="\$",timeout=10)

 #   def verifySSH(self,**connectargs):
 #       response = self.execute(cmd="h1 /usr/sbin/sshd -D&",prompt="mininet>",timeout=10)
 #       response = self.execute(cmd="h4 /usr/sbin/sshd -D&",prompt="mininet>",timeout=10)
 #       for key in connectargs:
 #           vars(self)[key] = connectargs[key]
 #       response = self.execute(cmd="xterm h1 h4 ",prompt="mininet>",timeout=10)
 #       import time
 #       time.sleep(20)
 #       if self.flag == 0:
 #           self.flag = 1
 #           return main.FALSE
 #       else :
 #           return main.TRUE
 #   
 #   def getMacAddress(self,host):
 #       '''
 #           Verifies the host's ip configured or not.
 #       '''
 #       if self.handle :
 #           response = self.execute(cmd=host+" ifconfig",prompt="mininet>",timeout=10)

 #           pattern = "HWaddr\s(((\d|\w)+:)+(\d|\w))"
 #           mac_address_search = re.search(pattern, response)
 #           main.log.info("Mac-Address of Host "+host +" is "+mac_address_search.group(1))
 #           return mac_address_search.group(1)
 #       else :
 #           main.log.error("Connection failed to the host") 
 #   def getIPAddress(self,host):
 #       '''
 #           Verifies the host's ip configured or not.
 #       '''
 #       if self.handle :
 #           response = self.execute(cmd=host+" ifconfig",prompt="mininet>",timeout=10)

 #           pattern = "inet\saddr:(\d+\.\d+\.\d+\.\d+)"
 #           ip_address_search = re.search(pattern, response)
 #           main.log.info("IP-Address of Host "+host +" is "+ip_address_search.group(1))
 #           return ip_address_search.group(1)
 #       else :
 #           main.log.error("Connection failed to the host") 
 #       
 #   def dump(self):
 #       main.log.info("Dump node info")
 #       self.execute(cmd = 'dump',prompt = 'mininet>',timeout = 10)
 #       return main.TRUE
 #           
 #   def intfs(self):
 #       main.log.info("List interfaces")
 #       self.execute(cmd = 'intfs',prompt = 'mininet>',timeout = 10)
 #       return main.TRUE
 #   
 #   def net(self):
 #       main.log.info("List network connections")
 #       self.execute(cmd = 'net',prompt = 'mininet>',timeout = 10)
 #       return main.TRUE
 #   
 #   def iperf(self):
 #       main.log.info("Simple iperf TCP test between two (optionally specified) hosts")
 #       self.execute(cmd = 'iperf',prompt = 'mininet>',timeout = 10)
 #       return main.TRUE
 #   
 #   def iperfudp(self):
 #       main.log.info("Simple iperf TCP test between two (optionally specified) hosts")
 #       self.execute(cmd = 'iperfudp',prompt = 'mininet>',timeout = 10)
 #       return main.TRUE
 #   
 #   def nodes(self):
 #       main.log.info("List all nodes.")
 #       self.execute(cmd = 'nodes',prompt = 'mininet>',timeout = 10)    
 #       return main.TRUE
 #   
 #   def pingpair(self):
 #       main.log.infoe("Ping between first two hosts")
 #       self.execute(cmd = 'pingpair',prompt = 'mininet>',timeout = 20)
 #       
 #       if utilities.assert_matches(expect='0% packet loss',actual=response,onpass="No Packet loss",onfail="Hosts not reachable"):
 #           main.log.info("Ping between two hosts SUCCESS")
 #           main.last_result = main.TRUE 
 #           return main.TRUE
 #       else :
 #           main.log.error("PACKET LOST, HOSTS NOT REACHABLE")
 #           main.last_result = main.FALSE
 #           return main.FALSE
 #   
 #   def link(self,**linkargs):
 #       '''
 #       Bring link(s) between two nodes up or down
 #       '''
 #       main.log.info('Bring link(s) between two nodes up or down')
 #       args = utilities.parse_args(["END1","END2","OPTION"],**linkargs)
 #       end1 = args["END1"] if args["END1"] != None else ""
 #       end2 = args["END2"] if args["END2"] != None else ""
 #       option = args["OPTION"] if args["OPTION"] != None else ""
 #       command = "link "+str(end1) + " " + str(end2)+ " " + str(option)
 #       response = self.execute(cmd=command,prompt="mininet>",timeout=10)
 #       return main.TRUE
 #       

 #   def dpctl(self,**dpctlargs):
 #       '''
 #        Run dpctl command on all switches.
 #       '''
 #       main.log.info('Run dpctl command on all switches')
 #       args = utilities.parse_args(["CMD","ARGS"],**dpctlargs)
 #       cmd = args["CMD"] if args["CMD"] != None else ""
 #       cmdargs = args["ARGS"] if args["ARGS"] != None else ""
 #       command = "dpctl "+cmd + " " + str(cmdargs)
 #       response = self.execute(cmd=command,prompt="mininet>",timeout=10)
 #       return main.TRUE
 #  
 #       
 #   def get_version(self):
 #       file_input = path+'/lib/Mininet/INSTALL'
 #       version = super(Mininet, self).get_version()
 #       pattern = 'Mininet\s\w\.\w\.\w\w*'
 #       for line in open(file_input,'r').readlines():
 #           result = re.match(pattern, line)
 #           if result:
 #               version = result.group(0)
 #               
 #           
 #       return version    
    def start_tcpdump(self, filename, intf = "eth0", port = "port 6633"):
        ''' 
        Runs tpdump on an intferface and saves the file
        intf can be specified, or the default eth0 is used
        '''
        try:
            self.handle.sendline("")
            self.handle.sendline("sudo tcpdump -n -i "+ intf + " " + port + " -w " + filename.strip() + "  &")
            self.handle.sendline("")
            self.handle.sendline("")
            i=self.handle.expect(['No\ssuch\device','listening\son',pexpect.TIMEOUT,"\$"],timeout=10)
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
            self.handle.sendline("sudo pkill tcpdump")
            self.handle.sendline("")
            self.handle.sendline("")
            self.handle.expect("\$")
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

    def del_switch(self,sw):
        self.handle.sendline("")
        self.handle.expect("\$")
        self.handle.sendline("sudo ovs-vsctl del-br "+sw)
        self.handle.expect("\$")
        return main.TRUE

    def add_switch(self,sw):
        self.handle.sendline("")
        self.handle.expect("\$")
        self.handle.sendline("sudo ovs-vsctl add-br "+sw)
        self.handle.expect("\$")
        self.handle.sendline("sudo ovs-vsctl add-port "+sw+" " + sw + "-eth1")
        self.handle.expect("\$")
        self.handle.sendline("sudo ovs-vsctl add-port "+sw+" " + sw + "-eth2")
        self.handle.expect("\$")
        self.handle.sendline("sudo ovs-vsctl add-port "+sw+" " + sw + "-eth3")
        self.handle.expect("\$")
        self.handle.sendline("sudo ovs-vsctl add-port "+sw+" " + sw + "-eth4")
        self.handle.expect("\$")
        self.handle.sendline("sudo ovs-vsctl add-port "+sw+" " + sw + "-eth5")
        self.handle.expect("\$")
        self.handle.sendline("sudo ovs-vsctl add-port "+sw+" " + sw + "-eth6")
        self.handle.expect("\$")
        self.handle.sendline("sudo ovs-vsctl add-port "+sw+" " + sw + "-eth7")
        self.handle.expect("\$")
        self.handle.sendline("sudo ovs-vsctl add-port "+sw+" " + sw + "-eth8")
        self.handle.expect("\$")
        self.handle.sendline("sudo ovs-vsctl add-port "+sw+" " + sw + "-eth9")
        self.handle.expect("\$")
        self.handle.sendline("sudo ovs-vsctl add-port "+sw+" " + sw + "-eth10")
        self.handle.expect("\$")
        self.handle.sendline("sudo ovs-vsctl add-port "+sw+" " + sw + "-eth11")
        self.handle.expect("\$")
        self.handle.sendline("sudo ovs-vsctl add-port "+sw+" " + sw + "-eth12")
        self.handle.expect("\$")
        self.handle.sendline("sudo ovs-vsctl add-port "+sw+" " + sw + "-eth13")
        self.handle.expect("\$")
        self.handle.sendline("sudo ovs-vsctl add-port "+sw+" " + sw + "-eth14")
        self.handle.expect("\$")


    def disconnect(self):
        '''    
        Called at the end of the test to disconnect the handle.    
        '''    
        response = ''
        #print "Disconnecting Mininet"
        if self.handle:
            self.handle.sendline("exit") 
            self.handle.expect("exit")
            self.handle.expect("(.*)")
            response = self.handle.before

        else :
            main.log.error("Connection failed to the host")
            response = main.FALSE
        return response  

    def get_flowTable(self,sw):
        self.handle.sendline("cd")
        self.handle.expect(["\$",pexpect.EOF,pexpect.TIMEOUT])
        #TODO: Write seperate versions of the function for this, possibly a string that tells it which switch is in use?
        #For 1.0 version of OVS
        #command = "sudo ovs-ofctl dump-flows " + sw + " | awk '{OFS=\",\" ; print $1 $6 $7 }' |sort -n -k1"
        #for 1.3 version of OVS
        command = "sudo ovs-ofctl dump-flows " + sw + " | awk '{OFS=\",\" ; print $1 $3 $7 $8}' |sort -n -k1"
        self.handle.sendline(command)
        self.handle.expect(["sort -n -k1",pexpect.EOF,pexpect.TIMEOUT])
        self.handle.expect(["NXST_FLOW",pexpect.EOF,pexpect.TIMEOUT])
        response = self.handle.before
        return response 
        

    def flow_comp(self,flow1,flow2):
        if flow1==flow2:
            return main.TRUE
        else:
            main.log.info("Flow tables do not match, printing tables:")
            main.log.info("Flow Table 1:")
            main.log.info(flow1)
            main.log.info("Flow Table 2:")
            main.log.info(flow2)
            return main.FALSE

if __name__ != "__main__":
    import sys
    sys.modules[__name__] = RemoteMininetDriver()
