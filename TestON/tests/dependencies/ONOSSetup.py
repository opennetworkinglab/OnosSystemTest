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
import os


class ONOSSetup:

    def __init__( self ):
        self.default = ''
        try:
            main.persistentSetup
        except ( NameError, AttributeError ):
            main.persistentSetup = False

    def envSetupDescription( self, includeCaseDesc=True ):
        """
        Introduction part of the test. It will initialize some basic vairables.
        """
        if includeCaseDesc:
            main.case( "Constructing test variables and building ONOS package" )
            main.caseExplanation = "For loading from params file, and pull" + \
                                   " and build the latest ONOS package"
        main.step( "Constructing test variables" )
        try:
            from tests.dependencies.Cluster import Cluster
        except ImportError:
            main.log.error( "Cluster not found. exiting the test" )
            main.cleanAndExit()
        try:
            main.Cluster
        except ( NameError, AttributeError ):
            main.Cluster = Cluster( main.ONOScell.nodes, useDocker=main.ONOScell.useDocker )
        main.ONOSbench = main.Cluster.controllers[ 0 ].Bench
        main.testOnDirectory = re.sub( "(/tests)$", "", main.testsRoot )

    def gitPulling( self, includeCaseDesc=True ):
        """
        it will do git checkout or pull if they are enabled from the params file.
        """

        if includeCaseDesc:
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

    def envSetup( self, includeGitPull=True, includeCaseDesc=True ):
        """
        Description:
            some environment setup for the test.
        Required:
            * includeGitPull - if wish to git pulling function to be executed.
        Returns:
            Returns main.TRUE
        """
        if includeGitPull:
            self.gitPulling( includeCaseDesc )

        try:
            from tests.dependencies.Cluster import Cluster
        except ImportError:
            main.log.error( "Cluster not found. exiting the test" )
            main.cleanAndExit()
        try:
            main.Cluster
        except ( NameError, AttributeError ):
            main.Cluster = Cluster( main.ONOScell.nodes, useDocker=main.ONOScell.useDocker )

        main.cellData = {}  # For creating cell file

        return main.TRUE

    def envSetupException( self, error ):
        """
        Description:
            handles the exception that might occur from the environment setup.
        Required:
            * error - exception returned from except.
        """
        main.log.exception( error )
        main.cleanAndExit()

    def envSetupConclusion( self, stepResult ):
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

        if main.params[ 'GRAPH' ].get('jobName'):
            url = self.generateGraphURL( testname=main.params[ 'GRAPH' ][ 'jobName' ] )
        else:
            url = self.generateGraphURL()
        main.log.wiki( url )

        if not main.persistentSetup:
            # ONOS is not deployed by the test
            # TODO: Try to get commit another way, maybe container labels?
            #       Or try to link to deployment job?
            main.commit = main.ONOSbench.getVersion( report=True )

    def generateGraphURL( self, testname=main.TEST, width=525, height=350 ):
        """
        Description:
            Obtain the URL for the graph that corresponds to the test being run.
        """

        nodeCluster = main.params[ 'GRAPH' ][ 'nodeCluster' ]
        branch = main.ONOSbench.getBranchName()
        maxBuildsToShow = main.params[ 'GRAPH' ][ 'builds' ]

        return '<ac:structured-macro ac:name="html">\n' + \
                '<ac:plain-text-body><![CDATA[\n' + \
                '<img src="https://jenkins.onosproject.org/view/QA/job/postjob-' + \
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
            Set new number of controllers if it uses different number of nodes.
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
            # main.scale[ 0 ] determines the current number of ONOS controllers
            main.Cluster.setRunningNode( int( main.scale.pop( 0 ) ) )

    def killingAllAtomix( self, cluster, killRemoveMax, stopAtomix ):
        """
        Description:
            killing atomix. It will either kill the current runningnodes or
            max number of the nodes.
        Required:
            * cluster - the cluster driver that will be used.
            * killRemoveMax - The boolean that will decide either to kill
            only running nodes ( False ) or max number of nodes ( True ).
            * stopAtomix - If wish to stop atomix before killing it. True for
            enable stop, False for disable stop.
        Returns:
            Returns main.TRUE if successfully killing it.
        """
        main.log.info( "Safety check, killing all Atomix processes" )
        return cluster.killAtomix( killRemoveMax, stopAtomix )

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
            enable stop, False for disable stop.
        Returns:
            Returns main.TRUE if successfully killing it.
        """
        main.log.info( "Safety check, killing all ONOS processes" )
        return cluster.killOnos( killRemoveMax, stopOnos )

    def killingAllOnosDocker( self, cluster, killRemoveMax ):
        """
        Description:
            killing the onos docker images . It will either kill the
            current runningnodes or max number of the nodes.
        Required:
            * cluster - the cluster driver that will be used.
            * killRemoveMax - The boolean that will decide either to kill
            only running nodes ( False ) or max number of nodes ( True ).
        Returns:
            Returns main.TRUE if successfully killing it.
        """
        main.log.info( "Safety check, stopping all ONOS docker containers" )
        return cluster.dockerStop( killRemoveMax )

    def createApplyCell( self, cluster, newCell, cellName, cellApps,
                         mininetIp, useSSH, onosIps, installMax=False,
                         atomixClusterSize=None ):
        """
        Description:
            create new cell ( optional ) and apply it. It will also verify the
            cell.
        Required Arguments:
            * cluster - the cluster driver that will be used.
            * newCell - True for making a new cell and False for not making it.
            * cellName - The name of the cell.
            * cellApps - The onos apps string.
            * mininetIp - Mininet IP address.
            * useSSH - True for using ssh when creating a cell
            * onosIps - ip( s ) of the ONOS node( s ).
        Optional Arguments:
            * installMax
            * atomixClusterSize - The size of the atomix cluster. Defaults to same
                as ONOS Cluster size
        Returns:
            Returns main.TRUE if it successfully executed.
        """
        if atomixClusterSize is None:
            atomixClusterSize = len( cluster.runningNodes )
        if atomixClusterSize is 1:
            atomixClusterSize = len( cluster.controllers )
        atomixClusterSize = int( atomixClusterSize )
        cluster.setAtomixNodes( atomixClusterSize )
        atomixIps = [ node.ipAddress for node in cluster.atomixNodes ]
        main.log.info( "Atomix Cluster Size = {} ".format( atomixClusterSize ) )
        if newCell:
            cluster.createCell( cellName, cellApps, mininetIp, useSSH, onosIps,
                                atomixIps, installMax )
        main.step( "Apply cell to environment" )
        stepResult = cluster.applyCell( cellName )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully applied cell to " +
                                       "environment",
                                 onfail="Failed to apply cell to environment" )
        return stepResult

    def uninstallAtomix( self, cluster, uninstallMax ):
        """
        Description:
            uninstalling atomix and verify the result.
        Required:
            * cluster - a cluster driver that will be used.
            * uninstallMax - True for uninstalling max number of nodes
                False for uninstalling the current running nodes.
        Returns:
            Returns main.TRUE if it successfully uninstalled.
        """
        main.step( "Uninstalling Atomix" )
        atomixUninstallResult = cluster.uninstallAtomix( uninstallMax )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=atomixUninstallResult,
                                 onpass="Successfully uninstalled Atomix",
                                 onfail="Failed to uninstall Atomix" )
        return atomixUninstallResult

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
        onosUninstallResult = cluster.uninstallOnos( uninstallMax )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=onosUninstallResult,
                                 onpass="Successfully uninstalled ONOS package",
                                 onfail="Failed to uninstall ONOS package" )
        return onosUninstallResult

    def buildOnos( self, cluster ):
        """
        Description:
            build the onos using bazel build onos and verify the result
        Required:
            * cluster - the cluster driver that will be used.
        Returns:
            Returns main.TRUE if it successfully built.
        """
        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.bazelBuild()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=packageResult,
                                 onpass="Successfully created ONOS package",
                                 onfail="Failed to create ONOS package" )
        if not packageResult:
            main.cleanAndExit()
        return packageResult

    def buildDocker( self, cluster ):
        """
        Description:
            Build the latest docker
        Required:
            * cluster - the cluster driver that will be used.
        Returns:
            Returns main.TRUE if it successfully built.
        """
        main.step( "Building ONOS Docker image" )
        buildResult = cluster.dockerBuild()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=buildResult,
                                 onpass="Successfully created ONOS docker",
                                 onfail="Failed to create ONOS docker" )
        if not buildResult:
            main.cleanAndExit()
        return buildResult

    def installAtomix( self, cluster, parallel=True ):
        """
        Description:
            Installing atomix and verify the result
        Required:
            * cluster - the cluster driver that will be used.
            False for installing current running nodes only.
        Returns:
            Returns main.TRUE if it successfully installed
        """
        main.step( "Installing Atomix" )
        atomixInstallResult = main.TRUE

        atomixInstallResult = cluster.installAtomix( parallel )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=atomixInstallResult,
                                 onpass="Successfully installed Atomix",
                                 onfail="Failed to install Atomix" )
        if not atomixInstallResult:
            main.cleanAndExit()
        return atomixInstallResult

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

        cluster.installOnos( installMax, parallel )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=onosInstallResult,
                                 onpass="Successfully installed ONOS package",
                                 onfail="Failed to install ONOS package" )
        if not onosInstallResult:
            main.cleanAndExit()
        return onosInstallResult

    def startDocker( self, cluster, installMax, parallel=True ):
        """
        Description:
            Start onos docker containers and verify the result
        Required:
            * cluster - the cluster driver that will be used.
            * installMax - True for installing max number of nodes
            False for installing current running nodes only.
        Returns:
            Returns main.TRUE if it successfully installed
        """
        main.step( "Create Cluster Config" )
        configResult = cluster.genPartitions()
        utilities.assert_equals( expect=main.TRUE,
                                 actual=configResult,
                                 onpass="Successfully create cluster config",
                                 onfail="Failed to create cluster config" )

        # install atomix docker containers
        main.step( "Installing Atomix via docker containers" )
        atomixInstallResult = cluster.startAtomixDocker( parallel )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=atomixInstallResult,
                                 onpass="Successfully start atomix containers",
                                 onfail="Failed to start atomix containers" )

        main.step( "Installing ONOS via docker containers" )
        onosInstallResult = cluster.startONOSDocker( installMax, parallel )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=onosInstallResult,
                                 onpass="Successfully start ONOS containers",
                                 onfail="Failed to start ONOS containers" )
        if not onosInstallResult and atomixInstallResult:
            main.cleanAndExit()
        return onosInstallResult and atomixInstallResult

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
                                 onpass="Secured ONOS ssh",
                                 onfail="Failed to secure ssh" )
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

    def checkOnosNodes( self, cluster ):
        """
        Description:
            Checking if the onos nodes are in READY state
        Required:
            * cluster - the cluster driver that will be used.
        Returns:
            Returns main.TRUE if it successfully checked
        """
        main.step( "Checking ONOS nodes" )
        stepResult = utilities.retry( main.Cluster.nodesCheck,
                                      False,
                                      attempts=90 )

        utilities.assert_equals( expect=True,
                                 actual=stepResult,
                                 onpass="All ONOS nodes are in READY state",
                                 onfail="Not all ONOS nodes are in READY state" )

        if not stepResult:
            for ctrl in main.Cluster.active():
                main.log.debug( "{} components not ACTIVE: \n{}".format(
                    ctrl.name,
                    #  FIXME: This output has changed a lot
                    ctrl.CLI.sendline( "onos:scr-list | grep -v ACTIVE" ) ) )
            main.log.error( "Failed to start ONOS, stopping test" )
            main.cleanAndExit( msg="Failed to start ONOS: not all nodes are in READY state" )
        return main.TRUE

    def checkOnosApps( self, cluster, apps ):
        """
        Description:
            Checking if the onos applications are activated
        Required:
            * cluster - the cluster driver that will be used.
            * apps: list of applications that are expected to be activated
        Returns:
            Returns main.TRUE if it successfully checked
        """
        main.step( "Checking ONOS applications" )
        stepResult = utilities.retry( main.Cluster.appsCheck,
                                      False,
                                      args = [ apps ],
                                      sleep=5,
                                      attempts=90 )

        utilities.assert_equals( expect=True,
                                 actual=stepResult,
                                 onpass="All ONOS apps are activated",
                                 onfail="Not all ONOS apps are activated" )

        return main.TRUE if stepResult else main.FALSE

    def processList( self, functions, args ):
        if functions is not None:
            if isinstance( functions, list ):
                i = 0
                for f in functions:
                    f( *( args[ i ] ) ) if args is not None and args[ i ] is not None else f()
                    i += 1
            else:
                functions( *args ) if args is not None else functions()

    def ONOSSetUp( self, cluster, hasMultiNodeRounds=False, startOnosCli=True, newCell=True,
                   cellName="temp", cellApps="drivers", appPrefix="org.onosproject.",
                   mininetIp="", extraApply=None, applyArgs=None,
                   extraClean=None, cleanArgs=None, skipPack=False, installMax=False,
                   atomixClusterSize=None, useSSH=True, killRemoveMax=True, stopAtomix=False,
                   stopOnos=False, installParallel=True, cellApply=True,
                   includeCaseDesc=True, restartCluster=True ):
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
        Required Arguments:
            * cluster - the cluster driver that will be used.
        Optional Arguments:
            * hasMultiNodeRounds - True if the test is testing different set of nodes
            * startOnosCli - True if wish to start onos CLI.
            * newCell - True for making a new cell and False for not making it.
            * cellName - Name of the cell that will be used.
            * cellApps - The cell apps string. Will be overwritten by main.apps if it exists
            * appPrefix - Prefix of app names. Will use "org.onosproject." by default
            * mininetIp - Mininet IP address.
            * extraApply - Function( s ) that will be called before building ONOS. Default to None.
            * applyArgs - argument of the functon( s ) of the extraApply. Should be in list.
            * extraClean - Function( s ) that will be called after building ONOS. Defaults to None.
            * cleanArgs - argument of the functon( s ) of the extraClean. Should be in list.
            * skipPack - True if wish to skip some packing.
            * installMax - True if wish to install onos max number of nodes
                False if wish to install onos of running nodes only
            * atomixClusterSize - The number of Atomix nodes in the cluster.
                Defaults to None which will be the number of OC# nodes in the cell
            * useSSH - True for using ssh when creating a cell
            * killRemoveMax - True for removing/killing max number of nodes. False for
                removing/killing running nodes only.
            * stopAtomix - True if wish to stop atomix before killing it.
            * stopOnos - True if wish to stop onos before killing it.
            * restartCluster - True if wish to kill and restart atomix and onos clusters
        Returns:
            Returns main.TRUE if it everything successfully proceeded.
        """
        self.setNumCtrls( hasMultiNodeRounds )
        if not main.persistentSetup:
            if includeCaseDesc:
                main.case( "Starting up " + str( cluster.numCtrls ) +
                           " node(s) ONOS cluster" )
                main.caseExplanation = "Set up ONOS with " + str( cluster.numCtrls ) + \
                                       " node(s) ONOS cluster"

        main.log.info( "ONOS cluster size = " + str( cluster.numCtrls ) )
        cellResult = main.TRUE
        if cellApply:
            try:
                apps = main.apps
            except ( NameError, AttributeError ):
                apps = cellApps
            main.log.debug( "Apps: " + str( apps ) )
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
                                               cellName, apps,
                                               mininetIp, useSSH,
                                               tempOnosIp, installMax,
                                               atomixClusterSize )

        if not main.persistentSetup and restartCluster:
            atomixKillResult = self.killingAllAtomix( cluster, killRemoveMax, stopAtomix )
            onosKillResult = self.killingAllOnos( cluster, killRemoveMax, stopOnos )
            dockerKillResult = self.killingAllOnosDocker( cluster, killRemoveMax )
            killResult = atomixKillResult and onosKillResult
        else:
            killResult = main.TRUE

        if not main.persistentSetup and restartCluster:
            atomixUninstallResult = self.uninstallAtomix( cluster, killRemoveMax )
            onosUninstallResult = self.uninstallOnos( cluster, killRemoveMax )
            uninstallResult = atomixUninstallResult and onosUninstallResult
            self.processList( extraApply, applyArgs )

            packageResult = main.TRUE
            if not skipPack:
                if cluster.useDocker:
                    packageResult = self.buildDocker( cluster )
                else:
                    packageResult = self.buildOnos( cluster )

            if cluster.useDocker:
                installResult = self.startDocker( cluster, installMax, installParallel )
            else:
                atomixInstallResult = self.installAtomix( cluster, installParallel )
                onosInstallResult = self.installOnos( cluster, installMax, installParallel )
                installResult = atomixInstallResult and onosInstallResult

            preCLIResult = main.TRUE
            if cluster.useDocker:
                attachResult = cluster.attachToONOSDocker()
                prepareResult = cluster.prepareForCLI()

                preCLIResult = preCLIResult and attachResult and prepareResult

            self.processList( extraClean, cleanArgs )
            secureSshResult = self.setupSsh( cluster )
        else:
            packageResult = main.TRUE
            uninstallResult = main.TRUE
            installResult = main.TRUE
            secureSshResult = main.TRUE
            preCLIResult = main.TRUE

        onosServiceResult = main.TRUE
        if not cluster.useDocker:
            onosServiceResult = self.checkOnosService( cluster )
        elif main.persistentSetup:
            for ctrl in cluster.getRunningNodes():
                ctrl.inDocker = True

        onosCliResult = main.TRUE
        if startOnosCli:
            onosCliResult = self.startOnosClis( cluster )

        onosNodesResult = self.checkOnosNodes( cluster )

        externalAppsResult = main.TRUE
        if not main.persistentSetup and main.params.get( 'EXTERNAL_APPS' ):
            node = main.Cluster.controllers[0]
            for app, url in main.params[ 'EXTERNAL_APPS' ].iteritems():
                path, fileName = os.path.split( url )
                main.ONOSbench.onosApp( node.ipAddress, "reinstall!", fileName, appName=app, user=node.karafUser, password=node.karafPass )


        onosAppsResult = main.TRUE
        if not main.persistentSetup and cellApply:
            if apps:
                newApps = []
                appNames = apps.split( ',' )
                if cluster.useDocker:
                    node = main.Cluster.active( 0 )
                    for app in appNames:
                        appName = app if "org." in app else appPrefix + app
                        node.activateApp( appName )
                        newApps.append( appName )

                onosAppsResult = self.checkOnosApps( cluster, newApps )
            else:
                main.log.warn( "No apps were specified to be checked after startup" )

        return killResult and cellResult and packageResult and uninstallResult and \
               installResult and secureSshResult and onosServiceResult and onosCliResult and \
               onosNodesResult and onosAppsResult and preCLIResult
