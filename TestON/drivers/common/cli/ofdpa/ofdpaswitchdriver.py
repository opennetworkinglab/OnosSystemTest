#!/usr/bin/env python
"""
Copyright 2018 Open Networking Foundation (ONF)

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
import re
import json
import types
import time
import os
from drivers.common.clidriver import CLI
from core import utilities
from shutil import copyfile

class OFDPASwitchDriver( CLI ):

    def __init__( self ):
        """
        Initialize client
        """
        super( CLI, self ).__init__()
        self.name = None
        self.shortName = None
        self.handle = None
        self.prompt = "~#"
        # Respect to bin folder
        self.home = "../drivers/common/cli/ofdpa/"
        # Local home for functions using scp
        self.tempDirectory = "/tmp/"
        self.conf = "ofagent.conf"
        self.switchDirectory = "/etc/ofagent/"
        self.ports = []
        self.isup = False

    def connect( self, **connectargs ):
        """
        Creates ssh handle for Accton cli.
        """
        try:
            # Parse keys in xml object
            for key in connectargs:
                vars( self )[ key ] = connectargs[ key ]
            # Get the name
            self.name = self.options[ 'name' ]
            self.shortName = self.options[ 'shortName' ]
            # Get the dpid
            self.dpid = self.options[ 'dpid' ]
            # Get ofagent patch
            for key, value in self.options.items():
                if re.match( 'link[\d]+', key ):
                    self.ports.append( { 'enabled': True,
                                         'ips': [ None ],
                                         'mac': None,
                                         'name': None,
                                         'node2': value[ 'node2' ],
                                         'port2': value[ 'port2' ],
                                         'of_port': value[ 'port1' ] } )
            if 'confDir' in self.options:
                self.switchDirectory = self.options[ 'confDir' ]
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
            # Build the handle using the above information
            self.handle = super(OFDPASwitchDriver, self ).connect(
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
                main.log.error( "Failed to connect to the OFDPA CLI" )
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
        Called when Test is complete to disconnect the OFDPASwitchDriver handle.
        """
        response = main.TRUE
        try:
            if self.handle:
                # Stop the ofagent
                self.stopOfAgent()
                # Disconnect from the device
                self.handle.sendline( "" )
                self.handle.expect( self.prompt )
                self.handle.sendline( "exit" )
                self.handle.expect( "closed" )
        # Errors handling
        except pexpect.TIMEOUT:
            main.log.error( self.name + ": pexpect.TIMEOUT found" )
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

    def assignSwController( self, ip, port="6653", ptcp="", updateConf=False ):
        """
        Description:
            The assignment is realized properly creating the agent.conf
            for each switch and then pushing it into the device.
        Required:
            ip - Ip addresses of controllers. This can be a list or a string.
        Optional:
            port - controller port is ignored
            ptcp - ptcp information is ignored
            updateConf - create new ofagent conf file and push to the switch if
                         set to True; otherwise will use the existing conf file
                         on the switch.
        Return:
            Returns main.TRUE if the switch is correctly assigned to controllers,
            otherwise it will return main.FALSE or an appropriate exception(s)
        """
        assignResult = main.TRUE
        # Initial arguments for OFDPA
        opt_args = 'OPT_ARGS="-d 2 -c 2 -c 4 '
        onosIp = ""
        # Parses the controller option
        try:
            if isinstance( ip, types.StringType ):
                onosIp = "-t " + str( ip )
            elif isinstance( ip, types.ListType ):
                for ipAddress in ip:
                    onosIp += "-t " + str( ipAddress ) + " "
            else:
                main.log.error( self.name + ": Invalid ip address" )
                return main.FALSE
            # Complete the arguments adding the dpid
            opt_args += onosIp + '-i %s' % self.dpid + '"'
            if updateConf:
                # Create a copy of the cfg file using the template
                self.createCfg()
                # Load the cfg file and adds the missing option
                self.updateCfg( opt_args )
                # Backup the cfg on the switch
                self.backupCfg()
                # Push the new cfg on the device
                self.pushCfg()
                # Start the ofagent on the device
            self.startOfAgent()
            # Enable all the ports
            assignResult = utilities.retry(
                self.enablePorts,
                main.FALSE,
                kwargs={},
                attempts=10,
                sleep=10)
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

    def createCfg( self ):
        """
        Create in bench context a new config file starting from the template
        """
        copyfile(self.home + self.conf + ".template", self.tempDirectory + self.conf)

    def updateCfg( self, opt_args):
        """
        Add the arguments related to the current switch (self)
        """
        with open(self.tempDirectory + self.conf, "a") as cfg:
            cfg.write(opt_args + "\n")
            cfg.close()

    def backupCfg( self ):
        """
        Create a backup file of the old configuration on the switch
        """
        try:
            self.handle.sendline( "" )
            self.handle.expect( self.prompt )
            self.handle.sendline( "cp %s%s %s%s.backup" % (self.switchDirectory, self.conf, self.switchDirectory, self.conf) )
            self.handle.expect( self.prompt )
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

    def pushCfg( self ):
        """
        Push the new configuration from the network bench
        """
        # We use os.system to send the command from TestON cluster
        # to the switches. This means that passwordless access is
        # necessary in order to push the configuration file
        os.system( "scp " + self.tempDirectory + self.conf + " " +
                   self.user_name + "@" + self.ip_address + ":" + self.switchDirectory)

    def ofagentIsRunning( self ):
        """
        Return main.TRUE if service ofagentd is running on the
        switch; otherwise main.FALSE
        """
        try:
            self.handle.sendline( "" )
            self.handle.expect( self.prompt )
            self.handle.sendline( "service ofagentd status" )
            self.handle.expect( self.prompt )
            response = self.handle.before
            if "ofagentd is running" in response:
                return main.TRUE
            else:
                return main.FALSE
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

    def startOfAgent( self ):
        """
        Start the ofagent on the device
        """
        try:
            if self.ofagentIsRunning():
                main.log.warn( self.name + ": ofagentd is already running" )
                return main.TRUE
            self.handle.sendline( "" )
            self.handle.expect( self.prompt )
            self.handle.sendline( "service ofagentd start" )
            self.handle.expect( self.prompt )
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

    def stopOfAgent( self ):
        """
        Stop the ofagent on the device
        """
        try:
            self.handle.sendline( "" )
            self.handle.expect( self.prompt )
            self.handle.sendline( "service ofagentd stop" )
            self.handle.expect( self.prompt )
            self.isup = False
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

    def dumpFlows( self ):
        """
        Dump the flows from the devices
        FIXME need changes in the workflow in order to be used
        """
        try:
            self.handle.sendline( "" )
            self.handle.expect( self.prompt )
            # Create the dump of the flows locally on the switches
            self.handle.sendline( "client_flowtable_dump" )
            self.handle.expect( self.prompt )
            response = self.handle.before
            # Write back in the tmp folder - needs to be changed in future
            with open(self.tempDirectory + "flows_%s.txt" % self.dpid, "w") as flows:
                flows.write(response + "\n")
                flows.close()
            # Done return for further processing
            return response
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

    def dumpGroups( self ):
        """
        Dump the groups from the devices
        FIXME need changes in the workflow in order to be used
        """
        try:
            self.handle.sendline( "" )
            self.handle.expect( self.prompt )
            self.handle.sendline( "client_grouptable_dump > groups.txt" )
            self.handle.expect( self.prompt )
            response = self.handle.before
            # Write back in the tmp folder - needs to be changed in future
            with open(self.tempDirectory + "groups_%s.txt" % self.dpid, "w") as groups:
                groups.write(response + "\n")
                groups.close()
            # Done return for further processing
            return response
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

    def enablePorts( self ):
        """
        Enable all the ports on the devices
        It needs to wait for the boot
        """
        try:
            self.handle.sendline( "" )
            self.handle.expect( self.prompt )
            self.handle.sendline( "client_port_table_dump" )
            self.handle.expect( self.prompt )
            response = self.handle.before
            if "Error from ofdpaClientInitialize()" in response:
                main.log.warn( self.name + ": Not yet started" )
                return main.FALSE
            # Change port speed
            self.handle.sendline( "sh portspeed" )
            self.handle.expect( self.prompt )
            response = self.handle.before
            if "Failure calling" in response:
                main.log.warn( self.name + ": failed to change port speed" )
                return main.FALSE
            return main.TRUE
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

    def setPortSpeed( self, index, speed=40000 ):
        """
        Run client_drivshell on the switch to set speed for a
        specific port
        index: port index, e.g. 1
        speed: port speed, e.g. 40000
        """
        try:
            self.handle.sendline( "" )
            self.handle.expect( self.prompt )
            cmd = "client_drivshell port {} sp={}".format( index, speed )
            self.handle.sendline( cmd )
            self.handle.expect( self.prompt )
            response = self.handle.before
            return main.TRUE
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

    def updatePorts( self ):
        """
        Get latest port status on the switch by running
        client_port_table_dump commmand and parsing the output
        """
        try:
            self.handle.sendline( "" )
            self.handle.expect( self.prompt )
            self.handle.sendline( "client_port_table_dump" )
            self.handle.expect( self.prompt )
            ports = self.handle.before
            if "Error from ofdpaClientInitialize()" in ports:
                main.log.warn( self.name + ": Not yet started" )
                return main.FALSE
            ports = re.findall( r"0x[\d]+.*port[\d]+:\r\r\n.*\r\r\n.*PeerFeature:.*\r\r\n", ports )
            for port in ports:
                m = re.match( r".*port([\d]+):\r\r\n.*state = (.*), mac", port )
                index = m.group( 1 )
                enabled = True if m.group( 2 ) == '0x00000000' else False
                for p in self.ports:
                    if p[ 'of_port' ] == index:
                        p[ 'enabled' ] = enabled
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
