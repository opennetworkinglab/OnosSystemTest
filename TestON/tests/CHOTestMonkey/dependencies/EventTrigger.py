"""
Insert network/ONOS/app events into CHOTestMonkey
Author: you@onlab.us
"""
import time
import random
from multiprocessing.connection import Client

def triggerEvent( type, scheduleMethod, *args ):
    """
    This function inserts an event into CHOTestMonkey
    """
    host = "localhost"
    port = 6000
    address = ( host, port )
    conn = Client( address )
    request = []
    request.append( 2 )
    request.append( type )
    request.append( scheduleMethod )
    for arg in args:
        request.append( arg )
    conn.send( request )
    response = conn.recv()
    while response == 11:
        time.sleep( 1 )
        conn.send( request )
        response = conn.recv()
    if response == 10:
        print "Event inserted:", type, scheduleMethod, args
    elif response == 20:
        print "Unknown message to server"
    elif response == 21:
        print "Unknown event type to server"
    elif response == 22:
        print "Unknown schedule method to server"
    elif response == 23:
        print "Not enough argument"
    else:
        print "Unknown response from server:", response
    conn.close()

def testLoop( sleepTime=5 ):
    downLinkNum = 0
    downDeviceNum = 0
    while True:
        r = random.random()
        if r < 0.2:
            triggerEvent( 'NETWORK_LINK_DOWN', 'RUN_BLOCK', 'random', 'random' )
            downLinkNum += 1
            time.sleep( sleepTime )
        elif r < 0.4:
            triggerEvent( 'NETWORK_DEVICE_DOWN', 'RUN_BLOCK', 'random' )
            downDeviceNum += 1
            time.sleep( sleepTime * 2 )
        elif r < 0.7 and downLinkNum > 0:
            triggerEvent( 'NETWORK_LINK_UP', 'RUN_BLOCK', 'random', 'random' )
            downLinkNum -= 1
            time.sleep( sleepTime )
        elif downDeviceNum > 0:
            triggerEvent( 'NETWORK_DEVICE_UP', 'RUN_BLOCK', 'random' )
            downDeviceNum -= 1
            time.sleep( sleepTime * 2 )
        else:
            pass

if __name__ == '__main__':
    testLoop( 2 )
