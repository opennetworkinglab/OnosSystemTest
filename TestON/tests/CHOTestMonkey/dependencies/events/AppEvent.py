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
This file contains classes for CHOTestMonkey that are related to application event
Author: you@onlab.us
"""
from tests.CHOTestMonkey.dependencies.events.Event import EventType, EventStates, Event
from tests.CHOTestMonkey.dependencies.elements.ONOSElement import HostIntent, PointIntent


class IntentEvent( Event ):

    def __init__( self ):
        Event.__init__( self )
        # The index of the ONOS CLI that is going to run the command
        self.CLIIndex = 0

    def getRandomCorrespondent( self, hostA, connected=True ):
        import random
        if connected:
            candidates = hostA.correspondents
        else:
            candidates = [ host for host in main.hosts if host not in hostA.correspondents and host != hostA ]
        if len( candidates ) == 0:
            return None
        hostB = random.sample( candidates, 1 )[ 0 ]
        return hostB

    def getRandomHostPair( self, connected=True ):
        import random
        candidateDict = {}
        with main.variableLock:
            for host in main.hosts:
                correspondent = self.getRandomCorrespondent( host, connected=connected )
                if correspondent is not None:
                    candidateDict[ host ] = correspondent
            if candidateDict == {}:
                return None
            hostA = random.sample( candidateDict.keys(), 1 )[ 0 ]
            hostB = candidateDict[ hostA ]
            return [ hostA, hostB ]

    def getIntentsByType( self, intentType ):
        intents = []
        with main.variableLock:
            for intent in main.intents:
                if intent.type == intentType:
                    intents.append( intent )
        return intents

    def getRandomIntentByType( self, intentType ):
        import random
        intents = self.getIntentsByType( intentType )
        if len( intents ) == 0:
            return None
        intent = random.sample( intents, 1 )[ 0 ]
        return intent


class HostIntentEvent( IntentEvent ):

    def __init__( self ):
        IntentEvent.__init__( self )
        self.hostA = None
        self.hostB = None

    def startHostIntentEvent( self ):
        return EventStates().PASS

    def startEvent( self, args ):
        with self.eventLock:
            # main.log.info( "%s - starting event" % ( self.typeString ) )
            if self.typeIndex == EventType().APP_INTENT_HOST_ADD or self.typeIndex == EventType().APP_INTENT_HOST_DEL:
                if len( args ) < 3:
                    main.log.warn( "%s - Not enough arguments: %s" % ( self.typeString, args ) )
                    return EventStates().ABORT
                elif len( args ) > 3:
                    main.log.warn( "%s - Too many arguments: %s" % ( self.typeString, args ) )
                    return EventStates().ABORT
                try:
                    if args[ 0 ] == 'random' or args[ 1 ] == 'random':
                        if self.typeIndex == EventType().APP_INTENT_HOST_ADD:
                            hostPairRandom = self.getRandomHostPair( connected=False )
                            if hostPairRandom is None:
                                main.log.warn( "All host pairs are connected, aborting event" )
                                return EventStates().ABORT
                            self.hostA = hostPairRandom[ 0 ]
                            self.hostB = hostPairRandom[ 1 ]
                        elif self.typeIndex == EventType().APP_INTENT_HOST_DEL:
                            intent = self.getRandomIntentByType( 'INTENT_HOST' )
                            if intent is None:
                                main.log.warn( "No host intent for deletion, aborting event" )
                                return EventStates().ABORT
                            self.hostA = intent.hostA
                            self.hostB = intent.hostB
                    elif args[ 0 ] == args[ 1 ]:
                        main.log.warn( "%s - invalid argument: %s, %s" % ( self.typeString, args[ 0 ], args[ 1 ] ) )
                        return EventStates().ABORT
                    else:
                        for host in main.hosts:
                            if host.name == args[ 0 ]:
                                self.hostA = host
                            elif host.name == args[ 1 ]:
                                self.hostB = host
                            if self.hostA is not None and self.hostB is not None:
                                break
                        if self.hostA is None:
                            main.log.warn( "Host %s does not exist: " % ( args[ 0 ] ) )
                            return EventStates().ABORT
                        if self.hostB is None:
                            main.log.warn( "Host %s does not exist: " % ( args[ 1 ] ) )
                            return EventStates().ABORT
                    index = int( args[ 2 ] )
                    if index < 1 or index > int( main.Cluster.numCtrls ):
                        main.log.warn( "%s - invalid argument: %s" % ( self.typeString, index ) )
                        return EventStates().ABORT
                    if not main.controllers[ index - 1 ].isUp():
                        main.log.warn( self.typeString + " - invalid argument: onos %s is down" % ( controller.index ) )
                        return EventStates().ABORT
                    self.CLIIndex = index
                    return self.startHostIntentEvent()
                except Exception:
                    main.log.warn( "Caught exception, aborting event" )
                    return EventStates().ABORT


class AddHostIntent( HostIntentEvent ):

    """
    Add a host-to-host intent ( bidirectional )
    """
    def __init__( self ):
        HostIntentEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startHostIntentEvent( self ):
        try:
            assert self.hostA is not None and self.hostB is not None
            # Check whether there already exists some intent for the host pair
            # For now we should avoid installing overlapping intents
            for intent in main.intents:
                if not intent.type == 'INTENT_HOST':
                    continue
                if intent.hostA == self.hostA and intent.hostB == self.hostB or\
                        intent.hostB == self.hostA and intent.hostA == self.hostB:
                    main.log.warn( self.typeString + " - find an exiting intent for the host pair, abort installation" )
                    return EventStates().ABORT
            main.log.info( "Event recorded: {} {} {} {} {}".format( self.typeIndex, self.typeString, self.hostA.name, self.hostB.name, self.CLIIndex ) )
            controller = main.controllers[ self.CLIIndex - 1 ]
            with controller.CLILock:
                id = controller.CLI.addHostIntent( self.hostA.id, self.hostB.id )
            if id is None:
                main.log.warn( self.typeString + " - add host intent failed" )
                return EventStates().FAIL
            with main.variableLock:
                newHostIntent = HostIntent( id, self.hostA, self.hostB )
                if self.hostA.isDown() or self.hostA.isRemoved() or self.hostB.isDown() or self.hostB.isRemoved():
                    newHostIntent.setFailed()
                else:
                    newHostIntent.setInstalled()
                main.intents.append( newHostIntent )
            return EventStates().PASS
        except Exception:
            main.log.warn( "Caught exception, aborting event" )
            return EventStates().ABORT


class DelHostIntent( HostIntentEvent ):

    """
    Delete a host-to-host intent ( bidirectional )
    """
    def __init__( self ):
        HostIntentEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startHostIntentEvent( self ):
        try:
            assert self.hostA is not None and self.hostB is not None
            targetIntent = None
            for intent in main.intents:
                if not intent.type == 'INTENT_HOST':
                    continue
                if intent.hostA == self.hostA and intent.hostB == self.hostB or\
                        intent.hostB == self.hostA and intent.hostA == self.hostB:
                    targetIntent = intent
                    break
            if targetIntent is None:
                main.log.warn( self.typeString + " - intent does not exist" )
                return EventStates().FAIL
            main.log.info( "Event recorded: {} {} {} {} {}".format( self.typeIndex, self.typeString, self.hostA.name, self.hostB.name, self.CLIIndex ) )
            controller = main.controllers[ self.CLIIndex - 1 ]
            with controller.CLILock:
                result = controller.CLI.removeIntent( targetIntent.id, purge=True )
            if result is None or result == main.FALSE:
                main.log.warn( self.typeString + " - delete host intent failed" )
                return EventStates().FAIL
            with main.variableLock:
                targetIntent.setWithdrawn()
                main.intents.remove( targetIntent )
            return EventStates().PASS
        except Exception:
            main.log.warn( "Caught exception, aborting event" )
            return EventStates().ABORT


class PointIntentEvent( IntentEvent ):

    def __init__( self ):
        IntentEvent.__init__( self )
        self.deviceA = None
        self.deviceB = None

    def startPointIntentEvent( self ):
        return EventStates().PASS

    def startEvent( self, args ):
        with self.eventLock:
            # main.log.info( "%s - starting event" % ( self.typeString ) )
            if self.typeIndex == EventType().APP_INTENT_POINT_ADD or self.typeIndex == EventType().APP_INTENT_POINT_DEL:
                if len( args ) < 3:
                    main.log.warn( "%s - Not enough arguments: %s" % ( self.typeString, args ) )
                    return EventStates().ABORT
                elif len( args ) > 4:
                    main.log.warn( "%s - Too many arguments: %s" % ( self.typeString, args ) )
                    return EventStates().ABORT
                try:
                    if args[ 0 ] == 'random' or args[ 1 ] == 'random':
                        if self.typeIndex == EventType().APP_INTENT_POINT_ADD:
                            hostPairRandom = self.getRandomHostPair( connected=False )
                            if hostPairRandom is None:
                                main.log.warn( "All host pairs are connected, aborting event" )
                                return EventStates().ABORT
                            self.deviceA = hostPairRandom[ 0 ].device
                            self.deviceB = hostPairRandom[ 1 ].device
                        elif self.typeIndex == EventType().APP_INTENT_POINT_DEL:
                            intent = self.getRandomIntentByType( 'INTENT_POINT' )
                            if intent is None:
                                main.log.warn( "No point intent for deletion, aborting event" )
                                return EventStates().ABORT
                            self.deviceA = intent.deviceA
                            self.deviceB = intent.deviceB
                    elif args[ 0 ] == args[ 1 ]:
                        main.log.warn( "%s - invalid argument: %s" % ( self.typeString, args[ 0 ], args[ 1 ] ) )
                        return EventStates().ABORT
                    else:
                        for device in main.devices:
                            if device.name == args[ 0 ]:
                                self.deviceA = device
                            elif device.name == args[ 1 ]:
                                self.deviceB = device
                            if self.deviceA is not None and self.deviceB is not None:
                                break
                        if self.deviceA is None:
                            main.log.warn( "Device %s does not exist: " % ( args[ 0 ] ) )
                            return EventStates().ABORT
                        if self.deviceB is None:
                            main.log.warn( "Device %s does not exist: " % ( args[ 1 ] ) )
                            return EventStates().ABORT
                    index = int( args[ 2 ] )
                    if index < 1 or index > int( main.Cluster.numCtrls ):
                        main.log.warn( "%s - invalid argument: %s" % ( self.typeString, index ) )
                        return EventStates().ABORT
                    if not main.controllers[ index - 1 ].isUp():
                        main.log.warn( self.typeString + " - invalid argument: onos %s is down" % ( controller.index ) )
                        return EventStates().ABORT
                    self.CLIIndex = index
                    if len( args ) == 4 and args[ 3 ] == 'bidirectional':
                        # Install point intents for both directions
                        resultA = self.startPointIntentEvent()
                        [ self.deviceA, self.deviceB ] = [ self.deviceB, self.deviceA ]
                        resultB = self.startPointIntentEvent()
                        if resultA == EventStates().PASS and resultB == EventStates().PASS:
                            return EventStates().PASS
                        else:
                            return EventStates().FAIL
                    else:
                        return self.startPointIntentEvent()
                except Exception:
                    main.log.warn( "Caught exception, aborting event" )
                    return EventStates().ABORT


class AddPointIntent( PointIntentEvent ):

    """
    Add a point-to-point intent
    """
    def __init__( self ):
        PointIntentEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startPointIntentEvent( self ):
        try:
            assert self.deviceA is not None and self.deviceB is not None
            controller = main.controllers[ self.CLIIndex - 1 ]
            # TODO: support multiple hosts under one device
            # Check whether there already exists some intent for the device pair
            # For now we should avoid installing overlapping intents
            for intent in main.intents:
                if not intent.type == 'INTENT_POINT':
                    continue
                if intent.deviceA == self.deviceA and intent.deviceB == self.deviceB:
                    main.log.warn( self.typeString + " - find an exiting intent for the device pair, abort installation" )
                    return EventStates().ABORT
            main.log.info( "Event recorded: {} {} {} {} {}".format( self.typeIndex, self.typeString, self.deviceA.name, self.deviceB.name, self.CLIIndex ) )
            controller = main.controllers[ self.CLIIndex - 1 ]
            with controller.CLILock:
                srcMAC = ""
                dstMAC = ""
                if len( self.deviceA.hosts ) > 0:
                    srcMAC = self.deviceA.hosts[ 0 ].mac
                if len( self.deviceB.hosts ) > 0:
                    dstMAC = self.deviceB.hosts[ 0 ].mac
                id = controller.CLI.addPointIntent( self.deviceA.dpid, self.deviceB.dpid, 1, 1, '', srcMAC, dstMAC )
            if id is None:
                main.log.warn( self.typeString + " - add point intent failed" )
                return EventStates().FAIL
            with main.variableLock:
                newPointIntent = PointIntent( id, self.deviceA, self.deviceB )
                if self.deviceA.isDown() or self.deviceB.isDown() or self.deviceA.isRemoved() or self.deviceB.isRemoved():
                    newPointIntent.setFailed()
                else:
                    newPointIntent.setInstalled()
                main.intents.append( newPointIntent )
            return EventStates().PASS
        except Exception:
            main.log.warn( "Caught exception, aborting event" )
            return EventStates().ABORT


class DelPointIntent( PointIntentEvent ):

    """
    Delete a point-to-point intent
    """
    def __init__( self ):
        PointIntentEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startPointIntentEvent( self ):
        try:
            assert self.deviceA is not None and self.deviceB is not None
            targetIntent = None
            for intent in main.intents:
                if not intent.type == 'INTENT_POINT':
                    continue
                if intent.deviceA == self.deviceA and intent.deviceB == self.deviceB:
                    targetIntent = intent
                    break
            if targetIntent is None:
                main.log.warn( self.typeString + " - intent does not exist" )
                return EventStates().FAIL
            main.log.info( "Event recorded: {} {} {} {} {}".format( self.typeIndex, self.typeString, self.deviceA.name, self.deviceB.name, self.CLIIndex ) )
            controller = main.controllers[ self.CLIIndex - 1 ]
            with controller.CLILock:
                result = controller.CLI.removeIntent( targetIntent.id, purge=True )
            if result is None or result == main.FALSE:
                main.log.warn( self.typeString + " - delete point intent failed" )
                return EventStates().FAIL
            with main.variableLock:
                targetIntent.setWithdrawn()
                main.intents.remove( targetIntent )
            return EventStates().PASS
        except Exception:
            main.log.warn( "Caught exception, aborting event" )
            return EventStates().ABORT
