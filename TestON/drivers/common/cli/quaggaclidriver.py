#!/usr/bin/env python

import time
import pexpect
import struct, fcntl, os, sys, signal
import sys
import re
import json
sys.path.append("../")
from drivers.common.clidriver import CLI

class QuaggaCliDriver(CLI):

    def __init__(self):
        super(CLI, self).__init__()

    def connect(self, **connectargs):
        for key in connectargs:
            vars(self)[key] = connectargs[key]
        
        self.name = self.options['name']
        self.handle = super(QuaggaCliDriver,self).connect(user_name = self.user_name, ip_address = self.ip_address,port = self.port, pwd = self.pwd)

        if self.handle: 
            self.handle.expect("")
            self.handle.expect("\$")
            self.handle.sendline("telnet localhost 2605")
            self.handle.expect("Password:", timeout = 5)
            self.handle.sendline("hello")
            self.handle.expect("bgpd",timeout = 5)
            self.handle.sendline("enable")
            self.handle.expect("bgpd#", timeout = 5)
            return self.handle
        else :
            main.log.info("NO HANDLE")
            return main.FALSE

    def enter_config(self, asn):
        try:
            self.handle.sendline("")
            self.handle.expect("bgpd#")
        except:
            main.log.warn("Probably not currently in enable mode!")
            self.disconnect()
            return main.FALSE
        self.handle.sendline("configure terminal")
        self.handle.expect("config", timeout = 5)
        routerAS = "router bgp " + str(asn)
        try:
            self.handle.sendline(routerAS)
            self.handle.expect("config-router", timeout = 5)
            return main.TRUE
        except:
            return main.FALSE
    def add_route(self, net, numRoutes, routeRate):
        try:
            self.handle.sendline("")
            self.handle.expect("config-router")
        except:
            main.log.warn("Probably not in config-router mode!")
            self.disconnect()
        main.log.report("Adding Routes")
        j=0
        k=0
        while numRoutes > 255:
            numRoutes = numRoutes - 255
            j = j + 1
        k = numRoutes % 254
        routes_added = 0
        if numRoutes > 255:
            numRoutes = 255
        for m in range(1,j+1):
            for n in range(1, numRoutes+1):
                network = str(net) + "." + str(m) + "." + str(n) + ".0/24"
                routeCmd = "network " + network
                try:
                    self.handle.sendline(routeCmd)
                    self.handle.expect("bgpd")
                except:
                    main.log.warn("failed to add route")
                    self.disconnect() 
                waitTimer = 1.00/routeRate
                time.sleep(waitTimer)
                routes_added = routes_added + 1
        for d in range(j+1,j+2):
            for e in range(1,k+1):
                network = str(net) + "." + str(d) + "." + str(e) + ".0/24"
                routeCmd = "network " + network
                try:
                    self.handle.sendline(routeCmd)
                    self.handle.expect("bgpd")
                except:
                    main.log.warn("failed to add route")
                    self.disconnect
                waitTimer = 1.00/routeRate
                time.sleep(waitTimer)
                routes_added = routes_added + 1
        if routes_added == numRoutes:
            return main.TRUE
        return main.FALSE
    def del_route(self, net, numRoutes, routeRate):
        try:
            self.handle.sendline("")
            self.handle.expect("config-router")
        except:
            main.log.warn("Probably not in config-router mode!")
            self.disconnect()
        main.log.report("Deleting Routes")
        j=0
        k=0
        while numRoutes > 255:
            numRoutes = numRoutes - 255
            j = j + 1
        k = numRoutes % 254
        routes_deleted = 0
        if numRoutes > 255:
            numRoutes = 255
        for m in range(1,j+1):
            for n in range(1, numRoutes+1):
                network = str(net) + "." + str(m) + "." + str(n) + ".0/24"
                routeCmd = "no network " + network
                try:
                    self.handle.sendline(routeCmd)
                    self.handle.expect("bgpd")
                except:
                    main.log.warn("Failed to delete route")
                    self.disconnect()
                waitTimer = 1.00/routeRate
                time.sleep(waitTimer)
                routes_deleted = routes_deleted + 1
        for d in range(j+1,j+2):
            for e in range(1,k+1):
                network = str(net) + "." + str(d) + "." + str(e) + ".0/24"
                routeCmd = "no network " + network
                try:
                    self.handle.sendline(routeCmd)
                    self.handle.expect("bgpd")
                except:
                    main.log.warn("Failed to delete route")
                    self.disconnect()
                waitTimer = 1.00/routeRate
                time.sleep(waitTimer)
                routes_deleted = routes_deleted + 1
        if routes_deleted == numRoutes:
            return main.TRUE
        return main.FALSE
    def check_routes(self, brand, ip, user, pw):
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
            if brand == "pronto" or brand == "PRONTO":
                pronto(ip,user,passwd)
            #elif brand  == "cisco" or brand == "CISCO":
            #    cisco(ip,user,passwd) 
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
