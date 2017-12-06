#!/usr/bin/python

"""
Copyright 2015 Open Networking Foundation ( ONF )

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
"""
Set up the SDN-IP topology as same as it on Internet2
"""
"""
AS 64513, ( SDN AS )
AS 64514, reachable by 10.0.4.1
AS 64515, reachable by 10.0.5.1
AS 64516, reachable by 10.0.6.1
"""
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.node import Host, RemoteController
from mininet.topo import Topo
from mininet.util import quietRun

QUAGGA_DIR = '/usr/lib/quagga'
QUAGGA_RUN_DIR = '/usr/local/var/run/quagga'
QUAGGA_CONFIG_DIR = '~/OnosSystemTest/TestON/tests/USECASE/USECASE_SdnipFunction/dependencies/'
numSw = 39


class VLANHost( Host ):

    def config( self, vlan=100, intfName=None, **params ):
        r = super( Host, self ).config( **params )
        intf = self.intf( intfName )
        self.cmd( 'ifconfig %s inet 0' % intf )
        self.cmd( 'vconfig add %s %d' % ( intf, vlan ) )
        self.cmd( 'ifconfig %s.%d inet %s' % ( intf, vlan, params[ 'ip' ] ) )
        newName = '%s.%d' % ( intf, vlan )
        intf.name = newName
        self.nameToIntf[ newName ] = intf
        return r


class SDNTopo( Topo ):

    "SDN Topology"

    def __init__( self, *args, **kwargs ):

        Topo.__init__( self, *args, **kwargs )

        # BGP peer hosts
        p64514 = self.addHost( 'p64514' )
        p64515 = self.addHost( 'p64515' )
        p64516 = self.addHost( 'p64516' )

        p64517 = self.addHost( 'p64517', cls=VLANHost, vlan=20 )
        p64518 = self.addHost( 'p64518', cls=VLANHost, vlan=20 )
        p64519 = self.addHost( 'p64519', cls=VLANHost, vlan=10 )
        p64520 = self.addHost( 'p64520', cls=VLANHost, vlan=10 )

        """
        sw1 = self.addSwitch( 'SEAT', dpid='00000000000000a1' )
        sw2 = self.addSwitch( 'PORT', dpid='00000000000000a2' )
        sw3 = self.addSwitch( 'SUNN', dpid='00000000000000a3' )
        sw4 = self.addSwitch( 'RENO', dpid='00000000000000a4' )
        sw5 = self.addSwitch( 'LOSA', dpid='00000000000000a5' )
        sw6 = self.addSwitch( 'MISS', dpid='00000000000000a6' )
        sw7 = self.addSwitch( 'LASV', dpid='00000000000000a7' )
        sw8 = self.addSwitch( 'SALT', dpid='00000000000000a8' )
        sw9 = self.addSwitch( 'PHOE', dpid='00000000000000a9' )
        sw10 = self.addSwitch( 'TUCS', dpid='0000000000000a10' )
        sw11 = self.addSwitch( 'DENV', dpid='0000000000000a11' )
        sw12 = self.addSwitch( 'ELPA', dpid='0000000000000a12' )
        sw13 = self.addSwitch( 'MINN', dpid='0000000000000a13' )
        sw14 = self.addSwitch( 'KANS', dpid='0000000000000a14' )
        sw15 = self.addSwitch( 'TULS', dpid='0000000000000a15' )
        sw16 = self.addSwitch( 'DALL', dpid='0000000000000a16' )
        sw17 = self.addSwitch( 'HOUH', dpid='0000000000000a17' )
        sw18 = self.addSwitch( 'COLU', dpid='0000000000000a18' )
        sw19 = self.addSwitch( 'JCSN', dpid='0000000000000a19' )
        sw20 = self.addSwitch( 'BATO', dpid='0000000000000a20' )
        sw21 = self.addSwitch( 'EQCH', dpid='0000000000000a21' )
        sw22 = self.addSwitch( 'STAR', dpid='0000000000000a22' )
        sw23 = self.addSwitch( 'CHIC', dpid='0000000000000a23' )
        sw24 = self.addSwitch( 'INDI', dpid='0000000000000a24' )
        sw25 = self.addSwitch( 'CINC', dpid='0000000000000a25' )
        sw26 = self.addSwitch( 'LOUI', dpid='0000000000000a26' )
        sw27 = self.addSwitch( 'ATLA', dpid='0000000000000a27' )
        sw28 = self.addSwitch( 'JACK', dpid='0000000000000a28' )
        sw29 = self.addSwitch( 'CLEV', dpid='0000000000000a29' )
        sw30 = self.addSwitch( 'PITT', dpid='0000000000000a30' )
        sw31 = self.addSwitch( 'ASHB', dpid='0000000000000a31' )
        sw32 = self.addSwitch( 'WASH', dpid='0000000000000a32' )
        sw33 = self.addSwitch( 'RALE', dpid='0000000000000a33' )
        sw34 = self.addSwitch( 'CHAR', dpid='0000000000000a34' )
        sw35 = self.addSwitch( 'ALBA', dpid='0000000000000a35' )
        sw36 = self.addSwitch( 'BOST', dpid='0000000000000a36' )
        sw37 = self.addSwitch( 'HART', dpid='0000000000000a37' )
        sw38 = self.addSwitch( 'NEWY', dpid='0000000000000a38' )
        sw39 = self.addSwitch( 'PHIL', dpid='0000000000000a39' )
        """
        sw1 = self.addSwitch( 'sw1', dpid='00000000000000a1' )
        sw2 = self.addSwitch( 'sw2', dpid='00000000000000a2' )
        sw3 = self.addSwitch( 'sw3', dpid='00000000000000a3' )
        sw4 = self.addSwitch( 'sw4', dpid='00000000000000a4' )
        sw5 = self.addSwitch( 'sw5', dpid='00000000000000a5' )
        sw6 = self.addSwitch( 'sw6', dpid='00000000000000a6' )
        sw7 = self.addSwitch( 'sw7', dpid='00000000000000a7' )
        sw8 = self.addSwitch( 'sw8', dpid='00000000000000a8' )
        sw9 = self.addSwitch( 'sw9', dpid='00000000000000a9' )
        sw10 = self.addSwitch( 'sw10', dpid='0000000000000a10' )
        sw11 = self.addSwitch( 'sw11', dpid='0000000000000a11' )
        sw12 = self.addSwitch( 'sw12', dpid='0000000000000a12' )
        sw13 = self.addSwitch( 'sw13', dpid='0000000000000a13' )
        sw14 = self.addSwitch( 'sw14', dpid='0000000000000a14' )
        sw15 = self.addSwitch( 'sw15', dpid='0000000000000a15' )
        sw16 = self.addSwitch( 'sw16', dpid='0000000000000a16' )
        sw17 = self.addSwitch( 'sw17', dpid='0000000000000a17' )
        sw18 = self.addSwitch( 'sw18', dpid='0000000000000a18' )
        sw19 = self.addSwitch( 'sw19', dpid='0000000000000a19' )
        sw20 = self.addSwitch( 'sw20', dpid='0000000000000a20' )
        sw21 = self.addSwitch( 'sw21', dpid='0000000000000a21' )
        sw22 = self.addSwitch( 'sw22', dpid='0000000000000a22' )
        sw23 = self.addSwitch( 'sw23', dpid='0000000000000a23' )
        sw24 = self.addSwitch( 'sw24', dpid='0000000000000a24' )
        sw25 = self.addSwitch( 'sw25', dpid='0000000000000a25' )
        sw26 = self.addSwitch( 'sw26', dpid='0000000000000a26' )
        sw27 = self.addSwitch( 'sw27', dpid='0000000000000a27' )
        sw28 = self.addSwitch( 'sw28', dpid='0000000000000a28' )
        sw29 = self.addSwitch( 'sw29', dpid='0000000000000a29' )
        sw30 = self.addSwitch( 'sw30', dpid='0000000000000a30' )
        sw31 = self.addSwitch( 'sw31', dpid='0000000000000a31' )
        sw32 = self.addSwitch( 'sw32', dpid='0000000000000a32' )
        sw33 = self.addSwitch( 'sw33', dpid='0000000000000a33' )
        sw34 = self.addSwitch( 'sw34', dpid='0000000000000a34' )
        sw35 = self.addSwitch( 'sw35', dpid='0000000000000a35' )
        sw36 = self.addSwitch( 'sw36', dpid='0000000000000a36' )
        sw37 = self.addSwitch( 'sw37', dpid='0000000000000a37' )
        sw38 = self.addSwitch( 'sw38', dpid='0000000000000a38' )
        sw39 = self.addSwitch( 'sw39', dpid='0000000000000a39' )

        # Add a layer2 switch for control plane connectivity
        # This switch isn't part of the SDN topology
        # We'll use the ovs-controller to turn this into a learning switch
        swCtl100 = self.addSwitch( 'swCtl100', dpid='0000000000000100' )

        # BGP speaker hosts
        spk1 = self.addHost( 'spk1' )
        spk2 = self.addHost( 'spk2', cls=VLANHost, vlan=20 )
        spk3 = self.addHost( 'spk3', cls=VLANHost, vlan=10 )

        root = self.addHost( 'root', inNamespace=False, ip='0' )

        # hosts behind each AS
        h64514 = self.addHost( 'h64514' )
        h64515 = self.addHost( 'h64515' )
        h64516 = self.addHost( 'h64516' )

        # VLAN hosts behind each AS
        h64517 = self.addHost( 'h64517', cls=VLANHost, vlan=20 )
        h64518 = self.addHost( 'h64518', cls=VLANHost, vlan=20 )
        h64519 = self.addHost( 'h64519', cls=VLANHost, vlan=10 )
        h64520 = self.addHost( 'h64520', cls=VLANHost, vlan=10 )

        self.addLink( 'spk1', sw24 )
        self.addLink( 'spk2', sw24 )
        self.addLink( 'spk3', sw24 )

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
        self.addLink( p64514, sw32 )
        self.addLink( p64515, sw8 )
        self.addLink( p64516, sw28 )

        self.addLink( p64517, sw7 )
        self.addLink( p64518, sw9 )
        self.addLink( p64519, sw5 )
        self.addLink( p64520, sw5 )  # should be sw5

        # connection between BGP peer and hosts behind the BGP peer
        self.addLink( p64514, h64514 )
        self.addLink( p64515, h64515 )
        self.addLink( p64516, h64516 )

        self.addLink( p64517, h64517 )
        self.addLink( p64518, h64518 )
        self.addLink( p64519, h64519 )
        self.addLink( p64520, h64520 )

        # Internal Connection To Hosts
        self.addLink( swCtl100, p64514 )
        self.addLink( swCtl100, p64515 )
        self.addLink( swCtl100, p64516 )

        self.addLink( swCtl100, p64517 )
        self.addLink( swCtl100, p64518 )
        self.addLink( swCtl100, p64519 )
        self.addLink( swCtl100, p64520 )

        self.addLink( swCtl100, spk1 )
        self.addLink( swCtl100, spk2 )
        self.addLink( swCtl100, spk3 )

        # add h64514 to control plane for ping test
        self.addLink( swCtl100, h64514 )
        self.addLink( swCtl100, h64517 )
        self.addLink( swCtl100, h64519 )
        self.addLink( swCtl100, root )


def startsshd( host ):
    "Start sshd on host"
    info( '*** Starting sshd\n' )
    name, intf, ip = host.name, host.defaultIntf(), host.IP()
    banner = '/tmp/%s.banner' % name
    host.cmd( 'echo "Welcome to %s at %s" >  %s' % ( name, ip, banner ) )
    host.cmd( '/usr/sbin/sshd -o "Banner %s"' % banner, '-o "UseDNS no"' )
    info( '***', host.name, 'is running sshd on', intf, 'at', ip, '\n' )


def startsshds( hosts ):
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
    net = Mininet( topo=topo, controller=RemoteController )

    spk1, spk2, spk3, p64514, p64515, p64516, p64517, p64518, p64519, p64520 = \
        net.get( 'spk1', 'spk2', 'spk3',
                 'p64514', 'p64515', 'p64516', 'p64517', 'p64518', 'p64519', 'p64520' )

    # Adding addresses to host64513_1 interface connected to sw24
    # for BGP peering
    spk1.setMAC( '00:00:00:00:00:01', 'spk1-eth0' )
    spk1.cmd( 'ip addr add 10.0.4.101/24 dev spk1-eth0' )
    spk1.cmd( 'ip addr add 10.0.5.101/24 dev spk1-eth0' )
    spk1.cmd( 'ip addr add 10.0.6.101/24 dev spk1-eth0' )
    spk1.defaultIntf().setIP( '10.1.4.101/24' )
    spk1.defaultIntf().setMAC( '00:00:00:00:00:01' )

    spk2.setMAC( '00:00:00:00:00:02', 'spk2-eth0.20' )
    spk2.cmd( 'ip addr add 10.0.7.101/24 dev spk2-eth0.20' )
    spk2.cmd( 'ip addr add 10.0.8.101/24 dev spk2-eth0.20' )
    spk2.defaultIntf().setIP( '10.1.7.101/24' )
    spk2.defaultIntf().setMAC( '00:00:00:00:00:02' )

    spk3.setMAC( '00:00:00:00:00:03', 'spk3-eth0.10' )
    spk3.cmd( 'ip addr add 10.0.9.101/24 dev spk3-eth0.10' )
    spk3.cmd( 'ip addr add 10.0.20.101/24 dev spk3-eth0.10' )
    spk3.defaultIntf().setIP( '10.1.9.101/24' )
    spk3.defaultIntf().setMAC( '00:00:00:00:00:03' )

    p64517.config( vlan=20, intfName="p64517-eth1", ip="7.0.0.254" )
    p64518.config( vlan=20, intfName="p64518-eth1", ip="8.0.0.254" )
    p64519.config( vlan=10, intfName="p64519-eth1", ip="9.0.0.254" )
    p64520.config( vlan=10, intfName="p64520-eth1", ip="20.0.0.254" )

    # Net has to be start after adding the above link
    net.start()

    # setup configuration on the interface connected to switch
    p64514.cmd( "ifconfig  p64514-eth0 10.0.4.1 up" )
    p64514.setMAC( '00:00:00:00:00:04', 'p64514-eth0' )
    p64515.cmd( "ifconfig  p64515-eth0 10.0.5.1 up" )
    p64515.setMAC( '00:00:00:00:00:05', 'p64515-eth0' )
    p64516.cmd( "ifconfig  p64516-eth0 10.0.6.1 up" )
    p64516.setMAC( '00:00:00:00:00:06', 'p64516-eth0' )

    p64517.cmd( "ifconfig  p64517-eth0.20 10.0.7.1 up" )
    p64517.setMAC( '00:00:00:00:00:07', 'p64517-eth0.20' )
    p64518.cmd( "ifconfig  p64518-eth0.20 10.0.8.1 up" )
    p64518.setMAC( '00:00:00:00:00:08', 'p64518-eth0.20' )

    p64519.cmd( "ifconfig  p64519-eth0.10 10.0.9.1 up" )
    p64519.setMAC( '00:00:00:00:00:09', 'p64519-eth0.10' )
    p64520.cmd( "ifconfig  p64520-eth0.10 10.0.20.1 up" )
    p64520.setMAC( '00:00:00:00:00:20', 'p64520-eth0.10' )

    # setup configuration on the interface connected to hosts
    p64514.setIP( "4.0.0.254", 8, "p64514-eth1" )
    p64514.setMAC( '00:00:00:00:00:44', 'p64514-eth1' )
    p64515.setIP( "5.0.0.254", 8, "p64515-eth1" )
    p64515.setMAC( '00:00:00:00:00:55', 'p64515-eth1' )
    p64516.setIP( "6.0.0.254", 8, "p64516-eth1" )
    p64516.setMAC( '00:00:00:00:00:66', 'p64516-eth1' )

    p64517.setIP( "7.0.0.254", 8, "p64517-eth1.20" )
    p64517.setMAC( '00:00:00:00:00:77', 'p64517-eth1.20' )
    p64518.setIP( "8.0.0.254", 8, "p64518-eth1.20" )
    p64518.setMAC( '00:00:00:00:00:88', 'p64518-eth1.20' )

    p64519.setIP( "9.0.0.254", 8, "p64519-eth1.10" )
    p64519.setMAC( '00:00:00:00:00:99', 'p64519-eth1.10' )
    p64520.setIP( "20.0.0.254", 8, "p64520-eth1.10" )
    p64520.setMAC( '00:00:00:00:00:20', 'p64520-eth1.10' )

    # enable forwarding on BGP peer hosts
    p64514.cmd( 'sysctl net.ipv4.conf.all.forwarding=1' )
    p64515.cmd( 'sysctl net.ipv4.conf.all.forwarding=1' )
    p64516.cmd( 'sysctl net.ipv4.conf.all.forwarding=1' )

    p64517.cmd( 'sysctl net.ipv4.conf.all.forwarding=1' )
    p64518.cmd( 'sysctl net.ipv4.conf.all.forwarding=1' )
    p64519.cmd( 'sysctl net.ipv4.conf.all.forwarding=1' )
    p64520.cmd( 'sysctl net.ipv4.conf.all.forwarding=1' )

    # config interface for control plane connectivity
    p64514.setIP( "192.168.0.4", 24, "p64514-eth2" )
    p64515.setIP( "192.168.0.5", 24, "p64515-eth2" )
    p64516.setIP( "192.168.0.6", 24, "p64516-eth2" )

    p64517.setIP( "192.168.0.7", 24, "p64517-eth2" )
    p64518.setIP( "192.168.0.8", 24, "p64518-eth2" )
    p64519.setIP( "192.168.0.9", 24, "p64519-eth2" )
    p64520.setIP( "192.168.0.20", 24, "p64520-eth2" )

    # Setup hosts in each non-SDN AS
    h64514, h64515, h64516, h64517, h64518, h64519, h64520 = \
        net.get( 'h64514', 'h64515', 'h64516', 'h64517', 'h64518', 'h64519', 'h64520' )
    h64514.cmd( 'ifconfig h64514-eth0 4.0.0.1 up' )
    h64514.cmd( 'ip route add default via 4.0.0.254' )
    h64514.setIP( '192.168.0.44', 24, 'h64514-eth1' )  # for control plane
    h64515.cmd( 'ifconfig h64515-eth0 5.0.0.1 up' )
    h64515.cmd( 'ip route add default via 5.0.0.254' )
    h64516.cmd( 'ifconfig h64516-eth0 6.0.0.1 up' )
    h64516.cmd( 'ip route add default via 6.0.0.254' )

    h64517.cmd( 'ifconfig h64517-eth0.20 7.0.0.1 up' )
    h64517.cmd( 'ip route add default via 7.0.0.254' )
    h64517.setIP( '192.168.0.77', 24, 'h64517-eth1' )  # for control plane
    h64518.cmd( 'ifconfig h64518-eth0.20 8.0.0.1 up' )
    h64518.cmd( 'ip route add default via 8.0.0.254' )

    h64519.cmd( 'ifconfig h64519-eth0.10 9.0.0.1 up' )
    h64519.cmd( 'ip route add default via 9.0.0.254' )
    h64519.setIP( '192.168.0.99', 24, 'h64519-eth1' )  # for control plane
    h64520.cmd( 'ifconfig h64520-eth0.10 20.0.0.1 up' )
    h64520.cmd( 'ip route add default via 20.0.0.254' )

    # set up swCtl100 as a learning
    swCtl100 = net.get( 'swCtl100' )
    swCtl100.cmd( 'ovs-vsctl set-controller swCtl100 none' )
    swCtl100.cmd( 'ovs-vsctl set-fail-mode swCtl100 standalone' )

    # connect all switches to controller
    """
    for i in range ( 1, numSw + 1 ):
        swX = net.get( 'sw%s' % ( i ) )
        swX.cmd( 'ovs-vsctl set-controller sw%s tcp:%s:6653' % ( i, onos1IP ) )
    """
    # Start Quagga as the external BGP routers
    """
    for i in range ( 64514, 64516 + 1 ):
        startquagga( 'peer%s' % ( i ), i, 'quagga%s.conf' % ( i ) )
    """
    startquagga( p64514, 64514, 'quagga64514.conf' )
    startquagga( p64515, 64515, 'quagga64515.conf' )
    startquagga( p64516, 64516, 'quagga64516.conf' )

    startquagga( p64517, 64517, 'quagga64517.conf' )
    startquagga( p64518, 64518, 'quagga64518.conf' )
    startquagga( p64519, 64519, 'quagga64519.conf' )
    startquagga( p64520, 64520, 'quagga64520.conf' )

    # start Quagga as the BGP speaker
    startquagga( spk1, 64513, 'quagga-sdn.conf' )
    startquagga( spk2, 64512, 'quagga-sdn2.conf' )
    startquagga( spk3, 64511, 'quagga-sdn3.conf' )

    root = net.get( 'root' )

    root.intf( 'root-eth0' ).setIP( '1.1.1.2/24' )
    root.cmd( 'ip addr add 192.168.0.100/24 dev root-eth0' )

    spk1.intf( 'spk1-eth1' ).setIP( '1.1.1.1/24' )
    spk2.intf( 'spk2-eth1' ).setIP( '1.1.1.3/24' )
    spk3.intf( 'spk3-eth1' ).setIP( '1.1.1.5/24' )

    stopsshd()

    hosts = [ p64514, p64515, p64516, p64517, p64518, p64519, p64520,
              h64514, h64517, h64519 ]
    startsshds( hosts )
    #
    """
    forwarding1 = '%s:2000:%s:2000' % ( '1.1.1.2', onos1IP )
    root.cmd( 'ssh -nNT -o "PasswordAuthentication no" \
    -o "StrictHostKeyChecking no" -l sdn -L %s %s & ' % ( forwarding1, onos1IP ) )

    """
    # time.sleep( 3000000000 )
    CLI( net )

    stopsshd()
    stopquagga()
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'debug' )
    sdn1net()
