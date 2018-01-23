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

MininetScapyCliDriver is for controlling scapy hosts running in Mininet

TODO: Add Explanation on how to install scapy
"""
import pexpect
import re
import sys
import types
import os
from drivers.common.cli.emulator.scapyclidriver import ScapyCliDriver


class MininetScapyCliDriver( ScapyCliDriver ):
    """
    MininetScapyCliDriver is for controlling scapy hosts running in Mininet
    """
    def __init__( self ):
        super( MininetScapyCliDriver, self ).__init__()
        self.handle = self
        self.name = None
        self.home = None
        self.wrapped = sys.modules[ __name__ ]
        self.flag = 0
        self.hostPrompt = "~#"
        self.scapyPrompt = ">>>"

    def connect( self, **connectargs ):
        """
        Here the main is the TestON instance after creating
        all the log handles.
        """
        try:
            for key in connectargs:
                vars( self )[ key ] = connectargs[ key ]
            self.home = self.options[ 'home' ] if 'home' in self.options.keys() else "~/mininet"
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
        Called at the end of the test to stop the scapy component and
        disconnect the handle.
        """
        self.handle.sendline( '' )
        i = self.handle.expect( [ 'mininet>', pexpect.EOF, pexpect.TIMEOUT ],
                                timeout=2 )
        response = main.TRUE
        if i == 0:
            response = self.stopNet()
        elif i == 1:
            return main.TRUE
        # print "Disconnecting Mininet"
        if self.handle:
            self.handle.sendline( "exit" )
            self.handle.expect( "exit" )
            self.handle.expect( "(.*)" )
        else:
            main.log.error( "Connection failed to the host" )
        return response

    def stopNet( self, fileName="", timeout=5 ):
        """
        Stops mininet.
        Returns main.TRUE if the mininet successfully stops and
                main.FALSE if the pexpect handle does not exist.

        Will cleanup and exit the test if scapy fails to stop
        """
        main.log.info( self.name + ": Stopping scapy..." )
        response = ''
        if self.handle:
            try:
                self.handle.sendline( "" )
                i = self.handle.expect( [ '>>>',
                                          self.prompt,
                                          pexpect.EOF,
                                          pexpect.TIMEOUT ],
                                        timeout )
                if i == 0:
                    main.log.info( "Exiting scapy..." )
                response = self.execute(
                    cmd="exit",
                    prompt="(.*)",
                    timeout=120 )
                main.log.info( self.name + ": Stopped" )
                response = main.TRUE

                if i == 1:
                    main.log.info( " Mininet trying to exit while not " +
                                   "in the mininet prompt" )
                elif i == 2:
                    main.log.error( "Something went wrong exiting mininet" )
                elif i == 3:  # timeout
                    main.log.error( "Something went wrong exiting mininet " +
                                    "TIMEOUT" )

                if fileName:
                    self.handle.sendline( "" )
                    self.handle.expect( self.prompt )
                    self.handle.sendline(
                        "sudo kill -9 \`ps -ef | grep \"" +
                        fileName +
                        "\" | grep -v grep | awk '{print $2}'\`" )
            except pexpect.EOF:
                main.log.error( self.name + ": EOF exception found" )
                main.log.error( self.name + ":     " + self.handle.before )
                main.cleanAndExit()
        else:
            main.log.error( self.name + ": Connection failed to the host" )
            response = main.FALSE
        return response

    def createHostComponent( self, name ):
        """
        Creates a new mininet cli component with the same parameters as self.
        This new component is intended to be used to login to the hosts created
        by mininet.

        Arguments:
            name - The string of the name of this component. The new component
                   will be assigned to main.<name> .
                   In addition, main.<name>.name = str( name )
        """
        try:
            # look to see if this component already exists
            getattr( main, name )
        except AttributeError:
            # namespace is clear, creating component
            main.componentDictionary[ name ] = main.componentDictionary[ self.name ].copy()
            main.componentDictionary[ name ][ 'connect_order' ] = str( int( main.componentDictionary[ name ][ 'connect_order' ] ) + 1 )
            main.componentInit( name )
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()
        else:
            # namespace is not clear!
            main.log.error( name + " component already exists!" )
            main.cleanAndExit()

    def removeHostComponent( self, name ):
        """
        Remove host component
        Arguments:
            name - The string of the name of the component to delete.
        """
        try:
            # Get host component
            component = getattr( main, name )
        except AttributeError:
            main.log.error( "Component " + name + " does not exist." )
            return main.FALSE
        try:
            # Disconnect from component
            component.disconnect()
            # Delete component
            delattr( main, name )
            # Delete component from ComponentDictionary
            del( main.componentDictionary[ name ] )
            return main.TRUE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def startHostCli( self, host=None ):
        """
        Use the mininet m utility to connect to the host's cli
        """
        # These are fields that can be used by scapy packets. Initialized to None
        self.hostIp = None
        self.hostMac = None
        try:
            if not host:
                host = self.name
            self.handle.sendline( self.home + "/util/m " + host )
            self.handle.sendline( "cd" )
            self.handle.expect( self.hostPrompt )
            self.handle.sendline( "" )
            self.handle.expect( self.hostPrompt )
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return main.FALSE
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

if __name__ != "__main__":
    sys.modules[ __name__ ] = MininetScapyCliDriver()
