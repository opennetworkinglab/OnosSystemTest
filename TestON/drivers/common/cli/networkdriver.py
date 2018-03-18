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
import types
from drivers.common.clidriver import CLI

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
        super( NetworkDriver, self ).__init__()

    def checkOptions( self, var, defaultVar ):
        if var is None or var == "":
            return defaultVar
        return var

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
                    if value[ 'type' ] in [ 'MininetSwitchDriver', 'OFDPASwitchDriver' ]:
                        self.switches[ key ] = getattr( main, key )
                    elif value[ 'type' ] in [ 'MininetHostDriver', 'HostDriver' ]:
                        self.hosts[ key ] = getattr( main, key )
            return main.TRUE
        except Exception:
            main.log.error( self.name + ": failed to connect to network" )
            return main.FALSE

    def getHosts( self, verbose=False, updateTimeout=1000 ):
        """
        Return a dictionary which maps short names to host data
        """
        hosts = {}
        try:
            for hostComponent in self.hosts.values():
                # TODO: return more host data
                hosts[ hostComponent.options[ 'shortName' ] ] = {}
        except Exception:
            main.log.error( self.name + ": host component not as expected" )
        return hosts

    def getMacAddress( self, host ):
        """
        Return MAC address of a host
        """
        import re
        try:
            hostComponent = self.getHostComponentByShortName( host )
            response = hostComponent.ifconfig()
            pattern = r'HWaddr\s([0-9A-F]{2}[:-]){5}([0-9A-F]{2})'
            macAddressSearch = re.search( pattern, response, re.I )
            macAddress = macAddressSearch.group().split( " " )[ 1 ]
            main.log.info( self.name + ": Mac-Address of Host " + host + " is " + macAddress )
            return macAddress
        except Exception:
            main.log.error( self.name + ": failed to get host MAC address" )

    def getSwitchComponentByShortName( self, shortName ):
        """
        Get switch component by its short name i.e. "s1"
        """
        for switchComponent in self.switches.values():
            if switchComponent.options[ 'shortName' ] == shortName:
                return switchComponent
        main.log.warn( self.name + ": failed to find switch component by name " + shortName )
        return None

    def getHostComponentByShortName( self, shortName ):
        """
        Get host component by its short name i.e. "h1"
        """
        for hostComponent in self.hosts.values():
            if hostComponent.options[ 'shortName' ] == shortName:
                return hostComponent
        main.log.warn( self.name + ": failed to find host component by name " + shortName )
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
                switchComponent = self.getSwitchComponentByShortName( switch )
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
        import time
        import itertools
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

    def pingallHosts( self, hostList, wait=1 ):
        """
            Ping all specified IPv4 hosts

            Acceptable hostList:
                - [ 'h1','h2','h3','h4' ]

            Returns main.TRUE if all hosts specified can reach
            each other

            Returns main.FALSE if one or more of hosts specified
            cannot reach each other"""
        import time
        import itertools
        hostComponentList = []
        for hostName in hostList:
            hostComponent = self.getHostComponentByShortName( hostName )
            if hostComponent:
                hostComponentList.append( hostComponent )
        try:
            main.log.info( "Testing reachability between specified hosts" )
            isReachable = main.TRUE
            pingResponse = "IPv4 ping across specified hosts\n"
            failedPings = 0
            hostPairs = itertools.permutations( list( hostComponentList ), 2 )
            for hostPair in list( hostPairs ):
                pingResponse += hostPair[ 0 ].options[ 'shortName' ] + " -> "
                ipDst = hostPair[ 1 ].options[ 'ip6' ] if ipv6 else hostPair[ 1 ].options[ 'ip' ]
                pingResult = hostPair[ 0 ].ping( ipDst, wait=int( wait ) )
                if pingResult:
                    pingResponse += hostPair[ 1 ].options[ 'shortName' ]
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
