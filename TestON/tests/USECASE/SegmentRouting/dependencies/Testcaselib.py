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
import os
import imp
import time
import json
import urllib
from core import utilities


class Testcaselib:

    useSSH = True

    @staticmethod
    def initTest( main ):
        """
        - Construct tests variables
        - GIT ( optional )
            - Checkout ONOS master branch
            - Pull latest ONOS code
        - Building ONOS ( optional )
            - Install ONOS package
            - Build ONOS package
        """
        try:
            from tests.dependencies.ONOSSetup import ONOSSetup
            main.testSetUp = ONOSSetup()
        except ImportError:
            main.log.error( "ONOSSetup not found. exiting the test" )
            main.cleanAndExit()
        from tests.dependencies.Network import Network
        main.Network = Network()
        main.testSetUp.envSetupDescription( False )
        stepResult = main.FALSE
        try:
            main.step( "Constructing test variables" )
            # Test variables
            main.cellName = main.params[ 'ENV' ][ 'cellName' ]
            main.apps = main.params[ 'ENV' ][ 'cellApps' ]
            main.path = os.path.dirname( main.testFile )
            main.topoPath = main.path + "/../dependencies/"
            main.configPath = main.path + "/../dependencies/conf/"
            main.testConfPath = main.path + "/dependencies/conf/"
            main.topology = main.params[ 'DEPENDENCY' ][ 'topology' ]
            main.topologyLib = main.params[ 'DEPENDENCY' ][ 'lib' ] if 'lib' in main.params[ 'DEPENDENCY' ] else None
            main.topologyConf = main.params[ 'DEPENDENCY' ][ 'conf' ] if 'conf' in main.params[ 'DEPENDENCY' ] else None
            main.testConf = main.params[ 'DEPENDENCY' ][ 'testConf' ] if 'testConf' in main.params[ 'DEPENDENCY' ] else None
            main.scale = ( main.params[ 'SCALE' ][ 'size' ] ).split( "," )
            main.maxNodes = int( main.params[ 'SCALE' ][ 'max' ] )
            main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )

            stepResult = main.testSetUp.envSetup( False )
        except Exception as e:
            main.testSetUp.envSetupException( e )

        main.testSetUp.evnSetupConclusion( stepResult )

    @staticmethod
    def installOnos( main, vlanCfg=True, skipPackage=False, cliSleep=10,
                     parallel=True ):
        """
        - Set up cell
            - Create cell file
            - Set cell file
            - Verify cell file
        - Kill ONOS process
        - Uninstall ONOS cluster
        - Verify ONOS start up
        - Install ONOS cluster
        - Connect to cli
        """
        # main.scale[ 0 ] determines the current number of ONOS controller
        if not main.apps:
            main.log.error( "App list is empty" )
        main.log.info( "NODE COUNT = " + str( main.Cluster.numCtrls ) )
        main.log.info( ''.join( main.Cluster.getIps() ) )
        main.dynamicHosts = [ 'in1', 'out1' ]
        main.testSetUp.ONOSSetUp( main.Cluster, newCell=True, cellName=main.cellName,
                                  skipPack=skipPackage,
                                  useSSH=Testcaselib.useSSH,
                                  installParallel=parallel, includeCaseDesc=False )
        ready = utilities.retry( main.Cluster.active( 0 ).CLI.summary,
                                 main.FALSE,
                                 sleep=cliSleep,
                                 attempts=10 )
        if ready:
            ready = main.TRUE
        utilities.assert_equals( expect=main.TRUE, actual=ready,
                                 onpass="ONOS summary command succeded",
                                 onfail="ONOS summary command failed" )

        with open( "%s/json/%s.json" % (main.configPath, main.cfgName)) as cfg:
            main.Cluster.active( 0 ).REST.setNetCfg(json.load(cfg))
        with open("%s/json/%s.chart" % (main.configPath, main.cfgName)) as chart:
            main.pingChart = json.load(chart)
        if not ready:
            main.log.error( "ONOS startup failed!" )
            main.cleanAndExit()

        for ctrl in main.Cluster.active():
            ctrl.CLI.logSet( "DEBUG", "org.onosproject.segmentrouting" )
            ctrl.CLI.logSet( "DEBUG", "org.onosproject.driver.pipeline" )
            ctrl.CLI.logSet( "DEBUG", "org.onosproject.store.group.impl" )
            ctrl.CLI.logSet( "DEBUG", "org.onosproject.net.flowobjective.impl" )

    @staticmethod
    def startMininet( main, topology, args="" ):
        copyResult = main.ONOSbench.scp( main.Mininet1,
                                         main.topoPath + main.topology,
                                         main.Mininet1.home,
                                         direction="to" )
        if main.topologyLib:
            for lib in main.topologyLib.split(","):
                copyResult = copyResult and main.ONOSbench.scp( main.Mininet1,
                                                                main.topoPath + lib,
                                                                main.Mininet1.home,
                                                                direction="to" )
        if main.topologyConf:
            for conf in main.topologyConf.split(","):
                copyResult = copyResult and main.ONOSbench.scp( main.Mininet1,
                                                                main.configPath + conf,
                                                                "~/",
                                                                direction="to" )
        if main.testConf:
            for conf in main.testConf.split(","):
                copyResult = copyResult and main.ONOSbench.scp( main.Mininet1,
                                                                main.testConfPath + conf,
                                                                "~/",
                                                                direction="to" )
        stepResult = copyResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully copied topo files",
                                 onfail="Failed to copy topo files" )
        main.step( "Starting Mininet Topology" )
        arg = "--onos-ip=%s %s" % (",".join([ctrl.ipAddress for ctrl in main.Cluster.runningNodes]), args)
        main.topology = topology
        topoResult = main.Mininet1.startNet(
                topoFile=main.Mininet1.home + main.topology, args=arg )
        stepResult = topoResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanAndExit()

    @staticmethod
    def connectToPhysicalNetwork( main, switchNames ):
        main.step( "Connecting to physical netowrk" )
        topoResult = main.NetworkBench.connectToNet()
        stepResult = topoResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanAndExit()

        main.step( "Assign switches to controllers." )
        assignResult = main.TRUE
        for name in switchNames:
            assignResult = assignResult & main.NetworkBench.assignSwController( sw=name,
                                                                                ip=main.Cluster.getIps(),
                                                                                port='6653' )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully assign switches to controllers",
                                 onfail="Failed to assign switches to controllers" )

    @staticmethod
    def config( main, cfgName ):
        main.spines = []

        main.failures = int( main.params[ 'failures' ] )
        main.cfgName = cfgName

        if main.cfgName == '2x2':
            spine = {}
            spine[ 'name' ] = main.params[ 'switches' ][ 'spine1' ]
            spine[ 'dpid' ] = main.params[ 'switches' ][ 'spinedpid1' ]
            main.spines.append( spine )

            spine = {}
            spine[ 'name' ] = main.params[ 'switches' ][ 'spine2' ]
            spine[ 'dpid' ] = main.params[ 'switches' ][ 'spinedpid2' ]
            main.spines.append( spine )

        elif main.cfgName == '4x4':
            spine = {}
            spine[ 'name' ] = main.params[ 'switches' ][ 'spine1' ]
            spine[ 'dpid' ] = main.params[ 'switches' ][ 'spinedpid1' ]
            main.spines.append( spine )

            spine = {}
            spine[ 'name' ] = main.params[ 'switches' ][ 'spine2' ]
            spine[ 'dpid' ] = main.params[ 'switches' ][ 'spinedpid2' ]
            main.spines.append( spine )

            spine = {}
            spine[ 'name' ] = main.params[ 'switches' ][ 'spine3' ]
            spine[ 'dpid' ] = main.params[ 'switches' ][ 'spinedpid3' ]
            main.spines.append( spine )

            spine = {}
            spine[ 'name' ] = main.params[ 'switches' ][ 'spine4' ]
            spine[ 'dpid' ] = main.params[ 'switches' ][ 'spinedpid4' ]
            main.spines.append( spine )

        else:
            main.log.error( "Configuration failed!" )
            main.cleanAndExit()

    @staticmethod
    def checkFlows( main, minFlowCount, tag="", dumpflows=True, sleep=10 ):
        main.step(
                " Check whether the flow count is bigger than %s" % minFlowCount )
        if tag == "":
            tag = 'CASE%d' % main.CurrentTestCaseNumber
        count = utilities.retry( main.Cluster.active( 0 ).CLI.checkFlowCount,
                                 main.FALSE,
                                 kwargs={ 'min': minFlowCount },
                                 attempts=10,
                                 sleep=sleep )
        utilities.assertEquals(
                expect=True,
                actual=( count > 0 ),
                onpass="Flow count looks correct: " + str( count ),
                onfail="Flow count looks wrong: " + str( count ) )

        main.step( "Check whether all flow status are ADDED" )
        flowCheck = utilities.retry( main.Cluster.active( 0 ).CLI.checkFlowsState,
                                     main.FALSE,
                                     kwargs={ 'isPENDING': False },
                                     attempts=5,
                                     sleep=sleep )
        utilities.assertEquals(
                expect=main.TRUE,
                actual=flowCheck,
                onpass="Flow status is correct!",
                onfail="Flow status is wrong!" )
        if dumpflows:
            main.ONOSbench.dumpONOSCmd( main.Cluster.active( 0 ).ipAddress,
                                        "flows",
                                        main.logdir,
                                        tag + "_FlowsBefore" )
            main.ONOSbench.dumpONOSCmd( main.Cluster.active( 0 ).ipAddress,
                                        "groups",
                                        main.logdir,
                                        tag + "_GroupsBefore" )

    @staticmethod
    def checkFlowsByDpid( main, dpid, minFlowCount, sleep=10 ):
        main.step(
                " Check whether the flow count of device %s is bigger than %s" % ( dpid, minFlowCount ) )
        count = utilities.retry( main.Cluster.active( 0 ).CLI.flowAddedCount,
                                 None,
                                 args=( dpid, ),
                                 attempts=5,
                                 sleep=sleep )
        utilities.assertEquals(
                expect=True,
                actual=( int( count ) > minFlowCount ),
                onpass="Flow count looks correct: " + count ,
                onfail="Flow count looks wrong: " + count )

    @staticmethod
    def pingAll( main, tag="", dumpflows=True, acceptableFailed=0, basedOnIp=False ):
        '''
        acceptableFailed: max number of acceptable failed pings. Only works for ping6
        basedOnIp: if True, run ping or ping6 based on suffix of host names
        '''
        main.log.report( "Check full connectivity" )
        print main.pingChart
        if tag == "":
            tag = 'CASE%d' % main.CurrentTestCaseNumber
        for entry in main.pingChart.itervalues():
            print entry
            hosts, expect = entry[ 'hosts' ], entry[ 'expect' ]
            try:
                expect = main.TRUE if str(expect).lower() == 'true' else main.FALSE
            except:
                expect = main.FALSE
            main.step( "Connectivity for %s %s" % ( str( hosts ), tag ) )

            if basedOnIp:
                if ("v4" in hosts[0]):
                    pa = main.Network.pingallHosts( hosts )
                    utilities.assert_equals( expect=expect, actual=pa,
                                             onpass="IPv4 connectivity successfully tested",
                                             onfail="IPv4 connectivity failed" )
                if ("v6" in hosts[0]):
                    pa = main.Network.pingIpv6Hosts( hosts, acceptableFailed=acceptableFailed )
                    utilities.assert_equals( expect=expect, actual=pa,
                                             onpass="IPv6 connectivity successfully tested",
                                             onfail="IPv6 connectivity failed" )
            else:
                pa = main.Network.pingallHosts( hosts )
                utilities.assert_equals( expect=expect, actual=pa,
                                         onpass="IP connectivity successfully tested",
                                         onfail="IP connectivity failed" )

        if dumpflows:
            main.ONOSbench.dumpONOSCmd( main.Cluster.active( 0 ).ipAddress,
                                        "flows",
                                        main.logdir,
                                        tag + "_FlowsOn" )
            main.ONOSbench.dumpONOSCmd( main.Cluster.active( 0 ).ipAddress,
                                        "groups",
                                        main.logdir,
                                        tag + "_GroupsOn" )

    @staticmethod
    def killLink( main, end1, end2, switches, links ):
        """
        end1,end2: identify the switches, ex.: 'leaf1', 'spine1'
        switches, links: number of expected switches and links after linkDown, ex.: '4', '6'
        Kill a link and verify ONOS can see the proper link change
        """
        main.linkSleep = float( main.params[ 'timers' ][ 'LinkDiscovery' ] )
        main.step( "Kill link between %s and %s" % ( end1, end2 ) )
        LinkDown = main.Network.link( END1=end1, END2=end2, OPTION="down" )
        LinkDown = main.Network.link( END2=end1, END1=end2, OPTION="down" )
        main.log.info(
                "Waiting %s seconds for link down to be discovered" % main.linkSleep )
        time.sleep( main.linkSleep )
        topology = utilities.retry( main.Cluster.active( 0 ).CLI.checkStatus,
                                    main.FALSE,
                                    kwargs={ 'numoswitch': switches,
                                             'numolink': links },
                                    attempts=10,
                                    sleep=main.linkSleep )
        result = topology & LinkDown
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                 onpass="Link down successful",
                                 onfail="Failed to turn off link?" )

    @staticmethod
    def restoreLink( main, end1, end2, dpid1, dpid2, port1, port2, switches,
                     links ):
        """
        Params:
            end1,end2: identify the end switches, ex.: 'leaf1', 'spine1'
            dpid1, dpid2: dpid of the end switches respectively, ex.: 'of:0000000000000002'
            port1, port2: respective port of the end switches that connects to the link, ex.:'1'
            switches, links: number of expected switches and links after linkDown, ex.: '4', '6'
        Kill a link and verify ONOS can see the proper link change
        """
        main.step( "Restore link between %s and %s" % ( end1, end2 ) )
        result = False
        count = 0
        while True:
            count += 1
            main.Network.link( END1=end1, END2=end2, OPTION="up" )
            main.Network.link( END2=end1, END1=end2, OPTION="up" )
            main.log.info(
                    "Waiting %s seconds for link up to be discovered" % main.linkSleep )
            time.sleep( main.linkSleep )

            for i in range( 0, main.Cluster.numCtrls ):
                ctrl = main.Cluster.runningNodes[ i ]
                onosIsUp = main.ONOSbench.isup( ctrl.ipAddress )
                if onosIsUp == main.TRUE:
                    ctrl.CLI.portstate( dpid=dpid1, port=port1, state='Enable' )
                    ctrl.CLI.portstate( dpid=dpid2, port=port2, state='Enable' )
            time.sleep( main.linkSleep )

            result = main.Cluster.active( 0 ).CLI.checkStatus( numoswitch=switches,
                                                               numolink=links )
            if count > 5 or result:
                break
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                 onpass="Link up successful",
                                 onfail="Failed to bring link up" )

    @staticmethod
    def killSwitch( main, switch, switches, links ):
        """
        Params: switches, links: number of expected switches and links after SwitchDown, ex.: '4', '6'
        Completely kill a switch and verify ONOS can see the proper change
        """
        main.switchSleep = float( main.params[ 'timers' ][ 'SwitchDiscovery' ] )
        main.step( "Kill " + switch )
        main.log.info( "Stopping" + switch )
        main.Network.switch( SW=switch, OPTION="stop" )
        # todo make this repeatable
        main.log.info( "Waiting %s seconds for switch down to be discovered" % (
            main.switchSleep ) )
        time.sleep( main.switchSleep )
        topology = utilities.retry( main.Cluster.active( 0 ).CLI.checkStatus,
                                    main.FALSE,
                                    kwargs={ 'numoswitch': switches,
                                             'numolink': links },
                                    attempts=10,
                                    sleep=main.switchSleep )
        utilities.assert_equals( expect=main.TRUE, actual=topology,
                                 onpass="Kill switch successful",
                                 onfail="Failed to kill switch?" )

    @staticmethod
    def recoverSwitch( main, switch, switches, links ):
        """
        Params: switches, links: number of expected switches and links after SwitchUp, ex.: '4', '6'
        Recover a switch and verify ONOS can see the proper change
        """
        # todo make this repeatable
        main.step( "Recovering " + switch )
        main.log.info( "Starting" + switch )
        main.Network.switch( SW=switch, OPTION="start" )
        main.log.info( "Waiting %s seconds for switch up to be discovered" % (
            main.switchSleep ) )
        time.sleep( main.switchSleep )
        topology = utilities.retry( main.Cluster.active( 0 ).CLI.checkStatus,
                                    main.FALSE,
                                    kwargs={ 'numoswitch': switches,
                                             'numolink': links },
                                    attempts=10,
                                    sleep=main.switchSleep )
        utilities.assert_equals( expect=main.TRUE, actual=topology,
                                 onpass="Switch recovery successful",
                                 onfail="Failed to recover switch?" )

    @staticmethod
    def cleanup( main ):
        """
        Stop Onos-cluster.
        Stops Mininet
        Copies ONOS log
        """
        try:
            from tests.dependencies.utils import Utils
        except ImportError:
            main.log.error( "Utils not found exiting the test" )
            main.cleanAndExit()
        try:
            main.utils
        except ( NameError, AttributeError ):
            main.utils = Utils()

        main.utils.mininetCleanup( main.Mininet1 )

        main.utils.copyKarafLog( "CASE%d" % main.CurrentTestCaseNumber, before=True, includeCaseDesc=False )

        for ctrl in main.Cluster.active():
            main.ONOSbench.onosStop( ctrl.ipAddress )

    @staticmethod
    def killOnos( main, nodes, switches, links, expNodes ):
        """
        Params: nodes, integer array with position of the ONOS nodes in the CLIs array
        switches, links, nodes: number of expected switches, links and nodes after KillOnos, ex.: '4', '6'
        Completely Kill an ONOS instance and verify the ONOS cluster can see the proper change
        """
        main.step( "Killing ONOS instance" )

        for i in nodes:
            killResult = main.ONOSbench.onosDie( main.Cluster.runningNodes[ i ].ipAddress )
            utilities.assert_equals( expect=main.TRUE, actual=killResult,
                                     onpass="ONOS instance Killed",
                                     onfail="Error killing ONOS instance" )
            main.Cluster.runningNodes[ i ].active = False
        time.sleep( 12 )

        if len( nodes ) < main.Cluster.numCtrls:

            nodeResults = utilities.retry( main.Cluster.nodesCheck,
                                           False,
                                           attempts=5,
                                           sleep=10 )
            utilities.assert_equals( expect=True, actual=nodeResults,
                                     onpass="Nodes check successful",
                                     onfail="Nodes check NOT successful" )

            if not nodeResults:
                for i in nodes:
                    ctrl = main.Cluster.runningNodes[ i ]
                    main.log.debug( "{} components not ACTIVE: \n{}".format(
                        ctrl.name,
                        ctrl.CLI.sendline( "scr:list | grep -v ACTIVE" ) ) )
                main.log.error( "Failed to kill ONOS, stopping test" )
                main.cleanAndExit()

            topology = utilities.retry( main.Cluster.active( 0 ).CLI.checkStatus,
                                        main.FALSE,
                                        kwargs={ 'numoswitch': switches,
                                                 'numolink': links,
                                                 'numoctrl': expNodes },
                                        attempts=10,
                                        sleep=12 )
            utilities.assert_equals( expect=main.TRUE, actual=topology,
                                     onpass="ONOS Instance down successful",
                                     onfail="Failed to turn off ONOS Instance" )

    @staticmethod
    def recoverOnos( main, nodes, switches, links, expNodes ):
        """
        Params: nodes, integer array with position of the ONOS nodes in the CLIs array
        switches, links, nodes: number of expected switches, links and nodes after recoverOnos, ex.: '4', '6'
        Recover an ONOS instance and verify the ONOS cluster can see the proper change
        """
        main.step( "Recovering ONOS instance" )
        [ main.ONOSbench.onosStart( main.Cluster.runningNodes[ i ].ipAddress ) for i in nodes ]
        for i in nodes:
            isUp = main.ONOSbench.isup( main.Cluster.runningNodes[ i ].ipAddress )
            utilities.assert_equals( expect=main.TRUE, actual=isUp,
                                     onpass="ONOS service is ready",
                                     onfail="ONOS service did not start properly" )
        for i in nodes:
            main.step( "Checking if ONOS CLI is ready" )
            ctrl = main.Cluster.runningNodes[ i ]
            # ctrl.CLI.startCellCli()
            cliResult = ctrl.CLI.startOnosCli( ctrl.ipAddress,
                                               commandlineTimeout=60,
                                               onosStartTimeout=100 )
            ctrl.active = True
            utilities.assert_equals( expect=main.TRUE,
                                     actual=cliResult,
                                     onpass="ONOS CLI is ready",
                                     onfail="ONOS CLI is not ready" )

        main.step( "Checking ONOS nodes" )
        nodeResults = utilities.retry( main.Cluster.nodesCheck,
                                       False,
                                       attempts=5,
                                       sleep=10 )
        utilities.assert_equals( expect=True, actual=nodeResults,
                                 onpass="Nodes check successful",
                                 onfail="Nodes check NOT successful" )

        if not nodeResults:
            for i in nodes:
                ctrl = main.Cluster.runningNodes[ i ]
                main.log.debug( "{} components not ACTIVE: \n{}".format(
                    ctrl.name,
                    ctrl.CLI.sendline( "scr:list | grep -v ACTIVE" ) ) )
            main.log.error( "Failed to start ONOS, stopping test" )
            main.cleanAndExit()

        topology = utilities.retry( main.Cluster.active( 0 ).CLI.checkStatus,
                                    main.FALSE,
                                    kwargs={ 'numoswitch': switches,
                                             'numolink': links,
                                             'numoctrl': expNodes },
                                    attempts=10,
                                    sleep=12 )
        utilities.assert_equals( expect=main.TRUE, actual=topology,
                                 onpass="ONOS Instance down successful",
                                 onfail="Failed to turn off ONOS Instance" )
        ready = utilities.retry( main.Cluster.active( 0 ).CLI.summary,
                                 main.FALSE,
                                 attempts=10,
                                 sleep=12 )
        if ready:
            ready = main.TRUE
        utilities.assert_equals( expect=main.TRUE, actual=ready,
                                 onpass="ONOS summary command succeded",
                                 onfail="ONOS summary command failed" )
        if not ready:
            main.log.error( "ONOS startup failed!" )
            main.cleanAndExit()

    @staticmethod
    def addHostCfg( main ):
        """
        Adds Host Configuration to ONOS
        Updates expected state of the network ( pingChart )
        """
        import json
        hostCfg = {}
        with open( main.configPath + "/json/extra.json" ) as template:
            hostCfg = json.load( template )
        main.pingChart[ 'ip' ][ 'hosts' ] += [ 'in1' ]
        main.step( "Pushing new configuration" )
        mac, cfg = hostCfg[ 'hosts' ].popitem()
        main.Cluster.active( 0 ).REST.setNetCfg( cfg[ 'basic' ],
                                                 subjectClass="hosts",
                                                 subjectKey=urllib.quote( mac,
                                                                          safe='' ),
                                                 configKey="basic" )
        main.pingChart[ 'ip' ][ 'hosts' ] += [ 'out1' ]
        main.step( "Pushing new configuration" )
        mac, cfg = hostCfg[ 'hosts' ].popitem()
        main.Cluster.active( 0 ).REST.setNetCfg( cfg[ 'basic' ],
                                                 subjectClass="hosts",
                                                 subjectKey=urllib.quote( mac,
                                                                          safe='' ),
                                                 configKey="basic" )
        main.pingChart.update( { 'vlan1': { "expect": "True",
                                            "hosts": [ "olt1", "vsg1" ] } } )
        main.pingChart[ 'vlan5' ][ 'expect' ] = 0
        main.pingChart[ 'vlan10' ][ 'expect' ] = 0
        ports = "[%s,%s]" % ( 5, 6 )
        cfg = '{"of:0000000000000001":[{"vlan":1,"ports":%s,"name":"OLT 1"}]}' % ports
        main.Cluster.active( 0 ).REST.setNetCfg( json.loads( cfg ),
                                                 subjectClass="apps",
                                                 subjectKey="org.onosproject.segmentrouting",
                                                 configKey="xconnect" )

    @staticmethod
    def delHostCfg( main ):
        """
        Removest Host Configuration from ONOS
        Updates expected state of the network ( pingChart )
        """
        import json
        hostCfg = {}
        with open( main.configPath + "/json/extra.json" ) as template:
            hostCfg = json.load( template )
        main.step( "Removing host configuration" )
        main.pingChart[ 'ip' ][ 'expect' ] = 0
        mac, cfg = hostCfg[ 'hosts' ].popitem()
        main.Cluster.active( 0 ).REST.removeNetCfg( subjectClass="hosts",
                                                    subjectKey=urllib.quote(
                                                            mac,
                                                            safe='' ),
                                                    configKey="basic" )
        main.step( "Removing configuration" )
        main.pingChart[ 'ip' ][ 'expect' ] = 0
        mac, cfg = hostCfg[ 'hosts' ].popitem()
        main.Cluster.active( 0 ).REST.removeNetCfg( subjectClass="hosts",
                                                    subjectKey=urllib.quote(
                                                            mac,
                                                            safe='' ),
                                                    configKey="basic" )
        main.step( "Removing vlan configuration" )
        main.pingChart[ 'vlan1' ][ 'expect' ] = 0
        main.Cluster.active( 0 ).REST.removeNetCfg( subjectClass="apps",
                                                    subjectKey="org.onosproject.segmentrouting",
                                                    configKey="xconnect" )
