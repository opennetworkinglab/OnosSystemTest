#!/usr/bin/python

import os
import re
from optparse import OptionParser

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import RemoteController, UserSwitch, Host, OVSBridge
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI


# Parse command line options and dump results
def parseOptions( ):
    """Parse command line options"""
    parser = OptionParser( )
    parser.add_option( '--spine', dest='spine', type='int', default=2,
                       help='number of spine switches, default=2' )
    parser.add_option( '--leaf', dest='leaf', type='int', default=2,
                       help='number of leaf switches, default=2' )
    parser.add_option( '--fanout', dest='fanout', type='int', default=2,
                       help='number of hosts per leaf switch, default=2' )
    parser.add_option( '--onos', dest='onos', type='int', default=0,
                       help='number of ONOS Instances, default=0, 0 means localhost, 1 will use OC1 and so on' )
    parser.add_option( '--vlan', dest='vlan', type='int', default=-1,
                       help='vid of cross connect, default=-1, -1 means utilize default value' )
    (options, args) = parser.parse_args( )
    return options, args


opts, args = parseOptions( )


class LeafAndSpine( Topo ):
    def __init__( self, spine=2, leaf=2, fanout=2, **opts ):
        "Create Leaf and Spine Topo."
        Topo.__init__( self, **opts )
        # Add spine switches
        spines = { }
        leafs = { }
        for s in range( spine ):
            spines[ s ] = self.addSwitch( 'spine10%s' % (s + 1),
                                          dpid="00000000010%s" % (s + 1) )
        # Set link speeds to 100Mb/s
        linkopts = dict( bw=100 )
        # Add Leaf switches
        for ls in range( leaf ):
            leafs[ ls ] = self.addSwitch( 'leaf%s' % (ls + 1),
                                          dpid="00000000000%s" % (1 + ls) )
            # Add hosts under a leaf, fanout hosts per leaf switch
            for f in range( fanout ):
                host = self.addHost( 'h%s' % (ls * fanout + f + 1),
                                     cls=IpHost,
                                     ip='10.0.%s.%s/24' % ((ls + 1), (f + 1)),
                                     gateway='10.0.%s.254' % (ls + 1) )
                self.addLink( host, leafs[ ls ], **linkopts )
                # Add Xconnect simulation
            if ls is 0:
                in1 = self.addHost( 'in1', cls=IpHost, ip='10.0.1.9/24', mac="00:00:00:00:00:09" )
                self.addLink( in1, leafs[0], **linkopts )
                out1 = self.addHost( 'out1', cls=IpHost, ip='10.0.9.1/24', mac="00:00:00:00:09:01" )
                self.addLink( out1, leafs[0], **linkopts )
                br1 = self.addSwitch( 'br1', cls=OVSBridge )
                self.addLink( br1, leafs[ 0 ], **linkopts )
                vlans = [ 1, 5, 10 ]
                for vid in vlans:
                    olt = self.addHost( 'olt%s' % vid, cls=VLANHost, vlan=vid,
                                        ip="10.%s.0.1/24" % vid
                                        , mac="00:00:%02d:00:00:01" % vid )
                    vsg = self.addHost( 'vsg%s' % vid, cls=VLANHost, vlan=vid,
                                        ip="10.%s.0.2/24" % vid
                                        , mac="00:00:%02d:00:00:02" % vid )
                    self.addLink( olt, leafs[ 0 ], **linkopts )
                    self.addLink( vsg, br1, **linkopts )
            # Connect leaf to all spines
            for s in range( spine ):
                switch = spines[ s ]
                self.addLink( leafs[ ls ], switch, **linkopts )

class IpHost( Host ):
    def __init__( self, name, *args, **kwargs ):
        super( IpHost, self ).__init__( name, *args, **kwargs )
        gateway = re.split('\.|/', kwargs['ip'])
        gateway[3] = '254'
        self.gateway = '.'.join(gateway[0:4])

    def config( self, **kwargs ):
        Host.config( self, **kwargs )
        mtu = "ifconfig " + self.name + "-eth0 mtu 1490"
        self.cmd( mtu )
        self.cmd( 'ip route add default via %s' % self.gateway )


class VLANHost( Host ):
    "Host connected to VLAN interface"

    def config( self, vlan=100, **params ):
        """Configure VLANHost according to (optional) parameters:
           vlan: VLAN ID for default interface"""
        r = super( VLANHost, self ).config( **params )
        intf = self.defaultIntf( )
        # remove IP from default, "physical" interface
        self.cmd( 'ifconfig %s inet 0' % intf )
        intf = self.defaultIntf( )
        # create VLAN interface
        self.cmd( 'vconfig add %s %d' % (intf, vlan) )
        self.cmd( 'ifconfig %s.%d %s' % (intf, vlan, params[ 'ip' ]) )
        # update the intf name and host's intf map
        self.cmd( 'ifconfig %s.%d mtu 1480' % (intf, vlan) )
        newName = '%s.%d' % (intf, vlan)
        # update the (Mininet) interface to refer to VLAN interface name
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
        #Parsing args from CLI
        args = line.split( )
        if len( args ) < 3 or len( args ) :
            "usage: addhost hostname switch **params"
        hostname, switch = args[0],  args[1]
        params = eval(line.split( ' ', 3 )[2])
        if 'cls' in params:
            params['cls'] = eval( params[ 'cls' ] )
        if hostname in self.mn:
            #error( '%s already exists!\n' % hostname )
            return
        if switch not in self.mn:
            #error( '%s does not exist!\n' % switch )
            return
        print params
        host = self.mn.addHostCfg( hostname, **params )
        #switch.attach( link.intf2 )
        #host.config()
        link = self.mn.addLink( host, switch )
        host.config(**params)

def config( opts ):
    spine = opts.spine
    leaf = opts.leaf
    fanout = opts.fanout
    vlan = opts.vlan
    controllers = [ os.environ[ 'OC%s' % i ] for i in
                    range( 1, opts.onos + 1 ) ] if (opts.onos) else [
        '127.0.0.1' ]
    topo = LeafAndSpine( spine=spine, leaf=leaf, fanout=fanout, vlan=vlan )
    net = Mininet( topo=topo, link=TCLink, build=False,
                   switch=UserSwitch, controller=None, autoSetMacs=True )
    i = 0
    for ip in controllers:
        net.addController( "c%s" % (i), controller=RemoteController, ip=ip )
        i += 1;
    net.build( )
    net.start( )
    out1 = net.get( 'out1' )
    out1.cmd( "arp -s 10.0.9.254 10:00:00:00:00:01 -i %s " % (out1.intf()) )
    CLI(net)
    net.stop( )


if __name__ == '__main__':
    setLogLevel( 'info' )
    config( opts )
    os.system( 'sudo mn -c' )
