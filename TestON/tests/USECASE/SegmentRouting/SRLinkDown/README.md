This test verifies basic connectivity using SegmentRouting via pingall,
it should not fail.

It consists of 

1) Configure and Install ONOS
2) Start Mininet and check flow state
3) Pingall

Requirements

 - An updated version of the CPQD switch has to be running to make sure it supports group chaining.

The test is executed using the netcfg subsystem:
    1) APPS=openflow-base,netcfghostprovider,netcfglinksprovider
The topology is a 2x2 Leaf-spine
