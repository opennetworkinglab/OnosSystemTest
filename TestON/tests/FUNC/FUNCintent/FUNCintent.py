"""
Copyright 2015 Open Networking Foundation ( ONF )

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    ( at your option ) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.
"""
# Testing the basic intent functionality of ONOS


class FUNCintent:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
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
        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
            main.testSetUp = ONOSSetup()
        except ImportError:
            main.log.error( "ONOSSetup not found. exiting the test" )
            main.cleanAndExit()
        main.testSetUp.envSetupDescription()
        stepResult = main.FALSE

        from tests.dependencies.Network import Network
        main.Network = Network()

        # Test variables
        try:
            main.apps = main.params[ 'ENV' ][ 'cellApps' ]
            main.dependencyPath = main.testOnDirectory + \
                                  main.params[ 'DEPENDENCY' ][ 'path' ]
            main.topology = main.params[ 'DEPENDENCY' ][ 'topology' ]
            main.scale = ( main.params[ 'SCALE' ][ 'size' ] ).split( "," )

            wrapperFile1 = main.params[ 'DEPENDENCY' ][ 'wrapper1' ]
            wrapperFile2 = main.params[ 'DEPENDENCY' ][ 'wrapper2' ]
            wrapperFile3 = main.params[ 'DEPENDENCY' ][ 'wrapper3' ]
            main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
            main.checkIntentSleep = int( main.params[ 'SLEEP' ][ 'checkintent' ] )
            main.removeIntentSleep = int( main.params[ 'SLEEP' ][ 'removeintent' ] )
            main.rerouteSleep = int( main.params[ 'SLEEP' ][ 'reroute' ] )
            main.fwdSleep = int( main.params[ 'SLEEP' ][ 'fwd' ] )
            main.checkConnectionSleep = int( main.params[ 'SLEEP' ][ 'checkConnection' ] )
            main.checkFlowCountSleep = int( main.params[ 'SLEEP' ][ 'checkFlowCount' ] )
            main.checkIntentHostSleep = int( main.params[ 'SLEEP' ][ 'checkIntentHost' ] )
            main.checkIntentPointSleep = int( main.params[ 'SLEEP' ][ 'checkIntentPoint' ] )
            main.checkTopoAttempts = int( main.params[ 'SLEEP' ][ 'topoAttempts' ] )
            main.flowDurationSleep = int( main.params[ 'SLEEP' ][ 'flowDuration' ] )
            main.generalAttemptsNum = int( main.params[ 'RETRY' ][ 'generalAttempts' ] )
            main.middleAttemptsNum = int( main.params[ 'RETRY' ][ 'middleAttempts' ] )
            main.minimumAttemptsNum = int( main.params[ 'RETRY' ][ 'minimumAttempts' ] )
            main.checkConnectionAttNum = int( main.params[ 'RETRY' ][ 'checkConnectionAtt' ] )
            main.removeIntentAttNum = int( main.params[ 'RETRY' ][ 'removeIntentAtt' ] )
            main.numSwitch = int( main.params[ 'MININET' ][ 'switch' ] )
            main.numLinks = int( main.params[ 'MININET' ][ 'links' ] )
            main.hostsData = {}
            main.scapyHostNames = main.params[ 'SCAPY' ][ 'HOSTNAMES' ].split( ',' )
            main.scapyHosts = []  # List of scapy hosts for iterating
            main.assertReturnString = ''  # Assembled assert return string
            main.cycle = 0  # How many times FUNCintent has run through its tests
            main.usePortstate = True if main.params[ 'TEST' ][ 'usePortstate' ] == "True" else False

            # -- INIT SECTION, ONLY RUNS ONCE -- #

            main.intents = imp.load_source( wrapperFile2,
                                            main.dependencyPath +
                                            wrapperFile2 +
                                            ".py" )

            if hasattr( main, "Mininet1" ):
                copyResult1 = main.ONOSbench.scp( main.Mininet1,
                                                  main.dependencyPath +
                                                  main.topology,
                                                  main.Mininet1.home + "custom/",
                                                  direction="to" )

            stepResult = main.testSetUp.envSetup()
        except Exception as e:
            main.testSetUp.envSetupException( e )
        main.testSetUp.evnSetupConclusion( stepResult )

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
        main.flowCompiler = "Flow Rules"
        main.initialized = main.testSetUp.ONOSSetUp( main.Cluster, True )
        main.intents.report( main )

    def CASE8( self, main ):
        """
        Compare ONOS Topology to Mininet Topology
        """
        import time
        try:
            from tests.dependencies.topology import Topology
        except ImportError:
            main.log.error( "Topology not found exiting the test" )
            main.cleanAndExit()
        try:
            main.topoRelated
        except ( NameError, AttributeError ):
            main.topoRelated = Topology()
        main.topoRelated.compareTopos( main.Mininet1, main.checkTopoAttempts )

    def CASE10( self, main ):
        """
            Start Mininet topology with OF 1.0 switches
        """
        if main.initialized == main.FALSE:
            main.log.error( "Test components did not start correctly, skipping further tests" )
            main.skipCase()
        main.OFProtocol = "1.0"
        main.log.report( "Start Mininet topology with OF 1.0 switches" )
        main.case( "Start Mininet topology with OF 1.0 switches" )
        main.caseExplanation = "Start mininet topology with OF 1.0 " +\
                                "switches to test intents, exits out if " +\
                                "topology did not start correctly"

        main.step( "Starting Mininet topology with OF 1.0 switches" )
        args = "--switch ovs,protocols=OpenFlow10"
        topoResult = main.Mininet1.startNet( topoFile=main.Mininet1.home + "/custom/" + main.topology,
                                             args=args )
        stepResult = topoResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )

        # Set flag to test cases if topology did not load properly
        if not topoResult:
            main.initialized = main.FALSE
            main.skipCase()

    def CASE11( self, main ):
        """
            Start Mininet topology with OF 1.3 switches
        """
        if main.initialized == main.FALSE:
            main.log.error( "Test components did not start correctly, skipping further tests" )
            main.skipCase()
        main.OFProtocol = "1.3"
        main.log.report( "Start Mininet topology with OF 1.3 switches" )
        main.case( "Start Mininet topology with OF 1.3 switches" )
        main.caseExplanation = "Start mininet topology with OF 1.3 " +\
                                "switches to test intents, exits out if " +\
                                "topology did not start correctly"

        main.step( "Starting Mininet topology with OF 1.3 switches" )
        args = "--switch ovs,protocols=OpenFlow13"
        topoResult = main.Mininet1.startNet( topoFile=main.Mininet1.home + "/custom/" + main.topology,
                                             args=args )
        stepResult = topoResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )
        # Set flag to skip test cases if topology did not load properly
        if not topoResult:
            main.initialized = main.FALSE

    def CASE12( self, main ):
        """
            Assign mastership to controllers
        """
        import re

        if main.initialized == main.FALSE:
            main.log.error( "Test components did not start correctly, skipping further tests" )
            main.skipCase()
        main.case( "Assign switches to controllers" )
        main.step( "Assigning switches to controllers" )
        main.caseExplanation = "Assign OF " + main.OFProtocol +\
                                " switches to ONOS nodes"

        switchList = []

        # Creates a list switch name, use getSwitch() function later...
        for i in range( 1, ( main.numSwitch + 1 ) ):
            switchList.append( 's' + str( i ) )

        tempONOSip = main.Cluster.getIps()

        assignResult = main.Network.assignSwController( sw=switchList,
                                                         ip=tempONOSip,
                                                         port="6653" )
        if not assignResult:
            main.log.error( "Problem assigning mastership of switches" )
            main.initialized = main.FALSE
            main.skipCase()

        for i in range( 1, ( main.numSwitch + 1 ) ):
            response = main.Network.getSwController( "s" + str( i ) )
            main.log.debug( "Response is " + str( response ) )
            if re.search( "tcp:" + main.Cluster.active( 0 ).ipAddress, response ):
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
        if not stepResult:
            main.initialized = main.FALSE

    def CASE13( self, main ):
        """
            Create Scapy components
        """
        if main.initialized == main.FALSE:
            main.log.error( "Test components did not start correctly, skipping further tests" )
            main.skipCase()
        main.case( "Create scapy components" )
        main.step( "Create scapy components" )
        scapyResult = main.TRUE
        for hostName in main.scapyHostNames:
            main.Scapy1.createHostComponent( hostName )
            main.scapyHosts.append( getattr( main, hostName ) )

        main.step( "Start scapy components" )
        for host in main.scapyHosts:
            host.startHostCli()
            host.startScapy()
            host.updateSelf()
            main.log.debug( host.name )
            main.log.debug( host.hostIp )
            main.log.debug( host.hostMac )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=scapyResult,
                                 onpass="Successfully created Scapy Components",
                                 onfail="Failed to discover Scapy Components" )
        if not scapyResult:
            main.initialized = main.FALSE

    def CASE14( self, main ):
        """
            Discover all hosts with fwd and pingall and store its data in a dictionary
        """
        if main.initialized == main.FALSE:
            main.log.error( "Test components did not start correctly, skipping further tests" )
            main.skipCase()
        main.case( "Discover all hosts" )
        main.step( "Pingall hosts and confirm ONOS discovery" )
        utilities.retry( f=main.intents.fwdPingall, retValue=main.FALSE, args=[ main ] )

        stepResult = utilities.retry( f=main.intents.confirmHostDiscovery, retValue=main.FALSE,
                                      args=[ main ], attempts=main.checkTopoAttempts, sleep=2 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully discovered hosts",
                                 onfail="Failed to discover hosts" )
        if not stepResult:
            main.initialized = main.FALSE
            main.skipCase()

        main.step( "Populate hostsData" )
        stepResult = main.intents.populateHostData( main )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully populated hostsData",
                                 onfail="Failed to populate hostsData" )
        if not stepResult:
            main.initialized = main.FALSE

    def CASE15( self, main ):
        """
            Discover all hosts with scapy arp packets and store its data to a dictionary
        """
        if main.initialized == main.FALSE:
            main.log.error( "Test components did not start correctly, skipping further tests" )
            main.skipCase()
        main.case( "Discover all hosts using scapy" )
        main.step( "Send packets from each host to the first host and confirm onos discovery" )

        if len( main.scapyHosts ) < 1:
            main.log.error( "No scapy hosts have been created" )
            main.initialized = main.FALSE
            main.skipCase()

        # Send ARP packets from each scapy host component
        main.intents.sendDiscoveryArp( main, main.scapyHosts )

        stepResult = utilities.retry( f=main.intents.confirmHostDiscovery,
                                      retValue=main.FALSE, args=[ main ],
                                      attempts=main.checkTopoAttempts, sleep=2 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ONOS correctly discovered all hosts",
                                 onfail="ONOS incorrectly discovered hosts" )
        if not stepResult:
            main.initialized = main.FALSE
            main.skipCase()

        main.step( "Populate hostsData" )
        stepResult = main.intents.populateHostData( main )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully populated hostsData",
                                 onfail="Failed to populate hostsData" )
        if not stepResult:
            main.initialized = main.FALSE

    def CASE16( self, main ):
        """
            Balance Masters
        """
        if main.initialized == main.FALSE:
            main.log.error( "Test components did not start correctly, skipping further tests" )
            main.skipCase()
        main.case( "Balance mastership of switches" )
        main.step( "Balancing mastership of switches" )

        balanceResult = utilities.retry( f=main.Cluster.active( 0 ).CLI.balanceMasters, retValue=main.FALSE, args=[] )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=balanceResult,
                                 onpass="Successfully balanced mastership of switches",
                                 onfail="Failed to balance mastership of switches" )
        if not balanceResult:
            main.initialized = main.FALSE

    def CASE17( self, main ):
        """
            Use Flow Objectives
        """
        if main.initialized == main.FALSE:
            main.log.error( "Test components did not start correctly, skipping further tests" )
            main.skipCase()
        main.case( "Enable intent compilation using Flow Objectives" )
        main.step( "Enabling Flow Objectives" )

        main.flowCompiler = "Flow Objectives"

        cmd = "org.onosproject.net.intent.impl.compiler.IntentConfigurableRegistrator"

        stepResult = main.Cluster.active( 0 ).CLI.setCfg( component=cmd,
                                                          propName="useFlowObjectives", value="true" )
        stepResult &= main.Cluster.active( 0 ).CLI.setCfg( component=cmd,
                                                           propName="defaultFlowObjectiveCompiler",
                                                           value='org.onosproject.net.intent.impl.compiler.LinkCollectionIntentObjectiveCompiler' )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully activated Flow Objectives",
                                 onfail="Failed to activate Flow Objectives" )
        if not balanceResult:
            main.initialized = main.FALSE

    def CASE18( self, main ):
        """
            Stop mininet and remove scapy host
        """
        try:
            from tests.dependencies.utils import Utils
        except ImportError:
            main.log.error( "Utils not found exiting the test" )
            main.cleanAndExit()
        try:
            main.Utils
        except ( NameError, AttributeError ):
            main.Utils = Utils()
        main.log.report( "Stop Mininet and Scapy" )
        main.case( "Stop Mininet and Scapy" )
        main.caseExplanation = "Stopping the current mininet topology " +\
                                "to start up fresh"
        main.step( "Stopping and Removing Scapy Host Components" )
        scapyResult = main.TRUE
        for host in main.scapyHosts:
            scapyResult = scapyResult and host.stopScapy()
            main.log.info( "Stopped Scapy Host: {0}".format( host.name ) )

        for host in main.scapyHosts:
            scapyResult = scapyResult and main.Scapy1.removeHostComponent( host.name )
            main.log.info( "Removed Scapy Host Component: {0}".format( host.name ) )

        main.scapyHosts = []
        main.scapyHostIPs = []

        utilities.assert_equals( expect=main.TRUE,
                                 actual=scapyResult,
                                 onpass="Successfully stopped scapy and removed host components",
                                 onfail="Failed to stop mininet and scapy" )

        mininetResult = main.Utils.mininetCleanup( main.Mininet1 )
        # Exit if topology did not load properly
        if not ( mininetResult and scapyResult ):
            main.cleanAndExit()

    def CASE19( self, main ):
        """
            Copy the karaf.log files after each testcase cycle
        """
        try:
            from tests.dependencies.utils import Utils
        except ImportError:
            main.log.error( "Utils not found exiting the test" )
            main.cleanAndExit()
        try:
            main.Utils
        except ( NameError, AttributeError ):
            main.Utils = Utils()
        main.Utils.copyKarafLog( "cycle" + str( main.cycle ) )

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
        if main.initialized == main.FALSE:
            main.log.error( "Test components did not start correctly, skipping further tests" )
            main.skipCase()
        # Assert variables - These variable's name|format must be followed
        # if you want to use the wrapper function
        assert main, "There is no main"
        try:
            assert main.numSwitch
        except AssertionError:
            main.log.error( "Place the total number of switch topology in " +
                             main.numSwitch )
            main.initialized = main.FALSE
            main.skipCase()

        # Save leader candidates
        intentLeadersOld = main.Cluster.active( 0 ).CLI.leaderCandidates()

        main.testName = "Host Intents"
        main.case( main.testName + " Test - " + str( main.Cluster.numCtrls ) +
                   " NODE(S) - OF " + main.OFProtocol + " - Using " + main.flowCompiler )
        main.caseExplanation = "This test case tests Host intents using " +\
                                str( main.Cluster.numCtrls ) + " node(s) cluster;\n" +\
                                "Different type of hosts will be tested in " +\
                                "each step such as IPV4, Dual stack, VLAN " +\
                                "etc;\nThe test will use OF " + main.OFProtocol +\
                                " OVS running in Mininet and compile intents" +\
                                " using " + main.flowCompiler

        main.step( "IPV4: Add host intents between h1 and h9" )
        main.assertReturnString = "Assertion Result for IPV4 host intent with mac addresses\n"
        host1 = { "name": "h1", "id": "00:00:00:00:00:01/-1" }
        host2 = { "name": "h9", "id": "00:00:00:00:00:09/-1" }
        testResult = main.FALSE
        installResult = main.intents.installHostIntent( main,
                                                        name="IPV4",
                                                        onosNode=0,
                                                        host1=host1,
                                                        host2=host2 )
        if installResult:
            testResult = main.intents.testHostIntent( main,
                                                      name="IPV4",
                                                      intentId=installResult,
                                                      onosNode=0,
                                                      host1=host1,
                                                      host2=host2,
                                                      sw1="s5",
                                                      sw2="s2",
                                                      expectedLink=18 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "DUALSTACK1: Add host intents between h3 and h11" )
        main.assertReturnString = "Assertion Result for dualstack IPV4 with MAC addresses\n"
        host1 = { "name": "h3", "id": "00:00:00:00:00:03/-1" }
        host2 = { "name": "h11", "id": "00:00:00:00:00:0B/-1 " }
        testResult = main.FALSE
        installResult = main.intents.installHostIntent( main,
                                                        name="DUALSTACK",
                                                        onosNode=0,
                                                        host1=host1,
                                                        host2=host2 )

        if installResult:
            testResult = main.intents.testHostIntent( main,
                                                      name="DUALSTACK",
                                                      intentId=installResult,
                                                      onosNode=0,
                                                      host1=host1,
                                                      host2=host2,
                                                      sw1="s5",
                                                      sw2="s2",
                                                      expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "DUALSTACK2: Add host intents between h1 and h11" )
        main.assertReturnString = "Assertion Result for dualstack2 host intent\n"
        host1 = { "name": "h1" }
        host2 = { "name": "h11" }
        testResult = main.FALSE
        installResult = main.intents.installHostIntent( main,
                                                        name="DUALSTACK2",
                                                        onosNode=0,
                                                        host1=host1,
                                                        host2=host2 )

        if installResult:
            testResult = main.intents.testHostIntent( main,
                                                      name="DUALSTACK2",
                                                      intentId=installResult,
                                                      onosNode=0,
                                                      host1=host1,
                                                      host2=host2,
                                                      sw1="s5",
                                                      sw2="s2",
                                                      expectedLink=18 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "1HOP: Add host intents between h1 and h3" )
        main.assertReturnString = "Assertion Result for 1HOP for IPV4 same switch\n"
        host1 = { "name": "h1" }
        host2 = { "name": "h3" }
        testResult = main.FALSE
        installResult = main.intents.installHostIntent( main,
                                                        name="1HOP",
                                                        onosNode=0,
                                                        host1=host1,
                                                        host2=host2 )

        if installResult:
            testResult = main.intents.testHostIntent( main,
                                                      name="1HOP",
                                                      intentId=installResult,
                                                      onosNode=0,
                                                      host1=host1,
                                                      host2=host2,
                                                      sw1="s5",
                                                      sw2="s2",
                                                      expectedLink=18 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "VLAN1: Add vlan host intents between h4 and h12" )
        main.assertReturnString = "Assertion Result vlan IPV4\n"
        host1 = { "name": "h4", "id": "00:00:00:00:00:04/100", "vlan": "100" }
        host2 = { "name": "h12", "id": "00:00:00:00:00:0C/100", "vlan": "100" }
        testResult = main.FALSE
        installResult = main.intents.installHostIntent( main,
                                                        name="VLAN1",
                                                        onosNode=0,
                                                        host1=host1,
                                                        host2=host2 )
        if installResult:
            testResult = main.intents.testHostIntent( main,
                                                      name="VLAN1",
                                                      intentId=installResult,
                                                      onosNode=0,
                                                      host1=host1,
                                                      host2=host2,
                                                      sw1="s5",
                                                      sw2="s2",
                                                      expectedLink=18 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "VLAN2: Add vlan host intents between h4 and h13" )
        main.assertReturnString = "Assertion Result vlan IPV4\n"
        host1 = { "name": "h5", "vlan": "200" }
        host2 = { "name": "h12", "vlan": "100" }
        testResult = main.FALSE
        installResult = main.intents.installHostIntent( main,
                                                        name="VLAN2",
                                                        onosNode=0,
                                                        host1=host1,
                                                        host2=host2 )

        if installResult:
            testResult = main.intents.testHostIntent( main,
                                                      name="VLAN2",
                                                      intentId=installResult,
                                                      onosNode=0,
                                                      host1=host1,
                                                      host2=host2,
                                                      sw1="s5",
                                                      sw2="s2",
                                                      expectedLink=18 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "Encapsulation: Add host intents between h1 and h9" )
        main.assertReturnString = "Assertion Result for VLAN Encapsulated host intent\n"
        host1 = { "name": "h1", "id": "00:00:00:00:00:01/-1" }
        host2 = { "name": "h9", "id": "00:00:00:00:00:09/-1" }
        testResult = main.FALSE
        installResult = main.intents.installHostIntent( main,
                                                        name="ENCAPSULATION",
                                                        onosNode=0,
                                                        host1=host1,
                                                        host2=host2,
                                                        encap="VLAN" )
        if installResult:
            testResult = main.intents.testHostIntent( main,
                                                      name="ENCAPSULATION",
                                                      intentId=installResult,
                                                      onosNode=0,
                                                      host1=host1,
                                                      host2=host2,
                                                      sw1="s5",
                                                      sw2="s2",
                                                      expectedLink=18 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        # Testing MPLS would require kernel version of 4.1 or higher ( Current version is 3.13 )
        # main.step( "Encapsulation: Add host intents between h1 and h9" )
        # main.assertReturnString = "Assertion Result for MPLS Encapsulated host intent\n"
        # host1 = { "name": "h1", "id": "00:00:00:00:00:01/-1" }
        # host2 = { "name": "h9", "id": "00:00:00:00:00:09/-1" }
        # testResult = main.FALSE
        # installResult = main.intents.installHostIntent( main,
        #                                                 name="ENCAPSULATION",
        #                                                 onosNode=0,
        #                                                 host1=host1,
        #                                                 host2=host2,
        #                                                 encap="MPLS" )
        # if installResult:
        #     testResult = main.intents.testHostIntent( main,
        #                                               name="ENCAPSULATION",
        #                                               intentId=installResult,
        #                                               onosNode=0,
        #                                               host1=host1,
        #                                               host2=host2,
        #                                               sw1="s5",
        #                                               sw2="s2",
        #                                               expectedLink=18 )
        # else:
        #     main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )
        #
        # utilities.assert_equals( expect=main.TRUE,
        #                          actual=testResult,
        #                          onpass=main.assertReturnString,
        #                          onfail=main.assertReturnString )

        main.step( "Confirm that ONOS leadership is unchanged" )
        intentLeadersNew = main.Cluster.active( 0 ).CLI.leaderCandidates()
        testResult = main.intents.checkLeaderChange( intentLeadersOld,
                                                     intentLeadersNew )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass="ONOS Leaders Unchanged",
                                 onfail="ONOS Leader Mismatch" )

        main.intents.report( main )

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
        if main.initialized == main.FALSE:
            main.log.error( "Test components did not start correctly, skipping further tests" )
            main.skipCase()
        # Assert variables - These variable's name|format must be followed
        # if you want to use the wrapper function
        assert main, "There is no main"
        try:
            assert main.numSwitch
        except AssertionError:
            main.log.error( "Place the total number of switch topology in " +
                             main.numSwitch )
            main.initialized = main.FALSE
            main.skipCase()

        main.testName = "Point Intents"
        main.case( main.testName + " Test - " + str( main.Cluster.numCtrls ) +
                   " NODE(S) - OF " + main.OFProtocol + " - Using " + main.flowCompiler )
        main.caseExplanation = "This test case will test point to point" +\
                               " intents using " + str( main.Cluster.numCtrls ) +\
                               " node(s) cluster;\n" +\
                               "Different type of hosts will be tested in " +\
                               "each step such as IPV4, Dual stack, VLAN etc" +\
                               ";\nThe test will use OF " + main.OFProtocol +\
                               " OVS running in Mininet and compile intents" +\
                               " using " + main.flowCompiler

        # No option point intents
        main.step( "NOOPTION: Add point intents between h1 and h9" )
        main.assertReturnString = "Assertion Result for NOOPTION point intent\n"
        senders = [
            { "name": "h1", "device": "of:0000000000000005/1" }
        ]
        recipients = [
            { "name": "h9", "device": "of:0000000000000006/1" }
        ]
        testResult = main.FALSE
        installResult = main.intents.installPointIntent(
                                       main,
                                       name="NOOPTION",
                                       senders=senders,
                                       recipients=recipients )

        if installResult:
            testResult = main.intents.testPointIntent(
                                         main,
                                         intentId=installResult,
                                         name="NOOPTION",
                                         senders=senders,
                                         recipients=recipients,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "IPV4: Add point intents between h1 and h9" )
        main.assertReturnString = "Assertion Result for IPV4 point intent\n"
        senders = [
            { "name": "h1", "device": "of:0000000000000005/1", "mac": "00:00:00:00:00:01" }
        ]
        recipients = [
            { "name": "h9", "device": "of:0000000000000006/1", "mac": "00:00:00:00:00:09" }
        ]
        testResult = main.FALSE
        installResult = main.intents.installPointIntent(
                                       main,
                                       name="IPV4",
                                       senders=senders,
                                       recipients=recipients,
                                       ethType="IPV4" )

        if installResult:
            testResult = main.intents.testPointIntent(
                                         main,
                                         intentId=installResult,
                                         name="IPV4",
                                         senders=senders,
                                         recipients=recipients,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "Protected: Add point intents between h1 and h9" )
        main.assertReturnString = "Assertion Result for protected point intent\n"
        senders = [
            { "name": "h1", "device": "of:0000000000000005/1", "mac": "00:00:00:00:00:01" }
        ]
        recipients = [
            { "name": "h9", "device": "of:0000000000000006/1", "mac": "00:00:00:00:00:09" }
        ]
        testResult = main.FALSE
        installResult = main.intents.installPointIntent(
            main,
            name="Protected",
            senders=senders,
            recipients=recipients,
            protected=True )

        if installResult:
            testResult = main.intents.testPointIntent(
                main,
                name="Protected",
                intentId=installResult,
                senders=senders,
                recipients=recipients,
                sw1="s5",
                sw2="s2",
                protected=True,
                expectedLink=18 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "IPV4_2: Add point intents between h1 and h9" )
        main.assertReturnString = "Assertion Result for IPV4 no mac address point intents\n"
        senders = [
            { "name": "h1", "device": "of:0000000000000005/1" }
        ]
        recipients = [
            { "name": "h9", "device": "of:0000000000000006/1" }
        ]
        testResult = main.FALSE
        installResult = main.intents.installPointIntent(
                                       main,
                                       name="IPV4_2",
                                       senders=senders,
                                       recipients=recipients,
                                       ethType="IPV4" )

        if installResult:
            testResult = main.intents.testPointIntent(
                                         main,
                                         intentId=installResult,
                                         name="IPV4_2",
                                         senders=senders,
                                         recipients=recipients,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "SDNIP-ICMP: Add point intents between h1 and h9" )
        main.assertReturnString = "Assertion Result for SDNIP-ICMP IPV4 using TCP point intents\n"
        senders = [
            { "name": "h1", "device": "of:0000000000000005/1", "mac": "00:00:00:00:00:01",
              "ip": ( main.h1.hostIp + "/24" ) }
        ]
        recipients = [
            { "name": "h9", "device": "of:0000000000000006/1", "mac": "00:00:00:00:00:09",
              "ip": ( main.h9.hostIp + "/24" ) }
        ]
        ipProto = main.params[ 'SDNIP' ][ 'ipPrototype' ]
        # Uneccessary, not including this in the selectors
        tcpSrc = main.params[ 'SDNIP' ][ 'srcPort' ]
        tcpDst = main.params[ 'SDNIP' ][ 'dstPort' ]
        testResult = main.FALSE
        installResult = main.intents.installPointIntent(
                                       main,
                                       name="SDNIP-ICMP",
                                       senders=senders,
                                       recipients=recipients,
                                       ethType="IPV4",
                                       ipProto=ipProto,
                                       tcpSrc=tcpSrc,
                                       tcpDst=tcpDst )

        if installResult:
            testResult = main.intents.testPointIntent(
                                         main,
                                         intentId=installResult,
                                         name="SDNIP_ICMP",
                                         senders=senders,
                                         recipients=recipients,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18,
                                         useTCP=True )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "SDNIP-TCP: Add point intents between h1 and h9" )
        main.assertReturnString = "Assertion Result for SDNIP-TCP IPV4 using ICMP point intents\n"
        mac1 = main.hostsData[ 'h1' ][ 'mac' ]
        mac2 = main.hostsData[ 'h9' ][ 'mac' ]
        ip1 = str( main.hostsData[ 'h1' ][ 'ipAddresses' ][ 0 ] ) + "/32"
        ip2 = str( main.hostsData[ 'h9' ][ 'ipAddresses' ][ 0 ] ) + "/32"
        ipProto = main.params[ 'SDNIP' ][ 'tcpProto' ]
        tcp1 = main.params[ 'SDNIP' ][ 'srcPort' ]
        tcp2 = main.params[ 'SDNIP' ][ 'dstPort' ]

        stepResult = main.intents.pointIntentTcp(
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
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "DUALSTACK1: Add point intents between h3 and h11" )
        main.assertReturnString = "Assertion Result for Dualstack1 IPV4 with mac address point intents\n"
        senders = [
            { "name": "h3", "device": "of:0000000000000005/3", "mac": "00:00:00:00:00:03" }
        ]
        recipients = [
            { "name": "h11", "device": "of:0000000000000006/3", "mac": "00:00:00:00:00:0B" }
        ]
        testResult = main.FALSE
        installResult = main.intents.installPointIntent(
                                       main,
                                       name="DUALSTACK1",
                                       senders=senders,
                                       recipients=recipients,
                                       ethType="IPV4" )

        if installResult:
            testResult = main.intents.testPointIntent(
                                         main,
                                         intentId=installResult,
                                         name="DUALSTACK1",
                                         senders=senders,
                                         recipients=recipients,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "VLAN: Add point intents between h5 and h21" )
        main.assertReturnString = "Assertion Result for VLAN IPV4 with mac address point intents\n"
        senders = [
            { "name": "h5", "device": "of:0000000000000005/5", "mac": "00:00:00:00:00:05", "vlan": "200" }
        ]
        recipients = [
            { "name": "h21", "device": "of:0000000000000007/5", "mac": "00:00:00:00:00:15", "vlan": "200" }
        ]
        testResult = main.FALSE
        installResult = main.intents.installPointIntent(
                                       main,
                                       name="VLAN",
                                       senders=senders,
                                       recipients=recipients )

        if installResult:
            testResult = main.intents.testPointIntent(
                                         main,
                                         intentId=installResult,
                                         name="VLAN",
                                         senders=senders,
                                         recipients=recipients,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "VLAN: Add point intents between h5 and h21" )
        main.assertReturnString = "Assertion Result for VLAN IPV4 point intents with VLAN treatment\n"
        senders = [
            { "name": "h4", "vlan": "100" }
        ]
        recipients = [
            { "name": "h21", "vlan": "200" }
        ]
        testResult = main.FALSE
        installResult = main.intents.installPointIntent(
                                       main,
                                       name="VLAN2",
                                       senders=senders,
                                       recipients=recipients,
                                       setVlan=200 )

        if installResult:
            testResult = main.intents.testPointIntent(
                                         main,
                                         intentId=installResult,
                                         name="VLAN2",
                                         senders=senders,
                                         recipients=recipients,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "1HOP: Add point intents between h1 and h3" )
        main.assertReturnString = "Assertion Result for 1HOP IPV4 with no mac address point intents\n"
        senders = [
            { "name": "h1", "device": "of:0000000000000005/1", "mac": "00:00:00:00:00:01" }
        ]
        recipients = [
            { "name": "h3", "device": "of:0000000000000005/3", "mac": "00:00:00:00:00:03" }
        ]
        testResult = main.FALSE
        installResult = main.intents.installPointIntent(
                                       main,
                                       name="1HOP IPV4",
                                       senders=senders,
                                       recipients=recipients,
                                       ethType="IPV4" )

        if installResult:
            testResult = main.intents.testPointIntent(
                                         main,
                                         intentId=installResult,
                                         name="1HOP IPV4",
                                         senders=senders,
                                         recipients=recipients,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "Add point to point intents using VLAN Encapsulation" )
        main.assertReturnString = "Assertion Result for VLAN Encapsulation Point Intent"
        senders = [
            { "name": "h1", "device": "of:0000000000000005/1" }
        ]
        recipients = [
            { "name": "h9", "device": "of:0000000000000006/1" }
        ]
        testResult = main.FALSE
        installResult = main.intents.installPointIntent(
                                       main,
                                       name="ENCAPSULATION",
                                       senders=senders,
                                       recipients=recipients,
                                       encap="VLAN" )

        if installResult:
            testResult = main.intents.testPointIntent(
                                         main,
                                         intentId=installResult,
                                         name="ENCAPSULATION",
                                         senders=senders,
                                         recipients=recipients,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "BANDWIDTH ALLOCATION: Checking bandwidth allocation for point intents between h1 and h9" )
        main.assertReturnString = "Assertion Result for BANDWIDTH ALLOCATION for point intent\n"
        senders = [
            { "name": "h1", "device": "of:0000000000000005/1" }
        ]
        recipients = [
            { "name": "h9", "device": "of:0000000000000006/1" }
        ]
        testResult = main.FALSE
        installResult = main.intents.installPointIntent(
                                      main,
                                      name="NOOPTION",
                                      senders=senders,
                                      recipients=recipients,
                                      bandwidth=100 )

        if installResult:
            testResult = main.intents.testPointIntent(
                                         main,
                                         intentId=installResult,
                                         name="NOOPTION",
                                         senders=senders,
                                         recipients=recipients,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        # Testing MPLS would require kernel version of 4.1 or higher ( Current version is 3.13 )
        # main.step( "Add point to point intents using MPLS Encapsulation" )
        # main.assertReturnString = "Assertion Result for MPLS Encapsulation Point Intent"
        # senders = [
        #     { "name": "h1", "device": "of:0000000000000005/1" }
        # ]
        # recipients = [
        #     { "name": "h9", "device": "of:0000000000000006/1" }
        # ]
        # testResult = main.FALSE
        # installResult = main.intents.installPointIntent(
        #     main,
        #     name="ENCAPSULATION",
        #     senders=senders,
        #     recipients=recipients,
        #     encap="MPLS" )
        #
        # if installResult:
        #     testResult = main.intents.testPointIntent(
        #         main,
        #         intentId=installResult,
        #         name="ENCAPSULATION",
        #         senders=senders,
        #         recipients=recipients,
        #         sw1="s5",
        #         sw2="s2",
        #         expectedLink=18 )
        # else:
        #     main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )
        #
        # utilities.assert_equals( expect=main.TRUE,
        #                          actual=testResult,
        #                          onpass=main.assertReturnString,
        #                          onfail=main.assertReturnString )

        main.intents.report( main )

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
        if main.initialized == main.FALSE:
            main.log.error( "Test components did not start correctly, skipping further tests" )
            main.skipCase()
        assert main, "There is no main"
        try:
            assert main.numSwitch
        except AssertionError:
            main.log.error( "Place the total number of switch topology in " +
                             main.numSwitch )
            main.initialized = main.FALSE
            main.skipCase()

        main.testName = "Single to Multi Point Intents"
        main.case( main.testName + " Test - " + str( main.Cluster.numCtrls ) +
                   " NODE(S) - OF " + main.OFProtocol + " - Using " + main.flowCompiler )
        main.caseExplanation = "This test case will test single point to" +\
                               " multi point intents using " +\
                               str( main.Cluster.numCtrls ) + " node(s) cluster;\n" +\
                               "Different type of hosts will be tested in " +\
                               "each step such as IPV4, Dual stack, VLAN etc" +\
                               ";\nThe test will use OF " + main.OFProtocol +\
                               " OVS running in Mininet and compile intents" +\
                               " using " + main.flowCompiler

        main.step( "NOOPTION: Install and test single point to multi point intents" )
        main.assertReturnString = "Assertion results for IPV4 single to multi point intent with no options set\n"
        senders = [
            { "name": "h8", "device": "of:0000000000000005/8" }
        ]
        recipients = [
            { "name": "h16", "device": "of:0000000000000006/8" },
            { "name": "h24", "device": "of:0000000000000007/8" }
        ]
        badSenders = [ { "name": "h9" } ]  # Senders that are not in the intent
        badRecipients = [ { "name": "h17" } ]  # Recipients that are not in the intent
        testResult = main.FALSE
        installResult = main.intents.installSingleToMultiIntent(
                                         main,
                                         name="NOOPTION",
                                         senders=senders,
                                         recipients=recipients,
                                         sw1="s5",
                                         sw2="s2" )

        if installResult:
            testResult = main.intents.testPointIntent(
                                         main,
                                         intentId=installResult,
                                         name="NOOPTION",
                                         senders=senders,
                                         recipients=recipients,
                                         badSenders=badSenders,
                                         badRecipients=badRecipients,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "IPV4: Install and test single point to multi point intents" )
        main.assertReturnString = "Assertion results for IPV4 single to multi point intent with IPV4 type and MAC addresses\n"
        senders = [
            { "name": "h8", "device": "of:0000000000000005/8", "mac": "00:00:00:00:00:08" }
        ]
        recipients = [
            { "name": "h16", "device": "of:0000000000000006/8", "mac": "00:00:00:00:00:10" },
            { "name": "h24", "device": "of:0000000000000007/8", "mac": "00:00:00:00:00:18" }
        ]
        badSenders = [ { "name": "h9" } ]  # Senders that are not in the intent
        badRecipients = [ { "name": "h17" } ]  # Recipients that are not in the intent
        testResult = main.FALSE
        installResult = main.intents.installSingleToMultiIntent(
                                         main,
                                         name="IPV4",
                                         senders=senders,
                                         recipients=recipients,
                                         ethType="IPV4",
                                         sw1="s5",
                                         sw2="s2" )

        if installResult:
            testResult = main.intents.testPointIntent(
                                         main,
                                         intentId=installResult,
                                         name="IPV4",
                                         senders=senders,
                                         recipients=recipients,
                                         badSenders=badSenders,
                                         badRecipients=badRecipients,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "IPV4_2: Add single point to multi point intents" )
        main.assertReturnString = "Assertion results for IPV4 single to multi point intent with IPV4 type and no MAC addresses\n"
        senders = [
            { "name": "h8", "device": "of:0000000000000005/8" }
        ]
        recipients = [
            { "name": "h16", "device": "of:0000000000000006/8" },
            { "name": "h24", "device": "of:0000000000000007/8" }
        ]
        badSenders = [ { "name": "h9" } ]  # Senders that are not in the intent
        badRecipients = [ { "name": "h17" } ]  # Recipients that are not in the intent
        testResult = main.FALSE
        installResult = main.intents.installSingleToMultiIntent(
                                         main,
                                         name="IPV4_2",
                                         senders=senders,
                                         recipients=recipients,
                                         ethType="IPV4",
                                         sw1="s5",
                                         sw2="s2" )

        if installResult:
            testResult = main.intents.testPointIntent(
                                         main,
                                         intentId=installResult,
                                         name="IPV4_2",
                                         senders=senders,
                                         recipients=recipients,
                                         badSenders=badSenders,
                                         badRecipients=badRecipients,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "VLAN: Add single point to multi point intents" )
        main.assertReturnString = "Assertion results for IPV4 single to multi point intent with IPV4 type and MAC addresses in the same VLAN\n"
        senders = [
            { "name": "h4", "device": "of:0000000000000005/4", "mac": "00:00:00:00:00:04", "vlan": "100" }
        ]
        recipients = [
            { "name": "h12", "device": "of:0000000000000006/4", "mac": "00:00:00:00:00:0C", "vlan": "100" },
            { "name": "h20", "device": "of:0000000000000007/4", "mac": "00:00:00:00:00:14", "vlan": "100" }
        ]
        badSenders = [ { "name": "h13" } ]  # Senders that are not in the intent
        badRecipients = [ { "name": "h21" } ]  # Recipients that are not in the intent
        testResult = main.FALSE
        installResult = main.intents.installSingleToMultiIntent(
                                         main,
                                         name="VLAN",
                                         senders=senders,
                                         recipients=recipients,
                                         sw1="s5",
                                         sw2="s2" )

        if installResult:
            testResult = main.intents.testPointIntent(
                                         main,
                                         intentId=installResult,
                                         name="VLAN",
                                         senders=senders,
                                         recipients=recipients,
                                         badSenders=badSenders,
                                         badRecipients=badRecipients,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "VLAN: Add single point to multi point intents" )
        main.assertReturnString = "Assertion results for single to multi point intent with VLAN treatment\n"
        senders = [
            { "name": "h5", "vlan": "200" }
        ]
        recipients = [
            { "name": "h12", "device": "of:0000000000000006/4", "mac": "00:00:00:00:00:0C", "vlan": "100" },
            { "name": "h20", "device": "of:0000000000000007/4", "mac": "00:00:00:00:00:14", "vlan": "100" }
        ]
        badSenders = [ { "name": "h13" } ]  # Senders that are not in the intent
        badRecipients = [ { "name": "h21" } ]  # Recipients that are not in the intent
        testResult = main.FALSE
        installResult = main.intents.installSingleToMultiIntent(
                                         main,
                                         name="VLAN2",
                                         senders=senders,
                                         recipients=recipients,
                                         sw1="s5",
                                         sw2="s2",
                                         setVlan=100 )

        if installResult:
            testResult = main.intents.testPointIntent(
                                         main,
                                         intentId=installResult,
                                         name="VLAN2",
                                         senders=senders,
                                         recipients=recipients,
                                         badSenders=badSenders,
                                         badRecipients=badRecipients,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        # Does not support Single point to multi point encapsulation
        # main.step( "ENCAPSULATION: Install and test single point to multi point intents" )
        # main.assertReturnString = "Assertion results for VLAN Encapsulation single to multi point intent\n"
        # senders = [
        #     { "name": "h8", "device": "of:0000000000000005/8" }
        # ]
        # recipients = [
        #     { "name": "h16", "device": "of:0000000000000006/8" },
        #     { "name": "h24", "device": "of:0000000000000007/8" }
        # ]
        # badSenders = [ { "name": "h9" } ]  # Senders that are not in the intent
        # badRecipients = [ { "name": "h17" } ]  # Recipients that are not in the intent
        # testResult = main.FALSE
        # installResult = main.intents.installSingleToMultiIntent(
        #                                  main,
        #                                  name="ENCAPSULATION",
        #                                  senders=senders,
        #                                  recipients=recipients,
        #                                  sw1="s5",
        #                                  sw2="s2",
        #                                  encap="VLAN" )
        #
        # if installResult:
        #     testResult = main.intents.testPointIntent(
        #                                  main,
        #                                  intentId=installResult,
        #                                  name="ENCAPSULATION",
        #                                  senders=senders,
        #                                  recipients=recipients,
        #                                  badSenders=badSenders,
        #                                  badRecipients=badRecipients,
        #                                  sw1="s5",
        #                                  sw2="s2",
        #                                  expectedLink=18 )
        # else:
        #     main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )
        #
        # utilities.assert_equals( expect=main.TRUE,
        #                          actual=testResult,
        #                          onpass=main.assertReturnString,
        #                          onfail=main.assertReturnString )

        main.intents.report( main )

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
        if main.initialized == main.FALSE:
            main.log.error( "Test components did not start correctly, skipping further tests" )
            main.skipCase()
        assert main, "There is no main"
        try:
            assert main.numSwitch
        except AssertionError:
            main.log.error( "Place the total number of switch topology in " +
                             main.numSwitch )
            main.initialized = main.FALSE
            main.skipCase()

        main.testName = "Multi To Single Point Intents"
        main.case( main.testName + " Test - " + str( main.Cluster.numCtrls ) +
                   " NODE(S) - OF " + main.OFProtocol + " - Using " + main.flowCompiler )
        main.caseExplanation = "This test case will test single point to" +\
                               " multi point intents using " +\
                               str( main.Cluster.numCtrls ) + " node(s) cluster;\n" +\
                               "Different type of hosts will be tested in " +\
                               "each step such as IPV4, Dual stack, VLAN etc" +\
                               ";\nThe test will use OF " + main.OFProtocol +\
                               " OVS running in Mininet and compile intents" +\
                               " using " + main.flowCompiler

        main.step( "NOOPTION: Add multi point to single point intents" )
        main.assertReturnString = "Assertion results for NOOPTION multi to single point intent\n"
        senders = [
            { "name": "h16", "device": "of:0000000000000006/8" },
            { "name": "h24", "device": "of:0000000000000007/8" }
        ]
        recipients = [
            { "name": "h8", "device": "of:0000000000000005/8" }
        ]
        badSenders = [ { "name": "h17" } ]  # Senders that are not in the intent
        badRecipients = [ { "name": "h9" } ]  # Recipients that are not in the intent
        testResult = main.FALSE
        installResult = main.intents.installMultiToSingleIntent(
                                         main,
                                         name="NOOPTION",
                                         senders=senders,
                                         recipients=recipients,
                                         sw1="s5",
                                         sw2="s2" )

        if installResult:
            testResult = main.intents.testPointIntent(
                                         main,
                                         intentId=installResult,
                                         name="NOOPTION",
                                         senders=senders,
                                         recipients=recipients,
                                         badSenders=badSenders,
                                         badRecipients=badRecipients,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "IPV4: Add multi point to single point intents" )
        main.assertReturnString = "Assertion results for IPV4 multi to single point intent with IPV4 type and MAC addresses\n"
        senders = [
            { "name": "h16", "device": "of:0000000000000006/8", "mac": "00:00:00:00:00:10" },
            { "name": "h24", "device": "of:0000000000000007/8", "mac": "00:00:00:00:00:18" }
        ]
        recipients = [
            { "name": "h8", "device": "of:0000000000000005/8", "mac": "00:00:00:00:00:08" }
        ]
        badSenders = [ { "name": "h17" } ]  # Senders that are not in the intent
        badRecipients = [ { "name": "h9" } ]  # Recipients that are not in the intent
        testResult = main.FALSE
        installResult = main.intents.installMultiToSingleIntent(
                                         main,
                                         name="IPV4",
                                         senders=senders,
                                         recipients=recipients,
                                         ethType="IPV4",
                                         sw1="s5",
                                         sw2="s2" )

        if installResult:
            testResult = main.intents.testPointIntent(
                                         main,
                                         intentId=installResult,
                                         name="IPV4",
                                         senders=senders,
                                         recipients=recipients,
                                         badSenders=badSenders,
                                         badRecipients=badRecipients,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "IPV4_2: Add multi point to single point intents" )
        main.assertReturnString = "Assertion results for IPV4 multi to single point intent with IPV4 type and no MAC addresses\n"
        senders = [
            { "name": "h16", "device": "of:0000000000000006/8" },
            { "name": "h24", "device": "of:0000000000000007/8" }
        ]
        recipients = [
            { "name": "h8", "device": "of:0000000000000005/8" }
        ]
        badSenders = [ { "name": "h17" } ]  # Senders that are not in the intent
        badRecipients = [ { "name": "h9" } ]  # Recipients that are not in the intent
        testResult = main.FALSE
        installResult = main.intents.installMultiToSingleIntent(
                                         main,
                                         name="IPV4_2",
                                         senders=senders,
                                         recipients=recipients,
                                         ethType="IPV4",
                                         sw1="s5",
                                         sw2="s2" )

        if installResult:
            testResult = main.intents.testPointIntent(
                                         main,
                                         intentId=installResult,
                                         name="IPV4_2",
                                         senders=senders,
                                         recipients=recipients,
                                         badSenders=badSenders,
                                         badRecipients=badRecipients,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "VLAN: Add multi point to single point intents" )
        main.assertReturnString = "Assertion results for IPV4 multi to single point intent with IPV4 type and no MAC addresses in the same VLAN\n"
        senders = [
            { "name": "h13", "device": "of:0000000000000006/5", "vlan": "200" },
            { "name": "h21", "device": "of:0000000000000007/5", "vlan": "200" }
        ]
        recipients = [
            { "name": "h5", "device": "of:0000000000000005/5", "vlan": "200" }
        ]
        badSenders = [ { "name": "h12" } ]  # Senders that are not in the intent
        badRecipients = [ { "name": "h20" } ]  # Recipients that are not in the intent
        testResult = main.FALSE
        installResult = main.intents.installMultiToSingleIntent(
                                         main,
                                         name="VLAN",
                                         senders=senders,
                                         recipients=recipients,
                                         sw1="s5",
                                         sw2="s2" )

        if installResult:
            testResult = main.intents.testPointIntent(
                                         main,
                                         intentId=installResult,
                                         name="VLAN",
                                         senders=senders,
                                         recipients=recipients,
                                         badSenders=badSenders,
                                         badRecipients=badRecipients,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        # Right now this fails because of this bug: https://jira.onosproject.org/browse/ONOS-4383
        main.step( "VLAN: Add multi point to single point intents" )
        main.assertReturnString = "Assertion results for multi to single point intent with VLAN ID treatment\n"
        senders = [
            { "name": "h13", "device": "of:0000000000000006/5", "vlan": "200" },
            { "name": "h21", "device": "of:0000000000000007/5", "vlan": "200" }
        ]
        recipients = [
            { "name": "h4", "vlan": "100" }
        ]
        badSenders = [ { "name": "h12" } ]  # Senders that are not in the intent
        badRecipients = [ { "name": "h20" } ]  # Recipients that are not in the intent
        testResult = main.FALSE
        installResult = main.intents.installMultiToSingleIntent(
                                         main,
                                         name="VLAN2",
                                         senders=senders,
                                         recipients=recipients,
                                         sw1="s5",
                                         sw2="s2",
                                         setVlan=100 )

        if installResult:
            testResult = main.intents.testPointIntent(
                                         main,
                                         intentId=installResult,
                                         name="VLAN2",
                                         senders=senders,
                                         recipients=recipients,
                                         badSenders=badSenders,
                                         badRecipients=badRecipients,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "ENCAPSULATION: Add multi point to single point intents" )
        main.assertReturnString = "Assertion results for VLAN Encapsulation multi to single point intent\n"
        senders = [
            { "name": "h16", "device": "of:0000000000000006/8" },
            { "name": "h24", "device": "of:0000000000000007/8" }
        ]
        recipients = [
            { "name": "h8", "device": "of:0000000000000005/8" }
        ]
        badSenders = [ { "name": "h17" } ]  # Senders that are not in the intent
        badRecipients = [ { "name": "h9" } ]  # Recipients that are not in the intent
        testResult = main.FALSE
        installResult = main.intents.installMultiToSingleIntent(
                                         main,
                                         name="ENCAPSULATION",
                                         senders=senders,
                                         recipients=recipients,
                                         sw1="s5",
                                         sw2="s2",
                                         encap="VLAN" )

        if installResult:
            testResult = main.intents.testPointIntent(
                                         main,
                                         intentId=installResult,
                                         name="ENCAPSULATION",
                                         senders=senders,
                                         recipients=recipients,
                                         badSenders=badSenders,
                                         badRecipients=badRecipients,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )
        """
        Testing MPLS would require kernel version of 4.1 or higher ( Current version is 3.13 )
        main.step( "ENCAPSULATION: Add multi point to single point intents" )
        main.assertReturnString = "Assertion results for MPLS Encapsulation multi to single point intent\n"
        senders = [
           { "name": "h16", "device": "of:0000000000000006/8" },
           { "name": "h24", "device": "of:0000000000000007/8" }
        ]
        recipients = [
           { "name": "h8", "device": "of:0000000000000005/8" }
        ]
        badSenders = [ { "name": "h17" } ]  # Senders that are not in the intent
        badRecipients = [ { "name": "h9" } ]  # Recipients that are not in the intent
        testResult = main.FALSE
        installResult = main.intents.installMultiToSingleIntent(
           main,
           name="ENCAPSULATION",
           senders=senders,
           recipients=recipients,
           sw1="s5",
           sw2="s2",
           encap="MPLS" )

        if installResult:
           testResult = main.intents.testPointIntent(
               main,
               intentId=installResult,
               name="ENCAPSULATION",
               senders=senders,
               recipients=recipients,
               badSenders=badSenders,
               badRecipients=badRecipients,
               sw1="s5",
               sw2="s2",
               expectedLink=18 )
        else:
           main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                actual=testResult,
                                onpass=main.assertReturnString,
                                onfail=main.assertReturnString )
        """

        main.intents.report( main )

    def CASE5000( self, main ):
        """
        Tests Host Mobility
        Modifies the topology location of h1
        """
        if main.initialized == main.FALSE:
            main.log.error( "Test components did not start correctly, skipping further tests" )
            main.skipCase()
        assert main, "There is no main"
        try:
            assert main.numSwitch
        except AssertionError:
            main.log.error( "Place the total number of switch topology in " +
                             main.numSwitch )
            main.initialized = main.FALSE
            main.skipCase()
        main.case( "Test host mobility with host intents " + " - " + str( main.Cluster.numCtrls ) +
                   " NODE(S) - OF " + main.OFProtocol + " - Using " + main.flowCompiler )
        main.step( "Testing host mobility by moving h1 from s5 to s6" )

        main.log.info( "Moving h1 from s5 to s6" )
        main.Network.moveHost( "h1", "s5", "s6" )

        # Send discovery ping from moved host
        # Moving the host brings down the default interfaces and creates a new one.
        # Scapy is restarted on this host to detect the new interface
        main.h1.stopScapy()
        main.h1.startScapy()

        # Discover new host location in ONOS and populate host data.
        # Host 1 IP and MAC should be unchanged
        main.intents.sendDiscoveryArp( main, [ main.h1 ] )
        main.intents.populateHostData( main )

        h1PostMove = main.hostsData[ "h1" ][ "location" ][ 0:19 ]

        utilities.assert_equals( expect="of:0000000000000006",
                                 actual=h1PostMove,
                                 onpass="Mobility: Successfully moved h1 to s6",
                                 onfail="Mobility: Failed to move h1 to s6" +
                                        " to single point intents" +
                                        " with IPV4 type and MAC addresses" +
                                        " in the same VLAN" )

        main.step( "IPV4: Add host intents between h1 and h9" )
        main.assertReturnString = "Assert result for IPV4 host intent between h1, moved, and h9\n"
        host1 = { "name": "h1", "id": "00:00:00:00:00:01/-1" }
        host2 = { "name": "h9", "id": "00:00:00:00:00:09/-1" }
        testResult = main.FALSE
        installResult = main.intents.installHostIntent( main,
                                                        name="IPV4 Mobility IPV4",
                                                        onosNode=0,
                                                        host1=host1,
                                                        host2=host2 )
        if installResult:
            testResult = main.intents.testHostIntent( main,
                                                      name="Host Mobility IPV4",
                                                      intentId=installResult,
                                                      onosNode=0,
                                                      host1=host1,
                                                      host2=host2,
                                                      sw1="s6",
                                                      sw2="s2",
                                                      expectedLink=18 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.intents.report( main )

    def CASE6000( self, main ):
        """
        Tests Multi to Single Point Intent and Single to Multi Point Intent End Point Failure
        """
        # At some later point discussion on this behavior in MPSP and SPMP intents
        # will be reoppened and this test case may need to be updated to reflect
        # the outcomes of that discussion
        if main.initialized == main.FALSE:
            main.log.error( "Test components did not start correctly, skipping further tests" )
            main.skipCase()
        assert main, "There is no main"
        try:
            assert main.numSwitch
        except AssertionError:
            main.log.error( "Place the total number of switch topology in " + main.numSwitch )
            main.initialized = main.FALSE
            main.skipCase()
        main.case( "Test Multi to Single End Point Failure" + " - " + str( main.Cluster.numCtrls ) +
                   " NODE(S) - OF " + main.OFProtocol + " - Using " + main.flowCompiler )
        main.step( "Installing Multi to Single Point intents with no options set" )
        main.assertReturnString = "Assertion results for IPV4 multi to single " +\
                                  "point intent end point failure with no options set\n"
        senders = [
            { "name": "h16", "device": "of:0000000000000006/8" },
            { "name": "h24", "device": "of:0000000000000007/8" }
        ]
        recipients = [
            { "name": "h8", "device": "of:0000000000000005/8" }
        ]
        isolatedSenders = [
            { "name": "h24" }
        ]
        isolatedRecipients = []
        testResult = main.FALSE
        installResult = main.intents.installMultiToSingleIntent(
                                         main,
                                         name="NOOPTION",
                                         senders=senders,
                                         recipients=recipients,
                                         sw1="s5",
                                         sw2="s2" )

        if installResult:
            testResult = main.intents.testEndPointFail(
                                         main,
                                         intentId=installResult,
                                         name="NOOPTION",
                                         senders=senders,
                                         recipients=recipients,
                                         isolatedSenders=isolatedSenders,
                                         isolatedRecipients=isolatedRecipients,
                                         sw1="s6",
                                         sw2="s2",
                                         sw3="s4",
                                         sw4="s1",
                                         sw5="s3",
                                         expectedLink1=16,
                                         expectedLink2=14 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "Installing Multi to Single Point intents with partial failure allowed" )

        main.assertReturnString = "Assertion results for IPV4 multi to single " +\
                                  "with partial failures allowed\n"
        senders = [
            { "name": "h16", "device": "of:0000000000000006/8" },
            { "name": "h24", "device": "of:0000000000000007/8" }
        ]
        recipients = [
            { "name": "h8", "device": "of:0000000000000005/8" }
        ]
        isolatedSenders = [
            { "name": "h24" }
        ]
        isolatedRecipients = []
        testResult = main.FALSE
        installResult = main.intents.installMultiToSingleIntent(
                                         main,
                                         name="NOOPTION",
                                         senders=senders,
                                         recipients=recipients,
                                         sw1="s5",
                                         sw2="s2",
                                         partial=True )

        if installResult:
            testResult = main.intents.testEndPointFail(
                                         main,
                                         intentId=installResult,
                                         name="NOOPTION",
                                         senders=senders,
                                         recipients=recipients,
                                         isolatedSenders=isolatedSenders,
                                         isolatedRecipients=isolatedRecipients,
                                         sw1="s6",
                                         sw2="s2",
                                         sw3="s4",
                                         sw4="s1",
                                         sw5="s3",
                                         expectedLink1=16,
                                         expectedLink2=14,
                                         partial=True )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "NOOPTION: Install and test single point to multi point intents" )
        main.assertReturnString = "Assertion results for IPV4 single to multi " +\
                                  "point intent with no options set\n"
        senders = [
            { "name": "h8", "device": "of:0000000000000005/8" }
        ]
        recipients = [
            { "name": "h16", "device": "of:0000000000000006/8" },
            { "name": "h24", "device": "of:0000000000000007/8" }
        ]
        isolatedSenders = []
        isolatedRecipients = [
            { "name": "h24" }
        ]
        testResult = main.FALSE
        installResult = main.intents.installSingleToMultiIntent(
                                         main,
                                         name="NOOPTION",
                                         senders=senders,
                                         recipients=recipients,
                                         sw1="s5",
                                         sw2="s2" )

        if installResult:
            testResult = main.intents.testEndPointFail(
                                         main,
                                         intentId=installResult,
                                         name="NOOPTION",
                                         senders=senders,
                                         recipients=recipients,
                                         isolatedSenders=isolatedSenders,
                                         isolatedRecipients=isolatedRecipients,
                                         sw1="s6",
                                         sw2="s2",
                                         sw3="s4",
                                         sw4="s1",
                                         sw5="s3",
                                         expectedLink1=16,
                                         expectedLink2=14 )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )
        # Right now this functionality doesn't work properly in SPMP intents
        main.step( "NOOPTION: Install and test single point to multi point " +
                   "intents with partial failures allowed" )
        main.assertReturnString = "Assertion results for IPV4 single to multi " +\
                                  "point intent with partial failures allowed\n"
        senders = [
            { "name": "h8", "device": "of:0000000000000005/8" }
        ]
        recipients = [
            { "name": "h16", "device": "of:0000000000000006/8" },
            { "name": "h24", "device": "of:0000000000000007/8" }
        ]
        isolatedSenders = []
        isolatedRecipients = [
            { "name": "h24" }
        ]
        testResult = main.FALSE
        installResult = main.intents.installSingleToMultiIntent(
                                         main,
                                         name="NOOPTION",
                                         senders=senders,
                                         recipients=recipients,
                                         sw1="s5",
                                         sw2="s2",
                                         partial=True )

        if installResult:
            testResult = main.intents.testEndPointFail(
                                         main,
                                         intentId=installResult,
                                         name="NOOPTION",
                                         senders=senders,
                                         recipients=recipients,
                                         isolatedSenders=isolatedSenders,
                                         isolatedRecipients=isolatedRecipients,
                                         sw1="s6",
                                         sw2="s2",
                                         sw3="s4",
                                         sw4="s1",
                                         sw5="s3",
                                         expectedLink1=16,
                                         expectedLink2=14,
                                         partial=True )
        else:
            main.Cluster.active( 0 ).CLI.removeAllIntents( purge=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.intents.report( main )
