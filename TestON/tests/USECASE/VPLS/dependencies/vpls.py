"""
Copyright 2016 Open Networking Foundation (ONF)

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.
"""

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
    pprint = main.Cluster.active( 0 ).REST.pprint
    SLEEP = int( main.params[ 'SLEEP' ][ 'netcfg' ] )

    main.step( "Check network configurations for vpls application" )
    clusterResult = True
    for ctrl in main.Cluster.active():
        result = False
        getVPLS = utilities.retry( f=ctrl.REST.getNetCfg,
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
    for ctrl in main.Cluster.active():
        result = False
        #TODO Read from vpls show and match to pushed json
        vpls = ctrl.CLI.parseVplsShow()
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

    checkIntentState( main )

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



# TODO: if encapsulation is set, look for that
# TODO: can we look at the intent keys?

def checkIntentState( main , bl=[] ):
    # Print the intent states
    intents = main.Cluster.active( 0 ).CLI.intents()
    count = 0
    while count <= 5:
        installedCheck = True
        try:
            i = 1
            for intent in json.loads( intents ):
                state = intent.get( 'state', None )
                if "INSTALLED" not in state or ( "WITHDRAWN" not in state and "h" + str( i ) in bl ):
                    installedCheck = False
                i += 1
        except ( ValueError, TypeError ):
            main.log.exception( "Error parsing intents" )
        if installedCheck:
            break
        count += 1
    return installedCheck


def getVplsHashtable( main, bl=[] ):
    """
    Returns a hashtable of vpls to hosts
    """
    result = {}
    vplsConfig = main.vplsConfig
    for v in vplsConfig:
        interfaces = v[ 'interfaces' ][:]
        for i in bl:
            if i in interfaces:
                interfaces.remove( i )
        result[ v[ 'name' ] ] = interfaces
    return result


def testConnectivityVpls( main, blacklist=[], isNodeUp=True ):

    # Can't do intent check when onos node is stopped/killed yet
    if isNodeUp:
        main.step( "Check intent states" )
        intentsCheck = utilities.retry( f=checkIntentState,
                                        retValue=False,
                                        args=( main, blacklist ),
                                        sleep=main.timeSleep,
                                        attempts=main.numAttempts )

        utilities.assert_equals( expect=True,
                                 actual=intentsCheck,
                                 onpass="All Intents in installed state",
                                 onfail="Not all Intents in installed state" )

    main.step( "Testing connectivity..." )

    vplsHashtable = getVplsHashtable( main, blacklist )
    main.log.debug( "vplsHashtable: " + str( vplsHashtable ) )
    result = True
    for key in vplsHashtable:
        pingResult = utilities.retry( f=main.Mininet1.pingallHosts,
                                      retValue=False,
                                      args=( vplsHashtable[ key ], ),
                                      sleep=main.timeSleep,
                                      attempts=main.numAttempts )
        result = result and pingResult

    utilities.assert_equals( expect=main.TRUE, actual=result,
                             onpass="Connectivity succeeded.",
                             onfail="Connectivity failed." )
    return result


def compareApps( main ):
    result = True
    first = None
    for ctrl in main.Cluster.active():
        currentApps = ctrl.CLI.apps( summary=True, active=True )
        if not result:
            first = currentApps
        else:
            result = result and ( currentApps == first )
    return result
