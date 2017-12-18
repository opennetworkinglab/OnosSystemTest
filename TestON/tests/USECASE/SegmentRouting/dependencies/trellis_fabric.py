#!/usr/bin/python
import os
import re
from optparse import OptionParser

from ipaddress import ip_network
from mininet.node import RemoteController, OVSBridge, Host
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.nodelib import NAT
from mininet.cli import CLI

from routinglib import BgpRouter, RoutedHost
from trellislib import DhcpServer, TaggedRoutedHost, DualHomedRoutedHost, DualHomedTaggedRoutedHost

# Parse command line options and dump results
def parseOptions():
    "Parse command line options"
    parser = OptionParser()
    parser.add_option( '--spine', dest='spine', type='int', default=2,
                       help='number of spine switches, default=2' )
    parser.add_option( '--leaf', dest='leaf', type='int', default=2,
                       help='number of leaf switches, default=2' )
    parser.add_option( '--fanout', dest='fanout', type='int', default=2,
                       help='number of hosts per leaf switch, default=2' )
    parser.add_option( '--onos-ip', dest='onosIp', type='str', default='',
                       help='IP address list of ONOS instances, separated by comma(,). Overrides --onos option' )
    parser.add_option( '--ipv6', action="store_true", dest='ipv6',
                       help='hosts are capable to use also ipv6' )
    parser.add_option( '--dual-homed', action="store_true", dest='dualhomed', default=False,
                       help='True if the topology is dual-homed, default=False' )
    parser.add_option( '--vlan', dest='vlan', type='str', default='',
                       help='list of vlan id for hosts, separated by comma(,).'
                            'Empty or id with 0 will be unconfigured.' )
    ( options, args ) = parser.parse_args()
    return options, args


opts, args = parseOptions()

IP6_SUBNET_CLASS = 120
IP4_SUBNET_CLASS = 24

# TODO: DHCP support
class IpHost( Host ):

    def __init__( self, name, *args, **kwargs ):
        super( IpHost, self ).__init__( name, *args, **kwargs )
        gateway = re.split( '\.|/', kwargs[ 'ip' ] )
        gateway[ 3 ] = '254'
        self.gateway = '.'.join( gateway[ 0:4 ] )

    def config( self, **kwargs ):
        Host.config( self, **kwargs )
        mtu = "ifconfig " + self.name + "-eth0 mtu 1490"
        self.cmd( mtu )
        self.cmd( 'ip route add default via %s' % self.gateway )

class DualHomedIpHost(IpHost):
    def __init__(self, name, *args, **kwargs):
        super(DualHomedIpHost, self).__init__(name, **kwargs)
        self.bond0 = None

    def config(self, **kwargs):
        super(DualHomedIpHost, self).config(**kwargs)
        intf0 = self.intfs[0].name
        intf1 = self.intfs[1].name
        self.bond0 = "%s-bond0" % self.name
        self.cmd('modprobe bonding')
        self.cmd('ip link add %s type bond' % self.bond0)
        self.cmd('ip link set %s down' % intf0)
        self.cmd('ip link set %s down' % intf1)
        self.cmd('ip link set %s master %s' % (intf0, self.bond0))
        self.cmd('ip link set %s master %s' % (intf1, self.bond0))
        self.cmd('ip addr flush dev %s' % intf0)
        self.cmd('ip addr flush dev %s' % intf1)
        self.cmd('ip link set %s up' % self.bond0)

    def terminate(self, **kwargs):
        self.cmd('ip link set %s down' % self.bond0)
        self.cmd('ip link delete %s' % self.bond0)
        self.cmd('kill -9 `cat %s`' % self.pidFile)
        self.cmd('rm -rf %s' % self.pidFile)
        super(DualHomedIpHost, self).terminate()


# TODO: Implement IPv6 support
class DualHomedLeafSpineFabric (Topo) :
    def __init__(self, spine = 2, leaf = 4, fanout = 2, vlan_id = [], **opts):
        Topo.__init__(self, **opts)
        spines = dict()
        leafs = dict()

        # leaf should be 2 or 4

        # calculate the subnets to use and set options
        linkopts = dict( bw=100 )
        # Create spine switches
        for s in range(spine):
            spines[s] = self.addSwitch('spine10%s' % (s + 1), dpid = "00000000010%s" % (s + 1) )

        # Create leaf switches
        for ls in range(leaf):
            leafs[ls] = self.addSwitch('leaf%s' % (ls + 1), dpid = "00000000000%s" % ( ls + 1) )

            # Connect leaf to all spines with dual link
            for s in range( spine ):
                switch = spines[ s ]
                self.addLink(leafs[ls], switch, **linkopts)
                self.addLink(leafs[ls], switch, **linkopts)

            # Add hosts after paired ToR switches are added.
            if ls % 2 == 0:
                continue

            # Add leaf-leaf link
            self.addLink(leafs[ls], leafs[ls-1])

            dual_ls = ls / 2
            # Add hosts
            for f in range(fanout):
                if vlan_id[ dual_ls * fanout + f] != 0:
                    host = self.addHost(
                        name='h%s' % ( dual_ls * fanout + f + 1),
                        cls=DualHomedTaggedRoutedHost,
                        ips=['10.0.%d.%d/%d' % ( dual_ls + 2, f + 1, IP4_SUBNET_CLASS)],
                        gateway='10.0.%d.254' % ( dual_ls + 2),
                        mac='00:aa:00:00:00:%02x' % (dual_ls * fanout + f + 1),
                        vlan=vlan_id[ dual_ls*fanout + f ]
                    )
                else:
                    host = self.addHost(
                        name='h%s' % (dual_ls * fanout + f + 1),
                        cls= DualHomedRoutedHost,
                        ips=['10.0.%d.%d/%d' % (dual_ls+2, f+1, IP4_SUBNET_CLASS)],
                        gateway='10.0.%d.254' % (dual_ls+2),
                        mac='00:aa:00:00:00:%02x' % (dual_ls * fanout + f + 1)
                    )
                self.addLink(host, leafs[ls], **linkopts)
                self.addLink(host, leafs[ls-1], **linkopts)

        last_ls = leafs[leaf-2]
        last_paired_ls = leafs[leaf-1]
        # Create common components
        # DHCP server
        dhcp = self.addHost('dhcp', cls=DhcpServer, mac='00:99:00:00:00:01', ips=['10.0.3.253/24'],
                            gateway='10.0.3.254')

        # Control plane switch (for DHCP servers)
        cs1 = self.addSwitch('cs1', cls=OVSBridge)
        self.addLink(cs1, last_ls)
        self.addLink(dhcp, cs1)

        # Control plane switch (for quagga fpm)
        cs0 = self.addSwitch('cs0', cls=OVSBridge)

        # Control plane NAT (for quagga fpm)
        nat = self.addHost('nat', cls=NAT,
                           ip='172.16.0.1/12',
                           subnet=str(ip_network(u'172.16.0.0/12')), inNamespace=False)
        self.addLink(cs0, nat)

        # Internal Quagga bgp1
        intfs = {'bgp1-eth0': {'ipAddrs': ['10.0.1.2/24', '2000::102/120'], 'mac': '00:88:00:00:00:02'},
                 'bgp1-eth1': {'ipAddrs': ['172.16.0.2/12']}}
        bgp1 = self.addHost('bgp1', cls=BgpRouter,
                            interfaces=intfs,
                            quaggaConfFile='conf/bgpdbgp1.conf',
                            zebraConfFile='conf/zebradbgp1.conf')
        self.addLink(bgp1, last_ls)
        self.addLink(bgp1, cs0)

        # Internal Quagga bgp2
        intfs = {'bgp2-eth0': [{'ipAddrs': ['10.0.5.2/24', '2000::502/120'], 'mac': '00:88:00:00:00:04', 'vlan': '150'},
                               {'ipAddrs': ['10.0.6.2/24', '2000::602/120'], 'mac': '00:88:00:00:00:04', 'vlan': '160'}],
                 'bgp2-eth1': {'ipAddrs': ['172.16.0.4/12']}}
        bgp2 = self.addHost('bgp2', cls=BgpRouter,
                            interfaces=intfs,
                            quaggaConfFile='conf/bgpdbgp2.conf',
                            zebraConfFile='conf/zebradbgp2.conf')
        self.addLink(bgp2, last_paired_ls)
        self.addLink(bgp2, cs0)

        # External Quagga r1
        intfs = {'r1-eth0': {'ipAddrs': ['10.0.1.1/24', '2000::101/120'], 'mac': '00:88:00:00:00:01'},
                 'r1-eth1': {'ipAddrs': ['10.0.5.1/24', '2000::501/120'], 'mac': '00:88:00:00:00:11'},
                 'r1-eth2': {'ipAddrs': ['10.0.99.1/16']}}
        r1 = self.addHost('r1', cls=BgpRouter,
                            interfaces=intfs,
                            quaggaConfFile='conf/bgpdr1.conf')
        self.addLink(r1, last_ls)
        self.addLink(r1, last_paired_ls)

        # External IPv4 Host behind r1
        rh1 = self.addHost('rh1', cls=RoutedHost, ips=['10.0.99.2/24'], gateway='10.0.99.1')
        self.addLink(r1, rh1)

        # External Quagga r2
        intfs = {'r2-eth0': {'ipAddrs': ['10.0.6.1/24', '2000::601/120'], 'mac': '00:88:00:00:00:02'},
                 'r2-eth1': {'ipAddrs': ['10.0.7.1/24', '2000::701/120'], 'mac': '00:88:00:00:00:22'},
                 'r2-eth2': {'ipAddrs': ['10.0.99.1/16']}}
        r2 = self.addHost('r2', cls=BgpRouter,
                            interfaces=intfs,
                            quaggaConfFile='conf/bgpdr2.conf')
        self.addLink(r2, last_ls)
        self.addLink(r2, last_paired_ls)

        # External IPv4 Host behind r2
        rh2 = self.addHost('rh2', cls=RoutedHost, ips=['10.0.99.2/24'], gateway='10.0.99.1')
        self.addLink(r2, rh2)

class LeafSpineFabric (Topo) :
    def __init__(self, spine = 2, leaf = 2, fanout = 2, vlan_id = [], **opts):
        Topo.__init__(self, **opts)
        spines = dict()
        leafs = dict()

        # TODO: support IPv6 hosts
        linkopts = dict( bw=100 )

        # Create spine switches
        for s in range(spine):
            spines[s] = self.addSwitch('spine10%s' % (s + 1), dpid = "00000000010%s" % (s + 1) )

        # Create leaf switches
        for ls in range(leaf):
            leafs[ls] = self.addSwitch('leaf%s' % (ls + 1), dpid = "00000000000%s" % ( ls + 1) )

            # Connect leaf to all spines
            for s in range( spine ):
                switch = spines[ s ]
                self.addLink( leafs[ ls ], switch, **linkopts )

            # If dual-homed ToR, add hosts only when adding second switch at each edge-pair
            # When the number of leaf switches is odd, leave the last switch as a single ToR

            # Add hosts
            for f in range(fanout):
                if vlan_id[ls * fanout + f] != 0:
                    host = self.addHost(
                        name='h%s' % (ls * fanout + f + 1),
                        cls=TaggedRoutedHost,
                        ips=['10.0.%d.%d/%d' % (ls+2, f+1, IP4_SUBNET_CLASS)],
                        gateway='10.0.%d.254' % (ls+2),
                        mac='00:aa:00:00:00:%02x' % (ls * fanout + f + 1),
                        vlan=vlan_id[ ls*fanout + f ]
                    )
                else:
                    host = self.addHost(
                        name='h%s' % (ls * fanout + f + 1),
                        cls= RoutedHost,
                        ips=['10.0.%d.%d/%d' % (ls+2, f+1, IP4_SUBNET_CLASS)],
                        gateway='10.0.%d.254' % (ls+2),
                        mac='00:aa:00:00:00:%02x' % (ls * fanout + f + 1)
                    )
                self.addLink(host, leafs[ls], **linkopts)

        last_ls = leafs[leaf-1]
        # Create common components
        # DHCP server
        dhcp = self.addHost('dhcp', cls=DhcpServer, mac='00:99:00:00:00:01', ips=['10.0.3.253/24'],
                            gateway='10.0.3.254')

        # Control plane switch (for DHCP servers)
        cs1 = self.addSwitch('cs1', cls=OVSBridge)
        self.addLink(cs1, last_ls)
        self.addLink(dhcp, cs1)

        # Control plane switch (for quagga fpm)
        cs0 = self.addSwitch('cs0', cls=OVSBridge)

        # Control plane NAT (for quagga fpm)
        nat = self.addHost('nat', cls=NAT,
                           ip='172.16.0.1/12',
                           subnet=str(ip_network(u'172.16.0.0/12')), inNamespace=False)
        self.addLink(cs0, nat)

        # Internal Quagga bgp1
        intfs = {'bgp1-eth0': {'ipAddrs': ['10.0.1.2/24', '2000::102/120'], 'mac': '00:88:00:00:00:02'},
                 'bgp1-eth1': {'ipAddrs': ['172.16.0.2/12']}}
        bgp1 = self.addHost('bgp1', cls=BgpRouter,
                            interfaces=intfs,
                            quaggaConfFile='conf/bgpdbgp1.conf',
                            zebraConfFile='conf/zebradbgp1.conf')
        self.addLink(bgp1, last_ls)
        self.addLink(bgp1, cs0)

        # External Quagga r1
        intfs = {'r1-eth0': {'ipAddrs': ['10.0.1.1/24', '2000::101/120'], 'mac': '00:88:00:00:00:01'},
                 'r1-eth1': {'ipAddrs': ['10.0.99.1/16']},
                 'r1-eth2': {'ipAddrs': ['2000::9901/120']}}
        r1 = self.addHost('r1', cls=BgpRouter,
                            interfaces=intfs,
                            quaggaConfFile='conf/bgpdr1.conf')
        self.addLink(r1, last_ls)

        # External IPv4 Host behind r1
        rh1 = self.addHost('rh1', cls=RoutedHost, ips=['10.0.99.2/24'], gateway='10.0.99.1')
        self.addLink(r1, rh1)


def config( opts ):
    spine = opts.spine
    leaf = opts.leaf
    fanout = opts.fanout
    ipv6 = opts.ipv6
    dualhomed = opts.dualhomed
    if opts.vlan == '':
        vlan = [0] * (((leaf / 2) if dualhomed else leaf) * fanout)
    else:
        vlan = [int(vlan_id) if vlan_id != '' else 0 for vlan_id in opts.vlan.split(',')]

    if opts.onosIp != '':
        controllers = opts.onosIp.split( ',' )
    else:
        controllers = ['127.0.0.1']

    if len(vlan) != ((leaf / 2) if dualhomed else leaf ) * fanout:
        print "Invalid vlan configuration is given."
        return

    if not ipv6:
        if dualhomed:
            if leaf % 2 == 1 or leaf == 0:
                print "Even number of leaf switches (at least two) are needed to build dual-homed topology."
                return
            else:
                topo = DualHomedLeafSpineFabric(spine=spine, leaf=leaf, fanout=fanout, vlan_id=vlan)
        else:
            topo = LeafSpineFabric(spine=spine, leaf=leaf, fanout=fanout, vlan_id=vlan)
    else:
        print "IPv6 hosts are not supported yet."
        return

    net = Mininet( topo=topo, link=TCLink, build=False,
                   controller=None, autoSetMacs=True )
    i = 0
    for ip in controllers:
        net.addController( "c%s" % ( i ), controller=RemoteController, ip=ip )
        i += 1
    net.build()
    net.start()
    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    config(opts)
    os.system('sudo mn -c')
