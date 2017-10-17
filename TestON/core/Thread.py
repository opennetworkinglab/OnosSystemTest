#!/usr/bin/env python

'''
Copyright 2015 Open Networking Foundation (ONF)

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
'''
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
            print "ThreadID:" + str( self.threadID ) + ", Name:" + \
                  self.name + "- something went wrong with " + \
                  str( self.target.im_class ) + "." + \
                  str( self.target.im_func ) + " method: "
            print e
