class SRMulticast:
    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Create a Multicast flow between a source and sink on the same dual-tor leaf
        Verify flows and groups
        Verify traffic
        Remove sink
        Verify flows and groups
        """
        try:
            from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import SRMulticastTest
        except ImportError:
            main.log.error( "SRMulticastTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRMulticastTest()
        main.funcs.runTest( main,
                            test_idx=1,
                            onosNodes=3,
                            description="Create a Multicast flow between a source and sink on the same dual-tor leaf" )

    def CASE2( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Create a Multicast flow between a source and sink on different dual-tor leaves
        Verify flows and groups
        Verify traffic
        Remove sink
        Verify flows and groups
        """
        try:
            from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import SRMulticastTest
        except ImportError:
            main.log.error( "SRMulticastTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRMulticastTest()
        main.funcs.runTest( main,
                            test_idx=2,
                            onosNodes=3,
                            description="Create a Multicast flow between a source and sink on different dual-tor leaves" )

    def CASE3( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Create a Multicast flow between a source and sink on different leaves (sink on single-tor)
        Verify flows and groups
        Verify traffic
        Remove sink
        Verify flows and groups
        """
        try:
            from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import SRMulticastTest
        except ImportError:
            main.log.error( "SRMulticastTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRMulticastTest()
        main.funcs.runTest( main,
                            test_idx=3,
                            onosNodes=3,
                            description="Create a Multicast flow between a source and sink on different leaves (sink on single-tor)" )

    def CASE4( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE1 and CASE2
        Verify flows and groups
        Verify traffic
        Remove sinks
        Verify flows and groups
        """
        try:
            from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import SRMulticastTest
        except ImportError:
            main.log.error( "SRMulticastTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRMulticastTest()
        main.funcs.runTest( main,
                            test_idx=4,
                            onosNodes=3,
                            description="Combines CASE1 and CASE2" )

    def CASE5( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE2 and CASE3
        Verify flows and groups
        Verify traffic
        Remove sinks
        Verify flows and groups
        """
        try:
            from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import SRMulticastTest
        except ImportError:
            main.log.error( "SRMulticastTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRMulticastTest()
        main.funcs.runTest( main,
                            test_idx=5,
                            onosNodes=3,
                            description="Combines CASE2 and CASE3" )

    def CASE6( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE1 and CASE3
        Verify flows and groups
        Verify traffic
        Remove sinks
        Verify flows and groups
        """
        try:
            from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import SRMulticastTest
        except ImportError:
            main.log.error( "SRMulticastTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRMulticastTest()
        main.funcs.runTest( main,
                            test_idx=5,
                            onosNodes=3,
                            description="Combines CASE1 and CASE3" )

    def CASE7( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE1, CASE2 and CASE3
        Verify flows and groups
        Verify traffic
        Remove sinks
        Verify flows and groups
        """
        try:
            from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import SRMulticastTest
        except ImportError:
            main.log.error( "SRMulticastTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRMulticastTest()
        main.funcs.runTest( main,
                            test_idx=7,
                            onosNodes=3,
                            description="Combines CASE7 with route removal" )

    def CASE8( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE7 with route removal
        Verify flows and groups
        """
        try:
            from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import SRMulticastTest
        except ImportError:
            main.log.error( "SRMulticastTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRMulticastTest()
        main.funcs.runTest( main,
                            test_idx=8,
                            onosNodes=3,
                            description="Combines CASE7 with route removal",
                            removeRoute=True )

    def CASE101( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE7 with a link failure (link ingress-spine)
        Verify flows and groups
        Verify traffic
        """
        try:
            from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import SRMulticastTest
        except ImportError:
            main.log.error( "SRMulticastTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRMulticastTest()
        main.funcs.runTest( main,
                            test_idx=101,
                            onosNodes=3,
                            description="Combines CASE7 with a link failure (link ingress-spine)",
                            linkFailure=True )

    def CASE102( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE7 with a link failure (link spine-egress-dt-leaf)
        Verify flows and groups
        Verify traffic
        """
        try:
            from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import SRMulticastTest
        except ImportError:
            main.log.error( "SRMulticastTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRMulticastTest()
        main.funcs.runTest( main,
                            test_idx=102,
                            onosNodes=3,
                            description="Combines CASE7 with a link failure (link spine-engress-dt-leaf)",
                            linkFailure=True )

    def CASE103( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE7 with a link failure (link spine-egress-st-leaf)
        Verify flows and groups
        Verify traffic
        """
        try:
            from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import SRMulticastTest
        except ImportError:
            main.log.error( "SRMulticastTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRMulticastTest()
        main.funcs.runTest( main,
                            test_idx=103,
                            onosNodes=3,
                            description="Combines CASE7 with a link failure (link spine-engress-st-leaf)",
                            linkFailure=True )

    def CASE201( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE7 with spine failure
        Verify flows and groups
        Verify traffic
        """
        try:
            from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import SRMulticastTest
        except ImportError:
            main.log.error( "SRMulticastTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRMulticastTest()
        main.funcs.runTest( main,
                            test_idx=201,
                            onosNodes=3,
                            description="Combines CASE7 with spine failure",
                            switchFailure=True )

    def CASE202( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE7 with ingress failure and recovery
        Verify flows and groups are removed (failure)
        Verify flows and groups (recovery)
        Verify traffic (recovery)
        """
        pass

    def CASE203( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE7 with egress-dt-leaf failure and recovery
        Verify flows and groups are removed for the failing sink (failure)
        Verify traffic on remaining sinks (failure)
        Verify flows and groups (recovery)
        Verify traffic (recovery)
        """
        pass

    def CASE204( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE7 with egress-st-leaf failure and recovery
        Verify flows and groups are removed for the failing sink (failure)
        Verify traffic on remaining sinks (failure)
        Verify flows and groups (recovery)
        Verify traffic (recovery)
        """
        pass

    def CASE205( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE7 with egress leaves failure and recovery
        Verify flows and groups are removed for the failing sinks (failure)
        Verify traffic on remaining sink (failure)
        Verify flows and groups (recovery)
        Verify traffic (recovery)
        """
        pass

    def CASE301( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE7 with ONOS failure and recovery
        Verify flows and groups (failure)
        Verify traffic (failure)
        Verify flows and groups (recovery)
        Verify traffic (recovery)
        """
        pass
