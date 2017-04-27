'''
The functions for intentRerouteLat

'''
import numpy
import time
import json

def _init_( self ):
    self.default = ''

def sanityCheck( main, linkNumExpected, flowNumExpected, intentNumExpected ):
    '''
    Sanity check on numbers of links, flows and intents in ONOS
    '''
    attemps = 0
    main.verify = main.FALSE
    linkNum = 0
    flowNum = 0
    intentNum = 0
    while attemps <= main.verifyAttempts:
        time.sleep(main.verifySleep)
        summary = json.loads( main.CLIs[0].summary( timeout=main.timeout ) )
        linkNum = summary.get("links")
        flowNum = summary.get("flows")
        intentNum = summary.get("intents")
        if linkNum == linkNumExpected and flowNum == flowNumExpected and intentNum == intentNumExpected:
            main.log.info("links: {}, flows: {}, intents: {}".format(linkNum, flowNum, intentNum))
            main.verify = main.TRUE
            break
        attemps += 1
    if not main.verify:
        main.log.warn("Links or flows or intents number not as expected")
        main.log.warn("links: {}, flows: {}, intents: {}".format(linkNum, flowNum, intentNum))
        # bring back topology
        bringBackTopology( main )
        if main.validRun >= main.warmUp:
            main.invalidRun += 1
        else:
            main.validRun += 1

def bringBackTopology( main ):
    main.log.info( "Bring back topology " )
    main.CLIs[ 0 ].pushTestIntents(main.ingress, main.egress, main.batchSize,
                                 offset=1, options="-w", timeout=main.timeout)
    main.CLIs[ 0 ].purgeWithdrawnIntents()
    main.CLIs[ 0 ].setCfg( "org.onosproject.provider.nil.NullProviders", "deviceCount", value=0)
    main.CLIs[ 0 ].setCfg( "org.onosproject.provider.nil.NullProviders", "enabled", value="false")
    main.CLIs[ 0 ].setCfg( "org.onosproject.provider.nil.NullProviders", "deviceCount", value=main.deviceCount)
    main.CLIs[ 0 ].setCfg( "org.onosproject.provider.nil.NullProviders", "enabled", value="true")
    main.CLIs[ 0 ].balanceMasters()
    time.sleep( main.setMasterSleep )
    if len( main.ONOSip ) > 1:
        main.CLIs[ 0 ].deviceRole(main.end1[ 'name' ], main.ONOSip[ 0 ])
        main.CLIs[ 0 ].deviceRole(main.end2[ 'name' ], main.ONOSip[ 0 ])
    time.sleep( main.setMasterSleep )

def getLogNum( main, nodeId ):
    '''
    Return the number of karaf log files
    '''
    try:
        logNameList = main.ONOSbench.listLog( main.onosIp[ nodeId ] )
        assert logNameList is not None
        # FIXME: are two karaf logs enough to cover the events we want?
        if len( logNameList ) >= 2:
            return 2
        return 1
    except AssertionError:
        main.log.error("There is no karaf log")
        return -1

def getTopologyTimestamps( main ):
    '''
    Get timestamps for the last topology events on all cluster nodes
    '''
    timestamps = []
    for i in range( main.numCtrls ):
        # Search for last topology event in karaf log
        lines = main.CLIs[ i ].logSearch( mode='last', searchTerm=main.searchTerm[ "TopologyTime" ], startLine=main.startLine[ i ], logNum=getLogNum( main, i ) )
        if lines is None or len( lines ) != 1:
            main.log.error( "Error when trying to get topology event timestamp" )
            return main.ERROR
        try:
            timestampField = lines[0].split( "creationTime=" )
            timestamp = timestampField[ 1 ].split( "," )
            timestamp = int( timestamp[ 0 ] )
            timestamps.append( timestamp )
        except KeyError:
            main.log.error( "Error when trying to get intent key or timestamp" )
            return main.ERROR
    return timestamps

def getIntentTimestamps( main ):
    '''
    Get timestamps for all intent keys on all cluster nodes
    '''
    timestamps = {}
    for i in range( main.numCtrls ):
        # Search for intent INSTALLED event in karaf log
        lines = main.CLIs[ i ].logSearch( mode='all', searchTerm=main.searchTerm[ "InstallTime" ], startLine=main.startLine[ i ], logNum=getLogNum( main, i ) )
        if lines is None or len( lines ) == 0:
            main.log.error( "Error when trying to get intent key or timestamp" )
            return main.ERROR
        for line in lines:
            try:
                # Get intent key
                keyField = line.split( "key=" )
                key = keyField[ 1 ].split( "," )
                key = key[ 0 ]
                if not key in timestamps.keys():
                    timestamps[ key ] = []
                # Get timestamp
                timestampField = line.split( "time = " )
                timestamp = timestampField[ 1 ].split( " " )
                timestamp = int( timestamp[ 0 ] )
                timestamps[ key ].append( timestamp )
            except KeyError:
                main.log.error( "Error when trying to get intent key or timestamp" )
                return main.ERROR
    return timestamps

def calculateLatency( main, topologyTimestamps, intentTimestamps ):
    '''
    Calculate reroute latency values using timestamps
    '''
    topologyTimestamp = numpy.min( topologyTimestamps )
    firstInstalledLatency = {}
    lastInstalledLatency = {}
    for key in intentTimestamps.keys():
        firstInstalledTimestamp = numpy.min( intentTimestamps[ key ] )
        lastInstalledTimestamp = numpy.max( intentTimestamps[ key ] )
        firstInstalledLatency[ key ] = firstInstalledTimestamp - topologyTimestamp
        lastInstalledLatency[ key ] = lastInstalledTimestamp - topologyTimestamp
    firstLocalLatnecy = numpy.min( firstInstalledLatency.values() )
    lastLocalLatnecy = numpy.max( firstInstalledLatency.values() )
    firstGlobalLatency = numpy.min( lastInstalledLatency.values() )
    lastGlobalLatnecy = numpy.max( lastInstalledLatency.values() )
    main.log.info( "firstLocalLatnecy: {}, lastLocalLatnecy: {}, firstGlobalLatency: {}, lastGlobalLatnecy: {}".format( firstLocalLatnecy, lastLocalLatnecy, firstGlobalLatency, lastGlobalLatnecy ) )
    return firstLocalLatnecy, lastLocalLatnecy, firstGlobalLatency, lastGlobalLatnecy
