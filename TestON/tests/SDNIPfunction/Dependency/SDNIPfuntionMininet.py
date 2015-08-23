#!/usr/bin/python

"""
Set up the SDN-IP function test topology
"""

"""
AS1 = 64513, (SDN AS)
AS2 = 64514, reachable by 192.168.10.1, 192.168.20.1
AS3 = 64516, reachable by 192.168.30.1
AS4 = 64517, reachable by 192.168.40.1
AS6 = 64520, reachable by 192.168.60.2, (route server 192.168.60.1)
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


class SDNTopo( Topo ):
    "SDN Topology"

    def __init__( self, *args, **kwargs ):
        global numHost101
        global numHost200
        numHost101 = 101
        numHost200 = 200
        Topo.__init__( self, *args, **kwargs )
        sw1 = self.addSwitch( 'sw1', dpid = '00000000000000a1' )
        sw2 = self.addSwitch( 'sw2', dpid = '00000000000000a2' )
        sw3 = self.addSwitch( 'sw3', dpid = '00000000000000a3' )
        sw4 = self.addSwitch( 'sw4', dpid = '00000000000000a4' )
        sw5 = self.addSwitch( 'sw5', dpid = '00000000000000a5' )
        sw6 = self.addSwitch( 'sw6', dpid = '00000000000000a6' )
        # add a switch for 100 quagga hosts
        sw100 = self.addSwitch( 'sw100', dpid = '0000000000000100' )
        swTestOn = self.addSwitch( 'swTestOn', dpid = '0000000000000102' )
        # Note this switch isn't part of the SDN topology
        # We'll use the ovs-controller to turn this into a learning switch
        as6sw = self.addSwitch( 'as6sw', dpid = '00000000000000a7' )

        host1 = self.addHost( 'host1' )
        host2 = self.addHost( 'host2' )
        root1 = self.addHost( 'root1', inNamespace = False , ip = '0' )
        root2 = self.addHost( 'root2', inNamespace = False, ip = '0' )
        rootTestOn = self.addHost( 'rootTestOn', inNamespace = False, ip = '0' )

        # AS2 host
        host3 = self.addHost( 'host3' )
        as2host = self.addHost( 'as2host' )
        # AS3 host
        host4 = self.addHost( 'host4' )
        as3host = self.addHost( 'as3host' )
        # AS4 host
        for i in range( numHost101, numHost200 + 1 ):
            self.addHost( 'host%s' % ( i ) )

        as4host = self.addHost( 'as4host' )
        for i in range( numHost101, numHost200 + 1 ):
            self.addHost( 'as4host%s' % ( i ) )
        # AS6 host
        as6rs = self.addHost( 'as6rs' )
        host5 = self.addHost( 'host5' )
        as6host = self.addHost( 'as6host' )

        self.addLink( host1, sw1 )
        self.addLink( host2, sw1 )
        # Links to the multihomed AS
        self.addLink( host3, sw3 )
        self.addLink( host3, sw5 )
        self.addLink( as2host, host3 )
        # Single links to the remaining two ASes
        self.addLink( host4, sw2 )
        self.addLink( sw100, sw6 )
        self.addLink( as3host, host4 )
        for i in range( numHost101, numHost200 + 1 ):
            self.addLink( 'host%s' % ( i ), sw100 )
        for i in range( numHost101, numHost200 + 1 ):
            self.addLink( 'host%s' % ( i ), 'as4host%s' % ( i ) )

        # AS3-AS4 link
        # self.addLink( host4, host5)
        # Add new AS6 to its bridge
        self.addLink( as6rs, as6sw )
        self.addLink( host5, as6sw )
        self.addLink( as6host, host5 )
        # test the host behind the router(behind the router server)
        '''
        for i in range(1, 10):
            host = self.addHost('as6host%d' % i)
            self.addLink(host, as6router)
        '''
        # Internal Connection To Hosts
        self.addLink( root1, host1 )
        self.addLink( root2, host2 )

        self.addLink( sw1, sw2 )
        self.addLink( sw1, sw3 )
        self.addLink( sw2, sw4 )
        self.addLink( sw3, sw4 )
        self.addLink( sw3, sw5 )
        self.addLink( sw4, sw6 )
        self.addLink( sw5, sw6 )
        self.addLink( as6sw, sw4 )

        self.addLink( swTestOn, rootTestOn )
        self.addLink( swTestOn, host3 )
        self.addLink( swTestOn, host4 )
        self.addLink( swTestOn, host5 )
        self.addLink( swTestOn, as2host )

        for i in range( numHost101, numHost200 + 1 ):
            self.addLink( swTestOn, 'host' + str( i ) )

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
    net = Mininet( topo = topo, controller = RemoteController )

    host1, host2, host3, host4, host5 = \
    net.get( 'host1', 'host2' , 'host3', 'host4', 'host5' )

    # Adding 2nd, 3rd and 4th interface to host1 connected to sw1
    # for another BGP peering
    host1.setMAC( '00:00:00:00:00:01', 'host1-eth0' )
    host1.cmd( 'ip addr add 192.168.20.101/24 dev host1-eth0' )
    host1.cmd( 'ip addr add 192.168.30.101/24 dev host1-eth0' )
    host1.cmd( 'ip addr add 192.168.40.101/24 dev host1-eth0' )
    host1.cmd( 'ip addr add 192.168.60.101/24 dev host1-eth0' )

    # Net has to be start after adding the above link
    net.start()
    for i in range( numHost101, numHost200 + 1 ):
        host100 = net.get( 'host%s' % ( i ) )
        host100.cmd( 'ifconfig host%s-eth0 192.168.40.%s up' % ( i, i - 100 ) )
        host100.setIP( str( i ) + ".0.0.254", 8, str( host100 ) + "-eth1" )
        host100.setMAC( '00:00:' + str( i - 101 ) + ':00:00:90', 'host'
                        + str( i ) + '-eth0' )
        host100.cmd( 'sysctl net.ipv4.conf.all.forwarding=1' )

    # Set up as6sw as a learning switch as quickly as possible so it
    # hopefully doesn't connect to the actual controller
    # TODO figure out how to change controller before starting switch
    as6sw = net.get( 'as6sw' )
    as6sw.cmd( 'ovs-vsctl set-controller as6sw none' )
    as6sw.cmd( 'ovs-vsctl set-fail-mode as6sw standalone' )


    sw1, sw2, sw3, sw4, sw5, sw6 = \
    net.get( 'sw1', 'sw2', 'sw3', 'sw4', 'sw5', 'sw6' )
    sw1.cmd( 'ovs-vsctl set-controller sw1 tcp:10.128.4.52:6653' )
    sw2.cmd( 'ovs-vsctl set-controller sw2 tcp:10.128.4.52:6653' )
    sw3.cmd( 'ovs-vsctl set-controller sw3 tcp:10.128.4.52:6653' )
    sw4.cmd( 'ovs-vsctl set-controller sw4 tcp:10.128.4.52:6653' )
    sw5.cmd( 'ovs-vsctl set-controller sw5 tcp:10.128.4.52:6653' )
    sw6.cmd( 'ovs-vsctl set-controller sw6 tcp:10.128.4.52:6653' )


    # Set up sw100 as a learning
    sw100 = net.get( 'sw100' )
    sw100.cmd( 'ovs-vsctl set-controller sw100 none' )
    sw100.cmd( 'ovs-vsctl set-fail-mode sw100 standalone' )

    swTestOn = net.get( 'swTestOn' )
    swTestOn.cmd( 'ovs-vsctl set-controller swTestOn none' )
    swTestOn.cmd( 'ovs-vsctl set-fail-mode swTestOn standalone' )

    host1.defaultIntf().setIP( '192.168.10.101/24' )

    # Configure new host interfaces
    host2.defaultIntf().setIP( '172.16.10.2/24' )
    host2.defaultIntf().setMAC( '00:00:00:00:01:02' )

    # Set up AS2
    host3.setIP( '192.168.10.1', 24, 'host3-eth0' )
    host3.setIP( '192.168.20.1', 24, 'host3-eth1' )
    host3.setMAC( '00:00:00:00:02:01', 'host3-eth0' )
    host3.setMAC( '00:00:00:00:02:02', 'host3-eth1' )
    host3.setIP( '3.0.0.254', 8, 'host3-eth2' )
    host3.cmd( 'sysctl net.ipv4.conf.all.forwarding=1' )

    host3.setIP( '1.168.30.2', 24, 'host3-eth3' )
    host3.cmd( 'sysctl net.ipv4.conf.all.arp_ignore=1' )
    host3.cmd( 'sysctl net.ipv4.conf.all.arp_announce=1' )
    as2host = net.get( 'as2host' )

    for i in range( 0, 20 ):
        as2host.cmd( 'sudo ip addr add 3.0.%d.1/24 dev as2host-eth0' % i )
    as2host.setIP( '1.168.30.100', 24, 'as2host-eth1' )

    as2host.cmd( 'ip route add default via 3.0.0.254' )

    # Set up AS3
    host4.setIP( '192.168.30.1', 24, 'host4-eth0' )
    host4.setMAC( '00:00:00:00:03:01', 'host4-eth0' )
    host4.setIP( '4.0.0.254', 8, 'host4-eth1' )
    host4.setMAC( '00:00:00:00:03:99', 'host4-eth1' )
    host4.cmd( 'sysctl net.ipv4.conf.all.forwarding=1' )
    as3host = net.get( 'as3host' )
    for i in range( 0, 20 ):
        as3host.cmd( 'sudo ip addr add 4.0.%d.1/24 dev as3host-eth0' % i )
    as3host.cmd( 'ip route add default via 4.0.0.254' )

    # root space
    host4.setIP( '1.168.30.3', 24, 'host4-eth2' )
    host4.setMAC( '00:00:00:00:03:03', 'host4-eth2' )

    # setup interface address for 100 quagga hosts
    time.sleep( 10 )
    for i in range( numHost101, numHost200 + 1 ):
        as4host100 = net.get( 'as4host%s' % ( i ) )
        as4host100.defaultIntf().setIP( str( i ) + '.0.0.1/24' )
        as4host100.cmd( 'ip route add default via ' + str( i ) + '.0.0.254' )
        for j in range( 0, 100 ):
            as4host100.cmd( 'sudo ip addr add %d.0.%d.1/24 dev %s-eth0' \
                           % ( i, j, as4host100 ) )

    # Set up AS6 - This has a router and a route server
    as6rs, host5 = net.get( 'as6rs', 'host5' )
    as6rs.setIP( '192.168.60.1', 24, 'as6rs-eth0' )
    as6rs.setMAC( '00:00:00:00:06:01', 'as6rs-eth0' )
    host5.setIP( '192.168.60.2', 24, 'host5-eth0' )
    host5.setMAC( '00:00:00:00:06:02', 'host5-eth0' )
    host5.setIP( '5.0.0.254', 8, 'host5-eth1' )
    host5.cmd( 'sysctl net.ipv4.conf.all.forwarding=1' )
    host5.setIP( '1.168.30.5', 24, 'host5-eth2' )
    host5.setMAC( '00:00:00:00:06:05', 'host5-eth2' )

    as6host = net.get( 'as6host' )
    as6host.defaultIntf().setIP( '5.0.0.1/24' )
    as6host.cmd( 'ip route add default via 5.0.0.254' )
    for i in range( 0, 10 ):
        as6host.cmd( 'sudo ip addr add 5.0.%d.1/24 dev as6host-eth0' % i )

    # test the host in the as6
    '''
    for i in range(1, 10):
        baseip = (i-1)*4
        host = net.get('as6host%d' % i)
        host.defaultIntf().setIP('172.16.70.%d/24' % (baseip+1))
        host.cmd('ip route add default via 172.16.70.%d' % (baseip+2))
        as6router.setIP('172.16.70.%d' % (baseip+2), 30, 'as6router-eth%d' % (i+1))
    '''

    # Start Quagga on border routers
    startquagga( host3, 1, 'quagga1.conf' )
    startquagga( host4, 2, 'quagga2.conf' )
    for i in range( numHost101, numHost200 + 1 ):
        host100 = net.get( 'host%d' % ( i ) )
        startquaggahost5( host100, i )

    startquagga( as6rs, 4, 'quagga-as6-rs.conf' )
    startquagga( host5, 5, 'quagga-as6.conf' )

    root1, root2, rootTestOn = net.get( 'root1', 'root2', 'rootTestOn' )
    host1.intf( 'host1-eth1' ).setIP( '1.1.1.1/24' )
    root1.intf( 'root1-eth0' ).setIP( '1.1.1.2/24' )
    host2.intf( 'host2-eth1' ).setIP( '1.1.2.1/24' )
    root2.intf( 'root2-eth0' ).setIP( '1.1.2.2/24' )

    rootTestOn.cmd( 'ip addr add 1.168.30.99/24 dev rootTestOn-eth0' )

    stopsshd()
    for i in range( numHost101, numHost200 + 1 ):
        hostX = net.get( 'host%s' % ( i ) )
        hostX.setIP( '1.168.30.' + str( i ), 24, str( "host" ) + str( i )
                     + "-eth2" )
        startsshd( hostX )

    startquagga( host1, 100, 'quagga-sdn.conf' )
    hosts = [ host1, host2, host3, host4, host5, as2host ];
    startsshds( hosts )
    #
    onos1 = '10.128.4.52'
    forwarding1 = '%s:2000:%s:2000' % ( '1.1.1.2', onos1 )
    root1.cmd( 'ssh -nNT -o "PasswordAuthentication no" \
    -o "StrictHostKeyChecking no" -l sdn -L %s %s & ' % ( forwarding1, onos1 ) )

    # Forward 2605 to root namespace for easier access to SDN domain BGPd
    # If root can ssh to itself without a password this should work
    '''
    root1.cmd('ssh -N -o "PasswordAuthentication no" \
    -o "StrictHostKeyChecking no" -L 2605:1.1.1.1:2605 1.1.1.1 &')
    '''
    # time.sleep( 3000000000 )
    CLI( net )

    # Close the ssh port forwarding
    # quietRun('sudo pkill -f 1.1.1.1')

    stopsshd()
    stopquagga()
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'debug' )
    sdn1net()
