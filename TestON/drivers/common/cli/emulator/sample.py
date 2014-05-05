import sys
import socket
import time

import pexpect
import struct
import fcntl
import os
import signal
import re

import oftest.cstruct as ofp
import oftest.message as message
import oftest.action as action
import oftest.parse as parse
import oftest.fakedevice as fakedevice

#Create a Fake controller listening on port 10100
ctr = fakedevice.FakeController(name= 'ctrller0',port= 10100,timeout= 5)
print ctr
#ctr.start()

#Start flowvisor on remote instance
child = pexpect.spawn("ssh flowvisor@10.128.101.59")
child.expect('flowvisor@ubuntu:~\$')
child.sendline('cd flowvisor/scripts')
child.expect('flowvisor@ubuntu:~/flowvisor/scripts\$')
child.sendline('sudo -u flowvisor flowvisor -p 6633 >& display.log & ')
child.expect('\$')
time.sleep(15)
child.sendline('cat display.log')
child.expect('\$')
print child.before

#Open another session of remote instance and add a slice mentioning the fakecontroller's address
child1 = pexpect.spawn("ssh flowvisor@10.128.101.59")
child1.expect('flowvisor@ubuntu:~\$')
child1.sendline('cd flowvisor/scripts')
child1.expect('flowvisor@ubuntu:~/flowvisor/scripts\$')
print "Started another session of remote flowvisor instance"

#Delete any exisitng slice with name slice1
child1.sendline('fvctl -n remove-slice slice1')
child1.expect('\$')
print child1.before

#Now create slice1
child1.sendline('fvctl add-slice slice1 tcp:10\.128\.100\.38:10100 shreya@onlab\.us')
child1.expect('Password:')
child1.sendline('')
child1.expect('Slice password:')
child1.sendline('')
child1.expect('\$')
print child1.before
#child1.expect('Slice slice1 was successfully created')

#Create a fake switch(Client) trying to connect to port 8081 of Flowvisor instance
sw = fakedevice.FakeSwitch(name='switch0', host='10.128.101.59', port=6633)
print sw

ctr.start()

send_msg = message.hello().pack()
sw.send(send_msg)

#ctr.start()
#time.sleep(5)

send_msg = message.features_reply(1).pack()
sw.send(send_msg)

#sw1 = fakedevice.FakeSwitch(name='switch1', host='localhost', port=10100)
#print sw

#send_msg = message.hello().pack()
#sw1.send(send_msg)

#send_msg = message.features_reply(2).pack()
#sw1.send(send_msg)

time.sleep(300)

SwitchNames = ctr.getSwitches()
print "Switch Names=", SwitchNames

#sw.set_dead()		#Close the connection 
#sw1.set_dead()		#Close the connection
