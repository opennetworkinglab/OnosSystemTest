# Testing the NETCONF protocol within ONOS

class FUNCnetconf:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        import time
        import imp
        import re

        """
        - Construct tests variables
        - GIT ( optional )
            - Checkout ONOS master branch
            - Pull latest ONOS code
        - Building ONOS ( optional )
            - Install ONOS package
            - Build ONOS package
        """

        main.case( "Constructing test variables and building ONOS package" )
        main.step( "Constructing test variables" )
        main.caseExplanation = "This test case is mainly for loading " +\
                               "from params file, and pull and build the " +\
                               " latest ONOS package"
        stepResult = main.FALSE

        # Test variables
        try:
            main.testOnDirectory = re.sub( "(/tests)$", "", main.testDir )
            main.apps = main.params[ 'ENV' ][ 'cellApps' ]
            gitBranch = main.params[ 'GIT' ][ 'branch' ]
            main.dependencyPath = main.testOnDirectory + \
                                  main.params[ 'DEPENDENCY' ][ 'path' ]
            # main.topology = main.params[ 'DEPENDENCY' ][ 'topology' ]
            main.scale = ( main.params[ 'SCALE' ][ 'size' ] ).split( "," )
            if main.ONOSbench.maxNodes:
                main.maxNodes = int( main.ONOSbench.maxNodes )
            else:
                main.maxNodes = 0
            wrapperFile1 = main.params[ 'DEPENDENCY' ][ 'wrapper1' ]
            wrapperFile2 = main.params[ 'DEPENDENCY' ][ 'wrapper2' ]
            wrapperFile3 = main.params[ 'DEPENDENCY' ][ 'wrapper3' ]
            main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
            main.switchSleep = int( main.params[ 'SLEEP' ][ 'upSwitch' ] )
            main.checkTopoAttempts = int( main.params[ 'SLEEP' ][ 'topoAttempts' ] )
            main.numSwitch = int( main.params[ 'MININET' ][ 'switch' ] )

            # Config file parameters
            main.configDevicePort = main.params[ 'CONFIGURE' ][ 'cfgDevicePort' ]
            main.configDriver = main.params[ 'CONFIGURE' ][ 'cfgDriver' ]
            main.configApps = main.params[ 'CONFIGURE' ][ 'cfgApps' ]
            main.configName = main.params[ 'CONFIGURE' ][ 'cfgName' ]
            main.configPass = main.params[ 'CONFIGURE' ][ 'cfgPass' ]
            main.configPort = main.params[ 'CONFIGURE' ][ 'cfgAppPort' ]
            main.cycle = 0 # How many times FUNCintent has run through its tests

            gitPull = main.params[ 'GIT' ][ 'pull' ]
            main.cellData = {} # for creating cell file
            main.hostsData = {}
            main.CLIs = []
            main.CLIs2 = []
            main.ONOSip = []
            main.assertReturnString = ''  # Assembled assert return string

            main.ONOSip = main.ONOSbench.getOnosIps()
            print main.ONOSip

            # Assigning ONOS cli handles to a list
            for i in range( 1,  main.maxNodes + 1 ):
                main.CLIs.append( getattr( main, 'ONOSrest' + str( i ) ) )
                main.CLIs2.append( getattr( main, 'ONOScli' + str( i ) ) )

            # -- INIT SECTION, ONLY RUNS ONCE -- #
            main.startUp = imp.load_source( wrapperFile1,
                                            main.dependencyPath +
                                            wrapperFile1 +
                                            ".py" )

            main.netconfFunction = imp.load_source( wrapperFile2,
                                            main.dependencyPath +
                                            wrapperFile2 +
                                            ".py" )

            main.topo = imp.load_source( wrapperFile3,
                                         main.dependencyPath +
                                         wrapperFile3 +
                                         ".py" )

            # Uncomment out the following if a mininet topology is added
            # copyResult1 = main.ONOSbench.scp( main.Mininet1,
            #                                   main.dependencyPath +
            #                                   main.topology,
            #                                   main.Mininet1.home + "custom/",
            #                                   direction="to" )

            if main.CLIs and main.CLIs2:
                stepResult = main.TRUE
            else:
                main.log.error( "Did not properly created list of ONOS CLI handle" )
                stepResult = main.FALSE
        except Exception as e:
            main.log.exception(e)
            main.cleanup()
            main.exit()

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully construct " +
                                        "test variables ",
                                 onfail="Failed to construct test variables" )

        if gitPull == 'True':
            main.step( "Building ONOS in " + gitBranch + " branch" )
            onosBuildResult = main.startUp.onosBuild( main, gitBranch )
            stepResult = onosBuildResult
            utilities.assert_equals( expect=main.TRUE,
                                     actual=stepResult,
                                     onpass="Successfully compiled " +
                                            "latest ONOS",
                                     onfail="Failed to compile " +
                                            "latest ONOS" )
        else:
            main.log.warn( "Did not pull new code so skipping mvn " +
                           "clean install" )
        main.ONOSbench.getVersion( report=True )

    def CASE2( self, main ):
        """
        - Set up cell
            - Create cell file
            - Set cell file
            - Verify cell file
        - Kill ONOS process
        - Uninstall ONOS cluster
        - Verify ONOS start up
        - Install ONOS cluster
        - Connect to cli
        """

        main.cycle += 1

        # main.scale[ 0 ] determines the current number of ONOS controller
        main.numCtrls = int( main.scale[ 0 ] )

        main.case( "Starting up " + str( main.numCtrls ) +
                   " node(s) ONOS cluster" )
        main.caseExplanation = "Set up ONOS with " + str( main.numCtrls ) +\
                                " node(s) ONOS cluster"



        #kill off all onos processes
        main.log.info( "Safety check, killing all ONOS processes" +
                       " before initiating environment setup" )



        time.sleep( main.startUpSleep )
        main.step( "Uninstalling ONOS package" )
        onosUninstallResult = main.TRUE
        for ip in main.ONOSip:
            onosUninstallResult = onosUninstallResult and \
                    main.ONOSbench.onosUninstall( nodeIp=ip )
        stepResult = onosUninstallResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully uninstalled ONOS package",
                                 onfail="Failed to uninstall ONOS package" )

        for i in range( main.maxNodes ):
            main.ONOSbench.onosDie( main.ONOSip[ i ] )

        main.log.info( "NODE COUNT = " + str( main.numCtrls ) )

        tempOnosIp = []
        for i in range( main.numCtrls ):
            tempOnosIp.append( main.ONOSip[i] )

        main.ONOSbench.createCellFile( main.ONOSbench.ip_address,
                                       "temp", main.Mininet1.ip_address,
                                       main.apps, tempOnosIp )

        main.step( "Apply cell to environment" )
        cellResult = main.ONOSbench.setCell( "temp" )
        verifyResult = main.ONOSbench.verifyCell()
        stepResult = cellResult and verifyResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully applied cell to " + \
                                        "environment",
                                 onfail="Failed to apply cell to environment " )

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()
        stepResult = packageResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully created ONOS package",
                                 onfail="Failed to create ONOS package" )

        time.sleep( main.startUpSleep )
        main.step( "Installing ONOS package" )
        onosInstallResult = main.TRUE
        for i in range( main.numCtrls ):
            onosInstallResult = onosInstallResult and \
                    main.ONOSbench.onosInstall( node=main.ONOSip[ i ], options="" )
        stepResult = onosInstallResult

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully installed ONOS package",
                                 onfail="Failed to install ONOS package" )

        time.sleep( main.startUpSleep )
        main.step( "Starting ONOS service" )
        stopResult = main.TRUE
        startResult = main.TRUE
        onosIsUp = main.TRUE

        for i in range( main.numCtrls ):
            onosIsUp = onosIsUp and main.ONOSbench.isup( main.ONOSip[ i ] )
        if onosIsUp == main.TRUE:
            main.log.report( "ONOS instance is up and ready" )
        else:
            main.log.report( "ONOS instance may not be up, stop and " +
                             "start ONOS again " )
            for i in range( main.numCtrls ):
                stopResult = stopResult and \
                        main.ONOSbench.onosStop( main.ONOSip[ i ] )
            for i in range( main.numCtrls ):
                startResult = startResult and \
                        main.ONOSbench.onosStart( main.ONOSip[ i ] )
        stepResult = onosIsUp and stopResult and startResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ONOS service is ready",
                                 onfail="ONOS service did not start properly" )

        # Start an ONOS cli to provide functionality that is not currently
        # supported by the Rest API remove this when Leader Checking is supported
        # by the REST API

        main.step( "Start ONOS cli" )
        cliResult = main.TRUE
        for i in range( main.numCtrls ):
            cliResult = cliResult and \
                        main.CLIs2[ i ].startOnosCli( main.ONOSip[ i ] )
        stepResult = cliResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully start ONOS cli",
                                 onfail="Failed to start ONOS cli" )

        # Remove the first element in main.scale list
        main.scale.remove( main.scale[ 0 ] )

    def CASE19( self, main ):
        """
            Copy the karaf.log files after each testcase cycle
        """
        main.log.report( "Copy karaf logs" )
        main.case( "Copy karaf logs" )
        main.caseExplanation = "Copying the karaf logs to preserve them through" +\
                               "reinstalling ONOS"
        main.step( "Copying karaf logs" )
        stepResult = main.TRUE
        scpResult = main.TRUE
        copyResult = main.TRUE
        i = 0
        for cli in main.CLIs2:
            main.node = cli
            ip = main.ONOSip[ i ]
            main.node.ip_address = ip
            scpResult = scpResult and main.ONOSbench.scp( main.node ,
                                            "/opt/onos/log/karaf.log",
                                            "/tmp/karaf.log",
                                            direction="from" )
            copyResult = copyResult and main.ONOSbench.cpLogsToDir( "/tmp/karaf.log", main.logdir,
                                                                    copyFileName=( "karaf.log.node{0}.cycle{1}".format( str( i + 1 ), str( main.cycle ) ) ) )
            if scpResult and copyResult:
                stepResult =  main.TRUE and stepResult
            else:
                stepResult = main.FALSE and stepResult
            i += 1
            if main.numCtrls == 1:
                break
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully copied remote ONOS logs",
                                 onfail="Failed to copy remote ONOS logs" )

    def CASE100( self, main ):
        """
            Start NETCONF app and OFC-Server or make sure that they are already running
        """
        assert main, "There is no main"
        assert main.CLIs, "There is no main.CLIs"
        assert main.numCtrls, "Placed the total number of switch topology in \
                                main.numCtrls"

        testResult = main.FALSE
        main.testName = "Start up NETCONF app in all nodes"
        main.case( main.testName + " Test - " + str( main.numCtrls ) +
                   " NODE(S)" )
        main.step( "Starting NETCONF app" )
        main.assertReturnString = "Assertion result for starting NETCONF app"
        testResult = main.netconfFunction.startApp( main )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "Starting OFC-Server" )
        main.assertReturnString = "Assertion result for starting OFC-Server"
        testResult = main.netconfFunction.startOFC( main )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )
        time.sleep( main.startUpSleep )

    def CASE200( self, main ):
        """
            Create or modify a Configuration file
                -The file is built from information loaded from the .params file
        """
        assert main, "There is no main"
        assert main.CLIs, "There is no main.CLIs"
        assert main.numCtrls, "Placed the total number of switch topology in \
                                main.numCtrls"

        main.testName = "Assemble the configuration"
        main.case( main.testName + " Test - " + str( main.numCtrls ) +
                   " NODES(S)" )
        main.step( "Assembling configuration file" )
        main.assertReturnString = "Assertion result for assembling configuration file"
        testResult = main.FALSE
        testResult = main.netconfFunction.createConfig( main )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )
        time.sleep( main.startUpSleep )

    def CASE300( self, main ):
        """
            Push a configuration and bring up a switch
        """
        assert main, "There is no main"
        assert main.CLIs, "There is no main.CLIs"
        assert main.numCtrls, "Placed the total number of switch topology in \
                                main.numCtrls"

        main.testName = "Uploading the configuration"
        main.case( main.testName + " Test - " + str( main.numCtrls ) +
                   " NODES(S)" )
        main.step( "Sending the configuration file")
        main.assertReturnString = "Assertion result for sending the configuration file"
        testResult = main.FALSE

        testResult = main.netconfFunction.sendConfig( main )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        time.sleep( main.switchSleep )

        main.step( "Confirming the device was configured" )
        main.assertReturnString = "Assertion result for confirming a configuration."
        testResult = main.FALSE

        testResult = main.netconfFunction.devices( main )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

    def CASE400( self, main ):
        """
            Bring down a switch
            This test case is not yet possible, but the functionality needed to
            perform it is planned to be added
                There is a message that is sent "Device () has closed session"
                when the device disconnects from onos for some reason.
                    Because of the triggers for this message are not practical
                    to activate this will likely not be used to implement the test
                    case at this time
            Possible ways to do this may include bringing down mininet then checking
            ONOS to see if it was recongnized the device being disconnected
        """
