#!/usr/bin/env python
"""
2015-2016
Copyright 2016 Open Networking Foundation (ONF)

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
import pexpect
import re
import sys
import types
import os
from drivers.common.cli.emulator.scapyclidriver import ScapyCliDriver


class MininetHostScapyCliDriver( ScapyCliDriver ):

    """
    This class is created as a standalone Mininet host scapy driver. It
    could be used as driver for a mock physical host for proof-of-concept
    testing in physical environment.
    """
    def __init__( self ):
        super( MininetHostScapyCliDriver, self ).__init__()
        self.handle = self
        self.name = None
        self.home = None
        self.wrapped = sys.modules[ __name__ ]
        self.flag = 0
        # TODO: Refactor driver to use these everywhere
        self.hostPrompt = "~#"
        self.scapyPrompt = ">>>"

    def connect( self, **connectargs ):
        """
           Here the main is the TestON instance after creating
           all the log handles."""
        try:
            for key in connectargs:
                vars( self )[ key ] = connectargs[ key ]
            self.home = self.options[ 'home' ] if 'home' in self.options.keys() else "~/"
            self.name = self.options[ 'name' ]
            self.ifaceName = self.options[ 'ifaceName' ] if 'ifaceName' in self.options.keys() else self.name + "-eth0"

            try:
                if os.getenv( str( self.ip_address ) ) is not None:
                    self.ip_address = os.getenv( str( self.ip_address ) )
                else:
                    main.log.info( self.name +
                                   ": Trying to connect to " +
                                   self.ip_address )

            except KeyError:
                main.log.info( "Invalid host name," +
                               " connecting to local host instead" )
                self.ip_address = 'localhost'
            except Exception as inst:
                main.log.error( "Uncaught exception: " + str( inst ) )

            self.handle = super(
                ScapyCliDriver,
                self ).connect(
                user_name=self.user_name,
                ip_address=self.ip_address,
                port=None,
                pwd=self.pwd )

            if self.handle:
                main.log.info( "Connection successful to the host " +
                               self.user_name +
                               "@" +
                               self.ip_address )
                self.handle.sendline( "~/mininet/util/m " + self.name )
                self.handle.sendline( "cd" )
                self.handle.expect( self.hostPrompt )
                self.handle.sendline( "" )
                self.handle.expect( self.hostPrompt )
                return main.TRUE
            else:
                main.log.error( "Connection failed to the host " +
                                self.user_name +
                                "@" +
                                self.ip_address )
                main.log.error( "Failed to connect to the Mininet Host" )
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def disconnect( self ):
        """
        Called when test is complete to disconnect the handle.
        """
        try:
            self.handle.sendline( '' )
            i = self.handle.expect( [ self.hostPrompt, pexpect.EOF, pexpect.TIMEOUT ],
                                    timeout=2 )
            if i == 0:
                return main.TRUE
            elif i == 1:
                return main.TRUE
            else:
                main.log.error( "Connection failed to the host" )
            return main.ERROR
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

if __name__ != "__main__":
    sys.modules[ __name__ ] = MininetHostScapyCliDriver()
