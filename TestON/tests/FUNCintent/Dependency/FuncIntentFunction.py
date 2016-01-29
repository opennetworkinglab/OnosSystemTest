"""
    Wrapper functions for FuncIntent
    This functions include Onosclidriver and Mininetclidriver driver functions
    Author: kelvin@onlab.us
"""
import time
import copy
import json

def __init__( self ):
    self.default = ''

def installHostIntent( main,
                       name,
                       host1,
                       host2,
                       onosNode=0,
                       ethType="",
                       bandwidth="",
                       lambdaAlloc=False,
                       ipProto="",
                       ipAddresses="",
                       tcp="",
                       sw1="",
                       sw2=""):
    """
    Installs a Host Intent

    Description:
        Install a host intent using
        add-host-intent

    Steps:
        - Fetch host data if not given
        - Add host intent
            - Ingress device is the first sender host
            - Egress devices are the recipient devices
            - Ports if defined in senders or recipients
            - MAC address ethSrc loaded from Ingress device
        - Check intent state with retry
    Required:
        name - Type of point intent to add eg. IPV4 | VLAN | Dualstack
        host1 - Dictionary for host1
            { "name":"h8", "id":"of:0000000000000005/8" }
        host2 - Dictionary for host2
            { "name":"h16", "id":"of:0000000000000006/8" }
    Optional:
        onosNode - ONOS node to install the intents in main.CLIs[ ]
                   0 by default so that it will always use the first
                   ONOS node
        ethType - Ethernet type eg. IPV4, IPV6
        bandwidth - Bandwidth capacity
        lambdaAlloc - Allocate lambda, defaults to False
        ipProto - IP protocol
        tcp - TCP ports in the same order as the hosts in hostNames
    """

    assert main, "There is no main variable"
    assert host1, "You must specify host1"
    assert host2, "You must specify host2"

    global itemName  # The name of this run. Used for logs.
    itemName = name
    onosNode = int( onosNode )

    main.log.info( itemName + ": Adding single point to multi point intents" )

    if not host1.get( "id" ):
        main.log.warn( "ID not given for host1 {0}. Loading from main.hostData".format( host1.get( "name" ) ) )
        main.log.debug( main.hostsData.get( host1.get( "name" ) ) )
        host1[ "id" ] = main.hostsData.get( host1.get( "name" ) ).get( "id" )

    if not host2.get( "id" ):
        main.log.warn( "ID not given for host2 {0}. Loading from main.h ostData".format( host2.get( "name" ) ) )
        host2[ "id" ] = main.hostsData.get( host2.get( "name" ) ).get( "id" )

    # Adding point intent
    intentId = main.CLIs[ onosNode ].addHostIntent( hostIdOne=host1.get( "id" ),
                                                    hostIdTwo=host2.get( "id" ) )

    # Check intents state
    if utilities.retry( f=checkIntentState, retValue=main.FALSE,
                        args=( main, [ intentId ] ), sleep=main.checkIntentSleep ):
        return intentId
    else:
        main.log.error( "Host Intent did not install correctly" )
        return main.FALSE

def testHostIntent( main,
                    name,
                    intentId,
                    host1,
                    host2,
                    onosNode=0,
                    sw1="s5",
                    sw2="s2",
                    expectedLink=0):
    """
    Test a Host Intent

    Description:
        Test a host intent of given ID between given hosts

    Steps:
        - Fetch host data if not given
        - Check Intent State
        - Check Flow State
        - Check Connectivity
        - Check Lack of Connectivity Between Hosts not in the Intent
        - Reroute
            - Take Expected Link Down
            - Check Intent State
            - Check Flow State
            - Check Topology
            - Check Connectivity
            - Bring Expected Link Up
            - Check Intent State
            - Check Flow State
            - Check Topology
            - Check Connectivity
        - Remove Topology

    Required:
        name - Type of point intent to add eg. IPV4 | VLAN | Dualstack
        intentId - intent ID to be tested ( and removed )
        host1 - Dictionary for host1
            { "name":"h8", "id":"of:0000000000000005/8" }
        host2 - Dictionary for host2
            { "name":"h16", "id":"of:0000000000000006/8" }
    Optional:
        onosNode - ONOS node to install the intents in main.CLIs[ ]
                   0 by default so that it will always use the first
                   ONOS node
        sw1 - First switch to bring down & up for rerouting purpose
        sw2 - Second switch to bring down & up for rerouting purpose
        expectedLink - Expected link when the switches are down, it should
                       be two links lower than the links before the two
                       switches are down

    """

    # Parameter Validity Check
    assert main, "There is no main variable"
    assert host1, "You must specify host1"
    assert host2, "You must specify host2"

    global itemName
    itemName = name
    tempHostsData = {}
    onosNode = int( onosNode )

    main.log.info( itemName + ": Testing Host Intent" )

    if not host1.get( "id" ):
        main.log.warn( "Id not given for host1 {0}. Loading from main.hostData".format( host1.get( "name" ) ) )
        host1[ "id" ] = main.hostsData.get( host1.get( "name" ) ).get( "location" )

    if not host2.get( "id" ):
        main.log.warn( "Id not given for host2 {0}. Loading from main.hostData".format( host2.get( "name" ) ) )
        host2[ "id" ] = main.hostsData.get( host2.get( "name" ) ).get( "location" )

    senderNames = [ host1.get( "name" ), host2.get( "name" ) ]
    recipientNames = [ host1.get( "name" ), host2.get( "name" ) ]

    testResult = main.TRUE
    main.log.info( itemName + ": Adding single point to multi point intents" )

    # Check intent state
    if utilities.retry( f=checkIntentState, retValue=main.FALSE, args=( main, [ intentId ] ), sleep=main.checkIntentSleep ):
        main.assertReturnString += 'Initial Intent State Passed\n'
    else:
        main.assertReturnString += 'Initial Intent State Failed\n'
        testResult = main.FALSE

    # Check flows count in each node
    if utilities.retry( f=checkFlowsCount, retValue=main.FALSE, args=[ main ] ) and utilities.retry( f=checkFlowsState, retValue=main.FALSE, args=[ main ] ):
        main.assertReturnString += 'Initial Flow State Passed\n'
    else:
        main.assertReturnString += 'Intial Flow State Failed\n'
        testResult = main.FALSE

    # Check Connectivity
    if utilities.retry( f=scapyCheckConnection, retValue=main.FALSE, args=( main, senderNames, recipientNames ) ):
        main.assertReturnString += 'Initial Ping Passed\n'
    else:
        main.assertReturnString += 'Initial Ping Failed\n'
        testResult = main.FALSE

    # Test rerouting if these variables exist
    if sw1 and sw2 and expectedLink:
        # Take link down
        if utilities.retry( f=link, retValue=main.FALSE, args=( main, sw1, sw2, "down" ) ):
            main.assertReturnString += 'Link Down Passed\n'
        else:
            main.assertReturnString += 'Link Down Failed\n'
            testResult = main.FALSE

        # Check intent state
        if utilities.retry( f=checkIntentState, retValue=main.FALSE, args=( main, [ intentId ] ), sleep=main.checkIntentSleep ):
            main.assertReturnString += 'Link Down Intent State Passed\n'
        else:
            main.assertReturnString += 'Link Down Intent State Failed\n'
            testResult = main.FALSE

        # Check flows count in each node
        if utilities.retry( f=checkFlowsCount, retValue=main.FALSE, args=[ main ] ) and utilities.retry( f=checkFlowsState, retValue=main.FALSE, args=[ main ] ):
            main.assertReturnString += 'Link Down Flow State Passed\n'
        else:
            main.assertReturnString += 'Link Down Flow State Failed\n'
            testResult = main.FALSE

        # Check OnosTopology
        if utilities.retry( f=checkTopology, retValue=main.FALSE, args=( main, expectedLink ) ):
            main.assertReturnString += 'Link Down Topology State Passed\n'
        else:
            main.assertReturnString += 'Link Down Topology State Failed\n'
            testResult = main.FALSE

        # Check Connection
        if utilities.retry( f=scapyCheckConnection, retValue=main.FALSE, args=( main, senderNames, recipientNames ) ):
            main.assertReturnString += 'Link Down Pingall Passed\n'
        else:
            main.assertReturnString += 'Link Down Pingall Failed\n'
            testResult = main.FALSE

        # Bring link up
        if utilities.retry( f=link, retValue=main.FALSE, args=( main, sw1, sw2, "up" ) ):
            main.assertReturnString += 'Link Up Passed\n'
        else:
            main.assertReturnString += 'Link Up Failed\n'
            testResult = main.FALSE

        # Wait for reroute
        time.sleep( main.rerouteSleep )

        # Check Intents
        if utilities.retry( f=checkIntentState, retValue=main.FALSE, args=( main, [ intentId ] ), sleep=main.checkIntentSleep ):
            main.assertReturnString += 'Link Up Intent State Passed\n'
        else:
            main.assertReturnString += 'Link Up Intent State Failed\n'
            testResult = main.FALSE

        # Check flows count in each node
        if utilities.retry( f=checkFlowsCount, retValue=main.FALSE, args=[ main ] ) and utilities.retry( f=checkFlowsState, retValue=main.FALSE, args=[ main ] ):
            main.assertReturnString += 'Link Up Flow State Passed\n'
        else:
            main.assertReturnString += 'Link Up Flow State Failed\n'
            testResult = main.FALSE

        # Check OnosTopology
        if utilities.retry( f=checkTopology, retValue=main.FALSE, args=( main, main.numLinks ) ):
            main.assertReturnString += 'Link Up Topology State Passed\n'
        else:
            main.assertReturnString += 'Link Up Topology State Failed\n'
            testResult = main.FALSE

        # Check Connection
        if utilities.retry( f=scapyCheckConnection, retValue=main.FALSE, args=( main, senderNames, recipientNames ) ):
            main.assertReturnString += 'Link Up Pingall Passed\n'
        else:
            main.assertReturnString += 'Link Up Pingall Failed\n'
            testResult = main.FALSE

    # Remove all intents
    if utilities.retry( f=removeAllIntents, retValue=main.FALSE, args=( main, [ intentId ] ) ):
        main.assertReturnString += 'Remove Intents Passed'
    else:
        main.assertReturnString += 'Remove Intents Failed'
        testResult = main.FALSE

    return testResult

def installPointIntent( main,
                        name,
                        senders,
                        recipients,
                        onosNode=0,
                        ethType="",
                        bandwidth="",
                        lambdaAlloc=False,
                        ipProto="",
                        ipSrc="",
                        ipDst="",
                        tcpSrc="",
                        tcpDst=""):
    """
    Installs a Single to Single Point Intent

    Description:
        Install a single to single point intent

    Steps:
        - Fetch host data if not given
        - Add point intent
            - Ingress device is the first sender device
            - Egress device is the first recipient device
            - Ports if defined in senders or recipients
            - MAC address ethSrc loaded from Ingress device
        - Check intent state with retry
    Required:
        name - Type of point intent to add eg. IPV4 | VLAN | Dualstack
        senders - List of host dictionaries i.e.
            [ { "name":"h8", "device":"of:0000000000000005/8","mac":"00:00:00:00:00:08" } ]
        recipients - List of host dictionaries i.e.
            [ { "name":"h16", "device":"of:0000000000000006/8", "mac":"00:00:00:00:00:10" } ]
    Optional:
        onosNode - ONOS node to install the intents in main.CLIs[ ]
                   0 by default so that it will always use the first
                   ONOS node
        ethType - Ethernet type eg. IPV4, IPV6
        bandwidth - Bandwidth capacity
        lambdaAlloc - Allocate lambda, defaults to False
        ipProto - IP protocol
        tcp - TCP ports in the same order as the hosts in hostNames
        sw1 - First switch to bring down & up for rerouting purpose
        sw2 - Second switch to bring down & up for rerouting purpose
        expectedLink - Expected link when the switches are down, it should
                       be two links lower than the links before the two
                       switches are down
    """

    assert main, "There is no main variable"
    assert senders, "You must specify a sender"
    assert recipients, "You must specify a recipient"
    # Assert devices or main.hostsData, "You must specify devices"

    global itemName  # The name of this run. Used for logs.
    itemName = name
    onosNode = int( onosNode )

    main.log.info( itemName + ": Adding mutli to single point intents" )

    for sender in senders:
        if not sender.get( "device" ):
            main.log.warn( "Device not given for sender {0}. Loading from main.hostData".format( sender.get( "name" ) ) )
            sender[ "device" ] = main.hostsData.get( sender.get( "name" ) ).get( "location" )

    for recipient in recipients:
        if not recipient.get( "device" ):
            main.log.warn( "Device not given for recipient {0}. Loading from main.hostData".format( recipient.get( "name" ) ) )
            recipient[ "device" ] = main.hostsData.get( recipient.get( "name" ) ).get( "location" )


    ingressDevice = senders[ 0 ].get( "device" )
    egressDevice = recipients[ 0 ].get( "device" )

    portIngress = senders[ 0 ].get( "port", "" )
    portEgress = recipients[ 0 ].get( "port", "" )

    dstMac = recipients[ 0 ].get( "mac" )

    ipSrc = senders[ 0 ].get( "ip" )
    ipDst = recipients[ 0 ].get( "ip" )

    # Adding point intent
    intentId = main.CLIs[ onosNode ].addPointIntent(
                                        ingressDevice=ingressDevice,
                                        egressDevice=egressDevice,
                                        portIngress=portIngress,
                                        portEgress=portEgress,
                                        ethType=ethType,
                                        ethDst=dstMac,
                                        bandwidth=bandwidth,
                                        lambdaAlloc=lambdaAlloc,
                                        ipProto=ipProto,
                                        ipSrc=ipSrc,
                                        ipDst=ipDst,
                                        tcpSrc=tcpSrc,
                                        tcpDst=tcpDst )

    # Check intents state
    if utilities.retry( f=checkIntentState, retValue=main.FALSE, args=( main, [ intentId ] ), sleep=main.checkIntentSleep ):
        return intentId
    else:
        main.log.error( "Point Intent did not install correctly" )
        return main.FALSE

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

    # Check flows count in each node
    checkFlowsCount( main )

    # Verify flows
    checkFlowsState( main )

    # Run iperf to both host
    iperfTemp = main.Mininet1.iperftcp( host1,host2,10 )
    iperfResult = iperfResult and iperfTemp
    if iperfTemp:
        main.assertReturnString += 'Initial Iperf Passed\n'
    else:
        main.assertReturnString += 'Initial Iperf Failed\n'

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
        iperfTemp = main.Mininet1.iperftcp( host1,host2,10 )
        iperfResult = iperfResult and iperfTemp
        if iperfTemp:
            main.assertReturnString += 'Link Down Iperf Passed\n'
        else:
            main.assertReturnString += 'Link Down Iperf Failed\n'

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
        if linkUpTemp:
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
        iperfTemp = main.Mininet1.iperftcp( host1,host2,10 )
        iperfResult = iperfResult and iperfTemp
        if iperfTemp:
            main.assertReturnString += 'Link Up Iperf Passed\n'
        else:
            main.assertReturnString += 'Link Up Iperf Failed\n'

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

def installSingleToMultiIntent( main,
                                name,
                                senders,
                                recipients,
                                onosNode=0,
                                ethType="",
                                bandwidth="",
                                lambdaAlloc=False,
                                ipProto="",
                                ipAddresses="",
                                tcp="",
                                sw1="",
                                sw2=""):
    """
    Installs a Single to Multi Point Intent

    Description:
        Install a single to multi point intent using
        add-single-to-multi-intent

    Steps:
        - Fetch host data if not given
        - Add single to multi intent
            - Ingress device is the first sender host
            - Egress devices are the recipient devices
            - Ports if defined in senders or recipients
            - MAC address ethSrc loaded from Ingress device
        - Check intent state with retry
    Required:
        name - Type of point intent to add eg. IPV4 | VLAN | Dualstack
        senders - List of host dictionaries i.e.
            { "name":"h8", "device":"of:0000000000000005/8","mac":"00:00:00:00:00:08" }
        recipients - List of host dictionaries i.e.
            { "name":"h16", "device":"of:0000000000000006/8", "mac":"00:00:00:00:00:10" }
    Optional:
        onosNode - ONOS node to install the intents in main.CLIs[ ]
                   0 by default so that it will always use the first
                   ONOS node
        ethType - Ethernet type eg. IPV4, IPV6
        bandwidth - Bandwidth capacity
        lambdaAlloc - Allocate lambda, defaults to False
        ipProto - IP protocol
        tcp - TCP ports in the same order as the hosts in hostNames
        sw1 - First switch to bring down & up for rerouting purpose
        sw2 - Second switch to bring down & up for rerouting purpose
        expectedLink - Expected link when the switches are down, it should
                       be two links lower than the links before the two
                       switches are down
    """

    assert main, "There is no main variable"
    assert senders, "You must specify a sender"
    assert recipients, "You must specify a recipient"
    # Assert devices or main.hostsData, "You must specify devices"

    global itemName  # The name of this run. Used for logs.
    itemName = name
    onosNode = int( onosNode )

    main.log.info( itemName + ": Adding single point to multi point intents" )

    for sender in senders:
        if not sender.get( "device" ):
            main.log.warn( "Device not given for sender {0}. Loading from main.hostData".format( sender.get( "name" ) ) )
            sender[ "device" ] = main.hostsData.get( sender.get( "name" ) ).get( "location" )

    for recipient in recipients:
        if not recipient.get( "device" ):
            main.log.warn( "Device not given for recipient {0}. Loading from main.hostData".format( recipient.get( "name" ) ) )
            recipient[ "device" ] = main.hostsData.get( recipient.get( "name" ) ).get( "location" )


    ingressDevice = senders[ 0 ].get( "device" )
    egressDeviceList = [ x.get( "device" ) for x in recipients if x.get( "device" ) ]

    portIngress = senders[ 0 ].get( "port", "" )
    portEgressList = [ x.get( "port" ) for x in recipients if x.get( "port" ) ]
    if not portEgressList:
        portEgressList = None

    srcMac = senders[ 0 ].get( "mac" )

    # Adding point intent
    intentId = main.CLIs[ onosNode ].addSinglepointToMultipointIntent(
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
                                        tcpDst="" )

    # Check intents state
    if utilities.retry( f=checkIntentState, retValue=main.FALSE, args=( main, [ intentId ] ), sleep=main.checkIntentSleep ):
        return intentId
    else:
        main.log.error( "Single to Multi Intent did not install correctly" )
        return main.FALSE

def installMultiToSingleIntent( main,
                                name,
                                senders,
                                recipients,
                                onosNode=0,
                                ethType="",
                                bandwidth="",
                                lambdaAlloc=False,
                                ipProto="",
                                ipAddresses="",
                                tcp="",
                                sw1="",
                                sw2=""):
    """
    Installs a Multi to Single Point Intent

    Description:
        Install a multi to single point intent using
        add-multi-to-single-intent

    Steps:
        - Fetch host data if not given
        - Add multi to single intent
            - Ingress devices are the senders devices
            - Egress device is the first recipient host
            - Ports if defined in senders or recipients
            - MAC address ethSrc loaded from Ingress device
        - Check intent state with retry
    Required:
        name - Type of point intent to add eg. IPV4 | VLAN | Dualstack
        senders - List of host dictionaries i.e.
            [ { "name":"h8", "device":"of:0000000000000005/8","mac":"00:00:00:00:00:08" } ]
        recipients - List of host dictionaries i.e.
            [ { "name":"h16", "device":"of:0000000000000006/8", "mac":"00:00:00:00:00:10" } ]
    Optional:
        onosNode - ONOS node to install the intents in main.CLIs[ ]
                   0 by default so that it will always use the first
                   ONOS node
        ethType - Ethernet type eg. IPV4, IPV6
        bandwidth - Bandwidth capacity
        lambdaAlloc - Allocate lambda, defaults to False
        ipProto - IP protocol
        tcp - TCP ports in the same order as the hosts in hostNames
        sw1 - First switch to bring down & up for rerouting purpose
        sw2 - Second switch to bring down & up for rerouting purpose
        expectedLink - Expected link when the switches are down, it should
                       be two links lower than the links before the two
                       switches are down
    """

    assert main, "There is no main variable"
    assert senders, "You must specify a sender"
    assert recipients, "You must specify a recipient"
    # Assert devices or main.hostsData, "You must specify devices"

    global itemName  # The name of this run. Used for logs.
    itemName = name
    onosNode = int( onosNode )

    main.log.info( itemName + ": Adding mutli to single point intents" )

    for sender in senders:
        if not sender.get( "device" ):
            main.log.warn( "Device not given for sender {0}. Loading from main.hostData".format( sender.get( "name" ) ) )
            sender[ "device" ] = main.hostsData.get( sender.get( "name" ) ).get( "location" )

    for recipient in recipients:
        if not recipient.get( "device" ):
            main.log.warn( "Device not given for recipient {0}. Loading from main.hostData".format( recipient.get( "name" ) ) )
            recipient[ "device" ] = main.hostsData.get( recipient.get( "name" ) ).get( "location" )


    ingressDeviceList = [ x.get( "device" ) for x in senders if x.get( "device" ) ]
    egressDevice = recipients[ 0 ].get( "device" )

    portIngressList = [ x.get( "port" ) for x in senders if x.get( "port" ) ]
    portEgress = recipients[ 0 ].get( "port", "" )
    if not portIngressList:
        portIngressList = None

    dstMac = recipients[ 0 ].get( "mac" )

    # Adding point intent
    intentId = main.CLIs[ onosNode ].addMultipointToSinglepointIntent(
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
                                        tcpDst="" )

    # Check intents state
    if utilities.retry( f=checkIntentState, retValue=main.FALSE, args=( main, [ intentId ] ), sleep=main.checkIntentSleep ):
        return intentId
    else:
        main.log.error( "Multi to Single Intent did not install correctly" )
        return main.FALSE

def testPointIntent( main,
                     name,
                     intentId,
                     senders,
                     recipients,
                     badSenders={},
                     badRecipients={},
                     onosNode=0,
                     ethType="",
                     bandwidth="",
                     lambdaAlloc=False,
                     ipProto="",
                     ipAddresses="",
                     tcp="",
                     sw1="s5",
                     sw2="s2",
                     expectedLink=0):
    """
    Test a Point Intent

    Description:
        Test a point intent

    Steps:
        - Fetch host data if not given
        - Check Intent State
        - Check Flow State
        - Check Connectivity
        - Check Lack of Connectivity Between Hosts not in the Intent
        - Reroute
            - Take Expected Link Down
            - Check Intent State
            - Check Flow State
            - Check Topology
            - Check Connectivity
            - Bring Expected Link Up
            - Check Intent State
            - Check Flow State
            - Check Topology
            - Check Connectivity
        - Remove Topology

    Required:
        name - Type of point intent to add eg. IPV4 | VLAN | Dualstack

        senders - List of host dictionaries i.e.
            { "name":"h8", "device":"of:0000000000000005/8","mac":"00:00:00:00:00:08" }
        recipients - List of host dictionaries i.e.
            { "name":"h16", "device":"of:0000000000000006/8", "mac":"00:00:00:00:00:10" }
    Optional:
        onosNode - ONOS node to install the intents in main.CLIs[ ]
                   0 by default so that it will always use the first
                   ONOS node
        ethType - Ethernet type eg. IPV4, IPV6
        bandwidth - Bandwidth capacity
        lambdaAlloc - Allocate lambda, defaults to False
        ipProto - IP protocol
        tcp - TCP ports in the same order as the hosts in hostNames
        sw1 - First switch to bring down & up for rerouting purpose
        sw2 - Second switch to bring down & up for rerouting purpose
        expectedLink - Expected link when the switches are down, it should
                       be two links lower than the links before the two
                       switches are down

    """

    # Parameter Validity Check
    assert main, "There is no main variable"
    assert senders, "You must specify a sender"
    assert recipients, "You must specify a recipient"

    global itemName
    itemName = name
    tempHostsData = {}
    onosNode = int( onosNode )

    main.log.info( itemName + ": Testing Point Intent" )

    # Names for scapy
    senderNames = [ x.get( "name" ) for x in senders ]
    recipientNames = [ x.get( "name" ) for x in recipients ]
    badSenderNames = [ x.get( "name" ) for x in badSenders ]
    badRecipientNames = [ x.get( "name" ) for x in badRecipients ]

    for sender in senders:
        if not sender.get( "device" ):
            main.log.warn( "Device not given for sender {0}. Loading from main.hostData".format( sender.get( "name" ) ) )
            sender[ "device" ] = main.hostsData.get( sender.get( "name" ) ).get( "location" )

    for recipient in recipients:
        if not recipient.get( "device" ):
            main.log.warn( "Device not given for recipient {0}. Loading from main.hostData".format( recipient.get( "name" ) ) )
            recipient[ "device" ] = main.hostsData.get( recipient.get( "name" ) ).get( "location" )

    testResult = main.TRUE
    main.log.info( itemName + ": Adding single point to multi point intents" )

    # Check intent state
    if utilities.retry( f=checkIntentState, retValue=main.FALSE, args=( main, [ intentId ] ), sleep=main.checkIntentSleep ):
        main.assertReturnString += 'Initial Intent State Passed\n'
    else:
        main.assertReturnString += 'Initial Intent State Failed\n'
        testResult = main.FALSE

    # Check flows count in each node
    if utilities.retry( f=checkFlowsCount, retValue=main.FALSE, args=[ main ] ) and utilities.retry( f=checkFlowsState, retValue=main.FALSE, args=[ main ] ):
        main.assertReturnString += 'Initial Flow State Passed\n'
    else:
        main.assertReturnString += 'Intial Flow State Failed\n'
        testResult = main.FALSE

    # Check Connectivity
    if utilities.retry( f=scapyCheckConnection, retValue=main.FALSE, args=( main, senderNames, recipientNames ) ):
        main.assertReturnString += 'Initial Ping Passed\n'
    else:
        main.assertReturnString += 'Initial Ping Failed\n'
        testResult = main.FALSE

    # Check connections that shouldn't work
    if badSenderNames:
        main.log.info( "Checking that packets from incorrect sender do not go through" )
        if utilities.retry( f=scapyCheckConnection, retValue=main.FALSE, args=( main, badSenderNames, recipientNames ), kwargs={ "expectFailure":True } ):
            main.assertReturnString += 'Bad Sender Ping Passed\n'
        else:
            main.assertReturnString += 'Bad Sender Ping Failed\n'
            testResult = main.FALSE

    if badRecipientNames:
        main.log.info( "Checking that packets to incorrect recipients do not go through" )
        if utilities.retry( f=scapyCheckConnection, retValue=main.FALSE, args=( main, senderNames, badRecipientNames ), kwargs={ "expectFailure":True } ):
            main.assertReturnString += 'Bad Recipient Ping Passed\n'
        else:
            main.assertReturnString += 'Bad Recipient Ping Failed\n'
            testResult = main.FALSE

    # Test rerouting if these variables exist
    if sw1 and sw2 and expectedLink:
        # Take link down
        if utilities.retry( f=link, retValue=main.FALSE, args=( main, sw1, sw2, "down" ) ):
            main.assertReturnString += 'Link Down Passed\n'
        else:
            main.assertReturnString += 'Link Down Failed\n'
            testResult = main.FALSE

        # Check intent state
        if utilities.retry( f=checkIntentState, retValue=main.FALSE, args=( main, [ intentId ] ), sleep=main.checkIntentSleep ):
            main.assertReturnString += 'Link Down Intent State Passed\n'
        else:
            main.assertReturnString += 'Link Down Intent State Failed\n'
            testResult = main.FALSE

        # Check flows count in each node
        if utilities.retry( f=checkFlowsCount, retValue=main.FALSE, args=[ main ] ) and utilities.retry( f=checkFlowsState, retValue=main.FALSE, args=[ main ] ):
            main.assertReturnString += 'Link Down Flow State Passed\n'
        else:
            main.assertReturnString += 'Link Down Flow State Failed\n'
            testResult = main.FALSE

        # Check OnosTopology
        if utilities.retry( f=checkTopology, retValue=main.FALSE, args=( main, expectedLink ) ):
            main.assertReturnString += 'Link Down Topology State Passed\n'
        else:
            main.assertReturnString += 'Link Down Topology State Failed\n'
            testResult = main.FALSE

        # Check Connection
        if utilities.retry( f=scapyCheckConnection, retValue=main.FALSE, args=( main, senderNames, recipientNames ) ):
            main.assertReturnString += 'Link Down Pingall Passed\n'
        else:
            main.assertReturnString += 'Link Down Pingall Failed\n'
            testResult = main.FALSE

        # Bring link up
        if utilities.retry( f=link, retValue=main.FALSE, args=( main, sw1, sw2, "up" ) ):
            main.assertReturnString += 'Link Up Passed\n'
        else:
            main.assertReturnString += 'Link Up Failed\n'
            testResult = main.FALSE

        # Wait for reroute
        time.sleep( main.rerouteSleep )

        # Check Intents
        if utilities.retry( f=checkIntentState, retValue=main.FALSE, args=( main, [ intentId ] ), sleep=main.checkIntentSleep ):
            main.assertReturnString += 'Link Up Intent State Passed\n'
        else:
            main.assertReturnString += 'Link Up Intent State Failed\n'
            testResult = main.FALSE

        # Check flows count in each node
        if utilities.retry( f=checkFlowsCount, retValue=main.FALSE, args=[ main ] ) and utilities.retry( f=checkFlowsState, retValue=main.FALSE, args=[ main ] ):
            main.assertReturnString += 'Link Up Flow State Passed\n'
        else:
            main.assertReturnString += 'Link Up Flow State Failed\n'
            testResult = main.FALSE

        # Check OnosTopology
        if utilities.retry( f=checkTopology, retValue=main.FALSE, args=( main, main.numLinks ) ):
            main.assertReturnString += 'Link Up Topology State Passed\n'
        else:
            main.assertReturnString += 'Link Up Topology State Failed\n'
            testResult = main.FALSE

        # Check Connection
        if utilities.retry( f=scapyCheckConnection, retValue=main.FALSE, args=( main, senderNames, recipientNames ) ):
            main.assertReturnString += 'Link Up Scapy Packet Received Passed\n'
        else:
            main.assertReturnString += 'Link Up Scapy Packet Recieved Failed\n'
            testResult = main.FALSE

    # Remove all intents
    if utilities.retry( f=removeAllIntents, retValue=main.FALSE, args=( main, [ intentId ] ) ):
        main.assertReturnString += 'Remove Intents Passed'
    else:
        main.assertReturnString += 'Remove Intents Failed'
        testResult = main.FALSE

    return testResult

def testEndPointFail( main,
                      name,
                      intentId,
                      senders,
                      recipients,
                      isolatedSenders,
                      isolatedRecipients,
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
    Test Single to Multipoint Topology for Endpoint failures
    """

    # Parameter Validity Check
    assert main, "There is no main variable"
    assert senders, "You must specify a sender"
    assert recipients, "You must specify a recipient"

    global itemName
    itemName = name
    tempHostsData = {}
    onosNode = int( onosNode )

    main.log.info( itemName + ": Testing Point Intent" )

    # Names for scapy
    senderNames = [ x.get( "name" ) for x in senders ]
    recipientNames = [ x.get( "name" ) for x in recipients ]
    isolatedSenderNames = [ x.get( "name" ) for x in isolatedSenders ]
    isolatedRecipientNames = [ x.get( "name" ) for x in isolatedRecipients ]
    connectedSenderNames = [x.get("name") for x in senders if x.get("name") not in isolatedSenderNames]
    connectedRecipientNames = [x.get("name") for x in recipients if x.get("name") not in isolatedRecipientNames]

    for sender in senders:
        if not sender.get( "device" ):
            main.log.warn( "Device not given for sender {0}. Loading from main.hostData".format( sender.get( "name" ) ) )
            sender[ "device" ] = main.hostsData.get( sender.get( "name" ) ).get( "location" )

    for recipient in recipients:
        if not recipient.get( "device" ):
            main.log.warn( "Device not given for recipient {0}. Loading from\
                            main.hostData".format( recipient.get( "name" ) ) )
            recipient[ "device" ] = main.hostsData.get( recipient.get( "name" ) ).get( "location" )

    testResult = main.TRUE
    main.log.info( itemName + ": Adding multi point to single point intents" )

    # Check intent state
    if utilities.retry( f=checkIntentState, retValue=main.FALSE,
                        args=( main, [ intentId ] ), sleep=main.checkIntentSleep ):
        main.assertReturnString += 'Initial Intent State Passed\n'
    else:
        main.assertReturnString += 'Initial Intent State Failed\n'
        testResult = main.FALSE

    # Check flows count in each node
    if utilities.retry( f=checkFlowsCount, retValue=main.FALSE,
                        args=[ main ] ) and utilities.retry( f=checkFlowsState,
                                                             retValue=main.FALSE,
                                                             args=[ main ] ):
        main.assertReturnString += 'Initial Flow State Passed\n'
    else:
        main.assertReturnString += 'Intial Flow State Failed\n'
        testResult = main.FALSE

    # Check Connectivity
    if utilities.retry( f=scapyCheckConnection, retValue=main.FALSE,
                        args=( main, senderNames, recipientNames ) ):
        main.assertReturnString += 'Initial Connectivity Check Passed\n'
    else:
        main.assertReturnString += 'Initial Connectivity Check Failed\n'
        testResult = main.FALSE

    # Take two links down
    # Take first link down
    if utilities.retry( f=link, retValue=main.FALSE, args=( main, sw1, sw2, "down" ) ):
        main.assertReturnString += 'Link Down Passed\n'
    else:
        main.assertReturnString += 'Link Down Failed\n'
        testResult = main.FALSE

    # Take second link down
    if utilities.retry( f=link, retValue=main.FALSE, args=( main, sw3, sw4, "down" ) ):
        main.assertReturnString += 'Link Down Passed\n'
    else:
        main.assertReturnString += 'Link Down Failed\n'
        testResult = main.FALSE

    # Check intent state
    if utilities.retry( f=checkIntentState, retValue=main.FALSE,
                        args=( main, [ intentId ] ), sleep=main.checkIntentSleep ):
        main.assertReturnString += 'Link Down Intent State Passed\n'
    else:
        main.assertReturnString += 'Link Down Intent State Failed\n'
        testResult = main.FALSE

    # Check flows count in each node
    if utilities.retry( f=checkFlowsCount, retValue=main.FALSE,
                        args=[ main ] ) and utilities.retry( f=checkFlowsState,
                                                             retValue=main.FALSE, args=[ main ] ):
        main.assertReturnString += 'Link Down Flow State Passed\n'
    else:
        main.assertReturnString += 'Link Down Flow State Failed\n'
        testResult = main.FALSE

    # Check OnosTopology
    if utilities.retry( f=checkTopology, retValue=main.FALSE, args=( main, expectedLink1 ) ):
        main.assertReturnString += 'Link Down Topology State Passed\n'
    else:
        main.assertReturnString += 'Link Down Topology State Failed\n'
        testResult = main.FALSE

    # Check Connection
    if utilities.retry( f=scapyCheckConnection, retValue=main.FALSE,
                        args=( main, senderNames, recipientNames ) ):
        main.assertReturnString += 'Link Down Connectivity Check Passed\n'
    else:
        main.assertReturnString += 'Link Down Connectivity Check Failed\n'
        testResult = main.FALSE

    # Take a third link down to isolate one node
    if utilities.retry( f=link, retValue=main.FALSE, args=( main, sw3, sw5, "down" ) ):
        main.assertReturnString += 'Isolation link Down Passed\n'
    else:
        main.assertReturnString += 'Isolation link Down Failed\n'
        testResult = main.FALSE

    # Check intent state
    if utilities.retry( f=checkIntentState, retValue=main.FALSE,
                        args=( main, [ intentId ] ), sleep=main.checkIntentSleep ):
        main.assertReturnString += 'Isolation link Down Intent State Passed\n'
    else:
        main.assertReturnString += 'Isolation link Down Intent State Failed\n'
        testResult = main.FALSE

    # Check flows count in each node
    if utilities.retry( f=checkFlowsCount, retValue=main.FALSE,
                        args=[ main ] ) and utilities.retry( f=checkFlowsState,
                                                             retValue=main.FALSE, args=[ main ] ):
        main.assertReturnString += 'Isolation link Down Flow State Passed\n'
    else:
        main.assertReturnString += 'Isolation link Down Flow State Failed\n'
        testResult = main.FALSE

    # Check OnosTopology
    if utilities.retry( f=checkTopology, retValue=main.FALSE, args=( main, expectedLink2 ) ):
        main.assertReturnString += 'Isolation link Down Topology State Passed\n'
    else:
        main.assertReturnString += 'Isolation link Down Topology State Failed\n'
        testResult = main.FALSE

    # Check Connectivity
    # First check connectivity of any isolated senders to recipients
    if isolatedSenderNames:
        if scapyCheckConnection( main, isolatedSenderNames, recipientNames, None, None, main.TRUE ):
            main.assertReturnString += 'Isolation link Down Connectivity Check Passed\n'
        else:
            main.assertReturnString += 'Isolation link Down Connectivity Check Failed\n'
            testResult = main.FALSE

    # Next check connectivity of senders to any isolated recipients
    if isolatedRecipientNames:
        if scapyCheckConnection( main, senderNames, isolatedRecipientNames, None, None, main.TRUE ):
            main.assertReturnString += 'Isolation link Down Connectivity Check Passed\n'
        else:
            main.assertReturnString += 'Isolation link Down Connectivity Check Failed\n'
            testResult = main.FALSE

    # Next check connectivity of connected senders and recipients
    if utilities.retry( f=scapyCheckConnection, retValue=main.FALSE,
                        args=( main, connectedSenderNames , connectedRecipientNames ) ):
        main.assertReturnString += 'Isolation link Down Connectivity Check Passed\n'
    else:
        main.assertReturnString += 'Isolation link Down Connectivity Check Failed\n'
        testResult = main.FALSE

    # Bring the links back up
    # Bring first link up
    if utilities.retry( f=link, retValue=main.FALSE, args=( main, sw1, sw2, "up" ) ):
        main.assertReturnString += 'Link Up Passed\n'
    else:
        main.assertReturnString += 'Link Up Failed\n'
        testResult = main.FALSE

    # Bring second link up
    if utilities.retry( f=link, retValue=main.FALSE, args=( main, sw3, sw5, "up" ) ):
        main.assertReturnString += 'Link Up Passed\n'
    else:
        main.assertReturnString += 'Link Up Failed\n'
        testResult = main.FALSE

    # Bring third link up
    if utilities.retry( f=link, retValue=main.FALSE, args=( main, sw3, sw4, "up" ) ):
        main.assertReturnString += 'Link Up Passed\n'
    else:
        main.assertReturnString += 'Link Up Failed\n'
        testResult = main.FALSE

    # Wait for reroute
    time.sleep( main.rerouteSleep )

    # Check Intents
    if utilities.retry( f=checkIntentState, retValue=main.FALSE,
                        args=( main, [ intentId ] ), sleep=main.checkIntentSleep ):
        main.assertReturnString += 'Link Up Intent State Passed\n'
    else:
        main.assertReturnString += 'Link Up Intent State Failed\n'
        testResult = main.FALSE

    # Check flows count in each node
    if utilities.retry( f=checkFlowsCount, retValue=main.FALSE,
                        args=[ main ] ) and utilities.retry( f=checkFlowsState,
                                                             retValue=main.FALSE, args=[ main ] ):
        main.assertReturnString += 'Link Up Flow State Passed\n'
    else:
        main.assertReturnString += 'Link Up Flow State Failed\n'
        testResult = main.FALSE

    # Check OnosTopology
    if utilities.retry( f=checkTopology, retValue=main.FALSE, args=( main, main.numLinks ) ):
        main.assertReturnString += 'Link Up Topology State Passed\n'
    else:
        main.assertReturnString += 'Link Up Topology State Failed\n'
        testResult = main.FALSE

    # Check Connection
    if utilities.retry( f=scapyCheckConnection, retValue=main.FALSE,
                        args=( main, senderNames, recipientNames ) ):
        main.assertReturnString += 'Link Up Scapy Packet Received Passed\n'
    else:
        main.assertReturnString += 'Link Up Scapy Packet Recieved Failed\n'
        testResult = main.FALSE

    # Remove all intents
    if utilities.retry( f=removeAllIntents, retValue=main.FALSE, args=( main, [ intentId ] ) ):
        main.assertReturnString += 'Remove Intents Passed'
    else:
        main.assertReturnString += 'Remove Intents Failed'
        testResult = main.FALSE

    return testResult


def pingallHosts( main, hostList ):
    """
        Ping all host in the hosts list variable
    """
    main.log.info( "Pinging: " + str( hostList ) )
    return main.Mininet1.pingallHosts( hostList )

def fwdPingall( main ):
    """
        Use fwd app and pingall to discover all the hosts
    """
    activateResult = main.TRUE
    appCheck = main.TRUE
    getDataResult = main.TRUE
    main.log.info( "Activating reactive forwarding app " )
    activateResult = main.CLIs[ 0 ].activateApp( "org.onosproject.fwd" )

    # Wait for forward app activation to propagate
    time.sleep( main.fwdSleep )

    # Check that forwarding is enabled on all nodes
    for i in range( main.numCtrls ):
        appCheck = appCheck and main.CLIs[ i ].appToIDCheck()
        if appCheck != main.TRUE:
            main.log.warn( main.CLIs[ i ].apps() )
            main.log.warn( main.CLIs[ i ].appIDs() )

    # Send pingall in mininet
    main.log.info( "Run Pingall" )
    pingResult = main.Mininet1.pingall( timeout = 600 )

    main.log.info( "Deactivating reactive forwarding app " )
    deactivateResult = main.CLIs[ 0 ].deactivateApp( "org.onosproject.fwd" )
    if activateResult and deactivateResult:
        main.log.info( "Successfully used fwd app to discover hosts" )
        getDataResult = main.TRUE
    else:
        main.log.info( "Failed to use fwd app to discover hosts" )
        getDataResult = main.FALSE
    return getDataResult

def confirmHostDiscovery( main ):
    """
        Confirms that all ONOS nodes have discovered all scapy hosts
    """
    import collections
    scapyHostCount = len( main.scapyHosts )
    hosts = main.topo.getAllHosts( main )  # Get host data from each ONOS node
    hostFails = []  # Reset for each failed attempt

    #  Check for matching hosts on each node
    scapyHostIPs = [ x.hostIp for x in main.scapyHosts if x.hostIp != "0.0.0.0" ]
    for controller in range( main.numCtrls ):
        controllerStr = str( controller + 1 )  # ONOS node number
        # Compare Hosts
        # Load hosts data for controller node
        if hosts[ controller ] and "Error" not in hosts[ controller ]:
            try:
                hostData = json.loads( hosts[ controller ] )
            except ( TypeError, ValueError ):
                main.log.error( "Could not load json:" + str( hosts[ controller ] ) )
                hostFails.append( controllerStr )
            else:
                onosHostIPs = [ x.get( "ipAddresses" )[ 0 ]
                                for x in hostData
                                if len( x.get( "ipAddresses" ) ) > 0 ]
                if not set( collections.Counter( scapyHostIPs ) ).issubset( set ( collections.Counter( onosHostIPs ) ) ):
                    main.log.warn( "Controller {0} only sees nodes with {1} IPs. It should see all of the following: {2}".format( controllerStr, onosHostIPs, scapyHostIPs ) )
                    hostFails.append( controllerStr )
        else:
            main.log.error( "Hosts returned nothing or an error." )
            hostFails.append( controllerStr )

    if hostFails:
        main.log.error( "List of failed ONOS Nodes:" + ', '.join(map(str, hostFails )) )
        return main.FALSE
    else:
        return main.TRUE

def sendDiscoveryArp( main, hosts=None ):
    """
        Sends Discovery ARP packets from each host provided
        Defaults to each host in main.scapyHosts
    """
    # Send an arp ping from each host
    if not hosts:
        hosts = main.scapyHosts
    for host in hosts:
        pkt = 'Ether( src="{0}")/ARP( psrc="{1}")'.format( host.hostMac ,host.hostIp )
        # Send from the VLAN interface if there is one so ONOS discovers the VLAN correctly
        iface = None
        for interface in host.getIfList():
            if '.' in interface:
                main.log.debug( "Detected VLAN interface {0}. Sending ARP packet from {0}".format( interface ) )
                iface = interface
                break
        host.sendPacket( packet=pkt, iface=iface )
        main.log.info( "Sending ARP packet from {0}".format( host.name ) )

def populateHostData( main ):
    """
        Populates hostsData
    """
    import json
    try:
        hostsJson = json.loads( main.CLIs[ 0 ].hosts() )
        hosts = main.Mininet1.getHosts().keys()
        # TODO: Make better use of new getHosts function
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
        return main.TRUE
    except KeyError:
        main.log.error( "KeyError while populating hostsData")
        return main.FALSE

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
            tempResult = main.CLIs[ i ].checkIntentState( intentsId=intentsId )
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

def scapyCheckConnection( main, senders, recipients, packet=None, packetFilter=None, expectFailure=False ):
    """
        Checks the connectivity between all given sender hosts and all given recipient hosts
        Packet may be specified. Defaults to Ether/IP packet
        Packet Filter may be specified. Defaults to Ether/IP from current sender MAC
            Todo: Optional packet and packet filter attributes for sender and recipients
        Expect Failure when the sender and recipient are not supposed to have connectivity
            Timeout of 1 second, returns main.TRUE if the filter is not triggered and kills the filter

    """
    connectionsFunctional = main.TRUE

    if not packetFilter:
        packetFilter = 'ether host {}'

    if expectFailure:
        timeout = 1
    else:
        timeout = 10

    for sender in senders:
        try:
            senderComp = getattr( main, sender )
        except AttributeError:
            main.log.error( "main has no attribute {}".format( sender ) )
            connectionsFunctional = main.FALSE
            continue

        for recipient in recipients:
            # Do not send packets to self since recipient CLI will already be busy
            if recipient == sender:
                continue
            try:
                recipientComp = getattr( main, recipient )
            except AttributeError:
                main.log.error( "main has no attribute {}".format( recipient ) )
                connectionsFunctional = main.FALSE
                continue

            recipientComp.startFilter( pktFilter = packetFilter.format( senderComp.hostMac ) )

            if not packet:
                pkt = 'Ether( src="{0}", dst="{2}" )/IP( src="{1}", dst="{3}" )'.format(
                    senderComp.hostMac,
                    senderComp.hostIp,
                    recipientComp.hostMac,
                    recipientComp.hostIp )
            else:
                pkt = packet
            senderComp.sendPacket( packet = pkt )

            if recipientComp.checkFilter( timeout ):
                if expectFailure:
                    main.log.error( "Packet from {0} successfully received by {1} when it should not have been".format( sender , recipient ) )
                    connectionsFunctional = main.FALSE
                else:
                    main.log.info( "Packet from {0} successfully received by {1}".format( sender , recipient ) )
            else:
                recipientComp.killFilter()
                if expectFailure:
                    main.log.info( "As expected, packet from {0} was not received by {1}".format( sender , recipient ) )
                else:
                    main.log.error( "Packet from {0} was not received by {1}".format( sender , recipient ) )
                    connectionsFunctional = main.FALSE

        return connectionsFunctional

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
