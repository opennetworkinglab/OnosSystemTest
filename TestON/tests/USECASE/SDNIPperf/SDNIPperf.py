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

        cleanInstallResult = main.TRUE
        gitPullResult = main.TRUE

        main.step( "Git pull" )
        gitPullResult = main.FALSE
        #Need to push some new code to ONOS before using the git pull
        #gitPullResult = main.ONOSbench.gitPull()

        main.step( "Using mvn clean install" )
        if gitPullResult == main.TRUE:
            #cleanInstallResult = main.ONOSbench.cleanInstall()
            cleanInstallResult = main.ONOSbench.cleanInstall( skipTest=True)
        else:
             main.log.warn( "Did not pull new code so skipping mvn " +
                             "clean install" )
        main.ONOSbench.getVersion( report=True )

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage( opTimeout=500 )

        main.step( "Installing ONOS package" )
        onos1InstallResult = main.ONOSbench.onosInstall( options="-f",
                                                           node=ONOS1Ip )

        main.step( "Checking if ONOS is up yet" )
        for i in range( 2 ):
            onos1Isup = main.ONOSbench.isup( ONOS1Ip, timeout=420 )
            if onos1Isup:
                break
        if not onos1Isup:
            main.log.report( "ONOS1 didn't start!" )

        cliResult = main.ONOScli.startOnosCli( ONOS1Ip,
                commandlineTimeout=100, onosStartTimeout=600)

        case1Result = ( cleanInstallResult and packageResult and
                        cellResult and verifyResult and
                        onos1InstallResult and
                        onos1Isup and cliResult )

        utilities.assert_equals( expect=main.TRUE, actual=case1Result,
                                 onpass="ONOS startup successful",
                                 onfail="ONOS startup NOT successful" )

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
        listResult = main.ONOScli.devices( jsonFormat=False )
        main.log.info( listResult )

        main.step( "Get links in the network" )
        listResult = main.ONOScli.links ( jsonFormat=False )
        main.log.info( listResult )

        main.log.info( "Activate sdn-ip application" )
        main.ONOScli.activateApp( "org.onosproject.sdnip" )

        main.step("Sleep 1200 seconds")
        # wait until SDN-IP receives all routes and ONOS installs all intents
        time.sleep( int(main.params[ 'timers' ][ 'SystemBoot' ]) )

        main.step( "Checking routes installed" )

        main.log.info( "Total route number expected is:" )
        main.log.info( routeNumberExpected )

        routeNumberActual = main.ONOScli.ipv4RouteNumber()
        main.log.info("Total route  number actual is: ")
        main.log.info(routeNumberActual)

        utilities.assertEquals(
            expect=routeNumberExpected, actual=routeNumberActual,
            onpass="***Routes in SDN-IP are correct!***",
            onfail="***Routes in SDN-IP are wrong!***" )


        main.step( "Checking MultiPointToSinglePointIntent intents installed" )

        main.log.info( "MultiPointToSinglePoint intent number expected is:" )
        main.log.info( m2SIntentsNumberExpected )

        m2SIntentsNumberActual = main.ONOScli.m2SIntentInstalledNumber()
        main.log.info( "MultiPointToSinglePoint intent number actual is:" )
        main.log.info(m2SIntentsNumberActual)

        utilities.assertEquals(
            expect=True,
            actual=eq( m2SIntentsNumberExpected, m2SIntentsNumberActual ),
            onpass="***MultiPointToSinglePoint intent number is correct!***",
            onfail="***MultiPointToSinglePoint intent number is wrong!***" )
