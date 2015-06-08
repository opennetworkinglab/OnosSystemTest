"""
FuncPlatform

A functional test designed to test the environment and 
gather information on startup -> shutdown related issues.

Future works may also include security mode startup /
shutdown check and cfg get and set.

Abstracting the collection of commands that go hand in hand 
should allow easy rearrangement of steps to replicate or 
create scenarios. 
For example:
    CASE N - Represents a particular scenario
        Steps - Represents abstraction methods called from 
                dependency
        1. Bring ONOS 1 up
        2. Activate application X
        3. Activate application Y
        4. Deactivate application X

The ideal platform test script should have incredible
robustness to possible exceptions and report the most
useful error messages. 

contributers to contact for help:
andrew@onlab.us
"""

class FuncPlatform:
    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        """
        Main scope initialization case
        Must include to run any other test cases
        """   
        import imp 

        # NOTE: Hardcoded application name subject to change
        #       closely monitor and make changes when necessary
        #       (or implement ways to dynamically get names)
        main.appList = { 
            'bgprouter' : 'org.onosproject.bgprouter',
            'config' : 'org.onosproject.config',
            'cordfabric' : 'org.onosproject.cordfabric',
            'demo' : 'org.onosproject.demo',
            'distributedprimitives' : 'org.onosproject.distributedprimitives',
            'election' : 'org.onosproject.election',
            'flowrule' : 'org.onosproject.flowrule',
            'fwd' : 'org.onosproject.fwd',
            'intentperf' : 'org.onosproject.intentperf',
            'messagingperf' : 'org.onosproject.messagingperf',
            'metrics' : 'org.onosproject.metrics',
            'mobility' : 'org.onosproject.mobility',
            'netconf' : 'org.onosproject.netconf', 
            'null' : 'org.onosproject.null',
            'optical' : 'org.onosproject.optical',
            'pcep' : 'org.onosproject.pcep',
            'proxyarp' : 'org.onosproject.proxyarp',
            'reactive.routing' : 'org.onosproject.reactive.routing',
            'sdnip' : 'org.onosproject.sdnip',
            'segmentrouting' : 'org.onosproject.segmentrouting',
            'tunnel' : 'org.onosproject.tunnel',
            'virtualbng' : 'org.onosproject.virtualbng',
            'xosintegration' : 'org.onosproject.xosintegration'
            } 
        # List of ONOS ip's specififed in params
        main.ONOSips = [] 
        main.CLIs = []
        main.ONOSnode = []

        for node in range( 0, int(main.params['CTRL']['num']) ):
            main.ONOSips.append( main.params['CTRL']['ip'+str(node+1)] )
            main.CLIs.append(
                    getattr( main, 'ONOS' + str(node+1) + 'cli' ) )
            main.ONOSnode.append(
                    getattr( main, 'ONOS' + str(node+1) ) )
       
        # Application source and name definitions
        startupSrc = main.params['DEP']['startupSrc']
        startupClassName = main.params['DEP']['startupClassName']
        
        appClassName = main.params['DEP']['appClassName']
        appSrc = main.params['DEP']['appSrc']

        logClassName = main.params['DEP']['logClassName']
        logSrc = main.params['DEP']['logSrc']

        shutdownClassName = main.params['DEP']['shutdownClassName']
        shutdownSrc = main.params['DEP']['shutdownSrc']

        # Importing dependency class(es)
        # Refer to source files in Dependency folder to
        # make changes to its respective methods
        # Be weary of naming collisions
        try:
            main.startup = imp.load_source( startupClassName, startupSrc )
            main.app = imp.load_source( appClassName, appSrc )
            main.onosLog = imp.load_source( logClassName, logSrc )
            main.shutdown = imp.load_source( shutdownClassName, shutdownSrc )
        except ImportError:
            main.log.error( 'Error importing class file(s). Please ' +
                    'check file location' )
            main.cleanup()
            main.exit()

    def CASE2( self, main ):
        import time

        cellName = main.params['CELL']['name']
        appStr = main.params['CELL']['appStr']
        benchIp = main.params['BENCH']['ip']
        branchName = main.params['GIT']['branchName']
        gitPull = main.params['GIT']['pull']
        mnIp = main.params['MN']['ip']

        main.case( 'Setup environment and install ONOS' )
        if gitPull == 'on': 
            main.step( 'Git pull and clean install' )
            gitPullResult = main.startup.gitPullAndMci( branchName )
            utilities.assert_equals( expect=main.TRUE,
                        actual=gitPullResult,
                        onpass='Git pull and install successful',
                        onfail='Git pull and install failed: ' +
                            str(gitPullResult) )
        
        main.step( 'Initiate ONOS startup sequence' )    
        startupResult = main.startup.initOnosStartupSequence(
                cellName, appStr, benchIp, mnIp, main.ONOSips )
        utilities.assert_equals( expect=main.TRUE,
                        actual=startupResult,
                        onpass='ONOS startup sequence successful',
                        onfail='ONOS startup sequence failed: ' +
                            str(startupResult) )
        
    def CASE3( self, main ):
        import time

        main.case( 'Activate applications and check installation' )
       
        # NOTE: Test only
        # Unceremoniously kill onos 2 
        main.ONOSbench.onosDie( '10.128.174.2' )
        
        time.sleep( 30 )

        main.step( 'Sample Onos log check' )
        logResult = main.onosLog.checkOnosLog( main.ONOSips[0] )
        main.log.info( logResult )
        # TODO: Define pass criteria
        utilities.assert_equals( expect=main.TRUE,
                actual=main.TRUE,
                onpass= 'Logging successful',
                onfail= 'Logging failed ' )

        # Sample app activation
        main.step( 'Activating applications metrics and fwd' ) 
        appList = ['metrics', 'fwd']
        appResult = main.app.activate( appList ) 
        utilities.assert_equals( expect=main.TRUE,
                actual=appResult,
                onpass= 'App activation of ' + str(appList) + ' successful',
                onfail= 'App activation failed ' + str(appResult) )

    def CASE4( self, main ):
        """
        Download ONOS tar.gz built from latest nightly
        (following tutorial on wiki) and run ONOS directly on the
        instance
        """
        import imp

        targz = main.params['DEP']['targz']
        clusterCount = main.params['CTRL']['num']
       
        main.case( 'Install ONOS from onos.tar.gz file' )

        main.step( 'Killing all ONOS instances previous started' )
        killResult = main.shutdown.killOnosNodes( main.ONOSips )
        utilities.assert_equals( expect=main.TRUE,
                actual = killResult,
                onpass = 'All Onos nodes successfully killed',
                onfail = 'Onos nodes were not successfully killed' )

        main.step( 'Starting ONOS using tar.gz on all nodes' )
        installResult = main.startup.installOnosFromTar( targz, main.ONOSips )
        utilities.assert_equals( expect=main.TRUE,
                actual = installResult,
                onpass= 'Onos tar.gz installation successful',
                onfail= 'Onos tar.gz installation failed' )


