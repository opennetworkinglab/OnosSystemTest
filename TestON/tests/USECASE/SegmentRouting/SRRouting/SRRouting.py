
class SRRouting:
    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        Ping between all ipv4 hosts in the topology.
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=1,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=1,
                               ipv6=0,
                               countFlowsGroups=False,
                               linkFailure=False,
                               description="Ping between all ipv4 hosts in the topology" )

    def CASE2( self, main ):
        """
        Ping between all ipv6 hosts in the topology.
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=2,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=0,
                               ipv6=1,
                               countFlowsGroups=False,
                               linkFailure=False,
                               description="Ping between all ipv6 hosts in the topology" )

    def CASE3( self, main ):
        """
        Ping between all ipv4 and ipv6 hosts in the topology.
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=3,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=1,
                               ipv6=1,
                               countFlowsGroups=False,
                               linkFailure=False,
                               description="Ping between all ipv4 and ipv6 hosts in the topology" )

    def CASE4( self, main ):
        """
        Ping between all ipv4 hosts in the topology and check connectivity to external ipv4 hosts
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=4,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=1,
                               ipv6=0,
                               description="Ping between all ipv4 hosts in the topology and check connectivity to external hosts",
                               checkExternalHost=True,
                               linkFailure=False,
                               countFlowsGroups=False )

    def CASE5( self, main ):
        """
        Ping between all ipv6 hosts in the topology and check connectivity to external ipv6 hosts
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=5,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=0,
                               ipv6=1,
                               description="Ping between all ipv6 hosts in the topology and check connectivity to external hosts",
                               checkExternalHost=True,
                               linkFailure=False,
                               countFlowsGroups=False )

    def CASE6( self, main ):
        """
        Ping between all ipv4 and ipv6 hosts in the topology and check connectivity to external ipv4 and ipv6 hosts
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=6,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=1,
                               ipv6=1,
                               description="Ping between all ipv4 and ipv6 hosts in the topology and check connectivity to external hosts",
                               checkExternalHost=True,
                               linkFailure=False,
                               countFlowsGroups=False )

    def CASE7( self, main ):
        """
        Ping between ipv4 hosts and an external host that is not configured in
        external router config, but reachable through the use of route-add
        command.
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=7,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=1,
                               ipv6=0,
                               description="Ping between from ipv4 hosts to external host configured with route-add command.",
                               checkExternalHost=False,
                               countFlowsGroups=False,
                               linkFailure=False,
                               staticRouteConfigure=True )

    def CASE8( self, main ):
        """
        Ping between ipv6 hosts and an external host that is not configured in
        external router config, but reachable through the use of route-add
        command.
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=8,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=0,
                               ipv6=1,
                               description="Ping between from ipv6 hosts to external host configured with route-add command.",
                               checkExternalHost=False,
                               countFlowsGroups=False,
                               linkFailure=False,
                               staticRouteConfigure=True )

    def CASE9( self, main ):
        """
        Ping between ipv4 and pv6 hosts and external hosts that is not configured in
        external router config, but reachable through the use of route-add
        command.
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=9,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=1,
                               ipv6=1,
                               description="Ping between from ipv4 and ipv6 hosts to external hosts configured with route-add command.",
                               checkExternalHost=False,
                               countFlowsGroups=False,
                               linkFailure=False,
                               staticRouteConfigure=True )

    def CASE101( self, main ):
        """
        Kill and recover links
        Ping between all ipv4 hosts in the topology.
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=101,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=1,
                               ipv6=0,
                               countFlowsGroups=False,
                               linkFailure=True,
                               description="Test link failures with IPv4 hosts",
                               switchFailure=False )

    def CASE102( self, main ):
        """
        Kill and recover links
        Ping between all ipv6 hosts in the topology.
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=102,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=0,
                               ipv6=1,
                               countFlowsGroups=False,
                               linkFailure=True,
                               description="Test link failures with IPv6 hosts",
                               switchFailure=False )

    def CASE103( self, main ):
        """
        Kill and recover links
        Ping between all ipv4 and ipv6 hosts in the topology.
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=103,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=1,
                               ipv6=1,
                               countFlowsGroups=False,
                               linkFailure=True,
                               description="Test link failures with IPv4 and IPv6 hosts",
                               switchFailure=False )

    def CASE104( self, main ):
        """
        Kill and recover links
        Ping between all ipv4 hosts in the topology and check connectivity to external ipv4 hosts
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=104,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=1,
                               ipv6=0,
                               description="Test link failures with IPv4 hosts (including external hosts)",
                               checkExternalHost=True,
                               linkFailure=True,
                               switchFailure=False )

    def CASE105( self, main ):
        """
        Kill and recover links
        Ping between all ipv6 hosts in the topology and check connectivity to external ipv6 hosts
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=105,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=0,
                               ipv6=1,
                               description="Test link failures with IPv6 hosts (including external hosts)",
                               checkExternalHost=True,
                               linkFailure=True,
                               switchFailure=False )

    def CASE106( self, main ):
        """
        Kill and recover links
        Ping between all ipv4 and ipv6 hosts in the topology and check connectivity to external ipv4 and ipv6 hosts
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=106,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=1,
                               ipv6=1,
                               description="Test link failures with IPv4 and IPv6 hosts (including external hosts)",
                               checkExternalHost=True,
                               linkFailure=True,
                               switchFailure=False )

    def CASE107( self, main ):
        """
        Kill and recover links
        Ping between ipv4 hosts and an external host that is not configured in
        external router config, but reachable through the use of route-add command.
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=107,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=1,
                               ipv6=0,
                               description="Test link failures with IPv4 hosts (including external host configured with route-add command)",
                               checkExternalHost=False,
                               countFlowsGroups=False,
                               linkFailure=True,
                               staticRouteConfigure=True,
                               switchFailure=False )

    def CASE108( self, main ):
        """
        Kill and recover links
        Ping between ipv6 hosts and an external host that is not configured in
        external router config, but reachable through the use of route-add command.
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=108,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=0,
                               ipv6=1,
                               description="Test link failures with IPv6 hosts (including external host configured with route-add command)",
                               checkExternalHost=False,
                               countFlowsGroups=False,
                               linkFailure=True,
                               staticRouteConfigure=True,
                               switchFailure=False )

    def CASE109( self, main ):
        """
        Kill and recover links
        Ping between ipv4 and pv6 hosts and external hosts that is not configured in
        external router config, but reachable through the use of route-add command.
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=109,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=1,
                               ipv6=1,
                               description="Test link failures with IPv4 and IPv6 hosts (including external host configured with route-add command)",
                               checkExternalHost=False,
                               countFlowsGroups=False,
                               linkFailure=True,
                               staticRouteConfigure=True,
                               switchFailure=False )

    def CASE201( self, main ):
        """
        Kill and recover spine switches
        Ping between all ipv4 hosts in the topology.
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=201,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=1,
                               ipv6=0,
                               countFlowsGroups=False,
                               linkFailure=False,
                               description="Test switch failures with IPv4 hosts",
                               switchFailure=True )

    def CASE202( self, main ):
        """
        Kill and recover spine switches
        Ping between all ipv6 hosts in the topology.
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=202,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=0,
                               ipv6=1,
                               countFlowsGroups=False,
                               linkFailure=False,
                               description="Test switch failures with IPv6 hosts",
                               switchFailure=True )

    def CASE203( self, main ):
        """
        Kill and recover spine switches
        Ping between all ipv4 and ipv6 hosts in the topology.
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=203,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=1,
                               ipv6=1,
                               countFlowsGroups=False,
                               linkFailure=False,
                               description="Test switch failures with IPv4 and IPv6 hosts",
                               switchFailure=True )

    def CASE204( self, main ):
        """
        Kill and recover spine switches
        Ping between all ipv4 hosts in the topology and check connectivity to external ipv4 hosts
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=204,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=1,
                               ipv6=0,
                               description="Test switch failures with IPv4 hosts (including external hosts)",
                               checkExternalHost=True,
                               linkFailure=False,
                               switchFailure=True )

    def CASE205( self, main ):
        """
        Kill and recover spine switches
        Ping between all ipv6 hosts in the topology and check connectivity to external ipv6 hosts
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=205,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=0,
                               ipv6=1,
                               description="Test switch failures with IPv6 hosts (including external hosts)",
                               checkExternalHost=True,
                               linkFailure=False,
                               switchFailure=True )

    def CASE206( self, main ):
        """
        Kill and recover spine switches
        Ping between all ipv4 and ipv6 hosts in the topology and check connectivity to external ipv4 and ipv6 hosts
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=206,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=1,
                               ipv6=1,
                               description="Test switch failures with IPv4 and IPv6 hosts (including external hosts)",
                               checkExternalHost=True,
                               linkFailure=False,
                               switchFailure=True )

    def CASE207( self, main ):
        """
        Kill and recover spine switches
        Ping between ipv4 hosts and an external host that is not configured in
        external router config, but reachable through the use of route-add command.
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=207,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=1,
                               ipv6=0,
                               description="Test switch failures with IPv4 hosts (including external host configured with route-add command)",
                               checkExternalHost=False,
                               countFlowsGroups=False,
                               linkFailure=False,
                               staticRouteConfigure=True,
                               switchFailure=True )

    def CASE208( self, main ):
        """
        Kill and recover spine switches
        Ping between ipv6 hosts and an external host that is not configured in
        external router config, but reachable through the use of route-add command.
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=208,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=0,
                               ipv6=1,
                               description="Test switch failures with IPv6 hosts (including external host configured with route-add command)",
                               checkExternalHost=False,
                               countFlowsGroups=False,
                               linkFailure=False,
                               staticRouteConfigure=True,
                               switchFailure=True )

    def CASE209( self, main ):
        """
        Kill and recover spine switches
        Ping between ipv4 and pv6 hosts and external hosts that is not configured in
        external router config, but reachable through the use of route-add command.
        """

        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import SRRoutingTest

        SRRoutingTest.runTest( main,
                               test_idx=209,
                               onosNodes=3,
                               dhcp=1,
                               routers=1,
                               ipv4=1,
                               ipv6=1,
                               description="Test switch failures with IPv4 and IPv6 hosts (including external host configured with route-add command)",
                               checkExternalHost=False,
                               countFlowsGroups=False,
                               linkFailure=False,
                               staticRouteConfigure=True,
                               switchFailure=True )


