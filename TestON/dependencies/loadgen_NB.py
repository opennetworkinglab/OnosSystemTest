#! /usr/bin/env python
from time import time, sleep
import time
import json
import requests
import urllib2
from urllib2 import URLError, HTTPError


class Loadgen_SB_thread:
    '''
    This script is for Intent Throughput testing. Use linear 7-switch topo. Intents are from S1P1 to/from S7/P1, with incrementing src/dst Mac addresses'''

    '''response
    [{'intent_id':'5','status':'CREATED','log':['created, time:73268214932534']}]
    '''

    def __init__(self, urls, intPerGroup, groups, addrate, delrate, pause):
        self.intPerGroup = intPerGroup
        self.groups = groups
        self.urls = urls
        self.addrate = addrate
        self.delrate = delrate
        self.pause = pause
        
        intents = [[0 for group in range(self.groups)] for i in range(self.intPerGroup)]

    def setIntJSN(self, node_id, intPerGroup, groups):
        intents = [[None for a in range(self.intPerGroup)] for g in range(self.groups)]
        id = 0
        oper = {}
        for group in range(groups):
            index = 0
            for i in range(intPerGroup / 2):
                smac = str("%x" %(node_id * 0x100000000000 + 0x010000000000 + (group * 0x000001000000) +i + 1))
                dmac = str("%x" %(node_id * 0x100000000000 + 0x070000000000 + (group * 0x000001000000) +i + 1))
                srcMac = ':'.join(smac[i:i+2] for i in range(0, len(smac), 2))
                dstMac = ':'.join(dmac[i:i+2] for i in range(0, len(dmac), 2))
                srcSwitch = "00:00:00:00:00:00:00:01"
                dstSwitch = "00:00:00:00:00:00:00:07"
                srcPort = 1
                dstPort = 1

                oper['intentId'] = id
                oper['intentType'] = 'SHORTEST_PATH'    # XXX: Hardcoded
                oper['staticPath'] = False              # XXX: Hardcoded
                oper['srcSwitchDpid'] = srcSwitch
                oper['srcSwitchPort'] = srcPort
                oper['dstSwitchDpid'] = dstSwitch
                oper['dstSwitchPort'] = dstPort
                oper['matchSrcMac'] = srcMac
                oper['matchDstMac'] = dstMac
                intents[group][index] = oper
                #print ("perGroup Intents-0 are: " + json.dumps(intents) + "\n\n\n" )
                index =index + 1
                id =id+1
                oper = {}
                #print ("ID:" + str(id))

                oper['intentId'] = id
                oper['intentType'] = 'SHORTEST_PATH'    # XXX: Hardcoded
                oper['staticPath'] = False              # XXX: Hardcoded
                oper['srcSwitchDpid'] = dstSwitch
                oper['srcSwitchPort'] = dstPort
                oper['dstSwitchDpid'] = srcSwitch
                oper['dstSwitchPort'] = srcPort
                oper['matchSrcMac'] = dstMac
                oper['matchDstMac'] = srcMac
                intents[group][index] = oper
                index = index + 1 
                id = id + 1
                oper = {}
                #print ("ID: " + str(id))
                #print ("perGroup Intents-1 are: " + json.dumps(intents) + "\n\n\n" )
        #print ("contructed intents are: " + json.dumps(intents) + "\n\n\n")
        return intents, id

    def post_json(self, url, data):
        """Make a REST POST call and return the JSON result
           url: the URL to call
           data: the data to POST"""
        posturl = "http://%s/wm/onos/intent/high" %(url)
        print ("\nPost url is : " + posturl + "\n")
        parsed_result = []
        data_json = json.dumps(data)
        try:
            request = urllib2.Request(posturl, data_json)
            request.add_header("Content-Type", "application/json")
            response = urllib2.urlopen(request)
            result = response.read()
            response.close()
            if len(result) != 0:
                parsed_result = json.loads(result)
        except HTTPError as exc:
            print "ERROR:"
            print "  REST POST URL: %s" % posturl
            # NOTE: exc.fp contains the object with the response payload
            error_payload = json.loads(exc.fp.read())
            print "  REST Error Code: %s" % (error_payload['code'])
            print "  REST Error Summary: %s" % (error_payload['summary'])
            print "  REST Error Description: %s" % (error_payload['formattedDescription'])
            print "  HTTP Error Code: %s" % exc.code
            print "  HTTP Error Reason: %s" % exc.reason
        except URLError as exc:
            print "ERROR:"
            print "  REST POST URL: %s" % posturl
            print "  URL Error Reason: %s" % exc.reason
        return parsed_result

    def delete_json(self, url, startID):
        """Make a REST DELETE call and return the JSON result
           url: the URL to call"""
        #url = "localhost:8080"
        for i in range(self.intPerGroup):
            posturl = "http://%s/wm/onos/intent/high/%s" %(url, str(i + startID))
            parsed_result = []
            try:
                request = urllib2.Request(posturl)
                request.get_method = lambda: 'DELETE'
                response = urllib2.urlopen(request)
                result = response.read()
                response.close()
                #if len(result) != 0:
                #    parsed_result = json.loads(result)
            except HTTPError as exc:
                print "ERROR:"
                print "  REST DELETE URL: %s" % posturl
                # NOTE: exc.fp contains the object with the response payload
                error_payload = json.loads(exc.fp.read())
                print "  REST Error Code: %s" % (error_payload['code'])
                print "  REST Error Summary: %s" % (error_payload['summary'])
                print "  REST Error Description: %s" % (error_payload['formattedDescription'])
                print "  HTTP Error Code: %s" % exc.code
                print "  HTTP Error Reason: %s" % exc.reason
            except URLError as exc:
                print "ERROR:"
                print "  REST DELETE URL: %s" % posturl
                print "  URL Error Reason: %s" % exc.reason
        return parsed_result

    def delete_all_json(self, url):
        """Make a REST DELETE call and return the JSON result
           url: the URL to call"""
        #url = "localhost:8080"
        posturl = "http://%s/wm/onos/intent/high" %(url)
        parsed_result = []
        try:
            request = urllib2.Request(posturl)
            request.get_method = lambda: 'DELETE'
            response = urllib2.urlopen(request)
            result = response.read()
            response.close()
            if len(result) != 0:
                parsed_result = json.loads(result)
        except HTTPError as exc:
            print "ERROR:"
            print "  REST DELETE URL: %s" % posturl
            # NOTE: exc.fp contains the object with the response payload
            error_payload = json.loads(exc.fp.read())
            print "  REST Error Code: %s" % (error_payload['code'])
            print "  REST Error Summary: %s" % (error_payload['summary'])
            print "  REST Error Description: %s" % (error_payload['formattedDescription'])
            print "  HTTP Error Code: %s" % exc.code
            print "  HTTP Error Reason: %s" % exc.reason
        except URLError as exc:
            print "ERROR:"
            print "  REST DELETE URL: %s" % posturl
            print "  URL Error Reason: %s" % exc.reason
        return parsed_result


if __name__ == '__main__':
    import argparse
    import threading
    from threading import Thread

    parser = argparse.ArgumentParser(description="less script")
    parser.add_argument("-u", "--urls", dest="urls", default="10.128.10.1", type=str, help="a string to show urls to post intents to separated by space, ex. '10.128.10.1:8080 10.128.10.2:80080' ")
    parser.add_argument("-i", "--intentsPerGroup", dest="intPerGroup", default=100, type=int, help="number of intents in one restcall group")
    parser.add_argument("-g", "--groups", dest="groups", default=1, type=int, help="number of groups")
    parser.add_argument("-a", "--addrate", dest="addrate", default=10, type=int, help="rate to add intents groups, groups per second")
    parser.add_argument("-d", "--delrate", dest="delrate", default=100, type=int, help= "rate to delete intents, intents/second")
    parser.add_argument("-p", "--pause", dest="pause", default=0, type=int, help= "pausing time between add and delete of intents")
    args = parser.parse_args()

    myloadgen = Loadgen_SB_thread(args.urls, args.intPerGroup, args.groups, args.addrate, args.delrate, args.pause) 
    print ("Intent posting urls are: " + args.urls)
    print ("Number of Intents per group: " + str(args.intPerGroup))
    print ("Number of Intent Groups: " + str(args.groups))
    print ("Intent group add rate: " + str(args.addrate) )
    print ("Intent delete rate:" + str(args.delrate) )
    addsleeptimer = (1.000/args.addrate)
    print ("Add Sleep timer: " + str(addsleeptimer) )
    delsleeptimer = (1.000/args.delrate)
    print ("Del Sleep timer: " + str(delsleeptimer) )
    print ("Pause between add and delete: " + str(args.pause))
 
    urllist = args.urls.split()
    urlindex = 0

    intents,id = myloadgen.setIntJSN(7, args.intPerGroup, args.groups)
    print json.dumps(intents)
    print ("Number of intents: " + str(id) )    
    print ("Number of url: " + str(len(urllist)) )
    
    tstart = time.time()
    for group in range(args.groups):
        if urlindex < len(urllist):
            realurlind = urlindex
        else:
            realurlind = 0
            urlindex = 0
        
        u = str(urllist[realurlind])
        gstart = time.time()
        #print json.dumps(intents[group])
        print ("urlindex is : " + str(urlindex) + "realurlindex is: " + str(realurlind))
        print ("post url is: " + str(urllist[realurlind]) )
        print ("intent group is : " + str(group))
        result = myloadgen.post_json(u,intents[group])
        #print ("post result: " + str(result))
        gelapse = time.time() - gstart
        print ("Group: " + str(group) + " of " + str(args.groups) + " with " +str(args.intPerGroup) + " intents were added in " + str(gelapse) + " seconds.")
        sleep(1.000/myloadgen.addrate)
        urlindex = urlindex + 1
    
    telapse = time.time() - tstart
    print ( str(args.groups * args.intPerGroup) + " intents were added in " + str(telapse) + " seconds.")

    sleep(myloadgen.pause)
 
    urlindex = 0 
    inID = 0
    tstart = time.time()
    for group in range(args.groups):
        if urlindex < len(urllist):
            realurlind = urlindex
        else:
            realurlind = 0
            urlindex = 0
        
        inID = group * args.intPerGroup
        gstart = time.time()
        u = str(urllist[realurlind])
        for i in range(args.intPerGroup):
            result = myloadgen.delete_json(u, inID)
            #print ("post result: " + str(result))
        gelapse = time.time() - gstart
        print ("Group: " + str(group) + " of " + str(args.groups) " with " + str(args.intPerGroup) + " intents were deleted in " + str(gelapse) + " seconds.")
        sleep(1.000/myloadgen.delrate)
        urlindex = urlindex +1
    telapse = time.time() - tstart
    print ( str(args.groups * args.intPerGroup) + " intents were deleted in " + str(telapse) + " seconds.")

    print ("Final cleanup to delete all intents on nodes."
    for u in urllist:
        myloadgen.delete_all(u)
