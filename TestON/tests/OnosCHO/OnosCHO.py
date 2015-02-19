import time
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
        import imp
        ThreadingOnos = imp.load_source('ThreadingOnos','/home/admin/ONLabTest/TestON/tests/OnosCHO/ThreadingOnos.py')
        threadID = 0

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

        main.step( "Removing copy-cat logs from ONOS nodes" )
        main.ONOSbench.onosRemoveRaftLogs()

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
        time.sleep( 20 )

        main.log.step(" Start ONOS cli using thread ")
        
        CLI1 = (main.ONOScli1.startOnosCli,main.ONOS1_ip)
        CLI2 = (main.ONOScli2.startOnosCli,main.ONOS2_ip)
        CLI3 = (main.ONOScli3.startOnosCli,main.ONOS3_ip)
        CLI4 = (main.ONOScli4.startOnosCli,main.ONOS4_ip)
        CLI5 = (main.ONOScli5.startOnosCli,main.ONOS5_ip)
        ONOSCLI = [CLI1,CLI2,CLI3,CLI4,CLI5]
        pool = []
        time1 = time.time()
        for cli,ip in ONOSCLI:
            t = ThreadingOnos.ThreadingOnos(target=cli,threadID=threadID,
                    name="startOnosCli",args=[ip])
            pool.append(t)
            t.start()
            threadID = threadID + 1
            
        case1Result  = main.FALSE
        results = []
        for thread in pool:
            thread.join()
            results.append(thread.result)
        time2 = time.time()
        
        if( all(result == main.TRUE for result in results) == False):
                main.log.info("ONOS CLI did not start up properly")
                main.cleanup()
                main.exit()
        else:
            main.log.info("Successful CLI startup!!!")
            case1Result = main.TRUE
        main.log.info("Time for connecting to CLI: %2f seconds" %(time2-time1))
        utilities.assert_equals( expect=main.TRUE, actual=case1Result,
                                 onpass="Set up test environment PASS",
                                 onfail="Set up test environment FAIL" )

    def CASE2( self, main ):
        """
        This test loads a Topology (ATT) on Mininet and balances all switches.
        """
        import re
        import time
        import copy
        main.numMNswitches = int ( main.params[ 'TOPO1' ][ 'numSwitches' ] )
        main.numMNlinks = int ( main.params[ 'TOPO1' ][ 'numLinks' ] )
        main.numMNhosts = int ( main.params[ 'TOPO1' ][ 'numHosts' ] )

        main.log.report(
            "Assign and Balance all Mininet switches across controllers" )
        main.log.report(
            "_________________________________________________________" )
        # need to wait here for sometime. This will be removed once ONOS is
        # stable enough
        time.sleep( 15 )
        main.case(
            "Assign and Balance all Mininet switches across controllers" )
        main.step( "Assign switches to controllers" )
        netStatus = main.Mininet1.startNet()
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
        time.sleep( 15 )

        #main.step( "Balance devices across controllers" )
        #for i in range( int( main.numCtrls ) ):
        #    balanceResult = main.ONOScli1.balanceMasters()
            # giving some breathing time for ONOS to complete re-balance
        #    time.sleep( 3 )

        #utilities.assert_equals(
         #   expect=main.TRUE,
          #  actual=balanceResult,
           # onpass="Assign and Balance devices test PASS",
            #onfail="Assign and Balance devices test FAIL" )

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
        main.case( "Collect and Store Topology Deatils from ONOS" )

        main.step( "Collect and store current number of switches and links" )
        topology_output = main.ONOScli1.topology()
        topology_result = main.ONOSbench.getTopology( topology_output )
        numOnosDevices = topology_result[ 'devices' ]
        numOnosLinks = topology_result[ 'links' ]

        if ( ( main.numMNswitches == int(numOnosDevices) ) and ( main.numMNlinks == int(numOnosLinks) ) ):
            main.step( "Store Device DPIDs" )
            for i in range( 1, (main.numMNswitches+1) ):
                main.deviceDPIDs.append( "of:00000000000000" + format( i, '02x' ) )
            print "Device DPIDs in Store: \n", str( main.deviceDPIDs )

            main.step( "Store Host MACs" )
            for i in range( 1, ( main.numMNhosts + 1 ) ):
                main.hostMACs.append( "00:00:00:00:00:" + format( i, '02x' ) + "/-1" )
            print "Host MACs in Store: \n", str( main.hostMACs )

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
            for i in range( 1, ( main.numMNswitches + 1) ):
                portResult = main.ONOScli1.getDevicePortsEnabledCount(
                    "of:00000000000000" + format( i,'02x' ) )
                portTemp = re.split( r'\t+', portResult )
                portCount = portTemp[ 1 ].replace( "\r\r\n\x1b[32m", "" )
                main.devicePortsEnabledCount.append( portCount )
            print "Device Enabled Port Counts Stored: \n", str( main.devicePortsEnabledCount )

            main.step( "Collect and store each Device active links Count" )
            for i in range( 1, ( main.numMNswitches + 1) ):
                linkCountResult = main.ONOScli1.getDeviceLinksActiveCount(
                    "of:00000000000000" + format( i,'02x' ) )
                linkCountTemp = re.split( r'\t+', linkCountResult )
                linkCount = linkCountTemp[ 1 ].replace( "\r\r\n\x1b[32m", "" )
                main.deviceActiveLinksCount.append( linkCount )
            print "Device Active Links Count Stored: \n", str( main.deviceActiveLinksCount )

        else:
            main.log.info("Devices (expected): %s, Links (expected): %s" % 
                    ( str( main.numMNswitches ), str( main.numMNlinks ) ) )
            main.log.info("Devices (actual): %s, Links (actual): %s" %
                    ( numOnosDevices , numOnosLinks ) )
            main.log.info("Topology does not match, exiting CHO test...")
            time.sleep(300)
            #main.cleanup()
            #main.exit()

        # just returning TRUE for now as this one just collects data
        case3Result = main.TRUE
        utilities.assert_equals( expect=main.TRUE, actual=case3Result,
                                 onpass="Saving ONOS topology data test PASS",
                                 onfail="Saving ONOS topology data test FAIL" )

    def CASE4( self, main ):
        """
        Enable onos-app-fwd, Verify Reactive forwarding through ping all and Disable it
        """
        import re
        import copy
        import time
        import imp

        ThreadingOnos = imp.load_source('ThreadingOnos','/home/admin/ONLabTest/TestON/tests/OnosCHO/ThreadingOnos.py')
        threadID = 6

        main.log.report( "Enable Reactive forwarding and Verify ping all" )
        main.log.report( "______________________________________________" )
        main.case( "Enable Reactive forwarding and Verify ping all" )
        main.step( "Enable Reactive forwarding" )
        installResult = main.TRUE
        
        CLI1 = (main.ONOScli1.featureInstall,"onos-app-fwd")
        CLI2 = (main.ONOScli2.featureInstall,"onos-app-fwd")
        CLI3 = (main.ONOScli3.featureInstall,"onos-app-fwd")
        CLI4 = (main.ONOScli4.featureInstall,"onos-app-fwd")
        CLI5 = (main.ONOScli5.featureInstall,"onos-app-fwd")
        ONOSCLI = [CLI1,CLI2,CLI3,CLI4,CLI5]
        pool = []
        time1 = time.time()
        for cli,feature in ONOSCLI:
            t = ThreadingOnos.ThreadingOnos(target=cli,threadID=threadID,
                    name="featureInstall",args=[feature])
            pool.append(t)
            t.start()
            threadID = threadID + 1
            
        case4Result1  = main.FALSE
        results = []
        for thread in pool:
            thread.join()
            results.append(thread.result)
        time2 = time.time()
        
        if( all(result == main.TRUE for result in results) == False):
                main.log.info("Did not install onos-app-fwd feature properly")
                main.cleanup()
                main.exit()
        else:
            main.log.info("Successful feature:install onos-app-fwd!!!")
            case4Result1 = main.TRUE
        main.log.info("Time for feature:install onos-app-fwd: %2f seconds" %(time2-time1))
        
        time.sleep( 5 )

        main.step( "Verify Pingall" )
        ping_result = main.FALSE
        time1 = time.time()
        ping_result = main.Mininet1.pingall(timeout=60)
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
        uninstallResult = main.TRUE
        
        CLI1 = (main.ONOScli1.featureUninstall,"onos-app-fwd")
        CLI2 = (main.ONOScli2.featureUninstall,"onos-app-fwd")
        CLI3 = (main.ONOScli3.featureUninstall,"onos-app-fwd")
        CLI4 = (main.ONOScli4.featureUninstall,"onos-app-fwd")
        CLI5 = (main.ONOScli5.featureUninstall,"onos-app-fwd")
        ONOSCLI = [CLI1,CLI2,CLI3,CLI4,CLI5]
        pool = []
        time1 = time.time()
        for cli,feature in ONOSCLI:
            t = ThreadingOnos.ThreadingOnos(target=cli,threadID=threadID,
                    name="featureUninstall",args=[feature])
            pool.append(t)
            t.start()
            threadID = threadID + 1
            
        case4Result2  = main.FALSE
        results = []
        for thread in pool:
            thread.join()
            results.append(thread.result)
        time2 = time.time()
        
        if( all(result == main.TRUE for result in results) == False):
                main.log.info("Did not uninstall onos-app-fwd feature properly")
                main.cleanup()
                main.exit()
        else:
            main.log.info("Successful feature:uninstall onos-app-fwd!!!")
            case4Result2 = main.TRUE
        main.log.info("Time for feature:uninstall onos-app-fwd: %2f seconds" %(time2-time1))

        # Waiting for reative flows to be cleared.
        time.sleep( 5 )
        
        case4Result = case4Result1 and case4Result2
        utilities.assert_equals( expect=main.TRUE, actual=case4Result,
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
        for i in range( 1, 26 ):
            portResult = main.ONOScli1.getDevicePortsEnabledCount(
                "of:00000000000000" +
                format(
                    i,
                    '02x' ) )
            portTemp = re.split( r'\t+', portResult )
            portCount = portTemp[ 1 ].replace( "\r\r\n\x1b[32m", "" )
            devicePortsEnabledCountTemp.append( portCount )
            time.sleep( 2 )
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
        for i in range( 1, 26 ):
            linkResult = main.ONOScli1.getDeviceLinksActiveCount(
                "of:00000000000000" +
                format(
                    i,
                    '02x' ) )
            linkTemp = re.split( r'\t+', linkResult )
            linkCount = linkTemp[ 1 ].replace( "\r\r\n\x1b[32m", "" )
            deviceActiveLinksCountTemp.append( linkCount )
            time.sleep( 3 )
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

    def CASE6( self ):
        """
        Install 300 host intents and verify ping all
        """
        main.log.report( "Add 300 host intents and verify pingall" )
        main.log.report( "_______________________________________" )
        import itertools

        main.case( "Install 300 host intents" )
        main.step( "Add host Intents" )
        intentResult = main.TRUE
        hostCombos = list( itertools.combinations( main.hostMACs, 2 ) )
        for i in range( len( hostCombos ) ):
            iResult = main.ONOScli1.addHostIntent(
                hostCombos[ i ][ 0 ],
                hostCombos[ i ][ 1 ] )
            intentResult = ( intentResult and iResult )

        main.step( "Verify Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall()
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        case4Result = ( intentResult and pingResult )
        #case4Result = pingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case4Result,
            onpass="Install 300 Host Intents and Ping All test PASS",
            onfail="Install 300 Host Intents and Ping All test FAIL" )

    def CASE70( self, main ):
        """
        Randomly bring some core links down and verify ping all ( Host Intents Scenario )
        """
        import random
        main.randomLink1 = []
        main.randomLink2 = []
        main.randomLink3 = []
        link1End1 = main.params[ 'CORELINKS' ][ 'linkS3a' ]
        link1End2 = main.params[ 'CORELINKS' ][ 'linkS3b' ].split( ',' )
        link2End1 = main.params[ 'CORELINKS' ][ 'linkS14a' ]
        link2End2 = main.params[ 'CORELINKS' ][ 'linkS14b' ].split( ',' )
        link3End1 = main.params[ 'CORELINKS' ][ 'linkS18a' ]
        link3End2 = main.params[ 'CORELINKS' ][ 'linkS18b' ].split( ',' )
        switchLinksToToggle = main.params[ 'CORELINKS' ][ 'toggleLinks' ]
        link_sleep = int( main.params[ 'timers' ][ 'LinkDiscovery' ] )

        main.log.report( "Host intents - Randomly bring some core links down and verify ping all" )
        main.log.report( "_________________________________________________________________" )
        main.case( "Host intents - Randomly bring some core links down and verify ping all" )
        main.step( "Verify number of Switch links to toggle on each Core Switch are between 1 - 5" )
        if ( int( switchLinksToToggle ) ==
             0 or int( switchLinksToToggle ) > 5 ):
            main.log.info( "Please check your PARAMS file. Valid range for number of switch links to toggle is between 1 to 5" )
            main.cleanup()
            main.exit()
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
        pingResultLinkDown = main.Mininet1.pingall()
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
        Bring the core links up that are down and verify ping all ( Host Intents Scenario )
        """
        import random
        link1End1 = main.params[ 'CORELINKS' ][ 'linkS3a' ]
        link2End1 = main.params[ 'CORELINKS' ][ 'linkS14a' ]
        link3End1 = main.params[ 'CORELINKS' ][ 'linkS18a' ]
        link_sleep = int( main.params[ 'timers' ][ 'LinkDiscovery' ] )
        switchLinksToToggle = main.params[ 'CORELINKS' ][ 'toggleLinks' ]

        main.log.report(
            "Host intents - Bring the core links up that are down and verify ping all" )
        main.log.report(
            "__________________________________________________________________" )
        main.case(
            "Host intents - Bring the core links up that are down and verify ping all" )
        main.step( "Bring randomly cut links on Core devices up" )
        for i in range( int( switchLinksToToggle ) ):
            main.Mininet1.link(
                END1=link1End1,
                END2=randomLink1[ i ],
                OPTION="up" )
            main.Mininet1.link(
                END1=link2End1,
                END2=randomLink2[ i ],
                OPTION="up" )
            main.Mininet1.link(
                END1=link3End1,
                END2=randomLink3[ i ],
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
        Randomly bring some core links down and verify ping all ( Point Intents Scenario )
        """
        import random
        main.randomLink1 = []
        main.randomLink2 = []
        main.randomLink3 = []
        link1End1 = main.params[ 'CORELINKS' ][ 'linkS3a' ]
        link1End2 = main.params[ 'CORELINKS' ][ 'linkS3b' ].split( ',' )
        link2End1 = main.params[ 'CORELINKS' ][ 'linkS14a' ]
        link2End2 = main.params[ 'CORELINKS' ][ 'linkS14b' ].split( ',' )
        link3End1 = main.params[ 'CORELINKS' ][ 'linkS18a' ]
        link3End2 = main.params[ 'CORELINKS' ][ 'linkS18b' ].split( ',' )
        switchLinksToToggle = main.params[ 'CORELINKS' ][ 'toggleLinks' ]
        link_sleep = int( main.params[ 'timers' ][ 'LinkDiscovery' ] )

        main.log.report( "Point Intents - Randomly bring some core links down and verify ping all" )
        main.log.report( "__________________________________________________________________" )
        main.case( "Point Intents - Randomly bring some core links down and verify ping all" )
        main.step( "Verify number of Switch links to toggle on each Core Switch are between 1 - 5" )
        if ( int( switchLinksToToggle ) ==
             0 or int( switchLinksToToggle ) > 5 ):
            main.log.info(
                "Please check you PARAMS file. Valid range for number of switch links to toggle is between 1 to 5" )
            main.cleanup()
            main.exit()
        else:
            main.log.info(
                "User provided Core switch links range to toggle is correct, proceeding to run the test" )

        main.step( "Cut links on Core devices using user provided range" )
        randomLink1 = random.sample( link1End2, int( switchLinksToToggle ) )
        randomLink2 = random.sample( link2End2, int( switchLinksToToggle ) )
        randomLink3 = random.sample( link3End2, int( switchLinksToToggle ) )
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
            topology_output, main.numSwitches, str(
                int( main.numLinks ) - int( switchLinksToToggle ) * 6 ) )
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
        pingResultLinkDown = main.Mininet1.pingall()
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResultLinkDown,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        caseResult7 = linkDown and pingResultLinkDown
        utilities.assert_equals( expect=main.TRUE, actual=caseResult7,
                                 onpass="Random Link cut Test PASS",
                                 onfail="Random Link cut Test FAIL" )

    def CASE81( self, main ):
        """
        Bring the core links up that are down and verify ping all ( Point Intents Scenario )
        """
        import random
        link1End1 = main.params[ 'CORELINKS' ][ 'linkS3a' ]
        link2End1 = main.params[ 'CORELINKS' ][ 'linkS14a' ]
        link3End1 = main.params[ 'CORELINKS' ][ 'linkS18a' ]
        link_sleep = int( main.params[ 'timers' ][ 'LinkDiscovery' ] )
        switchLinksToToggle = main.params[ 'CORELINKS' ][ 'toggleLinks' ]

        main.log.report(
            "Point intents - Bring the core links up that are down and verify ping all" )
        main.log.report(
            "___________________________________________________________________" )
        main.case(
            "Point intents - Bring the core links up that are down and verify ping all" )
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

        caseResult81 = linkUp and pingResultLinkUp
        utilities.assert_equals( expect=main.TRUE, actual=caseResult81,
                                 onpass="Link Up Test PASS",
                                 onfail="Link Up Test FAIL" )

    def CASE9( self ):
        """
        Install 114 point intents and verify Ping all works
        """
        import copy
        main.log.report( "Install 114 point intents and verify Ping all" )
        main.log.report( "___________________________________________" )
        main.case( "Install 114 point intents and Ping all" )
        deviceLinksCopy = copy.copy( main.deviceLinks )
        main.step( "Install 114 point intents" )
        for i in range( len( deviceLinksCopy ) ):
            pointLink = str(
                deviceLinksCopy[ i ] ).replace(
                "src=",
                "" ).replace(
                "dst=",
                "" ).split( ',' )
            point1 = pointLink[ 0 ].split( '/' )
            point2 = pointLink[ 1 ].split( '/' )
            installResult = main.ONOScli1.addPointIntent(
                point1[ 0 ], point2[ 0 ], int(
                    point1[ 1 ] ), int(
                    point2[ 1 ] ) )
            if installResult == main.TRUE:
                print "Installed Point intent between :", point1[ 0 ], int( point1[ 1 ] ), point2[ 0 ], int( point2[ 1 ] )

        main.step( "Obtain the intent id's" )
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
        for i in range( len( intentsList ) ):
            intentsTemp = intentsList[ i ].split( ',' )
            intentIdList.append( intentsTemp[ 0 ] )
        print "Intent IDs: ", intentIdList
        print "Total Intents installed: ", len( intentIdList )

        main.step( "Verify Ping across all hosts" )
        pingResult = main.FALSE
        time1 = time.time()
        pingResult = main.Mininet1.pingall()
        time2 = time.time()
        timeDiff = round( ( time2 - time1 ), 2 )
        main.log.report(
            "Time taken for Ping All: " +
            str( timeDiff ) +
            " seconds" )
        utilities.assert_equals( expect=main.TRUE, actual=pingResult,
                                 onpass="PING ALL PASS",
                                 onfail="PING ALL FAIL" )

        case8_result = installResult and pingResult
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case8_result,
            onpass="Ping all test after Point intents addition successful",
            onfail="Ping all test after Point intents addition failed" )

    def CASE10( self ):
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
        if ( len( intentsList ) > 1 ):
            for i in range( len( intentsList ) ):
                intentsTemp = intentsList[ i ].split( ',' )
                intentIdList.append( intentsTemp[ 0 ] )
            print "Intent IDs: ", intentIdList
            for id in range( len( intentIdList ) ):
                print "Removing intent id (round 1) :", intentIdList[ id ]
                main.ONOScli1.removeIntent( intentId=intentIdList[ id ] )
                #time.sleep( 1 )

            main.log.info(
                "Verify all intents are removed and if any leftovers try remove one more time" )
            intentsList1 = main.ONOScli1.getAllIntentIds()
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
            print "Round 2 (leftover) intents to remove: ", intentsList1
            intentIdList1 = []
            if ( len( intentsList1 ) > 1 ):
                for i in range( len( intentsList1 ) ):
                    intentsTemp1 = intentsList[ i ].split( ',' )
                    intentIdList1.append( intentsTemp1[ 0 ] )
                print "Leftover Intent IDs: ", intentIdList1
                for id in range( len( intentIdList1 ) ):
                    print "Removing intent id (round 2):", intentIdList1[ id ]
                    main.ONOScli1.removeIntent(
                        intentId=intentIdList1[ id ] )
                    #time.sleep( 2 )
            else:
                print "There are no more intents that need to be removed"
                step1Result = main.TRUE
        else:
            print "No Intent IDs found in Intents list: ", intentsList
            step1Result = main.FALSE

        caseResult7 = step1Result
        utilities.assert_equals( expect=main.TRUE, actual=caseResult7,
                                 onpass="Intent removal test successful",
                                 onfail="Intent removal test failed" )

    def CASE11( self, main ):
        """
        Enable onos-app-ifwd, Verify Intent based Reactive forwarding through ping all and Disable it
        """
        import re
        import copy
        import time

        main.log.report( "Enable Intent based Reactive forwarding and Verify ping all" )
        main.log.report( "_____________________________________________________" )
        main.case( "Enable Intent based Reactive forwarding and Verify ping all" )
        main.step( "Enable intent based Reactive forwarding" )
        installResult = main.TRUE
        for i in range( 1, int( main.numCtrls ) + 1 ):
            onosFeature = 'onos-app-ifwd'
            ONOS_ip = main.params[ 'CTRL' ][ 'ip' + str( i ) ]
            ONOScli = 'ONOScli' + str( i )
            main.log.info( "Enabling Intent based Reactive forwarding on ONOS Node " + ONOS_ip )
            exec "inResult=main." + ONOScli + ".featureInstall(onosFeature)"
            time.sleep( 3 )
            installResult = inResult and installResult

        time.sleep( 5 )

        main.step( "Verify Pingall" )
        ping_result = main.FALSE
        time1 = time.time()
        ping_result = main.Mininet1.pingall()
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
        uninstallResult = main.TRUE
        for i in range( 1, int( main.numCtrls ) + 1 ):
            onosFeature = 'onos-app-ifwd'
            ONOS_ip = main.params[ 'CTRL' ][ 'ip' + str( i ) ]
            ONOScli = 'ONOScli' + str( i )
            main.log.info( "Disabling Intent based Reactive forwarding on ONOS Node " + ONOS_ip )
            exec "unResult=main." + ONOScli + ".featureUninstall(onosFeature)"
            uninstallResult = unResult and uninstallResult

        # Waiting for reative flows to be cleared.
        time.sleep( 10 )

        case11Result = installResult and ping_result and uninstallResult
        utilities.assert_equals( expect=main.TRUE, actual=case11Result,
                                 onpass="Intent based Reactive forwarding Pingall test PASS",
                                 onfail="Intent based Reactive forwarding Pingall test FAIL" )

    def CASE12( self, main ):
        """
        This test script Loads a new Topology (Chordal) on CHO setup and balances all switches
        """
        import re
        import time
        import copy
        import imp

        ThreadingOnos = imp.load_source('ThreadingOnos','/home/admin/ONLabTest/TestON/tests/OnosCHO/ThreadingOnos.py')
        threadID = 0
        newTopo = main.params['TOPO2']['topo']
        main.numMNswitches = int ( main.params[ 'TOPO2' ][ 'numSwitches' ] )
        main.numMNlinks = int ( main.params[ 'TOPO2' ][ 'numLinks' ] )
        main.numMNhosts = int ( main.params[ 'TOPO2' ][ 'numHosts' ] )

        main.log.report(
            "Load Chordal topology and Balance all Mininet switches across controllers" )
        main.log.report(
            "________________________________________________________________________" )
        # need to wait here for sometime until ONOS bootup
        time.sleep( 15 )
        main.case(
            "Assign and Balance all Mininet switches across controllers" )
        main.step( "Stop any previous Mininet network topology" )
        stopStatus = main.Mininet1.stopNet()

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

        main.step( "Start Mininet with Chordal topology" )
        startStatus = main.Mininet1.startNet(topoFile = newTopo)

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
        #karafTimeout = "3600000" # This is not needed here as it is already set before.
        # need to wait here sometime for ONOS to bootup.
        time.sleep( 30 )

        main.log.step(" Start ONOS cli using thread ")
        
        CLI1 = (main.ONOScli1.startOnosCli,main.ONOS1_ip)
        CLI2 = (main.ONOScli2.startOnosCli,main.ONOS2_ip)
        CLI3 = (main.ONOScli3.startOnosCli,main.ONOS3_ip)
        CLI4 = (main.ONOScli4.startOnosCli,main.ONOS4_ip)
        CLI5 = (main.ONOScli5.startOnosCli,main.ONOS5_ip)
        ONOSCLI = [CLI1,CLI2,CLI3,CLI4,CLI5]
        pool = []
        time1 = time.time()
        for cli,ip in ONOSCLI:
            t = ThreadingOnos.ThreadingOnos(target=cli,threadID=threadID,
                    name="startOnosCli",args=[ip])
            pool.append(t)
            t.start()
            threadID = threadID + 1
            
        cliResult  = main.FALSE
        results = []
        for thread in pool:
            thread.join()
            results.append(thread.result)
        time2 = time.time()
        
        if( all(result == main.TRUE for result in results) == False):
                main.log.info("ONOS CLI did not start up properly")
                main.cleanup()
                main.exit()
        else:
            main.log.info("Successful CLI startup!!!")
            cliResult = main.TRUE
        main.log.info("Time for connecting to CLI: %2f seconds" %(time2-time1))

        main.step( "Balance devices across controllers" )
        for i in range( int( main.numCtrls ) ):
            balanceResult = main.ONOScli1.balanceMasters()
            # giving some breathing time for ONOS to complete re-balance
            time.sleep( 3 )

        case12Result = ( startResult and cliResult )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case12Result,
            onpass="Starting new Chordal topology test PASS",
            onfail="Starting new Chordal topology test FAIL" )

    def CASE13( self, main ):
        """
        This test script Loads a new Topology (Spine) on CHO setup and balances all switches
        """
        import re
        import time
        import copy

        newTopo = main.params['TOPO3']['topo']
        main.numMNswitches = int ( main.params[ 'TOPO3' ][ 'numSwitches' ] )
        main.numMNlinks = int ( main.params[ 'TOPO3' ][ 'numLinks' ] )
        main.numMNhosts = int ( main.params[ 'TOPO3' ][ 'numHosts' ] )

        main.log.report(
            "Load Spine and Leaf topology and Balance all Mininet switches across controllers" )
        main.log.report(
            "________________________________________________________________________" )
        # need to wait here for sometime until ONOS bootup
        time.sleep( 15 )
        main.case(
            "Assign and Balance all Mininet switches across controllers" )
        main.step( "Stop any previous Mininet network topology" )
        stopStatus = main.Mininet1.stopNet()

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

        main.step( "Start Mininet with Spine topology" )
        startStatus = main.Mininet1.startNet(topoFile = newTopo)

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
        #karafTimeout = "3600000" # This is not needed here as it is already set before.
        # need to wait here sometime for ONOS to bootup.
        time.sleep( 30 )
        
        main.log.step(" Start ONOS cli using thread ")
        
        CLI1 = (main.ONOScli1.startOnosCli,main.ONOS1_ip)
        CLI2 = (main.ONOScli2.startOnosCli,main.ONOS2_ip)
        CLI3 = (main.ONOScli3.startOnosCli,main.ONOS3_ip)
        CLI4 = (main.ONOScli4.startOnosCli,main.ONOS4_ip)
        CLI5 = (main.ONOScli5.startOnosCli,main.ONOS5_ip)
        ONOSCLI = [CLI1,CLI2,CLI3,CLI4,CLI5]
        pool = []
        time1 = time.time()
        for cli,ip in ONOSCLI:
            t = ThreadingOnos.ThreadingOnos(target=cli,threadID=threadID,
                    name="startOnosCli",args=[ip])
            pool.append(t)
            t.start()
            threadID = threadID + 1
            
        cliResult  = main.FALSE
        results = []
        for thread in pool:
            thread.join()
            results.append(thread.result)
        time2 = time.time()
        
        if( all(result == main.TRUE for result in results) == False):
                main.log.info("ONOS CLI did not start up properly")
                main.cleanup()
                main.exit()
        else:
            main.log.info("Successful CLI startup!!!")
            cliResult = main.TRUE
        main.log.info("Time for connecting to CLI: %2f seconds" %(time2-time1))

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

        case13Result = ( startResult and cliResult )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=case13Result,
            onpass="Starting new Spine topology test PASS",
            onfail="Starting new Spine topology test FAIL" )
