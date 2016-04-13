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
        #FIXME: should we retry outside the function?
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
