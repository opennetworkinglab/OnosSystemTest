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

        # TODO: MOVE TO CONFIG FILE
        switchComponent = getattr( main, "SwitchSpine1" )
        device = "device:leaf1"

        ## First Spine Reboot
        shortDesc = descPrefix + "-Failure1"
        longDesc = "%s Failure: Reboot %s" % ( descPrefix, device )
        main.funcs.onlReboot( device, switchComponent, srcComponentList, dstComponent, shortDesc, longDesc )
        ## Second Spine Reboot

        main.log.warn( json.dumps( main.downtimeResults, indent=4, sort_keys=True ) )
        main.funcs.cleanup( main )
