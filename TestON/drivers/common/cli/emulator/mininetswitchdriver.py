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
from drivers.common.cli.emulatordriver import Emulator
from core.graph import Graph


class MininetSwitchDriver( Emulator ):
    """
    This class is created as a standalone switch driver. Hoever actually the
    switch is an ovs-switch created by Mininet. It could be used as driver
    for a mock physical switch for proof-of-concept testing in physical
    environment.
    """
    def __init__( self ):
        super( MininetSwitchDriver, self ).__init__()
        self.handle = self
        self.name = None
        self.shortName = None
        self.home = None

    def connect( self, **connectargs ):
        """
        Creates ssh handle for the Mininet switch.
        NOTE:
        The ip_address would come from the topo file using the host tag, the
        value can be an environment variable as well as a "localhost" to get
        the ip address needed to ssh to the "bench"
        """
        try:
            for key in connectargs:
                vars( self )[ key ] = connectargs[ key ]
            self.home = "~/mininet"
            self.name = self.options[ 'name' ]
            self.shortName = self.options[ 'shortName' ]
            for key in self.options:
                if key == "home":
                    self.home = self.options[ 'home' ]
                    break
            if self.home is None or self.home == "":
                self.home = "~/mininet"

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
                MininetSwitchDriver,
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
                return main.TRUE
            else:
                main.log.error( "Connection failed to the host " +
                                self.user_name +
                                "@" +
                                self.ip_address )
                main.log.error( "Failed to connect to the Mininet CLI" )
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
            i = self.handle.expect( [ self.prompt, pexpect.EOF, pexpect.TIMEOUT ],
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

    def assignSwController( self, ip, port="6653", ptcp="" ):
        """
        Description:
            Assign the Mininet switch to the controllers
        Required:
            ip - Ip addresses of controllers. This can be a list or a string.
        Optional:
            port - ONOS use port 6653, if no list of ports is passed, then
                   the all the controller will use 6653 as their port number
            ptcp - ptcp number. This needs to be a string.
        Return:
            Returns main.TRUE if the switch is correctly assigned to controllers,
            otherwise it will return main.FALSE or an appropriate exception(s)
        """
        assignResult = main.TRUE
        # Initial ovs command
        commandList = []
        command = "sudo ovs-vsctl set-controller "
        onosIp = ""
        try:
            if isinstance( ip, types.StringType ):
                onosIp = "tcp:" + str( ip ) + ":"
                if isinstance( port, types.StringType ) or \
                   isinstance( port, types.IntType ):
                    onosIp += str( port )
                elif isinstance( port, types.ListType ):
                    main.log.error( self.name + ": Only one controller " +
                                    "assigned and a list of ports has" +
                                    " been passed" )
                    return main.FALSE
                else:
                    main.log.error( self.name + ": Invalid controller port " +
                                    "number. Please specify correct " +
                                    "controller port" )
                    return main.FALSE
            elif isinstance( ip, types.ListType ):
                if isinstance( port, types.StringType ) or \
                   isinstance( port, types.IntType ):
                    for ipAddress in ip:
                        onosIp += "tcp:" + str( ipAddress ) + ":" + \
                                  str( port ) + " "
                elif isinstance( port, types.ListType ):
                    if ( len( ip ) != len( port ) ):
                        main.log.error( self.name + ": Port list = " +
                                        str( len( port ) ) +
                                        "should be the same as controller" +
                                        " ip list = " + str( len( ip ) ) )
                        return main.FALSE
                    else:
                        onosIp = ""
                        for ipAddress, portNum in zip( ip, port ):
                            onosIp += "tcp:" + str( ipAddress ) + ":" + \
                                      str( portNum ) + " "
                else:
                    main.log.error( self.name + ": Invalid controller port " +
                                    "number. Please specify correct " +
                                    "controller port" )
                    return main.FALSE
            else:
                main.log.error( self.name + ": Invalid ip address" )
                return main.FALSE
            command += self.shortName + " "
            if ptcp:
                if isinstance( ptcp, types.StringType ):
                    command += "ptcp:" + str( ptcp ) + " "
                elif isinstance( ptcp, types.ListType ):
                    main.log.error( self.name + ": Only one switch is " +
                                    "being set and multiple PTCP is " +
                                    "being passed " )
                    return main.FALSE
                else:
                    main.log.error( self.name + ": Invalid PTCP" )
                    return main.FALSE
            command += onosIp
            self.execute( cmd=command, prompt=self.prompt, timeout=5 )
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": pexpect.TIMEOUT found" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()
