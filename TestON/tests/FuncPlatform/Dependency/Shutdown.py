
def __init__( self ):
    self.ip = '127.0.0.1'

def killOnosNodes( nodeIps ):
    """
    Kill all components of Onos on 
    given list of ips
    
    Ex) nodeIps = ['10.0.0.1', '10.0.0.2']
    """
    killResult = main.TRUE
    
    for node in nodeIps:
        killResult = killResult and main.ONOSbench.onosDie( node )
        if killResult == main.TRUE:
            main.log.info( str(node) + ' was killed' ) 

    return killResult
