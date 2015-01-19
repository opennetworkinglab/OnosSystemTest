"""
Description: This test is to determine if the HA test setup is
    working correctly. There are no failures so this test should
    have a 100% pass rate

List of test cases:
CASE1: Compile ONOS and push it to the test machines
CASE2: Assign mastership to controllers
CASE3: Assign intents
CASE4: Ping across added host intents
CASE5: Reading state of ONOS
CASE6: The Failure case. Since this is the Sanity test, we do nothing.
CASE7: Check state after control plane failure
CASE8: Compare topo
CASE9: Link s3-s28 down
CASE10: Link s3-s28 up
CASE11: Switch down
CASE12: Switch up
CASE13: Clean up
CASE14: start election app on all onos nodes
CASE15: Check that Leadership Election is still functional
"""
class HATestSanity:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        CASE1 is to compile ONOS and push it to the test machines

        Startup sequence:
        git pull
        mvn clean install
        onos-package
        cell <name>
        onos-verify-cell
        NOTE: temporary - onos-remove-raft-logs
        onos-install -f
        onos-wait-for-start
        """
        main.log.report( "ONOS HA Sanity test - initialization" )
        main.case( "Setting up test environment" )
        # TODO: save all the timers and output them for plotting

        # load some vairables from the params file
        PULL_CODE = False
        if main.params[ 'Git' ] == 'True':
            PULL_CODE = True

        cell_name = main.params[ 'ENV' ][ 'cellName' ]

        # set global variables
        global ONOS1_ip
        global ONOS1_port
        global ONOS2_ip
        global ONOS2_port
        global ONOS3_ip
        global ONOS3_port
        global ONOS4_ip
        global ONOS4_port
        global ONOS5_ip
        global ONOS5_port
        global ONOS6_ip
        global ONOS6_port
        global ONOS7_ip
        global ONOS7_port
        global num_controllers

        ONOS1_ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS1_port = main.params[ 'CTRL' ][ 'port1' ]
        ONOS2_ip = main.params[ 'CTRL' ][ 'ip2' ]
        ONOS2_port = main.params[ 'CTRL' ][ 'port2' ]
        ONOS3_ip = main.params[ 'CTRL' ][ 'ip3' ]
        ONOS3_port = main.params[ 'CTRL' ][ 'port3' ]
        ONOS4_ip = main.params[ 'CTRL' ][ 'ip4' ]
        ONOS4_port = main.params[ 'CTRL' ][ 'port4' ]
        ONOS5_ip = main.params[ 'CTRL' ][ 'ip5' ]
        ONOS5_port = main.params[ 'CTRL' ][ 'port5' ]
        ONOS6_ip = main.params[ 'CTRL' ][ 'ip6' ]
        ONOS6_port = main.params[ 'CTRL' ][ 'port6' ]
        ONOS7_ip = main.params[ 'CTRL' ][ 'ip7' ]
        ONOS7_port = main.params[ 'CTRL' ][ 'port7' ]
        num_controllers = int( main.params[ 'num_controllers' ] )

        main.step( "Applying cell variable to environment" )
        cell_result = main.ONOSbench.set_cell( cell_name )
        verify_result = main.ONOSbench.verify_cell()

        # FIXME:this is short term fix
        main.log.report( "Removing raft logs" )
        main.ONOSbench.onos_remove_raft_logs()
        main.log.report( "Uninstalling ONOS" )
        main.ONOSbench.onos_uninstall( ONOS1_ip )
        main.ONOSbench.onos_uninstall( ONOS2_ip )
        main.ONOSbench.onos_uninstall( ONOS3_ip )
        main.ONOSbench.onos_uninstall( ONOS4_ip )
        main.ONOSbench.onos_uninstall( ONOS5_ip )
        main.ONOSbench.onos_uninstall( ONOS6_ip )
        main.ONOSbench.onos_uninstall( ONOS7_ip )

        clean_install_result = main.TRUE
        git_pull_result = main.TRUE

        main.step( "Compiling the latest version of ONOS" )
        if PULL_CODE:
            # TODO Configure branch in params
            main.step( "Git checkout and pull master" )
            main.ONOSbench.git_checkout( "master" )
            git_pull_result = main.ONOSbench.git_pull()

            main.step( "Using mvn clean & install" )
            clean_install_result = main.TRUE
            if git_pull_result == main.TRUE:
                clean_install_result = main.ONOSbench.clean_install()
            else:
                main.log.warn( "Did not pull new code so skipping mvn " +
                               "clean install" )
        main.ONOSbench.get_version( report=True )

        main.step( "Creating ONOS package" )
        package_result = main.ONOSbench.onos_package()

        main.step( "Installing ONOS package" )
        onos1_install_result = main.ONOSbench.onos_install( options="-f",
                                                            node=ONOS1_ip )
        onos2_install_result = main.ONOSbench.onos_install( options="-f",
                                                            node=ONOS2_ip )
        onos3_install_result = main.ONOSbench.onos_install( options="-f",
                                                            node=ONOS3_ip )
        onos4_install_result = main.ONOSbench.onos_install( options="-f",
                                                            node=ONOS4_ip )
        onos5_install_result = main.ONOSbench.onos_install( options="-f",
                                                            node=ONOS5_ip )
        onos6_install_result = main.ONOSbench.onos_install( options="-f",
                                                            node=ONOS6_ip )
        onos7_install_result = main.ONOSbench.onos_install( options="-f",
                                                            node=ONOS7_ip )
        onos_install_result = onos1_install_result and onos2_install_result\
            and onos3_install_result and onos4_install_result\
            and onos5_install_result and onos6_install_result\
            and onos7_install_result

        main.step( "Checking if ONOS is up yet" )
        # TODO check bundle:list?
        for i in range( 2 ):
            onos1_isup = main.ONOSbench.isup( ONOS1_ip )
            if not onos1_isup:
                main.log.report( "ONOS1 didn't start!" )
            onos2_isup = main.ONOSbench.isup( ONOS2_ip )
            if not onos2_isup:
                main.log.report( "ONOS2 didn't start!" )
            onos3_isup = main.ONOSbench.isup( ONOS3_ip )
            if not onos3_isup:
                main.log.report( "ONOS3 didn't start!" )
            onos4_isup = main.ONOSbench.isup( ONOS4_ip )
            if not onos4_isup:
                main.log.report( "ONOS4 didn't start!" )
            onos5_isup = main.ONOSbench.isup( ONOS5_ip )
            if not onos5_isup:
                main.log.report( "ONOS5 didn't start!" )
            onos6_isup = main.ONOSbench.isup( ONOS6_ip )
            if not onos6_isup:
                main.log.report( "ONOS6 didn't start!" )
            onos7_isup = main.ONOSbench.isup( ONOS7_ip )
            if not onos7_isup:
                main.log.report( "ONOS7 didn't start!" )
            onos_isup_result = onos1_isup and onos2_isup and onos3_isup\
                and onos4_isup and onos5_isup and onos6_isup and onos7_isup
            if onos_isup_result == main.TRUE:
                break

        cli_result1 = main.ONOScli1.start_onos_cli( ONOS1_ip )
        cli_result2 = main.ONOScli2.start_onos_cli( ONOS2_ip )
        cli_result3 = main.ONOScli3.start_onos_cli( ONOS3_ip )
        cli_result4 = main.ONOScli4.start_onos_cli( ONOS4_ip )
        cli_result5 = main.ONOScli5.start_onos_cli( ONOS5_ip )
        cli_result6 = main.ONOScli6.start_onos_cli( ONOS6_ip )
        cli_result7 = main.ONOScli7.start_onos_cli( ONOS7_ip )
        cli_results = cli_result1 and cli_result2 and cli_result3 and\
            cli_result4 and cli_result5 and cli_result6 and cli_result7

        main.step( "Start Packet Capture MN" )
        main.Mininet2.start_tcpdump(
            str( main.params[ 'MNtcpdump' ][ 'folder' ] ) + str( main.TEST )
            + "-MN.pcap",
            intf=main.params[ 'MNtcpdump' ][ 'intf' ],
            port=main.params[ 'MNtcpdump' ][ 'port' ] )

        case1_result = ( clean_install_result and package_result and
                         cell_result and verify_result and onos_install_result
                         and onos_isup_result and cli_results )

        utilities.assert_equals( expect=main.TRUE, actual=case1_result,
                                 onpass="Test startup successful",
                                 onfail="Test startup NOT successful" )

        if case1_result == main.FALSE:
            main.cleanup()
            main.exit()

    def CASE2( self, main ):
        """
        Assign mastership to controllers
        """
        import re

        main.log.report( "Assigning switches to controllers" )
        main.case( "Assigning Controllers" )
        main.step( "Assign switches to controllers" )

        for i in range( 1, 29 ):
            main.Mininet1.assign_sw_controller(
                sw=str( i ),
                count=num_controllers,
                ip1=ONOS1_ip, port1=ONOS1_port,
                ip2=ONOS2_ip, port2=ONOS2_port,
                ip3=ONOS3_ip, port3=ONOS3_port,
                ip4=ONOS4_ip, port4=ONOS4_port,
                ip5=ONOS5_ip, port5=ONOS5_port,
                ip6=ONOS6_ip, port6=ONOS6_port,
                ip7=ONOS7_ip, port7=ONOS7_port )

        mastership_check = main.TRUE
        for i in range( 1, 29 ):
            response = main.Mininet1.get_sw_controller( "s" + str( i ) )
            try:
                main.log.info( str( response ) )
            except:
                main.log.info( repr( response ) )
            if re.search( "tcp:" + ONOS1_ip, response )\
                    and re.search( "tcp:" + ONOS2_ip, response )\
                    and re.search( "tcp:" + ONOS3_ip, response )\
                    and re.search( "tcp:" + ONOS4_ip, response )\
                    and re.search( "tcp:" + ONOS5_ip, response )\
                    and re.search( "tcp:" + ONOS6_ip, response )\
                    and re.search( "tcp:" + ONOS7_ip, response ):
                mastership_check = mastership_check and main.TRUE
            else:
                mastership_check = main.FALSE
        if mastership_check == main.TRUE:
            main.log.report( "Switch mastership assigned correctly" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=mastership_check,
            onpass="Switch mastership assigned correctly",
            onfail="Switches not assigned correctly to controllers" )

        # Manually assign mastership to the controller we want
        role_call = main.TRUE
        role_check = main.TRUE

        # Assign switch
        device_id = main.ONOScli1.get_device( "1000" ).get( 'id' )
        role_call = role_call and main.ONOScli1.device_role(
            device_id,
            ONOS1_ip )
        # Check assignment
        if ONOS1_ip in main.ONOScli1.get_role( device_id ).get( 'master' ):
            role_check = role_check and main.TRUE
        else:
            role_check = role_check and main.FALSE

        # Assign switch
        device_id = main.ONOScli1.get_device( "2800" ).get( 'id' )
        role_call = role_call and main.ONOScli1.device_role(
            device_id,
            ONOS1_ip )
        # Check assignment
        if ONOS1_ip in main.ONOScli1.get_role( device_id ).get( 'master' ):
            role_check = role_check and main.TRUE
        else:
            role_check = role_check and main.FALSE

        # Assign switch
        device_id = main.ONOScli1.get_device( "2000" ).get( 'id' )
        role_call = role_call and main.ONOScli1.device_role(
            device_id,
            ONOS2_ip )
        # Check assignment
        if ONOS2_ip in main.ONOScli1.get_role( device_id ).get( 'master' ):
            role_check = role_check and main.TRUE
        else:
            role_check = role_check and main.FALSE

        # Assign switch
        device_id = main.ONOScli1.get_device( "3000" ).get( 'id' )
        role_call = role_call and main.ONOScli1.device_role(
            device_id,
            ONOS2_ip )
        # Check assignment
        if ONOS2_ip in main.ONOScli1.get_role( device_id ).get( 'master' ):
            role_check = role_check and main.TRUE
        else:
            role_check = role_check and main.FALSE

        # Assign switch
        device_id = main.ONOScli1.get_device( "5000" ).get( 'id' )
        role_call = role_call and main.ONOScli1.device_role(
            device_id,
            ONOS3_ip )
        # Check assignment
        if ONOS3_ip in main.ONOScli1.get_role( device_id ).get( 'master' ):
            role_check = role_check and main.TRUE
        else:
            role_check = role_check and main.FALSE

        # Assign switch
        device_id = main.ONOScli1.get_device( "6000" ).get( 'id' )
        role_call = role_call and main.ONOScli1.device_role(
            device_id,
            ONOS3_ip )
        # Check assignment
        if ONOS3_ip in main.ONOScli1.get_role( device_id ).get( 'master' ):
            role_check = role_check and main.TRUE
        else:
            role_check = role_check and main.FALSE

        # Assign switch
        device_id = main.ONOScli1.get_device( "3004" ).get( 'id' )
        role_call = role_call and main.ONOScli1.device_role(
            device_id,
            ONOS4_ip )
        # Check assignment
        if ONOS4_ip in main.ONOScli1.get_role( device_id ).get( 'master' ):
            role_check = role_check and main.TRUE
        else:
            role_check = role_check and main.FALSE

        for i in range( 8, 18 ):
            dpid = '3' + str( i ).zfill( 3 )
            device_id = main.ONOScli1.get_device( dpid ).get( 'id' )
            role_call = role_call and main.ONOScli1.device_role(
                device_id,
                ONOS5_ip )
            # Check assignment
            if ONOS5_ip in main.ONOScli1.get_role( device_id ).get( 'master' ):
                role_check = role_check and main.TRUE
            else:
                role_check = role_check and main.FALSE

        device_id = main.ONOScli1.get_device( "6007" ).get( 'id' )
        role_call = role_call and main.ONOScli1.device_role(
            device_id,
            ONOS6_ip )
        # Check assignment
        if ONOS6_ip in main.ONOScli1.get_role( device_id ).get( 'master' ):
            role_check = role_check and main.TRUE
        else:
            role_check = role_check and main.FALSE

        for i in range( 18, 28 ):
            dpid = '6' + str( i ).zfill( 3 )
            device_id = main.ONOScli1.get_device( dpid ).get( 'id' )
            role_call = role_call and main.ONOScli1.device_role(
                device_id,
                ONOS7_ip )
            # Check assignment
            if ONOS7_ip in main.ONOScli1.get_role( device_id ).get( 'master' ):
                role_check = role_check and main.TRUE
            else:
                role_check = role_check and main.FALSE

        utilities.assert_equals(
            expect=main.TRUE,
            actual=role_call,
            onpass="Re-assigned switch mastership to designated controller",
            onfail="Something wrong with device_role calls" )

        utilities.assert_equals(
            expect=main.TRUE,
            actual=role_check,
            onpass="Switches were successfully reassigned to designated " +
                   "controller",
            onfail="Switches were not successfully reassigned" )
        mastership_check = mastership_check and role_call and role_check
        utilities.assert_equals( expect=main.TRUE, actual=mastership_check,
                                 onpass="Switch mastership correctly assigned",
                                 onfail="Error in (re)assigning switch" +
                                        " mastership" )

    def CASE3( self, main ):
        """
        Assign intents
        """
        import time
        main.log.report( "Adding host intents" )
        main.case( "Adding host Intents" )

        main.step( "Discovering  Hosts( Via pingall for now)" )
        # FIXME: Once we have a host discovery mechanism, use that instead

        # install onos-app-fwd
        main.log.info( "Install reactive forwarding app" )
        main.ONOScli1.feature_install( "onos-app-fwd" )
        main.ONOScli2.feature_install( "onos-app-fwd" )
        main.ONOScli3.feature_install( "onos-app-fwd" )
        main.ONOScli4.feature_install( "onos-app-fwd" )
        main.ONOScli5.feature_install( "onos-app-fwd" )
        main.ONOScli6.feature_install( "onos-app-fwd" )
        main.ONOScli7.feature_install( "onos-app-fwd" )

        # REACTIVE FWD test
        ping_result = main.FALSE
        time1 = time.time()
        ping_result = main.Mininet1.pingall()
        time2 = time.time()
        main.log.info( "Time for pingall: %2f seconds" % ( time2 - time1 ) )

        # uninstall onos-app-fwd
        main.log.info( "Uninstall reactive forwarding app" )
        main.ONOScli1.feature_uninstall( "onos-app-fwd" )
        main.ONOScli2.feature_uninstall( "onos-app-fwd" )
        main.ONOScli3.feature_uninstall( "onos-app-fwd" )
        main.ONOScli4.feature_uninstall( "onos-app-fwd" )
        main.ONOScli5.feature_uninstall( "onos-app-fwd" )
        main.ONOScli6.feature_uninstall( "onos-app-fwd" )
        main.ONOScli7.feature_uninstall( "onos-app-fwd" )
        # timeout for fwd flows
        time.sleep( 10 )

        main.step( "Add  host intents" )
        # TODO:  move the host numbers to params
        intent_add_result = True
        for i in range( 8, 18 ):
            main.log.info( "Adding host intent between h" + str( i ) +
                           " and h" + str( i + 10 ) )
            host1 = "00:00:00:00:00:" + \
                str( hex( i )[ 2: ] ).zfill( 2 ).upper()
            host2 = "00:00:00:00:00:" + \
                str( hex( i + 10 )[ 2: ] ).zfill( 2 ).upper()
            host1_id = main.ONOScli1.get_host( host1 )[ 'id' ]
            host2_id = main.ONOScli1.get_host( host2 )[ 'id' ]
            # NOTE: get host can return None
            if host1_id and host2_id:
                tmp_result = main.ONOScli1.add_host_intent(
                    host1_id,
                    host2_id )
            else:
                main.log.error( "Error, get_host() failed" )
                tmp_result = main.FALSE
            intent_add_result = bool( ping_result and intent_add_result
                                      and tmp_result )
        utilities.assert_equals(
            expect=True,
            actual=intent_add_result,
            onpass="Switch mastership correctly assigned",
            onfail="Error in (re)assigning switch mastership" )
        # TODO Check if intents all exist in datastore

    def CASE4( self, main ):
        """
        Ping across added host intents
        """
        description = " Ping across added host intents"
        main.log.report( description )
        main.case( description )
        Ping_Result = main.TRUE
        for i in range( 8, 18 ):
            ping = main.Mininet1.pingHost(
                src="h" + str( i ), target="h" + str( i + 10 ) )
            Ping_Result = Ping_Result and ping
            if ping == main.FALSE:
                main.log.warn( "Ping failed between h" + str( i ) +
                               " and h" + str( i + 10 ) )
            elif ping == main.TRUE:
                main.log.info( "Ping test passed!" )
                Ping_Result = main.TRUE
        if Ping_Result == main.FALSE:
            main.log.report(
                "Intents have not been installed correctly, pings failed." )
        if Ping_Result == main.TRUE:
            main.log.report(
                "Intents have been installed correctly and verified by pings" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=Ping_Result,
            onpass="Intents have been installed correctly and pings work",
            onfail="Intents have not been installed correctly, pings failed." )

    def CASE5( self, main ):
        """
        Reading state of ONOS
        """
        import json
        # assumes that sts is already in you PYTHONPATH
        from sts.topology.teston_topology import TestONTopology

        main.log.report( "Setting up and gathering data for current state" )
        main.case( "Setting up and gathering data for current state" )
        # The general idea for this test case is to pull the state of
        # ( intents,flows, topology,... ) from each ONOS node
        # We can then compare them with eachother and also with past states

        main.step( "Get the Mastership of each switch from each controller" )
        global mastership_state
        mastership_state = []

        # Assert that each device has a master
        ONOS1_master_not_null = main.ONOScli1.roles_not_null()
        ONOS2_master_not_null = main.ONOScli2.roles_not_null()
        ONOS3_master_not_null = main.ONOScli3.roles_not_null()
        ONOS4_master_not_null = main.ONOScli4.roles_not_null()
        ONOS5_master_not_null = main.ONOScli5.roles_not_null()
        ONOS6_master_not_null = main.ONOScli6.roles_not_null()
        ONOS7_master_not_null = main.ONOScli7.roles_not_null()
        roles_not_null = ONOS1_master_not_null and ONOS2_master_not_null and\
            ONOS3_master_not_null and ONOS4_master_not_null and\
            ONOS5_master_not_null and ONOS6_master_not_null and\
            ONOS7_master_not_null
        utilities.assert_equals(
            expect=main.TRUE,
            actual=roles_not_null,
            onpass="Each device has a master",
            onfail="Some devices don't have a master assigned" )

        ONOS1_mastership = main.ONOScli1.roles()
        ONOS2_mastership = main.ONOScli2.roles()
        ONOS3_mastership = main.ONOScli3.roles()
        ONOS4_mastership = main.ONOScli4.roles()
        ONOS5_mastership = main.ONOScli5.roles()
        ONOS6_mastership = main.ONOScli6.roles()
        ONOS7_mastership = main.ONOScli7.roles()
        # print json.dumps( json.loads( ONOS1_mastership ), sort_keys=True,
        # indent=4, separators=( ',', ': ' ) )
        if "Error" in ONOS1_mastership or not ONOS1_mastership\
                or "Error" in ONOS2_mastership or not ONOS2_mastership\
                or "Error" in ONOS3_mastership or not ONOS3_mastership\
                or "Error" in ONOS4_mastership or not ONOS4_mastership\
                or "Error" in ONOS5_mastership or not ONOS5_mastership\
                or "Error" in ONOS6_mastership or not ONOS6_mastership\
                or "Error" in ONOS7_mastership or not ONOS7_mastership:
            main.log.report( "Error in getting ONOS roles" )
            main.log.warn(
                "ONOS1 mastership response: " +
                repr( ONOS1_mastership ) )
            main.log.warn(
                "ONOS2 mastership response: " +
                repr( ONOS2_mastership ) )
            main.log.warn(
                "ONOS3 mastership response: " +
                repr( ONOS3_mastership ) )
            main.log.warn(
                "ONOS4 mastership response: " +
                repr( ONOS4_mastership ) )
            main.log.warn(
                "ONOS5 mastership response: " +
                repr( ONOS5_mastership ) )
            main.log.warn(
                "ONOS6 mastership response: " +
                repr( ONOS6_mastership ) )
            main.log.warn(
                "ONOS7 mastership response: " +
                repr( ONOS7_mastership ) )
            consistent_mastership = main.FALSE
        elif ONOS1_mastership == ONOS2_mastership\
                and ONOS1_mastership == ONOS3_mastership\
                and ONOS1_mastership == ONOS4_mastership\
                and ONOS1_mastership == ONOS5_mastership\
                and ONOS1_mastership == ONOS6_mastership\
                and ONOS1_mastership == ONOS7_mastership:
            mastership_state = ONOS1_mastership
            consistent_mastership = main.TRUE
            main.log.report(
                "Switch roles are consistent across all ONOS nodes" )
        else:
            main.log.warn(
                "ONOS1 roles: ",
                json.dumps(
                    json.loads( ONOS1_mastership ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
            main.log.warn(
                "ONOS2 roles: ",
                json.dumps(
                    json.loads( ONOS2_mastership ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
            main.log.warn(
                "ONOS3 roles: ",
                json.dumps(
                    json.loads( ONOS3_mastership ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
            main.log.warn(
                "ONOS4 roles: ",
                json.dumps(
                    json.loads( ONOS4_mastership ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
            main.log.warn(
                "ONOS5 roles: ",
                json.dumps(
                    json.loads( ONOS5_mastership ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
            main.log.warn(
                "ONOS6 roles: ",
                json.dumps(
                    json.loads( ONOS6_mastership ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
            main.log.warn(
                "ONOS7 roles: ",
                json.dumps(
                    json.loads( ONOS7_mastership ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
            consistent_mastership = main.FALSE
        utilities.assert_equals(
            expect=main.TRUE,
            actual=consistent_mastership,
            onpass="Switch roles are consistent across all ONOS nodes",
            onfail="ONOS nodes have different views of switch roles" )

        main.step( "Get the intents from each controller" )
        global intent_state
        intent_state = []
        ONOS1_intents = main.ONOScli1.intents( json_format=True )
        ONOS2_intents = main.ONOScli2.intents( json_format=True )
        ONOS3_intents = main.ONOScli3.intents( json_format=True )
        ONOS4_intents = main.ONOScli4.intents( json_format=True )
        ONOS5_intents = main.ONOScli5.intents( json_format=True )
        ONOS6_intents = main.ONOScli6.intents( json_format=True )
        ONOS7_intents = main.ONOScli7.intents( json_format=True )
        intent_check = main.FALSE
        if "Error" in ONOS1_intents or not ONOS1_intents\
                or "Error" in ONOS2_intents or not ONOS2_intents\
                or "Error" in ONOS3_intents or not ONOS3_intents\
                or "Error" in ONOS4_intents or not ONOS4_intents\
                or "Error" in ONOS5_intents or not ONOS5_intents\
                or "Error" in ONOS6_intents or not ONOS6_intents\
                or "Error" in ONOS7_intents or not ONOS7_intents:
            main.log.report( "Error in getting ONOS intents" )
            main.log.warn( "ONOS1 intents response: " + repr( ONOS1_intents ) )
            main.log.warn( "ONOS2 intents response: " + repr( ONOS2_intents ) )
            main.log.warn( "ONOS3 intents response: " + repr( ONOS3_intents ) )
            main.log.warn( "ONOS4 intents response: " + repr( ONOS4_intents ) )
            main.log.warn( "ONOS5 intents response: " + repr( ONOS5_intents ) )
            main.log.warn( "ONOS6 intents response: " + repr( ONOS6_intents ) )
            main.log.warn( "ONOS7 intents response: " + repr( ONOS7_intents ) )
        elif ONOS1_intents == ONOS2_intents\
                and ONOS1_intents == ONOS3_intents\
                and ONOS1_intents == ONOS4_intents\
                and ONOS1_intents == ONOS5_intents\
                and ONOS1_intents == ONOS6_intents\
                and ONOS1_intents == ONOS7_intents:
            intent_state = ONOS1_intents
            intent_check = main.TRUE
            main.log.report( "Intents are consistent across all ONOS nodes" )
        else:
            main.log.warn(
                "ONOS1 intents: ",
                json.dumps(
                    json.loads( ONOS1_intents ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
            main.log.warn(
                "ONOS2 intents: ",
                json.dumps(
                    json.loads( ONOS2_intents ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
            main.log.warn(
                "ONOS3 intents: ",
                json.dumps(
                    json.loads( ONOS3_intents ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
            main.log.warn(
                "ONOS4 intents: ",
                json.dumps(
                    json.loads( ONOS4_intents ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
            main.log.warn(
                "ONOS5 intents: ",
                json.dumps(
                    json.loads( ONOS5_intents ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
            main.log.warn(
                "ONOS6 intents: ",
                json.dumps(
                    json.loads( ONOS6_intents ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
            main.log.warn(
                "ONOS7 intents: ",
                json.dumps(
                    json.loads( ONOS7_intents ),
                    sort_keys=True,
                    indent=4,
                    separators=(
                        ',',
                        ': ' ) ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=intent_check,
            onpass="Intents are consistent across all ONOS nodes",
            onfail="ONOS nodes have different views of intents" )

        main.step( "Get the flows from each controller" )
        global flow_state
        flow_state = []
        ONOS1_flows = main.ONOScli1.flows( json_format=True )
        ONOS2_flows = main.ONOScli2.flows( json_format=True )
        ONOS3_flows = main.ONOScli3.flows( json_format=True )
        ONOS4_flows = main.ONOScli4.flows( json_format=True )
        ONOS5_flows = main.ONOScli5.flows( json_format=True )
        ONOS6_flows = main.ONOScli6.flows( json_format=True )
        ONOS7_flows = main.ONOScli7.flows( json_format=True )
        ONOS1_flows_json = json.loads( ONOS1_flows )
        ONOS2_flows_json = json.loads( ONOS2_flows )
        ONOS3_flows_json = json.loads( ONOS3_flows )
        ONOS4_flows_json = json.loads( ONOS4_flows )
        ONOS5_flows_json = json.loads( ONOS5_flows )
        ONOS6_flows_json = json.loads( ONOS6_flows )
        ONOS7_flows_json = json.loads( ONOS7_flows )
        flow_check = main.FALSE
        if "Error" in ONOS1_flows or not ONOS1_flows\
                or "Error" in ONOS2_flows or not ONOS2_flows\
                or "Error" in ONOS3_flows or not ONOS3_flows\
                or "Error" in ONOS4_flows or not ONOS4_flows\
                or "Error" in ONOS5_flows or not ONOS5_flows\
                or "Error" in ONOS6_flows or not ONOS6_flows\
                or "Error" in ONOS7_flows or not ONOS7_flows:
            main.log.report( "Error in getting ONOS intents" )
            main.log.warn( "ONOS1 flows repsponse: " + ONOS1_flows )
            main.log.warn( "ONOS2 flows repsponse: " + ONOS2_flows )
            main.log.warn( "ONOS3 flows repsponse: " + ONOS3_flows )
            main.log.warn( "ONOS4 flows repsponse: " + ONOS4_flows )
            main.log.warn( "ONOS5 flows repsponse: " + ONOS5_flows )
            main.log.warn( "ONOS6 flows repsponse: " + ONOS6_flows )
            main.log.warn( "ONOS7 flows repsponse: " + ONOS7_flows )
        elif len( ONOS1_flows_json ) == len( ONOS2_flows_json )\
                and len( ONOS1_flows_json ) == len( ONOS3_flows_json )\
                and len( ONOS1_flows_json ) == len( ONOS4_flows_json )\
                and len( ONOS1_flows_json ) == len( ONOS5_flows_json )\
                and len( ONOS1_flows_json ) == len( ONOS6_flows_json )\
                and len( ONOS1_flows_json ) == len( ONOS7_flows_json ):
                # TODO: Do a better check, maybe compare flows on switches?
            flow_state = ONOS1_flows
            flow_check = main.TRUE
            main.log.report( "Flow count is consistent across all ONOS nodes" )
        else:
            main.log.warn( "ONOS1 flows: " +
                           json.dumps( ONOS1_flows_json, sort_keys=True,
                                       indent=4, separators=( ',', ': ' ) ) )
            main.log.warn( "ONOS2 flows: " +
                           json.dumps( ONOS2_flows_json, sort_keys=True,
                                       indent=4, separators=( ',', ': ' ) ) )
            main.log.warn( "ONOS3 flows: " +
                           json.dumps( ONOS3_flows_json, sort_keys=True,
                                       indent=4, separators=( ',', ': ' ) ) )
            main.log.warn( "ONOS4 flows: " +
                           json.dumps( ONOS4_flows_json, sort_keys=True,
                                       indent=4, separators=( ',', ': ' ) ) )
            main.log.warn( "ONOS5 flows: " +
                           json.dumps( ONOS5_flows_json, sort_keys=True,
                                       indent=4, separators=( ',', ': ' ) ) )
            main.log.warn( "ONOS6 flows: " +
                           json.dumps( ONOS6_flows_json, sort_keys=True,
                                       indent=4, separators=( ',', ': ' ) ) )
            main.log.warn( "ONOS7 flows: " +
                           json.dumps( ONOS7_flows_json, sort_keys=True,
                                       indent=4, separators=( ',', ': ' ) ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=flow_check,
            onpass="The flow count is consistent across all ONOS nodes",
            onfail="ONOS nodes have different flow counts" )

        main.step( "Get the OF Table entries" )
        global flows
        flows = []
        for i in range( 1, 29 ):
            flows.append( main.Mininet2.get_flowTable( 1.3, "s" + str( i ) ) )

        # TODO: Compare switch flow tables with ONOS flow tables

        main.step( "Start continuous pings" )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source1' ],
            target=main.params[ 'PING' ][ 'target1' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source2' ],
            target=main.params[ 'PING' ][ 'target2' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source3' ],
            target=main.params[ 'PING' ][ 'target3' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source4' ],
            target=main.params[ 'PING' ][ 'target4' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source5' ],
            target=main.params[ 'PING' ][ 'target5' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source6' ],
            target=main.params[ 'PING' ][ 'target6' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source7' ],
            target=main.params[ 'PING' ][ 'target7' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source8' ],
            target=main.params[ 'PING' ][ 'target8' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source9' ],
            target=main.params[ 'PING' ][ 'target9' ],
            pingTime=500 )
        main.Mininet2.pingLong(
            src=main.params[ 'PING' ][ 'source10' ],
            target=main.params[ 'PING' ][ 'target10' ],
            pingTime=500 )

        main.step( "Create TestONTopology object" )
        ctrls = []
        count = 1
        while True:
            temp = ()
            if ( 'ip' + str( count ) ) in main.params[ 'CTRL' ]:
                temp = temp + ( getattr( main, ( 'ONOS' + str( count ) ) ), )
                temp = temp + ( "ONOS" + str( count ), )
                temp = temp + ( main.params[ 'CTRL' ][ 'ip' + str( count ) ], )
                temp = temp + \
                    ( eval( main.params[ 'CTRL' ][ 'port' + str( count ) ] ), )
                ctrls.append( temp )
                count = count + 1
            else:
                break
        MNTopo = TestONTopology(
            main.Mininet1,
            ctrls )  # can also add Intent API info for intent operations

        main.step( "Collecting topology information from ONOS" )
        devices = []
        devices.append( main.ONOScli1.devices() )
        devices.append( main.ONOScli2.devices() )
        devices.append( main.ONOScli3.devices() )
        devices.append( main.ONOScli4.devices() )
        devices.append( main.ONOScli5.devices() )
        devices.append( main.ONOScli6.devices() )
        devices.append( main.ONOScli7.devices() )
        hosts = []
        hosts.append( main.ONOScli1.hosts() )
        hosts.append( main.ONOScli2.hosts() )
        hosts.append( main.ONOScli3.hosts() )
        hosts.append( main.ONOScli4.hosts() )
        hosts.append( main.ONOScli5.hosts() )
        hosts.append( main.ONOScli6.hosts() )
        hosts.append( main.ONOScli7.hosts() )
        ports = []
        ports.append( main.ONOScli1.ports() )
        ports.append( main.ONOScli2.ports() )
        ports.append( main.ONOScli3.ports() )
        ports.append( main.ONOScli4.ports() )
        ports.append( main.ONOScli5.ports() )
        ports.append( main.ONOScli6.ports() )
        ports.append( main.ONOScli7.ports() )
        links = []
        links.append( main.ONOScli1.links() )
        links.append( main.ONOScli2.links() )
        links.append( main.ONOScli3.links() )
        links.append( main.ONOScli4.links() )
        links.append( main.ONOScli5.links() )
        links.append( main.ONOScli6.links() )
        links.append( main.ONOScli7.links() )
        clusters = []
        clusters.append( main.ONOScli1.clusters() )
        clusters.append( main.ONOScli2.clusters() )
        clusters.append( main.ONOScli3.clusters() )
        clusters.append( main.ONOScli4.clusters() )
        clusters.append( main.ONOScli5.clusters() )
        clusters.append( main.ONOScli6.clusters() )
        clusters.append( main.ONOScli7.clusters() )
        paths = []
        temp_topo = main.ONOSbench.get_topology( main.ONOScli1.topology() )
        paths.append( temp_topo.get( 'paths', False ) )
        temp_topo = main.ONOSbench.get_topology( main.ONOScli2.topology() )
        paths.append( temp_topo.get( 'paths', False ) )
        temp_topo = main.ONOSbench.get_topology( main.ONOScli3.topology() )
        paths.append( temp_topo.get( 'paths', False ) )
        temp_topo = main.ONOSbench.get_topology( main.ONOScli4.topology() )
        paths.append( temp_topo.get( 'paths', False ) )
        temp_topo = main.ONOSbench.get_topology( main.ONOScli5.topology() )
        paths.append( temp_topo.get( 'paths', False ) )
        temp_topo = main.ONOSbench.get_topology( main.ONOScli6.topology() )
        paths.append( temp_topo.get( 'paths', False ) )
        temp_topo = main.ONOSbench.get_topology( main.ONOScli7.topology() )
        paths.append( temp_topo.get( 'paths', False ) )

        # Compare json objects for hosts, dataplane clusters and paths

        # hosts
        consistent_hosts_result = main.TRUE
        for controller in range( len( hosts ) ):
            controller_str = str( controller + 1 )
            if "Error" not in hosts[ controller ]:
                if hosts[ controller ] == hosts[ 0 ]:
                    continue
                else:  # hosts not consistent
                    main.log.report( "hosts from ONOS" +
                                     controller_str +
                                     " is inconsistent with ONOS1" )
                    main.log.warn( repr( hosts[ controller ] ) )
                    consistent_hosts_result = main.FALSE

            else:
                main.log.report( "Error in getting ONOS hosts from ONOS" +
                                 controller_str )
                consistent_hosts_result = main.FALSE
                main.log.warn( "ONOS" + controller_str +
                               " hosts response: " +
                               repr( hosts[ controller ] ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=consistent_hosts_result,
            onpass="Hosts view is consistent across all ONOS nodes",
            onfail="ONOS nodes have different views of hosts" )

        # Strongly connected clusters of devices
        consistent_clusters_result = main.TRUE
        for controller in range( len( clusters ) ):
            if "Error" not in clusters[ controller ]:
                if clusters[ controller ] == clusters[ 0 ]:
                    continue
                else:  # clusters not consistent
                    main.log.report( "clusters from ONOS" +
                                     controller_str +
                                     " is inconsistent with ONOS1" )
                    consistent_clusters_result = main.FALSE

            else:
                main.log.report( "Error in getting dataplane clusters " +
                                 "from ONOS" + controller_str )
                consistent_clusters_result = main.FALSE
                main.log.warn( "ONOS" + controller_str +
                               " clusters response: " +
                               repr( clusters[ controller ] ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=consistent_clusters_result,
            onpass="Clusters view is consistent across all ONOS nodes",
            onfail="ONOS nodes have different views of clusters" )
        # there should always only be one cluster
        num_clusters = len( json.loads( clusters[ 0 ] ) )
        utilities.assert_equals(
            expect=1,
            actual=num_clusters,
            onpass="ONOS shows 1 SCC",
            onfail="ONOS shows " +
            str( num_clusters ) +
            " SCCs" )

        # paths
        consistent_paths_result = main.TRUE
        for controller in range( len( paths ) ):
            controller_str = str( controller + 1 )
            if "Error" not in paths[ controller ]:
                if paths[ controller ] == paths[ 0 ]:
                    continue
                else:  # paths not consistent
                    main.log.report( "paths from ONOS" + controller_str +
                                     " is inconsistent with ONOS1" )
                    consistent_paths_result = main.FALSE

            else:
                main.log.report( "Error in getting paths from ONOS" +
                                 controller_str )
                consistent_paths_result = main.FALSE
                main.log.warn( "ONOS" + controller_str + " paths response: " +
                               repr( paths[ controller ] ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=consistent_paths_result,
            onpass="Paths count is consistent across all ONOS nodes",
            onfail="ONOS nodes have different counts of paths" )

        main.step( "Comparing ONOS topology to MN" )
        devices_results = main.TRUE
        ports_results = main.TRUE
        links_results = main.TRUE
        for controller in range( num_controllers ):
            controller_str = str( controller + 1 )
            if devices[ controller ] or "Error" not in devices[ controller ]:
                current_devices_result = main.Mininet1.compare_switches(
                    MNTopo,
                    json.loads(
                        devices[ controller ] ) )
            else:
                current_devices_result = main.FALSE
            utilities.assert_equals( expect=main.TRUE,
                                     actual=current_devices_result,
                                     onpass="ONOS" + controller_str +
                                     " Switches view is correct",
                                     onfail="ONOS" + controller_str +
                                     " Switches view is incorrect" )

            if ports[ controller ] or "Error" not in ports[ controller ]:
                current_ports_result = main.Mininet1.compare_ports(
                    MNTopo,
                    json.loads(
                        ports[ controller ] ) )
            else:
                current_ports_result = main.FALSE
            utilities.assert_equals( expect=main.TRUE,
                                     actual=current_ports_result,
                                     onpass="ONOS" + controller_str +
                                     " ports view is correct",
                                     onfail="ONOS" + controller_str +
                                     " ports view is incorrect" )

            if links[ controller ] or "Error" not in links[ controller ]:
                current_links_result = main.Mininet1.compare_links(
                    MNTopo,
                    json.loads(
                        links[ controller ] ) )
            else:
                current_links_result = main.FALSE
            utilities.assert_equals( expect=main.TRUE,
                                     actual=current_links_result,
                                     onpass="ONOS" + controller_str +
                                     " links view is correct",
                                     onfail="ONOS" + controller_str +
                                     " links view is incorrect" )

            devices_results = devices_results and current_devices_result
            ports_results = ports_results and current_ports_result
            links_results = links_results and current_links_result

        topo_result = devices_results and ports_results and links_results\
            and consistent_hosts_result and consistent_clusters_result\
            and consistent_paths_result
        utilities.assert_equals( expect=main.TRUE, actual=topo_result,
                                 onpass="Topology Check Test successful",
                                 onfail="Topology Check Test NOT successful" )

        final_assert = main.TRUE
        final_assert = final_assert and topo_result and flow_check \
            and intent_check and consistent_mastership and roles_not_null
        utilities.assert_equals( expect=main.TRUE, actual=final_assert,
                                 onpass="State check successful",
                                 onfail="State check NOT successful" )

    def CASE6( self, main ):
        """
        The Failure case. Since this is the Sanity test, we do nothing.
        """
        import time
        main.log.report( "Wait 60 seconds instead of inducing a failure" )
        time.sleep( 60 )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=main.TRUE,
            onpass="Sleeping 60 seconds",
            onfail="Something is terribly wrong with my math" )

    def CASE7( self, main ):
        """
        Check state after ONOS failure
        """
        import json
        main.case( "Running ONOS Constant State Tests" )

        # Assert that each device has a master
        ONOS1_master_not_null = main.ONOScli1.roles_not_null()
        ONOS2_master_not_null = main.ONOScli2.roles_not_null()
        ONOS3_master_not_null = main.ONOScli3.roles_not_null()
        ONOS4_master_not_null = main.ONOScli4.roles_not_null()
        ONOS5_master_not_null = main.ONOScli5.roles_not_null()
        ONOS6_master_not_null = main.ONOScli6.roles_not_null()
        ONOS7_master_not_null = main.ONOScli7.roles_not_null()
        roles_not_null = ONOS1_master_not_null and ONOS2_master_not_null and\
            ONOS3_master_not_null and ONOS4_master_not_null and\
            ONOS5_master_not_null and ONOS6_master_not_null and\
            ONOS7_master_not_null
        utilities.assert_equals(
            expect=main.TRUE,
            actual=roles_not_null,
            onpass="Each device has a master",
            onfail="Some devices don't have a master assigned" )

        main.step( "Check if switch roles are consistent across all nodes" )
        ONOS1_mastership = main.ONOScli1.roles()
        ONOS2_mastership = main.ONOScli2.roles()
        ONOS3_mastership = main.ONOScli3.roles()
        ONOS4_mastership = main.ONOScli4.roles()
        ONOS5_mastership = main.ONOScli5.roles()
        ONOS6_mastership = main.ONOScli6.roles()
        ONOS7_mastership = main.ONOScli7.roles()
        # print json.dumps( json.loads( ONOS1_mastership ), sort_keys=True,
        # indent=4, separators=( ',', ': ' ) )
        if "Error" in ONOS1_mastership or not ONOS1_mastership\
                or "Error" in ONOS2_mastership or not ONOS2_mastership\
                or "Error" in ONOS3_mastership or not ONOS3_mastership\
                or "Error" in ONOS4_mastership or not ONOS4_mastership\
                or "Error" in ONOS5_mastership or not ONOS5_mastership\
                or "Error" in ONOS6_mastership or not ONOS6_mastership\
                or "Error" in ONOS7_mastership or not ONOS7_mastership:
            main.log.error( "Error in getting ONOS mastership" )
            main.log.warn( "ONOS1 mastership response: " +
                           repr( ONOS1_mastership ) )
            main.log.warn( "ONOS2 mastership response: " +
                           repr( ONOS2_mastership ) )
            main.log.warn( "ONOS3 mastership response: " +
                           repr( ONOS3_mastership ) )
            main.log.warn( "ONOS4 mastership response: " +
                           repr( ONOS4_mastership ) )
            main.log.warn( "ONOS5 mastership response: " +
                           repr( ONOS5_mastership ) )
            main.log.warn( "ONOS6 mastership response: " +
                           repr( ONOS6_mastership ) )
            main.log.warn( "ONOS7 mastership response: " +
                           repr( ONOS7_mastership ) )
            consistent_mastership = main.FALSE
        elif ONOS1_mastership == ONOS2_mastership\
                and ONOS1_mastership == ONOS3_mastership\
                and ONOS1_mastership == ONOS4_mastership\
                and ONOS1_mastership == ONOS5_mastership\
                and ONOS1_mastership == ONOS6_mastership\
                and ONOS1_mastership == ONOS7_mastership:
            consistent_mastership = main.TRUE
            main.log.report(
                "Switch roles are consistent across all ONOS nodes" )
        else:
            main.log.warn( "ONOS1 roles: ", json.dumps(
                json.loads( ONOS1_mastership ), sort_keys=True, indent=4,
                separators=( ',', ': ' ) ) )
            main.log.warn( "ONOS2 roles: ", json.dumps(
                json.loads( ONOS2_mastership ), sort_keys=True, indent=4,
                separators=( ',', ': ' ) ) )
            main.log.warn( "ONOS3 roles: ", json.dumps(
                json.loads( ONOS3_mastership ), sort_keys=True, indent=4,
                separators=( ',', ': ' ) ) )
            main.log.warn( "ONOS4 roles: ", json.dumps(
                json.loads( ONOS4_mastership ), sort_keys=True, indent=4,
                separators=( ',', ': ' ) ) )
            main.log.warn( "ONOS5 roles: ", json.dumps(
                json.loads( ONOS5_mastership ), sort_keys=True, indent=4,
                separators=( ',', ': ' ) ) )
            main.log.warn( "ONOS6 roles: ", json.dumps(
                json.loads( ONOS6_mastership ), sort_keys=True, indent=4,
                separators=( ',', ': ' ) ) )
            main.log.warn( "ONOS7 roles: ", json.dumps(
                json.loads( ONOS7_mastership ), sort_keys=True, indent=4,
                separators=( ',', ': ' ) ) )
            consistent_mastership = main.FALSE
        utilities.assert_equals(
            expect=main.TRUE,
            actual=consistent_mastership,
            onpass="Switch roles are consistent across all ONOS nodes",
            onfail="ONOS nodes have different views of switch roles" )

        description2 = "Compare switch roles from before failure"
        main.step( description2 )

        current_json = json.loads( ONOS1_mastership )
        old_json = json.loads( mastership_state )
        mastership_check = main.TRUE
        for i in range( 1, 29 ):
            switchDPID = str(
                main.Mininet1.getSwitchDPID(
                    switch="s" +
                    str( i ) ) )

            current = [ switch[ 'master' ] for switch in current_json
                        if switchDPID in switch[ 'id' ] ]
            old = [ switch[ 'master' ] for switch in old_json
                    if switchDPID in switch[ 'id' ] ]
            if current == old:
                mastership_check = mastership_check and main.TRUE
            else:
                main.log.warn( "Mastership of switch %s changed" % switchDPID )
                mastership_check = main.FALSE
        if mastership_check == main.TRUE:
            main.log.report( "Mastership of Switches was not changed" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=mastership_check,
            onpass="Mastership of Switches was not changed",
            onfail="Mastership of some switches changed" )
        mastership_check = mastership_check and consistent_mastership

        main.step( "Get the intents and compare across all nodes" )
        ONOS1_intents = main.ONOScli1.intents( json_format=True )
        ONOS2_intents = main.ONOScli2.intents( json_format=True )
        ONOS3_intents = main.ONOScli3.intents( json_format=True )
        ONOS4_intents = main.ONOScli4.intents( json_format=True )
        ONOS5_intents = main.ONOScli5.intents( json_format=True )
        ONOS6_intents = main.ONOScli6.intents( json_format=True )
        ONOS7_intents = main.ONOScli7.intents( json_format=True )
        intent_check = main.FALSE
        if "Error" in ONOS1_intents or not ONOS1_intents\
                or "Error" in ONOS2_intents or not ONOS2_intents\
                or "Error" in ONOS3_intents or not ONOS3_intents\
                or "Error" in ONOS4_intents or not ONOS4_intents\
                or "Error" in ONOS5_intents or not ONOS5_intents\
                or "Error" in ONOS6_intents or not ONOS6_intents\
                or "Error" in ONOS7_intents or not ONOS7_intents:
            main.log.report( "Error in getting ONOS intents" )
            main.log.warn( "ONOS1 intents response: " + repr( ONOS1_intents ) )
            main.log.warn( "ONOS2 intents response: " + repr( ONOS2_intents ) )
            main.log.warn( "ONOS3 intents response: " + repr( ONOS3_intents ) )
            main.log.warn( "ONOS4 intents response: " + repr( ONOS4_intents ) )
            main.log.warn( "ONOS5 intents response: " + repr( ONOS5_intents ) )
            main.log.warn( "ONOS6 intents response: " + repr( ONOS6_intents ) )
            main.log.warn( "ONOS7 intents response: " + repr( ONOS7_intents ) )
        elif ONOS1_intents == ONOS2_intents\
                and ONOS1_intents == ONOS3_intents\
                and ONOS1_intents == ONOS4_intents\
                and ONOS1_intents == ONOS5_intents\
                and ONOS1_intents == ONOS6_intents\
                and ONOS1_intents == ONOS7_intents:
            intent_check = main.TRUE
            main.log.report( "Intents are consistent across all ONOS nodes" )
        else:
            main.log.warn( "ONOS1 intents: " )
            print json.dumps( json.loads( ONOS1_intents ), sort_keys=True,
                              indent=4, separators=( ',', ': ' ) )
            main.log.warn( "ONOS2 intents: " )
            print json.dumps( json.loads( ONOS2_intents ), sort_keys=True,
                              indent=4, separators=( ',', ': ' ) )
            main.log.warn( "ONOS3 intents: " )
            print json.dumps( json.loads( ONOS3_intents ), sort_keys=True,
                              indent=4, separators=( ',', ': ' ) )
            main.log.warn( "ONOS4 intents: " )
            print json.dumps( json.loads( ONOS4_intents ), sort_keys=True,
                              indent=4, separators=( ',', ': ' ) )
            main.log.warn( "ONOS5 intents: " )
            print json.dumps( json.loads( ONOS5_intents ), sort_keys=True,
                              indent=4, separators=( ',', ': ' ) )
            main.log.warn( "ONOS6 intents: " )
            print json.dumps( json.loads( ONOS6_intents ), sort_keys=True,
                              indent=4, separators=( ',', ': ' ) )
            main.log.warn( "ONOS7 intents: " )
            print json.dumps( json.loads( ONOS7_intents ), sort_keys=True,
                              indent=4, separators=( ',', ': ' ) )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=intent_check,
            onpass="Intents are consistent across all ONOS nodes",
            onfail="ONOS nodes have different views of intents" )

        # NOTE: Hazelcast has no durability, so intents are lost across system
        # restarts
        main.step( "Compare current intents with intents before the failure" )
        # NOTE: this requires case 5 to pass for intent_state to be set.
        #      maybe we should stop the test if that fails?
        if intent_state == ONOS1_intents:
            same_intents = main.TRUE
            main.log.report( "Intents are consistent with before failure" )
        # TODO: possibly the states have changed? we may need to figure out
        # what the aceptable states are
        else:
            try:
                main.log.warn( "ONOS1 intents: " )
                print json.dumps( json.loads( ONOS1_intents ),
                                  sort_keys=True, indent=4,
                                  separators=( ',', ': ' ) )
            except:
                pass
            same_intents = main.FALSE
        utilities.assert_equals(
            expect=main.TRUE,
            actual=same_intents,
            onpass="Intents are consistent with before failure",
            onfail="The Intents changed during failure" )
        intent_check = intent_check and same_intents

        main.step( "Get the OF Table entries and compare to before " +
                   "component failure" )
        Flow_Tables = main.TRUE
        flows2 = []
        for i in range( 28 ):
            main.log.info( "Checking flow table on s" + str( i + 1 ) )
            tmp_flows = main.Mininet2.get_flowTable( 1.3, "s" + str( i + 1 ) )
            flows2.append( tmp_flows )
            temp_result = main.Mininet2.flow_comp(
                flow1=flows[ i ],
                flow2=tmp_flows )
            Flow_Tables = Flow_Tables and temp_result
            if Flow_Tables == main.FALSE:
                main.log.info( "Differences in flow table for switch: s" +
                               str( i + 1 ) )
        if Flow_Tables == main.TRUE:
            main.log.report( "No changes were found in the flow tables" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=Flow_Tables,
            onpass="No changes were found in the flow tables",
            onfail="Changes were found in the flow tables" )

        main.step( "Check the continuous pings to ensure that no packets " +
                   "were dropped during component failure" )
        # FIXME: This check is always failing. Investigate cause
        # NOTE:  this may be something to do with file permsissions
        #       or slight change in format
        main.Mininet2.pingKill(
            main.params[ 'TESTONUSER' ],
            main.params[ 'TESTONIP' ] )
        Loss_In_Pings = main.FALSE
        # NOTE: checkForLoss returns main.FALSE with 0% packet loss
        for i in range( 8, 18 ):
            main.log.info(
                "Checking for a loss in pings along flow from s" +
                str( i ) )
            Loss_In_Pings = main.Mininet2.checkForLoss(
                "/tmp/ping.h" +
                str( i ) ) or Loss_In_Pings
        if Loss_In_Pings == main.TRUE:
            main.log.info( "Loss in ping detected" )
        elif Loss_In_Pings == main.ERROR:
            main.log.info( "There are multiple mininet process running" )
        elif Loss_In_Pings == main.FALSE:
            main.log.info( "No Loss in the pings" )
            main.log.report( "No loss of dataplane connectivity" )
        utilities.assert_equals(
            expect=main.FALSE,
            actual=Loss_In_Pings,
            onpass="No Loss of connectivity",
            onfail="Loss of dataplane connectivity detected" )

        # Test of LeadershipElection
        # NOTE: this only works for the sanity test. In case of failures,
        # leader will likely change
        leader = ONOS1_ip
        leader_result = main.TRUE
        for controller in range( 1, num_controllers + 1 ):
            # loop through ONOScli handlers
            node = getattr( main, ( 'ONOScli' + str( controller ) ) )
            leaderN = node.election_test_leader()
            # verify leader is ONOS1
            if leaderN == leader:
                # all is well
                # NOTE: In failure scenario, this could be a new node, maybe
                # check != ONOS1
                pass
            elif leaderN == main.FALSE:
                # error in  response
                main.log.report( "Something is wrong with " +
                                 "election_test_leader function," +
                                 " check the error logs" )
                leader_result = main.FALSE
            elif leader != leaderN:
                leader_result = main.FALSE
                main.log.report( "ONOS" + str( controller ) + " sees " +
                                 str( leaderN ) +
                                 " as the leader of the election app. " +
                                 "Leader should be " + str( leader ) )
        if leader_result:
            main.log.report( "Leadership election tests passed(consistent " +
                             "view of leader across listeners and a new " +
                             "leader was re-elected if applicable)" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=leader_result,
            onpass="Leadership election passed",
            onfail="Something went wrong with Leadership election" )

        result = mastership_check and intent_check and Flow_Tables and\
                ( not Loss_In_Pings ) and roles_not_null and leader_result
        result = int( result )
        if result == main.TRUE:
            main.log.report( "Constant State Tests Passed" )
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                 onpass="Constant State Tests Passed",
                                 onfail="Constant state tests failed" )

    def CASE8( self, main ):
        """
        Compare topo
        """
        import sys
        # FIXME add this path to params
        sys.path.append( "/home/admin/sts" )
        # assumes that sts is already in you PYTHONPATH
        from sts.topology.teston_topology import TestONTopology
        import json
        import time

        description = "Compare ONOS Topology view to Mininet topology"
        main.case( description )
        main.log.report( description )
        main.step( "Create TestONTopology object" )
        ctrls = []
        count = 1
        while True:
            temp = ()
            if ( 'ip' + str( count ) ) in main.params[ 'CTRL' ]:
                temp = temp + ( getattr( main, ( 'ONOS' + str( count ) ) ), )
                temp = temp + ( "ONOS" + str( count ), )
                temp = temp + ( main.params[ 'CTRL' ][ 'ip' + str( count ) ], )
                temp = temp + \
                    ( eval( main.params[ 'CTRL' ][ 'port' + str( count ) ] ), )
                ctrls.append( temp )
                count = count + 1
            else:
                break
        MNTopo = TestONTopology(
            main.Mininet1,
            ctrls )  # can also add Intent API info for intent operations

        main.step( "Comparing ONOS topology to MN" )
        devices_results = main.TRUE
        ports_results = main.TRUE
        links_results = main.TRUE
        topo_result = main.FALSE
        elapsed = 0
        count = 0
        main.step( "Collecting topology information from ONOS" )
        start_time = time.time()
        while topo_result == main.FALSE and elapsed < 60:
            count = count + 1
            if count > 1:
                # TODO: Depricate STS usage
                MNTopo = TestONTopology(
                    main.Mininet1,
                    ctrls )
            cli_start = time.time()
            devices = []
            devices.append( main.ONOScli1.devices() )
            devices.append( main.ONOScli2.devices() )
            devices.append( main.ONOScli3.devices() )
            devices.append( main.ONOScli4.devices() )
            devices.append( main.ONOScli5.devices() )
            devices.append( main.ONOScli6.devices() )
            devices.append( main.ONOScli7.devices() )
            hosts = []
            hosts.append( main.ONOScli1.hosts() )
            hosts.append( main.ONOScli2.hosts() )
            hosts.append( main.ONOScli3.hosts() )
            hosts.append( main.ONOScli4.hosts() )
            hosts.append( main.ONOScli5.hosts() )
            hosts.append( main.ONOScli6.hosts() )
            hosts.append( main.ONOScli7.hosts() )
            ports = []
            ports.append( main.ONOScli1.ports() )
            ports.append( main.ONOScli2.ports() )
            ports.append( main.ONOScli3.ports() )
            ports.append( main.ONOScli4.ports() )
            ports.append( main.ONOScli5.ports() )
            ports.append( main.ONOScli6.ports() )
            ports.append( main.ONOScli7.ports() )
            links = []
            links.append( main.ONOScli1.links() )
            links.append( main.ONOScli2.links() )
            links.append( main.ONOScli3.links() )
            links.append( main.ONOScli4.links() )
            links.append( main.ONOScli5.links() )
            links.append( main.ONOScli6.links() )
            links.append( main.ONOScli7.links() )
            clusters = []
            clusters.append( main.ONOScli1.clusters() )
            clusters.append( main.ONOScli2.clusters() )
            clusters.append( main.ONOScli3.clusters() )
            clusters.append( main.ONOScli4.clusters() )
            clusters.append( main.ONOScli5.clusters() )
            clusters.append( main.ONOScli6.clusters() )
            clusters.append( main.ONOScli7.clusters() )
            paths = []
            temp_topo = main.ONOSbench.get_topology( main.ONOScli1.topology() )
            paths.append( temp_topo.get( 'paths', False ) )
            temp_topo = main.ONOSbench.get_topology( main.ONOScli2.topology() )
            paths.append( temp_topo.get( 'paths', False ) )
            temp_topo = main.ONOSbench.get_topology( main.ONOScli3.topology() )
            paths.append( temp_topo.get( 'paths', False ) )
            temp_topo = main.ONOSbench.get_topology( main.ONOScli4.topology() )
            paths.append( temp_topo.get( 'paths', False ) )
            temp_topo = main.ONOSbench.get_topology( main.ONOScli5.topology() )
            paths.append( temp_topo.get( 'paths', False ) )
            temp_topo = main.ONOSbench.get_topology( main.ONOScli6.topology() )
            paths.append( temp_topo.get( 'paths', False ) )
            temp_topo = main.ONOSbench.get_topology( main.ONOScli7.topology() )
            paths.append( temp_topo.get( 'paths', False ) )

            elapsed = time.time() - start_time
            cli_time = time.time() - cli_start
            print "CLI time: " + str( cli_time )

            for controller in range( num_controllers ):
                controller_str = str( controller + 1 )
                if devices[ controller ] or "Error" not in devices[
                        controller ]:
                    current_devices_result = main.Mininet1.compare_switches(
                        MNTopo,
                        json.loads(
                            devices[ controller ] ) )
                else:
                    current_devices_result = main.FALSE
                utilities.assert_equals( expect=main.TRUE,
                                         actual=current_devices_result,
                                         onpass="ONOS" + controller_str +
                                                " Switches view is correct",
                                         onfail="ONOS" + controller_str +
                                                " Switches view is incorrect" )

                if ports[ controller ] or "Error" not in ports[ controller ]:
                    current_ports_result = main.Mininet1.compare_ports(
                        MNTopo,
                        json.loads(
                            ports[ controller ] ) )
                else:
                    current_ports_result = main.FALSE
                utilities.assert_equals( expect=main.TRUE,
                                         actual=current_ports_result,
                                         onpass="ONOS" + controller_str +
                                                " ports view is correct",
                                         onfail="ONOS" + controller_str +
                                                " ports view is incorrect" )

                if links[ controller ] or "Error" not in links[ controller ]:
                    current_links_result = main.Mininet1.compare_links(
                        MNTopo,
                        json.loads(
                            links[ controller ] ) )
                else:
                    current_links_result = main.FALSE
                utilities.assert_equals( expect=main.TRUE,
                                         actual=current_links_result,
                                         onpass="ONOS" + controller_str +
                                                " links view is correct",
                                         onfail="ONOS" + controller_str +
                                                " links view is incorrect" )
            devices_results = devices_results and current_devices_result
            ports_results = ports_results and current_ports_result
            links_results = links_results and current_links_result

            # Compare json objects for hosts, dataplane clusters and paths

            # hosts
            consistent_hosts_result = main.TRUE
            for controller in range( len( hosts ) ):
                controller_str = str( controller + 1 )
                if "Error" not in hosts[ controller ]:
                    if hosts[ controller ] == hosts[ 0 ]:
                        continue
                    else:  # hosts not consistent
                        main.log.report( "hosts from ONOS" + controller_str +
                                         " is inconsistent with ONOS1" )
                        main.log.warn( repr( hosts[ controller ] ) )
                        consistent_hosts_result = main.FALSE

                else:
                    main.log.report( "Error in getting ONOS hosts from ONOS" +
                                     controller_str )
                    consistent_hosts_result = main.FALSE
                    main.log.warn( "ONOS" + controller_str +
                                   " hosts response: " +
                                   repr( hosts[ controller ] ) )
            utilities.assert_equals(
                expect=main.TRUE,
                actual=consistent_hosts_result,
                onpass="Hosts view is consistent across all ONOS nodes",
                onfail="ONOS nodes have different views of hosts" )

            # Strongly connected clusters of devices
            consistent_clusters_result = main.TRUE
            for controller in range( len( clusters ) ):
                controller_str = str( controller + 1 )
                if "Error" not in clusters[ controller ]:
                    if clusters[ controller ] == clusters[ 0 ]:
                        continue
                    else:  # clusters not consistent
                        main.log.report( "clusters from ONOS" +
                                         controller_str +
                                         " is inconsistent with ONOS1" )
                        consistent_clusters_result = main.FALSE

                else:
                    main.log.report( "Error in getting dataplane clusters " +
                                     "from ONOS" + controller_str )
                    consistent_clusters_result = main.FALSE
                    main.log.warn( "ONOS" + controller_str +
                                   " clusters response: " +
                                   repr( clusters[ controller ] ) )
            utilities.assert_equals(
                expect=main.TRUE,
                actual=consistent_clusters_result,
                onpass="Clusters view is consistent across all ONOS nodes",
                onfail="ONOS nodes have different views of clusters" )
            # there should always only be one cluster
            num_clusters = len( json.loads( clusters[ 0 ] ) )
            utilities.assert_equals(
                expect=1,
                actual=num_clusters,
                onpass="ONOS shows 1 SCC",
                onfail="ONOS shows " +
                str( num_clusters ) +
                " SCCs" )

            # paths
            consistent_paths_result = main.TRUE
            for controller in range( len( paths ) ):
                controller_str = str( controller + 1 )
                if "Error" not in paths[ controller ]:
                    if paths[ controller ] == paths[ 0 ]:
                        continue
                    else:  # paths not consistent
                        main.log.report( "paths from ONOS" + controller_str +
                                         " is inconsistent with ONOS1" )
                        consistent_paths_result = main.FALSE

                else:
                    main.log.report( "Error in getting paths from ONOS" +
                                     controller_str )
                    consistent_paths_result = main.FALSE
                    main.log.warn( "ONOS" + controller_str +
                                   " paths response: " +
                                   repr( paths[ controller ] ) )
            utilities.assert_equals(
                expect=main.TRUE,
                actual=consistent_paths_result,
                onpass="Paths count is consistent across all ONOS nodes",
                onfail="ONOS nodes have different counts of paths" )

            topo_result = ( devices_results and ports_results and links_results
                            and consistent_hosts_result
                            and consistent_clusters_result
                            and consistent_paths_result )

        topo_result = topo_result and int( count <= 2 )
        note = "note it takes about " + str( int( cli_time ) ) + \
                " seconds for the test to make all the cli calls to fetch " +\
                "the topology from each ONOS instance"
        main.log.report(
            "Very crass estimate for topology discovery/convergence(" +
            str( note ) + "): " + str( elapsed ) + " seconds, " +
            str( count ) + " tries" )
        utilities.assert_equals( expect=main.TRUE, actual=topo_result,
                                 onpass="Topology Check Test successful",
                                 onfail="Topology Check Test NOT successful" )
        if topo_result == main.TRUE:
            main.log.report( "ONOS topology view matches Mininet topology" )

    def CASE9( self, main ):
        """
        Link s3-s28 down
        """
        import time
        # NOTE: You should probably run a topology check after this

        link_sleep = float( main.params[ 'timers' ][ 'LinkDiscovery' ] )

        description = "Turn off a link to ensure that Link Discovery " +\
                "is working properly"
        main.log.report( description )
        main.case( description )

        main.step( "Kill Link between s3 and s28" )
        Link_Down = main.Mininet1.link( END1="s3", END2="s28", OPTION="down" )
        main.log.info(
            "Waiting " +
            str( link_sleep ) +
            " seconds for link down to be discovered" )
        time.sleep( link_sleep )
        utilities.assert_equals( expect=main.TRUE, actual=Link_Down,
                                 onpass="Link down succesful",
                                 onfail="Failed to bring link down" )
        # TODO do some sort of check here

    def CASE10( self, main ):
        """
        Link s3-s28 up
        """
        import time
        # NOTE: You should probably run a topology check after this

        link_sleep = float( main.params[ 'timers' ][ 'LinkDiscovery' ] )

        description = "Restore a link to ensure that Link Discovery is " + \
                "working properly"
        main.log.report( description )
        main.case( description )

        main.step( "Bring link between s3 and s28 back up" )
        Link_Up = main.Mininet1.link( END1="s3", END2="s28", OPTION="up" )
        main.log.info(
            "Waiting " +
            str( link_sleep ) +
            " seconds for link up to be discovered" )
        time.sleep( link_sleep )
        utilities.assert_equals( expect=main.TRUE, actual=Link_Up,
                                 onpass="Link up succesful",
                                 onfail="Failed to bring link up" )
        # TODO do some sort of check here

    def CASE11( self, main ):
        """
        Switch Down
        """
        # NOTE: You should probably run a topology check after this
        import time

        switch_sleep = float( main.params[ 'timers' ][ 'SwitchDiscovery' ] )

        description = "Killing a switch to ensure it is discovered correctly"
        main.log.report( description )
        main.case( description )
        switch = main.params[ 'kill' ][ 'switch' ]
        switchDPID = main.params[ 'kill' ][ 'dpid' ]

        # TODO: Make this switch parameterizable
        main.step( "Kill " + switch )
        main.log.report( "Deleting " + switch )
        main.Mininet1.del_switch( switch )
        main.log.info( "Waiting " + str( switch_sleep ) +
                       " seconds for switch down to be discovered" )
        time.sleep( switch_sleep )
        device = main.ONOScli1.get_device( dpid=switchDPID )
        # Peek at the deleted switch
        main.log.warn( str( device ) )
        result = main.FALSE
        if device and device[ 'available' ] is False:
            result = main.TRUE
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                 onpass="Kill switch succesful",
                                 onfail="Failed to kill switch?" )

    def CASE12( self, main ):
        """
        Switch Up
        """
        # NOTE: You should probably run a topology check after this
        import time

        switch_sleep = float( main.params[ 'timers' ][ 'SwitchDiscovery' ] )
        switch = main.params[ 'kill' ][ 'switch' ]
        switchDPID = main.params[ 'kill' ][ 'dpid' ]
        links = main.params[ 'kill' ][ 'links' ].split()
        description = "Adding a switch to ensure it is discovered correctly"
        main.log.report( description )
        main.case( description )

        main.step( "Add back " + switch )
        main.log.report( "Adding back " + switch )
        main.Mininet1.add_switch( switch, dpid=switchDPID )
        # TODO: New dpid or same? Ask Thomas?
        for peer in links:
            main.Mininet1.add_link( switch, peer )
        main.Mininet1.assign_sw_controller(
            sw=switch.split( 's' )[ 1 ],
            count=num_controllers,
            ip1=ONOS1_ip,
            port1=ONOS1_port,
            ip2=ONOS2_ip,
            port2=ONOS2_port,
            ip3=ONOS3_ip,
            port3=ONOS3_port,
            ip4=ONOS4_ip,
            port4=ONOS4_port,
            ip5=ONOS5_ip,
            port5=ONOS5_port,
            ip6=ONOS6_ip,
            port6=ONOS6_port,
            ip7=ONOS7_ip,
            port7=ONOS7_port )
        main.log.info(
            "Waiting " +
            str( switch_sleep ) +
            " seconds for switch up to be discovered" )
        time.sleep( switch_sleep )
        device = main.ONOScli1.get_device( dpid=switchDPID )
        # Peek at the deleted switch
        main.log.warn( str( device ) )
        result = main.FALSE
        if device and device[ 'available' ]:
            result = main.TRUE
        utilities.assert_equals( expect=main.TRUE, actual=result,
                                 onpass="add switch succesful",
                                 onfail="Failed to add switch?" )

    def CASE13( self, main ):
        """
        Clean up
        """
        import os
        import time
        # TODO: make use of this elsewhere
        ips = []
        ips.append(ONOS1_ip)
        ips.append(ONOS2_ip)
        ips.append(ONOS3_ip)
        ips.append(ONOS4_ip)
        ips.append(ONOS5_ip)
        ips.append(ONOS6_ip)
        ips.append(ONOS7_ip)

        # printing colors to terminal
        colors = {}
        colors[ 'cyan' ] = '\033[96m'
        colors[ 'purple' ] = '\033[95m'
        colors[ 'blue' ] = '\033[94m'
        colors[ 'green' ] = '\033[92m'
        colors[ 'yellow' ] = '\033[93m'
        colors[ 'red' ] = '\033[91m'
        colors[ 'end' ] = '\033[0m'
        description = "Test Cleanup"
        main.log.report( description )
        main.case( description )
        main.step( "Killing tcpdumps" )
        main.Mininet2.stop_tcpdump()

        main.step( "Checking ONOS Logs for errors" )
        for i in range(7):
            print colors[ 'purple' ] + "Checking logs for errors on " + \
                    "ONOS" + str( i + 1 ) + ":" + colors[ 'end' ]
            print main.ONOSbench.check_logs( ips[i] )

        main.step( "Copying MN pcap and ONOS log files to test station" )
        testname = main.TEST
        teststation_user = main.params[ 'TESTONUSER' ]
        teststation_IP = main.params[ 'TESTONIP' ]
        # NOTE: MN Pcap file is being saved to ~/packet_captures
        #       scp this file as MN and TestON aren't necessarily the same vm
        # FIXME: scp
        # mn files
        # TODO: Load these from params
        # NOTE: must end in /
        log_folder = "/opt/onos/log/"
        log_files = [ "karaf.log", "karaf.log.1" ]
        # NOTE: must end in /
        dst_dir = "~/packet_captures/"
        for f in log_files:
            for i in range(7):
                main.ONOSbench.handle.sendline( "scp sdn@" + ips[i] + ":" +
                                                log_folder + f + " " +
                                                teststation_user + "@" +
                                                teststation_IP + ":" +
                                                dst_dir + str( testname ) +
                                                "-ONOS" + str( i + 1 ) + "-" +
                                                f )
        # std*.log's
        # NOTE: must end in /
        log_folder = "/opt/onos/var/"
        log_files = [ "stderr.log", "stdout.log" ]
        # NOTE: must end in /
        dst_dir = "~/packet_captures/"
        for f in log_files:
            for i in range(7):
                main.ONOSbench.handle.sendline( "scp sdn@" + ips[i] + ":" +
                                                log_folder + f + " " +
                                                teststation_user + "@" +
                                                teststation_IP + ":" +
                                                dst_dir + str( testname ) +
                                                "-ONOS" + str( i + 1 ) + "-" +
                                                f )
        # sleep so scp can finish
        time.sleep( 10 )
        main.step( "Packing and rotating pcap archives" )
        os.system( "~/TestON/dependencies/rotate.sh " + str( testname ) )

        # TODO: actually check something here
        utilities.assert_equals( expect=main.TRUE, actual=main.TRUE,
                                 onpass="Test cleanup successful",
                                 onfail="Test cleanup NOT successful" )

    def CASE14( self, main ):
        """
        start election app on all onos nodes
        """
        leader_result = main.TRUE
        # install app on onos 1
        main.log.info( "Install leadership election app" )
        main.ONOScli1.feature_install( "onos-app-election" )
        # wait for election
        # check for leader
        leader = main.ONOScli1.election_test_leader()
        # verify leader is ONOS1
        if leader == ONOS1_ip:
            # all is well
            pass
        elif leader is None:
            # No leader elected
            main.log.report( "No leader was elected" )
            leader_result = main.FALSE
        elif leader == main.FALSE:
            # error in  response
            # TODO: add check for "Command not found:" in the driver, this
            # means the app isn't loaded
            main.log.report( "Something is wrong with election_test_leader" +
                             " function, check the error logs" )
            leader_result = main.FALSE
        else:
            # error in  response
            main.log.report(
                "Unexpected response from election_test_leader function:'" +
                str(leader) +
                "'" )
            leader_result = main.FALSE

        # install on other nodes and check for leader.
        # Should be onos1 and each app should show the same leader
        for controller in range( 2, num_controllers + 1 ):
            # loop through ONOScli handlers
            node = getattr( main, ( 'ONOScli' + str( controller ) ) )
            node.feature_install( "onos-app-election" )
            leaderN = node.election_test_leader()
            # verify leader is ONOS1
            if leaderN == ONOS1_ip:
                # all is well
                pass
            elif leaderN == main.FALSE:
                # error in  response
                # TODO: add check for "Command not found:" in the driver, this
                # means the app isn't loaded
                main.log.report( "Something is wrong with " +
                                 "election_test_leader function, check the" +
                                 " error logs" )
                leader_result = main.FALSE
            elif leader != leaderN:
                leader_result = main.FALSE
                main.log.report( "ONOS" + str( controller ) + " sees " +
                                 str( leaderN ) +
                                 " as the leader of the election app. Leader" +
                                 " should be " +
                                 str( leader ) )
        if leader_result:
            main.log.report( "Leadership election tests passed( consistent " +
                             "view of leader across listeners and a leader " +
                             "was elected)" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=leader_result,
            onpass="Leadership election passed",
            onfail="Something went wrong with Leadership election" )

    def CASE15( self, main ):
        """
        Check that Leadership Election is still functional
        """
        leader_result = main.TRUE
        description = "Check that Leadership Election is still functional"
        main.log.report( description )
        main.case( description )
        main.step( "Find current leader and withdraw" )
        leader = main.ONOScli1.election_test_leader()
        # TODO: do some sanity checking on leader before using it
        withdraw_result = main.FALSE
        if leader == ONOS1_ip:
            old_leader = getattr( main, "ONOScli1" )
        elif leader == ONOS2_ip:
            old_leader = getattr( main, "ONOScli2" )
        elif leader == ONOS3_ip:
            old_leader = getattr( main, "ONOScli3" )
        elif leader == ONOS4_ip:
            old_leader = getattr( main, "ONOScli4" )
        elif leader == ONOS5_ip:
            old_leader = getattr( main, "ONOScli5" )
        elif leader == ONOS6_ip:
            old_leader = getattr( main, "ONOScli6" )
        elif leader == ONOS7_ip:
            old_leader = getattr( main, "ONOScli7" )
        elif leader is None or leader == main.FALSE:
            main.log.report(
                "Leader for the election app should be an ONOS node," +
                "instead got '" +
                str(leader) +
                "'" )
            leader_result = main.FALSE
        withdraw_result = old_leader.election_test_withdraw()
        utilities.assert_equals(
            expect=main.TRUE,
            actual=withdraw_result,
            onpass="App was withdrawn from election",
            onfail="App was not withdrawn from election" )

        main.step( "Make sure new leader is elected" )
        leader_list = []
        for controller in range( 1, num_controllers + 1 ):
            # loop through ONOScli handlers
            node = getattr( main, ( 'ONOScli' + str( controller ) ) )
            leader_list.append( node.election_test_leader() )
        for leaderN in leader_list:
            if leaderN == leader:
                main.log.report(
                    "ONOS" +
                    str( controller ) +
                    " still sees " +
                    str( leader ) +
                    " as leader after they withdrew" )
                leader_result = main.FALSE
            elif leaderN == main.FALSE:
                # error in  response
                # TODO: add check for "Command not found:" in the driver, this
                # means the app isn't loaded
                main.log.report( "Something is wrong with " +
                                 "election_test_leader function, " +
                                 "check the error logs" )
                leader_result = main.FALSE
        consistent_leader = main.FALSE
        if len( set( leader_list ) ) == 1:
            main.log.info( "Each Election-app sees '" +
                           str(leader_list[0]) +
                           "' as the leader" )
            consistent_leader = main.TRUE
        else:
            main.log.report(
                "Inconsistent responses for leader of Election-app:" )
            for n in range( len( leader_list ) ):
                main.log.report( "ONOS" + str( n + 1 ) + " response: " +
                                 str( leader_list[ n ] ) )
        if leader_result:
            main.log.report( "Leadership election tests passed(consistent " +
                             "view of leader across listeners and a new " +
                             "leader was elected when the old leader " +
                             "resigned)" )
        utilities.assert_equals(
            expect=main.TRUE,
            actual=leader_result,
            onpass="Leadership election passed",
            onfail="Something went wrong with Leadership election" )

        main.step(
            "Run for election on old leader(just so everyone is in the hat)" )
        run_result = old_leader.election_test_run()
        utilities.assert_equals(
            expect=main.TRUE,
            actual=run_result,
            onpass="App re-ran for election",
            onfail="App failed to run for election" )
        if consistent_leader == main.TRUE:
            after_run = main.ONOScli1.election_test_leader()
            # verify leader didn't just change
            if after_run == leader_list[ 0 ]:
                leader_result = main.TRUE
            else:
                leader_result = main.FALSE
        # TODO: assert on  run and withdraw results?

        utilities.assert_equals(
            expect=main.TRUE,
            actual=leader_result,
            onpass="Leadership election passed",
            onfail="Something went wrong with Leadership election after " +
                   "the old leader re-ran for election" )
