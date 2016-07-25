This test verifies connectivity in face of dynamic configuration and Onos failures using SegmentRouting

It consists of

1) Configure and Install ONOS
2) Start Mininet and check flow state
3) Connectivity test
4) Add Hosts dynamically
5) Connectivity test
6) Onos Failure
7) Remove host configuration

Requirements

 - An updated version of the CPQD switch has to be running to make sure it supports group chaining.

The test is executed using the netcfg subsystem:
    1) APPS=openflow-base,netcfghostprovider,netcfglinksprovider
The test runs for different topologies:
 - 2x2 Leaf-Spine and 3-node ONOS cluster
 - 4x4 Leaf-Spine and 3-node ONOS cluster
 - Single switch and 3-node ONOS cluster