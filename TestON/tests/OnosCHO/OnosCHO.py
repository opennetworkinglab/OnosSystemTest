
import sys
import os
import re
import time
import json
import itertools


class OnosCHO:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        Startup sequence:
        git pull
        mvn clean install
        onos-package
        cell <name>
        onos-verify-cell
        onos-install -f
        onos-wait-for-start
        """
        import time

        global intentState
        main.threadID = 0
        main.pingTimeout = 300
        main.numCtrls = main.params[ 'CTRL' ][ 'numCtrl' ]
        main.ONOS1_ip = main.params[ 'CTRL' ][ 'ip1' ]
        main.ONOS2_ip = main.params[ 'CTRL' ][ 'ip2' ]
        main.ONOS3_ip = main.params[ 'CTRL' ][ 'ip3' ]
        main.ONOS4_ip = main.params[ 'CTRL' ][ 'ip4' ]
        main.ONOS5_ip = main.params[ 'CTRL' ][ 'ip5' ]
        main.ONOS1_port = main.params[ 'CTRL' ][ 'port1' ]
        main.ONOS2_port = main.params[ 'CTRL' ][ 'port2' ]
        main.ONOS3_port = main.params[ 'CTRL' ][ 'port3' ]
        main.ONOS4_port = main.params[ 'CTRL' ][ 'port4' ]
        main.ONOS5_port = main.params[ 'CTRL' ][ 'port5' ]
        cell_name = main.params[ 'ENV' ][ 'cellName' ]
        git_pull = main.params[ 'GIT' ][ 'autoPull' ]
        git_branch = main.params[ 'GIT' ][ 'branch' ]
        main.newTopo = ""
        main.CLIs = []
        main.nodes = []
        for i in range( 1, int(main.numCtrls) + 1 ):
            main.CLIs.append( getattr( main, 'ONOScli' + str( i ) ) )
            main.nodes.append( getattr( main, 'ONOS' + str( i ) ) )
        
        main.case( "Set up test environment" )
        main.log.report( "Set up test environment" )
        main.log.report( "_______________________" )

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

        main.step( "Apply Cell environment for ONOS" )
        cell_result = main.ONOSbench.setCell( cell_name )
        utilities.assert_equals( expect=main.TRUE, actual=cell_result,
                                 onpass="Test step PASS",
                                 onfail="Test step FAIL" )

        main.step( "Create ONOS package" )
        packageResult = main.ONOSbench.onosPackage()
        utilities.assert_equals( expect=main.TRUE, actual=packageResult,
                                 onpass="Test step PASS",
                                 onfail="Test step FAIL" )

        main.step( "Uninstall ONOS package on all Nodes" )
        uninstallResult = main.TRUE
        for i in range( 1, int( main.numCtrls ) + 1 ):
            ONOS_ip = main.params[ 'CTRL' ][ 'ip' + str( i ) ]
            main.log.info( "Uninstalling package on ONOS Node IP: " + ONOS_ip )
            u_result = main.ONOSbench.onosUninstall( ONOS_ip )
            utilities.assert_equals( expect=main.TRUE, actual=u_result,
                                     onpass="Test step PASS",
                                     onfail="Test step FAIL" )
            uninstallResult = ( uninstallResult and u_result )

        #main.step( "Removing copy-cat logs from ONOS nodes" )
        #main.ONOSbench.onosRemoveRaftLogs()

        main.step( "Install ONOS package on all Nodes" )
        installResult = main.TRUE
        for i in range( 1, int( main.numCtrls ) + 1 ):
            ONOS_ip = main.params[ 'CTRL' ][ 'ip' + str( i ) ]
            main.log.info( "Intsalling package on ONOS Node IP: " + ONOS_ip )
            i_result = main.ONOSbench.onosInstall( node=ONOS_ip )
            utilities.assert_equals( expect=main.TRUE, actual=i_result,
                                     onpass="Test step PASS",
                                     onfail="Test step FAIL" )
            installResult = ( installResult and i_result )

        main.step( "Verify ONOS nodes UP status" )
        statusResult = main.TRUE
        for i in range( 1, int( main.numCtrls ) + 1 ):
            ONOS_ip = main.params[ 'CTRL' ][ 'ip' + str( i ) ]
            main.log.info( "ONOS Node " + ONOS_ip + " status:" )
            onos_status = main.ONOSbench.onosStatus( node=ONOS_ip )
            utilities.assert_equals( expect=main.TRUE, actual=onos_status,
                                     onpass="Test step PASS",
                                     onfail="Test step FAIL" )
            statusResult = ( statusResult and onos_status )
        
        main.step( "Start ONOS CLI on all nodes" )
        cliResult = main.TRUE
        karafTimeout = "3600000"
        # need to wait here for sometime. This will be removed once ONOS is
        # stable enough
        time.sleep( 25 )
        main.log.step(" Start ONOS cli using thread ")
        startCliResult  = main.TRUE
        pool = []
        time1 = time.time()
        for i in range( int( main.numCtrls) ):
            t = main.Thread( target=main.CLIs[i].startOnosCli,
                             threadID=main.threadID,
                             name="startOnosCli",
                             args=[ main.nodes[i].ip_address ] )
            pool.append(t)
            t.start()
            main.threadID = main.threadID + 1
        for t in pool:
            t.join()
            startCliResult = startCliResult and t.result
        time2 = time.time()
        
        if not startCliResult:
                main.log.info("ONOS CLI did not start up properly")
                #main.cleanup()
                #main.exit()
        else:
            main.log.info("Successful CLI startup")
            startCliResult = main.TRUE
        case1Result = installResult and uninstallResult and statusResult and startCliResult
        
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

        main.numMNswitches = int ( main.params[ 'TOPO1' ][ 'numSwitches' ] )
        main.numMNlinks = int ( main.params[ 'TOPO1' ][ 'numLinks' ] )
        main.numMNhosts = int ( main.params[ 'TOPO1' ][ 'numHosts' ] )
        main.pingTimeout = 60 
        main.log.report(
            "Load Att topology and Balance all Mininet switches across controllers" )
        main.log.report(
            "________________________________________________________________________" )
        main.case(
            "Assign and Balance all Mininet switches across controllers" )
        main.step( "Stop any previous Mininet network topology" )
        cliResult = main.TRUE
        if main.newTopo == main.params['TOPO3']['topo']:
            stopStatus = main.Mininet1.stopNet( fileName = "topoSpine" )

        main.step( "Start Mininet with Att topology" )
        main.newTopo = main.params['TOPO1']['topo']
        startStatus = main.Mininet1.startNet(topoFile = main.newTopo)

        main.step( "Assign switches to controllers" )
        for i in range( 1, ( main.numMNswitches + 1 ) ):  # 1 to ( num of switches +1 )
            main.Mininet1.assignSwController(
                sw=str( i ),
                count=int( main.numCtrls ),
                ip1=main.ONOS1_ip,
                port1=main.ONOS1_port,
                ip2=main.ONOS2_ip,
                port2=main.ONOS2_port,
                ip3=main.ONOS3_ip,
                port3=main.ONOS3_port,
                ip4=main.ONOS4_ip,
                port4=main.ONOS4_port,
                ip5=main.ONOS5_ip,
                port5=main.ONOS5_port )

        switch_mastership = main.TRUE
        for i in range( 1, ( main.numMNswitches + 1 ) ):
            response = main.Mininet1.getSwController( "s" + str( i ) )
            print( "Response is " + str( response ) )
            if re.search( "tcp:" + main.ONOS1_ip, response ):
                switch_mastership = switch_mastership and main.TRUE
            else:
                switch_mastership = main.FALSE

        if switch_mastership == main.TRUE:
            main.log.report( "Controller assignment successfull" )
        else:
            main.log.report( "Controller assignment failed" )
        
        """topoFailed = main.FALSE
        checkCount = 0
        while(topoFailed  == main.FALSE):
            topology_output = main.ONOScli1.topology()
            topology_result = main.ONOSbench.getTopology( topology_output )
            numOnosDevices = topology_result[ 'deviceCount' ]
            numOnosLinks = topology_result[ 'linkCount' ]
            if ( ( main.numMNswitches == int(numOnosDevices) ) and ( main.numMNlinks >= int(numOnosLinks) ) ):
                main.log.info("Att topology is now ready!")
                break
            else:
                main.log.info("Att topology is not ready yet!")
            checkCount = checkCount + 1
            time.sleep(2)
            if checkCount == 10:
                topoFailed = main.TRUE
        if topoFailed:
            main.log.info("Att topology failed to start correctly")
        """
        time.sleep(15)
        #Don't balance master for now..
        main.step( "Balance devices across controllers" )
        for i in range( int( main.numCtrls ) ):
            balanceResult = main.ONOScli1.balanceMasters()
            # giving some breathing time for ONOS to complete re-balance
            time.sleep( 3 )
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

        main.newTopo = main.params['TOPO2']['topo']
        main.numMNswitches = int ( main.params[ 'TOPO2' ][ 'numSwitches' ] )
        main.numMNlinks = int ( main.params[ 'TOPO2' ][ 'numLinks' ] )
        main.numMNhosts = int ( main.params[ 'TOPO2' ][ 'numHosts' ] )
        main.pingTimeout = 120
        main.log.report(
            "Load Chordal topology and Balance all Mininet switches across controllers" )
        main.log.report(
            "________________________________________________________________________" )
        main.case(
            "Assign and Balance all Mininet switches across controllers" )
        main.step( "Stop any previous Mininet network topology" )
        stopStatus = main.Mininet1.stopNet(fileName = "topoChordal" )
        #time.sleep(10)
        main.step( "Start Mininet with Chordal topology" )
        startStatus = main.Mininet1.startNet(topoFile = main.newTopo)
        time.sleep(15)
        main.step( "Assign switches to controllers" )
        for i in range( 1, ( main.numMNswitches + 1 ) ):  # 1 to ( num of switches +1 )
            main.Mininet1.assignSwController(
                sw=str( i ),
                count=int( main.numCtrls ),
                ip1=main.ONOS1_ip,
                port1=main.ONOS1_port,
                ip2=main.ONOS2_ip,
                port2=main.ONOS2_port,
                ip3=main.ONOS3_ip,
                port3=main.ONOS3_port,
                ip4=main.ONOS4_ip,
                port4=main.ONOS4_port,
                ip5=main.ONOS5_ip,
                port5=main.ONOS5_port )

        switch_mastership = main.TRUE
        for i in range( 1, ( main.numMNswitches + 1 ) ):
            response = main.Mininet1.getSwController( "s" + str( i ) )
            print( "Response is " + str( response ) )
            if re.search( "tcp:" + main.ONOS1_ip, response ):
                switch_mastership = switch_mastership and main.TRUE
            else:
                switch_mastership = main.FALSE

        if switch_mastership == main.TRUE:
            main.log.report( "Controller assignment successfull" )
        else:
            main.log.report( "Controller assignment failed" )
        time.sleep( 5 )
        
        #Don't balance master for now..
        """
        main.step( "Balance devices across controllers" )
        for i in range( int( main.numCtrls ) ):
            balanceResult = main.ONOScli1.balanceMasters()
            # giving some breathing time for ONOS to complete re-balance
            time.sleep( 3 )
        """
        case21Result = switch_mastership
        time.sleep(30)
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case21Result,
            onpass="Starting new Chordal topology test PASS",
            onfail="Starting new Chordal topology test FAIL" )
        
    def CASE22( self, main ):
        """
        This test script Loads a new Topology (Spine) on CHO setup and balances all switches
        """
        import re
        import time
        import copy

        main.newTopo = main.params['TOPO3']['topo']
        main.numMNswitches = int ( main.params[ 'TOPO3' ][ 'numSwitches' ] )
        main.numMNlinks = int ( main.params[ 'TOPO3' ][ 'numLinks' ] )
        main.numMNhosts = int ( main.params[ 'TOPO3' ][ 'numHosts' ] )
        main.pingTimeout = 400
        
        main.log.report(
            "Load Spine and Leaf topology and Balance all Mininet switches across controllers" )
        main.log.report(
            "________________________________________________________________________" )
        # need to wait here for sometime until ONOS bootup
        main.case(
            "Assign and Balance all Mininet switches across controllers" )
        main.step( "Stop any previous Mininet network topology" )
        stopStatus = main.Mininet1.stopNet(fileName = "topoSpine" )
        main.step( "Start Mininet with Spine topology" )
        startStatus = main.Mininet1.startNet(topoFile = main.newTopo)
        time.sleep(20)
        main.step( "Assign switches to controllers" )
        for i in range( 1, ( main.numMNswitches + 1 ) ):  # 1 to ( num of switches +1 )
            main.Mininet1.assignSwController(
                sw=str( i ),
                count= 1,
                ip1=main.ONOS1_ip,
                port1=main.ONOS1_port,
                ip2=main.ONOS2_ip,
                port2=main.ONOS2_port,
                ip3=main.ONOS3_ip,
                port3=main.ONOS3_port,
                ip4=main.ONOS4_ip,
                port4=main.ONOS4_port,
                ip5=main.ONOS5_ip,
                port5=main.ONOS5_port )

        switch_mastership = main.TRUE
        for i in range( 1, ( main.numMNswitches + 1 ) ):
            response = main.Mininet1.getSwController( "s" + str( i ) )
            print( "Response is " + str( response ) )
            if re.search( "tcp:" + main.ONOS1_ip, response ):
                switch_mastership = switch_mastership and main.TRUE
            else:
                switch_mastership = main.FALSE
        
        if switch_mastership == main.TRUE:
            main.log.report( "Controller assignment successfull" )
        else:
            main.log.report( "Controller assignment failed" )
        time.sleep( 5 )
        """
        main.step( "Balance devices across controllers" )
        
        for i in range( int( main.numCtrls ) ):
            balanceResult = main.ONOScli1.balanceMasters()
            # giving some breathing time for ONOS to complete re-balance
            time.sleep( 3 )

        main.step( "Balance devices across controllers" )
        for i in range( int( main.numCtrls ) ):
            balanceResult = main.ONOScli1.balanceMasters()
            # giving some breathing time for ONOS to complete re-balance
            time.sleep( 3 )
        """
        case22Result = switch_mastership
        time.sleep(30)
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case22Result,
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
        numOnosDevices = topology_result[ 'deviceCount' ]
        numOnosLinks = topology_result[ 'linkCount' ]
        topoResult = main.TRUE

        if ( ( main.numMNswitches == int(numOnosDevices) ) and ( main.numMNlinks >= int(numOnosLinks) ) ):
            main.step( "Store Device DPIDs" )
            for i in range( 1, (main.numMNswitches+1) ):
                main.deviceDPIDs.append( "of:00000000000000" + format( i, '02x' ) )
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
            linksResult = linksResult[ 1: ]
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
                    dpid = "of:00000000000000" + format( i,'02x' )
                    t = main.Thread(target = cli.getDevicePortsEnabledCount,threadID = main.threadID, name = "getDevicePortsEnabledCount",args = [dpid])
                    t.start()
                    pool.append(t)
                    i = i + 1
                    main.threadID = main.threadID + 1
                for thread in pool:
                    thread.join()
                    portResult = thread.result
                    portTemp = re.split( r'\t+', portResult )
                    portCount = portTemp[ 1 ].replace( "\r\r\n\x1b[32m", "" )
                    main.devicePortsEnabledCount.append( portCount )
            print "Device Enabled Port Counts Stored: \n", str( main.devicePortsEnabledCount )
            time2 = time.time()
            main.log.info("Time for counting enabled ports of the switches: %2f seconds" %(time2-time1))

            main.step( "Collect and store each Device active links Count" )
            time1 = time.time()
            
            for i in xrange( 1,( main.numMNswitches + 1 ), int( main.numCtrls) ):
                pool = []
                for cli in main.CLIs:
                    dpid = "of:00000000000000" + format( i,'02x' )
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
                    linkCountTemp = re.split( r'\t+', linkCountResult )
                    linkCount = linkCountTemp[ 1 ].replace( "\r\r\n\x1b[32m", "" )
                    main.deviceActiveLinksCount.append( linkCount )
                print "Device Active Links Count Stored: \n", str( main.deviceActiveLinksCount )
            time2 = time.time()
            main.log.info("Time for counting all enabled links of the switches: %2f seconds" %(time2-time1))

        else:
            main.log.info("Devices (expected): %s, Links (expected): %s" % 
                    ( str( main.numMNswitches ), str( main.numMNlinks ) ) )
            main.log.info("Devices (actual): %s, Links (actual): %s" %
                    ( numOnosDevices , numOnosLinks ) )
            main.log.info("Topology does not match, exiting CHO test...")
            topoResult = main.FALSE
            
            #time.sleep(300)
            #main.cleanup()
            #main.exit()

        # just returning TRUE for now as this one just collects data
        case3Result = topoResult
        utilities.assert_equals( expect=main.TRUE, actual=case3Result,
                                 onpass="Saving ONOS topology data test PASS",
                                 onfail="Saving ONOS topology data test FAIL" )

    def CASE40( self, main ):
        """
        Verify Reactive forwarding (Att Topology)
        """
        import re
        import copy
        import time
        main.log.report( "Verify Reactive forwarding (Att Topology)" )
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

        main.step( "Verify Pingall" )
        ping_result = main.FALSE
        time1 = time.time()
        ping_result = main.Mininet1.pingall(timeout=main.pingTimeout,shortCircuit=True)
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )

        if ping_result == main.TRUE:
            main.log.report( "Pingall Test in Reactive mode successful" )
        else:
            main.log.report( "Pingall Test in Reactive mode failed" )

        main.step( "Disable Reactive forwarding" )
       
        main.log.info( "Uninstall reactive forwarding app" )
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
        time.sleep( 10 )
        case40Result =  installResult and uninstallResult and ping_result
        utilities.assert_equals( expect=main.TRUE, actual=case40Result,
                                 onpass="Reactive Mode Pingall test PASS",
                                 onfail="Reactive Mode Pingall test FAIL" )

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

        main.step( "Verify Pingall" )
        ping_result = main.FALSE
        time1 = time.time()
        ping_result = main.Mininet1.pingall(timeout=main.pingTimeout,shortCircuit=True)
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )

        if ping_result == main.TRUE:
            main.log.report( "Pingall Test in Reactive mode successful" )
        else:
            main.log.report( "Pingall Test in Reactive mode failed" )

        main.step( "Disable Reactive forwarding" )
       
        main.log.info( "Uninstall reactive forwarding app" )
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
        time.sleep( 10 )
        case41Result =  installResult and uninstallResult and ping_result
        utilities.assert_equals( expect=main.TRUE, actual=case41Result,
                                 onpass="Reactive Mode Pingall test PASS",
                                 onfail="Reactive Mode Pingall test FAIL" )

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

        main.step( "Verify Pingall" )
        ping_result = main.FALSE
        time1 = time.time()
        ping_result = main.Mininet1.pingall(timeout=main.pingTimeout,shortCircuit=True)
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )

        if ping_result == main.TRUE:
            main.log.report( "Pingall Test in Reactive mode successful" )
        else:
            main.log.report( "Pingall Test in Reactive mode failed" )

        main.step( "Disable Reactive forwarding" )
       
        main.log.info( "Uninstall reactive forwarding app" )
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
        time.sleep( 10 )
        case42Result =  installResult and uninstallResult and ping_result
        utilities.assert_equals( expect=main.TRUE, actual=case42Result,
                                 onpass="Reactive Mode Pingall test PASS",
                                 onfail="Reactive Mode Pingall test FAIL" )

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
        time1 = time.time()
        for i in xrange( 1,(main.numMNswitches + 1), int( main.numCtrls ) ):
            pool = []
            for cli in main.CLIs:
                dpid = "of:00000000000000" + format( i,'02x' )
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
                portTemp = re.split( r'\t+', portResult )
                portCount = portTemp[ 1 ].replace( "\r\r\n\x1b[32m", "" )
                devicePortsEnabledCountTemp.append( portCount )
        print "Device Enabled Port Counts Stored: \n", str( main.devicePortsEnabledCount )
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
                dpid = "of:00000000000000" + format( i,'02x' )
                t = main.Thread(target = cli.getDeviceLinksActiveCount,
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
                linkCountTemp = re.split( r'\t+', linkCountResult )
                linkCount = linkCountTemp[ 1 ].replace( "\r\r\n\x1b[32m", "" )
                deviceActiveLinksCountTemp.append( linkCount )
            print "Device Active Links Count Stored: \n", str( main.deviceActiveLinksCount )
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
        case5Result = ( stepResult1 and stepResult2 )
        utilities.assert_equals( expect=main.TRUE, actual=case5Result,
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

        intentResult = main.TRUE
        intentsJson = main.ONOScli2.intents()
        getIntentStateResult = main.ONOScli1.getIntentState(intentsId = intentIdList,
                intentsJson = intentsJson)
        print getIntentStateResult
        # Takes awhile for all the onos to get the intents
        time.sleep(30)
        main.step( "Verify Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall(timeout=main.pingTimeout,shortCircuit=True)
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        case60Result = ( intentResult and pingResult )
        
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case60Result,
            onpass="Install 300 Host Intents and Ping All test PASS",
            onfail="Install 300 Host Intents and Ping All test FAIL" )

    def CASE61( self ):
        """
        Install 600 host intents and verify ping all for Chordal Topology
        """
        main.log.report( "Add 600 host intents and verify pingall (Chordal Topo)" )
        main.log.report( "_______________________________________" )
        import itertools
        
        main.case( "Install 600 host intents" )
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
        intentResult = main.TRUE
        intentsJson = main.ONOScli2.intents()
        getIntentStateResult = main.ONOScli1.getIntentState(intentsId = intentIdList,
                intentsJson = intentsJson)
        print getIntentStateResult

        main.step( "Verify Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall(timeout=main.pingTimeout,shortCircuit=True)
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        case14Result = ( intentResult and pingResult )
        
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case14Result,
            onpass="Install 300 Host Intents and Ping All test PASS",
            onfail="Install 300 Host Intents and Ping All test FAIL" )

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
        intentResult = main.TRUE
        intentsJson = main.ONOScli2.intents()
        getIntentStateResult = main.ONOScli1.getIntentState(intentsId = intentIdList,
                intentsJson = intentsJson)
        print getIntentStateResult

        main.step( "Verify Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall(timeout=main.pingTimeout,shortCircuit=True)
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        case15Result = ( intentResult and pingResult )
        
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case15Result,
            onpass="Install 2278 Host Intents and Ping All test PASS",
            onfail="Install 2278 Host Intents and Ping All test FAIL" )

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
            main.Mininet1.link(
                END1=link2End1,
                END2=main.randomLink2[ i ],
                OPTION="down" )
            main.Mininet1.link(
                END1=link3End1,
                END2=main.randomLink3[ i ],
                OPTION="down" )
        time.sleep( link_sleep )

        topology_output = main.ONOScli2.topology()
        linkDown = main.ONOSbench.checkStatus(
            topology_output, main.numMNswitches, str(
                int( main.numMNlinks ) - int( switchLinksToToggle ) * 6 ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=linkDown,
            onpass="Link Down discovered properly",
            onfail="Link down was not discovered in " +
            str( link_sleep ) +
            " seconds" )

        main.step( "Verify Ping across all hosts" )
        pingResultLinkDown = main.FALSE
        time1 = time.time()
        pingResultLinkDown = main.Mininet1.pingall(timeout=main.pingTimeout,shortCircuit=True)
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResultLinkDown,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult70 = linkDown and pingResultLinkDown
        utilities.assert_equals( expect=main.TRUE, actual=caseResult70,
                                 onpass="Random Link cut Test PASS",
                                 onfail="Random Link cut Test FAIL" )

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
            main.Mininet1.link(
                END1=link2End1,
                END2=main.randomLink2[ i ],
                OPTION="up" )
            main.Mininet1.link(
                END1=link3End1,
                END2=main.randomLink3[ i ],
                OPTION="up" )
        time.sleep( link_sleep )

        topology_output = main.ONOScli2.topology()
        linkUp = main.ONOSbench.checkStatus(
            topology_output,
            main.numMNswitches,
            str( main.numMNlinks ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=linkUp,
            onpass="Link up discovered properly",
            onfail="Link up was not discovered in " +
            str( link_sleep ) +
            " seconds" )

        main.step( "Verify Ping across all hosts" )
        pingResultLinkUp = main.FALSE
        time1 = time.time()
        pingResultLinkUp = main.Mininet1.pingall()
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResultLinkUp,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult80 = linkUp and pingResultLinkUp
        utilities.assert_equals( expect=main.TRUE, actual=caseResult80,
                                 onpass="Link Up Test PASS",
                                 onfail="Link Up Test FAIL" )

    def CASE71( self, main ):
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
            main.Mininet1.link(
                END1=link2End1,
                END2=main.randomLink2[ i ],
                OPTION="down" )
            main.Mininet1.link(
                END1=link3End1,
                END2=main.randomLink3[ i ],
                OPTION="down" )
        time.sleep( link_sleep )

        topology_output = main.ONOScli2.topology()
        linkDown = main.ONOSbench.checkStatus(
            topology_output, main.numMNswitches, str(
                int( main.numMNlinks ) - int( switchLinksToToggle ) * 6 ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=linkDown,
            onpass="Link Down discovered properly",
            onfail="Link down was not discovered in " +
            str( link_sleep ) +
            " seconds" )

        main.step( "Verify Ping across all hosts" )
        pingResultLinkDown = main.FALSE
        time1 = time.time()
        pingResultLinkDown = main.Mininet1.pingall(timeout=main.pingTimeout,shortCircuit=True)
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResultLinkDown,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult71 = linkDown and pingResultLinkDown
        utilities.assert_equals( expect=main.TRUE, actual=caseResult71,
                                 onpass="Random Link cut Test PASS",
                                 onfail="Random Link cut Test FAIL" )

    def CASE81( self, main ):
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
            main.Mininet1.link(
                END1=link2End1,
                END2=main.randomLink2[ i ],
                OPTION="up" )
            main.Mininet1.link(
                END1=link3End1,
                END2=main.randomLink3[ i ],
                OPTION="up" )
        time.sleep( link_sleep )

        topology_output = main.ONOScli2.topology()
        linkUp = main.ONOSbench.checkStatus(
            topology_output,
            main.numMNswitches,
            str( main.numMNlinks ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=linkUp,
            onpass="Link up discovered properly",
            onfail="Link up was not discovered in " +
            str( link_sleep ) +
            " seconds" )

        main.step( "Verify Ping across all hosts" )
        pingResultLinkUp = main.FALSE
        time1 = time.time()
        pingResultLinkUp = main.Mininet1.pingall(timeout = main.pingTimeout)
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResultLinkUp,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult81 = linkUp and pingResultLinkUp
        utilities.assert_equals( expect=main.TRUE, actual=caseResult81,
                                 onpass="Link Up Test PASS",
                                 onfail="Link Up Test FAIL" )

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

        topology_output = main.ONOScli2.topology()
        linkDown = main.ONOSbench.checkStatus(
            topology_output, main.numMNswitches, str(
                int( main.numMNlinks ) - 5 * 2 ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=linkDown,
            onpass="Link Down discovered properly",
            onfail="Link down was not discovered in " +
            str( link_sleep ) +
            " seconds" )

        main.step( "Verify Ping across all hosts" )
        pingResultLinkDown = main.FALSE
        time1 = time.time()
        pingResultLinkDown = main.Mininet1.pingall(timeout=main.pingTimeout,shortCircuit=True)
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResultLinkDown,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult71 = pingResultLinkDown
        utilities.assert_equals( expect=main.TRUE, actual=caseResult71,
                                 onpass="Random Link cut Test PASS",
                                 onfail="Random Link cut Test FAIL" )

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

        topology_output = main.ONOScli2.topology()
        linkUp = main.ONOSbench.checkStatus(
            topology_output,
            main.numMNswitches,
            str( main.numMNlinks ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=linkUp,
            onpass="Link up discovered properly",
            onfail="Link up was not discovered in " +
            str( link_sleep ) +
            " seconds" )

        main.step( "Verify Ping across all hosts" )
        pingResultLinkUp = main.FALSE
        time1 = time.time()
        pingResultLinkUp = main.Mininet1.pingall(timeout = main.pingTimeout)
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResultLinkUp,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult82 = linkUp and pingResultLinkUp
        utilities.assert_equals( expect=main.TRUE, actual=caseResult82,
                                 onpass="Link Up Test PASS",
                                 onfail="Link Up Test FAIL" )

    def CASE73( self, main ):
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

        topology_output = main.ONOScli2.topology()
        linkDown = main.ONOSbench.checkStatus(
            topology_output, main.numMNswitches, str(
                int( main.numMNlinks ) - 5 * 2 ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=linkDown,
            onpass="Link Down discovered properly",
            onfail="Link down was not discovered in " +
            str( link_sleep ) +
            " seconds" )

        main.step( "Verify Ping across all hosts" )
        pingResultLinkDown = main.FALSE
        time1 = time.time()
        pingResultLinkDown = main.Mininet1.pingall(timeout=main.pingTimeout,shortCircuit=True)
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResultLinkDown,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult73 = pingResultLinkDown
        utilities.assert_equals( expect=main.TRUE, actual=caseResult73,
                                 onpass="Random Link cut Test PASS",
                                 onfail="Random Link cut Test FAIL" )

    def CASE83( self, main ):
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

        topology_output = main.ONOScli2.topology()
        linkUp = main.ONOSbench.checkStatus(
            topology_output,
            main.numMNswitches,
            str( main.numMNlinks ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=linkUp,
            onpass="Link up discovered properly",
            onfail="Link up was not discovered in " +
            str( link_sleep ) +
            " seconds" )

        main.step( "Verify Ping across all hosts" )
        pingResultLinkUp = main.FALSE
        time1 = time.time()
        pingResultLinkUp = main.Mininet1.pingall(timeout = main.pingTimeout)
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResultLinkUp,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult83 = linkUp and pingResultLinkUp
        utilities.assert_equals( expect=main.TRUE, actual=caseResult83,
                                 onpass="Link Up Test PASS",
                                 onfail="Link Up Test FAIL" )

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
        main.pingTimeout = 400
        
        main.log.report( "Bring some core links down and verify ping all (Host Intents-Spine Topo)" )
        main.log.report( "___________________________________________________________________________" )
        
        linkIndex = range(4)
        linkIndexS9 = random.sample(linkIndex,1)[0] 
        linkIndex.remove(linkIndexS9)
        linkIndexS10 = random.sample(linkIndex,1)[0]
        main.randomLink1 = link1End2top[linkIndexS9]
        main.randomLink2 = link2End2top[linkIndexS10]
        main.randomLink3 = random.sample(link1End2bot,1)[0]
        main.randomLink4 = random.sample(link2End2bot,1)[0]
        # main.Mininet1.link( END1=link1End1, END2=main.randomLink1, OPTION="down" )
        # main.Mininet1.link( END1=link2End1, END2=main.randomLink2, OPTION="down" )
        main.Mininet1.link( END1=link1End1, END2=main.randomLink3, OPTION="down" )
        main.Mininet1.link( END1=link2End1, END2=main.randomLink4, OPTION="down" )
        
        time.sleep( link_sleep )

        topology_output = main.ONOScli2.topology()
        linkDown = main.ONOSbench.checkStatus(
            topology_output, main.numMNswitches, str(
                int( main.numMNlinks ) - 8 ))
        utilities.assert_equals(
            expect=main.TRUE,
            actual=linkDown,
            onpass="Link Down discovered properly",
            onfail="Link down was not discovered in " +
            str( link_sleep ) +
            " seconds" )

        main.step( "Verify Ping across all hosts" )
        pingResultLinkDown = main.FALSE
        time1 = time.time()
        pingResultLinkDown = main.Mininet1.pingall(timeout=main.pingTimeout,shortCircuit=True)
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResultLinkDown,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult74 = linkDown and pingResultLinkDown
        utilities.assert_equals( expect=main.TRUE, actual=caseResult74,
                                 onpass="Random Link cut Test PASS",
                                 onfail="Random Link cut Test FAIL" )

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
        
        #main.Mininet1.link( END1=link1End1, END2=main.randomLink1, OPTION="up" )
        #main.Mininet1.link( END1=link2End1, END2=main.randomLink2, OPTION="up" )
        main.Mininet1.link( END1=link1End1, END2=main.randomLink3, OPTION="up" )
        main.Mininet1.link( END1=link2End1, END2=main.randomLink4, OPTION="up" )
       
        time.sleep( link_sleep )
        topology_output = main.ONOScli2.topology()
        linkUp = main.ONOSbench.checkStatus(
            topology_output,
            main.numMNswitches,
            str( main.numMNlinks ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=linkUp,
            onpass="Link up discovered properly",
            onfail="Link up was not discovered in " +
            str( link_sleep ) +
            " seconds" )

        main.step( "Verify Ping across all hosts" )
        pingResultLinkUp = main.FALSE
        time1 = time.time()
        pingResultLinkUp = main.Mininet1.pingall(timeout = main.pingTimeout)
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResultLinkUp,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult84 = linkUp and pingResultLinkUp
        utilities.assert_equals( expect=main.TRUE, actual=caseResult84,
                                 onpass="Link Up Test PASS",
                                 onfail="Link Up Test FAIL" )
    
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
                        args=[deviceCombos[i][0],deviceCombos[i][1],1,1,"IPV4","",main.MACsDict.get(deviceCombos[i][1])])
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
        intentResult = main.TRUE
        intentsJson = main.ONOScli2.intents()
        getIntentStateResult = main.ONOScli1.getIntentState(intentsId = intentIdList,
                intentsJson = intentsJson)
        print getIntentStateResult
        # Takes awhile for all the onos to get the intents
        time.sleep(30)
        main.step( "Verify Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall(timeout=main.pingTimeout,shortCircuit=True)
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        case90Result = ( intentResult and pingResult )
        
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case90Result,
            onpass="Install 600 point Intents and Ping All test PASS",
            onfail="Install 600 point Intents and Ping All test FAIL" )

    def CASE91( self ):
        """
        Install ###$$$ point intents and verify ping all (Chordal Topology)
        """
        main.log.report( "Add ###$$$ point intents and verify pingall (Chordal Topology)" )
        main.log.report( "_______________________________________" )
        import itertools
        import time
        main.case( "Install ###$$$ point intents" )
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
                        args=[deviceCombos[i][0],deviceCombos[i][1],1,1,"IPV4","",main.MACsDict.get(deviceCombos[i][1])])
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
        intentResult = main.TRUE
        intentsJson = main.ONOScli2.intents()
        getIntentStateResult = main.ONOScli1.getIntentState(intentsId = intentIdList,
                intentsJson = intentsJson)
        print getIntentStateResult
        # Takes awhile for all the onos to get the intents
        time.sleep(30)
        main.step( "Verify Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall(timeout=main.pingTimeout,shortCircuit=True)
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        case91Result = ( intentResult and pingResult )
        
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case91Result,
            onpass="Install ###$$$ point Intents and Ping All test PASS",
            onfail="Install ###$$$ point Intents and Ping All test FAIL" )
    
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
                        args=[deviceCombos[i][0],deviceCombos[i][1],1,1,"IPV4","",main.MACsDict.get(deviceCombos[i][1])])
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
        intentResult = main.TRUE
        intentsJson = main.ONOScli2.intents()
        getIntentStateResult = main.ONOScli1.getIntentState(intentsId = intentIdList,
                intentsJson = intentsJson)
        #print getIntentStateResult
        # Takes awhile for all the onos to get the intents
        time.sleep(60)
        main.step( "Verify Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall(timeout=main.pingTimeout,shortCircuit=True)
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        case92Result = ( intentResult and pingResult )
        
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case92Result,
            onpass="Install 4556 point Intents and Ping All test PASS",
            onfail="Install 4556 point Intents and Ping All test FAIL" )
     
    def CASE93( self ):
        """
        Install multi-single point intents and verify Ping all works
        for att topology
        """
        import copy
        import time
        main.log.report( "Install multi-single point intents and verify Ping all" )
        main.log.report( "___________________________________________" )
        main.case( "Install multi-single point intents and Ping all" )
        deviceDPIDsCopy = copy.copy(main.deviceDPIDs)
        portIngressList = ['1']*(len(deviceDPIDsCopy) - 1)
        intentIdList = []
        print "MACsDict", main.MACsDict
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
                        args =[ingressDeviceList,egressDevice,portIngressList,'1','IPV4','',main.MACsDict.get(egressDevice)])
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
        print intentIdList
        time.sleep(5)
        main.step( "Verify Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall(timeout=main.pingTimeout,shortCircuit=True)
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )

        case93Result = pingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case93Result,
            onpass="Install 25 multi to single point Intents and Ping All test PASS",
            onfail="Install 25 multi to single point Intents and Ping All test FAIL" )
        
    def CASE94( self ):
        """
        Install multi-single point intents and verify Ping all works
        for spine topology
        """
        import copy
        import time
        main.log.report( "Install multi-single point intents and verify Ping all" )
        main.log.report( "___________________________________________" )
        main.case( "Install multi-single point intents and Ping all" )
        deviceDPIDsCopy = copy.copy(main.deviceDPIDs)
        portIngressList = ['1']*(len(deviceDPIDsCopy) - 1)
        intentIdList = []
        print "MACsDict", main.MACsDict
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
                        args =[ingressDeviceList,egressDevice,portIngressList,'1','IPV4','',main.MACsDict.get(egressDevice)])
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
        time.sleep(5)
        main.step( "Verify Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall(timeout=main.pingTimeout,shortCircuit=True)
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )

        case94Result = pingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case94Result,
            onpass="Install 25 multi to single point Intents and Ping All test PASS",
            onfail="Install 25 multi to single point Intents and Ping All test FAIL" )
    
    #def CASE95 multi-single point intent for Spine

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
        print "MACsDict", main.MACsDict
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
                        args =[ingressDevice,egressDeviceList,'1',portEgressList,'IPV4',main.MACsDict.get(ingressDevice)])
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
        time.sleep(5)
        main.step( "Verify Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall(timeout=main.pingTimeout,shortCircuit=True)
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )

        case96Result = pingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case96Result,
            onpass="Install 25 single to multi point Intents and Ping All test PASS",
            onfail="Install 25 single to multi point Intents and Ping All test FAIL" )

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
        print "MACsDict", main.MACsDict
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
                        args =[ingressDevice,egressDeviceList,'1',portEgressList,'IPV4',main.MACsDict.get(ingressDevice),''])
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
        time.sleep(5)
        main.step( "Verify Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall(timeout=main.pingTimeout,shortCircuit=True)
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )

        case97Result = pingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case97Result,
            onpass="Install 25 single to multi point Intents and Ping All test PASS",
            onfail="Install 25 single to multi point Intents and Ping All test FAIL" )

    def CASE10( self ):
        import time
        """
         Remove all Intents
        """
        main.log.report( "Remove all intents that were installed previously" )
        main.log.report( "______________________________________________" )
        main.log.info( "Remove all intents" )
        main.case( "Removing intents" )
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
        intentsList = intentsList[ 1: ]
        intentIdList = []
        step1Result = main.TRUE
        moreIntents = main.TRUE
        removeIntentCount = 0
        intentsCount = len(intentsList)
        print "Current number of intents" , len(intentsList)
        if ( len( intentsList ) > 1 ):
            results = main.TRUE
            main.log.info("Removing intent...")
            while moreIntents:
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
                intentsList1 = intentsList1[ 1: ]
                print "Round %d intents to remove: " %(removeIntentCount)
                print intentsList1
                intentIdList1 = []
                if ( len( intentsList1 ) > 0 ):
                    moreIntents = main.TRUE
                    for i in range( len( intentsList1 ) ):
                        intentsTemp1 = intentsList1[ i ].split( ',' )
                        intentIdList1.append( intentsTemp1[ 0 ].split('=')[1] )
                    print "Leftover Intent IDs: ", intentIdList1
                    print len(intentIdList1)
                    time1 = time.time()
                    for i in xrange( 0, len( intentIdList1 ), int(main.numCtrls) ):
                        pool = []
                        for cli in main.CLIs:
                            if i >= len( intentIdList1 ):
                                break
                            t = main.Thread( target=cli.removeIntent,
                                    threadID=main.threadID,
                                    name="removeIntent",
                                    args=[intentIdList1[i],'org.onosproject.cli',True,False])
                            pool.append(t)
                            t.start()
                            i = i + 1
                            main.threadID = main.threadID + 1
                        for thread in pool:
                            thread.join()
                            intentIdList.append(thread.result)
                    time2 = time.time()
                    main.log.info("Time for removing host intents: %2f seconds" %(time2-time1))
                    time.sleep(10)
                else:
                    time.sleep(15)
                    if len( main.ONOScli1.intents()):
                        continue
                    break

            else:
                print "Removed %d intents" %(intentsCount)
                step1Result = main.TRUE
        else:
            print "No Intent IDs found in Intents list: ", intentsList
            step1Result = main.FALSE

        print main.ONOScli1.intents()
        caseResult10 = step1Result
        utilities.assert_equals( expect=main.TRUE, actual=caseResult10,
                                 onpass="Intent removal test successful",
                                 onfail="Intent removal test failed" )

    def CASE11( self, main ):
        """
        Enable onos-app-ifwd, Verify Intent based Reactive forwarding through ping all and Disable it
        """
        import re
        import copy
        import time

        Thread = imp.load_source('Thread','/home/admin/ONLabTest/TestON/tests/OnosCHO/Thread.py')
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
        
        main.step( "Verify Pingall" )
        ping_result = main.FALSE
        time1 = time.time()
        ping_result = main.Mininet1.pingall(timeout=600)
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        
        if ping_result == main.TRUE:
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

        case11Result = installResult and ping_result and uninstallResult
        utilities.assert_equals( expect=main.TRUE, actual=case11Result,
                                 onpass="Intent based Reactive forwarding Pingall test PASS",
                                 onfail="Intent based Reactive forwarding Pingall test FAIL" )

    def CASE99(self):
        import time
        # WORK AROUND FOR ONOS-581. STOP ONOS BEFORE ASSIGNING CONTROLLERS AT MININET & START ONCE DONE
        main.step( "Stop ONOS on all Nodes" )
        stopResult = main.TRUE
        for i in range( 1, int( main.numCtrls ) + 1 ):
            ONOS_ip = main.params[ 'CTRL' ][ 'ip' + str( i ) ]
            main.log.info( "Stopping ONOS Node IP: " + ONOS_ip )
            sresult = main.ONOSbench.onosStop( ONOS_ip )
            utilities.assert_equals( expect=main.TRUE, actual=sresult,
                                     onpass="Test step PASS",
                                     onfail="Test step FAIL" )
            stopResult = ( stopResult and sresult )

        main.step( "Start ONOS on all Nodes" )
        startResult = main.TRUE
        for i in range( 1, int( main.numCtrls ) + 1 ):
            ONOS_ip = main.params[ 'CTRL' ][ 'ip' + str( i ) ]
            main.log.info( "Starting ONOS Node IP: " + ONOS_ip )
            sresult = main.ONOSbench.onosStart( ONOS_ip )
            utilities.assert_equals( expect=main.TRUE, actual=sresult,
                                     onpass="Test step PASS",
                                     onfail="Test step FAIL" )
            startResult = ( startResult and sresult )
    
        main.step( "Start ONOS CLI on all nodes" )
        cliResult = main.TRUE
        time.sleep( 30 )
        main.log.step(" Start ONOS cli using thread ")
        pool = []
        time1 = time.time()
        for i in range( int( main.numCtrls ) ):
            t = main.Thread(target=main.CLIs[i].startOnosCli,
                    threadID=main.threadID,
                    name="startOnosCli",
                    args=[main.nodes[i].ip_address])
            pool.append(t)
            t.start()
            main.threadID = main.threadID + 1
        for t in pool:
            t.join()
            cliResult = cliResult and t.result
        time2 = time.time()
        
        if not cliResult:
                main.log.info("ONOS CLI did not start up properly")
                #main.cleanup()
                #main.exit()
        else:
            main.log.info("Successful CLI startup")
        main.log.info("Time for connecting to CLI: %2f seconds" %(time2-time1))

        case99Result = ( startResult and cliResult )
        time.sleep(30)
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case99Result,
            onpass="Starting new Chordal topology test PASS",
            onfail="Starting new Chordal topology test FAIL" )




