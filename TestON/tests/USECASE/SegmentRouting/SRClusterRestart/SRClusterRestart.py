"""
Copyright 2016 Open Networking Foundation ( ONF )

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
# CASE1: 2x2 topo + 3-node ONOS CLUSTER + IP connectivity test + CLUSTER restart
# CASE2: 4x4 topo + 3-node ONOS CLUSTER + IP connectivity test + CLUSTER restart
# CASE3: Single switch + 3-node ONOS CLUSTER + IP connectivity test + CLUSTER restart


class SRClusterRestart:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        Sets up 3-node Onos-cluster
        Start 2x2 Leaf-Spine topology
        Pingall
        Induce CLUSTER restart
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRClusterRestart.dependencies.SRClusterRestartFuncs import SRClusterRestartFuncs
        except ImportError:
            main.log.error( "SRClusterRestartFuncs not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRClusterRestartFuncs()
        main.funcs.runTest( main, 1, 3,
                            '2x2', 116, 'Failure' )

    def CASE2( self, main ):
        """
        Sets up 3-node Onos-cluster
        Start 4x4 Leaf-Spine topology
        Pingall
        Induce Cluster Restart
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRClusterRestart.dependencies.SRClusterRestartFuncs import SRClusterRestartFuncs
        except ImportError:
            main.log.error( "SRClusterRestartFuncs not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRClusterRestartFuncs()
        main.funcs.runTest( main, 2, 3,
                            '4x4', 350, 'Failure' )

    def CASE3( self, main ):
        """
        Sets up 3-node Onos-cluster
        Start single switch topology
        Pingall
        Induce Cluster Restart
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRClusterRestart.dependencies.SRClusterRestartFuncs import SRClusterRestartFuncs
        except ImportError:
            main.log.error( "SRClusterRestartFuncs not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRClusterRestartFuncs()
        main.funcs.runTest( main, 3, 3,
                            '0x1', 15, 'Failure' )

