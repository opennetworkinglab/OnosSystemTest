
"""
Startup related methods for ONOS

Guidelines:
    * Group sequential functionalities together
    * Methods should not prohibit cross platform execution
    * Return main.TRUE on success or comprehensive error message 
      on failure (TBD)
"""
import time

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

def initOnosStartupSequence( cellName, appStr, benchIp, mnIp, onosIps ):
    """
    Startup sequence includes the following:
        * Create cell file
        * Set cell variables on ONOS bench
        * Verify cell
        * Create ONOS package
        * Force install ONOS package
        * Start ONOS service
        * Start ONOS cli
    """

    # NOTE: leave out create cell file until bug addressed
    #cf = main.ONOSbench.createCellFile( benchIp, cellName, mnIp, 
    #        str(appStr), *onosIps )
    numNodes = len(onosIps) 

    sc = main.ONOSbench.setCell( cellName )
    vc = main.ONOSbench.verifyCell()
    op = main.ONOSbench.onosPackage()
    for addr in onosIps:
        oi = main.ONOSbench.onosInstall( node = addr )
    
    time.sleep( 5 )
   
    iu = main.TRUE
    for node in onosIps:
        iu = iu and main.ONOSbench.isup( node )
   
    cli = main.TRUE
    for node in range( 0, numNodes ):
        cli = cli and main.CLIs[node].startOnosCli( onosIps[node] )

    if sc and vc and op and oi and iu and cli == main.TRUE:
        return main.TRUE
    else:
        return main.FALSE

