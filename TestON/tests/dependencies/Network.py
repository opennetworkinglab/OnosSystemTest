"""
Copyright 2018 Open Networking Foundation ( ONF )

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
import json
class Network():

    def __str__( self ):
        return self.name

    def __repr__( self ):
        return "%s:%s" % ( self.name, self.components )

    def __getattr__( self, name ):
        """
        Called when an attribute lookup has not found the attribute
        in the usual places (i.e. it is not an instance attribute nor
        is it found in the class tree for self). name is the attribute
        name. This method should return the (computed) attribute value
        or raise an AttributeError exception.

        We will look into each of the network component handles to try
        to find the attreibute.
        """
        # FIXME: allow to call a specific driver
        for component in self.components:
            if hasattr( component, name ):
                main.log.debug( "%s has attribute '%s'" % ( component.options[ 'name' ], name ) )
                return getattr( component, name )
        raise AttributeError( "Could not find attribute '%s' in any of these components: %s" % ( name, self.components ) )

    def __init__( self, name="Network" ):
        """
        components: network components created for the test
        """
        self.name = str( name )
        # Get a list of network components that are created in the test
        self.components = []
        for key, value in main.componentDictionary.items():
            if value[ 'type' ] in [ 'MininetCliDriver', 'RemoteMininetDriver', 'NetworkDriver', 'OFDPASwitchDriver' ] and hasattr( main, key ):
                self.components.append( getattr( main, key ) )
        main.log.debug( "%s initialized with components: %s" % ( self.name, self.components ) )
