#!/usr/bin/env python
"""
Created on 07-08-2015

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

from drivers.common.api.controllerdriver import Controller


class OnosRestDriver( Controller ):

    def __init__( self ):
        super( Controller, self ).__init__()
        self.ip_address = "localhost"
        self.port = "8080"
        self.user_name = "user"
        self.password = "CHANGEME"

    def connect( self, **connectargs ):
        try:
            for key in connectargs:
                vars( self )[ key ] = connectargs[ key ]
            self.name = self.options[ 'name' ]
        except Exception as e:
            main.log.exception( e )
        try:
            if os.getenv( str( self.ip_address ) ) != None:
                self.ip_address = os.getenv( str( self.ip_address ) )
            else:
                main.log.info( self.name + ": ip set to" + self.ip_address )
        except KeyError:
            main.log.info( "Invalid host name," +
                           "defaulting to 'localhost' instead" )
            self.ip_address = 'localhost'
        except Exception as inst:
            main.log.error( "Uncaught exception: " + str( inst ) )

        self.handle = super( OnosRestDriver, self ).connect()
        return self.handle

    def send( self, ip, port, url, base="/onos/v1", method="GET",
              query=None, data=None ):
        """
        Arguments:
            str ip: ONOS IP Address
            str port: ONOS REST Port
            str url: ONOS REST url path.
                     NOTE that this is is only the relative path. IE "/devices"
            str base: The base url for the given REST api. Applications could
                      potentially have their own base url
            str method: HTTP method type
            dict params: Dictionary to be sent in the query string for
                         the request
            dict data: Dictionary to be sent in the body of the request
        """
        # TODO: Authentication - simple http (user,pass) tuple
        # TODO: should we maybe just pass kwargs straight to response?
        # TODO: Do we need to allow for other protocols besides http?
        # ANSWER: Not yet, but potentially https with certificates
        try:
            path = "http://" + str( ip ) + ":" + str( port ) + base + url
            main.log.info( "Sending request " + path + " using " +
                           method.upper() + " method." )
            response = requests.request( method.upper(),
                                         path,
                                         params=query,
                                         data=data )
            return ( response.status_code, response.text.encode( 'utf8' ) )
        except requests.exceptions:
            main.log.exception( "Error sending request." )
            return None
        except Exception as e:
            main.log.exception( e )
            return None
        # FIXME: add other exceptions  

    def intents( self, ip="DEFAULT", port="DEFAULT" ):
        """
        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( "No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( "No port given, reverting to port from topo file" )
                port = self.port
            response = self.send( ip, port, url="/intents" )
            if response:
                main.log.debug( response )
                # We can do some verification on the return code
                # NOTE: Not all requests return 200 on success, usually it will be a 2XX code
                #       3XX is a redirction, which may be given on a post to show where the new resource can be found
                #       4XX is usually a bad request on our side
                #       5XX will usually mean an ONOS bug
                if response[0] == 200:
                    main.log.debug("all ok")
                else:
                    main.log.error( "Error with REST request, response was: " +
                                    str( response ) )
                    # return main.FALSE
                output = response[1]

            # NOTE: The output is slightly differen from the cli.
            # if data = cli's json output
            # then rest output is dict( 'intents' : data )

            # We have some options here:
            # 1) we can return the whole thing as a string as we do with cli,
            #    then change our tests to correctly parse the data
            #
            # 2) We could return just the data of the response, but we would
            #    have to decide if we return:
            # 2a) the data as a dictionary or
            # 2b) as a json string.
            #
            # If we return the dict, we probably want to change the
            #    cli drivers to match.

            # Ideally, we would be able to switch between using the api driver
            # and the cli driver by simply changing the .topo file. I don't
            # know if we will achive that right away, but we should try to plan
            # for that.


            # 1)
            '''
            return output
            '''

            # 2a)
            '''
            import json
            a = json.loads( output )
            return a.get( 'intents' )
            '''

            # 2b)
            import json
            a = json.loads( output ).get( 'intents' )
            b = json.dumps(a)
            main.log.debug( b )
            return b
        except Exception as e:
            main.log.exception( e )
            return None

    def intent( self, appId, intentId,  ip="DEFAULT", port="DEFAULT" ):
        """
        Returns a single intent in dictionary form
        """
        try:
            output = None
            if ip == "DEFAULT":
                main.log.warn( "No ip given, reverting to ip from topo file" )
                ip = self.ip_address
            if port == "DEFAULT":
                main.log.warn( "No port given, reverting to port from topo file" )
                port = self.port
            # NOTE: REST url requires the intent id to be in decimal form
            query = "/" + str( appId ) + "/" + str( int( intentId, 16 ) )
            response = self.send( ip, port, url="/intents" + query )
            if response:
                main.log.debug( response )
                # We can do some verification on the return code
                # NOTE: Not all requests return 200 on success, usually it will be a 2XX code
                #       3XX is a redirction, which may be given on a post to show where the new resource can be found
                #       4XX is usually a bad request on our side
                #       5XX will usually mean an ONOS bug
                if response[0] == 200:
                    main.log.debug("all ok")
                else:
                    main.log.error( "Error with REST request, response was: " +
                                    str( response ) )
                    # return main.FALSE
                output = response[1]
            a = json.loads( output )
            return a
        except Exception as e:
            main.log.exception( e )
            return None
