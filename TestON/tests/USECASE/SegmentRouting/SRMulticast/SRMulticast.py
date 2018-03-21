class SRMulticast:
    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        Sets up 3 ONOS instances
        Start 2x2 topology of hardware switches
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
                            topology='2x2',
                            onosNodes=1,
                            description="TBD" )

    def CASE01( self, main ):
        """
        Sets up 3 ONOS instances, start 2x5 topology
        Create a Multicast flow between a source and sink on the same dual-tor leaf
        Verify flows and groups
        Verify traffic
        Remove sink
        Verify flows and groups
        """
        pass

    def CASE02( self, main ):
        """
        Sets up 3 ONOS instances, start 2x5 topology
        Create a Multicast flow between a source and sink on different dual-tor leaves
        Verify flows and groups
        Verify traffic
        Remove sink
        Verify flows and groups
        """
        pass

    def CASE03( self, main ):
        """
        Sets up 3 ONOS instances, start 2x5 topology
        Create a Multicast flow between a source and sink on different leaves (sink on single-tor)
        Verify flows and groups
        Verify traffic
        Remove sink
        Verify flows and groups
        """
        pass

    def CASE04( self, main ):
        """
        Sets up 3 ONOS instances, start 2x5 topology
        Combines CASE01 and CASE02
        Verify flows and groups
        Verify traffic
        Remove sinks
        Verify flows and groups
        """
        pass

    def CASE05( self, main ):
        """
        Sets up 3 ONOS instances, start 2x5 topology
        Combines CASE02 and CASE03
        Verify flows and groups
        Verify traffic
        Remove sinks
        Verify flows and groups
        """
        pass

    def CASE06( self, main ):
        """
        Sets up 3 ONOS instances, start 2x5 topology
        Combines CASE01 and CASE03
        Verify flows and groups
        Verify traffic
        Remove sinks
        Verify flows and groups
        """
        pass

    def CASE07( self, main ):
        """
        Sets up 3 ONOS instances, start 2x5 topology
        Combines CASE01, CASE02 and CASE03
        Verify flows and groups
        Verify traffic
        Remove sinks
        Verify flows and groups
        """
        pass

    def CASE08( self, main ):
        """
        Sets up 3 ONOS instances, start 2x5 topology
        Combines CASE07 with route removal
        Verify flows and groups
        """
        pass

    def CASE101( self, main ):
        """
        Sets up 3 ONOS instances, start 2x5 topology
        Combines CASE07 with a link failure (link ingress-spine)
        Verify flows and groups
        Verify traffic
        """
        pass

    def CASE102( self, main ):
        """
        Sets up 3 ONOS instances, start 2x5 topology
        Combines CASE07 with a link failure (link spine-egress-dt-leaf)
        Verify flows and groups
        Verify traffic
        """
        pass

    def CASE103( self, main ):
        """
        Sets up 3 ONOS instances, start 2x5 topology
        Combines CASE07 with a link failure (link spine-egress-st-leaf)
        Verify flows and groups
        Verify traffic
        """
        pass

    def CASE201( self, main ):
        """
        Sets up 3 ONOS instances, start 2x5 topology
        Combines CASE07 with spine failure
        Verify flows and groups
        Verify traffic
        """
        pass

    def CASE202( self, main ):
        """
        Sets up 3 ONOS instances, start 2x5 topology
        Combines CASE07 with ingress failure and recovery
        Verify flows and groups are removed (failure)
        Verify flows and groups (recovery)
        Verify traffic (recovery)
        """
        pass

    def CASE203( self, main ):
        """
        Sets up 3 ONOS instances, start 2x5 topology
        Combines CASE07 with egress-dt-leaf failure and recovery
        Verify flows and groups are removed for the failing sink (failure)
        Verify traffic on remaining sinks (failure)
        Verify flows and groups (recovery)
        Verify traffic (recovery)
        """
        pass

    def CASE204( self, main ):
        """
        Sets up 3 ONOS instances, start 2x5 topology
        Combines CASE07 with egress-st-leaf failure and recovery
        Verify flows and groups are removed for the failing sink (failure)
        Verify traffic on remaining sinks (failure)
        Verify flows and groups (recovery)
        Verify traffic (recovery)
        """
        pass

    def CASE205( self, main ):
        """
        Sets up 3 ONOS instances, start 2x5 topology
        Combines CASE07 with egress leaves failure and recovery
        Verify flows and groups are removed for the failing sinks (failure)
        Verify traffic on remaining sink (failure)
        Verify flows and groups (recovery)
        Verify traffic (recovery)
        """
        pass

    def CASE301( self, main ):
        """
        Sets up 3 ONOS instances, start 2x5 topology
        Combines CASE07 with ONOS failure and recovery
        Verify flows and groups (failure)
        Verify traffic (failure)
        Verify flows and groups (recovery)
        Verify traffic (recovery)
        """
        pass
