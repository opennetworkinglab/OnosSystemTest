"""
Copyright 2016 Open Networking Foundation ( ONF )

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
import time
import json
"""
    Warp function for SCPFportLat test
"""
def capturePortStatusPack( main, deviceName, interface, portStatus, resultDict, warmup ):
    """
    Change device port status and use tshark to capture openflow port package
    Args:
        main: TestON class
        deviceName: Device to change portStatus
        interface: port number
        portStatus: up or down
        resultDict: put result to dictionary
        warmup: if warmup, ignore results

    """
    main.log.info( "Clean up tshark" )
    with open( main.tsharkResultPath, "w" ) as tshark:
        tshark.write( "" )
    main.log.info( "Starting tshark capture" )
    main.ONOSbench.tsharkGrep( main.ofportStatus, main.tsharkResultPath )
    time.sleep( main.measurementSleep )
    main.log.info( "{} port {} {}".format( deviceName, interface, portStatus ) )
    main.Mininet1.changeInterfaceStatus( deviceName, interface, portStatus )
    time.sleep( main.measurementSleep )
    main.log.info( "Stopping all Tshark processes" )
    main.ONOSbench.tsharkStop()

    # Get tshark output
    with open( main.tsharkResultPath, "r" ) as resultFile:
        resultText = resultFile.readline()
        main.log.info( "Capture result:" + resultText )
        resultText = resultText.strip().split( " " )
        if len( resultText ) > 1:
            tsharkResultTime = int( float( resultText[ 1 ] ) * 1000.0 )
            resultFile.close()
            for i in range( 1, main.Cluster.numCtrls + 1 ):
                main.log.info( "================================================" )
                # get onos metrics timestamps
                try:
                    response = json.loads( main.Cluster.active( i - 1 ).CLI.topologyEventsMetrics() )
                    deviceTime = int( response.get( "topologyDeviceEventTimestamp" ).get( "value" ) )
                    main.log.info( "ONOS{} device Event timestemp: {}".format( i, deviceTime ) )

                    linkTime = int( response.get( "topologyLinkEventTimestamp" ).get( "value" ) )
                    main.log.info( "ONOS{} Link Event timestemp: {}".format( i, linkTime ) )

                    graphTime = int( response.get( "topologyGraphEventTimestamp" ).get( "value" ) )
                    main.log.info( "ONOS{} Graph Event timestemp: {}".format( i, graphTime ) )
                except TypeError:
                    main.log.warn( "TypeError!" )
                    break
                except ValueError:
                    main.log.warn( "Unable to decode Json object!" )
                    break
                main.log.info( "================================================" )
                # calculate latency
                EtoE = graphTime - tsharkResultTime
                PtoD = deviceTime - tsharkResultTime
                DtoL = linkTime - deviceTime
                LtoG = graphTime - linkTime
                main.log.info( "ONOS{} End to End time: {}".format( i, EtoE ) )
                main.log.info( "ONOS{} Package to Device time: {}".format( i, PtoD ) )
                main.log.info( "ONOS{} Device to Link time: {}".format( i, DtoL ) )
                main.log.info( "ONOS{} Link to Graph time: {}".format( i, LtoG ) )
                # if less than 0 waring
                if EtoE < 0 or PtoD < 0 or DtoL < 0 or LtoG < 0:
                    main.log.warn( "Latency less than 0! Ingore this loop." )
                else:
                    # put result to dictionary
                    if not warmup:
                        resultDict[ portStatus ][ 'node' + str( i ) ][ 'EtoE' ].append( EtoE )
                        resultDict[ portStatus ][ 'node' + str( i ) ][ 'PtoD' ].append( PtoD )
                        resultDict[ portStatus ][ 'node' + str( i ) ][ 'DtoL' ].append( DtoL )
                        resultDict[ portStatus ][ 'node' + str( i ) ][ 'LtoG' ].append( LtoG )
        else:
            main.log.error( "Unexpected tshark output file" )
