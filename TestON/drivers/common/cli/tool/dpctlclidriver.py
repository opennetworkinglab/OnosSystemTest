#/usr/bin/env python
"""
Created on 26-Nov-2012

author:: Raghav Kashyap( raghavkashyap@paxterrasolutions.com )


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



DPCTL driver class provides the basic functions of DPCTL controller
"""
import sys
from drivers.common.cli.toolsdriver import Tools


class DpctlCliDriver( Tools ):

    """
     DpctlCliDriver driver class provides the basic functions of DPCTL controller
    """
    def __init__( self ):
        super( DpctlCliDriver, self ).__init__()
        self.handle = self
        self.wrapped = sys.modules[ __name__ ]

    def connect( self, **connectargs ):

        for key in connectargs:
            vars( self )[ key ] = connectargs[ key ]

        self.name = self.options[ 'name' ]

        self.handle = super(
                   DpctlCliDriver, self ).connect( user_name=self.user_name,
                   ip_address=self.ip_address,
                   port=None,
                   pwd=self.pwd )
        if self.handle:
            main.log.info( "Connected to the host" )
            return main.TRUE
        else:
            main.log.error(
                "Connection failed to the host " +
                self.user_name +
                "@" +
                self.ip_address )
            return main.FALSE

    def addFlow( self, **flowParameters ):
        """
         addFlow create a new flow entry into flow table using "dpctl"
        """
        args = utilities.parse_args( [
                                     "TCPIP",
                                     "TCPPORT",
                                     "INPORT",
                                     "ACTION",
                                     "TIMEOUT" ],
                             **flowParameters )

        cmd = "dpctl add-flow tcp:"
        tcpIP = args[ "TCPIP" ] if args[ "TCPIP" ] is not None else "127.0.0.1"
        tcpPort = args[ "TCPPORT" ] if args[
            "TCPPORT" ] is not None else "6634"
        timeOut = args[ "TIMEOUT" ] if args[ "TIMEOUT" ] is not None else 120
        cmd = cmd + tcpIP + ":" + tcpPort + " in_port=" + \
            str( args[ "INPORT" ] ) + ",idle_timeout=" + str(
                args[ "TIMEOUT" ] ) + ",actions=" + args[ "ACTION" ]
        response = self.execute( cmd=cmd, prompt="\~\$", timeout=60 )
        if utilities.assert_matches( expect="openflow", actual=response, onpass="Flow Added Successfully", onfail="Adding Flow Failed!!!" ):
            return main.TRUE
        else:
            return main.FALSE

    def showFlow( self, **flowParameters ):
        """
         showFlow dumps the flow entries of flow table using "dpctl"
        """
        args = utilities.parse_args( [ "TCPIP", "TCPPORT" ], **flowParameters )
        tcpIP = args[ "TCPIP" ] if args[ "TCPIP" ] is not None else "127.0.0.1"
        tcpPort = args[ "TCPPORT" ] if args[
            "TCPPORT" ] is not None else "6634"
        command = "dpctl show tcp:" + str( tcpIP ) + ":" + str( tcpPort )
        response = self.execute(
            cmd=command,
            prompt="get_config_reply",
            timeout=240 )
        if utilities.assert_matches( expect='features_reply', actual=response, onpass="Show flow executed", onfail="Show flow execution Failed" ):
            main.last_result = main.TRUE
            return main.TRUE
        else:
            main.last_result = main.FALSE
            return main.FALSE

    def dumpFlow( self, **flowParameters ):
        """
         dumpFlow  gives installed flow information
        """
        args = utilities.parse_args( [ "TCPIP", "TCPPORT" ], **flowParameters )
        tcpIP = args[ "TCPIP" ] if args[ "TCPIP" ] is not None else "127.0.0.1"
        tcpPort = args[ "TCPPORT" ] if args[
            "TCPPORT" ] is not None else "6634"
        command = "dpctl dump-flows tcp:" + str( tcpIP ) + ":" + str( tcpPort )
        response = self.execute( cmd=command, prompt="type=", timeout=240 )
        if utilities.assert_matches( expect='stats_reply', actual=response, onpass="Dump flow executed", onfail="Dump flow execution Failed" ):
            main.last_result = main.TRUE
            return main.TRUE
        else:
            main.last_result = main.FALSE
            return main.FALSE

    def dumpTables( self, **flowParameters ):
        """
         dumpTables gives statistics for each of the flow tables used by datapath switch.
        """
        args = utilities.parse_args( [ "TCPIP", "TCPPORT" ], **flowParameters )
        tcpIP = args[ "TCPIP" ] if args[ "TCPIP" ] is not None else "127.0.0.1"
        tcpPort = args[ "TCPPORT" ] if args[
            "TCPPORT" ] is not None else "6634"
        command = "dpctl dump-tables tcp:" + \
            str( tcpIP ) + ":" + str( tcpPort )
        response = self.execute( cmd=command, prompt="matched", timeout=240 )
        if utilities.assert_matches( expect='lookup=3', actual=response, onpass="Dump Tables executed", onfail="Dump Tables execution Failed" ):
            main.last_result = main.TRUE
            return main.TRUE
        else:
            main.last_result = main.FALSE
            return main.FALSE

    def dumpPorts( self, **flowParameters ):
        """
         dumpPorts gives ports information
        """
        args = utilities.parse_args( [ "TCPIP", "TCPPORT" ], **flowParameters )
        tcpIP = args[ "TCPIP" ] if args[ "TCPIP" ] is not None else "127.0.0.1"
        tcpPort = args[ "TCPPORT" ] if args[
            "TCPPORT" ] is not None else "6634"
        command = "dpctl dump-ports tcp:" + str( tcpIP ) + ":" + str( tcpPort )
        response = self.execute( cmd=command, prompt="rx pkts", timeout=240 )
        if utilities.assert_matches( expect='ports', actual=response, onpass="Dump Ports executed", onfail="Dump Ports execution Failed" ):
            main.last_result = main.TRUE
            return main.TRUE
        else:
            main.last_result = main.FALSE
            return main.FALSE

    def dumpAggregate( self, **flowParameters ):
        """
         dumpAggregate  gives installed flow information.ggregate statistics for flows in datapath WITCH's tables that match flows.
         If flows is omitted, the statistics are aggregated across all flows in the datapath's flow tables
        """
        args = utilities.parse_args(
            [ "TCPIP", "TCPPORT", "FLOW" ], **flowParameters )
        tcpIP = args[ "TCPIP" ] if args[ "TCPIP" ] is not None else "127.0.0.1"
        tcpPort = args[ "TCPPORT" ] if args[
            "TCPPORT" ] is not None else "6634"
        flow = args[ "FLOW" ] if args[ "FLOW" ] is not None else ""
        command = "dpctl dump-aggregate tcp:" + \
            str( tcpIP ) + ":" + str( tcpPort ) + " " + str( flow )
        response = self.execute(
            cmd=command,
            prompt="flow_count=",
            timeout=240 )
        if utilities.assert_matches( expect='stats_reply', actual=response, onpass="Dump Aggregate executed", onfail="Dump Aggregate execution Failed" ):
            main.last_result = main.TRUE
            return main.TRUE
        else:
            main.last_result = main.FALSE
            return main.FALSE

    def delFlow( self, **flowParameters ):
        """
         delFlow Deletes entries from the datapath switch's tables that match flow
        """
        args = utilities.parse_args(
            [ "TCPIP", "TCPPORT", "FLOW" ], **flowParameters )
        tcpIP = args[ "TCPIP" ] if args[ "TCPIP" ] is not None else "127.0.0.1"
        tcpPort = args[ "TCPPORT" ] if args[
            "TCPPORT" ] is not None else "6634"
        flow = args[ "FLOW" ] if args[ "FLOW" ] is not None else ""
        command = "dpctl del-flows tcp:" + \
            str( tcpIP ) + ":" + str( tcpPort ) + " " + str( flow )
        response = self.execute(
            cmd=command,
            prompt="ETH-Tutorial",
            timeout=240 )
        if utilities.assert_matches( expect='@', actual=response, onpass="Delete flow executed", onfail="Delete flow execution Failed" ):
            main.last_result = main.TRUE
            return main.TRUE
        else:
            main.last_result = main.FALSE
            return main.FALSE

    def show( self, **flowParameters ):
        """
         show gives information on datapath switch including information on its flow tables and ports.
        """
        args = utilities.parse_args( [ "TCPIP", "TCPPORT" ], **flowParameters )
        tcpIP = args[ "TCPIP" ] if args[ "TCPIP" ] is not None else "127.0.0.1"
        tcpPort = args[ "TCPPORT" ] if args[
            "TCPPORT" ] is not None else "6634"
        command = "dpctl show tcp:" + str( tcpIP ) + ":" + str( tcpPort )
        response = self.execute(
            cmd=command,
            prompt="miss_send_len=",
            timeout=240 )
        if utilities.assert_matches( expect='get_config_reply', actual=response, onpass="show command executed", onfail="show command execution Failed" ):
            main.last_result = main.TRUE
            return main.TRUE
        else:
            main.last_result = main.FALSE
            return main.FALSE

    def showStatus( self, **flowParameters ):
        """
         showStatus gives a series of key-value pairs that report the status of switch.
         If key is specified, only the key-value pairs whose key names begin with key are printed.
        """
        args = utilities.parse_args(
            [ "TCPIP", "TCPPORT", "KEY" ], **flowParameters )
        tcpIP = args[ "TCPIP" ] if args[ "TCPIP" ] is not None else "127.0.0.1"
        tcpPort = args[ "TCPPORT" ] if args[
            "TCPPORT" ] is not None else "6634"
        key = args[ "KEY" ] if args[ "KEY" ] is not None else ""
        command = "dpctl status tcp:" + \
            str( tcpIP ) + ":" + str( tcpPort ) + " " + key
        response = self.execute( cmd=command, prompt="(.*)", timeout=240 )
        if utilities.assert_matches( expect='(.*)', actual=response, onpass="show command executed", onfail="show command execution Failed" ):
            main.last_result = main.TRUE
            return main.TRUE
        else:
            main.last_result = main.FALSE
            return main.FALSE

    def desc_set( self, **flowParameters ):
        """
         desc_set Sets the switch description ( as returned in ofp_desc_stats ) to string ( max length is DESC_STR_LEN )
        """
        args = utilities.parse_args( [
                                     "TCPIP",
                                     "TCPPORT",
                                     "STRING" ],
                            **flowParameters )

        tcpIP = args[ "TCPIP" ] if args[ "TCPIP" ] is not None else "127.0.0.1"
        tcpPort = args[ "TCPPORT" ] if args[
            "TCPPORT" ] is not None else "6634"
        string = " " + args[ "STRING" ] if args[
            "STRING" ] is not None else " DESC_STR_LEN"
        command = "dpctl desc tcp:" + \
            str( tcpIP ) + ":" + str( tcpPort ) + str( string )
        response = self.execute(
            cmd=command,
            prompt="ETH-Tutorial",
            timeout=240 )
        if utilities.assert_matches( expect='@', actual=response, onpass="desc command executed", onfail="desc command execution Failed" ):
            main.last_result = main.TRUE
            return main.TRUE
        else:
            main.last_result = main.FALSE
            return main.FALSE

    def dumpDesc( self, **flowParameters ):
        """
         dumpDesc Sets the switch description ( as returned in ofp_desc_stats ) to string ( max length is DESC_STR_LEN )
        """
        args = utilities.parse_args( [
                                     "TCPIP",
                                     "TCPPORT",
                                     "STRING" ],
                             **flowParameters )

        tcpIP = args[ "TCPIP" ] if args[ "TCPIP" ] is not None else "127.0.0.1"
        tcpPort = args[ "TCPPORT" ] if args[
            "TCPPORT" ] is not None else "6634"
        command = "dpctl dump-desc tcp:" + str( tcpIP ) + ":" + str( tcpPort )
        response = self.execute(
            cmd=command,
            prompt="Serial Num:",
            timeout=240 )
        if utilities.assert_matches( expect='stats_reply', actual=response, onpass="desc command executed", onfail="desc command execution Failed" ):
            main.last_result = main.TRUE
            return main.TRUE
        else:
            main.last_result = main.FALSE
            return main.FALSE

if __name__ != "__main__":
    import sys
    sys.modules[ __name__ ] = DpctlCliDriver()

