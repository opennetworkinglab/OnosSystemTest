#!/usr/bin/env python

import json
import os
import re
import subprocess
from docker import Client
from drivers.common.apidriver import API

class DockerApiDriver( API ):

    def __init__( self ):
        """
        Initialize client
        """
        self.name = None
        self.home = None
        self.handle = None
        super( API, self ).__init__()

    def connect( self, **connectargs ):
        """
        Create Client handle to connnect to Docker server
        """
        try:
            for key in connectargs:
                vars( self )[ key ] = connectargs[ key ]
            self.name = self.options[ 'name' ]
            for key in self.options:
                if key == "home":
                    self.home = self.options[ 'home' ]
                    break
            if self.home is None or self.home == "":
                self.home = "/var/tmp"

            self.handle = super( DockerApiDriver, self ).connect()
            self.dockerClient = Client(base_url='unix://var/run/docker.sock')
            return self.handle
        except Exception as e:
            main.log.exception( e )

    def dockerPull( self, image="onosproject/onos", tag="latest" ):
        """
        Pulls Docker image from repository
        """
        try:
            main.log.info( self.name +
                           ": Pulling Docker image " + image + ":"+tag )
            for line in self.dockerClient.pull( repository=image, \
                    tag=tag, stream=True ):
                response = json.dumps( json.loads( line ), indent=4 )
            if( re.search( "Downloaded", response ) ):
                return main.TRUE
            else:
                main.log.error( "Failed to download image: " + image +":"+ tag )
                main.log.error( "Error respone: " )
                main.log.error( response )
                return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def dockerRun( self, image="onosproject/onos", node="onos1" ):
        """
            Run specified Docker container
        """
        try:
            main.log.info( self.name +
                           ": Creating Docker conatiner for node " + node )
            reponse = self.dockerClient.create_container( image=image, \
                    tty=True, hostname=node, detach=True )
            if( reponse['Warnings'] == 'None' ):
                main.log.info( "Created container for node: " + node )
                return main.TRUE
            else:
                main.log.info( "Noticed warnings during create" )
                return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def dockerStart( self, node="onos1" ):
        """
            Start Docker container
        """
        try:
            main.log.info( self.name +
                           ": Starting Docker conatiner for node " + node )
            reponse = self.dockerClient.start( node )
            if( reponse == 'None' ):
                main.log.info( "Started container for node: " + node )
                return main.TRUE
            else:
                main.log.info( "Noticed warnings during start" )
                return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def dockerStop( self, node="onos1" ):
        """
            Stop docker container
        """
        try:
            main.log.info( self.name +
                           ": Stopping Docker conatiner for node " + node )
            reponse = self.dockerClient.stop( node )
            if( reponse == 'None' ):
                main.log.info( "Stopped container for node: " + node )
                return main.TRUE
            else:
                main.log.info( "Noticed warnings during stop" )
                return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def dockerRestart( self, node="onos1" ):
        """
            Restart Docker container
        """
        try:
            main.log.info( self.name +
                           ": Restarting Docker conatiner for node " + node )
            reponse = self.dockerClient.restart( node )
            if( reponse == 'None' ):
                main.log.info( "Restarted container for node: " + node )
                return main.TRUE
            else:
                main.log.info( "Noticed warnings during Restart" )
                return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def dockerStatus( self, node="onos1" ):
        """
            Check Docker conatiner status
        """
        try:
            main.log.info( self.name +
                           ": Checking Docker Status for node " + node )
            reponse = self.dockerClient.inspect_container( node )
            if( reponse == 'True' ):
                main.log.info( "Container " + node + " is running" )
                return main.TRUE
            else:
                main.log.info( "Container " + node + " is not running" )
                return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def dockerRemove( self, node="onos1" ):
        """
            Remove Docker conatiner
        """
        try:
            main.log.info( self.name +
                           ": Removing Docker container for node " + node )
            reponse = self.dockerClient.remove_container( node )
            if( reponse == 'None' ):
                main.log.info( "Removed container for node: " + node )
                return main.TRUE
            else:
                main.log.info( "Noticed warnings during Remove " + node )
                return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def dockerImageRemove( self, image="onosproject/onos" ):
        """
            Remove Docker image
        """
        try:
            main.log.info( self.name +
                           ": Removing Docker container for node " + node )
            reponse = self.dockerClient.remove_image( image )
            if( reponse == 'None' ):
                main.log.info( "Removed Docker image: " + image )
                return main.TRUE
            else:
                main.log.info( "Noticed warnings during Remove " + image )
                return main.FALSE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def fetchLatestClusterFile( self, branch="master" ):
        """
            Fetch onos-form-cluster file from a particular branch
        """
        try:
            command = "wget -N https://raw.githubusercontent.com/opennetworkinglab/\
                    onos/" + branch + "/tools/package/bin/onos-form-cluster"
            subprocess.call( command ) # output checks are missing for now
            command = "chmod u+x " + "onos-form-cluster"
            subprocess.call( command )
            return main.TRUE
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def onosFormCluster( self, onosIPs, user="onos", passwd="rocks" ):
        """
            From ONOS cluster for IP addresses in onosIPs list
        """
        try:
            onosIPs = " ".join(onosIPs)
            command = "./onos-form-cluster -u " + user + " -p " + passwd + \
                    " `" + onosIPs + "`"
            subprocess.call( command ) # output checks are missing for now
            return main.TRUE # FALSE condition will be verified from output
        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()

    def dockerIP( self, node='onos1' ):
        """
            Fetch IP address assigned to specified node/container
        """
        try:
            output = self.dockerClient.inspect_container(node)
            nodeIP = output['NetworkSettings']['IPAddress']
            #main.log.info( " Docker IP " + str(nodeIP) )
            return str(nodeIP)

        except Exception:
            main.log.exception( self.name + ": Uncaught exception!" )
            main.cleanup()
            main.exit()
