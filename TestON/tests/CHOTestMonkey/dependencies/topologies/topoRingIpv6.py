#!/usr/bin/python
"""
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

class dualStackHost( Host ):
    def config( self, v6Addr='1000::1/64', **params ):
        r = super( Host, self ).config( **params )
        intf = self.defaultIntf()
        self.cmd( 'ip -6 addr add %s dev %s' % ( v6Addr, intf ) )
        return r

class ringTopo( Topo ):

    def __init__( self, **opts ):
        "Create a topology."

        # Initialize Topology
        Topo.__init__( self, **opts )

        s1 = self.addSwitch( 's1' )
        s2 = self.addSwitch( 's2' )
        s3 = self.addSwitch( 's3' )
        s4 = self.addSwitch( 's4' )
        s5 = self.addSwitch( 's5' )
        s6 = self.addSwitch( 's6' )
        s7 = self.addSwitch( 's7' )
        s8 = self.addSwitch( 's8' )
        s9 = self.addSwitch( 's9' )
        s10 = self.addSwitch( 's10' )

        # ... and now hosts
        s1_host = self.addHost( 'h1', ip='10.1.0.1/24', cls=dualStackHost, v6Addr='1000::1/64' )
        s2_host = self.addHost( 'h2', ip='10.1.0.2/24', cls=dualStackHost, v6Addr='1000::2/64' )
        s3_host = self.addHost( 'h3', ip='10.1.0.3/24', cls=dualStackHost, v6Addr='1000::3/64' )
        s4_host = self.addHost( 'h4', ip='10.1.0.4/24', cls=dualStackHost, v6Addr='1000::4/64' )
        s5_host = self.addHost( 'h5', ip='10.1.0.5/24', cls=dualStackHost, v6Addr='1000::5/64' )
        s6_host = self.addHost( 'h6', ip='10.1.0.6/24', cls=dualStackHost, v6Addr='1000::6/64' )
        s7_host = self.addHost( 'h7', ip='10.1.0.7/24', cls=dualStackHost, v6Addr='1000::7/64' )
        s8_host = self.addHost( 'h8', ip='10.1.0.8/24', cls=dualStackHost, v6Addr='1000::8/64' )
        s9_host = self.addHost( 'h9', ip='10.1.0.9/24', cls=dualStackHost, v6Addr='1000::9/64' )
        s10_host = self.addHost( 'h10', ip='10.1.0.10/24', cls=dualStackHost, v6Addr='1000::10/64' )

        # add edges between switch and corresponding host
        self.addLink( s1 , s1_host )
        self.addLink( s2 , s2_host )
        self.addLink( s3 , s3_host )
        self.addLink( s4 , s4_host )
        self.addLink( s5 , s5_host )
        self.addLink( s6 , s6_host )
        self.addLink( s7 , s7_host )
        self.addLink( s8 , s8_host )
        self.addLink( s9 , s9_host )
        self.addLink( s10 , s10_host )
        self.addLink(s1, s2)
        self.addLink(s2, s3)
        self.addLink(s3, s4)
        self.addLink(s4, s5)
        self.addLink(s5, s6)
        self.addLink(s6, s7)
        self.addLink(s7, s8)
        self.addLink(s8, s9)
        self.addLink(s9, s10)
        self.addLink(s10, s1)

topos = { 'ring': ( lambda: ringTopo() ) }

# HERE THE CODE DEFINITION OF THE TOPOLOGY ENDS

def setupNetwork():
    "Create network"
    topo = ringTopo()
    #if controller_ip == '':
        #controller_ip = '10.0.2.2';
    #    controller_ip = '127.0.0.1';
    network = Mininet(topo=topo, switch=OVSSwitch, autoSetMacs=True, controller=None)
    network.start()
    CLI( network )
    network.stop()

if __name__ == '__main__':
    setLogLevel('info')
    #setLogLevel('debug')
    setupNetwork()
