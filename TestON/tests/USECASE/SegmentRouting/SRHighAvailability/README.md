These tests are meant to test the high availability of ONOS and
SR application.

It consists of:
1) Configure and install ONOS;
2) Pingall between hosts;
3) Kill one ONOS instance;
4) Kill one spine;
5) Repeat this test a number of time;

Requirements:
1) An updated version of the CPQD switch has to be running to make sure it supports group chaining.

The test is executed using the netcfg subsystem:
1) APPS=openflow-base,netcfghostprovider,lldpprovider

The topologies are 2x2 Leaf-Spine and 4x4 Leaf-Spine.
