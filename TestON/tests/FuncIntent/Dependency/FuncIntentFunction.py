"""
    Wrapper functions for FuncIntent
    This functions include Onosclidriver and Mininetclidriver driver functions
"""
def __init__( self ):
    self.default = ''

def hostIntent( main,
                name,
                host1,
                host2,
                host1Id="",
                host2Id="",
                mac1="",
                mac2="",
                vlan1="-1",
                vlan2="-1",
                sw1="",
                sw2="",
                expectedLink=0 ):
    """
        Add host intents
    """
    import time

    # Assert variables
    assert main, "There is no main variable"
    assert name, "variable name is empty"
    assert host1 and host2, "You must specify hosts"

    global itemName
    itemName = name
    h1Name = host1
    h2Name = host2
    h1Id = host1Id
    h2Id = host2Id
    h1Mac = mac1
    h2Mac = mac2
    vlan1 = vlan1
    vlan2 = vlan2
    intentsId = []
    stepResult = main.TRUE
    pingResult = main.TRUE
    intentResult = main.TRUE
    removeIntentResult = main.TRUE
    flowResult = main.TRUE
    topoResult = main.TRUE
    linkDownResult = main.TRUE
    linkUpResult = main.TRUE

    if main.hostsData:
        if not h1Mac:
            h1Mac = main.hostsData[ h1Name ][ 'mac' ]
        if not h2Mac:
            h2Mac = main.hostsData[ h2Name ][ 'mac' ]
        if main.hostsData[ h1Name ][ 'vlan' ] != '-1':
            vlan1 = main.hostsData[ h1Name ][ 'vlan' ]
        if main.hostsData[ h2Name ][ 'vlan' ] != '-1':
            vlan2 = main.hostsData[ h2Name ][ 'vlan' ]
        if not h1Id:
            h1Id = main.hostsData[ h1Name ][ 'id' ]
        if not h2Id:
            h2Id = main.hostsData[ h2Name ][ 'id' ]

    assert h1Id and h2Id, "You must specify host IDs"
    if not ( h1Id and h2Id ):
        main.log.info( "There are no host IDs" )
        return main.FALSE

    # Discover hosts using arping
    main.log.info( itemName + ": Discover host using arping" )
    main.Mininet1.arping( host=h1Name )
    main.Mininet1.arping( host=h2Name )
    host1 = main.CLIs[ 0 ].getHost( mac=h1Mac )
    host2 = main.CLIs[ 0 ].getHost( mac=h2Mac )

    # Adding host intents
    main.log.info( itemName + ": Adding host intents" )
    intent1 = main.CLIs[ 0 ].addHostIntent( hostIdOne=h1Id,
                                           hostIdTwo=h2Id )
    intentsId.append( intent1 )
    time.sleep( 5 )

    # Check intents state
    time.sleep( 30 )
    intentResult = checkIntentState( main, intentsId )

    # Verify flows
    checkFlowsState( main )

    # Ping hosts
    firstPingResult = pingHost( main, h1Name, h2Name )
    if not firstPingResult:
        main.log.info( "First ping failed, there must be" +
                       " something wrong with ONOS performance" )

    # Ping hosts again...
    pingResult = pingHost( main, h1Name, h2Name )
    time.sleep( 5 )

    # Test rerouting if these variables exist
    if sw1 and sw2 and expectedLink:
        # link down
        linkDownResult = link( main, sw1, sw2, "down" )
        intentResult = intentResult and checkIntentState( main, intentsId )

        # Verify flows
        checkFlowsState( main )

        # Check OnosTopology
        topoResult = checkTopology( main, expectedLink )

        # Ping hosts
        pingResult = pingResult and  pingHost( main, h1Name, h2Name )

        intentResult = checkIntentState( main, intentsId )

        # Checks ONOS state in link down
        if linkDownResult and topoResult and pingResult and intentResult:
            main.log.info( itemName + ": Successfully brought link down" )
        else:
            main.log.info( itemName + ": Failed to bring link down" )

        # link up
        linkUpResult = link( main, sw1, sw2, "up" )
        time.sleep( 5 )

        # Verify flows
        checkFlowsState( main )

        # Check OnosTopology
        topoResult = checkTopology( main, main.numLinks )

        # Ping hosts
        pingResult = pingResult and pingHost( main, h1Name, h2Name )

        intentResult = checkIntentState( main, intentsId )

        # Checks ONOS state in link up
        if linkUpResult and topoResult and pingResult and intentResult:
            main.log.info( itemName + ": Successfully brought link back up" )
        else:
            main.log.info( itemName + ": Failed to bring link back up" )

    # Remove all intents
    removeIntentResult = removeAllIntents( main, intentsId )

    stepResult = pingResult and linkDownResult and linkUpResult \
                 and intentResult and removeIntentResult

    return stepResult

def pointIntent( main,
                 name,
                 host1,
                 host2,
                 deviceId1,
                 deviceId2,
                 port1="",
                 port2="",
                 ethType="",
                 mac1="",
                 mac2="",
                 bandwidth="",
                 lambdaAlloc=False,
                 ipProto="",
                 ip1="",
                 ip2="",
                 tcp1="",
                 tcp2="",
                 sw1="",
                 sw2="",
                 expectedLink=0 ):
    """
        Add Point intents
    """
    import time
    assert main, "There is no main variable"
    assert name, "variable name is empty"
    assert host1 and host2, "You must specify hosts"

    global itemName
    itemName = name
    h1Name = host1
    h2Name = host2
    intentsId = []

    pingResult = main.TRUE
    intentResult = main.TRUE
    removeIntentResult = main.TRUE
    flowResult = main.TRUE
    topoResult = main.TRUE
    linkDownResult = main.TRUE
    linkUpResult = main.TRUE

    # Adding bidirectional point  intents
    main.log.info( itemName + ": Adding point intents" )
    intent1 = main.CLIs[ 0 ].addPointIntent( ingressDevice=deviceId1,
                                             egressDevice=deviceId2,
                                             portIngress=port1,
                                             portEgress=port2,
                                             ethType=ethType,
                                             ethSrc=mac1,
                                             ethDst=mac2,
                                             bandwidth=bandwidth,
                                             lambdaAlloc=lambdaAlloc,
                                             ipProto=ipProto,
                                             ipSrc=ip1,
                                             ipDst=ip2,
                                             tcpSrc=tcp1,
                                             tcpDst=tcp2 )

    intentsId.append( intent1 )
    time.sleep( 5 )
    intent2 = main.CLIs[ 0 ].addPointIntent( ingressDevice=deviceId2,
                                             egressDevice=deviceId1,
                                             portIngress=port2,
                                             portEgress=port1,
                                             ethType=ethType,
                                             ethSrc=mac2,
                                             ethDst=mac1,
                                             bandwidth=bandwidth,
                                             lambdaAlloc=lambdaAlloc,
                                             ipProto=ipProto,
                                             ipSrc=ip2,
                                             ipDst=ip1,
                                             tcpSrc=tcp2,
                                             tcpDst=tcp1 )
    intentsId.append( intent2 )

    # Check intents state
    time.sleep( 30 )
    intentResult = checkIntentState( main, intentsId )

    # Verify flows
    checkFlowsState( main )

    # Ping hosts
    firstPingResult = pingHost( main, h1Name, h2Name )
    if not firstPingResult:
        main.log.info( "First ping failed, there must be" +
                       " something wrong with ONOS performance" )

    # Ping hosts again...
    pingResult = pingHost( main, h1Name, h2Name )
    time.sleep( 5 )

    # Test rerouting if these variables exist
    if sw1 and sw2 and expectedLink:
        # link down
        linkDownResult = link( main, sw1, sw2, "down" )
        intentResult = intentResult and checkIntentState( main, intentsId )

        # Verify flows
        checkFlowsState( main )

        # Check OnosTopology
        topoResult = checkTopology( main, expectedLink )

        # Ping hosts
        pingResult = pingResult and  pingHost( main, h1Name, h2Name )

        intentResult = checkIntentState( main, intentsId )

        # Checks ONOS state in link down
        if linkDownResult and topoResult and pingResult and intentResult:
            main.log.info( itemName + ": Successfully brought link down" )
        else:
            main.log.info( itemName + ": Failed to bring link down" )

        # link up
        linkUpResult = link( main, sw1, sw2, "up" )
        time.sleep( 5 )

        # Verify flows
        checkFlowsState( main )

        # Check OnosTopology
        topoResult = checkTopology( main, main.numLinks )

        # Ping hosts
        pingResult = pingResult and pingHost( main, h1Name, h2Name )

        intentResult = checkIntentState( main, intentsId )

        # Checks ONOS state in link up
        if linkUpResult and topoResult and pingResult and intentResult:
            main.log.info( itemName + ": Successfully brought link back up" )
        else:
            main.log.info( itemName + ": Failed to bring link back up" )

    # Remove all intents
    removeIntentResult = removeAllIntents( main, intentsId )

    stepResult = pingResult and linkDownResult and linkUpResult \
                 and intentResult and removeIntentResult

    return stepResult

def singleToMultiIntent( main,
                         name,
                         hostNames,
                         devices="",
                         ports=None,
                         ethType="",
                         macs=None,
                         bandwidth="",
                         lambdaAlloc=False,
                         ipProto="",
                         ipAddresses="",
                         tcp="",
                         sw1="",
                         sw2="",
                         expectedLink=0 ):
    """
        Add Single to Multi Point intents
        If main.hostsData is not defined, variables data should be passed in the
        same order index wise. All devices in the list should have the same
        format, either all the devices have its port or it doesn't.
        eg. hostName = [ 'h1', 'h2' ,..  ]
            devices = [ 'of:0000000000000001', 'of:0000000000000002', ...]
            ports = [ '1', '1', ..]
            ...
    """
    import time
    import copy
    assert main, "There is no main variable"
    assert hostNames, "You must specify hosts"
    assert devices or main.hostsData, "You must specify devices"

    global itemName
    itemName = name
    tempHostsData = {}
    intentsId = []

    if hostNames and devices:
        if len( hostNames ) != len( devices ):
            main.log.error( "hosts and devices does not have the same length" )
            print "len hostNames = ", len( hostNames )
            print "len devices = ", len( devices )
            return main.FALSE
        if ports:
            if len( ports ) != len( devices ):
                main.log.error( "Ports and devices does " +
                                "not have the same length" )
                print "len devices = ", len( devices )
                print "len ports = ", len( ports )
                return main.FALSE
        else:
            main.log.info( "Device Ports are not specified" )
    elif hostNames and not devices and main.hostsData:
        main.log.info( "singleToMultiIntent function is using main.hostsData" ) 
        print main.hostsData

    print 'host names = ', hostNames
    print 'devices = ', devices

    macsDict = {}
    for i in range( len( devices ) ):
        macsDict[ devices[ i ] ] = macs[ i ]

    print "macsDict = ", macsDict

    pingResult = main.TRUE
    intentResult = main.TRUE
    removeIntentResult = main.TRUE
    flowResult = main.TRUE
    topoResult = main.TRUE
    linkDownResult = main.TRUE
    linkUpResult = main.TRUE

    devicesCopy = copy.copy( devices )
    if ports:
        portsCopy = copy.copy( ports )
    main.log.info( itemName + ": Adding single point to multi point intents" )
    # Adding bidirectional point  intents
    for i in range( len( devices ) ):
        ingressDevice = devicesCopy[ i ]
        egressDeviceList = copy.copy( devicesCopy )
        egressDeviceList.remove( ingressDevice )
        if ports:
            portIngress = portsCopy[ i ]
            portEgressList = copy.copy( portsCopy )
            del portEgressList[ i ]
        else:
            portIngress = ""
            portEgressList = None
        intentsId.append( main.CLIs[ 0 ].addSinglepointToMultipointIntent(
                                            ingressDevice=ingressDevice,
                                            egressDeviceList=egressDeviceList,
                                            portIngress=portIngress,
                                            portEgressList=portEgressList,
                                            ethType=ethType,
                                            ethSrc="",
                                            bandwidth=bandwidth,
                                            lambdaAlloc=lambdaAlloc,
                                            ipProto=ipProto,
                                            ipSrc="",
                                            ipDst="",
                                            tcpSrc="",
                                            tcpDst="" ) )

    pingHost( main, hostNames[ 0 ], hostNames[ 1 ] )
    pingHost( main, hostNames[ 0 ], hostNames[ 2 ] )
    pingHost( main, hostNames[ 1 ], hostNames[ 2 ] )
    pingHost( main, hostNames[ 1 ], hostNames[ 0 ] )
    pingHost( main, hostNames[ 2 ], hostNames[ 1 ] )
    pingHost( main, hostNames[ 2 ], hostNames[ 0 ] )
    return main.TRUE

    # Check intents state
    time.sleep( 30 )
    intentResult = checkIntentState( main, intentsId )

    # Verify flows
    checkFlowsState( main )

    # Ping hosts
    pingHost( main, h1Name, h2Name )
    # Ping hosts again...
    pingResult = pingHost( main, h1Name, h2Name )
    time.sleep( 5 )

    # Test rerouting if these variables exist
    if sw1 and sw2 and expectedLink:
        # link down
        linkDownResult = link( main, sw1, sw2, "down" )
        intentResult = intentResult and checkIntentState( main, intentsId )

        # Verify flows
        checkFlowsState( main )

        # Check OnosTopology
        topoResult = checkTopology( main, expectedLink )

        # Ping hosts
        pingResult = pingResult and  pingHost( main, h1Name, h2Name )

        intentResult = checkIntentState( main, intentsId )

        # Checks ONOS state in link down
        if linkDownResult and topoResult and pingResult and intentResult:
            main.log.info( itemName + ": Successfully brought link down" )
        else:
            main.log.info( itemName + ": Failed to bring link down" )

        # link up
        linkUpResult = link( main, sw1, sw2, "up" )
        time.sleep( 5 )

        # Verify flows
        checkFlowsState( main )

        # Check OnosTopology
        topoResult = checkTopology( main, main.numLinks )

        # Ping hosts
        pingResult = pingResult and pingHost( main, h1Name, h2Name )

        intentResult = checkIntentState( main, intentsId )

        # Checks ONOS state in link up
        if linkUpResult and topoResult and pingResult and intentResult:
            main.log.info( itemName + ": Successfully brought link back up" )
        else:
            main.log.info( itemName + ": Failed to bring link back up" )

    # Remove all intents
    removeIntentResult = removeAllIntents( main, intentsId )

    stepResult = pingResult and linkDownResult and linkUpResult \
                 and intentResult and removeIntentResult

    return stepResult

def pingHost( main, h1Name, h2Name ):

    # Ping hosts
    main.log.info( itemName + ": Ping " + h1Name + " and " +
                   h2Name )
    pingResult1 = main.Mininet1.pingHost( src=h1Name , target=h2Name )
    if not pingResult1:
        main.log.info( itemName + ": " + h1Name + " cannot ping "
                       + h2Name )
    pingResult2 = main.Mininet1.pingHost( src=h2Name , target=h1Name )
    if not pingResult2:
        main.log.info( itemName + ": " + h2Name + " cannot ping "
                       + h1Name )
    pingResult = pingResult1 and pingResult2
    if pingResult:
        main.log.info( itemName + ": Successfully pinged " +
                       "both hosts" )
    else:
        main.log.info( itemName + ": Failed to ping " +
                       "both hosts" )
    return pingResult

def pingAllHost( main, hosts ):
    # Ping all host in the hosts list variable
    import itertools
    print "Pinging : ", hosts
    hostCombination = itertools.permutations( hosts, 2 )
    pingResult = main.TRUE
    for hostPair in hostCombination:
        pingResult = pingResult and main.Mininet.pingHost(
                                                       src=hostPair[ 0 ],
                                                       target=hostPair[ 1 ] )
    return pingResult


def getHostsData( main ):
    """
        Use fwd app and pingall to discover all the hosts
    """
    """
        hosts json format:
    """
    import json
    activateResult = main.TRUE
    appCheck = main.TRUE
    main.log.info( "Activating reactive forwarding app " )
    activateResult = main.CLIs[ 0 ].activateApp( "org.onosproject.fwd" )

    for i in range( main.numCtrls ):
        appCheck = appCheck and main.CLIs[ i ].appToIDCheck()
        if appCheck != main.TRUE:
            main.log.warn( main.CLIs[ 0 ].apps() )
            main.log.warn( main.CLIs[ 0 ].appIDs() )

    pingResult = main.Mininet1.pingall()
    hostsJson = json.loads( main.CLIs[ 0 ].hosts() )
    hosts = main.Mininet1.getHosts()
    for host in hosts:
        main.hostsData[ host ] = {}
        main.hostsData[ host ][ 'mac' ] =  \
            main.Mininet1.getMacAddress( host ).upper()
        for hostj in hostsJson:
            if main.hostsData[ host ][ 'mac' ] == hostj[ 'mac' ]:
                main.hostsData[ host ][ 'id' ] = hostj[ 'id' ]
                main.hostsData[ host ][ 'vlan' ] = hostj[ 'vlan' ]
                main.hostsData[ host ][ 'location' ] = \
                            hostj[ 'location' ][ 'elementId' ] + '/' + \
                            hostj[ 'location' ][ 'port' ]
                main.hostsData[ host ][ 'ipAddresses' ] = hostj[ 'ipAddresses' ]

    main.log.info( "Deactivating reactive forwarding app " )
    deactivateResult = main.CLIs[ 0 ].deactivateApp( "org.onosproject.fwd" )
    if activateResult and deactivateResult and pingResult:
        main.log.info( "Successfully used fwd app to discover hosts " )
    else:
        main.log.info( "Failed to use fwd app to discover hosts " )

    main.log.info( "Hosts data:\n "+ main.hostsData )

    return pingResult

def checkTopology( main, expectedLink ):
    statusResult = main.TRUE
    # Check onos topology
    main.log.info( itemName + ": Checking ONOS topology " )

    for i in range( main.numCtrls ):
        topologyResult = main.CLIs[ i ].topology()
        statusResult = main.ONOSbench.checkStatus( topologyResult,
                                                   main.numSwitch,
                                                   expectedLink )\
                       and statusResult
    if not statusResult:
        main.log.info( itemName + ": Topology mismatch" )
    else:
        main.log.info( itemName + ": Topology match" )
    return statusResult

def checkIntentState( main, intentsId ):

    main.log.info( itemName + ": Check host intents state" )
    for i in range( main.numCtrls ):
        intentResult = main.CLIs[ i ].checkIntentState( intentsId=intentsId )
    if not intentResult:
        main.log.info( itemName +  ": Check host intents state again")
        for i in range( main.numCtrls ):
            intentResult = main.CLIs[ i ].checkIntentState(
                                                          intentsId=intentsId )
    return intentResult

def checkFlowsState( main ):

    main.log.info( itemName + ": Check flows state" )
    checkFlowsResult = main.CLIs[ 0 ].checkFlowsState()
    return checkFlowsResult

def link( main, sw1, sw2, option):

    # link down
    main.log.info( itemName + ": Bring link " + option + "between " +
                       sw1 + " and " + sw2 )
    linkResult = main.Mininet1.link( end1=sw1, end2=sw2, option=option )
    return linkResult

def removeAllIntents( main, intentsId ):
    """
        Remove all intents in the intentsId
    """
    import time
    intentsRemaining = []
    removeIntentResult = main.TRUE
    # Remove intents
    for intent in intentsId:
        main.CLIs[ 0 ].removeIntent( intentId=intent, purge=True )

    time.sleep( 5 )
    # Checks if there is remaining intents using intents()
    intentsRemaining = main.CLIs[ 0 ].intents()
    print intentsRemaining
    # If there is remianing intents then remove intents should fail
    if not intentsRemaining:
        main.log.info( itemName + ": There are " +
                       str( len( intentsRemaining ) ) + " intents remaining, "
                       + "failed to remove all the intents " )
        removeIntentResult = main.FALSE
    else:
        main.log.info( itemName + ": There are no intents remaining, " +
                       "successfully removed all the intents." )
        removeIntentResult = main.TRUE
    return removeIntentResult
