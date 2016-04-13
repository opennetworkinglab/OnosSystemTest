"""
    These functions can be used for topology comparisons
"""

import time
import os
import json

def getAllDevices( main ):
    """
        Return a list containing the devices output from each ONOS node
    """
    devices = []
    threads = []
    for i in main.activeNodes:
        t = main.Thread( target=main.CLIs[i].devices,
                         name="devices-" + str( i ),
                         args=[ ] )
        threads.append( t )
        t.start()

    for t in threads:
        t.join()
        devices.append( t.result )
    return devices

def getAllHosts( main ):
    """
        Return a list containing the hosts output from each ONOS node
    """
    hosts = []
    ipResult = main.TRUE
    threads = []
    for i in main.activeNodes:
        t = main.Thread( target=main.CLIs[i].hosts,
                         name="hosts-" + str( i ),
                         args=[ ] )
        threads.append( t )
        t.start()

    for t in threads:
        t.join()
        hosts.append( t.result )
    return hosts

def getAllPorts( main ):
    """
        Return a list containing the ports output from each ONOS node
    """
    ports = []
    threads = []
    for i in main.activeNodes:
        t = main.Thread( target=main.CLIs[i].ports,
                         name="ports-" + str( i ),
                         args=[ ] )
        threads.append( t )
        t.start()

    for t in threads:
        t.join()
        ports.append( t.result )
    return ports

def getAllLinks( main ):
    """
        Return a list containing the links output from each ONOS node
    """
    links = []
    threads = []
    for i in main.activeNodes:
        t = main.Thread( target=main.CLIs[i].links,
                         name="links-" + str( i ),
                         args=[ ] )
        threads.append( t )
        t.start()

    for t in threads:
        t.join()
        links.append( t.result )
    return links

def getAllClusters( main ):
    """
        Return a list containing the clusters output from each ONOS node
    """
    clusters = []
    threads = []
    for i in main.activeNodes:
        t = main.Thread( target=main.CLIs[i].clusters,
                         name="clusters-" + str( i ),
                         args=[ ] )
        threads.append( t )
        t.start()

    for t in threads:
        t.join()
        clusters.append( t.result )
    return clusters


