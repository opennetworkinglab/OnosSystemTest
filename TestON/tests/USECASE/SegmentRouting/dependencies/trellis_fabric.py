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

from routinglib import BgpRouter
from trellislib import TrellisHost, DhcpRelay
from functools import partial

from bmv2 import ONOSBmv2Switch

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
    parser.add_option( '--dhcp-client', action="store_true", dest='dhcpClient', default=False,
                       help='Set hosts as DhcpClient if True' )
    parser.add_option( '--dhcp-relay', action="store_true", dest='dhcpRelay', default=False,
                       help='Connect half of the hosts to switch indirectly (via DHCP relay) if True' )
    parser.add_option( '--multiple-dhcp-server', action="store_true", dest='multipleServer', default=False,
                       help='Use another DHCP server for indirectly connected DHCP clients if True' )
    parser.add_option( '--remote-dhcp-server', action="store_true", dest='remoteServer', default=False,
                       help='Connect DHCP server indirectly (via gateway) if True' )
    parser.add_option( '--switch', dest='switch', type='str', default='ovs',
                       help='Switch type: ovs, bmv2 (with fabric.p4)' )
    ( options, args ) = parser.parse_args()
    return options, args

opts, args = parseOptions()

IP6_SUBNET_CLASS = 120
IP4_SUBNET_CLASS = 24
FABRIC_PIPECONF = "org.onosproject.pipelines.fabric"

SWITCH_TO_PARAMS_DICT = {
    "ovs": dict(cls=OVSSwitch),
    "bmv2": dict(cls=ONOSBmv2Switch, pipeconf=FABRIC_PIPECONF)
}
if opts.switch not in SWITCH_TO_PARAMS_DICT:
    raise Exception("Unknown switch type '%s'" % opts.switch)
SWITCH_PARAMS = SWITCH_TO_PARAMS_DICT[opts.switch]

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
    def __init__(self, spine = 2, leaf = 2, fanout = 2, vlan_id = [], ipv6 = False,
                 dhcp_client = False, dhcp_relay = False,
                 multiple_server = False, remote_server = False, **opts):
        # TODO: add support to dhcp_relay, multiple_server and remote_server
        Topo.__init__(self, **opts)
        spines = dict()
        leafs = dict()

        # leaf should be 2 or 4

        # calculate the subnets to use and set options
        linkopts = dict( bw=100 )
        # Create spine switches
        for s in range(spine):
            spines[s] = self.addSwitch( 'spine10%s' % (s + 1),
                                        dpid="00000000010%s" % (s + 1),
                                        **SWITCH_PARAMS )

        # Create leaf switches
        for ls in range(leaf):
            leafs[ls] = self.addSwitch( 'leaf%s' % (ls + 1),
                                        dpid="00000000000%s" % (ls + 1),
                                        **SWITCH_PARAMS )

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
                name = 'h%s%s' % (dual_ls * fanout + f + 1, "v6" if ipv6 else "")
                if ipv6:
                    ips = ['2000::%d0%d/%d' % (dual_ls+2, f+1, IP6_SUBNET_CLASS)]
                    gateway = '2000::%dff' % (dual_ls+2)
                    mac = '00:bb:00:00:00:%02x' % (dual_ls * fanout + f + 1)
                else:
                    ips = ['10.0.%d.%d/%d' % (dual_ls+2, f+1, IP4_SUBNET_CLASS)]
                    gateway = '10.0.%d.254' % (dual_ls+2)
                    mac = '00:aa:00:00:00:%02x' % (dual_ls * fanout + f + 1)
                host = self.addHost( name=name, cls=TrellisHost, ips=ips, gateway=gateway, mac=mac,
                                     vlan=vlan_id[ dual_ls*fanout + f ] if vlan_id[dual_ls * fanout + f] != 0 else None,
                                     dhcpClient=dhcp_client, ipv6=ipv6, dualHomed=True )
                self.addLink(host, leafs[ls], **linkopts)
                self.addLink(host, leafs[ls-1], **linkopts)

        last_ls = leafs[leaf-2]
        last_paired_ls = leafs[leaf-1]
        # Create common components
        # Control plane switch (for DHCP servers)
        cs1 = self.addSwitch('cs1', cls=OVSBridge)
        self.addLink(cs1, last_ls)

        # Control plane switch (for quagga fpm)
        cs0 = self.addSwitch('cs0', cls=OVSBridge)

        # Control plane NAT (for quagga fpm)
        nat = self.addHost('nat', cls=NAT,
                           ip='172.16.0.1/12',
                           subnet=str(ip_network(u'172.16.0.0/12')), inNamespace=False)
        self.addLink(cs0, nat)

        # Internal Quagga bgp1
        intfs = {'bgp1-eth0': {'ipAddrs': ['10.0.1.2/24', '2000::102/120'], 'mac': '00:88:00:00:00:03'},
                 'bgp1-eth1': {'ipAddrs': ['172.16.0.2/12']}}
        bgp1 = self.addHost('bgp1', cls=BgpRouter,
                            interfaces=intfs,
                            quaggaConfFile='./bgpdbgp1.conf',
                            zebraConfFile='./zebradbgp1.conf')
        self.addLink(bgp1, last_ls)
        self.addLink(bgp1, cs0)

        # Internal Quagga bgp2
        intfs = {'bgp2-eth0': [{'ipAddrs': ['10.0.5.2/24', '2000::502/120'], 'mac': '00:88:00:00:00:04', 'vlan': '150'},
                               {'ipAddrs': ['10.0.6.2/24', '2000::602/120'], 'mac': '00:88:00:00:00:04', 'vlan': '160'}],
                 'bgp2-eth1': {'ipAddrs': ['172.16.0.4/12']}}
        bgp2 = self.addHost('bgp2', cls=BgpRouter,
                            interfaces=intfs,
                            quaggaConfFile='./bgpdbgp2.conf',
                            zebraConfFile='./zebradbgp2.conf')
        self.addLink(bgp2, last_paired_ls)
        self.addLink(bgp2, cs0)

        # External Quagga r1
        intfs = {'r1-eth0': {'ipAddrs': ['10.0.1.1/24', '2000::101/120'], 'mac': '00:88:00:00:00:01'},
                 'r1-eth1': {'ipAddrs': ['10.0.5.1/24', '2000::501/120'], 'mac': '00:88:00:00:00:11'},
                 'r1-eth2': {'ipAddrs': ['10.0.99.1/16']}}
        r1 = self.addHost('r1', cls=BgpRouter,
                            interfaces=intfs,
                            quaggaConfFile='./bgpdr1.conf')
        self.addLink(r1, last_ls)
        self.addLink(r1, last_paired_ls)

        # External IPv4 Host behind r1
        rh1 = self.addHost('rh1', cls=TrellisHost, ips=['10.0.99.2/24'], gateway='10.0.99.1')
        self.addLink(r1, rh1)

        # External Quagga r2
        intfs = {'r2-eth0': {'ipAddrs': ['10.0.6.1/24', '2000::601/120'], 'mac': '00:88:00:00:00:02'},
                 'r2-eth1': {'ipAddrs': ['10.0.7.1/24', '2000::701/120'], 'mac': '00:88:00:00:00:22'},
                 'r2-eth2': {'ipAddrs': ['10.0.99.1/16']}}
        r2 = self.addHost('r2', cls=BgpRouter,
                            interfaces=intfs,
                            quaggaConfFile='./bgpdr2.conf')
        self.addLink(r2, last_ls)
        self.addLink(r2, last_paired_ls)

        # External IPv4 Host behind r2
        rh2 = self.addHost('rh2', cls=TrellisHost, ips=['10.0.99.2/24'], gateway='10.0.99.1')
        self.addLink(r2, rh2)

        # DHCP server
        if ipv6:
            dhcp = self.addHost('dhcp', cls=TrellisHost, mac='00:99:00:00:00:01',
                                ips=['2000::3fd/120'], gateway='2000::3ff',
                                dhcpServer=True, ipv6=True)
            self.addLink(dhcp, cs1)
        else:
            dhcp = self.addHost('dhcp', cls=TrellisHost, mac='00:99:00:00:00:01',
                                ips=['10.0.3.253/24'], gateway='10.0.3.254',
                                dhcpServer=True)
            self.addLink(dhcp, cs1)


class LeafSpineFabric (Topo) :
    def __init__(self, spine = 2, leaf = 2, fanout = 2, vlan_id = [], ipv6 = False,
                 dhcp_client = False, dhcp_relay = False,
                 multiple_server = False, remote_server = False, **opts):
        Topo.__init__(self, **opts)
        spines = dict()
        leafs = dict()

        # TODO: support IPv6 hosts
        linkopts = dict( bw=100 )

        # Create spine switches
        for s in range(spine):
            spines[s] = self.addSwitch( 'spine10%s' % (s + 1),
                                        dpid="00000000010%s" % (s + 1),
                                        **SWITCH_PARAMS )

        # Create leaf switches
        for ls in range(leaf):
            leafs[ls] = self.addSwitch( 'leaf%s' % (ls + 1),
                                        dpid="00000000000%s" % (ls + 1),
                                        **SWITCH_PARAMS )

            # Connect leaf to all spines
            for s in range( spine ):
                switch = spines[ s ]
                self.addLink( leafs[ ls ], switch, **linkopts )

            # If dual-homed ToR, add hosts only when adding second switch at each edge-pair
            # When the number of leaf switches is odd, leave the last switch as a single ToR

            # Add hosts
            for f in range(fanout):
                name = 'h%s%s' % (ls * fanout + f + 1, "v6" if ipv6 else "")
                if ipv6:
                    ips = ['2000::%d0%d/%d' % (ls+2, f+1, IP6_SUBNET_CLASS)]
                    gateway = '2000::%dff' % (ls+2)
                    mac = '00:bb:00:00:00:%02x' % (ls * fanout + f + 1)
                else:
                    ips = ['10.0.%d.%d/%d' % (ls+2, f+1, IP4_SUBNET_CLASS)]
                    gateway = '10.0.%d.254' % (ls+2)
                    mac = '00:aa:00:00:00:%02x' % (ls * fanout + f + 1)
                host = self.addHost( name=name, cls=TrellisHost, ips=ips, gateway=gateway, mac=mac,
                                     vlan=vlan_id[ ls*fanout + f ] if vlan_id[ls * fanout + f] != 0 else None,
                                     dhcpClient=dhcp_client, ipv6=ipv6 )
                if dhcp_relay and f % 2:
                    relayIndex = ls * fanout + f + 1
                    if ipv6:
                        intfs = {
                            'relay%s-eth0' % relayIndex: { 'ipAddrs': ['2000::%dff/%d' % (leaf + ls + 2, IP6_SUBNET_CLASS)] },
                            'relay%s-eth1' % relayIndex: { 'ipAddrs': ['2000::%d5%d/%d' % (ls + 2, f, IP6_SUBNET_CLASS)] }
                        }
                        if remote_server:
                            serverIp = '2000::99fd'
                        elif multiple_server:
                            serverIp = '2000::3fc'
                        else:
                            serverIp = '2000::3fd'
                        dhcpRelay = self.addHost(name='relay%s' % relayIndex, cls=DhcpRelay, serverIp=serverIp,
                                                 gateway='2000::%dff' % (ls+2), interfaces=intfs)
                    else:
                        intfs = {
                            'relay%s-eth0' % relayIndex: { 'ipAddrs': ['10.0.%d.254/%d' % (leaf + ls + 2, IP4_SUBNET_CLASS)] },
                            'relay%s-eth1' % relayIndex: { 'ipAddrs': ['10.0.%d.%d/%d' % (ls + 2, f + 99, IP4_SUBNET_CLASS)] }
                        }
                        if remote_server:
                            serverIp = '10.0.99.3'
                        elif multiple_server:
                            serverIp = '10.0.3.252'
                        else:
                            serverIp = '10.0.3.253'
                        dhcpRelay = self.addHost(name='relay%s' % relayIndex, cls=DhcpRelay, serverIp=serverIp,
                                                 gateway='10.0.%d.254' % (ls+2), interfaces=intfs)
                    self.addLink(host, dhcpRelay, **linkopts)
                    self.addLink(dhcpRelay, leafs[ls], **linkopts)
                else:
                    self.addLink(host, leafs[ls], **linkopts)

        last_ls = leafs[leaf-1]
        # Create common components
        # Control plane switch (for DHCP servers)
        cs1 = self.addSwitch('cs1', cls=OVSBridge)
        self.addLink(cs1, last_ls)

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
                            quaggaConfFile='./bgpdbgp1.conf',
                            zebraConfFile='./zebradbgp1.conf')
        self.addLink(bgp1, last_ls)
        self.addLink(bgp1, cs0)

        # External Quagga r1
        intfs = {'r1-eth0': {'ipAddrs': ['10.0.1.1/24', '2000::101/120'], 'mac': '00:88:00:00:00:01'},
                 'r1-eth1': {'ipAddrs': ['10.0.99.1/16']},
                 'r1-eth2': {'ipAddrs': ['2000::9901/120']}}
        r1 = self.addHost('r1', cls=BgpRouter,
                            interfaces=intfs,
                            quaggaConfFile='./bgpdr1.conf')
        self.addLink(r1, last_ls)

        # External switch behind r1
        rs0 = self.addSwitch('rs0', cls=OVSBridge)
        self.addLink(r1, rs0)

        # External IPv4 Host behind r1
        rh1 = self.addHost('rh1', cls=TrellisHost, ips=['10.0.99.2/24'], gateway='10.0.99.1')
        self.addLink(r1, rh1)

        # External IPv6 Host behind r1
        rh1v6 = self.addHost('rh1v6', cls=TrellisHost, ips=['2000::9902/120'], gateway='2000::9901')
        self.addLink(r1, rh1v6)

        # DHCP server
        if ipv6:
            if remote_server:
                dhcp = self.addHost('dhcp', cls=TrellisHost, mac='00:99:00:00:00:01',
                                    ips=['2000::99fd/120'], gateway='2000::9901',
                                    dhcpServer=True, ipv6=True)
                self.addLink(rs0, dhcp)
            else:
                dhcp = self.addHost('dhcp', cls=TrellisHost, mac='00:99:00:00:00:01',
                                    ips=['2000::3fd/120'], gateway='2000::3ff',
                                    dhcpServer=True, ipv6=True)
                self.addLink(dhcp, cs1)
                if multiple_server:
                    dhcp2 = self.addHost('dhcp2', cls=TrellisHost, mac='00:99:00:00:00:02',
                                         ips=['2000::3fc/120'], gateway='2000::3ff',
                                         dhcpServer=True, ipv6=True)
                    self.addLink(dhcp2, cs1)
        else:
            if remote_server:
                dhcp = self.addHost('dhcp', cls=TrellisHost, mac='00:99:00:00:00:01',
                                    ips=['10.0.99.3/24'], gateway='10.0.99.1',
                                    dhcpServer=True)
                self.addLink(rs0, dhcp)
            else:
                dhcp = self.addHost('dhcp', cls=TrellisHost, mac='00:99:00:00:00:01',
                                    ips=['10.0.3.253/24'], gateway='10.0.3.254',
                                    dhcpServer=True)
                self.addLink(dhcp, cs1)
                if multiple_server:
                    dhcp2 = self.addHost('dhcp2', cls=TrellisHost, mac='00:99:00:00:00:02',
                                         ips=['10.0.3.252/24'], gateway='10.0.3.254',
                                         dhcpServer=True)
                    self.addLink(dhcp2, cs1)

def config( opts ):
    spine = opts.spine
    leaf = opts.leaf
    fanout = opts.fanout
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

    if dualhomed:
        if leaf % 2 == 1 or leaf == 0:
            print "Even number of leaf switches (at least two) are needed to build dual-homed topology."
            return
        else:
            topo = DualHomedLeafSpineFabric(spine=spine, leaf=leaf, fanout=fanout, vlan_id=vlan,
                                            ipv6=opts.ipv6,
                                            dhcp_client=opts.dhcpClient,
                                            dhcp_relay=opts.dhcpRelay,
                                            multiple_server=opts.multipleServer,
                                            remote_server=opts.remoteServer)
    else:
        topo = LeafSpineFabric(spine=spine, leaf=leaf, fanout=fanout, vlan_id=vlan, ipv6=opts.ipv6,
                               dhcp_client=opts.dhcpClient,
                               dhcp_relay=opts.dhcpRelay,
                               multiple_server=opts.multipleServer,
                               remote_server=opts.remoteServer)

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
