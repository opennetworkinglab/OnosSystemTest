""" This script is just the commands and the test case, all the testutils functions 
are moved to another file named modifiedTestUtils.py which is being imported here 
"""

import sys
import socket
import time

import random
import pexpect
import struct
import fcntl
import os
import signal
import re
import binascii

import scapy.all as scapy

import oftest.cstruct as ofp
import oftest.message as message
import oftest.action as action
import oftest.parse as parse
import oftest.fakedevice as fakedevice

from modifiedTestUtils import *

timeout = 30

#Create a Fake controller listening on port 10100
ctr = fakedevice.FakeController(name= 'ctrller0',port= 10100,timeout= 5)
print ctr
ctr.start()
time.sleep(30)

#ctr1 = fakedevice.FakeController(name= 'ctrller1',port= 10101,timeout= 5)
#print ctr1
#ctr1.start()

#Create a controllerList and a switchList
contList = []
contList.append(ctr)
#contList.append(ctr1)

sw = fakedevice.FakeSwitch(name='switch0', host='10.128.100.29', port=6633)
print sw

swList = []
swList.append(sw)
send_msg = message.hello().pack()
sw.send(send_msg)
sw.start()
#time.sleep(30)

print "Fake Switch handshake with Flowvisor"
print "___________________________________"
m = sw.recv_blocking(timeout=timeout)
exp = send_msg
if (m != exp):
        print "Got mismatched hello at switch"
else:
        print "Got hello at switch"
        print "___________________"

m = sw.recv_blocking(timeout=timeout)
exp = genFlowModFlush().pack()
if (m != exp):
        print "Did not get flow mod"
else:
        print "Received flow mod"
        print "_________________"

m = sw.recv_blocking(timeout=timeout)
exp = message.features_request().pack()
if (m != exp):
        print "Did not get features request from flowvisor"
else:
        print "Got features request from flowvisor"
        print "____________________________________"


nPorts=4
ports = []
for dataport in range(nPorts):
        ports.append(dataport)
switch_features = genFeaturesReply(ports=ports, dpid=0)
switch_features.header.xid = parse.of_header_parse(m).xid
send_msg = switch_features.pack()
sw.send(send_msg)
print "Sent switch_features to flowvisor"

print "HANDSHAKE OF FAKESWITCH and FAKECONTROLLER"
print "Waiting for features_request from fakeController"
m = sw.recv_blocking(timeout=timeout)
ref_type = parse.of_header_parse(m).type
ref_xid = parse.of_header_parse(m).xid

if (ref_type != ofp.OFPT_FEATURES_REQUEST):
        print "Failed to get features_request from fake controller"
else:
        print "Got features_request from fake controller for"

switch_features.header.xid = parse.of_header_parse(m).xid
send_msg = switch_features.pack()
sw.send(send_msg)
print " Sent switch_features to fake controller "
print "HANDSHAKE COMPLETE!!"

SwitchNames = ctr.getSwitches()
print "Switch Names=", SwitchNames

print "****************************************************"

SRC_MAC_FOR_CTL0_0 = "00:00:00:00:00:02"
print "Generating a Simple Packet"
print "\n"
pkt = simplePacket(dl_src = SRC_MAC_FOR_CTL0_0)
in_port = 0 #CTL0 has this port
msg = genPacketIn(in_port=in_port, pkt=pkt)
print "Packet = ", pkt
print "\n"
print "Message = ", msg
print "\n"


snd_list = ["switch", 0, msg]
exp_list = [["controller", 0, msg]]
print "Comparing expected and actual messages"
res = ofmsgSndCmp(snd_list, exp_list, swList, contList, xid_ignore=True)
print "Result = ", res
#self.assertTrue(res, "%s: Received unexpected message" %(self.__class__.__name__))

