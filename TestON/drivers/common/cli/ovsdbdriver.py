#!/usr/bin/env python

"""
drivers for ovsdb commands.

zhanghaoyu7@huawei.com
AUG 10 2015
"""
import pexpect
import re
import json
import types
import time
import os
from drivers.common.clidriver import CLI


class OvsdbDriver( CLI ):

    def __init__( self ):
        """
        Initialize client
        """
        self.name = None
        self.home = None
        self.handle = None
        super( CLI, self ).__init__()

    def connect( self, **connectargs ):
        try:
            for key in connectargs:
                vars( self)[ key ] = connectargs[ key ]

            self.name = self.options[ 'name' ]
            if os.getenv( str( self.ip_address ) ) != None:
                self.ip_address = os.getenv(str ( self.ip_address ) )
            else:
                main.log.info( self.name + ": Trying to connect to " +
                               self.ip_address )
            self.handle = super( OvsdbDriver, self ).connect(
                    user_name=self.user_name,
                    ip_address=self.ip_address,
                    port=self.port,
                    pwd=self.pwd)

            if self.handle:
                return self.handle
                main.log.onfo( "Connection successful to the ovsdb node " +
                                self.name )
            else:
                main.log.error( "Connection failed to the ovsdb node " +
                                self.name )
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
        try:
            self.handle.sendline( "exit" )
            self.handle.expect( "closed" )
            response = main.TRUE
        except pexpect.ExceptionPexpect:
            response = main.FALSE
            main.log.exception( self.name + ": Uncaught exception!" )
        return response

    def setManager( self, ip, port, delaytime="5" ):
        command= "sudo ovs-vsctl set-manager tcp:" + str( ip ) + ":" + str( port )
        try:
            handle = self.execute(
                cmd=command,
                timeout=10 )
            if re.search( "Error", handle ):
                main.log.error( "Error in set ovsdb manager" )
                main.log.error( handle )
                return main.FALSE
            else:
                main.log.info( "Ovsdb manager " + str( ip ) + " set" )
                #delay time  for ovsdb connection create
                main.log.info( "Wait " + str( delaytime ) + " seconds for ovsdb connection create" )
                time.sleep( int( delaytime ) )
                return main.TRUE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()

    def delManager( self, delaytime="5" ):
        command= "sudo ovs-vsctl del-manager"
        try:
            handle = self.execute(
                cmd=command,
                timeout=10 )
            if re.search( "Error", handle ):
                main.log.error( "Error in delete ovsdb manager" )
                main.log.error( handle )
                return main.FALSE
            else:
                main.log.info( "Ovsdb manager delete" )
                #delay time  for ovsdb connection delete
                main.log.info( "Wait " + str( delaytime ) + " seconds for ovsdb connection delete" )
                time.sleep( int( delaytime ) )
                return main.TRUE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()

    def getManager( self ):
        command= "sudo ovs-vsctl get-manager"
        try:
            response = self.execute(
                cmd=command,
                timeout=10 )
            return response
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()

    def listBr( self ):
        """
        Parameters:
            none
        Return:
            The output of the command from the linux
            or main.FALSE on timeout
        """
        command= "sudo ovs-vsctl list-br"
        try:
            response = self.execute(
                cmd=command,
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

    def listPorts( self, sw ):
        """
        Parameters:
            sw: The name of an OVS switch. Example "s1"
        Return:
            The output of the command from the linux
            or main.FALSE on timeout
        """
        command= "sudo ovs-vsctl list-ports " + str( sw )
        try:
            response = self.execute(
                cmd=command,
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

    def getController( self, sw ):
        """
        Parameters:
            sw: The name of an OVS switch. Example "s1"
        Return:
            The output of the command from the mininet cli
            or main.FALSE on timeout"""
        command = "sudo ovs-vsctl get-controller " + str( sw )
        try:
            response = self.execute(
                cmd=command,
                timeout=10)
            if response:
                return response
            else:
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
    def show( self ):
        """
        Parameters:
            none
        Return:
            The output of the command from the linux
            or main.FALSE on timeout"""
        command = "sudo ovs-vsctl show "
        try:
            response = self.execute(
                cmd=command,
                timeout=10)
            if response:
                return response
            else:
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()
