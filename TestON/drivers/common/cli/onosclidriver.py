#!/usr/bin/env python

"""
This driver enters the onos> prompt to issue commands.

Please follow the coding style demonstrated by existing
functions and document properly.

If you are a contributor to the driver, please
list your email here for future contact:

jhall@onlab.us
andrew@onlab.us
shreya@onlab.us

OCT 13 2014

"""
import pexpect
import re
import json
import types
import time
import os
from drivers.common.clidriver import CLI


class OnosCliDriver( CLI ):

    def __init__( self ):
        """
        Initialize client
        """
        self.name = None
        self.home = None
        self.handle = None
        super( CLI, self ).__init__()

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
                    self.home = self.options[ 'home' ]
                    break
            if self.home is None or self.home == "":
                self.home = "~/onos"

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
            self.handle.expect( "\$" )
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
                    self.handle.expect( "\$" )
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
                i = self.handle.expect( [ "onos>", "\$", pexpect.TIMEOUT ],
                                        timeout=10 )
                if i == 0:  # In ONOS CLI
                    self.handle.sendline( "logout" )
                    j = self.handle.expect( [ "\$",
                                              "Command not found:",
                                              pexpect.TIMEOUT ] )
                    if j == 0:  # Successfully logged out
                        return main.TRUE
                    elif j == 1 or j == 2:
                        # ONOS didn't fully load, and logout command isn't working
                        # or the command timed out
                        self.handle.send( "\x04" )  # send ctrl-d
                        try:
                            self.handle.expect( "\$" )
                        except pexpect.TIMEOUT:
                            main.log.error( "ONOS did not respond to 'logout' or CTRL-d" )
                        return main.TRUE
                    else: # some other output
                        main.log.warn( "Unknown repsonse to logout command: '{}'",
                                       repr( self.handle.before ) )
                        return main.FALSE
                elif i == 1:  # not in CLI
                    return main.TRUE
                elif i == 3:  # Timeout
                    return main.FALSE
            else:
                return main.TRUE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": eof exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except ValueError:
            main.log.error( self.name +
                            "ValueError exception in logout method" )
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def setCell( self, cellname ):
        """
        Calls 'cell <name>' to set the environment variables on ONOSbench

        Before issuing any cli commands, set the environment variable first.
        """
        try:
            if not cellname:
                main.log.error( "Must define cellname" )
                main.cleanup()
                main.exit()
            else:
                self.handle.sendline( "cell " + str( cellname ) )
                # Expect the cellname in the ONOSCELL variable.
                # Note that this variable name is subject to change
                #   and that this driver will have to change accordingly
                self.handle.expect(str(cellname))
                handleBefore = self.handle.before
                handleAfter = self.handle.after
                # Get the rest of the handle
                self.handle.sendline("")
                self.handle.expect("\$")
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def startOnosCli( self, ONOSIp, karafTimeout="",
                      commandlineTimeout=10, onosStartTimeout=60 ):
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
            self.handle.sendline( "" )
            x = self.handle.expect( [
                "\$", "onos>" ], commandlineTimeout)

            if x == 1:
                main.log.info( "ONOS cli is already running" )
                return main.TRUE

            # Wait for onos start ( -w ) and enter onos cli
            self.handle.sendline( "onos -w " + str( ONOSIp ) )
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
                    self.handle.expect( "\$" )
                    self.handle.sendline( "onos -w " + str( ONOSIp ) )
                    self.handle.expect( "onos>" )
                return main.TRUE
            else:
                # If failed, send ctrl+c to process and try again
                main.log.info( "Starting CLI failed. Retrying..." )
                self.handle.send( "\x03" )
                self.handle.sendline( "onos -w " + str( ONOSIp ) )
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
                        self.handle.expect( "\$" )
                        self.handle.sendline( "onos -w " + str( ONOSIp ) )
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
                "\$", "onos>" ], commandlineTimeout)

            if x == 1:
                main.log.info( "ONOS cli is already running" )
                return main.TRUE

            # Wait for onos start ( -w ) and enter onos cli
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
                    self.handle.expect( "\$" )
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
                        self.handle.expect( "\$" )
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def log( self, cmdStr, level="",noExit=False):
        """
            log  the commands in the onos CLI.
            returns main.TRUE on success
            returns main.FALSE if Error occurred
            if noExit is True, TestON will not exit, but clean up
            Available level: DEBUG, TRACE, INFO, WARN, ERROR
            Level defaults to INFO
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
                main.cleanup()
                main.exit()
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            if noExit:
                main.cleanup()
                return None
            else:
                main.cleanup()
                main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            if noExit:
                main.cleanup()
                return None
            else:
                main.cleanup()
                main.exit()

    def sendline( self, cmdStr, showResponse=False, debug=False, timeout=10, noExit=False ):
        """
        Send a completely user specified string to
        the onos> prompt. Use this function if you have
        a very specific command to send.

        if noExit is True, TestON will not exit, but clean up

        Warning: There are no sanity checking to commands
        sent using this method.

        """
        try:
            # Try to reconnect if disconnected from cli
            self.handle.sendline( "" )
            i = self.handle.expect( [ "onos>", "\$", pexpect.TIMEOUT ] )
            if i == 1:
                main.log.error( self.name + ": onos cli session closed. ")
                if self.onosIp:
                    main.log.warn( "Trying to reconnect " + self.onosIp )
                    reconnectResult = self.startOnosCli( self.onosIp )
                    if reconnectResult:
                        main.log.info( self.name + ": onos cli session reconnected." )
                    else:
                        main.log.error( self.name + ": reconnection failed." )
                        main.cleanup()
                        main.exit()
                else:
                    main.cleanup()
                    main.exit()
            if i == 2:
                self.handle.sendline( "" )
                self.handle.expect( "onos>" )

            if debug:
                # NOTE: This adds and average of .4 seconds per call
                logStr = "\"Sending CLI command: '" + cmdStr + "'\""
                self.log( logStr,noExit=noExit )
            self.handle.sendline( cmdStr )
            i = self.handle.expect( ["onos>", "\$"], timeout )
            response = self.handle.before
            # TODO: do something with i
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
            if debug:
                main.log.debug( self.name + ": split output" )
                for r in output:
                    main.log.debug( self.name + ": " + repr( r ) )
            output = output[1].strip()
            if showResponse:
                main.log.info( "Response from ONOS: {}".format( output ) )
            return output
        except pexpect.TIMEOUT:
            main.log.error( self.name + ":ONOS timeout" )
            if debug:
                main.log.debug( self.handle.before )
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
                main.cleanup()
                return None
            else:
                main.cleanup()
                main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            if noExit:
                main.cleanup()
                return None
            else:
                main.cleanup()
                main.exit()

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
                main.log.error( "Error in adding node" )
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
                main.log.error( "Error in removing node" )
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def nodes( self, jsonFormat=True):
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def deviceRemove( self, deviceId ):
        """
        Removes particular device from storage

        TODO: refactor this function
        """
        try:
            cmdStr = "device-remove " + str( deviceId )
            handle = self.sendline( cmdStr )
            assert "Command not found:" not in handle, handle
            if re.search( "Error", handle ):
                main.log.error( "Error in removing device" )
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def devices( self, jsonFormat=True ):
        """
        Lists all infrastructure devices or switches
        Optional argument:
            * jsonFormat - boolean indicating if you want output in json
        """
        try:
            cmdStr = "devices"
            if jsonFormat:
                cmdStr += " -j"
            handle = self.sendline( cmdStr )
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def balanceMasters( self ):
        """
        This balances the devices across all controllers
        by issuing command: 'onos> onos:balance-masters'
        If required this could be extended to return devices balanced output.
        """
        try:
            cmdStr = "onos:balance-masters"
            handle = self.sendline( cmdStr )
            assert "Command not found:" not in handle, handle
            if re.search( "Error", handle ):
                main.log.error( "Error in balancing masters" )
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.log.info( "Mastership balanced between " \
                            + str( len(masters) ) + " masters" )
            return main.TRUE
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, mastersOutput ) )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def ports( self, jsonFormat=True ):
        """
        Lists all ports
        Optional argument:
            * jsonFormat - boolean indicating if you want output in json
        """
        try:
            cmdStr = "ports"
            if jsonFormat:
                cmdStr += " -j"
            handle = self.sendline( cmdStr )
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def paths( self, srcId, dstId ):
        """
        Returns string of paths, and the cost.
        Issues command: onos:paths <src> <dst>
        """
        try:
            cmdStr = "onos:paths " + str( srcId ) + " " + str( dstId )
            handle = self.sendline( cmdStr )
            assert "Command not found:" not in handle, handle
            if re.search( "Error", handle ):
                main.log.error( "Error in getting paths" )
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.log.exception( "Error in processing '" + cmdStr + "' " +
                                "command: " + str( handle ) )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def addHostIntent( self, hostIdOne, hostIdTwo, vlanId="", setVlan="" ):
        """
        Required:
            * hostIdOne: ONOS host id for host1
            * hostIdTwo: ONOS host id for host2
        Optional:
            * vlanId: specify a VLAN id for the intent
            * setVlan: specify a VLAN id treatment
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
            cmdStr += str( hostIdOne ) + " " + str( hostIdTwo )
            handle = self.sendline( cmdStr )
            assert "Command not found:" not in handle, handle
            if re.search( "Error", handle ):
                main.log.error( "Error in adding Host intent" )
                main.log.debug( "Response from ONOS was: " + repr( handle ) )
                return None
            else:
                main.log.info( "Host intent installed between " +
                               str( hostIdOne ) + " and " + str( hostIdTwo ) )
                match = re.search('id=0x([\da-f]+),', handle)
                if match:
                    return match.group()[3:-1]
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            assert "Command not found:" not in handle, handle
            # If error, return error message
            if re.search( "Error", handle ):
                main.log.error( "Error in adding Optical intent" )
                return None
            else:
                main.log.info( "Optical intent installed between " +
                               str( ingressDevice ) + " and " +
                               str( egressDevice ) )
                match = re.search('id=0x([\da-f]+),', handle)
                if match:
                    return match.group()[3:-1]
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            ipProto="",
            ipSrc="",
            ipDst="",
            tcpSrc="",
            tcpDst="",
            vlanId="",
            setVlan="" ):
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
            assert "Command not found:" not in handle, handle
            # If error, return error message
            if re.search( "Error", handle ):
                main.log.error( "Error in adding point-to-point intent" )
                return None
            else:
                # TODO: print out all the options in this message?
                main.log.info( "Point-to-point intent installed between " +
                               str( ingressDevice ) + " and " +
                               str( egressDevice ) )
                match = re.search('id=0x([\da-f]+),', handle)
                if match:
                    return match.group()[3:-1]
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            partial=False ):
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
            assert "Command not found:" not in handle, handle
            # If error, return error message
            if re.search( "Error", handle ):
                main.log.error( "Error in adding multipoint-to-singlepoint " +
                                "intent" )
                return None
            else:
                match = re.search('id=0x([\da-f]+),', handle)
                if match:
                    return match.group()[3:-1]
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            partial=False ):
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
            assert "Command not found:" not in handle, handle
            # If error, return error message
            if re.search( "Error", handle ):
                main.log.error( "Error in adding singlepoint-to-multipoint " +
                                "intent" )
                return None
            else:
                match = re.search('id=0x([\da-f]+),', handle)
                if match:
                    return match.group()[3:-1]
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            priority=""):
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
            assert "Command not found:" not in handle, handle
            # If error, return error message
            if re.search( "Error", handle ):
                main.log.error( "Error in adding mpls intent" )
                return None
            else:
                # TODO: print out all the options in this message?
                main.log.info( "MPLS intent installed between " +
                               str( ingressDevice ) + " and " +
                               str( egressDevice ) )
                match = re.search('id=0x([\da-f]+),', handle)
                if match:
                    return match.group()[3:-1]
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            assert "Command not found:" not in handle, handle
            if re.search( "Error", handle ):
                main.log.error( "Error in removing intent" )
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            assert "Command not found:" not in handle, handle
            if re.search( "Error", handle ):
                main.log.error( "Error in removing intent" )
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def purgeWithdrawnIntents( self ):
        """
        Purges all WITHDRAWN Intents
        """
        try:
            cmdStr = "purge-intents"
            handle = self.sendline( cmdStr )
            assert "Command not found:" not in handle, handle
            if re.search( "Error", handle ):
                main.log.error( "Error in purging intents" )
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def ipv4RouteNumber( self ):
        """
        NOTE: This method should be used after installing application:
              onos-app-sdnip
        Description:
            Obtain the total IPv4 routes number in the system
        """
        try:
            cmdStr = "routes -s -j"
            handle = self.sendline( cmdStr )
            assert "Command not found:" not in handle, handle
            jsonResult = json.loads( handle )
            return jsonResult['totalRoutes4']
        except AssertionError:
            main.log.exception( "" )
            return None
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, handle ) )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def intents( self, jsonFormat = True, summary = False, **intentargs):
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
            handle = self.sendline( cmdStr )
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def getIntentState(self, intentsId, intentsJson=None):
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
                               " on the list" )
                return state
            elif isinstance( intentsId, types.ListType ):
                dictList = []
                for i in xrange( len( intentsId ) ):
                    stateDict = {}
                    for intents in parsedIntentsJson:
                        if intentsId[ i ] == intents[ 'id' ]:
                            stateDict[ 'state' ] = intents[ 'state' ]
                            stateDict[ 'id' ] = intentsId[ i ]
                            dictList.append( stateDict )
                            break
                if len( intentsId ) != len( dictList ):
                    main.log.info( "Cannot find some of the intent ID state" )
                return dictList
            else:
                main.log.info( "Invalid intents ID entry" )
                return None
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, rawJson ) )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            Returns main.TRUE only if all intent are the same as expected states
            , otherwise, returns main.FALSE.
        """
        try:
            # Generating a dictionary: intent id as a key and state as value
            returnValue = main.TRUE
            intentsDict = self.getIntentState( intentsId )
            if len( intentsId ) != len( intentsDict ):
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            if len( intentDict ) != len( intentDictONOS ):
                main.log.info( self.name + ": expected intent count does not match that in ONOS, " +
                               str( len( intentDict ) ) + " expected and " +
                               str( len( intentDictONOS ) ) + " actual" )
                return main.FALSE
            returnValue = main.TRUE
            for intentID in intentDict.keys():
                if not intentID in intentDictONOS.keys():
                    main.log.debug( self.name + ": intent ID - " + intentID + " is not in ONOS" )
                    returnValue = main.FALSE
                elif intentDict[ intentID ] != intentDictONOS[ intentID ]:
                    main.log.debug( self.name + ": intent ID - " + intentID +
                                    " expected state is " + intentDict[ intentID ] +
                                    " but actual state is " + intentDictONOS[ intentID ] )
                    returnValue = main.FALSE
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def checkIntentSummary( self, timeout=60 ):
        """
        Description:
            Check the number of installed intents.
        Optional:
            timeout - the timeout for pexcept
        Return:
            Returns main.TRUE only if the number of all installed intents are the same as total intents number
            , otherwise, returns main.FALSE.
        """

        try:
            cmd = "intents -s -j"

            # Check response if something wrong
            response = self.sendline( cmd, timeout=timeout )
            if response == None:
                return main.FALSE
            response = json.loads( response )

            # get total and installed number, see if they are match
            allState = response.get( 'all' )
            if allState.get('total') == allState.get('installed'):
                main.log.info( 'Total Intents: {}   Installed Intents: {}'.format( allState.get('total'), allState.get('installed') ) )
                return main.TRUE
            main.log.info( 'Verified Intents failed Excepte intetnes: {} installed intents: {}'.format( allState.get('total'), allState.get('installed') ) )
            return main.FALSE

        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, response ) )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": ONOS timeout" )
            return None

    def flows( self, state="", jsonFormat=True, timeout=60, noExit=False ):
        """
        Optional:
            * jsonFormat: enable output formatting in json
        Description:
            Obtain flows currently installed
        """
        try:
            cmdStr = "flows"
            if jsonFormat:
                cmdStr += " -j "
            cmdStr += state
            handle = self.sendline( cmdStr, timeout=timeout, noExit=noExit )
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def checkFlowCount(self, min=0, timeout=60 ):
        count = int(self.getTotalFlowsNum( timeout=timeout ))
        return count if (count > min) else False

    def checkFlowsState( self, isPENDING=True, timeout=60,noExit=False ):
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
            states = ["PENDING_ADD", "PENDING_REMOVE", "REMOVED", "FAILED"]
            checkedStates = []
            statesCount = [0, 0, 0, 0]
            for s in states:
                rawFlows = self.flows( state=s, timeout = timeout )
                if rawFlows:
                    # if we didn't get flows or flows function return None, we should return
                    # main.Flase
                    checkedStates.append( json.loads( rawFlows ) )
                else:
                    return main.FALSE
            for i in range( len( states ) ):
                for c in checkedStates[i]:
                    try:
                        statesCount[i] += int( c.get( "flowCount" ) )
                    except TypeError:
                        main.log.exception( "Json object not as expected" )
                main.log.info( states[i] + " flows: " + str( statesCount[i] ) )

            # We want to count PENDING_ADD if isPENDING is true
            if isPENDING:
                if statesCount[1] + statesCount[2] + statesCount[3] > 0:
                    return main.FALSE
            else:
                if statesCount[0] + statesCount[1] + statesCount[2] + statesCount[3] > 0:
                    return main.FALSE
            return main.TRUE
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, rawFlows ) )
            return None

        except AssertionError:
            main.log.exception( "" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": ONOS timeout" )
            return None


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
            assert "Command not found:" not in response, response
            main.log.info( response )
            if response == None:
                return None

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
            main.cleanup()
            main.exit()
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def getTotalFlowsNum( self, timeout=60, noExit=False ):
        """
        Description:
            Get the number of ADDED flows.
        Return:
            The number of ADDED flows
        """

        try:
            # get total added flows number
            cmd = "flows -s|grep ADDED|wc -l"
            totalFlows = self.sendline( cmd, timeout=timeout, noExit=noExit )

            if totalFlows == None:
                # if timeout, we will get total number of all flows, and subtract other states
                states = ["PENDING_ADD", "PENDING_REMOVE", "REMOVED", "FAILED"]
                checkedStates = []
                totalFlows = 0
                statesCount = [0, 0, 0, 0]

                # get total flows from summary
                response = json.loads( self.sendline( "summary -j", timeout=timeout, noExit=noExit ) )
                totalFlows = int( response.get("flows") )

                for s in states:
                    rawFlows = self.flows( state=s, timeout = timeout )
                    if rawFlows == None:
                        # if timeout, return the total flows number from summary command
                        return totalFlows
                    checkedStates.append( json.loads( rawFlows ) )

                # Calculate ADDED flows number, equal total subtracts others
                for i in range( len( states ) ):
                    for c in checkedStates[i]:
                        try:
                            statesCount[i] += int( c.get( "flowCount" ) )
                        except TypeError:
                            main.log.exception( "Json object not as expected" )
                    totalFlows = totalFlows - int( statesCount[i] )
                    main.log.info( states[i] + " flows: " + str( statesCount[i] ) )

                return totalFlows

            return int(totalFlows)

        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, rawFlows ) )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": ONOS timeout" )
            return None

    def getTotalIntentsNum( self, timeout=60 ):
        """
        Description:
            Get the total number of intents, include every states.
        Return:
            The number of intents
        """
        try:
            cmd = "summary -j"
            response = self.sendline( cmd, timeout=timeout )
            if response == None:
                return  -1
            response = json.loads( response )
            return int( response.get("intents") )
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, response ) )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            intentsStr = self.intents(jsonFormat=False)
            intentIdList = []

            # Parse the intents output for ID's
            intentsList = [ s.strip() for s in intentsStr.splitlines() ]
            for intents in intentsList:
                match = re.search('id=0x([\da-f]+),', intents)
                if match:
                    tmpId = match.group()[3:-1]
                    intentIdList.append( tmpId )
            return intentIdList

        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def FlowAddedCount( self, deviceId ):
        """
        Determine the number of flow rules for the given device id that are
        in the added state
        """
        try:
            cmdStr = "flows any " + str( deviceId ) + " | " +\
                     "grep 'state=ADDED' | wc -l"
            handle = self.sendline( cmdStr )
            assert "Command not found:" not in handle, handle
            return handle
        except AssertionError:
            main.log.exception( "" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            idList = [ node.get('id') for node in nodesJson ]
            return idList
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, nodesStr ) )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            topology = json.loads(topologyOutput)
            main.log.debug( topology )
            return topology
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, topologyOutput ) )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def checkStatus(self, numoswitch, numolink, numoctrl = -1, logLevel="info"):
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
            topology = self.getTopology( self.topology() )
            summary = json.loads( self.summary() )

            if topology == {} or topology == None or summary == {} or summary == None:
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
            linkCheck = ( int( links ) == int( numolink ) )
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
                                "Value was '" + str(role) + "'." )
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def clusters( self, jsonFormat=True ):
        """
        Lists all clusters
        Optional argument:
            * jsonFormat - boolean indicating if you want output in json
        """
        try:
            cmdStr = "clusters"
            if jsonFormat:
                cmdStr += " -j"
            handle = self.sendline( cmdStr )
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.log.error( "Error in electionTestLeader on " + self.name +
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.log.error( "Error in electionTestRun on " + self.name +
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            assert "Command not found:" not in response, response
            # success
            successPattern = "Withdrawing\sfrom\sleadership\selections\sfor" +\
                "\sthe\sElection\sapp."
            if re.search( successPattern, response ):
                main.log.info( self.name + " withdrawing from leadership " +
                               "elections for the Election app." )
                return main.TRUE
            # error
            main.log.error( "Error in electionTestWithdraw on " +
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
                main.log.error( "Error in getting ports" )
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
                main.log.error( "Error in getting ports " )
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
                main.log.error( "Error in getting ports" )
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
                if dict["topic"] == topic:
                    leader = dict["leader"]
                    candidates = re.split( ", ", dict["candidates"][1:-1] )
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def partitions( self, jsonFormat=True ):
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def apps( self, jsonFormat=True ):
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
            if jsonFormat:
                cmdStr += " -j"
            output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            assert "Error executing command" not in output, output
            return output
        # FIXME: look at specific exceptions/Errors
        except AssertionError:
            main.log.exception( "Error in processing onos:app command." )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
                if appName == app.get('name'):
                    state = app.get('state')
                    break
            if state == "ACTIVE" or state == "INSTALLED":
                return state
            elif state is None:
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
                                "; was given '" + option + "'")
                return main.FALSE
            cmdStr = "onos:app " + option + " " + appName
            output = self.sendline( cmdStr )
            if "Error executing command" in output:
                main.log.error( "Error in processing onos:app command: " +
                                str( output ) )
                return main.FALSE
            elif "No such application" in output:
                main.log.error( "The application '" + appName +
                                "' is not installed in ONOS" )
                return main.FALSE
            elif "Command not found:" in output:
                main.log.error( "Error in processing onos:app command: " +
                                str( output ) )
                return main.FALSE
            elif "Unsupported command:" in output:
                main.log.error( "Incorrect command given to 'app': " +
                                str( output ) )
            # NOTE: we may need to add more checks here
            # else: Command was successful
            # main.log.debug( "app response: " + repr( output ) )
            return main.TRUE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.ERROR
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
                    for i in range(10):  # try 10 times then give up
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
                    for i in range(10):  # try 10 times then give up
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
                    for i in range(10):  # try 10 times then give up
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
                    for i in range(10):  # try 10 times then give up
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.log.exception( "Error in processing onos:app-ids command." )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            bail = False
            rawJson = self.appIDs( jsonFormat=True )
            if rawJson:
                ids = json.loads( rawJson )
            else:
                main.log.error( "app-ids returned nothing:" + repr( rawJson ) )
                bail = True
            rawJson = self.apps( jsonFormat=True )
            if rawJson:
                apps = json.loads( rawJson )
            else:
                main.log.error( "apps returned nothing:" + repr( rawJson ) )
                bail = True
            if bail:
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
                # main.log.debug( "Comparing " + str( app ) + " to " +
                #                 str( current ) )
                if not current:  # if ids doesn't have this id
                    result = main.FALSE
                    main.log.error( "'app-ids' does not have the ID for " +
                                    str( appName ) + " that apps does." )
                elif len( current ) > 1:
                    # there is more than one app with this ID
                    result = main.FALSE
                    # We will log this later in the method
                elif not current[0][ 'name' ] == appName:
                    currentName = current[0][ 'name' ]
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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.log.exception( "Error in processing 'cfg get' command." )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.log.exception( "Error in processing 'cfg set' command." )
            return main.FALSE
        except ( TypeError, ValueError ):
            main.log.exception( "{}: Object not as expected: {!r}".format( self.name, results ) )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            try:
                # TODO: Maybe make this less hardcoded
                # ConsistentMap Exceptions
                assert "org.onosproject.store.service" not in output
                # Node not leader
                assert "java.lang.IllegalStateException" not in output
            except AssertionError:
                main.log.error( "Error in processing '" + cmdStr + "' " +
                                "command: " + str( output ) )
                retryTime = 30  # Conservative time, given by Madan
                main.log.info( "Waiting " + str( retryTime ) +
                               "seconds before retrying." )
                time.sleep( retryTime )  # Due to change in mastership
                output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Error executing command" not in output
            positiveMatch = "\[(.*)\] was added to the set " + str( setName )
            negativeMatch = "\[(.*)\] was already in set " + str( setName )
            main.log.info( self.name + ": " + output )
            if re.search( positiveMatch, output):
                return main.TRUE
            elif re.search( negativeMatch, output):
                return main.FALSE
            else:
                main.log.error( self.name + ": setTestAdd did not" +
                                " match expected output" )
                main.log.debug( self.name + " actual: " + repr( output ) )
                return main.ERROR
        except AssertionError:
            main.log.exception( "Error in processing '" + cmdStr + "' command. " )
            return main.ERROR
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.ERROR
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            output = self.sendline( cmdStr )
            try:
                assert output is not None, "Error in sendline"
                # TODO: Maybe make this less hardcoded
                # ConsistentMap Exceptions
                assert "org.onosproject.store.service" not in output
                # Node not leader
                assert "java.lang.IllegalStateException" not in output
            except AssertionError:
                main.log.error( "Error in processing '" + cmdStr + "' " +
                                "command: " + str( output ) )
                retryTime = 30  # Conservative time, given by Madan
                main.log.info( "Waiting " + str( retryTime ) +
                               "seconds before retrying." )
                time.sleep( retryTime )  # Due to change in mastership
                output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            assert "Error executing command" not in output, output
            main.log.info( self.name + ": " + output )
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
        except AssertionError:
            main.log.exception( "Error in processing '" + cmdStr + "' commandr. " )
            return main.ERROR
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.ERROR
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            pattern = "Items in set " + setName + ":\n" + setPattern
            containsTrue = "Set " + setName + " contains the value " + values
            containsFalse = "Set " + setName + " did not contain the value " +\
                            values
            containsAllTrue = "Set " + setName + " contains the the subset " +\
                              setPattern
            containsAllFalse = "Set " + setName + " did not contain the the" +\
                               " subset " + setPattern

            cmdStr = "set-test-get "
            cmdStr += setName + " " + values
            output = self.sendline( cmdStr )
            try:
                assert output is not None, "Error in sendline"
                # TODO: Maybe make this less hardcoded
                # ConsistentMap Exceptions
                assert "org.onosproject.store.service" not in output
                # Node not leader
                assert "java.lang.IllegalStateException" not in output
            except AssertionError:
                main.log.error( "Error in processing '" + cmdStr + "' " +
                                "command: " + str( output ) )
                retryTime = 30  # Conservative time, given by Madan
                main.log.info( "Waiting " + str( retryTime ) +
                               "seconds before retrying." )
                time.sleep( retryTime )  # Due to change in mastership
                output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            assert "Error executing command" not in output, output
            main.log.info( self.name + ": " + output )

            if length == 0:
                match = re.search( pattern, output )
            else:  # if given values
                if length == 1:  # Contains output
                    patternTrue = pattern + "\n" + containsTrue
                    patternFalse = pattern + "\n" + containsFalse
                else:  # ContainsAll output
                    patternTrue = pattern + "\n" + containsAllTrue
                    patternFalse = pattern + "\n" + containsAllFalse
                matchTrue = re.search( patternTrue, output )
                matchFalse = re.search( patternFalse, output )
                if matchTrue:
                    containsCheck = main.TRUE
                    match = matchTrue
                elif matchFalse:
                    containsCheck = main.FALSE
                    match = matchFalse
                else:
                    main.log.error( self.name + " setTestGet did not match " +\
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
        except AssertionError:
            main.log.exception( "Error in processing '" + cmdStr + "' command." )
            return main.ERROR
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.ERROR
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            pattern = "There are (\d+) items in set " + setName + ":\n" +\
                          setPattern
            cmdStr = "set-test-get -s "
            cmdStr += setName
            output = self.sendline( cmdStr )
            try:
                assert output is not None, "Error in sendline"
                # TODO: Maybe make this less hardcoded
                # ConsistentMap Exceptions
                assert "org.onosproject.store.service" not in output
                # Node not leader
                assert "java.lang.IllegalStateException" not in output
            except AssertionError:
                main.log.error( "Error in processing '" + cmdStr + "' " +
                                "command: " + str( output ) )
                retryTime = 30  # Conservative time, given by Madan
                main.log.info( "Waiting " + str( retryTime ) +
                               "seconds before retrying." )
                time.sleep( retryTime )  # Due to change in mastership
                output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            assert "Error executing command" not in output, output
            main.log.info( self.name + ": " + output )
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
        except AssertionError:
            main.log.exception( "Error in processing '" + cmdStr + "' command." )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            counters = {}
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
            main.log.exception( "Error in processing 'counters' command." )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            output = self.sendline( cmdStr )
            try:
                assert output is not None, "Error in sendline"
                # TODO: Maybe make this less hardcoded
                # ConsistentMap Exceptions
                assert "org.onosproject.store.service" not in output
                # Node not leader
                assert "java.lang.IllegalStateException" not in output
            except AssertionError:
                main.log.error( "Error in processing '" + cmdStr + "' " +
                                "command: " + str( output ) )
                retryTime = 30  # Conservative time, given by Madan
                main.log.info( "Waiting " + str( retryTime ) +
                               "seconds before retrying." )
                time.sleep( retryTime )  # Due to change in mastership
                output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            assert "Error executing command" not in output, output
            main.log.info( self.name + ": " + output )
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
        except AssertionError:
            main.log.exception( "Error in processing '" + cmdStr + "' command." )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            output = self.sendline( cmdStr )
            try:
                assert output is not None, "Error in sendline"
                # TODO: Maybe make this less hardcoded
                # ConsistentMap Exceptions
                assert "org.onosproject.store.service" not in output
                # Node not leader
                assert "java.lang.IllegalStateException" not in output
            except AssertionError:
                main.log.error( "Error in processing '" + cmdStr + "' " +
                                "command: " + str( output ) )
                retryTime = 30  # Conservative time, given by Madan
                main.log.info( "Waiting " + str( retryTime ) +
                               "seconds before retrying." )
                time.sleep( retryTime )  # Due to change in mastership
                output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            assert "Error executing command" not in output, output
            main.log.info( self.name + ": " + output )
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
        except AssertionError:
            main.log.exception( "Error in processing '" + cmdStr + "' command." )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            try:
                # TODO: Maybe make this less hardcoded
                # ConsistentMap Exceptions
                assert "org.onosproject.store.service" not in output
                # Node not leader
                assert "java.lang.IllegalStateException" not in output
            except AssertionError:
                main.log.error( "Error in processing '" + cmdStr + "' " +
                                "command: " + str( output ) )
                return None
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
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            output = self.sendline( cmdStr )
            assert output is not None, "Error in sendline"
            assert "Command not found:" not in output, output
            try:
                # TODO: Maybe make this less hardcoded
                # ConsistentMap Exceptions
                assert "org.onosproject.store.service" not in output
                # Node not leader
                assert "java.lang.IllegalStateException" not in output
            except AssertionError:
                main.log.error( "Error in processing '" + cmdStr + "' " +
                                "command: " + str( output ) )
                return None
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
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
                ip = [ip]
            for item in ip:
                if ":" in item:
                    sitem = item.split( ":" )
                    if len(sitem) == 3:
                        cmd += " " + item
                    elif "." in sitem[1]:
                        cmd += " {}:{}".format(item, port)
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
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            if type( device ) is str:
                device = list( device )

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
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            if type( host ) is str:
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
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            cmd =  "null-link null:{} null:{} {}".format( begin, end, state )
            response = self.sendline( cmd, showResponse=showResponse, timeout=timeout )
            assert response is not None, "Error in sendline"
            assert "Command not found:" not in response, response
            if "Error" in response or "Failure" in response:
                main.log.error( response )
                return main.FALSE
            return main.TRUE
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def portstate(self, dpid='of:0000000000000102', port='2', state='enable'):
        '''
        Description:
             Changes the state of port in an OF switch by means of the
             PORTSTATUS OF messages.
        params:
            dpid - (string) Datapath ID of the device
            port - (string) target port in the device
            state - (string) target state (enable or disabled)
        returns:
            main.TRUE if no exceptions were thrown and no Errors are
            present in the resoponse. Otherwise, returns main.FALSE
        '''
        try:
            cmd =  "portstate {} {} {}".format( dpid, port, state )
            response = self.sendline( cmd, showResponse=True )
            assert response is not None, "Error in sendline"
            assert "Command not found:" not in response, response
            if "Error" in response or "Failure" in response:
                main.log.error( response )
                return main.FALSE
            return main.TRUE
        except AssertionError:
            main.log.exception( "" )
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

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
            self.handle.sendline( "log:set %s %s" %( level, app ) )
            self.handle.expect( "onos>" )

            response = self.handle.before
            if re.search( "Error", response ):
                return main.FALSE
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception found" )
            main.cleanup()
            main.exit()
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()
