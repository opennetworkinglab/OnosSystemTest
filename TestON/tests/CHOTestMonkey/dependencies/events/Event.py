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

"""
This file contains the Event class for CHOTestMonkey
Author: you@onlab.us
"""
from threading import Lock


class EventType:

    def __init__( self ):
        self.map = {}
        # Group events ( >100 ) should be divided into individual events by the generator before going to the scheduler
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
