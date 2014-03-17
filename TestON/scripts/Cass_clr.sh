#!/bin/bash

#1 = testname
#2 = buildnumber

basename="autoONOS"
machine1="admin@10.128.100.1"
machine2="admin@10.128.100.4"
machine3="admin@10.128.100.5"
machine4="admin@10.128.100.6"
logmachine="onos@10.254.1.111"

ssh $machine1 "~/ONOS/start-cassandra.sh stop"
ssh $machine2 "~/ONOS/start-cassandra.sh stop"
ssh $machine3 "~/ONOS/start-cassandra.sh stop"
ssh $machine4 "~/ONOS/start-cassandra.sh stop"
ssh $machine1 "~/clrCass.sh"
ssh $machine2 "~/clrCass.sh"
ssh $machine3 "~/clrCass.sh"
ssh $machine4 "~/clrCass.sh"





