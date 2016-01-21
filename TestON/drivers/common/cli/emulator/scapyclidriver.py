#!/usr/bin/env python
"""
2015-2016

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
import types
import os
from drivers.common.cli.emulatordriver import Emulator


class ScapyCliDriver( Emulator ):

    """
       ScapyCliDriver is the basic driver which will handle
       the Scapy functions"""
    def __init__( self ):
        super( Emulator, self ).__init__()
        self.handle = self
        self.name = None
        self.home = None
        self.wrapped = sys.modules[ __name__ ]
        self.flag = 0
        # TODO: Refactor driver to use these everywhere
        self.hostPrompt = "~#"
        self.bashPrompt = "\$"
        self.scapyPrompt = ">>>"

    def connect( self, **connectargs ):
        """
           Here the main is the TestON instance after creating
           all the log handles."""
        try:
            for key in connectargs:
                vars( self )[ key ] = connectargs[ key ]
            self.home = "~/mininet"
            self.name = self.options[ 'name' ]
            for key in self.options:
                if key == "home":
                    self.home = self.options[ 'home' ]
                    break
            if self.home is None or self.home == "":
                self.home = "~/mininet"

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
                ScapyCliDriver,
                self ).connect(
                user_name=self.user_name,
                ip_address=self.ip_address,
                port=None,
                pwd=self.pwd )

            if self.handle:
                main.log.info( "Connection successful to the host " +
                               self.user_name +
                               "@" +
                               self.ip_address )
                return main.TRUE
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def disconnect( self ):
        """
        Called at the end of the test to stop the scapy component and
        disconnect the handle.
        """
        self.handle.sendline( '' )
        i = self.handle.expect( [ 'mininet>', pexpect.EOF, pexpect.TIMEOUT ],
                                timeout=2 )
        response = main.TRUE
        if i == 0:
            response = self.stopNet()
        elif i == 1:
            return main.TRUE
        # print "Disconnecting Mininet"
        if self.handle:
            self.handle.sendline( "exit" )
            self.handle.expect( "exit" )
            self.handle.expect( "(.*)" )
        else:
            main.log.error( "Connection failed to the host" )
        return response

    def stopNet( self, fileName="", timeout=5 ):
        """
        Stops mininet.
        Returns main.TRUE if the mininet successfully stops and
                main.FALSE if the pexpect handle does not exist.

        Will cleanup and exit the test if scapy fails to stop
        """
        main.log.info( self.name + ": Stopping scapy..." )
        response = ''
        if self.handle:
            try:
                self.handle.sendline( "" )
                i = self.handle.expect( [ '>>>',
                                          '\$',
                                          pexpect.EOF,
                                          pexpect.TIMEOUT ],
                                        timeout )
                if i == 0:
                    main.log.info( "Exiting scapy..." )
                response = self.execute(
                    cmd="exit",
                    prompt="(.*)",
                    timeout=120 )
                main.log.info( self.name + ": Stopped" )
                response = main.TRUE

                if i == 1:
                    main.log.info( " Mininet trying to exit while not " +
                                   "in the mininet prompt" )
                elif i == 2:
                    main.log.error( "Something went wrong exiting mininet" )
                elif i == 3:  # timeout
                    main.log.error( "Something went wrong exiting mininet " +
                                    "TIMEOUT" )

                if fileName:
                    self.handle.sendline( "" )
                    self.handle.expect( '\$' )
                    self.handle.sendline(
                        "sudo kill -9 \`ps -ef | grep \"" +
                        fileName +
                        "\" | grep -v grep | awk '{print $2}'\`" )
            except pexpect.EOF:
                main.log.error( self.name + ": EOF exception found" )
                main.log.error( self.name + ":     " + self.handle.before )
                main.cleanup()
                main.exit()
        else:
            main.log.error( self.name + ": Connection failed to the host" )
            response = main.FALSE
        return response

    def createHostComponent( self, name ):
        """
        Creates a new mininet cli component with the same parameters as self.
        This new component is intended to be used to login to the hosts created
        by mininet.

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
            main.componentDictionary[name] = main.componentDictionary[self.name].copy()
            main.componentDictionary[name]['connect_order'] = str( int( main.componentDictionary[name]['connect_order'] ) + 1 )
            main.componentInit( name )
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()
        else:
            # namespace is not clear!
            main.log.error( name + " component already exists!" )
            main.cleanup()
            main.exit()

    def removeHostComponent( self, name ):
        """
        Remove host component
        Arguments:
            name - The string of the name of the component to delete.
        """
        try:
            # Get host component
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
            del( main.componentDictionary[name] )
            return main.TRUE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def startHostCli( self, host=None ):
        """
        Use the mininet m utility to connect to the host's cli
        """
        # These are fields that can be used by scapy packets. Initialized to None
        self.hostIp = None
        self.hostMac = None
        try:
            if not host:
                host = self.name
            self.handle.sendline( self.home + "/util/m " + host )
            self.handle.expect( self.hostPrompt )
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return main.FALSE
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def startScapy( self, mplsPath="" ):
        """
        Start the Scapy cli
        optional:
            mplsPath - The path where the MPLS class is located
            NOTE: This can be a relative path from the user's home dir
        """
        mplsLines = ['import imp',
            'imp.load_source( "mplsClass", "{}mplsClass.py" )'.format(mplsPath),
            'from mplsClass import MPLS',
            'bind_layers(Ether, MPLS, type = 0x8847)',
            'bind_layers(MPLS, MPLS, bottom_of_label_stack = 0)',
            'bind_layers(MPLS, IP)']

        try:
            self.handle.sendline( "scapy" )
            self.handle.expect( self.scapyPrompt )
            self.handle.sendline( "conf.color_theme = NoTheme()" )
            self.handle.expect( self.scapyPrompt )
            if mplsPath:
                main.log.info( "Adding MPLS class" )
                main.log.info( "MPLS class path: " + mplsPath )
                for line in mplsLines:
                    main.log.info( "sending line: " + line )
                    self.handle.sendline( line )
                    self.handle.expect( self.scapyPrompt )
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return main.FALSE
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def stopScapy( self ):
        """
        Exit the Scapy cli
        """
        try:
            self.handle.sendline( "exit()" )
            self.handle.expect( self.hostPrompt )
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return main.FALSE
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            if "Traceback" in self.handle.before:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + self.handle.before )
                return main.FALSE
            self.handle.sendline( "packet = ether" )
            self.handle.expect( self.scapyPrompt )
            if "Traceback" in self.handle.before:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + self.handle.before )
                return main.FALSE
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return main.FALSE
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            if "Traceback" in self.handle.before:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + self.handle.before )
                return main.FALSE
            self.handle.sendline( "packet = ether/ip" )
            self.handle.expect( self.scapyPrompt )
            if "Traceback" in self.handle.before:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + self.handle.before )
                return main.FALSE
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return main.FALSE
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            if "Traceback" in self.handle.before:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + self.handle.before )
                return main.FALSE
            self.handle.sendline( "packet = ether/ipv6" )
            self.handle.expect( self.scapyPrompt )
            if "Traceback" in self.handle.before:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + self.handle.before )
                return main.FALSE
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return main.FALSE
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            # Set the TCP frame
            cmd = 'tcp = TCP( '
            options = []
            for key, value in kwargs.iteritems():
                options.append( str( key ) + "=" + str( value ) )
            cmd += ", ".join( options )
            cmd += ' )'
            self.handle.sendline( cmd )
            self.handle.expect( self.scapyPrompt )
            if "Traceback" in self.handle.before:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + self.handle.before )
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
            if "Traceback" in self.handle.before:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + self.handle.before )
                return main.FALSE
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return main.FALSE
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            # Set the UDP frame
            cmd = 'udp = UDP( '
            options = []
            for key, value in kwargs.iteritems():
                options.append( str( key ) + "=" + str( value ) )
            cmd += ", ".join( options )
            cmd += ' )'
            self.handle.sendline( cmd )
            self.handle.expect( self.scapyPrompt )
            if "Traceback" in self.handle.before:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + self.handle.before )
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
            if "Traceback" in self.handle.before:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + self.handle.before )
                return main.FALSE
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return main.FALSE
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def buildICMP( self, **kwargs ):
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

        Returns main.TRUE or main.FALSE on error
        """
        try:
            # Set the ICMP frame
            cmd = 'icmp = ICMP( '
            options = []
            for key, value in kwargs.iteritems():
                if isinstance( value, str ):
                    value = '"' + value + '"'
                options.append( str( key ) + "=" + str( value ) )
            cmd += ", ".join( options )
            cmd += ' )'
            self.handle.sendline( cmd )
            self.handle.expect( self.scapyPrompt )
            if "Traceback" in self.handle.before:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + self.handle.before )
                return main.FALSE
            self.handle.sendline( "packet = ether/ip/icmp" )
            self.handle.expect( self.scapyPrompt )
            if "Traceback" in self.handle.before:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + self.handle.before )
                return main.FALSE
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return main.FALSE
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def sendPacket( self, iface=None, packet=None, timeout=1 ):
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
            # TODO: add all params, or use kwargs
            sendCmd = 'srp( '
            if packet:
                sendCmd += packet
            else:
                sendCmd += "packet"
            if iface:
                sendCmd += ", iface='{}'".format( iface )

            sendCmd += ', timeout=' + str( timeout ) + ')'
            self.handle.sendline( sendCmd )
            self.handle.expect( self.scapyPrompt )
            if "Traceback" in self.handle.before:
                # KeyError, SyntaxError, ...
                main.log.error( "Error in sending command: " + self.handle.before )
                return main.FALSE
            # TODO: Check # of packets sent?
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return main.FALSE
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def startFilter( self, ifaceName=None, sniffCount=1, pktFilter="ip" ):
        """
        Listen for packets using the given filters

        Options:
        ifaceName - the name of the interface to listen on. If none is given,
                    defaults to <host name>-eth0
        pktFilter - A string in Berkeley Packet Filter (BPF) format which
                    specifies which packets to sniff
        sniffCount - The number of matching packets to capture before returning

        Returns main.TRUE or main.FALSE on error
        """
        try:
            # TODO: add all params, or use kwargs
            ifaceName = str( ifaceName ) if ifaceName else self.name + "-eth0"
            # Set interface
            self.handle.sendline( ' conf.iface = "' + ifaceName + '"' )
            self.handle.expect( self.scapyPrompt )
            cmd = 'pkt = sniff(count = ' + str( sniffCount ) +\
                  ', filter = "' + str( pktFilter ) + '")'
            print self.name + ' > ' + cmd
            self.handle.sendline( cmd )
            self.handle.expect( '"\)\r\n' )
            # TODO: parse this?
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return main.FALSE
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def checkFilter( self, timeout=10 ):
        """
        Check that a filter returned and returns the reponse
        """
        try:
            i = self.handle.expect( [ self.scapyPrompt, pexpect.TIMEOUT ], timeout=timeout )
            if i == 0:
                return main.TRUE
            else:
                return main.FALSE
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def killFilter( self ):
        """
        Kill a scapy filter
        """
        try:
            self.handle.send( "\x03" )  # Send a ctrl-c to kill the filter
            self.handle.expect( self.scapyPrompt )
            return self.handle.before
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return None
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def readPackets( self ):
        """
        Read all the packets captured by the previous filter
        """
        try:
            self.handle.sendline( "for p in pkt: p \n")
            self.handle.expect( "for p in pkt: p \r\n... \r\n" )
            self.handle.expect( self.scapyPrompt )
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return None
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()
        return self.handle.before

    def updateSelf( self ):
        """
        Updates local MAC and IP fields
        """
        self.hostMac = self.getMac()
        self.hostIp = self.getIp()

    def getMac( self, ifaceName=None ):
        """
        Save host's MAC address
        """
        try:
            ifaceName = str( ifaceName ) if ifaceName else self.name + "-eth0"
            cmd = 'get_if_hwaddr("' + str( ifaceName ) + '")'
            self.handle.sendline( cmd )
            self.handle.expect( self.scapyPrompt )
            pattern = r'(([0-9a-f]{2}[:-]){5}([0-9a-f]{2}))'
            match = re.search( pattern, self.handle.before )
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def getIp( self, ifaceName=None ):
        """
        Save host's IP address

        Returns the IP of the first interface that is not a loopback device.
        If no IP could be found then it will return 0.0.0.0.
        """
        def getIPofInterface( ifaceName ):
            cmd = 'get_if_addr("' + str( ifaceName ) + '")'
            self.handle.sendline( cmd )
            self.handle.expect( self.scapyPrompt )

            pattern = r'(((2[0-5]|1[0-9]|[0-9])?[0-9]\.){3}((2[0-5]|1[0-9]|[0-9])?[0-9]))'
            match = re.search( pattern, self.handle.before )
            if match:
                # NOTE: The command will return 0.0.0.0 if the iface doesn't exist
                if match.group() == '0.0.0.0':
                    main.log.warn( 'iface {0} has no IPv4 address'.format( ifaceName ) )
                return match.group()
            else:
                return None
        try:
            if not ifaceName:
                # Get list of interfaces
                ifList = self.getIfList()
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def getIfList( self ):
        """
        Return List of Interfaces
        """
        try:
            self.handle.sendline( 'get_if_list()' )
            self.handle.expect( self.scapyPrompt )
            ifList = self.handle.before.split( '\r\n' )
            ifList = ifList[ 1 ].replace( "'","" )[ 1:-1 ].split( ', ' )
            return ifList

        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Command timed out" )
            return None
        except pexpect.EOF:
            main.log.exception( self.name + ": connection closed." )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

if __name__ != "__main__":
    sys.modules[ __name__ ] = ScapyCliDriver()
