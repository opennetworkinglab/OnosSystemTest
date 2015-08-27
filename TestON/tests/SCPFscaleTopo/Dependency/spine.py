#!/usr/bin/python

"""
Custom topology for Mininet
Author: kelvin@onlab.us
"""
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Host, RemoteController
from mininet.node import Node
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.util import dumpNodeConnections
from mininet.node import ( UserSwitch, OVSSwitch, IVSSwitch )
import sys
coreSwitches = {}
spineSwitches = {}
leafSwitches = {}
endSwitches = {}
allSwitches = {}
# Counters for nodes
totalSwitches = 0
totalEndSwitches = 0
totalHosts = 0
endSwitchCount = 0 # total count of end switch in each row in gui
class spineTopo( Topo ):

    def __init__( self, **opts ):
        "Create a topology."
        Topo.__init__( self, **opts )

    def build( self, s, l, c, e, h, **opts ):
        """
            s = number of spine switches
            l = number of leaf switches
            c = number of core
            e = number of end switch
            h = number of end host
        """
        global totalSwitches
        global coreSwitches
        global spineSwitches
        global leafSwitches
        global endSwitches
        global totalEndSwitches
        global totalHosts
        global allSwitches
        global endSwitchCount
        endSwitchCount = e

        print "Creating topology with", s,"spine", l,"leaf", c,"core",\
                e,"end switches and",h,"host for each end switches"

        self.addCore( c )
        self.addSpine( s )
        self.addLeaf( l )
        self.linkLayer( coreSwitches, spineSwitches )
        self.linkLayer( spineSwitches, leafSwitches )
        self.linkEndSwitch( e, leafSwitches )
        self.linkHosts( h )

        allSwitches = coreSwitches
        allSwitches.update( spineSwitches )
        allSwitches.update( leafSwitches )
        allSwitches.update( endSwitches )
        deviceData = self.createSwitchDict()
        self.genCfgJson( deviceData )


    def addCore( self, numSwitch ):
        global totalSwitches
        global coreSwitches
        for i in range( numSwitch ):
            coreSwitches[ 'core' + str( i + 1 ) ] = self.addSwitch(
                                             's' + str( totalSwitches + 1 ) )
            totalSwitches += 1

    def addSpine( self, numSwitch ):
        global totalSwitches
        global spineSwitches
        for i in range( numSwitch ):
            spineSwitches[ 'spine' + str( i + 1 ) ] = self.addSwitch(
                                                 's' + str( totalSwitches + 1 ) )
            totalSwitches += 1

    def addLeaf( self, numSwitch ):
        global totalSwitches
        global leafSwitches
        for i in range( numSwitch ):
            leafSwitches[ 'leaf' + str( i + 1 ) ] = self.addSwitch(
                                         's' + str( totalSwitches + 1 ) )
            totalSwitches += 1

    def addEnd( self ):
        global totalSwitches
        global totalEndSwitches
        global endSwitches

        endSwitches[ 'end' + str( totalEndSwitches + 1 ) ] = self.addSwitch(
                                      's' + str( totalSwitches + 1 ) )
        totalSwitches += 1
        totalEndSwitches += 1

        return endSwitches[ 'end' + str( totalEndSwitches ) ]

    def addEndHosts( self ):
        global totalHosts

        totalHosts += 1
        host = self.addHost( 'h' + str( totalHosts ) )

        return host


    def linkHosts( self, numHosts ):
        global endSwitches
        switches = sorted( endSwitches.values() )

        for sw in switches:
            for i in xrange( numHosts ):
                self.addLink( sw, self.addEndHosts() )


    def linkLayer( self, topLayer, botLayer ):
        """
        Description:
            The top layer is the upper layer in the spine topology eg. top layer
            can be the spine and the bottom layer is the leaf, another is the
            core layer is the top layer and the spine is the bottom layer and
            so on.
        Required:
            topLayer - Upper layer in the spine topology to be linked in the
                       layer below
            botLater - Layer that is below the upper layer to be linked at
        """

        topSwitches = sorted( topLayer.keys() )
        botSwitches = sorted( botLayer.keys() )

        for topSw in topSwitches:
            for botSw in botSwitches:
                self.addLink( topLayer.get( topSw ), botLayer.get( botSw ) )


    def linkEndSwitch( self, numSwitch, leafLayer ):
        global totalSwitches
        global totalEndSwitches

        leaf = sorted( leafLayer.values() )

        for i in xrange( len( leafSwitches ) ):
            if len( leafSwitches ) == 1:
                for j in xrange( numSwitch ):
                    self.addLink( leaf[ 0 ], self.addEnd() )
                break
            if len( leafSwitches ) == 2:
                for j in xrange( numSwitch ):
                    endSw = self.addEnd()
                    self.addLink( leaf[ i ], endSw )
                    self.addLink( leaf[ i + 1 ], endSw )
                break
            if i == ( len( leafSwitches ) - 1 ) and len( leafSwitches )%2:
                for j in xrange( numSwitch ):
                    self.addLink( leaf[ i ], self.addEnd() )
                break
            if i == 0:
                for j in xrange( numSwitch ):
                    endSw = self.addEnd()
                    self.addLink( leaf[ i ], endSw )
                    self.addLink( leaf[ i + 1 ], endSw )
                continue
            if i == 1:
                continue
            if i%2 == 0:
                for j in xrange( numSwitch ):
                    endSw = self.addEnd()
                    self.addLink( leaf[ i ], endSw )
                    self.addLink( leaf[ i + 1 ], endSw )

    def genCfgJson( self, deviceData ):
        import json
        configJson = {}
        configJson[ "devices" ] = deviceData
        with open( 'spine.json', 'w+' ) as outfile:
            json.dump( configJson, outfile )
        #cfgFile = open( "spine.json" , 'w+' )
        #cfgFile.write( configJson )
        #cfgFile.close()



    def createSwitchDict( self ):
        global allSwitches
        global endSwitchCount

        latitude = 0
        longitude = 0
        coreLong = -70
        spineLong = -80
        leafLong = -90
        endLat = 30
        rowCount = 0 # count of end switches or rows
        colOffSet = 0 # off set for end switches; longitude

        #for i in xrange( len( allSwitches ) ):
        deviceList = []
        deviceDict = {}
        for sw in allSwitches:
            tempSw = allSwitches.get( sw )
            uri = str( "{0:0>16}".format( str( hex( int( tempSw[ 1: ] ) )\
                            ).split( "x" )[ 1 ] ) )
            mac = str( "{0:0>12}".format( str( hex( int( tempSw[ 1: ] ) )\
                            ).split( "x" )[ 1 ] ) )

            if "core" in sw:
                latitude = 45
                longitude = coreLong
                coreLong += 2.5
            elif "spine" in sw:
                latitude = 40
                longitude = spineLong
                spineLong += 1.5
            elif "leaf" in sw:
                latitude = 35
                longitude = leafLong
                leafLong += 1.5
            elif "end" in sw:
                # Reset position and move to the right once every
                # number of end switches
                if rowCount == endSwitchCount:
                    colOffSet += 2.5
                    rowCount = 0
                    endLat = 30
                longitude = -80 + colOffSet
                latitude = endLat
                endLat -= 1
                rowCount += 1

            tempItem = { "alias": allSwitches.get( sw ) ,
                         "uri": "of:" + uri,
                         "mac": mac,
                         "annotations": { "name": sw,
                                          "latitude": latitude,
                                          "longitude": longitude },
                         "type": "SWITCH" }
            deviceList.append( tempItem )

        return deviceList
    #def createHostsJson( hostDict ):

topos = { 'spine': ( lambda s=2, l=3, c=1, e=5, h=1: spineTopo( s=s,
                                                                l=l,
                                                                c=c,
                                                                e=e,
                                                                h=h) ) }

# HERE THE CODE DEFINITION OF THE TOPOLOGY ENDS

def setupNetwork():
    "Create network"
    topo = spineTopo()
    #if controller_ip == '':
        #controller_ip = '10.0.2.2';
    #    controller_ip = '127.0.0.1';
    network = Mininet( topo=topo,
                       autoSetMacs=True,
                       controller=None )
    network.start()
    CLI( network )
    network.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    #setLogLevel('debug')
    setupNetwork()
