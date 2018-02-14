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
# In this test we perform several failures and then test for connectivity
# CASE1: 2x2 topo + 3 ONOS + | ONOS failure + IP connectivity test | x failures
# CASE2: 2x2 topo + 3 ONOS + | ONOS ( random instance ) failure + IP connectivity test | x failures
# CASE3: 4x4 topo + 3 ONOS + | ONOS failure + IP connectivity test | x failures
# CASE4: 4x4 topo + 3 ONOS + | ONOS ( random instance ) failure + IP connectivity test | x failures
# CASE5: 2x2 topo + 3 ONOS + | ONOS failure + Spine failure + IP connectivity test | x failures
# CASE6: 2x2 topo + 3 ONOS + | ONOS ( random instance ) failure + Spine ( random switch ) failure + IP connectivity test | x failures
# CASE7: 4x4 topo + 3 ONOS + | ONOS failure + Spine failure + IP connectivity test | x failures
# CASE8: 4x4 topo + 3 ONOS + | ONOS ( random instance ) failure + Spine ( random switch ) failure + IP connectivity test | x failures


class SRHighAvailability:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        1 ) Sets up 3-nodes Onos-cluster
        2 ) Start 2x2 Leaf-Spine topology
        3 ) Pingall
        4 ) Cause sequential ONOS failure
        5 ) Pingall
        6 ) Repeat 3 ), 4 ), 5 ) 'failures' times
        """
        try:
            from tests.USECASE.SegmentRouting.SRHighAvailability.dependencies.SRHAFuncs import SRHAFuncs
        except ImportError:
            main.log.error( "SRHAFuncs not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRHAFuncs()
        main.funcs.runTest( main, 1, 3, '2x2',
                            116, False, False )

    def CASE2( self, main ):
        """
        1 ) Sets up 3-nodes Onos-cluster
        2 ) Start 2x2 Leaf-Spine topology
        3 ) Pingall
        4 ) Cause random ONOS failure
        5 ) Pingall
        6 ) Repeat 3 ), 4 ), 5 ) 'failures' times
        """
        try:
            from tests.USECASE.SegmentRouting.SRHighAvailability.dependencies.SRHAFuncs import SRHAFuncs
        except ImportError:
            main.log.error( "SRHAFuncs not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRHAFuncs()
        main.funcs.runTest( main, 2, 3, '2x2',
                            116, True, False )

    def CASE3( self, main ):
        """
        1 ) Sets up 3-nodes Onos-cluster
        2 ) Start 4x4 Leaf-Spine topology
        3 ) Pingall
        4 ) Cause sequential ONOS failure
        5 ) Pingall
        6 ) Repeat 3 ), 4 ), 5 ) 'failures' times
        """
        try:
            from tests.USECASE.SegmentRouting.SRHighAvailability.dependencies.SRHAFuncs import SRHAFuncs
        except ImportError:
            main.log.error( "SRHAFuncs not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRHAFuncs()
        main.funcs.runTest( main, 3, 3, '4x4',
                            350, False, False )

    def CASE4( self, main ):
        """
        1 ) Sets up 3-nodes Onos-cluster
        2 ) Start 4x4 Leaf-Spine topology
        3 ) Pingall
        4 ) Cause random ONOS failure
        5 ) Pingall
        6 ) Repeat 3 ), 4 ), 5 ) 'failures' times
        """
        try:
            from tests.USECASE.SegmentRouting.SRHighAvailability.dependencies.SRHAFuncs import SRHAFuncs
        except ImportError:
            main.log.error( "SRHAFuncs not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRHAFuncs()
        main.funcs.runTest( main, 4, 3, '4x4',
                            350, True, False )

    def CASE5( self, main ):
        """
        1 ) Sets up 3-nodes Onos-cluster
        2 ) Start 2x2 Leaf-Spine topology
        3 ) Pingall
        4 ) Cause sequential ONOS failure
        5 ) Pingall
        6 ) Cause sequential Spine failure
        7 ) Pingall
        8 ) Repeat 3 ), 4 ), 5 ), 6 ), 7 ), 'failures' times
        """
        try:
            from tests.USECASE.SegmentRouting.SRHighAvailability.dependencies.SRHAFuncs import SRHAFuncs
        except ImportError:
            main.log.error( "SRHAFuncs not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRHAFuncs()
        main.funcs.runTest( main, 5, 3, '2x2',
                            116, False, True )

    def CASE6( self, main ):
        """
        1 ) Sets up 3-nodes Onos-cluster
        2 ) Start 2x2 Leaf-Spine topology
        3 ) Pingall
        4 ) Cause random ONOS failure
        5 ) Pingall
        6 ) Cause random Spine failure
        7 ) Pingall
        8 ) Repeat 3 ), 4 ), 5 ), 6 ), 7 ) 'failures' times
        """
        try:
            from tests.USECASE.SegmentRouting.SRHighAvailability.dependencies.SRHAFuncs import SRHAFuncs
        except ImportError:
            main.log.error( "SRHAFuncs not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRHAFuncs()
        main.funcs.runTest( main, 6, 3, '2x2',
                            116, True, True )

    def CASE7( self, main ):
        """
        1 ) Sets up 3-nodes Onos-cluster
        2 ) Start 4x4 Leaf-Spine topology
        3 ) Pingall
        4 ) Cause sequential ONOS failure
        5 ) Pingall
        6 ) Cause sequential Spine failure
        7 ) Pingall
        8 ) Repeat 3 ), 4 ), 5 ), 6 ), 7 ), 'failures' times
        """
        try:
            from tests.USECASE.SegmentRouting.SRHighAvailability.dependencies.SRHAFuncs import SRHAFuncs
        except ImportError:
            main.log.error( "SRHAFuncs not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRHAFuncs()
        main.funcs.runTest( main, 7, 3, '4x4',
                            350, False, True )

    def CASE8( self, main ):
        """
        1 ) Sets up 3-nodes Onos-cluster
        2 ) Start 4x4 Leaf-Spine topology
        3 ) Pingall
        4 ) Cause random ONOS failure
        5 ) Pingall
        6 ) Cause random Spine failure
        7 ) Pingall
        8 ) Repeat 3 ), 4 ), 5 ), 6 ), 7 ), 'failures' times
        """
        try:
            from tests.USECASE.SegmentRouting.SRHighAvailability.dependencies.SRHAFuncs import SRHAFuncs
        except ImportError:
            main.log.error( "SRHAFuncs not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRHAFuncs()
        main.funcs.runTest( main, 8, 3, '4x4',
                            350, True, True )
