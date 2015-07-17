
# Testing network scalability, this test suite scales up a network topology
# using mininet and verifies ONOS stability

class SCPFscaleTopo:

    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        import time
        import os
        import imp

        """
        - Construct tests variables
        - GIT ( optional )
            - Checkout ONOS master branch
            - Pull latest ONOS code
        - Building ONOS ( optional )
            - Install ONOS package
            - Build ONOS package
        """

        main.case( "Constructing test variables and building ONOS package" )
        main.step( "Constructing test variables" )
        stepResult = main.FALSE

        # Test variables
        main.testOnDirectory = os.path.dirname( os.getcwd ( ) )
        main.apps = main.params[ 'ENV' ][ 'cellApps' ]
        gitBranch = main.params[ 'GIT' ][ 'branch' ]
        main.dependencyPath = main.testOnDirectory + \
                              main.params[ 'DEPENDENCY' ][ 'path' ]
        main.topology = main.params[ 'DEPENDENCY' ][ 'topology' ]
        main.scale = ( main.params[ 'SCALE' ][ 'size' ] ).split( "," )
        main.maxNodes = int( main.params[ 'SCALE' ][ 'max' ] )
        main.ONOSport = main.params[ 'CTRL' ][ 'port' ]
        wrapperFile1 = main.params[ 'DEPENDENCY' ][ 'wrapper1' ]
        wrapperFile2 = main.params[ 'DEPENDENCY' ][ 'wrapper2' ]
        main.startUpSleep = int( main.params[ 'SLEEP' ][ 'startup' ] )
        main.fwdSleep = int( main.params[ 'SLEEP' ][ 'fwd' ] )
        gitPull = main.params[ 'GIT' ][ 'pull' ]
        main.cellData = {} # for creating cell file
        main.hostsData = {}
        main.CLIs = []
        main.ONOSip = []

        main.ONOSip = main.ONOSbench.getOnosIps()
        print main.ONOSip

        # Assigning ONOS cli handles to a list
        for i in range( 1,  main.maxNodes + 1 ):
            main.CLIs.append( getattr( main, 'ONOScli' + str( i ) ) )

        # -- INIT SECTION, ONLY RUNS ONCE -- #
        main.startUp = imp.load_source( wrapperFile1,
                                        main.dependencyPath +
                                        wrapperFile1 +
                                        ".py" )
        main.scaleTopoFunction = imp.load_source( wrapperFile2,
                                                  main.dependencyPath +
                                                  wrapperFile2 +
                                                  ".py" )

        copyResult = main.ONOSbench.copyMininetFile( main.topology,
                                                     main.dependencyPath,
                                                     main.Mininet1.user_name,
                                                     main.Mininet1.ip_address )
        if main.CLIs:
            stepResult = main.TRUE
        else:
            main.log.error( "Did not properly created list of ONOS CLI handle" )
            stepResult = main.FALSE

        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Successfully construct " +
                                        "test variables ",
                                 onfail="Failed to construct test variables" )

        if gitPull == 'True':
            main.step( "Building ONOS in " + gitBranch + " branch" )
            onosBuildResult = main.startUp.onosBuild( main, gitBranch )
            stepResult = onosBuildResult
            utilities.assert_equals( expect=main.TRUE,
                                     actual=stepResult,
                                     onpass="Successfully compiled " +
                                            "latest ONOS",
                                     onfail="Failed to compile " +
                                            "latest ONOS" )
        else:
            main.log.warn( "Did not pull new code so skipping mvn " +
                           "clean install" )

    def CASE2( self, main ):
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
        main.numCtrls = int( main.scale[ 0 ] )

        main.case( "Starting up " + str( main.numCtrls ) +
                   " node(s) ONOS cluster" )

        #kill off all onos processes
        main.log.info( "Safety check, killing all ONOS processes" +
                       " before initiating enviornment setup" )

        for i in range( main.maxNodes ):
            main.ONOSbench.onosDie( main.ONOSip[ i ] )

        print "NODE COUNT = ", main.numCtrls

        tempOnosIp = []
        for i in range( main.numCtrls ):
            tempOnosIp.append( main.ONOSip[i] )

        main.ONOSbench.createCellFile( main.ONOSbench.ip_address,
                                       "temp", main.Mininet1.ip_address,
                                       main.apps,
                                       tempOnosIp )

        main.step( "Apply cell to environment" )
        cellResult = main.ONOSbench.setCell( "temp" )
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


        # Remove the first element in main.scale list
        main.scale.remove( main.scale[ 0 ] )

    def CASE9( self, main ):
        '''
            Report errors/warnings/exceptions
        '''
        main.log.info("Error report: \n" )
        main.ONOSbench.logReport( main.ONOSip[ 0 ],
                                  [ "INFO",
                                    "FOLLOWER",
                                    "WARN",
                                    "flow",
                                    "ERROR",
                                    "Except" ],
                                  "s" )

    def CASE11( self, main ):
        """
            Start mininet
        """
        main.log.report( "Start Mininet topology" )
        main.log.case( "Start Mininet topology" )

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

    def CASE1001( self, main ):
        """
            Test topology discovery
        """
        main.case( "Topology discovery test" )


        main.step( "Torus 5-5 topology" )
        main.topoName = "TORUS5-5"
        mnCmd = "mn --topo=torus,5,5 --mac"
        stepResult = main.scaleTopoFunction.testTopology( main,
                                                          mnCmd=mnCmd,
                                                          clean=False )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Torus 5-5 topology successful",
                                 onfail="Torus 5-5 topology failed" )

        main.topoName = "TREE3-3"
        stepResult = main.TRUE
        main.step( "Tree 3-3 topology" )
        mnCmd = "mn --topo=tree,3,3 --mac"
        stepResult = main.scaleTopoFunction.testTopology( main,
                                                          mnCmd=mnCmd,
                                                          clean=True )
        utilities.assert_equals( expect=main.TRUE,
                                 actual=stepResult,
                                 onpass="Tree 3-3 topology successful",
                                 onfail="Tree 3-3 topology failed" )
