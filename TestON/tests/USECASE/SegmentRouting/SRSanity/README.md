This test verifies basic IP connectivity using SegmentRouting via pingall

It consists of

1) Configure and Install ONOS
2) Start Mininet and check flow state
3) Pingall

Requirements

 - An updated version of the CPQD switch has to be running to make sure it supports group chaining.

The test is executed using the netcfg subsystem:
    1) APPS=openflow-base,netcfghostprovider,lldpprovider
The test runs for different topologies:
 - 2x2 Leaf-Spine and 1-node ONOS cluster
 - 4x4 Leaf-Spine and 1-node ONOS cluster
 - Single switch and 1-node ONOS cluster
 - 2x2 Leaf-Spine and 3-node ONOS cluster
 - 4x4 Leaf-Spine and 3-node ONOS cluster
 - Single switch and 3-node ONOS cluster