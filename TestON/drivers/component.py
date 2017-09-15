#!/usr/bin/env python
"""
Created on 24-Oct-2012
Copyright 2012 Open Networking Foundation ( ONF )

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
import logging


class Component( object ):

    """
    This is the tempalte class for components
    """
    def __str__( self ):
        try:
            assert self.name
        except AttributeError:
            return repr( self )
        return str( self.name )

    def __init__( self ):
        self.default = ''
        self.name = ''
        self.wrapped = sys.modules[ __name__ ]
        self.count = 0
        self.prompt = "\$"

    def __getattr__( self, name ):
        """
         Called when an attribute lookup has not found the attribute
         in the usual places ( i.e. it is not an instance attribute nor
         is it found in the class tree for self ). name is the attribute
         name. This method should return the ( computed ) attribute value
         or raise an AttributeError exception.
        """
        try:
            return getattr( self.wrapped, name )
        except AttributeError as error:
            # NOTE: The first time we load a driver module we get this error
            if "'module' object has no attribute '__path__'" in error:
                pass
            else:
                raise error

    def connect( self ):

        vars( main )[ self.name + 'log' ] = logging.getLogger( self.name )

        session_file = main.logdir + "/" + self.name + ".session"
        self.log_handler = logging.FileHandler( session_file )
        self.log_handler.setLevel( logging.DEBUG )

        vars( main )[ self.name + 'log' ].setLevel( logging.DEBUG )
        _formatter = logging.Formatter(
            "%(asctime)s  %(name)-10s: %(levelname)-8s: %(message)s" )
        self.log_handler.setFormatter( _formatter )
        vars( main )[ self.name + 'log' ].addHandler( self.log_handler )
        # Adding header for the component log
        vars( main )[ self.name + 'log' ].info( main.logHeader )
        # Opening the session log to append command's execution output
        self.logfile_handler = open( session_file, "a" )

        return "Dummy"

    def execute( self, cmd ):
        return main.TRUE
        # import commands
        # return commands.getoutput( cmd )

    def disconnect( self ):
        return main.TRUE

    def config( self ):
        self = self
        # Need to update the configuration code

    def cleanup( self ):
        return main.TRUE

    def log( self, message ):
        """
        Here finding the for the component to which the
        log message based on the called child object.
        """
        vars( main )[ self.name + 'log' ].info( "\n" + message + "\n" )

    def close_log_handles( self ):
        vars( main )[ self.name + 'log' ].removeHandler( self.log_handler )
        if self.logfile_handler:
            self.logfile_handler.close()

    def get_version( self ):
        return "Version unknown"

    def experimentRun( self, *args, **kwargs ):
        # FIXME handle *args
        args = utilities.parse_args( [ "RETURNS" ], **kwargs )
        return args[ "RETURNS" ]

if __name__ != "__main__":
    import sys
    sys.modules[ __name__ ] = Component()
