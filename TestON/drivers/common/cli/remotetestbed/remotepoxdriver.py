#!/usr/bin/env python
"""
Created on 12-Feb-2013
Modified 2015 by ON.Lab

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

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
from drivers.common.cli.remotetestbeddriver import RemoteTestBedDriver


class RemotePoxDriver( RemoteTestBedDriver ):

    """
        RemoteVMDriver is the basic driver which will handle the Mininet functions
    """
    def __init__( self ):
        super( RemotePoxDriver, self ).__init__()

    def connect( self, **connectargs ):
        for key in connectargs:
            vars( self )[ key ] = connectargs[ key ]

        self.name = self.options[ 'name' ]

        self.handle = super(
            RemotePoxDriver,
            self ).connect(
            user_name=self.user_name,
            ip_address=self.ip_address,
            port=self.port,
            pwd=self.pwd )
        if self.handle:
            main.log.info( self.name + " connected successfully " )

            self.execute(
                cmd="cd " +
                self.options[ 'pox_lib_location' ],
                prompt="/pox" + self.prompt,
                timeout=120 )
            self.execute(
                cmd='./pox.py samples.of_tutorial',
                prompt="DEBUG:",
                timeout=120 )
            return self.handle
        return main.TRUE

    def disconnect( self, handle ):
        if self.handle:
            self.execute( cmd="exit()", prompt="/pox" + self.prompt, timeout=120 )
        else:
            main.log.error( "Connection failed to the host" )
