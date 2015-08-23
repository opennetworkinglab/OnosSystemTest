#!/usr/bin/env python
"""
Created on 26-Oct-2012

author:: Anil Kumar ( anilkumar.s@paxterrasolutions.com )


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
"""
import pexpect
import re
import sys
import os
from drivers.common.cli.emulatordriver import Emulator


class RemoteMininetDriver( Emulator ):

    """
    RemoteMininetCliDriver is the basic driver which will handle the Mininet
    functions. The main different between this and the MininetCliDriver is that
    this one does not build the mininet. It assumes that there is already a
    mininet running on the target.
    """
    def __init__( self ):
        super( Emulator, self ).__init__()
        self.handle = self
        self.name = None
        self.wrapped = sys.modules[ __name__ ]
        self.flag = 0

    def connect( self, **connectargs ):
        """,user_name, ip_address, pwd,options ):
         Here the main is the TestON instance after creating all the log
         handles."""
        for key in connectargs:
            vars( self )[ key ] = connectargs[ key ]

        self.name = self.options[ 'name' ]

        try:
            if os.getenv( str( self.ip_address ) ) != None:
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
            RemoteMininetDriver,
            self ).connect(
            user_name=self.user_name,
            ip_address=self.ip_address,
            port=None,
            pwd=self.pwd )

        # Copying the readme file to process the
        if self.handle:
            return main.TRUE

        else:
            main.log.error(
                "Connection failed to the host " +
                self.user_name +
                "@" +
                self.ip_address )
            main.log.error( "Failed to connect to the Mininet" )
            return main.FALSE

    def checkForLoss( self, pingList ):
        """
        Returns main.FALSE for 0% packet loss and
        Returns main.ERROR if "found multiple mininet" is found and
        Returns main.TRUE else
        """
        self.handle.sendline( "" )
        self.handle.expect( "\$" )
        self.handle.sendline( "" )
        self.handle.expect( "\$" )
        self.handle.sendline( "cat " + pingList )
        self.handle.expect( pingList )
        self.handle.expect( "\$" )
        outputs = self.handle.before + self.handle.after
        if re.search( " 0% packet loss", outputs ):
            return main.FALSE
        elif re.search( "found multiple mininet", outputs ):
            return main.ERROR
        else:
            # TODO: Parse for failed pings, give some truncated output
            main.log.error( "Error, unexpected output in the ping file" )
            main.log.warn( outputs )
            return main.TRUE

    def pingLong( self, **pingParams ):
        """
        Starts a continuous ping on the mininet host outputting
        to a file in the /tmp dir.
        """
        self.handle.sendline( "" )
        self.handle.expect( "\$" )
        args = utilities.parse_args(
            [ "SRC", "TARGET", "PINGTIME" ], **pingParams )
        precmd = "sudo rm /tmp/ping." + args[ "SRC" ]
        self.execute( cmd=precmd, prompt="(.*)", timeout=10 )
        command = "sudo mininet/util/m " + args[ "SRC" ] + " ping " +\
                  args[ "TARGET" ] + " -i .2 -w " +\
                  str( args[ 'PINGTIME' ] ) + " -D > /tmp/ping." +\
                  args[ "SRC" ] + " &"
        main.log.info( command )
        self.execute( cmd=command, prompt="(.*)", timeout=10 )
        self.handle.sendline( "" )
        self.handle.expect( "\$" )
        return main.TRUE

    def pingstatus( self, **pingParams ):
        """
        Tails the respective ping output file and check that
        there is a moving "64 bytes"
        """
        self.handle.sendline( "" )
        self.handle.expect( "\$" )
        args = utilities.parse_args( [ "SRC" ], **pingParams )
        self.handle.sendline( "tail /tmp/ping." + args[ "SRC" ] )
        self.handle.expect( "tail" )
        self.handle.expect( "\$" )
        result = self.handle.before + self.handle.after
        self.handle.sendline( "" )
        self.handle.expect( "\$" )
        if re.search( 'Unreachable', result ):
            main.log.info( "Unreachable found in ping logs..." )
            return main.FALSE
        elif re.search( '64\sbytes', result ):
            main.log.info( "Pings look good" )
            return main.TRUE
        else:
            main.log.info( "No, or faulty ping data..." )
            return main.FALSE

    def pingKill( self, testONUser, testONIP ):
        """
        Kills all continuous ping processes.
        Then copies all the ping files to the TestStation.
        """
        self.handle.sendline( "" )
        self.handle.expect( "\$" )
        command = "sudo kill -SIGINT `pgrep ping`"
        main.log.info( command )
        self.execute( cmd=command, prompt="(.*)", timeout=10 )

        main.log.info( "Transferring ping files to TestStation" )
        command = "scp /tmp/ping.* " + \
            str( testONUser ) + "@" + str( testONIP ) + ":/tmp/"
        self.execute( cmd=command, prompt="100%", timeout=20 )
        # Make sure the output is cleared
        self.handle.sendline( "" )
        self.handle.expect( "\$" )
        self.handle.sendline( "" )
        self.handle.expect( "\$" )
        self.handle.sendline( "" )
        i = self.handle.expect( [ "password", "\$" ] )
        if i == 0:
            main.log.error( "Error, sudo asking for password" )
            main.log.error( self.handle.before )
            return main.FALSE
        else:
            return main.TRUE

    def pingLongKill( self ):
        self.handle.sendline( "" )
        self.handle.expect( "\$" )
        command = "sudo kill -SIGING `pgrep ping`"
        main.log.info( command )
        self.execute( cmd=command, prompt="(.*)", timeout=10 )
        self.handle.sendline( "" )
        self.handle.expect( "\$" )
        return main.TRUE

    def pingHostOptical( self, **pingParams ):
        """
        This function is only for Packet Optical related ping
        Use the next pingHost() function for all normal scenarios )
        Ping from one mininet host to another
        Currently the only supported Params: SRC and TARGET
        """
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

    def pingHost( self, **pingParams ):
        """
        Pings between two hosts on remote mininet
        """
        self.handle.sendline( "" )
        self.handle.expect( "\$" )
        args = utilities.parse_args( [ "SRC", "TARGET" ], **pingParams )
        command = "mininet/util/m " + \
            args[ "SRC" ] + " ping " + args[ "TARGET" ] + " -c 4 -W 1 -i .2"
        main.log.info( command )
        response = self.execute( cmd=command, prompt="rtt", timeout=10 )
        if utilities.assert_matches(
                expect=',\s0\%\spacket\sloss',
                actual=response,
                onpass="No Packet loss",
                onfail="Host is not reachable" ):
            main.log.info( "NO PACKET LOSS, HOST IS REACHABLE" )
            main.lastResult = main.TRUE
            return main.TRUE
        else:
            main.log.error( "PACKET LOST, HOST IS NOT REACHABLE" )
            main.lastResult = main.FALSE
            return main.FALSE

    def checknum( self, num ):
        """
        Verifies the correct number of switches are running
        """
        if self.handle:
            self.handle.sendline( "" )
            self.handle.expect( "\$" )
            self.handle.sendline( 'ifconfig -a | grep "sw.. " | wc -l' )
            self.handle.expect( "wc" )
            self.handle.expect( "\$" )
            response = self.handle.before
            self.handle.sendline(
                'ps -ef | grep "bash -ms mininet:sw" | grep -v color | wc -l' )
            self.handle.expect( "color" )
            self.handle.expect( "\$" )
            response2 = self.handle.before

            if re.search( num, response ):
                if re.search( num, response2 ):
                    return main.TRUE
                else:
                    return main.FALSE
            else:
                return main.FALSE
        else:
            main.log.error( "Connection failed to the host" )

    def startTcpdump(
            self,
            filename,
            intf="eth0",
            port="port 6653",
            user="admin" ):
        """
        Runs tcpdump on an interface and saves the file
        intf can be specified, or the default eth0 is used
        """
        try:
            self.handle.sendline( "" )
            self.handle.sendline(
                "sudo tcpdump -n -i " +
                intf +
                " " +
                port +
                " -w " +
                filename.strip() +
                " -Z " +
                user +
                "  &" )
            self.handle.sendline( "" )
            self.handle.sendline( "" )
            i = self.handle.expect( [ 'No\ssuch\device', 'listening\son',
                                    pexpect.TIMEOUT, "\$" ], timeout=10 )
            main.log.info( self.handle.before + self.handle.after )
            if i == 0:
                main.log.error( self.name + ": tcpdump - No such device exists.\
                        tcpdump attempted on: " + intf )
                return main.FALSE
            elif i == 1:
                main.log.info( self.name + ": tcpdump started on " + intf )
                return main.TRUE
            elif i == 2:
                main.log.error( self.name + ": tcpdump command timed out!\
                        Check interface name, given interface was: " + intf )
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
            self.handle.sendline( "sudo pkill tcpdump" )
            self.handle.sendline( "" )
            self.handle.expect( "\$" )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def runOpticalMnScript( self,name = 'onos', ctrllerIP = None ):
        import time
        import types
        """
            Description:
                This function is only meant for Packet Optical.
                It runs python script "opticalTest.py" to create the
                packet layer( mn ) and optical topology
            Optional:
                name - Name of onos directory. (ONOS | onos)
            Required:
                ctrllerIP = Controller(s) IP address
            TODO: If no ctrllerIP is provided, a default
                $OC1 can be accepted
        """
        try:
            self.handle.sendline( "" )
            self.handle.expect( "\$" )
            self.handle.sendline( "cd ~/" + name + "/tools/test/topos" )
            self.handle.expect( "topos\$" )
            if ctrllerIP == None:
                main.log.info( "You need to specify the IP" )
                return main.FALSE
            else:
                controller = ''
                if isinstance( ctrllerIP, types.ListType ):
                    for i in xrange( len( ctrllerIP ) ):
                        controller += ctrllerIP[i] + ' '
                    main.log.info( "Mininet topology is being loaded with " +
                                   "controllers: " + controller )
                elif isinstance( ctrllerIP, types.StringType ):
                    controller = ctrllerIP
                    main.log.info( "Mininet topology is being loaded with " +
                                   "controller: " + controller )
                else:
                    main.log.info( "You need to specify a valid IP" )
                    return main.FALSE
                cmd = "sudo -E python opticalTest.py " + controller
                main.log.info( self.name + ": cmd = " + cmd )
                self.handle.sendline( cmd )
                time.sleep(30)
                self.handle.sendline( "" )
                self.handle.sendline( "" )
                self.handle.expect("mininet>")
                return main.TRUE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE

    def attachLincOESession( self ):
        """
            Since executing opticalTest.py will give you mininet
            prompt, you would at some point require to get onto
            console of LincOE ((linc@onosTestBench)1>) to execute
            commands like bring a optical port up or down on a ROADM
            You can attach to console of Linc-OE session by a cmd:
            sudo ~/linc-oe/rel/linc/bin/linc attach
        """
        try:
            self.handle.sendline( "" )
            self.handle.expect( "\$" )
            self.handle.sendline( "sudo ~/linc-oe/rel/linc/bin/linc attach" )
            self.handle.expect( ">" )
            return main.TRUE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE

    def disconnect( self ):
        """
        Called at the end of the test to disconnect the handle.
        """
        if self.handle:
            # Close the ssh connection
            self.handle.sendline( "" )
            # self.handle.expect( "\$" )
            i = self.handle.expect( [ '\$', 'mininet>', pexpect.TIMEOUT,
                                      pexpect.EOF ], timeout=2 )
            if i == 0:
                self.handle.sendline( "exit" )
                self.handle.expect( "closed" )
            elif i == 1:
                self.handle.sendline( "exit" )
                self.handle.expect( "exit" )
                self.handle.expect('\$')
                self.handle.sendline( "exit" )
                self.handle.expect( "exit" )
                self.handle.expect( "closed" )
        else:
            main.log.error( "Connection failed to the host" )
        return main.TRUE

    def setIpTablesOUTPUT( self, dstIp, dstPort, action='add',
                           packetType='tcp', rule='DROP' ):
        """
        Description:
            add or remove iptables rule to DROP ( default )
            packets from specific IP and PORT
        Usage:
        * specify action ( 'add' or 'remove' )
          when removing, pass in the same argument as you would add. It will
          delete that specific rule.
        * specify the destination ip to block with dstIp
        * specify destination port to block to dstPort
        * optional packet type to block ( default tcp )
        * optional iptables rule ( default DROP )
        WARNING:
        * This function uses root privilege iptables command which may result
        in unwanted network errors. USE WITH CAUTION
        """
        import re
        import time

        # NOTE*********
        #   The strict checking methods of this driver function is intentional
        #   to discourage any misuse or error of iptables, which can cause
        #   severe network errors
        # *************

        # NOTE: Sleep needed to give some time
        # for rule to be added and registered
        #      to the instance
        time.sleep( 5 )

        actionType = action.lower()
        if actionType != 'add' and actionType != 'remove':
            main.log.error(
                "Invalid action type. 'add' or 'remove' table rule" )
            if rule != 'DROP' and rule != 'ACCEPT' and rule != 'LOG':
                # NOTE: Currently only supports rules DROP, ACCEPT, and LOG
                main.log.error(
                    "Invalid rule. 'DROP' or 'ACCEPT' or 'LOG' only." )
                return
            return
        else:

            # If there is no existing rule in the iptables, we will see an
            # 'iptables:'... message. We expect to see this message.
            # Otherwise, if there IS an existing rule, we will get the prompt
            # back, hence why we expect $ for remove type. We want to remove
            # an already existing rule

            if actionType == 'add':
                # NOTE: "iptables:" expect is a result of
                # return from the command
                # iptables -C ...
                # Any changes by the iptables command return string
                # will result in failure of the function. ( deemed unlikely
                # at the time of writing this function )
                # Check for existing rules on current input
                self.handle.sendline( "" )
                self.handle.expect( "\$" )
                self.handle.sendline(
                    "sudo iptables -C OUTPUT -p " +
                    str( packetType ) +
                    " -d " +
                    str( dstIp ) +
                    " --dport " +
                    str( dstPort ) +
                    " -j " +
                    str( rule ) )
                i = self.handle.expect( [ "iptables:", "\$" ] )
                print i
                print self.handle.before
                print "after: "
                print self.handle.after

            elif actionType == 'remove':
                # Check for existing rules on current input
                self.handle.sendline( "" )
                self.handle.expect( "\$" )
                self.handle.sendline(
                    "sudo iptables -C OUTPUT -p " +
                    str( packetType ) +
                    " -d " +
                    str( dstIp ) +
                    " --dport " +
                    str( dstPort ) +
                    " -j " +
                    str( rule ) )
                self.handle.expect( "\$" )
            print "before: "
            print self.handle.before
            actualString = self.handle.after
            expectString = "iptables:"
            print "Actual String:"
            print actualString

            if re.search( expectString, actualString ):
                matchResult = main.TRUE
            else:
                matchResult = main.FALSE
            # If matchResult is main.TRUE, it means there is no matching rule.

            # If tables does not exist and expected prompt is returned,
            # go ahead and add iptables rule
            if matchResult == main.TRUE:
                # Ensure action type is add
                if actionType == 'add':
                    # -A is the 'append' action of iptables
                    actionAdd = '-A'
                    try:
                        self.handle.sendline( "" )
                        self.handle.sendline(
                            "sudo iptables " +
                            actionAdd +
                            " OUTPUT -p " +
                            str( packetType ) +
                            " -d " +
                            str( dstIp ) +
                            " --dport " +
                            str( dstPort ) +
                            " -j " +
                            str( rule ) )

                        infoString = "Rules added to " + str( self.name )
                        infoString += "iptables rule added to block IP: " + \
                            str( dstIp )
                        infoString += "Port: " + \
                            str( dstPort ) + " Rule: " + str( rule )

                        main.log.info( infoString )

                        self.handle.expect(
                            [ "\$", pexpect.EOF, pexpect.TIMEOUT ] )
                    except pexpect.TIMEOUT:
                        main.log.error(
                            self.name +
                            ": Timeout exception in setIpTables function" )
                    except Exception:
                        main.log.exception( self.name +
                                            ": Uncaught exception!" )
                        main.cleanup()
                        main.exit()
                else:
                    main.log.error(
                        "Given rule already exists, but attempted to add it" )
            # If matchResult is 0, it means there IS a matching rule provided
            elif matchResult == main.FALSE:
                # Ensure action type is remove
                if actionType == 'remove':
                    # -D is the 'delete' rule of iptables
                    actionRemove = '-D'
                    try:
                        self.handle.sendline( "" )
                        # Delete a specific rule specified into the function
                        self.handle.sendline(
                            "sudo iptables " +
                            actionRemove +
                            " OUTPUT -p " +
                            str( packetType ) +
                            " -d " +
                            str( dstIp ) +
                            " --dport " +
                            str( dstPort ) +
                            " -j " +
                            str( rule ) )

                        infoString = "Rules removed from " + str( self.name )
                        infoString += " iptables rule removed \
                                      from blocking IP: " + \
                                      str( dstIp )
                        infoString += " Port: " + \
                            str( dstPort ) + " Rule: " + str( rule )

                        main.log.info( infoString )

                        self.handle.expect(
                            [ "\$", pexpect.EOF, pexpect.TIMEOUT ] )
                    except pexpect.TIMEOUT:
                        main.log.error(
                            self.name +
                            ": Timeout exception in setIpTables function" )
                    except Exception:
                        main.log.exception( self.name +
                                            ": Uncaught exception!" )
                        main.cleanup()
                        main.exit()
                else:
                    main.log.error(
                        "Given rule does not exist,\
                                but attempted to remove it" )
            else:
                # NOTE: If a bad usage of this function occurs, exit the entire
                # test
                main.log.error( "Bad rule given for iptables. Exiting..." )
                main.cleanup()
                main.exit()


if __name__ != "__main__":
    import sys
    sys.modules[ __name__ ] = RemoteMininetDriver()
