class SRStaging:
    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        main.case("Testing connections")
        main.persistentSetup = True
    def CASE7( self, main ):
        """
        Tests connectivity between two untagged hosts
        (Ports are configured as vlan-untagged)

        Sets up 3 ONOS instance
        Start 2x2 leaf-spine topology
        Pingall
        """
        try:
            from tests.USECASE.SegmentRouting.SRStaging.dependencies.SRStagingTest import SRStagingTest
        except ImportError:
            main.log.error( "SRStagingTest not found. Exiting the test" )
            main.cleanAndExit()
        try:
            main.funcs
        except ( NameError, AttributeError ):
            main.funcs = SRStagingTest()
        # Load kubeconfig
        # Setup ssh tunnel
        # connect to ONOS CLI


        main.funcs.setupTest( main,
                              test_idx=7,
                              topology='2x2staging',
                              onosNodes=3,
                              description="Developing tests on the staging pod" )
        srcComponentNames = main.params[ 'PERF' ][ 'traffic_host' ].split()
        srcComponentList = []
        for name in srcComponentNames:
            srcComponentList.append( getattr( main, name ) )
        dstComponent = getattr( main, main.params[ 'PERF' ][ 'pcap_host' ] )

        main.downtimeResults = {}


        # TODO: MOVE TO CONFIG FILE
        device = "device:leaf2"
        port1 = "268"
        port2 = "284"
        port3 = "260"
        port4 = "276"

        descPrefix = "Upstream_Leaf_Spine_Portstate"
        # TODO: Move most of this logic into linkDown/linkUp
        ## First Link Down
        shortDesc = descPrefix + "-Failure1"
        longDesc = "%s Failure: Bring down %s/%s" % ( descPrefix, device, port1 )
        main.funcs.linkDown( device, port1, srcComponentList, dstComponent, shortDesc, longDesc )
        ## Second Link Down
        shortDesc = descPrefix + "-Failure2"
        longDesc = "%s Failure: Bring down %s/%s" % ( descPrefix, device, port2 )
        main.funcs.linkDown( device, port2, srcComponentList, dstComponent, shortDesc, longDesc )
        ## First Link Up
        # TODO Check these are set correctly
        shortDesc = descPrefix + "-Recovery1"
        longDesc = "%s Recovery: Bring up %s/%s" % ( descPrefix, device, port1 )
        main.funcs.linkUp( device, port1, srcComponentList, dstComponent, shortDesc, longDesc )
        ## Second Link Up
        shortDesc = descPrefix + "-Recovery2"
        longDesc = "%s Recovery: Bring up %s/%s" % ( descPrefix, device, port2 )
        main.funcs.linkUp( device, port2, srcComponentList, dstComponent, shortDesc, longDesc )
        ## Third Link Down
        shortDesc = descPrefix + "-Failure3"
        longDesc = "%s Failure: Bring down %s/%s" % ( descPrefix, device, port3 )
        main.funcs.linkDown( device, port3, srcComponentList, dstComponent, shortDesc, longDesc )
        ## Forth Link Down
        shortDesc = descPrefix + "-Failure4"
        longDesc = "%s Failure: Bring down %s/%s" % ( descPrefix, device, port4 )
        main.funcs.linkDown( device, port4, srcComponentList, dstComponent, shortDesc, longDesc )
        ## Third Link Up
        shortDesc = descPrefix + "-Recovery3"
        longDesc = "%s Recovery: Bring upn %s/%s" % ( descPrefix, device, port3 )
        main.funcs.linkUp( device, port3, srcComponentList, dstComponent, shortDesc, longDesc )
        ## Forth Link Up
        shortDesc = descPrefix + "-Recovery4"
        longDesc = "%s Recovery: Bring up  %s/%s" % ( descPrefix, device, port4 )
        main.funcs.linkUp( device, port4, srcComponentList, dstComponent, shortDesc, longDesc )

        main.log.warn( main.downtimeResults )
        import json
        main.log.warn( json.dumps( main.downtimeResults, indent=4, sort_keys=True ) )
        main.funcs.cleanup( main )
