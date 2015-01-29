# LincOETest
#
# Packet-Optical Intent Testing
#
# andrew@onlab.us


import time
import sys
import os
import re


class LincOETest:

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

        cellName = main.params[ 'ENV' ][ 'cellName' ]

        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        ONOS1Port = main.params[ 'CTRL' ][ 'port1' ]

        gitPullTrigger = main.params[ 'GIT' ][ 'autoPull' ]
        gitCheckoutBranch = main.params[ 'GIT' ][ 'checkout' ]

        main.case( "Setting up test environment" )

        main.step( "Creating cell file" )
        # params: ( bench ip, cell name, mininet ip, *onos ips )
        cellFileResult = main.ONOSbench.createCellFile(
            "10.128.20.10", cellName, "10.128.10.90",
            "onos-core-trivial,onos-app-fwd",
            "10.128.174.1" )

        main.step( "Applying cell variable to environment" )
        # cellResult = main.ONOSbench.setCell( cellName )
        cellResult = main.ONOSbench.setCell( "temp_cell_2" )
        verifyResult = main.ONOSbench.verifyCell()

        if gitPullTrigger == 'on':
            main.step( "Git checkout and pull master" )
            main.ONOSbench.gitCheckout( gitCheckoutBranch )
            gitPullResult = main.ONOSbench.gitPull()
        else:
            main.log.info( "Git checkout and pull skipped by config" )
            gitPullResult = main.TRUE

        main.step( "Using mvn clean & install" )
        # cleanInstallResult = main.ONOSbench.cleanInstall()
        cleanInstallResult = main.TRUE

        main.step( "Creating ONOS package" )
        packageResult = main.ONOSbench.onosPackage()

        main.step( "Installing ONOS package" )
        onosInstallResult = main.ONOSbench.onosInstall()
        onos1Isup = main.ONOSbench.isup()

        main.step( "Starting ONOS service" )
        startResult = main.ONOSbench.onosStart( ONOS1Ip )

        main.step( "Setting cell for ONOScli" )
        main.ONOScli.setCell( cellName )

        main.step( "Starting ONOScli" )
        main.ONOScli.startOnosCli( ONOS1Ip )

        case1Result = ( cleanInstallResult and packageResult and
                        cellResult and verifyResult and onosInstallResult and
                        onos1Isup and startResult )
        utilities.assertEquals( expect=main.TRUE, actual=case1Result,
                                onpass="Test startup successful",
                                onfail="Test startup NOT successful" )

        time.sleep( 10 )

    def CASE2( self, main ):
        """
        Configure topology
        """
        import time

        ONOS1Ip = main.params[ 'CTRL' ][ 'ip1' ]
        defaultSwPort = main.params[ 'CTRL' ][ 'port1' ]

        # Assign packet level switches to controller
        main.Mininet1.assignSwController(
            sw="1",
            ip1=ONOS1Ip,
            port1=defaultSwPort )
        main.Mininet1.assignSwController(
            sw="2",
            ip1=ONOS1Ip,
            port1=defaultSwPort )

        # Check devices in controller
        # This should include Linc-OE devices as well
        devices = main.ONOScli.devices()
        main.log.info( devices )

    def CASE3( self, main ):
        """
        Install multi-layer intents
        """
