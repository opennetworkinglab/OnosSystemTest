class SRrollingRestart:
    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        main.case("Testing connections")
        main.persistentSetup = True

    def CASE2( self, main ):
        """
        Connect to Pod
        Perform rolling ONOS failure/recovery test
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

        descPrefix = "Rolling ONOS Restart"
        pod = main.params['GRAPH'].get( 'nodeCluster', "hardware" )
        main.funcs.setupTest( main,
                              topology='0x2',
                              onosNodes=3,
                              description="%s tests on the %s pod" % ( descPrefix, pod ) )
        switches = int( main.params[ 'TOPO' ][ 'switchNum' ] )
        links = int( main.params[ 'TOPO' ][ 'linkNum' ] )
        hosts = [ 'h1', 'h2', 'h3' ]

        clusterSize = main.Cluster.numCtrls
        restartRounds = int( main.params.get( 'restartRounds', 1 ) )

        def verifications( main, switches, links, hosts ):
            """
            Checks to perform before and after each ONOS node event
            All asserts should happen within this function
            """
            from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as run
            run.verifyTopology( main, switches, links, main.Cluster.numCtrls )
            run.pingAllFabricIntfs( main, hosts, dumpFlows=False )
            run.verifyPing( main, hosts, hosts )
        verifications( main, switches, links, hosts )
        # TODO ADD control plane checks: nodes, flows, ...
        # TODO: Mastership check? look at HA Test
        # TODO: Any specific fabric checks? APP commands?

        for i in range( 0, clusterSize * restartRounds ):
            n = i % clusterSize
            ctrl = main.Cluster.getControllers( n )

            longDesc = "%s - kill %s" % ( descPrefix, ctrl.name )
            # TODO: verify flow isn't interrupted
            node = main.funcs.onosDown( main, ctrl, preventRestart=True )
            verifications( main, switches, links, hosts )
            main.funcs.onosUp( main, node, ctrl )
            verifications( main, switches, links, hosts )
        # Cleanup
        main.log.warn( json.dumps( main.downtimeResults, indent=4, sort_keys=True ) )
        main.funcs.cleanup( main )


