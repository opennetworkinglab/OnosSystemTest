"""
This file contains classes for CHOTestMonkey that are related to check event
Author: you@onlab.us
"""
from tests.CHOTestMonkey.dependencies.events.Event import EventType, EventStates, Event

class TestEvent( Event ):
    def __init__( self ):
        Event.__init__( self )

    def startTestEvent( self ):
        return EventStates().PASS

    def startEvent( self, args ):
        with self.eventLock:
            main.log.info( "%s - starting event" % ( self.typeString ) )
            result = self.startTestEvent( args )
            return result

class TestPause( TestEvent ):
    def __init__( self ):
        TestEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startTestEvent( self, args=None ):
        result = EventStates().PASS
        main.eventScheduler.setRunningState( False )
        return result

class TestResume( TestEvent ):
    def __init__( self ):
        TestEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startTestEvent( self, args=None ):
        result = EventStates().PASS
        main.eventScheduler.setRunningState( True )
        return result

class TestSleep( TestEvent ):
    def __init__( self ):
        TestEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startTestEvent( self, args ):
        import time
        result = EventStates().PASS
        if len( args ) < 1:
            main.log.warn( "%s - Not enough arguments: %s" % ( self.typeString, args ) )
            result = EventStates().ABORT
        elif len( args ) > 1:
            main.log.warn( "%s - Too many arguments: %s" % ( self.typeString, args ) )
            result = EventStates().ABORT
        sleepTime = int( args[ 0 ] )
        time.sleep( sleepTime )
        return result
