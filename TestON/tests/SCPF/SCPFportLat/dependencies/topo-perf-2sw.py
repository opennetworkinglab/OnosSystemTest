'''
imple 2 switch topology for topologoy performance test
'''

from mininet.topo import Topo

class MyTopo( Topo ):
    def __init__(self):
        Topo.__init__(self)
        s1 = self.addSwitch( "s1", dpid="0000000000000001")
        s2 = self.addSwitch( "s2", dpid="0000000000000002")

        h1 = self.addHost( "h1" )
        h2 = self.addHost( "h2" )
        self.addLink( s1, s2 )
        self.addLink( s1, h1 )
        self.addLink( s2, h2 )

topos = { 'mytopo': ( lambda: MyTopo() ) }
