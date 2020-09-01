#!/usr/bin/python

"""
Copyright 2016 Open Networking Foundation ( ONF )

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
import os
import re
import math
from optparse import OptionParser
from ipaddress import IPv6Network, IPv4Network
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import RemoteController, Host, OVSBridge, OVSSwitch
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI

from bmv2 import ONOSBmv2Switch
from stratum import StratumBmv2Switch

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
    parser.add_option( '--vlan', dest='vlan', type='int', default=-1,
                       help='vid of cross connect, default=-1, -1 means utilize default value' )
    parser.add_option( '--ipv6', action="store_true", dest='ipv6',
                       help='hosts are capable to use also ipv6' )
    parser.add_option( '--switch', dest='switch', type='str', default='ovs',
                       help='Switch type: ovs, bmv2 (with fabric.p4), stratum' )
    ( options, args ) = parser.parse_args()
    return options, args


opts, args = parseOptions()

FABRIC_PIPECONF = "org.onosproject.pipelines.fabric"

SWITCH_TO_PARAMS_DICT = {
    "ovs": dict(cls=OVSSwitch),
    "bmv2": dict(cls=ONOSBmv2Switch, pipeconf=FABRIC_PIPECONF),
    "stratum": dict(cls=StratumBmv2Switch, pipeconf=FABRIC_PIPECONF, loglevel='debug')
}
if opts.switch not in SWITCH_TO_PARAMS_DICT:
    raise Exception("Unknown switch type '%s'" % opts.switch)
SWITCH_PARAMS = SWITCH_TO_PARAMS_DICT[opts.switch]

IP6_SUBNET_CLASS = 120
IP4_SUBNET_CLASS = 24

class LeafAndSpine6( Topo ):

    """
    Create Leaf and Spine Topology for IPv4/IPv6 tests.
    """
    def __init__( self, spine=2, leaf=2, fanout=2, **opts ):
        Topo.__init__( self, **opts )
        spines = {}
        leafs = {}
        """
        We calculate the offset from /120 and from /24 in order to have
        a number of /120 and /24 subnets == leaf
        """
        offset = int( math.ceil( math.sqrt( leaf ) ) )
        """
        We calculate the subnets to use and set options
        """
        ipv6SubnetClass = unicode( '2000::/%s' % ( IP6_SUBNET_CLASS - offset ) )
        ipv6Subnets = list( IPv6Network( ipv6SubnetClass ).subnets( new_prefix=IP6_SUBNET_CLASS ) )
        ipv4SubnetClass = unicode( '10.0.0.0/%s' % ( IP4_SUBNET_CLASS - offset ) )
        ipv4Subnets = list( IPv4Network( ipv4SubnetClass ).subnets( new_prefix=IP4_SUBNET_CLASS ) )
        linkopts = dict( bw=100 )
        """
        We create the spine switches
        """
        for s in range( spine ):
            spines[ s ] = self.addSwitch( 'spine10%s' % ( s + 1 ),
                                          dpid="00000000010%s" % ( s + 1 ) )
        """
        We create the leaf switches
        """
        for ls in range( leaf ):
            leafs[ ls ] = self.addSwitch( 'leaf%s' % ( ls + 1 ),
                                          dpid="00000000000%s" % ( 1 + ls ) )
            ipv6Subnet = ipv6Subnets[ ls ]
            ipv6Hosts = list( ipv6Subnet.hosts() )
            ipv4Subnet = ipv4Subnets[ ls ]
            ipv4Hosts = list( ipv4Subnet.hosts() )
            """
            We add the hosts
            """
            for f in range( fanout ):
                ipv6 = ipv6Hosts[ f ]
                ipv6Gateway = ipv6Hosts[ len( ipv6Hosts ) - 1 ]
                ipv4 = ipv4Hosts[ f ]
                ipv4Gateway = ipv4Hosts[ len( ipv4Hosts ) - 1 ]
                host = self.addHost(
                    name='h%s' % ( ls * fanout + f + 1 ),
                    cls=Ipv6Host,
                    ip="%s/%s" % ( ipv4, IP4_SUBNET_CLASS ),
                    gateway='%s' % ipv4Gateway,
                    ipv6="%s/%s" % ( ipv6, IP6_SUBNET_CLASS ),
                    ipv6Gateway="%s" % ipv6Gateway
                )
                self.addLink( host, leafs[ ls ], **linkopts )
            """
            Connect leaf to all spines
            """
            for s in range( spine ):
                switch = spines[ s ]
                self.addLink( leafs[ ls ], switch, **linkopts )


class LeafAndSpine( Topo ):

    def __init__( self, spine=2, leaf=2, fanout=2, **opts ):
        "Create Leaf and Spine Topo."
        Topo.__init__( self, **opts )
        # Add spine switches
        spines = {}
        leafs = {}
        for s in range( spine ):
            spines[ s ] = self.addSwitch( 'spine10%s' % ( s + 1 ),
                                          dpid="00000000010%s" % ( s + 1 ),
                                          **SWITCH_PARAMS )
        # Set link speeds to 100Mb/s
        linkopts = dict( bw=100 )
        # Add Leaf switches
        for ls in range( leaf ):
            leafs[ ls ] = self.addSwitch( 'leaf%s' % ( ls + 1 ),
                                          dpid="00000000000%s" % ( 1 + ls ),
                                          **SWITCH_PARAMS )
            # Add hosts under a leaf, fanout hosts per leaf switch
            for f in range( fanout ):
                host = self.addHost( 'h%s' % ( ls * fanout + f + 1 ),
                                     cls=IpHost,
                                     ip='10.0.%s.%s/24' % ( ( ls + 1 ), ( f + 1 ) ),
                                     gateway='10.0.%s.254' % ( ls + 1 ) )
                self.addLink( host, leafs[ ls ], **linkopts )
                # Add Xconnect simulation
            if ls is 0:
                in1 = self.addHost( 'in1', cls=IpHost, ip='10.0.1.9/24', mac="00:00:00:00:00:09" )
                self.addLink( in1, leafs[ 0 ], **linkopts )
                out1 = self.addHost( 'out1', cls=IpHost, ip='10.0.9.1/24', mac="00:00:00:00:09:01" )
                self.addLink( out1, leafs[ 0 ], **linkopts )
                br1 = self.addSwitch( 'br1', cls=OVSBridge )
                self.addLink( br1, leafs[ 0 ], **linkopts )
                vlans = [ 1, 5, 10 ]
                for vid in vlans:
                    olt = self.addHost( 'olt%s' % vid, cls=VLANHost, vlan=vid,
                                        ip="10.%s.0.1/24" % vid, mac="00:00:%02d:00:00:01" % vid )
                    vsg = self.addHost( 'vsg%s' % vid, cls=VLANHost, vlan=vid,
                                        ip="10.%s.0.2/24" % vid, mac="00:00:%02d:00:00:02" % vid )
                    self.addLink( olt, leafs[ 0 ], **linkopts )
                    self.addLink( vsg, br1, **linkopts )
            # Connect leaf to all spines
            for s in range( spine ):
                switch = spines[ s ]
                self.addLink( leafs[ ls ], switch, **linkopts )


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


class Ipv6Host( IpHost ):

    """
    Abstraction to model an augmented host with a ipv6
    functionalities as well
    """
    def __init__( self, name, *args, **kwargs ):
        IpHost.__init__( self, name, *args, **kwargs )

    def config( self, **kwargs ):
        IpHost.config( self, **kwargs )
        ipv6Cmd = 'ifconfig %s-eth0 inet6 add %s' % ( self.name, kwargs[ 'ipv6' ] )
        ipv6GatewayCmd = 'ip -6 route add default via %s' % kwargs[ 'ipv6Gateway' ]
        ipv6MtuCmd = 'ifconfig %s-eth0 inet6 mtu 1490' % ( self.name )
        self.cmd( ipv6Cmd )
        self.cmd( ipv6GatewayCmd )
        self.cmd( ipv6MtuCmd )


class VLANHost( Host ):

    "Host connected to VLAN interface"

    def config( self, vlan=100, **params ):
        """Configure VLANHost according to ( optional ) parameters:
           vlan: VLAN ID for default interface"""
        r = super( VLANHost, self ).config( **params )
        intf = self.defaultIntf()
        # remove IP from default, "physical" interface
        self.cmd( 'ifconfig %s inet 0' % intf )
        intf = self.defaultIntf()
        # create VLAN interface
        self.cmd( 'vconfig add %s %d' % ( intf, vlan ) )
        self.cmd( 'ifconfig %s.%d %s' % ( intf, vlan, params[ 'ip' ] ) )
        # update the intf name and host's intf map
        self.cmd( 'ifconfig %s.%d mtu 1480' % ( intf, vlan ) )
        newName = '%s.%d' % ( intf, vlan )
        # update the ( Mininet ) interface to refer to VLAN interface name
        intf.name = newName
        # add VLAN interface to host's name to intf map
        self.nameToIntf[ newName ] = intf


class ExtendedCLI( CLI ):

    """
    Extends mininet CLI with the following commands:
    addvlanhost
    addiphost
    """
    def do_addhost( self, line ):
        # Parsing args from CLI
        args = line.split()
        if len( args ) < 3 or len( args ):
            "usage: addhost hostname switch **params"
        hostname, switch = args[ 0 ], args[ 1 ]
        params = eval( line.split( ' ', 3 )[ 2 ] )
        if 'cls' in params:
            params[ 'cls' ] = eval( params[ 'cls' ] )
        if hostname in self.mn:
            # error( '%s already exists!\n' % hostname )
            return
        if switch not in self.mn:
            # error( '%s does not exist!\n' % switch )
            return
        print params
        host = self.mn.addHostCfg( hostname, **params )
        # switch.attach( link.intf2 )
        # host.config()
        link = self.mn.addLink( host, switch )
        host.config( **params )

    def do_pingall6( self, line ):
        "Ping6 between all hosts."
        self.mn.pingAll6( line )


def config( opts ):
    spine = opts.spine
    leaf = opts.leaf
    fanout = opts.fanout
    vlan = opts.vlan
    ipv6 = opts.ipv6
    if opts.onosIp != '':
        controllers = opts.onosIp.split( ',' )
    else:
        controllers = ['127.0.0.1']

    if not ipv6:
        topo = LeafAndSpine(
            spine=spine,
            leaf=leaf,
            fanout=fanout,
            vlan=vlan,
        )
    else:
        topo = LeafAndSpine6(
            spine=spine,
            leaf=leaf,
            fanout=fanout,
            vlan=vlan,
            ipv6=ipv6
        )
    net = Mininet( topo=topo, link=TCLink, build=False,
                   controller=None, autoSetMacs=True )
    i = 0
    for ip in controllers:
        net.addController( "c%s" % ( i ), controller=RemoteController, ip=ip )
        i += 1
    net.build()
    net.start()
    if not ipv6:
        out1 = net.get( 'out1' )
        out1.cmd( "arp -s 10.0.9.254 10:00:00:00:00:01 -i %s " % ( out1.intf() ) )
    ExtendedCLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    config( opts )
    os.system( 'sudo mn -c' )
