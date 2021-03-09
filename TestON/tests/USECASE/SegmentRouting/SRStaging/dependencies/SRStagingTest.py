"""
Copyright 2017 Open Networking Foundation ( ONF )

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

from tests.USECASE.SegmentRouting.dependencies.Testcaselib import Testcaselib as run
import time
import re
import json
import pexpect

class SRStagingTest():

    def __init__( self ):
        self.default = ''
        self.topo = dict()
        # TODO: Check minFlowCount of leaf for BMv2 switch
        # (number of spine switch, number of leaf switch, dual-homed, description, minFlowCount - leaf (OvS), minFlowCount - leaf (BMv2))
        self.topo[ '0x1' ] = ( 0, 1, False, 'single ToR', 28, 20 )
        self.topo[ '0x2' ] = ( 0, 2, True, 'dual-homed ToR', 37, 37 )
        self.topo[ '2x2' ] = ( 2, 2, False, '2x2 leaf-spine topology', 37, 32 )
        self.topo[ '2x2staging' ] = ( 2, 2, True, '2x2 leaf-spine topology', 37, 32 )
        # TODO: Implement 2x3 topology
        # topo[ '2x3' ] = ( 2, 3, True, '2x3 leaf-spine topology with dual ToR and single ToR', 28 )
        self.topo[ '2x4' ] = ( 2, 4, True, '2x4 dual-homed leaf-spine topology', 53, 53 )
        self.topo[ '2x4' ] = ( 2, 4, True, '2x4 dual-homed leaf-spine topology', 53, 53 )
        self.switchNames = {}
        self.switchNames[ '0x1' ] = [ "leaf1" ]
        self.switchNames[ '2x2' ] = [ "leaf1", "leaf2", "spine101", "spine102" ]
        main.switchType = "ovs"

    def setupTest( self, main, topology, onosNodes, description, vlan=[] ):
        try:
            skipPackage = False
            init = False
            if not hasattr( main, 'apps' ):
                init = True
                run.initTest( main )
            # Skip onos packaging if the cluster size stays the same
            if not init and onosNodes == main.Cluster.numCtrls:
                skipPackage = True

            main.case( '%s, with %s, %s switches and %d ONOS instance%s' %
                       ( description, self.topo[ topology ][ 3 ],
                         main.switchType,
                         onosNodes,
                         's' if onosNodes > 1 else '' ) )

            main.Cluster.setRunningNode( onosNodes )
            # Set ONOS Log levels
            # TODO: Check levels before and reset them after
            run.installOnos( main, skipPackage=skipPackage, cliSleep=5 )

            if hasattr( main, 'Mininet1' ):
                run.mnDockerSetup( main )  # optionally create and setup docker image

                # Run the test with Mininet
                mininet_args = ' --spine=%d --leaf=%d' % ( self.topo[ topology ][ 0 ], self.topo[ topology ][ 1 ] )
                if self.topo[ topology ][ 2 ]:
                    mininet_args += ' --dual-homed'
                if len( vlan ) > 0 :
                    mininet_args += ' --vlan=%s' % ( ','.join( ['%d' % vlanId for vlanId in vlan ] ) )
                if main.useBmv2:
                    mininet_args += ' --switch %s' % main.switchType
                    main.log.info( "Using %s switch" % main.switchType )

                run.startMininet( main, 'trellis_fabric.py', args=mininet_args )

            else:
                # Run the test with physical devices
                run.connectToPhysicalNetwork( main, hostDiscovery=False )  # We don't want to do host discovery in the pod
        except Exception as e:
            main.log.exception( "Error in setupTest" )
            main.skipCase( result="FAIL", msg=e )

    def startCapturing( self, main, srcList, dst, shortDesc=None, longDesc=None ):
        """
        Starts logging, traffic generation, traffic filters, etc before a failure is induced
        src: the src component that sends the traffic
        dst: the dst component that receives the traffic
        """
        try:
            # ping right before to make sure arp is cached and sudo is authenticated
            for src in srcList:
                src.handle.sendline( "sudo /bin/ping -c 1 %s" % dst.interfaces[0]['ips'][0] )
                try:
                    i = src.handle.expect( [ "password", src.prompt ] )
                    if i == 0:
                        src.handle.sendline( src.pwd )
                        src.handle.expect( src.prompt )
                except Exception:
                    main.log.error( "Unexpected response from ping" )
                    src.handle.send( '\x03' )  # ctrl-c
                    src.handle.expect( src.prompt )
                main.log.warn( "%s: %s" % ( src.name, str( src.handle.before ) ) )
            # TODO: Create new components for iperf and tshark?
            #       Also generate more streams with differnt udp ports or some other
            #       method of guranteeing we kill a link with traffic
            # Start traffic
            # TODO: ASSERTS
            main.pingStart = time.time()
            dstIp = dst.interfaces[0]['ips'][0]
            for src in srcList:
                srcIp = src.interfaces[0]['ips'][0]
                iperfArgs = "%s --bind %s -c %s" % ( main.params[ 'PERF' ][ 'traffic_cmd_arguments' ],
                                                     srcIp,
                                                     dstIp )
                main.log.info( "Starting iperf" )
                src.handle.sendline( "/usr/bin/iperf %s &> /dev/null &" % iperfArgs )
                src.handle.expect( src.prompt )
            # Check path of traffic, to use in failures
            # TODO: Do we need to add udp port to filter?
            # TODO: Dynamically find the interface to filter on
            # Start packet capture
            pcapFileReceiver = "%s/tshark/%s-%s-tsharkReceiver" % ( "~/TestON",
                                                                    shortDesc if shortDesc else "tshark",
                                                                    dst.name )
            tsharkArgsReceiver = "%s -i %s -f 'udp && host %s' -w %s" % ( main.params[ 'PERF' ][ 'pcap_cmd_arguments' ],
                                                                          dst.interfaces[0]['name'],
                                                                          dstIp,
                                                                          pcapFileReceiver )
            commands = [ 'mkdir -p ~/TestON/tshark',
                         'rm %s' % pcapFileReceiver,
                         'touch %s' % pcapFileReceiver,
                         'chmod o=rw %s' % pcapFileReceiver ]
            for command in commands:
                dst.handle.sendline( command )
                dst.handle.expect( dst.prompt )
                main.log.debug( "%s: %s" % (dst.name, str( dst.handle.before ) ) )
            main.log.info( "Starting tshark on %s " % dst.name )
            dst.handle.sendline( "sudo /usr/bin/tshark %s &> /dev/null &" % tsharkArgsReceiver )
            dst.handle.expect( dst.prompt )

            for src in srcList:
                srcIp = src.interfaces[0]['ips'][0]
                pcapFileSender = "%s/tshark/%s-%s-tsharkSender" % ( "~/TestON",
                                                                    shortDesc if shortDesc else "tshark",
                                                                    src.name )
                tsharkArgsSender = "%s -i %s -f 'udp && host %s' -w %s" % ( main.params[ 'PERF' ][ 'pcap_cmd_arguments' ],
                                                                            src.interfaces[0]['name'],
                                                                            srcIp,
                                                                            pcapFileSender )
                # Prepare file with correct permissions
                commands = [ 'mkdir -p ~/TestON/tshark',
                             'rm %s' % pcapFileSender,
                             'touch %s' % pcapFileSender,
                             'chmod o=rw %s' % pcapFileSender ]
                for command in commands:
                    src.handle.sendline( command )
                    src.handle.expect( src.prompt )
                    main.log.debug( "%s: %s" % (src.name, str( src.handle.before ) ) )

                main.log.info( "Starting tshark on %s " % src.name )
                for src in srcList:
                    src.handle.sendline( "sudo /usr/bin/tshark %s &> /dev/null &" % tsharkArgsSender )
                    src.handle.expect( src.prompt )
            # Timestamp used for EVENT START
            main.eventStart = time.time()
            # LOG Event start in ONOS logs
            for ctrl in main.Cluster.active():
                ctrl.CLI.log( "'%s START'" % longDesc, level="INFO" )
        except Exception as e:
            main.log.exception( "Error in startCapturing" )
            main.skipCase( result="FAIL", msg=e )

    def stopCapturing( self, main, srcList, dst, shortDesc=None, longDesc=None ):
        try:
            pcapFileReceiver = "%s/tshark/%s-%s-tsharkReceiver" % ( "~/TestON",
                                                                shortDesc if shortDesc else "tshark",
                                                                dst.name )
            # Timestamp used for EVENT STOP
            main.eventStop = time.time()
            # LOG Event stop in ONOS logs
            for ctrl in main.Cluster.active():
                ctrl.CLI.log( "'%s STOP'" % longDesc, level="INFO" )
            # Stop packet capture
            dst.handle.sendline( 'fg' )  # Bring process to front
            dst.handle.send( '\x03' )  # send ctrl-c
            try:
                for _ in range(10):
                    dst.handle.expect( dst.prompt, timeout=1 )
            except pexpect.TIMEOUT:
                pass
            for src in srcList:
                src.handle.sendline( 'fg' )  # Bring process to front
                src.handle.send( '\x03' )  # send ctrl-c
                try:
                    for _ in range(10):
                        src.handle.expect( src.prompt, timeout=1 )
                except pexpect.TIMEOUT:
                    pass
            # Stop traffic
            for src in srcList:
                src.handle.sendline( 'fg' )  # Bring process to front
                src.handle.send( '\x03' )  # send ctrl-c
                try:
                    for _ in range(10):
                        src.handle.expect( src.prompt, timeout=1 )
                except pexpect.TIMEOUT:
                    pass
            main.pingStop = time.time()
            main.log.warn( "It took %s seconds since we started ping for us to stop pcap" % ( main.pingStop - main.pingStart ) )

            for src in srcList:
                pcapFileSender = "%s/tshark/%s-%s-tsharkSender" % ( "~/TestON",
                                                                shortDesc if shortDesc else "tshark",
                                                                src.name )
                senderTime = self.analyzePcap( src, pcapFileSender, "'udp && ip.src == %s'" % src.interfaces[0]['ips'][0], debug=False )
                receiverTime = self.analyzePcap( dst, pcapFileReceiver, "'udp && ip.src == %s'" % src.interfaces[0]['ips'][0], debug=False )
                main.downtimeResults[ "%s-%s" % ( shortDesc, src.name ) ] = senderTime
                main.downtimeResults[ "%s-%s-%s" % ( shortDesc, src.name, dst.name ) ] = receiverTime
                # Grab pcap
                senderSCP = main.ONOSbench.scp( src, pcapFileSender, main.logdir, direction="from" )
                utilities.assert_equals( expect=main.TRUE, actual=senderSCP,
                                         onpass="Saved pcap files from %s" % src.name,
                                         onfail="Failed to scp pcap files from %s" % src.name )
            # Grab logs
            # Grab pcap
            receiverSCP = main.ONOSbench.scp( dst, pcapFileReceiver, main.logdir, direction="from" )
            utilities.assert_equals( expect=main.TRUE, actual=receiverSCP,
                                     onpass="Saved pcap files from %s" % dst.name,
                                     onfail="Failed to scp pcap files from %s" % dst.name )
            # Grab Write logs on switches
            #  TODO: kubectl cp write-reqs.txt

        except Exception as e:
            main.log.exception( "Error in stopCapturing" )

    def linkDown( self, device, portsList, srcComponentList, dstComponent, shortDesc, longDesc, sleepTime=10 ):
        """"
        High level function that handles an event including monitoring
        Arguments:
            device - String of the device uri in ONOS
            portsList - List of strings of the port uri in ONOS that we might take down
            srcComponentLsit - List containing src components, used for sending traffic
            dstComponent - Component used for receiving taffic
            shortDesc - String, Short description, used in reporting and file prefixes
            longDesc - String, Longer description, used in logging
        Returns:
            A string of the port id that was brought down
        """
        import time
        deltaStats = {}
        for p in portsList:
            deltaStats[ p ] = {}
        try:
            # Get port stats info
            initialStats = json.loads( main.Cluster.active(0).REST.portstats() )
            for d in initialStats:
                if d[ 'device' ] == device:
                    for p in d[ 'ports' ]:
                        if p[ 'port' ] in portsList:
                            deltaStats[ p[ 'port' ] ][ 'tx1' ] = p[ 'packetsSent' ]

            main.step( "Start Capturing" )
            main.funcs.startCapturing( main,
                                       srcComponentList,
                                       dstComponent,
                                       shortDesc=shortDesc,
                                       longDesc=longDesc )
            # Let some packets flow
            time.sleep( float( main.params['timers'].get( 'TrafficDiscovery', 5 ) ) )
            # Get port stats info
            updatedStats = json.loads( main.Cluster.active(0).REST.portstats() )
            for d in updatedStats:
                if d[ 'device' ] == device:
                    for p in d[ 'ports' ]:
                        if p[ 'port' ] in portsList:
                            deltaStats[ p[ 'port' ] ][ 'tx2' ] = p[ 'packetsSent' ]
            for port, stats in deltaStats.iteritems():
                deltaStats[ port ]['delta'] = stats[ 'tx2' ] - stats[ 'tx1' ]

            main.log.debug( deltaStats )
            port = max( deltaStats, key=lambda p: deltaStats[ p ][ 'tx2' ] - deltaStats[ p ][ 'tx1' ] )
            if deltaStats[ port ][ 'delta' ] == 0:
                main.log.warn( "Could not find a port with traffic. Likely need to wait longer for stats to be updated" )
            main.log.debug( port )
            # Determine which port to bring down
            main.step( "Port down" )
            ctrl = main.Cluster.active( 0 ).CLI
            portDown = ctrl.portstate( dpid=device, port=port, state="disable" )
            portsJson = json.loads( ctrl.ports() )
            for d in portsJson:
                if d['device']['id'] == device:
                    for p in d['ports']:
                        if "(%s)" % port in p['port']:
                            adminState = p['isEnabled']
            main.log.debug( adminState )
            #TODO ASSERTS
            main.log.info( "Sleeping %s seconds" % sleepTime )
            time.sleep( sleepTime )
            main.step( "Stop Capturing" )
            main.funcs.stopCapturing( main,
                                      srcComponentList,
                                      dstComponent,
                                      shortDesc=shortDesc,
                                      longDesc=longDesc )
            return port
        except Exception as e:
            main.log.exception( "Error in linkDown" )

    def linkUp( self, device, port, srcComponentList, dstComponent, shortDesc, longDesc, sleepTime=10 ):
        """"
        High level function that handles an event including monitoring
        Arguments:
            device - String of the device uri in ONOS
            port - String of the port uri in ONOS
            srcComponentLsit - List containing src components, used for sending traffic
            dstComponent - Component used for receiving taffic
            shortDesc - String, Short description, used in reporting and file prefixes
            longDesc - String, Longer description, used in logging
        """
        import time
        if port is None:
            main.log.warn( "Incorrect port number, cannot bring up port" )
            return
        try:
            main.step( "Start Capturing" )
            main.funcs.startCapturing( main,
                                       srcComponentList,
                                       dstComponent,
                                       shortDesc=shortDesc,
                                       longDesc=longDesc )
            main.step( "Port Up" )
            ctrl = main.Cluster.active( 0 ).CLI
            portUp = ctrl.portstate( dpid=device, port=port, state="enable" )
            portsJson = json.loads( ctrl.ports() )
            for d in portsJson:
                if d['device']['id'] == device:
                    for p in d['ports']:
                        if "(%s)" % port in p['port']:
                            adminState = p['isEnabled']
            main.log.debug( adminState )
            #TODO ASSERTS
            main.log.info( "Sleeping %s seconds" % sleepTime )
            time.sleep( sleepTime )
            main.step( "Stop Capturing" )
            main.funcs.stopCapturing( main,
                                      srcComponentList,
                                      dstComponent,
                                      shortDesc=shortDesc,
                                      longDesc=longDesc )
        except Exception as e:
            main.log.exception( "Error in linkUp" )

    def switchDown( self ):
        try:
            pass
        except Exception as e:
            main.log.exception( "Error in switchDown" )

    def switchUp( self ):
        try:
            pass
        except Exception as e:
            main.log.exception( "Error in switchUp" )

    def onosDown( self ):
        try:
            pass
        except Exception as e:
            main.log.exception( "Error in onosDown" )

    def analyzePcap( self, component, filePath, packetFilter, debug=False ):
        try:
            try:
                output = ""
                component.handle.sendline( "" )
                while True:
                    component.handle.expect( component.prompt, timeout=1 )
                    output += component.handle.before + str( component.handle.after )
            except pexpect.TIMEOUT:
                main.log.debug( "%s: %s" % ( component.name, output ) )
                component.handle.send( "\x03" )  # CTRL-C
                component.handle.expect( component.prompt, timeout=5 )
                main.log.debug( component.handle.before + str( component.handle.after ) )
            except Exception as e:
                main.log.exception( "Error in onosDown" )
                return -1
            lineRE = r'^\s*\d+\s+([0-9.]+)'
            tsharkOptions = "-t dd -r %s -Y %s -T fields -e frame.number -e frame.time_delta  -e ip.src -e ip.dst -e udp" % ( filePath, packetFilter )
            component.handle.sendline( "sudo /usr/bin/tshark %s" % tsharkOptions )
            i = component.handle.expect( [ "appears to be damaged or corrupt.", "Malformed Packet", component.prompt, pexpect.TIMEOUT ], timeout=240 )
            if i != 2:
                main.log.error( "Error Reading pcap file" )
                main.log.debug( component.handle.before + str( component.handle.after ) )
                component.handle.send( '\x03' )  # CTRL-C to end process
                component.handle.expect( [ component.prompt, pexpect.TIMEOUT ] )
                main.log.debug( component.handle.before )
                return 0
            output = component.handle.before
            deltas = []
            for line in output.splitlines():
                # Search for a packet in each line
                # If match, save the delta time of the packet
                m = re.search( lineRE, line )
                if m:
                    if debug:
                        main.log.debug( repr( line ) )
                        main.log.info( m.groups() )
                    deltas.append( float( m.group(1) ) * 1000  )
                else:
                    main.log.warn( repr( line ) )
            if not deltas:
                main.log.error( "No Packets found" )
                return 0
            # Print largest timestamp gap
            deltas.sort()
            if debug:
                main.log.debug( deltas[ -10: ] )  # largest 10
            main.log.info( "%s: Detected downtime (longest gap between packets): %s ms" % ( component.name, deltas[ -1 ] )  )
            return deltas[ -1 ]
        except Exception as e:
            main.log.exception( "Error in analyzePcap" )

    def dbWrite( self, main, filename, headerOrder=None ):
        try:
            dbFileName = "%s/%s" % ( main.logdir, filename )
            dbfile = open( dbFileName, "w+" )
            header = []
            row = []
            if not headerOrder:
                headerOrder = main.downtimeResults.keys()
                headerOrder.sort()
            for item in headerOrder:
                header.append( "'%s'" % item )
                row.append( "'%s'" % main.downtimeResults[ item ] )

            dbfile.write( ",".join( header ) + "\n" + ",".join( row ) + "\n" )
            dbfile.close()
        except IOError:
            main.log.warn( "Error opening " + dbFileName + " to write results." )

    def cleanup( self, main, headerOrder=None ):
        run.cleanup( main )
        main.step( "Writing csv results file for db" )
        self.dbWrite( main, main.TEST + "-dbfile.csv", headerOrder )
