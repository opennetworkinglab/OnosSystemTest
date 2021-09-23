class SRpairedLeaves:
    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        Connect to Pod
        Check host dataplane connectivity
        Collect logs and analyze results
        """
        try:
            from tests.USECASE.SegmentRouting.SRStaging.dependencies.SRStagingTest import SRStagingTest
            from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as run
            import datetime
            import json
        except ImportError as e:
            main.log.exception( "SRStagingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRStagingTest()

        try:
            main.log.debug( "loading parser script" )
            import tests.USECASE.SegmentRouting.SRStaging.dependencies.log_breakdown as logParser
        except ImportError as e:
            main.log.exception( "Error running script" )
        descPrefix = "Host Connectivity"
        pod = main.params['GRAPH'].get( 'nodeCluster', "hardware" )
        main.cfgName = 'CASE001'
        main.funcs.setupTest( main,
                              topology='0x2',
                              onosNodes=3,
                              description="%s tests on the %s pod" % ( descPrefix, pod ) )
        switches = int( main.params[ 'TOPO' ][ 'switchNum' ] )
        links = int( main.params[ 'TOPO' ][ 'linkNum' ] )
        hosts = [ 'h1', 'h2', 'h3', 'mgmt' ]
        run.verifyTopology( main, switches, links, main.Cluster.numCtrls )
        run.verifyPing( main, hosts, hosts )
        main.funcs.cleanup( main )

    def CASE2( self, main ):
        """
        Connect to Pod
        Check host to gateway connectivity
        Collect logs and analyze results
        """
        try:
            from tests.USECASE.SegmentRouting.SRStaging.dependencies.SRStagingTest import SRStagingTest
            from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as run
            import json
        except ImportError:
            main.log.error( "SRStagingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRStagingTest()

        descPrefix = "Host to gateway connectivity"
        pod = main.params['GRAPH'].get( 'nodeCluster', "hardware" )
        main.funcs.setupTest( main,
                              topology='0x2',
                              onosNodes=3,
                              description="%s tests on the %s pod" % ( descPrefix, pod ) )
        hosts = [ 'h1', 'h2', 'h3', 'mgmt' ]
        run.pingAllFabricIntfs( main, hosts, dumpFlows=False )
        main.funcs.cleanup( main )

    def CASE101( self, main ):
        """
        Connect to Pod
        Create Flow between 2 dual homed hosts
        Kill link from leaf to src host used by flow
        Verify flow continues using other link
        Collect logs and analyze results
        """
        try:
            from tests.USECASE.SegmentRouting.SRStaging.dependencies.SRStagingTest import SRStagingTest
            import json
        except ImportError:
            main.log.error( "SRStagingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRStagingTest()

        descPrefix = "CASE101-Source-Link"
        pod = main.params['GRAPH'].get( 'nodeCluster', "hardware" )
        main.funcs.setupTest( main,
                              topology='0x2',
                              onosNodes=3,
                              description="%s tests on the %s pod" % ( descPrefix, pod ) )
        srcComponent = getattr( main, 'Compute1' )
        dstComponent = getattr( main, 'Compute2' )

        targets = main.funcs.getHostConnections( main, srcComponent )
        shortDesc = descPrefix + "-Failure"
        longDesc = "%s Failure: Bring down port with traffic from %s" % ( descPrefix, srcComponent.name )
        killDevice, killPort = main.funcs.linkDown( targets, srcComponent, dstComponent, shortDesc,
                                                    longDesc, stat='packetsReceived', bidirectional=False )
        # TODO: These should be "bidirectional" names
        shortDesc = descPrefix + "-Recovery"
        longDesc = "%s Recovery: Bring up %s/%s" % ( descPrefix, killDevice, killPort )
        main.funcs.linkUp( killDevice, killPort, srcComponent, dstComponent, shortDesc, longDesc,
                           bidirectional=False )
        # Cleanup
        main.log.warn( json.dumps( main.downtimeResults, indent=4, sort_keys=True ) )
        main.funcs.cleanup( main )

    def CASE102( self, main ):
        """
        Connect to Pod
        Create Flow between 2 dual homed hosts
        Kill link from leaf to dst host used by flow
        Verify flow continues using other link
        Collect logs and analyze results
        """
        try:
            from tests.USECASE.SegmentRouting.SRStaging.dependencies.SRStagingTest import SRStagingTest
            import json
        except ImportError:
            main.log.error( "SRStagingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRStagingTest()

        descPrefix = "CASE102-Destination-Link"
        pod = main.params['GRAPH'].get( 'nodeCluster', "hardware" )
        main.funcs.setupTest( main,
                              topology='0x2',
                              onosNodes=3,
                              description="%s tests on the %s pod" % ( descPrefix, pod ) )
        srcComponent = getattr( main, 'Compute2' )
        dstComponent = getattr( main, 'Compute1' )

        targets = main.funcs.getHostConnections( main, dstComponent )
        shortDesc = descPrefix + "-Failure"
        longDesc = "%s Failure: Bring down port with traffic to %s" % ( descPrefix, dstComponent.name )
        killDevice, killPort = main.funcs.linkDown( targets, srcComponent, dstComponent, shortDesc,
                                                    longDesc, stat='packetsSent', bidirectional=False )
        # TODO: These should be "bidirectional" names
        shortDesc = descPrefix + "-Recovery"
        longDesc = "%s Recovery: Bring up %s/%s" % ( descPrefix, killDevice, killPort )
        main.funcs.linkUp( killDevice, killPort, srcComponent, dstComponent, shortDesc, longDesc,
                           bidirectional=False )
        # Cleanup
        main.log.warn( json.dumps( main.downtimeResults, indent=4, sort_keys=True ) )
        main.funcs.cleanup( main )

    def CASE103( self, main ):
        """
        Connect to Pod
        Create Flow between 1 dual homed host and 1 single homed host
        Kill link from leaf to src host used by flow
        Verify flow continues using other link
        Collect logs and analyze results
        """
        try:
            from tests.USECASE.SegmentRouting.SRStaging.dependencies.SRStagingTest import SRStagingTest
            import json
        except ImportError:
            main.log.error( "SRStagingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRStagingTest()

        descPrefix = "CASE103-Source-Link"
        pod = main.params['GRAPH'].get( 'nodeCluster', "hardware" )
        main.funcs.setupTest( main,
                              topology='0x2',
                              onosNodes=3,
                              description="%s tests on the %s pod" % ( descPrefix, pod ) )
        srcComponent = getattr( main, 'Compute1' )
        dstComponent = getattr( main, 'Compute3' )

        targets = main.funcs.getHostConnections( main, srcComponent )
        shortDesc = descPrefix + "-Failure"
        longDesc = "%s Failure: Bring down port with traffic from %s" % ( descPrefix, srcComponent.name )
        killDevice, killPort = main.funcs.linkDown( targets, srcComponent, dstComponent, shortDesc,
                                                    longDesc, stat='packetsReceived', bidirectional=False )
        # TODO: These should be "bidirectional" names
        shortDesc = descPrefix + "-Recovery"
        longDesc = "%s Recovery: Bring up %s/%s" % ( descPrefix, killDevice, killPort )
        main.funcs.linkUp( killDevice, killPort, srcComponent, dstComponent, shortDesc, longDesc,
                bidirectional=False )
        # Cleanup
        main.log.warn( json.dumps( main.downtimeResults, indent=4, sort_keys=True ) )
        main.funcs.cleanup( main )

    def CASE104( self, main ):
        """
        Connect to Pod
        Create Flow between 1 dual homed host and 1 single homed host
        Kill link from leaf to dst host used by flow
        Verify flow continues using other link
        Collect logs and analyze results
        """
        try:
            from tests.USECASE.SegmentRouting.SRStaging.dependencies.SRStagingTest import SRStagingTest
            import json
        except ImportError:
            main.log.error( "SRStagingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRStagingTest()

        descPrefix = "CASE104-Destination-Link"
        pod = main.params['GRAPH'].get( 'nodeCluster', "hardware" )
        main.funcs.setupTest( main,
                              topology='0x2',
                              onosNodes=3,
                              description="%s tests on the %s pod" % ( descPrefix, pod ) )
        srcComponent = getattr( main, 'Compute3' )
        dstComponent = getattr( main, 'Compute1' )

        targets = main.funcs.getHostConnections( main, dstComponent )
        shortDesc = descPrefix + "-Failure"
        longDesc = "%s Failure: Bring down port with traffic to %s" % ( descPrefix, dstComponent.name )
        killDevice, killPort = main.funcs.linkDown( targets, srcComponent, dstComponent, shortDesc,
                                                    longDesc, stat='packetsSent', bidirectional=False )
        # TODO: These should be "bidirectional" names
        shortDesc = descPrefix + "-Recovery"
        longDesc = "%s Recovery: Bring up %s/%s" % ( descPrefix, killDevice, killPort )
        main.funcs.linkUp( killDevice, killPort, srcComponent, dstComponent, shortDesc, longDesc,
                bidirectional=False )
        # Cleanup
        main.log.warn( json.dumps( main.downtimeResults, indent=4, sort_keys=True ) )
        main.funcs.cleanup( main )

    def CASE201( self, main ):
        """
        Connect to Pod
        Create Flow between 2 dual homed hosts
        Kill the leaf that traffic first flows into
        Verify flow continues using other link
        Collect logs and analyze results
        """
        try:
            from tests.USECASE.SegmentRouting.SRStaging.dependencies.SRStagingTest import SRStagingTest
            import json
        except ImportError:
            main.log.error( "SRStagingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRStagingTest()

        descPrefix = "CASE201-Source-Leaf"
        pod = main.params['GRAPH'].get( 'nodeCluster', "hardware" )
        main.funcs.setupTest( main,
                              topology='0x2',
                              onosNodes=3,
                              description="%s tests on the %s pod" % ( descPrefix, pod ) )
        srcComponent = getattr( main, 'Compute1' )
        dstComponent = getattr( main, 'Compute2' )

        targets = main.funcs.getHostConnections( main, srcComponent )
        shortDescFailure = descPrefix + "-Failure"
        longDescFailure = "%s Failure: Bring down switch with traffic from %s" % ( descPrefix, srcComponent.name )
        shortDescRecovery = descPrefix + "-Recovery"
        longDescRecovery = "%s Recovery: Bring up switch previously killed" % descPrefix
        main.funcs.onlReboot( targets, srcComponent, dstComponent,
                              shortDescFailure, longDescFailure,
                              shortDescRecovery, longDescRecovery,
                              stat='packetsReceived', bidirectional=False )
        # Cleanup
        main.log.warn( json.dumps( main.downtimeResults, indent=4, sort_keys=True ) )
        main.funcs.cleanup( main )

    def CASE202( self, main ):
        """
        Connect to Pod
        Create Flow between 2 dual homed hosts
        Kill the last leaf that traffic flows out of
        Verify flow continues using other link
        Collect logs and analyze results
        """
        try:
            from tests.USECASE.SegmentRouting.SRStaging.dependencies.SRStagingTest import SRStagingTest
            import json
        except ImportError:
            main.log.error( "SRStagingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRStagingTest()

        descPrefix = "CASE202-Destination-Leaf"
        pod = main.params['GRAPH'].get( 'nodeCluster', "hardware" )
        main.funcs.setupTest( main,
                              topology='0x2',
                              onosNodes=3,
                              description="%s tests on the %s pod" % ( descPrefix, pod ) )
        srcComponent = getattr( main, 'Compute1' )
        dstComponent = getattr( main, 'Compute2' )

        targets = main.funcs.getHostConnections( main, dstComponent )
        shortDescFailure = descPrefix + "-Failure"
        longDescFailure = "%s Failure: Bring down switch with traffic from %s" % ( descPrefix, srcComponent.name )
        shortDescRecovery = descPrefix + "-Recovery"
        longDescRecovery = "%s Recovery: Bring up switch previously killed" % descPrefix
        main.funcs.onlReboot( targets, srcComponent, dstComponent,
                              shortDescFailure, longDescFailure,
                              shortDescRecovery, longDescRecovery,
                              stat='packetsSent', bidirectional=False )
        # Cleanup
        main.log.warn( json.dumps( main.downtimeResults, indent=4, sort_keys=True ) )
        main.funcs.cleanup( main )

    def CASE203( self, main ):
        """
        Connect to Pod
        Create Flow between 1 dual homed host and 1 single homed host
        Kill the leaf that traffic first flows into
        Verify flow continues using other link
        Collect logs and analyze results
        """
        try:
            from tests.USECASE.SegmentRouting.SRStaging.dependencies.SRStagingTest import SRStagingTest
            import json
        except ImportError:
            main.log.error( "SRStagingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRStagingTest()

        descPrefix = "CASE203-Source-Leaf"
        pod = main.params['GRAPH'].get( 'nodeCluster', "hardware" )
        main.funcs.setupTest( main,
                              topology='0x2',
                              onosNodes=3,
                              description="%s tests on the %s pod" % ( descPrefix, pod ) )
        srcComponentList = [ getattr( main, name ) for name in [ 'ManagmentServer', 'Compute1', 'Compute2' ] ]
        dstComponent = getattr( main, 'Compute3' )

        targets = main.funcs.getHostConnections( main, srcComponentList, excludedDIDs=[ 'leaf2' ] )
        shortDescFailure = descPrefix + "-Failure"
        longDescFailure = "%s Failure: Bring down switch with traffic to %s" % ( descPrefix, dstComponent.name )
        shortDescRecovery = descPrefix + "-Recovery"
        longDescRecovery = "%s Recovery: Bring up switch previously killed" % descPrefix
        main.funcs.onlReboot( targets, srcComponentList, dstComponent,
                              shortDescFailure, longDescFailure,
                              shortDescRecovery, longDescRecovery,
                              stat='packetsReceived', bidirectional=False,
                              singleFlow=True )
        # Cleanup
        main.log.warn( json.dumps( main.downtimeResults, indent=4, sort_keys=True ) )
        main.funcs.cleanup( main )

    def CASE204( self, main ):
        """
        Connect to Pod
        Create Flow between 1 dual homed host and 1 single homed host
        Kill the last leaf that traffic flows out of
        Verify flow continues using other link
        Collect logs and analyze results
        """
        try:
            from tests.USECASE.SegmentRouting.SRStaging.dependencies.SRStagingTest import SRStagingTest
            import json
        except ImportError:
            main.log.error( "SRStagingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRStagingTest()

        descPrefix = "CASE204-Destination-Leaf"
        pod = main.params['GRAPH'].get( 'nodeCluster', "hardware" )
        main.funcs.setupTest( main,
                              topology='0x2',
                              onosNodes=3,
                              description="%s tests on the %s pod" % ( descPrefix, pod ) )
        srcComponent = getattr( main, 'Compute3' )
        dstComponentList = [ getattr( main, name ) for name in [ 'ManagmentServer', 'Compute1', 'Compute2' ] ]

        targets = main.funcs.getHostConnections( main, dstComponentList, excludedDIDs=[ 'leaf2' ] )
        shortDescFailure = descPrefix + "-Failure"
        longDescFailure = "%s Failure: Bring down switch with traffic from %s" % ( descPrefix, srcComponent.name )
        shortDescRecovery = descPrefix + "-Recovery"
        longDescRecovery = "%s Recovery: Bring up switch previously killed" % descPrefix
        main.funcs.onlReboot( targets, srcComponent, dstComponentList,
                              shortDescFailure, longDescFailure,
                              shortDescRecovery, longDescRecovery,
                              stat='packetsSent', bidirectional=False,
                              singleFlow=True )
        # Cleanup
        main.log.warn( json.dumps( main.downtimeResults, indent=4, sort_keys=True ) )
        main.funcs.cleanup( main )

    def CASE205( self, main ):
        """
        Connect to Pod
        Create Flow between 2 dual homed hosts
        Kill the leaf that traffic first flows into
        Verify flow continues using other link
        Collect logs and analyze results
        """
        try:
            from tests.USECASE.SegmentRouting.SRStaging.dependencies.SRStagingTest import SRStagingTest
            import json
        except ImportError:
            main.log.error( "SRStagingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRStagingTest()

        descPrefix = "CASE205-Source-Leaf"
        pod = main.params['GRAPH'].get( 'nodeCluster', "hardware" )
        main.funcs.setupTest( main,
                              topology='0x2',
                              onosNodes=3,
                              description="%s tests on the %s pod" % ( descPrefix, pod ) )
        srcComponent = getattr( main, 'Compute1' )
        dstComponent = getattr( main, 'Compute2' )

        targets = main.funcs.getHostConnections( main, srcComponent )
        shortDescFailure = descPrefix + "-Failure"
        longDescFailure = "%s Failure: Bring down switch with traffic from %s" % ( descPrefix, srcComponent.name )
        shortDescRecovery = descPrefix + "-Recovery"
        longDescRecovery = "%s Recovery: Bring up switch previously killed" % descPrefix
        main.funcs.killSwitchAgent( targets, srcComponent, dstComponent,
                              shortDescFailure, longDescFailure,
                              shortDescRecovery, longDescRecovery,
                              stat='packetsReceived', bidirectional=False )
        # Cleanup
        main.log.warn( json.dumps( main.downtimeResults, indent=4, sort_keys=True ) )
        main.funcs.cleanup( main )

    def CASE206( self, main ):
        """
        Connect to Pod
        Create Flow between 2 dual homed hosts
        Kill the last leaf that traffic flows out of
        Verify flow continues using other link
        Collect logs and analyze results
        """
        try:
            from tests.USECASE.SegmentRouting.SRStaging.dependencies.SRStagingTest import SRStagingTest
            import json
        except ImportError:
            main.log.error( "SRStagingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRStagingTest()

        descPrefix = "CASE206-Destination-Leaf"
        pod = main.params['GRAPH'].get( 'nodeCluster', "hardware" )
        main.funcs.setupTest( main,
                              topology='0x2',
                              onosNodes=3,
                              description="%s tests on the %s pod" % ( descPrefix, pod ) )
        srcComponent = getattr( main, 'Compute1' )
        dstComponent = getattr( main, 'Compute2' )

        targets = main.funcs.getHostConnections( main, dstComponent )
        shortDescFailure = descPrefix + "-Failure"
        longDescFailure = "%s Failure: Bring down switch with traffic from %s" % ( descPrefix, srcComponent.name )
        shortDescRecovery = descPrefix + "-Recovery"
        longDescRecovery = "%s Recovery: Bring up switch previously killed" % descPrefix
        main.funcs.killSwitchAgent( targets, srcComponent, dstComponent,
                              shortDescFailure, longDescFailure,
                              shortDescRecovery, longDescRecovery,
                              stat='packetsSent', bidirectional=False )
        # Cleanup
        main.log.warn( json.dumps( main.downtimeResults, indent=4, sort_keys=True ) )
        main.funcs.cleanup( main )

    def CASE207( self, main ):
        """
        Connect to Pod
        Create Flow between 1 dual homed host and 1 single homed host
        Kill the leaf that traffic first flows into
        Verify flow continues using other link
        Collect logs and analyze results
        """
        try:
            from tests.USECASE.SegmentRouting.SRStaging.dependencies.SRStagingTest import SRStagingTest
            import json
        except ImportError:
            main.log.error( "SRStagingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRStagingTest()

        descPrefix = "CASE207-Source-Leaf"
        pod = main.params['GRAPH'].get( 'nodeCluster', "hardware" )
        main.funcs.setupTest( main,
                              topology='0x2',
                              onosNodes=3,
                              description="%s tests on the %s pod" % ( descPrefix, pod ) )
        srcComponentList = [ getattr( main, name ) for name in [ 'ManagmentServer', 'Compute1', 'Compute2' ] ]
        dstComponent = getattr( main, 'Compute3' )

        targets = main.funcs.getHostConnections( main, srcComponentList, excludedDIDs=[ 'leaf2' ] )
        shortDescFailure = descPrefix + "-Failure"
        longDescFailure = "%s Failure: Bring down switch with traffic to %s" % ( descPrefix, dstComponent.name )
        shortDescRecovery = descPrefix + "-Recovery"
        longDescRecovery = "%s Recovery: Bring up switch previously killed" % descPrefix
        main.funcs.killSwitchAgent( targets, srcComponentList, dstComponent,
                              shortDescFailure, longDescFailure,
                              shortDescRecovery, longDescRecovery,
                              stat='packetsReceived', bidirectional=False,
                              singleFlow=True )
        # Cleanup
        main.log.warn( json.dumps( main.downtimeResults, indent=4, sort_keys=True ) )
        main.funcs.cleanup( main )

    def CASE208( self, main ):
        """
        Connect to Pod
        Create Flow between 1 dual homed host and 1 single homed host
        Kill the last leaf that traffic flows out of
        Verify flow continues using other link
        Collect logs and analyze results
        """
        try:
            from tests.USECASE.SegmentRouting.SRStaging.dependencies.SRStagingTest import SRStagingTest
            import json
        except ImportError:
            main.log.error( "SRStagingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRStagingTest()

        descPrefix = "CASE208-Destination-Leaf"
        pod = main.params['GRAPH'].get( 'nodeCluster', "hardware" )
        main.funcs.setupTest( main,
                              topology='0x2',
                              onosNodes=3,
                              description="%s tests on the %s pod" % ( descPrefix, pod ) )
        srcComponent = getattr( main, 'Compute3' )
        dstComponentList = [ getattr( main, name ) for name in [ 'ManagmentServer', 'Compute1', 'Compute2' ] ]

        targets = main.funcs.getHostConnections( main, dstComponentList, excludedDIDs=[ 'leaf2' ] )
        shortDescFailure = descPrefix + "-Failure"
        longDescFailure = "%s Failure: Bring down switch with traffic from %s" % ( descPrefix, srcComponent.name )
        shortDescRecovery = descPrefix + "-Recovery"
        longDescRecovery = "%s Recovery: Bring up switch previously killed" % descPrefix
        main.funcs.killSwitchAgent( targets, srcComponent, dstComponentList,
                              shortDescFailure, longDescFailure,
                              shortDescRecovery, longDescRecovery,
                              stat='packetsSent', bidirectional=False,
                              singleFlow=True )
        # Cleanup
        main.log.warn( json.dumps( main.downtimeResults, indent=4, sort_keys=True ) )
        main.funcs.cleanup( main )

    def CASE301( self, main ):
        """
        Connect to Pod
        Setup static route to public internet via mgmt
        Ping public ip
        chech which link the ICMP traffic is going to
        Kill that link
        Verify flow continues using other link
        Restore link
        verify traffic still flows
        Collect logs and analyze results
        """
        try:
            from tests.USECASE.SegmentRouting.SRStaging.dependencies.SRStagingTest import SRStagingTest
            import json
            import re
        except ImportError:
            main.log.error( "SRStagingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRStagingTest()

        descPrefix = "CASE301-Upstream-Link"
        pod = main.params['GRAPH'].get( 'nodeCluster', "hardware" )
        main.funcs.setupTest( main,
                              topology='0x2',
                              onosNodes=3,
                              description="%s tests on the %s pod" % ( descPrefix, pod ) )

        # TODO Route ADD
        dstIp = "8.8.8.8"
        route = "%s/32" % dstIp
        """
        Try this on the host:
        ip route add 8.8.8.8/32 via <fabric interface ip>
        and this in ONOS:
        route-add 8.8.8.8/32 via <mgmt server fabric ip
        """

        srcComponent = getattr( main, 'Compute1' )
        nextHopComponent = getattr( main, 'ManagmentServer' )

        # Add route in host to outside host via gateway ip
        srcIface = srcComponent.interfaces[0].get( 'name' )
        srcIp = srcComponent.getIPAddress( iface=srcIface )
        hostsJson = json.loads( main.Cluster.active( 0 ).hosts() )
        netcfgJson = json.loads( main.Cluster.active( 0 ).getNetCfg( subjectClass='ports') )
        ips = []
        fabricIntfIp = None
        for obj in hostsJson:
            if srcIp in obj['ipAddresses']:
                for location in obj['locations']:
                    main.log.debug( location )
                    did = location['elementId'].encode( 'utf-8' )
                    port = location['port'].encode( 'utf-8' )
                    m = re.search( '\((\d+)\)', port )
                    if m:
                        port = m.group(1)
                    portId = "%s/%s" % ( did, port )
                    # Lookup ip assigned to this network port
                    ips.extend( [ x.encode( 'utf-8' ) for x in netcfgJson[ portId ][ 'interfaces' ][0][ 'ips' ] ] )
        ips = set( ips )
        ipRE = r'(\d+\.\d+\.\d+\.\d+)/\d+|([\w,:]*)/\d+'
        for ip in ips:
            ipMatch = re.search( ipRE, ip )
            if ipMatch:
                fabricIntfIp = ipMatch.group(1)
                main.log.debug( "Found %s as gateway ip for %s" % ( fabricIntfIp, srcComponent.shortName ) )
                # FIXME: How to chose the correct one if there are multiple? look at subnets
        addResult = srcComponent.addRouteToHost( route, fabricIntfIp, srcIface, sudoRequired=True, purgeOnDisconnect=True )
        failMsg = "Failed to add static route to host"
        utilities.assert_equals( expect=main.TRUE, actual=addResult,
                                 onpass="Added static route to host",
                                 onfail=failMsg )
        main.log.debug( srcComponent.getRoutes() )
        if not addResult:
            main.skipCase( result="FAIL", msg=failMsg )

        # Add route in ONOS
        nextHopIface = nextHopComponent.interfaces[0].get( 'name' )
        nextHopIp = nextHopComponent.getIPAddress( iface=nextHopIface )
        main.Cluster.active( 0 ).routeAdd( route, nextHopIp )
        main.log.debug( main.Cluster.active( 0 ).routes() )



        ####
        targets = main.funcs.getHostConnections( main, nextHopComponent )
        shortDesc = descPrefix + "-Failure"
        longDesc = "%s Failure: Bring down port with traffic to %s" % ( descPrefix, route )
        #TODO: Option to just do ping
        killDevice, killPort = main.funcs.linkDown( targets, srcComponent, nextHopComponent, shortDesc,
                                                    longDesc, stat='packetsSent', bidirectional=False,
                                                    pingOnly=True, dstIp=dstIp )
        shortDesc = descPrefix + "-Recovery"
        longDesc = "%s Recovery: Bring up %s/%s" % ( descPrefix, killDevice, killPort )
        main.funcs.linkUp( killDevice, killPort, srcComponent, nextHopComponent, shortDesc, longDesc,
                           bidirectional=False, pingOnly=True, dstIp=dstIp )

        # Remove route in ONOS
        main.Cluster.active( 0 ).routeRemove( route, nextHopIp )
        main.log.debug( main.Cluster.active( 0 ).routes() )
        # Remove route on host
        delResult = srcComponent.deleteRoute( route, fabricIntfIp, srcIface, sudoRequired=True )
        utilities.assert_equals( expect=main.TRUE, actual=delResult,
                                 onpass="Removed static route from host",
                                 onfail="Failed to remove static route from host" )
        main.log.debug( srcComponent.getRoutes() )
        # Cleanup
        main.log.warn( json.dumps( main.downtimeResults, indent=4, sort_keys=True ) )
        main.funcs.cleanup( main )
