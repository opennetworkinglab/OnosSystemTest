#!/bin/bash
# -----------------------------------------------------------------------------
# This script will kill any TestON, ssh, and Mininet sessions that are running.
# -----------------------------------------------------------------------------

# TODO: Add help to this file, and some more options?
#       Maybe kill/uninstall ONOS?
sudo kill -9 `ps -ef | grep "./cli.py" | grep -v grep | awk '{print $2}'`
sudo kill -9 `ps -ef | grep "bin/teston" | grep -v grep | awk '{print $2}'`
sudo kill -9 `ps -ef | grep "ssh -X" | grep -v grep | awk '{print $2}'`
sudo mn -c
sudo pkill -f mn.pid
sudo pkill bgpd
sudo pkill zebra
sudo pkill vrrpd
sudo kill -9 `ps -ef | grep "bird" | grep -v grep | awk '{print $2}'`


# Restore persistent firewall rules
if [ "$1" = "-f" ]; then

    OCIS=( $(env | sed -ne 's:OC[0-9]\{1,\}=\(.*\):\1 :g p' | sort -k1) )
    if [ -z "$OCIS" ]; then
      printf "no ONOS nodes set in your cell, Don't know where to look" >&2 && exit 0
    fi

    # TODO: Make the file configurable
    for i in ${OCIS[@]}; do
        echo "Restoring iptables rules on ${i}"
        ssh sdn@$i "sudo iptables -F"
        ssh sdn@$i "sudo iptables-restore < /etc/iptables/rules.v4"
        exit 0
    done
fi
