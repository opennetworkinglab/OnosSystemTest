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

class SRRoutingTest ():

    topo = {}

    def __init__( self ):
        self.default = ''

    @staticmethod
    def runTest( main, test_idx, onosNodes, dhcp, routers, ipv4, ipv6, description):

        skipPackage = False
        init = False
        if not hasattr( main, 'apps' ):
            init = True
            run.initTest( main )

        # Skip onos packaging if the cluster size stays the same
        if not init and onosNodes == main.Cluster.numCtrls:
            skipPackage = True

        main.case('%s, ONOS instance%s' %
                  (description, onosNodes))

        main.cfgName = 'COMCAST_CONFIG_ipv4=%d_ipv6=%d_dhcp=%d_routers=%d' % \
            (ipv4, ipv6, dhcp, routers)
        main.configPath = main.path + "/dependencies/"
        main.resultFileName = 'CASE%02d' % test_idx
        main.Cluster.setRunningNode(onosNodes)

        run.installOnos(main, skipPackage=skipPackage, cliSleep=5,
                        parallel=False)

        if hasattr(main, 'Mininet1'):
            # Run the test with Mininet
            mininet_args = ' --dhcp=%s --routers=%s --ipv6=%s --ipv4=%s' % (dhcp, routers, ipv6, ipv4)
            run.startMininet(main, 'comcast_fabric.py', args=mininet_args)
        else:
            # Run the test with physical devices
            # TODO: connect TestON to the physical network
            pass

        # ping hosts
        main.Network.pingAll()

        if hasattr(main, 'Mininet1'):
            run.cleanup(main)
        else:
            # TODO: disconnect TestON from the physical network
            pass
