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
from leafspineTopo import MyTopo

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
    net = Mininet(topo=topo, switch=UserSwitch, controller=partial(RemoteController,ip='10.128.4.49'))
    net.start()
   
    h1, h2, h3, h4 = net.hosts

    h1.setIP("10.0.1.1/24")
    h1.setMAC("00:00:00:00:00:01")
    setDefaultRoute(h1, "10.0.1.128")

    h2.setIP("10.0.2.1/24")
    h2.setMAC("00:00:00:00:00:02")
    setDefaultRoute(h2, "10.0.2.128")

    h3.setIP("10.0.3.1/24")
    h3.setMAC("00:00:00:00:00:03")
    setDefaultRoute(h3, "10.0.3.128")

    h4.setIP("10.0.4.1/24")
    h4.setMAC("00:00:00:00:00:04")
    setDefaultRoute(h4, "10.0.4.128")

    CLI(net)
    net.stop()
