class SdnBase:

    def __init__( self ):
        self.default = ''

    def initSetup( self ):
        import json
        import time
        import os
        from operator import eq
        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
            main.testSetUp = ONOSSetup()
        except Exception:
            main.log.error( "ONOSSetup not found. exiting the test" )
            main.cleanAndExit()
        main.testSetUp.envSetupDescription()
        main.testSetUp.envSetup()
        main.apps = main.params[ 'ENV' ][ 'appString' ]
        cellName = main.params[ 'ENV' ][ 'cellName' ]

        main.step( "Copying config files" )
        src = os.path.dirname( main.testFile ) + "/network-cfg.json"
        dst = main.ONOSbench.home + "/tools/package/config/network-cfg.json"
        status = main.ONOSbench.scp( main.ONOSbench, src, dst, direction="to" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=status,
                                 onpass="Copy config file succeeded",
                                 onfail="Copy config file failed" )
        main.testSetUp.ONOSSetUp( main.Cluster, cellName=cellName )

        main.step( "Checking if ONOS CLI is ready for issuing commands" )
        ready = utilities.retry( main.Cluster.command,
                                  False,
                                  kwargs={ "function": "summary", "contentCheck": True },
                                  sleep=30,
                                  attempts=10 )
        utilities.assert_equals( expect=True, actual=ready,
                                 onpass="ONOS summary command succeded",
                                 onfail="ONOS summary command failed" )

        if not ready:
            main.log.error( "ONOS startup failed!" )
            main.cleanAndExit()

    def pToPIntentTest( self, intentExpectedNum ):
        """
        point-to-point intents test for each BGP peer and BGP speaker pair
        """
        import time
        main.case( "Check point-to-point intents" )
        main.log.info( "There are %s BGP peers in total "
                       % main.params[ 'config' ][ 'peerNum' ] )
        main.step( "Check P2P intents number from ONOS CLI" )

        getIntentsResult = main.Cluster.active( 0 ).CLI.intents( jsonFormat=True )
        bgpIntentsActualNum = \
            main.QuaggaCliSpeaker1.extractActualBgpIntentNum( getIntentsResult )
        bgpIntentsExpectedNum = int( main.params[ 'config' ][ 'peerNum' ] ) * intentExpectedNum
        if bgpIntentsActualNum != bgpIntentsExpectedNum:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            getIntentsResult = main.Cluster.active( 0 ).CLI.intents( jsonFormat=True )
            bgpIntentsActualNum = \
                main.QuaggaCliSpeaker1.extractActualBgpIntentNum( getIntentsResult )
        main.log.info( "bgpIntentsExpected num is:" )
        main.log.info( bgpIntentsExpectedNum )
        main.log.info( "bgpIntentsActual num is:" )
        main.log.info( bgpIntentsActualNum )
        utilities.assert_equals( expect=bgpIntentsExpectedNum,
                                 actual=bgpIntentsActualNum,
                                 onpass="PointToPointIntent Intent Num is correct!",
                                 onfail="PointToPointIntent Intent Num is wrong!" )

    def routeAndIntentCheck( self, allRoutesExpected, routeIntentsExpectedNum ):
        """
        routes and intents check to all BGP peers
        """
        import time
        getRoutesResult = main.Cluster.active( 0 ).CLI.routes( jsonFormat=True )
        allRoutesActual = \
            main.QuaggaCliSpeaker1.extractActualRoutesMaster( getRoutesResult )
        allRoutesStrExpected = str( sorted( allRoutesExpected ) )
        allRoutesStrActual = str( allRoutesActual ).replace( 'u', "" )
        if allRoutesStrActual != allRoutesStrExpected:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            getRoutesResult = main.Cluster.active( 0 ).CLI.routes( jsonFormat=True )
            allRoutesActual = \
                main.QuaggaCliSpeaker1.extractActualRoutesMaster( getRoutesResult )
            allRoutesStrActual = str( allRoutesActual ).replace( 'u', "" )

        main.step( "Check routes installed" )
        main.log.info( "Routes expected:" )
        main.log.info( allRoutesStrExpected )
        main.log.info( "Routes get from ONOS CLI:" )
        main.log.info( allRoutesStrActual )
        utilities.assertEquals(
            expect=allRoutesStrExpected, actual=allRoutesStrActual,
            onpass="Routes are correct!",
            onfail="Routes are wrong!" )

        main.step( "Check M2S intents installed" )
        getIntentsResult = main.Cluster.active( 0 ).CLI.intents( jsonFormat=True )
        routeIntentsActualNum = \
            main.QuaggaCliSpeaker1.extractActualRouteIntentNum( getIntentsResult )
        if routeIntentsActualNum != routeIntentsExpectedNum:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            getIntentsResult = main.Cluster.active( 0 ).CLI.intents( jsonFormat=True )
            routeIntentsActualNum = \
                main.QuaggaCliSpeaker1.extractActualRouteIntentNum( getIntentsResult )

        main.log.info( "MultiPointToSinglePoint Intent Num expected is:" )
        main.log.info( routeIntentsExpectedNum )
        main.log.info( "MultiPointToSinglePoint Intent NUM Actual is:" )
        main.log.info( routeIntentsActualNum )
        utilities.assertEquals(
            expect=routeIntentsExpectedNum,
            actual=routeIntentsActualNum,
            onpass="MultiPointToSinglePoint Intent Num is correct!",
            onfail="MultiPointToSinglePoint Intent Num is wrong!" )

        main.step( "Check whether all flow status are ADDED" )
        flowCheck = utilities.retry( main.Cluster.active( 0 ).CLI.checkFlowsState,
                                     main.FALSE,
                                     kwargs={ 'isPENDING': False },
                                     attempts=10 )
        utilities.assertEquals(
            expect=main.TRUE,
            actual=flowCheck,
            onpass="Flow status is correct!",
            onfail="Flow status is wrong!" )

    def linkUpDownCheck( self, link1Peer, link2Peer, link3Peer,
                         link1RouteNum, link1IntentNum,
                         link2RouteNum, link2IntentNum,
                         link3RouteNum, link3IntentNum,
                         speakers, hosts, upOrDown ):
        """
        Cut/Recover links to peers one by one, check routes/intents
        upOrDown - "up" or "down"
        """
        import time
        main.case( "Bring " + upOrDown + " links and check routes/intents" )
        main.step( "Bring " + upOrDown + " the link between sw32 and " + link1Peer )
        linkResult1 = main.Mininet.link( END1="sw32", END2=link1Peer,
                                         OPTION=upOrDown )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=linkResult1,
                                 onpass="Bring down link succeeded!",
                                 onfail="Bring down link failed!" )

        if linkResult1 == main.TRUE:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, link1RouteNum )
            main.Functions.checkM2SintentNum( main, link1IntentNum )
        else:
            main.log.error( "Bring " + upOrDown + " link failed!" )
            main.cleanAndExit()

        main.step( "Bring " + upOrDown + " the link between sw8 and " + link2Peer )
        linkResult2 = main.Mininet.link( END1="sw8", END2=link2Peer,
                                         OPTION=upOrDown )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=linkResult2,
                                 onpass="Bring " + upOrDown + " link succeeded!",
                                 onfail="Bring " + upOrDown + " link failed!" )
        if linkResult2 == main.TRUE:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, link2RouteNum )
            main.Functions.checkM2SintentNum( main, link2IntentNum )
        else:
            main.log.error( "Bring " + upOrDown + " link failed!" )
            main.cleanAndExit()

        main.step( "Bring " + upOrDown + " the link between sw28 and " + link3Peer )
        linkResult3 = main.Mininet.link( END1="sw28", END2=link3Peer,
                                         OPTION=upOrDown )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=linkResult3,
                                 onpass="Bring " + upOrDown + " link succeeded!",
                                 onfail="Bring " + upOrDown + " link failed!" )
        if linkResult3 == main.TRUE:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, link3RouteNum )
            main.Functions.checkM2SintentNum( main, link3IntentNum )
        else:
            main.log.error( "Bring " + upOrDown + " link failed!" )
            main.cleanAndExit()

        main.step( "Check whether all flow status are ADDED" )
        flowCheck = utilities.retry( main.Cluster.active( 0 ).CLI.checkFlowsState,
                                     main.FALSE,
                                     kwargs={ 'isPENDING': False },
                                     attempts=10 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=flowCheck,
                                 onpass="Flow status is correct!",
                                 onfail="Flow status is wrong!" )

        # Ping test
        main.Functions.pingSpeakerToPeer( main, speakers=[ speakers ],
                                          peers=[ link1Peer, link2Peer, link3Peer ],
                                          expectAllSuccess=False )
        main.Functions.pingHostToHost( main,
                                       hosts=hosts,
                                       expectAllSuccess=False )
