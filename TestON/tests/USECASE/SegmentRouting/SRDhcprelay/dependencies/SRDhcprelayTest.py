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

class SRDhcprelayTest ():

    def __init__( self ):
        self.default = ''

    @staticmethod
    def runTest( main, testIndex, onosNodes, description, dhcpRelay=False, remoteServer=False, multipleServer=False, ipv6=False, vlan=[], dualHomed=False ):
        skipPackage = False
        init = False
        if not hasattr( main, 'apps' ):
            init = True
            run.initTest( main )
        # Skip onos packaging if the clusrer size stays the same
        if not init and onosNodes == main.Cluster.numCtrls:
            skipPackage = True

        main.case( '%s, with %d ONOS instance%s' %
                   ( description, onosNodes, 's' if onosNodes > 1 else '' ) )

        main.cfgName = 'CASE%02d' % testIndex
        main.resultFileName = 'CASE%02d' % testIndex
        main.Cluster.setRunningNode( onosNodes )
        run.installOnos( main, skipPackage=skipPackage, cliSleep=5 )
        if main.useBmv2:
            # Translate configuration file from OVS-OFDPA to BMv2 driver
            translator.ofdpaToBmv2( main )
        else:
            translator.bmv2ToOfdpa( main )
        run.loadJson( main )
        run.loadHost( main )
        if hasattr( main, 'Mininet1' ):
            # Run the test with Mininet
            if dualHomed:
                mininet_args = ' --spine=2 --leaf=4 --dual-homed'
            else:
                mininet_args = ' --spine=2 --leaf=2'
            mininet_args += ' --dhcp-client'
            if dhcpRelay:
                mininet_args += ' --dhcp-relay'
                if multipleServer:
                    mininet_args += ' --multiple-dhcp-server'
            if remoteServer:
                mininet_args += ' --remote-dhcp-server'
            if ipv6:
                mininet_args += ' --ipv6'
            if len( vlan ) > 0 :
                mininet_args += ' --vlan=%s' % ( ','.join( ['%d' % vlanId for vlanId in vlan ] ) )
            if main.useBmv2:
                mininet_args += ' --switch bmv2'
                main.log.info( "Using BMv2 switch" )

            run.startMininet( main, 'trellis_fabric.py', args=mininet_args )
        else:
            # Run the test with physical devices
            # TODO: connect TestON to the physical network
            pass
        run.verifyOnosHostIp( main )
        run.verifyNetworkHostIp( main )

        run.cleanup( main )
