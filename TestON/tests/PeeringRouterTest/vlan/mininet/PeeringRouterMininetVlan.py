#!/usr/bin/python

"""
Start up the SDN-IP demo topology
"""

"""
AS1 = 64513, (SDN AS)
AS2 = 64514, reachable by 192.168.10.1, 192.168.20.1
AS3 = 64516, reachable by 192.168.30.1
AS4 = 64517, reachable by 192.168.40.1
AS6 = 64520, reachable by 192.168.60.2, (route server 192.168.60.1)
"""

from mininet.node import Host
from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.util import quietRun
from mininet.moduledeps import pathCheck

import os.path
import time
import sys
from subprocess import Popen, STDOUT, PIPE

QUAGGA_DIR = '/usr/lib/quagga'
#QUAGGA_DIR = '/usr/local/sbin'
QUAGGA_RUN_DIR = '/usr/local/var/run/quagga'

QUAGGA_CONFIG_FILE_DIR = '/home/admin/ONLabTest/TestON/tests/PeeringRouterTest/mininet'

class VLANHost( Host ):
    "Host connected to VLAN interface"

    def config( self, vlan=10, intf2 = '', ip2 = 0, vlan2 = 0, **params):
        """Configure VLANHost according to (optional) parameters:
           vlan: VLAN ID for default interface"""

        r = super( VLANHost, self ).config( **params )

        intf = params['inf']
        # remove IP from default, "physical" interface
        self.cmd( 'ifconfig %s inet 0' % intf )
        # create VLAN interface
        self.cmd( 'vconfig add %s %d' % ( intf, vlan ) )
        # assign the host's IP to the VLAN interface
        self.cmd( 'ifconfig %s.%d inet %s' % ( intf, vlan, params['ip'] ) )
        # update the intf name and host's intf map
        newName = '%s.%d' % ( intf, vlan )
        # update the (Mininet) interface to refer to VLAN interface name
        defaultIntf = self.defaultIntf()
        defaultIntf.name = newName
        # add VLAN interface to host's name to intf map
        self.nameToIntf[ newName ] = defaultIntf

        return r

class SDNIpModifiedTopo( Topo ):
    "SDN Ip Modified Topology"
    
    def __init__( self, *args, **kwargs ):
        global numHost101 
        global numHost200
        numHost101 = 101
        numHost200 = 200
        Topo.__init__( self, *args, **kwargs )
        sw1 = self.addSwitch('sw1', dpid='0000000000000001')
        sw2 = self.addSwitch('sw2', dpid='0000000000000002')
        #add a switch for 3 quagga hosts
        swTestOn = self.addSwitch('swTestOn', dpid='0000000000000102')
        #Note this switch isn't part of the SDN topology
        #We'll use the ovs-controller to turn this into a learning switch
        as6sw = self.addSwitch('as6sw', dpid='00000000000000a7')

        host1 = self.addHost( 'host1' )
        root1 = self.addHost( 'root1', inNamespace=False , ip='0')
        rootTestOn = self.addHost( 'rootTestOn', inNamespace=False, ip='0' )

        #AS2 host
        host3 = self.addHost( 'host3', cls=VLANHost, vlan=10, inf="host3-eth0", ip="192.168.10.1")
        
        as2host = self.addHost( 'as2host' )
        #AS3 host
        host4 = self.addHost( 'host4', cls=VLANHost, vlan=30, inf="host4-eth0", ip="192.168.30.1" )
        as3host = self.addHost( 'as3host' )
        #AS6 host
        host5 = self.addHost( 'host5', cls=VLANHost, vlan=60, inf="host5-eth0", ip="192.168.60.2" )
        as6host = self.addHost( 'as6host' )

        self.addLink( host1, sw2 )
        #Links to the multihomed AS
        self.addLink( host3, sw1 )
        self.addLink( host3, sw1 )
        self.addLink( as2host, host3 )
        #Single links to the remaining two ASes
        self.addLink( host4, sw1 )
        self.addLink( as3host, host4 )
          
        #AS3-AS4 link
        #self.addLink( host4, host5)
        #Add new AS6 to its bridge
        self.addLink( host5, as6sw )
        self.addLink( as6host, host5 )
        #test the host behind the router(behind the router server)
#        for i in range(1, 10):
 #           host = self.addHost('as6host%d' % i)
  #          self.addLink(host, as6router)

        ## Internal Connection To Hosts ##
        self.addLink( root1, host1 )

 #       self.addLink( sw1, sw2 )
 #       self.addLink( sw1, sw3 )
 #       self.addLink( sw2, sw4 )
 #       self.addLink( sw3, sw4 )
 #       self.addLink( sw3, sw5 )
 #       self.addLink( sw4, sw6 )
 #       self.addLink( sw5, sw6 )
        self.addLink( as6sw, sw1 )
        
        
        self.addLink(swTestOn, rootTestOn)
        #self.addLink(swTestOn, host1)
        self.addLink(swTestOn, host3)
        self.addLink(swTestOn, host4)
        self.addLink(swTestOn, host5)
        self.addLink(swTestOn, as2host)
        
        
        #self.addLink(rootTestOn, host4)

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

def stopsshd( ):
    "Stop *all* sshd processes with a custom banner"
    info( '*** Shutting down stale sshd/Banner processes ',
          quietRun( "pkill -9 -f Banner" ), '\n' )

def startquagga( host, num, config_file ):
    info( '*** Starting Quagga on %s\n' % host )
    zebra_cmd = 'sudo %s/zebra -d -f  %s/zebra.conf -z %s/zserv%s.api -i %s/zebra%s.pid' % (QUAGGA_DIR, QUAGGA_CONFIG_FILE_DIR, QUAGGA_RUN_DIR, num, QUAGGA_RUN_DIR, num)
    quagga_cmd = 'sudo %s/bgpd -d -f %s -z %s/zserv%s.api -i %s/bgpd%s.pid' % (QUAGGA_DIR, config_file, QUAGGA_RUN_DIR, num, QUAGGA_RUN_DIR, num)
    
    print zebra_cmd
    print quagga_cmd

    host.cmd( zebra_cmd )
    host.cmd( quagga_cmd )
    
def startquaggahost5( host, num ):
    info( '*** Starting Quagga on %s\n' % host )
    zebra_cmd = 'sudo %s/zebra -d -f %s/zebra.conf -z %s/zserv%s.api -i %s/zebra%s.pid' % (QUAGGA_DIR, QUAGGA_CONFIG_FILE_DIR, QUAGGA_RUN_DIR, num, QUAGGA_RUN_DIR, num)
    quagga_cmd = 'sudo %s/bgpd -d -f ./as4quaggas/quagga%s.conf -z %s/zserv%s.api -i %s/bgpd%s.pid' % (QUAGGA_DIR, num, QUAGGA_RUN_DIR, num, QUAGGA_RUN_DIR, num)
   
    host.cmd( zebra_cmd )
    host.cmd( quagga_cmd )    
    

def stopquagga( ):
    quietRun( 'sudo pkill -9 -f bgpd' )
    quietRun( 'sudo pkill -9 -f zebra' )

def sdn1net():
    topo = SDNIpModifiedTopo()
    info( '*** Creating network\n' )
    net = Mininet( topo=topo, controller=RemoteController )
    net = Mininet( topo=topo, controller=RemoteController )

    host1, host3, host4, host5 = net.get( 'host1', 'host3', 'host4', 'host5' )
    
        #host100.setIP('1.168.30.' + str(i), 24, str(host100) + "-eth2")  
         
        #host500.setMAC('00:00:00:00:04:%d' % (i-101), 'host%d-eth0' %(i))
        #add IP prefixes
        #for j in range(0,121):
            #host100.cmd('sudo ip addr add %s.0.40.%s/24 dev host%s-eth0' %(i,j,i))

    ## Adding 2nd, 3rd and 4th interface to host1 connected to sw1 (for another BGP peering)
    #sw1 = net.get('sw1')
    host1.setMAC('00:00:00:00:00:01', 'host1-eth0')
    #host1.cmd('ip addr add 192.168.20.101/24 dev host1-eth0')
    #host1.cmd('ip addr add 192.168.30.101/24 dev host1-eth0')
    #host1.cmd('ip addr add 192.168.60.101/24 dev host1-eth0')

    # Net has to be start after adding the above link
    net.start()

    # Set up as6sw as a learning switch as quickly as possible so it 
    # hopefully doesn't connect to the actual controller
    # TODO figure out how to change controller before starting switch
    as6sw = net.get('as6sw')
    as6sw.cmd('ovs-vsctl set-controller as6sw none')
    as6sw.cmd('ovs-vsctl set-fail-mode as6sw standalone')
    
    as6sw.cmd( 'sudo ovs-vsctl set port as6sw-eth1 trunk=60')
    as6sw.cmd( 'sudo ovs-vsctl set port as6sw-eth2 trunk=60')


    sw1 = net.get('sw1')
    sw1.cmd('ovs-vsctl set-controller sw1 tcp:127.0.0.1:6633')
    
    swTestOn = net.get('swTestOn')
    swTestOn.cmd('ovs-vsctl set-controller swTestOn none')
    swTestOn.cmd('ovs-vsctl set-fail-mode swTestOn standalone')

    #host1.defaultIntf().setIP('192.168.10.101/24') 
    
    host1.cmd( 'ifconfig host1-eth0 inet 0')
    host1.cmd( 'vconfig add host1-eth0 10')
    host1.cmd( 'ifconfig host1-eth0.10 inet 192.168.10.101')
    
    host1.cmd( 'vconfig add host1-eth0 20')
    host1.cmd( 'ifconfig host1-eth0.20 inet 192.168.20.101')
    
    host1.cmd( 'vconfig add host1-eth0 30')
    host1.cmd( 'ifconfig host1-eth0.30 inet 192.168.30.101')
    
    host1.cmd( 'vconfig add host1-eth0 60')
    host1.cmd( 'ifconfig host1-eth0.60 inet 192.168.60.101')

    # Run BGPd
    #host1.cmd('%s -d -f %s' % (BGPD, BGPD_CONF))
    #host1.cmd('/sbin/route add default gw 192.168.10.254 dev %s-eth0' % (host1.name))
    
    # Configure new host interfaces
    #host2.defaultIntf().setIP('172.16.10.2/24')
    #host2.defaultIntf().setMAC('00:00:00:00:01:02') 
    #host2.cmd('/sbin/route add default gw 172.16.10.254 dev %s-eth0' % (host2.name))

    # Set up AS2
    # add additional VLAN interface
    host3.cmd( 'ifconfig host3-eth1 inet 0')
    host3.cmd( 'vconfig add host3-eth1 20')
    host3.cmd( 'ifconfig host3-eth1.20 inet 192.168.20.1')
    # change the interface for the sencond connection to sw1 to vlan interface
    newName = "host3-eth1.20"
    secondIntf = host3.intf("host3-eth1")
    secondIntf.name = newName
    host3.nameToIntf[ newName ] = secondIntf
    
    host3.setMAC('00:00:00:00:02:01', 'host3-eth0.10')
    host3.setMAC('00:00:00:00:02:02', 'host3-eth1.20')
    
    #host3.setIP('172.16.20.254', 24, 'host3-eth2')
    host3.setIP('3.0.0.254', 8, 'host3-eth2')
    host3.cmd('sysctl net.ipv4.conf.all.forwarding=1')
    
    host3.setIP('1.168.30.2', 24, 'host3-eth3')   
    host3.cmd('sysctl net.ipv4.conf.all.arp_ignore=1')
    host3.cmd('sysctl net.ipv4.conf.all.arp_announce=1')
    host3.cmd('ip route add default via 192.168.10.101')
    as2host = net.get('as2host')
    #as2host.defaultIntf().setIP('172.16.20.1/24')
    for i in range(0, 20):
        as2host.cmd('sudo ip addr add 3.0.%d.1/24 dev as2host-eth0' %i)
    as2host.setIP('1.168.30.100', 24, 'as2host-eth1')
    
    as2host.cmd('ip route add default via 3.0.0.254')
    
    # Set up AS3
    host4.setMAC('00:00:00:00:03:01', 'host4-eth0.30')
    host4.setIP('4.0.0.254', 8, 'host4-eth1')
    host4.setMAC('00:00:00:00:03:99', 'host4-eth1')
    host4.cmd('sysctl net.ipv4.conf.all.forwarding=1')
    host4.cmd('ip route add default via 192.168.30.101')
    as3host = net.get('as3host')
    for i in range(0, 20):
        as3host.cmd('sudo ip addr add 4.0.%d.1/24 dev as3host-eth0' %i)
    as3host.cmd('ip route add default via 4.0.0.254')
    
    #root space
    host4.setIP('1.168.30.3', 24, 'host4-eth2')
    host4.setMAC('00:00:00:00:03:03', 'host4-eth2')
    
    # Set up AS4
    #as4host = net.get('as4host')
    #as4host.defaultIntf().setIP('172.16.40.1/24')
    #as4host.cmd('ip route add default via 172.16.40.254')
    
    # setup interface address for 100 quagga hosts
    time.sleep(10)
    #for i in range(numHost101, numHost200 + 1):
        #host100 = net.get('host' + str(i))
        #host100.cmd(str(i)+'.0.1.254', 24, 'host'+str(i)+'-eth1')
        #as4host100 = net.get('as4host%s' %(i))
        #as4host100.defaultIntf().setIP(str(i) + '.0.0.1/24')
        #as4host100.cmd('ip route add default via ' + str(i) + '.0.0.254')
        #for j in range(0, 100):
            #as4host100.cmd('sudo ip addr add %d.0.%d.1/24 dev %s-eth0' %(i, j, as4host100))

    # Set up AS6 - This has a router and a route server
    host5 = net.get('host5')
    host5.setMAC('00:00:00:00:06:02', 'host5-eth0.60')
    #as6router.setIP('172.16.60.254', 24, 'as6router-eth1')
    host5.setIP('5.0.0.254', 8, 'host5-eth1')
    host5.cmd('sysctl net.ipv4.conf.all.forwarding=1')
    host5.setIP('1.168.30.5', 24, 'host5-eth2')
    host5.setMAC('00:00:00:00:06:05', 'host5-eth2')
    host5.cmd('ip route add default via 192.168.60.101')
    as6host = net.get('as6host')
    #as6host.defaultIntf().setIP('5.0.0.1/24')
    for i in range(0, 10):
        as6host.cmd('sudo ip addr add 5.0.%d.1/24 dev as6host-eth0' %i)
    as6host.cmd('ip route add default via 5.0.0.254')

    # test the host in the as6
    #for i in range(1, 10):
    #    baseip = (i-1)*4
    #    host = net.get('as6host%d' % i)
    #    host.defaultIntf().setIP('172.16.70.%d/24' % (baseip+1))
    #    host.cmd('ip route add default via 172.16.70.%d' % (baseip+2))
     #   as6router.setIP('172.16.70.%d' % (baseip+2), 30, 'as6router-eth%d' % (i+1))

    # Start Quagga on border routers
    startquagga(host3, 1, QUAGGA_CONFIG_FILE_DIR + '/quagga1.conf')
    startquagga(host4, 2, QUAGGA_CONFIG_FILE_DIR + '/quagga2.conf')
    #for i in range(numHost101, numHost200 + 1):
        #host100=net.get('host%d' % (i))
        #startquaggahost5(host100, i)

    #startquagga(as6rs, 4, 'quagga-as6-rs.conf')
    startquagga(host5, 5, QUAGGA_CONFIG_FILE_DIR + '/quagga-as6.conf')

    #root1, root2, rootTestOn  = net.get( 'root1', 'root2', 'rootTestOn' )
    root1, rootTestOn  = net.get( 'root1', 'rootTestOn' )
    host1.intf('host1-eth1').setIP('1.1.1.1/24')
    root1.intf('root1-eth0').setIP('1.1.1.2/24')
    #host2.intf('host2-eth1').setIP('1.1.2.1/24')
    #root2.intf('root2-eth0').setIP('1.1.2.2/24')
    
    #rootTestOn.cmd('ip addr add 1.168.30.102/24 dev rootTestOn-eth0')
    rootTestOn.cmd('ip addr add 1.168.30.99/24 dev rootTestOn-eth0')
    
    stopsshd()    

    startquagga(host1, 100, QUAGGA_CONFIG_FILE_DIR + '/quagga-sdn-modified.conf')    
    hosts = [ host1, host3, host4, host5, as2host ];
    #sshdHosts = sshdHosts + hosts
    startsshds( hosts )
    #
    onos1 = '127.0.0.1'
    forwarding1 = '%s:2000:%s:2000' % ('1.1.1.2', onos1)
    root1.cmd( 'ssh -nNT -o "PasswordAuthentication no" -o "StrictHostKeyChecking no" -l sdn -L %s %s & ' % (forwarding1, onos1) )

    # Forward 2605 to root namespace for easier access to SDN domain BGPd
    # If root can ssh to itself without a password this should work
    root1.cmd('ssh -N -o "PasswordAuthentication no" -o "StrictHostKeyChecking no" -L 2605:1.1.1.1:2605 1.1.1.1 &')
    #time.sleep(3000000000)
    CLI( net )

    # Close the ssh port forwarding
    #quietRun('sudo pkill -f 1.1.1.1')

    stopsshd()
    stopquagga()
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'debug' )
    if len(sys.argv) > 1:
        QUAGGA_CONFIG_FILE_DIR = sys.argv[1]
    sdn1net()
