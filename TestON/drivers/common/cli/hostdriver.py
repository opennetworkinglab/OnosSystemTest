#!/usr/bin/env python
"""
Copyright 2018 Open Networking Foundation (ONF)

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

import pexpect
import re
import os
from drivers.common.cli.emulator.scapyclidriver import ScapyCliDriver

class HostDriver( ScapyCliDriver ):
    """
    This class is created as a standalone host driver.
    """
    def __init__( self ):
        super( HostDriver, self ).__init__()
        self.handle = self
        self.name = None
        self.shortName = None
        self.interfaces = []
        self.home = None
        self.inband = False
        self.prompt = "\$"
        self.scapyPrompt = ">>>"
        self.tempRoutes = []

    def connect( self, **connectargs ):
        """
        Creates ssh handle for host.
        NOTE:
        The ip_address would come from the topo file using the host tag, the
        value can be an environment variable as well as a "localhost" to get
        the ip address needed to ssh to the "bench"
        """
        try:
            for key in connectargs:
                vars( self )[ key ] = connectargs[ key ]
            self.name = self.options[ 'name' ]
            self.shortName = self.options[ 'shortName' ]
            self.interfaces.append( { 'ips': [ self.options[ 'ip' ] ],
                                      'isUp': True,
                                      'mac': self.options[ 'mac' ],
                                      'dhcp': self.options.get( 'dhcp', "False" ),
                                      'name': self.options.get( 'ifaceName', None ) } )

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

            self.handle = super(
                HostDriver,
                self ).connect(
                user_name=self.user_name,
                ip_address=self.ip_address,
                port=None,
                pwd=self.pwd )

            # Update IP of interfaces if using dhcp
            for intf in self.interfaces:
                if intf[ 'dhcp' ].lower() == "true":
                    ip = self.getIPAddress( iface=intf[ 'name' ] )
                    if ip:
                        intf['ips'] = [ ip ]
                    else:
                        main.log.warn( self.name + ": Could not find IP of %s" % intf[ 'name' ] )

            if self.handle:
                main.log.info( "Connection successful to the " +
                               self.user_name +
                               "@" +
                               self.ip_address )
                self.handle.sendline( "" )
                self.handle.expect( self.prompt )
                return main.TRUE
            else:
                main.log.error( "Connection failed to " +
                                self.user_name +
                                "@" +
                                self.ip_address )
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def disconnect( self, **connectargs ):
        """
        Called when test is complete to disconnect the handle.
        """
        response = main.TRUE
        try:
            if self.handle:
                self.preDisconnect()
                if self.tempRoutes:
                    for r in self.tempRoutes:
                        self.deleteRoute( *r )
                # Disconnect from the host
                if not self.options.get( 'inband', False ) == 'True':
                    self.handle.sendline( "" )
                    self.handle.expect( self.prompt )
                    self.handle.sendline( "exit" )
                    i = self.handle.expect( [ "closed", pexpect.TIMEOUT ] )
                    if i == 1:
                        main.log.error( self.name + ": timeout when waiting for response" )
                        main.log.error( self.name + ": response: " + str( self.handle.before ) )
                else:
                    self.handle.sendline( "" )
                    i = self.handle.expect( [ self.prompt, pexpect.TIMEOUT ], timeout=2 )
                    if i == 1:
                        main.log.warn( self.name + ": timeout when waiting for response" )
                        main.log.warn( self.name + ": response: " + str( self.handle.before ) )
                    self.handle.sendline( "exit" )
                    i = self.handle.expect( [ "closed", pexpect.TIMEOUT ], timeout=2 )
                    if i == 1:
                        main.log.warn( self.name + ": timeout when waiting for response" )
                        main.log.warn( self.name + ": response: " + str( self.handle.before ) )
                return main.TRUE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            response = main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
        except ValueError:
            main.log.exception( "Exception in disconnect of " + self.name )
            response = main.TRUE
        except Exception:
            main.log.exception( self.name + ": Connection failed to the host" )
            response = main.FALSE
        return response

    def connectInband( self ):
        """
        ssh to the host using its data plane IP
        """
        try:
            if not self.options[ 'inband' ] == 'True':
                main.log.info( "Skip connecting the host via data plane" )
                return main.TRUE
            self.handle.sendline( "" )
            self.handle.expect( self.prompt )
            self.handle.sendline( "ssh {}@{}".format( self.options[ 'username' ],
                                                      self.options[ 'ip' ] ) )
            i = self.handle.expect( [ "password:|Password:", self.prompt, pexpect.TIMEOUT ], timeout=30 )
            if i == 0:
                self.handle.sendline( self.options[ 'password' ] )
                j = self.handle.expect( [ "password:|Password:", self.prompt, pexpect.TIMEOUT ], timeout=10 )
                if j != 1:
                    main.log.error( "Incorrect password" )
                    return main.FALSE
            elif i == 1:
                main.log.info( "Password not required logged in" )
            else:
                main.log.error( "Failed to connect to the host" )
                return main.FALSE
            self.inband = True
            return main.TRUE
        except KeyError:
            main.log.error( self.name + ": host component not as expected" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE

    def disconnectInband( self ):
        """
        Terminate the ssh connection to the host's data plane IP
        """
        try:
            if not self.options[ 'inband' ] == 'True':
                main.log.info( "Skip disconnecting the host via data plane" )
                return main.TRUE
            self.handle.sendline( "" )
            self.handle.expect( self.prompt, timeout=2 )
            self.handle.sendline( "exit" )
            i = self.handle.expect( [ "closed", pexpect.TIMEOUT ], timeout=2 )
            if i == 1:
                main.log.error( self.name + ": timeout when waiting for response" )
                main.log.error( self.name + ": response: " + str( self.handle.before ) )
            return main.TRUE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE

    def getRoutes( self ):
        """
        Returns the output of 'ip route show' command
        # TODO: process and return a a list or json object
        """
        try:
            cmd = "ip route show"
            self.handle.sendline( cmd )
            i = self.handle.expect( [ "password|Password", self.prompt ]  )
            if i == 0:
                self.handle.sendline( self.pwd )
                j = self.handle.expect( [ "password|Password", self.prompt ] )
                if j != 1:
                    main.log.error( "Incorrect password" )
                    return main.FALSE
            return self.handle.before
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE

    def addRouteToHost( self, route, gw, interface=None, sudoRequired=True, purgeOnDisconnect=True ):
        """
        Adds a static route to the host
        Arguments:
        * route - String, CIDR notation for the destination subnet
        * gw - String, IP address of gateway
        Optional Arguments:
        * interface - String, The interface to use for this route, defaults to None, or the default interface
        * sudoRequired - Boolean, whether sudo is needed for this command, defaults to True
        * purgeOnDisconnect - Boolean, remove this route before disconnecting from component
        """
        try:
            cmd = "ip route add %s via %s" % ( route, gw )
            if sudoRequired:
                cmd = "sudo %s" % cmd
            if interface:
                cmd = "%s dev %s" % ( cmd, interface )
            if purgeOnDisconnect:
                self.tempRoutes.append( (route, gw, interface, sudoRequired ) )
            self.handle.sendline( cmd )
            i = self.handle.expect( [ "password|Password", self.prompt, "Error" ]  )
            output = ""
            if i == 2:
                output += self.handle.before + self.handle.after
                self.handle.expect( self.prompt )
                output += self.handle.before + self.handle.after
                main.log.error( "%s: Erorr in ip route command: %s" % ( self.name, output ) )
                return main.FALSE
            elif i == 0:
                self.handle.sendline( self.pwd )
                j = self.handle.expect( [ "password|Password", self.prompt, "Error" ] )
                if j == 0:
                    main.log.error( "Incorrect password" )
                    return main.FALSE
                elif j == 2:
                    output += self.handle.before + self.handle.after
                    self.handle.expect( self.prompt )
                    output += self.handle.before + self.handle.after
                    main.log.error( "%s: Erorr in ip route command: %s" % ( self.name, output ) )
                    return main.FALSE
            output += self.handle.before + self.handle.after
            main.log.debug( output )
            return self.handle.before
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE

    def deleteRoute( self, route, gw, interface=None, sudoRequired=True ):
        """
        Deletess a static route from the host
        Arguments:
        * route - String, CIDR notation for the destination subnet
        * gw - String, IP address of gateway
        Optional Arguments:
        * interface - String, The interface to use for this route, defaults to None, or the default interface
        * sudoRequired - Boolean, whether sudo is needed for this command, defaults to True
        """
        try:
            cmd = "ip route del %s via %s" % ( route, gw )
            if sudoRequired:
                cmd = "sudo %s" % cmd
            if interface:
                cmd = "%s dev %s" % ( cmd, interface )
            self.handle.sendline( cmd )
            i = self.handle.expect( [ "password|Password", self.prompt, "Error" ]  )
            output = ""
            if i == 2:
                output += self.handle.before + self.handle.after
                self.handle.expect( self.prompt )
                output += self.handle.before + self.handle.after
                main.log.error( "%s: Erorr in ip route command: %s" % ( self.name, output ) )
                return main.FALSE
            elif i == 0:
                self.handle.sendline( self.pwd )
                j = self.handle.expect( [ "password|Password", self.prompt, "Error" ] )
                if j == 0:
                    main.log.error( "Incorrect password" )
                    return main.FALSE
                elif j == 2:
                    output += self.handle.before + self.handle.after
                    self.handle.expect( self.prompt )
                    output += self.handle.before + self.handle.after
                    main.log.error( "%s: Erorr in ip route command: %s" % ( self.name, output ) )
                    return main.FALSE
            output += self.handle.before + self.handle.after
            main.log.debug( output )
            return self.handle.before
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE

    def getIPAddress( self, iface=None, proto='IPV4' ):
        """
        Returns IP address of the host
        """
        cmd = "ifconfig %s" % iface if iface else ""
        response = self.command( cmd )
        if "Command 'ifconfig' not found" in response:
            # ip a show dev
            cmd = "ip addr show %s" % iface if iface else ""
            response = self.command( cmd )
            pattern = ''
            if proto == 'IPV4':
                pattern = "inet\s(\d+\.\d+\.\d+\.\d+)/\d+"
            else:
                pattern = "inet6\s([\w,:]*)/\d+"
        else:
            pattern = ''
            if proto == 'IPV4':
                pattern = "inet\s(\d+\.\d+\.\d+\.\d+)\s\snetmask"
            else:
                pattern = "inet6\s([\w,:]*)/\d+\s\sprefixlen"
        ipAddressSearch = re.search( pattern, response )
        if not ipAddressSearch:
            return None
        main.log.info(
            self.name +
            ": IP-Address is " +
            ipAddressSearch.group( 1 ) )
        return ipAddressSearch.group( 1 )

    def ping( self, dst, ipv6=False, interface=None, wait=3 ):
        """
        Description:
            Ping from this host to another
        Required:
            dst: IP address of destination host
        Optional:
            ipv6: will use ping6 command if True; otherwise use ping command
            interface: Specify which interface to use for the ping
            wait: timeout for ping command
        """
        try:
            command = "ping6" if ipv6 else "ping"
            if interface:
                command += " -I %s " % interface
            command += " -c 1 -i 1 -W " + str( wait ) + " " + str( dst )
            main.log.info( self.name + ": Sending: " + command )
            self.handle.sendline( command )
            i = self.handle.expect( [ self.prompt, pexpect.TIMEOUT ],
                                    timeout=wait + 5 )
            response = self.handle.before
            if i == 1:
                main.log.error(
                    self.name +
                    ": timeout when waiting for response" )
                main.log.error( self.name + ": response: " + str( self.handle.before ) )
            if re.search( ',\s0\%\spacket\sloss', response ):
                main.log.info( self.name + ": no packets lost, host is reachable" )
                return main.TRUE
            else:
                main.log.warn(
                    self.name +
                    ": PACKET LOST, HOST IS NOT REACHABLE" )
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def pingHostSetAlternative( self, dstIPList, wait=1, IPv6=False ):
        """
        Description:
            Ping a set of destination host.
        Params:
            dstIPList is a list of destination ip addresses
        Returns:
            main.TRUE if the destination host is reachable
            main.FALSE otherwise
        """
        isReachable = main.TRUE
        wait = int( wait )
        cmd = "ping"
        if IPv6:
            cmd = cmd + "6"
        cmd = cmd + " -c 1 -i 1 -W " + str( wait )
        try:
            for dstIP in dstIPList:
                pingCmd = cmd + " " + dstIP
                self.handle.sendline( pingCmd )
                i = self.handle.expect( [ self.prompt,
                                          pexpect.TIMEOUT ],
                                        timeout=wait + 5 )
                if i == 0:
                    response = self.handle.before
                    if not re.search( ',\s0\%\spacket\sloss', response ):
                        main.log.debug( "Ping failed between %s and %s" % ( self.name, dstIP ) )
                        isReachable = main.FALSE
                elif i == 1:
                    main.log.error( self.name + ": timeout when waiting for response" )
                    isReachable = main.FALSE
                else:
                    main.log.error( self.name + ": unknown response: " + self.handle.before )
                    isReachable = main.FALSE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception" )
            self.exitFromCmd( [ self.prompt ] )
            isReachable = main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()
        return isReachable

    def ifconfig( self, wait=3 ):
        """
        Run ifconfig command on host and return output
        """
        try:
            command = "ifconfig"
            main.log.info( self.name + ": Sending: " + command )
            self.handle.sendline( command )
            i = self.handle.expect( [ "Command 'ifconfig' not found", self.prompt, pexpect.TIMEOUT ],
                                    timeout=wait + 5 )
            if i == 0:
                response = self.handle.before
                self.handle.expect( [ self.prompt, pexpect.TIMEOUT ] )
                response += str( self.handle.before )
                main.log.error( self.name + ": Error running ifconfig: %s " % response )
                return response
            if i == 2:
                main.log.error(
                    self.name +
                    ": timeout when waiting for response" )
                main.log.error( self.name + ": response: " + str( self.handle.before ) )
            response = self.handle.before
            return response
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": uncaught exception!" )
            main.cleanAndExit()

    def ip( self, options="a", wait=3 ):
        """
        Run ip command on host and return output
        """
        try:
            command = "ip {}".format( options )
            main.log.info( self.name + ": Sending: " + command )
            self.handle.sendline( command )
            i = self.handle.expect( [ self.prompt, pexpect.TIMEOUT ],
                                    timeout=wait + 5 )
            if i == 1:
                main.log.error( self.name + ": timeout when waiting for response" )
                main.log.error( self.name + ": response: " + str( self.handle.before ) )
            response = self.handle.before
            return response
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": uncaught exception!" )
            main.cleanAndExit()

    def command( self, cmd, wait=3, debug=False):
        """
        Run shell command on host and return output
        Required:
            cmd: command to run on the host
        """
        try:
            main.log.info( self.name + ": Sending: " + cmd )
            self.handle.sendline( cmd )
            i = self.handle.expect( [ self.prompt, pexpect.TIMEOUT ],
                                    timeout=wait + 5 )
            response = self.handle.before
            if debug:
                main.log.debug( response )
            if i == 1:
                main.log.error( self.name + ": timeout when waiting for response" )
                main.log.error( self.name + ": response: " + str( response ) )
            return response
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": uncaught exception!" )
            main.cleanAndExit()
