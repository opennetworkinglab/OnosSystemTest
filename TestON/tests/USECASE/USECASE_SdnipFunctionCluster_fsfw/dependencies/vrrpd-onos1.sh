#!/bin/bash

vrrpd -D -n -i eth0 -v 1 -p 150  10.128.20.11 -f /var/run/
vrrpd -D -n -i eth0 -v 2 -p 100  10.128.20.12 -f /var/run/
vrrpd -D -n -i eth0 -v 3 -p 50  10.128.20.13 -f /var/run/
