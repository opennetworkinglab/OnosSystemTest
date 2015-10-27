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

    def dumpFlows( self, sw, protocols=None ):
        """
        Parameters:
            sw: The name of an OVS switch. Example "s1"
        Return:
            The output of the command from the linux
            or main.FALSE on timeout"""
        if protocols:
            command = "sudo ovs-ofctl -O " + \
                protocols + " dump-flows " + str( sw )
        else:
            command = "sudo ovs-ofctl dump-flows " + str( sw )
        try:
            response = self.execute(
                cmd=command,
                timeout=10 )
            if response:
                return response
            else:
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()

    def createHost( self, hostname ):
        command = "sudo ip netns add " + str( hostname )
        try:
            handle = self.execute(
                cmd=command,
                timeout=10)
            if re.search( "Error", handle ):
                main.log.error( "Error in create host" + str( hostname ) )
                main.log.error( handle )
                return main.FALSE
            else:
                main.log.info( "Create " + str( hostname ) + " sucess" )
                return main.TRUE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()

    def createHostport(self, hostname="host1", hostport="host1-eth0", ovsport="port1", hostportmac="000000000001" ):
        command = "sudo ip link add " + str(hostport) +" type veth peer name " + str(ovsport)
        command += ";" + "sudo ip link set " + str(hostport) + " up"
        command += ";" + "sudo ip link set " + str(ovsport) + " up"
        command += ";" +" sudo ifconfig " + str(hostport) + " hw ether " + str(hostportmac)
        command += ";" +" sudo ip link set " + str(hostport) + " netns " + str(hostname)
        try:
            handle = self.execute(
                cmd=command,
                timeout=10)
            if re.search( "Error", handle ):
                main.log.error( "Error in create host port " + str( hostport ) + " on " + str( hostname ) )
                main.log.error( handle )
                return main.FALSE
            else:
                main.log.info( "Create host port " + str( hostport ) + " on " + str( hostname ) + " sucess" )
                return main.TRUE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()

    def addPortToOvs(self, ifaceId, attachedMac, vmuuid, port="port1", ovsname="br-int" ):
        command = "sudo ovs-vsctl add-port " + str(ovsname) +" " + str(port)
        if ifaceId:
            command += " -- set Interface " + str(port) + " external-ids:iface-id=" + str(ifaceId) + " external-ids:iface-status=active"
        if attachedMac:
            command += " external-ids:attached-mac=" + str(attachedMac)
        if vmuuid:
            command += " external-ids:vm-uuid=" + str(vmuuid)
        try:
            handle = self.execute(
                cmd=command,
                timeout=10)
            if re.search( "Error", handle ):
                main.log.error( "Error in add port " + str(port) + " to ovs " + str( ovsname ) )
                main.log.error( handle )
                return main.FALSE
            else:
                main.log.info( "Add port " + str(port) + " to ovs " + str( ovsname )  + " sucess" )
                return main.TRUE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()

    def setHostportIp(self, ip, hostname="host1", hostport1="host1-eth0" ):
        command = "sudo ip netns exec " + str(hostname) +" ifconfig " + str(hostport1) + " " + str(ip)
        try:
            handle = self.execute(
                cmd=command,
                timeout=10)
            if re.search( "Error", handle ):
                main.log.error( "Error in set host ip for " + str( hostport1 ) + " on host " + str( hostname ) )
                main.log.error( handle )
                return main.FALSE
            else:
                main.log.info( "Set host ip for " + str( hostport1 ) + " on host " + str( hostname ) + " sucess" )
                return main.TRUE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()

    def hostPing(self, src, target, hostname="host1" ):
        if src:
            command = "sudo ip netns exec " + str( hostname ) +" ping -c 1 -S " +\
             str( src ) + " " + str( target )
        else:
            command = "sudo ip netns exec " + str( hostname ) +" ping -c 1 " + str( target )
        try:
            for i in range(1,5):
                handle = self.execute(
                    cmd=command,
                    timeout=10)
                if re.search(',\s0\%\spacket\sloss', handle):
                    main.log.info(self.name + ": no packets lost, host is reachable")
                    return main.TRUE
                    break
                time.sleep(5)
            else:
                main.log.info(self.name + ": packets lost, host is unreachable")
                return main.FALSE
        except pexpect.EOF:
            main.log.error(self.name + ": EOF exception found")
            main.log.error(self.name + ":     " + self.handle.before)
            main.cleanup()
            main.exit()

    def delBr( self, sw ):
        """
        Parameters:
            sw: The name of an OVS switch. Example "br-int"
        Return:
            Delete sucess return main.TRUE or main.FALSE on delete failed
        """
        command= "sudo ovs-vsctl del-br " + str( sw )
        try:
            response = self.execute(
                cmd=command,
                timeout=10 )
            if response:
                return main.TRUE
            else:
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()

    def delHost( self, hostname ):
        """
        Parameters:
            hostname: The name of an ip netns name. Example "host1"
        Return:
            Delete sucess return main.TRUE or main.FALSE on delete failed
        """
        command= "sudo ip netns delete " + str( hostname )
        try:
            response = self.execute(
                cmd=command,
                timeout=10 )
            if response:
                return main.TRUE
            else:
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanup()
            main.exit()