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
    failMsg = "Net Cfg is different on some nodes."
    failed = False
    for node in main.nodes:
        response = node.getNetCfg( )
        responses.append( node.pprint( response ) )
        if response == main.FALSE:
            failed = True
    compare = [ i == responses[0] for i in responses ]
    if failed:
        failMsg += " Some nodes failed to GET netCfg."
    utilities.assert_equals( expect=True,
                             actual=all( compare ),
                             onpass="Net Cfg is the same on all nodes",
                             onfail=failMsg )
    if not all( compare ):
        main.log.debug( "Net Config results:" )
        for i in responses:
            main.log.debug( i )
