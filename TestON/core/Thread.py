#!/usr/bin/env python
import threading

class Thread(threading.Thread):
    def __init__(self, target = None, threadID=None, name="", args=(), kwargs={}):
        super(Thread, self).__init__()
        self.threadID = threadID
        self.name = name
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.result = None

    def run( self ):
        try:
            if self.target is not None:
                if len(self.args) != 0:
                    self.result = self.target( *self.args )
                else:
                    self.result = self.target()
        except Exception as e:
            print "Thread-" + str(self.threadID) + \
                  ":something went wrong with " + self.name + " method"
            print e
