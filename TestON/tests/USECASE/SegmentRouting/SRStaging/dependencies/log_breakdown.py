#! /usr/bin/python2
"""
Copyright 2021 Open Networking Foundation ( ONF )

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

import datetime
import re
import sys
import json
from copy import deepcopy as deepcopy

DEBUG = 0
TIMEFMT = '%Y-%m-%d %H:%M:%S.%f'
################## ONOS REGULAR EXPRESSIONS ##################
# TODO Add log:log from the test for start and end timestamps
# TODO: Investigate why these don't show up in the logs
# TODO Using a tail of the logs will help reduce log size

defaultOnosLineRE = r"((?P<pod>onos-tost-onos-classic-\d+) (?P<app>onos-classic) )?(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2},\d{3}) (?P<level>\w+)"

# Error in RPC Stream
p4rt_switch_down_re = r"Error on StreamChannel RPC for device:(?P<deviceName>\w+)"
gnmi_switch_down_re = r"Error on Subscribe RPC for device:(?P<deviceName>\w+)"
gnmi_switch_state_re = r"Detected channel connectivity change for device:(?P<deviceName>\w+), new state is (?P<state>\w+)"
p4rt_channel_open_re = r"Notifying event CHANNEL_OPEN for device:(?P<deviceName>\w+)"
gnmi_update_re = r"Received SubscribeResponse from device:(?P<deviceName>\w+)"
device_manager_port_change_re = r"Device device:(?P<deviceName>\w+) port \[(\d+)/(\d+)\]\((?P<sdkPort>\d+)\) status changed \(enabled=(?P<state>\w+)\)"
# Trellis processing
sr_switch_down_re = r"\*\* DEVICE DOWN Processing device event DEVICE_AVAILABILITY_CHANGED for unavailable device device:(?P<deviceName>\w+)"
sr_port_updated_re = r"\*\* PORT UPDATED"
sr_link_added_re = r"\*\* LINK ADDED"
sr_link_removed_re = r"\*\* LINK REMOVED"
sr_event_re = r"\*\* "
# Cause writes to switches
sr_remove_re = r"removeFromHash in device device:(?P<deviceName>\w+): "
sr_add_re = r"addToHash in device device:(?P<deviceName>\w+): "
sr_rule_re = r"Sending MPLS fwd obj ([\d-]+) for SID (\d+)-> next (\d+) in sw: device:(?P<deviceName>\w+)"
# There should probably be another line between add/remove FAR to write request
sr_far_installation_re = r"Installing FAR"
sr_far_removal_re = r"Removing FAR"  # VERIFY RE
# write requests/response
p4rt_write_request_update_re = r"Adding (?P<updateType>\w+) update to write request for device:(?P<deviceName>\w+):"
p4rt_write_request_re = r"Sending write request to device:(?P<deviceName>\w+)"
p4rt_write_response_re = r"Received write response from device:(?P<deviceName>\w+)"
# exclude next write request/response
p4rt_cleanup_re = r"Cleaning up (\d+) action profile groups and (\d+) members on device:(?P<deviceName>\w+)..."
# Remove filtering caused by port down, not related to new path plumbing, but ignore next write for switch
sr_port_filter_removal_re = r"Switchport device:(?P<deviceName>\w+)/\[(\d+)/(\d+)\]\((?P<sdkPort>\d+)\) disabled..removing filters"
sr_port_filter_program_re = r"Switchport device:(?P<deviceName>\w+)/\[(\d+)/(\d+)\]\((?P<sdkPort>\d+)\) enabled..programming filters"
# Unable to delete/modify - write failed
p4rt_unable_to_re = r"Unable to (?P<action>\w+) action profile group on device:(?P<deviceName>\w+)"
onos_error_re = r"ERROR"

################## STRATUM REGULAR EXPRESSIONS ##################
defaultStratumLineRE = r"((?P<pod>stratum-\w+) (?P<app>stratum-bf) \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{9}Z (\x1b\[(0;\d+)?m)*)?(I|E|W)?(?P<date>(\d{4}\d{2}\d{2})|(\d{4}-\d{2}-\d{2})) (?P<time>\d{2}:\d{2}:\d{2}\.\d{6})"
stratum_disable_port_re = r"Disabling port (?P<sdkPort>\d+) in node"
stratum_enable_port_re = r"Enabling port (?P<sdkPort>\d+) in node"
stratum_port_detect_re = r"State of port (?P<sdkPort>\d+) in node (\d+) \(SDK port (\d+)\): (?P<state>UP|DOWN)"
stratum_p4_write_success_re = r"P4-based forwarding entities written successfully to node"
stratum_controller_connect_re = r"is connected as (\w+) for node"
stratum_p4_write_fail_re = r"Failed to write forwarding entries to node 1: One or more write operations failed."
stratum_error_re = r"ERROR"

################## STRATUM WRITE REQUESTS REGULAR EXPRESSIONS ##################
defaultStratumWritesLineRE = r"(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}\.\d{6})"
write_entity_RE = r"type: (?P<operation>\w+) entity"

################ LINES USED FOR TIMESTAMPS ##########################
selectedLines = { 'stratum_disabling_port': [],
                  'stratum_enabling_port': [],
                  'onos_receives_port_update': [],
                  'stratum_port_down': [],
                  'stratum_port_up': [],
                  'onos_p4_switch_down': [],
                  'onos_gnmi_switch_down': [],
                  'onos_sr_switch_down': [],
                  'stratum_controller_connect': [],
                  'onos_gnmi_switch_state': [],
                  'onos_p4rt_channel_open': [],
                  'onos_port_down_device_manager': [],
                  'onos_port_up_device_manager': [],
                  'onos_sr_port_updated': [],
                  'onos_sr_link_added': [],
                  'onos_sr_link_removed': [],
                  'onos_sr_remove_bucket': [],
                  'onos_sr_add_bucket': [],
                  'onos_sr_mpls_rule': [],
                  'onos_sr_wildcard_event': [],
                  'onos_p4_write_request_update': [],
                  'onos_p4_write_request': [],
                  'onos_p4_write_response': [],
                  'onos_p4_write_response_fail': [],
                  'onos_error': [],
                  'stratum_error': [],
                  'stratum_p4_write': [],
                  'stratum_p4_write_fail': [],
                  'stratum_modify': [],
                  'stratum_insert': [],
                  'stratum_delete': [] }

def parseLine( line, lineRE, pod=None, startDT=None, endDT=None ):
    """
    Returns a dict of the line and its components
    expects the lineRE to contain named groups, among them "time" and "pod"
    """
    match = re.search( lineRE, line )
    if not match:
        if DEBUG > 2:
            print( repr( line ) )
            print( "COULDN'T MATCH LINE RE" )
        return

    output = match.groupdict()
    output[ 'line' ] = line
    if pod:
        output[ 'pod' ] = pod
    if not output.get('pod') and DEBUG > 1:
        print( output )
        print( "COULDN'T FIND NODE" )
    # Add datetime for easier math later
    date = output[ 'date' ]
    time = output[ 'time' ]
    dateFmt = '%Y-%m-%d' if '-' in date else '%Y%m%d'
    if '.' in time:
        timeFmt = '%H:%M:%S.%f'
    elif ',' in time:
        timeFmt = '%H:%M:%S,%f'
    # TODO: Default time format?

    dt = datetime.datetime.strptime( "%s %s" % ( date, time ), '%s %s' % ( dateFmt, timeFmt ) )
    if startDT and dt < startDT:
        return None
    if endDT and dt > endDT:
        return None
    outputFmt = '%Y-%m-%d %H:%M:%S.%f'
    output[ 'datetime' ] = datetime.datetime.strftime( dt, outputFmt )
    return output

def readLog( log, lineRE, pod=None, startDT=None, endDT=None ):
    """
    Parse a log file
    If using stern, pod will be parsed from the log, if the file is from a
    single switch, pod can be supplied
    RE must have 'date' and 'time' as named groups and
    'pod' and 'app' as optional named groups
    """
    foundLines = []
    with open( log, "r" ) as logFile:
        if DEBUG:
            print( "Reading file: %s" % log )
        for line in logFile:
            parsed = parseLine( line, lineRE, pod, startDT, endDT )
            if not parsed:
                continue
            foundLines.append( parsed )
    return foundLines

def ignoreLine( line, lineType, writeActivity, deviceName=None ):
    """
    We try to filter out writes that aren't related to the rerouting caused by topology change.
    writeActivity is a dictionary with key's being a cause for writes and a map of log lines with counters for how many we include
    """
    assert lineType == "onos_write_request" or\
           lineType == "onos_write_success" or\
           lineType == "onos_write_fail" or\
           lineType == "stratum_success" or\
           lineType == "stratum_fail"
    if not deviceName:
        deviceName = line[ 'deviceName' ]
    if DEBUG:
        print( "parsing line: " )
        print( line )
    acceptCauses = [ 'addBucket', 'removeBucket', 'mplsRule' ]
    ignored = True
    for cause in acceptCauses:
        count = writeActivity[ deviceName ][ cause ]
        if count['writes']:
            if count[ 'onos_write_req' ] < count[ 'writes' ]:
                if lineType == "onos_write_request":
                    count[ 'onos_write_req' ] += 1
                    if DEBUG:
                        print( "Including line for %s" % cause )
                    ignored = False
            if count[ 'onos_write_resp' ] < count[ 'onos_write_req' ]:
                if lineType == "onos_write_fail":
                    # We will retry?
                    pass
                    #count[ 'writes' ] += 1
                if lineType == "onos_write_success" or lineType == "onos_write_fail":
                    count[ 'onos_write_resp' ] += 1
                    if DEBUG:
                        print( "Including line for %s" % cause )
                    ignored = False
            if count[ 'stratum_write' ] < count[ 'onos_write_req' ]:
                if lineType == "stratum_fail":
                    pass
                    #count[ 'ignored_write' ] += 1
                if lineType == "stratum_success" or lineType == "stratum_fail":
                    count[ 'stratum_write' ] += 1
                    if DEBUG:
                        print( "Including line for %s\n" % cause )
                    ignored = False
            if ignored:
                if DEBUG:
                    print( "DEBUG: writeActivity - ignored writes during a non ignored write")
                    print( writeActivity[ deviceName ] )
            else:
                if DEBUG:
                    print( writeActivity[ deviceName ] )
                if count[ 'stratum_write' ] == count[ 'writes' ] and\
                   count[ 'onos_write_resp' ] == count[ 'writes' ] and\
                   count[ 'onos_write_req' ] == count[ 'writes' ]:
                        for key, value in count.items():
                                count[ key ] = 0
                break
    if ignored:
        if DEBUG:
            print( "Line ignored\n" )
    return ignored

def analyzeLogs( lines, podMapping ):
    """
    Analyze a list of parsed log lines and pull out selected log lines. These can be a combined stream of multiple log files
    """
    if DEBUG:
        print( "\n"*3 )
        print( "Analyzing merged logs" )
        print( "\n"*3 )
    writeDict = { "writes": 0,
                  "onos_write_req": 0,
                  "onos_write_resp": 0,
                  "stratum_write": 0 }
    writeActivity = {
        node: {
            "removeBucket": deepcopy(writeDict),
            "addBucket": deepcopy(writeDict),
            "mplsRule": deepcopy(writeDict)
        }
        for pod, node in podMapping.items()
    }

    for line in lines:
        m = re.search( p4rt_switch_down_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            if DEBUG:
                print( "parsing line: " )
                print( line )
            selectedLines[ 'onos_p4_switch_down' ].append( line )
            if DEBUG:
                print( "Line added\n" )
            continue
        m = re.search( gnmi_switch_down_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            if DEBUG:
                print( "parsing line: " )
                print( line )
            selectedLines[ 'onos_gnmi_switch_down' ].append( line )
            if DEBUG:
                print( "Line added\n" )
            continue
        m = re.search( gnmi_update_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            if DEBUG:
                print( "parsing line: " )
                print( line )
            selectedLines[ 'onos_receives_port_update' ].append( line )
            if DEBUG:
                print( "Line added\n" )
            continue
        m = re.search( gnmi_switch_state_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            if DEBUG:
                print( "parsing line: " )
                print( line )
            selectedLines[ 'onos_gnmi_switch_state' ].append( line )
            if DEBUG:
                print( "Line added\n" )
            continue
        m = re.search( device_manager_port_change_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            if DEBUG:
                print( "parsing line: " )
                print( line )
            state = m.group( 'state' )
            if state == "false":
                selectedLines[ 'onos_port_down_device_manager' ].append( line )
            if state == "true":
                selectedLines[ 'onos_port_up_device_manager' ].append( line )
            if DEBUG:
                print( "Line added\n" )
            continue
        m = re.search( sr_switch_down_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            if DEBUG:
                print( "parsing line: " )
                print( line )
            selectedLines[ 'onos_sr_switch_down' ].append( line )
            if DEBUG:
                print( "Line added\n" )
            continue
        m = re.search( p4rt_channel_open_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            if DEBUG:
                print( "parsing line: " )
                print( line )
            selectedLines[ 'onos_p4rt_channel_open' ].append( line )
            if DEBUG:
                print( "Line added\n" )
            continue
        m = re.search( sr_rule_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            if DEBUG:
                print( "parsing line: " )
                print( line )
            writeActivity[ line[ 'deviceName' ] ][ 'mplsRule' ][ 'writes' ] += 1
            selectedLines[ 'onos_sr_mpls_rule' ].append( line )
            if DEBUG:
                print( "Line added\n" )
            continue
        m = re.search( sr_far_installation_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            if DEBUG:
                print( "parsing line: " )
                print( line )
            #writeActivity[ line[ 'deviceName' ] ][ 'farInstall' ][ 'ignored_write' ] = 1
            # NOTE: Without knowing which device this gets written to, not sure how to correspond writes with this
            if DEBUG:
                print( "Line ignored\n" )
            continue
        m = re.search( sr_far_removal_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            if DEBUG:
                print( "parsing line: " )
                print( line )
            #writeActivity[ line[ 'deviceName' ] ][ 'farRemove' ][ 'ignored_write' ] = 1
            # NOTE: Without knowing which device this gets written to, not sure how to correspond writes with this
            if DEBUG:
                print( "Line ignored\n" )
            continue
        m = re.search( sr_remove_re, line[ 'line' ] )
        if m:
            # TODO: measure first to last of these events
            line.update( m.groupdict() )
            if DEBUG:
                print( "parsing line: " )
                print( line )
            writeActivity[ line[ 'deviceName' ] ][ 'removeBucket' ][ 'writes' ] += 2
            selectedLines[ 'onos_sr_remove_bucket' ].append( line )
            if DEBUG:
                print( "Line added\n" )
            continue
        m = re.search( sr_add_re, line[ 'line' ] )
        if m:
            # TODO: measure first to last of these events
            line.update( m.groupdict() )
            if DEBUG:
                print( "parsing line: " )
                print( line )
            writeActivity[ line[ 'deviceName' ] ][ 'addBucket' ][ 'writes' ] += 2
            selectedLines[ 'onos_sr_add_bucket' ].append( line )
            if DEBUG:
                print( "Line added\n" )
            continue
        m = re.search( sr_port_updated_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            if DEBUG:
                print( "parsing line: " )
                print( line )
            selectedLines[ 'onos_sr_port_updated' ].append( line )
            if DEBUG:
                print( "Line added\n" )
            continue
        m = re.search( sr_link_added_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            if DEBUG:
                print( "parsing line: " )
                print( line )
            selectedLines[ 'onos_sr_link_added' ].append( line )
            if DEBUG:
                print( "Line added\n" )
            continue
        m = re.search( sr_link_removed_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            if DEBUG:
                print( "parsing line: " )
                print( line )
            selectedLines[ 'onos_sr_link_removed' ].append( line )
            if DEBUG:
                print( "Line added\n" )
            continue
        m = re.search( sr_event_re, line[ 'line' ] )
        if m:
            # This is any other important event from SR
            line.update( m.groupdict() )
            if DEBUG:
                print( "parsing line: " )
                print( line )
            selectedLines[ 'onos_sr_wildcard_event' ].append( line )
            if DEBUG:
                print( "Line added\n" )
            continue
        m = re.search( p4rt_cleanup_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            if DEBUG:
                print( "parsing line: " )
                print( line )
            #writeActivity[ line[ 'deviceName' ] ][ 'cleanup' ][ 'ignored_write' ] = 1
            if DEBUG:
                print( "Line ignored\n" )
            continue
        m = re.search( sr_port_filter_removal_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            # Ignore 1 for leaf and 2 for spines?
            # TODO: This seems really hacky to me
            deviceName = line[ 'deviceName' ]
            if DEBUG:
                print( "parsing line: " )
                print( line )
            #if "spine" in deviceName:
            #    writeActivity[ deviceName ][ 'removeFilters' ][ 'ignored_write' ] = 2
            #else:
            #    writeActivity[ deviceName ][ 'removeFilters' ][ 'ignored_write' ] = 1
            if DEBUG:
                print( "Line ignored\n" )
            continue
        m = re.search( sr_port_filter_program_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            # Ignore 1 for leaf and 2 for spines?
            # TODO: This seems really hacky to me
            deviceName = line[ 'deviceName' ]
            if DEBUG:
                print( "parsing line: " )
                print( line )
            #if "spine" in deviceName:
            #    writeActivity[ deviceName ][ 'addFilters' ][ 'ignored_write' ] = 2
            #else:
            #    writeActivity[ deviceName ][ 'addFilters' ][ 'ignored_write' ] = 1
            if DEBUG:
                print( "Line ignored\n" )
            continue
        m = re.search( p4rt_write_request_update_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            if DEBUG:
                print( "parsing line: " )
                print( line )
            selectedLines[ 'onos_p4_write_request_update' ].append( line )
            if DEBUG:
                print( "Line added\n" )
            continue
        m = re.search( p4rt_write_request_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            if ignoreLine( line, "onos_write_request", writeActivity ):
                continue
            selectedLines[ 'onos_p4_write_request' ].append( line )
            continue
        m = re.search( p4rt_write_response_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            if ignoreLine( line, "onos_write_success", writeActivity ):
                continue
            selectedLines[ 'onos_p4_write_response' ].append( line )
            continue
        m = re.search( p4rt_unable_to_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            if ignoreLine( line, "onos_write_fail", writeActivity ):
                continue
            selectedLines[ 'onos_p4_write_response_fail' ].append( line )
            continue
        m = re.search( onos_error_re, line[ 'line' ] )
        # FIXME: This matches all "ERROR" in any line, since at this point we aren't looking where it came from
        if m:
            line.update( m.groupdict() )
            if DEBUG:
                print( "parsing line: " )
                print( line )
            selectedLines[ 'onos_error' ].append( line )
            if DEBUG:
                print( "Line added\n" )
            continue
        m = re.search( stratum_disable_port_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            if DEBUG:
                print( "parsing line: " )
                print( line )
            selectedLines[ 'stratum_disabling_port' ].append( line )
            if DEBUG:
                print( "Line added\n" )
            continue
        m = re.search( stratum_enable_port_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            if DEBUG:
                print( "parsing line: " )
                print( line )
            selectedLines[ 'stratum_enabling_port' ].append( line )
            if DEBUG:
                print( "Line added\n" )
            continue
        m = re.search( stratum_port_detect_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            if DEBUG:
                print( "parsing line: " )
                print( line )
            state = m.group( 'state' )
            if state == "DOWN":
                selectedLines[ 'stratum_port_down' ].append( line )
            if state == "UP":
                selectedLines[ 'stratum_port_up' ].append( line )
            if DEBUG:
                print( "Line added\n" )
            continue
        m = re.search( stratum_p4_write_success_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            deviceName = podMapping[ line[ 'pod' ] ]
            if ignoreLine( line, "stratum_success", writeActivity, deviceName ):
                continue
            selectedLines[ 'stratum_p4_write' ].append( line )
            continue
        m = re.search( stratum_p4_write_fail_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            deviceName = podMapping[ line[ 'pod' ] ]
            if ignoreLine( line, "stratum_fail", writeActivity, deviceName ):
                continue
            selectedLines[ 'stratum_p4_write_fail' ].append( line )
            continue
        m = re.search( stratum_controller_connect_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            if DEBUG:
                print( "parsing line: " )
                print( line )
            selectedLines[ 'stratum_controller_connect' ].append( line )
            if DEBUG:
                print( "Line added\n" )
            continue
        m = re.search( write_entity_RE, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            if DEBUG:
                print( "parsing line: " )
                print( line )
            # TODO: Ignore Line?
            """
            operation = m.group( 'operation' )
            if operation == "MODIFY":
                selectedLines[ 'stratum_modify' ].append( line )
            elif operation == "INSERT":
                selectedLines[ 'stratum_insert' ].append( line )
            elif operation == "DELETE":
                selectedLines[ 'stratum_delete' ].append( line )
            else:
                raise NotImplementedError
            """
            if DEBUG:
                print( "Line added\n" )
            continue
        m = re.search( stratum_error_re, line[ 'line' ] )
        if m:
            line.update( m.groupdict() )
            if DEBUG:
                print( "parsing line: " )
                print( line )
            selectedLines[ 'stratum_error' ].append( line )
            if DEBUG:
                print( "Line added\n" )
            continue

def sortByDateTime( parsed ):
    """
    Returns the key used to sort the parsed line dictionary by date/time
    """
    date = parsed[ 'date' ]
    dateRE = r"(?P<year>\d{4})[:\-/]?(?P<month>\d{2})[:\-/]?(?P<day>\d{2})"
    m1 = re.search( dateRE, date )
    time = parsed[ 'time' ]
    timeRE = r"(?P<hours>\d{2}):(?P<minutes>\d{2}):(?P<seconds>\d{2})(,|\.)(?P<ms>\d{3,9})"
    m2 = re.search( timeRE, time )
    return "%s-%s-%s %s:%s:%s.%s" % ( m1.group( 'year' ),
                                      m1.group( 'month' ),
                                      m1.group( 'day' ),
                                      m2.group( 'hours' ),
                                      m2.group( 'minutes' ),
                                      m2.group( 'seconds' ),
                                      m2.group( 'ms' ) )

def duration( stop, start ):
    """
    Returns the difference between two time stamps in ms
    """
    #fmt = '%Y-%m-%d %H:%M:%S.%f'
    stopDT = datetime.datetime.strptime( stop, TIMEFMT )
    startDT = datetime.datetime.strptime( start, TIMEFMT )
    result = stopDT - startDT
    return result.total_seconds() * 1000

def readLogsFromTestFolder( startDT, endDT,
                            testDir=None,
                            onosLineRE=defaultOnosLineRE,
                            stratumLineRE=defaultStratumLineRE,
                            stratumWritesLineRE=defaultStratumWritesLineRE ):
    import os

    podMappingFile = "podMapping.txt"
    pod_mapping_re = r"(?P<pod>stratum-\w{5})( +[^ ]+){5}( )+(?P<deviceName>\w+)"
    onos_log_prefix = "onos-tost-onos-classic-"
    stratum_log_prefix = "stratum-"
    stratum_write_log_suffix = "write-reqs.txt"
    tempMapping = {}
    tempLines = []
    onos_files = []
    stratum_files = []
    write_files = []
    fileName = "%s/%s" % ( testDir, podMappingFile ) if testDir else podMappingFile
    with open( fileName, "r" ) as logFile:
        for line in logFile:
            m = re.search( pod_mapping_re, line )
            if not m:
                continue
            tempMapping[ m.group( 'pod' ) ] = m.group( 'deviceName' )
    if DEBUG:
        print( tempMapping )
    # Search for all files

    rootDir = testDir if testDir else "."
    for root, dirs, files in os.walk( rootDir ):
        for f in files:
            if f.startswith( onos_log_prefix ):
                onos_files.append( os.path.join( rootDir, f ) )
            elif f.startswith( stratum_log_prefix ):
                stratum_files.append( os.path.join( rootDir, f ) )
            elif f.endswith( stratum_write_log_suffix ):
                write_files.append( os.path.join( rootDir, f ) )
    # parse each file
    for f in onos_files:
        try:
            startIndex = f.rindex( '/' ) + 1
        except ValueError:
            startIndex = 0
        pod = f[ startIndex : -4  ]
        tempLines.extend( readLog( f, onosLineRE, pod=pod, startDT=startDT, endDT=endDT ) )
    for f in stratum_files:
        try:
            startIndex = f.rindex( '/' ) + 1
        except ValueError:
            startIndex = 0
        pod = f[ startIndex : -4  ]
        tempLines.extend( readLog( f, stratumLineRE, pod=pod, startDT=startDT, endDT=endDT ) )
    for f in write_files:
        pod = None
        for p in tempMapping:
            if p in f:
                pod = p
                break
        # FIXME: Pod name isn't correct
        tempLines.extend( readLog( f, stratumWritesLineRE, pod=pod, startDT=startDT, endDT=endDT ) )


    #print( tempLines )
    return tempLines, tempMapping



def main():
    # First arg is ONOS logs
    # second arg is stratum logs
    # third arg is stratum write requests
    lines = []
    # TODO: These should be read as arguments

    manualTriggerTime = ""
    ##### These are for the logs found here:
    ##### https://drive.google.com/drive/folders/1_Mil7OINIS54McKHN4MngzGR1e6KEKtX?usp=sharing
    # disable-spine2-leaf1-links.*
    enbPortDown1StartStr = "2021-01-30 00:06:12.0000"
    enbPortDown1EndStr = "2021-01-30 00:06:40.00000"
    enbPortDown2EndStr = "2021-01-30 00:06:47.0000"

    # enable-spine2-leaf1-links.*
    enbPortUp1StartStr = "2021-01-30 00:08:30.0000"
    enbPortUp1EndStr = "2021-01-30 00:09:00.00000"
    enbPortUp2EndStr = "2021-01-30 00:09:10.00000"

    # portstate-spine2-leaf1-links.*
    enbPortDown3StartStr = "2021-01-30 00:13:00.000"
    enbPortDown3EndStr = "2021-01-30 00:13:30.00000"
    enbPortDown4EndStr = "2021-01-30 00:13:50.0000"
    enbPortUp3StartStr = "2021-01-30 00:16:50.0000"
    enbPortUp3EndStr = "2021-01-30 00:17:00.00000"
    enbPortUp4EndStr = "2021-01-30 00:17:50.00000"


    # disable-spine2-leaf2-links.*
    upstreamPortDown1StartStr = "2021-01-29 23:57:30.0000"
    upstreamPortDown1EndStr = "2021-01-29 23:57:40.00000"
    upstreamPortDown2EndStr = "2021-01-29 23:58:50.0000"

    # enable-spine2-leaf2-links.*
    upstreamPortUp1StartStr = "2021-01-30 00:01:50.0000"
    upstreamPortUp1EndStr = "2021-01-30 00:02:00.00000"
    upstreamPortUp2EndStr = "2021-01-30 00:02:30.00000"

    # unplug-leaf2-spine1.*
    unpluglink1Start = "2021-01-29 23:49:30.0000"
    unpluglink1End = "2021-01-29 23:50:00.0000"
    pluglink1End = "2021-01-29 23:50:33.0000"

    # powercycle-spine1.*
    powerDown1Start = "2021-01-29 23:19:17.0000"
    powerDown1End = "2021-01-29 23:19:19.0000"
    powerUp1Start = "2021-01-29 23:23:33.0000"
    powerUp1End = "2021-01-29 23:23:45.0000"

    # onl-reboot-spine1.*
    onlDown1Start = "2021-01-29 23:32:00.0000"
    onlDown1End = "2021-01-29 23:36:20.0000"
    onlUp1Start = "2021-01-29 23:36:20.0000"
    onlUp1End = "2021-01-29 23:36:35.0000"


    event_selection = 3
    if event_selection == 1:
        # enb link down1
        startStr = enbPortDown1StartStr
        endStr = enbPortDown1EndStr
        event = "portstate_down"
        eventType = "failure"
    elif event_selection == 2:
        # enb link down2
        startStr = enbPortDown1EndStr
        endStr = enbPortDown2EndStr
        event = "portstate_down"
        eventType = "failure"
    elif event_selection == 3:
        # enb link up1
        startStr = enbPortUp1StartStr
        endStr = enbPortUp1EndStr
        event = "portstate_up"
        eventType = "recovery"
    elif event_selection == 4:
        # enb link up2
        startStr = enbPortUp1EndStr
        endStr = enbPortUp2EndStr
        event = "portstate_up"
        eventType = "recovery"
    elif event_selection == 5:
        # enb link down3
        startStr = enbPortDown3StartStr
        endStr = enbPortDown3EndStr
        event = "portstate_down"
        eventType = "failure"
    elif event_selection == 6:
        # enb link down4
        startStr = enbPortDown3EndStr
        endStr = enbPortDown4EndStr
        event = "portstate_down"
        eventType = "failure"
    elif event_selection == 7:
        # enb link up3
        startStr = enbPortUp3StartStr
        endStr = enbPortUp3EndStr
        event = "portstate_up"
        eventType = "recovery"
    elif event_selection == 8:
        # enb link up4
        startStr = enbPortUp3EndStr
        endStr = enbPortUp4EndStr
        event = "portstate_up"
        eventType = "recovery"
    elif event_selection == 9:
        # upstream link down1
        startStr = upstreamPortDown1StartStr
        endStr = upstreamPortDown1EndStr
        event = "portstate_down"
        eventType = "failure"
    elif event_selection == 10:
        # upstream link down2
        startStr = upstreamPortDown1EndStr
        endStr = upstreamPortDown2EndStr
        event = "portstate_down"
        eventType = "failure"
    elif event_selection == 11:
        # upstream link up1
        startStr = upstreamPortUp1StartStr
        endStr = upstreamPortUp1EndStr
        event = "portstate_up"
        eventType = "recovery"
    elif event_selection == 12:
        # upstream link up2
        startStr = upstreamPortUp1EndStr
        endStr = upstreamPortUp2EndStr
        event = "portstate_up"
        eventType = "recovery"
    elif event_selection == 13:
        # unplug link
        startStr = unpluglink1Start
        endStr = unpluglink1End
        event = "unplug_link"
        eventType = "failure"
    elif event_selection == 14:
        # plug link
        startStr = unpluglink1End
        endStr = pluglink1End
        event = "plug_link"
        eventType = "recovery"
    elif event_selection == 15:
        # power down switch
        startStr = powerDown1Start
        endStr = powerDown1End
        event = "powerdown_switch"
        eventType = "failure"
    elif event_selection == 16:
        # power up switch
        startStr = powerUp1Start
        endStr = powerUp1End
        event = "powerup_switch"
        eventType = "recovery"
    elif event_selection == 17:
        # onl shutdown on switch
        startStr = onlDown1Start
        endStr = onlDown1End
        event = "powerdown_switch"
        eventType = "failure"
    elif event_selection == 18:
        # onl start on switch
        startStr = onlUp1Start
        endStr = onlUp1End
        event = "powerup_switch"
        eventType = "recovery"
    elif event_selection == 19:
        # onl shutdown on switch
        # SRONLReboot_30_Mar_2021_08_27_02
        #manualTriggerTime = "2021-03-30 08:29:17.534335"
        startStr = "2021-03-30 08:28:52.206714"
        endStr = "2021-03-30 08:30:22.642694"
        event = "shutdown_onl"
        eventType = "failure"
    elif event_selection == 20:
        # onl start on switch
        # SRONLReboot_30_Mar_2021_08_27_02
        startStr = "2021-03-30 08:29:22.642694"
        endStr = "2021-03-30 08:33:12.293721"
        event = "start_onl"
        eventType = "recovery"
    # TODO: Read from a `get pods -o wide output`
    podMapping = {"stratum-7dtb8": "leaf1",
                  "stratum-c4p42": "spine2",
                  "stratum-jbb5w": "leaf2",
                  "stratum-49fwj": "spine1" }

    ######### Manual testing, test will do this  ########
    p1down = "2021-06-08 10:02:28.842681"
    p2down = "2021-06-08 10:05:47.638684"
    p1up = "2021-06-08 10:08:54.974723"
    p2up = "2021-06-08 10:11:44.923067"
    p3down = "2021-06-08 10:14:48.605082"
    p4down = "2021-06-08 10:18:00.892514"
    p3up = "2021-06-08 10:20:59.108350"
    p4up = "2021-06-08 10:23:53.826612"
    times = [ p1down, p2down, p1up, p2up, p3down, p4down, p3up, p4up ]
    startStr = times[2]
    endStr = times[3]
    event = 'portstate_up'
    prefix = "recovery1"
    #####################################################

    #fmt = '%Y-%m-%d %H:%M:%S.%f'
    endDT = datetime.datetime.strptime( endStr, TIMEFMT )
    startDT = datetime.datetime.strptime( startStr, TIMEFMT )

    # Read files
    if len( sys.argv ) > 1:
        try:
            onos_logfile = sys.argv[1]
            lines.extend( readLog( onos_logfile, defaultOnosLineRE, startDT=startDT, endDT=endDT ) )
        except IndexError:
            print( "ERROR: COULD NOT FIND ONOS LOG FILE" )
        try:
            stratum_logfile = sys.argv[2]
            lines.extend( readLog( stratum_logfile, defaultStratumLineRE, startDT=startDT, endDT=endDT ) )
        except IndexError:
            print( "ERROR: COULD NOT FIND STRATUM LOG FILE" )
        try:
            stratum_writes_logfile = sys.argv[3]
            lines.extend( readLog( stratum_writes_logfile, defaultStratumWritesLineRE, pod="stratum-g6k7", startDT=startDT, endDT=endDT ) )
        except IndexError:
            print( "ERROR: COULD NOT FIND STRATUM WRITE REQUESTS FILE" )
    else:
        # Read files from cwd
        lines, podMapping = readLogsFromTestFolder( startDT, endDT )

    # Sort merged files by time
    ordered_lines = sorted( lines, key=sortByDateTime )

    # TODO: Make a function
    mergedLogFile = "%s-mergedLogs.txt" % prefix
    with open( mergedLogFile, 'w' ) as output:
        for line in ordered_lines:
            output.write( "%s %s" % ( line['pod'], line['line'] ) )

    if DEBUG:
        for line in ordered_lines:
            #print( repr( line['line'] ) )
            print( line )

    # pull out interesting log lines
    analyzeLogs( ordered_lines, podMapping )
    breakdownEvent( event, podMapping )

def breakdownEvent( event, podMapping, manualTriggerTime=None, outputFile="log_breakdown_output.txt", DEBUG=0 ):

    results = {}
    with open( outputFile, 'w' ) as outFile:
        if DEBUG:
            outFile.write("\n\nSelected Lines in order:\n")
        selectedLinesList = []
        for cause in selectedLines:
            selectedLinesList.extend( selectedLines[cause] )
        sorted_selectedLinesList = sorted( selectedLinesList, key=sortByDateTime )
        if DEBUG:
            outFile.write( json.dumps( sorted_selectedLinesList, sort_keys=True, indent=4 ) )
        # FOR DEBUG
        if DEBUG:
            outFile.write("\n\nSelected Lines by group:\n")
            for eventLabel, eventLines in selectedLines.items():
                outFile.write( eventLabel )
                outFile.write( '\n' )
                outFile.write( json.dumps( eventLines, sort_keys=True, indent=4 ) )
                outFile.write( '\n' )

        writeCauses = [ 'onos_sr_add_bucket', 'onos_sr_remove_bucket', 'onos_sr_mpls_rule' ]
        trellisEvents = [ 'onos_sr_port_updated', 'onos_sr_switch_down', 'onos_sr_link_added', 'onos_sr_link_removed' ]
        if event == 'portstate_down':
            eventType = "failure"
            triggerLine = 'stratum_disabling_port'
            onosDetectEvent = 'onos_receives_port_update'
            rerouteCauses = [ 'onos_sr_remove_bucket' ]
            switchEvents = [ 'stratum_port_down' ]
        elif event == 'portstate_up':
            eventType = "recovery"
            triggerLine = 'stratum_enabling_port'
            onosDetectEvent = 'onos_receives_port_update'
            rerouteCauses = [ 'onos_sr_add_bucket' ]
            switchEvents = [ 'stratum_port_up' ]
        elif event == 'unplug_link':
            eventType = "failure"
            onosDetectEvent = 'onos_receives_port_update'
            rerouteCauses = [ 'onos_sr_remove_bucket' ]
            switchEvents = [ 'stratum_port_down' ]
            # TODO: pass in manual trigger time
            triggerLine = switchEvents[0]
        elif event == 'plug_link':
            eventType = "recovery"
            onosDetectEvent = 'onos_receives_port_update'
            rerouteCauses = [ 'onos_sr_add_bucket' ]
            switchEvents = [ 'stratum_port_up' ]
            # TODO: pass in manual trigger time
            triggerLine = switchEvents[0]
        elif event == 'powerdown_switch':
            eventType = "failure"
            onosDetectEvent = 'onos_port_down_device_manager'
            rerouteCauses = [ 'onos_sr_remove_bucket' ]
            switchEvents = [ 'stratum_port_down' ]
            # TODO: pass in manual trigger time
            triggerLine = switchEvents[0]
        elif event in ['powerup_switch', 'start_onl']:
            eventType = "recovery"
            # Even though this is a manual event, we really shouldn't count the time for the switch to boot up
            triggerLine = 'stratum_controller_connect'
            """
            Trigger could be the first of these? Its possible switch's time is out of sync when first starts, often see events out of order on these recovery cases
                      'stratum_controller_connect': [],
                      'onos_p4rt_channel_open': [],
            """
            onosDetectEvent = 'onos_p4rt_channel_open'
            rerouteCauses = [ 'onos_sr_mpls_rule' ]
            switchEvents = [ 'stratum_port_up' ]
        elif event == 'shutdown_onl':
            eventType = "failure"
            onosDetectEvent = 'onos_gnmi_switch_state'
            rerouteCauses = [ 'onos_sr_remove_bucket' ]
            switchEvents = [ 'stratum_port_down' ]
            # TODO: pass in manual trigger time
            triggerLine = onosDetectEvent

        if eventType == "failure":
            trellis_link = 'onos_sr_link_removed'
        elif eventType == "recovery":
            trellis_link = 'onos_sr_link_added'

        temp_list = []
        for cause in rerouteCauses:
            temp_list.extend( selectedLines[cause] )
        if len( temp_list ) == 0:
            outFile.write( "\nWARNING Could Not find a cause for rerouting, looking for all causes" )
        for cause in writeCauses:
            temp_list.extend( selectedLines[cause] )
        sorted_reroute_causes = sorted( temp_list, key=sortByDateTime )
        temp_list = []
        for e in switchEvents:
            temp_list.extend( selectedLines[e] )
        sorted_switch_events = sorted( temp_list, key=sortByDateTime )
        if sorted_switch_events:
            last_switch_event = sorted_switch_events[-1]['datetime']
        if sorted_reroute_causes:
            n2s_start = sorted_reroute_causes[0]['datetime']
            trellis_programming_finish = sorted_reroute_causes[-1]['datetime']
        else:
            n2s_start = None
            trellis_programming_finish = None

        temp_list = []
        for e in trellisEvents:
            temp_list.extend( selectedLines[e] )
        sorted_trellis_events = sorted( temp_list, key=sortByDateTime )
        if DEBUG:
            outFile.write( "\nSorted Trellis events\n" )
            for line in sorted_trellis_events:
                outFile.write( str( line ) )

        if manualTriggerTime:
            trigger = manualTriggerTime
            triggerEvent = {}
        else:
            if not triggerLine:
                triggerEvent = sorted_switch_events[0]
            else:
                triggerEvent = selectedLines[ triggerLine ][0]
            trigger = triggerEvent['datetime']
        triggerDT = datetime.datetime.strptime( trigger, TIMEFMT )
        # Group events by switch
        switchDict = { 'onos_sr_add_bucket': [],
                       'onos_sr_remove_bucket': [],
                       'onos_sr_mpls_rule': [],
                       'onos_p4_write_request': [],
                       'onos_p4_write_response': [],
                       'onos_p4_write_response_fail': [],
                       'stratum_p4_write': [],
                       'stratum_p4_write_fail': [],
                       'stratum_modify': [],
                       'stratum_insert': [],
                       'stratum_delete': [] }
        switches = {}
        for eventName in switchDict:
            for line in selectedLines[eventName]:
                eventDT = datetime.datetime.strptime(line['datetime'], TIMEFMT)
                if eventDT < triggerDT:
                    continue
                try:
                    switch = line.get('deviceName')
                    if not switch:
                        switch = podMapping[line['pod']]
                except KeyError:
                    outFile.write("\nCould not find device for line: %s" % line)
                    continue
                if switch not in switches:
                    switches[switch] = deepcopy(switchDict)
                switches[switch][eventName].append(line)

        if DEBUG:
            outFile.write( "\nevents by switch\n" )
            outFile.write( json.dumps( switches, sort_keys=True, indent=4 ) )
            outFile.write( '\n' )

        if DEBUG:
            outFile.write( "\nIgnoring late writes..." )
        for switch in switches:
            lastWriteCause = {}
            for cause in writeCauses:
                if switches[switch][cause]:
                    line = switches[switch][cause][-1]
                    if not lastWriteCause:
                        lastWriteCause = line
                    else:
                        tempDT = datetime.datetime.strptime(line['datetime'], TIMEFMT)
                        lastDT = datetime.datetime.strptime(lastWriteCause['datetime'], TIMEFMT)
                        if tempDT > lastDT:
                            lastWriteCause = line
            lastDT = datetime.datetime.strptime(lastWriteCause['datetime'], TIMEFMT)
            for e, lines in switches[switch].items():
                if lines:
                    tempList = lines
                    #outFile.write( len( lines ) )
                    lateLines = [line for line in tempList if datetime.datetime.strptime(line['datetime'], TIMEFMT) > ( lastDT + datetime.timedelta( 0, 1 ) ) ]
                    if lateLines:
                        outFile.write( "\nWARNING: Ignoring %s %s on %s that came >1 second after write cause(script likely expected more writes from cause than happened)\n" % ( len(lateLines), e, switch ) )
                        outFile.write( json.dumps( lateLines, sort_keys=True, indent=4 ) )
                    # remove from switch dict
                    switches[switch][e] = [ line for line in tempList if line not in lateLines ]
                    # remove from selected lines
                    selectedLines[e] = [ line for line in selectedLines[e] if line not in lateLines ]

        temp_list = []
        for cause in [ 'onos_p4_write_response', 'onos_p4_write_response_fail' ]:
            temp_list.extend( selectedLines[cause] )
        sorted_acks = sorted( temp_list, key=sortByDateTime )

        onos_first_detect = selectedLines[ onosDetectEvent ][0]['datetime']  # Same for port down/up
        trellis_start = sorted_trellis_events[0]['datetime']
        trellis_first_link = selectedLines[ trellis_link ][0]['datetime']
        trellis_last_link = selectedLines[ trellis_link ][-1]['datetime']
        n2s_finish = sorted_acks[-1]['datetime']
        entire_duration = duration( n2s_finish, trigger )
        trigger_to_onos_event = duration( onos_first_detect, trigger )
        onos_to_trellis = duration( trellis_start, onos_first_detect )
        onos_to_trellis_link = duration( trellis_first_link, onos_first_detect )
        # Programming time for each switch
        trellis_processing = duration( n2s_start, trellis_start )
        trellis_processing_and_programming = duration( trellis_programming_finish, trellis_start )
        trellis_processing_and_programming_with_acks = duration( n2s_finish, trellis_start )
        n2s = duration( n2s_finish, n2s_start )

        if eventType == "failure":
            worst_case_desc = "Trigger to last write response in onos"
            worst_case = duration( n2s_finish, trigger )
        elif eventType == "recovery":
            worst_case_desc = "Start of Trellis reroute programming to last switch write response in ONOS"
            worst_case = n2s

        # Lines
        outFile.write( "\nTrigger:\n%s" % triggerEvent.get( 'line', '' ) )
        outFile.write( "\nONOS First detect:\n%s" % selectedLines[ onosDetectEvent ][0]['line'] )
        outFile.write( "\nTrellis first event:\n%s" % sorted_trellis_events[0]['line'] )
        outFile.write( "\nTrellis first link event:\n%s" % selectedLines[ trellis_link ][0]['line'] )
        if len( selectedLines[ trellis_link ] ) > 1:
            outFile.write( "\nTrellis last link event:\n%s" % selectedLines[ trellis_link ][-1]['line'] )
        outFile.write( "\nTrellis starts programming:\n%s" % sorted_reroute_causes[0]['line'] )
        outFile.write( "\nTrellis ends programming:\n%s" % sorted_reroute_causes[-1]['line'] )
        outFile.write( "\nFirst write response in onos:\n%s" % selectedLines[ 'onos_p4_write_response' ][0][ 'line' ] )
        outFile.write( "\nLast write response in onos:\n%s" % selectedLines[ 'onos_p4_write_response' ][-1][ 'line' ] )
        outFile.write( "\nFirst write success on switches:\n%s" % selectedLines[ 'stratum_p4_write' ][0][ 'line' ] )
        outFile.write( "\nLast write success on switches:\n%s" % selectedLines[ 'stratum_p4_write' ][-1][ 'line' ] )

        # Times
        outFile.write( "\nEntire duration (trigger to last write response in onos): %s ms" % entire_duration )
        outFile.write( "\nWorst case traffic loss (%s): %s ms" % ( worst_case_desc, worst_case ) )
        if sorted_switch_events:
            outFile.write( "\nTrigger to last switch event: %s ms" % ( duration( last_switch_event, trigger ) ) )
        outFile.write( "\nTrigger to first onos event: %s ms   \t\t\t\t\t(top box under the switches)" % trigger_to_onos_event )
        results[ 'trigger_to_onos_event' ] = trigger_to_onos_event
        outFile.write( "\nFirst ONOS event to first Trellis event: %s ms\t\t\t\t\t(South to North)" % onos_to_trellis )
        results[ 's2n' ] = onos_to_trellis
        outFile.write( "\nFirst ONOS event to first Trellis Link event: %s ms" % onos_to_trellis_link )
        outFile.write( "\nFirst Trellis link event to last Trellis Link: %s ms" % duration( trellis_last_link, trellis_first_link ) )
        outFile.write( "\nFirst Trellis event to start of programming devices: %s ms" % trellis_processing )
        outFile.write( "\nFirst Trellis link event to start of programming devices: %s ms" % duration( n2s_start, trellis_first_link ) )
        outFile.write( "\nLast Trellis link event to start of programming devices: %s ms" % duration( n2s_start, trellis_last_link ) )
        outFile.write( "\nFirst Trellis event to end of Trellis programming devices: %s ms\t\t(Trellis)" % trellis_processing_and_programming )
        results[ 'trellis' ] = trellis_processing_and_programming
        outFile.write( "\nFirst Trellis link event to end of Trellis programming devices: %s ms" % duration( trellis_programming_finish, trellis_first_link ) )
        outFile.write( "\nLast Trellis link event to end of Trellis programming devices: %s ms" % duration( trellis_programming_finish, trellis_last_link ) )
        outFile.write( "\nFirst Trellis event to end of programming devices with acks: %s ms" % trellis_processing_and_programming_with_acks )
        outFile.write( "\nFirst Trellis link event to end of programming devices with acks: %s ms" % duration( n2s_finish, trellis_first_link ) )
        outFile.write( "\nStart of programming devices to last ack: %s ms\t\t\t\t(North to South)" % n2s )
        results[ 'n2s' ] = n2s
        for switchName, events in switches.items():
            try:
                writeCauseList = []
                for cause in writeCauses:
                    if events[ cause ]:
                        writeCauseList.extend( events[cause] )
                sorted_write_causes = sorted( writeCauseList, key=sortByDateTime )

                onos_p4_acks = []
                for cause in [ 'onos_p4_write_response', 'onos_p4_write_response_fail' ]:
                    onos_p4_acks.extend( events[cause] )
                sorted_onos_p4_acks = sorted( onos_p4_acks, key=sortByDateTime )

                stratum_results = []
                for cause in [ 'stratum_p4_write', 'stratum_p4_write_fail' ]:
                    stratum_results.extend( events[cause] )
                sorted_stratum_results = sorted( stratum_results, key=sortByDateTime )

                # Get pod name
                podName = ""
                for pod, sw in podMapping.items():
                    if sw == switchName:
                        podName = pod

                outFile.write( "\n----------Results for %s%s----------" % ( switchName, "(%s)" % podName if podName else "" ) )
                programming_cause = sorted_write_causes[ 0 ]
                programmingDT = datetime.datetime.strptime( programming_cause['datetime'], TIMEFMT )
                writes_after_programming = [ line for line in events['onos_p4_write_request'] if datetime.datetime.strptime( line['datetime'], TIMEFMT ) >= programmingDT ]
                write_responses_after_programming = [ line for line in sorted_onos_p4_acks if datetime.datetime.strptime( line['datetime'], TIMEFMT ) >= programmingDT ]
                stratum_success_after_programming = [ line for line in events['stratum_p4_write'] if datetime.datetime.strptime( line['datetime'], TIMEFMT ) >= programmingDT ]
                stratum_result_after_programming = [ line for line in sorted_stratum_results if datetime.datetime.strptime( line['datetime'], TIMEFMT ) >= programmingDT ]
                onos_responses = len( sorted_onos_p4_acks )
                stratum_responses = len( events['stratum_p4_write'] ) + len( events['stratum_p4_write_fail'] )
                if len( events['onos_p4_write_request'] ) != onos_responses:
                    outFile.write( "\nWARNING: # of write requests != # of write responses on %s" % switchName )
                if onos_responses != stratum_responses:
                    outFile.write( "\nWARNING: # of write requests != # of write results on %s" % switchName )
                writeDuration = duration( stratum_success_after_programming[-1]['datetime'], programming_cause['datetime'] )
                outFile.write( "\nFirst programming to last write success for %s: %s ms" % (switchName, writeDuration ) )
                for cause in writeCauses:
                    if events[ cause ]:
                        outFile.write( "\nNumber of '%s's for %s: %s" % ( cause, switchName, len( events[cause] ) ) )
                outFile.write( "\nNumber of write requests for %s: %s" % (switchName, len( events['onos_p4_write_request'] ) ) )
                outFile.write( "\nNumber of write responses for %s: %s success, %s failed" % (switchName, len( events['onos_p4_write_response'] ), len( events['onos_p4_write_response_fail'] ) ) )
                outFile.write( "\nNumber of write results on stratum for %s: %s success, %s failed" % (switchName, len( events['stratum_p4_write'] ), len( events['stratum_p4_write_fail'] ) ) )

                # Lines per switch
                outFile.write( "\nFirst programming:\n%s" % programming_cause[ 'line' ] )
                outFile.write( "\nFirst write request from ONOS:\n%s" % writes_after_programming[0][ 'line' ] )
                outFile.write( "\nFirst write response on ONOS:\n%s" % write_responses_after_programming[0][ 'line' ] )
                outFile.write( "\nFirst write result on switch:\n%s" % stratum_success_after_programming[0][ 'line' ] )
                if len( sorted_write_causes ) > 1:
                    outFile.write( "\nLast programming:\n%s" % sorted_write_causes[-1][ 'line' ] )
                outFile.write( "\nLast write request from ONOS:\n%s" % writes_after_programming[-1][ 'line' ] )
                outFile.write( "\nLast write response on ONOS:\n%s" % write_responses_after_programming[-1][ 'line' ] )
                outFile.write( "\nLast write result on switch:\n%s" % stratum_success_after_programming[-1][ 'line' ] )

                # Times per switch
                progToReq = duration( writes_after_programming[0]['datetime'], programming_cause['datetime'] )
                outFile.write( "\nFirst programming from ONOS to first write request for %s: %s ms" % (switchName, progToReq ) )
                progToLastReq = duration( writes_after_programming[-1]['datetime'], programming_cause['datetime'] )
                outFile.write( "\nFirst programming from ONOS to last write request for %s: %s ms" % (switchName, progToLastReq ) )
                reqToRes = duration( write_responses_after_programming[0]['datetime'], writes_after_programming[0]['datetime'] )
                outFile.write( "\nFirst write request to first write response for %s: %s ms" % (switchName, reqToRes ) )
                reqToLastRes = duration( write_responses_after_programming[-1]['datetime'], writes_after_programming[0]['datetime'] )
                outFile.write( "\nFirst write request to last write response for %s: %s ms" % (switchName, reqToLastRes ) )
                resToSuc = duration( stratum_success_after_programming[0]['datetime'], write_responses_after_programming[0]['datetime'] )
                outFile.write( "\nFirst write response to first write result for %s: %s ms" % (switchName, resToSuc ) )
                resToLastSuc = duration( sorted_stratum_results[-1]['datetime'], write_responses_after_programming[0]['datetime'] )
                outFile.write( "\nFirst write response to last write result for %s: %s ms" % (switchName, resToLastSuc ) )
                successDuration = duration( stratum_result_after_programming[-1]['datetime'], stratum_result_after_programming[0]['datetime'] )
                outFile.write( "\nFirst switch write result to last write result for %s: %s ms\t\t(Bottom box under switches)" % ( switchName, successDuration ) )
                results[ '%s-writes' % switchName ] = successDuration
            except IndexError as e:
                outFile.write( "\nError processing logs for switch %s: %s" % ( switchName, e ) )
    return results


if __name__ == '__main__':
    main()
