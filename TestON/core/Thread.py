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
            '''
            if self.target is not None:
                if len(self.args) != 0:
                    self.result = self.target( *self.args )
                else:
                    self.result = self.target()
                    # FIXME: handle kwargs?
            '''
        except Exception as e:
            print "Thread-" + str( self.threadID ) + " '" + self.name + "'"\
                  ":something went wrong with " + self.target + " method"
            print e
