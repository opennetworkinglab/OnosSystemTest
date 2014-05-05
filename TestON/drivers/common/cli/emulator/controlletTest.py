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

timeout = 30
ETHERTYPE_IP = 0x800
ETHERTYPE_ARP = 0x806
ARP_REQ = 1
ARP_REPLY = 2
IPPROTO_ICMP = socket.IPPROTO_ICMP
ECHO_REQUEST = 0x3

ETHERTYPE_LLDP = 0x88cc
CHASSISID_TYPE = 1
PORTID_TYPE = 2
TTL_TYPE = 3


def _b2a(str):
    """
    Translate binary to an ascii hex code (almost) human readable form
    @parem binary hexadecimal value
    @return a set of ascii values of 0 to F
    """
    if str :
        return binascii.hexlify(str)
    else :
        return "***NONE***"

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

def simplePacket(pktlen=100,
                 dl_dst='00:01:02:03:04:05',
                 dl_src='00:06:07:08:09:0a',
                 dl_vlan=0xffff,
                 dl_vlan_pcp=0,
                 dl_vlan_cfi=0,
                 dl_type = ETHERTYPE_IP,
                 nw_src='192.168.0.1',
                 nw_dst='192.168.0.2',
                 nw_tos=0,
                 nw_proto=socket.IPPROTO_TCP,
                 tp_src=1234,
                 tp_dst=80
                 ):
    """
    Return a simple packet
    Users shouldn't assume anything about this packet other than that
    it is a valid ethernet/IP/TCP frame.
    It generates a packet in a shape of TCP, UDP, ICMP, ARP, IP,
    Raw ethernet, with or without a VLAN tag.
    If dl_type is other than IP or ARP, the upper layer parameters will be ignored
    If nw_proto is other than TCP, UDP or ICMP, the upper layer parameters will be ignored
    Supports a few parameters
    @param pktlen Length of packet in bytes w/o CRC
    @param dl_dst Destination MAC
    @param dl_src Source MAC
    @param dl_vlan VLAN ID, No VLAN tags if the value is 0xffff
    @param dl_vlan_pcp VLAN priority. Valid only dl_vlan is in a valid range
    @param dl_vlan_cfi VLAN CFI
    @param dl_type Type of L3
    @param nw_src IP source
    @param nw_dst IP destination
    @param nw_tos IP ToS
    @param nw_proto L4 protocol When ARP is specified in dl_type, it is used for op code
    @param tp_dst UDP/TCP destination port
    @param tp_src UDP/TCP source port
    @return valid packet
    """
    # Note Dot1Q.id is really CFI
    if (dl_vlan == 0xffff):
        pkt = scapy.Ether(dst=dl_dst, src=dl_src)
    else:
        dl_vlan = dl_vlan & 0x0fff
        pkt = scapy.Ether(dst=dl_dst, src=dl_src)/ \
            scapy.Dot1Q(prio=dl_vlan_pcp, id=dl_vlan_cfi, vlan=dl_vlan)

    if (dl_type == ETHERTYPE_IP):
        pkt = pkt/ scapy.IP(src=nw_src, dst=nw_dst, tos=nw_tos)
        if (nw_proto == socket.IPPROTO_TCP):
            pkt = pkt/ scapy.TCP(sport=tp_src, dport=tp_dst)
        elif (nw_proto == socket.IPPROTO_UDP):
            pkt = pkt/ scapy.UDP(sport=tp_src, dport=tp_dst)
        elif (nw_proto == socket.IPPROTO_ICMP):
            pkt = pkt/ scapy.ICMP(type=tp_src, code=tp_dst)

    elif (dl_type == ETHERTYPE_ARP):
        pkt = pkt/ scapy.ARP(op=nw_proto, hwsrc=dl_src, psrc=nw_src, hwdst=dl_dst, pdst=nw_dst)
        return pkt

    pkt = pkt/("D" * (pktlen - len(pkt)))
    return pkt

def genVal32bit():
    """
    Generate random 32bit value used for xid, dpid and buffer_id
    @return 32bit value excluding 0 and 0xffffffff
    """
    return random.randrange(1,0xfffffffe)


def genPacketIn(xid=None,
                buffer_id=None,
                in_port=3,
                pkt=simplePacket()):
    """
    Create a packet_in message with genericly usable values
    @param xid transaction ID used in OpenFlow header
    @param buffer_id bufer_id
    @param in_port ingress port
    @param pkt a packet to be attached on packet_in
    @return packet_in
    """
    if xid == None:
        xid = genVal32bit()
    if buffer_id == None:
        buffer_id = genVal32bit()

    packet_in = message.packet_in()
    packet_in.header.xid = xid
    packet_in.buffer_id = buffer_id
    packet_in.in_port = in_port
    packet_in.reason = ofp.OFPR_NO_MATCH
    if pkt is not None:
        packet_in.data = str(pkt)
    return packet_in



def ofmsgSndCmp(snd_list, exp_list, xid_ignore=False, hdr_only=False, ignore_cookie=True, cookies=[]):
    """
    Wrapper method for comparing received message and expected message
    See ofmsgSndCmpWithXid()
    """
    (success, ret_xid) = ofmsgSndCmpWithXid(snd_list, exp_list, xid_ignore, hdr_only, ignore_cookie, cookies)
    return success


def ofmsgSndCmpWithXid(snd_list, exp_list, xid_ignore=False, hdr_only=False, ignore_cookie=True, cookies=[]):
    """
    Extract snd_list (list) and exp_list (list of list).
    With snd_list, send a message from the specific switch/controller ports.
    Then using the information inside exp_list, check the specified switch/controller to
    wait for message(s).
    Compare the received data with expected data.
    It accept multiple expected messages on multiple switches/controllers.
    It also supports to check if any packet was not received on specified
    switches/controllers.
    @param parent parent must have FlowVisor object for the test and logger
    @param snd_list list of the information for sending a message.
    ["controller", num, sw_num, buf] or ["switch", num, buf]
    num is switch number or controller number (starting at 0) as int,
    sw_num is switch number (starting at 0) if sw_ctl is "controller".
    buf is OpenFlow message created using the test utilities
    @param exp_list list of list of the information about expected messages
    [[sw_ctrl, num, buf], [sw_ctrl, num, buf], ---- [sw_ctrl, num, buf]]
    where: sw_ctrl is a string, either "switch" or "controller",
    num is switch number or controller number (starting at 0) as int,
    buf is OpenFlow message created using the test utilities.
    If messages should not be received, this field must be None.
    @param xid_ignore If True, it doesn't care about xid difference
    @param hdr_only If True, it only checks OpenFlow header
    @return False if error, True on success
    @return xid in received message. If not successful, returns 0
    """
    
    snd_sw_ctrl = snd_list[0]
    snd_num = snd_list[1]
    ret_xid = 0

    if snd_sw_ctrl == "switch":
        snd_msg = snd_list[2].pack()
        print "Print sent message in readable format_______"
	sent_string = snd_list[2].show()
	print sent_string
	print "\n"
	try:
            sw = swList[0]
	    sw.send(snd_msg)
	    print "Sent message from switch to controller"
	    print "Sent message is: ", snd_msg
	    print "\n"
	except:
	    print "Unknown Switch isn't sending any messages"
    elif snd_sw_ctrl == "controller":
        sw_num = snd_list[2]
        snd_msg = snd_list[3].pack()
        try:
            cont = contList[0]
        except:
            print "Unknown Controller"
        try:
            #sw = cont.getSwitch(sw_num)
	    sw = swList[0]
        except:
            print "Unknown switch connected to controller"
            return (False, ret_xid)
        print "Sending message from controller to switch"
        sw.send(snd_msg)
    else:
	print "Looks like sender is not connected"
        return (False, ret_xid)

    for exp in exp_list:
        exp_sw_ctrl = exp[0]
        exp_num = exp[1]
        if exp[2]:
            exp_msg = exp[2].pack()
	    exp_string = exp[2].show()
	    print "Printing the expected string _______"
	    print exp_string
	    print "\n"
	    print "expected message is: ", exp_msg
        else:
            exp_msg = None
        #if exp_sw_ctrl == "switch":
        	#print " This part is taken off"
        if exp_sw_ctrl == "controller":
            try:
                cont = contList[0]
		print "Receiver is a controller"
            except:
                print "Unknown controller"
                return (False, ret_xid)
            try:
                if snd_sw_ctrl == "controller":
                    sw = contList[0]
                else:
                    sw = cont.getSwitch(snd_num)
            except:
                print "Unknown switch connected to controller"
                return (False, ret_xid)
            if exp_msg:
                response = sw.recv_blocking(timeout=timeout)
                if response:
		    print "Analysing the response"
                    print "Response before parsing: ", response
		    print "\n"
		    ret_xid = int(_b2a(response[4:8]), 16)
                    if xid_ignore:
                        response = response[0:4] + exp_msg[4:8] + response[8:]
			print "Response parsed"
			print "Response = ", response
                if hdr_only:
                    print "This part of code is taken off since hdr_only is false"
                else:
                    if response != exp_msg:
                        print "Received unexpected message"
                        return (False, ret_xid)
            else:
                response = sw.recv()
                if response != None:
                    return (False, ret_xid)

        else:
            print "Target not specified in one of exp_list"
            return (False, ret_xid)

    return (True, ret_xid)    


#Create a Fake controller listening on port 10100
ctr = fakedevice.FakeController(name= 'ctrller0',port= 10100,timeout= 5)
print ctr
ctr.start()
time.sleep(30)

ctr1 = fakedevice.FakeController(name= 'ctrller1',port= 10101,timeout= 5)
print ctr1
#ctr1.start()

#Create a controllerList and a switchList
contList = []
contList.append(ctr)
contList.append(ctr1)

sw = fakedevice.FakeSwitch(name='switch0', host='10.128.100.29', port=6633)
print sw

swList = []
swList.append(sw)

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
res = ofmsgSndCmp(snd_list, exp_list, xid_ignore=True)
print "Result = ", res
#self.assertTrue(res, "%s: Received unexpected message" %(self.__class__.__name__))
















