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
             a full network partion

List of test cases:
CASE1: Compile ONOS and push it to the test machines
CASE2: Assign devices to controllers
CASE21: Assign mastership to controllers
CASE3: Assign intents
CASE4: Ping across added host intents
CASE5: Reading state of ONOS
CASE61: The Failure inducing case.
CASE62: The Failure recovery case.
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
class HAfullNetPartition:

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
        main.log.info( "ONOS HA test: Partition ONOS nodes into two sub-clusters - " +
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
            # load some variables from the params file
            cellName = main.params[ 'ENV' ][ 'cellName' ]
            main.apps = main.params[ 'ENV' ][ 'appString' ]
            stepResult = main.testSetUp.envSetup( includeCaseDesc=False )
        except Exception as e:
            main.testSetUp.envSetupException( e )
        main.testSetUp.evnSetupConclusion( stepResult )

        applyFuncs = [ main.HA.removeKarafConsoleLogging, main.HA.customizeOnosGenPartitions ]
        applyArgs = [ None, None ]
        try:
            if main.params[ 'topology' ][ 'topoFile' ]:
                main.log.info( 'Skipping start of Mininet in this case, make sure you start it elsewhere' )
            else:
                applyFuncs.append( main.HA.startingMininet )
                applyArgs.append( None )
        except (KeyError, IndexError):
                applyFuncs.append( main.HA.startingMininet )
                applyArgs.append( None )

        main.testSetUp.ONOSSetUp( main.Cluster, cellName=cellName,
                                  extraApply=applyFuncs,
                                  applyArgs=applyArgs,
                                  extraClean=main.HA.cleanUpGenPartition,
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

    def CASE61( self, main ):
        """
        The Failure case.
        """
        import pexpect
        import time
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"
        main.case( "Partition ONOS nodes into two distinct partitions" )

        main.step( "Checking ONOS Logs for errors" )
        for ctrl in main.Cluster.runningNodes:
            main.log.debug( "Checking logs for errors on " + ctrl.name + ":" )
            main.log.warn( main.ONOSbench.checkLogs( ctrl.ipAddress ) )

        main.log.debug( main.Cluster.next().CLI.roles( jsonFormat=False ) )

        n = len( main.Cluster.runningNodes )  # Number of nodes
        p = ( ( n + 1 ) / 2 ) + 1  # Number of partitions
        main.partition = [ 0 ]  # ONOS node to partition, listed by index in main.nodes
        if n > 3:
            main.partition.append( p - 1 )
            # NOTE: This only works for cluster sizes of 3,5, or 7.

        main.step( "Partitioning ONOS nodes" )
        nodeList = [ str( i + 1 ) for i in main.partition ]
        main.log.info( "Nodes to be partitioned: " + str( nodeList ) )
        partitionResults = main.TRUE
        standalonePort = "5679"  # use params file and default to this
        embeddedPort = "9876"  # use params file and default to this
        # We are blocking traffic from the embedded Atomix instance on nodes in main.partition
        for i in range( 0, n ):
            iCtrl = main.Cluster.runningNodes[ i ]
            this = iCtrl.Bench.sshToNode( iCtrl.ipAddress )
            if i not in main.partition:  # i is in the majority partition
                for j in main.partition:  # j is in the minority partition
                    foe = main.Cluster.runningNodes[ j ]
                    main.log.warn( "Setting IP Tables rule from {} to {}. ".format( iCtrl.ipAddress,
                                                                                    foe.ipAddress ) )
                    # CMD HERE
                    # On node i in majority partition: add rule to block from j in minority partition
                    cmdList = [ ]
                    cmdList.append( "sudo iptables -A {} -p tcp --sp {} -d {} -s {} -j DROP".format( "INPUT",
                                                                                                     embeddedPort,
                                                                                                     iCtrl.ipAddress,
                                                                                                     foe.ipAddress ) )
                    cmdList.append( "sudo ip6tables -A {} -p tcp --sp {} -d {} -s {} -j DROP".format( "INPUT",
                                                                                                      embeddedPort,
                                                                                                      iCtrl.ipAddress,
                                                                                                      foe.ipAddress ) )
                    try:
                        for cmd in cmdList:
                            this.sendline( cmd )
                            this.expect( "\$" )
                            main.log.debug( this.before )
                    except pexpect.EOF:
                        main.log.error( iCtrl.name + ": EOF exception found" )
                        main.log.error( iCtrl.name + ":    " + this.before )
                        main.cleanAndExit()
                    except Exception:
                        main.log.exception( iCtrl.name + ": Uncaught exception!" )
                        main.cleanAndExit()
            else:
                for j in range( 0, n ):
                    if j not in main.partition:
                        # On node i in minority partition: add rule to block from j in majority partition
                        foe = main.Cluster.runningNodes[ j ]
                        main.log.warn( "Setting IP Tables rule from {} to {}. ".format( iCtrl.ipAddress,
                                                                                        foe.ipAddress ) )
                        # CMD HERE
                        cmdList = [ ]
                        cmdList.append( "sudo iptables -A {} -p tcp --dp {} -d {} -s {} -j DROP".format( "INPUT",
                                                                                                         embeddedPort,
                                                                                                         iCtrl.ipAddress,
                                                                                                         foe.ipAddress ) )
                        cmdList.append( "sudo ip6tables -A {} -p tcp --dp {} -d {} -s {} -j DROP".format( "INPUT",
                                                                                                          embeddedPort,
                                                                                                          iCtrl.ipAddress,
                                                                                                          foe.ipAddress ) )
                        cmdList.append( "sudo iptables -A {} -p tcp --sp {} -s {} -j DROP".format( "OUTPUT",
                                                                                                   embeddedPort,
                                                                                                   iCtrl.ipAddress ) )
                        cmdList.append( "sudo ip6tables -A {} -p tcp --sp {} -s {} -j DROP".format( "OUTPUT",
                                                                                                    embeddedPort,
                                                                                                    iCtrl.ipAddress ) )
                        cmdList.append( "sudo iptables -A {} -p tcp --sp {} -s {} -m conntrack --ctstate ESTABLISHED -j DROP".format( "OUTPUT",
                                                                                                                                      embeddedPort,
                                                                                                                                      iCtrl.ipAddress ) )
                        cmdList.append( "sudo ip6tables -A {} -p tcp --sp {} -s {} -m conntrack --ctstate ESTABLISHED -j DROP".format( "OUTPUT",
                                                                                                                                       embeddedPort,
                                                                                                                                       iCtrl.ipAddress ) )
                        cmdList.append( "sudo iptables -A {} -p tcp --sp {} -s {} -m conntrack --ctstate ESTABLISHED -j DROP".format( "INPUT",
                                                                                                                                      embeddedPort,
                                                                                                                                      foe.ipAddress ) )
                        cmdList.append( "sudo ip6tables -A {} -p tcp --sp {} -s {} -m conntrack --ctstate ESTABLISHED -j DROP".format( "INPUT",
                                                                                                                                       embeddedPort,
                                                                                                                                       foe.ipAddress ) )
                        try:
                            for cmd in cmdList:
                                this.sendline( cmd )
                                this.expect( "\$" )
                                main.log.debug( this.before )
                        except pexpect.EOF:
                            main.log.error( iCtrl.name + ": EOF exception found" )
                            main.log.error( iCtrl.name + ":    " + this.before )
                            main.cleanAndExit()
                        except Exception:
                            main.log.exception( iCtrl.name + ": Uncaught exception!" )
                            main.cleanAndExit()
                # From embedded atomix to standalone atomix on same node, node i in minority partition
                foe = main.Cluster.runningNodes[ i ]
                main.log.warn( "Setting IP Tables rule from {} to {}. ".format( iCtrl.ipAddress,
                                                                                foe.ipAddress ) )
                # CMD HERE
                cmdStr = "sudo iptables -A {} -p tcp --sp {} -d {} -s {} -j DROP".format( "INPUT",
                                                                                             embeddedPort,
                                                                                             iCtrl.ipAddress,
                                                                                             foe.ipAddress )
                cmdStr2 = "sudo iptables -A {} -p tcp --dp {} -d {} -s {} -j DROP".format( "INPUT",
                                                                                              embeddedPort,
                                                                                              iCtrl.ipAddress,
                                                                                              foe.ipAddress )
                cmdStr3 = "sudo iptables -A {} -p tcp --sp {} -j DROP".format( "OUTPUT",
                                                                                   embeddedPort )
                try:
                    this.sendline( cmdStr )
                    this.expect( "\$" )
                    main.log.debug( this.before )
                    this.sendline( cmdStr2 )
                    this.expect( "\$" )
                    main.log.debug( this.before )
                except pexpect.EOF:
                    main.log.error( iCtrl.name + ": EOF exception found" )
                    main.log.error( iCtrl.name + ":    " + this.before )
                    main.cleanAndExit()
                except Exception:
                    main.log.exception( iCtrl.name + ": Uncaught exception!" )
                    main.cleanAndExit()
                main.Cluster.runningNodes[ i ].active = False
            # end if/else
            iCtrl.Bench.exitFromSsh( this, iCtrl.ipAddress )
        utilities.assert_equals( expect=main.TRUE, actual=partitionResults,
                                 onpass="Firewall rules set successfully",
                                 onfail="Error setting firewall rules" )
        main.Cluster.reset()
        main.log.debug( main.Cluster.active )

        main.step( "Sleeping 60 seconds" )
        time.sleep( 60 )

    def CASE62( self, main ):
        """
        Healing Partition
        """
        assert main, "main not defined"
        assert utilities.assert_equals, "utilities.assert_equals not defined"
        assert main.partition, "main.partition not defined"
        main.case( "Healing Partition" )

        main.step( "Deleteing firewall rules" )
        healResults = main.TRUE
        for ctrl in main.Cluster.runningNodes:
            cmdStr = "sudo iptables -F"
            handle = ctrl.Bench.sshToNode( ctrl.ipAddress )
            handle.sendline( cmdStr )
            handle.expect( "\$" )
            main.log.debug( handle.before )
            ctrl.Bench.exitFromSsh( handle, ctrl.ipAddress )
        utilities.assert_equals( expect=main.TRUE, actual=healResults,
                                 onpass="Firewall rules removed",
                                 onfail="Error removing firewall rules" )

        for node in main.partition:
            main.Cluster.runningNodes[ node ].active = True
        main.Cluster.reset()

        main.step( "Checking ONOS nodes" )
        nodeResults = utilities.retry( main.Cluster.nodesCheck,
                                       False,
                                       sleep=15,
                                       attempts=50 )

        utilities.assert_equals( expect=True, actual=nodeResults,
                                 onpass="Nodes check successful",
                                 onfail="Nodes check NOT successful" )

        if not nodeResults:
            for ctrl in main.Cluster.active():
                main.log.debug( "{} components not ACTIVE: \n{}".format(
                    ctrl.name,
                    ctrl.CLI.sendline( "onos:scr-list | grep -v ACTIVE" ) ) )
            main.log.error( "Failed to start ONOS, stopping test" )
            main.cleanAndExit()

    def CASE7( self, main ):
        """
        Check state after ONOS failure
        """
        main.HA.checkStateAfterEvent( main, afterWhich=0 )

        main.step( "Leadership Election is still functional" )
        # Test of LeadershipElection
        leaderList = []

        partitioned = []
        for i in main.partition:
            partitioned.append( main.Cluster.runningNodes[ i ].ipAddress )
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
                main.log.error( ctrl.name +
                                 " shows no leader for the election-app was" +
                                 " elected after the old one died" )
                leaderResult = main.FALSE
            elif leaderN in partitioned:
                main.log.error( ctrl.name + " shows " + str( leaderN ) +
                                 " as leader for the election-app, but it " +
                                 "was partitioned" )
                leaderResult = main.FALSE
        if len( set( leaderList ) ) != 1:
            leaderResult = main.FALSE
            main.log.error(
                "Inconsistent view of leader for the election test app" )
            main.log.debug( leaderList )
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
