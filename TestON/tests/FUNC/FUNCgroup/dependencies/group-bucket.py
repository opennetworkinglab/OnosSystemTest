"""
Copyright 2016 Open Networking Foundation (ONF)

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.
"""

def addBucket( main, egressPort="" ):
    """
    Description:
         Create a single bucket which can be added to a Group.
    Optional:
         * egressPort: port of egress device
    Returns:
         * Returns a Bucket
         * Returns None in case of error
    Note:
         The ip and port option are for the requests input's ip and port
         of the ONOS node.
    """
    try:

        bucket = {
                     "treatment": { "instructions": [] }
                 }
        if egressPort:
            bucket[ 'treatment' ][ 'instructions' ].append( {
                                                     "type": "OUTPUT",
                                                     "port": egressPort } )
        return bucket

    except ( AttributeError, TypeError ):
        main.log.exception( self.name + ": Object not as expected" )
        return None
    except Exception:
        main.log.exception( self.name + ": Uncaught exception!" )
        main.cleanup()
        main.exit()
