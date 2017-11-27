"""
Copyright 2017 Open Networking Foundation ( ONF )

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    ( at your option ) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.
"""
import json

def checkingNumNodes( main, expected ):
    """
    check the number of nodes
    :param expected:
        Expected number of nodes
    :return:
        main.TRUE if all the number of the nodes are matched
        main.FALSE if not.
    """
    result = main.TRUE
    for cluster in main.Cluster.active():
        actual = json.loads( cluster.CLI.summary() ).get( 'nodes' )
        thisResult = main.TRUE if expected == actual else main.FALSE
        if not thisResult:
            main.log.error( "Number of the nodes not matched." +
                            "\nExpected nodes: " + str( expected ) +
                            "\nActual nodes: " + str( actual ) )
    return result

def checkingApp( main, appToBeChecked, cluster, expectedToBeThere ):
    """
    check the existence of app
    :param appToBeChecked:
        Name of the apps to be checked
    :param cluster:
        nth cluster to be checked
    :param expectedToBeThere:
        True if it is expected to be installed. False if it is expected not to be installed.
    :return:
        main.TRUE if they are all matched. Otherwise main.FALSE
    """
    result = False
    appStatus = cluster.CLI.appStatus( appToBeChecked )
    if appStatus == "ACTIVE" if expectedToBeThere else "UNINSTALL":
        result = True
    if result:
        main.log.info( "App is " + ( "not " if not expectedToBeThere else "" ) + "there as expected" )
        return main.TRUE
    else:
        main.log.error("App is " + ( "" if not expectedToBeThere else "not " ) + "there which should" +
                       ( "n't" if not expectedToBeThere else "" ) + " be there.")
        return main.FALSE
