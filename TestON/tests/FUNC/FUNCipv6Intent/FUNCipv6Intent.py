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
# Testing the basic intent for ipv6 functionality of ONOS


class FUNCipv6Intent:

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
            main.checkTopoAttempts = int( main.params[ 'SLEEP' ][ 'topoAttempts' ] )
            main.numSwitch = int( main.params[ 'MININET' ][ 'switch' ] )
            main.numLinks = int( main.params[ 'MININET' ][ 'links' ] )
            main.hostsData = {}
            main.assertReturnString = ''  # Assembled assert return string

            # -- INIT SECTION, ONLY RUNS ONCE -- #

            main.intentFunction = imp.load_source( wrapperFile2,
                                                   main.dependencyPath +
                                                   wrapperFile2 +
                                                   ".py" )

            copyResult1 = main.ONOSbench.scp( main.Mininet1,
                                              main.dependencyPath +
                                              main.topology,
                                              main.Mininet1.home,
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
        import time

        main.initialized = main.testSetUp.ONOSSetUp( main.Mininet1, main.Cluster, True )

        main.step( "Checking that ONOS is ready" )

        ready = utilities.retry( main.Cluster.command,
                                  False,
                                  kwargs={ "function": "summary", "contentCheck": True },
                                  sleep=30,
                                  attempts=3 )
        utilities.assert_equals( expect=True, actual=ready,
                                 onpass="ONOS summary command succeded",
                                 onfail="ONOS summary command failed" )
        if not ready:
            main.cleanAndExit()
            main.cleanAndExit()

        main.step( "setup the ipv6NeighbourDiscovery" )
        cfgResult1 = main.Cluster.active( 0 ).CLI.setCfg( "org.onosproject.net.neighbour.impl.NeighbourResolutionManager", "ndpEnabled", "true" )
        cfgResult2 = main.Cluster.active( 0 ).CLI.setCfg( "org.onosproject.provider.host.impl.HostLocationProvider", "requestIpv6ND", "true" )
        cfgResult = cfgResult1 and cfgResult2
        utilities.assert_equals( expect=main.TRUE, actual=cfgResult,
                                 onpass="ipv6NeighborDiscovery cfg is set to true",
                                 onfail="Failed to cfg set ipv6NeighborDiscovery" )

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
            main.cleanAndExit()
            main.cleanAndExit()

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
        for ctrl in main.Cluster.active():
            tempONOSip.append( ctrl.ipAddress )

        assignResult = main.Mininet1.assignSwController( sw=switchList,
                                                         ip=tempONOSip,
                                                         port='6633' )
        if not assignResult:
            main.cleanAndExit()
            main.cleanAndExit()

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

    def CASE13( self, main ):
        """
        Discover all hosts and store its data to a dictionary
        """
        main.case( "Discover all hosts" )

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
        balanceResult = utilities.retry( f=main.Cluster.active( 0 ).CLI.balanceMasters, retValue=main.FALSE, args=[] )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=balanceResult,
                                 onpass="Successfully balanced mastership of switches",
                                 onfail="Failed to balance mastership of switches" )

    def CASE14( self, main ):
        """
            Stop mininet
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
        main.Utils.mininetCleanIntro()
        topoResult = main.Utils.mininetCleanup( main.Mininet1 )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanAndExit()
            main.cleanAndExit()

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
        assert main.Mininet1, "Mininet handle should be named Mininet1"
        assert main.numSwitch, "Placed the total number of switch topology in \
                                main.numSwitch"

        intentLeadersOld = main.Cluster.active( 0 ).CLI.leaderCandidates()

        main.testName = "Host Intents"
        main.case( main.testName + " Test - " + str( main.Cluster.numCtrls ) +
                   " NODE(S) - OF " + main.OFProtocol )
        main.caseExplanation = "This test case tests Host intents using " +\
                                str( main.Cluster.numCtrls ) + " node(s) cluster;\n" +\
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
                                        "between two IPV6 hosts" )

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
                                                     host2Id='00:00:00:00:00:09/-1' )

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
        assert main.Mininet1, "Mininet handle should be named Mininet1"
        assert main.numSwitch, "Placed the total number of switch topology in \
                                main.numSwitch"

        main.testName = "Point Intents"
        main.case( main.testName + " Test - " + str( main.Cluster.numCtrls ) +
                   " NODE(S) - OF " + main.OFProtocol )
        main.caseExplanation = "This test case will test point to point" +\
                               " intents using " + str( main.Cluster.numCtrls ) +\
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
                                       deviceId2="of:0000000000000006/1" )

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
                                       expectedLink="" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )
        main.step( "SDNIP-ICMP: Add point intents between h1 and h9" )
        main.assertReturnString = "Assertion Result for SDNIP-ICMP IPV6 using ICMP point intents\n"
        mac1 = main.hostsData[ 'h1' ][ 'mac' ]
        mac2 = main.hostsData[ 'h9' ][ 'mac' ]
        main.log.debug( mac2 )
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
                                                      deviceId2="of:0000000000000006/1" )
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
        assert main.Mininet1, "Mininet handle should be named Mininet1"
        assert main.numSwitch, "Placed the total number of switch topology in \
                        main.numSwitch"
        main.testName = "Single to Multi Point Intents"
        main.case( main.testName + " Test - " + str( main.Cluster.numCtrls ) + " NODE(S) - OF " + main.OFProtocol )
        main.caseExplanation = "This test case will test single point to" +\
                               " multi point intents using " +\
                               str( main.Cluster.numCtrls ) + " node(s) cluster;\n" +\
                               "Different type of hosts will be tested in " +\
                               "each step such as IPV6, Dual stack, VLAN etc" +\
                               ";\nThe test will use OF " + main.OFProtocol +\
                               " OVS running in Mininet "
        main.step( "NOOPTION: Add single point to multi point intents" )
        hostNames = [ 'h1', 'h9', 'h17' ]
        devices = [ 'of:0000000000000005/1', 'of:0000000000000006/1', 'of:0000000000000007/1' ]
        main.assertReturnString = "Assertion results for IPV6 single to multi point intent with no options set\n"
        stepResult = main.TRUE
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
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )
        main.step( "IPV6: Add single point to multi point intents" )
        main.assertReturnString = "Assertion results for IPV6 single to multi point intent with IPV6 type and MAC addresses\n"
        hostNames = [ 'h1', 'h9', 'h17' ]
        devices = [ 'of:0000000000000005/1', 'of:0000000000000006/1', 'of:0000000000000007/1' ]
        macs = [ '00:00:00:00:00:01', '00:00:00:00:00:09', '00:00:00:00:00:11' ]
        stepResult = main.TRUE
        stepResult = main.intentFunction.singleToMultiIntent(
                                         main,
                                         name="IPV6",
                                         hostNames=hostNames,
                                         devices=devices,
                                         macs=macs,
                                         ethType="IPV6",
                                         sw1="",
                                         sw2="" )
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
                                         sw2="" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )
        main.step( "VLAN: Add single point to multi point intents" )
        main.assertReturnString = "Assertion results for IPV6 single to multi point intent with IPV6 type and MAC addresses in the same VLAN\n"
        hostNames = [ 'h5', 'h24' ]
        devices = [ 'of:0000000000000005/5', 'of:0000000000000007/8' ]
        macs = [ '00:00:00:00:00:05', '00:00:00:00:00:18' ]
        stepResult = main.TRUE
        stepResult = main.intentFunction.singleToMultiIntent(
                                         main,
                                         name="IPV6",
                                         hostNames=hostNames,
                                         devices=devices,
                                         macs=macs,
                                         ethType="IPV6",
                                         sw1="",
                                         sw2="" )
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
        assert main.Mininet1, "Mininet handle should be named Mininet1"
        assert main.numSwitch, "Placed the total number of switch topology in \
                                main.numSwitch"

        main.testName = "Multi To Single Point Intents"
        main.case( main.testName + " Test - " + str( main.Cluster.numCtrls ) +
                   " NODE(S) - OF " + main.OFProtocol )
        main.caseExplanation = "This test case will test single point to" +\
                               " multi point intents using " +\
                               str( main.Cluster.numCtrls ) + " node(s) cluster;\n" +\
                               "Different type of hosts will be tested in " +\
                               "each step such as IPV6, Dual stack, VLAN etc" +\
                               ";\nThe test will use OF " + main.OFProtocol +\
                               " OVS running in Mininet"

        main.step( "NOOPTION: Add multi point to single point intents" )
        main.assertReturnString = "Assertion results for NOOPTION multi to single point intent\n"
        stepResult = main.TRUE
        hostNames = [ 'h17', 'h9' ]
        devices = [ 'of:0000000000000007/1', 'of:0000000000000006/1' ]
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
        macs = [ '00:00:00:00:00:01', '00:00:00:00:00:09', '00:00:00:00:00:11' ]
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
                                         expectedLink="" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass=main.assertReturnString,
                                 onfail=main.assertReturnString )

        main.step( "VLAN: Add multi point to single point intents" )
        main.assertReturnString = "Assertion results for IPV6 multi to single point intent with IPV6 type and no MAC addresses in the same VLAN\n"
        hostNames = [ 'h5', 'h24' ]
        devices = [ 'of:0000000000000005/5', 'of:0000000000000007/8' ]
        macs = [ '00:00:00:00:00:05', '00:00:00:00:00:18' ]
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
                                         expectedLink="" )
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
        assert main.Mininet1, "Mininet handle should be named Mininet1"
        assert main.numSwitch, "Placed the total number of switch topology in \
                                main.numSwitch"
        main.case( "Test host mobility with host intents " )
        main.step( "Testing host mobility by moving h1 from s5 to s6" )
        h1PreMove = main.hostsData[ "h1" ][ "location" ][ 0:19 ]

        main.log.info( "Moving h1 from s5 to s6" )
        main.Mininet1.moveHostv6( "h1", "s5", "s6" )
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
                                                     host2Id='00:00:00:00:00:09/-1' )

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
        macs = [ '00:00:00:00:00:08', '00:00:00:00:00:09', '00:00:00:00:00:11' ]
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
        macs = [ '00:00:00:00:00:05', '00:00:00:00:00:18' ]
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
        macs = [ '00:00:00:00:00:08', '00:00:00:00:00:09', '00:00:00:00:00:11' ]
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
        macs = [ '00:00:00:00:00:05', '00:00:00:00:00:18' ]
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
