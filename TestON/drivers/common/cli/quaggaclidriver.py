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

    # TODO: simplify this method
    def connect(self, **connectargs):
        for key in connectargs:
            vars(self)[key] = connectargs[key]

        self.name = self.options['name']
        # self.handle = super(QuaggaCliDriver,self).connect(user_name = self.user_name, ip_address = self.ip_address,port = self.port, pwd = self.pwd)
        self.handle = super(QuaggaCliDriver, self).connect(user_name=self.user_name, ip_address="1.1.1.1", port=self.port, pwd=self.pwd)
        main.log.info("quagga handle" + str(self.handle) )
        main.log.info("where is this timeout from?")
        main.log.info("connect parameters:" + str(self.user_name) + ";" + str(self.ip_address) + ";" + str(self.port) + ";" + str(self.pwd))

        if self.handle:
            #self.handle.expect("",timeout=10)
            #self.handle.expect("\$",timeout=10)
            #main.log.info(self.handle.before)
            #main.log.info(self.handle.after)
            self.handle.sendline("telnet localhost 2605")
            #self.handle.expect("Password:", timeout=5)
            self.handle.expect("Password:")
            main.log.info("TEST1")
            self.handle.sendline("hello")
            #self.handle.expect("bgpd", timeout=5)
            self.handle.expect("bgpd")
            main.log.info("TEST2")
            self.handle.sendline("enable")
            #self.handle.expect("bgpd#", timeout=5)
            self.handle.expect("bgpd#")
            main.log.info("TEST3")
            return self.handle
        else :
            main.log.info("NO HANDLE")
            return main.FALSE

    def loginQuagga(self, ip_address):
        self.name = self.options['name']
        self.handle = super(QuaggaCliDriver, self).connect(
            user_name=self.user_name, ip_address=ip_address,
            port=self.port, pwd=self.pwd)
        main.log.info("connect parameters:" + str(self.user_name) + ";"
        + str(self.ip_address) + ";" + str(self.port) + ";" + str(self.pwd))

        if self.handle:
            #self.handle.expect("")
            #self.handle.expect("\$")
            self.handle.sendline("telnet localhost 2605")
            self.handle.expect("Password:", timeout=5)
            self.handle.sendline("hello")
            self.handle.expect("bgpd", timeout=5)
            self.handle.sendline("enable")
            self.handle.expect("bgpd#", timeout=5)
            main.log.info("I in quagga on host " + str(ip_address))

            return self.handle
        else:
            main.log.info("NO HANDLE")
            return main.FALSE

    def enter_config(self, asn):
        main.log.info("I am in enter_config method!")
        try:
            self.handle.sendline("")
            self.handle.expect("bgpd#")
        except:
            main.log.warn("Probably not currently in enable mode!")
            self.disconnect()
            return main.FALSE
        self.handle.sendline("configure terminal")
        self.handle.expect("config", timeout=5)
        routerAS = "router bgp " + str(asn)
        try:
            self.handle.sendline(routerAS)
            self.handle.expect("config-router", timeout=5)
            return main.TRUE
        except:
            return main.FALSE

    def generate_prefixes(self, net, numRoutes):
        main.log.info("I am in generate_prefixes method!")

        # each IP prefix will be composed by "net" + "." + m + "." + n + "." + x
        # the length of each IP prefix is 24
        routes = []
        routes_gen = 0
        m = numRoutes / 256
        n = numRoutes % 256

        for i in range(0, m):
            for j in range(0, 256):
                network = str(net) + "." + str(i) + "." + str(j) + ".0/24"
                routes.append(network)
                routes_gen = routes_gen + 1

        for j in range(0, n):
            network = str(net) + "." + str(m) + "." + str(j) + ".0/24"
            routes.append(network)
            routes_gen = routes_gen + 1

        if routes_gen == numRoutes:
            main.log.info("Successfully generated " + str(numRoutes)
            + " prefixes!")
            return routes
        return main.FALSE

    # This method generates a multiple to single point intent(MultiPointToSinglePointIntent) for a given route
    def generate_expected_singleRouteIntent(self, prefix, nextHop, nextHopMac, sdnip_data):

        ingress = []
        egress = ""
        for peer in sdnip_data['bgpPeers']:
            if peer['ipAddress'] == nextHop:
                egress = "of:" + str(peer['attachmentDpid']).replace(":", "") + ":" + str(peer['attachmentPort'])
            else:
                ingress.append("of:" + str(peer['attachmentDpid']).replace(":", "") + ":" + str(peer['attachmentPort']))

        selector = "ETH_TYPE{ethType=800},IPV4_DST{ip=" + prefix + "}"
        treatment = "[ETH_DST{mac=" + str(nextHopMac) + "}]"

        intent = egress + "/" + str(sorted(ingress)) + "/" + selector + "/" + treatment
        return intent

    def generate_expected_onePeerRouteIntents(self, prefixes, nextHop, nextHopMac, sdnip_json_file_path):
        intents = []
        sdnip_json_file = open(sdnip_json_file_path).read()

        sdnip_data = json.loads(sdnip_json_file)

        for prefix in prefixes:
            intents.append(self.generate_expected_singleRouteIntent(prefix, nextHop, nextHopMac, sdnip_data))
        return sorted(intents)

    # TODO
    # This method generates all expected route intents for all BGP peers
    def generate_expected_routeIntents(self):
        intents = []
        return intents

    # This method extracts all actual routes from ONOS CLI
    def extract_actual_routes(self, get_routes_result):
        routes_json_obj = json.loads(get_routes_result)

        allRoutes_actual = []
        for route in routes_json_obj:
            if route['prefix'] == '172.16.10.0/24':
                continue
            allRoutes_actual.append(route['prefix'] + "/" + route['nextHop'])

        return sorted(allRoutes_actual)

    # This method extracts all actual route intents from ONOS CLI
    def extract_actual_routeIntents(self, get_intents_result):
        intents = []
        # TODO: delete the line below when change to Mininet demo script
        # get_intents_result=open("../tests/SdnIpTest/intents.json").read()
        intents_json_obj = json.loads(get_intents_result)

        for intent in intents_json_obj:
            if intent['appId'] != "org.onlab.onos.sdnip" :
                continue
            if intent['type'] == "MultiPointToSinglePointIntent" and intent['state'] == 'INSTALLED':
                egress = str(intent['egress']['device']) + ":" + str(intent['egress']['port'])
                ingress = []
                for attachmentPoint in intent['ingress']:
                    ingress.append(str(attachmentPoint['device']) + ":" + str(attachmentPoint['port']))

                selector = intent['selector'].replace("[" , "").replace("]" , "").replace(" ", "")
                if str(selector).startswith("IPV4"):
                    str1, str2 = str(selector).split(",")
                    selector = str2 + "," + str1

                intent = egress + "/" + str(sorted(ingress)) + "/" + selector + "/" + intent['treatment']
                intents.append(intent)
        return sorted(intents)

    # This method extracts all actual BGP intents from ONOS CLI
    def extract_actual_bgpIntents(self, get_intents_result):
        intents = []
        # TODO: delete the line below when change to Mininet demo script
        # get_intents_result=open("../tests/SdnIpTest/intents.json").read()
        intents_json_obj = json.loads(get_intents_result)

        for intent in intents_json_obj:
            if intent['appId'] != "org.onlab.onos.sdnip":
                continue
            if intent['type'] == "PointToPointIntent" and "protocol=6" in str(intent['selector']):
                ingress = str(intent['ingress']['device']) + ":" + str(intent['ingress']['port'])
                egress = str(intent['egress']['device']) + ":" + str(intent['egress']['port'])
                selector = str(intent['selector']).replace(" ", "").replace("[", "").replace("]", "").split(",")
                intent = ingress + "/" + egress + "/" + str(sorted(selector))
                intents.append(intent)

        return sorted(intents)

    # This method generates a single point to single point intent(PointToPointIntent) for BGP path
    def generate_expected_bgpIntents(self, sdnip_json_file_path):
        from operator import eq

        sdnip_json_file = open(sdnip_json_file_path).read()
        sdnip_data = json.loads(sdnip_json_file)

        intents = []
        bgpPeerAttachmentPoint = ""
        bgpSpeakerAttachmentPoint = "of:" + str(sdnip_data['bgpSpeakers'][0]['attachmentDpid']).replace(":", "") + ":" + str(sdnip_data['bgpSpeakers'][0]['attachmentPort'])
        for peer in sdnip_data['bgpPeers']:
            bgpPeerAttachmentPoint = "of:" + str(peer['attachmentDpid']).replace(":", "") + ":" + str(peer['attachmentPort'])
            # find out the BGP speaker IP address for this BGP peer
            bgpSpeakerIpAddress = ""
            for interfaceAddress in sdnip_data['bgpSpeakers'][0]['interfaceAddresses']:
                # if eq(interfaceAddress['interfaceDpid'],sdnip_data['bgpSpeakers'][0]['attachmentDpid']) and eq(interfaceAddress['interfacePort'], sdnip_data['bgpSpeakers'][0]['attachmentPort']):
                if eq(interfaceAddress['interfaceDpid'], peer['attachmentDpid']) and eq(interfaceAddress['interfacePort'], peer['attachmentPort']):
                    bgpSpeakerIpAddress = interfaceAddress['ipAddress']
                    break
                else:
                    continue

            # from bgpSpeakerAttachmentPoint to bgpPeerAttachmentPoint direction
            selector_str = "IPV4_SRC{ip=" + bgpSpeakerIpAddress + "/32}," + "IPV4_DST{ip=" + peer['ipAddress'] + "/32}," + "IP_PROTO{protocol=6}, ETH_TYPE{ethType=800}, TCP_DST{tcpPort=179}"
            selector = selector_str.replace(" ", "").replace("[", "").replace("]", "").split(",")
            intent = bgpSpeakerAttachmentPoint + "/" + bgpPeerAttachmentPoint + "/" + str(sorted(selector))
            intents.append(intent)

            selector_str = "IPV4_SRC{ip=" + bgpSpeakerIpAddress + "/32}," + "IPV4_DST{ip=" + peer['ipAddress'] + "/32}," + "IP_PROTO{protocol=6}, ETH_TYPE{ethType=800}, TCP_SRC{tcpPort=179}"
            selector = selector_str.replace(" ", "").replace("[", "").replace("]", "").split(",")
            intent = bgpSpeakerAttachmentPoint + "/" + bgpPeerAttachmentPoint + "/" + str(sorted(selector))
            intents.append(intent)

            # from bgpPeerAttachmentPoint to bgpSpeakerAttachmentPoint direction
            selector_str = "IPV4_SRC{ip=" + peer['ipAddress'] + "/32}," + "IPV4_DST{ip=" + bgpSpeakerIpAddress + "/32}," + "IP_PROTO{protocol=6}, ETH_TYPE{ethType=800}, TCP_DST{tcpPort=179}"
            selector = selector_str.replace(" ", "").replace("[", "").replace("]", "").split(",")
            intent = bgpPeerAttachmentPoint + "/" + bgpSpeakerAttachmentPoint + "/" + str(sorted(selector))
            intents.append(intent)

            selector_str = "IPV4_SRC{ip=" + peer['ipAddress'] + "/32}," + "IPV4_DST{ip=" + bgpSpeakerIpAddress + "/32}," + "IP_PROTO{protocol=6}, ETH_TYPE{ethType=800}, TCP_SRC{tcpPort=179}"
            selector = selector_str.replace(" ", "").replace("[", "").replace("]", "").split(",")
            intent = bgpPeerAttachmentPoint + "/" + bgpSpeakerAttachmentPoint + "/" + str(sorted(selector))
            intents.append(intent)

        return sorted(intents)

    def add_routes(self, routes, routeRate):
        main.log.info("I am in add_routes method!")

        routes_added = 0
        try:
            self.handle.sendline("")
            # self.handle.expect("config-router")
            self.handle.expect("config-router", timeout=5)
        except:
            main.log.warn("Probably not in config-router mode!")
            self.disconnect()
        main.log.info("Start to add routes")

        for i in range(0, len(routes)):
            routeCmd = "network " + routes[i]
            try:
                self.handle.sendline(routeCmd)
                self.handle.expect("bgpd", timeout=5)
            except:
                main.log.warn("Failed to add route")
                self.disconnect()
            waitTimer = 1.00 / routeRate
            time.sleep(waitTimer)
        if routes_added == len(routes):
            main.log.info("Finished adding routes")
            return main.TRUE
        return main.FALSE

    def delete_routes(self, routes, routeRate):
        main.log.info("I am in delete_routes method!")

        routes_added = 0
        try:
            self.handle.sendline("")
            # self.handle.expect("config-router")
            self.handle.expect("config-router", timeout=5)
        except:
            main.log.warn("Probably not in config-router mode!")
            self.disconnect()
        main.log.info("Start to delete routes")

        for i in range(0, len(routes)):
            routeCmd = "no network " + routes[i]
            try:
                self.handle.sendline(routeCmd)
                self.handle.expect("bgpd", timeout=5)
            except:
                main.log.warn("Failed to add route")
                self.disconnect()
            waitTimer = 1.00 / routeRate
            time.sleep(waitTimer)
        if routes_added == len(routes):
            main.log.info("Finished deleting routes")
            return main.TRUE
        return main.FALSE

    def ping_test(self, ip_address, ping_test_file, ping_test_result_file):
        main.log.info("Start the ping test on host:" + str(ip_address))

        self.name = self.options['name']
        self.handle = super(QuaggaCliDriver, self).connect(
            user_name=self.user_name, ip_address=ip_address,
            port=self.port, pwd=self.pwd)
        main.log.info("connect parameters:" + str(self.user_name) + ";"
        + str(self.ip_address) + ";" + str(self.port) + ";" + str(self.pwd))

        if self.handle:
            self.handle.expect("")
            self.handle.expect("\$")
            main.log.info("I in host " + str(ip_address))
            main.log.info(ping_test_file + " > " + ping_test_result_file + " &")
            self.handle.sendline(ping_test_file + " > " + ping_test_result_file + " &")
            self.handle.expect("\$", timeout=60)
            handle = self.handle.before

            return handle
        else:
            main.log.info("NO HANDLE")
            return main.FALSE


    # Please use the generate_routes plus add_routes instead of this one
    def add_route(self, net, numRoutes, routeRate):
        try:
            self.handle.sendline("")
            self.handle.expect("config-router")
        except:
            main.log.warn("Probably not in config-router mode!")
            self.disconnect()
        main.log.info("Adding Routes")
        j = 0
        k = 0
        while numRoutes > 255:
            numRoutes = numRoutes - 255
            j = j + 1
        k = numRoutes % 254
        routes_added = 0
        if numRoutes > 255:
            numRoutes = 255
        for m in range(1, j + 1):
            for n in range(1, numRoutes + 1):
                network = str(net) + "." + str(m) + "." + str(n) + ".0/24"
                routeCmd = "network " + network
                try:
                    self.handle.sendline(routeCmd)
                    self.handle.expect("bgpd")
                except:
                    main.log.warn("failed to add route")
                    self.disconnect()
                waitTimer = 1.00 / routeRate
                time.sleep(waitTimer)
                routes_added = routes_added + 1
        for d in range(j + 1, j + 2):
            for e in range(1, k + 1):
                network = str(net) + "." + str(d) + "." + str(e) + ".0/24"
                routeCmd = "network " + network
                try:
                    self.handle.sendline(routeCmd)
                    self.handle.expect("bgpd")
                except:
                    main.log.warn("failed to add route")
                    self.disconnect
                waitTimer = 1.00 / routeRate
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
        main.log.info("Deleting Routes")
        j = 0
        k = 0
        while numRoutes > 255:
            numRoutes = numRoutes - 255
            j = j + 1
        k = numRoutes % 254
        routes_deleted = 0
        if numRoutes > 255:
            numRoutes = 255
        for m in range(1, j + 1):
            for n in range(1, numRoutes + 1):
                network = str(net) + "." + str(m) + "." + str(n) + ".0/24"
                routeCmd = "no network " + network
                try:
                    self.handle.sendline(routeCmd)
                    self.handle.expect("bgpd")
                except:
                    main.log.warn("Failed to delete route")
                    self.disconnect()
                waitTimer = 1.00 / routeRate
                time.sleep(waitTimer)
                routes_deleted = routes_deleted + 1
        for d in range(j + 1, j + 2):
            for e in range(1, k + 1):
                network = str(net) + "." + str(d) + "." + str(e) + ".0/24"
                routeCmd = "no network " + network
                try:
                    self.handle.sendline(routeCmd)
                    self.handle.expect("bgpd")
                except:
                    main.log.warn("Failed to delete route")
                    self.disconnect()
                waitTimer = 1.00 / routeRate
                time.sleep(waitTimer)
                routes_deleted = routes_deleted + 1
        if routes_deleted == numRoutes:
            return main.TRUE
        return main.FALSE

    def check_routes(self, brand, ip, user, pw):
        def pronto(ip, user, passwd):
            print "Connecting to Pronto switch"
            child = pexpect.spawn("telnet " + ip)
            i = child.expect(["login:", "CLI#", pexpect.TIMEOUT])
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
                i = child.expect(['17\d\.\d{1,3}\.\d{1,3}\.\d{1,3}', 'CLI#', pexpect.TIMEOUT])
                if i == 0:
                    count = count + 1
                elif i == 1:
                    print "Pronto flows: " + str(count) + "\nDone\n"
                    break
                else:
                    break
        def cisco(ip, user, passwd):
            print "Establishing Cisco switch connection"
            child = pexpect.spawn("ssh " + user + "@" + ip)
            i = child.expect(["Password:", "CLI#", pexpect.TIMEOUT])
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
                i = child.expect(["nw_src=17", "#", pexpect.TIMEOUT])
                if i == 0:
                    count = count + 1
                elif i == 1:
                    print "Cisco flows: " + str(count) + "\nDone\n"
                    break
                else:
                    break
            if brand == "pronto" or brand == "PRONTO":
                pronto(ip, user, passwd)
            # elif brand  == "cisco" or brand == "CISCO":
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
