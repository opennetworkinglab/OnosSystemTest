#!/usr/bin/env python
import multiprocessing
import time

class ProcessOnos(multiprocessing.Process):
    def __init__(self,target = None, processID=None, name="", args=None):
        super(ProcessOnos, self).__init__()
        self.processID = processID
        self.name = name
        self.target = target
        self.args = args
        self.result = None
    def run( self ):
        try:
            print "args length = " + str(len(self.args))
            print "Running ",self.name
            if self.target is not None:
                if len(self.args) != 0:
                    self.result = self.target( *self.args )
                else: self.result = self.target()
        except:
            print "Process-" + str(self.processID) + ":something went wrong with " + self.name + "method"
