"""
This file contains the event generator class for CHOTestMonkey
Author: you@onlab.us
"""
from threading import Lock, Condition
from tests.CHOTestMonkey.dependencies.events.Event import EventType, EventStates, Event
from tests.CHOTestMonkey.dependencies.EventScheduler import EventScheduleMethod
from tests.CHOTestMonkey.dependencies.GraphHelper import GraphHelper

class MessageType:
    def __init__( self ):
        self.map = {}
        # This message type is used for requesting an event injection from outside CHOTestMonkey
        self.EVENT_REQUEST = 1
        self.map[ 1 ] = 'EVENT_REQUEST'
        # This message tyoe will force the event generator to accept the event injection request for debugging purpose
        self.EVENT_REQUEST_DEBUG = 2
        self.map[ 2 ] = 'EVENT_REQUEST_DEBUG'
        # This message type implies the event generator has inserted the event
        self.EVENT_INSERTED = 10
        self.map[ 10 ] = 'EVENT_INSERTED'
        # This message type implies CHOTestMonkey has refused the event injection request
        # due to, e.g. too many pending events in the scheduler
        self.EVENT_DENIED = 11
        self.map[ 11 ] = 'EVENT_DENIED'
        # The followings are error messages
        self.UNKNOWN_MESSAGE = 20
        self.map[ 20 ] = 'UNKNOWN_MESSAGE'
        self.UNKNOWN_EVENT_TYPE = 21
        self.map[ 21 ] = 'UNKNOWN_EVENT_TYPE'
        self.UNKNOWN_SCHEDULE_METHOD = 22
        self.map[ 22 ] = 'UNKNOWN_SCHEDULE_METHOD'
        self.NOT_ENOUGH_ARGUMENT = 23
        self.map[ 23 ] = 'NOT_ENOUGH_ARGUMENT'

class EventGenerator:
    def __init__( self ):
        self.default = ''
        self.eventGeneratorLock = Lock()

    def startListener( self ):
        """
        Listen to event triggers
        """
        from multiprocessing.connection import Listener
        import time

        host = "localhost"
        port = int( main.params[ 'GENERATOR' ][ 'listenerPort' ] )
        address = ( host, port )
        listener = Listener( address )
        main.log.info( "Event Generator - Event listener start listening on %s:%s" % ( host, port ) )

        while 1:
            conn = listener.accept()
            t = main.Thread( target=self.handleConnection,
                             threadID=main.threadID,
                             name="handleConnection",
                             args=[ conn ])
            t.start()
            with main.variableLock:
                main.threadID += 1
        listener.close()

    def handleConnection( self, conn ):
        """
        Handle connections from event triggers
        """
        request = conn.recv()
        if isinstance( request, list ) and ( request[ 0 ] == MessageType().EVENT_REQUEST or request[ 0 ] == MessageType().EVENT_REQUEST_DEBUG ):
            if len( request ) < 3:
                response = MessageType().NOT_ENOUGH_ARGUMENT
            elif request[ 0 ] == MessageType().EVENT_REQUEST and not main.eventScheduler.isAvailable():
                response = MessageType().EVENT_DENIED
            else:
                typeString = str( request[ 1 ] )
                scheduleMethodString = str( request[ 2 ] )
                if len( request ) > 3:
                    args = request[ 3: ]
                else:
                    args = None
                for key, value in EventType().map.items():
                    if value == typeString:
                        typeIndex = key
                        break
                if not value == typeString:
                    response = MessageType().UNKNOWN_EVENT_TYPE
                else:
                    for key, value in EventScheduleMethod().map.items():
                        if value == scheduleMethodString:
                            scheduleMethod = key
                            break
                    if not value == scheduleMethodString:
                        response = MessageType().UNKNOWN_SCHEDULE_METHOD
                    else:
                        self.insertEvent( typeIndex, scheduleMethod, args )
                        response = MessageType().EVENT_INSERTED
        else:
            response = MessageType().UNKNOWN_MESSAGE
        conn.send( response )
        conn.close()

    def triggerEvent( self, typeIndex, scheduleMethod, *args ):
        """
        This function triggers an event from inside of CHOTestMonkey
        """
        import time
        if not typeIndex in EventType().map.keys():
            main.log.warn( "Event Generator - Unknown event type: " + str( typeIndex ) )
            return
        if not scheduleMethod in EventScheduleMethod().map.keys():
            main.log.warn( "Event Generator - Unknown event schedule method: " + str( scheduleMethod ) )
            return
        while not main.eventScheduler.isAvailable():
            time.sleep( int( main.params[ 'GENERATOR' ][ 'insertEventRetryInterval' ] ) )
        self.insertEvent( typeIndex, scheduleMethod, list( args ) )

    def insertEvent( self, typeIndex, scheduleMethod, args=None ):
        """
        This function inserts an event into the scheduler
        """
        if typeIndex > 100:
            # Handle group events
            if not typeIndex in main.enabledEvents.keys():
                main.log.warn( "Event Generator - event type %s not enabled" % ( typeIndex ) )
                return
            function = getattr( self, main.enabledEvents[ typeIndex ] )
            assert function != None, "Event Generator - funtion for group event " + typeIndex + " not found"
            function( scheduleMethod, args )
        else:
            # Add individual events to the scheduler
            main.eventScheduler.scheduleEvent( typeIndex, scheduleMethod, args )

    def insertAllChecks( self, args=None ):
        """
        Acquire eventGeneratorLock before calling this funtion
        """
        for eventType in main.enabledEvents.keys():
            if eventType < 100 and EventType().map[ eventType ].startswith( 'CHECK' ):
                main.eventScheduler.scheduleEvent( eventType,
                                                   EventScheduleMethod().RUN_NON_BLOCK,
                                                   args )

    def addAllChecks( self, scheduleMethod, args=None ):
        """
        The function adds all check events into the scheduler
        """
        with self.eventGeneratorLock:
            if scheduleMethod == EventScheduleMethod().RUN_BLOCK:
                main.eventScheduler.scheduleEvent( EventType().NULL, EventScheduleMethod().RUN_BLOCK )
            self.insertAllChecks( args )
            if scheduleMethod == EventScheduleMethod().RUN_BLOCK:
                main.eventScheduler.scheduleEvent( EventType().NULL, EventScheduleMethod().RUN_BLOCK )

    def randomLinkToggle( self, scheduleMethod, args=[ 5 ], blocking=True ):
        """
        The function randomly adds a link down-up event pair into the scheduler
        After each individual link event, all checks are inserted into the scheduler
        param:
            args[0] is the average interval between link down and link up events
            blocking means blocking other events from being scheduled between link down and link up
        """
        import random
        import time

        if len( args ) < 1:
            main.log.warn( "Event Generator - Not enough arguments for randomLinkToggle: %s" % ( args ) )
        elif len( args ) > 1:
            main.log.warn( "Event Generator - Too many arguments for randomLinkToggle: %s" % ( args ) )
        else:
            downUpAvgInterval = int( args[ 0 ] )
        with main.variableLock:
            graphHelper = GraphHelper()
            availableLinks = graphHelper.getNonCutEdges()
            if len( availableLinks ) == 0:
                main.log.warn( "All links are cut edges, aborting event" )
                return
            link = random.sample( availableLinks, 1 )

        self.eventGeneratorLock.acquire()
        main.eventScheduler.scheduleEvent( EventType().NETWORK_LINK_DOWN,
                                           scheduleMethod,
                                           [ link[ 0 ].deviceA.name, link[ 0 ].deviceB.name ] )
        with main.variableLock:
            link[ 0 ].setPendingDown()
            link[ 0 ].backwardLink.setPendingDown()
        sleepTime = int( main.params[ 'EVENT' ][ 'randomLinkToggle' ][ 'sleepBeforeCheck' ] )
        main.eventScheduler.scheduleEvent( EventType().TEST_SLEEP, EventScheduleMethod().RUN_BLOCK, [ sleepTime ] )
        self.insertAllChecks( EventScheduleMethod().RUN_NON_BLOCK )
        if scheduleMethod == EventScheduleMethod().RUN_BLOCK:
            # Insert a NULL BLOCK event
            main.eventScheduler.scheduleEvent( EventType().NULL, EventScheduleMethod().RUN_BLOCK )
        downUpInterval = abs( random.gauss( downUpAvgInterval, 1 ) )
        if not blocking:
            self.eventGeneratorLock.release()
            time.sleep( downUpInterval )
            self.eventGeneratorLock.acquire()
        else:
            time.sleep( downUpInterval )
        main.eventScheduler.scheduleEvent( EventType().NETWORK_LINK_UP,
                                           scheduleMethod,
                                           [ link[ 0 ].deviceA.name, link[ 0 ].deviceB.name ] )
        main.eventScheduler.scheduleEvent( EventType().TEST_SLEEP, EventScheduleMethod().RUN_BLOCK, [ sleepTime ] )
        self.insertAllChecks( EventScheduleMethod().RUN_NON_BLOCK )
        if scheduleMethod == EventScheduleMethod().RUN_BLOCK:
            main.eventScheduler.scheduleEvent( EventType().NULL, EventScheduleMethod().RUN_BLOCK )
        self.eventGeneratorLock.release()

    def randomLinkGroupToggle( self, scheduleMethod, args=None, blocking=True ):
        """
        The function randomly adds a group of link down-up events into the scheduler
        After each link down or up, all checks are inserted into the scheduler
        param:
            args[0] is the number of links that are to be brought down
            args[1] is the average interval between link down events
            args[2] is the average interval between link group down and group up events
            blocking means blocking other events from being scheduled between link events
        """
        import random
        import time

        if len( args ) < 3:
            main.log.warn( "Event Generator - Not enough arguments for randomLinkGroupToggle: %s" % ( args ) )
        elif len( args ) > 3:
            main.log.warn( "Event Generator - Too many arguments for randomLinkGroupToggle: %s" % ( args ) )
        else:
            linkGroupSize = int( args[ 0 ] )
            downDownAvgInterval = int( args[ 1 ] )
            downUpAvgInterval = int( args[ 2 ] )
        downLinks = []
        for i in range( 0, linkGroupSize ):
            with main.variableLock:
                graphHelper = GraphHelper()
                availableLinks = graphHelper.getNonCutEdges()
                if len( availableLinks ) == 0:
                    main.log.warn( "All links are cut edges, aborting event" )
                    continue
                link = random.sample( availableLinks, 1 )
            if i == 0:
                self.eventGeneratorLock.acquire()
            main.eventScheduler.scheduleEvent( EventType().NETWORK_LINK_DOWN,
                                               scheduleMethod,
                                               [ link[ 0 ].deviceA.name, link[ 0 ].deviceB.name ] )
            with main.variableLock:
                link[ 0 ].setPendingDown()
                link[ 0 ].backwardLink.setPendingDown()
            downLinks.append( link[ 0 ] )
            sleepTime = int( main.params[ 'EVENT' ][ 'randomLinkGroupToggle' ][ 'sleepBeforeCheck' ] )
            main.eventScheduler.scheduleEvent( EventType().TEST_SLEEP, EventScheduleMethod().RUN_BLOCK, [ sleepTime ] )
            self.insertAllChecks( EventScheduleMethod().RUN_NON_BLOCK )
            if scheduleMethod == EventScheduleMethod().RUN_BLOCK:
                # Insert a NULL BLOCK event
                main.eventScheduler.scheduleEvent( EventType().NULL, EventScheduleMethod().RUN_BLOCK )
            downDownInterval = abs( random.gauss( downDownAvgInterval, 1 ) )
            if not blocking:
                self.eventGeneratorLock.release()
                time.sleep( downDownInterval )
                self.eventGeneratorLock.acquire()
            else:
                time.sleep( downDownInterval )

        downUpInterval = abs( random.gauss( downUpAvgInterval, 1 ) )
        if not blocking:
            self.eventGeneratorLock.release()
            time.sleep( downUpInterval )
            self.eventGeneratorLock.acquire()
        else:
            time.sleep( downUpInterval )

        for link in downLinks:
            main.eventScheduler.scheduleEvent( EventType().NETWORK_LINK_UP,
                                               scheduleMethod,
                                               [ link.deviceA.name, link.deviceB.name ] )
            main.eventScheduler.scheduleEvent( EventType().TEST_SLEEP, EventScheduleMethod().RUN_BLOCK, [ sleepTime ] )
            self.insertAllChecks( EventScheduleMethod().RUN_NON_BLOCK )
            if scheduleMethod == EventScheduleMethod().RUN_BLOCK:
                main.eventScheduler.scheduleEvent( EventType().NULL, EventScheduleMethod().RUN_BLOCK )
            upUpInterval = abs( random.gauss( downDownAvgInterval, 1 ) )
            if not blocking:
                self.eventGeneratorLock.release()
                time.sleep( upUpInterval )
                self.eventGeneratorLock.acquire()
            else:
                time.sleep( upUpInterval )
        self.eventGeneratorLock.release()

    def randomDeviceToggle( self, scheduleMethod, args=[ 5 ], blocking=True ):
        """
        The function randomly removes a device and then adds it back
        After each individual device event, all checks are inserted into the scheduler
        param:
            args[0] is the average interval between device down and device up events
            blocking means blocking other events from being scheduled between device down and device up
        """
        import random
        import time

        if len( args ) < 1:
            main.log.warn( "Event Generator - Not enough arguments for randomDeviceToggle: %s" % ( args ) )
        elif len( args ) > 1:
            main.log.warn( "Event Generator - Too many arguments for randomDeviceToggle: %s" % ( args ) )
        else:
            downUpAvgInterval = int( args[ 0 ] )
        with main.variableLock:
            graphHelper = GraphHelper()
            availableDevices = graphHelper.getNonCutVertices()
            if len( availableDevices ) == 0:
                main.log.warn( "All devices are Cut vertices, aborting event" )
                return
            device = random.sample( availableDevices, 1 )

        self.eventGeneratorLock.acquire()
        main.eventScheduler.scheduleEvent( EventType().NETWORK_DEVICE_DOWN,
                                           scheduleMethod,
                                           [ device[ 0 ].name ] )
        with main.variableLock:
            device[ 0 ].setPendingDown()
        sleepTime = int( main.params[ 'EVENT' ][ 'randomLinkToggle' ][ 'sleepBeforeCheck' ] )
        main.eventScheduler.scheduleEvent( EventType().TEST_SLEEP, EventScheduleMethod().RUN_BLOCK, [ sleepTime ] )
        self.insertAllChecks( EventScheduleMethod().RUN_NON_BLOCK )
        if scheduleMethod == EventScheduleMethod().RUN_BLOCK:
            # Insert a NULL BLOCK event
            main.eventScheduler.scheduleEvent( EventType().NULL, EventScheduleMethod().RUN_BLOCK )
        downUpInterval = abs( random.gauss( downUpAvgInterval, 1 ) )
        if not blocking:
            self.eventGeneratorLock.release()
            time.sleep( downUpInterval )
            self.eventGeneratorLock.acquire()
        else:
            time.sleep( downUpInterval )
        main.eventScheduler.scheduleEvent( EventType().NETWORK_DEVICE_UP,
                                           scheduleMethod,
                                           [ device[ 0 ].name ] )
        main.eventScheduler.scheduleEvent( EventType().TEST_SLEEP, EventScheduleMethod().RUN_BLOCK, [ sleepTime ] )
        self.insertAllChecks( EventScheduleMethod().RUN_NON_BLOCK )
        if scheduleMethod == EventScheduleMethod().RUN_BLOCK:
            main.eventScheduler.scheduleEvent( EventType().NULL, EventScheduleMethod().RUN_BLOCK )
        self.eventGeneratorLock.release()

    def randomDeviceGroupToggle( self, scheduleMethod, args=None, blocking=True ):
        """
        The function randomly adds a group of device down-up events into the scheduler
        After each device down or up, all checks are inserted into the scheduler
        param:
            args[0] is the number of devices that are to be brought down
            args[1] is the average interval between device down events
            args[2] is the average interval between device group down and group up events
            blocking means blocking other events from being scheduled between device events
        """
        import random
        import time

        if len( args ) < 3:
            main.log.warn( "Event Generator - Not enough arguments for randomDeviceGroupToggle: %s" % ( args ) )
        elif len( args ) > 3:
            main.log.warn( "Event Generator - Too many arguments for randomDeviceGroupToggle: %s" % ( args ) )
        else:
            deviceGroupSize = int( args[ 0 ] )
            downDownAvgInterval = int( args[ 1 ] )
            downUpAvgInterval = int( args[ 2 ] )
        downDevices = []
        for i in range( 0, deviceGroupSize ):
            with main.variableLock:
                graphHelper = GraphHelper()
                availableDevices = graphHelper.getNonCutVertices()
                if len( availableDevices ) == 0:
                    main.log.warn( "All devices are cut vertices, aborting event" )
                    continue
                device = random.sample( availableDevices, 1 )
            if i == 0:
                self.eventGeneratorLock.acquire()
            main.eventScheduler.scheduleEvent( EventType().NETWORK_DEVICE_DOWN,
                                               scheduleMethod,
                                               [ device[ 0 ].name ] )
            with main.variableLock:
                device[ 0 ].setPendingDown()
            downDevices.append( device[ 0 ] )
            sleepTime = int( main.params[ 'EVENT' ][ 'randomLinkGroupToggle' ][ 'sleepBeforeCheck' ] )
            main.eventScheduler.scheduleEvent( EventType().TEST_SLEEP, EventScheduleMethod().RUN_BLOCK, [ sleepTime ] )
            self.insertAllChecks( EventScheduleMethod().RUN_NON_BLOCK )
            if scheduleMethod == EventScheduleMethod().RUN_BLOCK:
                # Insert a NULL BLOCK event
                main.eventScheduler.scheduleEvent( EventType().NULL, EventScheduleMethod().RUN_BLOCK )
            downDownInterval = abs( random.gauss( downDownAvgInterval, 1 ) )
            if not blocking:
                self.eventGeneratorLock.release()
                time.sleep( downDownInterval )
                self.eventGeneratorLock.acquire()
            else:
                time.sleep( downDownInterval )

        downUpInterval = abs( random.gauss( downUpAvgInterval, 1 ) )
        if not blocking:
            self.eventGeneratorLock.release()
            time.sleep( downUpInterval )
            self.eventGeneratorLock.acquire()
        else:
            time.sleep( downUpInterval )

        for device in downDevices:
            main.eventScheduler.scheduleEvent( EventType().NETWORK_DEVICE_UP,
                                               scheduleMethod,
                                               [ device.name ] )
            main.eventScheduler.scheduleEvent( EventType().TEST_SLEEP, EventScheduleMethod().RUN_BLOCK, [ sleepTime ] )
            self.insertAllChecks( EventScheduleMethod().RUN_NON_BLOCK )
            if scheduleMethod == EventScheduleMethod().RUN_BLOCK:
                main.eventScheduler.scheduleEvent( EventType().NULL, EventScheduleMethod().RUN_BLOCK )
            upUpInterval = abs( random.gauss( downDownAvgInterval, 1 ) )
            if not blocking:
                self.eventGeneratorLock.release()
                time.sleep( upUpInterval )
                self.eventGeneratorLock.acquire()
            else:
                time.sleep( upUpInterval )
        self.eventGeneratorLock.release()

    def installAllHostIntents( self, scheduleMethod, args=None ):
        """
        This function installs host intents for all host pairs
        After all intent events are inserted, this funciton also insert intent and traffic checks
        """
        import itertools

        with self.eventGeneratorLock:
            if scheduleMethod == EventScheduleMethod().RUN_BLOCK:
                main.eventScheduler.scheduleEvent( EventType().NULL, EventScheduleMethod().RUN_BLOCK )
            availableControllers = []
            for controller in main.controllers:
                if controller.isUp():
                    availableControllers.append( controller.index )
            if len( availableControllers ) == 0:
                main.log.warn( "Event Generator - No available controllers" )
                return
            hostCombos = list( itertools.combinations( main.hosts, 2 ) )
            for i in xrange( 0, len( hostCombos ), len( availableControllers ) ):
                for CLIIndex in availableControllers:
                    if i >= len( hostCombos ):
                        break
                    main.eventScheduler.scheduleEvent( EventType().APP_INTENT_HOST_ADD,
                                                       EventScheduleMethod().RUN_NON_BLOCK,
                                                       [ hostCombos[ i ][ 0 ].name, hostCombos[ i ][ 1 ].name, CLIIndex ] )
                    i += 1
            # Pending checks after installing all intents
            if scheduleMethod == EventScheduleMethod().RUN_BLOCK:
                main.eventScheduler.scheduleEvent( EventType().NULL, EventScheduleMethod().RUN_BLOCK )
            sleepTime = int( main.params[ 'EVENT' ][ 'installAllHostIntents' ][ 'sleepBeforeCheck' ] )
            main.eventScheduler.scheduleEvent( EventType().TEST_SLEEP, EventScheduleMethod().RUN_BLOCK, [ sleepTime ] )
            main.eventScheduler.scheduleEvent( EventType().CHECK_INTENT, EventScheduleMethod().RUN_NON_BLOCK )
            main.eventScheduler.scheduleEvent( EventType().CHECK_FLOW, EventScheduleMethod().RUN_NON_BLOCK )
            main.eventScheduler.scheduleEvent( EventType().CHECK_TRAFFIC, EventScheduleMethod().RUN_NON_BLOCK )
            if scheduleMethod == EventScheduleMethod().RUN_BLOCK:
                main.eventScheduler.scheduleEvent( EventType().NULL, EventScheduleMethod().RUN_BLOCK )

    def removeAllHostIntents( self, scheduleMethod, args=None ):
        """
        This function removes host intents for all host pairs
        After all intent events are inserted, this funciton also insert intent and traffic checks
        """
        import itertools

        with self.eventGeneratorLock:
            if scheduleMethod == EventScheduleMethod().RUN_BLOCK:
                main.eventScheduler.scheduleEvent( EventType().NULL, EventScheduleMethod().RUN_BLOCK )
            availableControllers = []
            for controller in main.controllers:
                if controller.isUp():
                    availableControllers.append( controller.index )
            if len( availableControllers ) == 0:
                main.log.warn( "Event Generator - No available controllers" )
                return
            hostCombos = list( itertools.combinations( main.hosts, 2 ) )
            for i in xrange( 0, len( hostCombos ), len( availableControllers ) ):
                for CLIIndex in availableControllers:
                    if i >= len( hostCombos ):
                        break
                    main.eventScheduler.scheduleEvent( EventType().APP_INTENT_HOST_DEL,
                                                       EventScheduleMethod().RUN_NON_BLOCK,
                                                       [ hostCombos[ i ][ 0 ].name, hostCombos[ i ][ 1 ].name, CLIIndex ] )
                    i += 1
            # Pending checks after removing all intents
            if scheduleMethod == EventScheduleMethod().RUN_BLOCK:
                main.eventScheduler.scheduleEvent( EventType().NULL, EventScheduleMethod().RUN_BLOCK )
            sleepTime = int( main.params[ 'EVENT' ][ 'removeAllHostIntents' ][ 'sleepBeforeCheck' ] )
            main.eventScheduler.scheduleEvent( EventType().TEST_SLEEP, EventScheduleMethod().RUN_BLOCK, [ sleepTime ] )
            main.eventScheduler.scheduleEvent( EventType().CHECK_INTENT, EventScheduleMethod().RUN_NON_BLOCK )
            main.eventScheduler.scheduleEvent( EventType().CHECK_FLOW, EventScheduleMethod().RUN_NON_BLOCK )
            main.eventScheduler.scheduleEvent( EventType().CHECK_TRAFFIC, EventScheduleMethod().RUN_NON_BLOCK )
            if scheduleMethod == EventScheduleMethod().RUN_BLOCK:
                main.eventScheduler.scheduleEvent( EventType().NULL, EventScheduleMethod().RUN_BLOCK )

    def installAllPointIntents( self, scheduleMethod, args=None ):
        """
        This function installs point intents for all device pairs
        After all intent events are inserted, this funciton also insert intent and traffic checks
        """
        import itertools

        with self.eventGeneratorLock:
            if scheduleMethod == EventScheduleMethod().RUN_BLOCK:
                main.eventScheduler.scheduleEvent( EventType().NULL, EventScheduleMethod().RUN_BLOCK )
            availableControllers = []
            for controller in main.controllers:
                if controller.isUp():
                    availableControllers.append( controller.index )
            if len( availableControllers ) == 0:
                main.log.warn( "Event Generator - No available controllers" )
                return
            deviceCombos = list( itertools.permutations( main.devices, 2 ) )
            for i in xrange( 0, len( deviceCombos ), len( availableControllers ) ):
                for CLIIndex in availableControllers:
                    if i >= len( deviceCombos ):
                        break
                    main.eventScheduler.scheduleEvent( EventType().APP_INTENT_POINT_ADD,
                                                       EventScheduleMethod().RUN_NON_BLOCK,
                                                       [ deviceCombos[ i ][ 0 ].name, deviceCombos[ i ][ 1 ].name, CLIIndex ] )
                    i += 1
            # Pending checks after installing all intents
            if scheduleMethod == EventScheduleMethod().RUN_BLOCK:
                main.eventScheduler.scheduleEvent( EventType().NULL, EventScheduleMethod().RUN_BLOCK )
            sleepTime = int( main.params[ 'EVENT' ][ 'installAllPointIntents' ][ 'sleepBeforeCheck' ] )
            main.eventScheduler.scheduleEvent( EventType().TEST_SLEEP, EventScheduleMethod().RUN_BLOCK, [ sleepTime ] )
            main.eventScheduler.scheduleEvent( EventType().CHECK_INTENT, EventScheduleMethod().RUN_NON_BLOCK )
            main.eventScheduler.scheduleEvent( EventType().CHECK_FLOW, EventScheduleMethod().RUN_NON_BLOCK )
            main.eventScheduler.scheduleEvent( EventType().CHECK_TRAFFIC, EventScheduleMethod().RUN_NON_BLOCK )
            if scheduleMethod == EventScheduleMethod().RUN_BLOCK:
                main.eventScheduler.scheduleEvent( EventType().NULL, EventScheduleMethod().RUN_BLOCK )

    def removeAllPointIntents( self, scheduleMethod, args=None ):
        """
        This function removes point intents for all device pairs
        After all intent events are inserted, this funciton also insert intent and traffic checks
        """
        import itertools

        with self.eventGeneratorLock:
            if scheduleMethod == EventScheduleMethod().RUN_BLOCK:
                main.eventScheduler.scheduleEvent( EventType().NULL, EventScheduleMethod().RUN_BLOCK )
            availableControllers = []
            for controller in main.controllers:
                if controller.isUp():
                    availableControllers.append( controller.index )
            if len( availableControllers ) == 0:
                main.log.warn( "Event Generator - No available controllers" )
                return
            deviceCombos = list( itertools.permutations( main.devices, 2 ) )
            for i in xrange( 0, len( deviceCombos ), len( availableControllers ) ):
                for CLIIndex in availableControllers:
                    if i >= len( deviceCombos ):
                        break
                    main.eventScheduler.scheduleEvent( EventType().APP_INTENT_POINT_DEL,
                                                       EventScheduleMethod().RUN_NON_BLOCK,
                                                       [ deviceCombos[ i ][ 0 ].name, deviceCombos[ i ][ 1 ].name, CLIIndex ] )
                    i += 1
            # Pending checks after removing all intents
            if scheduleMethod == EventScheduleMethod().RUN_BLOCK:
                main.eventScheduler.scheduleEvent( EventType().NULL, EventScheduleMethod().RUN_BLOCK )
            sleepTime = int( main.params[ 'EVENT' ][ 'removeAllPointIntents' ][ 'sleepBeforeCheck' ] )
            main.eventScheduler.scheduleEvent( EventType().TEST_SLEEP, EventScheduleMethod().RUN_BLOCK, [ sleepTime ] )
            main.eventScheduler.scheduleEvent( EventType().CHECK_INTENT, EventScheduleMethod().RUN_NON_BLOCK )
            main.eventScheduler.scheduleEvent( EventType().CHECK_FLOW, EventScheduleMethod().RUN_NON_BLOCK )
            main.eventScheduler.scheduleEvent( EventType().CHECK_TRAFFIC, EventScheduleMethod().RUN_NON_BLOCK )
            if scheduleMethod == EventScheduleMethod().RUN_BLOCK:
                main.eventScheduler.scheduleEvent( EventType().NULL, EventScheduleMethod().RUN_BLOCK )
