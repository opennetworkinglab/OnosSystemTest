
# Testing the basic functionality of ONOS Next
# For sanity and driver functionality excercises only.

import time
import json

class FuncTopo:

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
        global init
        global globalONOSip
        try:
            if type(init) is not bool:
                init = False
        except NameError:
            init = False

        #Local variables
        cellName = main.params[ 'ENV' ][ 'cellName' ]
        apps = main.params[ 'ENV' ][ 'cellApps' ]
        gitBranch = main.params[ 'GIT' ][ 'branch' ]
        benchIp = os.environ[ 'OCN' ]
        benchUser = main.params[ 'BENCH' ][ 'user' ]
        topology = main.params[ 'MININET' ][ 'topo' ]
        main.numSwitch = int( main.params[ 'MININET' ][ 'switch' ] )
        main.numLinks = int( main.params[ 'MININET' ][ 'links' ] )
        main.numCtrls = main.params[ 'CTRL' ][ 'num' ]
        PULLCODE = False
        if main.params[ 'GIT' ][ 'pull' ] == 'True':
            PULLCODE = True
        main.case( "Setting up test environment" )
        main.CLIs = []
        for i in range( 1, int( main.numCtrls ) + 1 ):
            main.CLIs.append( getattr( main, 'ONOScli' + str( i ) ) )

        # -- INIT SECTION, ONLY RUNS ONCE -- #
        if init == False:
            init = True

            main.ONOSport = []
            main.scale = ( main.params[ 'SCALE' ] ).split( "," )
            main.numCtrls = int( main.scale[ 0 ] )

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
                                         onpass="Successfully compiled " +
                                                "latest ONOS",
                                         onfail="Failed to compile " +
                                                "latest ONOS" )
            else:
                main.log.warn( "Did not pull new code so skipping mvn " +
                               "clean install" )

            globalONOSip = main.ONOSbench.getOnosIps()
        maxNodes = ( len(globalONOSip) - 2 )

        main.numCtrls = int( main.scale[ 0 ] )
        main.scale.remove( main.scale[ 0 ] )

        main.ONOSip = []
        for i in range( maxNodes ):
            main.ONOSip.append( globalONOSip[i] )

        #kill off all onos processes
        main.log.info( "Safety check, killing all ONOS processes" +
                       " before initiating enviornment setup" )
        for i in range(maxNodes):
            main.ONOSbench.onosDie( globalONOSip[ i ] )

        print "NODE COUNT = ", main.numCtrls
        main.log.info( "Creating cell file" )
        cellIp = []
        for i in range( main.numCtrls ):
            cellIp.append( str( main.ONOSip[ i ] ) )
        print cellIp
        main.ONOSbench.createCellFile( benchIp, cellName, "",
                                       str( apps ), *cellIp )

        main.step( "Apply cell to environment" )
        cellResult = main.ONOSbench.setCell( cellName )
        verifyResult = main.ONOSbench.verifyCell()
        stepResult = cellResult and verifyResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully applied cell to " + \
                                        "environment",
                                 onfail="Failed to apply cell to environment " )

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()
        stepResult = packageResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully created ONOS package",
                                 onfail="Failed to create ONOS package" )

        main.step( "Uninstalling ONOS package" )
        onosUninstallResult = main.TRUE
        for i in range( main.numCtrls ):
            onosUninstallResult = onosUninstallResult and \
                    main.ONOSbench.onosUninstall( nodeIp=main.ONOSip[ i ] )
        stepResult = onosUninstallResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully uninstalled ONOS package",
                                 onfail="Failed to uninstall ONOS package" )
        time.sleep( 5 )
        main.step( "Installing ONOS package" )
        onosInstallResult = main.TRUE
        for i in range( main.numCtrls ):
            onosInstallResult = onosInstallResult and \
                    main.ONOSbench.onosInstall( node=main.ONOSip[ i ] )
        stepResult = onosInstallResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully installed ONOS package",
                                 onfail="Failed to install ONOS package" )

        time.sleep( 20 )
        main.step( "Starting ONOS service" )
        stopResult = main.TRUE
        startResult = main.TRUE
        onosIsUp = main.TRUE
        for i in range( main.numCtrls ):
            onosIsUp = onosIsUp and main.ONOSbench.isup( main.ONOSip[ i ] )
        if onosIsUp == main.TRUE:
            main.log.report( "ONOS instance is up and ready" )
        else:
            main.log.report( "ONOS instance may not be up, stop and " +
                             "start ONOS again " )
            for i in range( main.numCtrls ):
                stopResult = stopResult and \
                        main.ONOSbench.onosStop( main.ONOSip[ i ] )
            for i in range( main.numCtrls ):
                startResult = startResult and \
                        main.ONOSbench.onosStart( main.ONOSip[ i ] )
        stepResult = onosIsUp and stopResult and startResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="ONOS service is ready",
                                 onfail="ONOS service did not start properly" )

        main.step( "Start ONOS cli" )
        cliResult = main.TRUE
        for i in range( main.numCtrls ):
            cliResult = cliResult and \
                        main.CLIs[i].startOnosCli( main.ONOSip[ i ] )
        stepResult = cliResult
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully start ONOS cli",
                                 onfail="Failed to start ONOS cli" )

    def CASE9( self, main ):
        '''
            Report errors/warnings/exceptions
        '''
        main.log.info("Error report: \n")
        main.ONOSbench.logReport( globalONOSip[0],
                                  [ "INFO","FOLLOWER","WARN",
                                    "flow","ERROR","Except" ],
                                  "s" )
        #main.ONOSbench.logReport( globalONOSip[1], [ "INFO" ], "d" )

    def CASE1001( self, main )
    """
        Test topology discovery
    """
