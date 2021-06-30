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
import tests.USECASE.SegmentRouting.SRStaging.dependencies.log_breakdown as logParser
import time
import re
import json
import pexpect
import os


class SRStagingTest:

    def __init__( self ):
        self.default = ''
        self.topo = run.getTopo()
        # TODO: Check minFlowCount of leaf for BMv2 switch
        # (number of spine switch, number of leaf switch, dual-homed, description, minFlowCount - leaf (OvS), minFlowCount - leaf (BMv2))
        self.switchNames = {}
        self.switchNames[ '0x1' ] = [ "leaf1" ]
        self.switchNames[ '0x2' ] = [ "leaf1", "leaf2" ]
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
            try:
                main.downtimeResults
            except ( NameError, AttributeError ):
                main.downtimeResults = {}

            main.logdir = main.logdir + "/CASE" + str( main.CurrentTestCaseNumber )
            os.mkdir( main.logdir )
            main.case( '%s, with %s, %s switches and %d ONOS instance%s' %
                       ( description, self.topo[ topology ][ 'description' ],
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
                mininet_args = ' --spine=%d --leaf=%d' % ( self.topo[ topology ][ 'spines' ], self.topo[ topology ][ 'leaves' ] )
                if self.topo[ topology ][ 'dual-homed' ]:
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
    def getHostConnections( main, host ):
        """
        Returns a dictionary with keys as devices the host is connected
        to and values as the string name of the ports connected to the host
        """
        import json
        import re
        hostsJson = json.loads( main.Cluster.active(0).REST.hosts() )
        locations = {}
        ip = host.interfaces[0]['ips'][0]
        for h in hostsJson:
            if ip in h[ 'ipAddresses' ]:
                for connectPoint in h[ 'locations' ]:
                    did = connectPoint[ 'elementId' ].encode( 'utf-8' )
                    device = locations.get( did, [] )
                    port = connectPoint['port'].encode( 'utf-8' )
                    m = re.search( '\((\d+)\)', port )
                    if m:
                        port = m.group(1)
                    device.append( int( port ) )
                    locations[ did ] = device
        return locations

    @staticmethod
    def singlePingWithSudo( main, src, dstIp ):
        """
        Send a single ping with sudo. This verifies connectivity and sudo access
        """
        # TODO: Assert
        src.handle.sendline( "sudo /bin/ping -w 1 -c 1 %s -I %s" % ( dstIp,
                                                                     src.interfaces[0]['name'] ) )
        try:
            i = src.handle.expect( [ "password", src.prompt ] )
            if i == 0:
                src.handle.sendline( src.pwd )
                i = src.handle.expect( [ "password", src.prompt ] )
                assert i != 0, "Incorrect Password"
        except Exception:
            main.log.exception( "%s: Unexpected response from ping" % src.name )
            src.handle.send( '\x03' )  # ctrl-c
            src.handle.expect( src.prompt )
        main.funcs.clearBuffer( src )
        main.log.warn( "%s: %s" % ( src.name, str( src.handle.before ) ) )

    @staticmethod
    def startIperf( main, src, dst, trafficSelector, trafficDuration ):
        """
        Start iperf from src ip to dst ip
        Handles connectivity check and sudo password input as well
        Arguments:
            src: src host component
            dst: dst host component
            trafficSelector: traffic selector string, passed to iperf
            trafficDuration: Traffic duration string, passed to iperf

        """
        dstIp = dst.interfaces[0]['ips'][0]
        srcIp = src.interfaces[0]['ips'][0]
        iperfArgs = "%s --bind %s -c %s -t %s" % ( trafficSelector,
                                                   srcIp,
                                                   dstIp,
                                                   trafficDuration )
        main.log.info( "Starting iperf between %s and %s" % ( src.shortName, dst.shortName ) )
        iperfSrc = getattr( main, "NetworkBench-%s" % src.shortName )
        sudoCheck = main.funcs.singlePingWithSudo( main, iperfSrc, dst.interfaces[0]['ips'][0] )
        iperfSrc.handle.sendline( "/usr/bin/iperf %s " % iperfArgs )

    @staticmethod
    def startTshark( main, host, pingDesc=None, direction="Sender" ):
        """
        """

        if direction == "Sender":
            suffix = "Sender"
            hostStr = "src host %s" % host.interfaces[0]['ips'][0]
        else:
            suffix = "Receiver"
            hostStr = "dst host %s" % host.interfaces[0]['ips'][0]
        if not pingDesc:
            pingDesc = host.name
        fileName = "%s-tshark%s" % ( pingDesc, suffix )
        pcapFile = "%s/tshark/%s" % ( "~/TestON", fileName )
        tsharkArgs = "%s -i %s -f 'udp && %s' -w %s" % ( main.params[ 'PERF' ][ 'pcap_cmd_arguments' ],
                                                         host.interfaces[0]['name'],
                                                         hostStr,
                                                         pcapFile )
        commands = [ 'mkdir -p ~/TestON/tshark',
                     'rm %s' % pcapFile,
                     'touch %s' % pcapFile,
                     'chmod o=rw %s' % pcapFile ]
        for command in commands:
            host.handle.sendline( command )
            host.handle.expect( host.prompt )
            main.log.debug( "%s: %s" % ( host.name, str( host.handle.before ) ) )
        main.log.info( "Starting tshark on %s " % host.name )
        host.handle.sendline( "sudo /usr/bin/tshark %s &> /dev/null " % tsharkArgs )

    @staticmethod
    def startCapturing( main, srcList, dst, shortDesc=None, longDesc=None,
                        trafficDuration=60, trafficSelector="-u -b 20M",
                        bidirectional=False ):
        """
        Starts logging, traffic generation, traffic filters, etc before a failure is induced
        src: the src component that sends the traffic
        dst: the dst component that receives the traffic
        """
        import datetime
        try:
            if not isinstance( srcList, list ):
                srcList = [ srcList ]
            srcReceiverList = [ ]
            dstReceiver = None
            if bidirectional:
                # Create new sessions so we can send and receive on the same host
                for src in srcList:
                    newName = "%s-%s" % ( src.shortName, "Receiver" )
                    main.Network.copyComponent( src.name, newName )
                    srcReceiver = getattr( main, newName )
                    srcReceiverList.append( srcReceiver )
                newName = "%s-%s" % ( dst.shortName, "Receiver" )
                main.Network.copyComponent( dst.name, newName )
                dstReceiver = getattr( main, newName )

            # ping right before to make sure arp is cached and sudo is authenticated
            for src in srcList:
                main.funcs.singlePingWithSudo( main, src, dst.interfaces[0]['ips'][0] )
                main.funcs.singlePingWithSudo( main, dst, src.interfaces[0]['ips'][0] )
            if bidirectional:
                for src in srcReceiverList:
                    main.funcs.singlePingWithSudo( main, src, dstReceiver.interfaces[0]['ips'][0] )
                    main.funcs.singlePingWithSudo( main, dstReceiver, src.interfaces[0]['ips'][0] )
            # Start traffic
            # TODO: ASSERTS
            main.pingStart = time.time()
            for src in srcList:
                main.funcs.startIperf( main, src, dst, trafficSelector, trafficDuration )
                if bidirectional:
                    main.funcs.startIperf( main, dstReceiver, src, trafficSelector, trafficDuration )
            # Start packet capture on receiver
            pingDesc = "%s-%s" % ( shortDesc, dst.shortName )
            main.funcs.startTshark( main, dst, pingDesc, direction="Receiver" )
            if bidirectional:
                for src in srcReceiverList:
                    pingDesc = "%s-%s" % ( shortDesc, src.shortName )
                    main.funcs.startTshark( main, src, pingDesc, direction="Receiver" )

            for src in srcList:
                pingDesc = "%s-%s%s" % ( shortDesc, src.shortName, "-to-%s" % dst.shortName if bidirectional else "" )
                main.funcs.startTshark( main, src, pingDesc=pingDesc, direction="Sender" )
                if bidirectional:
                    pingDesc = "%s-%s%s" % ( shortDesc, dst.shortName, "-to-%s" % src.shortName if bidirectional else "" )
                    main.funcs.startTshark( main, dstReceiver, pingDesc=pingDesc, direction="Sender" )

            # Timestamp used for EVENT START
            main.eventStart = datetime.datetime.utcnow()
            # LOG Event start in ONOS logs
            for ctrl in main.Cluster.active():
                ctrl.CLI.log( "'%s START'" % longDesc, level="INFO" )
        except Exception as e:
            main.log.exception( "Error in startCapturing" )
            main.skipCase( result="FAIL", msg=e )

    def checkContinuedFlow(self):
        """
        We need a way to verify that traffic hasn't stopped.
        Maybe check filesize of pcaps is increasing?
        """
        return main.TRUE

    def stopCapturing( self, main, srcList, dst, shortDesc=None, longDesc=None, bidirectional=False ):
        import datetime
        import time
        from tests.dependencies.utils import Utils
        main.utils = Utils()
        if not isinstance( srcList, list ):
            srcList = [ srcList ]
        try:
            srcReceiverList = [ ]
            dstReceiver = None
            if bidirectional:
                for src in srcList:
                    newName = "%s-%s" % ( src.shortName, "Receiver" )
                    srcReceiver = getattr( main, newName )
                    srcReceiverList.append( srcReceiver )
                newName = "%s-%s" % ( dst.shortName, "Receiver" )
                dstReceiver = getattr( main, newName )
            pingDescReceiver = "%s%s" % ( "%s-" % shortDesc if shortDesc else "", dst.shortName )
            pcapFileReceiver = "%s/tshark/%s-tsharkReceiver" % ( "~/TestON",
                                                                 pingDescReceiver )
            # Timestamp used for EVENT STOP
            main.eventStop = datetime.datetime.utcnow()
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
                pingDesc = "%s-%s%s" % ( shortDesc, src.shortName, "-to-%s" % dst.shortName if bidirectional else "" )
                pingDescReceiver = "%s%s-to-%s" % ( "%s-" % shortDesc if shortDesc else "", src.shortName, dst.shortName )
                pcapFileSender = "%s/tshark/%s-tsharkSender" % ( "~/TestON",
                                                                 pingDesc )
                senderTime = self.analyzePcap( src, pcapFileSender, "'udp && ip.src == %s'" % src.interfaces[0]['ips'][0], debug=False )
                receiverTime = self.analyzePcap( dst, pcapFileReceiver, "'udp && ip.src == %s'" % src.interfaces[0]['ips'][0], debug=False )
                main.downtimeResults[ "%s" % pingDesc ] = senderTime
                main.downtimeResults[ "%s" % pingDescReceiver ] = receiverTime
                # TODO: Add alarm here if time is too high
                # Grab pcap
                # TODO: Move this elsewhere, for automatic recovery, this could delay us
                #       to not start capture for the recovery until its already happened
                senderSCP = main.ONOSbench.scp( src, pcapFileSender, main.logdir, direction="from" )
                utilities.assert_equals( expect=main.TRUE, actual=senderSCP,
                                         onpass="Saved pcap files from %s" % src.name,
                                         onfail="Failed to scp pcap files from %s" % src.name )
            if bidirectional:
                for src in srcReceiverList:
                    pingDescOther = "%s-%s%s" % ( shortDesc, dstReceiver.shortName, "-to-%s" % src.shortName if bidirectional else "" )
                    pcapFileSender = "%s/tshark/%s-tsharkSender" % ( "~/TestON",
                                                                     pingDescOther )
                    pingDescReceiverOther = "%s%s-to-%s" % ( "%s-" % shortDesc if shortDesc else "", src.shortName, dstReceiver.shortName )
                    pcapFileReceiverOther = "%s/tshark/%s-tsharkReceiver" % ( "~/TestON",
                                                                              pingDescReceiverOther )
                    senderTime = self.analyzePcap( dstReceiver, pcapFileSender, "'udp && ip.src == %s'" % dstReceiver.interfaces[0]['ips'][0], debug=False )
                    receiverTime = self.analyzePcap( src, pcapFileReceiverOther, "'udp && ip.src == %s'" % dstReceiver.interfaces[0]['ips'][0], debug=False )
                    main.downtimeResults[ "%s" % pingDescOther ] = senderTime
                    main.downtimeResults[ "%s" % pingDescReceiverOther ] = receiverTime
                    # Grab pcap
                    # TODO: Move this elsewhere, for automatic recovery, this could delay us
                    #       to not start capture for the recovery until its already happened
                    senderSCP = main.ONOSbench.scp( dstReceiver, pcapFileSender, main.logdir, direction="from" )
                    utilities.assert_equals( expect=main.TRUE, actual=senderSCP,
                                             onpass="Saved pcap files from %s" % src.name,
                                             onfail="Failed to scp pcap files from %s" % src.name )
                    # Grab pcap
                    receiverSCP = main.ONOSbench.scp( src, pcapFileReceiverOther, main.logdir, direction="from" )
                    utilities.assert_equals( expect=main.TRUE, actual=receiverSCP,
                                             onpass="Saved pcap files from %s" % dst.name,
                                             onfail="Failed to scp pcap files from %s" % dst.name )

            # Grab pcap
            receiverSCP = main.ONOSbench.scp( dst, pcapFileReceiver, main.logdir, direction="from" )
            utilities.assert_equals( expect=main.TRUE, actual=receiverSCP,
                                     onpass="Saved pcap files from %s" % dst.name,
                                     onfail="Failed to scp pcap files from %s" % dst.name )
            # Grab logs
            useStern = main.params['use_stern'].lower() == "true"
            main.utils.copyKarafLog( shortDesc, before=True,
                                     includeCaseDesc=True, useStern=useStern,
                                     startTime=main.eventStart )
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
            # We also need to save the pod name to switch name mapping
            main.ONOSbench.kubectlPodNodes( dstPath=main.logdir + "/podMapping.txt",
                                            kubeconfig=kubeConfig,
                                            namespace=namespace )

        except Exception:
            main.log.exception( "Error in stopCapturing" )

    @staticmethod
    def analyzeLogs( shortDesc, event, startTime, stopTime, logDir=main.logdir ):
        try:
            import datetime
            main.log.step( "Read saved component logs" )
            main.log.debug( main.eventStart )
            # Seems like there is clock skew, +/- 30 seconds
            MINUTE = datetime.timedelta( minutes=1 )
            lines, podMapping = logParser.readLogsFromTestFolder( startTime-MINUTE,
                                                                  stopTime+MINUTE,
                                                                  testDir=logDir )
            # Write a merged log file
            ordered_lines = sorted( lines, key=logParser.sortByDateTime )
            mergedLogFile = "%s/%s-mergedLogs.txt" % ( logDir, shortDesc )
            with open( mergedLogFile, 'w' ) as output:
                for line in ordered_lines:
                    output.write( "%s %s" % ( line['pod'], line['line'] ) )

            # Pull out lines related to test. These are stored in logParser
            logParser.analyzeLogs( ordered_lines, podMapping )
            # save human readable results to this file
            outFile = "log_breakdown_output"
            outputTextFile = "%s/%s-%s.txt" % ( logDir, shortDesc, outFile )
            # Find component times based on these lines
            resultsDict = logParser.breakdownEvent( event, podMapping, outputFile=outputTextFile )
            main.log.debug( json.dumps( resultsDict, sort_keys=True, indent=4 ) )
            # Add these times to be saved to test output
            componentBreakdownDict = {}
            for oldKey in resultsDict.keys():
                newKey = "%s-%s" % ( shortDesc, oldKey )
                componentBreakdownDict[ newKey ] = resultsDict[ oldKey ]
            # We need another way of uploading, this doesn't have guaranteed order and # of fields
            # main.downtimeResults.update( componentBreakdownDict )
            main.log.debug( json.dumps( main.downtimeResults, sort_keys=True, indent=4 ) )
        except Exception:
            main.log.exception( "Error while breaking down logs" )

    @staticmethod
    def clearBuffer( component, kill=False, debug=False ):
        if kill:
            component.handle.send( "\x03" )  # Ctrl-C
        for _ in range(10):
            i = component.handle.expect( [ component.prompt, pexpect.TIMEOUT ], timeout=1 )
            if debug:
                main.log.debug( "%s: %s" % ( component.name, str( component.handle.before ) ) )
            if i == 1:
                # Do we check if the ctrl-c worked?
                break
        try:
            component.handle.sendline( "uname" )
            component.handle.expect( "Linux" )
            component.handle.expect( component.prompt )
        except pexpect.TIMEOUT:
            component.handle.send( "\x03" )  # Ctrl-C
            component.handle.expect( component.prompt )

    @staticmethod
    def linkDown( targets, srcComponentList, dstComponent, shortDesc,
                  longDesc, sleepTime=10, stat='packetsSent', bidirectional=False ):
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
                                       longDesc=longDesc,
                                       bidirectional=bidirectional )
            # Let some packets flow
            trafficDiscoverySleep = float( main.params['timers'].get( 'TrafficDiscovery', 5 ) )
            main.log.debug( "Sleeping %d seconds for traffic counters to update" % trafficDiscoverySleep )
            time.sleep( trafficDiscoverySleep )
            updatedStats = json.loads( main.Cluster.active(0).REST.portstats() )
            device, port = main.funcs.findPortWithTraffic( targets, initialStats, updatedStats, stat=stat )

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
            # TODO ASSERTS
            main.log.info( "Sleeping %s seconds" % sleepTime )
            time.sleep( sleepTime )
            main.step( "Verify Traffic still flows" )
            #checkContinuedFlow()
            main.step( "Stop Capturing" )
            main.funcs.stopCapturing( main,
                                      srcComponentList,
                                      dstComponent,
                                      shortDesc=shortDesc,
                                      longDesc=longDesc,
                                      bidirectional=bidirectional )
            # Break down logs
            main.funcs.analyzeLogs( shortDesc, 'portstate_down', main.eventStart, main.eventStop, main.logdir )
            return device, port
        except Exception:
            main.log.exception( "Error in linkDown" )

    @staticmethod
    def linkUp( device, port, srcComponentList, dstComponent, shortDesc, longDesc,
                sleepTime=10, bidirectional=False ):
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
                                       longDesc=longDesc,
                                       bidirectional=bidirectional )
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
            # TODO ASSERTS
            main.log.info( "Sleeping %s seconds" % sleepTime )
            time.sleep( sleepTime )
            main.step( "Stop Capturing" )
            main.funcs.stopCapturing( main,
                                      srcComponentList,
                                      dstComponent,
                                      shortDesc=shortDesc,
                                      longDesc=longDesc,
                                      bidirectional=bidirectional )
            # Break down logs
            main.funcs.analyzeLogs( shortDesc, 'portstate_up', main.eventStart, main.eventStop, main.logdir )
        except Exception:
            main.log.exception( "Error in linkUp" )

    @staticmethod
    def onlReboot( switchComponentList, srcComponentList, dstComponent,
                   shortDescFailure, longDescFailure, shortDescRecovery, longDescRecovery,
                   sleepTime=5, bidirectional=False ):
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
                                       trafficDuration=120,
                                       bidirectional=bidirectional )
            # Let some packets flow
            time.sleep( float( main.params['timers'].get( 'TrafficDiscovery', 5 ) ) )
            updatedStats = json.loads( main.Cluster.active(0).REST.portstats() )
            switchComponent = main.funcs.findSwitchWithTraffic( switchComponentList,
                                                                initialStats,
                                                                updatedStats )
            main.step( "Reboot ONL on Switch %s" % switchComponent.name )
            startTime = time.time()
            switchComponent.handle.sendline( "sudo reboot" )

            # TODO ASSERTS
            main.log.info( "Sleeping %s seconds" % sleepTime )
            time.sleep( sleepTime )
            main.step( "Stop Capturing" )
            main.funcs.stopCapturing( main,
                                      srcComponentList,
                                      dstComponent,
                                      shortDesc=shortDescFailure,
                                      longDesc=longDescFailure,
                                      bidirectional=bidirectional )
            # Break down logs
            main.funcs.analyzeLogs( shortDescFailure, 'shutdown_onl', main.eventStart, main.eventStop, main.logdir )
            main.case( longDescRecovery )
            main.step( "Start Capturing" )
            main.funcs.startCapturing( main,
                                       srcComponentList,
                                       dstComponent,
                                       shortDesc=shortDescRecovery,
                                       longDesc=longDescRecovery,
                                       trafficDuration=300,
                                       bidirectional=bidirectional )
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
                                      longDesc=longDescRecovery,
                                      bidirectional=bidirectional )
            # Break down logs
            main.funcs.analyzeLogs( shortDescRecovery, 'start_onl', main.eventStart, main.eventStop, main.logdir )
            # Check the switch is back in ONOS
        except Exception:
            main.log.exception( "Error in onlReboot" )

    @staticmethod
    def killSwitchAgent( switchComponentList, srcComponentList, dstComponent,
                         shortDescFailure, longDescFailure, shortDescRecovery,
                         longDescRecovery, sleepTime=5, bidirectional=False ):
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
                                       trafficDuration=120,
                                       bidirectional=bidirectional )
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
            # TODO ASSERTS
            main.log.info( "Sleeping %s seconds" % sleepTime )
            time.sleep( sleepTime )
            main.step( "Stop Capturing" )
            main.funcs.stopCapturing( main,
                                      srcComponentList,
                                      dstComponent,
                                      shortDesc=shortDescFailure,
                                      longDesc=longDescFailure,
                                      bidirectional=bidirectional )
            # Break down logs
            main.funcs.analyzeLogs( shortDescFailure, 'powerdown_switch', main.eventStart, main.eventStop, main.logdir )

            main.case( longDescRecovery )
            main.step( "Start Capturing" )
            main.funcs.startCapturing( main,
                                       srcComponentList,
                                       dstComponent,
                                       shortDesc=shortDescRecovery,
                                       longDesc=longDescRecovery,
                                       trafficDuration=400,
                                       bidirectional=bidirectional )
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

            main.step( "Stratum agent start on Switch %s" % switchComponent.name )
            main.log.info( "Sleeping %s seconds" % sleepTime )
            time.sleep( sleepTime )
            main.step( "Stop Capturing" )
            main.funcs.stopCapturing( main,
                                      srcComponentList,
                                      dstComponent,
                                      shortDesc=shortDescRecovery,
                                      longDesc=longDescRecovery,
                                      bidirectional=bidirectional )
            # Break down logs
            main.funcs.analyzeLogs( shortDescRecovery, 'powerup_switch', main.eventStart, main.eventStop, main.logdir )
        except Exception:
            main.log.exception( "Error in killSwitchAgent" )

    @staticmethod
    def onosDown():
        try:
            pass
        except Exception:
            main.log.exception( "Error in onosDown" )

    @staticmethod
    def analyzePcap( component, filePath, packetFilter, debug=False, timeout=240 ):
        try:
            main.log.info( "%s analyzing pcap file %s" % ( component.name, filePath ) )
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
            except Exception:
                main.log.exception( "Error in onosDown" )
                return -1
            # Remove first and last packets, sometimes there can be a long gap between
            # these and the other packets
            # Then sort by time from previous packet, grab the last one and print
            # the time from previous packet
            oneLiner = "head -n -50 | tail -n +50 | sort -u -g -k2,2 | tail -1 | cut -f2 "
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
                m = re.search( lineRE, line )
                if m:
                    if debug:
                        main.log.debug( repr( line ) )
                        main.log.info( m.groups() )
                    delta = float( m.group(1) ) * 1000
                    main.log.info( "%s: Detected downtime (longest gap between packets): %s ms" % ( component.name, delta )  )
                    return delta
            main.log.error( "No Packets found" )
            return 0
        except Exception:
            main.log.exception( "Error in analyzePcap" )

    @staticmethod
    def findPortWithTraffic( targets, initialStats, updatedStats, stat="packetsSent" ):
        """
        Given a device id and a list of ports, returns the port with the most packets sent
        between two device statistics reads
        Arguments:
            device - String, device id of the device to check
            portsList - list of ints, the ports on the device to look at
            initialStats - A dict created from the json output of ONOS device statistics
            updatedStats - A dict created from the json output of ONOS device statistics
        Optional Arguments:
            stat - String, The stat to compare for each port across updates. Defaults to 'packetsSent'
        Returns:
            The port with the largest increase in packets sent between the two device statistics

        """
        try:
            targetsStats = {}
            main.log.debug( targets )
            main.log.debug( stat )
            for device, portsList in targets.iteritems():
                deltaStats = {p: {} for p in portsList}
                for d in initialStats:
                    if d[ 'device' ] == device:
                        for p in d[ 'ports' ]:
                            if p[ 'port' ] in portsList:
                                deltaStats[ p[ 'port' ] ][ 'value1' ] = p[ stat ]
                for d in updatedStats:
                    if d[ 'device' ] == device:
                        for p in d[ 'ports' ]:
                            if p[ 'port' ] in portsList:
                                deltaStats[ p[ 'port' ] ][ 'value2' ] = p[ stat ]
                for port, stats in deltaStats.iteritems():
                    assert stats, "Expected port not found"
                    deltaStats[ port ]['delta'] = stats[ 'value2' ] - stats[ 'value1' ]
                port = max( deltaStats, key=lambda p: deltaStats[ p ][ 'value2' ] - deltaStats[ p ][ 'value1' ] )
                if deltaStats[ port ][ 'delta' ] == 0:
                    main.log.warn( "Could not find a port with traffic on %s. Likely need to wait longer for stats to be updated" % device )
                main.log.debug( port )
                targetsStats[ device ] = deltaStats
            # Find out which port has highest delta across all devices
            main.log.debug( targetsStats )
            retDevice = None
            retPort = None
            highestDelta = 0
            for device, deltaStats in targetsStats.iteritems():
                for p in deltaStats:
                    delta = deltaStats[ p ][ 'value2' ] - deltaStats[ p ][ 'value1' ]
                    if delta > highestDelta:
                        highestDelta = delta
                        retPort = p
                        retDevice = device
            main.log.debug( "Chosen port %s/%s" % ( retDevice, retPort ) )
            return retDevice, retPort
        except Exception as e:
            main.log.exception( "Error in findPortWithTraffic" )
            main.log.debug( "Initial: %s\nUpdated: %s\n" % ( initialStats, updatedStats ) )
            main.skipCase( result="FAIL", msg=e )

    @staticmethod
    def findSwitchWithTraffic( switchComponentList, initialStats, updatedStats ):
        """
        Given a list of switch components, returns the switch component with the
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
            with open( dbFileName, "w+" ) as dbfile:
                header = []
                row = []
                if not headerOrder:
                    headerOrder = main.downtimeResults.keys()
                    headerOrder.sort()
                for item in headerOrder:
                    header.append( "'%s'" % item )
                    row.append( "'%s'" % main.downtimeResults[ item ] )

                dbfile.write( ",".join( header ) + "\n" + ",".join( row ) + "\n" )
            return main.TRUE
        except IOError:
            main.log.warn( "Error opening " + dbFileName + " to write results." )
            return main.FALSE
        except KeyError:
            main.log.exception( "1 or more given headers not found" )
            return main.FALSE

    def cleanup( self, main, headerOrder=None ):
        run.cleanup( main, copyKarafLog=False )
        main.logdir = main.logdirBase
        main.step( "Writing csv results file for db" )
        writeResult = self.dbWrite( main, main.TEST + "-dbfile.csv", headerOrder )
        utilities.assert_equals( expect=main.TRUE, actual=writeResult,
                                 onpass="Successfully wrote test results to csv file",
                                 onfail="Failed to write csv file" )
