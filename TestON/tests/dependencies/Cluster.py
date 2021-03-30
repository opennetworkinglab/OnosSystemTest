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
import json
class Cluster():

    def __str__( self ):
        return self.name

    def __repr__( self ):
        controllers = []
        runningNodes = self.getRunningNodes()
        atomixNodes = []
        for ctrl in self.controllers:
            controllers.append( "{%s:%s, %s - %s}" % ( ctrl.name,
                                                       ctrl.ipAddress,
                                                       "Configured" if ctrl in runningNodes else "Not Configured",
                                                       "Active" if ctrl.active else "Inactive" ) )
        for node in self.atomixNodes:
            atomixNodes.append( "{%s:%s}" % ( node.name, node.ipAddress ) )
        return "%s[%s; Atomix Nodes:%s]" % ( self.name, ", ".join( controllers ), ", ".join( atomixNodes ) )

    def __init__( self, ctrlList=[], name="Cluster", useDocker=False ):
        """
            controllers : All the nodes
            runningNodes : Node that are specifically running from the test.
                ie ) When the test is testing different number of nodes on each
                    run.
            numCtrls : number of runningNodes
            maxCtrls : number of controllers
        """
        self.controllers = ctrlList
        self.runningNodes = ctrlList
        self.numCtrls = len( self.runningNodes )
        self.maxCtrls = len( self.controllers )
        self.name = str( name )
        self.atomixNodes = ctrlList
        self.iterator = iter( self.active() )
        self.useDocker = useDocker
        clusterParams = main.params.get( "CLUSTER", {} )
        self.dockerSkipBuild = clusterParams.get( "dockerSkipBuild", False )
        self.dockerBuildCmd = clusterParams.get( "dockerBuildCmd", None )
        self.dockerBuildTimeout = int( clusterParams.get( "dockerBuildTimeout", 600 ) )
        self.dockerFilePath = clusterParams.get( "dockerFilePath", None )
        self.dockerImageTag = clusterParams.get( "dockerImageTag", None )
        self.dockerOptions = clusterParams.get( "dockerOptions", "" )
        self.atomixImageTag = clusterParams.get( "atomixImageTag", None )
        self.atomixOptions = clusterParams.get( "atomixOptions", "" )

    def fromNode( self, ctrlList ):
        """
        Helper function to get a specific list of controllers
        Required Arguments:
        * ctrlList - The list of controllers to return. This can be either an index or a keyword
            Index | Keyword   | List returned
            0     | "all"     | self.controllers
            1     | "running" | self.runningNodes
            2     | "active   | self.active()

        Throws a ValueError exception if ctrlList value is not recognized
        """
        # TODO: Add Atomix Nodes?
        if isinstance( ctrlList, str ):
            ctrlList = ctrlList.lower()
        if ctrlList == 0 or ctrlList == "all":
            return self.controllers
        elif ctrlList == 1 or ctrlList == "running":
            return self.runningNodes
        elif ctrlList == 2 or ctrlList == "active":
            return self.active()
        else:
            raise ValueError( "Unknown argument: {}".format( ctrlList ) )

    def getIps( self, activeOnly=False, allNode=False ):
        """
        Description:
            get the list of the ip. Default to get ips of running nodes.
        Required:
            * activeOnly - True for getting ips of active nodes
            * allNode - True for getting ips of all nodes
        Returns:
            Retruns ips of active nodes if activeOnly is True.
            Returns ips of all nodes if allNode is True.
        """
        ips = []
        if allNode:
            nodeList = self.controllers
        else:
            if activeOnly:
                nodeList = self.active()
            else:
                nodeList = self.runningNodes

        for ctrl in nodeList:
            ips.append( ctrl.ipAddress if 'localhost' not in ctrl.ipAddress else ctrl.address )

        return ips

    def clearActive( self ):
        """
        Description:
            Sets the activeness of each cluster node to be False
        """
        for ctrl in self.controllers:
            ctrl.active = False

    def getRunningPos( self ):
        """
        Description:
            get the position of the active running nodes.
        Required:
        Returns:
            Retruns the list of the position of the active
            running nodes.
        """
        return [ ctrl.pos for ctrl in self.runningNodes
                 if ctrl.active ]

    def setRunningNode( self, numCtrls ):
        """
        Description:
            Set running nodes of n number of nodes.
            It will create new list of runningNodes.
            If numCtrls is a list, it will add the nodes of the
            list.
        Required:
            * numCtrls - number of nodes to be set.
        Returns:
        """
        self.runningNodes = []
        for i in numCtrls if isinstance( numCtrls, list ) else range( numCtrls ):
            self.runningNodes.append( self.controllers[ i ] )
        self.numCtrls = len( numCtrls ) if isinstance( numCtrls, list ) else numCtrls

    def setAtomixNodes( self, nodes ):
        """
        Description:
            Sets the list of Atomix nodes for the cluster
            If nodes is a list, it will add the nodes of the list.
            If nodes is an int, the function will set the Atomix nodes
            to be the first n in the list of controllers.
        Required:
            * nodes - number of nodes to be set, or a list of nodes to set
        Returns:
        """
        self.atomixNodes = []
        for i in nodes if isinstance( nodes, list ) else range( nodes ):
            self.atomixNodes.append( self.controllers[ i ] )

    def getControllers( self, node=None ):
        """
        Description:
            Get the list of all controllers in a cluster or a controller at an index in the list
        Optional Arguments:
            * node - position of the node to get from the list of controllers.
        Returns:
            Return a list of controllers in the cluster if node is None
            if not, it will return the controller at the given index.
        """
        result = self.controllers
        return result if node is None else result[ node % len( result ) ]

    def getRunningNodes( self, node=None ):
        """
        Description:
            Get the list of all controllers in a cluster that should be running or
            a controller at an index in the list
        Optional Arguments:
            * node - position of the node to get from the list of controllers.
        Returns:
            Return a list of controllers in the cluster if node is None
            if not, it will return the controller at the given index.
        """
        result = self.runningNodes
        return result if node is None else result[ node % len( result ) ]

    def active( self, node=None ):
        """
        Description:
            Get the list of all active controllers in a cluster or
            a controller at an index in the list
        Optional Arguments:
            * node - position of the node to get from the list of controllers.
        Returns:
            Return a list of controllers in the cluster if node is None
            if not, it will return the controller at the given index.
        """
        result = [ ctrl for ctrl in self.runningNodes
                      if ctrl.active ]
        return result if node is None else result[ node % len( result ) ]

    def next( self ):
        """
        An iterator for the cluster's active controllers that
        resets when there are no more elements.

        Returns the next controller in the cluster
        """
        try:
            node = self.iterator.next()
            assert node.active
            return node
        except ( StopIteration, AssertionError ):
            self.reset()
            try:
                return self.iterator.next()
            except StopIteration:
                raise RuntimeError( "There are no active nodes in the cluster" )

    def reset( self ):
        """
        Resets the cluster iterator.

        This should be used whenever a node's active state is changed
        and is also used internally when the iterator has been exhausted.
        """
        self.iterator = iter( self.active() )

    def createCell( self, cellName, cellApps, mininetIp, useSSH, onosIps,
                    atomixIps, installMax=False ):
        """
        Description:
            create a new cell
        Required:
            * cellName - The name of the cell.
            * cellApps - The ONOS apps string.
            * mininetIp - Mininet IP address.
            * useSSH - True for using ssh when creating a cell
            * onosIps - ip( s ) of the ONOS node( s ).
            * atomixIps - ip( s ) of the Atomix node( s ).

        Returns:
        """
        self.command( "createCellFile",
                      args=[ main.ONOSbench.ip_address,
                             cellName,
                             mininetIp,
                             cellApps,
                             onosIps,
                             atomixIps,
                             main.ONOScell.nodeUser,
                             useSSH ],
                      specificDriver=1,
                      getFrom="all" if installMax else "running" )

    def uninstallAtomix( self, uninstallMax ):
        """
        Description:
            uninstalling atomix
        Required:
            * uninstallMax - True for uninstalling max number of nodes
            False for uninstalling the current running nodes.
        Returns:
            Returns main.TRUE if it successfully uninstalled.
        """
        result = main.TRUE
        uninstallResult = self.command( "atomixUninstall",
                                        kwargs={ "nodeIp": "ipAddress" },
                                        specificDriver=1,
                                        getFrom="all" if uninstallMax else "running",
                                        funcFromCtrl=True )
        for uninstallR in uninstallResult:
            result = result and uninstallR
        return result

    def uninstallOnos( self, uninstallMax ):
        """
        Description:
            uninstalling onos
        Required:
            * uninstallMax - True for uninstalling max number of nodes
            False for uninstalling the current running nodes.
        Returns:
            Returns main.TRUE if it successfully uninstalled.
        """
        result = main.TRUE
        uninstallResult = self.command( "onosUninstall",
                                        kwargs={ "nodeIp": "ipAddress" },
                                        specificDriver=1,
                                        getFrom="all" if uninstallMax else "running",
                                        funcFromCtrl=True )
        for uninstallR in uninstallResult:
            result = result and uninstallR
        return result

    def applyCell( self, cellName, installMax=False ):
        """
        Description:
            apply the cell with cellName. It will also verify the
            cell.
        Required:
            * cellName - The name of the cell.
        Returns:
            Returns main.TRUE if it successfully set and verify cell.
        """
        result = main.TRUE
        setCellResult = self.command( "setCell",
                                      args=[ cellName ],
                                      specificDriver=1,
                                      getFrom="all" )
        for i in range( len( setCellResult ) ):
            result = result and setCellResult[ i ]
        benchCellResult = main.ONOSbench.setCell( cellName )
        result = result and benchCellResult
        if not self.useDocker:
            verifyResult = self.command( "verifyCell",
                                         specificDriver=1,
                                         getFrom="all" )
            for i in range( len( verifyResult ) ):
                result = result and verifyResult[ i ]
        return result

    def checkService( self ):
        """
        Description:
            Checking if the onos service is up. If not, it will
            start the onos service manually.
        Required:
        Returns:
            Returns main.TRUE if it successfully checked
        """
        getFrom = "running"
        onosIsUp = main.TRUE
        onosUp = self.command( "isup",
                                 args=[ "ipAddress" ],
                                 specificDriver=1,
                                 getFrom=getFrom,
                                 funcFromCtrl=True )
        ctrlList = self.fromNode( getFrom )
        for i in range( len( onosUp ) ):
            ctrl = ctrlList[ i ]
            onosIsUp = onosIsUp and onosUp[ i ]
            if onosUp[ i ] == main.TRUE:
                main.log.info( ctrl.name + " is up and ready" )
            else:
                main.log.warn( ctrl.name + " may not be up." )
        return onosIsUp

    def killAtomix( self, killMax, stopAtomix ):
        """
        Description:
            killing atomix. It will either kill the current runningnodes or
            max number of the nodes.
        Required:
            * killRemoveMax - The boolean that will decide either to kill
            only running nodes ( False ) or max number of nodes ( True ).
            * stopAtomix - If wish to atomix onos before killing it. True for
            enable stop, False for disable stop.
        Returns:
            Returns main.TRUE if successfully killing it.
        """
        result = main.TRUE
        killResult = self.command( "atomixKill",
                                   args=[ "ipAddress" ],
                                   specificDriver=1,
                                   getFrom="all" if killMax else "running",
                                   funcFromCtrl=True )
        for i in range( len( killResult ) ):
            result = result and killResult[ i ]
        return result

    def killOnos( self, killMax, stopOnos ):
        """
        Description:
            killing the onos. It will either kill the current runningnodes or
            max number of the nodes.
        Required:
            * killRemoveMax - The boolean that will decide either to kill
            only running nodes ( False ) or max number of nodes ( True ).
            * stopOnos - If wish to stop onos before killing it. True for
            enable stop , False for disable stop.
        Returns:
            Returns main.TRUE if successfully killing it.
        """
        getFrom = "all" if killMax else "running"
        result = main.TRUE
        killResult = self.command( "onosKill",
                                   args=[ "ipAddress" ],
                                   specificDriver=1,
                                   getFrom=getFrom,
                                   funcFromCtrl=True )
        ctrlList = self.fromNode( getFrom )
        for i in range( len( killResult ) ):
            result = result and killResult[ i ]
            ctrlList[ i ].active = False
        return result

    def dockerStop( self, killMax, atomix=True ):
        """
        Description:
            killing the onos docker containers. It will either kill the
            current runningnodes or max number of the nodes.
        Required:
            * killRemoveMax - The boolean that will decide either to kill
            only running nodes ( False ) or max number of nodes ( True ).
        Returns:
            Returns main.TRUE if successfully killing it.
        """
        getFrom = "all" if killMax else "running"
        result = main.TRUE
        stopResult = self.command( "dockerStop",
                                   args=[ "name" ],
                                   specificDriver=4,
                                   getFrom=getFrom,
                                   funcFromCtrl=True )
        ctrlList = self.fromNode( getFrom )
        for i in range( len( stopResult ) ):
            result = result and stopResult[ i ]
            ctrlList[ i ].active = False
        atomixResult = main.TRUE
        if atomix:
            atomixResult = self.stopAtomixDocker( killMax )
        return result and atomixResult

    def dockerBuild( self, pull=True ):
        """
        Description:
        Build ONOS docker image
        Optional:
            * pull - Try to pull latest image before building
        Returns:
            Returns main.TRUE if successfully killing it.
        """
        getFrom = "all"
        result = main.TRUE
        atomixResult = []
        buildResult = []
        if self.atomixImageTag:
            atomixResult = self.command( "dockerPull",
                                         args=[ self.atomixImageTag ],
                                         specificDriver=4,
                                         getFrom=getFrom,
                                         funcFromCtrl=False )
        if not self.dockerImageTag:
            main.log.error( "No image given, exiting test" )
            return main.FALSE
        if pull and self.dockerImageTag:
            buildResult = self.command( "dockerPull",
                                        args=[ self.dockerImageTag ],
                                        specificDriver=4,
                                        getFrom=getFrom,
                                        funcFromCtrl=False )
            for i in range( len( buildResult ) ):
                result = result and buildResult[ i ]
        if self.dockerSkipBuild:
            return main.TRUE
        if not result and self.dockerBuildCmd:
            buildResult = self.command( "makeDocker",
                                        args=[ self.dockerFilePath, self.dockerBuildCmd ],
                                        kwargs={ "timeout": self.dockerBuildTimeout,
                                                 "prompt": "Successfully tagged %s" % self.dockerImageTag },
                                        specificDriver=4,
                                        getFrom=getFrom,
                                        funcFromCtrl=False )

        elif not result:
            buildResult = self.command( "dockerBuild",
                                        args=[ self.dockerFilePath, self.dockerImageTag ],
                                        kwargs={ "timeout": self.dockerBuildTimeout,
                                                 "pull": pull },
                                        specificDriver=4,
                                        getFrom=getFrom,
                                        funcFromCtrl=False )
        for i in range( len( atomixResult ) ):
            result = result and atomixResult[ i ]
        for i in range( len( buildResult ) ):
            result = result and buildResult[ i ]
        return result

    def ssh( self ):
        """
        Description:
            set up ssh to the onos
        Required:
        Returns:
            Returns main.TRUE if it successfully setup the ssh to
            the onos.
        """
        result = main.TRUE
        if self.useDocker:
            driver = 2
            kwargs = { "userName": "karafUser",
                       "userPWD": "karafPass" }
        else:
            driver = 1
            kwargs = { "node": "ipAddress" }
        sshResult = self.command( "onosSecureSSH",
                                   kwargs=kwargs,
                                   specificDriver=driver,
                                   getFrom="running",
                                   funcFromCtrl=True )
        for sshR in sshResult:
            result = result and sshR
        return result

    def installAtomix( self, installParallel=True ):
        """
        Description:
            Installing Atomix.
        Required:
        Returns:
            Returns main.TRUE if it successfully installed
        """
        result = main.TRUE
        if self.useDocker:
            # We will do this as part of startDocker
            return result
        threads = []
        i = 0
        for ctrl in self.atomixNodes:
            options = "-f"
            if installParallel:
                t = main.Thread( target=ctrl.Bench.atomixInstall,
                                 name="atomix-install-" + ctrl.name,
                                 kwargs={ "node" : ctrl.ipAddress,
                                          "options" : options } )
                threads.append( t )
                t.start()
            else:
                result = result and \
                            main.ONOSbench.atomixInstall( node=ctrl.ipAddress, options=options )
            i += 1
        if installParallel:
            for t in threads:
                t.join()
                result = result and t.result
        return result

    def installOnos( self, installMax=True, installParallel=True, retries=5 ):
        """
        Description:
            Installing onos.
        Required:
            * installMax - True for installing max number of nodes
            False for installing current running nodes only.
        Returns:
            Returns main.TRUE if it successfully installed
        """
        result = main.TRUE
        threads = []
        i = 0
        for ctrl in self.controllers if installMax else self.runningNodes:
            options = "-f"
            if installMax and i >= self.numCtrls:
                options = "-nf"
            args = [ ctrl.Bench.onosInstall, main.FALSE ]
            kwargs={ "node" : ctrl.ipAddress,
                     "options" : options }
            if installParallel:
                t = main.Thread( target=utilities.retry,
                                 name="onos-install-" + ctrl.name,
                                 args=args,
                                 kwargs={ 'kwargs': kwargs,
                                          'attempts': retries } )

                threads.append( t )
                t.start()
            else:
                result = result and \
                            utilities.retry( args=args, kwargs=kwargs, attempts=retries )
            i += 1
        if installParallel:
            for t in threads:
                t.join()
                result = result and t.result
        return result

    def startONOSDocker( self, installMax=True, installParallel=True ):
        """
        Description:
            Installing onos via docker containers.
        Required:
            * installMax - True for installing max number of nodes
            False for installing current running nodes only.
        Returns:
            Returns main.TRUE if it successfully installed
        """
        result = main.TRUE
        threads = []
        for ctrl in self.controllers if installMax else self.runningNodes:
            if installParallel:
                t = main.Thread( target=ctrl.server.dockerRun,
                                 name="onos-run-docker-" + ctrl.name,
                                 args=[ self.dockerImageTag, ctrl.name ],
                                 kwargs={ "options" : self.dockerOptions } )
                threads.append( t )
                t.start()
            else:
                result = result and \
                            ctrl.server.dockerRun( self.dockerImageTag,
                                                   ctrl.name,
                                                   options=self.dockerOptions )
        if installParallel:
            for t in threads:
                t.join()
                result = result and t.result
        return result

    def startONOSDockerNode( self, node ):
        """
        Description:
            Installing onos via docker container on a specific node.
        Required:
            * node - the node to install ONOS on, given in index of runningNodes
        Returns:
            Returns main.TRUE if it successfully installed
        """
        ctrl = self.runningNodes[ node ]
        result = ctrl.server.dockerRun( self.dockerImageTag,
                                        ctrl.name,
                                        options=self.dockerOptions )
        return result

    def startAtomixDocker( self, installParallel=True ):
        """
        Description:
            Installing atomix via docker containers.
        Required:
            * installParallel - True for installing atomix in parallel.
        Returns:
            Returns main.TRUE if it successfully installed
        """
        result = main.TRUE
        threads = []
        for ctrl in self.atomixNodes:
            if installParallel:
                t = main.Thread( target=ctrl.server.dockerRun,
                                 name="atomix-run-docker-" + ctrl.name,
                                 args=[ self.atomixImageTag, "atomix-" + ctrl.name ],
                                 kwargs={ "options" : main.params['CLUSTER']['atomixOptions'],
                                          "imageArgs": " --config /opt/atomix/conf/atomix.json --ignore-resources"} )
                threads.append( t )
                t.start()
            else:
                result = result and \
                            ctrl.server.dockerRun( self.atomixImageTag,
                                                   "atomix-" + ctrl.name,
                                                   options=main.params['CLUSTER']['atomixOptions'] )
        if installParallel:
            for t in threads:
                t.join()
                result = result and t.result
        return result

    def stopAtomixDocker( self, killMax=True, installParallel=True ):
        """
        Description:
            Stoping all atomix containers
        Required:
            * killMax - True for stoping max number of nodes
            False for stoping current running nodes only.
        Returns:
            Returns main.TRUE if it successfully stoped
        """
        result = main.TRUE
        threads = []
        for ctrl in self.controllers if killMax else self.atomixNodes:
            if installParallel:
                t = main.Thread( target=ctrl.server.dockerStop,
                                 name="atomix-stop-docker-" + ctrl.name,
                                 args=[ "atomix-" + ctrl.name ] )
                threads.append( t )
                t.start()
            else:
                result = result and \
                            ctrl.server.dockerStop( "atomix-" + ctrl.name )
        if installParallel:
            for t in threads:
                t.join()
                result = result and t.result
        return result

    def genPartitions( self, path="/tmp/cluster.json" ):
        """
        Description:
           Create cluster config and move to each onos server
        Required:
            * installMax - True for installing max number of nodes
            False for installing current running nodes only.
        Returns:
            Returns main.TRUE if it successfully installed
        """
        result = main.TRUE
        # move files to onos servers
        for ctrl in self.atomixNodes:
            localAtomixFile = ctrl.ip_address + "-atomix.json"
            result = result and main.ONOSbench.generateAtomixConfig( ctrl.server.ip_address, path=localAtomixFile )
            result = result and main.ONOSbench.scp( ctrl.server,
                                                    localAtomixFile,
                                                    "/tmp/atomix.json",
                                                    direction="to" )
        for ctrl in self.controllers:
            localOnosFile = ctrl.ip_address + "-cluster.json"
            result = result and main.ONOSbench.generateOnosConfig( ctrl.server.ip_address, path=localOnosFile )
            result = result and main.ONOSbench.scp( ctrl.server,
                                                    localOnosFile,
                                                    path,
                                                    direction="to" )
        return result

    def startCLIs( self ):
        """
        Description:
            starting Onos using onosCli driver
        Required:
        Returns:
            Returns main.TRUE if it successfully started.
        """
        getFrom = "running"
        result = main.TRUE
        cliResults = self.command( "startOnosCli",
                                   args=[ "ipAddress" ],
                                   kwargs= { "karafTimeout": "karafTimeout" },
                                   specificDriver=2,
                                   getFrom=getFrom,
                                   funcFromCtrl=True )
        ctrlList = self.fromNode( getFrom )
        for i in range( len( cliResults ) ):
            result = result and cliResults[ i ]
            ctrlList[ i ].active = True
        return result

    def nodesCheck( self ):
        """
        Description:
            Checking if all the onos nodes are in READY state
        Required:
        Returns:
            Returns True if it successfully checked
        """
        import time
        results = True
        nodesOutput = self.command( "nodes", specificDriver=2 )
        if None in nodesOutput:
            time.sleep(60)
            nodesOutput = self.command( "nodes", specificDriver=2 )
            main.log.debug(nodesOutput)
            if None in nodesOutput:
                return False
        try:
            self.command( "getAddress", specificDriver=2 )
        except ( ValueError, TypeError ):
            main.log.error( "Error parsing summary output" )
            currentResult = False
            return currentResult
        ips = sorted( self.getIps( activeOnly=True ) )
        for i in nodesOutput:
            try:
                current = json.loads( i )
                activeIps = []
                currentResult = False
                for node in current:
                    if node[ 'state' ] == 'READY':
                        activeIps.append( node[ 'ip' ] )
                activeIps.sort()
                if ips == activeIps:
                    currentResult = True
                else:
                    main.log.warn( "Expected {} != found {}".format( ips, activeIps ) )
            except ( ValueError, TypeError ):
                main.log.error( "Error parsing nodes output" )
                main.log.warn( repr( i ) )
                currentResult = False
            results = results and currentResult
        # Check to make sure all bundles are started
        bundleOutput = self.command( "sendline", args=[ "bundle:list" ] )
        for i in bundleOutput:
            if "START LEVEL 100" in i:
                currentResult = True
            else:
                currentResult = False
                main.log.warn( "Node's bundles not fully started" )
                main.log.debug( i )
            results = results and currentResult
        return results

    def appsCheck( self, apps ):
        """
        Description:
            Checking if all the applications are activated
        Required:
            apps: list of applications that are expected to be activated
        Returns:
            Returns True if it successfully checked
        """
        results = True
        for app in apps:
            states = self.command( "appStatus",
                                   args=[ app ],
                                   specificDriver=2 )
            for i in range( len( states ) ):
                ctrl = self.controllers[ i ]
                if states[ i ] == "ACTIVE":
                    results = results and True
                    main.log.info( "{}: {} is activated".format( ctrl.name, app ) )
                else:
                    results = False
                    main.log.warn( "{}: {} is in {} state".format( ctrl.name, app, states[ i ] ) )
        return results

    def attachToONOSDocker( self ):
        """
        Description:
            connect to onos docker using onosCli driver
        Required:
        Returns:
            Returns main.TRUE if it successfully started.
        """
        getFrom = "running"
        result = main.TRUE
        execResults = self.command( "dockerExec",
                                    args=[ "name" ],
                                    kwargs={ "dockerPrompt": "dockerPrompt" },
                                    specificDriver=2,
                                    getFrom=getFrom,
                                    funcFromCtrl=True )
        ctrlList = self.fromNode( getFrom )
        for i in range( len( execResults ) ):
            result = result and execResults[ i ]
            ctrlList[ i ].active = True
        return result

    def prepareForCLI( self ):
        """
        Description:
            prepare docker to connect to the onos cli
        Required:
        Returns:
            Returns main.TRUE if it successfully started.
        """
        getFrom = "running"
        for ctrl in self.getRunningNodes():
            ctrl.CLI.inDocker = True
        result = main.TRUE
        execResults = self.command( "prepareForCLI",
                                    specificDriver=2,
                                    getFrom=getFrom,
                                    funcFromCtrl=True )
        ctrlList = self.fromNode( getFrom )
        for i in range( len( execResults ) ):
            result = result and execResults[ i ]
            ctrlList[ i ].active = True
        return result

    def printResult( self, results, activeList, logLevel="debug" ):
        """
        Description:
            Print the value of the list.
        Required:
            * results - list of the result
            * activeList - list of the acitve nodes.
            * logLevel - Type of log level you want it to be printed.
        Returns:
        """
        f = getattr( main.log, logLevel )
        for i in range( len( results ) ):
            f( activeList[ i ].name + "'s result : " + str( results[ i ] ) )

    def allTrueResultCheck( self, results, activeList ):
        """
        Description:
            check if all the result has main.TRUE.
        Required:
            * results - list of the result
            * activeList - list of the acitve nodes.
        Returns:
            Returns True if all == main.TRUE else
            returns False
        """
        self.printResult( results, activeList )
        return all( result == main.TRUE for result in results )

    def notEmptyResultCheck( self, results, activeList ):
        """
        Description:
            check if all the result has any contents
        Required:
            * results - list of the result
            * activeList - list of the acitve nodes.
        Returns:
            Returns True if all the results has
            something else returns False
        """
        self.printResult( results, activeList )
        return all( result for result in results )

    def identicalResultsCheck( self, results, activeList ):
        """
        Description:
            check if all the results has same output.
        Required:
            * results - list of the result
            * activeList - list of the acitve nodes.
        Returns:
            Returns True if all the results has
            same result else returns False
        """
        self.printResult( results, activeList )
        resultOne = results[ 0 ]
        return all( resultOne == result for result in results )

    def command( self, function, args=(), kwargs={}, returnBool=False,
                 specificDriver=0, contentCheck=False, getFrom="active",
                 funcFromCtrl=False ):
        """
        Description:
            execute some function of the active nodes.
        Required:
            * function - name of the function
            * args - argument of the function
            * kwargs - kwargs of the funciton
            * returnBool - True if wish to check all the result has main.TRUE
            * specificDriver - specific driver to execute the function. Since
            some of the function can be used in different drivers, it is important
            to specify which driver it will be executed from.
                0 - any type of driver
                1 - from bench
                2 - from cli
                3 - from rest
                4 - from server
            * contentCheck - If this is True, it will check if the result has some
            contents.
            * getFrom - from which nodes
                2 or "active" - active nodes
                1 or "running" - current running nodes
                0 or "all" - all nodes
            * funcFromCtrl - specific function of the args/kwargs
                 from each controller from the list of the controllers
        Returns:
            Returns results if not returnBool and not contentCheck
            Returns checkTruthValue of the result if returnBool
            Returns resultContent of the result if contentCheck
        """
        threads = []
        drivers = [ None, "Bench", "CLI", "REST", "server" ]
        results = []
        for ctrl in self.fromNode( getFrom ):
            funcArgs = []
            funcKwargs = {}
            try:
                f = getattr( ( ctrl if not specificDriver else
                               getattr( ctrl, drivers[ specificDriver ] ) ), function )
            except AttributeError:
                main.log.error( "Function " + function + " not found. Exiting the Test." )
                main.cleanAndExit()
            if funcFromCtrl:
                if args:
                    try:
                        for i in range( len( args ) ):
                            funcArgs.append( getattr( ctrl, args[ i ] ) )
                    except AttributeError:
                        main.log.error( "Argument " + str( args[ i ] ) + " for " + str( f ) + " not found. Exiting the Test." )
                        main.cleanAndExit()
                if kwargs:
                    try:
                        for k in kwargs:
                            funcKwargs.update( { k: getattr( ctrl, kwargs[ k ] ) } )
                    except AttributeError as e:
                        main.log.exception("")
                        main.log.error( "Keyword Argument " + str( k ) + " for " + str( f ) + " not found. Exiting the Test." )
                        main.log.debug( "Passed kwargs: %s; dir(ctrl): %s" % ( repr( kwargs ), dir( ctrl ) ) )
                        main.cleanAndExit()
            t = main.Thread( target=f,
                             name=function + "-" + ctrl.name,
                             args=funcArgs if funcFromCtrl else args,
                             kwargs=funcKwargs if funcFromCtrl else kwargs )
            threads.append( t )
            t.start()

        for t in threads:
            t.join()
            results.append( t.result )
        if returnBool:
            return self.allTrueResultCheck( results, self.fromNode( getFrom ) )
        elif contentCheck:
            return self.notEmptyResultCheck( results, self.fromNode( getFrom ) )
        return results

    def checkPartitionSize( self, segmentSize='64', units='M', multiplier='3' ):
        # max segment size in bytes: 1024 * 1024 * 64
        # multiplier is somewhat arbitrary, but the idea is the logs would have
        # been compacted before this many segments are written

        try:
            maxSize = float( segmentSize ) * float( multiplier )
            ret = True
            for n in self.runningNodes:
                # Partition logs
                ret = ret and n.server.folderSize( "/opt/atomix/data/raft/partitions/*/*.log",
                                                   size=maxSize, unit=units, ignoreRoot=False )
            return ret
        except Exception as e:
            main.log.error( e )
            main.log.error( repr( e ) )
