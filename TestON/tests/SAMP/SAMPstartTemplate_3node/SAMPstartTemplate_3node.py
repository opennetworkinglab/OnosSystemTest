
# This is a sample template that starts up ONOS cluster, this template
# can be use as a base script for ONOS System Testing.

class SAMPstartTemplate_3node:

    def __init__( self ):
        self.default = ''


    def CASE0(self, main):
        '''
            Pull specific ONOS branch, then Build ONOS on ONOS Bench.
            This step is usually skipped. Because in a Jenkins driven automated
            test env. We want Jenkins jobs to pull&build for flexibility to handle
            different versions of ONOS.
        '''
        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
        except ImportError:
            main.log.error( "ONOSSetup not found. exiting the test" )
            main.exit()
        try:
            main.testSetUp
        except ( NameError, AttributeError ):
            main.testSetUp = ONOSSetup()

        main.testSetUp.gitPulling()


    def CASE1( self, main ):
        '''
            Set up global test variables;
            Uninstall all running cells in test env defined in .topo file

        '''
        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
        except ImportError:
            main.log.error( "ONOSSetup not found. exiting the test" )
            main.exit()
        try:
            main.testSetUp
        except ( NameError, AttributeError ):
            main.testSetUp = ONOSSetup()

        main.testSetUp.envSetupDescription()
        stepResult = main.FALSE
        try:
            main.nodeList = main.params['CASE1']['NodeList'].split(",")
            main.onosStartupSleep = float(main.params['CASE1']['SleepTimers']['onosStartup'])
            main.onosCfgSleep = float(main.params['CASE1']['SleepTimers']['onosCfg'])
            main.mnStartupSleep = float(main.params['CASE1']['SleepTimers']['mnStartup'])
            main.mnCfgSleep = float(main.params['CASE1']['SleepTimers']['mnCfg'])
            main.numCtrls = int( main.params['CASE10']['numNodes'] )
            stepResult = main.testSetUp.envSetup( includeGitPull=False )
        except Exception as e:
            main.testSetUp.envSetupException( e )
        main.testSetUp.evnSetupConclusion( stepResult )


    def CASE2( self, main ):
        '''
            Report errors/warnings/exceptions
        '''
        main.log.info("Error report: \n" )
        main.ONOSbench.logReport( main.ONOSip[0],
                                  [ "INFO",
                                    "FOLLOWER",
                                    "WARN",
                                    "flow",
                                    "ERROR",
                                    "Except" ],
                                  "s" )

    def CASE10( self, main ):
        """
        Start ONOS cluster (3 nodes in this example) in three steps:
        1) start a basic cluster with drivers app via ONOSDriver;
        2) activate apps via ONOSCliDriver;
        3) configure onos via ONOSCliDriver;
        """
        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
        except ImportError:
            main.log.error( "ONOSSetup not found. exiting the test" )
            main.exit()
        try:
            main.testSetUp
        except ( NameError, AttributeError ):
            main.testSetUp = ONOSSetup()

        import time

        main.case( "Start up " + str( main.numCtrls ) + "-node onos cluster.")
        main.step( "Start ONOS cluster with basic (drivers) app.")
        stepResult = main.ONOSbench.startBasicONOS( nodeList=main.ONOSip, opSleep=200,
                                                    onosUser=main.ONOScli1.karafUser )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully started basic ONOS cluster ",
                                 onfail="Failed to start basic ONOS Cluster " )

        main.testSetUp.startOnosClis()

        main.step( "Activate onos apps.")
        main.apps = main.params['CASE10'].get( 'Apps' )
        if main.apps:
            main.log.info( "Apps to activate: " + main.apps )
            activateResult = main.TRUE
            for a in main.apps.split(","):
                activateResult = activateResult & main.ONOScli1.activateApp(a)
            # TODO: check this worked
            time.sleep( main.onosCfgSleep )  # wait for apps to activate
        else:
            main.log.warn( "No configurations were specified to be changed after startup" )
        utilities.assert_equals( expect=main.TRUE,
                                     actual=activateResult,
                                     onpass="Successfully set config",
                                     onfail="Failed to set config" )

        main.step( "Set ONOS configurations" )
        config = main.params['CASE10'].get( 'ONOS_Configuration' )
        if config:
            main.log.debug( config )
            checkResult = main.TRUE
            for component in config:
                for setting in config[component]:
                    value = config[component][setting]
                    check = main.ONOScli1.setCfg( component, setting, value )
                    main.log.info( "Value was changed? {}".format( main.TRUE == check ) )
                    checkResult = check and checkResult
            utilities.assert_equals( expect=main.TRUE,
                                     actual=checkResult,
                                     onpass="Successfully set config",
                                     onfail="Failed to set config" )
        else:
            main.log.warn( "No configurations were specified to be changed after startup" )

    def CASE11( self, main ):
        """
            Start mininet and assign controllers
        """
        import time

        topology = main.params['CASE11']['topo']
        main.log.report( "Start Mininet topology" )
        main.case( "Start Mininet topology" )

        main.step( "Starting Mininet Topology" )
        topoResult = main.Mininet1.startNet(mnCmd=topology )
        stepResult = topoResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanup()
            main.exit()

        main.step( "Assign switches to controllers.")
        assignResult = main.TRUE
        for i in range(1, 8):
            assignResult = assignResult & main.Mininet1.assignSwController( sw="s" + str( i ),
                                                         ip=main.ONOSip,
                                                         port='6653' )
        time.sleep(main.mnCfgSleep)
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully assign switches to controllers",
                                 onfail="Failed to assign switches to controllers" )


    def CASE12( self, main ):
        """
            Tests using through ONOS CLI handles
        """

        main.case( "Test some onos commands through CLI. ")
        main.log.debug( main.ONOScli1.sendline("summary") )
        main.log.debug( main.ONOScli3.sendline("devices") )

    def CASE22( self, main ):
        """
            Tests using ONOS REST API handles
        """

        main.case( " Sample tests using ONOS REST API handles. ")
        main.log.debug( main.ONOSrest1.send("/devices") )
        main.log.debug( main.ONOSrest2.apps() )

    def CASE32( self, main ):
        """
            Configure fwd app from .params json string with parameter configured
            Check if configuration successful
            Run pingall to check connectivity
            Check ONOS log for warning/error/exceptions
        """
        main.case( "Configure onos-app-fwd and check if configuration successful. " )
        main.step( "Install reactive forwarding app." )
        installResults = main.ONOScli1.activateApp( "org.onosproject.fwd" )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass= "Configure fwd successful", onfail= "Configure fwd failed" )
        main.step( "Run pingall to check connectivity. " )
        pingResult = main.FALSE
        passMsg = "Reactive Pingall test passed"
        pingResult = main.Mininet1.pingall()
        if not pingResult:
           main.log.warn("First pingall failed. Trying again...")
           pingResult = main.Mininet1.pingall()
           passMsg += "on the second try"
        utilities.assert_equals( expect=main.TRUE, actual=pingResult, onpass=passMsg, onfail= "Reactive Pingall failed, " + "one or more ping pairs failed" )
