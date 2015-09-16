# Testing the functionality of SDN-IP with single ONOS instance
class USECASE_SdnipI2:

    def __init__( self ):
        self.default = ''
        global branchName

    # This case is to setup Mininet testbed
    def CASE100( self, main ):
        """
            Start mininet
        """
        import os
        import imp
        main.log.case( "Start Mininet topology" )
        main.dependencyPath = main.testDir + \
                              main.params[ 'DEPENDENCY' ][ 'path' ]
        main.topology = main.params[ 'DEPENDENCY' ][ 'topology' ]

        main.step( "Starting Mininet Topology" )
        topology = main.dependencyPath + main.topology
        topoResult = main.Mininet.startNet( topoFile = topology )
        stepResult = topoResult
        utilities.assert_equals( expect = main.TRUE,
                                 actual = stepResult,
                                 onpass = "Successfully loaded topology",
                                 onfail = "Failed to load topology" )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanup()
            main.exit()

    # This case is to setup ONOS
    def CASE101( self, main ):
        """
           CASE100 is to compile ONOS and install it
           Startup sequence:
           cell <name>
           onos-verify-cell
           git pull
           mvn clean install
           onos-package
           onos-install -f
           onos-wait-for-start
        """
        import json
        import time
        from operator import eq

        main.case( "Setting up test environment" )

        cellName = main.params[ 'ENV' ][ 'cellName' ]
        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]

        main.step( "Applying cell variable to environment" )
        cellResult = main.ONOSbench.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()

        branchName = main.ONOSbench.getBranchName()
        main.log.info( "ONOS is on branch: " + branchName )

        main.log.report( "Uninstalling ONOS" )
        main.ONOSbench.onosUninstall( ONOS1Ip )

        # cleanInstallResult = main.TRUE
        # gitPullResult = main.TRUE

        main.step( "Git pull" )
        gitPullResult = main.ONOSbench.gitPull()

        main.step( "Using mvn clean install" )
        if gitPullResult == main.TRUE:
            cleanInstallResult = main.ONOSbench.cleanInstall( mciTimeout = 1000 )
        else:
             main.log.warn( "Did not pull new code so skipping mvn " +
                            "clean install" )
             cleanInstallResult = main.TRUE

        main.ONOSbench.getVersion( report = True )

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage( opTimeout = 500 )

        main.step( "Installing ONOS package" )
        onos1InstallResult = main.ONOSbench.onosInstall( options = "-f",
                                                           node = ONOS1Ip )

        main.step( "Checking if ONOS is up yet" )
        for i in range( 2 ):
            onos1Isup = main.ONOSbench.isup( ONOS1Ip, timeout = 420 )
            if onos1Isup:
                break
        if not onos1Isup:
            main.log.report( "ONOS1 didn't start!" )

        cliResult = main.ONOScli.startOnosCli( ONOS1Ip,
                commandlineTimeout = 100, onosStartTimeout = 600 )

        caseResult = ( cleanInstallResult and packageResult and
                        cellResult and verifyResult and
                        onos1InstallResult and
                        onos1Isup and cliResult )

        utilities.assert_equals( expect = main.TRUE, actual = caseResult,
                                 onpass = "ONOS startup successful",
                                 onfail = "ONOS startup NOT successful" )

        if caseResult == main.FALSE:
            main.cleanup()
            main.exit()

        main.step( "Get links in the network" )
        listResult = main.ONOScli.links( jsonFormat = False )
        main.log.info( listResult )
        main.log.info( "Activate sdn-ip application" )
        main.ONOScli.activateApp( "org.onosproject.sdnip" )

        main.log.info( "Wait sdn-ip to finish installing connectivity intents, \
        and the BGP paths in data plane are ready..." )
        time.sleep( int( main.params[ 'timers' ][ 'SdnIpSetup' ] ) )
        main.log.info( "Wait Quagga to finish delivery all routes to each \
        other and to sdn-ip, plus finish installing all intents..." )
        time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
        time.sleep( int( main.params[ 'timers' ][ 'PathAvailable' ] ) )


    def CASE102( self, main ):
        '''
        This test case is to load the methods from other Python files.
        '''
        main.case( "Loading the methods from other Python file" )
        # load the methods from other file
        wrapperFile = main.params[ 'DEPENDENCY' ][ 'wrapper1' ]
        main.Functions = imp.load_source( wrapperFile,
                                          main.dependencyPath +
                                          wrapperFile +
                                          ".py" )


    def CASE1( self, main ):
        '''
        ping test from 3 bgp peers to BGP speaker
        '''

        m2SIntentsNumberActual = main.ONOScli.m2SIntentInstalledNumber()
        main.log.info( "MultiPointToSinglePoint intent number actual is:" )
        main.log.info( m2SIntentsNumberActual )

        main.case( "This case is to check ping between BGP peers and speakers" )
        result1 = main.Mininet.pingHost( src = "speaker1", target = "peer64514" )
        result2 = main.Mininet.pingHost( src = "speaker1", target = "peer64515" )
        result3 = main.Mininet.pingHost( src = "speaker1", target = "peer64516" )


        caseResult = result1 and result2 and result3
        utilities.assert_equals( expect = main.TRUE, actual = caseResult,
                                 onpass = "Speaker1 ping peers successful",
                                 onfail = "Speaker1 ping peers NOT successful" )

        if caseResult == main.FALSE:
            main.cleanup()
            main.exit()


    def CASE2( self, main ):
        '''
        point-to-point intents test for each BGP peer and BGP speaker pair
        '''
        main.case( "This case is to check point-to-point intents" )
        main.log.info( "There are %s BGP peers in total "
                       % main.params[ 'config' ][ 'peerNum' ] )
        main.step( "Get point-to-point intents from ONOS CLI" )

        getIntentsResult = main.ONOScli.intents( jsonFormat = True )
        bgpIntentsActualNum = \
            main.QuaggaCliSpeaker1.extractActualBgpIntentNum( getIntentsResult )
        bgpIntentsExpectedNum = int( main.params[ 'config' ][ 'peerNum' ] ) * 6
        main.log.info( "bgpIntentsExpected num is:" )
        main.log.info( bgpIntentsExpectedNum )
        main.log.info( "bgpIntentsActual num is:" )
        main.log.info( bgpIntentsActualNum )
        utilities.assertEquals( \
            expect = True,
            actual = eq( bgpIntentsExpectedNum, bgpIntentsActualNum ),
            onpass = "***PointToPointIntent Intent Num in SDN-IP are correct!***",
            onfail = "***PointToPointIntent Intent Num in SDN-IP are wrong!***" )


    def CASE3( self, main ):
        '''
        routes and intents check to all BGP peers
        '''
        main.case( "This case is to check routes and intents to all BGP peers" )

        allRoutesExpected = []
        allRoutesExpected.append( "4.0.0.0/24" + "/" + "10.0.4.1" )
        allRoutesExpected.append( "5.0.0.0/24" + "/" + "10.0.5.1" )
        allRoutesExpected.append( "6.0.0.0/24" + "/" + "10.0.6.1" )

        getRoutesResult = main.ONOScli.routes( jsonFormat = True )
        allRoutesActual = \
            main.QuaggaCliSpeaker1.extractActualRoutesMaster( getRoutesResult )
        allRoutesStrExpected = str( sorted( allRoutesExpected ) )
        allRoutesStrActual = str( allRoutesActual ).replace( 'u', "" )

        main.step( "Check routes installed" )
        main.log.info( "Routes expected:" )
        main.log.info( allRoutesStrExpected )
        main.log.info( "Routes get from ONOS CLI:" )
        main.log.info( allRoutesStrActual )
        utilities.assertEquals( \
            expect = allRoutesStrExpected, actual = allRoutesStrActual,
            onpass = "***Routes in SDN-IP are correct!***",
            onfail = "***Routes in SDN-IP are wrong!***" )

        main.step( "Check MultiPointToSinglePointIntent intents installed" )
        getIntentsResult = main.ONOScli.intents( jsonFormat = True )
        routeIntentsActualNum = \
            main.QuaggaCliSpeaker1.extractActualRouteIntentNum( getIntentsResult )
        routeIntentsExpectedNum = 3

        main.log.info( "MultiPointToSinglePoint Intent Num expected is:" )
        main.log.info( routeIntentsExpectedNum )
        main.log.info( "MultiPointToSinglePoint Intent NUM Actual is:" )
        main.log.info( routeIntentsActualNum )
        utilities.assertEquals( \
            expect = True,
            actual = eq( routeIntentsExpectedNum, routeIntentsActualNum ),
            onpass = "***MultiPointToSinglePoint Intent Num in SDN-IP is \
            correct!***",
            onfail = "***MultiPointToSinglePoint Intent Num in SDN-IP is \
            wrong!***" )


    def CASE4( self, main ):
        '''
        Ping test in data plane for each route
        '''
        main.case( "This case is to check ping for each route" )
        result1 = main.Mininet.pingHost( src = "host64514", target = "host64515" )
        result2 = main.Mininet.pingHost( src = "host64515", target = "host64516" )
        result3 = main.Mininet.pingHost( src = "host64514", target = "host64516" )

        caseResult = result1 and result2 and result3
        utilities.assert_equals( expect = main.TRUE, actual = caseResult,
                                 onpass = "Ping test for each route successful",
                                 onfail = "Ping test for each route NOT successful" )

        if caseResult == main.FALSE:
            main.cleanup()
            main.exit()


    def CASE5( self, main ):
        '''
        Cut links to peers one by one, check routes/intents
        '''
        import time
        main.case( "This case is to bring down links and check routes/intents" )
        main.step( "Bring down the link between sw32 and peer64514" )
        result = main.Mininet.link( END1 = "sw32", END2 = "peer64514",
                                    OPTION = "down" )
        if result == main.TRUE:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, 2 )
            main.Functions.checkM2SintentNum( main, 2 )
        else:
            main.log.info( "Bring down link failed!!!" )
            main.exit();

        main.step( "Bring down the link between sw8 and peer64515" )
        result = main.Mininet.link( END1 = "sw8", END2 = "peer64515",
                                    OPTION = "down" )
        if result == main.TRUE:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, 1 )
            main.Functions.checkM2SintentNum( main, 1 )
        else:
            main.log.info( "Bring down link failed!!!" )
            main.exit();

        main.step( "Bring down the link between sw28 and peer64516" )
        result = main.Mininet.link( END1 = "sw28", END2 = "peer64516",
                                    OPTION = "down" )
        if result == main.TRUE:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, 0 )
            main.Functions.checkM2SintentNum( main, 0 )
        else:
            main.log.info( "Bring down link failed!!!" )
            main.exit();


    def CASE6(self, main):
        '''
        Recover links to peers one by one, check routes/intents
        '''
        import time
        main.case( "This case is to bring up links and check routes/intents" )
        main.step( "Bring up the link between sw32 and peer64514" )
        result = main.Mininet.link( END1 = "sw32", END2 = "peer64514",
                                    OPTION = "up" )
        if result == main.TRUE:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, 1 )
            main.Functions.checkM2SintentNum( main, 1 )
        else:
            main.log.info( "Bring up link failed!!!" )
            main.exit();

        main.step( "Bring up the link between sw8 and peer64515" )
        result = main.Mininet.link( END1 = "sw8", END2 = "peer64515",
                                    OPTION = "up" )
        if result == main.TRUE:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, 2 )
            main.Functions.checkM2SintentNum( main, 2 )
        else:
            main.log.info( "Bring up link failed!!!" )
            main.exit();

        main.step( "Bring up the link between sw28 and peer64516" )
        result = main.Mininet.link( END1 = "sw28", END2 = "peer64516",
                                    OPTION = "up" )
        if result == main.TRUE:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, 3 )
            main.Functions.checkM2SintentNum( main, 3 )
        else:
            main.log.info( "Bring up link failed!!!" )
            main.exit();
        '''
        Note: at the end of this test case, we should carry out ping test.
        So we run CASE4 again after CASE6
        '''


    def CASE7(self, main):
        '''
        shut down a edge switch, check P-2-P and M-2-S intents, ping test
        '''
        import time
        main.case( "This case is to stop 1 edge switch,\
        check P-2-P and M-2-S intents, ping test")
        main.step( "Stop sw32" )
        result = main.Mininet.switch( SW = "sw32", OPTION = "stop" )
        if result == main.TRUE:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, 2 )
            main.Functions.checkM2SintentNum( main, 2 )
            main.Functions.checkP2PintentNum( main, 12 )
        else:
            main.log.info( "Stop switch failed!!!" )
            main.exit();

        '''
        main.step( "Stop sw8" )
        result = main.Mininet.switch( SW = "sw8", OPTION = "stop" )
        if result == main.TRUE:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, 1 )

            # Note: there should be 0 M2S intent, not 1.
            main.Functions.checkM2SintentNum( main, 0 )
            main.Functions.checkP2PintentNum( main, 6 )
        else:
            main.log.info( "Stop switch failed!!!" )
            main.exit();

        main.step( "Stop sw28" )
        result = main.Mininet.switch( SW = "sw28", OPTION = "stop" )
        if result == main.TRUE:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, 0 )
            main.Functions.checkM2SintentNum( main, 0 )
            main.Functions.checkP2PintentNum( main, 0 )
        else:
            main.log.info( "Stop switch failed!!!" )
            main.exit();
        '''
        '''
        ping test between BGP speaker and BGP peers, ping test between hosts
        behind BGP peers ===
        '''

    def CASE8( self, main ):
        main.case( "This case is to bring up 1 edge switch,\
        check P-2-P and M-2-S intents, ping test" )


    def CASE20( self, main ):
        '''
        ping test from 3 bgp peers to BGP speaker
        '''
        main.case( "This case is to check ping between BGP peers and speakers" )
        result1 = main.Mininet.pingHost( src = "speaker1", target = "peer64514" )
        result2 = main.Mininet.pingHost( src = "speaker1", target = "peer64515" )
        result3 = main.Mininet.pingHost( src = "speaker1", target = "peer64516" )


        caseResult = result1 or result2 or result3
        utilities.assert_equals( expect = main.FALSE, actual = caseResult,
                                 onpass = "Speaker1 failed to ping all peers - Correct",
                                 onfail = "Speaker1 did not fail to ping all peers- NOT Correct" )

        if caseResult == main.TRUE:
            main.cleanup()
            main.exit()


    def CASE21( self, main ):
        '''
        Ping test in data plane for each route
        '''
        main.case( "This case is to check ping for each route" )
        result1 = main.Mininet.pingHost( src = "host64514", target = "host64515" )
        result2 = main.Mininet.pingHost( src = "host64515", target = "host64516" )
        result3 = main.Mininet.pingHost( src = "host64514", target = "host64516" )

        caseResult = result1 or result2 or result3
        utilities.assert_equals( expect = main.FALSE, actual = caseResult,
                                 onpass = "Ping test for all routes failed- Correct",
                                 onfail = "Ping test for all routes NOT failed- NOT Correct" )

        if caseResult == main.TRUE:
            main.cleanup()
            main.exit()

