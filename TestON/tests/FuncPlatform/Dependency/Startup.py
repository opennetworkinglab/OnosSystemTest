
"""
Startup related methods for ONOS

Guidelines:
    * Group sequential functionalities together
    * Methods should not be dependent on platform
    * Return main.TRUE on success or comprehensive error message 
      on failure (TBD)
    * All methods should be consistent in expected behavior
"""
import time
import json

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
    
    Also verifies that Onos is up and running by 
    'isup' driver function which executs 
    'onos-wait-for-start'
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

    # Check if all nodes are discovered correctly using
    # 'nodes' command in Onos Cli
    na = main.TRUE
    try:
        nodeCmdJson = json.loads( main.CLIs[0].nodes() )
        for node in nodeCmdJson:
            if node['state'] != 'ACTIVE':
                main.log.warn( str( node['id'] ) + 
                        ' Node is not in ACTIVE state.' )
                na = main.FALSE
        if na != main.FALSE:
            main.log.info( 'All nodes discovered successfully' )
    except Exception:
        main.log.error( 'nodes command did not execute properly' )
        return main.FALSE

    if sc and vc and op and oi and iu and cli and na == main.TRUE:
        return main.TRUE
    else:
        return main.FALSE

def installOnosFromTar( wgetAddr, nodeIps ):
    """
    Install Onos directly from tar.gz file.
    Due to the nature of the specific steps required 
    to startup Onos in this fashion, all commands
    required to start Onos from tar.gz will be
    grouped in this method. 

    1) wget latest onos tar.gz on onos node
    2) untar package
    3) specify onos-config cluster
    4) start onos via onos-service
    5) form onos cluster using onos-form-cluster
    6) check for successful startup

    Specify the download link for the tar.gz.
    Provide a list of nodeIps

    Ex) wgetAddr = 'https://mytargzdownload.com/file.tar.gz'
        nodeIps = ['10.0.0.1', '10.0.0.2']
    """
    if isinstance( nodeIps, ( int, basestring ) ):
        main.log.error( 'Please pass in a list of string nodes' )
        return main.FALSE

    clusterCount = len( nodeIps )

    main.log.info( 'Initiating Onos installation sequence ' +
            'using tar.gz ... This may take a few minutes' )

    for node in range( 0, clusterCount ):
        try:
            main.ONOSnode[node].handle.sendline( 'wget ' + wgetAddr )
            main.ONOSnode[node].handle.expect( 'saved' )
            main.ONOSnode[node].handle.expect( '\$' )
            main.log.info( 'Successfully downloaded tar.gz ' +
                    'on node: ' + str( main.ONOSips[node] ) ) 
        except Exception:
            # NOTE: Additional exception may be appropriate 
            main.log.error( 'Uncaught exception while ' +
                    'downloading Onos tar.gz: ' + 
                    main.ONOSnode[node].handle.before )
            return main.FALSE

    return main.TRUE
    
def addAndStartOnosNode( nodeIps ):
    """
    A scale-out scenario that adds specified list of 
    nodes and starts those instances.

    Ex) nodeIps = ['10.0.0.2', '10.0.0.3', 10.0.0.4']
    """
    main.log.info( 'addAndStartOnosNode implement me!' )
