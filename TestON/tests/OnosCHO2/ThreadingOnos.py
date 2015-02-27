#!/usr/bin/env python
import threading
import time

class ThreadingOnos(threading.Thread):
    def __init__(self,target = None, threadID=None, name="", args=None):
        super(ThreadingOnos, self).__init__()
        self.threadID = threadID
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
            print "Thread-" + str(self.threadID) + ":something went wrong with " + self.name + "method"
