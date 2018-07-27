
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
        setupTest( main, test_idx=7, onosNodes=3, ipv6=False, external=False, static=True )
        main.externalIpv4Hosts = main.staticIpv4Hosts
        main.externalIpv6Hosts = main.staticIpv6Hosts
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
        setupTest( main, test_idx=8, onosNodes=3, ipv4=False, external=False, static=True )
        main.externalIpv4Hosts = main.staticIpv4Hosts
        main.externalIpv6Hosts = main.staticIpv6Hosts
        verify( main, ipv4=False, internal=False, disconnected=False )
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
        setupTest( main, test_idx=9, onosNodes=3, external=False, static=True )
        main.externalIpv4Hosts = main.staticIpv4Hosts
        main.externalIpv6Hosts = main.staticIpv6Hosts
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
        setupTest( main, test_idx=107, onosNodes=3, ipv6=False, external=False, static=True )
        main.externalIpv4Hosts = main.staticIpv4Hosts
        main.externalIpv6Hosts = main.staticIpv6Hosts
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
        setupTest( main, test_idx=108, onosNodes=3, ipv4=False, external=False, static=True )
        main.externalIpv4Hosts = main.staticIpv4Hosts
        main.externalIpv6Hosts = main.staticIpv6Hosts
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
        setupTest( main, test_idx=109, onosNodes=3, external=False, static=True )
        main.externalIpv4Hosts = main.staticIpv4Hosts
        main.externalIpv6Hosts = main.staticIpv6Hosts
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
        setupTest( main, test_idx=207, onosNodes=3, ipv6=False, external=False, static=True )
        main.externalIpv4Hosts = main.staticIpv4Hosts
        main.externalIpv6Hosts = main.staticIpv6Hosts
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
        setupTest( main, test_idx=208, onosNodes=3, ipv4=False, external=False, static=True )
        main.externalIpv4Hosts = main.staticIpv4Hosts
        main.externalIpv6Hosts = main.staticIpv6Hosts
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
        setupTest( main, test_idx=209, onosNodes=3, external=False, static=True )
        main.externalIpv4Hosts = main.staticIpv4Hosts
        main.externalIpv6Hosts = main.staticIpv6Hosts
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
        setupTest( main, test_idx=307, onosNodes=3, ipv6=False, external=False, static=True )
        main.externalIpv4Hosts = main.staticIpv4Hosts
        main.externalIpv6Hosts = main.staticIpv6Hosts
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
        setupTest( main, test_idx=308, onosNodes=3, ipv4=False, external=False, static=True )
        main.externalIpv4Hosts = main.staticIpv4Hosts
        main.externalIpv6Hosts = main.staticIpv6Hosts
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
        setupTest( main, test_idx=309, onosNodes=3, external=False, static=True )
        main.externalIpv4Hosts = main.staticIpv4Hosts
        main.externalIpv6Hosts = main.staticIpv6Hosts
        verify( main, disconnected=False )
        verifyOnosFailure( main, internal=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE601( self, main ):
        """
        Bring down all switches
        Verify Topology
        Bring up all switches
        Verify

        repeat x3
        """
        import time
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Bring down all switches then recover" )
        setupTest( main, test_idx=601, external=False )
        main.Cluster.next().CLI.balanceMasters()
        time.sleep( float( main.params[ 'timers' ][ 'balanceMasterSleep' ] ) )
        main.Network.discoverHosts( hostList=main.internalIpv4Hosts + main.internalIpv6Hosts )
        totalSwitches = int( main.params[ 'TOPO' ][ 'switchNum' ] )
        totalLinks = int( main.params[ 'TOPO' ][ 'linkNum' ] )
        switchList = [ 'spine101', 'spine102', 'spine103', 'spine104',
                       'leaf1', 'leaf2', 'leaf3', 'leaf4', 'leaf5', 'leaf6' ]
        verify( main, disconnected=False, external=False )
        for i in range( 1, 4 ):
            main.log.info( "Beginning iteration {} of stopping then starting all switches".format( i ) )
            main.log.debug( main.Cluster.next().summary() )
            # Bring down all switches
            main.step( "Stopping switches - iteration " + str( i ) )
            switchStop = main.TRUE
            for switch in switchList:
                switchStop = switchStop and main.Network.switch( SW=switch, OPTION="stop" )
            utilities.assert_equals( expect=main.TRUE, actual=switchStop,
                                     onpass="All switches stopped",
                                     onfail="Failed to stop all switches" )

            time.sleep( 60 )
            lib.verifyTopology( main, 0, 0, main.Cluster.numCtrls )
            # Bring up all switches
            main.log.debug( main.Cluster.next().summary() )
            main.step( "Starting switches - iteration " + str( i ) )
            switchStart = main.TRUE
            for switch in switchList:
                switchStart = switchStart and main.Network.switch( SW=switch, OPTION="start" )
            utilities.assert_equals( expect=main.TRUE, actual=switchStart,
                                     onpass="All switches started",
                                     onfail="Failed to start all switches" )

            main.Network.discoverHosts( hostList=main.internalIpv4Hosts + main.internalIpv6Hosts )
            lib.verifyTopology( main, totalSwitches, totalLinks, main.Cluster.numCtrls )
            main.log.debug( main.Cluster.next().summary() )
            time.sleep( 60 )
            main.log.debug( main.Cluster.next().summary() )
            time.sleep( 60 )
            main.log.debug( main.Cluster.next().summary() )
            verifyPing( main )
            verify( main, disconnected=False, external=False )
        verify( main, disconnected=False, external=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE602( self, main ):
        """"
        Take down a leaf switch that is paired and has a dual homed host
        Restore the leaf switch
        Repeat for various dual homed hosts and paired switches
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Drop a leaf switch that is paired and has a dual homed host." )
        setupTest( main, test_idx=602, onosNodes=3 )
        verify( main, disconnected=False )
        # We need to disable ports toward dual-homed hosts before killing the leaf switch
        portsToDisable = [ [ "of:0000000000000002", 7 ], [ "of:0000000000000002", 8 ],
                           [ "of:0000000000000002", 10 ], [ "of:0000000000000002", 11 ] ]
        lib.disablePortBatch( main, portsToDisable, 10, 48, 5 )
        # Kill leaf-2
        lib.killSwitch( main, "leaf2", 9, 38 )
        # FIXME: the downed interfaces on h4v6 and h5v6 won't disappear because they are
        # configured by netcfg
        hostLocations = { "h4v6": "of:0000000000000003/6",
                          "h5v6": [ "of:0000000000000002/8", "of:0000000000000003/7" ],
                          "h4v4": "of:0000000000000003/10",
                          "h5v4": "of:0000000000000003/11" }
        lib.verifyHostLocations( main, hostLocations )
        main.disconnectedIpv4Hosts = [ "h3v4" ]
        main.disconnectedIpv6Hosts = [ "h3v6" ]
        verify( main )
        # Recover leaf-2
        lib.recoverSwitch( main, "leaf2", 10, 48, rediscoverHosts=True )
        hostLocations = { "h4v6": [ "of:0000000000000002/7", "of:0000000000000003/6" ],
                          "h5v6": [ "of:0000000000000002/8", "of:0000000000000003/7" ],
                          "h4v4": [ "of:0000000000000002/10", "of:0000000000000003/10" ],
                          "h5v4": [ "of:0000000000000002/11", "of:0000000000000003/11" ] }
        lib.verifyHostLocations( main, hostLocations )
        main.disconnectedIpv4Hosts = []
        main.disconnectedIpv6Hosts = []
        verify( main, disconnected=False )
        # We need to disable ports toward dual-homed hosts before killing the leaf switch
        portsToDisable = [ [ "of:0000000000000004", 7 ], [ "of:0000000000000004", 8 ],
                           [ "of:0000000000000004", 10 ], [ "of:0000000000000004", 11 ] ]
        lib.disablePortBatch( main, portsToDisable, 10, 48, 5 )
        # Kill leaf-4
        lib.killSwitch( main, "leaf4", 9, 38 )
        hostLocations = { "h9v6": [ "of:0000000000000004/7", "of:0000000000000005/6" ],
                          "h10v6": [ "of:0000000000000004/8", "of:0000000000000005/7" ],
                          "h9v4": "of:0000000000000005/9",
                          "h10v4": "of:0000000000000005/10" }
        lib.verifyHostLocations( main, hostLocations )
        main.disconnectedIpv4Hosts = [ "h8v4" ]
        main.disconnectedIpv6Hosts = [ "h8v6" ]
        verify( main )
        # Recover leaf-4
        lib.recoverSwitch( main, "leaf4", 10, 48, rediscoverHosts=True )
        hostLocations = { "h9v6": [ "of:0000000000000004/7", "of:0000000000000005/6" ],
                          "h10v6": [ "of:0000000000000004/8", "of:0000000000000005/7" ],
                          "h9v4": [ "of:0000000000000004/10", "of:0000000000000005/9" ],
                          "h10v4": [ "of:0000000000000004/11", "of:0000000000000005/10" ] }
        lib.verifyHostLocations( main, hostLocations )
        main.disconnectedIpv4Hosts = []
        main.disconnectedIpv6Hosts = []
        verify( main, disconnected=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE603( self, main ):
        """"
        Drop HAGG-1 device and test connectivity.
        Drop DAAS-1 device and test connectivity (some hosts lost it)
        Bring up DAAS-1 and test connectivity (all hosts gained it again)

        Repeat the same with HAGG-2 and DAAS-2.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Drop hagg spine switch along with dass leaf switch." )
        setupTest( main, test_idx=603, onosNodes=3 )
        main.disconnectedIpv4Hosts = []
        main.disconnectedIpv6Hosts = []

        verify( main )
        lib.killSwitch( main, "spine103",
                        int( main.params[ "TOPO" ]["switchNum" ] ) - 1,
                        int( main.params[ "TOPO" ][ "linkNum" ] ) - 6 )
        verify( main )
        lib.killSwitch( main, "leaf6",
                        int( main.params[ "TOPO" ]["switchNum" ] ) - 2,
                        int( main.params[ "TOPO" ][ "linkNum" ] ) - 8 )
        main.disconnectedIpv4Hosts = [ 'h12v4', 'h13v4']
        main.disconnectedIpv6Hosts = [ 'h12v6', 'h13v6']
        verify( main )
        lib.recoverSwitch( main, "leaf6",
                           int( main.params[ "TOPO" ]["switchNum" ] ) - 1,
                           int( main.params[ "TOPO" ][ "linkNum" ] ) - 6,
                           rediscoverHosts=True)
        main.disconnectedIpv4Hosts = []
        main.disconnectedIpv6Hosts = []
        verify( main )
        lib.recoverSwitch( main, "spine103",
                           int( main.params[ "TOPO" ][ "switchNum" ] ),
                           int( main.params[ "TOPO" ][ "linkNum" ] ) )
        verify( main )

        lib.killSwitch( main, "spine104",
                        int( main.params[ "TOPO" ]["switchNum" ] ) - 1,
                        int( main.params[ "TOPO" ][ "linkNum" ] ) - 6 )
        verify( main )
        lib.killSwitch( main, "leaf1",
                        int( main.params[ "TOPO" ]["switchNum" ] ) - 2,
                        int( main.params[ "TOPO" ][ "linkNum" ] ) - 8 )
        main.disconnectedIpv4Hosts = [ 'h1v4', 'h2v4']
        main.disconnectedIpv6Hosts = [ 'h1v6', 'h2v6']
        verify( main )
        lib.recoverSwitch( main, "leaf1",
                           int( main.params[ "TOPO" ]["switchNum" ] ) - 1,
                           int( main.params[ "TOPO" ][ "linkNum" ] ) - 6,
                           rediscoverHosts=True )
        main.disconnectedIpv4Hosts = []
        main.disconnectedIpv6Hosts = []
        verify( main )
        lib.recoverSwitch( main, "spine104",
                           int( main.params[ "TOPO" ][ "switchNum" ] ),
                           int( main.params[ "TOPO" ][ "linkNum" ] ) )
        verify( main )

        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE604( self, main ):
        """"
        Drop HAGG-1 device and test connectivity.
        Bring up HAGG-1 and test connectivity.
        Drop HAGG-2 device and test connectivity.
        Bring up HAGG-2 device and test connectivity
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Drop hagg spine switches." )
        setupTest( main, test_idx=604, onosNodes=3 )
        main.disconnectedIpv4Hosts = []
        main.disconnectedIpv6Hosts = []
        verify( main )
        lib.killSwitch( main, "spine103",
                        int( main.params[ "TOPO" ]["switchNum" ] ) - 1,
                        int( main.params[ "TOPO" ][ "linkNum" ] ) - 6 )
        verify( main )
        lib.recoverSwitch( main, "spine103",
                           int( main.params[ "TOPO" ][ "switchNum" ] ),
                           int( main.params[ "TOPO" ][ "linkNum" ] ) )
        verify( main )
        lib.killSwitch( main, "spine104",
                        int( main.params[ "TOPO" ]["switchNum" ] ) - 1,
                        int( main.params[ "TOPO" ][ "linkNum" ] ) - 6 )
        verify( main )
        lib.recoverSwitch( main, "spine104",
                           int( main.params[ "TOPO" ][ "switchNum" ] ),
                           int( main.params[ "TOPO" ][ "linkNum" ] ) )
        verify( main )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE605( self, main ):
        """
        Drop HAGG-1 and test connectivity (expect no failure)
        Drop all leafs in big fabric and test connectivity (expect some failures)
        Bring up HAGG-1 and test connectivity (still expect some failures)
        Bring up all leafs in big fabric and test connectivity (expect no failure)
        Repeat above with HAGG-2
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Drop one hagg and all leafs in big fabric" )
        setupTest( main, test_idx=605, onosNodes=3 )
        main.disconnectedIpv4Hosts = []
        main.disconnectedIpv6Hosts = []
        verify( main )
        lib.killSwitch( main, "spine103",
                        int( main.params[ "TOPO" ][ "switchNum" ] ) - 1,
                        int( main.params[ "TOPO" ][ "linkNum" ] ) - 6 )
        verify( main )
        lib.killSwitch( main, [ "leaf2", "leaf3", "leaf4", "leaf5" ],
                        int( main.params[ "TOPO" ][ "switchNum" ] ) - 5,
                        int( main.params[ "TOPO" ][ "linkNum" ] ) - 42 )
        main.disconnectedIpv4Hosts = [ "h3v4", "h4v4", "h5v4", "h6v4", "h7v4", "h8v4", "h9v4", "h10v4", "h11v4" ]
        main.disconnectedIpv6Hosts = [ "h3v6", "h4v6", "h5v6", "h6v6", "h7v6", "h8v6", "h9v6", "h10v6", "h11v6" ]
        main.disconnectedExternalIpv4Hosts = [ "rh1v4", "rh2v4", "rh5v4" ]
        main.disconnectedExternalIpv6Hosts = [ "rh1v6", "rh11v6", "rh5v6", "rh2v6", "rh22v6" ]
        verify( main, disconnected=True )
        lib.recoverSwitch( main, "spine103",
                           int( main.params[ "TOPO" ][ "switchNum" ] ) - 4,
                           int( main.params[ "TOPO" ][ "linkNum" ] ) - 36 )
        verify( main, disconnected=True )
        lib.recoverSwitch( main, [ "leaf2", "leaf3", "leaf4", "leaf5" ],
                           int( main.params[ "TOPO" ][ "switchNum" ] ),
                           int( main.params[ "TOPO" ][ "linkNum" ] ) )
        main.disconnectedIpv4Hosts = []
        main.disconnectedIpv6Hosts = []
        main.disconnectedExternalIpv4Hosts = [ ]
        main.disconnectedExternalIpv6Hosts = [ ]
        verify( main )

        lib.killSwitch( main, "spine104",
                        int( main.params[ "TOPO" ][ "switchNum" ] ) - 1,
                        int( main.params[ "TOPO" ][ "linkNum" ] ) - 6 )
        verify( main )
        lib.killSwitch( main, [ "leaf2", "leaf3", "leaf4", "leaf5" ],
                        int( main.params[ "TOPO" ][ "switchNum" ] ) - 5,
                        int( main.params[ "TOPO" ][ "linkNum" ] ) - 42 )
        main.disconnectedIpv4Hosts = [ "h3v4", "h4v4", "h5v4", "h6v4", "h7v4", "h8v4", "h9v4", "h10v4", "h11v4" ]
        main.disconnectedIpv6Hosts = [ "h3v6", "h4v6", "h5v6", "h6v6", "h7v6", "h8v6", "h9v6", "h10v6", "h11v6" ]
        main.disconnectedExternalIpv4Hosts = [ "rh1v4", "rh2v4", "rh5v4" ]
        main.disconnectedExternalIpv6Hosts = [ "rh1v6", "rh11v6", "rh5v6", "rh2v6", "rh22v6" ]
        verify( main, disconnected=True )
        lib.recoverSwitch( main, "spine104",
                           int( main.params[ "TOPO" ][ "switchNum" ] ) - 4,
                           int( main.params[ "TOPO" ][ "linkNum" ] ) - 36 )
        verify( main, disconnected=True )
        lib.recoverSwitch( main, [ "leaf2", "leaf3", "leaf4", "leaf5" ],
                           int( main.params[ "TOPO" ][ "switchNum" ] ),
                           int( main.params[ "TOPO" ][ "linkNum" ] ) )
        main.disconnectedIpv4Hosts = []
        main.disconnectedIpv6Hosts = []
        main.disconnectedExternalIpv4Hosts = [ ]
        main.disconnectedExternalIpv6Hosts = [ ]
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
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Drop spine and paired leaf" )
        setupTest( main, test_idx=606, onosNodes=3 )
        verify( main, disconnected=False )
        # Drop spine101 and leaf-2/3
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
        lib.recoverSwitch( main, "leaf2", 10, 48, rediscoverHosts=True,
                           hostsToDiscover=main.disconnectedIpv4Hosts + main.disconnectedIpv6Hosts )
        main.disconnectedIpv4Hosts = []
        main.disconnectedIpv6Hosts = []
        verify( main, disconnected=False )
        # Drop spine102 and leaf-4/5
        lib.killSwitch( main, "spine102", 9, 30 )
        verify( main, disconnected=False )
        lib.killSwitch( main, "leaf4", 8, 24 )
        lib.killSwitch( main, "leaf5", 7, 20 )
        main.disconnectedIpv4Hosts = [ "h8v4", "h9v4", "h10v4", "h11v4" ]
        main.disconnectedIpv6Hosts = [ "h8v6", "h9v6", "h10v6", "h11v6" ]
        verify( main, external=False )
        lib.recoverSwitch( main, "spine102", 8, 30 )
        verify( main, external=False )
        lib.recoverSwitch( main, "leaf5", 9, 38 )
        lib.recoverSwitch( main, "leaf4", 10, 48, rediscoverHosts=True,
                           hostsToDiscover=main.disconnectedIpv4Hosts + main.disconnectedIpv6Hosts )
        main.disconnectedIpv4Hosts = []
        main.disconnectedIpv6Hosts = []
        verify( main, disconnected=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE620( self, main ):
        """
        Take down one of double links towards the spine from all leaf switches and
        check that buckets in select groups change accordingly
        Bring up links again and check that buckets in select groups change accordingly
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Take down one of double links towards the spine" )
        setupTest( main, test_idx=620, onosNodes=3 )
        verify( main, disconnected=False )
        groupBuckets = { "of:0000000000000002": { "10.1.0.0/24": 4, "10.1.10.0/24": 4,
                                                  "10.2.0.0/24": 1, "10.2.30.0/24": 1, "10.2.20.0/24": 1,
                                                  "10.2.10.0/24": 4, "10.2.40.0/24": 4,
                                                  "10.3.0.0/24": 4, "10.3.10.0/24": 8, "10.3.30.0/24": 8,
                                                  "10.3.20.0/24": 4, "10.5.10.0/24": 4, "10.5.20.0/24": 4 },
                         "of:0000000000000003": { "10.1.0.0/24": 4, "10.1.10.0/24": 4,
                                                  "10.2.0.0/24": 4, "10.2.30.0/24": 1, "10.2.20.0/24": 1,
                                                  "10.2.10.0/24": 1, "10.2.40.0/24": 1,
                                                  "10.3.0.0/24": 4, "10.3.10.0/24": 8, "10.3.30.0/24": 8,
                                                  "10.3.20.0/24": 4, "10.5.10.0/24": 4, "10.5.20.0/24": 4 },
                         "of:0000000000000004": { "10.1.0.0/24": 4, "10.1.10.0/24": 4,
                                                  "10.2.0.0/24": 4, "10.2.30.0/24": 8, "10.2.20.0/24": 8,
                                                  "10.2.10.0/24": 4, "10.2.40.0/24": 4,
                                                  "10.3.0.0/24": 1, "10.3.10.0/24": 1, "10.3.30.0/24": 1,
                                                  "10.3.20.0/24": 4, "10.5.10.0/24": 4, "10.5.20.0/24": 4 },
                         "of:0000000000000005": { "10.1.0.0/24": 4, "10.1.10.0/24": 4,
                                                  "10.2.0.0/24": 4, "10.2.30.0/24": 8, "10.2.20.0/24": 8,
                                                  "10.2.10.0/24": 4, "10.2.40.0/24": 4,
                                                  "10.3.0.0/24": 4, "10.3.10.0/24": 1, "10.3.30.0/24": 1,
                                                  "10.3.20.0/24": 1, "10.5.10.0/24": 4, "10.5.20.0/24": 4 } }
        for switch, subnets in groupBuckets.items():
            lib.checkGroupsForBuckets( main, switch, subnets )
        # Take down one of double links
        portsToDisable = [ [ "of:0000000000000002", 1 ], [ "of:0000000000000002", 3 ],
                           [ "of:0000000000000003", 1 ], [ "of:0000000000000003", 3 ],
                           [ "of:0000000000000004", 1 ], [ "of:0000000000000004", 3 ],
                           [ "of:0000000000000005", 1 ], [ "of:0000000000000005", 3 ] ]
        lib.disablePortBatch( main, portsToDisable, 10, 32 )
        groupBucketsNew = { "of:0000000000000002": { "10.1.0.0/24": 2, "10.1.10.0/24": 2,
                                                     "10.2.0.0/24": 1, "10.2.30.0/24": 1, "10.2.20.0/24": 1,
                                                     "10.2.10.0/24": 2, "10.2.40.0/24": 2,
                                                     "10.3.0.0/24": 2, "10.3.10.0/24": 4, "10.3.30.0/24": 4,
                                                     "10.3.20.0/24": 2, "10.5.10.0/24": 2, "10.5.20.0/24": 2 },
                            "of:0000000000000003": { "10.1.0.0/24": 2, "10.1.10.0/24": 2,
                                                     "10.2.0.0/24": 2, "10.2.30.0/24": 1, "10.2.20.0/24": 1,
                                                     "10.2.10.0/24": 1, "10.2.40.0/24": 1,
                                                     "10.3.0.0/24": 2, "10.3.10.0/24": 4, "10.3.30.0/24": 4,
                                                     "10.3.20.0/24": 2, "10.5.10.0/24": 2, "10.5.20.0/24": 2 },
                            "of:0000000000000004": { "10.1.0.0/24": 2, "10.1.10.0/24": 2,
                                                     "10.2.0.0/24": 2, "10.2.30.0/24": 4, "10.2.20.0/24": 4,
                                                     "10.2.10.0/24": 2, "10.2.40.0/24": 2,
                                                     "10.3.0.0/24": 1, "10.3.10.0/24": 1, "10.3.30.0/24": 1,
                                                     "10.3.20.0/24": 2, "10.5.10.0/24": 2, "10.5.20.0/24": 2 },
                            "of:0000000000000005": { "10.1.0.0/24": 2, "10.1.10.0/24": 2,
                                                     "10.2.0.0/24": 2, "10.2.30.0/24": 4, "10.2.20.0/24": 4,
                                                     "10.2.10.0/24": 2, "10.2.40.0/24": 2,
                                                     "10.3.0.0/24": 2, "10.3.10.0/24": 1, "10.3.30.0/24": 1,
                                                     "10.3.20.0/24": 1, "10.5.10.0/24": 2, "10.5.20.0/24": 2 } }
        for switch, subnets in groupBucketsNew.items():
            lib.checkGroupsForBuckets( main, switch, subnets )
        verify( main, disconnected=False )
        # Bring up the links
        lib.enablePortBatch( main, portsToDisable, 10, 48 )
        for switch, subnets in groupBuckets.items():
            lib.checkGroupsForBuckets( main, switch, subnets )
        verify( main, disconnected=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE621( self, main ):
        """
        Remove all the links in the network and restore all Links (repeat x3)
        """
        import time
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Remove all the links in the network and restore all Links" )
        setupTest( main, test_idx=621, onosNodes=3 )
        verify( main, disconnected=False )
        linksToRemove = [ ["spine101", "spine103"], ["spine102", "spine104"],
                          ["spine103", "leaf6"], ["spine103", "leaf1"],
                          ["spine104", "leaf6"], ["spine104", "leaf1"],
                          ["spine101", "leaf2"], ["spine101", "leaf3"], ["spine101", "leaf4"], ["spine101", "leaf5"],
                          ["spine102", "leaf2"], ["spine102", "leaf3"], ["spine102", "leaf4"], ["spine102", "leaf5"],
                          ["leaf2", "leaf3"], ["leaf4", "leaf5"] ]
        portsToDisable = [ [ "of:0000000000000001", 3 ], [ "of:0000000000000001", 4 ],
                           [ "of:0000000000000001", 5 ], [ "of:0000000000000001", 6 ],
                           [ "of:0000000000000002", 6 ], [ "of:0000000000000002", 7 ],
                           [ "of:0000000000000002", 8 ], [ "of:0000000000000002", 9 ],
                           [ "of:0000000000000002", 10 ], [ "of:0000000000000002", 11 ],
                           [ "of:0000000000000003", 6 ], [ "of:0000000000000003", 7 ],
                           [ "of:0000000000000003", 8 ], [ "of:0000000000000003", 9 ],
                           [ "of:0000000000000003", 10 ], [ "of:0000000000000003", 11 ],
                           [ "of:0000000000000003", 12 ], [ "of:0000000000000003", 13 ],
                           [ "of:0000000000000004", 6 ], [ "of:0000000000000004", 7 ],
                           [ "of:0000000000000004", 8 ], [ "of:0000000000000004", 9 ],
                           [ "of:0000000000000004", 10 ], [ "of:0000000000000004", 11 ],
                           [ "of:0000000000000004", 12 ], [ "of:0000000000000004", 13 ], [ "of:0000000000000004", 14 ],
                           [ "of:0000000000000005", 6 ], [ "of:0000000000000005", 7 ],
                           [ "of:0000000000000005", 8 ], [ "of:0000000000000005", 9 ],
                           [ "of:0000000000000005", 10 ], [ "of:0000000000000005", 11 ],
                           [ "of:0000000000000005", 12 ], [ "of:0000000000000005", 13 ],
                           [ "of:0000000000000005", 14 ], [ "of:0000000000000005", 15 ],
                           [ "of:0000000000000006", 3 ], [ "of:0000000000000006", 4 ],
                           [ "of:0000000000000006", 5 ], [ "of:0000000000000006", 6 ] ]
        for i in range( 0, 3 ):
            lib.killLinkBatch( main, linksToRemove, 0, 10 )
            lib.disablePortBatch( main, portsToDisable, 10, 0 )
            main.disconnectedIpv4Hosts = main.internalIpv4Hosts
            main.disconnectedIpv6Hosts = main.internalIpv6Hosts
            verify( main )
            lib.restoreLinkBatch( main, linksToRemove, 48, 10 )
            lib.enablePortBatch( main, portsToDisable, 10, 48 )
            main.Network.discoverHosts( hostList=main.disconnectedIpv4Hosts + main.disconnectedIpv6Hosts )
            time.sleep( 10 )
            main.disconnectedIpv4Hosts = []
            main.disconnectedIpv6Hosts = []
            verify( main )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE622( self, main ):
        """
        Take down all uplinks from a paired leaf switch
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        from core import utilities
        main.case( "Take down all uplinks from a paired leaf switch" )
        setupTest( main, test_idx=622, onosNodes=3 )
        verify( main, disconnected=False )
        hostLocations = { "h4v6": [ "of:0000000000000002/7", "of:0000000000000003/6" ],
                          "h5v6": [ "of:0000000000000002/8", "of:0000000000000003/7" ],
                          "h4v4": [ "of:0000000000000002/10", "of:0000000000000003/10" ],
                          "h5v4": [ "of:0000000000000002/11", "of:0000000000000003/11" ] }
        lib.verifyHostLocations( main, hostLocations )
        linksToRemove = [ ["spine101", "leaf2"], ["spine102", "leaf2"] ]
        lib.killLinkBatch( main, linksToRemove, 40, 10 )
        # TODO: more verifications are required
        main.disconnectedIpv4Hosts = [ "h3v4" ]
        main.disconnectedIpv6Hosts = [ "h3v6" ]
        verify( main )
        hostLocations = { "h4v6": "of:0000000000000003/6",
                          "h5v6": [ "of:0000000000000002/8", "of:0000000000000003/7" ],
                          "h4v4": "of:0000000000000003/10",
                          "h5v4": "of:0000000000000003/11" }
        lib.verifyHostLocations( main, hostLocations )
        lib.restoreLinkBatch( main, linksToRemove, 48, 10 )
        main.disconnectedIpv4Hosts = []
        main.disconnectedIpv6Hosts = []
        verify( main, disconnected=False )
        hostLocations = { "h4v6": [ "of:0000000000000002/7", "of:0000000000000003/6" ],
                          "h5v6": [ "of:0000000000000002/8", "of:0000000000000003/7" ],
                          "h4v4": [ "of:0000000000000002/10", "of:0000000000000003/10" ],
                          "h5v4": [ "of:0000000000000002/11", "of:0000000000000003/11" ] }
        lib.verifyHostLocations( main, hostLocations )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE630( self, main ):
        """
        Bring an instance down
        Drop a device
        Bring that same instance up again and observe that this specific instance sees that the device is down.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        from core import utilities
        main.case( "Bring an instance down and drop a device" )
        setupTest( main, test_idx=630, onosNodes=3 )
        onosToKill = 0
        deviceToDrop = "spine101"
        lib.killOnos( main, [ onosToKill ], 10, 48, 2 )
        lib.killSwitch( main, deviceToDrop, 9, 30 )
        lib.recoverOnos( main, [ onosToKill ], 9, 30, 3 )
        result = main.Cluster.runningNodes[ onosToKill ].CLI.checkStatus( 9, 30, 3 )
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                 onpass="ONOS instance {} sees correct device numbers".format( onosToKill ),
                                 onfail="ONOS instance {} doesn't see correct device numbers".format( onosToKill ) )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE640( self, main ):
        """
        Controller instance going down and switch coming down at the same time and then we bring them up together

        A. Instance goes down and SPINE-1 goes down
            - All connectivity should be there
            - Bring them up together
            - All connectivity should be there
        B. Instance goes down and HAGG-1 goes down
            - All connectivity should be there
            - Bring them up together
            - All connectivity should be there
        C. Instance goes down and a paired leaf switch goes down
            - Single homed hosts in this leaf should lose connectivity all others should be ok
            - Bring them up together
            - Test connectivity
        """
        import time
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Drop an ONOS instance and switch(es) at the same time" )
        caseDict = { 'A': { 'switches': "spine101",
                            'ports': [],
                            'disconnectedV4': [],
                            'disconnectedV6': [],
                            'expectedSwitches': 9,
                            'expectedLinks': 30 },
                     'B': { 'switches': "spine103",
                            'ports': [],
                            'disconnectedV4': [],
                            'disconnectedV6': [],
                            'expectedSwitches': 9,
                            'expectedLinks': 42 },
                     'C': { 'switches': "leaf2",
                            'ports': [ [ "of:0000000000000002", 7 ], [ "of:0000000000000002", 8 ],
                                       [ "of:0000000000000002", 10 ], [ "of:0000000000000002", 11 ] ],
                            'disconnectedV4': [ "h3v4" ],
                            'disconnectedV6': [ "h3v6" ],
                            'expectedSwitches': 9,
                            'expectedLinks': 38 } }
        totalSwitches = int( main.params[ 'TOPO' ][ 'switchNum' ] )
        totalLinks = int( main.params[ 'TOPO' ][ 'linkNum' ] )
        nodeIndex = 0
        cases = sorted( caseDict.keys() )
        for case in cases:
            switches = caseDict[ case ][ 'switches' ]
            ports = caseDict[ case ][ 'ports' ]
            expectedSwitches = caseDict[ case ][ 'expectedSwitches' ]
            expectedLinks = caseDict[ case ][ 'expectedLinks' ]
            main.step( "\n640{}: Drop ONOS{} and switch(es) {} at the same time".format( case,
                                                                                         nodeIndex + 1,
                                                                                         switches ) )
            setupTest( main, test_idx=640 )
            main.Cluster.next().CLI.balanceMasters()
            time.sleep( float( main.params[ 'timers' ][ 'balanceMasterSleep' ] ) )
            main.Network.discoverHosts( hostList=main.internalIpv4Hosts + main.internalIpv6Hosts )
            instance = main.Cluster.controllers[ nodeIndex ]
            verify( main, disconnected=False, external=False )

            # Simultaneous failures
            main.step( "Kill ONOS{}: {}".format( nodeIndex + 1, instance.ipAddress ) )
            killResult = main.ONOSbench.onosDie( instance.ipAddress )
            utilities.assert_equals( expect=main.TRUE, actual=killResult,
                                     onpass="ONOS node killed",
                                     onfail="Failed to kill ONOS node" )
            instance.active = False
            main.Cluster.reset()
            if ports:
                lib.disablePortBatch( main, ports, 10, 48, 0 )
            # TODO: Remove sleeps from the concurrent events
            lib.killSwitch( main, switches, expectedSwitches, expectedLinks )
            main.disconnectedIpv4Hosts = caseDict[ case ][ 'disconnectedV4' ]
            main.disconnectedIpv6Hosts = caseDict[ case ][ 'disconnectedV6' ]

            # verify functionality
            main.log.debug( main.Cluster.next().summary() )
            main.Network.discoverHosts( hostList=main.internalIpv4Hosts + main.internalIpv6Hosts )
            main.log.debug( main.Cluster.next().summary() )
            lib.verifyTopology( main, expectedSwitches, expectedLinks, main.Cluster.numCtrls - 1  )
            lib.verifyNodes( main )
            verify( main, external=False )

            # Bring everything back up
            lib.recoverSwitch( main, switches, totalSwitches, totalLinks, rediscoverHosts=True )
            main.disconnectedIpv4Hosts = []
            main.disconnectedIpv6Hosts = []
            lib.recoverOnos( main, [ nodeIndex ], expectedSwitches, expectedLinks, main.Cluster.numCtrls )

            # Verify functionality
            lib.verifyNodes( main )
            verify( main, disconnected=False, external=False )
            lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )
            nodeIndex = ( nodeIndex + 1 ) % main.Cluster.numCtrls

    def CASE641( self, main ):
        """
        Controller instance going down while switch comes up at the same time

        A. Take down SPINE-1
            - Test connectivity
            - Bring up SPINE-1 and drop an instance at the same time
            - Test connectivity
            - Bring up instance one
            - Test connectivity
        B. Take down HAGG-1
            - Test connectivity
            - Bring up HAGG-1 and drop an instance at the same time
            - Test connectivity
            - Bring up instance one
            - Test connectivity
        C. Take down a paired leaf switch
            - Test connectivity ( single homed hosts on this leaf will lose it )
            - Bring up paired leaf switch and drop a controller instance at the same time
            - Test connectivity
            - Bring up the instance
            - Test connectivity
        """
        import time
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Drop an ONOS instance and recover switch(es) at the same time" )
        caseDict = { 'A': { 'switches': "spine101",
                            'ports': [],
                            'disconnectedV4': [],
                            'disconnectedV6': [],
                            'expectedSwitches': 9,
                            'expectedLinks': 30 },
                     'B': { 'switches': "spine103",
                            'ports': [],
                            'disconnectedV4': [],
                            'disconnectedV6': [],
                            'expectedSwitches': 9,
                            'expectedLinks': 42 },
                     'C': { 'switches': "leaf2",
                            'ports': [ [ "of:0000000000000002", 7 ], [ "of:0000000000000002", 8 ],
                                       [ "of:0000000000000002", 10 ], [ "of:0000000000000002", 11 ] ],
                            'disconnectedV4': [ "h3v4" ],
                            'disconnectedV6': [ "h3v6" ],
                            'expectedSwitches': 9,
                            'expectedLinks': 38 } }
        totalSwitches = int( main.params[ 'TOPO' ][ 'switchNum' ] )
        totalLinks = int( main.params[ 'TOPO' ][ 'linkNum' ] )
        nodeIndex = 0
        cases = sorted( caseDict.keys() )
        for case in cases:
            switches = caseDict[ case ][ 'switches' ]
            ports = caseDict[ case ][ 'ports' ]
            expectedSwitches = caseDict[ case ][ 'expectedSwitches' ]
            expectedLinks = caseDict[ case ][ 'expectedLinks' ]
            main.step( "\n641{}: Drop ONOS{} and recover switch(es) {} at the same time".format( case,
                                                                                                 nodeIndex + 1,
                                                                                                 switches ) )
            setupTest( main, test_idx=641 )
            main.Cluster.next().CLI.balanceMasters()
            time.sleep( float( main.params[ 'timers' ][ 'balanceMasterSleep' ] ) )
            main.Network.discoverHosts( hostList=main.internalIpv4Hosts + main.internalIpv6Hosts )
            instance = main.Cluster.controllers[ nodeIndex ]
            verify( main, disconnected=False, external=False )
            # Drop the switch to setup scenario
            if ports:
                lib.disablePortBatch( main, ports, 10, 48, 5 )
            lib.killSwitch( main, switches, expectedSwitches, expectedLinks )
            main.disconnectedIpv4Hosts = caseDict[ case ][ 'disconnectedV4' ]
            main.disconnectedIpv6Hosts = caseDict[ case ][ 'disconnectedV6' ]
            verify( main, external=False )

            # Simultaneous node failure and switch recovery
            main.step( "Kill ONOS{}: {}".format( nodeIndex + 1, instance.ipAddress ) )
            killResult = main.ONOSbench.onosDie( instance.ipAddress )
            utilities.assert_equals( expect=main.TRUE, actual=killResult,
                                     onpass="ONOS node killed",
                                     onfail="Failed to kill ONOS node" )
            instance.active = False
            main.Cluster.reset()
            # TODO: Remove sleeps from the concurrent events
            lib.recoverSwitch( main, switches, totalSwitches, totalLinks, rediscoverHosts=True )
            main.disconnectedIpv4Hosts = []
            main.disconnectedIpv6Hosts = []

            # verify functionality
            main.log.debug( main.Cluster.next().summary() )
            lib.verifyTopology( main, totalSwitches, totalLinks, main.Cluster.numCtrls - 1 )
            lib.verifyNodes( main )
            verify( main, disconnected=False, external=False )

            # Bring everything back up and verify functionality
            lib.recoverOnos( main, [ nodeIndex ], totalSwitches, totalLinks, main.Cluster.numCtrls )
            lib.verifyNodes( main )
            verify( main, external=False )
            lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )
            nodeIndex = ( nodeIndex + 1 ) % main.Cluster.numCtrls

    def CASE642( self, main ):
        """
        Drop one link from each double link
        Drop a link between DAAS-1 and HAAG-1
        Drop a link between HAGG-2 and SPINE-2
        Drop one ONOS instance
        Test connectivity (expect no failure)
        Bring up all links and ONOS instance
        Test connectivity (expect no failure)
        """
        import time
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Drop ONOS instance and links at the same time" )
        setupTest( main, test_idx=642, onosNodes=3 )
        main.Cluster.active( 0 ).CLI.balanceMasters()
        time.sleep( float( main.params[ 'timers' ][ 'balanceMasterSleep' ] ) )
        verify( main )
        portsToDisable = [ [ "of:0000000000000001", 1 ], [ "of:0000000000000103", 1 ],
                           [ "of:0000000000000006", 1 ], [ "of:0000000000000103", 2 ],
                           [ "of:0000000000000101", 9 ], [ "of:0000000000000103", 3 ],
                           [ "of:0000000000000002", 1 ], [ "of:0000000000000101", 1 ],
                           [ "of:0000000000000003", 1 ], [ "of:0000000000000101", 3 ],
                           [ "of:0000000000000004", 1 ], [ "of:0000000000000101", 5 ],
                           [ "of:0000000000000005", 1 ], [ "of:0000000000000101", 7 ],
                           [ "of:0000000000000002", 3 ], [ "of:0000000000000102", 1 ],
                           [ "of:0000000000000003", 3 ], [ "of:0000000000000102", 3 ],
                           [ "of:0000000000000004", 3 ], [ "of:0000000000000102", 5 ],
                           [ "of:0000000000000005", 3 ], [ "of:0000000000000102", 7 ] ]
        lib.disablePortBatch( main, portsToDisable,
                              int( main.params[ "TOPO" ][ "switchNum" ] ),
                              int( main.params[ "TOPO" ][ "linkNum" ] ) - len( portsToDisable ),
                              sleep=0 )
        lib.killOnos( main, [ 2, ], int( main.params[ "TOPO" ][ "switchNum" ] ),
                      int( main.params[ "TOPO" ][ "linkNum" ] ) - len( portsToDisable ), 2 )
        verify( main )
        lib.enablePortBatch( main, portsToDisable,
                             int( main.params[ "TOPO" ][ "switchNum" ] ),
                             int( main.params[ "TOPO" ][ "linkNum" ] ),
                             sleep=0 )
        lib.recoverOnos( main, [ 2, ], int( main.params[ "TOPO" ][ "switchNum" ] ),
                         int( main.params[ "TOPO" ][ "linkNum" ] ), 3 )
        verify( main )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE643( self, main ):
        """
        Drop one link from each double link
        Drop a link between DAAS-1 and HAAG-1
        Drop a link between HAGG-2 and SPINE-2
        Test connectivity (expect no failure)
        Bring up all links
        Drop one ONOS instance
        Test connectivity (expect no failure)
        Bring up ONOS instance
        Test connectivity (expect no failure)
        """
        import time
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Drop ONOS instances and bring up links at the same time" )
        setupTest( main, test_idx=643, onosNodes=3 )
        main.Cluster.active( 0 ).CLI.balanceMasters()
        time.sleep( float( main.params[ 'timers' ][ 'balanceMasterSleep' ] ) )
        verify( main )
        portsToDisable = [ [ "of:0000000000000001", 1 ], [ "of:0000000000000103", 1 ],
                           [ "of:0000000000000006", 1 ], [ "of:0000000000000103", 2 ],
                           [ "of:0000000000000101", 9 ], [ "of:0000000000000103", 3 ],
                           [ "of:0000000000000002", 1 ], [ "of:0000000000000101", 1 ],
                           [ "of:0000000000000003", 1 ], [ "of:0000000000000101", 3 ],
                           [ "of:0000000000000004", 1 ], [ "of:0000000000000101", 5 ],
                           [ "of:0000000000000005", 1 ], [ "of:0000000000000101", 7 ],
                           [ "of:0000000000000002", 3 ], [ "of:0000000000000102", 1 ],
                           [ "of:0000000000000003", 3 ], [ "of:0000000000000102", 3 ],
                           [ "of:0000000000000004", 3 ], [ "of:0000000000000102", 5 ],
                           [ "of:0000000000000005", 3 ], [ "of:0000000000000102", 7 ] ]
        lib.disablePortBatch( main, portsToDisable,
                              int( main.params[ "TOPO" ][ "switchNum" ] ),
                              int( main.params[ "TOPO" ][ "linkNum" ] ) - len( portsToDisable ) )
        verify( main )
        lib.enablePortBatch( main, portsToDisable,
                             int( main.params[ "TOPO" ][ "switchNum" ] ),
                             int( main.params[ "TOPO" ][ "linkNum" ] ) )
        lib.killOnos( main, [ 2, ], int( main.params[ "TOPO" ][ "switchNum" ] ),
                      int( main.params[ "TOPO" ][ "linkNum" ] ), 2 )
        verify( main )
        lib.recoverOnos( main, [ 2, ], int( main.params[ "TOPO" ][ "switchNum" ] ),
                         int( main.params[ "TOPO" ][ "linkNum" ] ), 3 )
        verify( main )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE651( self, main ):
        """
        Move a single-homed host from port A to port B in DAAS-1
        Test connectivity (expect no failure)

        Repeat with DAAS-2
        """
        import time
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Move a single-homed host to another port in the same DAAS" )
        setupTest( main, test_idx=651, onosNodes=3 )
        main.Cluster.active( 0 ).CLI.balanceMasters()
        time.sleep( float( main.params[ 'timers' ][ 'balanceMasterSleep' ] ) )
        verify( main )
        # Move an untagged IPv4 host on DAAS-1
        h1v4cfg = '{"of:0000000000000001/7" : { "interfaces" : [ { "ips" : [ "10.1.0.254/24" ], "vlan-untagged": 10 } ] } }'
        lib.moveHost( main, "h1v4", "leaf1", "leaf1", "10.1.0.254", prefixLen=24, cfg=h1v4cfg )
        hostLocations = { "h1v4": "of:0000000000000001/7" }
        lib.verifyHostLocations( main, hostLocations )
        verify( main )
        # Move an untagged IPv6 host on DAAS-1
        h1v6cfg = '{"of:0000000000000001/8" : { "interfaces" : [ { "ips" : [ "1000::3ff/120" ], "vlan-untagged": 21 } ] } }'
        lib.moveHost( main, "h1v6", "leaf1", "leaf1", "1000::3ff", prefixLen=128, cfg=h1v6cfg, ipv6=True )
        hostLocations = { "h1v6": "of:0000000000000001/8" }
        lib.verifyHostLocations( main, hostLocations )
        verify( main )
        # FIXME: We don't have any tagged hosts on DAAS-1

        # Move an untagged IPv4 host on DAAS-2
        h13v4cfg = '{"of:0000000000000006/7" : { "interfaces" : [ { "ips" : [ "10.5.20.254/24" ], "vlan-untagged": 20 } ] } }'
        lib.moveHost( main, "h13v4", "leaf6", "leaf6", "10.5.20.254", prefixLen=24, cfg=h13v4cfg )
        hostLocations = { "h13v4": "of:0000000000000006/7" }
        lib.verifyHostLocations( main, hostLocations )
        verify( main )
        # Move an untagged IPv6 host on DAAS-2
        h13v6cfg = '{"of:0000000000000006/8" : { "interfaces" : [ { "ips" : [ "1012::3ff/120" ], "vlan-untagged": 26 } ] } }'
        lib.moveHost( main, "h13v6", "leaf6", "leaf6", "1012::3ff", prefixLen=128, cfg=h13v6cfg, ipv6=True )
        hostLocations = { "h13v6": "of:0000000000000006/8" }
        lib.verifyHostLocations( main, hostLocations )
        verify( main )
        # Move a tagged IPv4 host on DAAS-2
        h12v4cfg = '{"of:0000000000000006/9" : { "interfaces" : [ { "ips" : [ "10.5.10.254/24" ], "vlan-tagged": [80] } ] } }'
        lib.moveHost( main, "h12v4", "leaf6", "leaf6", "10.5.10.254", prefixLen=24, cfg=h12v4cfg, vlan=80 )
        hostLocations = { "h12v4": "of:0000000000000006/9" }
        lib.verifyHostLocations( main, hostLocations )
        verify( main )
        # FIXME: Due to CORD-3079, we are not able to test movement of tagged IPv6 hosts at the moment
        '''
        h12v6cfg = '{"of:0000000000000006/10" : { "interfaces" : [ { "ips" : [ "1011::3ff/120" ], "vlan-tagged": [127] } ] } }'
        lib.moveHost( main, "h12v6", "leaf6", "leaf6", "1011::3ff", prefixLen=128, cfg=h12v6cfg, ipv6=True, vlan=127 )
        hostLocations = { "h12v6": "of:0000000000000006/10" }
        lib.verifyHostLocations( main, hostLocations )
        verify( main )
        '''

        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE652( self, main ):
        """
        Move a dual-homed host from porst 1A and 1B to ports 2A and 2B
        Host retains the same MAC and IP address
        Test connectivity (expect no failure)
        """
        import time
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Move a dual-homed host from porst 1A and 1B to ports 2A and 2B with the same MAC and IP" )
        setupTest( main, test_idx=652, onosNodes=3 )
        main.Cluster.active( 0 ).CLI.balanceMasters()
        time.sleep( float( main.params[ 'timers' ][ 'balanceMasterSleep' ] ) )
        verify( main )

        # Move an untagged IPv4 host
        lib.addStaticOnosRoute( main, "10.2.31.0/24", "10.2.30.1" )
        lib.startScapyHosts( main, scapyNames=[ 'h4v4Scapy' ], mininetNames=[ 'h4v4' ] )
        lib.verifyTraffic( main, main.internalIpv4Hosts, "10.2.31.1", "h4v4Scapy", "h4v4-bond0" )
        h4v4cfg = '''{"of:0000000000000002/12" : { "interfaces" : [ { "ips" : [ "10.2.30.254/24" ], "vlan-untagged": 16 } ] },
                      "of:0000000000000003/14" : { "interfaces" : [ { "ips" : [ "10.2.30.254/24" ], "vlan-untagged": 16 } ] } }'''
        lib.moveDualHomedHost( main, "h4v4", "leaf2", "leaf3", "leaf2", "leaf3", "10.2.30.254", prefixLen=24, cfg=h4v4cfg )
        hostLocations = { "h4v4": [ "of:0000000000000002/12", "of:0000000000000003/14" ] }
        lib.verifyHostLocations( main, hostLocations )
        verify( main )
        lib.verifyTraffic( main, main.internalIpv4Hosts, "10.2.31.1", "h4v4Scapy", "h4v4-bond1" )

        # Move an untagged IPv6 host
        lib.addStaticOnosRoute( main, "1003::400/120", "1003::3fe" )
        lib.startScapyHosts( main, scapyNames=[ 'h4v6Scapy' ], mininetNames=[ 'h4v6' ] )
        lib.verifyTraffic( main, main.internalIpv6Hosts, "1003::4fe", "h4v6Scapy", "h4v6-bond0", ipv6=True )
        h4v6cfg = '''{"of:0000000000000002/13" : { "interfaces" : [ { "ips" : [ "1003::3ff/120" ], "vlan-untagged": 24 } ] },
                      "of:0000000000000003/15" : { "interfaces" : [ { "ips" : [ "1003::3ff/120" ], "vlan-untagged": 24 } ] } }'''
        lib.moveDualHomedHost( main, "h4v6", "leaf2", "leaf3", "leaf2", "leaf3", "1003::3fe", prefixLen=128, cfg=h4v6cfg, ipv6=True )
        hostLocations = { "h4v6": [ "of:0000000000000002/13", "of:0000000000000003/15" ] }
        lib.verifyHostLocations( main, hostLocations )
        verify( main )
        lib.verifyTraffic( main, main.internalIpv6Hosts, "1003::4fe", "h4v6Scapy", "h4v6-bond1", ipv6=True )

        # Move a tagged IPv4 host
        lib.addStaticOnosRoute( main, "10.2.21.0/24", "10.2.20.1" )
        lib.startScapyHosts( main, scapyNames=[ 'h5v4Scapy' ], mininetNames=[ 'h5v4' ] )
        lib.verifyTraffic( main, main.internalIpv4Hosts, "10.2.21.1", "h5v4Scapy", "h5v4-bond0" )
        h5v4cfg = '''{"of:0000000000000002/14" : { "interfaces" : [ { "ips" : [ "10.2.20.254/24" ], "vlan-tagged": [30] } ] },
                      "of:0000000000000003/16" : { "interfaces" : [ { "ips" : [ "10.2.20.254/24" ], "vlan-tagged": [30] } ] } }'''
        lib.moveDualHomedHost( main, "h5v4", "leaf2", "leaf3", "leaf2", "leaf3", "10.2.20.254", prefixLen=24, cfg=h5v4cfg, vlan=30 )
        hostLocations = { "h5v4": [ "of:0000000000000002/14", "of:0000000000000003/16" ] }
        lib.verifyHostLocations( main, hostLocations )
        verify( main )
        lib.verifyTraffic( main, main.internalIpv4Hosts, "10.2.21.1", "h5v4Scapy", "h5v4-bond1" )

        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE653( self, main ):
        """
        Move a dual-homed host from porst 1A and 1B to ports 2A and 2B
        Host retains the same IP but MAC address changes
        Test connectivity (expect no failure)
        """
        import time
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Move a dual-homed host from porst 1A and 1B to ports 2A and 2B with the same IP and different MAC" )
        setupTest( main, test_idx=653, onosNodes=3 )
        main.Cluster.active( 0 ).CLI.balanceMasters()
        time.sleep( float( main.params[ 'timers' ][ 'balanceMasterSleep' ] ) )
        verify( main )

        # Move an untagged IPv4 host
        lib.addStaticOnosRoute( main, "10.2.31.0/24", "10.2.30.1" )
        lib.startScapyHosts( main, scapyNames=[ 'h4v4Scapy' ], mininetNames=[ 'h4v4' ] )
        lib.verifyTraffic( main, main.internalIpv4Hosts, "10.2.31.1", "h4v4Scapy", "h4v4-bond0" )
        h4v4cfg = '''{"of:0000000000000002/12" : { "interfaces" : [ { "ips" : [ "10.2.30.254/24" ], "vlan-untagged": 16 } ] },
                      "of:0000000000000003/14" : { "interfaces" : [ { "ips" : [ "10.2.30.254/24" ], "vlan-untagged": 16 } ] } }'''
        lib.moveDualHomedHost( main, "h4v4", "leaf2", "leaf3", "leaf2", "leaf3", "10.2.30.254", macAddr="00:aa:01:00:00:03", prefixLen=24, cfg=h4v4cfg )
        hostLocations = { "h4v4": [ "of:0000000000000002/12", "of:0000000000000003/14" ] }
        lib.verifyHostLocations( main, hostLocations )
        verify( main )
        lib.verifyTraffic( main, main.internalIpv4Hosts, "10.2.31.1", "h4v4Scapy", "h4v4-bond1" )

        # Move an untagged IPv6 host
        lib.addStaticOnosRoute( main, "1003::400/120", "1003::3fe" )
        lib.startScapyHosts( main, scapyNames=[ 'h4v6Scapy' ], mininetNames=[ 'h4v6' ] )
        lib.verifyTraffic( main, main.internalIpv6Hosts, "1003::4fe", "h4v6Scapy", "h4v6-bond0", ipv6=True )
        h4v6cfg = '''{"of:0000000000000002/13" : { "interfaces" : [ { "ips" : [ "1003::3ff/120" ], "vlan-untagged": 24 } ] },
                      "of:0000000000000003/15" : { "interfaces" : [ { "ips" : [ "1003::3ff/120" ], "vlan-untagged": 24 } ] } }'''
        lib.moveDualHomedHost( main, "h4v6", "leaf2", "leaf3", "leaf2", "leaf3", "1003::3fe", macAddr="00:bb:01:00:00:03", prefixLen=128, cfg=h4v6cfg, ipv6=True )
        hostLocations = { "h4v6": [ "of:0000000000000002/13", "of:0000000000000003/15" ] }
        lib.verifyHostLocations( main, hostLocations )
        verify( main )
        lib.verifyTraffic( main, main.internalIpv6Hosts, "1003::4fe", "h4v6Scapy", "h4v6-bond1", ipv6=True )

        # Move a tagged IPv4 host
        lib.addStaticOnosRoute( main, "10.2.21.0/24", "10.2.20.1" )
        lib.startScapyHosts( main, scapyNames=[ 'h5v4Scapy' ], mininetNames=[ 'h5v4' ] )
        lib.verifyTraffic( main, main.internalIpv4Hosts, "10.2.21.1", "h5v4Scapy", "h5v4-bond0" )
        h5v4cfg = '''{"of:0000000000000002/14" : { "interfaces" : [ { "ips" : [ "10.2.20.254/24" ], "vlan-tagged": [30] } ] },
                      "of:0000000000000003/16" : { "interfaces" : [ { "ips" : [ "10.2.20.254/24" ], "vlan-tagged": [30] } ] } }'''
        lib.moveDualHomedHost( main, "h5v4", "leaf2", "leaf3", "leaf2", "leaf3", "10.2.20.254", macAddr="00:aa:01:00:00:04", prefixLen=24, cfg=h5v4cfg, vlan=30 )
        hostLocations = { "h5v4": [ "of:0000000000000002/14", "of:0000000000000003/16" ] }
        lib.verifyHostLocations( main, hostLocations )
        verify( main )
        lib.verifyTraffic( main, main.internalIpv4Hosts, "10.2.21.1", "h5v4Scapy", "h5v4-bond1" )

        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE660( self, main ):
        """
        External router failure
        - Bring down quagga external router-1. Hosts that are behind router-2 should still be reachable. Hosts that are behind router-1 should not be reachable.
        - Bring router up again, all external hosts are reachable again.
        - Repeat this with external router-2.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "External router failure with cross-link" )
        setupTest( main, test_idx=660, onosNodes=3, static=True )
        main.externalIpv4Hosts += main.staticIpv4Hosts
        main.externalIpv6Hosts += main.staticIpv6Hosts
        verify( main, disconnected=False )
        # Bring down/up external router-1
        verifyRouterFailure( main, "r1", [ "rh5v4" ], [ "rh11v6", "rh5v6" ] )
        # Bring down/up external router-2
        verifyRouterFailure( main, "r2", [], [ "rh22v6" ] )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE661( self, main ):
        """
        External router link failure
        - Drop a non-cross-link for external router-1. All external hosts should be reachable (via cross-link).
        - Bring up the link. All external hosts should be reachable.
        - Repeat the steps above with the cross-link of external router-1
        - Repeat all steps above with external router-2
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "External router link failure with cross-link" )
        setupTest( main, test_idx=661, onosNodes=3, static=True )
        main.externalIpv4Hosts += main.staticIpv4Hosts
        main.externalIpv6Hosts += main.staticIpv6Hosts
        verify( main, disconnected=False )
        # Bring down/up a non-cross-link for external router-1
        portsToDisable = [ [ "of:0000000000000005", 13 ] ]
        lib.disablePortBatch( main, portsToDisable, 10, 48 )
        verify( main, disconnected=False, internal=False )
        lib.enablePortBatch( main, portsToDisable, 10, 48 )
        verify( main, disconnected=False, internal=False )
        # Bring down/up a cross-link for external router-1
        portsToDisable = [ [ "of:0000000000000005", 14 ] ]
        lib.disablePortBatch( main, portsToDisable, 10, 48 )
        verify( main, disconnected=False, internal=False )
        lib.enablePortBatch( main, portsToDisable, 10, 48 )
        verify( main, disconnected=False, internal=False )
        # Bring down/up a non-cross-link for external router-2
        portsToDisable = [ [ "of:0000000000000004", 14 ] ]
        lib.disablePortBatch( main, portsToDisable, 10, 48 )
        verify( main, disconnected=False, internal=False )
        lib.enablePortBatch( main, portsToDisable, 10, 48 )
        verify( main, disconnected=False, internal=False )
        # Bring down/up a cross-link for external router-2
        portsToDisable = [ [ "of:0000000000000004", 13 ] ]
        lib.disablePortBatch( main, portsToDisable, 10, 48 )
        verify( main, disconnected=False, internal=False )
        lib.enablePortBatch( main, portsToDisable, 10, 48 )
        verify( main, disconnected=False, internal=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE662( self, main ):
        """
        Internal router failure
        - Bring down quagga internal router-1. All external hosts should be reachable (via cross-link).
        - Bring the router up. All external hosts should be reachable.
        - Repeat this with internal router-2.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Internal router failure with cross-link" )
        setupTest( main, test_idx=662, onosNodes=3, static=True )
        main.externalIpv4Hosts += main.staticIpv4Hosts
        main.externalIpv6Hosts += main.staticIpv6Hosts
        verify( main, disconnected=False )
        # Bring down/up internal router-1
        verifyRouterFailure( main, "bgp1" )
        # Bring down/up internal router-2
        verifyRouterFailure( main, "bgp2" )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE663( self, main ):
        """
        External router failure without cross-link
        - Drop the cross-link for both external routers. All external hosts should be reachable.
        - Bring down quagga external router-1. Hosts that are behind router-2 should still be reachable. Hosts that are behind router-1 should not be reachable.
        - Bring router up again, all external hosts are reachable again.
        - Repeat this with external router-2.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "External router failure without cross-link" )
        setupTest( main, test_idx=663, onosNodes=3, static=True )
        main.externalIpv4Hosts += main.staticIpv4Hosts
        main.externalIpv6Hosts += main.staticIpv6Hosts
        verify( main, disconnected=False )
        # Drop the cross-link
        portsToDisable = [ [ "of:0000000000000004", 13 ], [ "of:0000000000000005", 14 ] ]
        lib.disablePortBatch( main, portsToDisable, 10, 48 )
        verify( main, disconnected=False, internal=False )
        # Bring down/up external router-1
        verifyRouterFailure( main, "r1", [ "rh5v4" ], [ "rh11v6", "rh5v6" ] )
        # Bring down/up external router-2
        verifyRouterFailure( main, "r2", [], [ "rh22v6" ] )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE664( self, main ):
        """
        External router link failure without cross-link
        - Drop the cross-link for both external routers. All external hosts should be reachable.
        - Drop an extra link for external router-1. Only hosts connected to router-2 should be reachable.
        - Bring up single link for external router-1. All external hosts should be reachable.
        - Repeat the two steps above with external router-2
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "External router link failure without cross-link" )
        setupTest( main, test_idx=664, onosNodes=3, static=True )
        main.externalIpv4Hosts += main.staticIpv4Hosts
        main.externalIpv6Hosts += main.staticIpv6Hosts
        verify( main, disconnected=False )
        # Drop the cross-link
        portsToDisable = [ [ "of:0000000000000004", 13 ], [ "of:0000000000000005", 14 ] ]
        lib.disablePortBatch( main, portsToDisable, 10, 48 )
        verify( main, disconnected=False, internal=False )
        # Bring down/up a non-cross-link for external router-1
        portsToDisable = [ [ "of:0000000000000005", 13 ] ]
        lib.disablePortBatch( main, portsToDisable, 10, 48 )
        main.disconnectedExternalIpv4Hosts = [ 'rh5v4' ]
        main.disconnectedExternalIpv6Hosts = [ "rh11v6", "rh5v6" ]
        verify( main, internal=False )
        lib.enablePortBatch( main, portsToDisable, 10, 48 )
        main.disconnectedExternalIpv4Hosts = []
        main.disconnectedExternalIpv6Hosts = []
        verify( main, disconnected=False, internal=False )
        # Bring down/up a non-cross-link for external router-2
        portsToDisable = [ [ "of:0000000000000004", 14 ] ]
        lib.disablePortBatch( main, portsToDisable, 10, 48 )
        main.disconnectedExternalIpv6Hosts = [ "rh22v6" ]
        verify( main, internal=False )
        lib.enablePortBatch( main, portsToDisable, 10, 48 )
        main.disconnectedExternalIpv6Hosts = []
        verify( main, disconnected=False, internal=False )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )

    def CASE665( self, main ):
        """
        Internal router failure without cross-link
        - Drop the cross-link for both external routers. All external hosts should be reachable.
        - Bring down quagga internal router-1. Hosts that are behind router-2 should still be reachable. Hosts that are behind router-1 should not be reachable.
        - Bring router up again, all external hosts are reachable again.
        - Repeat this with internal router-2.
        """
        from tests.USECASE.SegmentRouting.SRRouting.dependencies.SRRoutingTest import *
        from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
        main.case( "Internal router failure without cross-link" )
        setupTest( main, test_idx=665, onosNodes=3, static=True )
        main.externalIpv4Hosts += main.staticIpv4Hosts
        main.externalIpv6Hosts += main.staticIpv6Hosts
        verify( main, disconnected=False )
        # Drop the cross-link
        portsToDisable = [ [ "of:0000000000000004", 13 ], [ "of:0000000000000005", 14 ] ]
        lib.disablePortBatch( main, portsToDisable, 10, 48 )
        verify( main, disconnected=False, internal=False )
        # Bring down/up internal router-1
        verifyRouterFailure( main, "bgp1", [], [ "rh22v6" ] )
        # Bring down/up internal router-2
        verifyRouterFailure( main, "bgp2", [ "rh5v4" ], [ "rh11v6", "rh5v6" ] )
        lib.cleanup( main, copyKarafLog=False, removeHostComponent=True )
