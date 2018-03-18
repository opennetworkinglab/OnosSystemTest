#!/usr/bin/env python
"""
Copyright 2018 Open Networking Foundation (ONF)

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
import time
from math import pow
from drivers.common.clidriver import CLI

class HostDriver( CLI ):
    """
    This class is created as a standalone host driver.
    """
    def __init__( self ):
        super( HostDriver, self ).__init__()
        self.handle = self
        self.name = None
        self.shortName = None
        self.home = None

    def connect( self, **connectargs ):
        """
        Creates ssh handle for host.
        NOTE:
        The ip_address would come from the topo file using the host tag, the
        value can be an environment variable as well as a "localhost" to get
        the ip address needed to ssh to the "bench"
        """
        try:
            for key in connectargs:
                vars( self )[ key ] = connectargs[ key ]
            self.name = self.options[ 'name' ]
            self.shortName = self.options[ 'shortName' ]

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
                HostDriver,
                self ).connect(
                user_name=self.user_name,
                ip_address=self.ip_address,
                port=None,
                pwd=self.pwd )

            if self.handle:
                main.log.info( "Connection successful to the " +
                               self.user_name +
                               "@" +
                               self.ip_address )
                self.handle.sendline( "" )
                self.handle.expect( self.prompt )
                return main.TRUE
            else:
                main.log.error( "Connection failed to " +
                                self.user_name +
                                "@" +
                                self.ip_address )
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def disconnect( self, **connectargs ):
        """
        Called when test is complete to disconnect the handle.
        """
        response = main.TRUE
        try:
            if self.handle:
                # Disconnect from the host
                self.handle.sendline( "" )
                self.handle.expect( self.prompt )
                self.handle.sendline( "exit" )
                i = self.handle.expect( [ "closed", pexpect.TIMEOUT ], timeout=2 )
                if i == 1:
                    main.log.error(
                        self.name +
                        ": timeout when waiting for response" )
                    main.log.error( "response: " + str( self.handle.before ) )
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            response = main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
        except ValueError:
            main.log.exception( "Exception in disconnect of " + self.name )
            response = main.TRUE
        except Exception:
            main.log.exception( self.name + ": Connection failed to the host" )
            response = main.FALSE
        return response

    def ping( self, dst, ipv6=False, wait=3 ):
        """
        Description:
            Ping from this host to another
        Required:
            dst: IP address of destination host
        Optional:
            ipv6: will use ping6 command if True; otherwise use ping command
            wait: timeout for ping command
        """
        try:
            command = "ping6" if ipv6 else "ping"
            command += " -c 1 -i 1 -W " + str( wait ) + " " + str( dst )
            main.log.info( self.name + ": Sending: " + command )
            self.handle.sendline( command )
            i = self.handle.expect( [ self.prompt, pexpect.TIMEOUT ],
                                    timeout=wait + 1 )
            if i == 1:
                main.log.error(
                    self.name +
                    ": timeout when waiting for response" )
                main.log.error( "response: " + str( self.handle.before ) )
            self.handle.sendline( "" )
            self.handle.expect( self.prompt )
            response = self.handle.before
            if re.search( ',\s0\%\spacket\sloss', response ):
                main.log.info( self.name + ": no packets lost, host is reachable" )
                return main.TRUE
            else:
                main.log.warn(
                    self.name +
                    ": PACKET LOST, HOST IS NOT REACHABLE" )
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def ifconfig( self, wait=3 ):
        """
        Run ifconfig command on host and return output
        """
        try:
            command = "ifconfig"
            main.log.info( self.name + ": Sending: " + command )
            self.handle.sendline( command )
            i = self.handle.expect( [ self.prompt, pexpect.TIMEOUT ],
                                    timeout=wait + 1 )
            if i == 1:
                main.log.error(
                    self.name +
                    ": timeout when waiting for response" )
                main.log.error( "response: " + str( self.handle.before ) )
            self.handle.sendline( "" )
            self.handle.expect( self.prompt )
            response = self.handle.before
            return response
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()
