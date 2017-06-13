"""
    Wrapper functions for FuncIntent
    This functions include Onosclidriver and Mininetclidriver driver functions
    Author: kelvin@onlab.us
"""
import time
import json
import os


def __init__( self ):
    self.default = ''

hostIntentFailFlag = False
pointIntentFailFlag = False
singleToMultiFailFlag = False
multiToSingleFailFlag = False


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
                       sw2="",
                       setVlan="",
                       encap="" ):
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

    global hostIntentFailFlag
    hostIntentFailFlag = False

    main.log.info( itemName + ": Adding single point to multi point intents" )
    try:
        if not host1.get( "id" ):
            main.log.warn( "ID not given for host1 {0}. Loading from main.hostData".format( host1.get( "name" ) ) )
            main.log.debug( main.hostsData.get( host1.get( "name" ) ) )
            host1[ "id" ] = main.hostsData.get( host1.get( "name" ) ).get( "id" )

        if not host2.get( "id" ):
            main.log.warn( "ID not given for host2 {0}. Loading from main.hostData".format( host2.get( "name" ) ) )
            host2[ "id" ] = main.hostsData.get( host2.get( "name" ) ).get( "id" )

        # Adding point intent
        vlanId = host1.get( "vlan" )
        intentId = main.CLIs[ onosNode ].addHostIntent( hostIdOne=host1.get( "id" ),
                                                        hostIdTwo=host2.get( "id" ),
                                                        vlanId=vlanId,
                                                        setVlan=setVlan,
                                                        encap=encap )
    except( KeyError, TypeError ):
        errorMsg = "There was a problem loading the hosts data."
        if intentId:
            errorMsg += "  There was a problem installing host to host intent."
        main.log.error( errorMsg )
        return main.FALSE

    # Check intents state
    if utilities.retry( f=checkIntentState,
                        retValue=main.FALSE,
                        args=( main, [ intentId ] ),
                        sleep=main.checkIntentSleep,
                        attempts=50 ):
        main.assertReturnString += 'Install Intent State Passed\n'

        # Check VLAN if test encapsulation
        if encap != "":
            if EncapsulatedIntentCheck( main, tag=encap ):
                main.assertReturnString += 'Encapsulation intents check Passed\n'
            else:
                main.assertReturnString += 'Encapsulation intents check failed\n'
        if bandwidth != "":
            allocationsFile = open( os.path.dirname( main.testFile ) + main.params[ 'DEPENDENCY' ][ 'filePath' ], 'r' )
            expectedFormat = allocationsFile.read()
            bandwidthCheck = checkBandwidthAllocations( main, expectedFormat )
            allocationsFile.close()
            if bandwidthCheck:
                main.assertReturnString += 'Bandwidth Allocation check Passed\n'
            else:
                main.assertReturnString += 'Bandwidth Allocation check Failed\n'
                return main.FALSE

        if flowDuration( main ):
            main.assertReturnString += 'Flow duration check Passed\n'
            return intentId
        else:
            main.assertReturnString += 'Flow duration check Failed\n'
            return main.FALSE

    else:
        main.log.error( "Host Intent did not install correctly" )
        hostIntentFailFlag = True
        main.assertReturnString += 'Install Intent State Failed\n'
        return main.FALSE


def testHostIntent( main,
                    name,
                    intentId,
                    host1,
                    host2,
                    onosNode=0,
                    sw1="s5",
                    sw2="s2",
                    expectedLink=0 ):
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

    global hostIntentFailFlag

    main.log.info( itemName + ": Testing Host Intent" )

    try:
        if not host1.get( "id" ):
            main.log.warn( "Id not given for host1 {0}. Loading from main.hostData".format( host1.get( "name" ) ) )
            host1[ "id" ] = main.hostsData.get( host1.get( "name" ) ).get( "location" )

        if not host2.get( "id" ):
            main.log.warn( "Id not given for host2 {0}. Loading from main.hostData".format( host2.get( "name" ) ) )
            host2[ "id" ] = main.hostsData.get( host2.get( "name" ) ).get( "location" )

        senderNames = [ host1.get( "name" ), host2.get( "name" ) ]
        recipientNames = [ host1.get( "name" ), host2.get( "name" ) ]
        vlanId = host1.get( "vlan" )

        testResult = main.TRUE
    except( KeyError, TypeError ):
        main.log.error( "There was a problem loading the hosts data." )
        return main.FALSE

    main.log.info( itemName + ": Testing Host to Host intents" )

    # Check intent state
    if hostIntentFailFlag:
        attempts = 1
    else:
        attempts = 50
    if utilities.retry( f=checkIntentState,
                        retValue=main.FALSE,
                        args=( main, [ intentId ] ),
                        sleep=main.checkIntentSleep,
                        attempts=attempts ):
        main.assertReturnString += 'Initial Intent State Passed\n'
    else:
        main.assertReturnString += 'Initial Intent State Failed\n'
        testResult = main.FALSE
        attempts = 1

    # Check flows count in each node
    if utilities.retry( f=checkFlowsCount,
                        retValue=main.FALSE,
                        args=[ main ],
                        sleep=main.checkFlowCountSleep,
                        attempts=3 ) and utilities.retry( f=checkFlowsState,
                                                          retValue=main.FALSE,
                                                          args=[ main ],
                                                          sleep=main.checkFlowCountSleep,
                                                          attempts=3 ):
        main.assertReturnString += 'Initial Flow State Passed\n'
    else:
        main.assertReturnString += 'Intial Flow State Failed\n'
        testResult = main.FALSE

    # Check Connectivity
    if utilities.retry( f=scapyCheckConnection,
                        retValue=main.FALSE,
                        attempts=attempts,
                        sleep=main.checkConnectionSleep,
                        args=( main, senderNames, recipientNames, vlanId ) ):
        main.assertReturnString += 'Initial Ping Passed\n'
    else:
        main.assertReturnString += 'Initial Ping Failed\n'
        testResult = main.FALSE

    # Test rerouting if these variables exist
    if sw1 and sw2 and expectedLink:
        # Take link down
        if utilities.retry( f=link,
                            retValue=main.FALSE,
                            args=( main, sw1, sw2, "down" ) ):
            main.assertReturnString += 'Link Down Passed\n'
        else:
            main.assertReturnString += 'Link Down Failed\n'
            testResult = main.FALSE

        # Check intent state
        if utilities.retry( f=checkIntentState,
                            retValue=main.FALSE,
                            args=( main, [ intentId ] ),
                            sleep=main.checkIntentHostSleep,
                            attempts=attempts ):
            main.assertReturnString += 'Link Down Intent State Passed\n'
        else:
            main.assertReturnString += 'Link Down Intent State Failed\n'
            testResult = main.FALSE

        # Check flows count in each node
        if utilities.retry( f=checkFlowsCount,
                            retValue=main.FALSE,
                            args=[ main ],
                            sleep=main.checkFlowCountSleep,
                            attempts=attempts ) and utilities.retry( f=checkFlowsState,
                                                                     retValue=main.FALSE,
                                                                     args=[ main ],
                                                                     sleep=main.checkFlowCountSleep,
                                                                     attempts=attempts ):
            main.assertReturnString += 'Link Down Flow State Passed\n'
        else:
            main.assertReturnString += 'Link Down Flow State Failed\n'
            testResult = main.FALSE

        # Check OnosTopology
        if utilities.retry( f=checkTopology,
                            retValue=main.FALSE,
                            args=( main, expectedLink ) ):
            main.assertReturnString += 'Link Down Topology State Passed\n'
        else:
            main.assertReturnString += 'Link Down Topology State Failed\n'
            testResult = main.FALSE

        # Check Connection
        if utilities.retry( f=scapyCheckConnection,
                            retValue=main.FALSE,
                            args=( main, senderNames, recipientNames, vlanId ),
                            sleep=main.checkConnectionSleep,
                            attempts=attempts ):
            main.assertReturnString += 'Link Down Pingall Passed\n'
        else:
            main.assertReturnString += 'Link Down Pingall Failed\n'
            testResult = main.FALSE

        # Bring link up
        if utilities.retry( f=link,
                            retValue=main.FALSE,
                            args=( main, sw1, sw2, "up" ) ):
            main.assertReturnString += 'Link Up Passed\n'
        else:
            main.assertReturnString += 'Link Up Failed\n'
            testResult = main.FALSE

        # Wait for reroute
        main.log.info( "Sleeping {} seconds".format( main.rerouteSleep ) )
        time.sleep( main.rerouteSleep )

        # Check Intents
        if utilities.retry( f=checkIntentState,
                            retValue=main.FALSE,
                            attempts=attempts * 2,
                            args=( main, [ intentId ] ),
                            sleep=main.checkIntentSleep ):
            main.assertReturnString += 'Link Up Intent State Passed\n'
        else:
            main.assertReturnString += 'Link Up Intent State Failed\n'
            testResult = main.FALSE

        # Check flows count in each node
        if utilities.retry( f=checkFlowsCount,
                            retValue=main.FALSE,
                            args=[ main ],
                            sleep=main.checkFlowCountSleep,
                            attempts=3 ) and utilities.retry( f=checkFlowsState,
                                                              retValue=main.FALSE,
                                                              args=[ main ],
                                                              sleep=main.checkFlowCountSleep,
                                                              attempts=3 ):
            main.assertReturnString += 'Link Up Flow State Passed\n'
        else:
            main.assertReturnString += 'Link Up Flow State Failed\n'
            testResult = main.FALSE

        # Check OnosTopology
        if utilities.retry( f=checkTopology,
                            retValue=main.FALSE,
                            args=( main, main.numLinks ) ):
            main.assertReturnString += 'Link Up Topology State Passed\n'
        else:
            main.assertReturnString += 'Link Up Topology State Failed\n'
            testResult = main.FALSE

        # Check Connection
        if utilities.retry( f=scapyCheckConnection,
                            retValue=main.FALSE,
                            args=( main, senderNames, recipientNames, vlanId ) ):
            main.assertReturnString += 'Link Up Pingall Passed\n'
        else:
            main.assertReturnString += 'Link Up Pingall Failed\n'
            testResult = main.FALSE

    # Remove all intents
    if utilities.retry( f=removeAllIntents,
                        retValue=main.FALSE,
                        attempts=10,
                        args=( main, [ intentId ] ) ):
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
                        protected=False,
                        ipProto="",
                        ipSrc="",
                        ipDst="",
                        tcpSrc="",
                        tcpDst="",
                        setVlan="",
                        encap="" ):
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

    global pointIntentFailFlag
    pointIntentFailFlag = False

    main.log.info( itemName + ": Adding point to point intents" )

    try:
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

        vlanId = senders[ 0 ].get( "vlan" )

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
                                            protected=protected,
                                            ipProto=ipProto,
                                            ipSrc=ipSrc,
                                            ipDst=ipDst,
                                            tcpSrc=tcpSrc,
                                            tcpDst=tcpDst,
                                            vlanId=vlanId,
                                            setVlan=setVlan,
                                            encap=encap )
    except( KeyError, TypeError ):
        errorMsg = "There was a problem loading the hosts data."
        if intentId:
            errorMsg += "  There was a problem installing Point to Point intent."
        main.log.error( errorMsg )
        return main.FALSE

    # Check intents state
    if utilities.retry( f=checkIntentState,
                        retValue=main.FALSE,
                        args=( main, [ intentId ] ),
                        sleep=main.checkIntentSleep,
                        attempts=50 ):
        main.assertReturnString += 'Install Intent State Passed\n'

        if bandwidth != "":
            allocationsFile = open( os.path.dirname( main.testFile ) + main.params[ 'DEPENDENCY' ][ 'filePath' ], 'r' )
            expectedFormat = allocationsFile.read()
            bandwidthCheck = checkBandwidthAllocations( main, expectedFormat )
            allocationsFile.close()
            if bandwidthCheck:
                main.assertReturnString += 'Bandwidth Allocation check Passed\n'
            else:
                main.assertReturnString += 'Bandwidth Allocation check Failed\n'
                return main.FALSE

        # Check VLAN if test encapsulation
        if encap != "":
            if EncapsulatedIntentCheck( main, tag=encap ):
                main.assertReturnString += 'Encapsulation intents check Passed\n'
            else:
                main.assertReturnString += 'Encapsulation intents check failed\n'

        if flowDuration( main ):
            main.assertReturnString += 'Flow duration check Passed\n'
            return intentId
        else:
            main.assertReturnString += 'Flow duration check failed\n'
            return main.FALSE
    else:
        main.log.error( "Point Intent did not install correctly" )
        pointIntentFailFlag = True
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
    intentsId = []

    iperfResult = main.TRUE
    linkDownResult = main.TRUE
    linkUpResult = main.TRUE

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
    main.log.info( "Sleeping {} seconds".format( main.checkIntentSleep ) )
    time.sleep( main.checkIntentSleep )
    intentResult = utilities.retry( f=checkIntentState,
                                    retValue=main.FALSE,
                                    args=( main, intentsId ),
                                    sleep=1,
                                    attempts=50 )
    # Check flows count in each node
    checkFlowsCount( main )

    # Check intents state again if first check fails...
    if not intentResult:
        intentResult = utilities.retry( f=checkIntentState,
                                        retValue=main.FALSE,
                                        args=( main, intentsId ),
                                        sleep=1,
                                        attempts=50 )

    # Check flows count in each node
    checkFlowsCount( main )

    # Verify flows
    checkFlowsState( main )

    # Run iperf to both host
    iperfTemp = main.Mininet1.iperftcp( host1, host2, 10 )
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
        iperfTemp = main.Mininet1.iperftcp( host1, host2, 10 )
        iperfResult = iperfResult and iperfTemp
        if iperfTemp:
            main.assertReturnString += 'Link Down Iperf Passed\n'
        else:
            main.assertReturnString += 'Link Down Iperf Failed\n'

        # Check intent state
        intentTemp = utilities.retry( f=checkIntentState,
                                      retValue=main.FALSE,
                                      args=( main, intentsId ),
                                      sleep=1,
                                      attempts=50 )
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

        main.log.info( "Sleeping {} seconds".format( main.rerouteSleep ) )
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
        iperfTemp = main.Mininet1.iperftcp( host1, host2, 10 )
        iperfResult = iperfResult and iperfTemp
        if iperfTemp:
            main.assertReturnString += 'Link Up Iperf Passed\n'
        else:
            main.assertReturnString += 'Link Up Iperf Failed\n'

        # Check intent state
        intentTemp = utilities.retry( f=checkIntentState,
                                      retValue=main.FALSE,
                                      args=( main, intentsId ),
                                      sleep=1,
                                      attempts=50 )
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
                                sw2="",
                                setVlan="",
                                partial=False,
                                encap="" ):
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

    global singleToMultiFailFlag
    singleToMultiFailFlag = False

    main.log.info( itemName + ": Adding single point to multi point intents" )

    try:
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
        vlanId = senders[ 0 ].get( "vlan" )

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
                                            tcpDst="",
                                            vlanId=vlanId,
                                            setVlan=setVlan,
                                            partial=partial,
                                            encap=encap )
    except( KeyError, TypeError ):
        errorMsg = "There was a problem loading the hosts data."
        if intentId:
            errorMsg += "  There was a problem installing Singlepoint to Multipoint intent."
        main.log.error( errorMsg )
        singleToMultiFailFlag = True
        return main.FALSE

    # Check intents state
    if singleToMultiFailFlag:
        attempts = 5
    else:
        attempts = 50

    if utilities.retry( f=checkIntentState,
                        retValue=main.FALSE,
                        args=( main, [ intentId ] ),
                        sleep=main.checkIntentSleep,
                        attempts=attempts ):
        main.assertReturnString += 'Install Intent State Passed\n'
        if bandwidth != "":
            allocationsFile = open( os.path.dirname( main.testFile ) + main.params[ 'DEPENDENCY' ][ 'filePath' ], 'r' )
            expectedFormat = allocationsFile.read()
            bandwidthCheck = checkBandwidthAllocations( main, expectedFormat )
            allocationsFile.close()
            if bandwidthCheck:
                main.assertReturnString += 'Bandwidth Allocation check Passed\n'
            else:
                main.assertReturnString += 'Bandwidth Allocation check Failed\n'
                return main.FALSE

        if flowDuration( main ):
            main.assertReturnString += 'Flow duration check Passed\n'
            return intentId
        else:
            main.assertReturnString += 'Flow duration check failed\n'
            return main.FALSE
    else:
        main.log.error( "Single to Multi Intent did not install correctly" )
        singleToMultiFailFlag = True
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
                                sw2="",
                                setVlan="",
                                partial=False,
                                encap="" ):
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

    global multiToSingleFailFlag
    multiToSingleFailFlag = False

    main.log.info( itemName + ": Adding mutli to single point intents" )

    try:
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
        vlanId = senders[ 0 ].get( "vlan" )

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
                                            tcpDst="",
                                            vlanId=vlanId,
                                            setVlan=setVlan,
                                            partial=partial,
                                            encap=encap )
    except( KeyError, TypeError ):
        errorMsg = "There was a problem loading the hosts data."
        if intentId:
            errorMsg += "  There was a problem installing Multipoint to Singlepoint intent."
        main.log.error( errorMsg )
        multiToSingleFailFlag = True
        return main.FALSE

    # Check intents state
    if multiToSingleFailFlag:
        attempts = 5
    else:
        attempts = 50

    if utilities.retry( f=checkIntentState,
                        retValue=main.FALSE,
                        args=( main, [ intentId ] ),
                        sleep=main.checkIntentSleep,
                        attempts=attempts ):
        main.assertReturnString += 'Install Intent State Passed\n'
        if bandwidth != "":
            allocationsFile = open( os.path.dirname( main.testFile ) + main.params[ 'DEPENDENCY' ][ 'filePath' ], 'r' )
            expectedFormat = allocationsFile.read()
            bandwidthCheck = checkBandwidthAllocations( main, expectedFormat )
            allocationsFile.close()
            if bandwidthCheck:
                main.assertReturnString += 'Bandwidth Allocation check Passed\n'
            else:
                main.assertReturnString += 'Bandwidth Allocation check Failed\n'
                return main.FALSE

        if flowDuration( main ):
            main.assertReturnString += 'Flow duration check Passed\n'
            return intentId
        else:
            main.assertReturnString += 'Flow duration check failed\n'
            return main.FALSE
    else:
        main.log.error( "Multi to Single Intent did not install correctly" )
        multiToSingleFailFlag = True
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
                     protected=False,
                     ipProto="",
                     ipAddresses="",
                     tcp="",
                     sw1="s5",
                     sw2="s2",
                     expectedLink=0,
                     useTCP=False ):
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

    global pointIntentFailFlag
    global singleToMultiFailFlag
    global multiToSingleFailFlag

    main.log.info( itemName + ": Testing Point Intent" )

    try:
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
        vlanId = senders[ 0 ].get( "vlan" )
    except( KeyError, TypeError ):
        main.log.error( "There was a problem loading the hosts data." )
        return main.FALSE

    testResult = main.TRUE
    main.log.info( itemName + ": Adding single point to multi point intents" )

    if pointIntentFailFlag or singleToMultiFailFlag or multiToSingleFailFlag:
        attempts = 1
    else:
        attempts = 50

    # Check intent state
    if utilities.retry( f=checkIntentState,
                        retValue=main.FALSE,
                        args=( main, [ intentId ] ),
                        sleep=main.checkIntentSleep,
                        attempts=attempts ):
        main.assertReturnString += 'Initial Intent State Passed\n'
    else:
        main.assertReturnString += 'Initial Intent State Failed\n'
        testResult = main.FALSE
        attempts = 1

    # Check flows count in each node
    if utilities.retry( f=checkFlowsCount,
                        retValue=main.FALSE,
                        args=[ main ],
                        sleep=main.checkFlowCountSleep,
                        attempts=attempts ) and utilities.retry( f=checkFlowsState,
                                                                 retValue=main.FALSE,
                                                                 args=[ main ],
                                                                 sleep=main.checkFlowCountSleep,
                                                                 attempts=attempts ):
        main.assertReturnString += 'Initial Flow State Passed\n'
    else:
        main.assertReturnString += 'Intial Flow State Failed\n'
        testResult = main.FALSE

    # Check Connectivity
    if utilities.retry( f=scapyCheckConnection,
                        retValue=main.FALSE,
                        args=( main, senderNames, recipientNames, vlanId, useTCP ),
                        attempts=attempts,
                        sleep=main.checkConnectionSleep ):
        main.assertReturnString += 'Initial Ping Passed\n'
    else:
        main.assertReturnString += 'Initial Ping Failed\n'
        testResult = main.FALSE

    # Check connections that shouldn't work
    if badSenderNames:
        main.log.info( "Checking that packets from incorrect sender do not go through" )
        if utilities.retry( f=scapyCheckConnection,
                            retValue=main.FALSE,
                            args=( main, badSenderNames, recipientNames ),
                            kwargs={ "expectFailure": True } ):
            main.assertReturnString += 'Bad Sender Ping Passed\n'
        else:
            main.assertReturnString += 'Bad Sender Ping Failed\n'
            testResult = main.FALSE

    if badRecipientNames:
        main.log.info( "Checking that packets to incorrect recipients do not go through" )
        if utilities.retry( f=scapyCheckConnection,
                            retValue=main.FALSE,
                            args=( main, senderNames, badRecipientNames ),
                            kwargs={ "expectFailure": True } ):
            main.assertReturnString += 'Bad Recipient Ping Passed\n'
        else:
            main.assertReturnString += 'Bad Recipient Ping Failed\n'
            testResult = main.FALSE

    # Test rerouting if these variables exist
    if sw1 and sw2 and expectedLink:
        # Take link down
        if utilities.retry( f=link,
                            retValue=main.FALSE,
                            args=( main, sw1, sw2, "down" ) ):
            main.assertReturnString += 'Link Down Passed\n'
        else:
            main.assertReturnString += 'Link Down Failed\n'
            testResult = main.FALSE

        if protected:
            # Check Connection
            if utilities.retry( f=scapyCheckConnection,
                                retValue=main.FALSE,
                                args=( main, senderNames, recipientNames, vlanId, useTCP ) ):
                main.assertReturnString += 'Link down Scapy Packet Received Passed\n'
            else:
                main.assertReturnString += 'Link down Scapy Packet Recieved Failed\n'
                testResult = main.FALSE

            if ProtectedIntentCheck( main ):
                main.assertReturnString += 'Protected Intent Check Passed\n'
            else:
                main.assertReturnString += 'Protected Intent Check Failed\n'
                testResult = main.FALSE

        # Check intent state
        if utilities.retry( f=checkIntentState,
                            retValue=main.FALSE,
                            args=( main, [ intentId ] ),
                            sleep=main.checkIntentPointSleep,
                            attempts=attempts ):
            main.assertReturnString += 'Link Down Intent State Passed\n'
        else:
            main.assertReturnString += 'Link Down Intent State Failed\n'
            testResult = main.FALSE

        # Check flows count in each node
        if utilities.retry( f=checkFlowsCount,
                            retValue=main.FALSE,
                            args=[ main ],
                            sleep=main.checkFlowCountSleep,
                            attempts=attempts ) and utilities.retry( f=checkFlowsState,
                                                                         retValue=main.FALSE,
                                                                         args=[ main ],
                                                                         sleep=main.checkFlowCountSleep,
                                                                         attempts=attempts ):
            main.assertReturnString += 'Link Down Flow State Passed\n'
        else:
            main.assertReturnString += 'Link Down Flow State Failed\n'
            testResult = main.FALSE

        # Check OnosTopology
        if utilities.retry( f=checkTopology,
                            retValue=main.FALSE,
                            args=( main, expectedLink ) ):
            main.assertReturnString += 'Link Down Topology State Passed\n'
        else:
            main.assertReturnString += 'Link Down Topology State Failed\n'
            testResult = main.FALSE

        # Check Connection
        if utilities.retry( f=scapyCheckConnection,
                            retValue=main.FALSE,
                            args=( main, senderNames, recipientNames, vlanId, useTCP ),
                            sleep=main.checkConnectionSleep,
                            attempts=attempts ):
            main.assertReturnString += 'Link Down Pingall Passed\n'
        else:
            main.assertReturnString += 'Link Down Pingall Failed\n'
            testResult = main.FALSE

        # Bring link up
        if utilities.retry( f=link,
                            retValue=main.FALSE,
                            args=( main, sw1, sw2, "up" ) ):
            main.assertReturnString += 'Link Up Passed\n'
        else:
            main.assertReturnString += 'Link Up Failed\n'
            testResult = main.FALSE

        # Wait for reroute
        main.log.info( "Sleeping {} seconds".format( main.rerouteSleep ) )
        time.sleep( main.rerouteSleep )

        # Check Intents
        if utilities.retry( f=checkIntentState,
                            retValue=main.FALSE,
                            attempts=attempts * 2,
                            args=( main, [ intentId ] ),
                            sleep=main.checkIntentSleep ):
            main.assertReturnString += 'Link Up Intent State Passed\n'
        else:
            main.assertReturnString += 'Link Up Intent State Failed\n'
            testResult = main.FALSE

        # Check flows count in each node
        if utilities.retry( f=checkFlowsCount,
                            retValue=main.FALSE,
                            args=[ main ],
                            sleep=main.checkFlowCountSleep,
                            attempts=attempts ) and utilities.retry( f=checkFlowsState,
                                                                     retValue=main.FALSE,
                                                                     args=[ main ],
                                                                     sleep=main.checkFlowCountSleep,
                                                                     attempts=attempts ):
            main.assertReturnString += 'Link Up Flow State Passed\n'
        else:
            main.assertReturnString += 'Link Up Flow State Failed\n'
            testResult = main.FALSE

        # Check OnosTopology
        if utilities.retry( f=checkTopology,
                            retValue=main.FALSE,
                            args=( main, main.numLinks ) ):
            main.assertReturnString += 'Link Up Topology State Passed\n'
        else:
            main.assertReturnString += 'Link Up Topology State Failed\n'
            testResult = main.FALSE

        # Check Connection
        if utilities.retry( f=scapyCheckConnection,
                            retValue=main.FALSE,
                            sleep=main.checkConnectionSleep,
                            attempts=attempts,
                            args=( main, senderNames, recipientNames, vlanId, useTCP ) ):
            main.assertReturnString += 'Link Up Scapy Packet Received Passed\n'
        else:
            main.assertReturnString += 'Link Up Scapy Packet Recieved Failed\n'
            testResult = main.FALSE

    # Remove all intents
    if utilities.retry( f=removeAllIntents,
                        retValue=main.FALSE,
                        attempts=10,
                        args=( main, [ intentId ] ) ):
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
                      expectedLink2=0,
                      partial=False ):
    """
    Test Multi point to single point intent Topology for Endpoint failures
    """
    # Parameter Validity Check
    assert main, "There is no main variable"
    assert senders, "You must specify a sender"
    assert recipients, "You must specify a recipient"

    global itemName
    itemName = name

    global singleToMultiFailFlag
    global multiToSingleFailFlag

    main.log.info( itemName + ": Testing Point Intent" )

    try:
        # Names for scapy
        senderNames = [ x.get( "name" ) for x in senders ]
        recipientNames = [ x.get( "name" ) for x in recipients ]
        isolatedSenderNames = [ x.get( "name" ) for x in isolatedSenders ]
        isolatedRecipientNames = [ x.get( "name" ) for x in isolatedRecipients ]
        connectedSenderNames = [ x.get( "name" ) for x in senders if x.get( "name" ) not in isolatedSenderNames ]
        connectedRecipientNames = [ x.get( "name" ) for x in recipients if x.get( "name" ) not in isolatedRecipientNames ]

        for sender in senders:
            if not sender.get( "device" ):
                main.log.warn( "Device not given for sender {0}. Loading from main.hostData".format( sender.get( "name" ) ) )
                sender[ "device" ] = main.hostsData.get( sender.get( "name" ) ).get( "location" )

        for recipient in recipients:
            if not recipient.get( "device" ):
                main.log.warn( "Device not given for recipient {0}. Loading from " +
                                main.hostData.format( recipient.get( "name" ) ) )
                recipient[ "device" ] = main.hostsData.get( recipient.get( "name" ) ).get( "location" )
    except( KeyError, TypeError ):
        main.log.error( "There was a problem loading the hosts data." )
        return main.FALSE

    testResult = main.TRUE
    main.log.info( itemName + ": Adding multi point to single point intents" )

    # Check intent state
    if singleToMultiFailFlag or multiToSingleFailFlag:
        attempts = 1
    else:
        attempts = 50

    if utilities.retry( f=checkIntentState,
                        retValue=main.FALSE,
                        args=( main, [ intentId ] ),
                        sleep=main.checkIntentSleep,
                        attempts=attempts ):
        main.assertReturnString += 'Initial Intent State Passed\n'
    else:
        main.assertReturnString += 'Initial Intent State Failed\n'
        testResult = main.FALSE
        attempts = 1

    # Check flows count in each node
    if utilities.retry( f=checkFlowsCount,
                        retValue=main.FALSE,
                        args=[ main ],
                        attempts=5 ) and utilities.retry( f=checkFlowsState,
                                                          retValue=main.FALSE,
                                                          args=[ main ],
                                                          attempts=5 ):
        main.assertReturnString += 'Initial Flow State Passed\n'
    else:
        main.assertReturnString += 'Intial Flow State Failed\n'
        testResult = main.FALSE

    # Check Connectivity
    if utilities.retry( f=scapyCheckConnection,
                        retValue=main.FALSE,
                        args=( main, senderNames, recipientNames ) ):
        main.assertReturnString += 'Initial Connectivity Check Passed\n'
    else:
        main.assertReturnString += 'Initial Connectivity Check Failed\n'
        testResult = main.FALSE

    # Take two links down
    # Take first link down
    if utilities.retry( f=link,
                        retValue=main.FALSE,
                        args=( main, sw1, sw2, "down" ) ):
        main.assertReturnString += 'Link Down Passed\n'
    else:
        main.assertReturnString += 'Link Down Failed\n'
        testResult = main.FALSE

    # Take second link down
    if utilities.retry( f=link,
                        retValue=main.FALSE,
                        args=( main, sw3, sw4, "down" ) ):
        main.assertReturnString += 'Link Down Passed\n'
    else:
        main.assertReturnString += 'Link Down Failed\n'
        testResult = main.FALSE

    # Check intent state
    if utilities.retry( f=checkIntentState,
                        retValue=main.FALSE,
                        attempts=attempts,
                        args=( main, [ intentId ] ),
                        sleep=main.checkIntentSleep ):
        main.assertReturnString += 'Link Down Intent State Passed\n'
    else:
        main.assertReturnString += 'Link Down Intent State Failed\n'
        testResult = main.FALSE

    # Check flows count in each node
    if utilities.retry( f=checkFlowsCount,
                        retValue=main.FALSE,
                        sleep=1,
                        attempts=attempts,
                        args=[ main ] ) and utilities.retry( f=checkFlowsState,
                                                             retValue=main.FALSE,
                                                             sleep=1,
                                                             attempts=attempts,
                                                             args=[ main ] ):
        main.assertReturnString += 'Link Down Flow State Passed\n'
    else:
        main.assertReturnString += 'Link Down Flow State Failed\n'
        testResult = main.FALSE

    # Check OnosTopology
    if utilities.retry( f=checkTopology,
                        retValue=main.FALSE,
                        args=( main, expectedLink1 ) ):
        main.assertReturnString += 'Link Down Topology State Passed\n'
    else:
        main.assertReturnString += 'Link Down Topology State Failed\n'
        testResult = main.FALSE

    # Check Connection
    if utilities.retry( f=scapyCheckConnection,
                        retValue=main.FALSE,
                        args=( main, senderNames, recipientNames ) ):
        main.assertReturnString += 'Link Down Connectivity Check Passed\n'
    else:
        main.assertReturnString += 'Link Down Connectivity Check Failed\n'
        testResult = main.FALSE

    # Take a third link down to isolate one node
    if utilities.retry( f=link,
                        retValue=main.FALSE,
                        args=( main, sw3, sw5, "down" ) ):
        main.assertReturnString += 'Isolation link Down Passed\n'
    else:
        main.assertReturnString += 'Isolation link Down Failed\n'
        testResult = main.FALSE

    if partial:
        # Check intent state
        if utilities.retry( f=checkIntentState,
                            retValue=main.FALSE,
                            args=( main, [ intentId ] ),
                            sleep=main.checkIntentSleep,
                            attempts=attempts ):
            main.assertReturnString += 'Partial failure isolation link Down Intent State Passed\n'
        else:
            main.assertReturnString += 'Partial failure isolation link Down Intent State Failed\n'
            testResult = main.FALSE

        # Check flows count in each node
        if utilities.retry( f=checkFlowsCount,
                            retValue=main.FALSE,
                            args=[ main ],
                            attempts=5 ) and utilities.retry( f=checkFlowsState,
                                                              retValue=main.FALSE,
                                                              args=[ main ],
                                                              attempts=5 ):
            main.assertReturnString += 'Partial failure isolation link Down Flow State Passed\n'
        else:
            main.assertReturnString += 'Partial failure isolation link Down Flow State Failed\n'
            testResult = main.FALSE

        # Check OnosTopology
        if utilities.retry( f=checkTopology,
                            retValue=main.FALSE,
                            args=( main, expectedLink2 ) ):
            main.assertReturnString += 'Partial failure isolation link Down Topology State Passed\n'
        else:
            main.assertReturnString += 'Partial failure isolation link Down Topology State Failed\n'
            testResult = main.FALSE

        # Check Connectivity
        # First check connectivity of any isolated senders to recipients
        if isolatedSenderNames:
            if scapyCheckConnection( main,
                                     isolatedSenderNames,
                                     recipientNames,
                                     None,
                                     None,
                                     None,
                                     None,
                                     main.TRUE ):
                main.assertReturnString += 'Partial failure isolation link Down Connectivity Check Passed\n'
            else:
                main.assertReturnString += 'Partial failure isolation link Down Connectivity Check Failed\n'
                testResult = main.FALSE

        # Next check connectivity of senders to any isolated recipients
        if isolatedRecipientNames:
            if scapyCheckConnection( main,
                                     senderNames,
                                     isolatedRecipientNames,
                                     None,
                                     None,
                                     None,
                                     None,
                                     main.TRUE ):
                main.assertReturnString += 'Partial failure isolation link Down Connectivity Check Passed\n'
            else:
                main.assertReturnString += 'Partial failure isolation link Down Connectivity Check Failed\n'
                testResult = main.FALSE

        # Next check connectivity of connected senders and recipients
        if utilities.retry( f=scapyCheckConnection,
                            retValue=main.FALSE,
                            attempts=attempts,
                            args=( main, connectedSenderNames, connectedRecipientNames ) ):
            main.assertReturnString += 'Partial failure isolation link Down Connectivity Check Passed\n'
        else:
            main.assertReturnString += 'Partial failure isolation link Down Connectivity Check Failed\n'
            testResult = main.FALSE
    else:
        # Check intent state
        if not utilities.retry( f=checkIntentState,
                                retValue=main.TRUE,
                                args=( main, [ intentId ] ),
                                sleep=main.checkIntentSleep,
                                attempts=attempts ):
            main.assertReturnString += 'Isolation link Down Intent State Passed\n'
        else:
            main.assertReturnString += 'Isolation link Down Intent State Failed\n'
            testResult = main.FALSE

        # Check flows count in each node
        if utilities.retry( f=checkFlowsCount,
                            retValue=main.FALSE,
                            args=[ main ],
                            attempts=5 ) and utilities.retry( f=checkFlowsState,
                                                              retValue=main.FALSE,
                                                              args=[ main ],
                                                              attempts=5 ):
            main.assertReturnString += 'Isolation link Down Flow State Passed\n'
        else:
            main.assertReturnString += 'Isolation link Down Flow State Failed\n'
            testResult = main.FALSE

        # Check OnosTopology
        if utilities.retry( f=checkTopology,
                            retValue=main.FALSE,
                            args=( main, expectedLink2 ) ):
            main.assertReturnString += 'Isolation link Down Topology State Passed\n'
        else:
            main.assertReturnString += 'Isolation link Down Topology State Failed\n'
            testResult = main.FALSE

        # Check Connectivity
        # First check connectivity of any isolated senders to recipients
        if isolatedSenderNames:
            if scapyCheckConnection( main,
                                     isolatedSenderNames,
                                     recipientNames,
                                     None,
                                     None,
                                     None,
                                     None,
                                     main.TRUE ):
                main.assertReturnString += 'Isolation link Down Connectivity Check Passed\n'
            else:
                main.assertReturnString += 'Isolation link Down Connectivity Check Failed\n'
                testResult = main.FALSE

        # Next check connectivity of senders to any isolated recipients
        if isolatedRecipientNames:
            if scapyCheckConnection( main,
                                     senderNames,
                                     isolatedRecipientNames,
                                     None,
                                     None,
                                     None,
                                     None,
                                     main.TRUE ):
                main.assertReturnString += 'Isolation link Down Connectivity Check Passed\n'
            else:
                main.assertReturnString += 'Isolation link Down Connectivity Check Failed\n'
                testResult = main.FALSE

        # Next check connectivity of connected senders and recipients
        if utilities.retry( f=scapyCheckConnection,
                            retValue=main.TRUE,
                            args=( main, connectedSenderNames, connectedRecipientNames, None, None, None, None, main.TRUE ) ):
            main.assertReturnString += 'Isolation link Down Connectivity Check Passed\n'
        else:
            main.assertReturnString += 'Isolation link Down Connectivity Check Failed\n'
            testResult = main.FALSE

    # Bring the links back up
    # Bring first link up
    if utilities.retry( f=link,
                        retValue=main.FALSE,
                        args=( main, sw1, sw2, "up" ) ):
        main.assertReturnString += 'Link Up Passed\n'
    else:
        main.assertReturnString += 'Link Up Failed\n'
        testResult = main.FALSE

    # Bring second link up
    if utilities.retry( f=link,
                        retValue=main.FALSE,
                        args=( main, sw3, sw5, "up" ) ):
        main.assertReturnString += 'Link Up Passed\n'
    else:
        main.assertReturnString += 'Link Up Failed\n'
        testResult = main.FALSE

    # Bring third link up
    if utilities.retry( f=link,
                        retValue=main.FALSE,
                        args=( main, sw3, sw4, "up" ) ):
        main.assertReturnString += 'Link Up Passed\n'
    else:
        main.assertReturnString += 'Link Up Failed\n'
        testResult = main.FALSE

    # Wait for reroute
    main.log.info( "Sleeping {} seconds".format( main.rerouteSleep ) )
    time.sleep( main.rerouteSleep )

    # Check Intents
    if utilities.retry( f=checkIntentState,
                        retValue=main.FALSE,
                        attempts=attempts,
                        args=( main, [ intentId ] ),
                        sleep=main.checkIntentHostSleep ):
        main.assertReturnString += 'Link Up Intent State Passed\n'
    else:
        main.assertReturnString += 'Link Up Intent State Failed\n'
        testResult = main.FALSE

    # Check flows count in each node
    if utilities.retry( f=checkFlowsCount,
                        retValue=main.FALSE,
                        args=[ main ],
                        sleep=main.checkFlowCountSleep,
                        attempts=attempts ) and utilities.retry( f=checkFlowsState,
                                                                 retValue=main.FALSE,
                                                                 args=[ main ],
                                                                 sleep=main.checkFlowCountSleep,
                                                                 attempts=attempts ):
        main.assertReturnString += 'Link Up Flow State Passed\n'
    else:
        main.assertReturnString += 'Link Up Flow State Failed\n'
        testResult = main.FALSE

    # Check OnosTopology
    if utilities.retry( f=checkTopology,
                        retValue=main.FALSE,
                        args=( main, main.numLinks ) ):
        main.assertReturnString += 'Link Up Topology State Passed\n'
    else:
        main.assertReturnString += 'Link Up Topology State Failed\n'
        testResult = main.FALSE

    # Check Connection
    if utilities.retry( f=scapyCheckConnection,
                        retValue=main.FALSE,
                        sleep=main.checkConnectionSleep,
                        attempts=attempts,
                        args=( main, senderNames, recipientNames ) ):
        main.assertReturnString += 'Link Up Scapy Packet Received Passed\n'
    else:
        main.assertReturnString += 'Link Up Scapy Packet Recieved Failed\n'
        testResult = main.FALSE

    # Remove all intents
    if utilities.retry( f=removeAllIntents,
                        retValue=main.FALSE,
                        attempts=10,
                        args=( main, [ intentId ] ) ):
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
    appCheck = main.TRUE
    main.log.info( "Activating reactive forwarding app " )
    activateResult = main.CLIs[ 0 ].activateApp( "org.onosproject.fwd" )

    # Wait for forward app activation to propagate
    main.log.info( "Sleeping {} seconds".format( main.fwdSleep ) )
    time.sleep( main.fwdSleep )

    # Check that forwarding is enabled on all nodes
    for i in range( main.numCtrls ):
        appCheck = appCheck and main.CLIs[ i ].appToIDCheck()
        if appCheck != main.TRUE:
            main.log.warn( main.CLIs[ i ].apps() )
            main.log.warn( main.CLIs[ i ].appIDs() )

    # Send pingall in mininet
    main.log.info( "Run Pingall" )
    pingResult = main.Mininet1.pingall( timeout=600 )

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
    hosts = main.topo.getAllHosts( main )  # Get host data from each ONOS node
    hostFails = []  # Reset for each failed attempt

    #  Check for matching hosts on each node
    scapyHostIPs = [ x.hostIp for x in main.scapyHosts if x.hostIp != "0.0.0.0" ]
    for controller in range( main.numCtrls ):
        controllerStr = str( controller + 1 )  # ONOS node number
        # Compare Hosts
        # Load hosts data for controller node
        try:
            if hosts[ controller ]:
                main.log.info( "Hosts discovered" )
            else:
                main.log.error( "Problem discovering hosts" )
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
                    if not set( collections.Counter( scapyHostIPs ) ).issubset(
                            set( collections.Counter( onosHostIPs ) ) ):
                        main.log.warn( "Controller {0} only sees nodes with {1} IPs. It should see all of the following: {2}".format( controllerStr, onosHostIPs, scapyHostIPs ) )
                        hostFails.append( controllerStr )
            else:
                main.log.error( "Hosts returned nothing or an error." )
                hostFails.append( controllerStr )
        except IndexError:
            main.log.error( "Hosts returned nothing, Failed to discover hosts." )
            return main.FALSE

    if hostFails:
        main.log.error( "List of failed ONOS Nodes:" + ', '.join( map( str, hostFails ) ) )
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
        pkt = 'Ether( src="{0}")/ARP( psrc="{1}")'.format( host.hostMac, host.hostIp )
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
                                hostj[ 'locations' ][ 0 ][ 'elementId' ] + '/' + \
                                hostj[ 'locations' ][ 0 ][ 'port' ]
                    main.hostsData[ host ][ 'ipAddresses' ] = hostj[ 'ipAddresses' ]
        return main.TRUE
    except ValueError:
        main.log.error( "ValueError while populating hostsData" )
        return main.FALSE
    except KeyError:
        main.log.error( "KeyError while populating hostsData" )
        return main.FALSE
    except IndexError:
        main.log.error( "IndexError while populating hostsData" )
        return main.FALSE
    except TypeError:
        main.log.error( "TypeError while populating hostsData" )
        return main.FALSE


def checkTopology( main, expectedLink ):
    statusResult = main.TRUE
    # Check onos topology
    main.log.info( itemName + ": Checking ONOS topology " )

    for i in range( main.numCtrls ):
        statusResult = main.CLIs[ i ].checkStatus( main.numSwitch,
                                                   expectedLink ) and statusResult
    if not statusResult:
        main.log.error( itemName + ": Topology mismatch" )
    else:
        main.log.info( itemName + ": Topology match" )
    return statusResult


def checkIntentState( main, intentsId ):
    """
        This function will check intent state to make sure all the intents
        are in INSTALLED state
        Returns main.TRUE or main.FALSE
    """
    intentResult = main.TRUE
    stateCheckResults = []
    for i in range( main.numCtrls ):
        output = main.CLIs[ i ].checkIntentState( intentsId=intentsId )
        stateCheckResults.append( output )
    if all( result == main.TRUE for result in stateCheckResults ):
        main.log.info( itemName + ": Intents state check passed" )
    else:
        main.log.warn( "Intents state check failed" )
        intentResult = main.FALSE
    return intentResult


def checkBandwidthAllocations( main, bandwidth ):
    """
        Compare the given bandwith allocation output to the cli output on each node
        Returns main.TRUE or main.FALSE
    """
    bandwidthResults = []
    for i in range( main.numCtrls ):
        output = main.CLIs[ i ].compareBandwidthAllocations( bandwidth )
        bandwidthResults.append( output )
    if all( result == main.TRUE for result in bandwidthResults ):
        main.log.info( itemName + ": bandwidth check passed" )
        bandwidthResult = main.TRUE
    else:
        main.log.warn( itemName + ": bandwidth check failed" )
        bandwidthResult = main.FALSE
    return bandwidthResult


def checkFlowsState( main ):

    main.log.info( itemName + ": Check flows state" )
    checkFlowsResult = main.CLIs[ 0 ].checkFlowsState( isPENDING=False )
    return checkFlowsResult


def link( main, sw1, sw2, option ):

    # link down
    main.log.info( itemName + ": Bring link " + option + " between " +
                       sw1 + " and " + sw2 )
    linkResult = main.Mininet1.link( end1=sw1, end2=sw2, option=option )
    return linkResult


def scapyCheckConnection( main,
                          senders,
                          recipients,
                          vlanId=None,
                          useTCP=False,
                          packet=None,
                          packetFilter=None,
                          expectFailure=False ):
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
    if useTCP:
        packetFilter += ' ip proto \\tcp tcp port {}'.format( main.params[ 'SDNIP' ][ 'dstPort' ] )
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

            if vlanId:
                recipientComp.startFilter( pktFilter=( "vlan {}".format( vlanId ) + " && " + packetFilter.format( senderComp.hostMac ) ) )
            else:
                recipientComp.startFilter( pktFilter=packetFilter.format( senderComp.hostMac ) )

            if not packet:
                if vlanId:
                    pkt = 'Ether( src="{0}", dst="{2}" )/Dot1Q(vlan={4})/IP( src="{1}", dst="{3}" )'.format(
                        senderComp.hostMac,
                        senderComp.hostIp,
                        recipientComp.hostMac,
                        recipientComp.hostIp,
                        vlanId )
                else:
                    pkt = 'Ether( src="{0}", dst="{2}" )/IP( src="{1}", dst="{3}" )'.format(
                        senderComp.hostMac,
                        senderComp.hostIp,
                        recipientComp.hostMac,
                        recipientComp.hostIp )
            else:
                pkt = packet
            if vlanId:
                senderComp.sendPacket( iface=( "{0}-eth0.{1}".format( sender, vlanId ) ), packet = pkt )
            else:
                senderComp.sendPacket( packet=pkt )

            if recipientComp.checkFilter( timeout ):
                if expectFailure:
                    main.log.error( "Packet from {0} successfully received by {1} when it should not have been".format( sender, recipient ) )
                    connectionsFunctional = main.FALSE
                else:
                    main.log.info( "Packet from {0} successfully received by {1}".format( sender, recipient ) )
                    connectionsFunctional = main.TRUE
            else:
                recipientComp.killFilter()
                if expectFailure:
                    main.log.info( "As expected, packet from {0} was not received by {1}".format( sender, recipient ) )
                else:
                    main.log.error( "Packet from {0} was not received by {1}".format( sender, recipient ) )
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

    main.log.info( "Sleeping {} seconds".format( main.removeIntentSleep ) )
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
        if all( flows == flowsCount[ 0 ] for flows in flowsCount ):
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
    except( AttributeError, TypeError ):
        main.log.exception( "checkLeaderChange: Object not as expected" )
        return main.FALSE
    except Exception:
        main.log.exception( "checkLeaderChange: Uncaught exception!" )
        main.cleanup()
        main.exit()
    main.log.info( "Checking Intent Paritions for Change in Leadership" )
    mismatch = False
    for dict1 in leaders1:
        if "intent" in dict1.get( "topic", [] ):
            for dict2 in leaders2:
                if dict1.get( "topic", 0 ) == dict2.get( "topic", 0 ) and\
                        dict1.get( "leader", 0 ) != dict2.get( "leader", 0 ):
                    mismatch = True
                    main.log.error( "%s changed leader from %s to %s",
                                    dict1.get( "topic", "no-topic" ),
                                    dict1.get( "leader", "no-leader" ),
                                    dict2.get( "leader", "no-leader" ) )
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


def flowDuration( main ):
    """
        Check age of flows to see if flows are being overwritten
    """
    main.log.info( "Getting current flow durations" )
    flowsJson1 = main.CLIs[ 0 ].flows( noCore=True )
    try:
        flowsJson1 = json.loads( flowsJson1 )
    except ValueError:
        main.log.error( "Unable to read flows" )
        return main.FALSE
    flowLife = []
    waitFlowLife = []
    for device in flowsJson1:
        if device.get( 'flowcount', 0 ) > 0:
            for i in range( device[ 'flowCount' ] ):
                flowLife.append( device[ 'flows' ][ i ][ 'life' ] )
    main.log.info( "Sleeping for {} seconds".format( main.flowDurationSleep ) )
    time.sleep( main.flowDurationSleep )
    main.log.info( "Getting new flow durations" )
    flowsJson2 = main.CLIs[ 0 ].flows( noCore=True )
    try:
        flowsJson2 = json.loads( flowsJson2 )
    except ValueError:
        main.log.error( "Unable to read flows" )
        return main.FALSE
    for device in flowsJson2:
        if device.get( 'flowcount', 0 ) > 0:
            for i in range( device[ 'flowCount' ] ):
                waitFlowLife.append( device[ 'flows' ][ i ][ 'life' ] )
    main.log.info( "Determining whether flows where overwritten" )
    if len( flowLife ) == len( waitFlowLife ):
        for i in range( len( flowLife ) ):
            if waitFlowLife[ i ] - flowLife[ i ] < main.flowDurationSleep:
                return main.FALSE
    else:
        return main.FALSE
    return main.TRUE


def EncapsulatedIntentCheck( main, tag="" ):
    """
        Check encapsulated intents
        tag: encapsulation tag ( e.g. VLAN, MPLS )

        Getting added flows
        Check tags on each flows
        If each direction has push or pop, passed
        else failed

    """
    HostJson = []
    Jflows = main.CLIs[ 0 ].flows( noCore=True )
    try:
        Jflows = json.loads( Jflows )
    except ValueError:
        main.log.error( "Unable to read flows" )
        return main.FALSE

    for flow in Jflows:
        if len( flow[ "flows" ] ) != 0:
            HostJson.append( flow[ "flows" ] )

    totalflows = len( HostJson[ 0 ] )

    pop = 0
    push = 0

    PopTag = tag + "_POP"
    PushTag = tag + "_PUSH"

    for EachHostJson in HostJson:
        for i in range( totalflows ):
            if EachHostJson[ i ][ "treatment" ][ "instructions" ][ 0 ][ "subtype" ] == PopTag:
                pop += 1
            elif EachHostJson[ i ][ "treatment" ][ "instructions" ][ 0 ][ "subtype" ] == PushTag:
                push += 1

    if pop == totalflows and push == totalflows:
        return main.TRUE
    else:
        return main.FALSE


def ProtectedIntentCheck( main ):
    intent = main.CLIs[ 0 ].intents( jsonFormat=False )
    if "Protection" in intent:
        return main.TRUE
    return main.FALSE
