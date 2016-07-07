#!/usr/bin/env python

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import Host, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel

from opticalUtils import LINCSwitch, LINCLink

class OpticalTopo( Topo ):
    """
    A simple optical topology of three LINC nodes(OE*), two OVS switches(ps*), and two hosts:

              OE3
              /\
    h1-ps1-OE1--OE2-ps2-h2

    """
    def build( self ):

        # set up packet layer - OVS + hosts
        s1 = self.addSwitch( 'ps1' )
        s2 = self.addSwitch( 'ps2' )
        h1 = self.addHost( 'h1' )
        h2 = self.addHost( 'h2' )
        self.addLink( s1, h1 )
        self.addLink( s2, h2 )

        # set up ROADMs, add them to oel[]
        oel = []
        an = { "durable": "true" }
        for i in range (1,4):
            oean = { "optical.regens": 0 }
            oel.append( self.addSwitch('OE%s' % i, dpid='0000ffffffffff0%s' % i, annotations=oean, cls=LINCSwitch) )

        # ROADM port numbers are built as: OE1 <-> OE2 = 1200
        # leaving port number up to 100 open for use by Och port
        self.addLink( oel[0], oel[1], port1=1200, port2=2100, annotations=an, cls=LINCLink )
        self.addLink( oel[1], oel[2], port1=2300, port2=3200, annotations=an, cls=LINCLink )
        self.addLink( oel[2], oel[0], port1=3100, port2=1300, annotations=an, cls=LINCLink )

        # cross-connects between OVSes and LINCs
        self.addLink( s1, oel[0], port1=2, port2=1, annotations=an, cls=LINCLink )
        self.addLink( s2, oel[1], port1=2, port2=1, annotations=an, cls=LINCLink )


def setup( ctls ):
    net = Mininet( topo=OpticalTopo(), controller=None )
    i = 1
    for ctl in ctls:
        net.addController( RemoteController( 'c%d' % i, ip=ctl ) )
        i+=1

    net.start()
    LINCSwitch.bootOE( net )
    CLI( net )
    net.stop()
    LINCSwitch.shutdownOE()


if __name__ == "__main__" :
    import sys
    if len( sys.argv ) >= 2 :
        setLogLevel( 'info' )
        ctls = sys.argv[ 1: ]
        setup( ctls )
    else:
        print('./ectopo.py [IP1] [IP2]...\n')
