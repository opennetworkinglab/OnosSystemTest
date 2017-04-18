import json
import time

class HA():

    def __init__( self ):
        self.default = ''

    def consistentCheck( self ):
        """
        Checks that TestON counters are consistent across all nodes.

        Returns the tuple (onosCounters, consistent)
        - onosCounters is the parsed json output of the counters command on
          all nodes
        - consistent is main.TRUE if all "TestON" counters are consitent across
          all nodes or main.FALSE
        """
        try:
            # Get onos counters results
            onosCountersRaw = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=utilities.retry,
                                 name="counters-" + str( i ),
                                 args=[ main.CLIs[i].counters, [ None ] ],
                                 kwargs= { 'sleep': 5, 'attempts': 5,
                                           'randomTime': True } )
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

            testCounters = {}
            # make a list of all the "TestON-*" counters in ONOS
            # lookes like a dict whose keys are the name of the ONOS node and
            # values are a list of the counters. I.E.
            # { "ONOS1": [ { "name":"TestON-Partitions","value":56} ]
            # }
            # NOTE: There is an assumtion that all nodes are active
            #        based on the above for loops
            for controller in enumerate( onosCounters ):
                for key, value in controller[1].iteritems():
                    if 'TestON' in key:
                        node = 'ONOS' + str( controller[0] + 1 )
                        try:
                            testCounters[node].append( { key: value } )
                        except KeyError:
                            testCounters[node] = [ { key: value } ]
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

    def counterCheck( self, counterName, counterValue ):
        """
        Checks that TestON counters are consistent across all nodes and that
        specified counter is in ONOS with the given value
        """
        try:
            correctResults = main.TRUE
            # Get onos counters results and consistentCheck
            onosCounters, consistent = self.consistentCheck()
            # Check for correct values
            for i in range( len( main.activeNodes ) ):
                current = onosCounters[i]
                onosValue = None
                try:
                    onosValue = current.get( counterName )
                except AttributeError:
                    node = str( main.activeNodes[i] + 1 )
                    main.log.exception( "ONOS" + node + " counters result " +
                                        "is not as expected" )
                    correctResults = main.FALSE
                if onosValue == counterValue:
                    main.log.info( counterName + " counter value is correct" )
                else:
                    main.log.error( counterName +
                                    " counter value is incorrect," +
                                    " expected value: " + str( counterValue ) +
                                    " current value: " + str( onosValue ) )
                    correctResults = main.FALSE
            return consistent and correctResults
        except Exception:
            main.log.exception( "" )
            main.cleanup()
            main.exit()

    def consistentLeaderboards( self, nodes ):
        TOPIC = 'org.onosproject.election'
        # FIXME: use threads
        # FIXME: should we retry outside the function?
        for n in range( 5 ):  # Retry in case election is still happening
            leaderList = []
            # Get all leaderboards
            for cli in nodes:
                leaderList.append( cli.specificLeaderCandidate( TOPIC ) )
            # Compare leaderboards
            result = all( i == leaderList[0] for i in leaderList ) and\
                     leaderList is not None
            main.log.debug( leaderList )
            main.log.warn( result )
            if result:
                return ( result, leaderList )
            time.sleep(5)  # TODO: paramerterize
        main.log.error( "Inconsistent leaderboards:" + str( leaderList ) )
        return ( result, leaderList )

    def nodesCheck( self, nodes ):
        nodesOutput = []
        results = True
        threads = []
        for i in nodes:
            t = main.Thread( target=main.CLIs[i].nodes,
                             name="nodes-" + str( i ),
                             args=[ ] )
            threads.append( t )
            t.start()

        for t in threads:
            t.join()
            nodesOutput.append( t.result )
        ips = [ main.nodes[node].ip_address for node in nodes ]
        ips.sort()
        for i in nodesOutput:
            try:
                current = json.loads( i )
                activeIps = []
                currentResult = False
                for node in current:
                    if node['state'] == 'READY':
                        activeIps.append( node['ip'] )
                activeIps.sort()
                if ips == activeIps:
                    currentResult = True
            except ( ValueError, TypeError ):
                main.log.error( "Error parsing nodes output" )
                main.log.warn( repr( i ) )
                currentResult = False
            results = results and currentResult
        return results

    def workQueueStatsCheck( self, workQueueName, completed, inProgress, pending ):
        # Completed
        threads = []
        completedValues = []
        for i in main.activeNodes:
            t = main.Thread( target=main.CLIs[i].workQueueTotalCompleted,
                             name="WorkQueueCompleted-" + str( i ),
                             args=[ workQueueName ] )
            threads.append( t )
            t.start()

        for t in threads:
            t.join()
            completedValues.append( int( t.result ) )
        # Check the results
        completedResults = [ x == completed for x in completedValues ]
        completedResult = all( completedResults )
        if not completedResult:
            main.log.warn( "Expected Work Queue {} to have {} completed, found {}".format(
                workQueueName, completed, completedValues ) )

        # In Progress
        threads = []
        inProgressValues = []
        for i in main.activeNodes:
            t = main.Thread( target=main.CLIs[i].workQueueTotalInProgress,
                             name="WorkQueueInProgress-" + str( i ),
                             args=[ workQueueName ] )
            threads.append( t )
            t.start()

        for t in threads:
            t.join()
            inProgressValues.append( int( t.result ) )
        # Check the results
        inProgressResults = [ x == inProgress for x in inProgressValues ]
        inProgressResult = all( inProgressResults )
        if not inProgressResult:
            main.log.warn( "Expected Work Queue {} to have {} inProgress, found {}".format(
                workQueueName, inProgress, inProgressValues ) )

        # Pending
        threads = []
        pendingValues = []
        for i in main.activeNodes:
            t = main.Thread( target=main.CLIs[i].workQueueTotalPending,
                             name="WorkQueuePending-" + str( i ),
                             args=[ workQueueName ] )
            threads.append( t )
            t.start()

        for t in threads:
            t.join()
            pendingValues.append( int( t.result ) )
        # Check the results
        pendingResults = [ x == pending for x in pendingValues ]
        pendingResult = all( pendingResults )
        if not pendingResult:
            main.log.warn( "Expected Work Queue {} to have {} pending, found {}".format(
                workQueueName, pending, pendingValues ) )
        return completedResult and inProgressResult and pendingResult

    def CASE17( self, main ):
        """
        Check for basic functionality with distributed primitives
        """
        # TODO: Clean this up so it's not just a cut/paste from the test
        try:
            # Make sure variables are defined/set
            assert main.numCtrls, "main.numCtrls not defined"
            assert utilities.assert_equals, "utilities.assert_equals not defined"
            assert main.CLIs, "main.CLIs not defined"
            assert main.nodes, "main.nodes not defined"
            assert main.pCounterName, "main.pCounterName not defined"
            assert main.onosSetName, "main.onosSetName not defined"
            # NOTE: assert fails if value is 0/None/Empty/False
            try:
                main.pCounterValue
            except NameError:
                main.log.error( "main.pCounterValue not defined, setting to 0" )
                main.pCounterValue = 0
            try:
                main.onosSet
            except NameError:
                main.log.error( "main.onosSet not defined, setting to empty Set" )
                main.onosSet = set([])
            # Variables for the distributed primitives tests. These are local only
            addValue = "a"
            addAllValue = "a b c d e f"
            retainValue = "c d e f"
            valueName = "TestON-Value"
            valueValue = None
            workQueueName = "TestON-Queue"
            workQueueCompleted = 0
            workQueueInProgress = 0
            workQueuePending = 0

            description = "Check for basic functionality with distributed " +\
                          "primitives"
            main.case( description )
            main.caseExplanation = "Test the methods of the distributed " +\
                                    "primitives (counters and sets) throught the cli"
            # DISTRIBUTED ATOMIC COUNTERS
            # Partitioned counters
            main.step( "Increment then get a default counter on each node" )
            pCounters = []
            threads = []
            addedPValues = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].counterTestAddAndGet,
                                 name="counterAddAndGet-" + str( i ),
                                 args=[ main.pCounterName ] )
                main.pCounterValue += 1
                addedPValues.append( main.pCounterValue )
                threads.append( t )
                t.start()

            for t in threads:
                t.join()
                pCounters.append( t.result )
            # Check that counter incremented numController times
            pCounterResults = True
            for i in addedPValues:
                tmpResult = i in pCounters
                pCounterResults = pCounterResults and tmpResult
                if not tmpResult:
                    main.log.error( str( i ) + " is not in partitioned "
                                    "counter incremented results" )
            utilities.assert_equals( expect=True,
                                     actual=pCounterResults,
                                     onpass="Default counter incremented",
                                     onfail="Error incrementing default" +
                                            " counter" )

            main.step( "Get then Increment a default counter on each node" )
            pCounters = []
            threads = []
            addedPValues = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].counterTestGetAndAdd,
                                 name="counterGetAndAdd-" + str( i ),
                                 args=[ main.pCounterName ] )
                addedPValues.append( main.pCounterValue )
                main.pCounterValue += 1
                threads.append( t )
                t.start()

            for t in threads:
                t.join()
                pCounters.append( t.result )
            # Check that counter incremented numController times
            pCounterResults = True
            for i in addedPValues:
                tmpResult = i in pCounters
                pCounterResults = pCounterResults and tmpResult
                if not tmpResult:
                    main.log.error( str( i ) + " is not in partitioned "
                                    "counter incremented results" )
            utilities.assert_equals( expect=True,
                                     actual=pCounterResults,
                                     onpass="Default counter incremented",
                                     onfail="Error incrementing default" +
                                            " counter" )

            main.step( "Counters we added have the correct values" )
            incrementCheck = main.HA.counterCheck( main.pCounterName, main.pCounterValue )
            utilities.assert_equals( expect=main.TRUE,
                                     actual=incrementCheck,
                                     onpass="Added counters are correct",
                                     onfail="Added counters are incorrect" )

            main.step( "Add -8 to then get a default counter on each node" )
            pCounters = []
            threads = []
            addedPValues = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].counterTestAddAndGet,
                                 name="counterIncrement-" + str( i ),
                                 args=[ main.pCounterName ],
                                 kwargs={ "delta": -8 } )
                main.pCounterValue += -8
                addedPValues.append( main.pCounterValue )
                threads.append( t )
                t.start()

            for t in threads:
                t.join()
                pCounters.append( t.result )
            # Check that counter incremented numController times
            pCounterResults = True
            for i in addedPValues:
                tmpResult = i in pCounters
                pCounterResults = pCounterResults and tmpResult
                if not tmpResult:
                    main.log.error( str( i ) + " is not in partitioned "
                                    "counter incremented results" )
            utilities.assert_equals( expect=True,
                                     actual=pCounterResults,
                                     onpass="Default counter incremented",
                                     onfail="Error incrementing default" +
                                            " counter" )

            main.step( "Add 5 to then get a default counter on each node" )
            pCounters = []
            threads = []
            addedPValues = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].counterTestAddAndGet,
                                 name="counterIncrement-" + str( i ),
                                 args=[ main.pCounterName ],
                                 kwargs={ "delta": 5 } )
                main.pCounterValue += 5
                addedPValues.append( main.pCounterValue )
                threads.append( t )
                t.start()

            for t in threads:
                t.join()
                pCounters.append( t.result )
            # Check that counter incremented numController times
            pCounterResults = True
            for i in addedPValues:
                tmpResult = i in pCounters
                pCounterResults = pCounterResults and tmpResult
                if not tmpResult:
                    main.log.error( str( i ) + " is not in partitioned "
                                    "counter incremented results" )
            utilities.assert_equals( expect=True,
                                     actual=pCounterResults,
                                     onpass="Default counter incremented",
                                     onfail="Error incrementing default" +
                                            " counter" )

            main.step( "Get then add 5 to a default counter on each node" )
            pCounters = []
            threads = []
            addedPValues = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].counterTestGetAndAdd,
                                 name="counterIncrement-" + str( i ),
                                 args=[ main.pCounterName ],
                                 kwargs={ "delta": 5 } )
                addedPValues.append( main.pCounterValue )
                main.pCounterValue += 5
                threads.append( t )
                t.start()

            for t in threads:
                t.join()
                pCounters.append( t.result )
            # Check that counter incremented numController times
            pCounterResults = True
            for i in addedPValues:
                tmpResult = i in pCounters
                pCounterResults = pCounterResults and tmpResult
                if not tmpResult:
                    main.log.error( str( i ) + " is not in partitioned "
                                    "counter incremented results" )
            utilities.assert_equals( expect=True,
                                     actual=pCounterResults,
                                     onpass="Default counter incremented",
                                     onfail="Error incrementing default" +
                                            " counter" )

            main.step( "Counters we added have the correct values" )
            incrementCheck = main.HA.counterCheck( main.pCounterName, main.pCounterValue )
            utilities.assert_equals( expect=main.TRUE,
                                     actual=incrementCheck,
                                     onpass="Added counters are correct",
                                     onfail="Added counters are incorrect" )

            # DISTRIBUTED SETS
            main.step( "Distributed Set get" )
            size = len( main.onosSet )
            getResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestGet,
                                 name="setTestGet-" + str( i ),
                                 args=[ main.onosSetName ] )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                getResponses.append( t.result )

            getResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                node = str( main.activeNodes[i] + 1 )
                if isinstance( getResponses[ i ], list):
                    current = set( getResponses[ i ] )
                    if len( current ) == len( getResponses[ i ] ):
                        # no repeats
                        if main.onosSet != current:
                            main.log.error( "ONOS" + node +
                                            " has incorrect view" +
                                            " of set " + main.onosSetName + ":\n" +
                                            str( getResponses[ i ] ) )
                            main.log.debug( "Expected: " + str( main.onosSet ) )
                            main.log.debug( "Actual: " + str( current ) )
                            getResults = main.FALSE
                    else:
                        # error, set is not a set
                        main.log.error( "ONOS" + node +
                                        " has repeat elements in" +
                                        " set " + main.onosSetName + ":\n" +
                                        str( getResponses[ i ] ) )
                        getResults = main.FALSE
                elif getResponses[ i ] == main.ERROR:
                    getResults = main.FALSE
            utilities.assert_equals( expect=main.TRUE,
                                     actual=getResults,
                                     onpass="Set elements are correct",
                                     onfail="Set elements are incorrect" )

            main.step( "Distributed Set size" )
            sizeResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestSize,
                                 name="setTestSize-" + str( i ),
                                 args=[ main.onosSetName ] )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                sizeResponses.append( t.result )

            sizeResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                node = str( main.activeNodes[i] + 1 )
                if size != sizeResponses[ i ]:
                    sizeResults = main.FALSE
                    main.log.error( "ONOS" + node +
                                    " expected a size of " + str( size ) +
                                    " for set " + main.onosSetName +
                                    " but got " + str( sizeResponses[ i ] ) )
            utilities.assert_equals( expect=main.TRUE,
                                     actual=sizeResults,
                                     onpass="Set sizes are correct",
                                     onfail="Set sizes are incorrect" )

            main.step( "Distributed Set add()" )
            main.onosSet.add( addValue )
            addResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestAdd,
                                 name="setTestAdd-" + str( i ),
                                 args=[ main.onosSetName, addValue ] )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                addResponses.append( t.result )

            # main.TRUE = successfully changed the set
            # main.FALSE = action resulted in no change in set
            # main.ERROR - Some error in executing the function
            addResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                if addResponses[ i ] == main.TRUE:
                    # All is well
                    pass
                elif addResponses[ i ] == main.FALSE:
                    # Already in set, probably fine
                    pass
                elif addResponses[ i ] == main.ERROR:
                    # Error in execution
                    addResults = main.FALSE
                else:
                    # unexpected result
                    addResults = main.FALSE
            if addResults != main.TRUE:
                main.log.error( "Error executing set add" )

            # Check if set is still correct
            size = len( main.onosSet )
            getResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestGet,
                                 name="setTestGet-" + str( i ),
                                 args=[ main.onosSetName ] )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                getResponses.append( t.result )
            getResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                node = str( main.activeNodes[i] + 1 )
                if isinstance( getResponses[ i ], list):
                    current = set( getResponses[ i ] )
                    if len( current ) == len( getResponses[ i ] ):
                        # no repeats
                        if main.onosSet != current:
                            main.log.error( "ONOS" + node + " has incorrect view" +
                                            " of set " + main.onosSetName + ":\n" +
                                            str( getResponses[ i ] ) )
                            main.log.debug( "Expected: " + str( main.onosSet ) )
                            main.log.debug( "Actual: " + str( current ) )
                            getResults = main.FALSE
                    else:
                        # error, set is not a set
                        main.log.error( "ONOS" + node + " has repeat elements in" +
                                        " set " + main.onosSetName + ":\n" +
                                        str( getResponses[ i ] ) )
                        getResults = main.FALSE
                elif getResponses[ i ] == main.ERROR:
                    getResults = main.FALSE
            sizeResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestSize,
                                 name="setTestSize-" + str( i ),
                                 args=[ main.onosSetName ] )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                sizeResponses.append( t.result )
            sizeResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                node = str( main.activeNodes[i] + 1 )
                if size != sizeResponses[ i ]:
                    sizeResults = main.FALSE
                    main.log.error( "ONOS" + node +
                                    " expected a size of " + str( size ) +
                                    " for set " + main.onosSetName +
                                    " but got " + str( sizeResponses[ i ] ) )
            addResults = addResults and getResults and sizeResults
            utilities.assert_equals( expect=main.TRUE,
                                     actual=addResults,
                                     onpass="Set add correct",
                                     onfail="Set add was incorrect" )

            main.step( "Distributed Set addAll()" )
            main.onosSet.update( addAllValue.split() )
            addResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestAdd,
                                 name="setTestAddAll-" + str( i ),
                                 args=[ main.onosSetName, addAllValue ] )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                addResponses.append( t.result )

            # main.TRUE = successfully changed the set
            # main.FALSE = action resulted in no change in set
            # main.ERROR - Some error in executing the function
            addAllResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                if addResponses[ i ] == main.TRUE:
                    # All is well
                    pass
                elif addResponses[ i ] == main.FALSE:
                    # Already in set, probably fine
                    pass
                elif addResponses[ i ] == main.ERROR:
                    # Error in execution
                    addAllResults = main.FALSE
                else:
                    # unexpected result
                    addAllResults = main.FALSE
            if addAllResults != main.TRUE:
                main.log.error( "Error executing set addAll" )

            # Check if set is still correct
            size = len( main.onosSet )
            getResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestGet,
                                 name="setTestGet-" + str( i ),
                                 args=[ main.onosSetName ] )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                getResponses.append( t.result )
            getResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                node = str( main.activeNodes[i] + 1 )
                if isinstance( getResponses[ i ], list):
                    current = set( getResponses[ i ] )
                    if len( current ) == len( getResponses[ i ] ):
                        # no repeats
                        if main.onosSet != current:
                            main.log.error( "ONOS" + node +
                                            " has incorrect view" +
                                            " of set " + main.onosSetName + ":\n" +
                                            str( getResponses[ i ] ) )
                            main.log.debug( "Expected: " + str( main.onosSet ) )
                            main.log.debug( "Actual: " + str( current ) )
                            getResults = main.FALSE
                    else:
                        # error, set is not a set
                        main.log.error( "ONOS" + node +
                                        " has repeat elements in" +
                                        " set " + main.onosSetName + ":\n" +
                                        str( getResponses[ i ] ) )
                        getResults = main.FALSE
                elif getResponses[ i ] == main.ERROR:
                    getResults = main.FALSE
            sizeResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestSize,
                                 name="setTestSize-" + str( i ),
                                 args=[ main.onosSetName ] )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                sizeResponses.append( t.result )
            sizeResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                node = str( main.activeNodes[i] + 1 )
                if size != sizeResponses[ i ]:
                    sizeResults = main.FALSE
                    main.log.error( "ONOS" + node +
                                    " expected a size of " + str( size ) +
                                    " for set " + main.onosSetName +
                                    " but got " + str( sizeResponses[ i ] ) )
            addAllResults = addAllResults and getResults and sizeResults
            utilities.assert_equals( expect=main.TRUE,
                                     actual=addAllResults,
                                     onpass="Set addAll correct",
                                     onfail="Set addAll was incorrect" )

            main.step( "Distributed Set contains()" )
            containsResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestGet,
                                 name="setContains-" + str( i ),
                                 args=[ main.onosSetName ],
                                 kwargs={ "values": addValue } )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                # NOTE: This is the tuple
                containsResponses.append( t.result )

            containsResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                if containsResponses[ i ] == main.ERROR:
                    containsResults = main.FALSE
                else:
                    containsResults = containsResults and\
                                      containsResponses[ i ][ 1 ]
            utilities.assert_equals( expect=main.TRUE,
                                     actual=containsResults,
                                     onpass="Set contains is functional",
                                     onfail="Set contains failed" )

            main.step( "Distributed Set containsAll()" )
            containsAllResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestGet,
                                 name="setContainsAll-" + str( i ),
                                 args=[ main.onosSetName ],
                                 kwargs={ "values": addAllValue } )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                # NOTE: This is the tuple
                containsAllResponses.append( t.result )

            containsAllResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                if containsResponses[ i ] == main.ERROR:
                    containsResults = main.FALSE
                else:
                    containsResults = containsResults and\
                                      containsResponses[ i ][ 1 ]
            utilities.assert_equals( expect=main.TRUE,
                                     actual=containsAllResults,
                                     onpass="Set containsAll is functional",
                                     onfail="Set containsAll failed" )

            main.step( "Distributed Set remove()" )
            main.onosSet.remove( addValue )
            removeResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestRemove,
                                 name="setTestRemove-" + str( i ),
                                 args=[ main.onosSetName, addValue ] )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                removeResponses.append( t.result )

            # main.TRUE = successfully changed the set
            # main.FALSE = action resulted in no change in set
            # main.ERROR - Some error in executing the function
            removeResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                if removeResponses[ i ] == main.TRUE:
                    # All is well
                    pass
                elif removeResponses[ i ] == main.FALSE:
                    # not in set, probably fine
                    pass
                elif removeResponses[ i ] == main.ERROR:
                    # Error in execution
                    removeResults = main.FALSE
                else:
                    # unexpected result
                    removeResults = main.FALSE
            if removeResults != main.TRUE:
                main.log.error( "Error executing set remove" )

            # Check if set is still correct
            size = len( main.onosSet )
            getResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestGet,
                                 name="setTestGet-" + str( i ),
                                 args=[ main.onosSetName ] )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                getResponses.append( t.result )
            getResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                node = str( main.activeNodes[i] + 1 )
                if isinstance( getResponses[ i ], list):
                    current = set( getResponses[ i ] )
                    if len( current ) == len( getResponses[ i ] ):
                        # no repeats
                        if main.onosSet != current:
                            main.log.error( "ONOS" + node +
                                            " has incorrect view" +
                                            " of set " + main.onosSetName + ":\n" +
                                            str( getResponses[ i ] ) )
                            main.log.debug( "Expected: " + str( main.onosSet ) )
                            main.log.debug( "Actual: " + str( current ) )
                            getResults = main.FALSE
                    else:
                        # error, set is not a set
                        main.log.error( "ONOS" + node +
                                        " has repeat elements in" +
                                        " set " + main.onosSetName + ":\n" +
                                        str( getResponses[ i ] ) )
                        getResults = main.FALSE
                elif getResponses[ i ] == main.ERROR:
                    getResults = main.FALSE
            sizeResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestSize,
                                 name="setTestSize-" + str( i ),
                                 args=[ main.onosSetName ] )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                sizeResponses.append( t.result )
            sizeResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                node = str( main.activeNodes[i] + 1 )
                if size != sizeResponses[ i ]:
                    sizeResults = main.FALSE
                    main.log.error( "ONOS" + node +
                                    " expected a size of " + str( size ) +
                                    " for set " + main.onosSetName +
                                    " but got " + str( sizeResponses[ i ] ) )
            removeResults = removeResults and getResults and sizeResults
            utilities.assert_equals( expect=main.TRUE,
                                     actual=removeResults,
                                     onpass="Set remove correct",
                                     onfail="Set remove was incorrect" )

            main.step( "Distributed Set removeAll()" )
            main.onosSet.difference_update( addAllValue.split() )
            removeAllResponses = []
            threads = []
            try:
                for i in main.activeNodes:
                    t = main.Thread( target=main.CLIs[i].setTestRemove,
                                     name="setTestRemoveAll-" + str( i ),
                                     args=[ main.onosSetName, addAllValue ] )
                    threads.append( t )
                    t.start()
                for t in threads:
                    t.join()
                    removeAllResponses.append( t.result )
            except Exception, e:
                main.log.exception(e)

            # main.TRUE = successfully changed the set
            # main.FALSE = action resulted in no change in set
            # main.ERROR - Some error in executing the function
            removeAllResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                if removeAllResponses[ i ] == main.TRUE:
                    # All is well
                    pass
                elif removeAllResponses[ i ] == main.FALSE:
                    # not in set, probably fine
                    pass
                elif removeAllResponses[ i ] == main.ERROR:
                    # Error in execution
                    removeAllResults = main.FALSE
                else:
                    # unexpected result
                    removeAllResults = main.FALSE
            if removeAllResults != main.TRUE:
                main.log.error( "Error executing set removeAll" )

            # Check if set is still correct
            size = len( main.onosSet )
            getResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestGet,
                                 name="setTestGet-" + str( i ),
                                 args=[ main.onosSetName ] )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                getResponses.append( t.result )
            getResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                node = str( main.activeNodes[i] + 1 )
                if isinstance( getResponses[ i ], list):
                    current = set( getResponses[ i ] )
                    if len( current ) == len( getResponses[ i ] ):
                        # no repeats
                        if main.onosSet != current:
                            main.log.error( "ONOS" + node +
                                            " has incorrect view" +
                                            " of set " + main.onosSetName + ":\n" +
                                            str( getResponses[ i ] ) )
                            main.log.debug( "Expected: " + str( main.onosSet ) )
                            main.log.debug( "Actual: " + str( current ) )
                            getResults = main.FALSE
                    else:
                        # error, set is not a set
                        main.log.error( "ONOS" + node +
                                        " has repeat elements in" +
                                        " set " + main.onosSetName + ":\n" +
                                        str( getResponses[ i ] ) )
                        getResults = main.FALSE
                elif getResponses[ i ] == main.ERROR:
                    getResults = main.FALSE
            sizeResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestSize,
                                 name="setTestSize-" + str( i ),
                                 args=[ main.onosSetName ] )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                sizeResponses.append( t.result )
            sizeResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                node = str( main.activeNodes[i] + 1 )
                if size != sizeResponses[ i ]:
                    sizeResults = main.FALSE
                    main.log.error( "ONOS" + node +
                                    " expected a size of " + str( size ) +
                                    " for set " + main.onosSetName +
                                    " but got " + str( sizeResponses[ i ] ) )
            removeAllResults = removeAllResults and getResults and sizeResults
            utilities.assert_equals( expect=main.TRUE,
                                     actual=removeAllResults,
                                     onpass="Set removeAll correct",
                                     onfail="Set removeAll was incorrect" )

            main.step( "Distributed Set addAll()" )
            main.onosSet.update( addAllValue.split() )
            addResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestAdd,
                                 name="setTestAddAll-" + str( i ),
                                 args=[ main.onosSetName, addAllValue ] )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                addResponses.append( t.result )

            # main.TRUE = successfully changed the set
            # main.FALSE = action resulted in no change in set
            # main.ERROR - Some error in executing the function
            addAllResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                if addResponses[ i ] == main.TRUE:
                    # All is well
                    pass
                elif addResponses[ i ] == main.FALSE:
                    # Already in set, probably fine
                    pass
                elif addResponses[ i ] == main.ERROR:
                    # Error in execution
                    addAllResults = main.FALSE
                else:
                    # unexpected result
                    addAllResults = main.FALSE
            if addAllResults != main.TRUE:
                main.log.error( "Error executing set addAll" )

            # Check if set is still correct
            size = len( main.onosSet )
            getResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestGet,
                                 name="setTestGet-" + str( i ),
                                 args=[ main.onosSetName ] )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                getResponses.append( t.result )
            getResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                node = str( main.activeNodes[i] + 1 )
                if isinstance( getResponses[ i ], list):
                    current = set( getResponses[ i ] )
                    if len( current ) == len( getResponses[ i ] ):
                        # no repeats
                        if main.onosSet != current:
                            main.log.error( "ONOS" + node +
                                            " has incorrect view" +
                                            " of set " + main.onosSetName + ":\n" +
                                            str( getResponses[ i ] ) )
                            main.log.debug( "Expected: " + str( main.onosSet ) )
                            main.log.debug( "Actual: " + str( current ) )
                            getResults = main.FALSE
                    else:
                        # error, set is not a set
                        main.log.error( "ONOS" + node +
                                        " has repeat elements in" +
                                        " set " + main.onosSetName + ":\n" +
                                        str( getResponses[ i ] ) )
                        getResults = main.FALSE
                elif getResponses[ i ] == main.ERROR:
                    getResults = main.FALSE
            sizeResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestSize,
                                 name="setTestSize-" + str( i ),
                                 args=[ main.onosSetName ] )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                sizeResponses.append( t.result )
            sizeResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                node = str( main.activeNodes[i] + 1 )
                if size != sizeResponses[ i ]:
                    sizeResults = main.FALSE
                    main.log.error( "ONOS" + node +
                                    " expected a size of " + str( size ) +
                                    " for set " + main.onosSetName +
                                    " but got " + str( sizeResponses[ i ] ) )
            addAllResults = addAllResults and getResults and sizeResults
            utilities.assert_equals( expect=main.TRUE,
                                     actual=addAllResults,
                                     onpass="Set addAll correct",
                                     onfail="Set addAll was incorrect" )

            main.step( "Distributed Set clear()" )
            main.onosSet.clear()
            clearResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestRemove,
                                 name="setTestClear-" + str( i ),
                                 args=[ main.onosSetName, " "],  # Values doesn't matter
                                 kwargs={ "clear": True } )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                clearResponses.append( t.result )

            # main.TRUE = successfully changed the set
            # main.FALSE = action resulted in no change in set
            # main.ERROR - Some error in executing the function
            clearResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                if clearResponses[ i ] == main.TRUE:
                    # All is well
                    pass
                elif clearResponses[ i ] == main.FALSE:
                    # Nothing set, probably fine
                    pass
                elif clearResponses[ i ] == main.ERROR:
                    # Error in execution
                    clearResults = main.FALSE
                else:
                    # unexpected result
                    clearResults = main.FALSE
            if clearResults != main.TRUE:
                main.log.error( "Error executing set clear" )

            # Check if set is still correct
            size = len( main.onosSet )
            getResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestGet,
                                 name="setTestGet-" + str( i ),
                                 args=[ main.onosSetName ] )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                getResponses.append( t.result )
            getResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                node = str( main.activeNodes[i] + 1 )
                if isinstance( getResponses[ i ], list):
                    current = set( getResponses[ i ] )
                    if len( current ) == len( getResponses[ i ] ):
                        # no repeats
                        if main.onosSet != current:
                            main.log.error( "ONOS" + node +
                                            " has incorrect view" +
                                            " of set " + main.onosSetName + ":\n" +
                                            str( getResponses[ i ] ) )
                            main.log.debug( "Expected: " + str( main.onosSet ) )
                            main.log.debug( "Actual: " + str( current ) )
                            getResults = main.FALSE
                    else:
                        # error, set is not a set
                        main.log.error( "ONOS" + node +
                                        " has repeat elements in" +
                                        " set " + main.onosSetName + ":\n" +
                                        str( getResponses[ i ] ) )
                        getResults = main.FALSE
                elif getResponses[ i ] == main.ERROR:
                    getResults = main.FALSE
            sizeResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestSize,
                                 name="setTestSize-" + str( i ),
                                 args=[ main.onosSetName ] )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                sizeResponses.append( t.result )
            sizeResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                node = str( main.activeNodes[i] + 1 )
                if size != sizeResponses[ i ]:
                    sizeResults = main.FALSE
                    main.log.error( "ONOS" + node +
                                    " expected a size of " + str( size ) +
                                    " for set " + main.onosSetName +
                                    " but got " + str( sizeResponses[ i ] ) )
            clearResults = clearResults and getResults and sizeResults
            utilities.assert_equals( expect=main.TRUE,
                                     actual=clearResults,
                                     onpass="Set clear correct",
                                     onfail="Set clear was incorrect" )

            main.step( "Distributed Set addAll()" )
            main.onosSet.update( addAllValue.split() )
            addResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestAdd,
                                 name="setTestAddAll-" + str( i ),
                                 args=[ main.onosSetName, addAllValue ] )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                addResponses.append( t.result )

            # main.TRUE = successfully changed the set
            # main.FALSE = action resulted in no change in set
            # main.ERROR - Some error in executing the function
            addAllResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                if addResponses[ i ] == main.TRUE:
                    # All is well
                    pass
                elif addResponses[ i ] == main.FALSE:
                    # Already in set, probably fine
                    pass
                elif addResponses[ i ] == main.ERROR:
                    # Error in execution
                    addAllResults = main.FALSE
                else:
                    # unexpected result
                    addAllResults = main.FALSE
            if addAllResults != main.TRUE:
                main.log.error( "Error executing set addAll" )

            # Check if set is still correct
            size = len( main.onosSet )
            getResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestGet,
                                 name="setTestGet-" + str( i ),
                                 args=[ main.onosSetName ] )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                getResponses.append( t.result )
            getResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                node = str( main.activeNodes[i] + 1 )
                if isinstance( getResponses[ i ], list):
                    current = set( getResponses[ i ] )
                    if len( current ) == len( getResponses[ i ] ):
                        # no repeats
                        if main.onosSet != current:
                            main.log.error( "ONOS" + node +
                                            " has incorrect view" +
                                            " of set " + main.onosSetName + ":\n" +
                                            str( getResponses[ i ] ) )
                            main.log.debug( "Expected: " + str( main.onosSet ) )
                            main.log.debug( "Actual: " + str( current ) )
                            getResults = main.FALSE
                    else:
                        # error, set is not a set
                        main.log.error( "ONOS" + node +
                                        " has repeat elements in" +
                                        " set " + main.onosSetName + ":\n" +
                                        str( getResponses[ i ] ) )
                        getResults = main.FALSE
                elif getResponses[ i ] == main.ERROR:
                    getResults = main.FALSE
            sizeResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestSize,
                                 name="setTestSize-" + str( i ),
                                 args=[ main.onosSetName ] )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                sizeResponses.append( t.result )
            sizeResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                node = str( main.activeNodes[i] + 1 )
                if size != sizeResponses[ i ]:
                    sizeResults = main.FALSE
                    main.log.error( "ONOS" + node +
                                    " expected a size of " + str( size ) +
                                    " for set " + main.onosSetName +
                                    " but got " + str( sizeResponses[ i ] ) )
            addAllResults = addAllResults and getResults and sizeResults
            utilities.assert_equals( expect=main.TRUE,
                                     actual=addAllResults,
                                     onpass="Set addAll correct",
                                     onfail="Set addAll was incorrect" )

            main.step( "Distributed Set retain()" )
            main.onosSet.intersection_update( retainValue.split() )
            retainResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestRemove,
                                 name="setTestRetain-" + str( i ),
                                 args=[ main.onosSetName, retainValue ],
                                 kwargs={ "retain": True } )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                retainResponses.append( t.result )

            # main.TRUE = successfully changed the set
            # main.FALSE = action resulted in no change in set
            # main.ERROR - Some error in executing the function
            retainResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                if retainResponses[ i ] == main.TRUE:
                    # All is well
                    pass
                elif retainResponses[ i ] == main.FALSE:
                    # Already in set, probably fine
                    pass
                elif retainResponses[ i ] == main.ERROR:
                    # Error in execution
                    retainResults = main.FALSE
                else:
                    # unexpected result
                    retainResults = main.FALSE
            if retainResults != main.TRUE:
                main.log.error( "Error executing set retain" )

            # Check if set is still correct
            size = len( main.onosSet )
            getResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestGet,
                                 name="setTestGet-" + str( i ),
                                 args=[ main.onosSetName ] )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                getResponses.append( t.result )
            getResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                node = str( main.activeNodes[i] + 1 )
                if isinstance( getResponses[ i ], list):
                    current = set( getResponses[ i ] )
                    if len( current ) == len( getResponses[ i ] ):
                        # no repeats
                        if main.onosSet != current:
                            main.log.error( "ONOS" + node +
                                            " has incorrect view" +
                                            " of set " + main.onosSetName + ":\n" +
                                            str( getResponses[ i ] ) )
                            main.log.debug( "Expected: " + str( main.onosSet ) )
                            main.log.debug( "Actual: " + str( current ) )
                            getResults = main.FALSE
                    else:
                        # error, set is not a set
                        main.log.error( "ONOS" + node +
                                        " has repeat elements in" +
                                        " set " + main.onosSetName + ":\n" +
                                        str( getResponses[ i ] ) )
                        getResults = main.FALSE
                elif getResponses[ i ] == main.ERROR:
                    getResults = main.FALSE
            sizeResponses = []
            threads = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].setTestSize,
                                 name="setTestSize-" + str( i ),
                                 args=[ main.onosSetName ] )
                threads.append( t )
                t.start()
            for t in threads:
                t.join()
                sizeResponses.append( t.result )
            sizeResults = main.TRUE
            for i in range( len( main.activeNodes ) ):
                node = str( main.activeNodes[i] + 1 )
                if size != sizeResponses[ i ]:
                    sizeResults = main.FALSE
                    main.log.error( "ONOS" + node + " expected a size of " +
                                    str( size ) + " for set " + main.onosSetName +
                                    " but got " + str( sizeResponses[ i ] ) )
            retainResults = retainResults and getResults and sizeResults
            utilities.assert_equals( expect=main.TRUE,
                                     actual=retainResults,
                                     onpass="Set retain correct",
                                     onfail="Set retain was incorrect" )

            # Transactional maps
            main.step( "Partitioned Transactional maps put" )
            tMapValue = "Testing"
            numKeys = 100
            putResult = True
            node = main.activeNodes[0]
            putResponses = main.CLIs[node].transactionalMapPut( numKeys, tMapValue )
            if putResponses and len( putResponses ) == 100:
                for i in putResponses:
                    if putResponses[ i ][ 'value' ] != tMapValue:
                        putResult = False
            else:
                putResult = False
            if not putResult:
                main.log.debug( "Put response values: " + str( putResponses ) )
            utilities.assert_equals( expect=True,
                                     actual=putResult,
                                     onpass="Partitioned Transactional Map put successful",
                                     onfail="Partitioned Transactional Map put values are incorrect" )

            main.step( "Partitioned Transactional maps get" )
            # FIXME: is this sleep needed?
            time.sleep( 5 )

            getCheck = True
            for n in range( 1, numKeys + 1 ):
                getResponses = []
                threads = []
                valueCheck = True
                for i in main.activeNodes:
                    t = main.Thread( target=main.CLIs[i].transactionalMapGet,
                                     name="TMap-get-" + str( i ),
                                     args=[ "Key" + str( n ) ] )
                    threads.append( t )
                    t.start()
                for t in threads:
                    t.join()
                    getResponses.append( t.result )
                for node in getResponses:
                    if node != tMapValue:
                        valueCheck = False
                if not valueCheck:
                    main.log.warn( "Values for key 'Key" + str( n ) + "' do not match:" )
                    main.log.warn( getResponses )
                getCheck = getCheck and valueCheck
            utilities.assert_equals( expect=True,
                                     actual=getCheck,
                                     onpass="Partitioned Transactional Map get values were correct",
                                     onfail="Partitioned Transactional Map values incorrect" )

            # DISTRIBUTED ATOMIC VALUE
            main.step( "Get the value of a new value" )
            threads = []
            getValues = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].valueTestGet,
                                 name="ValueGet-" + str( i ),
                                 args=[ valueName ] )
                threads.append( t )
                t.start()

            for t in threads:
                t.join()
                getValues.append( t.result )
            main.log.debug( getValues )
            # Check the results
            atomicValueGetResult = True
            expected = valueValue if valueValue is not None else "null"
            main.log.debug( "Checking for value of " + expected )
            for i in getValues:
                if i != expected:
                    atomicValueGetResult = False
            utilities.assert_equals( expect=True,
                                     actual=atomicValueGetResult,
                                     onpass="Atomic Value get successful",
                                     onfail="Error getting atomic Value " +
                                            str( valueValue ) + ", found: " +
                                            str( getValues ) )

            main.step( "Atomic Value set()" )
            valueValue = "foo"
            threads = []
            setValues = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].valueTestSet,
                                 name="ValueSet-" + str( i ),
                                 args=[ valueName, valueValue ] )
                threads.append( t )
                t.start()

            for t in threads:
                t.join()
                setValues.append( t.result )
            main.log.debug( setValues )
            # Check the results
            atomicValueSetResults = True
            for i in setValues:
                if i != main.TRUE:
                    atomicValueSetResults = False
            utilities.assert_equals( expect=True,
                                     actual=atomicValueSetResults,
                                     onpass="Atomic Value set successful",
                                     onfail="Error setting atomic Value" +
                                            str( setValues ) )

            main.step( "Get the value after set()" )
            threads = []
            getValues = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].valueTestGet,
                                 name="ValueGet-" + str( i ),
                                 args=[ valueName ] )
                threads.append( t )
                t.start()

            for t in threads:
                t.join()
                getValues.append( t.result )
            main.log.debug( getValues )
            # Check the results
            atomicValueGetResult = True
            expected = valueValue if valueValue is not None else "null"
            main.log.debug( "Checking for value of " + expected )
            for i in getValues:
                if i != expected:
                    atomicValueGetResult = False
            utilities.assert_equals( expect=True,
                                     actual=atomicValueGetResult,
                                     onpass="Atomic Value get successful",
                                     onfail="Error getting atomic Value " +
                                            str( valueValue ) + ", found: " +
                                            str( getValues ) )

            main.step( "Atomic Value compareAndSet()" )
            oldValue = valueValue
            valueValue = "bar"
            i = main.activeNodes[0]
            CASValue = main.CLIs[i].valueTestCompareAndSet( valueName, oldValue, valueValue )
            main.log.debug( CASValue )
            utilities.assert_equals( expect=main.TRUE,
                                     actual=CASValue,
                                     onpass="Atomic Value comapreAndSet successful",
                                     onfail="Error setting atomic Value:" +
                                            str( CASValue ) )

            main.step( "Get the value after compareAndSet()" )
            threads = []
            getValues = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].valueTestGet,
                                 name="ValueGet-" + str( i ),
                                 args=[ valueName ] )
                threads.append( t )
                t.start()

            for t in threads:
                t.join()
                getValues.append( t.result )
            main.log.debug( getValues )
            # Check the results
            atomicValueGetResult = True
            expected = valueValue if valueValue is not None else "null"
            main.log.debug( "Checking for value of " + expected )
            for i in getValues:
                if i != expected:
                    atomicValueGetResult = False
            utilities.assert_equals( expect=True,
                                     actual=atomicValueGetResult,
                                     onpass="Atomic Value get successful",
                                     onfail="Error getting atomic Value " +
                                            str( valueValue ) + ", found: " +
                                            str( getValues ) )

            main.step( "Atomic Value getAndSet()" )
            oldValue = valueValue
            valueValue = "baz"
            i = main.activeNodes[0]
            GASValue = main.CLIs[i].valueTestGetAndSet( valueName, valueValue )
            main.log.debug( GASValue )
            expected = oldValue if oldValue is not None else "null"
            utilities.assert_equals( expect=expected,
                                     actual=GASValue,
                                     onpass="Atomic Value GAS successful",
                                     onfail="Error with GetAndSet atomic Value: expected " +
                                            str( expected ) + ", found: " +
                                            str( GASValue ) )

            main.step( "Get the value after getAndSet()" )
            threads = []
            getValues = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].valueTestGet,
                                 name="ValueGet-" + str( i ),
                                 args=[ valueName ] )
                threads.append( t )
                t.start()

            for t in threads:
                t.join()
                getValues.append( t.result )
            main.log.debug( getValues )
            # Check the results
            atomicValueGetResult = True
            expected = valueValue if valueValue is not None else "null"
            main.log.debug( "Checking for value of " + expected )
            for i in getValues:
                if i != expected:
                    atomicValueGetResult = False
            utilities.assert_equals( expect=True,
                                     actual=atomicValueGetResult,
                                     onpass="Atomic Value get successful",
                                     onfail="Error getting atomic Value: expected " +
                                            str( valueValue ) + ", found: " +
                                            str( getValues ) )

            main.step( "Atomic Value destory()" )
            valueValue = None
            threads = []
            i = main.activeNodes[0]
            destroyResult = main.CLIs[i].valueTestDestroy( valueName )
            main.log.debug( destroyResult )
            # Check the results
            utilities.assert_equals( expect=main.TRUE,
                                     actual=destroyResult,
                                     onpass="Atomic Value destroy successful",
                                     onfail="Error destroying atomic Value" )

            main.step( "Get the value after destroy()" )
            threads = []
            getValues = []
            for i in main.activeNodes:
                t = main.Thread( target=main.CLIs[i].valueTestGet,
                                 name="ValueGet-" + str( i ),
                                 args=[ valueName ] )
                threads.append( t )
                t.start()

            for t in threads:
                t.join()
                getValues.append( t.result )
            main.log.debug( getValues )
            # Check the results
            atomicValueGetResult = True
            expected = valueValue if valueValue is not None else "null"
            main.log.debug( "Checking for value of " + expected )
            for i in getValues:
                if i != expected:
                    atomicValueGetResult = False
            utilities.assert_equals( expect=True,
                                     actual=atomicValueGetResult,
                                     onpass="Atomic Value get successful",
                                     onfail="Error getting atomic Value " +
                                            str( valueValue ) + ", found: " +
                                            str( getValues ) )

            # WORK QUEUES
            main.step( "Work Queue add()" )
            threads = []
            i = main.activeNodes[0]
            addResult = main.CLIs[i].workQueueAdd( workQueueName, 'foo' )
            workQueuePending += 1
            main.log.debug( addResult )
            # Check the results
            utilities.assert_equals( expect=main.TRUE,
                                     actual=addResult,
                                     onpass="Work Queue add successful",
                                     onfail="Error adding to Work Queue" )

            main.step( "Check the work queue stats" )
            statsResults = self.workQueueStatsCheck( workQueueName,
                                                     workQueueCompleted,
                                                     workQueueInProgress,
                                                     workQueuePending )
            utilities.assert_equals( expect=True,
                                     actual=statsResults,
                                     onpass="Work Queue stats correct",
                                     onfail="Work Queue stats incorrect " )

            main.step( "Work Queue addMultiple()" )
            threads = []
            i = main.activeNodes[0]
            addMultipleResult = main.CLIs[i].workQueueAddMultiple( workQueueName, 'bar', 'baz' )
            workQueuePending += 2
            main.log.debug( addMultipleResult )
            # Check the results
            utilities.assert_equals( expect=main.TRUE,
                                     actual=addMultipleResult,
                                     onpass="Work Queue add multiple successful",
                                     onfail="Error adding multiple items to Work Queue" )

            main.step( "Check the work queue stats" )
            statsResults = self.workQueueStatsCheck( workQueueName,
                                                     workQueueCompleted,
                                                     workQueueInProgress,
                                                     workQueuePending )
            utilities.assert_equals( expect=True,
                                     actual=statsResults,
                                     onpass="Work Queue stats correct",
                                     onfail="Work Queue stats incorrect " )

            main.step( "Work Queue takeAndComplete() 1" )
            threads = []
            i = main.activeNodes[0]
            number = 1
            take1Result = main.CLIs[i].workQueueTakeAndComplete( workQueueName, number )
            workQueuePending -= number
            workQueueCompleted += number
            main.log.debug( take1Result )
            # Check the results
            utilities.assert_equals( expect=main.TRUE,
                                     actual=take1Result,
                                     onpass="Work Queue takeAndComplete 1 successful",
                                     onfail="Error taking 1 from Work Queue" )

            main.step( "Check the work queue stats" )
            statsResults = self.workQueueStatsCheck( workQueueName,
                                                     workQueueCompleted,
                                                     workQueueInProgress,
                                                     workQueuePending )
            utilities.assert_equals( expect=True,
                                     actual=statsResults,
                                     onpass="Work Queue stats correct",
                                     onfail="Work Queue stats incorrect " )

            main.step( "Work Queue takeAndComplete() 2" )
            threads = []
            i = main.activeNodes[0]
            number = 2
            take2Result = main.CLIs[i].workQueueTakeAndComplete( workQueueName, number )
            workQueuePending -= number
            workQueueCompleted += number
            main.log.debug( take2Result )
            # Check the results
            utilities.assert_equals( expect=main.TRUE,
                                     actual=take2Result,
                                     onpass="Work Queue takeAndComplete 2 successful",
                                     onfail="Error taking 2 from Work Queue" )

            main.step( "Check the work queue stats" )
            statsResults = self.workQueueStatsCheck( workQueueName,
                                                     workQueueCompleted,
                                                     workQueueInProgress,
                                                     workQueuePending )
            utilities.assert_equals( expect=True,
                                     actual=statsResults,
                                     onpass="Work Queue stats correct",
                                     onfail="Work Queue stats incorrect " )

            main.step( "Work Queue destroy()" )
            valueValue = None
            threads = []
            i = main.activeNodes[0]
            destroyResult = main.CLIs[i].workQueueDestroy( workQueueName )
            workQueueCompleted = 0
            workQueueInProgress = 0
            workQueuePending = 0
            main.log.debug( destroyResult )
            # Check the results
            utilities.assert_equals( expect=main.TRUE,
                                     actual=destroyResult,
                                     onpass="Work Queue destroy successful",
                                     onfail="Error destroying Work Queue" )

            main.step( "Check the work queue stats" )
            statsResults = self.workQueueStatsCheck( workQueueName,
                                                     workQueueCompleted,
                                                     workQueueInProgress,
                                                     workQueuePending )
            utilities.assert_equals( expect=True,
                                     actual=statsResults,
                                     onpass="Work Queue stats correct",
                                     onfail="Work Queue stats incorrect " )
        except Exception as e:
            main.log.error( "Exception: " + str( e ) )
