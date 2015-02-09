#!/usr/bin/env python
"""
Created on 26-Oct-2012

author: Anil Kumar ( anilkumar.s@paxterrasolutions.com )


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


MininetCliDriver is the basic driver which will handle the Mininet functions

Some functions rely on STS module. To install this,
    git clone https://github.com/jhall11/sts.git

Some functions rely on a modified version of Mininet. These functions
should all be noted in the comments. To get this MN version run these commands
from within your Mininet folder:
    git remote add jhall11 https://github.com/jhall11/mininet.git
    git fetch jhall11
    git checkout -b dynamic_topo remotes/jhall11/dynamic_topo
    git pull


    Note that you may need to run 'sudo make develop' if your mnexec.c file
changed when switching branches."""
import traceback
import pexpect
import re
import sys
sys.path.append( "../" )
from math import pow
from drivers.common.cli.emulatordriver import Emulator


class MininetCliDriver( Emulator ):

    """
       MininetCliDriver is the basic driver which will handle
       the Mininet functions"""
    def __init__( self ):
        super( Emulator, self ).__init__()
        self.handle = self
        self.wrapped = sys.modules[ __name__ ]
        self.flag = 0

    def connect( self, **connectargs ):
        """
           Here the main is the TestON instance after creating
           all the log handles."""
        try:
            for key in connectargs:
                vars( self )[ key ] = connectargs[ key ]

            self.name = self.options[ 'name' ]
            self.handle = super(
                MininetCliDriver,
                self ).connect(
                user_name=self.user_name,
                ip_address=self.ip_address,
                port=None,
                pwd=self.pwd )

            if self.handle:
                main.log.info("Connection successful to the host " +
                        self.user_name +
                        "@" +
                        self.ip_address )
                return main.TRUE
            else:
                main.log.error( "Connection failed to the host " +
                        self.user_name +
                        "@" +
                        self.ip_address )
                msin.log.error( "Failed to connect to the Mininet CLI" )
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.info( self.name + ":::::::::::::::::::::::" )
            main.log.error( traceback.print_exc() )
            main.log.info( ":::::::::::::::::::::::" )
            main.cleanup()
            main.exit()


    def startNet( self, topoFile = '', args = '', timeout = 120 ):
        """
        Starts Mininet accepts a topology(.py) file and/or an optional
        arguement ,to start the mininet, as a parameter.
        Returns true if the mininet starts successfully
        """
        if self.handle:
            main.log.info(
                self.name +
                ": Clearing any residual state or processes" )
            self.handle.sendline( "sudo mn -c" )
            i = self.handle.expect( [ 'password\sfor\s',
                                      'Cleanup\scomplete',
                                      pexpect.EOF,
                                      pexpect.TIMEOUT ],
                                    timeout )
            if i == 0:
                main.log.info( self.name + ": Sending sudo password" )
                self.handle.sendline( self.pwd )
                i = self.handle.expect( [ '%s:' % ( self.user ),
                                          '\$',
                                          pexpect.EOF,
                                          pexpect.TIMEOUT ],
                                        timeout )
            if i == 1:
                main.log.info( self.name + ": Clean" )
            elif i == 2:
                main.log.error( self.name + ": Connection terminated" )
            elif i == 3:  # timeout
                main.log.error(
                    self.name +
                    ": Something while cleaning MN took too long... " )
            if topoFile == ''  and  args ==  '':
                main.log.info( self.name + ": building fresh mininet" )
                # for reactive/PARP enabled tests
                cmdString = "sudo mn " + self.options[ 'arg1' ] +\
                    " " + self.options[ 'arg2' ] +\
                    " --mac --controller " +\
                    self.options[ 'controller' ] + " " +\
                    self.options[ 'arg3' ]

                argList = self.options[ 'arg1' ].split( "," )
                global topoArgList
                topoArgList = argList[ 0 ].split( " " )
                argList = map( int, argList[ 1: ] )
                topoArgList = topoArgList[ 1: ] + argList

                self.handle.sendline( cmdString )
                self.handle.expect( [ "sudo mn",
                                    pexpect.EOF,
                                    pexpect.TIMEOUT ] )
                while True:
                    i = self.handle.expect( [ 'mininet>',
                                              '\*\*\*',
                                              'Exception',
                                              pexpect.EOF,
                                              pexpect.TIMEOUT ],
                                            timeout )
                    if i == 0:
                        main.log.info( self.name + ": mininet built" )
                        return main.TRUE
                    if i == 1:
                        self.handle.expect(
                            [ "\n", pexpect.EOF, pexpect.TIMEOUT ] )
                        main.log.info( self.handle.before )
                    elif i == 2:
                        main.log.error(
                            self.name +
                            ": Launching mininet failed..." )
                        return main.FALSE
                    elif i == 3:
                        main.log.error( self.name + ": Connection timeout" )
                        return main.FALSE
                    elif i == 4:  # timeout
                        main.log.error(
                            self.name +
                            ": Something took too long... " )
                        return main.FALSE
                return main.TRUE
            else:
                main.log.info( "Starting topo file " + topoFile )
                if args == None:
                    args = ''
                else:
                    main.log.info( "args = " + args)
                self.handle.sendline( 'sudo ' + topoFile + ' ' + args)
                i = 1
                i = self.handle.expect( [ 'mininet>',
                                        pexpect.EOF ,
                                        pexpect.TIMEOUT ],
                                        timeout)
                if i == 0:
                    main.log.info(self.name + ": Network started")
                    return main.TRUE
                if i == 1:
                    self.handle.expect(
                        [ "\n", pexpect.EOF, pexpect.TIMEOUT ] )
                    main.log.info( self.handle.before )
                elif i == 2:
                    main.log.error(
                        self.name +
                        ": Launching mininet failed..." )
                    return main.FALSE
                elif i == 3:
                    main.log.error( self.name + ": Connection timeout" )
                    return main.FALSE
                elif i == 4:  # timeout
                    main.log.error(
                        self.name +
                        ": Something took too long... " )
                    return main.FALSE
                return main.TRUE
        else:  # if no handle
            main.log.error(
                self.name +
                ": Connection failed to the host " +
                self.user_name +
                "@" +
                self.ip_address )
            main.log.error( self.name + ": Failed to connect to the Mininet" )
            return main.FALSE

    def numSwitchesNlinks( self, topoType, depth, fanout ):
        if topoType == 'tree':
            # In tree topology, if fanout arg is not given, by default it is 2
            if fanout is None:
                fanout = 2
            k = 0
            count = 0
            while( k <= depth - 1 ):
                count = count + pow( fanout, k )
                k = k + 1
                numSwitches = count
            while( k <= depth - 2 ):
                # depth-2 gives you only core links and not considering
                # edge links as seen by ONOS. If all the links including
                # edge links are required, do depth-1
                count = count + pow( fanout, k )
                k = k + 1
            numLinks = count * fanout
            # print "num_switches for %s(%d,%d) = %d and links=%d" %(
            # topoType,depth,fanout,numSwitches,numLinks )

        elif topoType == 'linear':
            # In linear topology, if fanout or numHostsPerSw is not given,
            # by default it is 1
            if fanout is None:
                fanout = 1
            numSwitches = depth
            numHostsPerSw = fanout
            totalNumHosts = numSwitches * numHostsPerSw
            numLinks = totalNumHosts + ( numSwitches - 1 )
            print "num_switches for %s(%d,%d) = %d and links=%d" %\
                ( topoType, depth, fanout, numSwitches, numLinks )
        topoDict = {}
        topoDict = {
            "num_switches": int( numSwitches ),
            "num_corelinks": int( numLinks ) }
        return topoDict

    def calculateSwAndLinks( self ):
        topoDict = self.numSwitchesN_links( *topoArgList )
        return topoDict

    def pingall( self, timeout=300 ):
        """
           Verifies the reachability of the hosts using pingall command.
           Optional parameter timeout allows you to specify how long to
           wait for pingall to complete
           Returns:
           main.TRUE if pingall completes with no pings dropped
           otherwise main.FALSE"""
        if self.handle:
            main.log.info(
                self.name +
                ": Checking reachabilty to the hosts using pingall" )
            try:
                response = self.execute(
                    cmd="pingall",
                    prompt="mininet>",
                    timeout=int( timeout ) )
            except pexpect.EOF:
                main.log.error( self.name + ": EOF exception found" )
                main.log.error( self.name + ":     " + self.handle.before )
                main.cleanup()
                main.exit()
            except pexpect.TIMEOUT:
                # We may not want to kill the test if pexpect times out
                main.log.error( self.name + ": TIMEOUT exception found" )
                main.log.error( self.name +
                                ":     " +
                                str( self.handle.before ) )
            # NOTE: mininet's pingall rounds, so we will check the number of
            # passed and number of failed
            pattern = "Results\:\s0\%\sdropped\s\(" +\
                      "(?P<passed>[\d]+)/(?P=passed)"
            if re.search( pattern, response ):
                main.log.info( self.name + ": All hosts are reachable" )
                return main.TRUE
            else:
                main.log.error( self.name + ": Unable to reach all the hosts" )
                main.log.info( "Pingall output: " + str( response ) )
                # NOTE: Send ctrl-c to make sure pingall is done
                self.handle.send( "\x03" )
                self.handle.expect( "Interrupt" )
                self.handle.expect( "mininet>" )
                return main.FALSE
        else:
            main.log.error( self.name + ": Connection failed to the host" )
            main.cleanup()
            main.exit()

    def fpingHost( self, **pingParams ):
        """
           Uses the fping package for faster pinging...
           *requires fping to be installed on machine running mininet"""
        args = utilities.parse_args( [ "SRC", "TARGET" ], **pingParams )
        command = args[ "SRC" ] + \
            " fping -i 100 -t 20 -C 1 -q " + args[ "TARGET" ]
        self.handle.sendline( command )
        self.handle.expect(
            [ args[ "TARGET" ], pexpect.EOF, pexpect.TIMEOUT ] )
        self.handle.expect( [ "mininet", pexpect.EOF, pexpect.TIMEOUT ] )
        response = self.handle.before
        if re.search( ":\s-", response ):
            main.log.info( self.name + ": Ping fail" )
            return main.FALSE
        elif re.search( ":\s\d{1,2}\.\d\d", response ):
            main.log.info( self.name + ": Ping good!" )
            return main.TRUE
        main.log.info( self.name + ": Install fping on mininet machine... " )
        main.log.info( self.name + ": \n---\n" + response )
        return main.FALSE

    def pingHost( self, **pingParams ):
        """
           Ping from one mininet host to another
           Currently the only supported Params: SRC and TARGET"""
        args = utilities.parse_args( [ "SRC", "TARGET" ], **pingParams )
        command = args[ "SRC" ] + " ping " + \
            args[ "TARGET" ] + " -c 1 -i 1 -W 8"
        try:
            main.log.warn( "Sending: " + command )
            self.handle.sendline( command )
            i = self.handle.expect( [ command, pexpect.TIMEOUT ] )
            if i == 1:
                main.log.error(
                    self.name +
                    ": timeout when waiting for response from mininet" )
                main.log.error( "response: " + str( self.handle.before ) )
            i = self.handle.expect( [ "mininet>", pexpect.TIMEOUT ] )
            if i == 1:
                main.log.error(
                    self.name +
                    ": timeout when waiting for response from mininet" )
                main.log.error( "response: " + str( self.handle.before ) )
            response = self.handle.before
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        main.log.info( self.name + ": Ping Response: " + response )
        if re.search( ',\s0\%\spacket\sloss', response ):
            main.log.info( self.name + ": no packets lost, host is reachable" )
            main.lastResult = main.TRUE
            return main.TRUE
        else:
            main.log.error(
                self.name +
                ": PACKET LOST, HOST IS NOT REACHABLE" )
            main.lastResult = main.FALSE
            return main.FALSE

    def checkIP( self, host ):
        """
           Verifies the host's ip configured or not."""
        if self.handle:
            try:
                response = self.execute(
                    cmd=host +
                    " ifconfig",
                    prompt="mininet>",
                    timeout=10 )
            except pexpect.EOF:
                main.log.error( self.name + ": EOF exception found" )
                main.log.error( self.name + ":     " + self.handle.before )
                main.cleanup()
                main.exit()

            pattern = "inet\s(addr|Mask):([0-1]{1}[0-9]{1,2}|" +\
                "2[0-4][0-9]|25[0-5]|[0-9]{1,2}).([0-1]{1}" +\
                "[0-9]{1,2}|2[0-4][0-9]|25[0-5]|[0-9]{1,2})." +\
                "([0-1]{1}[0-9]{1,2}|2[0-4][0-9]|25[0-5]|" +\
                "[0-9]{1,2}).([0-1]{1}[0-9]{1,2}|2[0-4]" +\
                "[0-9]|25[0-5]|[0-9]{1,2})"
            # pattern = "inet addr:10.0.0.6"
            if re.search( pattern, response ):
                main.log.info( self.name + ": Host Ip configured properly" )
                return main.TRUE
            else:
                main.log.error( self.name + ": Host IP not found" )
                return main.FALSE
        else:
            main.log.error( self.name + ": Connection failed to the host" )

    def verifySSH( self, **connectargs ):
        try:
            response = self.execute(
                cmd="h1 /usr/sbin/sshd -D&",
                prompt="mininet>",
                timeout=10 )
            response = self.execute(
                cmd="h4 /usr/sbin/sshd -D&",
                prompt="mininet>",
                timeout=10 )
            for key in connectargs:
                vars( self )[ key ] = connectargs[ key ]
            response = self.execute(
                cmd="xterm h1 h4 ",
                prompt="mininet>",
                timeout=10 )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        import time
        time.sleep( 20 )
        if self.flag == 0:
            self.flag = 1
            return main.FALSE
        else:
            return main.TRUE

    def moveHost( self, host, oldSw, newSw, ):
        """
           Moves a host from one switch to another on the fly
           Note: The intf between host and oldSw when detached
                using detach(), will still show up in the 'net'
                cmd, because switch.detach() doesn't affect switch.intfs[]
                (which is correct behavior since the interfaces 
                haven't moved).
        """
        if self.handle:
            try:
                # Bring link between oldSw-host down
                cmd = "py net.configLinkStatus('" + oldSw + "'," + "'" + host + "'," +\
                "'down')"
                print "cmd1= ", cmd
                response = self.execute(
                cmd=cmd,
                prompt="mininet>",
                timeout=10 )
     
                # Determine hostintf and Oldswitchintf
                cmd = "px hintf,sintf = " + host + ".connectionsTo(" + oldSw +\
                ")[0]"
                print "cmd2= ", cmd
                self.handle.sendline( cmd )
                self.handle.expect( "mininet>" )

                # Determine ipaddress of the host-oldSw interface
                cmd = "px ipaddr = hintf.IP()"
                print "cmd3= ", cmd
                self.handle.sendline( cmd )
                self.handle.expect( "mininet>" )
                
                # Detach interface between oldSw-host
                cmd = "px " + oldSw + ".detach( sintf )"
                print "cmd4= ", cmd
                self.handle.sendline( cmd )
                self.handle.expect( "mininet>" )

                # Add link between host-newSw
                cmd = "py net.addLink(" + host + "," + newSw + ")"
                print "cmd5= ", cmd
                self.handle.sendline( cmd )
                self.handle.expect( "mininet>" )
 
                # Determine hostintf and Newswitchintf
                cmd = "px hintf,sintf = " + host + ".connectionsTo(" + newSw +\
                ")[0]"
                print "cmd6= ", cmd
                self.handle.sendline( cmd )
                self.handle.expect( "mininet>" )                 

                # Attach interface between newSw-host
                cmd = "px " + newSw + ".attach( sintf )"
                print "cmd3= ", cmd
                self.handle.sendline( cmd )
                self.handle.expect( "mininet>" )
                
                # Set ipaddress of the host-newSw interface
                cmd = "px " + host + ".setIP( ip = ipaddr, intf = hintf)"
                print "cmd7 = ", cmd
                self.handle.sendline( cmd )
                self.handle.expect( "mininet>" )
                
                cmd = "net"
                print "cmd8 = ", cmd
                self.handle.sendline( cmd )
                self.handle.expect( "mininet>" )
                print "output = ", self.handle.before

                # Determine ipaddress of the host-newSw interface
                cmd = "h1 ifconfig"
                print "cmd9= ", cmd
                self.handle.sendline( cmd )
                self.handle.expect( "mininet>" )
                print "ifconfig o/p = ", self.handle.before
                
                return main.TRUE
            except pexpect.EOF:
                main.log.error( self.name + ": EOF exception found" )
                main.log.error( self.name + ":     " + self.handle.before )
                return main.FALSE

    def changeIP( self, host, intf, newIP, newNetmask ):
        """
           Changes the ip address of a host on the fly
           Ex: h2 ifconfig h2-eth0 10.0.1.2 netmask 255.255.255.0"""
        if self.handle:
            try:
                cmd = host + " ifconfig " + intf + " " + \
                    newIP + " " + 'netmask' + " " + newNetmask
                self.handle.sendline( cmd )
                self.handle.expect( "mininet>" )
                response = self.handle.before
                main.log.info( "response = " + response )
                main.log.info(
                    "Ip of host " +
                    host +
                    " changed to new IP " +
                    newIP )
                return main.TRUE
            except pexpect.EOF:
                main.log.error( self.name + ": EOF exception found" )
                main.log.error( self.name + ":     " + self.handle.before )
                return main.FALSE

    def changeDefaultGateway( self, host, newGW ):
        """
           Changes the default gateway of a host
           Ex: h1 route add default gw 10.0.1.2"""
        if self.handle:
            try:
                cmd = host + " route add default gw " + newGW
                self.handle.sendline( cmd )
                self.handle.expect( "mininet>" )
                response = self.handle.before
                main.log.info( "response = " + response )
                main.log.info(
                    "Default gateway of host " +
                    host +
                    " changed to " +
                    newGW )
                return main.TRUE
            except pexpect.EOF:
                main.log.error( self.name + ": EOF exception found" )
                main.log.error( self.name + ":     " + self.handle.before )
                return main.FALSE

    def addStaticMACAddress( self, host, GW, macaddr ):
        """
           Changes the mac address of a geateway host"""
        if self.handle:
            try:
                # h1  arp -s 10.0.1.254 00:00:00:00:11:11
                cmd = host + " arp -s " + GW + " " + macaddr
                self.handle.sendline( cmd )
                self.handle.expect( "mininet>" )
                response = self.handle.before
                main.log.info( "response = " + response )
                main.log.info(
                    "Mac adrress of gateway " +
                    GW +
                    " changed to " +
                    macaddr )
                return main.TRUE
            except pexpect.EOF:
                main.log.error( self.name + ": EOF exception found" )
                main.log.error( self.name + ":     " + self.handle.before )
                return main.FALSE

    def verifyStaticGWandMAC( self, host ):
        """
           Verify if the static gateway and mac address assignment"""
        if self.handle:
            try:
                # h1  arp -an
                cmd = host + " arp -an "
                self.handle.sendline( cmd )
                self.handle.expect( "mininet>" )
                response = self.handle.before
                main.log.info( host + " arp -an = " + response )
                return main.TRUE
            except pexpect.EOF:
                main.log.error( self.name + ": EOF exception found" )
                main.log.error( self.name + ":     " + self.handle.before )
                return main.FALSE

    def getMacAddress( self, host ):
        """
           Verifies the host's ip configured or not."""
        if self.handle:
            try:
                response = self.execute(
                    cmd=host +
                    " ifconfig",
                    prompt="mininet>",
                    timeout=10 )
            except pexpect.EOF:
                main.log.error( self.name + ": EOF exception found" )
                main.log.error( self.name + ":     " + self.handle.before )
                main.cleanup()
                main.exit()

            pattern = r'HWaddr\s([0-9A-F]{2}[:-]){5}([0-9A-F]{2})'
            macAddressSearch = re.search( pattern, response, re.I )
            macAddress = macAddressSearch.group().split( " " )[ 1 ]
            main.log.info(
                self.name +
                ": Mac-Address of Host " +
                host +
                " is " +
                macAddress )
            return macAddress
        else:
            main.log.error( self.name + ": Connection failed to the host" )

    def getInterfaceMACAddress( self, host, interface ):
        """
           Return the IP address of the interface on the given host"""
        if self.handle:
            try:
                response = self.execute( cmd=host + " ifconfig " + interface,
                                         prompt="mininet>", timeout=10 )
            except pexpect.EOF:
                main.log.error( self.name + ": EOF exception found" )
                main.log.error( self.name + ":     " + self.handle.before )
                main.cleanup()
                main.exit()

            pattern = r'HWaddr\s([0-9A-F]{2}[:-]){5}([0-9A-F]{2})'
            macAddressSearch = re.search( pattern, response, re.I )
            if macAddressSearch is None:
                main.log.info( "No mac address found in %s" % response )
                return main.FALSE
            macAddress = macAddressSearch.group().split( " " )[ 1 ]
            main.log.info(
                "Mac-Address of " +
                host +
                ":" +
                interface +
                " is " +
                macAddress )
            return macAddress
        else:
            main.log.error( "Connection failed to the host" )

    def getIPAddress( self, host ):
        """
           Verifies the host's ip configured or not."""
        if self.handle:
            try:
                response = self.execute(
                    cmd=host +
                    " ifconfig",
                    prompt="mininet>",
                    timeout=10 )
            except pexpect.EOF:
                main.log.error( self.name + ": EOF exception found" )
                main.log.error( self.name + ":     " + self.handle.before )
                main.cleanup()
                main.exit()

            pattern = "inet\saddr:(\d+\.\d+\.\d+\.\d+)"
            ipAddressSearch = re.search( pattern, response )
            main.log.info(
                self.name +
                ": IP-Address of Host " +
                host +
                " is " +
                ipAddressSearch.group( 1 ) )
            return ipAddressSearch.group( 1 )
        else:
            main.log.error( self.name + ": Connection failed to the host" )

    def getSwitchDPID( self, switch ):
        """
           return the datapath ID of the switch"""
        if self.handle:
            cmd = "py %s.dpid" % switch
            try:
                response = self.execute(
                    cmd=cmd,
                    prompt="mininet>",
                    timeout=10 )
            except pexpect.EOF:
                main.log.error( self.name + ": EOF exception found" )
                main.log.error( self.name + ":     " + self.handle.before )
                main.cleanup()
                main.exit()
            pattern = r'^(?P<dpid>\w)+'
            result = re.search( pattern, response, re.MULTILINE )
            if result is None:
                main.log.info(
                    "Couldn't find DPID for switch %s, found: %s" %
                    ( switch, response ) )
                return main.FALSE
            return str( result.group( 0 ) ).lower()
        else:
            main.log.error( "Connection failed to the host" )

    def getDPID( self, switch ):
        if self.handle:
            self.handle.sendline( "" )
            self.expect( "mininet>" )
            cmd = "py %s.dpid" % switch
            try:
                response = self.execute(
                    cmd=cmd,
                    prompt="mininet>",
                    timeout=10 )
                self.handle.expect( "mininet>" )
                response = self.handle.before
                return response
            except pexpect.EOF:
                main.log.error( self.name + ": EOF exception found" )
                main.log.error( self.name + ":     " + self.handle.before )
                main.cleanup()
                main.exit()

    def getInterfaces( self, node ):
        """
           return information dict about interfaces connected to the node"""
        if self.handle:
            cmd = 'py "\\n".join(["name=%s,mac=%s,ip=%s,enabled=%s"' +\
                ' % (i.name, i.MAC(), i.IP(), i.isUp())'
            cmd += ' for i in %s.intfs.values()])' % node
            try:
                response = self.execute(
                    cmd=cmd,
                    prompt="mininet>",
                    timeout=10 )
            except pexpect.EOF:
                main.log.error( self.name + ": EOF exception found" )
                main.log.error( self.name + ":     " + self.handle.before )
                main.cleanup()
                main.exit()
            return response
        else:
            main.log.error( "Connection failed to the node" )

    def dump( self ):
        main.log.info( self.name + ": Dump node info" )
        try:
            response = self.execute(
                cmd='dump',
                prompt='mininet>',
                timeout=10 )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        return response

    def intfs( self ):
        main.log.info( self.name + ": List interfaces" )
        try:
            response = self.execute(
                cmd='intfs',
                prompt='mininet>',
                timeout=10 )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        return response

    def net( self ):
        main.log.info( self.name + ": List network connections" )
        try:
            response = self.execute( cmd='net', prompt='mininet>', timeout=10 )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        return response

    def iperf( self, host1, host2 ):
        main.log.info(
            self.name +
            ": Simple iperf TCP test between two hosts" )
        try:
            cmd1 = 'iperf ' + host1 + " " + host2
            self.handle.sendline( cmd1 )
            self.handle.expect( "mininet>" )
            response = self.handle.before
            if re.search( 'Results:', response ):
                main.log.info( self.name + ": iperf test succssful" )
                return main.TRUE
            else:
                main.log.error( self.name + ": iperf test failed" )
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()

    def iperfudp( self ):
        main.log.info(
            self.name +
            ": Simple iperf TCP test between two " +
            "(optionally specified) hosts" )
        try:
            response = self.execute(
                cmd='iperfudp',
                prompt='mininet>',
                timeout=10 )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        return response

    def nodes( self ):
        main.log.info( self.name + ": List all nodes." )
        try:
            response = self.execute(
                cmd='nodes',
                prompt='mininet>',
                timeout=10 )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        return response

    def pingpair( self ):
        main.log.info( self.name + ": Ping between first two hosts" )
        try:
            response = self.execute(
                cmd='pingpair',
                prompt='mininet>',
                timeout=20 )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()

        if re.search( ',\s0\%\spacket\sloss', response ):
            main.log.info( self.name + ": Ping between two hosts SUCCESSFUL" )
            main.lastResult = main.TRUE
            return main.TRUE
        else:
            main.log.error( self.name + ": PACKET LOST, HOSTS NOT REACHABLE" )
            main.lastResult = main.FALSE
            return main.FALSE

    def link( self, **linkargs ):
        """
           Bring link( s ) between two nodes up or down"""
        args = utilities.parse_args( [ "END1", "END2", "OPTION" ], **linkargs )
        end1 = args[ "END1" ] if args[ "END1" ] is not None else ""
        end2 = args[ "END2" ] if args[ "END2" ] is not None else ""
        option = args[ "OPTION" ] if args[ "OPTION" ] is not None else ""
        main.log.info(
            "Bring link between '" +
            end1 +
            "' and '" +
            end2 +
            "' '" +
            option +
            "'" )
        command = "link " + \
            str( end1 ) + " " + str( end2 ) + " " + str( option )
        try:
            self.handle.sendline( command )
            self.handle.expect( "mininet>" )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        return main.TRUE

    def yank( self, **yankargs ):
        """
           yank a mininet switch interface to a host"""
        main.log.info( 'Yank the switch interface attached to a host' )
        args = utilities.parse_args( [ "SW", "INTF" ], **yankargs )
        sw = args[ "SW" ] if args[ "SW" ] is not None else ""
        intf = args[ "INTF" ] if args[ "INTF" ] is not None else ""
        command = "py " + str( sw ) + '.detach("' + str(intf) + '")'
        try:
            response = self.execute(
                cmd=command,
                prompt="mininet>",
                timeout=10 )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        return main.TRUE

    def plug( self, **plugargs ):
        """
           plug the yanked mininet switch interface to a switch"""
        main.log.info( 'Plug the switch interface attached to a switch' )
        args = utilities.parse_args( [ "SW", "INTF" ], **plugargs )
        sw = args[ "SW" ] if args[ "SW" ] is not None else ""
        intf = args[ "INTF" ] if args[ "INTF" ] is not None else ""
        command = "py " + str( sw ) + '.attach("' + str(intf) + '")'
        try:
            response = self.execute(
                cmd=command,
                prompt="mininet>",
                timeout=10 )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        return main.TRUE

    def dpctl( self, **dpctlargs ):
        """
           Run dpctl command on all switches."""
        main.log.info( 'Run dpctl command on all switches' )
        args = utilities.parse_args( [ "CMD", "ARGS" ], **dpctlargs )
        cmd = args[ "CMD" ] if args[ "CMD" ] is not None else ""
        cmdargs = args[ "ARGS" ] if args[ "ARGS" ] is not None else ""
        command = "dpctl " + cmd + " " + str( cmdargs )
        try:
            response = self.execute(
                cmd=command,
                prompt="mininet>",
                timeout=10 )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        return main.TRUE

    def getVersion( self ):
        fileInput = path + '/lib/Mininet/INSTALL'
        version = super( Mininet, self ).getVersion()
        pattern = 'Mininet\s\w\.\w\.\w\w*'
        for line in open( fileInput, 'r' ).readlines():
            result = re.match( pattern, line )
            if result:
                version = result.group( 0 )
        return version

    def getSwController( self, sw ):
        """
        Parameters:
            sw: The name of an OVS switch. Example "s1"
        Return:
            The output of the command from the mininet cli
            or main.FALSE on timeout"""
        command = "sh ovs-vsctl get-controller " + str( sw )
        try:
            response = self.execute(
                cmd=command,
                prompt="mininet>",
                timeout=10 )
            if response:
                return response
            else:
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()

    def assignSwController( self, **kwargs ):
        """
           count is only needed if there is more than 1 controller"""
        args = utilities.parse_args( [ "COUNT" ], **kwargs )
        count = args[ "COUNT" ] if args != {} else 1

        argstring = "SW"
        for j in range( count ):
            argstring = argstring + ",IP" + \
                str( j + 1 ) + ",PORT" + str( j + 1 )
        args = utilities.parse_args( argstring.split( "," ), **kwargs )

        sw = args[ "SW" ] if args[ "SW" ] is not None else ""
        ptcpA = int( args[ "PORT1" ] ) + \
            int( sw ) if args[ "PORT1" ] is not None else ""
        ptcpB = "ptcp:" + str( ptcpA ) if ptcpA != "" else ""

        command = "sh ovs-vsctl set-controller s" + \
            str( sw ) + " " + ptcpB + " "
        for j in range( count ):
            i = j + 1
            args = utilities.parse_args(
                [ "IP" + str( i ), "PORT" + str( i ) ], **kwargs )
            ip = args[
                "IP" +
                str( i ) ] if args[
                "IP" +
                str( i ) ] is not None else ""
            port = args[
                "PORT" +
                str( i ) ] if args[
                "PORT" +
                str( i ) ] is not None else ""
            tcp = "tcp:" + str( ip ) + ":" + str( port ) + \
                " " if ip != "" else ""
            command = command + tcp
        try:
            self.execute( cmd=command, prompt="mininet>", timeout=5 )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.info( self.name + ":" * 50 )
            main.log.error( traceback.print_exc() )
            main.log.info( ":" * 50 )
            main.cleanup()
            main.exit()

    def deleteSwController( self, sw ):
        """
           Removes the controller target from sw"""
        command = "sh ovs-vsctl del-controller " + str( sw )
        try:
            response = self.execute(
                cmd=command,
                prompt="mininet>",
                timeout=10 )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        else:
            main.log.info( response )

    def addSwitch( self, sw, **kwargs ):
        """
        adds a switch to the mininet topology
        NOTE: This uses a custom mn function. MN repo should be on
            dynamic_topo branch
        NOTE: cannot currently specify what type of switch
        required params:
            switchname = name of the new switch as a string
        optional keyvalues:
            dpid = "dpid"
        returns: main.FASLE on an error, else main.TRUE
        """
        dpid = kwargs.get( 'dpid', '' )
        command = "addswitch " + str( sw ) + " " + str( dpid )
        try:
            response = self.execute(
                cmd=command,
                prompt="mininet>",
                timeout=10 )
            if re.search( "already exists!", response ):
                main.log.warn( response )
                return main.FALSE
            elif re.search( "Error", response ):
                main.log.warn( response )
                return main.FALSE
            elif re.search( "usage:", response ):
                main.log.warn( response )
                return main.FALSE
            else:
                return main.TRUE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()

    def delSwitch( self, sw ):
        """
        delete a switch from the mininet topology
        NOTE: This uses a custom mn function. MN repo should be on
            dynamic_topo branch
        required params:
            switchname = name of the switch as a string
        returns: main.FASLE on an error, else main.TRUE"""
        command = "delswitch " + str( sw )
        try:
            response = self.execute(
                cmd=command,
                prompt="mininet>",
                timeout=10 )
            if re.search( "no switch named", response ):
                main.log.warn( response )
                return main.FALSE
            elif re.search( "Error", response ):
                main.log.warn( response )
                return main.FALSE
            elif re.search( "usage:", response ):
                main.log.warn( response )
                return main.FALSE
            else:
                return main.TRUE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()

    def addLink( self, node1, node2 ):
        """
           add a link to the mininet topology
           NOTE: This uses a custom mn function. MN repo should be on
                dynamic_topo branch
           NOTE: cannot currently specify what type of link
           required params:
           node1 = the string node name of the first endpoint of the link
           node2 = the string node name of the second endpoint of the link
           returns: main.FASLE on an error, else main.TRUE"""
        command = "addlink " + str( node1 ) + " " + str( node2 )
        try:
            response = self.execute(
                cmd=command,
                prompt="mininet>",
                timeout=10 )
            if re.search( "doesnt exist!", response ):
                main.log.warn( response )
                return main.FALSE
            elif re.search( "Error", response ):
                main.log.warn( response )
                return main.FALSE
            elif re.search( "usage:", response ):
                main.log.warn( response )
                return main.FALSE
            else:
                return main.TRUE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()

    def delLink( self, node1, node2 ):
        """
           delete a link from the mininet topology
           NOTE: This uses a custom mn function. MN repo should be on
                dynamic_topo branch
           required params:
           node1 = the string node name of the first endpoint of the link
           node2 = the string node name of the second endpoint of the link
           returns: main.FASLE on an error, else main.TRUE"""
        command = "dellink " + str( node1 ) + " " + str( node2 )
        try:
            response = self.execute(
                cmd=command,
                prompt="mininet>",
                timeout=10 )
            if re.search( "no node named", response ):
                main.log.warn( response )
                return main.FALSE
            elif re.search( "Error", response ):
                main.log.warn( response )
                return main.FALSE
            elif re.search( "usage:", response ):
                main.log.warn( response )
                return main.FALSE
            else:
                return main.TRUE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()

    def addHost( self, hostname, **kwargs ):
        """
        Add a host to the mininet topology
        NOTE: This uses a custom mn function. MN repo should be on
            dynamic_topo branch
        NOTE: cannot currently specify what type of host
        required params:
            hostname = the string hostname
        optional key-value params
            switch = "switch name"
            returns: main.FASLE on an error, else main.TRUE
        """
        switch = kwargs.get( 'switch', '' )
        command = "addhost " + str( hostname ) + " " + str( switch )
        try:
            response = self.execute(
                cmd=command,
                prompt="mininet>",
                timeout=10 )
            if re.search( "already exists!", response ):
                main.log.warn( response )
                return main.FALSE
            elif re.search( "doesnt exists!", response ):
                main.log.warn( response )
                return main.FALSE
            elif re.search( "Error", response ):
                main.log.warn( response )
                return main.FALSE
            elif re.search( "usage:", response ):
                main.log.warn( response )
                return main.FALSE
            else:
                return main.TRUE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()

    def delHost( self, hostname ):
        """
           delete a host from the mininet topology
           NOTE: This uses a custom mn function. MN repo should be on
               dynamic_topo branch
           NOTE: this uses a custom mn function
           required params:
           hostname = the string hostname
           returns: main.FASLE on an error, else main.TRUE"""
        command = "delhost " + str( hostname )
        try:
            response = self.execute(
                cmd=command,
                prompt="mininet>",
                timeout=10 )
            if re.search( "no host named", response ):
                main.log.warn( response )
                return main.FALSE
            elif re.search( "Error", response ):
                main.log.warn( response )
                return main.FALSE
            elif re.search( "usage:", response ):
                main.log.warn( response )
                return main.FALSE
            else:
                return main.TRUE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()

    def disconnect( self ):
        """
        Called at the end of the test to stop the mininet and
        disconnect the handle.
        """
        self.handle.sendline('')
        i = 1
        i = self.handle.expect( ['mininet>',pexpect.EOF,pexpect.TIMEOUT ], timeout = 2)
        if i == 0:
            self.stopNet()
        response = ''
        # print "Disconnecting Mininet"
        if self.handle:
            self.handle.sendline( "exit" )
            self.handle.expect( "exit" )
            self.handle.expect( "(.*)" )
            main.log.info( "Mininet CLI is successfully disconnected" )
            response = main.TRUE
        else:
            main.log.error( "Connection failed to the host" )
            response = main.FALSE

        return response

    def stopNet( self , timeout = 5):
        """
        Stops mininet. returns true if the mininet succesfully stops.
        """
        
        main.log.info( self.name + ": Disconnecting mininet..." )
        response = ''
        if self.handle:
            try:
                self.handle.sendline("")
                i = self.handle.expect( [ 'mininet>',
                                          '\$',
                                          pexpect.EOF,
                                          pexpect.TIMEOUT ],
                                        timeout )
                if i == 0:
                    main.log.info( "Exiting mininet..." )
               
                response = self.execute(
                    cmd="exit",
                    prompt="(.*)",
                    timeout=120 )
                main.log.info( self.name + ": Disconnected")
                self.handle.sendline( "sudo mn -c" )
                response = main.TRUE

                if i == 1:
                    main.log.info( " Mininet trying to exit while not " +
                                   "in the mininet prompt" )
                elif i == 2:
                    main.log.error( "Something went wrong exiting mininet" )
                elif i == 3:  # timeout
                    main.log.error( "Something went wrong exiting mininet " +
                                    "TIMEOUT" )
                
            except pexpect.EOF:
                main.log.error( self.name + ": EOF exception found" )
                main.log.error( self.name + ":     " + self.handle.before )
                main.cleanup()
                main.exit()
        else:
            main.log.error( self.name + ": Connection failed to the host" )
            response = main.FALSE
        return response



    def arping( self, src, dest, destmac ):
        self.handle.sendline( '' )
        self.handle.expect( [ "mininet", pexpect.EOF, pexpect.TIMEOUT ] )

        self.handle.sendline( src + ' arping ' + dest )
        try:
            self.handle.expect( [ destmac, pexpect.EOF, pexpect.TIMEOUT ] )
            main.log.info( self.name + ": ARP successful" )
            self.handle.expect( [ "mininet", pexpect.EOF, pexpect.TIMEOUT ] )
            return main.TRUE
        except:
            main.log.warn( self.name + ": ARP FAILURE" )
            self.handle.expect( [ "mininet", pexpect.EOF, pexpect.TIMEOUT ] )
            return main.FALSE

    def decToHex( self, num ):
        return hex( num ).split( 'x' )[ 1 ]

    def getSwitchFlowCount( self, switch ):
        """
           return the Flow Count of the switch"""
        if self.handle:
            cmd = "sh ovs-ofctl dump-aggregate %s" % switch
            try:
                response = self.execute(
                    cmd=cmd,
                    prompt="mininet>",
                    timeout=10 )
            except pexpect.EOF:
                main.log.error( self.name + ": EOF exception found" )
                main.log.error( self.name + "     " + self.handle.before )
                main.cleanup()
                main.exit()
            pattern = "flow_count=(\d+)"
            result = re.search( pattern, response, re.MULTILINE )
            if result is None:
                main.log.info(
                    "Couldn't find flows on switch %s, found: %s" %
                    ( switch, response ) )
                return main.FALSE
            return result.group( 1 )
        else:
            main.log.error( "Connection failed to the Mininet host" )

    def checkFlows( self, sw, dumpFormat=None ):
        if dumpFormat:
            command = "sh ovs-ofctl -F " + \
                dumpFormat + " dump-flows " + str( sw )
        else:
            command = "sh ovs-ofctl dump-flows " + str( sw )
        try:
            response = self.execute(
                cmd=command,
                prompt="mininet>",
                timeout=10 )
            return response
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        else:
            main.log.info( response )

    def startTcpdump( self, filename, intf="eth0", port="port 6633" ):
        """
           Runs tpdump on an intferface and saves the file
           intf can be specified, or the default eth0 is used"""
        try:
            self.handle.sendline( "" )
            self.handle.expect( "mininet>" )
            self.handle.sendline(
                "sh sudo tcpdump -n -i " +
                intf +
                " " +
                port +
                " -w " +
                filename.strip() +
                "  &" )
            self.handle.sendline( "" )
            i = self.handle.expect( [ 'No\ssuch\device',
                                      'listening\son',
                                      pexpect.TIMEOUT,
                                      "mininet>" ],
                                    timeout=10 )
            main.log.warn( self.handle.before + self.handle.after )
            self.handle.sendline( "" )
            self.handle.expect( "mininet>" )
            if i == 0:
                main.log.error(
                    self.name +
                    ": tcpdump - No such device exists. " +
                    "tcpdump attempted on: " +
                    intf )
                return main.FALSE
            elif i == 1:
                main.log.info( self.name + ": tcpdump started on " + intf )
                return main.TRUE
            elif i == 2:
                main.log.error(
                    self.name +
                    ": tcpdump command timed out! Check interface name," +
                    " given interface was: " +
                    intf )
                return main.FALSE
            elif i == 3:
                main.log.info( self.name + ": " + self.handle.before )
                return main.TRUE
            else:
                main.log.error( self.name + ": tcpdump - unexpected response" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.info( self.name + ":" * 50 )
            main.log.error( traceback.print_exc() )
            main.log.info( ":" * 50 )
            main.cleanup()
            main.exit()

    def stopTcpdump( self ):
        "pkills tcpdump"
        try:
            self.handle.sendline( "sh sudo pkill tcpdump" )
            self.handle.expect( "mininet>" )
            self.handle.sendline( "" )
            self.handle.expect( "mininet>" )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.info( self.name + ":" * 50 )
            main.log.error( traceback.print_exc() )
            main.log.info( ":" * 50 )
            main.cleanup()
            main.exit()

    def compareSwitches( self, topo, switchesJson ):
        """
           Compare mn and onos switches
           topo: sts TestONTopology object
            switchesJson: parsed json object from the onos devices api

           This uses the sts TestONTopology object"""
        # main.log.debug( "Switches_json string: ", switchesJson )
        output = { "switches": [] }
        # iterate through the MN topology and pull out switches and and port
        # info
        for switch in topo.graph.switches:
            ports = []
            for port in switch.ports.values():
                ports.append( { 'of_port': port.port_no,
                                'mac': str( port.hw_addr ).replace( '\'',
                                                                   '' ),
                                'name': port.name } )
            output[ 'switches' ].append( {
                "name": switch.name,
                "dpid": str( switch.dpid ).zfill( 16 ),
                "ports": ports } )

        # print "mn"
        # print json.dumps( output,
        #                   sortKeys=True,
        #                   indent=4,
        #                   separators=( ',', ': ' ) )
        # print "onos"
        # print json.dumps( switchesJson,
        #                   sortKeys=True,
        #                   indent=4,
        #                   separators=( ',', ': ' ) )

        # created sorted list of dpid's in MN and ONOS for comparison
        mnDPIDs = []
        for switch in output[ 'switches' ]:
            mnDPIDs.append( switch[ 'dpid' ].lower() )
        mnDPIDs.sort()
        # print "List of Mininet switch DPID's"
        # print mnDPIDs
        if switchesJson == "":  # if rest call fails
            main.log.error(
                self.name +
                ".compare_switches(): Empty JSON object given from ONOS" )
            return main.FALSE
        onos = switchesJson
        onosDPIDs = []
        for switch in onos:
            if switch[ 'available' ]:
                onosDPIDs.append(
                    switch[ 'id' ].replace(
                        ":",
                        '' ).replace(
                        "of",
                        '' ).lower() )
            # else:
                # print "Switch is unavailable:"
                # print switch
        onosDPIDs.sort()
        # print "List of ONOS switch DPID's"
        # print onosDPIDs

        if mnDPIDs != onosDPIDs:
            switchResults = main.FALSE
            main.log.report( "Switches in MN but not in ONOS:" )
            list1 = [ switch for switch in mnDPIDs if switch not in onosDPIDs ]
            main.log.report( str( list1 ) )
            main.log.report( "Switches in ONOS but not in MN:" )
            list2 = [ switch for switch in onosDPIDs if switch not in mnDPIDs ]
            main.log.report( str( list2 ) )
        else:  # list of dpid's match in onos and mn
            switchResults = main.TRUE
        return switchResults

    def comparePorts( self, topo, portsJson ):
        """
        Compare mn and onos ports
        topo: sts TestONTopology object
        portsJson: parsed json object from the onos ports api

        Dependencies:
            1. This uses the sts TestONTopology object
            2. numpy - "sudo pip install numpy"

        """
        # FIXME: this does not look for extra ports in ONOS, only checks that
        # ONOS has what is in MN
        from numpy import uint64
        portsResults = main.TRUE
        output = { "switches": [] }
        # iterate through the MN topology and pull out switches and and port
        # info
        for switch in topo.graph.switches:
            ports = []
            for port in switch.ports.values():
                # print port.hw_addr.toStr( separator='' )
                tmpPort = {}
                tmpPort[ 'of_port' ] = port.port_no
                tmpPort[ 'mac' ] = str( port.hw_addr ).replace( '\'', '' )
                tmpPort[ 'name' ] = port.name
                tmpPort[ 'enabled' ] = port.enabled

                ports.append( tmpPort )
            tmpSwitch = {}
            tmpSwitch[ 'name' ] = switch.name
            tmpSwitch[ 'dpid' ] = str( switch.dpid ).zfill( 16 )
            tmpSwitch[ 'ports' ] = ports

            output[ 'switches' ].append( tmpSwitch )

        # PORTS
        for mnSwitch in output[ 'switches' ]:
            mnPorts = []
            onosPorts = []
            switchResult = main.TRUE
            for port in mnSwitch[ 'ports' ]:
                if port[ 'enabled' ]:
                    mnPorts.append( port[ 'of_port' ] )
            for onosSwitch in portsJson:
                # print "Iterating through a new switch as seen by ONOS"
                # print onosSwitch
                if onosSwitch[ 'device' ][ 'available' ]:
                    if onosSwitch[ 'device' ][ 'id' ].replace(
                            ':',
                            '' ).replace(
                            "of",
                            '' ) == mnSwitch[ 'dpid' ]:
                        for port in onosSwitch[ 'ports' ]:
                            if port[ 'isEnabled' ]:
                                if port[ 'port' ] == 'local':
                                    # onosPorts.append( 'local' )
                                    onosPorts.append( long( uint64( -2 ) ) )
                                else:
                                    onosPorts.append( int( port[ 'port' ] ) )
                        break
            mnPorts.sort( key=float )
            onosPorts.sort( key=float )
            # print "\nPorts for Switch %s:" % ( mnSwitch[ 'name' ] )
            # print "\tmn_ports[] = ", mnPorts
            # print "\tonos_ports[] = ", onosPorts
            mnPortsLog = mnPorts
            onosPortsLog = onosPorts
            mnPorts = [ x for x in mnPorts ]
            onosPorts = [ x for x in onosPorts ]

            # TODO: handle other reserved port numbers besides LOCAL
            # NOTE: Reserved ports
            # Local port: -2 in Openflow, ONOS shows 'local', we store as
            # long( uint64( -2 ) )
            for mnPort in mnPortsLog:
                if mnPort in onosPorts:
                    # don't set results to true here as this is just one of
                    # many checks and it might override a failure
                    mnPorts.remove( mnPort )
                    onosPorts.remove( mnPort )
                # NOTE: OVS reports this as down since there is no link
                #      So ignoring these for now
                # TODO: Come up with a better way of handling these
                if 65534 in mnPorts:
                    mnPorts.remove( 65534 )
                if long( uint64( -2 ) ) in onosPorts:
                    onosPorts.remove( long( uint64( -2 ) ) )
            if len( mnPorts ):  # the ports of this switch don't match
                switchResult = main.FALSE
                main.log.warn( "Ports in MN but not ONOS: " + str( mnPorts ) )
            if len( onosPorts ):  # the ports of this switch don't match
                switchResult = main.FALSE
                main.log.warn(
                    "Ports in ONOS but not MN: " +
                    str( onosPorts ) )
            if switchResult == main.FALSE:
                main.log.report(
                    "The list of ports for switch %s(%s) does not match:" %
                    ( mnSwitch[ 'name' ], mnSwitch[ 'dpid' ] ) )
                main.log.warn( "mn_ports[]  =  " + str( mnPortsLog ) )
                main.log.warn( "onos_ports[] = " + str( onosPortsLog ) )
            portsResults = portsResults and switchResult
        return portsResults

    def compareLinks( self, topo, linksJson ):
        """
           Compare mn and onos links
           topo: sts TestONTopology object
           linksJson: parsed json object from the onos links api

           This uses the sts TestONTopology object"""
        # FIXME: this does not look for extra links in ONOS, only checks that
        # ONOS has what is in MN
        linkResults = main.TRUE
        output = { "switches": [] }
        onos = linksJson
        # iterate through the MN topology and pull out switches and and port
        # info
        for switch in topo.graph.switches:
            # print "Iterating though switches as seen by Mininet"
            # print switch
            ports = []
            for port in switch.ports.values():
                # print port.hw_addr.toStr( separator='' )
                ports.append( { 'of_port': port.port_no,
                                'mac': str( port.hw_addr ).replace( '\'',
                                                                   '' ),
                                'name': port.name } )
            output[ 'switches' ].append( {
                "name": switch.name,
                "dpid": str( switch.dpid ).zfill( 16 ),
                "ports": ports } )
        # LINKS

        mnLinks = [
            link for link in topo.patch_panel.network_links if (
                link.port1.enabled and link.port2.enabled ) ]
        if 2 * len( mnLinks ) == len( onos ):
            linkResults = main.TRUE
        else:
            linkResults = main.FALSE
            main.log.report(
                "Mininet has " + str( len( mnLinks ) ) +
                " bidirectional links and ONOS has " +
                str( len( onos ) ) + " unidirectional links" )

        # iterate through MN links and check if an ONOS link exists in
        # both directions
        # NOTE: Will currently only show mn links as down if they are
        #       cut through STS. We can either do everything through STS or
        #       wait for upNetworkLinks and downNetworkLinks to be
        #       fully implemented.
        for link in mnLinks:
            # print "Link: %s" % link
            # TODO: Find a more efficient search method
            node1 = None
            port1 = None
            node2 = None
            port2 = None
            firstDir = main.FALSE
            secondDir = main.FALSE
            for switch in output[ 'switches' ]:
                # print "Switch: %s" % switch[ 'name' ]
                if switch[ 'name' ] == link.node1.name:
                    node1 = switch[ 'dpid' ]
                    for port in switch[ 'ports' ]:
                        if str( port[ 'name' ] ) == str( link.port1 ):
                            port1 = port[ 'of_port' ]
                    if node1 is not None and node2 is not None:
                        break
                if switch[ 'name' ] == link.node2.name:
                    node2 = switch[ 'dpid' ]
                    for port in switch[ 'ports' ]:
                        if str( port[ 'name' ] ) == str( link.port2 ):
                            port2 = port[ 'of_port' ]
                    if node1 is not None and node2 is not None:
                        break

            for onosLink in onos:
                onosNode1 = onosLink[ 'src' ][ 'device' ].replace(
                    ":",
                    '' ).replace(
                    "of",
                    '' )
                onosNode2 = onosLink[ 'dst' ][ 'device' ].replace(
                    ":",
                    '' ).replace(
                    "of",
                    '' )
                onosPort1 = onosLink[ 'src' ][ 'port' ]
                onosPort2 = onosLink[ 'dst' ][ 'port' ]

                # check onos link from node1 to node2
                if str( onosNode1 ) == str( node1 ) and str(
                        onosNode2 ) == str( node2 ):
                    if int( onosPort1 ) == int( port1 ) and int(
                            onosPort2 ) == int( port2 ):
                        firstDir = main.TRUE
                    else:
                        main.log.warn(
                            'The port numbers do not match for ' +
                            str( link ) +
                            ' between ONOS and MN. When cheking ONOS for ' +
                            'link %s/%s -> %s/%s' %
                            ( node1,
                              port1,
                              node2,
                              port2 ) +
                            ' ONOS has the values %s/%s -> %s/%s' %
                            ( onosNode1,
                              onosPort1,
                              onosNode2,
                              onosPort2 ) )

                # check onos link from node2 to node1
                elif ( str( onosNode1 ) == str( node2 ) and
                        str( onosNode2 ) == str( node1 ) ):
                    if ( int( onosPort1 ) == int( port2 )
                            and int( onosPort2 ) == int( port1 ) ):
                        secondDir = main.TRUE
                    else:
                        main.log.warn(
                            'The port numbers do not match for ' +
                            str( link ) +
                            ' between ONOS and MN. When cheking ONOS for ' +
                            'link %s/%s -> %s/%s' %
                            ( node2,
                              port2,
                              node1,
                              port1 ) +
                            ' ONOS has the values %s/%s -> %s/%s' %
                            ( onosNode2,
                              onosPort2,
                              onosNode1,
                              onosPort1 ) )
                else:  # this is not the link you're looking for
                    pass
            if not firstDir:
                main.log.report(
                    'ONOS does not have the link %s/%s -> %s/%s' %
                    ( node1, port1, node2, port2 ) )
            if not secondDir:
                main.log.report(
                    'ONOS does not have the link %s/%s -> %s/%s' %
                    ( node2, port2, node1, port1 ) )
            linkResults = linkResults and firstDir and secondDir
        return linkResults

    def getHosts( self ):
        """
           Returns a list of all hosts
           Don't ask questions just use it"""
        self.handle.sendline( "" )
        self.handle.expect( "mininet>" )

        self.handle.sendline( "py [ host.name for host in net.hosts ]" )
        self.handle.expect( "mininet>" )

        handlePy = self.handle.before
        handlePy = handlePy.split( "]\r\n", 1 )[ 1 ]
        handlePy = handlePy.rstrip()

        self.handle.sendline( "" )
        self.handle.expect( "mininet>" )

        hostStr = handlePy.replace( "]", "" )
        hostStr = hostStr.replace( "'", "" )
        hostStr = hostStr.replace( "[", "" )
        hostList = hostStr.split( "," )

        return hostList

    def update( self ):
        """
           updates the port address and status information for
           each port in mn"""
        # TODO: Add error checking. currently the mininet command has no output
        main.log.info( "Updateing MN port information" )
        try:
            self.handle.sendline( "" )
            self.handle.expect( "mininet>" )

            self.handle.sendline( "update" )
            self.handle.expect( "update" )
            self.handle.expect( "mininet>" )

            self.handle.sendline( "" )
            self.handle.expect( "mininet>" )

            return main.TRUE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()

if __name__ != "__main__":
    import sys
    sys.modules[ __name__ ] = MininetCliDriver()
