#!/usr/bin/python
import os
import re
from optparse import OptionParser
from ipaddress import ip_network
from mininet.node import RemoteController, OVSBridge, Host, OVSSwitch
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.nodelib import NAT
from mininet.cli import CLI

from routinglib import BgpRouter, RoutedHost
from trellislib import DhcpServer, TaggedRoutedHost, DualHomedRoutedHost, DualHomedTaggedRoutedHost, DhcpClient, Dhcp6Client, DhcpServer, Dhcp6Server, TrellisHost

from bmv2 import ONOSBmv2Switch

# Parse command line options and dump results
def parseOptions():
    "Parse command line options"
    parser = OptionParser()
    parser.add_option( '--dhcp', dest='dhcp', type='int', default=0,
                       help='Configure hosts with dhcp or not' )
    parser.add_option( '--routers', dest='routers', type='int', default=0,
                       help='Configure external routers or not in the topology' )
    parser.add_option( '--ipv6', dest='ipv6', type='int', default=0,
                       help='Configure hosts with ipv6 or not' )
    parser.add_option( '--ipv4', dest='ipv4', type='int', default=1,
                       help='Configure hosts with ipv4 or not' )
    parser.add_option( '--onos-ip', dest='onosIp', type='str', default='',
                       help='IP address list of ONOS instances, separated by comma(,). Overrides --onos option' )
    parser.add_option( '--switch', dest='switch', type='str', default='ovs',
                       help='Switch type: ovs, bmv2 (with fabric.p4)' )

    ( options, args ) = parser.parse_args()
    return options, args

opts, args = parseOptions()

FABRIC_PIPECONF = "org.onosproject.pipelines.fabric"

SWITCH_TO_PARAMS_DICT = {
    "ovs": dict(cls=OVSSwitch),
    "bmv2": dict(cls=ONOSBmv2Switch, pipeconf=FABRIC_PIPECONF)
}
if opts.switch not in SWITCH_TO_PARAMS_DICT:
    raise Exception("Unknown switch type '%s'" % opts.switch)
SWITCH_PARAMS = SWITCH_TO_PARAMS_DICT[opts.switch]

class ComcastLeafSpineFabric(Topo):

    spines = dict()
    leafs = dict()
    hosts_dict = dict()

    def createIpv4Hosts(self, dhcp):

        h1 = self.addHost('h1v4', cls=TrellisHost,
                           mac='00:aa:00:00:00:01', ips=['10.1.0.1/24'],
                           gateway='10.1.0.254', dhcpClient=dhcp)
        self.addLink(h1, self.leafs[0])
        self.hosts_dict['h1v4'] = h1

        h2 = self.addHost('h2v4', cls=TrellisHost,
                          mac='00:aa:00:00:01:01', ips=['10.1.10.1/24'],
                          gateway='10.1.10.254', dhcpClient=dhcp)
        self.addLink(h2, self.leafs[0])
        self.hosts_dict['h2v4'] = h2

        h3 = self.addHost('h3v4', cls=TrellisHost,
                          mac='00:aa:00:00:00:02', ips=['10.2.0.1/24'],
                          gateway='10.2.0.254', dhcpClient=dhcp)
        self.addLink(h3, self.leafs[1])
        self.hosts_dict['h3v4'] = h3

        h4 = self.addHost('h4v4', cls=TrellisHost,
                          mac='00:aa:00:00:00:03', ips=['10.2.30.1/24'],
                          gateway='10.2.30.254', dhcpClient=dhcp,
                          dualHomed=True)
        self.addLink(h4, self.leafs[1])
        self.addLink(h4, self.leafs[2])
        self.hosts_dict['h4v4'] = h4

        h5 = self.addHost('h5v4', cls=TrellisHost,
                          mac='00:aa:00:00:00:04', ips=['10.2.20.1/24'],
                          gateway='10.2.20.254', dhcpClient=dhcp, vlan=30,
                          dualHomed=True)
        self.addLink(h5, self.leafs[1])
        self.addLink(h5, self.leafs[2])
        self.hosts_dict['h5v4'] = h5

        h6 = self.addHost('h6v4', cls=TrellisHost,
                          mac='00:aa:00:00:00:05', ips=['10.2.10.1/24'],
                          gateway='10.2.10.254', dhcpClient=dhcp, vlan=20)
        self.addLink(h6, self.leafs[2])
        self.hosts_dict['h6v4'] = h6

        h7 = self.addHost('h7v4', cls=TrellisHost,
                          mac='00:aa:00:00:01:05', ips=['10.2.40.1/24'],
                          gateway='10.2.40.254', dhcpClient=dhcp, vlan=40)
        self.addLink(h7, self.leafs[2])
        self.hosts_dict['h7v4'] = h7

        h8 = self.addHost('h8v4', cls=TrellisHost,
                          mac='00:aa:00:00:00:06', ips=['10.3.0.1/24'],
                          gateway='10.3.0.254', dhcpClient=dhcp)
        self.addLink(h8, self.leafs[3])
        self.hosts_dict['h8v4'] = h8

        h9 = self.addHost('h9v4', cls=TrellisHost,
                          mac='00:aa:00:00:00:07', ips=['10.3.10.1/24'],
                          gateway='10.3.10.254', dhcpClient=dhcp, vlan=50,
                          dualHomed=True)
        self.addLink(h9, self.leafs[3])
        self.addLink(h9, self.leafs[4])
        self.hosts_dict['h9v4'] = h9

        h10 = self.addHost('h10v4', cls=TrellisHost,
                           mac='00:aa:00:00:00:08', ips=['10.3.30.1/24'],
                           gateway='10.3.30.254', dhcpClient=dhcp, vlan=60,
                           dualHomed=True)
        self.addLink(h10, self.leafs[3])
        self.addLink(h10, self.leafs[4])
        self.hosts_dict['h10v4'] = h10

        h11 = self.addHost('h11v4', cls=TrellisHost,
                           mac='00:aa:00:00:00:0a', ips=['10.3.20.1/24'],
                           gateway='10.3.20.254', dhcpClient=dhcp, vlan=70)
        self.addLink(h11, self.leafs[4])
        self.hosts_dict['h11v4'] = h11

        h12 = self.addHost('h12v4', cls=TrellisHost,
                           mac='00:aa:00:00:02:01', ips=['10.5.10.1/24'],
                           gateway='10.5.10.254', dhcpClient=dhcp, vlan=80)
        self.addLink(h12, self.leafs[5])
        self.hosts_dict['h12v4'] = h12

        h13 = self.addHost('h13v4', cls=TrellisHost,
                           mac='00:aa:00:00:02:02', ips=['10.5.20.1/24'],
                           gateway='10.5.20.254', dhcpClient=dhcp)
        self.addLink(h13, self.leafs[5])
        self.hosts_dict['h13v4'] = h13
        return

    def createIpv6Hosts(self, dhcp):

        h1 = self.addHost('h1v6', cls=TrellisHost,
                          mac='00:bb:00:00:00:01', ips=["1000::3fe/120"],
                          gateway='1000::3ff', dhcpClient=dhcp, ipv6=1)
        self.addLink(h1, self.leafs[0])
        self.hosts_dict['h1v6'] = h1

        h2 = self.addHost('h2v6', cls=TrellisHost,
                          mac='00:bb:00:00:01:01', ips=['1001::3fe/120'],
                          gateway='1001::3ff', dhcpClient=dhcp, ipv6=1)
        self.addLink(h2, self.leafs[0])
        self.hosts_dict['h2v6'] = h2

        h3 = self.addHost('h3v6', cls=TrellisHost,
                          mac='00:bb:00:00:00:02', ips=['1002::3fe/120'],
                          gateway='1002::3ff', dhcpClient=dhcp, ipv6=1)
        self.addLink(h3, self.leafs[1])
        self.hosts_dict['h3v6'] = h3

        h4 = self.addHost('h4v6', cls=TrellisHost,
                          mac='00:bb:00:00:00:03', ips=['1003::3fe/120'],
                          gateway='1003::3ff', dhcpClient=dhcp, ipv6=1,
                          dualHomed=True)
        self.addLink(h4, self.leafs[1])
        self.addLink(h4, self.leafs[2])
        self.hosts_dict['h4v6'] = h4

        h5 = self.addHost('h5v6', cls=TrellisHost,
                          mac='00:bb:00:00:00:04', ips=['1004::3fe/120'],
                          gateway='1004::3ff', dhcpClient=False, ipv6=1,
                          vlan=121,
                          dualHomed=True)
        self.addLink(h5, self.leafs[1])
        self.addLink(h5, self.leafs[2])
        self.hosts_dict['h5v6'] = h5

        h6 = self.addHost('h6v6', cls=TrellisHost,
                          mac='00:bb:00:00:00:05', ips=['1005::3fe/120'],
                          gateway='1005::3ff', dhcpClient=False, ipv6=1,
                          vlan=122)
        self.addLink(h6, self.leafs[2])
        self.hosts_dict['h6v6'] = h6

        h7 = self.addHost('h7v6', cls=TrellisHost,
                          mac='00:bb:00:00:01:05', ips=['1006::3fe/120'],
                          gateway='1006::3ff', dhcpClient=False, ipv6=1,
                          vlan=123)
        self.addLink(h7, self.leafs[2])
        self.hosts_dict['h7v6'] = h7

        h8 = self.addHost('h8v6', cls=TrellisHost,
                          mac='00:bb:00:00:00:06', ips=['1007::3fe/120'],
                          gateway='1007::3ff', dhcpClient=dhcp, ipv6=1)
        self.addLink(h8, self.leafs[3])
        self.hosts_dict['h8v6'] = h8

        h9 = self.addHost('h9v6', cls=TrellisHost,
                          mac='00:bb:00:00:00:07', ips=['1008::3fe/120'],
                          gateway='1008::3ff', dhcpClient=False, vlan=124,
                          dualHomed=True, ipv6=1)
        self.addLink(h9, self.leafs[3])
        self.addLink(h9, self.leafs[4])
        self.hosts_dict['h9v6'] = h9

        h10 = self.addHost('h10v6', cls=TrellisHost,
                           mac='00:bb:00:00:00:08', ips=['1009::3fe/120'],
                           gateway='1009::3ff', dhcpClient=False, vlan=125,
                           dualHomed=True, ipv6=1)
        self.addLink(h10, self.leafs[3])
        self.addLink(h10, self.leafs[4])
        self.hosts_dict['h10v6'] = h10

        h11 = self.addHost('h11v6', cls=TrellisHost,
                           mac='00:bb:00:00:00:0a', ips=['1010::3fe/120'],
                           gateway='1010::3ff', dhcpClient=False, vlan=126,
                           ipv6=1)
        self.addLink(h11, self.leafs[4])
        self.hosts_dict['h11v6'] = h11

        h12 = self.addHost('h12v6', cls=TrellisHost,
                           mac='00:bb:00:00:01:0a', ips=['1011::3fe/120'],
                           gateway='1011::3ff', dhcpClient=False, vlan=127,
                           ipv6=1)
        self.addLink(h12, self.leafs[5])
        self.hosts_dict['h12v6'] = h12

        h13 = self.addHost('h13v6', cls=TrellisHost,
                           mac='00:bb:00:00:02:0a', ips=['1012::3fe/120'],
                           gateway='1012::3ff', dhcpClient=dhcp, ipv6=1)
        self.addLink(h13, self.leafs[5])
        self.hosts_dict['h13v6'] = h13

        return

    '''
    Creates the HAGG topology employed by Comcast.
    '''
    def __init__(self, dhcp=False, routers=False, ipv4=False, ipv6=False, **opts):
        Topo.__init__(self, **opts)

        linkopts = dict( bw=10 )

        spine = 4
        leaf = 6

        # Create spine switches
        for s in range(spine):
            self.spines[s] = self.addSwitch( 'spine10%s' % (s + 1),
                                             dpid = "00000000010%s" % (s + 1),
                                             **SWITCH_PARAMS )

        # Create leaf switches
        for ls in range(leaf):
            self.leafs[ls] = self.addSwitch( 'leaf%s' % (ls + 1),
                                             dpid = "00000000000%s" % (ls + 1),
                                             **SWITCH_PARAMS )

        # connecting leaf and spines, leafs 1-5 have double links
        for s in range(2):
            spine_switch = self.spines[s]

            for ls in range(1, 5):
                leaf_switch = self.leafs[ls]

                self.addLink( spine_switch, leaf_switch, **linkopts )
                self.addLink( spine_switch, leaf_switch, **linkopts )

        # connect paired leafs
        self.addLink(self.leafs[1], self.leafs[2], **linkopts)
        self.addLink(self.leafs[3], self.leafs[4], **linkopts)

        # build second fabric with single links
        for s in range(2, 4):
            spine_switch = self.spines[s]

            for ls in [0, 5]:
                leaf_switch = self.leafs[ls]
                self.addLink( spine_switch, leaf_switch, **linkopts )

        # connect spines together
        self.addLink(self.spines[2], self.spines[0], **linkopts)
        self.addLink(self.spines[3], self.spines[1], **linkopts)

        # create hosts
        if ipv6:
            self.createIpv6Hosts(dhcp)

        if ipv4:
            self.createIpv4Hosts(dhcp)

        if not ipv4 and not ipv6:
            print("No hosts were created!")

        # create quagga routers
        # Note: Change "fpm connection ip" to $OC1 in zebradbgp1.conf and zebradbgp2.conf to make quagga work correctly
        if routers:
            last_ls = self.leafs[4]
            last_paired_ls = self.leafs[3]

            # Control plane switch (for quagga fpm)
            cs0 = self.addSwitch('cs0', cls=OVSBridge)

            # Control plane NAT (for quagga fpm)
            nat = self.addHost('nat', cls=NAT,
                               ip='172.16.0.1/12',
                               subnet=str(ip_network(u'172.16.0.0/12')), inNamespace=False)
            self.addLink(cs0, nat)

            # Internal Quagga bgp1
            intfs = {'bgp1-eth0': [{'ipAddrs': ['10.0.1.2/24', '2000::102/120'], 'mac': '00:88:00:00:00:03', 'vlan': '110'},
                                   {'ipAddrs': ['10.0.7.2/24', '2000::702/120'], 'mac': '00:88:00:00:00:03', 'vlan': '170'}],
                     'bgp1-eth1': {'ipAddrs': ['172.16.0.3/12']}}
            bgp1 = self.addHost('bgp1', cls=BgpRouter,
                                interfaces=intfs,
                                quaggaConfFile='./bgpdbgp1.conf',
                                zebraConfFile='./zebradbgp1.conf')
            self.addLink(bgp1, last_paired_ls)
            self.addLink(bgp1, cs0)

            # Internal Quagga bgp2
            intfs = {'bgp2-eth0': [{'ipAddrs': ['10.0.5.2/24', '2000::502/120'], 'mac': '00:88:00:00:00:04', 'vlan': '150'},
                                   {'ipAddrs': ['10.0.6.2/24', '2000::602/120'], 'mac': '00:88:00:00:00:04', 'vlan': '160'}],
                     'bgp2-eth1': {'ipAddrs': ['172.16.0.4/12']}}
            bgp2 = self.addHost('bgp2', cls=BgpRouter,
                                interfaces=intfs,
                                quaggaConfFile='./bgpdbgp2.conf',
                                zebraConfFile='./zebradbgp2.conf')
            self.addLink(bgp2, last_ls)
            self.addLink(bgp2, cs0)

            # External Quagga r1
            intfs = {'r1-eth0': {'ipAddrs': ['10.0.1.1/24', '2000::101/120'], 'mac': '00:88:00:00:00:01'},
                     'r1-eth1': {'ipAddrs': ['10.0.5.1/24', '2000::501/120'], 'mac': '00:88:00:00:00:11'},
                     'r1-eth2': {'ipAddrs': ['10.0.99.1/16']},
                     'r1-eth3': {'ipAddrs': ['2000::9901/120']},
                     'r1-eth4': {'ipAddrs': ['2000::7701/120']},
                     'r1-eth5': {'ipAddrs': ['10.0.88.1/24']},
                     'r1-eth6': {'ipAddrs': ['2000::8701/120']}}
            r1 = self.addHost('r1', cls=BgpRouter,
                                interfaces=intfs,
                                quaggaConfFile='./bgpdr1.conf')
            self.addLink(r1, last_paired_ls)
            self.addLink(r1, last_ls)

            # External IPv4 Host behind r1
            rh1v4 = self.addHost('rh1v4', cls=RoutedHost, ips=['10.0.99.2/24'], gateway='10.0.99.1')
            self.addLink(r1, rh1v4)

            # External IPv6 Host behind r1
            rh1v6 = self.addHost('rh1v6', cls=RoutedHost, ips=['2000::9902/120'], gateway='2000::9901')
            self.addLink(r1, rh1v6)

            # Another external IPv6 Host behind r1
            rh11v6 = self.addHost('rh11v6', cls=RoutedHost, ips=['2000::7702/120'], gateway='2000::7701')
            self.addLink(r1, rh11v6)

            # Add an external ipv4 hosts that is not configured in the bgp conf
            # files
            rh5v4 = self.addHost('rh5v4', cls=RoutedHost, ips=['10.0.88.2/24'], gateway='10.0.88.1')
            self.addLink(r1, rh5v4)

            # Add an external ipv6 hosts that is not configured in the bgp conf
            # files
            rh5v6 = self.addHost('rh5v6', cls=RoutedHost, ips=['2000::8702/120'], gateway='2000::8701')
            self.addLink(r1, rh5v6)

            # External Quagga r2
            intfs = {'r2-eth0': {'ipAddrs': ['10.0.6.1/24', '2000::601/120'], 'mac': '00:88:00:00:00:02'},
                     'r2-eth1': {'ipAddrs': ['10.0.7.1/24', '2000::701/120'], 'mac': '00:88:00:00:00:22'},
                     'r2-eth2': {'ipAddrs': ['10.0.99.1/16']},
                     'r2-eth3': {'ipAddrs': ['2000::9901/120']},
                     'r2-eth4': {'ipAddrs': ['2000::8801/120']}}
            r2 = self.addHost('r2', cls=BgpRouter,
                                interfaces=intfs,
                                quaggaConfFile='./bgpdr2.conf')
            self.addLink(r2, last_ls)
            self.addLink(r2, last_paired_ls)

            # External IPv4 Host behind r2
            rh2v4 = self.addHost('rh2v4', cls=RoutedHost, ips=['10.0.99.2/24'], gateway='10.0.99.1')
            self.addLink(r2, rh2v4)

            # External IPv6 Host behind r2
            rh2v6 = self.addHost('rh2v6', cls=RoutedHost, ips=['2000::9902/120'], gateway='2000::9901')
            self.addLink(r2, rh2v6)

            # Another external IPv6 Host behind r1
            rh22v6 = self.addHost('rh22v6', cls=RoutedHost, ips=['2000::8802/120'], gateway='2000::8801')
            self.addLink(r2, rh22v6)

        # create dhcp servers
        if dhcp:
            cs1 = self.addSwitch('cs1', cls=OVSBridge)
            self.addLink(cs1, self.leafs[4])
            if ipv4:
                dhcp4 = self.addHost( 'dhcp', cls=TrellisHost,
                                      mac="00:cc:00:00:00:01", ips=["10.0.3.253/24"],
                                      gateway="10.0.3.254", dhcpServer=True)
                self.addLink(dhcp4, cs1, **linkopts)
            if ipv6:
                dhcp6 = self.addHost( 'dhcp6', cls=TrellisHost,
                                      mac="00:dd:00:00:00:01", ips=["2000::3fd/120"],
                                      gateway="2000::3ff", dhcpServer=True, ipv6=True)
                self.addLink(dhcp6, cs1, **linkopts)


def config( opts ):

    dhcp = bool(opts.dhcp)
    routers = bool(opts.routers)
    ipv6 = bool(opts.ipv6)
    ipv4 = bool(opts.ipv4)

    if opts.onosIp != '':
        controllers = opts.onosIp.split( ',' )
    else:
        controllers = ['127.0.0.1']
    topo = ComcastLeafSpineFabric(dhcp=dhcp, routers=routers, ipv6=ipv6,
                                  ipv4=ipv4)

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

