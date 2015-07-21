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


class RemoteSysDriver( CLI ):
    # The common functions for emulator included in emulatordriver

    def __init__( self ):
        super( CLI, self ).__init__()

    def connect( self, **connectargs ):
        for key in connectargs:
            vars( self )[ key ] = connectargs[ key ]

        self.name = self.options[ 'name' ]

        self.handle = super(
            RemoteSysDriver,
            self ).connect(
            user_name=self.user_name,
            ip_address=self.ip_address,
            port=self.port,
            pwd=self.pwd )
        """
        if self.handle:
            self.execute( cmd= "\n",prompt= "\$|>|#",timeout= 10 )
            self.execute( cmd= "ssh -l paxterra 10.128.4.1",prompt= "paxterra@10.128.4.1's password:",timeout= 10 )
            self.execute( cmd= "\n",prompt= "paxterra@10.128.4.1's password:",timeout= 10 )
            self.execute( cmd="0nLab_gu3st",prompt="\$",timeout=10 )
            self.execute( cmd="cd TestON/bin/",prompt="\$",timeout=10 )
            self.execute( cmd="./cli.py run Assert example 1",prompt="\$",timeout=10 )
            self.execute( cmd= "\n",prompt= "$",timeout= 10 )
            #self.execute( cmd="help",prompt=">",timeout=10 )

            #self.execute( cmd="~.",prompt= ".*",timeout= 10 )
        return main.TRUE
        """
