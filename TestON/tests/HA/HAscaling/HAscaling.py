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
Description: This test is to determine if ONOS can handle
             dynamic scaling of the cluster size.

List of test cases:
CASE1: Compile ONOS and push it to the test machines
CASE2: Assign devices to controllers
CASE21: Assign mastership to controllers
CASE3: Assign intents
CASE4: Ping across added host intents
CASE5: Reading state of ONOS
CASE6: The scaling case.
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
class HAscaling:

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
        import time
        import os
        import re
        main.log.info( "ONOS HA test: Restart all ONOS nodes - " +
                         "initialization" )
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
            from tests.HA.HAswapNodes.dependencies.Server import Server
            main.Server = Server()

            # load some variables from the params file
            cellName = main.params[ 'ENV' ][ 'cellName' ]
            main.apps = main.params[ 'ENV' ][ 'appString' ]
            stepResult = main.testSetUp.envSetup()
        except Exception as e:
            main.testSetUp.envSetupException( e )
        main.testSetUp.evnSetupConclusion( stepResult )

        main.testSetUp.ONOSSetUp( main.Mininet1, main.Cluster, cellName=cellName, removeLog=True,
                                  extraApply=[ main.HA.setServerForCluster,
                                               main.HA.scalingMetadata,
                                               main.HA.startingMininet,
                                               main.HA.copyBackupConfig,
                                               main.HA.setMetadataUrl ],
                                  extraClean=main.HA.cleanUpOnosService,
                                  installMax=True )

        main.HA.initialSetUp( serviceClean=True )

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
        main.HA.readingState( main )

    def CASE6( self, main ):
        """
        The Scaling case.
        """
        import time
        import re
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"
        try:
            main.HAlabels
        except ( NameError, AttributeError ):
            main.log.error( "main.HAlabels not defined, setting to []" )
            main.HAlabels = []
        try:
            main.HAdata
        except ( NameError, AttributeError ):
            main.log.error( "main.HAdata not defined, setting to []" )
            main.HAdata = []

        main.case( "Scale the number of nodes in the ONOS cluster" )

        main.step( "Checking ONOS Logs for errors" )
        for ctrl in main.Cluster.active():
            main.log.debug( "Checking logs for errors on " + ctrl.name + ":" )
            main.log.warn( main.ONOSbench.checkLogs( ctrl.ipAddress ) )

        """
        pop # of nodes from a list, might look like 1,3b,3,5b,5,7b,7,7b,5,5b,3...
        modify cluster.json file appropriately
        install/deactivate node as needed
        """
        try:
            prevNodes = main.Cluster.active()
            scale = main.scaling.pop( 0 )
            if "e" in scale:
                equal = True
            else:
                equal = False
            main.Cluster.setRunningNode( int( re.search( "\d+", scale ).group( 0 ) ) )
            main.log.info( "Scaling to {} nodes".format( main.Cluster.numCtrls ) )
            genResult = main.Server.generateFile( main.Cluster.numCtrls, equal=equal )
            utilities.assert_equals( expect=main.TRUE, actual=genResult,
                                     onpass="New cluster metadata file generated",
                                     onfail="Failled to generate new metadata file" )
            time.sleep( 5 )  # Give time for nodes to read new file
        except IndexError:
            main.cleanAndExit()

        activeNodes = [ i for i in range( 0, main.Cluster.numCtrls ) ]
        newNodes = [ x for x in activeNodes if x not in prevNodes ]
        main.Cluster.resetActive()
        main.step( "Start new nodes" )  # OR stop old nodes?
        started = main.TRUE
        for i in newNodes:
            started = main.ONOSbench.onosStart( main.Cluster.runningNodes[ i ].ipAddress ) and main.TRUE
        utilities.assert_equals( expect=main.TRUE, actual=started,
                                 onpass="ONOS started",
                                 onfail="ONOS start NOT successful" )

        main.testSetUp.setupSsh( main.Cluster )

        main.testSetUp.checkOnosService( main.Cluster )

        main.Cluster.startCLIs()

        main.step( "Checking ONOS nodes" )
        nodeResults = utilities.retry( main.HA.nodesCheck,
                                       False,
                                       args=[ main.Cluster.active() ],
                                       attempts=5 )
        utilities.assert_equals( expect=True, actual=nodeResults,
                                 onpass="Nodes check successful",
                                 onfail="Nodes check NOT successful" )

        for i in range( 10 ):
            ready = True
            for ctrl in main.Cluster.active():
                output = ctrl.CLI.summary()
                if not output:
                    ready = False
            if ready:
                break
            time.sleep( 30 )
        utilities.assert_equals( expect=True, actual=ready,
                                 onpass="ONOS summary command succeded",
                                 onfail="ONOS summary command failed" )
        if not ready:
            main.cleanAndExit()

        # Rerun for election on new nodes
        runResults = main.TRUE
        for ctrl in main.Cluster.active():
            run = ctrl.CLI.electionTestRun()
            if run != main.TRUE:
                main.log.error( "Error running for election on " + ctrl.name )
            runResults = runResults and run
        utilities.assert_equals( expect=main.TRUE, actual=runResults,
                                 onpass="Reran for election",
                                 onfail="Failed to rerun for election" )

        # TODO: Make this configurable
        time.sleep( 60 )
        main.HA.commonChecks()

    def CASE7( self, main ):
        """
        Check state after ONOS scaling
        """
        main.HA.checkStateAfterEvent( main, afterWhich=1 )

        main.step( "Leadership Election is still functional" )
        # Test of LeadershipElection
        leaderList = []
        leaderResult = main.TRUE

        for ctrl in main.Cluster.active():
            leaderN = ctrl.CLI.electionTestLeader()
            leaderList.append( leaderN )
            if leaderN == main.FALSE:
                # error in response
                main.log.error( "Something is wrong with " +
                                 "electionTestLeader function, check the" +
                                 " error logs" )
                leaderResult = main.FALSE
            elif leaderN is None:
                main.log.error( cli.name +
                                 " shows no leader for the election-app." )
                leaderResult = main.FALSE
        if len( set( leaderList ) ) != 1:
            leaderResult = main.FALSE
            main.log.error(
                "Inconsistent view of leader for the election test app" )
            # TODO: print the list
        utilities.assert_equals(
            expect=main.TRUE,
            actual=leaderResult,
            onpass="Leadership election passed",
            onfail="Something went wrong with Leadership election" )

    def CASE8( self, main ):
        """
        Compare topo
        """
        main.HA.compareTopo( main )

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
        main.HA.cleanUp( main )

        main.step( "Stopping webserver" )
        status = main.Server.stop()
        utilities.assert_equals( expect=main.TRUE, actual=status,
                                 onpass="Stop Server",
                                 onfail="Failled to stop SimpleHTTPServer" )
        del main.Server

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
