#!/usr/bin/python

"""
Custom topology for Mininet
"""
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Host, RemoteController
from mininet.node import Node
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.util import dumpNodeConnections
from mininet.node import ( UserSwitch, OVSSwitch, IVSSwitch )

class VLANHost( Host ):
    def config( self, vlan=100, **params ):
        r = super( Host, self ).config( **params )
        intf = self.defaultIntf()
        self.cmd( 'ifconfig %s inet 0' % intf )
        self.cmd( 'vconfig add %s %d' % ( intf, vlan ) )
        self.cmd( 'ifconfig %s.%d inet %s' % ( intf, vlan, params['ip'] ) )
        newName = '%s.%d' % ( intf, vlan )
        intf.name = newName
        self.nameToIntf[ newName ] = intf
        return r

class IPv6Host( Host ):
    def config( self, v6Addr='1000:1/64', **params ):
        r = super( Host, self ).config( **params )
        intf = self.defaultIntf()
        self.cmd( 'ifconfig %s inet 0' % intf )
        self.cmd( 'ip -6 addr add %s dev %s' % ( v6Addr, intf ) )
        return r

class MyTopo( Topo ):

    def __init__( self, **opts ):
        # Initialize topology
        Topo.__init__( self, **opts)

        # IPv4 hosts
        host1=self.addHost( 'h1', ip='10.0.0.1/24' )
        host2=self.addHost( 'h2', ip='10.0.0.2/24' )

        # VLAN hosts
        host3=self.addHost( 'h3', ip='10.0.0.3/24', cls=VLANHost, vlan=10 )
        host4=self.addHost( 'h4', ip='10.0.0.4/24', cls=VLANHost, vlan=10 )


        s1 = self.addSwitch( 's1' )

        self.addLink(s1, host1)
        self.addLink(s1, host2)
        self.addLink(s1, host3)
        self.addLink(s1, host4)


        topos = { 'mytopo': ( lambda: MyTopo() ) }

def setupNetwork():
    "Create network"
    topo = MyTopo()
    network = Mininet(topo=topo, autoSetMacs=True, autoStaticArp=True, controller=None)
    network.start()
    CLI( network )
    network.stop()

if __name__ == '__main__':
    setLogLevel('info')
    #setLogLevel('debug')
    setupNetwork()
