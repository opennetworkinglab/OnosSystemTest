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
        hostB = random.sample( candidates, 1 )[0]
        return hostB

    def getRandomHostPair( self, connected=True ):
        import random
        candidateDict = {}
        with main.variableLock:
            for host in main.hosts:
                correspondent = self.getRandomCorrespondent( host, connected=connected )
                if correspondent != None:
                    candidateDict[ host ] = correspondent
            if candidateDict == {}:
                return None
            hostA = random.sample( candidateDict.keys(), 1 )[0]
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
            main.log.info( "%s - starting event" % ( self.typeString ) )
            if self.typeIndex == EventType().APP_INTENT_HOST_ADD or self.typeIndex == EventType().APP_INTENT_HOST_DEL:
                if len( args ) < 3:
                    main.log.warn( "%s - Not enough arguments: %s" % ( self.typeString, args ) )
                    return EventStates().ABORT
                elif len( args ) > 3:
                    main.log.warn( "%s - Too many arguments: %s" % ( self.typeString, args ) )
                    return EventStates().ABORT
                if args[ 0 ] == 'random' or args[ 1 ] == 'random':
                    if self.typeIndex == EventType().APP_INTENT_HOST_ADD:
                        hostPairRandom = self.getRandomHostPair( connected=False )
                        if hostPairRandom == None:
                            main.log.warn( "All host pairs are connected, aborting event" )
                            return EventStates().ABORT
                        self.hostA = hostPairRandom[ 0 ]
                        self.hostB = hostPairRandom[ 1 ]
                    elif self.typeIndex == EventType().APP_INTENT_HOST_DEL:
                        intent = self.getRandomIntentByType( 'INTENT_HOST' )
                        if intent == None:
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
                        if self.hostA != None and self.hostB != None:
                            break
                    if self.hostA == None:
                        main.log.warn( "Host %s does not exist: " % ( args[ 0 ] ) )
                        return EventStates().ABORT
                    if self.hostB == None:
                        main.log.warn( "Host %s does not exist: " % ( args[ 1 ] ) )
                        return EventStates().ABORT
                index = int( args[ 2 ] )
                if index < 1 or index > int( main.numCtrls ):
                    main.log.warn( "%s - invalid argument: %s" % ( self.typeString, index ) )
                    return EventStates().ABORT
                if not main.controllers[ index - 1 ].isUp():
                    main.log.warn( self.typeString + " - invalid argument: onos %s is down" % ( controller.index ) )
                    return EventStates().ABORT
                self.CLIIndex = index
                return self.startHostIntentEvent()

class AddHostIntent( HostIntentEvent ):
    """
    Add a host-to-host intent (bidirectional)
    """
    def __init__( self ):
        HostIntentEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex= int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startHostIntentEvent( self ):
        try:
            assert self.hostA != None and self.hostB != None
            # Check whether there already exists some intent for the host pair
            # For now we should avoid installing overlapping intents
            for intent in main.intents:
                if not intent.type == 'INTENT_HOST':
                    continue
                if intent.hostA == self.hostA and intent.hostB == self.hostB or\
                intent.hostB == self.hostA and intent.hostA == self.hostB:
                    main.log.warn( self.typeString + " - find an exiting intent for the host pair, abort installation" )
                    return EventStates().ABORT
            controller = main.controllers[ self.CLIIndex - 1 ]
            with controller.CLILock:
                id = controller.CLI.addHostIntent( self.hostA.id, self.hostB.id )
            if id == None:
                main.log.warn( self.typeString + " - add host intent failed" )
                return EventStates().FAIL
            with main.variableLock:
                newHostIntent = HostIntent( id, self.hostA, self.hostB )
                if self.hostA.isDown() or self.hostA.isRemoved() or self.hostB.isDown() or self.hostB.isRemoved():
                    newHostIntent.setFailed()
                main.intents.append( newHostIntent )
                # Update host connectivity status
                # TODO: should we check whether hostA and hostB are already correspondents?
                self.hostB.correspondents.append( self.hostA )
                self.hostA.correspondents.append( self.hostB )
            return EventStates().PASS
        except Exception:
            main.log.warn( "Caught exception, aborting event" )
            return EventStates().ABORT

class DelHostIntent( HostIntentEvent ):
    """
    Delete a host-to-host intent (bidirectional)
    """
    def __init__( self ):
        HostIntentEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex= int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startHostIntentEvent( self ):
        try:
            assert self.hostA != None and self.hostB != None
            targetIntent = None
            for intent in main.intents:
                if not intent.type == 'INTENT_HOST':
                    continue
                if intent.hostA == self.hostA and intent.hostB == self.hostB or\
                intent.hostB == self.hostA and intent.hostA == self.hostB:
                    targetIntent = intent
                    break
            if targetIntent == None:
                main.log.warn( self.typeString + " - intent does not exist" )
                return EventStates().FAIL
            controller = main.controllers[ self.CLIIndex - 1 ]
            with controller.CLILock:
                result = controller.CLI.removeIntent( targetIntent.id, purge=True )
            if result == None or result == main.FALSE:
                main.log.warn( self.typeString + " - delete host intent failed" )
                return EventStates().FAIL
            with main.variableLock:
                main.intents.remove( targetIntent )
                # Update host connectivity status
                self.hostB.correspondents.remove( self.hostA )
                self.hostA.correspondents.remove( self.hostB )
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
            main.log.info( "%s - starting event" % ( self.typeString ) )
            if self.typeIndex == EventType().APP_INTENT_POINT_ADD or self.typeIndex == EventType().APP_INTENT_POINT_DEL:
                if len( args ) < 3:
                    main.log.warn( "%s - Not enough arguments: %s" % ( self.typeString, args ) )
                    return EventStates().ABORT
                elif len( args ) > 4:
                    main.log.warn( "%s - Too many arguments: %s" % ( self.typeString, args ) )
                    return EventStates().ABORT
                if args[ 0 ] == 'random' or args[ 1 ] == 'random':
                    if self.typeIndex == EventType().APP_INTENT_POINT_ADD:
                        hostPairRandom = self.getRandomHostPair( connected=False )
                        if hostPairRandom == None:
                            main.log.warn( "All host pairs are connected, aborting event" )
                            return EventStates().ABORT
                        self.deviceA = hostPairRandom[ 0 ].device
                        self.deviceB = hostPairRandom[ 1 ].device
                    elif self.typeIndex == EventType().APP_INTENT_POINT_DEL:
                        intent = self.getRandomIntentByType( 'INTENT_POINT' )
                        if intent == None:
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
                        if self.deviceA != None and self.deviceB != None:
                            break
                    if self.deviceA == None:
                        main.log.warn( "Device %s does not exist: " % ( args[ 0 ] ) )
                        return EventStates().ABORT
                    if self.deviceB == None:
                        main.log.warn( "Device %s does not exist: " % ( args[ 1 ] ) )
                        return EventStates().ABORT
                index = int( args[ 2 ] )
                if index < 1 or index > int( main.numCtrls ):
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

class AddPointIntent( PointIntentEvent ):
    """
    Add a point-to-point intent
    """
    def __init__( self ):
        PointIntentEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex= int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startPointIntentEvent( self ):
        try:
            assert self.deviceA != None and self.deviceB != None
            controller = main.controllers[ self.CLIIndex - 1 ]
            # TODO: the following check only work when we use default port number for point intents
            # Check whether there already exists some intent for the device pair
            # For now we should avoid installing overlapping intents
            for intent in main.intents:
                if not intent.type == 'INTENT_POINT':
                    continue
                if intent.deviceA == self.deviceA and intent.deviceB == self.deviceB:
                    main.log.warn( self.typeString + " - find an exiting intent for the device pair, abort installation" )
                    return EventStates().ABORT
            controller = main.controllers[ self.CLIIndex - 1 ]
            with controller.CLILock:
                # TODO: handle the case that multiple hosts attach to one device
                srcMAC = ""
                dstMAC = ""
                if len( self.deviceA.hosts ) > 0:
                    srcMAC = self.deviceA.hosts[ 0 ].mac
                if len( self.deviceB.hosts ) > 0:
                    dstMAC = self.deviceB.hosts[ 0 ].mac
                id = controller.CLI.addPointIntent( self.deviceA.dpid, self.deviceB.dpid,
                                                    1, 1, '', srcMAC, dstMAC )
            if id == None:
                main.log.warn( self.typeString + " - add point intent failed" )
                return EventStates().FAIL
            with main.variableLock:
                newPointIntent = PointIntent( id, self.deviceA, self.deviceB )
                if self.deviceA.isDown() or self.deviceB.isDown() or self.deviceA.isRemoved() or self.deviceB.isRemoved():
                    newPointIntent.setFailed()
                main.intents.append( newPointIntent )
                # Update host connectivity status
                for hostA in self.deviceA.hosts:
                    for hostB in self.deviceB.hosts:
                        hostA.correspondents.append( hostB )
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
        self.typeIndex= int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startPointIntentEvent( self ):
        try:
            assert self.deviceA != None and self.deviceB != None
            targetIntent = None
            for intent in main.intents:
                if not intent.type == 'INTENT_POINT':
                    continue
                if intent.deviceA == self.deviceA and intent.deviceB == self.deviceB:
                    targetIntent = intent
                    break
            if targetIntent == None:
                main.log.warn( self.typeString + " - intent does not exist" )
                return EventStates().FAIL
            controller = main.controllers[ self.CLIIndex - 1 ]
            with controller.CLILock:
                result = controller.CLI.removeIntent( targetIntent.id, purge=True )
            if result == None or result == main.FALSE:
                main.log.warn( self.typeString + " - delete point intent failed" )
                return EventStates().FAIL
            with main.variableLock:
                main.intents.remove( targetIntent )
                # Update host connectivity status
                for hostA in self.deviceA.hosts:
                    for hostB in self.deviceB.hosts:
                        hostA.correspondents.remove( hostB )
            return EventStates().PASS
        except Exception:
            main.log.warn( "Caught exception, aborting event" )
            return EventStates().ABORT
