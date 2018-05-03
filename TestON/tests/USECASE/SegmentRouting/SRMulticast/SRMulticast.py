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
        import time
        from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Create a Multicast flow between a source and sink on the same dual-tor leaf" )
        main.mcastRoutes = { "ipv4": { "src": [ 0 ], "dst": [ 0 ] } }
        setupTest( main, test_idx=1, onosNodes=3 )
        verifyMcastRoutes( main )
        verifyMcastSinkRemoval( main, "ipv4", 0, False )
        verifyMcastSourceRemoval( main, "ipv4", 0, False )
        lib.cleanup( main, copyKarafLog=False )

    def CASE2( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Create a Multicast flow between a source and sink on different dual-tor leaves
        Verify flows and groups
        Verify traffic
        Remove sink
        Verify flows and groups
        """
        import time
        from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Create a Multicast flow between a source and sink on different dual-tor leaves" )
        main.mcastRoutes = { "ipv4": { "src": [ 0 ], "dst": [ 1 ] } }
        setupTest( main, test_idx=2, onosNodes=3 )
        verifyMcastRoutes( main )
        verifyMcastSinkRemoval( main, "ipv4", 1, False )
        verifyMcastSourceRemoval( main, "ipv4", 0, False )
        lib.cleanup( main, copyKarafLog=False )

    def CASE3( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Create a Multicast flow between a source and sink on different leaves (sink on single-tor)
        Verify flows and groups
        Verify traffic
        Remove sink
        Verify flows and groups
        """
        import time
        from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Create a Multicast flow between a source and sink on different leaves (sink on single-tor)" )
        main.mcastRoutes = { "ipv6": { "src": [ 0 ], "dst": [ 0 ] } }
        setupTest( main, test_idx=3, onosNodes=3 )
        verifyMcastRoutes( main )
        verifyMcastRouteRemoval( main, "ipv6" )
        lib.cleanup( main, copyKarafLog=False )

    def CASE4( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE1 and CASE2
        Verify flows and groups
        Verify traffic
        Remove sinks
        Verify flows and groups
        """
        import time
        from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Combines CASE1 and CASE2" )
        main.mcastRoutes = { "ipv4": { "src": [ 0 ], "dst": [ 0, 1 ] } }
        setupTest( main, test_idx=4, onosNodes=3 )
        verifyMcastRoutes( main )
        verifyMcastSinkRemoval( main, "ipv4", 0, [ False, True ] )
        verifyMcastSinkRemoval( main, "ipv4", 1, False )
        verifyMcastSourceRemoval( main, "ipv4", 0, False )
        lib.cleanup( main, copyKarafLog=False )

    def CASE5( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE2 and CASE3
        Verify flows and groups
        Verify traffic
        Remove sinks
        Verify flows and groups
        """
        import time
        from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Combines CASE2 and CASE3" )
        main.mcastRoutes = { "ipv4": { "src": [ 0 ], "dst": [ 1 ] }, "ipv6": { "src": [ 0 ], "dst": [ 0 ] } }
        setupTest( main, test_idx=5, onosNodes=3 )
        verifyMcastRoutes( main )
        verifyMcastRouteRemoval( main, "ipv6" )
        verifyMcastSinkRemoval( main, "ipv4", 1, False )
        verifyMcastSourceRemoval( main, "ipv4", 0, False )
        lib.cleanup( main, copyKarafLog=False )

    def CASE6( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE1 and CASE3
        Verify flows and groups
        Verify traffic
        Remove sinks
        Verify flows and groups
        """
        import time
        from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Combines CASE1 and CASE3" )
        main.mcastRoutes = { "ipv4": { "src": [ 0 ], "dst": [ 0 ] }, "ipv6": { "src": [ 0 ], "dst": [ 0 ] } }
        setupTest( main, test_idx=6, onosNodes=3 )
        verifyMcastRoutes( main )
        verifyMcastRouteRemoval( main, "ipv6" )
        verifyMcastSinkRemoval( main, "ipv4", 0, False )
        verifyMcastSourceRemoval( main, "ipv4", 0, False )
        lib.cleanup( main, copyKarafLog=False )

    def CASE7( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE1, CASE2 and CASE3
        Verify flows and groups
        Verify traffic
        Remove sinks
        Verify flows and groups
        """
        import time
        from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Combines CASE1, CASE2 and CASE3" )
        main.mcastRoutes = { "ipv4": { "src": [ 0 ], "dst": [ 0, 1 ] }, "ipv6": { "src": [ 0 ], "dst": [ 0 ] } }
        setupTest( main, test_idx=7, onosNodes=3 )
        verifyMcastRoutes( main )
        verifyMcastRouteRemoval( main, "ipv6" )
        verifyMcastSinkRemoval( main, "ipv4", 0, [ False, True ] )
        verifyMcastSinkRemoval( main, "ipv4", 1, False )
        verifyMcastSourceRemoval( main, "ipv4", 0, False )
        lib.cleanup( main, copyKarafLog=False )

    def CASE8( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Use all of the four sinks
        Verify flows and groups
        Verify traffic
        Remove sinks
        Verify flows and groups
        """
        import time
        from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Use all of the four sinks" )
        main.mcastRoutes = { "ipv4": { "src": [ 0 ], "dst": [ 0, 1, 2 ] }, "ipv6": { "src": [ 0 ], "dst": [ 0 ] } }
        setupTest( main, test_idx=8, onosNodes=3 )
        verifyMcastRoutes( main )
        verifyMcastRemoval( main )
        lib.cleanup( main, copyKarafLog=False )

    def CASE101( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE8 with a link failure (link ingress-spine)
        Verify flows and groups
        Verify traffic
        """
        import time
        from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Combines CASE8 with a link failure (link ingress-spine)" )
        main.mcastRoutes = { "ipv4": { "src": [ 0 ], "dst": [ 0, 1, 2 ] }, "ipv6": { "src": [ 0 ], "dst": [ 0 ] } }
        setupTest( main, test_idx=101, onosNodes=3 )
        verifyMcastRoutes( main )
        verifyLinkDown( main, [ "leaf2", "spine101" ], 4 )
        verifyMcastRemoval( main )
        lib.cleanup( main, copyKarafLog=False )

    def CASE102( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE8 with a link failure (link spine-egress-dt-leaf)
        Verify flows and groups
        Verify traffic
        """
        import time
        from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Combines CASE8 with a link failure (link spine-engress-dt-leaf)" )
        main.mcastRoutes = { "ipv4": { "src": [ 0 ], "dst": [ 0, 1, 2 ] }, "ipv6": { "src": [ 0 ], "dst": [ 0 ] } }
        setupTest( main, test_idx=102, onosNodes=3 )
        verifyMcastRoutes( main )
        verifyLinkDown( main, [ "leaf5", "spine101" ], 4 )
        verifyMcastRemoval( main )
        lib.cleanup( main, copyKarafLog=False )

    def CASE103( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE8 with a link failure (link spine-egress-st-leaf)
        Verify flows and groups
        Verify traffic
        """
        import time
        from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Combines CASE8 with a link failure (link spine-engress-st-leaf)" )
        main.mcastRoutes = { "ipv4": { "src": [ 0 ], "dst": [ 0, 1, 2 ] }, "ipv6": { "src": [ 0 ], "dst": [ 0 ] } }
        setupTest( main, test_idx=103, onosNodes=3 )
        verifyMcastRoutes( main )
        verifyLinkDown( main, [ "spine103", "spine101" ], 4 )
        verifyMcastRemoval( main )
        lib.cleanup( main, copyKarafLog=False )

    def CASE104( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE8 with a link failure (link spine-egress-st-leaf-2)
        Verify flows and groups
        Verify traffic
        """
        import time
        from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Combines CASE8 with a link failure (link spine-engress-st-leaf-2)" )
        main.mcastRoutes = { "ipv4": { "src": [ 0 ], "dst": [ 0, 1, 2 ] }, "ipv6": { "src": [ 0 ], "dst": [ 0 ] } }
        setupTest( main, test_idx=104, onosNodes=3 )
        verifyMcastRoutes( main )
        verifyLinkDown( main, [ "leaf4", "spine101" ], 4 )
        verifyMcastRemoval( main )
        lib.cleanup( main, copyKarafLog=False )

    def CASE105( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE8 with a link failure (link dt-leaf-sink)
        Verify flows and groups
        Verify traffic
        """
        import time
        from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Combines CASE8 with a link failure (link dt-leaf-sink)" )
        main.mcastRoutes = { "ipv4": { "src": [ 0 ], "dst": [ 0, 1, 2 ] }, "ipv6": { "src": [ 0 ], "dst": [ 0 ] } }
        setupTest( main, test_idx=105, onosNodes=3 )
        verifyMcastRoutes( main )
        verifyLinkDown( main, [ "leaf2", "h4v4" ], 0 )
        verifyMcastRemoval( main )
        lib.cleanup( main, copyKarafLog=False )

    def CASE106( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE8 with a link failure (link dt-leaf-sink-2)
        Verify flows and groups
        Verify traffic
        """
        import time
        from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Combines CASE8 with a link failure (link dt-leaf-sink-2)" )
        main.mcastRoutes = { "ipv4": { "src": [ 0 ], "dst": [ 0, 1, 2 ] }, "ipv6": { "src": [ 0 ], "dst": [ 0 ] } }
        setupTest( main, test_idx=106, onosNodes=3 )
        verifyMcastRoutes( main )
        verifyLinkDown( main, [ "leaf5", "h10v4" ], 0 )
        verifyMcastRemoval( main )
        lib.cleanup( main, copyKarafLog=False )

    def CASE201( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE8 with spine failure
        Verify flows and groups
        Verify traffic
        """
        import time
        from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Combines CASE8 with spine failure" )
        main.mcastRoutes = { "ipv4": { "src": [ 0 ], "dst": [ 0, 1, 2 ] }, "ipv6": { "src": [ 0 ], "dst": [ 0 ] } }
        setupTest( main, test_idx=201, onosNodes=3 )
        verifyMcastRoutes( main )
        verifySwitchDown( main, "spine101", 18 )
        verifySwitchDown( main, "spine102", 18 )
        verifyMcastRemoval( main, removeDHT1=False )
        lib.cleanup( main, copyKarafLog=False )

    def CASE202( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE8 with ingress failure and recovery
        Verify flows and groups are removed (failure)
        Verify flows and groups (recovery)
        Verify traffic (recovery)
        """
        import time
        from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Combines CASE8 with ingress failure and recovery" )
        main.mcastRoutes = { "ipv4": { "src": [ 0 ], "dst": [ 0, 1, 2 ] }, "ipv6": { "src": [ 0 ], "dst": [ 0 ] } }
        setupTest( main, test_idx=202, onosNodes=3 )
        verifyMcastRoutes( main )
        verifySwitchDown( main, "leaf2", 10, { "ipv4": False, "ipv6": False } )
        verifyMcastRemoval( main, removeDHT1=False )
        lib.cleanup( main, copyKarafLog=False )

    def CASE203( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE8 with egress-dt-leaf failure and recovery
        Verify flows and groups are removed for the failing sink (failure)
        Verify traffic on remaining sinks (failure)
        Verify flows and groups (recovery)
        Verify traffic (recovery)
        """
        import time
        from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Combines CASE8 with egress-dt-leaf failure and recovery" )
        main.mcastRoutes = { "ipv4": { "src": [ 0 ], "dst": [ 0, 1, 2 ] }, "ipv6": { "src": [ 0 ], "dst": [ 0 ] } }
        setupTest( main, test_idx=203, onosNodes=3 )
        verifyMcastRoutes( main )
        verifySwitchDown( main, "leaf5", 10 )
        verifyMcastRemoval( main, removeDHT1=False )
        lib.cleanup( main, copyKarafLog=False )

    def CASE204( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE8 with egress-st-leaf failure and recovery
        Verify flows and groups are removed for the failing sink (failure)
        Verify traffic on remaining sinks (failure)
        Verify flows and groups (recovery)
        Verify traffic (recovery)
        """
        import time
        from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Combines CASE8 with egress-st-leaf failure and recovery" )
        main.mcastRoutes = { "ipv4": { "src": [ 0 ], "dst": [ 0, 1, 2 ] }, "ipv6": { "src": [ 0 ], "dst": [ 0 ] } }
        setupTest( main, test_idx=204, onosNodes=3 )
        verifyMcastRoutes( main )
        verifySwitchDown( main, "leaf4", 10, { "ipv4": [ True, False, True ], "ipv6": True } )
        verifyMcastRemoval( main, removeDHT1=False )
        lib.cleanup( main, copyKarafLog=False )

    def CASE205( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE8 with egress leaves failure and recovery
        Verify flows and groups are removed for the failing sinks (failure)
        Verify traffic on remaining sink (failure)
        Verify flows and groups (recovery)
        Verify traffic (recovery)
        """
        import time
        from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Combines CASE8 with leaves failure and recovery" )
        main.mcastRoutes = { "ipv4": { "src": [ 0 ], "dst": [ 0, 1, 2 ] }, "ipv6": { "src": [ 0 ], "dst": [ 0 ] } }
        setupTest( main, test_idx=205, onosNodes=3 )
        verifyMcastRoutes( main )
        verifySwitchDown( main, [ "leaf1", "leaf3", "leaf4", "leaf5" ], 32, { "ipv4": [ True, False, False ], "ipv6": False } )
        verifyMcastRemoval( main, removeDHT1=False )
        lib.cleanup( main, copyKarafLog=False )

    def CASE301( self, main ):
        """
        Sets up 3 ONOS instances, start H-AGG topology
        Combines CASE8 with ONOS failure and recovery
        Verify flows and groups (failure)
        Verify traffic (failure)
        Verify flows and groups (recovery)
        Verify traffic (recovery)
        """
        import time
        from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Combines CASE8 with leaves failure and recovery" )
        main.mcastRoutes = { "ipv4": { "src": [ 0 ], "dst": [ 0, 1, 2 ] }, "ipv6": { "src": [ 0 ], "dst": [ 0 ] } }
        setupTest( main, test_idx=205, onosNodes=3 )
        verifyMcastRoutes( main )
        verifyOnosDown( main )
        verifyMcastRemoval( main, removeDHT1=False )
        lib.cleanup( main, copyKarafLog=False )

    def CASE401( self, main ):
        """
        Extends MCAST105
        Create sinks and verify traffic is working
        Bring down host port and verify traffic is still working for all sinks
        Bring up host port again and start ping from DTH1 to STS
        Verify host has both location and stop the ping
        Kill LEAFA and verify traffic is still working for all sinks
        Remove IPv6 route
        Remove DTH2 sink
        Remove STH2 sink
        Remove STS
        """
        import time
        from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Extends MCAST105" )
        main.mcastRoutes = { "ipv4": { "src": [ 0 ], "dst": [ 0, 1, 2 ] }, "ipv6": { "src": [ 0 ], "dst": [ 0 ] } }
        setupTest( main, test_idx=401, onosNodes=3 )
        verifyMcastRoutes( main )
        #TODO: Verify host has both locations
        # Verify killing one link of dual-homed host h4
        verifyLinkDown( main, [ "leaf2", "h4v4" ], 0 )
        verifyLinkDown( main, [ "leaf3", "h4v4" ], 0 )
        # Verify killing one link of dual-homed host h10
        verifyLinkDown( main, [ "leaf4", "h10v4" ], 0 )
        verifyLinkDown( main, [ "leaf5", "h10v4" ], 0 )
        verifySwitchDown( main, "leaf3", 10 )
        verifyMcastRemoval( main, removeDHT1=False )
        lib.cleanup( main, copyKarafLog=False )

    def CASE402( self, main ):
        """
        No downstream path for DTH2
        Create sinks and verify traffic is working
        Kill all up-links of the LEAFB and verify traffic is still working
        Remove IPv6 route
        Remove DTH2 sink
        Remove STH2 sink
        Remove STS
        """
        import time
        from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "No downstream path for DTH2" )
        main.mcastRoutes = { "ipv4": { "src": [ 0 ], "dst": [ 0, 1, 2 ] }, "ipv6": { "src": [ 0 ], "dst": [ 0 ] } }
        setupTest( main, test_idx=402, onosNodes=3 )
        verifyMcastRoutes( main )
        verifyLinkDown( main, [ [ "leaf5", "spine101" ], [ "leaf5", "spine102" ] ], 8 )
        verifyMcastRemoval( main, removeDHT1=False )
        lib.cleanup( main, copyKarafLog=False )

    def CASE403( self, main ):
        """
        No downstream path for DTH1
        Create sinks and verify traffic is working
        Bring down host port and verify traffic is still working for all sinks
        Bring up host port again and start ping from DTH1 to STS
        Verify host has both location and stop the ping
        Kill all up-links of the LEAFA and verify traffic is still working
        Remove IPv6 route
        Remove DTH2 sink
        Remove STH2 sink
        Remove STS
        """
        import time
        from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "No downstream path for DTH1" )
        main.mcastRoutes = { "ipv4": { "src": [ 0 ], "dst": [ 0, 1, 2 ] }, "ipv6": { "src": [ 0 ], "dst": [ 0 ] } }
        setupTest( main, test_idx=403, onosNodes=3 )
        verifyMcastRoutes( main )
        # Verify killing one link of dual-homed host h4
        verifyLinkDown( main, [ "leaf2", "h4v4" ], 0 )
        verifyLinkDown( main, [ "leaf3", "h4v4" ], 0 )
        # Verify killing one link of dual-homed host h10
        verifyLinkDown( main, [ "leaf4", "h10v4" ], 0 )
        verifyLinkDown( main, [ "leaf5", "h10v4" ], 0 )
        verifyLinkDown( main, [ [ "leaf3", "spine101" ], [ "leaf3", "spine102" ] ], 8 )
        verifyMcastRemoval( main, removeDHT1=False )
        lib.cleanup( main, copyKarafLog=False )

    def CASE404( self, main ):
        """
        Extends MCAST 403
        Create sinks and verify traffic is working
        Bring down host port and verify traffic is still working for all sinks
        Bring up host port again and start ping from DTH1 to STS
        Verify host has both location and stop the ping
        Kill up-links of the LEAFA towards SPINEA, kill up-links of the SOURCE LEAF towards SPINEC and verify traffic is still working for all sinks
        Remove IPv6 route
        Remove DTH2 sink
        Remove STH2 sink
        Remove STS
        """
        import time
        from tests.USECASE.SegmentRouting.SRMulticast.dependencies.SRMulticastTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Extends MCASR 403" )
        main.mcastRoutes = { "ipv4": { "src": [ 0 ], "dst": [ 0, 1, 2 ] }, "ipv6": { "src": [ 0 ], "dst": [ 0 ] } }
        setupTest( main, test_idx=404, onosNodes=3 )
        verifyMcastRoutes( main )
        # Verify killing one link of dual-homed host h4
        verifyLinkDown( main, [ "leaf2", "h4v4" ], 0 )
        verifyLinkDown( main, [ "leaf3", "h4v4" ], 0 )
        # Verify killing one link of dual-homed host h10
        verifyLinkDown( main, [ "leaf4", "h10v4" ], 0 )
        verifyLinkDown( main, [ "leaf5", "h10v4" ], 0 )
        verifyLinkDown( main, [ [ "leaf3", "spine101" ], [ "leaf2", "spine102" ] ], 8 )
        verifyMcastRemoval( main, removeDHT1=False )
        lib.cleanup( main, copyKarafLog=False )
