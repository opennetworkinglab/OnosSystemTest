#!/usr/bin/env python
"""
Created on 26-Oct-2012

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


fvtapidriver is the basic driver which will handle the fvtapidriver functions
"""
"""
There are two changes required in flowvisor-test framework :

1. In ~/flowvisortests/tests/templatetest.py line : 15 comment 'basic_logger = None'
2. In ~/flowvisortests/tests/testutils.py line : 50 specify config file path CONFIG_FILE = "~/flowvisor-test/tests/tests-base.json"

"""
import pexpect
import struct
import fcntl
import os
import signal
import re
import sys
from common.apidriver import API
import logging

sys.path.append( path + "/lib/flowvisor-test/tests" )
sys.path.append( path + "/lib/flowvisor-test/src/python/" )

import templatetest
import testutils
import oftest.cstruct as ofp
import oftest.message as message
import oftest.parse as parse
import oftest.action as action
import oftest.error as error
import socket
import __builtin__

config_default = {
    "param": None,
    "fv_cmd": "/home/openflow/flowvisor/scripts/flowvisor.sh",
    "platform": "local",
    "controller_host": "127.0.0.1",
    "controller_port": 6653,
    "timeout": 3,
    "port_count": 4,
    "base_of_port": 1,
    "base_if_index": 1,
    "test_spec": "all",
    "test_dir": ".",
    "log_file": "/home/openflow/fvt.log",
    "list": False,
    "debug": "debug",
    "dbg_level": logging.DEBUG,
    "port_map": {},
    "test_params": "None"
}


def test_set_init( config ):
    """
    Set up function for basic test classes
    config: The configuration dictionary; see fvt
    """
    global basic_port_map
    global basic_fv_cmd
    global basic_logger
    global basic_timeout
    global basic_config
    global baisc_logger

    basic_fv_cmd = config[ "fv_cmd" ]
    basic_timeout = config[ "timeout" ]
    basic_port_map = config[ "port_map" ]
    basic_config = config


class FvtApiDriver( API, templatetest.TemplateTest ):

    def __init__( self ):
        super( API, self ).__init__()
        print 'init'

    def connect( self, **connectargs ):
        for key in connectargs:
            vars( self )[ key ] = connectargs[ key ]

        self.name = self.options[ 'name' ]
        connect_result = super( API, self ).connect()
        self.logFileName = main.logdir + "/" + self.name + ".session"
        config_default[ "log_file" ] = self.logFileName
        test_set_init( config_default )
        __builtin__.basic_logger = vars( main )[ self.name + 'log' ]
        __builtin__.basic_logger.info( "Calling my test setup" )
        self.setUp( basic_logger )

        ( self.fv, self.sv, sv_ret, ctl_ret, sw_ret ) = testutils.setUpTestEnv(
            self, fv_cmd=basic_fv_cmd )

        self.chkSetUpCondition( self.fv, sv_ret, ctl_ret, sw_ret )
        return main.TRUE

    def simplePacket( self, dl_src ):
        dl_src = vars( testutils )[ dl_src ]
        return testutils.simplePacket( dl_src=dl_src )

    def genPacketIn( self, in_port, pkt ):
        return testutils.genPacketIn( in_port=in_port, pkt=pkt )

    def ofmsgSndCmp( self, snd_list, exp_list, xid_ignore=True, hdr_only=True ):
        return testutils.ofmsgSndCmp( self, snd_list, exp_list, xid_ignore, hdr_only )

    def setRule( self, sv, rule, num_try ):
        return testutils.setRule( self, sv, rule, num_try )

    def chkFlowdb( self, controller_number, switch_number, exp_count, exp_rewrites ):
        return testutils.chkFlowdb( self, controller_number, switch_number, exp_count, exp_rewrites )

    def chkSwitchStats( self, switch_number, ofproto, exp_snd_count, exp_rcv_count ):
        return testutils.chkSwitchStats( self, switch_number, ofproto, exp_snd_count, exp_rcv_count )

    def chkSliceStats( self, controller_number, ofproto, exp_snd_count, exp_rcv_count ):
        return testutils.chkSliceStats( self, controller_number, ofproto, exp_snd_count, exp_rcv_count )

    def recvStats( self, swId, typ ):
        return testutils.recvStats( self, swId, typ )

    def ofmsgSndCmpWithXid( self, snd_list, exp_list, xid_ignore, hdr_only ):
        return testutils.ofmsgSndCmpWithXid( self, snd_list, exp_list, xid_ignore, hdr_only )

    def genPacketOut( self, xid, buffer_id, in_port, action_ports, pkt ):
        return testutils.genPacketOut( self, xid, buffer_id, in_port, action_ports, pkt )

    def genFlowModFlush( self ):
        return testutils.genFlowModFlush()

    def genPhyPort( self, name, addr, port_no ):
        return testutils.genPhyPort( name, addr, port_no )

    def disconnect( self, handle ):
        response = ''
        """
        if self.handle:
            self.handle = handle
            response = self.execute( cmd="exit",prompt="(.*)",timeout=120 )
        else :
            main.log.error( "Connection failed to the host" )
            response = main.FALSE
        """
        return response

    def setUp( self, basic_logger ):
        self.logger = basic_logger
        # basic_logger.info( "** START TEST CASE " + str( self ) )
        if basic_timeout == 0:
            self.timeout = None
        else:
            self.timeout = basic_timeout
        self.fv = None
        self.sv = None
        self.controllers = []
        self.switches = []

    def close_log_handles( self ):
        self.tearDown()
        vars( main )[ self.name + 'log' ].removeHandler( self.log_handler )
        # if self.logfile_handler:
        #    self.logfile_handler.close()

        return main.TRUE

