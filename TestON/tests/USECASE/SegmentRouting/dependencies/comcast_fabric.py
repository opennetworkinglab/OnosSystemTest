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
from trellislib import DhcpServer, TaggedRoutedHost, DualHomedRoutedHost, DualHomedTaggedRoutedHost, DhcpClient, Dhcp6Client, DhcpServer, Dhcp6Server

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

    ( options, args ) = parser.parse_args()
    return options, args

opts, args = parseOptions()

class DualHomedTaggedHostWithIpv4(Host):

    def __init__(self, name, ip, gateway, dhcp, vlan, *args, **kwargs):
        super(DualHomedTaggedHostWithIpv4, self).__init__(name, **kwargs)
        self.bond0 = None
        self.ip = ip
        self.gateway = gateway
        self.dhcp = dhcp
        self.vlan = vlan

    def config(self, **kwargs):
        super(DualHomedTaggedHostWithIpv4, self).config(**kwargs)
        intf0 = self.intfs[0].name
        intf1 = self.intfs[1].name

        self.bond0 = "%s-bond0" % self.name
        self.vlanBondIntf = "%s.%s" % (self.bond0, self.vlan)

        self.cmd('modprobe bonding')
        self.cmd('ip link add %s type bond' % self.bond0)
        self.cmd('ip link set %s down' % intf0)
        self.cmd('ip link set %s down' % intf1)
        self.cmd('ip link set %s master %s' % (intf0, self.bond0))
        self.cmd('ip link set %s master %s' % (intf1, self.bond0))
        self.cmd('ip addr flush dev %s' % intf0)
        self.cmd('ip addr flush dev %s' % intf1)
        self.cmd('ip link set %s up' % self.bond0)

        self.cmd('ip link add link %s name %s type vlan id %s' % (self.bond0,
                                                                  self.vlanBondIntf, self.vlan))

        self.cmd('ip link set up %s' % self.vlanBondIntf)
        self.cmd('ip addr add %s/24 dev %s' % (self.ip, self.vlanBondIntf))
        self.cmd('ip route add default via %s' % self.gateway)

        default_intf = self.defaultIntf()
        default_intf.name = self.bond0
        self.nameToIntf[self.bond0] = default_intf

    def terminate(self, **kwargs):
        self.cmd('ip link set %s down' % self.bond0)
        self.cmd('ip link delete %s' % self.bond0)
        super(DualHomedTaggedHostWithIpv4, self).terminate()

class DualHomedUntaggedHostWithIpv4(Host):

    def __init__(self, name, ip, gateway, dhcp, *args, **kwargs):
        super(DualHomedUntaggedHostWithIpv4, self).__init__(name, **kwargs)
        self.bond0 = None
        self.ip = ip
        self.gateway = gateway
        self.dhcp = dhcp

    def config(self, **kwargs):
        super(DualHomedUntaggedHostWithIpv4, self).config(**kwargs)
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
        self.cmd('ip addr add %s/24 dev %s' % (self.ip, self.bond0))
        self.cmd('ip route add default via %s' % self.gateway)

        default_intf = self.defaultIntf()
        default_intf.name = self.bond0
        self.nameToIntf[self.bond0] = default_intf

    def terminate(self, **kwargs):
        self.cmd('ip link set %s down' % self.bond0)
        self.cmd('ip link delete %s' % self.bond0)
        super(DualHomedUntaggedHostWithIpv4, self).terminate()

class TaggedHostWithIpv4(Host):
    '''
        Tagged host configured with a static ip address.
    '''
    def __init__(self, name, ip, gateway, dhcp, vlan, *args, **kwargs):
        super(TaggedHostWithIpv4, self).__init__(name, *args, **kwargs)
        self.ip = ip
        self.gateway = gateway
        self.vlan = vlan
        self.vlanIntf = None
        self.dhcp = dhcp

    def config(self, **kwargs):
        Host.config(self, **kwargs)

        intf = self.defaultIntf()
        self.vlanIntf = "%s.%s" % (intf, self.vlan)
        self.cmd('ip -4 addr flush dev %s' % intf)
        self.cmd('ip link add link %s name %s type vlan id %s' % (intf, self.vlanIntf, self.vlan))
        self.cmd('ip link set up %s' % self.vlanIntf)
        self.cmd('ip addr add %s/24 dev %s' % (self.ip, self.vlanIntf))
        self.cmd('ip route add default via %s' % self.gateway)
        intf.name = self.vlanIntf
        self.nameToIntf[self.vlanIntf] = intf

    def terminate(self, **kwargs):
        self.cmd('ip link remove link %s' % self.vlanIntf)
        super(TaggedHostWithIpv4, self).terminate()


class UnTaggedHostWithIpv4(Host):
    '''
        Untagged host configured with a static ip address.
    '''
    def __init__(self, name, ip, gateway, dhcp, *args, **kwargs):
        super(UnTaggedHostWithIpv4, self).__init__(name, *args, **kwargs)
        self.ip = ip
        self.gateway = gateway
        self.dhcp = dhcp

    def config(self, **kwargs):
        Host.config(self, **kwargs)

        intf = self.defaultIntf()
        self.cmd('ip -4 addr flush dev %s' % intf)
        self.cmd('ip addr add %s/24 dev %s' % (self.ip, intf))
        self.cmd('ip route add default via %s' % self.gateway)

    def terminate(self, **kwargs):
        super(UnTaggedHostWithIpv4, self).terminate()

class ComcastLeafSpineFabric(Topo):

    spines = dict()
    leafs = dict()
    hosts_dict = dict()

    def createIpv4Hosts(self, dhcp):

        h1 = self.addHost('h1v4', cls=UnTaggedHostWithIpv4,
                          mac='00:aa:00:00:00:01', ip='10.1.0.1',
                          gateway='10.1.0.254', dhcp=dhcp)
        self.addLink(h1, self.leafs[0])
        self.hosts_dict['h1v4'] = h1

        h2 = self.addHost('h2v4', cls=UnTaggedHostWithIpv4,
                          mac='00:aa:00:00:01:01', ip='10.1.10.1',
                          gateway='10.1.10.254', dhcp=dhcp)
        self.addLink(h2, self.leafs[0])
        self.hosts_dict['h2v4'] = h2

        h3 = self.addHost('h3v4', cls=UnTaggedHostWithIpv4,
                          mac='00:aa:00:00:00:02', ip='10.2.0.1',
                          gateway='10.2.0.254', dhcp=dhcp)
        self.addLink(h3, self.leafs[1])
        self.hosts_dict['h3v4'] = h3

        h4 = self.addHost('h4v4', cls=DualHomedUntaggedHostWithIpv4,
                          mac='00:aa:00:00:00:03', ip='10.2.30.1',
                          gateway='10.2.30.254', dhcp=dhcp)
        self.addLink(h4, self.leafs[1])
        self.addLink(h4, self.leafs[2])
        self.hosts_dict['h4v4'] = h4

        h5 = self.addHost('h5v4', cls=DualHomedTaggedHostWithIpv4,
                          mac='00:aa:00:00:00:04', ip='10.2.20.1',
                          gateway='10.2.20.254', dhcp=dhcp, vlan=30)
        self.addLink(h5, self.leafs[1])
        self.addLink(h5, self.leafs[2])
        self.hosts_dict['h5v4'] = h5

        h6 = self.addHost('h6v4', cls=TaggedHostWithIpv4,
                          mac='00:aa:00:00:00:05', ip='10.2.10.1',
                          gateway='10.2.10.254', dhcp=dhcp, vlan=20)
        self.addLink(h6, self.leafs[2])
        self.hosts_dict['h6v4'] = h6

        h7 = self.addHost('h7v4', cls=TaggedHostWithIpv4,
                          mac='00:aa:00:00:01:05', ip='10.2.40.1',
                          gateway='10.2.40.254', dhcp=dhcp, vlan=40)
        self.addLink(h7, self.leafs[2])
        self.hosts_dict['h7v4'] = h7

        h8 = self.addHost('h8v4', cls=TaggedHostWithIpv4,
                          mac='00:aa:00:00:00:06', ip='10.3.0.1',
                          gateway='10.3.0.254', dhcp=dhcp, vlan=30)
        self.addLink(h8, self.leafs[3])
        self.hosts_dict['h8v4'] = h8

        h9 = self.addHost('h9v4', cls=DualHomedTaggedHostWithIpv4,
                          mac='00:aa:00:00:00:07', ip='10.3.10.1',
                          gateway='10.3.10.254', dhcp=dhcp, vlan=40)
        self.addLink(h9, self.leafs[3])
        self.addLink(h9, self.leafs[4])
        self.hosts_dict['h9v4'] = h9

        h10 = self.addHost('h10v4', cls=DualHomedTaggedHostWithIpv4,
                           mac='00:aa:00:00:00:08', ip='10.3.30.1',
                           gateway='10.3.30.254', dhcp=dhcp, vlan=40)
        self.addLink(h10, self.leafs[3])
        self.addLink(h10, self.leafs[4])
        self.hosts_dict['h10v4'] = h10

        h11 = self.addHost('h11v4', cls=TaggedHostWithIpv4,
                           mac='00:aa:00:00:00:0a', ip='10.3.20.1',
                           gateway='10.3.20.254', dhcp=dhcp, vlan=40)
        self.addLink(h11, self.leafs[4])
        self.hosts_dict['h11v4'] = h11

        return

    def createIpv6Hosts(self, dhcp):
        print("NYI")
        return

    '''
    Creates the topology employed by Comcast which is a 2x5
    leaf spine traffic.

            S1  S2

    L1      L2 L3       L4 L5

    Where L2/L3 and L4/L5 are paired switches.
    Parameters for this topology :
        dhcp = True/False : set up dhcp servers
        routers = True/False : set up external routers
    '''
    def __init__(self, dhcp=False, routers=False, ipv4=False, ipv6=False, **opts):
        Topo.__init__(self, **opts)

        # TODO: support IPv6 hosts
        linkopts = dict( bw=10 )

        spine = 2
        leaf = 5

        # Create spine switches
        for s in range(spine):
            self.spines[s] = self.addSwitch('spine10%s' % (s + 1), dpid = "00000000010%s" % (s + 1) )

        # Create leaf switches
        for ls in range(leaf):
            self.leafs[ls] = self.addSwitch('leaf%s' % (ls + 1), dpid = "00000000000%s" % ( ls + 1) )

        # connecting leaf and spines, leafs 1-5 have double links
        for s in range( spine ):
            spine_switch = self.spines[s]

            for ls in range( leaf ):
                leaf_switch = self.leafs[ls]

                self.addLink( spine_switch, leaf_switch, **linkopts )
                if ls > 0:
                    self.addLink( spine_switch, leaf_switch, **linkopts )

        # connect paired leafs
        self.addLink(self.leafs[1], self.leafs[2], **linkopts)
        self.addLink(self.leafs[3], self.leafs[4], **linkopts)

        # create hosts
        if ipv6:
            self.createIpv6Hosts(dhcp)

        if ipv4:
            self.createIpv4Hosts(dhcp)

        if not ipv4 and not ipv6:
            print("No hosts were created!")

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

