#!/usr/bin/env python
"""
Created on 07-08-2015
Copyright 2015 Open Networking Foundation (ONF)

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
import os
import requests
import types
import sys
import time

from drivers.common.api.controllerdriver import Controller


class OnosRestDriver( Controller ):

    def __init__( self ):
        self.pwd = None
        self.user_name = "user"
        super( OnosRestDriver, self ).__init__()
        self.ip_address = "localhost"
        self.port = "8080"
        self.wrapped = sys.modules[ __name__ ]

    def connect( self, **connectargs ):
        try:
            for key in connectargs:
                vars( self )[ key ] = connectargs[ key ]
            self.name = self.options[ 'name' ]
        except Exception as e:
            main.log.exception( e )
        try:
            if os.getenv( str( self.ip_address ) ) is not None:
                self.ip_address = os.getenv( str( self.ip_address ) )
            else:
                main.log.info( self.name + ": ip set to " + self.ip_address )
        except KeyError:
            main.log.info( self.name + ": Invalid host name," +
                           "defaulting to 'localhost' instead" )
            self.ip_address = 'localhost'
        except Exception as inst:
            main.log.error( "Uncaught exception: " + str( inst ) )

        return super( OnosRestDriver, self ).connect()

    def pprint( self, jsonObject ):
        """
        Pretty Prints a json object

        arguments:
            jsonObject - a parsed json object
        returns:
            A formatted string for printing or None on error
        """
        try:
            if not jsonObject:
                return None
            if isinstance( jsonObject, str ):
                jsonObject = json.loads( jsonObject )
            return json.dumps( jsonObject, sort_keys=True,
                               indent=4, separators=( ',', ': ' ) )
        except ( TypeError, ValueError ):
            main.log.exception( "Error parsing jsonObject %s" % repr(jsonObject) )
            return None

    def send( self, url, ip = "DEFAULT", port = "DEFAULT", base="/onos/v1", method="GET",
              query=None, data=None, debug=False ):
        """
        Arguments:
            str ip: ONOS IP Address
            str port: ONOS REST Port
            str url: ONOS REST url path.
                     NOTE that this is is only the relative path. IE "/devices"
            str base: The base url for the given REST api. Applications could
                      potentially have their own base url
            str method: HTTP method type
            dict query: Dictionary to be sent in the query string for
                         the request
            dict data: Dictionary to be sent in the body of the request
        """
        # TODO: Authentication - simple http (user,pass) tuple
        # TODO: should we maybe just pass kwargs straight to response?
        # TODO: Do we need to allow for other protocols besides http?
        # ANSWER: Not yet, but potentially https with certificates
        if ip == "DEFAULT":
            main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
            ip = self.ip_address
        if port == "DEFAULT":
            main.log.warn( self.name + ": No port given, reverting to port " +
                           "from topo file" )
            port = self.port

        try:
            path = "http://" + str( ip ) + ":" + str( port ) + base + url
            if self.user_name and self.pwd:
                main.log.info( self.name + ": user/passwd is: " + self.user_name + "/" + self.pwd )
                auth = ( self.user_name, self.pwd )
            else:
                auth = None
            main.log.info( self.name + ": Sending request " + path + " using " +
                           method.upper() + " method." )
            if debug:
                main.log.debug( self.name + ": request data: " + str( data ) )
            self.log( "Sending %s to %s with %s\n" % ( method.upper(),
                                                       path,
                                                       self.pprint( data ) ) )
            try:
                response = requests.request( method.upper(),
                                             path,
                                             params=query,
                                             data=data,
                                             auth=auth )
            except requests.ConnectionError as e:
                # FIXME: This isn't really the correct place for this, but it works for now
                # Check if port-forward session is still up first
                if hasattr( main, "Cluster"):
                    main.log.warn( self.name + ": Error sending request, checking port-forwarding status" )
                    ctrl = None
                    for c in main.Cluster.controllers:
                        if c.REST is self:
                            ctrl = c
                            break
                    if not ctrl:
                        main.log.warn( self.name + ": Could not find this node in Cluster. Can't check port-forward status" )
                        raise
                    elif ctrl.k8s:
                        ctrl.k8s.checkPortForward( ctrl.k8s.podName,
                                                   kubeconfig=ctrl.k8s.kubeConfig,
                                                   namespace=main.params[ 'kubernetes' ][ 'namespace' ] )
                        main.log.debug( self.name + ": Resending message" )
                        response = requests.request( method.upper(),
                                                     path,
                                                     params=query,
                                                     data=data,
                                                     auth=auth )
                else:
                    raise
            self.log( "Received %s code with body: %s\n" % ( response.status_code,
                                                             self.pprint( response.text.encode( 'utf8' ) ) ) )
            if debug:
                main.log.debug( response )
            return ( response.status_code, response.text.encode( 'utf8' ) )
        except requests.ConnectionError:
            main.log.exception( "Error sending request." )
            return ( None, None )
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def intents( self, ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Gets a list of dictionary of all intents in the system
        Returns:
            A list of dictionary of intents in string type to match the cli
            version for now; Returns main.FALSE if error on request;
            Returns None for exception
        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            response = self.send( url="/intents", ip = ip, port = port )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    output = response[ 1 ]
                    a = json.loads( output ).get( 'intents' )
                    assert a is not None, "Error parsing json object"
                    b = json.dumps( a )
                    return b
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, AssertionError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def intent( self, intentId, appId="org.onosproject.cli",
                ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Get the specific intent information of the given application ID and
            intent ID
        Required:
            str intentId - Intent id in hexadecimal form
        Optional:
            str appId - application id of intent
        Returns:
            Returns an information dictionary of the given intent;
            Returns main.FALSE if error on requests; Returns None for exception
        NOTE:
            The GET /intents REST api command accepts  application id but the
            api will get updated to accept application name instead
        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            # NOTE: REST url requires the intent id to be in decimal form
            query = "/" + str( appId ) + "/" + str( intentId )
            response = self.send( url="/intents" + query, ip = ip, port = port )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    output = response[ 1 ]
                    a = json.loads( output )
                    return a
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def apps( self, ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Returns all the current application installed in the system
        Returns:
            List of dictionary of installed application; Returns main.FALSE for
            error on request; Returns None for exception
        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            response = self.send( url="/applications", ip = ip, port = port )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    output = response[ 1 ]
                    a = json.loads( output ).get( 'applications' )
                    assert a is not None, "Error parsing json object"
                    b = json.dumps( a )
                    return b
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, AssertionError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def activateApp( self, appName, ip="DEFAULT", port="DEFAULT", check=True ):
        """
        Decription:
            Activate an app that is already installed in ONOS
        Optional:
            bool check - If check is True, method will check the status
                         of the app after the command is issued
        Returns:
            Returns main.TRUE if the command was successfully or main.FALSE
            if the REST responded with an error or given incorrect input;
            Returns None for exception

        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            query = "/" + str( appName ) + "/active"
            retry = 0
            retCode = main.TRUE
            while retry < 50:
                if retry > 0:
                    main.log.warn( self.name + ": Retrying " + query + " for the " + str( retry ) + " time" )

                retry += 1
                response = self.send( method="POST",
                                      debug=True,
                                      url="/applications" + query,
                                      ip = ip, port = port )
                if response:
                    output = response[ 1 ]
                    if 200 <= response[ 0 ] <= 299:
                        if check:
                            app = json.loads( output )
                            if app.get( 'state' ) == 'ACTIVE':
                                main.log.info( self.name + ": " + appName +
                                               " application" +
                                               " is in ACTIVE state" )
                                appHealth = self.getAppHealth( appName=appName, ip=ip, port=port )
                                if "ready" == json.loads( appHealth[1] ).get( 'message' ):
                                    return main.TRUE
                                else:
                                    return main.FALSE
                            else:
                                main.log.error( self.name + ": " + appName +
                                                " application" + " is in " +
                                                app.get( 'state' ) + " state" )
                                retCode = main.FALSE
                        else:
                            main.log.warn( self.name + ": Skipping " + appName +
                                           "application check" )
                            return main.TRUE
                    else:
                        main.log.error( "Error with REST request, response was: %s: %s" %
                                        ( response[ 0 ], response[ 1 ] ) )
                        retCode = main.FALSE
                time.sleep( 30 )
                return retCode
        except ( ValueError ):
            main.log.exception( self.name + ": Error parsing json" )
            return main.FALSE
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.log.debug( self.name + ": " + response )
            main.cleanAndExit()

    def deactivateApp( self, appName, ip="DEFAULT", port="DEFAULT",
                       check=True ):
        """
        Required:
            Deactivate an app that is already activated in ONOS
        Optional:
            bool check - If check is True, method will check the status of the
            app after the command is issued
        Returns:
            Returns main.TRUE if the command was successfully sent
            main.FALSE if the REST responded with an error or given
            incorrect input; Returns None for exception
        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            query = "/" + str( appName ) + "/active"
            self.send( method="DELETE",
                       url="/applications" + query,
                       ip = ip, port = port )
            response = self.getApp( appName, ip, port )
            if response:
                output = response[ 1 ]
                app = {} if output == "" else json.loads( output )
                if 200 <= response[ 0 ] <= 299:
                    if check:
                        if app.get( 'state' ) == 'INSTALLED':
                            main.log.info( self.name + ": " + appName +
                                           " application" +
                                           " is in INSTALLED state" )
                            return main.TRUE
                        else:
                            main.log.error( self.name + ": " + appName +
                                            " application" + " is in " +
                                            app.get( 'state' ) + " state" )
                            return main.FALSE
                    else:
                        main.log.warn( self.name + ": Skipping " + appName +
                                       "application check" )
                        return main.TRUE
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getApp( self, appName, ip="DEFAULT",
                port="DEFAULT" ):
        """
        Decription:
            Gets the informaion of the given application
        Required:
            str name - Name of onos application
        Returns:
            Returns a dictionary of information ONOS application in string type;
            Returns main.FALSE if error on requests; Returns None for exception
        """
        try:
            response = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            query = "/" + str( appName )
            response = self.send( url="/applications" + query,
                                  ip = ip, port = port )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    return response
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getAppHealth( self, appName, ip="DEFAULT",
                      port="DEFAULT" ):
        """
        Decription:
            Gets the health of the given application
        Required:
            str name - Name of onos application
        Returns:
            Returns a dictionary of information ONOS application in string type;
            Returns main.FALSE if error on requests; Returns None for exception
        """
        try:
            response = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            response = self.send( url="/applications/%s/health" % str( appName ),
                                  ip = ip, port = port )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    return response
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getAllAppHealth( self, retries=1, wait=30 , ip="DEFAULT",
                         port="DEFAULT" ):
        """
        Description:
            Gets the health of all activated apps
        Required:
        Optional:
            retries - The number of tries to return before returning
            wait - Time to wait in between retries
        """
        try:
            responses = main.TRUE
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            apps = self.apps()
            for app in json.loads(apps):
                appName = app.get( "name" )
                response = self.getAppHealth( appName=appName, ip=ip, port=port )
                responses = main.TRUE and "ready" == json.loads( response[1] ).get( "message" )
            return responses
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def addHostIntent( self, hostIdOne, hostIdTwo, appId='org.onosproject.cli',
                       ip="DEFAULT", port="DEFAULT", vlanId="" ):
        """
        Description:
            Adds a host-to-host intent ( bidirectional ) by
            specifying the two hosts.
        Required:
            * hostIdOne: ONOS host id for host1
            * hostIdTwo: ONOS host id for host2
        Optional:
            str appId - Application name of intent identifier
        Returns:
            Returns main.TRUE for successful requests; Returns main.FALSE if
            error on requests; Returns None for exceptions
        """
        try:
            intentJson = { "two": str( hostIdTwo ),
                           "selector": { "criteria": [] }, "priority": 7,
                           "treatment": { "deferred": [], "instructions": [] },
                           "appId": appId, "one": str( hostIdOne ),
                           "type": "HostToHostIntent",
                           "constraints": [ { "type": "LinkTypeConstraint",
                                              "types": [ "OPTICAL" ],
                                              "inclusive": 'false' } ] }
            if vlanId:
                intentJson[ 'selector' ][ 'criteria' ].append( { "type": "VLAN_VID",
                                                                 "vlanId": vlanId } )
            response = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            response = self.send( method="POST",
                                  url="/intents", ip = ip, port = port,
                                  data=json.dumps( intentJson ) )
            if response:
                if "201" in str( response[ 0 ] ):
                    main.log.info( self.name + ": Successfully POST host" +
                                   " intent between host: " + hostIdOne +
                                   " and host: " + hostIdTwo )
                    return main.TRUE
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE

        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def addPointIntent( self,
                        ingressDevice,
                        egressDevice,
                        appId='org.onosproject.cli',
                        ingressPort="",
                        egressPort="",
                        ethType="",
                        ethSrc="",
                        ethDst="",
                        bandwidth="",
                        protected=False,
                        lambdaAlloc=False,
                        ipProto="",
                        ipSrc="",
                        ipDst="",
                        tcpSrc="",
                        tcpDst="",
                        ip="DEFAULT",
                        port="DEFAULT",
                        vlanId="" ):
        """
        Description:
            Adds a point-to-point intent ( uni-directional ) by
            specifying device id's and optional fields
        Required:
            * ingressDevice: device id of ingress device
            * egressDevice: device id of egress device
        Optional:
            * ethType: specify ethType
            * ethSrc: specify ethSrc ( i.e. src mac addr )
            * ethDst: specify ethDst ( i.e. dst mac addr )
            * bandwidth: specify bandwidth capacity of link (TODO)
            * lambdaAlloc: if True, intent will allocate lambda
              for the specified intent (TODO)
            * ipProto: specify ip protocol
            * ipSrc: specify ip source address with mask eg. ip#/24
            * ipDst: specify ip destination address eg. ip#/24
            * tcpSrc: specify tcp source port
            * tcpDst: specify tcp destination port
        Returns:
            Returns main.TRUE for successful requests; Returns main.FALSE if
            no ingress|egress port found and if error on requests;
            Returns None for exceptions
        NOTE:
            The ip and port option are for the requests input's ip and port
            of the ONOS node
        """
        try:
            if "/" in ingressDevice:
                if not ingressPort:
                    ingressPort = ingressDevice.split( "/" )[ 1 ]
                ingressDevice = ingressDevice.split( "/" )[ 0 ]
            else:
                if not ingressPort:
                    main.log.debug( self.name + ": Ingress port not specified" )
                    return main.FALSE

            if "/" in egressDevice:
                if not egressPort:
                    egressPort = egressDevice.split( "/" )[ 1 ]
                egressDevice = egressDevice.split( "/" )[ 0 ]
            else:
                if not egressPort:
                    main.log.debug( self.name + ": Egress port not specified" )
                    return main.FALSE

            intentJson = { "ingressPoint": { "device": ingressDevice,
                                             "port": ingressPort },
                           "selector": { "criteria": [] },
                           "priority": 55,
                           "treatment": { "deferred": [],
                                          "instructions": [] },
                           "egressPoint": { "device": egressDevice,
                                            "port": egressPort },
                           "appId": appId,
                           "type": "PointToPointIntent",
                           "constraints": [ { "type": "LinkTypeConstraint",
                                              "types": [ "OPTICAL" ],
                                              "inclusive": "false" } ] }

            if ethType == "IPV4":
                intentJson[ 'selector' ][ 'criteria' ].append( {
                                                         "type": "ETH_TYPE",
                                                         "ethType": 2048 } )
            elif ethType:
                intentJson[ 'selector' ][ 'criteria' ].append( {
                                                         "type": "ETH_TYPE",
                                                         "ethType": ethType } )

            if ethSrc:
                intentJson[ 'selector' ][ 'criteria' ].append(
                                                       { "type": "ETH_SRC",
                                                         "mac": ethSrc } )
            if ethDst:
                intentJson[ 'selector' ][ 'criteria' ].append(
                                                       { "type": "ETH_DST",
                                                         "mac": ethDst } )
            if ipSrc:
                intentJson[ 'selector' ][ 'criteria' ].append(
                                                       { "type": "IPV4_SRC",
                                                         "ip": ipSrc } )
            if ipDst:
                intentJson[ 'selector' ][ 'criteria' ].append(
                                                       { "type": "IPV4_DST",
                                                         "ip": ipDst } )
            if tcpSrc:
                intentJson[ 'selector' ][ 'criteria' ].append(
                                                       { "type": "TCP_SRC",
                                                         "tcpPort": tcpSrc } )
            if tcpDst:
                intentJson[ 'selector' ][ 'criteria' ].append(
                                                       { "type": "TCP_DST",
                                                         "tcpPort": tcpDst } )
            if ipProto:
                intentJson[ 'selector' ][ 'criteria' ].append(
                                                       { "type": "IP_PROTO",
                                                         "protocol": ipProto } )
            if vlanId:
                intentJson[ 'selector' ][ 'criteria' ].append(
                                                       { "type": "VLAN_VID",
                                                         "vlanId": vlanId } )

            # TODO: Bandwidth and Lambda will be implemented if needed

            response = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            response = self.send( method="POST",
                                  url="/intents", ip = ip, port = port,
                                  data=json.dumps( intentJson ) )

            main.log.debug( intentJson )

            if response:
                if "201" in str( response[ 0 ] ):
                    main.log.info( self.name + ": Successfully POST point" +
                                   " intent between ingress: " + ingressDevice +
                                   " and egress: " + egressDevice + " devices" )
                    return main.TRUE
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE

        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def addSinglepointToMultipointIntent( self,
                                          ingressDevice,
                                          egressDeviceList,
                                          portEgressList,
                                          appId='org.onosproject.cli',
                                          portIngress="",
                                          ethType="",
                                          ethSrc="",
                                          ethDst="",
                                          bandwidth="",
                                          lambdaAlloc=False,
                                          ipProto="",
                                          ipSrc="",
                                          ipDst="",
                                          tcpSrc="",
                                          tcpDst="",
                                          partial=False,
                                          ip="DEFAULT",
                                          port="DEFAULT",
                                          vlanId="" ):
        """
        Description:
            Adds a point-to-multi point intent ( uni-directional ) by
            specifying device id's and optional fields
        Required:
            * ingressDevice: device id of ingress device
            * egressDevice: device id of egress device
            * portEgressList: a list of port id of egress device

        Optional:
            * portIngress: port id of ingress device
            * ethType: specify ethType
            * ethSrc: specify ethSrc ( i.e. src mac addr )
            * ethDst: specify ethDst ( i.e. dst mac addr )
            * bandwidth: specify bandwidth capacity of link (TODO)
            * lambdaAlloc: if True, intent will allocate lambda
              for the specified intent (TODO)
            * ipProto: specify ip protocol
            * ipSrc: specify ip source address with mask eg. ip#/24
            * ipDst: specify ip destination address eg. ip#/24
            * tcpSrc: specify tcp source port
            * tcpDst: specify tcp destination port
        Returns:
            Returns main.TRUE for successful requests; Returns main.FALSE if
            no ingress|egress port found and if error on requests;
            Returns None for exceptions
        NOTE:
            The ip and port option are for the requests input's ip and port
            of the ONOS node
        """
        try:

            if "/" in ingressDevice:
                if not portIngress:
                    ingressPort = ingressDevice.split( "/" )[ 1 ]
                ingressDevice = ingressDevice.split( "/" )[ 0 ]
            else:
                if not portIngress:
                    main.log.debug( self.name + ": Ingress port not specified" )
                    return main.FALSE
            index = 0
            for egressDevice in egressDeviceList:
                if "/" in egressDevice:
                    portEgressList.append( egressDevice.split( "/" )[ 1 ] )
                    egressDeviceList[ index ] = egressDevice.split( "/" )[ 0 ]
                else:
                    if not portEgressList:
                        main.log.debug( self.name + ": Egress port not specified" )
                        return main.FALSE
                index = index + 1

            intentJson = { "ingressPoint": { "device": ingressDevice,
                                             "port": ingressPort },
                           "selector": { "criteria": [] },
                           "priority": 55,
                           "treatment": { "deferred": [],
                                          "instructions": [] },
                           "egressPoint": { "connectPoints": [] },
                           "appId": appId,
                           "type": "SinglePointToMultiPointIntent",
                           "constraints": [ { "type": "LinkTypeConstraint",
                                              "types": [ "OPTICAL" ],
                                              "inclusive": "false" } ] }

            index = 0
            for ep in portEgressList:
                intentJson[ 'egressPoint' ][ 'connectPoints' ].append(
                    { "device": egressDeviceList[ index ],
                      "port": ep } )
                index += 1

            if ethType == "IPV4":
                intentJson[ 'selector' ][ 'criteria' ].append(
                    { "type": "ETH_TYPE",
                      "ethType": 2048 } )
            elif ethType:
                intentJson[ 'selector' ][ 'criteria' ].append(
                    { "type": "ETH_TYPE",
                      "ethType": ethType } )

            if ethSrc:
                intentJson[ 'selector' ][ 'criteria' ].append(
                    { "type": "ETH_SRC",
                      "mac": ethSrc } )

            if ethDst:
                for dst in ethDst:
                    if dst:
                        intentJson[ 'selector' ][ 'criteria' ].append(
                            { "type": "ETH_DST",
                              "mac": dst } )
            if tcpSrc:
                intentJson[ 'selector' ][ 'criteria' ].append(
                    { "type": "TCP_SRC",
                      "tcpPort": tcpSrc } )
            if tcpDst:
                intentJson[ 'selector' ][ 'criteria' ].append(
                    { "type": "TCP_DST",
                      "tcpPort": tcpDst } )
            if ipProto:
                intentJson[ 'selector' ][ 'criteria' ].append(
                    { "type": "IP_PROTO",
                      "protocol": ipProto } )
            if vlanId:
                intentJson[ 'selector' ][ 'criteria' ].append(
                    { "type": "VLAN_VID",
                      "vlanId": vlanId } )

            # TODO: Bandwidth and Lambda will be implemented if needed

            response = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            response = self.send( method="POST",
                                  url="/intents", ip=ip, port=port,
                                  data=json.dumps( intentJson ) )

            main.log.debug( intentJson )

            if response:
                if "201" in str( response[ 0 ] ):
                    main.log.info( self.name + ": Successfully POST point" +
                                   " intent between ingress: " + ingressDevice +
                                   " and egress: " + str( egressDeviceList ) + " devices" )
                    return main.TRUE
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" % ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
            else:
                main.log.error( "REST request has no response." )
                return main.FALSE

        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def removeIntent( self, intentId, appId='org.onosproject.cli',
                       ip="DEFAULT", port="DEFAULT" ):
        """
            Remove intent for specified application id and intent id;
            Returns None for exception
        """
        try:
            response = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            # NOTE: REST url requires the intent id to be in decimal form
            query = "/" + str( appId ) + "/" + str( int( intentId, 16 ) )
            response = self.send( method="DELETE",
                                  url="/intents" + query, ip = ip, port = port )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    return main.TRUE
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getIntentsId( self, ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Gets all intents ID using intents function
        Returns:
            List of intents ID if found any intents; Returns main.FALSE for other exceptions
        """
        try:
            intentIdList = []
            intentsJson = json.loads( self.intents( ip=ip, port=port ) )
            for intent in intentsJson:
                intentIdList.append( intent.get( 'id' ) )
            if not intentIdList:
                main.log.debug( self.name + ": Cannot find any intents" )
                return main.FALSE
            else:
                return intentIdList
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def removeAllIntents( self, intentIdList ='ALL', appId='org.onosproject.cli',
                          ip="DEFAULT", port="DEFAULT", delay=5 ):
        """
        Description:
            Remove all the intents
        Returns:
            Returns main.TRUE if all intents are removed, otherwise returns
            main.FALSE; Returns None for exception
        """
        try:
            results = []
            if intentIdList == 'ALL':
                # intentIdList = self.getIntentsId( ip=ip, port=port )
                intentIdList = self.getIntentsId()

            main.log.info( self.name + ": Removing intents " +
                           str( intentIdList ) )

            if isinstance( intentIdList, types.ListType ):
                for intent in intentIdList:
                    results.append( self.removeIntent( intentId=intent,
                                                       appId=appId,
                                                       ip=ip,
                                                       port=port ) )
                # Check for remaining intents
                # NOTE: Noticing some delay on Deleting the intents so i put
                # this time out
                import time
                time.sleep( delay )
                intentRemain = len( json.loads( self.intents() ) )
                if all( result == main.TRUE for result in results ) and \
                   intentRemain == 0:
                    main.log.info( self.name + ": All intents are removed " )
                    return main.TRUE
                else:
                    main.log.error( self.name + ": Did not removed all intents,"
                                    + " there are " + str( intentRemain )
                                    + " intents remaining" )
                    return main.FALSE
            else:
                main.log.debug( self.name + ": There is no intents ID list" )
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def hosts( self, ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Get a list of dictionary of all discovered hosts
        Returns:
            Returns a list of dictionary of information of the hosts currently
            discovered by ONOS; Returns main.FALSE if error on requests;
            Returns None for exception
        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            response = self.send( url="/hosts", ip = ip, port = port )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    output = response[ 1 ]
                    a = json.loads( output ).get( 'hosts' )
                    assert a is not None, "Error parsing json object"
                    b = json.dumps( a )
                    return b
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, AssertionError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getHost( self, mac, vlan="-1", ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Gets the information from the given host
        Required:
            str mac - MAC address of the host
        Optional:
            str vlan - VLAN tag of the host, defaults to -1
        Returns:
            Return the host id from the hosts/mac/vlan output in REST api
            whose 'id' contains mac/vlan; Returns None for exception;
            Returns main.FALSE if error on requests

        NOTE:
            Not sure what this function should do, any suggestion?
        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            query = "/" + mac + "/" + vlan
            response = self.send( url="/hosts" + query, ip = ip, port = port )
            if response:
                # NOTE: What if the person wants other values? would it be better
                # to have a function that gets a key and return a value instead?
                # This function requires mac and vlan and returns an ID which
                # makes this current function useless
                if 200 <= response[ 0 ] <= 299:
                    output = response[ 1 ]
                    hostId = json.loads( output ).get( 'id' )
                    return hostId
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def topology( self, ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Gets the overview of network topology
        Returns:
            Returns a dictionary containing information about network topology;
            Returns None for exception
        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            response = self.send( url="/topology", ip = ip, port = port )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    output = response[ 1 ]
                    a = json.loads( output )
                    b = json.dumps( a )
                    return b
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def devices( self, ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Get the devices discovered by ONOS is json string format
        Returns:
            a json string of the devices currently discovered by ONOS OR
            main.FALSE if there is an error in the request OR
            Returns None for exception
        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            response = self.send( url="/devices", ip = ip, port = port )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    output = response[ 1 ]
                    a = json.loads( output ).get( 'devices' )
                    assert a is not None, "Error parsing json object"
                    b = json.dumps( a )
                    return b
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, AssertionError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getIntentState( self, intentsId, intentsJson=None,
                        ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Get intent state.
            Accepts a single intent ID (string type) or a list of intent IDs.
            Returns the state(string type) of the id if a single intent ID is
            accepted.
        Required:
            intentId: intent ID (string type)
            intentsJson: parsed json object from the onos:intents api
        Returns:
            Returns a dictionary with intent IDs as the key and its
            corresponding states as the values; Returns None for invalid IDs or
            Type error and any exceptions
        NOTE:
            An intent's state consist of INSTALLED,WITHDRAWN etc.
        """
        try:
            state = "State is Undefined"
            if not intentsJson:
                intentsJsonTemp = json.loads( self.intents() )
            else:
                intentsJsonTemp = json.loads( intentsJson )
            if isinstance( intentsId, types.StringType ):
                for intent in intentsJsonTemp:
                    if intentsId == intent[ 'id' ]:
                        state = intent[ 'state' ]
                        return state
                main.log.info( self.name + ": Cannot find intent ID" + str( intentsId ) +
                               " on the list" )
                return state
            elif isinstance( intentsId, types.ListType ):
                dictList = []
                for i in xrange( len( intentsId ) ):
                    stateDict = {}
                    for intents in intentsJsonTemp:
                        if intentsId[ i ] == intents[ 'id' ]:
                            stateDict[ 'state' ] = intents[ 'state' ]
                            stateDict[ 'id' ] = intentsId[ i ]
                            dictList.append( stateDict )
                            break
                if len( intentsId ) != len( dictList ):
                    main.log.info( self.name + ": Cannot find some of the intent ID state" )
                return dictList
            else:
                main.log.info( self.name + ": Invalid intents ID entry" )
                return None

        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def checkIntentState( self, intentsId="ALL", expectedState='INSTALLED',
                          ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Check intents state based on expected state which defaults to
            INSTALLED state
        Required:
            intentsId - List of intents ID to be checked
        Optional:
            expectedState - Check the expected state(s) of each intents
                            state in the list.
                            *NOTE: You can pass in a list of expected state,
                            Eg: expectedState = [ 'INSTALLED' , 'INSTALLING' ]
        Return:
            Returns main.TRUE only if all intent are the same as expected states
            , otherwise, returns main.FALSE; Returns None for general exception
        """
        try:
            # Generating a dictionary: intent id as a key and state as value
            returnValue = main.TRUE
            if intentsId == "ALL":
                intentsId = self.getIntentsId( ip=ip, port=port )
            intentsDict = self.getIntentState( intentsId, ip=ip, port=port )

            if len( intentsId ) != len( intentsDict ):
                main.log.error( self.name + ": There is something wrong " +
                                "getting intents state" )
                return main.FALSE

            if isinstance( expectedState, types.StringType ):
                for intents in intentsDict:
                    if intents.get( 'state' ) != expectedState:
                        main.log.debug( self.name + ": Intent ID - " +
                                        intents.get( 'id' ) +
                                        " actual state = " +
                                        intents.get( 'state' )
                                        + " does not equal expected state = "
                                        + expectedState )
                        returnValue = main.FALSE

            elif isinstance( expectedState, types.ListType ):
                for intents in intentsDict:
                    if not any( state == intents.get( 'state' ) for state in
                                expectedState ):
                        main.log.debug( self.name + ": Intent ID - " +
                                        intents.get( 'id' ) +
                                        " actual state = " +
                                        intents.get( 'state' ) +
                                        " does not equal expected states = "
                                        + str( expectedState ) )
                        returnValue = main.FALSE

            if returnValue == main.TRUE:
                main.log.info( self.name + ": All " +
                               str( len( intentsDict ) ) +
                               " intents are in " + str( expectedState ) +
                               " state" )
            return returnValue
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def flows( self, ip="DEFAULT", port="DEFAULT", subjectClass=None, subjectKey=None ):
        """
        Description:
            Get flows currently added to the system
        NOTE:
            The flows -j cli command has completely different format than
            the REST output

        Returns None for exception
        """
        try:
            output = None
            url = "/flows"
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            if subjectKey and not subjectClass:
                main.log.warning( "Subject Key provided without Subject Class.  Ignoring Subject Key" )
            if subjectClass:
                url += "/" + subjectClass
                if subjectKey:
                    url += "/" + subjectKey
            response = self.send( url=url, ip=ip, port=port )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    output = response[ 1 ]
                    a = json.loads( output ).get( 'flows' )
                    assert a is not None, "Error parsing json object"
                    b = json.dumps( a )
                    return b
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, AssertionError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getFlows( self, deviceId, flowId=None, ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Gets all the flows of the device or get a specific flow in the
            device by giving its flow ID
        Required:
            str deviceId - device/switch Id
        Optional:
            int/hex flowId - ID of the flow
        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            url = "/flows/" + deviceId
            if flowId:
                url += "/" + str( int( flowId ) )
            print url
            response = self.send( url=url, ip = ip, port = port )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    output = response[ 1 ]
                    a = json.loads( output ).get( 'flows' )
                    assert a is not None, "Error parsing json object"
                    b = json.dumps( a )
                    return b
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, AssertionError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def sendFlow( self, deviceId, flowJson, ip="DEFAULT", port="DEFAULT", debug=False ):
        """
        Description:
            Sends a single flow to the specified device. This function exists
            so you can bypass the addFLow driver and send your own custom flow.
        Required:
            * The flow in json
            * the device id to add the flow to
        Returns:
            Returns main.TRUE for successful requests; Returns main.FALSE
            if error on requests;
            Returns None for exceptions
        NOTE:
            The ip and port option are for the requests input's ip and port
            of the ONOS node
        """

        try:
            if debug:
                main.log.debug( self.name + ": Adding flow: " + self.pprint( flowJson ) )
            response = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            url = "/flows/" + deviceId
            response = self.send( method="POST",
                                  url=url, ip = ip, port = port,
                                  data=json.dumps( flowJson ) )
            if response:
                if "201" in str( response[ 0 ] ):
                    main.log.info( self.name + ": Successfully POST flow" +
                                   "in device: " + str( deviceId ) )
                    return main.TRUE
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except NotImplementedError as e:
            raise e  # Inform the caller
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def addFlow( self,
                 deviceId,
                 appId=0,
                 ingressPort="",
                 egressPort="",
                 ethType="",
                 ethSrc="",
                 ethDst="",
                 vlan="",
                 ipProto="",
                 ipSrc=(),
                 ipDst=(),
                 tcpSrc="",
                 tcpDst="",
                 udpDst="",
                 udpSrc="",
                 mpls="",
                 priority=100,
                 groupId="",
                 ip="DEFAULT",
                 port="DEFAULT",
                 debug=False ):
        """
        Description:
            Creates a single flow in the specified device
        Required:
            * deviceId: id of the device
        Optional:
            * ingressPort: port ingress device
            * egressPort: port  of egress device
            * ethType: specify ethType
            * ethSrc: specify ethSrc ( i.e. src mac addr )
            * ethDst: specify ethDst ( i.e. dst mac addr )
            * ipProto: specify ip protocol
            * ipSrc: specify ip source address with mask eg. ip#/24
                as a tuple (type, ip#)
            * ipDst: specify ip destination address eg. ip#/24
                as a tuple (type, ip#)
            * tcpSrc: specify tcp source port
            * tcpDst: specify tcp destination port
        Returns:
            Returns main.TRUE for successful requests; Returns main.FALSE
            if error on requests;
            Returns None for exceptions
        NOTE:
            The ip and port option are for the requests input's ip and port
            of the ONOS node
        """
        try:
            flowJson = {   "priority": priority,
                           "isPermanent": "true",
                           "timeout": 0,
                           "deviceId": deviceId,
                           "treatment": { "instructions": [] },
                           "selector": { "criteria": [] }}
            if appId:
                flowJson[ "appId" ] = appId

            if groupId:
                flowJson[ 'treatment' ][ 'instructions' ].append( {
                                                        "type": "GROUP",
                                                        "groupId": groupId } )

            if egressPort:
                flowJson[ 'treatment' ][ 'instructions' ].append( {
                                                        "type": "OUTPUT",
                                                        "port": egressPort } )
            if ingressPort:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                        "type": "IN_PORT",
                                                        "port": ingressPort } )
            if ethType:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                        "type": "ETH_TYPE",
                                                        "ethType": ethType } )
            if ethSrc:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                        "type": "ETH_SRC",
                                                        "mac": ethSrc } )
            if ethDst:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                        "type": "ETH_DST",
                                                        "mac": ethDst } )
            if vlan:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                        "type": "VLAN_VID",
                                                        "vlanId": vlan } )
            if mpls:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                        "type": "MPLS_LABEL",
                                                        "label": mpls } )
            if ipSrc:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                        "type": ipSrc[ 0 ],
                                                        "ip": ipSrc[ 1 ] } )
            if ipDst:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                        "type": ipDst[ 0 ],
                                                        "ip": ipDst[ 1 ] } )
            if tcpSrc:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                        "type": "TCP_SRC",
                                                        "tcpPort": tcpSrc } )
            if tcpDst:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                        "type": "TCP_DST",
                                                        "tcpPort": tcpDst } )
            if udpSrc:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                        "type": "UDP_SRC",
                                                        "udpPort": udpSrc } )
            if udpDst:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                        "type": "UDP_DST",
                                                        "udpPort": udpDst } )
            if ipProto:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                        "type": "IP_PROTO",
                                                        "protocol": ipProto } )

            return self.sendFlow( deviceId=deviceId, flowJson=flowJson, debug=debug, ip=ip, port=port )

        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def removeFlow( self, deviceId, flowId,
                       ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Remove specific device flow
        Required:
            str deviceId - id of the device
            str flowId - id of the flow
        Return:
            Returns main.TRUE if successfully deletes flows, otherwise
            Returns main.FALSE, Returns None on error
        """
        try:
            response = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            # NOTE: REST url requires the intent id to be in decimal form
            query = "/" + str( deviceId ) + "/" + str( int( flowId ) )
            response = self.send( method="DELETE",
                                  url="/flows" + query, ip = ip, port = port )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    return main.TRUE
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def checkFlowsState( self , ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Check if all the current flows are in ADDED state
        Return:
            returnValue - Returns main.TRUE only if all flows are in
                          return main.FALSE otherwise;
                          Returns None for exception
        """
        try:
            tempFlows = json.loads( self.flows( ip=ip, port=port ) )
            returnValue = main.TRUE
            for flow in tempFlows:
                if flow.get( 'state' ) != 'ADDED':
                    main.log.info( self.name + ": flow Id: " +
                                   str( flow.get( 'groupId' ) ) +
                                   " | state:" +
                                   str( flow.get( 'state' ) ) )
                    returnValue = main.FALSE
            return returnValue
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getNetCfg( self, ip="DEFAULT", port="DEFAULT",
                   subjectClass=None, subjectKey=None, configKey=None ):
        """
        Description:
            Get a json object with the ONOS network configurations
        Returns:
            A json object containing the network configuration in
            ONOS; Returns main.FALSE if error on requests;
            Returns None for exception
        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            url = "/network/configuration"
            if subjectClass:
                url += "/" + self.checkRegex( subjectClass )
                if subjectKey:
                    url += "/" + self.checkRegex( subjectKey )
                    if configKey:
                        url += "/" + self.checkRegex( configKey )
            url = requests.utils.quote( url, safe="%/" )
            response = self.send( url=url, ip = ip, port = port )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    output = response[ 1 ]
                    a = json.loads( output )
                    b = json.dumps( a )
                    return b
                elif response[ 0 ] == 404:
                    main.log.error( "Requested configuration doesn't exist: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return {}
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def checkRegex( self, inputStr ):
        res = inputStr.replace('/', '%2f')
        return res

    def setNetCfg( self, cfgJson, ip="DEFAULT", port="DEFAULT",
                   subjectClass=None, subjectKey=None, configKey=None ):
        """
        Description:
            Set a json object with the ONOS network configurations
        Returns:
            Returns main.TRUE for successful requests; Returns main.FALSE
            if error on requests;
            Returns None for exceptions

        """
        try:
            response = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            url = "/network/configuration"
            if subjectClass:
                url += "/" + self.checkRegex( subjectClass )
                if subjectKey:
                    url += "/" + self.checkRegex( subjectKey )
                    if configKey:
                        url += "/" + self.checkRegex( configKey )
            url = requests.utils.quote( url, safe="%/" )
            response = self.send( method="POST",
                                  url=url, ip = ip, port = port,
                                  data=json.dumps( cfgJson ) )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    main.log.info( self.name + ": Successfully POST cfg" )
                    return main.TRUE
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def removeNetCfg( self, ip="DEFAULT", port="DEFAULT",
                      subjectClass=None, subjectKey=None, configKey=None ):
        """
        Description:
            Remove a json object from the ONOS network configurations
        Returns:
            Returns main.TRUE for successful requests; Returns main.FALSE
            if error on requests;
            Returns None for exceptions

        """
        try:
            response = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            url = "/network/configuration"
            if subjectClass:
                url += "/" + subjectClass
                if subjectKey:
                    url += "/" + subjectKey
                    if configKey:
                        url += "/" + configKey
            response = self.send( method="DELETE",
                                  url=url, ip = ip, port = port )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    main.log.info( self.name + ": Successfully delete cfg" )
                    return main.TRUE
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getXconnect( self, ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Get xconnects
        Returns:
            Return xconnects json object
            Returns None for exceptions

        """
        try:
            base = "/onos/segmentrouting"
            response = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            url = "/xconnect"
            response = self.send( method="GET",
                                  base=base,
                                  url=url, ip = ip, port = port )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    main.log.info( self.name + ": Successfully POST cfg" )
                    return main.TRUE
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def setXconnect( self, deviceId, vlanId, port1, port2, ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Set xconnects
        Returns:
            Returns main.TRUE for successful requests; Returns main.FALSE
            if error on requests;
            Returns None for exceptions

        """
        try:
            cfgJson = json.loads( '{"deviceId": "%s", "vlanId": "%s", "endpoints":[%s,%s]}' %
                                 ( deviceId, vlanId, port1, port2 ) )
            response = self.setXconnectJson( cfgJson, ip=ip, port=port )
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def setXconnectJson( self, cfgJson, ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Set xconnects
        Returns:
            Returns main.TRUE for successful requests; Returns main.FALSE
            if error on requests;
            Returns None for exceptions

        """
        try:
            base = "/onos/segmentrouting"
            response = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            url = "/xconnect"
            response = self.send( method="POST",
                                  base=base,
                                  url=url, ip = ip, port = port,
                                  data=json.dumps( cfgJson ) )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    main.log.info( self.name + ": Successfully POST cfg" )
                    return main.TRUE
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def deleteXconnect( self, cfgJson, ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Remove xconnects
        Returns:
            Returns main.TRUE for successful requests; Returns main.FALSE
            if error on requests;
            Returns None for exceptions

        """
        try:
            base = "/onos/segmentrouting"
            response = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            url = "/xconnect"
            response = self.send( method="DELETE",
                                  base=base,
                                  url=url, ip = ip, port = port,
                                  data=json.dumps( cfgJson ) )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    main.log.info( self.name + ": Successfully POST cfg" )
                    return main.TRUE
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def createFlowBatch( self,
                         numSw = 1,
                         swIndex = 1,
                         batchSize = 1,
                         batchIndex = 1,
                         deviceIdpreFix = "of:",
                         appId=0,
                         deviceID="",
                         ingressPort="",
                         egressPort="",
                         ethType="",
                         ethSrc="",
                         ethDst="",
                         vlan="",
                         ipProto="",
                         ipSrc=(),
                         ipDst=(),
                         tcpSrc="",
                         tcpDst="",
                         udpDst="",
                         udpSrc="",
                         mpls="",
                         ip="DEFAULT",
                         port="DEFAULT",
                         debug=False ):
        """
        Description:
            Creates batches of MAC-rule flows for POST.
            Predefined MAC: 2 MS Hex digit for iterating devices
                        Next 5 Hex digit for iterating batch numbers
                        Next 5 Hex digit for iterating flows within a batch
        Required:
            * deviceId: id of the device
        Optional:
            * ingressPort: port ingress device
            * egressPort: port  of egress device
            * ethType: specify ethType
            * ethSrc: specify ethSrc ( i.e. src mac addr )
            * ethDst: specify ethDst ( i.e. dst mac addr )
            * ipProto: specify ip protocol
            * ipSrc: specify ip source address with mask eg. ip#/24
                as a tuple (type, ip#)
            * ipDst: specify ip destination address eg. ip#/24
                as a tuple (type, ip#)
            * tcpSrc: specify tcp source port
            * tcpDst: specify tcp destination port
        Returns:
            Returns main.TRUE for successful requests; Returns main.FALSE
            if error on requests;
            Returns None for exceptions
        NOTE:
            The ip and port option are for the requests input's ip and port
            of the ONOS node
        """

        flowJsonList = []
        flowJsonBatch = { "flows": flowJsonList }
        dev = swIndex

        for fl in range( 1, batchSize + 1 ):
            flowJson = { "priority": 100,
                           "deviceId": "",
                           "isPermanent": "true",
                           "timeout": 0,
                           "treatment": { "instructions": [] },
                           "selector": { "criteria": [] }}

            # main.log.info("fl: " + str(fl))
            if dev <= numSw:
                deviceId = deviceIdpreFix + "{0:0{1}x}".format( dev, 16 )
                # print deviceId
                flowJson[ 'deviceId' ] = deviceId
                dev += 1
            else:
                dev = 1
                deviceId = deviceIdpreFix + "{0:0{1}x}".format( dev, 16 )
                # print deviceId
                flowJson[ 'deviceId' ] = deviceId
                dev += 1

                # ethSrc starts with "0"; ethDst starts with "1"
                # 2 Hex digit of device number; 5 digits of batch index number; 5 digits of batch size
            ethS = "%02X" % int( "0" + "{0:0{1}b}".format( dev, 7 ), 2 ) + \
                   "{0:0{1}x}".format( batchIndex, 5 ) + "{0:0{1}x}".format( fl, 5 )
            ethSrc = ':'.join( ethS[ i: i+2 ] for i in range( 0, len( ethS ), 2 ) )
            ethD = "%02X" % int( "1" + "{0:0{1}b}".format( dev, 7 ), 2 ) + \
                   "{0:0{1}x}".format( batchIndex, 5 ) + "{0:0{1}x}".format( fl, 5 )
            ethDst = ':'.join( ethD[ i: i+2 ] for i in range( 0, len( ethD ), 2 ) )

            if appId:
                flowJson[ "appId" ] = appId

            if egressPort:
                flowJson[ 'treatment' ][ 'instructions' ].append( {
                                                        "type": "OUTPUT",
                                                        "port": egressPort } )
            if ingressPort:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                        "type": "IN_PORT",
                                                        "port": ingressPort } )
            if ethType:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                        "type": "ETH_TYPE",
                                                        "ethType": ethType } )
            if ethSrc:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                        "type": "ETH_SRC",
                                                        "mac": ethSrc } )
            if ethDst:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                        "type": "ETH_DST",
                                                        "mac": ethDst } )
            if vlan:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                        "type": "VLAN_VID",
                                                        "vlanId": vlan } )
            if mpls:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                        "type": "MPLS_LABEL",
                                                        "label": mpls } )
            if ipSrc:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                        "type": ipSrc[ 0 ],
                                                        "ip": ipSrc[ 1 ] } )
            if ipDst:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                        "type": ipDst[ 0 ],
                                                        "ip": ipDst[ 1 ] } )
            if tcpSrc:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                        "type": "TCP_SRC",
                                                        "tcpPort": tcpSrc } )
            if tcpDst:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                        "type": "TCP_DST",
                                                        "tcpPort": tcpDst } )
            if udpSrc:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                        "type": "UDP_SRC",
                                                        "udpPort": udpSrc } )
            if udpDst:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                        "type": "UDP_DST",
                                                        "udpPort": udpDst } )
            if ipProto:
                flowJson[ 'selector' ][ 'criteria' ].append( {
                                                        "type": "IP_PROTO",
                                                        "protocol": ipProto } )
            flowJsonList.append( flowJson )

        main.log.info( self.name + ": Number of flows in batch: " + str( len( flowJsonList ) ) )
        flowJsonBatch[ 'flows' ] = flowJsonList

        return flowJsonBatch

    def sendFlowBatch( self, batch={}, ip="DEFAULT", port="DEFAULT", debug=False ):
        """
        Description:
            Sends a single flow batch through /flows REST API.
        Required:
            * The batch of flows
        Returns:
            Returns main.TRUE for successful requests; Returns main.FALSE
            if error on requests;
            Returns None for exceptions
        NOTE:
            The ip and port option are for the requests input's ip and port
            of the ONOS node
        """

        try:
            if debug:
                main.log.debug( self.name + ": Adding flow: " + self.pprint( batch ) )
            response = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            url = "/flows/"
            response = self.send( method="POST",
                                  url=url, ip = ip, port = port,
                                  data=json.dumps( batch ) )
            # main.log.info("Post response is: ", str(response[0]))
            if response[ 0 ] == 200:
                main.log.info( self.name + ": Successfully POST flow batch" )
                return main.TRUE, response
            else:
                main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                return main.FALSE, response
        except NotImplementedError as e:
            raise e  # Inform the caller
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None, None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def removeFlowBatch( self, batch={},
                         ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Remove a batch of flows
        Required:
            flow batch
        Return:
            Returns main.TRUE if successfully deletes flows, otherwise
            Returns main.FALSE, Returns None on error
        """
        try:
            response = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            # NOTE: REST url requires the intent id to be in decimal form

            response = self.send( method="DELETE",
                                  url="/flows/", ip = ip, port = port,
                                  data = json.dumps( batch ) )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    return main.TRUE
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getTopology( self, topologyOutput ):
        """
        Definition:
            Loads a json topology output
        Return:
            topology = current ONOS topology
        """
        import json
        try:
            # either onos:topology or 'topology' will work in CLI
            topology = json.loads( topologyOutput )
            main.log.debug( topology )
            return topology
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def checkStatus(
            self,
            numswitch,
            numlink,
            logLevel="info" ):
        """
        Checks the number of switches & links that ONOS sees against the
        supplied values. By default this will report to main.log, but the
        log level can be specific.

        Params: numswitch = expected number of switches
                numlink = expected number of links
                logLevel = level to log to.
                Currently accepts 'info', 'warn' and 'report'

        Returns: main.TRUE if the number of switches and links are correct,
                 main.FALSE if the number of switches and links is incorrect,
                 and main.ERROR otherwise
        """
        try:
            topology = self.getTopology( self.topology() )
            # summary = self.summary()
            if topology == {}:
                return main.ERROR
            output = ""
            # Is the number of switches is what we expected
            devices = topology.get( 'devices', False )
            links = topology.get( 'links', False )
            if devices is False or links is False:
                return main.ERROR
            switchCheck = ( int( devices ) == int( numswitch ) )
            # Is the number of links is what we expected
            linkCheck = ( int( links ) == int( numlink ) )
            if switchCheck and linkCheck:
                # We expected the correct numbers
                output = output + "The number of links and switches match "\
                    + "what was expected"
                result = main.TRUE
            else:
                output = output + \
                    "The number of links and switches does not match " + \
                    "what was expected"
                result = main.FALSE
            output = output + "\n ONOS sees %i devices" % int( devices )
            output = output + " (%i expected) " % int( numswitch )
            output = output + "and %i links " % int( links )
            output = output + "(%i expected)" % int( numlink )
            if logLevel == "report":
                main.log.report( output )
            elif logLevel == "warn":
                main.log.warn( output )
            else:
                main.log.info( output )
            return result
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def addGroup( self, deviceId, groupType, bucketList, appCookie, groupId,
                  ip="DEFAULT", port="DEFAULT", debug=False ):
        """
        Description:
            Creates a single Group for the specified device.
        Required:
            * deviceId: id of the device
            * type: Type of the Group
            * bucketList: Buckets to be added to the group
            * appCookie: Cookie for the Group
            * groupId: Id of the Group
        Returns:
            Returns main.TRUE for successful requests; Returns main.FALSE
            if error on requests;
            Returns None for exceptions
        Note:
            The ip and port option are for the requests input's ip and port
            of the ONOS node
        """
        try:
            groupJson = { "type": groupType,
                          "appCookie": appCookie,
                          "groupId": groupId,
                          "buckets": bucketList
                          }
            return self.sendGroup( deviceId=deviceId, groupJson=groupJson, ip="DEFAULT", port="DEFAULT", debug=False )

        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def sendGroup( self, deviceId, groupJson, ip="DEFAULT", port="DEFAULT", debug=False ):
        """
        Description:
            Sends a single group to the specified device.
        Required:
            * deviceId: id of the device
            * groupJson: the group in json
        Returns:
            Returns main.TRUE for successful requests; Returns main.FALSE
            if error on requests;
            Returns None for exceptions
        NOTE:
            The ip and port option are for the requests input's ip and port
            of the ONOS node
        """
        try:
            if debug:
                main.log.debug( self.name + ": Adding group: " + self.pprint( groupJson ) )
            response = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            url = "/groups/" + deviceId
            response = self.send( method="POST",
                                  url=url, ip = ip, port = port,
                                  data=json.dumps( groupJson ) )
            if response:
                if "201" in str( response[ 0 ] ):
                    main.log.info( self.name + ": Successfully POST group " +
                                   "in device: " + str( deviceId ) )
                    return main.TRUE
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except NotImplementedError as e:
            raise e  # Inform the caller
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getGroups( self, deviceId=None, appCookie=None, ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Get all the groups or get a specific group by giving the
            deviceId and appCookie
        Optional:
            * deviceId: id of the Device
            * appCookie: Cookie of the Group
        Returns:
            Returns Groups for successful requests; Returns main.FALSE
            if error on requests;
            Returns None for exceptions
        NOTE:
            The ip and port option are for the requests input's ip and port
            of the ONOS node
        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            url = "/groups"
            if deviceId:
                url += "/" + deviceId
                if appCookie:
                    url += "/" + appCookie
            response = self.send( url=url, ip = ip, port = port )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    output = response[ 1 ]
                    groupsJson = json.loads( output ).get( 'groups' )
                    assert groupsJson is not None, "Error parsing json object"
                    groups = json.dumps( groupsJson )
                    return groups
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, AssertionError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def removeGroup( self, deviceId, appCookie,
                       ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Removes specific device group
        Required:
            * deviceId: id of the Device
            * appCookie: Cookie of the Group
        Returns:
            Returns main.TRUE for successful requests; Returns main.FALSE
            if error on requests;
            Returns None for exceptions
        NOTE:
            The ip and port option are for the requests input's ip and port
            of the ONOS node

        """
        try:
            response = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            query = "/" + str( deviceId ) + "/" + str( appCookie )
            response = self.send( method="DELETE",
                                  url="/groups" + query, ip = ip, port = port )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    return main.TRUE
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def portstats( self, ip="DEFAULT", port="DEFAULT" ):
        """
        Description:
            Gets the portstats for each port in ONOS
        Returns:
            A list of dicts containing device id and a list of dicts containing the
            port statistics for each port.
            Returns main.FALSE if error on request;
            Returns None for exception
        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            response = self.send( url="/statistics/ports", ip = ip, port = port )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    output = response[ 1 ]
                    a = json.loads( output ).get( 'statistics' )
                    assert a is not None, "Error parsing json object"
                    b = json.dumps( a )
                    return b
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, AssertionError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getSlices( self, ip="DEFAULT", port="DEFAULT", debug=False ):
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            url = "/fabrictna/slicing/slice"
            response = self.send( url=url, ip = ip, port = port, base="/onos" )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    output = response[ 1 ]
                    if debug:
                        main.log.debug(self.name + ": read: " + output)
                    slices = json.loads( output ).get( 'Slices' )
                    assert slices is not None, "Error parsing json object"
                    return json.dumps( slices )
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, AssertionError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def getTrafficClasses( self, slice_id, ip="DEFAULT", port="DEFAULT", debug=False ):
        try:
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            url = "/fabrictna/slicing/tc/%d" % slice_id
            response = self.send( url=url, ip = ip, port = port, base="/onos" )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    output = response[ 1 ]
                    if debug:
                        main.log.debug(self.name + ": read: " + output)
                    traffic_classes = json.loads( output ).get( 'TrafficClasses' )
                    assert traffic_classes is not None, "Error parsing json object"
                    return json.dumps( traffic_classes )
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, AssertionError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def addSlicingClassifierFlow( self, slice_id, traffic_class, traffic_selector,
                                  ip="DEFAULT", port="DEFAULT", debug=False ):
        self.__slicingClassifierFlow( slice_id, traffic_class, traffic_selector,
                                     ip, port, debug, method="POST" )

    def removeSlicingClassifierFlow( self, slice_id, traffic_class, traffic_selector,
                                     ip="DEFAULT", port="DEFAULT", debug=False ):
        self.__slicingClassifierFlow( slice_id, traffic_class, traffic_selector,
                                     ip, port, debug, method="DELETE" )

    def getSlicingClassifierFlows( self, slice_id, traffic_class, ip="DEFAULT",
                                  port="DEFAULT", debug=False ):
        try:
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            url = "/fabrictna/slicing/flow/%d/%s" % ( slice_id, traffic_class )
            response = self.send( url=url, ip = ip, port = port, base="/onos" )
            if response:
                if 200 <= response[ 0 ] <= 299:
                    output = response[ 1 ]
                    if debug:
                        main.log.debug(self.name + ": read: " + output)
                    # FIXME: use plural in slicing service API
                    #  TrafficSelector actually points to an array of selectors.
                    traffic_selectors = json.loads( output ).get( 'TrafficSelector' )
                    assert traffic_selectors is not None, "Error parsing json object"
                    return json.dumps( traffic_selectors )
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except ( AttributeError, AssertionError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def __slicingClassifierFlow( self, slice_id, traffic_class, traffic_selector,
                                 ip="DEFAULT", port="DEFAULT", debug=False,
                                 method="POST" ):
        try:
            if debug:
                main.log.debug( self.name + ": %s Slicing Classifier Flow" % method )
                main.log.debug( self.name + ": Slice ID: %d, Traffic Class: %s, Traffic Selector: %s" % (
                    slice_id, traffic_class, self.pprint( traffic_selector ) ) )
            if ip == "DEFAULT":
                main.log.warn( self.name + ": No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( self.name + ": No port given, reverting to port " +
                               "from topo file" )
                port = self.port
            url = "/fabrictna/slicing/flow/%d/%s" % ( slice_id, traffic_class )
            response = self.send( method=method,
                                  url=url, ip = ip, port = port,
                                  data=json.dumps( traffic_selector ),
                                  base="/onos" )
            if response:
                if "200" in str( response[ 0 ] ):
                    main.log.info( self.name + ": Successfully %s Slicing Classifier Flow for " % method +
                                   "Slice ID: %d, Traffic Class: %s" % ( slice_id, traffic_class ) )
                    return main.TRUE
                else:
                    main.log.error( "Error with REST request, response was: %s: %s" %
                                    ( response[ 0 ], response[ 1 ] ) )
                    return main.FALSE
        except NotImplementedError as e:
            raise # Inform the caller
        except ( AttributeError, TypeError ):
            main.log.exception( self.name + ": Object not as expected" )
            return None
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()
