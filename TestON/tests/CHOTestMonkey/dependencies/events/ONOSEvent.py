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
This file contains classes for CHOTestMonkey that are related to application event
Author: you@onlab.us
"""
from tests.CHOTestMonkey.dependencies.events.Event import EventType, EventStates, Event


class ONOSEvent( Event ):

    def __init__( self ):
        Event.__init__( self )
        self.ONOSIndex = -1

    def startEvent( self, args ):
        with self.eventLock:
            #main.log.info( "%s - starting event" % ( self.typeString ) )
            result = EventStates().PASS
            if self.typeIndex == EventType().ONOS_ONOS_DOWN or self.typeIndex == EventType().ONOS_ONOS_UP:
                if len( args ) < 1:
                    main.log.warn( "%s - Not enough arguments: %s" % ( self.typeString, args ) )
                    result = EventStates().ABORT
                elif len( args ) > 1:
                    main.log.warn( "%s - Too many arguments: %s" % ( self.typeString, args ) )
                    result = EventStates().ABORT
                else:
                    index = int( args[ 0 ] )
                    if index < 1 or index > int( main.numCtrls ):
                        main.log.warn( "%s - invalid argument: %s" % ( self.typeString, index ) )
                        result = EventStates().ABORT
                    else:
                        self.ONOSIndex = index
                        result = self.startONOSEvent()
            return result


class ONOSDown( ONOSEvent ):

    def __init__( self ):
        ONOSEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startONOSEvent( self ):
        assert self.ONOSIndex != -1
        with main.variableLock:
            if not main.controllers[ self.ONOSIndex - 1 ].isUp():
                main.log.warn( "ONOS Down - ONOS already down" )
                return EventStates().ABORT
        main.log.info( "Event recorded: {} {} {}".format( self.typeIndex, self.typeString, self.ONOSIndex ) )
        with main.ONOSbenchLock:
            result = main.ONOSbench.onosStop( main.controllers[ self.ONOSIndex - 1 ].ip )
        if not result:
            main.log.warn( "%s - failed to bring down ONOS" % ( self.typeString ) )
            return EventStates().FAIL
        with main.variableLock:
            main.controllers[ self.ONOSIndex - 1 ].bringDown()
        return EventStates().PASS


class ONOSUp( ONOSEvent ):

    def __init__( self ):
        ONOSEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startONOSEvent( self ):
        assert self.ONOSIndex != -1
        with main.variableLock:
            if main.controllers[ self.ONOSIndex - 1 ].isUp():
                main.log.warn( "ONOS Up - ONOS already up" )
                return EventStates().ABORT
        main.log.info( "Event recorded: {} {} {}".format( self.typeIndex, self.typeString, self.ONOSIndex ) )
        with main.ONOSbenchLock:
            startResult = main.ONOSbench.onosStart( main.controllers[ self.ONOSIndex - 1 ].ip )
        if not startResult:
            main.log.warn( "%s - failed to bring up ONOS" % ( self.typeString ) )
            return EventStates().FAIL
        else:
            ONOSState = main.ONOSbench.isup( main.controllers[ self.ONOSIndex - 1 ].ip )
            if not ONOSState:
                main.log.warn( "%s - ONOS is not up" % ( self.typeString ) )
                return EventStates().FAIL
            else:
                cliResult = main.controllers[ self.ONOSIndex - 1 ].startCLI()
                if not cliResult:
                    main.log.warn( "%s - failed to start ONOS cli" % ( self.typeString ) )
                    return EventStates().FAIL
                else:
                    with main.variableLock:
                        main.controllers[ self.ONOSIndex - 1 ].bringUp()
        return EventStates().PASS


class CfgEvent( Event ):

    def __init__( self ):
        Event.__init__( self )
        self.component = ''
        self.propName = ''
        self.value = ''

    def startEvent( self, args ):
        with self.eventLock:
            #main.log.info( "%s - starting event" % ( self.typeString ) )
            result = self.startCfgEvent( args )
            return result


class SetCfg( CfgEvent ):

    def __init__( self ):
        CfgEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startCfgEvent( self, args ):
        if len( args ) < 3:
            main.log.warn( "%s - Not enough arguments: %s" % ( self.typeString, args ) )
            return EventStates().ABORT
        elif len( args ) > 3:
            main.log.warn( "%s - Too many arguments: %s" % ( self.typeString, args ) )
            return EventStates().ABORT
        else:
            self.component = str( args[ 0 ] )
            self.propName = str( args[ 1 ] )
            self.value = str( args[ 2 ] )
        assert self.component != '' and self.propName != '' and self.value != ''
        index = -1
        for controller in main.controllers:
            if controller.isUp():
                index = controller.index
        if index == -1:
            main.log.warn( "%s - No available controllers" % s( self.typeString ) )
            return EventStates().ABORT
        main.log.info( "Event recorded: {} {} {} {} {}".format( self.typeIndex, self.typeString, self.component, self.propName, self.value ) )
        controller = main.controllers[ index - 1 ]
        with controller.CLILock:
            result = controller.CLI.setCfg( component=self.component,
                                            propName=self.propName,
                                            value=self.value )
        if not result:
            main.log.warn( "%s - failed to set configuration" % ( self.typeString ) )
            return EventStates().FAIL
        return EventStates().PASS


class SetFlowObj( CfgEvent ):

    def __init__( self ):
        CfgEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startCfgEvent( self, args ):
        if len( args ) < 1:
            main.log.warn( "%s - Not enough arguments: %s" % ( self.typeString, args ) )
            return EventStates().ABORT
        elif len( args ) > 1:
            main.log.warn( "%s - Too many arguments: %s" % ( self.typeString, args ) )
            return EventStates().ABORT
        elif args[ 0 ] != 'true' and args[ 0 ] != 'false':
            main.log.warn( "%s - Invalid arguments: %s" % ( self.typeString, args ) )
            return EventStates().ABORT
        else:
            self.component = 'org.onosproject.net.intent.impl.compiler.IntentConfigurableRegistrator'
            self.propName = 'useFlowObjectives'
            self.value = str( args[ 0 ] )
        index = -1
        for controller in main.controllers:
            if controller.isUp():
                index = controller.index
        if index == -1:
            main.log.warn( "%s - No available controllers" % s( self.typeString ) )
            return EventStates().ABORT
        main.log.info( "Event recorded: {} {} {} {} {}".format( self.typeIndex, self.typeString, self.component, self.propName, self.value ) )
        controller = main.controllers[ index - 1 ]
        with controller.CLILock:
            result = controller.CLI.setCfg( component=self.component,
                                            propName=self.propName,
                                            value=self.value )
        if not result:
            main.log.warn( "%s - failed to set configuration" % ( self.typeString ) )
            return EventStates().FAIL
        return EventStates().PASS


class BalanceMasters( Event ):

    def __init__( self ):
        Event.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startEvent( self, args=None ):
        with self.eventLock:
            main.log.info( "%s - starting event" % ( self.typeString ) )
            index = -1
            for controller in main.controllers:
                if controller.isUp():
                    index = controller.index
            if index == -1:
                main.log.warn( "%s - No available controllers" % s( self.typeString ) )
                return EventStates().ABORT
            main.log.info( "Event recorded: {} {}".format( self.typeIndex, self.typeString ) )
            controller = main.controllers[ index - 1 ]
            with controller.CLILock:
                result = controller.CLI.balanceMasters()
            if not result:
                main.log.warn( "%s - failed to balance masters" % ( self.typeString ) )
                return EventStates().FAIL
            return EventStates().PASS


class SetFlowObjCompiler( CfgEvent ):

    def __init__( self ):
        CfgEvent.__init__( self )
        self.typeString = main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeString' ]
        self.typeIndex = int( main.params[ 'EVENT' ][ self.__class__.__name__ ][ 'typeIndex' ] )

    def startCfgEvent( self, args ):
        if len( args ) < 1:
            main.log.warn( "%s - Not enough arguments: %s" % ( self.typeString, args ) )
            return EventStates().ABORT
        elif len( args ) > 1:
            main.log.warn( "%s - Too many arguments: %s" % ( self.typeString, args ) )
            return EventStates().ABORT
        else:
            self.component = 'org.onosproject.net.intent.impl.compiler.IntentConfigurableRegistrator'
            self.propName = 'defaultFlowObjectiveCompiler'
            self.value = str( args[ 0 ] )
        index = -1
        for controller in main.controllers:
            if controller.isUp():
                index = controller.index
        if index == -1:
            main.log.warn( "%s - No available controllers" % s( self.typeString ) )
            return EventStates().ABORT
        main.log.info( "Event recorded: {} {} {} {} {}".format( self.typeIndex, self.typeString, self.component, self.propName, self.value ) )
        controller = main.controllers[ index - 1 ]
        with controller.CLILock:
            result = controller.CLI.setCfg( component=self.component,
                                            propName=self.propName,
                                            value=self.value )
        if not result:
            main.log.warn( "%s - failed to set configuration" % ( self.typeString ) )
            return EventStates().FAIL
        return EventStates().PASS
