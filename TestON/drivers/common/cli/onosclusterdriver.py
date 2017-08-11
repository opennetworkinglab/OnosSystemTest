#!/usr/bin/env python
"""
Copyright 2017 Open Networking Foundation (ONF)

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


This driver is used to interact with an ONOS cluster. It should
handle creating the necessary components to interact with each specific ONOS nodes.

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

"""
import pexpect
import os
from drivers.common.clidriver import CLI

# FIXME: Move this to it's own file?
class Controller():
    def __str__( self ):
        return self.name
    def __repr__( self ):
        #TODO use repr() for components?
        return "%s<IP=%s, CLI=%s, REST=%s, Bench=%s >" % ( self.name,
                                                          self.ipAddress,
                                                          self.CLI,
                                                          self.REST,
                                                          self.Bench )

    def __getattr__( self, name ):
        """
        Called when an attribute lookup has not found the attribute
        in the usual places (i.e. it is not an instance attribute nor
        is it found in the class tree for self). name is the attribute
        name. This method should return the (computed) attribute value
        or raise an AttributeError exception.

        We will look into each of the node's component handles to try to find the attreibute, looking at REST first
        """
        usedDriver = False
        if hasattr( self.REST, name ):
            main.log.warn( "Rest driver has attribute '%s'" % ( name ) )
            if not usedDriver:
                usedDriver = True
                main.log.debug("Using Rest driver's attribute for '%s'" % (name))
                f = getattr( self.REST, name)
        if hasattr( self.CLI, name ):
            main.log.warn( "CLI driver has attribute '%s'" % ( name ) )
            if not usedDriver:
                usedDriver = True
                main.log.debug("Using CLI driver's attribute for '%s'" % (name))
                f = getattr( self.CLI, name)
        if hasattr( self.Bench, name ):
            main.log.warn( "Bench driver has attribute '%s'" % ( name ) )
            if not usedDriver:
                usedDriver = True
                main.log.debug("Using Bench driver's attribute for '%s'" % (name))
                f = getattr( self.Bench, name)
        if usedDriver:
            return f
        raise AttributeError( "Could not find the attribute %s in %r or it's component handles" % ( name, self ) )



    def __init__( self, name, ipAddress, CLI=None, REST=None, Bench=None, pos=None, userName=None ):
        #TODO: validate these arguments
        self.name = str( name )
        self.ipAddress = ipAddress
        self.CLI = CLI
        self.REST = REST
        self.Bench = Bench
        self.active = False
        self.pos = pos
        self.ip_address = ipAddress
        self.user_name = userName

class OnosClusterDriver( CLI ):

    def __init__( self ):
        """
        Initialize client
        """
        self.name = None
        self.home = None
        self.handle = None
        self.nodes = []
        super( OnosClusterDriver, self ).__init__()

    def checkOptions( self, var, defaultVar ):
        if var is None or var == "":
            return defaultVar
        return var

    def connect( self, **connectargs ):
        """
        Creates ssh handle for ONOS "bench".
        NOTE:
        The ip_address would come from the topo file using the host tag, the
        value can be an environment variable as well as a "localhost" to get
        the ip address needed to ssh to the "bench"
        """
        try:
            for key in connectargs:
                vars( self )[ key ] = connectargs[ key ]
            self.home = "~/onos"
            for key in self.options:
                if key == "home":
                    self.home = self.options[ 'home' ]
                elif key == "karaf_username":
                    self.karafUser = self.options[ key ]
                elif key == "karaf_password":
                    self.karafPass = self.options[ key ]
                elif key == "cluster_name":
                    prefix = self.options[ key ]

            self.home = self.checkOptions(self.home, "~/onos")
            self.karafUser = self.checkOptions(self.karafUser, self.user_name)
            self.karafPass = self.checkOptions(self.karafPass, self.pwd )
            prefix = self.checkOptions( prefix, "ONOS" )

            self.name = self.options[ 'name' ]

            # The 'nodes' tag is optional and it is not required in .topo file
            for key in self.options:
                if key == "nodes":
                    # Maximum number of ONOS nodes to run, if there is any
                    self.maxNodes = int( self.options[ 'nodes' ] )
                    break
                self.maxNodes = None

            if self.maxNodes is None or self.maxNodes == "":
                self.maxNodes = 100

            # Grabs all OC environment variables based on max number of nodes
            # TODO: Also support giving an ip range as a compononet option
            self.onosIps = {}  # Dictionary of all possible ONOS ip

            try:
                if self.maxNodes:
                    for i in range( self.maxNodes ):
                        envString = "OC" + str( i + 1 )
                        # If there is no more OC# then break the loop
                        if os.getenv( envString ):
                            self.onosIps[ envString ] = os.getenv( envString )
                        else:
                            self.maxNodes = len( self.onosIps )
                            main.log.info( self.name +
                                           ": Created cluster data with " +
                                           str( self.maxNodes ) +
                                           " maximum number" +
                                           " of nodes" )
                            break

                    if not self.onosIps:
                        main.log.info( "Could not read any environment variable"
                                       + " please load a cell file with all" +
                                        " onos IP" )
                        self.maxNodes = None
                    else:
                        main.log.info( self.name + ": Found " +
                                       str( self.onosIps.values() ) +
                                       " ONOS IPs" )
            except KeyError:
                main.log.info( "Invalid environment variable" )
            except Exception as inst:
                main.log.error( "Uncaught exception: " + str( inst ) )

            try:
                if os.getenv( str( self.ip_address ) ) is not None:
                    self.ip_address = os.getenv( str( self.ip_address ) )
                else:
                    main.log.info( self.name +
                                   ": Trying to connect to " +
                                   self.ip_address )
            except KeyError:
                main.log.info( "Invalid host name," +
                               " connecting to local host instead" )
                self.ip_address = 'localhost'
            except Exception as inst:
                main.log.error( "Uncaught exception: " + str( inst ) )

            self.handle = super( OnosClusterDriver, self ).connect(
                user_name=self.user_name,
                ip_address=self.ip_address,
                port=self.port,
                pwd=self.pwd,
                home=self.home )

            if self.handle:
                self.handle.sendline( "cd " + self.home )
                self.handle.expect( "\$" )
                self.createComponents( prefix=prefix )
                return self.handle
            else:
                main.log.info( "Failed to create ONOS handle" )
                return main.FALSE
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()

    def disconnect( self ):
        """
        Called when Test is complete to disconnect the ONOS handle.
        """
        response = main.TRUE
        try:
            if self.handle:
                self.handle.sendline( "" )
                self.handle.expect( "\$" )
                self.handle.sendline( "exit" )
                self.handle.expect( "closed" )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
        except ValueError:
            main.log.exception( "Exception in disconnect of " + self.name )
            response = main.TRUE
        except Exception:
            main.log.exception( self.name + ": Connection failed to the host" )
            response = main.FALSE
        return response

    def setCliOptions( self, name, host ):
        """
        Parse the cluster options to create an ONOS cli component with the given name
        """
        main.componentDictionary[name] = main.componentDictionary[self.name].copy()
        clihost = main.componentDictionary[ name ][ 'COMPONENTS' ].get( "diff_clihost", "" )
        if clihost == "True":
            main.componentDictionary[ name ][ 'host' ] = host
        main.componentDictionary[name]['type'] = "OnosCliDriver"
        main.componentDictionary[name]['connect_order'] = str( int( main.componentDictionary[name]['connect_order'] ) + 1 )
        main.log.debug( main.componentDictionary[name] )

    def createCliComponent( self, name, host ):
        """
        Creates a new onos cli component.

        Arguments:
            name - The string of the name of this component. The new component
                   will be assigned to main.<name> .
                   In addition, main.<name>.name = str( name )
        """
        try:
            # look to see if this component already exists
            getattr( main, name )
        except AttributeError:
            # namespace is clear, creating component
            self.setCliOptions( name, host )
            return main.componentInit( name )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()
        else:
            # namespace is not clear!
            main.log.error( name + " component already exists!" )
            main.cleanAndExit()

    def setRestOptions( self, name, host ):
        """
        Parse the cluster options to create an ONOS cli component with the given name
        """
        main.componentDictionary[name] = main.componentDictionary[self.name].copy()
        main.log.debug( main.componentDictionary[name] )
        user = main.componentDictionary[name]['COMPONENTS'].get( "web_user", "onos" )
        main.componentDictionary[name]['user'] = self.checkOptions( user, "onos" )
        password = main.componentDictionary[name]['COMPONENTS'].get( "web_pass", "rocks" )
        main.componentDictionary[name]['pass'] = self.checkOptions( password, "rocks" )
        main.componentDictionary[name]['host'] = host
        port = main.componentDictionary[name]['COMPONENTS'].get( "rest_port", "8181" )
        main.componentDictionary[name]['port'] = self.checkOptions( port, "8181" )
        main.componentDictionary[name]['type'] = "OnosRestDriver"
        main.componentDictionary[name]['connect_order'] = str( int( main.componentDictionary[name]['connect_order'] ) + 1 )
        main.log.debug( main.componentDictionary[name] )

    def createRestComponent( self, name, ipAddress ):
        """
        Creates a new onos rest component.

        Arguments:
            name - The string of the name of this component. The new component
                   will be assigned to main.<name> .
                   In addition, main.<name>.name = str( name )
        """
        try:
            # look to see if this component already exists
            getattr( main, name )
        except AttributeError:
            # namespace is clear, creating component
            self.setRestOptions( name, ipAddress )
            return main.componentInit( name )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()
        else:
            # namespace is not clear!
            main.log.error( name + " component already exists!" )
            main.cleanAndExit()

    def setBenchOptions( self, name ):
        """
        Parse the cluster options to create an ONOS "bench" component with the given name
        """
        main.componentDictionary[name] = main.componentDictionary[self.name].copy()
        main.componentDictionary[name]['type'] = "OnosDriver"
        home = main.componentDictionary[name]['COMPONENTS'].get( "onos_home", None )
        main.componentDictionary[name]['home'] = self.checkOptions( home, None )
        main.componentDictionary[name]['connect_order'] = str( int( main.componentDictionary[name]['connect_order'] ) + 1 )
        main.log.debug( main.componentDictionary[name] )

    def createBenchComponent( self, name ):
        """
        Creates a new onos "bench" component.

        Arguments:
            name - The string of the name of this component. The new component
                   will be assigned to main.<name> .
                   In addition, main.<name>.name = str( name )
        """
        try:
            # look to see if this component already exists
            getattr( main, name )
        except AttributeError:
            # namespace is clear, creating component
            self.setBenchOptions( name )
            return main.componentInit( name )
        except pexpect.EOF:
            main.log.error( self.name + ": EOF exception found" )
            main.log.error( self.name + ":     " + self.handle.before )
            main.cleanAndExit()
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanAndExit()
        else:
            # namespace is not clear!
            main.log.error( name + " component already exists!" )
            main.cleanAndExit()

    def createComponents( self, prefix='' ):
        """
        Creates a CLI and REST component for each nodes in the cluster
        """
        # TODO: This needs work to support starting two seperate clusters in one test
        cliPrefix = prefix + "cli"
        restPrefix = prefix + "rest"
        benchPrefix = prefix + "bench"
        #self.nodes = []
        for i in xrange( 1, self.maxNodes + 1 ):
            cliName = cliPrefix + str( i  )
            restName = restPrefix + str( i )
            benchName = benchPrefix + str( i )

            # Unfortunately this means we need to have a cell set beofre running TestON,
            # Even if it is just the entire possible cluster size
            ip = self.onosIps[ 'OC' + str( i ) ]

            cli = self.createCliComponent( cliName, ip )
            rest = self.createRestComponent( restName, ip )
            bench = self.createBenchComponent( benchName )
            self.nodes.append( Controller( prefix + str( i ), ip, cli, rest, bench, i - 1, self.user_name ) )