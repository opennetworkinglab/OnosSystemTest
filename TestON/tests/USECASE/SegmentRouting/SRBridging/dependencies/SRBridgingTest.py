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
        self.topo = run.getTopo()
        # TODO: Implement 2x3 topology
        # topo[ '2x3' ] = ( 2, 3, True, '2x3 leaf-spine topology with dual ToR and single ToR', 28 )
        self.switchNames = {}
        self.switchNames[ '0x1' ] = [ "leaf1" ]
        self.switchNames[ '2x2' ] = [ "leaf1", "leaf2", "spine101", "spine102" ]
        main.switchType = "ovs"

    def runTest( self, main, test_idx, topology, onosNodes, description, vlan = [] ):
        try:
            skipPackage = False
            init = False
            if not hasattr( main, 'apps' ):
                init = True
                run.initTest( main )
            # Skip onos packaging if the cluster size stays the same
            if not init and onosNodes == main.Cluster.numCtrls:
                skipPackage = True

            main.case( '%s, with %s, %s switches and %d ONOS instance%s' %( description, self.topo[ topology ][ 'description' ], main.switchType, onosNodes, 's' if onosNodes > 1 else '' ) )
            spines = self.topo[ topology ][ 'spines' ]
            leaves = self.topo[ topology ][ 'leaves' ]
            switches = spines + leaves
            links = ( spines * leaves ) * 2
            if self.topo[ topology ][ 'dual-linked' ]:
                links += links
            if self.topo[ topology ][ 'dual-homed' ]:
                links += ( leaves - 1 ) * 2

            main.cfgName = 'CASE%01d%01d' % ( test_idx / 10, test_idx % 10 )
            print (main.cfgName, "Testcase : CASE 09")
            main.Cluster.setRunningNode( onosNodes )
            run.installOnos( main, skipPackage=skipPackage, cliSleep=5 )
            if not main.persistentSetup:
                if main.useBmv2:
                    switchPrefix = main.params[ 'DEPENDENCY' ].get( 'switchPrefix', '' )
                    if switchPrefix is None or "None":
                        switchPrefix = ''
                    # Translate configuration file from OVS-OFDPA to BMv2 driver
                    translator.bmv2ToOfdpa( main )  # Try to cleanup if switching between switch types
                    translator.ofdpaToBmv2( main, switchPrefix=switchPrefix )
                else:
                    translator.bmv2ToOfdpa( main )
                suf = main.params.get( 'jsonFileSuffix', None)
                if suf:
                    run.loadJson( main, suffix=suf )
                else:
                    run.loadJson( main )
            run.loadChart( main )  # stores hosts to ping and expected results
            if hasattr( main, 'Mininet1' ):
                run.mnDockerSetup( main )  # optionally create and setup docker image

                # Run the test with Mininet
                mininet_args = ' --spine=%d --leaf=%d' % ( self.topo[ topology ][ 'spines' ], self.topo[ topology ][ 'leaves' ] )
                if self.topo[ topology ][ 'dual-homed' ]:
                    mininet_args += ' --dual-homed'
                if len( vlan ) > 0 :
                    mininet_args += ' --vlan=%s' % ( ','.join( ['%d' % vlanId for vlanId in vlan ] ) )
                if main.useBmv2:
                    mininet_args += ' --switch %s' % main.switchType
                    main.log.info( "Using %s switch" % main.switchType )

                run.startMininet( main, 'trellis_fabric.py', args=mininet_args )

            else:
                # Run the test with physical devices
                run.connectToPhysicalNetwork( main, hostDiscovery=False )  # We don't want to do host discovery in the pod

            run.checkFlows( main, minFlowCount=self.topo[ topology ][ 'minFlow-Stratum' if main.useBmv2 else 'minFlow-OvS' ] * self.topo[ topology ][ 'leaves' ], sleep=5 )
            if main.useBmv2:
                switchPrefix = main.params[ 'DEPENDENCY' ].get( 'switchPrefix', '' )
                if switchPrefix is None or "None":
                    switchPrefix = ''
                if switchPrefix is not '' and switchPrefix is not None:
                    switchPrefix += ':'
                leaf_dpid = [ "device:%sleaf%d" % ( switchPrefix, ls + 1 ) for ls in range( self.topo[ topology ][ 'leaves' ]) ]
            else:
                leaf_dpid = [ "of:%016d" % ( ls + 1 ) for ls in range( self.topo[ topology ][ 'leaves' ] ) ]
            for dpid in leaf_dpid:
                run.checkFlowsByDpid( main, dpid, self.topo[ topology ][ 'minFlow-Stratum' if main.useBmv2 else 'minFlow-OvS' ], sleep=5 )
            run.verifyTopology( main, switches, links, onosNodes )
            run.pingAll( main )
        except Exception as e:
            main.log.exception( "Error in runTest" )
            main.skipCase( result="FAIL", msg=e )
        finally:
            run.cleanup( main )
