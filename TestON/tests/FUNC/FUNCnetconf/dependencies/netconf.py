"""
Copyright 2016 Open Networking Foundation ( ONF )

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


    Wrapper functions for FUNCnetconf
    This functions include Onosclidriver and Mininetclidriver driver functions
    Author: Jeremy Songster, jeremy@onlab.us
"""
import time
import json
import os


def __init__( self ):
    self.default = ''


def startApp( main ):
    """
        This function starts the netconf app in all onos nodes and ensures that
        the OF-Config server is running on the node to be configured
    """
    startResult = main.FALSE
    startResult = main.Cluster.active( 0 ).REST.activateApp( appName="org.onosproject.netconf" )
    return startResult


def startOFC( main ):
    """
        This function uses pexpect pxssh class to activate the ofc-server daemon on OC2
    """
    startResult = main.FALSE
    try:
        main.configDeviceIp = main.ONOSbench.getIpAddr( iface=main.iface )
        main.log.info( "Device to be configured: " + str( main.configDeviceIp ) )
        main.ONOSbench.handle.sendline( "sudo ofc-server" )
        main.ONOSbench.handle.expect( "\$" )
        startResult = main.TRUE
        return startResult
    except pexpect.ExceptionPexpect as e:
        main.log.exception( self.name + ": Pexpect exception found: " )
        main.log.error( self.name + ":    " + self.handle.before )
        main.cleanAndExit()


def createConfig( main ):
    """
        This function writes a configuration file that can later be sent to the
        REST API to configure a device.
        The controller device is assumed to be OC1
        The device to be configured is assumed to be OC2
    """
    createCfgResult = main.FALSE
    # TODO, add ability to set Manufacturer, Hardware and Software versions
    main.cfgJson = '{' \
                        '"devices": {' \
                            '"netconf:' + main.configDeviceIp + ':' + main.configDevicePort + '": {' \
                                '"netconf": {' \
                                    '"ip": "' + main.configDeviceIp + '",' \
                                    '"port": ' + main.configPort + ',' \
                                    '"username": ' + main.configName + ',' \
                                    '"password": ' + main.configPass + \
                                '},' \
                                '"basic": {' \
                                    '"driver": "' + main.configDriver + '"' \
                                '}' \
                            '}' \
                        '}' \
                    '}'
    try:
        file = open( os.path.dirname( main.testFile ) + "/dependencies/netconfConfig.json", 'w' )
        # These lines can cause errors during the configuration process because
        # they cause the json string to turn into an unordered dictionary before
        # sorting it alphabetically which can cause the driver type to not be
        # configured.
        # main.cfgJson = json.loads( main.cfgJson )
        # main.cfgJson = json.dumps( main.cfgJson, sort_keys=True,
        #                        indent=4, separators=( ',', ': ' ) )
        print main.cfgJson
        file.write( main.cfgJson )
        if file:
            createCfgResult = main.TRUE
            file.close()
            return createCfgResult
        else:
            main.log.error( "There was an error opening the file" )
            return createCfgResult
    except:
        main.log.exception( "There was an error opening the file" )
        return createCfgResult


def sendConfig( main ):
    """
        This function prepares the command needed to upload the configuration
        file to the REST API
    """
    url = "/network/configuration"
    method = "POST"
    data = main.cfgJson
    configResult = main.FALSE
    sendResult = main.Cluster.active( 0 ).REST.send( url=url, method=method, data=data )
    main.log.info( "Device configuration request response code: " + str( sendResult[ 0 ] ) )
    if ( 200 <= sendResult[ 0 ] <= 299 ):
        configResult = main.TRUE
    else:
        configResult = main.FALSE

    return configResult


def devices( main ):
    """
        This function get the list of devices from the REST API, the ONOS CLI, and
        the device-controllers command and check to see that each recognizes the
        device is configured according to the configuration uploaded above.
    """
    availResult = main.FALSE
    typeResult = main.FALSE
    addressResult = main.FALSE
    driverResult = main.FALSE
    try:
        apiResult = main.Cluster.active( 0 ).REST.devices()
        cliResult = main.Cluster.active( 0 ).CLI.devices()

        apiDict = json.loads( apiResult )
        cliDict = json.loads( cliResult )
        apiAnnotations = apiDict[ 0 ].get( "annotations" )
        cliAnnotations = cliDict[ 0 ].get( "annotations" )

        main.log.info( "API device availability result: " + str( apiDict[ 0 ].get( "available" ) ) )
        main.log.info( "CLI device availability result: " + str( cliDict[ 0 ].get( "available" ) ) )
        if apiDict[ 0 ].get( "available" ) and cliDict[ 0 ].get( "available" ):
            availResult = main.TRUE
        main.log.info( "API device type result: " + apiDict[ 0 ].get( "type" ) )
        main.log.info( "CLI device type result: " + cliDict[ 0 ].get( "type" ) )
        if apiDict[ 0 ].get( "type" ) == "SWITCH" and cliDict[ 0 ].get( "type" ) == "SWITCH":
            typeResult = main.TRUE
        main.log.info( "API device ipaddress: " + apiAnnotations.get( "ipaddress" ) )
        main.log.info( "CLI device ipaddress: " + apiAnnotations.get( "ipaddress" ) )
        if str( apiAnnotations.get( "ipaddress" ) ) == main.configDeviceIp and str( cliAnnotations.get( "ipaddress" ) ) == main.configDeviceIp:
            addressResult = main.TRUE
        main.log.info( "API device driver: " + apiAnnotations.get( "driver" ) )
        main.log.info( "CLI device driver: " + cliAnnotations.get( "driver" ) )
        if apiAnnotations.get( "driver" ) == main.configDriver and cliAnnotations.get( "driver" ) == main.configDriver:
            driverResult = main.TRUE

        return availResult and typeResult and addressResult and driverResult
    except TypeError:
        main.log.error( "Device was not configured correctly" )
        return main.FALSE
