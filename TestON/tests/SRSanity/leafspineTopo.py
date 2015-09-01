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

	s1 = self.addSwitch('s1')
	s2 = self.addSwitch('s2')
	s3 = self.addSwitch('s3')
	s4 = self.addSwitch('s4')

	s101 = self.addSwitch('s257')
	s102 = self.addSwitch('s258')
        s103 = self.addSwitch('s259')
        s104 = self.addSwitch('s260')
        
        # Add links
        self.addLink( host1, s1)
        self.addLink( host2, s2)
        self.addLink( host3, s3)
        self.addLink( host4, s4)

        self.addLink( s1, s101)
        self.addLink( s1, s102)
        self.addLink( s1, s103)
        self.addLink( s1, s104)

        self.addLink( s2, s101)
        self.addLink( s2, s102)
        self.addLink( s2, s103)
        self.addLink( s2, s104)

        self.addLink( s3, s101)
        self.addLink( s3, s102)
        self.addLink( s3, s103)
        self.addLink( s3, s104)

        self.addLink( s4, s101)
        self.addLink( s4, s102)
        self.addLink( s4, s103)
        self.addLink( s4, s104)

topos = { 'mytopo': ( lambda: MyTopo() ) }
