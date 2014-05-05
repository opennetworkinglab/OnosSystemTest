#!/usr/bin/python

"""
Fake Controller and Switch
Taken and modified from fvregress
"""
from threading import Thread,Lock,Condition
import socket
import sys
import logging
import os
import re
from struct import *

import cstruct as ofp
import message
import action
import parse

ctl_logger = logging.getLogger("CTL")
sw_logger = logging.getLogger("SW")

ctl_logger.setLevel(logging.DEBUG)
sw_logger.setLevel(logging.DEBUG)
class FvExcept(Exception):
    pass


class FakeController(Thread):
    ListenQueueSize = 2
    DefTimeout=5

    def __init__(self, name, port, timeout=DefTimeout):
        Thread.__init__(self)
        self.active = True
        self.name=name
        self.port=port
        if timeout is not None:
            self.timeout=timeout*2
        else:
            self.timeout=None
        self.switch_lock = Lock()
        self.sliced_switches = {}
        self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        #self.listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT,1)
        self.listen_sock.bind(('10.128.100.38',port))
        self.listen_sock.listen(FakeController.ListenQueueSize)
        self.setDaemon(True)
        ctl_logger.info("Spawning new controller " + self.name + " on listenning on port " + str(port))

    def run(self):
        print "Inside run function of FakeController class"
	ctl_logger.info(self.name + ": Starting io loop")
        while self.active :
	    print "Calling try block"
            try:
                (sock, address) = self.listen_sock.accept()
		print "Inside Try block"
		print "Address= ", address
		print "Last line of try block"
            except:
                if not self.active:
		    print "Not active"
                    break
            self.switch_lock.acquire()
            ctl_logger.info(self.name + ": Got a new connection from " + address[0] +
                ":"+ str(address[1]) + " : spawning new FakeSwitch")
            
	    print "Spawning new FakeSwitch from the controller"
	    sw = FakeSwitch("sliced_switch_"+self.name+"_"+ str(len(self.sliced_switches)),sock=sock)
            print ("Starting fake switch from the controller")
	    sw.start()

            # Initial handshake with switch(flowvisor)
   	    print "Sending hello"
            ctl_logger.info(self.name + ": Sending hello")
            send_msg = message.hello().pack()
            sw.send(send_msg)
	
	    #print ("Starting fake switch from the controller")
            #sw.start()	

	    print "Waiting for hello back"
            ctl_logger.info(self.name + ": Waiting for hello back")
            m = sw.recv_blocking(timeout=self.timeout)
            if (m != send_msg):
                print "message=:", m
		raise FvExcept("mismatched hellos in FakeController " + self.name)
            ctl_logger.info(self.name + ": Got hello")
	    print "Got hello"
		
	    print "Sending features request"
            ctl_logger.info(self.name + ": Sending features request")
            send_msg = message.features_request().pack()
            sw.send(send_msg)

	    print "Waiting for switch features"
            ctl_logger.info(self.name + ": Waiting for switch features")
            m = sw.recv_blocking(timeout=self.timeout)
            print "m from switch features=: ",m
	    if not m :
                raise FvExcept("Got no feature_response from sliced switch " + address[0] + ":" + str(address[1]) + \
                    " on FakeController " + self.name)
            oftype = parse.of_header_parse(m).type
            if (oftype != ofp.OFPT_FEATURES_REPLY):
                raise FvExcept("Got OFType: " + str(oftype) + " instead of switch features in FakeController " + self.name)
            #oftype = parse.of_header_parse(m).type
            #if (oftype != ofp.OFPT_FEATURES_REPLY):
            #    raise FvExcept("Got OFType: " + str(oftype) + " instead of switch features in FakeController " + self.name)
            if len(m) < 32 :
                raise FvExcept("Got short feature_response from sliced switch " + address[0] + ":" + str(address[1]) + \
                    " on FakeController " + self.name)
            ctl_logger.info(self.name + ": Got switch features")
	    print "Got switch features"
     
            dpid = parse.of_message_parse(m).datapath_id
            ctl_logger.info(self.name + ": Got a connection from switch with dpid= '" + str(dpid) + "'")
	    print "Got a connection from switch with dpid:", str(dpid)
	    	
            self.sliced_switches[dpid]=sw
            #self.active = False    
	    self.switch_lock.release()

    def name(self):
            return self.name

    def getSwitch(self, dpid):
        self.switch_lock.acquire()
        try:
            switch = self.sliced_switches[dpid]
        except (KeyError):
            ctl_logger.error("Tried to access switch with dpid='" + str(dpid) + "' on fake controller " + self.name)
            return None
        self.switch_lock.release()
        return switch

    def getSwitches(self) :
        return self.sliced_switches

    def set_dead(self) :
        for sw in self.sliced_switches.values():
            sw.set_dead()
        #self.active = False
        self.listen_sock.shutdown(socket.SHUT_RDWR)
        self.listen_sock.close()


class FakeSwitch(Thread):
    """ Acts as both a physical and sliced switch """
    BUFSIZE=4096

    def __init__(self,name, sock=None,host=None,port=None):
        usage= """Must specify one of socket or host+port"""
        Thread.__init__(self)
        if sock == None and ( host == None or port == None) :
            raise FvExcept(usage)
        # Setup socket
        if sock != None :
            self.sock= sock
            how = " on port " + str(sock.getsockname())
        else :
            self.sock= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.sock == None :
                raise FvExcept("socket returned None")
            self.sock.connect((host,port))
            if self.sock == None :
                raise FvExcept("connect returned None")
            how = " with connection " + host + ":" + str(port) + " " +  str(self.sock.getsockname())
        sw_logger.info("Created switch "+ name + how)
        # set up msg queues and locks
        self.sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY,1)
        self.name = name
        self.msg_cond = Condition()
        self.msgs = []
        self.alive=True
        self.setDaemon(True)

    def run(self):
        print "Inside run method of fake switch"
	sw_logger.info("Starting io loop for switch "+ self.name)
        while self.alive :
            try:
                print "Inside try block of run method of FakeSwitch" 
		m = self.sock.recv(FakeSwitch.BUFSIZE)
		print "m from run of FakeSwitch=: ", m
                if m == '' :
                    print "Since message is empty, I am printed" 
		    if self.alive:
                        sw_logger.info(self.name + " got EOF ; exiting...")
                        self.alive=False
			print "Got EOF..exiting"
                    return
            except (Exception), e :
                if self.alive:
                    sw_logger.info(self.name + " got " + str(e) + "; exiting...")
		    print "Except block..exiting"
                return
            #sw_logger.debug("----------------- Got packet")
            self.msg_cond.acquire()
            msgs = self.of_frame(m)
            for m in msgs :
                self.msgs.append(m)
                self.msg_cond.notify()
            self.msg_cond.release()
	    print "End of run method of FakeSwitch"
	    #self.alive = False

    def send(self,m) :
        return self.sock.send(m)

    def recv(self) :
        self.msg_cond.acquire()
        if len(self.msgs) > 0 :
            m = self.msgs.pop()
        else :
            m = None
        self.msg_cond.release()
        return m

    def recv_blocking(self, timeout=None) :
        self.msg_cond.acquire()
        if len(self.msgs) == 0 :     # assumes wakeup by notify() -- no stampeed!
            self.msg_cond.wait(timeout)
        if len(self.msgs) == 0 :
            return None    # timed out
        m = self.msgs.pop(0)
        self.msg_cond.release()
        return m

    def of_frame(self, m):
        msgs = []
        while 1 :
            if len(m) < 8 :
                raise FvExcept(" Bad framing in recv(). Message too short")
            (size,) = unpack("!2x H",m[0:4])
            #pdb.set_trace()
            msgs.append(m[0:size])
            if len(m) > size :
                m=m[size:]
            else :
                return msgs

    def is_alive(self):
        return self.alive

    def set_dead(self):
        sw_logger.info(self.name + ": Socket closing: " + str(self.sock.getsockname()))
        self.alive=False
        try:
            self.sock.close()
	except:
	    pass
	self.sock = None
