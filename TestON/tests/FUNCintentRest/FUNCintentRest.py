
# Testing the basic intent functionality of ONOS

import time
import json

class FUNCintentRest:

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
            main.topology = main.params[ 'DEPENDENCY' ][ 'topology' ]
            main.scale = ( main.params[ 'SCALE' ][ 'size' ] ).split( "," )
            if main.ONOSbench.maxNodes:
                main.maxNodes = int( main.ONOSbench.maxNodes )
            else:
                main.maxNodes = 0
            wrapperFile1 = main.params[ 'DEPENDENCY' ][ 'wrapper1' ]
            wrapperFile2 = main.params[ 'DEPENDENCY' ][ 'wrapper2' ]
            wrapperFile3 = main.params[ 'DEPENDENCY' ][ 'wrapper3' ]
            main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
            main.checkIntentSleep = int( main.params[ 'SLEEP' ]\
                    [ 'checkintent' ] )
            main.rerouteSleep = int( main.params[ 'SLEEP' ][ 'reroute' ] )
            main.fwdSleep = int( main.params[ 'SLEEP' ][ 'fwd' ] )
            main.addIntentSleep = int( main.params[ 'SLEEP' ][ 'addIntent' ] )
            gitPull = main.params[ 'GIT' ][ 'pull' ]
            main.numSwitch = int( main.params[ 'MININET' ][ 'switch' ] )
            main.numLinks = int( main.params[ 'MININET' ][ 'links' ] )
            main.cellData = {} # for creating cell file
            main.hostsData = {}
            main.CLIs = []
            main.ONOSip = []

            main.ONOSip = main.ONOSbench.getOnosIps()

            # Assigning ONOS cli handles to a list
            try:
                for i in range( 1,  main.maxNodes + 1 ):
                    main.CLIs.append( getattr( main, 'ONOSrest' + str( i ) ) )
            except AttributeError:
                main.log.warn( "A " + str( main.maxNodes ) + " node cluster " +
                               "was defined in env variables, but only " +
                               str( len( main.CLIs ) ) +
                               " nodes were defined in the .topo file. " +
                               "Using " + str( len( main.CLIs ) ) +
                               " nodes for the test." )

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

            copyResult1 = main.ONOSbench.scp( main.Mininet1,
                                              main.dependencyPath +
                                              main.topology,
                                              main.Mininet1.home,
                                              direction="to" )
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

        # Remove the first element in main.scale list
        main.scale.remove( main.scale[ 0 ] )

    def CASE8( self, main ):
        """
        Compare Topo
        """
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

        main.step( "Comparing MN topology to ONOS topology" )
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
        main.log.info( "Error report: \n" )
        main.ONOSbench.logReport( globalONOSip[0],
                [ "INFO", "FOLLOWER", "WARN", "flow", "ERROR" , "Except" ],
                "s" )
        #main.ONOSbench.logReport( globalONOSip[1], [ "INFO" ], "d" )

    def CASE10( self, main ):
        """
            Start Mininet topology with OF 1.0 switches
        """
        main.OFProtocol = "1.0"
        main.log.report( "Start Mininet topology with OF 1.0 switches" )
        main.case( "Start Mininet topology with OF 1.0 switches" )
        main.caseExplanation = "Start mininet topology with OF 1.0 " +\
                                "switches to test intents, exits out if " +\
                                "topology did not start correctly"

        main.step( "Starting Mininet topology with OF 1.0 switches" )
        args = "--switch ovs,protocols=OpenFlow10"
        topoResult = main.Mininet1.startNet( topoFile=main.dependencyPath +
                                                      main.topology,
                                             args=args )
        stepResult = topoResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanup()
            main.exit()

    def CASE11( self, main ):
        """
            Start Mininet topology with OF 1.3 switches
        """
        main.OFProtocol = "1.3"
        main.log.report( "Start Mininet topology with OF 1.3 switches" )
        main.case( "Start Mininet topology with OF 1.3 switches" )
        main.caseExplanation = "Start mininet topology with OF 1.3 " +\
                                "switches to test intents, exits out if " +\
                                "topology did not start correctly"

        main.step( "Starting Mininet topology with OF 1.3 switches" )
        args = "--switch ovs,protocols=OpenFlow13"
        topoResult = main.Mininet1.startNet( topoFile=main.dependencyPath +
                                                      main.topology,
                                             args=args )
        stepResult = topoResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanup()
            main.exit()

    def CASE12( self, main ):
        """
            Assign mastership to controllers
        """
        import re

        main.case( "Assign switches to controllers" )
        main.step( "Assigning switches to controllers" )
        main.caseExplanation = "Assign OF " + main.OFProtocol +\
                                " switches to ONOS nodes"

        assignResult = main.TRUE
        switchList = []

        # Creates a list switch name, use getSwitch() function later...
        for i in range( 1, ( main.numSwitch + 1 ) ):
            switchList.append( 's' + str( i ) )

        tempONOSip = []
        for i in range( main.numCtrls ):
            tempONOSip.append( main.ONOSip[ i ] )

        assignResult = main.Mininet1.assignSwController( sw=switchList,
                                                         ip=tempONOSip,
                                                         port='6653' )
        if not assignResult:
            main.cleanup()
            main.exit()

        for i in range( 1, ( main.numSwitch + 1 ) ):
            response = main.Mininet1.getSwController( "s" + str( i ) )
            print( "Response is " + str( response ) )
            if re.search( "tcp:" + main.ONOSip[ 0 ], response ):
                assignResult = assignResult and main.TRUE
            else:
                assignResult = main.FALSE
        stepResult = assignResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully assigned switches" +
                                        "to controller",
                                 onfail="Failed to assign switches to " +
                                        "controller" )
    def CASE13( self, main ):
        """
            Discover all hosts and store its data to a dictionary
        """
        main.case( "Discover all hosts" )

        stepResult = main.TRUE
        main.step( "Discover all ipv4 host hosts " )
        hostList = []
        # List of host with default vlan
        defaultHosts = [ "h1", "h3", "h8", "h9", "h11", "h16", "h17", "h19", "h24" ]
        # Lists of host with unique vlan
        vlanHosts1 = [ "h4", "h12", "h20" ]
        vlanHosts2 = [ "h5", "h13", "h21" ]
        vlanHosts3 = [ "h6", "h14", "h22" ]
        vlanHosts4 = [ "h7", "h15", "h23" ]
        hostList.append( defaultHosts )
        hostList.append( vlanHosts1 )
        hostList.append( vlanHosts2 )
        hostList.append( vlanHosts3 )
        hostList.append( vlanHosts4 )

        stepResult = main.intentFunction.getHostsData( main, hostList )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully discovered hosts",
                                 onfail="Failed to discover hosts" )

    def CASE14( self, main ):
        """
            Stop mininet
        """
        main.log.report( "Stop Mininet topology" )
        main.case( "Stop Mininet topology" )
        main.caseExplanation = "Stopping the current mininet topology " +\
                                "to start up fresh"

        main.step( "Stopping Mininet Topology" )
        topoResult = main.Mininet1.stopNet( )
        stepResult = topoResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully stop mininet",
                                 onfail="Failed to stop mininet" )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanup()
            main.exit()

    def CASE1000( self, main ):
        """
            Add host intents between 2 host:
                - Discover hosts
                - Add host intents
                - Check intents
                - Verify flows
                - Ping hosts
                - Reroute
                    - Link down
                    - Verify flows
                    - Check topology
                    - Ping hosts
                    - Link up
                    - Verify flows
                    - Check topology
                    - Ping hosts
                - Remove intents
        """
        import time
        import json
        import re

        # Assert variables - These variable's name|format must be followed
        # if you want to use the wrapper function
        assert main, "There is no main"
        assert main.CLIs, "There is no main.CLIs"
        assert main.Mininet1, "Mininet handle should be named Mininet1"
        assert main.numSwitch, "Placed the total number of switch topology in \
                                main.numSwitch"

        main.case( "Host Intents Test - " + str( main.numCtrls ) +
                   " NODE(S) - OF " + main.OFProtocol )
        main.caseExplanation = "This test case tests Host intents using " +\
                                str( main.numCtrls ) + " node(s) cluster;\n" +\
                                "Different type of hosts will be tested in " +\
                                "each step such as IPV4, Dual stack, VLAN " +\
                                "etc;\nThe test will use OF " + main.OFProtocol\
                                + " OVS running in Mininet"

        main.step( "IPV4: Add host intents between h1 and h9" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.hostIntent( main,
                                              onosNode='0',
                                              name='IPV4',
                                              host1='h1',
                                              host2='h9',
                                              host1Id='00:00:00:00:00:01/-1',
                                              host2Id='00:00:00:00:00:09/-1',
                                              sw1='s5',
                                              sw2='s2',
                                              expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="IPV4: Host intent test successful " +
                                        "between two IPV4 hosts",
                                 onfail="IPV4: Host intent test failed " +
                                        "between two IPV4 hosts")

        main.step( "DUALSTACK1: Add host intents between h3 and h11" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.hostIntent( main,
                                              name='DUALSTACK',
                                              host1='h3',
                                              host2='h11',
                                              host1Id='00:00:00:00:00:03/-1',
                                              host2Id='00:00:00:00:00:0B/-1',
                                              sw1='s5',
                                              sw2='s2',
                                              expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="DUALSTACK: Host intent test " +
                                        "successful between two " +
                                        "dual stack host using IPV4",
                                 onfail="DUALSTACK: Host intent test " +
                                        "failed between two" +
                                        "dual stack host using IPV4" )


        main.step( "DUALSTACK2: Add host intents between h1 and h11" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.hostIntent( main,
                                              name='DUALSTACK2',
                                              host1='h1',
                                              host2='h11',
                                              sw1='s5',
                                              sw2='s2',
                                              expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="DUALSTACK2: Host intent test " +
                                        "successful between two " +
                                        "dual stack host using IPV4",
                                 onfail="DUALSTACK2: Host intent test " +
                                        "failed between two" +
                                        "dual stack host using IPV4" )

        main.step( "1HOP: Add host intents between h1 and h3" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.hostIntent( main,
                                              name='1HOP',
                                              host1='h1',
                                              host2='h3' )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="1HOP: Host intent test " +
                                        "successful between two " +
                                        "host using IPV4 in the same switch",
                                 onfail="1HOP: Host intent test " +
                                        "failed between two" +
                                        "host using IPV4 in the same switch" )

        main.step( "VLAN1: Add vlan host intents between h4 and h12" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.hostIntent( main,
                                              name='VLAN1',
                                              host1='h4',
                                              host2='h12',
                                              host1Id='00:00:00:00:00:04/100',
                                              host2Id='00:00:00:00:00:0C/100',
                                              sw1='s5',
                                              sw2='s2',
                                              expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="VLAN1: Host intent test " +
                                        "successful between two " +
                                        "host using IPV4 in the same VLAN",
                                 onfail="VLAN1: Host intent test " +
                                        "failed between two" +
                                        "host using IPV4 in the same VLAN" )

        main.step( "VLAN2: Add inter vlan host intents between h13 and h20" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.hostIntent( main,
                                              name='VLAN2',
                                              host1='h13',
                                              host2='h20' )

        utilities.assert_equals( expect=main.FALSE,
                                 actual=stepResult,
                                 onpass="VLAN2: Host intent negative test " +
                                        "successful between two " +
                                        "host using IPV4 in different VLAN",
                                 onfail="VLAN2: Host intent negative test " +
                                        "failed between two" +
                                        "host using IPV4 in different VLAN" )


    def CASE2000( self, main ):
        """
            Add point intents between 2 hosts:
                - Get device ids | ports
                - Add point intents
                - Check intents
                - Verify flows
                - Ping hosts
                - Reroute
                    - Link down
                    - Verify flows
                    - Check topology
                    - Ping hosts
                    - Link up
                    - Verify flows
                    - Check topology
                    - Ping hosts
                - Remove intents
        """
        import time
        import json
        import re

        # Assert variables - These variable's name|format must be followed
        # if you want to use the wrapper function
        assert main, "There is no main"
        assert main.CLIs, "There is no main.CLIs"
        assert main.Mininet1, "Mininet handle should be named Mininet1"
        assert main.numSwitch, "Placed the total number of switch topology in \
                                main.numSwitch"

        main.case( "Point Intents Test - " + str( main.numCtrls ) +
                   " NODE(S) - OF " + main.OFProtocol )
        main.caseExplanation = "This test case will test point to point" +\
                               " intents using " + str( main.numCtrls ) +\
                               " node(s) cluster;\n" +\
                               "Different type of hosts will be tested in " +\
                               "each step such as IPV4, Dual stack, VLAN etc" +\
                               ";\nThe test will use OF " + main.OFProtocol +\
                               " OVS running in Mininet"

        # No option point intents
        main.step( "NOOPTION: Add point intents between h1 and h9" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.pointIntent(
                                       main,
                                       name="NOOPTION",
                                       host1="h1",
                                       host2="h9",
                                       deviceId1="of:0000000000000005/1",
                                       deviceId2="of:0000000000000006/1",
                                       sw1="s5",
                                       sw2="s2",
                                       expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="NOOPTION: Point intent test " +
                                        "successful using no match action",
                                 onfail="NOOPTION: Point intent test " +
                                        "failed using no match action" )

        stepResult = main.TRUE
        main.step( "IPV4: Add point intents between h1 and h9" )
        stepResult = main.intentFunction.pointIntent(
                                       main,
                                       name="IPV4",
                                       host1="h1",
                                       host2="h9",
                                       deviceId1="of:0000000000000005/1",
                                       deviceId2="of:0000000000000006/1",
                                       port1="",
                                       port2="",
                                       ethType="IPV4",
                                       mac1="00:00:00:00:00:01",
                                       mac2="00:00:00:00:00:09",
                                       bandwidth="",
                                       lambdaAlloc=False,
                                       ipProto="",
                                       ip1="",
                                       ip2="",
                                       tcp1="",
                                       tcp2="",
                                       sw1="s5",
                                       sw2="s2",
                                       expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="IPV4: Point intent test " +
                                        "successful using IPV4 type with " +
                                        "MAC addresses",
                                 onfail="IPV4: Point intent test " +
                                        "failed using IPV4 type with " +
                                        "MAC addresses" )
        main.step( "IPV4_2: Add point intents between h1 and h9" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.pointIntent(
                                       main,
                                       name="IPV4_2",
                                       host1="h1",
                                       host2="h9",
                                       deviceId1="of:0000000000000005/1",
                                       deviceId2="of:0000000000000006/1",
                                       ipProto="",
                                       ip1="",
                                       ip2="",
                                       tcp1="",
                                       tcp2="",
                                       sw1="s5",
                                       sw2="s2",
                                       expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="IPV4_2: Point intent test " +
                                        "successful using IPV4 type with " +
                                        "no MAC addresses",
                                 onfail="IPV4_2: Point intent test " +
                                        "failed using IPV4 type with " +
                                        "no MAC addresses" )

        main.step( "SDNIP-ICMP: Add point intents between h1 and h9" )
        stepResult = main.TRUE
        mac1 = main.hostsData[ 'h1' ][ 'mac' ]
        mac2 = main.hostsData[ 'h9' ][ 'mac' ]
        try:
            ip1 = str( main.hostsData[ 'h1' ][ 'ipAddresses' ][ 0 ] ) + "/32"
            ip2 = str( main.hostsData[ 'h9' ][ 'ipAddresses' ][ 0 ] ) + "/32"
        except KeyError:
            main.log.debug( "Key Error getting IP addresses of h1 | h9 in" +
                            "main.hostsData" )
            ip1 = main.Mininet1.getIPAddress( 'h1')
            ip2 = main.Mininet1.getIPAddress( 'h9')

        ipProto = main.params[ 'SDNIP' ][ 'icmpProto' ]
        # Uneccessary, not including this in the selectors
        tcp1 = main.params[ 'SDNIP' ][ 'srcPort' ]
        tcp2 = main.params[ 'SDNIP' ][ 'dstPort' ]

        stepResult = main.intentFunction.pointIntent(
                                           main,
                                           name="SDNIP-ICMP",
                                           host1="h1",
                                           host2="h9",
                                           deviceId1="of:0000000000000005/1",
                                           deviceId2="of:0000000000000006/1",
                                           mac1=mac1,
                                           mac2=mac2,
                                           ethType="IPV4",
                                           ipProto=ipProto,
                                           ip1=ip1,
                                           ip2=ip2 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="SDNIP-ICMP: Point intent test " +
                                        "successful using IPV4 type with " +
                                        "IP protocol TCP enabled",
                                 onfail="SDNIP-ICMP: Point intent test " +
                                        "failed using IPV4 type with " +
                                        "IP protocol TCP enabled" )

        main.step( "SDNIP-TCP: Add point intents between h1 and h9" )
        stepResult = main.TRUE
        mac1 = main.hostsData[ 'h1' ][ 'mac' ]
        mac2 = main.hostsData[ 'h9' ][ 'mac' ]
        ip1 = str( main.hostsData[ 'h1' ][ 'ipAddresses' ][ 0 ] ) + "/32"
        ip2 = str( main.hostsData[ 'h9' ][ 'ipAddresses' ][ 0 ] ) + "/32"
        ipProto = main.params[ 'SDNIP' ][ 'tcpProto' ]
        tcp1 = main.params[ 'SDNIP' ][ 'srcPort' ]
        tcp2 = main.params[ 'SDNIP' ][ 'dstPort' ]

        stepResult = main.intentFunction.pointIntentTcp(
                                           main,
                                           name="SDNIP-TCP",
                                           host1="h1",
                                           host2="h9",
                                           deviceId1="of:0000000000000005/1",
                                           deviceId2="of:0000000000000006/1",
                                           mac1=mac1,
                                           mac2=mac2,
                                           ethType="IPV4",
                                           ipProto=ipProto,
                                           ip1=ip1,
                                           ip2=ip2,
                                           tcp1=tcp1,
                                           tcp2=tcp2 )

        utilities.assert_equals( expect=main.TRUE,
                             actual=stepResult,
                                 onpass="SDNIP-TCP: Point intent test " +
                                        "successful using IPV4 type with " +
                                        "IP protocol TCP enabled",
                                 onfail="SDNIP-TCP: Point intent test " +
                                        "failed using IPV4 type with " +
                                        "IP protocol TCP enabled" )

        main.step( "DUALSTACK1: Add point intents between h1 and h9" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.pointIntent(
                                       main,
                                       name="DUALSTACK1",
                                       host1="h3",
                                       host2="h11",
                                       deviceId1="of:0000000000000005",
                                       deviceId2="of:0000000000000006",
                                       port1="3",
                                       port2="3",
                                       ethType="IPV4",
                                       mac1="00:00:00:00:00:03",
                                       mac2="00:00:00:00:00:0B",
                                       bandwidth="",
                                       lambdaAlloc=False,
                                       ipProto="",
                                       ip1="",
                                       ip2="",
                                       tcp1="",
                                       tcp2="",
                                       sw1="s5",
                                       sw2="s2",
                                       expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="DUALSTACK1: Point intent test " +
                                        "successful using IPV4 type with " +
                                        "MAC addresses",
                                 onfail="DUALSTACK1: Point intent test " +
                                        "failed using IPV4 type with " +
                                        "MAC addresses" )

        main.step( "VLAN: Add point intents between h5 and h21" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.pointIntent(
                                       main,
                                       name="VLAN",
                                       host1="h5",
                                       host2="h21",
                                       deviceId1="of:0000000000000005/5",
                                       deviceId2="of:0000000000000007/5",
                                       port1="",
                                       port2="",
                                       ethType="IPV4",
                                       mac1="00:00:00:00:00:05",
                                       mac2="00:00:00:00:00:15",
                                       bandwidth="",
                                       lambdaAlloc=False,
                                       ipProto="",
                                       ip1="",
                                       ip2="",
                                       tcp1="",
                                       tcp2="",
                                       sw1="s5",
                                       sw2="s2",
                                       expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="VLAN1: Point intent test " +
                                        "successful using IPV4 type with " +
                                        "MAC addresses",
                                 onfail="VLAN1: Point intent test " +
                                        "failed using IPV4 type with " +
                                        "MAC addresses" )

        main.step( "1HOP: Add point intents between h1 and h3" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.hostIntent( main,
                                              name='1HOP',
                                              host1='h1',
                                              host2='h3' )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="1HOP: Point intent test " +
                                        "successful using IPV4 type with " +
                                        "no MAC addresses",
                                 onfail="1HOP: Point intent test " +
                                        "failed using IPV4 type with " +
                                        "no MAC addresses" )

    def CASE3000( self, main ):
        """
            Add single point to multi point intents
                - Get device ids
                - Add single point to multi point intents
                - Check intents
                - Verify flows
                - Ping hosts
                - Reroute
                    - Link down
                    - Verify flows
                    - Check topology
                    - Ping hosts
                    - Link up
                    - Verify flows
                    - Check topology
                    - Ping hosts
                - Remove intents
        """
        assert main, "There is no main"
        assert main.CLIs, "There is no main.CLIs"
        assert main.Mininet1, "Mininet handle should be named Mininet1"
        assert main.numSwitch, "Placed the total number of switch topology in \
                                main.numSwitch"

        main.case( "Single To Multi Point Intents Test - " +
                   str( main.numCtrls ) + " NODE(S) - OF " + main.OFProtocol )
        main.caseExplanation = "This test case will test single point to" +\
                               " multi point intents using " +\
                               str( main.numCtrls ) + " node(s) cluster;\n" +\
                               "Different type of hosts will be tested in " +\
                               "each step such as IPV4, Dual stack, VLAN etc" +\
                               ";\nThe test will use OF " + main.OFProtocol +\
                               " OVS running in Mininet"

        main.step( "NOOPTION: Add single point to multi point intents" )
        stepResult = main.TRUE
        hostNames = [ 'h8', 'h16', 'h24' ]
        devices = [ 'of:0000000000000005/8', 'of:0000000000000006/8', \
                    'of:0000000000000007/8' ]
        macs = [ '00:00:00:00:00:08', '00:00:00:00:00:10', '00:00:00:00:00:18' ]
        stepResult = main.intentFunction.singleToMultiIntent(
                                         main,
                                         name="NOOPTION",
                                         hostNames=hostNames,
                                         devices=devices,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="NOOPTION: Successfully added single "
                                        + " point to multi point intents" +
                                        " with no match action",
                                 onfail="NOOPTION: Failed to add single point"
                                        + " point to multi point intents" +
                                        " with no match action" )

        main.step( "IPV4: Add single point to multi point intents" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.singleToMultiIntent(
                                         main,
                                         name="IPV4",
                                         hostNames=hostNames,
                                         devices=devices,
                                         ports=None,
                                         ethType="IPV4",
                                         macs=macs,
                                         bandwidth="",
                                         lambdaAlloc=False,
                                         ipProto="",
                                         ipAddresses="",
                                         tcp="",
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="IPV4: Successfully added single "
                                        + " point to multi point intents" +
                                        " with IPV4 type and MAC addresses",
                                 onfail="IPV4: Failed to add single point"
                                        + " point to multi point intents" +
                                        " with IPV4 type and MAC addresses" )

        main.step( "IPV4_2: Add single point to multi point intents" )
        stepResult = main.TRUE
        hostNames = [ 'h8', 'h16', 'h24' ]
        stepResult = main.intentFunction.singleToMultiIntent(
                                         main,
                                         name="IPV4",
                                         hostNames=hostNames,
                                         ethType="IPV4",
                                         lambdaAlloc=False )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="IPV4_2: Successfully added single "
                                        + " point to multi point intents" +
                                        " with IPV4 type and no MAC addresses",
                                 onfail="IPV4_2: Failed to add single point"
                                        + " point to multi point intents" +
                                        " with IPV4 type and no MAC addresses" )

        main.step( "VLAN: Add single point to multi point intents" )
        stepResult = main.TRUE
        hostNames = [ 'h4', 'h12', 'h20' ]
        devices = [ 'of:0000000000000005/4', 'of:0000000000000006/4', \
                    'of:0000000000000007/4' ]
        macs = [ '00:00:00:00:00:04', '00:00:00:00:00:0C', '00:00:00:00:00:14' ]
        stepResult = main.intentFunction.singleToMultiIntent(
                                         main,
                                         name="VLAN",
                                         hostNames=hostNames,
                                         devices=devices,
                                         ports=None,
                                         ethType="IPV4",
                                         macs=macs,
                                         bandwidth="",
                                         lambdaAlloc=False,
                                         ipProto="",
                                         ipAddresses="",
                                         tcp="",
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="VLAN: Successfully added single "
                                        + " point to multi point intents" +
                                        " with IPV4 type and MAC addresses" +
                                        " in the same VLAN",
                                 onfail="VLAN: Failed to add single point"
                                        + " point to multi point intents" +
                                        " with IPV4 type and MAC addresses" +
                                        " in the same VLAN")

    def CASE4000( self, main ):
        """
            Add multi point to single point intents
                - Get device ids
                - Add multi point to single point intents
                - Check intents
                - Verify flows
                - Ping hosts
                - Reroute
                    - Link down
                    - Verify flows
                    - Check topology
                    - Ping hosts
                    - Link up
                    - Verify flows
                    - Check topology
                    - Ping hosts
             - Remove intents
        """
        assert main, "There is no main"
        assert main.CLIs, "There is no main.CLIs"
        assert main.Mininet1, "Mininet handle should be named Mininet1"
        assert main.numSwitch, "Placed the total number of switch topology in \
                                main.numSwitch"

        main.case( "Multi To Single Point Intents Test - " +
                   str( main.numCtrls ) + " NODE(S) - OF " + main.OFProtocol )
        main.caseExplanation = "This test case will test single point to" +\
                               " multi point intents using " +\
                               str( main.numCtrls ) + " node(s) cluster;\n" +\
                               "Different type of hosts will be tested in " +\
                               "each step such as IPV4, Dual stack, VLAN etc" +\
                               ";\nThe test will use OF " + main.OFProtocol +\
                               " OVS running in Mininet"

        main.step( "NOOPTION: Add multi point to single point intents" )
        stepResult = main.TRUE
        hostNames = [ 'h8', 'h16', 'h24' ]
        devices = [ 'of:0000000000000005/8', 'of:0000000000000006/8', \
                    'of:0000000000000007/8' ]
        macs = [ '00:00:00:00:00:08', '00:00:00:00:00:10', '00:00:00:00:00:18' ]
        stepResult = main.intentFunction.multiToSingleIntent(
                                         main,
                                         name="NOOPTION",
                                         hostNames=hostNames,
                                         devices=devices,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="NOOPTION: Successfully added multi "
                                        + " point to single point intents" +
                                        " with no match action",
                                 onfail="NOOPTION: Failed to add multi point" +
                                        " to single point intents" +
                                        " with no match action" )

        main.step( "IPV4: Add multi point to single point intents" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.multiToSingleIntent(
                                         main,
                                         name="IPV4",
                                         hostNames=hostNames,
                                         devices=devices,
                                         ports=None,
                                         ethType="IPV4",
                                         macs=macs,
                                         bandwidth="",
                                         lambdaAlloc=False,
                                         ipProto="",
                                         ipAddresses="",
                                         tcp="",
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="IPV4: Successfully added multi point"
                                        + " to single point intents" +
                                        " with IPV4 type and MAC addresses",
                                 onfail="IPV4: Failed to add multi point" +
                                        " to single point intents" +
                                        " with IPV4 type and MAC addresses" )

        main.step( "IPV4_2: Add multi point to single point intents" )
        stepResult = main.TRUE
        hostNames = [ 'h8', 'h16', 'h24' ]
        stepResult = main.intentFunction.multiToSingleIntent(
                                         main,
                                         name="IPV4",
                                         hostNames=hostNames,
                                         ethType="IPV4",
                                         lambdaAlloc=False )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="IPV4_2: Successfully added multi point"
                                        + " to single point intents" +
                                        " with IPV4 type and no MAC addresses",
                                 onfail="IPV4_2: Failed to add multi point" +
                                        " to single point intents" +
                                        " with IPV4 type and no MAC addresses" )

        main.step( "VLAN: Add multi point to single point intents" )
        stepResult = main.TRUE
        hostNames = [ 'h5', 'h13', 'h21' ]
        devices = [ 'of:0000000000000005/5', 'of:0000000000000006/5', \
                    'of:0000000000000007/5' ]
        macs = [ '00:00:00:00:00:05', '00:00:00:00:00:0D', '00:00:00:00:00:15' ]
        stepResult = main.intentFunction.multiToSingleIntent(
                                         main,
                                         name="VLAN",
                                         hostNames=hostNames,
                                         devices=devices,
                                         ports=None,
                                         ethType="IPV4",
                                         macs=macs,
                                         bandwidth="",
                                         lambdaAlloc=False,
                                         ipProto="",
                                         ipAddresses="",
                                         tcp="",
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="VLAN: Successfully added multi point"
                                        + " to single point intents" +
                                        " with IPV4 type and MAC addresses" +
                                        " in the same VLAN",
                                 onfail="VLAN: Failed to add multi point" +
                                        " to single point intents" )

    def CASE5000( self, main ):
        """
        Will add description in next patch set
        """
        assert main, "There is no main"
        assert main.CLIs, "There is no main.CLIs"
        assert main.Mininet1, "Mininet handle should be named Mininet1"
        assert main.numSwitch, "Placed the total number of switch topology in \
                                main.numSwitch"
        main.case( "Test host mobility with host intents " )
        main.step( " Testing host mobility by moving h1 from s5 to s6" )
        h1PreMove = main.hostsData[ "h1" ][ "location" ][ 0:19 ]

        main.log.info( "Moving h1 from s5 to s6")

        main.Mininet1.moveHost( "h1","s5","s6" )

        main.intentFunction.getHostsData( main )
        h1PostMove = main.hostsData[ "h1" ][ "location" ][ 0:19 ]

        utilities.assert_equals( expect="of:0000000000000006",
                                 actual=h1PostMove,
                                 onpass="Mobility: Successfully moved h1 to s6",
                                 onfail="Mobility: Failed to moved h1 to s6" +
                                        " to single point intents" +
                                        " with IPV4 type and MAC addresses" +
                                        " in the same VLAN" )

        main.step( "IPV4: Add host intents between h1 and h9" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.hostIntent( main,
                                              onosNode='0',
                                              name='IPV4',
                                              host1='h1',
                                              host2='h9',
                                              host1Id='00:00:00:00:00:01/-1',
                                              host2Id='00:00:00:00:00:09/-1' )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="IPV4: Host intent test successful " +
                                        "between two IPV4 hosts",
                                 onfail="IPV4: Host intent test failed " +
                                        "between two IPV4 hosts")
