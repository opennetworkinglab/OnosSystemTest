
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
        onfail = "***Routes number is wrong!***" )

def checkM2SintentNum( main, intentNumExpected ):
    main.step( "Check M2S intents installed" )
    main.log.info( "Intent number expected:" )
    main.log.info( intentNumExpected )
    main.log.info( "Intent number from ONOS CLI:" )
    intentNumActual = main.ONOScli.m2SIntentInstalledNumber()
    main.log.info( intentNumActual )
    utilities.assertEquals( \
        expect = intentNumExpected, actual = intentNumActual,
        onpass = "***Intents number is correct!***",
        onfail = "***Intents number is wrong!***" )

