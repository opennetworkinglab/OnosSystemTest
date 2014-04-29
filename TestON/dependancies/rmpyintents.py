#! /usr/bin/env python

'''
This file removes the ONOS intents for the sanity 4 nodes tests. The flows associated with these intents should be deleted from the switches.
'''

import json
import requests



url = 'http://127.0.0.1:8080/wm/onos/datagrid/add/intents/json'
headers = {'Content-type': 'application/json', 'Accept': 'application/json'}


'''response
[{'intent_id':'5','status':'CREATED','log':['created, time:73268214932534']}]
'''



for i in range(6,16):
    #intent = [{'intent_id': '%d' %i,'intent_type':'shortest_intent_type','intent_op':'remove','srcSwitch':'8249','srcPort':1,'srcMac':'00:00:00:00:00:01','dstSwitch':'4103','dstPort':1,'dstMac':'00:00:00:00:00:02'}]
    srcMac = '00:00:00:00:00:'+ str(hex(i)[2:]).zfill(2)
    dstMac = '00:00:00:00:00:'+ str(hex(i+10)[2:])
    srcSwitch = '00:00:00:00:00:00:10:'+ str(i).zfill(2)
    dstSwitch = '00:00:00:00:00:00:20:'+ str(i+25)
    srcPort = 1 
    dstPort = 1 

    intent = [{'intent_id': '%d' %(i),'intent_type':'shortest_intent_type','intent_op':'remove','srcSwitch':srcSwitch,'srcPort':srcPort,'srcMac':srcMac,'dstSwitch':dstSwitch,'dstPort':dstPort,'dstMac':dstMac}]


    print json.dumps(intent, sort_keys = True)


    #r = requests.post(url, data=json.dumps(iid, sort_keys=True)+json.dumps(intent, sort_keys=True), headers = headers)
    r = requests.post(url, data=json.dumps(intent, sort_keys=True), headers = headers)
    print r
    print r.content



    intent = [{'intent_id': '%d' %(i+10),'intent_type':'shortest_intent_type','intent_op':'remove','srcSwitch':dstSwitch,'srcPort':dstPort,'srcMac':dstMac,'dstSwitch':srcSwitch,'dstPort':srcPort,'dstMac':srcMac}]
    print json.dumps(intent, sort_keys = True)
    r = requests.post(url, data=json.dumps(intent, sort_keys=True), headers = headers)
    print r
    print r.content

