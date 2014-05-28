#! /usr/bin/env python
import json
import os
import sys

# http://localhost:8080/wm/onos/topology/switches
# http://localhost:8080/wm/onos/topology/links
# http://localhost:8080/wm/onos/registry/controllers/json
# http://localhost:8080/wm/onos/registry/switches/json"

def get_json(url):
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

  return parsedResult 

def check_switch(RestIP,correct_nr_switch ):
  buf = ""
  retcode = 0
  RestPort="8080"

  url="http://%s:%s/wm/onos/topology/switches" % (RestIP, RestPort)
  parsedResult = get_json(url)

  if parsedResult == "":
    retcode = 1
    return (retcode, "Rest API has an issue")

  url = "http://%s:%s/wm/onos/registry/switches/json" % (RestIP, RestPort)
  registry = get_json(url)

  if registry == "":
    retcode = 1
    return (retcode, "Rest API has an issue")


  buf += "switch: total %d switches\n" % len(parsedResult)
  cnt = 0
  active = 0

  for s in parsedResult:
    cnt += 1

    if s['state']  == "ACTIVE":
      active += 1

    if not s['dpid'] in registry:
      buf += "switch:  dpid %s lost controller\n" % (s['dpid'])

  buf += "switch: network %d : %d switches %d active\n" % (0+1, cnt, active)
  if correct_nr_switch != cnt:
    buf += "switch fail: network %d should have %d switches but has %d\n" % (1, correct_nr_switch, cnt)
    retcode = 1

  if correct_nr_switch != active:
    buf += "switch fail: network %d should have %d active switches but has %d\n" % (1, correct_nr_switch, active)
    retcode = 1

  return (retcode, buf)

def check_link(RestIP, nr_links):
  RestPort = "8080"
  buf = ""
  retcode = 0

  url = "http://%s:%s/wm/onos/topology/links" % (RestIP, RestPort)
  parsedResult = get_json(url)

  if parsedResult == "":
    retcode = 1
    return (retcode, "Rest API has an issue")

  buf += "link: total %d links (correct : %d)\n" % (len(parsedResult), nr_links)
  intra = 0
  interlink=0

  for s in parsedResult:
    intra = intra + 1 

  if intra != nr_links:
    buf += "link fail: network %d should have %d intra links but has %d\n" % (1, nr_links, intra)
    retcode = 1

  return (retcode, buf)

#if __name__ == "__main__":
def check_status(ip, numoswitch, numolink):

  switch = check_switch(ip, numoswitch)
  link = check_link(ip, numolink)
  value = switch[0]
  value += link[0]
  if value != 0:
    print "FAIL"
    return 0
  else: 
    print "PASS"
    return 1
  print "%s" % switch[1]
  print "%s" % link[1]
 # print "%s" % check_switch_local()[1]
 # print "%s" % check_controllers(8)[1]
