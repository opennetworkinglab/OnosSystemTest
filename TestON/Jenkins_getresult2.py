#!/usr/bin/env python

import sys
import os
import re
import datetime
import time
#from xml.etree import ElementTree as ET

testnames=["TopoPerf", "IntentPerf"]

output = ''
testdate = datetime.datetime.now()

output +="**************************************<br>"
output +=testdate.strftime('Jenkins test result for %H:%M on %b %d, %Y. %Z')

#TestON reporting
for test in testnames: 
    name = os.popen("ls /home/admin/TestON/logs/ -rt | grep %s | tail -1" % test).read().split()[0]
    path = "/home/admin/TestON/logs/" + name + "/"
    output +="<br><br>"
    output +="   Date: %s, %s %s" % (name.split("_")[2], name.split("_")[1], name.split("_")[3]) + "<br>*******************<br>"
    f = open(path + name + ".rpt")
    for line in f:
        if re.search("Result summary for Testcase", line):
            output += "<br>"
            output += line
            output += "<br>" 
        if re.search("\[REPORT\]", line): 
            output += "<br>"
            output += line
            output += "<br>"
        if re.search("Result:", line):
            output += "<br>***********<br>"
            output += line
            output += "<br>***********<br>"
    f.close()


print output
