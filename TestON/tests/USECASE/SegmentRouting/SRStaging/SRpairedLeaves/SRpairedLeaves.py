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
        # TODO: Verify Cleanup works as intended, even with multiple testcases running in a row
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
        # TODO: Verify Cleanup works as intended, even with multiple testcases running in a row
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
        # TODO: Verify Cleanup works as intended, even with multiple testcases running in a row
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
        # TODO: Verify Cleanup works as intended, even with multiple testcases running in a row
        main.log.warn( json.dumps( main.downtimeResults, indent=4, sort_keys=True ) )
        main.funcs.cleanup( main )
