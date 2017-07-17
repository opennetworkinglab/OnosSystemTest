"""
Copyright 2015 Open Networking Foundation (ONF)

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
    along with TestON.  If not, see <http://www.gnu.org/licenses/>


    These functions are for use with the Network config system
"""
import time


def compareCfg( main, gossipTime=None ):
    """
    Compare the network configurations across all nodes in the network
    gossipTime is the number of seconds each gossip round take for the netCfg maps
    """
    main.step( "Check net config" )
    if gossipTime:
        time.sleep( gossipTime * len( main.RESTs ) )
    responses = []
    result = utilities.retry( f=checkNodeResponses,
                              retValue=False,
                              kwargs={'main' : main,'responses' : responses},
                              sleep = main.retrysleep,
                              attempts = main.retrytimes )
    utilities.assert_equals( expect=True,
                             actual=result,
                             onpass="Net Cfg is the same on all nodes",
                             onfail="Check Net Cfg failed. Check above messages." )


def checkNodeResponses ( main, responses ):
    numberOfFailedNodes = 0  # Tracks the number of nodes that failed to get net configuration
    for node in main.RESTs:
        response = node.getNetCfg( )
        responses.append( node.pprint( response ) )
        if response == main.FALSE:
            numberOfFailedNodes += 1

    compare = [ i == responses[ 0 ] for i in responses ]
    if numberOfFailedNodes == 0 and all( compare ):
        return True

    # Failed, providing feedback on cli
    if numberOfFailedNodes > 0:
        main.log.warn( numberOfFailedNodes + " node(s) failed to GET Net Config" )
    if not all( compare ):
        main.log.debug( "Net Cfg is different on some nodes. Net Config results:" )
        for i in responses:
            main.log.debug( i )
    return False

def checkDeviceAnnotations( main, jsonObj, sw ):
    id = str( sw.get( 'id' ) )
    keys = [ 'name', 'owner', 'rackAddress' ]
    correct = True
    for k in keys:
        if str( sw.get( 'annotations', {} ).get( k ) ) != str( jsonObj[ k ] ) :
            correct = False
            main.log.debug( "{} is wrong on switch: ".format( k ) + id )
    if not correct:
        main.log.error( "Annotations for switch " + id  + " are incorrect: {}".format( sw ) )
    return correct


def checkAllDeviceAnnotations( main, json ):
    devices = main.ONOSrest1.devices( )
    id = "of:0000000000000001"
    i = 1
    result = [ ]
    try:
        for sw in json.loads( devices ):
            if id in sw.get( 'id' ):
                jsonObj = getattr( main, "s" + str( i ) + "Json" )
                isDeviceAnnotationCorrect = checkDeviceAnnotations( main, jsonObj, sw )
                result.append( isDeviceAnnotationCorrect )
                i += 1
                id = "of:000000000000000" + str( i )
    except( TypeError, ValueError ):
        main.log.error( "Problem loading device" )
        return False
    return all( result )
