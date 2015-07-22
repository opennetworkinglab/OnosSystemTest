def __init__( self ):
    self.default = ''

def counterCheck( counterName, counterValue ):
    """
    Add Text here
    """
    import json
    correctResults = main.TRUE
    # Get onos counters results
    onosCounters = []
    threads = []
    for i in range( main.numCtrls ):
        t = main.Thread( target=main.CLIs[i].counters,
                         name="counters-" + str( i ) )
        threads.append( t )
        t.start()
    for t in threads:
        t.join()
        onosCounters.append( t.result )
    tmp = [ i == onosCounters[ 0 ] for i in onosCounters ]
    if all( tmp ):
        consistent = main.TRUE
    else:
        consistent = main.FALSE
        main.log.error( "ONOS nodes have different values for counters" )
        for node in onosCounters:
            main.log.debug( node )

    # Check for correct values
    for i in range( main.numCtrls ):
        try:
            current = json.loads( onosCounters[i] )
        except ( ValueError, TypeError ):
            main.log.error( "Could not parse counters response from ONOS" +
                            str( i + 1 ) )
            main.log.warn( repr( onosCounters[ i ] ) )
        onosValue = None
        try:
            for database in current:
                database = database.values()[0]
                for counter in database:
                    if counter.get( 'name' ) == counterName:
                        onosValue = counter.get( 'value' )
                        break
        except AttributeError, e:
            main.log.error( "ONOS" + str( i + 1 ) + " counters result " +
                            "is not as expected" )
            correctResults = main.FALSE
        if onosValue == counterValue:
            main.log.info( counterName + " counter value is correct" )
        else:
            main.log.error( counterName + " counter value is incorrect," +
                            " expected value: " + str( counterValue )
                            + " current value: " + str( onosValue ) )
            correctResults = main.FALSE
    return consistent and correctResults
