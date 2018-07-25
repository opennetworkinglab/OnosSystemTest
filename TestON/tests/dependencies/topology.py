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
import time
import re
import imp
import json
from core import utilities


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
                             name=function + "-" + str( ctrl ),
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
                    compareArg = [ compareArg, json.loads( compareElem[ controller ] ) ]

                currentCompareResult = compareF( *compareArg )
            except( TypeError, ValueError ):
                main.log.error(
                    "Could not load json: {0} or {1}".format( str( compareElem[ controller ] ) ) )
                currentCompareResult = main.FALSE
        else:
            currentCompareResult = main.FALSE

        return currentCompareResult

    def compareTopos( self, Mininet, attempts=1, includeCaseDesc=True ):
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
        if includeCaseDesc:
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

    def ping( self, srcList, dstList, ipv6=False, expect=True, wait=1, acceptableFailed=0, collectT3=True, t3Simple=False ):
        """
        Description:
            Ping from every host in srcList to every host in dstList and
            verify if ping results are as expected.
            Pings are executed in parallel from host components
        Options:
            src: a list of source host names, e.g. [ "h1", "h2" ]
            dst: a list of destination host names, e.g. [ "h3", "h4" ]
            expect: expect ping result to pass if True, otherwise fail
            acceptableFailed: maximum number of failed pings acceptable for
                              each src-dst host pair
            collectT3: save t3-troubleshoot output for src and dst host that failed to ping
            t3Simple: use t3-troubleshoot-simple command when collecting t3 output
        Returns:
            main.TRUE if all ping results are expected, otherwise main.FALSE
        """
        main.log.info( "Pinging from {} to {}, expected result is {}".format( srcList, dstList,
                                                                              "pass" if expect else "fail" ) )
        # Verify host component has been created
        srcIpList = {}
        for src in srcList:
            if not hasattr( main, src ):
                main.log.info( "Creating component for host {}".format( src ) )
                main.Network.createHostComponent( src )
                hostHandle = getattr( main, src )
                main.log.info( "Starting CLI on host {}".format( src ) )
                hostHandle.startHostCli()
            srcIpList[ src ] = main.Network.getIPAddress( src, proto='IPV6' if ipv6 else 'IPV4' )
        unexpectedPings = []
        for dst in dstList:
            dstIp = main.Network.getIPAddress( dst, proto='IPV6' if ipv6 else 'IPV4' )
            # Start pings from src hosts in parallel
            pool = []
            for src in srcList:
                srcIp = srcIpList[ src ]
                if not srcIp or not dstIp:
                    if expect:
                        unexpectedPings.append( [ src, dst, "no IP" ] )
                    continue
                if srcIp == dstIp:
                    continue
                hostHandle = getattr( main, src )
                thread = main.Thread( target=utilities.retry,
                                      name="{}-{}".format( srcIp, dstIp ),
                                      args=[ hostHandle.pingHostSetAlternative, [ main.FALSE ] ],
                                      kwargs={ "args": ( [ dstIp ], wait, ipv6 ),
                                               "attempts": acceptableFailed + 1,
                                               "sleep": 1 } )
                pool.append( thread )
                thread.start()
            # Wait for threads to finish and check ping result
            for thread in pool:
                thread.join( 10 )
                srcIp, dstIp = thread.name.split( "-" )
                if expect and not thread.result or not expect and thread.result:
                    unexpectedPings.append( [ srcIp, dstIp, "fail" if expect else "pass" ] )
        main.log.info( "Unexpected pings: {}".format( unexpectedPings ) )
        if collectT3:
            for unexpectedPing in unexpectedPings:
                if unexpectedPing[ 2 ] == "no IP":
                    continue
                srcIp = unexpectedPing[ 0 ]
                dstIp = unexpectedPing[ 1 ]
                main.log.debug( "Collecting t3 with source {} and destination {}".format( srcIp, dstIp ) )
                cmdList = main.Cluster.active( 0 ).CLI.composeT3Command( srcIp, dstIp, ipv6, True, t3Simple )
                if not cmdList:
                    main.log.warn( "Failed to compose T3 command with source {} and destination {}".format( srcIp, dstIp ) )
                    continue
                for i in range( 0, len( cmdList ) ):
                    cmd = cmdList[ i ]
                    main.log.debug( "t3 command: {}".format( cmd ) )
                    main.ONOSbench.dumpONOSCmd( main.Cluster.active( 0 ).ipAddress, cmd, main.logdir,
                                                "t3-CASE{}-{}-{}-route{}-".format( main.CurrentTestCaseNumber, srcIp, dstIp, i ),
                                                timeout=10 )
        return main.FALSE if unexpectedPings else main.TRUE

    def sendScapyPackets( self, sender, receiver, pktFilter, pkt, sIface=None, dIface=None, expect=True, acceptableFailed=0, collectT3=True, t3Command="" ):
        """
        Description:
            Send Scapy packets from sender to receiver and verify if result is as expected and retry if neccessary
            If collectT3 is True and t3Command is specified, collect t3-troubleshoot output on unexpected scapy results
        Options:
            sender: the component of the host that is sending packets
            receiver: the component of the host that is receiving packets
            pktFilter: packet filter used by receiver
            pkt: keyword that is expected to be conrained in the received packets
            expect: expect receiver to receive the packet if True, otherwise not receiving the packet
            acceptableFailed: maximum number of unexpected scapy results acceptable
            collectT3: save t3-troubleshoot output for unexpected scapy results
        Returns:
            main.TRUE if scapy result is expected, otherwise main.FALSE
        Note: It is assumed that Scapy is already started on the destination host
        """
        main.log.info( "Sending scapy packets from  {} to {}, expected result is {}".format( sender.name, receiver.name,
                                                                                             "pass" if expect else "fail" ) )
        scapyResult = utilities.retry( self.sendScapyPacketsHelper,
                                       main.FALSE,
                                       args=( sender, receiver, pktFilter, pkt,
                                              sIface, dIface, expect ),
                                       attempts=acceptableFailed + 1,
                                       sleep=1 )
        if not scapyResult and collectT3 and t3Command:
            main.log.debug( "Collecting t3 with source {} and destination {}".format( sender.name, receiver.name ) )
            main.log.debug( "t3 command: {}".format( t3Command ) )
            main.ONOSbench.dumpONOSCmd( main.Cluster.active( 0 ).ipAddress, t3Command, main.logdir,
                                        "t3-CASE{}-{}-{}-".format( main.CurrentTestCaseNumber, sender.name, receiver.name ) )
        return scapyResult

    def sendScapyPacketsHelper( self, sender, receiver, pktFilter, pkt, sIface=None, dIface=None, expect=True ):
        """
        Description:
            Send Scapy packets from sender to receiver and verify if result is as expected
        Options:
            sender: the component of the host that is sending packets
            receiver: the component of the host that is receiving packets
            pktFilter: packet filter used by receiver
            pkt: keyword that is expected to be conrained in the received packets
            expect: expect receiver to receive the packet if True, otherwise not receiving the packet
        Returns:
            main.TRUE if scapy result is expected, otherwise main.FALSE
        """
        receiver.startFilter( ifaceName=dIface, pktFilter=pktFilter )
        sender.sendPacket( iface=sIface )
        finished = receiver.checkFilter()
        packet = ""
        if finished:
            packets = receiver.readPackets()
            for packet in packets.splitlines():
                main.log.debug( packet )
        else:
            kill = receiver.killFilter()
            main.log.debug( kill )
            sender.handle.sendline( "" )
            sender.handle.expect( sender.scapyPrompt )
            main.log.debug( sender.handle.before )
        packetCaptured = True if pkt in packet else False
        return main.TRUE if packetCaptured == expect else main.FALSE

    def pingAndCapture( self, srcHost, dstIp, dstHost, dstIntf, ipv6=False, expect=True, acceptableFailed=0, collectT3=True, t3Simple=False ):
        """
        Description:
            Ping from src host to dst IP and capture packets at dst Host using Scapy and retry if neccessary
            If collectT3 is True, collect t3-troubleshoot output on unexpected scapy results
        Options:
            srcHost: name of the source host
            dstIp: destination IP of the ping packets
            dstHost: host that runs Scapy to capture the packets
            dstIntf: name of the interface on the destination host
            ipv6: ping with IPv6 if True; Otherwise IPv4
            expect: use True if the ping is expected to be captured at destination;
                    Otherwise False
            acceptableFailed: maximum number of failed pings acceptable
            collectT3: save t3-troubleshoot output for src and dst host that failed to ping
            t3Simple: use t3-troubleshoot-simple command when collecting t3 output
        Returns:
            main.TRUE if packet capturing result is expected, otherwise main.FALSE
        Note: It is assumed that Scapy is already started on the destination host
        """
        main.log.info( "Pinging from {} to {}, expected {} capture the packet at {}".format( srcHost, dstIp,
                       "to" if expect else "not to", dstHost ) )
        # Verify host component has been created
        if not hasattr( main, srcHost ):
            main.log.info( "Creating component for host {}".format( srcHost ) )
            main.Network.createHostComponent( srcHost )
            srcHandle = getattr( main, srcHost )
            main.log.info( "Starting CLI on host {}".format( srcHost ) )
            srcHandle.startHostCli()
        trafficResult = utilities.retry( self.pingAndCaptureHelper,
                                         main.FALSE,
                                         args=( srcHost, dstIp, dstHost, dstIntf, ipv6, expect ),
                                         attempts=acceptableFailed + 1,
                                         sleep=1 )
        if not trafficResult and collectT3:
            srcIp = main.Network.getIPAddress( srcHost, proto='IPV6' if ipv6 else 'IPV4' )
            main.log.debug( "Collecting t3 with source {} and destination {}".format( srcIp, dstIp ) )
            cmdList = main.Cluster.active( 0 ).CLI.composeT3Command( srcIp, dstIp, ipv6, True, t3Simple )
            if not cmdList:
                main.log.warn( "Failed to compose T3 command with source {} and destination {}".format( srcIp, dstIp ) )
            for i in range( 0, len( cmdList ) ):
                cmd = cmdList[ i ]
                main.log.debug( "t3 command: {}".format( cmd ) )
                main.ONOSbench.dumpONOSCmd( main.Cluster.active( 0 ).ipAddress, cmd, main.logdir,
                                            "t3-CASE{}-{}-{}-route{}-".format( main.CurrentTestCaseNumber, srcIp, dstIp, i ),
                                            timeout=10 )
        return trafficResult

    def pingAndCaptureHelper( self, srcHost, dstIp, dstHost, dstIntf, ipv6=False, expect=True ):
        """
        Description:
            Ping from src host to dst IP and capture packets at dst Host using Scapy
        Options:
            srcHost: name of the source host
            dstIp: destination IP of the ping packets
            dstHost: host that runs Scapy to capture the packets
            dstIntf: name of the interface on the destination host
            ipv6: ping with IPv6 if True; Otherwise IPv4
            expect: use True if the ping is expected to be captured at destination;
                    Otherwise False
        Returns:
            main.TRUE if packet capturing result is expected, otherwise main.FALSE
        """
        packetCaptured = True
        srcHandle = getattr( main, srcHost )
        dstHandle = getattr( main, dstHost )
        dstHandle.startFilter( ifaceName=dstIntf, pktFilter="ip host {}".format( dstIp ) )
        srcHandle.pingHostSetAlternative( [ dstIp ], IPv6=ipv6 )
        finished = dstHandle.checkFilter()
        packet = ""
        if finished:
            packets = dstHandle.readPackets()
            for packet in packets.splitlines():
                main.log.debug( packet )
        else:
            kill = dstHandle.killFilter()
            main.log.debug( kill )
        packetCaptured = True if "dst={}".format( dstIp ) in packet else False
        return main.TRUE if packetCaptured == expect else main.FALSE
