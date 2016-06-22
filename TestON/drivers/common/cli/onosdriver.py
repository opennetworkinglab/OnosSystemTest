#!/usr/bin/env python

"""
This driver interacts with ONOS bench, the OSGi platform
that configures the ONOS nodes. ( aka ONOS-next )

Please follow the coding style demonstrated by existing
functions and document properly.

If you are a contributor to the driver, please
list your email here for future contact:

jhall@onlab.us
andrew@onlab.us

OCT 9 2014

"""
import time
import types
import pexpect
import os
import re
import subprocess
from requests.models import Response
from drivers.common.clidriver import CLI

class OnosDriver( CLI ):

    def __init__( self ):
        """
        Initialize client
        """
        self.name = None
        self.home = None
        self.handle = None
        self.nicAddr = None
        super( CLI, self ).__init__()

    def connect( self, **connectargs ):
        """
        Creates ssh handle for ONOS "bench".
        NOTE:
        The ip_address would come from the topo file using the host tag, the
        value can be an environment variable as well as a "localhost" to get
        the ip address needed to ssh to the "bench"
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

            self.name = self.options[ 'name' ]

            # The 'nodes' tag is optional and it is not required in .topo file
            for key in self.options:
                if key == "nodes":
                    # Maximum number of ONOS nodes to run, if there is any
                    self.maxNodes = int( self.options[ 'nodes' ] )
                    break
                self.maxNodes = None

            if self.maxNodes == None or self.maxNodes == "":
                self.maxNodes = 100


            # Grabs all OC environment variables based on max number of nodes
            self.onosIps = {}  # Dictionary of all possible ONOS ip

            try:
                if self.maxNodes:
                    for i in range( self.maxNodes ):
                        envString = "OC" + str( i + 1 )
                        # If there is no more OC# then break the loop
                        if os.getenv( envString ):
                            self.onosIps[ envString ] = os.getenv( envString )
                        else:
                            self.maxNodes = len( self.onosIps )
                            main.log.info( self.name +
                                           ": Created cluster data with " +
                                           str( self.maxNodes ) +
                                           " maximum number" +
                                           " of nodes" )
                            break

                    if not self.onosIps:
                        main.log.info( "Could not read any environment variable"
                                       + " please load a cell file with all" +
                                        " onos IP" )
                        self.maxNodes = None
                    else:
                        main.log.info( self.name + ": Found " +
                                       str( self.onosIps.values() ) +
                                       " ONOS IPs" )
            except KeyError:
                main.log.info( "Invalid environment variable" )
            except Exception as inst:
                main.log.error( "Uncaught exception: " + str( inst ) )

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

            self.handle = super( OnosDriver, self ).connect(
                user_name=self.user_name,
                ip_address=self.ip_address,
                port=self.port,
                pwd=self.pwd,
                home=self.home )

            if self.handle:
                self.handle.sendline( "cd " + self.home )
                self.handle.expect( "\$" )
                return self.handle
            else:
                main.log.info( "Failed to create ONOS handle" )
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
        Called when Test is complete to disconnect the ONOS handle.
        """
        response = main.TRUE
        try:
            if self.handle:
                self.handle.sendline( "" )
                self.handle.expect( "\$" )
                self.handle.sendline( "exit" )
                self.handle.expect( "closed" )
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

    def getEpochMs( self ):
        """
        Returns milliseconds since epoch

        When checking multiple nodes in a for loop,
        around a hundred milliseconds of difference (ascending) is
        generally acceptable due to calltime of the function.
        Few seconds, however, is not and it means clocks
        are off sync.
        """
        try:
            self.handle.sendline( 'date +%s.%N' )
            self.handle.expect( 'date \+\%s\.\%N' )
            self.handle.expect( '\$' )
            epochMs = self.handle.before
            return epochMs
        except Exception:
            main.log.exception( 'Uncaught exception getting epoch time' )
            main.cleanup()
            main.exit()

    def onosPackage( self, opTimeout=180 ):
        """
        Produce a self-contained tar.gz file that can be deployed
        and executed on any platform with Java 8 JRE.
        """
        try:
            ret = main.TRUE
            self.handle.sendline( "onos-package" )
            self.handle.expect( "onos-package" )
            while True:
                i = self.handle.expect( [ "Downloading",
                                          "Unknown options",
                                          "No such file or directory",
                                          "tar.gz",
                                          "\$" ],
                                        opTimeout )
                handle = str( self.handle.before + self.handle.after )
                if i == 0:
                    # Give more time to download the file
                    continue  # expect again
                elif i == 1:
                    # Incorrect usage
                    main.log.error( "onos-package does not recognize the given options" )
                    ret = main.FALSE
                    continue  # expect again
                elif i == 2:
                    # File(s) not found
                    main.log.error( "onos-package could not find a file or directory" )
                    ret = main.FALSE
                    continue  # expect again
                elif i == 3:
                    # tar.gz
                    continue  # expect again
                elif i == 4:
                    # Prompt returned
                    break
            main.log.info( "onos-package command returned: " + handle )
            # As long as the sendline does not time out,
            # return true. However, be careful to interpret
            # the results of the onos-package command return
            return ret
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": TIMEOUT exception found in onosPackage" )
            main.log.error( self.name + ":    " + self.handle.before )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( "Failed to package ONOS" )
            main.cleanup()
            main.exit()

    def onosBuild( self ):
        """
        Use the pre defined script to build onos via mvn
        """
        try:
            self.handle.sendline( "onos-build" )
            self.handle.expect( "onos-build" )
            i = self.handle.expect( [
                "BUILD SUCCESS",
                "ERROR",
                "BUILD FAILED" ],
                timeout=120 )
            handle = str( self.handle.before )
            self.handle.expect( "\$" )

            main.log.info( "onos-build command returned: " +
                           handle )

            if i == 0:
                return main.TRUE
            else:
                return handle

        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
        except Exception:
            main.log.exception( "Failed to build ONOS" )
            main.cleanup()
            main.exit()

    def cleanInstall( self, skipTest=False, mciTimeout=600 ):
        """
        Runs mvn clean install in the root of the ONOS directory.
        This will clean all ONOS artifacts then compile each module
        Optional:
            skipTest - Does "-DskipTests -Dcheckstyle.skip -U -T 1C" which
                       skip the test. This will make the building faster.
                       Disregarding the credibility of the build
        Returns: main.TRUE on success
        On Failure, exits the test
        """
        try:
            main.log.info( "Running 'mvn clean install' on " +
                           str( self.name ) +
                           ". This may take some time." )
            self.handle.sendline( "cd " + self.home )
            self.handle.expect( "\$" )

            self.handle.sendline( "" )
            self.handle.expect( "\$" )

            if not skipTest:
                self.handle.sendline( "mvn clean install" )
                self.handle.expect( "mvn clean install" )
            else:
                self.handle.sendline( "mvn clean install -DskipTests" +
                                      " -Dcheckstyle.skip -U -T 1C" )
                self.handle.expect( "mvn clean install -DskipTests" +
                                      " -Dcheckstyle.skip -U -T 1C" )
            while True:
                i = self.handle.expect( [
                    'There\sis\sinsufficient\smemory\sfor\sthe\sJava\s' +
                    'Runtime\sEnvironment\sto\scontinue',
                    'BUILD\sFAILURE',
                    'BUILD\sSUCCESS',
                    'onos\$',  #TODO: fix this to be more generic?
                    'ONOS\$',
                    pexpect.TIMEOUT ], mciTimeout )
                if i == 0:
                    main.log.error( self.name + ":There is insufficient memory \
                            for the Java Runtime Environment to continue." )
                    # return main.FALSE
                    main.cleanup()
                    main.exit()
                if i == 1:
                    main.log.error( self.name + ": Build failure!" )
                    # return main.FALSE
                    main.cleanup()
                    main.exit()
                elif i == 2:
                    main.log.info( self.name + ": Build success!" )
                elif i == 3 or i == 4:
                    main.log.info( self.name + ": Build complete" )
                    # Print the build time
                    for line in self.handle.before.splitlines():
                        if "Total time:" in line:
                            main.log.info( line )
                    self.handle.sendline( "" )
                    self.handle.expect( "\$", timeout=60 )
                    return main.TRUE
                elif i == 5:
                    main.log.error(
                        self.name +
                        ": mvn clean install TIMEOUT!" )
                    # return main.FALSE
                    main.cleanup()
                    main.exit()
                else:
                    main.log.error( self.name + ": unexpected response from " +
                                    "mvn clean install" )
                    # return main.FALSE
                    main.cleanup()
                    main.exit()
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def gitPull( self, comp1="", fastForward=True ):
        """
        Assumes that "git pull" works without login

        If the fastForward boolean is set to true, only git pulls that can
        be fast forwarded will be performed. IE if you have not local commits
        in your branch.

        This function will perform a git pull on the ONOS instance.
        If used as gitPull( "NODE" ) it will do git pull + NODE. This is
        for the purpose of pulling from other nodes if necessary.

        Otherwise, this function will perform a git pull in the
        ONOS repository. If it has any problems, it will return main.ERROR
        If it successfully does a gitPull, it will return a 1 ( main.TRUE )
        If it has no updates, it will return 3.

        """
        try:
            self.handle.sendline( "cd " + self.home )
            self.handle.expect( self.home + "\$" )
            cmd = "git pull"
            if comp1 != "":
                cmd += ' ' +  comp1
            if fastForward:
                cmd += ' ' + " --ff-only"
            self.handle.sendline( cmd )
            i = self.handle.expect(
                [
                    'fatal',
                    'Username\sfor\s(.*):\s',
                    '\sfile(s*) changed,\s',
                    'Already up-to-date',
                    'Aborting',
                    'You\sare\snot\scurrently\son\sa\sbranch',
                    'You asked me to pull without telling me which branch you',
                    'Pull is not possible because you have unmerged files',
                    'Please enter a commit message to explain why this merge',
                    'Found a swap file by the name',
                    'Please, commit your changes before you can merge.',
                    pexpect.TIMEOUT ],
                timeout=300 )
            if i == 0:
                main.log.error( self.name + ": Git pull had some issue" )
                output = self.handle.after
                self.handle.expect( '\$' )
                output += self.handle.before
                main.log.warn( output )
                return main.ERROR
            elif i == 1:
                main.log.error(
                    self.name +
                    ": Git Pull Asking for username. " )
                return main.ERROR
            elif i == 2:
                main.log.info(
                    self.name +
                    ": Git Pull - pulling repository now" )
                self.handle.expect( self.home + "\$", 120 )
            # So that only when git pull is done, we do mvn clean compile
                return main.TRUE
            elif i == 3:
                main.log.info( self.name + ": Git Pull - Already up to date" )
                return i
            elif i == 4:
                main.log.info(
                    self.name +
                    ": Git Pull - Aborting..." +
                    "Are there conflicting git files?" )
                return main.ERROR
            elif i == 5:
                main.log.info(
                    self.name +
                    ": Git Pull - You are not currently " +
                    "on a branch so git pull failed!" )
                return main.ERROR
            elif i == 6:
                main.log.info(
                    self.name +
                    ": Git Pull - You have not configured an upstream " +
                    "branch to pull from. Git pull failed!" )
                return main.ERROR
            elif i == 7:
                main.log.info(
                    self.name +
                    ": Git Pull - Pull is not possible because " +
                    "you have unmerged files." )
                return main.ERROR
            elif i == 8:
                # NOTE: abandoning test since we can't reliably handle this
                #       there could be different default text editors and we
                #       also don't know if we actually want to make the commit
                main.log.error( "Git pull resulted in a merge commit message" +
                                ". Exiting test!" )
                main.cleanup()
                main.exit()
            elif i == 9:  # Merge commit message but swap file exists
                main.log.error( "Git pull resulted in a merge commit message" +
                                " but a swap file exists." )
                try:
                    self.handle.send( 'A' )  # Abort
                    self.handle.expect( "\$" )
                    return main.ERROR
                except Exception:
                    main.log.exception( "Couldn't exit editor prompt!")
                    main.cleanup()
                    main.exit()
            elif i == 10:  # In the middle of a merge commit
                main.log.error( "Git branch is in the middle of a merge. " )
                main.log.warn( self.handle.before + self.handle.after )
                return main.ERROR
            elif i == 11:
                main.log.error( self.name + ": Git Pull - TIMEOUT" )
                main.log.error(
                    self.name + " Response was: " + str(
                        self.handle.before ) )
                return main.ERROR
            else:
                main.log.error(
                    self.name +
                    ": Git Pull - Unexpected response, check for pull errors" )
                return main.ERROR
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def gitCheckout( self, branch="master" ):
        """
        Assumes that "git pull" works without login

        This function will perform a git git checkout on the ONOS instance.
        If used as gitCheckout( "branch" ) it will do git checkout
        of the "branch".

        Otherwise, this function will perform a git checkout of the master
        branch of the ONOS repository. If it has any problems, it will return
        main.ERROR.
        If the branch was already the specified branch, or the git checkout was
        successful then the function will return main.TRUE.

        """
        try:
            self.handle.sendline( "cd " + self.home )
            self.handle.expect( self.home + "\$" )
            main.log.info( self.name +
                           ": Checking out git branch/ref: " + branch + "..." )
            cmd = "git checkout " + branch
            self.handle.sendline( cmd )
            self.handle.expect( cmd )
            i = self.handle.expect(
                [ 'fatal',
                  'Username for (.*): ',
                  'Already on \'',
                  'Switched to (a new )?branch \'' + str( branch ),
                  pexpect.TIMEOUT,
                  'error: Your local changes to the following files' +
                  'would be overwritten by checkout:',
                  'error: you need to resolve your current index first',
                  "You are in 'detached HEAD' state.",
                  "HEAD is now at " ],
                timeout=60 )
            if i == 0:
                main.log.error(
                    self.name +
                    ": Git checkout had some issue..." )
                main.log.error( self.name + ":     " + self.handle.before )
                return main.ERROR
            elif i == 1:
                main.log.error(
                    self.name +
                    ": Git checkout asking for username." +
                    " Please configure your local git repository to be able " +
                    "to access your remote repository passwordlessly" )
                # TODO add support for authenticating
                return main.ERROR
            elif i == 2:
                main.log.info(
                    self.name +
                    ": Git Checkout %s : Already on this branch" % branch )
                self.handle.expect( self.home + "\$" )
                # main.log.info( "DEBUG: after checkout cmd = "+
                # self.handle.before )
                return main.TRUE
            elif i == 3:
                main.log.info(
                    self.name +
                    ": Git checkout %s - Switched to this branch" % branch )
                self.handle.expect( self.home + "\$" )
                # main.log.info( "DEBUG: after checkout cmd = "+
                # self.handle.before )
                return main.TRUE
            elif i == 4:
                main.log.error( self.name + ": Git Checkout- TIMEOUT" )
                main.log.error(
                    self.name + " Response was: " + str( self.handle.before ) )
                return main.ERROR
            elif i == 5:
                self.handle.expect( "Aborting" )
                main.log.error(
                    self.name +
                    ": Git checkout error: \n" +
                    "Your local changes to the following files would" +
                    " be overwritten by checkout:" +
                    str( self.handle.before ) )
                self.handle.expect( self.home + "\$" )
                return main.ERROR
            elif i == 6:
                main.log.error(
                    self.name +
                    ": Git checkout error: \n" +
                    "You need to resolve your current index first:" +
                    str( self.handle.before ) )
                self.handle.expect( self.home + "\$" )
                return main.ERROR
            elif i == 7:
                main.log.info(
                    self.name +
                    ": Git checkout " + str( branch ) +
                    " - You are in 'detached HEAD' state. HEAD is now at " +
                    str( branch ) )
                self.handle.expect( self.home + "\$" )
                return main.TRUE
            elif i == 8:  # Already in detached HEAD on the specified commit
                main.log.info(
                    self.name +
                    ": Git Checkout %s : Already on commit" % branch )
                self.handle.expect( self.home + "\$" )
                return main.TRUE
            else:
                main.log.error(
                    self.name +
                    ": Git Checkout - Unexpected response, " +
                    "check for pull errors" )
                main.log.error( self.name + ":     " + self.handle.before )
                return main.ERROR

        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def getBranchName( self ):
        main.log.info( "self.home = " )
        main.log.info( self.home )
        self.handle.sendline( "cd " + self.home )
        self.handle.expect( self.home + "\$" )
        self.handle.sendline( "git name-rev --name-only HEAD" )
        self.handle.expect( "git name-rev --name-only HEAD" )
        self.handle.expect( "\$" )

        lines =  self.handle.before.splitlines()
        if lines[1] == "master":
            return "master"
        elif lines[1] == "onos-1.0":
            return "onos-1.0"
        else:
            main.log.info( lines[1] )
            return "unexpected ONOS branch for SDN-IP test"

    def getVersion( self, report=False ):
        """
        Writes the COMMIT number to the report to be parsed
                by Jenkins data collector.
        """
        try:
            self.handle.sendline( "" )
            self.handle.expect( "\$" )
            self.handle.sendline(
                "cd " +
                self.home +
                "; git log -1 --pretty=fuller --decorate=short | grep -A 6 " +
                " \"commit\" --color=never" )
            # NOTE: for some reason there are backspaces inserted in this
            # phrase when run from Jenkins on some tests
            self.handle.expect( "never" )
            self.handle.expect( "\$" )
            response = ( self.name + ": \n" + str(
                self.handle.before + self.handle.after ) )
            self.handle.sendline( "cd " + self.home )
            self.handle.expect( "\$" )
            lines = response.splitlines()
            for line in lines:
                print line
            if report:
                main.log.wiki( "<blockquote>" )
                for line in lines[ 2:-1 ]:
                    # Bracket replacement is for Wiki-compliant
                    # formatting. '<' or '>' are interpreted
                    # as xml specific tags that cause errors
                    line = line.replace( "<", "[" )
                    line = line.replace( ">", "]" )
                    #main.log.wiki( "\t" + line )
                    main.log.wiki( line + "<br /> " )
                    main.log.summary( line )
                main.log.wiki( "</blockquote>" )
                main.log.summary("\n")
            return lines[ 2 ]
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def createCellFile( self, benchIp, fileName, mnIpAddrs,
                        appString, onosIpAddrs, onosUser="sdn" ):
        """
        Creates a cell file based on arguments
        Required:
            * Bench IP address ( benchIp )
                - Needed to copy the cell file over
            * File name of the cell file ( fileName )
            * Mininet IP address ( mnIpAddrs )
                - Note that only 1 ip address is
                  supported currently
            * ONOS IP addresses ( onosIpAddrs )
                - Must be passed in as last arguments
            * ONOS USER (onosUser)
                - optional argument to set ONOS_USER environment variable

        NOTE: Assumes cells are located at:
            ~/<self.home>/tools/test/cells/
        """
        # Variable initialization
        cellDirectory = self.home + "/tools/test/cells/"
        # We want to create the cell file in the dependencies directory
        # of TestON first, then copy over to ONOS bench
        tempDirectory = "/tmp/"
        # Create the cell file in the directory for writing ( w+ )
        cellFile = open( tempDirectory + fileName, 'w+' )
        if isinstance( onosIpAddrs, types.StringType ):
            onosIpAddrs = [ onosIpAddrs ]

        # App string is hardcoded environment variables
        # That you may wish to use by default on startup.
        # Note that you  may not want certain apps listed
        # on here.
        appString = "export ONOS_APPS=" + appString
        onosGroup = "export ONOS_GROUP=" + onosUser
        onosUser = "export ONOS_USER=" + onosUser
        mnString = "export OCN="
        if mnIpAddrs == "":
            mnString = ""
        onosString = "export OC"
        tempCount = 1

        # Create ONOSNIC ip address prefix
        tempOnosIp = str( onosIpAddrs[ 0 ] )
        tempList = []
        tempList = tempOnosIp.split( "." )
        # Omit last element of list to format for NIC
        tempList = tempList[ :-1 ]
        # Structure the nic string ip
        nicAddr = ".".join( tempList ) + ".*"
        self.nicAddr = nicAddr
        onosNicString = "export ONOS_NIC=" + nicAddr

        try:
            # Start writing to file
            cellFile.write( onosNicString + "\n" )

            for arg in onosIpAddrs:
                # For each argument in onosIpAddrs, write to file
                # Output should look like the following:
                #   export OC1="10.128.20.11"
                #   export OC2="10.128.20.12"
                cellFile.write( onosString + str( tempCount ) +
                                "=\"" + arg + "\"\n" )
                tempCount = tempCount + 1

            cellFile.write( "export OCI=$OC1\n" )
            cellFile.write( mnString + "\"" + mnIpAddrs + "\"\n" )
            cellFile.write( appString + "\n" )
            cellFile.write( onosGroup + "\n" )
            cellFile.write( onosUser + "\n" )
            cellFile.close()

            # We use os.system to send the command to TestON cluster
            # to account for the case in which TestON is not located
            # on the same cluster as the ONOS bench
            # Note that even if TestON is located on the same cluster
            # as ONOS bench, you must setup passwordless ssh
            # between TestON and ONOS bench in order to automate the test.
            os.system( "scp " + tempDirectory + fileName + " " +
                       self.user_name + "@" + self.ip_address + ":" + cellDirectory )

            return main.TRUE

        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def setCell( self, cellname ):
        """
        Calls 'cell <name>' to set the environment variables on ONOSbench
        """
        import re
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
                self.handle.expect( str( cellname ) )
                handleBefore = self.handle.before
                handleAfter = self.handle.after
                # Get the rest of the handle
                self.handle.expect( "\$" )
                time.sleep(10)
                handleMore = self.handle.before

                cell_result = handleBefore + handleAfter + handleMore
                #print cell_result
                if( re.search( "No such cell", cell_result ) ):
                    main.log.error( "Cell call returned: " + handleBefore +
                               handleAfter + handleMore )
                    main.cleanup()
                    main.exit()
                return main.TRUE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def verifyCell( self ):
        """
        Calls 'onos-verify-cell' to check for cell installation
        """
        # TODO: Add meaningful expect value

        try:
            # Clean handle by sending empty and expecting $
            self.handle.sendline( "" )
            self.handle.expect( "\$" )
            self.handle.sendline( "onos-verify-cell" )
            self.handle.expect( "\$" )
            handleBefore = self.handle.before
            handleAfter = self.handle.after
            main.log.info( "Verify cell returned: " + handleBefore +
                           handleAfter )
            return main.TRUE
        except pexpect.ExceptionPexpect as e:
            main.log.exception( self.name + ": Pexpect exception found: " )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def onosCfgSet( self, ONOSIp, configName, configParam ):
        """
        Uses 'onos <node-ip> cfg set' to change a parameter value of an
        application.

        ex)
            onos 10.0.0.1 cfg set org.onosproject.myapp appSetting 1
        ONOSIp = '10.0.0.1'
        configName = 'org.onosproject.myapp'
        configParam = 'appSetting 1'
        """
        try:
            cfgStr = "onos {} cfg set {} {}".format( ONOSIp,
                                                     configName,
                                                     configParam )
            self.handle.sendline( "" )
            self.handle.expect( ":~" )
            self.handle.sendline( cfgStr )
            self.handle.expect("cfg set")
            self.handle.expect( ":~" )

            paramValue = configParam.split(" ")[1]
            paramName = configParam.split(" ")[0]

            checkStr = 'onos {} cfg get " {} {} " '.format( ONOSIp, configName, paramName )

            self.handle.sendline( checkStr )
            self.handle.expect( ":~" )

            if "value=" + paramValue + "," in self.handle.before:
                main.log.info("cfg " + configName + " successfully set to " + configParam)
                return main.TRUE
        except pexpect.ExceptionPexpect as e:
            main.log.exception( self.name + ": Pexpect exception found: " )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def onosCli( self, ONOSIp, cmdstr ):
        """
        Uses 'onos' command to send various ONOS CLI arguments.
        Required:
            * ONOSIp: specify the ip of the cell machine
            * cmdstr: specify the command string to send

        This function is intended to expose the entire karaf
        CLI commands for ONOS. Try to use this function first
        before attempting to write a ONOS CLI specific driver
        function.
        You can see a list of available 'cmdstr' arguments
        by starting onos, and typing in 'onos' to enter the
        onos> CLI. Then, type 'help' to see the list of
        available commands.
        """
        try:
            if not ONOSIp:
                main.log.error( "You must specify the IP address" )
                return main.FALSE
            if not cmdstr:
                main.log.error( "You must specify the command string" )
                return main.FALSE

            cmdstr = str( cmdstr )
            self.handle.sendline( "" )
            self.handle.expect( "\$" )

            self.handle.sendline( "onos -w " + ONOSIp + " " + cmdstr )
            self.handle.expect( "\$" )

            handleBefore = self.handle.before
            main.log.info( "Command sent successfully" )
            # Obtain return handle that consists of result from
            # the onos command. The string may need to be
            # configured further.
            returnString = handleBefore
            return returnString
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def onosInstall( self, options="-f", node="" ):
        """
        Installs ONOS bits on the designated cell machine.
        If -f option is provided, it also forces an uninstall.
        Presently, install also includes onos-push-bits and
        onos-config within.
        The node option allows you to selectively only push the jar
        files to certain onos nodes

        Returns: main.TRUE on success and main.FALSE on failure
        """
        try:
            if options:
                self.handle.sendline( "onos-install " + options + " " + node )
            else:
                self.handle.sendline( "onos-install " + node )
            self.handle.expect( "onos-install " )
            # NOTE: this timeout may need to change depending on the network
            # and size of ONOS
            i = self.handle.expect( [ "Network\sis\sunreachable",
                                      "onos\sstart/running,\sprocess",
                                      "ONOS\sis\salready\sinstalled",
                                      "already\sup-to-date",
                                      "\$",
                                      pexpect.TIMEOUT ], timeout=180 )
            if i == 0:
                main.log.warn( "Network is unreachable" )
                self.handle.expect( "\$" )
                return main.FALSE
            elif i == 1:
                main.log.info(
                    "ONOS was installed on " +
                    node +
                    " and started" )
                self.handle.expect( "\$" )
                return main.TRUE
            elif i == 2:
                main.log.info( "ONOS is already installed on " + node )
                self.handle.expect( "\$" )
                return main.TRUE
            elif i == 3:
                main.log.info( "ONOS is already installed on " + node )
                self.handle.expect( "\$" )
                return main.TRUE
            elif i == 4:
                main.log.info( "ONOS was installed on " + node )
                return main.TRUE
            elif i == 5:
                main.log.info(
                    "Installation of ONOS on " +
                    node +
                    " timed out" )
                self.handle.expect( "\$" )
                main.log.warn( self.handle.before )
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

    def onosStart( self, nodeIp ):
        """
        Calls onos command: 'onos-service [<node-ip>] start'
        This command is a remote management of the ONOS upstart daemon
        """
        try:
            self.handle.sendline( "" )
            self.handle.expect( "\$" )
            self.handle.sendline( "onos-service " + str( nodeIp ) +
                                  " start" )
            i = self.handle.expect( [
                "Job\sis\salready\srunning",
                "start/running",
                "\$",
                "Unknown\sinstance",
                pexpect.TIMEOUT ], timeout=180 )
            if i == 0:
                self.handle.expect( "\$" )
                main.log.info( "Service is already running" )
                return main.TRUE
            elif i == 1:
                self.handle.expect( "\$" )
                main.log.info( "ONOS service started" )
                return main.TRUE
            elif i == 2:
                main.log.info( "ONOS service started" )
                return main.TRUE
            else:
                self.handle.expect( "\$" )
                main.log.error( "ONOS service failed to start" )
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

    def onosStop( self, nodeIp ):
        """
        Calls onos command: 'onos-service [<node-ip>] stop'
        This command is a remote management of the ONOS upstart daemon
        """
        try:
            self.handle.sendline( "" )
            self.handle.expect( "\$" )
            self.handle.sendline( "onos-service " + str( nodeIp ) +
                                  " stop" )
            i = self.handle.expect( [
                "stop/waiting",
                "Could not resolve hostname",
                "Unknown\sinstance",
                "\$",
                pexpect.TIMEOUT ], timeout=180 )
            if i == 0:
                self.handle.expect( "\$" )
                main.log.info( "ONOS service stopped" )
                return main.TRUE
            elif i == 1:
                self.handle.expect( "\$" )
                main.log.info( "onosStop() Unknown ONOS instance specified: " +
                               str( nodeIp ) )
                return main.FALSE
            elif i == 2:
                self.handle.expect( "\$" )
                main.log.warn( "ONOS wasn't running" )
                return main.TRUE
            elif i == 3:
                main.log.info( "ONOS service stopped" )
                return main.TRUE
            else:
                main.log.error( "ONOS service failed to stop" )
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

    def onosUninstall( self, nodeIp="" ):
        """
        Calls the command: 'onos-uninstall'
        Uninstalls ONOS from the designated cell machine, stopping
        if needed
        """
        try:
            self.handle.sendline( "" )
            self.handle.expect( "\$", timeout=180 )
            self.handle.sendline( "onos-uninstall " + str( nodeIp ) )
            self.handle.expect( "\$", timeout=180 )
            main.log.info( "ONOS " + nodeIp + " was uninstalled" )
            # onos-uninstall command does not return any text
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Timeout in onosUninstall" )
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

    def onosDie( self, nodeIp ):
        """
        Issues the command 'onos-die <node-ip>'
        This command calls onos-kill and also stops the node
        """
        try:
            self.handle.sendline( "" )
            self.handle.expect( "\$" )
            cmdStr = "onos-die " + str( nodeIp )
            self.handle.sendline( cmdStr )
            i = self.handle.expect( [
                "Killing\sONOS",
                "ONOS\sprocess\sis\snot\srunning",
                pexpect.TIMEOUT ], timeout=60 )
            if i == 0:
                main.log.info( "ONOS instance " + str( nodeIp ) +
                               " was killed and stopped" )
                self.handle.sendline( "" )
                self.handle.expect( "\$" )
                return main.TRUE
            elif i == 1:
                main.log.info( "ONOS process was not running" )
                self.handle.sendline( "" )
                self.handle.expect( "\$" )
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

    def onosKill( self, nodeIp ):
        """
        Calls the command: 'onos-kill [<node-ip>]'
        "Remotely, and unceremoniously kills the ONOS instance running on
        the specified cell machine" - Tom V
        """
        try:
            self.handle.sendline( "" )
            self.handle.expect( "\$" )
            self.handle.sendline( "onos-kill " + str( nodeIp ) )
            i = self.handle.expect( [
                "\$",
                "No\sroute\sto\shost",
                "password:",
                pexpect.TIMEOUT ], timeout=60 )

            if i == 0:
                main.log.info(
                    "ONOS instance " + str(
                        nodeIp ) + " was killed" )
                return main.TRUE
            elif i == 1:
                main.log.info( "No route to host" )
                return main.FALSE
            elif i == 2:
                main.log.info(
                    "Passwordless login for host: " +
                    str( nodeIp ) +
                    " not configured" )
                return main.FALSE
            else:
                main.log.info( "ONOS instance was not killed" )
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

    def onosRemoveRaftLogs( self ):
        """
        Removes Raft / Copy cat files from ONOS to ensure
        a cleaner environment.

        Description:
            Stops all ONOS defined in the cell,
            wipes the raft / copycat log files
        """
        try:
            self.handle.sendline( "" )
            self.handle.expect( "\$" )
            self.handle.sendline( "onos-remove-raft-logs" )
            # Sometimes this command hangs
            i = self.handle.expect( [ "\$", pexpect.TIMEOUT ],
                                    timeout=120 )
            if i == 1:
                i = self.handle.expect( [ "\$", pexpect.TIMEOUT ],
                                        timeout=120 )
                if i == 1:
                    return main.FALSE
            return main.TRUE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def onosStartNetwork( self, mntopo ):
        """
        Calls the command 'onos-start-network [ <mininet-topo> ]
        "remotely starts the specified topology on the cell's
        mininet machine against all controllers configured in the
        cell."
        * Specify mininet topology file name for mntopo
        * Topo files should be placed at:
          ~/<your-onos-directory>/tools/test/topos

        NOTE: This function will take you to the mininet prompt
        """
        try:
            if not mntopo:
                main.log.error( "You must specify a topo file to execute" )
                return main.FALSE

            mntopo = str( mntopo )
            self.handle.sendline( "" )
            self.handle.expect( "\$" )

            self.handle.sendline( "onos-start-network " + mntopo )
            self.handle.expect( "mininet>" )
            main.log.info( "Network started, entered mininet prompt" )

            # TODO: Think about whether return is necessary or not

        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def isup( self, node="", timeout=240 ):
        """
        Run's onos-wait-for-start which only returns once ONOS is at run
        level 100(ready for use)

        Returns: main.TRUE if ONOS is running and main.FALSE on timeout
        """
        try:
            self.handle.sendline( "onos-wait-for-start " + node )
            self.handle.expect( "onos-wait-for-start" )
            # NOTE: this timeout is arbitrary"
            i = self.handle.expect(["\$", pexpect.TIMEOUT], timeout)
            if i == 0:
                main.log.info( self.name + ": " + node + " is up" )
                return main.TRUE
            elif i == 1:
                # NOTE: since this function won't return until ONOS is ready,
                #   we will kill it on timeout
                main.log.error( "ONOS has not started yet" )
                self.handle.send( "\x03" )  # Control-C
                self.handle.expect( "\$" )
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

    def pushTestIntentsShell(
            self,
            dpidSrc,
            dpidDst,
            numIntents,
            dirFile,
            onosIp,
            numMult="",
            appId="",
            report=True,
            options="" ):
        """
        Description:
            Use the linux prompt to push test intents to
            better parallelize the results than the CLI
        Required:
            * dpidSrc: specify source dpid
            * dpidDst: specify destination dpid
            * numIntents: specify number of intents to push
            * dirFile: specify directory and file name to save
              results
            * onosIp: specify the IP of ONOS to install on
        NOTE:
            You must invoke this command at linux shell prompt
        """
        try:
            # Create the string to sendline
            if options:
                baseCmd = "onos " + str( onosIp ) + " push-test-intents " +\
                    options + " "
            else:
                baseCmd = "onos " + str( onosIp ) + " push-test-intents "

            addDpid = baseCmd + str( dpidSrc ) + " " + str( dpidDst )
            if not numMult:
                addIntents = addDpid + " " + str( numIntents )
            elif numMult:
                addIntents = addDpid + " " + str( numIntents ) + " " +\
                    str( numMult )
                if appId:
                    addApp = addIntents + " " + str( appId )
                else:
                    addApp = addIntents

            if report:
                sendCmd = addApp + " > " + str( dirFile ) + " &"
            else:
                sendCmd = addApp + " &"
            main.log.info( "Send cmd: " + sendCmd )

            self.handle.sendline( sendCmd )

        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def tsharkPcap( self, interface, dirFile ):
        """
        Capture all packet activity and store in specified
        directory/file

        Required:
            * interface: interface to capture
            * dir: directory/filename to store pcap
        """
        try:
            self.handle.sendline( "" )
            self.handle.expect( "\$" )

            self.handle.sendline( "tshark -i " + str( interface ) + " -t e -w " + str( dirFile ) + " &" )
            self.handle.sendline( "\n" )
            self.handle.expect( "Capturing on" )
            self.handle.sendline( "\n" )
            self.handle.expect( "\$" )

            main.log.info( "Tshark started capturing files on " +
                           str( interface ) + " and saving to directory: " +
                           str( dirFile ) )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def onosTopoCfg( self, onosIp, jsonFile ):
        """
            Description:
                Execute onos-topo-cfg command
            Required:
                onosIp - IP of the onos node you want to send the json to
                jsonFile - File path of the json file
            Return:
                Returns main.TRUE if the command is successfull; Returns
                main.FALSE if there was an error
        """
        try:
            self.handle.sendline( "" )
            self.handle.expect( "\$" )
            cmd = "onos-topo-cfg "
            self.handle.sendline( cmd + str( onosIp ) + " " + jsonFile )
            handle = self.handle.before
            print handle
            if "Error" in handle:
                main.log.error( self.name + ":    " + self.handle.before )
                return main.FALSE
            else:
                self.handle.expect( "\$" )
                return main.TRUE

        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def tsharkGrep( self, grep, directory, interface='eth0', grepOptions='' ):
        """
        Required:
            * grep string
            * directory to store results
        Optional:
            * interface - default: eth0
            * grepOptions - options for grep
        Description:
            Uses tshark command to grep specific group of packets
            and stores the results to specified directory.
            The timestamp is hardcoded to be in epoch
        """
        try:
            self.handle.sendline( "" )
            self.handle.expect( "\$" )
            self.handle.sendline( "" )
            if grepOptions:
                grepStr = "grep "+str(grepOptions)
            else:
                grepStr = "grep"

            cmd = (
                "sudo tshark -i " +
                str( interface ) +
                " -t e | " +
                grepStr + " --line-buffered \"" +
                str(grep) +
                "\" >" +
                directory +
                " &" )
            self.handle.sendline(cmd)
            main.log.info(cmd)
            self.handle.expect( "Capturing on" )
            self.handle.sendline( "\n" )
            self.handle.expect( "\$" )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def tsharkStop( self ):
        """
        Removes wireshark files from /tmp and kills all tshark processes
        """
        # Remove all pcap from previous captures
        try:
            self.execute( cmd="sudo rm /tmp/wireshark*" )
            self.handle.sendline( "" )
            self.handle.sendline( "sudo kill -9 `ps -ef | grep \"tshark -i\"" +
                                  " | grep -v grep | awk '{print $2}'`" )
            self.handle.sendline( "" )
            main.log.info( "Tshark stopped" )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def ptpd( self, args ):
        """
        Initiate ptp with user-specified args.
        Required:
            * args: specify string of args after command
              'sudo ptpd'
        """
        try:
            self.handle.sendline( "sudo ptpd " + str( args ) )
            i = self.handle.expect( [
                "Multiple",
                "Error",
                "\$" ] )
            self.handle.expect( "\$" )

            if i == 0:
                handle = self.handle.before
                main.log.info( "ptpd returned an error: " +
                               str( handle ) )
                return handle
            elif i == 1:
                handle = self.handle.before
                main.log.error( "ptpd returned an error: " +
                                str( handle ) )
                return handle
            else:
                return main.TRUE

        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def dumpFlows(self,ONOSIp, destDir, filename="flows" ):
        """
        Dump Flow Tables to a desired directory.
        For debugging purposes, you may want to use
        this function to capture flows at a given point in time.
        Localtime will be attached to the filename

        Required:
            * ONOSIp: the IP of the target ONOS instance
            * destDir: specify directory to copy to.
              ex ) /tmp/
        Optional:
            * fileName: Name of the file
        """

        localtime = time.strftime( '%x %X' )
        localtime = localtime.replace( "/", "" )
        localtime = localtime.replace( " ", "_" )
        localtime = localtime.replace( ":", "" )
        if destDir[ -1: ] != "/":
            destDir += "/"
        cmd="flows > "+ str( destDir ) + str( filename ) + localtime
        return self.onosCli(ONOSIp,cmd)

    def dumpGroups(self,ONOSIp, destDir, filename="groups" ):
        """
        Dump Group Tables to a desired directory.
        For debugging purposes, you may want to use
        this function to capture groups at a given point in time.
        Localtime will be attached to the filename

        Required:
            * ONOSIp: the IP of the target ONOS instance
            * destDir: specify directory to copy to.
              ex ) /tmp/
        Optional:
            * fileName: Name of the file
        """

        localtime = time.strftime( '%H %M' )
        localtime = localtime.replace( "/", "" )
        localtime = localtime.replace( " ", "_" )
        localtime = localtime.replace( ":", "" )
        if destDir[ -1: ] != "/":
            destDir += "/"
        cmd="groups > "+ str( destDir ) + str( filename ) + localtime
        return self.onosCli(ONOSIp,cmd)

    def cpLogsToDir( self, logToCopy,
                     destDir, copyFileName="" ):
        """
        Copies logs to a desired directory.
        Current implementation of ONOS deletes its karaf
        logs on every iteration. For debugging purposes,
        you may want to use this function to capture
        certain karaf logs. ( or any other logs if needed )
        Localtime will be attached to the filename

        Required:
            * logToCopy: specify directory and log name to
              copy.
              ex ) /opt/onos/log/karaf.log.1
              For copying multiple files, leave copyFileName
              empty and only specify destDir -
              ex ) /opt/onos/log/karaf*
            * destDir: specify directory to copy to.
              ex ) /tmp/
        Optional:
            * copyFileName: If you want to rename the log
              file, specify copyFileName. This will not work
              with multiple file copying
        """
        try:
            localtime = time.strftime( '%H %M' )
            localtime = localtime.replace( "/", "" )
            localtime = localtime.replace( " ", "_" )
            localtime = localtime.replace( ":", "" )
            if destDir[ -1: ] != "/":
                destDir += "/"

            if copyFileName:
                self.handle.sendline( "cp " + str( logToCopy ) + " " +
                                      str( destDir ) + str( copyFileName ) +
                                      localtime )
                self.handle.expect( "cp" )
                self.handle.expect( "\$" )
            else:
                self.handle.sendline( "cp " + str( logToCopy ) +
                                      " " + str( destDir ) )
                self.handle.expect( "cp" )
                self.handle.expect( "\$" )

            return self.handle.before

        except pexpect.EOF:
            main.log.error( "Copying files failed" )
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
        except Exception:
            main.log.exception( "Copying files failed" )

    def checkLogs( self, onosIp, restart=False):
        """
        runs onos-check-logs on the given onos node
        If restart is True, use the old version of onos-check-logs which
            does not print the full stacktrace, but shows the entire log file,
            including across restarts
        returns the response
        """
        try:
            cmd = "onos-check-logs " + str( onosIp )
            if restart:
                cmd += " old"
            self.handle.sendline( cmd )
            self.handle.expect( cmd )
            self.handle.expect( "\$ " )
            response = self.handle.before
            return response
        except pexpect.EOF:
            main.log.error( "Lost ssh connection" )
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def onosStatus( self, node="" ):
        """
        Calls onos command: 'onos-service [<node-ip>] status'
        """
        try:
            self.handle.sendline( "" )
            self.handle.expect( "\$" )
            self.handle.sendline( "onos-service " + str( node ) +
                                  " status" )
            i = self.handle.expect( [
                "start/running",
                "Running ...",
                "stop/waiting",
                "Not Running ...",
                pexpect.TIMEOUT ], timeout=120 )
            self.handle.sendline( "" )
            self.handle.expect( "\$" )

            if i == 0 or i == 1:
                main.log.info( "ONOS is running" )
                return main.TRUE
            elif i == 2 or i == 3:
                main.log.info( "ONOS is stopped" )
                main.log.error( "ONOS service failed to check the status" )
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

    def setIpTables( self, ip, port='', action='add', packet_type='',
                     direction='INPUT', rule='DROP', states=True ):
        """
        Description:
            add or remove iptables rule to DROP (default) packets from
            specific IP and PORT
        Usage:
        * specify action ('add' or 'remove')
          when removing, pass in the same argument as you would add. It will
          delete that specific rule.
        * specify the ip to block
        * specify the destination port to block (defaults to all ports)
        * optional packet type to block (default tcp)
        * optional iptables rule (default DROP)
        * optional direction to block (default 'INPUT')
        * States boolean toggles adding all supported tcp states to the
          firewall rule
        Returns:
            main.TRUE on success or
            main.FALSE if given invalid input or
            main.ERROR if there is an error in response from iptables
        WARNING:
        * This function uses root privilege iptables command which may result
          in unwanted network errors. USE WITH CAUTION
        """

        # NOTE*********
        #   The strict checking methods of this driver function is intentional
        #   to discourage any misuse or error of iptables, which can cause
        #   severe network errors
        # *************

        # NOTE: Sleep needed to give some time for rule to be added and
        #       registered to the instance. If you are calling this function
        #       multiple times this sleep will prevent any errors.
        #       DO NOT REMOVE
        # time.sleep( 5 )
        try:
            # input validation
            action_type = action.lower()
            rule = rule.upper()
            direction = direction.upper()
            if action_type != 'add' and action_type != 'remove':
                main.log.error( "Invalid action type. Use 'add' or "
                                "'remove' table rule" )
                if rule != 'DROP' and rule != 'ACCEPT' and rule != 'LOG':
                    # NOTE Currently only supports rules DROP, ACCEPT, and LOG
                    main.log.error( "Invalid rule. Valid rules are 'DROP' or "
                                    "'ACCEPT' or 'LOG' only." )
                    if direction != 'INPUT' and direction != 'OUTPUT':
                        # NOTE currently only supports rules INPUT and OUPTUT
                        main.log.error( "Invalid rule. Valid directions are"
                                        " 'OUTPUT' or 'INPUT'" )
                        return main.FALSE
                    return main.FALSE
                return main.FALSE
            if action_type == 'add':
                # -A is the 'append' action of iptables
                actionFlag = '-A'
            elif action_type == 'remove':
                # -D is the 'delete' rule of iptables
                actionFlag = '-D'
            self.handle.sendline( "" )
            self.handle.expect( "\$" )
            cmd = "sudo iptables " + actionFlag + " " +\
                  direction +\
                  " -s " + str( ip )
                  # " -p " + str( packet_type ) +\
            if packet_type:
                cmd += " -p " + str( packet_type )
            if port:
                cmd += " --dport " + str( port )
            if states:
                cmd += " -m state --state="
                #FIXME- Allow user to configure which states to block
                cmd += "INVALID,ESTABLISHED,NEW,RELATED,UNTRACKED"
            cmd += " -j " + str( rule )

            self.handle.sendline( cmd )
            self.handle.expect( "\$" )
            main.log.warn( self.handle.before )

            info_string = "On " + str( self.name )
            info_string += " " + str( action_type )
            info_string += " iptable rule [ "
            info_string += " IP: " + str( ip )
            info_string += " Port: " + str( port )
            info_string += " Rule: " + str( rule )
            info_string += " Direction: " + str( direction ) + " ]"
            main.log.info( info_string )
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Timeout exception in "
                                "setIpTables function" )
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

    def detailed_status(self, log_filename):
        """
        This method is used by STS to check the status of the controller
        Reports RUNNING, STARTING, STOPPED, FROZEN, ERROR (and reason)
        """
        import re
        try:
            self.handle.sendline( "" )
            self.handle.expect( "\$" )
            self.handle.sendline( "cd " + self.home )
            self.handle.expect( "\$" )
            self.handle.sendline( "service onos status" )
            self.handle.expect( "\$" )
            response = self.handle.before
            if re.search( "onos start/running", response ):
                # onos start/running, process 10457
                return 'RUNNING'
            # FIXME: Implement this case
            # elif re.search( pattern, response ):
            #      return 'STARTING'
            elif re.search( "onos stop/", response ):
                # onos stop/waiting
                # FIXME handle this differently?:  onos stop/pre-stop
                return 'STOPPED'
            # FIXME: Implement this case
            # elif re.search( pattern, response ):
            #      return 'FROZEN'
            else:
                main.log.warn( self.name +
                               " WARNING: status received unknown response" )
                main.log.warn( response )
                return 'ERROR', "Unknown response: %s" % response
        except pexpect.TIMEOUT:
            main.log.exception( self.name + ": Timeout exception in "
                                "setIpTables function" )
            return 'ERROR', "Pexpect Timeout"
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def createLinkGraphFile( self, benchIp, ONOSIpList, deviceCount):
        '''
            Create/formats the LinkGraph.cfg file based on arguments
                -only creates a linear topology and connects islands
                -evenly distributes devices
                -must be called by ONOSbench

                ONOSIpList - list of all of the node IPs to be used

                deviceCount - number of switches to be assigned
        '''
        main.log.info("Creating link graph configuration file." )
        linkGraphPath = self.home + "/tools/package/etc/linkGraph.cfg"
        tempFile = "/tmp/linkGraph.cfg"

        linkGraph = open(tempFile, 'w+')
        linkGraph.write("# NullLinkProvider topology description (config file).\n")
        linkGraph.write("# The NodeId is only added if the destination is another node's device.\n")
        linkGraph.write("# Bugs: Comments cannot be appended to a line to be read.\n")

        clusterCount = len(ONOSIpList)

        if type(deviceCount) is int or type(deviceCount) is str:
            deviceCount = int(deviceCount)
            switchList = [0]*(clusterCount+1)
            baselineSwitchCount = deviceCount/clusterCount

            for node in range(1, clusterCount + 1):
                switchList[node] = baselineSwitchCount

            for node in range(1, (deviceCount%clusterCount)+1):
                switchList[node] += 1

        if type(deviceCount) is list:
            main.log.info("Using provided device distribution")
            switchList = [0]
            for i in deviceCount:
                switchList.append(int(i))

        tempList = ['0']
        tempList.extend(ONOSIpList)
        ONOSIpList = tempList

        myPort = 6
        lastSwitch = 0
        for node in range(1, clusterCount+1):
            if switchList[node] == 0:
                continue

            linkGraph.write("graph " + ONOSIpList[node] + " {\n")

            if node > 1:
                #connect to last device on previous node
                line = ("\t0:5 -> " + str(lastSwitch) + ":6:" + lastIp + "\n")     #ONOSIpList[node-1]
                linkGraph.write(line)

            lastSwitch = 0
            for switch in range (0, switchList[node]-1):
                line = ""
                line = ("\t" + str(switch) + ":" + str(myPort))
                line += " -- "
                line += (str(switch+1) + ":" + str(myPort-1) + "\n")
                linkGraph.write(line)
                lastSwitch = switch+1
            lastIp = ONOSIpList[node]

            #lastSwitch += 1
            if node < (clusterCount):
                #connect to first device on the next node
                line = ("\t" + str(lastSwitch) + ":6 -> 0:5:" + ONOSIpList[node+1] + "\n")
                linkGraph.write(line)

            linkGraph.write("}\n")
        linkGraph.close()

        #SCP
        os.system( "scp " + tempFile + " " + self.user_name + "@" + benchIp + ":" + linkGraphPath)
        main.log.info("linkGraph.cfg creation complete")

    def configNullDev( self, ONOSIpList, deviceCount, numPorts=10):

        '''
            ONOSIpList = list of Ip addresses of nodes switches will be devided amongst
            deviceCount = number of switches to distribute, or list of values to use as custom distribution
            numPorts = number of ports per device. Defaults to 10 both in this function and in ONOS. Optional arg
        '''

        main.log.info("Configuring Null Device Provider" )
        clusterCount = len(ONOSIpList)

        try:

            if type(deviceCount) is int or type(deviceCount) is str:
                main.log.info("Creating device distribution")
                deviceCount = int(deviceCount)
                switchList = [0]*(clusterCount+1)
                baselineSwitchCount = deviceCount/clusterCount

                for node in range(1, clusterCount + 1):
                    switchList[node] = baselineSwitchCount

                for node in range(1, (deviceCount%clusterCount)+1):
                    switchList[node] += 1

            if type(deviceCount) is list:
                main.log.info("Using provided device distribution")

                if len(deviceCount) == clusterCount:
                    switchList = ['0']
                    switchList.extend(deviceCount)

                if len(deviceCount) == (clusterCount + 1):
                    if deviceCount[0] == '0' or deviceCount[0] == 0:
                        switchList = deviceCount

                assert len(switchList) == (clusterCount + 1)

        except AssertionError:
            main.log.error( "Bad device/Ip list match")
        except TypeError:
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()


        ONOSIp = [0]
        ONOSIp.extend(ONOSIpList)

        devicesString  = "devConfigs = "
        for node in range(1, len(ONOSIp)):
            devicesString += (ONOSIp[node] + ":" + str(switchList[node] ))
            if node < clusterCount:
                devicesString += (",")

        try:
            self.handle.sendline("onos $OC1 cfg set org.onosproject.provider.nil.device.impl.NullDeviceProvider devConfigs " + devicesString )
            self.handle.expect(":~")
            self.handle.sendline("onos $OC1 cfg set org.onosproject.provider.nil.device.impl.NullDeviceProvider numPorts " + str(numPorts) )
            self.handle.expect(":~")

            for i in range(10):
                self.handle.sendline("onos $OC1 cfg get org.onosproject.provider.nil.device.impl.NullDeviceProvider")
                self.handle.expect(":~")
                verification = self.handle.before
                if (" value=" + str(numPorts)) in verification and (" value=" + devicesString) in verification:
                    break
                else:
                    time.sleep(1)

            assert ("value=" + str(numPorts)) in verification and (" value=" + devicesString) in verification

        except AssertionError:
            main.log.error("Incorrect Config settings: " + verification)
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def configNullLink( self,fileName="/opt/onos/apache-karaf-3.0.3/etc/linkGraph.cfg", eventRate=0):
        '''
                fileName default is currently the same as the default on ONOS, specify alternate file if
                you want to use a different topology file than linkGraph.cfg
        '''


        try:
            self.handle.sendline("onos $OC1 cfg set org.onosproject.provider.nil.link.impl.NullLinkProvider eventRate " + str(eventRate))
            self.handle.expect(":~")
            self.handle.sendline("onos $OC1 cfg set org.onosproject.provider.nil.link.impl.NullLinkProvider cfgFile " + fileName )
            self.handle.expect(":~")

            for i in range(10):
                self.handle.sendline("onos $OC1 cfg get org.onosproject.provider.nil.link.impl.NullLinkProvider")
                self.handle.expect(":~")
                verification = self.handle.before
                if (" value=" + str(eventRate)) in verification and (" value=" + fileName) in verification:
                    break
                else:
                    time.sleep(1)

            assert ("value=" + str(eventRate)) in verification and (" value=" + fileName) in verification

        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except AssertionError:
            main.log.info("Settings did not post to ONOS")
            main.log.error(varification)
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.log.error(varification)
            main.cleanup()
            main.exit()

    def getOnosIps( self ):
        """
            Get all onos IPs stored in
        """

        return sorted( self.onosIps.values() )

    def logReport( self, nodeIp, searchTerms, outputMode="s" ):
        """
        Searches the latest ONOS log file for the given search terms and
        prints the total occurances of each term. Returns to combined total of
        all occurances.

        Arguments:
            * nodeIp - The ip of the ONOS node where the log is located
            * searchTerms - A string to grep for or a list of strings to grep
                            for in the ONOS log. Will print out the number of
                            occurances for each term.
        Optional Arguments:
            * outputMode - 's' or 'd'. If 'd' will print the last 5 lines
                           containing each search term as well as the total
                           number of occurances of each term. Defaults to 's',
                           which prints the simple output of just the number
                           of occurances for each term.
        """
        try:
            main.log.info( " Log Report for {} ".format( nodeIp ).center( 70, '=' ) )
            if type( searchTerms ) is str:
                searchTerms = [searchTerms]
            numTerms = len( searchTerms )
            outputMode = outputMode.lower()

            totalHits = 0
            logLines = []
            for termIndex in range( numTerms ):
                term = searchTerms[termIndex]
                logLines.append( [term] )
                cmd = "onos-ssh " + nodeIp + " cat /opt/onos/log/karaf.log | grep " + term
                self.handle.sendline( cmd )
                self.handle.expect( ":~" )
                before = self.handle.before.splitlines()
                count = 0
                for line in before:
                    if term in line and "grep" not in line:
                        count += 1
                        if before.index( line ) > ( len( before ) - 7 ):
                            logLines[termIndex].append( line )
                main.log.info( "{}: {}".format( term, count ) )
                totalHits += count
                if termIndex == numTerms - 1:
                    print "\n"
            if outputMode != "s":
                outputString = ""
                for term in logLines:
                    outputString = term[0] + ": \n"
                    for line in range( 1, len( term ) ):
                        outputString += ( "\t" + term[line] + "\n" )
                    if outputString != ( term[0] + ": \n" ):
                        main.log.info( outputString )
            main.log.info( "=" * 70 )
            return totalHits
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def copyMininetFile( self, fileName, localPath, userName, ip,
                         mnPath='~/mininet/custom/', timeout = 60 ):
        """
        Description:
            Copy mininet topology file from dependency folder in the test folder
            and paste it to the mininet machine's mininet/custom folder
        Required:
            fileName - Name of the topology file to copy
            localPath - File path of the mininet topology file
            userName - User name of the mininet machine to send the file to
            ip - Ip address of the mininet machine
        Optional:
            mnPath - of the mininet directory to send the file to
        Return:
            Return main.TRUE if successfully copied the file otherwise
            return main.FALSE
        """

        try:
            cmd = "scp " + localPath + fileName + " " + userName + "@" + \
                  str( ip ) + ":" + mnPath + fileName

            self.handle.sendline( "" )
            self.handle.expect( "\$" )

            main.log.info( self.name + ": Execute: " + cmd )

            self.handle.sendline( cmd )

            i = self.handle.expect( [ 'No such file',
                                      "100%",
                                      pexpect.TIMEOUT ] )

            if i == 0:
                main.log.error( self.name + ": File " + fileName +
                                " does not exist!" )
                return main.FALSE

            if i == 1:
                main.log.info( self.name + ": File " + fileName +
                                " has been copied!" )
                self.handle.sendline( "" )
                self.handle.expect( "\$" )
                return main.TRUE

        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":    " + self.handle.before )
            main.cleanup()
            main.exit()
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": TIMEOUT exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()

    def jvmSet(self, memory=8):

        import os

        homeDir = os.path.expanduser('~')
        filename = "/onos/tools/package/bin/onos-service"

        serviceConfig = open(homeDir + filename, 'w+')
        serviceConfig.write("#!/bin/bash\n ")
        serviceConfig.write("#------------------------------------- \n ")
        serviceConfig.write("# Starts ONOS Apache Karaf container\n ")
        serviceConfig.write("#------------------------------------- \n ")
        serviceConfig.write("#export JAVA_HOME=${JAVA_HOME:-/usr/lib/jvm/java-7-openjdk-amd64/}\n ")
        serviceConfig.write("""export JAVA_OPTS="${JAVA_OPTS:--Xms""" + str(memory) + "G -Xmx" + str(memory) + """G}" \n """)
        serviceConfig.write("[ -d $ONOS_HOME ] && cd $ONOS_HOME || ONOS_HOME=$(dirname $0)/..\n")
        serviceConfig.write("""${ONOS_HOME}/apache-karaf-$KARAF_VERSION/bin/karaf "$@" \n """)
        serviceConfig.close()

    def createDBFile( self, testData ):

        filename = main.TEST + "DB"
        DBString = ""

        for item in testData:
            if type( item ) is string:
                item = "'" + item + "'"
            if testData.index( item ) < len( testData - 1 ):
                item += ","
            DBString += str( item )

        DBFile = open( filename, "a" )
        DBFile.write( DBString )
        DBFile.close()

    def verifySummary( self, ONOSIp, *deviceCount ):

        self.handle.sendline( "onos " + ONOSIp  + " summary" )
        self.handle.expect( ":~" )

        summaryStr = self.handle.before
        print "\nSummary\n==============\n" + summaryStr + "\n\n"

        #passed = "SCC(s)=1" in summaryStr
        #if deviceCount:
        #    passed = "devices=" + str(deviceCount) + "," not in summaryStr

        passed = False
        if "SCC(s)=1," in summaryStr:
            passed = True
            print "Summary is verifed"
        else:
            print "Summary failed"

        if deviceCount:
            print" ============================="
            checkStr = "devices=" + str( deviceCount[0] ) + ","
            print "Checkstr: " + checkStr
            if checkStr not in summaryStr:
                passed = False
                print "Device count failed"
            else:
                print "device count verified"

        return passed

    def getIpAddr( self, iface=None ):
        """
        Update self.ip_address with numerical ip address. If multiple IP's are
        located on the device, will attempt to use self.nicAddr to choose the
        right one. Defaults to 127.0.0.1 if no other address is found or cannot
        determine the correct address.

        ONLY WORKS WITH IPV4 ADDRESSES
        """
        try:
            LOCALHOST = "127.0.0.1"
            ipPat = "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
            pattern = re.compile( ipPat )
            match = re.search( pattern, self.ip_address )
            if self.nicAddr:
                nicPat = self.nicAddr.replace( ".", "\." ).replace( "\*", r"\d{1,3}" )
                nicPat = re.compile( nicPat )
            else:
                nicPat = None
            # IF self.ip_address is an ip address and matches
            #    self.nicAddr: return self.ip_address
            if match:
                curIp = match.group(0)
                if nicPat:
                    nicMatch = re.search( nicPat, curIp )
                    if nicMatch:
                        return self.ip_address
            # ELSE: IF iface, return ip of interface
            cmd = "ifconfig"
            ifPat = re.compile( "inet addr:({})".format( ipPat ) )
            if iface:
                cmd += " " + str( iface )
            raw = subprocess.check_output( cmd.split() )
            ifPat = re.compile( "inet addr:({})".format( ipPat ) )
            ips = re.findall( ifPat, raw )
            if iface:
                if ips:
                    ip = ips[0]
                    self.ip_address = ip
                    return ip
                else:
                    main.log.error( "Error finding ip, ifconfig output:".format( raw ) )
            # ELSE: attempt to get address matching nicPat.
            if nicPat:
                for ip in ips:
                    curMatch = re.search( nicPat, ip )
                    if curMatch:
                        self.ip_address = ip
                        return ip
            else:  # If only one non-localhost ip, return that
                tmpList = [ ip for ip in ips if ip is not LOCALHOST ]
                if len(tmpList) == 1:
                    curIp = tmpList[0]
                    self.ip_address = curIp
                    return curIp
            # Either no non-localhost IPs, or more than 1
            main.log.warn( "getIpAddr failed to find a public IP address" )
            return LOCALHOST
        except subprocess.CalledProcessError:
            main.log.exception( "Error executing ifconfig" )
        except IndexError:
            main.log.exception( "Error getting IP Address" )
        except Exception:
            main.log.exception( "Uncaught exception" )

    def startBasicONOS(self, nodeList, opSleep = 60, onosStartupSleep = 60):

        '''
        Start onos cluster with defined nodes, but only with drivers app

        '''
        import time

        self.createCellFile( self.ip_address,
                                       "temp",
                                       self.ip_address,
                                       "drivers",
                                       nodeList )

        main.log.info( self.name + ": Apply cell to environment" )
        cellResult = self.setCell( "temp" )
        verifyResult = self.verifyCell()

        main.log.info( self.name + ": Creating ONOS package" )
        packageResult = self.onosPackage( opTimeout=opSleep )

        main.log.info( self.name + ": Installing ONOS package" )
        for nd in nodeList:
                    self.onosInstall( node=nd )

        main.log.info( self.name + ": Starting ONOS service" )
        time.sleep( onosStartupSleep )

        onosStatus = True
        for nd in nodeList:
            onosStatus = onosStatus & self.isup( node = nd )
            #print "onosStatus is: " + str( onosStatus )

        return main.TRUE if onosStatus else main.FALSE

