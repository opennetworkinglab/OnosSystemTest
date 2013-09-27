'''
Driver for blank dataplane VMs. Created for SDNIP test. 
'''

import time
import pexpect
import struct, fcntl, os, sys, signal
import sys
import re
import json
sys.path.append("../")
from drivers.common.clidriver import CLI

class DPCliDriver(CLI):

    def __init__(self):
        super(CLI, self).__init__()

    def connect(self,**connectargs):
        for key in connectargs:
           vars(self)[key] = connectargs[key]


        self.name = self.options['name']
        self.handle = super(DPCliDriver,self).connect(user_name = self.user_name, ip_address = self.ip_address,port = self.port, pwd = self.pwd)

        if self.handle:
            return self.handle
        else :
            main.log.info("NO HANDLE")
            return main.FALSE

    def create_interfaces(self, net, number, start, destlogin, dest):
        self.handle.sendline("")
        self.handle.expect("\$")

        self.handle.sendline("rm /tmp/local_ip.txt")
        self.handle.expect("\$")
        self.handle.sendline("touch /tmp/local_ip.txt")
        self.handle.expect("\$")

        main.log.info("Creating interfaces")
        k = 0
        intf = 0
        while number != 0:
            k= k + 1
            if k == 256:
                k = 1
                start = start + 1
            number = number - 1
            intf = intf + 1
            ip = net+"."+str(start)+"."+str(k)+".1"
            self.handle.sendline("sudo ifconfig eth0:"+str(intf)+" "+ip+" netmask 255.255.255.0")

            i = self.handle.expect(["\$","password",pexpect.TIMEOUT,pexpect.EOF], timeout = 120)
                if i == 0:
                    self.handle.sendline("echo "+str(ip)+"\n >> /tmp/local_ip.txt")
                    self.handle.expect("\$")
                elif i == 1:
                    main.log.info("Sending sudo password")
                    self.handle.sendline(self.pwd) 
                    self.handle.expect("\$")
                else:
                    main.log.error("INTERFACES NOT CREATED")
                    return main.FALSE
        self.handle.sendline("scp /tmp/local_ip.txt "+str(destlogin)+"@"+str(destip)+":/tmp/ip_table"+str(net)+".txt")
        try:
            self.handle.expect("100%")
            return main.TRUE
        except:
            self.log.warn("FAILURE SENDING IP TABLE TO DESTINATION MACHINE")
            return main.FALSE

    '''
    def remove_interfaces(self, number, start):
        self.handle.sendline("")
        self.handle.expect("\$")

        main.log.info("Deleting interfaces")
        while number != 0:
            number = number - 1
            intf = intf + 1
            self.handle.sendline("sudo ifconfig eth0:"+str(intf)+" down")

        i = self.handle.expect(["\$","password",pexpect.TIMEOUT,pexpect.EOF], timeout = 120)
            if i == 0:
                 main.log.info("Interfaces deleted")
                 return main.TRUE
            elif i == 1:
                main.log.info("Sending sudo password")
                self.handle.sendline(self.pwd)
                self.handle.expect("DONE")
                main.log.info("Interfaces deleted")
                return main.TRUE
            else:
                main.log.error("INTERFACES NOT DELETED")
                return main.FALSE
    '''

    def pingall_interfaces(self, netsrc, netstrt, netdst):
        self.handle.sendline("")
        self.handle.expect("\$")
       
        main.log.info("Pinging interfaces on the "+str(netdst)+" network from "+str(netsrc)+"."+str(netstrt)+".1.1") 
        self.handle.sendline("sudo fping -S "+str(netsrc)+"."+str(netstrt)+".1.1 -f /tmp/ip_table"+str(netdst)+".txt")
        while 1:
            i = self.handle.expect(["reachable","unreachable","\$","password",pexpect.TIMEOUT,"not installed"], timeout=45)
            if i == 0:
                result = main.TRUE
            elif i == 1:
                main.log.error("An interface was unreachable")
                result = main.FALSE
                return result
            elif i == 2:
                main.log.info("All interfaces reachable")
                return result
            elif i == 3:
                self.handle.sendline(self.pwd)
            elif i == 4:
                main.log.error("Unable to fping")
                result = main.FALSE
                return result
            elif i == 5:
                main.log.info("fping not installed, installing fping")
                self.handle.sendline("sudo apt-get install fping")
                i = self.handle.expect(["password","\$",pexpect.TIMEOUT], timeout = 60)
                if i == 0:
                    self.handle.sendline(self.pwd)
                    self.handle.expect("\$", timeout = 30)
                    main.log.info("fping installed")
                    self.handle.sendline("sudo fping -S "+str(netsrc)+"."+str(netstrt)+".1.1 -f /tmp/ip_table"+str(netdst)+".txt")
                elif i == 1:
                    main.log.info("fping installed")
                    self.handle.sendline("sudo fping -S "+str(netsrc)+"."+str(netstrt)+".1.1 -f /tmp/ip_table"+str(netdst)+".txt")
                elif i == 2:
                    main.log.error("Could not install fping")
                    result = main.FALSE
                    return result

    def disconnect(self):
        response = ''
        try:
            self.handle.sendline("exit")
            self.handle.expect("closed")
        except:
            main.log.error("Connection failed to the host")
            response = main.FALSE
        return response

