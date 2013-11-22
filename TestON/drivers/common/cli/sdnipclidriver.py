import time
import pexpect
import struct, fcntl, os, sys, signal
import sys
import re
import json
sys.path.append("../")
from drivers.common.clidriver import CLI


class SDNIPCliDriver(CLI):

    def __init__(self):
        super(CLI, self).__init__()

    def connect(self, **connectargs):
        for key in connectargs:
            vars(self)[key] = connectargs[key]

        self.name = self.options['name']
        self.handle = super(SDNIPCliDriver,self).connect(user_name = self.user_name, ip_address = self.ip_address,port = self.port, pwd = self.pwd)

        if self.handle:
            return self.handle
        else :
            main.log.info("NO HANDLE")
            return main.FALSE
    
    def check_routes(self, brand, ip, user, pw):
        self.handle.sendline("")
        self.handle.expect("\$")    
        main.log.info("Connecting to Pronto switch")
        child = pexpect.spawn("telnet " + ip)
        i = child.expect(["login:", "CLI#",pexpect.TIMEOUT])
        if i == 0:
            main.log.info("Username and password required. Passing login info.")
            child.sendline(user)
            child.expect("Password:")
            child.sendline(pw)
            child.expect("CLI#")
        main.log.info("Logged in, getting flowtable.")
        child.sendline("flowtable brief")
        for t in range (9):
            t2 = 9 - t
            main.log.info("\r" + str(t2))
            sys.stdout.write("\033[F")
            time.sleep(1)
        time.sleep(10)
        main.log.info("Scanning flowtable")
        child.expect("Flow table show")
        count = 0
        while 1:
            i = child.expect(['17\d\.\d{1,3}\.\d{1,3}\.\d{1,3}','CLI#',pexpect.TIMEOUT])
            if i == 0:
                count = count + 1
            elif i == 1:
                a ="Pronto flows: " + str(count) + "\nDone\n"
                main.log.info(a)
                break
            else:
                break
        return count
    def disconnect(self):
        '''
        Called when Test is complete to disconnect the Quagga handle.  
        '''
        response = ''
        try:
            self.handle.close()
        except:
            main.log.error("Connection failed to the host")
            response = main.FALSE
        return response
