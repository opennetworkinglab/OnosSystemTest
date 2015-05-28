
def __init__( self ):
    self.ip = '127.0.0.1'

def activate( apps, nodeToActivateFrom=0 ):
    """
    Activate specified applications from node specified

    Ex) apps = ['metrics', 'fwd']
        nodeToActivateFrom = range( 0, nodes )
    """
    if isinstance( apps, ( int, basestring ) ):
        main.log.error( "Please pass in a list of strings for args" )
        return main.FALSE

    if not isinstance( nodeToActivateFrom, ( int ) ) or \
            nodeToActivateFrom < 0:
        main.log.error( "Incorrect node specified" )
        return main.FALSE

    for app in apps:
        # Check if app str in appList is in the main scope
        # definition main.appList
        if app not in main.appList:
            main.log.error( "Invalid app name given" )
            return main.FALSE
      
        # NOTE: assumes node 1 is always activating application
        appOutput = main.CLIs[nodeToActivateFrom].activateApp( 
                main.appList[app] ) 

    return main.TRUE

def isAppInstallSuccess():
    """
    Check the app list across clusters to determine
    that apps have been installed successfully

    """

    main.log.report( "isAppInstallSuccess" )

