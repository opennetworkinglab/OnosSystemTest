#!/usr/bin/env python

"""
OCT 13 2014
Copyright 2014 Open Networking Foundation (ONF)

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

"""
This driver enters the onos> prompt to issue commands.

Please follow the coding style demonstrated by existing
functions and document properly.

If you are a contributor to the driver, please
list your email here for future contact:

jhall@onlab.us
andrew@onlab.us
shreya@onlab.us
jeremyr@opennetworking.org
"""
import pexpect
import re
import json
import types
import time
import os
from drivers.common.clidriver import CLI
from core.graph import Graph
from cStringIO import StringIO
from itertools import izip

class OnosCliDriver( CLI ):

    def __init__( self ):
        """
        Initialize client
        """
        self.name = None
        self.home = None
        self.handle = None
        self.karafUser = None
        self.karafPass = None
        self.graph = Graph()
        super( OnosCliDriver, self ).__init__()

    def checkOptions( self, var, defaultVar ):
        if var is None or var == "":
            return defaultVar
        return var

    def connect( self, **connectargs ):
        """
        Creates ssh handle for ONOS cli.
        """
        try:
            for key in connectargs:
                vars( self )[ key ] = connectargs[ key ]
            self.home = "~/onos"
            for key in self.options:
                if key == "home":
                    self.home = self.options[ key ]
                elif key == "karaf_username":
                    self.karafUser = self.options[ key ]
                elif key == "karaf_password":
                    self.karafPass = self.options[ key ]

            self.home = self.checkOptions( self.home, "~/onos" )
            self.karafUser = self.checkOptions( self.karafUser, self.user_name )
            self.karafPass = self.checkOptions( self.karafPass, self.pwd )

            for key in self.options:
                if key == 'onosIp':
                    self.onosIp = self.options[ 'onosIp' ]
                    break

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

            self.handle = super( OnosCliDriver, self ).connect(
                user_name=self.user_name,
                ip_address=self.ip_address,
                port=self.port,
                pwd=self.pwd,
                home=self.home )

            self.handle.sendline( "cd " + self.home )
            self.handle.expect( self.prompt )
            if self.handle:
                return self.handle
            else:
                main.log.info( "NO ONOS HANDLE" )
                return main.FALSE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def disconnect( self ):
        """
        Called when Test is complete to disconnect the ONOS handle.
        """
        response = main.TRUE
        try:
            if self.handle:
                i = self.logout()
                if i == main.TRUE:
                    self.handle.sendline( "" )
                    self.handle.expect( self.prompt )
                    self.handle.sendline( "exit" )
                    self.handle.expect( "closed" )
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

    def logout( self ):
        """
        Sends 'logout' command to ONOS cli
        Returns main.TRUE if exited CLI and
                main.FALSE on timeout (not guranteed you are disconnected)
                None on TypeError
                Exits test on unknown error or pexpect exits unexpectedly
        """
        try:
            if self.handle:
                self.handle.sendline( "" )
                i = self.handle.expect( [ "onos>", self.prompt, pexpect.TIMEOUT ],
                                        timeout=10 )
                if i == 0:  # In ONOS CLI
                    self.handle.sendline( "logout" )
                    j = self.handle.expect( [ self.prompt,
                                              "Command not found:",
                                              pexpect.TIMEOUT ] )
                    if j == 0:  # Successfully logged out
                        return main.TRUE
                    elif j == 1 or j == 2:
                        # ONOS didn't fully load, and logout command isn't working
                        # or the command timed out
                        self.handle.send( "\x04" )  # send ctrl-d
                        try:
                            self.handle.expect( self.prompt )
                        except pexpect.TIMEOUT:
                            main.log.error( "ONOS did not respond to 'logout' or CTRL-d" )
                        return main.TRUE
                    else:  # some other output
                        main.log.warn( "Unknown repsonse to logout command: '{}'",
                                       repr( self.handle.before ) )
                        return main.FALSE
                elif i == 1:  # not in CLI
                    return main.TRUE
                elif i == 2:  # Timeout
                    return main.FALSE
            else:
                return main.TRUE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": eof exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except ValueError:
            main.log.error( self.name +
                            "ValueError exception in logout method" )
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def setCell( self, cellname ):
        """
        Calls 'cell <name>' to set the environment variables on ONOSbench

        Before issuing any cli commands, set the environment variable first.
        """
        try:
            if not cellname:
                main.log.error( "Must define cellname" )
                main.cleanAndExit()
            else:
                self.handle.sendline( "cell " + str( cellname ) )
                # Expect the cellname in the ONOSCELL variable.
                # Note that this variable name is subject to change
                #   and that this driver will have to change accordingly
                self.handle.expect( str( cellname ) )
                handleBefore = self.handle.before
                handleAfter = self.handle.after
                # Get the rest of the handle
                self.handle.sendline( "" )
                self.handle.expect( self.prompt )
                handleMore = self.handle.before

                main.log.info( "Cell call returned: " + handleBefore +
                               handleAfter + handleMore )

                return main.TRUE

        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": eof exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def startOnosCli( self, ONOSIp, karafTimeout="",
                      commandlineTimeout=10, onosStartTimeout=60, waitForStart=False ):
        """
        karafTimeout is an optional argument. karafTimeout value passed
        by user would be used to set the current karaf shell idle timeout.
        Note that when ever this property is modified the shell will exit and
        the subsequent login would reflect new idle timeout.
        Below is an example to start a session with 60 seconds idle timeout
        ( input value is in milliseconds ):

        tValue = "60000"
        main.ONOScli1.startOnosCli( ONOSIp, karafTimeout=tValue )

        Note: karafTimeout is left as str so that this could be read
        and passed to startOnosCli from PARAMS file as str.
        """
        self.onosIp = ONOSIp
        try:
            # Check if we are already in the cli
            self.handle.sendline( "" )
            x = self.handle.expect( [
                self.prompt, "onos>" ], commandlineTimeout )
            if x == 1:
                main.log.info( "ONOS cli is already running" )
                return main.TRUE

            # Not in CLI so login
            if waitForStart:
                # Wait for onos start ( onos-wait-for-start ) and enter onos cli
                startCliCommand = "onos-wait-for-start "
            else:
                startCliCommand = "onos "
            self.handle.sendline( startCliCommand + str( ONOSIp ) )
            i = self.handle.expect( [
                "onos>",
                pexpect.TIMEOUT ], onosStartTimeout )

            if i == 0:
                main.log.info( str( ONOSIp ) + " CLI Started successfully" )
                if karafTimeout:
                    self.handle.sendline(
                        "config:property-set -p org.apache.karaf.shell\
                                 sshIdleTimeout " +
                        karafTimeout )
                    self.handle.expect( self.prompt )
                    self.handle.sendline( startCliCommand + str( ONOSIp ) )
                    self.handle.expect( "onos>" )
                return main.TRUE
            else:
                # If failed, send ctrl+c to process and try again
                main.log.info( "Starting CLI failed. Retrying..." )
                self.handle.send( "\x03" )
                self.handle.sendline( startCliCommand + str( ONOSIp ) )
                i = self.handle.expect( [ "onos>", pexpect.TIMEOUT ],
                                        timeout=30 )
                if i == 0:
                    main.log.info( str( ONOSIp ) + " CLI Started " +
                                   "successfully after retry attempt" )
                    if karafTimeout:
                        self.handle.sendline(
                            "config:property-set -p org.apache.karaf.shell\
                                    sshIdleTimeout " +
                            karafTimeout )
                        self.handle.expect( self.prompt )
                        self.handle.sendline( startCliCommand + str( ONOSIp ) )
                        self.handle.expect( "onos>" )
                    return main.TRUE
                else:
                    main.log.error( "Connection to CLI " +
                                    str( ONOSIp ) + " timeout" )
                    return main.FALSE

        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def startCellCli( self, karafTimeout="",
                      commandlineTimeout=10, onosStartTimeout=60 ):
        """
        Start CLI on onos ecll handle.

        karafTimeout is an optional argument. karafTimeout value passed
        by user would be used to set the current karaf shell idle timeout.
        Note that when ever this property is modified the shell will exit and
        the subsequent login would reflect new idle timeout.
        Below is an example to start a session with 60 seconds idle timeout
        ( input value is in milliseconds ):

        tValue = "60000"

        Note: karafTimeout is left as str so that this could be read
        and passed to startOnosCli from PARAMS file as str.
        """

        try:
            self.handle.sendline( "" )
            x = self.handle.expect( [
                self.prompt, "onos>" ], commandlineTimeout )

            if x == 1:
                main.log.info( "ONOS cli is already running" )
                return main.TRUE

            # Wait for onos start ( onos-wait-for-start ) and enter onos cli
            self.handle.sendline( "/opt/onos/bin/onos" )
            i = self.handle.expect( [
                "onos>",
                pexpect.TIMEOUT ], onosStartTimeout )

            if i == 0:
                main.log.info( self.name + " CLI Started successfully" )
                if karafTimeout:
                    self.handle.sendline(
                        "config:property-set -p org.apache.karaf.shell\
                                 sshIdleTimeout " +
                        karafTimeout )
                    self.handle.expect( self.prompt )
                    self.handle.sendline( "/opt/onos/bin/onos" )
                    self.handle.expect( "onos>" )
                return main.TRUE
            else:
                # If failed, send ctrl+c to process and try again
                main.log.info( "Starting CLI failed. Retrying..." )
                self.handle.send( "\x03" )
                self.handle.sendline( "/opt/onos/bin/onos" )
                i = self.handle.expect( [ "onos>", pexpect.TIMEOUT ],
                                        timeout=30 )
                if i == 0:
                    main.log.info( self.name + " CLI Started " +
                                   "successfully after retry attempt" )
                    if karafTimeout:
                        self.handle.sendline(
                            "config:property-set -p org.apache.karaf.shell\
                                    sshIdleTimeout " +
                            karafTimeout )
                        self.handle.expect( self.prompt )
                        self.handle.sendline( "/opt/onos/bin/onos" )
                        self.handle.expect( "onos>" )
                    return main.TRUE
                else:
                    main.log.error( "Connection to CLI " +
                                    self.name + " timeout" )
                    return main.FALSE

        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def log( self, cmdStr, level="", noExit=False ):
        """
            log  the commands in the onos CLI.
            returns main.TRUE on success
            returns main.FALSE if Error occurred
            if noExit is True, TestON will not exit, but clean up
            Available level: DEBUG, TRACE, INFO, WARN, ERROR
            Level defaults to INFO
            if cmdStr has spaces then put quotes in the passed string
        """
        try:
            lvlStr = ""
            if level:
                lvlStr = "--level=" + level

            self.handle.sendline( "log:log " + lvlStr + " " + cmdStr )
            self.handle.expect( "log:log" )
            self.handle.expect( "onos>" )

            response = self.handle.before
            if re.search( "Error", response ):
                return main.FALSE
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception found" )
            if noExit:
                main.cleanup()
                return None
            else:
                main.cleanAndExit()
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            if noExit:
                main.cleanup()
                return None
            else:
                main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            if noExit:
                main.cleanup()
                return None
            else:
                main.cleanAndExit()

    def clearBuffer( self, debug=False, timeout=10, noExit=False ):
        """
        Test cli connection and clear any left over output in the buffer
        Optional Arguments:
        debug - Defaults to False. If True, will enable debug logging.
        timeout - Defaults to 10. Amount of time in seconds for a command to return
                  before a timeout.
        noExit - Defaults to False. If True, will not exit TestON in the event of a
        """
        try:
            # Try to reconnect if disconnected from cli
            self.handle.sendline( "" )
            i = self.handle.expect( [ "onos>", self.prompt, pexpect.TIMEOUT ] )
            response = self.handle.before
            if i == 1:
                main.log.error( self.name + ": onos cli session closed. " )
                if self.onosIp:
                    main.log.warn( "Trying to reconnect " + self.onosIp )
                    reconnectResult = self.startOnosCli( self.onosIp )
                    if reconnectResult:
                        main.log.info( self.name + ": onos cli session reconnected." )
                    else:
                        main.log.error( self.name + ": reconnection failed." )
                        if noExit:
                            return None
                        else:
                            main.cleanAndExit()
                else:
                    main.cleanAndExit()
            if i == 2:
                main.log.warn( "Timeout when testing cli responsiveness" )
                main.log.debug( self.handle.before )
                self.handle.send( "\x03" )  # Send ctrl-c to clear previous output
                self.handle.expect( "onos>" )

            response += self.handle.before
            if debug:
                main.log.debug( self.name + ": Raw output from sending ''" )
                main.log.debug( self.name + ": " + repr( response ) )
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": ONOS timeout" )
            main.log.debug( self.handle.before )
            self.handle.send( "\x03" )
            self.handle.expect( "onos>" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            if noExit:
                return None
            else:
                main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            if noExit:
                return None
            else:
                main.cleanAndExit()

    def sendline( self, cmdStr, showResponse=False, debug=False, timeout=10, noExit=False ):
        """
        A wrapper around pexpect's sendline/expect. Will return all the output from a given command

        Required Arguments:
        cmdStr - String to send to the pexpect session

        Optional Arguments:
        showResponse - Defaults to False. If True will log the response.
        debug - Defaults to False. If True, will enable debug logging.
        timeout - Defaults to 10. Amount of time in seconds for a command to return
                  before a timeout.
        noExit - Defaults to False. If True, will not exit TestON in the event of a
                 closed channel, but instead return None

        Warning: There are no sanity checking to commands sent using this method.

        """
        try:
            # Try to reconnect if disconnected from cli
            self.clearBuffer( debug=debug, timeout=timeout, noExit=noExit )
            if debug:
                # NOTE: This adds an average of .4 seconds per call
                logStr = "\"Sending CLI command: '" + cmdStr + "'\""
                self.log( logStr, noExit=noExit )
            self.handle.sendline( cmdStr )
            self.handle.expect( "onos>", timeout )
            response = self.handle.before
            main.log.info( "Command '" + str( cmdStr ) + "' sent to "
                           + self.name + "." )
            if debug:
                main.log.debug( self.name + ": Raw output" )
                main.log.debug( self.name + ": " + repr( response ) )

            # Remove ANSI color control strings from output
            ansiEscape = re.compile( r'\x1b[^m]*m' )
            response = ansiEscape.sub( '', response )
            if debug:
                main.log.debug( self.name + ": ansiEscape output" )
                main.log.debug( self.name + ": " + repr( response ) )

            # Remove extra return chars that get added
            response = re.sub(  r"\s\r", "", response )
            if debug:
                main.log.debug( self.name + ": Removed extra returns " +
                                "from output" )
                main.log.debug( self.name + ": " + repr( response ) )

            # Strip excess whitespace
            response = response.strip()
            if debug:
                main.log.debug( self.name + ": parsed and stripped output" )
                main.log.debug( self.name + ": " + repr( response ) )

            # parse for just the output, remove the cmd from response
            output = response.split( cmdStr.strip(), 1 )
            if output:
                if debug:
                    main.log.debug( self.name + ": split output" )
                    for r in output:
                        main.log.debug( self.name + ": " + repr( r ) )
                output = output[ 1 ].strip()
            if showResponse:
                main.log.info( "Response from ONOS: {}".format( output ) )
            self.clearBuffer( debug=debug, timeout=timeout, noExit=noExit )
            return output
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": ONOS timeout" )
            if debug:
                main.log.debug( self.handle.before )
            self.handle.send( "\x03" )
            self.handle.expect( "onos>" )
            return None
        except IndexError:
            main.log.exception( self.name + ": Object not as expected" )
            main.log.debug( "response: {}".format( repr( response ) ) )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            if noExit:
                return None
            else:
                main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            if noExit:
                return None
            else:
                main.cleanAndExit()

    # IMPORTANT NOTE:
    # For all cli commands, naming convention should match
    # the cli command changing 'a:b' with 'aB'.
    # Ex ) onos:topology > onosTopology
    #    onos:links    > onosLinks
    #    feature:list  > featureList

    def addNode( self, nodeId, ONOSIp, tcpPort="" ):
        """
        Adds a new cluster node by ID and address information.
        Required:
            * nodeId
            * ONOSIp
        Optional:
            * tcpPort
        """
        try:
            cmdStr = "add-node " + str( nodeId ) + " " +\
                str( ONOSIp ) + " " + str( tcpPort )
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            if re.search( "Error", handle ):
                main.log.error( self.name + ": Error in adding node" )
                main.log.error( handle )
                return main.FALSE
            else:
                main.log.info( "Node " + str( ONOSIp ) + " added" )
                return main.TRUE
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def removeNode( self, nodeId ):
        """
        Removes a cluster by ID
        Issues command: 'remove-node [<node-id>]'
        Required:
            * nodeId
        """
        try:

            cmdStr = "remove-node " + str( nodeId )
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            if re.search( "Error", handle ):
                main.log.error( self.name + ": Error in removing node" )
                main.log.error( handle )
                return main.FALSE
            else:
                return main.TRUE
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def nodes( self, jsonFormat=True ):
        """
        List the nodes currently visible
        Issues command: 'nodes'
        Optional argument:
            * jsonFormat - boolean indicating if you want output in json
        """
        try:
            cmdStr = "nodes"
            if jsonFormat:
                cmdStr += " -j"
            output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            return output
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def topology( self ):
        """
        Definition:
            Returns the output of topology command.
        Return:
            topology = current ONOS topology
        """
        try:
            cmdStr = "topology -j"
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            main.log.info( cmdStr + " returned: " + str( handle ) )
            return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def deviceRemove( self, deviceId ):
        """
        Removes particular device from storage

        TODO: refactor this function
        """
        try:
            cmdStr = "device-remove " + str( deviceId )
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            if re.search( "Error", handle ):
                main.log.error( self.name + ": Error in removing device" )
                main.log.error( handle )
                return main.FALSE
            else:
                return main.TRUE
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def devices( self, jsonFormat=True, timeout=30 ):
        """
        Lists all infrastructure devices or switches
        Optional argument:
            * jsonFormat - boolean indicating if you want output in json
        """
        try:
            cmdStr = "devices"
            if jsonFormat:
                cmdStr += " -j"
            handle = self.sendline( cmdStr, timeout=timeout )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def balanceMasters( self ):
        """
        This balances the devices across all controllers
        by issuing command: 'onos> onos:balance-masters'
        If required this could be extended to return devices balanced output.
        """
        try:
            cmdStr = "onos:balance-masters"
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            if re.search( "Error", handle ):
                main.log.error( self.name + ": Error in balancing masters" )
                main.log.error( handle )
                return main.FALSE
            else:
                return main.TRUE
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def checkMasters( self, jsonFormat=True  ):
        """
            Returns the output of the masters command.
            Optional argument:
                * jsonFormat - boolean indicating if you want output in json
        """
        try:
            cmdStr = "onos:masters"
            if jsonFormat:
                cmdStr += " -j"
            output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            return output
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def checkBalanceMasters( self, jsonFormat=True ):
        """
            Uses the master command to check that the devices' leadership
            is evenly divided

            Dependencies: checkMasters() and summary()

            Returns main.TRUE if the devices are balanced
            Returns main.FALSE if the devices are unbalanced
            Exits on Exception
            Returns None on TypeError
        """
        try:
            summaryOutput = self.summary()
            totalDevices = json.loads( summaryOutput )[ "devices" ]
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, summaryOutput ) )
            return None
        try:
            totalOwnedDevices = 0
            mastersOutput = self.checkMasters()
            masters = json.loads( mastersOutput )
            first = masters[ 0 ][ "size" ]
            for master in masters:
                totalOwnedDevices += master[ "size" ]
                if master[ "size" ] > first + 1 or master[ "size" ] < first - 1:
                    main.log.error( "Mastership not balanced" )
                    main.log.info( "\n" + self.checkMasters( False ) )
                    return main.FALSE
            main.log.info( "Mastership balanced between " +
                           str( len( masters ) ) + " masters" )
            return main.TRUE
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, mastersOutput ) )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def links( self, jsonFormat=True, timeout=30 ):
        """
        Lists all core links
        Optional argument:
            * jsonFormat - boolean indicating if you want output in json
        """
        try:
            cmdStr = "links"
            if jsonFormat:
                cmdStr += " -j"
            handle = self.sendline( cmdStr, timeout=timeout )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def ports( self, jsonFormat=True, timeout=30 ):
        """
        Lists all ports
        Optional argument:
            * jsonFormat - boolean indicating if you want output in json
        """
        try:
            cmdStr = "ports"
            if jsonFormat:
                cmdStr += " -j"
            handle = self.sendline( cmdStr, timeout=timeout )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def roles( self, jsonFormat=True ):
        """
        Lists all devices and the controllers with roles assigned to them
        Optional argument:
            * jsonFormat - boolean indicating if you want output in json
        """
        try:
            cmdStr = "roles"
            if jsonFormat:
                cmdStr += " -j"
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getRole( self, deviceId ):
        """
        Given the a string containing the json representation of the "roles"
        cli command and a partial or whole device id, returns a json object
        containing the roles output for the first device whose id contains
        "device_id"

        Returns:
        A dict of the role assignments for the given device or
        None if no match
        """
        try:
            if deviceId is None:
                return None
            else:
                rawRoles = self.roles()
                rolesJson = json.loads( rawRoles )
                # search json for the device with id then return the device
                for device in rolesJson:
                    # print device
                    if str( deviceId ) in device[ 'id' ]:
                        return device
            return None
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, rawRoles ) )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def rolesNotNull( self ):
        """
        Iterates through each device and checks if there is a master assigned
        Returns: main.TRUE if each device has a master
                 main.FALSE any device has no master
        """
        try:
            rawRoles = self.roles()
            rolesJson = json.loads( rawRoles )
            # search json for the device with id then return the device
            for device in rolesJson:
                # print device
                if device[ 'master' ] == "none":
                    main.log.warn( "Device has no master: " + str( device ) )
                    return main.FALSE
            return main.TRUE
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, rawRoles ) )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def paths( self, srcId, dstId ):
        """
        Returns string of paths, and the cost.
        Issues command: onos:paths <src> <dst>
        """
        try:
            cmdStr = "onos:paths " + str( srcId ) + " " + str( dstId )
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            if re.search( "Error", handle ):
                main.log.error( self.name + ": Error in getting paths" )
                return ( handle, "Error" )
            else:
                path = handle.split( ";" )[ 0 ]
                cost = handle.split( ";" )[ 1 ]
                return ( path, cost )
        except AssertionError:
            main.log.exception( "" )
            return ( handle, "Error" )
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return ( handle, "Error" )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def hosts( self, jsonFormat=True ):
        """
        Lists all discovered hosts
        Optional argument:
            * jsonFormat - boolean indicating if you want output in json
        """
        try:
            cmdStr = "hosts"
            if jsonFormat:
                cmdStr += " -j"
            handle = self.sendline( cmdStr )
            if handle:
                assert "Command not found:" not in handle, handle
                # TODO: Maybe make this less hardcoded
                # ConsistentMap Exceptions
                assert "org.onosproject.store.service" not in handle
                # Node not leader
                assert "java.lang.IllegalStateException" not in handle
            return handle
        except AssertionError:
            main.log.exception( self.name + ": Error in processing '" + cmdStr + "' " +
                                "command: " + str( handle ) )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getHost( self, mac ):
        """
        Return the first host from the hosts api whose 'id' contains 'mac'

        Note: mac must be a colon separated mac address, but could be a
              partial mac address

        Return None if there is no match
        """
        try:
            if mac is None:
                return None
            else:
                mac = mac
                rawHosts = self.hosts()
                hostsJson = json.loads( rawHosts )
                # search json for the host with mac then return the device
                for host in hostsJson:
                    # print "%s in  %s?" % ( mac, host[ 'id' ] )
                    if not host:
                        pass
                    elif mac in host[ 'id' ]:
                        return host
            return None
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, rawHosts ) )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getHostsId( self, hostList ):
        """
        Obtain list of hosts
        Issues command: 'onos> hosts'

        Required:
            * hostList: List of hosts obtained by Mininet
        IMPORTANT:
            This function assumes that you started your
            topology with the option '--mac'.
            Furthermore, it assumes that value of VLAN is '-1'
        Description:
            Converts mininet hosts ( h1, h2, h3... ) into
            ONOS format ( 00:00:00:00:00:01/-1 , ... )
        """
        try:
            onosHostList = []

            for host in hostList:
                host = host.replace( "h", "" )
                hostHex = hex( int( host ) ).zfill( 12 )
                hostHex = str( hostHex ).replace( 'x', '0' )
                i = iter( str( hostHex ) )
                hostHex = ":".join( a + b for a, b in zip( i, i ) )
                hostHex = hostHex + "/-1"
                onosHostList.append( hostHex )

            return onosHostList

        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def verifyHostLocation( self, hostIp, location ):
        """
        Description:
            Verify the host given is discovered in all locations expected
        Required:
            hostIp: IP address of the host
            location: expected location(s) of the given host. ex. "of:0000000000000005/8"
                      Could be a string or list
        Returns:
            main.TRUE if host is discovered on all locations provided
            main.FALSE otherwise
        """
        import json
        locations = [ location ] if isinstance( location, str ) else location
        assert isinstance( locations, list ), "Wrong type of location: {}".format( type( location ) )
        try:
            hosts = self.hosts()
            hosts = json.loads( hosts )
            targetHost = None
            for host in hosts:
                if hostIp in host[ "ipAddresses" ]:
                    targetHost = host
            assert targetHost, "Not able to find host with IP {}".format( hostIp )
            result = main.TRUE
            locationsDiscovered = [ loc[ "elementId" ] + "/" + loc[ "port" ] for loc in targetHost[ "locations" ] ]
            for loc in locations:
                discovered = False
                for locDiscovered in locationsDiscovered:
                    locToMatch = locDiscovered if "/" in loc else locDiscovered.split( "/" )[0]
                    if loc == locToMatch:
                        main.log.debug( "Host {} discovered with location {}".format( hostIp, loc ) )
                        discovered = True
                        break
                if discovered:
                    locationsDiscovered.remove( locDiscovered )
                else:
                    main.log.warn( "Host {} not discovered with location {}".format( hostIp, loc ) )
                    result = main.FALSE
            if locationsDiscovered:
                main.log.warn( "Host {} is also discovered with location {}".format( hostIp, locationsDiscovered ) )
                result = main.FALSE
            return result
        except KeyError:
            main.log.exception( self.name + ": host data not as expected: " + hosts )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception" )
            return None

    def verifyHostIp( self, hostList=[], prefix="" ):
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
        import json
        try:
            hosts = self.hosts()
            hosts = json.loads( hosts )
            if not hostList:
                hostList = [ host[ "id" ] for host in hosts ]
            for host in hosts:
                hostId = host[ "id" ]
                if hostId not in hostList:
                    continue
                ipList = host[ "ipAddresses" ]
                main.log.debug( self.name + ": IP list on host " + str( hostId ) + ": " + str( ipList ) )
                if not ipList:
                    main.log.warn( self.name + ": Failed to discover any IP addresses on host " + str( hostId ) )
                else:
                    if not any( ip.startswith( str( prefix ) ) for ip in ipList ):
                        main.log.warn( self.name + ": None of the IPs on host " + str( hostId ) + " has prefix " + str( prefix ) )
                    else:
                        main.log.debug( self.name + ": Found matching IP on host " + str( hostId ) )
                        hostList.remove( hostId )
            if hostList:
                main.log.warn( self.name + ": failed to verify IP on following hosts: " + str( hostList) )
                return main.FALSE
            else:
                return main.TRUE
        except KeyError:
            main.log.exception( self.name + ": host data not as expected: " + hosts )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception" )
            return None

    def addHostIntent( self, hostIdOne, hostIdTwo, vlanId="", setVlan="", encap="", bandwidth="" ):
        """
        Required:
            * hostIdOne: ONOS host id for host1
            * hostIdTwo: ONOS host id for host2
        Optional:
            * vlanId: specify a VLAN id for the intent
            * setVlan: specify a VLAN id treatment
            * encap: specify an encapsulation type
        Description:
            Adds a host-to-host intent ( bidirectional ) by
            specifying the two hosts.
        Returns:
            A string of the intent id or None on Error
        """
        try:
            cmdStr = "add-host-intent "
            if vlanId:
                cmdStr += "-v " + str( vlanId ) + " "
            if setVlan:
                cmdStr += "--setVlan " + str( vlanId ) + " "
            if encap:
                cmdStr += "--encapsulation " + str( encap ) + " "
            if bandwidth:
                cmdStr += "-b " + str( bandwidth ) + " "
            cmdStr += str( hostIdOne ) + " " + str( hostIdTwo )
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            if re.search( "Error", handle ):
                main.log.error( self.name + ": Error in adding Host intent" )
                main.log.debug( "Response from ONOS was: " + repr( handle ) )
                return None
            else:
                main.log.info( "Host intent installed between " +
                               str( hostIdOne ) + " and " + str( hostIdTwo ) )
                match = re.search( 'id=0x([\da-f]+),', handle )
                if match:
                    return match.group()[ 3:-1 ]
                else:
                    main.log.error( "Error, intent ID not found" )
                    main.log.debug( "Response from ONOS was: " +
                                    repr( handle ) )
                    return None
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def addOpticalIntent( self, ingressDevice, egressDevice ):
        """
        Required:
            * ingressDevice: device id of ingress device
            * egressDevice: device id of egress device
        Optional:
            TODO: Still needs to be implemented via dev side
        Description:
            Adds an optical intent by specifying an ingress and egress device
        Returns:
            A string of the intent id or None on error
        """
        try:
            cmdStr = "add-optical-intent " + str( ingressDevice ) +\
                " " + str( egressDevice )
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            # If error, return error message
            if re.search( "Error", handle ):
                main.log.error( self.name + ": Error in adding Optical intent" )
                return None
            else:
                main.log.info( "Optical intent installed between " +
                               str( ingressDevice ) + " and " +
                               str( egressDevice ) )
                match = re.search( 'id=0x([\da-f]+),', handle )
                if match:
                    return match.group()[ 3:-1 ]
                else:
                    main.log.error( "Error, intent ID not found" )
                    return None
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def addPointIntent(
            self,
            ingressDevice,
            egressDevice,
            portIngress="",
            portEgress="",
            ethType="",
            ethSrc="",
            ethDst="",
            bandwidth="",
            lambdaAlloc=False,
            protected=False,
            ipProto="",
            ipSrc="",
            ipDst="",
            tcpSrc="",
            tcpDst="",
            vlanId="",
            setVlan="",
            encap="" ):
        """
        Required:
            * ingressDevice: device id of ingress device
            * egressDevice: device id of egress device
        Optional:
            * ethType: specify ethType
            * ethSrc: specify ethSrc ( i.e. src mac addr )
            * ethDst: specify ethDst ( i.e. dst mac addr )
            * bandwidth: specify bandwidth capacity of link
            * lambdaAlloc: if True, intent will allocate lambda
              for the specified intent
            * ipProto: specify ip protocol
            * ipSrc: specify ip source address
            * ipDst: specify ip destination address
            * tcpSrc: specify tcp source port
            * tcpDst: specify tcp destination port
            * vlanId: specify vlan ID
            * setVlan: specify a VLAN id treatment
            * encap: specify an Encapsulation type to use
        Description:
            Adds a point-to-point intent ( uni-directional ) by
            specifying device id's and optional fields
        Returns:
            A string of the intent id or None on error

        NOTE: This function may change depending on the
              options developers provide for point-to-point
              intent via cli
        """
        try:
            cmd = "add-point-intent"

            if ethType:
                cmd += " --ethType " + str( ethType )
            if ethSrc:
                cmd += " --ethSrc " + str( ethSrc )
            if ethDst:
                cmd += " --ethDst " + str( ethDst )
            if bandwidth:
                cmd += " --bandwidth " + str( bandwidth )
            if lambdaAlloc:
                cmd += " --lambda "
            if ipProto:
                cmd += " --ipProto " + str( ipProto )
            if ipSrc:
                cmd += " --ipSrc " + str( ipSrc )
            if ipDst:
                cmd += " --ipDst " + str( ipDst )
            if tcpSrc:
                cmd += " --tcpSrc " + str( tcpSrc )
            if tcpDst:
                cmd += " --tcpDst " + str( tcpDst )
            if vlanId:
                cmd += " -v " + str( vlanId )
            if setVlan:
                cmd += " --setVlan " + str( setVlan )
            if encap:
                cmd += " --encapsulation " + str( encap )
            if protected:
                cmd += " --protect "

            # Check whether the user appended the port
            # or provided it as an input
            if "/" in ingressDevice:
                cmd += " " + str( ingressDevice )
            else:
                if not portIngress:
                    main.log.error( "You must specify the ingress port" )
                    # TODO: perhaps more meaningful return
                    #       Would it make sense to throw an exception and exit
                    #       the test?
                    return None

                cmd += " " + \
                    str( ingressDevice ) + "/" +\
                    str( portIngress ) + " "

            if "/" in egressDevice:
                cmd += " " + str( egressDevice )
            else:
                if not portEgress:
                    main.log.error( "You must specify the egress port" )
                    return None

                cmd += " " +\
                    str( egressDevice ) + "/" +\
                    str( portEgress )

            handle = self.sendline( cmd )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            # If error, return error message
            if re.search( "Error", handle ):
                main.log.error( self.name + ": Error in adding point-to-point intent" )
                return None
            else:
                # TODO: print out all the options in this message?
                main.log.info( "Point-to-point intent installed between " +
                               str( ingressDevice ) + " and " +
                               str( egressDevice ) )
                match = re.search( 'id=0x([\da-f]+),', handle )
                if match:
                    return match.group()[ 3:-1 ]
                else:
                    main.log.error( "Error, intent ID not found" )
                    return None
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def addMultipointToSinglepointIntent(
            self,
            ingressDeviceList,
            egressDevice,
            portIngressList=None,
            portEgress="",
            ethType="",
            ethSrc="",
            ethDst="",
            bandwidth="",
            lambdaAlloc=False,
            ipProto="",
            ipSrc="",
            ipDst="",
            tcpSrc="",
            tcpDst="",
            setEthSrc="",
            setEthDst="",
            vlanId="",
            setVlan="",
            partial=False,
            encap="" ):
        """
        Note:
            This function assumes the format of all ingress devices
            is same. That is, all ingress devices include port numbers
            with a "/" or all ingress devices could specify device
            ids and port numbers seperately.
        Required:
            * ingressDeviceList: List of device ids of ingress device
                ( Atleast 2 ingress devices required in the list )
            * egressDevice: device id of egress device
        Optional:
            * ethType: specify ethType
            * ethSrc: specify ethSrc ( i.e. src mac addr )
            * ethDst: specify ethDst ( i.e. dst mac addr )
            * bandwidth: specify bandwidth capacity of link
            * lambdaAlloc: if True, intent will allocate lambda
              for the specified intent
            * ipProto: specify ip protocol
            * ipSrc: specify ip source address
            * ipDst: specify ip destination address
            * tcpSrc: specify tcp source port
            * tcpDst: specify tcp destination port
            * setEthSrc: action to Rewrite Source MAC Address
            * setEthDst: action to Rewrite Destination MAC Address
            * vlanId: specify vlan Id
            * setVlan: specify VLAN Id treatment
            * encap: specify a type of encapsulation
        Description:
            Adds a multipoint-to-singlepoint intent ( uni-directional ) by
            specifying device id's and optional fields
        Returns:
            A string of the intent id or None on error

        NOTE: This function may change depending on the
              options developers provide for multipoint-to-singlepoint
              intent via cli
        """
        try:
            cmd = "add-multi-to-single-intent"

            if ethType:
                cmd += " --ethType " + str( ethType )
            if ethSrc:
                cmd += " --ethSrc " + str( ethSrc )
            if ethDst:
                cmd += " --ethDst " + str( ethDst )
            if bandwidth:
                cmd += " --bandwidth " + str( bandwidth )
            if lambdaAlloc:
                cmd += " --lambda "
            if ipProto:
                cmd += " --ipProto " + str( ipProto )
            if ipSrc:
                cmd += " --ipSrc " + str( ipSrc )
            if ipDst:
                cmd += " --ipDst " + str( ipDst )
            if tcpSrc:
                cmd += " --tcpSrc " + str( tcpSrc )
            if tcpDst:
                cmd += " --tcpDst " + str( tcpDst )
            if setEthSrc:
                cmd += " --setEthSrc " + str( setEthSrc )
            if setEthDst:
                cmd += " --setEthDst " + str( setEthDst )
            if vlanId:
                cmd += " -v " + str( vlanId )
            if setVlan:
                cmd += " --setVlan " + str( setVlan )
            if partial:
                cmd += " --partial"
            if encap:
                cmd += " --encapsulation " + str( encap )

            # Check whether the user appended the port
            # or provided it as an input

            if portIngressList is None:
                for ingressDevice in ingressDeviceList:
                    if "/" in ingressDevice:
                        cmd += " " + str( ingressDevice )
                    else:
                        main.log.error( "You must specify " +
                                        "the ingress port" )
                        # TODO: perhaps more meaningful return
                        return main.FALSE
            else:
                if len( ingressDeviceList ) == len( portIngressList ):
                    for ingressDevice, portIngress in zip( ingressDeviceList,
                                                           portIngressList ):
                        cmd += " " + \
                            str( ingressDevice ) + "/" +\
                            str( portIngress ) + " "
                else:
                    main.log.error( "Device list and port list does not " +
                                    "have the same length" )
                    return main.FALSE
            if "/" in egressDevice:
                cmd += " " + str( egressDevice )
            else:
                if not portEgress:
                    main.log.error( "You must specify " +
                                    "the egress port" )
                    return main.FALSE

                cmd += " " +\
                    str( egressDevice ) + "/" +\
                    str( portEgress )
            handle = self.sendline( cmd )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            # If error, return error message
            if re.search( "Error", handle ):
                main.log.error( self.name + ": Error in adding multipoint-to-singlepoint " +
                                "intent" )
                return None
            else:
                match = re.search( 'id=0x([\da-f]+),', handle )
                if match:
                    return match.group()[ 3:-1 ]
                else:
                    main.log.error( "Error, intent ID not found" )
                    return None
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def addSinglepointToMultipointIntent(
            self,
            ingressDevice,
            egressDeviceList,
            portIngress="",
            portEgressList=None,
            ethType="",
            ethSrc="",
            ethDst="",
            bandwidth="",
            lambdaAlloc=False,
            ipProto="",
            ipSrc="",
            ipDst="",
            tcpSrc="",
            tcpDst="",
            setEthSrc="",
            setEthDst="",
            vlanId="",
            setVlan="",
            partial=False,
            encap="" ):
        """
        Note:
            This function assumes the format of all egress devices
            is same. That is, all egress devices include port numbers
            with a "/" or all egress devices could specify device
            ids and port numbers seperately.
        Required:
            * EgressDeviceList: List of device ids of egress device
                ( Atleast 2 eress devices required in the list )
            * ingressDevice: device id of ingress device
        Optional:
            * ethType: specify ethType
            * ethSrc: specify ethSrc ( i.e. src mac addr )
            * ethDst: specify ethDst ( i.e. dst mac addr )
            * bandwidth: specify bandwidth capacity of link
            * lambdaAlloc: if True, intent will allocate lambda
              for the specified intent
            * ipProto: specify ip protocol
            * ipSrc: specify ip source address
            * ipDst: specify ip destination address
            * tcpSrc: specify tcp source port
            * tcpDst: specify tcp destination port
            * setEthSrc: action to Rewrite Source MAC Address
            * setEthDst: action to Rewrite Destination MAC Address
            * vlanId: specify vlan Id
            * setVlan: specify VLAN ID treatment
            * encap: specify an encapsulation type
        Description:
            Adds a singlepoint-to-multipoint intent ( uni-directional ) by
            specifying device id's and optional fields
        Returns:
            A string of the intent id or None on error

        NOTE: This function may change depending on the
              options developers provide for singlepoint-to-multipoint
              intent via cli
        """
        try:
            cmd = "add-single-to-multi-intent"

            if ethType:
                cmd += " --ethType " + str( ethType )
            if ethSrc:
                cmd += " --ethSrc " + str( ethSrc )
            if ethDst:
                cmd += " --ethDst " + str( ethDst )
            if bandwidth:
                cmd += " --bandwidth " + str( bandwidth )
            if lambdaAlloc:
                cmd += " --lambda "
            if ipProto:
                cmd += " --ipProto " + str( ipProto )
            if ipSrc:
                cmd += " --ipSrc " + str( ipSrc )
            if ipDst:
                cmd += " --ipDst " + str( ipDst )
            if tcpSrc:
                cmd += " --tcpSrc " + str( tcpSrc )
            if tcpDst:
                cmd += " --tcpDst " + str( tcpDst )
            if setEthSrc:
                cmd += " --setEthSrc " + str( setEthSrc )
            if setEthDst:
                cmd += " --setEthDst " + str( setEthDst )
            if vlanId:
                cmd += " -v " + str( vlanId )
            if setVlan:
                cmd += " --setVlan " + str( setVlan )
            if partial:
                cmd += " --partial"
            if encap:
                cmd += " --encapsulation " + str( encap )

            # Check whether the user appended the port
            # or provided it as an input

            if "/" in ingressDevice:
                cmd += " " + str( ingressDevice )
            else:
                if not portIngress:
                    main.log.error( "You must specify " +
                                    "the Ingress port" )
                    return main.FALSE

                cmd += " " +\
                    str( ingressDevice ) + "/" +\
                    str( portIngress )

            if portEgressList is None:
                for egressDevice in egressDeviceList:
                    if "/" in egressDevice:
                        cmd += " " + str( egressDevice )
                    else:
                        main.log.error( "You must specify " +
                                        "the egress port" )
                        # TODO: perhaps more meaningful return
                        return main.FALSE
            else:
                if len( egressDeviceList ) == len( portEgressList ):
                    for egressDevice, portEgress in zip( egressDeviceList,
                                                         portEgressList ):
                        cmd += " " + \
                            str( egressDevice ) + "/" +\
                            str( portEgress )
                else:
                    main.log.error( "Device list and port list does not " +
                                    "have the same length" )
                    return main.FALSE
            handle = self.sendline( cmd )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            # If error, return error message
            if re.search( "Error", handle ):
                main.log.error( self.name + ": Error in adding singlepoint-to-multipoint " +
                                "intent" )
                return None
            else:
                match = re.search( 'id=0x([\da-f]+),', handle )
                if match:
                    return match.group()[ 3:-1 ]
                else:
                    main.log.error( "Error, intent ID not found" )
                    return None
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def addMplsIntent(
            self,
            ingressDevice,
            egressDevice,
            ingressPort="",
            egressPort="",
            ethType="",
            ethSrc="",
            ethDst="",
            bandwidth="",
            lambdaAlloc=False,
            ipProto="",
            ipSrc="",
            ipDst="",
            tcpSrc="",
            tcpDst="",
            ingressLabel="",
            egressLabel="",
            priority="" ):
        """
        Required:
            * ingressDevice: device id of ingress device
            * egressDevice: device id of egress device
        Optional:
            * ethType: specify ethType
            * ethSrc: specify ethSrc ( i.e. src mac addr )
            * ethDst: specify ethDst ( i.e. dst mac addr )
            * bandwidth: specify bandwidth capacity of link
            * lambdaAlloc: if True, intent will allocate lambda
              for the specified intent
            * ipProto: specify ip protocol
            * ipSrc: specify ip source address
            * ipDst: specify ip destination address
            * tcpSrc: specify tcp source port
            * tcpDst: specify tcp destination port
            * ingressLabel: Ingress MPLS label
            * egressLabel: Egress MPLS label
        Description:
            Adds MPLS intent by
            specifying device id's and optional fields
        Returns:
            A string of the intent id or None on error

        NOTE: This function may change depending on the
              options developers provide for MPLS
              intent via cli
        """
        try:
            cmd = "add-mpls-intent"

            if ethType:
                cmd += " --ethType " + str( ethType )
            if ethSrc:
                cmd += " --ethSrc " + str( ethSrc )
            if ethDst:
                cmd += " --ethDst " + str( ethDst )
            if bandwidth:
                cmd += " --bandwidth " + str( bandwidth )
            if lambdaAlloc:
                cmd += " --lambda "
            if ipProto:
                cmd += " --ipProto " + str( ipProto )
            if ipSrc:
                cmd += " --ipSrc " + str( ipSrc )
            if ipDst:
                cmd += " --ipDst " + str( ipDst )
            if tcpSrc:
                cmd += " --tcpSrc " + str( tcpSrc )
            if tcpDst:
                cmd += " --tcpDst " + str( tcpDst )
            if ingressLabel:
                cmd += " --ingressLabel " + str( ingressLabel )
            if egressLabel:
                cmd += " --egressLabel " + str( egressLabel )
            if priority:
                cmd += " --priority " + str( priority )

            # Check whether the user appended the port
            # or provided it as an input
            if "/" in ingressDevice:
                cmd += " " + str( ingressDevice )
            else:
                if not ingressPort:
                    main.log.error( "You must specify the ingress port" )
                    return None

                cmd += " " + \
                    str( ingressDevice ) + "/" +\
                    str( ingressPort ) + " "

            if "/" in egressDevice:
                cmd += " " + str( egressDevice )
            else:
                if not egressPort:
                    main.log.error( "You must specify the egress port" )
                    return None

                cmd += " " +\
                    str( egressDevice ) + "/" +\
                    str( egressPort )

            handle = self.sendline( cmd )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            # If error, return error message
            if re.search( "Error", handle ):
                main.log.error( self.name + ": Error in adding mpls intent" )
                return None
            else:
                # TODO: print out all the options in this message?
                main.log.info( "MPLS intent installed between " +
                               str( ingressDevice ) + " and " +
                               str( egressDevice ) )
                match = re.search( 'id=0x([\da-f]+),', handle )
                if match:
                    return match.group()[ 3:-1 ]
                else:
                    main.log.error( "Error, intent ID not found" )
                    return None
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def removeIntent( self, intentId, app='org.onosproject.cli',
                      purge=False, sync=False ):
        """
        Remove intent for specified application id and intent id
        Optional args:-
        -s or --sync: Waits for the removal before returning
        -p or --purge: Purge the intent from the store after removal

        Returns:
            main.FALSE on error and
            cli output otherwise
        """
        try:
            cmdStr = "remove-intent"
            if purge:
                cmdStr += " -p"
            if sync:
                cmdStr += " -s"

            cmdStr += " " + app + " " + str( intentId )
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            if re.search( "Error", handle ):
                main.log.error( self.name + ": Error in removing intent" )
                return main.FALSE
            else:
                # TODO: Should this be main.TRUE
                return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def removeAllIntents( self, purge=False, sync=False, app='org.onosproject.cli', timeout=30 ):
        """
        Description:
            Remove all the intents
        Optional args:-
            -s or --sync: Waits for the removal before returning
            -p or --purge: Purge the intent from the store after removal
        Returns:
            Returns main.TRUE if all intents are removed, otherwise returns
            main.FALSE; Returns None for exception
        """
        try:
            cmdStr = "remove-intent"
            if purge:
                cmdStr += " -p"
            if sync:
                cmdStr += " -s"

            cmdStr += " " + app
            handle = self.sendline( cmdStr, timeout=timeout )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            if re.search( "Error", handle ):
                main.log.error( self.name + ": Error in removing intent" )
                return main.FALSE
            else:
                return main.TRUE
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def purgeWithdrawnIntents( self ):
        """
        Purges all WITHDRAWN Intents
        """
        try:
            cmdStr = "purge-intents"
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            if re.search( "Error", handle ):
                main.log.error( self.name + ": Error in purging intents" )
                return main.FALSE
            else:
                return main.TRUE
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def wipeout( self ):
        """
        Wipe out the flows,intents,links,devices,hosts, and groups from the ONOS.
        """
        try:
            cmdStr = "wipe-out please"
            handle = self.sendline( cmdStr, timeout=60 )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            return main.TRUE
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def routes( self, jsonFormat=False ):
        """
        NOTE: This method should be used after installing application:
              onos-app-sdnip
        Optional:
            * jsonFormat: enable output formatting in json
        Description:
            Obtain all routes in the system
        """
        try:
            cmdStr = "routes"
            if jsonFormat:
                cmdStr += " -j"
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def ipv4RouteNumber( self ):
        """
        NOTE: This method should be used after installing application:
              onos-app-sdnip
        Description:
            Obtain the total IPv4 routes number in the system
        """
        try:
            cmdStr = "routes -j"
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            jsonResult = json.loads( handle )
            return len( jsonResult[ 'routes4' ] )
        except AssertionError:
            main.log.exception( "" )
            return None
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, handle ) )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    # =============Function to check Bandwidth allocation========
    def allocations( self, jsonFormat = True ):
        """
        Description:
            Obtain Bandwidth Allocation Information from ONOS cli.
        """
        try:
            cmdStr = "allocations"
            if jsonFormat:
                cmdStr += " -j"
            handle = self.sendline( cmdStr, timeout=300 )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, handle ) )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def intents( self, jsonFormat = True, summary = False, **intentargs ):
        """
        Description:
            Obtain intents from the ONOS cli.
        Optional:
            * jsonFormat: Enable output formatting in json, default to True
            * summary: Whether only output the intent summary, defaults to False
            * type: Only output a certain type of intent. This options is valid
                    only when jsonFormat is True and summary is True.
        """
        try:
            cmdStr = "intents"
            if summary:
                cmdStr += " -s"
            if jsonFormat:
                cmdStr += " -j"
            handle = self.sendline( cmdStr, timeout=300 )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            args = utilities.parse_args( [ "TYPE" ], **intentargs )
            if "TYPE" in args.keys():
                intentType = args[ "TYPE" ]
            else:
                intentType = ""
            # IF we want the summary of a specific intent type
            if jsonFormat and summary and ( intentType != "" ):
                jsonResult = json.loads( handle )
                if intentType in jsonResult.keys():
                    return jsonResult[ intentType ]
                else:
                    main.log.error( "unknown TYPE, returning all types of intents" )
                    return handle
            else:
                return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, handle ) )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getIntentState( self, intentsId, intentsJson=None ):
        """
        Description:
            Gets intent state. Accepts a single intent ID (string type) or a
            list of intent IDs.
        Parameters:
            intentsId: intent ID, both string type and list type are acceptable
            intentsJson: parsed json object from the onos:intents api
        Returns:
            Returns the state (string type) of the ID if a single intent ID is
            accepted.
            Returns a list of dictionaries if a list of intent IDs is accepted,
            and each dictionary maps 'id' to the Intent ID and 'state' to
            corresponding intent state.
        """

        try:
            state = "State is Undefined"
            if not intentsJson:
                rawJson = self.intents()
            else:
                rawJson = intentsJson
            parsedIntentsJson = json.loads( rawJson )
            if isinstance( intentsId, types.StringType ):
                for intent in parsedIntentsJson:
                    if intentsId == intent[ 'id' ]:
                        state = intent[ 'state' ]
                        return state
                main.log.info( "Cannot find intent ID" + str( intentsId ) +
                               " in the list" )
                return state
            elif isinstance( intentsId, types.ListType ):
                dictList = []
                for i in xrange( len( intentsId ) ):
                    stateDict = {}
                    for intent in parsedIntentsJson:
                        if intentsId[ i ] == intent[ 'id' ]:
                            stateDict[ 'state' ] = intent[ 'state' ]
                            stateDict[ 'id' ] = intentsId[ i ]
                            dictList.append( stateDict )
                            break
                if len( intentsId ) != len( dictList ):
                    main.log.warn( "Could not find all intents in ONOS output" )
                    main.log.debug( "expected ids: {} \n ONOS intents: {}".format( intentsId, parsedIntentsJson ) )
                return dictList
            else:
                main.log.info( "Invalid type for intentsId argument" )
                return None
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, rawJson ) )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def checkIntentState( self, intentsId, expectedState='INSTALLED' ):
        """
        Description:
            Check intents state
        Required:
            intentsId - List of intents ID to be checked
        Optional:
            expectedState - Check the expected state(s) of each intents
                            state in the list.
                            *NOTE: You can pass in a list of expected state,
                            Eg: expectedState = [ 'INSTALLED' , 'INSTALLING' ]
        Return:
            Returns main.TRUE only if all intent are the same as expected states,
            otherwise returns main.FALSE.
        """
        try:
            returnValue = main.TRUE
            # Generating a dictionary: intent id as a key and state as value

            # intentsDict = self.getIntentState( intentsId )
            intentsDict = []
            for intent in json.loads( self.intents() ):
                if isinstance( intentsId, types.StringType ) \
                        and intent.get( 'id' ) == intentsId:
                    intentsDict.append( intent )
                elif isinstance( intentsId, types.ListType ) \
                        and any( intent.get( 'id' ) == ids for ids in intentsId ):
                    intentsDict.append( intent )

            if not intentsDict:
                main.log.info( self.name + ": There is something wrong " +
                               "getting intents state" )
                return main.FALSE

            if isinstance( expectedState, types.StringType ):
                for intents in intentsDict:
                    if intents.get( 'state' ) != expectedState:
                        main.log.debug( self.name + " : Intent ID - " +
                                        intents.get( 'id' ) +
                                        " actual state = " +
                                        intents.get( 'state' )
                                        + " does not equal expected state = "
                                        + expectedState )
                        returnValue = main.FALSE
            elif isinstance( expectedState, types.ListType ):
                for intents in intentsDict:
                    if not any( state == intents.get( 'state' ) for state in
                                expectedState ):
                        main.log.debug( self.name + " : Intent ID - " +
                                        intents.get( 'id' ) +
                                        " actual state = " +
                                        intents.get( 'state' ) +
                                        " does not equal expected states = "
                                        + str( expectedState ) )
                        returnValue = main.FALSE

            if returnValue == main.TRUE:
                main.log.info( self.name + ": All " +
                               str( len( intentsDict ) ) +
                               " intents are in " + str( expectedState ) +
                               " state" )
            return returnValue
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def compareBandwidthAllocations( self, expectedAllocations ):
        """
        Description:
            Compare the allocated bandwidth with the given allocations
        Required:
            expectedAllocations - The expected ONOS output of the allocations command
        Return:
            Returns main.TRUE only if all intent are the same as expected states,
            otherwise returns main.FALSE.
        """
        # FIXME: Convert these string comparisons to object comparisons
        try:
            returnValue = main.TRUE
            bandwidthFailed = False
            rawAlloc = self.allocations()
            expectedFormat = StringIO( expectedAllocations )
            ONOSOutput = StringIO( rawAlloc )
            main.log.debug( "ONOSOutput: {}\nexpected output: {}".format( str( ONOSOutput ),
                                                                          str( expectedFormat ) ) )

            for actual, expected in izip( ONOSOutput, expectedFormat ):
                actual = actual.rstrip()
                expected = expected.rstrip()
                main.log.debug( "Expect: {}\nactual: {}".format( expected, actual ) )
                if actual != expected and 'allocated' in actual and 'allocated' in expected:
                    marker1 = actual.find( 'allocated' )
                    m1 = actual[ :marker1 ]
                    marker2 = expected.find( 'allocated' )
                    m2 = expected[ :marker2 ]
                    if m1 != m2:
                        bandwidthFailed = True
                elif actual != expected and 'allocated' not in actual and 'allocated' not in expected:
                    bandwidthFailed = True
            expectedFormat.close()
            ONOSOutput.close()

            if bandwidthFailed:
                main.log.error( "Bandwidth not allocated correctly using Intents!!" )
                returnValue = main.FALSE
            return returnValue
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def compareIntent( self, intentDict ):
        """
        Description:
            Compare the intent ids and states provided in the argument with all intents in ONOS
        Return:
            Returns main.TRUE if the two sets of intents match exactly, otherwise main.FALSE
        Arguments:
            intentDict: a dictionary which maps intent ids to intent states
        """
        try:
            intentsRaw = self.intents()
            intentsJson = json.loads( intentsRaw )
            intentDictONOS = {}
            for intent in intentsJson:
                intentDictONOS[ intent[ 'id' ] ] = intent[ 'state' ]
            returnValue = main.TRUE
            if len( intentDict ) != len( intentDictONOS ):
                main.log.warn( self.name + ": expected intent count does not match that in ONOS, " +
                               str( len( intentDict ) ) + " expected and " +
                               str( len( intentDictONOS ) ) + " actual" )
                returnValue = main.FALSE
            for intentID in intentDict.keys():
                if intentID not in intentDictONOS.keys():
                    main.log.debug( self.name + ": intent ID - " + intentID + " is not in ONOS" )
                    returnValue = main.FALSE
                else:
                    if intentDict[ intentID ] != intentDictONOS[ intentID ]:
                        main.log.debug( self.name + ": intent ID - " + intentID +
                                        " expected state is " + intentDict[ intentID ] +
                                        " but actual state is " + intentDictONOS[ intentID ] )
                        returnValue = main.FALSE
                    intentDictONOS.pop( intentID )
            if len( intentDictONOS ) > 0:
                returnValue = main.FALSE
                for intentID in intentDictONOS.keys():
                    main.log.debug( self.name + ": find extra intent in ONOS: intent ID " + intentID )
            if returnValue == main.TRUE:
                main.log.info( self.name + ": all intent IDs and states match that in ONOS" )
            return returnValue
        except KeyError:
            main.log.exception( self.name + ": KeyError exception found" )
            return main.ERROR
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, intentsRaw ) )
            return main.ERROR
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def checkIntentSummary( self, timeout=60, noExit=True ):
        """
        Description:
            Check the number of installed intents.
        Optional:
            timeout - the timeout for pexcept
            noExit - If noExit, TestON will not exit if any except.
        Return:
            Returns main.TRUE only if the number of all installed intents are the same as total intents number
            , otherwise, returns main.FALSE.
        """

        try:
            cmd = "intents -s -j"

            # Check response if something wrong
            response = self.sendline( cmd, timeout=timeout, noExit=noExit )
            if response is None:
                return main.FALSE
            response = json.loads( response )

            # get total and installed number, see if they are match
            allState = response.get( 'all' )
            if allState.get( 'total' ) == allState.get( 'installed' ):
                main.log.info( 'Total Intents: {}   Installed Intents: {}'.format(
                    allState.get( 'total' ), allState.get( 'installed' ) ) )
                return main.TRUE
            main.log.info( 'Verified Intents failed Expected intents: {} installed intents: {}'.format(
                allState.get( 'total' ), allState.get( 'installed' ) ) )
            return main.FALSE

        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, response ) )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            if noExit:
                return main.FALSE
            else:
                main.cleanAndExit()
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": ONOS timeout" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            if noExit:
                return main.FALSE
            else:
                main.cleanAndExit()

    def flows( self, state="any", jsonFormat=True, timeout=60, noExit=False, noCore=False, device=""):
        """
        Optional:
            * jsonFormat: enable output formatting in json
            * noCore: suppress core flows
        Description:
            Obtain flows currently installed
        """
        try:
            cmdStr = "flows"
            if jsonFormat:
                cmdStr += " -j"
            if noCore:
                cmdStr += " -n"
            cmdStr += " " + state
            cmdStr += " " + device
            handle = self.sendline( cmdStr, timeout=timeout, noExit=noExit )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            if re.search( "Error:", handle ):
                main.log.error( self.name + ": flows() response: " +
                                str( handle ) )
            return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": ONOS timeout" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def checkFlowCount( self, min=0, timeout=60 ):
        count = self.getTotalFlowsNum( timeout=timeout )
        count = int( count ) if count else 0
        main.log.debug( "found {} flows".format( count ) )
        return count if ( count > min ) else False

    def checkFlowsState( self, isPENDING=True, timeout=60, noExit=False ):
        """
        Description:
            Check the if all the current flows are in ADDED state
            We check PENDING_ADD, PENDING_REMOVE, REMOVED, and FAILED flows,
            if the count of those states is 0, which means all current flows
            are in ADDED state, and return main.TRUE otherwise return main.FALSE
        Optional:
            * isPENDING:  whether the PENDING_ADD is also a correct status
        Return:
            returnValue - Returns main.TRUE only if all flows are in
                          ADDED state or PENDING_ADD if the isPENDING
                          parameter is set true, return main.FALSE otherwise.
        """
        try:
            states = [ "PENDING_ADD", "PENDING_REMOVE", "REMOVED", "FAILED" ]
            checkedStates = []
            statesCount = [ 0, 0, 0, 0 ]
            for s in states:
                rawFlows = self.flows( state=s, timeout = timeout )
                if rawFlows:
                    # if we didn't get flows or flows function return None, we should return
                    # main.Flase
                    checkedStates.append( json.loads( rawFlows ) )
                else:
                    return main.FALSE
            for i in range( len( states ) ):
                for c in checkedStates[ i ]:
                    try:
                        statesCount[ i ] += int( c.get( "flowCount" ) )
                    except TypeError:
                        main.log.exception( "Json object not as expected" )
                main.log.info( states[ i ] + " flows: " + str( statesCount[ i ] ) )

            # We want to count PENDING_ADD if isPENDING is true
            if isPENDING:
                if statesCount[ 1 ] + statesCount[ 2 ] + statesCount[ 3 ] > 0:
                    return main.FALSE
            else:
                if statesCount[ 0 ] + statesCount[ 1 ] + statesCount[ 2 ] + statesCount[ 3 ] > 0:
                    return main.FALSE
            return main.TRUE
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, rawFlows ) )
            return None

        except AssertionError:
            main.log.exception( "" )
            return None
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": ONOS timeout" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def pushTestIntents( self, ingress, egress, batchSize, offset="",
                         options="", timeout=10, background = False, noExit=False, getResponse=False ):
        """
        Description:
            Push a number of intents in a batch format to
            a specific point-to-point intent definition
        Required:
            * ingress: specify source dpid
            * egress: specify destination dpid
            * batchSize: specify number of intents to push
        Optional:
            * offset: the keyOffset is where the next batch of intents
                      will be installed
            * noExit: If set to True, TestON will not exit if any error when issus command
            * getResponse: If set to True, function will return ONOS response.

        Returns: If failed to push test intents, it will returen None,
                 if successful, return true.
                 Timeout expection will return None,
                 TypeError will return false
                 other expections will exit()
        """
        try:
            if background:
                back = "&"
            else:
                back = ""
            cmd = "push-test-intents {} {} {} {} {} {}".format( options,
                                                                ingress,
                                                                egress,
                                                                batchSize,
                                                                offset,
                                                                back )
            response = self.sendline( cmd, timeout=timeout, noExit=noExit )
            assert response is not None, "Error in sendline"
            assert "Command not found:" not in response, response
            main.log.info( response )
            if getResponse:
                return response

            # TODO: We should handle if there is failure in installation
            return main.TRUE

        except AssertionError:
            main.log.exception( "" )
            return None
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": ONOS timeout" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getTotalFlowsNum( self, timeout=60, noExit=False ):
        """
        Description:
            Get the number of ADDED flows.
        Return:
            The number of ADDED flows
            Or return None if any exceptions
        """

        try:
            # get total added flows number
            cmd = "flows -c added"
            rawFlows = self.sendline( cmd, timeout=timeout, noExit=noExit )
            if rawFlows:
                rawFlows = rawFlows.split( "\n" )
                totalFlows = 0
                for l in rawFlows:
                    totalFlows += int( l.split( "Count=" )[ 1 ] )
            else:
                main.log.warn( "Response not as expected!" )
                return None
            return totalFlows

        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected!".format( self.name ) )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            if not noExit:
                main.cleanAndExit()
            return None
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": ONOS timeout" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            if not noExit:
                main.cleanAndExit()
            return None

    def getTotalIntentsNum( self, timeout=60, noExit = False ):
        """
        Description:
            Get the total number of intents, include every states.
        Optional:
            noExit - If noExit, TestON will not exit if any except.
        Return:
            The number of intents
        """
        try:
            cmd = "summary -j"
            response = self.sendline( cmd, timeout=timeout, noExit=noExit )
            if response is None:
                return -1
            response = json.loads( response )
            return int( response.get( "intents" ) )
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, response ) )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            if noExit:
                return -1
            else:
                main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            if noExit:
                return -1
            else:
                main.cleanAndExit()

    def intentsEventsMetrics( self, jsonFormat=True ):
        """
        Description:Returns topology metrics
        Optional:
            * jsonFormat: enable json formatting of output
        """
        try:
            cmdStr = "intents-events-metrics"
            if jsonFormat:
                cmdStr += " -j"
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def topologyEventsMetrics( self, jsonFormat=True ):
        """
        Description:Returns topology metrics
        Optional:
            * jsonFormat: enable json formatting of output
        """
        try:
            cmdStr = "topology-events-metrics"
            if jsonFormat:
                cmdStr += " -j"
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            if handle:
                return handle
            elif jsonFormat:
                # Return empty json
                return '{}'
            else:
                return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    # Wrapper functions ****************
    # Wrapper functions use existing driver
    # functions and extends their use case.
    # For example, we may use the output of
    # a normal driver function, and parse it
    # using a wrapper function

    def getAllIntentsId( self ):
        """
        Description:
            Obtain all intent id's in a list
        """
        try:
            # Obtain output of intents function
            intentsStr = self.intents( jsonFormat=True )
            if intentsStr is None:
                raise TypeError
            # Convert to a dictionary
            intents = json.loads( intentsStr )
            intentIdList = []
            for intent in intents:
                intentIdList.append( intent[ 'id' ] )
            return intentIdList
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def flowAddedCount( self, deviceId, core=False ):
        """
        Determine the number of flow rules for the given device id that are
        in the added state
        Params:
            core: if True, only return the number of core flows added
        """
        try:
            if core:
                cmdStr = "flows any " + str( deviceId ) + " | " +\
                         "grep 'state=ADDED' | grep org.onosproject.core | wc -l"
            else:
                cmdStr = "flows any " + str( deviceId ) + " | " +\
                         "grep 'state=ADDED' | wc -l"
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def groupAddedCount( self, deviceId, core=False ):
        """
        Determine the number of group rules for the given device id that are
        in the added state
        Params:
            core: if True, only return the number of core groups added
        """
        try:
            if core:
                cmdStr = "groups any " + str( deviceId ) + " | " +\
                         "grep 'state=ADDED' | grep org.onosproject.core | wc -l"
            else:
                cmdStr = "groups any " + str( deviceId ) + " | " +\
                         "grep 'state=ADDED' | wc -l"
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def addStaticRoute( self, subnet, intf):
        """
        Adds a static route to onos.
        Params:
            subnet: The subnet reaching through this route
            intf: The interface this route is reachable through
        """
        try:
            cmdStr = "route-add " + subnet + " " + intf
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def checkGroupAddedCount( self, deviceId, expectedGroupCount=0, core=False, comparison=0):
        """
        Description:
            Check whether the number of groups for the given device id that
            are in ADDED state is bigger than minGroupCount.
        Required:
            * deviceId: device id to check the number of added group rules
        Optional:
            * minGroupCount: the number of groups to compare
            * core: if True, only check the number of core groups added
            * comparison: if 0, compare with greater than minFlowCount
            *             if 1, compare with equal to minFlowCount
        Return:
            Returns the number of groups if it is bigger than minGroupCount,
            returns main.FALSE otherwise.
        """
        count = self.groupAddedCount( deviceId, core )
        count = int( count ) if count else 0
        main.log.debug( "found {} groups".format( count ) )
        return count if ((count > expectedGroupCount) if (comparison == 0) else (count == expectedGroupCount)) else main.FALSE

    def getGroups( self, deviceId, groupType="any" ):
        """
        Retrieve groups from a specific device.
        deviceId: Id of the device from which we retrieve groups
        groupType: Type of group
        """
        try:
            groupCmd = "groups -t {0} any {1}".format( groupType, deviceId )
            handle = self.sendline( groupCmd )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def checkFlowAddedCount( self, deviceId, expectedFlowCount=0, core=False, comparison=0):
        """
        Description:
            Check whether the number of flow rules for the given device id that
            are in ADDED state is bigger than minFlowCount.
        Required:
            * deviceId: device id to check the number of added flow rules
        Optional:
            * minFlowCount: the number of flow rules to compare
            * core: if True, only check the number of core flows added
            * comparison: if 0, compare with greater than minFlowCount
            *             if 1, compare with equal to minFlowCount
        Return:
            Returns the number of flow rules if it is bigger than minFlowCount,
            returns main.FALSE otherwise.
        """
        count = self.flowAddedCount( deviceId, core )
        count = int( count ) if count else 0
        main.log.debug( "found {} flows".format( count ) )
        return count if ((count > expectedFlowCount) if (comparison == 0) else (count == expectedFlowCount)) else main.FALSE

    def getAllDevicesId( self ):
        """
        Use 'devices' function to obtain list of all devices
        and parse the result to obtain a list of all device
        id's. Returns this list. Returns empty list if no
        devices exist
        List is ordered sequentially

        This function may be useful if you are not sure of the
        device id, and wish to execute other commands using
        the ids. By obtaining the list of device ids on the fly,
        you can iterate through the list to get mastership, etc.
        """
        try:
            # Call devices and store result string
            devicesStr = self.devices( jsonFormat=False )
            idList = []

            if not devicesStr:
                main.log.info( "There are no devices to get id from" )
                return idList

            # Split the string into list by comma
            deviceList = devicesStr.split( "," )
            # Get temporary list of all arguments with string 'id='
            tempList = [ dev for dev in deviceList if "id=" in dev ]
            # Split list further into arguments before and after string
            # 'id='. Get the latter portion ( the actual device id ) and
            # append to idList
            for arg in tempList:
                idList.append( arg.split( "id=" )[ 1 ] )
            return idList

        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getAllNodesId( self ):
        """
        Uses 'nodes' function to obtain list of all nodes
        and parse the result of nodes to obtain just the
        node id's.
        Returns:
            list of node id's
        """
        try:
            nodesStr = self.nodes( jsonFormat=True )
            idList = []
            # Sample nodesStr output
            # id=local, address=127.0.0.1:9876, state=READY *
            if not nodesStr:
                main.log.info( "There are no nodes to get id from" )
                return idList
            nodesJson = json.loads( nodesStr )
            idList = [ node.get( 'id' ) for node in nodesJson ]
            return idList
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, nodesStr ) )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getDevice( self, dpid=None ):
        """
        Return the first device from the devices api whose 'id' contains 'dpid'
        Return None if there is no match
        """
        try:
            if dpid is None:
                return None
            else:
                dpid = dpid.replace( ':', '' )
                rawDevices = self.devices()
                devicesJson = json.loads( rawDevices )
                # search json for the device with dpid then return the device
                for device in devicesJson:
                    # print "%s in  %s?" % ( dpid, device[ 'id' ] )
                    if dpid in device[ 'id' ]:
                        return device
            return None
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, rawDevices ) )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getTopology( self, topologyOutput ):
        """
        Definition:
            Loads a json topology output
        Return:
            topology = current ONOS topology
        """
        import json
        try:
            # either onos:topology or 'topology' will work in CLI
            topology = json.loads( topologyOutput )
            main.log.debug( topology )
            return topology
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, topologyOutput ) )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def checkStatus( self, numoswitch, numolink = -1, numoctrl = -1, logLevel="info" ):
        """
        Checks the number of switches & links that ONOS sees against the
        supplied values. By default this will report to main.log, but the
        log level can be specific.

        Params: numoswitch = expected number of switches
                numolink = expected number of links
                numoctrl = expected number of controllers
                logLevel = level to log to.
                Currently accepts 'info', 'warn' and 'report'

        Returns: main.TRUE if the number of switches and links are correct,
                 main.FALSE if the number of switches and links is incorrect,
                 and main.ERROR otherwise
        """
        import json
        try:
            summary = self.summary()
            summary = json.loads( summary )
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, summary ) )
            return main.ERROR
        try:
            topology = self.getTopology( self.topology() )
            if topology == {} or topology is None or summary == {} or summary is None:
                return main.ERROR
            output = ""
            # Is the number of switches is what we expected
            devices = topology.get( 'devices', False )
            links = topology.get( 'links', False )
            nodes = summary.get( 'nodes', False )
            if devices is False or links is False or nodes is False:
                return main.ERROR
            switchCheck = ( int( devices ) == int( numoswitch ) )
            # Is the number of links is what we expected
            linkCheck = ( int( links ) == int( numolink ) ) or int( numolink ) == -1
            nodeCheck = ( int( nodes ) == int( numoctrl ) ) or int( numoctrl ) == -1
            if switchCheck and linkCheck and nodeCheck:
                # We expected the correct numbers
                output = output + "The number of links and switches match "\
                    + "what was expected"
                result = main.TRUE
            else:
                output = output + \
                    "The number of links and switches does not match " + \
                    "what was expected"
                result = main.FALSE
            output = output + "\n ONOS sees %i devices" % int( devices )
            output = output + " (%i expected) " % int( numoswitch )
            if int( numolink ) > 0:
                output = output + "and %i links " % int( links )
                output = output + "(%i expected)" % int( numolink )
            if int( numoctrl ) > 0:
                output = output + "and %i controllers " % int( nodes )
                output = output + "(%i expected)" % int( numoctrl )
            if logLevel == "report":
                main.log.report( output )
            elif logLevel == "warn":
                main.log.warn( output )
            else:
                main.log.info( output )
            return result
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def deviceRole( self, deviceId, onosNode, role="master" ):
        """
        Calls the device-role cli command.
        deviceId must be the id of a device as seen in the onos devices command
        onosNode is the ip of one of the onos nodes in the cluster
        role must be either master, standby, or none

        Returns:
            main.TRUE or main.FALSE based on argument verification and
            main.ERROR if command returns and error
        """
        try:
            if role.lower() == "master" or role.lower() == "standby" or\
                    role.lower() == "none":
                cmdStr = "device-role " +\
                    str( deviceId ) + " " +\
                    str( onosNode ) + " " +\
                    str( role )
                handle = self.sendline( cmdStr )
                assert handle is not None, "Error in sendline"
                assert "Command not found:" not in handle, handle
                if re.search( "Error", handle ):
                    # end color output to escape any colours
                    # from the cli
                    main.log.error( self.name + ": " +
                                    handle + '\033[0m' )
                    return main.ERROR
                return main.TRUE
            else:
                main.log.error( "Invalid 'role' given to device_role(). " +
                                "Value was '" + str( role ) + "'." )
                return main.FALSE
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def clusters( self, jsonFormat=True ):
        """
        Lists all topology clusters
        Optional argument:
            * jsonFormat - boolean indicating if you want output in json
        """
        try:
            cmdStr = "topo-clusters"
            if jsonFormat:
                cmdStr += " -j"
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def electionTestLeader( self ):
        """
        CLI command to get the current leader for the Election test application
        NOTE: Requires installation of the onos-app-election feature
        Returns: Node IP of the leader if one exists
                 None if none exists
                 Main.FALSE on error
        """
        try:
            cmdStr = "election-test-leader"
            response = self.sendline( cmdStr )
            assert response is not None, "Error in sendline"
            assert "Command not found:" not in response, response
            # Leader
            leaderPattern = "The\scurrent\sleader\sfor\sthe\sElection\s" +\
                "app\sis\s(?P<node>.+)\."
            nodeSearch = re.search( leaderPattern, response )
            if nodeSearch:
                node = nodeSearch.group( 'node' )
                main.log.info( "Election-test-leader on " + str( self.name ) +
                               " found " + node + " as the leader" )
                return node
            # no leader
            nullPattern = "There\sis\scurrently\sno\sleader\selected\sfor\s" +\
                "the\sElection\sapp"
            nullSearch = re.search( nullPattern, response )
            if nullSearch:
                main.log.info( "Election-test-leader found no leader on " +
                               self.name )
                return None
            # error
            main.log.error( self.name + ": Error in electionTestLeader on " + self.name +
                            ": " + "unexpected response" )
            main.log.error( repr( response ) )
            return main.FALSE
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def electionTestRun( self ):
        """
        CLI command to run for leadership of the Election test application.
        NOTE: Requires installation of the onos-app-election feature
        Returns: Main.TRUE on success
                 Main.FALSE on error
        """
        try:
            cmdStr = "election-test-run"
            response = self.sendline( cmdStr )
            assert response is not None, "Error in sendline"
            assert "Command not found:" not in response, response
            # success
            successPattern = "Entering\sleadership\selections\sfor\sthe\s" +\
                "Election\sapp."
            search = re.search( successPattern, response )
            if search:
                main.log.info( self.name + " entering leadership elections " +
                               "for the Election app." )
                return main.TRUE
            # error
            main.log.error( self.name + ": Error in electionTestRun on " + self.name +
                            ": " + "unexpected response" )
            main.log.error( repr( response ) )
            return main.FALSE
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def electionTestWithdraw( self ):
        """
         * CLI command to withdraw the local node from leadership election for
         * the Election test application.
         #NOTE: Requires installation of the onos-app-election feature
         Returns: Main.TRUE on success
                  Main.FALSE on error
        """
        try:
            cmdStr = "election-test-withdraw"
            response = self.sendline( cmdStr )
            assert response is not None, "Error in sendline"
            assert "Command not found:" not in response, response
            # success
            successPattern = "Withdrawing\sfrom\sleadership\selections\sfor" +\
                "\sthe\sElection\sapp."
            if re.search( successPattern, response ):
                main.log.info( self.name + " withdrawing from leadership " +
                               "elections for the Election app." )
                return main.TRUE
            # error
            main.log.error( self.name + ": Error in electionTestWithdraw on " +
                            self.name + ": " + "unexpected response" )
            main.log.error( repr( response ) )
            return main.FALSE
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getDevicePortsEnabledCount( self, dpid ):
        """
        Get the count of all enabled ports on a particular device/switch
        """
        try:
            dpid = str( dpid )
            cmdStr = "onos:ports -e " + dpid + " | wc -l"
            output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            if re.search( "No such device", output ):
                main.log.error( self.name + ": Error in getting ports" )
                return ( output, "Error" )
            return output
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return ( output, "Error" )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getDeviceLinksActiveCount( self, dpid ):
        """
        Get the count of all enabled ports on a particular device/switch
        """
        try:
            dpid = str( dpid )
            cmdStr = "onos:links " + dpid + " | grep ACTIVE | wc -l"
            output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            if re.search( "No such device", output ):
                main.log.error( self.name + ": Error in getting ports " )
                return ( output, "Error " )
            return output
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return ( output, "Error " )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getAllIntentIds( self ):
        """
        Return a list of all Intent IDs
        """
        try:
            cmdStr = "onos:intents | grep id="
            output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            if re.search( "Error", output ):
                main.log.error( self.name + ": Error in getting ports" )
                return ( output, "Error" )
            return output
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return ( output, "Error" )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def intentSummary( self ):
        """
        Returns a dictionary containing the current intent states and the count
        """
        try:
            intents = self.intents( )
            states = []
            for intent in json.loads( intents ):
                states.append( intent.get( 'state', None ) )
            out = [ ( i, states.count( i ) ) for i in set( states ) ]
            main.log.info( dict( out ) )
            return dict( out )
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, intents ) )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def leaders( self, jsonFormat=True ):
        """
        Returns the output of the leaders command.
        Optional argument:
            * jsonFormat - boolean indicating if you want output in json
        """
        try:
            cmdStr = "onos:leaders"
            if jsonFormat:
                cmdStr += " -j"
            output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            return output
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def leaderCandidates( self, jsonFormat=True ):
        """
        Returns the output of the leaders -c command.
        Optional argument:
            * jsonFormat - boolean indicating if you want output in json
        """
        try:
            cmdStr = "onos:leaders -c"
            if jsonFormat:
                cmdStr += " -j"
            output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            return output
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def specificLeaderCandidate( self, topic ):
        """
        Returns a list in format [leader,candidate1,candidate2,...] for a given
        topic parameter and an empty list if the topic doesn't exist
        If no leader is elected leader in the returned list will be "none"
        Returns None if there is a type error processing the json object
        """
        try:
            cmdStr = "onos:leaders -j"
            rawOutput = self.sendline( cmdStr )
            assert rawOutput is not None, "Error in sendline"
            assert "Command not found:" not in rawOutput, rawOutput
            output = json.loads( rawOutput )
            results = []
            for dict in output:
                if dict[ "topic" ] == topic:
                    leader = dict[ "leader" ]
                    candidates = re.split( ", ", dict[ "candidates" ][ 1:-1 ] )
                    results.append( leader )
                    results.extend( candidates )
            return results
        except AssertionError:
            main.log.exception( "" )
            return None
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, rawOutput ) )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def pendingMap( self, jsonFormat=True ):
        """
        Returns the output of the intent Pending map.
        """
        try:
            cmdStr = "onos:intents -p"
            if jsonFormat:
                cmdStr += " -j"
            output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            return output
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def partitions( self, candidates=False, jsonFormat=True ):
        """
        Returns the output of the raft partitions command for ONOS.
        """
        # Sample JSON
        # {
        #     "leader": "tcp://10.128.30.11:7238",
        #     "members": [
        #         "tcp://10.128.30.11:7238",
        #         "tcp://10.128.30.17:7238",
        #         "tcp://10.128.30.13:7238",
        #     ],
        #     "name": "p1",
        #     "term": 3
        # },
        try:
            cmdStr = "onos:partitions"
            if candidates:
                cmdStr += " -c"
            if jsonFormat:
                cmdStr += " -j"
            output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            return output
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def apps( self, summary=False, active=False, jsonFormat=True ):
        """
        Returns the output of the apps command for ONOS. This command lists
        information about installed ONOS applications
        """
        # Sample JSON object
        # [{"name":"org.onosproject.openflow","id":0,"version":"1.2.0",
        # "description":"ONOS OpenFlow protocol southbound providers",
        # "origin":"ON.Lab","permissions":"[]","featuresRepo":"",
        # "features":"[onos-openflow]","state":"ACTIVE"}]
        try:
            cmdStr = "onos:apps"
            if summary:
                cmdStr += " -s"
            if active:
                cmdStr += " -a"
            if jsonFormat:
                cmdStr += " -j"
            output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            assert "Error executing command" not in output, output
            return output
        # FIXME: look at specific exceptions/Errors
        except AssertionError:
            main.log.exception( self.name + ": Error in processing onos:app command." )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def appStatus( self, appName ):
        """
        Uses the onos:apps cli command to return the status of an application.
        Returns:
            "ACTIVE" - If app is installed and activated
            "INSTALLED" - If app is installed and deactivated
            "UNINSTALLED" - If app is not installed
            None - on error
        """
        try:
            if not isinstance( appName, types.StringType ):
                main.log.error( self.name + ".appStatus(): appName must be" +
                                " a string" )
                return None
            output = self.apps( jsonFormat=True )
            appsJson = json.loads( output )
            state = None
            for app in appsJson:
                if appName == app.get( 'name' ):
                    state = app.get( 'state' )
                    break
            if state == "ACTIVE" or state == "INSTALLED":
                return state
            elif state is None:
                main.log.warn( "{} app not found".format( appName ) )
                return "UNINSTALLED"
            elif state:
                main.log.error( "Unexpected state from 'onos:apps': " +
                                str( state ) )
                return state
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, output ) )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def app( self, appName, option ):
        """
        Interacts with the app command for ONOS. This command manages
        application inventory.
        """
        try:
            # Validate argument types
            valid = True
            if not isinstance( appName, types.StringType ):
                main.log.error( self.name + ".app(): appName must be a " +
                                "string" )
                valid = False
            if not isinstance( option, types.StringType ):
                main.log.error( self.name + ".app(): option must be a string" )
                valid = False
            if not valid:
                return main.FALSE
            # Validate Option
            option = option.lower()
            # NOTE: Install may become a valid option
            if option == "activate":
                pass
            elif option == "deactivate":
                pass
            elif option == "uninstall":
                pass
            else:
                # Invalid option
                main.log.error( "The ONOS app command argument only takes " +
                                "the values: (activate|deactivate|uninstall)" +
                                "; was given '" + option + "'" )
                return main.FALSE
            cmdStr = "onos:app " + option + " " + appName
            output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            if "Error executing command" in output:
                main.log.error( self.name + ": Error in processing onos:app command: " +
                                str( output ) )
                return main.FALSE
            elif "No such application" in output:
                main.log.error( "The application '" + appName +
                                "' is not installed in ONOS" )
                return main.FALSE
            elif "Command not found:" in output:
                main.log.error( self.name + ": Error in processing onos:app command: " +
                                str( output ) )
                return main.FALSE
            elif "Unsupported command:" in output:
                main.log.error( "Incorrect command given to 'app': " +
                                str( output ) )
            # NOTE: we may need to add more checks here
            # else: Command was successful
            # main.log.debug( "app response: " + repr( output ) )
            return main.TRUE
        except AssertionError:
            main.log.exception( self.name + ": AssertionError exception found" )
            return main.ERROR
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.ERROR
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def activateApp( self, appName, check=True ):
        """
        Activate an app that is already installed in ONOS
        appName is the hierarchical app name, not the feature name
        If check is True, method will check the status of the app after the
        command is issued
        Returns main.TRUE if the command was successfully sent
                main.FALSE if the cli responded with an error or given
                    incorrect input
        """
        try:
            if not isinstance( appName, types.StringType ):
                main.log.error( self.name + ".activateApp(): appName must be" +
                                " a string" )
                return main.FALSE
            status = self.appStatus( appName )
            if status == "INSTALLED":
                response = self.app( appName, "activate" )
                if check and response == main.TRUE:
                    for i in range( 10 ):  # try 10 times then give up
                        status = self.appStatus( appName )
                        if status == "ACTIVE":
                            return main.TRUE
                        else:
                            main.log.debug( "The state of application " +
                                            appName + " is " + status )
                            time.sleep( 1 )
                    return main.FALSE
                else:  # not 'check' or command didn't succeed
                    return response
            elif status == "ACTIVE":
                return main.TRUE
            elif status == "UNINSTALLED":
                main.log.error( self.name + ": Tried to activate the " +
                                "application '" + appName + "' which is not " +
                                "installed." )
            else:
                main.log.error( "Unexpected return value from appStatus: " +
                                str( status ) )
                return main.ERROR
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.ERROR
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def deactivateApp( self, appName, check=True ):
        """
        Deactivate an app that is already activated in ONOS
        appName is the hierarchical app name, not the feature name
        If check is True, method will check the status of the app after the
        command is issued
        Returns main.TRUE if the command was successfully sent
                main.FALSE if the cli responded with an error or given
                    incorrect input
        """
        try:
            if not isinstance( appName, types.StringType ):
                main.log.error( self.name + ".deactivateApp(): appName must " +
                                "be a string" )
                return main.FALSE
            status = self.appStatus( appName )
            if status == "INSTALLED":
                return main.TRUE
            elif status == "ACTIVE":
                response = self.app( appName, "deactivate" )
                if check and response == main.TRUE:
                    for i in range( 10 ):  # try 10 times then give up
                        status = self.appStatus( appName )
                        if status == "INSTALLED":
                            return main.TRUE
                        else:
                            time.sleep( 1 )
                    return main.FALSE
                else:  # not check or command didn't succeed
                    return response
            elif status == "UNINSTALLED":
                main.log.warn( self.name + ": Tried to deactivate the " +
                                "application '" + appName + "' which is not " +
                                "installed." )
                return main.TRUE
            else:
                main.log.error( "Unexpected return value from appStatus: " +
                                str( status ) )
                return main.ERROR
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.ERROR
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def uninstallApp( self, appName, check=True ):
        """
        Uninstall an app that is already installed in ONOS
        appName is the hierarchical app name, not the feature name
        If check is True, method will check the status of the app after the
        command is issued
        Returns main.TRUE if the command was successfully sent
                main.FALSE if the cli responded with an error or given
                    incorrect input
        """
        # TODO: check with Thomas about the state machine for apps
        try:
            if not isinstance( appName, types.StringType ):
                main.log.error( self.name + ".uninstallApp(): appName must " +
                                "be a string" )
                return main.FALSE
            status = self.appStatus( appName )
            if status == "INSTALLED":
                response = self.app( appName, "uninstall" )
                if check and response == main.TRUE:
                    for i in range( 10 ):  # try 10 times then give up
                        status = self.appStatus( appName )
                        if status == "UNINSTALLED":
                            return main.TRUE
                        else:
                            time.sleep( 1 )
                    return main.FALSE
                else:  # not check or command didn't succeed
                    return response
            elif status == "ACTIVE":
                main.log.warn( self.name + ": Tried to uninstall the " +
                                "application '" + appName + "' which is " +
                                "currently active." )
                response = self.app( appName, "uninstall" )
                if check and response == main.TRUE:
                    for i in range( 10 ):  # try 10 times then give up
                        status = self.appStatus( appName )
                        if status == "UNINSTALLED":
                            return main.TRUE
                        else:
                            time.sleep( 1 )
                    return main.FALSE
                else:  # not check or command didn't succeed
                    return response
            elif status == "UNINSTALLED":
                return main.TRUE
            else:
                main.log.error( "Unexpected return value from appStatus: " +
                                str( status ) )
                return main.ERROR
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.ERROR
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def appIDs( self, jsonFormat=True ):
        """
        Show the mappings between app id and app names given by the 'app-ids'
        cli command
        """
        try:
            cmdStr = "app-ids"
            if jsonFormat:
                cmdStr += " -j"
            output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            assert "Error executing command" not in output, output
            return output
        except AssertionError:
            main.log.exception( self.name + ": Error in processing onos:app-ids command." )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def appToIDCheck( self ):
        """
        This method will check that each application's ID listed in 'apps' is
        the same as the ID listed in 'app-ids'. The check will also check that
        there are no duplicate IDs issued. Note that an app ID should be
        a globaly unique numerical identifier for app/app-like features. Once
        an ID is registered, the ID is never freed up so that if an app is
        reinstalled it will have the same ID.

        Returns: main.TRUE  if the check passes and
                 main.FALSE if the check fails or
                 main.ERROR if there is some error in processing the test
        """
        try:
            # Grab IDs
            rawJson = self.appIDs( jsonFormat=True )
            if rawJson:
                ids = json.loads( rawJson )
            else:
                main.log.error( "app-ids returned nothing: " + repr( rawJson ) )
                return main.FALSE

            # Grab Apps
            rawJson = self.apps( jsonFormat=True )
            if rawJson:
                apps = json.loads( rawJson )
            else:
                main.log.error( "apps returned nothing:" + repr( rawJson ) )
                return main.FALSE

            result = main.TRUE
            for app in apps:
                appID = app.get( 'id' )
                if appID is None:
                    main.log.error( "Error parsing app: " + str( app ) )
                    result = main.FALSE
                appName = app.get( 'name' )
                if appName is None:
                    main.log.error( "Error parsing app: " + str( app ) )
                    result = main.FALSE
                # get the entry in ids that has the same appID
                current = filter( lambda item: item[ 'id' ] == appID, ids )
                if not current:  # if ids doesn't have this id
                    result = main.FALSE
                    main.log.error( "'app-ids' does not have the ID for " +
                                    str( appName ) + " that apps does." )
                    main.log.debug( "apps command returned: " + str( app ) +
                                    "; app-ids has: " + str( ids ) )
                elif len( current ) > 1:
                    # there is more than one app with this ID
                    result = main.FALSE
                    # We will log this later in the method
                elif not current[ 0 ][ 'name' ] == appName:
                    currentName = current[ 0 ][ 'name' ]
                    result = main.FALSE
                    main.log.error( "'app-ids' has " + str( currentName ) +
                                    " registered under id:" + str( appID ) +
                                    " but 'apps' has " + str( appName ) )
                else:
                    pass  # id and name match!

            # now make sure that app-ids has no duplicates
            idsList = []
            namesList = []
            for item in ids:
                idsList.append( item[ 'id' ] )
                namesList.append( item[ 'name' ] )
            if len( idsList ) != len( set( idsList ) ) or\
               len( namesList ) != len( set( namesList ) ):
                main.log.error( "'app-ids' has some duplicate entries: \n"
                                + json.dumps( ids,
                                              sort_keys=True,
                                              indent=4,
                                              separators=( ',', ': ' ) ) )
                result = main.FALSE
            return result
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, rawJson ) )
            return main.ERROR
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getCfg( self, component=None, propName=None, short=False,
                jsonFormat=True ):
        """
        Get configuration settings from onos cli
        Optional arguments:
            component - Optionally only list configurations for a specific
                        component. If None, all components with configurations
                        are displayed. Case Sensitive string.
            propName - If component is specified, propName option will show
                       only this specific configuration from that component.
                       Case Sensitive string.
            jsonFormat - Returns output as json. Note that this will override
                         the short option
            short - Short, less verbose, version of configurations.
                    This is overridden by the json option
        returns:
            Output from cli as a string or None on error
        """
        try:
            baseStr = "cfg"
            cmdStr = " get"
            componentStr = ""
            if component:
                componentStr += " " + component
                if propName:
                    componentStr += " " + propName
            if jsonFormat:
                baseStr += " -j"
            elif short:
                baseStr += " -s"
            output = self.sendline( baseStr + cmdStr + componentStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            assert "Error executing command" not in output, output
            return output
        except AssertionError:
            main.log.exception( self.name + ": Error in processing 'cfg get' command." )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def setCfg( self, component, propName, value=None, check=True ):
        """
        Set/Unset configuration settings from ONOS cli
        Required arguments:
            component - The case sensitive name of the component whose
                        property is to be set
            propName - The case sensitive name of the property to be set/unset
        Optional arguments:
            value - The value to set the property to. If None, will unset the
                    property and revert it to it's default value(if applicable)
            check - Boolean, Check whether the option was successfully set this
                    only applies when a value is given.
        returns:
            main.TRUE on success or main.FALSE on failure. If check is False,
            will return main.TRUE unless there is an error
        """
        try:
            baseStr = "cfg"
            cmdStr = " set " + str( component ) + " " + str( propName )
            if value is not None:
                cmdStr += " " + str( value )
            output = self.sendline( baseStr + cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            assert "Error executing command" not in output, output
            if value and check:
                results = self.getCfg( component=str( component ),
                                       propName=str( propName ),
                                       jsonFormat=True )
                # Check if current value is what we just set
                try:
                    jsonOutput = json.loads( results )
                    current = jsonOutput[ 'value' ]
                except ( TypeError, ValueError ):
                    main.log.exception( "Error parsing cfg output" )
                    main.log.error( "output:" + repr( results ) )
                    return main.FALSE
                if current == str( value ):
                    return main.TRUE
                return main.FALSE
            return main.TRUE
        except AssertionError:
            main.log.exception( self.name + ": Error in processing 'cfg set' command." )
            return main.FALSE
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, results ) )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def distPrimitivesSend( self, cmd ):
        """
        Function to handle sending cli commands for the distributed primitives test app

        This command will catch some exceptions and retry the command on some
        specific store exceptions.

        Required arguments:
            cmd - The command to send to the cli
        returns:
            string containing the cli output
            None on Error
        """
        try:
            output = self.sendline( cmd )
            try:
                assert output is not None, "Error in sendline"
                # TODO: Maybe make this less hardcoded
                # ConsistentMap Exceptions
                assert "org.onosproject.store.service" not in output
                # Node not leader
                assert "java.lang.IllegalStateException" not in output
            except AssertionError:
                main.log.error( self.name + ": Error in processing '" + cmd + "' " +
                                "command: " + str( output ) )
                retryTime = 30  # Conservative time, given by Madan
                main.log.info( "Waiting " + str( retryTime ) +
                               "seconds before retrying." )
                time.sleep( retryTime )  # Due to change in mastership
                output = self.sendline( cmd )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            assert "Error executing command" not in output, output
            main.log.info( self.name + ": " + output )
            return output
        except AssertionError:
            main.log.exception( self.name + ": Error in processing '" + cmd + "' command." )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def setTestAdd( self, setName, values ):
        """
        CLI command to add elements to a distributed set.
        Arguments:
            setName - The name of the set to add to.
            values - The value(s) to add to the set, space seperated.
        Example usages:
            setTestAdd( "set1", "a b c" )
            setTestAdd( "set2", "1" )
        returns:
            main.TRUE on success OR
            main.FALSE if elements were already in the set OR
            main.ERROR on error
        """
        try:
            cmdStr = "set-test-add " + str( setName ) + " " + str( values )
            output = self.distPrimitivesSend( cmdStr )
            positiveMatch = "\[(.*)\] was added to the set " + str( setName )
            negativeMatch = "\[(.*)\] was already in set " + str( setName )
            if re.search( positiveMatch, output ):
                return main.TRUE
            elif re.search( negativeMatch, output ):
                return main.FALSE
            else:
                main.log.error( self.name + ": setTestAdd did not" +
                                " match expected output" )
                main.log.debug( self.name + " actual: " + repr( output ) )
                return main.ERROR
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.ERROR
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def setTestRemove( self, setName, values, clear=False, retain=False ):
        """
        CLI command to remove elements from a distributed set.
        Required arguments:
            setName - The name of the set to remove from.
            values - The value(s) to remove from the set, space seperated.
        Optional arguments:
            clear - Clear all elements from the set
            retain - Retain only the  given values. (intersection of the
                     original set and the given set)
        returns:
            main.TRUE on success OR
            main.FALSE if the set was not changed OR
            main.ERROR on error
        """
        try:
            cmdStr = "set-test-remove "
            if clear:
                cmdStr += "-c " + str( setName )
            elif retain:
                cmdStr += "-r " + str( setName ) + " " + str( values )
            else:
                cmdStr += str( setName ) + " " + str( values )
            output = self.distPrimitivesSend( cmdStr )
            if clear:
                pattern = "Set " + str( setName ) + " cleared"
                if re.search( pattern, output ):
                    return main.TRUE
            elif retain:
                positivePattern = str( setName ) + " was pruned to contain " +\
                                  "only elements of set \[(.*)\]"
                negativePattern = str( setName ) + " was not changed by " +\
                                  "retaining only elements of the set " +\
                                  "\[(.*)\]"
                if re.search( positivePattern, output ):
                    return main.TRUE
                elif re.search( negativePattern, output ):
                    return main.FALSE
            else:
                positivePattern = "\[(.*)\] was removed from the set " +\
                                  str( setName )
                if ( len( values.split() ) == 1 ):
                    negativePattern = "\[(.*)\] was not in set " +\
                                      str( setName )
                else:
                    negativePattern = "No element of \[(.*)\] was in set " +\
                                      str( setName )
                if re.search( positivePattern, output ):
                    return main.TRUE
                elif re.search( negativePattern, output ):
                    return main.FALSE
            main.log.error( self.name + ": setTestRemove did not" +
                            " match expected output" )
            main.log.debug( self.name + " expected: " + pattern )
            main.log.debug( self.name + " actual: " + repr( output ) )
            return main.ERROR
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.ERROR
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def setTestGet( self, setName, values="" ):
        """
        CLI command to get the elements in a distributed set.
        Required arguments:
            setName - The name of the set to remove from.
        Optional arguments:
            values - The value(s) to check if in the set, space seperated.
        returns:
            main.ERROR on error OR
            A list of elements in the set if no optional arguments are
                supplied OR
            A tuple containing the list then:
                main.FALSE if the given values are not in the set OR
                main.TRUE if the given values are in the set OR
        """
        try:
            values = str( values ).strip()
            setName = str( setName ).strip()
            length = len( values.split() )
            containsCheck = None
            # Patterns to match
            setPattern = "\[(.*)\]"
            pattern = "Items in set " + setName + ":\r\n" + setPattern
            containsTrue = "Set " + setName + " contains the value " + values
            containsFalse = "Set " + setName + " did not contain the value " +\
                            values
            containsAllTrue = "Set " + setName + " contains the the subset " +\
                              setPattern
            containsAllFalse = "Set " + setName + " did not contain the the" +\
                               " subset " + setPattern

            cmdStr = "set-test-get "
            cmdStr += setName + " " + values
            output = self.distPrimitivesSend( cmdStr )
            if length == 0:
                match = re.search( pattern, output )
            else:  # if given values
                if length == 1:  # Contains output
                    patternTrue = pattern + "\r\n" + containsTrue
                    patternFalse = pattern + "\r\n" + containsFalse
                else:  # ContainsAll output
                    patternTrue = pattern + "\r\n" + containsAllTrue
                    patternFalse = pattern + "\r\n" + containsAllFalse
                matchTrue = re.search( patternTrue, output )
                matchFalse = re.search( patternFalse, output )
                if matchTrue:
                    containsCheck = main.TRUE
                    match = matchTrue
                elif matchFalse:
                    containsCheck = main.FALSE
                    match = matchFalse
                else:
                    main.log.error( self.name + " setTestGet did not match " +
                                    "expected output" )
                    main.log.debug( self.name + " expected: " + pattern )
                    main.log.debug( self.name + " actual: " + repr( output ) )
                    match = None
            if match:
                setMatch = match.group( 1 )
                if setMatch == '':
                    setList = []
                else:
                    setList = setMatch.split( ", " )
                if length > 0:
                    return ( setList, containsCheck )
                else:
                    return setList
            else:  # no match
                main.log.error( self.name + ": setTestGet did not" +
                                " match expected output" )
                main.log.debug( self.name + " expected: " + pattern )
                main.log.debug( self.name + " actual: " + repr( output ) )
                return main.ERROR
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.ERROR
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def setTestSize( self, setName ):
        """
        CLI command to get the elements in a distributed set.
        Required arguments:
            setName - The name of the set to remove from.
        returns:
            The integer value of the size returned or
            None on error
        """
        try:
            # TODO: Should this check against the number of elements returned
            #       and then return true/false based on that?
            setName = str( setName ).strip()
            # Patterns to match
            setPattern = "\[(.*)\]"
            pattern = "There are (\d+) items in set " + setName + ":\r\n" +\
                          setPattern
            cmdStr = "set-test-get -s "
            cmdStr += setName
            output = self.distPrimitivesSend( cmdStr )
            if output:
                match = re.search( pattern, output )
                if match:
                    setSize = int( match.group( 1 ) )
                    setMatch = match.group( 2 )
                    if len( setMatch.split() ) == setSize:
                        main.log.info( "The size returned by " + self.name +
                                       " matches the number of elements in " +
                                       "the returned set" )
                    else:
                        main.log.error( "The size returned by " + self.name +
                                        " does not match the number of " +
                                        "elements in the returned set." )
                    return setSize
            else:  # no match
                main.log.error( self.name + ": setTestGet did not" +
                                " match expected output" )
                main.log.debug( self.name + " expected: " + pattern )
                main.log.debug( self.name + " actual: " + repr( output ) )
                return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def counters( self, jsonFormat=True ):
        """
        Command to list the various counters in the system.
        returns:
            if jsonFormat, a string of the json object returned by the cli
            command
            if not jsonFormat, the normal string output of the cli command
            None on error
        """
        try:
            cmdStr = "counters"
            if jsonFormat:
                cmdStr += " -j"
            output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            assert "Error executing command" not in output, output
            main.log.info( self.name + ": " + output )
            return output
        except AssertionError:
            main.log.exception( self.name + ": Error in processing 'counters' command." )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def counterTestAddAndGet( self, counter, delta=1 ):
        """
        CLI command to add a delta to then get a distributed counter.
        Required arguments:
            counter - The name of the counter to increment.
        Optional arguments:
            delta - The long to add to the counter
        returns:
            integer value of the counter or
            None on Error
        """
        try:
            counter = str( counter )
            delta = int( delta )
            cmdStr = "counter-test-increment "
            cmdStr += counter
            if delta != 1:
                cmdStr += " " + str( delta )
            output = self.distPrimitivesSend( cmdStr )
            pattern = counter + " was updated to (-?\d+)"
            match = re.search( pattern, output )
            if match:
                return int( match.group( 1 ) )
            else:
                main.log.error( self.name + ": counterTestAddAndGet did not" +
                                " match expected output." )
                main.log.debug( self.name + " expected: " + pattern )
                main.log.debug( self.name + " actual: " + repr( output ) )
                return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def counterTestGetAndAdd( self, counter, delta=1 ):
        """
        CLI command to get a distributed counter then add a delta to it.
        Required arguments:
            counter - The name of the counter to increment.
        Optional arguments:
            delta - The long to add to the counter
        returns:
            integer value of the counter or
            None on Error
        """
        try:
            counter = str( counter )
            delta = int( delta )
            cmdStr = "counter-test-increment -g "
            cmdStr += counter
            if delta != 1:
                cmdStr += " " + str( delta )
            output = self.distPrimitivesSend( cmdStr )
            pattern = counter + " was updated to (-?\d+)"
            match = re.search( pattern, output )
            if match:
                return int( match.group( 1 ) )
            else:
                main.log.error( self.name + ": counterTestGetAndAdd did not" +
                                " match expected output." )
                main.log.debug( self.name + " expected: " + pattern )
                main.log.debug( self.name + " actual: " + repr( output ) )
                return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def valueTestGet( self, valueName ):
        """
        CLI command to get the value of an atomic value.
        Required arguments:
            valueName - The name of the value to get.
        returns:
            string value of the value or
            None on Error
        """
        try:
            valueName = str( valueName )
            cmdStr = "value-test "
            operation = "get"
            cmdStr = "value-test {} {}".format( valueName,
                                                operation )
            output = self.distPrimitivesSend( cmdStr )
            pattern = "(\w+)"
            match = re.search( pattern, output )
            if match:
                return match.group( 1 )
            else:
                main.log.error( self.name + ": valueTestGet did not" +
                                " match expected output." )
                main.log.debug( self.name + " expected: " + pattern )
                main.log.debug( self.name + " actual: " + repr( output ) )
                return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def valueTestSet( self, valueName, newValue ):
        """
        CLI command to set the value of an atomic value.
        Required arguments:
            valueName - The name of the value to set.
            newValue - The value to assign to the given value.
        returns:
            main.TRUE on success or
            main.ERROR on Error
        """
        try:
            valueName = str( valueName )
            newValue = str( newValue )
            operation = "set"
            cmdStr = "value-test {} {} {}".format( valueName,
                                                   operation,
                                                   newValue )
            output = self.distPrimitivesSend( cmdStr )
            if output is not None:
                return main.TRUE
            else:
                return main.ERROR
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.ERROR
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def valueTestCompareAndSet( self, valueName, oldValue, newValue ):
        """
        CLI command to compareAndSet the value of an atomic value.
        Required arguments:
            valueName - The name of the value.
            oldValue - Compare the current value of the atomic value to this
            newValue - If the value equals oldValue, set the value to newValue
        returns:
            main.TRUE on success or
            main.FALSE on failure or
            main.ERROR on Error
        """
        try:
            valueName = str( valueName )
            oldValue = str( oldValue )
            newValue = str( newValue )
            operation = "compareAndSet"
            cmdStr = "value-test {} {} {} {}".format( valueName,
                                                      operation,
                                                      oldValue,
                                                      newValue )
            output = self.distPrimitivesSend( cmdStr )
            pattern = "(\w+)"
            match = re.search( pattern, output )
            if match:
                result = match.group( 1 )
                if result == "true":
                    return main.TRUE
                elif result == "false":
                    return main.FALSE
            else:
                main.log.error( self.name + ": valueTestCompareAndSet did not" +
                                " match expected output." )
                main.log.debug( self.name + " expected: " + pattern )
                main.log.debug( self.name + " actual: " + repr( output ) )
                return main.ERROR
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.ERROR
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def valueTestGetAndSet( self, valueName, newValue ):
        """
        CLI command to getAndSet the value of an atomic value.
        Required arguments:
            valueName - The name of the value to get.
            newValue - The value to assign to the given value
        returns:
            string value of the value or
            None on Error
        """
        try:
            valueName = str( valueName )
            cmdStr = "value-test "
            operation = "getAndSet"
            cmdStr += valueName + " " + operation
            cmdStr = "value-test {} {} {}".format( valueName,
                                                   operation,
                                                   newValue )
            output = self.distPrimitivesSend( cmdStr )
            pattern = "(\w+)"
            match = re.search( pattern, output )
            if match:
                return match.group( 1 )
            else:
                main.log.error( self.name + ": valueTestGetAndSet did not" +
                                " match expected output." )
                main.log.debug( self.name + " expected: " + pattern )
                main.log.debug( self.name + " actual: " + repr( output ) )
                return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def valueTestDestroy( self, valueName ):
        """
        CLI command to destroy an atomic value.
        Required arguments:
            valueName - The name of the value to destroy.
        returns:
            main.TRUE on success or
            main.ERROR on Error
        """
        try:
            valueName = str( valueName )
            cmdStr = "value-test "
            operation = "destroy"
            cmdStr += valueName + " " + operation
            output = self.distPrimitivesSend( cmdStr )
            if output is not None:
                return main.TRUE
            else:
                return main.ERROR
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.ERROR
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def summary( self, jsonFormat=True, timeout=30 ):
        """
        Description: Execute summary command in onos
        Returns: json object ( summary -j ), returns main.FALSE if there is
        no output

        """
        try:
            cmdStr = "summary"
            if jsonFormat:
                cmdStr += " -j"
            handle = self.sendline( cmdStr, timeout=timeout )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            assert "Error:" not in handle, handle
            assert "Error executing" not in handle, handle
            if not handle:
                main.log.error( self.name + ": There is no output in " +
                                "summary command" )
                return main.FALSE
            return handle
        except AssertionError:
            main.log.exception( "{} Error in summary output:".format( self.name ) )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def transactionalMapGet( self, keyName ):
        """
        CLI command to get the value of a key in a consistent map using
        transactions. This a test function and can only get keys from the
        test map hard coded into the cli command
        Required arguments:
            keyName - The name of the key to get
        returns:
            The string value of the key or
            None on Error
        """
        try:
            keyName = str( keyName )
            cmdStr = "transactional-map-test-get "
            cmdStr += keyName
            output = self.distPrimitivesSend( cmdStr )
            pattern = "Key-value pair \(" + keyName + ", (?P<value>.+)\) found."
            if "Key " + keyName + " not found." in output:
                main.log.warn( output )
                return None
            else:
                match = re.search( pattern, output )
                if match:
                    return match.groupdict()[ 'value' ]
                else:
                    main.log.error( self.name + ": transactionlMapGet did not" +
                                    " match expected output." )
                    main.log.debug( self.name + " expected: " + pattern )
                    main.log.debug( self.name + " actual: " + repr( output ) )
                    return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def transactionalMapPut( self, numKeys, value ):
        """
        CLI command to put a value into 'numKeys' number of keys in a
        consistent map using transactions. This a test function and can only
        put into keys named 'Key#' of the test map hard coded into the cli command
        Required arguments:
            numKeys - Number of keys to add the value to
            value - The string value to put into the keys
        returns:
            A dictionary whose keys are the name of the keys put into the map
            and the values of the keys are dictionaries whose key-values are
            'value': value put into map and optionaly
            'oldValue': Previous value in the key or
            None on Error

            Example output
            { 'Key1': {'oldValue': 'oldTestValue', 'value': 'Testing'},
              'Key2': {'value': 'Testing'} }
        """
        try:
            numKeys = str( numKeys )
            value = str( value )
            cmdStr = "transactional-map-test-put "
            cmdStr += numKeys + " " + value
            output = self.distPrimitivesSend( cmdStr )
            newPattern = 'Created Key (?P<key>(\w)+) with value (?P<value>(.)+)\.'
            updatedPattern = "Put (?P<value>(.)+) into key (?P<key>(\w)+)\. The old value was (?P<oldValue>(.)+)\."
            results = {}
            for line in output.splitlines():
                new = re.search( newPattern, line )
                updated = re.search( updatedPattern, line )
                if new:
                    results[ new.groupdict()[ 'key' ] ] = { 'value': new.groupdict()[ 'value' ] }
                elif updated:
                    results[ updated.groupdict()[ 'key' ] ] = { 'value': updated.groupdict()[ 'value' ],
                                                                'oldValue': updated.groupdict()[ 'oldValue' ] }
                else:
                    main.log.error( self.name + ": transactionlMapGet did not" +
                                    " match expected output." )
                    main.log.debug( "{} expected: {!r} or {!r}".format( self.name,
                                                                        newPattern,
                                                                        updatedPattern ) )
                    main.log.debug( self.name + " actual: " + repr( output ) )
            return results
        except ( TypeError, AttributeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def maps( self, jsonFormat=True ):
        """
        Description: Returns result of onos:maps
        Optional:
            * jsonFormat: enable json formatting of output
        """
        try:
            cmdStr = "maps"
            if jsonFormat:
                cmdStr += " -j"
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getSwController( self, uri, jsonFormat=True ):
        """
        Descrition: Gets the controller information from the device
        """
        try:
            cmd = "device-controllers "
            if jsonFormat:
                cmd += "-j "
            response = self.sendline( cmd + uri )
            assert response is not None, "Error in sendline"
            assert "Command not found:" not in response, response
            return response
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def setSwController( self, uri, ip, proto="tcp", port="6653", jsonFormat=True ):
        """
        Descrition: sets the controller(s) for the specified device

        Parameters:
            Required: uri - String: The uri of the device(switch).
                      ip - String or List: The ip address of the controller.
                      This parameter can be formed in a couple of different ways.
                        VALID:
                        10.0.0.1 - just the ip address
                        tcp:10.0.0.1 - the protocol and the ip address
                        tcp:10.0.0.1:6653 - the protocol and port can be specified,
                                            so that you can add controllers with different
                                            protocols and ports
                        INVALID:
                        10.0.0.1:6653 - this is not supported by ONOS

            Optional: proto - The type of connection e.g. tcp, ssl. If a list of ips are given
                      port - The port number.
                      jsonFormat - If set ONOS will output in json NOTE: This is currently not supported

        Returns: main.TRUE if ONOS returns without any errors, otherwise returns main.FALSE
        """
        try:
            cmd = "device-setcontrollers"

            if jsonFormat:
                cmd += " -j"
            cmd += " " + uri
            if isinstance( ip, str ):
                ip = [ ip ]
            for item in ip:
                if ":" in item:
                    sitem = item.split( ":" )
                    if len( sitem ) == 3:
                        cmd += " " + item
                    elif "." in sitem[ 1 ]:
                        cmd += " {}:{}".format( item, port )
                    else:
                        main.log.error( "Malformed entry: " + item )
                        raise TypeError
                else:
                    cmd += " {}:{}:{}".format( proto, item, port )
            response = self.sendline( cmd )
            assert response is not None, "Error in sendline"
            assert "Command not found:" not in response, response
            if "Error" in response:
                main.log.error( response )
                return main.FALSE
            return main.TRUE
        except AssertionError:
            main.log.exception( "" )
            return main.FALSE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def removeDevice( self, device ):
        '''
        Description:
            Remove a device from ONOS by passing the uri of the device(s).
        Parameters:
            device - (str or list) the id or uri of the device ex. "of:0000000000000001"
        Returns:
            Returns main.FALSE if an exception is thrown or an error is present
            in the response. Otherwise, returns main.TRUE.
        NOTE:
            If a host cannot be removed, then this function will return main.FALSE
        '''
        try:
            if isinstance( device, str ):
                deviceStr = device
                device = []
                device.append( deviceStr )

            for d in device:
                time.sleep( 1 )
                response = self.sendline( "device-remove {}".format( d ) )
                assert response is not None, "Error in sendline"
                assert "Command not found:" not in response, response
                if "Error" in response:
                    main.log.warn( "Error for device: {}\nResponse: {}".format( d, response ) )
                    return main.FALSE
            return main.TRUE
        except AssertionError:
            main.log.exception( "" )
            return main.FALSE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def removeHost( self, host ):
        '''
        Description:
            Remove a host from ONOS by passing the id of the host(s)
        Parameters:
            hostId - (str or list) the id or mac of the host ex. "00:00:00:00:00:01"
        Returns:
            Returns main.FALSE if an exception is thrown or an error is present
            in the response. Otherwise, returns main.TRUE.
        NOTE:
            If a host cannot be removed, then this function will return main.FALSE
        '''
        try:
            if isinstance( host, str ):
                host = list( host )

            for h in host:
                time.sleep( 1 )
                response = self.sendline( "host-remove {}".format( h ) )
                assert response is not None, "Error in sendline"
                assert "Command not found:" not in response, response
                if "Error" in response:
                    main.log.warn( "Error for host: {}\nResponse: {}".format( h, response ) )
                    return main.FALSE
            return main.TRUE
        except AssertionError:
            main.log.exception( "" )
            return main.FALSE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def link( self, begin, end, state, timeout=30, showResponse=True ):
        '''
        Description:
            Bring link down or up in the null-provider.
        params:
            begin - (string) One end of a device or switch.
            end - (string) the other end of the device or switch
        returns:
            main.TRUE if no exceptions were thrown and no Errors are
            present in the resoponse. Otherwise, returns main.FALSE
        '''
        try:
            cmd = "null-link null:{} null:{} {}".format( begin, end, state )
            response = self.sendline( cmd, showResponse=showResponse, timeout=timeout )
            assert response is not None, "Error in sendline"
            assert "Command not found:" not in response, response
            if "Error" in response or "Failure" in response:
                main.log.error( response )
                return main.FALSE
            return main.TRUE
        except AssertionError:
            main.log.exception( "" )
            return main.FALSE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def portstate( self, dpid, port, state ):
        '''
        Description:
             Changes the state of port in an OF switch by means of the
             PORTSTATUS OF messages.
        params:
            dpid - (string) Datapath ID of the device. Ex: 'of:0000000000000102'
            port - (string) target port in the device. Ex: '2'
            state - (string) target state (enable or disable)
        returns:
            main.TRUE if no exceptions were thrown and no Errors are
            present in the resoponse. Otherwise, returns main.FALSE
        '''
        try:
            state = state.lower()
            assert state == 'enable' or state == 'disable', "Unknown state"
            cmd = "portstate {} {} {}".format( dpid, port, state )
            response = self.sendline( cmd, showResponse=True )
            assert response is not None, "Error in sendline"
            assert "Command not found:" not in response, response
            if "Error" in response or "Failure" in response:
                main.log.error( response )
                return main.FALSE
            return main.TRUE
        except AssertionError:
            main.log.exception( "" )
            return main.FALSE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def logSet( self, level="INFO", app="org.onosproject" ):
        """
        Set the logging level to lvl for a specific app
        returns main.TRUE on success
        returns main.FALSE if Error occurred
        if noExit is True, TestON will not exit, but clean up
        Available level: DEBUG, TRACE, INFO, WARN, ERROR
        Level defaults to INFO
        """
        try:
            self.handle.sendline( "log:set %s %s" % ( level, app ) )
            self.handle.expect( "onos>" )

            response = self.handle.before
            if re.search( "Error", response ):
                return main.FALSE
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception found" )
            main.cleanAndExit()
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getGraphDict( self, timeout=60, includeHost=False ):
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
        If includeHost == True, all hosts (and host-switch links) will be included
        in topology data.
        """
        graphDict = {}
        try:
            links = self.links()
            links = json.loads( links )
            devices = self.devices()
            devices = json.loads( devices )
            idToDevice = {}
            for device in devices:
                idToDevice[ device[ 'id' ] ] = device
            if includeHost:
                hosts = self.hosts()
                # FIXME: support 'includeHost' argument
            for link in links:
                nodeA = link[ 'src' ][ 'device' ]
                nodeB = link[ 'dst' ][ 'device' ]
                assert idToDevice[ nodeA ][ 'available' ] and idToDevice[ nodeB ][ 'available' ]
                if nodeA not in graphDict.keys():
                    graphDict[ nodeA ] = { 'edges': {},
                                           'dpid': idToDevice[ nodeA ][ 'id' ][ 3: ],
                                           'type': idToDevice[ nodeA ][ 'type' ],
                                           'available': idToDevice[ nodeA ][ 'available' ],
                                           'role': idToDevice[ nodeA ][ 'role' ],
                                           'mfr': idToDevice[ nodeA ][ 'mfr' ],
                                           'hw': idToDevice[ nodeA ][ 'hw' ],
                                           'sw': idToDevice[ nodeA ][ 'sw' ],
                                           'serial': idToDevice[ nodeA ][ 'serial' ],
                                           'chassisId': idToDevice[ nodeA ][ 'chassisId' ],
                                           'annotations': idToDevice[ nodeA ][ 'annotations' ]}
                else:
                    # Assert nodeB is not connected to any current links of nodeA
                    assert nodeB not in graphDict[ nodeA ][ 'edges' ].keys()
                graphDict[ nodeA ][ 'edges' ][ nodeB ] = { 'port': link[ 'src' ][ 'port' ],
                                                           'type': link[ 'type' ],
                                                           'state': link[ 'state' ] }
            return graphDict
        except ( TypeError, ValueError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except KeyError:
            main.log.exception( self.name + ": KeyError exception found" )
            return None
        except AssertionError:
            main.log.exception( self.name + ": AssertionError exception found" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return None

    def getIntentPerfSummary( self ):
        '''
        Send command to check intent-perf summary
        Returns: dictionary for intent-perf summary
                 if something wrong, function will return None
        '''
        cmd = "intent-perf -s"
        respDic = {}
        resp = self.sendline( cmd )
        assert resp is not None, "Error in sendline"
        assert "Command not found:" not in resp, resp
        try:
            # Generate the dictionary to return
            for l in resp.split( "\n" ):
                # Delete any white space in line
                temp = re.sub( r'\s+', '', l )
                temp = temp.split( ":" )
                respDic[ temp[ 0 ] ] = temp[ 1 ]

        except ( TypeError, ValueError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except KeyError:
            main.log.exception( self.name + ": KeyError exception found" )
            return None
        except AssertionError:
            main.log.exception( self.name + ": AssertionError exception found" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return None
        return respDic

    def logSearch( self, mode='all', searchTerm='', startLine='', logNum=1 ):
        """
        Searches the latest ONOS log file for the given search term and
        return a list that contains all the lines that have the search term.

        Arguments:
            searchTerm:
                The string to grep from the ONOS log.
            startLine:
                The term that decides which line is the start to search the searchTerm in
                the karaf log. For now, startTerm only works in 'first' mode.
            logNum:
                In some extreme cases, one karaf log is not big enough to contain all the
                information.Because of this, search mutiply logs is necessary to capture
                the right result. logNum is the number of karaf logs that we need to search
                the searchTerm.
            mode:
                all: return all the strings that contain the search term
                last: return the last string that contains the search term
                first: return the first string that contains the search term
                num: return the number of times that the searchTerm appears in the log
                total: return how many lines in karaf log
        """
        try:
            assert isinstance( searchTerm, str )
            # Build the log paths string
            logPath = '/opt/onos/log/karaf.log.'
            logPaths = '/opt/onos/log/karaf.log'
            for i in range( 1, logNum ):
                logPaths = logPath + str( i ) + " " + logPaths
            cmd = "cat " + logPaths
            if startLine:
                # 100000000 is just a extreme large number to make sure this function can
                # grep all the lines after startLine
                cmd = cmd + " | grep -A 100000000 \'" + startLine + "\'"
            if mode == 'all':
                cmd = cmd + " | grep \'" + searchTerm + "\'"
            elif mode == 'last':
                cmd = cmd + " | grep \'" + searchTerm + "\'" + " | tail -n 1"
            elif mode == 'first':
                cmd = cmd + " | grep \'" + searchTerm + "\'" + " | head -n 1"
            elif mode == 'num':
                cmd = cmd + " | grep -c \'" + searchTerm + "\'"
                num = self.sendline( cmd )
                return num
            elif mode == 'total':
                totalLines = self.sendline( "cat /opt/onos/log/karaf.log | wc -l" )
                return int( totalLines )
            else:
                main.log.error( self.name + " unsupported mode" )
                return main.ERROR
            before = self.sendline( cmd )
            before = before.splitlines()
            # make sure the returned list only contains the search term
            returnLines = [ line for line in before if searchTerm in line ]
            return returnLines
        except AssertionError:
            main.log.error( self.name + " searchTerm is not string type" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def vplsShow( self, jsonFormat=True ):
        """
        Description: Returns result of onos:vpls show, which should list the
                     configured VPLS networks and the assigned interfaces.
        Optional:
            * jsonFormat: enable json formatting of output
        Returns:
            The output of the command or None on error.
        """
        try:
            cmdStr = "vpls show"
            if jsonFormat:
                raise NotImplementedError
                cmdStr += " -j"
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except NotImplementedError:
            main.log.exception( self.name + ": Json output not supported" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def parseVplsShow( self ):
        """
        Parse the cli output of 'vpls show' into json output. This is required
        as there is currently no json output available.
        """
        try:
            output = []
            raw = self.vplsShow( jsonFormat=False )
            namePat = "VPLS name: (?P<name>\w+)"
            interfacesPat = "Associated interfaces: \[(?P<interfaces>.*)\]"
            encapPat = "Encapsulation: (?P<encap>\w+)"
            pattern = "\s+".join( [ namePat, interfacesPat, encapPat ] )
            mIter = re.finditer( pattern, raw )
            for match in mIter:
                item = {}
                item[ 'name' ] = match.group( 'name' )
                ifaces = match.group( 'interfaces' ).split( ', ' )
                if ifaces == [ "" ]:
                    ifaces = []
                item[ 'interfaces' ] = ifaces
                encap = match.group( 'encap' )
                if encap != 'NONE':
                    item[ 'encapsulation' ] = encap.lower()
                output.append( item )
            return output
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def vplsList( self, jsonFormat=True ):
        """
        Description: Returns result of onos:vpls list, which should list the
                     configured VPLS networks.
        Optional:
            * jsonFormat: enable json formatting of output
        """
        try:
            cmdStr = "vpls list"
            if jsonFormat:
                raise NotImplementedError
                cmdStr += " -j"
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except NotImplementedError:
            main.log.exception( self.name + ": Json output not supported" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def vplsCreate( self, network ):
        """
        CLI command to create a new VPLS network.
        Required arguments:
            network - String name of the network to create.
        returns:
            main.TRUE on success and main.FALSE on failure
        """
        try:
            network = str( network )
            cmdStr = "vpls create "
            cmdStr += network
            output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            assert "Error executing command" not in output, output
            assert "VPLS already exists:" not in output, output
            return main.TRUE
        except AssertionError:
            main.log.exception( "" )
            return main.FALSE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def vplsDelete( self, network ):
        """
        CLI command to delete a VPLS network.
        Required arguments:
            network - Name of the network to delete.
        returns:
            main.TRUE on success and main.FALSE on failure
        """
        try:
            network = str( network )
            cmdStr = "vpls delete "
            cmdStr += network
            output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            assert "Error executing command" not in output, output
            assert " not found" not in output, output
            assert "still updating" not in output, output
            return main.TRUE
        except AssertionError:
            main.log.exception( "" )
            return main.FALSE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def vplsAddIface( self, network, iface ):
        """
        CLI command to add an interface to a VPLS network.
        Required arguments:
            network - Name of the network to add the interface to.
            iface - The ONOS name for an interface.
        returns:
            main.TRUE on success and main.FALSE on failure
        """
        try:
            network = str( network )
            iface = str( iface )
            cmdStr = "vpls add-if "
            cmdStr += network + " " + iface
            output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            assert "Error executing command" not in output, output
            assert "already associated to network" not in output, output
            assert "Interface cannot be added." not in output, output
            assert "still updating" not in output, output
            return main.TRUE
        except AssertionError:
            main.log.exception( "" )
            return main.FALSE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def vplsRemIface( self, network, iface ):
        """
        CLI command to remove an interface from a VPLS network.
        Required arguments:
            network - Name of the network to remove the interface from.
            iface - Name of the interface to remove.
        returns:
            main.TRUE on success and main.FALSE on failure
        """
        try:
            iface = str( iface )
            cmdStr = "vpls rem-if "
            cmdStr += network + " " + iface
            output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            assert "Error executing command" not in output, output
            assert "is not configured" not in output, output
            assert "still updating" not in output, output
            return main.TRUE
        except AssertionError:
            main.log.exception( "" )
            return main.FALSE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def vplsClean( self ):
        """
        Description: Clears the VPLS app configuration.
        Returns: main.TRUE on success and main.FALSE on failure
        """
        try:
            cmdStr = "vpls clean"
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            assert "still updating" not in handle, handle
            return handle
        except AssertionError:
            main.log.exception( "" )
            return main.FALSE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def vplsSetEncap( self, network, encapType ):
        """
        CLI command to add an interface to a VPLS network.
        Required arguments:
            network - Name of the network to create.
            encapType - Type of encapsulation.
        returns:
            main.TRUE on success and main.FALSE on failure
        """
        try:
            network = str( network )
            encapType = str( encapType ).upper()
            assert encapType in [ "MPLS", "VLAN", "NONE" ], "Incorrect type"
            cmdStr = "vpls set-encap "
            cmdStr += network + " " + encapType
            output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            assert "Error executing command" not in output, output
            assert "already associated to network" not in output, output
            assert "Encapsulation type " not in output, output
            assert "still updating" not in output, output
            return main.TRUE
        except AssertionError:
            main.log.exception( "" )
            return main.FALSE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def interfaces( self, jsonFormat=True ):
        """
        Description: Returns result of interfaces command.
        Optional:
            * jsonFormat: enable json formatting of output
        Returns:
            The output of the command or None on error.
        """
        try:
            cmdStr = "interfaces"
            if jsonFormat:
                raise NotImplementedError
                cmdStr += " -j"
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except NotImplementedError:
            main.log.exception( self.name + ": Json output not supported" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getTimeStampFromLog( self, mode, searchTerm, splitTerm_before, splitTerm_after, startLine='', logNum=1 ):
        '''
        Get the timestamp of searchTerm from karaf log.

        Arguments:
            splitTerm_before and splitTerm_after:

                The terms that split the string that contains the timeStamp of
                searchTerm. For example, if that string is "xxxxxxxcreationTime =
                1419510501xxxxxx", then the splitTerm_before is "CreationTime = "
                and the splitTerm_after is "x"

            others:
                Please look at the "logsearch" Function in onosclidriver.py
        '''
        if logNum < 0:
            main.log.error( "Get wrong log number ")
            return main.ERROR
        lines = self.logSearch( mode=mode, searchTerm=searchTerm, startLine=startLine, logNum=logNum )
        if len( lines ) == 0:
            main.log.warn( "Captured timestamp string is empty" )
            return main.ERROR
        lines = lines[ 0 ]
        try:
            assert isinstance( lines, str )
            # get the target value
            line = lines.split( splitTerm_before )
            key = line[ 1 ].split( splitTerm_after )
            return int( key[ 0 ] )
        except IndexError:
            main.log.warn( "Index Error!" )
            return main.ERROR
        except AssertionError:
            main.log.warn( "Search Term Not Found " )
            return main.ERROR

    def workQueueAdd( self, queueName, value ):
        """
        CLI command to add a string to the specified Work Queue.
        This function uses the distributed primitives test app, which
        gives some cli access to distributed primitives for testing
        purposes only.

        Required arguments:
            queueName - The name of the queue to add to
            value - The value to add to the queue
        returns:
            main.TRUE on success, main.FALSE on failure and
            main.ERROR on error.
        """
        try:
            queueName = str( queueName )
            value = str( value )
            prefix = "work-queue-test"
            operation = "add"
            cmdStr = " ".join( [ prefix, queueName, operation, value ] )
            output = self.distPrimitivesSend( cmdStr )
            if "Invalid operation name" in output:
                main.log.warn( output )
                return main.ERROR
            elif "Done" in output:
                return main.TRUE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.ERROR
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def workQueueAddMultiple( self, queueName, value1, value2 ):
        """
        CLI command to add two strings to the specified Work Queue.
        This function uses the distributed primitives test app, which
        gives some cli access to distributed primitives for testing
        purposes only.

        Required arguments:
            queueName - The name of the queue to add to
            value1 - The first value to add to the queue
            value2 - The second value to add to the queue
        returns:
            main.TRUE on success, main.FALSE on failure and
            main.ERROR on error.
        """
        try:
            queueName = str( queueName )
            value1 = str( value1 )
            value2 = str( value2 )
            prefix = "work-queue-test"
            operation = "addMultiple"
            cmdStr = " ".join( [ prefix, queueName, operation, value1, value2 ] )
            output = self.distPrimitivesSend( cmdStr )
            if "Invalid operation name" in output:
                main.log.warn( output )
                return main.ERROR
            elif "Done" in output:
                return main.TRUE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.ERROR
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def workQueueTakeAndComplete( self, queueName, number=1 ):
        """
        CLI command to take a value from the specified Work Queue and compelte it.
        This function uses the distributed primitives test app, which
        gives some cli access to distributed primitives for testing
        purposes only.

        Required arguments:
            queueName - The name of the queue to add to
            number - The number of items to take and complete
        returns:
            main.TRUE on success, main.FALSE on failure and
            main.ERROR on error.
        """
        try:
            queueName = str( queueName )
            number = str( int( number ) )
            prefix = "work-queue-test"
            operation = "takeAndComplete"
            cmdStr = " ".join( [ prefix, queueName, operation, number ] )
            output = self.distPrimitivesSend( cmdStr )
            if "Invalid operation name" in output:
                main.log.warn( output )
                return main.ERROR
            elif "Done" in output:
                return main.TRUE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.ERROR
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def workQueueDestroy( self, queueName ):
        """
        CLI command to destroy the specified Work Queue.
        This function uses the distributed primitives test app, which
        gives some cli access to distributed primitives for testing
        purposes only.

        Required arguments:
            queueName - The name of the queue to add to
        returns:
            main.TRUE on success, main.FALSE on failure and
            main.ERROR on error.
        """
        try:
            queueName = str( queueName )
            prefix = "work-queue-test"
            operation = "destroy"
            cmdStr = " ".join( [ prefix, queueName, operation ] )
            output = self.distPrimitivesSend( cmdStr )
            if "Invalid operation name" in output:
                main.log.warn( output )
                return main.ERROR
            return main.TRUE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.ERROR
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def workQueueTotalPending( self, queueName ):
        """
        CLI command to get the Total Pending items of the specified Work Queue.
        This function uses the distributed primitives test app, which
        gives some cli access to distributed primitives for testing
        purposes only.

        Required arguments:
            queueName - The name of the queue to add to
        returns:
            The number of Pending items in the specified work queue or
            None on error
        """
        try:
            queueName = str( queueName )
            prefix = "work-queue-test"
            operation = "totalPending"
            cmdStr = " ".join( [ prefix, queueName, operation ] )
            output = self.distPrimitivesSend( cmdStr )
            pattern = r'\d+'
            if "Invalid operation name" in output:
                main.log.warn( output )
                return None
            else:
                match = re.search( pattern, output )
                return match.group( 0 )
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected; " + str( output ) )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def workQueueTotalCompleted( self, queueName ):
        """
        CLI command to get the Total Completed items of the specified Work Queue.
        This function uses the distributed primitives test app, which
        gives some cli access to distributed primitives for testing
        purposes only.

        Required arguments:
            queueName - The name of the queue to add to
        returns:
            The number of complete items in the specified work queue or
            None on error
        """
        try:
            queueName = str( queueName )
            prefix = "work-queue-test"
            operation = "totalCompleted"
            cmdStr = " ".join( [ prefix, queueName, operation ] )
            output = self.distPrimitivesSend( cmdStr )
            pattern = r'\d+'
            if "Invalid operation name" in output:
                main.log.warn( output )
                return None
            else:
                match = re.search( pattern, output )
                return match.group( 0 )
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected; " + str( output ) )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def workQueueTotalInProgress( self, queueName ):
        """
        CLI command to get the Total In Progress items of the specified Work Queue.
        This function uses the distributed primitives test app, which
        gives some cli access to distributed primitives for testing
        purposes only.

        Required arguments:
            queueName - The name of the queue to add to
        returns:
            The number of In Progress items in the specified work queue or
            None on error
        """
        try:
            queueName = str( queueName )
            prefix = "work-queue-test"
            operation = "totalInProgress"
            cmdStr = " ".join( [ prefix, queueName, operation ] )
            output = self.distPrimitivesSend( cmdStr )
            pattern = r'\d+'
            if "Invalid operation name" in output:
                main.log.warn( output )
                return None
            else:
                match = re.search( pattern, output )
                return match.group( 0 )
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected; " + str( output ) )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def events( self, args='-a' ):
        """
        Description: Returns events -a command output
        Optional:
            add other arguments
        """
        try:
            cmdStr = "events"
            if args:
                cmdStr += " " + args
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getMaster( self, deviceID ):
        """
            Description: Obtains current master using "roles" command for a specific deviceID
        """
        try:
            return str( self.getRole( deviceID )[ 'master' ] )
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def issu( self ):
        """
        Short summary of In-Service Software Upgrade status

        Returns the output of the cli command or None on Error
        """
        try:
            cmdStr = "issu"
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            assert "Unsupported command:" not in handle, handle
            return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def issuInit( self ):
        """
        Initiates an In-Service Software Upgrade

        Returns main.TRUE on success, main.ERROR on error, else main.FALSE
        """
        try:
            cmdStr = "issu init"
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            assert "Unsupported command:" not in handle, handle
            if "Initialized" in handle:
                return main.TRUE
            else:
                return main.FALSE
        except AssertionError:
            main.log.exception( "" )
            return main.ERROR
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.ERROR
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def issuUpgrade( self ):
        """
        Transitions stores to upgraded nodes

        Returns main.TRUE on success, main.ERROR on error, else main.FALSE
        """
        try:
            cmdStr = "issu upgrade"
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            assert "Unsupported command:" not in handle, handle
            if "Upgraded" in handle:
                return main.TRUE
            else:
                return main.FALSE
        except AssertionError:
            main.log.exception( "" )
            return main.ERROR
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.ERROR
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def issuCommit( self ):
        """
        Finalizes an In-Service Software Upgrade

        Returns main.TRUE on success, main.ERROR on error, else main.FALSE
        """
        try:
            cmdStr = "issu commit"
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            assert "Unsupported command:" not in handle, handle
            # TODO: Check the version returned by this command
            if "Committed version" in handle:
                return main.TRUE
            else:
                return main.FALSE
        except AssertionError:
            main.log.exception( "" )
            return main.ERROR
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.ERROR
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def issuRollback( self ):
        """
        Rolls back an In-Service Software Upgrade

        Returns main.TRUE on success, main.ERROR on error, else main.FALSE
        """
        try:
            cmdStr = "issu rollback"
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            assert "Unsupported command:" not in handle, handle
            # TODO: Check the version returned by this command
            if "Rolled back to version" in handle:
                return main.TRUE
            else:
                return main.FALSE
        except AssertionError:
            main.log.exception( "" )
            return main.ERROR
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.ERROR
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def issuReset( self ):
        """
        Resets the In-Service Software Upgrade status after a rollback

        Returns main.TRUE on success, main.ERROR on error, else main.FALSE
        """
        try:
            cmdStr = "issu reset"
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            assert "Unsupported command:" not in handle, handle
            # TODO: Check the version returned by this command
            if "Reset version" in handle:
                return main.TRUE
            else:
                return main.FALSE
        except AssertionError:
            main.log.exception( "" )
            return main.ERROR
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.ERROR
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def issuStatus( self ):
        """
        Status of an In-Service Software Upgrade

        Returns the output of the cli command or None on Error
        """
        try:
            cmdStr = "issu status"
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            assert "Unsupported command:" not in handle, handle
            return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def issuVersion( self ):
        """
        Get the version of an In-Service Software Upgrade

        Returns the output of the cli command or None on Error
        """
        try:
            cmdStr = "issu version"
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            assert "Unsupported command:" not in handle, handle
            return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def mcastJoin( self, sIP, groupIP, sPort, dPorts ):
        """
        Create a multicast route by calling 'mcast-join' command
        sIP: source IP of the multicast route
        groupIP: group IP of the multicast route
        sPort: source port (e.g. of:0000000000000001/3 ) of the multicast route
        dPorts: a list of destination ports of the multicast route
        Returns main.TRUE if mcast route is added; Otherwise main.FALSE
        """
        try:
            cmdStr = "mcast-join"
            cmdStr += " " + str( sIP )
            cmdStr += " " + str( groupIP )
            cmdStr += " " + str( sPort )
            assert isinstance( dPorts, list )
            for dPort in dPorts:
                cmdStr += " " + str( dPort )
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            assert "Unsupported command:" not in handle, handle
            assert "Error executing command" not in handle, handle
            if "Added the mcast route" in handle:
                return main.TRUE
            else:
                return main.FALSE
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def mcastDelete( self, sIP, groupIP, dPorts ):
        """
        Delete a multicast route by calling 'mcast-delete' command
        sIP: source IP of the multicast route
        groupIP: group IP of the multicast route
        dPorts: a list of destination ports of the multicast route
        Returns main.TRUE if mcast route is deleted; Otherwise main.FALSE
        """
        try:
            cmdStr = "mcast-delete"
            cmdStr += " " + str( sIP )
            cmdStr += " " + str( groupIP )
            assert isinstance( dPorts, list )
            for dPort in dPorts:
                cmdStr += " " + str( dPort )
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            assert "Unsupported command:" not in handle, handle
            assert "Error executing command" not in handle, handle
            if "Updated the mcast route" in handle:
                return main.TRUE
            else:
                return main.FALSE
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def mcastHostJoin( self, sAddr, gAddr, srcs, sinks ):
        """
        Create a multicast route by calling 'mcast-host-join' command
        sAddr: we can provide * for ASM or a specific address for SSM
        gAddr: specifies multicast group address
        srcs: a list of HostId of the sources e.g. ["00:AA:00:00:00:01/None"]
        sinks: a list of HostId of the sinks e.g. ["00:AA:00:00:01:05/40"]
        Returns main.TRUE if mcast route is added; Otherwise main.FALSE
        """
        try:
            cmdStr = "mcast-host-join"
            cmdStr += " -sAddr " + str( sAddr )
            cmdStr += " -gAddr " + str( gAddr )
            assert isinstance( srcs, list )
            for src in srcs:
                cmdStr += " -srcs " + str( src )
            assert isinstance( sinks, list )
            for sink in sinks:
                cmdStr += " -sinks " + str( sink )
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            assert "Unsupported command:" not in handle, handle
            assert "Error executing command" not in handle, handle
            if "Added the mcast route" in handle:
                return main.TRUE
            else:
                return main.FALSE
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def mcastHostDelete( self, sAddr, gAddr, host=None ):
        """
        Delete multicast sink(s) by calling 'mcast-host-delete' command
        sAddr: we can provide * for ASM or a specific address for SSM
        gAddr: specifies multicast group address
        host: HostId of the sink e.g. "00:AA:00:00:01:05/40",
               will delete the route if not specified
        Returns main.TRUE if the mcast sink is deleted; Otherwise main.FALSE
        """
        try:
            cmdStr = "mcast-host-delete"
            cmdStr += " -sAddr " + str( sAddr )
            cmdStr += " -gAddr " + str( gAddr )
            if host:
                cmdStr += " -h " + str( host )
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            assert "Unsupported command:" not in handle, handle
            assert "Error executing command" not in handle, handle
            if "Updated the mcast route" in handle:
                return main.TRUE
            elif "Deleted the mcast route" in handle:
                return main.TRUE
            else:
                return main.FALSE
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def mcastSinkDelete( self, sAddr, gAddr, sink=None ):
        """
        Delete multicast sink(s) by calling 'mcast-sink-delete' command
        sAddr: we can provide * for ASM or a specific address for SSM
        gAddr: specifies multicast group address
        host: HostId of the sink e.g. "00:AA:00:00:01:05/40",
               will delete the route if not specified
        Returns main.TRUE if the mcast sink is deleted; Otherwise main.FALSE
        """
        try:
            cmdStr = "mcast-sink-delete"
            cmdStr += " -sAddr " + str( sAddr )
            cmdStr += " -gAddr " + str( gAddr )
            if sink:
                cmdStr += " -s " + str( sink )
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            assert "Unsupported command:" not in handle, handle
            assert "Error executing command" not in handle, handle
            if "Updated the mcast route" in handle:
                return main.TRUE
            elif "Deleted the mcast route" in handle:
                return main.TRUE
            else:
                return main.FALSE
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def mcastSourceDelete( self, sAddr, gAddr, srcs=None ):
        """
        Delete multicast src(s) by calling 'mcast-source-delete' command
        sAddr: we can provide * for ASM or a specific address for SSM
        gAddr: specifies multicast group address
        srcs: a list of host IDs of the sources e.g. ["00:AA:00:00:01:05/40"],
              will delete the route if not specified
        Returns main.TRUE if mcast sink is deleted; Otherwise main.FALSE
        """
        try:
            cmdStr = "mcast-source-delete"
            cmdStr += " -sAddr " + str( sAddr )
            cmdStr += " -gAddr " + str( gAddr )
            if srcs:
                assert isinstance( srcs, list )
                for src in srcs:
                    cmdStr += " -src " + str( src )
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            assert "Unsupported command:" not in handle, handle
            assert "Error executing command" not in handle, handle
            if "Updated the mcast route" in handle:
                return main.TRUE
            elif "Deleted the mcast route" in handle:
                return main.TRUE
            else:
                return main.FALSE
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def netcfg( self, jsonFormat=True, args="" ):
        """
        Run netcfg cli command with given args
        """
        try:
            cmdStr = "netcfg"
            if jsonFormat:
                cmdStr = cmdStr + " -j"
            if args:
                cmdStr = cmdStr + " " + str( args )
            handle = self.sendline( cmdStr )
            assert handle is not None, "Error in sendline"
            assert "Command not found:" not in handle, handle
            assert "Unsupported command:" not in handle, handle
            assert "Error executing command" not in handle, handle
            return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def composeT3Command( self, sAddr, dAddr, ipv6=False, verbose=True, simple=False ):
        """
        Compose and return a list of t3-troubleshoot cli commands for given source and destination addresses
        Options:
            sAddr: IP address of the source host
            dAddr: IP address of the destination host
            ipv6: True if hosts are IPv6
            verbose: return verbose t3 output if True
            simple: compose command for t3-troubleshoot-simple if True
        """
        try:
            # Collect information of both hosts from onos
            hosts = self.hosts()
            hosts = json.loads( hosts )
            sHost = None
            dHost = None
            for host in hosts:
                if sAddr in host[ "ipAddresses" ]:
                    sHost = host
                elif dAddr in host[ "ipAddresses" ]:
                    dHost = host
                if sHost and dHost:
                    break
            assert sHost, "Not able to find host with IP {}".format( sAddr )
            cmdList = []
            if simple:
                assert dHost, "Not able to find host with IP {}".format( dAddr )
                cmdStr = "t3-troubleshoot-simple"
                if verbose:
                    cmdStr += " -vv"
                if ipv6:
                    cmdStr += " -et ipv6"
                cmdStr += " {}/{} {}/{}".format( sHost[ "mac" ], sHost[ "vlan" ], dHost[ "mac" ], dHost[ "vlan" ] )
                cmdList.append( cmdStr )
            else:
                for location in sHost[ "locations" ]:
                    cmdStr = "t3-troubleshoot"
                    if verbose:
                        cmdStr += " -vv"
                    if ipv6:
                        cmdStr += " -et ipv6"
                    cmdStr += " -s " + str( sAddr )
                    cmdStr += " -sp " + str( location[ "elementId" ] ) + "/" + str( location[ "port" ] )
                    cmdStr += " -sm " + str( sHost[ "mac" ] )
                    if sHost[ "vlan" ] != "None":
                        cmdStr += " -vid " + sHost[ "vlan" ]
                    cmdStr += " -d " + str( dAddr )
                    netcfg = self.netcfg( args="devices {}".format( location[ "elementId" ] ) )
                    netcfg = json.loads( netcfg )
                    assert netcfg, "Failed to get netcfg"
                    cmdStr += " -dm " + str( netcfg[ "segmentrouting" ][ "routerMac" ] )
                    cmdList.append( cmdStr )
            return cmdList
        except AssertionError:
            main.log.exception( "" )
            return None
        except ( KeyError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def t3( self, sAddr, dAddr, ipv6=False ):
        """
        Run t3-troubleshoot cli commands for all posible routes given source and destination addresses
        Options:
            sAddr: IP address of the source host
            dAddr: IP address of the destination host
        """
        try:
            cmdList = self.composeT3Command( sAddr, dAddr, ipv6 )
            assert cmdList is not None, "composeT3Command returned None"
            t3Output = ""
            for cmdStr in cmdList:
                handle = self.sendline( cmdStr )
                assert handle is not None, "Error in sendline"
                assert "Command not found:" not in handle, handle
                assert "Unsupported command:" not in handle, handle
                assert "Error executing command" not in handle, handle
                assert "Tracing packet" in handle
                t3Output += handle
            return t3Output
        except AssertionError:
            main.log.exception( "" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()
