class SRONLReboot:
    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        main.case("Testing connections")
        main.persistentSetup = True

    def CASE2( self, main ):
        """
        Connect to Pod
        Perform ONL reboot failure/recovery test
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

        descPrefix = "ONL_Reboot"
        main.funcs.setupTest( main,
                              topology='2x2staging',
                              onosNodes=3,
                              description="%s tests on the staging pod" % descPrefix )
        srcComponentNames = main.params[ 'PERF' ][ 'traffic_host' ].split()
        srcComponentList = []
        for name in srcComponentNames:
            srcComponentList.append( getattr( main, name ) )
        dstComponent = getattr( main, main.params[ 'PERF' ][ 'pcap_host' ] )

        main.downtimeResults = {}

        switchComponentList = [ getattr( main, "Spine%s" % n ) for n in range( 1, 2+1 ) ]
        iterations = int( main.params[ 'PERF' ][ 'iterations' ] )

        for i in range( 1, iterations + 1 ):
            ## Spine ONL Reboot
            shortDescFailure = descPrefix + "-Failure%s" % i
            longDescFailure = "%s Failure%s: Reboot switch" % ( descPrefix, i )
            shortDescRecovery = descPrefix + "-Recovery%s" % i
            longDescRecovery = "%s Recovery%s: Reboot switch" % ( descPrefix, i )
            main.funcs.onlReboot( switchComponentList, srcComponentList, dstComponent,
                                  shortDescFailure, longDescFailure,
                                  shortDescRecovery, longDescRecovery )

        main.log.warn( json.dumps( main.downtimeResults, indent=4, sort_keys=True ) )
        main.funcs.cleanup( main )
