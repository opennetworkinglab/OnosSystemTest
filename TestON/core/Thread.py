#!/usr/bin/env python
import threading


class Thread( threading.Thread ):
    def __init__( self, target=None, threadID=None, name="", args=(),
                  kwargs={} ):
        super( Thread, self ).__init__()
        self.threadID = threadID
        self.name = name
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.result = None

    def run( self ):
        try:
            if self.target is not None:
                self.result = self.target( *self.args, **self.kwargs )
        except Exception as e:
            print "ThreadID:" + str( self.threadID ) + ", Name:" +\
                  self.name + "- something went wrong with " +\
                  str( self.target.im_class ) + "." +\
                  str( self.target.im_func ) + " method: "
            print e
