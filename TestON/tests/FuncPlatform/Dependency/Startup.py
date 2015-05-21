
"""
Startup related methods for ONOS

Guidelines:
    * Group sequential functionalities together
    * Methods should not prohibit cross platform execution
    * Return main.TRUE on success or comprehensive error message 
      on failure (TBD)
"""

def __init__( self ):
    self.ip = '127.0.0.1' 

def gitPullAndMci( branchName, commitLog=False ):
    """
    Pull from branch repository specified and compile changes
    If commitLog is True, report commit information

    Any errors / warnings will be handled by respective 
    driver function calls
    """
    co = main.ONOSbench.gitCheckout( branchName )
    gp = main.ONOSbench.gitPull()
    ci = main.ONOSbench.cleanInstall() 

    if co and gp and ci == main.TRUE:
        if commitLog:
            main.log.report( 'Commit information - ' )
            main.ONOSbench.getVersion(report=True)
        
        return main.TRUE
    
    else:
        # TODO: Comprehensive error message
        return 'git pull and mci failed'

def initOnosStartupSequence( cellName, appsStr, benchIp, onosIps ):
    """
    Startup sequence includes the following:
        * 
    """
    main.log.info( 'Initiating ONOS startup sequence' )

def isOnosNormal( onosIps ):
    """
    Quick and comprehensive check for 'normality'

    Definition of function TBD
    """
    main.log.info( 'isOnosNormal' )
