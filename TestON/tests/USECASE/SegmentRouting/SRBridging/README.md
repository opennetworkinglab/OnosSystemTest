This test verifies basic L2 connectivity using SegmentRouting via pingall

It consists of

1) Configure and install ONOS cluster
2) Start Mininet and check flow state
3) Pingall

<h3>Requirements</h3>
 - Trellis leaf-spine fabric: please visit following URL to set up Trellis leaf-spine fabric
 https://github.com/opennetworkinglab/routing/tree/master/trellis
 - ONOS_APPS=drivers,openflow,segmentrouting,fpm,netcfghostprovider
 - For the stratum bmv2 switch testing, the minient node requires docker. The docker image
 can be built using dependencies/Dockerfile.
 - The treliis mininet topology file requires the stratum.py file which can be found in the
 stratum repo (github.com/stratum/stratum) at stratum/tools/mininet/stratum.py.
 The stratum docker has this file already installed, but you may want to add this
 to the mininet/custom folder as well.

<h3>Topologies</h3>
- 0x1 single ToR
- 0x2 dual-homed ToR
- 2x2 leaf-spine
- 2x4 leaf-spine with dual-homed ToR and dual links to spines
- 2x3 leaf-spine with dual-homed ToR (Not implemented yet)
