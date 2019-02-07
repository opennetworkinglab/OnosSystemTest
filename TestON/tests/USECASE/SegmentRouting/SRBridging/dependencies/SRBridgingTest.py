"""
Copyright 2017 Open Networking Foundation ( ONF )

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
import tests.USECASE.SegmentRouting.dependencies.cfgtranslator as translator

class SRBridgingTest ():

    def __init__( self ):
        self.default = ''
        self.topo = dict()
        # TODO: Check minFlowCount of leaf for BMv2 switch
        # (number of spine switch, number of leaf switch, dual-homed, description, minFlowCount - leaf (OvS), minFlowCount - leaf (BMv2))
        self.topo[ '0x1' ] = ( 0, 1, False, 'single ToR', 28, 28 )
        self.topo[ '0x2' ] = ( 0, 2, True, 'dual-homed ToR', 37, 37 )
        self.topo[ '2x2' ] = ( 2, 2, False, '2x2 leaf-spine topology', 37, 32 )
        # TODO: Implement 2x3 topology
        # topo[ '2x3' ] = ( 2, 3, True, '2x3 leaf-spine topology with dual ToR and single ToR', 28 )
        self.topo[ '2x4' ] = ( 2, 4, True, '2x4 dual-homed leaf-spine topology', 53, 53 )
        self.switchNames = {}
        self.switchNames[ '2x2' ] = [ "leaf1", "leaf2", "spine101", "spine102" ]

    def runTest( self, main, test_idx, topology, onosNodes, description, vlan = [] ):
        skipPackage = False
        init = False
        if not hasattr( main, 'apps' ):
            init = True
            run.initTest( main )
        # Skip onos packaging if the clusrer size stays the same
        if not init and onosNodes == main.Cluster.numCtrls:
            skipPackage = True

        main.case( '%s, with %s and %d ONOS instance%s' %
                   ( description, self.topo[ topology ][ 3 ], onosNodes, 's' if onosNodes > 1 else '' ) )

        main.cfgName = 'CASE%01d%01d' % ( test_idx / 10, ( ( test_idx - 1 ) % 10 ) % 4 + 1 )
        main.Cluster.setRunningNode( onosNodes )
        run.installOnos( main, skipPackage=skipPackage, cliSleep=5 )
        if main.useBmv2:
            # Translate configuration file from OVS-OFDPA to BMv2 driver
            translator.ofdpaToBmv2( main )
        else:
            translator.bmv2ToOfdpa( main )
        run.loadJson( main )
        run.loadChart( main )
        if hasattr( main, 'Mininet1' ):
            # Run the test with Mininet
            mininet_args = ' --spine=%d --leaf=%d' % ( self.topo[ topology ][ 0 ], self.topo[ topology ][ 1 ] )
            if self.topo[ topology ][ 2 ]:
                mininet_args += ' --dual-homed'
            if len( vlan ) > 0 :
                mininet_args += ' --vlan=%s' % ( ','.join( ['%d' % vlanId for vlanId in vlan ] ) )
            if main.useBmv2:
                mininet_args += ' --switch bmv2'
                main.log.info( "Using BMv2 switch" )

            run.startMininet( main, 'trellis_fabric.py', args=mininet_args )
        else:
            # Run the test with physical devices
            run.connectToPhysicalNetwork( main, self.switchNames[ topology ] )

        run.checkFlows( main, minFlowCount=self.topo[ topology ][ 5 if main.useBmv2 else 4 ] * self.topo[ topology ][ 1 ], sleep=5 )
        if main.useBmv2:
            leaf_dpid = [ "device:bmv2:leaf%d" % ( ls + 1 ) for ls in range( self.topo[ topology ][ 1 ]) ]
        else:
            leaf_dpid = [ "of:%016d" % ( ls + 1 ) for ls in range( self.topo[ topology ][ 1 ] ) ]
        for dpid in leaf_dpid:
            run.checkFlowsByDpid( main, dpid, self.topo[ topology ][ 5 if main.useBmv2 else 4 ], sleep=5 )
        run.pingAll( main )

        run.cleanup( main )
