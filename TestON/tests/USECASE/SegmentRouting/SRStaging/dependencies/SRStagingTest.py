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
                if len( vlan ) > 0:
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

    @staticmethod
    def startCapturing( main, srcList, dst, shortDesc=None, longDesc=None,
                        trafficDuration=60, trafficSelector="-u -b 20M" ):
        """
        Starts logging, traffic generation, traffic filters, etc before a failure is induced
        src: the src component that sends the traffic
        dst: the dst component that receives the traffic
        """
        try:
            # ping right before to make sure arp is cached and sudo is authenticated
            for src in srcList:
                src.handle.sendline( "sudo /bin/ping -w 1 -c 1 %s -I %s" % ( dst.interfaces[0]['ips'][0],
                                                                        src.interfaces[0]['name'] ) )
                try:
                    i = src.handle.expect( [ "password", src.prompt ] )
                    if i == 0:
                        src.handle.sendline( src.pwd )
                        src.handle.expect( src.prompt )
                except Exception:
                    main.log.error( "%s: Unexpected response from ping" % src.name )
                    src.handle.send( '\x03' )  # ctrl-c
                    src.handle.expect( src.prompt )
                main.funcs.clearBuffer( src )
                main.log.warn( "%s: %s" % ( src.name, str( src.handle.before ) ) )
                dst.handle.sendline( "sudo /bin/ping -w 1 -c 1 %s -I %s" % ( src.interfaces[0]['ips'][0],
                                                                        dst.interfaces[0]['name'] ) )
                try:
                    i = dst.handle.expect( [ "password", dst.prompt ] )
                    if i == 0:
                        dst.handle.sendline( dst.pwd )
                        dst.handle.expect( dst.prompt )
                except Exception:
                    main.log.error( "%s: Unexpected response from ping" % dst.name )
                    dst.handle.send( '\x03' )  # ctrl-c
                    dst.handle.expect( dst.prompt )
                main.funcs.clearBuffer( dst )
                main.log.warn( "%s: %s" % ( dst.name, str( dst.handle.before ) ) )
            # Start traffic
            # TODO: ASSERTS
            main.pingStart = time.time()
            dstIp = dst.interfaces[0]['ips'][0]
            for src in srcList:
                srcIp = src.interfaces[0]['ips'][0]
                iperfArgs = "%s --bind %s -c %s -t %s" % ( trafficSelector,
                                                           srcIp,
                                                           dstIp,
                                                           trafficDuration )
                main.log.info( "Starting iperf" )
                iperfSrc = getattr( main, "NetworkBench-%s" % src.shortName )
                iperfSrc.handle.sendline( "sudo /bin/ping -w 1 -c 1 %s -I %s" % ( dst.interfaces[0]['ips'][0],
                                                                             iperfSrc.interfaces[0]['name'] ) )
                try:
                    i = iperfSrc.handle.expect( [ "password", iperfSrc.prompt ] )
                    if i == 0:
                        iperfSrc.handle.sendline( iperfSrc.pwd )
                        iperfSrc.handle.expect( iperfSrc.prompt )
                except Exception:
                    main.log.error( "%s: Unexpected response from ping" % iperfSrc.name )
                    iperfSrc.handle.send( '\x03' )  # ctrl-c
                    iperfSrc.handle.expect( iperfSrc.prompt )
                main.funcs.clearBuffer( iperfSrc )
                main.log.warn( "%s: %s" % ( iperfSrc.name, str( iperfSrc.handle.before ) ) )

                iperfSrc.handle.sendline( "/usr/bin/iperf %s " % iperfArgs )
            # TODO: Do we need to add udp port to filter?
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
            dst.handle.sendline( "sudo /usr/bin/tshark %s &> /dev/null " % tsharkArgsReceiver )

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
                src.handle.sendline( "sudo /usr/bin/tshark %s &> /dev/null " % tsharkArgsSender )
            # Timestamp used for EVENT START
            main.eventStart = time.time()
            # LOG Event start in ONOS logs
            for ctrl in main.Cluster.active():
                ctrl.CLI.log( "'%s START'" % longDesc, level="INFO" )
        except Exception as e:
            main.log.exception( "Error in startCapturing" )
            main.skipCase( result="FAIL", msg=e )

    def stopCapturing( self, main, srcList, dst, shortDesc=None, longDesc=None ):
        import time
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
            main.funcs.clearBuffer( dst, kill=True, debug=True )
            for src in srcList:
                main.funcs.clearBuffer( src, kill=True, debug=True )
                # Stop traffic
                iperfSrc = getattr( main, "NetworkBench-%s" % src.shortName )
                main.funcs.clearBuffer( iperfSrc, kill=True, debug=True )
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
                # TODO: Move this elsewhere, for automatic recovery, this chould delay us
                #       to not start capture for the recovery until its already happened
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
            kubeConfig = main.Cluster.active(0).k8s.kubeConfig
            namespace = main.params[ 'kubernetes' ][ 'namespace' ]
            switches = main.ONOSbench.kubectlGetPodNames( kubeconfig=kubeConfig,
                                                          namespace=namespace,
                                                          name="stratum" )
            for switch in switches:
                dstFile = "%s/%s-%s-write-reqs.txt" % ( main.logdir, shortDesc, switch )
                writeResult = main.ONOSbench.kubectlCp( switch, "/tmp/p4_writes.txt", dstFile,
                                                        kubeconfig=kubeConfig,
                                                        namespace=namespace )
                utilities.assert_equals( expect=main.TRUE, actual=writeResult,
                                         onpass="Saved write-req file from %s" % switch,
                                         onfail="Failed to cp write-req file from %s" % switch )

        except Exception as e:
            main.log.exception( "Error in stopCapturing" )

    @staticmethod
    def clearBuffer( component, kill=False, debug=False ):
        i = 0
        if kill:
            component.handle.send( "\x03" )  # Ctrl-C
        for _ in range(10):
            i = component.handle.expect( [ component.prompt, pexpect.TIMEOUT ] , timeout=1 )
            if debug:
                main.log.debug( "%s: %s" % ( component.name, str( component.handle.before ) ) )
            if i == 1:
                # Do we check if the ctrl-c worked?
                break
                """
                if kill:
                    component.handle.send( "\x03" )  # Ctrl-C
                    component.handle.expect( component.prompt, timeout=1 )
                """
        try:
            component.handle.sendline( "uname" )
            component.handle.expect( "Linux" )
            component.handle.expect( component.prompt )
        except pexpect.TIMEOUT:
            component.handle.send( "\x03" )  # Ctrl-C
            component.handle.expect( component.prompt )

    @staticmethod
    def linkDown( device, portsList, srcComponentList, dstComponent, shortDesc, longDesc, sleepTime=10 ):
        """"
        High level function that handles an event including monitoring
        Arguments:
            device - String of the device uri in ONOS
            portsList - List of strings of the port uri in ONOS that we might take down
            srcComponentList - List containing src components, used for sending traffic
            dstComponent - Component used for receiving traffic
            shortDesc - String, Short description, used in reporting and file prefixes
            longDesc - String, Longer description, used in logging
        Option Arguments:
            sleepTime - How long to wait between starting the capture and stopping
        Returns:
            A string of the port id that was brought down
        """
        import time
        try:
            initialStats = json.loads( main.Cluster.active(0).REST.portstats() )
            main.step( "Start Capturing" )
            main.funcs.startCapturing( main,
                                       srcComponentList,
                                       dstComponent,
                                       shortDesc=shortDesc,
                                       longDesc=longDesc )
            # Let some packets flow
            time.sleep( float( main.params['timers'].get( 'TrafficDiscovery', 5 ) ) )
            updatedStats = json.loads( main.Cluster.active(0).REST.portstats() )
            port = main.funcs.findPortWithTraffic( device, portsList, initialStats, updatedStats )

            # Determine which port to bring down
            main.step( "Port down" )
            ctrl = main.Cluster.active( 0 ).CLI
            portDown = ctrl.portstate( dpid=device, port=port, state="disable" )
            portsJson = json.loads( ctrl.ports() )
            adminState = None
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

    @staticmethod
    def linkUp( device, port, srcComponentList, dstComponent, shortDesc, longDesc, sleepTime=10 ):
        """"
        High level function that handles an event including monitoring
        Arguments:
            device - String of the device uri in ONOS
            port - String of the port uri in ONOS
            srcComponentList - List containing src components, used for sending traffic
            dstComponent - Component used for receiving traffic
            shortDesc - String, Short description, used in reporting and file prefixes
            longDesc - String, Longer description, used in logging
        Option Arguments:
            sleepTime - How long to wait between starting the capture and stopping
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
            adminState = None
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

    @staticmethod
    def onlReboot( switchComponentList, srcComponentList, dstComponent,
                   shortDescFailure, longDescFailure, shortDescRecovery, longDescRecovery,
                   sleepTime=5 ):
        """"
        High level function that handles an event including monitoring
        Arguments:
            switchComponent - Component used for restarting Switch
            srcComponentList - List containing src components, used for sending traffic
            dstComponent - Component used for receiving traffic
            shortDescFailure - String, Short description, used in reporting and file prefixes
            longDescFailure - String, Longer description, used in logging
            shortDescRecovery - String, Short description, used in reporting and file prefixes
            longDescRecovery - String, Longer description, used in logging
        Option Arguments:
            sleepTime - How long to wait between starting the capture and stopping
        """
        import time
        try:
            main.case( longDescFailure )
            initialStats = json.loads( main.Cluster.active(0).REST.portstats() )
            main.step( "Start Capturing" )
            main.funcs.startCapturing( main,
                                       srcComponentList,
                                       dstComponent,
                                       shortDesc=shortDescFailure,
                                       longDesc=longDescFailure,
                                       trafficDuration=120 )
            # Let some packets flow
            time.sleep( float( main.params['timers'].get( 'TrafficDiscovery', 5 ) ) )
            updatedStats = json.loads( main.Cluster.active(0).REST.portstats() )
            switchComponent = main.funcs.findSwitchWithTraffic( switchComponentList,
                                                                initialStats,
                                                                updatedStats )
            main.step( "Reboot ONL on Switch %s" % switchComponent.name )
            startTime = time.time()
            switchComponent.handle.sendline( "sudo reboot" )

            #TODO ASSERTS
            main.log.info( "Sleeping %s seconds" % sleepTime )
            time.sleep( sleepTime )
            main.step( "Stop Capturing" )
            main.funcs.stopCapturing( main,
                                      srcComponentList,
                                      dstComponent,
                                      shortDesc=shortDescFailure,
                                      longDesc=longDescFailure )
            # Try to minimize the amount of time we are sending 20mb/s while switch is down
            # Large pcaps can cause timeouts when analyzing the results
            #time.sleep( 60 )
            main.case( longDescRecovery )
            main.step( "Start Capturing" )
            main.funcs.startCapturing( main,
                                       srcComponentList,
                                       dstComponent,
                                       shortDesc=shortDescRecovery,
                                       longDesc=longDescRecovery,
                                       trafficDuration=300 )
            # TODO: Reconnect to the NetworkBench version as well
            connect = utilities.retry( switchComponent.connect,
                                       main.FALSE,
                                       attempts=30,
                                       getRetryingTime=True )
            reconnectTime = time.time()
            main.log.warn( "It took %s seconds for the switch to reboot - ssh" % float( reconnectTime - startTime ) )

            # We need to check the status of the switch in ONOS
            available = utilities.retry( main.funcs.switchIsConnected,
                                         False,
                                         args=[ switchComponent ],
                                         attempts=300,
                                         getRetryingTime=True )
            main.log.debug( available )
            stopTime = time.time()
            main.log.warn( "It took %s seconds for the switch to reconnect to ONOS" % float( stopTime - startTime ) )

            main.step( "ONL Restart on Switch %s" % switchComponent.name )
            main.log.info( "Sleeping %s seconds" % sleepTime )
            time.sleep( sleepTime )
            main.step( "Stop Capturing" )
            main.funcs.stopCapturing( main,
                                      srcComponentList,
                                      dstComponent,
                                      shortDesc=shortDescRecovery,
                                      longDesc=longDescRecovery )
            # Check the switch is back in ONOS
        except Exception as e:
            main.log.exception( "Error in onlReboot" )

    @staticmethod
    def killSwitchAgent( switchComponentList, srcComponentList, dstComponent,
                         shortDescFailure, longDescFailure, shortDescRecovery, longDescRecovery,
                         sleepTime=5 ):
        """"
        High level function that handles an event including monitoring
        Arguments:
            switchComponent - Component used for restarting Switch
            srcComponentList - List containing src components, used for sending traffic
            dstComponent - Component used for receiving traffic
            shortDescFailure - String, Short description, used in reporting and file prefixes
            longDescFailure - String, Longer description, used in logging
            shortDescRecovery - String, Short description, used in reporting and file prefixes
            longDescRecovery - String, Longer description, used in logging
        Option Arguments:
            sleepTime - How long to wait between starting the capture and stopping
        """
        import time
        try:
            main.case( longDescFailure )
            initialStats = json.loads( main.Cluster.active(0).REST.portstats() )
            main.step( "Start Capturing" )
            main.funcs.startCapturing( main,
                                       srcComponentList,
                                       dstComponent,
                                       shortDesc=shortDescFailure,
                                       longDesc=longDescFailure,
                                       trafficDuration=120 )
            # Let some packets flow
            time.sleep( float( main.params['timers'].get( 'TrafficDiscovery', 5 ) ) )
            updatedStats = json.loads( main.Cluster.active(0).REST.portstats() )
            switchComponent = main.funcs.findSwitchWithTraffic( switchComponentList,
                                                                initialStats,
                                                                updatedStats )
            main.step( "Kill stratum agent on Switch %s" % switchComponent.name )
            # Get pod name to delete
            nodeName = switchComponent.shortName.lower()
            kubeConfig = main.Cluster.active(0).k8s.kubeConfig
            namespace = main.params[ 'kubernetes' ][ 'namespace' ]
            output = main.ONOSbench.kubectlGetPodNames( kubeconfig=kubeConfig,
                                                        namespace=namespace,
                                                        name="stratum",
                                                        nodeName=nodeName )
            main.log.debug( output )
            if len( output ) != 1:
                main.log.warn( "Did not find a specific switch pod to kill" )
            startTime = time.time()
            # Delete pod
            main.ONOSbench.handle.sendline( "kubectl --kubeconfig %s delete pod -n %s %s" % ( kubeConfig, namespace, output[0] ) )
            main.ONOSbench.handle.expect( main.ONOSbench.prompt )
            main.log.debug( repr( main.ONOSbench.handle.before ) + repr( main.ONOSbench.handle.after ) )
            #TODO ASSERTS
            main.log.info( "Sleeping %s seconds" % sleepTime )
            time.sleep( sleepTime )
            main.step( "Stop Capturing" )
            main.funcs.stopCapturing( main,
                                      srcComponentList,
                                      dstComponent,
                                      shortDesc=shortDescFailure,
                                      longDesc=longDescFailure )

            # Try to minimize the amount of time we are sending 20mb/s while switch is down
            #time.sleep( 60 )
            main.case( longDescRecovery )
            main.step( "Start Capturing" )
            main.funcs.startCapturing( main,
                                       srcComponentList,
                                       dstComponent,
                                       shortDesc=shortDescRecovery,
                                       longDesc=longDescRecovery,
                                       trafficDuration=400 )
            # FIXME: We should check the health of the pod
            #connect = utilities.retry( switchComponent.connect,
            #                           main.FALSE,
            #                           attempts=30,
            #                           getRetryingTime=True )

            # Check the status of the switch in ONOS
            podRestartTime = time.time()
            available = utilities.retry( main.funcs.switchIsConnected,
                                         False,
                                         args=[ switchComponent ],
                                         attempts=300,
                                         getRetryingTime=True )

            main.log.debug( available )
            stopTime = time.time()
            main.log.warn( "It took %s seconds for the switch to reconnect to ONOS" % float( stopTime - startTime ) )

            main.step( "ONL Restart on Switch %s" % switchComponent.name )
            main.log.info( "Sleeping %s seconds" % sleepTime )
            time.sleep( sleepTime )
            main.step( "Stop Capturing" )
            main.funcs.stopCapturing( main,
                                      srcComponentList,
                                      dstComponent,
                                      shortDesc=shortDescRecovery,
                                      longDesc=longDescRecovery )
        except Exception as e:
            main.log.exception( "Error in killSwitchAgent" )

    @staticmethod
    def onosDown():
        try:
            pass
        except Exception as e:
            main.log.exception( "Error in onosDown" )

    @staticmethod
    def analyzePcap( component, filePath, packetFilter, debug=False, timeout=240 ):
        try:
            main.log.debug( "%s analyzing pcap file" % component.name )
            output = ""
            try:
                component.handle.sendline( "" )
                while True:
                    component.handle.expect( component.prompt, timeout=1 )
                    output += component.handle.before + str( component.handle.after )
            except pexpect.TIMEOUT:
                main.log.debug( "%s analyzePcap: %s" % ( component.name, output ) )
                component.handle.send( "\x03" )  # CTRL-C
                component.handle.expect( component.prompt, timeout=10 )
                main.log.debug( component.handle.before + str( component.handle.after ) )
            except Exception as e:
                main.log.exception( "Error in onosDown" )
                return -1
            oneLiner = "sort -u -g -k2,2 | tail -1 | cut -f2 "
            tsharkOptions = "-t dd -r %s -Y %s -T fields -e frame.number -e frame.time_delta  -e ip.src -e ip.dst -e udp | %s" % ( filePath, packetFilter, oneLiner )
            component.handle.sendline( "sudo /usr/bin/tshark %s" % tsharkOptions )
            i = component.handle.expect( [ "appears to be damaged or corrupt.",
                                           "Malformed Packet",
                                           component.prompt,
                                           pexpect.TIMEOUT ], timeout=timeout )
            if i != 2:
                main.log.error( "Error Reading pcap file" )
                main.log.debug( component.handle.before + str( component.handle.after ) )
                component.handle.send( '\x03' )  # CTRL-C to end process
                component.handle.expect( [ component.prompt, pexpect.TIMEOUT ] )
                main.log.debug( component.handle.before )
                return 0
            output = component.handle.before
            assert "not found" not in output, output
            assert "error" not in output, output
            lineRE = r'^([0-9.]+)$'
            for line in output.splitlines():
                m = re.search (lineRE, line )
                if m:
                    if debug:
                        main.log.debug( repr( line ) )
                        main.log.info( m.groups() )
                    delta = float( m.group(1) ) * 1000
                    main.log.info( "%s: Detected downtime (longest gap between packets): %s ms" % ( component.name, delta )  )
                    return delta
            main.log.error( "No Packets found" )
            return 0
            """
            lineRE = r'^\s*\d+\s+([0-9.]+)'
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
            """
        except Exception as e:
            main.log.exception( "Error in analyzePcap" )

    @staticmethod
    def findPortWithTraffic( device, portsList, initialStats, updatedStats ):
        """
        Given a device id and a list of ports, returns the port with the most packets sent
        between two device statistics reads
        Arguments:
            device - String, device id of the device to check
            portsList - list if ints, the ports on the device to look at
            initialStats - A dict created from the json output of ONOS device statistics
            updatedStats - A dict created from the json output of ONOS device statistics
        Returns:
            The port with the largest increase in packets sent between the two device statistics

        """
        try:
            deltaStats = {}
            for p in portsList:
                deltaStats[ p ] = {}
            for d in initialStats:
                if d[ 'device' ] == device:
                    for p in d[ 'ports' ]:
                        if p[ 'port' ] in portsList:
                            deltaStats[ p[ 'port' ] ][ 'tx1' ] = p[ 'packetsSent' ]
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
            return port
        except Exception as e:
            main.log.exception( "Error in findPortWithTraffic" )
            main.skipCase( result="FAIL", msg=e )

    @staticmethod
    def findSwitchWithTraffic( switchComponentList, initialStats, updatedStats ):
        """
        Given a list of switch components, returns the swtich component with the
        port with the most packets sent between two device statistics reads
        Arguments:
            switchComponentList - List of switch components to check
            initialStats - A dict created from the json output of ONOS device statistics
            updatedStats - A dict created from the json output of ONOS device statistics
        Returns:
            The switch component with the port with the largest increase in packets sent
            between the two device statistics

        """
        try:
            deltaStats = {}
            deviceNames = [ s.shortName for s in switchComponentList ]
            for device in deviceNames:
                deltaStats[ device ] = {}
                for d in initialStats:
                    if device in d[ 'device' ]:
                        for p in d[ 'ports' ]:
                            deltaStats[ device ][ p[ 'port' ] ] = {}
                            deltaStats[ device ][ p[ 'port' ] ][ 'tx1' ] = p[ 'packetsSent' ]
            for device in deviceNames:
                for d in updatedStats:
                    if device in d[ 'device' ]:
                        for p in d[ 'ports' ]:
                            deltaStats[ device ][p[ 'port' ] ][ 'tx2' ] = p[ 'packetsSent' ]
            target = ""
            highest = 0
            for device in deviceNames:
                for port, stats in deltaStats[ device ].iteritems():
                    delta = stats[ 'tx2' ] - stats[ 'tx1' ]
                    if delta >= highest:
                        highest = delta
                        target = device
                    deltaStats[ device ][ port ]['delta'] = stats[ 'tx2' ] - stats[ 'tx1' ]

            main.log.debug( deltaStats )
            if highest == 0:
                main.log.warn( "Could not find a port with traffic. Likely need to wait longer for stats to be updated" )
            main.log.debug( target )
            switchComponent = None
            for switch in switchComponentList:
                if switch.shortName is target:
                    switchComponent = switch
                    break
            main.log.debug( switchComponent )
            return switchComponent
        except Exception as e:
            main.log.exception( "Error in findSwitchWithTraffic" )
            main.skipCase( result="FAIL", msg=e )

    @staticmethod
    def switchIsConnected( switchComponent ):
        """
        Given a switch component, returns if the switch is "Available" in ONOS
        """
        try:
            devicesJson = json.loads( main.Cluster.active(0).devices() )
            for device in devicesJson:
                if switchComponent.shortName in device[ 'id' ]:
                    return device[ 'available' ]
            return False
        except Exception as e:
            main.log.exception( "Error in switchIsConnected" )
            main.skipCase( result="FAIL", msg=e )

    @staticmethod
    def dbWrite( main, filename, headerOrder=None ):
        """
        Prints the results stored in main.downtimeResults.
        Arguments:
            filename - the file name to save the results to, located in the test's log folder
        Optional Arguments:
            headerOrder - An ordered list of headers to write to the file. If None, will
                          print in alphabetical order
        """
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
