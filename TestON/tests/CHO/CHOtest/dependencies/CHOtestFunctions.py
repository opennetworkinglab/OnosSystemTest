"""
Wrapper functions for CHOtest
Author: you@onlab.us
"""

def __init__( self ):
    self.default = ''

def installHostIntents():
    """
    Install one host intent for each combination of hosts in the topology
    """
    import itertools
    import time

    hostCombos = list( itertools.combinations( main.hostMACs, 2 ) )
    intentIdList = []
    for i in xrange( 0, len( hostCombos ), int( main.numCtrls ) ):
        pool = []
        for cli in main.CLIs:
            if i >= len( hostCombos ):
                break
            t = main.Thread( target=cli.addHostIntent,
                             threadID=main.threadID,
                             name="addHostIntent",
                             args=[hostCombos[i][0],
                                   hostCombos[i][1]])
            pool.append(t)
            t.start()
            i = i + 1
            main.threadID = main.threadID + 1
        for thread in pool:
            thread.join()
            intentIdList.append( thread.result )

    return intentIdList

def installPointIntents():
    """
    Install one point intent for each permutation of devices in the topology
    """
    import itertools
    import time

    if main.prefix == 2:
        # Spine-leaf topology is a special case
        for i in range( len( main.hostMACs ) ):
            main.MACsDict[ main.deviceDPIDs[ i+10 ] ] = main.hostMACs[ i ].split('/')[0]
        deviceCombos = list( itertools.permutations( main.deviceDPIDs[10:], 2 ) )
    else:
        deviceCombos = list( itertools.permutations( main.deviceDPIDs, 2 ) )
    intentIdList = []
    time1 = time.time()
    for i in xrange( 0, len( deviceCombos ), int( main.numCtrls ) ):
        pool = []
        for cli in main.CLIs:
            if i >= len( deviceCombos ):
                break
            t = main.Thread( target=cli.addPointIntent,
                             threadID=main.threadID,
                             name="addPointIntent",
                             args=[ deviceCombos[i][0],
                                    deviceCombos[i][1],
                                    1, 1, '',
                                    main.MACsDict.get( deviceCombos[i][0] ),
                                    main.MACsDict.get( deviceCombos[i][1] ) ] )
            pool.append(t)
            t.start()
            i = i + 1
            main.threadID = main.threadID + 1
        for thread in pool:
            thread.join()
            intentIdList.append( thread.result )
    time2 = time.time()
    main.log.info("Time taken for adding point intents: %2f seconds" %( time2 - time1 ) )

    return intentIdList

def checkIntents():
    """
    Check if all the intents are in INSTALLED state
    """
    import time

    intentResult = main.TRUE
    for i in range( main.intentCheck ):
        if i != 0:
            main.log.warn( "Verification failed. Retrying..." )
        main.log.info("Waiting for onos to install intents...")
        time.sleep( main.checkIntentsDelay )

        intentResult = main.TRUE
        for e in range(int(main.numCtrls)):
            main.log.info( "Checking intents on CLI %s" % (e+1) )
            intentResultIndividual = main.CLIs[e].checkIntentState( intentsId=main.intentIds )
            if not intentResultIndividual:
                main.log.warn( "Not all intents installed on ONOS%s" % (e+1) )
            intentResult = intentResult and intentResultIndividual
        if intentResult:
            break
    if not intentResult:
        main.log.info( "**** Intent Summary ****\n" + str(main.ONOScli1.intents( jsonFormat=False, summary=True)) )

    return intentResult

def checkPingall( protocol="IPv4" ):
    """
    Verify ping across all hosts
    """
    import time

    pingResult = main.TRUE
    for i in range( main.numPings ):
        if i != 0:
            main.log.warn( "Pingall failed. Retrying..." )
            main.log.info( "Giving ONOS some time...")
            time.sleep( main.pingSleep )

        pingResult = main.Mininet1.pingall( protocol=protocol, timeout=main.pingTimeout )
        if pingResult:
            break

    return pingResult

def checkLinkEvents( linkEvent, linkNum ):
    """
    Verify link down/up events are correctly discovered by ONOS
    linkNum: the correct link number after link down/up
    """
    import time

    linkResult = main.TRUE
    for i in range( main.linkCheck ):
        if i != 0:
            main.log.warn( "Verification failed. Retrying..." )
            main.log.info( "Giving ONOS some time..." )
            time.sleep( main.linkSleep )

        linkResult = main.TRUE
        for e in range( int( main.numCtrls ) ):
            main.log.info( "Checking link number on ONOS%s" % (e+1) )
            linkResultIndividual = main.CLIs[e].checkStatus( main.numMNswitches,
                                                               str( linkNum ) )
            if not linkResultIndividual:
                main.log.warn( "Link %s not discovered by ONOS%s" % ( linkEvent, (e+1) ) )
            linkResult = linkResult and linkResultIndividual
        if linkResult:
            break

    return linkResult
