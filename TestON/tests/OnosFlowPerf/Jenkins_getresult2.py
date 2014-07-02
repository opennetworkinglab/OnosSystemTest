#!/usr/bin/env python

import sys
import os
import re
import datetime
import time
#from xml.etree import ElementTree as ET

#testnames=["RRCOnosSanity4nodesJ","RCOnosSanity4nodesJ","RCOnosPerf4nodes","RCOnosScale4nodes","OnosFlowPerf"]
testnames=["OnosFlowPerf"]
mvnpath = "/var/lib/jenkins/jobs/RCOnosNightly/builds/"
jacocopath = "/var/lib/jenkins/jobs/RCTestON/builds/"
casspath = "~/Measurement/data/result_n4_t"
threads = ["64"]

output = ''
testdate = datetime.datetime.now()

output +="**************************************<br>"
output +=testdate.strftime('Jenkins test result for %H:%M on %b %d, %Y. %Z')

#output +=The links

output +="<ul class=\'toc-indentation\'>"
output +="<li><a href=\'#ONOSNightlyTestResults-MavenUnitTestsResults\'>Maven Unit Test Results - </a></li>"
output +="<li><a href=\'#ONOSNightlyTestResults-RRCOnosSanity4nodesJ\'>Reactive Flow Sanity Test Results - </a></li>"
output +="<li><a href=\'#ONOSNightlyTestResults-RCOnosSanity4nodesJ\'>Proactive Flow Sanity Test Results - </a></li>"
output +="<li><a href=\'#ONOSNightlyTestResults-RCOnosPerf4nodes\'>Performance Test Results - </a></li>"
output +="<li><a href=\'#ONOSNightlyTestResults-RCOnosScale4nodes\'>Scale Test Results - </a></li>"
output +="<li><a href=\'#ONOSNightlyTestResults-OnosFlowPerf\'>Onos Flow Performance Results - </a></li>"
output +="</ul>"

#Maven reporting
#name = os.popen("ls %s -rt | tail -1" % mvnpath).read().split()[0]
name = "testing"
path = mvnpath + name + "/"
try:
    f = open(path + "log")
    mvnfailed = []
    mvnresults = []
    mvnerror = []
    failedflag = 0
    resultsflag = 0
    commit = ''
    for line in f:
        if re.search("Failed tests",line):
            failedflag = 1
            mvnfailed.append(line)
        elif re.search("Checking out Revision",line):
            commit = line
        elif re.search("Results",line):
            failedflag = 0
            resultsflag = 1
        elif re.search("Tests run",line) and resultsflag == 1:
            mvnresults = line
            resultsflag = 0
            failedflag = 0
        elif failedflag == 1:
            mvnfailed.append(line)
        elif re.search("<<< ERROR!", line):
            mvnerror.append(line.split()[0])
    f.close()
    output +="<br><h2 id=\"ONOSNightlyTestResults-MavenUnitTestsResults\">Maven Unit Tests Results</h2><br>*******************<br>"
    output +=str(commit) +"<br>"
    if len(mvnresults) == 0:
        output +="Maven build failed<br>"
        output = re.sub("Maven Unit Test Results - </a>","Maven Unit Test Results - Maven build failed</a>",output)
    else:
        output +=str(mvnresults)+"<br>"
        output = re.sub("Maven Unit Test Results - </a>","Maven Unit Test Results - "+ str(mvnresults) +"</a>",output)
    if len(mvnfailed) > 0:
        output +="<UL>Maven Tests Failed<br>"
        for i in range(len(mvnfailed)):
            output +=str(mvnfailed[i])+"<br>"
        output +="</UL>"
    if len(mvnerror) > 0:
        output +="<UL>The following tests had errors:<br>"
        for i in range(len(mvnerror)):
            output +=str(mvnerror[i])+"<br>"
        output +="</UL>"
except IOError:
    output +="Unable to open Maven log<br><br>"

#TestON reporting
for test in testnames: 
    results=[]
    descriptions=[]
    testresults = []
    casenum=[]
    scalefail = ["","",""]
    counter = 0
    failures = ""
    exceptions = ""
    totalExceptions = ""
    name = os.popen("ls ~/TestON/logs/ -rt | grep %s | tail -1" % test).read().split()[0]



    '''
    #test
    if test =="RCOnosSanity4nodesJ":
        name = "RCOnosSanity4nodesJ_15_May_2014_14_55_28"
    '''


    path = "/home/onos/TestON/logs/" + name + "/"
    output +="<br><br>"
    output +="<h2 id=\"ONOSNightlyTestResults-"+str(name.split("_")[0])+"\">"+str(name.split("_")[0])+"</h2>" 
    output +="   Date: %s, %s %s" % (name.split("_")[2], name.split("_")[1], name.split("_")[3]) + "<br>*******************<br>"
    f = open(path + name + ".rpt")
    for line in f:
        if len(results) == len(descriptions):
            if re.search("\[REPORT\]", line): 
	       descriptions.append(line.split("]")[2].split('\n')[0])
        if re.search("Result:",line):
            results.append(line.split()[1])
        elif re.search("\[REPORT\]", line):
	     output +=(line+"<br>") 
        elif re.search("Result summary for Testcase",line):
            casenum.append(re.split("[A-z]+",line)[4])
        elif re.search("commit\s", line ):
            output +="COMMIT: " + line.split()[1]+"<br>"
        elif re.search("Author: ",line):
           
            output +=(line+"<br>")
        elif re.search("CommitDate: ",line):
            output +=(line+"<br>")
            output +=("<br>*************************<br><br>")

        elif re.search("Average:", line):
            try:
                testresults.append(line.split()[1])
            except:
                testresults.append("Flows not rerouted")
        elif re.search("Convergence time of :",line):
            testresults.append(line.split()[9])
            scalefail[counter] = ""
            counter += 1
        elif re.search("switch fail:",line):
            scalefail[counter] += "<br>" + line
        elif re.search("link:",line):
            scalefail[counter] += "<br>" + line
        elif re.search("ONOS did NOT",line):
            testresults.append(line.split()[5])
            counter += 1 
        elif re.search ("Time to complete ping test:",line):
            testresults.append(line.split()[10])
        elif re.search ("Time to add flows:",line):
            testresults.append(line.split(':')[3])
        elif re.search("Flow check FAIL",line):
            testresults.append("FAIL")
        elif re.search ("PACKET LOST",line):
            testresults.append("FAIL")
        elif re.search("No data",line):
            testresults.append("FAIL")
        elif re.search("DEVICE DISCOVERY TEST FAILED",line):
            testresults.append("FAIL")
        elif re.search("Exceptions were found in the logs",line):
            totalExceptions = line
        elif re.search("Exceptions found in ",line):
            exceptions +="<LI>"+ line
            #print line
    f.close()
 
    counter = 0 
    passed = 0
    failed = 0
    for i in range(len(results)):
        try: 
            #output +="CASE%d: %s   *%s" % (i+1, results[i], descriptions[i])+"<br>"
            #output +="CASE%s: %s   *%s" % (casenum[i], results[i], descriptions[i])+"<br>"
            #output +="CASE%s: %s  " % (casenum[i], results[i])+"<br>"
            #get count of pass and failed
            if results[i]  == "Pass":
                passed += 1
            else:
                failed += 1


            if i == 6 and test == "RCOnosPerf4nodes":
                output +="<UL>Average Reroute time: " + str(testresults[0]) + " seconds</UL>"
            elif i == 9 and test == "RCOnosPerf4nodes":
                output +="<UL>Average Reroute time: " + str(testresults[1]) + " seconds</UL>"
            elif i == 12 and test == "RCOnosPerf4nodes":
                output +="<UL>Average Reroute time: " + str(testresults[2]) + " seconds</UL>"
            elif i >= 1 and test == "RCOnosScale4nodes" and i <= len(testresults):
                if str(testresults[i-1]) == "ONOS":
                    output +="<UL><b>ONOS did NOT converge</b>"
                    if i > 0 and scalefail[counter] != "":
                        output +=scalefail[counter] 
                    counter += 1
                    output +="</UL>"
                else:
                    output +="<UL>Convergence time: " + str(testresults[i-1]) + " seconds</UL>"
                    counter += 1
            elif i == 3 and (test == "RCOnosSanity4nodesJ" or test == "RRCOnosSanity4nodesJ"):
                if str(testresults[i-3]) == "FAIL":
                    output +="<UL>Unable to add flows</UL>"
                else:
                    output +="<UL>Time to add flows:" + str(testresults[i-3]) + "</UL>"
            elif i >= 4 and (test == "RCOnosSanity4nodesJ" or test == "RRCOnosSanity4nodesJ"):
                if len(testresults) <=i-3-1:
                    if str(testresults[i-3]) == "FAIL":
                        output +="<UL>Unable to ping between hosts</UL>"
                    else:
                        output +="<UL>Time to complete ping test: " + str(testresults[i-3]) + " seconds</UL>"
            else:
                output +=""
        except:
            '''
            import traceback
            print "Some exception was thrown\n"
            traceback.print_exc()
            traceback.print_exc(file=sys.stdout)
            '''
            if descriptions[i]:
                output += "CASE%s: %s   * ERROR WITH SOMETHING(NOT DESCRIPTIONS)" % (casenum[i], descriptions[i])+"<br>"
            if results[i]:
                output += "CASE%s: %s   * ERROR WITH SOMETHING(NOT RESULTS)" % (casenum[i], results[i])+"<br>"
            
    output += "<br>" + totalExceptions +"<br>"
    if not (exceptions == ''):
        output += "<UL>"
        output += exceptions
        output += "</UL>"
    output = re.sub(" - </a>"," - Tests run: " + str(len(results)) + ", Failures: " + str(failed) + ", Passed: "+ str(passed) + " </a>",output,count=1)



'''
#Code Coverage reporting
name = os.popen("ls %s -rt | tail -1" % jacocopath).read().split()[0]
path = jacocopath + name + "/"
tree = ET.parse(path+"build.xml")
root = tree.getroot()
classhit = root[0][1][0][1].text
classmiss = root[0][1][0][0].text
classtotal = int(classhit) + int(classmiss)
classpercent = (float(classhit)/float(classtotal))*100
methodmiss = root[0][1][1][0].text
methodhit = root[0][1][1][1].text
methodtotal = int(methodmiss) + int(methodhit)
methodpercent = (float(methodhit)/float(methodtotal))*100
linemiss = root[0][1][2][0].text
linehit =  root[0][1][2][1].text
linetotal = int(linemiss) + int(linehit)
linepercent = (float(linehit)/float(linetotal))*100
complexmiss = root[0][1][3][0].text 
complexhit = root[0][1][3][1].text
complextotal = int(complexmiss) + int(complexhit)
complexpercent = (float(complexhit)/float(complextotal))*100
instrmiss = root[0][1][4][0].text
instrhit = root[0][1][4][1].text
instrtotal = int(instrmiss) + int(instrhit)
instrpercent = (float(instrhit)/float(instrtotal))*100
branchmiss = root[0][1][5][0].text
branchhit = root[0][1][5][1].text
branchtotal = int(branchmiss) + int(branchhit)
branchpercent = (float(branchhit)/float(branchtotal))*100

output +="<br> Code Coverage: <br>*******************<br>"
output +="Class: %s hit, %s miss |  %.2f <br>" % (classhit, classmiss, classpercent)
output +="Class: %s hit, %s miss |  %.2f <br>" % (methodhit, methodmiss, methodpercent)
output +="Line: %s hit, %s miss |  %.2f <br>" % (linehit, linemiss, linepercent)
output +="Complex: %s hit, %s miss |  %.2f <br>" % (complexhit, complexmiss, complexpercent)
output +="Instruction: %s hit, %s miss |  %.2f <br>" % (instrhit, instrmiss, instrpercent)
output +="Branch: %s hit, %s miss |  %.2f <br>" % (branchhit, branchmiss, branchpercent)
'''

print output

with open("/home/onos//TestON/tests/OnosFlowPerf/jenkins_output.html", "w") as output_text:
    output_text.write(output)
    output_text.close()
