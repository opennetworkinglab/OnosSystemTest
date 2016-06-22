
# This is a sample template that starts up ONOS cluster, this template
# can be use as a base script for ONOS System Testing.

class SAMPstartTemplate_1node:

    def __init__( self ):
        self.default = ''


    def CASE0(self, main):
        '''
            Pull specific ONOS branch, then Build ONOS on ONOS Bench.
            This step is usually skipped. Because in a Jenkins driven automated
            test env. We want Jenkins jobs to pull&build for flexibility to handle
            different versions of ONOS.
        '''
        gitPull = main.params['CASE0']['gitPull']
        gitBranch = main.params['CASE0']['gitBranch']

        main.case("Pull onos branch and build onos on Teststation.")

        if gitPull == 'True':
            main.step( "Git Checkout ONOS branch: " + gitBranch)
            stepResult = main.ONOSbench.gitCheckout( branch = gitBranch )
            utilities.assert_equals( expect=main.TRUE,
                                     actual=stepResult,
                                     onpass="Successfully checkout onos branch.",
                                     onfail="Failed to checkout onos branch. Exiting test..." )
            if not stepResult: main.exit()

            main.step( "Git Pull on ONOS branch:" + gitBranch)
            stepResult = main.ONOSbench.gitPull( )
            utilities.assert_equals( expect=main.TRUE,
                                     actual=stepResult,
                                     onpass="Successfully pull onos. ",
                                     onfail="Failed to pull onos. Exiting test ..." )
            if not stepResult: main.exit()

            main.step( "Building ONOS branch: " + gitBranch )
            stepResult = main.ONOSbench.cleanInstall( skipTest = True )
            utilities.assert_equals( expect=main.TRUE,
                                     actual=stepResult,
                                     onpass="Successfully build onos.",
                                     onfail="Failed to build onos. Exiting test..." )
            if not stepResult: main.exit()

        else:
            main.log.warn( "Skipped pulling onos and Skipped building ONOS" )


    def CASE1( self, main ):
        '''
            Set up global test variables;
            Uninstall all running cells in test env defined in .topo file

        '''

        main.case( "Constructing global test variables and clean cluster env." )

        main.step( "Constructing test variables" )
        main.branch = main.ONOSbench.getBranchName()
        main.log.info( "Running onos branch: " + main.branch )
        main.commitNum = main.ONOSbench.getVersion().split(' ')[1]
        main.log.info( "Running onos commit Number: " + main.commitNum)
        main.nodeList = main.params['CASE1']['NodeList'].split(",")
        main.onosStartupSleep = float( main.params['CASE1']['SleepTimers']['onosStartup'] )
        main.onosCfgSleep = float( main.params['CASE1']['SleepTimers']['onosCfg'] )
        main.mnStartupSleep = float( main.params['CASE1']['SleepTimers']['mnStartup'] )
        main.mnCfgSleep = float( main.params['CASE1']['SleepTimers']['mnCfg'] )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=main.TRUE,
                                 onpass="Successfully construct " +
                                        "test variables ",
                                 onfail="Failed to construct test variables" )



        main.step( "Uninstall all onos nodes in the env.")
        stepResult = main.TRUE
        for node in main.nodeList:
            nodeResult = main.ONOSbench.onosUninstall( nodeIp = "$" + node )
            stepResult = stepResult & nodeResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully uninstall onos on all nodes in env.",
                                 onfail="Failed to uninstall onos on all nodes in env!" )
        if not stepResult:
            main.log.error( "Failure to clean test env. Exiting test..." )
            main.exit()

    def CASE2( self, main ):
        '''
            Report errors/warnings/exceptions
        '''
        main.log.info("Error report: \n" )
        main.ONOSbench.logReport( main.ONOScli1.ip_address,
                                  [ "INFO",
                                    "FOLLOWER",
                                    "WARN",
                                    "flow",
                                    "ERROR",
                                    "Except" ],
                                  "s" )

    def CASE10( self, main ):
        """
        Start ONOS cluster (1 node in this example) in three steps:
        1) start a basic cluster with drivers app via ONOSDriver;
        2) activate apps via ONOSCliDriver;
        3) configure onos via ONOSCliDriver;
        """

        import time

        numNodes = int( main.params['CASE10']['numNodes'] )
        main.case( "Start up " + str( numNodes ) + "-node onos cluster.")

        main.step( "Start ONOS cluster with basic (drivers) app.")
        onosClusterIPs = []
        for n in range( 1, numNodes + 1 ):
            handle = "main.ONOScli" + str( n )
            onosClusterIPs.append( eval( handle ).ip_address )

        stepResult = main.ONOSbench.startBasicONOS(nodeList = onosClusterIPs, opSleep = 200 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully started basic ONOS cluster ",
                                 onfail="Failed to start basic ONOS Cluster " )

        main.step( "Establishing Handles on ONOS CLIs.")
        cliResult = main.TRUE
        for n in range( 1, numNodes + 1 ):
            handle = "main.ONOScli" + str( n )
            cliResult = cliResult & ( eval( handle ).startCellCli() )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=cliResult,
                                 onpass="Successfully started onos cli's ",
                                 onfail="Failed to start onos cli's " )

        main.step( "Activate onos apps.")
        apps = main.params['CASE10'].get( 'Apps' )
        if apps:
            main.log.info( "Apps to activate: " + apps )
            activateResult = main.TRUE
            for a in apps.split(","):
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
        topoResult = main.Mininet1.startNet( mnCmd=topology )
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
        onosNodes = [ main.ONOScli1.ip_address ]
        for i in range(1, 8):
            assignResult = assignResult & main.Mininet1.assignSwController( sw="s" + str( i ),
                                                         ip=onosNodes,
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
        main.log.debug( main.ONOScli1.sendline("devices") )

    def CASE22( self, main ):
        """
            Tests using ONOS REST API handles
        """

        main.case( " Sample tests using ONOS REST API handles. ")
        main.log.debug( main.ONOSrest1.send("/devices") )
        main.log.debug( main.ONOSrest1.apps() )

    def CASE32( self, main ):
        """
            Configure fwd app from .param json string with parameter configured.
            Check if configuration successful
            Run pingall to check connectivity
            Check ONOS log for warning/error/exceptions
        """
        main.case( "Configure onos-app-fwd and check if configuration successful. " )
        main.step( "Install reactive forwarding app." )
        installResults = main.ONOScli1.activateApp( "org.onosproject.fwd" )
        utilities.assert_equals( expect=main.TRUE, actual=installResults,
                                 onpass = "Configure fwd successful", onfail="Configure fwd failed" )
        main.step( "Run pingall to check connectivity. " )
        pingResult = main.FALSE
        passMsg = "Reactive Pingall test passed"
        pingResult = main.Mininet1.pingall()
        if not pingResult:
           main.log.warn( "First pingall failed. Trying again..." )
           pingResult = main.Mininet1.pingall()
           passMsg += "on the second try"
        utilities.assert_equals( expect=main.TRUE, actual=pingResult, onpass=passMsg, onfail= "Reactive Pingall failed, " + "one or more ping pairs failed." )
