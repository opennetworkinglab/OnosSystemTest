"""
Description: This test is an example of a simple single node ONOS test

List of test cases:
CASE1: Compile ONOS and push it to the test machine
CASE2: Assign mastership to controller
CASE3: Pingall
"""
class PingallExample:

    def __init__( self ) :
        self.default = ''

    def CASE1( self, main ) :
        """
           CASE1 is to compile ONOS and push it to the test machines

           Startup sequence:
           git pull
           mvn clean install
           onos-package
           cell <name>
           onos-verify-cell
           onos-install -f
           onos-wait-for-start
        """
        desc = "ONOS Single node cluster restart HA test - initialization"
        main.log.report( desc )
        main.case( "Setting up test environment" )

        # load some vairables from the params file
        PULL_CODE = False
        if main.params[ 'Git' ] == 'True':
            PULL_CODE = True
        cell_name = main.params[ 'ENV' ][ 'cellName' ]

        ONOS1_ip = main.params[ 'CTRL' ][ 'ip1' ]

        main.step( "Applying cell variable to environment" )
        cell_result = main.ONOSbench.set_cell( cell_name )
        verify_result = main.ONOSbench.verify_cell()

        main.log.report( "Uninstalling ONOS" )
        main.ONOSbench.onos_uninstall( ONOS1_ip )

        clean_install_result = main.TRUE
        git_pull_result = main.TRUE

        main.step( "Compiling the latest version of ONOS" )
        if PULL_CODE:
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

        cell_result = main.ONOSbench.set_cell( cell_name )
        verify_result = main.ONOSbench.verify_cell()
        main.step( "Creating ONOS package" )
        package_result = main.ONOSbench.onos_package()

        main.step( "Installing ONOS package" )
        onos1_install_result = main.ONOSbench.onos_install( options="-f",
                                                            node=ONOS1_ip )

        main.step( "Checking if ONOS is up yet" )
        for i in range( 2 ):
            onos1_isup = main.ONOSbench.isup( ONOS1_ip )
            if onos1_isup:
                break
        if not onos1_isup:
            main.log.report( "ONOS1 didn't start!" )

        # TODO: if it becomes an issue, we can retry this step  a few times

        cli_result = main.ONOScli1.start_onos_cli( ONOS1_ip )

        case1_result = ( clean_install_result and package_result and
                         cell_result and verify_result and
                         onos1_install_result and
                         onos1_isup and cli_result )

        utilities.assert_equals( expect=main.TRUE, actual=case1_result,
                                 onpass="Test startup successful",
                                 onfail="Test startup NOT successful" )

        if case1_result == main.FALSE:
            main.cleanup()
            main.exit()

    def CASE2( self, main ) :
        """
           Assign mastership to controller
        """
        import re

        main.log.report( "Assigning switches to controller" )
        main.case( "Assigning Controller" )
        main.step( "Assign switches to controller" )

        ONOS1_ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS1_port = main.params[ 'CTRL' ][ 'port1' ]

        for i in range( 1, 14 ):
            main.Mininet1.assign_sw_controller(
                sw=str( i ),
                ip1=ONOS1_ip,
                port1=ONOS1_port )

        mastership_check = main.TRUE
        for i in range( 1, 14 ):
            response = main.Mininet1.get_sw_controller( "s" + str( i ) )
            try:
                main.log.info( str( response ) )
            except:
                main.log.info( repr( response ) )
            if re.search( "tcp:" + ONOS1_ip, response ):
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

    def CASE3( self, main ) :
        """
           Assign intents
        """
        import time

        main.log.report( "Run Pingall" )
        main.case( "Run Pingall" )

        # install onos-app-fwd
        main.log.info( "Install reactive forwarding app" )
        main.ONOScli1.feature_install( "onos-app-fwd" )

        # REACTIVE FWD test
        ping_result = main.FALSE
        time1 = time.time()
        ping_result = main.Mininet1.pingall()
        time2 = time.time()
        main.log.info( "Time for pingall: %2f seconds" % ( time2 - time1 ) )

        # uninstall onos-app-fwd
        main.log.info( "Uninstall reactive forwarding app" )
        main.ONOScli1.feature_uninstall( "onos-app-fwd" )

        utilities.assert_equals( expect=main.TRUE, actual=ping_result,
                                 onpass="All hosts are reachable",
                                 onfail="Some pings failed" )
