class SReNBLeafSpinePortstateFailure:
    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        main.case("Testing connections")
        main.persistentSetup = True

    def CASE2( self, main ):
        """
        Connect to Pod
        Perform eNB Leaf-Spine Link, portstate failure/recovery test
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

        descPrefix = "eNB_Leaf_Spine_Portstate"
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
        dbHeaders = []
        srcNames = [ src.name for src in srcComponentList ]
        srcNames.sort()
        # TODO: MOVE TO CONFIG FILE
        device = "device:leaf1"
        portsList = [ 176, 180, 184, 188 ]
        port1 = None
        port2 = None
        port3 = None
        port4 = None

        ## First Link Down
        shortDesc = descPrefix + "-Failure1"
        longDesc = "%s Failure: Bring down port with most traffic on %s" % ( descPrefix, device )
        port1 = main.funcs.linkDown( device, portsList, srcComponentList, dstComponent, shortDesc, longDesc )
        for src in srcNames:
            dbHeaders.append( "%s-%s" % ( shortDesc, src ) )
        for src in srcNames:
            dbHeaders.append( "%s-%s-%s" % ( shortDesc, src, dstComponent.name ) )
        ## Second Link Down
        shortDesc = descPrefix + "-Failure2"
        longDesc = "%s Failure: Bring down port with most traffic on %s" % ( descPrefix, device )
        port2 = main.funcs.linkDown( device, portsList, srcComponentList, dstComponent, shortDesc, longDesc )
        for src in srcNames:
            dbHeaders.append( "%s-%s" % ( shortDesc, src ) )
        for src in srcNames:
            dbHeaders.append( "%s-%s-%s" % ( shortDesc, src, dstComponent.name ) )
        ## First Link Up
        shortDesc = descPrefix + "-Recovery1"
        longDesc = "%s Recovery: Bring up %s/%s" % ( descPrefix, device, port1 )
        main.funcs.linkUp( device, port1, srcComponentList, dstComponent, shortDesc, longDesc )
        for src in srcNames:
            dbHeaders.append( "%s-%s" % ( shortDesc, src ) )
        for src in srcNames:
            dbHeaders.append( "%s-%s-%s" % ( shortDesc, src, dstComponent.name ) )
        ## Second Link Up
        shortDesc = descPrefix + "-Recovery2"
        longDesc = "%s Recovery: Bring up %s/%s" % ( descPrefix, device, port2 )
        main.funcs.linkUp( device, port2, srcComponentList, dstComponent, shortDesc, longDesc )
        for src in srcNames:
            dbHeaders.append( "%s-%s" % ( shortDesc, src ) )
        for src in srcNames:
            dbHeaders.append( "%s-%s-%s" % ( shortDesc, src, dstComponent.name ) )
        ## Third Link Down
        shortDesc = descPrefix + "-Failure3"
        longDesc = "%s Failure: Bring down port with most traffic on %s" % ( descPrefix, device )
        port3 = main.funcs.linkDown( device, portsList, srcComponentList, dstComponent, shortDesc, longDesc )
        for src in srcNames:
            dbHeaders.append( "%s-%s" % ( shortDesc, src ) )
        for src in srcNames:
            dbHeaders.append( "%s-%s-%s" % ( shortDesc, src, dstComponent.name ) )
        ## Forth Link Down
        shortDesc = descPrefix + "-Failure4"
        longDesc = "%s Failure: Bring down port with most traffic on %s" % ( descPrefix, device )
        port4 = main.funcs.linkDown( device, portsList, srcComponentList, dstComponent, shortDesc, longDesc )
        for src in srcNames:
            dbHeaders.append( "%s-%s" % ( shortDesc, src ) )
        for src in srcNames:
            dbHeaders.append( "%s-%s-%s" % ( shortDesc, src, dstComponent.name ) )
        ## Third Link Up
        shortDesc = descPrefix + "-Recovery3"
        longDesc = "%s Recovery: Bring upn %s/%s" % ( descPrefix, device, port3 )
        main.funcs.linkUp( device, port3, srcComponentList, dstComponent, shortDesc, longDesc )
        for src in srcNames:
            dbHeaders.append( "%s-%s" % ( shortDesc, src ) )
        for src in srcNames:
            dbHeaders.append( "%s-%s-%s" % ( shortDesc, src, dstComponent.name ) )
        ## Forth Link Up
        shortDesc = descPrefix + "-Recovery4"
        longDesc = "%s Recovery: Bring up  %s/%s" % ( descPrefix, device, port4 )
        main.funcs.linkUp( device, port4, srcComponentList, dstComponent, shortDesc, longDesc )
        for src in srcNames:
            dbHeaders.append( "%s-%s" % ( shortDesc, src ) )
        for src in srcNames:
            dbHeaders.append( "%s-%s-%s" % ( shortDesc, src, dstComponent.name ) )

        main.log.warn( json.dumps( main.downtimeResults, indent=4, sort_keys=True ) )
        main.funcs.cleanup( main, headerOrder=dbHeaders )
