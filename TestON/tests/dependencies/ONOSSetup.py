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
import re


class ONOSSetup:
    main = None

    def __init__( self ):
        self.default = ''

    def envSetupDescription( self ):
        """
        Introduction part of the test. It will initialize some basic vairables.
        """
        main.case( "Constructing test variables and building ONOS package" )
        main.step( "Constructing test variables" )
        main.caseExplanation = "For loading from params file, and pull" + \
                               " and build the latest ONOS package"
        try:
            from tests.dependencies.Cluster import Cluster
        except ImportError:
            main.log.error( "Cluster not found. exiting the test" )
            main.cleanAndExit()
        try:
            main.Cluster
        except ( NameError, AttributeError ):
            main.Cluster = Cluster( main.ONOScell.nodes )
        main.ONOSbench = main.Cluster.controllers[ 0 ].Bench
        main.testOnDirectory = re.sub( "(/tests)$", "", main.testDir )

    def gitPulling( self ):
        """
        it will do git checkout or pull if they are enabled from the params file.
        """
        main.case( "Pull onos branch and build onos on Teststation." )
        gitPull = main.params[ 'GIT' ][ 'pull' ]
        gitBranch = main.params[ 'GIT' ][ 'branch' ]
        if gitPull == 'True':
            main.step( "Git Checkout ONOS branch: " + gitBranch )
            stepResult = main.ONOSbench.gitCheckout( branch=gitBranch )
            utilities.assert_equals( expect=main.TRUE,
                                     actual=stepResult,
                                     onpass="Successfully checkout onos branch.",
                                     onfail="Failed to checkout onos branch. Exiting test..." )
            if not stepResult:
                main.cleanAndExit()

            main.step( "Git Pull on ONOS branch:" + gitBranch )
            stepResult = main.ONOSbench.gitPull()
            utilities.assert_equals( expect=main.TRUE,
                                     actual=stepResult,
                                     onpass="Successfully pull onos. ",
                                     onfail="Failed to pull onos. Exiting test ..." )
            if not stepResult:
                main.cleanAndExit()

        else:
            main.log.info( "Skipped git checkout and pull as they are disabled in params file" )

    def envSetup( self, includeGitPull=True ):
        """
        Description:
            some environment setup for the test.
        Required:
            * includeGitPull - if wish to git pulling function to be executed.
        Returns:
            Returns main.TRUE
        """
        if includeGitPull:
            self.gitPulling()

        try:
            from tests.dependencies.Cluster import Cluster
        except ImportError:
            main.log.error( "Cluster not found. exiting the test" )
            main.cleanAndExit()
        try:
            main.Cluster
        except ( NameError, AttributeError ):
            main.Cluster = Cluster( main.ONOScell.nodes )

        main.cellData = {}  # For creating cell file

        return main.TRUE

    def envSetupException( self, e ):
        """
        Description:
            handles the exception that might occur from the environment setup.
        Required:
            * includeGitPull - exceeption code e.
        """
        main.log.exception( e )
        main.cleanAndExit()

    def evnSetupConclusion( self, stepResult ):
        """
        Description:
            compare the result of the envSetup of the test.
        Required:
            * stepResult - Result of the envSetup.
        """
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully construct " +
                                        "test variables ",
                                 onfail="Failed to construct test variables" )

        url = self.generateGraphURL()
        main.log.wiki( url )

        main.commit = main.ONOSbench.getVersion( report=True )

    def generateGraphURL( self, width=525, height=350 ):
        """
        Description:
            Obtain the URL for the graph that corresponds to the test being run.
        """

        nodeCluster = main.params[ 'GRAPH' ][ 'nodeCluster' ]
        testname = main.TEST
        branch = main.ONOSbench.getBranchName()
        maxBuildsToShow = main.params[ 'GRAPH' ][ 'builds' ]

        return '<ac:structured-macro ac:name="html">\n' + \
                '<ac:plain-text-body><![CDATA[\n' + \
                '<img src="https://onos-jenkins.onlab.us/job/Pipeline_postjob_' + \
                nodeCluster + \
                '/lastSuccessfulBuild/artifact/' + \
                testname + \
                '_' + \
                branch + \
                '_' + \
                maxBuildsToShow + \
                '-builds_graph.jpg", alt="' + \
                testname + \
                '", style="width:' + \
                str( width ) + \
                'px;height:' + \
                str( height ) + \
                'px;border:0"' + \
                '>' + \
                ']]></ac:plain-text-body>\n' + \
                '</ac:structured-macro>\n'

    def setNumCtrls( self, hasMultiNodeRounds ):
        """
        Description:
            Set new number of controls if it uses different number of nodes.
            different number of nodes should be pre-defined in main.scale.
        Required:
            * hasMultiNodeRouds - if the test is testing different number of nodes.
        """
        if hasMultiNodeRounds:
            try:
                main.cycle
            except Exception:
                main.cycle = 0
            main.cycle += 1
            # main.scale[ 0 ] determines the current number of ONOS controller
            main.Cluster.setRunningNode( int( main.scale.pop( 0 ) ) )

    def killingAllOnos( self, cluster, killRemoveMax, stopOnos ):
        """
        Description:
            killing the onos. It will either kill the current runningnodes or
            max number of the nodes.
        Required:
            * cluster - the cluster driver that will be used.
            * killRemoveMax - The boolean that will decide either to kill
            only running nodes ( False ) or max number of nodes ( True ).
            * stopOnos - If wish to stop onos before killing it. True for
            enable stop , False for disable stop.
        Returns:
            Returns main.TRUE if successfully killing it.
        """
        main.log.info( "Safety check, killing all ONOS processes" )

        return cluster.kill( killRemoveMax, stopOnos )

    def createApplyCell( self, cluster, newCell, cellName, cellApps,
                         mininetIp, useSSH, ips, installMax=False ):
        """
        Description:
            create new cell ( optional ) and apply it. It will also verify the
            cell.
        Required:
            * cluster - the cluster driver that will be used.
            * newCell - True for making a new cell and False for not making it.
            * cellName - The name of the cell.
            * cellApps - The onos apps string.
            * mininetIp - Mininet IP address.
            * useSSH - True for using ssh when creating a cell
            * ips - ip( s ) of the node( s ).
        Returns:
            Returns main.TRUE if it successfully executed.
        """
        if newCell:
            cluster.createCell( cellName, cellApps, mininetIp, useSSH, ips )
        main.step( "Apply cell to environment" )
        stepResult = cluster.applyCell( cellName )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully applied cell to " +
                                       "environment",
                                 onfail="Failed to apply cell to environment" )
        return stepResult

    def uninstallOnos( self, cluster, uninstallMax ):
        """
        Description:
            uninstalling onos and verify the result.
        Required:
            * cluster - a cluster driver that will be used.
            * uninstallMax - True for uninstalling max number of nodes
            False for uninstalling the current running nodes.
        Returns:
            Returns main.TRUE if it successfully uninstalled.
        """
        main.step( "Uninstalling ONOS package" )
        onosUninstallResult = cluster.uninstall( uninstallMax )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=onosUninstallResult,
                                 onpass="Successfully uninstalled ONOS package",
                                 onfail="Failed to uninstall ONOS package" )
        return onosUninstallResult

    def buildOnos( self, cluster ):
        """
        Description:
            build the onos using buck build onos and verify the result
        Required:
            * cluster - the cluster driver that will be used.
        Returns:
            Returns main.TRUE if it successfully built.
        """
        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.buckBuild()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=packageResult,
                                 onpass="Successfully created ONOS package",
                                 onfail="Failed to create ONOS package" )
        return packageResult

    def installOnos( self, cluster, installMax, parallel=True ):
        """
        Description:
            Installing onos and verify the result
        Required:
            * cluster - the cluster driver that will be used.
            * installMax - True for installing max number of nodes
            False for installing current running nodes only.
        Returns:
            Returns main.TRUE if it successfully installed
        """
        main.step( "Installing ONOS package" )
        onosInstallResult = main.TRUE

        cluster.install( installMax, parallel )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=onosInstallResult,
                                 onpass="Successfully installed ONOS package",
                                 onfail="Failed to install ONOS package" )
        if not onosInstallResult:
            main.cleanAndExit()
        return onosInstallResult

    def setupSsh( self, cluster ):
        """
        Description:
            set up ssh to the onos and verify the result
        Required:
            * cluster - the cluster driver that will be used.
        Returns:
            Returns main.TRUE if it successfully setup the ssh to
            the onos.
        """
        main.step( "Set up ONOS secure SSH" )
        secureSshResult = cluster.ssh()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=secureSshResult,
                                 onpass="Test step PASS",
                                 onfail="Test step FAIL" )
        return secureSshResult

    def checkOnosService( self, cluster ):
        """
        Description:
            Checking if the onos service is up and verify the result
        Required:
            * cluster - the cluster driver that will be used.
        Returns:
            Returns main.TRUE if it successfully checked
        """
        main.step( "Checking ONOS service" )
        stepResult = cluster.checkService()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ONOS service is ready on all nodes",
                                 onfail="ONOS service did not start properly on all nodes" )
        return stepResult

    def startOnosClis( self, cluster ):
        """
        Description:
            starting Onos using onosCli driver and verify the result
        Required:
            * cluster - the cluster driver that will be used.
        Returns:
            Returns main.TRUE if it successfully started. It will exit
            the test if not started properly.
        """
        main.step( "Starting ONOS CLI sessions" )
        startCliResult = cluster.startCLIs()
        if not startCliResult:
            main.log.info( "ONOS CLI did not start up properly" )
            main.cleanAndExit()
        else:
            main.log.info( "Successful CLI startup" )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=startCliResult,
                                 onpass="Successfully start ONOS cli",
                                 onfail="Failed to start ONOS cli" )
        return startCliResult

    def processList( self, functions, args ):
        if functions is not None:
            if isinstance( functions, list ):
                i = 0
                for f in functions:
                    f( *( args[ i ] ) ) if args is not None and args[ i ] is not None else f()
                    i += 1
            else:
                functions( *args ) if args is not None else functions()

    def ONOSSetUp( self, cluster, hasMultiNodeRounds=False, startOnos=True, newCell=True,
                   cellName="temp", cellApps="drivers", mininetIp="", removeLog=False, extraApply=None, applyArgs=None,
                   extraClean=None, cleanArgs=None, skipPack=False, installMax=False, useSSH=True,
                   killRemoveMax=True, stopOnos=False, installParallel=True, cellApply=True ):
        """
        Description:
            Initial ONOS setting up of the tests. It will also verify the result of each steps.
            The procedures will be:
                killing onos
                creating ( optional ) /applying cell
                removing raft logs ( optional )
                uninstalling onos
                extra procedure to be applied( optional )
                building onos
                installing onos
                extra cleanup to be applied ( optional )
                setting up ssh to the onos
                checking the onos service
                starting onos
        Required:
            * cluster - the cluster driver that will be used.
            * hasMultiNodeRouds - True if the test is testing different set of nodes
            * startOnos - True if wish to start onos.
            * newCell - True for making a new cell and False for not making it.
            * cellName - Name of the cell that will be used.
            * cellApps - The cell apps string.
            * mininetIp - Mininet IP address.
            * removeLog - True if wish to remove raft logs
            * extraApply - Function( s ) that will be called before building ONOS. Default to None.
            * applyArgs - argument of the functon( s ) of the extraApply. Should be in list.
            * extraClean - Function( s ) that will be called after building ONOS. Defaults to None.
            * cleanArgs - argument of the functon( s ) of the extraClean. Should be in list.
            * skipPack - True if wish to skip some packing.
            * installMax - True if wish to install onos max number of nodes
            False if wish to install onos of running nodes only
            * useSSH - True for using ssh when creating a cell
            * killRemoveMax - True for removing/killing max number of nodes. False for
            removing/killing running nodes only.
            * stopOnos - True if wish to stop onos before killing it.
        Returns:
            Returns main.TRUE if it everything successfully proceeded.
        """
        self.setNumCtrls( hasMultiNodeRounds )

        main.case( "Starting up " + str( cluster.numCtrls ) +
                   " node(s) ONOS cluster" )
        main.caseExplanation = "Set up ONOS with " + str( cluster.numCtrls ) + \
                               " node(s) ONOS cluster"
        killResult = self.killingAllOnos( cluster, killRemoveMax, stopOnos )

        main.log.info( "NODE COUNT = " + str( cluster.numCtrls ) )
        cellResult = main.TRUE
        packageResult = main.TRUE
        onosCliResult = main.TRUE
        if cellApply:
            tempOnosIp = []
            for ctrl in cluster.runningNodes:
                tempOnosIp.append( ctrl.ipAddress )
            if mininetIp == "":
                mininetIp = "localhost"
                for key, value in main.componentDictionary.items():
                    if value['type'] in ['MininetCliDriver', 'RemoteMininetDriver'] and hasattr( main, key ):
                        mininetIp = getattr( main, key ).ip_address
                        break
            cellResult = self.createApplyCell( cluster, newCell,
                                               cellName, cellApps,
                                               mininetIp, useSSH,
                                               tempOnosIp, installMax )

        if removeLog:
            main.log.info("Removing raft logs")
            main.ONOSbench.onosRemoveRaftLogs()
        onosUninstallResult = self.uninstallOnos( cluster, killRemoveMax )
        self.processList( extraApply, applyArgs )

        if not skipPack:
            packageResult = self.buildOnos(cluster)

        onosInstallResult = self.installOnos( cluster, installMax, installParallel )

        self.processList( extraClean, cleanArgs )
        secureSshResult = self.setupSsh( cluster )

        onosServiceResult = self.checkOnosService( cluster )

        if startOnos:
            onosCliResult = self.startOnosClis( cluster )

        return killResult and cellResult and packageResult and onosUninstallResult and \
               onosInstallResult and secureSshResult and onosServiceResult and onosCliResult
