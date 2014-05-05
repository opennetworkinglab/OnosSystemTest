import sys
sys.path.append("../")
from drivers.common.apidriver import API

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

#from testutilsdriver import *
from testutilsdriver import TestUtilsDriver


timeout = 30

class FakeDeviceDriver(API):

    def __init__(self):
        super(API, self).__init__()
        print 'init'
	self.ctr1 = fakedevice.FakeController(name= 'ctrller0',port= 10100,timeout= 5)
	print self.ctr1
	self.sw = fakedevice.FakeSwitch(name='switch0', host='10.128.100.29', port=6633)
	print self.sw
	self.contList = []
	self.contList.append(self.ctr1)
	self.swList = []
	self.swList.append(self.sw)


    def connect(self,**connectargs):
        for key in connectargs:
            vars(self)[key] = connectargs[key]
        self.name = self.options['name']
        connect_result = super(API,self).connect()
        self.logFileName = main.logdir+"/"+self.name+".session"
        return main.TRUE

    def startController(self):
	self.ctr1.start()
	#time.sleep(30) 
	
    def startSwitch(self):
	send_msg = message.hello().pack()
	self.sw.send(send_msg)
	self.sw.start()
   
    def getswList(self):
	return self.swList

    def getcontList(self):
	return self.contList
	
    def handshake(self):
	print "Fake Switch handshake with Flowvisor"
	print "___________________________________"
	m = self.sw.recv_blocking(timeout=timeout)
	exp = self.send_msg
	if (m != exp):
        	print "Got mismatched hello at switch"
	else:
        	print "Got hello at switch"
        	print "___________________"

	m = self.sw.recv_blocking(timeout=timeout)
	exp = genFlowModFlush().pack()
	if (m != exp):
        	print "Did not get flow mod"
	else:
        	print "Received flow mod"
        	print "_________________"
	
	m = self.sw.recv_blocking(timeout=timeout)
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
	self.sw.send(send_msg)
	print "Sent switch_features to flowvisor"

	print "HANDSHAKE OF FAKESWITCH and FAKECONTROLLER"
	print "Waiting for features_request from fakeController"
	m = self.sw.recv_blocking(timeout=timeout)
	ref_type = parse.of_header_parse(m).type
	ref_xid = parse.of_header_parse(m).xid

	if (ref_type != ofp.OFPT_FEATURES_REQUEST):
        	print "Failed to get features_request from fake controller"
	else:
        	print "Got features_request from fake controller for"

	switch_features.header.xid = parse.of_header_parse(m).xid
	send_msg = switch_features.pack()
	self.sw.send(send_msg)
	print " Sent switch_features to fake controller "
	print "HANDSHAKE COMPLETE!!"


