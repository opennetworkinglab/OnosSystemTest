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
import time
import json

class SRRoutingTest ():

    topo = {}

    def __init__( self ):
        self.default = ''

    @staticmethod
    def runTest( main, test_idx, onosNodes, dhcp, routers, ipv4, ipv6,
                 description, countFlowsGroups=False, checkExternalHost=False,
                 staticRouteConfigure=False, switchFailure=False, linkFailure=False,
                 nodeFailure=False ):

        skipPackage = False
        init = False
        if not hasattr( main, 'apps' ):
            init = True
            run.initTest( main )

        # Skip onos packaging if the cluster size stays the same
        if not init and onosNodes == main.Cluster.numCtrls:
            skipPackage = True

        main.case( '%s, ONOS cluster size: %s' % ( description, onosNodes ) )

        main.cfgName = 'COMCAST_CONFIG_ipv4=%d_ipv6=%d_dhcp=%d_routers=%d' % \
            ( ipv4, ipv6, dhcp, routers )
        if checkExternalHost:
            main.cfgName += '_external=1'
        if staticRouteConfigure:
            main.cfgName += '_static=1'

        main.resultFileName = 'CASE%03d' % test_idx
        main.Cluster.setRunningNode( onosNodes )

        run.installOnos( main, skipPackage=skipPackage, cliSleep=5,
                         parallel=False )

        # Load configuration files
        run.loadJson( main )
        run.loadChart( main )
        run.loadHost( main )

        # if static route flag add routes
        # these routes are topology specific
        if (staticRouteConfigure):
            if (ipv4):
                run.addStaticOnosRoute( main, "10.0.88.0/24", "10.0.1.1")
            if (ipv6):
                run.addStaticOnosRoute( main, "2000::8700/120", "2000::101")

        if countFlowsGroups:
            run.loadCount( main )
        if switchFailure:
            run.loadSwitchFailureChart( main )
        if linkFailure:
            run.loadLinkFailureChart( main )

        # wait some time
        time.sleep( 5 )

        if hasattr( main, 'Mininet1' ):
            # Run the test with Mininet
            mininet_args = ' --dhcp=%s --routers=%s --ipv6=%s --ipv4=%s' % ( dhcp, routers, ipv6, ipv4 )
            run.startMininet( main, 'comcast_fabric.py', args=mininet_args )
        else:
            # Run the test with physical devices
            # TODO: connect TestON to the physical network
            pass

        # wait some time for onos to install the rules!
        time.sleep( 25 )
        if ( dhcp ):
            time.sleep( 60 )

        SRRoutingTest.runChecks( main, test_idx, countFlowsGroups )

        # Test switch failures
        if switchFailure:
            for switch, expected in main.switchFailureChart.items():
                run.killSwitch( main, switch, expected['switches_after_failure'], expected['links_after_failure'] )
                SRRoutingTest.runChecks( main, test_idx, countFlowsGroups )

                run.recoverSwitch( main, switch, expected['switches_before_failure'], expected['links_before_failure'] )
                SRRoutingTest.runChecks( main, test_idx, countFlowsGroups )

        # Test link failures
        if linkFailure:
            for link_batch_name, info in main.linkFailureChart.items():

                linksToRemove = info['links'].values()
                linksBefore = info['links_before']
                linksAfter = info['links_after']

                run.killLinkBatch( main, linksToRemove, linksAfter )
                SRRoutingTest.runChecks( main, test_idx, countFlowsGroups )

                run.restoreLinkBatch( main, linksToRemove, linksBefore )
                SRRoutingTest.runChecks( main, test_idx, countFlowsGroups )

        # Test node failures
        if nodeFailure:
            numCtrls = len( main.Cluster.runningNodes )
            links = len( json.loads( main.Cluster.next().links() ) )
            switches = len( json.loads( main.Cluster.next().devices() ) )
            for ctrl in xrange( numCtrls ):
                # Kill node
                run.killOnos( main, [ ctrl ], switches, links, ( numCtrls - 1 ) )
                time.sleep( float( main.params[ 'timers' ][ 'SwitchDiscovery' ] ) )
                main.Cluster.active(0).CLI.balanceMasters()
                time.sleep( float( main.params[ 'timers' ][ 'SwitchDiscovery' ] ) )
                SRRoutingTest.runChecks( main, test_idx, countFlowsGroups )

                # Recover node
                run.recoverOnos( main, [ ctrl ], switches, links, numCtrls )
                time.sleep( float( main.params[ 'timers' ][ 'SwitchDiscovery' ] ) )
                main.Cluster.active(0).CLI.balanceMasters()
                time.sleep( float( main.params[ 'timers' ][ 'SwitchDiscovery' ] ) )
                SRRoutingTest.runChecks( main, test_idx, countFlowsGroups )

        # Cleanup
        if hasattr( main, 'Mininet1' ):
            run.cleanup( main )
        else:
            # TODO: disconnect TestON from the physical network
            pass

    @staticmethod
    def runChecks( main, test_idx, countFlowsGroups ):
        # Verify host IP assignment
        run.verifyOnosHostIp( main )
        run.verifyNetworkHostIp( main )
        # check flows / groups numbers
        if countFlowsGroups:
            run.checkFlowsGroupsFromFile( main )
        # ping hosts
        run.pingAll( main, 'CASE%03d' % test_idx, acceptableFailed=5, basedOnIp=True )
