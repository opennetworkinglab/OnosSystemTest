def __init__( self ):
    self.default = ''

def consistentCheck():
    """
    Checks that TestON counters are consistent across all nodes.

    Returns the tuple (onosCounters, consistent)
    - onosCounters is the parsed json output of the counters command on all nodes
    - consistent is main.TRUE if all "TestON" counters are consitent across all
        nodes or main.FALSE
    """
    import json
    try:
        correctResults = main.TRUE
        # Get onos counters results
        onosCountersRaw = []
        threads = []
        for i in main.activeNodes:
            t = main.Thread( target=main.CLIs[i].counters,
                             name="counters-" + str( i ) )
            threads.append( t )
            t.start()
        for t in threads:
            t.join()
            onosCountersRaw.append( t.result )
        onosCounters = []
        for i in range( len( main.activeNodes ) ):
            try:
                onosCounters.append( json.loads( onosCountersRaw[i] ) )
            except ( ValueError, TypeError ):
                main.log.error( "Could not parse counters response from ONOS" +
                                str( main.activeNodes[i] + 1 ) )
                main.log.warn( repr( onosCountersRaw[ i ] ) )
                onosCounters.append( [] )
                return main.FALSE

        testCounters = {}
        # make a list of all the "TestON-*" counters in ONOS
        # lookes like a dict whose keys are the name of the ONOS node and values
        # are a list of the counters. I.E.
        # { "ONOS1": [ {"name":"TestON-inMemory","value":56},
        #              {"name":"TestON-Partitions","value":56} ]
        # }
        # NOTE: There is an assumtion that all nodes are active
        #        based on the above for loops
        for controller in enumerate( onosCounters ):
            for dbType in controller[1]:
                for dbName, items in dbType.iteritems():
                    for item in items:
                        if 'TestON' in item['name']:
                            node = 'ONOS' + str( main.activeNodes[ controller[0] ] + 1 )
                            try:
                                testCounters[node].append( item )
                            except KeyError:
                                testCounters[node] = [ item ]
        # compare the counters on each node
        firstV = testCounters.values()[0]
        tmp = [ v == firstV for k, v in testCounters.iteritems() ]
        if all( tmp ):
            consistent = main.TRUE
        else:
            consistent = main.FALSE
            main.log.error( "ONOS nodes have different values for counters:\n" +
                            testCounters )
        return ( onosCounters, consistent )
    except Exception:
        main.log.exception( "" )
        main.cleanup()
        main.exit()

def counterCheck( counterName, counterValue ):
    """
    Checks that TestON counters are consistent across all nodes and that
    specified counter is in ONOS with the given value
    """
    import json
    correctResults = main.TRUE
    # Get onos counters results and consistentCheck
    onosCounters, consistent = main.Counters.consistentCheck()
    # Check for correct values
    for i in range( len( main.activeNodes ) ):
        current = onosCounters[i]
        onosValue = None
        try:
            for database in current:
                database = database.values()[0]
                for counter in database:
                    if counter.get( 'name' ) == counterName:
                        onosValue = counter.get( 'value' )
                        break
        except AttributeError, e:
            node = str( main.activeNodes[i] + 1 )
            main.log.error( "ONOS" + node + " counters result " +
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
