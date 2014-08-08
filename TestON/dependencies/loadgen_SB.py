#!/usr/bin/python

"""
This example shows how to create an empty Mininet object
(without a topology object) and add nodes to it manually.
"""
import sys
import subprocess
import time
from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.log import setLogLevel, info

swlist = []
hostlist= []
count = 0 

def createSwPorts(numsw, numport):

    "Create an empty network and add nodes to it."

    net = Mininet()
    swlist = []
    hostlist= []
    print ("Starting Mininet Network....")
    for i in range(numsw):
        sw = net.addSwitch( 's' + str(i), dpid = ('00000000000000' + '%0d'%i))
        print str(sw),
        for p in range(numport):
            host = net.addHost("s"+str(i)+"h"+str(p))
            hostlist.append(host)
            print str(host),
            net.addLink(host,sw)
        swlist.append(sw)

            
    info( '*** Starting network\n')
    net.start()

    return swlist

def loadsw(urllist, swlist, addrate, delrate, duration):
    global numport
    urlindex = 0
    count = 0
    addsleeptimer = 1.000 /addrate
    delsleeptimer = 1.000/delrate
    print (" Add sleeptimer: " + str('%.3f' %addsleeptimer) + "; Delete sleeptimer: " + str('%.3f' %delsleeptimer))
    print str(swlist)
 
    tstart = time.time()
    while ( (time.time() - tstart) <= duration ):
        #print (time.time() - tstart)
        astart = time.time()
        for sw in swlist:
            if urlindex < len(urllist):
                i = urlindex
            else:
                i = 0
                urlindex = 0
        
            ovscmd = "sudo ovs-vsctl set-controller " + str(sw) + " tcp:" + urllist[i]
            print ("a"),
            s = subprocess.Popen(ovscmd, shell=True )
            time.sleep(addsleeptimer)
            count += 1
            urlindex += 1
        aelapse = time.time() - astart
        print ("Number of switches connected: " + str(len(swlist)) + " in: " + str('%.3f' %aelapse) + "seconds.")

        dstart = time.time()
        for sw in swlist:
            ovscmd = "sudo ovs-vsctl set-controller " + str(sw) + " tcp:127.0.0.1:6633"
            print ("d"),
            s = subprocess.Popen(ovscmd, shell=True )
            time.sleep(delsleeptimer)
            count += 1
        delapse = time.time() - dstart
        print ("Number of switches disconnected: " + str(len(swlist)) + " in: " + str('%.3f' %delapse) + "seconds.")
    telapse = time.time() - tstart
    
    return telapse, count
def cleanMN():
    print ("Cleaning MN switches...")
    s = subprocess.Popen("sudo mn -c > /dev/null 2>&1", shell=True)
    print ("Done.")

def main():
    import argparse
    import threading
    from threading import Thread

    parser = argparse.ArgumentParser(description="less script")
    parser.add_argument("-u", "--urls", dest="urls", default="10.128.10.1", type=str, help="a string to show urls to post intents to separated by space, ex. '10.128.10.1:6633 10.128.10.2:6633' ")
    parser.add_argument("-s", "--switches", dest="numsw", default=100, type=int, help="number of switches use in the load generator; together with the ports per switch config, each switch generates (numport + 2) events")
    parser.add_argument("-p", "--ports", dest="numport", default=1, type=int, help="number of ports per switches")
    parser.add_argument("-a", "--addrate", dest="addrate", default=10, type=float, help="rate to add intents groups, groups per second")
    parser.add_argument("-d", "--delrate", dest="delrate", default=100, type=float, help= "rate to delete intents, intents/second")
    parser.add_argument("-l", "--testlength", dest="duration", default=0, type=int, help= "pausing time between add and delete of intents")
    args = parser.parse_args()

    urllist = args.urls.split()
    numsw = args.numsw
    numport = args.numport
    addrate = args.addrate
    delrate = args.delrate
    duration = args.duration
    setLogLevel( 'info' )
    swlist = createSwPorts(numsw,numport)
    telapse,count = loadsw(urllist, swlist, addrate, delrate, duration)
    print ("Total number of switches connected/disconnected: " + str(count) + "; Total events generated: " + str(count * (2 + numport)) + "; Elalpse time: " + str('%.1f' %telapse))
    print ("Effective aggregated loading is: " + str('%.1f' %((( count * (2+ numport))) / telapse ) ) + "Events/s.")
    cleanMN()

if __name__ == '__main__':
    main()
