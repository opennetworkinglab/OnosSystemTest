import sys
import socket
import time

import oftest.cstruct as ofp
import oftest.message as message
import oftest.action as action
import oftest.parse as parse
import oftest.fakedevice as fakedevice


ctr = fakedevice.FakeController(name= 'ctrller0',port= 10101,timeout= 5)
print ctr

sw = fakedevice.FakeSwitch(name='switch0', host='10.128.100.38', port=10101)
print sw

#ctr.start()

send_msg = message.hello().pack()
print "Printing String in readable format______________"
sent_string = message.hello().show()
print sent_string
print "\n"
sw.send(send_msg)

ctr.start()

send_msg = message.features_reply().pack()
sw.send(send_msg)

sw1 = fakedevice.FakeSwitch(name='switch1', host='10.128.100.38', port=10101)
print sw

send_msg = message.hello().pack()
sw1.send(send_msg)

send_msg = message.features_reply(2).pack()
sw1.send(send_msg)

time.sleep(30)

SwitchNames = ctr.getSwitches()
print "Switch Names=", SwitchNames

sw.set_dead()		#Close the connection 
sw1.set_dead()		#Close the connection
