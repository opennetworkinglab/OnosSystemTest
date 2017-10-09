"""
Copyright 2015 Open Networking Foundation ( ONF )

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
"""
    These functions can be used for topology comparisons
"""
import time
import os
import json


def sendArpPackage( main, hostList ):
    import json
    import time
    """
        send arping package from host
        return the total hosts number from Onos
    """
    main.log.info( "Sending Arping package..." )
    if isinstance( hostList, list ):
        for h in hostList:
            main.Mininet1.arping( srcHost=h, dstHost="10.0.0.1", output=main.FALSE, noResult=True )
    else:
        main.Mininet1.arping( srcHost=hostList, dstHost="10.0.0.1", output=main.FALSE, noResult=True )

def getHostNum( main ):
    try:
        summaryStr = ""
        summaryStr = json.loads( main.Cluster.active( 0 ).CLI.summary().encode() )
        hostNum = summaryStr.get( 'hosts' )
        main.log.info( "host nums from ONOS : " + str( hostNum ) )
    except ( TypeError, ValueError ):
        main.log.exception( " Object not as expected: {!r}".format( summaryStr ) )
        return -1
    except Exception:
        main.log.exception( self.name + ": Uncaught exception!" )
        return -1

    return hostNum
