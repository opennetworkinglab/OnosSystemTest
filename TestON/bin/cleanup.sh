#!/bin/bash

# Copyright 2015 Open Networking Foundation (ONF)
#
# Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
# the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
# or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>
#
#     TestON is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 2 of the License, or
#     (at your option) any later version.
#
#     TestON is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with TestON.  If not, see <http://www.gnu.org/licenses/>.

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
sudo pkill dhclient
sudo pkill dhcpd
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
    done
fi
