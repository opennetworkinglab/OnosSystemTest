#! /usr/bin/env python
import json
import os
import sys



def find_host(RestIP,RestPort,RestAPI,hostMAC):
    retcode = 0
    url ="http://%s:%s/wm/device/" %(RestIP,RestPort)
        
    try:
        command = "curl -s %s" % (url)
        result = os.popen(command).read()
        parsedResult = json.loads(result)
    except:
        print "REST IF %s has issue" % command
        parsedResult = ""  

    if type(parsedResult) == 'dict' and parsedResult.has_key('code'):
        print "REST %s returned code %s" % (command, parsedResult['code'])
        parsedResult = ""



    if parsedResult == "":
        return (retcode, "Rest API has an error")
    else:
        found = [item for item in parsedResult if item['mac'] == [str(hostMAC)]]
        retcode = 1
        return (retcode, found)


if __name__ == "__main__":
	ip = "10.128.100.1"
	port = 8080
	hostMAC = "00:00:00:00:00:06"
	RestAPI = "/wm/device/"
	Reststat,Hoststat = find_host(ip,port,RestAPI,hostMAC)
	
	if Reststat == 1:
		print "Found device with MAC:" + hostMAC +" attached to switch(DPID):" + str(Hoststat[0]['attachmentPoint'][0]['switchDPID'])
	else:
		print " Device with MAC:" + hostMAC + " is not found!"
