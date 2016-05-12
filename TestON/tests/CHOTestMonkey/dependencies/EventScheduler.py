"""
This file contains the event scheduler class for CHOTestMonkey
Author: you@onlab.us
"""
from threading import Lock, Condition
from tests.CHOTestMonkey.dependencies.events.Event import EventType, EventStates, Event
from tests.CHOTestMonkey.dependencies.events.TestEvent import *
from tests.CHOTestMonkey.dependencies.events.CheckEvent import *
from tests.CHOTestMonkey.dependencies.events.NetworkEvent import *
from tests.CHOTestMonkey.dependencies.events.AppEvent import *
from tests.CHOTestMonkey.dependencies.events.ONOSEvent import *

class EventScheduleMethod:
    def __init__( self ):
        self.map = {}
        self.RUN_NON_BLOCK = 1
        self.map[ 1 ] = 'RUN_NON_BLOCK'
        self.RUN_BLOCK = -1
        self.map[ -1 ] = 'RUN_BLOCK'

class EventTuple:
    def __init__( self, id, className, typeString, typeIndex, scheduleMethod, args, rerunInterval, maxRerunNum ):
        self.default = ''
        self.id = 0
        self.className = className
        self.typeString = typeString
        self.typeIndex = typeIndex
        self.scheduleMethod = scheduleMethod
        self.args = args
        self.rerunInterval = rerunInterval
        self.maxRerunNum = maxRerunNum

    def startEvent( self ):
        assert self.className in globals().keys()
        event = globals()[ self.className ]
        return event().startEvent( self.args )

class EventScheduler:
    def __init__( self ):
        self.default = ''
        self.pendingEvents = []
        self.pendingEventsCondition = Condition()
        self.runningEvents = []
        self.runningEventsCondition = Condition()
        self.isRunning = True
        self.idleCondition = Condition()
        self.pendingEventsCapacity = int( main.params[ 'SCHEDULER' ][ 'pendingEventsCapacity' ] )
        self.runningEventsCapacity = int( main.params[ 'SCHEDULER' ][ 'runningEventsCapacity' ] )
        self.scheduleLoopSleep = float( main.params[ 'SCHEDULER' ][ 'scheduleLoopSleep' ] )

    def scheduleEvent( self, typeIndex, scheduleMethod, args=None, index=-1 ):
        """
        Insert an event to pendingEvents
        param:
            index: the position to insert into pendingEvents, default value -1 implies the tail of pendingEvents
        """
        if not typeIndex in main.enabledEvents.keys():
            main.log.warn( "Event Scheduler - event type %s not enabled" % ( typeIndex ) )
            return
        if main.enabledEvents[ typeIndex ] in main.params[ 'EVENT' ].keys():
            if 'rerunInterval' in main.params[ 'EVENT' ][ main.enabledEvents[ typeIndex ] ].keys():
                rerunInterval = int( main.params[ 'EVENT' ][ main.enabledEvents[ typeIndex ] ][ 'rerunInterval' ] )
                maxRerunNum = int( main.params[ 'EVENT' ][ main.enabledEvents[ typeIndex ] ][ 'maxRerunNum' ] )
            else:
                rerunInterval = int( main.params[ 'EVENT' ][ 'Event' ][ 'rerunInterval' ] )
                maxRerunNum = int( main.params[ 'EVENT' ][ 'Event' ][ 'maxRerunNum' ] )
        eventTuple = EventTuple( main.eventID, main.enabledEvents[ typeIndex ], EventType().map[ typeIndex ], typeIndex, scheduleMethod, args, rerunInterval, maxRerunNum )
        with main.variableLock:
            main.eventID += 1
        main.log.debug( "Event Scheduler - Event added: %s, %s, %s" % ( typeIndex,
                                                                       scheduleMethod,
                                                                       args ) )
        with self.pendingEventsCondition:
            if index == -1:
                self.pendingEvents.append( eventTuple )
            elif index > -1 and index <= len( self.pendingEvents ):
                self.pendingEvents.insert( index, eventTuple )
            else:
                main.log.warn( "Event Scheduler - invalid index when isnerting event: %s" % ( index ) )
            self.pendingEventsCondition.notify()
        self.printEvents()

    def startScheduler( self ):
        """
        Start the loop which schedules the events in pendingEvents
        """
        import time

        while 1:
            with self.pendingEventsCondition:
                while len( self.pendingEvents ) == 0:
                    self.pendingEventsCondition.wait()
                eventTuple = self.pendingEvents[ 0 ]
            main.log.debug( "Event Scheduler - Scheduling event: %s, %s, %s" % ( eventTuple.typeIndex,
                                                                                eventTuple.scheduleMethod,
                                                                                eventTuple.args ) )
            if eventTuple.scheduleMethod == EventScheduleMethod().RUN_NON_BLOCK:
                # Run NON_BLOCK events using threads
                with self.pendingEventsCondition:
                    self.pendingEvents.remove( eventTuple )
                t = main.Thread( target=self.startEvent,
                                 threadID=main.threadID,
                                 name="startEvent",
                                 args=[ eventTuple ])
                t.start()
                with main.variableLock:
                    main.threadID += 1
            elif eventTuple.scheduleMethod == EventScheduleMethod().RUN_BLOCK:
                # Wait for all other events before start
                with self.runningEventsCondition:
                    while not len( self.runningEvents ) == 0:
                        self.runningEventsCondition.wait()
                # BLOCK events will temporarily block the following events until finish running
                with self.pendingEventsCondition:
                    self.pendingEvents.remove( eventTuple )
                self.startEvent( eventTuple )
            else:
                with self.pendingEventsCondition:
                    self.pendingEvents.remove( eventTuple )
            time.sleep( self.scheduleLoopSleep )

    def startEvent( self, eventTuple ):
        """
        Start a network/ONOS/application event
        """
        import time

        with self.runningEventsCondition:
            self.runningEvents.append( eventTuple )
        self.printEvents()
        rerunNum = 0
        result = eventTuple.startEvent()
        while result == EventStates().FAIL and rerunNum < eventTuple.maxRerunNum:
            time.sleep( eventTuple.rerunInterval )
            rerunNum += 1
            main.log.debug( eventTuple.typeString + ": retry number " + str( rerunNum ) )
            result = eventTuple.startEvent()
        if result == EventStates().FAIL:
            main.log.error( eventTuple.typeString + " failed" )
            main.caseResult = main.FALSE
            if main.params[ 'TEST' ][ 'pauseTest' ] == 'on':
                #self.isRunning = False
                #main.log.error( "Event Scheduler - Test paused. To resume test, run \'resume-test\' command in CLI debugging mode" )
                main.stop()
        with self.runningEventsCondition:
            self.runningEvents.remove( eventTuple )
            if len( self.runningEvents ) == 0:
                self.runningEventsCondition.notify()
                with self.pendingEventsCondition:
                    if len( self.pendingEvents ) == 0:
                        with self.idleCondition:
                            self.idleCondition.notify()
        self.printEvents()

    def printEvents( self ):
        """
        Print all the events in pendingEvents and runningEvents
        """
        events = " ["
        with self.runningEventsCondition:
            for index in range( 0, len( self.runningEvents ) - 1 ):
                events += str( self.runningEvents[ index ].typeIndex )
                events += ", "
            if len( self.runningEvents ) > 0:
                events += str( self.runningEvents[ -1 ].typeIndex )
        events += "]"
        events += " ["
        with self.pendingEventsCondition:
            for index in range( 0, len( self.pendingEvents ) - 1 ):
                events += str( self.pendingEvents[ index ].typeIndex )
                events += ", "
            if len( self.pendingEvents ) > 0:
                events += str( self.pendingEvents[ -1 ].typeIndex )
        events += "]"
        main.log.debug( "Event Scheduler - Events: " + events )

    def isAvailable( self ):
        with self.pendingEventsCondition:
            with self.runningEventsCondition:
                return len( self.pendingEvents ) < self.pendingEventsCapacity and\
                       len( self.runningEvents ) < self.runningEventsCapacity and\
                       self.isRunning

    def isIdle( self ):
        with self.pendingEventsCondition:
            with self.runningEventsCondition:
                return len( self.pendingEvents ) == 0 and\
                       len( self.runningEvents ) == 0 and\
                       self.isRunning

    def setPendingEventsCapacity( self, capacity ):
        self.pendingEventsCapacity = capacity

    def setRunningState( self, state ):
        assert state == True or state == False
        self.isRunning = state

