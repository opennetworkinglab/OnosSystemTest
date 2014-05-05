import sys
import socket
import time

import pexpect
import struct
import fcntl
import os
import signal
import re

import oftest.cstruct as ofp
import oftest.message as message
import oftest.action as action
import oftest.parse as parse
import oftest.fakedevice as fakedevice

timeout = 30

def genFlowModFlush():
    """
    Genericly usable flush_flow command
    @return flow_mod with delete command
    """
    flow_mod = message.flow_mod()
    flow_mod.match.wildcards = ofp.OFPFW_ALL
    flow_mod.command = ofp.OFPFC_DELETE
    flow_mod.priority = 0
    flow_mod.buffer_id = 0xffffffff
    flow_mod.out_port = ofp.OFPP_NONE
    return flow_mod

def genFeaturesReply(dpid, ports = [0,1,2,3], xid=1):
    """
    Features Reply with some specific parameters.
    For HW address of each port, it exploits dpid and the port number
    @param dpid dpid in 32bit int
    @param ports a list of the ports this switch has
    @param xid transaction ID
    @return features_reply
    """
    feat_reply = message.features_reply()
    feat_reply.header.xid = xid
    feat_reply.datapath_id = dpid
    feat_reply.n_buffers = 128
    feat_reply.n_tables = 2
    feat_reply.capabilities = (ofp.OFPC_FLOW_STATS + ofp.OFPC_TABLE_STATS + ofp.OFPC_PORT_STATS)
    feat_reply.actions = ofp.OFPAT_OUTPUT
    for i in ports:
        name = "port " + str(i)
        byte4 = (dpid & 0xff0000)>>16
        byte3 = (dpid & 0xff00)>>8
        byte2 = dpid & 0xff
        byte1 = (i & 0xff00)>>8
        byte0 = i & 0xff
        addr = [0, byte4, byte3, byte2, byte1, byte0]
        feat_reply.ports.append(genPhyPort(name, addr, port_no=i))
    return feat_reply

def genPhyPort(name, addr, port_no):
    """
    Genericly usable phy_port
    @param name The port's name in string
    @param addr hw_addr (MAC address) as array: [xx,xx,xx,xx,xx,xx]
    @param port_no port number
    @return phy_port
    """
    phy_port = ofp.ofp_phy_port()
    phy_port.port_no = port_no
    phy_port.hw_addr = addr
    phy_port.name = name
    return phy_port


#Create a Fake controller listening on port 10100
ctr = fakedevice.FakeController(name= 'ctrller0',port= 10100,timeout= 5)
print ctr
ctr.start()
time.sleep(30)

sw = fakedevice.FakeSwitch(name='switch0', host='10.128.100.29', port=6633)
print sw

send_msg = message.hello().pack()
sw.send(send_msg)
sw.start()
#time.sleep(300)

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
switch_features = genFeaturesReply(ports=ports, dpid=1)
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
















