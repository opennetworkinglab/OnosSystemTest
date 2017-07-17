"""
Copyright 2016 Open Networking Foundation (ONF)

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.
"""

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
    request.append( 1 )
    request.append( type )
    request.append( scheduleMethod )
    for arg in args:
        request.append( arg )
    conn.send( request )
    response = conn.recv()
    while response == 11:
        conn.close()
        time.sleep( 1 )
        conn = Client( address )
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


def replayFromFile( filePath='/home/admin/event-list', sleepTime=1 ):
    try:
        f = open( filePath, 'r' )
        for line in f.readlines():
            event = line.split()
            if event[ 3 ].startswith( 'CHECK' ):
                continue
            triggerEvent( event[ 3 ], 'RUN_BLOCK', *event[ 4: ] )
            time.sleep( sleepTime )
        f.close()
    except Exception as e:
        print e

if __name__ == '__main__':
    #testLoop( 2 )
    replayFromFile()
