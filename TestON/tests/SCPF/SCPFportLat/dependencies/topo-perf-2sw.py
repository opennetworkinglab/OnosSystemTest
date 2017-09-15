"""
Copyright 2016 Open Networking Foundation ( ONF )

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    ( at your option ) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.
"""
"""
Simple 2 switch topology for topologoy performance test
"""
from mininet.topo import Topo


class MyTopo( Topo ):

    def __init__( self ):
        Topo.__init__( self )
        s1 = self.addSwitch( "s1", dpid="0000000000000001" )
        s2 = self.addSwitch( "s2", dpid="0000000000000002" )

        h1 = self.addHost( "h1" )
        h2 = self.addHost( "h2" )
        self.addLink( s1, s2 )
        self.addLink( s1, h1 )
        self.addLink( s2, h2 )

topos = { 'mytopo': ( lambda: MyTopo() ) }
