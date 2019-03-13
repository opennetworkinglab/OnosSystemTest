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
This file contains classes for CHOTestMonkey that are related to network event
Author: you@onlab.us
"""
from tests.CHOTestMonkey.dependencies.events.Event import EventType, EventStates, Event
from tests.CHOTestMonkey.dependencies.elements.NetworkElement import NetworkElement, Device, Host, Link
import time


class LinkEvent( Event ):

    def __init__( self ):
        Event.__init__( self )
        self.linkA = None
        self.linkB = None

    def startLinkEvent( self ):
        return EventStates().PASS

    def startEvent( self, args ):
        """
        args are the names of the two link ends, e.g. [ 's1', 's2' ]
        """
        with self.eventLock:
            # main.log.info( "%s - starting event" % ( self.typeString ) )
            if len( args ) < 2:
                main.log.warn( "%s - Not enough arguments: %s" % ( self.typeString, args ) )
                return EventStates().ABORT
            elif len( args ) > 2:
                main.log.warn( "%s - Too many arguments: %s" % ( self.typeString, args ) )
                return EventStates().ABORT
            if args[ 0 ] == 'random' or args[ 1 ] == 'random':
                if self.typeIndex == EventType().NETWORK_LINK_DOWN:
                    with main.networkLock:
                        linkRandom = main.Network.getLinkRandom( excludeNodes=main.excludeNodes,
                                                                 skipLinks=main.skipLinks )
                    if linkRandom is None:
                        main.log.warn( "No link available, aborting event" )
                        return EventStates().ABORT
                    args[ 0 ] = linkRandom[ 0 ]
                    args[ 1 ] = linkRandom[ 1 ]
                elif self.typeIndex == EventType().NETWORK_LINK_UP:
                    import random
                    with main.variableLock:
                        downLinks = []
                        for link in main.links:
                            if link.isDown():
                                downLinks.append( link )
                        if len( downLinks ) == 0:
                            main.log.warn( "None of the links are in 'down' state, aborting event" )
                            return EventStates().ABORT
                        linkList = random.sample( downLinks, 1 )
                        self.linkA = linkList[ 0 ]
                        self.linkB = linkList[ 0 ].backwardLink
            elif args[ 0 ] == args[ 1 ]:
                main.log.warn( "%s - invalid arguments: %s" % ( self.typeString, args ) )
                return EventStates().ABORT
            if self.linkA is None or self.linkB is None:
                for link in main.links:
                    if link.deviceA.name == args[ 0 ] and link.deviceB.name == args[ 1 ]:
                        self.linkA = link
                    elif link.deviceA.name == args[ 1 ] and link.deviceB.name == args[ 0 ]:
                        self.linkB = link
                    if self.linkA is not None and self.linkB is not None:
                        break
                if self.linkA is None or self.linkB is None:
                    main.log.warn( "Bidirectional link %s - %s does not exist: " % ( args[ 0 ], args[ 1 ] ) )
                    return EventStates().ABORT
            main.log.debug( "%s - %s" % ( self.typeString, self.linkA ) )
            return self.startLinkEvent()


class LinkDown( LinkEvent ):

    """
    Generate a link down event giving the two ends of the link
    """
    def __init__( self ):
        LinkEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startLinkEvent( self ):
        # TODO: do we need to handle a unidirectional link?
        assert self.linkA is not None and self.linkB is not None
        with main.variableLock:
            if self.linkA.isDown() or self.linkB.isDown():
                main.log.warn( "Link Down - link already down" )
                return EventStates().ABORT
            elif self.linkA.isRemoved() or self.linkB.isRemoved():
                main.log.warn( "Link Down - link has been removed" )
                return EventStates().ABORT
        main.log.info( "Event recorded: {} {} {} {}".format( self.typeIndex, self.typeString, self.linkA.deviceA.name, self.linkA.deviceB.name ) )
        with main.networkLock:
            """
            result = main.Network.link( END1=self.linkA.deviceA.name,
                                        END2=self.linkA.deviceB.name,
                                        OPTION="down" )
            """
            result = main.Network.delLink( self.linkA.deviceA.name,
                                           self.linkA.deviceB.name )
        if not result:
            main.log.warn( "%s - failed to bring down link" % ( self.typeString ) )
            return EventStates().FAIL
        with main.variableLock:
            self.linkA.bringDown()
            self.linkB.bringDown()
        return EventStates().PASS


class LinkUp( LinkEvent ):

    """
    Generate a link up event giving the two ends of the link
    """
    def __init__( self ):
        LinkEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startLinkEvent( self ):
        assert self.linkA is not None and self.linkB is not None
        with main.variableLock:
            if self.linkA.isUp() or self.linkB.isUp():
                main.log.warn( "Link Up - link already up" )
                return EventStates().ABORT
            if self.linkA.isRemoved() or self.linkB.isRemoved():
                main.log.warn( "Link Up - link has been removed" )
                return EventStates().ABORT
        main.log.info( "Event recorded: {} {} {} {}".format( self.typeIndex, self.typeString, self.linkA.deviceA.name, self.linkA.deviceB.name ) )
        with main.networkLock:
            """
            result = main.Network.link( END1=self.linkA.deviceA.name,
                                        END2=self.linkA.deviceB.name,
                                        OPTION="up" )
            """
            result = main.Network.addLink( self.linkA.deviceA.name,
                                           self.linkA.deviceB.name )
        if not result:
            main.log.warn( "%s - failed to bring up link" % ( self.typeString ) )
            return EventStates().FAIL
        with main.variableLock:
            self.linkA.bringUp()
            self.linkB.bringUp()
        return EventStates().PASS


class DeviceEvent( Event ):

    def __init__( self ):
        Event.__init__( self )
        self.device = None

    def startDeviceEvent( self ):
        return EventStates().PASS

    def startEvent( self, args ):
        """
        args are the names of the device, e.g. 's1'
        """
        with self.eventLock:
            # main.log.info( "%s - starting event" % ( self.typeString ) )
            if len( args ) < 1:
                main.log.warn( "%s - Not enough arguments: %s" % ( self.typeString, args ) )
                return EventStates().ABORT
            elif len( args ) > 1:
                main.log.warn( "%s - Too many arguments: %s" % ( self.typeString, args ) )
                return EventStates().ABORT
            if args[ 0 ] == 'random':
                import random
                if self.typeIndex == EventType().NETWORK_DEVICE_DOWN:
                    with main.networkLock:
                        switchRandom = main.Network.getSwitchRandom( excludeNodes=main.excludeNodes,
                                                                     skipSwitches=main.skipSwitches )
                    if switchRandom is None:
                        main.log.warn( "No switch available, aborting event" )
                        return EventStates().ABORT
                    args[ 0 ] = switchRandom
                elif self.typeIndex == EventType().NETWORK_DEVICE_UP:
                    with main.variableLock:
                        removedDevices = []
                        for device in main.devices:
                            if device.isRemoved():
                                removedDevices.append( device )
                        if len( removedDevices ) == 0:
                            main.log.warn( "None of the devices are removed, aborting event" )
                            return EventStates().ABORT
                        deviceList = random.sample( removedDevices, 1 )
                        self.device = deviceList[ 0 ]
            if self.device is None:
                for device in main.devices:
                    if device.name == args[ 0 ]:
                        self.device = device
                if self.device is None:
                    main.log.warn( "Device %s does not exist: " % ( args[ 0 ] ) )
                    return EventStates().ABORT
            main.log.debug( "%s - %s" % ( self.typeString, self.device ) )
            return self.startDeviceEvent()


class DeviceDown( DeviceEvent ):

    """
    Generate a device down event ( which actually removes this device for now ) giving its name
    """
    def __init__( self ):
        DeviceEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startDeviceEvent( self ):
        assert self.device is not None
        with main.variableLock:
            if self.device.isRemoved():
                main.log.warn( "Device Down - device has been removed" )
                return EventStates().ABORT
        main.log.info( "Event recorded: {} {} {}".format( self.typeIndex, self.typeString, self.device.name ) )
        result = main.TRUE
        with main.networkLock:
            # Disable ports toward dual-homed hosts
            for host, port in self.device.hosts.items():
                if host.isDualHomed:
                    main.log.info( "Disable port {}/{} which connects to a dual-homed host before bringing down this device".format( self.device.dpid, port ) )
                    result = result and main.Cluster.active( 0 ).CLI.portstate( dpid=self.device.dpid, port=port, state="disable" )
            # result = main.Network.delSwitch( self.device.name )
            result = result and main.Network.switch( SW=self.device.name, OPTION="stop" )
        if not result:
            main.log.warn( "%s - failed to bring down device" % ( self.typeString ) )
            return EventStates().FAIL
        with main.variableLock:
            self.device.setRemoved()
            for link in self.device.outgoingLinks:
                link.setRemoved()
                link.backwardLink.setRemoved()
            for host in self.device.hosts:
                host.setRemoved()
            for intent in main.intents:
                if intent.deviceA == self.device or intent.deviceB == self.device:
                    intent.setFailed()
        return EventStates().PASS


class DeviceUp( DeviceEvent ):

    """
    Generate a device up event ( which re-adds this device in case the device is removed ) giving its name
    """
    def __init__( self ):
        DeviceEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startDeviceEvent( self ):
        assert self.device is not None
        with main.variableLock:
            if self.device.isUp():
                main.log.warn( "Device Up - device already up" )
                return EventStates().ABORT
        # Re-add the device
        main.log.info( "Event recorded: {} {} {}".format( self.typeIndex, self.typeString, self.device.name ) )
        if hasattr( main, 'Mininet1' ):
            with main.networkLock:
                # result = main.Network.addSwitch( self.device.name, dpid=self.device.dpid[ 3: ] )
                result = main.Network.switch( SW=self.device.name, OPTION='start' )
            if not result:
                main.log.warn( "%s - failed to re-add device" % ( self.typeString ) )
                return EventStates().FAIL
        # Re-assign mastership for the device
        with main.networkLock:
            result = main.Network.assignSwController( sw=self.device.name, ip=main.Cluster.getIps() )
            if not result:
                main.log.warn( "%s - failed to assign device to controller" % ( self.typeString ) )
                return EventStates().FAIL
        with main.variableLock:
            self.device.bringUp()
        for link in self.device.outgoingLinks:
            neighbor = link.deviceB
            # Skip bringing up any link that connecting this device to a removed neighbor
            if neighbor.isRemoved():
                continue
            # FIXME: remove this temporary hack for CORD-3240
            if neighbor.name == 's225':
                time.sleep( 5 )
                main.NetworkBench.switches[ 's225' ].setPortSpeed( index=link.portB )
            # Bring down again any link that was brought down before the device was down
            if int( link.portB ) in link.deviceB.downPorts:
                with main.variableLock:
                    link.bringDown()
                    link.backwardLink.bringDown()
            else:
                with main.variableLock:
                    link.bringUp()
                    link.backwardLink.bringUp()
        # Re-discover hosts
        if self.device.hosts:
            main.Network.discoverHosts( hostList=[ host.name for host in self.device.hosts ] )
        for host in self.device.hosts:
            with main.variableLock:
                host.bringUp()
        self.device.downPorts = []
        return EventStates().PASS


class PortEvent( Event ):

    def __init__( self ):
        Event.__init__( self )
        self.device = None
        self.port = None
        self.link = None

    def startPortEvent( self ):
        return EventStates().PASS

    def startEvent( self, args ):
        """
        args are the device name and port number, e.g. [ 's1', '5' ]
        """
        with self.eventLock:
            # main.log.info( "%s - starting event" % ( self.typeString ) )
            if len( args ) < 2:
                main.log.warn( "%s - Not enough arguments: %s" % ( self.typeString, args ) )
                return EventStates().ABORT
            elif len( args ) > 2:
                main.log.warn( "%s - Too many arguments: %s" % ( self.typeString, args ) )
                return EventStates().ABORT
            if args[ 0 ] == 'random' or args[ 1 ] == 'random':
                if self.typeIndex == EventType().NETWORK_PORT_DOWN:
                    with main.networkLock:
                        linkRandom = main.Network.getLinkRandom( excludeNodes=main.excludeNodes,
                                                                 skipLinks=main.skipLinks )
                    if linkRandom is None:
                        main.log.warn( "No link available, aborting event" )
                        return EventStates().ABORT
                    for link in main.links:
                        if link.deviceA.name == linkRandom[ 0 ] and link.deviceB.name == linkRandom[ 1 ]:
                            self.device = link.deviceA
                            self.port = int( link.portA )
                    if not self.device:
                        main.log.warn( "Failed to get a radnom device port, aborting event" )
                        return EventStates().ABORT
                elif self.typeIndex == EventType().NETWORK_PORT_UP:
                    import random
                    with main.variableLock:
                        downPorts = {}
                        for link in main.links:
                            if link.isDown():
                                if int( link.portA ) in link.deviceA.downPorts:
                                    downPorts[ link.deviceA ] = link.portA
                        if len( downPorts ) == 0:
                            main.log.warn( "None of the links are in 'down' state, aborting event" )
                            return EventStates().ABORT
                        deviceList = random.sample( downPorts, 1 )
                        self.device = deviceList[ 0 ]
                        self.port = int( downPorts[ self.device ] )
            if self.device is None:
                for device in main.devices:
                    if device.name == args[ 0 ]:
                        self.device = device
                if self.device is None:
                    main.log.warn( "Device %s does not exist: " % ( args[ 0 ] ) )
                    return EventStates().ABORT
            if self.port is None:
                try:
                    self.port = int( args[ 1 ] )
                except Exception:
                    main.log.warn( "Device port is not a number: {}".format( args[ 1 ] ) )
                    return EventStates().ABORT
            if self.link is None:
                for link in main.links:
                    if link.deviceA.name == self.device.name and int( link.portA ) == self.port:
                        self.link = link
                if self.link is None:
                    main.log.warn( "There's no link on device {} port {}".format( self.device.name, self.port ) )
                    return EventStates().ABORT
            main.log.debug( "%s - %s:%s" % ( self.typeString, self.device, self.port ) )
            return self.startPortEvent()


class PortDown( PortEvent ):

    """
    Generate a port down event giving the device name and port number
    """
    def __init__( self ):
        PortEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startPortEvent( self ):
        assert self.device is not None and self.port is not None and self.link is not None
        if self.link.isDown():
            main.log.warn( "port Down - link already down" )
            return EventStates().ABORT
        elif self.link.isRemoved():
            main.log.warn( "port Down - link has been removed" )
            return EventStates().ABORT
        main.log.info( "Event recorded: {} {} {} {}".format( self.typeIndex, self.typeString, self.device.name, self.port ) )
        with main.networkLock:
            result = main.Cluster.active( 0 ).CLI.portstate( dpid=self.device.dpid, port=self.port, state="disable" )
        if not result:
            main.log.warn( "%s - failed to bring down port" % ( self.typeString ) )
            return EventStates().FAIL
        with main.variableLock:
            self.device.downPorts.append( self.port )
            self.link.bringDown()
            self.link.backwardLink.bringDown()
        return EventStates().PASS


class PortUp( PortEvent ):

    """
    Generate a port up event giving the device name and port number
    """
    def __init__( self ):
        PortEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startPortEvent( self ):
        assert self.device is not None and self.port is not None and self.link is not None
        if self.link.isUp():
            main.log.warn( "port up - link already up" )
            return EventStates().ABORT
        elif self.link.isRemoved():
            main.log.warn( "port up - link has been removed" )
            return EventStates().ABORT
        main.log.info( "Event recorded: {} {} {} {}".format( self.typeIndex, self.typeString, self.device.name, self.port ) )
        with main.networkLock:
            result = main.Cluster.active( 0 ).CLI.portstate( dpid=self.device.dpid, port=self.port, state="enable" )
        if not result:
            main.log.warn( "%s - failed to bring up port " % ( self.typeString ) )
            return EventStates().FAIL
        # FIXME: remove this temporary hack for CORD-3240
        if self.link.deviceB.name == 's225':
            main.NetworkBench.switches[ 's225' ].setPortSpeed( index=self.link.portB )
        with main.variableLock:
            self.device.downPorts.remove( self.port )
            self.link.bringUp()
            self.link.backwardLink.bringUp()
        return EventStates().PASS
