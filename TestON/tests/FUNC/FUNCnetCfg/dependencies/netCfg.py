"""
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
        time.sleep( gossipTime * len( main.nodes ) )
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
    for node in main.nodes:
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
