class SRDhcprelay:
    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        DHCP v4 tests
        Client: 4 clients attached to switch directly
        Server: 1 server attached to switch directly
        Sets up 3 ONOS instance
        """
        from tests.USECASE.SegmentRouting.SRDhcprelay.dependencies.SRDhcprelayTest import SRDhcprelayTest
        SRDhcprelayTest.runTest( main,
                                 testIndex=1,
                                 onosNodes=3,
                                 description="DHCP v4 tests with 4 clients attached to switch directly and 1 server attached to switch directly" )

    def CASE2( self, main ):
        """
        DHCP v4 tests
        Client: 4 clients attached to switch directly
        Server: 1 server attached to switch indirectly (via gateway)
        Sets up 3 ONOS instance
        """
        from tests.USECASE.SegmentRouting.SRDhcprelay.dependencies.SRDhcprelayTest import SRDhcprelayTest
        SRDhcprelayTest.runTest( main,
                                 testIndex=2,
                                 onosNodes=3,
                                 description="DHCP v4 tests with 4 clients attached to switch directly and 1 server attached to switch indirectly (via gateway)",
                                 remoteServer=True )

    def CASE3( self, main ):
        """
        DHCP v4 tests
        Client: 2 clients attached to switch directly, 2 clients via DHCP relay
        Server: 1 server attached to switch directly
        Sets up 3 ONOS instance
        """
        from tests.USECASE.SegmentRouting.SRDhcprelay.dependencies.SRDhcprelayTest import SRDhcprelayTest
        SRDhcprelayTest.runTest( main,
                                 testIndex=3,
                                 onosNodes=3,
                                 description="DHCP v4 tests with 2 clients attached to switch directly and 2 clients via DHCP relay and and 1 server attached to switch directly",
                                 dhcpRelay=True )

    def CASE4( self, main ):
        """
        DHCP v4 tests
        Client: 2 clients attached to switch directly, 2 clients via DHCP relay
        Server: 1 server attached to switch indirectly (via gateway)
        Sets up 3 ONOS instance
        """
        from tests.USECASE.SegmentRouting.SRDhcprelay.dependencies.SRDhcprelayTest import SRDhcprelayTest
        SRDhcprelayTest.runTest( main,
                                 testIndex=4,
                                 onosNodes=3,
                                 description="DHCP v4 tests with 4 clients attached to switch directly and 2 clients via DHCP relay and and 1 server attached to switch indirectly (via gateway)",
                                 dhcpRelay=True,
                                 remoteServer=True )

    def CASE5( self, main ):
        """
        DHCP v4 tests
        Client: 2 clients attached to switch directly, 2 clients via DHCP relay
        Server: 1 server attached to switch directly for directly connected hosts
                another server attached to switch directly for indirectly connected hosts
        Sets up 3 ONOS instance
        """
        from tests.USECASE.SegmentRouting.SRDhcprelay.dependencies.SRDhcprelayTest import SRDhcprelayTest
        SRDhcprelayTest.runTest( main,
                                 testIndex=5,
                                 onosNodes=3,
                                 description="DHCP v4 tests with 2 clients attached to switch directly, 2 clients via DHCP relay and, 1 server attached to switch directly for direcly connected hosts and another server attached to switch directly for indirectly connected hosts",
                                 dhcpRelay=True,
                                 multipleServer=True )

    def CASE6( self, main ):
        """
        DHCP v4 tests
        Client: 2 clients attached to switch directly, 2 clients via DHCP relay
        Server: 1 server attached to switch directly for directly connected hosts
                another server attached to switch directly for indirectly connected hosts
                "DhcpRelayAgentIp" addresses are configured for indirect hosts
        Sets up 3 ONOS instance
        """
        from tests.USECASE.SegmentRouting.SRDhcprelay.dependencies.SRDhcprelayTest import SRDhcprelayTest
        SRDhcprelayTest.runTest( main,
                                 testIndex=6,
                                 onosNodes=3,
                                 description="DHCP v4 tests with 2 clients attached to switch directly, 2 clients via DHCP relay and, 1 server attached to switch directly for direcly connected hosts and another server attached to switch directly for indirectly connected hosts, 'DhcpRelayAgentIp' addresses are configured for indirect hosts",
                                 dhcpRelay=True,
                                 multipleServer=True )

    def CASE11( self, main ):
        """
        DHCP v6 tests
        Client: 4 clients attached to switch directly
        Server: 1 server attached to switch directly
        Sets up 3 ONOS instance
        """
        from tests.USECASE.SegmentRouting.SRDhcprelay.dependencies.SRDhcprelayTest import SRDhcprelayTest
        SRDhcprelayTest.runTest( main,
                                 testIndex=11,
                                 onosNodes=3,
                                 description="DHCP v6 tests with 4 clients attached to switch directly and 1 server attached to switch directly",
                                 ipv6=True )

    def CASE12( self, main ):
        """
        DHCP v6 tests
        Client: 4 clients attached to switch directly
        Server: 1 server attached to switch indirectly (via gateway)
        Sets up 3 ONOS instance
        """
        from tests.USECASE.SegmentRouting.SRDhcprelay.dependencies.SRDhcprelayTest import SRDhcprelayTest
        SRDhcprelayTest.runTest( main,
                                 testIndex=12,
                                 onosNodes=3,
                                 description="DHCP v6 tests with 4 clients attached to switch directly and 1 server attached to switch indirectly (via gateway)",
                                 remoteServer=True,
                                 ipv6=True )

    def CASE13( self, main ):
        """
        DHCP v6 tests
        Client: 2 clients attached to switch directly, 2 clients via DHCP relay
        Server: 1 server attached to switch directly
        Sets up 3 ONOS instance
        """
        from tests.USECASE.SegmentRouting.SRDhcprelay.dependencies.SRDhcprelayTest import SRDhcprelayTest
        SRDhcprelayTest.runTest( main,
                                 testIndex=13,
                                 onosNodes=3,
                                 description="DHCP v6 tests with 2 clients attached to switch directly and 2 clients via DHCP relay and and 1 server attached to switch directly",
                                 dhcpRelay=True,
                                 ipv6=True )

    def CASE14( self, main ):
        """
        DHCP v6 tests
        Client: 2 clients attached to switch directly, 2 clients via DHCP relay
        Server: 1 server attached to switch indirectly (via gateway)
        Sets up 3 ONOS instance
        """
        from tests.USECASE.SegmentRouting.SRDhcprelay.dependencies.SRDhcprelayTest import SRDhcprelayTest
        SRDhcprelayTest.runTest( main,
                                 testIndex=14,
                                 onosNodes=3,
                                 description="DHCP v6 tests with 4 clients attached to switch directly and 2 clients via DHCP relay and and 1 server attached to switch indirectly (via gateway)",
                                 dhcpRelay=True,
                                 remoteServer=True,
                                 ipv6=True )

    def CASE15( self, main ):
        """
        DHCP v6 tests
        Client: 2 clients attached to switch directly, 2 clients via DHCP relay
        Server: 1 server attached to switch directly for directly connected hosts
                another server attached to switch directly for indirectly connected hosts
        Sets up 3 ONOS instance
        """
        from tests.USECASE.SegmentRouting.SRDhcprelay.dependencies.SRDhcprelayTest import SRDhcprelayTest
        SRDhcprelayTest.runTest( main,
                                 testIndex=15,
                                 onosNodes=3,
                                 description="DHCP v6 tests with 2 clients attached to switch directly, 2 clients via DHCP relay and, 1 server attached to switch directly for direcly connected hosts and another server attached to switch directly for indirectly connected hosts",
                                 dhcpRelay=True,
                                 multipleServer=True,
                                 ipv6=True )

    def CASE16( self, main ):
        """
        DHCP v6 tests
        Client: 2 clients attached to switch directly, 2 clients via DHCP relay
        Server: 1 server attached to switch directly for directly connected hosts
                another server attached to switch directly for indirectly connected hosts
                "DhcpRelayAgentIp" addresses are configured for indirect hosts
        Sets up 3 ONOS instance
        """
        from tests.USECASE.SegmentRouting.SRDhcprelay.dependencies.SRDhcprelayTest import SRDhcprelayTest
        SRDhcprelayTest.runTest( main,
                                 testIndex=16,
                                 onosNodes=3,
                                 description="DHCP v6 tests with 2 clients attached to switch directly, 2 clients via DHCP relay and, 1 server attached to switch directly for direcly connected hosts and another server attached to switch directly for indirectly connected hosts, 'DhcpRelayAgentIp' addresses are configured for indirect hosts",
                                 dhcpRelay=True,
                                 multipleServer=True,
                                 ipv6=True )

    def CASE21( self, main ):
        """
        DHCP v4 tests with tagged hosts
        Client: 4 clients attached to switch directly
        Server: 1 server attached to switch directly
        Sets up 3 ONOS instance
        """
        from tests.USECASE.SegmentRouting.SRDhcprelay.dependencies.SRDhcprelayTest import SRDhcprelayTest
        SRDhcprelayTest.runTest( main,
                                 testIndex=21,
                                 onosNodes=3,
                                 description="DHCP v4 tests with tagged hosts: 4 clients attached to switch directly and 1 server attached to switch directly",
                                 vlan=[ 20, 20, 30, 30 ] )

    def CASE22( self, main ):
        """
        DHCP v4 tests with tagged hosts
        Client: 4 clients attached to switch directly
        Server: 1 server attached to switch indirectly (via gateway)
        Sets up 3 ONOS instance
        """
        from tests.USECASE.SegmentRouting.SRDhcprelay.dependencies.SRDhcprelayTest import SRDhcprelayTest
        SRDhcprelayTest.runTest( main,
                                 testIndex=22,
                                 onosNodes=3,
                                 description="DHCP v4 tests with tagged hosts: 4 clients attached to switch directly and 1 server attached to switch indirectly (via gateway)",
                                 remoteServer=True,
                                 vlan=[ 20, 20, 30, 30 ] )

    def CASE31( self, main ):
        """
        DHCP v6 tests with tagged hosts
        Client: 4 clients attached to switch directly
        Server: 1 server attached to switch directly
        Sets up 3 ONOS instance
        """
        from tests.USECASE.SegmentRouting.SRDhcprelay.dependencies.SRDhcprelayTest import SRDhcprelayTest
        SRDhcprelayTest.runTest( main,
                                 testIndex=31,
                                 onosNodes=3,
                                 description="DHCP v6 tests with tagged hosts: 4 clients attached to switch directly and 1 server attached to switch directly",
                                 ipv6=True,
                                 vlan=[ 40, 40, 50, 50 ] )

    def CASE41( self, main ):
        """
        DHCP v4 tests with dual-homed hosts
        Client: 4 clients attached to switch directly
        Server: 1 server attached to switch directly
        Sets up 3 ONOS instance
        """
        from tests.USECASE.SegmentRouting.SRDhcprelay.dependencies.SRDhcprelayTest import SRDhcprelayTest
        SRDhcprelayTest.runTest( main,
                                 testIndex=41,
                                 onosNodes=3,
                                 description="DHCP v4 tests with dual-homed hosts: 4 clients attached to switch directly and 1 server attached to switch directly",
                                 dualHomed=True )

    def CASE51( self, main ):
        """
        DHCP v6 tests with dual-homed hosts
        Client: 4 clients attached to switch directly
        Server: 1 server attached to switch directly
        Sets up 3 ONOS instance
        """
        from tests.USECASE.SegmentRouting.SRDhcprelay.dependencies.SRDhcprelayTest import SRDhcprelayTest
        SRDhcprelayTest.runTest( main,
                                 testIndex=51,
                                 onosNodes=3,
                                 description="DHCP v6 tests with dual-homed hosts: 4 clients attached to switch directly and 1 server attached to switch directly",
                                 ipv6=True,
                                 dualHomed=True )

    def CASE61( self, main ):
        """
        DHCP v4 tests with dual-homed tagged hosts
        Client: 4 clients attached to switch directly
        Server: 1 server attached to switch directly
        Sets up 3 ONOS instance
        """
        from tests.USECASE.SegmentRouting.SRDhcprelay.dependencies.SRDhcprelayTest import SRDhcprelayTest
        SRDhcprelayTest.runTest( main,
                                 testIndex=61,
                                 onosNodes=3,
                                 description="DHCP v4 tests with dual-homed tagged hosts: 4 clients attached to switch directly and 1 server attached to switch directly",
                                 vlan=[ 20, 20, 30, 30 ],
                                 dualHomed=True )

    def CASE71( self, main ):
        """
        DHCP v6 tests with dual-homed tagged hosts
        Client: 4 clients attached to switch directly
        Server: 1 server attached to switch directly
        Sets up 3 ONOS instance
        """
        from tests.USECASE.SegmentRouting.SRDhcprelay.dependencies.SRDhcprelayTest import SRDhcprelayTest
        SRDhcprelayTest.runTest( main,
                                 testIndex=71,
                                 onosNodes=3,
                                 description="DHCP v6 tests with dual-homed tagged hosts: 4 clients attached to switch directly and 1 server attached to switch directly",
                                 ipv6=True,
                                 vlan=[ 40, 40, 50, 50 ],
                                 dualHomed=True )
