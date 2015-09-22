
def checkRouteNum( main, routeNumExpected ):
    main.step( "Check routes installed" )
    main.log.info( "Route number expected:" )
    main.log.info( routeNumExpected )
    main.log.info( "Route number from ONOS CLI:" )

    routeNumActual = main.ONOScli.ipv4RouteNumber()
    main.log.info( routeNumActual )
    utilities.assertEquals( \
        expect = routeNumExpected, actual = routeNumActual,
        onpass = "***Route number is correct!***",
        onfail = "***Route number is wrong!***" )

def checkM2SintentNum( main, intentNumExpected ):
    main.step( "Check M2S intents installed" )
    main.log.info( "Intent number expected:" )
    main.log.info( intentNumExpected )
    main.log.info( "Intent number from ONOS CLI:" )
    jsonResult = main.ONOScli.intents( jsonFormat = True, summary = True,
                                       TYPE = "multiPointToSinglePoint" )
    intentNumActual = jsonResult['installed']
    main.log.info( intentNumActual )
    utilities.assertEquals( \
        expect = intentNumExpected, actual = intentNumActual,
        onpass = "***M2S intent number is correct!***",
        onfail = "***M2S intent number is wrong!***" )

def checkP2PintentNum( main, intentNumExpected ):
    main.step( "Check P2P intents installed" )
    main.log.info( "Intent number expected:" )
    main.log.info( intentNumExpected )
    main.log.info( "Intent number from ONOS CLI:" )
    jsonResult = main.ONOScli.intents( jsonFormat = True, summary = True,
                                       TYPE = "pointToPoint" )
    intentNumActual = jsonResult['installed']
    main.log.info( intentNumActual )
    utilities.assertEquals( \
        expect = intentNumExpected, actual = intentNumActual,
        onpass = "***P2P intent number is correct!***",
        onfail = "***P2P intent number is wrong!***" )

def checkFlowNum( main, switch, flowNumExpected ):
    main.step( "Check flow entry number in " + switch )
    main.log.info( "Flow number expected:" )
    main.log.info( flowNumExpected )
    main.log.info( "Flow number actual:" )
    flowNumActual = main.Mininet.getSwitchFlowCount( switch )
    main.log.info( flowNumActual )
    utilities.assertEquals( \
        expect = flowNumExpected, actual = flowNumActual,
        onpass = "***Flow number in " + switch + " is correct!***",
        onfail = "***Flow number in " + switch + " is wrong!***" )

