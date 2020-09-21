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

class SRLinkFailFuncs():

    def __init__( self ):
        self.default = ''
        self.topo = dict()
        self.topo[ '0x1' ] = ( 0, 1, '--leaf=1 --spine=0', 'single switch' )
        self.topo[ '2x2' ] = ( 2, 2, '', '2x2 Leaf-spine' )
        self.topo[ '4x4' ] = ( 4, 4, '--leaf=4 --spine=4', '4x4 Leaf-spine' )
        main.switchType = "ovs"
        self.switchOne = 'spine101'
        self.switchTwo = 'leaf2'
        self.dpidOne = 'of:0000000000000101'
        self.dpidTwo = 'of:0000000000000002'
        self.portOne = '2'
        self.portTwo = '3'

    def runTest( self, main, caseNum, numNodes, Topo, minFlow ):
        try:
            description = "Bridging and Routing Link Failure test with " + self.topo[ Topo ][ 3 ] + " and {} Onos".format( numNodes )
            main.case( description )
            if not hasattr( main, 'apps' ):
                run.initTest( main )
            main.cfgName = Topo
            main.Cluster.setRunningNode( numNodes )
            run.installOnos( main )
            suf = main.params.get( 'jsonFileSuffix', '')
            xconnectFile = "%s%s-xconnects.json%s" % ( main.configPath + main.forJson,
                    main.cfgName, suf )
            if main.useBmv2:
                switchPrefix = main.params[ 'DEPENDENCY' ].get( 'switchPrefix', "bmv2" )
                # Translate configuration file from OVS-OFDPA to BMv2 driver
                translator.bmv2ToOfdpa( main ) # Try to cleanup if switching between switch types
                translator.ofdpaToBmv2( main, switchPrefix=switchPrefix )
                # translate xconnects
                translator.bmv2ToOfdpa( main, cfgFile=xconnectFile )
                translator.ofdpaToBmv2( main, cfgFile=xconnectFile, switchPrefix=switchPrefix )
            else:
                translator.bmv2ToOfdpa( main )
                translator.bmv2ToOfdpa( main, cfgFile=xconnectFile )
            if suf:
                run.loadJson( main, suffix=suf )
            else:
                run.loadJson( main )
            run.loadChart( main )
            if hasattr( main, 'Mininet1' ):
                run.mnDockerSetup( main )  # optionally create and setup docker image

                # Run the test with Mininet
                mininet_args = self.topo[ Topo ][ 2 ]
                if main.useBmv2:
                    mininet_args += ' --switch %s' % main.switchType
                    main.log.info( "Using %s switch" % main.switchType )

                run.startMininet( main, 'cord_fabric.py', args=mininet_args )
            else:
                # Run the test with physical devices
                # TODO: connect TestON to the physical network
                pass
            # xconnects need to be loaded after topology
            run.loadXconnects( main )
            # pre-configured routing and bridging test
            run.checkFlows( main, minFlowCount=minFlow )
            run.pingAll( main )
            switch = self.topo[ Topo ][ 0 ] + self.topo[ Topo ][ 1 ]
            link = ( self.topo[ Topo ][ 0 ] + self.topo[ Topo ][ 1 ] ) * self.topo[ Topo ][ 0 ]
            # link failure
            run.killLink( main, self.switchOne, self.switchTwo, switches='{}'.format( switch ), links='{}'.format( link - 2 ) )
            run.pingAll( main, "CASE{}_Failure".format( caseNum ) )
            run.restoreLink( main, self.switchOne, self.switchTwo, '{}'.format( switch ), '{}'.format( link ),
                             True, self.dpidOne, self.dpidTwo, self.portOne, self.portTwo )
            run.pingAll( main, "CASE{}_Recovery".format( caseNum ) )
            # TODO Dynamic config of hosts in subnet
            # TODO Dynamic config of host not in subnet
            # TODO Dynamic config of vlan xconnect
            # TODO Vrouter integration
            # TODO Mcast integration
        except Exception as e:
            main.log.exception( "Error in runTest" )
            main.skipCase( result="FAIL", msg=e )
        finally:
            run.cleanup( main )
