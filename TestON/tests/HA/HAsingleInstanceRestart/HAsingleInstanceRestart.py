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
"""
Description: This test is to determine if a single
    instance ONOS 'cluster' can handle a restart

List of test cases:
CASE1: Compile ONOS and push it to the test machines
CASE2: Assign devices to controllers
CASE21: Assign mastership to controllers
CASE3: Assign intents
CASE4: Ping across added host intents
CASE5: Reading state of ONOS
CASE6: The Failure case.
CASE7: Check state after control plane failure
CASE8: Compare topo
CASE9: Link s3-s28 down
CASE10: Link s3-s28 up
CASE11: Switch down
CASE12: Switch up
CASE13: Clean up
CASE14: start election app on all onos nodes
CASE15: Check that Leadership Election is still functional
CASE16: Install Distributed Primitives app
CASE17: Check for basic functionality with distributed primitives
"""
class HAsingleInstanceRestart:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        CASE1 is to compile ONOS and push it to the test machines

        Startup sequence:
        cell <name>
        onos-verify-cell
        NOTE: temporary - onos-remove-raft-logs
        onos-uninstall
        start mininet
        git pull
        mvn clean install
        onos-package
        onos-install -f
        onos-wait-for-start
        start cli sessions
        start tcpdump
        """
        main.log.info( "ONOS Single node cluster restart " +
                         "HA test - initialization" )
        main.case( "Setting up test environment" )
        main.caseExplanation = "Setup the test environment including " +\
                                "installing ONOS, starting Mininet and ONOS" +\
                                "cli sessions."

        # set global variables
        # These are for csv plotting in jenkins
        main.HAlabels = []
        main.HAdata = []
        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
            main.testSetUp = ONOSSetup()
        except ImportError:
            main.log.error( "ONOSSetup not found. exiting the test" )
            main.cleanAndExit()
        main.testSetUp.envSetupDescription()
        try:
            from tests.HA.dependencies.HA import HA
            main.HA = HA()
            # load some variables from the params file
            cellName = main.params[ 'ENV' ][ 'cellName' ]
            main.apps = main.params[ 'ENV' ][ 'appString' ]
            main.numCtrls = int( main.params[ 'num_controllers' ] )
            stepResult = main.testSetUp.envSetup()
        except Exception as e:
            main.testSetUp.envSetupException( e )
        main.testSetUp.evnSetupConclusion( stepResult )
        main.Cluster.setRunningNode( int( main.params[ 'num_controllers' ] ) )
        ip = main.Cluster.getIps( allNode=True )
        main.testSetUp.ONOSSetUp( main.Cluster, cellName="SingleHA", removeLog=True,
                                  extraApply=[ main.testSetUp.createApplyCell,
                                               main.HA.startingMininet,
                                               main.testSetUp.createApplyCell ],
                                  applyArgs=[ [ main.Cluster, True, cellName, main.Mininet1, True, ip ],
                                              None,
                                              [ main.Cluster, True, "SingleHA", main.Mininet1,
                                                True, main.Cluster.runningNodes[ 0 ].ipAddress ] ] )

        main.HA.initialSetUp()

    def CASE2( self, main ):
        """
        Assign devices to controllers
        """
        main.HA.assignDevices( main )

    def CASE21( self, main ):
        """
        Assign mastership to controllers
        """
        main.HA.assignMastership( main )

    def CASE3( self, main ):
        """
        Assign intents
        """
        main.HA.assignIntents( main )

    def CASE4( self, main ):
        """
        Ping across added host intents
        """
        main.HA.pingAcrossHostIntent( main )

    def CASE5( self, main ):
        """
        Reading state of ONOS
        """
        import json
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"

        main.case( "Setting up and gathering data for current state" )
        # The general idea for this test case is to pull the state of
        # ( intents,flows, topology,... ) from each ONOS node
        # We can then compare them with each other and also with past states

        main.step( "Check that each switch has a master" )
        global mastershipState
        mastershipState = '[]'

        # Assert that each device has a master
        main.HA.checkRoleNotNull()

        main.step( "Get the Mastership of each switch" )
        main.HA.checkTheRole()

        main.step( "Get the intents from each controller" )
        global intentState
        intentState = []
        ONOSIntents = main.Cluster.runningNodes[ 0 ].CLI.intents( jsonFormat=True )
        intentCheck = main.FALSE
        if "Error" in ONOSIntents or not ONOSIntents:
            main.log.error( "Error in getting ONOS intents" )
            main.log.warn( "ONOS1 intents response: " + repr( ONOSIntents ) )
        else:
            intentCheck = main.TRUE
        utilities.assert_equals(
            expect=main.TRUE,
            actual=intentCheck,
            onpass="Intents are consistent across all ONOS nodes",
            onfail="ONOS nodes have different views of intents" )

        main.step( "Get the flows from each controller" )
        global flowState
        flowState = []
        flowCheck = main.FALSE
        ONOSFlows = main.Cluster.runningNodes[ 0 ].CLI.flows( jsonFormat=True )
        if "Error" in ONOSFlows or not ONOSFlows:
            main.log.error( "Error in getting ONOS flows" )
            main.log.warn( "ONOS1 flows repsponse: " + ONOSFlows )
        else:
            # TODO: Do a better check, maybe compare flows on switches?
            flowState = ONOSFlows
            flowCheck = main.TRUE

        main.step( "Get the OF Table entries" )
        global flows
        flows = []
        for i in range( 1, 29 ):
            flows.append( main.Mininet1.getFlowTable( "s" + str( i ), version="1.3", debug=False ) )
        if flowCheck == main.FALSE:
            for table in flows:
                main.log.warn( table )
        # TODO: Compare switch flow tables with ONOS flow tables

        main.step( "Collecting topology information from ONOS" )
        devices = []
        devices.append( main.Cluster.runningNodes[ 0 ].CLI.devices() )
        hosts = []
        hosts.append( json.loads( main.Cluster.runningNodes[ 0 ].CLI.hosts() ) )
        ports = []
        ports.append( main.Cluster.runningNodes[ 0 ].CLI.ports() )
        links = []
        links.append( main.Cluster.runningNodes[ 0 ].CLI.links() )
        clusters = []
        clusters.append( main.Cluster.runningNodes[ 0 ].CLI.clusters() )

        main.step( "Each host has an IP address" )
        ipResult = main.TRUE
        for controller in range( 0, len( hosts ) ):
            controllerStr = str( main.Cluster.active( controller ) )
            if hosts[ controller ]:
                for host in hosts[ controller ]:
                    if not host.get( 'ipAddresses', [] ):
                        main.log.error( "Error with host ips on controller" +
                                        controllerStr + ": " + str( host ) )
                        ipResult = main.FALSE
        utilities.assert_equals(
            expect=main.TRUE,
            actual=ipResult,
            onpass="The ips of the hosts aren't empty",
            onfail="The ip of at least one host is missing" )

        # there should always only be one cluster
        main.step( "There is only one dataplane cluster" )
        try:
            numClusters = len( json.loads( clusters[ 0 ] ) )
        except ( ValueError, TypeError ):
            main.log.exception( "Error parsing clusters[0]: " +
                                repr( clusters[ 0 ] ) )
            numClusters = "ERROR"
        utilities.assert_equals(
            expect=1,
            actual=numClusters,
            onpass="ONOS shows 1 SCC",
            onfail="ONOS shows " + str( numClusters ) + " SCCs" )

        main.step( "Comparing ONOS topology to MN" )
        devicesResults = main.TRUE
        linksResults = main.TRUE
        hostsResults = main.TRUE
        mnSwitches = main.Mininet1.getSwitches()
        mnLinks = main.Mininet1.getLinks()
        mnHosts = main.Mininet1.getHosts()
        for controller in main.Cluster.getRunningPos():
            controllerStr = str( main.Cluster.active( controller ) )
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

            if hosts[ controller ] and "Error" not in hosts[ controller ]:
                currentHostsResult = main.Mininet1.compareHosts(
                        mnHosts,
                        hosts[ controller ] )
            else:
                currentHostsResult = main.FALSE
            utilities.assert_equals( expect=main.TRUE,
                                     actual=currentHostsResult,
                                     onpass="ONOS" + controllerStr +
                                     " hosts exist in Mininet",
                                     onfail="ONOS" + controllerStr +
                                     " hosts don't match Mininet" )

            devicesResults = devicesResults and currentDevicesResult
            linksResults = linksResults and currentLinksResult
            hostsResults = hostsResults and currentHostsResult

        main.step( "Device information is correct" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=devicesResults,
            onpass="Device information is correct",
            onfail="Device information is incorrect" )

        main.step( "Links are correct" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=linksResults,
            onpass="Link are correct",
            onfail="Links are incorrect" )

        main.step( "Hosts are correct" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=hostsResults,
            onpass="Hosts are correct",
            onfail="Hosts are incorrect" )

        ONOSMastership, rolesResult, consistentMastership = main.HA.checkTheRole()
        mastershipState = ONOSMastership[ 0 ]

    def CASE6( self, main ):
        """
        The Failure case.
        """
        import time
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"

        main.case( "Restart ONOS node" )
        main.caseExplanation = "Killing ONOS process and restart cli " +\
                                "sessions once onos is up."

        main.step( "Checking ONOS Logs for errors" )
        for ctrl in main.Cluster.active():
            main.log.debug( "Checking logs for errors on " + ctrl.name + ":" )
            main.log.warn( main.ONOSbench.checkLogs( ctrl.ip_address ) )
        ctrl = main.Cluster.runningNodes[ 0 ]
        main.step( "Killing ONOS processes" )
        killResult = main.ONOSbench.onosKill( ctrl.ipAddress )
        start = time.time()
        utilities.assert_equals( expect=main.TRUE, actual=killResult,
                                 onpass="ONOS Killed",
                                 onfail="Error killing ONOS" )

        main.step( "Checking if ONOS is up yet" )
        count = 0
        while count < 10:
            onos1Isup = main.ONOSbench.isup( ctrl.ipAddress )
            if onos1Isup == main.TRUE:
                elapsed = time.time() - start
                break
            else:
                count = count + 1
        utilities.assert_equals( expect=main.TRUE, actual=onos1Isup,
                                 onpass="ONOS is back up",
                                 onfail="ONOS failed to start" )

        main.step( "Starting ONOS CLI sessions" )
        cliResults = ctrl.CLI.startOnosCli( ctrl.ipAddress )
        utilities.assert_equals( expect=main.TRUE, actual=cliResults,
                                 onpass="ONOS cli startup successful",
                                 onfail="ONOS cli startup failed" )

        if elapsed:
            main.log.info( "ESTIMATE: ONOS took %s seconds to restart" %
                           str( elapsed ) )
            main.restartTime = elapsed
        else:
            main.restartTime = -1
        time.sleep( 5 )
        # rerun on election apps
        ctrl.CLI.electionTestRun()

    def CASE7( self, main ):
        """
        Check state after ONOS failure
        """
        import json
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"
        main.case( "Running ONOS Constant State Tests" )

        # Assert that each device has a master
        main.HA.checkRoleNotNull()

        main.step( "Check if switch roles are consistent across all nodes" )
        ONOSMastership, rolesResult, consistentMastership = main.HA.checkTheRole()
        ONOSMastership = ONOSMastership[ 0 ]
        description2 = "Compare switch roles from before failure"
        main.step( description2 )

        currentJson = json.loads( ONOSMastership )
        oldJson = json.loads( mastershipState )
        mastershipCheck = main.TRUE
        for i in range( 1, 29 ):
            switchDPID = str(
                main.Mininet1.getSwitchDPID( switch="s" + str( i ) ) )

            current = [ switch[ 'master' ] for switch in currentJson
                        if switchDPID in switch[ 'id' ] ]
            old = [ switch[ 'master' ] for switch in oldJson
                    if switchDPID in switch[ 'id' ] ]
            if current == old:
                mastershipCheck = mastershipCheck and main.TRUE
            else:
                main.log.warn( "Mastership of switch %s changed; old: %s, new: %s" % ( switchDPID,
                                                                                       old, current ) )
                mastershipCheck = main.FALSE
        utilities.assert_equals(
            expect=main.TRUE,
            actual=mastershipCheck,
            onpass="Mastership of Switches was not changed",
            onfail="Mastership of some switches changed" )
        mastershipCheck = mastershipCheck and consistentMastership

        main.step( "Get the intents and compare across all nodes" )
        ONOSIntents = main.Cluster.runningNodes[ 0 ].CLI.intents( jsonFormat=True )
        intentCheck = main.FALSE
        if "Error" in ONOSIntents or not ONOSIntents:
            main.log.error( "Error in getting ONOS intents" )
            main.log.warn( "ONOS1 intents response: " + repr( ONOSIntents ) )
        else:
            intentCheck = main.TRUE
        utilities.assert_equals(
            expect=main.TRUE,
            actual=intentCheck,
            onpass="Intents are consistent across all ONOS nodes",
            onfail="ONOS nodes have different views of intents" )
        # Print the intent states
        intents = []
        intents.append( ONOSIntents )
        intentStates = []
        for node in intents:  # Iter through ONOS nodes
            nodeStates = []
            # Iter through intents of a node
            for intent in json.loads( node ):
                nodeStates.append( intent[ 'state' ] )
            intentStates.append( nodeStates )
            out = [ ( i, nodeStates.count( i ) ) for i in set( nodeStates ) ]
            main.log.info( dict( out ) )

        # NOTE: Store has no durability, so intents are lost across system
        #       restarts
        main.step( "Get the OF Table entries and compare to before " +
                   "component failure" )
        FlowTables = main.TRUE
        for i in range( 28 ):
            main.log.info( "Checking flow table on s" + str( i + 1 ) )
            tmpFlows = main.Mininet1.getFlowTable( "s" + str( i + 1 ), version="1.3", debug=False )
            curSwitch = main.Mininet1.flowTableComp( flows[ i ], tmpFlows )
            FlowTables = FlowTables and curSwitch
            if curSwitch == main.FALSE:
                main.log.warn( "Differences in flow table for switch: s{}".format( i + 1 ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=FlowTables,
            onpass="No changes were found in the flow tables",
            onfail="Changes were found in the flow tables" )

        main.step( "Leadership Election is still functional" )
        # Test of LeadershipElection

        leader = main.Cluster.runningNodes[ 0 ].ipAddress
        leaderResult = main.TRUE
        for ctrl in main.Cluster.active():
            # loop through ONOScli handlers
            leaderN = ctrl.CLI.electionTestLeader()
            # verify leader is ONOS1
            # NOTE even though we restarted ONOS, it is the only one so onos 1
            # must be leader
            if leaderN == leader:
                # all is well
                pass
            elif leaderN == main.FALSE:
                # error in response
                main.log.error( "Something is wrong with " +
                                 "electionTestLeader function, check the" +
                                 " error logs" )
                leaderResult = main.FALSE
            elif leader != leaderN:
                leaderResult = main.FALSE
                main.log.error( ctrl.name + " sees " +
                                 str( leaderN ) +
                                 " as the leader of the election app. " +
                                 "Leader should be " + str( leader ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=leaderResult,
            onpass="Leadership election passed",
            onfail="Something went wrong with Leadership election" )

    def CASE8( self, main ):
        """
        Compare topo
        """
        import json
        import time
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"

        main.case( "Compare ONOS Topology view to Mininet topology" )
        main.caseExplanation = "Compare topology objects between Mininet" +\
                                " and ONOS"
        topoResult = main.FALSE
        elapsed = 0
        count = 0
        main.step( "Comparing ONOS topology to MN topology" )
        startTime = time.time()
        ctrl = main.Cluster.active( 0 )
        # Give time for Gossip to work
        while topoResult == main.FALSE and ( elapsed < 60 or count < 3 ):
            devicesResults = main.TRUE
            linksResults = main.TRUE
            hostsResults = main.TRUE
            hostAttachmentResults = True
            count += 1
            cliStart = time.time()
            devices = []
            devices.append( ctrl.CLI.devices() )
            hosts = []
            hosts.append( json.loads( ctrl.CLI.hosts() ) )
            ipResult = main.TRUE
            for controller in range( 0, len( hosts ) ):
                controllerStr = str( controller + 1 )
                for host in hosts[ controller ]:
                    if host is None or host.get( 'ipAddresses', [] ) == []:
                        main.log.error(
                            "DEBUG:Error with host ips on controller" +
                            controllerStr + ": " + str( host ) )
                        ipResult = main.FALSE
            ports = []
            ports.append( ctrl.CLI.ports() )
            links = []
            links.append( ctrl.CLI.links() )
            clusters = []
            clusters.append( ctrl.CLI.clusters() )

            elapsed = time.time() - startTime
            cliTime = time.time() - cliStart
            print "CLI time: " + str( cliTime )

            mnSwitches = main.Mininet1.getSwitches()
            mnLinks = main.Mininet1.getLinks()
            mnHosts = main.Mininet1.getHosts()
            for controller in main.Cluster.getRunningPos():
                controllerStr = str( controller )
                if devices[ controller ] and ports[ controller ] and\
                        "Error" not in devices[ controller ] and\
                        "Error" not in ports[ controller ]:

                    try:
                        currentDevicesResult = main.Mininet1.compareSwitches(
                                mnSwitches,
                                json.loads( devices[ controller ] ),
                                json.loads( ports[ controller ] ) )
                    except ( TypeError, ValueError ):
                        main.log.exception( "Object not as expected; devices={!r}\nports={!r}".format(
                            devices[ controller ], ports[ controller ] ) )
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
                            hosts[ controller ] )
                else:
                    currentHostsResult = main.FALSE
                utilities.assert_equals( expect=main.TRUE,
                                         actual=currentHostsResult,
                                         onpass="ONOS" + controllerStr +
                                         " hosts exist in Mininet",
                                         onfail="ONOS" + controllerStr +
                                         " hosts don't match Mininet" )
                # CHECKING HOST ATTACHMENT POINTS
                hostAttachment = True
                zeroHosts = False
                # FIXME: topo-HA/obelisk specific mappings:
                # key is mac and value is dpid
                mappings = {}
                for i in range( 1, 29 ):  # hosts 1 through 28
                    # set up correct variables:
                    macId = "00:" * 5 + hex( i ).split( "0x" )[ 1 ].upper().zfill( 2 )
                    if i == 1:
                        deviceId = "1000".zfill( 16 )
                    elif i == 2:
                        deviceId = "2000".zfill( 16 )
                    elif i == 3:
                        deviceId = "3000".zfill( 16 )
                    elif i == 4:
                        deviceId = "3004".zfill( 16 )
                    elif i == 5:
                        deviceId = "5000".zfill( 16 )
                    elif i == 6:
                        deviceId = "6000".zfill( 16 )
                    elif i == 7:
                        deviceId = "6007".zfill( 16 )
                    elif i >= 8 and i <= 17:
                        dpid = '3' + str( i ).zfill( 3 )
                        deviceId = dpid.zfill( 16 )
                    elif i >= 18 and i <= 27:
                        dpid = '6' + str( i ).zfill( 3 )
                        deviceId = dpid.zfill( 16 )
                    elif i == 28:
                        deviceId = "2800".zfill( 16 )
                    mappings[ macId ] = deviceId
                if hosts[ controller ] or "Error" not in hosts[ controller ]:
                    if hosts[ controller ] == []:
                        main.log.warn( "There are no hosts discovered" )
                        zeroHosts = True
                    else:
                        for host in hosts[ controller ]:
                            mac = None
                            location = None
                            device = None
                            port = None
                            try:
                                mac = host.get( 'mac' )
                                assert mac, "mac field could not be found for this host object"

                                location = host.get( 'locations' )[ 0 ]
                                assert location, "location field could not be found for this host object"

                                # Trim the protocol identifier off deviceId
                                device = str( location.get( 'elementId' ) ).split( ':' )[ 1 ]
                                assert device, "elementId field could not be found for this host location object"

                                port = location.get( 'port' )
                                assert port, "port field could not be found for this host location object"

                                # Now check if this matches where they should be
                                if mac and device and port:
                                    if str( port ) != "1":
                                        main.log.error( "The attachment port is incorrect for " +
                                                        "host " + str( mac ) +
                                                        ". Expected: 1 Actual: " + str( port ) )
                                        hostAttachment = False
                                    if device != mappings[ str( mac ) ]:
                                        main.log.error( "The attachment device is incorrect for " +
                                                        "host " + str( mac ) +
                                                        ". Expected: " + mappings[ str( mac ) ] +
                                                        " Actual: " + device )
                                        hostAttachment = False
                                else:
                                    hostAttachment = False
                            except AssertionError:
                                main.log.exception( "Json object not as expected" )
                                main.log.error( repr( host ) )
                                hostAttachment = False
                else:
                    main.log.error( "No hosts json output or \"Error\"" +
                                    " in output. hosts = " +
                                    repr( hosts[ controller ] ) )
                if zeroHosts is False:
                    hostAttachment = True

                devicesResults = devicesResults and currentDevicesResult
                linksResults = linksResults and currentLinksResult
                hostsResults = hostsResults and currentHostsResult
                hostAttachmentResults = hostAttachmentResults and\
                                        hostAttachment

            # "consistent" results don't make sense for single instance
            # there should always only be one cluster
            clusterResults = main.FALSE
            try:
                numClusters = len( json.loads( clusters[ 0 ] ) )
            except ( ValueError, TypeError ):
                main.log.exception( "Error parsing clusters[0]: " +
                                    repr( clusters[ 0 ] ) )
                numClusters = "ERROR"
                clusterResults = main.FALSE
            if numClusters == 1:
                clusterResults = main.TRUE
            utilities.assert_equals(
                expect=1,
                actual=numClusters,
                onpass="ONOS shows 1 SCC",
                onfail="ONOS shows " + str( numClusters ) + " SCCs" )

            topoResult = ( devicesResults and linksResults
                           and hostsResults and ipResult and clusterResults and
                           hostAttachmentResults )

        topoResult = topoResult and int( count <= 2 )
        note = "note it takes about " + str( int( cliTime ) ) + \
            " seconds for the test to make all the cli calls to fetch " +\
            "the topology from each ONOS instance"
        main.log.info(
            "Very crass estimate for topology discovery/convergence( " +
            str( note ) + " ): " + str( elapsed ) + " seconds, " +
            str( count ) + " tries" )
        utilities.assert_equals( expect=main.TRUE, actual=topoResult,
                                 onpass="Topology Check Test successful",
                                 onfail="Topology Check Test NOT successful" )
        main.step( "Checking ONOS nodes" )
        nodeResults = utilities.retry( main.Cluster.nodesCheck,
                                       False,
                                       attempts=5 )

        utilities.assert_equals( expect=True, actual=nodeResults,
                                 onpass="Nodes check successful",
                                 onfail="Nodes check NOT successful" )
        if not nodeResults:
            for ctrl in main.Cluster.active():
                main.log.debug( "{} components not ACTIVE: \n{}".format(
                    ctrl.name,
                    ctrl.CLI.sendline( "scr:list | grep -v ACTIVE" ) ) )

        if not topoResult:
            main.cleanAndExit()

    def CASE9( self, main ):
        """
        Link s3-s28 down
        """
        main.HA.linkDown( main )

    def CASE10( self, main ):
        """
        Link s3-s28 up
        """
        main.HA.linkUp( main )

    def CASE11( self, main ):
        """
        Switch Down
        """
        # NOTE: You should probably run a topology check after this
        main.HA.switchDown( main )

    def CASE12( self, main ):
        """
        Switch Up
        """
        # NOTE: You should probably run a topology check after this
        main.HA.switchUp( main )

    def CASE13( self, main ):
        """
        Clean up
        """
        main.HAlabels.append( "Restart" )
        main.HAdata.append( str( main.restartTime ) )
        main.HA.cleanUp( main )

    def CASE14( self, main ):
        """
        start election app on all onos nodes
        """
        main.HA.startElectionApp( main )

    def CASE15( self, main ):
        """
        Check that Leadership Election is still functional
            15.1 Run election on each node
            15.2 Check that each node has the same leaders and candidates
            15.3 Find current leader and withdraw
            15.4 Check that a new node was elected leader
            15.5 Check that that new leader was the candidate of old leader
            15.6 Run for election on old leader
            15.7 Check that oldLeader is a candidate, and leader if only 1 node
            15.8 Make sure that the old leader was added to the candidate list

            old and new variable prefixes refer to data from before vs after
                withdrawl and later before withdrawl vs after re-election
        """
        main.HA.isElectionFunctional( main )

    def CASE16( self, main ):
        """
        Install Distributed Primitives app
        """
        main.HA.installDistributedPrimitiveApp( main )

    def CASE17( self, main ):
        """
        Check for basic functionality with distributed primitives
        """
        main.HA.checkDistPrimitivesFunc( main )
