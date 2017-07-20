"""
Copyright 2017 Open Networking Foundation (ONF)

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.
"""


class Cluster():

    def __str__( self ):
        return self.name
    def __repr__( self ):
        #TODO use repr of cli's?
        controllers = []
        runningNodes = []
        for ctrl in self.controllers:
            controllers.append( str( ctrl ) )
        return "%s[%s]" % ( self.name, ", ".join( controllers ) )


    def __init__( self, ctrlList=[], name="Cluster" ):
        '''
            controllers : All the nodes
            runningNodes : Node that are specifically running from the test.
                ie) When the test is testing different number of nodes on each
                    run.
            numCtrls : number of runningNodes
            maxCtrls : number of controllers
        '''
        self.controllers = ctrlList
        self.runningNodes = ctrlList
        self.numCtrls = len( self.runningNodes )
        self.maxCtrls = len( self.controllers )
        self.name = str( name )
        self.iterator = iter( self.active() )

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
            ips.append( ctrl.ipAddress )

        return ips

    def resetActive( self ):
        """
        Description:
            reset the activeness of the runningNodes to be false
        Required:
        Returns:
        """
        for ctrl in self.runningNodes:
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
        for i in numCtrls if isinstance( numCtrls, list ) else range( numCtrls ) :
            self.runningNodes.append( self.controllers[ i ] )
        self.numCtrls = len( numCtrls ) if isinstance( numCtrls, list ) else numCtrls

    def active( self, node=None ):
        """
        Description:
            get the list/controller of the active controller.
        Required:
            * node - position of the node to get from the active controller.
        Returns:
            Return a list of active controllers in the cluster if node is None
            if not, it will return the nth controller.
        """
        result = [ ctrl for ctrl in self.runningNodes
                      if ctrl.active ]
        return result if node is None else result[ node % len( result ) ]

    def next( self ):
        """
        An iterator for the cluster's controllers that
        resets when there are no more elements.

        Returns the next controller in the cluster
        """
        try:
            return self.iterator.next()
        except StopIteration:
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

    def createCell( self, cellName, Mininet, useSSH, ips ):
        """
        Description:
            create a new cell
        Required:
            * cellName - The name of the cell.
            * Mininet - a mininet driver that will be used.
            * useSSH - True for using ssh when creating a cell
            * ips - ip(s) of the node(s).
        Returns:
        """
        main.ONOSbench.createCellFile( main.ONOSbench.ip_address,
                                       cellName,
                                       Mininet if isinstance( Mininet, str ) else
                                       Mininet.ip_address,
                                       main.apps,
                                       ips,
                                       main.ONOScell.karafUser,
                                       useSSH=useSSH )

    def uninstall( self, uninstallMax ):
        """
        Description:
            uninstalling onos
        Required:
            * uninstallMax - True for uninstalling max number of nodes
            False for uninstalling the current running nodes.
        Returns:
            Returns main.TRUE if it successfully uninstalled.
        """
        onosUninstallResult = main.TRUE
        for ctrl in self.controllers if uninstallMax else self.runningNodes:
            onosUninstallResult = onosUninstallResult and \
                                  main.ONOSbench.onosUninstall( nodeIp=ctrl.ipAddress )
        return onosUninstallResult

    def applyCell( self, cellName ):
        """
        Description:
            apply the cell with cellName. It will also verify the
            cell.
        Required:
            * cellName - The name of the cell.
        Returns:
            Returns main.TRUE if it successfully set and verify cell.
        """
        cellResult = main.ONOSbench.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()
        return cellResult and verifyResult

    def checkService( self ):
        """
        Description:
            Checking if the onos service is up. If not, it will
            start the onos service manually.
        Required:
        Returns:
            Returns main.TRUE if it successfully checked
        """
        stopResult = main.TRUE
        startResult = main.TRUE
        onosIsUp = main.TRUE
        i = 0
        for ctrl in self.runningNodes:
            onosIsUp = onosIsUp and main.ONOSbench.isup( ctrl.ipAddress )
            if onosIsUp == main.TRUE:
                main.log.report( "ONOS instance {0} is up and ready".format( i + 1 ) )
            else:
                main.log.report( "ONOS instance {0} may not be up, stop and ".format( i + 1 ) +
                                 "start ONOS again " )
                stopResult = stopResult and main.ONOSbench.onosStop( ctrl.ipAddress )
                startResult = startResult and main.ONOSbench.onosStart( ctrl.ipAddress )
                if not startResult or stopResult:
                    main.log.report( "ONOS instance {0} did not start correctly.".format( i + 1 ) )
            i += 1
        return onosIsUp and stopResult and startResult

    def kill( self, killMax, stopOnos ):
        """
        Description:
            killing the onos. It will either kill the current runningnodes or
            max number of the nodes.
        Required:
            * killRemoveMax - The boolean that will decide either to kill
            only running nodes (False) or max number of nodes (True).
            * stopOnos - If wish to stop onos before killing it. True for
            enable stop , False for disable stop.
        Returns:
            Returns main.TRUE if successfully killing it.
        """
        result = main.TRUE
        for ctrl in self.controllers if killMax else self.runningNodes:
            if stopOnos:
                result = result and main.ONOSbench.onosStop( ctrl.ipAddress )
            result = result and main.ONOSbench.onosKill( ctrl.ipAddress )
            ctrl.active = False
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
        secureSshResult = main.TRUE
        for ctrl in self.runningNodes:
            secureSshResult = secureSshResult and main.ONOSbench.onosSecureSSH( node=ctrl.ipAddress )
        return secureSshResult

    def install( self, installMax=True ):
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
            result = result and \
                            main.ONOSbench.onosInstall( node=ctrl.ipAddress, options=options )

        return result

    def startCLIs( self ):
        """
        Description:
            starting Onos using onosCli driver
        Required:
        Returns:
            Returns main.TRUE if it successfully started.
        """
        cliResults =  main.TRUE
        threads = []
        for ctrl in self.runningNodes:
            t = main.Thread( target=ctrl.CLI.startOnosCli,
                             name="startCli-" + ctrl.name,
                             args=[ ctrl.ipAddress ] )
            threads.append( t )
            t.start()
            ctrl.active = True

        for t in threads:
            t.join()
            cliResults = cliResults and t.result
        return cliResults

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
        for i in range ( len ( results ) ):
            f( activeList[ i ].name + "'s result : " + str ( results[ i ] ) )

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

    def command( self, function, args=(), kwargs={}, returnBool=False, specificDriver=0, contentCheck=False ):
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
            * contentCheck - If this is True, it will check if the result has some
            contents.
        Returns:
            Returns results if not returnBool and not contentCheck
            Returns checkTruthValue of the result if returnBool
            Returns resultContent of the result if contentCheck
        """
        """
        Send a command to all ONOS nodes and return the results as a list
        specificDriver:
            0 - any type of driver
            1 - from bench
            2 - from cli
            3 - from rest
        """
        threads = []
        drivers = [ None, "Bench", "CLI", "REST" ]
        results = []
        for ctrl in self.active():
            try:
                f = getattr( ( ctrl if not specificDriver else
                             getattr( ctrl, drivers[ specificDriver ] ) ), function )
            except AttributeError:
                main.log.error( "Function " + function + " not found. Exiting the Test." )
                main.cleanup()
                main.exit()

            t = main.Thread( target=f,
                             name=function + "-" + ctrl.name,
                             args=args,
                             kwargs=kwargs )
            threads.append( t )
            t.start()

        for t in threads:
            t.join()
            results.append( t.result )
        if returnBool:
            return self.allTrueResultCheck( results, self.active() )
        elif contentCheck:
            return self.notEmptyResultCheck( results, self.active() )
        return results