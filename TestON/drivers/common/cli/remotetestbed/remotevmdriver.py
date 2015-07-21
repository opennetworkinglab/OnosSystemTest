#!/usr/bin/env python
"""
Created on 12-Feb-2013

author:: Anil Kumar ( anilkumar.s@paxterrasolutions.com )


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


RemoteVMDriver is the basic driver which will handle the Mininet functions
"""
import pexpect

from drivers.common.cli.remotetestbeddriver import RemoteTestBedDriver


class RemoteVMDriver( RemoteTestBedDriver ):

    """
        RemoteVMDriver is the basic driver which will handle the Mininet functions
    """
    def __init__( self ):
        super( RemoteTestBedDriver, self ).__init__()

    def connect( self, **connectargs ):
        for key in connectargs:
            vars( self )[ key ] = connectargs[ key ]

        self.name = self.options[ 'name' ]

        self.handle = super(
            RemoteVMDriver,
            self ).connect(
            user_name=self.user_name,
            ip_address=self.ip_address,
            port=self.port,
            pwd=self.pwd )
        if self.handle:
            main.log.info( self.name + " connected successfully " )
            return self.handle
        return main.TRUE

    def SSH( self, **connectargs ):
        for key in connectargs:
            vars( self )[ key ] = connectargs[ key ]

        """
           Connection will establish to the remote host using ssh.
           It will take user_name ,ip_address and password as arguments<br>
           and will return the handle.
        """
        for key in connectargs:
            vars( self )[ key ] = connectargs[ key ]

        ssh_newkey = 'Are you sure you want to continue connecting'
        refused = "ssh: connect to host " + \
            self.ip_address + " port 22: Connection refused"
        if self.port:
            self.handle.sendline(
                'ssh -p ' +
                self.port +
                ' ' +
                self.user_name +
                '@' +
                self.ip_address )
        else:
            self.handle.sendline(
                'ssh ' +
                self.user_name +
                '@' +
                self.ip_address )
            self.handle.sendline( "\r" )

        i = self.handle.expect( [ ssh_newkey,
                                  'password:',
                                  pexpect.EOF,
                                  pexpect.TIMEOUT,
                                  refused ],
                                120 )

        if i == 0:
            main.log.info( "ssh key confirmation received, send yes" )
            self.handle.sendline( 'yes' )
            i = self.handle.expect( [ ssh_newkey, 'password:', pexpect.EOF ] )
        if i == 1:
            main.log.info( "ssh connection asked for password, gave password" )
            self.handle.sendline( self.pwd )
            self.handle.expect( '>|#|$' )

        elif i == 2:
            main.log.error( "Connection timeout" )
            return main.FALSE
        elif i == 3:  # timeout
            main.log.error(
                "No route to the Host " +
                self.user_name +
                "@" +
                self.ip_address )
            return main.FALSE
        elif i == 4:
            main.log.error(
                "ssh: connect to host " +
                self.ip_address +
                " port 22: Connection refused" )
            return main.FALSE

        self.handle.sendline( "\r" )
        return main.TRUE
