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

import time
from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as run

class SRMulticastTest ():

    def __init__( self ):
        self.default = ''
        self.switchNames = [ "leaf205", "leaf206", "spine227", "spine228" ]

    def runTest( self, main, test_idx, onosNodes, description, removeRoute=False, linkFailure=False, switchFailure=False ):
        skipPackage = False
        init = False
        if not hasattr( main, 'apps' ):
            init = True
            run.initTest( main )
        # Skip onos packaging if the cluster size stays the same
        if not init and onosNodes == main.Cluster.numCtrls:
            skipPackage = True

        main.resultFileName = 'CASE%03d' % test_idx
        main.Cluster.setRunningNode( onosNodes )
        run.installOnos( main, skipPackage=skipPackage, cliSleep=5 )
        # Load configuration files
        main.step("Load configurations")
        main.cfgName = 'TEST_CONFIG_ipv4=1_ipv6=1_dhcp=1_routers=1'
        run.loadJson( main )
        main.cfgName = 'CASE%03d' % test_idx
        run.loadMulticastConfig( main )
        if linkFailure:
            run.loadLinkFailureChart( main )
        if switchFailure:
            run.loadSwitchFailureChart( main )
        time.sleep( float( main.params[ 'timers' ][ 'loadNetcfgSleep' ] ) )

        if hasattr( main, 'Mininet1' ):
            # Run the test with Mininet
            mininet_args = ' --dhcp=1 --routers=1 --ipv6=1 --ipv4=1'
            run.startMininet( main, main.params['DEPENDENCY']['topology'], args=mininet_args )
            time.sleep( float( main.params[ 'timers' ][ 'startMininetSleep' ] ) )
        else:
            # Run the test with physical devices
            run.connectToPhysicalNetwork( main, self.switchNames )
            # Check if the devices are up
            run.checkDevices( main, switches=len( self.switchNames ) )

        # Create scapy components
        run.startScapyHosts( main )

        for entry in main.multicastConfig:
            main.step("Verify adding multicast route with group IP {}".format(entry["group"]))
            # Create a multicast route
            main.Cluster.active( 0 ).CLI.mcastHostJoin( entry["sIP"], entry["group"], entry["sPorts"], entry["dHosts"] )
            time.sleep( float( main.params[ 'timers' ][ 'mcastSleep' ] ) )
            # Check the flows against the devices
            # run.checkFlows( main, minFlowCount=2, sleep=5 )
            # Verify multicast traffic
            run.verifyMulticastTraffic( main, entry, True, skipOnFail=True )

            # Test switch failures
            if switchFailure:
                for switch, expected in main.switchFailureChart.items():
                    run.killSwitch( main, switch, expected['switches_after_failure'], expected['links_after_failure'] )
                    run.verifyMulticastTraffic( main, entry, True, skipOnFail=True )

                    run.recoverSwitch( main, switch, expected['switches_before_failure'], expected['links_before_failure'] )
                    run.verifyMulticastTraffic( main, entry, True, skipOnFail=True )

            # Test link failures
            if linkFailure:
                for link_batch_name, info in main.linkFailureChart.items():
                    linksToRemove = info['links'].values()
                    linksBefore = info['links_before']
                    linksAfter = info['links_after']

                    run.killLinkBatch( main, linksToRemove, linksAfter, switches=10 )
                    run.verifyMulticastTraffic( main, entry, True, skipOnFail=True )

                    run.restoreLinkBatch( main, linksToRemove, linksBefore, switches=10 )
                    run.verifyMulticastTraffic( main, entry, True, skipOnFail=True )

            if removeRoute:
                main.step("Verify deleting multicast route with group IP {}".format(entry["group"]))
                # delete a multicast route
                main.Cluster.active( 0 ).CLI.mcastHostDelete( entry["sIP"], entry["group"] )
                time.sleep( float( main.params[ 'timers' ][ 'mcastSleep' ] ) )
                # Check the flows against the devices
                # run.checkFlows( main, minFlowCount=2, sleep=5 )
                # Verify multicast traffic (traffic check is expected to fail)
                run.verifyMulticastTraffic( main, entry, False, skipOnFail=True )

        # Clean up the environment
        run.cleanup( main, copyKarafLog=False )
