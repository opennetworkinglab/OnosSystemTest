"""
Copyright 2016 Open Networking Foundation (ONF)

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
    def getAll( self, function, needRetry=False, kwargs={}, inJson=False ):
        """
        Description:
            get all devices/links/hosts/ports of the onosCli
        Required:
            * function - name of the function
            * needRetry - it will retry if this is true.
            * kwargs - kwargs of the function
            * inJson - True if want it in Json form
        Returns:
            Returns the list of the result.
        """
        returnList = []
        threads = []
        for ctrl in main.Cluster.active():
            func = getattr( ctrl.CLI, function )
            t = main.Thread( target=utilities.retry if needRetry else func,
                             name= function + "-" + str( ctrl ),
                             args=[ func, [ None ] ] if needRetry else [],
                             kwargs=kwargs )
            threads.append( t )
            t.start()

        for t in threads:
            t.join()
            if inJson:
                try:
                    returnList.append( json.loads( t.result ) )
                except ( ValueError, TypeError ):
                    main.log.exception( "Error parsing hosts results" )
                    main.log.error( repr( t.result ) )
                    returnList.append( None )
            else:
                returnList.append( t.result )
        return returnList

    def compareDevicePort( self, Mininet, controller, mnSwitches, devices, ports ):
        """
        Description:
            compares the devices and port of the onos to the mininet.
        Required:
            * Mininet - mininet driver to use
            * controller - controller position of the devices
            * mnSwitches - switches of mininet
            * devices - devices of the onos
            * ports - ports of the onos
        Returns:
            Returns main.TRUE if the results are matching else
            Returns main.FALSE
        """
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
        """
        Description:
            compares the links/hosts of the onos to the mininet.
        Required:
            * compareElem - list of links/hosts of the onos
            * controller - controller position of the devices
            * compareF - function of the mininet that will compare the
            results
            * compareArg - arg of the compareF.
        Returns:
            Returns main.TRUE if the results are matching else
            Returns main.FALSE
        """
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
        """
        Description:
            compares the links and hosts and switches of the onos to the mininet.
        Required:
            * Mininet - Mininet driver to use.
            * attempts - number of attempts to compare in case
            the result is different after a certain time.
        Returns:
            Returns main.TRUE if the results are matching else
            Returns main.FALSE
        """
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
                devices = self.getAll( "devices", False )
                ports = self.getAll( "ports", False )
                devicesResults = main.TRUE
                deviceFails = []  # Reset for each failed attempt
            if not linksResults:
                links = self.getAll( "links", False )
                linksResults = main.TRUE
                linkFails = []  # Reset for each failed attempt
            if not hostsResults:
                hosts = self.getAll( "hosts", False )
                hostsResults = main.TRUE
                hostFails = []  # Reset for each failed attempt

            #  Check for matching topology on each node
            for controller in main.Cluster.getRunningPos():
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
        return topoResults
