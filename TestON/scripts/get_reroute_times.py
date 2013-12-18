#! /usr/bin/env python
import sys
import time
import os
import re
import json


CONFIG_FILE="/home/admin/ping.h10"

 
  
def get_times(pingfile):
  icmp_reqs = [] 
  times = []
  f = open(pingfile)
  for line in f.readlines():
    if re.search('64\sbytes', line): 
      icmp_reqs.append( (line.split()[4]).split('=')[1] )
  f.close()
  #print icmp_reqs
  lastnum = int(icmp_reqs[0]) - 1 
  for num in icmp_reqs: 
    if int(num) != (lastnum + 1):
      times.append(int(num) - lastnum) 
    lastnum = int(num)

  return times

if __name__ == "__main__":
  total = 0 
  count = 0 
  flow = 1
  for i in os.popen("ls /tmp/ping.*"):
    print "Flow %d  " % flow
    for time in get_times(i.strip("\n")):
      total = total + time
      count = count + 1
      print "  %d" % time     
    flow = flow + 1
  print "Average: %d" % (total / count ) 
 
