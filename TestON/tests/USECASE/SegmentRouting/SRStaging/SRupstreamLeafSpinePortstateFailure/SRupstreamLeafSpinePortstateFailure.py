class SRupstreamLeafSpinePortstateFailure:
    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        main.case("Testing connections")
        main.persistentSetup = True

    def CASE2( self, main ):
        """
        Connect to Pod
        Perform Upstream Leaf-Spine Link, portstate failure/recovery test
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

        descPrefix = "Upstream_Leaf_Spine_Portstate"
        leafType = "upstream"
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
        deviceShortName = None
        portsList = []
        for shortName, values in main.params['PERF']['topo'].iteritems():
            if leafType in values['note']:
                deviceShortName = shortName
                portsList = [ int( p ) for p in values['ports'].split() ]
                break
        if not deviceShortName:
            main.skipCase( result="FAIL", msg="Don't know which switch for test" )

        device = "device:" + deviceShortName
        port1 = None
        port2 = None
        port3 = None
        port4 = None

        ## First Link Down
        shortDesc = descPrefix + "-Failure1"
        longDesc = "%s Failure: Bring down port with most traffic on %s" % ( descPrefix, device )
        targets = {}
        targets[device] = portsList
        device1, port1 = main.funcs.linkDown( targets, srcComponentList, dstComponent, shortDesc, longDesc )
        for src in srcNames:
            srcComponent = getattr( main, src )
            dbHeaders.append( "%s-%s" % ( shortDesc, srcComponent.shortName ) )
            dbHeaders.append( "%s-%s-to-%s" % ( shortDesc, srcComponent.shortName, dstComponent.shortName ) )
        ## Second Link Down
        shortDesc = descPrefix + "-Failure2"
        longDesc = "%s Failure: Bring down port with most traffic on %s" % ( descPrefix, device )
        device2, port2 = main.funcs.linkDown( targets, srcComponentList, dstComponent, shortDesc, longDesc )
        for src in srcNames:
            srcComponent = getattr( main, src )
            dbHeaders.append( "%s-%s" % ( shortDesc, srcComponent.shortName ) )
            dbHeaders.append( "%s-%s-to-%s" % ( shortDesc, srcComponent.shortName, dstComponent.shortName ) )
        ## First Link Up
        shortDesc = descPrefix + "-Recovery1"
        longDesc = "%s Recovery: Bring up %s/%s" % ( descPrefix, device, port1 )
        main.funcs.linkUp( device, port1, srcComponentList, dstComponent, shortDesc, longDesc )
        for src in srcNames:
            srcComponent = getattr( main, src )
            dbHeaders.append( "%s-%s" % ( shortDesc, srcComponent.shortName ) )
            dbHeaders.append( "%s-%s-to-%s" % ( shortDesc, srcComponent.shortName, dstComponent.shortName ) )
        ## Second Link Up
        shortDesc = descPrefix + "-Recovery2"
        longDesc = "%s Recovery: Bring up %s/%s" % ( descPrefix, device, port2 )
        main.funcs.linkUp( device, port2, srcComponentList, dstComponent, shortDesc, longDesc )
        for src in srcNames:
            srcComponent = getattr( main, src )
            dbHeaders.append( "%s-%s" % ( shortDesc, srcComponent.shortName ) )
            dbHeaders.append( "%s-%s-to-%s" % ( shortDesc, srcComponent.shortName, dstComponent.shortName ) )
        ## Third Link Down
        shortDesc = descPrefix + "-Failure3"
        longDesc = "%s Failure: Bring down port with most traffic on %s" % ( descPrefix, device )
        device3, port3 = main.funcs.linkDown( targets, srcComponentList, dstComponent, shortDesc, longDesc )
        for src in srcNames:
            srcComponent = getattr( main, src )
            dbHeaders.append( "%s-%s" % ( shortDesc, srcComponent.shortName ) )
            dbHeaders.append( "%s-%s-to-%s" % ( shortDesc, srcComponent.shortName, dstComponent.shortName ) )
        ## Forth Link Down
        shortDesc = descPrefix + "-Failure4"
        longDesc = "%s Failure: Bring down port with most traffic on %s" % ( descPrefix, device )
        device4, port4 = main.funcs.linkDown( targets, srcComponentList, dstComponent, shortDesc, longDesc )
        for src in srcNames:
            srcComponent = getattr( main, src )
            dbHeaders.append( "%s-%s" % ( shortDesc, srcComponent.shortName ) )
            dbHeaders.append( "%s-%s-to-%s" % ( shortDesc, srcComponent.shortName, dstComponent.shortName ) )
        ## Third Link Up
        shortDesc = descPrefix + "-Recovery3"
        longDesc = "%s Recovery: Bring up %s/%s" % ( descPrefix, device, port3 )
        main.funcs.linkUp( device, port3, srcComponentList, dstComponent, shortDesc, longDesc )
        for src in srcNames:
            srcComponent = getattr( main, src )
            dbHeaders.append( "%s-%s" % ( shortDesc, srcComponent.shortName ) )
            dbHeaders.append( "%s-%s-to-%s" % ( shortDesc, srcComponent.shortName, dstComponent.shortName ) )
        ## Forth Link Up
        shortDesc = descPrefix + "-Recovery4"
        longDesc = "%s Recovery: Bring up %s/%s" % ( descPrefix, device, port4 )
        main.funcs.linkUp( device, port4, srcComponentList, dstComponent, shortDesc, longDesc )
        for src in srcNames:
            srcComponent = getattr( main, src )
            dbHeaders.append( "%s-%s" % ( shortDesc, srcComponent.shortName ) )
            dbHeaders.append( "%s-%s-to-%s" % ( shortDesc, srcComponent.shortName, dstComponent.shortName ) )

        main.log.warn( json.dumps( main.downtimeResults, indent=4, sort_keys=True ) )
        main.funcs.cleanup( main )
