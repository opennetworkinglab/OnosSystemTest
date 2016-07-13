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
pkts = rdpcap(path + "/OnosSystemTest/TestON/tests/FUNC/FUNCbgpls/dependencies/Bgpls_packets/bgpls.pcap")
time.sleep(15)
pkts[759][BGPOpen].bgp_id = peerIp

s.listen(5)                   # Now wait for client connection.

print("starting Connecting to ONOS peer")
c, addr = s.accept()     # Establish connection with client.
print 'Got connection from ONOS :', addr
c.send(str(pkts[759][BGPHeader])) # OPEN MESSAGE
c.recv(4096)
c.send(str(pkts[765][BGPHeader]))# KEEPALIVE MESSAGE
c.recv(4096)
c.send(str(pkts[768][BGPHeader]))   # UPDATE MESSAGES
c.send(str(pkts[771][BGPHeader]))
c.send(str(pkts[773][BGPHeader]))
c.send(str(pkts[775][BGPHeader]))
c.send(str(pkts[778][BGPHeader]))
c.send(str(pkts[765][BGPHeader]))

while True:
    c.recv(4096)
    c.send(str(pkts[765][BGPHeader]))

  # c.close()                # Close the connection
