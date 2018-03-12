This test verifies the segmentrouting application to be working correctly when changing the interface configuration at runtime.

It consists of

1) Configure and install ONOS cluster
2) Start Mininet and check flow state
3) Pingall
4) Change the configuration of a certain interface
5) Pingall

<h3>Requirements</h3>
 - Trellis leaf-spine fabric: please visit following URL to set up Trellis leaf-spine fabric
 https://github.com/opennetworkinglab/routing/tree/master/trellis
 - ONOS_APPS=drivers,openflow,segmentrouting,fpm,netcfghostprovider

<h3>Topologies</h3>
- 0x1 single ToR
- 0x2 dual-homed ToR
- 2x2 leaf-spine
- 2x4 leaf-spine with dual-homed ToR and dual links to spines
- 2x5 topology with spines S0 and S1, and leafs L0, L1, L2, L3, L4.