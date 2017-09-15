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
# TODO: Replace the CLI calls with REST API equivalents as they become available.
#           - May need to write functions in the onosrestdriver.py file to do this
# TODO: Complete implementation of case 3000, 4000, and 6000 as REST API allows
#           -Currently there is no support in the REST API for Multi to Single and Single to Multi point intents
#            As such, these cases are incomplete and should not be enabled in the .params file

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
        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
            main.testSetUp = ONOSSetup()
        except ImportError:
            main.log.error( "ONOSSetup not found. exiting the test" )
            main.cleanAndExit()
        main.testSetUp.envSetupDescription()
        stepResult = main.FALSE

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
            main.removeIntentsleeo = int( main.params[ 'SLEEP' ][ 'removeintent' ] )
            main.rerouteSleep = int( main.params[ 'SLEEP' ][ 'reroute' ] )
            main.fwdSleep = int( main.params[ 'SLEEP' ][ 'fwd' ] )
            main.addIntentSleep = int( main.params[ 'SLEEP' ][ 'addIntent' ] )
            main.checkTopoAttempts = int( main.params[ 'SLEEP' ][ 'topoAttempts' ] )
            main.flowDurationSleep = int( main.params[ 'SLEEP' ][ 'flowDuration' ] )
            main.numSwitch = int( main.params[ 'MININET' ][ 'switch' ] )
            main.numLinks = int( main.params[ 'MININET' ][ 'links' ] )
            main.hostsData = {}
            main.scapyHostNames = main.params[ 'SCAPY' ][ 'HOSTNAMES' ].split( ',' )
            main.scapyHosts = []  # List of scapy hosts for iterating
            main.assertReturnString = ''  # Assembled assert return string
            main.cycle = 0  # How many times FUNCintent has run through its tests

            # -- INIT SECTION, ONLY RUNS ONCE -- #

            main.intentFunction = imp.load_source( wrapperFile2,
                                                   main.dependencyPath +
                                                   wrapperFile2 +
                                                   ".py" )

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
        main.initialized = main.testSetUp.ONOSSetUp( main.Mininet1, main.Cluster, True )
        main.intentFunction.report( main )

    def CASE8( self, main ):
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

    def CASE9( self, main ):
        """
            Report errors/warnings/exceptions
        """
        main.log.info( "Error report: \n" )
        main.ONOSbench.logReport( main.Cluster.active( 0 ).ipAddress,
                                  [ "INFO", "FOLLOWER", "WARN", "flow", "ERROR", "Except" ],
                                  "s" )
        # main.ONOSbench.logReport( globalONOSip[ 1 ], [ "INFO" ], "d" )

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
            main.initialized = main.FALSE

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

        assignResult = main.TRUE
        switchList = []

        # Creates a list switch name, use getSwitch() function later...
        for i in range( 1, ( main.numSwitch + 1 ) ):
            switchList.append( 's' + str( i ) )

        tempONOSip = main.Cluster.getIps()

        assignResult = main.Mininet1.assignSwController( sw=switchList,
                                                         ip=tempONOSip,
                                                         port='6653' )
        if not assignResult:
            main.log.error( "Problem assigning mastership of switches, skipping further test cases" )
            main.initialized = main.FALSE
            main.skipCase()

        for i in range( 1, ( main.numSwitch + 1 ) ):
            response = main.Mininet1.getSwController( "s" + str( i ) )
            print( "Response is " + str( response ) )
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
        import json
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
            Discover all hosts and store its data to a dictionary
        """
        if main.initialized == main.FALSE:
            main.log.error( "Test components did not start correctly, skipping further tests" )
            main.skipCase()
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
        if not stepResult:
            main.initialized = main.FALSE

    def CASE15( self, main ):
        """main.topo.
            Discover all hosts with scapy arp packets and store its data to a dictionary
        """
        if main.initialized == main.FALSE:
            main.log.error( "Test components did not start correctly, skipping further tests" )
            main.skipCase()
        main.case( "Discover all hosts using scapy" )
        main.step( "Send packets from each host to the first host and confirm onos discovery" )

        import collections
        if len( main.scapyHosts ) < 1:
            main.log.error( "No scapy hosts have been created" )
            main.initialized = main.FALSE
            main.skipCase()

        # Send ARP packets from each scapy host component
        main.intentFunction.sendDiscoveryArp( main, main.scapyHosts )

        stepResult = utilities.retry( f=main.intentFunction.confirmHostDiscovery,
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
        stepResult = main.intentFunction.populateHostData( main )
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

        balanceResult = main.FALSE
        balanceResult = utilities.retry( f=main.Cluster.active( 0 ).CLI.balanceMasters, retValue=main.FALSE, args=[] )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully balanced mastership of switches",
                                 onfail="Failed to balance mastership of switches" )
        if not stepResult:
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
        if not stepResult:
            main.initialized = main.FALSE

    def CASE18( self, main ):
        """
            Stop mininet and remove scapy hosts
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
        import time
        import json
        import re
        if main.initialized == main.FALSE:
            main.log.error( "Test components did not start correctly, skipping further tests" )
            main.skipCase()
        # Assert variables - These variable's name|format must be followed
        # if you want to use the wrapper function
        assert main, "There is no main"
        try:
            assert main.Mininet1
        except AssertionError:
            main.log.error( "Mininet handle should be named Mininet1, skipping test cases" )
            main.initialized = main.FALSE
            main.skipCase()
        try:
            assert main.numSwitch
        except AssertionError:
            main.log.error( "Place the total number of switch topology in " +
                             main.numSwitch )
            main.initialized = main.FALSE
            main.skipCase()

        # Save leader candidates
        intentLeadersOld = main.Cluster.active( 0 ).CLI.leaderCandidates()

        main.case( "Host Intents Test - " + str( main.Cluster.numCtrls ) +
                   " NODE(S) - OF " + main.OFProtocol + " - Using " + main.flowCompiler )
        main.caseExplanation = "This test case tests Host intents using " +\
                                str( main.Cluster.numCtrls ) + " node(s) cluster;\n" +\
                                "Different type of hosts will be tested in " +\
                                "each step such as IPV4, Dual stack, VLAN " +\
                                "etc;\nThe test will use OF " + main.OFProtocol +\
                                " OVS running in Mininet and compile intents" +\
                                " using " + main.flowCompiler

        main.step( "IPV4: Add and test host intents between h1 and h9" )
        main.assertReturnString = "Assertion result for IPV4 host intent with mac addresses\n"
        host1 = { "name": "h1", "id": "00:00:00:00:00:01/-1" }
        host2 = { "name": "h9", "id": "00:00:00:00:00:09/-1" }
        testResult = main.FALSE
        installResult = main.intentFunction.installHostIntent( main,
                                                               name='IPV4',
                                                               onosNode='0',
                                                               host1=host1,
                                                               host2=host2 )

        if installResult:
            testResult = main.intentFunction.testHostIntent( main,
                                                             name='IPV4',
                                                             intentId=installResult,
                                                             onosNode='0',
                                                             host1=host1,
                                                             host2=host2,
                                                             sw1='s5',
                                                             sw2='s2',
                                                             expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "DUALSTACK1: Add host intents between h3 and h11" )
        main.assertReturnString = "Assertion Result for dualstack IPV4 with MAC addresses\n"
        host1 = { "name": "h3", "id": "00:00:00:00:00:03/-1" }
        host2 = { "name": "h11", "id": "00:00:00:00:00:0B/-1" }
        testResult = main.FALSE
        installResult = main.intentFunction.installHostIntent( main,
                                                               name='DUALSTACK1',
                                                               onosNode='0',
                                                               host1=host1,
                                                               host2=host2 )

        if installResult:
            testResult = main.intentFunction.testHostIntent( main,
                                                             name='DUALSTACK1',
                                                             intentId=installResult,
                                                             onosNode='0',
                                                             host1=host1,
                                                             host2=host2,
                                                             sw1='s5',
                                                             sw2='s2',
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
        installResult = main.intentFunction.installHostIntent( main,
                                                               name='DUALSTACK2',
                                                               onosNode='0',
                                                               host1=host1,
                                                               host2=host2 )

        if installResult:
            testResult = main.intentFunction.testHostIntent( main,
                                                             name='DUALSTACK2',
                                                             intentId=installResult,
                                                             onosNode='0',
                                                             host1=host1,
                                                             host2=host2,
                                                             sw1='s5',
                                                             sw2='s2',
                                                             expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "1HOP: Add host intents between h1 and h3" )
        main.assertReturnString = "Assertion Result for 1HOP for IPV4 same switch\n"
        host1 = { "name": "h1" }
        host2 = { "name": "h3" }
        testResult = main.FALSE
        installResult = main.intentFunction.installHostIntent( main,
                                                               name='1HOP',
                                                               onosNode='0',
                                                               host1=host1,
                                                               host2=host2 )

        if installResult:
            testResult = main.intentFunction.testHostIntent( main,
                                                             name='1HOP',
                                                             intentId=installResult,
                                                             onosNode='0',
                                                             host1=host1,
                                                             host2=host2,
                                                             sw1='s5',
                                                             sw2='s2',
                                                             expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "VLAN1: Add vlan host intents between h4 and h12" )
        main.assertReturnString = "Assertion Result vlan IPV4\n"
        host1 = { "name": "h4", "id": "00:00:00:00:00:04/100", "vlanId": "100" }
        host2 = { "name": "h12", "id": "00:00:00:00:00:0C/100", "vlanId": "100" }
        testResult = main.FALSE
        installResult = main.intentFunction.installHostIntent( main,
                                                               name='VLAN1',
                                                               onosNode='0',
                                                               host1=host1,
                                                               host2=host2 )

        if installResult:
            testResult = main.intentFunction.testHostIntent( main,
                                                             name='VLAN1',
                                                             intentId=installResult,
                                                             onosNode='0',
                                                             host1=host1,
                                                             host2=host2,
                                                             sw1='s5',
                                                             sw2='s2',
                                                             expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        # This step isn't currently possible to perform in the REST API
        # main.step( "VLAN2: Add inter vlan host intents between h13 and h20" )
        # main.assertReturnString = "Assertion Result different VLAN negative test\n"
        # host1 = { "name":"h13" }
        # host2 = { "name":"h20" }
        # testResult = main.FALSE
        # installResult = main.intentFunction.installHostIntent( main,
        #                                       name='VLAN2',
        #                                       onosNode='0',
        #                                       host1=host1,
        #                                       host2=host2 )

        # if installResult:
        #     testResult = main.intentFunction.testHostIntent( main,
        #                                       name='VLAN2',
        #                                       intentId=installResult,
        #                                       onosNode='0',
        #                                       host1=host1,
        #                                       host2=host2,
        #                                       sw1='s5',
        #                                       sw2='s2',
        #                                       expectedLink=18 )

        # utilities.assert_equals( expect=main.TRUE,
        #                          actual=testResult,
        #                          onpass=main.assertReturnString,
        #                          onfail=main.assertReturnString )

        # Change the following to use the REST API when leader checking is
        # supported by it

        main.step( "Confirm that ONOS leadership is unchanged" )
        intentLeadersNew = main.Cluster.active( 0 ).CLI.leaderCandidates()
        main.intentFunction.checkLeaderChange( intentLeadersOld,
                                                intentLeadersNew )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass="ONOS Leaders Unchanged",
                                 onfail="ONOS Leader Mismatch" )

        main.intentFunction.report( main )

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
            assert main.Mininet1
        except AssertionError:
            main.log.error( "Mininet handle should be named Mininet1, skipping test cases" )
            main.initialized = main.FALSE
            main.skipCase()
        try:
            assert main.numSwitch
        except AssertionError:
            main.log.error( "Place the total number of switch topology in " +
                             main.numSwitch )
            main.initialized = main.FALSE
            main.skipCase()

        main.case( "Point Intents Test - " + str( main.Cluster.numCtrls ) +
                   " NODE(S) - OF " + main.OFProtocol + " - Using " + main.flowCompiler )
        main.caseExplanation = "This test case will test point to point" + \
                               " intents using " + str( main.Cluster.numCtrls ) + \
                               " node(s) cluster;\n" + \
                               "Different type of hosts will be tested in " + \
                               "each step such as IPV4, Dual stack, VLAN etc" + \
                               ";\nThe test will use OF " + main.OFProtocol + \
                               " OVS running in Mininet and compile intents" + \
                               " using " + main.flowCompiler

        # No option point intent
        main.step( "NOOPTION: Add point intents between h1 and h9" )
        main.assertReturnString = "Assertion Result for NOOPTION point intent\n"
        senders = [
            { "name": "h1", "device": "of:0000000000000005/1" }
        ]
        recipients = [
            { "name": "h9", "device": "of:0000000000000006/1" }
        ]
        testResult = main.FALSE
        installResult = main.intentFunction.installPointIntent(
            main,
            name="NOOPTION",
            senders=senders,
            recipients=recipients )

        if installResult:
            testResult = main.intentFunction.testPointIntent(
                                         main,
                                         intentId=installResult,
                                         name="NOOPTION",
                                         senders=senders,
                                         recipients=recipients,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )

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
        installResult = main.intentFunction.installPointIntent(
            main,
            name="IPV4",
            senders=senders,
            recipients=recipients,
            ethType="IPV4" )

        if installResult:
            testResult = main.intentFunction.testPointIntent(
                                         main,
                                         intentId=installResult,
                                         name="IPV4",
                                         senders=senders,
                                         recipients=recipients,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        # main.step( "Protected: Add point intents between h1 and h9" )
        # main.assertReturnString = "Assertion Result for protected point intent\n"
        # senders = [
        #     { "name": "h1", "device": "of:0000000000000005/1", "mac": "00:00:00:00:00:01" }
        # ]
        # recipients = [
        #     { "name": "h9", "device": "of:0000000000000006/1", "mac": "00:00:00:00:00:09" }
        # ]
        # testResult = main.FALSE
        # installResult = main.intentFunction.installPointIntent(
        #     main,
        #     name="Protected",
        #     senders=senders,
        #     recipients=recipients,
        #     protected=True )
        #
        # if installResult:
        #     testResult = main.intentFunction.testPointIntent(
        #         main,
        #         name="Protected",
        #         intentId=installResult,
        #         senders=senders,
        #         recipients=recipients,
        #         sw1="s5",
        #         sw2="s2",
        #         protected=True,
        #         expectedLink=18 )
        #
        # utilities.assert_equals( expect=main.TRUE,
        #                          actual=testResult,
        #                          onpass=main.assertReturnString,
        #                          onfail=main.assertReturnString )

        main.step( "IPV4_2: Add point intents between h1 and h9" )
        main.assertReturnString = "Assertion Result for IPV4 no mac address point intents\n"
        senders = [
            { "name": "h1", "device": "of:0000000000000005/1" }
        ]
        recipients = [
            { "name": "h9", "device": "of:0000000000000006/1" }
        ]
        installResult = main.intentFunction.installPointIntent(
            main,
            name="IPV4_2",
            senders=senders,
            recipients=recipients,
            ethType="IPV4" )

        if installResult:
            testResult = main.intentFunction.testPointIntent(
                                         main,
                                         intentId=installResult,
                                         name="IPV4_2",
                                         senders=senders,
                                         recipients=recipients,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )

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
        # ipProto = main.params[ 'SDNIP' ][ 'icmpProto' ]
        ipProto = main.params[ 'SDNIP' ][ 'ipPrototype' ]
        # Uneccessary, not including this in the selectors
        tcpSrc = main.params[ 'SDNIP' ][ 'srcPort' ]
        tcpDst = main.params[ 'SDNIP' ][ 'dstPort' ]

        installResult = main.intentFunction.installPointIntent(
            main,
            name="SDNIP-ICMP",
            senders=senders,
            recipients=recipients,
            ethType="IPV4",
            ipProto=ipProto,
            tcpSrc=tcpSrc,
            tcpDst=tcpDst )

        if installResult:
            testResult = main.intentFunction.testPointIntent(
                main,
                intentId=installResult,
                name="SDNIP_ICMP",
                senders=senders,
                recipients=recipients,
                sw1="s5",
                sw2="s2",
                expectedLink=18,
                useTCP=True )

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
        installResult = main.intentFunction.installPointIntent(
            main,
            name="DUALSTACK1",
            senders=senders,
            recipients=recipients,
            ethType="IPV4" )

        if installResult:
            testResult = main.intentFunction.testPointIntent(
                                        main,
                                        intentId=installResult,
                                        name="DUALSTACK1",
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
        main.assertReturnString = "Assertion Result for VLAN IPV4 with mac address point intents\n"
        senders = [
            { "name": "h5", "device": "of:0000000000000005/5", "mac": "00:00:00:00:00:05", "vlanId": "200" }
        ]
        recipients = [
            { "name": "h21", "device": "of:0000000000000007/5", "mac": "00:00:00:00:00:15", "vlanId": "200" }
        ]
        installResult = main.intentFunction.installPointIntent(
            main,
            name="VLAN",
            senders=senders,
            recipients=recipients )

        if installResult:
            testResult = main.intentFunction.testPointIntent(
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

        # TODO: implement VLAN selector REST API intent test once supported

        main.step( "1HOP: Add point intents between h1 and h3" )
        main.assertReturnString = "Assertion Result for 1HOP IPV4 with no mac address point intents\n"
        senders = [
            { "name": "h1", "device": "of:0000000000000005/1", "mac": "00:00:00:00:00:01" }
        ]
        recipients = [
            { "name": "h3", "device": "of:0000000000000005/3", "mac": "00:00:00:00:00:03" }
        ]
        installResult = main.intentFunction.installPointIntent(
            main,
            name="1HOP IPV4",
            senders=senders,
            recipients=recipients,
            ethType="IPV4" )

        if installResult:
            testResult = main.intentFunction.testPointIntent(
                                         main,
                                         intentId=installResult,
                                         name="1HOP IPV4",
                                         senders=senders,
                                         recipients=recipients,
                                         sw1="s5",
                                         sw2="s2",
                                         expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
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
        if main.initialized == main.FALSE:
            main.log.error( "Test components did not start correctly, skipping further tests" )
            main.skipCase()
        assert main, "There is no main"

        try:
            assert main.Mininet1, "Mininet handle should be named Mininet1, skipping test cases"
            assert main.numSwitch, "Place the total number of switch topology in main.numSwitch"
        except AssertionError:
            main.initialized = main.FALSE
            main.skipCase()

        main.testName = "Single to Multi Point Intents"
        main.case( main.testName + " Test - " + str( main.Cluster.numCtrls ) +
                   " NODE(S) - OF " + main.OFProtocol + " - Using " + main.flowCompiler )
        main.caseExplanation = "This test case will test single point to" + \
                               " multi point intents using " + \
                               str( main.Cluster.numCtrls ) + " node(s) cluster;\n" + \
                               "Different type of hosts will be tested in " + \
                               "each step such as IPV4, Dual stack, VLAN etc" + \
                               ";\nThe test will use OF " + main.OFProtocol + \
                               " OVS running in Mininet and compile intents" + \
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
        installResult = main.intentFunction.installSingleToMultiIntent(
            main,
            name="NOOPTION",
            senders=senders,
            recipients=recipients )

        if installResult:
            testResult = main.intentFunction.testPointIntent(
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
        main.assertReturnString = "Assertion results for IPV4 single to multi point intent " \
                                  "with IPV4 type and MAC addresses\n"
        senders = [
            { "name": "h8", "device": "of:0000000000000005/8", "mac": "00:00:00:00:00:08" }
        ]
        recipients = [
            { "name": "h16", "device": "of:0000000000000006/8", "mac": "00:00:00:00:00:10" },
            { "name": "h24", "device": "of:0000000000000007/8", "mac": "00:00:00:00:00:18" }
        ]
        badSenders = [ { "name": "h9" } ]  # Senders that are not in the intent
        badRecipients = [ { "name": "h17" } ]  # Recipients that are not in the intent
        installResult = main.intentFunction.installSingleToMultiIntent(
            main,
            name="IPV4",
            senders=senders,
            recipients=recipients,
            ethType="IPV4" )

        if installResult:
            testResult = main.intentFunction.testPointIntent(
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
        main.assertReturnString = "Assertion results for IPV4 single to multi point intent " \
                                  "with IPV4 type and no MAC addresses\n"
        senders = [
            { "name": "h8", "device": "of:0000000000000005/8" }
        ]
        recipients = [
            { "name": "h16", "device": "of:0000000000000006/8" },
            { "name": "h24", "device": "of:0000000000000007/8" }
        ]
        badSenders = [ { "name": "h9" } ]  # Senders that are not in the intent
        badRecipients = [ { "name": "h17" } ]  # Recipients that are not in the intent
        installResult = main.intentFunction.installSingleToMultiIntent(
            main,
            name="IPV4_2",
            senders=senders,
            recipients=recipients,
            ethType="IPV4" )

        if installResult:
            testResult = main.intentFunction.testPointIntent(
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
        main.assertReturnString = "Assertion results for IPV4 single to multi point intent with IPV4 type " \
                                  "and MAC addresses in the same VLAN\n"
        senders = [
            { "name": "h4", "device": "of:0000000000000005/4", "mac": "00:00:00:00:00:04", "vlan": "100" }
        ]
        recipients = [
            { "name": "h12", "device": "of:0000000000000006/4", "mac": "00:00:00:00:00:0C", "vlan": "100" },
            { "name": "h20", "device": "of:0000000000000007/4", "mac": "00:00:00:00:00:14", "vlan": "100" }
        ]
        badSenders = [ { "name": "h13" } ]  # Senders that are not in the intent
        badRecipients = [ { "name": "h21" } ]  # Recipients that are not in the intent
        installResult = main.intentFunction.installSingleToMultiIntent(
            main,
            name="VLAN",
            senders=senders,
            recipients=recipients,
            sw1="s5",
            sw2="s2" )

        if installResult:
            testResult = main.intentFunction.testPointIntent(
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
            main.Cluster.active( 0 ).CLI.removeAllIntents()

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
        installResult = main.intentFunction.installSingleToMultiIntent(
            main,
            name="VLAN2",
            senders=senders,
            recipients=recipients,
            sw1="s5",
            sw2="s2" )
        # setVlan=100 )

        if installResult:
            testResult = main.intentFunction.testPointIntent(
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
            main.Cluster.active( 0 ).CLI.removeAllIntents()

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
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
        assert main.Mininet1, "Mininet handle should be named Mininet1"
        assert main.numSwitch, "Placed the total number of switch topology in \
                                main.numSwitch"

        main.case( "Multi To Single Point Intents Test - " +
                   str( main.Cluster.numCtrls ) + " NODE(S) - OF " + main.OFProtocol + " - Using " + main.flowCompiler )
        main.caseExplanation = "This test case will test single point to" +\
                               " multi point intents using " +\
                               str( main.Cluster.numCtrls ) + " node(s) cluster;\n" +\
                               "Different type of hosts will be tested in " +\
                               "each step such as IPV4, Dual stack, VLAN etc" +\
                               ";\nThe test will use OF " + main.OFProtocol +\
                               " OVS running in Mininet and compile intents" +\
                               " using " + main.flowCompiler

        main.step( "NOOPTION: Add multi point to single point intents" )
        stepResult = main.TRUE
        hostNames = [ 'h8', 'h16', 'h24' ]
        devices = [ 'of:0000000000000005/8', 'of:0000000000000006/8',
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
        devices = [ 'of:0000000000000005/5', 'of:0000000000000006/5',
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
        Tests Host Mobility
        Modifies the topology location of h1
        """
        if main.initialized == main.FALSE:
            main.log.error( "Test components did not start correctly, skipping further tests" )
            main.skipCase()
        # Assert variables - These variable's name|format must be followed
        # if you want to use the wrapper function
        assert main, "There is no main"
        try:
            assert main.Mininet1
        except AssertionError:
            main.log.error( "Mininet handle should be named Mininet1, skipping test cases" )
            main.initialized = main.FALSE
            main.skipCase()
        try:
            assert main.numSwitch
        except AssertionError:
            main.log.error( "Place the total number of switch topology in " +
                             main.numSwitch )
            main.initialized = main.FALSE
            main.skipCase()
        main.case( "Test host mobility with host intents " )
        main.step( "Testing host mobility by moving h1 from s5 to s6" )
        h1PreMove = main.hostsData[ "h1" ][ "location" ][ 0:19 ]

        main.log.info( "Moving h1 from s5 to s6" )
        main.Mininet1.moveHost( "h1", "s5", "s6" )

        # Send discovery ping from moved host
        # Moving the host brings down the default interfaces and creates a new one.
        # Scapy is restarted on this host to detect the new interface
        main.h1.stopScapy()
        main.h1.startScapy()

        # Discover new host location in ONOS and populate host data.
        # Host 1 IP and MAC should be unchanged
        main.intentFunction.sendDiscoveryArp( main, [ main.h1 ] )
        main.intentFunction.populateHostData( main )

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

        installResult = main.intentFunction.installHostIntent( main,
                                                               name='IPV4 Mobility IPV4',
                                                               onosNode='0',
                                                               host1=host1,
                                                               host2=host2 )
        if installResult:
            testResult = main.intentFunction.testHostIntent( main,
                                                             name='Host Mobility IPV4',
                                                             intentId=installResult,
                                                             onosNode='0',
                                                             host1=host1,
                                                             host2=host2,
                                                             sw1="s6",
                                                             sw2="s2",
                                                             expectedLink=18 )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=testResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.intentFunction.report( main )
