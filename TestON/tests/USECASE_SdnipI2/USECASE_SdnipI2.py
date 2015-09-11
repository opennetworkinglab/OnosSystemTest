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


    def CASE1( self, main ):
        '''
        ping test from 3 bgp peers to BGP speaker
        '''
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

