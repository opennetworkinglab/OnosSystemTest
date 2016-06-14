#!/usr/bin/python           # This is server.py file
from scapy.all import *
import socket               # Import socket module
import time                 # Import Time module
import sys
import os

path = os.getcwd()
sys.path.append('OnosSystemTest/TestON/tests/FUNC/FUNCbgpls/dependencies')   #Setting the path for BgpLS
from Nbdata import BgpLs

obj = BgpLs()
returnlist = obj.Constants()
peerIp = returnlist[0][0]

load_contrib('bgp')
s = socket.socket()         # Create a socket object
host = peerIp # Get local machine name
port = 179                # Reserve a port for your service.
s.bind((host, port))        # Bind to the port
pkts = rdpcap(path + "/OnosSystemTest/TestON/tests/FUNC/FUNCbgpls/dependencies/Bgpls_packets/bgpls_all.pcap")
pkts[69][BGPOpen].bgp_id = peerIp

s.listen(5)                   # Now wait for client connection.

print("starting Connecting to ONOS peer")
c, addr = s.accept()     # Establish connection with client.
print 'Got connection from ONOS :', addr
c.send(str(pkts[69][BGPHeader])) # OPEN MESSAGE
c.recv(4096)
c.send(str(pkts[71][BGPHeader]))# KEEPALIVE MESSAGE
c.recv(4096)
c.send(str(pkts[72][BGPHeader]))   # UPDATE MESSAGES
c.send(str(pkts[74][BGPHeader]))
c.send(str(pkts[71][BGPHeader]))

time.sleep(10)               # Waiting for 120 seconds for update message.

c.send(str(pkts[298][BGPHeader]))
c.send(str(pkts[860][BGPHeader]))   # UPDATE MESSAGES with new node
c.send(str(pkts[865][BGPHeader]))
print ("New Node update msg sent")

time.sleep(5)
c.send(str(pkts[890][BGPHeader]))
print ("Node Delete msg sent")


while True:
    c.recv(4096)
    c.send(str(pkts[71][BGPHeader]))

  # c.close()                # Close the connection
