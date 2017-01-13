'''
The functions for intentRerouteLat

'''
import numpy
import time

def _init_( self ):
    self.default = ''

def checkLog( main, nodeId ):
    try:
        logNames = main.ONOSbench.listLog( main.onosIp[ nodeId ] )
        assert logNames is not None
        if len( logNames ) >= 2:
            return 2
        return 1
    except AssertionError:
        main.log.error("There is no karaf log")
        return -1

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

def getValues( main ):
    '''
    Calculated the wanted values for intentRerouteTest

    1. Get the first "last topology timestamp" from karaf.log in different node
    2. Get the first "first intent installed timestamp" from  karaf log in different node
    3. Get the last "last intent installed timestamp" from karaf log in different node

    Return:
        last_topology_to_first_installed: The time from the last topology to the first intent installed
        first_installed_to_last_installed: Time time from the first topology to the last intent installed
        totalTime: The time from the last topology to the last intent installed

    '''
    lastTopologyTimestamp = compareTimestamp( main, main.searchTerm[ "TopologyTime" ], "creationTime=", ",",  'last',func='min' )
    firstIntentInstalledTimestamp = compareTimestamp( main, main.searchTerm[ "InstallTime" ], "time = ", " ",  'first',func='min' )
    lastIntentInstalledTimestamp = compareTimestamp( main, main.searchTerm[ "InstallTime" ], "time = ", " ",  'last',func='max' )

    if lastTopologyTimestamp == -1 or firstIntentInstalledTimestamp == -1 or lastIntentInstalledTimestamp == -1:
        main.log.warn( "Can't get timestamp from karaf log! " )
        bringBackTopology( main )
        return -1, -1, -1

    #calculate values
    lastTopologyToFirstInstalled = firstIntentInstalledTimestamp - lastTopologyTimestamp
    if lastTopologyToFirstInstalled < 0:
        main.record = main.record + 1

    firstInstalledToLastInstalled = lastIntentInstalledTimestamp - firstIntentInstalledTimestamp
    totalTime = lastIntentInstalledTimestamp - lastTopologyTimestamp

    if main.validRun >= main.warmUp and main.verify:
        main.log.info( "Last topology time stamp: {0:f}".format( lastTopologyTimestamp ))
        main.log.info( "First installed time stamp: {0:f}".format( firstIntentInstalledTimestamp ))
        main.log.info( "Last installed time stamp: {0:f}".format( lastIntentInstalledTimestamp ))
        main.log.info( "Last topology to first installed latency:{0:f}".format( lastTopologyToFirstInstalled ))
        main.log.info( "First installed to last installed latency:{0:f}".format( firstInstalledToLastInstalled ))
        main.log.info( "Overall latency:{0:f}".format( totalTime ))
        main.LatencyList.append( totalTime )
        main.LatencyListTopoToFirstInstalled.append( lastTopologyToFirstInstalled )
        main.LatencyListFirstInstalledToLastInstalled.append( firstInstalledToLastInstalled )
    return lastTopologyToFirstInstalled, firstInstalledToLastInstalled, totalTime

def compareTimestamp( main, compareTerm, splitTerm_before, splitTerm_after, mode, func='max' ):
    '''
    Compare all the timestamps of compareTerm from different node.

    func:
        max: Compare which one is the biggest and retun it
        min: Compare which one is the smallest and return it

    return:
        This function will return the biggest or smallest timestamps of the compareTerm.

    '''
    compareTermList = []
    for i in range( main.numCtrls ):
        timestamp = main.CLIs[ i ].getTimeStampFromLog( mode, compareTerm, splitTerm_before, splitTerm_after, startLine=main.totalLines[ i ], logNum=checkLog( main, i ) )
        compareTermList.append( timestamp )
    main.log.info("-----------------------------------------------")
    for i in range( main.numCtrls ):
        main.log.info( "ONOS Node {} {} {} time stamp: {}".format((i+1), mode, compareTerm, compareTermList[ i ]))
    x = min( compareTermList )
    main.log.info("-----------------------------------------------")
    if x == -1:
        main.log.warn( "Can't compare timestamps" )
        return -1
    else:
        if func == 'max':
            return max( compareTermList )
        if func == 'min':
            return min( compareTermList )
