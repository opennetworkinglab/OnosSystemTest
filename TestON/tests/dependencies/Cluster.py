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
"""


class Cluster():

    def __str__( self ):
        return self.name
    def __repr__( self ):
        #TODO use repr of cli's?
        controllers = []
        for ctrl in self.controllers:
            controllers.append( str( ctrl ) )
        return "%s[%s]" % ( self.name, ", ".join( controllers ) )


    def __init__( self, ctrlList=[], name="Cluster" ):
        #assert isInstance( ctrlList, Controller ), "ctrlList should be a list of ONOS Controllers"
        self.controllers = ctrlList
        self.name = str( name )
        self.iterator = iter( self.active() )

    def getIps( self, activeOnly=False):
        ips = []
        if activeOnly:
            nodeList = self.active()
        else:
            nodeList = self.controllers
        for ctrl in nodeList:
            ips.append( ctrl.ipAddress )
        return ips

    def active( self ):
        """
        Return a list of active controllers in the cluster
        """
        return [ ctrl for ctrl in self.controllers
                      if ctrl.active ]

    def next( self ):
        """
        An iterator for the cluster's controllers that
        resets when there are no more elements.

        Returns the next controller in the cluster
        """
        try:
            return self.iterator.next()
        except StopIteration:
            self.reset()
            try:
                return self.iterator.next()
            except StopIteration:
                raise RuntimeError( "There are no active nodes in the cluster" )

    def reset( self ):
        """
        Resets the cluster iterator.

        This should be used whenever a node's active state is changed
        and is also used internally when the iterator has been exhausted.
        """
        self.iterator = iter( self.active() )

    def install( self ):
        """
        Install ONOS on all controller nodes in the cluster
        """
        result = main.TRUE
        # FIXME: use the correct onosdriver function
        # TODO: Use threads to install in parallel, maybe have an option for sequential installs
        for ctrl in self.controllers:
            result &= ctrl.installOnos( ctrl.ipAddress )
        return result

    def startCLIs( self ):
        """
        Start the ONOS cli on all controller nodes in the cluster
        """
        cliResults =  main.TRUE
        threads = []
        for ctrl in self.controllers:
            t = main.Thread( target=ctrl.CLI.startOnosCli,
                             name="startCli-" + ctrl.name,
                             args=[ ctrl.ipAddress ] )
            threads.append( t )
            t.start()
            ctrl.active = True

        for t in threads:
            t.join()
            cliResults = cliResults and t.result
        return cliResults

    def command( self, function, args=(), kwargs={} ):
        """
        Send a command to all ONOS nodes and return the results as a list
        """
        threads = []
        results = []
        for ctrl in self.active():
            f = getattr( ctrl, function )
            t = main.Thread( target=f,
                             name=function + "-" + ctrl.name,
                             args=args,
                             kwargs=kwargs )
            threads.append( t )
            t.start()

        for t in threads:
            t.join()
            results.append( t.result )
        return results
