import time
import re
import imp
import json
class Topology:

    def __init__( self ):
        self.default = ''
    """
        These functions can be used for topology comparisons
    """
    def getAllDevices( self, numNode, needRetry, kwargs={} ):
        """
            Return a list containing the devices output from each ONOS node
        """
        devices = []
        threads = []
        for ctrl in main.Cluster.active():
            t = main.Thread( target=utilities.retry if needRetry else ctrl.devices,
                             name="devices-" + str( ctrl ),
                             args=[ ctrl.devices, [ None ] ] if needRetry else [],
                             kwargs=kwargs )
            threads.append( t )
            t.start()

        for t in threads:
            t.join()
            devices.append( t.result )
        return devices

    def getAllHosts( self, numNode, needRetry, kwargs={}, inJson=False ):
        """
            Return a list containing the hosts output from each ONOS node
        """
        hosts = []
        ipResult = main.TRUE
        threads = []
        for ctrl in main.Cluster.active():
            t = main.Thread( target=utilities.retry if needRetry else ctrl.hosts,
                             name="hosts-" + str( ctrl ),
                             args=[ ctrl.hosts, [ None ] ] if needRetry else [],
                             kwargs=kwargs )
            threads.append( t )
            t.start()

        for t in threads:
            t.join()
            if inJson:
                try:
                    hosts.append( json.loads( t.result ) )
                except ( ValueError, TypeError ):
                    main.log.exception( "Error parsing hosts results" )
                    main.log.error( repr( t.result ) )
                    hosts.append( None )
            else:
                hosts.append( t.result )
        return hosts

    def getAllPorts( self, numNode, needRetry, kwargs={} ):
        """
            Return a list containing the ports output from each ONOS node
        """
        ports = []
        threads = []
        for ctrl in main.Cluster.active():
            t = main.Thread( target=utilities.retry if needRetry else ctrl.ports,
                             name="ports-" + str( ctrl ),
                             args=[ ctrl.ports, [ None ] ] if needRetry else [],
                             kwargs=kwargs )
            threads.append( t )
            t.start()

        for t in threads:
            t.join()
            ports.append( t.result )
        return ports

    def getAllLinks( self, numNode, needRetry, kwargs={} ):
        """
            Return a list containing the links output from each ONOS node
        """
        links = []
        threads = []
        for ctrl in main.Cluster.active():
            t = main.Thread( target=utilities.retry if needRetry else ctrl.links,
                             name="links-" + str( ctrl ),
                             args=[ ctrl.links, [ None ] ] if needRetry else [],
                             kwargs=kwargs )
            threads.append( t )
            t.start()

        for t in threads:
            t.join()
            links.append( t.result )
        print links
        return links

    def getAllClusters( self, numNode, needRetry, kwargs={} ):
        """
            Return a list containing the clusters output from each ONOS node
        """
        clusters = []
        threads = []
        for ctrl in main.Cluster.active():
            t = main.Thread( target=utilities.retry if needRetry else ctrl.clusters,
                             name="clusters-" + str( ctrl ),
                             args=[ ctrl.clusters, [ None ] ] if needRetry else [],
                             kwargs=kwargs )
            threads.append( t )
            t.start()

        for t in threads:
            t.join()
            clusters.append( t.result )
        return clusters

    def compareDevicePort( self, Mininet, controller, mnSwitches, devices, ports ):
        if devices[ controller ] and ports[ controller ] and \
                        "Error" not in devices[ controller ] and \
                        "Error" not in ports[ controller ]:
            try:
                currentDevicesResult = Mininet.compareSwitches(
                    mnSwitches,
                    json.loads( devices[ controller ] ),
                    json.loads( ports[ controller ] ) )
            except ( TypeError, ValueError ):
                main.log.error(
                    "Could not load json: {0} or {1}".format( str( devices[ controller ] ),
                                                              str( ports[ controller ] ) ) )
                currentDevicesResult = main.FALSE
        else:
            currentDevicesResult = main.FALSE
        return currentDevicesResult

    def compareBase( self, compareElem, controller, compareF, compareArg ):
        if compareElem[ controller ] and "Error" not in compareElem[ controller ]:
            try:
                if isinstance( compareArg, list ):
                    compareArg.append( json.loads( compareElem[ controller ] ) )
                else:
                    compareArg = [compareArg, json.loads( compareElem[ controller ] ) ]

                currentCompareResult = compareF( *compareArg )
            except(TypeError, ValueError):
                main.log.error(
                    "Could not load json: {0} or {1}".format( str( compareElem[ controller ] ) ) )
                currentCompareResult = main.FALSE
        else:
            currentCompareResult = main.FALSE

        return currentCompareResult

    def compareTopos( self, Mininet, attempts=1 ):

        main.case( "Compare ONOS Topology view to Mininet topology" )
        main.caseExplanation = "Compare topology elements between Mininet" +\
                                " and ONOS"
        main.log.info( "Gathering topology information from Mininet" )
        devicesResults = main.FALSE  # Overall Boolean for device correctness
        linksResults = main.FALSE  # Overall Boolean for link correctness
        hostsResults = main.FALSE  # Overall Boolean for host correctness
        deviceFails = []  # Nodes where devices are incorrect
        linkFails = []  # Nodes where links are incorrect
        hostFails = []  # Nodes where hosts are incorrect

        mnSwitches = Mininet.getSwitches()
        mnLinks = Mininet.getLinks()
        mnHosts = Mininet.getHosts()

        main.step( "Comparing Mininet topology to ONOS topology" )

        while ( attempts >= 0 ) and\
                ( not devicesResults or not linksResults or not hostsResults ):
            main.log.info( "Sleeping {} seconds".format( 2 ) )
            time.sleep( 2 )
            if not devicesResults:
                devices = self.getAllDevices( main.numCtrls, False )
                ports = self.getAllPorts( main.numCtrls, False )
                devicesResults = main.TRUE
                deviceFails = []  # Reset for each failed attempt
            if not linksResults:
                links = self.getAllLinks( main.numCtrls, False )
                linksResults = main.TRUE
                linkFails = []  # Reset for each failed attempt
            if not hostsResults:
                hosts = self.getAllHosts( main.numCtrls, False )
                hostsResults = main.TRUE
                hostFails = []  # Reset for each failed attempt

            #  Check for matching topology on each node
            for controller in range( main.numCtrls ):
                controllerStr = str( controller + 1 )  # ONOS node number
                # Compare Devices
                currentDevicesResult = self.compareDevicePort( Mininet, controller,
                                                               mnSwitches,
                                                               devices, ports )
                if not currentDevicesResult:
                    deviceFails.append( controllerStr )
                devicesResults = devicesResults and currentDevicesResult
                # Compare Links
                currentLinksResult = self.compareBase( links, controller,
                                                       Mininet.compareLinks,
                                                       [ mnSwitches, mnLinks ] )
                if not currentLinksResult:
                    linkFails.append( controllerStr )
                linksResults = linksResults and currentLinksResult
                # Compare Hosts
                currentHostsResult = self.compareBase( hosts, controller,
                                                           Mininet.compareHosts,
                                                           mnHosts )
                if not currentHostsResult:
                    hostFails.append( controllerStr )
                hostsResults = hostsResults and currentHostsResult
            # Decrement Attempts Remaining
            attempts -= 1

        utilities.assert_equals( expect=[],
                                 actual=deviceFails,
                                 onpass="ONOS correctly discovered all devices",
                                 onfail="ONOS incorrectly discovered devices on nodes: " +
                                 str( deviceFails ) )
        utilities.assert_equals( expect=[],
                                 actual=linkFails,
                                 onpass="ONOS correctly discovered all links",
                                 onfail="ONOS incorrectly discovered links on nodes: " +
                                 str( linkFails ) )
        utilities.assert_equals( expect=[],
                                 actual=hostFails,
                                 onpass="ONOS correctly discovered all hosts",
                                 onfail="ONOS incorrectly discovered hosts on nodes: " +
                                 str( hostFails ) )
        topoResults = hostsResults and linksResults and devicesResults
        utilities.assert_equals( expect=main.TRUE,
                                 actual=topoResults,
                                 onpass="ONOS correctly discovered the topology",
                                 onfail="ONOS incorrectly discovered the topology" )
