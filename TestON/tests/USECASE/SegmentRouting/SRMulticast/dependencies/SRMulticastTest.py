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

from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as run

class SRMulticastTest ():

    def __init__( self ):
        self.default = ''
        self.topo = dict()
        # (number of spine switch, number of leaf switch, dual-homed, description, minFlowCount - leaf)
        self.topo[ '2x2' ] = ( 2, 2, False, '2x2 leaf-spine topology', 1 )
        self.switchNames = {}
        self.switchNames[ '2x2' ] = [ "leaf205", "leaf206", "spine227", "spine228" ]

    def runTest( self, main, test_idx, topology, onosNodes, description, vlan = [] ):
        skipPackage = False
        init = False
        if not hasattr( main, 'apps' ):
            init = True
            run.initTest( main )
        # Skip onos packaging if the cluster size stays the same
        if not init and onosNodes == main.Cluster.numCtrls:
            skipPackage = True

        main.case( '%s, with %s and %d ONOS instance%s' %
                   ( description, self.topo[ topology ][ 3 ], onosNodes, 's' if onosNodes > 1 else '' ) )

        main.cfgName = 'CASE%01d%01d' % ( test_idx / 10, ( ( test_idx - 1 ) % 10 ) % 4 + 1 )
        main.Cluster.setRunningNode( onosNodes )
        run.installOnos( main, skipPackage=skipPackage, cliSleep=5 )
        if hasattr( main, 'Mininet1' ):
            # TODO Mininet implementation
            pass
        else:
            # Run the test with physical devices
            run.connectToPhysicalNetwork( main, self.switchNames[ topology ] )
        # Check if the devices are up
        run.checkDevices( main, switches=len(self.switchNames[ topology ]))
        # Check the flows against the devices
        run.checkFlows( main, minFlowCount=self.topo[ topology ][ 4 ] * self.topo[ topology ][ 1 ], sleep=5 )
        # Clean up the environment
        run.cleanup( main, physical=(not hasattr( main, 'Mininet1' )))
