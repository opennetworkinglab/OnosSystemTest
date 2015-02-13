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
import sys
import pexpect
import re
import Queue
sys.path.append( "../" )
from drivers.common.clidriver import CLI


class OnosCliDriver( CLI ):

    def __init__( self ):
        """
        Initialize client
        """
        super( CLI, self ).__init__()

    def connect( self, **connectargs ):
        """
        Creates ssh handle for ONOS cli.
        """
        try:
            for key in connectargs:
                vars( self )[ key ] = connectargs[ key ]
            self.home = "~/ONOS"
            for key in self.options:
                if key == "home":
                    self.home = self.options[ 'home' ]
                    break

            self.name = self.options[ 'name' ]
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
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def disconnect( self ):
        """
        Called when Test is complete to disconnect the ONOS handle.
        """
        response = ''
        try:
            self.handle.sendline( "" )
            i = self.handle.expect( [ "onos>", "\$" ] )
            if i == 0:
                self.handle.sendline( "system:shutdown" )
                self.handle.expect( "Confirm" )
                self.handle.sendline( "yes" )
                self.handle.expect( "\$" )
            self.handle.sendline( "" )
            self.handle.expect( "\$" )
            self.handle.sendline( "exit" )
            self.handle.expect( "closed" )

        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
        except:
            main.log.exception( self.name + ": Connection failed to the host" )
            response = main.FALSE
        return response

    def logout( self ):
        """
        Sends 'logout' command to ONOS cli
        """
        try:
            self.handle.sendline( "" )
            i = self.handle.expect( [
                "onos>",
                "\$" ], timeout=10 )
            if i == 0:
                self.handle.sendline( "logout" )
                self.handle.expect( "\$" )
            elif i == 1:
                return main.TRUE

        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": eof exception found" )
            main.log.error( self.name + ":    " +
                            self.handle.before )
            main.cleanup()
            main.exit()
        except:
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
                self.handle.expect( "ONOS_CELL=" + str( cellname ) )
                handleBefore = self.handle.before
                handleAfter = self.handle.after
                # Get the rest of the handle
                self.handle.sendline( "" )
                self.handle.expect( "\$" )
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
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def startOnosCli( self, ONOSIp, queue="", karafTimeout="" ):
        import Queue
        """
        karafTimeout is an optional arugument. karafTimeout value passed
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
        try:
            if queue=="":
                queue = Queue.Queue()
            self.handle.sendline( "" )
            x = self.handle.expect( [
                "\$", "onos>" ], timeout=10 )

            if x == 1:
                main.log.info( "ONOS cli is already running" )
                queue.put(main.TRUE)
                return main.TRUE

            # Wait for onos start ( -w ) and enter onos cli
            self.handle.sendline( "onos -w " + str( ONOSIp ) )
            i = self.handle.expect( [
                "onos>",
                pexpect.TIMEOUT ], timeout=60 )

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
                queue.put(main.TRUE)
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
                    queue.put(main.TRUE)
                    return main.TRUE
                else:
                    main.log.error( "Connection to CLI " +
                                    str( ONOSIp ) + " timeout" )
                    queue.put(main.TRUE)
                    return main.FALSE

        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def sendline( self, cmdStr ):
        """
        Send a completely user specified string to
        the onos> prompt. Use this function if you have
        a very specific command to send.

        Warning: There are no sanity checking to commands
        sent using this method.
        """
        try:
            self.handle.sendline( "" )
            self.handle.expect( "onos>" )

            self.handle.sendline( "log:log \"Sending CLI command: '"
                                  + cmdStr + "'\"" )
            self.handle.expect( "onos>" )
            self.handle.sendline( cmdStr )
            self.handle.expect( "onos>" )
            main.log.info( "Command '" + str( cmdStr ) + "' sent to "
                           + self.name + "." )

            handle = self.handle.before
            # Remove control strings from output
            ansiEscape = re.compile( r'\x1b[^m]*m' )
            handle = ansiEscape.sub( '', handle )
            #Remove extra return chars that get added
            handle = re.sub(  r"\s\r", "", handle )
            handle = handle.strip()
            # parse for just the output, remove the cmd from handle
            output = handle.split( cmdStr, 1 )[1]


            return output
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
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
            if re.search( "Error", handle ):
                main.log.error( "Error in adding node" )
                main.log.error( handle )
                return main.FALSE
            else:
                main.log.info( "Node " + str( ONOSIp ) + " added" )
                return main.TRUE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
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
            self.sendline( cmdStr )
            # TODO: add error checking. Does ONOS give any errors?

            return main.TRUE

        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def nodes( self ):
        """
        List the nodes currently visible
        Issues command: 'nodes'
        Returns: entire handle of list of nodes
        """
        try:
            cmdStr = "nodes"
            handle = self.sendline( cmdStr )
            return handle
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def topology( self ):
        """
        Shows the current state of the topology
        by issusing command: 'onos> onos:topology'
        """
        try:
            # either onos:topology or 'topology' will work in CLI
            cmdStr = "onos:topology"
            handle = self.sendline( cmdStr )
            main.log.info( "onos:topology returned: " + str( handle ) )
            return handle
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def featureInstall( self, featureStr, queue="" ):
        """
        Installs a specified feature
        by issuing command: 'onos> feature:install <feature_str>'
        """
        try:
            if queue=="":
                queue = Queue.Queue()
            cmdStr = "feature:install " + str( featureStr )
            self.sendline( cmdStr )
            # TODO: Check for possible error responses from karaf
            queue.put(main.TRUE)
            return main.TRUE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.log.report( "Failed to install feature" )
            main.log.report( "Exiting test" )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.log.report( "Failed to install feature" )
            main.log.report( "Exiting test" )
            main.cleanup()
            main.exit()

    def featureUninstall( self, featureStr, queue="" ):
        """
        Uninstalls a specified feature
        by issuing command: 'onos> feature:uninstall <feature_str>'
        """
        try:
            if queue=="":
                queue = Queue.Queue()
            cmdStr = "feature:uninstall " + str( featureStr )
            self.sendline( cmdStr )
            # TODO: Check for possible error responses from karaf
            queue.put(main.TRUE)
            return main.TRUE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def devices( self, jsonFormat=True, queue="" ):
        """
        Lists all infrastructure devices or switches
        Optional argument:
            * jsonFormat - boolean indicating if you want output in json
        """
        try:
            if queue=="":
                queue = Queue.Queue()
            if jsonFormat:
                cmdStr = "devices -j"
                handle = self.sendline( cmdStr )
                """
                handle variable here contains some ANSI escape color code
                sequences at the end which are invisible in the print command
                output. To make that escape sequence visible, use repr()
                function. The repr( handle ) output when printed shows the
                ANSI escape sequences. In json.loads( somestring ), this
                somestring variable is actually repr( somestring ) and
                json.loads would fail with the escape sequence. So we take off
                that escape sequence using:

                ansiEscape = re.compile( r'\r\r\n\x1b[^m]*m' )
                handle1 = ansiEscape.sub( '', handle )
                """
                ansiEscape = re.compile( r'\r\r\n\x1b[^m]*m' )
                handle1 = ansiEscape.sub( '', handle )
                queue.put(handle1)
                return handle1
            else:
                cmdStr = "devices"
                handle = self.sendline( cmdStr )
                queue.put(handle)
                return handle
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def balanceMasters( self, queue = "" ):
        """
        This balances the devices across all controllers
        by issuing command: 'onos> onos:balance-masters'
        If required this could be extended to return devices balanced output.
        """
        try:
            if queue=="":
                queue = Queue.Queue()
            cmdStr = "onos:balance-masters"
            self.sendline( cmdStr )
            # TODO: Check for error responses from ONOS
            queue.put(main.TRUE)
            return main.TRUE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def links( self, jsonFormat=True, queue="" ):
        """
        Lists all core links
        Optional argument:
            * jsonFormat - boolean indicating if you want output in json
        """
        try:
            if queue=="":
                queue = Queue.Queue()
            if jsonFormat:
                cmdStr = "links -j"
                handle = self.sendline( cmdStr )
                """
                handle variable here contains some ANSI escape color code
                sequences at the end which are invisible in the print command
                output. To make that escape sequence visible, use repr()
                function. The repr( handle ) output when printed shows the ANSI
                escape sequences. In json.loads( somestring ), this somestring
                variable is actually repr( somestring ) and json.loads would
                fail with the escape sequence. So we take off that escape
                sequence using:

                ansiEscape = re.compile( r'\r\r\n\x1b[^m]*m' )
                handle1 = ansiEscape.sub( '', handle )
                """
                ansiEscape = re.compile( r'\r\r\n\x1b[^m]*m' )
                handle1 = ansiEscape.sub( '', handle )
                queue.put(handle1)
                return handle1
            else:
                cmdStr = "links"
                handle = self.sendline( cmdStr )
                queue.put(handle)
                return handle
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def ports( self,jsonFormat=True, queue="" ):
        """
        Lists all ports
        Optional argument:
            * jsonFormat - boolean indicating if you want output in json
        """
        try:
            if queue=="":
                queue = Queue.Queue()
            if jsonFormat:
                cmdStr = "ports -j"
                handle = self.sendline( cmdStr )
                """
                handle variable here contains some ANSI escape color code
                sequences at the end which are invisible in the print command
                output. To make that escape sequence visible, use repr()
                function. The repr( handle ) output when printed shows the ANSI
                escape sequences. In json.loads( somestring ), this somestring
                variable is actually repr( somestring ) and json.loads would
                fail with the escape sequence. So we take off that escape
                sequence using the following commads:

                ansiEscape = re.compile( r'\r\r\n\x1b[^m]*m' )
                handle1 = ansiEscape.sub( '', handle )
                """
                ansiEscape = re.compile( r'\r\r\n\x1b[^m]*m' )
                handle1 = ansiEscape.sub( '', handle )
                queue.put(handle1)
                return handle1

            else:
                cmdStr = "ports"
                handle = self.sendline( cmdStr )
                queue.put(handle)
                return handle
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def roles( self,jsonFormat=True, queue="" ):
        """
        Lists all devices and the controllers with roles assigned to them
        Optional argument:
            * jsonFormat - boolean indicating if you want output in json
        """
        try:
            if queue=="":
                queue = Queue.Queue()
            if jsonFormat:
                cmdStr = "roles -j"
                handle = self.sendline( cmdStr )
                """
                handle variable here contains some ANSI escape color code
                sequences at the end which are invisible in the print command
                output. To make that escape sequence visible, use repr()
                function. The repr( handle ) output when printed shows the ANSI
                escape sequences. In json.loads( somestring ), this somestring
                variable is actually repr( somestring ) and json.loads would
                fail with the escape sequence.

                So we take off that escape sequence using the following
                commads:

                ansiEscape = re.compile( r'\r\r\n\x1b[^m]*m' )
                handle1 = ansiEscape.sub( '', handle )
                """
                ansiEscape = re.compile( r'\r\r\n\x1b[^m]*m' )
                handle1 = ansiEscape.sub( '', handle )
                queue.put(handle1)
                return handle1

            else:
                cmdStr = "roles"
                handle = self.sendline( cmdStr )
                queue.put(handle)
                return handle
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def getRole( self, deviceId, queue="" ):
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
            if queue=="":
                queue = Queue.Queue()
            import json
            if deviceId is None:
                queue.put(None)
                return None
            else:
                rawRoles = self.roles()
                rolesJson = json.loads( rawRoles )
                # search json for the device with id then return the device
                for device in rolesJson:
                    # print device
                    if str( deviceId ) in device[ 'id' ]:
                        queue.put(device)
                        return device
            queue.put(None)
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def rolesNotNull( self , queue=""):
        """
        Iterates through each device and checks if there is a master assigned
        Returns: main.TRUE if each device has a master
                 main.FALSE any device has no master
        """
        try:
            if queue=="":
                queue = Queue.Queue()
            import json
            rawRoles = self.roles()
            rolesJson = json.loads( rawRoles )
            # search json for the device with id then return the device
            for device in rolesJson:
                # print device
                if device[ 'master' ] == "none":
                    main.log.warn( "Device has no master: " + str( device ) )
                    queue.put(main.FALSE)
                    return main.FALSE
            queue.put(main.TRUE)
            return main.TRUE

        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def paths( self, srcId, dstI ):
        """
        Returns string of paths, and the cost.
        Issues command: onos:paths <src> <dst>
        """
        try:
            cmdStr = "onos:paths " + str( srcId ) + " " + str( dstId )
            handle = self.sendline( cmdStr )
            if re.search( "Error", handle ):
                main.log.error( "Error in getting paths" )
                return ( handle, "Error" )
            else:
                path = handle.split( ";" )[ 0 ]
                cost = handle.split( ";" )[ 1 ]
                return ( path, cost )
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return ( handle, "Error" )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def hosts( self, jsonFormat=True, queue="" ):
        """
        Lists all discovered hosts
        Optional argument:
            * jsonFormat - boolean indicating if you want output in json
        """
        try:
            if queue=="":
                queue = Queue.Queue()
            if jsonFormat:
                cmdStr = "hosts -j"
                handle = self.sendline( cmdStr )
                """
                handle variable here contains some ANSI escape color code
                sequences at the end which are invisible in the print command
                output. To make that escape sequence visible, use repr()
                function. The repr( handle ) output when printed shows the ANSI
                escape sequences. In json.loads( somestring ), this somestring
                variable is actually repr( somestring ) and json.loads would
                fail with the escape sequence. So we take off that escape
                sequence using:

                ansiEscape = re.compile( r'\r\r\n\x1b[^m]*m' )
                handle1 = ansiEscape.sub( '', handle )
                """
                ansiEscape = re.compile( r'\r\r\n\x1b[^m]*m' )
                handle1 = ansiEscape.sub( '', handle )
                queue.put(handle1)
                return handle1
            else:
                cmdStr = "hosts"
                handle = self.sendline( cmdStr )
                queue.put(handle)
                return handle
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def getHost( self, mac, queue=""):
        """
        Return the first host from the hosts api whose 'id' contains 'mac'

        Note: mac must be a colon seperated mac address, but could be a
              partial mac address

        Return None if there is no match
        """
        import json
        try:
            if queue=="":
                queue = Queue.Queue()
            if mac is None:
                queue.put(None)
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
                        queue.put(None)
                        return host
            queue.put(None)
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def getHostsId( self, hostList, queue="" ):
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
            if queue=="":
                queue = Queue.Queue()
            onosHostList = []

            for host in hostList:
                host = host.replace( "h", "" )
                hostHex = hex( int( host ) ).zfill( 12 )
                hostHex = str( hostHex ).replace( 'x', '0' )
                i = iter( str( hostHex ) )
                hostHex = ":".join( a + b for a, b in zip( i, i ) )
                hostHex = hostHex + "/-1"
                onosHostList.append( hostHex )
            queue.put(onosHostList)
            return onosHostList

        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def addHostIntent( self, hostIdOne, hostIdTwo, queue="" ):
        """
        Required:
            * hostIdOne: ONOS host id for host1
            * hostIdTwo: ONOS host id for host2
        Description:
            Adds a host-to-host intent ( bidrectional ) by
            specifying the two hosts.
        """
        try:
            if queue=="":
                queue = Queue.Queue()
            cmdStr = "add-host-intent " + str( hostIdOne ) +\
                " " + str( hostIdTwo )
            handle = self.sendline( cmdStr )
            if re.search( "Error", handle ):
                main.log.error( "Error in adding Host intent" )
                queue.put(handle)
                return handle
            else:
                main.log.info( "Host intent installed between " +
                           str( hostIdOne ) + " and " + str( hostIdTwo ) )
                queue.put(main.TRUE)
                return main.TRUE

        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def addOpticalIntent( self, ingressDevice, egressDevice, queue="" ):
        """
        Required:
            * ingressDevice: device id of ingress device
            * egressDevice: device id of egress device
        Optional:
            TODO: Still needs to be implemented via dev side
        """
        try:
            if queue=="":
                queue = Queue.Queue()
            cmdStr = "add-optical-intent " + str( ingressDevice ) +\
                " " + str( egressDevice )
            handle = self.sendline( cmdStr )
            # If error, return error message
            if re.search( "Error", handle ):
                queue.put(handle)
                return handle
            else:
                queue.put(main.TRUE)
                return main.TRUE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
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
            queue=""):
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
        Description:
            Adds a point-to-point intent ( uni-directional ) by
            specifying device id's and optional fields

        NOTE: This function may change depending on the
              options developers provide for point-to-point
              intent via cli
        """
        try:
            if queue=="":
                queue = Queue.Queue()
            cmd = ""

            # If there are no optional arguments
            if not ethType and not ethSrc and not ethDst\
                    and not bandwidth and not lambdaAlloc \
                    and not ipProto and not ipSrc and not ipDst \
                    and not tcpSrc and not tcpDst:
                cmd = "add-point-intent"

            else:
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

            # Check whether the user appended the port
            # or provided it as an input
            if "/" in ingressDevice:
                cmd += " " + str( ingressDevice )
            else:
                if not portIngress:
                    main.log.error( "You must specify " +
                                    "the ingress port" )
                    # TODO: perhaps more meaningful return
                    queue.put(main.FALSE)
                    return main.FALSE

                cmd += " " + \
                    str( ingressDevice ) + "/" +\
                    str( portIngress ) + " "

            if "/" in egressDevice:
                cmd += " " + str( egressDevice )
            else:
                if not portEgress:
                    main.log.error( "You must specify " +
                                    "the egress port" )
                    queue.put(main.FALSE)
                    return main.FALSE

                cmd += " " +\
                    str( egressDevice ) + "/" +\
                    str( portEgress )

            handle = self.sendline( cmd )
            if re.search( "Error", handle ):
                main.log.error( "Error in adding point-to-point intent" )
                queue.put(main.FALSE)
                return main.FALSE
            else:
                queue.put(main.TRUE)
                return main.TRUE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def addMultipointToSinglepointIntent(
            self,
            ingressDevice1,
            ingressDevice2,
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
            setEthSrc="",
            setEthDst="",
            queue=""):
        """
        Note:
            This function assumes that there would be 2 ingress devices and
            one egress device. For more number of ingress devices, this
            function needs to be modified
        Required:
            * ingressDevice1: device id of ingress device1
            * ingressDevice2: device id of ingress device2
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
        Description:
            Adds a multipoint-to-singlepoint intent ( uni-directional ) by
            specifying device id's and optional fields

        NOTE: This function may change depending on the
              options developers provide for multipointpoint-to-singlepoint
              intent via cli
        """
        try:
            if queue=="":
                queue = Queue.Queue()
            cmd = ""

            # If there are no optional arguments
            if not ethType and not ethSrc and not ethDst\
                    and not bandwidth and not lambdaAlloc\
                    and not ipProto and not ipSrc and not ipDst\
                    and not tcpSrc and not tcpDst and not setEthSrc\
                    and not setEthDst:
                cmd = "add-multi-to-single-intent"

            else:
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

            # Check whether the user appended the port
            # or provided it as an input
            if "/" in ingressDevice1:
                cmd += " " + str( ingressDevice1 )
            else:
                if not portIngress1:
                    main.log.error( "You must specify " +
                                    "the ingress port1" )
                    # TODO: perhaps more meaningful return
                    queue.put(main.FALSE)
                    return main.FALSE

                cmd += " " + \
                    str( ingressDevice1 ) + "/" +\
                    str( portIngress1 ) + " "

            if "/" in ingressDevice2:
                cmd += " " + str( ingressDevice2 )
            else:
                if not portIngress2:
                    main.log.error( "You must specify " +
                                    "the ingress port2" )
                    # TODO: perhaps more meaningful return
                    queue.put(main.FALSE)
                    return main.FALSE

                cmd += " " + \
                    str( ingressDevice2 ) + "/" +\
                    str( portIngress2 ) + " "

            if "/" in egressDevice:
                cmd += " " + str( egressDevice )
            else:
                if not portEgress:
                    main.log.error( "You must specify " +
                                    "the egress port" )
                    queue.put(main.FALSE)
                    return main.FALSE

                cmd += " " +\
                    str( egressDevice ) + "/" +\
                    str( portEgress )
            print "cmd= ", cmd
            handle = self.sendline( cmd )
            if re.search( "Error", handle ):
                main.log.error( "Error in adding point-to-point intent" )
                queue.put(self.handle)
                return self.handle
            else:
                queue.put(main.TRUE)
                return main.TRUE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def removeIntent( self, intentId, queue="" ):
        """
        Remove intent for specified intent id

        Returns:
            main.False on error and
            cli output otherwise
        """
        try:
            if queue=="":
                queue = Queue.Queue()
            cmdStr = "remove-intent " + str( intentId )
            handle = self.sendline( cmdStr )
            if re.search( "Error", handle ):
                main.log.error( "Error in removing intent" )
                queue.put(main.FALSE)
                return main.FALSE
            else:
                # TODO: Should this be main.TRUE
                queue.put(handle)
                return handle
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
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
            if jsonFormat:
                cmdStr = "routes -j"
                handleTmp = self.sendline( cmdStr )
                ansiEscape = re.compile( r'\r\r\n\x1b[^m]*m' )
                handle = ansiEscape.sub( '', handleTmp )
            else:
                cmdStr = "routes"
                handle = self.sendline( cmdStr )
            return handle
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def intents( self, jsonFormat=True, queue="" ):
        """
        Optional:
            * jsonFormat: enable output formatting in json
        Description:
            Obtain intents currently installed
        """
        try:
            if queue=="":
                queue = Queue.Queue()
            if jsonFormat:
                cmdStr = "intents -j"
                handle = self.sendline( cmdStr )
                ansiEscape = re.compile( r'\r\r\n\x1b[^m]*m' )
                handle = ansiEscape.sub( '', handle )
            else:
                cmdStr = "intents"
                handle = self.sendline( cmdStr )
            queue.put(handle)
            return handle
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def flows( self, jsonFormat=True, queue="" ):
        """
        Optional:
            * jsonFormat: enable output formatting in json
        Description:
            Obtain flows currently installed
        """
        try:
            if queue=="":
                queue = Queue.Queue()
            if jsonFormat:
                cmdStr = "flows -j"
                handle = self.sendline( cmdStr )
                ansiEscape = re.compile( r'\r\r\n\x1b[^m]*m' )
                handle = ansiEscape.sub( '', handle )
            else:
                cmdStr = "flows"
                handle = self.sendline( cmdStr )
            if re.search( "Error\sexecuting\scommand:", handle ):
                main.log.error( self.name + ".flows() response: " +
                                str( handle ) )
            queue.put(handle)
            return handle
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def pushTestIntents( self, dpidSrc, dpidDst, numIntents,
                          numMult="", appId="", report=True, queue="" ):
        """
        Description:
            Push a number of intents in a batch format to
            a specific point-to-point intent definition
        Required:
            * dpidSrc: specify source dpid
            * dpidDst: specify destination dpid
            * numIntents: specify number of intents to push
        Optional:
            * numMult: number multiplier for multiplying
              the number of intents specified
            * appId: specify the application id init to further
              modularize the intents
            * report: default True, returns latency information
        """
        try:
            if queue=="":
                queue = Queue.Queue()
            cmd = "push-test-intents " +\
                  str( dpidSrc ) + " " + str( dpidDst ) + " " +\
                  str( numIntents )
            if numMult:
                cmd += " " + str( numMult )
                # If app id is specified, then numMult
                # must exist because of the way this command
                if appId:
                    cmd += " " + str( appId )
            handle = self.sendline( cmd )
            ansiEscape = re.compile( r'\r\r\n\x1b[^m]*m' )
            handle = ansiEscape.sub( '', handle )
            if report:
                latResult = []
                main.log.info( handle )
                # Split result by newline
                newline = handle.split( "\r\r\n" )
                # Ignore the first object of list, which is empty
                newline = newline[ 1: ]
                # Some sloppy parsing method to get the latency
                for result in newline:
                    result = result.split( ": " )
                    # Append the first result of second parse
                    latResult.append( result[ 1 ].split( " " )[ 0 ] )
                main.log.info( latResult )
                queue.put(latResult)
                return latResult
            else:
                queue.put(main.TRUE)
                return main.TRUE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def intentsEventsMetrics( self, jsonFormat=True, queue="" ):
        """
        Description:Returns topology metrics
        Optional:
            * jsonFormat: enable json formatting of output
        """
        try:
            if queue=="":
                queue = Queue.Queue()
            if jsonFormat:
                cmdStr = "intents-events-metrics -j"
                handle = self.sendline( cmdStr )
                # Some color thing that we want to escape
                ansiEscape = re.compile( r'\r\r\n\x1b[^m]*m' )
                handle = ansiEscape.sub( '', handle )
            else:
                cmdStr = "intents-events-metrics"
                handle = self.sendline( cmdStr )
            queue.put(handle)
            return handle
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def topologyEventsMetrics( self, jsonFormat=True, queue="" ):
        """
        Description:Returns topology metrics
        Optional:
            * jsonFormat: enable json formatting of output
        """
        try:
            if queue=="":
                queue = Queue.Queue()
            if jsonFormat:
                cmdStr = "topology-events-metrics -j"
                handle = self.sendline( cmdStr )
                # Some color thing that we want to escape
                ansiEscape = re.compile( r'\r\r\n\x1b[^m]*m' )
                handle = ansiEscape.sub( '', handle )
            else:
                cmdStr = "topology-events-metrics"
                handle = self.sendline( cmdStr )
            queue.put(handle)
            return handle
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    # Wrapper functions ****************
    # Wrapper functions use existing driver
    # functions and extends their use case.
    # For example, we may use the output of
    # a normal driver function, and parse it
    # using a wrapper function

    def getAllIntentsId( self, queue="" ):
        """
        Description:
            Obtain all intent id's in a list
        """
        try:
            if queue=="":
                queue = Queue.Queue()
            # Obtain output of intents function
            intentsStr = self.intents()
            allIntentList = []
            intentIdList = []

            # Parse the intents output for ID's
            intentsList = [ s.strip() for s in intentsStr.splitlines() ]
            for intents in intentsList:
                if "onos>" in intents:
                    continue
                elif "intents" in intents:
                    continue
                else:
                    lineList = intents.split( " " )
                    allIntentList.append( lineList[ 0 ] )

            allIntentList = allIntentList[ 1:-2 ]

            for intents in allIntentList:
                if not intents:
                    continue
                else:
                    intentIdList.append( intents )
            queue.put(intentIdList)
            return intentIdList

        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def getAllDevicesId( self, queue=""):
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
            if queue=="":
                queue = Queue.Queue()
            # Call devices and store result string
            devicesStr = self.devices( jsonFormat=False )
            idList = []

            if not devicesStr:
                main.log.info( "There are no devices to get id from" )
                queue.put(idList)
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
            queue.put(idList)
            return idList

        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def getAllNodesId( self, queue="" ):
        """
        Uses 'nodes' function to obtain list of all nodes
        and parse the result of nodes to obtain just the
        node id's.
        Returns:
            list of node id's
        """
        try:
            if queue=="":
                queue = Queue.Queue()
            nodesStr = self.nodes()
            idList = []

            if not nodesStr:
                main.log.info( "There are no nodes to get id from" )
                queue.put(idList)
                return idList

            # Sample nodesStr output
            # id=local, address=127.0.0.1:9876, state=ACTIVE *

            # Split the string into list by comma
            nodesList = nodesStr.split( "," )
            tempList = [ node for node in nodesList if "id=" in node ]
            for arg in tempList:
                idList.append( arg.split( "id=" )[ 1 ] )
            queue.put(idList)
            return idList

        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def getDevice( self, dpid=None,queue="" ):
        """
        Return the first device from the devices api whose 'id' contains 'dpid'
        Return None if there is no match
        """
        import json
        try:
            if queue=="":
                queue = Queue.Queue()
            if dpid is None:
                queue.put(None)
                return None
            else:
                dpid = dpid.replace( ':', '' )
                rawDevices = self.devices()
                devicesJson = json.loads( rawDevices )
                # search json for the device with dpid then return the device
                for device in devicesJson:
                    # print "%s in  %s?" % ( dpid, device[ 'id' ] )
                    if dpid in device[ 'id' ]:
                        queue.put(device)
                        return device
            queue.put(None)
            return None
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def checkStatus( self, ip, numoswitch, numolink, logLevel="info", queue="" ):
        """
        Checks the number of swithes & links that ONOS sees against the
        supplied values. By default this will report to main.log, but the
        log level can be specifid.

        Params: ip = ip used for the onos cli
                numoswitch = expected number of switches
                numlink = expected number of links
                logLevel = level to log to. Currently accepts
                'info', 'warn' and 'report'


        logLevel can

        Returns: main.TRUE if the number of switchs and links are correct,
                 main.FALSE if the numer of switches and links is incorrect,
                 and main.ERROR otherwise
        """
        try:
            if queue=="":
                queue = Queue.Queue()
            topology = self.getTopology( ip )
            if topology == {}:
                queue.put(main.ERROR)
                return main.ERROR
            output = ""
            # Is the number of switches is what we expected
            devices = topology.get( 'devices', False )
            links = topology.get( 'links', False )
            if devices == False or links == False:
                queue.put(main.ERROR)
                return main.ERROR
            switchCheck = ( int( devices ) == int( numoswitch ) )
            # Is the number of links is what we expected
            linkCheck = ( int( links ) == int( numolink ) )
            if ( switchCheck and linkCheck ):
                # We expected the correct numbers
                output = output + "The number of links and switches match "\
                    + "what was expected"
                result = main.TRUE
            else:
                output = output + \
                    "The number of links and switches does not matc\
                    h what was expected"
                result = main.FALSE
            output = output + "\n ONOS sees %i devices (%i expected) \
                    and %i links (%i expected)" % (
                int( devices ), int( numoswitch ), int( links ),
                int( numolink ) )
            if logLevel == "report":
                main.log.report( output )
            elif logLevel == "warn":
                main.log.warn( output )
            else:
                main.log.info( output )
            queue.put(result)
            return result
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
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
                if re.search( "Error", handle ):
                    # end color output to escape any colours
                    # from the cli
                    main.log.error( self.name + ": " +
                                    handle + '\033[0m' )
                    queue.put(main.ERROR)
                    return main.ERROR
                queue.put(main.TRUE)
                return main.TRUE
            else:
                main.log.error( "Invalid 'role' given to device_role(). " +
                                "Value was '" + str(role) + "'." )
                queue.put(main.FALSE)
                return main.FALSE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put(None)
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
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
            if jsonFormat:
                cmdStr = "clusters -j"
                handle = self.sendline( cmdStr )
                """
                handle variable here contains some ANSI escape color code
                sequences at the end which are invisible in the print command
                output. To make that escape sequence visible, use repr()
                function. The repr( handle ) output when printed shows the ANSI
                escape sequences. In json.loads( somestring ), this somestring
                variable is actually repr( somestring ) and json.loads would
                fail with the escape sequence. So we take off that escape
                sequence using:

                ansiEscape = re.compile( r'\r\r\n\x1b[^m]*m' )
                handle1 = ansiEscape.sub( '', handle )
                """
                ansiEscape = re.compile( r'\r\r\n\x1b[^m]*m' )
                handle1 = ansiEscape.sub( '', handle )
                return handle1
            else:
                cmdStr = "clusters"
                handle = self.sendline( cmdStr )
                return handle
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
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
            errorPattern = "Command\snot\sfound"
            if re.search( errorPattern, response ):
                main.log.error( "Election app is not loaded on " + self.name )
                # TODO: Should this be main.ERROR?
                return main.FALSE
            else:
                main.log.error( "Error in election_test_leader: " +
                                "unexpected response" )
                main.log.error( repr( response ) )
                return main.FALSE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
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
            # success
            successPattern = "Entering\sleadership\selections\sfor\sthe\s" +\
                "Election\sapp."
            search = re.search( successPattern, response )
            if search:
                main.log.info( self.name + " entering leadership elections " +
                               "for the Election app." )
                return main.TRUE
            # error
            errorPattern = "Command\snot\sfound"
            if re.search( errorPattern, response ):
                main.log.error( "Election app is not loaded on " + self.name )
                return main.FALSE
            else:
                main.log.error( "Error in election_test_run: " +
                                "unexpected response" )
                main.log.error( repr( response ) )
                return main.FALSE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
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
            # success
            successPattern = "Withdrawing\sfrom\sleadership\selections\sfor" +\
                "\sthe\sElection\sapp."
            if re.search( successPattern, response ):
                main.log.info( self.name + " withdrawing from leadership " +
                               "elections for the Election app." )
                return main.TRUE
            # error
            errorPattern = "Command\snot\sfound"
            if re.search( errorPattern, response ):
                main.log.error( "Election app is not loaded on " + self.name )
                return main.FALSE
            else:
                main.log.error( "Error in election_test_withdraw: " +
                                "unexpected response" )
                main.log.error( repr( response ) )
                return main.FALSE
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def getDevicePortsEnabledCount( self, dpid, queue="" ):
        """
        Get the count of all enabled ports on a particular device/switch
        """
        try:
            if queue=="":
                queue = Queue.Queue()
            dpid = str( dpid )
            cmdStr = "onos:ports -e " + dpid + " | wc -l"
            output = self.sendline( cmdStr )
            if re.search( "No such device", output ):
                main.log.error( "Error in getting ports" )
                queue.put((output,"Error"))
                return ( output, "Error" )
            else:
                queue.put(output)
                return output
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put((output,"Error"))
            return ( output, "Error" )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def getDeviceLinksActiveCount( self, dpid, queue="" ):
        """
        Get the count of all enabled ports on a particular device/switch
        """
        try:
            if queue=="":
                queue = Queue.Queue()
            dpid = str( dpid )
            cmdStr = "onos:links " + dpid + " | grep ACTIVE | wc -l"
            output = self.sendline( cmdStr )
            if re.search( "No such device", output ):
                main.log.error( "Error in getting ports " ) 
                queue.put((output,"Error"))
                return ( output, "Error " )
            else:
                queue.put(output)
                return output
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put((output,"Error"))
            return ( output, "Error " )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def getAllIntentIds( self ,queue=""):
        """
        Return a list of all Intent IDs
        """
        try:
            if queue=="":
                queue = Queue.Queue()
            cmdStr = "onos:intents | grep id="
            output = self.sendline( cmdStr )
            if re.search( "Error", output ):
                main.log.error( "Error in getting ports" )
                queue.put((output,"Error"))
                return ( output, "Error" )
            else:
                queue.put(output)
                return output
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            queue.put((output,"Error"))
            return ( output, "Error" )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def testExceptions( self, obj ):
        """
        Test exception logging
        """
        # FIXME: Remove this before you commit

        try:
            return obj[ 'dedf' ]
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()
