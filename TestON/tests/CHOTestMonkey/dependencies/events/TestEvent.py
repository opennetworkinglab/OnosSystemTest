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
