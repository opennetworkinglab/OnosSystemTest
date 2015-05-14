"""
    Wrapper functions for FuncIntent
    This functions include Onosclidriver and Mininetclidriver driver functions
"""
def __init__( self ):
    self.default = ''

def addHostIntent( main, item ):
    """
        Add host intents
    """
    import time
    stepResult = main.TRUE
    global itemName
    itemName = item[ 'name' ]
    h1Name = item[ 'host1' ][ 'name' ]
    h2Name = item[ 'host2' ][ 'name' ]
    h1Mac = item[ 'host1' ][ 'MAC' ]
    h2Mac = item[ 'host2' ][ 'MAC' ]
    h1Id = item[ 'host1' ][ 'id']
    h2Id = item[ 'host2' ][ 'id']
    sw1 = item[ 'link' ][ 'switch1' ]
    sw2 = item[ 'link' ][ 'switch2' ]
    expectLink = item[ 'link' ][ 'expect' ]
    intentsId = []
    pingResult = main.TRUE
    intentResult = main.TRUE
    flowResult = main.TRUE
    topoResult = main.TRUE
    linkDownResult = main.TRUE
    linkUpResult = main.TRUE

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
    intent2 = main.CLIs[ 0 ].addHostIntent( hostIdOne=h2Id,
                                           hostIdTwo=h1Id )
    intentsId.append( intent2 )

    # Check intents state
    time.sleep( 50 )
    intentResult = checkIntentState( main, intentsId )

    # Verify flows
    checkFlowsState( main )

    # Ping hosts
    pingHost( main, h1Name, h2Name )
    # Ping hosts again...
    pingResult = pingHost( main, h1Name, h2Name )
    time.sleep( 5 )

    # link down
    link( main, sw1, sw2, "down" )
    intentResult = intentResult and checkIntentState( main, intentsId )

    # Verify flows
    checkFlowsState( main )

    # Check OnosTopology
    topoResult = checkTopology( main, expectLink )

    # Ping hosts
    pingResult = pingResult and pingHost( main, h1Name, h2Name )

    intentResult = checkIntentState( main, intentsId )

    # link up
    link( main, sw1, sw2, "up" )
    time.sleep( 5 )

    # Verify flows
    checkFlowsState( main )

    # Check OnosTopology
    topoResult = checkTopology( main, expectLink )

    # Ping hosts
    pingResult = pingResult and pingHost( main, h1Name, h2Name )

    # Remove intents
    for intent in intentsId:
        main.CLIs[ 0 ].removeIntent( intentId=intent, purge=True )

    print main.CLIs[ 0 ].intents()
    stepResult = pingResult and linkDownResult and linkUpResult \
                 and intentResult

    return stepResult

def addPointIntent( main, item ):
    """
        Add Point intents
    """
    import time
    stepResult = main.TRUE
    global itemName
    itemName = item[ 'name' ]
    h1Name = item[ 'host1' ][ 'name' ]
    h2Name = item[ 'host2' ][ 'name' ]
    ingressDevice = item[ 'ingressDevice' ]
    egressDevice = item[ 'egressDevice' ]
    option = item[ 'option' ]
    sw1 = item[ 'link' ][ 'switch1' ]
    sw2 = item[ 'link' ][ 'switch2' ]
    expectLink = item[ 'link' ][ 'expect' ]
    intentsId = []
    
    # Assign options to variables
    ingressPort = item.get( 'ingressPort' )
    egressPort = item.get( 'egressPort' )
    ethType = option.get( 'ethType' )
    ethSrc = option.get( 'ethSrc' )
    ethDst = option.get( 'ethDst' )
    bandwidth = option.get( 'bandwidth' )
    lambdaAlloc = option.get( 'lambdaAlloc' )
    ipProto = option.get( 'ipProto' )
    ipSrc = option.get( 'ipSrc' )
    ipDst = option.get( 'ipDst' )
    tcpSrc = option.get( 'tcpSrc' )
    tcpDst = option.get( 'tcpDst' )

    if ingressPort == None:
        ingressPort = ""
    if egressPort == None:
        egressPort = ""
    if ethType == None:
        ethType = ""
    if ethSrc == None:
        ethSrc = ""
    if ethDst == None:
        ethDst = ""
    if bandwidth == None:
        bandwidth = ""
    if lambdaAlloc == None:
        lambdaAlloc = False
    if ipProto == None:
        ipProto = ""
    if ipSrc == None:
        ipSrc = ""
    if ipDst == None:
        ipDst = ""
    if tcpSrc == None:
        tcpSrc = ""
    if tcpDst == None:
        tcpDst = ""

    """
    print 'ethType: ', ethType
    print 'ethSrc: ', ethSrc
    print 'ethDst: ', ethDst
    print 'bandwidth', bandwidth
    print 'lambdaAlloc: ', lambdaAlloc
    print 'ipProto: ', ipProto
    print 'ipSrc: ', ipSrc
    print 'ipDst:', ipDst
    print 'tcpSrc: ', tcpSrc
    print 'tcpDst: ', tcpDst
    """
    addedOption = ""
    for i in range( len( option ) ):
        addedOption = addedOption + option.keys()[ i ] + " = " + \
                      option.values()[ i ] + "\n"
    main.log.info( itemName + ": Printing added options...\n" + addedOption )

    pingResult = main.TRUE
    intentResult = main.TRUE
    flowResult = main.TRUE
    topoResult = main.TRUE
    linkDownResult = main.TRUE
    linkUpResult = main.TRUE

    # Adding bidirectional point  intents
    main.log.info( itemName + ": Adding host intents" )
    intent1 = main.CLIs[ 0 ].addPointIntent( ingressDevice=ingressDevice,
                                             egressDevice=egressDevice,
                                             portIngress=ingressPort,
                                             portEgress=egressPort,
                                             ethType=ethType,
                                             ethSrc=ethSrc,
                                             ethDst=ethDst,
                                             bandwidth=bandwidth,
                                             lambdaAlloc=lambdaAlloc,
                                             ipProto=ipProto,
                                             ipSrc=ipSrc,
                                             ipDst=ipDst,
                                             tcpSrc=tcpSrc,
                                             tcpDst=tcpDst )

    intentsId.append( intent1 )
    time.sleep( 5 )
    intent2 = main.CLIs[ 0 ].addPointIntent( ingressDevice=egressDevice,
                                             egressDevice=ingressDevice,
                                             portIngress=egressPort,
                                             portEgress=ingressPort,
                                             ethType=ethType,
                                             ethSrc=ethDst,
                                             ethDst=ethSrc,
                                             bandwidth=bandwidth,
                                             lambdaAlloc=lambdaAlloc,
                                             ipProto=ipProto,
                                             ipSrc=ipDst,
                                             ipDst=ipSrc,
                                             tcpSrc=tcpDst,
                                             tcpDst=tcpSrc )
    intentsId.append( intent2 )

    # Check intents state
    time.sleep( 50 )
    intentResult = checkIntentState( main, intentsId )

    # Verify flows
    checkFlowsState( main )

    # Ping hosts
    pingHost( main, h1Name, h2Name )
    # Ping hosts again...
    pingResult = pingHost( main, h1Name, h2Name )
    time.sleep( 5 )

    # link down
    link( main, sw1, sw2, "down" )
    intentResult = intentResult and checkIntentState( main, intentsId )

    # Verify flows
    checkFlowsState( main )

    # Check OnosTopology
    topoResult = checkTopology( main, expectLink )

    # Ping hosts
    pingResult = pingResult and pingHost( main, h1Name, h2Name )

    intentResult = checkIntentState( main, intentsId )

    # link up
    link( main, sw1, sw2, "up" )
    time.sleep( 5 )

    # Verify flows
    checkFlowsState( main )

    # Check OnosTopology
    topoResult = checkTopology( main, expectLink )

    # Ping hosts
    pingResult = pingResult and pingHost( main, h1Name, h2Name )

    # Remove intents
    for intent in intentsId:
        main.CLIs[ 0 ].removeIntent( intentId=intent, purge=True )

    print main.CLIs[ 0 ].intents()
    stepResult = pingResult and linkDownResult and linkUpResult \
                 and intentResult

    return stepResult

def link( main, sw1, sw2, option):

    # link down
    main.log.info( itemName + ": Bring link " + option + "between " +
                   sw1 + " and " + sw2 )
    main.Mininet1.link( end1=sw1, end2=sw2, option=option )

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

def checkItem( item ):
    """
        Checks the dictionary
    """

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

def printMsg( main, h1Name, h2Name ):
    main.log.info("PINGING HOST INSIDE printMSG")
    pingHost( main, itemName, h1Name, h2Name )
    print 'lala'

