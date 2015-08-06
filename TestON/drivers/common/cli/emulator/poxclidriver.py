#!/usr/bin/env python
"""
Created on 26-Oct-2012

author:: Raghav Kashyap( raghavkashyap@paxterrasolutions.com )


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


pox driver provides the basic functions of POX controller
"""
import pexpect
import struct
import fcntl
import os
import signal
import sys
from drivers.common.cli.emulatordriver import Emulator


class PoxCliDriver( Emulator ):

    """
        PoxCliDriver driver provides the basic functions of POX controller
    """
    def __init__( self ):
        super( Emulator, self ).__init__()
        self.handle = self
        self.wrapped = sys.modules[ __name__ ]

    def connect( self, **connectargs ):
        #,user_name, ip_address, pwd,options ):
        """
          this subroutine is to launch pox controller . It must have arguments as :
          user_name  = host name ,
          ip_address = ip address of the host ,
          pwd = password of host ,
          options = it is a topology hash which will consists the component's details for the test run

          *** host is here a virtual mahine or system where pox framework hierarchy exists
        """
        for key in connectargs:
            vars( self )[ key ] = connectargs[ key ]

        self.name = self.options[ 'name' ]

        poxLibPath = 'default'

        self.handle = super(
            PoxCliDriver,
            self ).connect(
            user_name=self.user_name,
            ip_address=self.ip_address,
            port=None,
            pwd=self.pwd )

        if self.handle:
            self.handle.expect( "openflow" )
            command = self.getcmd( self.options )
            # print command
            main.log.info( "Entering into POX hierarchy" )
            if self.options[ 'pox_lib_location' ] != 'default':
                self.execute(
                    cmd="cd " +
                    self.options[ 'pox_lib_location' ],
                    prompt="/pox\$",
                    timeout=120 )
            else:
                self.execute(
                    cmd="cd ~/TestON/lib/pox/",
                    prompt="/pox\$",
                    timeout=120 )
            # launching pox with components
            main.log.info( "launching POX controller with given components" )
            self.execute( cmd=command, prompt="DEBUG:", timeout=120 )
            return main.TRUE
        else:
            main.log.error(
                "Connection failed to the host " +
                self.user_name +
                "@" +
                self.ip_address )
            main.log.error( "Failed to connect to the POX controller" )
            return main.FALSE

    def disconnect( self, handle ):
        if self.handle:
            self.execute( cmd="exit()", prompt="/pox\$", timeout=120 )
        else:
            main.log.error( "Connection failed to the host" )

    def get_version( self ):
        file_input = path + '/lib/pox/core.py'
        version = super( PoxCliDriver, self ).get_version()
        pattern = '\s*self\.version(.*)'
        import re
        for line in open( file_input, 'r' ).readlines():
            result = re.match( pattern, line )
            if result:
                version = result.group( 0 )
                version = re.sub(
                    "\s*self\.version\s*=\s*|\(|\)",
                    '',
                    version )
                version = re.sub( ",", '.', version )
                version = "POX " + version

        return version

    def getcmd( self, options ):
        command = "./pox.py "
        for item in options.keys():
            if isinstance( options[ item ], dict ):
                command = command + item
                for items in options[ item ].keys():
                    if options[ item ][ items ] == "None":
                        command = command + " --" + items + " "
                    else:
                        command = command + " --" + items + \
                            "=" + options[ item ][ items ] + " "
            else:
                if item == 'pox_lib_location':
                    poxLibPath = options[ item ]
                elif item == 'type' or item == 'name':
                    pass
                else:
                    command = command + item

        return command


if __name__ != "__main__":
    import sys

    sys.modules[ __name__ ] = PoxCliDriver()
