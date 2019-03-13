"""
Copyright 2016 Open Networking Foundation ( ONF )

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
"""
CHOTestMonkey class
Author: you@onlab.us
"""
import sys
import os
import re
import time
import json
import itertools


class CHOTestMonkey:

    def __init__( self ):
        self.default = ''

    def CASE0( self, main ):
        """
        Startup sequence:
        apply cell <name>
        git pull
        onos-package
        onos-verify-cell
        onos-uninstall
        onos-install
        onos-start-cli
        start event scheduler
        start event listener
        """
        import time
        from threading import Lock, Condition
        from core.graph import Graph
        from tests.CHOTestMonkey.dependencies.elements.ONOSElement import Controller
        from tests.CHOTestMonkey.dependencies.EventGenerator import EventGenerator
        from tests.CHOTestMonkey.dependencies.EventScheduler import EventScheduler

        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
            main.testSetUp = ONOSSetup()
        except ImportError:
            main.log.error( "ONOSSetup not found exiting the test" )
            main.cleanAndExit()
        main.testSetUp.envSetupDescription()

        from tests.dependencies.Network import Network
        main.Network = Network()

        try:
            onosPackage = main.params[ 'TEST' ][ 'package' ]
            karafTimeout = main.params[ 'TEST' ][ 'karafCliTimeout' ]
            main.enableIPv6 = main.params[ 'TEST' ][ 'IPv6' ].lower() == "on"
            main.caseSleep = int( main.params[ 'TEST' ][ 'caseSleep' ] )
            main.onosCell = main.params[ 'ENV' ][ 'cellName' ]
            main.apps = main.params[ 'ENV' ][ 'cellApps' ]
            main.restartCluster = main.params[ 'TEST' ][ 'restartCluster' ] == "True"
            main.excludeNodes = main.params[ 'TOPO' ][ 'excludeNodes' ].split( ',' ) \
                                if main.params[ 'TOPO' ][ 'excludeNodes' ] else []
            main.skipSwitches = main.params[ 'CASE70' ][ 'skipSwitches' ].split( ',' ) \
                                if main.params[ 'CASE70' ][ 'skipSwitches' ] else []
            main.skipLinks = main.params[ 'CASE70' ][ 'skipLinks' ].split( ',' ) \
                             if main.params[ 'CASE70' ][ 'skipLinks' ] else []
            main.controllers = []
            main.devices = []
            main.links = []
            main.hosts = []
            main.intents = []
            main.flowObj = False
            main.enabledEvents = {}
            for eventName in main.params[ 'EVENT' ].keys():
                if main.params[ 'EVENT' ][ eventName ][ 'status' ] == 'on':
                    main.enabledEvents[ int( main.params[ 'EVENT' ][ eventName ][ 'typeIndex' ] ) ] = eventName
            main.graph = Graph()
            main.eventScheduler = EventScheduler()
            main.eventGenerator = EventGenerator()
            main.variableLock = Lock()
            main.networkLock = Lock()
            main.ONOSbenchLock = Lock()
            main.threadID = 0
            main.eventID = 0
            main.caseResult = main.TRUE
            stepResult = main.testSetUp.envSetup()
        except Exception as e:
            main.testSetUp.envSetupException( e )

        main.testSetUp.evnSetupConclusion( stepResult )

        setupResult = main.testSetUp.ONOSSetUp( main.Cluster,
                                                cellName=main.onosCell,
                                                restartCluster=main.restartCluster )
        for i in range( 1, main.Cluster.numCtrls + 1 ):
            newController = Controller( i )
            newController.setCLI( main.Cluster.runningNodes[ i - 1 ].CLI )
            main.controllers.append( newController )

        # Set logging levels
        for logLevel in [ 'DEBUG', 'TRACE' ]:
            if main.params[ 'LOGGING' ].get( logLevel ):
                for logger in main.params[ 'LOGGING' ][ logLevel ].split( ',' ):
                    for ctrl in main.Cluster.active():
                        ctrl.CLI.logSet( logLevel, logger )

        main.step( "Start a thread for the scheduler" )
        t = main.Thread( target=main.eventScheduler.startScheduler,
                         threadID=main.threadID,
                         name="startScheduler",
                         args=[] )
        t.start()
        stepResult = main.TRUE
        with main.variableLock:
            main.threadID = main.threadID + 1

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Test step PASS",
                                 onfail="Test step FAIL" )

        main.step( "Start a thread to listen to and handle network, ONOS and application events" )
        t = main.Thread( target=main.eventGenerator.startListener,
                         threadID=main.threadID,
                         name="startListener",
                         args=[] )
        t.start()
        with main.variableLock:
            main.threadID = main.threadID + 1

        caseResult = setupResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=caseResult,
                                 onpass="Set up test environment PASS",
                                 onfail="Set up test environment FAIL" )

    def CASE1( self, main ):
        """
        Set IPv6 cfg parameters for Neighbor Discovery
        """
        main.step( "Set IPv6 cfg parameters for Neighbor Discovery" )
        setIPv6CfgSleep = int( main.params[ 'CASE1' ][ 'setIPv6CfgSleep' ] )
        if main.enableIPv6:
            time.sleep( setIPv6CfgSleep )
            cfgResult1 = main.Cluster.active( 0 ).CLI.setCfg( "org.onosproject.net.neighbour.impl.NeighbourResolutionManager",
                                                              "ndpEnabled",
                                                              "true" )
            time.sleep( setIPv6CfgSleep )
            cfgResult2 = main.Cluster.active( 0 ).CLI.setCfg( "org.onosproject.provider.host.impl.HostLocationProvider",
                                                              "requestIpv6ND",
                                                              "true" )
        else:
            main.log.info( "Skipped setting IPv6 cfg parameters as it is disabled in params file" )
            cfgResult1 = main.TRUE
            cfgResult2 = main.TRUE
        cfgResult = cfgResult1 and cfgResult2
        utilities.assert_equals( expect=main.TRUE,
                                 actual=cfgResult,
                                 onpass="ipv6NeighborDiscovery cfg is set to true",
                                 onfail="Failed to cfg set ipv6NeighborDiscovery" )

    def CASE2( self, main ):
        """
        Load network configuration files
        """
        import json
        main.case( "Load json files for configuring the network" )

        main.step( "Load json files for configuring the network" )
        cfgResult = main.TRUE
        jsonFileName = main.params[ 'CASE2' ][ 'fileName' ]
        jsonFile = main.testDir + "/dependencies/topologies/json/" + jsonFileName
        with open( jsonFile ) as cfg:
            main.Cluster.active( 0 ).REST.setNetCfg( json.load( cfg ) )

        main.step( "Load host files" )
        hostFileName = main.params[ 'CASE2' ][ 'hostFileName' ]
        hostFile = main.testDir + "/dependencies/topologies/host/" + hostFileName
        with open( hostFile ) as cfg:
            main.expectedHosts = json.load( cfg )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=cfgResult,
                                 onpass="Correctly loaded network configurations",
                                 onfail="Failed to load network configurations" )

    def CASE4( self, main ):
        """
        Copy topology lib and config files to Mininet node
        """
        import re
        main.case( "Copy topology lib and config files to Mininet node" )

        copyResult = main.TRUE
        main.step( "Copy topology lib files to Mininet node" )
        for libFileName in main.params[ 'CASE4' ][ 'lib' ].split(","):
            libFile = main.testDir + "/dependencies/topologies/lib/" + libFileName
            copyResult = copyResult and main.ONOSbench.scp( main.Mininet1,
                                                            libFile,
                                                            main.Mininet1.home + "/custom",
                                                            direction="to" )

        main.step( "Copy topology config files to Mininet node" )
        controllerIPs = [ ctrl.ipAddress for ctrl in main.Cluster.runningNodes ]
        index = 0
        for confFileName in main.params[ 'CASE4' ][ 'conf' ].split(","):
            confFile = main.testDir + "/dependencies/topologies/conf/" + confFileName
            # Update zebra configurations with correct ONOS instance IP
            if confFileName in [ "zebradbgp1.conf", "zebradbgp2.conf" ]:
                ip = controllerIPs[ index ]
                index = ( index + 1 ) % len( controllerIPs )
                with open( confFile ) as f:
                    s = f.read()
                s = re.sub( r"(fpm connection ip).*(port 2620)", r"\1 " + ip + r" \2", s )
                with open( confFile, "w" ) as f:
                    f.write( s )
            copyResult = copyResult and main.ONOSbench.scp( main.Mininet1,
                                                            confFile,
                                                            "~/",
                                                            direction="to" )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=copyResult,
                                 onpass="Successfully copied topo lib/conf files",
                                 onfail="Failed to copy topo lib/conf files" )

    def CASE5( self, main ):
        """
        Load Mininet or physical network topology and balances switch mastership
        """
        import time
        import re
        main.log.report( "Load Mininet or physical network topology and Balance switch mastership" )
        main.log.report( "________________________________________________________________________" )
        main.case( "Load Mininet or physical network topology and Balance switch mastership" )

        if hasattr( main, 'Mininet1' ):
            main.step( "Copy Mininet topology files" )
            main.topoIndex = "topo" + str( main.params[ 'TEST' ][ 'topo' ] )
            topoFileName = main.params[ 'TOPO' ][ main.topoIndex ][ 'fileName' ]
            topoFile = main.testDir + "/dependencies/topologies/" + topoFileName
            copyResult = main.ONOSbench.scp( main.Mininet1, topoFile, main.Mininet1.home + "/custom", direction="to" )
            utilities.assert_equals( expect=main.TRUE,
                                     actual=copyResult,
                                     onpass="Successfully copied topo files",
                                     onfail="Failed to copy topo files" )

        main.step( "Load topology" )
        if hasattr( main, 'Mininet1' ):
            topoResult = main.Mininet1.startNet( topoFile=main.Mininet1.home + "/custom/" + topoFileName,
                                                  args=main.params[ 'TOPO' ][ 'mininetArgs' ] )
        else:
            topoResult = main.NetworkBench.connectToNet()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=topoResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanAndExit()

        main.step( "Assign switches to controllers" )
        if hasattr( main, 'Mininet1' ):
            main.networkSwitches = main.Network.getSwitches( excludeNodes=main.excludeNodes )
        else:
            main.networkSwitches = main.Network.getSwitches( excludeNodes=main.excludeNodes,
                                                             includeStopped=True )
        assignResult = main.TRUE
        for name in main.networkSwitches.keys():
            ips = main.Cluster.getIps()
            assignResult = assignResult and main.Network.assignSwController( sw=name, ip=ips )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=assignResult,
                                 onpass="Successfully assign switches to controllers",
                                 onfail="Failed to assign switches to controllers" )

        # Waiting here to make sure topology converges across all nodes
        sleep = int( main.params[ 'TOPO' ][ 'loadTopoSleep' ] )
        time.sleep( sleep )

        main.step( "Balance devices across controllers" )
        balanceResult = main.Cluster.active( 0 ).CLI.balanceMasters()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=balanceResult,
                                 onpass="Successfully balanced mastership",
                                 onfail="Faild to balance mastership" )
        # giving some breathing time for ONOS to complete re-balance
        time.sleep( 5 )

        # Connecting to hosts that only have data plane connectivity
        if hasattr( main, 'NetworkBench' ):
            main.step( "Connecting inband hosts" )
            hostResult = main.NetworkBench.connectInbandHosts()
            utilities.assert_equals( expect=main.TRUE,
                                     actual=hostResult,
                                     onpass="Successfully connected inband hosts",
                                     onfail="Failed to connect inband hosts" )
        else:
            hostResult = main.TRUE

        # Get network hosts and links
        main.networkHosts = main.Network.getHosts()
        if hasattr( main, "expectedHosts" ):
            main.networkHosts = { key: value for key, value in main.networkHosts.items() if key in main.expectedHosts[ "network" ].keys() }
        main.networkLinks = main.Network.getLinks()
        main.networkLinks = [ link for link in main.networkLinks if
                              link[ 'node1' ] in main.networkHosts.keys() + main.networkSwitches.keys() and
                              link[ 'node2' ] in main.networkHosts.keys() + main.networkSwitches.keys() ]

        caseResult = ( topoResult and assignResult and balanceResult and hostResult )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=caseResult,
                                 onpass="Starting new topology test PASS",
                                 onfail="Starting new topology test FAIL" )

    def CASE6( self, main ):
        """
        Collect and store device and link data from ONOS
        """
        import json
        from tests.CHOTestMonkey.dependencies.elements.NetworkElement import Device, Link

        main.log.report( "Collect and Store topology details from ONOS" )
        main.log.report( "____________________________________________________________________" )
        main.case( "Collect and Store Topology Details from ONOS" )

        topoResult = main.TRUE
        topologyOutput = main.Cluster.active( 0 ).CLI.topology()
        topologyResult = main.Cluster.active( 0 ).CLI.getTopology( topologyOutput )
        ONOSDeviceNum = int( topologyResult[ 'devices' ] )
        ONOSLinkNum = int( topologyResult[ 'links' ] )
        networkSwitchNum = len( main.networkSwitches )
        if hasattr( main, 'Mininet1' ):
            networkLinkNum = ( len( main.networkLinks ) - len( main.networkHosts ) ) * 2
        else:
            networkLinkNum = len( main.networkLinks ) * 2
        if networkSwitchNum == ONOSDeviceNum and networkLinkNum == ONOSLinkNum:
            main.step( "Collect and store device data" )
            stepResult = main.TRUE
            dpidToName = {}
            for key, value in main.networkSwitches.items():
                dpidToName[ 'of:' + str( value[ 'dpid' ] ) ] = key
            main.devicesRaw = main.Cluster.active( 0 ).CLI.devices()
            devices = json.loads( main.devicesRaw )
            deviceInitIndex = 0
            for device in devices:
                name = dpidToName[ device[ 'id' ] ]
                newDevice = Device( deviceInitIndex, name, device[ 'id' ] )
                main.log.info( 'New device: {}'.format( newDevice ) )
                main.devices.append( newDevice )
                deviceInitIndex += 1
            utilities.assert_equals( expect=main.TRUE,
                                     actual=stepResult,
                                     onpass="Successfully collected and stored device data",
                                     onfail="Failed to collect and store device data" )

            main.step( "Collect and store link data" )
            stepResult = main.TRUE
            main.linksRaw = main.Cluster.active( 0 ).CLI.links()
            links = json.loads( main.linksRaw )
            linkInitIndex = 0
            for link in links:
                for device in main.devices:
                    if device.dpid == link[ 'src' ][ 'device' ]:
                        deviceA = device
                    elif device.dpid == link[ 'dst' ][ 'device' ]:
                        deviceB = device
                assert deviceA is not None and deviceB is not None
                newLink = Link( linkInitIndex, deviceA, link[ 'src' ][ 'port' ], deviceB, link[ 'dst' ][ 'port' ] )
                main.log.info( 'New link: {}'.format( newLink ) )
                main.links.append( newLink )
                linkInitIndex += 1
            # Set backward links and outgoing links of devices
            for linkA in main.links:
                linkA.deviceA.outgoingLinks.append( linkA )
                if linkA.backwardLink is not None:
                    continue
                for linkB in main.links:
                    if linkB.backwardLink is not None:
                        continue
                    if linkA.deviceA == linkB.deviceB and\
                            linkA.deviceB == linkB.deviceA and\
                            linkA.portA == linkB.portB and\
                            linkA.portB == linkB.portA:
                        linkA.setBackwardLink( linkB )
                        linkB.setBackwardLink( linkA )
            utilities.assert_equals( expect=main.TRUE,
                                     actual=stepResult,
                                     onpass="Successfully collected and stored link data",
                                     onfail="Failed to collect and store link data" )
        else:
            main.log.info( "Devices (expected): %s, Links (expected): %s" % ( networkSwitchNum, networkLinkNum ) )
            main.log.info( "Devices (actual): %s, Links (actual): %s" % ( ONOSDeviceNum, ONOSLinkNum ) )
            topoResult = main.FALSE

        caseResult = topoResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=caseResult,
                                 onpass="Saving ONOS topology data test PASS",
                                 onfail="Saving ONOS topology data test FAIL" )

        if not caseResult:
            main.log.info( "Topology does not match, exiting test..." )
            main.cleanAndExit()

    def CASE7( self, main ):
        """
        Collect and store host data from ONOS
        """
        import json
        from tests.CHOTestMonkey.dependencies.elements.NetworkElement import Host

        main.log.report( "Collect and store host adta from ONOS" )
        main.log.report( "______________________________________________" )
        main.case( "Use fwd app and pingall to discover all the hosts if necessary, then collect and store host data" )

        if main.params[ 'TEST' ][ 'dataPlaneConnectivity' ] == 'False':
            main.step( "Enable Reactive forwarding" )
            appResult = main.Cluster.active( 0 ).CLI.activateApp( "org.onosproject.fwd" )
            cfgResult1 = main.TRUE
            cfgResult2 = main.TRUE
            if main.enableIPv6:
                cfgResult1 = main.Cluster.active( 0 ).CLI.setCfg( "org.onosproject.fwd.ReactiveForwarding", "ipv6Forwarding", "true" )
                cfgResult2 = main.Cluster.active( 0 ).CLI.setCfg( "org.onosproject.fwd.ReactiveForwarding", "matchIpv6Address", "true" )
            stepResult = appResult and cfgResult1 and cfgResult2
            utilities.assert_equals( expect=main.TRUE,
                                     actual=stepResult,
                                     onpass="Successfully enabled reactive forwarding",
                                     onfail="Failed to enable reactive forwarding" )

            main.step( "Discover hosts using pingall" )
            main.Network.pingall()
            if main.enableIPv6:
                ping6Result = main.Network.pingall( protocol="IPv6" )

            main.step( "Disable Reactive forwarding" )
            appResult = main.Cluster.active( 0 ).CLI.deactivateApp( "org.onosproject.fwd" )
            stepResult = appResult
            utilities.assert_equals( expect=main.TRUE,
                                     actual=stepResult,
                                     onpass="Successfully deactivated fwd app",
                                     onfail="Failed to deactivate fwd app" )

        main.step( "Verify host discovery" )
        stepResult = main.TRUE
        main.hostsRaw = main.Cluster.active( 0 ).CLI.hosts()
        hosts = json.loads( main.hostsRaw )
        if hasattr( main, "expectedHosts" ):
            hosts = [ host for host in hosts if host[ 'id' ] in main.expectedHosts[ 'onos' ].keys() ]
        if not len( hosts ) == len( main.networkHosts ):
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Host discovery PASS",
                                 onfail="Host discovery FAIL" )
        if not stepResult:
            main.log.debug( hosts )
            main.cleanAndExit()

        main.step( "Collect and store host data" )
        stepResult = main.TRUE
        macToName = {}
        for key, value in main.networkHosts.items():
            macToName[ value[ 'interfaces' ][ 0 ][ 'mac' ].upper() ] = key
        dpidToDevice = {}
        for device in main.devices:
            dpidToDevice[ device.dpid ] = device
        hostInitIndex = 0
        for host in hosts:
            name = macToName[ host[ 'mac' ] ]
            devices = {}
            for location in host[ 'locations' ]:
                device = dpidToDevice[ location[ 'elementId' ] ]
                devices[ device ] = location[ 'port' ]
            newHost = Host( hostInitIndex,
                            name, host[ 'id' ], host[ 'mac' ],
                            devices,
                            host[ 'vlan' ], host[ 'ipAddresses' ] )
            main.log.info( 'New host: {}'.format( newHost ) )
            main.hosts.append( newHost )
            hostInitIndex += 1
            for location in host[ 'locations' ]:
                device = dpidToDevice[ location[ 'elementId' ] ]
                main.devices[ device.index ].hosts[ newHost ] = location[ 'port' ]

        # Collect IPv4 and IPv6 hosts
        main.ipv4Hosts = []
        main.ipv6Hosts = []
        for host in main.hosts:
            if any( re.match( str( main.params[ 'TEST' ][ 'ipv6Regex' ] ), ipAddress ) for ipAddress in host.ipAddresses ):
                main.ipv6Hosts.append( host )
            if any( re.match( str( main.params[ 'TEST' ][ 'ipv4Regex' ] ), ipAddress ) for ipAddress in host.ipAddresses ):
                main.ipv4Hosts.append( host )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully collected and stored host data",
                                 onfail="Failed to collect and store host data" )

        main.step( "Create one host component for each host and then start host cli" )
        hostResult = main.TRUE
        for host in main.hosts:
            main.Network.createHostComponent( host.name )
            hostHandle = getattr( main, host.name )
            if hasattr( main, "Mininet1" ):
                main.log.info( "Starting CLI on host " + str( host.name ) )
                hostResult = hostResult and hostHandle.startHostCli()
            else:
                main.log.info( "Connecting inband host " + str( host.name ) )
                hostResult = hostResult and hostHandle.connectInband()
            host.setHandle( hostHandle )
            if main.params[ 'TEST' ][ 'dataPlaneConnectivity' ] == 'True':
                # Hosts should already be able to ping each other
                if host in main.ipv4Hosts:
                    host.correspondents += main.ipv4Hosts
                if host in main.ipv6Hosts:
                    host.correspondents += main.ipv6Hosts
        utilities.assert_equals( expect=main.TRUE,
                                 actual=hostResult,
                                 onpass="Host components created",
                                 onfail="Failed to create host components" )

    def CASE10( self, main ):
        """
        Run all enabled checks
        """
        import time
        from tests.CHOTestMonkey.dependencies.events.Event import EventType
        from tests.CHOTestMonkey.dependencies.EventScheduler import EventScheduleMethod

        main.log.report( "Run all enabled checks" )
        main.log.report( "__________________________________________________" )
        main.case( "Run all enabled checks" )
        main.step( "Run all enabled checks" )
        main.caseResult = main.TRUE
        main.eventGenerator.triggerEvent( EventType().CHECK_ALL, EventScheduleMethod().RUN_BLOCK )
        # Wait for the scheduler to become idle before going to the next testcase
        with main.eventScheduler.idleCondition:
            while not main.eventScheduler.isIdle():
                main.eventScheduler.idleCondition.wait()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=main.caseResult,
                                 onpass="All enabled checks passed",
                                 onfail="Not all enabled checks passed" )
        time.sleep( main.caseSleep )

    def CASE20( self, main ):
        """
        Bring down/up links and check topology and ping
        """
        import time
        from tests.CHOTestMonkey.dependencies.events.Event import EventType
        from tests.CHOTestMonkey.dependencies.EventScheduler import EventScheduleMethod

        main.log.report( "Bring down/up links and check topology and ping" )
        main.log.report( "__________________________________________________" )
        main.case( "Bring down/up links and check topology and ping" )
        main.step( "Bring down/up links and check topology and ping" )
        main.caseResult = main.TRUE
        linkToggleNum = int( main.params[ 'CASE20' ][ 'linkToggleNum' ] )
        linkDownUpInterval = int( main.params[ 'CASE20' ][ 'linkDownUpInterval' ] )
        for i in range( 0, linkToggleNum ):
            main.eventGenerator.triggerEvent( EventType().NETWORK_LINK_RANDOM_TOGGLE, EventScheduleMethod().RUN_BLOCK, linkDownUpInterval )
        with main.eventScheduler.idleCondition:
            while not main.eventScheduler.isIdle():
                main.eventScheduler.idleCondition.wait()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=main.caseResult,
                                 onpass="Toggle network links test passed",
                                 onfail="Toggle network links test failed" )
        time.sleep( main.caseSleep )

    def CASE21( self, main ):
        """
        Bring down/up a group of links and check topology and ping
        """
        import time
        from tests.CHOTestMonkey.dependencies.events.Event import EventType
        from tests.CHOTestMonkey.dependencies.EventScheduler import EventScheduleMethod

        main.log.report( "Bring down/up a group of links and check topology and ping" )
        main.log.report( "__________________________________________________" )
        main.case( "Bring down/up a group of links and check topology and ping" )
        main.step( "Bring down/up a group of links and check topology and ping" )
        main.caseResult = main.TRUE
        linkGroupSize = int( main.params[ 'CASE21' ][ 'linkGroupSize' ] )
        linkDownDownInterval = int( main.params[ 'CASE21' ][ 'linkDownDownInterval' ] )
        linkDownUpInterval = int( main.params[ 'CASE21' ][ 'linkDownUpInterval' ] )
        main.eventGenerator.triggerEvent( EventType().NETWORK_LINK_GROUP_RANDOM_TOGGLE, EventScheduleMethod().RUN_BLOCK, linkGroupSize, linkDownDownInterval, linkDownUpInterval )
        with main.eventScheduler.idleCondition:
            while not main.eventScheduler.isIdle():
                main.eventScheduler.idleCondition.wait()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=main.caseResult,
                                 onpass="Toggle network link group test passed",
                                 onfail="Toggle network link group test failed" )
        time.sleep( main.caseSleep )

    def CASE30( self, main ):
        """
        Install host intents and check intent states and ping
        """
        import time
        from tests.CHOTestMonkey.dependencies.events.Event import EventType
        from tests.CHOTestMonkey.dependencies.EventScheduler import EventScheduleMethod

        main.log.report( "Install host intents and check intent states and ping" )
        main.log.report( "__________________________________________________" )
        main.case( "Install host intents and check intent states and ping" )
        main.step( "Install host intents and check intent states and ping" )
        main.caseResult = main.TRUE
        main.eventGenerator.triggerEvent( EventType().APP_INTENT_HOST_ADD_ALL, EventScheduleMethod().RUN_BLOCK )
        with main.eventScheduler.idleCondition:
            while not main.eventScheduler.isIdle():
                main.eventScheduler.idleCondition.wait()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=main.caseResult,
                                 onpass="Install host intents test passed",
                                 onfail="Install host intents test failed" )
        time.sleep( main.caseSleep )

    def CASE31( self, main ):
        """
        Uninstall host intents and check intent states and ping
        """
        import time
        from tests.CHOTestMonkey.dependencies.events.Event import EventType
        from tests.CHOTestMonkey.dependencies.EventScheduler import EventScheduleMethod

        main.log.report( "Uninstall host intents and check intent states and ping" )
        main.log.report( "__________________________________________________" )
        main.case( "Uninstall host intents and check intent states and ping" )
        main.step( "Uninstall host intents and check intent states and ping" )
        main.caseResult = main.TRUE
        main.eventGenerator.triggerEvent( EventType().APP_INTENT_HOST_DEL_ALL, EventScheduleMethod().RUN_BLOCK )
        with main.eventScheduler.idleCondition:
            while not main.eventScheduler.isIdle():
                main.eventScheduler.idleCondition.wait()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=main.caseResult,
                                 onpass="Uninstall host intents test passed",
                                 onfail="Uninstall host intents test failed" )
        time.sleep( main.caseSleep )

    def CASE32( self, main ):
        """
        Install point intents and check intent states and ping
        """
        import time
        from tests.CHOTestMonkey.dependencies.events.Event import EventType
        from tests.CHOTestMonkey.dependencies.EventScheduler import EventScheduleMethod

        main.log.report( "Install point intents and check intent states and ping" )
        main.log.report( "__________________________________________________" )
        main.case( "Install point intents and check intent states and ping" )
        main.step( "Install point intents and check intent states and ping" )
        main.caseResult = main.TRUE
        main.eventGenerator.triggerEvent( EventType().APP_INTENT_POINT_ADD_ALL, EventScheduleMethod().RUN_BLOCK )
        with main.eventScheduler.idleCondition:
            while not main.eventScheduler.isIdle():
                main.eventScheduler.idleCondition.wait()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=main.caseResult,
                                 onpass="Install point intents test passed",
                                 onfail="Install point intents test failed" )
        time.sleep( main.caseSleep )

    def CASE33( self, main ):
        """
        Uninstall point intents and check intent states and ping
        """
        import time
        from tests.CHOTestMonkey.dependencies.events.Event import EventType
        from tests.CHOTestMonkey.dependencies.EventScheduler import EventScheduleMethod

        main.log.report( "Uninstall point intents and check intent states and ping" )
        main.log.report( "__________________________________________________" )
        main.case( "Uninstall point intents and check intent states and ping" )
        main.step( "Uninstall point intents and check intent states and ping" )
        main.caseResult = main.TRUE
        main.eventGenerator.triggerEvent( EventType().APP_INTENT_POINT_DEL_ALL, EventScheduleMethod().RUN_BLOCK )
        with main.eventScheduler.idleCondition:
            while not main.eventScheduler.isIdle():
                main.eventScheduler.idleCondition.wait()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=main.caseResult,
                                 onpass="Uninstall point intents test passed",
                                 onfail="Uninstall point intents test failed" )
        time.sleep( main.caseSleep )

    def CASE40( self, main ):
        """
        Randomly bring down one ONOS node
        """
        import time
        import random
        from tests.CHOTestMonkey.dependencies.events.Event import EventType
        from tests.CHOTestMonkey.dependencies.EventScheduler import EventScheduleMethod

        main.log.report( "Randomly bring down one ONOS node" )
        main.log.report( "__________________________________________________" )
        main.case( "Randomly bring down one ONOS node" )
        main.step( "Randomly bring down one ONOS node" )
        main.caseResult = main.TRUE
        availableControllers = []
        for controller in main.controllers:
            if controller.isUp():
                availableControllers.append( controller.index )
        if len( availableControllers ) == 0:
            main.log.warn( "No available controllers" )
            main.caseResult = main.FALSE
        else:
            index = random.sample( availableControllers, 1 )
            main.eventGenerator.triggerEvent( EventType().ONOS_ONOS_DOWN, EventScheduleMethod().RUN_BLOCK, index[ 0 ] )
            with main.eventScheduler.idleCondition:
                while not main.eventScheduler.isIdle():
                    main.eventScheduler.idleCondition.wait()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=main.caseResult,
                                 onpass="Randomly bring down ONOS test passed",
                                 onfail="Randomly bring down ONOS test failed" )
        time.sleep( int( main.params[ 'CASE40' ][ 'sleepSec' ] ) )

    def CASE41( self, main ):
        """
        Randomly bring up one ONOS node that is down
        """
        import time
        import random
        from tests.CHOTestMonkey.dependencies.events.Event import EventType
        from tests.CHOTestMonkey.dependencies.EventScheduler import EventScheduleMethod

        main.log.report( "Randomly bring up one ONOS node that is down" )
        main.log.report( "__________________________________________________" )
        main.case( "Randomly bring up one ONOS node that is down" )
        main.step( "Randomly bring up one ONOS node that is down" )
        main.caseResult = main.TRUE
        targetControllers = []
        for controller in main.controllers:
            if not controller.isUp():
                targetControllers.append( controller.index )
        if len( targetControllers ) == 0:
            main.log.warn( "All controllers are up" )
            main.caseResult = main.FALSE
        else:
            index = random.sample( targetControllers, 1 )
            main.eventGenerator.triggerEvent( EventType().ONOS_ONOS_UP, EventScheduleMethod().RUN_BLOCK, index[ 0 ] )
            with main.eventScheduler.idleCondition:
                while not main.eventScheduler.isIdle():
                    main.eventScheduler.idleCondition.wait()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=main.caseResult,
                                 onpass="Randomly bring up ONOS test passed",
                                 onfail="Randomly bring up ONOS test failed" )
        time.sleep( int( main.params[ 'CASE41' ][ 'sleepSec' ] ) )

    def CASE50( self, main ):
        """
        Set FlowObjective to True
        """
        import time
        from tests.CHOTestMonkey.dependencies.events.Event import EventType
        from tests.CHOTestMonkey.dependencies.EventScheduler import EventScheduleMethod

        main.log.report( "Set FlowObjective to True" )
        main.log.report( "__________________________________________________" )
        main.case( "Set FlowObjective to True" )
        main.step( "Set FlowObjective to True" )
        main.caseResult = main.TRUE
        main.eventGenerator.triggerEvent( EventType().ONOS_SET_FLOWOBJ, EventScheduleMethod().RUN_BLOCK, 'true' )
        with main.eventScheduler.idleCondition:
            while not main.eventScheduler.isIdle():
                main.eventScheduler.idleCondition.wait()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=main.caseResult,
                                 onpass="Set FlowObjective test passed",
                                 onfail="Set FlowObjective test failed" )
        time.sleep( main.caseSleep )

    def CASE51( self, main ):
        """
        Set FlowObjective to False
        """
        import time
        from tests.CHOTestMonkey.dependencies.events.Event import EventType
        from tests.CHOTestMonkey.dependencies.EventScheduler import EventScheduleMethod

        main.log.report( "Set FlowObjective to False" )
        main.log.report( "__________________________________________________" )
        main.case( "Set FlowObjective to False" )
        main.step( "Set FlowObjective to False" )
        main.caseResult = main.TRUE
        main.eventGenerator.triggerEvent( EventType().ONOS_SET_FLOWOBJ, EventScheduleMethod().RUN_BLOCK, 'false' )
        with main.eventScheduler.idleCondition:
            while not main.eventScheduler.isIdle():
                main.eventScheduler.idleCondition.wait()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=main.caseResult,
                                 onpass="Set FlowObjective test passed",
                                 onfail="Set FlowObjective test failed" )
        time.sleep( main.caseSleep )

    def CASE60( self, main ):
        """
        Balance device masters
        """
        import time
        from tests.CHOTestMonkey.dependencies.events.Event import EventType
        from tests.CHOTestMonkey.dependencies.EventScheduler import EventScheduleMethod

        main.log.report( "Balance device masters" )
        main.log.report( "__________________________________________________" )
        main.case( "Balance device masters" )
        main.step( "Balance device masters" )
        main.caseResult = main.TRUE
        main.eventGenerator.triggerEvent( EventType().ONOS_BALANCE_MASTERS, EventScheduleMethod().RUN_BLOCK )
        with main.eventScheduler.idleCondition:
            while not main.eventScheduler.isIdle():
                main.eventScheduler.idleCondition.wait()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=main.caseResult,
                                 onpass="Balance masters test passed",
                                 onfail="Balance masters test failed" )
        time.sleep( main.caseSleep )

    def CASE70( self, main ):
        """
        Randomly generate events
        """
        import time
        import random
        from tests.CHOTestMonkey.dependencies.events.Event import EventType
        from tests.CHOTestMonkey.dependencies.EventScheduler import EventScheduleMethod

        main.log.report( "Randomly generate events" )
        main.log.report( "__________________________________________________" )
        main.case( "Randomly generate events" )
        main.step( "Randomly generate events" )
        main.caseResult = main.TRUE
        sleepSec = int( main.params[ 'CASE70' ][ 'sleepSec' ] )
        allControllers = range( 1, int( main.params[ 'TEST' ][ 'numCtrl' ] ) + 1 )
        while True:
            upControllers = [ i for i in allControllers if main.controllers[ i - 1 ].isUp() ]
            downControllers = [ i for i in allControllers if i not in upControllers ]
            hostIntentNum = len( [ intent for intent in main.intents if intent.type == 'INTENT_HOST' ] )
            pointIntentNum = len( [ intent for intent in main.intents if intent.type == 'INTENT_POINT' ] )
            downDeviceNum = len( [ device for device in main.devices if device.isDown() or device.isRemoved() ] )
            downLinkNum = len( [ link for link in main.links if link.isDown() ] ) / 2
            downPortNum = sum( [ len( device.downPorts ) for device in main.devices ] )
            events = []
            for event, weight in main.params[ 'CASE70' ][ 'eventWeight' ].items():
                events += [ event ] * int( weight )
            events += [ 'del-host-intent' ] * int( pow( hostIntentNum, 1.5 ) / 100 )
            events += [ 'del-point-intent' ] * int( pow( pointIntentNum, 1.5 ) / 100 )
            events += [ 'device-up' ] * int( pow( 3, downDeviceNum ) - 1 )
            if 'link-down' in main.params[ 'CASE70' ][ 'eventWeight' ].keys():
                events += [ 'link-up' ] * int( pow( 3, downLinkNum ) - 1 )
            if 'port-down' in main.params[ 'CASE70' ][ 'eventWeight' ].keys():
                events += [ 'port-up' ] * int( pow( 3, downPortNum ) - 1 )
            events += [ 'onos-up' ] * int( pow( 3, len( downControllers ) - 1 ) )
            main.log.debug( events )
            event = random.sample( events, 1 )[ 0 ]
            if event == 'add-host-intent':
                n = random.randint( 5, 50 )
                for i in range( n ):
                    cliIndex = random.sample( upControllers, 1 )[ 0 ]
                    main.eventGenerator.triggerEvent( EventType().APP_INTENT_HOST_ADD, EventScheduleMethod().RUN_BLOCK, 'random', 'random', cliIndex )
            elif event == 'del-host-intent':
                n = random.randint( 5, hostIntentNum )
                for i in range( n ):
                    cliIndex = random.sample( upControllers, 1 )[ 0 ]
                    main.eventGenerator.triggerEvent( EventType().APP_INTENT_HOST_DEL, EventScheduleMethod().RUN_BLOCK, 'random', 'random', cliIndex )
            elif event == 'add-point-intent':
                n = random.randint( 5, 50 )
                for i in range( n ):
                    cliIndex = random.sample( upControllers, 1 )[ 0 ]
                    main.eventGenerator.triggerEvent( EventType().APP_INTENT_POINT_ADD, EventScheduleMethod().RUN_BLOCK, 'random', 'random', cliIndex, 'bidirectional' )
            elif event == 'del-point-intent':
                n = random.randint( 5, pointIntentNum / 2 )
                for i in range( n ):
                    cliIndex = random.sample( upControllers, 1 )[ 0 ]
                    main.eventGenerator.triggerEvent( EventType().APP_INTENT_POINT_DEL, EventScheduleMethod().RUN_BLOCK, 'random', 'random', cliIndex, 'bidirectional' )
            elif event == 'link-down':
                main.eventGenerator.triggerEvent( EventType().NETWORK_LINK_DOWN, EventScheduleMethod().RUN_BLOCK, 'random', 'random' )
            elif event == 'link-up':
                main.eventGenerator.triggerEvent( EventType().NETWORK_LINK_UP, EventScheduleMethod().RUN_BLOCK, 'random', 'random' )
            elif event == 'device-down':
                main.eventGenerator.triggerEvent( EventType().NETWORK_DEVICE_DOWN, EventScheduleMethod().RUN_BLOCK, 'random' )
            elif event == 'device-up':
                main.eventGenerator.triggerEvent( EventType().NETWORK_DEVICE_UP, EventScheduleMethod().RUN_BLOCK, 'random' )
            elif event == 'port-down':
                main.eventGenerator.triggerEvent( EventType().NETWORK_PORT_DOWN, EventScheduleMethod().RUN_BLOCK, 'random', 'random' )
            elif event == 'port-up':
                main.eventGenerator.triggerEvent( EventType().NETWORK_PORT_UP, EventScheduleMethod().RUN_BLOCK, 'random', 'random' )
            elif event == 'onos-down' and len( downControllers ) == 0:
                onosIndex = random.sample( upControllers, 1 )[ 0 ]
                main.eventGenerator.triggerEvent( EventType().ONOS_ONOS_DOWN, EventScheduleMethod().RUN_BLOCK, onosIndex )
            elif event == 'onos-up' and len( downControllers ) > 0:
                main.eventGenerator.triggerEvent( EventType().ONOS_ONOS_UP, EventScheduleMethod().RUN_BLOCK, downControllers[ 0 ] )
                main.eventGenerator.triggerEvent( EventType().ONOS_BALANCE_MASTERS, EventScheduleMethod().RUN_BLOCK )
            elif event == 'toggle-flowobj':
                main.eventGenerator.triggerEvent( EventType().ONOS_SET_FLOWOBJ, EventScheduleMethod().RUN_BLOCK, 'false' if main.flowObj else 'true' )
            else:
                pass
            main.eventGenerator.triggerEvent( EventType().CHECK_ALL, EventScheduleMethod().RUN_NON_BLOCK )
            with main.eventScheduler.idleCondition:
                while not main.eventScheduler.isIdle():
                    main.eventScheduler.idleCondition.wait()
            time.sleep( sleepSec )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=main.caseResult,
                                 onpass="Randomly generate events test passed",
                                 onfail="Randomly generate events test failed" )
        time.sleep( main.caseSleep )

    def CASE80( self, main ):
        """
        Replay events from log file
        """
        import time
        from tests.CHOTestMonkey.dependencies.events.Event import EventType
        from tests.CHOTestMonkey.dependencies.EventScheduler import EventScheduleMethod

        main.log.report( "Replay events from log file" )
        main.log.report( "__________________________________________________" )
        main.case( "Replay events from log file" )
        main.step( "Replay events from log file" )
        main.caseResult = main.TRUE
        try:
            f = open( main.params[ 'CASE80' ][ 'filePath' ], 'r' )
            for line in f.readlines():
                if 'CHOTestMonkey' in line and 'Event recorded' in line:
                    line = line.split()
                    eventIndex = int( line[ 9 ] )
                    eventName = line[ 10 ]
                    args = line[ 11: ]
                    assert eventName.startswith( 'CHECK' )\
                        or eventName.startswith( 'NETWORK' )\
                        or eventName.startswith( 'APP' )\
                        or eventName.startswith( 'ONOS' )
                    if main.params[ 'CASE80' ][ 'skipChecks' ] == 'on' and eventName.startswith( 'CHECK' ):
                        continue
                    with main.eventScheduler.idleCondition:
                        while not main.eventScheduler.isIdle():
                            main.eventScheduler.idleCondition.wait()
                    main.eventGenerator.triggerEvent( eventIndex, EventScheduleMethod().RUN_BLOCK, *args )
                    time.sleep( float( main.params[ 'CASE80' ][ 'sleepTime' ] ) )
        except Exception as e:
            main.log.error( "Uncaught exception: {}".format( e ) )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=main.caseResult,
                                 onpass="Replay from log file passed",
                                 onfail="Replay from log file failed" )

    def CASE90( self, main ):
        """
        Sleep for some time
        """
        import time
        from tests.CHOTestMonkey.dependencies.events.Event import EventType
        from tests.CHOTestMonkey.dependencies.EventScheduler import EventScheduleMethod

        main.log.report( "Sleep for some time" )
        main.log.report( "__________________________________________________" )
        main.case( "Sleep for some time" )
        main.step( "Sleep for some time" )
        main.caseResult = main.TRUE
        sleepSec = int( main.params[ 'CASE90' ][ 'sleepSec' ] )
        main.eventGenerator.triggerEvent( EventType().TEST_SLEEP, EventScheduleMethod().RUN_BLOCK, sleepSec )
        with main.eventScheduler.idleCondition:
            while not main.eventScheduler.isIdle():
                main.eventScheduler.idleCondition.wait()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=main.caseResult,
                                 onpass="Sleep test passed",
                                 onfail="Sleep test failed" )
        time.sleep( main.caseSleep )

    def CASE100( self, main ):
        """
        Do something else?
        """
        import time

        main.log.report( "Do something else?" )
        main.log.report( "__________________________________________________" )
        main.case( "..." )

        main.step( "Wait until the test stops" )

        main.caseResult = main.TRUE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=main.caseResult,
                                 onpass="Test PASS",
                                 onfail="Test FAIL" )

        testDuration = int( main.params[ 'TEST' ][ 'testDuration' ] )
        time.sleep( testDuration )
