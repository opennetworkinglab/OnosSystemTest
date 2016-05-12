"""
This file contains intent class for CHOTestMonkey
Author: you@onlab.us
"""
from threading import Lock

class Controller:
    def __init__( self, index ):
        self.default = ''
        self.index = index
        self.ip = main.onosIPs[ index - 1 ]
        self.CLI = None
        self.CLILock = Lock()
        self.status = 'up'

    def setCLI( self, CLI ):
        self.CLI = CLI

    def startCLI( self ):
        return self.CLI.startOnosCli( self.ip )

    def isUp( self ):
        return self.status == 'up'

    def bringDown( self ):
        self.status = 'down'

    def bringUp( self ):
        self.status = 'up'

class Intent:
    def __init__( self, id ):
        self.default = ''
        self.type = 'INTENT'
        self.id = id

    def isHostIntent( self ):
        return self.type == 'INTENT_HOST'

    def isPointIntent( self ):
        return self.type == 'INTENT_POINT'

class HostIntent( Intent ):
    def __init__( self, id, hostA, hostB ):
        Intent.__init__( self, id )
        self.type = 'INTENT_HOST'
        self.hostA = hostA
        self.hostB = hostB

    def __str__( self ):
        return "ID: " + self.id

class PointIntent( Intent ):
    def __init__( self, id, deviceA, deviceB ):
        Intent.__init__( self, id )
        self.type = 'INTENT_POINT'
        self.deviceA = deviceA
        self.deviceB = deviceB

    def __str__( self ):
        return "ID: " + self.id
