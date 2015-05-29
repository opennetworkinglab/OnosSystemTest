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
            'optical' : 'org.onosproject.optical'
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

    def CASE2( self, main ):
        import time
        import imp

        startupSrc = main.params['DEP']['startupSrc']
        startupClassName = main.params['DEP']['startupClassName']
        cellName = main.params['CELL']['name']
        appStr = main.params['CELL']['appStr']
        benchIp = main.params['BENCH']['ip']
        branchName = main.params['GIT']['branchName']
        gitPull = main.params['GIT']['pull']
        mnIp = main.params['MN']['ip']

        # importing dependency class(es)
        # Refer to source files in Dependency folder to
        # make changes to its respective methods
        try:
            startup = imp.load_source( startupClassName, startupSrc )
        except ImportError:
            main.log.error( "Error importing class " +
                    str(startupClassName) + " from " + str(startupSrc) )
            main.cleanup()
            main.exit()

        main.case( 'Setup environment and install ONOS' )
        if gitPull == 'on': 
            main.step( 'Git pull and clean install' )
            gitPullResult = startup.gitPullAndMci( branchName )
            utilities.assert_equals( expect=main.TRUE,
                        actual=gitPullResult,
                        onpass='Git pull and install successful',
                        onfail='Git pull and install failed: ' +
                            str(gitPullResult) )
        
        main.step( 'Initiate ONOS startup sequence' )    
        startupResult = startup.initOnosStartupSequence(
                cellName, appStr, benchIp, mnIp, main.ONOSips )
        utilities.assert_equals( expect=main.TRUE,
                        actual=startupResult,
                        onpass='ONOS startup sequence successful',
                        onfail='ONOS startup sequence failed: ' +
                            str(startupResult) )
        
    def CASE3( self, main ):
        import time
        import imp

        main.case( 'Activate applications and check installation' )
        # Activate applications and check consistency 
        # across clusters
        appClassName = main.params['DEP']['appClassName']
        appSrc = main.params['DEP']['appSrc']

        logClassName = main.params['DEP']['logClassName']
        logSrc = main.params['DEP']['logSrc']

        # Import application file to use its methods
        try:
            app = imp.load_source( appClassName, appSrc )
            onosLog = imp.load_source( logClassName, logSrc )
        except ImportError:
            main.log.error( "Error importing class " +
                    str(startupClassName) + " from " + str(startupSrc) )
            main.cleanup()
            main.exit()
       
        # NOTE: Test only
        # Unceremoniously kill onos 2 
        main.ONOSbench.onosDie( '10.128.174.2' )
        
        time.sleep( 30 )

        main.step( 'Sample Onos log check' )
        logResult = onosLog.checkOnosLog( main.ONOSips[0] )
        main.log.info( logResult )
        # TODO: Define assertion pass / fail criteria

        # Sample app activation
        main.step( 'Activating applications metrics and fwd' ) 
        appList = ['metrics', 'fwd']
        appResult = app.activate( appList ) 
        utilities.assert_equals( expect=main.TRUE,
                actual=appResult,
                onpass= 'App activation of ' + str(appList) + ' successful',
                onfail= 'App activation failed ' + str(appResult) )



