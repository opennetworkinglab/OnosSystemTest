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
        #run.loadChart( main )  # stores hosts to ping and expected results
        #run.pingAll( main, useScapy=False )
        run.verifyPing( main, hosts, hosts )
        #main.funcs.cleanup( main )
        # run.verifyTraffic

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
        #main.funcs.cleanup( main )
