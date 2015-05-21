#!/usr/bin/env python

import sys
import os
import re
import datetime
import time
import argparse
import glob
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", help="Comma Separated string of test names. Ex: --name='test1, test2, test3'")
parser.add_argument("-w", "--workspace", help="The name of the Jenkin's job/workspace where csv files will be saved'")
args = parser.parse_args()

#Pass in test names as a comma separated string argument. 
#Example: ./Jenkins_getresult.py "Test1,Test2,Test3,Test4"
name_list = args.name.split(",")
result_list = map(lambda x: x.strip(), name_list)
job = args.workspace
if job is None:
    job = ""
print job

#NOTE: testnames list should be in order in which it is run
testnames = result_list
output = ''
header = ''
graphs = ''
testdate = datetime.datetime.now()
#workspace = "/var/lib/jenkins/workspace/ONOS-HA"
workspace = "/var/lib/jenkins/workspace/"
workspace = workspace + job

header +="<p>**************************************</p>"
header +=testdate.strftime('Jenkins test result for %H:%M on %b %d, %Y. %Z')


#NOTE: CASE SPECIFIC THINGS

#THIS LINE IS LOUSY FIXME
if any("HA" in s for s in testnames):
    ##Graphs
    graphs += '<ac:structured-macro ac:name="html">\n'
    graphs += '<ac:plain-text-body><![CDATA[\n'
    graphs += '<iframe src="https://onos-jenkins.onlab.us/job/'+job+'/plot/Plot-HA/getPlot?index=2&width=500&height=300" noborder="0" width="500" height="300" scrolling="yes" seamless="seamless"></iframe>\n'
    graphs += '<iframe src="https://onos-jenkins.onlab.us/job/'+job+'/plot/Plot-HA/getPlot?index=1&width=500&height=300" noborder="0" width="500" height="300" scrolling="yes" seamless="seamless"></iframe>\n'
    graphs += '<iframe src="https://onos-jenkins.onlab.us/job/'+job+'/plot/Plot-HA/getPlot?index=0&width=500&height=300" noborder="0" width="500" height="300" scrolling="yes" seamless="seamless"></iframe>\n'
    graphs += '<iframe src="https://onos-jenkins.onlab.us/job/'+job+'/plot/Plot-HA/getPlot?index=3&width=500&height=300" noborder="0" width="500" height="300" scrolling="yes" seamless="seamless"></iframe>\n'
    graphs += ']]></ac:plain-text-body>\n'
    graphs += '</ac:structured-macro>\n'
    header +="<p> <a href='https://wiki.onosproject.org/display/OST/Test+Plan+-+HA'>Test Plan for HA Test Cases</a></p>"


# ***


#TestON reporting
for test in testnames:
    passes = 0
    fails = 0
    name = os.popen("ls /home/admin/ONLabTest/TestON/logs/ -rt | grep %s_ | tail -1" % test).read().split()[0]
    path = "/home/admin/ONLabTest/TestON/logs/" + name + "/"
    try:
        #IF exists, move the csv file to the workspace
        for csvFile in glob.glob( path + '*.csv' ):
            shutil.copy( csvFile, workspace )
    except IOError:
        #File probably doesn't exist
        pass

    output +="<p></p>"
    #output +="   Date: %s, %s %s" % (name.split("_")[2], name.split("_")[1], name.split("_")[3]) + "<p>*******************<p>"
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
            if re.search("Pass", line):
                passes = passes + 1
            elif re.search("Fail", line):
                fails = fails + 1
    f.close()
    #https://wiki.onosproject.org/display/OST/Test+Results+-+HA#Test+Results+-+HA
    #Example anchor on new wiki:        #TestResults-HA-TestHATestSanity
    page_name = "Master-HA"
    if "ONOS-HA-1.1.X" in job:
        page_name = "Blackbird-HA"
    elif "ONOS-HA-Maint" in job:
        # NOTE if page name starts with number confluence prepends 'id-'
        #      to anchor links
        page_name = "id-1.0-HA"

    header += "<li><a href=\'#" + str(page_name) + "-Test" + str(test) + "\'> " + str(test) + " - Results: " + str(passes) + " Passed, " + str(fails) + " Failed</a></li>"

    #*********************
    #include any other phrase specific to case you would like to include in wiki here
    if test == "IntentPerf":
        output += "URL to Historical Performance results data: <a href='http://10.128.5.54perf.html'>Perf Graph</a>"
    #*********************

#header_file = open("/tmp/header_ha.txt",'w')
#header_file.write(header)
output = header + graphs + output
print output
