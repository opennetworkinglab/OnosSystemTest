
def checkRouteNum( main, routeNumExpected, ONOScli = "ONOScli1" ):
    main.step( "Check routes installed" )
    main.log.info( "Route number expected:" )
    main.log.info( routeNumExpected )
    main.log.info( "Route number from ONOS CLI:" )

    if ONOScli == "ONOScli1":
        routeNumActual = main.ONOScli1.ipv4RouteNumber()
    else:
        routeNumActual = main.ONOScli2.ipv4RouteNumber()

    main.log.info( routeNumActual )
    utilities.assertEquals( \
        expect = routeNumExpected, actual = routeNumActual,
        onpass = "Route number is correct!",
        onfail = "Route number is wrong!" )

def checkM2SintentNum( main, intentNumExpected, ONOScli = "ONOScli1" ):
    main.step( "Check M2S intents installed" )
    main.log.info( "Intent number expected:" )
    main.log.info( intentNumExpected )
    main.log.info( "Intent number from ONOS CLI:" )
    if ONOScli == "ONOScli1":
        jsonResult = main.ONOScli1.intents( jsonFormat = True, summary = True,
                                            TYPE = "multiPointToSinglePoint" )
    else:
        jsonResult = main.ONOScli2.intents( jsonFormat = True, summary = True,
                                            TYPE = "multiPointToSinglePoint" )
    intentNumActual = jsonResult['installed']
    main.log.info( intentNumActual )
    utilities.assertEquals( \
        expect = intentNumExpected, actual = intentNumActual,
        onpass = "M2S intent number is correct!",
        onfail = "M2S intent number is wrong!" )

def checkP2PintentNum( main, intentNumExpected, ONOScli = "ONOScli1" ):
    main.step( "Check P2P intents installed" )
    main.log.info( "Intent number expected:" )
    main.log.info( intentNumExpected )
    main.log.info( "Intent number from ONOS CLI:" )
    if ONOScli == "ONOScli1":
        jsonResult = main.ONOScli1.intents( jsonFormat = True, summary = True,
                                            TYPE = "pointToPoint" )
    else:
        jsonResult = main.ONOScli2.intents( jsonFormat = True, summary = True,
                                            TYPE = "pointToPoint" )
    intentNumActual = jsonResult['installed']
    main.log.info( intentNumActual )
    utilities.assertEquals( \
        expect = intentNumExpected, actual = intentNumActual,
        onpass = "P2P intent number is correct!",
        onfail = "P2P intent number is wrong!" )

def checkFlowNum( main, switch, flowNumExpected ):
    main.step( "Check flow entry number in " + switch )
    main.log.info( "Flow number expected:" )
    main.log.info( flowNumExpected )
    main.log.info( "Flow number actual:" )
    flowNumActual = main.Mininet.getSwitchFlowCount( switch )
    main.log.info( flowNumActual )
    utilities.assertEquals( \
        expect = flowNumExpected, actual = flowNumActual,
        onpass = "Flow number in " + switch + " is correct!",
        onfail = "Flow number in " + switch + " is wrong!" )


def pingSpeakerToPeer( main, speakers = ["speaker1"],
                       peers = ["peer64514", "peer64515", "peer64516"],
                       expectAllSuccess = True ):
    """
    Carry out ping test between each BGP speaker and peer pair
    Optional argument:
        * speakers - BGP speakers
        * peers - BGP peers
        * expectAllSuccess - boolean indicating if you expect all results
        succeed if True, otherwise expect all results fail if False
    """
    if len( speakers ) == 0:
        main.log.error( "Parameter speakers can not be empty." )
        main.cleanup()
        main.exit()
    if len( peers ) == 0:
        main.log.error( "Parameter speakers can not be empty." )
        main.cleanup()
        main.exit()

    if expectAllSuccess:
        main.step( "BGP speakers ping peers, expect all tests to succeed" )
    else:
        main.step( "BGP speakers ping peers, expect all tests to fail" )

    result = True
    if expectAllSuccess:
        for speaker in speakers:
            for peer in peers:
                tmpResult = main.Mininet.pingHost( src = speaker,
                                                   target = peer )
                result = result and ( tmpResult == main.TRUE )
    else:
        for speaker in speakers:
            for peer in peers:
                tmpResult = main.Mininet.pingHost( src = speaker,
                                                   target = peer )

    utilities.assert_equals( expect = True, actual = result,
                             onpass = "Ping test results are expected",
                             onfail = "Ping test results are Not expected" )

    if result == False:
        main.cleanup()
        main.exit()


def pingHostToHost( main, hosts = ["host64514", "host64515", "host64516"],
                expectAllSuccess = True ):
    """
    Carry out ping test between each BGP host pair
    Optional argument:
        * hosts - hosts behind BGP peer routers
        * expectAllSuccess - boolean indicating if you expect all results
        succeed if True, otherwise expect all results fail if False
    """
    main.step( "Check ping between each host pair" )
    if len( hosts ) == 0:
        main.log.error( "Parameter hosts can not be empty." )
        main.cleanup()
        main.exit()

    result = True
    if expectAllSuccess:
        for srcHost in hosts:
            for targetHost in hosts:
                if srcHost != targetHost:
                    tmpResult = main.Mininet.pingHost( src = srcHost,
                                                       target = targetHost )
                    result = result and ( tmpResult == main.TRUE )
    else:
        for srcHost in hosts:
            for targetHost in hosts:
                if srcHost != targetHost:
                    tmpResult = main.Mininet.pingHost( src = srcHost,
                                                       target = targetHost )
                    result = result and ( tmpResult == main.FALSE )

    utilities.assert_equals( expect = True, actual = result,
                             onpass = "Ping test results are expected",
                             onfail = "Ping test results are Not expected" )

    '''
    if result == False:
        main.cleanup()
        main.exit()
    '''


def setupTunnel( main, srcIp, srcPort, dstIp, dstPort ):
    """
    Create a tunnel from Mininet host to host outside Mininet
    """
    main.step( "Set up tunnel from Mininet node " +
               str( srcIp ) + ":" + str( srcPort ) + " to ONOS node "
               + str(dstIp) + ":" + str(dstPort) )
    forwarding = '%s:%s:%s:%s' % ( srcIp, srcPort, dstIp, dstPort )
    command = 'ssh -nNT -o "PasswordAuthentication no" \
        -o "StrictHostKeyChecking no" -l sdn -L %s %s & ' % ( forwarding, dstIp )


    tunnelResult = main.TRUE
    tunnelResult = main.Mininet.node( "root", command )
    utilities.assert_equals( expect = True,
                             actual = ( "PasswordAuthentication" in tunnelResult ),
                             onpass = "Created tunnel succeeded",
                             onfail = "Create tunnel failed" )
    if ( "PasswordAuthentication" not in tunnelResult ) :
        main.cleanup()
        main.exit()

