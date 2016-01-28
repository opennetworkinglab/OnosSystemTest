#!/usr/bin/python

"""
Custom topology for Mininet
"""
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Host, RemoteController
from mininet.node import Node
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.util import dumpNodeConnections
from mininet.node import ( UserSwitch, OVSSwitch, IVSSwitch )

class MyTopo( Topo ):

    def __init__( self ):
        # Initialize topology
        Topo.__init__( self )

        host1 = self.addHost('h1', ip='10.1.0.1/24')
        host2 = self.addHost('h2', ip='10.1.0.2/24')
        host3 = self.addHost('h3', ip='10.1.0.3/24')
        host4 = self.addHost('h4', ip='10.1.0.4/24')
        host5 = self.addHost('h5', ip='10.1.0.5/24')
        host6 = self.addHost('h6', ip='10.1.0.6/24')
        host7 = self.addHost('h7', ip='10.1.0.7/24')

        s1 = self.addSwitch( 's1' )
        s2 = self.addSwitch( 's2' )
        s3 = self.addSwitch( 's3' )
        s4 = self.addSwitch( 's4' )
        s5 = self.addSwitch( 's5' )
        s6 = self.addSwitch( 's6' )
        s7 = self.addSwitch( 's7' )
        s8 = self.addSwitch( 's8' )


        self.addLink(s1, host1)
        self.addLink(s2, host2)
        self.addLink(s3, host3)
        self.addLink(s4, host4)
        self.addLink(s5, host5)
        self.addLink(s6, host6)
        self.addLink(s7, host7)



        self.addLink(s1,s2)
        self.addLink(s2,s3)
        self.addLink(s3,s4)
        self.addLink(s4,s5)
        self.addLink(s5,s6)
        self.addLink(s6,s7)
        self.addLink(s4,s8)
        self.addLink(s8,s5)

        topos = { 'mytopo': ( lambda: MyTopo() ) }

# HERE THE CODE DEFINITION OF THE TOPOLOGY ENDS

def setupNetwork():
    "Create network"
    topo = MyTopo()
    network = Mininet(topo=topo, autoSetMacs=True, controller=None)
    network.start()
    CLI( network )
    network.stop()

if __name__ == '__main__':
    setLogLevel('info')
    #setLogLevel('debug')
    setupNetwork()
