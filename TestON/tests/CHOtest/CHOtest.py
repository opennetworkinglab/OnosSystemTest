import sys
import os
import re
import time
import json
import itertools


class CHOtest:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        Startup sequence:
        apply cell <name>
        git pull
        mvn clean install
        onos-package
        onos-verify-cell
        onos-uninstall
        onos-install
        onos-start-cli
        """
        import time

        global intentState
        main.threadID = 0
        main.numCtrls = main.params[ 'CTRL' ][ 'numCtrl' ]
        git_pull = main.params[ 'GIT' ][ 'autoPull' ]
        git_branch = main.params[ 'GIT' ][ 'branch' ]
        karafTimeout = main.params['CTRL']['karafCliTimeout']
        main.checkIntentsDelay = int( main.params['timers']['CheckIntentDelay'] )
        main.failSwitch = main.params['TEST']['pauseTest']
        main.emailOnStop = main.params['TEST']['email']
        main.intentCheck = int( main.params['TEST']['intentChecks'] )
        main.linkCheck = int( main.params['TEST']['linkChecks'] )
        main.topoCheck = int( main.params['TEST']['topoChecks'] )
        main.numPings = int( main.params['TEST']['numPings'] )
        main.pingSleep = int( main.params['timers']['pingSleep'] )
        main.topoCheckDelay = int( main.params['timers']['topoCheckDelay'] )
        main.pingTimeout = int( main.params['timers']['pingTimeout'] )
        main.remHostDelay = int( main.params['timers']['remHostDelay'] )
        main.remDevDelay = int( main.params['timers']['remDevDelay'] )
        main.newTopo = ""
        main.CLIs = []

        main.failSwitch = True if main.failSwitch == "on" else False
        main.emailOnStop = True if main.emailOnStop == "on" else False

        for i in range( 1, int(main.numCtrls) + 1 ):
            main.CLIs.append( getattr( main, 'ONOScli' + str( i ) ) )

        main.case( "Set up test environment" )
        main.log.report( "Set up test environment" )
        main.log.report( "_______________________" )

        main.step( "Apply Cell environment for ONOS" )
        if ( main.onoscell ):
            cellName = main.onoscell
            cell_result = main.ONOSbench.setCell( cellName )
            utilities.assert_equals( expect=main.TRUE, actual=cell_result,
                                 onpass="Test step PASS",
                                 onfail="Test step FAIL" )
        else:
            main.log.error( "Please provide onoscell option at TestON CLI to run CHO tests" )
            main.log.error( "Example: ~/TestON/bin/cli.py run OnosCHO onoscell <cellName>" )
            main.cleanup()
            main.exit()

        main.step( "Git checkout and pull " + git_branch )
        if git_pull == 'on':
            checkout_result = main.ONOSbench.gitCheckout( git_branch )
            pull_result = main.ONOSbench.gitPull()
            cp_result = ( checkout_result and pull_result )
        else:
            checkout_result = main.TRUE
            pull_result = main.TRUE
            main.log.info( "Skipped git checkout and pull" )
            cp_result = ( checkout_result and pull_result )
        utilities.assert_equals( expect=main.TRUE, actual=cp_result,
                                 onpass="Test step PASS",
                                 onfail="Test step FAIL" )

        main.step( "mvn clean & install" )
        if git_pull == 'on':
            mvn_result = main.ONOSbench.cleanInstall()
            utilities.assert_equals( expect=main.TRUE, actual=mvn_result,
                                 onpass="Test step PASS",
                                 onfail="Test step FAIL" )
        else:
            mvn_result = main.TRUE
            main.log.info("Skipped mvn clean install as git pull is disabled in params file")

        main.ONOSbench.getVersion( report=True )

        main.step( "Create ONOS package" )
        packageResult = main.ONOSbench.onosPackage()
        utilities.assert_equals( expect=main.TRUE, actual=packageResult,
                                 onpass="Test step PASS",
                                 onfail="Test step FAIL" )

        main.step( "Uninstall ONOS package on all Nodes" )
        uninstallResult = main.TRUE
        for i in range( int( main.numCtrls ) ):
            main.log.info( "Uninstalling package on ONOS Node IP: " + main.onosIPs[i] )
            u_result = main.ONOSbench.onosUninstall( main.onosIPs[i] )
            utilities.assert_equals( expect=main.TRUE, actual=u_result,
                                     onpass="Test step PASS",
                                     onfail="Test step FAIL" )
            uninstallResult = ( uninstallResult and u_result )

        main.step( "Install ONOS package on all Nodes" )
        installResult = main.TRUE
        for i in range( int( main.numCtrls ) ):
            main.log.info( "Installing package on ONOS Node IP: " + main.onosIPs[i] )
            i_result = main.ONOSbench.onosInstall( node=main.onosIPs[i] )
            utilities.assert_equals( expect=main.TRUE, actual=i_result,
                                     onpass="Test step PASS",
                                     onfail="Test step FAIL" )
            installResult = ( installResult and i_result )

        main.step( "Verify ONOS nodes UP status" )
        statusResult = main.TRUE
        for i in range( int( main.numCtrls ) ):
            main.log.info( "ONOS Node " + main.onosIPs[i] + " status:" )
            onos_status = main.ONOSbench.onosStatus( node=main.onosIPs[i] )
            utilities.assert_equals( expect=main.TRUE, actual=onos_status,
                                     onpass="Test step PASS",
                                     onfail="Test step FAIL" )
            statusResult = ( statusResult and onos_status )

        main.step( "Start ONOS CLI on all nodes" )
        cliResult = main.TRUE
        main.log.step(" Start ONOS cli using thread ")
        startCliResult  = main.TRUE
        pool = []
        time1 = time.time()
        for i in range( int( main.numCtrls) ):
            t = main.Thread( target=main.CLIs[i].startOnosCli,
                             threadID=main.threadID,
                             name="startOnosCli",
                             args=[ main.onosIPs[i], karafTimeout ] )
            pool.append(t)
            t.start()
            main.threadID = main.threadID + 1
        for t in pool:
            t.join()
            startCliResult = startCliResult and t.result
        time2 = time.time()

        if not startCliResult:
                main.log.info("ONOS CLI did not start up properly")
                main.cleanup()
                main.exit()
        else:
            main.log.info("Successful CLI startup")
            startCliResult = main.TRUE

        main.step( "Set IPv6 cfg parameters for Neighbor Discovery" )
        cfgResult1 = main.CLIs[0].setCfg( "org.onosproject.proxyarp.ProxyArp", "ipv6NeighborDiscovery", "true" )
        cfgResult2 = main.CLIs[0].setCfg( "org.onosproject.provider.host.impl.HostLocationProvider", "ipv6NeighborDiscovery", "true" )
        cfgResult = cfgResult1 and cfgResult2
        utilities.assert_equals( expect=main.TRUE, actual=cfgResult,
                                 onpass="ipv6NeighborDiscovery cfg is set to true",
                                 onfail="Failed to cfg set ipv6NeighborDiscovery" )

        case1Result = installResult and uninstallResult and statusResult and startCliResult and cfgResult
        main.log.info("Time for connecting to CLI: %2f seconds" %(time2-time1))
        utilities.assert_equals( expect=main.TRUE, actual=case1Result,
                                 onpass="Set up test environment PASS",
                                 onfail="Set up test environment FAIL" )

    def CASE20( self, main ):
        """
        This test script Loads a new Topology (Att) on CHO setup and balances all switches
        """
        import re
        import time
        import copy

        main.prefix = 0

        main.numMNswitches = int ( main.params[ 'TOPO1' ][ 'numSwitches' ] )
        main.numMNlinks = int ( main.params[ 'TOPO1' ][ 'numLinks' ] )
        main.numMNhosts = int ( main.params[ 'TOPO1' ][ 'numHosts' ] )
        main.log.report(
            "Load Att topology and Balance all Mininet switches across controllers" )
        main.log.report(
            "________________________________________________________________________" )
        main.case(
            "Assign and Balance all Mininet switches across controllers" )

        main.step( "Start Mininet with Att topology" )
        main.newTopo = main.params['TOPO1']['topo']
        mininetDir = main.Mininet1.home + "/custom/"
        topoPath = main.testDir + "/" + main.TEST  + "/Dependencies/" + main.newTopo
        main.ONOSbench.secureCopy(main.Mininet1.user_name, main.Mininet1.ip_address, topoPath, mininetDir, direction="to")
        topoPath = mininetDir + main.newTopo
        startStatus = main.Mininet1.startNet(topoFile = topoPath)

        main.step( "Assign switches to controllers" )
        for i in range( 1, ( main.numMNswitches + 1 ) ):  # 1 to ( num of switches +1 )
            main.Mininet1.assignSwController(
                sw="s" + str( i ),
                ip=main.onosIPs )

        switch_mastership = main.TRUE
        for i in range( 1, ( main.numMNswitches + 1 ) ):
            response = main.Mininet1.getSwController( "s" + str( i ) )
            print( "Response is " + str( response ) )
            if re.search( "tcp:" + main.onosIPs[0], response ):
                switch_mastership = switch_mastership and main.TRUE
            else:
                switch_mastership = main.FALSE

        if switch_mastership == main.TRUE:
            main.log.report( "Controller assignment successfull" )
        else:
            main.log.report( "Controller assignment failed" )

        time.sleep(30) # waiting here to make sure topology converges across all nodes

        main.step( "Balance devices across controllers" )
        balanceResult = main.ONOScli1.balanceMasters()
        # giving some breathing time for ONOS to complete re-balance
        time.sleep( 5 )

        topology_output = main.ONOScli1.topology()
        topology_result = main.ONOSbench.getTopology( topology_output )
        case2Result = ( switch_mastership and startStatus )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case2Result,
            onpass="Starting new Att topology test PASS",
            onfail="Starting new Att topology test FAIL" )

    def CASE21( self, main ):
        """
        This test script Loads a new Topology (Chordal) on CHO setup and balances all switches
        """
        import re
        import time
        import copy

        main.prefix = 1

        main.newTopo = main.params['TOPO2']['topo']
        main.numMNswitches = int ( main.params[ 'TOPO2' ][ 'numSwitches' ] )
        main.numMNlinks = int ( main.params[ 'TOPO2' ][ 'numLinks' ] )
        main.numMNhosts = int ( main.params[ 'TOPO2' ][ 'numHosts' ] )
        main.log.report(
            "Load Chordal topology and Balance all Mininet switches across controllers" )
        main.log.report(
            "________________________________________________________________________" )
        main.case(
            "Assign and Balance all Mininet switches across controllers" )

        main.step("Start Mininet with Chordal topology")
        mininetDir = main.Mininet1.home + "/custom/"
        topoPath = main.testDir + "/" + main.TEST  + "/Dependencies/" + main.newTopo
        main.ONOSbench.secureCopy(main.Mininet1.user_name, main.Mininet1.ip_address, topoPath, mininetDir, direction="to")
        topoPath = mininetDir + main.newTopo
        startStatus = main.Mininet1.startNet(topoFile = topoPath)

        main.step( "Assign switches to controllers" )

        for i in range( 1, ( main.numMNswitches + 1 ) ):  # 1 to ( num of switches +1 )
            main.Mininet1.assignSwController(
                sw="s" + str( i ),
                ip=main.onosIPs )

        switch_mastership = main.TRUE
        for i in range( 1, ( main.numMNswitches + 1 ) ):
            response = main.Mininet1.getSwController( "s" + str( i ) )
            print( "Response is " + str( response ) )
            if re.search( "tcp:" + main.onosIPs[0], response ):
                switch_mastership = switch_mastership and main.TRUE
            else:
                switch_mastership = main.FALSE

        if switch_mastership == main.TRUE:
            main.log.report( "Controller assignment successfull" )
        else:
            main.log.report( "Controller assignment failed" )

        main.step( "Balance devices across controllers" )
        balanceResult = main.ONOScli1.balanceMasters()
        # giving some breathing time for ONOS to complete re-balance
        time.sleep( 5 )

        caseResult = switch_mastership
        time.sleep(30)
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="Starting new Chordal topology test PASS",
            onfail="Starting new Chordal topology test FAIL" )

    def CASE22( self, main ):
        """
        This test script Loads a new Topology (Spine) on CHO setup and balances all switches
        """
        import re
        import time
        import copy

        main.prefix = 2

        main.newTopo = main.params['TOPO3']['topo']
        main.numMNswitches = int ( main.params[ 'TOPO3' ][ 'numSwitches' ] )
        main.numMNlinks = int ( main.params[ 'TOPO3' ][ 'numLinks' ] )
        main.numMNhosts = int ( main.params[ 'TOPO3' ][ 'numHosts' ] )
        main.pingTimeout = 600

        main.log.report(
            "Load Spine and Leaf topology and Balance all Mininet switches across controllers" )
        main.log.report(
            "________________________________________________________________________" )
        main.case( "Assign and Balance all Mininet switches across controllers" )

        main.step("Start Mininet with Spine topology")
        mininetDir = main.Mininet1.home + "/custom/"
        topoPath = main.testDir + "/" + main.TEST  + "/Dependencies/" + main.newTopo
        main.ONOSbench.secureCopy(main.Mininet1.user_name, main.Mininet1.ip_address, topoPath, mininetDir, direction="to")
        topoPath = mininetDir + main.newTopo
        startStatus = main.Mininet1.startNet(topoFile = topoPath)

        for i in range( 1, ( main.numMNswitches + 1 ) ):  # 1 to ( num of switches +1 )
            main.Mininet1.assignSwController(
                sw="s" + str( i ),
                ip=main.onosIPs )

        switch_mastership = main.TRUE
        for i in range( 1, ( main.numMNswitches + 1 ) ):
            response = main.Mininet1.getSwController( "s" + str( i ) )
            print( "Response is " + str( response ) )
            if re.search( "tcp:" + main.onosIPs[0], response ):
                switch_mastership = switch_mastership and main.TRUE
            else:
                switch_mastership = main.FALSE

        if switch_mastership == main.TRUE:
            main.log.report( "Controller assignment successfull" )
        else:
            main.log.report( "Controller assignment failed" )
        time.sleep( 5 )

        main.step( "Balance devices across controllers" )
        for i in range( int( main.numCtrls ) ):
            balanceResult = main.ONOScli1.balanceMasters()
            # giving some breathing time for ONOS to complete re-balance
            time.sleep( 3 )

        caseResult = switch_mastership
        time.sleep(60)
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="Starting new Spine topology test PASS",
            onfail="Starting new Spine topology test FAIL" )

    def CASE3( self, main ):
        """
        This Test case will be extended to collect and store more data related
        ONOS state.
        """
        import re
        import copy
        main.deviceDPIDs = []
        main.hostMACs = []
        main.deviceLinks = []
        main.deviceActiveLinksCount = []
        main.devicePortsEnabledCount = []

        main.log.report(
            "Collect and Store topology details from ONOS before running any Tests" )
        main.log.report(
            "____________________________________________________________________" )
        main.case( "Collect and Store Topology Details from ONOS" )
        main.step( "Collect and store current number of switches and links" )
        topology_output = main.ONOScli1.topology()
        topology_result = main.ONOSbench.getTopology( topology_output )
        numOnosDevices = topology_result[ 'devices' ]
        numOnosLinks = topology_result[ 'links' ]
        topoResult = main.TRUE

        for check in range(main.topoCheck):
            if ( ( main.numMNswitches == int(numOnosDevices) ) and ( main.numMNlinks == int(numOnosLinks) ) ):
                main.step( "Store Device DPIDs" )
                for i in range( 1, (main.numMNswitches+1) ):
                    main.deviceDPIDs.append( "of:00000000000000" + format( i, "02x" ) )
                print "Device DPIDs in Store: \n", str( main.deviceDPIDs )

                main.step( "Store Host MACs" )
                for i in range( 1, ( main.numMNhosts + 1 ) ):
                    main.hostMACs.append( "00:00:00:00:00:" + format( i, '02x' ) + "/-1" )
                print "Host MACs in Store: \n", str( main.hostMACs )
                main.MACsDict = {}
                print "Creating dictionary of DPID and HostMacs"
                for i in range(len(main.hostMACs)):
                    main.MACsDict[main.deviceDPIDs[i]] = main.hostMACs[i].split('/')[0]
                print main.MACsDict
                main.step( "Collect and store all Devices Links" )
                linksResult = main.ONOScli1.links( jsonFormat=False )
                ansi_escape = re.compile( r'\x1b[^m]*m' )
                linksResult = ansi_escape.sub( '', linksResult )
                linksResult = linksResult.replace( " links", "" ).replace( "\r\r", "" )
                linksResult = linksResult.splitlines()
                main.deviceLinks = copy.copy( linksResult )
                print "Device Links Stored: \n", str( main.deviceLinks )
                # this will be asserted to check with the params provided count of
                # links
                print "Length of Links Store", len( main.deviceLinks )

                main.step( "Collect and store each Device ports enabled Count" )
                time1 = time.time()
                for i in xrange(1,(main.numMNswitches + 1), int( main.numCtrls ) ):
                    pool = []
                    for cli in main.CLIs:
                        if i >=  main.numMNswitches + 1:
                            break
                        dpid = "of:00000000000000" + format( i, "02x" )
                        t = main.Thread(target = cli.getDevicePortsEnabledCount,threadID = main.threadID, name = "getDevicePortsEnabledCount",args = [dpid])
                        t.start()
                        pool.append(t)
                        i = i + 1
                        main.threadID = main.threadID + 1
                    for thread in pool:
                        thread.join()
                        portResult = thread.result
                        main.devicePortsEnabledCount.append( portResult )
                print "Device Enabled Port Counts Stored: \n", str( main.devicePortsEnabledCount )
                time2 = time.time()
                main.log.info("Time for counting enabled ports of the switches: %2f seconds" %(time2-time1))

                main.step( "Collect and store each Device active links Count" )
                time1 = time.time()

                for i in xrange( 1,( main.numMNswitches + 1 ), int( main.numCtrls) ):
                    pool = []
                    for cli in main.CLIs:
                        if i >=  main.numMNswitches + 1:
                            break
                        dpid = "of:00000000000000" + format( i, "02x" )
                        t = main.Thread( target = cli.getDeviceLinksActiveCount,
                                         threadID = main.threadID,
                                         name = "getDevicePortsEnabledCount",
                                         args = [dpid])
                        t.start()
                        pool.append(t)
                        i = i + 1
                        main.threadID = main.threadID + 1
                    for thread in pool:
                        thread.join()
                        linkCountResult = thread.result
                        main.deviceActiveLinksCount.append( linkCountResult )
                print "Device Active Links Count Stored: \n", str( main.deviceActiveLinksCount )
                time2 = time.time()
                main.log.info("Time for counting all enabled links of the switches: %2f seconds" %(time2-time1))

                # Exit out of the topo check loop
                break

            else:
                main.log.info("Devices (expected): %s, Links (expected): %s" %
                        ( str( main.numMNswitches ), str( main.numMNlinks ) ) )
                main.log.info("Devices (actual): %s, Links (actual): %s" %
                        ( numOnosDevices , numOnosLinks ) )
                main.log.info("Topology does not match, trying again...")
                topoResult = main.FALSE
                time.sleep(main.topoCheckDelay)

        # just returning TRUE for now as this one just collects data
        case3Result = topoResult
        utilities.assert_equals( expect=main.TRUE, actual=case3Result,
                                 onpass="Saving ONOS topology data test PASS",
                                 onfail="Saving ONOS topology data test FAIL" )



    def CASE200( self, main ):

        import time
        main.log.report( "Clean up ONOS" )
        main.log.case( "Stop topology and remove hosts and devices" )

        main.step( "Stop Topology" )
        stopStatus = main.Mininet1.stopNet()
        utilities.assert_equals( expect=main.TRUE, actual=stopStatus,
                                 onpass="Stopped mininet",
                                 onfail="Failed to stop mininet" )


        main.log.info( "Constructing host id list" )
        hosts = []
        for i in range( main.numMNhosts ):
            hosts.append( "h" + str(i+1) )

        main.step( "Getting host ids" )
        hostList = main.CLIs[0].getHostsId( hosts )
        hostIdResult = True if hostList else False
        utilities.assert_equals( expect=True, actual=hostIdResult,
                                 onpass="Successfully obtained the host ids.",
                                 onfail="Failed to obtain the host ids" )

        main.step( "Removing hosts" )
        hostResult = main.CLIs[0].removeHost( hostList )
        utilities.assert_equals( expect=main.TRUE, actual=hostResult,
                                 onpass="Successfully removed hosts",
                                 onfail="Failed remove hosts" )

        time.sleep( main.remHostDelay )

        main.log.info( "Constructing device uri list" )
        deviceList = []
        for i in range( main.numMNswitches ):
            deviceList.append( "of:00000000000000" + format( i+1, "02x" ) )

        main.step( "Removing devices" )
        deviceResult = main.CLIs[0].removeDevice( deviceList )
        utilities.assert_equals( expect=main.TRUE, actual=deviceResult,
                                 onpass="Successfully removed devices",
                                 onfail="Failed remove devices" )

        time.sleep( main.remDevDelay )

        main.log.info( "Summary\n{}".format( main.CLIs[0].summary( jsonFormat=False ) ) )


    def CASE40( self, main ):
        """
        Verify Reactive forwarding
        """
        import time
        main.log.report( "Verify Reactive forwarding" )
        main.log.report( "______________________________________________" )
        main.case( "Enable Reactive forwarding, verify pingall, and disable reactive forwarding" )

        main.step( "Enable Reactive forwarding" )
        appResult = main.CLIs[0].activateApp( "org.onosproject.fwd" )
        utilities.assert_equals( expect=main.TRUE, actual=appResult,
                                 onpass="Successfully install fwd app",
                                 onfail="Failed to install fwd app" )


        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else:
                break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )

        if not pingResult:
            main.stop()

        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="Reactive Mode IPv4 Pingall test PASS",
                                 onfail="Reactive Mode IPv4 Pingall test FAIL" )

        main.step( "Disable Reactive forwarding" )
        appResult =  main.CLIs[0].deactivateApp( "org.onosproject.fwd" )
        utilities.assert_equals( expect=main.TRUE, actual=appResult,
                                 onpass="Successfully deactivated fwd app",
                                 onfail="Failed to deactivate fwd app" )

    def CASE41( self, main ):
        """
        Verify Reactive forwarding (Chordal Topology)
        """
        import re
        import copy
        import time
        main.log.report( "Verify Reactive forwarding (Chordal Topology)" )
        main.log.report( "______________________________________________" )
        main.case( "Enable Reactive forwarding and Verify ping all" )
        main.step( "Enable Reactive forwarding" )
        installResult = main.TRUE
        # Activate fwd app
        appResults = main.CLIs[0].activateApp( "org.onosproject.fwd" )

        appCheck = main.TRUE
        pool = []
        for cli in main.CLIs:
            t = main.Thread( target=cli.appToIDCheck,
                             name="appToIDCheck-" + str( i ),
                             args=[] )
            pool.append( t )
            t.start()
        for t in pool:
            t.join()
            appCheck = appCheck and t.result
        utilities.assert_equals( expect=main.TRUE, actual=appCheck,
                                 onpass="App Ids seem to be correct",
                                 onfail="Something is wrong with app Ids" )
        if appCheck != main.TRUE:
            main.log.warn( main.CLIs[0].apps() )
            main.log.warn( main.CLIs[0].appIDs() )

        time.sleep( 10 )

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )

        if pingResult == main.TRUE:
            main.log.report( "IPv4 Pingall Test in Reactive mode successful" )
        else:
            main.log.report( "IPv4 Pingall Test in Reactive mode failed" )

        caseResult =  appCheck and pingResult
        utilities.assert_equals( expect=main.TRUE, actual=caseResult,
                                 onpass="Reactive Mode IPv4 Pingall test PASS",
                                 onfail="Reactive Mode IPv4 Pingall test FAIL" )

    def CASE42( self, main ):
        """
        Verify Reactive forwarding (Spine Topology)
        """
        import re
        import copy
        import time
        main.log.report( "Verify Reactive forwarding (Spine Topology)" )
        main.log.report( "______________________________________________" )
        main.case( "Enable Reactive forwarding and Verify ping all" )
        main.step( "Enable Reactive forwarding" )
        installResult = main.TRUE
        # Activate fwd app
        appResults = main.CLIs[0].activateApp( "org.onosproject.fwd" )

        appCheck = main.TRUE
        pool = []
        for cli in main.CLIs:
            t = main.Thread( target=cli.appToIDCheck,
                             name="appToIDCheck-" + str( i ),
                             args=[] )
            pool.append( t )
            t.start()
        for t in pool:
            t.join()
            appCheck = appCheck and t.result
        utilities.assert_equals( expect=main.TRUE, actual=appCheck,
                                 onpass="App Ids seem to be correct",
                                 onfail="Something is wrong with app Ids" )
        if appCheck != main.TRUE:
            main.log.warn( main.CLIs[0].apps() )
            main.log.warn( main.CLIs[0].appIDs() )

        time.sleep( 10 )

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )

        if pingResult == main.TRUE:
            main.log.report( "IPv4 Pingall Test in Reactive mode successful" )
        else:
            main.log.report( "IPv4 Pingall Test in Reactive mode failed" )

        caseResult =  appCheck and pingResult
        utilities.assert_equals( expect=main.TRUE, actual=caseResult,
                                 onpass="Reactive Mode IPv4 Pingall test PASS",
                                 onfail="Reactive Mode IPv4 Pingall test FAIL" )

    def CASE47( self, main ):
        """
        Verify reactive forwarding in ATT topology, use a different ping method than CASE40
        """
        import time
        main.log.report( "Verify Reactive forwarding (ATT Topology) " )
        main.log.report( "______________________________________________" )
        main.case( "Enable Reactive forwarding, verify ping, and disable reactive forwarding" )

        main.step( "Enable Reactive forwarding" )
        appResult = main.CLIs[0].activateApp( "org.onosproject.fwd" )
        utilities.assert_equals( expect=main.TRUE, actual=appResult,
                                 onpass="Successfully install fwd app",
                                 onfail="Failed to install fwd app" )

        numHosts = int( main.params['TOPO1']['numHosts'] )

        for i in range(numHosts):
            src = "h1"
            dest = "h" + str(i+1)
            main.Mininet1.handle.sendline( src + " ping " + dest + " -c 3 -i 1 -W 1" )
            main.Mininet1.handle.expect( "mininet>" )
            main.log.info( main.Mininet1.handle.before )

        hosts = main.CLIs[0].hosts( jsonFormat=False )

        main.log.info( hosts )

        main.step( "Disable Reactive forwarding" )
        appResult =  main.CLIs[0].deactivateApp( "org.onosproject.fwd" )
        utilities.assert_equals( expect=main.TRUE, actual=appResult,
                                 onpass="Successfully deactivated fwd app",
                                 onfail="Failed to deactivate fwd app" )

    def CASE48( self, main ):
        """
        Verify reactive forwarding in Chordal topology, use a different ping method than CASE41
        """
        import time
        main.log.report( "Verify Reactive forwarding (Chordal Topology) " )
        main.log.report( "______________________________________________" )
        main.case( "Enable Reactive forwarding, verify ping, and disable reactive forwarding" )

        main.step( "Enable Reactive forwarding" )
        appResult = main.CLIs[0].activateApp( "org.onosproject.fwd" )
        utilities.assert_equals( expect=main.TRUE, actual=appResult,
                                 onpass="Successfully install fwd app",
                                 onfail="Failed to install fwd app" )

        numHosts = int( main.params['TOPO2']['numHosts'] )

        for i in range(numHosts):
            src = "h1"
            dest = "h" + str(i+1)
            main.Mininet1.handle.sendline( src + " ping " + dest + " -c 3 -i 1 -W 1" )
            main.Mininet1.handle.expect( "mininet>" )
            main.log.info( main.Mininet1.handle.before )

        hosts = main.CLIs[0].hosts( jsonFormat=False )

        main.log.info( hosts )

        main.step( "Disable Reactive forwarding" )
        appResult =  main.CLIs[0].deactivateApp( "org.onosproject.fwd" )
        utilities.assert_equals( expect=main.TRUE, actual=appResult,
                                 onpass="Successfully deactivated fwd app",
                                 onfail="Failed to deactivate fwd app" )

    def CASE49( self, main ):
        """
        Verify reactive forwarding in Spine-leaf topology, use a different ping method than CASE42
        """
        import time
        main.log.report( "Verify Reactive forwarding (Spine-leaf Topology) " )
        main.log.report( "______________________________________________" )
        main.case( "Enable Reactive forwarding, verify ping, and disable reactive forwarding" )

        main.step( "Enable Reactive forwarding" )
        appResult = main.CLIs[0].activateApp( "org.onosproject.fwd" )
        utilities.assert_equals( expect=main.TRUE, actual=appResult,
                                 onpass="Successfully install fwd app",
                                 onfail="Failed to install fwd app" )

        numHosts = int( main.params['TOPO3']['numHosts'] )

        for i in range(11, numHosts+10):
            src = "h11"
            dest = "h" + str(i+1)
            main.Mininet1.handle.sendline( src + " ping " + dest + " -c 3 -i 1 -W 1" )
            main.Mininet1.handle.expect( "mininet>" )
            main.log.info( main.Mininet1.handle.before )

        hosts = main.CLIs[0].hosts( jsonFormat=False )

        main.log.info( hosts )

        main.step( "Disable Reactive forwarding" )
        appResult =  main.CLIs[0].deactivateApp( "org.onosproject.fwd" )
        utilities.assert_equals( expect=main.TRUE, actual=appResult,
                                 onpass="Successfully deactivated fwd app",
                                 onfail="Failed to deactivate fwd app" )

    def CASE140( self, main ):
        """
        Verify IPv6 Reactive forwarding (Att Topology)
        """
        import re
        import copy
        import time
        main.log.report( "Verify IPv6 Reactive forwarding (Att Topology)" )
        main.log.report( "______________________________________________" )
        main.case( "Enable IPv6 Reactive forwarding and Verify ping all" )
        hostList = [ ('h'+ str(x + 1)) for x in range (main.numMNhosts) ]

        main.step( "Set IPv6 cfg parameters for Reactive forwarding" )
        cfgResult1 = main.CLIs[0].setCfg( "org.onosproject.fwd.ReactiveForwarding", "ipv6Forwarding", "true" )
        cfgResult2 = main.CLIs[0].setCfg( "org.onosproject.fwd.ReactiveForwarding", "matchIpv6Address", "true" )
        cfgResult = cfgResult1 and cfgResult2
        utilities.assert_equals( expect=main.TRUE, actual=cfgResult,
                                 onpass="Reactive mode ipv6Fowarding cfg is set to true",
                                 onfail="Failed to cfg set Reactive mode ipv6Fowarding" )

        main.step( "Verify IPv6 Pingall" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout)
        if not pingResult:
            main.log.warn("First pingall failed. Trying again..")
            pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for IPv6 Ping All: " +
            str( timeDiff ) +
            " seconds" )

        if pingResult == main.TRUE:
            main.log.report( "IPv6 Pingall Test in Reactive mode successful" )
        else:
            main.log.report( "IPv6 Pingall Test in Reactive mode failed" )


        caseResult =  appCheck and pingResult
        utilities.assert_equals( expect=main.TRUE, actual=caseResult,
                                 onpass="Reactive Mode IPv6 Pingall test PASS",
                                 onfail="Reactive Mode IPv6 Pingall test FAIL" )

    def CASE141( self, main ):
        """
        Verify IPv6 Reactive forwarding (Chordal Topology)
        """
        import re
        import copy
        import time
        main.log.report( "Verify IPv6 Reactive forwarding (Chordal Topology)" )
        main.log.report( "______________________________________________" )
        main.case( "Enable IPv6 Reactive forwarding and Verify ping all" )
        hostList = [ ('h'+ str(x + 1)) for x in range (main.numMNhosts) ]

        main.step( "Set IPv6 cfg parameters for Reactive forwarding" )
        cfgResult1 = main.CLIs[0].setCfg( "org.onosproject.fwd.ReactiveForwarding", "ipv6Forwarding", "true" )
        cfgResult2 = main.CLIs[0].setCfg( "org.onosproject.fwd.ReactiveForwarding", "matchIpv6Address", "true" )
        cfgResult = cfgResult1 and cfgResult2
        utilities.assert_equals( expect=main.TRUE, actual=cfgResult,
                                 onpass="Reactive mode ipv6Fowarding cfg is set to true",
                                 onfail="Failed to cfg set Reactive mode ipv6Fowarding" )

        main.step( "Verify IPv6 Pingall" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout)
        if not pingResult:
            main.log.warn("First pingall failed. Trying again..")
            pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for IPv6 Ping All: " +
            str( timeDiff ) +
            " seconds" )

        if pingResult == main.TRUE:
            main.log.report( "IPv6 Pingall Test in Reactive mode successful" )
        else:
            main.log.report( "IPv6 Pingall Test in Reactive mode failed" )

        main.step( "Disable Reactive forwarding" )

        main.log.info( "Uninstall reactive forwarding app" )
        appCheck = main.TRUE
        appResults = appResults and main.CLIs[0].deactivateApp( "org.onosproject.fwd" )
        pool = []
        for cli in main.CLIs:
            t = main.Thread( target=cli.appToIDCheck,
                             name="appToIDCheck-" + str( i ),
                             args=[] )
            pool.append( t )
            t.start()

        for t in pool:
            t.join()
            appCheck = appCheck and t.result
        utilities.assert_equals( expect=main.TRUE, actual=appCheck,
                                 onpass="App Ids seem to be correct",
                                 onfail="Something is wrong with app Ids" )
        if appCheck != main.TRUE:
            main.log.warn( main.CLIs[0].apps() )
            main.log.warn( main.CLIs[0].appIDs() )

        # Waiting for reative flows to be cleared.
        time.sleep( 30 )
        caseResult =  appCheck and cfgResult and pingResult
        utilities.assert_equals( expect=main.TRUE, actual=caseResult,
                                 onpass="Reactive Mode IPv6 Pingall test PASS",
                                 onfail="Reactive Mode IPv6 Pingall test FAIL" )

    def CASE142( self, main ):
        """
        Verify IPv6 Reactive forwarding (Spine Topology)
        """
        import re
        import copy
        import time
        main.log.report( "Verify IPv6 Reactive forwarding (Spine Topology)" )
        main.log.report( "______________________________________________" )
        main.case( "Enable IPv6 Reactive forwarding and Verify ping all" )
        # Spine topology do not have hosts h1-h10
        hostList = [ ('h'+ str(x + 11)) for x in range (main.numMNhosts) ]
        main.step( "Set IPv6 cfg parameters for Reactive forwarding" )
        cfgResult1 = main.CLIs[0].setCfg( "org.onosproject.fwd.ReactiveForwarding", "ipv6Forwarding", "true" )
        cfgResult2 = main.CLIs[0].setCfg( "org.onosproject.fwd.ReactiveForwarding", "matchIpv6Address", "true" )
        cfgResult = cfgResult1 and cfgResult2
        utilities.assert_equals( expect=main.TRUE, actual=cfgResult,
                                 onpass="Reactive mode ipv6Fowarding cfg is set to true",
                                 onfail="Failed to cfg set Reactive mode ipv6Fowarding" )

        main.step( "Verify IPv6 Pingall" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout)
        if not pingResult:
            main.log.warn("First pingall failed. Trying again...")
            pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for IPv6 Ping All: " +
            str( timeDiff ) +
            " seconds" )

        if pingResult == main.TRUE:
            main.log.report( "IPv6 Pingall Test in Reactive mode successful" )
        else:
            main.log.report( "IPv6 Pingall Test in Reactive mode failed" )

        main.step( "Disable Reactive forwarding" )

        main.log.info( "Uninstall reactive forwarding app" )
        appCheck = main.TRUE
        appResults = appResults and main.CLIs[0].deactivateApp( "org.onosproject.fwd" )
        pool = []
        for cli in main.CLIs:
            t = main.Thread( target=cli.appToIDCheck,
                             name="appToIDCheck-" + str( i ),
                             args=[] )
            pool.append( t )
            t.start()

        for t in pool:
            t.join()
            appCheck = appCheck and t.result
        utilities.assert_equals( expect=main.TRUE, actual=appCheck,
                                 onpass="App Ids seem to be correct",
                                 onfail="Something is wrong with app Ids" )
        if appCheck != main.TRUE:
            main.log.warn( main.CLIs[0].apps() )
            main.log.warn( main.CLIs[0].appIDs() )

        # Waiting for reative flows to be cleared.
        time.sleep( 30 )
        caseResult =  appCheck and cfgResult and pingResult
        utilities.assert_equals( expect=main.TRUE, actual=caseResult,
                                 onpass="Reactive Mode IPv6 Pingall test PASS",
                                 onfail="Reactive Mode IPv6 Pingall test FAIL" )

    def CASE147( self, main ):
        """
        Verify IPv6 reactive forwarding in ATT topology, use a different ping method than CASE140
        """
        import time
        main.log.report( "Verify IPv6 Reactive forwarding (ATT Topology)" )
        main.log.report( "______________________________________________" )
        main.case( "Enable Reactive forwarding, verify ping6, and disable reactive forwarding" )

        main.step( "Enable IPv4 Reactive forwarding" )
        appResult = main.CLIs[0].activateApp( "org.onosproject.fwd" )
        utilities.assert_equals( expect=main.TRUE, actual=appResult,
                                 onpass="Successfully install fwd app",
                                 onfail="Failed to install fwd app" )

        main.step( "Set IPv6 cfg parameters for Reactive forwarding" )
        cfgResult1 = main.CLIs[0].setCfg( "org.onosproject.fwd.ReactiveForwarding", "ipv6Forwarding", "true" )
        cfgResult2 = main.CLIs[0].setCfg( "org.onosproject.fwd.ReactiveForwarding", "matchIpv6Address", "true" )
        cfgResult = cfgResult1 and cfgResult2
        utilities.assert_equals( expect=main.TRUE, actual=cfgResult,
                                 onpass="Reactive mode ipv6Fowarding cfg is set to true",
                                 onfail="Failed to cfg set Reactive mode ipv6Fowarding" )


        numHosts = int( main.params['TOPO1']['numHosts'] )

        for i in range(numHosts):
            src = "h1"
            dest = "1000::" + str(i+1)
            main.Mininet1.handle.sendline( src + " ping6 " + dest + " -c 3 -i 1 -W 1")
            main.Mininet1.handle.expect( "mininet>" )
            main.log.info( main.Mininet1.handle.before )

        hosts = main.CLIs[0].hosts( jsonFormat=False )

        main.log.info( hosts )

        main.step( "Disable Reactive forwarding" )

        main.log.info( "Uninstall IPv6 reactive forwarding app" )
        appCheck = main.TRUE
        appResults = main.CLIs[0].deactivateApp( "org.onosproject.fwd" )
        pool = []
        for cli in main.CLIs:
            t = main.Thread( target=cli.appToIDCheck,
                             name="appToIDCheck-" + str( i ),
                             args=[] )
            pool.append( t )
            t.start()

        for t in pool:
            t.join()
            appCheck = appCheck and t.result
        utilities.assert_equals( expect=main.TRUE, actual=appCheck,
                                 onpass="App Ids seem to be correct",
                                 onfail="Something is wrong with app Ids" )

        if appCheck != main.TRUE:
            main.log.warn( main.CLIs[0].apps() )
            main.log.warn( main.CLIs[0].appIDs() )

        # Waiting for reative flows to be cleared.
        time.sleep( 30 )

        main.step( "Disable IPv4 Reactive forwarding" )
        appResult =  main.CLIs[0].deactivateApp( "org.onosproject.fwd" )
        utilities.assert_equals( expect=main.TRUE, actual=appResult,
                                 onpass="Successfully deactivated IPv4 fwd app",
                                 onfail="Failed to deactivate IPv4 fwd app" )

    def CASE148( self, main ):
        """
        Verify reactive forwarding in Chordal topology, use a different ping method than CASE141
        """
        import time
        main.log.report( "Verify IPv6 Reactive forwarding (Chordal Topology)" )
        main.log.report( "______________________________________________" )
        main.case( "Enable Reactive forwarding, verify ping6, and disable reactive forwarding" )

        main.step( "Enable IPv4 Reactive forwarding" )
        appResult = main.CLIs[0].activateApp( "org.onosproject.fwd" )
        utilities.assert_equals( expect=main.TRUE, actual=appResult,
                                 onpass="Successfully install fwd app",
                                 onfail="Failed to install fwd app" )

        main.step( "Set IPv6 cfg parameters for Reactive forwarding" )
        cfgResult1 = main.CLIs[0].setCfg( "org.onosproject.fwd.ReactiveForwarding", "ipv6Forwarding", "true" )
        cfgResult2 = main.CLIs[0].setCfg( "org.onosproject.fwd.ReactiveForwarding", "matchIpv6Address", "true" )
        cfgResult = cfgResult1 and cfgResult2
        utilities.assert_equals( expect=main.TRUE, actual=cfgResult,
                                 onpass="Reactive mode ipv6Fowarding cfg is set to true",
                                 onfail="Failed to cfg set Reactive mode ipv6Fowarding" )


        numHosts = int( main.params['TOPO2']['numHosts'] )

        for i in range(numHosts):
            src = "h1"
            dest = "1000::" + str(i+1)
            main.Mininet1.handle.sendline( src + " ping6 " + dest + " -c 3 -i 1 -W 1")
            main.Mininet1.handle.expect( "mininet>" )
            main.log.info( main.Mininet1.handle.before )

        hosts = main.CLIs[0].hosts( jsonFormat=False )

        main.log.info( hosts )

        main.step( "Disable Reactive forwarding" )

        main.log.info( "Uninstall IPv6 reactive forwarding app" )
        appCheck = main.TRUE
        appResults = main.CLIs[0].deactivateApp( "org.onosproject.fwd" )
        pool = []
        for cli in main.CLIs:
            t = main.Thread( target=cli.appToIDCheck,
                             name="appToIDCheck-" + str( i ),
                             args=[] )
            pool.append( t )
            t.start()

        for t in pool:
            t.join()
            appCheck = appCheck and t.result
        utilities.assert_equals( expect=main.TRUE, actual=appCheck,
                                 onpass="App Ids seem to be correct",
                                 onfail="Something is wrong with app Ids" )

        if appCheck != main.TRUE:
            main.log.warn( main.CLIs[0].apps() )
            main.log.warn( main.CLIs[0].appIDs() )

        # Waiting for reative flows to be cleared.
        time.sleep( 30 )

        main.step( "Disable IPv4 Reactive forwarding" )
        appResult =  main.CLIs[0].deactivateApp( "org.onosproject.fwd" )
        utilities.assert_equals( expect=main.TRUE, actual=appResult,
                                 onpass="Successfully deactivated IPv4 fwd app",
                                 onfail="Failed to deactivate IPv4 fwd app" )

    def CASE149( self, main ):
        """
        Verify reactive forwarding in Spine-leaf topology, use a different ping method than CASE142
        """
        import time
        main.log.report( "Verify IPv6 Reactive forwarding (Spine-leaf Topology)" )
        main.log.report( "______________________________________________" )
        main.case( "Enable Reactive forwarding, verify ping6, and disable reactive forwarding" )

        main.step( "Enable IPv4 Reactive forwarding" )
        appResult = main.CLIs[0].activateApp( "org.onosproject.fwd" )
        utilities.assert_equals( expect=main.TRUE, actual=appResult,
                                 onpass="Successfully install fwd app",
                                 onfail="Failed to install fwd app" )

        main.step( "Set IPv6 cfg parameters for Reactive forwarding" )
        cfgResult1 = main.CLIs[0].setCfg( "org.onosproject.fwd.ReactiveForwarding", "ipv6Forwarding", "true" )
        cfgResult2 = main.CLIs[0].setCfg( "org.onosproject.fwd.ReactiveForwarding", "matchIpv6Address", "true" )
        cfgResult = cfgResult1 and cfgResult2
        utilities.assert_equals( expect=main.TRUE, actual=cfgResult,
                                 onpass="Reactive mode ipv6Fowarding cfg is set to true",
                                 onfail="Failed to cfg set Reactive mode ipv6Fowarding" )


        numHosts = int( main.params['TOPO3']['numHosts'] )

        for i in range(11, numHosts+10):
            src = "h11"
            dest = "1000::" + str(i+1)
            main.Mininet1.handle.sendline( src + " ping6 " + dest + " -c 3 -i 1 -W 1")
            main.Mininet1.handle.expect( "mininet>" )
            main.log.info( main.Mininet1.handle.before )

        hosts = main.CLIs[0].hosts( jsonFormat=False )

        main.log.info( hosts )

        main.step( "Disable Reactive forwarding" )

        main.log.info( "Uninstall IPv6 reactive forwarding app" )
        appCheck = main.TRUE
        appResults = main.CLIs[0].deactivateApp( "org.onosproject.fwd" )
        pool = []
        for cli in main.CLIs:
            t = main.Thread( target=cli.appToIDCheck,
                             name="appToIDCheck-" + str( i ),
                             args=[] )
            pool.append( t )
            t.start()

        for t in pool:
            t.join()
            appCheck = appCheck and t.result
        utilities.assert_equals( expect=main.TRUE, actual=appCheck,
                                 onpass="App Ids seem to be correct",
                                 onfail="Something is wrong with app Ids" )

        if appCheck != main.TRUE:
            main.log.warn( main.CLIs[0].apps() )
            main.log.warn( main.CLIs[0].appIDs() )

        # Waiting for reative flows to be cleared.
        time.sleep( 30 )

        main.step( "Disable IPv4 Reactive forwarding" )
        appResult =  main.CLIs[0].deactivateApp( "org.onosproject.fwd" )
        utilities.assert_equals( expect=main.TRUE, actual=appResult,
                                 onpass="Successfully deactivated IPv4 fwd app",
                                 onfail="Failed to deactivate IPv4 fwd app" )

    def CASE5( self, main ):
        """
        Compare current ONOS topology with reference data
        """
        import re

        devicesDPIDTemp = []
        hostMACsTemp = []
        deviceLinksTemp = []
        deviceActiveLinksCountTemp = []
        devicePortsEnabledCountTemp = []

        main.log.report(
            "Compare ONOS topology with reference data in Stores" )
        main.log.report( "__________________________________________________" )
        main.case( "Compare ONOS topology with reference data" )

        main.step( "Compare current Device ports enabled with reference" )

        for check in range(main.topoCheck):
            time1 = time.time()
            for i in xrange( 1,(main.numMNswitches + 1), int( main.numCtrls ) ):
                pool = []
                for cli in main.CLIs:
                    if i >=  main.numMNswitches + 1:
                        break
                    dpid = "of:00000000000000" + format( i, "02x" )
                    t = main.Thread(target = cli.getDevicePortsEnabledCount,
                            threadID = main.threadID,
                            name = "getDevicePortsEnabledCount",
                            args = [dpid])
                    t.start()
                    pool.append(t)
                    i = i + 1
                    main.threadID = main.threadID + 1
                for thread in pool:
                    thread.join()
                    portResult = thread.result
                    #portTemp = re.split( r'\t+', portResult )
                    #portCount = portTemp[ 1 ].replace( "\r\r\n\x1b[32m", "" )
                    devicePortsEnabledCountTemp.append( portResult )

            time2 = time.time()
            main.log.info("Time for counting enabled ports of the switches: %2f seconds" %(time2-time1))
            main.log.info (
                "Device Enabled ports EXPECTED: %s" %
                str( main.devicePortsEnabledCount ) )
            main.log.info (
                "Device Enabled ports ACTUAL: %s" %
                str( devicePortsEnabledCountTemp ) )

            if ( cmp( main.devicePortsEnabledCount,
                      devicePortsEnabledCountTemp ) == 0 ):
                stepResult1 = main.TRUE
            else:
                stepResult1 = main.FALSE

            main.step( "Compare Device active links with reference" )
            time1 = time.time()
            for i in xrange( 1, ( main.numMNswitches + 1) , int( main.numCtrls ) ):
                pool = []
                for cli in main.CLIs:
                    if i >=  main.numMNswitches + 1:
                        break
                    dpid = "of:00000000000000" + format( i, "02x" )
                    t = main.Thread(target = cli.getDeviceLinksActiveCount,
                            threadID = main.threadID,
                            name = "getDeviceLinksActiveCount",
                            args = [dpid])
                    t.start()
                    pool.append(t)
                    i = i + 1
                    main.threadID = main.threadID + 1
                for thread in pool:
                    thread.join()
                    linkCountResult = thread.result
                    #linkCountTemp = re.split( r'\t+', linkCountResult )
                    #linkCount = linkCountTemp[ 1 ].replace( "\r\r\n\x1b[32m", "" )
                    deviceActiveLinksCountTemp.append( linkCountResult )

                    time2 = time.time()
                    main.log.info("Time for counting all enabled links of the switches: %2f seconds" %(time2-time1))
                    main.log.info (
                        "Device Active links EXPECTED: %s" %
                          str( main.deviceActiveLinksCount ) )
                    main.log.info (
                        "Device Active links ACTUAL: %s" % str( deviceActiveLinksCountTemp ) )
                    if ( cmp( main.deviceActiveLinksCount, deviceActiveLinksCountTemp ) == 0 ):
                        stepResult2 = main.TRUE
                    else:
                        stepResult2 = main.FALSE

            """
            place holder for comparing devices, hosts, paths and intents if required.
            Links and ports data would be incorrect with out devices anyways.
            """
            caseResult = ( stepResult1 and stepResult2 )

            if caseResult:
                break
            else:
                time.sleep( main.topoCheckDelay )
                main.log.warn( "Topology check failed. Trying again..." )


        utilities.assert_equals( expect=main.TRUE, actual=caseResult,
                                 onpass="Compare Topology test PASS",
                                 onfail="Compare Topology test FAIL" )

    def CASE60( self ):
        """
        Install 300 host intents and verify ping all (Att Topology)
        """
        main.log.report( "Add 300 host intents and verify pingall (Att Topology)" )
        main.log.report( "_______________________________________" )
        import itertools
        import time
        main.case( "Install 300 host intents" )
        main.step( "Add host Intents" )
        intentResult = main.TRUE
        hostCombos = list( itertools.combinations( main.hostMACs, 2 ) )

        intentIdList = []
        time1 = time.time()
        for i in xrange( 0, len( hostCombos ), int(main.numCtrls) ):
            pool = []
            for cli in main.CLIs:
                if i >= len( hostCombos ):
                    break
                t = main.Thread( target=cli.addHostIntent,
                        threadID=main.threadID,
                        name="addHostIntent",
                        args=[hostCombos[i][0],hostCombos[i][1]])
                pool.append(t)
                t.start()
                i = i + 1
                main.threadID = main.threadID + 1
            for thread in pool:
                thread.join()
                intentIdList.append(thread.result)
        time2 = time.time()
        main.log.info("Time for adding host intents: %2f seconds" %(time2-time1))

        # Saving intent ids to check intents in later cases
        main.intentIds = list(intentIdList)

        main.step("Verify intents are installed")

        # Giving onos multiple chances to install intents
        for i in range( main.intentCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
            main.log.info("Waiting for onos to install intents...")
            time.sleep( main.checkIntentsDelay )

            intentState = main.TRUE
            for e in range(int(main.numCtrls)):
                main.log.info( "Checking intents on CLI %s" % (e+1) )
                intentState = main.CLIs[e].checkIntentState( intentsId = intentIdList ) and\
                        intentState
                if not intentState:
                    main.log.warn( "Not all intents installed" )
            if intentState:
                break
        else:
            #Dumping intent summary
            main.log.info( "**** Intent Summary ****\n" + str(main.ONOScli1.intents( jsonFormat=False, summary=True)) )


        utilities.assert_equals( expect=main.TRUE, actual=intentState,
                                 onpass="INTENTS INSTALLED",
                                 onfail="SOME INTENTS NOT INSTALLED" )

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(3)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = ( intentState and pingResult )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="Install 300 Host Intents and Ping All test PASS",
            onfail="Install 300 Host Intents and Ping All test FAIL" )

        if not intentState:
            main.log.debug( "Intents failed to install completely" )
        if not pingResult:
            main.log.debug( "Pingall failed" )

        if not caseResult and main.failSwitch:
            main.log.report("Stopping test")
            main.stop( email=main.emailOnStop )

    def CASE61( self ):
        """
        Install 300 host intents and verify ping all for Chordal Topology
        """
        main.log.report( "Add 300 host intents and verify pingall (Chordal Topo)" )
        main.log.report( "_______________________________________" )
        import itertools

        main.case( "Install 300 host intents" )
        main.step( "Add host Intents" )
        intentResult = main.TRUE
        hostCombos = list( itertools.combinations( main.hostMACs, 2 ) )

        intentIdList = []
        time1 = time.time()

        for i in xrange( 0, len( hostCombos ), int(main.numCtrls) ):
            pool = []
            for cli in main.CLIs:
                if i >= len( hostCombos ):
                    break
                t = main.Thread( target=cli.addHostIntent,
                        threadID=main.threadID,
                        name="addHostIntent",
                        args=[hostCombos[i][0],hostCombos[i][1]])
                pool.append(t)
                t.start()
                i = i + 1
                main.threadID = main.threadID + 1
            for thread in pool:
                thread.join()
                intentIdList.append(thread.result)
        time2 = time.time()
        main.log.info("Time for adding host intents: %2f seconds" %(time2-time1))

        # Saving intent ids to check intents in later cases
        main.intentIds = list(intentIdList)

        main.step("Verify intents are installed")

        # Giving onos multiple chances to install intents
        for i in range( main.intentCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
            main.log.info("Waiting for onos to install intents...")
            time.sleep( main.checkIntentsDelay )

            intentState = main.TRUE
            for e in range(int(main.numCtrls)):
                main.log.info( "Checking intents on CLI %s" % (e+1) )
                intentState = main.CLIs[e].checkIntentState( intentsId = intentIdList ) and\
                        intentState
                if not intentState:
                    main.log.warn( "Not all intents installed" )
            if intentState:
                break
        else:
            #Dumping intent summary
            main.log.info( "**** Intents Summary ****\n" + str(main.ONOScli1.intents(jsonFormat=False, summary=True)) )

        utilities.assert_equals( expect=main.TRUE, actual=intentState,
                                 onpass="INTENTS INSTALLED",
                                 onfail="SOME INTENTS NOT INSTALLED" )

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = ( intentState and pingResult )

        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="Install 300 Host Intents and Ping All test PASS",
            onfail="Install 300 Host Intents and Ping All test FAIL" )

        if not intentState:
            main.log.debug( "Intents failed to install completely" )
        if not pingResult:
            main.log.debug( "Pingall failed" )

        if not caseResult and main.failSwitch:
            main.log.report("Stopping test")
            main.stop( email=main.emailOnStop )

    def CASE62( self ):
        """
        Install 2278 host intents and verify ping all for Spine Topology
        """
        main.log.report( "Add 2278 host intents and verify pingall (Spine Topo)" )
        main.log.report( "_______________________________________" )
        import itertools

        main.case( "Install 2278 host intents" )
        main.step( "Add host Intents" )
        intentResult = main.TRUE
        hostCombos = list( itertools.combinations( main.hostMACs, 2 ) )
        main.pingTimeout = 300
        intentIdList = []
        time1 = time.time()
        for i in xrange( 0, len( hostCombos ), int(main.numCtrls) ):
            pool = []
            for cli in main.CLIs:
                if i >= len( hostCombos ):
                    break
                t = main.Thread( target=cli.addHostIntent,
                        threadID=main.threadID,
                        name="addHostIntent",
                        args=[hostCombos[i][0],hostCombos[i][1]])
                pool.append(t)
                t.start()
                i = i + 1
                main.threadID = main.threadID + 1
            for thread in pool:
                thread.join()
                intentIdList.append(thread.result)
        time2 = time.time()
        main.log.info("Time for adding host intents: %2f seconds" %(time2-time1))

        # Saving intent ids to check intents in later cases
        main.intentIds = list(intentIdList)

        main.step("Verify intents are installed")

        # Giving onos multiple chances to install intents
        for i in range( main.intentCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
            main.log.info("Waiting for onos to install intents...")
            time.sleep( main.checkIntentsDelay )

            intentState = main.TRUE
            for e in range(int(main.numCtrls)):
                main.log.info( "Checking intents on CLI %s" % (e+1) )
                intentState = main.CLIs[e].checkIntentState( intentsId = intentIdList ) and\
                        intentState
                if not intentState:
                    main.log.warn( "Not all intents installed" )
            if intentState:
                break
        else:
            #Dumping intent summary
            main.log.info( "**** Intents Summary ****\n" + str(main.ONOScli1.intents(jsonFormat=False, summary=True)) )

        utilities.assert_equals( expect=main.TRUE, actual=intentState,
                                 onpass="INTENTS INSTALLED",
                                 onfail="SOME INTENTS NOT INSTALLED" )

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = ( intentState and pingResult )

        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="Install 2278 Host Intents and Ping All test PASS",
            onfail="Install 2278 Host Intents and Ping All test FAIL" )

        if not intentState:
            main.log.debug( "Intents failed to install completely" )
        if not pingResult:
            main.log.debug( "Pingall failed" )

        if not caseResult and main.failSwitch:
            main.log.report("Stopping test")
            main.stop( email=main.emailOnStop )

    def CASE160( self ):
        """
        Verify IPv6 ping across 300 host intents (Att Topology)
        """
        main.log.report( "Verify IPv6 ping across 300 host intents (Att Topology)" )
        main.log.report( "_________________________________________________" )
        import itertools
        import time
        main.case( "IPv6 ping all 300 host intents" )
        main.step( "Verify IPv6 Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        if not pingResult:
            main.log.warn("First pingall failed. Retrying...")
            time1 = time.time()
            pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for IPv6 Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = pingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="IPv6 Ping across 300 host intents test PASS",
            onfail="IPv6 Ping across 300 host intents test FAIL" )

    def CASE161( self ):
        """
        Verify IPv6 ping across 300 host intents (Chordal Topology)
        """
        main.log.report( "Verify IPv6 ping across 300 host intents (Chordal Topology)" )
        main.log.report( "_________________________________________________" )
        import itertools
        import time
        main.case( "IPv6 ping all 300 host intents" )
        main.step( "Verify IPv6 Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        if not pingResult:
            main.log.warn("First pingall failed. Retrying...")
            time1 = time.time()
            pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for IPv6 Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = pingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="IPv6 Ping across 300 host intents test PASS",
            onfail="IPv6 Ping across 300 host intents test FAIL" )

    def CASE162( self ):
        """
        Verify IPv6 ping across 2278 host intents (Spine Topology)
        """
        main.log.report( "Verify IPv6 ping across 2278 host intents (Spine Topology)" )
        main.log.report( "_________________________________________________" )
        import itertools
        import time
        main.case( "IPv6 ping all 2278 host intents" )
        main.step( "Verify IPv6 Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        if not pingResult:
            main.log.warn("First pingall failed. Retrying...")
            time1 = time.time()
            pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for IPv6 Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = pingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="IPv6 Ping across 2278 host intents test PASS",
            onfail="IPv6 Ping across 2278 host intents test FAIL" )

    def CASE70( self, main ):
        """
        Randomly bring some core links down and verify ping all ( Host Intents-Att Topo)
        """
        import random
        main.randomLink1 = []
        main.randomLink2 = []
        main.randomLink3 = []
        link1End1 = main.params[ 'ATTCORELINKS' ][ 'linkS3a' ]
        link1End2 = main.params[ 'ATTCORELINKS' ][ 'linkS3b' ].split( ',' )
        link2End1 = main.params[ 'ATTCORELINKS' ][ 'linkS14a' ]
        link2End2 = main.params[ 'ATTCORELINKS' ][ 'linkS14b' ].split( ',' )
        link3End1 = main.params[ 'ATTCORELINKS' ][ 'linkS18a' ]
        link3End2 = main.params[ 'ATTCORELINKS' ][ 'linkS18b' ].split( ',' )
        switchLinksToToggle = main.params[ 'ATTCORELINKS' ][ 'toggleLinks' ]
        link_sleep = int( main.params[ 'timers' ][ 'LinkDiscovery' ] )

        main.log.report( "Randomly bring some core links down and verify ping all (Host Intents-Att Topo)" )
        main.log.report( "___________________________________________________________________________" )
        main.case( "Host intents - Randomly bring some core links down and verify ping all" )
        main.step( "Verify number of Switch links to toggle on each Core Switch are between 1 - 5" )
        if ( int( switchLinksToToggle ) ==
             0 or int( switchLinksToToggle ) > 5 ):
            main.log.info( "Please check your PARAMS file. Valid range for number of switch links to toggle is between 1 to 5" )
            #main.cleanup()
            #main.exit()
        else:
            main.log.info( "User provided Core switch links range to toggle is correct, proceeding to run the test" )

        main.step( "Cut links on Core devices using user provided range" )
        main.randomLink1 = random.sample( link1End2, int( switchLinksToToggle ) )
        main.randomLink2 = random.sample( link2End2, int( switchLinksToToggle ) )
        main.randomLink3 = random.sample( link3End2, int( switchLinksToToggle ) )
        for i in range( int( switchLinksToToggle ) ):
            main.Mininet1.link(
                END1=link1End1,
                END2=main.randomLink1[ i ],
                OPTION="down" )
            time.sleep( link_sleep )
            main.Mininet1.link(
                END1=link2End1,
                END2=main.randomLink2[ i ],
                OPTION="down" )
            time.sleep( link_sleep )
            main.Mininet1.link(
                END1=link3End1,
                END2=main.randomLink3[ i ],
                OPTION="down" )
            time.sleep( link_sleep )

        main.step("Verify link down is discoverd by onos")
        # Giving onos multiple chances to discover link events
        for i in range( main.linkCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
                main.log.info("Giving onos some time...")
                time.sleep( link_sleep )

            topology_output = main.ONOScli1.topology()
            linkDown = main.ONOSbench.checkStatus(
            topology_output, main.numMNswitches, str(
                int( main.numMNlinks ) - int( switchLinksToToggle ) * 6 ) )
            if linkDown:
                break

        utilities.assert_equals(
            expect=main.TRUE,
            actual=linkDown,
            onpass="Link down discovered properly",
            onfail="Link down was not discovered in " +
            str( link_sleep * main.linkCheck ) +
            " seconds" )

        main.step("Verify intents are installed")
        # Giving onos multiple chances to install intents
        for i in range( main.intentCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
            main.log.info("Giving onos some time...")
            time.sleep( main.checkIntentsDelay )

            intentState = main.TRUE
            for e in range(int(main.numCtrls)):
                main.log.info( "Checking intents on CLI %s" % (e+1) )
                intentState = main.CLIs[e].checkIntentState( intentsId = main.intentIds ) and\
                        intentState
                if not intentState:
                    main.log.warn( "Not all intents installed" )
            if intentState:
                break
        else:
            #Dumping intent summary
            main.log.info( "**** Intent Summary ****\n" + str(main.ONOScli1.intents( jsonFormat=False, summary=True)) )


        utilities.assert_equals( expect=main.TRUE, actual=intentState,
                                 onpass="INTENTS INSTALLED",
                                 onfail="SOME INTENTS NOT INSTALLED" )

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = linkDown and pingResult and intentState
        utilities.assert_equals( expect=main.TRUE, actual=caseResult,
                                 onpass="Random Link cut Test PASS",
                                 onfail="Random Link cut Test FAIL" )

        # Printing what exactly failed
        if not linkDown:
            main.log.debug( "Link down was not discovered correctly" )
        if not pingResult:
            main.log.debug( "Pingall failed" )
        if not intentState:
            main.log.debug( "Intents are not all installed" )

        if not caseResult and main.failSwitch:
            main.log.report("Stopping test")
            main.stop( email=main.emailOnStop )

    def CASE80( self, main ):
        """
        Bring the core links up that are down and verify ping all ( Host Intents-Att Topo )
        """
        import random
        link1End1 = main.params[ 'ATTCORELINKS' ][ 'linkS3a' ]
        link2End1 = main.params[ 'ATTCORELINKS' ][ 'linkS14a' ]
        link3End1 = main.params[ 'ATTCORELINKS' ][ 'linkS18a' ]
        link_sleep = int( main.params[ 'timers' ][ 'LinkDiscovery' ] )
        switchLinksToToggle = main.params[ 'ATTCORELINKS' ][ 'toggleLinks' ]

        main.log.report(
            "Bring the core links up that are down and verify ping all (Host Intents-Att Topo" )
        main.log.report(
            "__________________________________________________________________" )
        main.case(
            "Host intents - Bring the core links up that are down and verify ping all" )
        main.step( "Bring randomly cut links on Core devices up" )
        for i in range( int( switchLinksToToggle ) ):
            main.Mininet1.link(
                END1=link1End1,
                END2=main.randomLink1[ i ],
                OPTION="up" )
            time.sleep( link_sleep )
            main.Mininet1.link(
                END1=link2End1,
                END2=main.randomLink2[ i ],
                OPTION="up" )
            time.sleep( link_sleep )
            main.Mininet1.link(
                END1=link3End1,
                END2=main.randomLink3[ i ],
                OPTION="up" )
            time.sleep( link_sleep )

        main.step("Verify link up is discoverd by onos")
        # Giving onos multiple chances to discover link events
        for i in range( main.linkCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
                main.log.info("Giving onos some time...")
                time.sleep( link_sleep )

            topology_output = main.ONOScli1.topology()
            linkUp = main.ONOSbench.checkStatus(
                topology_output,
                main.numMNswitches,
                str( main.numMNlinks ) )
            if linkUp:
                break

        utilities.assert_equals(
            expect=main.TRUE,
            actual=linkUp,
            onpass="Link up discovered properly",
            onfail="Link up was not discovered in " +
            str( link_sleep * main.linkCheck ) +
            " seconds" )

        main.step("Verify intents are installed")
        # Giving onos multiple chances to install intents
        for i in range( main.intentCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
            main.log.info("Giving onos some time...")
            time.sleep( main.checkIntentsDelay )

            intentState = main.TRUE
            for e in range(int(main.numCtrls)):
                main.log.info( "Checking intents on CLI %s" % (e+1) )
                intentState = main.CLIs[e].checkIntentState( intentsId = main.intentIds ) and\
                        intentState
                if not intentState:
                    main.log.warn( "Not all intents installed" )
            if intentState:
                break
        else:
            #Dumping intent summary
            main.log.info( "**** Intent Summary ****\n" + str(main.ONOScli1.intents( jsonFormat=False, summary=True)) )


        utilities.assert_equals( expect=main.TRUE, actual=intentState,
                                 onpass="INTENTS INSTALLED",
                                 onfail="SOME INTENTS NOT INSTALLED" )

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = linkUp and pingResult
        utilities.assert_equals( expect=main.TRUE, actual=caseResult,
                                 onpass="Link Up Test PASS",
                                 onfail="Link Up Test FAIL" )
        # Printing what exactly failed
        if not linkUp:
            main.log.debug( "Link up was not discovered correctly" )
        if not pingResult:
            main.log.debug( "Pingall failed" )
        if not intentState:
            main.log.debug( "Intents are not all installed" )

        if not caseResult and main.failSwitch:
            main.log.report("Stopping test")
            main.stop( email=main.emailOnStop )

    def CASE71( self, main ):
        """
        Randomly bring some core links down and verify ping all ( Point Intents-Att Topo)
        """
        import random
        main.randomLink1 = []
        main.randomLink2 = []
        main.randomLink3 = []
        link1End1 = main.params[ 'ATTCORELINKS' ][ 'linkS3a' ]
        link1End2 = main.params[ 'ATTCORELINKS' ][ 'linkS3b' ].split( ',' )
        link2End1 = main.params[ 'ATTCORELINKS' ][ 'linkS14a' ]
        link2End2 = main.params[ 'ATTCORELINKS' ][ 'linkS14b' ].split( ',' )
        link3End1 = main.params[ 'ATTCORELINKS' ][ 'linkS18a' ]
        link3End2 = main.params[ 'ATTCORELINKS' ][ 'linkS18b' ].split( ',' )
        switchLinksToToggle = main.params[ 'ATTCORELINKS' ][ 'toggleLinks' ]
        link_sleep = int( main.params[ 'timers' ][ 'LinkDiscovery' ] )

        main.log.report( "Randomly bring some core links down and verify ping all (Point Intents-Att Topo)" )
        main.log.report( "___________________________________________________________________________" )
        main.case( "Point intents - Randomly bring some core links down and verify ping all" )
        main.step( "Verify number of Switch links to toggle on each Core Switch are between 1 - 5" )
        if ( int( switchLinksToToggle ) ==
             0 or int( switchLinksToToggle ) > 5 ):
            main.log.info( "Please check your PARAMS file. Valid range for number of switch links to toggle is between 1 to 5" )
            #main.cleanup()
            #main.exit()
        else:
            main.log.info( "User provided Core switch links range to toggle is correct, proceeding to run the test" )

        main.step( "Cut links on Core devices using user provided range" )
        main.randomLink1 = random.sample( link1End2, int( switchLinksToToggle ) )
        main.randomLink2 = random.sample( link2End2, int( switchLinksToToggle ) )
        main.randomLink3 = random.sample( link3End2, int( switchLinksToToggle ) )
        for i in range( int( switchLinksToToggle ) ):
            main.Mininet1.link(
                END1=link1End1,
                END2=main.randomLink1[ i ],
                OPTION="down" )
            time.sleep( link_sleep )
            main.Mininet1.link(
                END1=link2End1,
                END2=main.randomLink2[ i ],
                OPTION="down" )
            time.sleep( link_sleep )
            main.Mininet1.link(
                END1=link3End1,
                END2=main.randomLink3[ i ],
                OPTION="down" )
            time.sleep( link_sleep )

        main.step("Verify link down is discoverd by onos")
        # Giving onos multiple chances to discover link events
        for i in range( main.linkCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
                main.log.info("Giving onos some time...")
                time.sleep( link_sleep )

            topology_output = main.ONOScli1.topology()
            linkDown = main.ONOSbench.checkStatus(
            topology_output, main.numMNswitches, str(
                int( main.numMNlinks ) - int( switchLinksToToggle ) * 6 ) )
            if linkDown:
                break

        utilities.assert_equals(
            expect=main.TRUE,
            actual=linkDown,
            onpass="Link down discovered properly",
            onfail="Link down was not discovered in " +
            str( link_sleep * main.linkCheck ) +
            " seconds" )

        main.step("Verify intents are installed")
        # Giving onos multiple chances to install intents
        for i in range( main.intentCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
            main.log.info("Giving onos some time...")
            time.sleep( main.checkIntentsDelay )

            intentState = main.TRUE
            for e in range(int(main.numCtrls)):
                main.log.info( "Checking intents on CLI %s" % (e+1) )
                intentState = main.CLIs[e].checkIntentState( intentsId = main.intentIds ) and\
                        intentState
                if not intentState:
                    main.log.warn( "Not all intents installed" )
            if intentState:
                break
        else:
            #Dumping intent summary
            main.log.info( "**** Intent Summary ****\n" + str(main.ONOScli1.intents( jsonFormat=False, summary=True)) )


        utilities.assert_equals( expect=main.TRUE, actual=intentState,
                                 onpass="INTENTS INSTALLED",
                                 onfail="SOME INTENTS NOT INSTALLED" )

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = linkDown and pingResult and intentState
        utilities.assert_equals( expect=main.TRUE, actual=caseResult,
                                 onpass="Random Link cut Test PASS",
                                 onfail="Random Link cut Test FAIL" )

        # Printing what exactly failed
        if not linkDown:
            main.log.debug( "Link down was not discovered correctly" )
        if not pingResult:
            main.log.debug( "Pingall failed" )
        if not intentState:
            main.log.debug( "Intents are not all installed" )

        if not caseResult and main.failSwitch:
            main.log.report("Stopping test")
            main.stop( email=main.emailOnStop )

    def CASE81( self, main ):
        """
        Bring the core links up that are down and verify ping all ( Point Intents-Att Topo )
        """
        import random
        link1End1 = main.params[ 'ATTCORELINKS' ][ 'linkS3a' ]
        link2End1 = main.params[ 'ATTCORELINKS' ][ 'linkS14a' ]
        link3End1 = main.params[ 'ATTCORELINKS' ][ 'linkS18a' ]
        link_sleep = int( main.params[ 'timers' ][ 'LinkDiscovery' ] )
        switchLinksToToggle = main.params[ 'ATTCORELINKS' ][ 'toggleLinks' ]

        main.log.report(
            "Bring the core links up that are down and verify ping all ( Point Intents-Att Topo" )
        main.log.report(
            "__________________________________________________________________" )
        main.case(
            "Point intents - Bring the core links up that are down and verify ping all" )
        main.step( "Bring randomly cut links on Core devices up" )
        for i in range( int( switchLinksToToggle ) ):
            main.Mininet1.link(
                END1=link1End1,
                END2=main.randomLink1[ i ],
                OPTION="up" )
            time.sleep( link_sleep )
            main.Mininet1.link(
                END1=link2End1,
                END2=main.randomLink2[ i ],
                OPTION="up" )
            time.sleep( link_sleep )
            main.Mininet1.link(
                END1=link3End1,
                END2=main.randomLink3[ i ],
                OPTION="up" )
            time.sleep( link_sleep )

        main.step("Verify link up is discoverd by onos")
        # Giving onos multiple chances to discover link events
        for i in range( main.linkCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
                main.log.info("Giving onos some time...")
                time.sleep( link_sleep )

            topology_output = main.ONOScli1.topology()
            linkUp = main.ONOSbench.checkStatus(
                topology_output,
                main.numMNswitches,
                str( main.numMNlinks ) )
            if linkUp:
                break

        utilities.assert_equals(
            expect=main.TRUE,
            actual=linkUp,
            onpass="Link up discovered properly",
            onfail="Link up was not discovered in " +
            str( link_sleep * main.linkCheck ) +
            " seconds" )

        main.step("Verify intents are installed")
        # Giving onos multiple chances to install intents
        for i in range( main.intentCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
            main.log.info("Giving onos some time...")
            time.sleep( main.checkIntentsDelay )

            intentState = main.TRUE
            for e in range(int(main.numCtrls)):
                main.log.info( "Checking intents on CLI %s" % (e+1) )
                intentState = main.CLIs[e].checkIntentState( intentsId = main.intentIds ) and\
                        intentState
                if not intentState:
                    main.log.warn( "Not all intents installed" )
            if intentState:
                break
        else:
            #Dumping intent summary
            main.log.info( "**** Intent Summary ****\n" + str(main.ONOScli1.intents( jsonFormat=False, summary=True)) )


        utilities.assert_equals( expect=main.TRUE, actual=intentState,
                                 onpass="INTENTS INSTALLED",
                                 onfail="SOME INTENTS NOT INSTALLED" )

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = linkUp and pingResult
        utilities.assert_equals( expect=main.TRUE, actual=caseResult,
                                 onpass="Link Up Test PASS",
                                 onfail="Link Up Test FAIL" )
        # Printing what exactly failed
        if not linkUp:
            main.log.debug( "Link up was not discovered correctly" )
        if not pingResult:
            main.log.debug( "Pingall failed" )
        if not intentState:
            main.log.debug( "Intents are not all installed" )

        if not caseResult and main.failSwitch:
            main.log.report("Stopping test")
            main.stop( email=main.emailOnStop )

    def CASE72( self, main ):
        """
        Randomly bring some links down and verify ping all ( Host Intents-Chordal Topo)
        """
        import random
        import itertools
        link_sleep = int( main.params[ 'timers' ][ 'LinkDiscovery' ] )

        main.log.report( "Randomly bring some core links down and verify ping all (Host Intents-Chordal Topo)" )
        main.log.report( "___________________________________________________________________________" )
        main.case( "Host intents - Randomly bring some core links down and verify ping all" )
        switches = []
        switchesComb = []
        for i in range( main.numMNswitches ):
            switches.append('s%d'%(i+1))
        switchesLinksComb = list(itertools.combinations(switches,2))
        main.randomLinks = random.sample(switchesLinksComb, 5 )
        print main.randomLinks
        main.step( "Cut links on random devices" )

        for switch in main.randomLinks:
            main.Mininet1.link(
                END1=switch[0],
                END2=switch[1],
                OPTION="down")
            time.sleep( link_sleep )

        main.step("Verify link down is discoverd by onos")
        # Giving onos multiple chances to discover link events
        for i in range( main.linkCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
                main.log.info("Giving onos some time...")
                time.sleep( link_sleep )

            topology_output = main.ONOScli1.topology()
            linkDown = main.ONOSbench.checkStatus(
            topology_output, main.numMNswitches, str(
                int( main.numMNlinks ) - 5 * 2 ) )
            if linkDown:
                break

        utilities.assert_equals(
            expect=main.TRUE,
            actual=linkDown,
            onpass="Link down discovered properly",
            onfail="Link down was not discovered in " +
            str( link_sleep * main.linkCheck ) +
            " seconds" )

        main.step("Verify intents are installed")
        # Giving onos multiple chances to install intents
        for i in range( main.intentCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
            main.log.info("Giving onos some time...")
            time.sleep( main.checkIntentsDelay )

            intentState = main.TRUE
            for e in range(int(main.numCtrls)):
                main.log.info( "Checking intents on CLI %s" % (e+1) )
                intentState = main.CLIs[e].checkIntentState( intentsId = main.intentIds ) and\
                        intentState
                if not intentState:
                    main.log.warn( "Not all intents installed" )
            if intentState:
                break
        else:
            #Dumping intent summary
            main.log.info( "**** Intent Summary ****\n" + str(main.ONOScli1.intents( jsonFormat=False, summary=True)) )


        utilities.assert_equals( expect=main.TRUE, actual=intentState,
                                 onpass="INTENTS INSTALLED",
                                 onfail="SOME INTENTS NOT INSTALLED" )

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = linkDown and pingResult and intentState
        utilities.assert_equals( expect=main.TRUE, actual=caseResult,
                                 onpass="Random Link cut Test PASS",
                                 onfail="Random Link cut Test FAIL" )

        # Printing what exactly failed
        if not linkDown:
            main.log.debug( "Link down was not discovered correctly" )
        if not pingResult:
            main.log.debug( "Pingall failed" )
        if not intentState:
            main.log.debug( "Intents are not all installed" )

        if not caseResult and main.failSwitch:
            main.log.report("Stopping test")
            main.stop( email=main.emailOnStop )

    def CASE82( self, main ):
        """
        Bring the core links up that are down and verify ping all ( Host Intents Chordal Topo )
        """
        import random
        link_sleep = int( main.params[ 'timers' ][ 'LinkDiscovery' ] )

        main.log.report(
            "Bring the core links up that are down and verify ping all (Host Intents-Chordal Topo" )
        main.log.report(
            "__________________________________________________________________" )
        main.case(
            "Host intents - Bring the core links up that are down and verify ping all" )
        main.step( "Bring randomly cut links on devices up" )

        for switch in main.randomLinks:
            main.Mininet1.link(
                END1=switch[0],
                END2=switch[1],
                OPTION="up")
            time.sleep( link_sleep )

        main.step("Verify link up is discoverd by onos")
        # Giving onos multiple chances to discover link events
        for i in range( main.linkCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
                main.log.info("Giving onos some time...")
                time.sleep( link_sleep )

            topology_output = main.ONOScli1.topology()
            linkUp = main.ONOSbench.checkStatus(
                topology_output,
                main.numMNswitches,
                str( main.numMNlinks ) )
            if linkUp:
                break

        utilities.assert_equals(
            expect=main.TRUE,
            actual=linkUp,
            onpass="Link up discovered properly",
            onfail="Link up was not discovered in " +
            str( link_sleep * main.linkCheck ) +
            " seconds" )

        main.step("Verify intents are installed")
        # Giving onos multiple chances to install intents
        for i in range( main.intentCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
            main.log.info("Giving onos some time...")
            time.sleep( main.checkIntentsDelay )

            intentState = main.TRUE
            for e in range(int(main.numCtrls)):
                main.log.info( "Checking intents on CLI %s" % (e+1) )
                intentState = main.CLIs[e].checkIntentState( intentsId = main.intentIds ) and\
                        intentState
                if not intentState:
                    main.log.warn( "Not all intents installed" )
            if intentState:
                break
        else:
            #Dumping intent summary
            main.log.info( "**** Intent Summary ****\n" + str(main.ONOScli1.intents( jsonFormat=False, summary=True)) )


        utilities.assert_equals( expect=main.TRUE, actual=intentState,
                                 onpass="INTENTS INSTALLED",
                                 onfail="SOME INTENTS NOT INSTALLED" )

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = linkUp and pingResult
        utilities.assert_equals( expect=main.TRUE, actual=caseResult,
                                 onpass="Link Up Test PASS",
                                 onfail="Link Up Test FAIL" )
        # Printing what exactly failed
        if not linkUp:
            main.log.debug( "Link up was not discovered correctly" )
        if not pingResult:
            main.log.debug( "Pingall failed" )
        if not intentState:
            main.log.debug( "Intents are not all installed" )

        if not caseResult and main.failSwitch:
            main.log.report("Stopping test")
            main.stop( email=main.emailOnStop )

    def CASE73( self, main ):
        """
        Randomly bring some links down and verify ping all ( Point Intents-Chordal Topo)
        """
        import random
        import itertools
        link_sleep = int( main.params[ 'timers' ][ 'LinkDiscovery' ] )

        main.log.report( "Randomly bring some core links down and verify ping all ( Point Intents-Chordal Topo)" )
        main.log.report( "___________________________________________________________________________" )
        main.case( "Point intents - Randomly bring some core links down and verify ping all" )
        switches = []
        switchesComb = []
        for i in range( main.numMNswitches ):
            switches.append('s%d'%(i+1))
        switchesLinksComb = list(itertools.combinations(switches,2))
        main.randomLinks = random.sample(switchesLinksComb, 5 )
        print main.randomLinks
        main.step( "Cut links on random devices" )

        for switch in main.randomLinks:
            main.Mininet1.link(
                END1=switch[0],
                END2=switch[1],
                OPTION="down")
            time.sleep( link_sleep )

        main.step("Verify link down is discoverd by onos")
        # Giving onos multiple chances to discover link events
        for i in range( main.linkCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
                main.log.info("Giving onos some time...")
                time.sleep( link_sleep )

            topology_output = main.ONOScli1.topology()
            linkDown = main.ONOSbench.checkStatus(
            topology_output, main.numMNswitches, str(
                int( main.numMNlinks ) - 5 * 2 ) )
            if linkDown:
                break

        utilities.assert_equals(
            expect=main.TRUE,
            actual=linkDown,
            onpass="Link down discovered properly",
            onfail="Link down was not discovered in " +
            str( link_sleep * main.linkCheck ) +
            " seconds" )

        main.step("Verify intents are installed")
        # Giving onos multiple chances to install intents
        for i in range( main.intentCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
            main.log.info("Giving onos some time...")
            time.sleep( main.checkIntentsDelay )

            intentState = main.TRUE
            for e in range(int(main.numCtrls)):
                main.log.info( "Checking intents on CLI %s" % (e+1) )
                intentState = main.CLIs[e].checkIntentState( intentsId = main.intentIds ) and\
                        intentState
                if not intentState:
                    main.log.warn( "Not all intents installed" )
            if intentState:
                break
        else:
            #Dumping intent summary
            main.log.info( "**** Intent Summary ****\n" + str(main.ONOScli1.intents( jsonFormat=False, summary=True)) )


        utilities.assert_equals( expect=main.TRUE, actual=intentState,
                                 onpass="INTENTS INSTALLED",
                                 onfail="SOME INTENTS NOT INSTALLED" )

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = linkDown and pingResult and intentState
        utilities.assert_equals( expect=main.TRUE, actual=caseResult,
                                 onpass="Random Link cut Test PASS",
                                 onfail="Random Link cut Test FAIL" )

        # Printing what exactly failed
        if not linkDown:
            main.log.debug( "Link down was not discovered correctly" )
        if not pingResult:
            main.log.debug( "Pingall failed" )
        if not intentState:
            main.log.debug( "Intents are not all installed" )

        if not caseResult and main.failSwitch:
            main.log.report("Stopping test")
            main.stop( email=main.emailOnStop )

    def CASE83( self, main ):
        """
        Bring the core links up that are down and verify ping all ( Point Intents Chordal Topo )
        """
        import random
        link_sleep = int( main.params[ 'timers' ][ 'LinkDiscovery' ] )

        main.log.report(
            "Bring the core links up that are down and verify ping all ( Point Intents-Chordal Topo" )
        main.log.report(
            "__________________________________________________________________" )
        main.case(
            "Point intents - Bring the core links up that are down and verify ping all" )
        main.step( "Bring randomly cut links on devices up" )

        for switch in main.randomLinks:
            main.Mininet1.link(
                END1=switch[0],
                END2=switch[1],
                OPTION="up")
            time.sleep( link_sleep )

        main.step("Verify link up is discoverd by onos")
        # Giving onos multiple chances to discover link events
        for i in range( main.linkCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
                main.log.info("Giving onos some time...")
                time.sleep( link_sleep )

            topology_output = main.ONOScli1.topology()
            linkUp = main.ONOSbench.checkStatus(
                topology_output,
                main.numMNswitches,
                str( main.numMNlinks ) )
            if linkUp:
                break

        utilities.assert_equals(
            expect=main.TRUE,
            actual=linkUp,
            onpass="Link up discovered properly",
            onfail="Link up was not discovered in " +
            str( link_sleep * main.linkCheck ) +
            " seconds" )

        main.step("Verify intents are installed")
        # Giving onos multiple chances to install intents
        for i in range( main.intentCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
            main.log.info("Giving onos some time...")
            time.sleep( main.checkIntentsDelay )

            intentState = main.TRUE
            for e in range(int(main.numCtrls)):
                main.log.info( "Checking intents on CLI %s" % (e+1) )
                intentState = main.CLIs[e].checkIntentState( intentsId = main.intentIds ) and\
                        intentState
                if not intentState:
                    main.log.warn( "Not all intents installed" )
            if intentState:
                break
        else:
            #Dumping intent summary
            main.log.info( "**** Intent Summary ****\n" + str(main.ONOScli1.intents( jsonFormat=False, summary=True)) )


        utilities.assert_equals( expect=main.TRUE, actual=intentState,
                                 onpass="INTENTS INSTALLED",
                                 onfail="SOME INTENTS NOT INSTALLED" )

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = linkUp and pingResult
        utilities.assert_equals( expect=main.TRUE, actual=caseResult,
                                 onpass="Link Up Test PASS",
                                 onfail="Link Up Test FAIL" )
        # Printing what exactly failed
        if not linkUp:
            main.log.debug( "Link up was not discovered correctly" )
        if not pingResult:
            main.log.debug( "Pingall failed" )
        if not intentState:
            main.log.debug( "Intents are not all installed" )

        if not caseResult and main.failSwitch:
            main.log.report("Stopping test")
            main.stop( email=main.emailOnStop )

    def CASE74( self, main ):
        """
        Randomly bring some core links down and verify ping all ( Host Intents-Spine Topo)
        """
        import random
        main.randomLink1 = []
        main.randomLink2 = []
        main.randomLink3 = []
        main.randomLink4 = []
        link1End1 = main.params[ 'SPINECORELINKS' ][ 'linkS9' ]
        link1End2top = main.params[ 'SPINECORELINKS' ][ 'linkS9top' ].split( ',' )
        link1End2bot = main.params[ 'SPINECORELINKS' ][ 'linkS9bot' ].split( ',' )
        link2End1 = main.params[ 'SPINECORELINKS' ][ 'linkS10' ]
        link2End2top = main.params[ 'SPINECORELINKS' ][ 'linkS10top' ].split( ',' )
        link2End2bot = main.params[ 'SPINECORELINKS' ][ 'linkS10bot' ].split( ',' )
        link_sleep = int( main.params[ 'timers' ][ 'LinkDiscovery' ] )

        main.log.report( "Bring some core links down and verify ping all (Host Intents-Spine Topo)" )
        main.log.report( "___________________________________________________________________________" )
        main.log.case( "Bring some core links down and verify ping all (Host Intents-Spine Topo)" )

        main.step( "Bring some core links down" )
        linkIndex = range(4)
        linkIndexS9 = random.sample(linkIndex,1)[0]
        linkIndex.remove(linkIndexS9)
        linkIndexS10 = random.sample(linkIndex,1)[0]
        main.randomLink1 = link1End2top[linkIndexS9]
        main.randomLink2 = link2End2top[linkIndexS10]
        main.randomLink3 = random.sample(link1End2bot,1)[0]
        main.randomLink4 = random.sample(link2End2bot,1)[0]

        # Work around for link state propagation delay. Added some sleep time.
        # main.Mininet1.link( END1=link1End1, END2=main.randomLink1, OPTION="down" )
        # main.Mininet1.link( END1=link2End1, END2=main.randomLink2, OPTION="down" )
        main.Mininet1.link( END1=link1End1, END2=main.randomLink3, OPTION="down" )
        time.sleep( link_sleep )
        main.Mininet1.link( END1=link2End1, END2=main.randomLink4, OPTION="down" )
        time.sleep( link_sleep )

        main.step("Verify link down is discoverd by onos")
        # Giving onos multiple chances to discover link events
        for i in range( main.linkCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
                main.log.info("Giving onos some time...")
                time.sleep( link_sleep )

            topology_output = main.ONOScli1.topology()
            linkDown = main.ONOSbench.checkStatus(
            topology_output, main.numMNswitches, str(
                int( main.numMNlinks ) - 4 ))
            if linkDown:
                break

        utilities.assert_equals(
            expect=main.TRUE,
            actual=linkDown,
            onpass="Link down discovered properly",
            onfail="Link down was not discovered in " +
            str( link_sleep * main.linkCheck ) +
            " seconds" )

        main.step("Verify intents are installed")
        # Giving onos multiple chances to install intents
        for i in range( main.intentCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
            main.log.info("Giving onos some time...")
            time.sleep( main.checkIntentsDelay )

            intentState = main.TRUE
            for e in range(int(main.numCtrls)):
                main.log.info( "Checking intents on CLI %s" % (e+1) )
                intentState = main.CLIs[e].checkIntentState( intentsId = main.intentIds ) and\
                        intentState
                if not intentState:
                    main.log.warn( "Not all intents installed" )
            if intentState:
                break
        else:
            #Dumping intent summary
            main.log.info( "**** Intent Summary ****\n" + str(main.ONOScli1.intents( jsonFormat=False, summary=True)) )


        utilities.assert_equals( expect=main.TRUE, actual=intentState,
                                 onpass="INTENTS INSTALLED",
                                 onfail="SOME INTENTS NOT INSTALLED" )

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = linkDown and pingResult and intentState
        utilities.assert_equals( expect=main.TRUE, actual=caseResult,
                                 onpass="Random Link cut Test PASS",
                                 onfail="Random Link cut Test FAIL" )

        # Printing what exactly failed
        if not linkDown:
            main.log.debug( "Link down was not discovered correctly" )
        if not pingResult:
            main.log.debug( "Pingall failed" )
        if not intentState:
            main.log.debug( "Intents are not all installed" )

        if not caseResult and main.failSwitch:
            main.log.report("Stopping test")
            main.stop( email=main.emailOnStop )

    def CASE84( self, main ):
        """
        Bring the core links up that are down and verify ping all ( Host Intents-Spine Topo )
        """
        import random
        link1End1 = main.params[ 'SPINECORELINKS' ][ 'linkS9' ]
        link2End1 = main.params[ 'SPINECORELINKS' ][ 'linkS10' ]
        link_sleep = int( main.params[ 'timers' ][ 'LinkDiscovery' ] )
        main.log.report(
            "Bring the core links up that are down and verify ping all (Host Intents-Spine Topo" )
        main.log.report(
            "__________________________________________________________________" )
        main.case(
            "Host intents - Bring the core links up that are down and verify ping all" )

        main.step( "Bring up the core links that are down" )
        # Work around for link state propagation delay. Added some sleep time.
        # main.Mininet1.link( END1=link1End1, END2=main.randomLink1, OPTION="up" )
        # main.Mininet1.link( END1=link2End1, END2=main.randomLink2, OPTION="up" )
        main.Mininet1.link( END1=link1End1, END2=main.randomLink3, OPTION="up" )
        time.sleep( link_sleep )
        main.Mininet1.link( END1=link2End1, END2=main.randomLink4, OPTION="up" )
        time.sleep( link_sleep )

        main.step("Verify link up is discoverd by onos")
        # Giving onos multiple chances to discover link events
        for i in range( main.linkCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
                main.log.info("Giving onos some time...")
                time.sleep( link_sleep )

            topology_output = main.ONOScli1.topology()
            linkUp = main.ONOSbench.checkStatus(
                topology_output,
                main.numMNswitches,
                str( main.numMNlinks ) )
            if linkUp:
                break

        utilities.assert_equals(
            expect=main.TRUE,
            actual=linkUp,
            onpass="Link up discovered properly",
            onfail="Link up was not discovered in " +
            str( link_sleep * main.linkCheck ) +
            " seconds" )

        main.step("Verify intents are installed")
        # Giving onos multiple chances to install intents
        for i in range( main.intentCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
            main.log.info("Giving onos some time...")
            time.sleep( main.checkIntentsDelay )

            intentState = main.TRUE
            for e in range(int(main.numCtrls)):
                main.log.info( "Checking intents on CLI %s" % (e+1) )
                intentState = main.CLIs[e].checkIntentState( intentsId = main.intentIds ) and\
                        intentState
                if not intentState:
                    main.log.warn( "Not all intents installed" )
            if intentState:
                break
        else:
            #Dumping intent summary
            main.log.info( "**** Intent Summary ****\n" + str(main.ONOScli1.intents( jsonFormat=False, summary=True)) )


        utilities.assert_equals( expect=main.TRUE, actual=intentState,
                                 onpass="INTENTS INSTALLED",
                                 onfail="SOME INTENTS NOT INSTALLED" )

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = linkUp and pingResult
        utilities.assert_equals( expect=main.TRUE, actual=caseResult,
                                 onpass="Link Up Test PASS",
                                 onfail="Link Up Test FAIL" )
        # Printing what exactly failed
        if not linkUp:
            main.log.debug( "Link up was not discovered correctly" )
        if not pingResult:
            main.log.debug( "Pingall failed" )
        if not intentState:
            main.log.debug( "Intents are not all installed" )

        if not caseResult and main.failSwitch:
            main.log.report("Stopping test")
            main.stop( email=main.emailOnStop )

    def CASE75( self, main ):
        """
        Randomly bring some core links down and verify ping all ( Point Intents-Spine Topo)
        """
        import random
        main.randomLink1 = []
        main.randomLink2 = []
        main.randomLink3 = []
        main.randomLink4 = []
        link1End1 = main.params[ 'SPINECORELINKS' ][ 'linkS9' ]
        link1End2top = main.params[ 'SPINECORELINKS' ][ 'linkS9top' ].split( ',' )
        link1End2bot = main.params[ 'SPINECORELINKS' ][ 'linkS9bot' ].split( ',' )
        link2End1 = main.params[ 'SPINECORELINKS' ][ 'linkS10' ]
        link2End2top = main.params[ 'SPINECORELINKS' ][ 'linkS10top' ].split( ',' )
        link2End2bot = main.params[ 'SPINECORELINKS' ][ 'linkS10bot' ].split( ',' )
        link_sleep = int( main.params[ 'timers' ][ 'LinkDiscovery' ] )
        main.pingTimeout = 400

        main.log.report( "Bring some core links down and verify ping all (Point Intents-Spine Topo)" )
        main.log.report( "___________________________________________________________________________" )
        main.case( "Bring some core links down and verify ping all (Point Intents-Spine Topo)" )

        main.step( "Bring some core links down" )
        linkIndex = range(4)
        linkIndexS9 = random.sample(linkIndex,1)[0]
        linkIndex.remove(linkIndexS9)
        linkIndexS10 = random.sample(linkIndex,1)[0]
        main.randomLink1 = link1End2top[linkIndexS9]
        main.randomLink2 = link2End2top[linkIndexS10]
        main.randomLink3 = random.sample(link1End2bot,1)[0]
        main.randomLink4 = random.sample(link2End2bot,1)[0]

        # Work around for link state propagation delay. Added some sleep time.
        # main.Mininet1.link( END1=link1End1, END2=main.randomLink1, OPTION="down" )
        # main.Mininet1.link( END1=link2End1, END2=main.randomLink2, OPTION="down" )
        main.Mininet1.link( END1=link1End1, END2=main.randomLink3, OPTION="down" )
        time.sleep( link_sleep )
        main.Mininet1.link( END1=link2End1, END2=main.randomLink4, OPTION="down" )
        time.sleep( link_sleep )

        main.step("Verify link down is discoverd by onos")
        # Giving onos multiple chances to discover link events
        for i in range( main.linkCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
                main.log.info("Giving onos some time...")
                time.sleep( link_sleep )

            topology_output = main.ONOScli1.topology()
            linkDown = main.ONOSbench.checkStatus(
            topology_output, main.numMNswitches, str(
                int( main.numMNlinks ) - 4 ))
            if linkDown:
                break

        utilities.assert_equals(
            expect=main.TRUE,
            actual=linkDown,
            onpass="Link down discovered properly",
            onfail="Link down was not discovered in " +
            str( link_sleep * main.linkCheck ) +
            " seconds" )

        main.step("Verify intents are installed")
        # Giving onos multiple chances to install intents
        for i in range( main.intentCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
            main.log.info("Giving onos some time...")
            time.sleep( main.checkIntentsDelay )

            intentState = main.TRUE
            for e in range(int(main.numCtrls)):
                main.log.info( "Checking intents on CLI %s" % (e+1) )
                intentState = main.CLIs[e].checkIntentState( intentsId = main.intentIds ) and\
                        intentState
                if not intentState:
                    main.log.warn( "Not all intents installed" )
            if intentState:
                break
        else:
            #Dumping intent summary
            main.log.info( "**** Intent Summary ****\n" + str(main.ONOScli1.intents( jsonFormat=False, summary=True)) )


        utilities.assert_equals( expect=main.TRUE, actual=intentState,
                                 onpass="INTENTS INSTALLED",
                                 onfail="SOME INTENTS NOT INSTALLED" )

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = linkDown and pingResult and intentState
        utilities.assert_equals( expect=main.TRUE, actual=caseResult,
                                 onpass="Random Link cut Test PASS",
                                 onfail="Random Link cut Test FAIL" )

        # Printing what exactly failed
        if not linkDown:
            main.log.debug( "Link down was not discovered correctly" )
        if not pingResult:
            main.log.debug( "Pingall failed" )
        if not intentState:
            main.log.debug( "Intents are not all installed" )

        if not caseResult and main.failSwitch:
            main.log.report("Stopping test")
            main.stop( email=main.emailOnStop )

    def CASE85( self, main ):
        """
        Bring the core links up that are down and verify ping all ( Point Intents-Spine Topo )
        """
        import random
        link1End1 = main.params[ 'SPINECORELINKS' ][ 'linkS9' ]
        link2End1 = main.params[ 'SPINECORELINKS' ][ 'linkS10' ]
        link_sleep = int( main.params[ 'timers' ][ 'LinkDiscovery' ] )
        main.log.report(
            "Bring the core links up that are down and verify ping all (Point Intents-Spine Topo" )
        main.log.report(
            "__________________________________________________________________" )
        main.case(
            "Point intents - Bring the core links up that are down and verify ping all" )

        main.step( "Bring up the core links that are down" )
        # Work around for link state propagation delay. Added some sleep time.
        # main.Mininet1.link( END1=link1End1, END2=main.randomLink1, OPTION="up" )
        # main.Mininet1.link( END1=link2End1, END2=main.randomLink2, OPTION="up" )
        main.Mininet1.link( END1=link1End1, END2=main.randomLink3, OPTION="up" )
        time.sleep( link_sleep )
        main.Mininet1.link( END1=link2End1, END2=main.randomLink4, OPTION="up" )
        time.sleep( link_sleep )

        main.step("Verify link up is discoverd by onos")
        # Giving onos multiple chances to discover link events
        for i in range( main.linkCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
                main.log.info("Giving onos some time...")
                time.sleep( link_sleep )

            topology_output = main.ONOScli1.topology()
            linkUp = main.ONOSbench.checkStatus(
                topology_output,
                main.numMNswitches,
                str( main.numMNlinks ) )
            if linkUp:
                break

        utilities.assert_equals(
            expect=main.TRUE,
            actual=linkUp,
            onpass="Link up discovered properly",
            onfail="Link up was not discovered in " +
            str( link_sleep * main.linkCheck ) +
            " seconds" )

        main.step("Verify intents are installed")
        # Giving onos multiple chances to install intents
        for i in range( main.intentCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
            main.log.info("Giving onos some time...")
            time.sleep( main.checkIntentsDelay )

            intentState = main.TRUE
            for e in range(int(main.numCtrls)):
                main.log.info( "Checking intents on CLI %s" % (e+1) )
                intentState = main.CLIs[e].checkIntentState( intentsId = main.intentIds ) and\
                        intentState
                if not intentState:
                    main.log.warn( "Not all intents installed" )
            if intentState:
                break
        else:
            #Dumping intent summary
            main.log.info( "**** Intent Summary ****\n" + str(main.ONOScli1.intents( jsonFormat=False, summary=True)) )


        utilities.assert_equals( expect=main.TRUE, actual=intentState,
                                 onpass="INTENTS INSTALLED",
                                 onfail="SOME INTENTS NOT INSTALLED" )

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = linkUp and pingResult
        utilities.assert_equals( expect=main.TRUE, actual=caseResult,
                                 onpass="Link Up Test PASS",
                                 onfail="Link Up Test FAIL" )
        # Printing what exactly failed
        if not linkUp:
            main.log.debug( "Link up was not discovered correctly" )
        if not pingResult:
            main.log.debug( "Pingall failed" )
        if not intentState:
            main.log.debug( "Intents are not all installed" )

        if not caseResult and main.failSwitch:
            main.log.report("Stopping test")
            main.stop( email=main.emailOnStop )

    def CASE170( self ):
        """
        IPv6 ping all with some core links down( Host Intents-Att Topo)
        """
        main.log.report( "IPv6 ping all with some core links down( Host Intents-Att Topo )" )
        main.log.report( "_________________________________________________" )
        import itertools
        import time
        main.case( "IPv6 ping all with some core links down( Host Intents-Att Topo )" )
        main.step( "Verify IPv6 Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        if not pingResult:
            main.log.warn("Failed to ping Ipv6 hosts. Retrying...")
            pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for IPv6 Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = pingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="IPv6 Ping across 300 host intents test PASS",
            onfail="IPv6 Ping across 300 host intents test FAIL" )

    def CASE180( self ):
        """
        IPv6 ping all with after core links back up( Host Intents-Att Topo)
        """
        main.log.report( "IPv6 ping all with after core links back up( Host Intents-Att Topo )" )
        main.log.report( "_________________________________________________" )
        import itertools
        import time
        main.case( "IPv6 ping all with after core links back up( Host Intents-Att Topo )" )
        main.step( "Verify IPv6 Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        if not pingResult:
            main.log.warn("First ping failed. Retrying...")
            time1 = time.time()
            pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for IPv6 Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = pingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="IPv6 Ping across 300 host intents test PASS",
            onfail="IPv6 Ping across 300 host intents test FAIL" )

    def CASE171( self ):
        """
        IPv6 ping all with some core links down( Point Intents-Att Topo)
        """
        main.log.report( "IPv6 ping all with some core links down( Point Intents-Att Topo )" )
        main.log.report( "_________________________________________________" )
        import itertools
        import time
        main.case( "IPv6 ping all with some core links down( Point Intents-Att Topo )" )
        main.step( "Verify IPv6 Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        if not pingResult:
            main.log.warn("First ping failed. Retrying...")
            time1 = time.time()
            pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for IPv6 Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = pingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="IPv6 Ping across 600 point intents test PASS",
            onfail="IPv6 Ping across 600 point intents test FAIL" )

    def CASE181( self ):
        """
        IPv6 ping all with after core links back up( Point Intents-Att Topo)
        """
        main.log.report( "IPv6 ping all with after core links back up( Point Intents-Att Topo )" )
        main.log.report( "_________________________________________________" )
        import itertools
        import time
        main.case( "IPv6 ping all with after core links back up( Point Intents-Att Topo )" )
        main.step( "Verify IPv6 Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        if not pingResult:
            main.log.warn("First ping failed. Retrying...")
            time1 = time.time()
            pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for IPv6 Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = pingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="IPv6 Ping across 600 Point intents test PASS",
            onfail="IPv6 Ping across 600 Point intents test FAIL" )

    def CASE172( self ):
        """
        IPv6 ping all with some core links down( Host Intents-Chordal Topo)
        """
        main.log.report( "IPv6 ping all with some core links down( Host Intents-Chordal Topo )" )
        main.log.report( "_________________________________________________" )
        import itertools
        import time
        main.case( "IPv6 ping all with some core links down( Host Intents-Chordal Topo )" )
        main.step( "Verify IPv6 Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        if not pingResult:
            main.log.warn("First ping failed. Retrying...")
            time1 = time.time()
            pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for IPv6 Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = pingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="IPv6 Ping across 300 host intents test PASS",
            onfail="IPv6 Ping across 300 host intents test FAIL" )

    def CASE182( self ):
        """
        IPv6 ping all with after core links back up( Host Intents-Chordal Topo)
        """
        main.log.report( "IPv6 ping all with after core links back up( Host Intents-Chordal Topo )" )
        main.log.report( "_________________________________________________" )
        import itertools
        import time
        main.case( "IPv6 ping all with after core links back up( Host Intents-Chordal Topo )" )
        main.step( "Verify IPv6 Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        if not pingResult:
            main.log.warn("First ping failed. Retrying...")
            time1 = time.time()
            pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for IPv6 Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = pingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="IPv6 Ping across 300 host intents test PASS",
            onfail="IPv6 Ping across 300 host intents test FAIL" )

    def CASE173( self ):
        """
        IPv6 ping all with some core links down( Point Intents-Chordal Topo)
        """
        main.log.report( "IPv6 ping all with some core links down( Point Intents-Chordal Topo )" )
        main.log.report( "_________________________________________________" )
        import itertools
        import time
        main.case( "IPv6 ping all with some core links down( Point Intents-Chordal Topo )" )
        main.step( "Verify IPv6 Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        if not pingResult:
            main.log.warn("First ping failed. Retrying...")
            time1 = time.time()
            pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for IPv6 Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = pingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="IPv6 Ping across 600 point intents test PASS",
            onfail="IPv6 Ping across 600 point intents test FAIL" )

    def CASE183( self ):
        """
        IPv6 ping all with after core links back up( Point Intents-Chordal Topo)
        """
        main.log.report( "IPv6 ping all with after core links back up( Point Intents-Chordal Topo )" )
        main.log.report( "_________________________________________________" )
        import itertools
        import time
        main.case( "IPv6 ping all with after core links back up( Point Intents-Chordal Topo )" )
        main.step( "Verify IPv6 Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        if not pingResult:
            main.log.warn("First ping failed. Retrying...")
            time1 = time.time()
            pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for IPv6 Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = pingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="IPv6 Ping across 600 Point intents test PASS",
            onfail="IPv6 Ping across 600 Point intents test FAIL" )

    def CASE174( self ):
        """
        IPv6 ping all with some core links down( Host Intents-Spine Topo)
        """
        main.log.report( "IPv6 ping all with some core links down( Host Intents-Spine Topo )" )
        main.log.report( "_________________________________________________" )
        import itertools
        import time
        main.case( "IPv6 ping all with some core links down( Host Intents-Spine Topo )" )
        main.step( "Verify IPv6 Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        if not pingResult:
            main.log.warn("First ping failed. Retrying...")
            time1 = time.time()
            pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for IPv6 Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = pingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="IPv6 Ping across 2278 host intents test PASS",
            onfail="IPv6 Ping across 2278 host intents test FAIL" )

    def CASE184( self ):
        """
        IPv6 ping all with after core links back up( Host Intents-Spine Topo)
        """
        main.log.report( "IPv6 ping all with after core links back up( Host Intents-Spine Topo )" )
        main.log.report( "_________________________________________________" )
        import itertools
        import time
        main.case( "IPv6 ping all with after core links back up( Host Intents-Spine Topo )" )
        main.step( "Verify IPv6 Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        if not pingResult:
            main.log.warn("First ping failed. Retrying...")
            time1 = time.time()
            pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for IPv6 Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = pingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="IPv6 Ping across 2278 host intents test PASS",
            onfail="IPv6 Ping across 2278 host intents test FAIL" )

    def CASE175( self ):
        """
        IPv6 ping all with some core links down( Point Intents-Spine Topo)
        """
        main.log.report( "IPv6 ping all with some core links down( Point Intents-Spine Topo )" )
        main.log.report( "_________________________________________________" )
        import itertools
        import time
        main.case( "IPv6 ping all with some core links down( Point Intents-Spine Topo )" )
        main.step( "Verify IPv6 Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        if not pingResult:
            main.log.warn("First ping failed. Retrying...")
            time1 = time.time()
            pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for IPv6 Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = pingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="IPv6 Ping across 4556 point intents test PASS",
            onfail="IPv6 Ping across 4556 point intents test FAIL" )

    def CASE185( self ):
        """
        IPv6 ping all with after core links back up( Point Intents-Spine Topo)
        """
        main.log.report( "IPv6 ping all with after core links back up( Point Intents-Spine Topo )" )
        main.log.report( "_________________________________________________" )
        import itertools
        import time
        main.case( "IPv6 ping all with after core links back up( Point Intents-Spine Topo )" )
        main.step( "Verify IPv6 Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        if not pingResult:
            main.log.warn("First ping failed. Retrying...")
            time1 = time.time()
            pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for IPv6 Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = pingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="IPv6 Ping across 4556 Point intents test PASS",
            onfail="IPv6 Ping across 4556 Point intents test FAIL" )

    def CASE90( self ):
        """
        Install 600 point intents and verify ping all (Att Topology)
        """
        main.log.report( "Add 600 point intents and verify pingall (Att Topology)" )
        main.log.report( "_______________________________________" )
        import itertools
        import time
        main.case( "Install 600 point intents" )
        main.step( "Add point Intents" )
        intentResult = main.TRUE
        deviceCombos = list( itertools.permutations( main.deviceDPIDs, 2 ) )

        intentIdList = []
        time1 = time.time()
        for i in xrange( 0, len( deviceCombos ), int(main.numCtrls) ):
            pool = []
            for cli in main.CLIs:
                if i >= len( deviceCombos ):
                    break
                t = main.Thread( target=cli.addPointIntent,
                        threadID=main.threadID,
                        name="addPointIntent",
                        args=[deviceCombos[i][0],deviceCombos[i][1],1,1,'',main.MACsDict.get(deviceCombos[i][0]),main.MACsDict.get(deviceCombos[i][1])])
                pool.append(t)
                t.start()
                i = i + 1
                main.threadID = main.threadID + 1
            for thread in pool:
                thread.join()
                intentIdList.append(thread.result)
        time2 = time.time()
        main.log.info("Time for adding point intents: %2f seconds" %(time2-time1))

        # Saving intent ids to check intents in later case
        main.intentIds = list(intentIdList)

        main.step("Verify intents are installed")

        # Giving onos multiple chances to install intents
        for i in range( main.intentCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
            main.log.info("Waiting for onos to install intents...")
            time.sleep( main.checkIntentsDelay )

            intentState = main.TRUE
            for e in range(int(main.numCtrls)):
                main.log.info( "Checking intents on CLI %s" % (e+1) )
                intentState = main.CLIs[e].checkIntentState( intentsId = intentIdList ) and\
                        intentState
                if not intentState:
                    main.log.warn( "Not all intents installed" )
            if intentState:
                break
        else:
            #Dumping intent summary
            main.log.info( "Intents:\n" + str( main.ONOScli1.intents( jsonFormat=False, summary=True ) ) )

        utilities.assert_equals( expect=main.TRUE, actual=intentState,
                                 onpass="INTENTS INSTALLED",
                                 onfail="SOME INTENTS NOT INSTALLED" )

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = ( intentState and pingResult )

        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="Install 600 point Intents and Ping All test PASS",
            onfail="Install 600 point Intents and Ping All test FAIL" )

        if not intentState:
            main.log.debug( "Intents failed to install completely" )
        if not pingResult:
            main.log.debug( "Pingall failed" )

        if not caseResult and main.failSwitch:
            main.log.report("Stopping test")
            main.stop( email=main.emailOnStop )

    def CASE91( self ):
        """
        Install 600 point intents and verify ping all (Chordal Topology)
        """
        main.log.report( "Add 600 point intents and verify pingall (Chordal Topology)" )
        main.log.report( "_______________________________________" )
        import itertools
        import time
        main.case( "Install 600 point intents" )
        main.step( "Add point Intents" )
        intentResult = main.TRUE
        deviceCombos = list( itertools.permutations( main.deviceDPIDs, 2 ) )

        intentIdList = []
        time1 = time.time()
        for i in xrange( 0, len( deviceCombos ), int(main.numCtrls) ):
            pool = []
            for cli in main.CLIs:
                if i >= len( deviceCombos ):
                    break
                t = main.Thread( target=cli.addPointIntent,
                        threadID=main.threadID,
                        name="addPointIntent",
                        args=[deviceCombos[i][0],deviceCombos[i][1],1,1,'',main.MACsDict.get(deviceCombos[i][0]),main.MACsDict.get(deviceCombos[i][1])])
                pool.append(t)
                #time.sleep(1)
                t.start()
                i = i + 1
                main.threadID = main.threadID + 1
            for thread in pool:
                thread.join()
                intentIdList.append(thread.result)
        time2 = time.time()
        main.log.info( "Time for adding point intents: %2f seconds" %(time2-time1) )

        # Saving intent ids to check intents in later case
        main.intentIds = list(intentIdList)

        main.step("Verify intents are installed")

        # Giving onos multiple chances to install intents
        for i in range( main.intentCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
            main.log.info("Waiting for onos to install intents...")
            time.sleep( main.checkIntentsDelay )

            intentState = main.TRUE
            for e in range(int(main.numCtrls)):
                main.log.info( "Checking intents on CLI %s" % (e+1) )
                intentState = main.CLIs[e].checkIntentState( intentsId = intentIdList ) and\
                        intentState
                if not intentState:
                    main.log.warn( "Not all intents installed" )
            if intentState:
                break
        else:
            #Dumping intent summary
            main.log.info( "Intents:\n" + str( main.ONOScli1.intents( jsonFormat=False, summary=True ) ) )

        utilities.assert_equals( expect=main.TRUE, actual=intentState,
                                 onpass="INTENTS INSTALLED",
                                 onfail="SOME INTENTS NOT INSTALLED" )

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = ( intentState and pingResult )

        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="Install 600 point Intents and Ping All test PASS",
            onfail="Install 600 point Intents and Ping All test FAIL" )

        if not intentState:
            main.log.debug( "Intents failed to install completely" )
        if not pingResult:
            main.log.debug( "Pingall failed" )

        if not caseResult and main.failSwitch:
            main.log.report("Stopping test")
            main.stop( email=main.emailOnStop )

    def CASE92( self ):
        """
        Install 4556 point intents and verify ping all (Spine Topology)
        """
        main.log.report( "Add 4556 point intents and verify pingall (Spine Topology)" )
        main.log.report( "_______________________________________" )
        import itertools
        import time
        main.case( "Install 4556 point intents" )
        main.step( "Add point Intents" )
        intentResult = main.TRUE
        main.pingTimeout = 600
        for i in range(len(main.hostMACs)):
            main.MACsDict[main.deviceDPIDs[i+10]] = main.hostMACs[i].split('/')[0]
        print main.MACsDict
        deviceCombos = list( itertools.permutations( main.deviceDPIDs[10:], 2 ) )
        intentIdList = []
        time1 = time.time()
        for i in xrange( 0, len( deviceCombos ), int(main.numCtrls) ):
            pool = []
            for cli in main.CLIs:
                if i >= len( deviceCombos ):
                    break
                t = main.Thread( target=cli.addPointIntent,
                        threadID=main.threadID,
                        name="addPointIntent",
                        args=[deviceCombos[i][0],deviceCombos[i][1],1,1,'',main.MACsDict.get(deviceCombos[i][0]),main.MACsDict.get(deviceCombos[i][1])])
                pool.append(t)
                #time.sleep(1)
                t.start()
                i = i + 1
                main.threadID = main.threadID + 1
            for thread in pool:
                thread.join()
                intentIdList.append(thread.result)
        time2 = time.time()
        main.log.info("Time for adding point intents: %2f seconds" %(time2-time1))

        # Saving intent ids to check intents in later case
        main.intentIds = list(intentIdList)

        main.step("Verify intents are installed")

        # Giving onos multiple chances to install intents
        for i in range( main.intentCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
            main.log.info("Waiting for onos to install intents...")
            time.sleep( main.checkIntentsDelay )

            intentState = main.TRUE
            for e in range(int(main.numCtrls)):
                main.log.info( "Checking intents on CLI %s" % (e+1) )
                intentState = main.CLIs[e].checkIntentState( intentsId = intentIdList ) and\
                        intentState
                if not intentState:
                    main.log.warn( "Not all intents installed" )
            if intentState:
                break
        else:
            #Dumping intent summary
            main.log.info( "Intents:\n" + str( main.ONOScli1.intents( jsonFormat=False, summary=True ) ) )

        utilities.assert_equals( expect=main.TRUE, actual=intentState,
                                 onpass="INTENTS INSTALLED",
                                 onfail="SOME INTENTS NOT INSTALLED" )

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = ( intentState and pingResult )

        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="Install 4556 point Intents and Ping All test PASS",
            onfail="Install 4556 point Intents and Ping All test FAIL" )

        if not intentState:
            main.log.debug( "Intents failed to install completely" )
        if not pingResult:
            main.log.debug( "Pingall failed" )

        if not caseResult and main.failSwitch:
            main.log.report("Stopping test")
            main.stop( email=main.emailOnStop )

    def CASE93( self ):
        """
        Install multi-single point intents and verify Ping all works
        for att topology
        """
        import copy
        import time
        from collections import Counter
        main.log.report( "Install multi-single point intents and verify Ping all" )
        main.log.report( "___________________________________________" )
        main.case( "Install multi-single point intents and Ping all" )
        deviceDPIDsCopy = copy.copy(main.deviceDPIDs)
        portIngressList = ['1']*(len(deviceDPIDsCopy) - 1)
        intentIdList = []
        main.log.info( "MACsDict" + str(main.MACsDict) )
        time1 = time.time()
        for i in xrange(0,len(deviceDPIDsCopy),int(main.numCtrls)):
            pool = []
            for cli in main.CLIs:
                egressDevice = deviceDPIDsCopy[i]
                ingressDeviceList = copy.copy(deviceDPIDsCopy)
                ingressDeviceList.remove(egressDevice)
                if i >= len( deviceDPIDsCopy ):
                    break
                t = main.Thread( target=cli.addMultipointToSinglepointIntent,
                        threadID=main.threadID,
                        name="addMultipointToSinglepointIntent",
                        args =[ingressDeviceList,egressDevice,portIngressList,'1','','',main.MACsDict.get(egressDevice)])
                pool.append(t)
                t.start()
                i = i + 1
                main.threadID = main.threadID + 1
            for thread in pool:
                thread.join()
                intentIdList.append(thread.result)
        time2 = time.time()
        main.log.info("Time for adding point intents: %2f seconds" %(time2-time1))

        main.step("Verify intents are installed")

        # Giving onos multiple chances to install intents
        for i in range( main.intentCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
            main.log.info("Waiting for onos to install intents...")
            time.sleep( main.checkIntentsDelay )

            intentState = main.TRUE
            for e in range(int(main.numCtrls)):
                main.log.info( "Checking intents on CLI %s" % (e+1) )
                intentState = main.CLIs[e].checkIntentState( intentsId = intentIdList ) and\
                        intentState
                if not intentState:
                    main.log.warn( "Not all intents installed" )
            if intentState:
                break
        else:
            #Dumping intent summary
            main.log.info( "Intents:\n" + str( main.ONOScli1.intents( jsonFormat=False, summary=True ) ) )

        utilities.assert_equals( expect=main.TRUE, actual=intentState,
                                 onpass="INTENTS INSTALLED",
                                 onfail="SOME INTENTS NOT INSTALLED" )

        main.step("Verify flows are all added")

        for i in range( main.flowCheck ):
            if i != 0:
                main.log.warn( "verification failed. Retrying..." )
            main.log.info( "Waiting for onos to add flows..." )
            time.sleep( main.checkFlowsDelay )

            flowState = main.TRUE
            for cli in main.CLIs:
                flowState = cli.checkFlowState()
                if not flowState:
                    main.log.warn( "Not all flows added" )
            if flowState:
                break
        else:
            #Dumping summary
            main.log.info( "Summary:\n" + str( main.ONOScli1.summary(jsonFormat=False) ) )

        utilities.assert_equals( expect=main.TRUE, actual=flowState,
                                 onpass="FLOWS INSTALLED",
                                 onfail="SOME FLOWS NOT ADDED" )

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )

        caseResult = ( checkFlowsState and pingResult and intentState )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="Install 25 multi to single point Intents and Ping All test PASS",
            onfail="Install 25 multi to single point Intents and Ping All test FAIL" )

        if not intentState:
            main.log.debug( "Intents failed to install completely" )
        if not pingResult:
            main.log.debug( "Pingall failed" )
        if not checkFlowsState:
            main.log.debug( "Flows failed to add completely" )

        if not caseResult and main.failSwitch:
            main.log.report("Stopping test")
            main.stop( email=main.emailOnStop )

    def CASE94( self ):
        """
        Install multi-single point intents and verify Ping all works
        for Chordal topology
        """
        import copy
        import time
        main.log.report( "Install multi-single point intents and verify Ping all" )
        main.log.report( "___________________________________________" )
        main.case( "Install multi-single point intents and Ping all" )
        deviceDPIDsCopy = copy.copy(main.deviceDPIDs)
        portIngressList = ['1']*(len(deviceDPIDsCopy) - 1)
        intentIdList = []
        main.log.info( "MACsDict" + str(main.MACsDict) )
        time1 = time.time()
        for i in xrange(0,len(deviceDPIDsCopy),int(main.numCtrls)):
            pool = []
            for cli in main.CLIs:
                egressDevice = deviceDPIDsCopy[i]
                ingressDeviceList = copy.copy(deviceDPIDsCopy)
                ingressDeviceList.remove(egressDevice)
                if i >= len( deviceDPIDsCopy ):
                    break
                t = main.Thread( target=cli.addMultipointToSinglepointIntent,
                        threadID=main.threadID,
                        name="addMultipointToSinglepointIntent",
                        args =[ingressDeviceList,egressDevice,portIngressList,'1','','',main.MACsDict.get(egressDevice)])
                pool.append(t)
                t.start()
                i = i + 1
                main.threadID = main.threadID + 1
            for thread in pool:
                thread.join()
                intentIdList.append(thread.result)
        time2 = time.time()
        main.log.info("Time for adding point intents: %2f seconds" %(time2-time1))

        main.step("Verify intents are installed")

        # Giving onos multiple chances to install intents
        for i in range( main.intentCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
            main.log.info("Waiting for onos to install intents...")
            time.sleep( main.checkIntentsDelay )

            intentState = main.TRUE
            for e in range(int(main.numCtrls)):
                main.log.info( "Checking intents on CLI %s" % (e+1) )
                intentState = main.CLIs[e].checkIntentState( intentsId = intentIdList ) and\
                        intentState
                if not intentState:
                    main.log.warn( "Not all intents installed" )
            if intentState:
                break
        else:
            #Dumping intent summary
            main.log.info( "Intents:\n" + str( main.ONOScli1.intents( jsonFormat=False, summary=True ) ) )

        utilities.assert_equals( expect=main.TRUE, actual=intentState,
                                 onpass="INTENTS INSTALLED",
                                 onfail="SOME INTENTS NOT INSTALLED" )

        main.step("Verify flows are all added")

        for i in range( main.flowCheck ):
            if i != 0:
                main.log.warn( "verification failed. Retrying..." )
            main.log.info( "Waiting for onos to add flows..." )
            time.sleep( main.checkFlowsDelay )

            flowState = main.TRUE
            for cli in main.CLIs:
                flowState = cli.checkFlowState()
                if not flowState:
                    main.log.warn( "Not all flows added" )
            if flowState:
                break
        else:
            #Dumping summary
            main.log.info( "Summary:\n" + str( main.ONOScli1.summary(jsonFormat=False) ) )

        utilities.assert_equals( expect=main.TRUE, actual=flowState,
                                 onpass="FLOWS INSTALLED",
                                 onfail="SOME FLOWS NOT ADDED" )

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )

        caseResult = ( checkFlowsState and pingResult and intentState )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="Install 25 multi to single point Intents and Ping All test PASS",
            onfail="Install 25 multi to single point Intents and Ping All test FAIL" )

        if not intentState:
            main.log.debug( "Intents failed to install completely" )
        if not pingResult:
            main.log.debug( "Pingall failed" )
        if not checkFlowsState:
            main.log.debug( "Flows failed to add completely" )

        if not caseResult and main.failSwitch:
            main.log.report("Stopping test")
            main.stop( email=main.emailOnStop )

    def CASE95( self ):
        """
        Install multi-single point intents and verify Ping all works
        for Spine topology
        """
        import copy
        import time
        main.log.report( "Install multi-single point intents and verify Ping all" )
        main.log.report( "___________________________________________" )
        main.case( "Install multi-single point intents and Ping all" )
        deviceDPIDsCopy = copy.copy(main.deviceDPIDs)
        portIngressList = ['1']*(len(deviceDPIDsCopy) - 1)
        intentIdList = []
        main.log.info( "MACsDict" + str(main.MACsDict) )
        time1 = time.time()
        for i in xrange(0,len(deviceDPIDsCopy),int(main.numCtrls)):
            pool = []
            for cli in main.CLIs:
                egressDevice = deviceDPIDsCopy[i]
                ingressDeviceList = copy.copy(deviceDPIDsCopy)
                ingressDeviceList.remove(egressDevice)
                if i >= len( deviceDPIDsCopy ):
                    break
                t = main.Thread( target=cli.addMultipointToSinglepointIntent,
                        threadID=main.threadID,
                        name="addMultipointToSinglepointIntent",
                        args =[ingressDeviceList,egressDevice,portIngressList,'1','','',main.MACsDict.get(egressDevice)])
                pool.append(t)
                t.start()
                i = i + 1
                main.threadID = main.threadID + 1
            for thread in pool:
                thread.join()
                intentIdList.append(thread.result)
        time2 = time.time()
        main.log.info("Time for adding point intents: %2f seconds" %(time2-time1))

        main.step("Verify intents are installed")

        # Giving onos multiple chances to install intents
        for i in range( main.intentCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
            main.log.info("Waiting for onos to install intents...")
            time.sleep( main.checkIntentsDelay )

            intentState = main.TRUE
            for e in range(int(main.numCtrls)):
                main.log.info( "Checking intents on CLI %s" % (e+1) )
                intentState = main.CLIs[e].checkIntentState( intentsId = intentIdList ) and\
                        intentState
                if not intentState:
                    main.log.warn( "Not all intents installed" )
            if intentState:
                break
        else:
            #Dumping intent summary
            main.log.info( "Intents:\n" + str( main.ONOScli1.intents( jsonFormat=False, summary=True ) ) )

        utilities.assert_equals( expect=main.TRUE, actual=intentState,
                                 onpass="INTENTS INSTALLED",
                                 onfail="SOME INTENTS NOT INSTALLED" )

        main.step("Verify flows are all added")

        for i in range( main.flowCheck ):
            if i != 0:
                main.log.warn( "verification failed. Retrying..." )
            main.log.info( "Waiting for onos to add flows..." )
            time.sleep( main.checkFlowsDelay )

            flowState = main.TRUE
            for cli in main.CLIs:
                flowState = cli.checkFlowState()
                if not flowState:
                    main.log.warn( "Not all flows added" )
            if flowState:
                break
        else:
            #Dumping summary
            main.log.info( "Summary:\n" + str( main.ONOScli1.summary(jsonFormat=False) ) )

        utilities.assert_equals( expect=main.TRUE, actual=flowState,
                                 onpass="FLOWS INSTALLED",
                                 onfail="SOME FLOWS NOT ADDED" )

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )

        caseResult = ( checkFlowsState and pingResult and intentState )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="Install 25 multi to single point Intents and Ping All test PASS",
            onfail="Install 25 multi to single point Intents and Ping All test FAIL" )

        if not intentState:
            main.log.debug( "Intents failed to install completely" )
        if not pingResult:
            main.log.debug( "Pingall failed" )
        if not checkFlowsState:
            main.log.debug( "Flows failed to add completely" )

        if not caseResult and main.failSwitch:
            main.log.report("Stopping test")
            main.stop( email=main.emailOnStop )

    def CASE96( self ):
        """
        Install single-multi point intents and verify Ping all works
        for att topology
        """
        import copy
        main.log.report( "Install single-multi point intents and verify Ping all" )
        main.log.report( "___________________________________________" )
        main.case( "Install single-multi point intents and Ping all" )
        deviceDPIDsCopy = copy.copy(main.deviceDPIDs)
        portEgressList = ['1']*(len(deviceDPIDsCopy) - 1)
        intentIdList = []
        main.log.info( "MACsDict" + str(main.MACsDict) )
        time1 = time.time()
        for i in xrange(0,len(deviceDPIDsCopy),int(main.numCtrls)):
            pool = []
            for cli in main.CLIs:
                ingressDevice = deviceDPIDsCopy[i]
                egressDeviceList = copy.copy(deviceDPIDsCopy)
                egressDeviceList.remove(ingressDevice)
                if i >= len( deviceDPIDsCopy ):
                    break
                t = main.Thread( target=cli.addSinglepointToMultipointIntent,
                        threadID=main.threadID,
                        name="addSinglepointToMultipointIntent",
                        args =[ingressDevice,egressDeviceList,'1',portEgressList,'',main.MACsDict.get(ingressDevice)])
                pool.append(t)
                t.start()
                i = i + 1
                main.threadID = main.threadID + 1
            for thread in pool:
                thread.join()
                intentIdList.append(thread.result)
        time2 = time.time()
        main.log.info("Time for adding point intents: %2f seconds" %(time2-time1))

        main.step("Verify intents are installed")

        # Giving onos multiple chances to install intents
        for i in range( main.intentCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
            main.log.info("Waiting for onos to install intents...")
            time.sleep( main.checkIntentsDelay )

            intentState = main.TRUE
            for e in range(int(main.numCtrls)):
                main.log.info( "Checking intents on CLI %s" % (e+1) )
                intentState = main.CLIs[e].checkIntentState( intentsId = intentIdList ) and\
                        intentState
                if not intentState:
                    main.log.warn( "Not all intents installed" )
            if intentState:
                break
        else:
            #Dumping intent summary
            main.log.info( "Intents:\n" + str( main.ONOScli1.intents( jsonFormat=False, summary=True ) ) )

        utilities.assert_equals( expect=main.TRUE, actual=intentState,
                                 onpass="INTENTS INSTALLED",
                                 onfail="SOME INTENTS NOT INSTALLED" )

        main.step("Verify flows are all added")

        for i in range( main.flowCheck ):
            if i != 0:
                main.log.warn( "verification failed. Retrying..." )
            main.log.info( "Waiting for onos to add flows..." )
            time.sleep( main.checkFlowsDelay )

            flowState = main.TRUE
            for cli in main.CLIs:
                flowState = cli.checkFlowState()
                if not flowState:
                    main.log.warn( "Not all flows added" )
            if flowState:
                break
        else:
            #Dumping summary
            main.log.info( "Summary:\n" + str( main.ONOScli1.summary(jsonFormat=False) ) )

        utilities.assert_equals( expect=main.TRUE, actual=flowState,
                                 onpass="FLOWS INSTALLED",
                                 onfail="SOME FLOWS NOT ADDED" )

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )

        caseResult = ( pingResult and intentState and flowState)
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="Install 25 single to multi point Intents and Ping All test PASS",
            onfail="Install 25 single to multi point Intents and Ping All test FAIL" )

        if not intentState:
            main.log.debug( "Intents failed to install completely" )
        if not pingResult:
            main.log.debug( "Pingall failed" )
        if not checkFlowsState:
            main.log.debug( "Flows failed to add completely" )

        if not caseResult and main.failSwitch:
            main.log.report("Stopping test")
            main.stop( email=main.emailOnStop )

    def CASE97( self ):
        """
        Install single-multi point intents and verify Ping all works
        for Chordal topology
        """
        import copy
        main.log.report( "Install single-multi point intents and verify Ping all" )
        main.log.report( "___________________________________________" )
        main.case( "Install single-multi point intents and Ping all" )
        deviceDPIDsCopy = copy.copy(main.deviceDPIDs)
        portEgressList = ['1']*(len(deviceDPIDsCopy) - 1)
        intentIdList = []
        main.log.info( "MACsDict" + str(main.MACsDict) )
        time1 = time.time()
        for i in xrange(0,len(deviceDPIDsCopy),int(main.numCtrls)):
            pool = []
            for cli in main.CLIs:
                ingressDevice = deviceDPIDsCopy[i]
                egressDeviceList = copy.copy(deviceDPIDsCopy)
                egressDeviceList.remove(ingressDevice)
                if i >= len( deviceDPIDsCopy ):
                    break
                t = main.Thread( target=cli.addSinglepointToMultipointIntent,
                        threadID=main.threadID,
                        name="addSinglepointToMultipointIntent",
                        args =[ingressDevice,egressDeviceList,'1',portEgressList,'',main.MACsDict.get(ingressDevice),''])
                pool.append(t)
                t.start()
                i = i + 1
                main.threadID = main.threadID + 1
            for thread in pool:
                thread.join()
                intentIdList.append(thread.result)
        time2 = time.time()
        main.log.info("Time for adding point intents: %2f seconds" %(time2-time1))

        main.step("Verify intents are installed")

        # Giving onos multiple chances to install intents
        for i in range( main.intentCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
            main.log.info("Waiting for onos to install intents...")
            time.sleep( main.checkIntentsDelay )

            intentState = main.TRUE
            for e in range(int(main.numCtrls)):
                main.log.info( "Checking intents on CLI %s" % (e+1) )
                intentState = main.CLIs[e].checkIntentState( intentsId = intentIdList ) and\
                        intentState
                if not intentState:
                    main.log.warn( "Not all intents installed" )
            if intentState:
                break
        else:
            #Dumping intent summary
            main.log.info( "Intents:\n" + str( main.ONOScli1.intents( jsonFormat=False, summary=True ) ) )

        utilities.assert_equals( expect=main.TRUE, actual=intentState,
                                 onpass="INTENTS INSTALLED",
                                 onfail="SOME INTENTS NOT INSTALLED" )

        main.step("Verify flows are all added")

        for i in range( main.flowCheck ):
            if i != 0:
                main.log.warn( "verification failed. Retrying..." )
            main.log.info( "Waiting for onos to add flows..." )
            time.sleep( main.checkFlowsDelay )

            flowState = main.TRUE
            for cli in main.CLIs:
                flowState = cli.checkFlowState()
                if not flowState:
                    main.log.warn( "Not all flows added" )
            if flowState:
                break
        else:
            #Dumping summary
            main.log.info( "Summary:\n" + str( main.ONOScli1.summary(jsonFormat=False) ) )

        utilities.assert_equals( expect=main.TRUE, actual=flowState,
                                 onpass="FLOWS INSTALLED",
                                 onfail="SOME FLOWS NOT ADDED" )

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )

        caseResult = ( pingResult and intentState and flowState)
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="Install 25 single to multi point Intents and Ping All test PASS",
            onfail="Install 25 single to multi point Intents and Ping All test FAIL" )

        if not intentState:
            main.log.debug( "Intents failed to install completely" )
        if not pingResult:
            main.log.debug( "Pingall failed" )
        if not checkFlowsState:
            main.log.debug( "Flows failed to add completely" )

        if not caseResult and main.failSwitch:
            main.log.report("Stopping test")
            main.stop( email=main.emailOnStop )

    def CASE98( self ):
        """
        Install single-multi point intents and verify Ping all works
        for Spine topology
        """
        import copy
        main.log.report( "Install single-multi point intents and verify Ping all" )
        main.log.report( "___________________________________________" )
        main.case( "Install single-multi point intents and Ping all" )
        deviceDPIDsCopy = copy.copy( main.deviceDPIDs )
        deviceDPIDsCopy = deviceDPIDsCopy[ 10: ]
        portEgressList = [ '1' ]*(len(deviceDPIDsCopy) - 1)
        intentIdList = []
        MACsDictCopy = {}
        for i in range( len( deviceDPIDsCopy ) ):
            MACsDictCopy[ deviceDPIDsCopy[ i ] ] = main.hostMACs[i].split( '/' )[ 0 ]

        main.log.info( "deviceDPIDsCopy" + str(deviceDPIDsCopy) )
        main.log.info( "MACsDictCopy" +  str(MACsDictCopy) )
        time1 = time.time()
        for i in xrange(0,len(deviceDPIDsCopy),int(main.numCtrls)):
            pool = []
            for cli in main.CLIs:
                if i >= len( deviceDPIDsCopy ):
                    break
                ingressDevice = deviceDPIDsCopy[i]
                egressDeviceList = copy.copy(deviceDPIDsCopy)
                egressDeviceList.remove(ingressDevice)
                t = main.Thread( target=cli.addSinglepointToMultipointIntent,
                        threadID=main.threadID,
                        name="addSinglepointToMultipointIntent",
                        args =[ingressDevice,egressDeviceList,'1',portEgressList,'',MACsDictCopy.get(ingressDevice),''])
                pool.append(t)
                t.start()
                i = i + 1
                main.threadID = main.threadID + 1
            for thread in pool:
                thread.join()
                intentIdList.append(thread.result)
        time2 = time.time()
        main.log.info("Time for adding point intents: %2f seconds" %(time2-time1))

        main.step("Verify intents are installed")

        # Giving onos multiple chances to install intents
        for i in range( main.intentCheck ):
            if i != 0:
                main.log.warn( "Verification failed. Retrying..." )
            main.log.info("Waiting for onos to install intents...")
            time.sleep( main.checkIntentsDelay )

            intentState = main.TRUE
            for e in range(int(main.numCtrls)):
                main.log.info( "Checking intents on CLI %s" % (e+1) )
                intentState = main.CLIs[e].checkIntentState( intentsId = intentIdList ) and\
                        intentState
                if not intentState:
                    main.log.warn( "Not all intents installed" )
            if intentState:
                break
        else:
            #Dumping intent summary
            main.log.info( "Intents:\n" + str( main.ONOScli1.intents( jsonFormat=False, summary=True ) ) )

        utilities.assert_equals( expect=main.TRUE, actual=intentState,
                                 onpass="INTENTS INSTALLED",
                                 onfail="SOME INTENTS NOT INSTALLED" )

        main.step("Verify flows are all added")

        for i in range( main.flowCheck ):
            if i != 0:
                main.log.warn( "verification failed. Retrying..." )
            main.log.info( "Waiting for onos to add flows..." )
            time.sleep( main.checkFlowsDelay )

            flowState = main.TRUE
            for cli in main.CLIs:
                flowState = cli.checkFlowState()
                if not flowState:
                    main.log.warn( "Not all flows added" )
            if flowState:
                break
        else:
            #Dumping summary
            main.log.info( "Summary:\n" + str( main.ONOScli1.summary(jsonFormat=False) ) )

        utilities.assert_equals( expect=main.TRUE, actual=flowState,
                                 onpass="FLOWS INSTALLED",
                                 onfail="SOME FLOWS NOT ADDED" )

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )

        caseResult = ( pingResult and intentState and flowState)
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="Install 25 single to multi point Intents and Ping All test PASS",
            onfail="Install 25 single to multi point Intents and Ping All test FAIL" )

        if not intentState:
            main.log.debug( "Intents failed to install completely" )
        if not pingResult:
            main.log.debug( "Pingall failed" )
        if not checkFlowsState:
            main.log.debug( "Flows failed to add completely" )

        if not caseResult and main.failSwitch:
            main.log.report("Stopping test")
            main.stop( email=main.emailOnStop )

    def CASE190( self ):
        """
        Verify IPv6 ping across 600 Point intents (Att Topology)
        """
        main.log.report( "Verify IPv6 ping across 600 Point intents (Att Topology)" )
        main.log.report( "_________________________________________________" )
        import itertools
        import time
        main.case( "IPv6 ping all 600 Point intents" )
        main.step( "Verify IPv6 Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        if not pingResult:
            main.log.warn("First pingall failed. Retrying...")
            time1 = time.time()
            pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for IPv6 Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = pingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="IPv6 Ping across 600 Point intents test PASS",
            onfail="IPv6 Ping across 600 Point intents test FAIL" )

    def CASE191( self ):
        """
        Verify IPv6 ping across 600 Point intents (Chordal Topology)
        """
        main.log.report( "Verify IPv6 ping across 600 Point intents (Chordal Topology)" )
        main.log.report( "_________________________________________________" )
        import itertools
        import time
        main.case( "IPv6 ping all 600 Point intents" )
        main.step( "Verify IPv6 Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        if not pingResult:
            main.log.warn("First pingall failed. Retrying...")
            time1 = time.time()
            pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for IPv6 Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = pingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="IPv6 Ping across 600 Point intents test PASS",
            onfail="IPv6 Ping across 600 Point intents test FAIL" )

    def CASE192( self ):
        """
        Verify IPv6 ping across 4556 Point intents (Spine Topology)
        """
        main.log.report( "Verify IPv6 ping across 4556 Point intents (Spine Topology)" )
        main.log.report( "_________________________________________________" )
        import itertools
        import time
        main.case( "IPv6 ping all 4556 Point intents" )
        main.step( "Verify IPv6 Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        if not pingResult:
            main.log.warn("First pingall failed. Retrying...")
            time1 = time.time()
            pingResult = main.Mininet1.pingall( protocol="IPv6", timeout=main.pingTimeout )
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for IPv6 Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult = pingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=caseResult,
            onpass="IPv6 Ping across 4556 Point intents test PASS",
            onfail="IPv6 Ping across 4556 Point intents test FAIL" )

    def CASE10( self ):
        import time
        import re
        """
         Remove all Intents
        """
        main.log.report( "Remove all intents that were installed previously" )
        main.log.report( "______________________________________________" )
        main.log.info( "Remove all intents" )
        main.case( "Removing intents" )
        purgeDelay = int( main.params[ "timers" ][ "IntentPurgeDelay" ] )
        main.step( "Obtain the intent id's first" )
        intentsList = main.ONOScli1.getAllIntentIds()
        ansi_escape = re.compile( r'\x1b[^m]*m' )
        intentsList = ansi_escape.sub( '', intentsList )
        intentsList = intentsList.replace(
            " onos:intents | grep id=",
            "" ).replace(
            "id=",
            "" ).replace(
            "\r\r",
             "" )
        intentsList = intentsList.splitlines()
        intentIdList = []
        step1Result = main.TRUE
        moreIntents = main.TRUE
        removeIntentCount = 0
        intentsCount = len(intentsList)
        main.log.info ( "Current number of intents:  " + str(intentsCount) )
        if ( len( intentsList ) > 1 ):
            results = main.TRUE
            main.log.info("Removing intent...")
            while moreIntents:
            # This is a work around only: cycle through intents removal for up to 5 times.
                if removeIntentCount == 5:
                    break
                removeIntentCount = removeIntentCount + 1
                intentsList1 = main.ONOScli1.getAllIntentIds()
                if len( intentsList1 ) == 0:
                    break
                ansi_escape = re.compile( r'\x1b[^m]*m' )
                intentsList1 = ansi_escape.sub( '', intentsList1 )
                intentsList1 = intentsList1.replace(
                    " onos:intents | grep id=",
                    "" ).replace(
                    " state=",
                    "" ).replace(
                    "\r\r",
                    "" )
                intentsList1 = intentsList1.splitlines()
                main.log.info ( "Round %d intents to remove: " %(removeIntentCount) )
                print intentsList1
                intentIdList1 = []
                if ( len( intentsList1 ) > 0 ):
                    moreIntents = main.TRUE
                    for i in range( len( intentsList1 ) ):
                        intentsTemp1 = intentsList1[ i ].split( ',' )
                        intentIdList1.append( intentsTemp1[ 0 ].split('=')[1] )
                    main.log.info ( "Leftover Intent IDs: " + str(intentIdList1) )
                    main.log.info ( "Length of Leftover Intents list: " + str(len(intentIdList1)) )
                    time1 = time.time()
                    for i in xrange( 0, len( intentIdList1 ), int(main.numCtrls) ):
                        pool = []
                        for cli in main.CLIs:
                            if i >= len( intentIdList1 ):
                                break
                            t = main.Thread( target=cli.removeIntent,
                                    threadID=main.threadID,
                                    name="removeIntent",
                                    args=[intentIdList1[i],'org.onosproject.cli',False,False])
                            pool.append(t)
                            t.start()
                            i = i + 1
                            main.threadID = main.threadID + 1
                        for thread in pool:
                            thread.join()
                            intentIdList.append(thread.result)
                        #time.sleep(2)
                    time2 = time.time()
                    main.log.info("Time for removing host intents: %2f seconds" %(time2-time1))
                    time.sleep( purgeDelay )
                    main.log.info("Purging WITHDRAWN Intents")
                    purgeResult  = main.ONOScli1.purgeWithdrawnIntents()
                else:
                    time.sleep(10)
                    if len( main.ONOScli1.intents()):
                        continue
                    break
                time.sleep( purgeDelay )
            else:
                print "Removed %d intents" %(intentsCount)
                step1Result = main.TRUE
        else:
            print "No Intent IDs found in Intents list: ", intentsList
            step1Result = main.FALSE

        print main.ONOScli1.intents()
        caseResult = step1Result
        utilities.assert_equals( expect=main.TRUE, actual=caseResult,
                                 onpass="Intent removal test successful",
                                 onfail="Intent removal test failed" )

    def CASE12( self, main ):
        """
        Enable onos-app-ifwd, Verify Intent based Reactive forwarding through ping all and Disable it
        """
        import re
        import copy
        import time

        threadID = 0

        main.log.report( "Enable Intent based Reactive forwarding and Verify ping all" )
        main.log.report( "_____________________________________________________" )
        main.case( "Enable Intent based Reactive forwarding and Verify ping all" )
        main.step( "Enable intent based Reactive forwarding" )
        installResult = main.FALSE
        feature = "onos-app-ifwd"

        pool = []
        time1 = time.time()
        for cli,feature in main.CLIs:
            t = main.Thread(target=cli,threadID=threadID,
                    name="featureInstall",args=[feature])
            pool.append(t)
            t.start()
            threadID = threadID + 1

        results = []
        for thread in pool:
            thread.join()
            results.append(thread.result)
        time2 = time.time()

        if( all(result == main.TRUE for result in results) == False):
                main.log.info("Did not install onos-app-ifwd feature properly")
                #main.cleanup()
                #main.exit()
        else:
            main.log.info("Successful feature:install onos-app-ifwd")
            installResult = main.TRUE
        main.log.info("Time for feature:install onos-app-ifwd: %2f seconds" %(time2-time1))

        main.step( "Verify Ping across all hosts" )
        for i in range(main.numPings):
            time1 = time.time()
            pingResult = main.Mininet1.pingall(timeout=main.pingTimeout)
            if not pingResult:
                main.log.warn("First pingall failed. Retrying...")
                time.sleep(main.pingSleep)
            else: break

        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )

        if pingResult == main.TRUE:
            main.log.report( "Pingall Test in Reactive mode successful" )
        else:
            main.log.report( "Pingall Test in Reactive mode failed" )

        main.step( "Disable Intent based Reactive forwarding" )
        uninstallResult = main.FALSE

        pool = []
        time1 = time.time()
        for cli,feature in main.CLIs:
            t = main.Thread(target=cli,threadID=threadID,
                    name="featureUninstall",args=[feature])
            pool.append(t)
            t.start()
            threadID = threadID + 1

        results = []
        for thread in pool:
            thread.join()
            results.append(thread.result)
        time2 = time.time()

        if( all(result == main.TRUE for result in results) == False):
                main.log.info("Did not uninstall onos-app-ifwd feature properly")
                uninstallResult = main.FALSE
                #main.cleanup()
                #main.exit()
        else:
            main.log.info("Successful feature:uninstall onos-app-ifwd")
            uninstallResult = main.TRUE
        main.log.info("Time for feature:uninstall onos-app-ifwd: %2f seconds" %(time2-time1))

        # Waiting for reative flows to be cleared.
        time.sleep( 10 )

        caseResult = installResult and pingResult and uninstallResult
        utilities.assert_equals( expect=main.TRUE, actual=caseResult,
                                 onpass="Intent based Reactive forwarding Pingall test PASS",
                                 onfail="Intent based Reactive forwarding Pingall test FAIL" )
