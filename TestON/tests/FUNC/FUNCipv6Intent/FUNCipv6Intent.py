# Testing the basic intent for ipv6 functionality of ONOS

class FUNCipv6Intent:

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
            main.checkIntentSleep = int( main.params[ 'SLEEP' ][ 'checkintent' ] )
            main.removeIntentSleep = int( main.params[ 'SLEEP' ][ 'removeintent' ] )
            main.rerouteSleep = int( main.params[ 'SLEEP' ][ 'reroute' ] )
            main.fwdSleep = int( main.params[ 'SLEEP' ][ 'fwd' ] )
            main.checkTopoAttempts = int( main.params[ 'SLEEP' ][ 'topoAttempts' ] )
            gitPull = main.params[ 'GIT' ][ 'pull' ]
            main.numSwitch = int( main.params[ 'MININET' ][ 'switch' ] )
            main.numLinks = int( main.params[ 'MININET' ][ 'links' ] )
            main.cellData = {} # for creating cell file
            main.hostsData = {}
            main.CLIs = []
            main.ONOSip = []
            main.assertReturnString = ''  # Assembled assert return string

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

        main.step( "Checking that ONOS is ready" )
        for i in range( 3 ):
            ready = True
            for i in range( int( main.scale[ 0 ] ) ):
                output = main.CLIs[ i ].summary()
                if not output:
                    ready = False
            time.sleep( 30 )
        utilities.assert_equals( expect=True, actual=ready,
                                 onpass="ONOS summary command succeded",
                                 onfail="ONOS summary command failed" )
        if not ready:
            main.cleanup()
            main.exit()

        main.step( "setup the ipv6NeighbourDiscovery" )
        cfgResult1 = main.CLIs[0].setCfg( "org.onosproject.proxyarp.ProxyArp", "ipv6NeighborDiscovery", "true" )
        cfgResult2 = main.CLIs[0].setCfg( "org.onosproject.provider.host.impl.HostLocationProvider", "ipv6NeighborDiscovery", "true" )
        cfgResult = cfgResult1 and cfgResult2
        utilities.assert_equals( expect=main.TRUE, actual=cfgResult,
                                onpass="ipv6NeighborDiscovery cfg is set to true",
                                onfail="Failed to cfg set ipv6NeighborDiscovery" )

        # Remove the first element in main.scale list
        main.scale.remove( main.scale[ 0 ] )

        main.intentFunction.report( main )

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
                                                         port='6633' )
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
        main.step( "Discover all hosts using pingall " )
        stepResult = main.intentFunction.getHostsData( main )
        utilities.assert_equals( expect=main.TRUE,
                                actual=stepResult,
                                onpass="Successfully discovered hosts",
                                onfail="Failed to discover hosts" )

    def CASE16( self, main ):
        """
            Balance Masters
        """
        main.case( "Balance mastership of switches" )
        main.step( "Balancing mastership of switches" )

        balanceResult = main.FALSE
        balanceResult = utilities.retry( f=main.CLIs[ 0 ].balanceMasters, retValue=main.FALSE, args=[] )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=balanceResult,
                                 onpass="Successfully balanced mastership of switches",
                                 onfail="Failed to balance mastership of switches" )

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

        intentLeadersOld = main.CLIs[ 0 ].leaderCandidates()

        main.testName = "Host Intents"
        main.case( main.testName + " Test - " + str( main.numCtrls ) +
                   " NODE(S) - OF " + main.OFProtocol )
        main.caseExplanation = "This test case tests Host intents using " +\
                                str( main.numCtrls ) + " node(s) cluster;\n" +\
                                "Different type of hosts will be tested in " +\
                                "each step such as IPV6, Dual stack, VLAN " +\
                                "etc;\nThe test will use OF " + main.OFProtocol\
                                + " OVS running in Mininet"

        main.step( "IPV6: Add host intents between h1 and h9" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.hostIntent( main,
                                              name='IPV6',
                                              host1='h1',
                                              host2='h9',
                                              host1Id='00:00:00:00:00:01/-1',
                                              host2Id='00:00:00:00:00:09/-1',
                                              sw1='s5',
                                              sw2='s2',
                                              expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="IPV6: Host intent test successful " +
                                        "between two IPV6 hosts",
                                 onfail="IPV6: Host intent test failed " +
                                        "between two IPV6 hosts")

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
                                        "dual stack host using IPV6",
                                 onfail="DUALSTACK: Host intent test " +
                                        "failed between two" +
                                        "dual stack host using IPV6" )

        main.step( "1HOP: Add host intents between h1 and h3" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.hostIntent( main,
                                              name='1HOP',
                                              host1='h1',
                                              host2='h9',
                                              host1Id='00:00:00:00:00:01/-1',
                                              host2Id='00:00:00:00:00:09/-1')

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="1HOP: Host intent test " +
                                        "successful between two " +
                                        "host using IPV6 in the same switch",
                                 onfail="1HOP: Host intent test " +
                                        "failed between two" +
                                        "host using IPV6 in the same switch" )

        main.step( "VLAN: Add vlan host intents between h5 and h24" )
        stepResult = main.TRUE
        stepResult = main.intentFunction.hostIntent( main,
                                              name='VLAN1',
                                              host1='h5',
                                              host2='h24',
                                              host1Id='00:00:00:00:00:05/100',
                                              host2Id='00:00:00:00:00:18/100',
                                              sw1='s5',
                                              sw2='s2',
                                              expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="VLAN: Host intent test " +
                                        "successful between two " +
                                        "host using IPV6 in the same VLAN",
                                 onfail="VLAN1: Host intent test " +
                                        "failed between two" +
                                        "host using IPV6 in the same VLAN" )

        main.intentFunction.report( main )

    def CASE2000( self, main ):
        """
            add point intents between 2 hosts:
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

        main.testName = "Point Intents"
        main.case( main.testName + " Test - " + str( main.numCtrls ) +
                   " NODE(S) - OF " + main.OFProtocol )
        main.caseExplanation = "This test case will test point to point" +\
                               " intents using " + str( main.numCtrls ) +\
                               " node(s) cluster;\n" +\
                               "Different type of hosts will be tested in " +\
                               "each step such as IPV6, Dual stack, VLAN etc" +\
                               ";\nThe test will use OF " + main.OFProtocol +\
                               " OVS running in Mininet"
        # No option point intents
        main.step( "NOOPTION: Add point intents between h1 and h9, ipv6 hosts" )
        main.assertReturnString = "Assertion Result for NOOPTION point intent\n"
        stepResult = main.TRUE
        stepResult = main.intentFunction.pointIntent(
                                       main,
                                       name="NOOPTION",
                                       host1="h1",
                                       host2="h9",
                                       deviceId1="of:0000000000000005/1",
                                       deviceId2="of:0000000000000006/1")

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )
        stepResult = main.TRUE
        main.step( "IPV6: Add point intents between h1 and h9" )
        main.assertReturnString = "Assertion Result for IPV6 point intent\n"
        stepResult = main.intentFunction.pointIntent(
                                       main,
                                       name="IPV6",
                                       host1="h1",
                                       host2="h9",
                                       deviceId1="of:0000000000000005/1",
                                       deviceId2="of:0000000000000006/1",
                                       port1="",
                                       port2="",
                                       ethType="IPV6",
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
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )
        main.step( "IPV6_2: Add point intents between h1 and h9" )
        main.assertReturnString = "Assertion Result for IPV6 no mac address point intents\n"
        stepResult = main.intentFunction.pointIntent(
                                       main,
                                       name="IPV6_2",
                                       host1="h1",
                                       host2="h9",
                                       deviceId1="of:0000000000000005/1",
                                       deviceId2="of:0000000000000006/1",
                                       ipProto="",
                                       ip1="",
                                       ip2="",
                                       tcp1="",
                                       tcp2="",
                                       expectedLink="")
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )
        main.step( "SDNIP-ICMP: Add point intents between h1 and h9" )
        main.assertReturnString = "Assertion Result for SDNIP-ICMP IPV6 using ICMP point intents\n"
        mac1 = main.hostsData[ 'h1' ][ 'mac' ]
        mac2 = main.hostsData[ 'h9' ][ 'mac' ]
        main.log.debug(mac2)
        ipProto = main.params[ 'SDNIP' ][ 'icmpProto' ]
        ip1 = str( main.hostsData[ 'h1' ][ 'ipAddresses' ][ 0 ] ) + "/128"
        ip2 = str( main.hostsData[ 'h9' ][ 'ipAddresses' ][ 0 ] ) + "/128"
        stepResult = main.intentFunction.pointIntent(
                                           main,
                                           name="SDNIP-ICMP",
                                           host1="h1",
                                           host2="h9",
                                           deviceId1="of:0000000000000005/1",
                                           deviceId2="of:0000000000000006/1",
                                           mac1=mac1,
                                           mac2=mac2,
                                           ethType="IPV6",
                                           ipProto=ipProto,
                                           ip1=ip1,
                                           ip2=ip2 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )
        main.step( "SDNIP-TCP: Add point intents between h1 and h9" )
        main.assertReturnString = "Assertion Result for SDNIP-TCP IPV6 using TCP point intents\n"
        mac1 = main.hostsData[ 'h1' ][ 'mac' ]
        mac2 = main.hostsData[ 'h9' ][ 'mac' ]
        ip1 = str( main.hostsData[ 'h1' ][ 'ipAddresses' ][ 0 ] ) + "/128"
        ip2 = str( main.hostsData[ 'h9' ][ 'ipAddresses' ][ 0 ] ) + "/128"
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
                                           ethType="IPV6",
                                           ipProto=ipProto,
                                           ip1=ip1,
                                           ip2=ip2,
                                           tcp1=tcp1,
                                           tcp2=tcp2,
                                           sw1="",
                                           sw2="",
                                           expectedLink="" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )
        main.step( "DUALSTACK1: Add point intents between h3 and h11" )
        main.assertReturnString = "Assertion Result for Dualstack1 IPV6 with mac address point intents\n"
        stepResult = main.intentFunction.pointIntent(
                                       main,
                                       name="DUALSTACK1",
                                       host1="h3",
                                       host2="h11",
                                       deviceId1="of:0000000000000005/3",
                                       deviceId2="of:0000000000000006/3",
                                       port1="",
                                       port2="",
                                       ethType="IPV6",
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
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )
        main.step( "VLAN: Add point intents between h5 and h24" )
        main.assertReturnString = "Assertion Result for VLAN IPV6 with mac address point intents\n"
        stepResult = main.intentFunction.pointIntent(
                                       main,
                                       name="VLAN",
                                       host1="h5",
                                       host2="h24",
                                       deviceId1="of:0000000000000005/5",
                                       deviceId2="of:0000000000000007/8",
                                       port1="",
                                       port2="",
                                       ethType="IPV6",
                                       mac1="00:00:00:00:00:05",
                                       mac2="00:00:00:00:00:18",
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
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )
        main.step( "1HOP: Add point intents between h1 and h9" )
        main.assertReturnString = "Assertion Result for 1HOP IPV6 with no mac address point intents\n"
        stepResult = main.intentFunction.pointIntent( main,
                                              name='1HOP',
                                              host1="h1",
                                              host2="h9",
                                              deviceId1="of:0000000000000005/1",
                                              deviceId2="of:0000000000000006/1")
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )
        main.intentFunction.report( main )

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
        import time
        import json
        import re
        assert main, "There is no main"
        assert main.CLIs, "There is no main.CLIs"
        assert main.Mininet1, "Mininet handle should be named Mininet1"
        assert main.numSwitch, "Placed the total number of switch topology in \
                        main.numSwitch"
        main.testName = "Single to Multi Point Intents"
        main.case( main.testName + " Test - " + str( main.numCtrls ) + " NODE(S) - OF " + main.OFProtocol )
        main.caseExplanation = "This test case will test single point to" +\
                               " multi point intents using " +\
                               str( main.numCtrls ) + " node(s) cluster;\n" +\
                               "Different type of hosts will be tested in " +\
                               "each step such as IPV6, Dual stack, VLAN etc" +\
                               ";\nThe test will use OF " + main.OFProtocol +\
                               " OVS running in Mininet "
        main.step( "NOOPTION: Add single point to multi point intents" )
        hostNames = [ 'h1', 'h9', 'h17' ]
        devices = [ 'of:0000000000000005/1','of:0000000000000006/1', 'of:0000000000000007/1' ]
        main.assertReturnString = "Assertion results for IPV6 single to multi point intent with no options set\n"
        stepResult = main.TRUE
        stepResult = main.intentFunction.singleToMultiIntent(
                                         main,
                                         name="NOOPTION",
                                         hostNames=hostNames,
                                         devices=devices,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18)
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )
        main.step( "IPV6: Add single point to multi point intents" )
        main.assertReturnString = "Assertion results for IPV6 single to multi point intent with IPV6 type and MAC addresses\n"
        hostNames = [ 'h1', 'h9', 'h17' ]
        devices = [ 'of:0000000000000005/1', 'of:0000000000000006/1', 'of:0000000000000007/1' ]
        macs = [ '00:00:00:00:00:01','00:00:00:00:00:09' ,'00:00:00:00:00:11' ]
        stepResult = main.TRUE
        stepResult = main.intentFunction.singleToMultiIntent(
                                         main,
                                         name="IPV6",
                                         hostNames=hostNames,
                                         devices=devices,
                                         macs=macs,
                                         ethType="IPV6",
                                         sw1="",
                                         sw2="")
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )
        main.step( "IPV6_2: Add single point to multi point intents" )
        main.assertReturnString = "Assertion results for IPV6 single to multi point intent with IPV6 type and no MAC addresses\n"
        hostNames = [ 'h1', 'h9', 'h17' ]
        devices = [ 'of:0000000000000005/1', 'of:0000000000000006/1', 'of:0000000000000007/1' ]
        stepResult = main.TRUE
        stepResult = main.intentFunction.singleToMultiIntent(
                                         main,
                                         name="IPV6_2",
                                         hostNames=hostNames,
                                         devices=devices,
                                         ethType="IPV6",
                                         sw1="",
                                         sw2="")
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )
        main.step( "VLAN: Add single point to multi point intents" )
        main.assertReturnString = "Assertion results for IPV6 single to multi point intent with IPV6 type and MAC addresses in the same VLAN\n"
        hostNames = [ 'h5', 'h24' ]
        devices = [ 'of:0000000000000005/5', 'of:0000000000000007/8' ]
        macs = [ '00:00:00:00:00:05','00:00:00:00:00:18' ]
        stepResult = main.TRUE
        stepResult = main.intentFunction.singleToMultiIntent(
                                         main,
                                         name="IPV6",
                                         hostNames=hostNames,
                                         devices=devices,
                                         macs=macs,
                                         ethType="IPV6",
                                         sw1="",
                                         sw2="")
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )
        main.intentFunction.report( main )
      
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

        main.testName = "Multi To Single Point Intents"
        main.case( main.testName + " Test - " + str( main.numCtrls ) +
                   " NODE(S) - OF " + main.OFProtocol )
        main.caseExplanation = "This test case will test single point to" +\
                               " multi point intents using " +\
                               str( main.numCtrls ) + " node(s) cluster;\n" +\
                               "Different type of hosts will be tested in " +\
                               "each step such as IPV6, Dual stack, VLAN etc" +\
                               ";\nThe test will use OF " + main.OFProtocol +\
                               " OVS running in Mininet"

        main.step( "NOOPTION: Add multi point to single point intents" )
        main.assertReturnString = "Assertion results for NOOPTION multi to single point intent\n"
        stepResult = main.TRUE
        hostNames = [ 'h17', 'h9' ]
        devices = ['of:0000000000000007/1', 'of:0000000000000006/1' ]
        stepResult = main.intentFunction.multiToSingleIntent(
                                         main,
                                         name="NOOPTION",
                                         hostNames=hostNames,
                                         devices=devices,
                                         sw1="s6",
                                         sw2="s2",
                                         expectedLink=18 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )
        main.step( "IPV6: Add multi point to single point intents" )
        main.assertReturnString = "Assertion results for IPV6 multi to single point intent with IPV6 type and MAC addresses\n"
        hostNames = [ 'h1', 'h9', 'h17' ]
        devices = [ 'of:0000000000000005/1', 'of:0000000000000006/1', 'of:0000000000000007/1' ]
        macs = [ '00:00:00:00:00:01','00:00:00:00:00:09' ,'00:00:00:00:00:11' ]
        stepResult = main.TRUE
        installResult = main.intentFunction.multiToSingleIntent(
                                         main,
                                         name="IPV6",
                                         hostNames=hostNames,
                                         devices=devices,
                                         macs=macs,
                                         ethType="IPV6",
                                         sw1="",
                                         sw2="",
                                         expectedLink="" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )
        main.step( "IPV6_2: Add multi point to single point intents" )
        main.assertReturnString = "Assertion results for IPV6 multi to single point intent with IPV6 type and no MAC addresses\n"
        hostNames = [ 'h1', 'h9' ]
        devices = [ 'of:0000000000000005/1', 'of:0000000000000006/1' ]
        stepResult = main.TRUE
        stepResult = main.intentFunction.multiToSingleIntent(
                                         main,
                                         name="IPV6_2",
                                         hostNames=hostNames,
                                         devices=devices,
                                         ethType="IPV6",
                                         sw1="",
                                         sw2="",
                                         expectedLink="")
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "VLAN: Add multi point to single point intents" )
        main.assertReturnString = "Assertion results for IPV6 multi to single point intent with IPV6 type and no MAC addresses in the same VLAN\n"
        hostNames = [ 'h5', 'h24' ]
        devices = [ 'of:0000000000000005/5', 'of:0000000000000007/8' ]
        macs = [ '00:00:00:00:00:05','00:00:00:00:00:18' ]
        stepResult = main.TRUE
        stepResult = main.intentFunction.multiToSingleIntent(
                                         main,
                                         name="VLAN",
                                         hostNames=hostNames,
                                         devices=devices,
                                         macs=macs,
                                         ethType="IPV6",
                                         sw1="",
                                         sw2="",
                                         expectedLink="")
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )
        main.intentFunction.report( main )

    def CASE5000( self, main ):
        """
        Tests Host Mobility
        Modifies the topology location of h1
        """
        assert main, "There is no main"
        assert main.CLIs, "There is no main.CLIs"
        assert main.Mininet1, "Mininet handle should be named Mininet1"
        assert main.numSwitch, "Placed the total number of switch topology in \
                                main.numSwitch"
        main.case( "Test host mobility with host intents " )
        main.step( "Testing host mobility by moving h1 from s5 to s6" )
        h1PreMove = main.hostsData[ "h1" ][ "location" ][ 0:19 ]

        main.log.info( "Moving h1 from s5 to s6")
        main.Mininet1.moveHostv6( "h1","s5","s6" )
        main.intentFunction.getHostsData( main )
        h1PostMove = main.hostsData[ "h1" ][ "location" ][ 0:19 ]

        utilities.assert_equals( expect="of:0000000000000006",
                                 actual=h1PostMove,
                                 onpass="Mobility: Successfully moved h1 to s6",
                                 onfail="Mobility: Failed to move h1 to s6" +
                                        " to single point intents" +
                                        " with IPV6 type and MAC addresses" +
                                        " in the same VLAN" )
        main.step( "IPV6: Add host intents between h1 and h9" )
        main.assertReturnString = "Assert result for IPV6 host intent between h1, moved, and h9\n"
        stepResult = main.TRUE
        stepResult = main.intentFunction.hostIntent( main,
                                              name='IPV6 Mobility IPV6',
                                              host1='h1',
                                              host2='h9',
                                              host1Id='00:00:00:00:00:01/-1',
                                              host2Id='00:00:00:00:00:09/-1')

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )
        main.intentFunction.report( main )

    def CASE6000( self, main ):
        """
        Tests Multi to Single Point Intent and Single to Multi Point Intent End Point Failure
        """
        assert main, "There is no main"
        assert main.CLIs, "There is no main.CLIs"
        assert main.Mininet1, "Mininet handle should be named Mininet1"
        assert main.numSwitch, "Placed the total number of switch topology in \
                                main.numSwitch"
        main.case( "Test Multi to Single End Point Failure" )
        main.step( "NOOPTION: test end point failure for multi point to single point intents" )
        main.assertReturnString = "Assertion results for IPV6 multi to single \
                                  point intent end point failure with no options set\n"
        hostNames = [ 'h8', 'h17' ]
        devices = [ 'of:0000000000000005/8', 'of:0000000000000007/1' ]
        testResult = main.TRUE
        testResult = main.intentFunction.testEndPointFail(
                                         main,
                                         name="NOOPTION",
                                         test="MultipletoSingle",
                                         hostNames=hostNames,
                                         devices=devices,
                                         sw1="s6",
                                         sw2="s2",
                                         sw3="s4",
                                         sw4="s1",
                                         sw5="s3",
                                         expectedLink1=16,
                                         expectedLink2=14 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "IPV6: test end point failure for multi point to single point intents" )
        main.assertReturnString = "Assertion results for IPV6 multi to single \
                                  point intent end point failure with IPV6 type and MAC addresses\n"
        hostNames = [ 'h8', 'h9', 'h17' ]
        devices = [ 'of:0000000000000005/8', 'of:0000000000000006/1', 'of:0000000000000007/1' ]
        macs = [ '00:00:00:00:00:08','00:00:00:00:00:09' ,'00:00:00:00:00:11' ]        
        testResult = main.TRUE
        testResult = main.intentFunction.testEndPointFail(
                                         main,
                                         test="MultipletoSingle",
                                         name="IPV6",
                                         hostNames=hostNames,
                                         devices=devices,
                                         macs=macs,
                                         ethType="IPV6",
                                         sw1="s6",
                                         sw2="s2",
                                         sw3="s4",
                                         sw4="s1",
                                         sw5="s3",
                                         expectedLink1=16,
                                         expectedLink2=14 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "IPV6_2: test end point faliure for multi point to single point intents" )
        main.assertReturnString = "Assertion results for IPV6 multi to single \
                                  point intent end point failure with IPV6 type and no MAC addresses\n"
        hostNames = [ 'h8', 'h17' ]
        devices = [ 'of:0000000000000005/8', 'of:0000000000000007/1' ]
        testResult = main.TRUE
        testResult = main.intentFunction.testEndPointFail(
                                         main,
                                         test="MultipletoSingle",
                                         name="IPV6_2",
                                         hostNames=hostNames,
                                         devices=devices,
                                         ethType="IPV6",
                                         sw1="s6",
                                         sw2="s2",
                                         sw3="s4",
                                         sw4="s1",
                                         sw5="s3",
                                         expectedLink1=16,
                                         expectedLink2=14 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "VLAN: test end point failure for multi point to single point intents" )
        main.assertReturnString = "Assertion results for IPV6 multi to single \
                                  point intent end point failure with IPV6 type and no MAC addresses in the same VLAN\n"
        hostNames = [ 'h5', 'h24' ]
        devices = [ 'of:0000000000000005/5', 'of:0000000000000007/8' ]
        macs = [ '00:00:00:00:00:05','00:00:00:00:00:18' ]
        testResult = main.TRUE
        testResult = main.intentFunction.testEndPointFail(
                                         main,
                                         test="MultipletoSingle",
                                         name="VLAN",
                                         hostNames=hostNames,
                                         devices=devices,
                                         ethType="IPV6",
                                         sw1="s6",
                                         sw2="s2",
                                         sw3="s4",
                                         sw4="s1",
                                         sw5="s3",
                                         expectedLink1=16,
                                         expectedLink2=14 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.case( "Test Single to Multiple End Point Failure" )
        main.step( "NOOPTION: test end point failure for single point to multi point intents" )
        main.assertReturnString = "Assertion results for IPV6 single to multi \
                                  point intent end point failure with no options set\n"
        hostNames = [ 'h8', 'h17' ]
        devices = [ 'of:0000000000000005/8', 'of:0000000000000007/1' ]
        testResult = main.TRUE
        testResult = main.intentFunction.testEndPointFail(
                                         main,
                                         test="SingletoMultiple",
                                         name="NOOPTION",
                                         hostNames=hostNames,
                                         devices=devices,
                                         sw1="s6",
                                         sw2="s2",
                                         sw3="s4",
                                         sw4="s1",
                                         sw5="s3",
                                         expectedLink1=16,
                                         expectedLink2=14 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )
        main.step( "IPV6: test end point failure for single point to multi point intents" )
        main.assertReturnString = "Assertion results for IPV6 single to multi \
                                  point intent end point failure with IPV6 type and MAC addresses\n"
        hostNames = [ 'h8', 'h9', 'h17' ]
        devices = [ 'of:0000000000000005/8', 'of:0000000000000006/1', 'of:0000000000000007/1' ]
        macs = [ '00:00:00:00:00:08','00:00:00:00:00:09' ,'00:00:00:00:00:11' ]  
        testResult = main.TRUE
        testResult = main.intentFunction.testEndPointFail(
                                         main,
                                         test="SingletoMultiple",
                                         name="IPV6",
                                         hostNames=hostNames,
                                         devices=devices,
                                         ethType="IPV6",
                                         macs=macs,
                                         sw1="s6",
                                         sw2="s2",
                                         sw3="s4",
                                         sw4="s1",
                                         sw5="s3",
                                         expectedLink1=16,
                                         expectedLink2=14 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "IPV6_2: test end point failure for single point to multi point intents" )
        main.assertReturnString = "Assertion results for IPV6 single to multi\
                                  point intent endpoint failure with IPV6 type and no MAC addresses\n"
        hostNames = [ 'h8', 'h17' ]
        devices = [ 'of:0000000000000005/8', 'of:0000000000000007/1' ]
        testResult = main.TRUE
        testResult = main.intentFunction.testEndPointFail(
                                         main,
                                         test="SingletoMultiple",
                                         name="IPV6_2",
                                         hostNames=hostNames,
                                         devices=devices,
                                         ethType="IPV6",
                                         sw1="s6",
                                         sw2="s2",
                                         sw3="s4",
                                         sw4="s1",
                                         sw5="s3",
                                         expectedLink1=16,
                                         expectedLink2=14 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "VLAN: test end point failure for single point to multi point intents" )
        main.assertReturnString = "Assertion results for IPV6 single to multi point\
                                  intent endpoint failure with IPV6 type and MAC addresses in the same VLAN\n"
        hostNames = [ 'h5', 'h24' ]
        devices = [ 'of:0000000000000005/5', 'of:0000000000000007/8' ]
        macs = [ '00:00:00:00:00:05','00:00:00:00:00:18' ]
        testResult = main.TRUE
        testResult = main.intentFunction.testEndPointFail(
                                         main,
                                         test="SingletoMultiple",
                                         name="IPV6",
                                         hostNames=hostNames,
                                         devices=devices,
                                         macs=macs,
                                         ethType="IPV6",
                                         sw1="s6",
                                         sw2="s2",
                                         sw3="s4",
                                         sw4="s1",
                                         sw5="s3",
                                         expectedLink1=16,
                                         expectedLink2=14 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.intentFunction.report( main )
