This test verifies DHCP relay functions:
  - Clients gets IP or IPv6 address from DHCP server
  - The host store and router store should includes specific hosts and routes.

It consists of:
1) Configure and install ONOS cluster
2) Start Mininet and check host discovery and IP assignment

<h3>Requirements</h3>
 - Trellis leaf-spine fabric: please visit following URL to set up Trellis leaf-spine fabric
 https://github.com/opennetworkinglab/routing/tree/master/trellis
 - ONOS_APPS=drivers,openflow,segmentrouting,fpm,dhcprelay,netcfghostprovider,routeradvertisement

<h3>Topologies</h3>
- 2x2 single ToR
- 2x4 dual-homed ToR
