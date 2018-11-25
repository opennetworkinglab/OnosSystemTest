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

import tests.USECASE.SegmentRouting.dependencies.cfgtranslator as translator

class SRDynamicConfTest:
    def __init__( self ):
        self.default = ''

    @staticmethod
    def runTest( main, testIndex, topology, onosNodes, description, vlan=( 0, 0, 0, 0 ) ):
        '''
        Tests connectivity for each test case.
        Configuration files:
        - (0x1, 0x2, 2x2, 2x4).json: device configuration, fed to ONOS before configuration change
        - CASE*.json: interface configuration, fed to ONOS before configuration change
        - CASE*0.chart: ping chart, used to check connectivity before configuration change.
                        Shared among same test scenario with different topology.
        - CASE*0_after.chart: ping chart, used to check connectivity after configuration change.
                        Shared among same test scenario with different topology.
                        Only used when ping chart is updated.
        '''
        topo = dict()
        # (number of spine switch, number of leaf switch, dual-homed, description, port number of h1)
        topo[ '0x1' ] = ( 0, 1, False, 'single ToR', 1 )
        topo[ '0x2' ] = ( 0, 2, True, 'dual-homed ToR', 2 )
        topo[ '2x2' ] = ( 2, 2, False, '2x2 leaf-spine topology', 3 )
        topo[ '2x4' ] = ( 2, 4, True, '2x4 dual-homed leaf-spine topology', 6 )
        fanout = 4
        switchNames = {}
        switchNames[ '2x2' ] = [ "leaf1", "leaf2", "spine101", "spine102" ]

        TAG = 'CASE%d' % testIndex
        skipPackage = False
        init = False
        dualHomed = topo[ topology ][ 2 ]
        portNum = topo[ topology ][ 4 ]
        defaultIntf = 'bond0' if dualHomed else 'eth0'

        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as run
        if not hasattr( main, 'apps' ):
            init = True
            run.initTest( main )
        # Skip onos packaging if the clusrer size stays the same
        if not init and onosNodes == main.Cluster.numCtrls:
            skipPackage = True

        main.case( '%s, with %s and %d ONOS instance%s' %
                   ( description, topo[ topology ][ 3 ], onosNodes, 's' if onosNodes > 1 else '' ) )
        main.cfgName = topology
        main.Cluster.setRunningNode( onosNodes )
        run.installOnos( main, skipPackage=skipPackage, cliSleep=5 )

        # Provide common configuration
        # TODO: Generate json and chart dynamically, according to topologies and scenarios
        if main.useBmv2:
            # Translate configuration file from OVS-OFDPA to BMv2 driver
            translator.ofdpaToBmv2( main )
        else:
            translator.bmv2ToOfdpa( main )
        run.loadJson( main )
        run.loadChart( main )

        # Provide topology-specific interface configuration
        import json
        try:
            intfCfg = "%s%s%s.json" % ( main.configPath, main.forJson, TAG )
            if main.useBmv2:
                # Translate configuration file from OVS-OFDPA to BMv2 driver
                translator.ofdpaToBmv2( main, intfCfg )
            else:
                translator.bmv2ToOfdpa( main, intfCfg )
            with open( intfCfg ) as cfg:
                main.Cluster.active( 0 ).REST.setNetCfg( json.load( cfg ) )
        except IOError:
            # Load default interface configuration
            defaultIntfCfg = "%s%s%s_ports.json" % ( main.configPath, main.forJson, topology )
            if main.useBmv2:
                # Translate configuration file from OVS-OFDPA to BMv2 driver
                translator.ofdpaToBmv2( main, defaultIntfCfg )
            else:
                translator.bmv2ToOfdpa( main, defaultIntfCfg )
            with open( defaultIntfCfg ) as cfg:
                main.Cluster.active( 0 ).REST.setNetCfg( json.load( cfg ) )

        try:
            with open( "%s%sCASE%d.chart" % (main.configPath, main.forChart, testIndex / 10 * 10) ) as chart:
                main.pingChart = json.load( chart )
        except IOError:
            # Load default chart
            with open( "%s%sdefault.chart" % (main.configPath, main.forChart) ) as chart:
                main.pingChart = json.load( chart )

        # Set up topology
        if hasattr( main, 'Mininet1' ):
            # Run the test with mininet topology
            mininet_args = ' --spine=%d --leaf=%d --fanout=%d' \
                           % ( topo[ topology ][ 0 ], topo[ topology ][ 1 ], fanout )
            if len( vlan ) > 0 :
                mininet_args += ' --vlan=%s' % ( ','.join( [ '%d' % vlanId for vlanId in vlan ] ) )
                if topo[ topology ][ 0 ] > 0:
                    mininet_args += ',0,0,0,0'
            if dualHomed:
                mininet_args += ' --dual-homed'
            if main.useBmv2:
                mininet_args += ' --switch bmv2'
                main.log.info( "Using BMv2 switch" )

            run.startMininet( main, 'trellis_fabric.py', args=mininet_args )
        else:
            # Run the test with physical devices
            run.connectToPhysicalNetwork( main, switchNames[ topology ] )

        # minFlowCountPerLeaf = 13 +  [# of ports] * 5 + [# of hosts] * 2 + [# of vlan ids]
        minFlowCountPerLeaf = 13 + ( fanout + topo[ topology ][ 0 ]) * 5 + fanout * 2 + len( set( vlan ) )
        run.checkFlows( main, minFlowCount=minFlowCountPerLeaf * topo[ topology ][ 1 ], sleep=5, dumpflows=False )
        # Check connectivity before changing interface configuration
        run.pingAll( main, '%s_Before' % TAG, retryAttempts=2 )

        if main.useBmv2:
            leaf_dpid = [ "device:bmv2:leaf%d" % ( ls + 1 ) for ls in range( topo[ topology ][ 1 ] ) ]
        else:
            leaf_dpid = [ "of:%016d" % ( ls + 1 ) for ls in range( topo[ topology ][ 1 ] ) ]
        for dpid in leaf_dpid:
            run.checkFlowsByDpid( main, dpid, minFlowCountPerLeaf, sleep=5 )

        # Testcase-specific interface configuration change
        if testIndex / 10 == 1:
            # CASE11-14
            if hasattr( main, 'Mininet1' ):
                # Assign vlan tag 10 to host h1
                main.Mininet1.assignVLAN( 'h1', 'h1-%s' % defaultIntf, '10' )
                # Update port configuration of port 1
                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], tagged=[ 10, ] )
            else:
                # TODO: update physical device configuration, same for all test cases
                pass
        elif testIndex / 10 == 2:
            # CASE21-24
            if hasattr( main, 'Mininet1' ):
                # Update port configuration of port 1
                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], untagged=20 )
        elif testIndex / 10 == 3:
            # CASE31-34
            if hasattr( main, 'Mininet1' ):
                # Update port configuration of port 1
                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], untagged=110 )
                # Update port configuration of port 2
                SRDynamicConfTest.updateIntfCfg( main, portNum + 1, dualHomed,
                                                 [ '10.0.2.254/24', ], untagged=110 )
        elif testIndex / 10 == 4:
            # CASE41-44
            if hasattr( main, 'Mininet1' ):
                # Assign vlan tag 20 to host h1
                main.Mininet1.assignVLAN( 'h1', 'h1-%s' % defaultIntf, '20')
                # Update port configuration of port 1
                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], tagged=[ 20, ] )
        elif testIndex / 10 == 5:
            # CASE51-54
            if hasattr( main, 'Mininet1' ):
                # Update port configuration of port 1
                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], tagged=[ 20, ], native=10 )
        elif testIndex / 10 == 6:
            # CASE61-64
            if hasattr( main, 'Mininet1' ):
                # Update port configuration of port 1
                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], tagged=[ 120, ], native=110 )
                # Update port configuration of port 2
                SRDynamicConfTest.updateIntfCfg( main, portNum + 1, dualHomed,
                                                 [ '10.0.2.254/24', ], tagged=[ 120, ], native=110 )
        elif testIndex / 10 == 7:
            # CASE71-74
            if hasattr( main, 'Mininet1' ):
                # Update host configuration of h1
                main.Mininet1.removeVLAN( 'h1', 'h1-%s.10' % defaultIntf )
                # Update port configuration of port 1
                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], untagged=10 )
        elif testIndex / 10 == 8:
            # CASE81-84
            if hasattr( main, 'Mininet1' ):
                # Update port configuration of port 1
                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], tagged=[ 20, ], native=10 )
        elif testIndex / 10 == 9:
            # CASE91-94
            if hasattr( main, 'Mininet1' ):
                # Update host configuration
                main.Mininet1.removeVLAN( 'h1', 'h1-%s.10' % defaultIntf )
                main.Mininet1.removeVLAN( 'h2', 'h2-%s.10' % defaultIntf )

                # Update port configuration
                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], tagged=[ 120, ], native=110 )
                SRDynamicConfTest.updateIntfCfg( main, portNum + 1, dualHomed,
                                                 [ '10.0.2.254/24', ], tagged=[ 120, ], native=110 )
        elif testIndex / 10 == 10:
            # CASE101-104
            if hasattr( main, 'Mininet1' ):
                # Update port configuration
                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], untagged=20 )
        elif testIndex / 10 == 11:
            # CASE111-114
            if hasattr( main, 'Mininet1' ):
                # Update port configuration
                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], tagged=[ 20, ] )
        elif testIndex / 10 == 12:
            # CASE121-124
            if hasattr( main, 'Mininet1' ):
                # Update port configuration
                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], tagged=[ 20, ], native=110 )
                SRDynamicConfTest.updateIntfCfg( main, portNum + 1, dualHomed,
                                                 [ '10.0.2.254/24', ], tagged=[ 20, ], native=110 )
        elif testIndex / 10 == 13:
            # CASE131-134
            if hasattr( main, 'Mininet1' ):
                # Update port configuration
                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], tagged=[ 120, ], native=10 )
        elif testIndex / 10 == 14:
            # CASE141-144
            if hasattr( main, 'Mininet1' ):
                # Update port configuration
                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], tagged=[ 20, ] )
        elif testIndex / 10 == 15:
            # CASE151-154
            if hasattr( main, 'Mininet1' ):
                # Update port configuration
                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], tagged=[ 120, ] )
        elif testIndex / 10 == 16:
            # CASE161-164
            if hasattr( main, 'Mininet1' ):
                # Update port configuration
                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], tagged=[ 20, ], native=10 )
        elif testIndex / 10 == 17:
            # CASE171-174
            if hasattr( main, 'Mininet1' ):
                # Update port configuration
                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], tagged=[ 120, ] )
        elif testIndex / 10 == 18:
            # CASE181-184
            if hasattr( main, 'Mininet1' ):
                # Update port configuration
                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], tagged=[ 20, ], native=10 )
        elif testIndex / 10 == 19:
            # CASE191-194
            if hasattr( main, 'Mininet1' ):
                # Update port configuration
                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], untagged=20 )
        elif testIndex / 10 == 20:
            # CASE201-204
            if hasattr( main, 'Mininet1' ):
                # Update port configuration
                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], tagged=[ 20 ] )
        elif testIndex / 10 == 21:
            # CASE211-214
            if hasattr( main, 'Mininet1' ):
                # Update port configuration
                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], tagged=[ 20 ], native=110 )
        elif testIndex / 10 == 22:
            # CASE221-224
            if hasattr( main, 'Mininet1' ):
                # Update port configuration
                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], tagged=[ 120 ], native=10 )
        elif testIndex / 10 == 23:
            # CASE231-234
            if hasattr( main, "Mininet1" ):
                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], tagged=[ 10, ] )
                for dpid in leaf_dpid:
                    run.checkFlowsByDpid( main, dpid, minFlowCountPerLeaf, sleep=5 )
                main.pingChart[ 'leaf1' ][ 'expect' ] = False
                run.pingAll( main, '%s_1' % TAG, retryAttempts=2 )

                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], untagged=50 )
                for dpid in leaf_dpid:
                    run.checkFlowsByDpid( main, dpid, minFlowCountPerLeaf, sleep=5 )
                run.pingAll( main, '%s_2' % TAG, retryAttempts=2 )

                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], tagged=[ 20, ] )
                for dpid in leaf_dpid:
                    run.checkFlowsByDpid( main, dpid, minFlowCountPerLeaf, sleep=5 )
                run.pingAll( main, '%s_3' % TAG, retryAttempts=2 )

                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], tagged=[ 40, ], native=10 )
                for dpid in leaf_dpid:
                    run.checkFlowsByDpid( main, dpid, minFlowCountPerLeaf, sleep=5 )
                main.pingChart[ 'leaf1' ][ 'expect' ] = True
                run.pingAll( main, '%s_4' % TAG, retryAttempts=2 )

                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], tagged=[ 20, ] )
                for dpid in leaf_dpid:
                    run.checkFlowsByDpid( main, dpid, minFlowCountPerLeaf, sleep=5 )
                main.pingChart[ 'leaf1' ][ 'expect' ] = False
                run.pingAll( main, '%s_5' % TAG, retryAttempts=2 )

                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], untagged= 20 )
                for dpid in leaf_dpid:
                    run.checkFlowsByDpid( main, dpid, minFlowCountPerLeaf, sleep=5 )
                run.pingAll( main, '%s_6' % TAG, retryAttempts=2 )

                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.2.254/24', ], untagged= 10 )
                for dpid in leaf_dpid:
                    run.checkFlowsByDpid( main, dpid, minFlowCountPerLeaf, sleep=5 )
                main.pingChart[ 'leaf1' ][ 'expect' ] = True
        elif testIndex / 10 == 24:
            # CASE243-244
            # Only for 2x2 and 2x4 topology, to test reachability from other leaf
            if hasattr( main, "Mininet1" ):
                # Update host IP and default GW
                main.Mininet1.changeIP( 'h1', 'h1-%s' % defaultIntf, '10.0.6.1', '255.255.255.0' )
                main.Mininet1.changeDefaultGateway( 'h1', '10.0.6.254' )
                # Update port configuration
                SRDynamicConfTest.updateIntfCfg( main, portNum, dualHomed,
                                                 [ '10.0.6.254/24', ], untagged=60 )

        # Update ping chart in case it is changed
        try:
            with open( "%s%sCASE%d_after.chart" % (main.configPath, main.forChart, testIndex / 10 * 10 ) ) as chart:
                main.pingChart = json.load(chart)
        except IOError:
            main.log.debug( "Ping chart is not changed" )

        # Check connectivity after changing interface configuration
        run.checkFlows( main, minFlowCount=minFlowCountPerLeaf * topo[ topology ][ 1 ], sleep=5, dumpflows=False )
        run.pingAll( main, '%s_After' % TAG, retryAttempts=2 )

        run.cleanup( main )

    @staticmethod
    def updateIntfCfg( main, portNum, dualHomed, ips=[], untagged=0, tagged=[], native=0 ):
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as run
        if main.useBmv2:
            run.updateIntfCfg( main, "device:bmv2:leaf1/%d" % portNum,
                               ips=ips, untagged=untagged, tagged=tagged, native=native )
        else:
            run.updateIntfCfg( main, "of:0000000000000001/%d" % portNum,
                               ips=ips, untagged=untagged, tagged=tagged, native=native )
        if dualHomed:
            if main.useBmv2:
                run.updateIntfCfg( main, "device:bmv2:leaf2/%d" % portNum,
                                   ips=ips, untagged=untagged, tagged=tagged, native=native )
            else:
                run.updateIntfCfg( main, "of:0000000000000002/%d" % portNum,
                                   ips=ips, untagged=untagged, tagged=tagged, native=native )
