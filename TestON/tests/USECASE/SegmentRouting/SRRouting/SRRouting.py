
class SRRouting:
    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        Ping between all ipv4 hosts in the topology.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Ping between all ipv4 hosts in the topology" )
        setupTest( main, test_idx=1, onosNodes=3, ipv6=False, external=False )
        verify( main, ipv6=False, disconnected=False, external=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE2( self, main ):
        """
        Ping between all ipv6 hosts in the topology.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Ping between all ipv6 hosts in the topology" )
        setupTest( main, test_idx=2, onosNodes=3, ipv4=False, external=False )
        verify( main, ipv4=False, disconnected=False, external=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE3( self, main ):
        """
        Ping between all ipv4 and ipv6 hosts in the topology.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Ping between all ipv4 and ipv6 hosts in the topology" )
        setupTest( main, test_idx=3, onosNodes=3, external=False )
        verify( main, disconnected=False, external=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE4( self, main ):
        """
        Ping between all ipv4 hosts in the topology and check connectivity to external ipv4 hosts
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Ping between all ipv4 hosts in the topology and check connectivity to external ipv4 hosts" )
        setupTest( main, test_idx=4, onosNodes=3, ipv6=False )
        verify( main, ipv6=False, disconnected=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE5( self, main ):
        """
        Ping between all ipv6 hosts in the topology and check connectivity to external ipv6 hosts
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Ping between all ipv6 hosts in the topology and check connectivity to external ipv6 hosts" )
        setupTest( main, test_idx=5, onosNodes=3, ipv4=False )
        verify( main, ipv4=False, disconnected=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE6( self, main ):
        """
        Ping between all ipv4 and ipv6 hosts in the topology and check connectivity to external ipv4 and ipv6 hosts
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Ping between all ipv4 and ipv6 hosts in the topology and check connectivity to external hosts" )
        setupTest( main, test_idx=6, onosNodes=3 )
        verify( main, disconnected=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE7( self, main ):
        """
        Ping between ipv4 hosts and an external host that is not configured in
        external router config, but reachable through the use of route-add
        command.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Ping between from ipv4 hosts to external host configured with route-add command" )
        setupTest( main, test_idx=7, onosNodes=3, ipv6=False, external=False )
        verify( main, ipv6=False, internal=False, disconnected=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE8( self, main ):
        """
        Ping between ipv6 hosts and an external host that is not configured in
        external router config, but reachable through the use of route-add
        command.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Ping between from ipv6 hosts to external host configured with route-add command" )
        setupTest( main, test_idx=8, onosNodes=3, ipv4=False, external=False )
        verify( main, ipv6=False, internal=False, disconnected=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE9( self, main ):
        """
        Ping between ipv4 and pv6 hosts and external hosts that is not configured in
        external router config, but reachable through the use of route-add
        command.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Ping between from ipv4 and ipv6 hosts to external host configured with route-add command" )
        setupTest( main, test_idx=9, onosNodes=3, external=False )
        verify( main, internal=False, disconnected=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE101( self, main ):
        """
        Kill and recover links
        Ping between all ipv4 hosts in the topology.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test link failures with IPv4 hosts" )
        setupTest( main, test_idx=101, onosNodes=3, ipv6=False, external=False )
        verify( main, ipv6=False, external=False, disconnected=False )
        verifyLinkFailure( main, ipv6=False, external=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE102( self, main ):
        """
        Kill and recover links
        Ping between all ipv6 hosts in the topology.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test link failures with IPv6 hosts" )
        setupTest( main, test_idx=102, onosNodes=3, ipv4=False, external=False )
        verify( main, ipv4=False, external=False, disconnected=False )
        verifyLinkFailure( main, ipv4=False, external=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE103( self, main ):
        """
        Kill and recover links
        Ping between all ipv4 and ipv6 hosts in the topology.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test link failures with IPv4 and IPv6 hosts" )
        setupTest( main, test_idx=103, onosNodes=3, external=False )
        verify( main, external=False, disconnected=False )
        verifyLinkFailure( main, external=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE104( self, main ):
        """
        Kill and recover links
        Ping between all ipv4 hosts in the topology and check connectivity to external ipv4 hosts
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test link failures with IPv4 hosts including external hosts" )
        setupTest( main, test_idx=104, onosNodes=3, ipv6=False )
        verify( main, ipv6=False, disconnected=False )
        verifyLinkFailure( main, ipv6=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE105( self, main ):
        """
        Kill and recover links
        Ping between all ipv6 hosts in the topology and check connectivity to external ipv6 hosts
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test link failures with IPv6 hosts including external hosts" )
        setupTest( main, test_idx=105, onosNodes=3, ipv4=False )
        verify( main, ipv4=False, disconnected=False )
        verifyLinkFailure( main, ipv4=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE106( self, main ):
        """
        Kill and recover links
        Ping between all ipv4 and ipv6 hosts in the topology and check connectivity to external ipv4 and ipv6 hosts
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test link failures with IPv4 and IPv6 hosts including external hosts" )
        setupTest( main, test_idx=106, onosNodes=3 )
        verify( main, disconnected=False )
        verifyLinkFailure( main )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE107( self, main ):
        """
        Kill and recover links
        Ping between ipv4 hosts and an external host that is not configured in
        external router config, but reachable through the use of route-add command.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test link failures with IPv4 hosts including external hosts configured with route-add command" )
        setupTest( main, test_idx=107, onosNodes=3, ipv6=False, external=False )
        verify( main, ipv6=False, disconnected=False )
        verifyLinkFailure( main, ipv6=False, internal=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE108( self, main ):
        """
        Kill and recover links
        Ping between ipv6 hosts and an external host that is not configured in
        external router config, but reachable through the use of route-add command.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test link failures with IPv6 hosts including external hosts configured with route-add command" )
        setupTest( main, test_idx=108, onosNodes=3, ipv4=False, external=False )
        verify( main, ipv4=False, disconnected=False )
        verifyLinkFailure( main, ipv4=False, internal=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE109( self, main ):
        """
        Kill and recover links
        Ping between ipv4 and pv6 hosts and external hosts that is not configured in
        external router config, but reachable through the use of route-add command.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test link failures with IPv4 and IPv6 hosts including external hosts configured with route-add command" )
        setupTest( main, test_idx=109, onosNodes=3, external=False )
        verify( main, disconnected=False )
        verifyLinkFailure( main, internal=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE201( self, main ):
        """
        Kill and recover spine switches
        Ping between all ipv4 hosts in the topology.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test switch failures with IPv4 hosts" )
        setupTest( main, test_idx=201, onosNodes=3, ipv6=False, external=False )
        verify( main, ipv6=False, external=False, disconnected=False )
        verifySwitchFailure( main, ipv6=False, external=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE202( self, main ):
        """
        Kill and recover spine switches
        Ping between all ipv6 hosts in the topology.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test switch failures with IPv6 hosts" )
        setupTest( main, test_idx=202, onosNodes=3, ipv4=False, external=False )
        verify( main, ipv4=False, external=False, disconnected=False )
        verifySwitchFailure( main, ipv4=False, external=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE203( self, main ):
        """
        Kill and recover spine switches
        Ping between all ipv4 and ipv6 hosts in the topology.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test switch failures with IPv4 and IPv6 hosts" )
        setupTest( main, test_idx=203, onosNodes=3, external=False )
        verify( main, external=False, disconnected=False )
        verifySwitchFailure( main, external=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE204( self, main ):
        """
        Kill and recover spine switches
        Ping between all ipv4 hosts in the topology and check connectivity to external ipv4 hosts
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test switch failures with IPv4 hosts including external hosts" )
        setupTest( main, test_idx=204, onosNodes=3, ipv6=False )
        verify( main, ipv6=False, disconnected=False )
        verifySwitchFailure( main, ipv6=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE205( self, main ):
        """
        Kill and recover spine switches
        Ping between all ipv6 hosts in the topology and check connectivity to external ipv6 hosts
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test switch failures with IPv6 hosts including external hosts" )
        setupTest( main, test_idx=205, onosNodes=3, ipv4=False )
        verify( main, ipv4=False, disconnected=False )
        verifySwitchFailure( main, ipv4=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE206( self, main ):
        """
        Kill and recover spine switches
        Ping between all ipv4 and ipv6 hosts in the topology and check connectivity to external ipv4 and ipv6 hosts
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test switch failures with IPv4 and IPv6 hosts including external hosts" )
        setupTest( main, test_idx=206, onosNodes=3 )
        verify( main, disconnected=False )
        verifySwitchFailure( main )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE207( self, main ):
        """
        Kill and recover spine switches
        Ping between ipv4 hosts and an external host that is not configured in
        external router config, but reachable through the use of route-add command.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test switch failures with IPv4 hosts including external hosts configured with route-add command" )
        setupTest( main, test_idx=207, onosNodes=3, ipv6=False, external=False )
        verify( main, ipv6=False, disconnected=False )
        verifySwitchFailure( main, ipv6=False, internal=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE208( self, main ):
        """
        Kill and recover spine switches
        Ping between ipv6 hosts and an external host that is not configured in
        external router config, but reachable through the use of route-add command.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test switch failures with IPv6 hosts including external hosts configured with route-add command" )
        setupTest( main, test_idx=208, onosNodes=3, ipv4=False, external=False )
        verify( main, ipv4=False, disconnected=False )
        verifySwitchFailure( main, ipv4=False, internal=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE209( self, main ):
        """
        Kill and recover spine switches
        Ping between ipv4 and pv6 hosts and external hosts that is not configured in
        external router config, but reachable through the use of route-add command.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test switch failures with IPv4 and IPv6 hosts including external hosts configured with route-add command" )
        setupTest( main, test_idx=209, onosNodes=3, external=False )
        verify( main, disconnected=False )
        verifySwitchFailure( main, internal=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE301( self, main ):
        """
        Kill and recover onos nodes
        Ping between all ipv4 hosts in the topology.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test onos failures with IPv4 hosts" )
        setupTest( main, test_idx=301, onosNodes=3, ipv6=False, external=False )
        verify( main, ipv6=False, external=False, disconnected=False )
        verifyOnosFailure( main, ipv6=False, external=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE302( self, main ):
        """
        Kill and recover onos nodes
        Ping between all ipv6 hosts in the topology.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test onos failures with IPv6 hosts" )
        setupTest( main, test_idx=302, onosNodes=3, ipv4=False, external=False )
        verify( main, ipv4=False, external=False, disconnected=False )
        verifyOnosFailure( main, ipv4=False, external=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE303( self, main ):
        """
        Kill and recover onos nodes
        Ping between all ipv4 and ipv6 hosts in the topology.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test onos failures with IPv4 and IPv6 hosts" )
        setupTest( main, test_idx=303, onosNodes=3, external=False )
        verify( main, external=False, disconnected=False )
        verifyOnosFailure( main, external=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE304( self, main ):
        """
        Kill and recover onos nodes
        Ping between all ipv4 hosts in the topology and check connectivity to external ipv4 hosts
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test onos failures with IPv4 hosts including external hosts" )
        setupTest( main, test_idx=304, onosNodes=3, ipv6=False )
        verify( main, ipv6=False, disconnected=False )
        verifyOnosFailure( main, ipv6=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE305( self, main ):
        """
        Kill and recover onos nodes
        Ping between all ipv6 hosts in the topology and check connectivity to external ipv6 hosts
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test onos failures with IPv6 hosts including external hosts" )
        setupTest( main, test_idx=305, onosNodes=3, ipv4=False )
        verify( main, ipv4=False, disconnected=False )
        verifyOnosFailure( main, ipv4=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE306( self, main ):
        """
        Kill and recover onos nodes
        Ping between all ipv4 and ipv6 hosts in the topology and check connectivity to external ipv4 and ipv6 hosts
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test onos failures with IPv4 and IPv6 hosts including external hosts" )
        setupTest( main, test_idx=306, onosNodes=3 )
        verify( main, disconnected=False )
        verifyOnosFailure( main )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE307( self, main ):
        """
        Kill and recover onos nodes
        Ping between ipv4 hosts and an external host that is not configured in
        external router config, but reachable through the use of route-add command.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test onos failures with IPv4 hosts including external hosts configured with route-add command" )
        setupTest( main, test_idx=307, onosNodes=3, ipv6=False, external=False )
        verify( main, ipv6=False, disconnected=False )
        verifyOnosFailure( main, ipv6=False, internal=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE308( self, main ):
        """
        Kill and recover onos nodes
        Ping between ipv6 hosts and an external host that is not configured in
        external router config, but reachable through the use of route-add command.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test onos failures with IPv6 hosts including external hosts configured with route-add command" )
        setupTest( main, test_idx=308, onosNodes=3, ipv4=False, external=False )
        verify( main, ipv4=False, disconnected=False )
        verifyOnosFailure( main, ipv4=False, internal=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE309( self, main ):
        """
        Kill and recover onos nodes
        Ping between ipv4 and pv6 hosts and external hosts that is not configured in
        external router config, but reachable through the use of route-add command.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Test onos failures with IPv4 and IPv6 hosts including external hosts configured with route-add command" )
        setupTest( main, test_idx=309, onosNodes=3, external=False )
        verify( main, disconnected=False )
        verifyOnosFailure( main, internal=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE603( self, main ):
        """"
        Drop HAGG-1 device and test connectivity.
        Drop DAAS-1 device and test connectivity (some hosts lost it)
        Bring up DAAS-1 and test connectivity (all hosts gained it again)

        Repeat the same with HAGG-2 and DAAS-2.
        """
        import time
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Drop hagg spine switch along with dass leaf switch." )
        setupTest( main, test_idx=603, onosNodes=3 )
        main.disconnectedIpv4Hosts = []
        main.disconnectedIpv6Hosts = []

        verify( main )
        lib.killSwitch( main, "spine103", int( main.params[ "TOPO" ]["switchNum" ] ) - 1, int( main.params[ "TOPO" ][ "linkNum" ] ) - 6 )
        verify( main )
        lib.killSwitch( main, "leaf6", int( main.params[ "TOPO" ]["switchNum" ] ) - 2, int( main.params[ "TOPO" ][ "linkNum" ] ) - 8 )
        main.disconnectedIpv4Hosts = [ 'h12v4', 'h13v4']
        main.disconnectedIpv6Hosts = [ 'h12v6', 'h13v6']
        verify( main )
        lib.recoverSwitch( main, "leaf6", int( main.params[ "TOPO" ]["switchNum" ] ) - 1, int( main.params[ "TOPO" ][ "linkNum" ] ) - 6, rediscoverHosts=True)
        main.disconnectedIpv4Hosts = []
        main.disconnectedIpv6Hosts = []
        verify( main )
        lib.recoverSwitch( main, "spine103", int( main.params[ "TOPO" ][ "switchNum" ] ), int( main.params[ "TOPO" ][ "linkNum" ] ))
        verify( main )

        lib.killSwitch( main, "spine104", int( main.params[ "TOPO" ]["switchNum" ] ) - 1, int( main.params[ "TOPO" ][ "linkNum" ] ) - 6 )
        verify( main )
        lib.killSwitch( main, "leaf1", int( main.params[ "TOPO" ]["switchNum" ] ) - 2, int( main.params[ "TOPO" ][ "linkNum" ] ) - 8 )
        main.disconnectedIpv4Hosts = [ 'h1v4', 'h2v4']
        main.disconnectedIpv6Hosts = [ 'h1v6', 'h2v6']
        verify( main )
        lib.recoverSwitch( main, "leaf1", int( main.params[ "TOPO" ]["switchNum" ] ) - 1, int( main.params[ "TOPO" ][ "linkNum" ] ) - 6, rediscoverHosts=True)
        main.disconnectedIpv4Hosts = []
        main.disconnectedIpv6Hosts = []
        verify( main )
        lib.recoverSwitch( main, "spine104", int( main.params[ "TOPO" ][ "switchNum" ] ), int( main.params[ "TOPO" ][ "linkNum" ] ))
        verify( main )

        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE604( self, main ):
        """"
        Drop HAGG-1 device and test connectivity.
        Bring up HAGG-1 and test connectivity.
        Drop HAGG-2 device and test connectivity.
        Bring up HAGG-2 device and test connectivity
        """
        import time
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Drop hagg spine switches." )
        setupTest( main, test_idx=604, onosNodes=3 )
        main.disconnectedIpv4Hosts = []
        main.disconnectedIpv6Hosts = []
        verify( main )
        lib.killSwitch( main, "spine103", int( main.params[ "TOPO" ]["switchNum" ] ) - 1, int( main.params[ "TOPO" ][ "linkNum" ] ) - 6 )
        verify( main )
        lib.recoverSwitch( main, "spine103", int( main.params[ "TOPO" ][ "switchNum" ] ), int( main.params[ "TOPO" ][ "linkNum" ] ))
        verify( main )
        lib.killSwitch( main, "spine104", int( main.params[ "TOPO" ]["switchNum" ] ) - 1, int( main.params[ "TOPO" ][ "linkNum" ] ) - 6 )
        verify( main )
        lib.recoverSwitch( main, "spine104", int( main.params[ "TOPO" ][ "switchNum" ] ), int( main.params[ "TOPO" ][ "linkNum" ] ))
        verify( main )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE606( self, main ):
        """
        Drop SPINE-1 and test connectivity
        Drop paired leaf and test connectivity (expect some failures)
        Bring up SPINE-1 and test connectivity (still expect some failures)
        Bring up the paired leaf and test connectivity
        Repeat above with SPINE-2 and a different paired leaf
        """
        import time
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Drop spine and paired leaf" )
        setupTest( main, test_idx=606, onosNodes=3 )
        verify( main, disconnected=False )
        lib.killSwitch( main, "spine101", 9, 30 )
        verify( main, disconnected=False )
        lib.killSwitch( main, "leaf2", 8, 24 )
        lib.killSwitch( main, "leaf3", 7, 20 )
        main.disconnectedIpv4Hosts = [ "h3v4", "h4v4", "h5v4", "h6v4", "h7v4" ]
        main.disconnectedIpv6Hosts = [ "h3v6", "h4v6", "h5v6", "h6v6", "h7v6" ]
        verify( main )
        lib.recoverSwitch( main, "spine101", 8, 30 )
        verify( main )
        lib.recoverSwitch( main, "leaf3", 9, 38 )
        lib.recoverSwitch( main, "leaf2", 10, 48 )
        main.disconnectedIpv4Hosts = []
        main.disconnectedIpv6Hosts = []
        verify( main )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )
