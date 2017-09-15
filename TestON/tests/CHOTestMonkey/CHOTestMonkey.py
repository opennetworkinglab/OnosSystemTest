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
        Set IPv6 cfg parameters for Neighbor Discovery
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

        try:
            onosPackage = main.params[ 'TEST' ][ 'package' ]
            karafTimeout = main.params[ 'TEST' ][ 'karafCliTimeout' ]
            main.enableIPv6 = main.params[ 'TEST' ][ 'IPv6' ]
            main.enableIPv6 = True if main.enableIPv6 == "on" else False
            main.caseSleep = int( main.params[ 'TEST' ][ 'caseSleep' ] )
            main.onosCell = main.params[ 'ENV' ][ 'cellName' ]
            main.apps = main.params[ 'ENV' ][ 'cellApps' ]
            main.controllers = []

            main.devices = []
            main.links = []
            main.hosts = []
            main.intents = []
            main.enabledEvents = {}
            for eventName in main.params[ 'EVENT' ].keys():
                if main.params[ 'EVENT' ][ eventName ][ 'status' ] == 'on':
                    main.enabledEvents[ int( main.params[ 'EVENT' ][ eventName ][ 'typeIndex' ] ) ] = eventName
            print main.enabledEvents
            main.graph = Graph()
            main.eventScheduler = EventScheduler()
            main.eventGenerator = EventGenerator()
            main.variableLock = Lock()
            main.mininetLock = Lock()
            main.ONOSbenchLock = Lock()
            main.threadID = 0
            main.eventID = 0
            main.caseResult = main.TRUE
            stepResult = main.testSetUp.envSetup()
        except Exception as e:
            main.testSetUp.envSetupException( e )

        main.testSetUp.evnSetupConclusion( stepResult )

        setupResult = main.testSetUp.ONOSSetUp( main.Mininet1, main.Cluster,
                                                cellName=main.onosCell )
        for i in range( 1, main.Cluster.numCtrls + 1 ):
            newController = Controller( i )
            newController.setCLI( main.Cluster.active( i - 1 ).CLI )
            main.controllers.append( newController )

        main.step( "Set IPv6 cfg parameters for Neighbor Discovery" )
        setIPv6CfgSleep = int( main.params[ 'TEST' ][ 'setIPv6CfgSleep' ] )
        if main.enableIPv6:
            time.sleep( setIPv6CfgSleep )
            cfgResult1 = main.controllers[ 0 ].CLI.setCfg( "org.onosproject.net.neighbour.impl.NeighbourResolutionManager",
                                                           "ndpEnabled",
                                                           "true" )
            time.sleep( setIPv6CfgSleep )
            cfgResult2 = main.controllers[ 0 ].CLI.setCfg( "org.onosproject.provider.host.impl.HostLocationProvider",
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

        caseResult = setupResult and cfgResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=caseResult,
                                 onpass="Set up test environment PASS",
                                 onfail="Set up test environment FAIL" )

    def CASE1( self, main ):
        """
        Load Mininet topology and balances all switches
        """
        import re
        import time
        import copy

        main.topoIndex = "topo" + str( main.params[ 'TEST' ][ 'topo' ] )

        main.log.report( "Load Mininet topology and Balance all Mininet switches across controllers" )
        main.log.report( "________________________________________________________________________" )
        main.case( "Assign and Balance all Mininet switches across controllers" )

        main.step( "Start Mininet topology" )
        newTopo = main.params[ 'TOPO' ][ main.topoIndex ][ 'fileName' ]
        mininetDir = main.Mininet1.home + "/custom/"
        topoPath = main.testDir + "/" + main.TEST + "/dependencies/topologies/" + newTopo
        main.ONOSbench.secureCopy( main.Mininet1.user_name, main.Mininet1.ip_address, topoPath, mininetDir, direction="to" )
        topoPath = mininetDir + newTopo
        startStatus = main.Mininet1.startNet( topoFile=topoPath )
        main.mininetSwitches = main.Mininet1.getSwitches()
        main.mininetHosts = main.Mininet1.getHosts()
        main.mininetLinks = main.Mininet1.getLinks( timeout=60 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=startStatus,
                                 onpass="Start Mininet topology test PASS",
                                 onfail="Start Mininet topology test FAIL" )

        main.step( "Assign switches to controllers" )
        switchMastership = main.TRUE
        for switchName in main.mininetSwitches.keys():
            ips = main.Cluster.getIps()
            main.Mininet1.assignSwController( sw=switchName, ip=ips )
            response = main.Mininet1.getSwController( switchName )
            print( "Response is " + str( response ) )
            if re.search( "tcp:" + main.Cluster.active( 0 ).ipAddress, response ):
                switchMastership = switchMastership and main.TRUE
            else:
                switchMastership = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=switchMastership,
                                 onpass="Assign switches to controllers test PASS",
                                 onfail="Assign switches to controllers test FAIL" )
        # Waiting here to make sure topology converges across all nodes
        sleep = int( main.params[ 'TEST' ][ 'loadTopoSleep' ] )
        time.sleep( sleep )

        main.step( "Balance devices across controllers" )
        balanceResult = main.Cluster.active( 0 ).CLI.balanceMasters()
        # giving some breathing time for ONOS to complete re-balance
        time.sleep( sleep )

        caseResult = ( startStatus and switchMastership and balanceResult )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=caseResult,
                                 onpass="Starting new Att topology test PASS",
                                 onfail="Starting new Att topology test FAIL" )

    def CASE2( self, main ):
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
        mininetSwitchNum = len( main.mininetSwitches )
        mininetLinkNum = ( len( main.mininetLinks ) - len( main.mininetHosts ) ) * 2
        if mininetSwitchNum == ONOSDeviceNum and mininetLinkNum == ONOSLinkNum:
            main.step( "Collect and store device data" )
            stepResult = main.TRUE
            dpidToName = {}
            for key, value in main.mininetSwitches.items():
                dpidToName[ 'of:' + str( value[ 'dpid' ] ) ] = key
            devicesRaw = main.Cluster.active( 0 ).CLI.devices()
            devices = json.loads( devicesRaw )
            deviceInitIndex = 0
            for device in devices:
                name = dpidToName[ device[ 'id' ] ]
                newDevice = Device( deviceInitIndex, name, device[ 'id' ] )
                print newDevice
                main.devices.append( newDevice )
                deviceInitIndex += 1
            utilities.assert_equals( expect=main.TRUE,
                                     actual=stepResult,
                                     onpass="Successfully collected and stored device data",
                                     onfail="Failed to collect and store device data" )

            main.step( "Collect and store link data" )
            stepResult = main.TRUE
            linksRaw = main.Cluster.active( 0 ).CLI.links()
            links = json.loads( linksRaw )
            linkInitIndex = 0
            for link in links:
                for device in main.devices:
                    if device.dpid == link[ 'src' ][ 'device' ]:
                        deviceA = device
                    elif device.dpid == link[ 'dst' ][ 'device' ]:
                        deviceB = device
                assert deviceA is not None and deviceB is not None
                newLink = Link( linkInitIndex, deviceA, link[ 'src' ][ 'port' ], deviceB, link[ 'dst' ][ 'port' ] )
                print newLink
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
            main.log.info( "Devices (expected): %s, Links (expected): %s" % ( mininetSwitchNum, mininetLinkNum ) )
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

    def CASE3( self, main ):
        """
        Collect and store host data from ONOS
        """
        import json
        from tests.CHOTestMonkey.dependencies.elements.NetworkElement import Host

        main.log.report( "Collect and store host adta from ONOS" )
        main.log.report( "______________________________________________" )
        main.case( "Use fwd app and pingall to discover all the hosts, then collect and store host data" )

        main.step( "Enable Reactive forwarding" )
        appResult = main.controllers[ 0 ].CLI.activateApp( "org.onosproject.fwd" )
        cfgResult1 = main.TRUE
        cfgResult2 = main.TRUE
        if main.enableIPv6:
            cfgResult1 = main.controllers[ 0 ].CLI.setCfg( "org.onosproject.fwd.ReactiveForwarding", "ipv6Forwarding", "true" )
            cfgResult2 = main.controllers[ 0 ].CLI.setCfg( "org.onosproject.fwd.ReactiveForwarding", "matchIpv6Address", "true" )
        stepResult = appResult and cfgResult1 and cfgResult2
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully enabled reactive forwarding",
                                 onfail="Failed to enable reactive forwarding" )

        main.step( "Discover hosts using pingall" )
        stepResult = main.TRUE
        main.Mininet1.pingall()
        if main.enableIPv6:
            ping6Result = main.Mininet1.pingall( protocol="IPv6" )
        hosts = main.controllers[ 0 ].CLI.hosts()
        hosts = json.loads( hosts )
        if not len( hosts ) == len( main.mininetHosts ):
            stepResult = main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Host discovery PASS",
                                 onfail="Host discovery FAIL" )
        if not stepResult:
            main.log.debug( hosts )
            main.cleanAndExit()

        main.step( "Disable Reactive forwarding" )
        appResult = main.controllers[ 0 ].CLI.deactivateApp( "org.onosproject.fwd" )
        stepResult = appResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully deactivated fwd app",
                                 onfail="Failed to deactivate fwd app" )

        main.step( "Collect and store host data" )
        stepResult = main.TRUE
        macToName = {}
        for key, value in main.mininetHosts.items():
            macToName[ value[ 'interfaces' ][ 0 ][ 'mac' ].upper() ] = key
        dpidToDevice = {}
        for device in main.devices:
            dpidToDevice[ device.dpid ] = device
        hostInitIndex = 0
        for host in hosts:
            name = macToName[ host[ 'mac' ] ]
            dpid = host[ 'locations' ][ 0 ][ 'elementId' ]
            device = dpidToDevice[ dpid ]
            newHost = Host( hostInitIndex,
                            name, host[ 'id' ], host[ 'mac' ],
                            device, host[ 'locations' ][ 0 ][ 'port' ],
                            host[ 'vlan' ], host[ 'ipAddresses' ] )
            print newHost
            main.hosts.append( newHost )
            main.devices[ device.index ].hosts.append( newHost )
            hostInitIndex += 1
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully collected and stored host data",
                                 onfail="Failed to collect and store host data" )

        main.step( "Create one host component for each host and then start host cli" )
        for host in main.hosts:
            main.Mininet1.createHostComponent( host.name )
            hostHandle = getattr( main, host.name )
            main.log.info( "Starting CLI on host " + str( host.name ) )
            startCLIResult = hostHandle.startHostCli()
            host.setHandle( hostHandle )
            stepResult = startCLIResult
            utilities.assert_equals( expect=main.TRUE,
                                     actual=startCLIResult,
                                     onpass="Host CLI started",
                                     onfail="Failed to start host CLI" )

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
        time.sleep( main.caseSleep )

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
        time.sleep( main.caseSleep )

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
        hostIntentNum = 0
        pointIntentNum = 0
        downDeviceNum = 0
        downLinkNum = 0
        flowObj = False
        upControllers = [ 1, 2, 3 ]
        while True:
            events = []
            for i in range( int( main.params[ 'CASE70' ][ 'toggleFlowObj' ] ) ):
                events.append( 'toggle-flowobj' )
            for i in range( int( main.params[ 'CASE70' ][ 'addHostIntentWeight' ] ) ):
                events.append( 'add-host-intent' )
            for i in range( int( main.params[ 'CASE70' ][ 'addPointIntentWeight' ] ) ):
                events.append( 'add-point-intent' )
            for i in range( int( main.params[ 'CASE70' ][ 'linkDownWeight' ] ) ):
                events.append( 'link-down' )
            for i in range( int( main.params[ 'CASE70' ][ 'deviceDownWeight' ] ) ):
                events.append( 'device-down' )
            for i in range( int( pow( hostIntentNum, 1.5 ) / 100 ) ):
                events.append( 'del-host-intent' )
            for i in range( int( pow( pointIntentNum, 1.5 ) / 100 ) ):
                events.append( 'del-point-intent' )
            for i in range( pow( 2, downLinkNum ) - 1 ):
                events.append( 'link-up' )
            for i in range( pow( 5, downDeviceNum ) - 1 ):
                events.append( 'device-up' )
            main.log.debug( events )
            event = random.sample( events, 1 )[ 0 ]
            if event == 'add-host-intent':
                n = random.randint( 5, 50 )
                for i in range( n ):
                    cliIndex = random.sample( upControllers, 1 )[ 0 ]
                    main.eventGenerator.triggerEvent( EventType().APP_INTENT_HOST_ADD, EventScheduleMethod().RUN_BLOCK, 'random', 'random', cliIndex )
                    hostIntentNum += 1
            elif event == 'del-host-intent':
                n = random.randint( 5, hostIntentNum )
                for i in range( n ):
                    cliIndex = random.sample( upControllers, 1 )[ 0 ]
                    main.eventGenerator.triggerEvent( EventType().APP_INTENT_HOST_DEL, EventScheduleMethod().RUN_BLOCK, 'random', 'random', cliIndex )
                    hostIntentNum -= 1
            elif event == 'add-point-intent':
                n = random.randint( 5, 50 )
                for i in range( n ):
                    cliIndex = random.sample( upControllers, 1 )[ 0 ]
                    main.eventGenerator.triggerEvent( EventType().APP_INTENT_POINT_ADD, EventScheduleMethod().RUN_BLOCK, 'random', 'random', cliIndex, 'bidirectional' )
                    pointIntentNum += 2
            elif event == 'del-point-intent':
                n = random.randint( 5, pointIntentNum / 2 )
                for i in range( n ):
                    cliIndex = random.sample( upControllers, 1 )[ 0 ]
                    main.eventGenerator.triggerEvent( EventType().APP_INTENT_POINT_DEL, EventScheduleMethod().RUN_BLOCK, 'random', 'random', cliIndex, 'bidirectional' )
                    pointIntentNum -= 2
            elif event == 'link-down':
                main.eventGenerator.triggerEvent( EventType().NETWORK_LINK_DOWN, EventScheduleMethod().RUN_BLOCK, 'random', 'random' )
                downLinkNum += 1
            elif event == 'link-up':
                main.eventGenerator.triggerEvent( EventType().NETWORK_LINK_UP, EventScheduleMethod().RUN_BLOCK, 'random', 'random' )
                downLinkNum -= 1
            elif event == 'device-down':
                main.eventGenerator.triggerEvent( EventType().NETWORK_DEVICE_DOWN, EventScheduleMethod().RUN_BLOCK, 'random' )
                downDeviceNum += 1
            elif event == 'device-up':
                main.eventGenerator.triggerEvent( EventType().NETWORK_DEVICE_UP, EventScheduleMethod().RUN_BLOCK, 'random' )
                downDeviceNum -= 1
            elif event == 'toggle-flowobj':
                if not flowObj:
                    main.eventGenerator.triggerEvent( EventType().ONOS_SET_FLOWOBJ, EventScheduleMethod().RUN_BLOCK, 'true' )
                else:
                    main.eventGenerator.triggerEvent( EventType().ONOS_SET_FLOWOBJ, EventScheduleMethod().RUN_BLOCK, 'false' )
                flowObj = not flowObj
            else:
                pass
            main.eventGenerator.triggerEvent( EventType().CHECK_TOPO, EventScheduleMethod().RUN_NON_BLOCK )
            main.eventGenerator.triggerEvent( EventType().CHECK_ONOS, EventScheduleMethod().RUN_NON_BLOCK )
            main.eventGenerator.triggerEvent( EventType().CHECK_TRAFFIC, EventScheduleMethod().RUN_NON_BLOCK )
            main.eventGenerator.triggerEvent( EventType().CHECK_FLOW, EventScheduleMethod().RUN_NON_BLOCK )
            main.eventGenerator.triggerEvent( EventType().CHECK_INTENT, EventScheduleMethod().RUN_NON_BLOCK )
            main.eventGenerator.triggerEvent( EventType().CHECK_RAFT_LOG_SIZE, EventScheduleMethod().RUN_NON_BLOCK )
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
            print e
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
