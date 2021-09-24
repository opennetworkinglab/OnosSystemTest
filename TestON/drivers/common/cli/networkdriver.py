#!/usr/bin/env python
"""
Copyright 2018 Open Networking Foundation (ONF)

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


This driver is used to interact with a physical network that SDN controller is controlling.

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

"""
import pexpect
import os
import re
import types
import time
import itertools
import random
from drivers.common.clidriver import CLI
from core.graph import Graph

class NetworkDriver( CLI ):

    def __init__( self ):
        """
        switches: a dictionary that maps switch names to components
        hosts: a dictionary that maps host names to components
        """
        self.name = None
        self.home = None
        self.handle = None
        self.switches = {}
        self.hosts = {}
        self.links = {}
        super( NetworkDriver, self ).__init__()
        self.graph = Graph()

    def connect( self, **connectargs ):
        """
        Creates ssh handle for the SDN network "bench".
        NOTE:
        The ip_address would come from the topo file using the host tag, the
        value can be an environment variable as well as a "localhost" to get
        the ip address needed to ssh to the "bench"
        """
        try:
            for key in connectargs:
                vars( self )[ key ] = connectargs[ key ]
            self.name = self.options[ 'name' ]
            try:
                if os.getenv( str( self.ip_address ) ) is not None:
                    self.ip_address = os.getenv( str( self.ip_address ) )
                else:
                    main.log.info( self.name +
                                   ": Trying to connect to " +
                                   self.ip_address )
            except KeyError:
                main.log.info( "Invalid host name," +
                               " connecting to local host instead" )
                self.ip_address = 'localhost'
            except Exception as inst:
                main.log.error( "Uncaught exception: " + str( inst ) )

            self.handle = super( NetworkDriver, self ).connect(
                user_name=self.user_name,
                ip_address=self.ip_address,
                port=self.port,
                pwd=self.pwd )

            if self.handle:
                main.log.info( "Connected to network bench node" )
                return self.handle
            else:
                main.log.info( "Failed to create handle" )
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def disconnect( self ):
        """
        Called when test is complete to disconnect the handle.
        """
        response = main.TRUE
        try:
            if self.handle:
                self.handle.sendline( "exit" )
                self.handle.expect( "closed" )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
        except Exception:
            main.log.exception( self.name + ": Connection failed to the host" )
            response = main.FALSE
        return response

    def connectToNet( self ):
        """
        Connect to an existing physical network by getting information
        of all switch and host components created
        """
        try:
            for key, value in main.componentDictionary.items():
                if hasattr( main, key ):
                    if value[ 'type' ] in [ 'MininetSwitchDriver', 'OFDPASwitchDriver', 'StratumOSSwitchDriver' ]:
                        component = getattr( main, key )
                        shortName = component.options[ 'shortName' ]
                        localName = self.name + "-" + shortName
                        self.copyComponent( key, localName )
                        self.switches[ shortName ] = getattr( main, localName )
                    elif value[ 'type' ] in [ 'MininetHostDriver', 'HostDriver' ]:
                        component = getattr( main, key )
                        shortName = component.options[ 'shortName' ]
                        localName = self.name + "-" + shortName
                        self.copyComponent( key, localName )
                        self.hosts[ shortName ] = getattr( main, localName )
            main.log.debug( self.name + ": found switches: {}".format( self.switches ) )
            main.log.debug( self.name + ": found hosts: {}".format( self.hosts ) )
            return main.TRUE
        except Exception:
            main.log.error( self.name + ": failed to connect to network" )
            return main.FALSE

    def disconnectFromNet( self ):
        """
        Disconnect from the physical network connected
        """
        try:
            for key, value in main.componentDictionary.items():
                if hasattr( main, key ) and key.startswith( self.name + "-" ):
                    self.removeComponent( key )
            self.switches = {}
            self.hosts = {}
            return main.TRUE
        except Exception:
            main.log.error( self.name + ": failed to disconnect from network" )
            return main.FALSE

    def copyComponent( self, name, newName ):
        """
        Copy the component initialized from the .topo file
        The copied components are only supposed to be called within this driver
        Required:
            name: name of the component to be copied
            newName: name of the new component
        """
        try:
            main.componentDictionary[ newName ] = main.componentDictionary[ name ].copy()
            main.componentInit( newName )
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def removeHostComponent( self, name ):
        """
        Remove host component
        Required:
            name: name of the component to be removed
        """
        try:
            self.removeComponent( name )
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def removeComponent( self, name ):
        """
        Remove host/switch component
        Required:
            name: name of the component to be removed
        """
        try:
            component = getattr( main, name )
        except AttributeError:
            main.log.error( "Component " + name + " does not exist." )
            return main.FALSE
        try:
            # Disconnect from component
            component.disconnect()
            # Delete component
            delattr( main, name )
            # Delete component from ComponentDictionary
            del( main.componentDictionary[ name ] )
            return main.TRUE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def createHostComponent( self, name ):
        """
        Creates host component with the same parameters as the one copied to local.
        Arguments:
            name - The string of the name of this component. The new component
                   will be assigned to main.<name> .
                   In addition, main.<name>.name = str( name )
        """
        try:
            # look to see if this component already exists
            getattr( main, name )
        except AttributeError:
            # namespace is clear, creating component
            localName = self.name + "-" + name
            main.componentDictionary[ name ] = main.componentDictionary[ localName ].copy()
            main.componentInit( name )
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()
        else:
            # namespace is not clear!
            main.log.error( name + " component already exists!" )
            main.cleanAndExit()

    def connectInbandHosts( self ):
        """
        Connect to hosts using data plane IPs specified
        """
        result = main.TRUE
        try:
            for hostName, hostComponent in self.hosts.items():
                if hostComponent.options[ 'inband' ] == 'True':
                    main.log.info( self.name + ": connecting inband host " + hostName )
                    result = hostComponent.connectInband() and result
            return result
        except Exception:
            main.log.error( self.name + ": failed to connect to inband hosts" )
            return main.FALSE

    def disconnectInbandHosts( self ):
        """
        Terminate the connections to hosts using data plane IPs
        """
        result = main.TRUE
        try:
            for hostName, hostComponent in self.hosts.items():
                if hostComponent.options[ 'inband' ] == 'True':
                    main.log.info( self.name + ": disconnecting inband host " + hostName )
                    result = hostComponent.disconnectInband() and result
            return result
        except Exception:
            main.log.error( self.name + ": failed to disconnect inband hosts" )
            return main.FALSE

    def getSwitches( self, timeout=60, excludeNodes=[], includeStopped=False ):
        """
        Return a dictionary which maps short names to switch data
        If includeStopped is True, stopped switches will also be included
        """
        switches = {}
        for switchName, switchComponent in self.switches.items():
            if switchName in excludeNodes:
                continue
            if not includeStopped and not switchComponent.isup:
                continue
            try:
                dpid = switchComponent.dpid
            except AttributeError:
                main.log.warn( "Switch has no dpid, ignore this if not an OpenFlow switch" )
                dpid = "0x0"
            dpid = dpid.replace( '0x', '' ).zfill( 16 )
            ports = switchComponent.ports
            swClass = 'Unknown'
            pid = None
            options = None
            switches[ switchName ] = { "dpid": dpid,
                                       "ports": ports,
                                       "swClass": swClass,
                                       "pid": pid,
                                       "options": options }
        return switches

    def getHosts( self, hostClass=None ):
        """
        Return a dictionary which maps short names to host data
        """
        hosts = {}
        for hostName, hostComponent in self.hosts.items():
            interfaces = hostComponent.interfaces
            hosts[ hostName ] = { "interfaces": interfaces }
        return hosts

    def updateLinks( self, timeout=60, excludeNodes=[] ):
        """
        Update self.links by getting up-to-date port information from
        switches
        """
        # TODO: also inlcude switch-to-host links
        self.links = {}
        for node1 in self.switches.keys():
            if node1 in excludeNodes:
                continue
            self.links[ node1 ] = {}
            self.switches[ node1 ].updatePorts()
            for port in self.switches[ node1 ].ports:
                if not port[ 'enabled' ]:
                    continue
                node2 = getattr( main, port[ 'node2' ] ).shortName
                if node2 in excludeNodes:
                    continue
                port1 = port[ 'of_port' ]
                port2 = port[ 'port2' ]
                if not self.links[ node1 ].get( node2 ):
                    self.links[ node1 ][ node2 ] = {}
                # Check if this link already exists
                if self.links.get( node2 ):
                    if self.links[ node2 ].get( node1 ):
                        if self.links[ node2 ].get( node1 ).get( port2 ):
                            assert self.links[ node2 ][ node1 ][ port2 ] == port1
                            continue
                self.links[ node1 ][ node2 ][ port1 ] = port2

    def getLinks( self, timeout=60, excludeNodes=[] ):
        """
        Return a list of links specify both node names and port numbers
        """
        self.updateLinks( timeout=timeout, excludeNodes=excludeNodes )
        links = []
        for node1, nodeLinks in self.links.items():
            for node2, ports in nodeLinks.items():
                for port1, port2 in ports.items():
                    links.append( { 'node1': node1, 'node2': node2,
                                    'port1': port1, 'port2': port2 } )
        return links

    def getMacAddress( self, host ):
        """
        Return MAC address of a host
        """
        try:
            hostComponent = self.hosts[ host ]
            response = hostComponent.ifconfig()
            pattern = r'HWaddr\s([0-9A-F]{2}[:-]){5}([0-9A-F]{2})'
            macAddressSearch = re.search( pattern, response, re.I )
            macAddress = macAddressSearch.group().split( " " )[ 1 ]
            main.log.info( self.name + ": Mac-Address of Host " + host + " is " + macAddress )
            return macAddress
        except Exception:
            main.log.error( self.name + ": failed to get host MAC address" )

    def runCmdOnHost( self, hostName, cmd ):
        """
        Run shell command on specified host and return output
        Required:
            hostName: name of the host e.g. "h1"
            cmd: command to run on the host
        """
        hostComponent = self.hosts[ hostName ]
        if hostComponent:
            return hostComponent.command( cmd )
        return None

    def assignSwController( self, sw, ip, port="6653", ptcp="" ):
        """
        Description:
            Assign switches to the controllers
        Required:
            sw - Short name of the switch specified in the .topo file, e.g. "s1".
            It can also be a list of switch names.
            ip - Ip addresses of controllers. This can be a list or a string.
        Optional:
            port - ONOS use port 6653, if no list of ports is passed, then
                   the all the controller will use 6653 as their port number
            ptcp - ptcp number, This can be a string or a list that has
                   the same length as switch. This is optional and not required
                   when using ovs switches.
        NOTE: If switches and ptcp are given in a list type they should have the
              same length and should be in the same order, Eg. sw=[ 's1' ... n ]
              ptcp=[ '6637' ... n ], s1 has ptcp number 6637 and so on.

        Return:
            Returns main.TRUE if switches are correctly assigned to controllers,
            otherwise it will return main.FALSE or an appropriate exception(s)
        """
        switchList = []
        ptcpList = None
        try:
            if isinstance( sw, types.StringType ):
                switchList.append( sw )
                if ptcp:
                    if isinstance( ptcp, types.StringType ):
                        ptcpList = [ ptcp ]
                    elif isinstance( ptcp, types.ListType ):
                        main.log.error( self.name + ": Only one switch is " +
                                        "being set and multiple PTCP is " +
                                        "being passed " )
                        return main.FALSE
                    else:
                        main.log.error( self.name + ": Invalid PTCP" )
                        return main.FALSE

            elif isinstance( sw, types.ListType ):
                switchList = sw
                if ptcp:
                    if isinstance( ptcp, types.ListType ):
                        if len( ptcp ) != len( sw ):
                            main.log.error( self.name + ": PTCP length = " +
                                            str( len( ptcp ) ) +
                                            " is not the same as switch" +
                                            " length = " +
                                            str( len( sw ) ) )
                            return main.FALSE
                        else:
                            ptcpList = ptcp
                    else:
                        main.log.error( self.name + ": Invalid PTCP" )
                        return main.FALSE
            else:
                main.log.error( self.name + ": Invalid switch type " )
                return main.FALSE

            assignResult = main.TRUE
            index = 0
            for switch in switchList:
                assigned = False
                switchComponent = self.switches[ switch ]
                if switchComponent:
                    ptcp = ptcpList[ index ] if ptcpList else ""
                    assignResult = assignResult and switchComponent.assignSwController( ip=ip, port=port, ptcp=ptcp )
                    assigned = True
                if not assigned:
                    main.log.error( self.name + ": Not able to find switch " + switch )
                    assignResult = main.FALSE
                index += 1
            return assignResult

        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def pingall( self, protocol="IPv4", timeout=300, shortCircuit=False, acceptableFailed=0 ):
        """
        Description:
            Verifies the reachability of the hosts using ping command.
        Optional:
            protocol - use ping6 command if specified as "IPv6"
            timeout( seconds ) - How long to wait before breaking the pingall
            shortCircuit - Break the pingall based on the number of failed hosts ping
            acceptableFailed - Set the number of acceptable failed pings for the
                               function to still return main.TRUE
        Returns:
            main.TRUE if pingall completes with no pings dropped
            otherwise main.FALSE
        """
        try:
            timeout = int( timeout )
            main.log.info( self.name + ": Checking reachabilty to the hosts using ping" )
            failedPings = 0
            returnValue = main.TRUE
            ipv6 = True if protocol == "IPv6" else False
            startTime = time.time()
            hostPairs = itertools.permutations( list( self.hosts.values() ), 2 )
            for hostPair in list( hostPairs ):
                ipDst = hostPair[ 1 ].options[ 'ip6' ] if ipv6 else hostPair[ 1 ].options[ 'ip' ]
                pingResult = hostPair[ 0 ].ping( ipDst, ipv6=ipv6 )
                returnValue = returnValue and pingResult
                if ( time.time() - startTime ) > timeout:
                    returnValue = main.FALSE
                    main.log.error( self.name +
                                    ": Aborting pingall - " +
                                    "Function took too long " )
                    break
                if not pingResult:
                    failedPings = failedPings + 1
                    if failedPings > acceptableFailed:
                        returnValue = main.FALSE
                        if shortCircuit:
                            main.log.error( self.name +
                                            ": Aborting pingall - "
                                            + str( failedPings ) +
                                            " pings failed" )
                            break
            return returnValue
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def pingallHosts( self, hostList, ipv6=False, wait=1, useScapy=False ):
        """
            Ping all specified IPv4 hosts

            Acceptable hostList:
                - [ 'h1','h2','h3','h4' ]

            Returns main.TRUE if all hosts specified can reach
            each other

            Returns main.FALSE if one or more of hosts specified
            cannot reach each other"""
        hostComponentList = []
        for hostName in hostList:
            hostComponent = self.hosts[ str( hostName ) ]
            if hostComponent:
                hostComponentList.append( hostComponent )
        try:
            main.log.info( "Testing reachability between specified hosts" )
            isReachable = main.TRUE
            pingResponse = "IPv4 ping across specified hosts\n"
            failedPings = 0
            hostPairs = itertools.permutations( list( hostComponentList ), 2 )
            for hostPair in list( hostPairs ):
                ipDst = hostPair[ 1 ].options.get( 'ip6', hostPair[ 1 ].options[ 'ip' ] ) if ipv6 else hostPair[ 1 ].options[ 'ip' ]
                srcIface = hostPair[ 0 ].interfaces[0].get( 'name' )
                dstIface = hostPair[ 1 ].interfaces[0].get( 'name' )
                srcMac = hostPair[0].interfaces[0].get( 'mac' )
                dstMac = hostPair[1].interfaces[0].get( 'mac' )
                if useScapy:
                    main.log.debug( "Pinging from " + str( hostPair[ 0 ].shortName ) + " to " + str( hostPair[ 1 ].shortName ) )
                    srcIPs = hostPair[ 0 ].interfaces[0].get( 'ips' )
                    dstIPs = hostPair[ 1 ].interfaces[0].get( 'ips' )
                    srcVLANs = hostPair[0].interfaces[0].get( 'vlan', [None] )
                    main.log.debug( srcVLANs )
                    for VLAN in srcVLANs:
                        pingResponse += hostPair[ 0 ].options[ 'shortName' ]
                        if VLAN:
                            pingResponse += "." + str( VLAN )
                        pingResponse += " -> "
                        main.log.debug( VLAN )
                        dstVLANs = hostPair[1].interfaces[0].get( 'vlan' )
                        # Use scapy to send and recieve packets
                        hostPair[ 1 ].startScapy( ifaceName=dstIface )
                        filters = []
                        if srcMac:
                            filters.append( "ether src host %s" % srcMac )
                        if srcIPs[0]:
                            filters.append( "ip src host %s" % srcIPs[0] )
                        hostPair[ 1 ].startFilter( ifaceName=dstIface, pktFilter=" and ".join(filters) )
                        hostPair[ 0 ].startScapy( ifaceName=srcIface )
                        hostPair[ 0 ].buildEther( src=srcMac, dst=dstMac )
                        if VLAN:
                            hostPair[ 0 ].buildVLAN( vlan=VLAN )
                        hostPair[ 0 ].buildIP( src=srcIPs[0], dst=dstIPs[0] )
                        hostPair[ 0 ].buildICMP( vlan=VLAN )
                        hostPair[ 0 ].sendPacket( iface=srcIface )

                        waiting = not hostPair[ 1 ].checkFilter()
                        if not waiting:
                            pingResult = main.FALSE
                            packets = hostPair[ 1 ].readPackets()
                            main.log.warn( repr( packets ) )
                            for packet in packets.splitlines():
                                main.log.debug( packet )
                                if srcIPs[0] in packet:
                                    pingResult = main.TRUE
                        else:
                            main.log.warn( "Did not receive packets, killing filter" )
                            kill = hostPair[ 1 ].killFilter()
                            main.log.debug( kill )
                            hostPair[ 1 ].handle.sendline( "" )
                            hostPair[ 1 ].handle.expect( hostPair[ 1 ].scapyPrompt )
                            main.log.debug( hostPair[ 1 ].handle.before )
                            # One of the host to host pair is unreachable
                            pingResult = main.FALSE
                        hostPair[ 0 ].stopScapy()
                        hostPair[ 1 ].stopScapy()
                        if pingResult:
                            pingResponse += hostPair[ 1 ].options[ 'shortName' ]
                            if VLAN:
                                pingResponse += "." + str( VLAN )
                        else:
                            pingResponse += "X"
                            # One of the host to host pair is unreachable
                            isReachable = main.FALSE
                            failedPings += 1
                        pingResponse += "\n"
                else:
                    pingResponse += hostPair[ 0 ].options[ 'shortName' ] + " -> "
                    pingResult = hostPair[ 0 ].ping( ipDst, interface=srcIface, wait=int( wait ) )
                    if pingResult:
                        pingResponse += hostPair[ 1 ].options[ 'shortName' ]
                        if VLAN:
                            pingResponse += "." + str( VLAN )
                    else:
                        pingResponse += "X"
                        # One of the host to host pair is unreachable
                        isReachable = main.FALSE
                        failedPings += 1
                    pingResponse += "\n"
            main.log.info( pingResponse + "Failed pings: " + str( failedPings ) )
            return isReachable
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def pingallHostsUnidirectional( self, srcList, dstList, ipv6=False, wait=1, acceptableFailed=0, useScapy=False ):
        """
        Verify ping from each host in srcList to each host in dstList

        acceptableFailed: max number of acceptable failed pings

        Returns main.TRUE if all src hosts can reach all dst hosts
        Returns main.FALSE if one or more of src hosts cannot reach one or more of dst hosts
        """
        try:
            main.log.info( "Verifying ping from each src host to each dst host" )

            srcComponentList = []
            for hostName in srcList:
                hostComponent = self.hosts[ hostName ]
                if hostComponent:
                    main.log.debug( repr( hostComponent ) )
                    srcComponentList.append( hostComponent )
            dstComponentList = []
            for hostName in dstList:
                hostComponent = self.hosts[ hostName ]
                if hostComponent:
                    main.log.debug( repr( hostComponent ) )
                    dstComponentList.append( hostComponent )

            isReachable = main.TRUE
            wait = int( wait )
            cmd = " ping" + ("6" if ipv6 else "") + " -c 1 -i 1 -W " + str( wait ) + " "
            pingResponse = "Ping output:\n"
            failedPingsTotal = 0
            for srcHost in srcComponentList:
                pingResponse += str( str( srcHost.shortName ) + " -> " )
                for dstHost in dstComponentList:
                    failedPings = 0
                    dstIP = dstHost.ip_address
                    assert dstIP, "Not able to get IP address of host {}".format( dstHost )
                    for iface in srcHost.interfaces:
                        # FIXME This only works if one iface name is configured
                        # NOTE: We can use an IP with -I instead of an interface name as well
                        name = iface.get( 'name' )
                        if name:
                            cmd += " -I %s " % name

                    if useScapy:
                        while failedPings <= acceptableFailed:
                            main.log.debug( "Pinging from " + str( srcHost.shortName ) + " to " + str( dstHost.shortName ) )
                            # Use scapy to send and recieve packets
                            dstHost.startFilter()
                            srcHost.buildEther( src=srcHost.interfaces[0].get( 'mac'), dst=dstHost.interfaces[0].get( 'mac') )
                            srcHost.sendPacket()
                            output = dstHost.checkFilter()
                            main.log.debug( output )
                            if output:
                                # TODO: parse output?
                                packets = dstHost.readPackets()
                                for packet in packets.splitlines():
                                    main.log.debug( packet )
                                pingResponse += " " + str( dstHost.shortName )
                                break
                            else:
                                kill = dstHost.killFilter()
                                main.log.debug( kill )
                                dstHost.handle.sendline( "" )
                                dstHost.handle.expect( dstHost.scapyPrompt )
                                main.log.debug( dstHost.handle.before )
                                failedPings += 1
                                time.sleep(1)
                        if failedPings > acceptableFailed:
                            # One of the host to host pair is unreachable
                            pingResponse += " X"
                            isReachable = main.FALSE
                            failedPingsTotal += 1

                    else:
                        pingCmd = cmd + str( dstIP )
                        while failedPings <= acceptableFailed:
                            main.log.debug( "Pinging from " + str( srcHost.shortName ) + " to " + str( dstHost.shortName ) )
                            self.handle.sendline( pingCmd )
                            self.handle.expect( self.prompt, timeout=wait + 5 )
                            response = self.handle.before
                            if re.search( ',\s0\%\spacket\sloss', response ):
                                pingResponse += " " + str( dstHost.shortName )
                                break
                            else:
                                failedPings += 1
                                time.sleep(1)
                        if failedPings > acceptableFailed:
                            # One of the host to host pair is unreachable
                            pingResponse += " X"
                            isReachable = main.FALSE
                            failedPingsTotal += 1
                pingResponse += "\n"
            main.log.info( pingResponse + "Failed pings: " + str( failedPingsTotal ) )
            return isReachable
        except AssertionError:
            main.log.exception( "" )
            return main.FALSE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception" )
            response = self.handle.before
            # NOTE: Send ctrl-c to make sure command is stopped
            self.exitFromCmd( [ "Interrupt", self.prompt ] )
            response += self.handle.before + self.handle.after
            self.handle.sendline( "" )
            self.handle.expect( self.prompt )
            response += self.handle.before + self.handle.after
            main.log.debug( response )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def iperftcp( self, host1="h1", host2="h2", timeout=6 ):
        '''
        Creates an iperf TCP test between two hosts. Returns main.TRUE if test results
        are valid.
        Optional:
            timeout: The defualt timeout is 6 sec to allow enough time for a successful test to complete,
            and short enough to stop an unsuccessful test from quiting and cleaning up mininet.
        '''
        main.log.info( self.name + ": Simple iperf TCP test between two hosts" )
        # TODO: complete this function
        return main.TRUE

    def update( self ):
        return main.TRUE

    def verifyHostIp( self, hostList=[], prefix="", update=False ):
        """
        Description:
            Verify that all hosts have IP address assigned to them
        Optional:
            hostList: If specified, verifications only happen to the hosts
            in hostList
            prefix: at least one of the ip address assigned to the host
            needs to have the specified prefix
        Returns:
            main.TRUE if all hosts have specific IP address assigned;
            main.FALSE otherwise
        """
        try:
            if not hostList:
                hostList = self.hosts.keys()
            for hostName, hostComponent in self.hosts.items():
                if hostName not in hostList:
                    continue
                ipList = []
                ipa = hostComponent.ip()
                ipv4Pattern = r'inet ((?:[0-9]{1,3}\.){3}[0-9]{1,3})/'
                ipList += re.findall( ipv4Pattern, ipa )
                # It's tricky to make regex for IPv6 addresses and this one is simplified
                ipv6Pattern = r'inet6 ((?:[0-9a-fA-F]{1,4})?(?:[:0-9a-fA-F]{1,4}){1,7}(?:::)?(?:[:0-9a-fA-F]{1,4}){1,7})/'
                ipList += re.findall( ipv6Pattern, ipa )
                main.log.debug( self.name + ": IP list on host " + str( hostName ) + ": " + str( ipList ) )
                if not ipList:
                    main.log.warn( self.name + ": Failed to discover any IP addresses on host " + str( hostName ) )
                else:
                    if not any( ip.startswith( str( prefix ) ) for ip in ipList ):
                        main.log.warn( self.name + ": None of the IPs on host " + str( hostName ) + " has prefix " + str( prefix ) )
                    else:
                        main.log.debug( self.name + ": Found matching IP on host " + str( hostName ) )
                        hostList.remove( hostName )
            return main.FALSE if hostList else main.TRUE
        except KeyError:
            main.log.exception( self.name + ": host data not as expected: " + self.hosts.keys() )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception" )
            return None

    def addRoute( self, host, dstIP, interface, ipv6=False ):
        """
        Add a route to host
        Ex: h1 route add -host 224.2.0.1 h1-eth0
        """
        try:
            if ipv6:
                cmd = "sudo route -A inet6 add "
            else:
                cmd = "sudo route add -host "
            cmd += str( dstIP ) + " " + str( interface )
            response = self.runCmdOnHost( host, cmd )
            main.log.debug( "response = " + response )
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getIPAddress( self, host, iface=None, proto='IPV4' ):
        """
        Returns IP address of the host
        """
        hostComponent = self.hosts[ host ]
        if hostComponent:
            return hostComponent.getIPAddress( iface=iface, proto=proto )
        else:
            main.log.warn( self.name + ": Could not find host with short name '%s'" % host )
            return None

    def getLinkRandom( self, timeout=60, nonCut=True, excludeNodes=[], skipLinks=[] ):
        """
        Randomly get a link from network topology.
        If nonCut is True, it gets a list of non-cut links (the deletion
        of a non-cut link will not increase the number of connected
        component of a graph) and randomly returns one of them, otherwise
        it just randomly returns one link from all current links.
        excludeNodes will be passed to getLinks and getGraphDict method.
        Any link that has either end included in skipLinks will be excluded.
        Returns the link as a list, e.g. [ 's1', 's2' ].
        """
        candidateLinks = []
        try:
            if not nonCut:
                links = self.getLinks( timeout=timeout, excludeNodes=excludeNodes )
                assert len( links ) != 0
                for link in links:
                    # Exclude host-switch link
                    if link[ 'node1' ].startswith( 'h' ) or link[ 'node2' ].startswith( 'h' ):
                        continue
                    candidateLinks.append( [ link[ 'node1' ], link[ 'node2' ] ] )
            else:
                graphDict = self.getGraphDict( timeout=timeout, useId=False,
                                               excludeNodes=excludeNodes )
                if graphDict is None:
                    return None
                self.graph.update( graphDict )
                candidateLinks = self.graph.getNonCutEdges()
            candidateLinks = [ link for link in candidateLinks
                               if link[0] not in skipLinks and link[1] not in skipLinks ]
            if candidateLinks is None:
                return None
            elif len( candidateLinks ) == 0:
                main.log.info( self.name + ": No candidate link for deletion" )
                return None
            else:
                link = random.sample( candidateLinks, 1 )
                return link[ 0 ]
        except KeyError:
            main.log.exception( self.name + ": KeyError exception found" )
            return None
        except AssertionError:
            main.log.exception( self.name + ": AssertionError exception found" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception" )
            return None

    def getSwitchRandom( self, timeout=60, nonCut=True, excludeNodes=[], skipSwitches=[] ):
        """
        Randomly get a switch from network topology.
        If nonCut is True, it gets a list of non-cut switches (the deletion
        of a non-cut switch will not increase the number of connected
        components of a graph) and randomly returns one of them, otherwise
        it just randomly returns one switch from all current switches in
        Mininet.
        excludeNodes will be pased to getSwitches and getGraphDict method.
        Switches specified in skipSwitches will be excluded.
        Returns the name of the chosen switch.
        """
        candidateSwitches = []
        try:
            if not nonCut:
                switches = self.getSwitches( timeout=timeout, excludeNodes=excludeNodes )
                assert len( switches ) != 0
                for switchName in switches.keys():
                    candidateSwitches.append( switchName )
            else:
                graphDict = self.getGraphDict( timeout=timeout, useId=False,
                                               excludeNodes=excludeNodes )
                if graphDict is None:
                    return None
                self.graph.update( graphDict )
                candidateSwitches = self.graph.getNonCutVertices()
            candidateSwitches = [ switch for switch in candidateSwitches if switch not in skipSwitches ]
            if candidateSwitches is None:
                return None
            elif len( candidateSwitches ) == 0:
                main.log.info( self.name + ": No candidate switch for deletion" )
                return None
            else:
                switch = random.sample( candidateSwitches, 1 )
                return switch[ 0 ]
        except KeyError:
            main.log.exception( self.name + ": KeyError exception found" )
            return None
        except AssertionError:
            main.log.exception( self.name + ": AssertionError exception found" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception" )
            return None

    def getGraphDict( self, timeout=60, useId=True, includeHost=False,
                      excludeNodes=[] ):
        """
        Return a dictionary which describes the latest network topology data as a
        graph.
        An example of the dictionary:
        { vertex1: { 'edges': ..., 'name': ..., 'protocol': ... },
          vertex2: { 'edges': ..., 'name': ..., 'protocol': ... } }
        Each vertex should at least have an 'edges' attribute which describes the
        adjacency information. The value of 'edges' attribute is also represented by
        a dictionary, which maps each edge (identified by the neighbor vertex) to a
        list of attributes.
        An example of the edges dictionary:
        'edges': { vertex2: { 'port': ..., 'weight': ... },
                   vertex3: { 'port': ..., 'weight': ... } }
        If useId == True, dpid/mac will be used instead of names to identify
        vertices, which is helpful when e.g. comparing network topology with ONOS
        topology.
        If includeHost == True, all hosts (and host-switch links) will be included
        in topology data.
        excludeNodes will be passed to getSwitches and getLinks methods to exclude
        unexpected switches and links.
        """
        # TODO: support excludeNodes
        graphDict = {}
        try:
            links = self.getLinks( timeout=timeout, excludeNodes=excludeNodes )
            portDict = {}
            switches = self.getSwitches( excludeNodes=excludeNodes )
            if includeHost:
                hosts = self.getHosts()
            for link in links:
                # TODO: support 'includeHost' argument
                if link[ 'node1' ].startswith( 'h' ) or link[ 'node2' ].startswith( 'h' ):
                    continue
                nodeName1 = link[ 'node1' ]
                nodeName2 = link[ 'node2' ]
                if not self.switches[ nodeName1 ].isup or not self.switches[ nodeName2 ].isup:
                    continue
                port1 = link[ 'port1' ]
                port2 = link[ 'port2' ]
                # Loop for two nodes
                for i in range( 2 ):
                    portIndex = port1
                    if useId:
                        node1 = 'of:' + str( switches[ nodeName1 ][ 'dpid' ] )
                        node2 = 'of:' + str( switches[ nodeName2 ][ 'dpid' ] )
                    else:
                        node1 = nodeName1
                        node2 = nodeName2
                    if node1 not in graphDict.keys():
                        if useId:
                            graphDict[ node1 ] = { 'edges': {},
                                                   'dpid': switches[ nodeName1 ][ 'dpid' ],
                                                   'name': nodeName1,
                                                   'ports': switches[ nodeName1 ][ 'ports' ],
                                                   'swClass': switches[ nodeName1 ][ 'swClass' ],
                                                   'pid': switches[ nodeName1 ][ 'pid' ],
                                                   'options': switches[ nodeName1 ][ 'options' ] }
                        else:
                            graphDict[ node1 ] = { 'edges': {} }
                    else:
                        # Assert node2 is not connected to any current links of node1
                        # assert node2 not in graphDict[ node1 ][ 'edges' ].keys()
                        pass
                    for port in switches[ nodeName1 ][ 'ports' ]:
                        if port[ 'of_port' ] == str( portIndex ):
                            # Use -1 as index for disabled port
                            if port[ 'enabled' ]:
                                graphDict[ node1 ][ 'edges' ][ node2 ] = { 'port': portIndex }
                            else:
                                graphDict[ node1 ][ 'edges' ][ node2 ] = { 'port': -1 }
                    # Swap two nodes/ports
                    nodeName1, nodeName2 = nodeName2, nodeName1
                    port1, port2 = port2, port1
            # Remove links with disabled ports
            linksToRemove = []
            for node, edges in graphDict.items():
                for neighbor, port in edges[ 'edges' ].items():
                    if port[ 'port' ] == -1:
                        linksToRemove.append( ( node, neighbor ) )
            for node1, node2 in linksToRemove:
                for i in range( 2 ):
                    if graphDict.get( node1 )[ 'edges' ].get( node2 ):
                        graphDict[ node1 ][ 'edges' ].pop( node2 )
                    node1, node2 = node2, node1
            return graphDict
        except KeyError:
            main.log.exception( self.name + ": KeyError exception found" )
            return None
        except AssertionError:
            main.log.exception( self.name + ": AssertionError exception found" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception" )
            return None

    def switch( self, **switchargs ):
        """
        start/stop a switch
        """
        args = utilities.parse_args( [ "SW", "OPTION" ], **switchargs )
        sw = args[ "SW" ] if args[ "SW" ] is not None else ""
        option = args[ "OPTION" ] if args[ "OPTION" ] is not None else ""
        try:
            switchComponent = self.switches[ sw ]
            if option == 'stop':
                switchComponent.stopOfAgent()
            elif option == 'start':
                switchComponent.startOfAgent()
            else:
                main.log.warn( self.name + ": Unknown switch command" )
                return main.FALSE
            return main.TRUE
        except KeyError:
            main.log.error( self.name + ": Not able to find switch [}".format( sw ) )
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception" )
            main.cleanAndExit()

    def discoverHosts( self, hostList=[], wait=1000, dstIp="6.6.6.6", dstIp6="1020::3fe" ):
        '''
        Hosts in hostList will do a single ARP/ND to a non-existent address for ONOS to
        discover them. A host will use arping/ndisc6 to send ARP/ND depending on if it
        has IPv4/IPv6 addresses configured.
        Optional:
            hostList: a list of names of the hosts that need to be discovered. If not
                      specified mininet will send ping from all the hosts
            wait: timeout for ARP/ND in milliseconds
            dstIp: destination address used by IPv4 hosts
            dstIp6: destination address used by IPv6 hosts
        Returns:
            main.TRUE if all packets were successfully sent. Otherwise main.FALSE
        '''
        try:
            hosts = self.getHosts()
            if not hostList:
                hostList = hosts.keys()
            discoveryResult = main.TRUE
            for host in hostList:
                flushCmd = ""
                cmd = ""
                intf = hosts[host]['interfaces'][0].get( 'name' )
                hostIp = self.getIPAddress( host, iface=intf ) or hosts[host]['interfaces'][0].get( 'ips', False )
                if hostIp:
                    flushCmd = "sudo ip neigh flush all"
                    intfStr = "-i {}".format( intf ) if intf else ""
                    srcIp = "-S {}".format( hostIp if isinstance( hostIp, types.StringType ) else hostIp[0] ) if intf else ""
                    cmd = "sudo arping -c 1 -w {} {} {} {}".format( wait, intfStr, srcIp, dstIp )
                    main.log.debug( "Sending IPv4 arping from host {}".format( host ) )
                elif self.getIPAddress( host, proto='IPV6' ):
                    flushCmd = "sudo ip -6 neigh flush all"
                    intf = hosts[host]['interfaces'][0]['name']
                    cmd = "ndisc6 -r 1 -w {} {} {}".format( wait, dstIp6, intf )
                    main.log.debug( "Sending IPv6 ND from host {}".format( host ) )
                else:
                    main.log.warn( "No IP addresses configured on host {}, skipping discovery".format( host ) )
                    discoveryResult = main.FALSE
                if cmd:
                    self.runCmdOnHost( host, flushCmd )
                    self.runCmdOnHost( host, cmd )
            return discoveryResult
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()
