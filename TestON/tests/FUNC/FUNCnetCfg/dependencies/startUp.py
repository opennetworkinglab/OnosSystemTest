"""
    This wrapper function is use for starting up onos instance
"""

import time

def onosBuild( main, gitBranch ):
    """
        This includes pulling ONOS and building it using maven install
    """

    buildResult = main.FALSE

    # Git checkout a branch of ONOS
    checkOutResult = main.ONOSbench.gitCheckout( gitBranch )
    # Does the git pull on the branch that was checked out
    if not checkOutResult:
        main.log.warn( "Failed to checked out " + gitBranch +
                                           " branch")
    else:
        main.log.info( "Successfully checked out " + gitBranch +
                                           " branch")
    gitPullResult = main.ONOSbench.gitPull()
    if gitPullResult == main.ERROR:
        main.log.error( "Error pulling git branch" )
    else:
        main.log.info( "Successfully pulled " + gitBranch + " branch" )

    # Maven clean install
    buildResult = main.ONOSbench.cleanInstall()

    return buildResult
