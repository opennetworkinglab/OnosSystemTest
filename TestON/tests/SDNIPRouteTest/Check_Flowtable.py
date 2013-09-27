#!/usr/bin/env python

import os
import pexpect
import re
import time
import sys

def pronto(ip, user, passwd):
    print "Connecting to Pronto switch"
    child = pexpect.spawn("telnet " + ip)
    i = child.expect(["login:", "CLI#",pexpect.TIMEOUT])
    if i == 0:
        print "Username and password required. Passing login info."    
        child.sendline(user)
        child.expect("Password:")
        child.sendline(passwd)
        child.expect("CLI#")
    print "Logged in, getting flowtable."
    child.sendline("flowtable brief")
    for t in range (9): 
        t2 = 9 - t 
        print "\r" + str(t2)
        sys.stdout.write("\033[F")
        time.sleep(1)
    print "Scanning flowtable"
    child.expect("Flow table show")
    count = 0
    while 1:
        i = child.expect(['17\d\.\d{1,3}\.\d{1,3}\.\d{1,3}','CLI#',pexpect.TIMEOUT])
        if i == 0:
            count = count + 1
        elif i == 1:
            print "Pronto flows: " + str(count) + "\nDone\n"
            break
        else:
            break

def cisco(ip,user,passwd):
    print "Establishing Cisco switch connection"
    child = pexpect.spawn("ssh " +  user + "@" + ip)
    i = child.expect(["Password:", "CLI#",pexpect.TIMEOUT])
    if i == 0:
        print "Password required. Passing now."
        child.sendline(passwd)
        child.expect("#")
    print "Logged in. Retrieving flow table then counting flows."
    child.sendline("show openflow switch all flows all")
    child.expect("Logical Openflow Switch")
    print "Flow table retrieved. Counting flows"
    count = 0
    while 1:
        i = child.expect(["nw_src=17","#",pexpect.TIMEOUT])
        if i == 0:
            count = count + 1
        elif i == 1:
            print "Cisco flows: " + str(count) + "\nDone\n"
            break
        else: 
            break

if __name__ == "__main__":
    usage_msg = "<Switch brand> <IP> <Username> <Password>\n"
    usage_msg = usage_msg + "\nCurrently supported switches:\n"
    usage_msg = usage_msg + "Pronto | Cisco\n"
    usage_msg = usage_msg + "\nShorthand commands: \n"
    usage_msg = usage_msg + "SDNIP : Runs \"Pronto 10.128.0.63 admin admin\" and \"Cisco 10.128.0.30 admin onos_test\" \n"

    if len(sys.argv) == 2:
        if sys.argv[1].lower() == "sdnip":
            switch = sys.argv[1]
    elif len(sys.argv) < 5 or (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
        print(usage_msg)
        exit(0)
    else:
        switch = sys.argv[1]
        ip = sys.argv[2]
        user = sys.argv[3]
        passwd = sys.argv[4]

    if switch.lower() == "sdnip":
        pronto("10.128.0.63","admin","admin")
        cisco("10.128.0.30","admin","onos_test")
    elif switch.lower() == "pronto":
        pronto(ip,user,passwd)
    elif switch.lower() == "cisco":
        cisco(ip,user,passwd)
