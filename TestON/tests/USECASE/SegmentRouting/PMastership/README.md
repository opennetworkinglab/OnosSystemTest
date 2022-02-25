# PMastership System Tests

Tests in this folder are meant to excercise the persistent Mastership
by simulating dataplane failure and verify that flows and groups
created by SegmentRouting are correctly purged and that when the
device is no longer available it still has the same master as before.

# Requirements to run PMastership tests

There are no particular requirements as it mainly relies on the ONOS
CLI driver and some utility functions to bring down a device and
manipulate k8s resources
