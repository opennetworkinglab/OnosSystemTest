"""
FuncPlatform

A functional test designed to test the environment and 
gather startup / shutdown related issues.

Future works may also include security mode startup /
shutdown check and cfg get and set.

contributers to contact for help:
andrew@onlab.us
"""

class FuncPlatform:
    def __init__( self ):
        self.default = ''

    def CASE1( self, main ):
        import time
        import imp
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

        # List of ONOS ip's specififed in params
        global ONOSips
        # CLIs handle for each ONOS CLI client specified in .topo file
        global CLIs

        ONOSips = []
        CLIs = []

        for node in range( 0, int(main.params['CTRL']['num']) ):
            ONOSips.append( main.params['CTRL']['ip'+str(node+1)] )
            CLIs.append( getattr( main, 'ONOS' + str(i) + 'cli' ) )

        startupSrc = main.params['startupSrc']
        startupClassName = main.params['startupClassName']
        branchName = main.params['GIT']['branchName']
        gitPull = main.params['GIT']['pull']

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
        startupResult = startup.initOnosStartupSequence()
        utilities.assert_equals( expect=main.TRUE,
                        actual=startupResult,
                        onpass='ONOS startup sequence successful',
                        onfail='ONOS startup sequence failed: ' +
                            str(startupResult) )

    def CASE2( self, main ):
        main.log.info( "Case 2" )
