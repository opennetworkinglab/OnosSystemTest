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
        self.switchNames = {
            '0x1': ["leaf1"],
            '0x2': ["leaf1", "leaf2"],
            '2x2': ["leaf1", "leaf2", "spine101", "spine102"],
        }

        main.switchType = "ovs"

    def setupTest( self, main, topology, onosNodes, description, vlan=None ):
        if vlan is None:
            vlan = [ ]
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

            try:
                baseDir = main.logdir + "/CASE" + str( main.CurrentTestCaseNumber )
                main.logdir = baseDir
                for i in range(100):
                    if os.path.isdir( main.logdir ):
                        i += 1
                        main.logdir = baseDir + "-" + str( i )
                    else:
                        os.mkdir( main.logdir )
                        break
            except OSError as e:
                main.log.exception( "Could not make new testcase folder" )
                main.skipCase( result="FAIL", msg=e )
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
                    mininet_args += ' --vlan=%s' % ','.join( '%d' % vlanId for vlanId in vlan )
                if main.useBmv2:
                    mininet_args += ' --switch %s' % main.switchType
                    main.log.info( "Using %s switch" % main.switchType )

                run.startMininet( main, 'trellis_fabric.py', args=mininet_args )

            else:
                # Run the test with physical devices
                run.connectToPhysicalNetwork( main, hostDiscovery=False )  # We don't want to do host discovery in the pod
        except SkipCase:
            raise
        except Exception as e:
            main.log.exception( "Error in setupTest" )
            main.skipCase( result="FAIL", msg=e )

    @staticmethod
    def getHostConnections( main, hosts, excludedDIDs=None ):
        """
        Returns a dictionary with keys as devices the host is connected
        to and values as the string name of the ports connected to the host
        """
        if excludedDIDs is None:
            excludedDIDs = [ ]
        import json
        import re
        hostsJson = json.loads( main.Cluster.active(0).REST.hosts() )
        locations = {}
        if not isinstance( hosts, list ):
            hosts = [ hosts ]
        for host in hosts:
            ip = host.interfaces[0]['ips'][0]
            for h in hostsJson:
                if ip in h[ 'ipAddresses' ]:
                    for connectPoint in h[ 'locations' ]:
                        did = connectPoint[ 'elementId' ].encode( 'utf-8' )
                        skip = any( ed in did for ed in excludedDIDs )
                        if skip:
                            continue
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
            output = src.handle.before + src.handle.after
            if i == 0:
                src.handle.sendline( src.pwd )
                i = src.handle.expect( [ "password", src.prompt ] )
                assert i != 0, "Incorrect Password"
                output += src.handle.before + src.handle.after
        except Exception:
            main.log.exception( "%s: Unexpected response from ping" % src.name )
            src.handle.send( '\x03' )  # ctrl-c
            src.handle.expect( src.prompt )
            output = src.handle.before + src.handle.after
            main.log.debug( output )
            return main.FALSE
        main.log.debug( output )
        main.funcs.clearBuffer( src )
        main.log.warn( "%s: %s" % ( src.name, str( src.handle.before ) ) )
        if " 0% packet loss" in output:
            return main.TRUE
        else:
            return main.FALSE

    @staticmethod
    def startIperf( main, src, dstIp, trafficSelector, trafficDuration ):
        """
        Start iperf from src ip to dst ip
        Handles connectivity check and sudo password input as well
        Arguments:
            src: src host component
            dstIp: dst ip
            trafficSelector: traffic selector string, passed to iperf
            trafficDuration: Traffic duration string, passed to iperf

        """
        srcIp = src.interfaces[0]['ips'][0]
        iperfArgs = "%s --bind %s -c %s -t %s" % ( trafficSelector,
                                                   srcIp,
                                                   dstIp,
                                                   trafficDuration )
        main.log.info( "Starting iperf between %s and %s" % ( src.shortName, dstIp ) )
        sudoCheck = main.funcs.singlePingWithSudo( main, src, dstIp )
        if not sudoCheck:
            main.skipCase( result="FAIL",
                           msg="Unable to ping with sudo. Either flows issue or permission error." )
        src.handle.sendline( "/usr/bin/iperf %s " % iperfArgs )
        src.preDisconnect = src.exitFromProcess

    @staticmethod
    def startPing( main, src, dstIp, count=None, interval=".3" ):
        """
        Start ping from src to dst ip
        Arguments:
            src: src host component
            dstIp: dst ip
            count: how many packets to send, defaults to None, or until stopped
            interval: How long to wait, in seconds, between pings, defaults to .5
        """
        srcIface = src.interfaces[0]['name']
        pingCmd = "ping -I %s %s " % ( srcIface, dstIp )
        if count:
            pingCmd += " -c %s " % count
        if interval:
            pingCmd += " -i %s " % interval

        main.log.info( "Starting ping between %s and %s" % ( src.shortName, dstIp ) )
        src.handle.sendline( pingCmd )
        src.preDisconnect = src.exitFromProcess


    @staticmethod
    def startTshark( main, host, pingDesc=None, direction="Sender", srcIp=None, dstIp=None, protocolStr="udp" ):
        """
        """

        hostStr = ""
        if direction == "Sender":
            suffix = "Sender"
        else:
            suffix = "Receiver"
        if dstIp:
            hostStr += " && dst host %s" % dstIp
        if srcIp:
            hostStr += " && src host %s" % srcIp
        if not pingDesc:
            pingDesc = host.name
        fileName = "%s-tshark%s" % ( pingDesc, suffix )
        pcapFile = "%s/tshark/%s.pcap" % ( "~/TestON", fileName )
        tsharkArgs = "%s -i %s -f '%s %s' -w %s" % ( main.params[ 'PERF' ][ 'pcap_cmd_arguments' ],
                                                        host.interfaces[0]['name'],
                                                        protocolStr,
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
        host.preDisconnect = host.exitFromProcess

    @staticmethod
    def setupFlow( main, src, dst, shortDesc=None, longDesc=None,
                   trafficDuration=600, trafficSelector="-u -b 20M", pingOnly=False, dstIp=None ):
        """
        Setup iperf flow between two hosts, also handles packet captures, etc.
        """
        try:
            if not dstIp:
                 dstIp = dst.interfaces[0]['ips'][0]
            main.log.info( "Setting up flow between %s and %s%s" % ( src.shortName, dst.shortName, "" if not dstIp else " with dstIp %s" % dstIp ) )
            # ping right before to make sure arp is cached and sudo is authenticated
            sudoCheck1 = main.funcs.singlePingWithSudo( main, src, dst.interfaces[0]['ips'][0] )
            checkDesc = "sudo ping from %s to %s" % ( src.shortName, dst.interfaces[0]['ips'][0] )
            utilities.assert_equals( expect=main.TRUE, actual=sudoCheck1,
                                     onpass="Successfully %s" % checkDesc,
                                     onfail="Failed to %s" % checkDesc,
                                     onfailFunc=main.skipCase,
                                     onfailFuncKwargs={ 'result': 'FAIL',
                                                        'msg': "Unable to %s" % checkDesc } )
            sudoCheck2 = main.funcs.singlePingWithSudo( main, dst, src.interfaces[0]['ips'][0] )
            checkDesc = "sudo ping from %s to %s" % ( dst.shortName, src.interfaces[0]['ips'][0] )
            utilities.assert_equals( expect=main.TRUE, actual=sudoCheck2,
                                     onpass="Successfully %s" % checkDesc,
                                     onfail="Failed to %s" % checkDesc,
                                     onfailFunc=main.skipCase,
                                     onfailFuncKwargs={ 'result': 'FAIL',
                                                        'msg': "Unable to %s" % checkDesc } )
            # Start traffic
            # TODO: ASSERTS
            if pingOnly:
                trafficCmd = "ping"
                protocolStr = "icmp"
            else:
                trafficCmd = "iperf"
                protocolStr = "udp"
            trafficSrc = getattr( main, "%s-%s" % ( src.name, trafficCmd ) )
            if trafficCmd == "iperf":
                main.funcs.startIperf( main, trafficSrc, dstIp, trafficSelector, trafficDuration )
            elif trafficCmd == "ping":
                main.funcs.startPing( main, trafficSrc, dstIp )
            else:
                raise NotImplemented, "Unknown Traffic Command"
            # Start packet capture
            pingDesc = "%s-%s-to-%s" % ( shortDesc, src.shortName, dst.shortName )
            pcapFileReceiver = "%s/tshark/%s-tsharkReceiver.pcap" % ( "~/TestON", pingDesc )
            pcapFileSender = "%s/tshark/%s-tsharkSender.pcap" % ( "~/TestON", pingDesc )
            srcIp = src.interfaces[0]['ips'][0]
            main.funcs.startTshark( main, dst, pingDesc=pingDesc, direction="Receiver",
                                    srcIp=srcIp, dstIp=dstIp, protocolStr=protocolStr )
            main.funcs.startTshark( main, src, pingDesc=pingDesc, direction="Sender",
                                    srcIp=srcIp, dstIp=dstIp, protocolStr=protocolStr )

        except SkipCase:
            raise
        except Exception as e:
            main.log.exception( "Error in setupFlow" )
            main.skipCase( result="FAIL", msg=e )

    @staticmethod
    def startCapturing( main, srcList, dstList, shortDesc=None, longDesc=None,
                        trafficDuration=600, trafficSelector="-u -b 20M",
                        bidirectional=False, singleFlow=False, targets=None,
                        threshold=10, stat="packetsSent", pingOnly=False, dstIp=None ):
        """
        Starts logging, traffic generation, traffic filters, etc before a failure is induced
        src: the src component that sends the traffic
        dst: the dst component that receives the traffic
        """
        import datetime
        import json
        try:
            try:
                main.k8sLogComponents
            except ( NameError, AttributeError ):
                main.k8sLogComponents = []
            else:
                main.log.warn( "main.k8sLogComponents is already defined" )
                main.log.debug( main.k8sLogComponents )
            try:
                main.trafficComponents
            except ( NameError, AttributeError ):
                main.trafficComponents = []
            else:
                main.log.warn( "main.trafficComponents is already defined" )
                main.log.debug( main.trafficComponents )


            switchComponent = None
            ctrl = main.Cluster.active(0)
            kubeConfig = ctrl.k8s.kubeConfig
            namespace = main.params[ 'kubernetes' ][ 'namespace' ]
            pods = main.ONOSbench.kubectlGetPodNames( kubeconfig=kubeConfig,
                                                      namespace=namespace )
            # Start tailing pod logs
            for pod in pods:
                # Create new component
                newName = "%s-%s" % ( pod, "logs" )
                main.Network.copyComponent( main.ONOSbench.name, newName )
                component = getattr( main, newName )
                main.k8sLogComponents.append( component )

                path = "%s/%s_%s.log" % ( main.logdir, shortDesc, pod )
                podResults = component.sternLogs( pod,
                                                  path,
                                                  kubeconfig=kubeConfig,
                                                  namespace=namespace,
                                                  since="1s",
                                                  wait="-1" )

            if not isinstance( srcList, list ):
                srcList = [ srcList ]
            if not isinstance( dstList, list ):
                dstList = [ dstList ]
            hostPairs = []
            trafficCmd = "ping" if pingOnly else "iperf"
            for src in srcList:
                for dst in dstList:
                    if src == dst:
                        continue
                    # Create new sessions so we can handle multiple flows per host
                    flowStr = "%s-to-%s" % ( src.shortName, dst.shortName )
                    senderName = flowStr + "-Sender"
                    main.Network.copyComponent( src.name, senderName )
                    sender = getattr( main, senderName )
                    main.trafficComponents.append( sender )
                    receiverName = flowStr + "-Receiver"
                    main.Network.copyComponent( dst.name, receiverName )
                    receiver = getattr( main, receiverName )
                    main.trafficComponents.append( receiver )
                    hostPairs.append( ( sender, receiver ) )
                    main.Network.copyComponent( src.name, "%s-%s" % ( senderName, trafficCmd ) )
                    main.trafficComponents.append( getattr( main, "%s-%s" % ( senderName, trafficCmd ) ) )
                    newName = "%s-%s" % ( dst.shortName, "FileSize" )
                    main.Network.copyComponent( dst.name, newName )
                    main.trafficComponents.append( getattr( main, newName ) )
                    newName = "%s-%s" % ( src.shortName, "FileSize" )
                    main.Network.copyComponent( src.name, newName )
                    main.trafficComponents.append( getattr( main, newName ) )
                    if bidirectional:
                        # Create new sessions so we can handle multiple flows per host
                        flowStr = "%s-to-%s" % ( dst.shortName, src.shortName )
                        senderName = flowStr + "-Sender"
                        main.Network.copyComponent( dst.name, senderName )
                        sender = getattr( main, senderName )
                        main.trafficComponents.append( sender )
                        receiverName = flowStr + "-Receiver"
                        main.Network.copyComponent( src.name, receiverName )
                        receiver = getattr( main, receiverName )
                        main.trafficComponents.append( receiver )
                        hostPairs.append( ( sender, receiver ) )
                        main.Network.copyComponent( dst.name, "%s-%s" % ( senderName, trafficCmd ) )
                        main.trafficComponents.append( "%s-%s" % ( senderName, trafficCmd ) )

            # TODO: make sure hostPairs is a set?
            main.log.debug( ["%s to %s" % ( p[0], p[1] ) for p in hostPairs ] )
            # Start traffic
            # TODO: ASSERTS
            initialStats = json.loads( main.Cluster.active(0).REST.portstats() )
            main.pingStart = time.time()
            for pair in hostPairs:
                src, dst = pair
                main.funcs.setupFlow( main, src, dst, shortDesc=shortDesc,
                                      longDesc=longDesc, trafficDuration=trafficDuration,
                                      trafficSelector=trafficSelector, pingOnly=pingOnly, dstIp=dstIp )
                if singleFlow:
                    # Let some packets flow
                    trafficSleep = float( main.params['timers'].get( 'TrafficDiscovery', 10 ) )
                    main.log.info( "Sleeping %s seconds for packet counters to update" % trafficSleep )
                    time.sleep( trafficSleep )
                    updatedStats = json.loads( main.Cluster.active(0).REST.portstats() )
                    switchComponent = main.funcs.findSwitchWithTraffic( targets,
                                                                        initialStats,
                                                                        updatedStats,
                                                                        stat=stat,
                                                                        threshold=threshold )
                    # If we find a flow going through the correct path continue with test, else keep looking
                    if switchComponent:
                        srcList, dstList = src, dst
                        break
                    else:
                        main.funcs.stopFlow( main, src, dst, shortDesc=shortDesc,
                                             longDesc=longDesc, abort=True,
                                             pingOnly=pingOnly )
            if singleFlow and not switchComponent:
                main.log.error( "Could not find a flow going through desired switch/port, aborting test" )
                main.skipCase( result="PASS" )
            main.pingStarted = time.time()
            main.log.warn( "It took %s seconds to start all traffic  and tshark sessions" % ( main.pingStarted - main.pingStart ) )

            # Timestamp used for EVENT START
            main.eventStart = datetime.datetime.utcnow()
            return switchComponent, srcList, dstList
        except SkipCase:
            raise
        except Exception as e:
            main.log.exception( "Error in startCapturing" )
            main.skipCase( result="FAIL", msg=e )

    def checkContinuedFlow( self, component, path ):
        """
        We need a way to verify that traffic hasn't stopped.
        Maybe check filesize of pcaps is increasing?
        """
        first = component.fileSize( path )
        time.sleep(1)
        second = component.fileSize( path )
        result = second > first
        if result:
            main.log.info( "Flows coming in to %s" % component.shortName )
        else:
            main.log.warn( "Flows NOT coming in to %s" % component.shortName )
        return result

    @staticmethod
    def stopFlow( main, src, dst, shortDesc=None, longDesc=None, abort=False, pingOnly=False ):
        """
        Check flow is still connected, Stop iperf, tshark, etc
        """
        try:
            pingDesc = "%s-%s-to-%s" % ( shortDesc, src.shortName, dst.shortName )
            # FIXME: If we do bidirectional, we will need to change this format and update DB
            senderResultDesc = "%s-%s" % ( shortDesc, src.shortName )
            receiverResultDesc = "%s-%s-to-%s" % ( shortDesc, src.shortName, dst.shortName )
            pcapFileReceiver = "%s/tshark/%s-tsharkReceiver.pcap" % ( "~/TestON", pingDesc )
            pcapFileSender = "%s/tshark/%s-tsharkSender.pcap" % ( "~/TestON", pingDesc )

            if not abort:
                main.step( "Verify Traffic flows from %s to %s" % ( src.shortName, dst.shortName ) )
                # FIXME: These components will exist on later flows
                newName = "%s-%s" % ( src.shortName, "FileSize" )
                try:
                    getattr( main, newName )
                except AttributeError:
                    main.Network.copyComponent( src.name, newName )
                srcFilesize = getattr( main, newName )
                srcFlowCheck = main.funcs.checkContinuedFlow( srcFilesize, pcapFileSender )
                utilities.assert_equals( expect=True, actual=srcFlowCheck,
                                         onpass="Traffic is flowing from %s" % srcFilesize.shortName,
                                         onfail="Traffic is not flowing from %s" % srcFilesize.shortName )

                main.step( "Verify Traffic flows to %s from %s" % ( dst.shortName, src.shortName ) )
                newName = "%s-%s" % ( dst.shortName, "FileSize" )
                try:
                    getattr( main, newName )
                except AttributeError:
                    main.Network.copyComponent( dst.name, newName )
                dstFilesize = getattr( main, newName )
                dstFlowCheck = main.funcs.checkContinuedFlow( dstFilesize, pcapFileReceiver )
                utilities.assert_equals( expect=True, actual=dstFlowCheck,
                                         onpass="Traffic is flowing to %s" % dstFilesize.shortName,
                                         onfail="Traffic is not flowing to %s" % dstFilesize.shortName )

            # Stop packet capture
            main.funcs.clearBuffer( dst, kill=True, debug=True )
            main.funcs.clearBuffer( src, kill=True, debug=True )
            # Stop traffic
            if pingOnly:
                trafficSrc = getattr( main, "%s-ping" % src.name )
            else:
                trafficSrc = getattr( main, "%s-iperf" % src.name )
            main.funcs.clearBuffer( trafficSrc, kill=True, debug=True )

            if not abort:
                srcIp = src.interfaces[0]['ips'][0]
                if pingOnly:
                    filterStr = "'icmp "
                else:
                    filterStr = "'udp "
                filterStr += " && ip.src == %s'" % srcIp
                #senderTime = main.funcs.analyzePcap( main, src, pcapFileSender, filterStr, debug=False )
                #receiverTime = main.funcs.analyzePcap( main, dst, pcapFileReceiver, filterStr, debug=False )
                #main.downtimeResults[ "%s" % senderResultDesc ] = senderTime     # Orig
                #main.downtimeResults[ "%s" % receiverResultDesc ] = receiverTime  # Orig
                # TODO: Add alarm here if time is too high
                # Grab pcaps
                # TODO: Move this elsewhere, for automatic recovery, this could delay us
                #       to not start capture for the recovery until its already happened
                senderSCP = main.ONOSbench.scp( src, pcapFileSender, main.logdir, direction="from", timeout=300 )
                utilities.assert_equals( expect=main.TRUE, actual=senderSCP,
                                         onpass="Saved pcap files from %s" % src.name,
                                         onfail="Failed to scp pcap files from %s" % src.name )

                receiverSCP = main.ONOSbench.scp( dst, pcapFileReceiver, main.logdir, direction="from", timeout=300  )
                utilities.assert_equals( expect=main.TRUE, actual=receiverSCP,
                                         onpass="Saved pcap files from %s" % dst.name,
                                         onfail="Failed to scp pcap files from %s" % dst.name )

                senderLosses = main.funcs.analyzeIperfPcap( main,
                                                            main.logdir + "/" + pingDesc + "-tsharkSender.pcap",
                                                            filterStr,
                                                            pingOnly=pingOnly )
                receiverLosses = main.funcs.analyzeIperfPcap( main,
                                                              main.logdir + "/" + pingDesc + "-tsharkReceiver.pcap",
                                                              filterStr,
                                                              pingOnly=pingOnly )
                ms, dropped = max( senderLosses, key=lambda i: i[0] )
                colName = "%s" % senderResultDesc
                main.downtimeResults[ colName[:63] ] = ms
                colName = "%s-dropped-packets" % senderResultDesc
                main.downtimeResults[ colName[:63] ] = dropped
                ms, dropped = max( receiverLosses, key=lambda i: i[0] )
                colName = "%s" % "%s" % receiverResultDesc
                main.downtimeResults[ colName[:63] ] = ms
                colName = "%s" % "%s-dropped-packets" % receiverResultDesc
                main.downtimeResults[ colName[:63] ] = dropped

        except SkipCase:
            raise
        except Exception as e:
            main.log.exception( "Error in stopFlow" )
            main.skipCase( result="FAIL", msg=e )

    @staticmethod
    def stopCapturing( main, srcList, dstList, shortDesc=None, longDesc=None, bidirectional=False,
                       killedNodes=None, pingOnly=False ):
        import datetime
        import time
        from tests.dependencies.utils import Utils
        if killedNodes is None:
            killedNodes = [ ]
        main.utils = Utils()
        if not isinstance( srcList, list ):
            srcList = [ srcList ]
        if not isinstance( dstList, list ):
            dstList = [ dstList ]
        try:
            hostPairs = []
            for src in srcList:
                for dst in dstList:
                    if src == dst:
                        continue
                    # Create new sessions so we can handle multiple flows per host
                    flowStr = "%s-to-%s" % ( src.shortName, dst.shortName )
                    senderName = flowStr + "-Sender"
                    sender = getattr( main, senderName )
                    receiverName = flowStr + "-Receiver"
                    receiver = getattr( main, receiverName )
                    hostPairs.append( ( sender, receiver ) )
                    if bidirectional:
                        # Create new sessions so we can handle multiple flows per host
                        flowStr = "%s-to-%s" % ( dst.shortName, src.shortName )
                        senderName = flowStr + "-Sender"
                        sender = getattr( main, senderName )
                        receiverName = flowStr + "-Receiver"
                        receiver = getattr( main, receiverName )
                        hostPairs.append( ( sender, receiver ) )

            main.log.debug( [ "%s to %s" % ( p[0], p[1] ) for p in hostPairs ] )
            main.step( "Stop Capturing" )
            # Timestamp used for EVENT STOP
            main.eventStop = datetime.datetime.utcnow()

            main.pingStopping = time.time()
            for pair in hostPairs:
                src, dst = pair
                main.funcs.stopFlow( main, src, dst, shortDesc=shortDesc,
                                     longDesc=longDesc, pingOnly=pingOnly )

            main.pingStop = time.time()
            main.log.warn( "It took %s seconds since we started to stop ping for us to stop pings" % ( main.pingStop - main.pingStopping ) )
            main.log.warn( "It took %s seconds since we started ping for us to stop pcap" % ( main.pingStop - main.pingStart ) )

            kubeConfig = main.Cluster.active(0).k8s.kubeConfig
            namespace = main.params[ 'kubernetes' ][ 'namespace' ]
            # We also need to save the pod name to switch name mapping
            main.ONOSbench.kubectlPodNodes( dstPath="%s/%s-podMapping.txt" % ( main.logdir, shortDesc ),
                                            kubeconfig=kubeConfig,
                                            namespace=namespace )

            # Stop tailing logs
            for component in main.k8sLogComponents:
                #component.exitFromCmd( component.prompt )
                main.Network.removeComponent( component.name )
            main.k8sLogComponents = []

            # Grab Write logs on switches
            switches = main.ONOSbench.kubectlGetPodNames( kubeconfig=kubeConfig,
                                                          namespace=namespace,
                                                          name="stratum",
                                                          status="Running" )
            killedPods = []
            for node in killedNodes:
                pods = main.ONOSbench.kubectlGetPodNames( kubeconfig=kubeConfig,
                                                          namespace=namespace,
                                                          nodeName=node.shortName )
                killedPods.extend( pods )
            switches = [ switch for switch in switches if switch not in killedPods ]

            """
            for switch in switches:
                dstFile = "%s/%s-%s-write-reqs.txt" % ( main.logdir, shortDesc, switch )
                writeResult = main.ONOSbench.kubectlCp( switch, "/tmp/p4_writes.txt", dstFile,
                                                        kubeconfig=kubeConfig,
                                                        namespace=namespace )
                utilities.assert_equals( expect=main.TRUE, actual=writeResult,
                                         onpass="Saved write-req file from %s" % switch,
                                         onfail="Failed to cp write-req file from %s" % switch )
            """
        except SkipCase:
            raise
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
        except SkipCase:
            raise
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
    def linkDown( targets, srcComponentList, dstComponentList, shortDesc,
                  longDesc, sleepTime=10, stat='packetsSent', bidirectional=False,
                  pingOnly=False, dstIp=None ):
        """"
        High level function that handles an event including monitoring
        Arguments:
            targets - Dictionary with device ids as keys and a list of port numbers as
                      values. These will be the switch ports to check the stats of.
            srcComponentList - List containing src components, used for sending traffic
            dstComponentList - List containing src components, used for receiveing traffic
            shortDesc - String, Short description, used in reporting and file prefixes
            longDesc - String, Longer description, used in logging
        Option Arguments:
            sleepTime - How long to wait between starting the capture and stopping
            stat - String, The stat to compare for each port across updates. Defaults to 'packetsSent'
            bidirectional - Boolean, Whether to start traffic flows in both directions. Defaults to False
            pingOnly - Boolean, Use ping if True else use iperf, defaults to False
             - String, If set, use this as the destination IP for traffic, defaults to None
        Returns:
            A string of the port id that was brought down
        """
        import time
        try:
            initialStats = json.loads( main.Cluster.active(0).REST.portstats() )
            main.step( "Start Capturing" )
            threshold = 2 if pingOnly else 100
            main.funcs.startCapturing( main,
                                       srcComponentList,
                                       dstComponentList,
                                       shortDesc=shortDesc,
                                       longDesc=longDesc,
                                       bidirectional=bidirectional,
                                       threshold=threshold,
                                       pingOnly=pingOnly,
                                       dstIp=dstIp )
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

            main.funcs.stopCapturing( main,
                                      srcComponentList,
                                      dstComponentList,
                                      shortDesc=shortDesc,
                                      longDesc=longDesc,
                                      bidirectional=bidirectional,
                                      pingOnly=pingOnly )
            # Break down logs
            main.log.warn( main.logdir )
            # This is not currently working, disabling for now
            # main.funcs.analyzeLogs( shortDesc, 'portstate_down', main.eventStart, main.eventStop, main.logdir )
            return device, port
        except SkipCase:
            raise
        except Exception:
            main.log.exception( "Error in linkDown" )

    @staticmethod
    def linkUp( device, port, srcComponentList, dstComponentList, shortDesc, longDesc,
                sleepTime=10, bidirectional=False, pingOnly=False, dstIp=None ):
        """"
        High level function that handles an event including monitoring
        Arguments:
            device - String of the device uri in ONOS
            port - String of the port uri in ONOS
            srcComponentList - List containing src components, used for sending traffic
            dstComponentList - List containing src components, used for receiveing traffic
            shortDesc - String, Short description, used in reporting and file prefixes
            longDesc - String, Longer description, used in logging
        Option Arguments:
            sleepTime - How long to wait between starting the capture and stopping
            bidirectional - Boolean, Whether to start traffic flows in both directions. Defaults to False
            pingOnly - Boolean, Use ping if True else use iperf, defaults to False
            dstIp - String, If set, use this as the destination IP for traffic, defaults to None
        """
        import time
        if port is None:
            main.log.warn( "Incorrect port number, cannot bring up port" )
            return
        try:
            main.step( "Start Capturing" )
            main.funcs.startCapturing( main,
                                       srcComponentList,
                                       dstComponentList,
                                       shortDesc=shortDesc,
                                       longDesc=longDesc,
                                       bidirectional=bidirectional,
                                       threshold=100,
                                       pingOnly=pingOnly,
                                       dstIp=dstIp )
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

            main.funcs.stopCapturing( main,
                                      srcComponentList,
                                      dstComponentList,
                                      shortDesc=shortDesc,
                                      longDesc=longDesc,
                                      bidirectional=bidirectional,
                                      pingOnly=pingOnly )
            # Break down logs
            # This is not currently working, disabling for now
            # main.funcs.analyzeLogs( shortDesc, 'portstate_up', main.eventStart, main.eventStop, main.logdir )
        except SkipCase:
            raise
        except Exception:
            main.log.exception( "Error in linkUp" )

    @staticmethod
    def onlReboot( targets, srcComponentList, dstComponentList,
                   shortDescFailure, longDescFailure, shortDescRecovery, longDescRecovery,
                   sleepTime=30, stat='packetsSent',  bidirectional=False,
                   singleFlow=False ):
        """"
        High level function that handles an event including monitoring
        Arguments:
            targets - Dictionary with device ids as keys and a list of port numbers as
                      values. These will be the switch ports to check the stats of.
            srcComponentList - List containing src components, used for sending traffic
            dstComponentList - List containing src components, used for receiveing traffic
            shortDescFailure - String, Short description, used in reporting and file prefixes
            longDescFailure - String, Longer description, used in logging
            shortDescRecovery - String, Short description, used in reporting and file prefixes
            longDescRecovery - String, Longer description, used in logging
        Optional Arguments:
            sleepTime - How long to wait between starting the capture and stopping
            stat - String, The stat to compare for each port across updates. Defaults to 'packetsSent'
            bidirectional - Boolean, Whether to start traffic flows in both directions. Defaults to False
        """
        import time
        try:
            main.case( longDescFailure )
            initialStats = json.loads( main.Cluster.active(0).REST.portstats() )
            main.step( "Start Capturing" )
            switchComponent, srcComponentList, dstComponentList = main.funcs.startCapturing( main,
                                                                                             srcComponentList,
                                                                                             dstComponentList,
                                                                                             shortDesc=shortDescFailure,
                                                                                             longDesc=longDescFailure,
                                                                                             trafficDuration=720,
                                                                                             bidirectional=bidirectional,
                                                                                             singleFlow=singleFlow,
                                                                                             targets=targets,
                                                                                             stat=stat,
                                                                                             threshold=100 )
            if not switchComponent:
                # Let some packets flow
                trafficSleep = float( main.params['timers'].get( 'TrafficDiscovery', 5 ) )
                main.log.info( "Sleeping %s seconds for packet counters to update" % trafficSleep )
                time.sleep( trafficSleep )
                updatedStats = json.loads( main.Cluster.active(0).REST.portstats() )
                switchComponent = main.funcs.findSwitchWithTraffic( targets,
                                                                    initialStats,
                                                                    updatedStats,
                                                                    stat=stat )
            main.step( "Reboot ONL on Switch %s" % switchComponent.shortName )
            startTime = time.time()
            switchComponent.handle.sendline( "sudo reboot" )

            # TODO ASSERTS
            main.log.info( "Sleeping %s seconds for Fabric to react" % sleepTime )
            time.sleep( sleepTime )

            main.funcs.stopCapturing( main,
                                      srcComponentList,
                                      dstComponentList,
                                      shortDesc=shortDescFailure,
                                      longDesc=longDescFailure,
                                      bidirectional=bidirectional,
                                      killedNodes=[ switchComponent ] )
            # Break down logs
            # This is not currently working, disabling for now
            # main.funcs.analyzeLogs( shortDescFailure, 'shutdown_onl', main.eventStart, main.eventStop, main.logdir )
            restartSleep = 30
            main.log.debug( "Sleeping %s seconds because Switch takes forever to restart" % restartSleep )
            time.sleep( restartSleep )
            main.case( longDescRecovery )
            main.step( "Start Capturing" )
            main.funcs.startCapturing( main,
                                       srcComponentList,
                                       dstComponentList,
                                       shortDesc=shortDescRecovery,
                                       longDesc=longDescRecovery,
                                       trafficDuration=720,
                                       bidirectional=bidirectional,
                                       threshold=100 )
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
            main.log.info( "Sleeping %s seconds for Fabric to react" % sleepTime )
            time.sleep( sleepTime )

            main.funcs.stopCapturing( main,
                                      srcComponentList,
                                      dstComponentList,
                                      shortDesc=shortDescRecovery,
                                      longDesc=longDescRecovery,
                                      bidirectional=bidirectional )
            # Break down logs
            # This is not currently working, disabling for now
            # main.funcs.analyzeLogs( shortDescRecovery, 'start_onl', main.eventStart, main.eventStop, main.logdir )
            # Check the switch is back in ONOS
        except SkipCase:
            raise
        except Exception:
            main.log.exception( "Error in onlReboot" )

    @staticmethod
    def killSwitchAgent( targets, srcComponentList, dstComponentList,
                         shortDescFailure, longDescFailure, shortDescRecovery,
                         longDescRecovery, sleepTime=30, stat='packetsSent',
                         bidirectional=False, singleFlow=False ):
        """"
        High level function that handles an event including monitoring
        Arguments:
            targets - Dictionary with device ids as keys and a list of port numbers as
                      values. These will be the switch ports to check the stats of.
            srcComponentList - List containing src components, used for sending traffic
            dstComponentList - List containing src components, used for receiveing traffic
            shortDescFailure - String, Short description, used in reporting and file prefixes
            longDescFailure - String, Longer description, used in logging
            shortDescRecovery - String, Short description, used in reporting and file prefixes
            longDescRecovery - String, Longer description, used in logging
        Optional Arguments:
            sleepTime - How long to wait between starting the capture and stopping
            stat - String, The stat to compare for each port across updates. Defaults to 'packetsSent'
            bidirectional - Boolean, Whether to start traffic flows in both directions. Defaults to False
        """
        import time
        try:
            main.case( longDescFailure )
            initialStats = json.loads( main.Cluster.active(0).REST.portstats() )
            main.step( "Start Capturing" )
            switchComponent, srcComponentList, dstComponentList = main.funcs.startCapturing( main,
                                                                                             srcComponentList,
                                                                                             dstComponentList,
                                                                                             shortDesc=shortDescFailure,
                                                                                             longDesc=longDescFailure,
                                                                                             trafficDuration=720,
                                                                                             bidirectional=bidirectional,
                                                                                             singleFlow=singleFlow,
                                                                                             targets=targets,
                                                                                             stat=stat,
                                                                                             threshold=100 )
            if not switchComponent:
                # Let some packets flow
                time.sleep( float( main.params['timers'].get( 'TrafficDiscovery', 5 ) ) )
                updatedStats = json.loads( main.Cluster.active(0).REST.portstats() )
                switchComponent = main.funcs.findSwitchWithTraffic( targets,
                                                                    initialStats,
                                                                    updatedStats,
                                                                    stat=stat )
            main.step( "Kill stratum agent on Switch %s" % switchComponent.shortName )
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
            deleted = main.ONOSbench.kubectlDeletePod( output[0], kubeConfig, namespace )
            utilities.assert_equals( expect=main.TRUE, actual=deleted,
                                     onpass="Successfully deleted switch pod",
                                     onfail="Failed to delete switch pod" )
            # TODO ASSERTS
            main.log.info( "Sleeping %s seconds" % sleepTime )
            time.sleep( sleepTime )

            main.funcs.stopCapturing( main,
                                      srcComponentList,
                                      dstComponentList,
                                      shortDesc=shortDescFailure,
                                      longDesc=longDescFailure,
                                      bidirectional=bidirectional,
                                      killedNodes=[ switchComponent ] )
            # Break down logs
            # This is not currently working, disabling for now
            # main.funcs.analyzeLogs( shortDescFailure, 'powerdown_switch', main.eventStart, main.eventStop, main.logdir )

            main.case( longDescRecovery )
            main.step( "Start Capturing" )
            main.funcs.startCapturing( main,
                                       srcComponentList,
                                       dstComponentList,
                                       shortDesc=shortDescRecovery,
                                       longDesc=longDescRecovery,
                                       trafficDuration=720,
                                       bidirectional=bidirectional,
                                       threshold=100 )
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

            main.funcs.stopCapturing( main,
                                      srcComponentList,
                                      dstComponentList,
                                      shortDesc=shortDescRecovery,
                                      longDesc=longDescRecovery,
                                      bidirectional=bidirectional )
            # Break down logs
            # This is not currently working, disabling for now
            # main.funcs.analyzeLogs( shortDescRecovery, 'powerup_switch', main.eventStart, main.eventStop, main.logdir )
        except SkipCase:
            raise
        except Exception:
            main.log.exception( "Error in killSwitchAgent" )

    @staticmethod
    def onosDown( main, controller, preventRestart=False ):
        """
        Brings down an ONOS kubernetes pod. If preventRestart, will attempt to prevent
        it from coming back on that node by adding a taint.
        Returns the nodeName of the pod that was killed
        """
        try:
            # Get pod name to delete
            podName = controller.k8s.podName
            kubeConfig = main.Cluster.active(0).k8s.kubeConfig
            namespace = main.params[ 'kubernetes' ][ 'namespace' ]
            if preventRestart:
                # Cordon off the node so no more pods will be scheduled
                k8sNode = controller.Bench.kubectlGetPodNode( podName,
                                                              kubeconfig=kubeConfig,
                                                              namespace=namespace )
                main.step( "Cordon off k8s node %s, which is hosting onos k8s pod %s" % ( k8sNode,
                                                                                          controller.name ) )
                cordoned = controller.Bench.kubectlCordonNode( k8sNode,
                                                               kubeconfig=kubeConfig,
                                                               namespace=namespace )
                utilities.assert_equals( expect=main.TRUE, actual=cordoned,
                                         onpass="Successfully cordoned k8s node",
                                         onfail="Failed to cordon off k8s node" )
                controller.active = False
                main.Cluster.setRunningNode( main.Cluster.getRunningPos() )
            else:
                k8sNode = None
            main.step( "Delete onos k8s pod %s" % controller.name )
            #startTime = time.time()
            # Delete pod
            deleted = controller.Bench.kubectlDeletePod( podName, kubeConfig, namespace )
            utilities.assert_equals( expect=main.TRUE, actual=deleted,
                                     onpass="Successfully deleted switch pod",
                                     onfail="Failed to delete switch pod" )
            return k8sNode
        except SkipCase:
            raise
        except Exception:
            main.log.exception( "Error in onosDown" )

    @staticmethod
    def onosUp( main, k8sNode, controller ):
        """
        Brings up an ONOS kubernetes pod by uncordoning the node
        """
        try:
            kubeConfig = main.Cluster.active(0).k8s.kubeConfig
            namespace = main.params[ 'kubernetes' ][ 'namespace' ]
            podName = controller.k8s.podName
            # Uncordon the node so pod will be scheduled
            main.step( "Uncordon k8s node %s, which is hosting onos k8s pod %s" % ( k8sNode,
                                                                                    controller.name ) )
            #startTime = time.time()
            uncordoned = controller.Bench.kubectlUncordonNode( k8sNode,
                                                               kubeconfig=kubeConfig,
                                                               namespace=namespace )
            utilities.assert_equals( expect=main.TRUE, actual=uncordoned,
                                     onpass="Successfully uncordoned k8s node",
                                     onfail="Failed to uncordon k8s node" )

            # Check pod is ready
            main.step( "Wait for ONOS pod to restart" )
            ready = utilities.retry( controller.Bench.kubectlCheckPodReady,
                                     main.FALSE,
                                     kwargs={ "podName": podName,
                                              "kubeconfig": kubeConfig,
                                              "namespace": namespace },
                                     attempts=50,
                                     getRetryingTime=True )
            utilities.assert_equals( expect=main.TRUE, actual=ready,
                                     onpass="Successfully restarted onos pod",
                                     onfail="Failed to restart onos pod" )
            controller.active = True
            # Set all nodes as "running", then reduce to only "active" nodes
            main.Cluster.runningNodes = main.Cluster.controllers
            main.Cluster.setRunningNode( main.Cluster.getRunningPos() )
            controller.k8s.clearBuffer()
            controller.k8s.kubectlPortForward( podName,
                                               controller.k8s.portForwardList,
                                               kubeConfig,
                                               namespace )
            #stopTime = time.time()
        except SkipCase:
            raise
        except Exception:
            main.log.exception( "Error in onosUp" )

    @staticmethod
    def analyzeIperfPcap( main, pcapFile, filterStr, timeout=240, pingOnly=False ):
        """
        Given a pcap file, will use tshark to create a csv file with iperf fields.
        Then reads the file and computes drops in packets and duration of disruption
        """
        try:
            import csv
            import datetime
            baseName = pcapFile[ :pcapFile.rfind('.') ]
            csvFile = baseName + ".csv"  # TODO: Strip any file extensions from pcapFile first
            tsharkCmd = 'tshark -r %s -Y %s -T fields -e frame.number -e frame.time_delta -e frame.time_epoch -e ip.src -e ip.dst ' % ( pcapFile, filterStr )
            if pingOnly:
                tsharkCmd += ' -e icmp.seq '
            else:
                tsharkCmd += ' -e iperf2.udp.sequence -d udp.port==5001,iperf2'
            tsharkCmd += ' -E separator=,'
            bench = main.ONOSbench
            bench.handle.sendline( "%s > %s" % ( tsharkCmd, csvFile ) )
            bench.handle.expect( bench.Prompt(), timeout=timeout )
            main.log.debug( bench.handle.before + bench.handle.after )

            DEBUGGING = False
            prevSeq = None
            prevTime = None
            prevPacket = None
            highestDelta = 0
            output = []
            with open( csvFile ) as f:
                reader = csv.DictReader( f, fieldnames=[ 'frame', 'delta', 'epoch', 'src', 'dst', 'sequence' ] )
                for packet in reader:
                    try:
                        curSeq = int( packet['sequence'] )
                        assert curSeq > 1
                    except ValueError:
                        main.log.error( "Could not parse packet: %s" % packet )
                    except AssertionError:
                        main.log.error( "Negative sequence number, flow ended too soon: %s" % packet )
                        continue
                    curTime = datetime.datetime.fromtimestamp( float( packet['epoch'] ) ) # Epoch arrival time of packet
                    if float( packet[ 'delta' ] ) >  .002:  # Over 2 ms, we have about .6 ms send rate
                        main.log.warn( packet )

                    if prevSeq:
                        diff = curSeq - prevSeq
                        if diff > 1:
                            if DEBUGGING or diff > 1:
                                main.log.debug( "\nCurrent Packet:  %s\n vs.\nPrevious Packet: %s" % ( packet, prevPacket ) )
                            duration = curTime - prevTime
                            millis = float( duration.days ) * 24 * 60 * 60 * 1000
                            millis += float( duration.seconds ) * 1000
                            millis += float( duration.microseconds ) / 1000
                            main.log.debug( duration )
                            result = ( millis, diff - 1 )
                            main.log.debug( result )
                            if int( packet['frame'] ) < 50:
                                main.log.warn( "I plan to ignore this" )
                            output.append( result )
                    prevSeq = curSeq
                    prevTime = curTime
                    prevPacket = packet
                    if packet[ 'delta' ] > highestDelta:
                        highestDelta = packet[ 'delta' ]
            if not output:
                output.append( ( float( highestDelta ) * 1000, 0 ) )
            if prevPacket:
                main.log.debug( "Total packet count: %s" % prevPacket[ 'frame' ] )
            else:
                main.log.warn( "No packets were found to analyze" )
            main.log.warn( output )

            # TODO What to return? List of touples? [(duration, dropped Packets),...] ?
            return output
        except SkipCase:
            raise
        except Exception as e:
            main.log.exception( "Error in analyzeIperfPcap" )

    @staticmethod
    def analyzePcap( main, component, filePath, packetFilter, debug=False, timeout=240 ):
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
            except SkipCase:
                raise
            except Exception:
                main.log.exception( "Error in analyzePcap" )
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
        except SkipCase:
            raise
        except Exception:
            main.log.exception( "Error in analyzePcap" )

    @staticmethod
    def portstatsDelta( targets, initialStats, updatedStats, stat="packetsSent" ):
        """
        Given a dictionary of device ids and port numbers, and two port statistics
        dictionaries, returns a dictionary with a delta for the given statistic.
        Arguments:
            targets - Dictionary with device ids as keys and a list of port numbers as
                      values. These will be the switch ports to check the stats of.
            initialStats - A dict created from the json output of ONOS device statistics
            updatedStats - A dict created from the json output of ONOS device statistics
        Optional Arguments:
            stat - String, The stat to compare for each port across updates. Defaults to 'packetsSent'
        Returns:
            A dictionary containing a delta for the given statistic for each port.
        """
        try:
            targetsStats = { }
            main.log.debug( targets )
            main.log.debug( stat )
            for device, portsList in targets.iteritems():
                deltaStats = { p: { } for p in portsList }
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
                    deltaStats[ port ][ 'delta' ] = stats[ 'value2' ] - stats[ 'value1' ]
                port = max( deltaStats, key=lambda p: deltaStats[ p ][ 'value2' ] - deltaStats[ p ][ 'value1' ] )
                if deltaStats[ port ][ 'delta' ] == 0:
                    main.log.warn(
                            "Could not find a port with traffic on %s. Likely need to wait longer for stats to be updated" %
                            device )
                main.log.debug( port )
                targetsStats[ device ] = deltaStats
            return targetsStats
        except SkipCase:
            raise
        except Exception as e:
            main.log.exception( "Error in portstatsDelta" )
            main.log.debug( "Initial: %s\nUpdated: %s\n" % (initialStats, updatedStats) )
            main.skipCase( result="FAIL", msg=e )

    @staticmethod
    def findPortWithTraffic( targets, initialStats, updatedStats, stat="packetsSent", threshold=10 ):
        """
        Given a device id and a list of ports, returns the port with the most packets sent
        between two device statistics reads
        Arguments:
            targets - Dictionary with device ids as keys and a list of port numbers as
                      values. These will be the switch ports to check the stats of.
            initialStats - A dict created from the json output of ONOS device statistics
            updatedStats - A dict created from the json output of ONOS device statistics
        Optional Arguments:
            stat - String, The stat to compare for each port across updates. Defaults to 'packetsSent'
        Returns:
            The port with the largest increase in packets sent between the two device statistics
        """
        try:

            # Find out which port has highest delta across all devices
            targetsStats = main.funcs.portstatsDelta( targets, initialStats, updatedStats, stat )
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
            if highestDelta < threshold:
                main.log.warn( "Delta not above threshold of %s" % threshold )
                return None, None
            return retDevice, retPort
        except SkipCase:
            raise
        except Exception as e:
            main.log.exception( "Error in findPortWithTraffic" )
            main.log.debug( "Initial: %s\nUpdated: %s\n" % ( initialStats, updatedStats ) )
            main.skipCase( result="FAIL", msg=e )

    @staticmethod
    def findSwitchWithTraffic( targets, initialStats, updatedStats, stat="packetsSent", threshold=10 ):
        """
        Given a dictionary containing switches and ports, returns the switch component with the
        port with the largest delta of the given stat between two device statistics reads
        Arguments:
            targets - Dictionary with device ids as keys and a list of port numbers as
                      values. These will be the switch ports to check the stats of.
            initialStats - A dict created from the json output of ONOS device statistics
            updatedStats - A dict created from the json output of ONOS device statistics
        Optional Arguments:
            stat - String, The stat to compare for each port across updates. Defaults to 'packetsSent'
        Returns:
            The switch component with the port with the largest increase in packets sent
            between the two device statistics

        """
        try:
            device, port = main.funcs.findPortWithTraffic( targets, initialStats,
                                                           updatedStats, stat=stat,
                                                           threshold=threshold )
            if not device:
                return None
            switchComponent = None
            switches = main.Network.getSwitches()
            main.log.debug( switches )
            for switch, data in switches.iteritems():
                if switch in device:
                    switchComponent = main.Network.switches[ switch ]
            main.log.debug( switchComponent )
            return switchComponent
        except SkipCase:
            raise
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
        except SkipCase:
            raise
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
            if not main.downtimeResults:
                return main.TRUE
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
        try:
            if hasattr( main, "trafficComponents" ):
                for component in main.trafficComponents:
                    main.Network.removeComponent( component.name )
            main.trafficComponents = []
        except Exception:
            main.log.exception( "Error cleaning up traffic components" )

        run.cleanup( main, copyKarafLog=False )
        main.logdir = main.logdirBase
        main.step( "Writing csv results file for db" )
        writeResult = self.dbWrite( main, main.TEST + "-dbfile.csv", headerOrder )
        utilities.assert_equals( expect=main.TRUE, actual=writeResult,
                                 onpass="Successfully wrote test results to csv file",
                                 onfail="Failed to write csv file" )
