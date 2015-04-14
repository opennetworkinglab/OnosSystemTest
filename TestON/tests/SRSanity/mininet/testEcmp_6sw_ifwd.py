#!/usr/bin/env python
'''
Script to define a single-switch topology and then set params on the hosts.

Intended for the "Advanced Switches" exercise.
'''

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import UserSwitch, RemoteController, OVSSwitch
from mininet.topolib import TreeNet
from mininet.topo import SingleSwitchTopo
from mininet.net import Mininet
from functools import partial
from ecmpTopo6 import MyTopo
from alterableNet import alterableCLI
from alterableNet import alterNet

def setDefaultRoute(node, ip, intf=None):
    """Modified node.setDefaultRoute that sets a default gateway IP.

    Example call:
    /sbin/route add -net 0.0.0.0 gw 1.1.1.1 eth0
    
    ip: string
    intf: interface string
    """
    if not intf:
        intf = node.defaultIntf()
    #node.cmd( 'ip route flush root 0/0' )
    #node.cmd( 'route add default %s' % intf )
    node.cmd('route add -net 0.0.0.0 gw %s %s' % (ip, intf))

if __name__ == '__main__':
    setLogLevel( 'info' )
    topo = MyTopo()
    net = alterNet(topo=topo, switch=UserSwitch, controller=partial(RemoteController,ip='192.168.0.5'))
    net.start()
   
    #h1, h2 = net.hosts

    #h1.setIP("10.0.1.1/24")
    #h1.setMAC("00:00:00:00:01:01")
    #h1.setARP("10.0.1.128", "00:00:00:01:01:80")
    #h1.setARP("10.0.1.2", "00:00:00:00:01:02")
    #setDefaultRoute(h1, "10.0.1.128")

    #h2.setIP("7.7.7.7/24")
    #h2.setMAC("00:00:00:00:07:07")
    #h2.setARP("10.0.1.128", "00:00:00:01:01:80")
    #h2.setARP("10.0.1.1", "00:00:00:00:01:01")
    #setDefaultRoute(h2, "7.7.7.128")


    alterableCLI(net)
    net.stop()
