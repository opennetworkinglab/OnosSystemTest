#!/usr/bin/python

import re,os,sys


testonpath = '~/TestON/logs'

name = os.popen("ls %s -rt | tail -1" % testonpath).read().split()[0]

logpath = testonpath+'/'+name+'/'+name+'.rpt'

os.popen('ssh admin@10.128.5.55 \'scp admin@10.128.5.55:'+logpath+' admin@10.128.5.55:~/jenkinsresults/syslogs/'+sys.argv[2]+'/'+sys.argv[1]+'/TestONLog.txt\'')
