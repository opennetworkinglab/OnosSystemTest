"""
This file contains the Event class for CHOTestMonkey
Author: you@onlab.us
"""
from threading import Lock

class EventType:
    def __init__( self ):
        self.map = {}
        # Group events (>100) should be divided into individual events by the generator before going to the scheduler
        self.NULL = 0
        for eventName in main.params[ 'EVENT' ].keys():
            typeString = main.params[ 'EVENT' ][ eventName ][ 'typeString' ]
            typeIndex = int( main.params[ 'EVENT' ][ eventName ][ 'typeIndex' ] )
            setattr( self, typeString, typeIndex )
            self.map[ typeIndex ] = typeString

class EventStates:
    def __init__( self ):
        self.map = {}
        self.FAIL = 0
        self.map[ 0 ] = 'FAIL'
        self.PASS = 1
        self.map[ 1 ] = 'PASS'
        self.ABORT = -1
        self.map[ -1 ] = 'ABORT'

class Event:
    """
    Event class for CHOTestMonkey
    It is the super class for CheckEvent and NetworkEvent
    """
    def __init__( self ):
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )
        self.eventLock = Lock()
        self.variableLock = Lock()

    def startEvent( self, args=None ):
        """
        Start running the event
        """
        return EventStates().PASS
