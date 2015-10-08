class FUNCflow:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        import time
        import os
        import imp

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
        stepResult = main.FALSE

        # Test variables
        main.testOnDirectory = os.path.dirname( os.getcwd ( ) )
        main.cellName = main.params[ 'ENV' ][ 'cellName' ]
        main.apps = main.params[ 'ENV' ][ 'cellApps' ]
        gitBranch = main.params[ 'GIT' ][ 'branch' ]
        main.dependencyPath = main.testOnDirectory + \
                              main.params[ 'DEPENDENCY' ][ 'path' ]
        main.topology = main.params[ 'DEPENDENCY' ][ 'topology' ]
        main.maxNodes = int( main.params[ 'SCALE' ][ 'max' ] )
        main.ONOSport = main.params[ 'CTRL' ][ 'port' ]
        main.numSwitches = int( main.params[ 'TOPO' ][ 'numSwitches' ] )
        main.numHosts = int( main.params[ 'TOPO' ][ 'numHosts' ] )
        main.numLinks = int( main.params[ 'TOPO' ][ 'numLinks' ] )
        wrapperFile1 = main.params[ 'DEPENDENCY' ][ 'wrapper1' ]
        wrapperFile2 = main.params[ 'DEPENDENCY' ][ 'wrapper2' ]
        main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
        gitPull = main.params[ 'GIT' ][ 'pull' ]
        main.cellData = {} # for creating cell file
        main.CLIs = []
        main.ONOSip = []

        main.ONOSip = main.ONOSbench.getOnosIps()
        print main.ONOSip

        # Assigning ONOS cli handles to a list
        for i in range( 1,  main.maxNodes + 1 ):
            main.CLIs.append( getattr( main, 'ONOScli' + str( i ) ) )

        # -- INIT SECTION, ONLY RUNS ONCE -- #
        main.startUp = imp.load_source( wrapperFile1,
                                        main.dependencyPath +
                                        wrapperFile1 +
                                        ".py" )

        main.topo = imp.load_source( wrapperFile2,
                                     main.dependencyPath +
                                     wrapperFile2 +
                                     ".py" )

        copyResult = main.ONOSbench.scp( main.Mininet1,
                                         main.dependencyPath+main.topology,
                                         main.Mininet1.home+'/custom/',
                                         direction="to" )

        if main.CLIs:
            stepResult = main.TRUE
        else:
            main.log.error( "Did not properly created list of ONOS CLI handle" )
            stepResult = main.FALSE

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

        main.numCtrls = int( main.maxNodes )

        main.case( "Starting up " + str( main.numCtrls ) +
                   " node(s) ONOS cluster" )

        #kill off all onos processes
        main.log.info( "Safety check, killing all ONOS processes" +
                       " before initiating enviornment setup" )

        for i in range( main.maxNodes ):
            main.ONOSbench.onosDie( main.ONOSip[ i ] )

        print "NODE COUNT = ", main.numCtrls

        tempOnosIp = []
        for i in range( main.numCtrls ):
            tempOnosIp.append( main.ONOSip[i] )

        main.ONOSbench.createCellFile( main.ONOSbench.ip_address, "temp", main.Mininet1.ip_address, main.apps, tempOnosIp )

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
        main.step( "Uninstalling ONOS package" )
        onosUninstallResult = main.TRUE
        for i in range( main.numCtrls ):
            onosUninstallResult = onosUninstallResult and \
                    main.ONOSbench.onosUninstall( nodeIp=main.ONOSip[ i ] )
        stepResult = onosUninstallResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully uninstalled ONOS package",
                                 onfail="Failed to uninstall ONOS package" )

        time.sleep( main.startUpSleep )
        main.step( "Installing ONOS package" )
        onosInstallResult = main.TRUE
        for i in range( main.numCtrls ):
            onosInstallResult = onosInstallResult and \
                    main.ONOSbench.onosInstall( node=main.ONOSip[ i ] )
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

        main.step( "Start ONOS cli" )
        cliResult = main.TRUE
        for i in range( main.numCtrls ):
            cliResult = cliResult and \
                        main.CLIs[ i ].startOnosCli( main.ONOSip[ i ] )
        stepResult = cliResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully start ONOS cli",
                                 onfail="Failed to start ONOS cli" )

    def CASE8( self, main ):
        '''
            Compare topology
        '''
        import json

        main.case( "Compare ONOS Topology view to Mininet topology" )
        main.caseExplanation = "Compare topology elements between Mininet" +\
                                " and ONOS"

        main.step( "Gathering topology information" )
        # TODO: add a paramaterized sleep here
        devicesResults = main.TRUE
        linksResults = main.TRUE
        hostsResults = main.TRUE
        devices = main.topo.getAllDevices( main )
        hosts = main.topo.getAllHosts( main )
        ports = main.topo.getAllPorts( main )
        links = main.topo.getAllLinks( main )
        clusters = main.topo.getAllClusters( main )

        mnSwitches = main.Mininet1.getSwitches()
        mnLinks = main.Mininet1.getLinks()
        mnHosts = main.Mininet1.getHosts()

        main.step( "Conmparing MN topology to ONOS topology" )
        for controller in range( main.numCtrls ):
            controllerStr = str( controller + 1 )
            if devices[ controller ] and ports[ controller ] and\
                "Error" not in devices[ controller ] and\
                "Error" not in ports[ controller ]:

                currentDevicesResult = main.Mininet1.compareSwitches(
                        mnSwitches,
                        json.loads( devices[ controller ] ),
                        json.loads( ports[ controller ] ) )
            else:
                currentDevicesResult = main.FALSE
            utilities.assert_equals( expect=main.TRUE,
                                     actual=currentDevicesResult,
                                     onpass="ONOS" + controllerStr +
                                     " Switches view is correct",
                                     onfail="ONOS" + controllerStr +
                                     " Switches view is incorrect" )
            if links[ controller ] and "Error" not in links[ controller ]:
                currentLinksResult = main.Mininet1.compareLinks(
                        mnSwitches, mnLinks,
                        json.loads( links[ controller ] ) )
            else:
                currentLinksResult = main.FALSE
            utilities.assert_equals( expect=main.TRUE,
                                     actual=currentLinksResult,
                                     onpass="ONOS" + controllerStr +
                                     " links view is correct",
                                     onfail="ONOS" + controllerStr +
                                     " links view is incorrect" )

            if hosts[ controller ] or "Error" not in hosts[ controller ]:
                currentHostsResult = main.Mininet1.compareHosts(
                        mnHosts,
                        json.loads( hosts[ controller ] ) )
            else:
                currentHostsResult = main.FALSE
            utilities.assert_equals( expect=main.TRUE,
                                     actual=currentHostsResult,
                                     onpass="ONOS" + controllerStr +
                                     " hosts exist in Mininet",
                                     onfail="ONOS" + controllerStr +
                                     " hosts don't match Mininet" )

    def CASE9( self, main ):
        '''
            Report errors/warnings/exceptions
        '''
        main.log.info("Error report: \n" )
        main.ONOSbench.logReport( main.ONOSip[ 0 ],
                                  [ "INFO",
                                    "FOLLOWER",
                                    "WARN",
                                    "flow",
                                    "ERROR",
                                    "Except" ],
                                 "s" )

    def CASE10( self, main ):
        '''
            Start Mininet with
        '''
        main.case( "Setup mininet and assign switches to controllers" )
        main.step( "Setup Mininet Topology" )
        topology = main.Mininet1.home + '/custom/' + main.topology
        stepResult1 = main.Mininet1.startNet( topoFile=topology )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult1,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )

        main.step( "Assign switches to controllers" )
        for i in range( main.numSwitches ):
            stepResult2 = main.Mininet1.assignSwController(
                                            sw="s" + str( i+1 ),
                                            ip=main.ONOSip )
            if not stepResult2:
                break

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult2,
                                 onpass="Controller assignment successfull",
                                 onfail="Controller assignment failed" )

        time.sleep(5)

        main.step( "Pingall hosts for discovery" )
        stepResult3 = main.Mininet1.pingall()
        if not stepResult3:
            stepResult3 = main.Mininet1.pingall()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult3,
                                 onpass="Pingall successfull",
                                 onfail="Pingall unsuccessfull" )

        caseResult = stepResult1 and stepResult2 and stepResult3
        if not caseResult:
            main.cleanup()
            main.exit()

    def CASE1000( self, main ):
        '''
            Add flows
        '''

    def CASE2000( self, main ):
        '''
            Delete flows
        '''

    def CASE3000( self, main ):
        '''
            Modify flow rule selectors
        '''

    def CASE4000( self, main ):
        '''
            Modify flow rule treatment
        '''

    def CASE5000( self, main ):
        '''
            Modify flow rule controller
        '''

    def CASE100( self, main ):
        '''
            Compare switch flow table with ONOS
        '''

