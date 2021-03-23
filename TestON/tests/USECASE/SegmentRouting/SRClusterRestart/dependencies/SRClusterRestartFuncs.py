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
        self.topo = run.getTopo()

    def runTest( self, main, caseNum, numNodes, topology, minFlow, testing, killList=[ 0, 1, 2 ] ):
        try:
            description = "Cluster Restart test with " + self.topo[ topology ][ 'description' ]
            caseTitle = 'CASE{}_'.format( caseNum ) + testing
            main.case( description )
            if not hasattr( main, 'apps' ):
                run.initTest( main )
            main.cfgName = topology
            main.Cluster.setRunningNode( numNodes )
            run.installOnos( main )
            if not main.persistentSetup:
                run.loadJson( main )
            run.loadChart( main )
            if hasattr( main, 'Mininet1' ):
                run.startMininet( main, 'cord_fabric.py', args=self.topo[ topology ][ 'mininetArgs' ] )
            else:
                # Run the test with physical devices
                # TODO: connect TestON to the physical network
                pass
            # xconnects need to be loaded after topology
            run.loadXconnects( main )
            # pre-configured routing and bridging test
            run.checkFlows( main, minFlowCount=minFlow )
            run.pingAll( main )
            switch = '{}'.format( self.topo[ topology ][ 'spines' ] + self.topo[ topology ][ 'leaves' ] )
            link = '{}'.format( ( self.topo[ topology ][ 'spines' ] + self.topo[ topology ][ 'leaves' ] ) * self.topo[ topology ][ 'spines' ] )
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
