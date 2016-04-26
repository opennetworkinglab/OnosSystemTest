This test is designed to verify basic connectivity the SegmentRouting application via pingaall.

It consists of 

1) Configure and Install ONOS
2) Start Mininet and check flow state
2) Test connectivity

Requirements

 - A single ONOS instance is required for the test, the application is currently not stable in a cluster as of today.
 - An updated version of the CPQD switch has to be running to make sure it supports group chaining.

Step 1:
In this step, we copy config file to ONOS, next we package ONOS and install it in the target machine.

Step 2:

In this step we start the topology, connect to ONOS

Step:3

Here, we send several pings between hosts to test connectivity.

Then Steps are repeated for different configurations and topologies.

    Configurations:
     1) APPS=openflow-base,netcfghostprovider,netcfglinksprovider
     2) APPS=openflow

    Topologies:
     1) 2x2 Leaf-Spine
     2) 4x4 Leaf-Spine
