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

def setupTest( main, test_idx, onosNodes=-1, ipv4=True, ipv6=True,
               external=True, static=False, countFlowsGroups=False ):
    """
    SRRouting test setup
    """
    from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
    import tests.USECASE.SegmentRouting.dependencies.cfgtranslator as translator
    import time

    try:
        skipPackage = False
        init = False
        if not hasattr( main, 'apps' ):
            init = True
            lib.initTest( main )
        if onosNodes < 0:
            onosNodes = main.Cluster.numCtrls
        # Skip onos packaging if the cluster size stays the same
        if not init and onosNodes == main.Cluster.numCtrls:
            skipPackage = True

        main.internalIpv4Hosts = main.params[ 'TOPO' ][ 'internalIpv4Hosts' ].split( ',' )
        main.internalIpv6Hosts = main.params[ 'TOPO' ][ 'internalIpv6Hosts' ].split( ',' ) if main.params[ 'TOPO' ].get( 'internalIpv6Hosts' ) else []
        main.externalIpv4Hosts = main.params[ 'TOPO' ][ 'externalIpv4Hosts' ].split( ',' ) if main.params[ 'TOPO' ].get('externalIpv4Hosts') else []
        main.externalIpv6Hosts = main.params[ 'TOPO' ][ 'externalIpv6Hosts' ].split( ',' ) if main.params[ 'TOPO' ].get('externalIpv6Hosts') else []
        main.staticIpv4Hosts = main.params[ 'TOPO' ][ 'staticIpv4Hosts' ].split( ',' ) if main.params[ 'TOPO' ].get('staticIpv4Hosts') else []
        main.staticIpv6Hosts = main.params[ 'TOPO' ][ 'staticIpv6Hosts' ].split( ',' ) if main.params[ 'TOPO' ].get('staticIpv6Hosts') else []
        main.disconnectedIpv4Hosts = []
        main.disconnectedIpv6Hosts = []
        main.disconnectedExternalIpv4Hosts = []
        main.disconnectedExternalIpv6Hosts = []
        main.disconnectedStaticIpv4Hosts = []
        main.disconnectedStaticIpv6Hosts = []
        main.resultFileName = 'CASE%03d' % test_idx
        main.Cluster.setRunningNode( onosNodes )

        lib.installOnos( main, skipPackage=skipPackage, cliSleep=5 )

        # Load configuration files
        if hasattr( main, "Mininet1" ):
            main.cfgName = 'TEST_CONFIG_ipv4={}_ipv6={}'.format( 1 if ipv4 else 0,
                                                                 1 if ipv6 else 0)
        else:
            main.cfgName = main.params[ "DEPENDENCY" ][ "confName" ]
        if not main.persistentSetup:
            if main.useBmv2:
                # Translate configuration file from OVS-OFDPA to BMv2 driver
                translator.bmv2ToOfdpa( main )  # Try to cleanup if switching between switch types
                switchPrefix = main.params[ 'DEPENDENCY' ].get( 'switchPrefix', '' )
                if switchPrefix is None:
                    switchPrefix = ''
                translator.ofdpaToBmv2( main, switchPrefix=switchPrefix )
            else:
                translator.bmv2ToOfdpa( main )
            lib.loadJson( main )
        main.log.debug( "sleeping %i seconds" % float( main.params[ 'timers' ][ 'loadNetcfgSleep' ] ) )
        time.sleep( float( main.params[ 'timers' ][ 'loadNetcfgSleep' ] ) )
        lib.loadHost( main )

        # if static route flag add routes
        # these routes are topology specific
        # these should be in the params file
        if static:
            if ipv4:
                lib.addStaticOnosRoute( main, "10.0.88.0/24", "10.0.1.1")
                lib.addStaticOnosRoute( main, "10.0.88.0/24", "10.0.5.1")
            if ipv6:
                lib.addStaticOnosRoute( main, "2000::8700/120", "2000::101")
                lib.addStaticOnosRoute( main, "2000::8700/120", "2000::501")
        if countFlowsGroups:
            lib.loadCount( main )

        if hasattr( main, 'Mininet1' ):
            lib.mnDockerSetup( main )
            # Run the test with Mininet
            mininet_args = ' --dhcp=1 --routers=1 --ipv6={} --ipv4={}'.format( 1 if ipv6 else 0,
                                                                               1 if ipv4 else 0 )
            if main.useBmv2:
                mininet_args += ' --switch %s' % main.switchType
                main.log.info( "Using %s switch" % main.switchType )
            lib.startMininet( main, main.params[ 'DEPENDENCY' ][ 'topology' ], args=mininet_args )
            main.log.debug( "Waiting %i seconds for ONOS to discover dataplane" % float( main.params[ "timers" ][ "startMininetSleep" ] ))
            time.sleep( float( main.params[ "timers" ][ "startMininetSleep" ] ) )
        else:
            # Run the test with physical devices
            lib.connectToPhysicalNetwork( main )

        # wait some time for onos to install the rules!
        main.log.info( "Waiting %i seconds for ONOS to program the dataplane" % float( main.params[ "timers" ][ "dhcpSleep" ] ))
        time.sleep( float( main.params[ 'timers' ][ 'dhcpSleep' ] ) )
    except Exception as e:
        main.log.exception( "Error in setupTest" )
        main.skipCase( result="FAIL", msg=e )

def verifyPingInternal( main, ipv4=True, ipv6=True, disconnected=True, skipOnFail=True, expect=True ):
    """
    Verify all connected internal hosts are able to reach each other,
    and disconnected internal hosts cannot reach any other internal host
    """
    from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
    # Verify connected hosts
    if ipv4:
        lib.verifyPing( main,
                        [ h for h in main.internalIpv4Hosts if h not in main.disconnectedIpv4Hosts ],
                        [ h for h in main.internalIpv4Hosts if h not in main.disconnectedIpv4Hosts ],
                        stepMsg="Verify reachability of connected internal IPv4 hosts", skipOnFail=skipOnFail, expect=expect )
    if ipv6:
        lib.verifyPing( main,
                        [ h for h in main.internalIpv6Hosts if h not in main.disconnectedIpv6Hosts ],
                        [ h for h in main.internalIpv6Hosts if h not in main.disconnectedIpv6Hosts ],
                        ipv6=True,
                        stepMsg="Verify reachability of connected internal IPv6 hosts", skipOnFail=skipOnFail, expect=expect )
    # Verify disconnected hosts
    if disconnected:
        if main.disconnectedIpv4Hosts:
            lib.verifyPing( main, main.internalIpv4Hosts, main.disconnectedIpv4Hosts, expect=False,
                            stepMsg="Verify unreachability of disconnected internal IPv4 hosts" )
        if main.disconnectedIpv6Hosts:
            lib.verifyPing( main, main.internalIpv6Hosts, main.disconnectedIpv6Hosts, ipv6=True, expect=False,
                            stepMsg="Verify unreachability of disconnected internal IPv6 hosts" )

def verifyPingExternal( main, ipv4=True, ipv6=True, disconnected=True, skipOnFail=True, expect=True ):
    """
    Verify all connected internal hosts are able to reach external hosts,
    and disconnected internal hosts cannot reach any external host
    """
    from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
    # Verify connected hosts
    if ipv4:
        lib.verifyPing( main,
                        [ h for h in main.internalIpv4Hosts if h not in main.disconnectedIpv4Hosts ],
                        [ h for h in main.externalIpv4Hosts if h not in main.disconnectedExternalIpv4Hosts ],
                        stepMsg="Verify reachability from connected internal IPv4 hosts to external IPv4 hosts",
                        t3Simple=False, skipOnFail=skipOnFail, expect=expect )
    if ipv6:
        lib.verifyPing( main,
                        [ h for h in main.internalIpv6Hosts if h not in main.disconnectedIpv6Hosts ],
                        [ h for h in main.externalIpv6Hosts if h not in main.disconnectedExternalIpv6Hosts ],
                        ipv6=True,
                        stepMsg="Verify reachability from connected internal IPv6 hosts to external IPv6 hosts",
                        t3Simple=False, skipOnFail=skipOnFail, expect=expect )
    # Verify disconnected hosts
    if disconnected:
        # Disconnected internal to connected external
        if main.disconnectedIpv4Hosts:
            lib.verifyPing( main, main.disconnectedIpv4Hosts,
                            [ h for h in main.externalIpv4Hosts if h not in main.disconnectedExternalIpv4Hosts ],
                            expect=False,
                            stepMsg="Verify unreachability of disconnected internal IPv4 hosts to connected external IPv4 hosts",
                            t3Simple=False )
        if main.disconnectedIpv6Hosts:
            lib.verifyPing( main, main.disconnectedIpv6Hosts,
                            [ h for h in main.externalIpv6Hosts if h not in main.disconnectedExternalIpv6Hosts ],
                            ipv6=True, expect=False,
                            stepMsg="Verify unreachability of disconnected internal IPv6 hosts to connected external IPv6 hosts",
                            t3Simple=False )
        # Connected internal to disconnected external
        if main.disconnectedExternalIpv4Hosts:
            lib.verifyPing( main,
                            [ h for h in main.internalIpv4Hosts if h not in main.disconnectedIpv4Hosts ],
                            main.disconnectedExternalIpv4Hosts,
                            expect=False,
                            stepMsg="Verify unreachability of connected internal IPv4 hosts to disconnected external IPv4 hosts",
                            t3Simple=False )
        if main.disconnectedExternalIpv6Hosts:
            lib.verifyPing( main,
                            [ h for h in main.internalIpv6Hosts if h not in main.disconnectedIpv6Hosts ],
                            main.disconnectedExternalIpv6Hosts,
                            ipv6=True, expect=False,
                            stepMsg="Verify unreachability of connected internal IPv6 hosts to disconnected external IPv6 hosts",
                            t3Simple=False )

def verifyPing( main, ipv4=True, ipv6=True, disconnected=False, internal=True, external=True, skipOnFail=True, expect=True ):
    """
    Verify reachability and unreachability of connected/disconnected hosts
    """
    if internal:
        verifyPingInternal( main, ipv4, ipv6, disconnected, skipOnFail, expect=expect )
    if external:
        verifyPingExternal( main, ipv4, ipv6, disconnected, skipOnFail, expect=expect )

def verifyLinkFailure( main, linksToRemove, expectedLinks, expectedSwitches, ipv4=True, ipv6=True, disconnected=False,
                       internal=True, external=True, countFlowsGroups=False, skipOnFail=True, expectedConnectivity=True ):
    """
    Kill all links sequencially and run verifications
    """
    from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
    #linksToRemove = [ ["leaf1", 260] ]
    if hasattr( main, "Mininet1" ):
        skipOnFail=True
        lib.killLinkBatch( main, linksToRemove, expectedLinks, expectedSwitches )
    else:
        skipOnFail=False
        for link in linksToRemove:
            main.Cluster.next().portstate( dpid="device:"+link[0], port=link[1], state="disable" )
    verifyPing( main, ipv4, ipv6, disconnected, internal, external, skipOnFail=skipOnFail, expect=expectedConnectivity )

def verifyLinksRestored( main, linksToRemove, expectedLinks, expectedSwitches, ipv4=True, ipv6=True, disconnected=False,
                         internal=True, external=True, countFlowsGroups=False, skipOnFail=True, topoSleep=30 ):
    """
    Recover all links sequencially and run verifications
    """
    from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
    import time
    if hasattr( main, "Mininet1"):
        lib.restoreLinkBatch( main, linksToRemove, expectedLinks, expectedSwitches )
    else:
        for link in linksToRemove:
            main.Cluster.next().portstate( dpid="device:"+link[0], port=link[1], state="enable" )
    time.sleep(topoSleep)
    lib.discoverHosts(main)
    verifyPing( main, ipv4, ipv6, disconnected, internal, external )

def verifySwitchFailure( main, ipv4=True, ipv6=True, disconnected=False,
                         internal=True, external=True, countFlowsGroups=False ):
    """
    Kill and recover spine101 and 102 sequencially and run verifications
    """
    from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
    for switchToKill in [ "spine101", "spine102" ]:
        lib.killSwitch( main, switchToKill, expectedLinks, expectedSwitches )
        verify( main, ipv4, ipv6, disconnected, internal, external, countFlowsGroups )
        lib.recoverSwitch( main, switchToKill, expectedLinks, expectedSwitches )
        verify( main, ipv4, ipv6, disconnected, internal, external, countFlowsGroups )

def verifyOnosFailure( main, ipv4=True, ipv6=True, disconnected=False,
                       internal=True, external=True, countFlowsGroups=False ):
    """
    Kill and recover onos nodes sequencially and run verifications
    """
    from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
    import json
    import time

    numCtrls = len( main.Cluster.runningNodes )
    links = len( json.loads( main.Cluster.next().links() ) )
    switches = len( json.loads( main.Cluster.next().devices() ) )
    mastershipSleep = float( main.params[ 'timers' ][ 'balanceMasterSleep' ] )
    for ctrl in xrange( numCtrls ):
        # Kill node
        lib.killOnos( main, [ ctrl ], switches, links, ( numCtrls - 1 ) )
        main.Cluster.active(0).CLI.balanceMasters()
        main.log.debug( "sleeping %i seconds" % mastershipSleep )
        time.sleep( mastershipSleep )
        verify( main, ipv4, ipv6, disconnected, internal, external, countFlowsGroups )
        # Recover node
        lib.recoverOnos( main, [ ctrl ], switches, links, numCtrls )
        main.Cluster.active(0).CLI.balanceMasters()
        main.log.debug( "sleeping %i seconds" % mastershipSleep )
        time.sleep( mastershipSleep )
        verify( main, ipv4, ipv6, disconnected, internal, external, countFlowsGroups )

def verify( main, ipv4=True, ipv6=True, disconnected=True, internal=True, external=True, countFlowsGroups=False ):
    """
    Verify host IP assignment, flow/group number and pings
    """
    from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib

    switches = int(main.params["TOPO"][ "switchNum" ])
    links = int( main.params["TOPO"][ "linkNum" ])
    lib.verifyTopology( main, switches, links, len( main.Cluster.runningNodes ) )
    # check flows / groups numbers
    if countFlowsGroups:
        lib.checkFlowsGroupsFromFile( main )
    # ping hosts
    verifyPing( main, ipv4, ipv6, disconnected, internal, external )
    # Verify host IP assignment
    lib.verifyOnosHostIp( main )
    lib.verifyNetworkHostIp( main )
    # ping hosts
    verifyPing( main, ipv4, ipv6, disconnected, internal, external )

def verifyRouterFailure( main, routerToKill, affectedIpv4Hosts=[], affectedIpv6Hosts=[],
                         ipv4=True, ipv6=True, countFlowsGroups=False ):
    """
    Kill and recover a quagga router and verify connectivities to external hosts
    """
    from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as lib
    lib.killRouter( main, routerToKill, 5 )
    main.disconnectedExternalIpv4Hosts = affectedIpv4Hosts
    main.disconnectedExternalIpv6Hosts = affectedIpv6Hosts
    verify( main, ipv4, ipv6, True if (affectedIpv4Hosts or affectedIpv6Hosts) else False, False, True, countFlowsGroups )
    lib.recoverRouter( main, routerToKill, 5 )
    main.disconnectedExternalIpv4Hosts = []
    main.disconnectedExternalIpv6Hosts = []
    verify( main, ipv4, ipv6, False, False, True, countFlowsGroups )
