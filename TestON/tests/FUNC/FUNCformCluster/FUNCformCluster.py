"""
Copyright 2017 Open Networking Foundation ( ONF )

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


class FUNCformCluster:

    def __init__( self ):
        self.default = ''

    def CASE0( self, main ):
        import imp
        import re

        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
            main.testSetUp = ONOSSetup()
        except ImportError:
            main.log.error( "ONOSSetup not found. exiting the test" )
            main.cleanAndExit()
        main.testSetUp.envSetupDescription()
        stepResult = main.TRUE
        try:
            main.apps = main.params[ 'ENV' ][ 'cellApps' ]
            main.additionalApp = main.params[ 'ENV' ][ 'additionalApp' ]
            main.cellBasicName = main.params[ 'ENV' ][ 'cellBasicName' ]
            main.mnTopo = main.params[ 'MININET' ][ 'topo' ]
            main.startSleep = int( main.params[ 'SLEEP' ][ 'afterONOSStart' ] )
            dependencyPath = main.testOnDirectory + \
                             main.params[ 'DEPENDENCY' ][ 'path' ]
            dependencyFile = main.params[ 'DEPENDENCY' ][ 'file' ]
            main.numNodes = int( main.params[ 'TEST' ][ 'numNodes' ] )
            main.funcs = imp.load_source( dependencyFile,
                                            dependencyPath +
                                            dependencyFile +
                                            ".py" )
            main.pingallRetry = int( main.params[ 'RETRY' ][ 'pingall' ] )
            main.topoCheckRetry = int( main.params[ 'RETRY' ][ 'topoCheck' ] )
            main.pingallSleep = int( main.params[ 'SLEEP' ][ 'pingall' ] )

        except Exception as e:
            main.testSetUp.envSetupException( e )
        if len( main.Cluster.runningNodes ) != main.numNodes:
            main.log.error( "The number of the nodes needs to be " + str( main.numNodes ) +
                            "\nExiting Test..." )
            main.cleanAndExit()
        main.testSetUp.envSetupConclusion( stepResult )

    def CASE1( self, main ):
        """
        - Create cells with single node
            - apply each cell to each cluster
        - install ONOS
        - ssh-secure
        - start the ONOS
        - activate org.onosproject.fwd to cluster 1 only.
        """
        main.case( "Starting ONOS with indepenent configuration" )
        main.caseExplanation = "Starting ONOS with one node itself."
        main.testSetUp.killingAllOnos( main.Cluster, True, False )
        threads = []
        i = 0
        for cluster in main.Cluster.runningNodes:
            i += 1
            t = main.Thread( target=cluster.Bench.createCellFile,
                             name="create-cell",
                             args=[ main.ONOSbench.ip_address,
                                    main.cellBasicName + str( i ),
                                    main.Mininet1.ip_address,
                                    main.apps,
                                    cluster.ip_address,
                                    cluster.ip_address,
                                    main.ONOScell.karafUser,
                                    True ] )
            threads.append( t )
            t.start()
        cellResult = main.TRUE
        for t in threads:
            t.join()
            cellResult = cellResult and t.result

        threads = []
        i = 0
        for cluster in main.Cluster.runningNodes:
            i += 1
            t = main.Thread( target=cluster.Bench.setCell,
                             name="set-cell",
                             args=[ main.cellBasicName + str( i ) ] )
            threads.append( t )
            t.start()
        for t in threads:
            t.join()
            cellResult = cellResult and t.result

        threads = []
        i = 0
        for cluster in main.Cluster.runningNodes:
            i += 1
            t = main.Thread( target=cluster.Bench.verifyCell,
                             name="verify-cell" )
            threads.append( t )
            t.start()
        for t in threads:
            t.join()
            cellResult = cellResult and t.result

        uninstallResult = main.testSetUp.uninstallOnos( main.Cluster, True )
        buildResult = main.testSetUp.buildOnos( main.Cluster )
        installResult = main.testSetUp.installOnos( main.Cluster, True, True )
        secureSshResult = main.testSetUp.setupSsh( main.Cluster )
        onosServiceResult = main.testSetUp.checkOnosService( main.Cluster )
        onosCliResult = main.testSetUp.startOnosClis( main.Cluster )
        activateResult = main.Cluster.active( 0 ).CLI.activateApp( main.additionalApp )

        result = cellResult and uninstallResult and buildResult and installResult and \
                 secureSshResult and onosServiceResult and onosCliResult and activateResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=result,
                                 onpass="Successfully started the ONOS",
                                 onfail="Failed to start the ONOS" )

    def CASE2( self, main ):
        """
        - Execute onos-form-cluster to all the nodes.
        - start the ONOS.
        - activate org.onosproject.fwd to cluster 1.
        """
        main.case( "Starting ONOS with form cluster." )
        main.caseExplanation = "This will connect all the clusters of the ONOS."
        main.step( "Executing onos-form-cluster" )
        formClusterResult = main.ONOSbench.formCluster( main.Cluster.getIps( True, True ) )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=formClusterResult,
                                 onpass="Successfully formed clusters to ONOS",
                                 onfail="Failed to form clusters to ONOS" )
        onosServiceResult = main.testSetUp.checkOnosService( main.Cluster )
        onosCliResult = main.testSetUp.startOnosClis( main.Cluster )
        activateResult = main.Cluster.active( 0 ).CLI.activateApp( main.additionalApp )
        result = formClusterResult and onosServiceResult and onosCliResult and activateResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=result,
                                 onpass="Successfully formed clusters to ONOS and started",
                                 onfail="Failed to form clusters to ONOS and started" )

    def CASE3( self, main ):
        """
            Checking the configuration of the ONOS with single-node ONOS.
            It will check :
                - the number of the node : They should only have 1 node.
                - App status : Only the first node should have additional app installed.
        """
        import time
        main.case( "Checking the configuration of the ONOS" )
        main.caseExplanation = "Checking the number of the nodes and apps"
        main.step( "Checking the number of the nodes" )
        main.log.info( "Sleep for " + str( main.startSleep ) + " to give enough time to ONOS")
        time.sleep( main.startSleep )
        result = main.funcs.checkingNumNodes( main, 1 )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=result,
                                 onpass="Successfully checking the nodes numbers of the ONOS",
                                 onfail="Failed to checking the nodes numbers of the ONOS" )
        main.step( "Checking the app status. Only the first node should have " +
                   main.additionalApp + " installed." )
        i = 0
        appResult = main.TRUE
        for cluster in main.Cluster.active():
            appResult = appResult and main.funcs.checkingApp( main, main.additionalApp, cluster, True if i == 0 else False )
            i += 1
        main.Cluster.active( 0 ).CLI.deactivateApp( main.additionalApp )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=appResult,
                                 onpass="Successfully checking the app status of the ONOS",
                                 onfail="Failed to checking the app status of the ONOS" )

    def CASE4( self, main ):
        """
            Checking the configuration of the ONOS with form-cluster.
            It will check :
                - the number of the node : They should only have 7 nodes.
                - state of the node.
                - App status : All the nodes should have additional app.
        """
        import time
        main.case( "Checking the configuration of the ONOS after form-cluster" )
        main.caseExplanation = "Checking the number of the nodes and apps"
        main.step( "Checking the number of the nodes" )
        main.log.info( "Sleep for " + str( main.startSleep ) + " to give enough time to ONOS")
        time.sleep( main.startSleep )
        result = main.funcs.checkingNumNodes( main, main.numNodes )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=result,
                                 onpass="Successfully checking the nodes numbers of the ONOS",
                                 onfail="Failed to checking the nodes numbers of the ONOS" )
        main.step( "Checking the status of the nodes" )
        nodeStatusResult = main.TRUE if main.Cluster.nodesCheck() else main.FALSE
        utilities.assert_equals( expect=main.TRUE,
                                 actual=nodeStatusResult,
                                 onpass="The status of the nodes were in READY as expected",
                                 onfail="The status of the nodes were NOT in READY as expected" )
        main.step( "Checking the app status. All nodes should have " +
                   main.additionalApp + " installed." )
        appResult = main.TRUE
        for cluster in main.Cluster.active():
            appResult = appResult and main.funcs.checkingApp( main, main.additionalApp, cluster, True )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=appResult,
                                 onpass="Successfully checking the app status of the ONOS",
                                 onfail="Failed to checking the app status of the ONOS" )

    def CASE5( self, main ):
        """
            Run simple mininet to check connectivity of ONOS clusters.
                - It will do ping all
                - It will compare topos between mininet and ONOS.
        """
        try:
            from tests.dependencies.topology import Topology
        except ImportError:
            main.log.error( "Topology not found exiting the test" )
            main.cleanAndExit()
        try:
            main.Topology
        except ( NameError, AttributeError ):
            main.Topology = Topology()
        main.case( "Starting 2x2 Tree Mininet and compare the Topology" )
        main.caseExplanation = "Starting 2x2 Mininet and assign ONOS controllers to switches."
        main.step( "Starting Mininet" )
        for ctrl in main.Cluster.runningNodes:
            main.mnTopo += " --controller remote,ip=" + ctrl.ipAddress
        startMnResult = main.Mininet1.startNet( mnCmd=main.mnTopo )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=startMnResult,
                                 onpass="Successfully started Mininet",
                                 onfail="Failed to start Mininet" )
        main.step( "Pingall hosts to confirm ONOS discovery" )
        pingResult = utilities.retry( f=main.Mininet1.pingall,
                                       retValue=main.FALSE,
                                       attempts=main.pingallRetry,
                                       sleep=main.pingallSleep )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=pingResult,
                                 onpass="Successfully discovered hosts",
                                 onfail="Failed to discover hosts" )
        main.Topology.compareTopos( main.Mininet1, main.topoCheckRetry )
