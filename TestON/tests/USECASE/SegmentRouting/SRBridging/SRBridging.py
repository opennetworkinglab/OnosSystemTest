class SRBridging:
    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        Tests connectivity between two untagged hosts
        (Ports are configured as vlan-untagged)

        Sets up 1 ONOS instance
        Start 0x1 single ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=1,
                            topology='0x1',
                            onosNodes=1,
                            description="Bridging test between two untagged hosts on vlan-untagged port" )

    def CASE2( self, main ):
        """
        Tests connectivity between two untagged hosts
        (Ports are configured as vlan-untagged)

        Sets up 1 ONOS instance
        Start 0x2 dual-homed ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=2,
                            topology='0x2',
                            onosNodes=1,
                            description="Bridging test between two untagged hosts on vlan-untagged port" )

    def CASE3( self, main ):
        """
        Tests connectivity between two untagged hosts
        (Ports are configured as vlan-untagged)

        Sets up 1 ONOS instance
        Start 2x2 leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=3,
                            topology='2x2 dual-linked',
                            onosNodes=1,
                            description="Bridging test between two untagged hosts on vlan-untagged port" )

    def CASE4( self, main ):
        """
        Tests connectivity between two untagged hosts
        (Ports are configured as vlan-untagged)

        Sets up 1 ONOS instance
        Start 2x4 dual-homed leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=4,
                            topology='2x4',
                            onosNodes=1,
                            description="Bridging test between two untagged hosts on vlan-untagged port" )

    def CASE5( self, main ):
        """
        Tests connectivity between two untagged hosts
        (Ports are configured as vlan-untagged)

        Sets up 3 ONOS instances
        Start 0x1 single ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                                test_idx=5,
                                topology='0x1',
                                onosNodes=3,
                                description="Bridging test between two untagged hosts on vlan-untagged port" )

    def CASE6( self, main ):
        """
        Tests connectivity between two untagged hosts
        (Ports are configured as vlan-untagged)

        Sets up 3 ONOS instances
        Start 0x2 dual-homed ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=6,
                            topology='0x2',
                            onosNodes=3,
                            description="Bridging test between two untagged hosts on vlan-untagged port" )

    def CASE7( self, main ):
        """
        Tests connectivity between two untagged hosts
        (Ports are configured as vlan-untagged)

        Sets up 3 ONOS instances
        Start 2x2 leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=7,
                            topology='2x2',
                            onosNodes=3,
                            description="Bridging test between two untagged hosts on vlan-untagged port" )

    def CASE8( self, main ):
        """
        Tests connectivity between two untagged hosts
        (Ports are configured as vlan-untagged)

        Sets up 3 ONOS instances
        Start 2x4 dual-homed leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=8,
                            topology='2x4',
                            onosNodes=3,
                            description="Bridging test between two untagged hosts on vlan-untagged port" )

    def CASE9( self, main ):
        """
        Tests connectivity between two untagged hosts
        (Ports are configured as vlan-untagged)

        Sets up 3 ONOS instances
        Start 2x2 leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=9,
                            topology='2x2 dual-linked',
                            onosNodes=3,
                            description="Bridging test between two untagged hosts on vlan-untagged port" )

    def CASE11( self, main ):
        """
        Tests connectivity between two tagged hosts
        (Ports are configured as vlan-tagged)

        Sets up 1 ONOS instance
        Start 0x1 single ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=11,
                            topology='0x1',
                            onosNodes=1,
                            description="Bridging test between two tagged hosts",
                            vlan=[ 10, 10 ] )

    def CASE12( self, main ):
        """
        Tests connectivity between two tagged hosts
        (Ports are configured as vlan-tagged)

        Sets up 1 ONOS instance
        Start 0x2 dual-homed ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=12,
                            topology='0x2',
                            onosNodes=1,
                            description="Bridging test between two tagged hosts",
                            vlan=[ 10, 10 ] )

    def CASE13( self, main ):
        """
        Tests connectivity between two tagged hosts
        (Ports are configured as vlan-tagged)

        Sets up 1 ONOS instance
        Start 2x2 leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=13,
                            topology='2x2',
                            onosNodes=1,
                            description="Bridging test between two tagged hosts",
                            vlan=[ 10, 10, 20, 20 ] )

    def CASE14( self, main ):
        """
        Tests connectivity between two tagged hosts
        (Ports are configured as vlan-tagged)

        Sets up 1 ONOS instance
        Start 2x4 dual-homed leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=14,
                            topology='2x4',
                            onosNodes=1,
                            description="Bridging test between two tagged hosts",
                            vlan=[ 10, 10, 20, 20 ] )

    def CASE15( self, main ):
        """
        Tests connectivity between two tagged hosts
        (Ports are configured as vlan-tagged)

        Sets up 3 ONOS instances
        Start 0x1 single ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=15,
                            topology='0x1',
                            onosNodes=3,
                            description="Bridging test between two tagged hosts",
                            vlan=[ 10, 10 ] )

    def CASE16( self, main ):
        """
        Tests connectivity between two tagged hosts
        (Ports are configured as vlan-tagged)

        Sets up 3 ONOS instances
        Start 0x2 dual-homed ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=16,
                            topology='0x2',
                            onosNodes=3,
                            description="Bridging test between two tagged hosts",
                            vlan=[ 10, 10 ] )

    def CASE17( self, main ):
        """
        Tests connectivity between two tagged hosts
        (Ports are configured as vlan-tagged)

        Sets up 3 ONOS instances
        Start 2x2 leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=17,
                            topology='2x2',
                            onosNodes=3,
                            description="Bridging test between two tagged hosts",
                            vlan=[ 10, 10, 20, 20 ] )

    def CASE18( self, main ):
        """
        Tests connectivity between two tagged hosts
        (Ports are configured as vlan-tagged)

        Sets up 3 ONOS instances
        Start 2x4 dual-homed leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=18,
                            topology='2x4',
                            onosNodes=3,
                            description="Bridging test between two tagged hosts",
                            vlan=[ 10, 10, 20, 20 ] )

    def CASE19( self, main ):
        """
        Tests connectivity between two tagged hosts
        (Ports are configured as vlan-tagged)

        Sets up 3 ONOS instances
        Start 2x2 leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=19,
                            topology='2x2 dual-linked',
                            onosNodes=3,
                            description="Bridging test between two tagged hosts"
                            vlan=[ 10, 10, 20, 20 ] )

    def CASE21( self, main ):
        """
        Tests connectivity between two untagged hosts
        (Ports are configured as vlan-native with vlan-tagged)

        Sets up 1 ONOS instance
        Start 0x1 single ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=21,
                            topology='0x1',
                            onosNodes=1,
                            description="Bridging test between two untagged hosts on vlan-native port" )

    def CASE22( self, main ):
        """
        Tests connectivity between two untagged hosts
        (Ports are configured as vlan-native with vlan-tagged)

        Sets up 1 ONOS instance
        Start 0x2 dual-homed ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=22,
                            topology='0x2',
                            onosNodes=1,
                            description="Bridging test between two untagged hosts on vlan-native port" )

    def CASE23( self, main ):
        """
        Tests connectivity between two untagged hosts
        (Ports are configured as vlan-native with vlan-tagged)

        Sets up 1 ONOS instance
        Start 2x2 leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=23,
                            topology='2x2',
                            onosNodes=1,
                            description="Bridging test between two untagged hosts on vlan-native port" )

    def CASE24( self, main ):
        """
        Tests connectivity between two untagged hosts
        (Ports are configured as vlan-native with vlan-tagged)

        Sets up 1 ONOS instance
        Start 2x4 dual-homed leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=24,
                            topology='2x4',
                            onosNodes=1,
                            description="Bridging test between two untagged hosts on vlan-native port" )

    def CASE25( self, main ):
        """
        Tests connectivity between two untagged hosts
        (Ports are configured as vlan-native with vlan-tagged)

        Sets up 3 ONOS instances
        Start 0x1 single ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=25,
                            topology='0x1',
                            onosNodes=3,
                            description="Bridging test between two untagged hosts on vlan-native port" )

    def CASE26( self, main ):
        """
        Tests connectivity between two untagged hosts
        (Ports are configured as vlan-native with vlan-tagged)

        Sets up 3 ONOS instances
        Start 0x2 dual-homed ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=26,
                            topology='0x2',
                            onosNodes=3,
                            description="Bridging test between two untagged hosts on vlan-native port" )

    def CASE27( self, main ):
        """
        Tests connectivity between two untagged hosts
        (Ports are configured as vlan-native with vlan-tagged)

        Sets up 3 ONOS instances
        Start 2x2 leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=27,
                            topology='2x2',
                            onosNodes=3,
                            description="Bridging test between two untagged hosts on vlan-native port" )

    def CASE28( self, main ):
        """
        Tests connectivity between two untagged hosts
        (Ports are configured as vlan-native with vlan-tagged)

        Sets up 3 ONOS instances
        Start 2x4 dual-homed leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=28,
                            topology='2x4',
                            onosNodes=3,
                            description="Bridging test between two untagged hosts on vlan-native port" )

    def CASE29( self, main ):
        """
        Tests connectivity between two untagged hosts
        (Ports are configured as vlan-native with vlan-tagged)

        Sets up 3 ONOS instances
        Start 2x2 leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=29,
                            topology='2x2 dual-linked',
                            onosNodes=3,
                            description="Bridging test between two untagged hosts on vlan-native port" )

    def CASE31( self, main ):
        """
        Tests connectivity between two untagged hosts
        (One port is configured as vlan-native with vlan-tagged,
        another with vlan-untagged)

        Sets up 1 ONOS instance
        Start 0x1 single ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=31,
                            topology='0x1',
                            onosNodes=1,
                            description="Bridging test between two untagged hosts, "
                            "one on vlan-untagged port and the other on vlan-native port" )

    def CASE32( self, main ):
        """
        Tests connectivity between two untagged hosts
        (One port is configured as vlan-native with vlan-tagged,
        another with vlan-untagged)

        Sets up 1 ONOS instance
        Start 0x2 dual-homed ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=32,
                            topology='0x2',
                            onosNodes=1,
                            description="Bridging test between two untagged hosts, "
                            "one on vlan-untagged port and the other on vlan-native port" )

    def CASE33( self, main ):
        """
        Tests connectivity between two untagged hosts
        (One port is configured as vlan-native with vlan-tagged,
        another with vlan-untagged)

        Sets up 1 ONOS instance
        Start 2x2 leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=33,
                            topology='2x2',
                            onosNodes=1,
                            description="Bridging test between two untagged hosts, "
                            "one on vlan-untagged port and the other on vlan-native port" )

    def CASE34( self, main ):
        """
        Tests connectivity between two untagged hosts
        (One port is configured as vlan-native with vlan-tagged,
        another with vlan-untagged)

        Sets up 1 ONOS instance
        Start 2x4 dual-homed leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=34,
                            topology='2x4',
                            onosNodes=1,
                            description="Bridging test between two untagged hosts, "
                            "one on vlan-untagged port and the other on vlan-native port" )

    def CASE35( self, main ):
        """
        Tests connectivity between two untagged hosts
        (One port is configured as vlan-native with vlan-tagged,
        another with vlan-untagged)

        Sets up 3 ONOS instances
        Start 0x1 single ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=35,
                            topology='0x1',
                            onosNodes=3,
                            description="Bridging test between two untagged hosts, "
                            "one on vlan-untagged port and the other on vlan-native port" )

    def CASE36( self, main ):
        """
        Tests connectivity between two untagged hosts
        (One port is configured as vlan-native with vlan-tagged,
        another with vlan-untagged)

        Sets up 3 ONOS instances
        Start 0x2 dual-homed ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=36,
                            topology='0x2',
                            onosNodes=3,
                            description="Bridging test between two untagged hosts, "
                            "one on vlan-untagged port and the other on vlan-native port" )

    def CASE37( self, main ):
        """
        Tests connectivity between two untagged hosts
        (One port is configured as vlan-native with vlan-tagged,
        another with vlan-untagged)

        Sets up 3 ONOS instances
        Start 2x2 leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=37,
                            topology='2x2',
                            onosNodes=3,
                            description="Bridging test between two untagged hosts, "
                            "one on vlan-untagged port and the other on vlan-native port" )

    def CASE38( self, main ):
        """
        Tests connectivity between two untagged hosts
        (One port is configured as vlan-native with vlan-tagged,
        another with vlan-untagged)

        Sets up 3 ONOS instances
        Start 2x4 dual-homed leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest(main,
                           test_idx=38,
                           topology='2x4',
                           onosNodes=3,
                           description="Bridging test between two untagged hosts, "
                                       "one on vlan-untagged port and the other on vlan-native port" )

    def CASE39( self, main ):
        """
        Tests connectivity between two untagged hosts
        (Ports are configured as vlan-native and vlan-tagged, another with vlan-untagged)

        Sets up 3 ONOS instances
        Start 2x2 leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=39,
                            topology='2x2 dual-linked',
                            onosNodes=3,
                            description="Bridging test between two untagged hosts, "
                                        "one on vlan-untagged port and the other on vlan-native port" )

    def CASE41( self, main ):
        """
        Tests connectivity between untagged host and tagged host
        (Ports are configured as vlan-untagged and
        vlan-tagged with same vlan id, respectively)

        Sets up 1 ONOS instance
        Start 0x1 single ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=41,
                            topology='0x1',
                            onosNodes=1,
                            description="Bridging test between untagged host and tagged host",
                            vlan=[ 0, 10 ] )

    def CASE42( self, main ):
        """
        Tests connectivity between untagged host and tagged host
        (Ports are configured as vlan-untagged and
        vlan-tagged with same vlan id, respectively)

        Sets up 1 ONOS instance
        Start 0x2 dual-homed ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=42,
                            topology='0x2',
                            onosNodes=1,
                            description="Bridging test between untagged host and tagged host",
                            vlan=[ 0, 10 ] )

    def CASE43( self, main ):
        """
        Tests connectivity between untagged host and tagged host
        (Ports are configured as vlan-untagged and
        vlan-tagged with same vlan id, respectively)

        Sets up 1 ONOS instance
        Start 2x2 leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=43,
                            topology='2x2',
                            onosNodes=1,
                            description="Bridging test between untagged host and tagged host",
                            vlan=[ 0, 10, 0, 20 ] )

    def CASE44( self, main ):
        """
        Tests connectivity between untagged host and tagged host
        (Ports are configured as vlan-untagged and
        vlan-tagged with same vlan id, respectively)

        Sets up 1 ONOS instance
        Start 2x4 dual-homed leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=44,
                            topology='2x4',
                            onosNodes=1,
                            description="Bridging test between untagged host and tagged host",
                            vlan=[ 0, 10, 0, 20 ] )

    def CASE45( self, main ):
        """
        Tests connectivity between untagged host and tagged host
        (Ports are configured as vlan-untagged and
        vlan-tagged with same vlan id, respectively)

        Sets up 3 ONOS instances
        Start 0x1 single ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=45,
                            topology='0x1',
                            onosNodes=3,
                            description="Bridging test between untagged host and tagged host",
                            vlan=[ 0, 10 ] )

    def CASE46( self, main ):
        """
        Tests connectivity between untagged host and tagged host
        (Ports are configured as vlan-untagged and
        vlan-tagged with same vlan id, respectively)

        Sets up 3 ONOS instances
        Start 0x2 dual-homed ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=46,
                            topology='0x2',
                            onosNodes=3,
                            description="Bridging test between untagged host and tagged host",
                            vlan=[ 0, 10 ] )

    def CASE47( self, main ):
        """
        Tests connectivity between untagged host and tagged host
        (Ports are configured as vlan-untagged and
        vlan-tagged with same vlan id, respectively)

        Sets up 3 ONOS instances
        Start 2x2 leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=47,
                            topology='2x2',
                            onosNodes=3,
                            description="Bridging test between untagged host and tagged host",
                            vlan=[ 0, 10, 0, 20 ] )

    def CASE48( self, main ):
        """
        Tests connectivity between untagged host and tagged host
        (Ports are configured as vlan-untagged and
        vlan-tagged with same vlan id, respectively)

        Sets up 3 ONOS instances
        Start 2x4 dual-homed leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=48,
                            topology='2x4',
                            onosNodes=3,
                            description="Bridging test between untagged host and tagged host",
                            vlan=[ 0, 10, 0, 20 ] )

    def CASE49( self, main ):
        """
        Tests connectivity between untagged host and tagged host
        (Ports are configured as vlan-untagged and
        vlan-tagged with same vlan-id, respectively)

        Sets up 3 ONOS instances
        Start 2x2 leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=49,
                            topology='2x2 dual-linked',
                            onosNodes=3,
                            description="Bridging test between two untagged hostand tagged host",
                            vlan=[ 102, 103 ] )

    def CASE51( self, main ):
        """
        Tests connectivity between two untagged hosts with different vlan id
        (Ports are configured as vlan-untagged 10 and 20, respectively)

        Sets up 1 ONOS instance
        Start 0x1 single ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=51,
                            topology='0x1',
                            onosNodes=1,
                            description="Bridging test between two untagged hosts with different vlan id" )

    def CASE52( self, main ):
        """
        Tests connectivity between two untagged hosts with different vlan id
        (Ports are configured as vlan-untagged 10 and 20, respectively)

        Sets up 1 ONOS instance
        Start 0x2 dual-homed ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=52,
                            topology='0x2',
                            onosNodes=1,
                            description="Bridging test between two untagged hosts with different vlan id" )

    def CASE53( self, main ):
        """
        Tests connectivity between two untagged hosts with different vlan id
        (Ports are configured as vlan-untagged 10 and 20, respectively)

        Sets up 1 ONOS instance
        Start 2x2 leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=53,
                            topology='2x2',
                            onosNodes=1,
                            description="Bridging test between two untagged hosts with different vlan id" )

    def CASE54( self, main ):
        """
        Tests connectivity between two untagged hosts with different vlan id
        (Ports are configured as vlan-untagged 10 and 20, respectively)

        Sets up 1 ONOS instance
        Start 2x4 dual-homed leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=54,
                            topology='2x4',
                            onosNodes=1,
                            description="Bridging test between two untagged hosts with different vlan id" )

    def CASE55( self, main ):
        """
        Tests connectivity between two untagged hosts with different vlan id
        (Ports are configured as vlan-untagged 10 and 20, respectively)

        Sets up 3 ONOS instances
        Start 0x1 single ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=55,
                            topology='0x1',
                            onosNodes=3,
                            description="Bridging test between two untagged hosts with different vlan id" )

    def CASE56( self, main ):
        """
        Tests connectivity between two untagged hosts with different vlan id
        (Ports are configured as vlan-untagged 10 and 20, respectively)

        Sets up 3 ONOS instances
        Start 0x2 dual-homed ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=56,
                            topology='0x2',
                            onosNodes=3,
                            description="Bridging test between two untagged hosts with different vlan id" )

    def CASE57( self, main ):
        """
        Tests connectivity between two untagged hosts with different vlan id
        (Ports are configured as vlan-untagged 10 and 20, respectively)

        Sets up 3 ONOS instances
        Start 2x2 leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=57,
                            topology='2x2',
                            onosNodes=3,
                            description="Bridging test between two untagged hosts with different vlan id" )

    def CASE58( self, main ):
        """
        Tests connectivity between two untagged hosts with different vlan id
        (Ports are configured as vlan-untagged 10 and 20, respectively)

        Sets up 3 ONOS instances
        Start 2x4 dual-homed leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=58,
                            topology='2x4',
                            onosNodes=3,
                            description="Bridging test between two untagged hosts with different vlan id" )

    def CASE59( self, main ):
        """
        Tests connectivity between two untagged hosts with different vlan id
        (Ports are configured as vlan-untagged 10 and 20, respectively)

        Sets up 3 ONOS instances
        Start 2x2 leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=59,
                            topology='2x2 dual-linked',
                            onosNodes=3,
                            description="Bridging test between two untagged hosts with different vlan-id" )

    def CASE61( self, main ):
        """
        Tests connectivity between two tagged hosts with different vlan id
        (Ports are configured as vlan-tagged 10 and 20, respectively)

        Sets up 1 ONOS instance
        Start 0x1 single ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=61,
                            topology='0x1',
                            onosNodes=1,
                            description="Bridging test between two tagged hosts with different vlan id",
                            vlan=[ 10, 20 ] )

    def CASE62( self, main ):
        """
        Tests connectivity between two tagged hosts with different vlan id
        (Ports are configured as vlan-tagged 10 and 20, respectively)

        Sets up 1 ONOS instance
        Start 0x2 dual-homed ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=62,
                            topology='0x2',
                            onosNodes=1,
                            description="Bridging test between two tagged hosts with different vlan id",
                            vlan=[ 10, 20 ] )

    def CASE63( self, main ):
        """
        Tests connectivity between two tagged hosts with different vlan id
        (Ports are configured as vlan-tagged 10 and 20, respectively)

        Sets up 1 ONOS instance
        Start 2x2 leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=63,
                            topology='2x2',
                            onosNodes=1,
                            description="Bridging test between two tagged hosts with different vlan id",
                            vlan=[ 10, 20, 30, 40 ] )

    def CASE64( self, main ):
        """
        Tests connectivity between two tagged hosts with different vlan id
        (Ports are configured as vlan-tagged 10 and 20, respectively)

        Sets up 1 ONOS instance
        Start 2x4 dual-homed leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=64,
                            topology='2x4',
                            onosNodes=1,
                            description="Bridging test between two tagged hosts with different vlan id",
                            vlan=[ 10, 20, 30, 40 ] )

    def CASE65( self, main ):
        """
        Tests connectivity between two tagged hosts with different vlan id
        (Ports are configured as vlan-tagged 10 and 20, respectively)

        Sets up 3 ONOS instances
        Start 0x1 single ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=65,
                            topology='0x1',
                            onosNodes=3,
                            description="Bridging test between two tagged hosts with different vlan id",
                            vlan=[ 10, 20 ] )

    def CASE66( self, main ):
        """
        Tests connectivity between two tagged hosts with different vlan id
        (Ports are configured as vlan-tagged 10 and 20, respectively)

        Sets up 3 ONOS instances
        Start 0x2 dual-homed ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=66,
                            topology='0x2',
                            onosNodes=3,
                            description="Bridging test between two tagged hosts with different vlan id",
                            vlan=[ 10, 20 ] )

    def CASE67( self, main ):
        """
        Tests connectivity between two tagged hosts with different vlan id
        (Ports are configured as vlan-tagged 10 and 20, respectively)

        Sets up 3 ONOS instances
        Start 2x2 leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=67,
                            topology='2x2',
                            onosNodes=3,
                            description="Bridging test between two tagged hosts with different vlan id",
                            vlan=[ 10, 20, 30, 40 ] )

    def CASE68( self, main ):
        """
        Tests connectivity between two tagged hosts with different vlan id
        (Ports are configured as vlan-tagged 10 and 20, respectively)

        Sets up 3 ONOS instances
        Start 2x4 dual-homed leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=68,
                            topology='2x4',
                            onosNodes=3,
                            description="Bridging test between two tagged hosts with different vlan id",
                            vlan=[ 10, 20, 30, 40 ] )

    def CASE69( self, main ):
        """
        Tests connectivity between two tagged hosts with different vlan id
        (Ports are configured as vlan-tagged 10 and 20, respectively)

        Sets up 3 ONOS instances
        Start 2x2 leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=69,
                            topology='2x2 dual-linked',
                            onosNodes=3,
                            description="Bridging test between two tagged hosts with different vlan id",
                            vlan=[ 10, 20, 30, 40 ] )

    def CASE71( self, main ):
        """
        Tests connectivity between untagged and tagged hosts with different vlan id
        (Ports are configured as vlan-untagged 10 and vlan-tagged 20, respectively)

        Sets up 1 ONOS instance
        Start 0x1 single ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=71,
                            topology='0x1',
                            onosNodes=1,
                            description="Bridging test between untagged and tagged hosts with different vlan id",
                            vlan=[ 0, 20 ] )

    def CASE72( self, main ):
        """
        Tests connectivity between untagged and tagged hosts with different vlan id
        (Ports are configured as vlan-untagged 10 and vlan-tagged 20, respectively)

        Sets up 1 ONOS instance
        Start 0x2 dual-homed ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=72,
                            topology='0x2',
                            onosNodes=1,
                            description="Bridging test between untagged and tagged hosts with different vlan id",
                            vlan=[ 0, 20 ] )

    def CASE73( self, main ):
        """
        Tests connectivity between untagged and tagged hosts with different vlan id
        (Ports are configured as vlan-untagged 10 and vlan-tagged 20, respectively)

        Sets up 1 ONOS instance
        Start 2x2 leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=73,
                            topology='2x2',
                            onosNodes=1,
                            description="Bridging test between untagged and tagged hosts with different vlan id",
                            vlan=[ 0, 20, 0, 40 ] )

    def CASE74( self, main ):
        """
        Tests connectivity between untagged and tagged hosts with different vlan id
        (Ports are configured as vlan-untagged 10 and vlan-tagged 20, respectively)

        Sets up 1 ONOS instance
        Start 2x2 dual-homed leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=74,
                            topology='2x4',
                            onosNodes=1,
                            description="Bridging test between untagged and tagged hosts with different vlan id",
                            vlan=[ 0, 20, 0, 40 ] )

    def CASE75( self, main ):
        """
        Tests connectivity between untagged and tagged hosts with different vlan id
        (Ports are configured as vlan-untagged 10 and vlan-tagged 20, respectively)

        Sets up 3 ONOS instances
        Start 0x1 single ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=75,
                            topology='0x1',
                            onosNodes=3,
                            description="Bridging test between untagged and tagged hosts with different vlan id",
                            vlan=[ 0, 20 ] )

    def CASE76( self, main ):
        """
        Tests connectivity between untagged and tagged hosts with different vlan id
        (Ports are configured as vlan-untagged 10 and vlan-tagged 20, respectively)

        Sets up 3 ONOS instances
        Start 0x2 dual-homed ToR topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=76,
                            topology='0x2',
                            onosNodes=3,
                            description="Bridging test between untagged and tagged hosts with different vlan id",
                            vlan=[ 0, 20 ] )

    def CASE77( self, main ):
        """
        Tests connectivity between untagged and tagged hosts with different vlan id
        (Ports are configured as vlan-untagged 10 and vlan-tagged 20, respectively)

        Sets up 3 ONOS instances
        Start 2x2 leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=77,
                            topology='2x2',
                            onosNodes=3,
                            description="Bridging test between untagged and tagged hosts with different vlan id",
                            vlan=[ 0, 20, 0, 40 ] )

    def CASE78( self, main ):
        """
        Tests connectivity between untagged and tagged hosts with different vlan id
        (Ports are configured as vlan-untagged 10 and vlan-tagged 20, respectively)

        Sets up 3 ONOS instances
        Start 2x2 dual-homed leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=78,
                            topology='2x4',
                            onosNodes=3,
                            description="Bridging test between untagged and tagged hosts with different vlan id",
                            vlan=[ 0, 20, 0, 40 ] )

    def CASE79( self, main ):
        """
        Tests connectivity between untagged and tagged hosts with different vlan id
        (Ports are configured as vlan-untagged 10 and vlan-tagged 20, respectively)

        Sets up 3 ONOS instances
        Start 2x2 leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRBridging.dependencies.SRBridgingTest import SRBridgingTest
        except ImportError:
            main.log.error( "SRBridgingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRBridgingTest()
        main.funcs.runTest( main,
                            test_idx=79,
                            topology='2x2 dual-linked',
                            onosNodes=3,
                            description="Bridging test between untagged and tagged hosts with different vlan idt",
                            vlan=[ 0, 20, 0, 40 ] )
