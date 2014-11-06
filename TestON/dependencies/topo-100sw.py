
from mininet.topo import Topo

class MyTopo( Topo ):
        "100 'floating' switch topology"

        def __init__( self ):
                # Initialize topology
                Topo.__init__( self )

                sw_list = []

                for i in range(1, 101):
                        sw_list.append(
                                self.addSwitch(
                                        's'+str(i),
                                        dpid = str(i).zfill(16)))


                #Below connections are used for test cases
                #that need to test link and port events
                #Add link between switch 1 and switch 2
                self.addLink(sw_list[0],sw_list[1])
                
                #Create hosts and attach to sw 1 and sw 2
                h1 = self.addHost('h1')
                h2 = self.addHost('h2')
                self.addLink(sw_list[0],h1)
                self.addLink(sw_list[1],h2)
        
topos = { 'mytopo': ( lambda: MyTopo() ) }
