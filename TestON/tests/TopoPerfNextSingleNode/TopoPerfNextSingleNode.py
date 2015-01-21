# TopoPerfNext
#
# Topology Performance test for ONOS-next
#*** Revised for single node operation ***
#
# andrew@onlab.us

import time
import sys
import os
import re


class TopoPerfNextSingleNode:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        ONOS startup sequence
        """
        import time

        cell_name = main.params[ 'ENV' ][ 'cellName' ]

        git_pull = main.params[ 'GIT' ][ 'autoPull' ]
        checkout_branch = main.params[ 'GIT' ][ 'checkout' ]

        ONOS1_ip = main.params[ 'CTRL' ][ 'ip1' ]
        MN1_ip = main.params[ 'MN' ][ 'ip1' ]
        BENCH_ip = main.params[ 'BENCH' ][ 'ip' ]

        main.case( "Setting up test environment" )

        main.step( "Creating cell file" )
        cell_file_result = main.ONOSbench.create_cell_file(
            BENCH_ip, cell_name, MN1_ip, "onos-core",
            ONOS1_ip )

        main.step( "Applying cell file to environment" )
        cell_apply_result = main.ONOSbench.set_cell( cell_name )
        verify_cell_result = main.ONOSbench.verify_cell()

        main.step( "Git checkout and pull " + checkout_branch )
        if git_pull == 'on':
            checkout_result = \
                main.ONOSbench.git_checkout( checkout_branch )
            pull_result = main.ONOSbench.git_pull()
        else:
            checkout_result = main.TRUE
            pull_result = main.TRUE
            main.log.info( "Skipped git checkout and pull" )

        main.step( "Using mvn clean & install" )
        #mvn_result = main.ONOSbench.clean_install()
        mvn_result = main.TRUE

        main.step( "Creating ONOS package" )
        package_result = main.ONOSbench.onos_package()

        main.step( "Installing ONOS package" )
        install1_result = main.ONOSbench.onos_install( node=ONOS1_ip )

        # NOTE: This step may be unnecessary
        #main.step( "Starting ONOS service" )
        #start_result = main.ONOSbench.onos_start( ONOS1_ip )

        main.step( "Set cell for ONOS cli env" )
        main.ONOS1cli.set_cell( cell_name )

        time.sleep( 10 )

        main.step( "Start onos cli" )
        cli1 = main.ONOS1cli.start_onos_cli( ONOS1_ip )

        main.step( "Enable metrics feature" )
        main.ONOS1cli.feature_install( "onos-app-metrics" )

        utilities.assert_equals( expect=main.TRUE,
                                 actual=cell_file_result and cell_apply_result and
                                 verify_cell_result and checkout_result and
                                 pull_result and mvn_result and
                                 install1_result,
                                 onpass="ONOS started successfully",
                                 onfail="Failed to start ONOS" )

    def CASE2( self, main ):
        """
        Assign s1 to ONOS1 and measure latency

        There are 4 levels of latency measurements to this test:
        1 ) End-to-end measurement: Complete end-to-end measurement
           from TCP ( SYN/ACK ) handshake to Graph change
        2 ) OFP-to-graph measurement: 'ONOS processing' snippet of
           measurement from OFP Vendor message to Graph change
        3 ) OFP-to-device measurement: 'ONOS processing without
           graph change' snippet of measurement from OFP vendor
           message to Device change timestamp
        4 ) T0-to-device measurement: Measurement that includes
           the switch handshake to devices timestamp without
           the graph view change. ( TCP handshake -> Device
           change )
        """
        import time
        import subprocess
        import json
        import requests
        import os

        ONOS1_ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS_user = main.params[ 'CTRL' ][ 'user' ]

        default_sw_port = main.params[ 'CTRL' ][ 'port1' ]

        # Number of iterations of case
        num_iter = main.params[ 'TEST' ][ 'numIter' ]

        # Timestamp 'keys' for json metrics output.
        # These are subject to change, hence moved into params
        deviceTimestamp = main.params[ 'JSON' ][ 'deviceTimestamp' ]
        graphTimestamp = main.params[ 'JSON' ][ 'graphTimestamp' ]

        # List of switch add latency collected from
        # all iterations
        latency_end_to_end_list = []
        latency_ofp_to_graph_list = []
        latency_ofp_to_device_list = []
        latency_t0_to_device_list = []

        # Directory/file to store tshark results
        tshark_of_output = "/tmp/tshark_of_topo.txt"
        tshark_tcp_output = "/tmp/tshark_tcp_topo.txt"

        # String to grep in tshark output
        tshark_tcp_string = "TCP 74 " + default_sw_port
        tshark_of_string = "OFP 86 Vendor"

        # Initialize assertion to TRUE
        assertion = main.TRUE

        main.log.report( "Latency of adding one switch" )

        for i in range( 0, int( num_iter ) ):
            main.log.info( "Starting tshark capture" )

            #* TCP [ ACK, SYN ] is used as t0_a, the
            #  very first "exchange" between ONOS and
            #  the switch for end-to-end measurement
            #* OFP [ Stats Reply ] is used for t0_b
            #  the very last OFP message between ONOS
            #  and the switch for ONOS measurement
            main.ONOS1.tshark_grep( tshark_tcp_string,
                                    tshark_tcp_output )
            main.ONOS1.tshark_grep( tshark_of_string,
                                    tshark_of_output )

            # Wait and ensure tshark is started and
            # capturing
            time.sleep( 10 )

            main.log.info( "Assigning s1 to controller" )

            main.Mininet1.assign_sw_controller(
                sw="1",
                ip1=ONOS1_ip,
                port1=default_sw_port )

            # Wait and ensure switch is assigned
            # before stopping tshark
            time.sleep( 30 )

            main.log.info( "Stopping all Tshark processes" )
            main.ONOS1.stop_tshark()

            # tshark output is saved in ONOS. Use subprocess
            # to copy over files to TestON for parsing
            main.log.info( "Copying over tshark files" )

            # TCP CAPTURE ****
            # Copy the tshark output from ONOS machine to
            # TestON machine in tshark_tcp_output directory>file
            os.system( "scp " + ONOS_user + "@" + ONOS1_ip + ":" +
                       tshark_tcp_output + " /tmp/" )
            tcp_file = open( tshark_tcp_output, 'r' )
            temp_text = tcp_file.readline()
            temp_text = temp_text.split( " " )

            main.log.info( "Object read in from TCP capture: " +
                           str( temp_text ) )
            if len( temp_text ) > 1:
                t0_tcp = float( temp_text[ 1 ] ) * 1000.0
            else:
                main.log.error( "Tshark output file for TCP" +
                                " returned unexpected results" )
                t0_tcp = 0
                assertion = main.FALSE

            tcp_file.close()
            #****************

            # OF CAPTURE ****
            os.system( "scp " + ONOS_user + "@" + ONOS1_ip + ":" +
                       tshark_of_output + " /tmp/" )
            of_file = open( tshark_of_output, 'r' )

            line_ofp = ""
            # Read until last line of file
            while True:
                temp_text = of_file.readline()
                if temp_text != '':
                    line_ofp = temp_text
                else:
                    break
            obj = line_ofp.split( " " )

            main.log.info( "Object read in from OFP capture: " +
                           str( line_ofp ) )

            if len( line_ofp ) > 1:
                t0_ofp = float( obj[ 1 ] ) * 1000.0
            else:
                main.log.error( "Tshark output file for OFP" +
                                " returned unexpected results" )
                t0_ofp = 0
                assertion = main.FALSE

            of_file.close()
            #****************

            json_str_1 = main.ONOS1cli.topology_events_metrics()

            json_obj_1 = json.loads( json_str_1 )

            # Obtain graph timestamp. This timestsamp captures
            # the epoch time at which the topology graph was updated.
            graph_timestamp_1 = \
                json_obj_1[ graphTimestamp ][ 'value' ]

            # Obtain device timestamp. This timestamp captures
            # the epoch time at which the device event happened
            device_timestamp_1 = \
                json_obj_1[ deviceTimestamp ][ 'value' ]

            # t0 to device processing latency
            delta_device_1 = int( device_timestamp_1 ) - int( t0_tcp )

            # Get average of delta from all instances
            avg_delta_device = ( int( delta_device_1 ) )

            # Ensure avg delta meets the threshold before appending
            if avg_delta_device > 0.0 and avg_delta_device < 10000:
                latency_t0_to_device_list.append( avg_delta_device )
            else:
                main.log.info( "Results for t0-to-device ignored" +
                               "due to excess in threshold" )

            # t0 to graph processing latency ( end-to-end )
            delta_graph_1 = int( graph_timestamp_1 ) - int( t0_tcp )

            # Get average of delta from all instances
            avg_delta_graph = int( delta_graph_1 )

            # Ensure avg delta meets the threshold before appending
            if avg_delta_graph > 0.0 and avg_delta_graph < 10000:
                latency_end_to_end_list.append( avg_delta_graph )
            else:
                main.log.info( "Results for end-to-end ignored" +
                               "due to excess in threshold" )

            # ofp to graph processing latency ( ONOS processing )
            delta_ofp_graph_1 = int( graph_timestamp_1 ) - int( t0_ofp )

            avg_delta_ofp_graph = int( delta_ofp_graph_1 )

            if avg_delta_ofp_graph > 0.0 and avg_delta_ofp_graph < 10000:
                latency_ofp_to_graph_list.append( avg_delta_ofp_graph )
            else:
                main.log.info( "Results for ofp-to-graph " +
                               "ignored due to excess in threshold" )

            # ofp to device processing latency ( ONOS processing )
            delta_ofp_device_1 = float( device_timestamp_1 ) - float( t0_ofp )

            avg_delta_ofp_device = float( delta_ofp_device_1 )

            # NOTE: ofp - delta measurements are occasionally negative
            #      due to system time misalignment.
            latency_ofp_to_device_list.append( avg_delta_ofp_device )

            # TODO:
            # Fetch logs upon threshold excess

            main.log.info( "ONOS1 delta end-to-end: " +
                           str( delta_graph_1 ) + " ms" )

            main.log.info( "ONOS1 delta OFP - graph: " +
                           str( delta_ofp_graph_1 ) + " ms" )

            main.log.info( "ONOS1 delta device - t0: " +
                           str( delta_device_1 ) + " ms" )

            main.step( "Remove switch from controller" )
            main.Mininet1.delete_sw_controller( "s1" )

            time.sleep( 5 )

        # END of for loop iteration

        # If there is at least 1 element in each list,
        # pass the test case
        if len( latency_end_to_end_list ) > 0 and\
           len( latency_ofp_to_graph_list ) > 0 and\
           len( latency_ofp_to_device_list ) > 0 and\
           len( latency_t0_to_device_list ) > 0:
            assertion = main.TRUE
        elif len( latency_end_to_end_list ) == 0:
            # The appending of 0 here is to prevent
            # the min,max,sum functions from failing
            # below
            latency_end_to_end_list.append( 0 )
            assertion = main.FALSE
        elif len( latency_ofp_to_graph_list ) == 0:
            latency_ofp_to_graph_list.append( 0 )
            assertion = main.FALSE
        elif len( latency_ofp_to_device_list ) == 0:
            latency_ofp_to_device_list.append( 0 )
            assertion = main.FALSE
        elif len( latency_t0_to_device_list ) == 0:
            latency_t0_to_device_list.append( 0 )
            assertion = main.FALSE

        # Calculate min, max, avg of latency lists
        latency_end_to_end_max = \
            int( max( latency_end_to_end_list ) )
        latency_end_to_end_min = \
            int( min( latency_end_to_end_list ) )
        latency_end_to_end_avg = \
            ( int( sum( latency_end_to_end_list ) ) /
              len( latency_end_to_end_list ) )

        latency_ofp_to_graph_max = \
            int( max( latency_ofp_to_graph_list ) )
        latency_ofp_to_graph_min = \
            int( min( latency_ofp_to_graph_list ) )
        latency_ofp_to_graph_avg = \
            ( int( sum( latency_ofp_to_graph_list ) ) /
              len( latency_ofp_to_graph_list ) )

        latency_ofp_to_device_max = \
            int( max( latency_ofp_to_device_list ) )
        latency_ofp_to_device_min = \
            int( min( latency_ofp_to_device_list ) )
        latency_ofp_to_device_avg = \
            ( int( sum( latency_ofp_to_device_list ) ) /
              len( latency_ofp_to_device_list ) )

        latency_t0_to_device_max = \
            float( max( latency_t0_to_device_list ) )
        latency_t0_to_device_min = \
            float( min( latency_t0_to_device_list ) )
        latency_t0_to_device_avg = \
            ( float( sum( latency_t0_to_device_list ) ) /
              len( latency_ofp_to_device_list ) )

        main.log.report( "Switch add - End-to-end latency: \n" +
                         "Min: " + str( latency_end_to_end_min ) + "\n" +
                         "Max: " + str( latency_end_to_end_max ) + "\n" +
                         "Avg: " + str( latency_end_to_end_avg ) )
        main.log.report( "Switch add - OFP-to-Graph latency: \n" +
                         "Min: " + str( latency_ofp_to_graph_min ) + "\n" +
                         "Max: " + str( latency_ofp_to_graph_max ) + "\n" +
                         "Avg: " + str( latency_ofp_to_graph_avg ) )
        main.log.report( "Switch add - t0-to-Device latency: \n" +
                         "Min: " + str( latency_t0_to_device_min ) + "\n" +
                         "Max: " + str( latency_t0_to_device_max ) + "\n" +
                         "Avg: " + str( latency_t0_to_device_avg ) )

        utilities.assert_equals( expect=main.TRUE, actual=assertion,
                                 onpass="Switch latency test successful",
                                 onfail="Switch latency test failed" )

    def CASE3( self, main ):
        """
        Bring port up / down and measure latency.
        Port enable / disable is simulated by ifconfig up / down

        In ONOS-next, we must ensure that the port we are
        manipulating is connected to another switch with a valid
        connection. Otherwise, graph view will not be updated.
        """
        import time
        import subprocess
        import os
        import requests
        import json

        ONOS1_ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS_user = main.params[ 'CTRL' ][ 'user' ]

        default_sw_port = main.params[ 'CTRL' ][ 'port1' ]

        assertion = main.TRUE
        # Number of iterations of case
        num_iter = main.params[ 'TEST' ][ 'numIter' ]

        # Timestamp 'keys' for json metrics output.
        # These are subject to change, hence moved into params
        deviceTimestamp = main.params[ 'JSON' ][ 'deviceTimestamp' ]
        graphTimestamp = main.params[ 'JSON' ][ 'graphTimestamp' ]

        # NOTE: Some hardcoded variables you may need to configure
        #      besides the params

        tshark_port_status = "OFP 130 Port Status"

        tshark_port_up = "/tmp/tshark_port_up.txt"
        tshark_port_down = "/tmp/tshark_port_down.txt"
        interface_config = "s1-eth1"

        main.log.report( "Port enable / disable latency" )

        main.step( "Assign switches s1 and s2 to controller 1" )
        main.Mininet1.assign_sw_controller( sw="1", ip1=ONOS1_ip,
                                            port1=default_sw_port )
        main.Mininet1.assign_sw_controller( sw="2", ip1=ONOS1_ip,
                                            port1=default_sw_port )

        # Give enough time for metrics to propagate the
        # assign controller event. Otherwise, these events may
        # carry over to our measurements
        time.sleep( 10 )

        main.step( "Verify switch is assigned correctly" )
        result_s1 = main.Mininet1.get_sw_controller( sw="s1" )
        result_s2 = main.Mininet1.get_sw_controller( sw="s2" )
        if result_s1 == main.FALSE or result_s2 == main.FALSE:
            main.log.info( "Switch s1 was not assigned correctly" )
            assertion = main.FALSE
        else:
            main.log.info( "Switch s1 was assigned correctly" )

        port_up_device_to_ofp_list = []
        port_up_graph_to_ofp_list = []
        port_down_device_to_ofp_list = []
        port_down_graph_to_ofp_list = []

        for i in range( 0, int( num_iter ) ):
            main.step( "Starting wireshark capture for port status down" )
            main.ONOS1.tshark_grep( tshark_port_status,
                                    tshark_port_down )

            time.sleep( 10 )

            # Disable interface that is connected to switch 2
            main.step( "Disable port: " + interface_config )
            main.Mininet2.handle.sendline( "sudo ifconfig " +
                                           interface_config + " down" )
            main.Mininet2.handle.expect( "\$" )
            time.sleep( 10 )

            main.ONOS1.tshark_stop()
            time.sleep( 5 )

            # Copy tshark output file from ONOS to TestON instance
            #/tmp directory
            os.system( "scp " + ONOS_user + "@" + ONOS1_ip + ":" +
                       tshark_port_down + " /tmp/" )

            f_port_down = open( tshark_port_down, 'r' )
            # Get first line of port down event from tshark
            f_line = f_port_down.readline()
            obj_down = f_line.split( " " )
            if len( f_line ) > 0:
                timestamp_begin_pt_down = int( float( obj_down[ 1 ] ) ) * 1000
                main.log.info( "Port down begin timestamp: " +
                               str( timestamp_begin_pt_down ) )
            else:
                main.log.info( "Tshark output file returned unexpected" +
                               " results: " + str( obj_down ) )
                timestamp_begin_pt_down = 0

            f_port_down.close()

            main.log.info( "TEST tshark obj: " + str( obj_down ) )

            main.step( "Obtain t1 by REST call" )
            json_str_1 = main.ONOS1cli.topology_events_metrics()

            main.log.info( "TEST json_str 1: " + str( json_str_1 ) )

            json_obj_1 = json.loads( json_str_1 )

            time.sleep( 5 )

            # Obtain graph timestamp. This timestsamp captures
            # the epoch time at which the topology graph was updated.
            graph_timestamp_1 = \
                json_obj_1[ graphTimestamp ][ 'value' ]

            # Obtain device timestamp. This timestamp captures
            # the epoch time at which the device event happened
            device_timestamp_1 = \
                json_obj_1[ deviceTimestamp ][ 'value' ]

            # Get delta between graph event and OFP
            pt_down_graph_to_ofp_1 = int( graph_timestamp_1 ) -\
                int( timestamp_begin_pt_down )

            # Get delta between device event and OFP
            pt_down_device_to_ofp_1 = int( device_timestamp_1 ) -\
                int( timestamp_begin_pt_down )

            # Caluclate average across clusters
            pt_down_graph_to_ofp_avg = int( pt_down_graph_to_ofp_1 )
            pt_down_device_to_ofp_avg = int( pt_down_device_to_ofp_1 )

            if pt_down_graph_to_ofp_avg > 0.0 and \
                    pt_down_graph_to_ofp_avg < 1000:
                port_down_graph_to_ofp_list.append(
                    pt_down_graph_to_ofp_avg )
                main.log.info( "Port down: graph to ofp avg: " +
                               str( pt_down_graph_to_ofp_avg ) + " ms" )
            else:
                main.log.info( "Average port down graph-to-ofp result" +
                               " exceeded the threshold: " +
                               str( pt_down_graph_to_ofp_avg ) )

            if pt_down_device_to_ofp_avg > 0 and \
                    pt_down_device_to_ofp_avg < 1000:
                port_down_device_to_ofp_list.append(
                    pt_down_device_to_ofp_avg )
                main.log.info( "Port down: device to ofp avg: " +
                               str( pt_down_device_to_ofp_avg ) + " ms" )
            else:
                main.log.info( "Average port down device-to-ofp result" +
                               " exceeded the threshold: " +
                               str( pt_down_device_to_ofp_avg ) )

            # Port up events
            main.step( "Enable port and obtain timestamp" )
            main.step( "Starting wireshark capture for port status up" )
            main.ONOS1.tshark_grep( "OFP 130 Port Status", tshark_port_up )
            time.sleep( 5 )

            main.Mininet2.handle.sendline( "sudo ifconfig " +
                                           interface_config + " up" )
            main.Mininet2.handle.expect( "\$" )
            time.sleep( 10 )

            main.ONOS1.tshark_stop()

            os.system( "scp " + ONOS_user + "@" + ONOS1_ip + ":" +
                       tshark_port_up + " /tmp/" )

            f_port_up = open( tshark_port_up, 'r' )
            f_line = f_port_up.readline()
            obj_up = f_line.split( " " )
            if len( f_line ) > 0:
                timestamp_begin_pt_up = int( float( obj_up[ 1 ] ) ) * 1000
                main.log.info( "Port up begin timestamp: " +
                               str( timestamp_begin_pt_up ) )
            else:
                main.log.info( "Tshark output file returned unexpected" +
                               " results." )
                timestamp_begin_pt_up = 0

            f_port_up.close()

            main.step( "Obtain t1 by REST call" )
            json_str_1 = main.ONOS1cli.topology_events_metrics()

            json_obj_1 = json.loads( json_str_1 )

            # Obtain graph timestamp. This timestsamp captures
            # the epoch time at which the topology graph was updated.
            graph_timestamp_1 = \
                json_obj_1[ graphTimestamp ][ 'value' ]

            # Obtain device timestamp. This timestamp captures
            # the epoch time at which the device event happened
            device_timestamp_1 = \
                json_obj_1[ deviceTimestamp ][ 'value' ]

            # Get delta between graph event and OFP
            pt_up_graph_to_ofp_1 = int( graph_timestamp_1 ) -\
                int( timestamp_begin_pt_up )

            # Get delta between device event and OFP
            pt_up_device_to_ofp_1 = int( device_timestamp_1 ) -\
                int( timestamp_begin_pt_up )

            pt_up_graph_to_ofp_avg = float( pt_up_graph_to_ofp_1 )

            pt_up_device_to_ofp_avg = float( pt_up_device_to_ofp_1 )

            if pt_up_graph_to_ofp_avg > 0 and \
                    pt_up_graph_to_ofp_avg < 1000:
                port_up_graph_to_ofp_list.append(
                    pt_up_graph_to_ofp_avg )
                main.log.info( "Port down: graph to ofp avg: " +
                               str( pt_up_graph_to_ofp_avg ) + " ms" )
            else:
                main.log.info( "Average port up graph-to-ofp result" +
                               " exceeded the threshold: " +
                               str( pt_up_graph_to_ofp_avg ) )

            if pt_up_device_to_ofp_avg > 0 and \
                    pt_up_device_to_ofp_avg < 1000:
                port_up_device_to_ofp_list.append(
                    pt_up_device_to_ofp_avg )
                main.log.info( "Port up: device to ofp avg: " +
                               str( pt_up_device_to_ofp_avg ) + " ms" )
            else:
                main.log.info( "Average port up device-to-ofp result" +
                               " exceeded the threshold: " +
                               str( pt_up_device_to_ofp_avg ) )

            # END ITERATION FOR LOOP

        # Check all list for latency existence and set assertion
        if ( port_down_graph_to_ofp_list and port_down_device_to_ofp_list
                and port_up_graph_to_ofp_list and port_up_device_to_ofp_list ):
            assertion = main.TRUE

        # Calculate and report latency measurements
        port_down_graph_to_ofp_min = min( port_down_graph_to_ofp_list )
        port_down_graph_to_ofp_max = max( port_down_graph_to_ofp_list )
        port_down_graph_to_ofp_avg = \
            ( sum( port_down_graph_to_ofp_list ) /
              len( port_down_graph_to_ofp_list ) )

        main.log.report( "Port down graph-to-ofp Min: " +
                         str( port_down_graph_to_ofp_min ) + " ms  Max: " +
                         str( port_down_graph_to_ofp_max ) + " ms  Avg: " +
                         str( port_down_graph_to_ofp_avg ) )

        port_down_device_to_ofp_min = min( port_down_device_to_ofp_list )
        port_down_device_to_ofp_max = max( port_down_device_to_ofp_list )
        port_down_device_to_ofp_avg = \
            ( sum( port_down_device_to_ofp_list ) /
              len( port_down_device_to_ofp_list ) )

        main.log.report( "Port down device-to-ofp Min: " +
                         str( port_down_device_to_ofp_min ) + " ms  Max: " +
                         str( port_down_device_to_ofp_max ) + " ms  Avg: " +
                         str( port_down_device_to_ofp_avg ) )

        port_up_graph_to_ofp_min = min( port_up_graph_to_ofp_list )
        port_up_graph_to_ofp_max = max( port_up_graph_to_ofp_list )
        port_up_graph_to_ofp_avg = \
            ( sum( port_up_graph_to_ofp_list ) /
              len( port_up_graph_to_ofp_list ) )

        main.log.report( "Port up graph-to-ofp Min: " +
                         str( port_up_graph_to_ofp_min ) + " ms  Max: " +
                         str( port_up_graph_to_ofp_max ) + " ms  Avg: " +
                         str( port_up_graph_to_ofp_avg ) )

        port_up_device_to_ofp_min = min( port_up_device_to_ofp_list )
        port_up_device_to_ofp_max = max( port_up_device_to_ofp_list )
        port_up_device_to_ofp_avg = \
            ( sum( port_up_device_to_ofp_list ) /
              len( port_up_device_to_ofp_list ) )

        main.log.report( "Port up device-to-ofp Min: " +
                         str( port_up_device_to_ofp_min ) + " ms  Max: " +
                         str( port_up_device_to_ofp_max ) + " ms  Avg: " +
                         str( port_up_device_to_ofp_avg ) )

        utilities.assert_equals(
            expect=main.TRUE,
            actual=assertion,
            onpass="Port discovery latency calculation successful",
            onfail="Port discovery test failed" )

    def CASE4( self, main ):
        """
        Link down event using loss rate 100%

        Important:
            Use a simple 2 switch topology with 1 link between
            the two switches. Ensure that mac addresses of the
            switches are 1 / 2 respectively
        """
        import time
        import subprocess
        import os
        import requests
        import json

        ONOS1_ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS_user = main.params[ 'CTRL' ][ 'user' ]

        default_sw_port = main.params[ 'CTRL' ][ 'port1' ]

        # Number of iterations of case
        num_iter = main.params[ 'TEST' ][ 'numIter' ]

        # Timestamp 'keys' for json metrics output.
        # These are subject to change, hence moved into params
        deviceTimestamp = main.params[ 'JSON' ][ 'deviceTimestamp' ]
        linkTimestamp = main.params[ 'JSON' ][ 'linkTimestamp' ]
        graphTimestamp = main.params[ 'JSON' ][ 'graphTimestamp' ]

        assertion = main.TRUE
        # Link event timestamp to system time list
        link_down_link_to_system_list = []
        link_up_link_to_system_list = []
        # Graph event timestamp to system time list
        link_down_graph_to_system_list = []
        link_up_graph_to_system_list = []

        main.log.report( "Add / remove link latency between " +
                         "two switches" )

        main.step( "Assign all switches" )
        main.Mininet1.assign_sw_controller(
            sw="1",
            ip1=ONOS1_ip,
            port1=default_sw_port )
        main.Mininet1.assign_sw_controller(
            sw="2",
            ip1=ONOS1_ip,
            port1=default_sw_port )

        main.step( "Verifying switch assignment" )
        result_s1 = main.Mininet1.get_sw_controller( sw="s1" )
        result_s2 = main.Mininet1.get_sw_controller( sw="s2" )

        # Allow time for events to finish before taking measurements
        time.sleep( 10 )

        link_down = False
        # Start iteration of link event test
        for i in range( 0, int( num_iter ) ):
            main.step( "Getting initial system time as t0" )

            timestamp_link_down_t0 = time.time() * 1000
            # Link down is simulated by 100% loss rate using traffic
            # control command
            main.Mininet1.handle.sendline(
                "sh tc qdisc add dev s1-eth1 root netem loss 100%" )

            # TODO: Iterate through 'links' command to verify that
            #      link s1 -> s2 went down ( loop timeout 30 seconds )
            #      on all 3 ONOS instances
            main.log.info( "Checking ONOS for link update" )
            loop_count = 0
            while( not link_down and loop_count < 30 ):
                json_str = main.ONOS1cli.links()

                if not json_str:
                    main.log.error( "CLI command returned error " )
                    break
                else:
                    json_obj = json.loads( json_str )
                for obj in json_obj:
                    if '01' not in obj[ 'src' ][ 'device' ]:
                        link_down = True
                        main.log.report( "Link down from " +
                                         "s1 -> s2 on ONOS1 detected" )
                loop_count += 1
                # If CLI doesn't like the continuous requests
                # and exits in this loop, increase the sleep here.
                # Consequently, while loop timeout will increase
                time.sleep( 1 )

            # Give time for metrics measurement to catch up
            # NOTE: May need to be configured more accurately
            time.sleep( 10 )
            # If we exited the while loop and link down 1,2,3 are still
            # false, then ONOS has failed to discover link down event
            if not link_down:
                main.log.info( "Link down discovery failed" )

                link_down_lat_graph1 = 0
                link_down_lat_device1 = 0
                assertion = main.FALSE
            else:
                json_topo_metrics_1 =\
                    main.ONOS1cli.topology_events_metrics()
                json_topo_metrics_1 = json.loads( json_topo_metrics_1 )

                main.log.info( "Obtaining graph and device timestamp" )
                graph_timestamp_1 = \
                    json_topo_metrics_1[ graphTimestamp ][ 'value' ]

                link_timestamp_1 = \
                    json_topo_metrics_1[ linkTimestamp ][ 'value' ]

                if graph_timestamp_1 and link_timestamp_1:
                    link_down_lat_graph1 = int( graph_timestamp_1 ) -\
                        timestamp_link_down_t0

                    link_down_lat_link1 = int( link_timestamp_1 ) -\
                        timestamp_link_down_t0
                else:
                    main.log.error( "There was an error calculating" +
                                    " the delta for link down event" )
                    link_down_lat_graph1 = 0

                    link_down_lat_device1 = 0

            main.log.report( "Link down latency ONOS1 iteration " +
                             str( i ) + " (end-to-end): " +
                             str( link_down_lat_graph1 ) + " ms" )

            main.log.report( "Link down latency ONOS1 iteration " +
                             str( i ) + " (link-event-to-system-timestamp): " +
                             str( link_down_lat_link1 ) + " ms" )

            # Calculate avg of node calculations
            link_down_lat_graph_avg = link_down_lat_graph1
            link_down_lat_link_avg = link_down_lat_link1

            # Set threshold and append latency to list
            if link_down_lat_graph_avg > 0.0 and\
               link_down_lat_graph_avg < 30000:
                link_down_graph_to_system_list.append(
                    link_down_lat_graph_avg )
            else:
                main.log.info( "Link down latency exceeded threshold" )
                main.log.info( "Results for iteration " + str( i ) +
                               "have been omitted" )
            if link_down_lat_link_avg > 0.0 and\
               link_down_lat_link_avg < 30000:
                link_down_link_to_system_list.append(
                    link_down_lat_link_avg )
            else:
                main.log.info( "Link down latency exceeded threshold" )
                main.log.info( "Results for iteration " + str( i ) +
                               "have been omitted" )

            # NOTE: To remove loss rate and measure latency:
            #       'sh tc qdisc del dev s1-eth1 root'
            timestamp_link_up_t0 = time.time() * 1000
            main.Mininet1.handle.sendline( "sh tc qdisc del dev " +
                                           "s1-eth1 root" )
            main.Mininet1.handle.expect( "mininet>" )

            main.log.info( "Checking ONOS for link update" )

            link_down1 = True
            loop_count = 0
            while( link_down1 and loop_count < 30 ):
                json_str1 = main.ONOS1cli.links()
                if not json_str1:
                    main.log.error( "CLI command returned error " )
                    break
                else:
                    json_obj1 = json.loads( json_str1 )

                for obj1 in json_obj1:
                    if '01' in obj1[ 'src' ][ 'device' ]:
                        link_down1 = False
                        main.log.report( "Link up from " +
                                         "s1 -> s2 on ONOS1 detected" )
                loop_count += 1
                time.sleep( 1 )

            if link_down1:
                main.log.info( "Link up discovery failed" )
                link_up_lat_graph1 = 0
                link_up_lat_device1 = 0
                assertion = main.FALSE
            else:
                json_topo_metrics_1 =\
                    main.ONOS1cli.topology_events_metrics()
                json_topo_metrics_1 = json.loads( json_topo_metrics_1 )

                main.log.info( "Obtaining graph and device timestamp" )
                graph_timestamp_1 = \
                    json_topo_metrics_1[ graphTimestamp ][ 'value' ]

                link_timestamp_1 = \
                    json_topo_metrics_1[ linkTimestamp ][ 'value' ]

                if graph_timestamp_1 and link_timestamp_1:
                    link_up_lat_graph1 = int( graph_timestamp_1 ) -\
                        timestamp_link_up_t0
                    link_up_lat_link1 = int( link_timestamp_1 ) -\
                        timestamp_link_up_t0
                else:
                    main.log.error( "There was an error calculating" +
                                    " the delta for link down event" )
                    link_up_lat_graph1 = 0
                    link_up_lat_device1 = 0

            main.log.info( "Link up latency ONOS1 iteration " +
                           str( i ) + " (end-to-end): " +
                           str( link_up_lat_graph1 ) + " ms" )

            main.log.info( "Link up latency ONOS1 iteration " +
                           str( i ) + " (link-event-to-system-timestamp): " +
                           str( link_up_lat_link1 ) + " ms" )

            # Calculate avg of node calculations
            link_up_lat_graph_avg = link_up_lat_graph1
            link_up_lat_link_avg = link_up_lat_link1

            # Set threshold and append latency to list
            if link_up_lat_graph_avg > 0.0 and\
               link_up_lat_graph_avg < 30000:
                link_up_graph_to_system_list.append(
                    link_up_lat_graph_avg )
            else:
                main.log.info( "Link up latency exceeded threshold" )
                main.log.info( "Results for iteration " + str( i ) +
                               "have been omitted" )
            if link_up_lat_link_avg > 0.0 and\
               link_up_lat_link_avg < 30000:
                link_up_link_to_system_list.append(
                    link_up_lat_link_avg )
            else:
                main.log.info( "Link up latency exceeded threshold" )
                main.log.info( "Results for iteration " + str( i ) +
                               "have been omitted" )

        # Calculate min, max, avg of list and report
        link_down_min = min( link_down_graph_to_system_list )
        link_down_max = max( link_down_graph_to_system_list )
        link_down_avg = sum( link_down_graph_to_system_list ) / \
            len( link_down_graph_to_system_list )
        link_up_min = min( link_up_graph_to_system_list )
        link_up_max = max( link_up_graph_to_system_list )
        link_up_avg = sum( link_up_graph_to_system_list ) / \
            len( link_up_graph_to_system_list )

        main.log.report( "Link down latency - Min: " +
                         str( link_down_min ) + "ms  Max: " +
                         str( link_down_max ) + "ms  Avg: " +
                         str( link_down_avg ) + "ms" )
        main.log.report( "Link up latency - Min: " +
                         str( link_up_min ) + "ms  Max: " +
                         str( link_up_max ) + "ms  Avg: " +
                         str( link_up_avg ) + "ms" )

        utilities.assert_equals(
            expect=main.TRUE,
            actual=assertion,
            onpass="Link discovery latency calculation successful",
            onfail="Link discovery latency case failed" )

    def CASE5( self, main ):
        """
        100 Switch discovery latency

        Important:
            This test case can be potentially dangerous if
            your machine has previously set iptables rules.
            One of the steps of the test case will flush
            all existing iptables rules.
        Note:
            You can specify the number of switches in the
            params file to adjust the switch discovery size
            ( and specify the corresponding topology in Mininet1
            .topo file )
        """
        import time
        import subprocess
        import os
        import requests
        import json

        ONOS1_ip = main.params[ 'CTRL' ][ 'ip1' ]
        MN1_ip = main.params[ 'MN' ][ 'ip1' ]
        ONOS_user = main.params[ 'CTRL' ][ 'user' ]

        default_sw_port = main.params[ 'CTRL' ][ 'port1' ]

        # Number of iterations of case
        num_iter = main.params[ 'TEST' ][ 'numIter' ]
        num_sw = main.params[ 'TEST' ][ 'numSwitch' ]

        # Timestamp 'keys' for json metrics output.
        # These are subject to change, hence moved into params
        deviceTimestamp = main.params[ 'JSON' ][ 'deviceTimestamp' ]
        graphTimestamp = main.params[ 'JSON' ][ 'graphTimestamp' ]

        tshark_ofp_output = "/tmp/tshark_ofp_" + num_sw + "sw.txt"
        tshark_tcp_output = "/tmp/tshark_tcp_" + num_sw + "sw.txt"

        tshark_ofp_result_list = []
        tshark_tcp_result_list = []

        main.case( num_sw + " Switch discovery latency" )
        main.step( "Assigning all switches to ONOS1" )
        for i in range( 1, int( num_sw ) + 1 ):
            main.Mininet1.assign_sw_controller(
                sw=str( i ),
                ip1=ONOS1_ip,
                port1=default_sw_port )

        # Ensure that nodes are configured with ptpd
        # Just a warning message
        main.log.info( "Please check ptpd configuration to ensure" +
                       " All nodes' system times are in sync" )
        time.sleep( 5 )

        for i in range( 0, int( num_iter ) ):

            main.step( "Set iptables rule to block incoming sw connections" )
            # Set iptables rule to block incoming switch connections
            # The rule description is as follows:
            #   Append to INPUT rule,
            #   behavior DROP that matches following:
            #       * packet type: tcp
            #       * source IP: MN1_ip
            #       * destination PORT: 6633
            main.ONOS1.handle.sendline(
                "sudo iptables -A INPUT -p tcp -s " + MN1_ip +
                " --dport " + default_sw_port + " -j DROP" )
            main.ONOS1.handle.expect( "\$" )
            #   Append to OUTPUT rule,
            #   behavior DROP that matches following:
            #       * packet type: tcp
            #       * source IP: MN1_ip
            #       * destination PORT: 6633
            main.ONOS1.handle.sendline(
                "sudo iptables -A OUTPUT -p tcp -s " + MN1_ip +
                " --dport " + default_sw_port + " -j DROP" )
            main.ONOS1.handle.expect( "\$" )
            # Give time to allow rule to take effect
            # NOTE: Sleep period may need to be configured
            #      based on the number of switches in the topology
            main.log.info( "Please wait for switch connection to " +
                           "time out" )
            time.sleep( 60 )

            # Gather vendor OFP with tshark
            main.ONOS1.tshark_grep( "OFP 86 Vendor",
                                    tshark_ofp_output )
            main.ONOS1.tshark_grep( "TCP 74 ",
                                    tshark_tcp_output )

            # NOTE: Remove all iptables rule quickly ( flush )
            #      Before removal, obtain TestON timestamp at which
            #      removal took place
            #      ( ensuring nodes are configured via ptp )
            #      sudo iptables -F

            t0_system = time.time() * 1000
            main.ONOS1.handle.sendline(
                "sudo iptables -F" )

            # Counter to track loop count
            counter_loop = 0
            counter_avail1 = 0
            onos1_dev = False
            while counter_loop < 60:
                # Continue to check devices for all device
                # availability. When all devices in all 3
                # ONOS instances indicate that devices are available
                # obtain graph event timestamp for t1.
                device_str_obj1 = main.ONOS1cli.devices()
                device_json1 = json.loads( device_str_obj1 )

                for device1 in device_json1:
                    if device1[ 'available' ]:
                        counter_avail1 += 1
                        if counter_avail1 == int( num_sw ):
                            onos1_dev = True
                            main.log.info( "All devices have been " +
                                           "discovered on ONOS1" )
                    else:
                        counter_avail1 = 0

                if onos1_dev:
                    main.log.info( "All devices have been discovered " +
                                   "on all ONOS instances" )
                    json_str_topology_metrics_1 =\
                        main.ONOS1cli.topology_events_metrics()
                    # Exit while loop if all devices discovered
                    break

                counter_loop += 1
                # Give some time in between CLI calls
                #( will not affect measurement )
                time.sleep( 3 )

            main.ONOS1.tshark_stop()

            os.system( "scp " + ONOS_user + "@" + ONOS1_ip + ":" +
                       tshark_ofp_output + " /tmp/" )
            os.system( "scp " + ONOS_user + "@" + ONOS1_ip + ":" +
                       tshark_tcp_output + " /tmp/" )
            ofp_file = open( tshark_ofp_output, 'r' )

            # The following is for information purpose only.
            # TODO: Automate OFP output analysis
            main.log.info( "Tshark OFP Vendor output: " )
            for line in ofp_file:
                tshark_ofp_result_list.append( line )
                main.log.info( line )

            ofp_file.close()

            tcp_file = open( tshark_tcp_output, 'r' )
            main.log.info( "Tshark TCP 74 output: " )
            for line in tcp_file:
                tshark_tcp_result_list.append( line )
                main.log.info( line )

            tcp_file.close()

            json_obj_1 = json.loads( json_str_topology_metrics_1 )

            graph_timestamp_1 = \
                json_obj_1[ graphTimestamp ][ 'value' ]

            main.log.info(
                int( graph_timestamp_1 ) - int( t0_system ) )
