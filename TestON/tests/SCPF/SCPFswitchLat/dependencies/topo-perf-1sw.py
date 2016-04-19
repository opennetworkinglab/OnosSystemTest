'''
Simple 1 switch topology for topologoy performance test
'''

from mininet.topo import Topo

class MyTopo( Topo ):
    def __init__(self):
        Topo.__init__(self)

        s3 = self.addSwitch( "s3", dpid="0000000000000001")

topos = { 'mytopo': ( lambda: MyTopo() ) }
