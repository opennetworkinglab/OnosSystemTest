"""
Copyright 2016 Open Networking Foundation ( ONF )

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    ( at your option ) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.
"""
class Utils:

    def __init__( self ):
        self.default = ''

    def mininetCleanIntro( self, includeCaseDesc=True ):
        """
        Description:
            Introduction information of the mininet clean up
        Required:
        Returns:
        """
        main.log.report( "Stop Mininet" )
        if includeCaseDesc:
            main.case( "Stop Mininet" )
            main.caseExplanation = "Stopping the current mininet to start up fresh"

    def mininetCleanup( self, Mininet, timeout=5, exitTimeout=1000 ):
        """
        Description:
            Clean up the mininet using stopNet and verify it.
        Required:
            * Mininet - mininet driver to use
            * timeout - time out of mininet.stopNet.
        Returns:
            Returns main.TRUE if successfully stopping minient.
            else returns main.FALSE
        """
        main.step( "Stopping Mininet" )
        topoResult = Mininet.stopNet( timeout=timeout, exitTimeout=exitTimeout )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=topoResult,
                                 onpass="Successfully stopped mininet",
                                 onfail="Failed to stopped mininet" )
        return topoResult

    def copyKarafLog( self, copyFileName="", before=False, includeCaseDesc=True ):
        """
        Description:
            copy the karaf log and verify it.
        Required:
            * copyFileName - name of the end portion of the
            copyFileName.
        Returns:
        """
        # TODO: Also grab the rotated karaf logs
        main.log.report( "Copy karaf logs" )
        if includeCaseDesc:
            main.case( "Copy karaf logs" )
            main.caseExplanation = "Copying the karaf logs to preserve them through" +\
                                   "reinstalling ONOS"
        main.step( "Copying karaf logs" )
        stepResult = main.TRUE
        scpResult = main.TRUE
        copyResult = main.TRUE
        for ctrl in main.Cluster.runningNodes:
            scpResult = scpResult and main.ONOSbench.scp( ctrl,
                                                          "/opt/onos/log/karaf.log",
                                                          "/tmp/karaf.log",
                                                          direction="from" )
            copyResult = copyResult and main.ONOSbench.cpLogsToDir( "/tmp/karaf.log", main.logdir,
                                                                    copyFileName=( copyFileName + "_karaf.log." +
                                                                                   ctrl.name + "_" ) if before else
                                                                                 ( "karaf.log." + ctrl.name +
                                                                                    "." + copyFileName ) )
            if scpResult and copyResult:
                stepResult = main.TRUE and stepResult
            else:
                stepResult = main.FALSE and stepResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully copied remote ONOS logs",
                                 onfail="Failed to copy remote ONOS logs" )
