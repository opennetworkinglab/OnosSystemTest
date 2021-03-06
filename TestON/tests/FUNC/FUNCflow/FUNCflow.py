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
class FUNCflow:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        import os
        import imp
        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
        except ImportError:
            main.log.error( "SetUp not found exiting the test" )
            main.cleanAndExit()
        try:
            main.testSetUp
        except ( NameError, AttributeError ):
            main.testSetUp = ONOSSetup()
        """
        - Construct tests variables
        - GIT ( optional )
            - Checkout ONOS master branch
            - Pull latest ONOS code
        """
        main.testSetUp.envSetupDescription()
        stepResult = main.FALSE
        try:
            # Test variables
            main.cellName = main.params[ 'ENV' ][ 'cellName' ]
            main.apps = main.params[ 'ENV' ][ 'cellApps' ]
            main.ONOSport = main.params[ 'CTRL' ][ 'port' ]
            main.dependencyPath = main.testOnDirectory + \
                                  main.params[ 'DEPENDENCY' ][ 'path' ]
            wrapperFile1 = main.params[ 'DEPENDENCY' ][ 'wrapper1' ]
            wrapperFile2 = main.params[ 'DEPENDENCY' ][ 'wrapper2' ]
            main.topology = main.params[ 'DEPENDENCY' ][ 'topology' ]
            main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
            main.startMNSleep = int( main.params[ 'SLEEP' ][ 'startMN' ] )
            main.addFlowSleep = int( main.params[ 'SLEEP' ][ 'addFlow' ] )
            main.delFlowSleep = int( main.params[ 'SLEEP' ][ 'delFlow' ] )
            main.debug = main.params[ 'DEBUG' ]
            main.swDPID = main.params[ 'TEST' ][ 'swDPID' ]
            main.scapyHostNames = main.params[ 'SCAPY' ][ 'HOSTNAMES' ].split( ',' )
            main.scapyHosts = []  # List of scapy hosts for iterating

            main.debug = True if "on" in main.debug else False

            # -- INIT SECTION, ONLY RUNS ONCE -- #

            try:
                from tests.FUNC.FUNCflow.dependencies.checkingFlow import CheckingFlow
                main.checkingFlow = CheckingFlow()
            except ImportError as e:
                print e
                main.log.error( "CheckingFlow not found exiting the test" )
                main.cleanAndExit()
            copyResult = main.ONOSbench.scp( main.Mininet1,
                                             main.dependencyPath + main.topology,
                                             main.Mininet1.home + '/custom/',
                                             direction="to" )

            utilities.assert_equals( expect=main.TRUE,
                                     actual=copyResult,
                                     onpass="Successfully copy " + "test variables ",
                                     onfail="Failed to copy test variables" )

            stepResult = main.testSetUp.envSetup()

        except Exception as e:
            main.testSetUp.envSetupException( e )
        main.testSetUp.envSetupConclusion( stepResult )

    def CASE2( self, main ):
        """
        - Set up cell
            - Create cell file
            - Set cell file
            - Verify cell file
        - Building ONOS
            - Install ONOS package
            - Build ONOS package
        - Kill ONOS process
        - Uninstall ONOS cluster
        - Verify ONOS start up
        - Install ONOS cluster
        - Connect to cli
        """
        main.testSetUp.ONOSSetUp( main.Cluster )

    def CASE10( self, main ):
        """
            Start Mininet
        """
        import json
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

        main.case( "Setup mininet and compare ONOS topology view to Mininet topology" )
        main.caseExplanation = "Start mininet with custom topology and compare topology " +\
                "elements between Mininet and ONOS"

        main.step( "Setup Mininet Topology" )
        topology = main.Mininet1.home + '/custom/' + main.topology
        stepResult = main.Mininet1.startNet( topoFile=topology )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )

        main.step( "Assign switch to controller" )
        stepResult = main.Mininet1.assignSwController( "s1", main.Cluster.active( 0 ).ipAddress )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully assigned switch to controller",
                                 onfail="Failed to assign switch to controller" )

        time.sleep( main.startMNSleep )

        main.topoRelated.compareTopos( main.Mininet1 )

    def CASE11( self, main ):
        """
            Start Scapy with Mininet
        """
        main.case( "Starting scapy with Mininet" )
        main.step( "Creating Host component" )
        scapyResult = main.TRUE
        for hostName in main.scapyHostNames:
            main.Scapy.createHostComponent( hostName )
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

    def CASE12( self, main ):
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
            scapyResult = scapyResult and main.Scapy.removeHostComponent( host.name )
            main.log.info( "Removed Scapy Host Component: {0}".format( host.name ) )

        main.scapyHosts = []

        utilities.assert_equals( expect=main.TRUE,
                                 actual=scapyResult,
                                 onpass="Successfully stopped scapy and removed host components",
                                 onfail="Failed to stop mininet and scapy" )

        mininetResult = main.Utils.mininetCleanup( main.Mininet1 )
        # Exit if topology did not load properly
        if not ( mininetResult and scapyResult ):
            main.cleanAndExit()

    def CASE66( self, main ):
        """
        Testing scapy
        """
        main.case( "Testing scapy" )
        for host in main.scapyHosts:
            host.stopScapy()
            host.startScapy()
            host.updateSelf()
            main.log.debug( host.name )
            main.log.debug( host.hostIp )
            main.log.debug( host.hostMac )

        main.step( "Sending/Receiving Test packet - Filter doesn't match" )
        main.log.info( "Starting Filter..." )
        main.h2.startFilter()
        main.log.info( "Building Ether frame..." )
        main.h1.buildEther( dst=main.h2.hostMac )
        main.log.info( "Sending Packet..." )
        main.h1.sendPacket()
        main.log.info( "Checking Filter..." )
        finished = main.h2.checkFilter()
        main.log.debug( finished )
        i = ""
        if finished:
            a = main.h2.readPackets()
            for i in a.splitlines():
                main.log.info( i )
        else:
            kill = main.h2.killFilter()
            main.log.debug( kill )
            main.h2.handle.sendline( "" )
            main.h2.handle.expect( main.h2.scapyPrompt )
            main.log.debug( main.h2.handle.before )
        utilities.assert_equals( expect=True,
                                 actual="dst=00:00:00:00:00:02 src=00:00:00:00:00:01" in i,
                                 onpass="Pass",
                                 onfail="Fail" )

        main.step( "Sending/Receiving Test packet - Filter matches" )
        main.h2.startFilter()
        main.h1.buildEther( dst=main.h2.hostMac )
        main.h1.buildIP( dst=main.h2.hostIp )
        main.h1.sendPacket()
        finished = main.h2.checkFilter()
        i = ""
        if finished:
            a = main.h2.readPackets()
            for i in a.splitlines():
                main.log.info( i )
        else:
            kill = main.h2.killFilter()
            main.log.debug( kill )
            main.h2.handle.sendline( "" )
            main.h2.handle.expect( main.h2.scapyPrompt )
            main.log.debug( main.h2.handle.before )
        utilities.assert_equals( expect=True,
                                 actual="dst=00:00:00:00:00:02 src=00:00:00:00:00:01" in i,
                                 onpass="Pass",
                                 onfail="Fail" )

    def CASE1000( self, main ):
        """
            Add flows with MAC selectors and verify the flows
        """
        import json
        import time
        ctrl = main.Cluster.active( 0 )
        main.case( "Verify flow MAC selectors are correctly compiled" )
        main.caseExplanation = "Install two flows with only MAC selectors " +\
                "specified, then verify flows are added in ONOS, finally " +\
                "send a packet that only specifies the MAC src and dst."

        main.step( "Add flows with MAC addresses as the only selectors" )
        for host in main.scapyHosts:
            host.stopScapy()
            host.startScapy()
            host.updateSelf()
            main.log.debug( host.name )
            main.log.debug( host.hostIp )
            main.log.debug( host.hostMac )

        # Add a flow that connects host1 on port1 to host2 on port2
        # send output on port2
        # recieve input on port1
        egress = 2
        ingress = 1

        # Add flows that sends packets from port1 to port2 with correct
        # MAC src and dst addresses
        main.log.info( "Adding flow with MAC selectors" )
        stepResult = ctrl.REST.addFlow( deviceId=main.swDPID,
                                        egressPort=egress,
                                        ingressPort=ingress,
                                        ethSrc=main.h1.hostMac,
                                        ethDst=main.h2.hostMac,
                                        debug=main.debug )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully added flows",
                                 onfail="Failed add flows" )

        # Giving ONOS time to add the flows
        time.sleep( main.addFlowSleep )

        main.checkingFlow.checkFlow()

        main.step( "Send a packet to verify the flows are correct" )

        # Specify the src and dst MAC addr
        main.log.info( "Constructing packet" )
        main.h1.buildEther( src=main.h1.hostMac, dst=main.h2.hostMac )

        # Filter for packets with the correct host name. Otherwise,
        # the filter we catch any packet that is sent to host2
        # NOTE: I believe it doesn't matter which host name it is,
        # as long as the src and dst are both specified
        main.log.info( "Starting filter on host2" )
        main.h2.startFilter( pktFilter="ether host %s" % main.h1.hostMac )

        main.log.info( "Sending packet to host2" )
        main.h1.sendPacket()

        main.log.info( "Checking filter for our packet" )
        stepResult = main.h2.checkFilter()
        if stepResult:
            main.log.info( "Packet: %s" % main.h2.readPackets() )
        else:
            main.h2.killFilter()

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully sent a packet",
                                 onfail="Failed to send a packet" )

    def CASE1400( self, main ):
        """
            Add flows with IPv4 selectors and verify the flows
        """
        import json
        import time
        ctrl = main.Cluster.active( 0 )
        main.case( "Verify flow IP selectors are correctly compiled" )
        main.caseExplanation = "Install two flows with only IP selectors " +\
                "specified, then verify flows are added in ONOS, finally " +\
                "send a packet that only specifies the IP src and dst."

        main.step( "Add flows with IPv4 addresses as the only selectors" )
        for host in main.scapyHosts:
            host.stopScapy()
            host.startScapy()
            host.updateSelf()
            main.log.debug( host.name )
            main.log.debug( host.hostIp )
            main.log.debug( host.hostMac )

        # Add a flow that connects host1 on port1 to host2 on port2
        # send output on port2
        # recieve input on port1
        egress = 2
        ingress = 1
        # IPv4 etherType = 0x800
        ethType = main.params[ 'TEST' ][ 'ip4Type' ]

        # Add flows that connects host1 to host2
        main.log.info( "Add flow with port ingress 1 to port egress 2" )
        stepResult = ctrl.REST.addFlow( deviceId=main.swDPID,
                                        egressPort=egress,
                                        ingressPort=ingress,
                                        ethType=ethType,
                                        ipSrc=( "IPV4_SRC", main.h1.hostIp + "/32" ),
                                        ipDst=( "IPV4_DST", main.h2.hostIp + "/32" ),
                                        debug=main.debug )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully added flows",
                                 onfail="Failed add flows" )

        # Giving ONOS time to add the flow
        time.sleep( main.addFlowSleep )

        main.checkingFlow.checkFlow()

        main.step( "Send a packet to verify the flow is correct" )

        main.log.info( "Constructing packet" )
        # No need for the MAC src dst
        main.h1.buildEther( dst=main.h2.hostMac )
        main.h1.buildIP( src=main.h1.hostIp, dst=main.h2.hostIp )

        main.log.info( "Starting filter on host2" )
        # Defaults to ip
        main.h2.startFilter()

        main.log.info( "Sending packet to host2" )
        main.h1.sendPacket()

        main.log.info( "Checking filter for our packet" )
        stepResult = main.h2.checkFilter()
        if stepResult:
            main.log.info( "Packet: %s" % main.h2.readPackets() )
        else:
            main.h2.killFilter()

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully sent a packet",
                                 onfail="Failed to send a packet" )

    def CASE1500( self, main ):
        """
        Add flow with IPv6 selector and verify the flow
        """
        import json
        import time
        main.case( "Verify IPv6 selector is correctly compiled" )
        main.caseExplanation = "Install two flows with only IP selectors " + \
                               "specified, then verify flows are added in ONOS, finally " + \
                               "send a packet that only specifies the IP src and dst."

        main.step( "Add flows with IPv6 addresses as the only selectors" )
        for host in main.scapyHosts:
            host.stopScapy()
            host.startScapy()
            host.updateSelf( IPv6=True )
            main.log.debug( host.name )
            main.log.debug( host.hostIp )
            main.log.debug( host.hostMac )

        # Add a flow that connects host1 on port1 to host2 on port2
        # send output on port2
        # recieve input on port1
        egress = 6
        ingress = 5
        # IPv6 etherType = 0x86DD
        ethType = main.params[ 'TEST' ][ 'ip6Type' ]

        # Add flows that connects host1 to host2
        main.log.info( "Add flow with port ingress 5 to port egress 6" )
        stepResult = ctrl.REST.addFlow( deviceId=main.swDPID,
                                        egressPort=egress,
                                        ingressPort=ingress,
                                        ethType=ethType,
                                        ipSrc=( "IPV6_SRC", main.h5.hostIp + "/128" ),
                                        ipDst=( "IPV6_DST", main.h6.hostIp + "/128" ),
                                        debug=main.debug )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully added flows",
                                 onfail="Failed add flows" )

        # Giving ONOS time to add the flow
        time.sleep( main.addFlowSleep )

        main.checkingFlow.checkFlow()

        main.step( "Send a packet to verify the flow is correct" )

        main.log.info( "Constructing packet" )
        # No need for the MAC src dst
        main.h5.buildEther( dst=main.h6.hostMac )
        main.h5.buildIPv6( src=main.h5.hostIp, dst=main.h6.hostIp )

        main.log.info( "Starting filter on host6" )
        # Defaults to ip
        main.h6.startFilter( pktFilter="ip6" )
        main.log.info( "Sending packet to host6" )
        main.h5.sendPacket()

        main.log.info( "Checking filter for our packet" )
        stepResult = main.h6.checkFilter()
        if stepResult:
            main.log.info( "Packet: %s" % main.h6.readPackets() )
        else:
            main.h6.killFilter()

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully sent a packet",
                                 onfail="Failed to send a packet" )

    def CASE1100( self, main ):
        """
            Add flow with VLAN selector and verify the flow
        """
        import json
        import time

        main.case( "Verify VLAN selector is correctly compiled" )
        main.caseExplanation = "Install one flow with only the VLAN selector " +\
                "specified, then verify the flow is added in ONOS, and finally " +\
                "broadcast a packet with the correct VLAN tag."

        for host in main.scapyHosts:
            host.stopScapy()
            host.startScapy()
            host.updateSelf()
            main.log.debug( host.name )
            main.log.debug( host.hostIp )
            main.log.debug( host.hostMac )

        main.step( "Add a flow with the VLAN tag as the only selector" )

        # Add flows that connects the two vlan hosts h3 and h4
        # Host 3 is on port 3 and host 4 is on port 4
        vlan = main.params[ 'TEST' ][ 'vlan' ]
        egress = 4
        ingress = 3
        # VLAN ethType = 0x8100
        ethType = main.params[ 'TEST' ][ 'vlanType' ]

        # Add only one flow because we don't need a response
        main.log.info( "Add flow with port ingress 1 to port egress 2" )
        stepResult = ctrl.REST.addFlow( deviceId=main.swDPID,
                                        egressPort=egress,
                                        ingressPort=ingress,
                                        ethType=ethType,
                                        vlan=vlan,
                                        debug=main.debug )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully added flow",
                                 onfail="Failed add flows" )

        # Giving ONOS time to add the flows
        time.sleep( main.addFlowSleep )

        main.checkingFlow.checkFlow()

        main.step( "Send a packet to verify the flow are correct" )

        # The receiving interface
        recIface = "{}-eth0.{}".format( main.h4.name, vlan )
        main.log.info( "Starting filter on host2" )
        # Filter is setup to catch any packet on the vlan interface with the correct vlan tag
        main.h4.startFilter( ifaceName=recIface, pktFilter="" )

        # Broadcast the packet on the vlan interface. We only care if the flow forwards
        # the packet with the correct vlan tag, not if the mac addr is correct
        sendIface = "{}-eth0.{}".format( main.h3.name, vlan )
        main.log.info( "Broadcasting the packet with a vlan tag" )
        main.h3.sendPacket( iface=sendIface,
                            packet="Ether()/Dot1Q(vlan={})".format( vlan ) )

        main.log.info( "Checking filter for our packet" )
        stepResult = main.h4.checkFilter()
        if stepResult:
            main.log.info( "Packet: %s" % main.h4.readPackets() )
        else:
            main.h4.killFilter()

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully sent a packet",
                                 onfail="Failed to send a packet" )

    def CASE1300( self, main ):
        """
            Add flows with MPLS selector and verify the flows
        """
        import json
        import time

        main.case( "Verify the MPLS selector is correctly compiled on the flow." )
        main.caseExplanation = "Install one flow with an MPLS selector, " +\
                               "verify the flow is added in ONOS, and finally " +\
                               "send a packet via scapy that has a MPLS label."

        main.step( "Add a flow with a MPLS selector" )
        for host in main.scapyHosts:
            host.stopScapy()
            host.startScapy( main.dependencyPath )
            host.updateSelf()
            main.log.debug( host.name )
            main.log.debug( host.hostIp )
            main.log.debug( host.hostMac )

        ctrl = main.Cluster.active( 0 )

        # ports
        egress = 2
        ingress = 1
        # MPLS etherType
        ethType = main.params[ 'TEST' ][ 'mplsType' ]
        # MPLS label
        mplsLabel = main.params[ 'TEST' ][ 'mpls' ]

        # Add a flow that connects host1 on port1 to host2 on port2
        main.log.info( "Adding flow with MPLS selector" )
        stepResult = ctrl.REST.addFlow( deviceId=main.swDPID,
                                        egressPort=egress,
                                        ingressPort=ingress,
                                        ethType=ethType,
                                        mpls=mplsLabel,
                                        debug=main.debug )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully added flow",
                                 onfail="Failed add flow" )

        # Giving ONOS time to add the flow
        time.sleep( main.addFlowSleep )

        main.step( "Check flow is in the ADDED state" )

        main.log.info( "Get the flows from ONOS" )
        try:
            flows = json.loads( ctrl.REST.flows() )

            stepResult = main.TRUE
            for f in flows:
                if "rest" in f.get( "appId" ):
                    if "ADDED" not in f.get( "state" ):
                        stepResult = main.FALSE
                        main.log.error( "Flow: %s in state: %s" % ( f.get( "id" ), f.get( "state" ) ) )
        except TypeError:
            main.log.error( "No Flows found by the REST API" )
            stepResult = main.FALSE
        except ValueError:
            main.log.error( "Problem getting Flows state from REST API.  Exiting test" )
            main.cleanAndExit()

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="All flows are in the ADDED state",
                                 onfail="All flows are NOT in the ADDED state" )

        main.step( "Check flows are in Mininet's flow table" )

        # get the flow IDs that were added through rest
        main.log.info( "Getting the flow IDs from ONOS" )
        flowIds = [ f.get( "id" ) for f in flows if "rest" in f.get( "appId" ) ]
        # convert the flowIDs to ints then hex and finally back to strings
        flowIds = [ str( hex( int( x ) ) ) for x in flowIds ]
        main.log.info( "ONOS flow IDs: {}".format( flowIds ) )

        stepResult = main.Mininet1.checkFlowId( "s1", flowIds, debug=True )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="All flows are in mininet",
                                 onfail="All flows are NOT in mininet" )

        main.step( "Send a packet to verify the flow is correct" )

        main.log.info( "Starting filter on host2" )
        main.h2.startFilter( pktFilter="mpls" )

        main.log.info( "Constructing packet" )
        main.log.info( "Sending packet to host2" )
        main.h1.sendPacket( packet='Ether()/MPLS(label={})'.format( mplsLabel ) )

        main.log.info( "Checking filter for our packet" )
        stepResult = main.h2.checkFilter()
        if stepResult:
            main.log.info( "Packet: %s" % main.h2.readPackets() )
        else:
            main.h2.killFilter()

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully sent a packet",
                                 onfail="Failed to send a packet" )

    def CASE1700( self, main ):
        """
            Add flows with a TCP selector and verify the flow
        """
        import json
        import time

        main.case( "Verify the TCP selector is correctly compiled on the flow" )
        main.caseExplanation = "Install a flow with only the TCP selector " +\
                "specified, verify the flow is added in ONOS, and finally " +\
                "send a TCP packet to verify the TCP selector is compiled correctly."

        main.step( "Add a flow with a TCP selector" )
        ctrl = main.Cluster.active( 0 )
        for host in main.scapyHosts:
            host.stopScapy()
            host.startScapy()
            host.updateSelf()
            main.log.debug( host.name )
            main.log.debug( host.hostIp )
            main.log.debug( host.hostMac )

        # Add a flow that connects host1 on port1 to host2 on port2
        egress = 2
        ingress = 1
        # IPv4 etherType
        ethType = main.params[ 'TEST' ][ 'ip4Type' ]
        # IP protocol
        ipProto = main.params[ 'TEST' ][ 'tcpProto' ]
        # TCP port destination
        tcpDst = main.params[ 'TEST' ][ 'tcpDst' ]

        main.log.info( "Add a flow that connects host1 on port1 to host2 on port2" )
        stepResult = ctrl.REST.addFlow( deviceId=main.swDPID,
                                        egressPort=egress,
                                        ingressPort=ingress,
                                        ethType=ethType,
                                        ipProto=ipProto,
                                        tcpDst=tcpDst,
                                        debug=main.debug )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully added flows",
                                 onfail="Failed add flows" )

        # Giving ONOS time to add the flow
        time.sleep( main.addFlowSleep )

        main.checkingFlow.checkFlow()

        main.step( "Send a packet to verify the flow is correct" )

        main.log.info( "Constructing packet" )
        # No need for the MAC src dst
        main.h1.buildEther( dst=main.h2.hostMac )
        main.h1.buildIP( dst=main.h2.hostIp )
        main.h1.buildTCP( dport=tcpDst )

        main.log.info( "Starting filter on host2" )
        # Defaults to ip
        main.h2.startFilter( pktFilter="tcp" )

        main.log.info( "Sending packet to host2" )
        main.h1.sendPacket()

        main.log.info( "Checking filter for our packet" )
        stepResult = main.h2.checkFilter()
        if stepResult:
            main.log.info( "Packet: %s" % main.h2.readPackets() )
        else:
            main.h2.killFilter()

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully sent a packet",
                                 onfail="Failed to send a packet" )

    def CASE1600( self, main ):
        """
            Add flows with a UDP selector and verify the flow
        """
        import json
        import time

        main.case( "Verify the UDP selector is correctly compiled on the flow" )
        main.caseExplanation = "Install a flow with only the UDP selector " +\
                "specified, verify the flow is added in ONOS, and finally " +\
                "send a UDP packet to verify the UDP selector is compiled correctly."

        main.step( "Add a flow with a UDP selector" )
        ctrl = main.Cluster.active( 0 )
        for host in main.scapyHosts:
            host.stopScapy()
            host.startScapy()
            host.updateSelf()
            main.log.debug( host.name )
            main.log.debug( host.hostIp )
            main.log.debug( host.hostMac )

        # Add a flow that connects host1 on port1 to host2 on port2
        egress = 2
        ingress = 1
        # IPv4 etherType
        ethType = main.params[ 'TEST' ][ 'ip4Type' ]
        # IP protocol
        ipProto = main.params[ 'TEST' ][ 'udpProto' ]
        # UDP port destination
        udpDst = main.params[ 'TEST' ][ 'udpDst' ]

        main.log.info( "Add a flow that connects host1 on port1 to host2 on port2" )
        stepResult = ctrl.REST.addFlow( deviceId=main.swDPID,
                                            egressPort=egress,
                                            ingressPort=ingress,
                                            ethType=ethType,
                                            ipProto=ipProto,
                                            udpDst=udpDst,
                                            debug=main.debug )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully added flows",
                                 onfail="Failed add flows" )

        # Giving ONOS time to add the flow
        time.sleep( main.addFlowSleep )

        main.checkingFlow.checkFlow()

        main.step( "Send a packet to verify the flow is correct" )

        main.log.info( "Constructing packet" )
        # No need for the MAC src dst
        main.h1.buildEther( dst=main.h2.hostMac )
        main.h1.buildIP( dst=main.h2.hostIp )
        main.h1.buildUDP( dport=udpDst )

        main.log.info( "Starting filter on host2" )
        # Defaults to ip
        main.h2.startFilter( pktFilter="udp" )

        main.log.info( "Sending packet to host2" )
        main.h1.sendPacket()

        main.log.info( "Checking filter for our packet" )
        stepResult = main.h2.checkFilter()
        if stepResult:
            main.log.info( "Packet: %s" % main.h2.readPackets() )
        else:
            main.h2.killFilter()

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully sent a packet",
                                 onfail="Failed to send a packet" )

    def CASE1900( self, main ):
        """
            Add flows with a ICMPv4 selector and verify the flow
        """
        import json
        import time

        main.case( "Verify the ICMPv4 selector is correctly compiled on the flow" )
        main.caseExplanation = "Install a flow with only the ICMPv4 selector " +\
                "specified, verify the flow is added in ONOS, and finally " +\
                "send a IMCPv4 packet to verify the ICMPv4 selector is compiled correctly."

        main.step( "Add a flow with a ICMPv4 selector" )

        for host in main.scapyHosts:
            host.stopScapy()
            host.startScapy()
            host.updateSelf()
            main.log.debug( host.name )
            main.log.debug( host.hostIp )
            main.log.debug( host.hostMac )

        # Add a flow that connects host1 on port1 to host2 on port2
        egress = 2
        ingress = 1
        # IPv4 etherType
        ethType = main.params[ 'TEST' ][ 'ip4Type' ]
        # IP protocol
        ipProto = main.params[ 'TEST' ][ 'icmpProto' ]
        ctrl = main.Cluster.active( 0 )
        main.log.info( "Add a flow that connects host1 on port1 to host2 on port2" )
        stepResult = ctrl.REST.addFlow( deviceId=main.swDPID,
                                        egressPort=egress,
                                        ingressPort=ingress,
                                        ethType=ethType,
                                        ipProto=ipProto,
                                        debug=main.debug )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully added flows",
                                 onfail="Failed add flows" )

        # Giving ONOS time to add the flow
        time.sleep( main.addFlowSleep )

        main.checkingFlow.checkFlow()

        main.step( "Send a packet to verify the flow is correct" )

        main.log.info( "Constructing packet" )
        # No need for the MAC src dst
        main.h1.buildEther( dst=main.h2.hostMac )
        main.h1.buildIP( dst=main.h2.hostIp )
        main.h1.buildICMP()

        main.log.info( "Starting filter on host2" )
        # Defaults to ip
        main.h2.startFilter( pktFilter="icmp" )

        main.log.info( "Sending packet to host2" )
        main.h1.sendPacket()

        main.log.info( "Checking filter for our packet" )
        stepResult = main.h2.checkFilter()
        if stepResult:
            main.log.info( "Packet: %s" % main.h2.readPackets() )
        else:
            main.h2.killFilter()

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully sent a packet",
                                 onfail="Failed to send a packet" )

    def CASE2000( self, main ):
        """
            Add flows with a ICMPv6 selector and verify the flow
        """
        import json
        import time

        main.case( "Verify the ICMPv6 selector is correctly compiled on the flow" )
        main.caseExplanation = "Install a flow with only the ICMPv6 selector " +\
                "specified, verify the flow is added in ONOS, and finally " +\
                "send a IMCPv6 packet to verify the ICMPv6 selector is compiled correctly."

        main.step( "Add a flow with a ICMPv6 selector" )

        for host in main.scapyHosts:
            host.stopScapy()
            host.startScapy()
            host.updateSelf( IPv6=True )
            main.log.debug( host.name )
            main.log.debug( host.hostIp )
            main.log.debug( host.hostMac )

        # Add a flow that connects host1 on port1 to host2 on port2
        egress = 6
        ingress = 5
        # IPv6 etherType
        ethType = main.params[ 'TEST' ][ 'ip6Type' ]
        # IP protocol
        ipProto = main.params[ 'TEST' ][ 'icmp6Proto' ]
        ctrl = main.Cluster.active( 0 )
        main.log.info( "Add a flow that connects host1 on port1 to host2 on port2" )
        stepResult = ctrl.REST.addFlow( deviceId=main.swDPID,
                                        egressPort=egress,
                                        ingressPort=ingress,
                                        ethType=ethType,
                                        ipProto=ipProto,
                                        debug=main.debug )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully added flows",
                                 onfail="Failed add flows" )

        # Giving ONOS time to add the flow
        time.sleep( main.addFlowSleep )

        main.checkingFlow.checkFlow()

        main.step( "Send a packet to verify the flow is correct" )

        main.log.info( "Constructing packet" )
        # No need for the MAC src dst
        main.h5.buildEther( dst=main.h6.hostMac )
        main.h5.buildIPv6( dst=main.h6.hostIp )
        main.h5.buildICMP( ipVersion=6 )

        main.log.info( "Starting filter on host2" )
        # Defaults to ip
        main.h6.startFilter( pktFilter="icmp6" )

        main.log.info( "Sending packet to host2" )
        main.h5.sendPacket()

        main.log.info( "Checking filter for our packet" )
        stepResult = main.h6.checkFilter()
        if stepResult:
            main.log.info( "Packet: %s" % main.h6.readPackets() )
        else:
            main.h6.killFilter()

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully sent a packet",
                                 onfail="Failed to send a packet" )

    def CASE3000( self, main ):
        """
            Delete flow
        """
        import json

        main.case( "Delete flows that were added through rest" )
        main.step( "Deleting flows" )
        ctrl = main.Cluster.active( 0 )
        main.log.info( "Getting flows" )
        try:
            flows = json.loads( ctrl.REST.flows() )

            stepResult = main.TRUE
            for f in flows:
                if "rest" in f.get( "appId" ):
                    if main.debug:
                        main.log.debug( "Flow to be deleted:\n{}".format( ctrl.REST.pprint( f ) ) )
                    stepResult = stepResult and ctrl.REST.removeFlow( f.get( "deviceId" ), f.get( "id" ) )
        except TypeError:
            main.log.error( "No Flows found by the REST API" )
            stepResult = main.FALSE
        except ValueError:
            main.log.error( "Problem getting Flows state from REST API.  Exiting test" )
            main.cleanAndExit()

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully deleting flows",
                                 onfail="Failed to delete flows" )

        time.sleep( main.delFlowSleep )

    def CASE1200( self, main ):
        """
            Add flows with a ARP selector and verify the flow
        """
        import json
        import time

        main.case( "Verify flow IP selectors are correctly compiled" )
        main.caseExplanation = "Install two flows with only IP selectors " + \
                               "specified, then verify flows are added in ONOS, finally " + \
                               "send a packet that only specifies the IP src and dst."

        main.step( "Add flows with ARP addresses as the only selectors" )

        for host in main.scapyHosts:
            host.stopScapy()
            host.startScapy()
            host.updateSelf()
            main.log.debug( host.name )
            main.log.debug( host.hostIp )
            main.log.debug( host.hostMac )

        ctrl = main.Cluster.active( 0 )
        # Add a flow that connects host1 on port1 to host2 on port2
        # send output on port2
        # recieve input on port1
        egress = 2
        ingress = 1
        # ARP etherType = 0x0806
        ethType = main.params[ 'TEST' ][ 'arpType' ]

        # Add flows that connects host1 to host2
        main.log.info( "Add flow with port ingress 1 to port egress 2" )
        stepResult = ctrl.REST.addFlow( deviceId=main.swDPID,
                                        egressPort=egress,
                                        ingressPort=ingress,
                                        ethType=ethType,
                                        priority=40001,
                                        debug=main.debug )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully added flows",
                                 onfail="Failed add flows" )

        # Giving ONOS time to add the flow
        time.sleep( main.addFlowSleep )

        main.checkingFlow.checkFlow()

        main.step( "Send a packet to verify the flow is correct" )

        main.log.info( "Constructing packet" )
        # No need for the MAC src dst
        main.h1.buildEther( src=main.h1.hostMac, dst=main.h2.hostMac )
        main.h1.buildARP( pdst=main.h2.hostIp )

        main.log.info( "Starting filter on host2" )
        # Defaults to ip
        main.h2.startFilter( pktFilter="arp" )

        main.log.info( "Sending packet to host2" )
        main.h1.sendPacket()

        main.log.info( "Checking filter for our packet" )
        stepResult = main.h2.checkFilter()
        if stepResult:
            main.log.info( "Packet: %s" % main.h2.readPackets() )
        else:
            main.h2.killFilter()

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully sent a packet",
                                 onfail="Failed to send a packet" )

    def CASE1800( self, main ):
        """
           Add flows with a SCTP selector and verify the flow
        """
        import json
        import time

        main.case( "Verify the UDP selector is correctly compiled on the flow" )
        main.caseExplanation = "Install a flow with only the UDP selector " + \
                               "specified, verify the flow is added in ONOS, and finally " + \
                               "send a UDP packet to verify the UDP selector is compiled correctly."

        main.step( "Add a flow with a SCTP selector" )

        for host in main.scapyHosts:
            host.stopScapy()
            host.startScapy()
            host.updateSelf()
            main.log.debug( host.name )
            main.log.debug( host.hostIp )
            main.log.debug( host.hostMac )

        # Add a flow that connects host1 on port1 to host2 on port2
        egress = 2
        ingress = 1
        # IPv4 etherType
        ethType = main.params[ 'TEST' ][ 'ip4Type' ]
        # IP protocol
        ipProto = main.params[ 'TEST' ][ 'sctpProto' ]
        ctrl = main.Cluster.active( 0 )
        main.log.info( "Add a flow that connects host1 on port1 to host2 on port2" )
        stepResult = ctrl.REST.addFlow( deviceId=main.swDPID,
                                        egressPort=egress,
                                        ingressPort=ingress,
                                        ethType=ethType,
                                        ipProto=ipProto,
                                        debug=main.debug )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully added flows",
                                 onfail="Failed add flows" )

        # Giving ONOS time to add the flow
        time.sleep( main.addFlowSleep )

        main.checkingFlow.checkFlow()

        main.step( "Send a packet to verify the flow is correct" )

        main.log.info( "Constructing packet" )
        # No need for the MAC src dst
        main.h1.buildEther( dst=main.h2.hostMac )
        main.h1.buildIP( dst=main.h2.hostIp )
        main.h1.buildSCTP()

        main.log.info( "Starting filter on host2" )
        # Defaults to ip
        main.h2.startFilter( pktFilter="sctp" )

        main.log.info( "Sending packet to host2" )
        main.h1.sendPacket()

        main.log.info( "Checking filter for our packet" )
        stepResult = main.h2.checkFilter()
        if stepResult:
            main.log.info( "Packet: %s" % main.h2.readPackets() )
        else:
            main.h2.killFilter()

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully sent a packet",
                                 onfail="Failed to send a packet" )

    def CASE100( self, main ):
        """
            Report errors/warnings/exceptions
        """
        main.log.info( "Error report: \n" )
        main.ONOSbench.logReport( main.Cluster.active( 0 ).ipAddress,
                                  [ "INFO",
                                    "FOLLOWER",
                                    "WARN",
                                    "flow",
                                    "ERROR",
                                    "Except" ],
                                  "s" )
