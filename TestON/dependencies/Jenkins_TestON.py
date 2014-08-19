#!/usr/bin/env python

import pexpect
import sys
import os
import re

testname = sys.argv[1]
os.chdir("/home/admin/TestON/bin")
print os.popen("pwd").read()
child = pexpect.spawn("./cli.py")
child.expect("Solutions")
child.expect("teston>")
response = child.before + child.after
if re.search("teston>",response):
    print "TestON is running"
else:
    print "TestON not running"
    sys.exit()
child.sendline("run "+str(sys.argv[1]))
child.expect("CASE\sINIT",timeout=120)
print child.before + child.after
while 1:
    i = child.expect(["Result\ssummary\sfor","Test\sExecution\sSummary",testname], timeout=1800)
    #Print child object for each line with string result summary for 
    if i == 0:
        print child.before+child.after
    #Print child object for each line with the testname 
    elif i == 2:
        print child.before + child.after
    else:
        break
print child.before+child.after
print child.before
child.sendline("quit")
