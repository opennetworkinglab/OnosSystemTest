"""
Copyright 2015 Open Networking Foundation ( ONF )

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


class USECASE_SdnipFunctionCluster:

    def __init__( self ):
        self.default = ''
        global branchName

    def CASE100( self, main ):
        """
            Start mininet
        """
        import imp
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
            main.cleanAndExit()
        main.step( "Connect switches to controllers" )

        # connect all switches to controllers
        swResult = main.TRUE
        for i in range( 1, int( main.params[ 'config' ][ 'switchNum' ] ) + 1 ):
            sw = "sw%s" % ( i )
            swResult = swResult and \
                       main.Mininet.assignSwController( sw, main.Cluster.getIps() )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=swResult,
                                 onpass="Successfully connect all switches to ONOS",
                                 onfail="Failed to connect all switches to ONOS" )
        if not swResult:
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
        import json
        import time
        import os
        from operator import eq
        global p64514
        global p64515
        global p64516
        p64514 = main.params[ 'config' ][ 'p64514' ]
        p64515 = main.params[ 'config' ][ 'p64515' ]
        p64516 = main.params[ 'config' ][ 'p64516' ]

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
        main.case( "Activate sdn-ip application" )
        main.log.info( "waiting link discovery......" )
        time.sleep( int( main.params[ 'timers' ][ 'TopoDiscovery' ] ) )

        main.step( "Get links in the network" )
        summaryResult = main.Cluster.active( 0 ).CLI.summary()
        linkNum = json.loads( summaryResult )[ "links" ]
        main.log.info( "Expected 100 links, actual number is: {}".format( linkNum ) )
        if linkNum < 100:
            main.log.error( "Link number is wrong! Retrying..." )
            time.sleep( int( main.params[ 'timers' ][ 'TopoDiscovery' ] ) )
            summaryResult = main.Cluster.active( 0 ).CLI.summary()
            linkNum = json.loads( summaryResult )[ "links" ]
        main.log.info( "Expected 100 links, actual number is: {}".format( linkNum ) )
        utilities.assert_equals( expect=100,
                                 actual=linkNum,
                                 onpass="ONOS correctly discovered all links",
                                 onfail="ONOS Failed to discover all links" )
        if linkNum < 100:
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

    def CASE102( self, main ):
        """
        This test case is to load the methods from other Python files, and create
        tunnels from mininet host to onos nodes.
        """
        import time
        main.case( "Load methods from other Python file and create tunnels" )
        # load the methods from other file
        wrapperFile1 = main.params[ 'DEPENDENCY' ][ 'wrapper1' ]
        main.Functions = imp.load_source( wrapperFile1,
                                          main.dependencyPath +
                                          wrapperFile1 +
                                          ".py" )
        # Create tunnels
        for i in range( main.Cluster.numCtrls ):
            main.Functions.setupTunnel( main,
                                        '1.1.1.' + str( ( i + 1 ) * 2 ),
                                        2000,
                                        main.Cluster.active( i ).ipAddress, 2000 )

        main.log.info( "Wait SDN-IP to finish installing connectivity intents \
        and the BGP paths in data plane are ready..." )
        time.sleep( int( main.params[ 'timers' ][ 'SdnIpSetup' ] ) )

        main.log.info( "Wait Quagga to finish delivery all routes to each \
        other and to sdn-ip, plus finish installing all intents..." )
        time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )

    def CASE1( self, main ):
        """
        ping test from 3 bgp peers to BGP speaker
        """
        main.case( "Ping between BGP peers and speakers" )
        main.Functions.pingSpeakerToPeer( main, speakers=[ "spk1" ],
                                          peers=[ "p64514", "p64515", "p64516" ],
                                          expectAllSuccess=True )

        main.Functions.pingSpeakerToPeer( main, speakers=[ "spk2" ],
                                          peers=[ p64514, p64515, p64516 ],
                                          expectAllSuccess=True )

        main.Functions.pingSpeakerToPeer( main, speakers=[ "spk3" ],
                                          peers=[ "p64519", "p64520" ],
                                          expectAllSuccess=True )

        main.Functions.pingSpeakerToPeer( main, speakers=[ "spk4" ],
                                          peers=[ "p64517", "p64518" ],
                                          expectAllSuccess=True )

    def CASE2( self, main ):
        """
        point-to-point intents test for each BGP peer and BGP speaker pair
        """
        main.sdnBase.pToPIntentTest( 12 )

    def CASE3( self, main ):
        """
        routes and intents check to all BGP peers
        """
        import time
        main.case( "Check routes and M2S intents to all BGP peers" )

        main.step( "Check routes installed" )
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
        main.Functions.pingHostToHost( main,
                                       hosts=[ "h64514", "h64515", "h64516" ],
                                       expectAllSuccess=True )
        main.Functions.pingHostToHost( main,
                                       hosts=[ "h64517", "h64518" ],
                                       expectAllSuccess=True )
        main.Functions.pingHostToHost( main,
                                       hosts=[ "h64519", "h64520" ],
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
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                 onpass="Stopping switch succeeded!",
                                 onfail="Stopping switch failed!" )

        if result == main.TRUE:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, 6 )
            main.Functions.checkM2SintentNum( main, 6 )
            main.Functions.checkP2PintentNum( main, 48 )  # 14 * 2
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

        main.step( "Check ping between BGP peers and spk1" )
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

        main.step( "Check ping between BGP peers and spk2" )
        # TODO
        result7 = main.Mininet.pingHost( src="spk2", target=p64514 )
        result8 = main.Mininet.pingHost( src="spk2", target=p64515 )
        result9 = main.Mininet.pingHost( src="spk2", target=p64516 )

        pingResult3 = ( result7 == main.FALSE ) and ( result8 == main.TRUE ) \
                                                and ( result9 == main.TRUE )
        utilities.assert_equals( expect=True, actual=pingResult2,
                                 onpass="Speaker2 ping peers successful",
                                 onfail="Speaker2 ping peers NOT successful" )

        if not pingResult3:
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

    def CASE8( self, main ):
        """
        Bring up the edge switch ( sw32 ) which was shut down in CASE7,
        check P-2-P and M-2-S intents, ping test
        """
        import time
        main.case( "Start the edge sw32, check P-2-P and M-2-S intents, ping test" )
        main.step( "Start sw32" )
        result1 = main.Mininet.switch( SW="sw32", OPTION="start" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=result1,
                                 onpass="Starting switch succeeded!",
                                 onfail="Starting switch failed!" )

        result2 = main.Mininet.assignSwController( "sw32", main.Cluster.active( 0 ).ipAddress )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=result2,
                                 onpass="Connect switch to ONOS succeeded!",
                                 onfail="Connect switch to ONOS failed!" )

        if result1 and result2:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, 7 )
            main.Functions.checkM2SintentNum( main, 7 )
            main.Functions.checkP2PintentNum( main, 30 * 2 )  # 18*2
        else:
            main.log.error( "Starting switch failed!" )
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
        main.Functions.pingSpeakerToPeer( main, speakers=[ "spk1" ],
                                          peers=[ "p64514", "p64515", "p64516" ],
                                          expectAllSuccess=True )

        main.Functions.pingSpeakerToPeer( main, speakers=[ "spk2" ],
                                          peers=[ p64514, p64515, p64516 ],
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
        main.Functions.checkFlowNum( main, "sw11", 49 )
        main.Functions.checkFlowNum( main, "sw1", 7 )
        main.Functions.checkFlowNum( main, "sw7", 34 )
        main.log.info( main.Mininet.checkFlows( "sw11" ) )
        main.log.info( main.Mininet.checkFlows( "sw1" ) )
        main.log.info( main.Mininet.checkFlows( "sw7" ) )

        main.step( "Stop sw11" )
        result = main.Mininet.switch( SW="sw11", OPTION="stop" )
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                 onpass="Stopping switch succeeded!",
                                 onfail="Stopping switch failed!" )
        if result:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, 7 )
            main.Functions.checkM2SintentNum( main, 7 )
            main.Functions.checkP2PintentNum( main, 30 * 2 )  # 18 * 2
        else:
            main.log.error( "Stopping switch failed!" )
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
        main.Functions.pingSpeakerToPeer( main, speakers=[ "spk1" ],
                                          peers=[ "p64514", "p64515", "p64516" ],
                                          expectAllSuccess=True )
        main.Functions.pingSpeakerToPeer( main, speakers=[ "spk2" ],
                                          peers=[ p64514, p64515, p64516 ],
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
        main.Functions.checkFlowNum( main, "sw1", 36 )
        main.Functions.checkFlowNum( main, "sw7", 30 )
        main.log.info( main.Mininet.checkFlows( "sw1" ) )
        main.log.info( main.Mininet.checkFlows( "sw7" ) )

        main.step( "Start sw11" )
        result1 = main.Mininet.switch( SW="sw11", OPTION="start" )
        utilities.assert_equals( expect=main.TRUE, actual=result1,
                                 onpass="Starting switch succeeded!",
                                 onfail="Starting switch failed!" )
        result2 = main.Mininet.assignSwController( "sw11", main.Cluster.active( 0 ).ipAddress )
        utilities.assert_equals( expect=main.TRUE, actual=result2,
                                 onpass="Connect switch to ONOS succeeded!",
                                 onfail="Connect switch to ONOS failed!" )
        if result1 and result2:
            time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
            main.Functions.checkRouteNum( main, 7 )
            main.Functions.checkM2SintentNum( main, 7 )
            main.Functions.checkP2PintentNum( main, 30 * 2 )

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
        utilities.assert_equals( expect=main.TRUE,
                                 actual=flowCheck,
                                 onpass="Flow status is correct!",
                                 onfail="Flow status is wrong!" )
        # Ping test
        main.Functions.pingSpeakerToPeer( main, speakers=[ "spk1" ],
                                          peers=[ "p64514", "p64515", "p64516" ],
                                          expectAllSuccess=True )
        main.Functions.pingSpeakerToPeer( main, speakers=[ "spk2" ],
                                          peers=[ p64514, p64515, p64516 ],
                                          expectAllSuccess=True )
        main.Functions.pingHostToHost( main,
                                       hosts=[ "h64514", "h64515", "h64516" ],
                                       expectAllSuccess=True )

    def CASE11( self, main ):
        import time
        main.case( "Kill spk1, check:\
        route number, P2P intent number, M2S intent number, ping test" )
        main.log.info( "Check network status before killing spk1" )
        main.Functions.checkRouteNum( main, 7 )
        main.Functions.checkM2SintentNum( main, 7 )
        main.Functions.checkP2PintentNum( main, 30 * 2 )
        main.step( "Check whether all flow status are ADDED" )
        flowCheck = utilities.retry( main.Cluster.active( 0 ).CLI.checkFlowsState,
                                     main.FALSE,
                                     kwargs={ 'isPENDING': False },
                                     attempts=10 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=flowCheck,
                                 onpass="Flow status is correct!",
                                 onfail="Flow status is wrong!" )

        main.Functions.pingSpeakerToPeer( main, speakers=[ "spk1" ],
                                          peers=[ "p64514", "p64515", "p64516" ],
                                          expectAllSuccess=True )
        main.Functions.pingSpeakerToPeer( main, speakers=[ "spk2" ],
                                          peers=[ p64514, p64515, p64516 ],
                                          expectAllSuccess=True )
        main.Functions.pingHostToHost( main,
                                       hosts=[ "h64514", "h64515", "h64516" ],
                                       expectAllSuccess=True )

        main.step( "Kill spk1" )
        command1 = "ps -e | grep bgp -c"
        result1 = main.Mininet.node( "root", command1 )

        # The total BGP daemon number in this test environment is 5.
        if "5" in result1:
            main.log.debug( "Before kill spk1, 5 BGP daemons - correct" )
        else:
            main.log.warn( "Before kill spk1, number of BGP daemons is wrong" )
            main.log.info( result1 )

        command2 = "sudo kill -9 `ps -ef | grep quagga-sdn.conf | grep -v grep | awk '{print $2}'`"
        result2 = main.Mininet.node( "root", command2 )

        result3 = main.Mininet.node( "root", command1 )

        utilities.assert_equals( expect=True,
                                 actual=( "4" in result3 ),
                                 onpass="Kill spk1 succeeded",
                                 onfail="Kill spk1 failed" )
        if ( "4" not in result3 ):
            main.log.info( result3 )
            main.cleanAndExit()

        time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )
        main.Functions.checkRouteNum( main, 7 )
        main.Functions.checkM2SintentNum( main, 7 )
        main.Functions.checkP2PintentNum( main, 30 * 2 )

        main.step( "Check whether all flow status are ADDED" )
        flowCheck = utilities.retry( main.Cluster.active( 0 ).CLI.checkFlowsState,
                                     main.FALSE,
                                     kwargs={ 'isPENDING': False },
                                     attempts=10 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=flowCheck,
                                 onpass="Flow status is correct!",
                                 onfail="Flow status is wrong!" )

        """
        main.Functions.pingSpeakerToPeer( main, speakers=[ "spk1" ],
                       peers=[ "p64514", "p64515", "p64516" ],
                       expectAllSuccess=False )
        """
        main.Functions.pingSpeakerToPeer( main, speakers=[ "spk2" ],
                                          peers=[ p64514, p64515, p64516 ],
                                          expectAllSuccess=True )
        main.Functions.pingHostToHost( main,
                                       hosts=[ "h64514", "h64515", "h64516" ],
                                       expectAllSuccess=True )

    def CASE12( self, main ):
        import time
        import json
        main.case( "Bring down leader ONOS node, check: \
        route number, P2P intent number, M2S intent number, ping test" )
        main.step( "Find out ONOS leader node" )
        result = main.Cluster.active( 0 ).CLI.leaders()
        jsonResult = json.loads( result )
        leaderIP = ""
        for entry in jsonResult:
            if entry[ "topic" ] == "org.onosproject.sdnip":
                leaderIP = entry[ "leader" ]
                main.log.info( "leaderIP is: " )
                main.log.info( leaderIP )

        main.step( "Uninstall ONOS/SDN-IP leader node" )
        for ip in main.Cluster.getIps():
            if leaderIP == ip:
                uninstallResult = main.ONOSbench.onosStop( ip )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=uninstallResult,
                                 onpass="Uninstall ONOS leader succeeded",
                                 onfail="Uninstall ONOS leader failed" )
        if uninstallResult != main.TRUE:
            main.cleanAndExit()
        time.sleep( int( main.params[ 'timers' ][ 'RouteDelivery' ] ) )

        if leaderIP == main.Cluster.active( 0 ).ipAddress:
            main.Functions.checkRouteNum( main, 7, node=2 )
            main.Functions.checkM2SintentNum( main, 7, node=2 )
            main.Functions.checkP2PintentNum( main, 30 * 2, node=2 )

            main.step( "Check whether all flow status are ADDED" )
            flowCheck = utilities.retry( main.Cluster.active( 0 ).CLI.checkFlowsState,
                                         main.FALSE,
                                         kwargs={ 'isPENDING': False },
                                         attempts=10 )
            utilities.assert_equals( expect=main.TRUE,
                                     actual=flowCheck,
                                     onpass="Flow status is correct!",
                                     onfail="Flow status is wrong!" )
        else:
            main.Functions.checkRouteNum( main, 7 )
            main.Functions.checkM2SintentNum( main, 7 )
            main.Functions.checkP2PintentNum( main, 30 * 2 )

            main.step( "Check whether all flow status are ADDED" )
            flowCheck = utilities.retry( main.Cluster.active( 0 ).CLI.checkFlowsState,
                                         main.FALSE,
                                         kwargs={ 'isPENDING': False },
                                         attempts=10 )
            utilities.assert_equals( expect=main.TRUE,
                                     actual=flowCheck,
                                     onpass="Flow status is correct!",
                                     onfail="Flow status is wrong!" )

        main.Functions.pingSpeakerToPeer( main, speakers=[ "spk1" ],
                                          peers=[ "p64514", "p64515", "p64516" ],
                                          expectAllSuccess=True )
        main.Functions.pingSpeakerToPeer( main, speakers=[ "spk2" ],
                                          peers=[ p64514, p64515, p64516 ],
                                          expectAllSuccess=True )
        main.Functions.pingHostToHost( main,
                                       hosts=[ "h64514", "h64515", "h64516" ],
                                       expectAllSuccess=True )
