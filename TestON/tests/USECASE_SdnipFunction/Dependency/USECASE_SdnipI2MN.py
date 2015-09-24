#!/usr/bin/python

"""
Set up the SDN-IP topology as same as it on Internet2
"""

"""
AS 64513, (SDN AS)
AS 64514, reachable by 10.0.4.1
AS 64515, reachable by 10.0.5.1
AS 64516, reachable by 10.0.6.1
"""

from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.util import quietRun
from mininet.moduledeps import pathCheck

import os.path
import time
from subprocess import Popen, STDOUT, PIPE

QUAGGA_DIR = '/usr/lib/quagga'
QUAGGA_RUN_DIR = '/usr/local/var/run/quagga'
QUAGGA_CONFIG_DIR = '~/OnosSystemTest/TestON/tests/USECASE_SdnipFunction/Dependency/'
# onos1IP = '10.254.1.201'
numSw = 39


class SDNTopo( Topo ):
    "SDN Topology"

    def __init__( self, *args, **kwargs ):

        Topo.__init__( self, *args, **kwargs )

        # BGP peer hosts
        peer64514 = self.addHost( 'peer64514' )
        peer64515 = self.addHost( 'peer64515' )
        peer64516 = self.addHost( 'peer64516' )

        '''
        sw1 = self.addSwitch( 'SEAT', dpid = '00000000000000a1' )
        sw2 = self.addSwitch( 'PORT', dpid = '00000000000000a2' )
        sw3 = self.addSwitch( 'SUNN', dpid = '00000000000000a3' )
        sw4 = self.addSwitch( 'RENO', dpid = '00000000000000a4' )
        sw5 = self.addSwitch( 'LOSA', dpid = '00000000000000a5' )
        sw6 = self.addSwitch( 'MISS', dpid = '00000000000000a6' )
        sw7 = self.addSwitch( 'LASV', dpid = '00000000000000a7' )
        sw8 = self.addSwitch( 'SALT', dpid = '00000000000000a8' )
        sw9 = self.addSwitch( 'PHOE', dpid = '00000000000000a9' )
        sw10 = self.addSwitch( 'TUCS', dpid = '0000000000000a10' )
        sw11 = self.addSwitch( 'DENV', dpid = '0000000000000a11' )
        sw12 = self.addSwitch( 'ELPA', dpid = '0000000000000a12' )
        sw13 = self.addSwitch( 'MINN', dpid = '0000000000000a13' )
        sw14 = self.addSwitch( 'KANS', dpid = '0000000000000a14' )
        sw15 = self.addSwitch( 'TULS', dpid = '0000000000000a15' )
        sw16 = self.addSwitch( 'DALL', dpid = '0000000000000a16' )
        sw17 = self.addSwitch( 'HOUH', dpid = '0000000000000a17' )
        sw18 = self.addSwitch( 'COLU', dpid = '0000000000000a18' )
        sw19 = self.addSwitch( 'JCSN', dpid = '0000000000000a19' )
        sw20 = self.addSwitch( 'BATO', dpid = '0000000000000a20' )
        sw21 = self.addSwitch( 'EQCH', dpid = '0000000000000a21' )
        sw22 = self.addSwitch( 'STAR', dpid = '0000000000000a22' )
        sw23 = self.addSwitch( 'CHIC', dpid = '0000000000000a23' )
        sw24 = self.addSwitch( 'INDI', dpid = '0000000000000a24' )
        sw25 = self.addSwitch( 'CINC', dpid = '0000000000000a25' )
        sw26 = self.addSwitch( 'LOUI', dpid = '0000000000000a26' )
        sw27 = self.addSwitch( 'ATLA', dpid = '0000000000000a27' )
        sw28 = self.addSwitch( 'JACK', dpid = '0000000000000a28' )
        sw29 = self.addSwitch( 'CLEV', dpid = '0000000000000a29' )
        sw30 = self.addSwitch( 'PITT', dpid = '0000000000000a30' )
        sw31 = self.addSwitch( 'ASHB', dpid = '0000000000000a31' )
        sw32 = self.addSwitch( 'WASH', dpid = '0000000000000a32' )
        sw33 = self.addSwitch( 'RALE', dpid = '0000000000000a33' )
        sw34 = self.addSwitch( 'CHAR', dpid = '0000000000000a34' )
        sw35 = self.addSwitch( 'ALBA', dpid = '0000000000000a35' )
        sw36 = self.addSwitch( 'BOST', dpid = '0000000000000a36' )
        sw37 = self.addSwitch( 'HART', dpid = '0000000000000a37' )
        sw38 = self.addSwitch( 'NEWY', dpid = '0000000000000a38' )
        sw39 = self.addSwitch( 'PHIL', dpid = '0000000000000a39' )
        '''
        sw1 = self.addSwitch( 'sw1', dpid = '00000000000000a1' )
        sw2 = self.addSwitch( 'sw2', dpid = '00000000000000a2' )
        sw3 = self.addSwitch( 'sw3', dpid = '00000000000000a3' )
        sw4 = self.addSwitch( 'sw4', dpid = '00000000000000a4' )
        sw5 = self.addSwitch( 'sw5', dpid = '00000000000000a5' )
        sw6 = self.addSwitch( 'sw6', dpid = '00000000000000a6' )
        sw7 = self.addSwitch( 'sw7', dpid = '00000000000000a7' )
        sw8 = self.addSwitch( 'sw8', dpid = '00000000000000a8' )
        sw9 = self.addSwitch( 'sw9', dpid = '00000000000000a9' )
        sw10 = self.addSwitch( 'sw10', dpid = '0000000000000a10' )
        sw11 = self.addSwitch( 'sw11', dpid = '0000000000000a11' )
        sw12 = self.addSwitch( 'sw12', dpid = '0000000000000a12' )
        sw13 = self.addSwitch( 'sw13', dpid = '0000000000000a13' )
        sw14 = self.addSwitch( 'sw14', dpid = '0000000000000a14' )
        sw15 = self.addSwitch( 'sw15', dpid = '0000000000000a15' )
        sw16 = self.addSwitch( 'sw16', dpid = '0000000000000a16' )
        sw17 = self.addSwitch( 'sw17', dpid = '0000000000000a17' )
        sw18 = self.addSwitch( 'sw18', dpid = '0000000000000a18' )
        sw19 = self.addSwitch( 'sw19', dpid = '0000000000000a19' )
        sw20 = self.addSwitch( 'sw20', dpid = '0000000000000a20' )
        sw21 = self.addSwitch( 'sw21', dpid = '0000000000000a21' )
        sw22 = self.addSwitch( 'sw22', dpid = '0000000000000a22' )
        sw23 = self.addSwitch( 'sw23', dpid = '0000000000000a23' )
        sw24 = self.addSwitch( 'sw24', dpid = '0000000000000a24' )
        sw25 = self.addSwitch( 'sw25', dpid = '0000000000000a25' )
        sw26 = self.addSwitch( 'sw26', dpid = '0000000000000a26' )
        sw27 = self.addSwitch( 'sw27', dpid = '0000000000000a27' )
        sw28 = self.addSwitch( 'sw28', dpid = '0000000000000a28' )
        sw29 = self.addSwitch( 'sw29', dpid = '0000000000000a29' )
        sw30 = self.addSwitch( 'sw30', dpid = '0000000000000a30' )
        sw31 = self.addSwitch( 'sw31', dpid = '0000000000000a31' )
        sw32 = self.addSwitch( 'sw32', dpid = '0000000000000a32' )
        sw33 = self.addSwitch( 'sw33', dpid = '0000000000000a33' )
        sw34 = self.addSwitch( 'sw34', dpid = '0000000000000a34' )
        sw35 = self.addSwitch( 'sw35', dpid = '0000000000000a35' )
        sw36 = self.addSwitch( 'sw36', dpid = '0000000000000a36' )
        sw37 = self.addSwitch( 'sw37', dpid = '0000000000000a37' )
        sw38 = self.addSwitch( 'sw38', dpid = '0000000000000a38' )
        sw39 = self.addSwitch( 'sw39', dpid = '0000000000000a39' )


        # Add a layer2 switch for control plane connectivity
        # This switch isn't part of the SDN topology
        # We'll use the ovs-controller to turn this into a learning switch
        swCtl100 = self.addSwitch( 'swCtl100', dpid = '0000000000000100' )


        # BGP speaker hosts
        speaker1 = self.addHost( 'speaker1' )
        speaker2 = self.addHost( 'speaker2' )

        root = self.addHost( 'root', inNamespace = False , ip = '0' )

        # hosts behind each AS
        host64514 = self.addHost( 'host64514' )
        host64515 = self.addHost( 'host64515' )
        host64516 = self.addHost( 'host64516' )

        self.addLink( 'speaker1', sw24 )
        self.addLink( 'speaker2', sw24 )

        # connect all switches
        self.addLink( sw1, sw2 )
        self.addLink( sw1, sw6 )
        self.addLink( sw1, sw8 )
        self.addLink( sw2, sw3 )
        self.addLink( sw3, sw4 )
        self.addLink( sw3, sw5 )
        self.addLink( sw4, sw8 )
        self.addLink( sw5, sw7 )
        self.addLink( sw5, sw9 )
        self.addLink( sw6, sw13 )
        self.addLink( sw7, sw8 )
        self.addLink( sw8, sw11 )
        self.addLink( sw9, sw10 )
        self.addLink( sw10, sw12 )
        self.addLink( sw11, sw12 )
        self.addLink( sw11, sw14 )
        self.addLink( sw12, sw17 )
        self.addLink( sw13, sw14 )
        self.addLink( sw13, sw21 )
        self.addLink( sw14, sw15 )
        self.addLink( sw14, sw18 )
        self.addLink( sw14, sw23 )
        self.addLink( sw15, sw16 )
        self.addLink( sw16, sw17 )
        self.addLink( sw17, sw19 )
        self.addLink( sw17, sw20 )
        self.addLink( sw18, sw23 )
        self.addLink( sw19, sw27 )
        self.addLink( sw20, sw28 )
        self.addLink( sw21, sw22 )
        self.addLink( sw21, sw29 )
        self.addLink( sw22, sw23 )
        self.addLink( sw23, sw24 )
        self.addLink( sw23, sw31 )
        self.addLink( sw24, sw25 )
        self.addLink( sw25, sw26 )
        self.addLink( sw26, sw27 )
        self.addLink( sw27, sw28 )
        self.addLink( sw27, sw34 )
        self.addLink( sw29, sw30 )
        self.addLink( sw29, sw35 )
        self.addLink( sw30, sw31 )
        self.addLink( sw31, sw32 )
        self.addLink( sw32, sw33 )
        self.addLink( sw32, sw39 )
        self.addLink( sw33, sw34 )
        self.addLink( sw35, sw36 )
        self.addLink( sw36, sw37 )
        self.addLink( sw37, sw38 )
        self.addLink( sw38, sw39 )

        # connection between switches and peers
        self.addLink( peer64514, sw32 )
        self.addLink( peer64515, sw8 )
        self.addLink( peer64516, sw28 )

        # connection between BGP peer and hosts behind the BGP peer
        self.addLink( peer64514, host64514 )
        self.addLink( peer64515, host64515 )
        self.addLink( peer64516, host64516 )

        # Internal Connection To Hosts
        self.addLink( swCtl100, peer64514 )
        self.addLink( swCtl100, peer64515 )
        self.addLink( swCtl100, peer64516 )
        self.addLink( swCtl100, speaker1 )
        self.addLink( swCtl100, speaker2 )



        # add host64514 to control plane for ping test
        self.addLink( swCtl100, host64514 )
        self.addLink( swCtl100, root )


def startsshd( host ):
    "Start sshd on host"
    info( '*** Starting sshd\n' )
    name, intf, ip = host.name, host.defaultIntf(), host.IP()
    banner = '/tmp/%s.banner' % name
    host.cmd( 'echo "Welcome to %s at %s" >  %s' % ( name, ip, banner ) )
    host.cmd( '/usr/sbin/sshd -o "Banner %s"' % banner, '-o "UseDNS no"' )
    info( '***', host.name, 'is running sshd on', intf, 'at', ip, '\n' )

def startsshds ( hosts ):
    for h in hosts:
        startsshd( h )

def stopsshd():
    "Stop *all* sshd processes with a custom banner"
    info( '*** Shutting down stale sshd/Banner processes ',
          quietRun( "pkill -9 -f Banner" ), '\n' )

def startquagga( host, num, config_file ):
    info( '*** Starting Quagga on %s\n' % host )
    host.cmd( "cd %s" % QUAGGA_CONFIG_DIR )
    zebra_cmd = \
    '%s/zebra -d -f  ./zebra.conf -z %s/zserv%s.api -i %s/zebra%s.pid'\
     % ( QUAGGA_DIR, QUAGGA_RUN_DIR, num, QUAGGA_RUN_DIR, num )
    quagga_cmd = '%s/bgpd -d -f %s -z %s/zserv%s.api -i %s/bgpd%s.pid' \
    % ( QUAGGA_DIR, config_file, QUAGGA_RUN_DIR, num, QUAGGA_RUN_DIR, num )

    print zebra_cmd
    print quagga_cmd

    host.cmd( zebra_cmd )
    host.cmd( quagga_cmd )

def startquaggahost5( host, num ):
    info( '*** Starting Quagga on %s\n' % host )
    zebra_cmd = \
    '%s/zebra -d -f  ./zebra.conf -z %s/zserv%s.api -i %s/zebra%s.pid' \
    % ( QUAGGA_DIR, QUAGGA_RUN_DIR, num, QUAGGA_RUN_DIR, num )
    quagga_cmd = \
    '%s/bgpd -d -f ./as4quaggas/quagga%s.conf -z %s/zserv%s.api -i %s/bgpd%s.pid'\
     % ( QUAGGA_DIR, num, QUAGGA_RUN_DIR, num, QUAGGA_RUN_DIR, num )

    host.cmd( zebra_cmd )
    host.cmd( quagga_cmd )


def stopquagga():
    quietRun( 'sudo pkill -9 -f bgpd' )
    quietRun( 'sudo pkill -9 -f zebra' )

def sdn1net():
    topo = SDNTopo()
    info( '*** Creating network\n' )
   # time.sleep( 30 )
    net = Mininet( topo = topo, controller = RemoteController )


    speaker1, speaker2, peer64514, peer64515, peer64516 = \
    net.get( 'speaker1', 'speaker2' ,
             'peer64514', 'peer64515', 'peer64516' )

    # Adding addresses to host64513_1 interface connected to sw24
    # for BGP peering
    speaker1.setMAC( '00:00:00:00:00:01', 'speaker1-eth0' )
    speaker1.cmd( 'ip addr add 10.0.4.101/24 dev speaker1-eth0' )
    speaker1.cmd( 'ip addr add 10.0.5.101/24 dev speaker1-eth0' )
    speaker1.cmd( 'ip addr add 10.0.6.101/24 dev speaker1-eth0' )

    speaker1.defaultIntf().setIP( '10.1.4.101/24' )
    speaker1.defaultIntf().setMAC( '00:00:00:00:00:01' )

    # Net has to be start after adding the above link
    net.start()

    # setup configuration on the interface connected to switch
    peer64514.cmd( "ifconfig  peer64514-eth0 10.0.4.1 up" )
    peer64514.setMAC( '00:00:00:00:00:04', 'peer64514-eth0' )
    peer64515.cmd( "ifconfig  peer64515-eth0 10.0.5.1 up" )
    peer64515.setMAC( '00:00:00:00:00:05', 'peer64515-eth0' )
    peer64516.cmd( "ifconfig  peer64516-eth0 10.0.6.1 up" )
    peer64516.setMAC( '00:00:00:00:00:06', 'peer64516-eth0' )

    # setup configuration on the interface connected to hosts
    peer64514.setIP( "4.0.0.254", 8, "peer64514-eth1" )
    peer64514.setMAC( '00:00:00:00:00:44', 'peer64514-eth1' )
    peer64515.setIP( "5.0.0.254", 8, "peer64515-eth1" )
    peer64515.setMAC( '00:00:00:00:00:55', 'peer64515-eth1' )
    peer64516.setIP( "6.0.0.254", 8, "peer64516-eth1" )
    peer64516.setMAC( '00:00:00:00:00:66', 'peer64516-eth1' )

    # enable forwarding on BGP peer hosts
    peer64514.cmd( 'sysctl net.ipv4.conf.all.forwarding=1' )
    peer64515.cmd( 'sysctl net.ipv4.conf.all.forwarding=1' )
    peer64516.cmd( 'sysctl net.ipv4.conf.all.forwarding=1' )

    # config interface for control plane connectivity
    peer64514.setIP( "192.168.0.4", 24, "peer64514-eth2" )
    peer64515.setIP( "192.168.0.5", 24, "peer64515-eth2" )
    peer64516.setIP( "192.168.0.6", 24, "peer64516-eth2" )

    # Setup hosts in each non-SDN AS
    host64514, host64515, host64516 = \
    net.get( 'host64514', 'host64515', 'host64516' )
    host64514.cmd( 'ifconfig host64514-eth0 4.0.0.1 up' )
    host64514.cmd( 'ip route add default via 4.0.0.254' )
    host64514.setIP( '192.168.0.44', 24, 'host64514-eth1' )  # for control plane
    host64515.cmd( 'ifconfig host64515-eth0 5.0.0.1 up' )
    host64515.cmd( 'ip route add default via 5.0.0.254' )
    host64516.cmd( 'ifconfig host64516-eth0 6.0.0.1 up' )
    host64516.cmd( 'ip route add default via 6.0.0.254' )


    # set up swCtl100 as a learning
    swCtl100 = net.get( 'swCtl100' )
    swCtl100.cmd( 'ovs-vsctl set-controller swCtl100 none' )
    swCtl100.cmd( 'ovs-vsctl set-fail-mode swCtl100 standalone' )

    # connect all switches to controller
    '''
    for i in range ( 1, numSw + 1 ):
        swX = net.get( 'sw%s' % ( i ) )
        swX.cmd( 'ovs-vsctl set-controller sw%s tcp:%s:6653' % ( i, onos1IP ) )
    '''
    # Start Quagga on border routers
    '''
    for i in range ( 64514, 64516 + 1 ):
        startquagga( 'peer%s' % ( i ), i, 'quagga%s.conf' % ( i ) )
    '''
    startquagga( peer64514, 64514, 'quagga64514.conf' )
    startquagga( peer64515, 64515, 'quagga64515.conf' )
    startquagga( peer64516, 64516, 'quagga64516.conf' )

    # start Quagga in SDN network
    startquagga( speaker1, 64513, 'quagga-sdn.conf' )


    root = net.get( 'root' )
    root.intf( 'root-eth0' ).setIP( '1.1.1.2/24' )
    root.cmd( 'ip addr add 192.168.0.100/24 dev root-eth0' )

    speaker1.intf( 'speaker1-eth1' ).setIP( '1.1.1.1/24' )


    stopsshd()

    hosts = [ peer64514, peer64515, peer64516, host64514];
    startsshds( hosts )
    #
    '''
    forwarding1 = '%s:2000:%s:2000' % ( '1.1.1.2', onos1IP )
    root.cmd( 'ssh -nNT -o "PasswordAuthentication no" \
    -o "StrictHostKeyChecking no" -l sdn -L %s %s & ' % ( forwarding1, onos1IP ) )

    '''
    # time.sleep( 3000000000 )
    CLI( net )


    stopsshd()
    stopquagga()
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'debug' )
    sdn1net()
