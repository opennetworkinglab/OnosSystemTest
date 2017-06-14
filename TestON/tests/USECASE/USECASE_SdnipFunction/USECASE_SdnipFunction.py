# Testing the functionality of SDN-IP with single ONOS instance
class USECASE_SdnipFunction:

    def __init__( self ):
        self.default = ''
        global branchName

    def CASE100( self, main ):
        """
            Start mininet
        """
        import os
        main.case( "Setup the Mininet testbed" )
        main.dependencyPath = main.testDir + \
                              main.params[ 'DEPENDENCY' ][ 'path' ]
        main.topology = main.params[ 'DEPENDENCY' ][ 'topology' ]

        main.step( "Starting Mininet Topology" )
        topology = main.dependencyPath + main.topology
        topoResult = main.Mininet.startNet( topoFile=topology )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=topoResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanup()
            main.exit()
        main.step( "Connect switches to controller" )

        global ONOS1Ip
        ONOS1Ip = os.getenv( main.params[ 'CTRL' ][ 'ip1' ] )
        # connect all switches to controller
        swResult = main.TRUE
        for i in range ( 1, int( main.params['config']['switchNum'] ) + 1 ):
            sw = "sw%s" % ( i )
            swResult = swResult and main.Mininet.assignSwController( sw, ONOS1Ip )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=swResult,
                                 onpass="Successfully connect all switches to ONOS",
                                 onfail="Failed to connect all switches to ONOS" )
        if not swResult:
            main.cleanup()
            main.exit()

        main.step( "Set up tunnel from Mininet node to onos node" )
        forwarding1 = '%s:2000:%s:2000' % ( '1.1.1.2', ONOS1Ip )
        command = 'ssh -nNT -o "PasswordAuthentication no" \
        -o "StrictHostKeyChecking no" -l sdn -L %s %s & ' % ( forwarding1, ONOS1Ip )

        tunnelResult = main.TRUE
        tunnelResult = main.Mininet.node( "root", command )
        utilities.assert_equals( expect=True,
                                 actual=( "PasswordAuthentication" in tunnelResult ),
                                 onpass="Created tunnel succeeded",
                                 onfail="Create tunnel failed" )
        if ("PasswordAuthentication" not in tunnelResult) :
            main.cleanup()
            main.exit()

    def CASE101( self, main ):
        """
           Package ONOS and install it
           Startup sequence:
           cell <name>
           onos-verify-cell
           onos-package
           onos-install -f
           onos-wait-for-start
        """
        import time
        import os

        main.case( "Setting up ONOS environment" )

        cellName = main.params[ 'ENV' ][ 'cellName' ]
        global ONOS1Ip
        ONOS1Ip = os.getenv( main.params[ 'CTRL' ][ 'ip1' ] )
        ipList = [ ONOS1Ip ]

        main.step( "Copying config files" )
        src = os.path.dirname( main.testFile ) + "/network-cfg.json"
        dst = main.ONOSbench.home + "/tools/package/config/network-cfg.json"
        status = main.ONOSbench.scp( main.ONOSbench, src, dst, direction="to" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=status,
                                 onpass="Copy config file succeeded",
                                 onfail="Copy config file failed" )

        main.step( "Create cell file" )
        cellAppString = main.params[ 'ENV' ][ 'appString' ]
        main.ONOSbench.createCellFile( main.ONOSbench.ip_address, cellName,
                                       main.Mininet.ip_address,
                                       cellAppString, ipList, main.ONOScli1.karafUser )

        main.step( "Applying cell variable to environment" )
        cellResult = main.ONOSbench.setCell( cellName )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=cellResult,
                                 onpass="Set cell succeeded",
                                 onfail="Set cell failed" )

        main.step( "Verify cell connectivity" )
        verifyResult = main.ONOSbench.verifyCell()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=verifyResult,
                                 onpass="Verify cell succeeded",
                                 onfail="Verify cell failed" )

        branchName = main.ONOSbench.getBranchName()
        main.log.report( "ONOS is on branch: " + branchName )

        main.step( "Uninstalling ONOS" )
        uninstallResult = main.ONOSbench.onosUninstall( ONOS1Ip )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=uninstallResult,
                                 onpass="Uninstall ONOS succeeded",
                                 onfail="Uninstall ONOS failed" )
        '''
        main.step( "Git pull" )
        gitPullResult = main.ONOSbench.gitPull()
        main.log.info( "gitPullResult" )
        main.log.info( gitPullResult )
        gitPullResult2 = ( gitPullResult == main.TRUE ) or ( gitPullResult == 3 )
        utilities.assert_equals( expect=True,
                                 actual=gitPullResult2,
                                 onpass="Git pull ONOS succeeded",
                                 onfail="Git pull ONOS failed" )
        '''

        main.ONOSbench.getVersion( report=True )

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.buckBuild()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=packageResult,
                                 onpass="Package ONOS succeeded",
                                 onfail="Package ONOS failed" )

        main.step( "Installing ONOS package" )
        onos1InstallResult = main.ONOSbench.onosInstall( options="-f",
                                                         node=ONOS1Ip )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=onos1InstallResult,
                                 onpass="Install ONOS succeeded",
                                 onfail="Install ONOS failed" )

        main.step( "Set up ONOS secure SSH" )
        secureSshResult = main.ONOSbench.onosSecureSSH( node=ONOS1Ip )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=secureSshResult,
                                 onpass="Set up ONOS secure SSH succeeded",
                                 onfail="Set up ONOS secure SSH failed " )

        main.step( "Checking if ONOS is up yet" )
        onos1UpResult = main.ONOSbench.isup( ONOS1Ip, timeout=420 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=onos1UpResult,
                                 onpass="ONOS is up",
                                 onfail="ONOS is NOT up" )

        main.step( "Checking if ONOS CLI is ready" )
        cliResult = main.ONOScli.startOnosCli( ONOS1Ip,
                commandlineTimeout=100, onosStartTimeout=600 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=cliResult,
                                 onpass="ONOS CLI is ready",
                                 onfail="ONOS CLI is not ready" )

        for i in range( 10 ):
            ready = True
            output = main.ONOScli.summary()
            if not output:
                ready = False
            if ready:
                break
            time.sleep( 30 )
        utilities.assert_equals( expect=True, actual=ready,
                                 onpass="ONOS summary command succeded",
                                 onfail="ONOS summary command failed" )

        if not ready:
            main.log.error( "ONOS startup failed!" )
            main.cleanup()
            main.exit()

    def CASE200( self, main ):
        import json
        import time

        main.case( "Activate sdn-ip application" )
        main.log.info( "waiting link discovery......" )
        time.sleep( int( main.params['timers']['TopoDiscovery'] ) )

        main.log.info( "Get links in the network" )
        summaryResult = main.ONOScli.summary()
        linkNum = json.loads( summaryResult )[ "links" ]
        listResult = main.ONOScli.links( jsonFormat=False )
        main.log.info( listResult )
        if linkNum < 100:
            main.log.error( "Link number is wrong!" )
            time.sleep( int( main.params['timers']['TopoDiscovery'] ) )
            listResult = main.ONOScli.links( jsonFormat=False )
            main.log.info( listResult )
            main.cleanup()
            main.exit()

        main.step( "Activate sdn-ip application" )
        activeSDNIPresult = main.ONOScli.activateApp( "org.onosproject.sdnip" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=activeSDNIPresult,
                                 onpass="Activate SDN-IP succeeded",
                                 onfail="Activate SDN-IP failed" )
        if not activeSDNIPresult:
            main.log.info( "Activate SDN-IP failed!" )
            main.cleanup()
            main.exit()


        main.log.info( "Wait SDN-IP to finish installing connectivity intents \
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
        import imp

        main.case( "Loading methods from other Python file" )
        # load the methods from other file
        wrapperFile = main.params[ 'DEPENDENCY' ][ 'wrapper1' ]
        main.Functions = imp.load_source( wrapperFile,
                                          main.dependencyPath +
                                          wrapperFile +
                                          ".py" )


    def CASE1( self, main ):
        '''
        ping test from 7 bgp peers to BGP speaker
        '''

        main.case( "Ping tests between BGP peers and speakers" )
        main.Functions.pingSpeakerToPeer( main, speakers=[ "spk1" ],
                                          peers=[ "p64514", "p64515", "p64516" ],
                                          expectAllSuccess=True )

        main.Functions.pingSpeakerToPeer( main, speakers=[ "spk2" ],
                                          peers=[ "p64517", "p64518" ],
                                          expectAllSuccess=True )

        main.Functions.pingSpeakerToPeer( main, speakers=[ "spk3" ],
                                          peers=[ "p64519", "p64520" ],
                                          expectAllSuccess=True )

    def CASE2( self, main ):
        '''
        point-to-point intents test for each BGP peer and BGP speaker pair
        '''
        import time
        from operator import eq

        main.case( "Check point-to-point intents" )
        main.log.info( "There are %s BGP peers in total "
                       % main.params[ 'config' ][ 'peerNum' ] )
        main.step( "Check P2P intents number from ONOS CLI" )

        getIntentsResult = main.ONOScli.intents( jsonFormat=True )
        bgpIntentsActualNum = \
            main.QuaggaCliSpeaker1.extractActualBgpIntentNum( getIntentsResult )
        bgpIntentsExpectedNum = int( main.params[ 'config' ][ 'peerNum' ] ) * 6
        if bgpIntentsActualNum != bgpIntentsExpectedNum:
            time.sleep( int( main.params['timers']['RouteDelivery'] ) )
            getIntentsResult = main.ONOScli.intents( jsonFormat=True )
            bgpIntentsActualNum = \
                main.QuaggaCliSpeaker1.extractActualBgpIntentNum( getIntentsResult )
        main.log.info( "bgpIntentsExpected num is:" )
        main.log.info( bgpIntentsExpectedNum )
        main.log.info( "bgpIntentsActual num is:" )
        main.log.info( bgpIntentsActualNum )
        utilities.assertEquals( \
            expect=True,
            actual=eq( bgpIntentsExpectedNum, bgpIntentsActualNum ),
            onpass="PointToPointIntent Intent Num is correct!",
            onfail="PointToPointIntent Intent Num is wrong!" )


    def CASE3( self, main ):
        '''
        routes and intents check to all BGP peers
        '''
        import time
        main.case( "Check routes and M2S intents to all BGP peers" )

        allRoutesExpected = []
        allRoutesExpected.append( "4.0.0.0/24" + "/" + "10.0.4.1" )
        allRoutesExpected.append( "5.0.0.0/24" + "/" + "10.0.5.1" )
        allRoutesExpected.append( "6.0.0.0/24" + "/" + "10.0.6.1" )

        allRoutesExpected.append( "7.0.0.0/24" + "/" + "10.0.7.1" )
        allRoutesExpected.append( "8.0.0.0/24" + "/" + "10.0.8.1" )
        allRoutesExpected.append( "9.0.0.0/24" + "/" + "10.0.9.1" )
        allRoutesExpected.append( "20.0.0.0/24" + "/" + "10.0.20.1" )

        getRoutesResult = main.ONOScli.routes( jsonFormat=True )
        allRoutesActual = \
            main.QuaggaCliSpeaker1.extractActualRoutesMaster( getRoutesResult )
        allRoutesStrExpected = str( sorted( allRoutesExpected ) )
        allRoutesStrActual = str( allRoutesActual ).replace( 'u', "" )
        if allRoutesStrActual != allRoutesStrExpected:
            time.sleep( int( main.params['timers']['RouteDelivery'] ) )
            getRoutesResult = main.ONOScli.routes( jsonFormat=True )
            allRoutesActual = \
                main.QuaggaCliSpeaker1.extractActualRoutesMaster( getRoutesResult )
            allRoutesStrActual = str( allRoutesActual ).replace( 'u', "" )

        main.step( "Check routes installed" )
        main.log.info( "Routes expected:" )
        main.log.info( allRoutesStrExpected )
        main.log.info( "Routes get from ONOS CLI:" )
        main.log.info( allRoutesStrActual )
        utilities.assertEquals( \
            expect=allRoutesStrExpected, actual=allRoutesStrActual,
            onpass="Routes are correct!",
            onfail="Routes are wrong!" )

        main.step( "Check M2S intents installed" )
        getIntentsResult = main.ONOScli.intents( jsonFormat=True )
        routeIntentsActualNum = \
            main.QuaggaCliSpeaker1.extractActualRouteIntentNum( getIntentsResult )
        routeIntentsExpectedNum = 7
        if routeIntentsActualNum != routeIntentsExpectedNum:
            time.sleep( int( main.params['timers']['RouteDelivery'] ) )
            getIntentsResult = main.ONOScli.intents( jsonFormat=True )
            routeIntentsActualNum = \
                main.QuaggaCliSpeaker1.extractActualRouteIntentNum( getIntentsResult )

        main.log.info( "MultiPointToSinglePoint Intent Num expected is:" )
        main.log.info( routeIntentsExpectedNum )
        main.log.info( "MultiPointToSinglePoint Intent NUM Actual is:" )
        main.log.info( routeIntentsActualNum )
        utilities.assertEquals( \
            expect=routeIntentsExpectedNum,
            actual=routeIntentsActualNum,
            onpass="MultiPointToSinglePoint Intent Num is correct!",
            onfail="MultiPointToSinglePoint Intent Num is wrong!" )

        main.step( "Check whether all flow status are ADDED" )
        flowCheck = utilities.retry( main.ONOScli.checkFlowsState,
                                     main.FALSE,
                                     kwargs={'isPENDING':False},
                                     attempts=10 )
        utilities.assertEquals( \
            expect=main.TRUE,
            actual=flowCheck,
            onpass="Flow status is correct!",
            onfail="Flow status is wrong!" )


    def CASE4( self, main ):
        '''
        Ping test in data plane for each route
        '''
        main.case( "Ping test for each route, all hosts behind BGP peers" )
        #No vlan
        main.Functions.pingHostToHost( main,
                                       hosts=[ "h64514", "h64515", "h64516" ],
                                       expectAllSuccess=True )
        #vlan 10
        main.Functions.pingHostToHost( main,
                                       hosts=[ "h64519", "h64520" ],
                                       expectAllSuccess=True )

        # vlan 20
        main.Functions.pingHostToHost( main,
                                       hosts=[ "h64517", "h64518" ],
                                       expectAllSuccess=True )

    def CASE5( self, main ):
        '''
        Cut links to peers one by one, check routes/intents
        '''
        import time
        main.case( "Bring down links and check routes/intents" )
        main.step( "Bring down the link between sw32 and p64514" )
        linkResult1 = main.Mininet.link( END1="sw32", END2="p64514",
                                         OPTION="down" )
        utilities.assertEquals( expect=main.TRUE,
                                actual=linkResult1,
                                onpass="Bring down link succeeded!",
                                onfail="Bring down link failed!" )

        if linkResult1 == main.TRUE:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, 6 ) #We have 7 links between peers and sw. After one link down, 7-1=6.
            main.Functions.checkM2SintentNum( main, 6 )
        else:
            main.log.error( "Bring down link failed!" )
            main.cleanup()
            main.exit()

        main.step( "Bring down the link between sw8 and p64515" )
        linkResult2 = main.Mininet.link( END1="sw8", END2="p64515",
                                         OPTION="down" )
        utilities.assertEquals( expect=main.TRUE,
                                actual=linkResult2,
                                onpass="Bring down link succeeded!",
                                onfail="Bring down link failed!" )
        if linkResult2 == main.TRUE:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, 5 ) #2 links down, 7-2=5.
            main.Functions.checkM2SintentNum( main, 5 )
        else:
            main.log.error( "Bring down link failed!" )
            main.cleanup()
            main.exit()

        main.step( "Bring down the link between sw28 and p64516" )
        linkResult3 = main.Mininet.link( END1="sw28", END2="p64516",
                                         OPTION="down" )
        utilities.assertEquals( expect=main.TRUE,
                                actual=linkResult3,
                                onpass="Bring down link succeeded!",
                                onfail="Bring down link failed!" )
        if linkResult3 == main.TRUE:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, 4 ) #3 links downs 7-3=4
            main.Functions.checkM2SintentNum( main, 4 )
        else:
            main.log.error( "Bring down link failed!" )
            main.cleanup()
            main.exit()

        main.step( "Check whether all flow status are ADDED" )
        flowCheck = utilities.retry( main.ONOScli.checkFlowsState,
                                     main.FALSE,
                                     kwargs={'isPENDING':False},
                                     attempts=10 )
        utilities.assertEquals( \
            expect=main.TRUE,
            actual=flowCheck,
            onpass="Flow status is correct!",
            onfail="Flow status is wrong!" )

        # Ping test
        main.Functions.pingSpeakerToPeer( main, speakers=["spk1"],
                                          peers=["p64514", "p64515", "p64516"],
                                          expectAllSuccess=False )

        main.Functions.pingHostToHost( main,
                                       hosts=["h64514", "h64515", "h64516"],
                                       expectAllSuccess=False )


    def CASE6( self, main ):
        '''
        Recover links to peers one by one, check routes/intents
        '''
        import time
        main.case( "Bring up links and check routes/intents" )
        main.step( "Bring up the link between sw32 and p64514" )
        linkResult1 = main.Mininet.link( END1="sw32", END2="p64514",
                                         OPTION="up" )
        utilities.assertEquals( expect=main.TRUE,
                                actual=linkResult1,
                                onpass="Bring up link succeeded!",
                                onfail="Bring up link failed!" )
        if linkResult1 == main.TRUE:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, 5 ) #one links up, 4+1=5
            main.Functions.checkM2SintentNum( main, 5 )
        else:
            main.log.error( "Bring up link failed!" )
            main.cleanup()
            main.exit()

        main.step( "Bring up the link between sw8 and p64515" )
        linkResult2 = main.Mininet.link( END1="sw8", END2="p64515",
                                         OPTION="up" )
        utilities.assertEquals( expect=main.TRUE,
                                actual=linkResult2,
                                onpass="Bring up link succeeded!",
                                onfail="Bring up link failed!" )
        if linkResult2 == main.TRUE:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, 6 )
            main.Functions.checkM2SintentNum( main, 6 )
        else:
            main.log.error( "Bring up link failed!" )
            main.cleanup()
            main.exit()

        main.step( "Bring up the link between sw28 and p64516" )
        linkResult3 = main.Mininet.link( END1="sw28", END2="p64516",
                                         OPTION="up" )
        utilities.assertEquals( expect=main.TRUE,
                                actual=linkResult3,
                                onpass="Bring up link succeeded!",
                                onfail="Bring up link failed!" )
        if linkResult3 == main.TRUE:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, 7 )
            main.Functions.checkM2SintentNum( main, 7 )
        else:
            main.log.error( "Bring up link failed!" )
            main.cleanup()
            main.exit()

        main.step( "Check whether all flow status are ADDED" )
        flowCheck = utilities.retry( main.ONOScli.checkFlowsState,
                                     main.FALSE,
                                     kwargs={'isPENDING':False},
                                     attempts=10 )
        utilities.assertEquals( \
            expect=main.TRUE,
            actual=flowCheck,
            onpass="Flow status is correct!",
            onfail="Flow status is wrong!" )

        # Ping test
        main.Functions.pingSpeakerToPeer( main, speakers=["spk1"],
                       peers=["p64514", "p64515", "p64516"],
                       expectAllSuccess=True )
        main.Functions.pingHostToHost( main,
                        hosts=["h64514", "h64515", "h64516"],
                        expectAllSuccess=True )


    def CASE7( self, main ):
        '''
        Shut down a edge switch, check P-2-P and M-2-S intents, ping test
        '''
        import time
        main.case( "Stop edge sw32,check P-2-P and M-2-S intents, ping test" )
        main.step( "Stop sw32" )
        result = main.Mininet.switch( SW="sw32", OPTION="stop" )
        utilities.assertEquals( expect=main.TRUE, actual=result,
                                onpass="Stopping switch succeeded!",
                                onfail="Stopping switch failed!" )

        if result == main.TRUE:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, 6 ) #stop one sw, which bring one link between peer and sw down.
            main.Functions.checkM2SintentNum( main, 6 )
            main.Functions.checkP2PintentNum( main, 36 ) #6 intents from sw to speakers x 6 intents to sw x 2 intents between them
        else:
            main.log.error( "Stopping switch failed!" )
            main.cleanup()
            main.exit()

        main.step( "Check ping between hosts behind BGP peers" )
        result1 = main.Mininet.pingHost( src="h64514", target="h64515" )
        result2 = main.Mininet.pingHost( src="h64515", target="h64516" )
        result3 = main.Mininet.pingHost( src="h64514", target="h64516" )

        pingResult1 = ( result1 == main.FALSE ) and ( result2 == main.TRUE ) \
                                                and ( result3 == main.FALSE )
        utilities.assert_equals( expect=True, actual=pingResult1,
                                 onpass="Ping test result is correct",
                                 onfail="Ping test result is wrong" )

        if pingResult1 == False:
            main.cleanup()
            main.exit()

        main.step( "Check ping between BGP peers and speakers" )
        result4 = main.Mininet.pingHost( src="spk1", target="p64514" )
        result5 = main.Mininet.pingHost( src="spk1", target="p64515" )
        result6 = main.Mininet.pingHost( src="spk1", target="p64516" )

        pingResult2 = ( result4 == main.FALSE ) and ( result5 == main.TRUE ) \
                                                and ( result6 == main.TRUE )
        utilities.assert_equals( expect=True, actual=pingResult2,
                                 onpass="Speaker1 ping peers successful",
                                 onfail="Speaker1 ping peers NOT successful" )

        if pingResult2 == False:
            main.cleanup()
            main.exit()

        main.step( "Check whether all flow status are ADDED" )
        flowCheck = utilities.retry( main.ONOScli.checkFlowsState,
                                     main.FALSE,
                                     kwargs={'isPENDING':False},
                                     attempts=10 )
        utilities.assertEquals( \
            expect=main.TRUE,
            actual=flowCheck,
            onpass="Flow status is correct!",
            onfail="Flow status is wrong!" )


    def CASE8( self, main ):
        '''
        Bring up the edge switch (sw32) which was shut down in CASE7,
        check P-2-P and M-2-S intents, ping test
        '''
        import time
        main.case( "Start the edge sw32, check P-2-P and M-2-S intents, ping test" )
        main.step( "Start sw32" )
        result1 = main.Mininet.switch( SW="sw32", OPTION="start" )
        utilities.assertEquals( \
            expect=main.TRUE,
            actual=result1,
            onpass="Starting switch succeeded!",
            onfail="Starting switch failed!" )

        result2 = main.Mininet.assignSwController( "sw32", ONOS1Ip )
        utilities.assertEquals( \
            expect=main.TRUE,
            actual=result2,
            onpass="Connect switch to ONOS succeeded!",
            onfail="Connect switch to ONOS failed!" )

        if result1 and result2:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, 7 )
            main.Functions.checkM2SintentNum( main, 7 )
            main.Functions.checkP2PintentNum( main, 42 )
        else:
            main.log.error( "Starting switch failed!" )
            main.cleanup()
            main.exit()

        main.step( "Check whether all flow status are ADDED" )
        flowCheck = utilities.retry( main.ONOScli.checkFlowsState,
                                     main.FALSE,
                                     kwargs={'isPENDING':False},
                                     attempts=10 )
        utilities.assertEquals( \
            expect=main.TRUE,
            actual=flowCheck,
            onpass="Flow status is correct!",
            onfail="Flow status is wrong!" )

        # Ping test
        main.Functions.pingSpeakerToPeer( main, speakers=["spk1"],
                       peers=["p64514", "p64515", "p64516"],
                       expectAllSuccess=True )
        main.Functions.pingHostToHost( main,
                        hosts=["h64514", "h64515", "h64516"],
                        expectAllSuccess=True )


    def CASE9( self, main ):
        '''
        Bring down a switch in best path, check:
        route number, P2P intent number, M2S intent number, ping test
        '''
        main.case( "Stop sw11 located in best path, \
        check route number, P2P intent number, M2S intent number, ping test" )

        main.log.info( "Check the flow number correctness before stopping sw11" )
        main.Functions.checkFlowNum( main, "sw11", 43 )
        main.Functions.checkFlowNum( main, "sw1", 3 )
        main.Functions.checkFlowNum( main, "sw7", 34 )
        main.log.debug( main.Mininet.checkFlows( "sw11" ) )
        main.log.debug( main.Mininet.checkFlows( "sw1" ) )
        main.log.debug( main.Mininet.checkFlows( "sw7" ) )

        main.step( "Stop sw11" )
        result = main.Mininet.switch( SW="sw11", OPTION="stop" )
        utilities.assertEquals( expect=main.TRUE, actual=result,
                                onpass="Stopping switch succeeded!",
                                onfail="Stopping switch failed!" )
        if result:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, 7 )
            main.Functions.checkM2SintentNum( main, 7 )
            main.Functions.checkP2PintentNum( main, 42 )
        else:
            main.log.error( "Stopping switch failed!" )
            main.cleanup()
            main.exit()

        main.step( "Check whether all flow status are ADDED" )
        flowCheck = utilities.retry( main.ONOScli.checkFlowsState,
                                     main.FALSE,
                                     kwargs={'isPENDING':False},
                                     attempts=10 )
        utilities.assertEquals( \
            expect=main.TRUE,
            actual=flowCheck,
            onpass="Flow status is correct!",
            onfail="Flow status is wrong!" )
        # Ping test
        main.Functions.pingSpeakerToPeer( main, speakers=["spk1"],
                       peers=["p64514", "p64515", "p64516"],
                       expectAllSuccess=True )
        main.Functions.pingHostToHost( main,
                        hosts=["h64514", "h64515", "h64516"],
                        expectAllSuccess=True )


    def CASE10( self, main ):
        '''
        Bring up the switch which was stopped in CASE9, check:
        route number, P2P intent number, M2S intent number, ping test
        '''
        main.case( "Start sw11 which was stopped in CASE9, \
        check route number, P2P intent number, M2S intent number, ping test" )

        main.log.info( "Check the flow status before starting sw11" )
        main.Functions.checkFlowNum( main, "sw1", 33 )
        main.Functions.checkFlowNum( main, "sw7", 28 )
        main.log.debug( main.Mininet.checkFlows( "sw1" ) )
        main.log.debug( main.Mininet.checkFlows( "sw7" ) )

        main.step( "Start sw11" )
        result1 = main.Mininet.switch( SW="sw11", OPTION="start" )
        utilities.assertEquals( expect=main.TRUE, actual=result1,
                                onpass="Starting switch succeeded!",
                                onfail="Starting switch failed!" )
        result2 = main.Mininet.assignSwController( "sw11", ONOS1Ip )
        utilities.assertEquals( expect=main.TRUE, actual=result2,
                                onpass="Connect switch to ONOS succeeded!",
                                onfail="Connect switch to ONOS failed!" )
        if result1 and result2:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, 7 )
            main.Functions.checkM2SintentNum( main, 7 )
            main.Functions.checkP2PintentNum( main, 42 )

            main.log.debug( main.Mininet.checkFlows( "sw11" ) )
            main.log.debug( main.Mininet.checkFlows( "sw1" ) )
            main.log.debug( main.Mininet.checkFlows( "sw7" ) )
        else:
            main.log.error( "Starting switch failed!" )
            main.cleanup()
            main.exit()

        main.step( "Check whether all flow status are ADDED" )
        flowCheck = utilities.retry( main.ONOScli.checkFlowsState,
                                     main.FALSE,
                                     kwargs={'isPENDING':False},
                                     attempts=10 )
        utilities.assertEquals( \
            expect=main.TRUE,
            actual=flowCheck,
            onpass="Flow status is correct!",
            onfail="Flow status is wrong!" )
        # Ping test
        main.Functions.pingSpeakerToPeer( main, speakers=["spk1"],
                       peers=["p64514", "p64515", "p64516"],
                       expectAllSuccess=True )
        main.Functions.pingHostToHost( main,
                        hosts=["h64514", "h64515", "h64516"],
                        expectAllSuccess=True )
