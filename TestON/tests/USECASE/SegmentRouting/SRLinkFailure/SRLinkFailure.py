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
# In this test we perform a link failure and then test for connectivity
# CASE1: 2x2 topo + link failure + IP connectivity test
# CASE2: 4x4 topo + link failure + IP connectivity test
# CASE4: 2x2 topo + 3-node ONOS CLUSTER + link failure + IP connectivity test
# CASE5: 4x4 topo + 3-node ONOS CLUSTER + link failure + IP connectivity test


class SRLinkFailure:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        Sets up 1-node Onos-cluster
        Start 2x2 Leaf-Spine topology
        Pingall
        Cause link failure
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRLinkFailure.dependencies.SRLinkFailFuncs import SRLinkFailFuncs
        except ImportError:
            main.log.error( "SRLinkFailFuncs not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRLinkFailFuncs()

        main.funcs.runTest( main, 1, 1, '2x2', 116 )

    def CASE2( self, main ):
        """
        Sets up 1-node Onos-cluster
        Start 4x4 Leaf-Spine topology
        Pingall
        Cause link failure
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRLinkFailure.dependencies.SRLinkFailFuncs import SRLinkFailFuncs
        except ImportError:
            main.log.error( "SRLinkFailFuncs not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRLinkFailFuncs()

        main.funcs.runTest( main, 2, 1, '4x4', 350 )

    def CASE4( self, main ):
        """
        Sets up 3-node Onos-cluster
        Start 2x2 Leaf-Spine topology
        Pingall
        Cause link failure
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRLinkFailure.dependencies.SRLinkFailFuncs import SRLinkFailFuncs
        except ImportError:
            main.log.error( "SRLinkFailFuncs not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRLinkFailFuncs()

        main.funcs.runTest( main, 3, 3, '2x2', 116 )

    def CASE5( self, main ):
        """
        Sets up 1-node Onos-cluster
        Start 4x4 Leaf-Spine topology
        Pingall
        Cause link failure
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRLinkFailure.dependencies.SRLinkFailFuncs import SRLinkFailFuncs
        except ImportError:
            main.log.error( "SRLinkFailFuncs not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRLinkFailFuncs()

        main.funcs.runTest( main, 4, 3, '4x4', 350 )
