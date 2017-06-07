"""
Functions for the vpls tests
"""
import time
import json


def sanitizeConfig( config ):
    """
    Take a python json object for vpls config and normalize it.
    Things it does:
        Converts all strings to the same format
        Make sure each network has an encapsulation key:value
        Makes sure encapsulation type is all uppercase
        Make sure an empty list of interfaces is formated consistently
        Sorts the list of interfaces
        Sorts the list of networks
    """
    # Convert to same string formats
    config = json.loads( json.dumps( config ) )
    for network in config:
        encap = network.get( 'encapsulation', None )
        if encap is None:
            encap = "NONE"
        network[ 'encapsulation' ] = encap.upper()
        ifaces = network.get( 'interfaces' )
        if ifaces == [ '' ]:
            ifaces = []
        else:
            ifaces = sorted( ifaces )
            network[ 'interfaces' ] = ifaces
    config = sorted( config, key=lambda k: k[ 'name' ] )
    return config


def verify( main ):
    """
    Runs some tests to verify the vpls configurations.
        - Compare sent vpls network configuration to what is stored in each:
            - ONOS network configuration
            - ONOS VPLS application configuration
        - Ping between each pair of hosts to check connectivity

    NOTE: This requires the expected/sent network config json for the vpls
          application be stored in main.vplsConfig
    """
    # Variables
    app = main.params[ 'vpls' ][ 'name' ]
    pprint = main.ONOSrest1.pprint
    SLEEP = int( main.params[ 'SLEEP' ][ 'netcfg' ] )

    main.step( "Check network configurations for vpls application" )
    clusterResult = True
    for node in main.RESTs:
        result = False
        getVPLS = utilities.retry( f=node.getNetCfg,
                                   retValue=False,
                                   kwargs={"subjectClass":"apps", "subjectKey":app},
                                   sleep=SLEEP )
        onosCfg = json.loads( getVPLS ).get( 'vpls' ).get( 'vplsList' )
        onosCfg = pprint( sanitizeConfig( onosCfg ) )
        sentCfg = pprint( sanitizeConfig( main.vplsConfig ) )
        result = onosCfg == sentCfg
        if result:
            main.log.info( "ONOS NetCfg matches what was sent" )
        else:
            clusterResult = False
            main.log.error( "ONOS NetCfg doesn't match what was sent" )
            main.log.debug( "ONOS config: {}".format( onosCfg ) )
            main.log.debug( "Sent config: {}".format( sentCfg ) )
    utilities.assert_equals( expect=True,
                             actual=clusterResult,
                             onpass="Net Cfg added for vpls",
                             onfail="Net Cfg not added for vpls" )

    main.step( "Check vpls app configurations" )
    clusterResult = True
    for node in main.CLIs:
        result = False
        #TODO Read from vpls show and match to pushed json
        vpls = node.parseVplsShow()
        parsedVpls = pprint( sanitizeConfig( vpls ) )
        sentVpls = pprint( sanitizeConfig( main.vplsConfig ) )
        result = parsedVpls == sentVpls
        if result:
            main.log.info( "VPLS config matches sent NetCfg" )
        else:
            clusterResult = False
            main.log.error( "VPLS config doesn't match sent NetCfg" )
            main.log.debug( "ONOS config: {}".format( parsedVpls ) )
            main.log.debug( "Sent config: {}".format( sentVpls ) )
    utilities.assert_equals( expect=True,
                             actual=clusterResult,
                             onpass="VPLS successfully configured",
                             onfail="VPLS not configured correctly" )

    # FIXME This doesn't work, some will be withdrawn if interfaces are removed
    # TODO: if encapsulation is set, look for that
    # TODO: can we look at the intent keys?
    """
    main.step( "Check intent states" )
    # Print the intent states
    intents = main.CLIs[ 0 ].intents()
    count = 0
    while count <= 5:
        installedCheck = True
        try:
            for intent in json.loads( intents ):
                state = intent.get( 'state', None )
                if "INSTALLED" not in state:
                    installedCheck = False
        except ( ValueError, TypeError ):
            main.log.exception( "Error parsing intents" )
        if installedCheck:
            break
        count += 1
    utilities.assert_equals( expect=True,
                             actual=installedCheck ,
                             onpass="All Intents in installed state",
                             onfail="Not all Intents in installed state" )
    """
    main.step( "Check connectivity" )
    connectivityCheck = True
    hosts = int( main.params[ 'vpls' ][ 'hosts' ] )
    networks = []
    for network in main.vplsConfig:
        nodes = network.get( 'interfaces', None )
        if nodes:
            networks.append( nodes )
    for i in range( 1, hosts + 1 ):
        src = "h" + str( i )
        for j in range( 1, hosts + 1 ):
            if j == i:
                continue
            dst = "h" + str( j )
            pingResult = main.Mininet1.pingHost( SRC=src, TARGET=dst )
            expected = main.FALSE
            for network in networks:
                if src in network and dst in network:
                    expected = main.TRUE
                    break
            if pingResult != expected:
                connectivityCheck = False
                main.log.error( "%s <-> %s: %s; Expected: %s" %
                               ( src, dst, pingResult, expected ) )
    utilities.assert_equals( expect=True,
                             actual=connectivityCheck,
                             onpass="Connectivity is as expected",
                             onfail="Connectivity is not as expected" )
