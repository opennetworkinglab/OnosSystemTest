class SDNIPperf:

    def __init__( self ):
        self.default = ''
        global branchName

    # This case is to setup ONOS
    def CASE100( self, main ):
        """
           CASE100 is to compile ONOS and push it to the test machines
           Startup sequence:
           cell <name>
           onos-verify-cell
           git pull
           mvn clean install
           onos-package
           onos-install -f
           onos-wait-for-start
        """
        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
            main.testSetUp = ONOSSetup()
        except ImportError:
            main.log.error( "ONOSSetup not found. exiting the test" )
            main.exit()
        main.testSetUp.envSetupDescription()
        stepResult = main.FALSE

        try:
            cellName = main.params[ 'ENV' ][ 'cellName' ]
            ONOS1Ip = main.params['CTRL']['ip1']
            stepResult = main.testSetUp.envSetup( specificIp=ONOS1Ip )
        except Exception as e:
            main.testSetUp.envSetupException( e )
        main.testSetUp.evnSetupConclusion( stepResult )

        case1Result = main.testSetUp.ONOSSetUp( "", newCell=False, cellname=cellName )

        if case1Result == main.FALSE:
            main.cleanup()
            main.exit()

    def CASE9( self, main ):
        """
        Test the SDN-IP Performance
        Test whether SDN-IP can boot with 600,000 routes from an external peer.
        Since our goal for SDN-IP is to handle 600,000 routes, in this test case
        we statically configure an external peer Quagga with 655360 routes.
        Thus, we pre-know the routes and intents it should be, and then boot the
        whole system and check whether the numbers of routes and intents from
        ONOS CLI are correct.
        """
        import time
        import json
        from operator import eq
        from time import localtime, strftime

        # We configured one external BGP peer with 655360 routes
        routeNumberExpected = 655360
        m2SIntentsNumberExpected = 655360

        main.case("This case is to testing the performance of SDN-IP with \
        single ONOS instance" )
        time.sleep( 10 )

        main.step( "Get devices in the network" )
        listResult = main.ONOScli1.devices( jsonFormat=False )
        main.log.info( listResult )

        main.step( "Get links in the network" )
        listResult = main.ONOScli1.links ( jsonFormat=False )
        main.log.info( listResult )

        main.log.info( "Activate sdn-ip application" )
        main.ONOScli1.activateApp( "org.onosproject.sdnip" )

        main.step("Sleep 1200 seconds")
        # wait until SDN-IP receives all routes and ONOS installs all intents
        time.sleep( int(main.params[ 'timers' ][ 'SystemBoot' ]) )

        main.step( "Checking routes installed" )

        main.log.info( "Total route number expected is:" )
        main.log.info( routeNumberExpected )

        routeNumberActual = main.ONOScli1.ipv4RouteNumber()
        main.log.info("Total route  number actual is: ")
        main.log.info(routeNumberActual)

        utilities.assertEquals(
            expect=routeNumberExpected, actual=routeNumberActual,
            onpass="***Routes in SDN-IP are correct!***",
            onfail="***Routes in SDN-IP are wrong!***" )


        main.step( "Checking MultiPointToSinglePointIntent intents installed" )

        main.log.info( "MultiPointToSinglePoint intent number expected is:" )
        main.log.info( m2SIntentsNumberExpected )

        m2SIntentsNumberActual = main.ONOScli1.m2SIntentInstalledNumber()
        main.log.info( "MultiPointToSinglePoint intent number actual is:" )
        main.log.info(m2SIntentsNumberActual)

        utilities.assertEquals(
            expect=True,
            actual=eq( m2SIntentsNumberExpected, m2SIntentsNumberActual ),
            onpass="***MultiPointToSinglePoint intent number is correct!***",
            onfail="***MultiPointToSinglePoint intent number is wrong!***" )
