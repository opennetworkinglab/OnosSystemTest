"""
Copyright 2018 Open Networking Foundation ( ONF )

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    ( at your option ) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.
"""
import json
import re

ONOS_GROUP_ID = 'org.onosproject'
SR_APP = 'segmentrouting'
DHCP_APP = 'dhcprelay'
DHCP_APP_ID = ONOS_GROUP_ID + '.' + DHCP_APP

# Translate configuration JSON file from BMv2 driver to OFDPA-OVS driver.
def bmv2ToOfdpa( main, cfgFile="", rolesRE=r'spine|leaf' ):
    didRE = r"device:(?P<swType>bmv2|tofino):(?P<swRole>" + rolesRE + ")(?P<swNum>[1-9][0-9]*)(/(?P<portNum>[0-9]+))?"
    if not cfgFile:
        cfgFile = "%s%s.json" % ( main.configPath + main.forJson,
                                  main.cfgName )
    with open( cfgFile ) as cfg:
        netcfg = json.load( cfg )

    if 'ports' in netcfg.keys():
        for port in netcfg[ 'ports' ].keys():
            searchObj = re.search( didRE, port )
            if searchObj:
                new_port = 'of:' + searchObj.group( 'swNum' ).zfill( 16 ) + '/' + searchObj.group( 'portNum' )
                netcfg[ 'ports' ][ new_port ] = netcfg[ 'ports' ].pop( port )

    if 'hosts' in netcfg.keys():
        for ( host, hostCfg ) in netcfg[ 'hosts' ].items():
            if type( hostCfg[ 'basic' ][ 'locations' ] ) is list:
                new_locations = []
                for location in hostCfg[ 'basic' ][ 'locations' ]:
                    searchObj = re.search( didRE, location )
                    if searchObj:
                        new_locations.append( 'of:' + searchObj.group( 'swNum' ).zfill( 16 ) + '/' + searchObj.group( 'portNum' ) )
                    else:
                        new_locations.append( location )
                netcfg[ 'hosts' ][ host ][ 'basic' ][ 'locations' ] = new_locations
            else:
                location = hostCfg[ 'basic' ][ 'locations' ]
                searchObj = re.search( didRE, location )
                if searchObj:
                    new_location = 'of:' + searchObj.group( 'swNum' ).zfill( 16 ) + '/' + searchObj.group( 'portNum' )
                    netcfg[ 'hosts' ][ host ][ 'basic' ][ 'locations' ] = new_location

    if 'devices' in netcfg.keys():
        for device in netcfg[ 'devices' ].keys():
            searchObj = re.search( didRE, device )
            new_device = device
            if searchObj:
                new_device = 'of:' + searchObj.group( 'swNum' ).zfill( 16 )
                netcfg[ 'devices' ][ new_device ] = netcfg[ 'devices' ].pop( device )
            if 'pairDeviceId' in netcfg[ 'devices' ][ new_device ][ SR_APP ].keys():
                searchObj = re.search( didRE, netcfg[ 'devices' ][ new_device ][ SR_APP ][ 'pairDeviceId' ])
                if searchObj:
                    netcfg[ 'devices' ][ new_device ][ SR_APP ][ 'pairDeviceId' ] = 'of:' + \
                                                                                    searchObj.group( 'swNum' ).zfill( 16 )
            if 'basic' in netcfg[ 'devices' ][ new_device ].keys():
                netcfg[ 'devices' ][ new_device ][ 'basic' ].update( { 'driver': 'ofdpa-ovs' } )

    if 'apps' in netcfg.keys():
        if DHCP_APP_ID in netcfg[ 'apps' ].keys():
            for i, dhcpcfg in enumerate( netcfg[ 'apps' ][ DHCP_APP_ID ][ 'default' ] ):
                if 'dhcpServerConnectPoint' in dhcpcfg.keys():
                    searchObj = re.search( didRE, dhcpcfg[ 'dhcpServerConnectPoint' ] )
                    if searchObj:
                        netcfg[ 'apps' ][ DHCP_APP_ID ][ 'default' ][ i ][ 'dhcpServerConnectPoint' ] = \
                            'of:' + searchObj.group( 'swNum' ).zfill(16) + '/' + searchObj.group( 'portNum' )

    if 'xconnects' in netcfg.keys():
        new_xconnects = []
        for xconnect in netcfg[ 'xconnects' ]:
            searchObj = re.search( didRE, xconnect.get( "deviceId" ) )
            if searchObj:
                new_device = 'of:' + searchObj.group( 'swNum' ).zfill( 16 )
                xconnect[ 'deviceId' ] = new_device
            new_xconnects.append( xconnect )
        netcfg[ 'xconnects' ] = new_xconnects

    with open( cfgFile, 'w' ) as cfg:
        cfg.write( json.dumps( netcfg, indent=4, separators=( ',', ':' ), sort_keys=True ) )

# Translate configuration JSON file from OFDPA-OVS driver to BMv2 driver.
def ofdpaToBmv2( main, switchPrefix="bmv2", cfgFile="", roleMap={r'0*[1-9]([0-9]){2}': 'spine', r'0{15}[1-9]': "leaf"} ):
    didRE = r"of:0*(?P<swNum>[1-9][0-9]*)(/(?P<portNum>[0-9]+))?"
    if switchPrefix is None:
        switchPrefix = ''
    else:
        switchPrefix += ':'
    if not cfgFile:
        cfgFile = "%s%s.json" % ( main.configPath + main.forJson,
                                  main.cfgName )
    with open( cfgFile ) as cfg:
        netcfg = json.load( cfg )

    if 'ports' in netcfg.keys():
        for port in netcfg[ 'ports' ].keys():
            searchObj = re.search( didRE, port )
            if searchObj:
                # search  for a match between keys of roleMap and device id and set role to value of key
                role = "leaf"
                for roleRE, roleValue in roleMap.items():
                    roleMatch = re.search( roleRE, searchObj.group( 'swNum' ) )
                    if roleMatch:
                        role = roleValue
                        break
                new_port = 'device:' + switchPrefix + role + searchObj.group( 'swNum' ) + '/' + searchObj.group( 'portNum' )
                netcfg[ 'ports' ][ new_port ] = netcfg[ 'ports' ].pop( port )

    if 'hosts' in netcfg.keys():
        for ( host, hostCfg ) in netcfg[ 'hosts' ].items():
            if type( hostCfg[ 'basic' ][ 'locations' ] ) is list:
                new_locations = []
                for location in hostCfg[ 'basic' ][ 'locations' ]:
                    searchObj = re.search( didRE, location )
                    if searchObj:
                        # search  for a match between keys of roleMap and device id and set role to value of key
                        role = "leaf"
                        for roleRE, roleValue in roleMap.items():
                            roleMatch = re.search( roleRE, searchObj.group( 'swNum' ) )
                            if roleMatch:
                                role = roleValue
                                break
                        new_locations.append( 'device:' + switchPrefix + role + searchObj.group( 'swNum' ) + '/' + searchObj.group( 'portNum' ) )
                    else:
                        new_locations.append( location )
                netcfg[ 'hosts' ][ host ][ 'basic' ][ 'locations' ] = new_locations
            else:
                location = hostCfg[ 'basic' ][ 'locations' ]
                searchObj = re.search( didRE, location )
                if searchObj:
                    # search  for a match between keys of roleMap and device id and set role to value of key
                    role = "leaf"
                    for roleRE, roleValue in roleMap.items():
                        roleMatch = re.search( roleRE, searchObj.group( 'swNum' ) )
                        if roleMatch:
                            role = roleValue
                            break
                    new_location = 'device:' + switchPrefix + role + searchObj.group( 'swNum' ) + '/' + searchObj.group( 'portNum' )
                    netcfg[ 'hosts' ][ host ][ 'basic' ][ 'locations' ] = new_location

    if 'devices' in netcfg.keys():
        for device in netcfg[ 'devices' ].keys():
            searchObj = re.search( didRE, device )
            new_device = device
            if searchObj:
                #TODO This or roleMap? maybe use this to populate role Map?
                isLeaf = netcfg[ 'devices' ][ device ][ SR_APP ][ 'isEdgeRouter' ]
                if isLeaf is True:
                    new_device = 'device:' + switchPrefix + 'leaf' + searchObj.group( 'swNum' )
                else:
                    new_device = 'device:' + switchPrefix + 'spine' + searchObj.group( 'swNum' )
                netcfg[ 'devices' ][ new_device ] = netcfg[ 'devices' ].pop( device )
            if 'pairDeviceId' in netcfg[ 'devices' ][ new_device ][ SR_APP ].keys():
                searchObj = re.search( didRE,
                                       netcfg[ 'devices' ][ new_device ][ SR_APP ][ 'pairDeviceId' ])
                if searchObj:
                    # search  for a match between keys of roleMap and device id and set role to value of key
                    role = "leaf"
                    for roleRE, roleValue in roleMap.items():
                        roleMatch = re.search( roleRE, searchObj.group( 'swNum' ) )
                        if roleMatch:
                            role = roleValue
                            break
                    netcfg[ 'devices' ][ new_device ][ SR_APP ][ 'pairDeviceId' ] = 'device:' + switchPrefix + role + \
                                                                                    searchObj.group( 'swNum' )
            if 'basic' in netcfg[ 'devices' ][ new_device ].keys():
                if 'driver' in netcfg[ 'devices' ][ new_device ][ 'basic' ].keys():
                    del netcfg[ 'devices' ][ new_device ][ 'basic' ][ 'driver' ]

    if 'apps' in netcfg.keys():
        if DHCP_APP_ID in netcfg[ 'apps' ].keys():
            for i, dhcpcfg in enumerate( netcfg[ 'apps' ][ DHCP_APP_ID ][ 'default' ] ):
                if 'dhcpServerConnectPoint' in dhcpcfg.keys():
                    searchObj = re.search( didRE,
                                           dhcpcfg[ 'dhcpServerConnectPoint' ] )
                    if searchObj:
                        # search  for a match between keys of roleMap and device id and set role to value of key
                        role = "leaf"
                        for roleRE, roleValue in roleMap.items():
                            roleMatch = re.search( roleRE, searchObj.group( 'swNum' ) )
                            if roleMatch:
                                role = roleValue
                                break
                        netcfg[ 'apps' ][ DHCP_APP_ID ][ 'default' ][ i ][ 'dhcpServerConnectPoint' ] = \
                            'device:' + switchPrefix + role + searchObj.group( 'swNum' ) + '/' + searchObj.group( 'portNum' )

    if 'xconnects' in netcfg.keys():
        new_xconnects = []
        for xconnect in netcfg[ 'xconnects' ]:
            searchObj = re.search( didRE, xconnect.get( "deviceId" ) )
            if searchObj:
                # search  for a match between keys of roleMap and device id and set role to value of key
                role = "leaf"
                for roleRE, roleValue in roleMap.items():
                    roleMatch = re.search( roleRE, searchObj.group( 'swNum' ) )
                    if roleMatch:
                        role = roleValue
                        break
                new_device = 'device:' + switchPrefix + role + searchObj.group( 'swNum' )
                xconnect[ 'deviceId' ] = new_device
            new_xconnects.append( xconnect )
        netcfg[ 'xconnects' ] = new_xconnects

    with open( cfgFile, 'w' ) as cfg:
        cfg.write( json.dumps( netcfg, indent=4, separators=( ',', ':' ), sort_keys=True ) )
