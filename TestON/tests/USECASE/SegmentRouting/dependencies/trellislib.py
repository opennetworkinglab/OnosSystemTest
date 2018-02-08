#!/usr/bin/python

"""
Libraries for Trellis hosts.
"""

import sys
sys.path.append('..')
from mininet.node import Host
from routinglib import RoutedHost, RoutedHost6, Router

class TaggedRoutedHost(RoutedHost):
    """Host that can be configured with multiple IP addresses."""
    def __init__(self, name, ips, gateway, vlan, *args, **kwargs):
        super(RoutedHost, self).__init__(name, *args, **kwargs)
        self.ips = ips
        self.gateway = gateway
        self.vlan = vlan
        self.vlanIntf = None

    def config(self, **kwargs):
        Host.config(self, **kwargs)
        intf = self.defaultIntf()
        self.vlanIntf = "%s.%s" % (intf, self.vlan)
        self.cmd('ip -4 addr flush dev %s' % intf)
        self.cmd('ip link add link %s name %s type vlan id %s' % (intf, self.vlanIntf, self.vlan))
        self.cmd('ip link set up %s' % self.vlanIntf)

        for ip in self.ips:
            self.cmd('ip addr add %s dev %s' % (ip, self.vlanIntf))

        self.cmd('ip route add default via %s' % self.gateway)
        intf.name = self.vlanIntf
        self.nameToIntf[self.vlanIntf] = intf

    def terminate(self, **kwargs):
        self.cmd('ip link remove link %s' % self.vlanIntf)
        super(TaggedRoutedHost, self).terminate()

class DualHomedRoutedHost(Host):
    def __init__(self, name, ips, gateway, *args, **kwargs):
        super(DualHomedRoutedHost, self).__init__(name, **kwargs)
        self.bond0 = None
        self.ips = ips
        self.gateway = gateway

    def config(self, **kwargs):
        super(DualHomedRoutedHost, self).config(**kwargs)
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

        for ip in self.ips:
            self.cmd('ip addr add %s dev %s' % (ip, self.bond0))

        self.cmd('ip route add default via %s' % self.gateway)
        default_intf = self.defaultIntf()
        default_intf.name = self.bond0
        self.nameToIntf[self.bond0] = default_intf

    def terminate(self, **kwargs):
        self.cmd('ip link set %s down' % self.bond0)
        self.cmd('ip link delete %s' % self.bond0)
        super(DualHomedRoutedHost, self).terminate()

class DualHomedTaggedRoutedHost(DualHomedRoutedHost):
    def __init__(self, name, ips, gateway, vlan, *args, **kwargs):
        super(DualHomedTaggedRoutedHost, self).__init__(name, ips, gateway, *args, **kwargs)
        self.ips = ips
        self.gateway = gateway
        self.vlan = vlan
        self.vlanIntf = None

    def config(self, **kwargs):
        super(DualHomedTaggedRoutedHost, self).config(**kwargs)
        default_intf = self.defaultIntf()
        self.vlanIntf = "%s.%s" % (default_intf, self.vlan)
        self.cmd('ip -4 addr flush dev %s' % default_intf)
        self.cmd('ip link add link %s name %s type vlan id %s' % (default_intf, self.vlanIntf, self.vlan))
        self.cmd('ip link set up %s' % self.vlanIntf)

        for ip in self.ips:
            self.cmd('ip addr add %s dev %s' % (ip, self.vlanIntf))

        self.cmd('ip route add default via %s' % self.gateway)
        default_intf.name = self.vlanIntf
        self.nameToIntf[self.vlanIntf] = default_intf

    def terminate(self, **kwargs):
        self.cmd('ip link remove link %s' % self.vlanIntf)
        super(DualHomedTaggedRoutedHost, self).terminate()

class DhcpClient(Host):
    def __init__(self, name, *args, **kwargs):
        super(DhcpClient, self).__init__(name, **kwargs)
        self.pidFile = '/run/dhclient-%s.pid' % self.name
        self.leaseFile = '/var/lib/dhcp/dhcpclient-%s.lease' % (self.name, )

    def config(self, **kwargs):
        super(DhcpClient, self).config(**kwargs)
        self.cmd('ip addr flush dev %s' % self.defaultIntf())
        self.cmd('dhclient -q -4 -nw -pf %s -lf %s %s' % (self.pidFile, self.leaseFile, self.defaultIntf()))

    def terminate(self, **kwargs):
        self.cmd('kill -9 `cat %s`' % self.pidFile)
        self.cmd('rm -rf %s' % self.pidFile)
        super(DhcpClient, self).terminate()

class Dhcp6Client(Host):
    def __init__(self, name, *args, **kwargs):
        super(Dhcp6Client, self).__init__(name, **kwargs)
        self.pidFile = '/run/dhclient-%s.pid' % self.name
        self.leaseFile = '/var/lib/dhcp/dhcpclient6-%s.lease' % (self.name, )

    def config(self, **kwargs):
        super(Dhcp6Client, self).config(**kwargs)
        self.cmd('ip -4 addr flush dev %s' % self.defaultIntf())
        self.cmd('dhclient -q -6 -nw -pf %s -lf %s %s' % (self.pidFile, self.leaseFile, self.defaultIntf()))

    def terminate(self, **kwargs):
        self.cmd('kill -9 `cat %s`' % self.pidFile)
        self.cmd('rm -rf %s' % self.pidFile)
        super(Dhcp6Client, self).terminate()

class DhcpServer(RoutedHost):
    binFile = '/usr/sbin/dhcpd'
    pidFile = '/run/dhcp-server-dhcpd.pid'
    configFile = './dhcpd.conf'
    leasesFile = '/var/lib/dhcp/dhcpd.leases'

    def config(self, **kwargs):
        super(DhcpServer, self).config(**kwargs)
        self.cmd('touch %s' % self.leasesFile)
        self.cmd('%s -q -4 -pf %s -cf %s %s' % (self.binFile, self.pidFile, self.configFile, self.defaultIntf()))

    def terminate(self, **kwargs):
        self.cmd('kill -9 `cat %s`' % self.pidFile)
        self.cmd('rm -rf %s' % self.pidFile)
        super(DhcpServer, self).terminate()

class Dhcp6Server(RoutedHost6):
    binFile = '/usr/sbin/dhcpd'
    pidFile = '/run/dhcp-server-dhcpd6.pid'
    configFile = './dhcpd6.conf'
    leasesFile = '/var/lib/dhcp/dhcpd6.leases'

    def config(self, **kwargs):
        super(Dhcp6Server, self).config(**kwargs)
        linkLocalAddr = mac_to_ipv6_linklocal(kwargs['mac'])
        self.cmd('ip -6 addr add dev %s scope link %s' % (self.defaultIntf(), linkLocalAddr))
        self.cmd('touch %s' % self.leasesFile)
        self.cmd('%s -q -6 -pf %s -cf %s %s' % (self.binFile, self.pidFile, self.configFile, self.defaultIntf()))

    def terminate(self, **kwargs):
        self.cmd('kill -9 `cat %s`' % self.pidFile)
        self.cmd('rm -rf %s' % self.pidFile)
        self.cmd('rm -rf  %s' % self.leasesFile)
        super(Dhcp6Server, self).terminate()

class DhcpRelay(Router):
    binFile = '/usr/sbin/dhcrelay'
    pidFile = '/run/dhcp-relay.pid'
    serverIp = None
    gateway = None

    def __init__(self, name, serverIp, gateway, *args, **kwargs):
        super(DhcpRelay, self).__init__(name, **kwargs)
        self.serverIp = serverIp
        self.gateway = gateway

    def config(self, **kwargs):
        super(DhcpRelay, self).config(**kwargs)
        ifacesStr = ' '.join(["-i " + ifaceName for ifaceName in self.interfaces.keys()])
        self.cmd('route add default gw %s' % self.gateway)
        self.cmd('%s -4 -a -pf %s %s %s' % (self.binFile, self.pidFile, ifacesStr, self.serverIp))

    def terminate(self, **kwargs):
        self.cmd('kill -9 `cat %s`', self.pidFile)
        self.cmd('rm -rf %s' % self.pidFile)
        super(DhcpRelay, self).terminate()

class TaggedDhcpClient(Host):
    def __init__(self, name, vlan, *args, **kwargs):
        super(TaggedDhcpClient, self).__init__(name, **kwargs)
        self.pidFile = '/run/dhclient-%s.pid' % self.name
        self.vlan = vlan
        self.vlanIntf = None

    def config(self, **kwargs):
        super(TaggedDhcpClient, self).config(**kwargs)
        self.vlanIntf = "%s.%s" % (self.defaultIntf(), self.vlan)
        self.cmd('ip addr flush dev %s' % self.defaultIntf())
        self.cmd('ip link add link %s name %s type vlan id %s' % (self.defaultIntf(), self.vlanIntf, self.vlan))
        self.cmd('ip link set up %s' % self.vlanIntf)
        self.cmd('dhclient -q -4 -nw -pf %s %s' % (self.pidFile, self.vlanIntf))

    def terminate(self, **kwargs):
        self.cmd('kill -9 `cat %s`' % self.pidFile)
        self.cmd('rm -rf %s' % self.pidFile)
        self.cmd('ip link remove link %s' % self.vlanIntf)
        super(TaggedDhcpClient, self).terminate()

class TaggedDhcpServer(TaggedRoutedHost):
    binFile = '/usr/sbin/dhcpd'
    pidFile = '/run/dhcp-server/dhcpd.pid'
    configFile = './dhcpd.conf'

    def config(self, **kwargs):
        super(TaggedDhcpServer, self).config(**kwargs)
        self.cmd('%s -q -4 -pf %s -cf %s %s' % (self.binFile, self.pidFile, self.configFile, self.vlanIntf))

    def terminate(self, **kwargs):
        self.cmd('kill -9 `cat %s`' % self.pidFile)
        self.cmd('rm -rf %s' % self.pidFile)
        super(TaggedDhcpServer, self).terminate()

class DualHomedDhcpClient(Host):
    def __init__(self, name, *args, **kwargs):
        super(DualHomedDhcpClient, self).__init__(name, **kwargs)
        self.pidFile = '/run/dhclient-%s.pid' % self.name
        self.bond0 = None

    def config(self, **kwargs):
        super(DualHomedDhcpClient, self).config(**kwargs)
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
        self.cmd('dhclient -q -4 -nw -pf %s %s' % (self.pidFile, self.bond0))

    def terminate(self, **kwargs):
        self.cmd('ip link set %s down' % self.bond0)
        self.cmd('ip link delete %s' % self.bond0)
        self.cmd('kill -9 `cat %s`' % self.pidFile)
        self.cmd('rm -rf %s' % self.pidFile)
        super(DualHomedDhcpClient, self).terminate()

class TrellisHost(Host):
    def __init__(self, name, ips=[], gateway="", dualHomed=False, vlan=None, dhcpClient=False, dhcpServer=False, ipv6=False, *args, **kwargs):
        super(TrellisHost, self).__init__(name, *args, **kwargs)
        self.dualHomed = dualHomed
        self.bond0 = None
        self.vlan = vlan
        self.vlanIntf = None
        self.dhcpClient = dhcpClient
        self.dhcpServer = dhcpServer
        if dhcpClient:
            self.pidFile = '/run/dhclient-%s.pid' % self.name
            self.leaseFile = '/var/lib/dhcp/dhcpclient%s-%s.lease' % ("6" if ipv6 else "", self.name)
        else:
            self.ips = ips
            self.gateway = gateway
            if dhcpServer:
                self.binFile = '/usr/sbin/dhcpd'
                self.pidFile = '/run/dhcp-server-dhcpd%s.pid' % ("6" if ipv6 else "")
                self.configFile = './dhcpd%s.conf' % ("6" if ipv6 else "")
                self.leasesFile = '/var/lib/dhcp/dhcpd%s.leases' % ("6" if ipv6 else "")
        self.ipv6 = ipv6

    def config(self, **kwargs):
        super(TrellisHost, self).config(**kwargs)

        if self.dualHomed:
            # Setup bond0 interface
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
            defaultIntf = self.defaultIntf()
            defaultIntf.name = self.bond0
            self.nameToIntf[self.bond0] = defaultIntf

        self.cmd('ip %s addr flush dev %s' % ("-4" if self.ipv6 else "", self.defaultIntf()))

        if self.vlan:
            # Setup vlan interface
            defaultIntf = self.defaultIntf()
            self.vlanIntf = "%s.%s" % (defaultIntf, self.vlan)
            self.cmd('ip link add link %s name %s type vlan id %s' % (defaultIntf, self.vlanIntf, self.vlan))
            self.cmd('ip link set up %s' % self.vlanIntf)
            defaultIntf.name = self.vlanIntf
            self.nameToIntf[self.vlanIntf] = defaultIntf

        if self.dhcpClient:
            if self.vlan or self.dualHomed:
                # Why leaseFile is not required here?
                self.cmd('dhclient -q -%s -nw -pf %s %s' % (6 if self.ipv6 else 4, self.pidFile, self.defaultIntf()))
            else:
                self.cmd('dhclient -q -%s -nw -pf %s -lf %s %s' % (6 if self.ipv6 else 4, self.pidFile, self.leaseFile, self.defaultIntf()))
        else:
            # Setup IP addresses
            for ip in self.ips:
                self.cmd('ip addr add %s dev %s' % (ip, self.defaultIntf()))
            self.cmd('ip route add default via %s' % self.gateway)

            if self.dhcpServer:
                if self.ipv6:
                    linkLocalAddr = mac_to_ipv6_linklocal(kwargs['mac'])
                    self.cmd('ip -6 addr add dev %s scope link %s' % (self.defaultIntf(), linkLocalAddr))
                self.cmd('touch %s' % self.leasesFile)
                self.cmd('%s -q -%s -pf %s -cf %s %s' % (self.binFile, 6 if self.ipv6 else 4, self.pidFile, self.configFile, self.defaultIntf()))

    def terminate(self, **kwargs):
        if self.vlan:
            self.cmd('ip link remove link %s' % self.vlanIntf)
        if self.dualHomed:
            self.cmd('ip link set %s down' % self.bond0)
            self.cmd('ip link delete %s' % self.bond0)
        if self.dhcpClient:
            self.cmd('kill -9 `cat %s`' % self.pidFile)
            self.cmd('rm -rf %s' % self.pidFile)
        if self.dhcpServer:
            self.cmd('kill -9 `cat %s`' % self.pidFile)
            self.cmd('rm -rf %s' % self.pidFile)
        super(TrellisHost, self).terminate()

# Utility for IPv6
def mac_to_ipv6_linklocal(mac):
    '''
    Convert mac address to link-local IPv6 address
    '''
    # Remove the most common delimiters; dots, dashes, etc.
    mac_value = int(mac.translate(None, ' .:-'), 16)

    # Split out the bytes that slot into the IPv6 address
    # XOR the most significant byte with 0x02, inverting the
    # Universal / Local bit
    high2 = mac_value >> 32 & 0xffff ^ 0x0200
    high1 = mac_value >> 24 & 0xff
    low1 = mac_value >> 16 & 0xff
    low2 = mac_value & 0xffff

    return 'fe80::{:04x}:{:02x}ff:fe{:02x}:{:04x}'.format(high2, high1, low1, low2)
