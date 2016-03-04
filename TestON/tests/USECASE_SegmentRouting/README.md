This test is designed to verify basic connectivity the SegmentRouting application.

It consists of 

1) Installing and Starting ONOS
2) Starting Mininet and testing connectivity

Requirements

 - A single ONOS instance is required for the test, the application is currently not stable in a cluster.
 - An updated version of the CPQD switch has to be running to make sure it supports group chaining.

Step 1:
In this step we copy the proper config file to ONOS, next we package ONOS and install it in the target machine.

Step 2:

In this step we start a 2x2 leaf-spine topology, connect to ONOS, and next we send several pings between hosts to test connectivity.
