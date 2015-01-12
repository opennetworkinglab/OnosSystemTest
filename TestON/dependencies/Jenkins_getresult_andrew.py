#!/usr/bin/env python

import sys
import os
import re
import datetime
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", help="Comma Separated string of test names. Ex: --name='test1, test2, test3'")
args = parser.parse_args()

#Pass in test names as a comma separated string argument. 
#Example: ./Jenkins_getresult.py "Test1,Test2,Test3,Test4"
name_list = args.name.split(",")
result_list = map(lambda x: x.strip(), name_list)

#NOTE: testnames list should be in order in which it is run
testnames = result_list
output = ''
testdate = datetime.datetime.now()

output +="<p>**************************************</p>"
output +=testdate.strftime('Jenkins test result for %H:%M on %b %d, %Y. %Z')

#TestON reporting
for test in testnames:
    name = os.popen("ls /home/admin/ONLabTest/TestON/logs/ -rt | grep %s | tail -1" % test).read().split()[0]
    path = "/home/admin/ONLabTest/TestON/logs/" + name + "/"
    output +="<p></p>"
    #output +="   Date: %s, %s %s" % (name.split("_")[2], name.split("_")[1], name.split("_")[3]) + "<br>*******************<br>"
    #Open the latest log folder 
    output += "<h2>Test "+str(test)+"</h2><p>************************************</p>"

    f = open(path + name + ".rpt")

    #Parse through each line of logs and look for specific strings to output to wiki.
    #NOTE: with current implementation, you must specify which output to output to wiki by using
    #main.log.report("") since it is looking for the [REPORT] tag in the logs
    for line in f:
        if re.search("Result summary for Testcase", line):
            output += "<h3>"+str(line)+"</h3>"
            #output += "<br>"
        if re.search("\[REPORT\]", line): 
            line_split = line.split("] ")
            #line string is split by bracket, and first two items (log tags) in list are omitted from output
            #join is used to convert list to string
            line_str = ''.join(line_split[2:])
            output += "<p>"
            output += line_str
            output += "</p>"
        if re.search("Result:", line):
            output += "<p>"
            output += line
            output += "</p>"
    f.close()

    #*********************
    #include any other phrase specific to case you would like to include in wiki here
    if test == "IntentPerf":
        output += "URL to Historical Performance results data: <a href='http://10.128.5.54/perf.html'>Perf Graph</a>"
    #*********************
print output
