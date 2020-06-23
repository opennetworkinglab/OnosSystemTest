#!/usr/bin/env python
"""
Copyright 2020 Open Networking Foundation (ONF)

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
"""

import pexpect
import types
import os
from drivers.common.clidriver import CLI

class StratumOSSwitchDriver( CLI ):

    def __init__( self ):
        """
        Initialize client
        """
        super( CLI, self ).__init__()
        self.name = None
        self.shortName = None
        self.handle = None
        self.prompt = "~(/TestON)?#"
        self.dockerPrompt = "/run/stratum#"

        self.home = "/root"
        # Local home for functions using scp
        self.tempDirectory = "/tmp/"
        self.ports = []
        self.isup = True

    def connect( self, **connectargs ):
        """
        Creates ssh handle for cli.
        """
        try:
            # Parse keys in xml object
            for key in connectargs:
                vars( self )[ key ] = connectargs[ key ]
            # Get the name
            self.name = self.options[ 'name' ]
            self.shortName = self.options[ 'shortName' ]
            # Parse the IP address
            try:
                if os.getenv( str( self.ip_address ) ) is not None:
                    self.ip_address = os.getenv( str( self.ip_address ) )
                # Otherwise is an ip address
                else:
                    main.log.info( self.name + ": Trying to connect to " + self.ip_address )
            # Error handling
            except KeyError:
                main.log.info( "Invalid host name," + " connecting to local host instead" )
                self.ip_address = 'localhost'
            except Exception as inst:
                main.log.error( "Uncaught exception: " + str( inst ) )
            self.handle = super( StratumOSSwitchDriver, self ).connect(
                user_name=self.user_name,
                ip_address=self.ip_address,
                port=None,
                pwd=self.pwd)
            # Successful connection
            if self.handle:
                main.log.info( "Connection successful to the host " + self.user_name + "@" + self.ip_address )
                self.handle.sendline( "" )
                self.handle.expect( self.prompt )
                return main.TRUE
            # Connection failed
            else:
                main.log.error( "Connection failed to the host " + self.user_name + "@" + self.ip_address )
                main.log.error( "Failed to connect to the Stratum Switch" )
                return main.FALSE
        # Error handling
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
        Called when Test is complete to disconnect the component handle.
        """
        response = main.TRUE
        try:
            if self.handle:
                # Stop the agent
                self.stopSwitchAgent()
                main.log.debug( self.name + ": Disconnected" )
                # Disconnect from the device
                self.handle.sendline( "" )
                self.handle.expect( self.prompt )
                self.handle.sendline( "exit" )
                self.handle.expect( "closed" )
        # Errors handling
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": pexpect.TIMEOUT found" )
            main.log.debug( self.handle.before )
            return main.FALSE
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

    def assignSwController( self, ip, updateConf=True, **kwargs ):
        """
        Description:
            Edit the config file for the switch and upload it to the onos
            controller to connect the switch and controller

            NOTE that this function is available on all switch drivers,
            and the name is a hold over from ovs switches.
            kwargs contains any arguments for other types of switches
        Required:
            ip - Ip addresses of controllers. This can be a list or a string.
            updateConf - whether to pull and update configurations and scripts
        Return:
            Returns main.TRUE if the switch is correctly assigned to controllers,
            otherwise it will return main.FALSE or an appropriate exception(s)
        """
        assignResult = main.TRUE
        onosIp = ""
        # Parses the controller option
        # We only need one onos ip
        try:
            if isinstance( ip, types.StringType ):
                onosIp = str( ip )
            elif isinstance( ip, types.ListType ):
                onosIp = ip[ 0 ]
            else:
                main.log.error( self.name + ": Invalid controller ip address" )
                return main.FALSE
            if updateConf:
                self.setupContainer()
                main.ONOSbench.onosNetCfg( onosIp, self.options[ 'onosConfigPath' ], self.options[ 'onosConfigFile' ] )

            assignResult = self.startSwitchAgent()
            if not assignResult:
                self.isup = False
            else:
                self.isup = True
            # Done return true
            return assignResult
        # Errors handling
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": pexpect.TIMEOUT found" )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def setupContainer( self ):
        """
        Prepare for the container to be run. Includes pulling scripts
        and modifying them
        """
        try:
            #TODO Remove hardcoding
            main.log.info( "Creating working directory" )
            self.handle.sendline( "mkdir TestON" )
            self.handle.expect( self.prompt )
            self.handle.sendline( "cd TestON" )
            self.handle.expect( self.prompt )

            main.log.info( "Getting start container script" )
            # TODO: Parameterize this
            self.handle.sendline( "wget --backups=1 https://raw.githubusercontent.com/stratum/stratum/master/stratum/hal/bin/barefoot/docker/start-stratum-container.sh" )
            self.handle.expect( self.prompt )
            main.log.info( "Modify start container script" )
            self.handle.sendline( "sed -i '/--privileged/a \    --name stratum \\\\' start-stratum-container.sh" )
            self.handle.expect( self.prompt )
            #self.handle.sendline( "sed -i '/LOG_DIR:\/var\/log\/stratum/a \    --entrypoint /bin/bash \\\\' start-stratum-container.sh" )
            #self.handle.expect( self.prompt )
            # TODO: Add docker pull command to the start-stratum-container.sh script

            main.log.info( "Getting chassis config" )
            # TODO: Parameterize this
            self.handle.sendline( "wget --backups=1 https://raw.githubusercontent.com/stratum/stratum/master/stratum/hal/config/x86-64-accton-wedge100bf-32x-r0/chassis_config.pb.txt" )
            self.handle.expect( self.prompt )
            main.log.info( "Modify chassis config" )
            # TODO: Parameterize this
            self.handle.sendline( "sed -i '$!N;s/\(port: [5|6]\\n\  speed_bps: \)\([0-9]*\)/\\1 40000000000/;P;D' chassis_config.pb.txt" )
            self.handle.expect( self.prompt )
            self.handle.sendline( "export CHASSIS_CONFIG=~/TestON/chassis_config.pb.txt" )
            self.handle.expect( self.prompt )
            self.handle.sendline( "chmod +x start-stratum-container.sh" )
            self.handle.expect( self.prompt )
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": pexpect.TIMEOUT found" )
            main.log.debug( self.handle.before )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def startSwitchAgent( self ):
        """
        Start the stratum agent on the device
        """
        try:
            main.log.info( "Starting switch agent" )
            self.handle.sendline( "./start-stratum-container.sh --bf-sim" )
            self.handle.expect( "Chassis config pushed successfully." )
            return main.TRUE
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": pexpect.TIMEOUT found" )
            main.log.debug( self.handle.before )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def stopSwitchAgent( self ):
        """
        Stop the strratum agent on the device
        """
        try:
            main.log.info( self.name + ": stopping Stratum Switch agent" )
            while True:
                self.handle.sendline( "" )
                i = self.handle.expect( [ self.prompt, self.dockerPrompt, pexpect.TIMEOUT, "Aborted at" ] )
                if i == 2:
                    self.handle.send( "\x03" )  # ctrl-c to close switch agent
                    self.handle.sendline( "" )
                elif i == 1:
                    self.handle.sendline( "exit" )  # exit docker
                    self.handle.expect( self.prompt )
                elif i == 0:
                    self.handle.sendline( "docker stop stratum" )  # Make sure the container is stopped
                    self.handle.expect( self.prompt )
                    main.log.debug( self.name + ": Stratum Switch agent stopped" )
                    return
                elif i == 3:
                    main.log.error( "Stratum agent aborted" )
                    # TODO: Find and save any extra logs
                    output = self.handle.before + self.handle.after
                    self.handle.sendline( "" )
                    self.handle.expect( self.prompt )
                    output += self.handle.before + self.handle.after
                    main.log.debug( output )
                    main.cleanAndExit()
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": pexpect.TIMEOUT found" )
            main.log.debug( self.handle.before )
            return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()
