"""
Copyright 2016 Open Networking Foundation (ONF)

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.
"""

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

class MyTopo( Topo ):

    def __init__( self, **opts ):
        # Initialize topology
        Topo.__init__( self, **opts)

        # IPv4 hosts
        host1=self.addHost( 'h1', ip='10.0.0.1/24' )
        host2=self.addHost( 'h2', ip='10.0.0.2/24' )
        host3=self.addHost( 'h3', ip='10.0.0.3/24' )
        host4=self.addHost( 'h4', ip='10.0.0.4/24' )

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
