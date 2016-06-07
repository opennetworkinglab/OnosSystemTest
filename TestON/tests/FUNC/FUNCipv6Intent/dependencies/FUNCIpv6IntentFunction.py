"""
    Wrapper functions for FuncIntent
    This functions include Onosclidriver and Mininetclidriver driver functions
    Author: subhash_singh@criterionnetworks.com
"""
import time
import copy
import json

def __init__( self ):
    self.default = ''

def hostIntent( main,
                name,
                host1,
                host2,
                onosNode=0,
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
    Description:
        Verify add-host-intent
    Steps:
        - Discover hosts
        - Add host intents
        - Check intents
        - Verify flows
        - Ping hosts
        - Reroute
            - Link down
            - Verify flows
            - Check topology
            - Ping hosts
            - Link up
            - Verify flows
            - Check topology
            - Ping hosts
        - Remove intents
    Required:
        name - Type of host intent to add eg. IPV4 | VLAN | Dualstack
        host1 - Name of first host
        host2 - Name of second host
    Optional:
        onosNode - ONOS node to install the intents in main.CLIs[ ]
                   0 by default so that it will always use the first
                   ONOS node
        host1Id - ONOS id of the first host eg. 00:00:00:00:00:01/-1
        host2Id - ONOS id of the second host
        mac1 - Mac address of first host
        mac2 - Mac address of the second host
        vlan1 - Vlan tag of first host, defaults to -1
        vlan2 - Vlan tag of second host, defaults to -1
        sw1 - First switch to bring down & up for rerouting purpose
        sw2 - Second switch to bring down & up for rerouting purpose
        expectedLink - Expected link when the switches are down, it should
                       be two links lower than the links before the two
                       switches are down
    Return:
        Returns main.TRUE if all verification passed, otherwise return
        main.FALSE; returns main.FALSE if there is a key error
    """

    # Assert variables
    assert main, "There is no main variable"
    assert name, "variable name is empty"
    assert host1 and host2, "You must specify hosts"

    global itemName
    itemName = name
    h1Id = host1Id
    h2Id = host2Id
    h1Mac = mac1
    h2Mac = mac2
    vlan1 = vlan1
    vlan2 = vlan2
    hostNames = [ host1 , host2 ]
    intentsId = []
    stepResult = main.TRUE
    pingResult = main.TRUE
    intentResult = main.TRUE
    removeIntentResult = main.TRUE
    flowResult = main.TRUE
    topoResult = main.TRUE
    linkDownResult = main.TRUE
    linkUpResult = main.TRUE
    onosNode = int( onosNode )

    try:
        if main.hostsData:
            if not h1Mac:
                h1Mac = main.hostsData[ host1 ][ 'mac' ]
            if not h2Mac:
                h2Mac = main.hostsData[ host2 ][ 'mac' ]
            if main.hostsData[ host1 ].get( 'vlan' ):
                vlan1 = main.hostsData[ host1 ][ 'vlan' ]
            if main.hostsData[ host1 ].get( 'vlan' ):
                vlan2 = main.hostsData[ host2 ][ 'vlan' ]
            if not h1Id:
                h1Id = main.hostsData[ host1 ][ 'id' ]
            if not h2Id:
                h2Id = main.hostsData[ host2 ][ 'id' ]

        assert h1Id and h2Id, "You must specify host IDs"
        if not ( h1Id and h2Id ):
            main.log.info( "There are no host IDs" )
            return main.FALSE

    except KeyError:
        main.log.error( itemName + ": Key error Exception" )
        return main.FALSE

    # Check flows count in each node
    checkFlowsCount( main )

    # Adding host intents
    main.log.info( itemName + ": Adding host intents" )
    intent1 = main.CLIs[ onosNode ].addHostIntent( hostIdOne=h1Id,
                                                   hostIdTwo=h2Id )
    intentsId.append( intent1 )

    # Check intents state
    time.sleep( main.checkIntentSleep )
    intentResult = checkIntentState( main, intentsId )
    checkFlowsCount( main )

    # Check intents state again if first check fails...
    if not intentResult:
        intentResult = checkIntentState( main, intentsId )
        if intentResult:
            main.assertReturnString += 'Initial Intent State Passed\n'
        else:
            main.assertReturnString += 'Initial Intent State Failed\n'

    # Check flows count in each node
    FlowResult = checkFlowsCount( main )
    if FlowResult:
        main.assertReturnString += 'Initial Flow Count Passed\n'
    else:
        main.assertReturnString += 'Initial Flow Count Failed\n'
    # Verify flows
    StateResult = checkFlowsState( main )
    if StateResult:
        main.assertReturnString += 'Initial Flow State Passed\n'
    else:
        main.assertReturnString += 'Initial Flow State Failed\n'

    # Ping hosts
    firstPingResult = main.Mininet1.ping6pair(SRC=hostNames[0], TARGET=main.hostsData[ host2 ][ 'ipAddresses' ][ 0 ])
    if not firstPingResult:
        main.log.debug( "First ping failed, there must be" +
                       " something wrong with ONOS performance" )

    # Ping hosts again...
    pingTemp = ping6allHosts( main, hostNames )
    pingResult = pingResult and pingTemp
    if pingTemp:
        main.assertReturnString += 'Initial Ping6all Passed\n'
    else:
        main.assertReturnString += 'Initial Ping6all Failed\n'

    # Test rerouting if these variables exist
    if sw1 and sw2 and expectedLink:
        # Link down
        linkDownResult = link( main, sw1, sw2, "down" )

        if linkDownResult:
            main.assertReturnString += 'Link Down Passed\n'
        else:
            main.assertReturnString += 'Link Down Failed\n'

        # Check flows count in each node
        checkFlowsCount( main )
        # Verify flows
        checkFlowsState( main )

        # Check OnosTopology
        topoResult = checkTopology( main, expectedLink )
        if topoResult:
            main.assertReturnString += 'Link Down Topology State Passed\n'
        else:
            main.assertReturnString += 'Link Down Topology State Failed\n'

        # Ping hosts
        pingTemp = ping6allHosts( main, hostNames )
        pingResult = pingResult and pingTemp

        if pingTemp:
            main.assertReturnString += 'Link Down Ping6all Passed\n'
        else:
            main.assertReturnString += 'Link Down Ping6all Failed\n'

        # Check intent states
        intentTemp = checkIntentState( main, intentsId )
        intentResult = intentResult and intentTemp
        if intentTemp:
            main.assertReturnString += 'Link Down Intent State Passed\n'
        else:
            main.assertReturnString += 'Link Down Intent State Failed\n'

        # Checks ONOS state in link down
        if linkDownResult and topoResult and pingResult and intentResult:
            main.log.info( itemName + ": Successfully brought link down" )
        else:
            main.log.error( itemName + ": Failed to bring link down" )

        # Link up
        linkUpResult = link( main, sw1, sw2, "up" )
        time.sleep( main.rerouteSleep )

        if linkUpResult:
            main.assertReturnString += 'Link Up Passed\n'
        else:
            main.assertReturnString += 'Link Up Failed\n'

        # Check flows count in each node
        checkFlowsCount( main )
        # Verify flows
        checkFlowsState( main )

        # Check OnosTopology
        topoResult = checkTopology( main, main.numLinks )

        if topoResult:
            main.assertReturnString += 'Link Up Topology State Passed\n'
        else:
            main.assertReturnString += 'Link Up Topology State Failed\n'

        # Ping hosts
        pingTemp = ping6allHosts( main, hostNames )
        pingResult = pingResult and pingTemp

        if pingTemp:
            main.assertReturnString += 'Link Up Ping6all Passed\n'
        else:
            main.assertReturnString += 'Link Up Ping6all Failed\n'

        intentTemp = checkIntentState( main, intentsId )
        intentResult = intentResult and intentTemp
        if intentTemp:
            main.assertReturnString += 'Link Up Intent State Passed\n'
        else:
            main.assertReturnString += 'Link Up Intent State Failed\n'

        # Checks ONOS state in link up
        if linkUpResult and topoResult and pingResult and intentResult:
            main.log.info( itemName + ": Successfully brought link back up" )
        else:
            main.log.error( itemName + ": Failed to bring link back up" )

    # Remove all intents
    removeIntentResult = removeAllIntents( main, intentsId )

    if removeIntentResult:
        main.assertReturnString += 'Remove Intents Passed'
    else:
        main.assertReturnString += 'Remove Intents Failed'

    stepResult = pingResult and linkDownResult and linkUpResult \
                 and intentResult and removeIntentResult

    return stepResult

def pointIntent( main,
                 name,
                 host1,
                 host2,
                 onosNode=0,
                 deviceId1="",
                 deviceId2="",
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
    Description:
        Verify add-point-intent
    Steps:
        - Get device ids | ports
        - Add point intents
        - Check intents
        - Verify flows
        - Ping hosts
        - Reroute
            - Link down
            - Verify flows
            - Check topology
            - Ping hosts
            - Link up
            - Verify flows
            - Check topology
            - Ping hosts
        - Remove intents
    Required:
        name - Type of point intent to add eg. IPV4 | VLAN | Dualstack
        host1 - Name of first host
        host2 - Name of second host
    Optional:
        onosNode - ONOS node to install the intents in main.CLIs[ ]
                   0 by default so that it will always use the first
                   ONOS node
        deviceId1 - ONOS device id of the first switch, the same as the
                    location of the first host eg. of:0000000000000001/1,
                    located at device 1 port 1
        deviceId2 - ONOS device id of the second switch
        port1 - The port number where the first host is attached
        port2 - The port number where the second host is attached
        ethType - Ethernet type eg. IPV4, IPV6
        mac1 - Mac address of first host
        mac2 - Mac address of the second host
        bandwidth - Bandwidth capacity
        lambdaAlloc - Allocate lambda, defaults to False
        ipProto - IP protocol
        ip1 - IP address of first host
        ip2 - IP address of second host
        tcp1 - TCP port of first host
        tcp2 - TCP port of second host
        sw1 - First switch to bring down & up for rerouting purpose
        sw2 - Second switch to bring down & up for rerouting purpose
        expectedLink - Expected link when the switches are down, it should
                       be two links lower than the links before the two
                       switches are down
    """

    assert main, "There is no main variable"
    assert name, "variable name is empty"
    assert host1 and host2, "You must specify hosts"

    global itemName
    itemName = name
    host1 = host1
    host2 = host2
    hostNames = [ host1, host2 ]
    intentsId = []

    pingResult = main.TRUE
    intentResult = main.TRUE
    removeIntentResult = main.TRUE
    flowResult = main.TRUE
    topoResult = main.TRUE
    linkDownResult = main.TRUE
    linkUpResult = main.TRUE
    onosNode = int( onosNode )

    # Adding bidirectional point  intents
    main.log.info( itemName + ": Adding point intents" )
    intent1 = main.CLIs[ onosNode ].addPointIntent( ingressDevice=deviceId1,
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
    intent2 = main.CLIs[ onosNode ].addPointIntent( ingressDevice=deviceId2,
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
    time.sleep( main.checkIntentSleep )
    intentResult = checkIntentState( main, intentsId )
    # Check flows count in each node
    checkFlowsCount( main )

    # Check intents state again if first check fails...
    if not intentResult:
        intentResult = checkIntentState( main, intentsId )
        if intentResult:
            main.assertReturnString += 'Initial Intent State Passed\n'
        else:
            main.assertReturnString += 'Initial Intent State Failed\n'

    # Check flows count in each node
    FlowResult = checkFlowsCount( main )
    if FlowResult:
        main.assertReturnString += 'Initial Flow Count Passed\n'
    else:
        main.assertReturnString += 'Initial Flow Count Failed\n'
    # Verify flows
    StateResult = checkFlowsState( main )
    if StateResult:
        main.assertReturnString += 'Initial Flow State Passed\n'
    else:
        main.assertReturnString += 'Initial Flow State Failed\n'

    # Ping hosts
    pingTemp = ping6allHosts( main, hostNames )
    pingResult = pingResult and pingTemp
    if pingTemp:
        main.assertReturnString += 'Initial Ping6all Passed\n'
    else:
        main.assertReturnString += 'Initial Ping6all Failed\n'

    # Test rerouting if these variables exist
    if sw1 and sw2 and expectedLink:
        # link down
        linkDownResult = link( main, sw1, sw2, "down" )

        if linkDownResult:
            main.assertReturnString += 'Link Down Passed\n'
        else:
            main.assertReturnString += 'Link Down Failed\n'

        # Check flows count in each node
        checkFlowsCount( main )
        # Verify flows
        checkFlowsState( main )

        # Check OnosTopology
        topoResult = checkTopology( main, expectedLink )
        if topoResult:
            main.assertReturnString += 'Link Down Topology State Passed\n'
        else:
            main.assertReturnString += 'Link Down Topology State Failed\n'

        # Ping hosts
        pingTemp = ping6allHosts( main, hostNames )
        pingResult = pingResult and pingTemp
        if pingTemp:
            main.assertReturnString += 'Link Down Ping6all Passed\n'
        else:
            main.assertReturnString += 'Link Down Ping6all Failed\n'

        # Check intent state
        intentTemp = checkIntentState( main, intentsId )
        intentResult = intentResult and intentTemp
        if intentTemp:
            main.assertReturnString += 'Link Down Intent State Passed\n'
        else:
            main.assertReturnString += 'Link Down Intent State Failed\n'

        # Checks ONOS state in link down
        if linkDownResult and topoResult and pingResult and intentResult:
            main.log.info( itemName + ": Successfully brought link down" )
        else:
            main.log.error( itemName + ": Failed to bring link down" )

        # link up
        linkUpResult = link( main, sw1, sw2, "up" )
        if linkUpResult:
            main.assertReturnString += 'Link Up Passed\n'
        else:
            main.assertReturnString += 'Link Up Failed\n'

        time.sleep( main.rerouteSleep )

        # Check flows count in each node
        checkFlowsCount( main )
        # Verify flows
        checkFlowsState( main )

        # Check OnosTopology
        topoResult = checkTopology( main, main.numLinks )
        if topoResult:
            main.assertReturnString += 'Link Up Topology State Passed\n'
        else:
            main.assertReturnString += 'Link Up Topology State Failed\n'

        # Ping hosts
        pingTemp = ping6allHosts( main, hostNames )
        pingResult = pingResult and pingTemp
        if pingTemp:
            main.assertReturnString += 'Link Up Ping6all Passed\n'
        else:
            main.assertReturnString += 'Link Up Ping6all Failed\n'

        intentTemp = checkIntentState( main, intentsId )
        intentResult = intentResult and intentTemp
        if intentTemp:
            main.assertReturnString += 'Link Up Intent State Passed\n'
        else:
            main.assertReturnString += 'Link Up Intent State Failed\n'

        # Checks ONOS state in link up
        if linkUpResult and topoResult and pingResult and intentResult:
            main.log.info( itemName + ": Successfully brought link back up" )
        else:
            main.log.error( itemName + ": Failed to bring link back up" )

    # Remove all intents
    removeIntentResult = removeAllIntents( main, intentsId )
    if removeIntentResult:
        main.assertReturnString += 'Remove Intents Passed'
    else:
        main.assertReturnString += 'Remove Intents Failed'

    stepResult = pingResult and linkDownResult and linkUpResult \
                 and intentResult and removeIntentResult

    return stepResult

def pointIntentTcp( main,
                    name,
                    host1,
                    host2,
                    onosNode=0,
                    deviceId1="",
                    deviceId2="",
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
    Description:
        Verify add-point-intent only for TCP
    Steps:
        - Get device ids | ports
        - Add point intents
        - Check intents
        - Verify flows
        - Ping hosts
        - Reroute
            - Link down
            - Verify flows
            - Check topology
            - Ping hosts
            - Link up
            - Verify flows
            - Check topology
            - Ping hosts
        - Remove intents
    Required:
        name - Type of point intent to add eg. IPV4 | VLAN | Dualstack
        host1 - Name of first host
        host2 - Name of second host
    Optional:
        onosNode - ONOS node to install the intents in main.CLIs[ ]
                   0 by default so that it will always use the first
                   ONOS node
        deviceId1 - ONOS device id of the first switch, the same as the
                    location of the first host eg. of:0000000000000001/1,
                    located at device 1 port 1
        deviceId2 - ONOS device id of the second switch
        port1 - The port number where the first host is attached
        port2 - The port number where the second host is attached
        ethType - Ethernet type eg. IPV4, IPV6
        mac1 - Mac address of first host
        mac2 - Mac address of the second host
        bandwidth - Bandwidth capacity
        lambdaAlloc - Allocate lambda, defaults to False
        ipProto - IP protocol
        ip1 - IP address of first host
        ip2 - IP address of second host
        tcp1 - TCP port of first host
        tcp2 - TCP port of second host
        sw1 - First switch to bring down & up for rerouting purpose
        sw2 - Second switch to bring down & up for rerouting purpose
        expectedLink - Expected link when the switches are down, it should
                       be two links lower than the links before the two
                       switches are down
    """

    assert main, "There is no main variable"
    assert name, "variable name is empty"
    assert host1 and host2, "You must specify hosts"

    global itemName
    itemName = name
    host1 = host1
    host2 = host2
    hostNames = [ host1, host2 ]
    intentsId = []

    iperfResult = main.TRUE
    intentResult = main.TRUE
    removeIntentResult = main.TRUE
    flowResult = main.TRUE
    topoResult = main.TRUE
    linkDownResult = main.TRUE
    linkUpResult = main.TRUE
    onosNode = int( onosNode )

    # Adding bidirectional point  intents
    main.log.info( itemName + ": Adding point intents" )
    intent1 = main.CLIs[ onosNode ].addPointIntent( ingressDevice=deviceId1,
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
                                                    tcpDst="" )

    intent2 = main.CLIs[ onosNode ].addPointIntent( ingressDevice=deviceId2,
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
                                                    tcpDst="" )

    intent3 = main.CLIs[ onosNode ].addPointIntent( ingressDevice=deviceId1,
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
                                                    tcpSrc="",
                                                    tcpDst=tcp2 )

    intent4 = main.CLIs[ onosNode ].addPointIntent( ingressDevice=deviceId2,
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
                                                    tcpSrc="",
                                                    tcpDst=tcp1 )
    intentsId.append( intent1 )
    intentsId.append( intent2 )
    intentsId.append( intent3 )
    intentsId.append( intent4 )

    # Check intents state
    time.sleep( main.checkIntentSleep )
    intentResult = checkIntentState( main, intentsId )
    # Check flows count in each node
    checkFlowsCount( main )

    # Check intents state again if first check fails...
    if not intentResult:
        intentResult = checkIntentState( main, intentsId )
        if intentResult:
            main.assertReturnString += 'Initial Intent State Passed\n'
        else:
            main.assertReturnString += 'Initial Intent State Failed\n'

    # Check flows count in each node
    FlowResult = checkFlowsCount( main )
    if FlowResult:
        main.assertReturnString += 'Initial Flow Count Passed\n'
    else:
        main.assertReturnString += 'Initial Flow Count Failed\n'
    # Verify flows
    StateResult = checkFlowsState( main )
    if StateResult:
        main.assertReturnString += 'Initial Flow State Passed\n'
    else:
        main.assertReturnString += 'Initial Flow State Failed\n'

        # Run iperf to both host
    iperfTemp = main.Mininet1.iperftcpipv6( host1,host2 )
    iperfResult = iperfResult and iperfTemp
    if iperfTemp:
        main.assertReturnString += 'Initial Iperf6 Passed\n'
    else:
        main.assertReturnString += 'Initial Iperf6 Failed\n'

    # Test rerouting if these variables exist
    if sw1 and sw2 and expectedLink:
        # link down
        linkDownResult = link( main, sw1, sw2, "down" )

        if linkDownResult:
            main.assertReturnString += 'Link Down Passed\n'
        else:
            main.assertReturnString += 'Link Down Failed\n'

        # Check flows count in each node
        checkFlowsCount( main )
        # Verify flows
        checkFlowsState( main )

        # Check OnosTopology
        topoResult = checkTopology( main, expectedLink )
        if topoResult:
            main.assertReturnString += 'Link Down Topology State Passed\n'
        else:
            main.assertReturnString += 'Link Down Topology State Failed\n'

        # Run iperf to both host
        iperfTemp = main.Mininet1.iperftcpipv6( host1,host2 )
        iperfResult = iperfResult and iperfTemp
        if iperfTemp:
            main.assertReturnString += 'Link Down Iperf6 Passed\n'
        else:
            main.assertReturnString += 'Link Down Iperf6 Failed\n'

        # Check intent state
        intentTemp = checkIntentState( main, intentsId )
        intentResult = intentResult and intentTemp
        if intentTemp:
            main.assertReturnString += 'Link Down Intent State Passed\n'
        else:
            main.assertReturnString += 'Link Down Intent State Failed\n'

        # Checks ONOS state in link down
        if linkDownResult and topoResult and iperfResult and intentResult:
            main.log.info( itemName + ": Successfully brought link down" )
        else:
            main.log.error( itemName + ": Failed to bring link down" )

        # link up
        linkUpResult = link( main, sw1, sw2, "up" )
        if linkUpResult:
            main.assertReturnString += 'Link Up Passed\n'
        else:
            main.assertReturnString += 'Link Up Failed\n'

        time.sleep( main.rerouteSleep )

        # Check flows count in each node
        checkFlowsCount( main )
        # Verify flows
        checkFlowsState( main )

        # Check OnosTopology
        topoResult = checkTopology( main, main.numLinks )

        if topoResult:
            main.assertReturnString += 'Link Up Topology State Passed\n'
        else:
            main.assertReturnString += 'Link Up Topology State Failed\n'

        # Run iperf to both host
        iperfTemp = main.Mininet1.iperftcpipv6( host1,host2,timeout=10 )
        iperfResult = iperfResult and iperfTemp
        if iperfTemp:
            main.assertReturnString += 'Link Up Iperf6 Passed\n'
        else:
            main.assertReturnString += 'Link Up Iperf6 Failed\n'

        # Check intent state
        intentTemp = checkIntentState( main, intentsId )
        intentResult = intentResult and intentTemp
        if intentTemp:
            main.assertReturnString += 'Link Down Intent State Passed\n'
        else:
            main.assertReturnString += 'Link Down Intent State Failed\n'

        # Checks ONOS state in link up
        if linkUpResult and topoResult and iperfResult and intentResult:
            main.log.info( itemName + ": Successfully brought link back up" )
        else:
            main.log.error( itemName + ": Failed to bring link back up" )

    # Remove all intents
    removeIntentResult = removeAllIntents( main, intentsId )
    if removeIntentResult:
        main.assertReturnString += 'Remove Intents Passed'
    else:
        main.assertReturnString += 'Remove Intents Failed'

    stepResult = iperfResult and linkDownResult and linkUpResult \
                 and intentResult and removeIntentResult

    return stepResult

def singleToMultiIntent( main,
                         name,
                         hostNames="",
                         onosNode=0,
                         devices="",
                         ports="",
                         ethType="",
                         macs="",
                         bandwidth="",
                         lambdaAlloc=False,
                         ipProto="",
                         ipAddresses="",
                         tcp="",
                         sw1="",
                         sw2="",
                         expectedLink=0 ):
    """
    Verify Single to Multi Point intents
    NOTE:If main.hostsData is not defined, variables data should be passed
    in the same order index wise. All devices in the list should have the same
    format, either all the devices have its port or it doesn't.
    eg. hostName = [ 'h1', 'h2' ,..  ]
        devices = [ 'of:0000000000000001', 'of:0000000000000002', ...]
        ports = [ '1', '1', ..]
        ...
    Description:
        Verify add-single-to-multi-intent iterates through the list of given
        host | devices and add intents
    Steps:
        - Get device ids | ports
        - Add single to multi point intents
        - Check intents
        - Verify flows
        - Ping hosts
        - Reroute
            - Link down
            - Verify flows
            - Check topology
            - Ping hosts
            - Link up
            - Verify flows
            - Check topology
            - Ping hosts
        - Remove intents
    Required:
        name - Type of point intent to add eg. IPV4 | VLAN | Dualstack
        hostNames - List of host names
    Optional:
        onosNode - ONOS node to install the intents in main.CLIs[ ]
                   0 by default so that it will always use the first
                   ONOS node
        devices - List of device ids in the same order as the hosts
                  in hostNames
        ports - List of port numbers in the same order as the device in
                devices
        ethType - Ethernet type eg. IPV4, IPV6
        macs - List of hosts mac address in the same order as the hosts in
               hostNames
        bandwidth - Bandwidth capacity
        lambdaAlloc - Allocate lambda, defaults to False
        ipProto - IP protocol
        ipAddresses - IP addresses of host in the same order as the hosts in
                      hostNames
        tcp - TCP ports in the same order as the hosts in hostNames
        sw1 - First switch to bring down & up for rerouting purpose
        sw2 - Second switch to bring down & up for rerouting purpose
        expectedLink - Expected link when the switches are down, it should
                       be two links lower than the links before the two
                       switches are down
    """

    assert main, "There is no main variable"
    assert hostNames, "You must specify hosts"
    assert devices or main.hostsData, "You must specify devices"

    global itemName
    itemName = name
    tempHostsData = {}
    intentsId = []
    onosNode = int( onosNode )

    macsDict = {}
    ipDict = {}
    if hostNames and devices:
        if len( hostNames ) != len( devices ):
            main.log.debug( "hosts and devices does not have the same length" )
            return main.FALSE
        if ports:
            if len( ports ) != len( devices ):
                main.log.error( "Ports and devices does " +
                                "not have the same length" )
                return main.FALSE
        else:
            main.log.info( "Device Ports are not specified" )
        if macs:
            for i in range( len( devices ) ):
                macsDict[ devices[ i ] ] = macs[ i ]

    elif hostNames and not devices and main.hostsData:
        devices = []
        main.log.info( "singleToMultiIntent function is using main.hostsData" )
        for host in hostNames:
               devices.append( main.hostsData.get( host ).get( 'location' ) )
               macsDict[ main.hostsData.get( host ).get( 'location' ) ] = \
                           main.hostsData.get( host ).get( 'mac' )
               ipDict[ main.hostsData.get( host ).get( 'location' ) ] = \
                           main.hostsData.get( host ).get( 'ipAddresses' )

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

    # Check flows count in each node
    checkFlowsCount( main )

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
        if not macsDict:
            srcMac = ""
        else:
            srcMac = macsDict[ ingressDevice ]
            if srcMac == None:
                main.log.debug( "There is no MAC in device - " + ingressDevice )
                srcMac = ""

        intentsId.append(
                        main.CLIs[ onosNode ].addSinglepointToMultipointIntent(
                                            ingressDevice=ingressDevice,
                                            egressDeviceList=egressDeviceList,
                                            portIngress=portIngress,
                                            portEgressList=portEgressList,
                                            ethType=ethType,
                                            ethSrc=srcMac,
                                            bandwidth=bandwidth,
                                            lambdaAlloc=lambdaAlloc,
                                            ipProto=ipProto,
                                            ipSrc="",
                                            ipDst="",
                                            tcpSrc="",
                                            tcpDst="" ) )


    # Check intents state
    time.sleep( main.checkIntentSleep )
    intentResult = checkIntentState( main, intentsId )

    # Check intents state again if first check fails...
    if not intentResult:
        intentResult = checkIntentState( main, intentsId )
        if intentResult:
            main.assertReturnString += 'Initial Intent State Passed\n'
        else:
            main.assertReturnString += 'Initial Intent State Failed\n'

    # Check flows count in each node
    FlowResult = checkFlowsCount( main )
    if FlowResult:
        main.assertReturnString += 'Initial Flow Count Passed\n'
    else:
        main.assertReturnString += 'Initial Flow Count Failed\n'
    # Verify flows
    StateResult = checkFlowsState( main )
    if StateResult:
        main.assertReturnString += 'Initial Flow State Passed\n'
    else:
        main.assertReturnString += 'Initial Flow State Failed\n'

    firstPingResult = main.Mininet1.ping6pair(SRC=hostNames[0], TARGET=main.hostsData[ hostNames[1] ][ 'ipAddresses' ][0])
    if not firstPingResult:
        main.log.debug( "First ping failed, there must be" +
                       " something wrong with ONOS performance" )

    # Ping hosts again...
    pingTemp = ping6allHosts( main, hostNames )
    pingResult = pingResult and pingTemp
    if pingTemp:
        main.assertReturnString += 'Initial Ping6all Passed\n'
    else:
        main.assertReturnString += 'Initial Ping6all Failed\n'

    # Test rerouting if these variables exist
    if sw1 and sw2 and expectedLink:
        # link down
        linkDownResult = link( main, sw1, sw2, "down" )

        if linkDownResult:
            main.assertReturnString += 'Link Down Passed\n'
        else:
            main.assertReturnString += 'Link Down Failed\n'

        # Check flows count in each node
        checkFlowsCount( main )
        # Verify flows
        checkFlowsState( main )

        # Check OnosTopology
        topoResult = checkTopology( main, expectedLink )
        if topoResult:
            main.assertReturnString += 'Link Down Topology State Passed\n'
        else:
            main.assertReturnString += 'Link Down Topology State Failed\n'

        # Ping hosts
        pingTemp = ping6allHosts( main, hostNames )
        pingResult = pingResult and pingTemp
        if pingTemp:
            main.assertReturnString += 'Link Down Ping6all Passed\n'
        else:
            main.assertReturnString += 'Link Down Ping6all Failed\n'

        # Check intent state
        intentTemp = checkIntentState( main, intentsId )
        intentResult = intentResult and intentTemp
        if intentTemp:
            main.assertReturnString += 'Link Down Intent State Passed\n'
        else:
            main.assertReturnString += 'Link Down Intent State Failed\n'

        # Checks ONOS state in link down
        if linkDownResult and topoResult and pingResult and intentResult:
            main.log.info( itemName + ": Successfully brought link down" )
        else:
            main.log.error( itemName + ": Failed to bring link down" )

        # link up
        linkUpResult = link( main, sw1, sw2, "up" )
        if linkUpResult:
            main.assertReturnString += 'Link Up Passed\n'
        else:
            main.assertReturnString += 'Link Up Failed\n'

        time.sleep( main.rerouteSleep )

        # Check flows count in each node
        checkFlowsCount( main )
        # Verify flows
        checkFlowsState( main )

        # Check OnosTopology
        topoResult = checkTopology( main, main.numLinks )
        if topoResult:
            main.assertReturnString += 'Link Up Topology State Passed\n'
        else:
            main.assertReturnString += 'Link Up Topology State Failed\n'

        # Ping hosts
        pingTemp = ping6allHosts( main, hostNames )
        pingResult = pingResult and pingTemp
        if pingTemp:
            main.assertReturnString += 'Link Up Ping6all Passed\n'
        else:
            main.assertReturnString += 'Link Up Ping6all Failed\n'

        # Check Intents
        intentTemp = checkIntentState( main, intentsId )
        intentResult = intentResult and intentTemp
        if intentTemp:
            main.assertReturnString += 'Link Up Intent State Passed\n'
        else:
            main.assertReturnString += 'Link Up Intent State Failed\n'

        # Checks ONOS state in link up
        if linkUpResult and topoResult and pingResult and intentResult:
            main.log.info( itemName + ": Successfully brought link back up" )
        else:
            main.log.error( itemName + ": Failed to bring link back up" )

    # Remove all intents
    removeIntentResult = removeAllIntents( main, intentsId )
    if removeIntentResult:
        main.assertReturnString += 'Remove Intents Passed'
    else:
        main.assertReturnString += 'Remove Intents Failed'

    stepResult = pingResult and linkDownResult and linkUpResult \
                 and intentResult and removeIntentResult

    return stepResult

def multiToSingleIntent( main,
                         name,
                         hostNames="",
                         onosNode=0,
                         devices="",
                         ports="",
                         ethType="",
                         macs="",
                         bandwidth="",
                         lambdaAlloc=False,
                         ipProto="",
                         ipAddresses="",
                         tcp="",
                         sw1="",
                         sw2="",
                         expectedLink=0 ):
    """
    Verify Single to Multi Point intents
    NOTE:If main.hostsData is not defined, variables data should be passed in the
    same order index wise. All devices in the list should have the same
    format, either all the devices have its port or it doesn't.
    eg. hostName = [ 'h1', 'h2' ,..  ]
        devices = [ 'of:0000000000000001', 'of:0000000000000002', ...]
        ports = [ '1', '1', ..]
        ...
    Description:
        Verify add-multi-to-single-intent
    Steps:
        - Get device ids | ports
        - Add multi to single point intents
        - Check intents
        - Verify flows
        - Ping hosts
        - Reroute
            - Link down
            - Verify flows
            - Check topology
            - Ping hosts
            - Link up
            - Verify flows
            - Check topology
            - Ping hosts
        - Remove intents
    Required:
        name - Type of point intent to add eg. IPV4 | VLAN | Dualstack
        hostNames - List of host names
    Optional:
        onosNode - ONOS node to install the intents in main.CLIs[ ]
                   0 by default so that it will always use the first
                   ONOS node
        devices - List of device ids in the same order as the hosts
                  in hostNames
        ports - List of port numbers in the same order as the device in
                devices
        ethType - Ethernet type eg. IPV4, IPV6
        macs - List of hosts mac address in the same order as the hosts in
               hostNames
        bandwidth - Bandwidth capacity
        lambdaAlloc - Allocate lambda, defaults to False
        ipProto - IP protocol
        ipAddresses - IP addresses of host in the same order as the hosts in
                      hostNames
        tcp - TCP ports in the same order as the hosts in hostNames
        sw1 - First switch to bring down & up for rerouting purpose
        sw2 - Second switch to bring down & up for rerouting purpose
        expectedLink - Expected link when the switches are down, it should
                       be two links lower than the links before the two
                       switches are down
        Note - Don't use more than 2 hosts for MultiToSingle Intent with no mac address option.
    """

    assert main, "There is no main variable"
    assert hostNames, "You must specify hosts"
    assert devices or main.hostsData, "You must specify devices"

    global itemName
    itemName = name
    tempHostsData = {}
    intentsId = []
    onosNode = int( onosNode )

    macsDict = {}
    ipDict = {}
    if hostNames and devices:
        if len( hostNames ) != len( devices ):
            main.log.debug( "hosts and devices does not have the same length" )
            return main.FALSE
        if ports:
            if len( ports ) != len( devices ):
                main.log.error( "Ports and devices does " +
                                "not have the same length" )
                return main.FALSE
        else:
            main.log.info( "Device Ports are not specified" )
        if macs:
            for i in range( len( devices ) ):
                macsDict[ devices[ i ] ] = macs[ i ]
    elif hostNames and not devices and main.hostsData:
        devices = []
        main.log.info( "multiToSingleIntent function is using main.hostsData" )
        for host in hostNames:
               devices.append( main.hostsData.get( host ).get( 'location' ) )
               macsDict[ main.hostsData.get( host ).get( 'location' ) ] = \
                           main.hostsData.get( host ).get( 'mac' )
               ipDict[ main.hostsData.get( host ).get( 'location' ) ] = \
                           main.hostsData.get( host ).get( 'ipAddresses' )

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
    main.log.info( itemName + ": Adding multi point to single point intents" )

    # Check flows count in each node
    checkFlowsCount( main )

    # Adding bidirectional point  intents
    for i in range( len( devices ) ):
        egressDevice = devicesCopy[ i ]
        ingressDeviceList = copy.copy( devicesCopy )
        ingressDeviceList.remove( egressDevice )
        if ports:
            portEgress = portsCopy[ i ]
            portIngressList = copy.copy( portsCopy )
            del portIngressList[ i ]
        else:
            portEgress = ""
            portIngressList = None
        if not macsDict:
            dstMac = ""
        else:
            dstMac = macsDict[ egressDevice ]
            if dstMac == None:
                main.log.debug( "There is no MAC in device - " + egressDevice )
                dstMac = ""

        intentsId.append(
                        main.CLIs[ onosNode ].addMultipointToSinglepointIntent(
                                            ingressDeviceList=ingressDeviceList,
                                            egressDevice=egressDevice,
                                            portIngressList=portIngressList,
                                            portEgress=portEgress,
                                            ethType=ethType,
                                            ethDst=dstMac,
                                            bandwidth=bandwidth,
                                            lambdaAlloc=lambdaAlloc,
                                            ipProto=ipProto,
                                            ipSrc="",
                                            ipDst="",
                                            tcpSrc="",
                                            tcpDst="" ) )
    # Check intents state
    time.sleep( main.checkIntentSleep )
    intentResult = checkIntentState( main, intentsId )

    # Check intents state again if first check fails...
    if not intentResult:
        intentResult = checkIntentState( main, intentsId )
        if intentResult:
            main.assertReturnString += 'Initial Intent State Passed\n'
        else:
            main.assertReturnString += 'Initial Intent State Failed\n'

    # Check flows count in each node
    FlowResult = checkFlowsCount( main )
    if FlowResult:
        main.assertReturnString += 'Initial Flow Count Passed\n'
    else:
        main.assertReturnString += 'Initial Flow Count Failed\n'
    # Verify flows
    StateResult = checkFlowsState( main )
    if StateResult:
        main.assertReturnString += 'Initial Flow State Passed\n'
    else:
        main.assertReturnString += 'Initial Flow State Failed\n'

    # Ping hosts...
    pingTemp = ping6allHosts( main, hostNames )
    pingResult = pingResult and pingTemp
    if pingTemp:
        main.assertReturnString += 'Initial Ping6all Passed\n'
    else:
        main.assertReturnString += 'Initial Ping6all Failed\n'

    # Test rerouting if these variables exist
    if sw1 and sw2 and expectedLink:
        # link down
        linkDownResult = link( main, sw1, sw2, "down" )

        if linkDownResult:
            main.assertReturnString += 'Link Down Passed\n'
        else:
            main.assertReturnString += 'Link Down Failed\n'

        # Check flows count in each node
        checkFlowsCount( main )
        # Verify flows
        checkFlowsState( main )

        # Check OnosTopology
        topoResult = checkTopology( main, expectedLink )
        if topoResult:
            main.assertReturnString += 'Link Down Topology State Passed\n'
        else:
            main.assertReturnString += 'Link Down Topology State Failed\n'

        # Ping hosts
        pingTemp = ping6allHosts( main, hostNames )
        pingResult = pingResult and pingTemp
        if pingTemp:
            main.assertReturnString += 'Link Down Ping6all Passed\n'
        else:
            main.assertReturnString += 'Link Down Ping6all Failed\n'

        # Check intent state
        intentTemp = checkIntentState( main, intentsId )
        intentResult = intentResult and intentTemp
        if intentTemp:
            main.assertReturnString += 'Link Down Intent State Passed\n'
        else:
            main.assertReturnString += 'Link Down Intent State Failed\n'

        # Checks ONOS state in link down
        if linkDownResult and topoResult and pingResult and intentResult:
            main.log.info( itemName + ": Successfully brought link down" )
        else:
            main.log.error( itemName + ": Failed to bring link down" )

        # link up
        linkUpResult = link( main, sw1, sw2, "up" )
        if linkUpResult:
            main.assertReturnString += 'Link Up Passed\n'
        else:
            main.assertReturnString += 'Link Up Failed\n'

        time.sleep( main.rerouteSleep )

        # Check flows count in each node
        checkFlowsCount( main )
        # Verify flows
        checkFlowsState( main )

        # Check OnosTopology
        topoResult = checkTopology( main, main.numLinks )
        if topoResult:
            main.assertReturnString += 'Link Up Topology State Passed\n'
        else:
            main.assertReturnString += 'Link Up Topology State Failed\n'

        # Ping hosts
        pingTemp = ping6allHosts( main, hostNames )
        pingResult = pingResult and pingTemp
        if pingTemp:
            main.assertReturnString += 'Link Up Ping6all Passed\n'
        else:
            main.assertReturnString += 'Link Up Ping6all Failed\n'

        # Check Intents
        intentTemp = checkIntentState( main, intentsId )
        intentResult = intentResult and intentTemp
        if intentTemp:
            main.assertReturnString += 'Link Up Intent State Passed\n'
        else:
            main.assertReturnString += 'Link Up Intent State Failed\n'

        # Checks ONOS state in link up
        if linkUpResult and topoResult and pingResult and intentResult:
            main.log.info( itemName + ": Successfully brought link back up" )
        else:
            main.log.error( itemName + ": Failed to bring link back up" )

    # Remove all intents
    removeIntentResult = removeAllIntents( main, intentsId )
    if removeIntentResult:
        main.assertReturnString += 'Remove Intents Passed'
    else:
        main.assertReturnString += 'Remove Intents Failed'

    stepResult = pingResult and linkDownResult and linkUpResult \
                 and intentResult and removeIntentResult

    return stepResult

def testEndPointFail( main,
                      name,
                      test="",
                      hostNames="",
                      devices="",
                      macs="",
                      ports="",
                      onosNode=0,
                      ethType="",
                      bandwidth="",
                      lambdaAlloc=False,
                      ipProto="",
                      ipAddresses="",
                      tcp="",
                      sw1="",
                      sw2="",
                      sw3="",
                      sw4="",
                      sw5="",
                      expectedLink1=0,
                      expectedLink2=0 ):
    """
    Test Multipoint Topology for Endpoint failures
    """

    assert main, "There is no main variable"
    assert hostNames, "You must specify hosts"
    assert devices or main.hostsData, "You must specify devices"

    global itemName
    itemName = name
    tempHostsData = {}
    intentsId = []
    onosNode = int( onosNode )

    macsDict = {}
    ipDict = {}
    if hostNames and devices:
        if len( hostNames ) != len( devices ):
            main.log.debug( "hosts and devices does not have the same length" )
            return main.FALSE
        if ports:
            if len( ports ) != len( devices ):
                main.log.error( "Ports and devices does " +
                                "not have the same length" )
                return main.FALSE
        else:
            main.log.info( "Device Ports are not specified" )
        if macs:
            for i in range( len( devices ) ):
                macsDict[ devices[ i ] ] = macs[ i ]
    elif hostNames and not devices and main.hostsData:
        devices = []
        main.log.info( "multiIntent function is using main.hostsData" )
        for host in hostNames:
               devices.append( main.hostsData.get( host ).get( 'location' ) )
               macsDict[ main.hostsData.get( host ).get( 'location' ) ] = \
                           main.hostsData.get( host ).get( 'mac' )
               ipDict[ main.hostsData.get( host ).get( 'location' ) ] = \
                           main.hostsData.get( host ).get( 'ipAddresses' )

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
    main.log.info( itemName + ": Adding intents" )

    # Check flows count in each node
    checkFlowsCount( main )

    if test=="MultipletoSingle":
        for i in range( len( devices ) ):
            egressDevice = devicesCopy[ i ]
            ingressDeviceList = copy.copy( devicesCopy )
            ingressDeviceList.remove( egressDevice )
            if ports:
                portEgress = portsCopy[ i ]
                portIngressList = copy.copy( portsCopy )
                del portIngressList[ i ]
            else:
                portEgress = ""
                portIngressList = None
            if not macsDict:
                dstMac = ""
            else:
                dstMac = macsDict[ egressDevice ]
                if dstMac == None:
                    main.log.debug( "There is no MAC in device - " + egressDevice )
                    dstMac = ""

            intentsId.append(
                            main.CLIs[ onosNode ].addMultipointToSinglepointIntent(
                                                ingressDeviceList=ingressDeviceList,
                                                egressDevice=egressDevice,
                                                portIngressList=portIngressList,
                                                portEgress=portEgress,
                                                ethType=ethType,
                                                ethDst=dstMac,
                                                bandwidth=bandwidth,
                                                lambdaAlloc=lambdaAlloc,
                                                ipProto=ipProto,
                                                ipSrc="",
                                                ipDst="",
                                                tcpSrc="",
                                                tcpDst="" ) )


    elif test=="SingletoMultiple":
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
            if not macsDict:
                srcMac = ""
            else:
                srcMac = macsDict[ ingressDevice ]
                if srcMac == None:
                    main.log.debug( "There is no MAC in device - " + ingressDevice )
                    srcMac = ""

            intentsId.append(
                            main.CLIs[ onosNode ].addSinglepointToMultipointIntent(
                                                ingressDevice=ingressDevice,
                                                egressDeviceList=egressDeviceList,
                                                portIngress=portIngress,
                                                portEgressList=portEgressList,
                                                ethType=ethType,
                                                ethSrc=srcMac,
                                                bandwidth=bandwidth,
                                                lambdaAlloc=lambdaAlloc,
                                                ipProto=ipProto,
                                                ipSrc="",
                                                ipDst="",
                                                tcpSrc="",
                                                tcpDst="" ) )

    else:
        main.log.info("Invalid test Name - Type either SingletoMultiple or MultipletoSingle")
        return main.FALSE

    # Check intents state
    time.sleep( main.checkIntentSleep )
    intentResult = checkIntentState( main, intentsId )

    # Check intents state again if first check fails...
    if not intentResult:
        intentResult = checkIntentState( main, intentsId )
        if intentResult:
            main.assertReturnString += 'Initial Intent State Passed\n'
        else:
            main.assertReturnString += 'Initial Intent State Failed\n'

    # Check flows count in each node
    FlowResult = checkFlowsCount( main )
    if FlowResult:
        main.assertReturnString += 'Initial Flow Count Passed\n'
    else:
        main.assertReturnString += 'Initial Flow Count Failed\n'
    # Verify flows
    StateResult = checkFlowsState( main )
    if StateResult:
        main.assertReturnString += 'Initial Flow State Passed\n'
    else:
        main.assertReturnString += 'Initial Flow State Failed\n'

    # Ping hosts...
    pingTemp = ping6allHosts( main, hostNames )
    pingResult = pingResult and pingTemp
    if pingTemp:
        main.assertReturnString += 'Initial Pingall Passed\n'
    else:
        main.assertReturnString += 'Initial Pingall Failed\n'

    # Test rerouting if these variables exist
    if sw1 and sw2 and sw3 and sw4 and sw5 and expectedLink1 and expectedLink2:
    # Take two links down
        # Take first link down
        linkDownResult1 = link( main, sw1, sw2, "down" )
        if linkDownResult1:
            main.assertReturnString += 'First Link Down Passed\n'
        else:
            main.assertReturnString += 'First Link Down Failed\n'

        # Take second link down
        linkDownResult2 = link( main, sw3, sw4, "down" )
        if linkDownResult2:
            main.assertReturnString += 'Second Link Down Passed\n'
        else:
            main.assertReturnString += 'Second Link Down Failed\n'

        # Check flows count in each node
        FlowResult = checkFlowsCount( main )
        if FlowResult:
            main.assertReturnString += 'Link Down Flow Count Passed\n'
        else:
            main.assertReturnString += 'Link Down Flow Count Failed\n'
        # Verify flows
        StateResult = checkFlowsState( main )
        if StateResult:
            main.assertReturnString += 'Link Down Flow State Passed\n'
        else:
            main.assertReturnString += 'Link Down Flow State Failed\n'

        # Check OnosTopology
        topoResult = checkTopology( main, expectedLink1 )
        if topoResult:
            main.assertReturnString += 'Link Down Topology State Passed\n'
        else:
            main.assertReturnString += 'Link Down Topology State Failed\n'

        # Ping hosts
        pingTemp = ping6allHosts( main, hostNames )
        pingResult = pingResult and pingTemp
        if pingTemp:
            main.assertReturnString += 'Link Down Ping6all Passed\n'
        else:
            main.assertReturnString += 'Link Down Ping6all Failed\n'

        # Check intent state
        intentTemp = checkIntentState( main, intentsId )
        intentResult = intentResult and intentTemp
        if intentTemp:
            main.assertReturnString += 'Link Down Intent State Passed\n'
        else:
            main.assertReturnString += 'Link Down Intent State Failed\n'

        # Take third link down to isolate the node
        linkDownResult3 = link( main, sw3, sw5, "down" )
        if linkDownResult3:
            main.assertReturnString += 'Isolation Third Link Down Passed\n'
        else:
            main.assertReturnString += 'Isolation Third Link Down Failed\n'

        # Check flows count in each node
        FlowResult = checkFlowsCount( main )
        if FlowResult:
            main.assertReturnString += 'Isolation Link Down Flow Count Passed\n'
        else:
            main.assertReturnString += 'Isolation Link Down Flow Count Failed\n'

        # Verify flows
        StateResult = checkFlowsState( main )
        if StateResult:
            main.assertReturnString += 'Isolation Link Down Flow State Passed\n'
        else:
            main.assertReturnString += 'Isolation Link Down Flow State Failed\n'

        # Check OnosTopology
        topoResult = checkTopology( main, expectedLink2 )
        if topoResult:
            main.assertReturnString += 'Isolation Link Down Topology State Passed\n'
        else:
            main.assertReturnString += 'Isolation Link Down Topology State Failed\n'

        # Ping hosts after isolation
        main.log.info("Ping will fail if the node is isolated correctly.It will ping only after bringing up the isolation link")
        pingIsolation = ping6allHosts( main, hostNames )
        if pingIsolation:
            main.assertReturnString += 'Isolation Link Down Ping6all Passed\n'
        else:
            main.assertReturnString += 'Isolation Link Down Ping6all Failed\n'

        # Check intent state after isolation
        main.log.info("Intent will be in FAILED state if the node is isolated correctly.It will be in INSTALLED state only after bringing up isolation link")
        intentIsolation = checkIntentState( main, intentsId )
        if intentIsolation:
            main.assertReturnString += 'Isolation Link Down Intent State Passed\n'
        else:
            main.assertReturnString += 'Isolation Link Down Intent State Failed\n'

        linkDownResult = linkDownResult1 and linkDownResult2 and linkDownResult3

        # Checks ONOS state in link down
        if linkDownResult and topoResult and pingResult and intentResult:
            main.log.info( itemName + ": Successfully brought link down" )
        else:
            main.log.error( itemName + ": Failed to bring link down" )

        # Bring the links back up
        # Bring first link up
        linkUpResult1 = link( main, sw1, sw2, "up" )
        if linkUpResult1:
            main.assertReturnString += 'First Link Up Passed\n'
        else:
            main.assertReturnString += 'First Link Up Failed\n'

        # Bring second link up
        linkUpResult2 = link( main, sw3, sw4, "up" )
        if linkUpResult2:
            main.assertReturnString += 'Second Link Up Passed\n'
        else:
            main.assertReturnString += 'Second Link Up Failed\n'
        # Bring third link up
        linkUpResult3 = link( main, sw3, sw5, "up" )
        if linkUpResult3:
            main.assertReturnString += 'Third Link Up Passed\n'
        else:
            main.assertReturnString += 'Third Link Up Failed\n'

        linkUpResult = linkUpResult1 and linkUpResult2 and linkUpResult3
        time.sleep( main.rerouteSleep )

        # Check flows count in each node
        FlowResult = checkFlowsCount( main )
        if FlowResult:
            main.assertReturnString += 'Link Up Flow Count Passed\n'
        else:
            main.assertReturnString += 'Link Up Flow Count Failed\n'
        # Verify flows
        StateResult = checkFlowsState( main )
        if StateResult:
            main.assertReturnString += 'Link Up Flow State Passed\n'
        else:
            main.assertReturnString += 'Link Up Flow State Failed\n'

        # Check OnosTopology
        topoResult = checkTopology( main, main.numLinks )
        if topoResult:
            main.assertReturnString += 'Link Up Topology State Passed\n'
        else:
            main.assertReturnString += 'Link Up Topology State Failed\n'

        # Ping hosts
        pingTemp = ping6allHosts( main, hostNames )
        pingResult = pingResult and pingTemp
        if pingTemp:
            main.assertReturnString += 'Link Up Pingall Passed\n'
        else:
            main.assertReturnString += 'Link Up Pingall Failed\n'

        # Check Intents
        intentTemp = checkIntentState( main, intentsId )
        intentResult = intentResult and intentTemp
        if intentTemp:
            main.assertReturnString += 'Link Up Intent State Passed\n'
        else:
            main.assertReturnString += 'Link Up Intent State Failed\n'

        # Checks ONOS state in link up
        if linkUpResult and topoResult and pingResult and intentResult:
            main.log.info( itemName + ": Successfully brought link back up" )
        else:
            main.log.error( itemName + ": Failed to bring link back up" )

    # Remove all intents
    removeIntentResult = removeAllIntents( main, intentsId )
    if removeIntentResult:
        main.assertReturnString += 'Remove Intents Passed'
    else:
        main.assertReturnString += 'Remove Intents Failed'

    testResult = pingResult and linkDownResult and linkUpResult \
                 and intentResult and removeIntentResult

    return testResult

def ping6allHosts( main, hostList ):
    # Ping all host in the hosts list variable
    main.log.info( "Pinging: " + str( hostList ) )
    return main.Mininet1.pingIpv6Hosts( hostList )

def getHostsData( main ):
    """
        Use fwd app and pingall to discover all the hosts
    """

    activateResult = main.TRUE
    appCheck = main.TRUE
    getDataResult = main.TRUE
    main.log.info( "Activating reactive forwarding app " )
    activateResult = main.CLIs[ 0 ].activateApp( "org.onosproject.fwd" )
    main.CLIs[ 0 ].setCfg( "org.onosproject.provider.host.impl.HostLocationProvider", "ipv6NeighborDiscovery", "true")
    main.CLIs[ 0 ].setCfg( "org.onosproject.proxyarp.ProxyArp", "ipv6NeighborDiscovery", "true")
    main.CLIs[ 0 ].setCfg( "org.onosproject.fwd.ReactiveForwarding", "ipv6Forwarding", "true")
    main.CLIs[ 0 ].setCfg( "org.onosproject.fwd.ReactiveForwarding", "matchIpv6Address", "true")
    time.sleep( main.fwdSleep )

    for i in range( main.numCtrls ):
        appCheck = appCheck and main.CLIs[ i ].appToIDCheck()
        if appCheck != main.TRUE:
            main.log.warn( main.CLIs[ i ].apps() )
            main.log.warn( main.CLIs[ i ].appIDs() )

    pingResult = main.Mininet1.pingall( protocol="IPv6", timeout = 600 )
    hostsJson = json.loads( main.CLIs[ 0 ].hosts() )
    hosts = main.Mininet1.getHosts().keys()
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
    if activateResult and deactivateResult and main.hostsData:
        main.log.info( "Successfully used fwd app to discover hosts " )
        getDataResult = main.TRUE
    else:
        main.log.info( "Failed to use fwd app to discover hosts " )
        getDataResult = main.FALSE

    main.log.info( "Removing the automatically configured ipv6 link-local addresses in hostsData to avoid unnecessary ping with these addresses during initial ping test - link-local starts with 'fe' " )
    for host in main.hostsData.keys():
     if main.hostsData[ host ].get( 'ipAddresses' ) != None:
      main.hostsData[ host ][ 'ipAddresses' ] = [ v for v in main.hostsData[ host ][ 'ipAddresses' ] if not v.startswith('fe') ]
    print main.hostsData
    return getDataResult

def checkTopology( main, expectedLink ):
    statusResult = main.TRUE
    # Check onos topology
    main.log.info( itemName + ": Checking ONOS topology " )

    for i in range( main.numCtrls ):
        statusResult = main.CLIs[ i ].checkStatus( main.numSwitch,
                                                   expectedLink )\
                       and statusResult
    if not statusResult:
        main.log.error( itemName + ": Topology mismatch" )
    else:
        main.log.info( itemName + ": Topology match" )
    return statusResult

def checkIntentState( main, intentsId ):
    """
        This function will check intent state to make sure all the intents
        are in INSTALLED state
    """

    intentResult = main.TRUE
    results = []

    main.log.info( itemName + ": Checking intents state" )
    # First check of intents
    for i in range( main.numCtrls ):
        tempResult = main.CLIs[ i ].checkIntentState( intentsId=intentsId )
        results.append( tempResult )

    expectedState = [ 'INSTALLED', 'INSTALLING' ]

    if all( result == main.TRUE for result in results ):
        main.log.info( itemName + ": Intents are installed correctly" )
    else:
        # Wait for at least 5 second before checking the intents again
        main.log.error( "Intents are not installed correctly. Waiting 5 sec" )
        time.sleep( 5 )
        results = []
        # Second check of intents since some of the intents may be in
        # INSTALLING state, they should be in INSTALLED at this time
        for i in range( main.numCtrls ):
            tempResult = main.CLIs[ i ].checkIntentState(
                                                        intentsId=intentsId )
            results.append( tempResult )
        if all( result == main.TRUE for result in results ):
            main.log.info( itemName + ": Intents are installed correctly" )
            intentResult = main.TRUE
        else:
            main.log.error( itemName + ": Intents are NOT installed correctly" )
            intentResult = main.FALSE

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

    onosSummary = []
    removeIntentResult = main.TRUE
    # Remove intents
    for intent in intentsId:
        main.CLIs[ 0 ].removeIntent( intentId=intent, purge=True )

    time.sleep( main.removeIntentSleep )

    # If there is remianing intents then remove intents should fail
    for i in range( main.numCtrls ):
        onosSummary.append( json.loads( main.CLIs[ i ].summary() ) )

    for summary in onosSummary:
        if summary.get( 'intents' ) != 0:
            main.log.warn( itemName + ": There are " +
                           str( summary.get( 'intents' ) ) +
                           " intents remaining in node " +
                           str( summary.get( 'node' ) ) +
                           ", failed to remove all the intents " )
            removeIntentResult = main.FALSE

    if removeIntentResult:
        main.log.info( itemName + ": There are no more intents remaining, " +
                       "successfully removed all the intents." )

    return removeIntentResult

def checkFlowsCount( main ):
    """
        Check flows count in each node
    """

    flowsCount = []
    main.log.info( itemName + ": Checking flows count in each ONOS node" )
    for i in range( main.numCtrls ):
        summaryResult = main.CLIs[ i ].summary()
        if not summaryResult:
            main.log.error( itemName + ": There is something wrong with " +
                            "summary command" )
            return main.FALSE
        else:
            summaryJson = json.loads( summaryResult )
            flowsCount.append( summaryJson.get( 'flows' ) )

    if flowsCount:
        if all( flows==flowsCount[ 0 ] for flows in flowsCount ):
            main.log.info( itemName + ": There are " + str( flowsCount[ 0 ] ) +
                           " flows in all ONOS node" )
        else:
            for i in range( main.numCtrls ):
                main.log.debug( itemName + ": ONOS node " + str( i ) + " has " +
                                str( flowsCount[ i ] ) + " flows" )
    else:
        main.log.error( "Checking flows count failed, check summary command" )
        return main.FALSE

    return main.TRUE

def checkLeaderChange( leaders1, leaders2 ):
    """
        Checks for a change in intent partition leadership.

        Takes the output of leaders -c in json string format before and after
        a potential change as input

        Returns main.TRUE if no mismatches are detected
        Returns main.FALSE if there is a mismatch or on error loading the input
    """
    try:
        leaders1 = json.loads( leaders1 )
        leaders2 = json.loads( leaders2 )
    except ( AttributeError, TypeError):
        main.log.exception( self.name + ": Object not as expected" )
        return main.FALSE
    except Exception:
        main.log.exception( self.name + ": Uncaught exception!" )
        main.cleanup()
        main.exit()
    main.log.info( "Checking Intent Paritions for Change in Leadership" )
    mismatch = False
    for dict1 in leaders1:
        if "intent" in dict1.get( "topic", [] ):
            for dict2 in leaders2:
                if dict1.get( "topic", 0 ) == dict2.get( "topic", 0 ) and \
                    dict1.get( "leader", 0 ) != dict2.get( "leader", 0 ):
                    mismatch = True
                    main.log.error( "{0} changed leader from {1} to {2}".\
                        format( dict1.get( "topic", "no-topic" ),\
                            dict1.get( "leader", "no-leader" ),\
                            dict2.get( "leader", "no-leader" ) ) )
    if mismatch:
        return main.FALSE
    else:
        return main.TRUE

def report( main ):
    """
    Report errors/warnings/exceptions
    """

    main.ONOSbench.logReport( main.ONOSip[ 0 ],
                              [ "INFO",
                                "FOLLOWER",
                                "WARN",
                                "flow",
                                "ERROR",
                                "Except" ],
                              "s" )

    main.log.info( "ERROR report: \n" )
    for i in range( main.numCtrls ):
        main.ONOSbench.logReport( main.ONOSip[ i ],
                [ "ERROR" ],
                "d" )

    main.log.info( "EXCEPTIONS report: \n" )
    for i in range( main.numCtrls ):
        main.ONOSbench.logReport( main.ONOSip[ i ],
                [ "Except" ],
                "d" )

    main.log.info( "WARNING report: \n" )
    for i in range( main.numCtrls ):
        main.ONOSbench.logReport( main.ONOSip[ i ],
                [ "WARN" ],
                "d" )
