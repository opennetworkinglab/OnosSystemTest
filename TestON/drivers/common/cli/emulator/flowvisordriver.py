#!/usr/bin/env python
"""
Created on 26-Mar-2013

author:: Anil Kumar ( anilkumar.s@paxterrasolutions.com )


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


FlowVisorDriver is the basic driver which will handle the Mininet functions
"""
import re
import sys
from drivers.common.cli.emulatordriver import Emulator


class FlowVisorDriver( Emulator ):

    """
        FlowVisorDriver is the basic driver which will handle the Mininet functions
    """
    def __init__( self ):
        super( Emulator, self ).__init__()
        self.handle = self
        self.wrapped = sys.modules[ __name__ ]

    def connect( self, **connectargs ):
        #,user_name, ip_address, pwd,options ):
        # Here the main is the TestON instance after creating all the log
        # handles.
        for key in connectargs:
            vars( self )[ key ] = connectargs[ key ]

        self.name = self.options[ 'name' ]
        self.handle = super(
            FlowVisorDriver,
            self ).connect(
            user_name=self.user_name,
            ip_address=self.ip_address,
            port=None,
            pwd=self.pwd )

        self.ssh_handle = self.handle

        # Copying the readme file to process the
        if self.handle:
            self.execute( cmd='\r', prompt='\$', timeout=10 )
            self.options[ 'path' ] = '/home/openflow/flowvisor/scripts/'
            #self.handle.logfile = sys.stdout
            self.execute(
                cmd='cd ' +
                self.options[ 'path' ],
                prompt='\$',
                timeout=10 )
            main.log.info( "Starting FlowVisor " )

            response = self.execute(
                cmd='./flowvisor.sh &',
                prompt='---\sSetting\slogging\slevel\sto\sNOTE',
                timeout=10 )

            pattern = '\d+'

            process_id_search = re.search( "\[\d+\]\s+(\d+)", str( response ) )
            self.fvprocess_id = "None"
            if process_id_search:
                self.fvprocess_id = process_id_search.group( 1 )

            utilities.assert_matches(
                expect=pattern,
                actual=response,
                onpass="FlowVisor Started Successfully : Proceess Id :" +
                self.fvprocess_id,
                onfail="Failed to start FlowVisor" )
            main.log.info( response )
            #import time
            # time.sleep( 10 )
            #response = self.execute( cmd='./start_visualizer.sh & \r',prompt='\$',timeout=10 )

            return main.TRUE
        else:
            main.log.error(
                "Connection failed to the host " +
                self.user_name +
                "@" +
                self.ip_address )
            main.log.error( "Failed to connect to the FlowVisor" )
            return main.FALSE

    def removeFlowSpace( self, id ):
        if id == "all":
            flow_space = self.listFlowSpace()
            flow_ids = re.findall( "\,id=\[(\d+)\]", flow_space )
            for id in flow_ids:
                self.removeFlowSpace( id )
        else:
            self.execute( cmd="clear", prompt="\$", timeout=10 )
            self.execute(
                cmd="./fvctl.sh removeFlowSpace " +
                id,
                prompt="passwd:",
                timeout=10 )
            self.execute( cmd="\n", prompt="\$", timeout=10 )
            main.log.info( "Removed flowSpace which is having id :" + id )

        return main.TRUE

    def addFlowSpace( self, **flowspace_args ):
        temp_string = None
        for key in flowspace_args:
            if temp_string:
                temp_string = temp_string + ',' + \
                    key + '=' + flowspace_args[ key ]
            else:
                temp_string = ''
                temp_string = temp_string + key + '=' + flowspace_args[ key ]

        src_search = re.search( 'dl_src', temp_string )
        if src_search:
            flowspace = "any 100 dl_type=0x806,nw_proto=6," + \
                temp_string + " Slice:SSH=4"
        else:
            flowspace = "any 100 dl_type=0x800,nw_proto=6," + \
                temp_string + " Slice:SSH=4"

        """
        try :
            if self.dl_src and self.nw_dst:
                flowspace = "any 100 dl_type=0x806,dl_src="+self.dl_src+",nw_dst="+self.nw_dst+" Slice:"+self.Slice+"=4"
        except Exception:
            try :
                if self.nw_src and self.tp_dst:
                    flowspace = "any 100 dl_type=0x800,nw_proto=6,nw_src="+self.nw_src+",tp_dst="+self.tp_dst+" Slice:"+self.Slice+"=4"
            except Exception:
                try :
                    if self.nw_src and self.tp_src:
                        flowspace = "any 100 dl_type=0x800,nw_proto=6,nw_src="+self.nw_src+",tp_src="+self.tp_dst+" Slice:"+self.Slice+"=4"
                except Exception:
                    main.log.error( "Please specify flowspace properly" )
        """
        # self.execute( cmd="clear",prompt="\$",timeout=10 )
        self.execute(
            cmd="./fvctl.sh addFlowSpace " +
            flowspace,
            prompt="passwd:",
            timeout=10 )
        self.execute( cmd="\n", prompt="\$", timeout=10 )
        sucess_match = re.search( "success\:\s+(\d+)", main.last_response )
        if sucess_match:
            main.log.info(
                "Added flow Space and id is " +
                sucess_match.group( 1 ) )
            return main.TRUE
        else:
            return main.FALSE

    def listFlowSpace( self ):
        self.execute( cmd="clear", prompt="\$", timeout=10 )
        self.execute(
            cmd="./fvctl.sh listFlowSpace ",
            prompt="passwd:",
            timeout=10 )
        self.execute( cmd="\n", prompt="\$", timeout=10 )
        flow_space = main.last_response
        flow_space = self.remove_contol_chars( flow_space )
        flow_space = re.sub(
            "rule\s(\d+)\:",
            "\nrule " +
            r'\1' +
            ":",
            flow_space )
        main.log.info( flow_space )

        return flow_space

    def listDevices( self ):
        # self.execute( cmd="clear",prompt="\$",timeout=10 )
        #self.execute( cmd="./fvctl.sh listDevices ",prompt="passwd:",timeout=10 )
        # self.execute( cmd="\n",prompt="\$",timeout=10 )
        devices_list = ''
        last_response = re.findall(
            "(Device\s\d+\:\s((\d|[a-z])(\d|[a-z])\:)+(\d|[a-z])(\d|[a-z]))",
            main.last_response )

        for resp in last_response:
            devices_match = re.search(
                "(Device\s\d+\:\s((\d|[a-z])(\d|[a-z])\:)+(\d|[a-z])(\d|[a-z]))",
                str( resp ) )
            if devices_match:
                devices_list = devices_list + devices_match.group( 0 ) + "\n"
        devices_list = "Device 0: 00:00:00:00:00:00:00:02 \n Device 1: 00:00:00:00:00:00:00:03"
        main.log.info( "List of Devices \n" + devices_list )

        return main.TRUE

    def disconnect( self ):

        response = ''
        main.log.info( "Stopping the FlowVisor" )
        if self.handle:
            self.handle.sendline( "kill -9 " + str( self.fvprocess_id ) )
        else:
            main.log.error( "Connection failed to the host" )
            response = main.FALSE
        return response
