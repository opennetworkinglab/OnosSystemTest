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
import random
from random import randint
from datetime import datetime

class SRDynamicFuncs():

    def __init__( self ):
        self.default = ''
        self.topo = run.getTopo()

    def runTest( self, main, caseNum, numNodes, topology, minBeforeFlow, minAfterFlow, killOnosAndDeleteCfg ):
        try:
            if not hasattr( main, 'apps' ):
                run.initTest( main )

            description = "Bridging and Routing sanity test with " + \
                          self.topo[ topology ][ 'description' ] + \
                          "and {} nodes.".format( numNodes ) + \
                          ( "\nAlso, killing the first Onos and removing the host cfg." if killOnosAndDeleteCfg else "" )
            main.case( description )

            main.cfgName = topology
            main.Cluster.setRunningNode( numNodes )
            run.installOnos( main )
            if not main.persistentSetup:
                run.loadJson( main )
            run.loadChart( main )
            run.startMininet( main, 'cord_fabric.py',
                              args=self.topo[ topology ][ 'mininetArgs' ] )
            # pre-configured routing and bridging test
            run.checkFlows( main, minFlowCount=minBeforeFlow )
            run.pingAll( main, dumpflows=False )
            run.addHostCfg( main )
            run.checkFlows( main, minFlowCount=minAfterFlow, dumpflows=False )
            run.pingAll( main )
            if killOnosAndDeleteCfg:
                switch = self.topo[ topology ][ 'spines' ] + self.topo[ topology ][ 'leaves' ]
                link = ( self.topo[ topology ][ 'spines' ] + self.topo[ topology ][ 'leaves' ] ) * self.topo[ topology ][ 'spines' ]
                self.killAndDelete( main, caseNum, numNodes, minBeforeFlow, switch, link )
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

    def killAndDelete( self, main, caseNum, numNodes, minBeforeFlow, switch, link ):
        run.killOnos( main, [ 0 ], '{}'.format( switch ), '{}'.format( link ), '{}'.format( numNodes - 1 ) )
        run.delHostCfg( main )
        run.checkFlows( main, minFlowCount=minBeforeFlow, dumpflows=False )
        run.pingAll( main, "CASE{}_After".format( caseNum ) )
