"""
Description: This test is to determine if a single
    instance ONOS 'cluster' can handle a restart

List of test cases:
CASE1: Compile ONOS and push it to the test machines
CASE2: Assign mastership to controllers
CASE3: Assign intents
CASE4: Ping across added host intents
CASE5: Reading state of ONOS
CASE6: The Failure case. Since this is the Sanity test, we do nothing.
CASE7: Check state after control plane failure
CASE8: Compare topo
CASE9: Link s3-s28 down
CASE10: Link s3-s28 up
CASE11: Switch down
CASE12: Switch up
CASE13: Clean up
CASE14: start election app on all onos nodes
CASE15: Check that Leadership Election is still functional
"""


class HATestSingleInstanceRestart:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        CASE1 is to compile ONOS and push it to the test machines

        Startup sequence:
        git pull
        mvn clean install
        onos-package
        cell <name>
        onos-verify-cell
        NOTE: temporary - onos-remove-raft-logs
        onos-install -f
        onos-wait-for-start
        """
        main.log.report( "ONOS Single node cluster restart " +
                         "HA test - initialization" )
        main.case( "Setting up test environment" )
        # TODO: save all the timers and output them for plotting

        # load some vairables from the params file
        PULLCODE = False
        if main.params[ 'Git' ] == 'True':
            PULLCODE = True
        gitBranch = main.params[ 'branch' ]
        cellName = main.params[ 'ENV' ][ 'cellName' ]

        # set global variables
        global ONOS1Ip
        global ONOS1Port
        global ONOS2Ip
        global ONOS2Port
        global ONOS3Ip
        global ONOS3Port
        global ONOS4Ip
        global ONOS4Port
        global ONOS5Ip
        global ONOS5Port
        global ONOS6Ip
        global ONOS6Port
        global ONOS7Ip
        global ONOS7Port
        global numControllers

        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS1Port = main.params[ 'CTRL' ][ 'port1' ]
        ONOS2Ip = main.params[ 'CTRL' ][ 'ip2' ]
        ONOS2Port = main.params[ 'CTRL' ][ 'port2' ]
        ONOS3Ip = main.params[ 'CTRL' ][ 'ip3' ]
        ONOS3Port = main.params[ 'CTRL' ][ 'port3' ]
        ONOS4Ip = main.params[ 'CTRL' ][ 'ip4' ]
        ONOS4Port = main.params[ 'CTRL' ][ 'port4' ]
        ONOS5Ip = main.params[ 'CTRL' ][ 'ip5' ]
        ONOS5Port = main.params[ 'CTRL' ][ 'port5' ]
        ONOS6Ip = main.params[ 'CTRL' ][ 'ip6' ]
        ONOS6Port = main.params[ 'CTRL' ][ 'port6' ]
        ONOS7Ip = main.params[ 'CTRL' ][ 'ip7' ]
        ONOS7Port = main.params[ 'CTRL' ][ 'port7' ]
        numControllers = int( main.params[ 'num_controllers' ] )

        main.step( "Applying cell variable to environment" )
        cellResult = main.ONOSbench.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()

        # FIXME:this is short term fix
        main.log.report( "Removing raft logs" )
        main.ONOSbench.onosRemoveRaftLogs()
        main.log.report( "Uninstalling ONOS" )
        main.ONOSbench.onosUninstall( ONOS1Ip )
        main.ONOSbench.onosUninstall( ONOS2Ip )
        main.ONOSbench.onosUninstall( ONOS3Ip )
        main.ONOSbench.onosUninstall( ONOS4Ip )
        main.ONOSbench.onosUninstall( ONOS5Ip )
        main.ONOSbench.onosUninstall( ONOS6Ip )
        main.ONOSbench.onosUninstall( ONOS7Ip )

        cleanInstallResult = main.TRUE
        gitPullResult = main.TRUE

        main.step( "Compiling the latest version of ONOS" )
        if PULLCODE:
            # TODO Configure branch in params
            main.step( "Git checkout and pull master" )
            main.ONOSbench.gitCheckout( gitBranch )
            gitPullResult = main.ONOSbench.gitPull()

            main.step( "Using mvn clean & install" )
            cleanInstallResult = main.ONOSbench.cleanInstall()
        else:
            main.log.warn( "Did not pull new code so skipping mvn " +
                           "clean install" )
        main.ONOSbench.getVersion( report=True )

        cellResult = main.ONOSbench.setCell( "SingleHA" )
        verifyResult = main.ONOSbench.verifyCell()
        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()

        main.step( "Installing ONOS package" )
        onos1InstallResult = main.ONOSbench.onosInstall( options="-f",
                                                           node=ONOS1Ip )

        main.step( "Checking if ONOS is up yet" )
        # TODO check bundle:list?
        for i in range( 2 ):
            onos1Isup = main.ONOSbench.isup( ONOS1Ip )
            if onos1Isup:
                break
        if not onos1Isup:
            main.log.report( "ONOS1 didn't start!" )

        cliResult = main.ONOScli1.startOnosCli( ONOS1Ip )

        main.step( "Start Packet Capture MN" )
        main.Mininet2.startTcpdump(
            str( main.params[ 'MNtcpdump' ][ 'folder' ] ) + str( main.TEST )
            + "-MN.pcap",
            intf=main.params[ 'MNtcpdump' ][ 'intf' ],
            port=main.params[ 'MNtcpdump' ][ 'port' ] )

        case1Result = ( cleanInstallResult and packageResult and
                        cellResult and verifyResult and onos1InstallResult
                        and onos1Isup and cliResult )

        utilities.assert_equals( expect=main.TRUE, actual=case1Result,
                                onpass="Test startup successful",
                                onfail="Test startup NOT successful" )

        if case1Result == main.FALSE:
            main.cleanup()
            main.exit()

    def CASE2( self, main ):
        """
        Assign mastership to controllers
        """
        import re

        main.log.report( "Assigning switches to controllers" )
        main.case( "Assigning Controllers" )
        main.step( "Assign switches to controllers" )

        for i in range( 1, 29 ):
            main.Mininet1.assignSwController(
                sw=str( i ),
                ip1=ONOS1Ip, port1=ONOS1Port )

        mastershipCheck = main.TRUE
        for i in range( 1, 29 ):
            response = main.Mininet1.getSwController( "s" + str( i ) )
            try:
                main.log.info( str( response ) )
            except:
                main.log.info( repr( response ) )
            if re.search( "tcp:" + ONOS1Ip, response ):
                mastershipCheck = mastershipCheck and main.TRUE
            else:
                mastershipCheck = main.FALSE
        if mastershipCheck == main.TRUE:
            main.log.report( "Switch mastership assigned correctly" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=mastershipCheck,
            onpass="Switch mastership assigned correctly",
            onfail="Switches not assigned correctly to controllers" )

    def CASE3( self, main ):
        """
        Assign intents
        """
        # FIXME: we must reinstall intents until we have a persistant
        # datastore!
        import time
        main.log.report( "Adding host intents" )
        main.case( "Adding host Intents" )

        main.step( "Discovering  Hosts( Via pingall for now )" )
        # FIXME: Once we have a host discovery mechanism, use that instead

        # install onos-app-fwd
        main.log.info( "Install reactive forwarding app" )
        main.ONOScli1.featureInstall( "onos-app-fwd" )

        # REACTIVE FWD test
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall()
        utilities.assert_equals(
            expect=main.TRUE,
            actual=pingResult,
            onpass="Reactive Pingall test passed",
            onfail="Reactive Pingall failed, one or more ping pairs failed" )
        time2 = time.time()
        main.log.info( "Time for pingall: %2f seconds" % ( time2 - time1 ) )

        # uninstall onos-app-fwd
        main.log.info( "Uninstall reactive forwarding app" )
        main.ONOScli1.featureUninstall( "onos-app-fwd" )
        # timeout for fwd flows
        time.sleep( 10 )

        main.step( "Add  host intents" )
        # TODO:  move the host numbers to params
        intentAddResult = True
        for i in range( 8, 18 ):
            main.log.info( "Adding host intent between h" + str( i ) +
                           " and h" + str( i + 10 ) )
            host1 = "00:00:00:00:00:" + \
                str( hex( i )[ 2: ] ).zfill( 2 ).upper()
            host2 = "00:00:00:00:00:" + \
                str( hex( i + 10 )[ 2: ] ).zfill( 2 ).upper()
            host1Id = main.ONOScli1.getHost( host1 )[ 'id' ]
            host2Id = main.ONOScli1.getHost( host2 )[ 'id' ]
            # NOTE: get host can return None
            if host1Id and host2Id:
                tmpResult = main.ONOScli1.addHostIntent(
                    host1Id,
                    host2Id )
            else:
                main.log.error( "Error, getHost() failed" )
                tmpResult = main.FALSE
            intentAddResult = bool( pingResult and intentAddResult
                                     and tmpResult )
            # TODO Check that intents were added?
        utilities.assert_equals(
            expect=True,
            actual=intentAddResult,
            onpass="Pushed host intents to ONOS",
            onfail="Error in pushing host intents to ONOS" )
        # TODO Check if intents all exist in datastore

    def CASE4( self, main ):
        """
        Ping across added host intents
        """
        description = " Ping across added host intents"
        main.log.report( description )
        main.case( description )
        PingResult = main.TRUE
        for i in range( 8, 18 ):
            ping = main.Mininet1.pingHost(
                src="h" + str( i ), target="h" + str( i + 10 ) )
            PingResult = PingResult and ping
            if ping == main.FALSE:
                main.log.warn( "Ping failed between h" + str( i ) +
                               " and h" + str( i + 10 ) )
            elif ping == main.TRUE:
                main.log.info( "Ping test passed!" )
                PingResult = main.TRUE
        if PingResult == main.FALSE:
            main.log.report(
                "Intents have not been installed correctly, pings failed." )
            #TODO: pretty print
            main.log.warn( "ONSO1 intents: " )
            main.log.warn( json.dumps( json.loads( main.ONOScli1.intents() ),
                                       sort_keys=True,
                                       indent=4,
                                       separators=( ',', ': ' ) ) )
        if PingResult == main.TRUE:
            main.log.report(
                "Intents have been installed correctly and verified by pings" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=PingResult,
            onpass="Intents have been installed correctly and pings work",
            onfail="Intents have not been installed correctly, pings failed." )

    def CASE5( self, main ):
        """
        Reading state of ONOS
        """
        import json
        # assumes that sts is already in you PYTHONPATH
        from sts.topology.teston_topology import TestONTopology

        main.log.report( "Setting up and gathering data for current state" )
        main.case( "Setting up and gathering data for current state" )
        # The general idea for this test case is to pull the state of
        # ( intents,flows, topology,... ) from each ONOS node
        # We can then compare them with eachother and also with past states

        main.step( "Get the Mastership of each switch from each controller" )
        global mastershipState
        mastershipState = []

        # Assert that each device has a master
        rolesNotNull = main.ONOScli1.rolesNotNull()
        utilities.assert_equals(
            expect=main.TRUE,
            actual=rolesNotNull,
            onpass="Each device has a master",
            onfail="Some devices don't have a master assigned" )

        ONOS1Mastership = main.ONOScli1.roles()
        # TODO: Make this a meaningful check
        if "Error" in ONOS1Mastership or not ONOS1Mastership:
            main.log.report( "Error in getting ONOS roles" )
            main.log.warn(
                "ONOS1 mastership response: " +
                repr( ONOS1Mastership ) )
            consistentMastership = main.FALSE
        else:
            mastershipState = ONOS1Mastership
            consistentMastership = main.TRUE

        main.step( "Get the intents from each controller" )
        global intentState
        intentState = []
        ONOS1Intents = main.ONOScli1.intents( jsonFormat=True )
        intentCheck = main.FALSE
        if "Error" in ONOS1Intents or not ONOS1Intents:
            main.log.report( "Error in getting ONOS intents" )
            main.log.warn( "ONOS1 intents response: " + repr( ONOS1Intents ) )
        else:
            intentCheck = main.TRUE

        main.step( "Get the flows from each controller" )
        global flowState
        flowState = []
        ONOS1Flows = main.ONOScli1.flows( jsonFormat=True )
        flowCheck = main.FALSE
        if "Error" in ONOS1Flows or not ONOS1Flows:
            main.log.report( "Error in getting ONOS intents" )
            main.log.warn( "ONOS1 flows repsponse: " + ONOS1Flows )
        else:
            # TODO: Do a better check, maybe compare flows on switches?
            flowState = ONOS1Flows
            flowCheck = main.TRUE

        main.step( "Get the OF Table entries" )
        global flows
        flows = []
        for i in range( 1, 29 ):
            flows.append( main.Mininet2.getFlowTable( 1.3, "s" + str( i ) ) )

        # TODO: Compare switch flow tables with ONOS flow tables

        main.step( "Create TestONTopology object" )
        ctrls = []
        count = 1
        temp = ()
        temp = temp + ( getattr( main, ( 'ONOS' + str( count ) ) ), )
        temp = temp + ( "ONOS" + str( count ), )
        temp = temp + ( main.params[ 'CTRL' ][ 'ip' + str( count ) ], )
        temp = temp + \
            ( eval( main.params[ 'CTRL' ][ 'port' + str( count ) ] ), )
        ctrls.append( temp )
        MNTopo = TestONTopology(
            main.Mininet1,
            ctrls )  # can also add Intent API info for intent operations

        main.step( "Collecting topology information from ONOS" )
        devices = []
        devices.append( main.ONOScli1.devices() )
        """
        hosts = []
        hosts.append( main.ONOScli1.hosts() )
        """
        ports = []
        ports.append( main.ONOScli1.ports() )
        links = []
        links.append( main.ONOScli1.links() )

        main.step( "Comparing ONOS topology to MN" )
        devicesResults = main.TRUE
        portsResults = main.TRUE
        linksResults = main.TRUE
        for controller in range( numControllers ):
            controllerStr = str( controller + 1 )
            if devices[ controller ] or "Error" not in devices[ controller ]:
                currentDevicesResult = main.Mininet1.compareSwitches(
                    MNTopo,
                    json.loads(
                        devices[ controller ] ) )
            else:
                currentDevicesResult = main.FALSE
            utilities.assert_equals( expect=main.TRUE,
                                    actual=currentDevicesResult,
                                    onpass="ONOS" + controllerStr +
                                    " Switches view is correct",
                                    onfail="ONOS" + controllerStr +
                                    " Switches view is incorrect" )

            if ports[ controller ] or "Error" not in ports[ controller ]:
                currentPortsResult = main.Mininet1.comparePorts(
                    MNTopo,
                    json.loads(
                        ports[ controller ] ) )
            else:
                currentPortsResult = main.FALSE
            utilities.assert_equals( expect=main.TRUE,
                                    actual=currentPortsResult,
                                    onpass="ONOS" + controllerStr +
                                    " ports view is correct",
                                    onfail="ONOS" + controllerStr +
                                    " ports view is incorrect" )

            if links[ controller ] or "Error" not in links[ controller ]:
                currentLinksResult = main.Mininet1.compareLinks(
                    MNTopo,
                    json.loads(
                        links[ controller ] ) )
            else:
                currentLinksResult = main.FALSE
            utilities.assert_equals( expect=main.TRUE,
                                    actual=currentLinksResult,
                                    onpass="ONOS" + controllerStr +
                                    " links view is correct",
                                    onfail="ONOS" + controllerStr +
                                    " links view is incorrect" )

            devicesResults = devicesResults and currentDevicesResult
            portsResults = portsResults and currentPortsResult
            linksResults = linksResults and currentLinksResult

        topoResult = devicesResults and portsResults and linksResults
        utilities.assert_equals( expect=main.TRUE, actual=topoResult,
                                onpass="Topology Check Test successful",
                                onfail="Topology Check Test NOT successful" )

        finalAssert = main.TRUE
        finalAssert = finalAssert and topoResult and flowCheck \
            and intentCheck and consistentMastership and rolesNotNull
        utilities.assert_equals( expect=main.TRUE, actual=finalAssert,
                                onpass="State check successful",
                                onfail="State check NOT successful" )

    def CASE6( self, main ):
        """
        The Failure case.
        """
        import time

        main.log.report( "Restart ONOS node" )
        main.log.case( "Restart ONOS node" )
        main.ONOSbench.onosKill( ONOS1Ip )
        start = time.time()

        main.step( "Checking if ONOS is up yet" )
        count = 0
        while count < 10:
            onos1Isup = main.ONOSbench.isup( ONOS1Ip )
            if onos1Isup == main.TRUE:
                elapsed = time.time() - start
                break
            else:
                count = count + 1

        cliResult = main.ONOScli1.startOnosCli( ONOS1Ip )

        caseResults = main.TRUE and onos1Isup and cliResult
        utilities.assert_equals( expect=main.TRUE, actual=caseResults,
                                onpass="ONOS restart successful",
                                onfail="ONOS restart NOT successful" )
        main.log.info(
            "ESTIMATE: ONOS took %s seconds to restart" %
            str( elapsed ) )
        time.sleep( 5 )

    def CASE7( self, main ):
        """
        Check state after ONOS failure
        """
        import json
        main.case( "Running ONOS Constant State Tests" )

        # Assert that each device has a master
        rolesNotNull = main.ONOScli1.rolesNotNull()
        utilities.assert_equals(
            expect=main.TRUE,
            actual=rolesNotNull,
            onpass="Each device has a master",
            onfail="Some devices don't have a master assigned" )

        main.step( "Check if switch roles are consistent across all nodes" )
        ONOS1Mastership = main.ONOScli1.roles()
        # FIXME: Refactor this whole case for single instance
        if "Error" in ONOS1Mastership or not ONOS1Mastership:
            main.log.report( "Error in getting ONOS mastership" )
            main.log.warn(
                "ONOS1 mastership response: " +
                repr( ONOS1Mastership ) )
            consistentMastership = main.FALSE
        else:
            consistentMastership = main.TRUE
            main.log.report(
                "Switch roles are consistent across all ONOS nodes" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=consistentMastership,
            onpass="Switch roles are consistent across all ONOS nodes",
            onfail="ONOS nodes have different views of switch roles" )

        description2 = "Compare switch roles from before failure"
        main.step( description2 )

        currentJson = json.loads( ONOS1Mastership )
        oldJson = json.loads( mastershipState )
        mastershipCheck = main.TRUE
        for i in range( 1, 29 ):
            switchDPID = str(
                main.Mininet1.getSwitchDPID(
                    switch="s" +
                    str( i ) ) )

            current = [ switch[ 'master' ] for switch in currentJson
                        if switchDPID in switch[ 'id' ] ]
            old = [ switch[ 'master' ] for switch in oldJson
                    if switchDPID in switch[ 'id' ] ]
            if current == old:
                mastershipCheck = mastershipCheck and main.TRUE
            else:
                main.log.warn( "Mastership of switch %s changed" % switchDPID )
                mastershipCheck = main.FALSE
        if mastershipCheck == main.TRUE:
            main.log.report( "Mastership of Switches was not changed" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=mastershipCheck,
            onpass="Mastership of Switches was not changed",
            onfail="Mastership of some switches changed" )
        mastershipCheck = mastershipCheck and consistentMastership

        main.step( "Get the intents and compare across all nodes" )
        ONOS1Intents = main.ONOScli1.intents( jsonFormat=True )
        intentCheck = main.FALSE
        if "Error" in ONOS1Intents or not ONOS1Intents:
            main.log.report( "Error in getting ONOS intents" )
            main.log.warn( "ONOS1 intents response: " + repr( ONOS1Intents ) )
        else:
            intentCheck = main.TRUE
            main.log.report( "Intents are consistent across all ONOS nodes" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=intentCheck,
            onpass="Intents are consistent across all ONOS nodes",
            onfail="ONOS nodes have different views of intents" )

        # NOTE: Hazelcast has no durability, so intents are lost across system
        # restarts
        """
        main.step( "Compare current intents with intents before the failure" )
        # NOTE: this requires case 5 to pass for intentState to be set.
        #      maybe we should stop the test if that fails?
        if intentState == ONOS1Intents:
            sameIntents = main.TRUE
            main.log.report( "Intents are consistent with before failure" )
        # TODO: possibly the states have changed? we may need to figure out
        # what the aceptable states are
        else:
            try:
                main.log.warn( "ONOS1 intents: " )
                print json.dumps( json.loads( ONOS1Intents ),
                                  sort_keys=True, indent=4,
                                  separators=( ',', ': ' ) )
            except:
                pass
            sameIntents = main.FALSE
        utilities.assert_equals(
            expect=main.TRUE,
            actual=sameIntents,
            onpass="Intents are consistent with before failure",
            onfail="The Intents changed during failure" )
        intentCheck = intentCheck and sameIntents
        """
        main.step( "Get the OF Table entries and compare to before " +
                   "component failure" )
        FlowTables = main.TRUE
        flows2 = []
        for i in range( 28 ):
            main.log.info( "Checking flow table on s" + str( i + 1 ) )
            tmpFlows = main.Mininet2.getFlowTable( 1.3, "s" + str( i + 1 ) )
            flows2.append( tmpFlows )
            tempResult = main.Mininet2.flowComp(
                flow1=flows[ i ],
                flow2=tmpFlows )
            FlowTables = FlowTables and tempResult
            if FlowTables == main.FALSE:
                main.log.info( "Differences in flow table for switch: s" +
                               str( i + 1 ) )
        if FlowTables == main.TRUE:
            main.log.report( "No changes were found in the flow tables" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=FlowTables,
            onpass="No changes were found in the flow tables",
            onfail="Changes were found in the flow tables" )

        # Test of LeadershipElection

        leader = ONOS1Ip
        leaderResult = main.TRUE
        for controller in range( 1, numControllers + 1 ):
            # loop through ONOScli handlers
            node = getattr( main, ( 'ONOScli' + str( controller ) ) )
            leaderN = node.electionTestLeader()
            # verify leader is ONOS1
            # NOTE even though we restarted ONOS, it is the only one so onos 1
            # must be leader
            if leaderN == leader:
                # all is well
                pass
            elif leaderN == main.FALSE:
                # error in  response
                main.log.report( "Something is wrong with " +
                                 "electionTestLeader function, check the" +
                                 " error logs" )
                leaderResult = main.FALSE
            elif leader != leaderN:
                leaderResult = main.FALSE
                main.log.report( "ONOS" + str( controller ) +
                                 " sees " + str( leaderN ) +
                                 " as the leader of the election app." +
                                 " Leader should be " + str( leader ) )
        if leaderResult:
            main.log.report( "Leadership election tests passed( consistent " +
                             "view of leader across listeners and a new " +
                             "leader was re-elected if applicable )" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=leaderResult,
            onpass="Leadership election passed",
            onfail="Something went wrong with Leadership election" )

        result = ( mastershipCheck and intentCheck and FlowTables and
                   rolesNotNull and leaderResult )
        result = int( result )
        if result == main.TRUE:
            main.log.report( "Constant State Tests Passed" )
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                onpass="Constant State Tests Passed",
                                onfail="Constant state tests failed" )

    def CASE8( self, main ):
        """
        Compare topo
        """
        import sys
        # FIXME add this path to params
        sys.path.append( "/home/admin/sts" )
        # assumes that sts is already in you PYTHONPATH
        from sts.topology.teston_topology import TestONTopology
        import json
        import time

        description = "Compare ONOS Topology view to Mininet topology"
        main.case( description )
        main.log.report( description )
        main.step( "Create TestONTopology object" )
        ctrls = []
        count = 1
        temp = ()
        temp = temp + ( getattr( main, ( 'ONOS' + str( count ) ) ), )
        temp = temp + ( "ONOS" + str( count ), )
        temp = temp + ( main.params[ 'CTRL' ][ 'ip' + str( count ) ], )
        temp = temp + \
            ( eval( main.params[ 'CTRL' ][ 'port' + str( count ) ] ), )
        ctrls.append( temp )
        MNTopo = TestONTopology(
            main.Mininet1,
            ctrls )  # can also add Intent API info for intent operations

        main.step( "Comparing ONOS topology to MN" )
        devicesResults = main.TRUE
        portsResults = main.TRUE
        linksResults = main.TRUE
        topoResult = main.FALSE
        elapsed = 0
        count = 0
        main.step( "Collecting topology information from ONOS" )
        startTime = time.time()
        while topoResult == main.FALSE and elapsed < 60:
            count = count + 1
            if count > 1:
                MNTopo = TestONTopology(
                    main.Mininet1,
                    ctrls )
            cliStart = time.time()
            devices = []
            devices.append( main.ONOScli1.devices() )
            """
            hosts = []
            hosts.append( main.ONOScli1.hosts() )
            """
            ports = []
            ports.append( main.ONOScli1.ports() )
            links = []
            links.append( main.ONOScli1.links() )
            elapsed = time.time() - startTime
            cliTime = time.time() - cliStart
            print "CLI time: " + str( cliTime )

            for controller in range( numControllers ):
                controllerStr = str( controller + 1 )
                if devices[ controller ] or "Error" not in devices[
                        controller ]:
                    currentDevicesResult = main.Mininet1.compareSwitches(
                        MNTopo,
                        json.loads(
                            devices[ controller ] ) )
                else:
                    currentDevicesResult = main.FALSE
                utilities.assert_equals( expect=main.TRUE,
                                        actual=currentDevicesResult,
                                        onpass="ONOS" + controllerStr +
                                        " Switches view is correct",
                                        onfail="ONOS" + controllerStr +
                                        " Switches view is incorrect" )

                if ports[ controller ] or "Error" not in ports[ controller ]:
                    currentPortsResult = main.Mininet1.comparePorts(
                        MNTopo,
                        json.loads(
                            ports[ controller ] ) )
                else:
                    currentPortsResult = main.FALSE
                utilities.assert_equals( expect=main.TRUE,
                                        actual=currentPortsResult,
                                        onpass="ONOS" + controllerStr +
                                        " ports view is correct",
                                        onfail="ONOS" + controllerStr +
                                        " ports view is incorrect" )

                if links[ controller ] or "Error" not in links[ controller ]:
                    currentLinksResult = main.Mininet1.compareLinks(
                        MNTopo,
                        json.loads(
                            links[ controller ] ) )
                else:
                    currentLinksResult = main.FALSE
                utilities.assert_equals( expect=main.TRUE,
                                        actual=currentLinksResult,
                                        onpass="ONOS" + controllerStr +
                                        " links view is correct",
                                        onfail="ONOS" + controllerStr +
                                        " links view is incorrect" )
            devicesResults = devicesResults and currentDevicesResult
            portsResults = portsResults and currentPortsResult
            linksResults = linksResults and currentLinksResult
            topoResult = devicesResults and portsResults and linksResults

        topoResult = topoResult and int( count <= 2 )
        note = "note it takes about " + str( int( cliTime ) ) + \
            " seconds for the test to make all the cli calls to fetch " +\
            "the topology from each ONOS instance"
        main.log.report(
            "Very crass estimate for topology discovery/convergence( " +
            str( note ) + " ): " + str( elapsed ) + " seconds, " +
            str( count ) + " tries" )
        if elapsed > 60:
            main.log.report( "Giving up on topology convergence" )
        utilities.assert_equals( expect=main.TRUE, actual=topoResult,
                                onpass="Topology Check Test successful",
                                onfail="Topology Check Test NOT successful" )
        if topoResult == main.TRUE:
            main.log.report( "ONOS topology view matches Mininet topology" )

    def CASE9( self, main ):
        """
        Link s3-s28 down
        """
        import time
        # NOTE: You should probably run a topology check after this

        linkSleep = float( main.params[ 'timers' ][ 'LinkDiscovery' ] )

        description = "Turn off a link to ensure that Link Discovery " +\
            "is working properly"
        main.log.report( description )
        main.case( description )

        main.step( "Kill Link between s3 and s28" )
        LinkDown = main.Mininet1.link( END1="s3", END2="s28", OPTION="down" )
        main.log.info(
            "Waiting " +
            str( linkSleep ) +
            " seconds for link down to be discovered" )
        time.sleep( linkSleep )
        utilities.assert_equals( expect=main.TRUE, actual=LinkDown,
                                onpass="Link down succesful",
                                onfail="Failed to bring link down" )
        # TODO do some sort of check here

    def CASE10( self, main ):
        """
        Link s3-s28 up
        """
        import time
        # NOTE: You should probably run a topology check after this

        linkSleep = float( main.params[ 'timers' ][ 'LinkDiscovery' ] )

        description = "Restore a link to ensure that Link Discovery is " + \
            "working properly"
        main.log.report( description )
        main.case( description )

        main.step( "Bring link between s3 and s28 back up" )
        LinkUp = main.Mininet1.link( END1="s3", END2="s28", OPTION="up" )
        main.log.info(
            "Waiting " +
            str( linkSleep ) +
            " seconds for link up to be discovered" )
        time.sleep( linkSleep )
        utilities.assert_equals( expect=main.TRUE, actual=LinkUp,
                                onpass="Link up succesful",
                                onfail="Failed to bring link up" )
        # TODO do some sort of check here

    def CASE11( self, main ):
        """
        Switch Down
        """
        # NOTE: You should probably run a topology check after this
        import time

        switchSleep = float( main.params[ 'timers' ][ 'SwitchDiscovery' ] )

        description = "Killing a switch to ensure it is discovered correctly"
        main.log.report( description )
        main.case( description )
        switch = main.params[ 'kill' ][ 'switch' ]
        switchDPID = main.params[ 'kill' ][ 'dpid' ]

        # TODO: Make this switch parameterizable
        main.step( "Kill " + switch )
        main.log.report( "Deleting " + switch )
        main.Mininet1.delSwitch( switch )
        main.log.info( "Waiting " + str( switchSleep ) +
                       " seconds for switch down to be discovered" )
        time.sleep( switchSleep )
        device = main.ONOScli1.getDevice( dpid=switchDPID )
        # Peek at the deleted switch
        main.log.warn( str( device ) )
        result = main.FALSE
        if device and device[ 'available' ] is False:
            result = main.TRUE
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                onpass="Kill switch succesful",
                                onfail="Failed to kill switch?" )

    def CASE12( self, main ):
        """
        Switch Up
        """
        # NOTE: You should probably run a topology check after this
        import time

        switchSleep = float( main.params[ 'timers' ][ 'SwitchDiscovery' ] )
        switch = main.params[ 'kill' ][ 'switch' ]
        switchDPID = main.params[ 'kill' ][ 'dpid' ]
        links = main.params[ 'kill' ][ 'links' ].split()
        description = "Adding a switch to ensure it is discovered correctly"
        main.log.report( description )
        main.case( description )

        main.step( "Add back " + switch )
        main.log.report( "Adding back " + switch )
        main.Mininet1.addSwitch( switch, dpid=switchDPID )
        # TODO: New dpid or same? Ask Thomas?
        for peer in links:
            main.Mininet1.addLink( switch, peer )
        main.Mininet1.assignSwController( sw=switch.split( 's' )[ 1 ],
                                           ip1=ONOS1Ip, port1=ONOS1Port )
        main.log.info(
            "Waiting " +
            str( switchSleep ) +
            " seconds for switch up to be discovered" )
        time.sleep( switchSleep )
        device = main.ONOScli1.getDevice( dpid=switchDPID )
        # Peek at the deleted switch
        main.log.warn( str( device ) )
        result = main.FALSE
        if device and device[ 'available' ]:
            result = main.TRUE
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                onpass="add switch succesful",
                                onfail="Failed to add switch?" )

    def CASE13( self, main ):
        """
        Clean up
        """
        import os
        import time
        # printing colors to terminal
        colors = {}
        colors[ 'cyan' ] = '\033[96m'
        colors[ 'purple' ] = '\033[95m'
        colors[ 'blue' ] = '\033[94m'
        colors[ 'green' ] = '\033[92m'
        colors[ 'yellow' ] = '\033[93m'
        colors[ 'red' ] = '\033[91m'
        colors[ 'end' ] = '\033[0m'
        description = "Test Cleanup"
        main.log.report( description )
        main.case( description )
        main.step( "Killing tcpdumps" )
        main.Mininet2.stopTcpdump()

        main.step( "Checking ONOS Logs for errors" )
        print colors[ 'purple' ] + "Checking logs for errors on ONOS1:" + \
            colors[ 'end' ]
        print main.ONOSbench.checkLogs( ONOS1Ip )
        main.step( "Copying MN pcap and ONOS log files to test station" )
        testname = main.TEST
        teststationUser = main.params[ 'TESTONUSER' ]
        teststationIP = main.params[ 'TESTONIP' ]
        # NOTE: MN Pcap file is being saved to ~/packet_captures
        #       scp this file as MN and TestON aren't necessarily the same vm
        # FIXME: scp
        # mn files
        # TODO: Load these from params
        # NOTE: must end in /
        logFolder = "/opt/onos/log/"
        logFiles = [ "karaf.log", "karaf.log.1" ]
        # NOTE: must end in /
        dstDir = "~/packet_captures/"
        for f in logFiles:
            main.ONOSbench.handle.sendline( "scp sdn@" + ONOS1Ip + ":" +
                                            logFolder + f + " " +
                                            teststationUser + "@" +
                                            teststationIP + ":" + dstDir +
                                            str( testname ) + "-ONOS1-" + f )
            main.ONOSbench.handle.expect( "\$" )
            print main.ONOSbench.handle.before

        # std*.log's
        # NOTE: must end in /
        logFolder = "/opt/onos/var/"
        logFiles = [ "stderr.log", "stdout.log" ]
        # NOTE: must end in /
        dstDir = "~/packet_captures/"
        for f in logFiles:
            main.ONOSbench.handle.sendline( "scp sdn@" + ONOS1Ip + ":" +
                                            logFolder + f + " " +
                                            teststationUser + "@" +
                                            teststationIP + ":" + dstDir +
                                            str( testname ) + "-ONOS1-" + f )
        # sleep so scp can finish
        time.sleep( 10 )
        main.step( "Packing and rotating pcap archives" )
        os.system( "~/TestON/dependencies/rotate.sh " + str( testname ) )

        # TODO: actually check something here
        utilities.assert_equals( expect=main.TRUE, actual=main.TRUE,
                                onpass="Test cleanup successful",
                                onfail="Test cleanup NOT successful" )

    def CASE14( self, main ):
        """
        start election app on all onos nodes
        """
        leaderResult = main.TRUE
        # install app on onos 1
        main.log.info( "Install leadership election app" )
        main.ONOScli1.featureInstall( "onos-app-election" )
        # wait for election
        # check for leader
        leader = main.ONOScli1.electionTestLeader()
        # verify leader is ONOS1
        if leader == ONOS1Ip:
            # all is well
            pass
        elif leader is None:
            # No leader elected
            main.log.report( "No leader was elected" )
            leaderResult = main.FALSE
        elif leader == main.FALSE:
            # error in  response
            # TODO: add check for "Command not found:" in the driver, this
            # means the app isn't loaded
            main.log.report( "Something is wrong with electionTestLeader" +
                             " function, check the error logs" )
            leaderResult = main.FALSE
        else:
            # error in  response
            main.log.report(
                "Unexpected response from electionTestLeader function:'" +
                str( leader ) +
                "'" )
            leaderResult = main.FALSE

        # install on other nodes and check for leader.
        # Should be onos1 and each app should show the same leader
        for controller in range( 2, numControllers + 1 ):
            # loop through ONOScli handlers
            node = getattr( main, ( 'ONOScli' + str( controller ) ) )
            node.featureInstall( "onos-app-election" )
            leaderN = node.electionTestLeader()
            # verify leader is ONOS1
            if leaderN == ONOS1Ip:
                # all is well
                pass
            elif leaderN == main.FALSE:
                # error in  response
                # TODO: add check for "Command not found:" in the driver, this
                # means the app isn't loaded
                main.log.report( "Something is wrong with " +
                                 "electionTestLeader function, check the" +
                                 " error logs" )
                leaderResult = main.FALSE
            elif leader != leaderN:
                leaderResult = main.FALSE
                main.log.report( "ONOS" + str( controller ) + " sees " +
                                 str( leaderN ) +
                                 " as the leader of the election app. Leader" +
                                 " should be " +
                                 str( leader ) )
        if leaderResult:
            main.log.report( "Leadership election tests passed( consistent " +
                             "view of leader across listeners and a leader " +
                             "was elected )" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=leaderResult,
            onpass="Leadership election passed",
            onfail="Something went wrong with Leadership election" )

    def CASE15( self, main ):
        """
        Check that Leadership Election is still functional
        """
        leaderResult = main.TRUE
        description = "Check that Leadership Election is still functional"
        main.log.report( description )
        main.case( description )
        main.step( "Find current leader and withdraw" )
        leader = main.ONOScli1.electionTestLeader()
        # TODO: do some sanity checking on leader before using it
        withdrawResult = main.FALSE
        if leader == ONOS1Ip:
            oldLeader = getattr( main, "ONOScli1" )
        elif leader is None or leader == main.FALSE:
            main.log.report(
                "Leader for the election app should be an ONOS node," +
                "instead got '" +
                str( leader ) +
                "'" )
            leaderResult = main.FALSE
        withdrawResult = oldLeader.electionTestWithdraw()
        utilities.assert_equals(
            expect=main.TRUE,
            actual=withdrawResult,
            onpass="App was withdrawn from election",
            onfail="App was not withdrawn from election" )

        main.step( "Make sure new leader is elected" )
        leaderList = []
        leaderN = main.ONOScli1.electionTestLeader()
        if leaderN == leader:
            main.log.report( "ONOS still sees " + str( leaderN ) +
                             " as leader after they withdrew" )
            leaderResult = main.FALSE
        elif leaderN == main.FALSE:
            # error in  response
            # TODO: add check for "Command not found:" in the driver, this
            # means the app isn't loaded
            main.log.report( "Something is wrong with electionTestLeader " +
                             "function, check the error logs" )
            leaderResult = main.FALSE
        elif leaderN is None:
            main.log.info(
                "There is no leader after the app withdrew from election" )
        if leaderResult:
            main.log.report( "Leadership election tests passed( There is no " +
                             "leader after the old leader resigned )" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=leaderResult,
            onpass="Leadership election passed",
            onfail="Something went wrong with Leadership election" )

        main.step(
            "Run for election on old leader( just so everyone is in the hat )" )
        runResult = oldLeader.electionTestRun()
        utilities.assert_equals(
            expect=main.TRUE,
            actual=runResult,
            onpass="App re-ran for election",
            onfail="App failed to run for election" )
        leader = main.ONOScli1.electionTestLeader()
        # verify leader is ONOS1
        if leader == ONOS1Ip:
            leaderResult = main.TRUE
        else:
            leaderResult = main.FALSE
        # TODO: assert on  run and withdraw results?

        utilities.assert_equals(
            expect=main.TRUE,
            actual=leaderResult,
            onpass="Leadership election passed",
            onfail="ONOS1's election app was not leader after it re-ran " +
                   "for election" )
