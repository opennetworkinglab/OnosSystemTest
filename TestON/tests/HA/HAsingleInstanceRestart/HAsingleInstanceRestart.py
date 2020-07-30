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
            stepResult = main.testSetUp.envSetup( includeCaseDesc=False )
        except Exception as e:
            main.testSetUp.envSetupException( e )
        main.testSetUp.envSetupConclusion( stepResult )

        cellApps = str( main.params["ENV"]["appString"] )
        cellName = str( main.params["ENV"]["appString"] )
        applyFuncs = [ main.HA.removeKarafConsoleLogging, main.testSetUp.createApplyCell ]
        applyArgs = [ None, [ main.Cluster, True, cellName , cellApps, "", True, main.Cluster.runningNodes[ 0 ].ipAddress ] ]
        try:
            if main.params[ 'topology' ][ 'topoFile' ]:
                main.log.info( 'Skipping start of Mininet in this case, make sure you start it elsewhere' )
            else:
                applyFuncs.append( main.HA.startingMininet )
                applyArgs.append( None )
        except (KeyError, IndexError):
                applyFuncs.append( main.HA.startingMininet )
                applyArgs.append( None )

        main.Cluster.setRunningNode( int( main.params[ 'num_controllers' ] ) )
        ip = main.Cluster.getIps( allNode=True )
        main.testSetUp.ONOSSetUp( main.Cluster, cellName="SingleHA",
                                  extraApply=applyFuncs,
                                  applyArgs=applyArgs,
                                  includeCaseDesc=False )
        main.HA.initialSetUp()

        main.step( 'Set logging levels' )
        logging = True
        try:
            logs = main.params.get( 'ONOS_Logging', False )
            if logs:
                for namespace, level in logs.items():
                    for ctrl in main.Cluster.active():
                        ctrl.CLI.logSet( level, namespace )
        except AttributeError:
            logging = False
        utilities.assert_equals( expect=True, actual=logging,
                                 onpass="Set log levels",
                                 onfail="Failed to set log levels" )

    def CASE2( self, main ):
        """
        Assign devices to controllers
        """
        main.HA.assignDevices( main )

    def CASE102( self, main ):
        """
        Set up Spine-Leaf fabric topology in Mininet
        """
        main.HA.startTopology( main )

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

    def CASE104( self, main ):
        """
        Ping Hosts
        """
        main.case( "Check connectivity" )
        main.step( "Ping between all hosts" )
        pingResult = main.Mininet1.pingall()
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="All Pings Passed",
                                 onfail="Failed to ping between all hosts" )

    def CASE5( self, main ):
        """
        Reading state of ONOS
        """
        main.HA.readingState( main )

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
        main.HA.checkStateAfterEvent( main, afterWhich=0, compareSwitch=True, isRestart=True )

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
                if main.topoMappings:
                    zeroHosts = False
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
                                        if device != main.topoMappings[ str( mac ) ]:
                                            main.log.error( "The attachment device is incorrect for " +
                                                            "host " + str( mac ) +
                                                            ". Expected: " + main.topoMappings[ str( mac ) ] +
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
        main.testSetUp.checkOnosNodes( main.Cluster )
        if not topoResult:
            main.cleanAndExit()

    def CASE9( self, main ):
        """
        Link down
        """
        src = main.params['kill']['linkSrc']
        dst = main.params['kill']['linkDst']
        main.HA.linkDown( main, src, dst )

    def CASE10( self, main ):
        """
        Link up
        """
        src = main.params['kill']['linkSrc']
        dst = main.params['kill']['linkDst']
        main.HA.linkUp( main, src, dst )

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
        Start election app on all onos nodes
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
