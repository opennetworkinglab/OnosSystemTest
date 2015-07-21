#!/usr/bin/env python
"""
Created on 26-Nov-2012

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


"""
from drivers.common.clidriver import CLI


class Tools( CLI ):
    # The common functions for Tools included in toolsdriver

    def __init__( self ):
        super( CLI, self ).__init__()
