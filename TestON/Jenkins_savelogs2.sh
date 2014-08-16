#!/bin/bash

#1 = testname
#2 = buildnumber

basename="andrew-ONOS"
machine1="admin@10.128.5.51"
machine2="admin@10.128.5.52"
machine3="admin@10.128.5.53"
logmachine="admin@10.128.5.55"
mn="admin@10.128.5.59"

directory="/home/onos/jenkinsresults/syslogs/$2/$1"
numdirs=`echo /home/onos/jenkinsresults/syslogs/*/ | wc -w`
dirlimit="20"

ssh $logmachine "mkdir -p $directory"

#onos.hostname.log
sudo scp $machine1:~/ONOS/onos-logs/onos.${basename}1.log $logmachine:$directory/
sudo scp $machine2:~/ONOS/onos-logs/onos.${basename}2.log $logmachine:$directory/
sudo scp $machine3:~/ONOS/onos-logs/onos.${basename}3.log $logmachine:$directory/
#zk logs
sudo scp $machine1:/var/log/zookeeper/zookeeper.out $logmachine:$directory/zk1.log
sudo scp $machine2:/var/log/zookeeper/zookeeper.out $logmachine:$directory/zk2.log
sudo scp $machine3:/var/log/zookeeper/zookeeper.out $logmachine:$directory/zk3.log
#stderr logs
sudo scp $machine1:~/ONOS/onos-logs/onos.${basename}1.stderr $logmachine:$directory/
sudo scp $machine2:~/ONOS/onos-logs/onos.${basename}2.stderr $logmachine:$directory/
sudo scp $machine3:~/ONOS/onos-logs/onos.${basename}3.stderr $logmachine:$directory/
#stdout logs
sudo scp $machine1:~/ONOS/onos-logs/onos.${basename}1.stdout $logmachine:$directory/
sudo scp $machine2:~/ONOS/onos-logs/onos.${basename}2.stdout $logmachine:$directory/
sudo scp $machine3:~/ONOS/onos-logs/onos.${basename}3.stdout $logmachine:$directory/
#ramcloud coordinator log
sudo scp $machine1:~/ONOS/onos-logs/ramcloud.coordinator.${basename}1.log $logmachine:$directory/
#ramcloud server logs
sudo scp $machine1:~/ONOS/onos-logs/ramcloud.server.${basename}1.log $logmachine:$directory/
sudo scp $machine2:~/ONOS/onos-logs/ramcloud.server.${basename}2.log $logmachine:$directory/
sudo scp $machine3:~/ONOS/onos-logs/ramcloud.server.${basename}3.log $logmachine:$directory/
#packet capture 
sudo scp $mn:~/packet_captures/${1}.pcap $directory/



if [ "$1" = "Scale" ]
then
    sudo scp $machine1:~/ONOS/onos-logs/onos.${basename}1.log.1 $logmachine:$directory/ONOS1.log.1
    sudo scp $machine1:~/ONOS/onos-logs/onos.${basename}1.log.2 $logmachine:$directory/ONOS1.log.2
    sudo scp $machine2:~/ONOS/onos-logs/onos.${basename}2.log.1 $logmachine:$directory/ONOS2.log.1
    sudo scp $machine2:~/ONOS/onos-logs/onos.${basename}2.log.2 $logmachine:$directory/ONOS2.log.2
    sudo scp $machine3:~/ONOS/onos-logs/onos.${basename}3.log.1 $logmachine:$directory/ONOS3.log.1
    sudo scp $machine3:~/ONOS/onos-logs/onos.${basename}3.log.2 $logmachine:$directory/ONOS3.log.2
fi

if [ $numdirs -gt $dirlimit ]
then
    ssh $logmachine 'sudo rm -R ~/jenkinsresults/syslogs/$(ls -lt ~/jenkinsresults/syslogs | grep '^d' | tail -1  | tr " " "\n" | tail -1)'
fi
