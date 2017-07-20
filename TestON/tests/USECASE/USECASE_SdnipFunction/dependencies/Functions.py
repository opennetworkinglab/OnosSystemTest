"""
Copyright 2016 Open Networking Foundation (ONF)

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.
"""

def checkRouteNum( main, routeNumExpected ):
    import time
    main.step( "Check routes installed" )
    wait = int( main.params['timers']['PathAvailable'] )
    main.log.info( "Route number expected:" )
    main.log.info( routeNumExpected )
    main.log.info( "Route number from ONOS CLI:" )

    routeNumActual = main.Cluster.active( 0 ).CLI.ipv4RouteNumber()
    if routeNumActual != routeNumExpected:
        time.sleep( wait )
        routeNumActual = main.Cluster.active( 0 ).CLI.ipv4RouteNumber()
    main.log.info( routeNumActual )
    utilities.assertEquals( \
        expect = routeNumExpected, actual = routeNumActual,
        onpass = "Route number is correct!",
        onfail = "Route number is wrong!" )

def checkM2SintentNum( main, intentNumExpected ):
    import time
    main.step( "Check M2S intents installed" )
    wait = int( main.params['timers']['PathAvailable'] )
    jsonResult = main.Cluster.active( 0 ).CLI.intents( jsonFormat = True, summary = True,
                                                       TYPE = "multiPointToSinglePoint" )
    try:
        intentNumActual = jsonResult['installed']
    except TypeError as e:
        intentNumActual = -1
        main.log.error( e )
    if intentNumActual != intentNumExpected:
        time.sleep( wait )
        jsonResult = main.Cluster.active( 0 ).CLI.intents( jsonFormat = True, summary = True,
                                                           TYPE = "multiPointToSinglePoint" )
        try:
            intentNumActual = jsonResult['installed']
        except TypeError as e:
            intentNumActual = -1
            main.log.error( e )
    main.log.info( "Intent number expected: {}".format( intentNumExpected ) )
    main.log.info( "Intent number from ONOS CLI: {}".format( intentNumActual ) )
    utilities.assertEquals( \
        expect = intentNumExpected, actual = intentNumActual,
        onpass = "M2S intent number is correct!",
        onfail = "M2S intent number is wrong!" )

def checkP2PintentNum( main, intentNumExpected ):
    import time
    main.step( "Check P2P intents installed" )
    wait = int( main.params['timers']['PathAvailable'] )
    jsonResult = main.Cluster.active( 0 ).CLI.intents( jsonFormat = True, summary = True,
                                                       TYPE = "pointToPoint" )
    try:
        intentNumActual = jsonResult['installed']
    except TypeError as e:
        intentNumActual = -1
        main.log.error( e )

    if intentNumActual != intentNumExpected:
        time.sleep( wait )
        jsonResult = main.Cluster.active( 0 ).CLI.intents( jsonFormat = True, summary = True,
                                                           TYPE = "pointToPoint" )
        try:
            intentNumActual = jsonResult['installed']
        except TypeError as e:
            intentNumActual = -1
            main.log.error( e )
    main.log.info( "Intent number expected: {}".format( intentNumExpected ) )
    main.log.info( "Intent number from ONOS CLI: {}".format( intentNumActual ) )
    utilities.assertEquals( \
        expect = intentNumExpected, actual = intentNumActual,
        onpass = "P2P intent number is correct!",
        onfail = "P2P intent number is wrong!" )

def checkFlowNum( main, switch, flowNumExpected ):
    import time
    main.step( "Check flow entry number in " + switch )
    wait = int( main.params['timers']['PathAvailable'] )
    main.log.info( "Flow number expected: {}".format( flowNumExpected ) )
    flowNumActual = main.Mininet.getSwitchFlowCount( switch )
    if flowNumActual != flowNumExpected :
        time.sleep( wait )
        flowNumActual = main.Mininet.getSwitchFlowCount( switch )
    main.log.info( "Flow number actual: {}".format( flowNumActual ) )
    utilities.assertEquals( \
        expect = flowNumExpected, actual = flowNumActual,
        onpass = "Flow number in " + switch + " is correct!",
        onfail = "Flow number in " + switch + " is wrong!" )


def pingSpeakerToPeer( main, speakers = [ "spk1" ],
                       peers = [ "peer64514", "peer64515", "peer64516" ],
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


def pingHostToHost( main,
                    hosts = [ "h64514", "h64515", "h64516" ],
                expectAllSuccess = True ):
    """
    Carry out ping test between each BGP host pair
    Optional argument:
        * hosts - hosts behind BGP peer routers
        * expectAllSuccess - boolean indicating if you expect all results
        succeed if True, otherwise expect all results fail if False
    """
    main.step( "Check ping between each host pair, expect all to succede=" +
               str( expectAllSuccess ) )
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

