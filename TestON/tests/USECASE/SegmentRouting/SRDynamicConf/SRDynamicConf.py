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
class SRDynamicConf:
    def __init__( self ):
        self.default = ''

    # TODO: Reduce the number of test cases by multiplying different types of parameters in a single test case
    # (e.g., topology, onosNodes, vlan)

    def CASE11( self, main ):
        """
        Tests connectivity after changing vlan configuration of P1 from untagged 10 to tagged [10].
        A vlan configuration of the host connected to P1 is also changed to tagged 10.

        Sets up 3 ONOS instances
        Starts 0x1 single ToR topology
        Pingall
        Changes host vlan configuration
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=11,
                                   topology='0x1',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to tagged 10' )

    def CASE12( self, main ):
        """
        Tests connectivity after changing vlan configuration of P1 from untagged 10 to tagged [10].
        A vlan configuration of the host connected to P1 is also changed to tagged 10.

        Sets up 3 ONOS instances
        Starts 0x2 dual-homed ToR topology
        Pingall
        Changes host vlan configuration
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=12,
                                   topology='0x2',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to tagged 10' )

    def CASE13( self, main ):
        """
        Tests connectivity after changing vlan configuration of P1 from untagged 10 to tagged [10].
        A vlan configuration of the host connected to P1 is also changed to tagged 10.

        Sets up 3 ONOS instances
        Starts 2x2 leaf-spine topology
        Pingall
        Changes host vlan configuration
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        try:
            test=SRDynamicConfTest()
            test.runTest( main,
                                   testIndex=13,
                                   topology='2x2',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to tagged 10' )
        except Exception:
            main.log.exception("debug")

    def CASE14( self, main ):
        """
        Tests connectivity after changing vlan configuration of P1 from untagged 10 to tagged [10].
        A vlan configuration of the host connected to P1 is also changed to tagged 10.

        Sets up 3 ONOS instances
        Starts 2x4 dual-homed leaf-spine topology
        Pingall
        Changes host vlan configuration
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=14,
                                   topology='2x4',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to tagged 10' )

    def CASE21( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to untagged 20.
        Port P2 is configured as untagged 10 and another port P3 and P4 as tagged 20 and native 10.

        Sets up 3 ONOS instances
        Starts 0x1 single ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=21,
                                   topology='0x1',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to '
                                               'tagged 20 and native 10',
                                   vlan=( 0, 0, 20, 20 ) )

    def CASE22( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to untagged 20.
        Port P2 is configured as untagged 10 and another port P3 and P4 as tagged 20 and native 10.

        Sets up 3 ONOS instances
        Starts 0x2 dual-homed ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=22,
                                   topology='0x2',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to '
                                               'tagged 20 and native 10',
                                   vlan=( 0, 0, 20, 20 ) )

    def CASE23( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to untagged 20.
        Port P2 is configured as untagged 10 and another port P3 and P4 as tagged 20 and native 10.

        Sets up 3 ONOS instances
        Starts 2x2 leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=23,
                                   topology='2x2',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to '
                                               'tagged 20 and native 10',
                                   vlan=( 0, 0, 20, 20 ) )

    def CASE24( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to untagged 20.
        Port P2 is configured as untagged 10 and another port P3 and P4 as tagged 20 and native 10.

        Sets up 3 ONOS instances
        Starts 2x4 dual-homed leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=24,
                                   topology='2x4',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to '
                                               'tagged 20 and native 10',
                                   vlan=( 0, 0, 20, 20 ) )

    def CASE31( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 and P2 from untagged 10 to untagged 110,
        newly introduced vlan id.
        Port P3 and P4 are configured as untagged 20.

        Sets up 3 ONOS instances
        Starts 0x1 single ToR topology
        Pingall
        Changes interface vlan configurations
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=31,
                                   topology='0x1',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to untagged 110' )

    def CASE32( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 and P2 from untagged 10 to untagged 110,
        newly introduced vlan id.
        Port P3 and P4 are configured as untagged 20.

        Sets up 3 ONOS instances
        Starts 0x2 dual-homed ToR topology
        Pingall
        Changes interface vlan configurations
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=32,
                                   topology='0x2',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to untagged 110' )

    def CASE33( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 and P2 from untagged 10 to untagged 110,
        newly introduced vlan id.
        Port P3 and P4 are configured as untagged 20.

        Sets up 3 ONOS instances
        Starts 2x2 leaf-spine topology
        Pingall
        Changes interface vlan configurations
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=33,
                                   topology='2x2',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to untagged 110' )

    def CASE34( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 and P2 from untagged 10 to untagged 110,
        newly introduced vlan id.
        Port P3 and P4 are configured as untagged 20.

        Sets up 3 ONOS instances
        Starts 2x4 dual-homed leaf-spine topology
        Pingall
        Changes interface vlan configurations
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=34,
                                   topology='2x4',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to untagged 110' )

    def CASE41( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to tagged 20.
        Port P2 is configured as untagged 10 and another port P3 and P4 as untagged 20.

        Sets up 3 ONOS instances
        Starts 0x1 single ToR topology
        Pingall
        Changes host vlan configuration
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=41,
                                   topology='0x1',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to tagged 20' )

    def CASE42( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to tagged 20.
        Port P2 is configured as untagged 10 and another port P3 and P4 as untagged 20.

        Sets up 3 ONOS instances
        Starts 0x2 dual-homed ToR topology
        Pingall
        Changes host vlan configuration
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=42,
                                   topology='0x2',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to tagged 20' )

    def CASE43( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to tagged 20.
        Port P2 is configured as untagged 10 and another port P3 and P4 as untagged 20.

        Sets up 3 ONOS instances
        Starts 2x2 leaf-spine topology
        Pingall
        Changes host vlan configuration
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=43,
                                   topology='2x2',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to tagged 20' )

    def CASE44( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to tagged 20.
        Port P2 is configured as untagged 10 and another port P3 and P4 as untagged 20.

        Sets up 3 ONOS instances
        Starts 2x4 dual-homed leaf-spine topology
        Pingall
        Changes host vlan configuration
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=44,
                                   topology='2x4',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to tagged 20' )

    def CASE51( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to tagged 20 with native 10.
        Port P2 is configured as untagged 10 and another port P3 and P4 as untagged 20.

        Sets up 3 ONOS instances
        Starts 0x1 single ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=51,
                                   topology='0x1',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to '
                                               'tagged 20 with native 10' )

    def CASE52( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to tagged 20 with native 10.
        Port P2 is configured as untagged 10 and another port P3 and P4 as untagged 20.

        Sets up 3 ONOS instances
        Starts 0x2 dual-homed ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=52,
                                   topology='0x2',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to '
                                               'tagged 20 with native 10' )

    def CASE53( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to tagged 20 with native 10.
        Port P2 is configured as untagged 10 and another port P3 and P4 as untagged 20.

        Sets up 3 ONOS instances
        Starts 2x2 leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=53,
                                   topology='2x2',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to '
                                               'tagged 20 with native 10' )

    def CASE54( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to tagged 20 with native 10.
        Port P2 is configured as untagged 10 and another port P3 and P4 as untagged 20.

        Sets up 3 ONOS instances
        Starts 2x4 dual-homed leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=54,
                                   topology='2x4',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to '
                                               'tagged 20 with native 10' )

    def CASE61( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to tagged 120 with native 110.
        Port P2 is configured as untagged 10 and another port P3 and P4 as untagged 20.

        Sets up 3 ONOS instances
        Starts 0x1 single ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=61,
                                   topology='0x1',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to '
                                               'tagged 120 with native 110' )

    def CASE62( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to tagged 120 with native 110.
        Port P2 is configured as untagged 10 and another port P3 and P4 as untagged 20.

        Sets up 3 ONOS instances
        Starts 0x2 dual-homed ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=62,
                                   topology='0x2',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to '
                                               'tagged 120 with native 110' )

    def CASE63( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to tagged 120 with native 110.
        Port P2 is configured as untagged 10 and another port P3 and P4 as untagged 20.

        Sets up 3 ONOS instances
        Starts 2x2 leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=63,
                                   topology='2x2',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to '
                                               'tagged 120 with native 110' )

    def CASE64( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to tagged 120 with native 110.
        Port P2 is configured as untagged 10 and another port P3 and P4 as untagged 20.

        Sets up 3 ONOS instances
        Starts 2x4 dual-homed leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=64,
                                   topology='2x4',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to '
                                               'tagged 120 with native 110' )

    def CASE71( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 10 to untagged 10.
        Port P2 is configured as untagged 10 and another port P3 and P4 as untagged 20.

        Sets up 3 ONOS instances
        Starts 0x1 single ToR topology
        Pingall
        Changes host vlan configuration
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=71,
                                   topology='0x1',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 10 to untagged 10',
                                   vlan=( 10, 0, 0, 0 ) )

    def CASE72( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 10 to untagged 10.
        Port P2 is configured as untagged 10 and another port P3 and P4 as untagged 20.

        Sets up 3 ONOS instances
        Starts 0x2 dual-homed ToR topology
        Pingall
        Changes host vlan configuration
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=72,
                                   topology='0x2',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 10 to untagged 10',
                                   vlan=( 10, 0, 0, 0 ) )

    def CASE73( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 10 to untagged 10.
        Port P2 is configured as untagged 10 and another port P3 and P4 as untagged 20.

        Sets up 3 ONOS instances
        Starts 2x2 leaf-spine topology
        Pingall
        Changes host vlan configuration
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=73,
                                   topology='2x2',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 10 to untagged 10',
                                   vlan=( 10, 0, 0, 0 ) )

    def CASE74( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 10 to untagged 10.
        Port P2 is configured as untagged 10 and another port P3 and P4 as untagged 20.

        Sets up 3 ONOS instances
        Starts 2x4 dual-homed leaf-spine topology
        Pingall
        Changes host vlan configuration
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=74,
                                   topology='2x4',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 10 to untagged 10',
                                   vlan=( 10, 0, 0, 0 ) )

    def CASE81( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 to tagged 20 and native 10.
        Port P2 is configured as untagged 10 and another port P3 and P4 as untagged 20.
        All hosts are not configured.

        Sets up 3 ONOS instances
        Starts 0x1 single ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=81,
                                   topology='0x1',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 to '
                                               'tagged 20 and native 10' )

    def CASE82( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 to tagged 20 and native 10.
        Port P2 is configured as untagged 10 and another port P3 and P4 as untagged 20.
        All hosts are not configured.

        Sets up 3 ONOS instances
        Starts 0x2 dual-homed ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=82,
                                   topology='0x2',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 to '
                                               'tagged 20 and native 10' )

    def CASE83( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 to tagged 20 and native 10.
        Port P2 is configured as untagged 10 and another port P3 and P4 as untagged 20.
        All hosts are not configured.

        Sets up 3 ONOS instances
        Starts 2x2 leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=83,
                                   topology='2x2',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 to '
                                               'tagged 20 and native 10' )

    def CASE84( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 to tagged 20 and native 10.
        Port P2 is configured as untagged 10 and another port P3 and P4 as untagged 20.
        All hosts are not configured.

        Sets up 3 ONOS instances
        Starts 2x4 dual-homed leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=84,
                                   topology='2x4',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 to '
                                               'tagged 20 and native 10' )

    def CASE91( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 and P2 from tagged 10 to
        tagged 120 with native 110 (both newly introduced VLAN IDs).
        Port P3 and P4 are configured as untagged 20.
        Host h1 and h2 are congifured as VLAN 10, h3 and h4 are not configured.

        Sets up 3 ONOS instances
        Starts 0x1 single ToR topology
        Pingall
        Changes host vlan configuration
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=91,
                                   topology='0x1',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 10 to '
                                               'tagged 120 with native 110',
                                   vlan=( 10, 10, 0, 0 ) )

    def CASE92( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 and P2 from tagged 10 to
        tagged 120 with native 110 (both newly introduced VLAN IDs).
        Port P3 and P4 are configured as untagged 20.
        Host h1 and h2 are congifured as VLAN 10, h3 and h4 are not configured.

        Sets up 3 ONOS instances
        Starts 0x2 dual-homed ToR topology
        Pingall
        Changes host vlan configuration
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=92,
                                   topology='0x2',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 10 to '
                                               'tagged 120 with native 110',
                                   vlan=( 10, 10, 0, 0 ) )

    def CASE93( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 and P2 from tagged 10 to
        tagged 120 with native 110 (both newly introduced VLAN IDs).
        Port P3 and P4 are configured as untagged 20.
        Host h1 and h2 are congifured as VLAN 10, h3 and h4 are not configured.

        Sets up 3 ONOS instances
        Starts 2x2 leaf-spine topology
        Pingall
        Changes host vlan configuration
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=93,
                                   topology='2x2',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 10 to '
                                               'tagged 120 with native 110',
                                   vlan=( 10, 10, 0, 0 ) )

    def CASE94( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 and P2 from tagged 10 to
        tagged 120 with native 110 (both newly introduced VLAN IDs).
        Port P3 and P4 are configured as untagged 20.
        Host h1 and h2 are congifured as VLAN 10, h3 and h4 are not configured.

        Sets up 3 ONOS instances
        Starts 2x4 dual-homed leaf-spine topology
        Pingall
        Changes host vlan configuration
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=94,
                                   topology='2x4',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 10 to '
                                               'tagged 120 with native 110',
                                   vlan=( 10, 10, 0, 0 ) )

    def CASE101( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 10 and native 20 to untagged 20.
        Port P3 and P4 are configured as untagged 20.
        All hosts are not configured.

        Sets up 3 ONOS instances
        Starts 0x1 single ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=101,
                                   topology='0x1',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 10 '
                                               'and native 20 to untagged 20' )

    def CASE102( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 10 and native 20 to untagged 20.
        Port P3 and P4 are configured as untagged 20.
        All hosts are not configured.

        Sets up 3 ONOS instances
        Starts 0x2 dual-homed ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=102,
                                   topology='0x2',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 10 '
                                               'and native 20 to untagged 20' )

    def CASE103( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 10 and native 20 to untagged 20.
        Port P3 and P4 are configured as untagged 20.
        All hosts are not configured.

        Sets up 3 ONOS instances
        Starts 2x2 leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=103,
                                   topology='2x2',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 10 '
                                               'and native 20 to untagged 20' )

    def CASE104( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 10 and native 20 to untagged 20.
        Port P3 and P4 are configured as untagged 20.
        All hosts are not configured.

        Sets up 3 ONOS instances
        Starts 2x4 dual-homed leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=104,
                                   topology='2x4',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 10 '
                                               'and native 20 to untagged 20' )

    def CASE111( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 and native 10 to tagged 20.
        Port P3 and P4 are configured as untagged 20.
        All hosts are not configured.

        Sets up 3 ONOS instances
        Starts 0x1 single ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=111,
                                   topology='0x1',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 '
                                               'and native 10 to tagged 20' )

    def CASE112( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 and native 10 to tagged 20.
        Port P3 and P4 are configured as untagged 20.
        All hosts are not configured.

        Sets up 3 ONOS instances
        Starts 0x2 dual-homed ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=112,
                                   topology='0x2',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 '
                                               'and native 10 to tagged 20' )

    def CASE113( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 and native 10 to tagged 20.
        Port P3 and P4 are configured as untagged 20.
        All hosts are not configured.

        Sets up 3 ONOS instances
        Starts 2x2 leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=113,
                                   topology='2x2',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 '
                                               'and native 10 to tagged 20' )

    def CASE114( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 and native 10 to tagged 20.
        Port P3 and P4 are configured as untagged 20.
        All hosts are not configured.

        Sets up 3 ONOS instances
        Starts 2x4 dual-homed leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=114,
                                   topology='2x4',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 '
                                               'and native 10 to tagged 20' )

    def CASE121( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 and P2 from tagged 20 and native 10
        to tagged 20 and native 110.
        Port P3 and P4 are configured as untagged 20.
        All hosts are not configured.

        Sets up 3 ONOS instances
        Starts 0x1 single ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=121,
                                   topology='0x1',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 and native 10 '
                                               'to tagged 20 and native 110' )

    def CASE122( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 and P2 from tagged 20 and native 10
        to tagged 20 and native 110.
        Port P3 and P4 are configured as untagged 20.
        All hosts are not configured.

        Sets up 3 ONOS instances
        Starts 0x2 dual-homed ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=122,
                                   topology='0x2',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 and native 10 '
                                               'to tagged 20 and native 110' )

    def CASE123( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 and P2 from tagged 20 and native 10
        to tagged 20 and native 110.
        Port P3 and P4 are configured as untagged 20.
        All hosts are not configured.

        Sets up 3 ONOS instances
        Starts 2x2 leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=123,
                                   topology='2x2',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 and native 10 '
                                               'to tagged 20 and native 110' )

    def CASE124( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 and P2 from tagged 20 and native 10
        to tagged 20 and native 110.
        Port P3 and P4 are configured as untagged 20.
        All hosts are not configured.

        Sets up 3 ONOS instances
        Starts 2x4 dual-homed leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=124,
                                   topology='2x4',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 and native 10 '
                                               'to tagged 20 and native 110' )

    def CASE131( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 and native 10
        to tagged 120 and native 10.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as untagged 20.
        All hosts are not configured.

        Sets up 3 ONOS instances
        Starts 0x1 single ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=131,
                                   topology='0x1',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 and native 10 '
                                               'to tagged 120 and native 10' )

    def CASE132( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 and native 10
        to tagged 120 and native 10.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as untagged 20.
        All hosts are not configured.

        Sets up 3 ONOS instances
        Starts 0x2 dual-homed ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=132,
                                   topology='0x2',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 and native 10 '
                                               'to tagged 120 and native 10' )

    def CASE133( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 and native 10
        to tagged 120 and native 10.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as untagged 20.
        All hosts are not configured.

        Sets up 3 ONOS instances
        Starts 2x2 leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=133,
                                   topology='2x2',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 and native 10 '
                                               'to tagged 120 and native 10' )

    def CASE134( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 and native 10
        to tagged 120 and native 10.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as untagged 20.
        All hosts are not configured.

        Sets up 3 ONOS instances
        Starts 2x4 dual-homed leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=134,
                                   topology='2x4',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 and native 10 '
                                               'to tagged 120 and native 10' )

    def CASE141( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to tagged 20.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as untagged 20.
        Host h1 is configured as VLAN ID 20 and all other hosts are not configured.

        Sets up 3 ONOS instances
        Starts 0x1 single ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=141,
                                   topology='0x1',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to tagged 20',
                                   vlan=( 20, 0, 0, 0 ) )

    def CASE142( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to tagged 20.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as untagged 20.
        Host h1 is configured as VLAN ID 20 and all other hosts are not configured.

        Sets up 3 ONOS instances
        Starts 0x2 dual-homed ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=142,
                                   topology='0x2',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to tagged 20',
                                   vlan=( 20, 0, 0, 0 ) )

    def CASE143( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to tagged 20.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as untagged 20.
        Host h1 is configured as VLAN ID 20 and all other hosts are not configured.

        Sets up 3 ONOS instances
        Starts 2x2 leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=143,
                                   topology='2x2',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to tagged 20',
                                   vlan=( 20, 0, 0, 0 ) )

    def CASE144( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to tagged 20.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as untagged 20.
        Host h1 is configured as VLAN ID 20 and all other hosts are not configured.

        Sets up 3 ONOS instances
        Starts 2x4 dual-homed leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=144,
                                   topology='2x4',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to tagged 20',
                                   vlan=( 20, 0, 0, 0 ) )

    def CASE151( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to tagged 120.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as untagged 20.
        Host h1 is configured as VLAN ID 20 and all other hosts are not configured.

        Sets up 3 ONOS instances
        Starts 0x1 single ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=151,
                                   topology='0x1',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to tagged 120',
                                   vlan=( 20, 0, 0, 0 ) )

    def CASE152( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to tagged 120.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as untagged 20.
        Host h1 is configured as VLAN ID 20 and all other hosts are not configured.

        Sets up 3 ONOS instances
        Starts 0x2 dual-homed ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=152,
                                   topology='0x2',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to tagged 120',
                                   vlan=( 20, 0, 0, 0 ) )

    def CASE153( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to tagged 120.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as untagged 20.
        Host h1 is configured as VLAN ID 20 and all other hosts are not configured.

        Sets up 3 ONOS instances
        Starts 2x2 leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=153,
                                   topology='2x2',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to tagged 120',
                                   vlan=( 20, 0, 0, 0 ) )

    def CASE154( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to tagged 120.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as untagged 20.
        Host h1 is configured as VLAN ID 20 and all other hosts are not configured.

        Sets up 3 ONOS instances
        Starts 2x4 dual-homed leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=154,
                                   topology='2x4',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to tagged 120',
                                   vlan=( 20, 0, 0, 0 ) )

    def CASE161( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to
        tagged 20 and native 10.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1, h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 0x1 single ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=161,
                                   topology='0x1',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to '
                                               'tagged 20 and native 10',
                                   vlan=( 20, 0, 20, 20 ) )

    def CASE162( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to
        tagged 20 and native 10.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1, h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 0x2 dual-homed ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=162,
                                   topology='0x2',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to '
                                               'tagged 20 and native 10',
                                   vlan=( 20, 0, 20, 20 ) )

    def CASE163( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to
        tagged 20 and native 10.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1, h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 2x2 leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=163,
                                   topology='2x2',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to '
                                               'tagged 20 and native 10',
                                   vlan=( 20, 0, 20, 20 ) )

    def CASE164( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from untagged 10 to
        tagged 20 and native 10.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1, h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 2x4 dual-homed leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=164,
                                   topology='2x4',
                                   onosNodes=3,
                                   description='Changing port configuration from untagged 10 to '
                                               'tagged 20 and native 10',
                                   vlan=( 20, 0, 20, 20 ) )

    def CASE171( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 to tagged 120.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1 ,h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 0x1 single ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=171,
                                   topology='0x1',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 to tagged 120',
                                   vlan=( 20, 0, 20, 20 ) )

    def CASE172( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 to tagged 120.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1 ,h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 0x2 dual-homed ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=172,
                                   topology='0x2',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 to tagged 120',
                                   vlan=( 20, 0, 20, 20 ) )

    def CASE173( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 to tagged 120.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1 ,h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 2x2 leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=173,
                                   topology='2x2',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 to tagged 120',
                                   vlan=( 20, 0, 20, 20 ) )

    def CASE174( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 to tagged 120.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1 ,h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 2x4 dual-homed leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=174,
                                   topology='2x4',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 to tagged 120',
                                   vlan=( 20, 0, 20, 20 ) )

    def CASE181( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 to
        tagged 20 and native 10.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1 ,h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 0x1 single ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=181,
                                   topology='0x1',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 to '
                                               'tagged 20 and native 10',
                                   vlan=( 20, 0, 20, 20 ) )

    def CASE182( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 to
        tagged 20 and native 10.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1 ,h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 0x2 dual-homed ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=182,
                                   topology='0x2',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 to '
                                               'tagged 20 and native 10',
                                   vlan=(20, 0, 20, 20) )

    def CASE183( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 to
        tagged 20 and native 10.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1 ,h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 2x2 leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=183,
                                   topology='2x2',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 to '
                                               'tagged 20 and native 10',
                                   vlan=(20, 0, 20, 20) )

    def CASE184( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 to
        tagged 20 and native 10.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1 ,h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 2x4 dual-homed leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=184,
                                   topology='2x4',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 to '
                                               'tagged 20 and native 10',
                                   vlan=(20, 0, 20, 20) )

    def CASE191( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 and native 10 to
        untagged 20.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1 ,h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 0x1 single ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=191,
                                   topology='0x1',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 and native 10 to '
                                               'untagged 20',
                                   vlan=( 20, 0, 20, 20 ) )

    def CASE192( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 and native 10 to
        untagged 20.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1 ,h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 0x2 dual-homed ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=192,
                                   topology='0x2',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 and native 10 to '
                                               'untagged 20',
                                   vlan=( 20, 0, 20, 20 ) )

    def CASE193( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 and native 10 to
        untagged 20.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1 ,h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 2x2 leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=193,
                                   topology='2x2',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 and native 10 to '
                                               'untagged 20',
                                   vlan=( 20, 0, 20, 20 ) )

    def CASE194( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 and native 10 to
        untagged 20.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1 ,h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 2x4 dual-homed leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=194,
                                   topology='2x4',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 and native 10 to '
                                               'untagged 20',
                                   vlan=( 20, 0, 20, 20 ) )

    def CASE201( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 and native 10 to
        tagged 20.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1 ,h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 0x1 single ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=201,
                                   topology='0x1',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 and native 10 to '
                                               'tagged 20',
                                   vlan=( 20, 0, 20, 20 ) )

    def CASE202( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 and native 10 to
        tagged 20.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1 ,h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 0x2 dual-homed ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=202,
                                   topology='0x2',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 and native 10 to '
                                               'tagged 20',
                                   vlan=( 20, 0, 20, 20 ) )

    def CASE203( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 and native 10 to
        tagged 20.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1 ,h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 2x2 leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=203,
                                   topology='2x2',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 and native 10 to '
                                               'tagged 20',
                                   vlan=( 20, 0, 20, 20 ) )

    def CASE204( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 and native 10 to
        tagged 20.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1 ,h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 2x4 dual-homed leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=204,
                                   topology='2x4',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 and native 10 to '
                                               'tagged 20',
                                   vlan=( 20, 0, 20, 20 ) )

    def CASE211( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 and native 10 to
        tagged 20 and native 110.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1 ,h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 0x1 single ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=211,
                                   topology='0x1',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 and native 10 to '
                                               'tagged 20 and native 110',
                                   vlan=( 20, 0, 20, 20 ) )

    def CASE212( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 and native 10 to
        tagged 20 and native 110.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1 ,h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 0x2 dual-homed ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=212,
                                   topology='0x2',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 and native 10 to '
                                               'tagged 20 and native 110',
                                   vlan=( 20, 0, 20, 20 ) )

    def CASE213( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 and native 10 to
        tagged 20 and native 110.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1 ,h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 2x2 leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=213,
                                   topology='2x2',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 and native 10 to '
                                               'tagged 20 and native 110',
                                   vlan=( 20, 0, 20, 20 ) )

    def CASE214( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 and native 10 to
        tagged 20 and native 110.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1 ,h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 2x4 dual-homed leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=214,
                                   topology='2x4',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 and native 10 to '
                                               'tagged 20 and native 110',
                                   vlan=( 20, 0, 20, 20 ) )

    def CASE221( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 and native 10 to
        tagged 120 and native 10.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1 ,h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 0x1 single ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=221,
                                   topology='0x1',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 and native 10 to '
                                               'tagged 120 and native 10',
                                   vlan=( 20, 0, 20, 20 ) )

    def CASE222( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 and native 10 to
        tagged 120 and native 10.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1 ,h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 0x2 dual-homed ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=222,
                                   topology='0x2',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 and native 10 to '
                                               'tagged 120 and native 10',
                                   vlan=( 20, 0, 20, 20 ) )

    def CASE223( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 and native 10 to
        tagged 120 and native 10.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1 ,h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 2x2 leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=223,
                                   topology='2x2',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 and native 10 to '
                                               'tagged 120 and native 10',
                                   vlan=( 20, 0, 20, 20 ) )

    def CASE224( self, main ):
        """
        Tests connectivity after changing vlan configuration of port P1 from tagged 20 and native 10 to
        tagged 120 and native 10.
        Port P2 is configured as untagged 10 and port P3 and P4 are configured as tagged 20.
        Host h1 ,h3 and h4 are configured as VLAN ID 20 and h2 is not configured.

        Sets up 3 ONOS instances
        Starts 2x4 dual-homed leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=224,
                                   topology='2x4',
                                   onosNodes=3,
                                   description='Changing port configuration from tagged 20 and native 10 to '
                                               'tagged 120 and native 10',
                                   vlan=( 20, 0, 20, 20 ) )

    def CASE231( self, main ):
        """
        Tests connectivity after consecutive vlan configuration changes.
        All hosts are not configured.

        Sets up 3 ONOS instances
        Starts 0x1 single ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        Repeat
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=231,
                                   topology='0x1',
                                   onosNodes=3,
                                   description='Consecutive configuration changes' )

    def CASE232( self, main ):
        """
        Tests connectivity after consecutive vlan configuration changes.
        All hosts are not configured.

        Sets up 3 ONOS instances
        Starts 0x2 dual-homed ToR topology
        Pingall
        Changes interface vlan configuration
        Pingall
        Repeat
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=232,
                                   topology='0x2',
                                   onosNodes=3,
                                   description='Consecutive configuration changes' )

    def CASE233( self, main ):
        """
        Tests connectivity after consecutive vlan configuration changes.
        All hosts are not configured.

        Sets up 3 ONOS instances
        Starts 2x2 leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        Repeat
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=233,
                                   topology='2x2',
                                   onosNodes=3,
                                   description='Consecutive configuration changes' )

    def CASE234( self, main ):
        """
        Tests connectivity after consecutive vlan configuration changes.
        All hosts are not configured.

        Sets up 3 ONOS instances
        Starts 2x4 dual-homed leaf-spine topology
        Pingall
        Changes interface vlan configuration
        Pingall
        Repeat
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=234,
                                   topology='0x1',
                                   onosNodes=1,
                                   description='Consecutive configuration changes' )

    def CASE243( self, main ):
        """
        Tests connectivity after changing subnet configuration of port P1 from 10.0.2.254/24 to
        10.0.6.254/24.
        IP address and default GW of host h1 are also changed correspondingly.

        Sets up 3 ONOS instances
        Starts 2x2 leaf-spine topology
        Pingall
        Changes host IP configuration
        Changes interface subnet configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=243,
                                   topology='2x2',
                                   onosNodes=3,
                                   description='Changing port configuration from 10.0.2.254/24 to 10.0.6.254/24' )

    def CASE244( self, main ):
        """
        Tests connectivity after changing subnet configuration of port P1 from 10.0.2.254/24 to
        10.0.6.254/24.
        IP address and default GW of host h1 are also changed correspondingly.

        Sets up 3 ONOS instances
        Starts 2x4 dual-homed leaf-spine topology
        Pingall
        Changes host IP configuration
        Changes interface subnet configuration
        Pingall
        """
        from tests.USECASE.SegmentRouting.SRDynamicConf.dependencies.SRDynamicConfTest import SRDynamicConfTest
        SRDynamicConfTest.runTest( main,
                                   testIndex=244,
                                   topology='2x4',
                                   onosNodes=3,
                                   description='Changing port configuration from 10.0.2.254/24 to 10.0.6.254/24' )
