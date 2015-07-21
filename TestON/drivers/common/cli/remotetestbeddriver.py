#!/usr/bin/env python
"""
Created on 26-Oct-2012

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


"""
from drivers.common.clidriver import CLI


class RemoteTestBedDriver( CLI ):
    # The common functions for emulator included in RemoteTestBedDriver

    def __init__( self ):
        super( CLI, self ).__init__()

    def connect( self, **connectargs ):
        for key in connectargs:
            vars( self )[ 'vm_' + key ] = connectargs[ key ]

        remote_user_name = main.componentDictionary[
            self.name ][ 'remote_user_name' ]
        remote_ip_address = main.componentDictionary[
            self.name ][ 'remote_ip_address' ]
        remote_port = main.componentDictionary[ self.name ][ 'remote_port' ]
        remote_pwd = main.componentDictionary[ self.name ][ 'remote_pwd' ]

        self.handle = super(
            RemoteTestBedDriver,
            self ).connect(
            user_name=remote_user_name,
            ip_address=remote_ip_address,
            port=remote_port,
            pwd=remote_pwd )

        if self.handle:
            self.execute( cmd="\n", prompt="\$|>|#", timeout=10 )
            self.execute( cmd="SET CYGWIN=notty", prompt="\$|>|#", timeout=10 )
            self.execute( cmd="\n", prompt="\$|>|#", timeout=10 )
            main.log.info(
                "ssh " +
                self.vm_user_name +
                '@' +
                self.vm_ip_address )
            self.execute(
                cmd="ssh " +
                self.vm_user_name +
                '@' +
                self.vm_ip_address,
                prompt="(.*)",
                timeout=10 )
            self.execute( cmd="\n", prompt="assword:", timeout=10 )
            self.execute( cmd=self.vm_pwd, prompt="\$", timeout=10 )

            return self.handle
        else:
            return main.FALSE
