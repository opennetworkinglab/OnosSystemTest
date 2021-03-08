#!/usr/bin/env python
"""
2015-2016
Copyright 2016 Open Networking Foundation (ONF)

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

ScapyCliDriver is the basic driver which will handle the Scapy functions

TODO: Add Explanation on how to install scapy
"""
import pexpect
import re
import sys
import os
from drivers.common.cli.emulatordriver import Emulator


class ScapyCliDriver( Emulator ):

    """
       ScapyCliDriver is the basic driver which will handle
       the Scapy functions"""
    def __init__( self ):
        super( ScapyCliDriver, self ).__init__()
        self.handle = self
        self.name = None
        self.home = "~/"
        self.wrapped = sys.modules[ __name__ ]
        self.flag = 0
        # TODO: Refactor driver to use these everywhere
        self.hostPrompt = "\$"
        self.scapyPrompt = ">>>"
        self.sudoRequired = True
        self.ifaceName = None

    def connect( self, **connectargs ):
        """
           Here the main is the TestON instance after creating
           all the log handles."""
        try:
            for key in connectargs:
                vars( self )[ key ] = connectargs[ key ]
            for key in self.options:
                if key == "home":
                    self.home = self.options[ key ]
                elif key == "name":
                    self.name = self.options[ key ]
                elif key == "sudo_required":
                    self.sudoRequired = False if self.options[ key ] == "false" else True
                elif key == "ifaceName":
                    self.ifaceName = self.options[ key ]
            if self.ifaceName is None:
                self.ifaceName = self.name + "-eth0"

            # Parse route config
            self.routes = []
            routes = self.options.get( 'routes' )
            if routes:
                for route in routes:
                    route = routes[ route ]
                    iface = route.get( 'interface' )
                    if not iface:
                        iface = None
                    self.routes.append( { 'network': route[ 'network' ],
                                          'netmask': route[ 'netmask' ],
                                          'gw': route.get( 'gw' ),
                                          'interface': iface } )
            try:
                if os.getenv( str( self.ip_address ) ) is not None:
                    self.ip_address = os.getenv( str( self.ip_address ) )
                else:
                    main.log.info( self.name +
                                   ": Trying to connect to " +
                                   self.ip_address )

            except KeyError:
                main.log.info( self.name + ": Invalid host name," +
                               " connecting to local host instead" )
                self.ip_address = 'localhost'
            except Exception as inst:
                main.log.error( self.name + ": Uncaught exception: " + str( inst ) )

            self.handle = super(
                ScapyCliDriver,
                self ).connect(
                user_name=self.user_name,
                ip_address=self.ip_address,
                port=None,
                pwd=self.pwd )

            if self.handle:
                main.log.info( self.name + ": Connection successful to the host " +
                               self.user_name +
                               "@" +
                               self.ip_address )
                return self.handle
            else:
                main.log.error( "Connection failed to the host " +
                                self.user_name +
                                "@" +
                                self.ip_address )
                main.log.error( "Failed to connect to the Mininet Host" )
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
        Called at the end of the test to stop the scapy component and
        disconnect the handle.
        """
        main.log.debug( self.name + ": Disconnecting" )
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

    def startScapy( self, mplsPath="", ifaceName=None ):
        """
        Start the Scapy cli
        optional:
            mplsPath - The path where the MPLS class is located
            NOTE: This can be a relative path from the user's home dir
            ifaceName - the name of the default interface to use.
        """
        mplsLines = [ 'import imp',
                      'imp.load_source( "mplsClass", "{}mplsClass.py" )'.format( mplsPath ),
                      'from mplsClass import MPLS',
                      'bind_layers(Ether, MPLS, type = 0x8847)',
                      'bind_layers(MPLS, MPLS, bottom_of_label_stack = 0)',
                      'bind_layers(MPLS, IP)' ]

        try:
            main.log.debug( self.name + ": Starting scapy" )
            if self.sudoRequired:
                self.handle.sendline( "sudo scapy" )
            else:
                self.handle.sendline( "scapy" )
            i = self.handle.expect( [ "not found", "password for", self.scapyPrompt ] )
            if i == 1:
                main.log.debug( "Sudo asking for password" )
                main.log.sendline( self.pwd )
                i = self.handle.expect( [ "not found", self.scapyPrompt ] )
            if i == 0:
                output = self.handle.before + self.handle.after
                self.handle.expect( self.prompt )
                output += self.handle.before + self.handle.after
                main.log.debug( self.name + ": Scapy not installed, aborting test. \n" + output )
                main.cleanAndExit()
            self.handle.sendline( "conf.color_theme = NoTheme()" )
            self.handle.expect( self.scapyPrompt )
            response = self.cleanOutput( self.handle.before )
            self.handle.sendline( "conf.fancy_prompt = False" )
            self.handle.expect( self.scapyPrompt )
            response = self.cleanOutput( self.handle.before )
            self.handle.sendline( "conf.interactive = False" )
            self.handle.expect( "interactive" )
            self.handle.expect( self.scapyPrompt )
            response = self.cleanOutput( self.handle.before )
            self.handle.sendline( "" )
            self.handle.expect( self.scapyPrompt )
            response = self.cleanOutput( self.handle.before )
            if mplsPath:
                main.log.debug( self.name + ": Adding MPLS class" )
                main.log.debug( self.name + ": MPLS class path: " + mplsPath )
                for line in mplsLines:
                    main.log.debug( self.name + ": sending line: " + line )
                    self.handle.sendline( line )
                    self.handle.expect( self.scapyPrompt )
                    response = self.cleanOutput( self.handle.before )

            # Set interface
            if ifaceName:
                self.handle.sendline( 'conf.iface = "' + ifaceName + '"' )
            self.clearBuffer()
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return main.FALSE
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def stopScapy( self ):
        """
        Exit the Scapy cli
        """
        try:
            main.log.debug( self.name + ": Stopping scapy" )
            self.handle.sendline( "exit()" )
            self.handle.expect( self.hostPrompt )
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return main.FALSE
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def buildEther( self, **kwargs ):
        """
        Build an Ethernet frame

        Will create a frame class with the given options. If a field is
        left blank it will default to the below value unless it is
        overwritten by the next frame.
        Default frame:
        ###[ Ethernet ]###
          dst= ff:ff:ff:ff:ff:ff
          src= 00:00:00:00:00:00
          type= 0x800

        Returns main.TRUE or main.FALSE on error
        """
        try:
            main.log.debug( self.name + ": Building Ethernet Frame" )
            # Set the Ethernet frame
            cmd = 'ether = Ether( '
            options = []
            for key, value in kwargs.iteritems():
                if isinstance( value, str ):
                    value = '"' + value + '"'
                options.append( str( key ) + "=" + str( value ) )
            cmd += ", ".join( options )
            cmd += ' )'
            self.handle.sendline( cmd )
            self.handle.expect( self.scapyPrompt )
            response = self.cleanOutput( self.handle.before )
            if "Traceback" in response:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + response )
                return main.FALSE
            self.handle.sendline( "packet = ether" )
            self.handle.expect( self.scapyPrompt )
            response = self.cleanOutput( self.handle.before )
            if "Traceback" in response:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + response )
                return main.FALSE
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return main.FALSE
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def buildIP( self, **kwargs ):
        """
        Build an IP frame

        Will create a frame class with the given options. If a field is
        left blank it will default to the below value unless it is
        overwritten by the next frame.
        Default frame:
        ###[ IP ]###
          version= 4
          ihl= None
          tos= 0x0
          len= None
          id= 1
          flags=
          frag= 0
          ttl= 64
          proto= hopopt
          chksum= None
          src= 127.0.0.1
          dst= 127.0.0.1
          \options\

        Returns main.TRUE or main.FALSE on error
        """
        try:
            main.log.debug( self.name + ": Building IP Frame" )
            # Set the IP frame
            cmd = 'ip = IP( '
            options = []
            for key, value in kwargs.iteritems():
                if isinstance( value, str ):
                    value = '"' + value + '"'
                options.append( str( key ) + "=" + str( value ) )
            cmd += ", ".join( options )
            cmd += ' )'
            self.handle.sendline( cmd )
            self.handle.expect( self.scapyPrompt )
            response = self.cleanOutput( self.handle.before )
            if "Traceback" in response:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + response )
                return main.FALSE
            self.handle.sendline( "packet = ether/ip" )
            self.handle.expect( self.scapyPrompt )
            response = self.cleanOutput( self.handle.before )
            if "Traceback" in response:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + response )
                return main.FALSE
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return main.FALSE
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def buildIPv6( self, **kwargs ):
        """
        Build an IPv6 frame

        Will create a frame class with the given options. If a field is
        left blank it will default to the below value unless it is
        overwritten by the next frame.
        Default frame:
        ###[ IPv6 ]###
          version= 6
          tc= 0
          fl= 0
          plen= None
          nh= No Next Header
          hlim= 64
          src= ::1
          dst= ::1

        Returns main.TRUE or main.FALSE on error
        """
        try:
            main.log.debug( self.name + ": Building IPv6 Frame" )
            # Set the IPv6 frame
            cmd = 'ipv6 = IPv6( '
            options = []
            for key, value in kwargs.iteritems():
                if isinstance( value, str ):
                    value = '"' + value + '"'
                options.append( str( key ) + "=" + str( value ) )
            cmd += ", ".join( options )
            cmd += ' )'
            self.handle.sendline( cmd )
            self.handle.expect( self.scapyPrompt )
            response = self.cleanOutput( self.handle.before )
            if "Traceback" in response:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + response )
                return main.FALSE
            self.handle.sendline( "packet = ether/ipv6" )
            self.handle.expect( self.scapyPrompt )
            response = self.cleanOutput( self.handle.before )
            if "Traceback" in response:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + response )
                return main.FALSE
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return main.FALSE
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def buildTCP( self, ipVersion=4, **kwargs ):
        """
        Build an TCP frame

        Will create a frame class with the given options. If a field is
        left blank it will default to the below value unless it is
        overwritten by the next frame.

        NOTE: Some arguments require quotes around them. It's up to you to
        know which ones and to add them yourself. Arguments with an asterisk
        do not need quotes.

        Options:
        ipVersion - Either 4 (default) or 6, indicates what Internet Protocol
                    frame to use to encapsulate into
        Default frame:
        ###[ TCP ]###
          sport= ftp_data *
          dport= http *
          seq= 0
          ack= 0
          dataofs= None
          reserved= 0
          flags= S
          window= 8192
          chksum= None
          urgptr= 0
          options= {}

        Returns main.TRUE or main.FALSE on error
        """
        try:
            main.log.debug( self.name + ": Building TCP" )
            # Set the TCP frame
            cmd = 'tcp = TCP( '
            options = []
            for key, value in kwargs.iteritems():
                options.append( str( key ) + "=" + str( value ) )
            cmd += ", ".join( options )
            cmd += ' )'
            self.handle.sendline( cmd )
            self.handle.expect( self.scapyPrompt )
            response = self.cleanOutput( self.handle.before )
            if "Traceback" in response:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + response )
                return main.FALSE
            if str( ipVersion ) is '4':
                self.handle.sendline( "packet = ether/ip/tcp" )
            elif str( ipVersion ) is '6':
                self.handle.sendline( "packet = ether/ipv6/tcp" )
            else:
                main.log.error( "Unrecognized option for ipVersion, given " +
                                repr( ipVersion ) )
                return main.FALSE
            self.handle.expect( self.scapyPrompt )
            response = self.cleanOutput( self.handle.before )
            if "Traceback" in response:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + response )
                return main.FALSE
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return main.FALSE
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def buildUDP( self, ipVersion=4, **kwargs ):
        """
        Build an UDP frame

        Will create a frame class with the given options. If a field is
        left blank it will default to the below value unless it is
        overwritten by the next frame.

        NOTE: Some arguments require quotes around them. It's up to you to
        know which ones and to add them yourself. Arguments with an asterisk
        do not need quotes.

        Options:
        ipVersion - Either 4 (default) or 6, indicates what Internet Protocol
                    frame to use to encapsulate into
        Default frame:
        ###[ UDP ]###
          sport= domain *
          dport= domain *
          len= None
          chksum= None

        Returns main.TRUE or main.FALSE on error
        """
        try:
            main.log.debug( self.name + ": Building UDP Frame" )
            # Set the UDP frame
            cmd = 'udp = UDP( '
            options = []
            for key, value in kwargs.iteritems():
                options.append( str( key ) + "=" + str( value ) )
            cmd += ", ".join( options )
            cmd += ' )'
            self.handle.sendline( cmd )
            self.handle.expect( self.scapyPrompt )
            response = self.cleanOutput( self.handle.before )
            if "Traceback" in response:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + response )
                return main.FALSE
            if str( ipVersion ) is '4':
                self.handle.sendline( "packet = ether/ip/udp" )
            elif str( ipVersion ) is '6':
                self.handle.sendline( "packet = ether/ipv6/udp" )
            else:
                main.log.error( "Unrecognized option for ipVersion, given " +
                                repr( ipVersion ) )
                return main.FALSE
            self.handle.expect( self.scapyPrompt )
            response = self.cleanOutput( self.handle.before )
            if "Traceback" in response:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + response )
                return main.FALSE
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return main.FALSE
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def buildSCTP( self, ipVersion=4, **kwargs ):
        """
        Build an SCTP frame

        Will create a frame class with the given options. If a field is
        left blank it will default to the below value unless it is
        overwritten by the next frame.

        NOTE: Some arguments require quotes around them. It's up to you to
        know which ones and to add them yourself. Arguments with an asterisk
        do not need quotes.

        Options:
        ipVersion - Either 4 (default) or 6, indicates what Internet Protocol
                    frame to use to encapsulate into
        Default frame:
        ###[ SCTP ]###
          sport= domain *
          dport= domain *
          tag = None
          chksum = None

        Returns main.TRUE or main.FALSE on error
        """
        try:
            main.log.debug( self.name + ": Building SCTP Frame" )
            # Set the SCTP frame
            cmd = 'sctp = SCTP( '
            options = [ ]
            for key, value in kwargs.iteritems( ):
                options.append( str( key ) + "=" + str( value ) )
            cmd += ", ".join( options )
            cmd += ' )'
            self.handle.sendline( cmd )
            self.handle.expect( self.scapyPrompt )
            response = self.cleanOutput( self.handle.before )
            if "Traceback" in response:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + response )
                return main.FALSE
            if str( ipVersion ) is '4':
                self.handle.sendline( "packet = ether/ip/sctp" )
            elif str( ipVersion ) is '6':
                self.handle.sendline( "packet = ether/ipv6/sctp" )
            else:
                main.log.error( "Unrecognized option for ipVersion, given " +
                                repr( ipVersion ) )
                return main.FALSE
            self.handle.expect( self.scapyPrompt )
            response = self.cleanOutput( self.handle.before )
            if "Traceback" in response:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + response )
                return main.FALSE
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return main.FALSE
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def buildARP( self, **kwargs ):
        """
        Build an ARP frame

        Will create a frame class with the given options. If a field is
        left blank it will default to the below value unless it is
        overwritten by the next frame.

        NOTE: Some arguments require quotes around them. It's up to you to
        know which ones and to add them yourself. Arguments with an asterisk
        do not need quotes.

        Default frame:
        ###[ ARP ]###
        hwtype     : XShortField          = (1)
        ptype      : XShortEnumField      = (2048)
        hwlen      : ByteField            = (6)
        plen       : ByteField            = (4)
        op         : ShortEnumField       = (1)
        hwsrc      : ARPSourceMACField    = (None)
        psrc       : SourceIPField        = (None)
        hwdst      : MACField             = ('00:00:00:00:00:00')
        pdst       : IPField              = ('0.0.0.0')

        Returns main.TRUE or main.FALSE on error
        """
        try:
            main.log.debug( self.name + ": Building ARP Frame" )
            # Set the ARP frame
            cmd = 'arp = ARP( '
            options = []
            for key, value in kwargs.iteritems( ):
                if isinstance( value, str ):
                    value = '"' + value + '"'
                options.append( str( key ) + "=" + str( value ) )
            cmd += ", ".join( options )
            cmd += ' )'
            self.handle.sendline( cmd )
            self.handle.expect( self.scapyPrompt )
            response = self.cleanOutput( self.handle.before )
            if "Traceback" in response:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + response )
                return main.FALSE
            self.handle.sendline( "packet = ether/arp" )
            self.handle.expect( self.scapyPrompt )
            response = self.cleanOutput( self.handle.before )
            if "Traceback" in response:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + response )
                return main.FALSE
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return main.FALSE
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def buildICMP( self, ipVersion=4, **kwargs ):
        """
        Build an ICMP frame

        Will create a frame class with the given options. If a field is
        left blank it will default to the below value unless it is
        overwritten by the next frame.
        Default frame:
        ###[ ICMP ]###
          type= echo-request
          code= 0
          chksum= None
          id= 0x0
          seq= 0x0

        Options:
        ipVersion - Either 4 (default) or 6, indicates what Internet Protocol
                    frame to use to encapsulate into

        Returns main.TRUE or main.FALSE on error
        """
        try:
            main.log.debug( self.name + ": Building ICMP Frame" )
            # Set the ICMP frame
            if str( ipVersion ) is '4':
                cmd = 'icmp = ICMP( '
            elif str( ipVersion ) is '6':
                cmd = 'icmp6 = ICMPv6EchoReply( '
            else:
                main.log.error( "Unrecognized option for ipVersion, given " +
                                repr( ipVersion ) )
                return main.FALSE
            options = []
            for key, value in kwargs.iteritems( ):
                if isinstance( value, str ):
                    value = '"' + value + '"'
                options.append( str( key ) + "=" + str( value ) )
            cmd += ", ".join( options )
            cmd += ' )'
            self.handle.sendline( cmd )
            self.handle.expect( self.scapyPrompt )
            response = self.cleanOutput( self.handle.before )
            if "Traceback" in response:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + response )
                return main.FALSE

            if str( ipVersion ) is '4':
                self.handle.sendline( "packet = ether/ip/icmp" )
            elif str( ipVersion ) is '6':
                self.handle.sendline( "packet = ether/ipv6/icmp6" )
            else:
                main.log.error( "Unrecognized option for ipVersion, given " +
                                repr( ipVersion ) )
                return main.FALSE
            self.handle.expect( self.scapyPrompt )
            response = self.cleanOutput( self.handle.before )
            if "Traceback" in response:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + response )
                return main.FALSE
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return main.FALSE
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def clearBuffer( self, debug=False ):
        """
        Keep reading from buffer until its empty
        Everything seems to be printed twice in newer versions of
        scapy, even when turning off fancy output
        """
        i = 0
        response = ''
        while True:
            try:
                i += 1
                # clear buffer
                if debug:
                    main.log.warn( "%s expect loop iteration" % i )
                self.handle.expect( self.scapyPrompt, timeout=5 )
                response += self.cleanOutput( self.handle.before, debug )
            except pexpect.TIMEOUT:
                return response

    def sendPacket( self, iface=None, packet=None, timeout=1, debug=True ):
        """
        Send a packet with either the given scapy packet command, or use the
        packet saved in the variable 'packet'.

        Examples of a valid string for packet:

        Simple IP packet
        packet='Ether(dst="a6:d9:26:df:1d:4b")/IP(dst="10.0.0.2")'

        A Ping with two vlan tags
        packet='Ether(dst='ff:ff:ff:ff:ff:ff')/Dot1Q(vlan=1)/Dot1Q(vlan=10)/
                IP(dst='255.255.255.255', src='192.168.0.1')/ICMP()'

        Returns main.TRUE or main.FALSE on error
        """
        try:
            main.log.debug( self.name + ": Sending Packet" )
            if debug:
                self.handle.sendline( "packet.summary()" )
                self.handle.expect( self.scapyPrompt )
            self.clearBuffer()
            # TODO: add all params, or use kwargs
            sendCmd = 'sendp( '
            if packet:
                sendCmd += packet
            else:
                sendCmd += "packet"
            if iface:
                sendCmd += ", iface='{}'".format( iface )

            if debug:
                sendCmd += ', return_packets=True).summary()'  # show packet(s) sent
            self.handle.sendline( sendCmd )
            self.handle.expect( self.scapyPrompt )
            response = self.cleanOutput( self.handle.before )
            main.log.debug( self.name + ": Send packet response: {}".format( response ) )
            if "Traceback" in response or "Errno" in response or "Error" in response:
                # KeyError, SyntaxError, ...
                main.log.error( self.name + ": Error in sending command: " + response )
                return main.FALSE
            # TODO: Check # of packets sent?
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return main.FALSE
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def startFilter( self, ifaceName=None, sniffCount=1, pktFilter="ip" ):
        """
        Listen for packets using the given filters

        Options:
        ifaceName - the name of the interface to listen on. If none is given,
                    defaults to self.ifaceName which is <host name>-eth0
        pktFilter - A string in Berkeley Packet Filter (BPF) format which
                    specifies which packets to sniff
        sniffCount - The number of matching packets to capture before returning

        Returns main.TRUE or main.FALSE on error
        """
        try:
            main.log.info( self.name + ": Starting filter on interface %s" % ifaceName )
            # TODO: add all params, or use kwargs
            ifaceName = str( ifaceName ) if ifaceName else self.ifaceName
            # Set interface
            self.handle.sendline( 'conf.iface = "' + ifaceName + '"' )
            self.handle.expect( ifaceName )
            self.cleanOutput( self.handle.before + self.handle.after )
            self.cleanOutput( self.handle.before )
            self.handle.expect( self.scapyPrompt )
            response = self.handle.before + self.handle.after
            self.cleanOutput( response )
            cmd = 'pkts = sniff(count = %s, filter = "%s", prn=lambda p: p.summary() )' % ( sniffCount, pktFilter )
            main.log.info( self.name + ": Starting filter on " + self.name + ' > ' + cmd )
            self.handle.sendline( cmd )
            response = self.clearBuffer()

            # Make sure the sniff function didn't exit due to failures
            i = self.handle.expect( [ self.scapyPrompt, pexpect.TIMEOUT ], timeout=3 )
            response = self.cleanOutput( self.handle.before + str( self.handle.after ) )
            if i == 0:
                # sniff exited
                main.log.error( self.name + ": sniff function exited" )
                main.log.error( self.name + ":     " + response )
                return main.FALSE
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return main.FALSE
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def checkFilter( self, timeout=10 ):
        """
        Check if a filter is still running.
        Returns:
            main.TRUE if the filter stopped
            main.FALSE if the filter is still running
        """
        try:
            main.log.debug( self.name + ": Checking Filter" )
            self.handle.sendline( "" )
            i = self.handle.expect( [ self.scapyPrompt, pexpect.TIMEOUT ], timeout=timeout )
            response = self.cleanOutput( self.handle.before + str( self.handle.after ), debug=True )
            if i == 0:
                return main.TRUE
            else:
                return main.FALSE
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def killFilter( self ):
        """
        Kill a scapy filter
        """
        try:
            main.log.debug( self.name + ": Killing scapy filter" )
            self.handle.send( "\x03" )  # Send a ctrl-c to kill the filter
            self.handle.expect( self.scapyPrompt )
            output = self.cleanOutput( self.handle.before, debug=True )
            return output
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return None
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def readPackets( self, detailed=False ):
        """
        Read all the packets captured by the previous filter
        """
        try:
            main.log.debug( self.name + ": Reading Packets" )
            main.log.debug( self.name + ": Begin clear buffer" )
            self.clearBuffer()
            main.log.debug( self.name + ": end clear buffer" )

            if detailed:
                self.handle.sendline( "[p for p in pkts]")
            else:
                self.handle.sendline( "pkts.summary()")
            output = self.clearBuffer()
            if "Traceback" in output or "Errno" in output or "Error" in output:
                # KeyError, SyntaxError, IOError, NameError, ...
                main.log.error( self.name + ": Error in sending command: " + output )
                main.cleanAndExit()
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return None
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()
        return output

    def updateSelf( self, IPv6=False ):
        """
        Updates local MAC and IP fields
        """
        self.hostMac = self.getMac()
        if IPv6:
            self.hostIp = self.getIp( IPv6=True )
        else:
            self.hostIp = self.getIp()

    def getMac( self, ifaceName=None ):
        """
        Save host's MAC address
        """
        try:
            ifaceName = str( ifaceName ) if ifaceName else self.ifaceName
            cmd = 'get_if_hwaddr("' + str( ifaceName ) + '")'
            self.handle.sendline( cmd )
            self.handle.expect( self.scapyPrompt )
            response = self.cleanOutput( self.handle.before )
            pattern = r'(([0-9a-f]{2}[:-]){5}([0-9a-f]{2}))'
            match = re.search( pattern, response )
            if match:
                return match.group()
            else:
                # the command will have an exception if iface doesn't exist
                return None
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return None
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getIp( self, ifaceName=None, IPv6=False ):
        """
        Save host's IP address

        Returns the IP of the first interface that is not a loopback device.
        If no IP could be found then it will return 0.0.0.0.

        If IPv6 is equal to True, returns IPv6 of the first interface that is not a loopback device.
        If no IPv6 could be found then it will return :: .

        """
        def getIPofInterface( ifaceName ):
            cmd = 'get_if_addr("' + str( ifaceName ) + '")'
            if IPv6:
                cmd = 'get_if_raw_addr6("' + str( ifaceName ) + '")'
            self.handle.sendline( cmd )
            self.handle.expect( self.scapyPrompt )
            response = self.cleanOutput( self.handle.before )

            pattern = r'(((2[0-5]|1[0-9]|[0-9])?[0-9]\.){3}((2[0-5]|1[0-9]|[0-9])?[0-9]))'
            if IPv6:
                pattern = r'(\\x([0-9]|[a-f]|[A-F])([0-9]|[a-f]|[A-F])){16}'
            match = re.search( pattern, response )
            if match:
                # NOTE: The command will return 0.0.0.0 if the iface doesn't exist
                if IPv6 is not True:
                    if match.group() == '0.0.0.0':
                        main.log.warn( 'iface {0} has no IPv4 address'.format( ifaceName ) )
                return match.group()
            else:
                return None
        try:
            if not ifaceName:
                # Get list of interfaces
                ifList = self.getIfList()
                if IPv6:
                    for ifaceName in ifList:
                        if ifaceName == "lo":
                            continue
                        ip = getIPofInterface( ifaceName )
                        if ip is not None:
                            newip = ip
                            tmp = newip.split( "\\x" )
                            ip = ""
                            counter = 0
                            for i in tmp:
                                if i != "":
                                    counter = counter + 1
                                    if counter % 2 == 0 and counter < 16:
                                        ip = ip + i + ":"
                                    else:
                                        ip = ip + i
                            return ip
                    return "::"
                else:
                    for ifaceName in ifList:
                        if ifaceName == "lo":
                            continue
                        ip = getIPofInterface( ifaceName )
                        if ip != "0.0.0.0":
                            return ip
                    return "0.0.0.0"
            else:
                return getIPofInterface( ifaceName )

        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return None
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def addRoute( self, network, gateway, interface=None ):
        """
        Add a route to the current scapy session
        """
        main.log.info( self.name + ": Adding route to scapy session; %s via %s out of interface %s" % ( network, gateway, interface ) )
        if gateway is None:
            main.log.error( self.name + ": Gateway is None, cannot set route" )
            return main.FALSE
        if network is None or "None" in network:
            main.log.error( self.name + ": Network is None, cannot set route" )
            return main.FALSE
        try:
            cmdStr = 'conf.route.add( net="%s", gw="%s"' % ( network, gateway )
            if interface:
                cmdStr += ', dev="%s"' % interface
            cmdStr += ')'
            self.handle.sendline( cmdStr )
            self.handle.expect( self.scapyPrompt )
            response = self.cleanOutput( self.handle.before )
            if "Traceback" in response:
                main.log.error( self.name + ": Error in adding route to scappy session" )
                main.log.debug( response )
                return main.FALSE
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return None
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def addRoutes( self ):
        """
        Add any routes configured for the host
        """
        returnValues = []
        for route in self.routes:
            gw = route.get( 'gw' )
            iface = route.get( 'interface' )
            returnValues .append( self.addRoute( "%s/%s" % ( route.get( 'network' ), route.get( 'netmask' ) ),
                                                 gw if gw else main.Cluster.active(0).address,
                                                 interface=iface if iface else self.interfaces[ 0 ].get( 'name' ) ) )
        return returnValues

    def getIfList( self ):
        """
        Return List of Interfaces
        """
        try:
            self.handle.sendline( 'get_if_list()' )
            self.handle.expect( self.scapyPrompt )
            response = self.cleanOutput( self.handle.before )
            ifList = response.split( '\r\n' )
            ifList = ifList[ 1 ].replace( "'", "" )[ 1:-1 ].split( ', ' )
            return ifList

        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return None
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

if __name__ != "__main__":
    sys.modules[ __name__ ] = ScapyCliDriver()
