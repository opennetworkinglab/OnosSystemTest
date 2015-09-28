#!/bin/bash
# This script will kill any TestON, ssh, and Mininet sessions that are running.
sudo kill -9 `ps -ef | grep "./cli.py" | grep -v grep | awk '{print $2}'`
sudo kill -9 `ps -ef | grep "bin/teston" | grep -v grep | awk '{print $2}'`
sudo kill -9 `ps -ef | grep "ssh -X" | grep -v grep | awk '{print $2}'`
sudo mn -c
sudo pkill -f mn.pid
sudo pkill bgpd
sudo pkill zebra
sudo kill -9 `ps -ef | grep "bird" | grep -v grep | awk '{print $2}'`
