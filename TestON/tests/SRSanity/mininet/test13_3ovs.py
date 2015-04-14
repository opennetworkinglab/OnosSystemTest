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
from exam import MyTopo


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
    #net = Mininet(topo=topo, switch=UserSwitch, controller=partial(RemoteController,ip='192.168.0.2'))
    net = Mininet(topo=topo, switch=OVSSwitch, controller=partial(RemoteController,ip='192.168.0.5'))
    net.start()


    h1, h2, h3, h4, h5, h6 = net.hosts

    # For each host in Subnet A, set up a default route and static ARPs.
    #for i, h in enumerate([h1, h2, h3]):
    #    h.setIP("10.0.1.%i/24" % (i + 1))
    #    h.setMAC("00:00:00:00:01:0%i" % (i + 1))
    #    setDefaultRoute(h, "10.0.1.128")

    #for subnet, h in [(2, h4), (3, h5)]:
    #    h.setIP("10.0.%i.1/24" % subnet)
    #    h.setMAC("00:00:00:00:0%i:01" % subnet)
	# router uses router-mac in arps, not interface macs
     #   setDefaultRoute(h, "10.0.%i.128" % subnet)

    #h6.setIP("7.7.7.7/24")
    #h6.setMAC("00:00:07:07:07:07")
    #setDefaultRoute(h6, "7.7.7.128")

    CLI(net)
    net.stop()
