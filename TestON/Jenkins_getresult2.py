#!/usr/bin/env python

import sys
import os
import re
import datetime
import time
#from xml.etree import ElementTree as ET

#NOTE: testnames list should be in order in which it is run
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
    #output +="   Date: %s, %s %s" % (name.split("_")[2], name.split("_")[1], name.split("_")[3]) + "<br>*******************<br>"
    #Open the latest log folder 
    output += "<b>Test "+str(test)+"</b><br>************************************<br>"

    f = open(path + name + ".rpt")

    #Parse through each line of logs and look for specific strings to output to wiki.
    #NOTE: with current implementation, you must specify which output to output to wiki by using
    #main.log.report("") since it is looking for the [REPORT] tag in the logs
    for line in f:
        if re.search("Result summary for Testcase", line):
            output += "<b>"+str(line)+"</b>"
            output += "<br>"
        if re.search("\[REPORT\]", line): 
            line_split = line.split("] ")
            #line string is split by bracket, and first two items (log tags) in list are omitted from output
            #join is used to convert list to string
            line_str = ''.join(line_split[2:])
            output += line_str
            output += "<br>"
        if re.search("Result:", line):
            output += line
            output += "<br><br>"
    f.close()

    #*********************
    #include any other phrase specific to case you would like to include in wiki here
    if test == "IntentPerf":
        output += "URL to Historical Performance results data: <a href='http://10.128.5.54/perf.html'>Perf Graph</a>"
    #*********************
print output
