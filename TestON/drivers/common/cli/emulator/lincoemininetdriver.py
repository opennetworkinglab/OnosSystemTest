#!/usr/bin/env python
"""

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


LincOEMininetDriver is an extension of the mininetclidriver to handle linc oe
"""
import pexpect
import re
import sys
import os
from drivers.common.cli.emulator.mininetclidriver import MininetCliDriver


class LincOEMininetDriver( MininetCliDriver ):
    def runOpticalMnScript( self,onosDirectory = 'onos', ctrllerIP = None ):
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
            if ctrllerIP == None:
                main.log.error( "You need to specify the IP" )
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
                topoFile = "~/{0}/tools/test/topos/opticalTest.py".format( onosDirectory )
                cmd = "sudo -E python {0} {1}".format( topoFile, controller )
                main.log.info( self.name + ": cmd = " + cmd )
                self.handle.sendline( cmd )
                lincStart = self.handle.expect( [ "mininet>", pexpect.TIMEOUT ],timeout=120 )
                if lincStart == 1:
                    self.handle.sendline( "\x03" )
                    self.handle.sendline( "sudo mn -c" )
                    self.handle.sendline( cmd )
                    lincStart = self.handle.expect( [ "mininet>", pexpect.TIMEOUT ],timeout=120 )
                if lincStart == 1:
                    main.log.error( "OpticalTest.py failed to start." )
                    return main.FALSE
                return main.TRUE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            return main.FALSE

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
