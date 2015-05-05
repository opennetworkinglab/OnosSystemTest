
# Testing the basic functionality of ONOS Next
# For sanity and driver functionality excercises only.

import time
import json

time.sleep( 1 )

class SingleFunc:

    def __init__( self ):
        self.default = ''

    def CASE10( self, main ):
        import time
        import os
        """
        Startup sequence:
        cell <name>
        onos-verify-cell
        onos-remove-raft-log
        git pull
        mvn clean install
        onos-package
        onos-install -f
        onos-wait-for-start
        """
        #Local variables
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        main.ONOS1ip = os.environ[ 'OC1' ]
        main.ONOS1port = main.params[ 'CTRL' ][ 'port1' ]
        main.numSwitch = int( main.params[ 'MININET' ][ 'switch' ] )
        gitBranch = main.params[ 'GIT' ][ 'branch' ]
        topology = main.params[ 'MININET' ][ 'topo' ]
        PULLCODE = False
        if main.params[ 'GIT' ][ 'pull' ] == 'True':
            PULLCODE = True
        main.case( "Setting up test environment" )

        main.step( "Apply cell to environment" )
        cellResult = main.ONOSbench.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()
        stepResult = cellResult and verifyResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully applied cell to " + \
                                        "environment",
                                 onfail="Failed to apply cell to environment " )
        """main.step( "Removing raft logs" )
        removeRaftResult = main.ONOSbench.onosRemoveRaftLogs()
        stepResult = removeRaftResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully removed raft logs",
                                 onfail="Failed to remove raft logs" )
        """
        if PULLCODE:
            main.step( "Git checkout and pull " + gitBranch )
            main.ONOSbench.gitCheckout( gitBranch )
            gitPullResult = main.ONOSbench.gitPull()
            if gitPullResult == main.ERROR:
                main.log.error( "Error pulling git branch" )
            main.step( "Using mvn clean & install" )
            cleanInstallResult = main.ONOSbench.cleanInstall()
            stepResult = cleanInstallResult
            utilities.assert_equals( expect=main.TRUE,
                                     actual=stepResult,
                                     onpass="Successfully compiled latest ONOS",
                                     onfail="Failed to compile latest ONOS" )
        else:
            main.log.warn( "Did not pull new code so skipping mvn " +
                           "clean install" )

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()
        stepResult = packageResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully created ONOS package",
                                 onfail="Failed to create ONOS package" )

        main.step( "Uninstalling ONOS package" )
        onosUninstallResult = main.ONOSbench.onosUninstall(
                                                          nodeIp=main.ONOS1ip )
        stepResult = onosUninstallResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully uninstalled ONOS package",
                                 onfail="Failed to uninstall ONOS package" )
        time.sleep( 5 )
        main.step( "Installing ONOS package" )
        onosInstallResult = main.ONOSbench.onosInstall( node=main.ONOS1ip )
        stepResult = onosInstallResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully installed ONOS package",
                                 onfail="Failed to install ONOS package" )

        main.step( "Starting ONOS service" )
        stopResult = main.TRUE
        startResult = main.TRUE
        onosIsUp = main.ONOSbench.isup()
        if onosIsUp == main.TRUE:
            main.log.report( "ONOS instance is up and ready" )
        else:
            main.log.report( "ONOS instance may not be up, stop and " +
                             "start ONOS again " )
            stopResult = main.ONOSbench.onosStop( main.ONOS1ip )
            startResult = main.ONOSbench.onosStart( main.ONOS1ip )
        stepResult = onosIsUp and stopResult and startResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ONOS service is ready",
                                 onfail="ONOS service did not start properly" )

        main.step( "Starting Mininet Topology" )
        topoResult = main.Mininet1.startNet( topoFile=topology )
        stepResult = topoResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully loaded topology",
                                 onfail="Failed to load topology" )
        # Exit if topology did not load properly
        if not topoResult:
            main.cleanup()
            main.exit()

        main.step( "Start ONOS cli" )
        cliResult =  main.ONOScli1.startOnosCli( ONOSIp=main.ONOS1ip )
        stepResult = cliResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully start ONOS cli",
                                 onfail="Failed to start ONOS cli" )

    def CASE11( self, main ):
        """
        Assign mastership to controllers
        """
        main.log.report( "Assigning switches to controllers" )
        main.log.case( "Assigning swithes to controllers" )

        main.step( "Assigning switches to controllers" )
        assignResult = main.TRUE
        for i in range( 1, 8 ):
            main.Mininet1.assignSwController( sw=str( i ),
                                              count=1,
                                              ip1=ONOS1ip,
                                              port1=ONOS1port )
        for i in range( 1, ( main.numSwitches + 1 ) ):
            response = main.Mininet1.getSwController( "s" + str( i ) )
            print( "Response is " + str( response ) )
            if re.search( "tcp:" + main.ONOS1cli, response ):
                assignResult = assignResult and main.TRUE
            else:
                assignResult = main.FALSE
        stepResult = assignResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully assigned switches" +
                                        "to controller",
                                 onfail="Failed to assign switches to " +
                                        "controller" )


