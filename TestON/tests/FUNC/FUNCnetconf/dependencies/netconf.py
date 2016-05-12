"""
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
    startResult = main.CLIs[ 0 ].activateApp( appName="org.onosproject.netconf" )
    return startResult

def startOFC( main ):
    """
        This function uses pexpect pxssh class to activate the ofc-server daemon on OC2
    """

    startResult = main.FALSE
    try:
        main.ONOSbench.handle.sendline( "" )
        main.ONOSbench.handle.expect( "\$" )
        main.ONOSbench.handle.sendline( "ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1 }'" )
        main.ONOSbench.handle.expect( "\$1 }'" )
        main.ONOSbench.handle.expect( "\$" )
        main.configDeviceIp = main.ONOSbench.handle.before
        main.configDeviceIp = main.configDeviceIp.split()
        main.configDeviceIp = main.configDeviceIp[ 0 ]
        main.log.info( "Device to be configured: " + str( main.configDeviceIp ) )
        main.ONOSbench.handle.sendline( "sudo ofc-server" )
        main.ONOSbench.handle.expect( "\$" )
        startResult = main.TRUE
        return startResult
    except pexpect.ExceptionPexpect as e:
        main.log.exception( self.name + ": Pexpect exception found: " )
        main.log.error( self.name + ":    " + self.handle.before )
        main.cleanup()
        main.exit()

def createConfig( main ):
    """
        This function writes a configuration file that can later be sent to the
        REST API to configure a device.
        The controller device is assumed to be OC1
        The device to be configured is assumed to be OC2
    """
    createCfgResult = main.FALSE
    # TODO, add ability to set Manufacturer, Hardware and Software versions
    main.cfgJson = '{ "devices":{ "netconf:'+ main.configDeviceIp + ":" +\
                    main.configDevicePort + '":' + '{ "basic":{ "driver":"'+\
                    main.configDriver + '" } } }, "apps": { "' +\
                    main.configApps + '":{ "devices":[ { "name":' +\
                    main.configName + ', "password":' + main.configPass +\
                    ', "ip":"' + main.configDeviceIp + '", "port":' +\
                    main.configPort + '} ] } } }'
    try:
        file = open( os.path.dirname( main.testFile ) + "/dependencies/netconfConfig.json", 'w' )
        # These lines can cause errors during the configuration process because
        # they cause the json string to turn into an unordered dictionary before
        # sorting it alphabetically which can cause the driver type to not be
        # configured.
        # main.cfgJson = json.loads( main.cfgJson )
        # main.cfgJson = json.dumps( main.cfgJson, sort_keys=True,
        #                        indent=4, separators=(',', ': '))
        print main.cfgJson
        file.write( main.cfgJson )
        if file:
            createCfgResult = main.TRUE
            file.close()
            return createCfgResult
        else:
            main.log.error( "There was an error opening the file")
            return createCfgResult
    except:
        main.log.exception( "There was an error opening the file")
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
    sendResult = main.CLIs[ 0 ].send( url=url, method=method, data=data )
    main.log.info( "Device configuration request response code: " + str( sendResult[ 0 ] ) )
    if ( 200 <= sendResult[ 0 ] <= 299):
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
        apiResult = main.CLIs[ 0 ].devices()
        cliResult = main.CLIs2[ 0 ].devices()

        apiDict = json.loads( apiResult )
        cliDict = json.loads( cliResult )
        apiAnnotations = apiDict[ 0 ].get( "annotations" )
        cliAnnotations = cliDict[ 0 ].get( "annotations" )

        main.log.info( "API device availability result: " + str( apiDict[ 0 ].get( "available" ) ) )
        main.log.info( "CLI device availability result: " + str( cliDict[ 0 ].get( "available" ) ) )
        if apiDict[ 0 ].get( "available" ) == True and cliDict[ 0 ].get( "available" ) == True:
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
