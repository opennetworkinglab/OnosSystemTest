"""Custom topology example

Two directly connected switches plus hosts for each switch:

   host(s) --- switch --- switch -- switch --- host(s)

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo
import sys
import os

class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        host1 = self.addHost( 'h1' )
        host2 = self.addHost( 'h2' )
	host3 = self.addHost( 'h3' )
	host4 = self.addHost( 'h4' )
	host5 = self.addHost( 'h5' )
	host6 = self.addHost( 'h6' )

        leftSwitch = self.addSwitch( 's1' )
        midSwitch = self.addSwitch( 's2' )
        rightSwitch = self.addSwitch( 's3' )
	

        # Add links
        self.addLink( host1, leftSwitch )
        self.addLink( host2, leftSwitch )
        self.addLink( host3, leftSwitch )
        self.addLink( host4, leftSwitch )
        self.addLink( host5, leftSwitch )
        self.addLink( rightSwitch, host6 )
        self.addLink( leftSwitch, midSwitch )
	self.addLink( rightSwitch, midSwitch )



topos = { 'mytopo': ( lambda: MyTopo() ) }
