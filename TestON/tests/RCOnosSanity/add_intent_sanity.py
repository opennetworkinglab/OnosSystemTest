#! /usr/bin/python

import json
import requests


url = 'http://127.0.0.1:8080/wm/onos/datagrid/add/intents/json'
headers = {'Content-type': 'application/json', 'Accept': 'application/json'}


for i in range(6,16):
	srcMac = '00:00:00:00:00:'+ str(hex(i)[2:]).zfill(2)
	dstMac = '00:00:00:00:00:'+ str(hex(i+10)[2:])
	srcSwitch = '00:00:00:00:00:00:10:'+ str(i).zfill(2)
	dstSwitch = '00:00:00:00:00:00:20:'+ str(i+25)
	srcPort = 1
	dstPort = 1
	
	intent = [{'intent_id': '%d' %(i),'intent_type':'shortest_intent_type','intent_op':'add','srcSwitch':srcSwitch,'srcPort':srcPort,'srcMac':srcMac,'dstSwitch':dstSwitch,'dstPort':dstPort,'dstMac':dstMac}]
	r = requests.post(url, data=json.dumps(intent, sort_keys=True), headers = headers)
	#print json.dumps(intent, sort_keys = True)
	
	intent = [{'intent_id': '%d' %(i+10),'intent_type':'shortest_intent_type','intent_op':'add','srcSwitch':dstSwitch,'srcPort':dstPort,'srcMac':dstMac,'dstSwitch':srcSwitch,'dstPort':srcPort,'dstMac':srcMac}]
	#print json.dumps(intent, sort_keys = True)
	r = requests.post(url, data=json.dumps(intent, sort_keys=True), headers = headers)

