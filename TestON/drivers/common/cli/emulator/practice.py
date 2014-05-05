import pexpect
import struct
import fcntl
import os
import signal
import re
import sys
import time


child = pexpect.spawn("ssh flowvisor@10.128.101.59")
child.expect('flowvisor@ubuntu:~\$')
child.sendline('cd flowvisor/scripts')
child.expect('flowvisor@ubuntu:~/flowvisor/scripts\$')
child.sendline('sudo -u flowvisor flowvisor')
child.expect('Starting FlowVisor')
time.sleep(15)
print child.after



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
#child1.expect('flowvisor@ubuntu:~/flowvisor/scripts\$')
child1.expect('\$')
print child1.before
#child1.expect('Slice slice1 was successfully created')


child.close()
child1.close()
