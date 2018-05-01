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

def setupTest( main, test_idx, onosNodes, ipv4=True, ipv6=True, external=True, static=False, countFlowsGroups=False ):
    """
    SRRouting test setup
    """
    from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
    import time

    skipPackage = False
    init = False
    if not hasattr( main, 'apps' ):
        init = True
        lib.initTest( main )
    # Skip onos packaging if the cluster size stays the same
    if not init and onosNodes == main.Cluster.numCtrls:
        skipPackage = True

    main.internalIpv4Hosts = main.params[ 'TOPO' ][ 'internalIpv4Hosts' ].split( ',' )
    main.internalIpv6Hosts = main.params[ 'TOPO' ][ 'internalIpv6Hosts' ].split( ',' )
    main.externalIpv4Hosts = main.params[ 'TOPO' ][ 'externalIpv4Hosts' ].split( ',' )
    main.externalIpv6Hosts = main.params[ 'TOPO' ][ 'externalIpv6Hosts' ].split( ',' )
    main.disconnectedIpv4Hosts = []
    main.disconnectedIpv6Hosts = []
    main.resultFileName = 'CASE%03d' % test_idx
    main.Cluster.setRunningNode( onosNodes )

    lib.installOnos( main, skipPackage=skipPackage, cliSleep=5, parallel=False )

    # Load configuration files
    main.cfgName = 'TEST_CONFIG_ipv4={}_ipv6={}_dhcp=1_routers=1{}{}'.format( 1 if ipv4 else 0,
                                                                              1 if ipv6 else 0,
                                                                              "_external=1" if external else "",
                                                                              "_static=1" if static else "" )
    lib.loadJson( main )
    time.sleep( float( main.params[ 'timers' ][ 'loadNetcfgSleep' ] ) )
    lib.loadHost( main )

    # if static route flag add routes
    # these routes are topology specific
    if static:
        if ipv4:
            lib.addStaticOnosRoute( main, "10.0.88.0/24", "10.0.1.1")
        if ipv6:
            lib.addStaticOnosRoute( main, "2000::8700/120", "2000::101")
    if countFlowsGroups:
        lib.loadCount( main )

    if hasattr( main, 'Mininet1' ):
        # Run the test with Mininet
        mininet_args = ' --dhcp=1 --routers=1 --ipv6={} --ipv4={}'.format( 1 if ipv6 else 0,
                                                                           1 if ipv4 else 0 )
        lib.startMininet( main, main.params[ 'DEPENDENCY' ][ 'topology' ], args=mininet_args )
        time.sleep( float( main.params[ "timers" ][ "startMininetSleep" ] ) )
    else:
        # Run the test with physical devices
        lib.connectToPhysicalNetwork( main, self.switchNames )
        # Check if the devices are up
        lib.checkDevices( main, switches=len( self.switchNames ) )
    # wait some time for onos to install the rules!
    time.sleep( float( main.params[ 'timers' ][ 'dhcpSleep' ] ) )

def verifyPingInternal( main, ipv4=True, ipv6=True, disconnected=True ):
    """
    Verify all connected internal hosts are able to reach each other,
    and disconnected internal hosts cannot reach any other internal host
    """
    from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
    # Verify connected hosts
    main.step("Verify reachability of connected internal hosts")
    if ipv4:
        lib.verifyPing( main,
                        [ h for h in main.internalIpv4Hosts if h not in main.disconnectedIpv4Hosts ],
                        [ h for h in main.internalIpv4Hosts if h not in main.disconnectedIpv4Hosts ] )
    if ipv6:
        lib.verifyPing( main,
                        [ h for h in main.internalIpv6Hosts if h not in main.disconnectedIpv6Hosts ],
                        [ h for h in main.internalIpv6Hosts if h not in main.disconnectedIpv6Hosts ],
                        ipv6=True, acceptableFailed=7 )
    # Verify disconnected hosts
    if disconnected:
        main.step("Verify unreachability of disconnected internal hosts")
        if main.disconnectedIpv4Hosts:
            lib.verifyPing( main, main.internalIpv4Hosts, main.disconnectedIpv4Hosts, expect=False )
        if main.disconnectedIpv6Hosts:
            lib.verifyPing( main, main.internalIpv6Hosts, main.disconnectedIpv6Hosts, ipv6=True, expect=False )

def verifyPingExternal( main, ipv4=True, ipv6=True, disconnected=True ):
    """
    Verify all connected internal hosts are able to reach external hosts,
    and disconnected internal hosts cannot reach any external host
    """
    from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
    # Verify connected hosts
    main.step("Verify reachability of from connected internal hosts to external hosts")
    if ipv4:
        lib.verifyPing( main,
                        [ h for h in main.internalIpv4Hosts if h not in main.disconnectedIpv4Hosts ],
                        main.externalIpv4Hosts )
    if ipv6:
        lib.verifyPing( main,
                        [ h for h in main.internalIpv6Hosts if h not in main.disconnectedIpv6Hosts ],
                        main.externalIpv6Hosts,
                        ipv6=True, acceptableFailed=7 )
    # Verify disconnected hosts
    if disconnected:
        main.step("Verify unreachability of disconnected internal hosts to external hosts")
        if main.disconnectedIpv4Hosts:
            lib.verifyPing( main, main.disconnectedIpv4Hosts, main.externalIpv4Hosts, expect=False )
        if main.disconnectedIpv6Hosts:
            lib.verifyPing( main, main.disconnectedIpv6Hosts, main.externalIpv6Hosts, ipv6=True, expect=False )

def verifyPing( main, ipv4=True, ipv6=True, disconnected=False, internal=True, external=True ):
    """
    Verify reachability and unreachability of connected/disconnected hosts
    """
    if internal:
        verifyPingInternal( main, ipv4, ipv6, disconnected )
    if external:
        verifyPingExternal( main, ipv4, ipv6, disconnected )

def verifyLinkFailure( main, ipv4=True, ipv6=True, disconnected=False, internal=True, external=True, countFlowsGroups=False ):
    """
    Kill and recover all links to spine101 and 102 sequencially and run verifications
    """
    from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
    linksToRemove = [ ["spine103", "spine101"],
                      ["leaf2", "spine101"],
                      ["leaf3", "spine101"],
                      ["leaf4", "spine101"],
                      ["leaf5", "spine101"] ]
    lib.killLinkBatch( main, linksToRemove, 30, 10 )
    verify( main, ipv4, ipv6, disconnected, internal, external, countFlowsGroups )
    lib.restoreLinkBatch( main, linksToRemove, 48, 10 )
    verify( main, ipv4, ipv6, disconnected, internal, external, countFlowsGroups )
    linksToRemove = [ ["spine104", "spine102"],
                      ["leaf2", "spine102"],
                      ["leaf3", "spine102"],
                      ["leaf4", "spine102"],
                      ["leaf5", "spine102"] ]
    lib.killLinkBatch( main, linksToRemove, 30, 10 )
    verify( main, ipv4, ipv6, disconnected, internal, external, countFlowsGroups )
    lib.restoreLinkBatch( main, linksToRemove, 48, 10 )
    verify( main, ipv4, ipv6, disconnected, internal, external, countFlowsGroups )

def verifySwitchFailure( main, ipv4=True, ipv6=True, disconnected=False, internal=True, external=True, countFlowsGroups=False ):
    """
    Kill and recover spine101 and 102 sequencially and run verifications
    """
    from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
    for switchToKill in [ "spine101", "spine102" ]:
        lib.killSwitch( main, switchToKill, 9, 30 )
        verify( main, ipv4, ipv6, disconnected, internal, external, countFlowsGroups )
        lib.recoverSwitch( main, switchToKill, 10, 48 )
        verify( main, ipv4, ipv6, disconnected, internal, external, countFlowsGroups )

def verifyOnosFailure( main, ipv4=True, ipv6=True, disconnected=False, internal=True, external=True, countFlowsGroups=False ):
    """
    Kill and recover onos nodes sequencially and run verifications
    """
    from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
    import json
    import time

    numCtrls = len( main.Cluster.runningNodes )
    links = len( json.loads( main.Cluster.next().links() ) )
    switches = len( json.loads( main.Cluster.next().devices() ) )
    for ctrl in xrange( numCtrls ):
        # Kill node
        lib.killOnos( main, [ ctrl ], switches, links, ( numCtrls - 1 ) )
        main.Cluster.active(0).CLI.balanceMasters()
        time.sleep( float( main.params[ 'timers' ][ 'balanceMasterSleep' ] ) )
        verify( main, ipv4, ipv6, disconnected, internal, external, countFlowsGroups )
        # Recover node
        lib.recoverOnos( main, [ ctrl ], switches, links, numCtrls )
        main.Cluster.active(0).CLI.balanceMasters()
        time.sleep( float( main.params[ 'timers' ][ 'balanceMasterSleep' ] ) )
        verify( main, ipv4, ipv6, disconnected, internal, external, countFlowsGroups )

def verify( main, ipv4=True, ipv6=True, disconnected=True, internal=True, external=True, countFlowsGroups=False ):
    """
    Verify host IP assignment, flow/group number and pings
    """
    from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
    # Verify host IP assignment
    lib.verifyOnosHostIp( main )
    lib.verifyNetworkHostIp( main )
    # check flows / groups numbers
    if countFlowsGroups:
        run.checkFlowsGroupsFromFile( main )
    # ping hosts
    verifyPing( main, ipv4, ipv6, disconnected, internal, external )
