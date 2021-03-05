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
        # TODO use repr() for components?
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
        if hasattr( self.REST, name ):
            main.log.debug( "%s: Using Rest driver's attribute for '%s'" % ( self.name, name ) )
            return getattr( self.REST, name )
        if hasattr( self.CLI, name ):
            main.log.debug( "%s: Using CLI driver's attribute for '%s'" % ( self.name, name ) )
            return getattr( self.CLI, name )
        if hasattr( self.Bench, name ):
            main.log.debug( "%s: Using Bench driver's attribute for '%s'" % ( self.name, name ) )
            return getattr( self.Bench, name )
        raise AttributeError( "Could not find the attribute %s in %r or it's component handles" % ( name, self ) )

    def __init__( self, name, ipAddress, CLI=None, REST=None, Bench=None, pos=None,
                  userName=None, server=None, k8s=None, dockerPrompt=None ):
        # TODO: validate these arguments
        self.name = str( name )
        self.ipAddress = ipAddress
        self.CLI = CLI
        self.REST = REST
        self.Bench = Bench
        self.active = False
        self.pos = pos
        self.ip_address = ipAddress
        self.user_name = userName
        self.server = server
        self.k8s = k8s
        self.dockerPrompt = dockerPrompt

class OnosClusterDriver( CLI ):

    def __init__( self ):
        """
        Initialize client
        """
        self.name = None
        self.home = None
        self.handle = None
        self.useDocker = False
        self.dockerPrompt = None
        self.maxNodes = None
        self.karafPromptPass = None
        self.kubeConfig = None
        self.karafPromptUser = None
        self.nodes = []
        super( OnosClusterDriver, self ).__init__()

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
                    self.home = self.options[ key ]
                elif key == "karaf_username":
                    self.karafUser = self.options[ key ]
                elif key == "karaf_password":
                    self.karafPass = self.options[ key ]
                elif key == "node_username":
                    self.nodeUser = self.options[ key ]
                elif key == "node_password":
                    self.nodePass = self.options[ key ]
                elif key == "karafPrompt_username":
                    self.karafPromptUser = self.options[ key ]
                elif key == "karafPrompt_password":
                    self.karafPromptPass = self.options[ key ]
                elif key == "cluster_name":
                    prefix = self.options[ key ]
                elif key == "useDocker":
                    self.useDocker = "True" == self.options[ key ]
                elif key == "docker_prompt":
                    self.dockerPrompt = self.options[ key ]
                elif key == "web_user":
                    self.webUser = self.options[ key ]
                elif key == "web_pass":
                    self.webPass = self.options[ key ]
                elif key == "nodes":
                    # Maximum number of ONOS nodes to run, if there is any
                    self.maxNodes = self.options[ key ]
                elif key == "kubeConfig":
                    self.kubeConfig = self.options[ key ]

            self.home = self.checkOptions( self.home, "~/onos" )
            self.karafUser = self.checkOptions( self.karafUser, self.user_name )
            self.karafPass = self.checkOptions( self.karafPass, self.pwd )
            self.nodeUser = self.checkOptions( self.nodeUser, self.user_name )
            self.nodePass = self.checkOptions( self.nodePass, self.pwd )
            self.karafPromptUser = self.checkOptions( self.karafPromptUser, self.user_name )
            self.karafPromptPass = self.checkOptions( self.karafPromptPass, self.pwd )
            self.webUser = self.checkOptions( self.webUser, "onos" )
            self.webPass = self.checkOptions( self.webPass, "rocks" )
            prefix = self.checkOptions( prefix, "ONOS" )
            self.useDocker = self.checkOptions( self.useDocker, False )
            self.dockerPrompt = self.checkOptions( self.dockerPrompt, "~/onos#" )
            self.maxNodes = int( self.checkOptions( self.maxNodes, 100 ) )
            self.kubeConfig = self.checkOptions( self.kubeConfig, None )

            self.name = self.options[ 'name' ]


            if not self.kubeConfig:
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
                if self.kubeConfig:
                    # Try to get # of onos nodes using given kubernetes configuration
                    names = self.kubectlGetPodNames( self.kubeConfig,
                                                     main.params[ 'kubernetes' ][ 'namespace' ],
                                                     main.params[ 'kubernetes' ][ 'appName' ] )
                    self.podNames = names
                    self.onosIps = {}  # Dictionary of all possible ONOS ip
                    for i in range( 1, len( names ) + 1 ):
                        self.onosIps[ 'OC%i' % i ] = self.ip_address
                    self.maxNodes = len( names )
                self.createComponents( prefix=prefix )
                if self.kubeConfig:
                    # Create Port Forwarding sessions for each controller
                    for node in self.nodes:
                        kubectl = node.k8s
                        index = self.nodes.index( node )
                        # Store each pod name in the k8s component
                        kubectl.podName = self.podNames[ index ]
                        # Setup port-forwarding and save the local port
                        guiPort = 8181
                        cliPort = 8101
                        portsList = ""
                        for port in [ guiPort, cliPort ]:
                            localPort = port + index + 1
                            portsList += "%s:%s " % ( localPort, port )
                            if port == cliPort:
                                node.CLI.karafPort = localPort
                            elif port == guiPort:
                                node.REST.port = localPort
                        main.log.info( "Setting up port forward for pod %s: [ %s ]" % ( self.podNames[ index ], portsList ) )
                        pf = kubectl.kubectlPortForward( self.podNames[ index ],
                                                         portsList,
                                                         kubectl.kubeConfig,
                                                         main.params[ 'kubernetes' ][ 'namespace' ] )
                        if not pf:
                            main.log.error( "Failed to create port forwarding" )
                            return main.FALSE
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
        home = main.componentDictionary[name]['COMPONENTS'].get( "onos_home", None )
        main.componentDictionary[name]['home'] = self.checkOptions( home, None )
        main.componentDictionary[name]['type'] = "OnosCliDriver"
        main.componentDictionary[name]['COMPONENTS']['karafPromptUser'] = self.karafPromptUser
        main.componentDictionary[name]['connect_order'] = str( int( main.componentDictionary[name]['connect_order'] ) + 1 )

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
        user = main.componentDictionary[name]['COMPONENTS'].get( "web_user", "onos" )
        main.componentDictionary[name]['user'] = self.checkOptions( user, "onos" )
        password = main.componentDictionary[name]['COMPONENTS'].get( "web_pass", "rocks" )
        main.componentDictionary[name]['password'] = self.checkOptions( password, "rocks" )
        main.componentDictionary[name]['host'] = host
        port = main.componentDictionary[name]['COMPONENTS'].get( "rest_port", "8181" )
        main.componentDictionary[name]['port'] = self.checkOptions( port, "8181" )
        main.componentDictionary[name]['type'] = "OnosRestDriver"
        main.componentDictionary[name]['connect_order'] = str( int( main.componentDictionary[name]['connect_order'] ) + 1 )

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

    def setServerOptions( self, name, ipAddress ):
        """
        Parse the cluster options to create an ONOS "server" component with the given name

        Arguments:
            name - The name of the server componet
            ipAddress - The ip address of the server
        """
        main.componentDictionary[name] = main.componentDictionary[self.name].copy()
        main.componentDictionary[name]['type'] = "OnosDriver"
        main.componentDictionary[name]['host'] = ipAddress
        home = main.componentDictionary[name]['COMPONENTS'].get( "onos_home", None )
        main.componentDictionary[name]['home'] = self.checkOptions( home, None )
        # TODO: for now we use karaf user name and password also for logging to the onos nodes
        # FIXME: We shouldn't use karaf* for this, what we want is another set of variables to
        #        login to a shell on the server ONOS is running on
        main.componentDictionary[name]['user'] = self.nodeUser
        main.componentDictionary[name]['password'] = self.nodePass
        main.componentDictionary[name]['connect_order'] = str( int( main.componentDictionary[name]['connect_order'] ) + 1 )

    def createServerComponent( self, name, ipAddress ):
        """
        Creates a new onos "server" component. This will be connected to the
        node ONOS is running on.

        Arguments:
            name - The string of the name of this component. The new component
                   will be assigned to main.<name> .
                   In addition, main.<name>.name = str( name )
            ipAddress - The ip address of the server
        """
        try:
            # look to see if this component already exists
            getattr( main, name )
        except AttributeError:
            # namespace is clear, creating component
            self.setServerOptions( name, ipAddress )
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

    def createComponents( self, prefix='', createServer=True ):
        """
        Creates a CLI and REST component for each nodes in the cluster
        """
        # TODO: This needs work to support starting two seperate clusters in one test
        cliPrefix = prefix + "cli"
        restPrefix = prefix + "rest"
        benchPrefix = prefix + "bench"
        serverPrefix = prefix + "server"
        k8sPrefix = prefix + "k8s"
        for i in xrange( 1, self.maxNodes + 1 ):
            cliName = cliPrefix + str( i  )
            restName = restPrefix + str( i )
            benchName = benchPrefix + str( i )
            serverName = serverPrefix + str( i )
            if self.kubeConfig:
                k8sName = k8sPrefix + str( i )

            # Unfortunately this means we need to have a cell set beofre running TestON,
            # Even if it is just the entire possible cluster size
            ip = self.onosIps[ 'OC' + str( i ) ]

            cli = self.createCliComponent( cliName, ip )
            rest = self.createRestComponent( restName, ip )
            bench = self.createBenchComponent( benchName )
            server = self.createServerComponent( serverName, ip ) if createServer else None
            k8s = self.createServerComponent( k8sName, ip ) if self.kubeConfig else None
            if self.kubeConfig:
                k8s.kubeConfig = self.kubeConfig
                k8s.podName = None
            self.nodes.append( Controller( prefix + str( i ), ip, cli, rest, bench, i - 1,
                                           self.user_name, server=server, k8s=k8s,
                                           dockerPrompt=self.dockerPrompt ) )
