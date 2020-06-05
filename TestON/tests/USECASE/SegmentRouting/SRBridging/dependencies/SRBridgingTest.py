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
            if 'MN_DOCKER' in main.params and main.params['MN_DOCKER']['args']:
                main.log.info( "Creating Mininet Docker" )
                main.Mininet1.dockerPrompt = '#'
                # Start docker container
                handle = main.Mininet1.handle
                handle.sendline( "docker run %s %s" % ( main.params[ 'MN_DOCKER' ][ 'args' ], main.params[ 'MN_DOCKER' ][ 'name' ] ) )
                handle.expect( main.Mininet1.bashPrompt )
                output = handle.before + handle.after
                main.log.debug( repr(output) )
                startStr = main.params[ 'MN_DOCKER' ][ 'name' ]
                endStr = main.Mininet1.user_name
                start = output.find( startStr ) + len( startStr )
                end = output.find( endStr )
                containerId = output[start:end].strip()
                main.log.debug( repr( containerId ) )

                handle = main.Mininet1.handle
                handle.sendline( "docker attach %s " % containerId )  # Strip?
                handle.expect( main.Mininet1.dockerPrompt )
                main.log.debug( handle.before + handle.after )
                # We should be good to go
                main.Mininet1.prompt = main.Mininet1.dockerPrompt
                main.Mininet1.sudoRequired = False


            # Run the test with Mininet
            mininet_args = ' --spine=%d --leaf=%d' % ( self.topo[ topology ][ 0 ], self.topo[ topology ][ 1 ] )
            if self.topo[ topology ][ 2 ]:
                mininet_args += ' --dual-homed'
            if len( vlan ) > 0 :
                mininet_args += ' --vlan=%s' % ( ','.join( ['%d' % vlanId for vlanId in vlan ] ) )
            if main.useBmv2:
                switchType = main.params[ 'DEPENDENCY' ].get( 'bmv2SwitchType', 'stratum' )
                mininet_args += ' --switch %s' % switchType
                main.log.info( "Using %s switch" % switchType )

            run.startMininet( main, 'trellis_fabric.py', args=mininet_args )

            if main.useBmv2:
                filename = "onos-netcfg.json"
                for switch in main.Mininet1.getSwitches(switchRegex=r"(StratumBmv2Switch)|(Bmv2Switch)").keys():
                    path = "/tmp/mn-stratum/%s/" % switch
                    main.ONOSbench1.handle.sendline( "sudo sed -i 's/localhost/%s/g' %s%s" % ( main.Mininet1.ip_address, path, filename ) )
                    main.ONOSbench1.handle.expect( main.ONOSbench1.prompt )
                    main.log.debug( main.ONOSbench1.handle.before + main.ONOSbench1.handle.after )
                    main.ONOSbench1.handle.sendline( "sudo sed -i 's/device:%s/device:bmv2:%s/g' %s%s" % ( switch, switch, path, filename ) )
                    main.ONOSbench1.handle.expect( main.ONOSbench1.prompt )
                    main.log.debug( main.ONOSbench1.handle.before + main.ONOSbench1.handle.after )
                    main.ONOSbench1.onosNetCfg( main.ONOSserver1.ip_address, path, filename )

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
        if 'MN_DOCKER' in main.params and main.params['MN_DOCKER']['args']:
                main.log.info( "Deleting Mininet Docker" )

                # Detach from container
                handle = main.Mininet1.handle
                try:
                    handle.sendline( "exit" )  # ctrl-p ctrk-q  to detach from container
                    import time
                    time.sleep(5)
                    handle.expect( main.Mininet1.dockerPrompt )
                    main.log.debug( handle.before + handle.after )
                    main.Mininet1.prompt = main.Mininet1.bashPrompt
                    handle.expect( main.Mininet1.prompt )
                    main.log.debug( handle.before + handle.after )
                    main.Mininet1.sudoRequired = True
                except Exception as e:
                    main.log.error( e )

                # We should be good to go
