#!/usr/bin/env python
"""
Created on 24-Oct-2012
Copyright 2012 Open Networking Foundation (ONF)

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
import pexpect
import re
import os

from drivers.component import Component


class CLI( Component ):

    """
        This will define common functions for CLI included.
    """
    def __init__( self ):
        super( CLI, self ).__init__()
        self.inDocker = False
        self.portForwardList = None

    def checkPrompt( self ):
        for key in self.options:
            if key == "prompt" and self.options[ 'prompt' ] is not None:
                self.prompt = self.options[ 'prompt' ]
                break

    def connect( self, **connectargs ):
        """
           Connection will establish to the remote host using ssh.
           It will take user_name ,ip_address and password as arguments<br>
           and will return the handle.
        """
        self.shell = "/bin/bash -l"
        for key in connectargs:
            vars( self )[ key ] = connectargs[ key ]
        self.checkPrompt()

        connect_result = super( CLI, self ).connect()
        ssh_newkey = 'Are you sure you want to continue connecting'
        refused = "ssh: connect to host " + \
            self.ip_address + " port 22: Connection refused"
        ssh_options = "-t -X -A -o ServerAliveInterval=50 -o ServerAliveCountMax=1000 -o TCPKeepAlive=yes"
        ssh_destination = self.user_name + "@" + self.ip_address
        envVars = { "TERM": "vt100" }
        # TODO: Add option to specify which shell/command to use
        jump_host = main.componentDictionary[ self.name ].get( 'jump_host' )
        if self.port:
            ssh_option += " -p " + self.port
        if jump_host:
            jump_host = main.componentDictionary.get( jump_host )
            ssh_options += " -J %s@%s" % ( jump_host.get( 'user' ), jump_host.get( 'host' ) )
        ssh_auth = os.getenv('SSH_AUTH_SOCK')
        if ssh_auth:
            envVars[ 'SSH_AUTH_SOCK' ] = ssh_auth
        self.handle = pexpect.spawn(
            "ssh %s %s %s" % ( ssh_options, ssh_destination, self.shell ),
            env=envVars,
            maxread=1000000,
            timeout=60 )

        # set tty window size
        self.handle.setwinsize( 24, 250 )

        self.handle.logfile = self.logfile_handler
        i = 5
        while i == 5:
            i = self.handle.expect( [ ssh_newkey,
                                      'password:|Password:',
                                      pexpect.EOF,
                                      pexpect.TIMEOUT,
                                      refused,
                                      'teston>',
                                      'Permission denied, please try again.',
                                      self.prompt ],
                                    120 )
            if i == 0:  # Accept key, then expect either a password prompt or access
                main.log.info( self.name + ": ssh key confirmation received, send yes" )
                self.handle.sendline( 'yes' )
                i = 5  # Run the loop again
                continue
            if i == 1:  # Password required
                if self.pwd:
                    main.log.info(
                            "ssh connection asked for password, gave password" )
                else:
                    main.log.info( self.name + ": Server asked for password, but none was "
                                    "given in the .topo file. Trying "
                                    "no password." )
                    self.pwd = ""
                self.handle.sendline( self.pwd )
                j = self.handle.expect( [
                                        'password:|Password:',
                                        'Permission denied, please try again.',
                                        self.prompt,
                                        pexpect.EOF,
                                        pexpect.TIMEOUT ],
                                        120 )
                if j != 2:
                    main.log.error( self.name + ": Incorrect Password" )
                    return main.FALSE
            elif i == 2:
                main.log.error( self.name + ": Connection timeout" )
                main.log.debug( self.handle.before )
                return main.FALSE
            elif i == 3:  # timeout
                main.log.error(
                    "No route to the Host " +
                    self.user_name +
                    "@" +
                    self.ip_address )
                main.log.debug( self.handle.before )
                return main.FALSE
            elif i == 4:
                main.log.error(
                    "ssh: connect to host " +
                    self.ip_address +
                    " port 22: Connection refused" )
                main.log.debug( self.handle.before )
                return main.FALSE
            elif i == 6:  # Incorrect Password
                main.log.error( self.name + ": Incorrect Password" )
                main.log.debug( self.handle.before )
                return main.FALSE
            elif i == 7:  # Prompt
                main.log.info( self.name + ": Password not required logged in" )

        self.handle.sendline( "" )
        self.handle.expect( self.prompt )

        # disable bracketed paste mode which is enabled by default on newer versions of bash/readline
        self.handle.sendline( "bind 'set enable-bracketed-paste off'" )
        self.handle.expect( self.prompt )

        self.handle.sendline( "cd" )
        self.handle.expect( self.prompt )
        return self.handle

    def disconnect( self ):
        result = self.preDisconnect()
        result = super( CLI, self ).disconnect( )
        result = main.TRUE

    def Prompt( self ):
        """
        Returns the prompt to expect depending on what program we are in
        """
        return self.prompt if not self.inDocker else self.dockerPrompt

    def execute( self, **execparams ):
        """
        It facilitates the command line execution of a given command. It has arguments as :
        cmd => represents command to be executed,
        prompt => represents expect command prompt or output,
        timeout => timeout for command execution,
        more => to provide a key press if it is on.
        logCmd => log the command executed if True

        It will return output of command exection.
        """
        result = super( CLI, self ).execute( self )
        defaultPrompt = '.*[$>\#]'
        args = utilities.parse_args( [ "CMD",
                                       "TIMEOUT",
                                       "PROMPT",
                                       "MORE",
                                       "LOGCMD" ],
                                     **execparams )

        expectPrompt = args[ "PROMPT" ] if args[ "PROMPT" ] else defaultPrompt
        self.LASTRSP = ""
        timeoutVar = args[ "TIMEOUT" ] if args[ "TIMEOUT" ] else 10
        cmd = ''
        if args[ "CMD" ]:
            cmd = args[ "CMD" ]
        else:
            return 0
        if args[ "MORE" ] is None:
            args[ "MORE" ] = " "
        self.handle.sendline( cmd )
        self.lastCommand = cmd
        index = self.handle.expect( [ expectPrompt,
                                      "--More--",
                                      'Command not found.',
                                      pexpect.TIMEOUT,
                                      "^:$" ],
                                    timeout=timeoutVar )
        if index == 0:
            self.LASTRSP = self.LASTRSP + \
                self.handle.before + self.handle.after
            if not args[ "LOGCMD" ] is False:
                main.log.info( self.name + ": Executed :" + str( cmd ) +
                               " \t\t Expected Prompt '" + str( expectPrompt ) +
                               "' Found" )
        elif index == 1:
            self.LASTRSP = self.LASTRSP + self.handle.before
            self.handle.send( args[ "MORE" ] )
            main.log.info(
                "Found More screen to go , Sending a key to proceed" )
            indexMore = self.handle.expect(
                [ "--More--", expectPrompt ], timeout=timeoutVar )
            while indexMore == 0:
                main.log.info(
                    "Found anoother More screen to go , Sending a key to proceed" )
                self.handle.send( args[ "MORE" ] )
                indexMore = self.handle.expect(
                    [ "--More--", expectPrompt ], timeout=timeoutVar )
                self.LASTRSP = self.LASTRSP + self.handle.before
        elif index == 2:
            main.log.error( self.name + ": Command not found" )
            self.LASTRSP = self.LASTRSP + self.handle.before
        elif index == 3:
            main.log.error( self.name + ": Expected Prompt not found, Time Out!!" )
            main.log.error( expectPrompt )
            self.LASTRSP = self.LASTRSP + self.handle.before
            return self.LASTRSP
        elif index == 4:
            self.LASTRSP = self.LASTRSP + self.handle.before
            # self.handle.send( args[ "MORE" ] )
            self.handle.sendcontrol( "D" )
            main.log.info(
                "Found More screen to go, Sending a key to proceed" )
            indexMore = self.handle.expect(
                [ "^:$", expectPrompt ], timeout=timeoutVar )
            while indexMore == 0:
                main.log.info(
                    "Found another More screen to go, Sending a key to proceed" )
                self.handle.sendcontrol( "D" )
                indexMore = self.handle.expect(
                    [ "^:$", expectPrompt ], timeout=timeoutVar )
                self.LASTRSP = self.LASTRSP + self.handle.before
        main.last_response = self.remove_contol_chars( self.LASTRSP )
        return self.LASTRSP

    def remove_contol_chars( self, response ):
        # RE_XML_ILLEGAL = '([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])|([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])'%( unichr( 0xd800 ),unichr( 0xdbff ),unichr( 0xdc00 ),unichr( 0xdfff ),unichr( 0xd800 ),unichr( 0xdbff ),unichr( 0xdc00 ),unichr( 0xdfff ),unichr( 0xd800 ),unichr( 0xdbff ),unichr( 0xdc00 ),unichr( 0xdfff ) )
        # response = re.sub( RE_XML_ILLEGAL, "\n", response )
        response = re.sub( r"[\x01-\x1F\x7F]", "", response )
        # response = re.sub( r"\[\d+\;1H", "\n", response )
        response = re.sub( r"\[\d+\;\d+H", "", response )
        return response

    def runAsSudoUser( self, handle, pwd, default ):

        i = handle.expect( [ ".ssword:*", default, pexpect.EOF ] )
        if i == 0:
            handle.sendline( pwd )
            handle.sendline( "\n" )

        if i == 1:
            handle.expect( default )

        if i == 2:
            main.log.error( self.name + ": Unable to run as Sudo user" )

        return handle

    def onfail( self ):
        if 'onfail' in main.componentDictionary[ self.name ]:
            commandList = main.componentDictionary[
                self.name ][ 'onfail' ].split( "," )
            for command in commandList:
                response = self.execute(
                    cmd=command,
                    prompt="(.*)",
                    timeout=120 )

    def secureCopy( self, userName, ipAddress, filePath, dstPath, pwd="",
                    direction="from", options="", timeout=120 ):
        """
        Definition:
            Execute scp command in linux to copy to/from a remote host
        Required:
            str userName - User name of the remote host
            str ipAddress - IP address of the remote host
            str filePath - File path including the file it self
            str dstPath - Destination path
        Optional:
            str pwd - Password of the host
            str direction - Direction of the scp, default to "from" which means
                            copy "from" the remote machine to local machine,
                            while "to" means copy "to" the remote machine from
                            local machine
        """
        returnVal = main.FALSE
        ssh_newkey = 'Are you sure you want to continue connecting'
        refused = "ssh: connect to host " + \
                  ipAddress + " port 22: Connection refused"
        cmd = "scp %s " % options
        try:
            self.handle.sendline( "" )
            self.handle.expect( self.prompt, timeout=5 )
        except pexpect.TIMEOUT:
            main.log.error( "%s: Component not ready for input" % self.name )
            main.log.debug( "%s: %s%s" % ( self.name, self.handle.before, str( self.handle.after ) ) )
            self.handle.send( "\x03" )  # CTRL-C
            self.handle.expect( self.prompt, timeout=5 )

        if direction == "from":
            cmd = cmd + str( userName ) + '@' + str( ipAddress ) + ':' + \
                  str( filePath ) + ' ' + str( dstPath )
        elif direction == "to":
            cmd = cmd + str( filePath ) + ' ' + str( userName ) + \
                  '@' + str( ipAddress ) + ':' + str( dstPath )
        else:
            main.log.debug( "Wrong direction using secure copy command!" )
            return main.FALSE

        main.log.info( self.name + ": Sending: " + cmd )
        self.handle.sendline( cmd )
        i = 0
        hit = False
        while i <= 6 :
            i = self.handle.expect( [
                                ssh_newkey,
                                'password:',
                                "100%",
                                refused,
                                "No such file or directory",
                                "Permission denied",
                                self.prompt,
                                pexpect.EOF,
                                pexpect.TIMEOUT ],
                                timeout=timeout )
            if i == 0:  # ask for ssh key confirmation
                hit = True
                main.log.info( self.name + ": ssh key confirmation received, sending yes" )
                self.handle.sendline( 'yes' )
            elif i == 1:  # Asked for ssh password
                hit = True
                timeout = 120
                main.log.info( self.name + ": ssh connection asked for password, gave password" )
                self.handle.sendline( pwd )
            elif i == 2:  # File finished transfering
                hit = True
                main.log.info( self.name + ": Secure copy successful" )
                timeout = 10
                returnVal = main.TRUE
            elif i == 3:  # Connection refused
                hit = True
                main.log.error(
                    "ssh: connect to host " +
                    ipAddress +
                    " port 22: Connection refused" )
                returnVal = main.FALSE
            elif i == 4:  # File Not found
                hit = True
                main.log.error( self.name + ": No such file found" )
                main.log.debug( self.handle.before + self.handle.after )
                returnVal = main.FALSE
            elif i == 5:  # Permission denied
                hit = True
                main.log.error( self.name + ": Permission denied. Check folder permissions" )
                main.log.debug( self.handle.before + self.handle.after )
                returnVal = main.FALSE
            elif i == 6:  # prompt returned
                hit = True
                timeout = 10
                main.log.debug( "%s: %s%s" % ( self.name, repr( self.handle.before ), repr( self.handle.after ) ) )
            elif i == 7:  # EOF
                hit = True
                main.log.error( self.name + ": Pexpect.EOF found!!!" )
                main.cleanAndExit()
            elif i == 8:  # timeout
                if not hit:
                    main.log.error(
                        "No route to the Host " +
                        userName +
                        "@" +
                        ipAddress )
                return returnVal
        self.handle.expect( [ self.prompt, pexpect.TIMEOUT ], timeout=5 )
        main.log.debug( "%s: %s%s" % ( self.name, repr( self.handle.before ), repr( self.handle.after ) ) )
        return returnVal

    def scp( self, remoteHost, filePath, dstPath, direction="from", options="", timeout=120 ):
        """
        Definition:
            Execute scp command in linux to copy to/from a remote host
        Required:
            * remoteHost - Test ON component to be parsed
            str filePath - File path including the file it self
            str dstPath - Destination path
        Optional:
            str direction - Direction of the scp, default to "from" which means
                            copy "from" the remote machine to local machine,
                            while "to" means copy "to" the remote machine from
                            local machine
        """
        jump_host = main.componentDictionary[ remoteHost.name ].get( 'jump_host' )
        if jump_host:
            jump_host = main.componentDictionary.get( jump_host )
            options += " -o 'ProxyJump %s@%s' " % ( jump_host.get( 'user' ), jump_host.get( 'host' ) )
        return self.secureCopy( remoteHost.user_name,
                                remoteHost.ip_address,
                                filePath,
                                dstPath,
                                pwd=remoteHost.pwd,
                                direction=direction,
                                options=options,
                                timeout=timeout )

    def sshToNode( self, ipAddress, uName="sdn", pwd="rocks" ):
        ssh_newkey = 'Are you sure you want to continue connecting'
        refused = "ssh: connect to host " + ipAddress + " port 22: Connection refused"
        handle = pexpect.spawn( 'ssh -X ' +
                                uName +
                                '@' +
                                ipAddress,
                                env={ "TERM": "vt100" },
                                maxread=1000000,
                                timeout=60 )

        # set tty window size
        handle.setwinsize( 24, 250 )

        i = 5
        while i == 5:
            i = handle.expect( [ ssh_newkey,
                                 'password:|Password:',
                                 pexpect.EOF,
                                 pexpect.TIMEOUT,
                                 refused,
                                 'teston>',
                                 self.prompt ],
                               120 )
            if i == 0:  # Accept key, then expect either a password prompt or access
                main.log.info( self.name + ": ssh key confirmation received, send yes" )
                handle.sendline( 'yes' )
                i = 5  # Run the loop again
                continue
            if i == 1:  # Password required
                if pwd:
                    main.log.info(
                            "ssh connection asked for password, gave password" )
                else:
                    main.log.info( self.name + ": Server asked for password, but none was "
                                    "given in the .topo file. Trying "
                                    "no password." )
                    pwd = ""
                handle.sendline( pwd )
                j = handle.expect( [ self.prompt,
                                     'password:|Password:',
                                     pexpect.EOF,
                                     pexpect.TIMEOUT ],
                                     120 )
                if j != 0:
                    main.log.error( self.name + ": Incorrect Password" )
                    main.cleanAndExit()
            elif i == 2:
                main.log.error( self.name + ": Connection timeout" )
                main.cleanAndExit()
            elif i == 3:  # timeout
                main.log.error(
                    "No route to the Host " +
                    uName +
                    "@" +
                    ipAddress )
                main.cleanAndExit()
            elif i == 4:
                main.log.error(
                    "ssh: connect to host " +
                    ipAddress +
                    " port 22: Connection refused" )
                main.cleanAndExit()
            elif i == 6:
                main.log.info( self.name + ": Password not required logged in" )

        handle.sendline( "" )
        handle.expect( self.prompt )
        handle.sendline( "cd" )
        handle.expect( self.prompt )

        main.log.info( self.name + ": Successfully ssh to " + ipAddress + "." )
        return handle

    def exitFromSsh( self, handle, ipAddress ):
        try:
            handle.sendline( "logout" )
            handle.expect( "closed." )
            main.log.info( self.name + ": Successfully closed ssh connection from " + ipAddress )
        except pexpect.EOF:
            main.log.error( self.name + ": Failed to close the connection from " + ipAddress )
        try:
            # check that this component handle still works
            self.handle.sendline( "" )
            self.handle.expect( self.prompt )
        except pexpect.EOF:
            main.log.error( self.handle.before )
            main.log.error( self.name + ": EOF after closing ssh connection" )

    def folderSize( self, path, size='10', unit='M', ignoreRoot=True ):
        """
        Run `du -h` on the folder path and verifies the folder(s) size is
        less than the given size. Note that if multiple subdirectories are
        present, the result will be the OR of all the individual subdirectories.

        Arguments:
        path - A string containing the path supplied to the du command
        size - The number portion of the file size that the results will be compared to
        unit - The unit portion of the file size that the results will be compared to
        ignoreRoot - If True, will ignore the "root" of the path supplied to du. I.E. will ignore `.`

        Returns True if the folder(s) size(s) are less than SIZE UNITS, else returns False
        """
        sizeRe = r'(?P<number>\d+\.*\d*)(?P<unit>\D)'
        unitsList = [ 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y' ]
        try:
            # make sure we convert units if size is too big
            size = float( size )
            if size >= 1000:
                size = size / 1000
                unit = unitsList[ unitsList.index( unit + 1 ) ]
            cmdStr = "du -h " + path
            self.handle.sendline( cmdStr )
            self.handle.expect( self.prompt )
            output = self.handle.before
            assert "cannot access" not in output
            assert "command not found" not in output
            main.log.debug( output )
            lines = [ line for line in output.split( '\r\n' ) ]
            retValue = True
            if ignoreRoot:
                lastIndex = -2
            else:
                lastIndex = -1
            for line in lines[ 1:lastIndex ]:
                parsed = line.split()
                sizeMatch = parsed[ 0 ]
                folder = parsed[ 1 ]
                match = re.search( sizeRe, sizeMatch )
                num = match.group( 'number' )
                unitMatch = match.group( 'unit' )
                if unitsList.index( unitMatch ) < unitsList.index( unit ):
                    retValue &= True
                elif unitsList.index( unitMatch ) == unitsList.index( unit ):
                    if float( num ) < float( size ):
                        retValue &= True
                    else:
                        retValue &= False
                elif unitsList.index( unitMatch ) > unitsList.index( unit ):
                    retValue &= False
            return retValue
        except AssertionError:
            main.log.error( self.name + ": Could not execute command: " + output )
            return False
        except ValueError as e:
            main.log.error( self.name + ": Error parsing output: " + output )
            main.log.error( e )
            return False
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            return False
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()

    def fileSize( self, path, inBytes=True ):
        """
        Run `du` on the file path and returns the file size

        Arguments:
        path - A string containing the path supplied to the du command
        Optional Arguments:
        inBytes - Display size in bytes, defaults to true

        Returns the size of the file as an int
        """
        sizeRe = r'(?P<number>\d+\.*\d*)(?P<unit>\D)'
        try:
            cmdStr = "du %s %s" % ( "-b" if inBytes else "", path )
            self.handle.sendline( cmdStr )
            self.handle.expect( self.prompt )
            output = self.handle.before
            assert "cannot access" not in output
            assert "command not found" not in output
            assert "No such file or directory" not in output
            main.log.debug( output )
            lines = [ line for line in output.split( '\r\n' ) ]
            return int( lines[1].split()[0] )
        except AssertionError:
            main.log.error( self.name + ": Could not execute command: " + output )
            return False
        except ValueError as e:
            main.log.error( self.name + ": Error parsing output: " + output )
            main.log.error( e )
            return False
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            return False
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()

    def setEnv( self, variable, value=None ):
        """
        Sets the environment variable to the given value for the current shell session.
        If value is None, will unset the variable.

        Required Arguments:
        variable - The name of the environment variable to set.

        Optional Arguments:
        value - The value to set the variable to. ( Defaults to None, which unsets the variable )

        Returns True if no errors are detected else returns False
        """
        try:
            if value:
                cmd = "export {}={}".format( variable, value )
            else:
                cmd = "unset {}".format( variable )
            self.handle.sendline( cmd )
            self.handle.expect( self.prompt )
            output = self.handle.before
            main.log.debug( output )
            return True
        except AssertionError:
            main.log.error( self.name + ": Could not execute command: " + output )
            return False
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            return False
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanAndExit()

    def exitFromCmd( self, expect, retry=10 ):
        """
        Call this function when sending ctrl+c is required to kill the current
        command. It will retry multiple times until the running command is
        completely killed and expected string is returned from the handle.
        Required:
            expect: expected string or list of strings which indicates that the
                    previous command was killed successfully.
        Optional:
            retry: maximum number of ctrl+c that will be sent.
        """
        expect = [ expect ] if isinstance( expect, str ) else expect
        try:
            while retry >= 0:
                main.log.debug( self.name + ": sending ctrl+c to kill the command" )
                self.handle.send( "\x03" )
                i = self.handle.expect( expect + [ pexpect.TIMEOUT ], timeout=3 )
                main.log.debug( self.handle.before )
                if i < len( expect ):
                    main.log.debug( self.name + ": successfully killed the command" )
                    return main.TRUE
                retry -= 1
            main.log.warn( self.name + ": failed to kill the command" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return main.FALSE

    def cleanOutput( self, output, debug=False ):
        """
        Clean ANSI characters from output
        """
        ansiEscape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        cleaned = ansiEscape.sub( '', output )
        if debug:
            main.log.debug( self.name + ": cleanOutput:" )
            main.log.debug( self.name + ": " + repr( cleaned ) )
        return cleaned

    def dockerPull( self, image, tag=None ):
        """
        Pull a docker image from a registry
        """
        try:
            imgStr = "%s%s" % ( image, ":%s" % tag if tag else "" )
            cmdStr = "docker pull %s" % imgStr
            main.log.info( self.name + ": sending: " + cmdStr )
            self.handle.sendline( cmdStr)
            i = self.handle.expect( [ self.prompt,
                                      "Error response from daemon",
                                      pexpect.TIMEOUT ], 120 )
            if i == 0:
                return main.TRUE
            else:
                main.log.error( self.name + ": Error pulling docker image " + imgStr  )
                output = self.handle.before + str( self.handle.after )
                if i == 1:
                    self.handle.expect( self.prompt )
                    output += self.handle.before + str( self.handle.after )
                main.log.debug( self.name + ": " + output )
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return main.FALSE

    def dockerBuild( self, path, imageTag, pull=False, options="", timeout=600 ):
        """
        Build a docker image
        Required Arguments:
         - path: Path to the dockerfile, it is recommended to avoid relative paths
         - imageTag: Give a tag to the built docker image
        Optional Arguments:
         - pull: Whether to attempt to pull latest images before building
         - options: A string containing any addition optional arguments
                    for the docker build command
         - timeout: How many seconds to wait for the build to complete
        """
        try:
            response = main.TRUE
            if pull:
                options = "--pull " + options
            cmdStr = "docker build -t %s %s %s" % ( imageTag, options, path )
            main.log.info( self.name + ": sending: " + cmdStr )
            self.handle.sendline( cmdStr)
            i = self.handle.expect( [ "Successfully built",
                                      "Error response from daemon",
                                      pexpect.TIMEOUT ], timeout=timeout )
            output = self.handle.before
            if i == 0:
                output += self.handle.after
                self.handle.expect( self.prompt )
                output += self.handle.before + self.handle.after
                return response
            elif i == 1:
                response = main.FALSE
                output += self.handle.after
                self.handle.expect( self.prompt )
                output += self.handle.before + self.handle.after
            elif i == 2:
                response = main.FALSE
            main.log.error( self.name + ": Error building docker image" )
            main.log.debug( self.name + ": " + output )
            return response
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return main.FALSE

    def dockerStop( self, containerName ):
        """
        Stop a docker container
        Required Arguments:
         - containerName: Name of the container to stop
        """
        try:
            cmdStr = "docker stop %s" % ( containerName )
            main.log.info( self.name + ": sending: " + cmdStr )
            self.handle.sendline( cmdStr)
            i = self.handle.expect( [ self.prompt,
                                      "Error response from daemon",
                                      pexpect.TIMEOUT ], 120 )
            output = self.handle.before
            if i == 0:
                return main.TRUE
            elif i == 1:
                output += self.handle.after
                self.handle.expect( self.prompt )
                output += self.handle.before
            elif i == 2:
                pass
            main.log.debug( "%s: %s" % ( self.name, output ) )
            if "No such container" in output:
                return main.TRUE
            main.log.error( self.name + ": Error stopping docker image" )
            main.log.debug( self.name + ": " + output )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return main.FALSE

    def dockerRun( self, image, containerName, options="", imageArgs="", background=False ):
        """
        Run a docker image
        Required Arguments:
         - containerName: Give a name to the container once its started
         - image: Run the given image
        Optional Arguments:
         - options: A string containing any addition optional arguments
                    for the docker run command
        - imageArgs: A string containing command line arguments for the
                     command run by docker
        """
        try:
            cmdStr = "docker run --name %s %s %s %s" % ( containerName,
                                                         options if options else "",
                                                         image,
                                                         imageArgs )
            if background:
                cmdStr += " &"
            main.log.info( self.name + ": sending: " + cmdStr )
            self.handle.sendline( cmdStr)
            i = self.handle.expect( [ self.prompt,
                                      "Error response from daemon",
                                      pexpect.TIMEOUT ], 120 )
            if i == 0:
                return main.TRUE
            else:
                output = self.handle.before
                main.log.debug( self.name + ": " + output )
                main.log.error( self.name + ": Error running docker image" )
                if i == 1:
                    output += self.handle.after
                    self.handle.expect( self.prompt )
                    output += self.handle.before + self.handle.after
                main.log.debug( self.name + ": " + output )
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return main.FALSE

    def dockerAttach( self, containerName, dockerPrompt="" ):
        """
        Attach to a docker image
        Required Arguments:
         - containerName: The name of the container to attach to
        Optional Arguments:
         - dockerPrompt: a regex for matching the docker shell prompt
        """
        try:
            if dockerPrompt:
                self.dockerPrompt = dockerPrompt
            cmdStr = "docker attach %s" % containerName
            main.log.info( self.name + ": sending: " + cmdStr )
            self.handle.sendline( cmdStr)
            i = self.handle.expect( [ self.dockerPrompt,
                                      "Error response from daemon",
                                      pexpect.TIMEOUT ] )
            if i == 0:
                self.inDocker = True
                return main.TRUE
            else:
                main.log.error( self.name + ": Error connecting to docker container" )
                output = self.handle.before + str( self.handle.after )
                if i == 1:
                    self.handle.expect( self.prompt )
                    output += self.handle.before + str( self.handle.after )
                main.log.debug( self.name + ": " + output )
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except AttributeError as e:
            main.log.exception( self.name + ": AttributeError - " + str( e ) )
            main.log.warn( self.name + ": Make sure dockerPrompt is set" )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return main.FALSE

    def dockerExec( self, containerName, command="/bin/bash", options="-it", dockerPrompt="" ):
        """
        Attach to a docker image
        Required Arguments:
         - containerName: The name of the container to attach to
        Optional Arguments:
         - command: Command to run in the docker container
         - options: Docker exec options
         - dockerPrompt: a regex for matching the docker shell prompt
        """
        try:
            if dockerPrompt:
                self.dockerPrompt = dockerPrompt
            cmdStr = "docker exec %s %s %s" % ( options, containerName, command )
            main.log.info( self.name + ": sending: " + cmdStr )
            self.handle.sendline( cmdStr)
            i = self.handle.expect( [ self.dockerPrompt,
                                      "Error response from daemon",
                                      pexpect.TIMEOUT ] )
            if i == 0:
                self.inDocker = True
                return main.TRUE
            else:
                main.log.error( self.name + ": Error connecting to docker container" )
                output = self.handle.before + str( self.handle.after )
                if i == 1:
                    self.handle.expect( self.prompt )
                    output += self.handle.before + str( self.handle.after )
                main.log.debug( self.name + ": " + output )
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except AttributeError as e:
            main.log.exception( self.name + ": AttributeError - " + str( e ) )
            main.log.warn( self.name + ": Make sure dockerPrompt is set" )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return main.FALSE

    def dockerCp( self, containerName, dockerPath, hostPath, direction="from" ):
        """
        Copy a file from/to a docker container to the host
        Required Arguments:
         - containerName: The name of the container to copy from/to
         - dockerPath: the path in the container to copy from/to
         - hostPath: the path on the host to copy to/from
        Optional Arguments:
         - direction: Choose whether to copy "from" the container or "to" the container
        """
        try:
            cmdStr = "docker cp "
            if direction == "from":
                cmdStr += "%s:%s %s" % ( containerName, dockerPath, hostPath )
            elif direction == "to":
                cmdStr += "%s %s:%s" % ( hostPath, containerName, dockerPath )
            main.log.info( self.name + ": sending: " + cmdStr )
            self.handle.sendline( cmdStr)
            i = self.handle.expect( [ self.prompt,
                                      "Error",
                                      pexpect.TIMEOUT ] )
            if i == 0:
                retValue = main.TRUE
            else:
                main.log.error( self.name + ": Error in docker cp" )
                output = self.handle.before + str( self.handle.after )
                if i == 1:
                    self.handle.expect( self.prompt )
                    output += self.handle.before + str( self.handle.after )
                main.log.debug( self.name + ": " + output )
                retValue = main.FALSE
            return retValue
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except AttributeError as e:
            main.log.exception( self.name + ": AttributeError - " + str( e ) )
            main.log.warn( self.name + ": Make sure dockerPrompt is set" )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return main.FALSE

    def dockerDisconnect( self ):
        """
        Send ctrl-c, ctrl-d to session, which should close and exit the
        attached docker session. This will likely exit the running program
        in the container and also stop the container.
        """
        try:
            cmdStr = "\x03"
            main.log.info( self.name + ": sending: " + repr( cmdStr ) )
            self.handle.send( cmdStr)
            cmdStr = "\x04"
            main.log.info( self.name + ": sending: " + repr( cmdStr ) )
            self.handle.send( cmdStr)
            i = self.handle.expect( [ self.prompt, pexpect.TIMEOUT ] )
            if i == 0:
                self.inDocker = False
                return main.TRUE
            else:
                main.log.error( self.name + ": Error disconnecting from docker image" )
                main.log.debug( self.name + ": " + self.handle.before + str( self.handle.after ) )
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return main.FALSE

# TODO: How is this different from exitFromCmd used elsewhere?
    def exitFromProcess( self ):
        """
        Send ctrl-c, which should close and exit the program
        """
        try:
            cmdStr = "\x03"
            main.log.info( self.name + ": sending: " + repr( cmdStr ) )
            self.handle.send( cmdStr)
            i = self.handle.expect( [ self.prompt, pexpect.TIMEOUT ] )
            if i == 0:
                return main.TRUE
            else:
                main.log.error( self.name + ": Error exiting process" )
                main.log.debug( self.name + ": " + self.handle.before + str( self.handle.after ) )
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return main.FALSE

    def preDisconnect( self ):
        """
        A Stub for a function that will be called before disconnect.
        This can be set if for instance, the shell is running a program
        and needs to exit the program before disconnecting from the component
        """
        print "preDisconnect"
        return main.TRUE

    def kubectlGetPodNames( self, kubeconfig=None, namespace=None, app=None, name=None,
                            nodeName=None, status=None ):
        """
        Use kubectl to get the names of pods
        Optional Arguments:
        - kubeconfig: The path to a kubeconfig file
        - namespace: The namespace to search in
        - app: Get pods belonging to a specific app
        - name: Get pods with a specific name label
        - nodeName: Get pods on a specific node
        - status: Get pods with the specified Status
        Returns a list containing the names of the pods or
            main.FALSE on Error
        """

        try:
            self.handle.sendline( "" )
            self.handle.expect( self.prompt )
            main.log.debug( self.handle.before + self.handle.after )
            cmdStr = "kubectl %s %s get pods %s %s %s %s --output=jsonpath='{.items..metadata.name}{\"\\n\"}'" % (
                        "--kubeconfig %s" % kubeconfig if kubeconfig else "",
                        "-n %s" % namespace if namespace else "",
                        "-l app=%s" % app if app else "",
                        "-l name=%s" % name if name else "",
                        "--field-selector=spec.nodeName=%s" % nodeName if nodeName else "",
                        "--field-selector=status.phase=%s" % status if status else "" )
            main.log.info( self.name + ": sending: " + repr( cmdStr ) )
            self.handle.sendline( cmdStr )
            i = self.handle.expect( [ "not found", "error", "The connection to the server", "Unable to find", "No resources found", self.prompt ] )
            if i == 4:
                # Command worked, but returned no pods
                output = self.handle.before + self.handle.after
                main.log.warn( self.name + ": " + output )
                return []
            elif i == 5:
                # Command returned pods
                output = self.handle.before + self.handle.after
                names = output.split( '\r\n' )[1].split()
                return names
            else:
                # Some error occured
                main.log.error( self.name + ": Error executing command" )
                main.log.debug( self.name + ": " + self.handle.before + str( self.handle.after ) )
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return main.FALSE

    def kubectlDescribe( self, describeString, dstPath, kubeconfig=None, namespace=None ):
        """
        Use kubectl to get the logs from a pod
        Required Arguments:
        - describeString: The string passed to the cli. Example: "pods"
        - dstPath: The location to save the logs to
        Optional Arguments:
        - kubeconfig: The path to a kubeconfig file
        - namespace: The namespace to search in
        Returns main.TRUE or
            main.FALSE on Error
        """

        try:
            cmdStr = "kubectl %s %s describe %s > %s " % (
                        "--kubeconfig %s" % kubeconfig if kubeconfig else "",
                        "-n %s" % namespace if namespace else "",
                        describeString,
                        dstPath )
            main.log.info( self.name + ": sending: " + repr( cmdStr ) )
            self.handle.sendline( cmdStr )
            i = self.handle.expect( [ "not found", "error", "The connection to the server", self.prompt ] )
            if i == 3:
                main.log.debug( self.name + ": " + self.handle.before )
                return main.TRUE
            else:
                main.log.error( self.name + ": Error executing command" )
                main.log.debug( self.name + ": " + self.handle.before + str( self.handle.after ) )
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return main.FALSE

    def kubectlPodNodes( self, dstPath=None, kubeconfig=None, namespace=None ):
        """
        Use kubectl to get the pod to node mappings
        Optional Arguments:
        - dstPath: The location to save the logs to
        - kubeconfig: The path to a kubeconfig file
        - namespace: The namespace to search in
        Returns main.TRUE if dstPath is given, else the output of the command or
            main.FALSE on Error
        """
        try:
            self.handle.sendline( "" )
            self.handle.expect( self.prompt )
            main.log.debug( self.handle.before + self.handle.after )
            cmdStr = "kubectl %s %s get pods -o wide %s " % (
                        "--kubeconfig %s" % kubeconfig if kubeconfig else "",
                        "-n %s" % namespace if namespace else "",
                        " > %s" % dstPath if dstPath else "" )
            main.log.info( self.name + ": sending: " + repr( cmdStr ) )
            self.handle.sendline( cmdStr )
            i = self.handle.expect( [ "not found", "error", "The connection to the server", self.prompt ] )
            if i == 3:
                output = self.handle.before
                main.log.debug( self.name + ": " + output )
                return output if dstPath else main.TRUE
            else:
                main.log.error( self.name + ": Error executing command" )
                main.log.debug( self.name + ": " + self.handle.before + str( self.handle.after ) )
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return main.FALSE

    def kubectlGetPodNode( self, podName, kubeconfig=None, namespace=None ):
        """
        Use kubectl to get the node a given pod is running on
        Arguments:
        - podName: The name of the pod
        Optional Arguments:
        - kubeconfig: The path to a kubeconfig file
        - namespace: The namespace to search in
        Returns a string of the node name or None
        """
        try:
            self.handle.sendline( "" )
            self.handle.expect( self.prompt )
            main.log.debug( self.handle.before + self.handle.after )
            cmdStr = "kubectl %s %s get pods %s --output=jsonpath='{.spec.nodeName}{\"\\n\"}'" % (
                        "--kubeconfig %s" % kubeconfig if kubeconfig else "",
                        "-n %s" % namespace if namespace else "",
                        podName )
            main.log.info( self.name + ": sending: " + repr( cmdStr ) )
            self.handle.sendline( cmdStr )
            i = self.handle.expect( [ "not found", "error", "The connection to the server", self.prompt ] )
            if i == 3:
                output = self.handle.before
                main.log.debug( self.name + ": " + output )
                output = output.splitlines()
                main.log.warn( output )
                return output[1] if len( output ) == 3 else None
            else:
                main.log.error( self.name + ": Error executing command" )
                main.log.debug( self.name + ": " + self.handle.before + str( self.handle.after ) )
                return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return None
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return None

    def kubectlCmd( self, cmd, kubeconfig=None, namespace=None ):
        """
        Run an arbitrary command using kubectl
        Arguments:
        - cmd: Command string to send to kubectl
        Optional Arguments:
        - kubeconfig: The path to a kubeconfig file
        - namespace: The namespace to search in
        Returns a string of the node name or None
        """
        try:
            self.handle.sendline( "" )
            self.handle.expect( self.prompt )
            main.log.debug( self.handle.before + self.handle.after )
            cmdStr = "kubectl %s %s %s" % (
                        "--kubeconfig %s" % kubeconfig if kubeconfig else "",
                        "-n %s" % namespace if namespace else "",
                        cmd )
            main.log.info( self.name + ": sending: " + repr( cmdStr ) )
            self.handle.sendline( cmdStr )
            i = self.handle.expect( [ "not found", "error", "The connection to the server", self.prompt ] )
            if i == 3:
                output = self.handle.before
                main.log.debug( self.name + ": " + output )
                output = output.splitlines()
                main.log.warn( output )
                return output[1] if len( output ) == 3 else None
            else:
                main.log.error( self.name + ": Error executing command" )
                main.log.debug( self.name + ": " + self.handle.before + str( self.handle.after ) )
                return None
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return None
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return None

    def sternLogs( self, podString, dstPath, kubeconfig=None, namespace=None, since='1h', wait=60 ):
        """
        Use stern to get the logs from a pod
        Required Arguments:
        - podString: The name of the pod or partial name of the pods to get the logs of
        - dstPath: The location to save the logs to
        Optional Arguments:
        - kubeconfig: The path to a kubeconfig file
        - namespace: The namespace to search in
        - since: Return logs newer than a relative duration like 5s, 2m, or 3h. Defaults to 1h
        - wait: How long to wait, in seconds, before killing the process. Stern does not currently
                support a way to exit if caught up to present time. If negative, leaves the stern
                process running, tailing the logs and returns main.TRUE. Defaults to 60 seconds
        Returns main.TRUE or
            main.FALSE on Error
        """
        import time
        try:
            cmdStr = "stern %s %s %s %s > %s " % (
                     "--kubeconfig %s" % kubeconfig if kubeconfig else "",
                     "-n %s" % namespace if namespace else "",
                     "--since %s" % since if since else "",
                     podString,
                     dstPath )
            main.log.info( self.name + ": sending: " + repr( cmdStr ) )
            self.handle.sendline( cmdStr )
            if int( wait ) >= 0:
                i = self.handle.expect( [ "not found",
                                          "Error: ",
                                          "The connection to the server",
                                          self.prompt,
                                          pexpect.TIMEOUT ], timeout=int( wait ) )
                if i == 3:
                    main.log.debug( self.name + ": " + self.handle.before )
                    return main.TRUE
                if i == 4:
                    self.handle.send( '\x03' )  # CTRL-C
                    self.handle.expect( self.prompt, timeout=5 )
                    main.log.debug( self.name + ": " + self.handle.before )
                    return main.TRUE
                else:
                    main.log.error( self.name + ": Error executing command" )
                    response = self.handle.before + str( self.handle.after )
                    self.handle.expect( [ self.prompt, pexpect.TIMEOUT ], timeout=5 )
                    response += self.handle.before + str( self.handle.after )
                    main.log.debug( self.name + ": " + response )
                    return main.FALSE
            else:
                self.preDisconnect = self.exitFromProcess
                return main.TRUE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return main.FALSE

    def kubectlLogs( self, podName, dstPath, kubeconfig=None, namespace=None, timeout=240 ):
        """
        Use kubectl to get the logs from a pod
        Required Arguments:
        - podName: The name of the pod to get the logs of
        - dstPath: The location to save the logs to
        Optional Arguments:
        - kubeconfig: The path to a kubeconfig file
        - namespace: The namespace to search in
        - timeout: Timeout for command to return. The longer the logs, the longer it will take to fetch them.
        Returns main.TRUE or
            main.FALSE on Error
        """

        try:
            cmdStr = "kubectl %s %s logs %s > %s " % (
                        "--kubeconfig %s" % kubeconfig if kubeconfig else "",
                        "-n %s" % namespace if namespace else "",
                        podName,
                        dstPath )
            main.log.info( self.name + ": sending: " + repr( cmdStr ) )
            self.handle.sendline( cmdStr )
            i = self.handle.expect( [ "not found", "error", "The connection to the server", self.prompt ], timeout=timeout )
            if i == 3:
                main.log.debug( self.name + ": " + self.handle.before )
                return main.TRUE
            else:
                main.log.error( self.name + ": Error executing command" )
                main.log.debug( self.name + ": " + self.handle.before + str( self.handle.after ) )
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return main.FALSE

    def kubectlCp( self, podName, srcPath, dstPath, kubeconfig=None, namespace=None, timeout=240 ):
        """
        Use kubectl to get a file from a pod
        Required Arguments:
        - podName: The name of the pod to get the logs of
        - srcPath: The file to copy from the pod
        - dstPath: The location to save the file to locally
        Optional Arguments:
        - kubeconfig: The path to a kubeconfig file
        - namespace: The namespace to search in
        - timeout: Timeout for command to return. The longer the logs, the longer it will take to fetch them.
        Returns main.TRUE or
            main.FALSE on Error
        """

        try:
            cmdStr = "kubectl %s %s cp %s:%s %s" % (
                        "--kubeconfig %s" % kubeconfig if kubeconfig else "",
                        "-n %s" % namespace if namespace else "",
                        podName,
                        srcPath,
                        dstPath )
            main.log.info( self.name + ": sending: " + repr( cmdStr ) )
            self.handle.sendline( cmdStr )
            i = self.handle.expect( [ "not found", "error", "The connection to the server", self.prompt ], timeout=timeout )
            if i == 3:
                main.log.debug( self.name + ": " + self.handle.before )
                return main.TRUE
            else:
                output = self.handle.before + str( self.handle.after )
                main.log.error( self.name + ": Error executing command" )
                self.handle.expect( [ self.prompt, pexpect.TIMEOUT ] )
                output += self.handle.before + str( self.handle.after )
                main.log.debug( self.name + ": " + output )
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return main.FALSE

    def kubectlPortForward( self, podName, portsList, kubeconfig=None, namespace=None ):
        """
        Use kubectl to setup port forwarding from the local machine to the kubernetes pod

        Note: This cli command does not return until the port forwarding session is ended.

        Required Arguments:
        - podName: The name of the pod as a string
        - portsList: The list of ports to forward, as a string. see kubectl help for details
        Optional Arguments:
        - kubeconfig: The path to a kubeconfig file
        - namespace: The namespace to search in
        Returns main.TRUE if a port-forward session was created or main.FALSE on Error


        """
        try:
            cmdStr = "kubectl %s %s port-forward pod/%s %s" % (
                        "--kubeconfig %s" % kubeconfig if kubeconfig else "",
                        "-n %s" % namespace if namespace else "",
                        podName,
                        portsList )

            self.clearBuffer()
            main.log.info( self.name + ": sending: " + repr( cmdStr ) )
            self.handle.sendline( cmdStr )
            self.handle.expect( "pod/%s" % podName )
            output = self.handle.before + self.handle.after
            i = self.handle.expect( [ "not found", "error", "closed/timedout",
                                      self.prompt, "The connection to the server",
                                      "Forwarding from", pexpect.TIMEOUT ] )
            output += self.handle.before + str( self.handle.after )
            # NOTE: This won't clear the buffer entirely, and each time the port forward
            #       is used, another line will be added to the buffer. We need to make
            #       sure we clear the buffer before using this component again.

            if i == 5:
                # Setup preDisconnect function
                self.preDisconnect = self.exitFromProcess
                self.portForwardList = portsList
                return main.TRUE
            elif i == 6:
                return self.checkPortForward( podName, portsList, kubeconfig, namespace )
            else:
                main.log.error( self.name + ": Error executing command" )
                main.log.debug( self.name + ": " + output )
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            return self.checkPortForward( podName, portsList, kubeconfig, namespace )
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return main.FALSE

    def checkPortForward( self, podName, portsList=None, kubeconfig=None, namespace=None ):
        """
        Check that kubectl port-forward session is still active and restarts it if it was closed.


        Required Arguments:
        - podName: The name of the pod as a string
        - portsList: The list of ports to forward, as a string. see kubectl help for details. Deafults to
                     the last used string on this node.
        Optional Arguments:
        - kubeconfig: The path to a kubeconfig file
        - namespace: The namespace to search in
        Returns main.TRUE if a port-forward session was created or is still active, main.FALSE on Error


        """
        try:
            main.log.debug( "%s: Checking port-forward session to %s" % ( self.name, podName ) )
            if not portsList:
                portsList = self.portForwardList
            self.handle.sendline( "" )
            i = self.handle.expect( [ self.prompt, pexpect.TIMEOUT ], timeout=5 )
            output = self.handle.before + str( self.handle.after )
            main.log.debug( "%s: %s" % ( self.name, output ) )
            if i == 0:
                # We are not currently in a port-forwarding session, try to re-establish.
                main.log.warn( "%s: port-forwarding session to %s closed, attempting to reestablish." % ( self.name, podName ) )
                return self.kubectlPortForward( podName, portsList, kubeconfig, namespace )
            elif i == 1:
                main.log.debug( "%s: We seem to still be in port-forwarding session" % self.name )
                # Still in a command, port-forward is probably still active
                return main.TRUE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return main.FALSE

    def kubectlSetLabel( self, nodeName, label, value, kubeconfig=None, namespace=None,
                         timeout=240, overwrite=True ):
        try:
            cmdStr = "kubectl %s %s label node %s %s %s=%s" % (
                "--kubeconfig %s" % kubeconfig if kubeconfig else "",
                "-n %s" % namespace if namespace else "",
                nodeName, "--overwrite" if overwrite else "",
                label, value )
            main.log.info( self.name + ": sending: " + repr( cmdStr ) )
            self.handle.sendline( cmdStr )
            i = self.handle.expect( [ "error",
                                      "The connection to the server",
                                      "node/%s not labeled" % nodeName,
                                      "node/%s labeled" % nodeName, ],
                                    timeout=timeout )
            if i == 3 or i == 4:
                output = self.handle.before + self.handle.after
                main.log.debug( self.name + ": " + output )
                self.clearBuffer()
                return main.TRUE
            else:
                main.log.error( self.name + ": Error executing command" )
                main.log.debug( self.name + ": " + self.handle.before + str( self.handle.after ) )
                self.clearBuffer()
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            self.clearBuffer()
            return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return main.FALSE

    def kubectlCordonNode( self, nodeName, kubeconfig=None, namespace=None, timeout=240, uncordonOnDisconnect=True ):
        try:
            cmdStr = "kubectl %s %s cordon %s" % (
                "--kubeconfig %s" % kubeconfig if kubeconfig else "",
                "-n %s" % namespace if namespace else "",
                nodeName )
            main.log.info( self.name + ": sending: " + repr( cmdStr ) )
            if uncordonOnDisconnect:
                self.nodeName = nodeName
                if kubeconfig:
                    self.kubeconfig = kubeconfig
                if namespace:
                    self.namespace = namespace
                self.preDisconnect = self.kubectlUncordonNode
            self.handle.sendline( cmdStr )
            i = self.handle.expect( [ "not found", "error",
                                      "The connection to the server",
                                      "node/%s cordoned" % nodeName,
                                      "node/%s already cordoned" % nodeName, ],
                                    timeout=timeout )
            if i == 3 or i == 4:
                output = self.handle.before + self.handle.after
                main.log.debug( self.name + ": " + output )
                self.clearBuffer()
                return main.TRUE
            else:
                main.log.error( self.name + ": Error executing command" )
                main.log.debug( self.name + ": " + self.handle.before + str( self.handle.after ) )
                self.clearBuffer()
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            self.clearBuffer()
            return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return main.FALSE

    def kubectlUncordonNode( self, nodeName=None, kubeconfig=None, namespace=None, timeout=240 ):
        try:
            if not nodeName:
                nodeName = getattr( self, "nodeName" )
            if not kubeconfig:
                kubeconfig = getattr( self, "kubeconfig", None )
            if not kubeconfig:
                namespace = getattr( self, "namespace", None )
            cmdStr = "kubectl %s %s uncordon %s" % (
                "--kubeconfig %s" % kubeconfig if kubeconfig else "",
                "-n %s" % namespace if namespace else "",
                nodeName )
            main.log.info( self.name + ": sending: " + repr( cmdStr ) )
            self.handle.sendline( cmdStr )
            i = self.handle.expect( [ "not found", "error",
                                      "The connection to the server",
                                      "node/%s uncordoned" % nodeName,
                                      "node/%s already uncordoned" % nodeName, ],
                                    timeout=timeout )
            if i == 3 or i == 4:
                output = self.handle.before + self.handle.after
                main.log.debug( self.name + ": " + output )
                self.clearBuffer()
                return main.TRUE
            else:
                main.log.error( self.name + ": Error executing command" )
                main.log.debug( self.name + ": " + self.handle.before + str( self.handle.after ) )
                self.clearBuffer()
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            self.clearBuffer()
            return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return main.FALSE

    def kubectlDeletePod( self, podName, kubeconfig=None, namespace=None, timeout=240 ):
        try:
            cmdStr = "kubectl %s %s delete pod %s" % (
                "--kubeconfig %s" % kubeconfig if kubeconfig else "",
                "-n %s" % namespace if namespace else "",
                podName )
            main.log.info( self.name + ": sending: " + repr( cmdStr ) )
            self.handle.sendline( cmdStr )
            i = self.handle.expect( [ "not found", "error",
                                      "The connection to the server",
                                      self.prompt ],
                                    timeout=timeout )
            if i == 3:
                main.log.debug( self.name + ": " + self.handle.before )
                self.clearBuffer()
                return main.TRUE
            else:
                main.log.error( self.name + ": Error executing command" )
                main.log.debug( self.name + ": " + self.handle.before + str( self.handle.after ) )
                self.clearBuffer()
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return main.FALSE

    def kubectlCheckPodReady( self, podName, kubeconfig=None, namespace=None, timeout=240 ):
        try:
            cmdStr = "kubectl %s %s get pods " \
                     "-o go-template='{{range $index, $element := .items}}{{range .status.containerStatuses}}{{if .ready}}{{$element.metadata.name}}{{\" ready\\n\"}}{{end}}{{end}}{{end}}' | grep --color=never %s" % (
                "--kubeconfig %s" % kubeconfig if kubeconfig else "",
                "-n %s" % namespace if namespace else "",
                podName )
            main.log.info( self.name + ": sending: " + repr( cmdStr ) )
            self.handle.sendline( cmdStr )
            # Since the command contains the prompt ($), we first expect for the
            # last part of the command and then we expect the actual values
            self.handle.expect( "grep --color=never %s" % podName, timeout=1 )
            i = self.handle.expect( [ podName + " ready",
                                      self.prompt ],
                                    timeout=timeout )
            if i == 0:
                main.log.debug( self.name + ": " + podName + " ready" )
                self.clearBuffer()
                return main.TRUE
            else:
                main.log.error( self.name + ": Error executing command" )
                main.log.debug( self.name + ": " + self.handle.before + str( self.handle.after ) )
                self.clearBuffer()
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return main.FALSE

    def kubectlGetServiceIP( self, serviceName, kubeconfig=None, namespace=None, timeout=240 ):
        try:
            cmdStr = "kubectl %s %s get service %s " \
                     "--output=jsonpath='{.spec.clusterIP}{\"\\n\"}'" % (
                "--kubeconfig %s" % kubeconfig if kubeconfig else "",
                "-n %s" % namespace if namespace else "",
                serviceName )
            main.log.info( self.name + ": sending: " + repr( cmdStr ) )
            self.handle.sendline( cmdStr )
            self.handle.expect( self.prompt, timeout=timeout )
            output = self.handle.before
            clusterIP = output.splitlines()
            main.log.debug( repr( clusterIP ) )
            return clusterIP[-2]
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return None
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return None

    def kubectlGetNodePort( self, serviceName, kubeconfig=None, namespace=None, timeout=240 ):
        try:
            cmdStr = "kubectl %s %s get service %s " \
                     "--output=jsonpath='{.spec.ports[*].nodePort}{\"\\n\"}'" % (
                "--kubeconfig %s" % kubeconfig if kubeconfig else "",
                "-n %s" % namespace if namespace else "",
                serviceName )
            main.log.info( self.name + ": sending: " + repr( cmdStr ) )
            self.handle.sendline( cmdStr )
            self.handle.expect( self.prompt, timeout=timeout )
            output = self.handle.before
            clusterIP = output.splitlines()
            main.log.debug( repr( clusterIP ) )
            return clusterIP[-2]
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return None
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            return None

    def clearBuffer(self):
        i = 0
        response = ''
        while True:
            try:
                i += 1
                self.handle.expect( self.prompt, timeout=5 )
                response += self.cleanOutput( self.handle.before )
            except pexpect.TIMEOUT:
                return response
