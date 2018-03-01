"""
Copyright 2016 Open Networking Foundation ( ONF )

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    ( at your option ) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.
"""
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
        main.dependencyPath = main.testsRoot + \
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
            main.cleanAndExit()
        main.step( "Connect switches to controller" )

        # connect all switches to controller
        swResult = main.TRUE
        for i in range( 1, int( main.params[ 'config' ][ 'switchNum' ] ) + 1 ):
            sw = "sw%s" % ( i )
            swResult = swResult and \
                       main.Mininet.assignSwController( sw, main.Cluster.active( 0 ).ipAddress )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=swResult,
                                 onpass="Successfully connect all switches to ONOS",
                                 onfail="Failed to connect all switches to ONOS" )
        if not swResult:
            main.cleanAndExit()

        main.step( "Set up tunnel from Mininet node to onos node" )
        forwarding1 = '%s:2000:%s:2000' % ( '1.1.1.2', main.Cluster.active( 0 ).ipAddress )
        command = 'ssh -nNT -o "PasswordAuthentication no" \
        -o "StrictHostKeyChecking no" -l sdn -L %s %s & ' % \
                  ( forwarding1, main.Cluster.active( 0 ).ipAddress )

        tunnelResult = main.TRUE
        tunnelResult = main.Mininet.node( "root", command )
        utilities.assert_equals( expect=True,
                                 actual=( "PasswordAuthentication" in tunnelResult ),
                                 onpass="Created tunnel succeeded",
                                 onfail="Create tunnel failed" )
        if ( "PasswordAuthentication" not in tunnelResult ):
            main.cleanAndExit()

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
        try:
            from tests.USECASE.dependencies.sdnipBaseFunction import SdnBase
        except ImportError:
            main.log.error( "sdnBase not found. exiting the test" )
            main.cleanAndExit()
        try:
            main.sdnBase
        except ( NameError, AttributeError ):
            main.sdnBase = SdnBase()

        main.sdnBase.initSetup()

    def CASE200( self, main ):
        import json
        import time

        main.case( "Activate sdn-ip application" )
        main.log.info( "waiting link discovery......" )
        time.sleep( int( main.params[ 'timers' ][ 'TopoDiscovery' ] ) )

        main.log.info( "Get links in the network" )
        summaryResult = main.Cluster.active( 0 ).CLI.summary()
        linkNum = json.loads( summaryResult )[ "links" ]
        listResult = main.Cluster.active( 0 ).CLI.links( jsonFormat=False )
        main.log.info( listResult )
        if linkNum < 100:
            main.log.error( "Link number is wrong!" )
            time.sleep( int( main.params[ 'timers' ][ 'TopoDiscovery' ] ) )
            listResult = main.Cluster.active( 0 ).CLI.links( jsonFormat=False )
            main.log.info( listResult )
            main.cleanAndExit()

        main.step( "Activate sdn-ip application" )
        activeSDNIPresult = main.Cluster.active( 0 ).CLI.activateApp( "org.onosproject.sdnip" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=activeSDNIPresult,
                                 onpass="Activate SDN-IP succeeded",
                                 onfail="Activate SDN-IP failed" )
        if not activeSDNIPresult:
            main.log.info( "Activate SDN-IP failed!" )
            main.cleanAndExit()

        main.log.info( "Wait SDN-IP to finish installing connectivity intents \
        and the BGP paths in data plane are ready..." )
        time.sleep( int( main.params[ 'timers' ][ 'SdnIpSetup' ] ) )
        main.log.info( "Wait Quagga to finish delivery all routes to each \
        other and to sdn-ip, plus finish installing all intents..." )
        time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
        time.sleep( int( main.params[ 'timers' ][ 'PathAvailable' ] ) )

    def CASE102( self, main ):
        """
        This test case is to load the methods from other Python files.
        """
        import imp

        main.case( "Loading methods from other Python file" )
        # load the methods from other file
        wrapperFile = main.params[ 'DEPENDENCY' ][ 'wrapper1' ]
        main.Functions = imp.load_source( wrapperFile,
                                          main.dependencyPath +
                                          wrapperFile +
                                          ".py" )

    def CASE1( self, main ):
        """
        ping test from 7 bgp peers to BGP speaker
        """
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
        """
        point-to-point intents test for each BGP peer and BGP speaker pair
        """
        main.sdnBase.pToPIntentTest( 6 )

    def CASE3( self, main ):
        """
        routes and intents check to all BGP peers
        """
        main.case( "Check routes and M2S intents to all BGP peers" )

        allRoutesExpected = []
        allRoutesExpected.append( "4.0.0.0/24" + "/" + "10.0.4.1" )
        allRoutesExpected.append( "5.0.0.0/24" + "/" + "10.0.5.1" )
        allRoutesExpected.append( "6.0.0.0/24" + "/" + "10.0.6.1" )
        allRoutesExpected.append( "7.0.0.0/24" + "/" + "10.0.7.1" )
        allRoutesExpected.append( "8.0.0.0/24" + "/" + "10.0.8.1" )
        allRoutesExpected.append( "9.0.0.0/24" + "/" + "10.0.9.1" )
        allRoutesExpected.append( "20.0.0.0/24" + "/" + "10.0.20.1" )

        main.sdnBase.routeAndIntentCheck( allRoutesExpected, 7 )

    def CASE4( self, main ):
        """
        Ping test in data plane for each route
        """
        main.case( "Ping test for each route, all hosts behind BGP peers" )
        # No vlan
        main.Functions.pingHostToHost( main,
                                       hosts=[ "h64514", "h64515", "h64516" ],
                                       expectAllSuccess=True )
        # vlan 10
        main.Functions.pingHostToHost( main,
                                       hosts=[ "h64519", "h64520" ],
                                       expectAllSuccess=True )

        # vlan 20
        main.Functions.pingHostToHost( main,
                                       hosts=[ "h64517", "h64518" ],
                                       expectAllSuccess=True )

    def CASE5( self, main ):
        """
        Cut links to peers one by one, check routes/intents
        """
        main.sdnBase.linkUpDownCheck( "p64514", "p64515", "p64516",
                                      6, 6, 5, 5, 4, 4,
                                      "spk1", [ "h64514", "h64515", "h64516" ],
                                      "down" )

    def CASE6( self, main ):
        """
        Recover links to peers one by one, check routes/intents
        """
        main.sdnBase.linkUpDownCheck( "p64514", "p64515", "p64516",
                                      5, 5, 6, 6, 7, 7,
                                      "spk1", [ "h64514", "h64515", "h64516" ],
                                      "up" )

    def CASE7( self, main ):
        """
        Shut down a edge switch, check P-2-P and M-2-S intents, ping test
        """
        import time
        main.case( "Stop edge sw32,check P-2-P and M-2-S intents, ping test" )
        main.step( "Stop sw32" )
        result = main.Mininet.switch( SW="sw32", OPTION="stop" )
        utilities.assertEquals( expect=main.TRUE, actual=result,
                                onpass="Stopping switch succeeded!",
                                onfail="Stopping switch failed!" )

        if result == main.TRUE:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, 6 )  # stop one sw, which bring one link between peer and sw down.
            main.Functions.checkM2SintentNum( main, 6 )
            main.Functions.checkP2PintentNum( main, 36 )  # 6 intents from sw to speakers x 6 intents to sw x 2 intents between them
        else:
            main.log.error( "Stopping switch failed!" )
            main.cleanAndExit()

        main.step( "Check ping between hosts behind BGP peers" )
        result1 = main.Mininet.pingHost( src="h64514", target="h64515" )
        result2 = main.Mininet.pingHost( src="h64515", target="h64516" )
        result3 = main.Mininet.pingHost( src="h64514", target="h64516" )

        pingResult1 = ( result1 == main.FALSE ) and ( result2 == main.TRUE ) \
                                                and ( result3 == main.FALSE )
        utilities.assert_equals( expect=True, actual=pingResult1,
                                 onpass="Ping test result is correct",
                                 onfail="Ping test result is wrong" )

        if not pingResult1:
            main.cleanAndExit()

        main.step( "Check ping between BGP peers and speakers" )
        result4 = main.Mininet.pingHost( src="spk1", target="p64514" )
        result5 = main.Mininet.pingHost( src="spk1", target="p64515" )
        result6 = main.Mininet.pingHost( src="spk1", target="p64516" )

        pingResult2 = ( result4 == main.FALSE ) and ( result5 == main.TRUE ) \
                                                and ( result6 == main.TRUE )
        utilities.assert_equals( expect=True, actual=pingResult2,
                                 onpass="Speaker1 ping peers successful",
                                 onfail="Speaker1 ping peers NOT successful" )

        if not pingResult2:
            main.cleanAndExit()

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

    def CASE8( self, main ):
        """
        Bring up the edge switch ( sw32 ) which was shut down in CASE7,
        check P-2-P and M-2-S intents, ping test
        """
        import time
        main.case( "Start the edge sw32, check P-2-P and M-2-S intents, ping test" )
        main.step( "Start sw32" )
        result1 = main.Mininet.switch( SW="sw32", OPTION="start" )
        utilities.assertEquals(
            expect=main.TRUE,
            actual=result1,
            onpass="Starting switch succeeded!",
            onfail="Starting switch failed!" )

        result2 = main.Mininet.assignSwController( "sw32", main.Cluster.active( 0 ).ipAddress )
        utilities.assertEquals(
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
            main.cleanAndExit()

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

        # Ping test
        main.Functions.pingSpeakerToPeer( main, speakers=[ "spk1" ],
                                          peers=[ "p64514", "p64515", "p64516" ],
                                          expectAllSuccess=True )
        main.Functions.pingHostToHost( main,
                                       hosts=[ "h64514", "h64515", "h64516" ],
                                       expectAllSuccess=True )

    def CASE9( self, main ):
        """
        Bring down a switch in best path, check:
        route number, P2P intent number, M2S intent number, ping test
        """
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
            main.cleanAndExit()

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
        # Ping test
        main.Functions.pingSpeakerToPeer( main, speakers=[ "spk1" ],
                                          peers=[ "p64514", "p64515", "p64516" ],
                                          expectAllSuccess=True )
        main.Functions.pingHostToHost( main,
                                       hosts=[ "h64514", "h64515", "h64516" ],
                                       expectAllSuccess=True )

    def CASE10( self, main ):
        """
        Bring up the switch which was stopped in CASE9, check:
        route number, P2P intent number, M2S intent number, ping test
        """
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
        result2 = main.Mininet.assignSwController( "sw11", main.Cluster.active( 0 ).ipAddress )
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
            main.cleanAndExit()

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
        # Ping test
        main.Functions.pingSpeakerToPeer( main, speakers=[ "spk1" ],
                                          peers=[ "p64514", "p64515", "p64516" ],
                                          expectAllSuccess=True )
        main.Functions.pingHostToHost( main,
                                       hosts=[ "h64514", "h64515", "h64516" ],
                                       expectAllSuccess=True )
