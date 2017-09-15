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
This file contains device, host and link class for CHOTestMonkey
Author: you@onlab.us
"""
class NetworkElement:

    def __init__( self, index ):
        self.default = ''
        self.index = index
        self.status = 'up'

    def isUp( self ):
        return self.status == 'up'

    def isDown( self ):
        return self.status == 'down'

    def isRemoved( self ):
        return self.status == 'removed'

    def setRemoved( self ):
        self.status = 'removed'

    def bringDown( self ):
        self.status = 'down'

    def bringUp( self ):
        self.status = 'up'


class Device( NetworkElement ):

    def __init__( self, index, name, dpid ):
        NetworkElement.__init__( self, index )
        self.name = name
        self.dpid = dpid
        self.hosts = []
        # For each bidirectional link, we only store one direction here
        self.outgoingLinks = []

    def __str__( self ):
        return "name: " + self.name + ", dpid: " + self.dpid + ", status: " + self.status


class Host( NetworkElement ):

    def __init__( self, index, name, id, mac, device, devicePort, vlan, ipAddresses ):
        NetworkElement.__init__( self, index )
        self.name = name
        self.id = id
        self.mac = mac
        self.device = device
        self.devicePort = devicePort
        self.vlan = vlan
        self.ipAddresses = ipAddresses
        self.correspondents = []
        self.handle = None

    def __str__( self ):
        return "name: " + self.name + ", mac: " + self.mac + ", device: " + self.device.dpid + ", ipAddresses: " + str( self.ipAddresses ) + ", status: " + self.status

    def setHandle( self, handle ):
        self.handle = handle


class Link( NetworkElement ):

    """
    Unidirectional link
    """
    def __init__( self, index, deviceA, portA, deviceB, portB ):
        NetworkElement.__init__( self, index )
        self.backwardLink = None
        self.deviceA = deviceA
        self.portA = portA
        self.deviceB = deviceB
        self.portB = portB

    def __str__( self ):
        return self.deviceA.dpid + "/" + self.portA + " - " + self.deviceB.dpid + "/" + self.portB + ", status: " + self.status

    def setBackwardLink( self, link ):
        self.backwardLink = link
