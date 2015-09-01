#!/usr/bin/python

for i in range(1, 101):
   num= i + 100

   v='quagga%d.conf' %num
   f=open(v, 'w')

   f.write('hostname bgpd\n')
   f.write('password hello\n')
   k=i + 65000
   v='router bgp %d\n' % (k)
   f.write(v)
   v='bgp router-id 192.168.40.%d\n' %i
   f.write(v)
   v='neighbor 192.168.40.101 remote-as 64513\n'
   f.write(v)
   #print v

   v='neighbor 192.168.40.101 ebgp-multihop\n'
   f.write(v)
   v='neighbor 192.168.40.101 update-source 192.168.40.%d\n' %i
   f.write(v)
   v='neighbor 192.168.40.101 timers connect 300\n'
   f.write(v)
