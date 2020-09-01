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

class SRClusterRestartFuncs():

    def __init__( self ):
        self.default = ''
        self.topo = dict()
        self.topo[ '0x1' ] = ( 0, 1, '--leaf=1 --spine=0', 'single switch' )
        self.topo[ '2x2' ] = ( 2, 2, '', '2x2 Leaf-spine' )
        self.topo[ '4x4' ] = ( 4, 4, '--leaf=4 --spine=4', '4x4 Leaf-spine' )

    def runTest( self, main, caseNum, numNodes, Topo, minFlow, testing, killList=[ 0, 1, 2 ] ):
        try:
            description = "Cluster Restart test with " + self.topo[ Topo ][ 3 ]
            caseTitle = 'CASE{}_'.format( caseNum ) + testing
            main.case( description )
            if not hasattr( main, 'apps' ):
                run.initTest( main )
            main.cfgName = Topo
            main.Cluster.setRunningNode( numNodes )
            run.installOnos( main )
            run.loadJson( main )
            run.loadChart( main )
            if hasattr( main, 'Mininet1' ):
                run.startMininet( main, 'cord_fabric.py', args=self.topo[ Topo ][ 2 ] )
            else:
                # Run the test with physical devices
                # TODO: connect TestON to the physical network
                pass
            # pre-configured routing and bridging test
            run.checkFlows( main, minFlowCount=minFlow )
            run.pingAll( main )
            switch = '{}'.format( self.topo[ Topo ][ 0 ] + self.topo[ Topo ][ 1 ] )
            link = '{}'.format( ( self.topo[ Topo ][ 0 ] + self.topo[ Topo ][ 1 ] ) * self.topo[ Topo ][ 0 ] )
            run.killOnos( main, killList, switch, link, '0' )
            run.pingAll( main, caseTitle, dumpflows=False )
            run.recoverOnos( main, killList, switch, link, '{}'.format( numNodes ) )
            run.checkFlows( main, minFlowCount=minFlow, tag=caseTitle )
            run.pingAll( main, caseTitle )
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
