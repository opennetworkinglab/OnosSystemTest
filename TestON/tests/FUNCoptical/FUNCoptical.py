# Testing the basic intent functionality of ONOS

class FUNCoptical:

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
            main.scale = ( main.params[ 'SCALE' ][ 'size' ] ).split( "," )
            if main.ONOSbench.maxNodes:
                main.maxNodes = int( main.ONOSbench.maxNodes )
            else:
                main.maxNodes = 0
            wrapperFile1 = main.params[ 'DEPENDENCY' ][ 'wrapper1' ]
            wrapperFile2 = main.params[ 'DEPENDENCY' ][ 'wrapper2' ]
            wrapperFile3 = main.params[ 'DEPENDENCY' ][ 'wrapper3' ]
            main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
            main.checkIntentSleep = int( main.params[ 'SLEEP' ][ 'checkintent' ] )
            main.removeIntentSleep = int( main.params[ 'SLEEP' ][ 'removeintent' ] )
            main.rerouteSleep = int( main.params[ 'SLEEP' ][ 'reroute' ] )
            main.fwdSleep = int( main.params[ 'SLEEP' ][ 'fwd' ] )
            main.checkTopoAttempts = int( main.params[ 'SLEEP' ][ 'topoAttempts' ] )
            gitPull = main.params[ 'GIT' ][ 'pull' ]
            main.numSwitch = int( main.params[ 'MININET' ][ 'switch' ] )
            main.numLinks = int( main.params[ 'MININET' ][ 'links' ] )
            main.cellData = {} # For creating cell file
            main.hostsData = {}
            main.CLIs = []
            main.ONOSip = []  # List of IPs of active ONOS nodes. CASE 2
            main.activeONOSip = []
            main.assertReturnString = ''  # Assembled assert return string

            main.ONOSip = main.ONOSbench.getOnosIps()

            # Assigning ONOS cli handles to a list
            for i in range( 1,  main.maxNodes + 1 ):
                main.CLIs.append( getattr( main, 'ONOScli' + str( i ) ) )

            # -- INIT SECTION, ONLY RUNS ONCE -- #
            main.startUp = imp.load_source( wrapperFile1,
                                            main.dependencyPath +
                                            wrapperFile1 +
                                            ".py" )

            main.intentFunction = imp.load_source( wrapperFile2,
                                            main.dependencyPath +
                                            wrapperFile2 +
                                            ".py" )

            main.topo = imp.load_source( wrapperFile3,
                                         main.dependencyPath +
                                         wrapperFile3 +
                                         ".py" )

            if main.CLIs:
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

        # main.scale[ 0 ] determines the current number of ONOS controller
        main.numCtrls = int( main.scale[ 0 ] )

        main.case( "Starting up " + str( main.numCtrls ) +
                   " node(s) ONOS cluster" )
        main.caseExplanation = "Set up ONOS with " + str( main.numCtrls ) +\
                                " node(s) ONOS cluster"



        #kill off all onos processes
        main.log.info( "Safety check, killing all ONOS processes" +
                       " before initiating environment setup" )

        for i in range( main.maxNodes ):
            main.ONOSbench.onosDie( main.ONOSip[ i ] )

        print "NODE COUNT = ", main.numCtrls

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

        time.sleep( main.startUpSleep )
        main.step( "Installing ONOS package" )
        onosInstallResult = main.TRUE
        for i in range( main.numCtrls ):
            onosInstallResult = onosInstallResult and \
                    main.ONOSbench.onosInstall( node=main.ONOSip[ i ] )
            # Populate activeONOSip
            main.activeONOSip.append( main.ONOSip[ i ] )
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

        # Remove the first element in main.scale list
        main.scale.remove( main.scale[ 0 ] )

        main.intentFunction.report( main )


    def CASE10( self, main ):
        """
            Start Mininet opticalTest Topology
        """
        main.case( "Mininet with Linc-OE startup")
        main.caseExplanation = "Start opticalTest.py topology included with ONOS"
        main.step( "Starting mininet and LINC-OE" )
        topoResult = main.TRUE
        time.sleep( 10 )
        controllerIPs = ' '.join( main.activeONOSip )
        opticalMnScript = main.LincOE.runOpticalMnScript(ctrllerIP = controllerIPs)
        topoResult = opticalMnScript
        utilities.assert_equals(
            expect=main.TRUE,
            actual=topoResult,
            onpass="Started the topology successfully ",
            onfail="Failed to start the topology")

        # Exit if topology did not load properly
        if not topoResult:
            main.cleanup()
            main.exit()

    


    def CASE14( self, main ):
        """
            Stop mininet
        """
        main.log.report( "Stop Mininet topology" )
        main.case( "Stop Mininet topology" )
        main.caseExplanation = "Stopping the current mininet topology " +\
                                "to start up fresh"

        main.step( "Stopping Mininet Topology" )
        topoResult = main.LincOE.stopNet( timeout=180 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=topoResult,
                                 onpass="Successfully stopped mininet",
                                 onfail="Failed to stopped mininet" )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanup()
            main.exit()

    def CASE21( self,main ):
        """
            Run pingall to discover all hosts
        """
        main.case( "Running Pingall" )
        main.caseExplanation = "Use pingall to discover all hosts. Pingall is expected to fail."
        main.step( "Discover Hosts through Pingall" )
        pingResult = main.LincOE.pingall( timeout = 600 )

        utilities.assert_equals( expect=main.FALSE,
                                 actual=pingResult,
                                 onpass="Pingall Completed",
                                 onfail="Pingall did not complete or did not return fales" )

    def CASE22( self,main ):
        """
            Send arpings to discover all hosts
        """
        main.case( "Discover Hosts with arping" )
        main.caseExplanation = "Send arpings between all the hosts to discover and verify them"

        main.step( "Send arping between all hosts" )

        hosts = [ "h1","h2","h3","h4","h5","h6" ]

        arpingHostResults = main.TRUE
        for host in hosts:
            if main.LincOE.arping( host ):
                main.log.info( "Successfully reached host {} with arping".format( host ) )
            else:
                main.log.error( "Could not reach host {} with arping".format( host ) )
                arpingHostResults = main.FALSE

        utilities.assert_equals( expect=main.TRUE,
                                 actual=arpingHostResults,
                                 onpass="Successfully discovered all hosts",
                                 onfail="Could not descover some hosts" )

    def CASE23( self, main ):
        """
        Compare ONOS Topology to Mininet Topology
        """
        import json

        main.case( "Compare ONOS Topology view to Mininet topology" )
        main.caseExplanation = "Compare topology elements between Mininet" +\
                                " and ONOS"

        main.log.info( "Gathering topology information from Mininet" )
        devicesResults = main.FALSE  # Overall Boolean for device correctness
        linksResults = main.FALSE  # Overall Boolean for link correctness
        hostsResults = main.FALSE  # Overall Boolean for host correctness
        deviceFails = []  # Nodes where devices are incorrect
        linkFails = []  # Nodes where links are incorrect
        hostFails = []  # Nodes where hosts are incorrect
        attempts = main.checkTopoAttempts  # Remaining Attempts

        mnSwitches = 16
        mnLinks = 46
        mnHosts = 6

        main.step( "Comparing Mininet topology to ONOS topology" )

        while ( attempts >= 0 ) and\
            ( not devicesResults or not linksResults or not hostsResults ):
            time.sleep( 2 )
            if not devicesResults:
                devices = main.topo.getAllDevices( main )
                ports = main.topo.getAllPorts( main )
                devicesResults = main.TRUE
                deviceFails = []  # Reset for each attempt
            if not linksResults:
                links = main.topo.getAllLinks( main )
                linksResults = main.TRUE
                linkFails = []  # Reset for each attempt
            if not hostsResults:
                hosts = main.topo.getAllHosts( main )
                hostsResults = main.TRUE
                hostFails = []  # Reset for each attempt

            #  Check for matching topology on each node
            for controller in range( main.numCtrls ):
                controllerStr = str( controller + 1 )  # ONOS node number
                # Compare Devices
                if devices[ controller ] and ports[ controller ] and\
                    "Error" not in devices[ controller ] and\
                    "Error" not in ports[ controller ]:

                    try:
                        deviceData = json.loads( devices[ controller ] )
                        portData = json.loads( ports[ controller ] )
                    except (TypeError,ValueError):
                        main.log.error("Could not load json:" + str( devices[ controller ] ) + ' or ' + str( ports[ controller ] ))
                        currentDevicesResult = main.FALSE
                    else:
                        if mnSwitches == len( deviceData ):
                            currentDevicesResult = main.TRUE
                        else:
                            currentDevicesResult = main.FALSE
                            main.log.error( "Node {} only sees {} device(s) but {} exist".format( 
                                controllerStr,len( deviceData ),mnSwitches ) )
                else:
                    currentDevicesResult = main.FALSE
                if not currentDevicesResult:
                    deviceFails.append( controllerStr )
                devicesResults = devicesResults and currentDevicesResult
                # Compare Links
                if links[ controller ] and "Error" not in links[ controller ]:
                    try:
                        linkData = json.loads( links[ controller ] )
                    except (TypeError,ValueError):
                        main.log.error("Could not load json:" + str( links[ controller ] ) )
                        currentLinksResult = main.FALSE
                    else:
                        if mnLinks == len( linkData ):
                            currentLinksResult = main.TRUE
                        else:
                            currentLinksResult = main.FALSE
                            main.log.error( "Node {} only sees {} link(s) but {} exist".format( 
                                controllerStr,len( linkData ),mnLinks ) )
                else:
                    currentLinksResult = main.FALSE
                if not currentLinksResult:
                    linkFails.append( controllerStr )
                linksResults = linksResults and currentLinksResult
                # Compare Hosts
                if hosts[ controller ] and "Error" not in hosts[ controller ]:
                    try:
                        hostData = json.loads( hosts[ controller ] )
                    except (TypeError,ValueError):
                        main.log.error("Could not load json:" + str( hosts[ controller ] ) )
                        currentHostsResult = main.FALSE
                    else:
                        if mnHosts == len( hostData ):
                            currentHostsResult = main.TRUE
                        else:
                            currentHostsResult = main.FALSE
                            main.log.error( "Node {} only sees {} host(s) but {} exist".format( 
                                controllerStr,len( hostData ),mnHosts ) )
                else:
                    currentHostsResult = main.FALSE
                if not currentHostsResult:
                    hostFails.append( controllerStr )
                hostsResults = hostsResults and currentHostsResult
            # Decrement Attempts Remaining
            attempts -= 1

        utilities.assert_equals( expect=[],
                                 actual=deviceFails,
                                 onpass="ONOS correctly discovered all devices",
                                 onfail="ONOS incorrectly discovered devices on nodes: " +
                                 str( deviceFails ) )
        utilities.assert_equals( expect=[],
                                 actual=linkFails,
                                 onpass="ONOS correctly discovered all links",
                                 onfail="ONOS incorrectly discovered links on nodes: " +
                                 str( linkFails ) )
        utilities.assert_equals( expect=[],
                                 actual=hostFails,
                                 onpass="ONOS correctly discovered all hosts",
                                 onfail="ONOS incorrectly discovered hosts on nodes: " +
                                 str( hostFails ) )
        if hostsResults and linksResults and devicesResults:
            topoResults = main.TRUE
        else:
            topoResults = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=topoResults,
                                 onpass="ONOS correctly discovered the topology",
                                 onfail="ONOS incorrectly discovered the topology" )


    def CASE31( self, main ):
        import time
        """
            Add bidirectional point intents between 2 packet layer( mininet )
            devices and ping mininet hosts
        """
        main.log.report(
            "This testcase adds bidirectional point intents between 2 " +
            "packet layer( mininet ) devices and ping mininet hosts" )
        main.case( "Install point intents between 2 packet layer device and " +
                   "ping the hosts" )
        main.caseExplanation = "This testcase adds bidirectional point intents between 2 " +\
            "packet layer( mininet ) devices and ping mininet hosts"

        main.step( "Adding point intents" )
        checkFlowResult = main.TRUE
        main.pIntentsId = []
        pIntent1 = main.CLIs[ 0 ].addPointIntent(
            "of:0000ffffffff0001/1",
            "of:0000ffffffff0005/1" )
        time.sleep( 10 )
        pIntent2 = main.CLIs[ 0 ].addPointIntent(
            "of:0000ffffffff0005/1",
            "of:0000ffffffff0001/1" )
        main.pIntentsId.append( pIntent1 )
        main.pIntentsId.append( pIntent2 )
        time.sleep( 10 )
        main.log.info( "Checking intents state")
        checkStateResult = main.CLIs[ 0 ].checkIntentState(
                                                  intentsId = main.pIntentsId )
        time.sleep( 10 )
        main.log.info( "Checking flows state")
        checkFlowResult = main.CLIs[ 0 ].checkFlowsState()
        # Sleep for 10 seconds to provide time for the intent state to change
        time.sleep( 10 )
        main.log.info( "Checking intents state one more time")
        checkStateResult = main.CLIs[ 0 ].checkIntentState(
                                                  intentsId = main.pIntentsId )
        
        if checkStateResult and checkFlowResult:
            addIntentsResult = main.TRUE
        else:
            addIntentsResult = main.FALSE
        utilities.assert_equals(
            expect=main.TRUE,
            actual=addIntentsResult,
            onpass="Successfully added point intents",
            onfail="Failed to add point intents")

        if not addIntentsResult:
            main.log.error( "Intents were not properly installed. Exiting case." )
            main.skipCase()

        main.step( "Ping h1 and h5" )
        pingResult = main.LincOE.pingHostOptical( src="h1", target="h5" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=pingResult,
            onpass="Successfully pinged h1 and h5",
            onfail="Failed to ping between h1 and h5")

    def CASE32( self ):
        """
            Add host intents between 2 packet layer host
        """
        import time
        import json
        main.log.report( "Adding host intents between 2 optical layer host" )
        main.case( "Test add host intents between optical layer host" )
        main.caseExplanation = "Test host intents between 2 optical layer host"

        main.step( "Adding host intents to h1 and h2" )
        hostMACs = []
        hostId = []
        # Listing host MAC addresses
        for i in range( 1 , 7 ):
            hostMACs.append( "00:00:00:00:00:" +
                                str( hex( i )[ 2: ] ).zfill( 2 ).upper() )
        for macs in hostMACs:
            hostId.append( macs + "/-1" )
        host1 = hostId[ 0 ]
        host2 = hostId[ 1 ]

        intentsId = []
        intent1 = main.CLIs[ 0 ].addHostIntent( hostIdOne = host1,
                                            hostIdTwo = host2 )
        intentsId.append( intent1 )
        # Checking intents state before pinging
        main.log.info( "Checking intents state" )
        intentResult = main.CLIs[ 0 ].checkIntentState( intentsId = intentsId )
        # Check intent state again if intents are not in installed state
        

        # If intent state is wrong, wait 3 sec and try again
        if not intentResult:
            time.sleep( 3 )
            intentResult = main.CLIs[ 0 ].checkIntentState( intentsId = intentsId )

        # If intent state is still wrong, display intent states
        if not intentResult:
            main.log.error( main.CLIs[ 0 ].intents() )
        
        utilities.assert_equals( expect=main.TRUE,
                                 actual=intentResult,
                                 onpass="All intents are in INSTALLED state ",
                                 onfail="Some of the intents are not in " +
                                        "INSTALLED state " )

        if not intentResult:
            main.log.error( "Intents were not properly installed. Skipping Ping" )
        else:
            # Pinging h1 to h2 and then ping h2 to h1
            main.step( "Pinging h1 and h2" )
            pingResult = main.TRUE
            pingResult = main.LincOE.pingHostOptical( src="h1", target="h2" ) \
                and main.LincOE.pingHostOptical( src="h2",target="h1" )
            
            utilities.assert_equals( expect=main.TRUE,
                                     actual=pingResult,
                                     onpass="Pinged successfully between h1 and h2",
                                     onfail="Pinged failed between h1 and h2" )

        # Removed all added host intents
        main.step( "Removing host intents" )
        removeResult = main.TRUE
        # Check remaining intents
        intentsJson = json.loads( main.CLIs[ 0 ].intents() )
        main.CLIs[ 0 ].removeIntent( intentId=intent1, purge=True )
        #main.CLIs[ 0 ].removeIntent( intentId=intent2, purge=True )
        for intents in intentsJson:
            main.CLIs[ 0 ].removeIntent( intentId=intents.get( 'id' ),
                                     app='org.onosproject.optical',
                                     purge=True )
        # Check if any intents could not be removed
        if len( json.loads( main.CLIs[ 0 ].intents() ) ):
            print json.loads( main.CLIs[ 0 ].intents() )
            removeResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=removeResult,
                                 onpass="Successfully removed host intents",
                                 onfail="Failed to remove host intents" )

