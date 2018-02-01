This test verifies basic L23 connectivity using SegmentRouting via pingall

It consists of

1) Configure and install ONOS cluster
2) Start Mininet and check flow state
3) Pingall

<h3>Requirements</h3>
 - Trellis leaf-spine fabric: please visit following URL to set up Trellis leaf-spine fabric
 https://github.com/opennetworkinglab/routing/tree/master/trellis
 - ONOS_APPS=drivers,openflow,segmentrouting,fpm,netcfghostprovider

<h3>Topologies</h3>
- 2x5 Comcast Topology.
