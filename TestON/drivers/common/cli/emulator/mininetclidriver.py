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

Some functions rely on a modified version of Mininet. These functions
should all be noted in the comments. To get this MN version run these commands
from within your Mininet folder:
    git remote add jhall11 https://github.com/jhall11/mininet.git
    git fetch jhall11
    git checkout -b dynamic_topo remotes/jhall11/dynamic_topo
    git pull


    Note that you may need to run 'sudo make develop' if your mnexec.c file
changed when switching branches."""
import pexpect
import re
import sys
import types
import os
from math import pow
from drivers.common.cli.emulatordriver import Emulator


class MininetCliDriver( Emulator ):

    """
       MininetCliDriver is the basic driver which will handle
       the Mininet functions"""
    def __init__( self ):
        super( Emulator, self ).__init__()
        self.handle = self
        self.name = None
        self.home = None
        self.wrapped = sys.modules[ __name__ ]
        self.flag = 0
        # TODO: Refactor driver to use these everywhere
        self.mnPrompt = "mininet>"
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
                MininetCliDriver,
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
                main.log.error( "Failed to connect to the Mininet CLI" )
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

    def startNet( self, topoFile='', args='', mnCmd='', timeout=120 ):
        """
        Description:
            Starts Mininet accepts a topology(.py) file and/or an optional
            argument, to start the mininet, as a parameter.
            Can also send regular mininet command to load up desired topology.
            Eg. Pass in a string 'sudo mn --topo=tree,3,3' to mnCmd
        Options:
            topoFile = file path for topology file (.py)
            args = extra option added when starting the topology from the file
            mnCmd = Mininet command use to start topology
        Returns:
                main.TRUE if the mininet starts successfully, main.FALSE
                otherwise
        """
        if self.handle:
            # make sure old networks are cleaned up
            main.log.info( self.name +
                           ": Clearing any residual state or processes" )
            self.handle.sendline( "sudo mn -c" )
            i = self.handle.expect( [ 'password\sfor\s',
                                      'Cleanup\scomplete',
                                      pexpect.EOF,
                                      pexpect.TIMEOUT ],
                                    timeout )
            if i == 0:
                # Sudo asking for password
                main.log.info( self.name + ": Sending sudo password" )
                self.handle.sendline( self.pwd )
                i = self.handle.expect( [ '%s:' % self.user,
                                          '\$',
                                          pexpect.EOF,
                                          pexpect.TIMEOUT ],
                                        timeout )
            if i == 1:
                main.log.info( self.name + ": Clean" )
            elif i == 2:
                main.log.error( self.name + ": Connection terminated" )
            elif i == 3:  # timeout
                main.log.error( self.name + ": Something while cleaning " +
                                "Mininet took too long... " )
            # Craft the string to start mininet
            cmdString = "sudo "
            if not mnCmd:
                if topoFile is None or topoFile == '':  # If no file is given
                    main.log.info( self.name + ": building fresh Mininet" )
                    cmdString += "mn "
                    if args is None or args == '':
                        # If no args given, use args from .topo file
                        args = self.options[ 'arg1' ] +\
                                " " + self.options[ 'arg2' ] +\
                                " --mac --controller " +\
                                self.options[ 'controller' ] + " " +\
                                self.options[ 'arg3' ]
                    else:  # else only use given args
                        pass
                        # TODO: allow use of topo args and method args?
                else:  # Use given topology file
                    main.log.info(
                        "Starting Mininet from topo file " +
                        topoFile )
                    cmdString += topoFile + " "
                    if args is None:
                        args = ''
                        # TODO: allow use of args from .topo file?
                cmdString += args
            else:
                main.log.info( "Starting Mininet topology using '" + mnCmd +
                               "' command" )
                cmdString += mnCmd
            # Send the command and check if network started
            self.handle.sendline( "" )
            self.handle.expect( '\$' )
            main.log.info( "Sending '" + cmdString + "' to " + self.name )
            self.handle.sendline( cmdString )
            while True:
                i = self.handle.expect( [ 'mininet>',
                                          'Exception',
                                          '\*\*\*',
                                          pexpect.EOF,
                                          pexpect.TIMEOUT ],
                                        timeout )
                if i == 0:
                    main.log.info( self.name + ": Mininet built" )
                    return main.TRUE
                elif i == 1:
                    response = str( self.handle.before +
                                    self.handle.after )
                    self.handle.expect( '\$' )
                    response += str( self.handle.before +
                                     self.handle.after )
                    main.log.error(
                        self.name +
                        ": Launching Mininet failed: " + response )
                    return main.FALSE
                elif i == 2:
                    self.handle.expect( [ "\n",
                                          pexpect.EOF,
                                          pexpect.TIMEOUT ],
                                        timeout )
                    main.log.info( self.handle.before )
                elif i == 3:
                    main.log.error( self.name + ": Connection timeout" )
                    return main.FALSE
                elif i == 4:  # timeout
                    main.log.error(
                        self.name +
                        ": Something took too long... " )
                    return main.FALSE
            # Why did we hit this part?
            main.log.error( "startNet did not return correctly" )
            return main.FASLE
        else:  # if no handle
            main.log.error( self.name + ": Connection failed to the host " +
                            self.user_name + "@" + self.ip_address )
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
        topoDict = { "num_switches": int( numSwitches ),
                     "num_corelinks": int( numLinks ) }
        return topoDict

    def calculateSwAndLinks( self ):
        """
            Calculate the number of switches and links in a topo."""
        # TODO: combine this function and numSwitchesNlinks
        argList = self.options[ 'arg1' ].split( "," )
        topoArgList = argList[ 0 ].split( " " )
        argList = map( int, argList[ 1: ] )
        topoArgList = topoArgList[ 1: ] + argList

        topoDict = self.numSwitchesNlinks( *topoArgList )
        return topoDict

    def pingall( self, protocol="IPv4", timeout=300, shortCircuit=False, acceptableFailed=0 ):
        """
           Verifies the reachability of the hosts using pingall command.
           Optional parameter timeout allows you to specify how long to
           wait for pingall to complete
           Optional:
           timeout( seconds ) - How long to wait before breaking the pingall
           shortCircuit - Break the pingall based on the number of failed hosts
                          ping
           acceptableFailed - Set the number of acceptable failed pings for the
                              function to still return main.TRUE
           Returns:
           main.TRUE if pingall completes with no pings dropped
           otherwise main.FALSE
        """
        import time
        try:
            timeout = int( timeout )
            if self.handle:
                main.log.info(
                    self.name +
                    ": Checking reachabilty to the hosts using pingall" )
                response = ""
                failedPings = 0
                returnValue = main.TRUE
                cmd = "pingall"
                if protocol == "IPv6":
                    cmd = "py net.pingAll6()"
                self.handle.sendline( cmd )
                startTime = time.time()
                while True:
                    i = self.handle.expect( [ "mininet>", "X",
                                              pexpect.EOF,
                                              pexpect.TIMEOUT ],
                                            timeout )
                    if i == 0:
                        main.log.info( self.name + ": pingall finished" )
                        response += self.handle.before
                        break
                    elif i == 1:
                        response += self.handle.before + self.handle.after
                        failedPings = failedPings + 1
                        if failedPings > acceptableFailed:
                            returnValue = main.FALSE
                            if shortCircuit:
                                main.log.error( self.name +
                                                ": Aborting pingall - "
                                                + str( failedPings ) +
                                                " pings failed" )
                                break
                        if ( time.time() - startTime ) > timeout:
                            returnValue = main.FALSE
                            main.log.error( self.name +
                                            ": Aborting pingall - " +
                                            "Function took too long " )
                            break
                    elif i == 2:
                        main.log.error( self.name +
                                        ": EOF exception found" )
                        main.log.error( self.name + ":     " +
                                        self.handle.before )
                        main.cleanup()
                        main.exit()
                    elif i == 3:
                        response += self.handle.before
                        main.log.error( self.name +
                                        ": TIMEOUT exception found" )
                        main.log.error( self.name +
                                        ":     " +
                                        str( response ) )
                        # NOTE: Send ctrl-c to make sure pingall is done
                        self.handle.sendline( "\x03" )
                        self.handle.expect( "Interrupt" )
                        self.handle.expect( "mininet>" )
                        break
                pattern = "Results\:"
                main.log.info( "Pingall output: " + str( response ) )
                if re.search( pattern, response ):
                    main.log.info( self.name + ": Pingall finished with "
                                   + str( failedPings ) + " failed pings" )
                    return returnValue
                else:
                    # NOTE: Send ctrl-c to make sure pingall is done
                    self.handle.sendline( "\x03" )
                    self.handle.expect( "Interrupt" )
                    self.handle.expect( "mininet>" )
                    return main.FALSE
            else:
                main.log.error( self.name + ": Connection failed to the host" )
                main.cleanup()
                main.exit()
        except pexpect.TIMEOUT:
            if response:
                main.log.info( "Pingall output: " + str( response ) )
            main.log.error( self.name + ": pexpect.TIMEOUT found" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
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

    def pingallHosts( self, hostList, wait=1 ):
        """
            Ping all specified IPv4 hosts

            Acceptable hostList:
                - [ 'h1','h2','h3','h4' ]

            Returns main.TRUE if all hosts specified can reach
            each other

            Returns main.FALSE if one or more of hosts specified
            cannot reach each other"""
        wait = int( wait )
        cmd = " ping -c 1 -i 1 -W " + str( wait ) + " "

        try:
            main.log.info( "Testing reachability between specified hosts" )

            isReachable = main.TRUE
            pingResponse = "IPv4 ping across specified hosts\n"
            failedPings = 0
            for host in hostList:
                listIndex = hostList.index( host )
                # List of hosts to ping other than itself
                pingList = hostList[ :listIndex ] + \
                    hostList[ ( listIndex + 1 ): ]

                pingResponse += str(str(host) + " -> ")

                for temp in pingList:
                    # Current host pings all other hosts specified
                    pingCmd = str( host ) + cmd + str( temp )
                    self.handle.sendline( pingCmd )
                    self.handle.expect( "mininet>", timeout=wait + 1 )
                    response = self.handle.before
                    if re.search( ',\s0\%\spacket\sloss', response ):
                        pingResponse += str(" h" + str( temp[1:] ))
                    else:
                        pingResponse += " X"
                        # One of the host to host pair is unreachable
                        isReachable = main.FALSE
                        failedPings += 1
                pingResponse += "\n"
            main.log.info( pingResponse + "Failed pings: " + str(failedPings) )
            return isReachable
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception" )
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

    def pingIpv6Hosts( self, hostList, prefix='1000::', wait=1 ):
        """
        IPv6 ping all hosts in hostList. If no prefix passed this will use
        default prefix of 1000::

        Returns main.TRUE if all hosts specified can reach each other

        Returns main.FALSE if one or more of hosts specified cannot reach each other
        """
        try:
            main.log.info( "Testing reachability between specified IPv6 hosts" )
            isReachable = main.TRUE
            wait = int( wait )
            cmd = " ping6 -c 1 -i 1 -W " + str( wait ) + " "
            pingResponse = "IPv6 Pingall output:\n"
            failedPings = 0
            for host in hostList:
                listIndex = hostList.index( host )
                # List of hosts to ping other than itself
                pingList = hostList[ :listIndex ] + \
                    hostList[ ( listIndex + 1 ): ]

                pingResponse += str(str(host) + " -> ")

                for temp in pingList:
                    # Current host pings all other hosts specified
                    pingCmd = str( host ) + cmd + prefix + str( temp[1:] )
                    self.handle.sendline( pingCmd )
                    self.handle.expect( "mininet>", timeout=wait + 1 )
                    response = self.handle.before
                    if re.search( ',\s0\%\spacket\sloss', response ):
                        pingResponse += str(" h" + str( temp[1:] ))
                    else:
                        pingResponse += " X"
                        # One of the host to host pair is unreachable
                        isReachable = main.FALSE
                        failedPings += 1
                pingResponse += "\n"
            main.log.info( pingResponse + "Failed pings: " + str(failedPings) )
            return isReachable

        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception" )
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

    def pingHost( self, **pingParams ):
        """
        Ping from one mininet host to another
        Currently the only supported Params: SRC, TARGET, and WAIT
        """
        args = utilities.parse_args( [ "SRC", "TARGET", 'WAIT' ], **pingParams )
        wait = args['WAIT']
        wait = int( wait if wait else 1 )
        command = args[ "SRC" ] + " ping " + \
            args[ "TARGET" ] + " -c 1 -i 1 -W " + str( wait ) + " "
        try:
            main.log.info( "Sending: " + command )
            self.handle.sendline( command )
            i = self.handle.expect( [ command, pexpect.TIMEOUT ],
                                    timeout=wait + 1 )
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
            if re.search( ',\s0\%\spacket\sloss', response ):
                main.log.info( self.name + ": no packets lost, host is reachable" )
                return main.TRUE
            else:
                main.log.error(
                    self.name +
                    ": PACKET LOST, HOST IS NOT REACHABLE" )
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

    def ping6pair( self, **pingParams ):
        """
           IPv6 Ping between a pair of mininet hosts
           Currently the only supported Params are: SRC, TARGET, and WAIT
           FLOWLABEL and -I (src interface) will be added later after running some tests.
           Example: main.Mininet1.ping6pair( src="h1", target="1000::2" )
        """
        args = utilities.parse_args( [ "SRC", "TARGET", 'WAIT' ], **pingParams )
        wait = args['WAIT']
        wait = int( wait if wait else 1 )
        command = args[ "SRC" ] + " ping " + \
            args[ "TARGET" ] + " -c 1 -i 1 -W " + str( wait ) + " "
        try:
            main.log.info( "Sending: " + command )
            self.handle.sendline( command )
            i = self.handle.expect( [ command, pexpect.TIMEOUT ],
                                    timeout=wait + 1 )
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
            main.log.info( self.name + ": Ping Response: " + response )
            if re.search( ',\s0\%\spacket\sloss', response ):
                main.log.info( self.name + ": no packets lost, host is reachable" )
                return main.TRUE
            else:
                main.log.error(
                    self.name +
                    ": PACKET LOST, HOST IS NOT REACHABLE" )
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
        # FIXME: Who uses this and what is the purpose? seems very specific
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
                ( which is correct behavior since the interfaces
                haven't moved ).
        """
        if self.handle:
            try:
                # Bring link between oldSw-host down
                cmd = "py net.configLinkStatus('" + oldSw + "'," + "'" + host +\
                      "'," + "'down')"
                print "cmd1= ", cmd
                response = self.execute( cmd=cmd,
                                         prompt="mininet>",
                                         timeout=10 )

                # Determine hostintf and Oldswitchintf
                cmd = "px hintf,sintf = " + host + ".connectionsTo(" + oldSw +\
                      ")[0]"
                print "cmd2= ", cmd
                self.handle.sendline( cmd )
                self.handle.expect( "mininet>" )

                # Determine ip and mac address of the host-oldSw interface
                cmd = "px ipaddr = hintf.IP()"
                print "cmd3= ", cmd
                self.handle.sendline( cmd )
                self.handle.expect( "mininet>" )

                cmd = "px macaddr = hintf.MAC()"
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

                # Set macaddress of the host-newSw interface
                cmd = "px " + host + ".setMAC( mac = macaddr, intf = hintf)"
                print "cmd8 = ", cmd
                self.handle.sendline( cmd )
                self.handle.expect( "mininet>" )

                cmd = "net"
                print "cmd9 = ", cmd
                self.handle.sendline( cmd )
                self.handle.expect( "mininet>" )
                print "output = ", self.handle.before

                # Determine ipaddress of the host-newSw interface
                cmd = host + " ifconfig"
                print "cmd10= ", cmd
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
           Changes the mac address of a gateway host"""
        if self.handle:
            try:
                # h1  arp -s 10.0.1.254 00:00:00:00:11:11
                cmd = host + " arp -s " + GW + " " + macaddr
                self.handle.sendline( cmd )
                self.handle.expect( "mininet>" )
                response = self.handle.before
                main.log.info( "response = " + response )
                main.log.info(
                    "Mac address of gateway " +
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

    def links( self ):
        main.log.info( self.name + ": List network links" )
        try:
            response = self.execute( cmd='links', prompt='mininet>',
                                     timeout=20 )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        return response

    def iperftcpAll(self, hosts, timeout=6):
        '''
        Runs the iperftcp function with a given set of hosts and specified timeout.

        @parm:
            timeout: The defualt timeout is 6 sec to allow enough time for a successful test to complete,
             and short enough to stop an unsuccessful test from quiting and cleaning up mininet.
        '''
        for host1 in hosts:
            for host2 in hosts:
                if host1 != host2:
                    if self.iperftcp(host1, host2, timeout) == main.FALSE:
                        main.log.error(self.name + ": iperftcp test failed for " + host1 + " and " + host2)

    def iperftcp(self, host1="h1", host2="h2", timeout=6):
        '''
        Creates an iperf TCP test between two hosts. Returns main.TRUE if test results
        are valid.

        @parm:
            timeout: The defualt timeout is 6 sec to allow enough time for a successful test to complete,
             and short enough to stop an unsuccessful test from quiting and cleaning up mininet.
        '''
        main.log.info( self.name + ": Simple iperf TCP test between two hosts" )
        try:
            # Setup the mininet command
            cmd1 = 'iperf ' + host1 + " " + host2
            self.handle.sendline( cmd1 )
            outcome = self.handle.expect( "mininet>", timeout )
            response = self.handle.before

            # checks if there are results in the mininet response
            if "Results:" in response:
                main.log.report(self.name + ": iperf test completed")
                # parse the mn results
                response = response.split("\r\n")
                response = response[len(response)-2]
                response = response.split(": ")
                response = response[len(response)-1]
                response = response.replace("[", "")
                response = response.replace("]", "")
                response = response.replace("\'", "")

                # this is the bandwith two and from the two hosts
                bandwidth = response.split(", ")

                # there should be two elements in the bandwidth list
                # ['host1 to host2', 'host2 to host1"]
                if len(bandwidth) == 2:
                    main.log.report(self.name + ": iperf test successful")
                    return main.TRUE
                else:
                    main.log.error(self.name + ": invalid iperf results")
                    return main.FALSE
            else:
                main.log.error( self.name + ": iperf test failed" )
                return main.FALSE
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + " response: " +
                            repr( self.handle.before ) )
            # NOTE: Send ctrl-c to make sure iperf is done
            self.handle.sendline( "\x03" )
            self.handle.expect( "Interrupt" )
            self.handle.expect( "mininet>" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()

    def iperfudpAll(self, hosts, bandwidth="10M"):
        '''
        Runs the iperfudp function with a given set of hosts and specified
        bandwidth

        @param:
            bandwidth: the targeted bandwidth, in megabits ('M')
        '''
        for host1 in hosts:
            for host2 in hosts:
                if host1 != host2:
                    if self.iperfudp(host1, host2, bandwidth) == main.FALSE:
                        main.log.error(self.name + ": iperfudp test failed for " + host1 + " and " + host2)

    def iperfudp( self, bandwidth="10M", host1="h1", host2="h2"):

        '''
        Creates an iperf UDP test with a specific bandwidth.
        Returns true if results are valid.

        @param:
            bandwidth: the targeted bandwidth, in megabits ('M'), to run the test
        '''
        main.log.info(self.name + ": Simple iperf UDP test between two hosts")
        try:
            # setup the mininet command
            cmd = 'iperfudp ' + bandwidth + " " + host1 + " " + host2
            self.handle.sendline(cmd)
            self.handle.expect("mininet>")
            response = self.handle.before

            # check if there are in results in the mininet response
            if "Results:" in response:
                main.log.report(self.name + ": iperfudp test completed")
                # parse the results
                response = response.split("\r\n")
                response = response[len(response)-2]
                response = response.split(": ")
                response = response[len(response)-1]
                response = response.replace("[", "")
                response = response.replace("]", "")
                response = response.replace("\'", "")

                mnBandwidth = response.split(", ")

                # check to see if there are at least three entries
                # ['bandwidth', 'host1 to host2', 'host2 to host1']
                if len(mnBandwidth) == 3:
                    # if one entry is blank then something is wrong
                    for item in mnBandwidth:
                        if item == "":
                            main.log.error(self.name + ": Could not parse iperf output")
                            main.log.error(self.name + ": invalid iperfudp results")
                            return main.FALSE
                    # otherwise results are vaild
                    main.log.report(self.name + ": iperfudp test successful")
                    return main.TRUE
                else:
                    main.log.error(self.name + ": invalid iperfudp results")
                    return main.FALSE

        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()

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
            return main.TRUE
        else:
            main.log.error( self.name + ": PACKET LOST, HOSTS NOT REACHABLE" )
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

    def switch( self, **switchargs ):
        """
           start/stop a switch
        """
        args = utilities.parse_args( [ "SW", "OPTION" ], **switchargs )
        sw = args[ "SW" ] if args[ "SW" ] is not None else ""
        option = args[ "OPTION" ] if args[ "OPTION" ] is not None else ""
        command = "switch " + str( sw ) + " " + str( option )
        main.log.info( command )
        try:
            self.handle.sendline( command )
            self.handle.expect( "mininet>" )
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": pexpect.TIMEOUT found" )
            main.cleanup()
            main.exit()
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        return main.TRUE

    def node( self, nodeName, commandStr ):
        """
        Carry out a command line on a given node
        @parm:
            nodeName: the node name in Mininet testbed
            commandStr: the command line will be carried out on the node
        Example: main.Mininet.node( nodeName="h1", commandStr="ls" )
        """
        command = str( nodeName ) + " " + str( commandStr )
        main.log.info( command )

        try:
            response = self.execute( cmd = command, prompt = "mininet>" )
            if re.search( "Unknown command", response ):
                main.log.warn( response )
                return main.FALSE
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": pexpect.TIMEOUT found" )
            main.cleanup()
            main.exit()
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        main.log.info( " response is :" )
        main.log.info( response )
        return response

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
        # FIXME: What uses this? This should be refactored to get
        #       version from MN and not some other file
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

    def assignSwController( self, sw, ip, port="6653", ptcp="" ):
        """
        Description:
            Assign switches to the controllers ( for ovs use only )
        Required:
            sw - Name of the switch. This can be a list or a string.
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
            Returns main.TRUE if mininet correctly assigned switches to
            controllers, otherwise it will return main.FALSE or an appropriate
            exception(s)
        """
        assignResult = main.TRUE
        # Initial ovs command
        commandList = []
        command = "sh ovs-vsctl set-controller "
        onosIp = ""
        try:
            if isinstance( ip, types.StringType ):
                onosIp = "tcp:" + str( ip ) + ":"
                if isinstance( port, types.StringType ) or \
                   isinstance( port, types.IntType ):
                    onosIp += str( port )
                elif isinstance( port, types.ListType ):
                    main.log.error( self.name + ": Only one controller " +
                                    "assigned and a list of ports has" +
                                    " been passed" )
                    return main.FALSE
                else:
                    main.log.error( self.name + ": Invalid controller port " +
                                    "number. Please specify correct " +
                                    "controller port" )
                    return main.FALSE

            elif isinstance( ip, types.ListType ):
                if isinstance( port, types.StringType ) or \
                   isinstance( port, types.IntType ):
                    for ipAddress in ip:
                        onosIp += "tcp:" + str( ipAddress ) + ":" + \
                                  str( port ) + " "
                elif isinstance( port, types.ListType ):
                    if ( len( ip ) != len( port ) ):
                        main.log.error( self.name + ": Port list = " +
                                        str( len( port ) ) +
                                        "should be the same as controller" +
                                        " ip list = " + str( len( ip ) ) )
                        return main.FALSE
                    else:
                        onosIp = ""
                        for ipAddress, portNum in zip( ip, port ):
                            onosIp += "tcp:" + str( ipAddress ) + ":" + \
                                      str( portNum ) + " "
                else:
                    main.log.error( self.name + ": Invalid controller port " +
                                    "number. Please specify correct " +
                                    "controller port" )
                    return main.FALSE
            else:
                main.log.error( self.name + ": Invalid ip address" )
                return main.FALSE

            if isinstance( sw, types.StringType ):
                command += sw + " "
                if ptcp:
                    if isinstance( ptcp, types.StringType ):
                        command += "ptcp:" + str( ptcp ) + " "
                    elif isinstance( ptcp, types.ListType ):
                        main.log.error( self.name + ": Only one switch is " +
                                        "being set and multiple PTCP is " +
                                        "being passed " )
                    else:
                        main.log.error( self.name + ": Invalid PTCP" )
                        ptcp = ""
                command += onosIp
                commandList.append( command )

            elif isinstance( sw, types.ListType ):
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
                            for switch, ptcpNum in zip( sw, ptcp ):
                                tempCmd = "sh ovs-vsctl set-controller "
                                tempCmd += switch + " ptcp:" + \
                                    str( ptcpNum ) + " "
                                tempCmd += onosIp
                                commandList.append( tempCmd )
                    else:
                        main.log.error( self.name + ": Invalid PTCP" )
                        return main.FALSE
                else:
                    for switch in sw:
                        tempCmd = "sh ovs-vsctl set-controller "
                        tempCmd += switch + " " + onosIp
                        commandList.append( tempCmd )
            else:
                main.log.error( self.name + ": Invalid switch type " )
                return main.FALSE

            for cmd in commandList:
                try:
                    self.execute( cmd=cmd, prompt="mininet>", timeout=5 )
                except pexpect.TIMEOUT:
                    main.log.error( self.name + ": pexpect.TIMEOUT found" )
                    return main.FALSE
                except pexpect.EOF:
                    main.log.error( self.name + ": EOF exception found" )
                    main.log.error( self.name + ":     " + self.handle.before )
                    main.cleanup()
                    main.exit()
            return main.TRUE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
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
            sw = name of the new switch as a string
        optional keywords:
            dpid = "dpid"
        returns: main.FALSE on an error, else main.TRUE
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
            sw = name of the switch as a string
        returns: main.FALSE on an error, else main.TRUE"""
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
           returns: main.FALSE on an error, else main.TRUE"""
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
           returns: main.FALSE on an error, else main.TRUE"""
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
            returns: main.FALSE on an error, else main.TRUE
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
           returns: main.FALSE on an error, else main.TRUE"""
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

        Will cleanup and exit the test if mininet fails to stop
        """
        main.log.info( self.name + ": Stopping mininet..." )
        response = ''
        if self.handle:
            try:
                self.handle.sendline( "" )
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
                main.log.info( self.name + ": Stopped" )
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

    def arping( self, srcHost="", dstHost="10.128.20.211", ethDevice="" ):
        """
        Description:
            Sends arp message from mininet host for hosts discovery
        Required:
            host - hosts name
        Optional:
            ip - ip address that does not exist in the network so there would
                 be no reply.
        """
        if ethDevice:
            ethDevice = '-I ' + ethDevice + ' '
        cmd = srcHost + " arping -c1 " + ethDevice + dstHost
        try:
            main.log.info( "Sending: " + cmd )
            self.handle.sendline( cmd )
            i = self.handle.expect( [ "mininet>", "arping: " ] )
            if i == 0:
                return main.TRUE
            elif i == 1:
                response = self.handle.before + self.handle.after
                self.handle.expect( "mininet>" )
                response += self.handle.before + self.handle.after
                main.log.warn( "Error sending arping, output was: " +
                                response )
                return main.FALSE
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": TIMEOUT exception found" )
            main.log.warn( self.handle.before )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()

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

    def flowComp( self, flow1, flow2 ):
        if flow1 == flow2:
            return main.TRUE
        else:
            main.log.info( "Flow tables do not match, printing tables:" )
            main.log.info( "Flow Table 1:" )
            main.log.info( flow1 )
            main.log.info( "Flow Table 2:" )
            main.log.info( flow2 )
            return main.FALSE

    def parseFlowTable( self, flows, debug=True ):
        '''
        Discription: Parses flows into json format.
        NOTE: this can parse any string thats separated with commas
        Arguments:
            Required:
                flows: a list of strings that represnt flows
            Optional:
                version: The version of OpenFlow. Currently, 1.3 and 1.0 are supported.
                debug: prints out the final result
        returns: A list of flows in json format
        '''
        # Parse the flows
        jsonFlows = []
        for flow in flows:
            # split on the comma
            flow = flow.split(",")
            # get rid of empty elements
            flow = [f for f in flow if f != ""]
            jsonFlow = {}
            for f in flow:
                # separate the key and the value
                if "=" in f:
                    f = f.split("=")
                    key = f[0]
                    # get rid of unwanted spaces
                    if key[0] == " ": key = key[1:]
                    val = f[1]
                    jsonFlow.update( {key:val} )
            jsonFlows.append( jsonFlow )

        if debug: print "jsonFlows:\n{}\n\n".format(jsonFlows)

        return jsonFlows

    def getFlowTable( self, sw, version="1.3", debug=True):
        '''
        Discription: Returns the flow table(s) on a switch or switches in a list.
            Each element is a flow.
        Arguments:
            Required:
                sw: The switch name ("s1") to retrive the flow table. Can also be
                    a list of switches.
            Optional:
                version: The version of OpenFlow. Currently, 1.3 and 1.0 are supported.
                debug: prints out the final result
        '''
        try:
            switches = []
            if type(sw) is list:
                switches.extend(sw)
            else: switches.append(sw)

            flows = []
            for s in switches:
                cmd = "sh ovs-ofctl dump-flows " + s

                if "1.3" in version:
                    cmd += " -O OpenFlow13"
                else: cmd += " -F OpenFlow10-table_id"

                main.log.info( "Sending: " + cmd )
                self.handle.sendline( cmd )
                self.handle.expect( "mininet>" )
                response = self.handle.before
                response = response.split( "\r\n" )
                # dump the first two elements and the last
                # the first element is the command that was sent
                # the second is the table header
                # the last element is empty
                response = response[2:-1]
                flows.extend( response )

            if debug: print "Flows:\n{}\n\n".format(flows)

            return self.parseFlowTable( flows, debug )

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

    def checkFlowId( self, sw, flowId, version="1.3", debug=True ):
        '''
        Discription: Checks whether the ID provided matches a flow ID in Mininet
        Arguments:
            Required:
                sw: The switch name ("s1") to retrive the flow table. Can also be
                    a list of switches.
                flowId: the flow ID in hex format. Can also be a list of IDs
            Optional:
                version: The version of OpenFlow. Currently, 1.3 and 1.0 are supported.
                debug: prints out the final result
        returns: main.TRUE if all IDs are present, otherwise returns main.FALSE
        NOTE: prints out IDs that are not present
        '''
        try:
            main.log.info( "Getting flows from Mininet" )
            flows = self.getFlowTable( sw, version, debug )

            if debug: print "flow ids:\n{}\n\n".format(flowId)

            # Check flowId is a list or a string
            if type( flowId ) is str:
                result = False
                for f in flows:
                    if flowId in f.get( 'cookie' ):
                        result = True
                        break
            # flowId is a list
            else:
                result = True
                # Get flow IDs from Mininet
                mnFlowIds = [ f.get( 'cookie' ) for f in flows ]
                # Save the IDs that are not in Mininet
                absentIds = [ x for x in flowId if x not in mnFlowIds ]

                if debug: print "mn flow ids:\n{}\n\n".format(mnFlowIds)

                # Print out the IDs that are not in Mininet
                if absentIds:
                    main.log.warn( "Absent ids: {}".format( absentIds ) )
                    result = False

            return main.TRUE if result else main.FALSE

        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()


    def startTcpdump( self, filename, intf="eth0", port="port 6653" ):
        """
           Runs tpdump on an interface and saves the file
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
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def stopTcpdump( self ):
        """
            pkills tcpdump"""
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
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def getPorts( self, nodeName, verbose=False ):
        """
        Read ports from a Mininet switch.

        Returns a json structure containing information about the
        ports of the given switch.
        """
        response = self.getInterfaces( nodeName )
        # TODO: Sanity check on response. log if no such switch exists
        ports = []
        for line in response.split( "\n" ):
            if not line.startswith( "name=" ):
                continue
            portVars = {}
            for var in line.split( "," ):
                key, value = var.split( "=" )
                portVars[ key ] = value
            isUp = portVars.pop( 'enabled', "True" )
            isUp = "True" in isUp
            if verbose:
                main.log.info( "Reading switch port %s(%s)" %
                               ( portVars[ 'name' ], portVars[ 'mac' ] ) )
            mac = portVars[ 'mac' ]
            if mac == 'None':
                mac = None
            ips = []
            ip = portVars[ 'ip' ]
            if ip == 'None':
                ip = None
            ips.append( ip )
            name = portVars[ 'name' ]
            if name == 'None':
                name = None
            portRe = r'[^\-]\d\-eth(?P<port>\d+)'
            if name == 'lo':
                portNo = 0xfffe  # TODO: 1.0 value - Should we just return lo?
            else:
                portNo = re.search( portRe, name ).group( 'port' )
            ports.append( { 'of_port': portNo,
                            'mac': str( mac ).replace( '\'', '' ),
                            'name': name,
                            'ips': ips,
                            'enabled': isUp } )
        return ports

    def getSwitches( self, verbose=False ):
        """
        Read switches from Mininet.

        Returns a dictionary whose keys are the switch names and the value is
        a dictionary containing information about the switch.
        """
        # NOTE: To support new Mininet switch classes, just append the new
        # class to the switchClasses variable

        # Regex patterns to parse 'dump' output
        # Example Switches:
        # <OVSSwitch s1: lo:127.0.0.1,s1-eth1:None,s1-eth2:None,s1-eth3:None pid=5238>
        # <OVSSwitch{ 'protocols': 'OpenFlow10' } s1: lo:127.0.0.1,s1-eth1:None,s1-eth2:None pid=25974>
        # <OVSSwitchNS s1: lo:127.0.0.1,s1-eth1:None,s1-eth2:None,s1-eth3:None pid=22550>
        # <OVSBridge s1: lo:127.0.0.1,s1-eth1:None,s1-eth2:None pid=26830>
        # <UserSwitch s1: lo:127.0.0.1,s1-eth1:None,s1-eth2:None pid=14737>
        switchClasses = r"(OVSSwitch)|(OVSBridge)|(OVSSwitchNS)|(IVSSwitch)|(LinuxBridge)|(UserSwitch)"
        swRE = r"<(?P<class>" + switchClasses + r")" +\
               r"(?P<options>\{.*\})?\s" +\
               r"(?P<name>[^:]+)\:\s" +\
               r"(?P<ports>([^,]+,)*[^,\s]+)" +\
               r"\spid=(?P<pid>(\d)+)"
        # Update mn port info
        self.update()
        output = {}
        dump = self.dump().split( "\n" )
        for line in dump:
            result = re.search( swRE, line, re.I )
            if result:
                name = result.group( 'name' )
                dpid = str( self.getSwitchDPID( name ) ).zfill( 16 )
                pid = result.group( 'pid' )
                swClass = result.group( 'class' )
                options = result.group( 'options' )
                if verbose:
                    main.log.info( "Reading switch %s(%s)" % ( name, dpid ) )
                ports = self.getPorts( name )
                output[ name ] = { "dpid": dpid,
                                   "ports": ports,
                                   "swClass": swClass,
                                   "pid": pid,
                                   "options": options }
        return output

    def getHosts( self, verbose=False ):
        """
        Read hosts from Mininet.

        Returns a dictionary whose keys are the host names and the value is
        a dictionary containing information about the host.
        """
        # Regex patterns to parse dump output
        # Example host: <Host h1: h1-eth0:10.0.0.1 pid=5227>
        #               <Host h1:  pid=12725>
        #               <VLANHost h12: h12-eth0.100.100.100:100.1.0.3 pid=30186>
        #               <dualStackHost h19: h19-eth0:10.1.0.9 pid=30200>
        #               <IPv6Host h18: h18-eth0:10.0.0.18 pid=30198>
        # NOTE: Does not correctly match hosts with multi-links
        #       <Host h2: h2-eth0:10.0.0.2,h2-eth1:10.0.1.2 pid=14386>
        # FIXME: Fix that
        hostRE = r"Host\s(?P<name>[^:]+)\:((\s(?P<ifname>[^:]+)\:" +\
            "(?P<ip>[^\s]+))|(\s)\spid=(?P<pid>[^>]+))"
        # update mn port info
        self.update()
        # Get mininet dump
        dump = self.dump().split( "\n" )
        hosts = {}
        for line in dump:
            if "Host" in line :
                result = re.search( hostRE, line )
                name = result.group( 'name' )
                interfaces = []
                response = self.getInterfaces( name )
                # Populate interface info
                for line in response.split( "\n" ):
                    if line.startswith( "name=" ):
                        portVars = {}
                        for var in line.split( "," ):
                            key, value = var.split( "=" )
                            portVars[ key ] = value
                        isUp = portVars.pop( 'enabled', "True" )
                        isUp = "True" in isUp
                        if verbose:
                            main.log.info( "Reading host port %s(%s)" %
                                           ( portVars[ 'name' ],
                                             portVars[ 'mac' ] ) )
                        mac = portVars[ 'mac' ]
                        if mac == 'None':
                            mac = None
                        ips = []
                        ip = portVars[ 'ip' ]
                        if ip == 'None':
                            ip = None
                        ips.append( ip )
                        intfName = portVars[ 'name' ]
                        if name == 'None':
                            name = None
                        interfaces.append( {
                            "name": intfName,
                            "ips": ips,
                            "mac": str( mac ),
                            "isUp": isUp } )
                hosts[ name ] = { "interfaces": interfaces }
        return hosts

    def getLinks( self ):
        """
        Gathers information about current Mininet links. These links may not
        be up if one of the ports is down.

        Returns a list of dictionaries with link endpoints.

        The dictionary structure is:
            { 'node1': str( node1 name )
              'node2': str( node2 name )
              'port1': str( port1 of_port )
              'port2': str( port2 of_port ) }
        Note: The port number returned is the eth#, not necessarily the of_port
              number. In Mininet, for OVS switch, these should be the same. For
              hosts, this is just the eth#.
        """
        self.update()
        response = self.links().split( '\n' )

        # Examples:
        # s1-eth3<->s2-eth1 (OK OK)
        # s13-eth3<->h27-eth0 (OK OK)
        linkRE = "(?P<node1>[\w]+)\-eth(?P<port1>[\d]+)\<\-\>" +\
                 "(?P<node2>[\w]+)\-eth(?P<port2>[\d]+)"
        links = []
        for line in response:
            match = re.search( linkRE, line )
            if match:
                node1 = match.group( 'node1' )
                node2 = match.group( 'node2' )
                port1 = match.group( 'port1' )
                port2 = match.group( 'port2' )
                links.append( { 'node1': node1,
                                'node2': node2,
                                'port1': port1,
                                'port2': port2 } )
        return links

    def compareSwitches( self, switches, switchesJson, portsJson ):
        """
           Compare mn and onos switches
           switchesJson: parsed json object from the onos devices api

        Dependencies:
            1. numpy - "sudo pip install numpy"
        """
        from numpy import uint64
        # created sorted list of dpid's in MN and ONOS for comparison
        mnDPIDs = []
        for swName, switch in switches.iteritems():
            mnDPIDs.append( switch[ 'dpid' ].lower() )
        mnDPIDs.sort()
        if switchesJson == "":  # if rest call fails
            main.log.error(
                self.name +
                ".compareSwitches(): Empty JSON object given from ONOS" )
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
        onosDPIDs.sort()

        if mnDPIDs != onosDPIDs:
            switchResults = main.FALSE
            main.log.error( "Switches in MN but not in ONOS:" )
            list1 = [ switch for switch in mnDPIDs if switch not in onosDPIDs ]
            main.log.error( str( list1 ) )
            main.log.error( "Switches in ONOS but not in MN:" )
            list2 = [ switch for switch in onosDPIDs if switch not in mnDPIDs ]
            main.log.error( str( list2 ) )
        else:  # list of dpid's match in onos and mn
            switchResults = main.TRUE
        finalResults = switchResults

        # FIXME: this does not look for extra ports in ONOS, only checks that
        # ONOS has what is in MN
        portsResults = main.TRUE

        # PORTS
        for name, mnSwitch in switches.iteritems():
            mnPorts = []
            onosPorts = []
            switchResult = main.TRUE
            for port in mnSwitch[ 'ports' ]:
                if port[ 'enabled' ]:
                    mnPorts.append( int( port[ 'of_port' ] ) )
            for onosSwitch in portsJson:
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
                main.log.error(
                    "The list of ports for switch %s(%s) does not match:" %
                    ( name, mnSwitch[ 'dpid' ] ) )
                main.log.warn( "mn_ports[]  =  " + str( mnPortsLog ) )
                main.log.warn( "onos_ports[] = " + str( onosPortsLog ) )
            portsResults = portsResults and switchResult
        finalResults = finalResults and portsResults
        return finalResults

    def compareLinks( self, switches, links, linksJson ):
        """
           Compare mn and onos links
           linksJson: parsed json object from the onos links api

        """
        # FIXME: this does not look for extra links in ONOS, only checks that
        #        ONOS has what is in MN
        onos = linksJson

        mnLinks = []
        for l in links:
            try:
                node1 = switches[ l[ 'node1' ] ]
                node2 = switches[ l[ 'node2' ] ]
                enabled = True
                for port in node1[ 'ports' ]:
                    if port[ 'of_port' ] == l[ 'port1' ]:
                        enabled = enabled and port[ 'enabled' ]
                for port in node2[ 'ports' ]:
                    if port[ 'of_port' ] == l[ 'port2' ]:
                        enabled = enabled and port[ 'enabled' ]
                if enabled:
                    mnLinks.append( l )
            except KeyError:
                pass
        if 2 * len( mnLinks ) == len( onos ):
            linkResults = main.TRUE
        else:
            linkResults = main.FALSE
            main.log.error(
                "Mininet has " + str( len( mnLinks ) ) +
                " bidirectional links and ONOS has " +
                str( len( onos ) ) + " unidirectional links" )

        # iterate through MN links and check if an ONOS link exists in
        # both directions
        for link in mnLinks:
            # TODO: Find a more efficient search method
            node1 = None
            port1 = None
            node2 = None
            port2 = None
            firstDir = main.FALSE
            secondDir = main.FALSE
            for swName, switch in switches.iteritems():
                if swName == link[ 'node1' ]:
                    node1 = switch[ 'dpid' ]
                    for port in switch[ 'ports' ]:
                        if str( port[ 'of_port' ] ) == str( link[ 'port1' ] ):
                            port1 = port[ 'of_port' ]
                    if node1 is not None and node2 is not None:
                        break
                if swName == link[ 'node2' ]:
                    node2 = switch[ 'dpid' ]
                    for port in switch[ 'ports' ]:
                        if str( port[ 'of_port' ] ) == str( link[ 'port2' ] ):
                            port2 = port[ 'of_port' ]
                    if node1 is not None and node2 is not None:
                        break

            for onosLink in onos:
                onosNode1 = onosLink[ 'src' ][ 'device' ].replace(
                    ":", '' ).replace( "of", '' )
                onosNode2 = onosLink[ 'dst' ][ 'device' ].replace(
                    ":", '' ).replace( "of", '' )
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
                            ' between ONOS and MN. When checking ONOS for ' +
                            'link %s/%s -> %s/%s' %
                            ( node1, port1, node2, port2 ) +
                            ' ONOS has the values %s/%s -> %s/%s' %
                            ( onosNode1, onosPort1, onosNode2, onosPort2 ) )

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
                            ' between ONOS and MN. When checking ONOS for ' +
                            'link %s/%s -> %s/%s' %
                            ( node1, port1, node2, port2 ) +
                            ' ONOS has the values %s/%s -> %s/%s' %
                            ( onosNode2, onosPort2, onosNode1, onosPort1 ) )
                else:  # this is not the link you're looking for
                    pass
            if not firstDir:
                main.log.error(
                    'ONOS does not have the link %s/%s -> %s/%s' %
                    ( node1, port1, node2, port2 ) )
            if not secondDir:
                main.log.error(
                    'ONOS does not have the link %s/%s -> %s/%s' %
                    ( node2, port2, node1, port1 ) )
            linkResults = linkResults and firstDir and secondDir
        return linkResults

    def compareHosts( self, hosts, hostsJson ):
        """
        Compare mn and onos Hosts.
        Since Mininet hosts are quiet, ONOS will only know of them when they
        speak. For this reason, we will only check that the hosts in ONOS
        stores are in Mininet, and not vice versa.

        Arguments:
            hostsJson: parsed json object from the onos hosts api
        Returns:
        """
        import json
        hostResults = main.TRUE
        for onosHost in hostsJson:
            onosMAC = onosHost[ 'mac' ].lower()
            match = False
            for mnHost, info in hosts.iteritems():
                for mnIntf in info[ 'interfaces' ]:
                    if onosMAC == mnIntf[ 'mac' ].lower():
                        match = True
                        for ip in mnIntf[ 'ips' ]:
                            if ip in onosHost[ 'ipAddresses' ]:
                                pass  # all is well
                            else:
                                # misssing ip
                                main.log.error( "ONOS host " +
                                                onosHost[ 'id' ] +
                                                " has a different IP(" +
                                                str( onosHost[ 'ipAddresses' ] ) +
                                                ") than the Mininet host(" +
                                                str( ip ) +
                                                ")." )
                                output = json.dumps(
                                    onosHost,
                                    sort_keys=True,
                                    indent=4,
                                    separators=( ',', ': ' ) )
                                main.log.info( output )
                                hostResults = main.FALSE
            if not match:
                hostResults = main.FALSE
                main.log.error( "ONOS host " + onosHost[ 'id' ] + " has no " +
                                "corresponding Mininet host." )
                output = json.dumps( onosHost,
                                     sort_keys=True,
                                     indent=4,
                                     separators=( ',', ': ' ) )
                main.log.info( output )
        return hostResults

    def getHostsOld( self ):
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
        hostStr = hostStr.replace( " ", "" )
        hostList = hostStr.split( "," )

        return hostList

    def getSwitch( self ):
        """
            Returns a list of all switches
            Again, don't ask question just use it...
        """
        # get host list...
        hostList = self.getHosts()
        # Make host set
        hostSet = set( hostList )

        # Getting all the nodes in mininet
        self.handle.sendline( "" )
        self.handle.expect( "mininet>" )

        self.handle.sendline( "py [ node.name for node in net.values() ]" )
        self.handle.expect( "mininet>" )

        handlePy = self.handle.before
        handlePy = handlePy.split( "]\r\n", 1 )[ 1 ]
        handlePy = handlePy.rstrip()

        self.handle.sendline( "" )
        self.handle.expect( "mininet>" )

        nodesStr = handlePy.replace( "]", "" )
        nodesStr = nodesStr.replace( "'", "" )
        nodesStr = nodesStr.replace( "[", "" )
        nodesStr = nodesStr.replace( " ", "" )
        nodesList = nodesStr.split( "," )

        nodesSet = set( nodesList )
        # discarding default controller(s) node
        nodesSet.discard( 'c0' )
        nodesSet.discard( 'c1' )
        nodesSet.discard( 'c2' )

        switchSet = nodesSet - hostSet
        switchList = list( switchSet )

        return switchList

    def update( self ):
        """
           updates the port address and status information for
           each port in mn"""
        # TODO: Add error checking. currently the mininet command has no output
        main.log.info( "Updating MN port information" )
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

    def assignVLAN( self, host, intf, vlan ):
        """
           Add vlan tag to a host.
           Dependencies:
               This class depends on the "vlan" package
               $ sudo apt-get install vlan
           Configuration:
               Load the 8021q module into the kernel
               $sudo modprobe 8021q

               To make this setup permanent:
               $ sudo su -c 'echo "8021q" >> /etc/modules'
           """
        if self.handle:
            try:
                # get the ip address of the host
                main.log.info( "Get the ip address of the host" )
                ipaddr = self.getIPAddress( host )
                print repr( ipaddr )

                # remove IP from interface intf
                # Ex: h1 ifconfig h1-eth0 inet 0
                main.log.info( "Remove IP from interface " )
                cmd2 = host + " ifconfig " + intf + " " + " inet 0 "
                self.handle.sendline( cmd2 )
                self.handle.expect( "mininet>" )
                response = self.handle.before
                main.log.info( "====> %s ", response )

                # create VLAN interface
                # Ex: h1 vconfig add h1-eth0 100
                main.log.info( "Create Vlan" )
                cmd3 = host + " vconfig add " + intf + " " + vlan
                self.handle.sendline( cmd3 )
                self.handle.expect( "mininet>" )
                response = self.handle.before
                main.log.info( "====> %s ", response )

                # assign the host's IP to the VLAN interface
                # Ex: h1 ifconfig h1-eth0.100 inet 10.0.0.1
                main.log.info( "Assign the host IP to the vlan interface" )
                vintf = intf + "." + vlan
                cmd4 = host + " ifconfig " + vintf + " " + " inet " + ipaddr
                self.handle.sendline( cmd4 )
                self.handle.expect( "mininet>" )
                response = self.handle.before
                main.log.info( "====> %s ", response )

                return main.TRUE
            except pexpect.EOF:
                main.log.error( self.name + ": EOF exception found" )
                main.log.error( self.name + ":     " + self.handle.before )
                return main.FALSE

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
            # FIXME: Should we exit here?
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
            return
        try:
            # Disconnect from component
            component.disconnect()
            # Delete component
            delattr( main, name )
            # Delete component from ComponentDictionary
            del( main.componentDictionary[name] )
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

    def checkFilter( self ):
        """
        Check that a filter returned and returns the reponse
        """
        try:
            i = self.handle.expect( [ self.scapyPrompt, pexpect.TIMEOUT ] )
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
        """
        try:
            ifaceName = ifaceName if ifaceName else self.name + "-eth0"
            cmd = 'get_if_addr("' + str( ifaceName ) + '")'
            self.handle.sendline( cmd )
            self.handle.expect( self.scapyPrompt )

            pattern = r'(((2[0-5]|1[0-9]|[0-9])?[0-9]\.){3}((2[0-5]|1[0-9]|[0-9])?[0-9]))'
            match = re.search( pattern, self.handle.before )
            if match:
                # NOTE: The command will return 0.0.0.0 if the iface doesn't exist
                return match.group()
            else:
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

if __name__ != "__main__":
    sys.modules[ __name__ ] = MininetCliDriver()
