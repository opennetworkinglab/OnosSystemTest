#! /usr/bin/env python
from time import time, sleep
import time
import json
import requests
import urllib2
from urllib2 import URLError, HTTPError

'''
    This script is for Intent Throughput testing. Use linear 7-switch topo. Intents are from S1P1 to/from S7/P1, with incrementing src/dst Mac addresses.
'''

def setIntentJSN(node_id, intPerGroup, group_id, intent_id):
    intents = [None for i in range(intPerGroup)]
    oper = {}
    index = 0
    for i in range(intPerGroup / 2):
        smac = str("%x" %(node_id * 0x100000000000 + 0x010000000000 + (group_id * 0x000001000000) +i + 1))
        dmac = str("%x" %(node_id * 0x100000000000 + 0x070000000000 + (group_id * 0x000001000000) +i + 1))
        srcMac = ':'.join(smac[i:i+2] for i in range(0, len(smac), 2))
        dstMac = ':'.join(dmac[i:i+2] for i in range(0, len(dmac), 2))
        srcSwitch = "00:00:00:00:00:00:00:01"
        dstSwitch = "00:00:00:00:00:00:00:07"
        srcPort = 1
        dstPort = 1

        oper['intentId'] = intent_id
        oper['intentType'] = 'SHORTEST_PATH'    # XXX: Hardcode
        oper['staticPath'] = False              # XXX: Hardcoded
        oper['srcSwitchDpid'] = srcSwitch
        oper['srcSwitchPort'] = srcPort
        oper['dstSwitchDpid'] = dstSwitch
        oper['dstSwitchPort'] = dstPort
        oper['matchSrcMac'] = srcMac
        oper['matchDstMac'] = dstMac
        intents[index] = oper
        #print ("perGroup Intents-0 are: " + json.dumps(intents) + "\n\n\n" )
        index += 1
        intent_id += 1
        oper = {}
        #print ("ID:" + str(id))

        oper['intentId'] = intent_id
        oper['intentType'] = 'SHORTEST_PATH'    # XXX: Hardcoded
        oper['staticPath'] = False              # XXX: Hardcoded
        oper['srcSwitchDpid'] = dstSwitch
        oper['srcSwitchPort'] = dstPort
        oper['dstSwitchDpid'] = srcSwitch
        oper['dstSwitchPort'] = srcPort
        oper['matchSrcMac'] = dstMac
        oper['matchDstMac'] = srcMac
        intents[index] = oper
        index += 1 
        intent_id += 1
        oper = {}
        #print ("ID: " + str(id))
        #print ("perGroup Intents-1 are: " + json.dumps(intents) + "\n\n\n" )
    #print ("contructed intents are: " + json.dumps(intents) + "\n\n\n")
    return intents, intent_id

def post_json(url, data):
    """Make a REST POST call and return the JSON result
           url: the URL to call
           data: the data to POST"""
    posturl = "http://%s/wm/onos/intent/high" %(url)
    #print ("\nPost url is : " + posturl + "\n")
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

def delete_json(self, url, intPerGroup, startID):
    """Make a REST DELETE call and return the JSON result
           url: the URL to call"""
    #url = "localhost:8080"
    for i in range(intPerGroup):
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

def delete_all_json(url):
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

def loadIntents(node_id, urllist, intPerGroup, addrate, duration):
    urlindex = 0
    group = 0
    start_id = 0
    sleeptimer = (1.000/addrate)
    tstart = time.time()
    while ( (time.time() - tstart) <= duration ):
        if urlindex < len(urllist):
            realurlind = urlindex
        else:
            realurlind = 0
            urlindex = 0

        u = str(urllist[realurlind])
        gstart = time.time()
        intents,start_id = setIntentJSN(node_id, intPerGroup, group, start_id)
        #print (str(intents))
        #print ("Starting intent id: " + str(start_id))
        result = post_json(u, intents)
        #print json.dumps(intents[group])
        #print ("post result: " + str(result))
        gelapse = time.time() - gstart
        print ("Group: " + str(group) + " with " + str(intPerGroup) + " intents were added in " + str('%.3f' %gelapse) + " seconds.")
        sleep(sleeptimer)
        urlindex += 1
        group += 1

    telapse = time.time() - tstart
    #print ( "Number of groups: " + str(group) + "; Totoal " + str(args.groups * args.intPerGroup) + " intents were added in " + str(telapse) + " seconds.")
    return telapse, group

def main():
    import argparse

    parser = argparse.ArgumentParser(description="less script")
    parser.add_argument("-n", "--node_id", dest="node_id", default = 1, type=int, help="id of the node generating the intents, this is used to distinguish intents when multiple nodes are use to generate intents")
    parser.add_argument("-u", "--urls", dest="urls", default="10.128.10.1", type=str, help="a string to show urls to post intents to separated by space, ex. '10.128.10.1:8080 10.128.10.2:80080' ")
    parser.add_argument("-i", "--intentsPerGroup", dest="intPerGroup", default=100, type=int, help="number of intents in one restcall group")
    parser.add_argument("-a", "--addrate", dest="addrate", default=10, type=float, help="rate to add intents groups, groups per second")
    parser.add_argument("-d", "--delrate", dest="delrate", default=100, type=float, help= "### Not Effective -for now intents are delete as bulk #### rate to delete intents, intents/second")
    parser.add_argument("-l", "--length", dest="duration", default=300, type=int, help="duration/length of time the intents are posted")
    parser.add_argument("-p", "--pause", dest="pause", default=0, type=int, help= "pausing time between add and delete of intents")
    args = parser.parse_args()

    node_id = args.node_id
    urllist = args.urls.split()
    intPerGroup = args.intPerGroup
    addrate = args.addrate
    delrate = args.delrate
    duration = args.duration    
    pause = args.pause

    print ("Intent posting urls are: " + str(urllist))
    print ("Number of Intents per group: " + str(intPerGroup))
    print ("Intent group add rate: " + str(addrate) )
    print ("Intent delete rate:" + str(delrate) )
    print ("Duration: " + str(duration) )
    print ("Pause between add and delete: " + str(args.pause))

    telapse, group = loadIntents(node_id, urllist, intPerGroup, addrate, duration)
    print ("\n\n#####################")
    print ( str(group) + " groups " + " of " + str(intPerGroup) + " Intents per group - Total " + str(group * intPerGroup) + " intents were added in " + str('%.3f' %telapse) + " seconds.")
    print ( "Effective intents posting rate is: " + str( '%.1f' %( (group * intPerGroup)/telapse ) ) + " Intents/second." )
    print ("#####################\n\n")
    print ("Sleep for " + str(pause) + " seconds before deleting all intents...")
    time.sleep(pause)
    print ("Cleaning up intents in all nodes...")
    for url in urllist:
        delete_all_json(url)
        
if __name__ == '__main__':
    main()
